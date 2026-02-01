# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema orquestrador de pagamentos de tributos desenvolvido em Spring Boot. O sistema é responsável por processar solicitações e liberações de pagamentos de tributos, integrando-se com diversos sistemas legados e serviços externos. Utiliza filas IBM MQ para receber solicitações e Apache Camel para orquestração dos fluxos de processamento. O sistema implementa validações, movimentações de conta, preparação de pagamentos, efetivação e confirmação, além de notificações para sistemas integrados (SPAG, SITP, PGFT).

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal de inicialização da aplicação Spring Boot |
| `PagamentoTributoService` | Serviço de domínio que processa solicitações e liberações de pagamento |
| `PagamentoTributoController` | Controlador REST para endpoints de solicitação e liberação de pagamento |
| `PagamentoTributoRouter` | Roteador Apache Camel que define o fluxo completo de processamento |
| `CircuitBreakRouter` | Roteador para validação de circuit break antes do processamento |
| `PagamentoTributoListner` | Listener JMS para consumo de mensagens das filas IBM MQ |
| `PagamentoTributoRepositoryImpl` | Implementação de validação de pagamento |
| `ConsultaIS2BRepositoryImpl` | Implementação de consulta ao sistema IS2B |
| `MovimentarContaRepositoryImpl` | Implementação de débito/crédito e estorno de conta |
| `PreparaPagamentoRepositoryImpl` | Implementação de preparação de pagamento |
| `EfetuarPagamentoTributoRepositoryImpl` | Implementação de efetivação de pagamento |
| `ConfirmarPagamentoTributoRepositoryImpl` | Implementação de confirmação de pagamento |
| `NotificarSPAGRepositoryImpl` | Implementação de notificação ao sistema SPAG |
| `NotificarSITPRepositoryImpl` | Implementação de notificação ao sistema SITP |
| `NotificarPGFTRepositoryImpl` | Implementação de notificação ao sistema PGFT |
| `PagamentoSpagRepositoryImpl` | Implementação de consulta e atualização no sistema SPAG |
| `IntegrarPagamentoRepositoryImpl` | Implementação de validação de circuit break |
| `TratarOcorrenciasRepositoryImpl` | Implementação de tratamento de ocorrências |

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Apache Camel 3.2.0** (orquestração de fluxos)
- **IBM MQ 2.3.1** (mensageria)
- **Spring Security OAuth2** (autenticação e autorização)
- **Micrometer + Prometheus** (métricas)
- **Grafana** (visualização de métricas)
- **Swagger/OpenAPI 3.0.0** (documentação de API)
- **Logback** (logging)
- **JUnit 5** (testes unitários)
- **Mockito 4.7.0** (mocks para testes)
- **RestAssured** (testes de API)
- **Pact** (testes de contrato)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Lombok** (redução de boilerplate)
- **HikariCP** (pool de conexões)

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/pagamento-tributo/solicitacao` | `PagamentoTributoController` | Processa solicitação de pagamento de tributo |
| GET | `/v1/pagamento-tributo/liberacao/{protocolo}` | `PagamentoTributoController` | Processa liberação de pagamento pelo protocolo |
| GET | `/actuator/health` | Spring Actuator | Verifica saúde da aplicação |
| GET | `/actuator/prometheus` | Spring Actuator | Expõe métricas para Prometheus |
| GET | `/swagger-ui.html` | Swagger UI | Documentação interativa da API |

## 5. Principais Regras de Negócio

1. **Validação de Circuit Break**: Antes de processar qualquer pagamento, o sistema valida se há circuit break ativo para o banco/tipo de lançamento. Se ativo, o pagamento é rejeitado e estornado.

2. **Validação de Pagamento**: Verifica se a solicitação de pagamento é válida através do serviço de validação (flRetornoValidaSolicitacaoPagto == 0).

3. **Consulta IS2B**: Consulta informações completas do tributo no sistema IS2B antes de prosseguir.

4. **Movimentação de Conta**: Realiza débito na conta do remetente antes de efetivar o pagamento.

5. **Preparação de Pagamento**: Prepara o pagamento no sistema antes da efetivação.

6. **Efetivação de Pagamento**: Efetiva o pagamento do tributo no sistema correspondente.

7. **Confirmação de Pagamento**: Confirma a efetivação do pagamento.

8. **Atualização de Favorecido**: Atualiza dados do favorecido no sistema SPAG.

9. **Notificações**: Notifica sistemas integrados (SPAG, SITP, PGFT) sobre o resultado do processamento.

10. **Tratamento de Erros**: Em caso de erro em qualquer etapa, realiza estorno da movimentação de conta, trata ocorrências e notifica o SPAG.

11. **Retry com Redelivery**: Implementa retry automático com 3 tentativas e delay de 15 segundos entre tentativas.

## 6. Relação entre Entidades

**Entidade Principal:**
- `DicionarioPagamento`: Estrutura de dados que trafega por todo o fluxo contendo informações do pagamento (remetente, favorecido, valores, códigos, datas, ocorrências, etc.)

**Entidades de Suporte:**
- `PagamentoTributo`: Entidade de domínio com id e version
- `CircuitBreak`: Entidade que representa o estado do circuit break
- `ListaOcorrencia`: Lista de ocorrências associadas ao pagamento
- `OcorrenciaDTO`: Detalhes de uma ocorrência (código, descrição, erro original)

**Relacionamentos:**
- `DicionarioPagamento` contém `ListaOcorrencia`
- `ListaOcorrencia` contém lista de `OcorrenciaDTO`
- O fluxo de processamento transforma e enriquece o `DicionarioPagamento` em cada etapa

## 7. Estruturas de Banco de Dados Lidas

não se aplica

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação (leitura/gravação) | Local/Classe Responsável | Breve Descrição |
|-----------------|----------------------------|-------------------------|-----------------|
| `logback-spring.xml` | leitura | Configuração de logging | Arquivo de configuração do Logback para logs da aplicação |
| `application.yml` | leitura | Spring Boot | Arquivo de configuração principal da aplicação |
| `application-local.yml` | leitura | Spring Boot | Arquivo de configuração para ambiente local |

## 10. Filas Lidas

- **QL.SPAG.SOLICITAR_PAGAMENTO_TRIBUTO_REQ.INT**: Fila IBM MQ para receber solicitações de pagamento de tributo. Consumida pelo listener `PagamentoTributoListner.listenerSolicitarPagamentoTributo()`.

- **QL.SPAG.LIBERAR_PAGAMENTO_TRIBUTO_REQ.INT**: Fila IBM MQ para receber liberações de pagamento de tributo. Consumida pelo listener `PagamentoTributoListner.listenerLiberarPagamentoTributo()`.

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

| Sistema | Tipo | Descrição |
|---------|------|-----------|
| **Serviço de Validação de Pagamento** | REST API | Valida solicitações de pagamento (endpoint: `/spag-base-validar-pagamento-rs/v1/atacado/pagamentos/validarPagamento/`) |
| **IS2B** | REST API | Consulta informações completas do tributo (endpoint: `/spag-base-consultar-servico-pagamento-tributo-rs/v1/atacado/pagamentos/consultarServPagamentoTributo/`) |
| **NCCS - Movimentação de Conta** | REST API | Realiza débito/crédito e estorno de conta (endpoints: `/nccs-base-debitar-creditar-conta-rs/v1/atacado/pagamentos/debitarCreditarConta` e `/estornarPagamento`) |
| **Serviço de Preparação de Pagamento** | REST API | Prepara pagamento de tributo (endpoint: `/spag-base-prepara-pagamento-tributo-rs/v1/atacado/pagamentos/preparaPagamentoTributo`) |
| **Serviço de Efetivação de Pagamento** | REST API | Efetiva pagamento de tributo (endpoint: `/spag-base-efetuar-servico-pagamento-tributo-rs/v1/atacado/pagamentos/efetuarServicoPagamento`) |
| **Serviço de Confirmação de Pagamento** | REST API | Confirma pagamento de tributo (endpoint: `/spag-base-confirmar-pagamento-tributo-consumo-rs/v1/atacado/pagamentos/confirmarPagamento`) |
| **SPAG - Atom Pagamento** | REST API | Consulta protocolo e atualiza favorecido (endpoints: `/v1/pagamento/protocoloTransacao/{protocoloTransacaoPagamento}` e `/v1/atualizarFavorecido`) |
| **SPAG - Notificação** | REST API | Notifica resultado do pagamento ao SPAG (endpoint: `/spag-base-notifica-pagamento-rs/v1/atacado/pagamentos/notificarPagamentoSPAG`) |
| **SITP** | REST API | Notifica pagamento ao SITP (endpoint: `/sitp-base-notificar-pagamento-sitp-rs/v1/atacado/pagamentos/notificarPagamentoSITP`) |
| **PGFT** | REST API | Notifica pagamento ao PGFT (endpoint: `/pgft-base-notificar-pagamento-pgft-rs/v1/atacado/pagamentos/notificarPagamentoPGFT`) |
| **Serviço de Tratamento de Ocorrências** | REST API | Trata ocorrências de pagamento (endpoint: `/spag-base-tratar-ocorrencias-rs/v1/atacado/pagamentos/tratarOcorrencias`) |
| **Atom Integrar Pagamento** | REST API | Valida circuit break (endpoints: `/circuit-break/` e `/circuit-break/double-check`) |
| **API Gateway OAuth** | OAuth2 | Autenticação e autorização via JWT (endpoint: `/auth/oauth/v2/token-jwt`) |
| **IBM MQ** | Mensageria | Consumo de mensagens de solicitação e liberação de pagamento |

## 13. Avaliação da Qualidade do Código

**Nota:** 7.5/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (application, domain, common)
- Uso adequado de padrões como Repository, Service e Controller
- Implementação de circuit breaker para resiliência
- Tratamento de exceções centralizado com retry automático
- Uso de Apache Camel para orquestração de fluxos complexos
- Configuração externalizada e suporte a múltiplos ambientes
- Cobertura de testes (unitários, integração e funcionais)
- Uso de Lombok para reduzir boilerplate
- Documentação com Swagger/OpenAPI
- Métricas e observabilidade com Prometheus/Grafana

**Pontos de Melhoria:**
- Falta de validação de entrada nos controllers (Bean Validation)
- Ausência de tratamento específico de timeouts nas chamadas REST
- Logs poderiam ser mais estruturados com MDC para rastreabilidade
- Falta de documentação inline em algumas classes complexas
- Alguns métodos poderiam ser quebrados em métodos menores para melhor legibilidade
- Ausência de cache para consultas repetitivas
- Configuração de segurança poderia ser mais restritiva
- Falta de testes de carga e performance documentados

## 14. Observações Relevantes

1. **Arquitetura Hexagonal**: O projeto segue princípios de arquitetura hexagonal com separação clara entre domínio, aplicação e infraestrutura através de ports e adapters.

2. **Orquestração com Camel**: O uso de Apache Camel permite uma orquestração declarativa e visual dos fluxos de pagamento, facilitando manutenção e evolução.

3. **Resiliência**: Implementa circuit breaker com double-check para evitar sobrecarga de sistemas integrados.

4. **Mensageria Assíncrona**: Utiliza IBM MQ para processamento assíncrono de solicitações, permitindo escalabilidade horizontal.

5. **Multithread Configurável**: A concorrência do listener JMS é configurável via feature toggle, permitindo ajuste dinâmico de capacidade.

6. **Estorno Automático**: Em caso de falha em qualquer etapa, o sistema automaticamente estorna a movimentação de conta e notifica os sistemas integrados.

7. **Ambientes Múltiplos**: Suporta configuração para ambientes local, des, qa, uat e prd com configurações específicas.

8. **Containerização**: Pronto para deploy em containers Docker e Kubernetes/OpenShift.

9. **Observabilidade**: Integração completa com stack de observabilidade (Prometheus, Grafana) com dashboards pré-configurados.

10. **Segurança**: Implementa OAuth2 com JWT para autenticação e autorização de requisições.

11. **Dependências Legadas**: Integra-se com sistemas legados via REST APIs hospedadas em WebSphere (WAS).

12. **Feature Toggle**: Utiliza ConfigCat para gerenciamento de features, permitindo ativação/desativação de funcionalidades sem deploy.