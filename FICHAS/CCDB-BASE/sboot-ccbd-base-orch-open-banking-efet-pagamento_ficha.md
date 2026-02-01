# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema orquestrador responsável por processar pagamentos e agendamentos PIX via Open Banking. O componente atua como listener de filas RabbitMQ, recebendo ordens de pagamento/agendamento da camada BVOpen e orquestrando a efetivação dessas transações através de integrações com diversos serviços internos (efetivação PIX, dados cadastrais, cancelamento de agendamentos, movimentações PIX). Implementa validações de negócio, controle de fraude, polling de status de transações e tratamento de erros com reenvio automático.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot que inicializa a aplicação |
| `PaymentListener` / `PixPfPaymentListener` | Listeners abstratos e concretos que consomem mensagens de pagamento das filas RabbitMQ |
| `OpenBankingEfetPagamentoService` | Serviço principal que orquestra o fluxo de efetivação/agendamento de pagamentos |
| `OpenBankingEfetPagamentoRouter` | Rota Apache Camel principal que define o fluxo de processamento de pagamentos |
| `CancelRouter` / `CancelBatchRouter` | Rotas Camel para cancelamento individual e em lote de agendamentos |
| `EfetTransfPixRepositoryImpl` | Implementação de integração com serviço de efetivação de transferências PIX |
| `GlobalRepositoryImpl` | Implementação de integração com serviço de dados cadastrais de clientes |
| `CancelScheduleRepositoryImpl` | Implementação de integração com serviço de cancelamento de agendamentos |
| `PixMovimentacoesRepositoryImpl` | Implementação de integração com serviço de movimentações PIX (consulta de status) |
| `AtualizaStatusRepositoryImpl` | Responsável por publicar eventos de atualização de status na fila |
| `OpenBankingEfetPagamentoMapper` | Mapeamento entre objetos de domínio e representações de APIs externas |
| `ValidatorChain` / `Validators` | Implementação de chain of responsibility para validações de negócio |
| `HandlerPaymentProcessedListener` / `HandlerErrorymentEventsListener` | Handlers de eventos para publicação em filas de status e erro |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Apache Camel 3.0.1** (orquestração de rotas e integração)
- **RabbitMQ** (mensageria assíncrona)
- **Spring AMQP** (integração com RabbitMQ)
- **Swagger/OpenAPI 3.0** (documentação de APIs)
- **Springfox 3.0.0** (geração de documentação Swagger)
- **MapStruct 1.5.5** (mapeamento de objetos)
- **Lombok** (redução de boilerplate)
- **Prometheus + Grafana** (métricas e monitoramento)
- **HikariCP** (pool de conexões)
- **Logback** (logging)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **JUnit 5** (testes unitários)
- **Rest Assured** (testes de API)
- **Pact** (testes de contrato)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/banco-digital/open-banking/pagamentos/cancelar` | `PagamentoController` | Cancela um agendamento de pagamento individual |
| POST | `/v1/banco-digital/open-banking/pagamentos/cancelar-por-consentimento` | `PagamentoController` | Cancela todos os agendamentos associados a um consentimento |

---

## 5. Principais Regras de Negócio

1. **Validação de Pagamentos**: Valida CPF/CNPJ do credor, EndToEndId único e valor não zerado antes de processar
2. **Análise de Fraude**: Integra com sistema de fraude (Feedzai) e rejeita transações reprovadas
3. **Polling de Status**: Para pagamentos imediatos, realiza polling (até 120 tentativas) no serviço de movimentações PIX para obter status atualizado
4. **Diferenciação Pagamento/Agendamento**: Pagamentos com `scheduleDate` são tratados como agendamentos e não entram no fluxo de polling
5. **Reenvio Automático**: Mensagens com erro são reenviadas automaticamente (máximo 2 tentativas via DLQ) antes de irem para PLQ (Parking Lot Queue)
6. **Mapeamento de Erros**: Converte códigos de erro internos para códigos padronizados Open Banking (V1 e V2)
7. **Atualização de Status**: Publica eventos de status apenas quando há mudança efetiva de status da transação
8. **Cancelamento de Agendamentos**: Suporta cancelamento individual (por NSU) e em lote (por consentimento)
9. **Validação de Limites**: Integra com serviço de dados cadastrais para validar limites e saldos
10. **Tratamento de Timeout**: Implementa timeout e retry para chamadas a serviços externos

---

## 6. Relação entre Entidades

**Principais entidades de domínio:**

- **Payment**: Representa uma ordem de pagamento/agendamento PIX com todos os dados do pagador, beneficiário, valor, forma de iniciação, etc.
- **PaymentStatus**: Representa o status de processamento de um pagamento (RCVD, PDNG, ACCP, ACSC, RJCT, SCHD, etc.)
- **EfetTransPixRequest**: Encapsula dados para requisição de efetivação de transferência PIX
- **PaymentCancelRequest**: Encapsula dados para cancelamento de agendamento
- **GlobalRequest**: Requisição para serviço de dados cadastrais
- **StatusMovimentacaoPix**: Status de fraude e processamento PIX retornado pelo PPBD

**Relacionamentos:**
- Payment → PaymentStatus (1:1) - cada pagamento gera um status
- Payment → EfetTransPixRequest (1:1) - pagamento é convertido em requisição de efetivação
- PaymentEvent → StatusPaymentEvent (1:1) - evento de entrada gera evento de status de saída

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `application.yml` | leitura | Spring Boot | Configurações da aplicação (profiles, URLs, credenciais) |
| `logback-spring.xml` | leitura | Logback | Configuração de logs (formato JSON, níveis, appenders) |
| `*.yaml` (Swagger) | leitura | Swagger Codegen | Especificações OpenAPI para geração de clientes e contratos |
| `rabbitmq_definitions.json` | leitura | RabbitMQ | Definições de filas, exchanges e bindings |
| `*.sample` (RabbitMQ) | leitura | Desenvolvimento | Exemplos de mensagens para testes locais |

---

## 10. Filas Lidas

- `events.business.OPEN-CONS.BDIGITAL-PF.envioPagamentoPix` - Consome ordens de pagamento/agendamento PIX de pessoa física do canal digital
- `events.business.OPEN-CONS.BDIGITAL-PJ.envioPagamentoPix` - Consome ordens de pagamento/agendamento PIX de pessoa jurídica do canal digital
- `events.business.OPEN-CONS.IB-PRIVATE.envioPagamentoPix` - Consome ordens de pagamento PIX do Internet Banking Private
- `events.business.OPEN-CONS.IB-ATACADO.envioPagamentoPix` - Consome ordens de pagamento PIX do Internet Banking Atacado

---

## 11. Filas Geradas

- `events.business.statusPagamento` (exchange fanout) - Publica eventos de atualização de status de pagamentos
- `events.business.envioPagamentoDLQ` (exchange fanout) - Publica mensagens com erro para reprocessamento (Dead Letter Queue)
- `events.business.envioPagamentoPLQ` (exchange fanout) - Publica mensagens que esgotaram tentativas de reprocessamento (Parking Lot Queue)

---

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| `sboot-ccbd-base-orch-efet-transf-pix` | REST API | Serviço de efetivação de transferências PIX (v4) |
| `sboot-glob-base-atom-cliente-dados-cadastrais` | REST API | Serviço de consulta de dados cadastrais de clientes (contas, bancos) |
| `sboot-ccbd-base-atom-cancel-agend` | REST API | Serviço de cancelamento de agendamentos PIX |
| `sboot-ppbd-pixx-atom-pix-movimentacoes` | REST API | Serviço de consulta de status de movimentações PIX |
| RabbitMQ | Message Broker | Consumo e publicação de eventos de pagamento |
| Gateway OAuth | OAuth2 | Autenticação para chamadas a APIs internas |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com módulos `common`, `domain` e `application`
- Uso adequado de padrões de projeto (Chain of Responsibility para validações, Repository para integrações)
- Implementação robusta de tratamento de erros e retry com DLQ/PLQ
- Uso de Apache Camel para orquestração de fluxos complexos
- Mapeamento claro de erros internos para códigos Open Banking
- Configuração adequada de métricas e observabilidade (Prometheus/Grafana)
- Testes unitários presentes

**Pontos de Melhoria:**
- Algumas classes com responsabilidades múltiplas (ex: `OpenBankingEfetPagamentoRouter` com lógica de negócio e roteamento)
- Uso excessivo de `Optional` em alguns mappers pode dificultar leitura
- Falta de documentação JavaDoc em classes críticas
- Alguns métodos longos que poderiam ser refatorados (ex: `paraEfetivarTransfPixRequest`)
- Configurações hardcoded em algumas classes (ex: `MAX_PAYMENT_STATUS_POLLS = 50`)
- Falta de testes de integração mais abrangentes
- Alguns nomes de variáveis poderiam ser mais descritivos (ex: `efetReq`)

---

## 14. Observações Relevantes

1. **Arquitetura Event-Driven**: Sistema fortemente baseado em eventos assíncronos via RabbitMQ, com tratamento robusto de falhas
2. **Polling Inteligente**: Implementa mecanismo de polling com limite de tentativas e delay configurável para consulta de status de transações imediatas
3. **Versionamento de API**: Suporta múltiplas versões da API Open Banking (V1 e V2) com mapeamento diferenciado de erros
4. **Jornada Sem Redirecionamento (JSR)**: Suporta fluxo específico do Open Finance para transações sem redirecionamento
5. **Configuração por Ambiente**: Utiliza profiles Spring (local, des, uat, prd) com configurações específicas por ambiente
6. **Observabilidade**: Integração completa com Prometheus/Grafana para monitoramento de métricas de negócio e técnicas
7. **Segurança**: Autenticação OAuth2 para todas as chamadas a APIs internas via Gateway
8. **Resiliência**: Implementa circuit breaker implícito através de retry e DLQ, com publicação em PLQ após esgotamento de tentativas
9. **Rastreabilidade**: Uso de EndToEndId único para rastreamento de transações fim-a-fim
10. **Docker/Kubernetes Ready**: Configuração completa para deploy em OpenShift/Kubernetes com health checks e métricas