# Ficha Técnica do Sistema

---

## 1. Descrição Geral

Sistema orquestrador responsável por gerenciar o ciclo de vida de transações PIX realizadas via cartão de crédito no contexto de Conta Corrente Banco Digital (CCBD). O sistema processa notificações de crédito e estorno, coordenando operações entre o autorizador de cartão, sistema de transferências TEF e base de dados de transações. Utiliza Apache Camel para orquestração de fluxos e RabbitMQ para comunicação assíncrona.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `GerenciarTransacoesPixService` | Serviço principal que coordena a confirmação e estorno de transações PIX |
| `GerenciarTransacoesPixRouter` | Define as rotas Apache Camel para processamento de transações (confirmação, estorno total, estorno parcial) |
| `NotificacaoCreditoListener` | Listener RabbitMQ que consome notificações de crédito PIX da fila `ccbd_credito` |
| `NotificacaoEstornoListener` | Listener RabbitMQ que consome solicitações de estorno da fila `ccbd_estornar_pix_cartao` |
| `AutorizadorCartaoRepositoryImpl` | Implementação de integração com o autorizador de cartão (confirmação e desfazimento de lançamentos) |
| `TransferenciaTefRepositoryImpl` | Implementação de integração com sistema de transferências TEF para estornos |
| `ConsultarTransacaoRepositoryImpl` | Consulta transações PIX por EndToEndId |
| `ConsultarTransacaoPorSeqTransacaoRepositoryImpl` | Consulta transações PIX por sequencial |
| `AtualizarTransacaoRepositoryImpl` | Atualiza status de transações PIX |
| `GlobalRepositoryImpl` | Consulta dados cadastrais de pessoa/conta |
| `StatusConfirmacaoProcessor` | Processor Camel que atualiza status para CONCLUIDO |
| `ValidaTransacaoProcessor` | Processor Camel que valida se transação está em status válido para estorno |
| `ExtrairCodigoAutorizacaoProcessor` | Processor Camel que extrai código de autorização dos protocolos |

---

## 3. Tecnologias Utilizadas

- **Framework**: Spring Boot 2.x
- **Orquestração**: Apache Camel 3.0.1
- **Mensageria**: RabbitMQ (Spring AMQP), IBM MQ
- **Segurança**: Spring Security OAuth2 (Resource Server)
- **Documentação API**: Swagger/OpenAPI (Springfox 2.9.2)
- **Monitoramento**: Spring Actuator, Micrometer Prometheus
- **Banco de Dados**: HikariCP (pool de conexões)
- **Build**: Maven
- **Containerização**: Docker
- **Infraestrutura**: Kubernetes/OpenShift
- **Observabilidade**: Prometheus, Grafana
- **Testes**: JUnit 5, Mockito, RestAssured, Pact

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/banco-digital/conta/pix-credito/estornar` | `GerenciarTransacoesPixController` | Estorna uma transação PIX (endpoint definido no Swagger, implementação comentada) |

**Observação**: O sistema opera principalmente via mensageria (RabbitMQ), com endpoints REST secundários.

---

## 5. Principais Regras de Negócio

1. **Confirmação de Transação PIX**: Ao receber notificação de crédito com status de sucesso (código 10), confirma o lançamento no autorizador de cartão e atualiza status para CONCLUIDO
2. **Estorno por Falha PIX**: Ao receber notificação de falha PIX (status FALHA ou FALHA_NOTIFICACAO), inicia processo de estorno total
3. **Validação de Status para Estorno**: Apenas transações com status PENDENTE podem ser estornadas
4. **Estorno Total**: Executa estorno TEF, seguido de estorno no autorizador de cartão, atualizando status para ESTORNADO
5. **Estorno com Falha TEF**: Se o estorno TEF falhar, confirma o lançamento no cartão e marca como CONCLUIDO_SEM_PIX
6. **Tipos de Estorno**: Suporta 4 tipos - ESTORNO_TOTAL, ESTORNO_AUTORIZADOR, ESTORNO_AUTORIZADOR_BANCO_DADOS, ESTORNO_AUTORIZADOR_BANCO_DADOS_TEF
7. **Delay de Processamento**: Aguarda 2 segundos antes de confirmar transação e 3 segundos antes de estornar (para garantir consistência)
8. **Consulta de Dados Cadastrais**: Valida e enriquece dados da conta antes de processar estorno TEF
9. **Mapeamento de Bancos**: Utiliza enum BancoEnum para mapear códigos internos (161-BV, 436-BVSA) para códigos externos (655, 413)

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **Transacao**: Entidade central contendo dados da transação PIX (sqTransacao, endToEndId, vlPagamento, cdStatusProcessamento, etc.)
  - Relacionamento 1:1 com **Cartao** (dados do cartão utilizado)
  - Relacionamento 1:N com **Protocolo** (protocolos de TEF, CREDITO, END_TO_END)
  
- **Protocolo**: Representa protocolos gerados durante processamento (tipos: TEF, TEF_ESTORNO, CREDITO, CREDITO_ESTORNO, END_TO_END)

- **Notificacao**: Mensagem recebida via RabbitMQ contendo dados do evento PIX (id, actionType, document, mensagem)

- **PixPagamento**: Dados detalhados do pagamento PIX extraídos da notificação (endToEndId, statusOperacao, valorOperacao, etc.)

- **Autorizacao**: Dados para confirmação/estorno no autorizador de cartão

- **TransferenciaTefDigital**: Dados para execução de transferência TEF de estorno

**Enums de Controle:**
- **StatusProcessamentoEnum**: PENDENTE, CONCLUIDO, ESTORNADO, ESTORNO_INICIALIZADO, CONCLUIDO_SEM_PIX
- **TipoEstornoEnum**: Define tipo de estorno a ser executado
- **StatusOperacaoEnum**: Mapeia códigos de status PIX (1-14) para tipos (SUCESSO, FALHA, AGUARDAR)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| Transações PIX (via API) | API REST | SELECT | Consulta transações PIX por EndToEndId ou sequencial via serviço `sboot-ccbd-base-atom-pix-credito` |
| Dados Cadastrais Pessoa/Conta | API REST | SELECT | Consulta dados de pessoa e conta via serviço `sboot-glob-base-atom-cliente-dados-cadastrais` |

**Observação**: O sistema não acessa banco de dados diretamente, apenas via APIs REST de outros microserviços.

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| Transações PIX (via API) | API REST | UPDATE | Atualiza status de transações PIX via serviço `sboot-ccbd-base-atom-pix-credito` (endpoint PUT) |
| Autorizações Cartão (via API) | API REST | DELETE | Desfaz lançamentos no autorizador via serviço `sboot-cart-svhp-atom-autorizador` |
| Transferências TEF (via API) | API REST | INSERT | Cria transferências de estorno via serviço `sboot-spag-base-orch-transferencias` |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | `src/main/resources` | Configurações da aplicação (profiles, URLs de serviços, filas, etc.) |
| logback-spring.xml | Leitura | `/usr/etc/log` (runtime) | Configuração de logs (formato JSON, níveis, appenders) |
| Swagger YAML files | Leitura | `src/main/resources/swagger` | Definições OpenAPI para geração de clientes REST |

---

## 10. Filas Lidas

| Nome da Fila | Tecnologia | Descrição |
|--------------|-----------|-----------|
| `ccbd_credito` | RabbitMQ | Fila de notificações de crédito PIX (confirmações e falhas) consumida por `NotificacaoCreditoListener` |
| `ccbd_estornar_pix_cartao` | RabbitMQ | Fila de solicitações de estorno de transações PIX consumida por `NotificacaoEstornoListener` |

---

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Descrição |
|--------------|-----------|-----------|
| `QL.CART.PROC_PAGMT_CONTAS.INT` | IBM MQ | Fila para publicação de confirmações de lançamento no autorizador de cartão (via `AutorizadorCartaoRepositoryImpl`) |

---

## 12. Integrações Externas

| Sistema | Tipo | Descrição |
|---------|------|-----------|
| `sboot-ccbd-base-atom-pix-credito` | REST API | Consulta e atualização de transações PIX (GET por EndToEndId/SeqTransacao, PUT para atualizar status) |
| `sboot-cart-svhp-atom-autorizador` | REST API | Autorizador de cartão - desfazimento de lançamentos (DELETE `/v1/autorizacoes/{idAutorizacao}`) |
| `sboot-spag-base-orch-transferencias` | REST API | Sistema de transferências TEF para processamento de estornos (POST `/v1/transferencia`) |
| `sboot-glob-base-atom-cliente-dados-cadastrais` | REST API | Consulta de dados cadastrais de pessoa/conta (GET `/v1/banco-digital/conta/{nuConta}`) |
| Gateway OAuth | REST API | Obtenção de tokens JWT para autenticação nas APIs (via `GatewayOAuthService`) |
| RabbitMQ | Message Broker | Consumo de notificações de crédito e estorno |
| IBM MQ | Message Broker | Publicação de confirmações para autorizador de cartão |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7.5/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (application, domain, common)
- Uso adequado de padrões como Repository, Service e Processor
- Implementação de testes unitários, integração e funcionais
- Configuração externalizada e suporte a múltiplos ambientes
- Uso de Apache Camel para orquestração de fluxos complexos
- Tratamento de exceções customizado com enum de erros
- Documentação OpenAPI/Swagger
- Uso de Lombok para reduzir boilerplate

**Pontos de Melhoria:**
- Código de produção comentado no controller (`GerenciarTransacoesPixController`)
- Alguns testes com implementação vazia ou comentada
- Falta de validações de entrada em alguns pontos
- Delays hardcoded nas rotas Camel (2s e 3s) - poderiam ser configuráveis
- Alguns mappers com lógica complexa que poderiam ser simplificados
- Falta de documentação inline em métodos mais complexos
- Alguns métodos longos que poderiam ser refatorados (ex: `TransferenciaTefMapper.montarRequest`)
- Uso de `new ArrayList<>()` em vários pontos poderia ser substituído por `Collections.emptyList()` quando apropriado

---

## 14. Observações Relevantes

1. **Arquitetura Orientada a Eventos**: O sistema é predominantemente event-driven, processando mensagens assíncronas via RabbitMQ
2. **Orquestração com Apache Camel**: Utiliza rotas Camel para coordenar fluxos complexos de confirmação e estorno
3. **Resiliência**: Implementa tratamento de falhas com fluxos alternativos (ex: confirmar cartão se TEF falhar)
4. **Multi-banco**: Suporta múltiplos bancos (BV 161/655 e BVSA 436/413) com mapeamento via enum
5. **Segurança**: Integrado com OAuth2 para autenticação/autorização
6. **Observabilidade**: Configurado com Prometheus/Grafana para monitoramento
7. **Containerização**: Pronto para deploy em Kubernetes/OpenShift
8. **Profiles**: Suporta múltiplos ambientes (local, des, qa, uat, prd)
9. **Auditoria**: Integrado com trilha de auditoria do BV (`springboot-arqt-base-trilha-auditoria`)
10. **Código Legado**: Alguns endpoints REST estão definidos mas não implementados, sugerindo evolução do sistema de REST para mensageria

---