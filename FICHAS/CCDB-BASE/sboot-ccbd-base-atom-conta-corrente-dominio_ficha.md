---
## Ficha Técnica do Sistema

### 1. Descrição Geral
O **sboot-ccbd-base-atom-conta-corrente-dominio** é um microserviço atômico Spring Boot responsável pela gestão do domínio de contas correntes corporativas do Banco Votorantim. O sistema implementa operações CRUD e regras de negócio para manutenção de cadastros, parâmetros, transações, bloqueios/desbloqueios, encerramentos e monitoramento de contas. Atua como serviço central para operações de domínio, integrando-se com múltiplas bases de dados (Sybase e MySQL) e utilizando mensageria assíncrona (Google Cloud Pub/Sub) para fluxos de encerramento e monitoramento de transações.

---

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ContaCorrenteDominioController** | Controller REST principal, expõe 40+ endpoints para operações de domínio |
| **EncerramentoContaService** | Gerencia fluxo de encerramento de contas, validações e publicação de mensagens |
| **MigracaoContaService** | Executa migração de contas entre bancos (655→413, 161→436), validando saldo zero |
| **BalanceamentoContasService** | Gerencia operações batch de inserção/atualização de contas balanceadas |
| **ModalidadeContaService** | CRUD de modalidades de conta com validação de categoria |
| **CategoriaService** | CRUD de categorias com validação de tipo conta |
| **TipoTransacaoService** | CRUD de tipos de transação com validação de operação lançamento |
| **ParametroMt940Service** | Gerencia parâmetros de extrato MT940 (batch save) |
| **GradeHorariaTransacaoService** | Consulta grades horárias (TED, natal, ano novo) |
| **ContaEncerradaListener** | Listener Pub/Sub para processar conclusão de encerramentos |
| **TransacoesEfetivadasCreditoListener** | Listener Pub/Sub para monitorar créditos de resgate CDB (códigos 520/498) |
| **EncerramentoContaPublisher** | Publica mensagens de solicitação de encerramento no Pub/Sub |
| **PubSubPublisherService** | Classe abstrata base para publishers com propagação de MDC |
| **MdcSettingChannelInterceptor** | Interceptor Spring Integration para propagar ticket MDC em mensagens |
| **Repositories (18+ classes JDBI)** | Camada de acesso a dados usando JDBI3 com SQL externalizado |
| **Converters/Mappers (15+ classes)** | Conversão entre domain e representation (MapStruct e manual) |
| **ResourceExceptionHandler** | Exception handler global com tratamento de 15+ tipos de exceções customizadas |

---

### 3. Tecnologias Utilizadas

- **Framework:** Spring Boot 2.x, Spring Security (OAuth2/JWT), Spring Retry, Spring Integration, Spring Cloud GCP
- **Linguagem:** Java 11
- **Persistência:** JDBI3 (SQL externalizado), HikariCP (pool de conexões)
- **Bancos de Dados:** Sybase (DBCONTACORRENTE, DBGLOBAL), MySQL/CloudSQL (CCBDContaCorrente)
- **Mensageria:** Google Cloud Pub/Sub
- **Mapeamento:** MapStruct, Lombok
- **Documentação:** Swagger/OpenAPI (Springfox)
- **Observabilidade:** Spring Actuator, Prometheus, Grafana, Logback (JSON estruturado), SLF4J MDC
- **Testes:** JUnit 5, Mockito, H2 (in-memory), ArchUnit, Pact (contract tests)
- **Serialização:** Apache Avro (schemas de mensagens)
- **Segurança:** OpenID Connect, LDAP
- **Infraestrutura:** Google Kubernetes Engine (GKE), Docker
- **Outros:** ExponentialBackOffPolicy (retry), Cursor-based pagination

---

### 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/manutencao-tabela/balanceamento-contas` | ContaCorrenteDominioController | Listar contas balanceadas |
| POST | `/v1/manutencao-tabela/balanceamento-contas` | ContaCorrenteDominioController | Inserir contas balanceadas (batch) |
| PUT | `/v1/manutencao-tabela/balanceamento-contas` | ContaCorrenteDominioController | Atualizar contas balanceadas |
| GET | `/v1/manutencao-tabela/balanceamento-contas/{id}` | ContaCorrenteDominioController | Consultar conta balanceada por ID |
| GET | `/v1/manutencao-tabela/balanceamento-contas/banco/{cdBanco}` | ContaCorrenteDominioController | Consultar contas balanceadas por banco |
| GET | `/v1/manutencao-tabela/categoria` | ContaCorrenteDominioController | Listar categorias |
| POST | `/v1/manutencao-tabela/categoria` | ContaCorrenteDominioController | Inserir categoria |
| PUT | `/v1/manutencao-tabela/categoria` | ContaCorrenteDominioController | Atualizar categoria |
| GET | `/v1/manutencao-tabela/zeragem-saldo` | ContaCorrenteDominioController | Listar contas BV Financeira (zeragem saldo) |
| POST | `/v1/manutencao-tabela/zeragem-saldo` | ContaCorrenteDominioController | Inserir conta BV Financeira |
| PUT | `/v1/manutencao-tabela/zeragem-saldo` | ContaCorrenteDominioController | Atualizar conta BV Financeira |
| GET | `/v1/conta-corrente-info` | ContaCorrenteDominioController | Busca paginada de contas (cursor-based) |
| GET | `/v1/manutencao-tabela/control/date` | ContaCorrenteDominioController | Consultar datas de controle por banco/agência |
| POST | `/v1/intencao-encerramento` | ContaCorrenteDominioController | Registrar intenção de encerramento |
| GET | `/v1/grade` | ContaCorrenteDominioController | Consultar grade horária de transação (TED) |
| PUT | `/v1/migracao/contacorrente` | ContaCorrenteDominioController | Migrar conta corrente entre bancos |
| GET | `/v1/manutencao-tabela/modalidade-conta` | ContaCorrenteDominioController | Listar modalidades |
| POST | `/v1/manutencao-tabela/modalidade-conta` | ContaCorrenteDominioController | Inserir modalidade |
| PUT | `/v1/manutencao-tabela/modalidade-conta` | ContaCorrenteDominioController | Atualizar modalidade |
| GET | `/v1/manutencao-tabela/saldo-negativo` | ContaCorrenteDominioController | Listar contas monitoradas (saldo credor) |
| POST | `/v1/manutencao-tabela/saldo-negativo` | ContaCorrenteDominioController | Associar conta para monitoramento |
| GET | `/v1/manutencao-tabela/motivo-bloqueio` | ContaCorrenteDominioController | Listar motivos de bloqueio |
| POST | `/v1/manutencao-tabela/motivo-bloqueio` | ContaCorrenteDominioController | Inserir motivo de bloqueio |
| PUT | `/v1/manutencao-tabela/motivo-bloqueio` | ContaCorrenteDominioController | Atualizar motivo de bloqueio |
| PUT | `/v1/manutencao-tabela/motivo-bloqueio/ordenacao` | ContaCorrenteDominioController | Atualizar ordem de prioridade |
| GET | `/v1/manutencao-tabela/motivo-desbloqueio` | ContaCorrenteDominioController | Listar motivos de desbloqueio |
| POST | `/v1/manutencao-tabela/motivo-desbloqueio` | ContaCorrenteDominioController | Inserir motivo de desbloqueio |
| PUT | `/v1/manutencao-tabela/motivo-desbloqueio` | ContaCorrenteDominioController | Atualizar motivo de desbloqueio |
| DELETE | `/v1/manutencao-tabela/motivo-desbloqueio/{id}` | ContaCorrenteDominioController | Inativar motivo de desbloqueio |
| GET | `/v1/manutencao-tabela/motivo-encerramento` | ContaCorrenteDominioController | Listar motivos de encerramento |
| POST | `/v1/manutencao-tabela/motivo-encerramento` | ContaCorrenteDominioController | Inserir motivo de encerramento |
| PUT | `/v1/manutencao-tabela/motivo-encerramento` | ContaCorrenteDominioController | Atualizar motivo de encerramento |
| GET | `/v1/manutencao-tabela/parametro-mt940` | ContaCorrenteDominioController | Buscar parâmetros extrato MT940 |
| POST | `/v1/manutencao-tabela/parametro-mt940` | ContaCorrenteDominioController | Salvar configurações MT940 (batch) |
| GET | `/v1/manutencao-tabela/parametro-movimento-contabil` | ContaCorrenteDominioController | Consultar parâmetros movimento contábil |
| POST | `/v1/manutencao-tabela/parametro-movimento-contabil` | ContaCorrenteDominioController | Cadastrar parâmetro movimento contábil |
| PUT | `/v1/manutencao-tabela/parametro-movimento-contabil` | ContaCorrenteDominioController | Alterar parâmetro movimento contábil |
| GET | `/v1/manutencao-tabela/tipo-conta-contabil` | ContaCorrenteDominioController | Consultar tipos de conta contábil |
| POST | `/v1/manutencao-tabela/tipo-conta-contabil` | ContaCorrenteDominioController | Cadastrar tipo de conta contábil |
| PUT | `/v1/manutencao-tabela/tipo-conta-contabil` | ContaCorrenteDominioController | Alterar tipo de conta contábil |
| GET | `/v1/manutencao-tabela/tipo-transacao` | ContaCorrenteDominioController | Buscar tipos de transação (filtros múltiplos) |
| POST | `/v1/manutencao-tabela/tipo-transacao` | ContaCorrenteDominioController | Inserir tipo de transação |
| PUT | `/v1/manutencao-tabela/tipo-transacao` | ContaCorrenteDominioController | Atualizar tipo de transação |
| GET | `/v1/transacoes-monitoraveis` | ContaCorrenteDominioController | Listar transações monitoradas |

---

### 5. Principais Regras de Negócio

#### Balanceamento de Contas
- Autoincremento de `cdCadastroBalanceamentoConta` para novos registros
- Atualização de registro existente ou inserção caso não exista

#### Zeragem de Saldo (Conta BV Financeira)
- **RN01:** Apenas uma conta principal permitida (`flagContaCorrentePrincipal='S'`)
- **RN02:** Conta não pode estar duplicada no cadastro
- **RN03:** Conta deve existir na base global
- **RN04:** Situação cadastral deve ser ATIVA (`cdSituacaoCadastral=2`)
- **RN05:** Tipo pessoa deve ser Pessoa Jurídica (PJ)

#### Migração de Conta
- **RN:** Saldo total (`saldoTotal - saldoIndisponivel - saldoBloqueado`) deve ser ZERO
- Etapas sequenciais: migração de relacionamento global → conta corrente global → conta corrente CCBD → atualização situação cadastral → atualização origens/destinos de agendamento (436↔161, 413↔655)

#### Motivo Bloqueio
- **RN:** Se `monitorado='S'`, gerar ordem de prioridade sequencial
- **RN:** Se `monitorado='N'` em atualização, remover ordem e reordenar lista completa

#### Categoria
- **RN:** `tipoConta` não pode ser 0 (zero)

#### Tipo Transação
- **RN:** `operacaoLancto` deve ser igual a `operacao` (caso contrário, lança `OperacaoLancamentoDiferenteException`)

#### Motivo Encerramento
- **RN:** `origem` deve ser 'B' (Banco) ou 'C' (Cliente)
- **RN:** `situacao` deve ser 'S' (Sim) ou 'N' (Não)

#### Modalidade Conta
- **RN:** `cdCategoria` deve existir na tabela de categorias

#### Parâmetro Movimento Contábil
- **RN:** `cdModalidadeConta` deve existir
- **RN:** `cdTipoContaContabil` deve existir
- **RN:** Não permitir duplicidade (combinação modalidade + tipo conta contábil + banco)

#### Intenção de Encerramento
- **RN:** Se conta não possui intenção registrada, inserir; se já existe, não reprocessar
- **RN:** Validação de crédito para encerramento: ao detectar transação de resgate CDB (códigos 520/498 parametrizáveis), publicar mensagem para conclusão do fluxo

#### Grade Horária Transação
- **RN:** Consultar grades de início, fim, natal e ano novo
- **RN:** Se data for natal (24/12 00:01-23:59) ou ano novo (31/12 00:01-23:59), usar grade especial (`codigoNatalAnoNovoFim`)

#### Listeners Pub/Sub
- **RN:** Retry automático com backoff exponencial (5 tentativas) para falhas recuperáveis (`FalhaRecuperavelFluxoException`)
- **RN:** Propagação de `ticket` MDC para correlação de logs em mensagens assíncronas

---

### 6. Relação entre Entidades

```
ModalidadeConta (n) ──> (1) Categoria
Categoria (n) ──> (1) TipoConta
TipoTransacao (n) ──> (1) CategoriaLancamento
ParametroMovimentoContabil (n) ──> (1) TipoContaContabil
ParametroMovimentoContabil (n) ──> (1) ModalidadeConta
IntencaoEncerramento (n) ──> (1) ContaCorrente
IntencaoEncerramento (n) ──> (1) MotivoEncerramento
ContaCorrenteBVFinanceira (n) ──> (1) ContaCorrente (base global)
BalanceamentoConta (n) ──> (1) Banco
MonitoracaoConta (n) ──> (1) ContaCorrente
MotivoBloqueio (1) ──> (1) OrdemPrioridade (se monitorado='S')
```

**Descrição textual:**
- Uma **ModalidadeConta** pertence a uma **Categoria**
- Uma **Categoria** pertence a um **TipoConta**
- Um **TipoTransacao** pertence a uma **CategoriaLancamento**
- Um **ParametroMovimentoContabil** referencia um **TipoContaContabil** e uma **ModalidadeConta**
- Uma **IntencaoEncerramento** referencia uma **ContaCorrente** e um **MotivoEncerramento**
- Uma **ContaCorrenteBVFinanceira** referencia uma **ContaCorrente** da base global
- Um **BalanceamentoConta** está associado a um **Banco**
- Uma **MonitoracaoConta** referencia uma **ContaCorrente**
- Um **MotivoBloqueio** possui **OrdemPrioridade** quando monitorado

---

### 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TB_BALANCEAMENTO_CONTAS | Tabela (Sybase DBCONTACORRENTE) | SELECT | Consulta contas balanceadas por ID, banco ou listagem completa |
| TB_CATEGORIA | Tabela (Sybase DBCONTACORRENTE) | SELECT | Consulta categorias de conta por ID ou listagem |
| TB_MOTIVO_BLOQUEIO | Tabela (Sybase DBCONTACORRENTE) | SELECT | Consulta motivos de bloqueio, incluindo monitorados e ordem prioridade |
| TB_MOTIVO_DESBLOQUEIO | Tabela (Sybase DBCONTACORRENTE) | SELECT | Consulta motivos de desbloqueio ativos |
| TB_MOTIVO_ENCERRAMENTO | Tabela (Sybase DBCONTACORRENTE) | SELECT | Consulta motivos de encerramento por origem e situação |
| TB_MODALIDADE_CONTA | Tabela (Sybase DBCONTACORRENTE) | SELECT | Consulta modalidades de conta por ID ou listagem |
| TB_MONITORACAO_CONTA | Tabela (Sybase DBCONTACORRENTE) | SELECT | Consulta contas monitoradas para saldo credor |
| TB_CONTROL_DATE | Tabela (Sybase DBCONTACORRENTE) | SELECT | Consulta datas de controle por banco e agência |
| TB_TIPO_TRANSACAO | Tabela (Sybase DBCONTACORRENTE) | SELECT | Consulta tipos de transação com filtros múltiplos |
| TB_CATEGORIA_LANCAMENTO | Tabela (Sybase DBCONTACORRENTE) | SELECT | Consulta categorias de lançamento |
| TB_PARAMETRO_GERAL_SISTEMA | Tabela (Sybase DBCONTACORRENTE) | SELECT | Consulta parâmetros gerais do sistema |
| TB_TRANSACOES_MONITORAVEIS | Tabela (Sybase DBCONTACORRENTE) | SELECT | Consulta transações configuradas para monitoramento |
| TB_GRADE_HORARIA_TRANSACAO | Tabela (Sybase DBCONTACORRENTE) | SELECT | Consulta grades horárias (TED, natal, ano novo) |
| TB_CONTA_CORRENTE | Tabela (Sybase DBGLOBAL) | SELECT | Consulta dados de conta corrente para migração e validações |
| TB_RELACAO_CONTA | Tabela (Sybase DBGLOBAL) | SELECT | Consulta relacionamentos de conta para migração |
| TB_SALDO_CONTA_CORRENTE | Tabela (Sybase DBGLOBAL) | SELECT | Validação de saldo zero para migração |
| TB_DADOS_CADASTRAIS | Tabela (Sybase DBGLOBAL) | SELECT | Validação de situação cadastral e tipo pessoa (zeragem saldo) |
| TB_AGENDAMENTO | Tabela (Sybase DBGLOBAL) | SELECT | Consulta agendamentos para atualização origem/destino na migração |
| TB_CONTA_CORRENTE_BV_FINANCEIRA | Tabela (MySQL CCBDContaCorrente) | SELECT | Consulta contas BV Financeira para zeragem de saldo |
| TB_PARAMETRO_MT940 | Tabela (MySQL CCBDContaCorrente) | SELECT | Consulta parâmetros de extrato MT940 |
| TB_TIPO_CONTA_CONTABIL | Tabela (MySQL CCBDContaCorrente) | SELECT | Consulta tipos de conta contábil |
| TB_PARAMETRO_MOVIMENTO_CONTABIL | Tabela (MySQL CCBDContaCorrente) | SELECT | Consulta parâmetros de movimento contábil |
| TB_INTENCAO_ENCERRAMENTO | Tabela (MySQL CCBDContaCorrente) | SELECT | Consulta intenções de encerramento existentes |

---

### 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TB_BALANCEAMENTO_CONTAS | Tabela (Sybase DBCONTACORRENTE) | INSERT/UPDATE | Inserção batch ou atualização de contas balanceadas |
| TB_CATEGORIA | Tabela (Sybase DBCONTACORRENTE) | INSERT/UPDATE | Inserção e atualização de categorias |
| TB_MOTIVO_BLOQUEIO | Tabela (Sybase DBCONTACORRENTE) | INSERT/UPDATE | Inserção e atualização de motivos de bloqueio, incluindo ordem prioridade |
| TB_MOTIVO_DESBLOQUEIO | Tabela (Sybase DBCONTACORRENTE) | INSERT/UPDATE/DELETE | CRUD completo de motivos de desbloqueio |
| TB_MOTIVO_ENCERRAMENTO | Tabela (Sybase DBCONTACORRENTE) | INSERT/UPDATE | Inserção e atualização de motivos de encerramento |
| TB_MODALIDADE_CONTA | Tabela (Sybase DBCONTACORRENTE) | INSERT/UPDATE | Inserção e atualização de modalidades de conta |
| TB_MONITORACAO_CONTA | Tabela (Sybase DBCONTACORRENTE) | INSERT/DELETE | Associação e remoção de contas monitoradas (saldo credor) |
| TB_TIPO_TRANSACAO | Tabela (Sybase DBCONTACORRENTE) | INSERT/UPDATE | Inserção e atualização de tipos de transação |
| TB_PARAMETRO_GERAL_SISTEMA | Tabela (Sybase DBCONTACORRENTE) | UPDATE | Atualização de parâmetros gerais do sistema |
| TB_CONTA_CORRENTE | Tabela (Sybase DBGLOBAL) | UPDATE | Atualização de banco/agência na migração de conta |
| TB_RELACAO_CONTA | Tabela (Sybase DBGLOBAL) | UPDATE | Atualização de banco/agência nos relacionamentos na migração |
| TB_AGENDAMENTO | Tabela (Sybase DBGLOBAL) | UPDATE | Atualização de origem/destino (436↔161, 413↔655) na migração |
| TB_CONTA_CORRENTE_BV_FINANCEIRA | Tabela (MySQL CCBDContaCorrente) | INSERT/UPDATE | Inserção e atualização de contas BV Financeira (zeragem saldo) |
| TB_PARAMETRO_MT940 | Tabela (MySQL CCBDContaCorrente) | INSERT/UPDATE | Salvamento batch de parâmetros MT940 |
| TB_TIPO_CONTA_CONTABIL | Tabela (MySQL CCBDContaCorrente) | INSERT/UPDATE | Cadastro e alteração de tipos de conta contábil |
| TB_PARAMETRO_MOVIMENTO_CONTABIL | Tabela (MySQL CCBDContaCorrente) | INSERT/UPDATE | Cadastro e alteração de parâmetros de movimento contábil |
| TB_INTENCAO_ENCERRAMENTO | Tabela (MySQL CCBDContaCorrente) | INSERT/UPDATE | Registro de intenções de encerramento |

---

### 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | Spring Boot (bootstrap) | Configurações por ambiente (des/uat/prd): datasources, Pub/Sub, retry, pools, probes |
| application-local.yml | Leitura | Spring Boot (profile local) | Configurações para ambiente local (H2, mocks) |
| logback-spring.xml | Leitura | Logback | Configuração de logs JSON estruturado com MDC (correlationId) |
| *.sql (50+ arquivos) | Leitura | JDBI3 (@UseClasspathSqlLocator) | Queries SQL externalizadas em resources para repositories |
| *.avsc (3 schemas Avro) | Leitura | Apache Avro | Schemas de serialização de mensagens Pub/Sub (GcpPubSubProperty, MensagemFila, TransacaoEfetivada) |
| swagger.yaml | Leitura | Springfox | Contrato OpenAPI 2.0 da API REST |
| Dockerfile | Leitura | Docker build | Definição de imagem Docker otimizada (Java 11, multi-stage) |
| pom.xml | Leitura | Maven | Dependências e plugins do projeto |

**Observação:** Não há geração de arquivos de saída (relatórios, exportações) identificada no código analisado. Logs são enviados para stdout/stderr em formato JSON.

---

### 10. Filas Lidas

| Nome da Fila | Tecnologia | Classe Responsável | Breve Descrição |
|--------------|-----------|-------------------|-----------------|
| business-ccbd-base-transacoes-efetivadas-monitora-resgate-cdb-sub | Google Cloud Pub/Sub (Subscription) | TransacoesEfetivadasCreditoListener | Monitora transações de crédito efetivadas para detectar resgates de CDB (códigos 520/498 parametrizáveis). Ao detectar crédito em conta com intenção de encerramento, publica mensagem para conclusão do fluxo. Retry com backoff exponencial (5 tentativas). |
| business-ccbd-base-encerramento-conta-monitora-encerramento-sub | Google Cloud Pub/Sub (Subscription) | ContaEncerradaListener | Monitora conclusão de encerramentos de conta. Atualiza registro de intenção de encerramento após confirmação. Ack manual de mensagens. |

---

### 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Responsável | Breve Descrição |
|--------------|-----------|-------------------|-----------------|
| business-ccbd-base-solicitar-encerramento-conta | Google Cloud Pub/Sub (Topic) | EncerramentoContaPublisher | Publica mensagens de solicitação de encerramento de conta para processamento assíncrono. Propaga ticket MDC para correlação de logs. Callbacks assíncronos com logging de sucesso/falha. |

---

### 12. Integrações Externas

| Sistema/Serviço | Tipo | Breve Descrição |
|-----------------|------|-----------------|
| Google Cloud Pub/Sub | Mensageria | Integração assíncrona para fluxos de encerramento de conta e monitoramento de transações. Topics e subscriptions configurados por ambiente (des/uat/prd). |
| OAuth2/JWT (OpenID Connect) | Autenticação | Autenticação via JWT com endpoints por ambiente: des (api-digitaldes.bancobv.com.br), uat (api-digitaluat.bancovotorantim.com.br), prd (api-digital.bancovotorantim.com.br). |
| LDAP (global-ldap-bvnet) | Autenticação | Autenticação corporativa via LDAP para usuários internos. |
| Sybase DBCONTACORRENTE | Banco de Dados | Base principal de conta corrente. Conexões por ambiente: des (SYBDESBCO:17500), uat (SYBUATBCO:14400), prd (sybbcossl_3050:3050). |
| Sybase DBGLOBAL | Banco de Dados | Base global corporativa. Conexões por ambiente: des (SYBDESBCO:7500), uat (MORUATBCO:4400), prd (MORSYBBCO:3000). |
| MySQL CloudSQL (CCBDContaCorrente) | Banco de Dados | Base MySQL em Google Cloud. Acesso via CloudSQL Proxy: des/uat/prd (gcmysdgXXX04-proxy.bvnet.bv:3306). |
| Prometheus/Grafana | Observabilidade | Métricas expostas via Spring Actuator para monitoramento em Prometheus e visualização em Grafana. |
| Swagger UI | Documentação | Interface de documentação da API REST (desabilitada em ambientes não-dev). |

---

### 13. Avaliação da Qualidade do Código

**Nota:** 8/10

**Justificativa:**

**Pontos Positivos:**
- **Arquitetura bem estruturada:** Implementação de arquitetura hexagonal (Ports & Adapters) com clara separação de responsabilidades entre camadas (domain, application, infrastructure)
- **Boas práticas de Spring:** Uso adequado de anotações, injeção de dependências, transações, retry patterns e exception handling centralizado
- **Externalização de configurações:** Configurações por ambiente bem organizadas em application.yml
- **Observabilidade:** Logging estruturado em JSON com MDC para correlação, métricas Prometheus, health checks
- **Resiliência:** Implementação de retry com backoff exponencial para falhas recuperáveis
- **Testes abrangentes:** Cobertura de testes unitários, integração, funcionais e contract tests (Pact)
- **Validação de arquitetura:** Uso de ArchUnit para garantir conformidade com padrões arquiteturais
- **Redução de boilerplate:** Uso efetivo de Lombok e MapStruct
- **SQL externalizado:** Queries SQL em arquivos .sql separados facilitam manutenção

**Pontos de Atenção:**
- **Controller com múltiplas responsabilidades:** ContaCorrenteDominioController expõe 40+ endpoints, violando princípio de responsabilidade única. Recomenda-se divisão em controllers especializados por domínio
- **Acoplamento alto:** Controller injeta 20+ services/bridges, indicando possível violação de coesão
- **SQL nativo:** Uso extensivo de SQL nativo (Sybase/MySQL) dificulta portabilidade e pode complicar manutenção
- **Testes com assertions comentadas:** Alguns testes possuem assertions comentadas, reduzindo efetividade
- **Documentação inline limitada:** Falta de JavaDoc em algumas classes críticas
- **Tratamento de exceções genérico:** Alguns catches tratam Exception de forma ampla

**Recomendações:**
1. Refatorar controller em múltiplos controllers especializados (ex: BalanceamentoController, CategoriaController, EncerramentoController)
2. Considerar uso de JPA/Hibernate para reduzir SQL nativo
3. Adicionar JavaDoc em classes de serviço e regras de negócio complexas
4. Revisar e ativar assertions comentadas em testes
5. Implementar circuit breaker para integrações externas (Pub/Sub, bancos)

---

### 14. Observações Relevantes

1. **Multidatabase:** Sistema integra 3 fontes de dados distintas (2 Sybase + 1 MySQL), exigindo gerenciamento cuidadoso de transações distribuídas

2. **Paginação cursor-based:** Implementação de paginação eficiente usando cursor codificado em base64 para consultas de grande volume

3. **MDC para correlação:** Propagação de `ticket` (correlationId) via MDC em logs e mensagens Pub/Sub para rastreabilidade distribuída

4. **Pub/Sub condicional:** Integração Pub/Sub habilitada via flag por ambiente (desabilitada em des, habilitada em uat/prd)

5. **Migração de contas:** Funcionalidade crítica de migração entre bancos (655→413, 161→436) com validação rigorosa de saldo zero e atualização de múltiplas tabelas relacionadas

6. **Retry configurável:** Estratégia de retry com backoff exponencial configurável via properties (maxAttempts, delay, multiplier)

7. **Grades horárias especiais:** Tratamento diferenciado para datas especiais (natal, ano novo) em grades de transação

8. **Zeragem de saldo:** Regras específicas para contas BV Financeira com validações de unicidade, situação cadastral e tipo pessoa

9. **Monitoramento de transações:** Sistema monitora códigos de transação parametrizáveis (520/498) para detectar resgates de CDB e acionar fluxo de encerramento

10. **HikariCP otimizado:** Pools de conexão configurados por ambiente (prd: max=30, des/uat: max=10) para otimização de recursos

11. **Probes Kubernetes:** Liveness probe com 420s de initial delay e readiness probe com 3s para garantir estabilidade em GKE

12. **Service Account GCP:** Uso de ksa-ccbd-base-14637 para autenticação em recursos Google Cloud

13. **Cofre de senhas:** Credenciais gerenciadas via cofre corporativo (lgettcompensacao, CCBDContaCorrente_appl)

14. **Enums de domínio:** Uso extensivo de enums para garantir type-safety (TipoContaEnum, BooleanBVEnum, OrigemMotivoEncerramentoEnum, etc)

15. **Scaffolding corporativo:** Projeto gerado a partir de template atomic (plugin 0.50.0) seguindo padrões corporativos do Banco Votorantim

16. **Segurança OAuth2:** Integração com servidor de recursos OAuth2 para autenticação e autorização de APIs

17. **Profiles Spring:** Suporte a múltiplos profiles (local, des, uat, prd) com configurações específicas por ambiente

18. **H2 para testes:** Uso de banco in-memory H2 para testes de integração, evitando dependência de bancos externos

19. **Exceções customizadas:** Hierarquia rica de exceções de negócio (15+ tipos) para tratamento granular de erros

20. **Versionamento de API:** Endpoints versionados (`/v1/`) preparando sistema para evolução de contrato

---