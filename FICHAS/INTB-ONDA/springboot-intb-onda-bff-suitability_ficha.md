# Ficha Técnica do Sistema

## 1. Descrição Geral

O **springboot-intb-onda-bff-suitability** é um BFF (Backend For Frontend) desenvolvido em Spring Boot que atua como intermediário entre interfaces de usuário (web/mobile) e serviços de backend corporativos. O sistema gerencia operações relacionadas a **Suitability** (adequação de perfil de investidor), permitindo obter, incluir e calcular informações de suitability de clientes pessoa física e jurídica. O BFF consome serviços REST externos através de um Service Bus corporativo, aplicando autenticação básica e tratamento de erros padronizado.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Server** | Classe principal da aplicação Spring Boot, inicializa o contexto e habilita Swagger |
| **HelloService** | Serviço de exemplo/referência para testes básicos |
| **SuitabilityService** | Orquestra as operações de negócio relacionadas a suitability (obter, incluir, calcular) |
| **SuitabilityRepository** | Responsável pela comunicação HTTP com os serviços externos via RestTemplate |
| **BrokerConnector** | Classe base para conectores de serviços externos, gerencia autenticação e tratamento de erros |
| **BrokerConfiguration** | Configuração centralizada de URLs, credenciais e endpoints dos serviços externos |
| **DocketConfiguration** | Configuração do Swagger para documentação da API |
| **ObterSuitabilityApi** | Controller REST para obter dados de suitability de um cliente |
| **IncluirSuitabilityApi** | Controller REST para incluir/gravar formulário de suitability |
| **CalcularSuitabilityApi** | Controller REST para calcular perfil de investidor baseado em respostas |
| **HelloApi** | Controller REST de exemplo/healthcheck |
| **FormularioSuitability** | Entidade de domínio representando um formulário de suitability completo |
| **RespostaFormularioSuitability** | Entidade de domínio representando o resultado do cálculo de suitability |
| **ApiTimeoutException** | Exceção customizada para timeout de APIs externas (HTTP 504) |
| **ApiUnavailableException** | Exceção customizada para indisponibilidade de APIs externas (HTTP 502) |
| **BusinessException** | Exceção customizada para erros de negócio (HTTP 400) |
| **IntegrationException** | Exceção customizada para erros de integração (HTTP 500) |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.0.0.RELEASE** - Framework principal
- **Spring Web** - Para criação de APIs REST
- **Spring Security** - Autenticação e autorização (Form Auth e LDAP)
- **Springfox Swagger 2.8.0** - Documentação de APIs
- **RestTemplate** - Cliente HTTP para consumo de serviços externos
- **Logback** - Framework de logging
- **Lombok 1.16.20** - Redução de boilerplate
- **Jackson** - Serialização/deserialização JSON
- **Gradle 4.5.1** - Gerenciamento de build
- **Docker** - Containerização (OpenJDK 8 com OpenJ9)
- **JMeter** - Testes funcionais automatizados
- **JaCoCo** - Cobertura de código
- **SonarQube** - Análise de qualidade de código
- **Bibliotecas Votorantim**:
  - springboot-arqt-base-trilha-auditoria-web:1.1.4
  - springboot-arqt-base-security-form:1.2.0
  - sbootlib-arqt-base-tracing:0.2.0
  - springboot-arqt-base-security:2.0.0

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | /hello | HelloApi | Endpoint de exemplo/healthcheck que retorna "Hello {name}" |
| POST | /obterSuitability | ObterSuitabilityApi | Obtém dados de suitability de um cliente por documento e tipo de pessoa |
| POST | /incluirSuitability | IncluirSuitabilityApi | Inclui/grava um novo formulário de suitability preenchido |
| POST | /calcularSuitability | CalcularSuitabilityApi | Calcula o perfil de investidor baseado nas respostas do questionário |

---

## 5. Principais Regras de Negócio

1. **Validação de Documento e Tipo de Pessoa**: Todos os endpoints de suitability exigem número de documento e tipo de pessoa (PF/PJ) como campos obrigatórios.

2. **Cálculo de Perfil de Investidor**: O sistema calcula o código e nome do perfil de investidor baseado nas respostas fornecidas ao questionário de suitability.

3. **Vigência de Suitability**: O sistema retorna informações sobre data de início e fim de vigência do suitability, além de dias restantes até expiração.

4. **Tratamento de Erros de Integração**: 
   - Timeout de serviços externos resulta em HTTP 504
   - Indisponibilidade de serviços resulta em HTTP 502
   - Erros de autenticação resultam em HTTP 401
   - Erros de negócio retornados pelos serviços são propagados como HTTP 400

5. **Autenticação Básica**: Todas as chamadas aos serviços externos utilizam autenticação HTTP Basic configurada por ambiente.

6. **Múltiplos Tipos de Resposta**: O sistema suporta diferentes tipos de resposta em questionários (múltipla escolha, valores numéricos, etc).

---

## 6. Relação entre Entidades

**FormularioSuitability** (entidade principal)
- numeroDocumento: String
- tipoPessoa: String
- questionario: Integer
- listaRespostas: List<RespostasInfo>
- codigoPerfilInvestidor: Integer
- nomePerfilInvestidor: String

**RespostasInfo** (composição de FormularioSuitability)
- pergunta: Integer
- tipoResposta: String
- listaItemResposta: List<ItemRespostaInfo>
- valorResposta: BigDecimal

**ItemRespostaInfo** (composição de RespostasInfo)
- resposta: String
- valorResposta: String

**RespostaFormularioSuitability** (resultado de cálculo)
- codigoPerfilInvestidor: Integer
- nomePerfilInvestidor: String

**Relacionamentos**:
- FormularioSuitability 1 ---> N RespostasInfo
- RespostasInfo 1 ---> N ItemRespostaInfo
- FormularioSuitability é convertido de/para Representations (DTOs) para comunicação REST

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
| application.yml | leitura | Spring Boot (resources) | Configurações da aplicação por ambiente (local, des, qa, uat, prd) |
| application-local.yml | leitura | Spring Boot (resources) | Configurações específicas do ambiente local |
| logback-spring.xml | leitura | Logback (resources e /usr/etc/log) | Configuração de logs da aplicação |
| roles/*.yml | leitura | Spring Security (resources/roles) | Definição de roles e grupos LDAP por ambiente |
| contratos/*.json | leitura | Swagger Codegen (resources/contratos) | Contratos OpenAPI dos serviços externos consumidos |
| .env | leitura | Docker runtime | Variáveis de ambiente para execução em container |

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
| **Service Bus Corporativo** | REST API | Barramento de serviços corporativo da Votorantim que expõe os serviços de dados corporativos de atacado |
| **Serviço Obter Suitability** | REST POST | Endpoint: `/v1/atacado/dadosCorporativos/obterSuitability` - Retorna dados de suitability de um cliente |
| **Serviço Incluir Suitability** | REST POST | Endpoint: `/v1/atacado/dadosCorporativos/incluirSuitability` - Persiste formulário de suitability |
| **Serviço Calcular Suitability** | REST POST | Endpoint: `/v1/atacado/dadosCorporativos/calcularSuitability` - Calcula perfil de investidor |
| **LDAP Corporativo** | LDAP | Autenticação de usuários e validação de grupos/roles (configurável por ambiente) |

**Configurações por Ambiente**:
- **DES**: https://servicebus-des.bvnet.bv
- **QA**: https://servicebus-qa.bvnet.bv
- **UAT**: https://servicebus-uat.bvnet.bv
- **PRD**: https://servicebus.bvnet.bv

**Autenticação**: HTTP Basic com credenciais configuradas via variáveis de ambiente (INTB_ACCOUNT_SERVICE_USERNAME e INTB_ACCOUNT_SERVICE_PASSWORD)

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Estrutura de pacotes bem organizada seguindo padrões de camadas (restservice, business, repository, domain, representation)
- Uso adequado de DTOs (Representations) separando camada de API do domínio
- Tratamento de exceções customizado e padronizado
- Configuração externalizada por ambiente
- Documentação Swagger implementada
- Uso de bibliotecas corporativas padronizadas
- Separação de testes por tipo (unit, integration, functional)
- Pipeline de CI/CD configurado (Jenkins, Docker, SonarQube)

**Pontos Negativos:**
- **Código comentado e não utilizado**: Presença de TODOs e comentários desnecessários
- **Falta de testes**: Diretórios de testes vazios (apenas arquivos .keep), indicando ausência de cobertura de testes
- **Tratamento de exceções genérico**: Métodos `tratrarErroRespostaApi` retornam null em alguns casos, o que pode causar NullPointerException
- **Falta de validações**: Ausência de validações de negócio nas camadas de serviço
- **Configurações hardcoded**: Timeouts fixos (5000ms connect, 20000ms read) sem possibilidade de configuração
- **Falta de logs estruturados**: Logs básicos sem contexto suficiente para troubleshooting
- **Ausência de circuit breaker**: Não há implementação de resiliência (Hystrix, Resilience4j)
- **Documentação incompleta**: README genérico sem informações específicas do projeto
- **Dependências desatualizadas**: Spring Boot 2.0.0 (lançado em 2018) está desatualizado

---

## 14. Observações Relevantes

1. **Padrão BFF**: O sistema implementa corretamente o padrão Backend For Frontend, atuando como agregador e adaptador entre frontend e serviços backend.

2. **Ambientes Múltiplos**: Suporte completo para 5 ambientes (local, des, qa, uat, prd) com configurações específicas.

3. **Segurança**: Implementa autenticação via Form Auth com integração LDAP corporativo, além de autenticação básica para serviços externos.

4. **Containerização**: Dockerfile otimizado usando OpenJDK 8 com OpenJ9 para melhor performance de memória.

5. **Infraestrutura como Código**: Arquivo `infra.yml` define probes de liveness/readiness, configmaps, secrets e volumes para deploy em Kubernetes/OpenShift.

6. **Geração de Código**: Utiliza Swagger Codegen para gerar automaticamente classes de representação a partir de contratos JSON.

7. **Ausência de Persistência**: O BFF não possui camada de persistência própria, atuando apenas como proxy/orquestrador.

8. **Versionamento de API**: Os serviços externos utilizam versionamento na URL (`/v1/`).

9. **Monitoramento**: Integração com ferramentas de observabilidade através de bibliotecas de tracing e auditoria corporativas.

10. **Limitações de Resiliência**: Não implementa padrões de resiliência como circuit breaker, retry ou fallback, o que pode impactar a disponibilidade em caso de falhas nos serviços externos.