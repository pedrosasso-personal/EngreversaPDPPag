---
## Ficha Técnica do Sistema

### 1. Descrição Geral
Sistema orquestrador de portabilidade de crédito para Open Finance Brasil (OFB). Implementa as APIs de portabilidade de crédito conforme especificação Open Finance, permitindo que clientes transfiram operações de crédito entre instituições financeiras. O sistema atua como camada de orquestração, integrando-se com múltiplos serviços internos (átomos) e externos para validar elegibilidade, processar solicitações, gerenciar cancelamentos e notificar pagamentos de portabilidade.

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal Spring Boot para inicialização da aplicação |
| **CreditPortabilityRouter** | Roteador Camel para endpoints de criação, consulta e cancelamento de portabilidade |
| **AccountDataRouter** | Roteador Camel para consulta de dados bancários para liquidação |
| **PaymentsRouter** | Roteador Camel para notificação de pagamentos de portabilidade |
| **ConcurrencyManagementRouter** | Roteador Camel para verificação de elegibilidade de contratos |
| **ValidateContractProcessor** | Processador que valida regras de negócio do contrato (periodicidade, CNPJ, valores, parcelas) |
| **ApiErrorProcessor** | Processador centralizado de tratamento de erros e formatação de respostas |
| **AuthenticationCreditPortabilityProcessor** | Processador de autenticação para escopo credit-portability |
| **AuthenticationLoansProcessor** | Processador de autenticação para escopo loans |
| **CreditPortabilityAtomRepositoryImpl** | Repositório para integração com átomo de portabilidade |
| **GestaoContratoRepositoryImpl** | Repositório para consulta de saldo devedor de contratos |
| **ParcelaFinanciamentoRepositoryImpl** | Repositório para consulta de parcelas vincendas |
| **OperationsRepositoryImpl** | Repositório para consulta de elegibilidade de contratos |
| **PortabilityGporAtomRepositoryImpl** | Repositório para consulta de dados bancários (ISPB, agência) |
| **ContractEligibilityServiceImpl** | Serviço de verificação de elegibilidade de contratos para portabilidade |
| **AccountDataServiceImpl** | Serviço para obtenção de dados bancários para liquidação |
| **InputValidator** | Validador de entrada usando Jakarta Validation |
| **LogBuild** | Builder fluente para construção de mensagens de log padronizadas |

### 3. Tecnologias Utilizadas
- **Framework:** Spring Boot 3.x (Jakarta EE)
- **Integração:** Apache Camel 4.x
- **Segurança:** Spring Security OAuth2 Resource Server, JWT
- **Serialização:** Jackson, Gson
- **Validação:** Jakarta Validation (Bean Validation)
- **Logging:** Logback com encoder JSON
- **Documentação:** SpringDoc OpenAPI 3.0 / Swagger
- **Build:** Maven
- **Containerização:** Docker
- **Infraestrutura:** Google Cloud Platform (GCP), Kubernetes
- **Monitoramento:** Micrometer, Prometheus, OpenTelemetry
- **HTTP Client:** RestTemplate, Apache HttpComponents
- **Utilitários:** Lombok, MapStruct

### 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /portabilities | CreditPortabilityRouter | Cria solicitação de portabilidade de crédito |
| GET | /portabilities/{portabilityId} | CreditPortabilityRouter | Consulta portabilidade por ID |
| PATCH | /portabilities/{portabilityId}/cancel | CreditPortabilityRouter | Cancela portabilidade de crédito |
| POST | /portabilities/{portabilityId}/payment | PaymentsRouter | Notifica pagamento/liquidação da portabilidade |
| GET | /portabilities/{portabilityId}/account-data | AccountDataRouter | Obtém dados bancários para liquidação via STR |
| GET | /credit-operations/{contractId}/portability-eligibility | ConcurrencyManagementRouter | Verifica elegibilidade do contrato para portabilidade |

### 5. Principais Regras de Negócio
- **Validação de Elegibilidade:** Verifica se contrato está elegível para portabilidade (não liquidado, sem ação judicial, modalidade compatível)
- **Gestão de Concorrência:** Impede múltiplas solicitações simultâneas para o mesmo contrato (OFB ou Registradora)
- **Validação de Periodicidade:** Garante que periodicidade das parcelas não foi alterada entre contrato original e proposta
- **Validação de CNPJ:** Verifica consistência do CNPJ da credora entre proposta e contrato original
- **Validação de Valor:** Contrato proposto não pode exceder saldo devedor do contrato original
- **Validação de Prazo:** Número de parcelas proposto não pode exceder parcelas vincendas do contrato original
- **Validação de Assinatura Digital:** Exige evidência de assinatura digital válida (documentId e signatureDateTime)
- **Validação Semântica de Cancelamento:** Impede cancelamento por "cliente" quando rejeitado por "proponente"
- **Estados da Portabilidade:** RECEIVED → PENDING → ACCEPTED_SETTLEMENT_IN_PROGRESS → ACCEPTED_SETTLEMENT_COMPLETED → PORTABILITY_COMPLETED
- **Cancelamento Condicional:** Permitido apenas nos estados RECEIVED, PENDING ou ACCEPTED_SETTLEMENT_IN_PROGRESS
- **Pagamento Condicional:** Aceito apenas nos estados ACCEPTED_SETTLEMENT_IN_PROGRESS ou PAYMENT_ISSUE

### 6. Relação entre Entidades
- **RequestCreditPortability:** Contém dados da proposta (customerContact, institution, contractIdentification, proposedContract)
- **Institution:** Relaciona creditor e proposing (cada um com companyName, companyCnpj, contact)
- **ContractIdentification:** Identifica contrato (contractId, contractNumber, ipocCode)
- **ProposedContract:** Detalha proposta (interestRates, contractedFees, contractedFinanceCharges, CET, amortizationScheduled, instalmentPeriodicity, totalNumberOfInstallments, installmentAmount, dueDate, contractAmount, digitalSignatureProof)
- **ResponsePortabilityEligibility:** Retorna elegibilidade (contractId, portability com isEligible, status, channel, companyName, companyCnpj, ineligible)
- **ResponsePortabilitiesByPortabilityId:** Retorna detalhes completos da portabilidade incluindo status, statusReason, rejection, loanSettlementInstruction
- **ResponseAccountData:** Retorna dados bancários (strCode com ispb, branchCode, hasFinancialAgent, accountNumber)

### 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| N/A | N/A | N/A | Sistema não acessa banco de dados diretamente |

**Observação:** O sistema consome dados de outros serviços via APIs REST, não acessa banco de dados diretamente.

### 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| N/A | N/A | N/A | Sistema não atualiza banco de dados diretamente |

**Observação:** Atualizações de estado são realizadas via chamadas aos átomos (serviços downstream).

### 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| openapi.yaml | Leitura | src/main/resources/swagger/ | Especificação OpenAPI 3.0 das APIs de portabilidade |
| application.yml | Leitura | src/main/resources/ | Configurações gerais da aplicação |
| application-des.yml | Leitura | src/main/resources/ | Configurações específicas do ambiente de desenvolvimento |
| application-local.yml | Leitura | src/main/resources/ | Configurações para execução local |
| logback-spring.xml | Leitura | src/main/resources/ e infra-as-code/arquivos/{env}/ | Configuração de logging |
| layers.xml | Leitura | src/main/resources/ | Configuração de camadas Docker para otimização de build |

### 10. Filas Lidas
não se aplica

### 11. Filas Geradas
não se aplica

### 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **sboot-open-pcre-atom-portability** | API REST | Átomo de portabilidade - CRUD de portabilidades, consulta de elegibilidade |
| **sboot-gpor-base-orch-elegibilidade** | API REST | Orquestrador de elegibilidade - verifica elegibilidade de contratos via registradora |
| **sboot-gpor-base-atom-dados-portabilidade** | API REST | Átomo de dados bancários - consulta ISPB, agência e dados para STR |
| **sboot-flex-base-orch-gestao-contrato** | API REST | Orquestrador de gestão de contratos - consulta saldo devedor |
| **sboot-flex-base-orch-parcela-financiamento** | API REST | Orquestrador de parcelas - consulta quantidade de parcelas vincendas |
| **sboot-open-cons-atom-consentimento** | API REST | Átomo de consentimento - validação de consentimentos Open Finance |
| **API Gateway (OAuth2)** | OAuth2/OIDC | Autenticação e autorização via JWT (issuer e JWKS) |

### 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões de orquestração com Apache Camel
- Separação clara de responsabilidades (routers, processors, services, repositories)
- Uso adequado de padrões de projeto (Builder para logs, Strategy para processadores)
- Tratamento centralizado de erros com ApiErrorProcessor
- Validação robusta de entrada com Jakarta Validation
- Logging estruturado com builder fluente (LogBuild)
- Configuração externalizada por ambiente
- Uso de DTOs gerados a partir de OpenAPI (design-first)
- Bom uso de anotações Lombok para reduzir boilerplate
- Tratamento de exceções customizadas (BusinessException, ValidationResponseException, AtomPassException)

**Pontos de Melhoria:**
- Alguns métodos longos em ValidateContractProcessor poderiam ser refatorados
- Falta de testes unitários incluídos na análise (marcados como NAO_ENVIAR)
- Algumas classes de domínio poderiam ter validações mais explícitas
- Uso misto de Gson e Jackson (poderia padronizar)
- Alguns hardcoded strings que poderiam ser constantes
- Documentação JavaDoc ausente em várias classes
- Alguns métodos em repositórios com lógica de negócio que deveria estar em services
- Tratamento de erros poderia ser mais granular em alguns casos

### 14. Observações Relevantes

1. **Conformidade Open Finance Brasil:** Sistema implementa especificação oficial de Portabilidade de Crédito v1.0.0-rc.1 do Open Finance Brasil

2. **Segurança:** Implementa dois fluxos OAuth2:
   - Client Credentials para comunicação máquina-a-máquina (credit-portability scope)
   - Authorization Code para operações com consentimento do usuário (loans scope)

3. **Assinatura de Payloads:** Suporta JWS (JSON Web Signature) para assinatura de mensagens conforme especificação OFB

4. **Idempotência:** Suporta header x-idempotency-key para garantir idempotência nas operações POST

5. **Rastreabilidade:** Implementa x-fapi-interaction-id para correlação de requisições/respostas

6. **Ambientes:** Configurado para múltiplos ambientes (local, des, uat, prd) com URLs específicas

7. **Infraestrutura:** Preparado para deploy em Kubernetes/GCP com configurações de probes (liveness/readiness)

8. **Observabilidade:** Integrado com OpenTelemetry, Prometheus e Spring Cloud Sleuth para tracing distribuído

9. **Multi-layer Docker:** Utiliza estratégia de camadas Docker otimizada para reduzir tempo de build e deploy

10. **Validações Complexas:** Implementa validações sintáticas (formato, obrigatoriedade) e semânticas (regras de negócio) conforme especificação OFB

11. **Gestão de Estados:** Máquina de estados bem definida para ciclo de vida da portabilidade (RECEIVED → PENDING → ACCEPTED_SETTLEMENT_IN_PROGRESS → ACCEPTED_SETTLEMENT_COMPLETED → PORTABILITY_COMPLETED, com possibilidade de REJECTED ou CANCELLED)

12. **Integração STR:** Suporta liquidação via Sistema de Transferência de Reservas (STR) exclusivo do OFB