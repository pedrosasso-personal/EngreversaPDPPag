---
## Ficha Técnica do Sistema

### 1. Descrição Geral
Sistema ACL (Anti-Corruption Layer) que atua como camada de integração entre aplicações do Banco Votorantim e o sistema core bancário Oracle FLEXCUBE (módulo Corporate Lending). O sistema expõe APIs REST que traduzem requisições para chamadas SOAP ao FLEXCUBE, realizando operações de criação e consulta de contas, contratos, renegociações, parcelas, desembolsos e rollover manual. Utiliza Apache Camel para orquestração de rotas e implementa mapeamento de domínios técnicos para tradução de valores entre sistemas.

---

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **FcubsclserviceController** | Controller REST que expõe 9 endpoints para operações de conta/contrato. Realiza conversão REST↔Domain via MapStruct e tratamento de exceções. |
| **FcubsclserviceService** | Serviço orquestrador que coordena chamadas via Apache Camel, valida headers e inicializa logs de rastreamento. |
| **FcubsclserviceRouter** | Configura rotas Camel (CREATE_ACCOUNT, QUERY_ACCOUNT, etc.) com tratamento global de exceções via ExceptionProcessor. |
| **FcubsclserviceAccountRepositoryImpl** | Repository que executa operações SOAP (createAccount, queryAccount, queryContractSummary) via FCUBSCLServiceConnector. |
| **FcubsclserviceRenegotiationRepositoryImpl** | Repository para criação de renegociações (operação CREATERENEGOTIATION). |
| **FcubsclserviceManualRolloverRepositoryImpl** | Repository para rollover manual de contratos (operação CREATEMANUALROLLOVER). |
| **FcubsclserviceInstallmentRepositoryImpl** | Repository para consulta de parcelas (operação QUERYINSTALLMENT). |
| **FcubsclserviceAmtOutstandRepositoryImpl** | Repository para consulta de valores em aberto (operação QUERYAMTOUTSTAND). |
| **FcubsclserviceExtSDisbrSettleRepositoryImpl** | Repository para consulta/modificação de liquidação de desembolso externo. |
| **MapeamentoDominioRepositoryImpl** | Repository que busca mapeamento de domínios técnicos via API externa (cache Caffeine). |
| **DominioCacheServiceImpl** | Serviço com cache Caffeine (4 itens, 1440min) para mapeamento de domínios. |
| **FCUBSCLServiceConnector** | Cliente SOAP (extends WebServiceTemplate) que realiza chamadas ao FLEXCUBE via Jaxb2Marshaller. |
| **FromAccountSoapMapper / ToAccountSoapMapper** | Mappers MapStruct bidirecionais (Domain↔SOAP) para entidade Account (centenas de campos). |
| **FromManualRolloverSoapMapper / ToManualRolloverSoapMapper** | Mappers para ManualRollover (60+ métodos). |
| **FromRenegotiationSoapMapper / ToRenegotiationSoapMapper** | Mappers para Renegotiation (50+ métodos). |
| **ExtraMapperImpl** | Mapper para conversão de headers, erros e warnings SOAP↔Domain. |
| **LogInfo** | Utilitário de log estruturado com mascaramento de referências (últimos 6 caracteres) e rastreamento de origem. |

---

### 3. Tecnologias Utilizadas

- **Framework**: Spring Boot 2.x
- **Orquestração**: Apache Camel 3.0.1 (RouteBuilder, ProducerTemplate, ExchangeBuilder)
- **Mapeamento**: MapStruct 1.4.1
- **SOAP**: Spring Web Services (WebServiceTemplate), Jaxb2Marshaller
- **Cache**: Caffeine 2.8.0 (max 4 itens, TTL 1440min)
- **Segurança**: OAuth2 JWT (0.19.0), Basic Auth (API mapeamento domínio)
- **Documentação**: Swagger 2.10.0 (OpenAPI 2.0)
- **Monitoramento**: Spring Actuator, Prometheus, Grafana (dashboards JVM/HTTP/HikariCP/Logback)
- **Banco de Dados**: HikariCP (configuração via properties)
- **Serialização**: Jackson (non_null), JAXB
- **Utilitários**: Lombok, Apache Commons Lang3
- **Testes**: JUnit, ArchUnit 0.19.0 (testes arquiteturais)
- **Infraestrutura**: Docker (adoptopenjdk/openjdk11-openj9:alpine-slim), OpenShift
- **Build**: Maven (multi-módulo: common, domain, application)

---

### 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/varejo/contrato/flex/fcubsclservice/account` | FcubsclserviceController | Cria nova conta no FLEXCUBE |
| GET | `/varejo/contrato/flex/fcubsclservice/account/{accountNumber}` | FcubsclserviceController | Consulta dados completos de conta |
| POST | `/varejo/contrato/flex/fcubsclservice/account/{accountNumber}/renegotiation` | FcubsclserviceController | Cria renegociação de contrato |
| POST | `/varejo/contrato/flex/fcubsclservice/account/{accountNumber}/rollover/{brn}/manual` | FcubsclserviceController | Cria rollover manual de contrato |
| GET | `/varejo/contrato/flex/fcubsclservice/account/{accountNumber}/outstanding/amount/{brn}` | FcubsclserviceController | Consulta valores em aberto (saldos) |
| GET | `/varejo/contrato/flex/fcubsclservice/account/{accountNumber}/contract/summary` | FcubsclserviceController | Consulta resumo de contratos por CPF/CNPJ |
| GET | `/varejo/contrato/flex/fcubsclservice/account/{accountNumber}/installment/{brn}` | FcubsclserviceController | Consulta parcelas de contrato |
| GET | `/varejo/contrato/flex/fcubsclservice/account/{accountNumber}/external/disbursement/{brn}` | FcubsclserviceController | Consulta liquidação de desembolso externo |
| POST | `/varejo/contrato/flex/fcubsclservice/account/{accountNumber}/external/disbursement/{brn}` | FcubsclserviceController | Modifica liquidação de desembolso externo |

**Observação**: Todos endpoints requerem OAuth2 JWT (exceto em profile local).

---

### 5. Principais Regras de Negócio

1. **Ajuste de Código de Filial (branchCode)**: Aplica padding de zeros à esquerda para garantir 3 dígitos em todas operações.

2. **Validação de Header para Mapeamento de Domínio**: Verifica presença de header `MAPEAMENTO_DOMINIO_INTERFACES` antes de executar operações. Se ausente, lança exceção `HEADER_NOT_FOUND`.

3. **Mapeamento de Domínios Técnicos**: Traduz valores entre sistemas (ex: FLEX→BV) através de API externa com cache Caffeine. Domínios mapeados: FLEX, CONFIGURACAO-ACESSO, CONFIGURACAO-CONTRATO, SITUACAO-CONTRATO, operações específicas (createAccount, queryAccount, etc).

4. **Montagem de Header SOAP FCUBS**: Método `setupFcubsHeader` constrói header transacional com dados de domínio (UBSCOMP, SERVICE, BRANCH, USERID, SOURCE, etc).

5. **Tratamento de Falhas SOAP**: Método `handleFailure` verifica `MsgStatType.FAILURE` em responses SOAP e lança `FcubsclserviceException` com código/mensagem de erro.

6. **Inicialização de Log Estruturado**: Cada operação inicializa log com número de contrato/referência mascarada (últimos 6 caracteres) para rastreamento.

7. **Conversão de Datas**: Parsing de datas ISO (LocalDate) para formato FLEXCUBE (yyyyMMdd) via `DateUtil`.

8. **Arredondamento Numérico**: Valores monetários arredondados para 2 casas decimais (HALF_EVEN) via `NumericUtil`.

9. **Campos Específicos BV**: Mapeamento de campos customizados do Banco Votorantim (cpfcnpj, businessprtnrcd, regioncode, bvuserid, cancltncd, addlFields com IOF, TAC, CET, seguro).

10. **Tratamento de Exceções com Preservação de Dados**: Em caso de erro, preserva dados de retorno parcial (Extra com header/error/warnings) para análise.

---

### 6. Relação entre Entidades

**Entidade Principal: Account (BaseAccount)**
- **Herança**: BaseAccount → Account, Renegotiation, ManualRollover
- **Composição**: 
  - Account contém: Promotions, AccountStats, Components (lista), ChgComp, Linkages, Advices, Assets, Financials, Collaterals, MIS, Security, Documents, UDFs (User Defined Fields), Disbursals, CompGuaCust, AccSchCmp, DisbrAddfieldsCustom
  - ManualRollover contém: AccountRoll, RollComponents, CrollSettlements, Guarantors
  - Renegotiation: estrutura similar a Account (sem Disbursals/CompGuaCust)
  - ContractSummary: CPFCNPJID, lista de SummaryDetail (status, produto, valores, parcelas)
  - Installment: INSTLDET (schedules), COMPDET (componentes), COMPPYTSTATS (histórico pagamentos)
  - AmountOutstand: AccountNumber, BranchCode, ValueDate, componentes outstanding
  - ExtSDisbrSettle: DsbrAccmasCustom, DisbrSchedulesCustom, DisbrAddfieldsCustom (beneficiário, barcode, pagamento)

**Entidade Transversal: Extra**
- Presente em todas entidades principais
- Contém: Header (dados transacionais FCUBS), ErrorResponse (lista), WarningResponse (lista)

**Relacionamento com SOAP**: Cada entidade Domain possui mapper bidirecional para tipo SOAP correspondente (ex: Account ↔ AccountFullType).

---

### 7. Estruturas de Banco de Dados Lidas

Não se aplica. O sistema não acessa banco de dados diretamente. Todas operações de leitura são realizadas via SOAP no sistema FLEXCUBE (Oracle).

---

### 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema não atualiza banco de dados diretamente. Todas operações de escrita (INSERT/UPDATE/DELETE) são realizadas via SOAP no sistema FLEXCUBE (Oracle).

---

### 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | ApplicationProperties | Configurações de ambiente (profiles, endpoints, mapeamento domínio) |
| FCUBSCLService.wsdl | Leitura | SOAPConfiguration (build-time) | Definição de contrato SOAP FLEXCUBE (650+ operações) |
| sboot-intr-base-acl-mapeamento-dominio.yml | Leitura | RestConfiguration (build-time) | Especificação OpenAPI da API de mapeamento de domínios |
| /usr/etc/log/*.log | Gravação | Logback (application.yml) | Logs estruturados da aplicação (JSON) |
| global-java-cacerts | Leitura | Infraestrutura (volume) | Certificados SSL/TLS para comunicação SOAP |

---

### 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas (JMS, Kafka, RabbitMQ).

---

### 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas.

---

### 12. Integrações Externas

| Sistema Externo | Tipo | Endpoint/URL | Descrição |
|-----------------|------|--------------|-----------|
| **Oracle FLEXCUBE (FCUBSCLService)** | SOAP | `https://flexcubewsuat.bvnet.bv:443/FCUBSCLService/FCUBSCLService` (UAT) / `${URL_FCUBSCL_SERVICE_ENDPOINT}` (outros ambientes) | Sistema core bancário. Operações: criação/consulta de contas, contratos, renegociações, parcelas, desembolsos, rollover manual, provisões, boletos. 650+ operações CRUD. |
| **API Mapeamento Domínio** | REST | `http://sboot-intr-base-acl-mapeamento-dominio.appuat.bvnet.bv/v2` (local/UAT) / `${URL_MAPEAMENTO_DOMINIO_ENDPOINT}` (outros ambientes) | API de tradução de valores entre domínios técnicos (FLEX, CONFIGURACAO-ACESSO, CONFIGURACAO-CONTRATO, SITUACAO-CONTRATO). Autenticação: Basic Auth. Cache Caffeine (4 itens, 1440min). |
| **OAuth2 Authorization Server** | OAuth2 JWT | `https://api-digitaldes.bancovotorantim.com.br/security/oauth2/token` (tokenUrl) / `${URL_API_JWK}` (jwkSetUri) | Servidor de autenticação/autorização. Valida tokens JWT em todos endpoints REST (exceto profile local). |
| **LDAP BV** | LDAP | `global-ldap-bvnet` | Diretório corporativo (não detalhado no código fornecido). |
| **Prometheus** | Métricas | Porta 9060 | Coleta de métricas (JVM, HTTP, HikariCP, Logback). |
| **Grafana** | Visualização | Porta 3000 | Dashboards de monitoramento. |

---

### 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- **Arquitetura Hexagonal**: Separação clara de responsabilidades (ports/adapters), módulos independentes (common, domain, application).
- **Uso de Padrões**: MapStruct para mapeamento (evita código boilerplate), Lombok para redução de verbosidade, Apache Camel para orquestração.
- **Testes Estruturados**: Profiles separados (unit, integration, functional, architecture com ArchUnit).
- **Observabilidade**: Logs estruturados (JSON), métricas Prometheus, dashboards Grafana, Actuator endpoints.
- **Cache Inteligente**: Caffeine para mapeamento de domínios (reduz chamadas externas).
- **Segurança**: OAuth2 JWT, mascaramento de dados sensíveis em logs.
- **Documentação**: Swagger/OpenAPI, WSDL bem estruturado.

**Pontos de Atenção:**
- **Exceções Genéricas**: Uso de `ERRO_GENERICO` (código 100) dificulta diagnóstico de falhas específicas.
- **Acoplamento Camel**: Domain layer possui dependência de Apache Camel (Exchange), violando parcialmente princípios de arquitetura limpa.
- **Logs Mascarados**: Mascaramento de referências (últimos 6 caracteres) pode dificultar debug em produção.
- **WSDL Legado**: Integração SOAP com sistema legado (FLEXCUBE) aumenta complexidade e fragilidade (650+ operações).
- **Falta de Testes de Contrato**: Não há evidências de testes de contrato (Pact, Spring Cloud Contract) para garantir compatibilidade com consumidores.
- **Documentação Inline**: Código possui poucos comentários explicativos (compensado parcialmente por nomes descritivos).

**Recomendações:**
1. Refinar hierarquia de exceções (criar exceções específicas por tipo de falha).
2. Isolar dependências de Camel em camada de infraestrutura (usar DTOs puros no domain).
3. Implementar testes de contrato para endpoints REST.
4. Adicionar circuit breaker (Resilience4j) para chamadas SOAP/REST externas.
5. Documentar regras de negócio complexas (mapeamento de domínios) em ADRs (Architecture Decision Records).

---

### 14. Observações Relevantes

1. **Contexto de Negócio**: Projeto FLEX-ORAC do Banco Votorantim, parte da iniciativa de modernização de integrações com sistema core bancário Oracle FLEXCUBE.

2. **Padrão ACL (Anti-Corruption Layer)**: Sistema atua como barreira de proteção, isolando aplicações internas de mudanças no FLEXCUBE. Traduz conceitos REST modernos para SOAP legado.

3. **Campos Customizados BV**: Extensivo uso de campos específicos do Banco Votorantim (cpfcnpj, businessprtnrcd, regioncode, bvuserid, cancltncd, addlFields com IOF, TAC, CET, seguro, barcode, beneficiário).

4. **Operações Críticas**: Sistema suporta operações financeiras críticas (criação de contas, renegociações, desembolsos). Falhas podem impactar diretamente clientes e operações bancárias.

5. **Versionamento**: Versão atual 0.6.0, JDK 11, plataforma GOOGLE (OpenShift).

6. **Ambientes**: Suporte a múltiplos ambientes (local, des, qa, uat, prd) com configurações dinâmicas via ConfigMaps.

7. **Monitoramento**: Infraestrutura robusta de observabilidade (Prometheus, Grafana, Actuator) com dashboards específicos para JVM, HTTP, HikariCP e Logback.

8. **Segurança**: OAuth2 JWT habilitado em todos ambientes exceto local. Cookies de sessão com flags httpOnly e secure.

9. **Performance**: Cache Caffeine reduz latência de chamadas à API de mapeamento de domínios. HikariCP otimiza pool de conexões (embora não haja acesso direto a BD no código analisado).

10. **Complexidade WSDL**: FLEXCUBE expõe 650+ operações SOAP com múltiplos sufixos (FS/IO/PK), suportando ciclo transacional completo (Create→Authorize→Modify→Delete→Reverse→Close→Reopen).

11. **Mapeamento Massivo**: Mappers MapStruct possuem centenas de mapeamentos explícitos (FromAccountSoapMapper possui 150+ propriedades), garantindo conversão precisa entre camadas.

12. **Trilha de Auditoria**: Integração com biblioteca "Trilha Auditoria Web" para rastreamento de operações (não detalhada no código fornecido).

---

**Documento gerado por análise automatizada de código-fonte. Versão: 1.0 | Data: 2025**