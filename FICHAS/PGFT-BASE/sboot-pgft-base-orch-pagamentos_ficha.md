---
## Ficha Técnica do Sistema

### 1. Descrição Geral
O **sboot-pgft-base-orch-pagamentos** é um orquestrador de pagamentos baseado em Apache Camel e RabbitMQ, responsável por processar movimentações financeiras (débito, crédito, TEF, estorno e cancelamento) com validações de circuit breaker e análise de fraude. O sistema integra-se com múltiplas APIs externas para efetivação de lançamentos em conta corrente, validação de fraudes, controle de processamento e integração de pagamentos. Utiliza arquitetura orientada a eventos (event-driven) com consumo e publicação de mensagens via RabbitMQ, aplicando padrões de retry, circuit breaker e validações de negócio antes da efetivação das transações.

---

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **MovimentoController** | Controlador REST que expõe endpoints para efetivação de movimentos, TEF, estorno e cancelamento de lançamentos |
| **MovimentoService** | Serviço orquestrador que delega processamento de movimentos para routers Camel apropriados |
| **IncluirLancamentoRouter** | Router Camel que processa inclusão de lançamentos da fila RabbitMQ, validando circuit break e fraude antes de efetivar débito/crédito |
| **TefRouter** | Router Camel especializado em processar transferências eletrônicas (TEF) com validações de segurança |
| **EstornoRouter** | Router Camel que processa estornos de documentos, buscando histórico e efetivando reversão |
| **AnaliseFraudeRouter** | Router Camel que realiza análise de fraude transacional quando aplicável |
| **CircuitBreakRouter** | Router Camel que valida mecanismo de circuit breaker para controle de fluxo de pagamentos |
| **ContaCorrenteRepositoryImpl** | Implementação de integração REST com APIs de conta corrente (débito, crédito, TEF, histórico, estorno, cancelamento) |
| **IntegrarPagamentoRepositoryImpl** | Implementação de integração REST com API de integração de pagamentos (protocolo, circuit break, validações) |
| **ProcessamentoRepositoryImpl** | Implementação de integração com Atom de processamento para atualização de status e lançamentos |
| **AnaliseFraudeRepositoryImpl** | Implementação de integração REST com API de análise de fraude transacional |
| **RabbitConsumerService** | Serviço que consome mensagens das filas RabbitMQ e delega para routers Camel |
| **EfetivaTefRabbitListener** | Listener RabbitMQ para fila de efetivação de TEF |
| **IncluirLancamentoRabbitListener** | Listener RabbitMQ para fila de inclusão de lançamentos |
| **EstornoDocRabbitListener** | Listener RabbitMQ para fila de estorno de documentos |
| **ResourceExceptionHandler** | Handler global de exceções que mapeia erros para códigos de falha padronizados |
| **AnaliseFraudeMapper** | Mapper que converte domínios de movimento para representações de análise de fraude |
| **MovimentoMapper** | Mapper que converte representations REST para domínios de movimento |
| **PagamentoMapper** | Mapper que converte representações legadas de débito/crédito/histórico |

---

### 3. Tecnologias Utilizadas

- **Spring Boot 2.3.1.RELEASE** - Framework base da aplicação
- **Apache Camel 3.2.0** - Framework de integração e roteamento de mensagens
- **RabbitMQ** - Message broker para processamento assíncrono
- **Spring Cloud OAuth2** - Autenticação e autorização via JWT
- **MapStruct** - Mapeamento de objetos
- **Gson** - Serialização/deserialização JSON
- **Lombok** - Redução de boilerplate code
- **Springfox Swagger** - Documentação de APIs
- **RestTemplate** - Cliente HTTP para integrações REST
- **Prometheus** - Métricas e monitoramento
- **Logback** - Logging estruturado em JSON
- **JUnit 5 + Mockito** - Testes unitários
- **RestAssured** - Testes funcionais
- **Pact** - Testes de contrato
- **OpenShift (OCP)** - Plataforma de deployment

---

### 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/movimento` | MovimentoController | Efetiva movimento financeiro (débito ou crédito) |
| POST | `/v1/movimento/tef` | MovimentoController | Efetiva transferência eletrônica (TEF) |
| POST | `/v1/movimento/estorno` | MovimentoController | Estorna documento financeiro |
| POST | `/v1/movimento/cancelamento` | MovimentoController | Cancela lançamento financeiro |
| POST | `/analise-fraude` | AnaliseFraudeController | Endpoint de teste para análise de fraude (profiles: local, des, uat) |

---

### 5. Principais Regras de Negócio

1. **Validação de Circuit Breaker**: Antes de efetivar pagamentos, valida se há circuit break ativo via mecanismo de trava, rejeitando transações quando necessário (status W, flag N).

2. **Análise de Fraude Transacional**: Movimentos com códigos de liquidação [1, 31, 32, 22] e tipo lançamento "S" (saída) passam por análise de fraude. Se reprovado (status NOK), movimento é rejeitado com status W e valor-status 6.

3. **Retry com Backoff Exponencial**: Efetivação de TEF possui retry manual (3 tentativas) para erro BDCC_TETO_GASTO_EXCEDIDO. Análise de fraude possui @Retryable (3 tentativas, backoff 200ms).

4. **Devolução por Circuit Break**: TEDs out (cdLiquidacao 31/32) com loginUsuario=RoboPGFTDev_CB são marcadas como devolução por circuit break.

5. **Tratamento de Crédito Indisponível**: Códigos de liquidação [10, 11, 21, 23] definem quantidade de dias de crédito indisponível (qtDiasCreditoIndisponivel).

6. **Validação de Código de Operação**: Movimentos com cdOperacao diferente de NENHUM, TRANSACAO_BANCO ou TRANSFERENCIA seguem fluxo de inclusão via router específico.

7. **Formatação de NSU**: NSU para análise de fraude é formatado como: codigoOrigem + CNPJ_BV + codigoLancamento.

8. **Validação de Documento Boleto**: Para liquidação 22 e valor < 250k, documento do boleto é zerado na análise de fraude.

9. **Atualização de Status Processamento**: Conforme resultado da efetivação (S=sucesso, N=falha, E=erro), atualiza status no Atom de processamento.

10. **Recover de Análise de Fraude**: Em caso de falha na análise de fraude após retries, sistema aprova automaticamente (status "OK") para não bloquear fluxo.

---

### 6. Relação entre Entidades

**Entidades Principais:**

- **Movimento**: Entidade central representando uma movimentação financeira (débito/crédito)
  - Relaciona-se com **Protocolo** (1:1) - identificação do pagamento
  - Contém **Estorno** (0:N) - histórico de estornos
  - Possui **Cancelamento** (0:1) - dados de cancelamento

- **MovimentoTefDTO**: Especialização de movimento para transferências eletrônicas
  - Herda características de Movimento
  - Adiciona dados específicos de TEF

- **Protocolo**: Identificador único do pagamento
  - Relaciona-se com **DadosMovimento** (1:1)
  - Contém **RetornoValidacao** (1:1) - resultado de validações

- **AnaliseTransacionalFraude**: Representação para análise de fraude
  - Contém **Remetente** (1:1)
  - Contém **Favorecido** (1:1)
  - Possui **AnaliseTransacionalFraudeResponse** (1:1) - resultado da análise

- **AtualizarProcessamentoDomain**: Entidade de atualização de status
  - Relaciona-se com **StatusProcessamentoEnum**
  - Relaciona-se com **FlContaCorrenteProcessadoEnum**

**Enumerações:**
- BancoEnum, MovimentoTransacaoEnum, TipoContaEnum, TipoLancamentoEnum, TipoPessoaEnum, StatusProcessamentoEnum, FlContaCorrenteProcessadoEnum

---

### 7. Estruturas de Banco de Dados Lidas

não se aplica

*Observação: O sistema não acessa diretamente banco de dados. Todas as operações de leitura são realizadas via APIs REST externas (Conta Corrente, Processamento, Integrar Pagamento).*

---

### 8. Estruturas de Banco de Dados Atualizadas

não se aplica

*Observação: O sistema não atualiza diretamente banco de dados. Todas as operações de escrita são realizadas via APIs REST externas (Conta Corrente, Processamento) ou mensageria (RabbitMQ).*

---

### 9. Arquivos Lidos e Gravados

não se aplica

*Observação: O sistema não manipula arquivos diretamente. Toda comunicação é via APIs REST e mensageria RabbitMQ. Logs são gravados em stdout no formato JSON.*

---

### 10. Filas Lidas

| Nome da Fila | Tecnologia | Classe Responsável | Descrição |
|--------------|------------|-------------------|-----------|
| `events.business.PGFT-BASE.incluiLancamento` | RabbitMQ | IncluirLancamentoRabbitListener | Fila de inclusão de lançamentos financeiros |
| `events.business.PGFT-BASE.efetivaTransferencia` | RabbitMQ | EfetivaTefRabbitListener | Fila de efetivação de transferências eletrônicas (TEF) |
| `events.business.PGFT-BASE.estornaDocumento` | RabbitMQ | EstornoDocRabbitListener | Fila de estorno de documentos financeiros |

**Configuração RabbitMQ:**
- Virtual Host: configurável por ambiente
- Concurrent Consumers: configurável
- Prefetch Count: configurável
- Retry: ExponentialBackOff com maxAttempts configurável
- Network Recovery Interval: configurável

---

### 11. Filas Geradas

| Nome da Fila/Exchange | Tecnologia | Classe Responsável | Descrição |
|----------------------|------------|-------------------|-----------|
| Exchange: `events.business.envioMensagemPGFT` | RabbitMQ | MensagemEstornoRepositoryImpl | Exchange para envio de mensagens de retorno |
| Routing Key: `PGFT.retornoEstornaDocumento.v1` | RabbitMQ | MensagemEstornoRepositoryImpl | Routing key para mensagens de retorno de estorno |

**Observação:** O sistema publica mensagens de retorno de estorno no exchange `events.business.envioMensagemPGFT` com routing key `PGFT.retornoEstornaDocumento.v1`.

---

### 12. Integrações Externas

| Sistema/API | Tipo | Classe Responsável | Descrição |
|-------------|------|-------------------|-----------|
| **ccbd-base-atom-conta-corrente** | REST | ContaCorrenteRepositoryImpl | API de conta corrente para débito, crédito, TEF, histórico, estorno e cancelamento |
| **sboot-pgft-base-atom-processamento** | REST | ProcessamentoRepositoryImpl | API de processamento para atualização de status e lançamentos |
| **sboot-sitp-base-atom-integrar-pagamento** | REST | IntegrarPagamentoRepositoryImpl | API de integração de pagamentos para busca de protocolo, validação de circuit break e configurações |
| **sboot-spag-base-orch-validacao-fraudes** | REST | AnaliseFraudeRepositoryImpl | API de análise de fraude transacional |
| **sboot-ccbd-base-atom-conta-corrente-stdin** | REST | ContaCorrenteRepositoryImpl | API de validação StandIn para transações pendentes |
| **API Gateway OAuth2** | REST | GatewayOAuthService | Serviço de autenticação para obtenção de tokens JWT |
| **RabbitMQ** | Message Broker | RabbitMQConfiguration | Broker de mensagens para processamento assíncrono |

**Endpoints Externos Configuráveis:**
- posicaoFintech, debito, credito, tef, historico, estorno, stdin, cancelamento, atualizarStatus, integrarPagamento, contaFintech, analiseFraude

---

### 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada com separação clara de responsabilidades (application, domain, common)
- Uso adequado de padrões de projeto (Repository, Mapper, Router, Processor)
- Implementação de retry e circuit breaker para resiliência
- Tratamento centralizado de exceções via @ControllerAdvice
- Uso de MapStruct e Lombok para redução de boilerplate
- Cobertura de testes abrangente (unitários, integração, funcionais, contrato)
- Configuração externalizada por ambiente (profiles)
- Logging estruturado em JSON
- Documentação OpenAPI/Swagger
- Uso de @Retryable e @Recover para tratamento de falhas

**Pontos de Melhoria:**
- Alguns processadores Camel poderiam ter lógica mais simplificada
- Retry manual em ContaCorrenteRepositoryImpl.efetivarTef poderia usar @Retryable
- Recover de AnaliseFraudeRepositoryImpl aprova automaticamente em falha (pode ser arriscado)
- Algumas classes com múltiplas responsabilidades (ex: ContaCorrenteRepositoryImpl)
- Falta de documentação inline em alguns métodos complexos
- Configurações hardcoded em alguns pontos (ex: CNPJ_BV, valores de timeout)

---

### 14. Observações Relevantes

1. **Arquitetura Event-Driven**: Sistema fortemente baseado em processamento assíncrono via RabbitMQ com Apache Camel como motor de integração.

2. **Resiliência**: Implementa múltiplas camadas de resiliência (retry, circuit breaker, recover) para garantir disponibilidade.

3. **Segurança**: Autenticação via OAuth2 JWT com API Gateway, tokens renovados automaticamente.

4. **Ambientes**: Suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas.

5. **Monitoramento**: Integração com Prometheus para métricas e observabilidade.

6. **Deployment**: Preparado para OpenShift (OCP) com ConfigMaps, Secrets, Probes e Resources definidos.

7. **Padrão de Nomenclatura**: Segue convenção de nomenclatura Votorantim (prefixos: sboot, ccbd, pgft, sitp, spag).

8. **Versionamento de API**: Endpoints versionados (v1) e routing keys com versionamento (v1).

9. **Testes de Contrato**: Implementa Pact para garantir compatibilidade entre consumidores e provedores.

10. **Formatação de Dados**: Utilitários específicos para formatação de datas, agências e NSU conforme padrões do negócio.

11. **Validações de Negócio**: Múltiplas validações antes da efetivação (circuit break, fraude, saldo, tipo operação).

12. **Auditoria**: Logs estruturados com nível AUDIT para rastreabilidade de operações críticas.

---