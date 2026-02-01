# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-spag-base-acl-baas-doc-ted** é um serviço de integração (ACL - Anti-Corruption Layer) desenvolvido em Spring Boot que atua como intermediário para operações de transferências bancárias DOC/TED. O sistema recebe requisições REST, processa-as através de rotas Apache Camel e integra-se com serviços SOAP legados (DOCTEDTransferenciaBusinessService) e APIs REST internas (springboot-spag-base-enviar-detalhes) para realizar transferências e consultar/reenviar notificações de protocolos.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot que inicializa a aplicação |
| `BaasDocTedController` | Controlador REST que expõe os endpoints da API |
| `BaasDocTedService` | Serviço de domínio que orquestra as chamadas via Apache Camel |
| `BaasDocTedRouter` | Define as rotas Apache Camel para processamento das requisições |
| `DOCTEDTransferenciaIIBRepositoryImpl` | Implementação da integração com o serviço SOAP de transferências |
| `EnviarDetalhesRepositoryImpl` | Implementação da integração com a API REST de detalhes/notificações |
| `DOCTEDTransferenciaIIBMapper` | Mapper MapStruct para conversão entre objetos de domínio e representações |
| `BaasDocTedConfiguration` | Configuração principal dos beans do sistema |
| `WSConfiguration` | Configuração de clientes SOAP (WebServiceTemplate) |
| `RestConfiguration` | Configuração de clientes REST (RestTemplate) |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot** (framework principal)
- **Apache Camel 3.0.1** (orquestração e roteamento)
- **Spring Web Services** (cliente SOAP)
- **RestTemplate** (cliente REST)
- **MapStruct 1.3.1** (mapeamento de objetos)
- **Lombok** (redução de boilerplate)
- **Swagger/OpenAPI 2.9.2** (documentação de API)
- **Spring Security OAuth2** (segurança JWT)
- **Logback** (logging)
- **JUnit 5** (testes unitários)
- **Pact 4.0.3** (testes de contrato)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Kubernetes/OpenShift** (orquestração - evidenciado pelo infra.yml)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/baas/pagamentos/transferencias-doc-ted/incluir` | `BaasDocTedController` | Solicita uma transferência DOC/TED |
| POST | `/v1/baas/pagamentos/transferencias-doc-ted/notificacao/consultar` | `BaasDocTedController` | Consulta detalhes de um protocolo de transferência |
| POST | `/v1/baas/pagamentos/transferencias-doc-ted/notificacao/reenviar` | `BaasDocTedController` | Solicita reenvio de notificação de um protocolo |

---

## 5. Principais Regras de Negócio

1. **Validação de Transferências**: O sistema valida dados obrigatórios de remetente e favorecido antes de processar transferências DOC/TED
2. **Suporte a Fintech**: Permite informar CPF/CNPJ do cliente fintech separadamente do remetente principal
3. **Conversão de Formatos**: Converte datas de String para XMLGregorianCalendar para integração SOAP
4. **Conversão de Valores**: Transforma valores monetários de String para BigDecimal
5. **Roteamento por Tipo de Operação**: Utiliza rotas Camel distintas para transferência, consulta e reenvio
6. **Autenticação WS-Security**: Aplica autenticação username/password em chamadas SOAP
7. **Trilha de Auditoria**: Propaga informações de auditoria nos headers SOAP

---

## 6. Relação entre Entidades

**Entidades Principais:**

- `TransferenciasDocTedTransacaoRequest`: Dados de entrada para solicitação de transferência
- `TransferenciasDocTedTransacao`: Resposta da transferência contendo protocolo
- `Protocolo`: Informações do protocolo gerado (número, status, código)
- `DetalheMensagemRequest`: Dados para consulta/reenvio de notificação
- `DetalheProtocoloResponse`: Detalhes completos de um protocolo
- `Mensagem`: Informações detalhadas da transação (valor, contas, datas, status)
- `RetornoMensagem`: Resposta de operação de reenvio

**Relacionamentos:**
- `TransferenciasDocTedTransacao` contém um `Protocolo`
- `DetalheProtocoloResponse` contém uma `Mensagem`
- Todas as entidades de request são mapeadas para objetos de domínio e posteriormente para representações SOAP/REST

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
| `application.yml` | leitura | Spring Boot (startup) | Configurações da aplicação (profiles, endpoints, credenciais) |
| `logback-spring.xml` | leitura | Logback (runtime) | Configuração de logs da aplicação |
| `*.wsdl` e `*.xsd` | leitura | JAX-WS (geração de código) | Contratos SOAP para geração de stubs |
| `*.yaml` (swagger) | leitura | Swagger Codegen (geração de código) | Contratos OpenAPI para geração de interfaces REST |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| **DOCTEDTransferenciaBusinessService** | SOAP | Serviço legado de transferências DOC/TED do Banco Votorantim (IIB/ESB). Endpoint: `https://servicebus-{env}.bvnet.bv/atacado/pagamentos/DOCTEDTransferenciaBusinessService/v1` |
| **springboot-spag-base-enviar-detalhes** | REST | API interna para consulta e reenvio de detalhes de mensagens/protocolos. Endpoints: `/v1/buscaDetalheMensagem` e `/v1/solicitaReenvioMensagem` |
| **API Gateway OAuth2** | REST | Serviço de autenticação JWT. Endpoint: `https://apigateway{env}.bvnet.bv/openid/connect/jwks.json` |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões hexagonais (ports/adapters)
- Separação clara entre camadas (domain, application, infrastructure)
- Uso adequado de frameworks modernos (Spring Boot, Camel, MapStruct)
- Implementação de testes (unitários, integração, funcionais)
- Documentação OpenAPI/Swagger
- Uso de Lombok para reduzir boilerplate
- Configuração externalizada por profiles

**Pontos de Melhoria:**
- Classe `Uteis` com método estático genérico (anti-pattern utility class)
- Conversões manuais extensas no método `toSolicitarTransferenciaTEDRequest` (poderia usar MapStruct)
- Tratamento de exceções genérico (`throws Exception`)
- Falta de validações de negócio mais robustas
- Comentários em português misturados com código em inglês
- Alguns testes vazios ou incompletos (ex: `BaasDocTedConfigurationTest`, `BaasDocTedControllerTest`)
- Configurações de segurança com credenciais em variáveis de ambiente sem criptografia adicional

---

## 14. Observações Relevantes

1. **Arquitetura ACL**: O sistema atua como Anti-Corruption Layer, isolando o domínio de negócio das peculiaridades dos sistemas legados SOAP
2. **Multi-ambiente**: Suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas
3. **Containerização**: Preparado para execução em containers Docker/Kubernetes
4. **Segurança**: Implementa autenticação OAuth2 JWT e WS-Security para SOAP
5. **Observabilidade**: Expõe métricas Prometheus e endpoints Actuator na porta 9090
6. **Versionamento de API**: Utiliza versionamento por path (`/v1/`)
7. **Fintech Support**: Campo específico `numeroCNPJCPFRemetenteClienteFintech` indica suporte a operações de fintechs
8. **Infraestrutura como Código**: Arquivo `infra.yml` define configurações de deployment no Kubernetes
9. **Pipeline CI/CD**: Arquivo `jenkins.properties` indica integração com Jenkins
10. **Documentação de Testes**: Projeto SoapUI incluído para testes manuais/automatizados