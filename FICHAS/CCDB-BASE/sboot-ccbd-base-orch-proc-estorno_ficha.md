---
## Ficha Técnica do Sistema

### 1. Descrição Geral
Sistema orquestrador de processamento de estornos e débitos em cartões de crédito/débito. Consome mensagens de filas (GCP PubSub e RabbitMQ) para processar autorizações de débito do motor de conciliação e estornos de arquivo Base2. Realiza validações de Advice (VISA/MASTER), consultas TIF para Motivo 22, rebloqueios para Motivo 34, efetivação de transferências e notificações de relatórios. Integra-se com múltiplas APIs externas para operações de cartões, contas correntes, movimentações, transferências e débitos. Utiliza Apache Camel para orquestração de rotas e Spring Boot como framework base.

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal Spring Boot que inicializa a aplicação |
| **ApplicationConfiguration** | Configuração de beans Spring/Camel, RestTemplate OAuth2, CamelContext e routers |
| **EstornoListener** | Listener RabbitMQ que consome mensagens da fila de estorno Base2 |
| **QuotesConsumer** | Consumer PubSub que recebe tentativas de débito do motor de conciliação |
| **EstornoRouter** | Rota Camel para processamento de estornos (consulta, transferência, atualização status) |
| **DebitoAdviceConfirmacaoRouter** | Rota Camel para confirmação de débito (validação Advice, desbloqueio/efetivação) |
| **EstornoRelatorioRouter** | Rota Camel para notificação de relatórios via RabbitMQ |
| **EstornoServiceImpl** | Serviço que executa rota de estorno e trata retentativas/DLQ |
| **DebitoAdviceServiceImpl** | Serviço que executa rota de confirmação de débito |
| **AdviceRepositoryImpl** | Integração com API de Advice (validar, processar, atualizar sequencial) |
| **TransferenciaRepositoryImpl** | Integração com API de transferências SPAG |
| **EstornoRepositoryImpl** | Integração com API de estorno (consultar, atualizar status, consultar TIF) |
| **GlobalRepositoryImpl** | Integração com API Global para consulta de contas por CPF/CNPJ |
| **ContaCorrenteRepositoryImpl** | Integração com API de cancelamento de bloqueio |
| **MovimentacoesRepositoryImpl** | Integração com API de consulta de bloqueios ativos |
| **SolicitarDebitorRepositoryImpl** | Integração com API de solicitação de débito/rebloqueio |
| **ContaCorrenteStdinRepositoryImpl** | Integração com API de consulta de bloqueios Stand-In |
| **CartoesRepositoryImpl** | Integração com API de listagem de cartões por conta/produto |
| **NotificarRelatorioRepositoryImpl** | Publicação de relatórios de estorno em fila RabbitMQ |
| **AutorizacaoDebitoMapper** | Mapeamento de DTO para domain de autorização de débito (define produto/transação VISA/MASTER) |
| **MapperTemplate** | Interface MapStruct para conversões entre representações e domínios |
| **CamelContextWrapper** | Wrapper para inicialização e gerenciamento do contexto Camel |

### 3. Tecnologias Utilizadas

- **Framework:** Spring Boot 2.x
- **Orquestração:** Apache Camel 3.0.1
- **Mensageria:** RabbitMQ (AMQP), Google Cloud Pub/Sub
- **Autenticação:** OAuth2 Client Credentials (custom com renovação antecipada de token - 60s antes de expirar)
- **Mapeamento:** MapStruct
- **Serialização:** Jackson, Gson
- **Documentação API:** Swagger/OpenAPI 3
- **Monitoramento:** Spring Actuator, Prometheus
- **Segurança:** Spring Security JWT
- **Geração de Clients:** Swagger Codegen (8 APIs externas)
- **Testes:** JUnit 5, Mockito
- **Containerização:** Docker
- **Orquestração Infra:** Kubernetes (GKE)
- **Linguagem:** Java 11
- **Build:** Maven
- **Logging:** Logback (JSON assíncrono)

### 4. Principais Endpoints REST

Não se aplica. O sistema não expõe endpoints REST próprios; atua como consumidor de filas e cliente de APIs externas.

### 5. Principais Regras de Negócio

1. **Validação de Produto/Transação:** Define código de produto (1=VISA, 2=MASTER) e código de transação (0100 VISA, 0200 MASTER) baseado no tipo de cartão
2. **Processamento de Advice:** Trata tipos APROVADO, ESTORNO e DESFAZIMENTO; identifica débito retroativo (código 002000) e saque (código 012000)
3. **Motivo de Bloqueio 22:** Consulta TIF para validação; se possui E4 ou estorno/desfazimento (tipo>200 + status 00), desbloqueia; caso contrário, efetiva débito
4. **Motivo de Bloqueio 34:** Verifica bloqueios em aberto (normal + stand-in); compara sequencial de bloqueio e valor; realiza rebloqueio em caso de erro SPAG
5. **Validação de Sequencial de Bloqueio:** sqBloqueio deve ser >= 1 para cancelamento
6. **Renovação de Token OAuth2:** Token renovado antecipadamente 60 segundos antes da expiração
7. **Retentativas:** Máximo de 3 tentativas com delay de 500ms; validação de Dead Letter Queue (máximo 2 mortes)
8. **Transferências:** Utiliza códigos ITP específicos para estorno nacional/internacional e débito retroativo; histórico limitado a 40 caracteres
9. **Crédito em Conta:** Códigos OCT (26) e DEVOLUÇÃO (20) definem se é operação de crédito
10. **Lançamento Incondicional:** Flag flLancamentoIncondicionalSaldo=S para rebloqueio motivo 34
11. **Notificação de Relatório:** Publica em fila RabbitMQ quando estorno atinge Dead Letter Queue (após validação de retentativas)
12. **Indicador Wallet:** Transações de cartão com indicadorTransacaoWallet=false

### 6. Relação entre Entidades

**Entidades Principais:**

- **Estorno:** Representa solicitação de estorno de arquivo Base2
  - Relaciona-se com **Cartao** (1:1)
  - Contém lista de **Conta** (1:N)
  
- **AutorizacaoDebito:** Representa tentativa de débito do motor de conciliação
  - Possui **TipoMotivoBloqueio** (22, 30 ou 34)
  - Relaciona-se com **Conta** (1:1)
  
- **ProcessarAdvice:** Representa processamento de Advice
  - Possui **TipoAdvice** (APROVADO, ESTORNO, DESFAZIMENTO)
  - Contém **DebtAdvice** (1:1)
  - Relaciona-se com **Cartao** (1:1)
  
- **TransferenciaRequest:** Representa solicitação de transferência
  - Contém **ParticipanteRemetente** e **ParticipanteFavorecido** (1:2)
  - Possui **ITP** (código de liquidação, evento, transação, processamento)
  
- **ContaCorrente:** Representa dados de conta corrente
  - Relaciona-se com **SaldoContaCorrente** (1:1)
  - Contém lista de **Bloqueio** (1:N)
  
- **TifDebito:** Representa consulta TIF para validação Motivo 22
  - Contém lista de transações ordenadas por tipo

**Enumerações de Domínio:**
- **TipoMotivoBloqueio:** 22, 30, 34
- **TipoAdvice:** APROVADO, ESTORNO, DESFAZIMENTO
- **TipoMoeda:** Real (986), outras moedas
- **ContaBanco:** BV (161/655), BVSA (436/413)
- **TipoConta:** Corrente, Poupança
- **TipoPessoa:** Física (F), Jurídica (J)

### 7. Estruturas de Banco de Dados Lidas

Não se aplica. O sistema não acessa banco de dados diretamente; todas as consultas são realizadas via APIs externas (atom/orch).

### 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema não acessa banco de dados diretamente; todas as atualizações são realizadas via APIs externas (atom/orch).

### 9. Arquivos Lidos e Gravados

Não se aplica. O sistema não manipula arquivos diretamente; processa mensagens de filas e integra-se com APIs.

### 10. Filas Lidas

| Nome da Fila | Tipo | Tecnologia | Descrição |
|--------------|------|------------|-----------|
| **quotesInputChannel** | Subscription | GCP Pub/Sub | Recebe tentativas de débito do motor de conciliação (AutorizacaoDebitoDTO). Subscription: motor-conciliacao-debito. AckMode: MANUAL. MaxFetch: 100 |
| **events.business.CCBD-BASE.estornoArquivoBase2** | Queue | RabbitMQ | Recebe solicitações de estorno de arquivo Base2. Possui Dead Letter Exchange configurada. Prefetch: 250 |

### 11. Filas Geradas

| Nome da Fila/Tópico | Tipo | Tecnologia | Descrição |
|---------------------|------|------------|-----------|
| **quotesOutputChannel** | Topic | GCP Pub/Sub | Publica mensagens para o motor de conciliação (topic: motor-conciliacao) |
| **events.ex.business.ccbd.estornoArquivoBase2Relatorio** | Exchange/Queue | RabbitMQ | Publica relatórios de estorno que atingiram DLQ. RoutingKey: CCBD.estornoArquivoBase2Relatorio. Queue: estornoArquivoBase2Relatorio |
| **events.ex.business.ccbd.estornoArquivoBase2.reenvio** | Exchange/Queue | RabbitMQ | Fila de reenvio com TTL de 30 segundos para retentativas de estorno |

### 12. Integrações Externas

| Sistema/API | Descrição | Operações |
|-------------|-----------|-----------|
| **sboot-ccbd-base-atom-advice** | API de Advice para validação e processamento de transações | validar(), processar() (tipos APROVADO/ESTORNO/DESFAZIMENTO), processarEfetivacaoDebitoInvalida() Motivo22, atualizarSequencialBloqueio() Motivo34 |
| **sboot-ccbd-base-atom-cartoes** | API de Cartões | listarCartoesPorContaProduto() - retorna CPF/CNPJ do cartão |
| **sboot-spag-base-orch-transferencias** | API de Transferências SPAG | transferencia() - efetua transferências e retorna protocolo |
| **sboot-ccbd-base-orch-proc-estorno** | API de Estorno | consultar() estorno por contas/produto/correlativo/moeda/autorizador; atualizarStatusEstorno() flagBase2Estornado; consultarDebitoTif() validação Motivo22 TIF |
| **sboot-ccbd-base-orch-solic-debito** | API de Solicitação de Débito | solicitarDebito() - rebloqueio de saldo, retorna sqUltimoBloqueioSaldo |
| **sboot-ccbd-base-atom-movimentacoes** | API de Movimentações | listarBloqueios() - consulta bloqueios ativos da conta (motivoBloqueio 34 típico) |
| **sboot-ccbd-base-atom-conta-corrente** | API de Conta Corrente | cancelarBloqueio() - valida sqBloqueio>=1 e cancela bloqueio |
| **sboot-ccbd-base-atom-conta-corrente-stdin** | API de Conta Corrente Stand-In | listarBloqueiosStandin() - lista bloqueios Stand-In se flag chamarBloqueiosStandin=true |
| **sboot-glob-base-atom-global** | API Global | getContasByCpfCnpj(), getContasByNuConta(), buscarDadosRemetente() - consulta contas e dados de clientes |
| **OAuth2 Token Service** | Serviço de autenticação | Obtenção e renovação de tokens OAuth2 Client Credentials |

**Observação:** Todas as integrações utilizam autenticação OAuth2 via Gateway com renovação antecipada de token (60 segundos antes da expiração).

### 13. Avaliação da Qualidade do Código

**Nota:** 8/10

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada com separação clara de responsabilidades (domain, application, common)
- Uso adequado de padrões de projeto (Repository, Mapper, Service)
- Implementação robusta de tratamento de erros com exceções customizadas
- Boa cobertura de testes unitários com Mockito e JUnit 5
- Uso de MapStruct para mapeamentos, reduzindo código boilerplate
- Configuração externalizada e suporte a múltiplos profiles (local, des, qa, uat, prd)
- Implementação de retry e Dead Letter Queue para resiliência
- Logging estruturado em JSON com níveis apropriados
- Uso de Lombok para redução de código repetitivo
- Documentação via Swagger/OpenAPI
- Renovação antecipada de token OAuth2 demonstra preocupação com disponibilidade

**Pontos de Melhoria:**
- Falta de documentação inline (JavaDoc) em algumas classes críticas
- Alguns processors Camel poderiam ter nomes mais descritivos
- Ausência de testes de integração (apenas unitários mencionados)
- Configurações hardcoded em alguns enums (ex: códigos ITP)
- Falta de circuit breaker explícito para chamadas externas (apenas retry básico)
- Alguns métodos com múltiplas responsabilidades (ex: DefinirFormaDesbloqueio22Processor)

O código demonstra maturidade técnica e boas práticas de desenvolvimento, com arquitetura limpa e preocupação com resiliência e manutenibilidade.

### 14. Observações Relevantes

1. **Arquitetura Multi-Módulo:** Projeto organizado em 3 módulos Maven (common, domain, application) facilitando reuso e manutenção

2. **Geração Automática de Clients:** Utiliza swagger-codegen para gerar clients de 8 APIs externas, garantindo consistência com contratos

3. **Infraestrutura como Código:** Configuração Kubernetes completa (infra.yml) com ConfigMaps, Secrets, probes de saúde e service accounts

4. **Profiles Ambientais:** Suporte completo para ambientes local, des, qa, uat e prd com configurações específicas

5. **Monitoramento:** Actuator exposto na porta 9090 separada da aplicação (8080) com métricas Prometheus

6. **Segurança:** Integração com LDAP e uso de cacerts customizado via volumes Kubernetes

7. **Recursos Kubernetes:** Limites de memória configurados (1Gi request / 2Gi limit)

8. **Dead Letter Queue:** Implementação sofisticada com validação de x-death header e limite de 2 mortes antes de notificar relatório

9. **Idempotência:** Geração de identificador único para transferências (max 30 caracteres) usando formato identificador+tipo+sqBloqueio

10. **Tratamento de Moeda:** Lógica específica para diferenciar operações nacionais (Real - 986) e internacionais

11. **Histórico de Transferência:** Limitação de 40 caracteres para histórico, requerendo truncamento cuidadoso

12. **Processamento Assíncrono:** Uso de async appender no Logback para não bloquear threads de processamento

13. **Validação de Wallet:** Sistema identifica e marca transações de carteira digital (indicadorTransacaoWallet)

14. **Códigos Contábeis:** Uso extensivo de enums para ITP (Instrução de Transferência de Pagamento) garantindo consistência contábil

15. **Auditoria:** Configuração de log AUDIT separado para rastreabilidade de operações críticas