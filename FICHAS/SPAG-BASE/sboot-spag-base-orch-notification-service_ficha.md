# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-spag-base-orch-notification-service** é um serviço de orquestração de notificações de pagamentos e recebimentos para parceiros externos e canais internos. O sistema processa eventos de transações financeiras (TEF, TED, Boletos, Tributos, Débitos Veiculares) e distribui notificações através de múltiplos canais: APIs REST (parceiros), RabbitMQ (legado PGFT), Google Cloud Pub/Sub e Apache Kafka. Utiliza Apache Camel para roteamento de mensagens, implementa lógica de retry distribuído, validação TEF (Goleiro), enriquecimento de dados via ITP e cache Redis. Suporta feature toggles para habilitar/desabilitar funcionalidades e autenticação mTLS para parceiros.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **KafkaConfiguration** | Configuração de beans Kafka (producer/consumer), Schema Registry Confluent, serialização Avro |
| **PubSubConfiguration** | Configuração Google Cloud Pub/Sub, beans de publicação de mensagens |
| **RabbitMQConfiguration/RabbitMQSpagConfiguration** | Configuração de conexões RabbitMQ (PGFT e SPAG), exchanges, queues e listeners |
| **RedisConfiguration** | Configuração de cache Redis com Lettuce, TTL configurável |
| **NotificacaoRouter** | Rota Camel principal para orquestração de notificações (envio, retorno, erro, interna, parceiro) |
| **KafkaNotificationRouter** | Rota Camel para publicação de dados consolidados no Kafka (TransacaoPagamentoProcessada) |
| **PubSubNotificationRouter** | Rota Camel para envio de notificações via Google Pub/Sub |
| **MainService** | Orquestrador principal do processamento de notificações, controla retentativas e aplica Goleiro Validação TEF |
| **NotificacaoRepositoryImpl** | Registra envio/retorno/erro de notificações, consulta wallet tributos, notifica ITP |
| **NotificarParceiroRepositoryImpl** | Notifica parceiros externos via API Gateway com suporte a mTLS e retry logic |
| **GoleiroValidacaoRepositoryImpl** | Valida status TEF comparando SPAG vs Conta Corrente, corrige divergências automaticamente |
| **PagamentoRepositoryImpl** | Consulta e atualiza situação de pagamentos via atom-pagamento |
| **ItpRepositoryImpl** | Enriquece notificações com descrições SPB/ISPB e finalidades |
| **EnvioDadoConsolidadoMapper** | Mapeia PubSubNotificationEntry para schema Avro TransacaoPagamentoProcessada |
| **NotificarParceiroMapper** | Converte ParceiroNotificacaoDTO para diversos DTOs de notificação (Pagamento, Tributo, Genérico, Recebimento) |
| **FeatureToggleService** | Gerencia feature flags via ConfigCat (Goleiro TEF, publicação Kafka, mTLS, listas de transações) |
| **NotificationServiceController** | API REST para consulta de notificações por protocolo ou filtros com paginação |
| **FilasRabbitListener** | Listener da fila RabbitMQ events.business.SPAG-BASE.notificationService |

---

## 3. Tecnologias Utilizadas

- **Linguagem:** Java 11
- **Framework:** Spring Boot 2.x (parent arqt-base-master-springboot 4.0.7)
- **Integração/Roteamento:** Apache Camel 3.2.0
- **Mensageria:** 
  - RabbitMQ (Spring AMQP)
  - Apache Kafka (Confluent Cloud, Schema Registry)
  - Google Cloud Pub/Sub (Spring Cloud GCP)
- **Cache:** Redis (Spring Data Redis, Lettuce)
- **Serialização:** Apache Avro 1.11.4, JAXB, Gson
- **Segurança:** OAuth2 (APIs internas), mTLS (parceiros), BasicAuth (CCBD)
- **Feature Toggle:** ConfigCat
- **Build:** Maven 3.x
- **Testes:** JUnit 5, Mockito, AssertJ, CamelTestSupport, ArchUnit 0.19.0
- **Infraestrutura:** Kubernetes/OpenShift, Docker, Helm, Ansible
- **Observabilidade:** Spring Actuator, Prometheus, Grafana
- **Banco de Dados:** Oracle (via atom-pagamento, atom-notificacao)

---

## 4. Principais Endpoints REST

### Endpoints Expostos (API do Serviço)

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/baas/payment/notification/{protocol}` | NotificationServiceController | Consulta notificação por protocolo (hash) |
| GET | `/v1/baas/payment/notification/by-date` | NotificationServiceController | Consulta notificações por filtros com paginação |
| POST | `/v1/notificar-pagamento/` | NotificationServiceController | Mock para envio de notificação via RabbitMQ (teste) |

### Endpoints Consumidos (Integrações Externas)

| Método | Endpoint | Sistema Integrado | Descrição |
|--------|----------|-------------------|-----------|
| POST | `/v1/atacado/notificar-pagamento` | API Gateway BV | Notificação de pagamento parceiro (sem mTLS) |
| POST | `/v2/atacado/notificar-pagamento` | API Gateway BV | Notificação de pagamento parceiro (com mTLS) |
| POST | `/v1/atacado/gestao/pagamento-tributo-consumo/confirmar` | API Gateway BV | Confirmação de pagamento de tributo |
| GET | `/serviceNotificarTipoPagamento` | API Gateway BV | Consulta tipo de notificação por protocolo |
| POST | `/v1/inserirNotificacaoFintech` | serviceAtomNotificarEnvio | Registra envio de notificação |
| POST | `/v1/inserirControleRetornoNotificacao` | serviceAtomNotificarRetorno | Registra retorno de notificação |
| POST | `/v1/inserirNotificacaoErroFintech` | serviceAtomNotificarErro | Registra erro de notificação |
| GET | `/obterNotificacaoParceiroWalletTributos/{cdLancamento}` | atom-notificacao | Consulta notificação wallet tributos |
| GET | `/obterDadosPagamento/{cdLancamento}` | atom-pagamento | Consulta dados de pagamento |
| PUT | `/atualizarPagamento` | atom-pagamento | Atualiza situação de pagamento |
| GET | `/consultarMovimentacaoPorDocumento` | sboot-ccbd-base-atom-movimentacoes | Consulta movimentação CC para validação TEF |
| GET | `/ispb/operation-description/{codigo}` | springboot-sitp-base-gestao-fintech | Consulta descrição operação ISPB |
| GET | `/contigencia/finalidades/{id}` | springboot-sitp-base-gestao-fintech | Consulta descrição finalidade SPB |

---

## 5. Principais Regras de Negócio

1. **Controle de Retentativas:** Sistema realiza até 5 tentativas de notificação (configurável por parceiro), com retry distribuído entre aplicação e RabbitMQ DLQ.

2. **Goleiro Validação TEF:** Para liquidações TEF (tipos 1, 61, 62), valida status entre SPAG e Conta Corrente. Se divergente, corrige SPAG automaticamente. Interrompe notificação em caso de erro crítico.

3. **Roteamento de Notificações:** 
   - Notificações internas (cdOrigem específicos) vão para RabbitMQ + Pub/Sub
   - Notificações externas vão para API Gateway parceiros + Pub/Sub + Kafka

4. **Tipos de Mensagem:** Sistema diferencia 5 tipos de notificação:
   - Tipo 1: Recebimentos (TED In) - confidencial
   - Tipo 2: Pagamentos V1 (legado)
   - Tipo 3: Tributos
   - Tipo 4/6: Pagamentos V2 (API genérica)
   - Tipo 5: Notificação genérica

5. **Validação de Protocolo:** Hash de validação tem validade de 3600 segundos (configurável).

6. **Publicação Kafka:** Dados consolidados são publicados no Kafka apenas para liquidações válidas (TED, TEF, Boletos, Tributos, Débitos Veiculares) e quando feature toggle habilitado.

7. **Classificação de Transações:** Sistema classifica cdTransacao como Tributos ou Débitos Veiculares baseado em listas configuradas via feature toggle.

8. **Mapeamento de Status:** 
   - Status 3 (Confirmado) → Sucesso
   - Status 4/99 → Erro
   - Status 8 → Rejeitado origem
   - Status 14 → Devolvido
   - Demais → Em processamento

9. **Enriquecimento de Dados:** Notificações são enriquecidas com descrições ISPB e finalidades SPB via integração com ITP.

10. **Autenticação mTLS:** Roteamento para endpoint mTLS controlado por feature toggle (ft_boolean_spag_base_mtls_toggle).

---

## 6. Relação entre Entidades

### Entidades Principais

**ParceiroNotificacaoDTO**
- Contém: cdLancamento, cdOrigem, stLancamento, tpMensagem, tpLancamento, dados de remetente/favorecido
- Relaciona-se com: DadosPagamento, NotificationEntry

**DadosPagamento**
- Contém: dados completos do pagamento/recebimento
- Relaciona-se com: TbLancamento (BD), NotificationEntry

**NotificationEntry**
- Contém: protocolo, status, dados de transação, SPB, billing
- Relaciona-se com: PubSubNotificationEntry, TransacaoPagamentoProcessada

**PubSubNotificationEntry**
- Versão Pub/Sub de NotificationEntry
- Relaciona-se com: TransacaoPagamentoProcessada (Kafka)

**TransacaoPagamentoProcessada (Avro)**
- Schema Kafka para dados consolidados
- Contém: protocolo, tipo liquidação, remetente, favorecido, valores, status

**NotificarEnvioParceiro<T>**
- Envelope genérico para notificações de parceiros
- Tipos: LancamentoNotificarParceiroDTO, LancamentoNotificarTributoParceiroDTO, NotificarGenerico, NotificarRecebimentoDTO

### Relacionamentos

```
ParceiroNotificacaoDTO → DadosPagamento → NotificationEntry → PubSubNotificationEntry → TransacaoPagamentoProcessada
                      ↓
                NotificarEnvioParceiro<T> → API Parceiro
```

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbLancamento | tabela | SELECT | Consulta dados de pagamentos/recebimentos via atom-pagamento |
| TbNotificacaoFintech | tabela | SELECT | Consulta histórico de notificações enviadas |
| TbControleRetornoNotificacao | tabela | SELECT | Consulta retornos de notificações |
| TbNotificacaoErroFintech | tabela | SELECT | Consulta erros de notificações |
| TbNotificacaoWallet | tabela | SELECT | Consulta notificações wallet tributos |
| MovimentacaoCC (CCBD) | tabela | SELECT | Consulta movimentações Conta Corrente para validação TEF |
| IspbOperationDescription (ITP) | tabela | SELECT | Consulta descrições de operações ISPB |
| Finalidades (ITP) | tabela | SELECT | Consulta descrições de finalidades SPB |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbNotificacaoFintech | tabela | INSERT | Registra envio de notificação para parceiro |
| TbControleRetornoNotificacao | tabela | INSERT | Registra retorno de notificação de parceiro |
| TbNotificacaoErroFintech | tabela | INSERT | Registra erro após esgotamento de retentativas |
| TbLancamento | tabela | UPDATE | Atualiza situação de pagamento (stLancamento, stSituacaoPagamento) via atom-pagamento |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| cacerts (volume Kubernetes) | leitura | Infraestrutura | Certificados SSL/TLS para mTLS |
| application.yml | leitura | Spring Boot | Configurações da aplicação por ambiente |
| infra.yml | leitura | Kubernetes/Helm | Definições de ConfigMaps, Secrets, recursos |

**Observação:** Sistema não processa arquivos de entrada/saída em disco. Toda comunicação é via APIs REST, filas de mensageria e banco de dados.

---

## 10. Filas Lidas

### RabbitMQ

| Nome da Fila | Tipo | Sistema | Descrição |
|--------------|------|---------|-----------|
| events.business.SPAG-BASE.notificationService | RabbitMQ | SPAG | Fila principal de entrada para notificações de parceiros |
| events.business.SPAG-BASE.notificationServiceWaiting | RabbitMQ | SPAG | Fila de espera para retry de notificações |

### Kafka

| Nome do Tópico | Tipo | Sistema | Descrição |
|----------------|------|---------|-----------|
| N/A | Kafka | N/A | Sistema não consome tópicos Kafka, apenas produz |

---

## 11. Filas Geradas

### RabbitMQ

| Nome da Fila/Exchange | Tipo | Sistema | Descrição |
|----------------------|------|---------|-----------|
| events.business.esteiraPagamentoOk | RabbitMQ | PGFT | Notificação de sucesso para canais internos |
| events.business.esteiraPagamentoErro | RabbitMQ | PGFT | Notificação de erro para canais internos |
| events.business.SPAG-BASE.notificationServiceWaiting | RabbitMQ | SPAG | Fila de retry para notificações com falha |

### Kafka

| Nome do Tópico | Tipo | Sistema | Descrição |
|----------------|------|---------|-----------|
| spag-base-transacao-pagamento-processada | Kafka | Confluent Cloud | Dados consolidados de transações processadas (schema Avro) |

### Google Cloud Pub/Sub

| Nome do Tópico | Tipo | Sistema | Descrição |
|----------------|------|---------|-----------|
| business-spag-base-notification-service | Pub/Sub | GCP | Notificações de pagamentos/recebimentos para consumidores internos |

---

## 12. Integrações Externas

| Sistema Externo | Tipo | Protocolo | Descrição |
|-----------------|------|-----------|-----------|
| API Gateway BV | API REST | HTTPS (OAuth2/mTLS) | Notificação de pagamentos/tributos para parceiros externos |
| atom-pagamento | API REST | HTTPS (OAuth2) | Consulta e atualização de dados de pagamentos |
| atom-notificacao | API REST | HTTPS (OAuth2) | Registro de envio/retorno/erro de notificações |
| sboot-ccbd-base-atom-movimentacoes | API REST | HTTPS (BasicAuth) | Consulta movimentações CC para validação TEF (Goleiro) |
| springboot-sitp-base-gestao-fintech | API REST | HTTPS (OAuth2) | Enriquecimento com descrições ISPB e finalidades SPB |
| RabbitMQ PGFT | Mensageria | AMQP | Notificações para canais internos legados |
| RabbitMQ SPAG | Mensageria | AMQP | Fila de entrada e retry de notificações |
| Redis SPAG | Cache | Redis Protocol | Cache de consultas de notificações |
| Kafka Confluent Cloud | Mensageria | Kafka Protocol | Publicação de dados consolidados (Avro) |
| Confluent Schema Registry | Schema Registry | HTTPS | Registro e validação de schemas Avro |
| Google Cloud Pub/Sub | Mensageria | gRPC/HTTPS | Publicação de notificações para consumidores GCP |
| ConfigCat | Feature Toggle | HTTPS | Gerenciamento de feature flags |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- **Arquitetura bem estruturada:** Separação clara entre camadas (domain, application, common) e uso adequado de Apache Camel para orquestração
- **Padrões de projeto:** Uso consistente de Repository, Mapper, Processor e Service patterns
- **Testabilidade:** Cobertura de testes unitários com JUnit 5, Mockito e CamelTestSupport; testes arquiteturais com ArchUnit
- **Configuração externalizada:** Uso de ConfigMaps, Secrets e Feature Toggles para gerenciar configurações por ambiente
- **Observabilidade:** Integração com Actuator, Prometheus e Grafana para monitoramento
- **Resiliência:** Implementação de retry distribuído, circuit breaker e validação TEF (Goleiro)
- **Documentação técnica:** Código bem comentado e estrutura de classes autoexplicativa

**Pontos de Melhoria:**
- **Complexidade de roteamento:** Rotas Camel com múltiplos processadores podem dificultar manutenção; considerar simplificação ou documentação adicional
- **Acoplamento com feature toggles:** Lógica de negócio dependente de flags pode gerar complexidade; avaliar estratégia de remoção de flags obsoletas
- **Tratamento de exceções:** Alguns fluxos poderiam ter tratamento de erro mais granular e mensagens mais descritivas
- **Testes de integração:** Estrutura preparada mas implementação incompleta (comentário "N/A" em alguns testes)
- **Documentação de APIs:** Falta especificação OpenAPI/Swagger para endpoints REST expostos

---

## 14. Observações Relevantes

1. **Arquitetura Híbrida:** Sistema opera com múltiplas tecnologias de mensageria (RabbitMQ legado, Kafka moderno, Pub/Sub cloud) para suportar migração gradual de infraestrutura.

2. **Goleiro TEF Crítico:** Validação TEF é essencial para integridade transacional, comparando status entre SPAG e Conta Corrente. Divergências são corrigidas automaticamente, mas erros críticos interrompem notificação.

3. **Feature Toggles Extensivos:** Sistema usa ConfigCat para controlar múltiplas funcionalidades:
   - `ft_boolean_notificacao_goleiro_tef_habilitado`: Habilita/desabilita Goleiro TEF
   - `ft_boolean_publicacao_transacao_consolidado`: Controla publicação Kafka
   - `ft_boolean_spag_base_mtls_toggle`: Ativa autenticação mTLS para parceiros
   - `ft_text_spag_consolidado_transacoes_*`: Listas de códigos de transação

4. **Schema Avro Versionado:** Dados consolidados publicados no Kafka usam schema Avro registrado no Confluent Schema Registry, garantindo compatibilidade entre versões.

5. **Retry Distribuído:** Lógica de retry implementada em dois níveis:
   - Aplicação: MainService controla até 5 tentativas
   - RabbitMQ: Fila DLQ (notificationServiceWaiting) para reprocessamento

6. **Segurança Multi-Camada:**
   - OAuth2 para APIs internas (atom-*, sitp-*)
   - mTLS para parceiros externos (API Gateway)
   - BasicAuth para CCBD
   - Secrets gerenciados via Kubernetes/Ansible

7. **Suporte a Múltiplos Tipos de Pagamento:** Sistema processa TED, TEF, Boletos, Tributos e Débitos Veiculares com lógicas específicas para cada tipo.

8. **Cache Redis:** Implementado para consultas de notificações (`consultaNotificacao`) com TTL configurável, reduzindo carga no banco de dados.

9. **Infraestrutura Kubernetes:** Deploy em OpenShift com:
   - Resources: 50m-250m CPU, 768Mi-1024Mi memória
   - Probes: liveness/readiness em `/actuator/health`
   - Volumes: cacerts para certificados, LDAP para autenticação
   - ServiceAccount: ksa-spag-base-21966

10. **Observabilidade Completa:** Métricas expostas em `/actuator/prometheus`, dashboards Grafana configurados, logs estruturados para análise.