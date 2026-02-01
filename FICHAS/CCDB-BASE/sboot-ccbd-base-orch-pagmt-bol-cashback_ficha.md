---
## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema **sboot-ccbd-base-orch-pagmt-bol-cashback** é um orquestrador de pagamentos de boletos utilizando saldo de cashback. Trata-se de uma aplicação Spring Boot que processa mensagens de filas RabbitMQ para realizar pagamentos de boletos com cashback, estornos e transferências bancárias. O sistema integra-se com diversos serviços externos para validar adesão ao cashback, recuperar dados de pagamento, efetuar pagamentos e atualizar status de transações.

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal de inicialização da aplicação Spring Boot |
| `PagmtBolCashbackService` | Serviço de domínio que orquestra os fluxos de pagamento e estorno de cashback |
| `EventListener` | Listener de eventos RabbitMQ que recebe mensagens de sucesso e erro de pagamentos |
| `CamelContextWrapper` | Wrapper do contexto Apache Camel para gerenciar rotas de processamento |
| `PagmtBolCashbackRouter` | Rota principal do Camel que define o fluxo de pagamento com cashback |
| `EstornoPagamentoRouter` | Rota do Camel para processar estornos de pagamento |
| `EstornoTransferenciaRouter` | Rota do Camel para processar estornos de transferência |
| `PagamentoBoletoRouter` | Rota do Camel para efetuar pagamento de boleto |
| `EstornoCashbackRouter` | Rota do Camel para definir fluxo de estorno de cashback |
| Diversos `*RepositoryImpl` | Implementações de repositórios para integração com APIs externas |
| Diversos `*Processor` | Processadores Camel para transformação de dados entre etapas |
| Diversos `*Builder` | Builders para construção de objetos de domínio |

### 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Apache Camel 3.0.1** (orquestração de fluxos)
- **RabbitMQ** (mensageria)
- **Spring AMQP** (integração com RabbitMQ)
- **Resilience4j** (retry e circuit breaker)
- **Swagger/OpenAPI** (documentação de APIs)
- **Springfox 3.0.0** (geração de documentação)
- **Prometheus/Micrometer** (métricas)
- **Grafana** (visualização de métricas)
- **Logback** (logging)
- **Lombok** (redução de boilerplate)
- **RestTemplate** (cliente HTTP)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **OpenShift/Kubernetes** (orquestração de containers)

### 4. Principais Endpoints REST

Não se aplica. O sistema não expõe endpoints REST públicos, funcionando primariamente como consumidor de mensagens de filas RabbitMQ. Possui apenas endpoints do Spring Actuator para monitoramento (health, metrics, prometheus).

### 5. Principais Regras de Negócio

1. **Validação de Adesão ao Cashback**: Verifica se o cliente possui adesão ativa ao programa de cashback antes de processar pagamentos
2. **Identificação de Operação**: Identifica o tipo de operação (pagamento de boleto ou transferência) através do protocolo
3. **Processamento Condicional**: Processa pagamentos apenas para entidades liquidantes específicas (código 1 para transferência ou 22 para pagamento de boleto)
4. **Fluxo de Pagamento**: Recupera dados do boleto, valida adesão, efetua pagamento e atualiza status
5. **Fluxo de Estorno**: Busca saldo de cashback, devolve valor ao banco via transferência, atualiza status do boleto e estorna cashback
6. **Geração de Protocolo**: Gera protocolo único em Base64 para rastreamento de transações
7. **Atualização de Status**: Atualiza status de protocolos de pagamento, boletos e transferências conforme resultado das operações
8. **Retry com Backoff Exponencial**: Implementa retry automático com backoff exponencial para chamadas a serviços externos
9. **Tratamento de Protocolos Não Identificados**: Ignora protocolos que não podem ser identificados após tentativas de retry

### 6. Relação entre Entidades

**Entidades Principais:**

- **TransferenciaMensagem**: Mensagem recebida da fila contendo dados da transferência/pagamento
- **DadosPagamentoResponse**: Dados completos do pagamento incluindo CPF, conta, valores e linha digitável
- **EfetuarPagmtoBolRequest/Response**: Request/Response para efetivação de pagamento de boleto
- **TransferenciaRequest/Response**: Request/Response para transferência bancária
- **AdesaoCashbackResponse**: Dados de adesão do cliente ao programa cashback
- **DadosOperacaoIdentificadaResponse**: Identificação do tipo de operação (pagamento ou transferência)
- **Remetente/Favorecido/Participante**: Dados das partes envolvidas nas transações
- **Protocolo**: Informações de protocolo de transação com status e possíveis erros

**Relacionamentos:**
- TransferenciaMensagem → DadosPagamentoResponse (1:1)
- DadosPagamentoResponse → Remetente (1:1)
- DadosPagamentoResponse → Favorecido (1:1)
- EfetuarPagmtoBolRequest → Protocolo (1:1)
- TransferenciaRequest → Participante (1:2 - remetente e favorecido)

### 7. Estruturas de Banco de Dados Lidas

Não se aplica. O sistema não acessa diretamente banco de dados, realizando todas as operações através de APIs REST de outros microserviços.

### 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema não acessa diretamente banco de dados, realizando todas as operações através de APIs REST de outros microserviços.

### 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | leitura | /usr/etc/log | Arquivo de configuração de logs montado via ConfigMap |
| application.yml | leitura | classpath | Arquivo de configuração da aplicação Spring Boot |
| prometheus.yml | leitura | metrics/ | Configuração do Prometheus para coleta de métricas (ambiente local) |
| grafana.ini | leitura | metrics/ | Configuração do Grafana (ambiente local) |

### 10. Filas Lidas

**Filas RabbitMQ consumidas:**

1. **events.business.CCBD-BASE.retornoPagmtoCabkSucesso**
   - Exchange: events.business.retornoPagamentoSucessoOK
   - Routing Key: CCBD.retornoPagamentoSucessoOK.91
   - Descrição: Recebe mensagens de sucesso de pagamentos para processar cashback

2. **events.business.CCBD-BASE.retornoPagmtoCabkErro**
   - Exchange: events.business.retornoPagamentoErro
   - Routing Key: CCBD.retornoPagamentoErro.91
   - Descrição: Recebe mensagens de erro de pagamentos para processar estornos

### 11. Filas Geradas

**Filas RabbitMQ publicadas:**

1. **events.business.CCBD-BASE.retornoPagmtoCabkSucesso**
   - Exchange: events.business.retornoPagmtoCabkSucesso
   - Routing Key: CCBD.retornoPagmtoCabkSucesso.91
   - Descrição: Publica eventos de sucesso no processamento de cashback

2. **events.business.CCBD-BASE.retornoPagmtoCabkErro**
   - Exchange: events.business.retornoPagmtoCabkErro
   - Routing Key: CCBD.retornoPagmtoCabkErro.91
   - Descrição: Publica eventos de erro no processamento de cashback

### 12. Integrações Externas

| Sistema/API | Descrição | Operação |
|-------------|-----------|----------|
| sboot-spag-base-orch-pagamento-boleto-srv | Orquestrador de pagamento de boletos | POST - Efetuar pagamento de boleto |
| sboot-spag-base-orch-transferencias | Orquestrador de transferências bancárias | POST - Efetuar transferência bancária |
| sboot-cabk-base-atom-cashback | Serviço atômico de cashback | GET/POST - Consultar adesão, recuperar dados, atualizar status, identificar operação |
| sboot-cabk-base-atom-calculo-cashback | Serviço de cálculo de cashback | POST - Atualizar e estornar saldo de cashback |
| sboot-spag-base-atom-pagamento | Serviço atômico de pagamento | GET - Recuperar dados detalhados de pagamento |
| API Gateway OAuth | Gateway de autenticação | POST - Obter token JWT para autenticação |

**Endpoints específicos integrados:**
- `/v1/pagamento-boleto` - Pagamento de boleto
- `/v1/transferencia` - Transferência bancária
- `/v1/cashback/atualiza/status/protocolo` - Atualizar status de protocolo
- `/v1/cashback/recupera/dados/pagamento` - Recuperar dados de pagamento
- `/v1/cashback/atualiza/status/pagamento` - Atualizar status de pagamento
- `/v1/cashback/identifica/operacao/protocolo/{nuProtocolo}` - Identificar operação
- `/v1/cashback/consulta/saldo/{nuCpf}` - Consultar saldo
- `/v1/cashback/atualiza/status/boleto` - Atualizar status de boleto
- `/v1/cashback/atualizar/saldo` - Atualizar saldo
- `/v1/cashback/estorna/resgate/boleto/{nuProtocoloTransferencia}` - Estornar resgate
- `/v1/cashback/consulta/adesao/{nuCpf}` - Consultar adesão
- `/v1/pagamento/detalhado/{nuProtocolo}` - Recuperar dados detalhados

### 13. Avaliação da Qualidade do Código

**Nota: 7.5/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (application, domain, common)
- Uso adequado de padrões como Builder, Repository e Processor
- Implementação de retry com Resilience4j para resiliência
- Uso de Apache Camel para orquestração de fluxos complexos de forma declarativa
- Configuração externalizada e parametrizada por ambiente
- Uso de Lombok para redução de boilerplate
- Implementação de observabilidade com Prometheus/Grafana
- Documentação via Swagger/OpenAPI
- Estrutura de testes organizada (unit, integration, functional)

**Pontos de Melhoria:**
- Falta de documentação JavaDoc em classes e métodos importantes
- Constantes hardcoded em algumas classes (ex: códigos de banco, tipos de transação)
- Tratamento de exceções genérico em alguns pontos, podendo ser mais específico
- Logs poderiam ser mais estruturados e padronizados
- Falta de validação de entrada em alguns pontos
- Alguns métodos muito longos que poderiam ser refatorados
- Uso de classes utilitárias com métodos estáticos que dificultam testes
- Acoplamento com RestTemplate (poderia usar WebClient para programação reativa)
- Falta de circuit breaker configurado (apenas retry)

### 14. Observações Relevantes

1. **Arquitetura Orientada a Eventos**: O sistema é totalmente orientado a eventos, consumindo mensagens de filas RabbitMQ e processando de forma assíncrona

2. **Apache Camel**: Uso extensivo do Apache Camel para orquestração de fluxos complexos com múltiplas etapas e decisões condicionais

3. **Resiliência**: Implementa retry com backoff exponencial para chamadas a serviços externos, mas poderia se beneficiar de circuit breaker

4. **Segurança**: Utiliza OAuth2 com JWT para autenticação nas chamadas a APIs externas via API Gateway

5. **Observabilidade**: Bem instrumentado com métricas Prometheus e dashboards Grafana pré-configurados

6. **Multi-ambiente**: Configuração preparada para múltiplos ambientes (local, des, qa, uat, prd) com variáveis específicas

7. **Containerização**: Preparado para execução em containers Docker e deploy em OpenShift/Kubernetes

8. **Processamento Condicional**: Filtra mensagens por entidade liquidante antes de processar, evitando processamento desnecessário

9. **Geração de Protocolo**: Implementa geração própria de protocolo em Base64 para rastreamento único de transações

10. **Fallback em Identificação**: Possui fallback para ignorar protocolos não identificados após tentativas de retry, evitando bloqueio do processamento

11. **Separação de Fluxos**: Fluxos de pagamento e estorno bem separados em rotas Camel distintas, facilitando manutenção

12. **Integração com Múltiplos Serviços**: Integra-se com diversos microserviços (pagamento, transferência, cashback) orquestrando operações complexas