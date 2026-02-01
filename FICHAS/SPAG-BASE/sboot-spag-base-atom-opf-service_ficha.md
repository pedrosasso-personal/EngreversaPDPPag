```markdown
## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um serviço atômico desenvolvido em Java com Spring Boot, destinado a gerenciar dados de transações financeiras e informações de contas e clientes. Ele utiliza o Firestore como banco de dados e oferece uma API REST para operações de CRUD e consultas relacionadas a transações, contas, contratos de crédito, cartões de crédito e registros de clientes.

### 2. Principais Classes e Responsabilidades
- **Application**: Classe principal que inicia a aplicação Spring Boot.
- **OpfServiceApiDelegateImpl**: Implementa a lógica dos endpoints da API REST, lidando com transações, contas, contratos de crédito, cartões de crédito e registros de clientes.
- **OpfServiceService**: Serviço principal que coordena operações de transações e registros.
- **TransactionService**: Gerencia operações relacionadas a transações financeiras.
- **AccountRepositoryImpl**: Implementação do repositório para operações de conta no Firestore.
- **CreditCardService**: Serviço para operações de cartões de crédito.
- **CreditContractService**: Serviço para operações de contratos de crédito.
- **BusinessService**: Serviço para operações de registros de negócios.
- **FeatureToggleService**: Gerencia configurações de feature toggle.
- **JdbiConfiguration**: Configura o Jdbi para integração com o banco de dados.
- **OpfExceptionHandler**: Lida com exceções de validação de argumentos de método.

### 3. Tecnologias Utilizadas
- Java 11+
- Spring Boot
- Firestore
- Jdbi
- Maven
- Swagger
- H2 Database (para testes locais)
- Microsoft SQL Server JDBC Driver

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST   | /v1/business | OpfServiceApiDelegateImpl | Registra dados de negócios. |
| GET    | /v1/business/{cnpjNumber} | OpfServiceApiDelegateImpl | Obtém dados de registro de negócios por CNPJ. |
| POST   | /v1/opf-info | OpfServiceApiDelegateImpl | Registra dados transacionais. |
| GET    | /v1/opf-info/{transactionId} | OpfServiceApiDelegateImpl | Obtém informações temporárias de transações por ID. |
| POST   | /v1/transactions-spag | OpfServiceApiDelegateImpl | Obtém dados de transações do SPAG. |
| GET    | /v1/accounts | OpfServiceApiDelegateImpl | Obtém lista de contas consentidas pelo cliente. |
| GET    | /v1/accounts/{accountId} | OpfServiceApiDelegateImpl | Obtém dados de identificação da conta por ID. |
| GET    | /v1/{accountId}/transactions | OpfServiceApiDelegateImpl | Obtém lista de transações da conta por ID. |
| POST   | /v1/customer | OpfServiceApiDelegateImpl | Registra dados de identificação do cliente. |
| GET    | /v1/customer/{personalId} | OpfServiceApiDelegateImpl | Obtém dados do cliente por ID. |
| POST   | /v1/credit/contract | OpfServiceApiDelegateImpl | Registra contrato de crédito. |
| POST   | /v1/credit/card | OpfServiceApiDelegateImpl | Registra cartão de crédito. |
| GET    | /v1/card | OpfServiceApiDelegateImpl | Obtém lista de cartões de crédito. |
| GET    | /v1/card/{proxy} | OpfServiceApiDelegateImpl | Obtém cartão de crédito por proxy. |
| POST   | /v1/credit/{creditCardAccountId}/transactions | OpfServiceApiDelegateImpl | Registra transações de cartão de crédito. |
| GET    | /v1/card/{creditCardAccountId}/transactions | OpfServiceApiDelegateImpl | Obtém transações de cartão de crédito paginadas. |
| GET    | /v1/card/{creditCardAccountId}/bills/{billId}/transactions | OpfServiceApiDelegateImpl | Obtém transações de fatura de cartão de crédito paginadas. |
| POST   | /v1/credit/bills | OpfServiceApiDelegateImpl | Registra fatura de cartão de crédito. |
| GET    | /v1/card/{creditCardAccountId}/bills | OpfServiceApiDelegateImpl | Obtém faturas de cartão de crédito paginadas. |
| GET    | /v1/bills/{billId} | OpfServiceApiDelegateImpl | Obtém fatura de cartão de crédito por ID. |

### 5. Principais Regras de Negócio
- Validação de dados de entrada para transações e registros de clientes.
- Persistência de dados no Firestore com controle de TTL (Time To Live) para expiração de registros.
- Geração de hash para identificação única de contas.
- Enriquecimento de dados de faturas de cartão de crédito com encargos financeiros.

### 6. Relação entre Entidades
- **Account**: Relaciona-se com transações e registros de clientes.
- **TransactionV2**: Relaciona-se com contas e faturas de cartão de crédito.
- **CreditCard**: Relaciona-se com contratos de crédito e transações.
- **Business**: Relaciona-se com proprietários e representantes legais.
- **Registration**: Relaciona-se com documentos pessoais e contatos.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| transactionsV2 | coleção | READ | Armazena transações financeiras. |
| accounts | coleção | READ | Armazena informações de contas. |
| customers | coleção | READ | Armazena registros de clientes. |
| creditContracts | coleção | READ | Armazena contratos de crédito. |
| creditCards | coleção | READ | Armazena cartões de crédito. |
| creditTransactionsV2 | coleção | READ | Armazena transações de crédito. |
| creditBillsV2 | coleção | READ | Armazena faturas de cartão de crédito. |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| transactionsV2 | coleção | INSERT/UPDATE | Armazena transações financeiras. |
| accounts | coleção | INSERT/UPDATE | Armazena informações de contas. |
| customers | coleção | INSERT/UPDATE | Armazena registros de clientes. |
| creditContracts | coleção | INSERT/UPDATE | Armazena contratos de crédito. |
| creditCards | coleção | INSERT/UPDATE | Armazena cartões de crédito. |
| creditTransactionsV2 | coleção | INSERT/UPDATE | Armazena transações de crédito. |
| creditBillsV2 | coleção | INSERT/UPDATE | Armazena faturas de cartão de crédito. |

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- Integração com Firestore para armazenamento de dados.
- Integração com serviços de autenticação via JWT.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de desenvolvimento, como injeção de dependências e uso de interfaces para abstração. A documentação e os comentários são adequados, facilitando o entendimento. No entanto, poderia haver uma maior padronização na nomenclatura de métodos e variáveis.

### 13. Observações Relevantes
- O sistema utiliza feature toggles para gerenciar configurações dinâmicas, como TTL de registros.
- A configuração de segurança utiliza JWT para autenticação de endpoints.
- A aplicação é configurada para diferentes ambientes (local, des, uat, prd) através de perfis do Spring.

--- 
```