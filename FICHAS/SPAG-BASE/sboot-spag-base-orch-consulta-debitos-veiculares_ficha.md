# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema orquestrador responsável por consultar débitos veiculares (IPVA, multas, licenciamento, etc.) junto aos Detrans através da integração com a Celcoin. O sistema recebe solicitações de consulta de Fintechs parceiras, valida as informações, registra a consulta em banco de dados, busca os débitos na API da Celcoin e retorna o resultado. Também processa webhooks de atualização de status de consultas, notificando os parceiros via RabbitMQ e API de notificação. Utiliza cache Redis para otimizar consultas repetidas.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `ConsultaDebitosVeicularesController` | Controller REST que expõe endpoints para consulta de débitos e recebimento de webhooks |
| `ConsultaDebitosVeicularesService` | Serviço de domínio que orquestra o fluxo de consulta de débitos veiculares via Apache Camel |
| `ConsultarDebitosWebHookService` | Serviço de domínio que processa webhooks de atualização de consultas |
| `ConsultaDebitosVeicularesRouter` | Roteador Camel principal que orquestra o fluxo de validação e consulta |
| `ConsultaDebitosWebHookRouter` | Roteador Camel para processamento de webhooks |
| `CelcoinDebitosVeicularesRouter` | Roteador Camel para integração com API Celcoin |
| `ValidaDebitosVeicularesRouter` | Roteador Camel para validações (CNPJ, débitos, arrecadadores) |
| `RegistrarDebitosVeicularesRouter` | Roteador Camel para registro de consultas no banco |
| `ValidaEstadoRouter` | Roteador Camel para validação de UF |
| `ConsultaErroOcorrenciaRouter` | Roteador Camel para tratamento de erros e ocorrências |
| `CelcoinDebitosVeicularesRepositoryImpl` | Implementação de integração com API Celcoin (com cache Redis) |
| `ValidarDebitosVeicularesRepositoryImpl` | Implementação de validações (busca CNPJ, débitos, arrecadadores) |
| `RegistrarDebitosVeicularesRepositoryImpl` | Implementação de registro e atualização de consultas |
| `AtualizarDebitosWebHookRepositoryImpl` | Implementação de atualização de consultas via webhook |
| `AtualizarNotificationDebitosWebHookRepositoryImpl` | Implementação de envio de notificações para fila RabbitMQ |
| `CacheRepositoryImpl` | Implementação de cache usando Redis/Redisson |

---

## 3. Tecnologias Utilizadas

- **Framework Principal**: Spring Boot 2.x
- **Orquestração**: Apache Camel 3.0.1
- **Cache**: Redis (Redisson 3.17.0), Bucket4J (rate limiting)
- **Mensageria**: RabbitMQ (Spring AMQP)
- **Segurança**: Spring Security OAuth2, JWT
- **Documentação**: Swagger/OpenAPI (Springfox 3.0.0)
- **Mapeamento**: MapStruct 1.4.2
- **Monitoramento**: Spring Actuator, Micrometer, Prometheus, Grafana
- **Testes**: JUnit 5, Mockito, RestAssured, Pact (testes de contrato)
- **Build**: Maven
- **Containerização**: Docker
- **Linguagem**: Java 11
- **Lombok**: Para redução de boilerplate

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/consultar-debitos` | `ConsultaDebitosVeicularesController` | Consulta débitos veiculares nos Detrans via Celcoin |
| POST | `/v1/consultar-debitos/webhook` | `ConsultaDebitosVeicularesController` | Recebe webhook de atualização de status de consulta |

---

## 5. Principais Regras de Negócio

1. **Validação de Estado (UF)**: Verifica se o estado informado é válido e se é suportado pela Celcoin (lista específica de UFs)
2. **Validação de Fintech**: Busca e valida o CNPJ da Fintech através do clientId
3. **Verificação de Consulta Duplicada**: Verifica se já existe consulta com mesmo NSU (uniqueIdentifier) para evitar duplicidade
4. **Cache de Consultas**: Armazena consultas bem-sucedidas em cache Redis por 1 hora para otimizar consultas repetidas
5. **Registro de Consultas**: Todas as consultas são registradas no banco de dados com status e mensagens
6. **Tratamento de Erros**: Busca código de ocorrência de erro específico baseado no arrecadador e código de erro
7. **Notificação de Parceiros**: Envia notificações via RabbitMQ e API REST quando há atualização de status
8. **Validação de Arrecadadores**: Verifica se existe arrecadador ativo para processar a consulta
9. **Fluxo de Exceções**: Em caso de erro, registra a consulta com status de erro (99) e retorna código de ocorrência apropriado
10. **Webhook de Atualização**: Processa webhooks da Celcoin, atualiza status no banco e notifica parceiros

---

## 6. Relação entre Entidades

**Entidades de Domínio Principais:**

- **ConsultarDebitosVeicularesRequestDomain**: Representa requisição de consulta (state, licensePlate, renavam, cpfCnpj, uniqueIdentifier, clientId)
- **ConsultarDebitosVeicularesResponseDomain**: Resposta da consulta (status, protocol, acceptanceDateTime, effectiveDateTime, uniqueIdentifier)
- **Vehicle**: Dados do veículo (uf, document, licensePlate, renavam, debtsType, debts)
- **DebtDomain**: Representa um débito individual (id, amount, title, description, dueDate, expirationDate, hasDiscount, isExpired, type, year, required, dependsOn, distinct)
- **VehicleRequestDomain/VehicleResponseDomain**: Request/Response para API Celcoin
- **CriaDebitoVeicularRequestDomain**: Dados para inserção de consulta no banco
- **AtualizarDebitoVeicularRequestDomain**: Dados para atualização de consulta no banco
- **BuscaCnpjRequestDomain/ResponseDomain**: Busca CNPJ da Fintech
- **BuscaDebitoRequestDomain/ResponseDomain**: Busca consulta existente por NSU
- **ArrecadadorDomain**: Dados do arrecadador (cdArrecadador, nuCpfCnpj, nmRazaoSocial, flAtivo)
- **OcorrenciaErroDebitoVeicularRequestDomain/ResponseDomain**: Busca código de erro de ocorrência

**Relacionamentos:**
- ConsultarDebitosVeicularesRequestDomain → gera → CriaDebitoVeicularRequestDomain (registro no banco)
- ConsultarDebitosVeicularesRequestDomain → transforma → VehicleRequestDomain (chamada Celcoin)
- VehicleResponseDomain → gera → ConsultarDebitosVeicularesResponseDomain
- ConsultarDebitosWebHookRequestDomain → contém → Vehicle → contém → List<DebtDomain>
- ConsultarDebitosWebHookRequestDomain → gera → AtualizarDebitoVeicularRequestDomain

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TB_CONSULTA_DEBITO_VEICULAR | tabela | SELECT | Busca consultas de débitos veiculares existentes por CNPJ e NSU |
| TB_ARRECADADOR | tabela | SELECT | Busca arrecadadores ativos cadastrados |
| TB_FINTECH | tabela | SELECT | Busca CNPJ da Fintech através do clientId |
| TB_OCORRENCIA_ERRO_PAGAMENTO | tabela | SELECT | Busca código e mensagem de erro de ocorrência baseado em arrecadador e código de erro |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TB_CONSULTA_DEBITO_VEICULAR | tabela | INSERT | Insere nova consulta de débito veicular com status inicial |
| TB_CONSULTA_DEBITO_VEICULAR | tabela | UPDATE | Atualiza status da consulta (sucesso/erro) e dados do arrecadador |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot | Arquivo de configuração da aplicação (profiles, endpoints, credenciais) |
| logback-spring.xml | leitura | Logback | Configuração de logs da aplicação |
| swagger/*.yml | leitura | Swagger Codegen | Especificações OpenAPI para geração de clients e APIs |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Descrição |
|--------------|------------|-----------|
| events.business.notificationService (exchange) com routing key SPAG.rk.notificationService | RabbitMQ | Fila para notificação de resultado de consultas de débitos veiculares aos parceiros |

---

## 12. Integrações Externas

| Sistema/API | Tipo | Descrição |
|-------------|------|-----------|
| API Celcoin (vehicle-debts-search-celcoin) | REST | Consulta débitos veiculares nos Detrans através da Celcoin |
| sboot-spag-base-atom-valida-debitos-veiculares | REST | Valida CNPJ de Fintech, busca débitos e arrecadadores |
| sboot-spag-base-atom-registrar-debitos-veiculares | REST | Registra e atualiza consultas de débitos veiculares no banco |
| sboot-spag-base-orch-notificar-parceiro | REST | Notifica parceiros sobre resultado de consultas |
| API Gateway BV | OAuth2 | Autenticação e autorização via OAuth2 client credentials |
| Redis | Cache | Armazenamento em cache de consultas e rate limiting |
| RabbitMQ | Mensageria | Envio de notificações assíncronas |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (presentation, domain, infrastructure)
- Uso adequado de padrões como Repository, Mapper e Service
- Implementação de cache para otimização de performance
- Tratamento de exceções estruturado com exceções customizadas
- Uso de Apache Camel para orquestração de fluxos complexos
- Testes unitários presentes
- Configuração externalizada
- Uso de Lombok para redução de boilerplate

**Pontos de Melhoria:**
- Presença de TODOs no código indicando pendências (ex: tipos Integer para campos que deveriam ser String/Long)
- Alguns processadores Camel com lógica de negócio que poderia estar em services
- Comentários em português misturados com código
- Alguns métodos com muitos parâmetros (ex: `buildRequestObj` com 9+ parâmetros)
- Falta de validação de entrada em alguns pontos
- Tratamento genérico de exceções em alguns casos (catch Exception)
- Código de tratamento de erro duplicado em alguns repositórios
- Falta de documentação JavaDoc em classes de domínio
- Alguns nomes de variáveis poderiam ser mais descritivos

---

## 14. Observações Relevantes

1. **Arquitetura Baseada em Camel**: O sistema utiliza Apache Camel como motor de orquestração, com rotas bem definidas para cada fluxo de negócio
2. **Multi-módulo Maven**: Projeto dividido em módulos (application, domain, common) seguindo boas práticas de separação
3. **Cache Inteligente**: Implementa cache Redis com TTL de 1 hora, usando chave composta (state+licensePlate+renavam+cpfCnpj)
4. **Resiliência**: Implementa retry em caso de falha (maximumRedeliveries=2) e tratamento de exceções em múltiplos níveis
5. **Observabilidade**: Integração completa com Prometheus/Grafana para monitoramento de métricas (JVM, HTTP, HikariCP, logs)
6. **Segurança**: Utiliza OAuth2 com client credentials para autenticação em APIs externas
7. **Ambientes**: Suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas
8. **Validação de Estado**: Apenas alguns estados são suportados pela Celcoin (lista hardcoded no código)
9. **Fluxo Assíncrono**: Consulta é registrada imediatamente e resultado é notificado posteriormente via webhook
10. **Rate Limiting**: Utiliza Bucket4J com JCache para controle de taxa de requisições
11. **Auditoria**: Integração com trilha de auditoria BV (bv-arqt-base-trilha-auditoria-web)
12. **Testes de Contrato**: Implementa testes Pact para garantir compatibilidade de contratos entre serviços