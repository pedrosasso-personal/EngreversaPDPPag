# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-ccbd-base-orch-agendamento** é um microsserviço orquestrador stateless desenvolvido em Java com Spring Boot, responsável por gerenciar operações de agendamento de pagamentos no Banco Votorantim. O sistema atua como camada de orquestração, coordenando chamadas a diversos serviços atômicos para realizar agendamentos de transferências (TED/TEF), pagamentos de boletos, tributos e operações relacionadas ao Open Banking e Débito Automático. Utiliza Apache Camel para orquestração de fluxos e integra-se com múltiplos backends através de APIs REST.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot que inicializa a aplicação |
| `AgendamentoController` | Controller REST que expõe endpoints de agendamento, consulta e cancelamento |
| `AgendamentoService` | Serviço de domínio que coordena operações de agendamento via Apache Camel |
| `AgendamentoRouter` | Define rotas Apache Camel para orquestração dos fluxos de negócio |
| `AgendamentoRepositoryImpl` | Implementação de repositório para operações de agendamento (criar, consultar, atualizar) |
| `ValidacaoRepositoryImpl` | Implementação de repositório para validação de boletos e transferências |
| `FeriadoRepositoryImpl` | Implementação de repositório para consulta de feriados |
| `CancelaAgendamentoRepositoryImpl` | Implementação de repositório para cancelamento de agendamentos |
| `CancelarAgendamentoOpenBankingRepositoryImpl` | Implementação específica para cancelamento de agendamentos Open Banking |
| `CancelarAgendamentoDebitoAutomaticoRepositoryImpl` | Implementação específica para cancelamento de débito automático |
| `BuscaDadosBoletoITPRepositoryImpl` | Implementação de repositório para buscar dados de boleto no sistema ITP |
| `AgendamentoMapper` | Mapper MapStruct para conversão entre objetos de domínio e representação |
| `AgendamentoBoletoMapper` | Mapper específico para operações de boleto |
| `FeriadoService` | Serviço para validação de dias úteis |
| `CamelContextWrapper` | Wrapper do contexto Apache Camel |
| `ConsultarAgendamentoProcessor` | Processor Camel para consulta de agendamentos |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Spring Security OAuth2** (autenticação e autorização)
- **Apache Camel 3.21.4** (orquestração de fluxos)
- **MapStruct 1.4.1** (mapeamento de objetos)
- **Swagger/OpenAPI 3.0** (documentação de APIs)
- **Maven** (gerenciamento de dependências)
- **Logback** (logging)
- **JUnit 5** (testes unitários)
- **Mockito** (mocks em testes)
- **RestTemplate** (cliente HTTP)
- **Lombok** (redução de boilerplate)
- **Jackson** (serialização JSON)
- **Micrometer/Prometheus** (métricas)
- **Docker** (containerização)
- **OpenShift/Kubernetes** (orquestração de containers)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/agendamento` | `AgendamentoController` | Cria um novo agendamento de pagamento (boleto, TED, TEF, etc) |
| PUT | `/v1/agendamento/atualizar` | `AgendamentoController` | Atualiza informações de agendamentos existentes |
| GET | `/v1/agendamentos/consumo-tributo` | `AgendamentoController` | Consulta agendamentos de consumo e tributo por período |
| POST | `/v1/agendamentos-movimentacao/cancelar` | `AgendamentoController` | Cancela um agendamento específico por NSU |
| GET | `/actuator/health` | Spring Actuator | Endpoint de health check |
| GET | `/actuator/metrics` | Spring Actuator | Endpoint de métricas |
| GET | `/swagger-ui/index.html` | Swagger UI | Interface de documentação da API |

---

## 5. Principais Regras de Negócio

1. **Validação de Dia Útil**: Agendamentos não podem ser realizados em finais de semana ou feriados nacionais
2. **Validação de Tipo de Pagamento**: Sistema valida se o código de liquidação corresponde a boleto (22), transferência (1, 21, 31, 32) ou outros tipos
3. **Validação de Dados Bancários**: Valida contas, agências e dados cadastrais através de serviços externos
4. **Validação de Saldo**: Consulta disponibilidade de saldo para débito
5. **Cancelamento Condicional**: Cancelamento de agendamentos segue regras específicas dependendo do tipo (Open Banking, Débito Automático ou padrão)
6. **Validação de Consentimento Open Banking**: Para agendamentos Open Banking, valida status do consentimento antes de processar
7. **Validação de Titularidade**: Verifica se a transferência é entre contas de mesma titularidade
8. **Validação de Limites**: Valida limites de valor para diferentes tipos de transação
9. **Validação de Boleto**: Valida linha digitável, data de vencimento e valores de boleto
10. **Atualização de Status**: Atualiza status de agendamentos (AWAITING_AUTHORISATION, AUTHORISED, REJECTED, CONSUMED, REVOKED)

---

## 6. Relação entre Entidades

**Principais Entidades de Domínio:**

- **AgendamentoDomainRequest/Response**: Representa um agendamento com dados completos (origem, destino, valores, datas, etc)
- **PessoaAgendamento**: Representa participantes (remetente/favorecido) com dados cadastrais
- **ValidaDomainResponse**: Resultado de validação de pagamento
- **Feriado**: Representa feriados nacionais
- **CancelaAgendamentoDomainRequest**: Dados para cancelamento de agendamento
- **ITPDomainResponse**: Resposta do sistema ITP com códigos de transação

**Relacionamentos:**
- Um `AgendamentoDomainRequest` possui um remetente e um favorecido (ambos `PessoaAgendamento`)
- Um `AgendamentoDomainResponse` contém status, valores e referências aos participantes
- `ValidaDomainResponse` contém dados de remetente, favorecido e conta corrente validados
- Agendamentos podem ser de diferentes tipos (boleto, transferência, débito automático, Open Banking)

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

**Observação**: O sistema não acessa diretamente bancos de dados. Todas as operações de leitura são realizadas através de chamadas a APIs de serviços atômicos (backends).

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

**Observação**: O sistema não atualiza diretamente bancos de dados. Todas as operações de escrita são realizadas através de chamadas a APIs de serviços atômicos (backends).

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `application.yml` | leitura | Spring Boot | Arquivo de configuração da aplicação com profiles (local, des, qa, uat, prd) |
| `logback-spring.xml` | leitura | Logback | Configuração de logging da aplicação |
| `swagger/*.yaml` | leitura | Swagger Codegen | Especificações OpenAPI dos serviços consumidos e expostos |
| `pom.xml` | leitura | Maven | Arquivo de configuração de dependências e build |
| `Dockerfile` | leitura | Docker | Definição da imagem Docker da aplicação |
| `infra.yml` | leitura | Infra as Code | Configurações de infraestrutura para deploy em Kubernetes/OpenShift |

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
| `sboot-ccbd-base-atom-agendamento` | API REST | Serviço atômico para persistência e consulta de agendamentos |
| `sboot-glob-base-atom-cliente-dados-cadastrais` | API REST | Serviço para consulta de feriados e dados cadastrais |
| `sboot-spag-base-orch-suporte-negocio` | API REST | Serviço de validação de boletos e transferências |
| `sboot-ccbd-base-atom-cancel-agend` | API REST | Serviço para cancelamento de agendamentos |
| `sboot-open-cons-orch-consentimento-pag-canal` | API REST | Serviço de consentimento Open Banking |
| `sboot-ccbd-base-orch-debito-automatico` | API REST | Serviço de débito automático |
| `sboot-sitp-base-atom-integrar-pagamento` | API REST | Serviço de integração com sistema ITP (busca dados de transação) |
| API Gateway OAuth2 | OAuth2 | Serviço de autenticação e autorização |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões de Clean Architecture (separação em camadas: application, domain, common)
- Uso adequado de padrões de projeto (Repository, Service, Mapper)
- Boa cobertura de testes unitários e estrutura para testes de integração
- Uso de MapStruct para mapeamento de objetos, reduzindo código boilerplate
- Documentação OpenAPI/Swagger bem definida
- Configuração adequada de profiles para diferentes ambientes
- Uso de Apache Camel para orquestração de fluxos complexos
- Tratamento de exceções estruturado
- Uso de Lombok para redução de código repetitivo

**Pontos de Melhoria:**
- Algumas classes com responsabilidades muito amplas (ex: `AgendamentoController` com múltiplas validações)
- Falta de documentação JavaDoc em várias classes e métodos
- Alguns métodos longos que poderiam ser refatorados (ex: `agendamento()` no controller)
- Uso de `RestClientException` genérica em vários pontos, dificultando tratamento específico de erros
- Configuração de múltiplas APIs via Swagger Codegen gera muito código duplicado
- Falta de validações mais robustas em alguns DTOs
- Alguns testes com mocks excessivos, dificultando manutenção
- Mistura de lógica de negócio no controller em alguns pontos

---

## 14. Observações Relevantes

1. **Arquitetura de Orquestração**: O sistema atua como orquestrador, não mantendo estado próprio, delegando persistência e lógica de negócio complexa para serviços atômicos

2. **Apache Camel**: Uso extensivo de rotas Camel para orquestração de fluxos, permitindo flexibilidade e manutenibilidade dos processos

3. **Multi-ambiente**: Configuração robusta para múltiplos ambientes (local, des, qa, uat, prd) através de profiles Spring

4. **Segurança**: Integração com OAuth2 JWT para autenticação e autorização de requisições

5. **Observabilidade**: Integração com Prometheus/Micrometer para métricas e monitoramento

6. **Containerização**: Aplicação preparada para deploy em containers Docker/Kubernetes

7. **Auditoria**: Integração com biblioteca de trilha de auditoria do Banco Votorantim

8. **Validações de Negócio**: Sistema realiza validações críticas como dia útil, feriados, limites e consentimentos antes de processar agendamentos

9. **Cancelamento Inteligente**: Lógica de cancelamento diferenciada para Open Banking, Débito Automático e agendamentos padrão

10. **Geração de Código**: Uso intensivo de Swagger Codegen para gerar clientes REST a partir de especificações OpenAPI, garantindo consistência com contratos de API

11. **Testes**: Estrutura de testes bem organizada (unit, integration, functional) com uso de frameworks adequados (JUnit 5, Mockito, Pact)

12. **Infraestrutura como Código**: Configuração de infraestrutura versionada em `infra.yml` para deploy automatizado