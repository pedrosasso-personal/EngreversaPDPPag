# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema ACL (Anti-Corruption Layer) responsável pelo recebimento de mensagens do Sistema de Pagamentos Brasileiro (SPB) através de filas IBM MQ e posterior encaminhamento para o Google Cloud Pub/Sub. O sistema atua como intermediário entre o Bacen e o SPB Core do Banco Votorantim, consumindo mensagens de diferentes filas MQ (participantes 655 - Votorantim e 413 - BV S.A.) e publicando-as em tópicos Pub/Sub para processamento posterior.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot, inicializa a aplicação com Feature Toggle e agendamento habilitados |
| `Recebimento655MQListener` | Listener JMS que consome mensagens das filas do participante 655 (Votorantim) - STR, PAG e SRC |
| `Recebimento413MQListener` | Listener JMS que consome mensagens das filas do participante 413 (BV S.A.) - STR, PAG e SRC |
| `RecebimentoMensagemSpbService` | Serviço que processa mensagens JMS, converte para byte array e envia para Pub/Sub |
| `PubSubTopicRepositoryImpl` | Implementação do repositório que publica mensagens no Google Cloud Pub/Sub |
| `FeatureToggleService` | Gerencia feature flags para habilitar/desabilitar listeners de filas específicas |
| `HabilitarListenerIbmMQConfig` | Configuração que controla dinamicamente o estado (ligado/desligado) dos listeners MQ via feature toggle |
| `JmsConfig` | Configuração das conexões JMS para IBM MQ (duas factories: Votorantim e BV S.A.) |
| `PubSubMessagingGatewayConfiguration` | Configuração do gateway de mensageria para Pub/Sub |
| `MqQueuesConstants` | Constantes com nomes das filas MQ |
| `PayloadPubSub` | DTO que encapsula mensagem e nome da fila para envio ao Pub/Sub |

---

## 3. Tecnologias Utilizadas

- **Framework**: Spring Boot 2.7.x
- **Mensageria**: 
  - IBM MQ (com mq-jms-spring-boot-starter 2.7.18)
  - Google Cloud Pub/Sub (spring-cloud-gcp-starter-pubsub)
- **Integração**: Spring Integration 5.5.12
- **Orquestração**: Apache Camel (múltiplos módulos)
- **Feature Toggle**: ConfigCat (via sbootlib-arqt-base-feature-toggle 3.0.1)
- **Segurança**: Spring Security OAuth2 Resource Server com JWT
- **Observabilidade**: 
  - Spring Boot Actuator
  - Micrometer com Prometheus
  - OpenTelemetry
- **Logging**: Logback com formato JSON
- **Containerização**: Docker com imagem base Java 11
- **Infraestrutura**: Google Cloud Platform (GCP)
- **Build**: Maven 3.8+
- **Java**: 11+

---

## 4. Principais Endpoints REST

não se aplica

(O sistema é orientado a eventos/mensageria, não expõe endpoints REST de negócio, apenas endpoints do Actuator para monitoramento)

---

## 5. Principais Regras de Negócio

1. **Consumo Seletivo de Filas**: Cada fila MQ pode ser habilitada/desabilitada individualmente via feature toggle, permitindo controle granular do processamento
2. **Conversão de Mensagens**: Mensagens JMS são convertidas para byte array, suportando tanto JMSBytesMessage quanto JMSTextMessage
3. **Roteamento por Participante**: Mensagens são segregadas por participante SPB (655 - Votorantim, 413 - BV S.A.)
4. **Roteamento por Tipo**: Três tipos de mensagens são processados: STR (Sistema de Transferência de Reservas), PAG (Pagamentos) e SRC (Sistema de Registro de Crédito)
5. **Garantia de Entrega**: Utiliza transações JMS (sessionTransacted=true) para garantir processamento confiável
6. **Retry e Reconexão**: Configuração de reconexão automática do IBM MQ (WMQ_CLIENT_RECONNECT com timeout de 1800s)
7. **Controle Dinâmico**: Verificação periódica (a cada 1 segundo) do estado dos feature toggles para ligar/desligar listeners em tempo de execução
8. **Enriquecimento de Contexto**: Mensagens enviadas ao Pub/Sub incluem metadados como nome da fila de origem e correlation ID

---

## 6. Relação entre Entidades

**Entidades de Domínio:**

- `PayloadPubSub`: Contém byte[] message e String filaMQ
- `Integration`: Entidade genérica com id e name (aparentemente não utilizada no fluxo principal)
- `Storage`: Entidade com informações de bucket, fileName, folder e contentType (aparentemente não utilizada no fluxo principal)

**Relacionamentos:**
- Não há relacionamentos JPA tradicionais, pois o sistema não persiste dados em banco relacional
- O fluxo é: Fila MQ → Listener → Service → Repository → Pub/Sub

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

(O sistema não realiza leitura de banco de dados)

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

(O sistema não realiza escrita em banco de dados)

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | leitura | Configuração do Logback | Arquivo de configuração de logs em formato JSON |
| application.yml | leitura | Spring Boot | Configurações da aplicação |
| application-des.yml | leitura | Spring Boot | Configurações específicas do ambiente de desenvolvimento |
| application-local.yml | leitura | Spring Boot | Configurações para execução local |
| openapi.yaml | leitura | Swagger/SpringDoc | Especificação OpenAPI da aplicação |

---

## 10. Filas Lidas

**IBM MQ - Participante 655 (Votorantim):**
- `QL.RSP.00038166.59588111.01` - Fila STR (Sistema de Transferência de Reservas)
- `QL.RSP.04391007.59588111.01` - Fila PAG (Pagamentos)
- `QL.RSP.00038166.59588111.03` - Fila SRC (Sistema de Registro de Crédito)

**IBM MQ - Participante 413 (BV S.A.):**
- `QL.RSP.00038166.01858774.01` - Fila STR
- `QL.RSP.04391007.01858774.01` - Fila PAG
- `QL.RSP.00038166.01858774.03` - Fila SRC

**Configurações de Conexão:**
- Queue Managers: QM.59588111.01 (655) e QM.01858774.01 (413)
- Modo de conexão: Cliente MQ com reconexão automática
- Autenticação: MQCSP com usuário e senha

---

## 11. Filas Geradas

**Google Cloud Pub/Sub:**
- Tópico: `business-spbb-base-recebimento-mensagem-spb`
- Projeto GCP: Variável por ambiente (bv-spbb-des, bv-spbb-uat, bv-spbb-prd)
- Mensagens publicadas contêm: payload em bytes, nome da fila de origem e correlation ID

---

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| IBM MQ (Votorantim) | Fila de Mensagens | Consumo de mensagens SPB do participante 655 |
| IBM MQ (BV S.A.) | Fila de Mensagens | Consumo de mensagens SPB do participante 413 |
| Google Cloud Pub/Sub | Fila de Mensagens | Publicação de mensagens para processamento downstream |
| ConfigCat | Feature Toggle | Controle de habilitação/desabilitação de listeners |
| OAuth2/JWT | Segurança | Autenticação e autorização via tokens JWT |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com camadas bem definidas (listener, service, repository, config)
- Uso adequado de injeção de dependências e anotações Spring
- Implementação de feature toggles para controle dinâmico de funcionalidades
- Tratamento de exceções com logging apropriado
- Testes unitários presentes com boa cobertura dos componentes principais
- Configuração externalizada por ambiente
- Uso de Lombok para reduzir boilerplate
- Documentação básica presente (README, OpenAPI)

**Pontos de Melhoria:**
- Classe `HabilitarListenerIbmMQConfig` possui lógica complexa com múltiplos ifs que poderia ser refatorada usando Strategy Pattern ou Map de handlers
- Método `getPreviousState` e `updatePreviousState` com código repetitivo que poderia usar um Map para armazenar estados
- Falta de constantes para strings literais em alguns pontos (ex: "Authorization", "nomeFilaMensagem")
- Ausência de validações mais robustas em alguns pontos (ex: validação de tamanho de mensagem)
- Comentários em código poderiam ser mais descritivos em pontos críticos
- Algumas classes de domínio (`Integration`, `Storage`) parecem não ser utilizadas e poderiam ser removidas
- Falta de documentação JavaDoc em métodos públicos importantes
- Configuração de concorrência hardcoded em alguns lugares (poderia ser mais flexível)

---

## 14. Observações Relevantes

1. **Arquitetura Multi-Tenant**: O sistema suporta dois participantes SPB distintos (655 e 413) com configurações MQ separadas
2. **Alta Disponibilidade**: Configuração de reconexão automática do MQ garante resiliência em caso de falhas de rede
3. **Controle Operacional**: Feature toggles permitem desabilitar processamento de filas específicas sem necessidade de redeploy
4. **Observabilidade**: Integração com OpenTelemetry e Prometheus para monitoramento e tracing distribuído
5. **Segurança**: Credenciais armazenadas em cofre de senhas (referenciadas via placeholders no infra.yml)
6. **Multi-Ambiente**: Suporte para ambientes local, des, uat e prd com configurações específicas
7. **Containerização**: Dockerfile otimizado com multi-layer para melhor cache de dependências
8. **Logging Estruturado**: Logs em formato JSON facilitam ingestão em ferramentas de análise
9. **Transacionalidade**: Uso de sessões transacionadas JMS garante processamento exactly-once
10. **Emulador Local**: Suporte para emulador Pub/Sub local via docker-compose para desenvolvimento

---