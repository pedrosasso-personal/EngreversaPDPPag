# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-spag-base-orch-solicitacao-bjud** é um serviço de orquestração desenvolvido em Spring Boot que processa solicitações de bloqueio judicial (BJUD). Sua principal função é buscar registros de solicitações de bloqueio de contas que ainda não possuem endereço cadastrado e enviá-los para processamento através de filas RabbitMQ. O sistema atua como um orquestrador que integra o serviço de bloqueio de contas (atom-bloqueio-conta) com o processamento assíncrono de endereços via mensageria.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application.java` | Classe principal que inicializa a aplicação Spring Boot |
| `SolicitacaoBjudController.java` | Controller REST que expõe o endpoint para processar registros |
| `SolicitacaoBjudService.java` | Serviço de domínio que orquestra o processamento através do Apache Camel |
| `SolicitacaoBjudRouter.java` | Define as rotas do Apache Camel para processamento e envio para fila |
| `BloqueioContaRepositoryImpl.java` | Implementação do repositório que consome API do atom-bloqueio-conta |
| `FilaRabbitRepositoryImpl.java` | Implementação do repositório que publica mensagens no RabbitMQ |
| `CamelContextWrapper.java` | Wrapper para gerenciar o contexto do Apache Camel |
| `SolicitacaoRegistro.java` | Entidade de domínio representando um registro de solicitação |
| `RabbitMQConfiguration.java` | Configuração do RabbitMQ (conexão, filas, exchanges) |
| `ExceptionHandler.java` | Tratamento centralizado de exceções |

## 3. Tecnologias Utilizadas

- **Spring Boot** (framework principal)
- **Apache Camel 3.0.1** (orquestração e integração)
- **RabbitMQ** (mensageria assíncrona)
- **Spring AMQP** (integração com RabbitMQ)
- **Swagger/OpenAPI 2.9.2** (documentação de APIs)
- **ModelMapper 2.3.7** (mapeamento de objetos)
- **Lombok** (redução de boilerplate)
- **Spring Actuator** (monitoramento e métricas)
- **Micrometer/Prometheus** (métricas customizadas)
- **RestTemplate** (cliente HTTP)
- **JUnit 5** (testes unitários)
- **Rest Assured** (testes funcionais)
- **Pact** (testes de contrato)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Java 11** (linguagem)

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/processar-registros` | `SolicitacaoBjudController` | Processa registros de ordem judicial sem endereço, buscando-os e enviando para fila RabbitMQ |

## 5. Principais Regras de Negócio

1. **Busca de Registros Sem Endereço**: O sistema busca registros de solicitações de bloqueio judicial que ainda não possuem endereço cadastrado através da integração com o serviço atom-bloqueio-conta.

2. **Processamento Assíncrono**: Cada registro encontrado é enviado individualmente para uma fila RabbitMQ para processamento posterior de endereços.

3. **Orquestração via Camel**: Utiliza Apache Camel para orquestrar o fluxo: buscar registros → dividir em mensagens individuais → enviar para fila.

4. **Tratamento de Erros**: Implementa tratamento customizado de erros com rejeição de mensagens (AmqpRejectAndDontRequeueException) em caso de falha no processamento.

5. **Processamento em Lote**: Embora processe registros individualmente na fila, a busca inicial retorna um array de registros que são divididos (split) pelo Camel.

## 6. Relação entre Entidades

**SolicitacaoRegistro** (Entidade Principal):
- `id` (Integer): Identificador único do registro
- `numeroDocumento` (String): Número do documento (CPF/CNPJ)
- `nuConta` (String): Número da conta

**SolicitacaoBjudRepresentation** (Representação para API):
- `id` (String): Identificador
- `version` (Integer): Versão do registro

**Relacionamentos**: As entidades são simples DTOs sem relacionamentos complexos. O sistema trabalha principalmente com transferência de dados entre serviços.

## 7. Estruturas de Banco de Dados Lidas

não se aplica

*Observação: O sistema não acessa diretamente banco de dados. Ele consome dados através de APIs REST de outros serviços.*

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

*Observação: O sistema não realiza operações diretas em banco de dados. Apenas consome e publica mensagens.*

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `application.yml` | Leitura | Spring Boot (startup) | Arquivo de configuração da aplicação com propriedades de ambiente |
| `logback-spring.xml` | Leitura | Logback (logging) | Configuração de logs da aplicação |
| `sboot-spag-base-orch-solicitacao-bjud.yml` | Leitura | Swagger Codegen | Especificação OpenAPI para geração de código |
| `prometheus.yml` | Leitura | Prometheus (métricas) | Configuração do Prometheus para coleta de métricas |
| `grafana.ini` | Leitura | Grafana (visualização) | Configuração do Grafana para dashboards |
| `rabbitmq_definitions.json` | Leitura | RabbitMQ (startup) | Definições de filas, exchanges e bindings do RabbitMQ |

## 10. Filas Lidas

não se aplica

*Observação: O sistema não consome mensagens de filas RabbitMQ, apenas publica.*

## 11. Filas Geradas

**Exchange**: `events.business.processarEnderecosBjud`
**Routing Key**: `SPAG.processarEnderecosBjud.v1`
**Tipo**: Direct Exchange
**Descrição**: Fila para onde são enviados os registros de solicitação de bloqueio judicial que necessitam processamento de endereço. Cada registro é publicado individualmente nesta fila.

**Classe Responsável**: `FilaRabbitRepositoryImpl.enviarParaProcessarEnderecos()`

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **sboot-spag-base-atom-bloqueio-conta** | API REST | Serviço que fornece registros de solicitações de bloqueio sem endereço através do endpoint `/v1/registros-sem-endereco` |
| **RabbitMQ** | Mensageria | Sistema de filas para processamento assíncrono de mensagens |
| **Prometheus** | Monitoramento | Coleta de métricas da aplicação através do endpoint `/actuator/prometheus` |

**URLs por Ambiente**:
- DES: `http://sboot-spag-base-atom-bloqueio-conta.des-spag-base.svc.cluster.local:8080`
- QA: `http://sboot-spag-base-atom-bloqueio-conta.qa-spag-base.svc.cluster.local:8080`
- UAT: `http://sboot-spag-base-atom-bloqueio-conta.uat-spag-base.svc.cluster.local:8080`
- PRD: `http://sboot-spag-base-atom-bloqueio-conta.prd-spag-base.svc.cluster.local:8080`

## 13. Avaliação da Qualidade do Código

**Nota: 7.5/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (domain, application, common)
- Uso adequado de padrões como Repository e Service
- Implementação de testes unitários, integração e funcionais
- Configuração adequada de logs e métricas
- Uso de Lombok para reduzir boilerplate
- Documentação OpenAPI/Swagger bem estruturada
- Uso de Apache Camel para orquestração, facilitando manutenção de fluxos

**Pontos de Melhoria:**
- Presença de código deprecated (construtor vazio em `SolicitacaoBjudRepresentation`)
- Tratamento de exceções genérico em alguns pontos (catch Exception)
- Falta de validações de entrada nos endpoints
- Ausência de circuit breaker para chamadas externas
- Configuração de segurança JWT presente mas não totalmente implementada
- Alguns testes vazios ou com implementação mínima
- Falta de documentação inline em algumas classes complexas
- Método `setAtomBloqueioContaUrl` público no repositório (usado apenas para testes)

O código demonstra boas práticas de desenvolvimento, mas há espaço para melhorias em robustez, tratamento de erros e cobertura de testes.

## 14. Observações Relevantes

1. **Arquitetura Modular**: O projeto segue uma estrutura modular clara com separação entre `application`, `domain` e `common`, facilitando manutenção e evolução.

2. **Orquestração com Camel**: O uso do Apache Camel para orquestração é uma escolha interessante que permite fácil visualização e manutenção dos fluxos de integração.

3. **Ambientes Kubernetes**: A aplicação está preparada para deploy em Kubernetes/OpenShift, com configurações específicas por ambiente (DES, QA, UAT, PRD).

4. **Observabilidade**: Boa implementação de observabilidade com Actuator, Prometheus e Grafana configurados.

5. **Segurança**: Implementa autenticação JWT através do framework de segurança do Banco Votorantim (bv-security-jwt).

6. **Processamento Assíncrono**: O padrão de processamento assíncrono via RabbitMQ permite escalabilidade e desacoplamento entre componentes.

7. **Versionamento de API**: Utiliza versionamento na URL (`/v1/`) seguindo boas práticas REST.

8. **Configuração por Perfil**: Suporta múltiplos perfis Spring (local, des, qa, uat, prd) com configurações específicas.

9. **Testes de Contrato**: Implementa testes de contrato com Pact, garantindo compatibilidade entre serviços.

10. **Limitação de Concorrência**: Configurado com apenas 1 consumidor concorrente no RabbitMQ, o que pode ser um gargalo em cenários de alta demanda.