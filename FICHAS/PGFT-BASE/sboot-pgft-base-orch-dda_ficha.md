# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-pgft-base-orch-dda** é um serviço stateless Spring Boot desenvolvido para gerenciar operações de DDA (Débito Direto Autorizado). Sua principal funcionalidade é realizar o cancelamento/exclusão de clientes no sistema DDA através de integração com serviços externos via SOAP/WebService. O sistema expõe uma API REST para receber solicitações de exclusão de DDA por CPF e orquestra a chamada ao serviço legado do Banco Votorantim utilizando Apache Camel para roteamento.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot que inicializa a aplicação |
| `DDAController` | Controlador REST que expõe o endpoint de exclusão de DDA |
| `CancelamentoDDAService` | Serviço de domínio que orquestra o processo de cancelamento via Camel |
| `ExcluirDDARouter` | Roteador Apache Camel que define o fluxo de exclusão |
| `ExcluirDDARepositoryImpl` | Implementação de repositório que realiza chamada SOAP ao serviço externo |
| `ExcluirDDARepository` | Interface de porta (hexagonal) para exclusão de DDA |
| `DdaConfiguration` | Classe de configuração Spring que define os beans da aplicação |
| `AppProperties` | Classe de propriedades de configuração (URL, credenciais) |
| `OpenApiConfiguration` | Configuração do Swagger/OpenAPI para documentação |
| `CamelContextWrapper` | Wrapper do contexto Camel para gerenciamento de rotas |
| `DdaException` | Exceção customizada de domínio para erros de DDA |
| `ResultExcluir` | Objeto de domínio representando resultado de exclusão |

---

## 3. Tecnologias Utilizadas

- **Spring Boot** (framework principal)
- **Spring Web** (REST APIs)
- **Spring Security OAuth2** (autenticação JWT)
- **Apache Camel 3.0.1** (orquestração e roteamento)
- **Apache CXF** (cliente SOAP/WebServices)
- **Swagger/Springfox 2.9.2** (documentação de API)
- **Micrometer/Prometheus** (métricas e monitoramento)
- **Logback** (logging)
- **Lombok** (redução de boilerplate)
- **Docker** (containerização)
- **Maven** (build e gerenciamento de dependências)
- **JUnit 5** (testes unitários)
- **Rest Assured** (testes funcionais)
- **Pact** (testes de contrato)
- **Grafana + Prometheus** (observabilidade)
- **Java 11** (linguagem)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/excluir/dda` | `DDAController` | Exclui/cancela cliente DDA pelo CPF informado no header |

---

## 5. Principais Regras de Negócio

1. **Exclusão de Cliente DDA**: O sistema recebe um CPF via header HTTP e solicita a exclusão do cliente no sistema DDA através de integração SOAP
2. **Autenticação OAuth2/JWT**: Todas as requisições devem ser autenticadas via token JWT
3. **Tratamento de Erros**: Erros são capturados e retornados com código de correlação, código HTTP e mensagem descritiva
4. **Orquestração via Camel**: O fluxo de exclusão é orquestrado pelo Apache Camel através de rotas definidas
5. **Auditoria**: Utiliza trilha de auditoria do BV para rastreamento de operações
6. **Credenciais de Serviço**: Utiliza usuário técnico (_saca_des/_saca_prd) para autenticação no ServiceBus

---

## 6. Relação entre Entidades

O sistema possui uma arquitetura hexagonal simplificada com as seguintes relações:

- **DDAController** (camada de apresentação) → **CancelamentoDDAService** (camada de domínio)
- **CancelamentoDDAService** → **CamelContextWrapper** → **ExcluirDDARouter** (orquestração)
- **ExcluirDDARouter** → **ExcluirDDARepository** (porta de saída)
- **ExcluirDDARepositoryImpl** (adaptador de infraestrutura) implementa **ExcluirDDARepository**
- **ResultExcluir** é o objeto de domínio que representa o resultado da operação
- **DdaException** é lançada em caso de erros de negócio

Não há entidades JPA/banco de dados, pois o sistema é stateless e apenas orquestra chamadas a serviços externos.

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
| `application.yml` | leitura | Spring Boot (startup) | Arquivo de configuração da aplicação com profiles (local, des, qa, uat, prd) |
| `logback-spring.xml` | leitura | Logback (logging) | Configuração de logs em formato JSON para diferentes ambientes |
| `DdaClienteAtacadoBusinessServiceContract_DES_1.wsdl` | leitura | CXF Plugin (build time) | WSDL do serviço SOAP de DDA para geração de classes cliente |
| `sboot-pgft-base-orch-dda.yaml` | leitura | Swagger Codegen (build time) | Especificação OpenAPI para geração de interfaces REST |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **ServiceBus DDA (SOAP)** | WebService SOAP | Serviço legado do Banco Votorantim para exclusão de clientes DDA. Endpoint: `https://servicebus[-des/-uat].bvnet.bv/atacado/crossProdutos/ddaClienteAtacadoBusinessService/v1` |
| **API Gateway (JWT)** | OAuth2/JWT | Validação de tokens JWT para autenticação. Endpoint: `https://apigateway[des/uat].bvnet.bv/openid/connect/jwks.json` |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura hexagonal bem definida com separação clara de camadas (application, domain, infrastructure)
- Uso adequado de padrões como Repository, Service e Controller
- Configuração externalizada e suporte a múltiplos ambientes
- Boa cobertura de testes (unitários, integração, funcionais)
- Uso de Lombok para reduzir boilerplate
- Documentação via Swagger/OpenAPI
- Observabilidade com Prometheus/Grafana
- Uso de Apache Camel para orquestração

**Pontos de Melhoria:**
- Tratamento de exceções genérico no controller (catch Exception)
- Falta de validação de entrada (CPF não é validado)
- Logs com informações sensíveis potenciais (CPF)
- Testes unitários com cobertura superficial (apenas assertNotNull)
- Falta de documentação inline (JavaDoc) nas classes principais
- Configuração de segurança OAuth2 básica sem customizações
- Ausência de circuit breaker para chamadas externas
- Código de testes com imports não utilizados e práticas questionáveis

---

## 14. Observações Relevantes

1. **Ambiente Multi-Cloud**: O sistema está preparado para deploy em Google Cloud Platform (conforme jenkins.properties)

2. **Profiles de Ambiente**: Suporta 5 ambientes distintos (local, des, qa, uat, prd) com configurações específicas

3. **Segurança**: Utiliza Resource Server OAuth2 com validação JWT via JWK

4. **Monitoramento**: Infraestrutura completa de observabilidade com Prometheus, Grafana e dashboards pré-configurados

5. **CI/CD**: Integração com Jenkins para pipeline automatizado

6. **Containerização**: Dockerfile otimizado com OpenJ9 JVM para redução de footprint de memória

7. **Arquitetura de Testes**: Separação clara entre testes unitários, integração e funcionais em diretórios distintos

8. **Versionamento**: Versão 0.1.0 indica que o sistema está em fase inicial de desenvolvimento

9. **Dependências Corporativas**: Utiliza bibliotecas internas do Banco Votorantim (arqt-base) para auditoria, segurança e tratamento de erros

10. **Limitação Funcional**: O sistema possui apenas uma operação (exclusão de DDA), sugerindo que pode ser parte de uma arquitetura de microsserviços maior