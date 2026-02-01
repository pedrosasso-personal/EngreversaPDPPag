---
## Ficha Técnica do Sistema

### 1. Descrição Geral
Sistema de orquestração e integração de dados PLD (Prevenção à Lavagem de Dinheiro) que atua como middleware entre sistemas parceiros e as APIs Atom (PLD e OPF). Recebe eventos de transações e cadastros via REST, transforma os dados conforme regras de negócio complexas, enriquece informações consultando APIs externas e publica em filas GCP PubSub. Utiliza Apache Camel para roteamento de mensagens e implementa feature toggles para controle de fluxo. O sistema é stateless, não mantém banco de dados próprio, atuando exclusivamente como orquestrador e transformador de dados.

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **PldServiceController** | Controller REST que expõe endpoints v1/transactional e v1/registration (POST/GET). Recebe eventos, converte para array JSON e delega para services. |
| **TransacionalService** | Orquestra processamento de eventos transacionais, invocando rota Camel TRANSACIONAL para salvar dados via repositórios. |
| **RegistrationService** | Orquestra processamento de eventos cadastrais, invocando rotas Camel REGISTRATION e ACCOUNTS para persistir dados. |
| **OpfRepositoryImpl** | Integra com APIs OPF (cartões, contratos, transações, faturas). Mapeia eventos para entidades OPF e publica no PubSub cadastro. |
| **PubSubRepositoryImpl** | Publica mensagens nos tópicos GCP PubSub (transacional, cadastro, ingestão parceiro) com filtros e feature toggles. |
| **RegistrationRepositoryImpl** | Publica dados cadastrais via PubSub e consulta API PLD para obter registros por documento/período. |
| **TransacionalRepositoryImpl** | Publica dados transacionais via PubSub e consulta API PLD para obter transações por credor/devedor. |
| **TransactionOpfRepositoryImpl** | Consulta dados OPF (OpfInfo, Account, Registration) via APIs externas para enriquecimento. |
| **OPFMapper** | Mapper complexo que converte EventData em múltiplos DTOs OPF (cartões, contratos, transações, faturas). Implementa lógicas isSendEvent, isGetEvent, isTempEvent. |
| **RegistrationAndTransacionalMapper** | Converte EventData em TransactionalDataRequest/RegistrationDataRequest. Define tipos de evento (TED, BOLETO, AUTORIZACAO). |
| **CreditCardMapper** | Mapeia JSON para RequestCreditCard, identifica múltiplos cartões e define CNPJ empresa por banco. |
| **CreditTransactionMapper** | Converte JSON para RequestCreditTransaction, classificando tipos (ESTORNO, TARIFA, CASHBACK, PAGAMENTO). |
| **RequestCreditCardBillMapper** | Mapeia JSON para RequestCreditCardBill e payments (cash, partial, installment). |
| **JsonHandler** | Utilitário para navegação JSON com dot notation, casting de tipos (Boolean→SIM/NAO, BigDecimal, datas) e fallbacks. |
| **MapperConfigs** | Centraliza configurações de mapeamento: conversões de tipo, valores default e formatos de data. |
| **PldServiceRouter** | Define rotas Apache Camel (transacionalRegister, registration, registrationAccounts) com tratamento de exceções. |
| **CamelContextWrapper** | Wrapper que inicializa contexto Camel com rotas e cria ProducerTemplate/ConsumerTemplate. |
| **HashGenerator** | Gera hash SHA3-256 único para AccountData (compeCode+branchCode+number). |
| **ExceptionHandlerConfig** | ControllerAdvice que trata exceções globalmente, retornando ResponseRepresentation padronizada. |
| **FeatureToggleService** | Gerencia flags de feature toggle (ft_pld_transacional_pubsub, ft_pld_registration_pubsub). |

### 3. Tecnologias Utilizadas
- **Framework:** Spring Boot 2.x
- **Integração:** Apache Camel 3.22.4
- **Linguagem:** Java 11
- **Serialização:** Jackson (ObjectMapper com JSR310, NON_NULL)
- **JSON:** org.json (JSONObject parsing)
- **Mensageria:** Google Cloud PubSub (spring-cloud-gcp-starter-pubsub)
- **HTTP Client:** RestTemplate (Spring)
- **Documentação API:** Swagger 2 (Springfox Docket)
- **Segurança:** OAuth2 Resource Server (JWT via jwks endpoint)
- **Feature Flags:** ConfigCat
- **Testes:** JUnit 5, Mockito, Rest-Assured
- **Build:** Maven (multi-module)
- **Monitoramento:** Spring Actuator (health endpoint)
- **Geração Clientes API:** Swagger Codegen

### 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/transactional | PldServiceController | Recebe eventos transacionais (header eventName), processa e salva via Camel route TRANSACIONAL |
| GET | /v1/transactional | PldServiceController | Consulta dados transacionais por documento credor/devedor, período (startDate, endDate, pageSize, pageNumber) |
| POST | /v1/registration | PldServiceController | Recebe eventos cadastrais (header eventName), processa e salva via Camel routes REGISTRATION/ACCOUNTS |
| GET | /v1/registration | PldServiceController | Consulta dados cadastrais por documento e período (startDate, endDate, pageSize, pageNumber) |

### 5. Principais Regras de Negócio
- **Orquestração de Eventos PLD:** Transforma eventos de parceiros (CARD_WAS_ISSUED, TRANSACTION_CREATED, CUSTOMER_WAS_APPROVED, INVOICE_CLOSED, etc.) em chamadas para APIs Atom PLD/OPF.
- **Validação de Eventos:** Filtra eventos válidos através de `isSendEvent`, marca eventos temporários via `isTempEvent` e enriquece dados com busca prévia usando `isGetEvent`.
- **Merge de Dados:** Atualiza faturas com pagamentos (evento INVOICE_PAYMENT_PROCESSED) e busca account/registration para completar informações de transações.
- **Classificação de Transações:** Define tipo de evento (TED, BOLETO, PAGAMENTO_CONTA, AUTORIZACAO), creditDebitType, paymentType (A_VISTA/A_PRAZO) e flag sendToAtom baseado em função (Pos/Debit).
- **Hash de Conta:** Gera identificador único SHA3-256 concatenando compeCode+branchCode+number (zero-padded).
- **Feature Toggle:** Controla envio para PubSub transacional/cadastro através de flags configuráveis (ft_pld_transacional_pubsub, ft_pld_registration_pubsub).
- **Mapeamento de Bancos:** Define CNPJ da empresa baseado em bank.code (332→13140088000199, 655→59588111000103, 413→01858774000110).
- **Validação de Envio Atom:** Verifica código de entidade (413 ou 01858774) para determinar se deve enviar para Atom.
- **Identificação de Múltiplos Cartões:** Calcula flag isMultipleCreditCard baseado em functionalities (lotpre/lotpos).
- **Classificação de Tipos de Transação:** Mapeia transactionType para categorias (ESTORNO, TARIFA, CASHBACK, PAGAMENTO, OUTROS).
- **Validação de Débito Aprovado:** Verifica se transação é débito com status SUCCESS (isApprovedDebit).
- **Conversões de Tipo Complexas:** Aplica castings customizados (Boolean→SIM/NAO, BigDecimal, timestamps, enums, substrings) com fallbacks e valores default.

### 6. Relação entre Entidades
**Modelo de Domínio Principal:**

- **EventData** (entrada): contém metadata, data (JSON estruturado), eventName
  - Transformado por mappers em múltiplos DTOs de saída

**Domínio Transacional:**
- **TransactionalDataRequest**: contém debtor, creditor, transaction, account, registration
  - **DebtorData/CreditorData**: document, name, account
  - **Transaction**: amount, type, date, status
  - **Account**: compeCode, branchCode, number, accountType
  - **Registration**: personalIdentification, address, contact

**Domínio Cadastral:**
- **RegistrationDataRequest**: personalIdentification, business, address, contact, licenses
  - **BusinessData** (PJ): cnpj, companyName, owners, legalRepresentatives
  - **Owner/LegalRepresentative**: document, name, qualification

**Domínio OPF:**
- **OpfInfo**: account, registration, creditCards, creditContracts, creditTransactions, creditCardBills
  - **RequestCreditCard**: holder, contract, program, card, functionalities
  - **RequestCreditContract**: contract, credit, program, holder
  - **RequestCreditTransaction**: transactionId, amounts, fees, billId, MCC
  - **RequestCreditCardBill**: billId, contract, dueDate, balance, payments

**Relacionamentos:**
- EventData → (OPFMapper) → OpfInfo (1:N com cards/contracts/transactions/bills)
- EventData → (RegistrationAndTransacionalMapper) → TransactionalDataRequest/RegistrationDataRequest
- OpfInfo referencia Account e Registration (enriquecidos via TransactionOpfRepository)
- RequestCreditCardBill contém List<RequestCreditCardBillUpdate> (payments)

### 7. Estruturas de Banco de Dados Lidas
não se aplica

### 8. Estruturas de Banco de Dados Atualizadas
não se aplica

### 9. Arquivos Lidos e Gravados
não se aplica

### 10. Filas Lidas
não se aplica

### 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Responsável | Descrição |
|--------------|------------|-------------------|-----------|
| business-spag-base-pldtransactional | GCP PubSub | PubSubRepositoryImpl | Publica eventos de transações PLD com filtros (entityId, companyKey). Controlado por feature toggle ft_pld_transacional_pubsub. |
| business-spag-base-pldregistration | GCP PubSub | PubSubRepositoryImpl | Publica eventos de cadastro PLD com filtros (entityId, companyKey). Controlado por feature toggle ft_pld_registration_pubsub. |
| business-spag-base-ingestao-dados-parceiro | GCP PubSub | PubSubRepositoryImpl | Publica dados de ingestão de parceiros com atributos de filtro. |

### 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| **sboot-spag-base-atom-pld-service** | API REST | API PLD Atom. Endpoints: POST/GET /transactionalData, POST/GET /registrationData. Utilizada para consultar e persistir dados transacionais e cadastrais. Cliente: PldServiceControllerApi. |
| **sboot-spag-base-atom-opf-service** | API REST | API OPF Atom. Endpoints para CRUD de cartões, contratos, transações, faturas, contas e clientes. Clientes: OpfServiceControlerApi, CreditCardsApi, CreditContractsApi, CreditBillsApi, CreditTransactionsApi, AccountsApi, CustomerApi. |
| **Google Cloud PubSub** | Mensageria | Plataforma de mensageria para publicação assíncrona de eventos PLD (transacional, cadastro, ingestão parceiro). Utiliza JacksonPubSubMessageConverter. |
| **ConfigCat** | Feature Toggle | Serviço de gerenciamento de feature flags para controlar fluxos de publicação PubSub. |
| **API Gateway OAuth2** | Segurança | Validação de tokens JWT via jwks endpoint. Sistema configurado como Resource Server. |

### 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Excelente separação de responsabilidades em camadas (controller, service, repository, mapper)
- Cobertura de testes unitários extensiva e bem estruturada (todos os componentes principais testados)
- Tratamento de exceções centralizado e padronizado (ExceptionHandlerConfig)
- Uso adequado de DTOs para contratos de API
- Implementação de feature toggles para controle de fluxo
- Boa utilização de padrões (Repository, Mapper, Wrapper)
- Configuração externalizada via properties

**Pontos a Melhorar:**
- **Classes mapper excessivamente grandes:** OPFMapper com 44KB contém lógica muito complexa e múltiplas responsabilidades, violando Single Responsibility Principle
- **Lógica de mapeamento complexa:** Muitos ifs aninhados e condicionais baseadas em eventType dificultam manutenção e compreensão
- **Documentação insuficiente:** Comentários escassos no código, especialmente em lógicas de negócio complexas
- **Forte acoplamento com estruturas JSON:** Dependência direta de estruturas JSON de parceiros torna sistema frágil a mudanças
- **Falta de validações explícitas:** Ausência de validações de entrada robustas (Bean Validation)
- **Métodos muito longos:** Alguns métodos de mapeamento ultrapassam 100 linhas
- **Magic numbers e strings:** Códigos hardcoded (332, 655, 413, "lotpre", "lotpos") deveriam ser constantes

**Recomendações:**
1. Refatorar OPFMapper em múltiplos mappers especializados por tipo de entidade
2. Extrair lógicas condicionais complexas para Strategy Pattern ou Chain of Responsibility
3. Adicionar JavaDoc em métodos públicos e lógicas de negócio não triviais
4. Implementar camada de validação com Bean Validation (JSR-303)
5. Criar constantes para valores mágicos e enums para tipos de evento
6. Considerar uso de bibliotecas de mapeamento como MapStruct para reduzir código boilerplate

### 14. Observações Relevantes

1. **Arquitetura Stateless:** O sistema não mantém estado próprio, atuando exclusivamente como orquestrador entre sistemas externos. Toda persistência é delegada para APIs Atom.

2. **Processamento Assíncrono:** Utiliza Apache Camel para roteamento de mensagens, permitindo processamento desacoplado e resiliente com tratamento de exceções.

3. **Enriquecimento de Dados:** Implementa lógica sofisticada de busca prévia (isGetEvent) para enriquecer eventos com dados de account/registration antes de persistir.

4. **Flexibilidade de Configuração:** Feature toggles permitem habilitar/desabilitar publicação PubSub sem necessidade de deploy, facilitando rollout gradual e rollback.

5. **Conversões Complexas de Tipo:** JsonHandler implementa sistema flexível de casting com fallbacks, concatenação e valores default, permitindo adaptação a variações nas estruturas JSON de entrada.

6. **Merge de Dados de Fatura:** Lógica específica para evento INVOICE_PAYMENT_PROCESSED que mescla informações de pagamento com faturas existentes.

7. **Múltiplos Formatos de Data:** MapperConfigs suporta parsing de múltiplos formatos de data (yyyy-MM-dd'T'HH:mm:ss.SSS'Z', yyyy-MM-dd, etc.) para compatibilidade com diferentes parceiros.

8. **Classificação Inteligente de Transações:** Lógica que determina tipo de transação (ESTORNO, TARIFA, CASHBACK, PAGAMENTO, OUTROS) baseada em múltiplos atributos do evento.

9. **Segurança:** Sistema protegido por OAuth2 Resource Server, validando tokens JWT em todas as requisições.

10. **Observabilidade:** Integração com Spring Actuator para health checks e monitoramento.

11. **Testes Abrangentes:** Cobertura de testes inclui cenários de sucesso, falha, null handling e validações de exceções, demonstrando preocupação com qualidade.

12. **Dependência de APIs Externas:** Sistema altamente dependente de disponibilidade das APIs Atom PLD/OPF. Falhas nessas integrações impactam diretamente o funcionamento.

---