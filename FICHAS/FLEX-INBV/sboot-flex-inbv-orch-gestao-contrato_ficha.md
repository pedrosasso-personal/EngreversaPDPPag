# Ficha Técnica do Sistema

---

## 1. Descrição Geral

Sistema de orquestração para consulta de dados básicos de contratos e clientes no contexto de financiamento veicular. O sistema integra duas fontes de dados distintas (GCTR e FLEX) através de serviços SOAP, expondo endpoints REST para consulta por placa de veículo ou número de contrato. Utiliza Apache Camel para orquestração das chamadas aos sistemas legados.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `GestaoContratoV4Controller` | Controlador REST que expõe endpoints para consulta de dados por placa e por contrato |
| `GestaoContratoV4Service` | Serviço de domínio que coordena a execução das rotas Camel |
| `DadosPorPlacaRouter` | Rota Camel para consulta de dados por placa no sistema GCTR |
| `DadosPorContratoRouter` | Rota Camel para orquestração de consultas por contrato (GCTR e FLEX) |
| `ConsultarPlacaGctrRepositoryImpl` | Implementação de repositório para consulta SOAP no sistema GCTR (por placa) |
| `ConsultarContratoGctrRepositoryImpl` | Implementação de repositório para consulta SOAP no sistema GCTR (por contrato) |
| `ConsultarContratoFlexRepositoryImpl` | Implementação de repositório para consulta SOAP no sistema FLEX |
| `EnrichContratoGCTRStrategy` | Estratégia de agregação Camel para enriquecer resposta com dados do GCTR |
| `EnrichContratoFlexStrategy` | Estratégia de agregação Camel para enriquecer resposta com dados do FLEX |
| `CamelContextWrapper` | Wrapper para gerenciamento do contexto Camel |
| `Mapper` | Classe utilitária para transformação de objetos (baseada em ModelMapper) |
| `WSConfiguration` | Configuração de WebServiceTemplates para consumo de serviços SOAP |
| `AppProperties` | Propriedades de configuração da aplicação (URLs dos serviços) |

---

## 3. Tecnologias Utilizadas

- **Framework principal**: Spring Boot 2.x
- **Linguagem**: Java 11
- **Orquestração**: Apache Camel 3.0.1
- **Consumo SOAP**: Spring Web Services (WebServiceTemplate)
- **Mapeamento de objetos**: ModelMapper 2.3.0
- **Documentação API**: Swagger/Springfox 2.9.2
- **Segurança**: Spring Security OAuth2 (JWT)
- **Auditoria**: Biblioteca BV de trilha de auditoria (springboot-arqt-base-trilha-auditoria-web 2.1.3)
- **Monitoramento**: Spring Actuator + Prometheus + Grafana
- **Testes**: JUnit 5, Mockito, RestAssured, Pact
- **Build**: Maven
- **Containerização**: Docker
- **Orquestração de containers**: Kubernetes/OpenShift

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/varejo/consultarDadosBasicosClientePorPlaca` | `GestaoContratoV4Controller` | Consulta CPF/CNPJ de clientes associados a uma placa de veículo |
| GET | `/v1/varejo/consultarDadosBasicosClientePorContrato` | `GestaoContratoV4Controller` | Consulta CPF/CNPJ do cliente associado a um contrato específico |

---

## 5. Principais Regras de Negócio

1. **Consulta por Placa**: Retorna lista de CPF/CNPJ de todos os clientes associados à placa informada através do sistema GCTR.

2. **Consulta por Contrato com Fallback**: 
   - Primeiro tenta buscar dados no sistema GCTR
   - Se o GCTR retornar CPF/CNPJ válido, retorna imediatamente
   - Se o GCTR não retornar CPF/CNPJ (nulo ou vazio), realiza consulta adicional no sistema FLEX
   - Retorna o CPF/CNPJ encontrado em qualquer um dos sistemas

3. **Orquestração Condicional**: Utiliza Apache Camel para decidir dinamicamente se deve ou não consultar o sistema FLEX baseado na resposta do GCTR.

4. **Enriquecimento de Dados**: Utiliza estratégias de agregação (AggregationStrategy) para combinar dados de múltiplas fontes.

---

## 6. Relação entre Entidades

**Entidades de Domínio:**

- `ConsultarClientePorPlaca`: Representa requisição de consulta por placa
- `PlacasGCTR`: Encapsula requisição e resposta de consulta por placa
- `ConsultarPlacaGCTRResponse`: Resposta contendo lista de CPF/CNPJ
- `ConsultarClientePorContratoGCTRRequest`: Requisição de consulta por contrato no GCTR
- `ConsultarContratoGCTRResponse`: Resposta do GCTR com CPF/CNPJ
- `ListarContratosFlexRequest`: Requisição de consulta no sistema FLEX
- `ListarContratosBasicosFlexResponse`: Resposta do FLEX com dados de contratos
- `OrchestrationContratoDomainRequest`: Requisição orquestrada
- `OrchestrationContratoDomainResponse`: Resposta orquestrada consolidada

**Relacionamentos:**
- Uma placa pode estar associada a múltiplos CPF/CNPJ (relacionamento 1:N)
- Um contrato está associado a um único CPF/CNPJ (relacionamento 1:1)
- Os dados podem vir de GCTR ou FLEX dependendo da disponibilidade

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
| `application.yml` | leitura | Spring Boot | Arquivo de configuração da aplicação com profiles (local, des, qa, uat, prd) |
| `logback-spring.xml` | leitura | Logback | Configuração de logs em formato JSON para diferentes ambientes |
| WSDLs diversos (*.wsdl) | leitura | JAX-WS / Spring WS | Contratos de serviços SOAP para geração de stubs |
| `sboot-flex-inbv-orch-gestao-contrato.json` | leitura | Swagger Codegen | Especificação OpenAPI para geração de interfaces REST |

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
| **GCTR - Gestão Contrato Varejo Backend Service** | SOAP/WSDL | Sistema legado de gestão de contratos. Operações: `consultarDadosBasicosClientePorPlaca` e `consultarDadosBasicosClientePorContrato`. URLs variam por ambiente (DES, QA, UAT, PRD) |
| **FLEX - Contrato Financeiro Flex Business Service** | SOAP/WSDL | Sistema de contratos Flex. Operação: `listarContratosDadosBasicos`. URLs variam por ambiente via ServiceBus |
| **API Gateway BV** | REST/OAuth2 | Autenticação e autorização via JWT. Endpoint JWKS varia por ambiente |
| **Trilha de Auditoria BV** | Biblioteca | Sistema de auditoria corporativo integrado via interceptors SOAP e REST |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (presentation, domain, infrastructure)
- Uso adequado de padrões como Repository, Strategy e Builder
- Cobertura de testes unitários presente
- Uso de Apache Camel para orquestração complexa é apropriado
- Configuração externalizada por ambiente
- Documentação via Swagger

**Pontos de Melhoria:**
- Presença de `System.out.println` em código de produção (classes Strategy e Service)
- Tratamento de exceções genérico com apenas log e retorno null
- Falta de validação de entrada nos controllers
- Código de teste com alguns anti-patterns (uso excessivo de mocks, testes que não validam comportamento real)
- Falta de documentação inline (JavaDoc) nas classes principais
- Classe `Mapper` muito genérica, poderia ter métodos específicos para cada transformação
- Configuração de segurança OAuth2 básica, sem customizações aparentes
- Ausência de circuit breakers ou retry policies para chamadas externas

---

## 14. Observações Relevantes

1. **Arquitetura Multi-módulo**: O projeto está organizado em 3 módulos Maven (common, domain, application), seguindo boas práticas de separação de concerns.

2. **Ambientes**: Sistema preparado para 4 ambientes (DES, QA, UAT, PRD) com configurações específicas via ConfigMaps e Secrets do Kubernetes.

3. **Segurança**: Utiliza autenticação OAuth2 com JWT, mas as credenciais para serviços SOAP são gerenciadas via properties (usuário/senha).

4. **Monitoramento**: Infraestrutura completa de observabilidade com Prometheus e Grafana configurados via docker-compose.

5. **CI/CD**: Integração com Jenkins configurada via `jenkins.properties` e infraestrutura como código em `infra.yml`.

6. **Geração de Código**: Utiliza plugins Maven para geração automática de código a partir de WSDLs (jaxws-maven-plugin) e especificação OpenAPI (swagger-codegen-maven-plugin).

7. **Testes**: Estrutura de testes separada em unit, integration e functional, com suporte a testes de contrato via Pact.

8. **Limitações**: Sistema não possui persistência própria, atuando puramente como orquestrador/agregador de dados de sistemas legados.

9. **Dependências Corporativas**: Forte acoplamento com bibliotecas proprietárias do Banco Votorantim (arqt-base-*), o que pode dificultar portabilidade.

10. **Performance**: Não há evidências de cache ou otimizações para chamadas repetidas aos sistemas legados.

---