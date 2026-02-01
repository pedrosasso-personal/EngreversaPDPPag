---
## Ficha Técnica do Sistema

### 1. Descrição Geral
Sistema orquestrador de transferências bancárias (TED, TEF, DOC, STN, PIX) integrado ao Sistema de Pagamentos Brasileiro (SPB). Processa solicitações de transferências, gerencia bloqueios/débitos em conta corrente, integra com múltiplos sistemas legados (ITP, CCBD, PGFT, SPB Core/Liberty), realiza validações de negócio, callbacks assíncronos para parceiros, devoluções automáticas e reprocessamento de transações. Arquitetura baseada em Apache Camel para orquestração de rotas, consumo de filas (RabbitMQ, IBM MQ, GCP PubSub) e integração REST com APIs externas.

---

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **TransferenciaController** | Endpoint REST v1 para transferências (TED/TEF/DOC/STN), callbacks, reprocessamento, devoluções, TED-In/STN-In |
| **TransferenciaV2Controller** | Endpoint REST v2 para clientes Wallet com retorno padronizado (EnumReturnCode) |
| **TransferenciaService** | Serviço principal de negócio: processa transferências, reprocessamento, devoluções automáticas, retorno SPB |
| **TransferenciaRouter** | Rota Camel para TEF: validação parceiro, efetivação CC, callback, reprocessamento |
| **TedSincronaRouter** | Rota Camel para TED síncrona (liq 31): bloqueio CC, integração SPB Core/Liberty, confirmação/cancelamento |
| **TedRouter** | Rota Camel TED legado: validação, efetivação TEF/TED, integração ITP/Esteira, callback |
| **TedInRouter** | Rota Camel TED-In: inclusão, validação, efetivação CC, devolução automática (timeout 17h), correspondência |
| **StnRouter** | Rota Camel STN: validação, bloqueio CC, integração SPB |
| **StnInRouter** | Rota Camel STN-In: validação, inclusão pagamento, geração TEF correspondente (TES0004R2/TES0010R2) |
| **PagamentoBloqueioCCRouter** | Rota Camel bloqueio/cancelamento CC: solicitação débito, cancelamento bloqueio, tratamento exceções |
| **CancelamentoPagamentoRouter** | Rota Camel cancelamento pagamento: confirmação CC, estorno, cancelamento bloqueio, devolução STR26 |
| **ConfirmacaoPagamentoRouter** | Rota Camel confirmação pagamento: confirma bloqueio/débito CC, atualiza lançamento origem STR26 |
| **ReprocessamentoRouter** | Rota Camel reprocessamento unificado: verifica duplicidade NSU, estorna, encaminha rota específica |
| **ReprocessamentoTedOutRouter** | Rota Camel reprocessamento TED-Out: consulta SPB, confirma/cancela conforme resultado |
| **ReprocessamentoStnRouter** | Rota Camel reprocessamento STN-In/Out: confirma SPAG ou gera nova TEF, consulta SPB |
| **CallbackRouter** | Rota Camel callback parceiro: validação cliente, resposta aprovado/rejeitado |
| **NotificacaoRouter** | Rota Camel notificação: envia mensagem RabbitMQ para status 3/4/8/14/99 |
| **ConsultarTedOutRouter** | Rota Camel consulta TED-Out: consulta movimento SPB/SPB-Core por NSU/cdLancamento |
| **LiquidacaoPagamentoCCRouter** | Rota Camel liquidação CC: credita favorecido, atualiza status confirmado, notifica |
| **PagamentoRepositoryImpl** | Integração PagamentoApi (SPAG): incluir, atualizar, obter, gerar autenticação, verificar duplicidade NSU |
| **MovimentoRepositoryImpl** | Integração MovimentoApi (PGFT) e EfetivarDebitoApi (CCBD): efetuarDebito, movimentar, confirmarBloqueio, estornar |
| **TefRepositoryImpl** | Integração EfetivarTefApi, EfetivarDebitoApi: realizaTransacao, efetivaTef, debitarRemetente, creditarFavorecido |
| **IntegracaoSpbRepositoryImpl** | Integração IntegrarApi (Liberty SPB): integrarSPB, retornoSPB, replicarIntegrarSPB |
| **IntegrarSpbCoreRestRepositoryImpl** | Integração IntegracaoSpbCoreApi REST: integrarSPBCoreRest com feature toggle NSU |
| **SuporteNegocioRepositoryImpl** | Integração ValidaTransferenciaApi: validaTransferencia v1/v2, valida campos CC |
| **ProdutoRepositoryImpl** | Integração ProdutoApi (ITP): consulta transação, transação+flagSaldo |
| **CadastroRepositoryImpl** | Integração CadastroApi (ITP): busca banco por COMPE/global |
| **SolicitarDebitoRepositoryImpl** | Integração SolicitarDebitoApi (CCBD): solicitar débito com bloqueio |
| **CancelarBloqueioRepositoryImpl** | Integração CancelarBloqueioApi (CCBD): cancela bloqueio saldo |
| **MovimentacoesRepositoryImpl** | Integração ConsultarMovimentacaoPorDocumentoApi: confirma pagamento CC, valida código bloqueio |
| **LiquidarPagamentoRepositoryImpl** | Integração LiquidarPagamentoApi: estornar via RabbitMQ PGFT ou direto |
| **ParceriaRepositoryImpl** | Integração ParceriasApi: buscar parceiro por CNPJ/conta/liquidação, valida tipo integração E |
| **SegurancaRepositoryImpl** | Integração SegurancaApi: validar clientId por CNPJ/codOrigem |
| **IntegrarPagamentoITPRepositoryImpl** | Publica RabbitMQ PGFT: fila integrarPagamentoITP |
| **IntegrarEsteiraRepositoryImpl** | Publica JMS MQ: filas TED/TEF, gera XML via Velocity |
| **CallbackParceiroRepositoryImpl** | Publica RabbitMQ PGFT: fila confirmarPagamentoApi |
| **NotificacaoSpagRepositoryImpl** | Publica RabbitMQ SPAG: fila notificationService |
| **ConfirmacaoSpbPubSubListener** | Listener PubSub confirmação SPB: processa ação aguardar/confirmar, feature toggle NSU |
| **RecebimentoTedInPubSubListener** | Listener PubSub TED-In: converte TedInRequest, chama TransferenciaService.tedIn |
| **ReprocessamentoSpbPubSubListener** | Listener PubSub reprocessamento: lê LancamentoReprocessar, chama reprocessarTransferencia |
| **TransferenciaRetornoTedListener** | Listener JMS retorno TED: parseia XML PGFTBVSA, processa via TransferenciaService |
| **TransferenciaMapper** | Mapeamento bidirecional Representation ↔ Transferencia (v1/v2/TedRefund/TedIn/Stn) |
| **PagamentoMapper** | Mapeamento bidirecional Transferencia ↔ Pagamento/Protocolo, truncamento strings |
| **MovimentoMapper** | Mapeamento Transferencia → Movimento |
| **EfetivarTefMapper** | Mapeamento Transferencia → EfetivarTef, Request (CCBD) |
| **IntegrarSpbMapper** | Mapeamento Transferencia → IntegracaoSpbOperRequest (Liberty) |
| **IntegrarSpbCoreMapper** | Mapeamento Transferencia → IntegrarSPBRequestRepresentation (Core) |
| **SuporteNegocioMapper** | Mapeamento bidirecional Transferencia ↔ ValidaRequest/ValidaResponse |
| **ProdutoMapper** | Mapeamento bidirecional BuscaTransacao ↔ IdentificadorTransacao, Transacao → TransacaoLancamento |
| **ExceptionHandlerConfig** | Handler global exceções: HttpMessageNotReadable, MethodArgumentNotValid, Exception genérica |
| **ExceptionControllerHandler** | Tratamento centralizado exceções negócio: PagamentoException, TransferenciaException, etc |
| **FeatureToggleService** | Gerencia feature toggles: TED síncrona sem estorno, envio NSU SPB Core, etc |
| **ApplicationConfig** | Configuração beans: APIs clients, Routers Camel |
| **PubSubInputChannelConfiguration** | Config consumo filas GCP PubSub: confirmação SPB, TED-In, reprocessamento |
| **IbmMqConfig** | Config IBM MQ JMS listener: fila retornoTED start/stop dinâmico |
| **RabbitMQPgftConfiguration** | Config RabbitMQ PGFT: host, port, vhost, user, pass |
| **RabbitMQSpagConfiguration** | Config RabbitMQ SPAG: conexão separada |
| **RestTemplateConfiguration** | Configs RestTemplate: timeout 60s, basic auth, logging interceptor |
| **OpenApiConfiguration** | Config Swagger/OpenAPI: Bearer token security |

---

### 3. Tecnologias Utilizadas

- **Framework:** Spring Boot 2.x, Apache Camel 3.22.4
- **Linguagem:** Java 11
- **Mensageria:** RabbitMQ (PGFT/SPAG), IBM MQ (ATA), GCP PubSub
- **Integração REST:** RestTemplate, OpenFeign (APIs clients)
- **Segurança:** OAuth2 Resource Server, JWT, Basic Auth
- **Template Engine:** Apache Velocity 2.3 (geração XML)
- **Documentação API:** Swagger/OpenAPI 3
- **Serialização:** Jackson (JSON), JAXB (XML)
- **Observabilidade:** Spring Actuator, Logback (JSON), MDC tracking
- **Feature Toggles:** ConfigCat (FeatureToggle 3.0.1)
- **Testes:** JUnit 5, Mockito, Spring Test, Apache Camel Test
- **Build:** Maven 3.3+
- **Containerização:** Docker, Kubernetes (OpenShift)
- **Banco de Dados:** Não acessa diretamente (via APIs externas)
- **Bibliotecas:** Commons Lang3, Lombok, Velocity, JAXB, JavaTimeModule

---

### 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/transferencia | TransferenciaController | Solicita transferência TED/TEF/DOC |
| POST | /v1/transferenciaStn | TransferenciaController | Solicita transferência STN |
| POST | /v1/processarCallBackParceiro | TransferenciaController | Processa callback parceiro |
| POST | /v1/reprocessarTransferencia/{cdLancamento} | TransferenciaController | Reprocessa transferência por código lançamento |
| POST | /v1/processarTransferenciaManual/{cdLancamento} | TransferenciaController | Processa transferência manual |
| POST | /v1/revertExternalTransfer | TransferenciaController | Reverte transferência externa |
| POST | /v1/automaticTedRefund | TransferenciaController | Devolução automática TED |
| POST | /v1/confirmaPagamentoBloqueioTeste | TransferenciaController | Confirma pagamento bloqueio (teste) |
| POST | /v1/tedIn | TransferenciaController | Recebe TED entrada |
| POST | /v1/stnIn | TransferenciaController | Recebe STN entrada |
| POST | /v2/transferencia | TransferenciaV2Controller | Solicita transferência v2 (Wallet) |
| GET | /v1/featureToggle/{feature} | FeatureToggleController | Consulta feature toggle |
| POST | /cancelamento-pagamento-teste/cancelar/{cdLancamento} | CancelamentoPagamentoControllerTest | Cancela pagamento (teste) |
| POST | /cancelamento-pagamento-teste/creditar-conta/{cdLancamento} | CancelamentoPagamentoControllerTest | Credita conta (teste) |

---

### 5. Principais Regras de Negócio

- **Validação Transferências:** Valida transações via SuporteNegocioApi (v1/v2), verifica campos CC (remetente/favorecido), códigos transação/banco, flag devolução automática, confirmação sem SPB
- **Bloqueio/Débito CC:** Solicita débito com bloqueio (BLOQUEIO_PARCIAL) para PAGAMENTO e TED judicial; cancela bloqueio em caso de erro; confirma bloqueio após confirmação SPB
- **Integração SPB:** Envia mensagens para SPB Core (REST) ou Liberty (SOAP); feature toggle para envio NSU; trata retorno SPB (R1=4 confirma, R1=9 cancela); reprocessamento com 3 retentativas
- **Conta Especial 10000001:** Bypass para Tesouro Nacional (bancos 655/413, tipos IF/CT/PG); não debita/credita; validações específicas liquidações 61/62
- **Liquidações:** Suporta liquidações 1, 12, 21, 31, 53, 56, 57, 61, 62; STR26 (liq 57) com código de barras; conversão liq 57→22 em estorno
- **Duplicidade NSU:** Verifica duplicidade NSU antes inclusão; retorna HTTP 208 (ALREADY_REPORTED) se duplicado; permite reprocessamento se novo
- **Parcerias:** Valida parceiro tipo integração E; modalidades 25/26 vetadas; urlCallback obrigatório; callback assíncrono para validação cliente
- **Correspondência TED:** Gera TED correspondente para bancos 655/413 (CNAB→CC, origem 78, liq 31/32); vincula TEF à TED original
- **Devolução Automática TED-In:** Devolve automaticamente TED-In após timeout 17h se não lançado CC; inverte remetente/favorecido; código motivo devolução
- **Reprocessamento:** Unificado para TEF/TED/STN; verifica duplicidade NSU; estorna se necessário; encaminha para rota específica; valida lançamento CC
- **TED Judicial:** Identifica transação depósito judicial; gera bloqueio CCBD; valida codIdentdTransf obrigatório
- **STN-In:** Valida STN-In; gera TEF correspondente se TES0004R2 (com UG) ou TES0010R2 (com nuControleSPB); vincula TEF à STN
- **Confirmação Sem SPB:** Flag flConfirmaSemSPB permite confirmação sem integração SPB
- **Notificação:** Envia notificação RabbitMQ SPAG para status 3/4/8/14/99
- **Estorno:** Estorna pagamento via RabbitMQ PGFT ou direto; trata erro inclusão TEF (422); ajusta protocolo
- **Processamento Manual:** Valida status permitido (ZERO); atualiza remetente/favorecido; envia callback se necessário
- **Resiliência:** Retry logic com 3 tentativas para integração SPB; PagamentoResilienciaException; tratamento exceções HTTP (4xx/5xx)
- **Validação Conta Espelho:** Valida status conta (encerrada, bloqueada); rejeita se inclusão judicial
- **Conversão Banco:** Converte código banco global→COMPE para STN; identifica conversão CNAB→CC
- **Fintech:** Valida CPF fintech em integração API; mapeamento fintech resto/favorecido; co-titulares
- **Histórico/Nome:** Truncamento strings (histórico 100 chars, nome 60 chars); remoção caracteres especiais; remoção espaços duplos
- **Agência:** Reformatação agência (padding zeros); tratamento agência null
- **Data:** Atualiza dataMovimento/dataLancamento; compara dtLancamento com 2h atrás; reformata data lançamento
- **Enums:** Conversões TipoPessoa, TipoConta, TipoLancamento, TipoDocumento, SimNaoEnum, FinalidadeEnum, SituacaoLancamentoEnum
- **Autenticação Bancária:** Gera código autenticação bancária para pagamento
- **Parametrização Correspondência:** Consulta parametrização correspondência TED com retries (@Retryable)

---

### 6. Relação entre Entidades

**Entidades Principais:**
- **Transferencia:** Entidade central representando transferência bancária (TED/TEF/DOC/STN). Contém dados transação, participantes (remetente/favorecido/fintech), valores, datas, códigos SPB, flags negócio
- **Protocolo:** Representa protocolo transação com status, código lançamento, autenticação bancária, erro, httpStatusCode
- **Participante:** Representa remetente/favorecido/fintech com dados pessoais (CPF/CNPJ, nome, tipo pessoa), bancários (banco, agência, conta, tipo conta), endereço
- **ContaCorrente:** Dados conta corrente (banco, agência, conta, tipo conta, transação)
- **PagamentoOcorrencia:** Representa ocorrência pagamento com situação lançamento, protocolo, transferência, sqUltimoBloqueioSaldo
- **Pagamento:** Entidade pagamento SPAG com dados completos transferência, participantes, protocolo, flags negócio
- **Movimento:** Representa movimento CCBD/PGFT com dados débito/crédito, NSU, data efetivação
- **SolicDebito:** Representa solicitação débito CCBD com bloqueio saldo
- **RetornoSPBRequest:** Representa retorno SPB com resultado R1, código movimento, controle SPB
- **TransacaoLancamento:** Representa transação produto ITP com código evento, tipo lançamento, indicadores débito CC
- **BancoDomain:** Representa banco com código COMPE, ISPB, nome
- **Parceiro:** Representa parceiro fintech com CNPJ, tipo integração, modalidade, urlCallback
- **TedInRequest:** Representa solicitação TED entrada com dados participantes, valores, códigos SPB
- **LancamentoReprocessar:** Representa lançamento para reprocessamento com código lançamento

**Relacionamentos:**
- Transferencia 1:1 Protocolo (composição)
- Transferencia 1:N Participante (remetente, favorecido, fintech, co-titulares)
- Transferencia 1:1 ContaCorrente (composição)
- PagamentoOcorrencia N:1 Protocolo (agregação)
- PagamentoOcorrencia N:1 Transferencia (agregação)
- Pagamento 1:1 Protocolo (composição)
- Pagamento 1:N Participante (composição)
- Movimento N:1 Transferencia (agregação)
- SolicDebito N:1 Transferencia (agregação)
- RetornoSPBRequest N:1 Transferencia (agregação)
- TransacaoLancamento N:1 Transferencia (agregação)
- BancoDomain N:1 Participante (agregação)
- Parceiro N:1 Transferencia (agregação)

---

### 7. Estruturas de Banco de Dados Lidas

**não se aplica** (sistema não acessa banco de dados diretamente; todas operações via APIs REST externas)

---

### 8. Estruturas de Banco de Dados Atualizadas

**não se aplica** (sistema não acessa banco de dados diretamente; todas operações via APIs REST externas)

---

### 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Descrição |
|-----------------|----------|-------------------------|-----------|
| dicionario-esteira-pagamento.xml | leitura | MqAdapter (Velocity) | Template XML para geração mensagem esteira pagamentos (TED/TEF) |
| logback-spring.xml | leitura | Spring Boot (profiles) | Configuração logs JSON por ambiente (local/des/qa/uat/prd) |
| application.yml | leitura | Spring Boot | Configuração aplicação (URLs, filas, segurança, profiles) |
| cacerts | leitura | Kubernetes (globalVol) | Certificados SSL para integrações HTTPS |

---

### 10. Filas Lidas

| Nome da Fila | Tipo | Tecnologia | Classe Responsável | Descrição |
|--------------|------|------------|-------------------|-----------|
| confirmacaoSpbInputChannel | subscription | GCP PubSub | ConfirmacaoSpbPubSubListener | Confirmação SPB (ação aguardar/confirmar) |
| recebimentoTedInInputChannel | subscription | GCP PubSub | RecebimentoTedInPubSubListener | Recebimento TED entrada |
| reprocessamentoSpbInputChannel | subscription | GCP PubSub | ReprocessamentoSpbPubSubListener | Reprocessamento SPB |
| ${ibm.mq.retornoTED} | queue | IBM MQ | TransferenciaRetornoTedListener | Retorno TED (XML PGFTBVSA) |

---

### 11. Filas Geradas

| Nome da Fila | Tipo | Tecnologia | Classe Responsável | Descrição |
|--------------|------|------------|-------------------|-----------|
| integrarPagamentoITP | queue | RabbitMQ PGFT | IntegrarPagamentoITPRepositoryImpl | Integração pagamento ITP |
| estornoPagamento | queue | RabbitMQ PGFT | LiquidarPagamentoRepositoryImpl | Estorno pagamento |
| confirmarPagamentoApi | queue | RabbitMQ PGFT | CallbackParceiroRepositoryImpl | Callback validação parceiro |
| notificationService | queue | RabbitMQ SPAG | NotificacaoSpagRepositoryImpl | Notificação status pagamento (CASHOUT) |
| ${ibm.mq.queueTEF} | queue | IBM MQ | IntegrarEsteiraRepositoryImpl | Integração esteira TEF (XML Velocity) |
| ${ibm.mq.queueTED} | queue | IBM MQ | IntegrarEsteiraRepositoryImpl | Integração esteira TED (XML Velocity) |

---

### 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| **SPAG - PagamentoApi** | REST | Inclusão, atualização, obtenção pagamento; geração autenticação bancária; verificação duplicidade NSU; parametrização correspondência |
| **SPAG - SuporteNegocioApi** | REST | Validação transferência v1/v2; validação campos CC (remetente/favorecido) |
| **SPAG - LiquidarPagamentoApi** | REST | Estorno pagamento (notificação ITP, realização estorno) |
| **SPAG - SegurancaApi** | REST | Validação clientId por CNPJ/codOrigem |
| **SPAG - ParceriasApi** | REST | Busca parceiro por CNPJ/conta/liquidação; validação correspondente |
| **SPAG - IntegracaoSpbCoreApi** | REST | Integração SPB Core (envio mensagens, consulta movimento) |
| **SPAG - MovimentoSpbApi** | REST | Consulta movimento SPB por cdMovimentoOrigem |
| **ITP - CadastroApi** | REST | Busca banco por COMPE/global |
| **ITP - ProdutoApi** | REST | Consulta transação, transação+flagSaldo |
| **ITP - IntegrarPagamentoApi** | REST | Integração pagamento ITP (via RabbitMQ) |
| **CCBD - EfetivarTefApi** | REST | Efetivação TEF (realização transação, débito remetente, crédito favorecido) |
| **CCBD - SolicitarDebitoApi** | REST | Solicitação débito com bloqueio saldo |
| **CCBD - EfetivarDebitoApi** | REST | Efetivação débito (efetuarDebito, confirmarBloqueio) |
| **CCBD - CancelarBloqueioApi** | REST | Cancelamento bloqueio saldo |
| **CCBD - ConsultarMovimentacaoPorDocumentoApi** | REST | Confirmação pagamento CC, validação código bloqueio |
| **PGFT - MovimentoApi** | REST | Movimentação (efetuarDebito, movimentar, confirmarBloqueio, estornar) |
| **GLOB - ClienteDadosCadastraisApi** | REST | Consulta conta conveniada por número conta |
| **Liberty SPB - IntegrarApi** | REST | Integração SPB (integrarSPB, retornoSPB, replicarIntegrarSPB) |
| **Fintech - ConsultaContaApi** | REST | Consulta dados conta fintech (Basic Auth) |
| **Gateway OAuth** | OAuth2 | Autenticação OAuth2 (clientId, clientSecret, tokenUrl) |
| **RabbitMQ PGFT** | AMQP | Filas: integrarPagamentoITP, estornoPagamento, confirmarPagamentoApi |
| **RabbitMQ SPAG** | AMQP | Fila: notificationService |
| **IBM MQ ATA** | JMS | Filas: queueTEF, queueTED, retornoTED |
| **GCP PubSub** | PubSub | Subscriptions: confirmacaoSpb, recebimentoTedIn, reprocessamentoSpb |

---

### 13. Avaliação da Qualidade do Código

**Nota:** 8/10

**Justificativa:**
- **Pontos Positivos:**
  - Arquitetura bem estruturada em camadas (Controller → Service → Repository → Camel Routes)
  - Separação clara de responsabilidades (domain, application, common)
  - Uso extensivo de padrões de projeto (Builder, Mapper, Repository, Strategy)
  - Tratamento robusto de exceções com handlers centralizados
  - Logs estruturados (JSON) com MDC tracking para rastreabilidade
  - Feature toggles para habilitar/desabilitar funcionalidades dinamicamente
  - Retry logic e resiliência para integrações externas
  - Testes unitários abrangentes (35+ classes de teste, cobertura mappers/repositories/controllers/listeners/routers)
  - Documentação OpenAPI/Swagger
  - Configuração externalizada (application.yml, profiles)
  - Uso de Lombok para redução boilerplate
  - Versionamento API (v1/v2)
  - Suporte a múltiplos protocolos de mensageria (RabbitMQ, IBM MQ, PubSub)

- **Pontos de Melhoria:**
  - Complexidade elevada em algumas rotas Camel (TedSincronaRouter, TedInRouter com 10+ sub-rotas)
  - Acoplamento forte com APIs externas (mudanças em contratos impactam múltiplas classes)
  - Falta de documentação inline em alguns processadores Camel (lógica negócio complexa)
  - Uso de strings mágicas em algumas propriedades Camel (poderia usar constantes)
  - Alguns mappers com lógica negócio (deveria estar em services/processors)
  - Testes de integração limitados (foco em testes unitários com mocks)
  - Falta de cache para consultas frequentes (ex: banco, transação)
  - Alguns métodos longos em mappers (>50 linhas)
  - Tratamento genérico de exceções em alguns pontos (catch Exception)
  - Falta de métricas de negócio (ex: taxa sucesso transferências, tempo médio processamento)

---

### 14. Observações Relevantes

- **Arquitetura Multi-Camadas:** Sistema segue arquitetura hexagonal com separação clara entre domain (entidades, portas), application (controllers, services, adapters) e common (utils, configs)
- **Apache Camel:** Uso intensivo de Camel para orquestração de rotas complexas; 15+ routers com sub-rotas, processadores customizados, tratamento exceções, retry logic
- **Mensageria Heterogênea:** Suporta 3 tecnologias mensageria (RabbitMQ PGFT/SPAG, IBM MQ ATA, GCP PubSub) com configurações separadas
- **Feature Toggles:** Uso extensivo de feature toggles (ConfigCat) para habilitar/desabilitar funcionalidades por ambiente/cliente (ex: TED síncrona sem estorno, envio NSU SPB Core)
- **Conta Especial 10000001:** Lógica específica para Tesouro Nacional (bypass débito/crédito, validações liquidações 61/62)
- **Correspondência TED:** Geração automática TED correspondente para bancos 655/413 (CNAB→CC)
- **Devolução Automática:** TED-In com timeout 17h; devolve automaticamente se não lançado CC
- **Reprocessamento Unificado:** Rota única para reprocessamento TEF/TED/STN com verificação duplicidade NSU
- **Resiliência:** Retry logic com 3 tentativas para integração SPB; tratamento exceções HTTP (4xx/5xx); PagamentoResilienciaException
- **Versionamento API:** Suporte v1 (legado) e v2 (Wallet) com retorno padronizado EnumReturnCode
- **OAuth2 Resource Server:** Segurança baseada em JWT; integração com Gateway OAuth para obtenção tokens
- **Velocity Templates:** Geração XML mensagens esteira pagamentos via templates Velocity
- **Mapeamento Complexo:** 20+ mappers para conversão entre representations/domains; truncamento strings, remoção caracteres especiais, conversões enums
- **Testes Abrangentes:** 35+ classes de teste unitário; cobertura mappers, repositories, controllers, listeners, routers; uso Mockito, ArgumentCaptor, verify
- **Configuração Kubernetes:** Infra-as-code com configmap (vars), secret (senhas), probes (liveness/readiness), resources (req/lim), globalVol (cacerts)
- **Profiles Spring:** Suporte múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas
- **Logs JSON:** Logback configurado para logs estruturados JSON por ambiente
- **Docker Compose:** Suporte desenvolvimento local com RabbitMQ, PubSub emulator
- **Jenkins Pipeline:** Integração CI/CD com Jenkins (jenkins.properties)
- **Swagger/OpenAPI:** Documentação API com Bearer token security
- **Actuator:** Endpoints health/metrics para monitoramento
- **Exceções Customizadas:** 15+ exceções negócio customizadas (PagamentoException, TransferenciaException, EfetivacaoDebitoException, etc)
- **Enums Negócio:** 20+ enums para padronização (TipoPessoa, TipoConta, TipoLancamento, SituacaoLancamentoEnum, ExceptionReasonEnum, etc)
- **Processadores Camel:** 37+ processadores customizados para lógica negócio (validação, enriquecimento, transformação, tratamento erro)
- **Callbacks Assíncronos:** Suporte callbacks parceiros para validação cliente (aprovado/rejeitado)
- **Integração SPB Dual:** Suporta integração SPB Core (REST) e Liberty (SOAP) com feature toggle
- **Validação Negócio:** Validações complexas (TED judicial, conta espelho, duplicidade NSU, parcerias, correspondência, fintech)
- **Estorno Inteligente:** Estorno automático em caso de erro; conversão liquidação 57→22 em estorno STR26
- **Processamento Manual:** Suporte processamento manual transferências com validação status permitido
- **Notificação Assíncrona:** Notificação RabbitMQ SPAG para status específicos (3/4/8/14/99)
- **Liquidações Múltiplas:** Suporte 9 tipos liquidação (1, 12, 21, 31, 53, 56, 57, 61, 62) com regras específicas
- **STN-In Inteligente:** Geração automática TEF correspondente para STN-In (TES0004R2/TES0010R2)
- **Timeout Configurável:** Timeout 60s para integrações REST; configurável via properties
- **Basic Auth:** Suporte Basic Auth para consulta conta fintech
- **MDC Tracking:** Rastreamento distribuído via MDC (ticket UUID)
- **Ack/Nack Manual:** Controle manual ack/nack mensagens PubSub
- **FlowControl PubSub:** Configuração FlowControl (maxElem=1000, maxBytes=100MB, behavior=Block)
- **Concorrência JMS:** Concorrência configurável para listener IBM MQ
- **Jackson Converter:** Uso Jackson converter com JavaTimeModule para RabbitMQ
- **JAXB:** Suporte JAXB para parsing XML mensagens JMS
- **Commons Lang3:** Uso Commons Lang3 para manipulação strings
- **ArchUnit:** Testes arquitetura com ArchUnit (profile architecture)
- **Maven Multi-Module:** Projeto multi-módulo (common, domain, application)
- **Parent POM:** Herança arqt-base-master-springboot 4.0.8
- **Java 11:** Uso Java 11 (LocalDate, OffsetDateTime, LocalDateTime)
- **Spring Boot 2.x:** Framework base Spring Boot 2.x
- **Camel 3.22.4:** Apache Camel 3.22.4 para orquestração
- **Microservices Error:** Uso microservices-error 0.14.7 para padronização erros
- **FeatureToggle 3.0.1:** Biblioteca FeatureToggle 3.0.1 para feature toggles
- **Lombok:** Uso extensivo Lombok (@Builder, @Data, @Slf4j, @UtilityClass)
- **OpenShift:** Deploy em OpenShift (platform GOOGLE)
- **Maven 3.9:** Build com Maven 3.9
- **JDK 11:** Compilação com JDK 11
- **Gitignore:** Gitignore completo (env, IDE, target, logs)
- **README:** Documentação básica projeto (pré-requisitos, compile, exec, links)