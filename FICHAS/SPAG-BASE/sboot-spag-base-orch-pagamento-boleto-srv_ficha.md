---
## Ficha Técnica do Sistema

### 1. Descrição Geral
Sistema orquestrador de pagamentos de boletos bancários desenvolvido em Spring Boot com Apache Camel. Responsável por gerenciar o fluxo completo de pagamento, desde a validação inicial até a liquidação final, incluindo integração com CIP (Câmara Interbancária de Pagamentos), débito em conta corrente, notificações e callbacks para parceiros externos. Suporta processamento síncrono e assíncrono através de feature toggles, com contingências e tratamento robusto de exceções.

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `PagamentoBoletoSrvService` | Orquestra o fluxo completo de pagamento através de rotas Apache Camel |
| `PagamentoBoletoSrvRouter` | Define rotas Camel para processamento assíncrono (inclusão, atualização, notificação) |
| `PagamentoBoletoSrvSincronoRouter` | Define rotas Camel para processamento síncrono (validação CIP, débito CC, confirmação) |
| `IntegrarPagamentoSrvRouter` | Decide entre fluxo novo SPAG ou legado (ITP/BVSA/modernização BaaS) |
| `ContaCorrenteSrvRouter` | Gerencia efetivação de movimento em conta corrente |
| `SuporteNegocioSrvRouter` | Validação de regras de negócio do boleto (V1/V2) |
| `ParceiroSrvRouter` | Validação e processamento de callbacks de parceiros externos |
| `ReprocessamentoBoletoRouter` | Reprocessamento de boletos com verificação de movimento em CC |
| `PagamentoBoletoMapper` | Conversões entre representations e objetos de domínio |
| `DefaultExceptionAdvice` | Handler global de exceções REST |
| `ExceptionControllerHandler` | Tratamento de exceções específicas por versão de API (V1-V4) |
| `PagamentoRepositoryImpl` | CRUD de pagamentos via API externa |
| `SuporteNegocioRepositoryImpl` | Validação e enriquecimento de dados do boleto |
| `ValidaRetornoCipRepositoryImpl` | Validação de boletos via CIP (V1 e V2) |
| `ContaCorrenteRepositoryImpl` | Efetivação de débito em conta corrente |
| `TransferenciaRepositoryImpl` | Envio de transferências para boletos VR (>R$250k) |
| `PagamentoITPRepositoryImpl` | Integração com fila ITP via RabbitMQ |
| `NotificacaoSpagRepositoryImpl` | Envio de notificações pós-pagamento |
| `LiquidarPagamentoRepositoryImpl` | Estorno de pagamentos |
| `ReprocessamentoBoletoPubSubListener` | Listener para reprocessamento via Google Cloud PubSub |

### 3. Tecnologias Utilizadas

- **Framework:** Spring Boot 2.3.x
- **Orquestração:** Apache Camel 3.2.0
- **Linguagem:** Java 11
- **Build:** Maven
- **Mensageria:** RabbitMQ (PGFT, SPAG), IBM MQ (BVSA), Google Cloud PubSub
- **REST Client:** RestTemplate com interceptors de logging
- **Segurança:** OAuth2 Resource Server, JWT
- **Documentação API:** Springfox (Swagger/OpenAPI)
- **Template Engine:** Apache Velocity (geração XML)
- **Serialização:** Jackson (JSON)
- **Testes:** JUnit 5, Mockito, ArchUnit
- **Logging:** Logback (formato JSON)
- **Métricas:** Prometheus/Actuator
- **Feature Toggle:** ConfigCat
- **Utilitários:** Lombok, Apache Commons

### 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/pagamento-boleto` | `PagamentoBoletoController` | Inclusão de pagamento boleto (fluxo assíncrono) |
| POST | `/v1/processar-callback-parceiro` | `PagamentoBoletoController` | Processamento de callback de parceiro externo |
| POST | `/v1/reprocessar-boleto` | `PagamentoBoletoController` | Reprocessamento manual de boleto |
| POST | `/v1/pagamento-boleto/manual/{cdLancamento}` | `PagamentoBoletoController` | Processamento manual de boleto específico |
| POST | `/v2/pagamento-boleto` | `PagamentoBoletoV2Controller` | Inclusão de pagamento boleto V2 (clientes Wallet) |
| POST | `/v3/pagamento-boleto` | `PagamentoBoletoV3Controller` | Inclusão de pagamento boleto V3 (formato Slip) |
| POST | `/v4/pagamento-boleto` | `PagamentoBoletoV4Controller` | Inclusão de pagamento boleto V4 (fluxo síncrono) |

### 5. Principais Regras de Negócio

- **Validação CIP:** Boletos são validados via CIP (Câmara Interbancária de Pagamentos) com contingência para NUCLEA em caso de falha
- **Limite Valor:** Boletos com valor superior a R$ 250.000,00 são processados via transferência VR ao invés de liquidação normal
- **Conta Mil-Mil-Contra:** Validação especial para conta 10000001 nos bancos 413 (BVSA) e 655 (BV)
- **Feature Toggle:** Processamento síncrono habilitado dinamicamente por banco, origem, CNPJ ou valor através de feature flags
- **Status Permitidos:** Reprocessamento permitido apenas para boletos com status SOLICITACAO_INCLUIDA
- **Validação Beneficiário:** Verificação de dados do beneficiário, valor e data limite de pagamento conforme retorno CIP
- **Estorno Automático:** Em caso de falha na integração após débito em conta, estorno é realizado automaticamente
- **Duplicidade:** Pagamentos duplicados retornam HTTP 208 (ALREADY_REPORTED)
- **Parceiros Externos:** Validação de modalidade (25-PF/26-PJ não permitidas para tipo integração 'E'), URL callback obrigatória, tipo cliente wallet
- **Enriquecimento de Dados:** Complementação automática de dados do remetente se conta for MilMilContra ou se faltarem códigos (banco, transação, evento)
- **Validação Remetente:** Para clientes fintech, consulta dados da conta CP1 e popula informações do remetente
- **Rejeição CIP:** Boletos com ocorrências na lista de baixa operacional são rejeitados automaticamente

### 6. Relação entre Entidades

**Entidades Principais:**

- **Boleto:** Entidade central contendo dados completos do pagamento (código de barras, valor, datas, status)
  - Relaciona-se com **PagamentoRemetente** (1:1) - dados do pagador
  - Relaciona-se com **PagamentoFavorecido** (1:1) - dados do beneficiário
  - Pode ter **PagamentoRemetenteFintech** (0:1) - dados específicos de cliente fintech
  - Pode ter **PagamentoFavorecidoFintech** (0:1) - dados específicos de favorecido fintech

- **PagamentoResponse:** Representa resposta completa do pagamento
  - Contém **DadosPagamento** (1:1) - informações do protocolo
  - Contém **PagamentoErro** (0:1) - detalhes de erro quando aplicável

- **SuporteNegocioResponse:** Resultado da validação de regras de negócio
  - Enriquece dados do **Boleto** com informações de transação e banco

- **Protocolo:** Representa o protocolo de pagamento gerado
  - Vinculado ao **Boleto** através do código de lançamento

- **IdentificadorTransacao:** Dados da transação produto
  - Utilizado para complementar informações do **Boleto**

**Relacionamentos de Integração:**

- **Parceria:** Dados do parceiro externo
  - Valida modalidade e tipo de integração do **Boleto**

- **Participante:** Dados do participante na recepção de boleto
  - Validado conforme origem da operação

- **DadosContaResponse:** Informações da conta fintech
  - Popula dados do **PagamentoRemetenteFintech**

### 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| não se aplica | - | - | Sistema não acessa banco de dados diretamente, todas operações são via APIs REST |

### 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| não se aplica | - | - | Sistema não atualiza banco de dados diretamente, todas operações são via APIs REST (API Pagamento) |

### 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `dicionario_boleto.xml` | leitura | `PagamentoBVSARepositoryImpl` (template Velocity) | Template para geração de XML de dicionário de pagamento enviado para esteira BVSA |
| `logback-spring.xml` | leitura | Configuração Spring Boot | Arquivo de configuração de logs em formato JSON para stdout |
| `application.yml` / `application-{profile}.yml` | leitura | Spring Boot Configuration | Arquivos de propriedades da aplicação por ambiente (local/des/qa/uat/prd) |

### 10. Filas Lidas

- **RabbitMQ SPAG:** Fila de reprocessamento de boletos (configurável via `spring.spag.rabbitmq.*`)
- **RabbitMQ PGFT:** Fila de callbacks de parceiros (configurável via `spring.pgft.rabbitmq.*`)
- **Google Cloud PubSub:** Subscription `reprocessarPagamentoBoletoChannel` para reprocessamento de boletos (listener `ReprocessamentoBoletoPubSubListener`)

### 11. Filas Geradas

- **RabbitMQ ITP:** `events.business.integrarPagamentoITP` - Mensagens de integração de pagamento ITP (`PagamentoITPMessage`)
- **RabbitMQ Liquidação:** `events.business.estornoPagamento` - Mensagens de estorno de pagamento (`RealizaEstornoRequest`)
- **RabbitMQ Notificação SPAG:** `events.business.notificationService` - Notificações pós-pagamento (`MensagemNotificacaoSpag`) com header `tipoMensagem=CASHOUT`
- **RabbitMQ Callback Parceiro:** `events.business.confirmarPagamentoApi` - Validação de parceiro (`ParceiroCallback`)
- **IBM MQ BVSA:** Fila configurável - XML de dicionário de pagamento gerado via template Velocity
- **Google Cloud PubSub:** Topic configurável via `solicitacaoPagamentoBoletoOutputChannel` - Solicitações de pagamento (`PagamentoSolicitadoPayload`)

### 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| `sboot-spag-base-atom-pagamento` | API REST | CRUD de protocolo de pagamento (inclusão, atualização, consulta detalhada, geração de autenticação bancária) |
| `sboot-spag-base-orch-suporte-negocio` | API REST | Validação de regras de negócio do boleto (V1/V2), enriquecimento de dados |
| `springboot-spag-base-valida-retorno-cip` | API REST | Consulta e validação de boleto via CIP (V1 e V2) |
| `sboot-spag-base-orch-transferencias` | API REST | Transferência bancária para boletos VR (valor > R$250k) |
| `sboot-ccbd-base-atom-movimentacoes` | API REST | Débito em conta corrente, consulta de movimentação por documento |
| `sboot-sitp-base-atom-integrar-pagamento` | API REST | Consulta de transação produto, consulta de banco |
| `sboot-spag-base-orch-liquidar-pagamento` | API REST | Realização de estorno de pagamento |
| `sboot-spag-base-atom-seguranca` | API REST | Validação de clientId e CNPJ |
| `sboot-spag-base-atom-parcerias` | API REST | Busca de parceiro por código de liquidação e número de conta |
| `sboot-spag-base-atom-recepcao-boleto` | API REST | Validação de participante por CNPJ/CPF e origem de operação |
| `springboot-spag-base-consulta-conta-fintech` | API REST | Consulta de dados de conta de usuário fintech (BasicAuth) |
| **ConfigCat** | Feature Toggle | Controle de feature flags para habilitar/desabilitar funcionalidades dinamicamente |
| **Gateway OAuth** | OAuth2 | Geração e validação de tokens JWT para autenticação |

### 13. Avaliação da Qualidade do Código

**Nota:** 8/10

**Justificativa:**

**Pontos Positivos:**
- Arquitetura hexagonal bem definida (domain/application/infrastructure)
- Uso adequado de Apache Camel para orquestração de fluxos complexos
- Mappers dedicados para conversão entre camadas (separation of concerns)
- Cobertura de testes unitários presente (controllers, repositories, mappers, processors)
- Exception handling estruturado com hierarquia clara (`RouterFlowException`, `PagamentoBoletoException`)
- Uso de Lombok reduz significativamente boilerplate
- Configurações externalizadas por ambiente
- Feature toggles permitem deploy contínuo com controle de funcionalidades
- Logging estruturado em JSON
- Interceptors para logging de requisições REST
- Validação arquitetural via ArchUnit

**Pontos de Melhoria:**
- Rotas Camel muito extensas e complexas, dificultando manutenção (ex: `PagamentoBoletoSrvRouter`, `PagamentoBoletoSrvSincronoRouter`)
- Acoplamento moderado entre processors e contexto Camel (uso intensivo de properties no Exchange)
- Falta de documentação inline em classes críticas
- Alguns processors com responsabilidades múltiplas (ex: `ComplementarBoletoSuporteNegocioProcessor`)
- Uso de constantes mágicas em alguns pontos (poderia ser enum)
- Testes de integração ausentes (apenas unitários)
- Falta de circuit breaker explícito para integrações externas (apenas retry)

### 14. Observações Relevantes

- **Fluxos Dual:** Sistema suporta tanto processamento síncrono quanto assíncrono através de feature toggles, permitindo migração gradual entre modelos
- **Contingência CIP:** Em caso de falha na validação CIP, sistema possui fallback para NUCLEA (feature toggle controlado)
- **Retry Logic:** Implementado para integrações críticas (ex: confirmação de pagamento com 3 tentativas)
- **Multi-Ambiente:** Configurações específicas para des/qa/uat/prd via arquivos YAML
- **Métricas:** Prometheus habilitado via Spring Actuator para monitoramento
- **Sanitização de Logs:** Implementada via `LogUtil` para evitar exposição de dados sensíveis
- **Validação Arquitetural:** Profile Maven `archunit` para garantir conformidade com padrões arquiteturais
- **Modernização BaaS:** Feature toggle específico para habilitar integração com nova plataforma BaaS
- **Processamento Manual:** Endpoint dedicado para reprocessamento manual de boletos com validação de status
- **Callback Assíncrono:** Suporte a parceiros externos com callback de validação de pagamento
- **Estorno Automático:** Mecanismo de compensação em caso de falha após débito em conta
- **Versionamento de API:** Suporte a 4 versões de API (V1-V4) com tratamento de exceções específico por versão
- **Documentação OpenAPI:** Swagger configurado com autenticação Bearer JWT
- **Locale:** Sistema configurado para pt_BR

---