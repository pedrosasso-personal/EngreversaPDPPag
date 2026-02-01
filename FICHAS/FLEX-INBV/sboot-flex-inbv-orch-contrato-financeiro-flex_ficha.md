---
## Ficha Técnica do Sistema

### 1. Descrição Geral
Sistema de integração e orquestração para consulta de contratos financeiros no Oracle FlexCube. Atua como camada de abstração entre sistemas internos do BV e o core bancário FlexCube, fornecendo APIs REST padronizadas para consulta de dados contratuais. Implementa transição arquitetural gradual de integrações SOAP legadas para APIs REST modernas, controlada por feature toggles. Oferece funcionalidades de consulta de contratos por CPF/CNPJ, detalhamento de contratos, dados de liberação/desembolso e informações de favorecidos.

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ContratoFinanceiroServiceController** | Controller REST que expõe endpoints para consulta de contratos financeiros |
| **ContratoFinanceiroFlexService** | Serviço de domínio que orquestra fluxos Camel para processamento de requisições |
| **ContratoFinanceiroFlexRouter** | Define rotas Apache Camel para orquestração de integrações e enriquecimento de dados |
| **ContratoFinanceiroFlexRepositoryImpl** | Repositório principal que integra com FlexCube (SOAP) e APIs MySQL, implementa lógica de negócio |
| **MapeamentoDominioFlexRepositoryImpl** | Repositório para tradução bidirecional de códigos de filiais BV↔Flex via ACL |
| **MapeamentoDominioRepositoryImpl** | Repositório para mapeamento de domínios técnicos via SOAP legado |
| **SequenciaFinanceiraRepositoryImpl** | Repositório para consulta e enriquecimento com sequência financeira de contratos |
| **GatewayOAuthService** | Serviço de autenticação OAuth2 com cache de tokens JWT |
| **FeatureToggleProcessor** | Processador Camel que avalia feature toggle para alternar fluxos SOAP/REST |
| **ContratoDadosBasicosMapper** | Mapper MapStruct para conversão de responses SOAP/REST em entidades de domínio |
| **ContratoFinanceiroFlexMapper** | Mapper para conversão de responses SOAP FlexCube em entidades detalhadas |
| **ApiRepresentationMapper** | Mapper para conversão de entidades de domínio em representations REST |

### 3. Tecnologias Utilizadas
- **Framework:** Spring Boot 2.x (parent arqt-base-master-springboot 4.0.4)
- **Orquestração:** Apache Camel 3.22.4
- **Persistência/Cache:** Spring Data Redis, Spring Cache
- **Segurança:** Spring Security OAuth2 Resource Server, JWT
- **Integração SOAP:** Spring WS, JAXB 2.3.1, WS-Security (UsernameToken)
- **Integração REST:** Spring RestTemplate, OpenAPI/Swagger
- **Mapeamento:** MapStruct
- **Feature Toggle:** feature-toggle 3.0.7
- **Observabilidade:** Spring Actuator, Prometheus, Grafana
- **Build:** Maven 3.9, Java 11
- **Testes:** JUnit 5, Mockito, ArchUnit 0.19.0
- **Containerização:** Docker, Kubernetes/OpenShift
- **Banco de Dados:** Oracle FlexCube (via SOAP), MySQL (via REST APIs)

### 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/contrato/resumo/documento/{cpfcnpj}` | ContratoFinanceiroServiceController | Lista contratos dados básicos por CPF/CNPJ |
| GET | `/contrato/resumo/numeroContrato/{cod}` | ContratoFinanceiroServiceController | Lista contratos dados básicos por número contrato |
| GET | `/contrato/resumo/parceiro/{cod}` | ContratoFinanceiroServiceController | Lista contratos dados básicos por código parceiro comercial |
| GET | `/contrato/numeroContrato/{cod}` | ContratoFinanceiroServiceController | Consulta contrato financeiro detalhado |
| GET | `/contrato/liberacao/numeroContrato/{cod}` | ContratoFinanceiroServiceController | Consulta dados de liberação/desembolso do contrato |
| GET | `/contrato/numeroContrato/{num}/dados-basicos/favorecidos/{filial}` | ContratoFinanceiroServiceController | Lista dados básicos de favorecidos do desembolso |

### 5. Principais Regras de Negócio
- **Validação FGTS:** Contratos com código produto 10 e modalidade 77 são identificados como FGTS e redirecionados para base MySQL quando feature toggle ativa
- **Mapeamento Filiais:** Tradução bidirecional de códigos de filiais BV↔Flex usando domínio "FLEX_MAPEAMENTO_FILIAL" + veículo legal
- **Situação Contrato:** Mapeamento de situações: L=Liquidado, V=Cancelado; contratos cancelados têm quantidade de parcelas pagas zerada
- **Extração Produto/Modalidade:** Parsing de PRODCODE (ex: "1377" → produto=13, modalidade=77)
- **Tipo Pessoa:** Tradução via domínio: I→PF (Pessoa Física), J→PJ (Pessoa Jurídica)
- **Sequência Financeira:** Enriquecimento padrão com sequência=1, código motivo=1, descrição="IMPLANTAÇÃO" quando não encontrado
- **Custos Contrato:** Extração de custos (IOF, etc.) de campos UDE-VALS do FlexCube
- **Participantes:** Extração de participantes contratuais de OthrApplicants
- **Desligamento Serviço:** Propriedade `servicoDesligado` simula erro FlexCube para desativação controlada
- **Cache Token OAuth2:** Tokens JWT são cacheados até expiração para otimização de chamadas

### 6. Relação entre Entidades

**Entidades de Domínio:**
- **ContratoDadosBasicos:** Dados resumidos do contrato (cliente, valores, parcelas, datas, situação)
  - Relaciona-se com **Cliente** (CPF/CNPJ, nome, tipo pessoa)
  - Contém **SequenciaFinanceira** (sequência, código motivo, descrição)
  
- **ContratoFinanceiroFlex:** Dados completos do contrato
  - Estende **ContratoDadosBasicos**
  - Contém lista de **CustoContrato** (tipo custo, valor)
  - Contém lista de **ParticipanteContrato** (código, papel)
  - Contém dados de taxas e índices
  
- **DadosLiberacaoContrato:** Dados de desembolso
  - Contém lista de **DadosPagamentoPrincipal** (valor, data agendamento)
  - Contém lista de **DadosBasicos** (favorecidos/beneficiários)

- **Dominio:** Estrutura de mapeamento chave-valor para tradução de códigos técnicos

### 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| STTM_CUST_ACCOUNT (FlexCube) | tabela | SELECT | Dados de contas de clientes no FlexCube |
| STTM_CUSTOMER (FlexCube) | tabela | SELECT | Dados cadastrais de clientes no FlexCube |
| GLTB_PROD_CODE (FlexCube) | tabela | SELECT | Códigos de produtos financeiros |
| Tabelas MySQL (via API) | tabelas | SELECT | Resumo contratos, contratos detalhados, dados clientes, dados desembolso (estrutura não exposta diretamente) |

### 8. Estruturas de Banco de Dados Atualizadas
não se aplica

### 9. Arquivos Lidos e Gravados
não se aplica

### 10. Filas Lidas
não se aplica

### 11. Filas Geradas
não se aplica

### 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| **Oracle FlexCube - FCUBSCLService** | SOAP | Sistema core bancário para operações de contratos financeiros. Operações: QueryContractSummary, QueryAccount, QueryExtsDisbrSettle. Endpoint UAT: https://flexcubewsuat.bvnet.bv:443/FCUBSCLService/FCUBSCLService |
| **Oracle FlexCube - FCUBSCustomerService** | SOAP | Sistema core bancário para dados de clientes. Operação: QueryCustomer. Endpoint UAT: https://flexcubewsdes.bvnet.bv:443/FCUBSCustomerService/FCUBSCustomerService |
| **Mapeamento Domínios Técnicos** | SOAP | Barramento de serviços corporativo para tradução de domínios técnicos. Operações: obterDominio, listarDominios. Endpoint: https://servicebus-des.bvnet.bv/corporativo/integradorCanais/mapeamentoDominiosTechinicalService/v1 |
| **ACL Mapeamento Domínio Flex** | REST | API para mapeamento bidirecional de filiais BV↔Flex. Endpoint UAT: sboot-intr-base-acl-mapeamento-dominio |
| **Dados Flex (MySQL)** | REST | API para consulta de dados contratuais em base MySQL. Endpoints: ResumoContratoApi, ContratoDetalhadoApi, DadosClienteApi, DadosDesembolsoApi, ResumoContratoSimplificadoApi. Endpoint UAT: sboot-flex-base-orch-dados-flex |
| **Sequência Financeira** | REST | API backend para consulta de sequência financeira de contratos. Endpoint local K8s: springboot-flex-orac-contrato-financiamento |
| **API Gateway OAuth2** | REST | Gateway de autenticação para obtenção de tokens JWT (client_credentials) |

### 13. Avaliação da Qualidade do Código

**Nota:** 8/10

**Justificativa:**
- **Pontos Positivos:**
  - Arquitetura bem estruturada com separação clara de responsabilidades (Controller → Service → Repository)
  - Uso adequado de padrões de projeto (Repository, Mapper, Strategy via Feature Toggle)
  - Boa cobertura de testes (~65%)
  - Implementação de transição arquitetural controlada (SOAP→REST) via feature toggles
  - Uso de MapStruct para mapeamentos type-safe
  - Configuração externalizada e parametrizada por ambiente
  - Observabilidade implementada (Actuator, Prometheus, Grafana)
  - Segurança OAuth2/JWT adequadamente configurada
  - Cache Redis para otimização de performance
  - Documentação OpenAPI/Swagger disponível

- **Pontos de Melhoria:**
  - Código com alta complexidade em alguns mappers (muitas transformações aninhadas)
  - Lógica de negócio misturada com lógica de integração em alguns repositórios
  - Tratamento de exceções poderia ser mais granular
  - Falta de logs estruturados em pontos críticos
  - Alguns métodos com muitos parâmetros (code smell)
  - Cache comentado em MapeamentoDominioRepositoryImpl sugere decisão arquitetural não finalizada
  - Dependência forte de configurações externas (muitos endpoints hardcoded em properties)

### 14. Observações Relevantes
- **Transição Arquitetural:** O sistema está em processo de migração de integrações SOAP legadas para APIs REST modernas. A feature toggle `ft_flex_base_consulta_base_interna` controla essa transição, permitindo rollback seguro.
- **Ambientes:** Configurações específicas para des/qa/uat/prd com diferentes TTLs de cache (120s em des/qa, 86400s em uat/prd).
- **Segurança SOAP:** Implementa WS-Security com UsernameToken/Password para autenticação em serviços FlexCube.
- **Mapeamento de Domínios:** Sistema complexo de tradução de códigos técnicos entre sistemas BV e FlexCube, essencial para interoperabilidade.
- **Orquestração Camel:** Uso de Apache Camel permite composição flexível de fluxos de integração e enriquecimento de dados.
- **Observabilidade:** Stack completa de monitoramento com Prometheus/Grafana configurada para ambientes locais e produção.
- **CI/CD:** Pipeline Jenkins configurado para deploy em Google Cloud Platform via OpenShift.
- **Scaffolding:** Projeto gerado a partir de template stateless 0.47.0, seguindo padrões corporativos BV.
- **Documentação:** README.md com instruções de setup, Confluence com documentação de onboarding e padrões.

---