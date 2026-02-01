# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-spag-base-orch-liquida-agendamento** é um orquestrador responsável por processar a liquidação de agendamentos de pagamentos. Ele consome mensagens de filas PubSub do Google Cloud contendo solicitações de execução de agendamentos e notificações de status de pagamento, realiza a conversão e enriquecimento dos dados, envia requisições para o serviço de transferências e publica o status final dos agendamentos em tópicos Kafka para o sistema SGAT (Sistema de Gestão de Agendamento de Transferências).

O sistema opera de forma reativa e assíncrona, utilizando Spring Boot com WebFlux, Google Cloud PubSub para mensageria de entrada e Apache Kafka para publicação de status. Implementa o padrão de arquitetura hexagonal (ports and adapters) com separação clara entre camadas de domínio, aplicação e infraestrutura.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal que inicializa a aplicação Spring Boot |
| **SettleSchedulingConsumerAdapter** | Adapter de entrada que consome mensagens de agendamento do PubSub |
| **NotifySchedulingStatusConsumerAdapter** | Adapter de entrada que consome notificações de status de pagamento do PubSub |
| **MessageConverter** | Converte mensagens do PubSub (bytes) para objetos de domínio (Transferencia) |
| **StatusAgendamentoSgatMapper** | Mapeia objetos de domínio para o formato Avro do SGAT |
| **SettleSchedulingUseCase** | Caso de uso que processa agendamentos e trata reagendamentos |
| **NotifySchedulingStatusUsecase** | Caso de uso que notifica status de agendamento |
| **FindAccountTypeUseCase** | Caso de uso que busca e cacheia tipos de conta |
| **SettleSchedulingAdapter** | Adapter de saída que envia transferências via WebClient |
| **SchedulingStatusProducer** | Adapter de saída que publica status no Kafka |
| **AccountTypeLookupAdapter** | Adapter de saída que consulta tipos de conta via API |
| **WebClientConfig** | Configuração do WebClient com OAuth2 e tracing |
| **ScheduleLiquidation** | Modelo de domínio representando um agendamento para liquidação |
| **NotificacaoPagamento** | Modelo de domínio representando notificação de pagamento |
| **StatusAgendamento** | Modelo Avro para publicação no Kafka |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.7.x** - Framework principal
- **Spring WebFlux** - Programação reativa
- **Spring Cloud GCP PubSub** - Integração com Google Cloud PubSub
- **Spring Cloud Stream** - Abstração para mensageria
- **Spring Security OAuth2 Client** - Autenticação OAuth2 client credentials
- **Apache Kafka** - Publicação de eventos (Confluent Cloud)
- **Apache Avro** - Serialização de mensagens Kafka
- **Jackson** - Serialização/deserialização JSON
- **Lombok** - Redução de boilerplate
- **Micrometer/Prometheus** - Métricas e observabilidade
- **Spring Cloud Sleuth + OpenTelemetry** - Tracing distribuído
- **WebClient** - Cliente HTTP reativo
- **Maven** - Gerenciamento de dependências
- **JUnit/Mockito** - Testes unitários
- **Docker** - Containerização
- **Google Cloud Platform** - Infraestrutura (PubSub)
- **Confluent Schema Registry** - Gerenciamento de schemas Avro

---

## 4. Principais Endpoints REST

Não se aplica. Este sistema não expõe endpoints REST públicos, apenas endpoints de gerenciamento (actuator) na porta 9090.

---

## 5. Principais Regras de Negócio

1. **Conversão de Agendamentos**: Converte mensagens de agendamento do formato PubSub para o formato de transferência aceito pelo orquestrador de transferências
2. **Enriquecimento de Dados**: Busca e cacheia informações de tipos de conta através de API externa para completar dados da transferência
3. **Tratamento de Reagendamento**: Quando o serviço de transferências retorna status 503 (SERVICE_UNAVAILABLE), o sistema marca o agendamento como "REAGENDADO" e notifica o SGAT
4. **Mapeamento de Status**: Converte códigos de status de pagamento (3=Confirmado, 4=Rejeitado) para status de agendamento SGAT (FINALIZADO_COM_SUCESSO, REAGENDADO, FINALIZADO_SEM_SUCESSO)
5. **Validação de Participantes**: Valida e formata dados de remetente e favorecido (CPF/CNPJ, tipo pessoa, tipo conta)
6. **Geração de Protocolo**: Mantém rastreabilidade através de protocolos de solicitação do cliente
7. **Tratamento de Erros**: Captura e trata erros de integração, convertendo-os em notificações de status apropriadas
8. **Cache de Tipos de Conta**: Implementa cache local para evitar consultas repetidas à API de tipos de conta
9. **Processamento Assíncrono**: Utiliza programação reativa para processar mensagens sem bloquear threads

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **ScheduleLiquidation**: Entidade raiz contendo Schedule, FinancialInfo e ExecutionInformation
  - **Schedule**: Informações do agendamento (canal origem, código liquidação, data, identificadores)
  - **FinancialInfo**: Informações financeiras (valor, descrição, credor, devedor, payload)
    - **AccountInformation**: Dados da conta (banco, agência, conta, tipo, CPF/CNPJ, nome)
    - **Payload**: Dados complementares (códigos de finalidade, evento, transação, histórico)
  - **ExecutionInformation**: Informações de execução (data batch, janelas de tempo)

- **NotificacaoPagamento**: Notificação de status de pagamento
  - **StatusPagamento**: Status e mensagem do pagamento
  - **OrigemPagamento**: Código da origem

- **Transferencia**: Objeto de transferência enviado ao orquestrador
  - **Participante**: Dados de remetente e favorecido (tipo pessoa, CPF/CNPJ, banco, agência, conta)

- **StatusAgendamento**: Objeto Avro publicado no Kafka
  - Contém protocolo de pagamento, protocolo de solicitação, status e motivo de insucesso

**Relacionamentos:**
- ScheduleLiquidation (1) -> (1) Schedule
- ScheduleLiquidation (1) -> (1) FinancialInfo
- FinancialInfo (1) -> (2) AccountInformation (creditor/debtor)
- FinancialInfo (1) -> (1) Payload
- Transferencia (1) -> (2) Participante (remetente/favorecido)

---

## 7. Estruturas de Banco de Dados Lidas

Não se aplica. O sistema não acessa diretamente bancos de dados relacionais ou NoSQL.

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema não realiza operações de escrita em bancos de dados.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | Leitura | Configuração de logging | Arquivo de configuração do Logback para formatação de logs em JSON |
| application.yml | Leitura | Spring Boot | Arquivo de configuração principal da aplicação |
| application-local.yml | Leitura | Spring Boot (profile local) | Configurações para ambiente de desenvolvimento local |
| StatusAgendamentoSGAT.avsc | Leitura | Maven Avro Plugin | Schema Avro para geração de classes de serialização Kafka |
| openapi.yaml | Leitura | OpenAPI Generator | Especificação OpenAPI (vazia, obrigatória pelo chassi) |
| sboot-spag-base-orch-transferencias.yaml | Leitura | OpenAPI Generator | Especificação da API de transferências para geração de DTOs |

---

## 10. Filas Lidas

**Google Cloud PubSub:**

1. **Tópico**: `business-sgat-base-executa-agendamento`
   - **Subscription**: `business-sgat-base-executa-agendamento-sub`
   - **Descrição**: Fila contendo solicitações de execução de agendamentos de pagamento
   - **Consumer**: `SettleSchedulingConsumerAdapter.receiveScheduling()`
   - **Formato**: JSON serializado em bytes (ScheduleLiquidation)

2. **Tópico**: `business-spag-base-notification-service`
   - **Subscription**: `business-spag-base-notificacao-agendamento-pagamento-sub`
   - **Descrição**: Fila contendo notificações de status de pagamento
   - **Consumer**: `NotifySchedulingStatusConsumerAdapter.receiveNotification()`
   - **Formato**: JSON (NotificacaoPagamento)

---

## 11. Filas Geradas

**Apache Kafka (Confluent Cloud):**

1. **Tópico**: `sgat-base-status-agendamento`
   - **Producer**: `SchedulingStatusProducer`
   - **Descrição**: Tópico para publicação de status de agendamentos para o sistema SGAT
   - **Formato**: Avro (StatusAgendamento)
   - **Schema Registry**: Confluent Schema Registry
   - **Chave**: String (null)
   - **Valor**: StatusAgendamento (Avro)

---

## 12. Integrações Externas

1. **sboot-spag-base-orch-transferencias**
   - **Tipo**: API REST
   - **Endpoint**: `/v1/transferencia` (POST)
   - **Descrição**: Serviço responsável por processar transferências (TED, TEF, DOC)
   - **Autenticação**: OAuth2 Client Credentials
   - **Classe**: `SettleSchedulingAdapter`

2. **sboot-glob-base-atom-cliente-dados-cadastrais**
   - **Tipo**: API REST
   - **Endpoint**: `/v1/banco-digital/tipo-conta/id/{accountType}` (GET)
   - **Descrição**: Serviço de consulta de tipos de conta bancária
   - **Autenticação**: OAuth2 Client Credentials
   - **Classe**: `AccountTypeLookupAdapter`
   - **Cache**: Implementado em memória (ConcurrentHashMap)

3. **Google Cloud PubSub**
   - **Tipo**: Mensageria
   - **Descrição**: Plataforma de mensageria para consumo de eventos de agendamento e notificação
   - **Projeto GCP**: bv-spag-{des|uat|prd}

4. **Confluent Kafka Cloud**
   - **Tipo**: Mensageria
   - **Descrição**: Plataforma Kafka gerenciada para publicação de status
   - **Schema Registry**: Gerenciamento de schemas Avro
   - **Autenticação**: SASL/PLAIN com API Key/Secret

5. **API Gateway BV**
   - **Tipo**: OAuth2 Token Provider
   - **Endpoint**: `/auth/oauth/v2/token-jwt`
   - **Descrição**: Provedor de tokens OAuth2 para autenticação em APIs internas

---

## 13. Avaliação da Qualidade do Código

**Nota:** 8/10

**Justificativa:**

**Pontos Positivos:**
- Arquitetura hexagonal bem implementada com separação clara de responsabilidades (adapters, application, domain, infrastructure)
- Uso adequado de padrões de projeto (Adapter, Use Case, Mapper)
- Programação reativa bem aplicada com Spring WebFlux e Reactor
- Tratamento de erros estruturado com exceções customizadas
- Configuração de observabilidade (tracing, métricas) bem implementada
- Cache inteligente para otimização de consultas de tipos de conta
- Uso de Lombok para redução de boilerplate
- Testes unitários presentes (embora não incluídos na análise)
- Documentação README completa e detalhada

**Pontos de Melhoria:**
- Algumas classes poderiam ter mais documentação JavaDoc (ex: casos de uso)
- A classe `MessageConverter` tem responsabilidades múltiplas (conversão + enriquecimento de dados)
- Constantes mágicas em alguns lugares (ex: `CPF_LENGTH = 11`)
- O tratamento de erro no `SettleSchedulingUseCase` poderia ser mais granular
- Falta validação mais robusta de payloads de entrada
- Alguns métodos poderiam ser quebrados em métodos menores para melhor legibilidade
- A configuração do WebClient está complexa e poderia ser modularizada

O código demonstra maturidade técnica, boas práticas de engenharia de software e preocupação com manutenibilidade, mas há espaço para melhorias em documentação e refatoração de alguns componentes.

---

## 14. Observações Relevantes

1. **Ambiente Multi-Cloud**: O sistema opera em Google Cloud Platform (PubSub) e Confluent Cloud (Kafka), demonstrando arquitetura multi-cloud

2. **Configuração por Ambiente**: Utiliza variáveis de ambiente para configuração específica de cada ambiente (DES, UAT, PRD) através do arquivo `infra.yml`

3. **Segurança**: Implementa OAuth2 Client Credentials para autenticação em APIs internas, com renovação automática de tokens

4. **Observabilidade**: Integração completa com OpenTelemetry, Micrometer e Prometheus para tracing distribuído e métricas

5. **Resiliência**: Implementa tratamento de reagendamento automático quando serviços downstream estão indisponíveis (503)

6. **Performance**: Uso de cache local para tipos de conta reduz latência e carga em serviços externos

7. **Containerização**: Dockerfile otimizado com multi-layer para melhor cache de dependências

8. **CI/CD**: Configuração Jenkins presente (`jenkins.properties`) para pipeline automatizado

9. **Chassi Atlante**: Utiliza o chassi corporativo Atlante Base para padronização e governança

10. **Versionamento Semântico**: Projeto na versão 0.3.0, indicando fase de desenvolvimento ativo

11. **Modo Reativo**: Aplicação configurada como `web-application-type: reactive` para melhor throughput e uso de recursos

12. **Ack Manual**: Configuração de acknowledge manual no PubSub para garantir processamento confiável de mensagens

13. **Código Origem**: Sistema identifica-se como origem "SGAT-BASE" (código 116) nas transações