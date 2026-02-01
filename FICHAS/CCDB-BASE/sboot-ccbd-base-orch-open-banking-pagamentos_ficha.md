# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema orquestrador de consultas e gestão de pagamentos e agendamentos Open Banking, responsável por:
- Consultar pagamentos e agendamentos PIX via Open Banking
- Enriquecer dados de transações com informações de instituições financeiras, QR Codes e marcas
- Processar eventos do ciclo de vida de consentimentos e pagamentos
- Validar titularidade de contas
- Persistir registros de transações no atomico de extrato Open Banking

O sistema atua como camada de orquestração entre APIs externas, filas de eventos (GCP Pub/Sub e RabbitMQ) e o serviço de extrato de pagamentos, aplicando regras de negócio, enriquecimento de dados e tratamento de resiliência.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **OpenBankingPaymentsController** | Controlador REST que expõe endpoints de consulta de pagamentos (lista paginada e detalhes) |
| **OpenBankingPaymentsService** | Serviço principal que orquestra chamadas às rotas Camel para operações de pagamento |
| **OpenBankingPaymentsRouter** | Roteador Apache Camel que define fluxos de orquestração (getPayments, getPayment, createRegistry, updateTransaction, etc) |
| **ConsentEventsSubscriber** | Subscriber GCP Pub/Sub que processa eventos de consentimento (AUTHORISED, REJECTED, REJECTED_60MIN) |
| **PaymentEventsSubscriber** | Subscriber GCP Pub/Sub que processa eventos de pagamento (CANC) |
| **ConsentAuthorizedSubscriber** | Subscriber GCP Pub/Sub (deprecated) que cria registros de transação ao autorizar consentimento |
| **OpenBankingPaymentsRepositoryImpl** | Implementação de repositório que realiza CRUD de transações via StatementsApi |
| **BancosRepositoryImpl** | Consulta nome de banco por ISPB via API externa |
| **MarcaRepositoryImpl** | Busca nome de marca por UUID via API de participantes |
| **QrcodeRepositoryImpl** | Consulta detalhes de QR Code via API externa |
| **ClienteDadosCadastraisRepositoryImpl** | Valida titularidade de conta comparando CPF/CNPJ do consentimento com dados cadastrais |
| **StatementMapper** | Mapeia entidades de domínio para representações REST (PaymentsPaged, PaymentDetail, etc) |
| **EventsMapper** | Mapeia eventos de consentimento e pagamento para eventos de transação (MapStruct) |
| **ResourceExceptionHandler** | Handler global de exceções que converte erros em representações padronizadas |

---

## 3. Tecnologias Utilizadas

- **Framework:** Spring Boot 2.x
- **Linguagem:** Java 11
- **Orquestração:** Apache Camel 3.0.1
- **Resiliência:** Resilience4j 1.7.1 (Circuit Breaker, Retry)
- **Mapeamento:** MapStruct 1.5.5, Lombok
- **Mensageria:** GCP Pub/Sub 1.2.8, RabbitMQ (Spring AMQP)
- **Segurança:** Spring Security OAuth2 Resource Server, JWT 0.22.1
- **Documentação:** Swagger/OpenAPI 3.0
- **Serialização:** Jackson (JSON)
- **Build:** Maven 3.3+
- **Containerização:** Docker
- **Monitoramento:** Spring Actuator, Prometheus, Grafana
- **Testes:** JUnit, ArchUnit 0.19.0
- **Bibliotecas Internas:** 
  - sbootlib-open-cons-pagamento-eventos-contrato 0.0.41
  - springboot-arqt-base-trilha-auditoria-web
  - springboot-arqt-base-trilha-rabbitmq 0.1.0
  - sboot-arqt-base-microservices-error 0.14.1

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/.../pagamentos` | OpenBankingPaymentsController | Lista paginada de pagamentos com filtros (data inicial/final, status, fluxo detentora/iniciadora, consentId) |
| GET | `/v1/.../pagamentos/detalhe` | OpenBankingPaymentsController | Detalhe de pagamento específico por consentId e índice de pagamento |

**Observação:** Endpoints protegidos por OAuth2 Bearer Token (Spring Security Resource Server).

---

## 5. Principais Regras de Negócio

1. **Validação de Titularidade:** Verifica se o CPF/CNPJ do consentimento corresponde ao titular da conta debitada, lançando exceção em caso de divergência.

2. **Enriquecimento de Dados:**
   - Consulta nome da instituição financeira credora por ISPB
   - Consulta nome da marca devedora (uuidMarca/uuidParticipante)
   - Consulta detalhes de QR Code (estático/dinâmico) quando aplicável (QRDN, QRES)

3. **Filtros de Extrato:**
   - Por período (data inicial/final)
   - Por status (TODOS, CONCLUIDO, AGENDADO, SOLICITADO, EM_PROCESSAMENTO, PENDENTE, NAO_CONCLUIDO, CANCELADO_PELO_USUARIO, AGENDAMENTO_CANCELADO)
   - Por fluxo (DETENTORA, INICIADORA)
   - Por consentId

4. **Mapeamento de Status Open Banking:**
   - Status de pagamento: PDNG, SASP, SASC, PART, ACSP, ACSC, ACCC, RJCT
   - Status de consentimento: AUTHORISED, AWAITING_AUTHORISATION, CONSUMED, REJECTED (5min), REJECTED (60min)

5. **Tratamento de Agendamentos Recorrentes:**
   - Suporte a scheduleRecurring: single, daily, weekly, monthly, custom
   - Controle de índice de pagamento recorrente (recurringPaymentIndex/Total)

6. **Processamento de Eventos:**
   - **Consentimento AUTHORISED:** Cria registro de transação (com validação de iniciadora BV em ambientes não-produtivos)
   - **Consentimento REJECTED/REJECTED_60MIN:** Atualiza status da transação
   - **Pagamento CANC:** Atualiza transação com status de cancelamento e instituição canceladora

7. **Cálculo de Instituição Canceladora:**
   - Baseado no fluxo (detentora/iniciadora) e origem do cancelamento (cancelledFrom)

8. **Anonimização de Documentos:**
   - CPF/CNPJ são mascarados nas respostas REST

9. **Resiliência:**
   - Circuit Breaker e Retry em chamadas externas
   - Fallbacks: retorno de string vazia (bancos, marca), null (QRCode), exceção controlada (transações)

10. **Validação de Perfil:**
    - Em ambientes UAT/DES, valida se iniciadora é BV (ISPB 01858774 ou 59588111)

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **PaymentDetail:** Entidade central representando um pagamento/agendamento
  - Contém: consentId, paymentId, endToEndId, status, datas, valores, debtor, creditor, pixDetails, scheduleRecurring, qrCodePaymentDetail, etc.
  
- **Debtor (Devedor):**
  - Atributos: ispb, issuer, number, accountType
  - Relacionamento: 1 PaymentDetail possui 1 Debtor

- **Creditor (Credor):**
  - Atributos: ispb, issuer, number, accountType, document, name, personType
  - Relacionamento: 1 PaymentDetail possui 1 Creditor

- **QrCodePaymentDetail:**
  - Atributos: paymentInterest, paymentFine, discount, identifier, originalValue, product, expiration, debtorName, qrCode
  - Relacionamento: 1 PaymentDetail pode ter 0..1 QrCodePaymentDetail (quando iniciação é QRDN ou QRES)

- **ScheduleRecurring:**
  - Subtipos: ScheduleSingle, ScheduleDaily, ScheduleWeekly, ScheduleMonthly, ScheduleCustom
  - Relacionamento: 1 PaymentDetail pode ter 0..1 ScheduleRecurring

- **Transaction (Evento):**
  - Contém: creditor, debtor, transactionDetails
  - Usado em eventos de criação/atualização

- **ConsentEvent, PaymentEvent, UpdateTransactionEvent:**
  - Eventos de domínio que disparam atualizações de transações

**Relacionamentos:**
```
PaymentDetail 1---1 Debtor
PaymentDetail 1---1 Creditor
PaymentDetail 1---0..1 QrCodePaymentDetail
PaymentDetail 1---0..1 ScheduleRecurring
PaymentsPaged 1---* Payment (lista paginada)
```

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| Transações (via StatementsApi) | Tabela/Coleção | SELECT/READ | Consulta de pagamentos e agendamentos Open Banking (getPayments, getPayment) |

**Observação:** O acesso ao banco de dados é indireto, via API REST (sboot-open-cons-atom-extrato-pagamento). Não há acesso direto a tabelas/views.

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| Transações (via StatementsApi) | Tabela/Coleção | INSERT | Criação de registro de transação ao autorizar consentimento (createTransactionRegistry) |
| Transações (via StatementsApi) | Tabela/Coleção | UPDATE | Atualização de status de transação por eventos de consentimento/pagamento (updateTransactionRegistry) |

**Observação:** O acesso ao banco de dados é indireto, via API REST (sboot-open-cons-atom-extrato-pagamento). Não há acesso direto a tabelas/views.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | Leitura | Volume Kubernetes | Configuração de logs estruturados |
| application.yml / infra.yml | Leitura | Spring Boot | Configurações de propriedades da aplicação |

**Observação:** Não há processamento batch de arquivos. Logs são gerenciados pelo framework de logging (Logback).

---

## 10. Filas Lidas

**GCP Pub/Sub:**

| Nome da Fila/Subscription | Tópico | Classe Responsável | Descrição |
|---------------------------|--------|-------------------|-----------|
| business-open-base-iniciacaopagamento-consentimento-autorizado-meuspagamentos-sub | business-open-base-iniciacaopagamento-consentimento-autorizado | ConsentAuthorizedSubscriber (deprecated) | Eventos de consentimento autorizado (ConsentApprovedEvent) |
| business-open-base-consentimento-pagamento-meuspagamentos-sub | business-open-base-consentimento-pagamento | ConsentEventsSubscriber | Eventos de consentimento (AUTHORISED, REJECTED, REJECTED_60MIN) |
| business-open-base-pagamento-meuspagamentos-sub | business-open-base-pagamento | PaymentEventsSubscriber | Eventos de pagamento (CANC) |

**RabbitMQ (Deprecated):**

| Nome da Fila | Classe Responsável | Descrição |
|--------------|-------------------|-----------|
| events.business.OPEN-CONS.statusMeusPagamentos | StatusMeusPagamentosListener (deprecated) | Eventos de status de pagamento (StatusPaymentEvent) |
| events.business.OPEN-CONS.envioPagamentoPixExtrato | TransactionOrderListener (deprecated) | Eventos de envio de pagamento PIX (PaymentEvent) - listener vazio |
| events.business.OPEN-CONS.statusPagamentoExtrato | TransactionUpdatedListener (deprecated) | Eventos de atualização de status de pagamento (StatusPaymentEvent) |

---

## 11. Filas Geradas

**Não se aplica.** O sistema não publica mensagens em filas. Apenas consome eventos de GCP Pub/Sub e RabbitMQ.

---

## 12. Integrações Externas

| Sistema Externo | Tipo | Classe/Componente | Descrição |
|-----------------|------|-------------------|-----------|
| sboot-ccbd-base-orch-pix-qr-code | API REST | QrcodeRepositoryImpl, ConsultarQrCodeApi | Consulta detalhes de QR Code PIX (estático/dinâmico) |
| sboot-glob-base-atom-lista-bancos | API REST | BancosRepositoryImpl, ConsultarBancosIspbApi | Consulta nome de instituição financeira por ISPB |
| sboot-glob-base-atom-cliente-dados-cadastrais | API REST | ClienteDadosCadastraisRepositoryImpl, GetContasByNuContaApi | Validação de titularidade de conta (CPF/CNPJ vs conta) |
| sboot-open-cons-atom-extrato-pagamento (v2) | API REST | OpenBankingPaymentsRepositoryImpl, StatementsApi | CRUD de transações de pagamento Open Banking |
| sboot-open-base-orch-participantes | API REST | MarcaRepositoryImpl, ParticipanteControllerApi | Consulta nome de marca por UUID |
| API Gateway OAuth2 | OAuth2 | GatewayOAuthService | Obtenção de token de acesso para chamadas autenticadas |
| GCP Pub/Sub | Mensageria | ConsentEventsSubscriber, PaymentEventsSubscriber, ConsentAuthorizedSubscriber | Consumo de eventos de consentimento e pagamento |
| RabbitMQ | Mensageria (deprecated) | StatusMeusPagamentosListener, TransactionOrderListener, TransactionUpdatedListener | Consumo de eventos legados de pagamento |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- **Arquitetura Limpa:** Separação clara de responsabilidades com padrão Ports & Adapters (hexagonal), módulos domain, application e common bem definidos
- **Resiliência:** Uso adequado de Circuit Breaker e Retry (Resilience4j) em integrações externas com fallbacks apropriados
- **Mapeamento Automatizado:** Uso de MapStruct reduz código boilerplate e erros de mapeamento manual
- **Documentação:** OpenAPI 3.0 bem configurado, README detalhado
- **Segurança:** Implementação de OAuth2 Resource Server, anonimização de dados sensíveis
- **Orquestração:** Apache Camel bem utilizado para fluxos complexos de integração
- **Tratamento de Exceções:** Handler global centralizado com conversão de charset
- **Logs Estruturados:** Uso de constantes para chaves de log, facilitando rastreabilidade
- **Testes:** Estrutura de profiles para testes unitários, integração, funcionais e arquiteturais (ArchUnit)

**Pontos de Melhoria:**
- **Código Deprecated:** Presença de listeners RabbitMQ marcados como deprecated indica migração incompleta para GCP Pub/Sub
- **Lógica de Negócio em Mappers:** Alguns mappers (EventsMapper, StatementMapper) contêm lógica de negócio que poderia estar em serviços dedicados
- **Validação de Perfil Hardcoded:** Validação de iniciadora BV em ambientes não-produtivos está hardcoded (ISPBs fixos)
- **Complexidade de PaymentDetail:** Classe de domínio com muitos atributos (>20), poderia ser refatorada em agregados menores
- **Falta de Testes Evidentes:** Não foram fornecidos arquivos de teste no resumo, dificultando avaliar cobertura
- **Documentação de Código:** Falta de JavaDoc em classes e métodos principais

---

## 14. Observações Relevantes

1. **Migração em Andamento:** O sistema está em processo de migração de RabbitMQ para GCP Pub/Sub. Listeners RabbitMQ estão marcados como `@Deprecated`, mas ainda presentes no código.

2. **Workload Identity GCP:** Utiliza service account `ksa-ccbd-base-19202` para autenticação no GCP Pub/Sub, seguindo boas práticas de segurança cloud-native.

3. **Ambientes Específicos:** Lógica diferenciada entre ambientes produtivos (prd) e não-produtivos (uat/des), especialmente na validação de iniciadora BV.

4. **Manual ACK/NACK:** Subscribers GCP Pub/Sub utilizam acknowledgment manual, garantindo controle fino sobre processamento de mensagens.

5. **Resiliência Configurável:** Circuit Breaker e Retry configurados via Resilience4j, permitindo ajustes de thresholds e timeouts.

6. **Swagger Codegen:** Uso extensivo de geração de código a partir de especificações OpenAPI para clientes de APIs externas, reduzindo manutenção manual.

7. **Monitoramento:** Dashboards Grafana pré-configurados para métricas JVM, HTTP, HikariCP, GC, CPU e memória, facilitando observabilidade.

8. **Recursos Kubernetes:** Configuração de resources (cpu: 100m-750m, memory: 512Mi-750Mi) e probes (liveness/readiness) adequadas para ambiente produtivo.

9. **Token Budget:** Sistema projetado para lidar com alto volume de tokens (budget: 200.000), adequado para processamento de eventos em larga escala.

10. **Charset Handling:** Tratamento específico de conversão ISO-8859-1 para UTF-8 em respostas de erro, indicando integração com sistemas legados.

11. **Enriquecimento Assíncrono:** Uso de Apache Camel permite enriquecimento paralelo de dados (bancos, marcas, QR Codes) de forma eficiente.

12. **Versionamento de API:** Endpoints REST versionados (`/v1/...`), facilitando evolução da API sem quebrar contratos.

---

**Documento gerado em:** 2024  
**Versão do Sistema:** 1.1.0  
**Tecnologia Base:** Spring Boot 2.x + Apache Camel 3.0.1 + GCP Pub/Sub 1.2.8