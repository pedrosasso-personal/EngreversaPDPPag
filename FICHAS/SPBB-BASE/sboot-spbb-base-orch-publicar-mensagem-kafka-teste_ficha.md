# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de apoio e teste para publicação de mensagens no Sistema de Pagamentos Brasileiro (SPB), atuando como intermediário entre sistemas internos (SPAG, PGFT) e o SPB (Core e Legado). Realiza rastreamento de movimentos financeiros entre múltiplos sistemas, gerencia envio/recebimento de mensagens para câmaras de compensação (STR, TED, Boletos), monitora saúde de serviços críticos e valida mensagens contra catálogo Bacen. Suporta operações multi-tenant (ISPB 413 BVSA e 655 Votorantim) com criptografia Evaltec para comunicação segura com Bacen.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **MovimentoController** | Rastreamento de movimentos entre SPAG, PGFT, SPBCore e SPBLegado |
| **IbmMQController** | Envio de mensagens criptografadas para filas IBM MQ das câmaras |
| **EnvioMensagemTopicoController** | Publicação de mensagens no Kafka (topic envio-mensagem) |
| **SpbLegadoService** | Gerenciamento de movimentos STR no sistema legado, aprovação e inserção NSU |
| **EncryptService** | Criptografia de mensagens usando biblioteca SPBSecJava (Evaltec) |
| **PubSubTopicRepositoryService** | Publicação/consumo de mensagens Google Pub/Sub (confirmações, TED In) |
| **ServiceStatusService** | Monitoramento e persistência de status de serviços (health check) |
| **EcoService** | Geração e envio de mensagens ECO para verificação de conectividade SPB |
| **RegistroBoletoService** | Registro de boletos genéricos via API Gateway |
| **TefService** | Execução de TEF genérica para testes |
| **ConsultaBoletoService** | Consulta de boletos com cache |
| **GatewayOAuthService** | Gerenciamento de tokens OAuth2 para integração com APIs |
| **SpbLegadoRepository** | Acesso a dados do sistema legado (tb_movi_movimento, tb_msbc_mensagem_bacen) |
| **LancamentoSpagRepository** | Consulta de lançamentos SPAG com notificações |
| **MovimentoSPBCoreRepository** | Consulta de movimentos no SPB Core |
| **MensagemAberturaSpbSchedule** | Validação periódica de recebimento de mensagens de abertura SPB |
| **CriptografiaSchedule** | Teste periódico de criptografia de mensagens |
| **RegistroBoletoSchedule** | Teste periódico de registro e consulta de boletos |

---

## 3. Tecnologias Utilizadas

- **Framework**: Spring Boot, Spring MVC, Spring Security, Spring AMQP, Spring Integration, Spring Cloud GCP Pub/Sub
- **Mensageria**: Apache Kafka (Confluent, Avro Schema Registry), IBM MQ, RabbitMQ, Google Cloud Pub/Sub
- **Persistência**: JDBI (MySQL, Sybase ASE), H2 (in-memory)
- **Comunicação**: RestTemplate, OAuth2 Client Credentials, JavaMail (SMTP)
- **Serialização**: Jackson, Gson, Avro
- **Template Engine**: Thymeleaf
- **Criptografia**: SPBSecJava (Evaltec EVAL)
- **Utilitários**: Lombok, SLF4J/Logback, Apache Commons
- **Build**: Maven, Docker multi-stage
- **Monitoramento**: Actuator, Swagger

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/movimento/rastreamento` | MovimentoController | Rastreia movimentos entre SPAG, PGFT, SPBCore e SPBLegado por código |
| POST | `/mq/envio-mensagem` | IbmMQController | Criptografa e envia XML para fila IBM MQ da câmara (655/413) |
| POST | `/publicarEnvioMensagem` | EnvioMensagemTopicoController | Publica mensagem no Kafka topic envio-mensagem (Avro) |
| POST | `/mensagem-processada-topico` | MensagemProcessadaTopicoController | Publica mensagem processada no Kafka (Avro) |
| POST | `/publicarRecebimentoMensagemSPB` | MensagemRecebidaSpbController | Publica mensagem recebida no Kafka (Avro) |
| POST | `/publicarStatusMensagem` | StatusEnvioMensagemTopicoController | Publica status de envio no Kafka (Avro) |
| POST | `/inserirMovimento` | MoviMovimentoController | Insere movimento STR no sistema legado (tb_movi_movimento) |
| POST | `/expurgarMovimentos` | MoviMovimentoController | Remove movimentos de teste do sistema legado |
| POST | `/publicarConfirmacaoSpbPubSub` | PublicarConfirmacaoSpbPubSubController | Publica confirmação no Google Pub/Sub |
| POST | `/publicarRecebimentoMensagemSpbCorePubSub` | PublicarRecebimentoMensagemSpbCorePubSubController | Publica recebimento SPB Core no Pub/Sub |
| POST | `/publicarRecebimentoMensagemTedInPubSub` | PublicarRecebimentoMensagemTedInPubSubController | Publica TED In no Pub/Sub |
| POST | `/enviarNotificacaoSpag/{cdLancamento}` | RabbitController | Envia notificação CASHOUT para SPAG via RabbitMQ |
| GET | `/service-status/status` | ServiceStatusController | Retorna status de todos os serviços monitorados |
| POST | `/spbcore/db/execute/{schema}` | SPBCoreDBController | Executa queries dinâmicas em SPBBMensageriaExterna/Historico |
| GET | `/spb-legado/processamento/registros` | SpbLegadoProcessamentoController | Lista movimentos por status (PROCESSANDO/EFETIVADO/ERRO) |
| GET | `/spb-legado/processamento/totais` | SpbLegadoProcessamentoController | Retorna totais de movimentos por status |
| POST | `/catalogo/validar-mensagem/xml` | ValidarMensagemCatalogoBCBController | Valida XML contra catálogo Bacen (XSD) |
| GET | `/spb-legado/cadastro-mensagens` | SpbLegadoController | Lista mensagens Bacen cadastradas com validações TED |
| POST | `/procedure/realizarRollback` | ProcedureController | Processa arquivo SQL e gera scripts de rollback |
| POST | `/comunicado-gmud/enviar-email` | ComunicadoGmudController | Envia email de comunicado GMUD |
| POST | `/envioMensagemClearing` | EnvioMensagemClearingController | Envia XML criptografado para fila Clearing |

---

## 5. Principais Regras de Negócio

1. **Rastreamento Multi-Sistema**: Correlaciona movimentos entre SPAG, PGFT, SPBCore e SPBLegado usando cdLancamento, cdOperacaoSPB, dsHeader e nuOp
2. **Criptografia Obrigatória**: Todas mensagens para câmaras Bacen devem ser criptografadas via SPBSecJava (Evaltec) antes do envio
3. **Seleção de Fila por ISPB**: Banco remetente 655 usa fila BV, 413 usa BVSA, Clearing usa fila específica
4. **Validação Horário Útil**: Schedules executam apenas 8h-19h em dias úteis (não finais de semana)
5. **Validação Data Movimento**: Operações SPB validam se data movimento = data atual (tb_pmge_parametro_geral)
6. **Mensagens Abertura SPB**: Sistema monitora recebimento obrigatório de STR0017 e PAG0102 para 413/655 BCB/Núclea
7. **Status Serviços**: OK (funcionando), WARN (processando/lento), DOWN (falha) com latência em ms
8. **Validação TED**: Mensagens TED devem ser R1/R2 com ação, R2 deve ser crédito
9. **Contingência Bacen**: Valida flag contingência STR (STR0008 stop_id=17 EGEN0152)
10. **Retry Criptografia**: 3 tentativas em falha de conexão com servidor EVAL
11. **Cache Token OAuth**: Tokens reutilizados até 15s antes da expiração
12. **Limite Queries**: SELECT dinâmicas limitadas a 100 registros por segurança
13. **Geração NSU**: Após inserção movimento STR, gera NSU aleatório para rastreamento
14. **Aprovação Movimento**: Movimentos STR devem ser aprovados via procedure sp_ge_atualiza_status_008
15. **DLQ Pub/Sub**: Mensagens com falha vão para DLQ com ACK manual

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **LancamentoSpag**: Lançamento SPAG com relacionamentos 1:N para LancamentoPessoa (favorecido/remetente), LancamentoClienteFintech e NotificacaoFintech
- **LancamentoPgft**: Lançamento PGFT com estrutura similar (favorecido, remetente, fintech)
- **MovimentoSPBCore**: Movimento no SPB Core identificado por cdMovimento, nmOrigem e cdMovimentoOrigem
- **MovimentoSPBLegado**: Movimento no sistema legado (tb_movi_movimento) com relacionamentos para tb_usua_usuario, tb_stop_situacao_operacao, tb_erms_erro_mensagem
- **MensagemBacen**: Cadastro de mensagens Bacen (tb_msbc_mensagem_bacen) com flags emissor/receptor/enviaLegado
- **ServiceStatus**: Status de serviços com histórico de latência e causas de falha
- **MensagemEco**: Mensagem ECO (GEN0001) com contadores de postada/entregue/lida/respondida

**Relacionamentos:**
- Lançamento → Pessoas (1:N)
- Lançamento → Notificações (1:N)
- Movimento → Usuário (N:1)
- Movimento → Situação Operação (N:1)
- Movimento → Mensagem Bacen (N:1)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbLancamento | tabela | SELECT | Lançamentos SPAG com favorecido, remetente, fintech |
| TbLancamentoPessoa | tabela | SELECT | Pessoas relacionadas aos lançamentos SPAG |
| TbLancamentoClienteFintech | tabela | SELECT | Clientes fintech dos lançamentos SPAG |
| TbNotificacaoFintech | tabela | SELECT | Notificações de lançamentos SPAG |
| DBPGF_TES..TBL_LANCAMENTO | tabela | SELECT | Lançamentos PGFT com joins para pessoas e fintech |
| TbMovimento | tabela | SELECT | Movimentos SPB Core (SPBBMensageriaExterna) |
| DBISPB..tb_movi_movimento | tabela | SELECT | Movimentos SPB Legado com situação e erros |
| DBISPB..tb_mvsr_movimento_str | tabela | SELECT | Movimentos STR detalhados (100+ campos) |
| DBISPB..tb_msbc_mensagem_bacen | tabela | SELECT | Cadastro de mensagens Bacen com flags |
| DBISPB..tb_pmge_parametro_geral | tabela | SELECT | Data movimento atual do sistema |
| DBISPB..tb_usua_usuario | tabela | SELECT | Usuários do sistema legado |
| DBISPB..tb_stop_situacao_operacao | tabela | SELECT | Situações de operações (processando, efetivado, erro) |
| DBISPB..tb_erms_erro_mensagem | tabela | SELECT | Erros de processamento de mensagens |
| DBISPB..tb_mvgn_movimento_gen | tabela | SELECT | Movimentos genéricos (ECO) |
| DBISPB..tb_ctfm_ctrl_fluxo_mqseries | tabela | SELECT | Controle de fluxo MQ (postada/entregue/lida/respondida) |
| DBISPB..tb_mvpg_movimento_pag | tabela | SELECT | Movimentos de pagamento |
| tb_service_status_current | tabela | SELECT | Status atual dos serviços monitorados (H2) |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBISPB..tb_movi_movimento | tabela | INSERT | Inserção de novos movimentos STR |
| DBISPB..tb_movi_movimento | tabela | DELETE | Expurgo de movimentos de teste |
| DBISPB..tb_mvsr_movimento_str | tabela | INSERT | Inserção de detalhes de movimentos STR |
| DBISPB..tb_mvsr_movimento_str | tabela | DELETE | Expurgo de detalhes de movimentos de teste |
| DBISPB..tb_movi_nsu | tabela | INSERT | Inserção de NSU para rastreamento |
| DBISPB..sp_ge_atualiza_status_008 | procedure | EXECUTE | Aprovação de movimentos (atualiza status) |
| tb_service_status_current | tabela | INSERT | Inserção de novo status de serviço (H2) |
| tb_service_status_current | tabela | UPDATE | Atualização de status existente (H2) |
| tb_service_status_current | tabela | DELETE | Limpeza de todos os status (H2) |
| SPBBMensageriaExterna | schema | UPDATE | Queries dinâmicas via endpoint (sanitizadas) |
| SPBBMensageriaHistorico | schema | UPDATE | Queries dinâmicas via endpoint (sanitizadas) |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| *.sql | leitura | ProcedureController | Arquivos SQL para geração de rollback |
| rollback_*.zip | gravação | ProcedureController | ZIP com scripts de rollback gerados |
| h2/schema.sql | leitura | H2SchemaInitalizer | Schema inicial do banco H2 |
| logback-spring.xml | leitura | Spring Boot | Configuração de logs (JSON format) |
| application.yml | leitura | Spring Boot | Configurações da aplicação |
| infra.yml | leitura | Kubernetes | Configurações de infraestrutura e secrets |
| docker-compose.yml | leitura | Docker Compose | Setup local Kafka/Zookeeper/Schema Registry |
| Dockerfile | leitura | Docker | Build multi-stage da aplicação |
| *.avsc | leitura | Kafka Schema Registry | Schemas Avro para mensagens Kafka |

---

## 10. Filas Lidas

| Nome da Fila | Tecnologia | Classe Responsável | Descrição |
|--------------|-----------|-------------------|-----------|
| business-spbb-base-recebimento-mensagem-spb-dlq-sub | Google Pub/Sub | PubSubTopicRepositoryService | DLQ para mensagens com falha no processamento |

---

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Responsável | Descrição |
|--------------|-----------|-------------------|-----------|
| envio-mensagem | Kafka (Avro) | EnvioMensagemTopicoController | Mensagens de envio para câmaras SPB |
| mensagem-processada | Kafka (Avro) | MensagemProcessadaTopicoController | Mensagens processadas pelo SPB |
| mensagem-recebida-spb | Kafka (Avro) | MensagemRecebidaSpbController | Mensagens recebidas das câmaras |
| status-envio-mensagem | Kafka (Avro) | StatusEnvioMensagemTopicoController | Status de processamento de mensagens |
| ${pubsub.topics.confirmacao} | Google Pub/Sub | PubSubTopicRepositoryService | Confirmações de processamento |
| ${pubsub.topics.ted-in} | Google Pub/Sub | PubSubTopicRepositoryService | Mensagens TED In |
| ${pubsub.topics.recebimento-mensagem-spb-core} | Google Pub/Sub | PubSubTopicRepositoryService | Recebimento de mensagens SPB Core |
| events.business.notificationService | RabbitMQ | NotificacaoSpagRepository | Notificações CASHOUT para SPAG |
| ${ibm.mq.bv.queues.destino} | IBM MQ (655) | EnvioMensagemCamaraService | Mensagens para câmara Votorantim |
| ${ibm.mq.bvsa.queues.destino} | IBM MQ (413) | EnvioMensagemCamaraService | Mensagens para câmara BVSA |
| ${ibm.mq.clearing.queues.destino} | IBM MQ | EnvioMensagemClearingService | Mensagens para Clearing |

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição | Autenticação |
|----------------|------|-----------|--------------|
| API Gateway Boleto | REST | Consulta e registro de boletos | Basic Auth |
| API Gateway TEF | REST | Execução de transferências eletrônicas | OAuth2 Client Credentials |
| API Gateway ECO | REST | Envio de mensagens ECO para verificação SPB | OAuth2 Client Credentials |
| API Gateway STR | REST | Inserção de operações STR no sistema legado | OAuth2 Client Credentials |
| SPBSecJava (Evaltec) | TCP | Criptografia de mensagens para Bacen | Conexão pool (porta 5000) |
| IBM MQ Câmaras | JMS | Envio de mensagens para câmaras 655/413/Clearing | User/Password |
| RabbitMQ SPAG | AMQP | Notificações de lançamentos para SPAG | User/Password |
| Google Cloud Pub/Sub | Pub/Sub | Publicação/consumo de eventos SPB | GCP Credentials |
| Apache Kafka | Kafka | Streaming de mensagens SPB (Avro) | SASL/PLAIN |
| Schema Registry | REST | Registro de schemas Avro | API Key |
| MySQL SPAG | JDBC | Consulta de lançamentos e notificações | User/Password |
| MySQL PGFT | JDBC | Consulta de lançamentos PGFT | User/Password |
| Sybase DBISPB | JDBC | Operações no sistema legado SPB | User/Password |
| SMTP Server | SMTP | Envio de emails (GMUD, notificações) | User/Password |
| Catálogo Bacen | XSD | Validação de mensagens XML contra schemas | Local |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com camadas bem definidas (controller, service, repository)
- Uso adequado de padrões Spring (Dependency Injection, Configuration Properties)
- Implementação de retry e tratamento de erros em operações críticas (criptografia)
- Uso de DTOs e mappers para isolamento de camadas
- Configuração externalizada e suporte a múltiplos ambientes
- Logs estruturados em JSON
- Uso de Avro para serialização eficiente no Kafka
- Implementação de health checks e monitoramento de serviços
- Gestão adequada de recursos (DisposableBean para fechamento de conexões)

**Pontos de Melhoria:**
- Falta de testes unitários e de integração evidentes
- Alguns métodos muito extensos (ex: MovimentoController.rastreamento)
- Uso de Singleton com mutex em EncryptService pode causar gargalo
- Queries SQL dinâmicas com concatenação de strings (risco de SQL injection, mesmo com sanitização)
- Falta de documentação JavaDoc em classes críticas
- Mistura de responsabilidades em alguns controllers (ex: SPBCoreDBController executando queries dinâmicas)
- Uso de RestTemplate (deprecated) ao invés de WebClient
- Hardcoded values em alguns templates (BoletoGenerico, TefGenerica)
- Falta de circuit breakers em integrações externas críticas
- Logs com informações sensíveis em alguns pontos (mesmo com sanitização)

**Recomendações:**
1. Implementar testes automatizados (JUnit, Mockito, TestContainers)
2. Refatorar métodos longos em métodos menores e mais coesos
3. Migrar de RestTemplate para WebClient (reativo)
4. Implementar circuit breakers (Resilience4j) para integrações externas
5. Adicionar documentação JavaDoc completa
6. Revisar estratégia de singleton em EncryptService
7. Implementar prepared statements para queries dinâmicas
8. Adicionar métricas customizadas (Micrometer)

---

## 14. Observações Relevantes

1. **Ambiente de Teste**: Sistema projetado para apoio e testes, não para produção crítica
2. **Multi-Tenant**: Suporta operações para ISPB 413 (BVSA) e 655 (Votorantim) simultaneamente
3. **Horário de Operação**: Schedules limitados a 8h-19h em dias úteis para evitar processamento fora do horário SPB
4. **Criptografia Crítica**: Dependência forte da biblioteca SPBSecJava (Evaltec) para comunicação com Bacen
5. **Rastreabilidade**: Sistema permite rastreamento completo de movimentos entre 4 sistemas diferentes
6. **Validação Catálogo**: Implementa validação de mensagens contra catálogo oficial Bacen (XSD)
7. **Gestão de Contingência**: Monitora e valida flags de contingência do Bacen STR
8. **DLQ Management**: Implementa consumo manual de DLQ com ACK para reprocessamento
9. **Cache Inteligente**: Tokens OAuth e consultas de boleto com cache para otimização
10. **Rollback Automation**: Ferramenta para geração automática de scripts de rollback SQL
11. **GMUD Support**: Sistema de comunicação de mudanças via email HTML
12. **Health Dashboard**: Interface web (Thymeleaf) para visualização de status de serviços
13. **Schema Evolution**: Uso de Avro permite evolução de schemas sem quebra de compatibilidade
14. **Segurança**: Desabilitação de CSRF e permitAll em endpoints (apropriado para ambiente de teste interno)
15. **Observabilidade**: Logs estruturados JSON, métricas de latência, rastreamento de causas de falha

**Dependências Críticas:**
- Disponibilidade de servidores EVAL para criptografia
- Conectividade com IBM MQ das câmaras
- Acesso aos bancos de dados legados (Sybase DBISPB)
- Disponibilidade do Schema Registry Kafka
- Conectividade com Google Cloud Pub/Sub

**Riscos Identificados:**
- Singleton de criptografia pode ser ponto de falha único
- Queries dinâmicas podem expor vulnerabilidades se sanitização falhar
- Falta de circuit breakers pode causar cascata de falhas
- Dependência de horário do sistema para validações de data movimento