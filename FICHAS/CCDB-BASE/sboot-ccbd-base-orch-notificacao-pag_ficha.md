# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-ccbd-base-orch-notificacao-pag** é um serviço de orquestração responsável por gerenciar notificações de pagamentos no contexto do Banco Digital (CCBD). Ele processa eventos de pagamentos (boletos, TED, DOC, tributos e consumo), notifica sistemas parceiros (SPAG), envia notificações push para clientes via Salesforce Marketing Cloud, e atualiza sistemas de prevenção à fraude. O sistema consome mensagens de filas RabbitMQ e tópicos Google Pub/Sub, orquestrando fluxos complexos de notificação com base no tipo de liquidação e status do pagamento.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot que inicializa a aplicação |
| `NotificacaoServiceImpl` | Implementa a lógica de negócio para notificações de sucesso, erro e push |
| `EventListener` | Listener RabbitMQ que consome eventos de pagamento (sucesso/erro) |
| `NotificacaoPushListener` | Listener Google Pub/Sub que consome eventos de movimentação para notificação push |
| `NotificacaoRouter` | Roteador Apache Camel que direciona notificações de cobrança, consumo e tributo |
| `StatusPagamentoRouter` | Roteador Apache Camel que processa status de pagamento (sucesso/erro) |
| `MovimentoRouter` | Roteador Apache Camel que processa movimentações TED/DOC de entrada |
| `NotificacaoTedOutRouter` | Roteador Apache Camel que processa TED de saída (sucesso/erro) |
| `NotificacaoFraudesRouter` | Roteador Apache Camel que envia notificações para sistema de fraudes |
| `NotificacaoRepositoryImpl` | Implementa chamadas REST para notificar pagamentos de cobrança e consumo |
| `ConsultarDadosBoletoRepositoryImpl` | Consulta detalhes de boletos pagos |
| `NotificacaoPushRepositoryImpl` | Envia notificações push para fila RabbitMQ |
| `NotificacaoPushSalesforceRepositoryImpl` | Envia notificações push via API Salesforce Marketing Cloud |
| `ConsultaCpfCnpjPorContaRepositoryImpl` | Consulta dados cadastrais (CPF/CNPJ) por conta corrente |
| `ConsultarNotificacaoPorProtocoloRepositoryImpl` | Consulta notificações SPAG por protocolo |
| `NotificacaoFraudesRepositoryImpl` | Publica mensagens de status de fraude em fila RabbitMQ |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.x** (framework principal)
- **Apache Camel** (orquestração de rotas e processamento de mensagens)
- **RabbitMQ** (mensageria para consumo e publicação de eventos)
- **Google Cloud Pub/Sub** (consumo de eventos de movimentação)
- **Spring Security OAuth2** (autenticação e autorização)
- **Swagger/OpenAPI** (documentação de APIs)
- **RestTemplate** (cliente HTTP para integrações REST)
- **Lombok** (redução de boilerplate)
- **Jackson** (serialização/deserialização JSON)
- **Micrometer + Prometheus** (métricas e monitoramento)
- **Grafana** (visualização de métricas)
- **JUnit 5 + Mockito** (testes unitários)
- **Docker** (containerização)
- **Maven** (gerenciamento de dependências e build)
- **Logback** (logging)
- **Feature Toggle** (controle de funcionalidades via flags)

---

## 4. Principais Endpoints REST

Não se aplica. Este componente não expõe endpoints REST próprios; ele atua como orquestrador consumindo eventos de filas e tópicos, e integrando-se com APIs externas.

---

## 5. Principais Regras de Negócio

1. **Roteamento por Tipo de Liquidação**: Direciona notificações para fluxos específicos (cobrança, consumo, tributo, TED, DOC) com base no código de liquidação (entidadeLiquidante).

2. **Notificação de Parceiros SPAG**: Notifica sistemas parceiros sobre confirmação ou rejeição de pagamentos via APIs REST.

3. **Notificação Push Condicional**: Envia notificações push para clientes apenas para operações TED/DOC de entrada (crédito), excluindo débitos e portabilidades.

4. **Atualização de Sistema de Fraudes**: Publica status de pagamento (aprovado/reprovado) em fila para sistema de prevenção à fraude (Feedzai).

5. **Retry com DLQ**: Implementa mecanismo de retry (até 5 tentativas) para mensagens com falha, enviando para Dead Letter Queue (DLQ) após esgotadas as tentativas.

6. **Feature Toggle para Migração**: Utiliza flag `ft_boolean_digital_ppbd_pgto_migracao_confirmacao_pagamento_boleto` para controlar se confirmações de boletos devem ser processadas pelo fluxo legado ou novo (ppbd-pgto).

7. **Enriquecimento de Dados**: Consulta dados cadastrais (CPF/CNPJ, nome titular) e detalhes de boletos antes de enviar notificações.

8. **Mapeamento de Status**: Converte códigos de status entre sistemas (SPAG ↔ CCBD) para garantir consistência.

9. **Validação de Transações**: Filtra transações de portabilidade e débitos para não enviar notificações push indevidas.

10. **Formatação de Mensagens Push**: Personaliza mensagens push com valores monetários formatados e nomes de pagadores/recebedores.

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **ParametrosNotificacao**: Contém dados de protocolo, status, datas e entidade liquidante para notificação de pagamentos.
- **MensagemCashOut**: Representa evento de pagamento recebido via RabbitMQ (sucesso/erro).
- **MovimentoMessage**: Representa evento de movimentação recebido via Pub/Sub para notificação push.
- **DetalhesBoleto**: Contém informações detalhadas de boleto (beneficiário, valor, CPF/CNPJ remetente).
- **StatusFraudes**: Representa status de operação para sistema de fraudes.
- **MessagePush**: Contém dados formatados para envio de notificação push (título, mensagem, deeplink, documentos).
- **NotificationSpag**: Representa notificação retornada pela API SPAG.
- **ContaCorrenteGlobal**: Representa dados de conta corrente consultados no sistema Global.

**Relacionamentos:**
- `ParametrosNotificacao` → `DadosPagamento` (composição)
- `DadosPagamento` → `Ocorrencia` (composição)
- `MovimentoMessage` é enriquecido com dados de `ContaCorrenteGlobal`
- `ParametrosNotificacao` é transformado em `StatusFraudes` para notificação de fraudes
- `NotificationSpag` é transformado em `MessagePush` para notificações TED Out

---

## 7. Estruturas de Banco de Dados Lidas

Não se aplica. O sistema não acessa diretamente bancos de dados; todas as consultas são realizadas via APIs REST de outros microserviços.

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema não realiza operações diretas de escrita em banco de dados; as atualizações são realizadas via APIs REST de outros microserviços.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `application.yml` | Leitura | Spring Boot | Arquivo de configuração da aplicação (profiles, URLs, credenciais) |
| `logback-spring.xml` | Leitura | Logback | Configuração de logging (console, formato JSON) |
| `swagger/*.yaml` | Leitura | Swagger Codegen | Especificações OpenAPI para geração de clientes REST |

---

## 10. Filas Lidas

| Nome da Fila | Tipo | Descrição |
|--------------|------|-----------|
| `events.business.CCBD-BASE.retornoPagamentoSucessoOK` | RabbitMQ Queue | Consome eventos de pagamentos confirmados com sucesso |
| `events.business.CCBD-BASE.retornoPagamentoErro` | RabbitMQ Queue | Consome eventos de pagamentos com erro/rejeição |
| `projects/{env}/subscriptions/business-ccbd-base-monitora-creditos-sub` | Google Pub/Sub Subscription | Consome eventos de movimentação de contas para notificação push |

---

## 11. Filas Geradas

| Nome da Fila/Exchange | Tipo | Descrição |
|-----------------------|------|-----------|
| `ex.ccbd.notificacao.fraudes` (routing key: `ccbd.atualizarFeedzai.v1`) | RabbitMQ Exchange | Publica status de pagamento para sistema de prevenção à fraude |
| `notificacao_pagamento_boleto` | RabbitMQ Queue | Publica notificações push de pagamento de boleto |
| `events.business.retornoPagamentoSucessoOK.DLQ` | RabbitMQ Exchange (DLQ) | Dead Letter Queue para mensagens de sucesso com falha no processamento |
| `events.business.retornoPagamentoErro.DLQ` | RabbitMQ Exchange (DLQ) | Dead Letter Queue para mensagens de erro com falha no processamento |

---

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| **sboot-ccbd-base-atom-pgto-trib-bol** | REST API | Notifica pagamentos de duplicata, consumo e tributos; consulta detalhes de boletos |
| **sboot-gnms-base-orch-envio-push** | REST API | Envia notificações push via Salesforce Marketing Cloud |
| **sboot-glob-base-atom-cliente-dados-cadastrais** | REST API | Consulta dados cadastrais (CPF/CNPJ, nome) por conta corrente |
| **sboot-spag-base-orch-notificar-parceiro** | REST API | Consulta notificações SPAG por protocolo |
| **API Gateway BV** | OAuth2 | Autenticação e autorização via token JWT |
| **Google Cloud Pub/Sub** | Mensageria | Consumo de eventos de movimentação de contas |
| **RabbitMQ** | Mensageria | Consumo e publicação de eventos de pagamento e fraude |
| **Feature Toggle Service** | REST API | Consulta flags de funcionalidades (ex: migração de confirmação de boletos) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7,5/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões hexagonais (ports/adapters)
- Uso adequado de Apache Camel para orquestração de fluxos complexos
- Separação clara entre camadas (domain, application, infrastructure)
- Boa cobertura de testes unitários
- Uso de Lombok para redução de boilerplate
- Configuração externalizada via application.yml
- Implementação de retry e DLQ para resiliência
- Uso de enums para constantes e mapeamentos
- Logging estruturado e adequado

**Pontos de Melhoria:**
- Alguns métodos longos com múltiplas responsabilidades (ex: `EventListener.esteiraPagamentoOk`)
- Lógica de negócio misturada com infraestrutura em alguns pontos
- Uso de `Gson` e `Jackson` simultaneamente (inconsistência)
- Falta de documentação JavaDoc em classes críticas
- Tratamento de exceções genérico em alguns listeners
- Hardcoding de valores em algumas classes (ex: routing keys, nomes de filas)
- Configuração de retry via propriedades poderia ser mais granular por rota
- Falta de validação de entrada em alguns pontos
- Alguns testes unitários apenas verificam ausência de exceções, sem validar comportamento

---

## 14. Observações Relevantes

1. **Migração de Fluxo**: O sistema possui lógica para migração gradual de confirmação de boletos do fluxo atual para um novo fluxo (ppbd-pgto), controlada por feature toggle.

2. **Múltiplos Canais de Entrada**: Consome eventos de duas fontes distintas (RabbitMQ e Pub/Sub), cada uma com propósito específico.

3. **Orquestração Complexa**: Utiliza Apache Camel para orquestrar fluxos com múltiplas etapas (consultas, transformações, notificações) de forma declarativa.

4. **Resiliência**: Implementa retry automático (até 5 tentativas) com delay configurável e DLQ para mensagens que falharam após todas as tentativas.

5. **Segurança**: Integração com API Gateway via OAuth2 JWT para autenticação em chamadas REST.

6. **Observabilidade**: Exposição de métricas via Micrometer/Prometheus e dashboards Grafana pré-configurados.

7. **Ambientes**: Suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas.

8. **Notificações Personalizadas**: Mensagens push são personalizadas com valores monetários formatados e nomes de pagadores/recebedores.

9. **Validação de Transações**: Filtra transações específicas (portabilidade, débitos) para evitar notificações indevidas.

10. **Mapeamento de Status**: Realiza conversão entre códigos de status de diferentes sistemas (SPAG ↔ CCBD) para garantir consistência nas notificações.