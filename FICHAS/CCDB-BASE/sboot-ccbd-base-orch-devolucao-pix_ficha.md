# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-ccbd-base-orch-devolucao-pix** é um microsserviço orquestrador responsável por processar devoluções de transferências Pix no Banco Votorantim. Ele gerencia todo o fluxo de devolução, desde a validação da conta até a efetivação da transação e envio de notificações aos clientes. O sistema integra-se com diversos serviços internos e externos (SPAG, GNMS, SalesForce) e utiliza mensageria (RabbitMQ, Kafka, Google Pub/Sub) para comunicação assíncrona.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `DevolucaoPixController` | Controller REST que expõe o endpoint de devolução de transferência Pix |
| `DevolucaoPixService` | Serviço de domínio que orquestra o fluxo de devolução via Apache Camel |
| `NotificacaoService` | Serviço de domínio que orquestra o envio de notificações aos clientes |
| `DevolucaoPixRouter` | Roteador Camel que define o fluxo de validação, geração de token, identificador, envio e consulta |
| `NotificacaoDevolucaoRouter` | Roteador Camel para processamento de notificações de devolução |
| `GerarTokenCoorpRouter` | Roteador Camel para geração de tokens corporativos (BV e BVSA) |
| `ValidarContaRepositoryImpl` | Implementação que valida contas do remetente e favorecido |
| `EnviarDevolucaoRepositoryImpl` | Implementação que envia a solicitação de devolução para SPAG |
| `ConsultarOperacaoRepositoryImpl` | Implementação que consulta o status da operação Pix |
| `NotificacaoListener` | Listener RabbitMQ que consome mensagens de devolução |
| `PubsubListener` | Listener Google Pub/Sub que consome mensagens de devolução |
| `DevolucaoPixMapper` | Mapper para conversão de requisições em objetos de domínio |
| `ComprovantePixMapper` | Mapper para conversão de comprovante em resposta |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (Web, AMQP, Actuator, Security OAuth2)
- **Apache Camel 3.2.0** (orquestração de fluxos)
- **RabbitMQ** (mensageria assíncrona)
- **Apache Kafka** (publicação de eventos de notificação)
- **Google Cloud Pub/Sub** (consumo de mensagens)
- **IBM MQ** (integração com GAPP)
- **Swagger/OpenAPI 3.0** (documentação de APIs)
- **Lombok** (redução de boilerplate)
- **RestTemplate** (cliente HTTP)
- **Micrometer + Prometheus** (métricas)
- **Logback** (logging)
- **JUnit 5 + Mockito** (testes unitários)
- **Pact** (testes de contrato)
- **Docker** (containerização)
- **Maven** (gerenciamento de dependências)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/banco-digital/transferencia-pix/devolver` | `DevolucaoPixController` | Realiza a devolução de uma transferência Pix, validando conta, gerando identificador único, enviando para SPAG e consultando status da operação |

**Headers obrigatórios:**
- `codigoBanco` (Integer)
- `numeroAgencia` (String)
- `numeroConta` (Long)
- `tipoConta` (Integer)
- `numeroCpfCnpj` (String, opcional)

---

## 5. Principais Regras de Negócio

1. **Validação de Conta**: Verifica se as contas do remetente e favorecido são válidas e se o remetente possui saldo suficiente para a devolução
2. **Geração de Token**: Gera token JWT diferenciado conforme o banco (BV ou BVSA) para autenticação nas APIs SPAG
3. **Geração de Identificador Único**: Cria um identificador único (NSU) para a transação de devolução no padrão do SPI
4. **Envio de Devolução**: Envia a solicitação de devolução para o sistema SPAG (Sistema de Pagamentos)
5. **Consulta de Status**: Realiza polling (até 17 tentativas com delay de 500ms) para verificar o status da operação até que seja efetivada ou falhe
6. **Conversão de Motivos**: Converte códigos de motivo de devolução (AM05, AM09, FOCR) para códigos padronizados (MD06, BE08)
7. **Notificação de Clientes**: Envia notificações push via SalesForce ou Kafka/GNMS dependendo de feature toggle
8. **Tratamento de Erros SPAG**: Mapeia códigos de erro específicos do SPAG para mensagens de negócio apropriadas
9. **Validação de Saldo**: Verifica se o saldo após débito não fica negativo
10. **Consulta de Participantes**: Busca informações do participante recebedor no SPI para enriquecimento da notificação

---

## 6. Relação entre Entidades

**Entidades principais:**

- **DevolucaoPix**: Entidade raiz que representa uma devolução, contém valor, data, motivo, NSU, token de autorização, agentes (remetente/favorecido) e transação original
- **Agente**: Representa remetente ou favorecido, contém conta, documento, nome e tipo de transação
- **Conta**: Representa uma conta bancária, contém agência, número, tipo, saldo e participante
- **Participante**: Representa uma instituição financeira, contém ISPB, CNPJ, código do banco e nome
- **TransacaoPix**: Representa a transação original sendo devolvida, contém NSU, valor, data e descrição
- **ComprovantePix**: Representa o comprovante da devolução efetivada
- **TokenAuthorization**: Token JWT para autenticação nas APIs SPAG
- **Notificacao**: Representa uma notificação a ser enviada ao cliente, contém mensagem, participante recebedor e tipo
- **MensagemDevolucaoPix**: Mensagem recebida via fila com dados da devolução processada

**Relacionamentos:**
- DevolucaoPix (1) -> (1) TransacaoPix (transação original)
- DevolucaoPix (1) -> (2) Agente (remetente e favorecido)
- Agente (1) -> (1) Conta
- Conta (1) -> (1) Participante
- ComprovantePix (1) -> (2) Agente (remetente e favorecido)
- Notificacao (1) -> (1) MensagemDevolucaoPix
- Notificacao (1) -> (1) Participante (recebedor)

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
| `application.yml` | leitura | Spring Boot | Arquivo de configuração da aplicação com propriedades por ambiente |
| `logback-spring.xml` | leitura | Logback | Configuração de logs por ambiente (des/qa/uat/prd) |
| `swagger-server/*.yaml` | leitura | Swagger Codegen | Contratos OpenAPI do servidor para geração de código |
| `swagger-client/*.yaml` | leitura | Swagger Codegen | Contratos OpenAPI de clientes externos para geração de código |
| `kafkaschema-ppbd-pixx-enviar-notificacao-usuario-cmd.avsc` | leitura | Avro Maven Plugin | Schema Avro para mensagens Kafka de notificação |

---

## 10. Filas Lidas

**RabbitMQ:**
- **Fila**: `ccbd_devolver_pix` (configurável via `queueGappName`)
- **Listener**: `NotificacaoListener`
- **Formato**: JSON
- **Descrição**: Consome mensagens de devolução Pix para envio de notificações aos clientes

**Google Pub/Sub:**
- **Subscription**: `projects/bv-ccbd-{env}/subscriptions/business-ppbd-pixx-devolucao-pix-sub`
- **Listener**: `PubsubListener`
- **Formato**: JSON
- **Descrição**: Consome mensagens de devolução Pix vindas do SPAG para processamento de notificações

---

## 11. Filas Geradas

**Apache Kafka:**
- **Tópico**: `ppbd-pixx-enviar-notificacao-usuario-cmd`
- **Producer**: `EnviaPushNotificationProducer`
- **Formato**: Avro
- **Descrição**: Publica eventos de notificação para o sistema GNMS enviar push notifications aos clientes

**IBM MQ (GAPP):**
- **Fila**: `QL.CCBD.LIQ_PAGMT_CONTAS_DIG.INT` (des) / `QL.GAPP.ENVIA_MENSAGEM.INT` (qa/uat/prd)
- **Producer**: `NotificacaoDevolucaoPixRepositoryImpl`
- **Formato**: JSON
- **Descrição**: Envia notificações para o sistema GAPP (Banco Digital)

---

## 12. Integrações Externas

| Sistema | Tipo | Descrição |
|---------|------|-----------|
| **SPAG - Validar Conta** | REST API | Valida contas correntes do remetente e favorecido (`sboot-ccbd-base-orch-consulta-cc-cliente`) |
| **SPAG - Enviar Devolução** | REST API | Envia solicitação de devolução Pix para o SPI (`sboot-spag-pixx-orch-enviar-devolucao`) |
| **SPAG - Gerar Identificador** | REST API | Gera identificador único (EndToEndId) para a devolução (`sboot-spag-pixx-orch-enviar-pagamento`) |
| **SPAG - Consultar Operação** | REST API | Consulta status da operação Pix no SPI (`sboot-spag-pixx-orch-consultar-pagamento`) |
| **SPAG - Consultar Participantes** | REST API | Consulta dados de participantes do SPI (`sboot-spag-pixx-atom-participantes`) |
| **GNMS - Envio Push** | REST API | Envia notificações push via SalesForce Marketing Cloud (`sboot-gnms-base-orch-envio-push`) |
| **API Gateway** | OAuth2 | Geração de tokens JWT para autenticação (BV e BVSA) |
| **RabbitMQ** | Message Broker | Consumo de mensagens de devolução para notificação |
| **Google Pub/Sub** | Message Broker | Consumo de mensagens de devolução vindas do SPAG |
| **Apache Kafka** | Message Broker | Publicação de eventos de notificação para GNMS |
| **IBM MQ (GAPP)** | Message Queue | Envio de notificações para Banco Digital |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 7.5/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (application, domain, common)
- Uso adequado de padrões como Repository, Service, Mapper e Router
- Implementação de testes unitários abrangentes (cobertura aparentemente boa)
- Uso de Apache Camel para orquestração de fluxos complexos
- Tratamento de exceções customizado e estruturado
- Configuração externalizada por ambiente
- Uso de feature toggles para controle de funcionalidades
- Documentação via Swagger/OpenAPI
- Logs estruturados em JSON

**Pontos de Melhoria:**
- Algumas classes com múltiplas responsabilidades (ex: `DevolucaoPixConfiguration` com muitos beans)
- Uso excessivo de constantes hardcoded em algumas classes
- Falta de documentação JavaDoc em métodos e classes
- Alguns métodos longos que poderiam ser refatorados (ex: `enviarNotificacaoSalesForce`)
- Tratamento de exceções poderia ser mais granular em alguns pontos
- Uso de `@SneakyThrows` em testes pode mascarar problemas
- Configuração de retry com valores fixos (poderia ser externalizada)
- Alguns TODOs no código indicando pendências

---

## 14. Observações Relevantes

1. **Arquitetura Multi-Banco**: O sistema suporta operações tanto para BV (161) quanto BVSA (436), com lógica condicional para geração de tokens específicos

2. **Resiliência**: Implementa retry automático (até 17 tentativas) para consulta de operação Pix, com delay de 500ms entre tentativas

3. **Feature Toggle**: Utiliza feature toggle (`ft_boolean_digital_ppbd_pixx_habilita_push_kafka_gnms`) para alternar entre envio de notificação via SalesForce ou Kafka/GNMS

4. **Segurança**: Implementa autenticação OAuth2 JWT com propagação de contexto de segurança entre chamadas

5. **Observabilidade**: Expõe métricas via Actuator/Prometheus na porta 9090 e possui configuração para Grafana

6. **Ambientes**: Suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas

7. **Timeouts**: Configurado com timeout de conexão e leitura de 10 segundos para chamadas HTTP

8. **Pool de Conexões**: Utiliza pool de conexões HTTP com máximo de 50 conexões totais e 5 por rota

9. **Conversão de Motivos**: Realiza conversão automática de códigos de motivo de devolução (AM05/FOCR → MD06, AM09 → BE08)

10. **Formatação de Mensagens**: Formata nomes de pessoas e valores monetários para exibição nas notificações

11. **Auditoria**: Integrado com framework de trilha de auditoria do BV para rastreabilidade

12. **Containerização**: Preparado para deploy em Kubernetes/OpenShift com configurações de probes (liveness/readiness)