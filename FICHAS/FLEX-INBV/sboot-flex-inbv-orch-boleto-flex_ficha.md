# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-flex-inbv-orch-boleto-flex** é um sistema orquestrador de operações de boletos e carnês para contratos financeiros Flex. Atua como camada de integração entre sistemas legados (Oracle FlexCube via SOAP) e serviços modernos (APIs REST internas), gerenciando todo o ciclo de vida de boletos: geração, consulta, registro, confirmação e emissão de segunda via. O sistema implementa feature toggles para alternar entre fluxos de processamento (FlexCube vs base interna) e utiliza Apache Camel para orquestração de rotas complexas.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **BoletoFlexController** | Controller REST expondo endpoints v2 para operações de boletos e carnês |
| **BoletoFlexRouter** | Router Apache Camel orquestrando fluxos de negócio (boleto avulso, carnê, 2ª via) |
| **BoletoFlexService** | Serviço principal contendo lógica de negócio de boletos |
| **BoletoFlexRepositoryImpl** | Repositório para operações de consulta e geração de boletos/carnês via FlexCube |
| **BoletoAvulsoFlexRepositoryImpl** | Repositório específico para boletos avulsos (query/modify adhoc payment simulation) |
| **GestaoContratoRepositoryImpl** | Repositório para gestão de contratos base interna FGTS (feature toggle) |
| **Solicitar2ViaCarneRepositoryImpl** | Repositório para operações de segunda via de carnê |
| **MapeamentoDominioRepositoryImpl** | Repositório para mapeamento de domínios e conversão de filiais BV<->Flex |
| **ClienteFlexRepositoryImpl** | Repositório para consulta de dados de clientes no FlexCube |
| **DominioCacheServiceImpl** | Serviço de cache (Caffeine) para mapeamentos de domínio |
| **GatewayOAuthService** | Serviço de autenticação OAuth2 (client credentials + password grant) |
| **FlexCube*Connector** | Conectores SOAP para serviços FlexCube (Query/Modify operations) |
| **BoletoBusinessServiceConnector** | Conector SOAP para serviço de registro de boletos SACA/SCCO |
| **ConsultarBoletoFlexMapper** | Mapper MapStruct para transformação de dados de boletos (inclui cálculos) |
| **SolicitarBoletoAvulsoProcessor** | Processor Camel para transformação de dados de boleto avulso |
| **GravarContratoProcessor** | Processor Camel para preparação de dados de gravação de contrato |

---

## 3. Tecnologias Utilizadas

- **Framework:** Spring Boot 2.x, Spring WS (SOAP clients)
- **Orquestração:** Apache Camel 3.20
- **Integração SOAP:** JAX-WS, JAXB, WSS4J (WS-Security)
- **Integração REST:** RestTemplate, Spring RestTemplate
- **Mapeamento:** MapStruct
- **Cache:** Caffeine (TTL 1440min, max 4 itens)
- **Segurança:** Spring Security OAuth2 Resource Server, JWT validation
- **Documentação API:** Swagger/OpenAPI (Springfox)
- **Observabilidade:** Spring Actuator, Micrometer, Prometheus, Grafana
- **Logs:** Logback (JSON format), Trilha Auditoria (arqt-base-trilha-auditoria-web)
- **Testes:** JUnit 5, Mockito, RestAssured, Pact (contract testing), ArchUnit
- **Build:** Maven 3.9, Java 11
- **Infraestrutura:** Kubernetes/OpenShift, Docker, Redis
- **CI/CD:** Jenkins

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v2/boletos/avulso/gerar` | BoletoFlexController | Gera PDF de boleto avulso |
| GET | `/v2/carnes/{numeroContrato}/segunda-via` | BoletoFlexController | Gera PDF de segunda via de carnê completo |
| GET | `/v2/carnes/{numeroContrato}/lamina/{numeroParcela}` | BoletoFlexController | Gera PDF de lâmina específica do carnê |
| POST | `/v2/boletos/contratos/gravar` | BoletoFlexController | Grava contrato flex na base interna |
| POST | `/v2/boletos/contratos/confirmar-registro` | BoletoFlexController | Confirma registro de boleto (com mensagem erro opcional) |
| GET | `/boleto` (deprecated) | BoletoFlexController | Consulta boletos |
| POST | `/boleto/avulso` (deprecated) | BoletoFlexController | Solicita boleto avulso |
| GET | `/carne` (deprecated) | BoletoFlexController | Consulta carnês |
| POST | `/carne/2via` (deprecated) | BoletoFlexController | Solicita segunda via carnê |

---

## 5. Principais Regras de Negócio

1. **Feature Toggle FGTS Base Interna:** Se `ft_flex_base_baixa_base_interna` ativo E contrato produto=10/modalidade=77 (FGTS), usa fluxo base interna; caso contrário, usa FlexCube.

2. **Validação Boleto Avulso:** Consulta simulação pagamento adhoc no FlexCube, valida status (MsgStatType.FAILURE), calcula valores (principal, juros, mora, desconto), registra via SACA e atualiza status no FlexCube.

3. **Geração Segunda Via Carnê:** Filtra boletos por numeroCarne, vencimento >= hoje, status não pago, gera PDF via atom-parcelas. Valida status de impressão/registro.

4. **Mapeamento Filial:** Conversão dinâmica filial BV <-> Flex via domínio FLEX_MAPEAMENTO_FILIAL + veículo legal, com right-padding 3 dígitos para FlexCube.

5. **Cálculo Valores Boleto:** Total atraso = principal + juros + mora - desconto. Tipo pessoa determinado por tamanho CPF/CNPJ. Multa calculada conforme regras contratuais.

6. **Confirmação Registro:** Trunca mensagem de erro em 180 caracteres. Atualiza status via ModifyAdhocBoleto (FlexCube) ou API dados-flex (base interna).

7. **Validação Carnê Reimpressão:** Motivo obrigatório (REPRINT_REASON). Parse boolean status via domínio. Valida MsgStatType.FAILURE.

8. **Headers FlexCube:** Monta headers SOAP com WS-Security (username/password) + trilha auditoria. Propaga contexto via headers Camel (numeroContrato, codigoFilial, nossoNumero).

9. **Cache Domínios:** Mapeamentos cacheados por 24h (1440min). Consulta via API mapeamento-dominio, monta Map propriedades.

10. **Gestão Contrato Base Interna:** Busca FSN (Financial Sequence Number) do contrato, salva boleto via API dados-flex com FSN, confirma registro com mensagem erro opcional.

---

## 6. Relação entre Entidades

**Domínio Principal:**
- `BoletoAvulso` contém `Boleto`, que possui array de `BoletoParcela`, cada uma com array de `DetalheParcela`
- `BoletoAvulso` possui `DetalheEnvio` (dados cliente/endereço) com `Endereco`
- `Carne2Via` referencia `Carne` (conjunto de boletos)
- `GravarContrato` contém array de `BoletoParcela` para registro

**Relacionamentos FlexCube (abstraídos via SOAP):**
- Contrato (Contract) → Boletos (Boleto Details)
- Contrato → Carnê (Carne Print/Reprint)
- Cliente (Customer) → Contratos
- Simulação Pagamento Adhoc (AdhocPymntSim) → Boleto Avulso

**Mapeamentos:**
- Filial BV ↔ Filial Flex (via domínio FLEX_MAPEAMENTO_FILIAL)
- Códigos domínio (instrumento cobrança, veículo legal, espécie título) via cache

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| FCUBS Contract Tables | tabela | SELECT (via SOAP) | Dados de contratos financeiros FlexCube |
| FCUBS Boleto Tables | tabela | SELECT (via SOAP) | Detalhes de boletos registrados |
| FCUBS Carne Tables | tabela | SELECT (via SOAP) | Informações de carnês impressos |
| FCUBS Customer Tables | tabela | SELECT (via SOAP) | Dados cadastrais de clientes |
| FCUBS AdhocPymnt Tables | tabela | SELECT (via SOAP) | Simulações de pagamento adhoc |
| Base Interna Contratos | tabela | SELECT (via API) | Resumo de contratos base interna (feature toggle) |

**Observação:** Acesso indireto via serviços SOAP FlexCube e APIs REST internas. Não há acesso direto SQL.

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| FCUBS AdhocPymnt Tables | tabela | UPDATE (via SOAP ModifyAdhocPymntSim) | Atualiza simulação pagamento adhoc |
| FCUBS Carne Tables | tabela | UPDATE (via SOAP ModifyCarneReprint) | Atualiza status reimpressão carnê |
| FCUBS Boleto Tables | tabela | UPDATE (via SOAP ModifyAdhocBoleto) | Confirma registro de boleto |
| Base Interna Boletos | tabela | INSERT/UPDATE (via API) | Salva e confirma boletos base interna (feature toggle) |

**Observação:** Atualizações indiretas via serviços SOAP FlexCube e APIs REST internas. Não há acesso direto SQL.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot Config | Configurações aplicação (profiles: local/des/qa/uat/prd) |
| infra.yml | leitura | Kubernetes ConfigMaps/Secrets | Configurações infraestrutura (URLs, credenciais) |
| *.wsdl (resources/wsdl/) | leitura | Maven JAXB2 Plugin | Contratos SOAP FlexCube para geração clientes |
| swagger/*.yaml | leitura | Swagger Codegen Plugin | Contratos REST APIs internas para geração clientes |
| logback-spring.xml | leitura | Logback | Configuração logs JSON (por ambiente) |
| boleto-*.pdf | gravação | atom-parcelas API (delegado) | PDFs de boletos/carnês gerados |
| cacerts (volume K8s) | leitura | JVM TrustStore | Certificados SSL para integrações |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

**SOAP Services (Oracle FlexCube - FCUBS):**
- **FCUBSCLService:** QueryContractSummary, QueryBoletoDetails, QueryCarneReprint, QueryAdhocPymntSim, ModifyAdhocPymntSim, ModifyCarneReprint, ModifyAdhocBoleto (>200 operações disponíveis)
- **FCUBSCustomerService:** QueryCustomer (dados cadastrais)
- **BoletoBusinessService (SACA/SCCO):** SolicitarRegistroBoleto (registro/baixa boletos)
- **BoletoFinanciamentoFlexBusinessService:** SolicitarAvulso, AtualizarRegistroBoletoAvulso
- **MapeamentoDominiosTechinicalService:** ListarDominios (conversões códigos/domínios)

**REST APIs Internas:**
- **sboot-flex-base-atom-parcelas:** Geração de PDFs (carnê completo, lâmina específica)
- **sboot-intr-base-acl-mapeamento-dominio:** Consulta domínios e mapeamento filiais BV<->Flex
- **sboot-flex-inbv-orch-contrato-financeiro-flex:** Consulta contratos financeiros
- **sboot-flex-base-orch-dados-flex:** Gestão boletos base interna (salvarBoleto, confirmarBoleto, queryContractSummary)

**Autenticação:**
- **API Gateway OAuth2:** Obtenção token JWT (client credentials + password grant) com usernameFlex/passwordFlex

**Infraestrutura:**
- **Redis:** Cache distribuído (configurado via secrets K8s)
- **Prometheus/Grafana:** Métricas e observabilidade (scrape /actuator/prometheus)

---

## 13. Avaliação da Qualidade do Código

**Nota:** 8/10

**Justificativa:**

**Pontos Positivos:**
- Arquitetura hexagonal bem definida (domain, application, common)
- Separação clara de responsabilidades (repositories, services, controllers, mappers)
- Uso adequado de MapStruct reduzindo boilerplate
- Testes abrangentes (unit, integration, functional, architecture com ArchUnit)
- Configuração externalizada por ambiente (YAML, ConfigMaps K8s)
- Observabilidade robusta (Actuator, Prometheus, logs JSON estruturados)
- Segurança implementada (OAuth2, JWT, WS-Security)
- Cache estratégico (Caffeine) para mapeamentos
- Feature toggles para controle de fluxos

**Pontos de Atenção:**
- Lógica de negócio distribuída entre routers Camel e services pode dificultar debug e manutenção
- Exception handling fragmentado (FlexCubeException, BoletoFlexException, GestaoContratoFlexException) sem hierarquia clara
- Feature toggle hardcoded em múltiplos locais (baixo acoplamento com serviço de feature flags)
- Dependência forte de headers Camel para propagação de contexto (acoplamento com framework)
- Conversões complexas em mappers (ex: ConsultarBoletoFlexMapper com lógica de cálculo) violam Single Responsibility
- Falta documentação inline em classes críticas (processors, routers)
- Truncamento de mensagem erro (180 chars) pode perder informações importantes

**Recomendações:**
- Centralizar lógica de negócio em services, usar Camel apenas para orquestração
- Criar hierarquia de exceptions com tratamento centralizado
- Externalizar feature toggles para serviço dedicado
- Extrair lógicas de cálculo dos mappers para services especializados
- Adicionar JavaDoc em classes/métodos públicos
- Implementar circuit breaker para integrações externas (Resilience4j)

---

## 14. Observações Relevantes

1. **Dual Mode Operation:** Sistema opera em dois modos via feature toggle `ft_flex_base_baixa_base_interna` - fluxo FlexCube (legado SOAP) vs base interna (REST moderno). Decisão baseada em produto/modalidade contrato (FGTS).

2. **Integração Híbrida SOAP/REST:** Mantém compatibilidade com sistema legado Oracle FlexCube (SOAP/WSDL) enquanto migra gradualmente para APIs REST internas. Conectores SOAP gerados via JAXB2, clientes REST via Swagger Codegen.

3. **Orquestração Camel:** Apache Camel gerencia fluxos complexos com múltiplas etapas (validação, transformação, integração, geração PDF). Headers Camel propagam contexto entre rotas.

4. **Segurança Multicamada:** WS-Security (username/password) para SOAP, OAuth2 JWT para REST, trilha auditoria em todas operações, validação token JWT com JWK.

5. **Mapeamento Dinâmico:** Conversão filiais BV<->Flex via domínio cacheado, suporta múltiplos veículos legais. Right-padding 3 dígitos para compatibilidade FlexCube.

6. **Geração PDF Delegada:** PDFs gerados por serviço especializado (atom-parcelas), desacoplando lógica de apresentação.

7. **Ambientes Segregados:** Configurações específicas por ambiente (local/des/qa/uat/prd) via ConfigMaps/Secrets K8s. URLs FlexCube, credenciais LDAP, tokens OAuth distintos.

8. **Observabilidade Completa:** Logs JSON estruturados, métricas Prometheus (scrape 5s), dashboards Grafana, health checks (liveness 420s initial delay, readiness 10s), async logging.

9. **Tratamento Robusto Erros:** Validação MsgStatType.FAILURE em respostas FlexCube, parse SoapFault, conversão para DomainException, mensagens erro truncadas 180 chars para persistência.

10. **CI/CD Automatizado:** Pipeline Jenkins com profiles Maven segregados (unit/integration/functional/architecture), contract testing Pact, deploy OCP, validação ArchUnit.