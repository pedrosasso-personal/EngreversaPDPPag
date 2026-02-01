# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de gestão de contas correntes bancárias multi-banco (BV e BVSA) desenvolvido em arquitetura hexagonal. Gerencia operações de crédito, débito, TEF (Transferência Eletrônica de Fundos), bloqueios, saldos, encerramento de contas e integração com sistemas Fintech. Implementa controles de teto de gasto, saldo indisponível (D+x), validações de situação cadastral e publicação de eventos via Google Cloud Pub/Sub. Suporta processamento transacional com roteamento dinâmico entre bases de dados Sybase (BVSA) e MySQL (Fintech).

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ContaCorrenteServiceImpl** | Orquestra operações principais: efetivar crédito/débito/TEF, solicitar débito, cancelar bloqueio, criar conta, validar situação, gerenciar saldo indisponível e bloqueios Renda Fixa |
| **CriticasServiceImpl** | Valida pré-condições transacionais: situação conta (ativa/encerrada), bloqueios crédito/débito (com exceções configuráveis), transação ativa, duplicidade de movimentos |
| **EfetivaTefServiceImpl** | Executa TEF completo: débito remetente + crédito favorecido, validação de valores, desbloqueio de saldo, atualização de protocolo |
| **EncerramentoServiceImpl** | Gerencia ciclo de vida do encerramento: demandar, cancelar, confirmar, bloqueio/desbloqueio, consultas analíticas (PLD/desinteresse) |
| **TransactionBankAspect** | AOP para transações multi-banco: injeta TransactionTemplate por código banco, aplica lock (SET LOCK WAIT), trata rollback configurável |
| **TransactionRouter** | Roteia Jdbi e TransactionTemplate por banco (BVSA/VTRM) baseado em código banco |
| **ContaCorrenteRepositoryImpl** | Acesso dados TbConta: CRUD, lock pessimista, atualização saldo, bloqueios, consultas ativas/inativas |
| **MovimentoRepositoryImpl** | Gestão movimentos: registro TbMovimentoDia/TbHistoricoMovimento, verificação duplicidade, consultas por documento/NSU/sistema |
| **SaldoBloqueadoRepositoryImpl** | Gerencia TbSaldoBloqueado: inserção, atualização, estorno, recuperação por motivo |
| **ProcessamentoFintechServiceImpl** | Consolida movimentos Fintech entre MySQL (fila) e Sybase (legado): verifica duplicidade, atualiza status processamento |
| **CreditoMonitoradoPublisher** | Publica eventos BloqueioMonitorado no tópico PubSub creditosMonitorados |
| **TransacaoEfetivadaPublisher** | Publica eventos Movimento no tópico PubSub transacoesEfetivadas |

---

## 3. Tecnologias Utilizadas

- **Framework**: Spring Boot 2.x, Spring Security (OAuth2 JWT)
- **Persistência**: JDBI 3 (SQL Object), Sybase ASE, MySQL 5.7+
- **Mensageria**: Google Cloud Pub/Sub
- **Documentação**: Swagger/OpenAPI 3
- **Monitoramento**: Prometheus, Grafana, Spring Boot Actuator
- **Testes**: JUnit 5, Mockito, Rest Assured, Pact (contract testing)
- **Build**: Maven 3.3+, Java 11
- **Infraestrutura**: Docker, Kubernetes (GCP), Jenkins CI/CD
- **Outros**: AspectJ (AOP), Jackson (JSON), ConfigCat (feature toggles), Logback (logs JSON)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/banco-digital/conta/status` | ContaCorrenteController | Consulta status conta corrente (aberta/fechada) |
| GET | `/v1/banco-digital/contas` | ContaCorrenteController | Consulta dados completos conta corrente |
| POST | `/v1/banco-digital/contas/credito` | ContaCorrenteController | Efetiva crédito em conta (com bloqueio RF opcional) |
| POST | `/v1/banco-digital/contas/debito/confirmar` | ContaCorrenteController | Efetiva débito previamente solicitado |
| POST | `/v1/banco-digital/contas/debito` | ContaCorrenteController | Solicita débito (bloqueia saldo, valida teto gasto) |
| POST | `/v1/banco-digital/contas/tef` | ContaCorrenteController | Efetiva TEF (débito remetente + crédito favorecido) |
| POST | `/v1/banco-digital/contas/bloqueio/cancelar` | ContaCorrenteController | Cancela bloqueio de saldo |
| POST | `/v1/banco-digital/contas/validacao` | ContaCorrenteController | Valida situação cadastral conta |
| POST | `/v1/banco-digital/contas/criarConta` | ContaCorrenteController | Cria nova conta corrente |
| GET | `/v1/banco-digital/estado/banco/{banco}/conta/{conta}` | ContaCorrenteController | Consulta estado atual conta (saldos) |
| POST | `/v1/banco-digital/consultarRelacaoConta` | ContaCorrenteController | Lista contas relacionadas a cliente |
| POST | `/v1/banco-digital/encerramento/demandar` | ContaCorrenteController | Demanda encerramento conta (cliente/banco) |
| POST | `/v1/banco-digital/encerramento/confirmarDemanda` | ContaCorrenteController | Confirma encerramento (valida 30 dias, saldos zerados) |
| POST | `/v1/banco-digital/encerramento/cancelarDemanda` | ContaCorrenteController | Cancela demanda encerramento |
| GET | `/v1/banco-digital/encerramento/banco/{banco}` | ContaCorrenteController | Lista encerramentos por iniciativa (cliente/banco/emergencial) |
| GET | `/v1/movimento/historico` | ContaCorrenteController | Consulta histórico movimentos por documento |
| POST | `/v1/movimento/cancelarLancamento` | ContaCorrenteController | Cancela lançamento (estorna movimento, saldo, histórico) |
| POST | `/v1/banco-digital/processo/fintech` | ContaCorrenteController | Consolida movimentos Fintech (MySQL→Sybase) |

---

## 5. Principais Regras de Negócio

1. **Validação Situação Conta**: Rejeita operações em contas inativas (CdSituacao≠2) ou encerradas (CdSituacao=8), exceto consultas.

2. **Bloqueio Crédito/Débito**: Valida bloqueios com exceções configuráveis via `BypassPorTransacaoProperties` (ex: transação 520 PLD bypass bloqueio crédito, transação 5626 MED bypass bloqueio débito).

3. **Bloqueio Renda Fixa (RF)**: Créditos com `FlBloqueioRendaFixa=true` criam/atualizam bloqueio judicial (CdMotivoBloqueio=1, CdMotivoDesbloqueio=NULL).

4. **Saldo Indisponível (D+x)**: Créditos com `qtDiasCreditoIndisponivel>0` inserem registro em TbSaldoIndisponivel com DtFimVigencia calculada, reduzindo saldo disponível temporariamente.

5. **Teto de Gasto**: Contas configuradas em `BV_TETO_GASTO_CONTAS` (hash SHA-256) permitem saldo negativo até limite configurado. Validação via `ValidaTetoGasto`.

6. **TEF (Transferência Eletrônica de Fundos)**:
   - Valida VrOperacao remetente = favorecido
   - Se remetente possui bloqueio: valida CdMotivoDesbloqueio=NULL, VrOperacao match, desbloqueia (CdMotivoDesbloqueio=9)
   - Se remetente sem bloqueio: valida saldo disponível e teto gasto
   - Atualiza protocolo se NuDocumento='0' (movimento já existe)

7. **Duplicidade Movimento**: Verifica NSU+NrDocumento+CdTransacao em TbMovimentoDia e TbHistoricoMovimento antes de registrar.

8. **StandIn**: Flag `standIn=true` bypassa validações de saldo e situação conta (modo contingência).

9. **Data Processamento**: Valida DtEfetivacao ≥ DtAtualProcCC (TbParametro) e ControleData.aceita movimentação (conta não fechada).

10. **Encerramento Conta**:
    - Demanda: valida saldos zerados (PADRAO) ou saldo bloqueado (DESINTERESSE)
    - Confirmação: valida 30 dias desde abertura (se emergencial), saldos zerados, sem bloqueios
    - BV CC (161+5): fica pendente TotalBanco (situação ENCERRAMENTO_PENDENTE_TOTALBANCO)
    - Cancelamento: valida analista≠responsável solicitação, desbloqueia por iniciativas CLIENTE/BANCO

11. **Processamento Fintech**: Consolida movimentos MySQL→Sybase em lotes de 20k registros, reprocessa timeout >2h, verifica duplicidade via NSU.

12. **Histórico Saldo**: Atualiza TbHistoricoSaldo diariamente (snapshot saldo total, indisponível, bloqueado).

13. **Validação Transação**: Verifica FlAtivo='S', TpDebitoCredito match operação (C/D).

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **ContaCorrente** (TbConta): Entidade central. Relaciona-se com:
  - **SaldoContaCorrente**: Composição (saldos total, bloqueado, indisponível, limite)
  - **MovimentoConta** (TbMovimentoDia/TbHistoricoMovimento): 1:N (histórico transações)
  - **SaldoBloqueado** (TbSaldoBloqueado): 1:N (bloqueios ativos)
  - **SaldoIndisponivel** (TbSaldoIndisponivel): 1:N (créditos D+x)
  - **ControleEncerramentoConta** (TbControleEncerramentoConta): 1:1 (controle encerramento)
  - **HistoricoSaldo** (TbHistoricoSaldo): 1:N (snapshots diários)

- **Transacao** (TbTransacao): Define tipo operação (C/D), relaciona-se com MovimentoConta via CdTransacao.

- **ControleEncerramentoConta**: Relaciona-se com:
  - **OcorEncerramentoConta** (TbOcorEncerramentoConta): 1:N (histórico ocorrências)
  - **Endereco** (TbEndereco): 1:1 (endereço correspondência)
  - **MotivoEncerramento** (TbMotivoEncerramentoConta): N:1 (motivo demanda)

- **ContaTetoGasto**: Configuração externa (properties), relaciona-se com ContaCorrente via hash SHA-256 (cdBanco+nuConta+cdTipoConta).

**Relacionamentos Chave:**
- ContaCorrente ↔ MovimentoConta (1:N)
- ContaCorrente ↔ SaldoBloqueado (1:N)
- ContaCorrente ↔ ControleEncerramentoConta (1:1)
- ControleEncerramentoConta ↔ OcorEncerramentoConta (1:N)
- MovimentoConta ↔ Transacao (N:1)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbConta | Tabela | SELECT | Dados conta corrente (saldos, situação, bloqueios, limites) |
| TbMovimentoDia | Tabela | SELECT | Movimentos do dia corrente (verificação duplicidade, consultas) |
| TbHistoricoMovimento | Tabela | SELECT | Histórico movimentos consolidados (consultas por documento/NSU) |
| TbTransacao | Tabela | SELECT | Definição transações (tipo C/D, flag ativa) |
| TbSaldoBloqueado | Tabela | SELECT | Bloqueios ativos de saldo (recuperação por motivo, último bloqueio) |
| TbHistoricoSaldoBloqueado | Tabela | SELECT | Histórico bloqueios (auditoria) |
| TbSaldoIndisponivel | Tabela | SELECT | Saldos indisponíveis D+x (consulta valor operação) |
| TbParametro | Tabela | SELECT | Data processamento atual conta corrente (DtAtualProcCC) |
| TbControleData | Tabela | SELECT | Controle aceite movimentação, data próximo movimento |
| TbMotivoBloqueio | Tabela | SELECT | Flag ignora bloqueio débito por motivo |
| TbControleEncerramentoConta | Tabela | SELECT | Controle encerramento (situação, datas, responsável) |
| TbOcorEncerramentoConta | Tabela | SELECT | Ocorrências encerramento (histórico ações) |
| TbMotivoEncerramentoConta | Tabela | SELECT | Motivos encerramento disponíveis |
| TbSituacaoEncerramentoConta | Tabela | SELECT | Situações encerramento (códigos 3-16) |
| TbModalidadeConta | Tabela | SELECT | Modalidades conta (join consultas encerramento) |
| TbCategoria | Tabela | SELECT | Categorias conta (join consultas encerramento) |
| TbLogAlteracao | Tabela | SELECT | Log alterações situação cadastral (auditoria) |
| TbEndereco | Tabela | SELECT | Endereços correspondência encerramento |
| TbCartaRelatorio | Tabela | SELECT | Cartas/relatórios encerramento |
| TbMovimentoDiaFintech (MySQL) | Tabela | SELECT | Fila movimentos Fintech pendentes processamento |
| TbMovimentoDiaFintech (Sybase) | Tabela | SELECT | Verificação duplicidade movimentos Fintech |
| TbCcs | Tabela | SELECT | Dados complementares conta (join consultas) |
| TbRcc | Tabela | SELECT | Relacionamento conta cliente (join consultas) |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbConta | Tabela | UPDATE | Atualização saldos (total, bloqueado, indisponível), situação cadastral, data encerramento, flag total banco |
| TbMovimentoDia | Tabela | INSERT/UPDATE/DELETE | Registro movimentos dia, atualização protocolo (NuDocumento), exclusão cancelamento |
| TbHistoricoMovimento | Tabela | INSERT/UPDATE/DELETE | Consolidação movimentos histórico, atualização protocolo, exclusão cancelamento |
| TbSaldoBloqueado | Tabela | INSERT/UPDATE | Criação bloqueios, atualização valor operação, desbloqueio (QtDiasBloqueioSaldo=0, CdMotivoDesbloqueio) |
| TbHistoricoSaldoBloqueado | Tabela | INSERT | Registro histórico bloqueios (auditoria) |
| TbSaldoIndisponivel | Tabela | INSERT/DELETE | Criação saldo indisponível D+x, exclusão após vigência |
| TbHistoricoSaldo | Tabela | INSERT/UPDATE | Snapshot diário saldos, atualização saldo indisponível |
| TbMovimentoCancelado | Tabela | INSERT | Registro movimentos cancelados (auditoria) |
| TbControleEncerramentoConta | Tabela | INSERT/UPDATE | Criação/atualização controle encerramento (situação, datas, responsável) |
| TbOcorEncerramentoConta | Tabela | INSERT | Registro ocorrências encerramento (demanda, cancelamento, confirmação) |
| TbLogAlteracao | Tabela | INSERT | Log alterações situação cadastral (auditoria) |
| TbEndereco | Tabela | INSERT/UPDATE | Criação/atualização endereço correspondência encerramento |
| TbMovimentoDiaFintech (MySQL) | Tabela | UPDATE | Atualização status processamento (StProcessamento=2), data alteração |
| TbMovimentoDiaFintech (Sybase) | Tabela | INSERT | Registro movimentos Fintech consolidados |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | Spring Boot Config | Configurações datasources, PubSub, pools conexão, timeouts, bypass bloqueios |
| logback-spring.xml | Leitura | Logback | Configuração logs JSON (console, níveis por pacote) |
| prometheus.yml | Leitura | Prometheus | Configuração scraping métricas Actuator |
| infra.yml | Leitura | K8s/Jenkins | Configurações infraestrutura por ambiente (des/uat/prd) |
| BV_TETO_GASTO_CONTAS (env var JSON) | Leitura | ContaTetoGastoProperties | Configuração contas teto gasto (hash→limite) |

**Observação**: Sistema não manipula arquivos de entrada/saída em disco (batch files). Logs são gravados em console (stdout) para captura por agregadores (Stackdriver/ELK).

---

## 10. Filas Lidas

| Nome da Fila | Tecnologia | Classe Consumidora | Breve Descrição |
|--------------|------------|-------------------|-----------------|
| **Não se aplica** | - | - | Sistema não consome filas. Apenas publica eventos (ver sessão 11). |

---

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Produtora | Breve Descrição |
|--------------|------------|------------------|-----------------|
| transacoesEfetivadas | GCP Pub/Sub | TransacaoEfetivadaPublisher | Publica eventos Movimento efetivado (crédito/débito/TEF) para auditoria/integração. Headers: CdBanco, CdTransacao, CdLiquidacao, TpOperacao, MDC ticket |
| creditosMonitorados | GCP Pub/Sub | CreditoMonitoradoPublisher | Publica eventos BloqueioMonitorado (créditos com restrição RF/PLD) para monitoramento compliance |

**Configuração**: Tópicos definidos em `PubSubProperties` (env vars `BVOD_TRANSACOES_EFETIVADAS_OUTPUT_CHANNEL`, `BVOD_BLOQUEIOS_MONITORADOS_OUTPUT_CHANNEL`).

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **Sybase ASE (DBCONTACORRENTE)** | Banco de Dados | Base legado BVSA: TbConta, TbMovimentoDia, TbHistoricoMovimento, TbSaldoBloqueado, TbControleEncerramentoConta. Pool: max 50 conexões, min 10, timeout 30s |
| **MySQL (CCBDContaCorrente)** | Banco de Dados | Base Fintech: TbMovimentoDiaFintech (fila processamento). Pool: max 10 conexões, min 5 |
| **Google Cloud Pub/Sub** | Mensageria | Publicação eventos transações efetivadas e bloqueios monitorados. Callback assíncrono via PubSubListener |
| **ConfigCat** | Feature Toggle | Controle features via FT_KEY (ambiente-específico) |
| **OAuth2 JWT** | Autenticação | Validação tokens JWT via Spring Security. URLs por ambiente (des/uat/prd) |
| **Prometheus** | Monitoramento | Scraping métricas Actuator endpoint `/actuator/prometheus` (porta 9090) |
| **Grafana** | Visualização | Dashboards métricas (datasource Prometheus) |

**Observação**: Sistema não integra diretamente com APIs REST externas. Comunicação assíncrona via Pub/Sub.

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Fortes:**
- **Arquitetura Hexagonal**: Separação clara entre domínio (domain), aplicação (application) e infraestrutura (adapters). Uso de ports/interfaces facilita testabilidade e manutenção.
- **Padrões de Projeto**: Factory pattern para roteamento multi-banco, AOP para transações, Strategy para validações (ValidaTransacao).
- **Cobertura de Testes**: Testes unitários abrangentes (JUnit5+Mockito) para services, mappers, utils, domains. Testes de contrato (Pact).
- **Configuração Externalizada**: Properties por ambiente (application.yml, infra.yml), feature toggles (ConfigCat).
- **Observabilidade**: Logs estruturados JSON, métricas Prometheus, health checks Actuator.
- **Segurança**: OAuth2 JWT, validação tokens, auditoria via TbLogAlteracao/TbMovimentoCancelado.

**Pontos de Melhoria:**
- **Complexidade Ciclomática**: Métodos longos em `ContaCorrenteServiceImpl` (ex: `efetivarCredito`, `efetivarDebito`) com múltiplas responsabilidades. Refatorar em métodos menores.
- **Acoplamento Temporal**: Dependência de ordem execução em TEF (débito→crédito). Considerar transação distribuída (Saga pattern).
- **Tratamento Exceções**: Uso excessivo de checked exceptions (`MovimentoException`) dificulta leitura. Preferir unchecked exceptions para erros negócio.
- **Documentação Código**: Falta Javadoc em classes públicas. Comentários inline escassos em lógicas complexas (ex: cálculo saldo disponível).
- **Magic Numbers**: Códigos hardcoded (ex: CdMotivoDesbloqueio=9, CdSituacao=2). Criar enums/constantes.
- **Queries SQL**: Alguns SQLs com isolation 0 (dirty read) podem causar inconsistências. Revisar necessidade.

**Recomendações:**
1. Refatorar services grandes em componentes menores (ex: `CreditoService`, `DebitoService`, `TefService`).
2. Adicionar Javadoc em interfaces públicas (ports, services).
3. Criar constantes para códigos mágicos (motivos bloqueio, situações).
4. Revisar isolation level queries críticas (saldos, bloqueios).
5. Implementar circuit breaker para integrações Pub/Sub (resiliência).

---

## 14. Observações Relevantes

1. **Multi-Banco**: Sistema suporta dois bancos (BV 161/655 e BVSA 436/413) com roteamento dinâmico via `TransactionRouter`. Factories injetam repositórios específicos por banco.

2. **Transações Distribuídas**: AOP `@TransactionByBank` gerencia transações multi-banco com timeout configurável (default 30s), lock pessimista (SET LOCK WAIT) e rollback condicional.

3. **Performance**: Queries otimizadas com hints índice, isolation 0 para consultas não-críticas, pools conexão ajustados (Sybase 50/10, MySQL 10/5).

4. **Auditoria Completa**: Todas operações críticas registradas em TbMovimentoCancelado, TbLogAlteracao, TbOcorEncerramentoConta. Eventos publicados em Pub/Sub para rastreabilidade.

5. **Regras Complexas**: Teto Gasto (limite saldo negativo configurável), Bloqueio Renda Fixa (judicial), Saldo Indisponível D+x (crédito temporário), TEF com desbloqueio automático.

6. **Integração Fintech**: Processamento batch assíncrono (lotes 20k registros) com reprocessamento automático timeout >2h. Consolidação MySQL→Sybase via stored procedure.

7. **Encerramento Workflow**: Demanda→Bloqueio→Confirmação com validações rigorosas (30 dias, saldos zerados, sem bloqueios). Suporte iniciativas Cliente/Banco/Emergencial.

8. **StandIn Mode**: Flag `standIn=true` bypassa validações críticas (saldo, situação) para contingência operacional.

9. **Configuração Ambiente-Específica**: Pools, URLs, flags (useMock, bypassContaBloqueada), timeouts ajustados por ambiente (des/uat/prd).

10. **Monitoramento Analítico**: Dashboards encerramento (totais, tempo aberto, gráficos hora/dia/mês/ano) para análise PLD e desinteresse.

11. **Versionamento API**: Endpoints versionados (`/v1/banco-digital/...`) para compatibilidade retroativa.

12. **Segurança Headers**: Validação `codigoBanco`, `numeroAgencia`, `numeroConta`, `tipoConta` em headers HTTP para autorização granular.

13. **Deprecação**: Método `efetivarTef` marcado deprecated. Usar `efetivarDebito` + `efetivarCredito` separadamente.

14. **Limitações**: Máximo 1000 registros por consulta (configurável via `MaximoRegistrosException`). Processamento Fintech limitado a 20k registros por lote.

15. **Tecnologia Legada**: Sybase ASE requer drivers específicos (jconn4). Considerar migração futura para PostgreSQL/Oracle.