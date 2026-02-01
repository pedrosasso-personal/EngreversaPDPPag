# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-spag-base-orch-liquidar-pagamento** é um microserviço orquestrador responsável pela liquidação de pagamentos no ecossistema SPAG (Sistema de Pagamentos). Atua como intermediário entre múltiplos sistemas (CCBD, ITP, Parcerias, Conta Corrente), coordenando o fluxo completo de liquidação, estorno, bloqueio/desbloqueio de saldo e notificações. Utiliza mensageria assíncrona (RabbitMQ, IBM MQ, Google PubSub) para integração com esteiras de pagamento e sistemas externos, além de Apache Camel para orquestração de rotas e processamento de mensagens.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application.java** | Classe principal Spring Boot para inicialização do microserviço |
| **LiquidarPagamentoController** | Expõe APIs REST para operações de liquidação, estorno, bloqueio de saldo e crédito |
| **PagamentoService** | Orquestra liquidação e estornos de pagamentos, gerencia tentativas e DLQ |
| **NotificacaoService** | Gerencia notificações de pagamentos (ITP, parceiros, PubSub), controla retentativas |
| **IntegrarPagamentoService** | Processa retornos do ITP, atualiza protocolo e login de devolução |
| **BloquearSaldoCcbdService** | Bloqueia saldo em conta via CCBD |
| **EfetivarDebitoService** | Confirma ou cancela bloqueio de saldo |
| **EfetivarCreditoService** | Efetiva crédito em conta corrente |
| **FilaRabbitListener** | Consome mensagens de filas RabbitMQ (PGFT/SPAG) |
| **FilaMQListener** | Consome mensagens de filas IBM MQ |
| **LiquidaPagamentoSubscriber** | Consome mensagens Google PubSub para liquidação de boletos |
| **PagamentoRepositoryImpl** | CRUD de pagamentos via atom service |
| **ContaCorrenteRepositoryImpl** | Executa estornos em conta corrente |
| **NotificacaoRepositoryImpl** | Publica notificações em filas RabbitMQ e registra no BD |
| **GoleiroValidacaoRepositoryImpl** | Valida TEF consultando movimentações em conta corrente (feature toggle) |
| **LiquidarPagamentoRouter** | Rota Camel para orquestração de liquidação de pagamentos |
| **NotificacaoRouter** | Rota Camel para orquestração de notificações |
| **PubSubNotificationRouter** | Rota Camel para envio de notificações via Google PubSub |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.x** (Web, AMQP, Actuator, Security)
- **Apache Camel 3.0.1** (orquestração de rotas e integração)
- **RabbitMQ** (mensageria PGFT e SPAG)
- **IBM MQ** (integração com esteira de pagamentos)
- **Google Cloud PubSub** (notificações assíncronas)
- **OAuth2** (autenticação via Gateway API)
- **Swagger/OpenAPI** (documentação de APIs)
- **Lombok** (redução de boilerplate)
- **Jackson/GSON** (serialização JSON)
- **JUnit 5 + Mockito** (testes unitários)
- **Maven** (gerenciamento de dependências)
- **Feature Toggle** (flags de funcionalidades experimentais)
- **Kubernetes/OpenShift** (deployment)
- **Prometheus + Grafana** (métricas e monitoramento)
- **Java 11**

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/notificarPagamento` | LiquidarPagamentoController | Notifica pagamento via dicionário |
| POST | `/v1/notificacaoITP` | LiquidarPagamentoController | Recebe notificação do ITP |
| POST | `/v1/realizarEstorno` | LiquidarPagamentoController | Executa estorno de pagamento |
| POST | `/v1/bloqueio-saldo` | LiquidarPagamentoController | Bloqueia saldo em conta CCBD |
| DELETE | `/v1/bloqueio-saldo` | LiquidarPagamentoController | Remove bloqueio de saldo |
| PUT | `/v1/bloqueio-saldo` | LiquidarPagamentoController | Confirma bloqueio de saldo |
| POST | `/v1/credito` | LiquidarPagamentoController | Efetiva crédito em conta |

---

## 5. Principais Regras de Negócio

1. **Conversão de Status ITP**: Status ITP código 2 é convertido para código 4 no processamento
2. **Limite de Tentativas de Estorno**: Configurável via `RabbitMQFilas.QTD_TENTATIVAS_PROCESSAMENTO_ESTORNO`
3. **Limite de Tentativas de Notificação**: Máximo de 10 tentativas (`MQUtil.QTD_MAX_RETENTATIVAS`)
4. **Limite de Tentativas ITP**: 120 tentativas para processamento de lançamento ITP
5. **Validação de Notificação Parceiro**: Requer `tipoIntegracao=EXTERNA` e `tipoCliente=WALLET`
6. **Reprocessamento ITP**: Mensagens com status `EM_PROCESSAMENTO` são reprocessadas
7. **Atualização de Login de Devolução**: Atualizado quando ISPB retorna status 2
8. **Goleiro TEF**: Valida divergências entre confirmação em CC e erro no SPAG (feature toggle)
   - Se conta = 10000001, valida favorecido
   - Interrompe notificação se houver divergência
   - Corrige SPAG se CC confirmado e SPAG com erro
   - 3 tentativas padrão para consulta CC
9. **Tratamento de Estorno 422**: Ignora erro 422 (pagamento já estornado)
10. **Geração de Ocorrências DLQ**: Pagamentos que excedem tentativas geram ocorrências para Dead Letter Queue
11. **Login Padrão Estorno**: Define `dsLogin="_spagEstorno"` se nulo

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **Pagamento**: Entidade central contendo dados do lançamento (cdLancamento, stLancamento, nuProtocolo, valores, datas)
- **EstornoPagamento**: Representa operação de estorno vinculada a um Pagamento
- **SituacaoPagamento**: Representa atualização de status de um Pagamento
- **NotificacaoParceiro**: Notificação enviada para parceiros externos
- **ClienteParceriasDTO**: Dados do cliente parceiro integrado
- **BloqueioSaldo**: Operação de bloqueio de saldo em conta CCBD
- **EfetivarCredito**: Operação de crédito em conta corrente

**Relacionamentos:**
- Pagamento (1) --- (0..N) EstornoPagamento
- Pagamento (1) --- (0..N) SituacaoPagamento
- Pagamento (1) --- (0..1) NotificacaoParceiro
- ClienteParceriasDTO (1) --- (0..N) NotificacaoParceiro

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| Pagamento (via atom service) | Tabela | SELECT | Consulta dados detalhados de pagamento por cdLancamento |
| Status ITP (via atom service) | Tabela | SELECT | Consulta status de integração com ITP por protocolo |
| Cliente Parcerias (via atom service) | Tabela | SELECT | Busca dados de cliente parceiro |
| Movimentação Bancária (via atom service) | Tabela | SELECT | Consulta movimentação por nuDocumento (validação Goleiro TEF) |
| Notificação Fintech (via atom service) | Tabela | SELECT | Busca notificações por protocolo |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| Pagamento (via atom service) | Tabela | UPDATE | Atualiza situação do pagamento (stLancamento) |
| Protocolo ITP (via atom service) | Tabela | UPDATE | Atualiza protocolo de integração ITP |
| Login Devolução (via atom service) | Tabela | UPDATE | Atualiza login de devolução quando ISPB retorna status 2 |
| Notificação Fintech (via atom service) | Tabela | INSERT | Registra envio de notificação para fintech |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | Spring Boot Config | Configurações de perfis, conexões, URLs de serviços |
| logback-spring.xml | Leitura | Logback | Configuração de logs da aplicação |
| cacerts | Leitura | Kubernetes Volume | Certificados SSL para comunicação segura |

---

## 10. Filas Lidas

| Nome da Fila | Tecnologia | Classe Responsável | Descrição |
|--------------|------------|-------------------|-----------|
| RETORNO_PAGAMENTO_ITP_PGFT_QUEUE | RabbitMQ PGFT | FilaRabbitListener | Retorno de pagamento do ITP |
| RETORNO_PAGAMENTO_ITP_PGFT_DLQ_QUEUE | RabbitMQ PGFT | FilaRabbitListener | Dead Letter Queue para estornos |
| RETORNO_PAGAMENTO_SPAG_QUEUE | RabbitMQ SPAG | FilaRabbitListener | Processa protocolo ITP |
| ESTORNO_PAGAMENTO_SPAG_QUEUE | RabbitMQ SPAG | FilaRabbitListener | Estorno por payload |
| QL.SPAG.ESTEIRA_PAGTO_RETORNO.INT | IBM MQ | FilaMQListener | Retorno da esteira de pagamento |
| business-spag-resultado-solicitacao-pagamento-boleto-sub | Google PubSub | LiquidaPagamentoSubscriber | Solicitação de liquidação de boleto |

---

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Responsável | Descrição |
|--------------|------------|-------------------|-----------|
| ESTORNO_PAGAMENTO_SPAG_QUEUE | RabbitMQ SPAG | PagamentoService | Envia solicitação de estorno |
| RETORNO_PAGAMENTO_SPAG_WAITING_QUEUE | RabbitMQ SPAG | IntegrarPagamentoRepository | Fila de espera para reprocessamento ITP |
| NOTIFICAR_ESTEIRA_OK_EXCHANGE | RabbitMQ PGFT | NotificacaoRepositoryImpl | Notificação de sucesso para esteira (routing: SPAG.esteiraPagamentoOk.{COD_ORIGEM}) |
| NOTIFICAR_ESTEIRA_ERRO_EXCHANGE | RabbitMQ PGFT | NotificacaoRepositoryImpl | Notificação de erro para esteira (routing: SPAG.esteiraPagamentoErro.{COD_ORIGEM}) |
| NOTIFICAR_PAGAMENTO_API_EXCHANGE | RabbitMQ PGFT | NotificacaoRepositoryImpl | Notificação via API |
| NOTIFICAR_PAGAMENTO_SPAG_EXCHANGE | RabbitMQ SPAG | NotificacaoSpagRepositoryImpl | Notificação interna SPAG |
| business-spag-base-notification-service | Google PubSub | PubSubTopicRepositoryImpl | Tópico de notificações PubSub |

---

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| sboot-spag-base-atom-pagamento | REST API | CRUD de pagamentos (atualizar situação, consultar por cdLancamento) |
| sboot-pgft-base-orch-pagamentos | REST API | Estorno de pagamento em conta corrente |
| sboot-spag-base-atom-parcerias | REST API | Consulta dados de cliente parceiro |
| sboot-spag-base-atom-notification-service | REST API | Registro e consulta de notificações fintech |
| sboot-sitp-base-atom-integrar-pagamento | REST API | Consulta status ITP e atualização de login |
| sboot-ccbd-base-orch-solic-debito | REST API | Bloqueio de saldo em conta CCBD |
| sboot-ccbd-base-orch-efet-debito | REST API | Confirmação/cancelamento de bloqueio |
| sboot-ccbd-base-orch-efet-credito | REST API | Efetivação de crédito em conta |
| sboot-ccbd-base-atom-movimentacoes | REST API | Consulta movimentações bancárias (validação Goleiro) |
| RabbitMQ PGFT | Mensageria | Filas de retorno ITP e notificações |
| RabbitMQ SPAG | Mensageria | Filas de estorno e notificações internas |
| IBM MQ (QM.ATA.01) | Mensageria | Retorno da esteira de pagamentos |
| Google Cloud PubSub | Mensageria | Notificações assíncronas e liquidação de boletos |
| Gateway API OAuth2 | Autenticação | Obtenção de tokens para chamadas REST |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada com separação clara de responsabilidades (domain, application, infra)
- Uso adequado de padrões de projeto (Hexagonal Architecture com ports/adapters)
- Cobertura de testes unitários presente com fixtures e mocks bem organizados
- Tratamento de exceções customizado e centralizado
- Uso de Lombok para redução de boilerplate
- Configuração por perfis (local, des, qa, uat, prd)
- Feature toggles para funcionalidades experimentais
- Orquestração clara com Apache Camel
- Documentação Swagger dos endpoints
- Separação de concerns entre services, repositories e routers

**Pontos de Melhoria:**
- Complexidade elevada em alguns services (PagamentoService, NotificacaoService) que poderiam ser decompostos
- Dependência forte de múltiplos sistemas externos aumenta acoplamento
- Configurações hardcoded em algumas classes (ex: tentativas, timeouts)
- Falta de documentação inline em alguns métodos complexos
- Alguns processors Camel muito simples poderiam ser inline
- Ausência de testes de integração documentados no resumo

O código demonstra maturidade técnica e boas práticas de engenharia de software, com espaço para melhorias em modularização e redução de complexidade.

---

## 14. Observações Relevantes

1. **Orquestrador Crítico**: Este microserviço é um componente central que integra múltiplos sistemas (CCBD, ITP, Parcerias, Conta Corrente), sendo crítico para o fluxo de liquidação de pagamentos.

2. **Múltiplas Tecnologias de Mensageria**: Utiliza simultaneamente RabbitMQ (PGFT e SPAG), IBM MQ e Google PubSub, demonstrando complexidade de integração.

3. **Goleiro de Validação TEF**: Funcionalidade crítica controlada por feature toggle que valida divergências entre confirmação em conta corrente e erro no SPAG, podendo interromper notificações ou corrigir status.

4. **Retentativas Configuráveis**: Sistema robusto de retentativas com limites específicos:
   - Estorno: configurável via propriedade
   - ITP: 120 tentativas
   - MQ: 10 tentativas
   - Notificação: 10 tentativas

5. **Dead Letter Queue**: Implementa tratamento de DLQ para pagamentos que excedem tentativas, gerando ocorrências específicas.

6. **Monitoramento**: Integração com Prometheus e Grafana para métricas de JVM, HTTP, HikariCP, GC e logs.

7. **Ambiente Local**: Fornece docker-compose para RabbitMQ, PubSub emulator e stack de métricas, facilitando desenvolvimento local.

8. **CI/CD**: Configurado para Jenkins com propriedades específicas (jdk11, springboot-ocp, platform GOOGLE).

9. **Segurança**: Utiliza OAuth2 para autenticação em chamadas REST e certificados SSL (cacerts) montados via volume Kubernetes.

10. **Versionamento**: Versão atual 0.28.0, com parent arqt-base-master-springboot 2.1.2.