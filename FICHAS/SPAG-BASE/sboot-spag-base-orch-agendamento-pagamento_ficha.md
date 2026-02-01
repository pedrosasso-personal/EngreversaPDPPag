# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-spag-base-orch-agendamento-pagamento** é um orquestrador de agendamentos de pagamentos (TED e TEF) desenvolvido em Java com Spring Boot e Apache Camel. Atua como camada de orquestração entre diferentes serviços, coordenando validações de conta (CCBD), validações contábeis (SITP) e a gestão de agendamentos (SGAT). O sistema oferece operações de criação, atualização, cancelamento e consulta de agendamentos únicos e recorrentes.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal de inicialização da aplicação Spring Boot |
| `CreateSchedulingRouter` | Orquestra o fluxo de criação de agendamentos, incluindo validações |
| `CancelSchedulingRouter` | Gerencia o cancelamento de agendamentos únicos |
| `CancelSchedulingRecurrenceRouter` | Gerencia o cancelamento de agendamentos recorrentes |
| `UpdateSchedulingRouter` | Gerencia a atualização de agendamentos únicos |
| `UpdateSchedulingRecurrenceRouter` | Gerencia a atualização de agendamentos recorrentes |
| `SearchSchedulingRouter` | Realiza consultas de agendamentos únicos |
| `SearchSchedulingRecurrenceRouter` | Realiza consultas de agendamentos recorrentes |
| `OrchSgatService` | Serviço de integração com o sistema SGAT (gestão de agendamentos) |
| `ValidateAccountService` | Coordena validações de conta entre SITP e CCBD |
| `OrchCcbdValidateDataClientService` | Cliente para validação de dados de conta no CCBD |
| `OrchSitpValidateAccountingService` | Cliente para validação contábil no SITP |
| `HandlerResponseProcessor` | Processador centralizado de tratamento de erros e respostas |
| `JwtClientCredentialInterceptor` | Interceptor para injeção de token JWT nas requisições |
| `ScheduleManagementMapper` | Mapeamento entre representações de agendamentos |
| `RecurrenceManagementMapper` | Mapeamento entre representações de recorrências |
| `ValidateAccountMapper` | Mapeamento de dados para validação de contas |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.7.7** - Framework base da aplicação
- **Apache Camel** - Framework de integração e roteamento
- **MapStruct 1.6.0** - Mapeamento de objetos
- **OpenAPI Generator** - Geração de clientes a partir de contratos Swagger
- **Lombok** - Redução de código boilerplate
- **Jackson** - Serialização/deserialização JSON
- **Logback** - Framework de logging com saída em JSON
- **Spring Security OAuth2** - Segurança e autenticação JWT
- **JUnit 5 + Mockito** - Testes unitários
- **OkHttp MockWebServer** - Testes de integração
- **Maven** - Gerenciamento de dependências e build
- **Docker** - Containerização
- **Kubernetes/OpenShift** - Orquestração de containers (Google Cloud Platform)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/schedule-management/schedule` | `CreateSchedulingRouter` | Registra um novo agendamento de pagamento |
| GET | `/schedule-management/schedule` | `SearchSchedulingRouter` | Consulta agendamentos com filtros diversos |
| PUT | `/schedule-management/schedule/{uid}` | `UpdateSchedulingRouter` | Atualiza um agendamento existente |
| DELETE | `/schedule-management/schedule/{uid}` | `CancelSchedulingRouter` | Cancela um agendamento |
| GET | `/recurrence-management/v1/recurrence/` | `SearchSchedulingRecurrenceRouter` | Consulta agendamentos recorrentes |
| PUT | `/recurrence-management/v1/recurrence/{uid}` | `UpdateSchedulingRecurrenceRouter` | Atualiza uma recorrência |
| DELETE | `/recurrence-management/v1/recurrence/{uid}` | `CancelSchedulingRecurrenceRouter` | Cancela uma recorrência |

---

## 5. Principais Regras de Negócio

1. **Validação de Contas Distintas**: Impede que conta de débito e crédito sejam idênticas (mesma agência e número)
2. **Validação de Conta no CCBD**: Verifica existência e situação das contas de remetente e favorecido
3. **Validação Contábil no SITP**: Valida transação e flag de saldo antes de criar agendamento
4. **Ajuste de Datas em Dias Úteis**: Permite antecipar ou postergar agendamentos para dias úteis
5. **Gestão de Recorrências**: Suporta agendamentos recorrentes (semanal, mensal, anual) com controle de repetições
6. **Cancelamento com Data de Solicitação**: Registra a data exata da solicitação de cancelamento
7. **Busca por Identificadores Alternativos**: Permite busca por UID ou por identificador de requisição
8. **Tratamento de Erros Diferenciado**: Distingue erros de negócio (4xx) de erros técnicos (5xx)
9. **Autenticação via JWT**: Todas as operações requerem token JWT válido
10. **Paginação de Resultados**: Consultas suportam paginação com controle de página e tamanho

---

## 6. Relação entre Entidades

**Principais entidades e relacionamentos:**

- **SchedulingRegistrationRequest**: Entidade de entrada para criação de agendamento
  - Contém `FinancialInfo` (informações financeiras)
  - Pode conter `RecurrenceFrequency` (regra de recorrência)
  
- **FinancialInfo**: Informações financeiras do agendamento
  - Possui `Creditor` (favorecido)
  - Possui `Debtor` (remetente)
  - Possui `Payload` (dados da transação)

- **RecurrenceRule**: Regra de recorrência
  - Associada a múltiplos `Scheduling` (agendamentos gerados)
  - Contém frequência, datas inicial/final, repetições

- **Scheduling**: Agendamento individual
  - Pode estar associado a uma `RecurrenceRule`
  - Possui status (SCHEDULED, PROCESSING, CANCELED, etc.)
  - Contém informações financeiras completas

**Relacionamento textual:**
```
SchedulingRegistrationRequest (1) --> (1) FinancialInfo
FinancialInfo (1) --> (1) Creditor
FinancialInfo (1) --> (1) Debtor
FinancialInfo (1) --> (1) Payload
SchedulingRegistrationRequest (1) --> (0..1) RecurrenceFrequency
RecurrenceRule (1) --> (0..*) Scheduling
```

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

**Observação**: O sistema não acessa diretamente banco de dados. Todas as operações de persistência são delegadas aos serviços integrados (SGAT, CCBD, SITP).

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

**Observação**: O sistema não realiza operações diretas de escrita em banco de dados. As atualizações são realizadas através dos serviços integrados.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Descrição |
|-----------------|----------|-------------------------|-----------|
| `application.yml` | Leitura | Spring Boot | Configurações da aplicação |
| `application-test.yml` | Leitura | Spring Boot (testes) | Configurações de ambiente de teste |
| `logback-spring.xml` | Leitura | Logback | Configuração de logs em formato JSON |
| `layers.xml` | Leitura | Spring Boot Layered JAR | Definição de camadas para otimização de imagem Docker |
| `sboot-spag-base-orch-agendamento-pagamento.yaml` | Leitura | OpenAPI Generator | Contrato da API principal |
| `sboot-sgat-base-orch-agendamento.yaml` | Leitura | OpenAPI Generator | Contrato do cliente SGAT |
| `sboot-ccbd-base-orch-consulta-cc-cliente.yaml` | Leitura | OpenAPI Generator | Contrato do cliente CCBD |
| `sboot-sitp-base-atom-integrar-pagamento.yaml` | Leitura | OpenAPI Generator | Contrato do cliente SITP |
| Logs JSON | Gravação | Logback (STDOUT) | Logs estruturados da aplicação |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema | Tipo | Descrição |
|---------|------|-----------|
| **SGAT** (sboot-sgat-base-orch-agendamento) | REST API | Sistema de Gestão de Agendamentos Transacionais - responsável pela persistência e gestão dos agendamentos |
| **CCBD** (sboot-ccbd-base-orch-consulta-cc-cliente) | REST API | Sistema de Consulta de Conta Corrente - valida existência e situação das contas bancárias |
| **SITP** (sboot-sitp-base-atom-integrar-pagamento) | REST API | Sistema de Integração de Pagamentos - valida aspectos contábeis das transações |
| **API Gateway** | OAuth2 Server | Servidor de autenticação para obtenção de tokens JWT via client credentials |

**Fluxo de integração:**
1. Cliente → Orquestrador (este sistema)
2. Orquestrador → API Gateway (obtenção de token)
3. Orquestrador → SITP (validação contábil)
4. Orquestrador → CCBD (validação de conta)
5. Orquestrador → SGAT (operação de agendamento)
6. Orquestrador → Cliente (resposta)

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada com separação clara de responsabilidades (routers, processors, services, mappers)
- Uso adequado de padrões de projeto (Strategy, Builder, Mapper)
- Boa cobertura de testes unitários e de integração
- Tratamento centralizado de exceções com `HandlerResponseProcessor`
- Uso de DTOs específicos para cada camada (presentation, domain, integration)
- Configuração externalizada e adequada para múltiplos ambientes
- Logs estruturados em JSON para facilitar observabilidade
- Uso de MapStruct para mapeamentos type-safe
- Documentação via OpenAPI/Swagger
- Boas práticas de segurança (JWT, OAuth2)

**Pontos de Melhoria:**
- Algumas classes de teste com mocks excessivos que dificultam manutenção
- Falta de documentação JavaDoc em algumas classes críticas
- Constantes espalhadas em múltiplas classes (poderia centralizar melhor)
- Alguns métodos com muitos parâmetros (ex: `searchScheduling` com 17 parâmetros)
- Ausência de cache para tokens JWT (gera novo token a cada requisição)
- Falta de circuit breaker para resiliência nas integrações
- Alguns nomes de variáveis poderiam ser mais descritivos
- Validações de entrada poderiam ser mais explícitas com Bean Validation

---

## 14. Observações Relevantes

1. **Arquitetura de Orquestração**: O sistema segue o padrão de orquestração, centralizando a lógica de coordenação entre múltiplos serviços. Isso facilita manutenção mas cria um ponto único de falha.

2. **Geração de Código**: Utiliza OpenAPI Generator para criar clientes REST a partir de contratos Swagger, garantindo consistência entre serviços.

3. **Multi-tenancy**: Suporta múltiplos ambientes (des, uat, prd) com configurações específicas via ConfigMaps do Kubernetes.

4. **Observabilidade**: Logs estruturados em JSON, métricas via Actuator/Prometheus e health checks configurados.

5. **Containerização**: Dockerfile otimizado com multi-layer para melhor cache de dependências.

6. **Segurança**: Implementa autenticação JWT com validação de issuer e JWKS, além de OAuth2 client credentials flow.

7. **Resiliência**: Tratamento robusto de erros com distinção entre erros de negócio e técnicos, mas falta implementação de circuit breaker.

8. **Versionamento**: API versionada (v1) permitindo evolução sem quebrar clientes existentes.

9. **Testes**: Boa cobertura com testes unitários (Mockito) e testes de integração (MockWebServer), mas alguns testes poderiam ser mais concisos.

10. **Deploy**: Configurado para deploy no Google Cloud Platform via Kubernetes/OpenShift com probes de liveness e readiness adequadamente configurados.