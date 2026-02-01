# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-spbb-base-orch-recebimento-mensagem** é um orquestrador desenvolvido em Java com Spring Boot e Apache Camel, responsável pelo recebimento e processamento de mensagens do Sistema de Pagamentos Brasileiro (SPB). 

O fluxo principal consiste em:
1. Receber mensagens criptografadas via Google Cloud Pub/Sub
2. Descriptografar as mensagens utilizando biblioteca SPBSecJava (EVALCryptoSPB)
3. Converter mensagens XML do Bacen para JSON
4. Processar e atualizar saldo de reserva no core bancário
5. Atualizar status do movimento no SPB
6. Publicar eventos de mensagens processadas e recebidas em tópicos Kafka
7. Em caso de falha, encaminhar para processamento legado (SPBBV)

O sistema atua como camada de orquestração entre as câmaras de liquidação do SPB e os sistemas internos do banco (Banco Votorantim - 655 e Banco BV SA - 413).

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot, ponto de entrada da aplicação |
| `RecebimentoMensagemSpbPubsubListener` | Listener que consome mensagens do Pub/Sub |
| `RecebimentoMensagemSpbRouter` | Roteador Camel principal que orquestra o fluxo de processamento |
| `MensagemRecebidaSPBRouter` | Roteador responsável pela conversão e atualização de movimentos |
| `ProcessamentoMensagemCoreRouter` | Roteador para atualização de saldo reserva no core |
| `DecryptService` | Serviço de descriptografia de mensagens usando SPBSecJava |
| `SpbAtomMensageriaServiceImpl` | Integração com atom-mensageria para conversão e atualização de movimentos |
| `SpbAtomIntegracaoServiceImpl` | Integração com atom-integracao para processamento no core |
| `MensagemCriptografadaProcessor` | Processor que prepara mensagem para descriptografia |
| `ExtracaoMensagemBacenProcessor` | Processor que extrai dados da mensagem Bacen |
| `AtualizaMovimentoProcessor` | Processor que prepara dados para atualização de movimento |
| `MensagemRecebidaProcessor` | Processor que monta evento de mensagem recebida |
| `SPBBVAclProcessor` | Processor que publica mensagem para processamento legado |
| `EnvioMensagemProcessadaRepositoryImpl` | Repositório para publicação em Kafka de mensagens processadas |
| `EnvioMensagemRecebidaRepositoryImpl` | Repositório para publicação em Kafka de mensagens recebidas |
| `FeatureToggleService` | Serviço para controle de feature flags |

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.5.x** (framework base)
- **Apache Camel 3.x** (orquestração e roteamento)
- **Google Cloud Pub/Sub** (mensageria de entrada)
- **Apache Kafka / Confluent** (mensageria de saída)
- **Apache Avro** (serialização de eventos)
- **SPBSecJava (EVALCryptoSPB)** (biblioteca de criptografia do SPB)
- **Spring Security OAuth2** (autenticação)
- **RestTemplate** (cliente HTTP)
- **MapStruct** (mapeamento de objetos)
- **Logback com JSON** (logging estruturado)
- **Spring Retry** (resiliência)
- **ConfigCat** (feature toggle)
- **Swagger/OpenAPI** (documentação de APIs)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Google Cloud Platform** (infraestrutura)

## 4. Principais Endpoints REST

Não se aplica. O sistema não expõe endpoints REST próprios, atuando como consumidor de mensagens Pub/Sub e cliente de APIs externas.

## 5. Principais Regras de Negócio

1. **Descriptografia de Mensagens SPB**: Mensagens recebidas são descriptografadas usando certificados digitais e algoritmos específicos do SPB através da biblioteca EVALCryptoSPB
2. **Identificação de Instituição**: Sistema identifica a instituição destinatária (BV-655 ou BVSA-413) através do código ISPB presente na mensagem
3. **Conversão XML para JSON**: Mensagens XML do padrão Bacen são convertidas para JSON utilizando catálogo de mensagens SPB
4. **Validação de Domínio**: Identifica o domínio da mensagem (SPB01, SPB02, etc.) através do sequencial na fila
5. **Atualização de Saldo Reserva**: Processa mensagens que impactam saldo de reserva bancária no core
6. **Controle de Status de Movimento**: Atualiza status do movimento SPB (Digitada, Respondida, Erro)
7. **Tratamento de Erros de Descriptografia**: Códigos de erro específicos da biblioteca EVALCryptoSPB são mapeados e tratados
8. **Resiliência em Falhas de Conexão**: Retry automático em falhas de conexão com servidores EVAL
9. **Fallback para Legado**: Em caso de falha no processamento novo, encaminha para sistema legado SPBBV
10. **Feature Toggle para Servidores EVAL**: Permite alternar entre servidores EVAL antigos e novos via feature flag
11. **Publicação de Histórico**: Registra mensagens processadas em tópico Kafka para histórico
12. **Controle de Conclusão**: Define flag de conclusão do movimento baseado no retorno do core

## 6. Relação entre Entidades

**Entidades Principais:**

- **MensagemRecebida**: Representa mensagem recebida do Pub/Sub (nomeFila, mensagemCriptografada)
- **MensagemDescriptografar**: Dados para descriptografia (domain, identdEmissor, identdDestinatario, mensagem)
- **RecebimentoMensagemDomain**: Entidade completa do movimento SPB com todos os dados processados
- **MensagemProcessadaSPB** (Avro): Evento de mensagem processada para Kafka
- **MensagemRecebidaSPB** (Avro): Evento de mensagem recebida para Kafka

**Relacionamentos:**
- MensagemRecebida → MensagemDescriptografar (transformação para descriptografia)
- MensagemDescriptografar → XML descriptografado → RecebimentoMensagemDomain (conversão)
- RecebimentoMensagemDomain → ProcessarMensagemCore (request para core)
- RecebimentoMensagemDomain → MensagemProcessadaSPB (evento histórico)
- RecebimentoMensagemDomain + ProcessarCoreResponse → MensagemRecebidaSPB (evento final)

## 7. Estruturas de Banco de Dados Lidas

não se aplica

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | leitura | Configuração de logging | Arquivo de configuração de logs em formato JSON |
| application.yml | leitura | Spring Boot | Configurações da aplicação por ambiente |
| application-des.yml | leitura | Spring Boot | Configurações específicas do ambiente de desenvolvimento |
| application-local.yml | leitura | Spring Boot | Configurações para execução local |
| MensagemProcessadaSPB.avsc | leitura | Avro Maven Plugin | Schema Avro para eventos de mensagens processadas |
| MensagemRecebidaSPB.avsc | leitura | Avro Maven Plugin | Schema Avro para eventos de mensagens recebidas |

## 10. Filas Lidas

**Google Cloud Pub/Sub:**
- **business-spbb-base-recebimento-mensagem-spb-sub**: Subscription que consome mensagens criptografadas do SPB provenientes das câmaras de liquidação. Configurado com controle de fluxo (max 2000 elementos, 100MB).

## 11. Filas Geradas

**Google Cloud Pub/Sub:**
- **business-spbb-base-integracao-legado**: Tópico para envio de mensagens ao sistema legado SPBBV em caso de falha ou quando mensagem não é processada pelo novo fluxo.

**Apache Kafka (Confluent Cloud):**
- **spbb-base-mensagem-processada**: Tópico para publicação de eventos de mensagens processadas (histórico XML)
- **spbb-base-mensagem-recebida-spb**: Tópico para publicação de eventos de mensagens recebidas após processamento completo (JSON)

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| **sboot-spbb-base-atom-mensageria** | API REST | Serviço para conversão de mensagens XML→JSON e atualização de movimentos SPB |
| **sboot-spbb-base-atom-integracao** | API REST | Serviço para processamento de mensagens no core bancário e atualização de saldo reserva |
| **EVALCryptoSPB** | Socket TCP | Servidores de descriptografia de mensagens SPB (mor-spbuat1, srv-eval01/02) |
| **API Gateway BV** | OAuth2 | Serviço de autenticação para obtenção de tokens JWT |
| **Google Cloud Pub/Sub** | Mensageria | Plataforma de mensageria para recebimento e envio de eventos |
| **Confluent Cloud Kafka** | Mensageria | Plataforma Kafka gerenciada para publicação de eventos |
| **Schema Registry (Confluent)** | API REST | Registro de schemas Avro para validação de eventos |
| **ConfigCat** | Feature Toggle | Serviço de feature flags para controle de funcionalidades |

## 13. Avaliação da Qualidade do Código

**Nota: 7,5/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com uso adequado de camadas (router, processor, service, repository)
- Uso de padrões de projeto apropriados (Strategy, Template Method via Camel)
- Tratamento de exceções estruturado com classes específicas
- Logging estruturado em JSON
- Uso de feature toggles para controle de mudanças
- Resiliência implementada com retry
- Documentação de APIs via Swagger/OpenAPI
- Uso de MapStruct para mapeamento de objetos
- Configuração externalizada por ambiente

**Pontos de Melhoria:**
- Alguns processadores Camel poderiam ser simplificados
- Classe `DecryptService` possui lógica complexa de gerenciamento de conexões que poderia ser refatorada
- Uso de `@SneakyThrows` em `PubSubTopicPublisher` mascara exceções
- Falta de testes unitários incluídos na análise (marcados como NÃO_ENVIAR)
- Alguns métodos com múltiplas responsabilidades (ex: `initializeConnection` no DecryptService)
- Uso de `synchronized` e mutex manual poderia ser substituído por abstrações do Spring
- Comentários em português e inglês misturados
- Algumas constantes poderiam estar em enums ao invés de classes utilitárias
- Falta de validação de entrada em alguns pontos

## 14. Observações Relevantes

1. **Criticidade**: Sistema crítico para operação bancária, processando mensagens do SPB em tempo real
2. **Segurança**: Utiliza criptografia específica do SPB com certificados digitais gerenciados pela biblioteca EVALCryptoSPB
3. **Multi-instituição**: Suporta processamento para duas instituições (BV-655 e BVSA-413)
4. **Resiliência**: Implementa fallback para sistema legado em caso de falhas
5. **Observabilidade**: Logs estruturados em JSON com MDC para rastreamento de mensagens
6. **Infraestrutura**: Executado em Google Cloud Platform com Kubernetes
7. **Versionamento de Schema**: Utiliza Avro com Schema Registry para evolução de contratos
8. **Configuração Dinâmica**: Feature toggles permitem alterações sem deploy (ex: troca de servidores EVAL)
9. **Monitoramento**: Expõe métricas via Actuator e Prometheus
10. **Dependência Externa Crítica**: Biblioteca SPBSecJava (1.0.6) é proprietária e essencial para descriptografia
11. **Processamento Assíncrono**: Utiliza AsyncAppender para logs e processamento não-bloqueante
12. **Controle de Fluxo**: Pub/Sub configurado com limites para evitar sobrecarga (2000 mensagens, 100MB)