---
## Ficha Técnica do Sistema

### 1. Descrição Geral
Sistema de gerenciamento de saldos e históricos de contas correntes bancárias. Oferece APIs REST para consulta de saldos (disponível, bloqueado, indisponível), histórico de movimentações, limites de conta e saldos negativos. Processa solicitações assíncronas de criação de histórico de saldo via mensageria GCP Pub/Sub, realizando apuração de saldos em datas específicas e atualizando registros históricos. Integra-se com banco de dados Sybase para persistência e consulta de dados financeiros.

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **SaldoController** | Controlador REST principal - expõe endpoints de consulta de saldo, histórico, contas sem movimento, saldo bloqueado e negativo |
| **FintechPosicaoController** | Controlador REST - atualiza valor total de boleto pago na posição fintech |
| **CriaSaldoHistoricoListener** | Listener GCP Pub/Sub - consome mensagens de solicitação de criação de histórico de saldo |
| **CriaHistoricoSaldoAtualizandoContaService** | Orquestra processo de criação de histórico de saldo e atualização de conta |
| **HistoricoSaldoService** | Gerencia criação de histórico de saldo com composição de valores (bloqueios, indisponíveis, limites, movimentações) |
| **SaldoService** | Implementa regras de negócio para consultas de saldo, contas sem movimento e saldo negativo |
| **ValidaCriacaoHistoricoSaldoService** | Valida contas elegíveis para criação de histórico (datas abertura/encerramento, último lançamento) |
| **AccountLimitService** | Consulta limites de conta com filtros por modalidade ou dados completos |
| **ConsultasContasSaldoBloqueadoService** | Consulta saldo bloqueado e mapeia status de bloqueio por tipo/tempo |
| **ContaRepositoryAsyncImpl** | Atualiza conta de forma assíncrona usando JdbiExecutor |
| **HistoricoSaldoRepositoryImpl** | Persiste histórico de saldo em batch ou individual, consulta último histórico antes da data de apuração |
| **SaldoRepositoryImpl** | Consulta saldos, contas sem movimento, saldo negativo e account balance |
| **AccountLimitRepositoryImpl** | Consulta limites com UNION entre tabelas correntes e históricas |

### 3. Tecnologias Utilizadas

- **Framework:** Spring Boot 2.x
- **Segurança:** Spring Security OAuth2 (Resource Server), JWT
- **Persistência:** JDBI 3.x (SQL Object Plugin)
- **Banco de Dados:** Sybase ASE (jConnect driver)
- **Mensageria:** Google Cloud Pub/Sub (Spring Cloud GCP)
- **Documentação API:** Springfox Swagger 2
- **Processamento Assíncrono:** JdbiExecutor (ThreadPoolExecutor com 10 threads)
- **Testes:** JUnit, Mockito, H2 (modo MSSQLServer para testes de integração)
- **Build:** Maven (multi-módulo: common, domain, application)
- **Logs:** Logback (formato JSON)
- **Containerização:** Docker Compose (RabbitMQ para testes)

### 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/saldo-bancario` | SaldoController | Consulta saldo de uma conta específica |
| GET | `/v1/historico-conta` | SaldoController | Retorna histórico de movimentações de uma conta |
| GET | `/v1/consulta-contas-sem-saldo-movimento` | SaldoController | Lista contas com saldo zero e sem movimentação nos últimos 180 dias |
| GET | `/v1/consulta-saldo-bloqueado` | SaldoController | Consulta saldo bloqueado de uma conta |
| POST | `/v1/consultar-saldo-bancario` | SaldoController | Consulta saldo de múltiplas contas simultaneamente |
| GET | `/v1/saldo-bancario/negativo` | SaldoController | Lista contas com saldo disponível negativo |
| GET | `/v1/digital-bank/{bank}/balances` | SaldoController | Consulta saldo por banco e data de referência |
| GET | `/v1/digital-bank/{bank}/limits` | SaldoController | Consulta limites de conta por banco |
| PUT | `/fintechPosicao/{codigoPosicaoFintech}` | FintechPosicaoController | Atualiza valor total de boleto pago na posição fintech |

### 5. Principais Regras de Negócio

1. **Cálculo de Saldo Disponível:** VrSaldoDisponivel = VrSaldoTotal - (VrSaldoBloqueio + VrSaldoIndisponivel)

2. **Criação de Histórico de Saldo:**
   - Valida que conta não está encerrada
   - Data de abertura deve ser menor ou igual à data de apuração
   - Deve existir data de último lançamento OU existir saldo bloqueado/indisponível/limite
   - Não permite duplicação de histórico para mesma data de apuração

3. **Atualização de Conta:**
   - Recalcula VrLimiteContaCorrente (soma de todos os limites vigentes)
   - Recalcula VrSaldoBloqueado (soma de bloqueios ativos sem desbloqueio ou com data desbloqueio > data apuração)
   - Recalcula VrSaldoIndisponivel (soma de valores indisponíveis vigentes)
   - Define VrSaldoInicioDia = VrSaldoTotal

4. **Saldo Bloqueado:**
   - Considera apenas motivos de bloqueio: 20, 21, 22, 23, 30
   - Bloqueio ativo: CdMotivoDesbloqueio NULL ou DtAlteracao > data apuração
   - Agências padrão: 2020, 0001
   - Bancos padrão: 436, 161

5. **Contas Sem Saldo/Movimento:**
   - VrSaldoTotal = 0
   - DtEncerramentoConta NULL (conta ativa)
   - DtUltimoLancamento nos últimos 180 dias

6. **Saldo Negativo:**
   - VrSaldoDisponivel < 0
   - Filtro opcional por modalidades de conta

7. **Limites de Conta:**
   - Consulta UNION entre TbLimiteContaCorrente e TbHistoricoLimiteContaCorrente
   - Vigência: DtInicioVigencia <= referenceDate <= DtFimVigencia
   - isActive = (DtFimVigencia > referenceDate)

8. **Cálculo de Movimentações:**
   - Soma débitos e créditos do dia (TpDebitoCredito 'C' ou 'D')
   - Considera TbHistoricoMovimento + TbMovimentoDia

### 6. Relação entre Entidades

**Entidades Principais:**

- **Conta:** Entidade central representando conta corrente (banco, agência, número, tipo, modalidade)
  - Relaciona-se com **Saldo** (1:1) - saldo atual da conta
  - Relaciona-se com **HistoricoSaldo** (1:N) - histórico de saldos por data de apuração
  - Relaciona-se com **SaldoBloqueado** (1:N) - bloqueios ativos
  - Relaciona-se com **SaldoIndisponivel** (1:N) - valores indisponíveis
  - Relaciona-se com **LimiteConta** (1:N) - limites vigentes
  - Relaciona-se com **Modalidade** (N:1) - tipo de modalidade da conta

- **HistoricoSaldo:** Snapshot de saldo em data específica
  - Contém valores: saldo total, bloqueado, indisponível, limite, movimentações

- **SaldoBloqueado:** Valores bloqueados na conta
  - Relaciona-se com **MotivoBloqueio** (N:1) - motivo do bloqueio

- **LimiteConta:** Limites de crédito da conta
  - Possui vigência (data início/fim)

- **PosicaoFintech:** Posição de boletos pagos em fintech
  - Atualizada via endpoint PUT

**Relacionamentos:**
- Conta 1:1 Saldo (atual)
- Conta 1:N HistoricoSaldo (temporal)
- Conta 1:N SaldoBloqueado
- Conta 1:N SaldoIndisponivel
- Conta 1:N LimiteConta
- Conta N:1 Modalidade
- SaldoBloqueado N:1 MotivoBloqueio

### 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbConta | Tabela | SELECT | Dados cadastrais de contas correntes |
| TbLimiteContaCorrente | Tabela | SELECT | Limites vigentes de contas |
| TbHistoricoLimiteContaCorrente | Tabela | SELECT | Histórico de limites de contas |
| TbSaldoBloqueado | Tabela | SELECT | Saldos bloqueados ativos |
| TbHistoricoSaldoBloqueado | Tabela | SELECT | Histórico de saldos bloqueados |
| TbSaldoIndisponivel | Tabela | SELECT | Saldos indisponíveis ativos |
| TbHistoricoSaldoIndisponivel | Tabela | SELECT | Histórico de saldos indisponíveis |
| TbHistoricoMovimento | Tabela | SELECT | Histórico de movimentações |
| TbMovimentoDia | Tabela | SELECT | Movimentações do dia corrente |
| TbHistoricoSaldo | Tabela | SELECT | Histórico de saldos apurados |
| TbModalidadeConta | Tabela | SELECT | Modalidades de contas |
| TbMotivoBloqueio | Tabela | SELECT | Motivos de bloqueio de saldo |
| VwContaCorrenteSaldoDia | View | SELECT | View de contas com saldo do dia |
| TbPosicaoContaFintech | Tabela | SELECT | Posição de boletos pagos em fintech |

### 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbConta | Tabela | UPDATE | Atualiza VrLimiteContaCorrente, VrSaldoBloqueio, VrSaldoIndisponivel, VrSaldoInicioDia, DtAlteracao |
| TbHistoricoSaldo | Tabela | INSERT | Insere registros de histórico de saldo (batch ou individual) |
| TbPosicaoContaFintech | Tabela | UPDATE | Incrementa VrTotalBoletoPago |

### 9. Arquivos Lidos e Gravados

não se aplica

### 10. Filas Lidas

| Nome da Fila | Tecnologia | Subscription | Payload | Descrição |
|--------------|-----------|--------------|---------|-----------|
| criacaoSaldoHistorico | GCP Pub/Sub | spring.cloud.gcp.pubsub.subscriptions.criacaoSaldoHistorico | SolicitacaoCriacaoHistoricoSaldo (JSON) | Recebe solicitações de criação de histórico de saldo para processamento assíncrono |

### 11. Filas Geradas

não se aplica

### 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| OAuth2 Token Service | API REST | Autenticação JWT - api-digitaldes.bancovotorantim.com.br/auth/oauth/v2/token-jwt |
| Google Cloud Pub/Sub | Mensageria | Projeto bv-ccbd-des - consumo de mensagens de criação de histórico de saldo |
| Sybase ASE | Banco de Dados | SYBDESBCO.bvnet.bv:17500/DBCONTACORRENTE - persistência de dados de contas e saldos |

### 13. Avaliação da Qualidade do Código

**Nota:** 8/10

**Justificativa:**

**Pontos Positivos:**
- Excelente separação de camadas (controller, service, repository, domain) seguindo princípios SOLID
- Uso adequado de JDBI para acesso a dados, evitando ORM pesado
- Processamento assíncrono bem implementado com JdbiExecutor e CompletableFuture
- Exception handlers centralizados com @ControllerAdvice
- Validadores dedicados para parâmetros de entrada
- Pattern Strategy aplicado para resolução de consultas de limite
- Testes unitários abrangentes com boa cobertura
- Uso de enums para códigos e mensagens de erro padronizadas
- Configuração externalizada por profiles (des/uat/prd)
- Documentação API com Swagger

**Pontos de Atenção:**
- Queries SQL embutidas em código Java (idealmente deveriam estar em arquivos .sql separados para melhor manutenibilidade)
- Uso de `readpast` e `AT ISOLATION 0` em queries Sybase (otimização de performance, mas pode causar leituras inconsistentes)
- Conversão `BigDecimal.abs()` em ConversorSaldo pode mascarar valores negativos importantes
- Controle de concorrência via `CompletableFuture[]` em batch pode ser complexo de debugar
- Falta de circuit breaker para integrações externas (OAuth2, Pub/Sub)
- Ausência de métricas e observabilidade explícitas (APM, traces distribuídos)

### 14. Observações Relevantes

1. **Isolamento de Leitura Sybase:** O sistema utiliza `AT ISOLATION 0` e `readpast` em queries para otimizar performance em ambiente de alta concorrência, mas isso pode resultar em leituras sujas (dirty reads).

2. **Processamento Assíncrono:** A criação de histórico de saldo é processada de forma assíncrona via Pub/Sub com ACK manual, garantindo reprocessamento em caso de falha.

3. **Histórico Temporal:** O sistema mantém união entre tabelas correntes e históricas (ex: TbLimiteContaCorrente + TbHistoricoLimiteContaCorrente) para consultas temporais, permitindo análise de saldos em datas passadas.

4. **Batch Processing:** Atualização de contas e criação de histórico de saldo suportam processamento em lote para melhor performance.

5. **Profiles de Ambiente:** Configurações específicas para ambientes des/uat/prd gerenciadas via ConfigMaps Kubernetes (infra.yml).

6. **Testes de Integração:** Utiliza H2 em modo MSSQLServer para simular Sybase em testes, com profile específico `teste-de-integracao`.

7. **Segurança:** Todos os endpoints REST protegidos por OAuth2 com JWT, exigindo token válido para acesso.

8. **Logs Estruturados:** Formato JSON para logs facilita integração com ferramentas de observabilidade (ELK, Splunk, etc).

9. **Multi-módulo Maven:** Arquitetura modular (common, domain, application) facilita reuso de código e separação de responsabilidades.

10. **Regra de Negócio Crítica:** O cálculo de saldo disponível considera bloqueios e indisponíveis, sendo fundamental para operações bancárias e limite de crédito.

---