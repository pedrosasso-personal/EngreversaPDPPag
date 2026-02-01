# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-spag-base-atom-opf-service** é um serviço atômico desenvolvido em Java com Spring Boot para gerenciar dados de Open Finance (OPF). O sistema é responsável por receber, armazenar e disponibilizar informações relacionadas a contas bancárias, transações, dados cadastrais de clientes (pessoas físicas e jurídicas), cartões de crédito, contratos de crédito, faturas e transações de crédito. Utiliza o Google Cloud Firestore como banco de dados NoSQL principal e SQL Server para consultas específicas de transações do sistema SPAG.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal que inicializa a aplicação Spring Boot |
| **OpfServiceApiDelegateImpl** | Implementa os endpoints REST da API, delegando chamadas aos serviços de negócio |
| **OpfServiceService** | Orquestra operações de contas, transações e cadastros de clientes |
| **TransactionService** | Gerencia transações bancárias (V2) |
| **TransactionTempService** | Gerencia transações temporárias |
| **BusinessService** | Gerencia dados cadastrais de empresas (Business, Owners, Legal Representatives) |
| **CreditCardService** | Gerencia informações de cartões de crédito |
| **CreditContractService** | Gerencia contratos de crédito |
| **CreditTransactionService** | Gerencia transações de cartão de crédito |
| **CreditBillService** | Gerencia faturas de cartão de crédito |
| **TransactionSpagService** | Consulta transações do sistema SPAG (SQL Server) |
| **FeatureToggleService** | Gerencia feature toggles, incluindo TTL de coleções |
| **GenericRepository** | Repositório genérico base para operações no Firestore |
| **AccountRepositoryImpl** | Repositório específico para contas |
| **TransactionV2RepositoryImpl** | Repositório para transações V2 |
| **BusinessRepositoryImpl** | Repositório para dados de empresas |
| **CreditCardRepositoryImpl** | Repositório para cartões de crédito |
| **CreditBillV2RepositoryImpl** | Repositório para faturas de crédito |
| **CreditTransactionV2RepositoryImpl** | Repositório para transações de crédito |
| **TransactionSpagRepositoryImpl** | Repositório JDBI para consultas SQL Server |

---

## 3. Tecnologias Utilizadas

- **Java 11+**
- **Spring Boot 2.7.8** (via parent pom-atle-base-sboot-atom-parent)
- **Spring Security** (OAuth2 Resource Server com JWT)
- **Google Cloud Firestore** (banco de dados NoSQL principal)
- **SQL Server** (banco de dados relacional para consultas SPAG)
- **JDBI 3.9.1** (acesso a dados SQL)
- **Maven** (gerenciamento de dependências)
- **Lombok** (redução de boilerplate)
- **Jackson** (serialização/deserialização JSON)
- **OpenAPI/Swagger** (documentação de API)
- **Logback** (logging)
- **Spring Actuator** (monitoramento e métricas)
- **Feature Toggle** (sbootlib-arqt-base-feature-toggle 3.0.7)
- **H2 Database** (testes locais)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/opf-info | OpfServiceApiDelegateImpl | Recebe e persiste dados transacionais (contas e transações) |
| GET | /v1/opf-info/{transactionId} | OpfServiceApiDelegateImpl | Obtém informações temporárias de transação |
| GET | /v1/accounts | OpfServiceApiDelegateImpl | Lista contas consentidas pelo cliente |
| GET | /v1/accounts/{accountId} | OpfServiceApiDelegateImpl | Obtém dados de identificação de uma conta |
| GET | /v1/{accountId}/transactions | OpfServiceApiDelegateImpl | Lista transações de uma conta |
| POST | /v1/customer | OpfServiceApiDelegateImpl | Persiste dados cadastrais de pessoa física |
| GET | /v1/customer/{personalId} | OpfServiceApiDelegateImpl | Obtém dados cadastrais de cliente |
| POST | /v1/business | OpfServiceApiDelegateImpl | Persiste dados cadastrais de empresa |
| GET | /v1/business/{cnpjNumber} | OpfServiceApiDelegateImpl | Obtém dados cadastrais de empresa |
| POST | /v1/credit/card | OpfServiceApiDelegateImpl | Persiste dados de cartão de crédito |
| GET | /v1/card | OpfServiceApiDelegateImpl | Lista cartões de crédito |
| GET | /v1/card/{proxy} | OpfServiceApiDelegateImpl | Obtém cartão de crédito por proxy |
| POST | /v1/credit/contract | OpfServiceApiDelegateImpl | Persiste contrato de crédito |
| POST | /v1/credit/{creditCardAccountId}/transactions | OpfServiceApiDelegateImpl | Persiste transação de crédito |
| GET | /v1/card/{creditCardAccountId}/transactions | OpfServiceApiDelegateImpl | Lista transações de cartão de crédito |
| POST | /v1/credit/bills | OpfServiceApiDelegateImpl | Persiste fatura de cartão de crédito |
| GET | /v1/card/{creditCardAccountId}/bills | OpfServiceApiDelegateImpl | Lista faturas de cartão de crédito |
| GET | /v1/bills/{billId} | OpfServiceApiDelegateImpl | Obtém fatura por ID |
| POST | /v1/transactions-spag | OpfServiceApiDelegateImpl | Obtém transações do sistema SPAG |

---

## 5. Principais Regras de Negócio

1. **Geração de AccountId**: O ID da conta é gerado através de hash SHA3-256 da concatenação de compeCode, branchCode e number (com padding de zeros)
2. **Validação de Contas**: Contas são validadas verificando se possuem número válido antes de operações
3. **TTL de Registros**: Registros no Firestore possuem timestamp de expiração calculado com base na data da transação/fatura mais N meses (configurável via feature toggle)
4. **Transações Temporárias**: Sistema suporta armazenamento temporário de transações e contas para processamento posterior
5. **Enriquecimento de Faturas**: Faturas são enriquecidas com informações de taxas (fees) das transações relacionadas
6. **Deduplicação de Pagamentos**: Pagamentos de faturas são deduplicados por idempotencyKey
7. **Filtros de Data**: Consultas com filtros de data suportam período único (mesmo dia) ou intervalo
8. **Status de Conta**: Contas sem status definido são automaticamente marcadas como "ATIVA"
9. **Validação de Parâmetros**: Consultas de cartões exigem creditCardAccountId OU documentNumber, mas não ambos
10. **Sanitização de Logs**: Dados sensíveis são sanitizados antes de serem logados

---

## 6. Relação entre Entidades

**Principais Entidades e Relacionamentos:**

- **Account**: Representa uma conta bancária (depósito à vista, poupança ou pagamento pré-paga)
  - Relaciona-se com **TransactionV2** via accountId
  
- **TransactionV2**: Representa uma transação bancária
  - Pertence a uma **Account**
  - Contém informações da parte envolvida (partieCnpjCpf, partieCompeCode, etc.)

- **Registration**: Dados cadastrais de pessoa física
  - Identificada por CPF (personalId)
  - Contém documentos, contatos, qualificação e filiação

- **Business**: Dados cadastrais de empresa
  - Identificada por CNPJ
  - Relaciona-se com **Owner** e **LegalRepresentative**

- **Owner**: Sócios/proprietários de empresa
  - Contém lista de **Party** (sócios)
  - Contém **Contacts**

- **LegalRepresentative**: Representantes legais de empresa
  - Contém lista de **Procurator**

- **CreditContract**: Contrato de crédito
  - Identificado por contractNumber

- **CreditCard**: Cartão de crédito
  - Identificado por proxy
  - Relaciona-se com **CreditContract** via contractNumber

- **CreditBillV2**: Fatura de cartão de crédito
  - Identificada por billId
  - Relaciona-se com **CreditContract** via contractNumber
  - Contém lista de **PaymentBill**

- **CreditTransactionV2**: Transação de cartão de crédito
  - Relaciona-se com **CreditBillV2** via billId
  - Relaciona-se com **CreditContract** via contractNumber
  - Contém lista de **Fee**

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbLancamento | tabela | SELECT | Tabela de lançamentos do sistema SPAG |
| TbLancamentoPessoa | tabela | SELECT | Tabela de pessoas envolvidas em lançamentos SPAG |
| accounts | coleção Firestore | READ | Coleção de contas bancárias |
| accountsTemp | coleção Firestore | READ | Coleção temporária de contas |
| transactionsV2 | coleção Firestore | READ | Coleção de transações bancárias |
| transactionsTempV2 | coleção Firestore | READ | Coleção temporária de transações |
| customers | coleção Firestore | READ | Coleção de dados cadastrais de pessoas físicas |
| business | coleção Firestore | READ | Coleção de dados de empresas |
| owners | coleção Firestore | READ | Coleção de sócios/proprietários |
| legalRepresentatives | coleção Firestore | READ | Coleção de representantes legais |
| creditContracts | coleção Firestore | READ | Coleção de contratos de crédito |
| creditCards | coleção Firestore | READ | Coleção de cartões de crédito |
| creditBillsV2 | coleção Firestore | READ | Coleção de faturas de cartão |
| creditTransactionsV2 | coleção Firestore | READ | Coleção de transações de crédito |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| accounts | coleção Firestore | INSERT/UPDATE | Persistência de contas bancárias |
| accountsTemp | coleção Firestore | INSERT/UPDATE | Persistência temporária de contas |
| transactionsV2 | coleção Firestore | INSERT/UPDATE | Persistência de transações bancárias |
| transactionsTempV2 | coleção Firestore | INSERT/UPDATE | Persistência temporária de transações |
| customers | coleção Firestore | INSERT/UPDATE | Persistência de dados cadastrais PF |
| business | coleção Firestore | INSERT/UPDATE | Persistência de dados de empresas |
| owners | coleção Firestore | INSERT/UPDATE | Persistência de sócios/proprietários |
| legalRepresentatives | coleção Firestore | INSERT/UPDATE | Persistência de representantes legais |
| creditContracts | coleção Firestore | INSERT/UPDATE | Persistência de contratos de crédito |
| creditCards | coleção Firestore | INSERT/UPDATE | Persistência de cartões de crédito |
| creditBillsV2 | coleção Firestore | INSERT/UPDATE | Persistência de faturas de cartão |
| creditTransactionsV2 | coleção Firestore | INSERT/UPDATE | Persistência de transações de crédito |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| getTransactionsSpag.sql | leitura | TransactionSpagRepositoryImpl | Query SQL para buscar transações do SPAG |
| application.yml | leitura | Spring Boot | Configurações da aplicação |
| application-local.yml | leitura | Spring Boot | Configurações para ambiente local |
| logback-spring.xml | leitura | Logback | Configurações de logging |
| sboot-spag-base-atom-opf-service.yaml | leitura | OpenAPI Generator | Especificação OpenAPI da API |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|----------------|------|-----------|
| Google Cloud Firestore | NoSQL Database | Banco de dados principal para armazenamento de dados de Open Finance |
| SQL Server (SPAG) | Relational Database | Banco de dados legado para consulta de transações do sistema SPAG |
| Feature Toggle Service | Serviço Interno | Serviço de feature flags para configurações dinâmicas (ex: TTL de coleções) |
| OAuth2 Authorization Server | Autenticação/Autorização | Servidor de autenticação JWT (issuer-uri configurável por ambiente) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com camadas bem definidas (controller, service, repository, mapper)
- Uso adequado de padrões como Repository, Service e DTO
- Tratamento de exceções centralizado com classes customizadas
- Uso de Lombok para reduzir boilerplate
- Documentação OpenAPI completa e bem estruturada
- Implementação de feature toggles para configurações dinâmicas
- Sanitização de logs para segurança
- Uso de mappers para conversão entre camadas

**Pontos de Melhoria:**
- Algumas classes de serviço muito extensas (ex: OpfServiceApiDelegateImpl com muitos métodos)
- Falta de testes unitários nos arquivos fornecidos (apenas estrutura de testes presente)
- Alguns métodos com muitos parâmetros (ex: getCreditTransactions com 7 parâmetros)
- Uso de `@SneakyThrows` no TransactionSpagRowMapper pode ocultar exceções importantes
- Comentários em português e inglês misturados
- Algumas validações poderiam ser mais robustas (ex: validação de datas)
- Código poderia se beneficiar de mais constantes para valores mágicos

---

## 14. Observações Relevantes

1. **Arquitetura Atlante**: O sistema segue o padrão arquitetural Atlante do Banco Votorantim, utilizando o parent POM `pom-atle-base-sboot-atom-parent`

2. **Multi-ambiente**: Suporta múltiplos ambientes (local, des, uat, prd) com configurações específicas

3. **Segurança**: Implementa autenticação OAuth2 com JWT, com endpoints públicos configuráveis

4. **Monitoramento**: Expõe métricas via Spring Actuator na porta 9090 (health, metrics, prometheus)

5. **TTL Automático**: Implementa expiração automática de registros no Firestore através do campo `registryExpirationTimestamp`

6. **Versionamento de API**: API versionada (v1) permitindo evolução futura

7. **Conformidade Open Finance**: Estrutura de dados alinhada com especificações do Open Finance Brasil

8. **Geração de Código**: Utiliza OpenAPI Generator para gerar interfaces e DTOs a partir da especificação YAML

9. **Banco H2 Local**: Suporta banco de dados em memória para desenvolvimento local

10. **Logging Estruturado**: Implementa constantes de log padronizadas para facilitar monitoramento