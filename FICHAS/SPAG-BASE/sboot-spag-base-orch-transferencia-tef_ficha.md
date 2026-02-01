# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-spag-base-orch-transferencia-tef** é um serviço de orquestração de transferências TEF (Transferência Eletrônica de Fundos) do Banco Votorantim. O sistema processa pagamentos recebidos via fila IBM MQ, orquestrando chamadas a diversos serviços (átomos) para validação, débito/crédito de contas, notificações a sistemas legados (SITP, PGFT, SPAG) e tratamento de ocorrências. Utiliza Apache Camel para orquestração de fluxos, com suporte a circuit breaker e estorno automático em caso de falhas.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `TransferenciaTefListener` | Listener JMS que recebe mensagens XML da fila IBM MQ e inicia o processamento |
| `TransferenciaTefController` | Controller REST que expõe endpoint HTTP para processamento de pagamentos |
| `TransferenciaTefService` | Serviço que delega o processamento para as rotas Camel |
| `TransferenciaTefRouter` | Rota principal Camel que orquestra o fluxo completo de processamento |
| `CircuitBreakRouter` | Rota Camel responsável pela verificação de circuit breaker |
| `ValidarPagamentoRepositoryImpl` | Implementação de chamada ao serviço de validação de pagamento |
| `DebitarCreditarContaRepositoryImpl` | Implementação de chamada ao serviço de débito/crédito em conta |
| `NotificarPagamentoSITPRepositoryImpl` | Implementação de notificação ao sistema SITP |
| `NotificarPagamentoPGFTRepositoryImpl` | Implementação de notificação ao sistema PGFT |
| `NotificarPagamentoSPAGRepositoryImpl` | Implementação de notificação ao sistema SPAG via RabbitMQ |
| `TratarOcorrenciasRepositoryImpl` | Implementação de chamada ao serviço de tratamento de ocorrências |
| `AtualizarSituacaoSpagRepositoryImpl` | Implementação de atualização de situação do lançamento no SPAG |
| `IntegrarPagamentoRepositoryImpl` | Implementação de verificação de circuit breaker |
| `EstornoProcessor` | Processor Camel para tratamento de estorno em caso de erro |
| `CircuitBreakProcessor` | Processor Camel para processamento de circuit breaker |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Apache Camel 3.0.1** (orquestração de fluxos)
- **IBM MQ** (mensageria para recebimento de solicitações)
- **RabbitMQ** (mensageria para notificações)
- **RestTemplate** (cliente HTTP para chamadas REST)
- **Swagger/OpenAPI** (documentação de APIs)
- **Lombok** (redução de boilerplate)
- **JUnit 5 + Mockito** (testes unitários)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Prometheus + Grafana** (métricas e monitoramento)
- **Spring Actuator** (health checks e métricas)
- **Feature Toggle (ConfigCat)** (controle de features)
- **OAuth2/JWT** (segurança e autenticação)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/transferencia-tef` | `TransferenciaTefController` | Processa uma transferência TEF recebendo um DicionarioPagamento |

---

## 5. Principais Regras de Negócio

1. **Validação de Pagamento**: Antes de processar, valida dados do pagamento (contas, valores, documentos)
2. **Circuit Breaker**: Verifica se há circuit breaker ativo para o tipo de transação antes de processar
3. **Débito/Crédito**: Realiza débito na conta remetente e crédito na conta favorecida
4. **Notificações Paralelas**: Notifica sistemas legados (SITP, PGFT) de forma assíncrona
5. **Notificação SPAG**: Envia notificação para fila RabbitMQ do sistema SPAG
6. **Estorno Automático**: Em caso de falha em qualquer etapa, executa estorno automático do débito
7. **Tratamento de Ocorrências**: Registra ocorrências de erro no sistema de tratamento
8. **Atualização de Status**: Atualiza status do lançamento (CONFIRMADO ou ERRO_PROCESSAMENTO)
9. **Retry com Backoff**: Implementa retry com delay exponencial (3 tentativas, 15s de intervalo)
10. **Conversão de Tipo de Conta**: Converte códigos numéricos de tipo de conta para abreviações (CC, PP, etc)
11. **Exclusão de Circuit Breaker para Devoluções**: Transações de devolução (códigos 7300, 7400) não passam por circuit breaker

---

## 6. Relação entre Entidades

**Entidade Principal**: `DicionarioPagamento` (da biblioteca `votorantim.spag.lib.datatype`)

**Entidades de Domínio**:
- `ValidarPagamentoRequest/Response`: Encapsula DicionarioPagamento para validação
- `DebitarCreditarContaRequest/Response`: Encapsula DicionarioPagamento para débito/crédito
- `NotificarPagamentoSITPRequest/Response`: Encapsula DicionarioPagamento para notificação SITP
- `NotificarPagamentoPGFTRequest/Response`: Encapsula DicionarioPagamento para notificação PGFT
- `NotificarPagamentoSPAG`: Contém apenas o número do protocolo para notificação
- `TratarOcorrenciasRequest/Response`: Encapsula DicionarioPagamento para tratamento de ocorrências
- `SituacaoPagamento`: Representa a situação do lançamento (status, ocorrências)
- `CircuitBreak`: Indica se circuit breaker está ativo
- `Ocorrencia`: Representa uma ocorrência de erro

**Enums**:
- `TipoContaEnum`: Tipos de conta (CC, PP, CI, IF, etc)
- `TipoDocumentoEnum`: Tipo de documento (C=Crédito, D=Débito)
- `StatusLancamentoEnum`: Status do lançamento (CONFIRMADO=3, ERRO_PROCESSAMENTO=99)

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Descrição |
|-----------------|----------|-------------------------|-----------|
| `logback-spring.xml` | Leitura | `/usr/etc/log` (runtime) | Configuração de logs da aplicação |
| `application.yml` | Leitura | `src/main/resources` | Configurações da aplicação |
| `application-local.yml` | Leitura | `src/main/resources` | Configurações para ambiente local |

---

## 10. Filas Lidas

| Nome da Fila | Tecnologia | Classe Consumidora | Descrição |
|--------------|------------|-------------------|-----------|
| `QL.SPAG.SOLICITAR_PAGAMENTO_CC_REQ.INT` | IBM MQ | `TransferenciaTefListener` | Fila de entrada para solicitações de pagamento TEF |

---

## 11. Filas Geradas

| Nome da Fila/Exchange | Tecnologia | Classe Produtora | Descrição |
|-----------------------|------------|------------------|-----------|
| `events.business.notificationService` (exchange) | RabbitMQ | `NotificarPagamentoSPAGRepositoryImpl` | Exchange para notificações ao sistema SPAG |
| Routing Key: `SPAG.rk.notificationService` | RabbitMQ | `NotificarPagamentoSPAGRepositoryImpl` | Routing key para notificações SPAG |

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **atom-validar-pagamento** | REST | Serviço de validação de pagamentos (endpoint: `/spag-base-validar-pagamento-rs/v1/atacado/pagamentos/validarPagamento/`) |
| **atom-debitar-creditar-conta** | REST | Serviço de débito/crédito em conta (endpoints: `/nccs-base-debitar-creditar-conta-rs/v1/atacado/pagamentos/debitarCreditarConta` e `/estornarPagamento`) |
| **atom-notificar-pagamento-sitp** | REST | Serviço de notificação ao sistema SITP (endpoint: `/sitp-base-notificar-pagamento-sitp-rs/v1/atacado/pagamentos/notificarPagamentoSITP`) |
| **atom-notificar-pagamento-pgft** | REST | Serviço de notificação ao sistema PGFT (endpoint: `/pgft-base-notificar-pagamento-pgft-rs/v1/atacado/pagamentos/notificarPagamentoPGFT`) |
| **atom-tratar-ocorrencias** | REST | Serviço de tratamento de ocorrências (endpoint: `/spag-base-tratar-ocorrencias-rs/v1/atacado/pagamentos/tratarOcorrencias`) |
| **atom-atualizar-situacao-spag** | REST | Serviço de atualização de situação do lançamento (endpoint: `/v1/atualizarSituacaoLancamento`) |
| **atom-integrar-pagamento** | REST | Serviço de verificação de circuit breaker (endpoints: `/circuit-break/` e `/circuit-break/double-check`) |
| **IBM MQ** | Mensageria | Fila de entrada para recebimento de solicitações de pagamento |
| **RabbitMQ** | Mensageria | Fila de saída para notificações ao sistema SPAG |
| **API Gateway** | OAuth2 | Autenticação e autorização via JWT |
| **ConfigCat** | Feature Toggle | Controle de features e configurações dinâmicas |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (application, domain, common)
- Uso adequado de padrões como Repository, Mapper e Service
- Implementação de circuit breaker e retry com backoff
- Tratamento de erros com estorno automático
- Uso de Apache Camel para orquestração complexa de fluxos
- Testes unitários presentes para a maioria das classes
- Configuração externalizada e suporte a múltiplos ambientes
- Uso de Lombok para reduzir boilerplate

**Pontos de Melhoria:**
- Código com alguns comentários em português misturados com inglês
- Algumas classes com responsabilidades muito amplas (ex: `TransferenciaTefRouter` com muitas rotas)
- Uso de `simple()` do Camel com strings hardcoded em vez de constantes
- Falta de documentação JavaDoc em várias classes
- Alguns métodos longos que poderiam ser refatorados
- Testes de integração comentados (ex: `EstornoProcessorTest`)
- Configuração de retry hardcoded (3 tentativas, 15s) poderia ser externalizada
- Uso de `@SuppressWarnings("java:S1874")` na classe Application sem justificativa clara

---

## 14. Observações Relevantes

1. **Arquitetura Multi-módulo**: O projeto está organizado em 3 módulos Maven (application, domain, common), seguindo boas práticas de separação de responsabilidades.

2. **Orquestração com Camel**: O uso de Apache Camel permite uma orquestração declarativa e visual dos fluxos de processamento, facilitando manutenção e evolução.

3. **Resiliência**: O sistema implementa múltiplos mecanismos de resiliência:
   - Circuit breaker para evitar sobrecarga de sistemas externos
   - Retry automático com backoff exponencial
   - Estorno automático em caso de falha
   - Double-check no circuit breaker

4. **Mensageria Híbrida**: Utiliza IBM MQ para entrada (integração com sistemas legados) e RabbitMQ para saída (arquitetura moderna baseada em eventos).

5. **Feature Toggle**: Integração com ConfigCat permite ativar/desativar funcionalidades sem deploy, incluindo controle dinâmico de concorrência do listener JMS.

6. **Segurança**: Implementa autenticação OAuth2/JWT via API Gateway, com suporte a Basic Auth para alguns serviços legados.

7. **Observabilidade**: Integração com Prometheus/Grafana para métricas, Spring Actuator para health checks, e logging estruturado.

8. **Infraestrutura como Código**: Arquivo `infra.yml` define toda a configuração de deployment em Kubernetes/OpenShift.

9. **Processamento Assíncrono**: As notificações aos sistemas legados (SITP, PGFT) são processadas de forma assíncrona, melhorando performance.

10. **Tratamento de XML**: O listener JMS faz parsing de XML SOAP, removendo namespaces e caracteres inválidos antes de deserializar para `DicionarioPagamento`.