---
## Ficha Técnica do Sistema

### 1. Descrição Geral

Sistema de orquestração de débitos advice de cartões de crédito/débito, responsável por processar confirmações, estornos e desfazimentos de transações. O sistema escuta mensagens de filas JMS (IBM MQ) e Google Cloud PubSub, valida as transações com o autorizador, executa transferências bancárias (TED/TEF), gerencia bloqueios e desbloqueios de saldo (código 34), controla limites transacionais e publica eventos de replicação para Salesforce e outros sistemas. Implementa arquitetura hexagonal com Apache Camel para orquestração de fluxos complexos, incluindo tratamento de IOF, confirmações parciais e validações específicas de produtos (voucher BNK, compra+saque Mastercard, AFT).

---

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **DebitoAdviceListener** | Escuta filas JMS (CCBD) e PubSub, valida e processa mensagens de advice, gerencia ACK/NACK e retentativas |
| **DebitoAdviceRouter** | Rota principal Camel para orquestração do fluxo de débito advice (aprovação/estorno/desfazimento) |
| **DebitoAdviceConfirmacaoRouter** | Rota Camel específica para confirmação de débito e desbloqueio de saldo |
| **NotificarPubSubRouter** | Rotas de notificação para tópicos PubSub (normal, DLQ, replicação) |
| **DebitoAdviceServiceImpl** | Serviço de domínio que inicia rotas Camel e trata exceções de execução |
| **TransferenciaProcessor** | Processa transferências bancárias definindo remetente/favorecido conforme tipo de advice |
| **AdviceRepositoryImpl** | Integra API de advice para validação, processamento, log e consulta de autorizações |
| **TransferenciaRepositoryImpl** | Executa transferências TED/TEF via API SPAG |
| **ContaCorrenteRepositoryImpl** | Cancela bloqueios de saldo via API |
| **GlobalRepositoryImpl** | Busca dados cadastrais de clientes e contas |
| **SolicitarDebitorRepositoryImpl** | Solicita débito e rebloqueio de saldo (código 34) |
| **LimitesTransacionaisRepositoryImpl** | Finaliza consumo de limite transacional |
| **NotificarPubSubRepositoryImpl** | Publica mensagens em tópicos PubSub (advice, DLQ, replicação, Salesforce) |
| **CriarEventosReplicacao** | Utilitário para criação de eventos de replicação consolidados |
| **ApplicationConfiguration** | Configuração Spring Boot para clientes OAuth2 das APIs REST |
| **JmsListenerConfiguration / JmsSendConfiguration** | Configuração de listeners e envio para filas IBM MQ |
| **PubSubListenerConfiguration** | Configuração de subscriptions e tópicos Google Cloud PubSub |

---

### 3. Tecnologias Utilizadas

- **Framework Principal**: Spring Boot
- **Orquestração**: Apache Camel
- **Mensageria**: IBM MQ (JMS), Google Cloud PubSub
- **Autenticação**: OAuth2 (client_credentials, JWT)
- **Serialização**: Jackson (JSON)
- **Utilitários**: Lombok
- **Banco de Dados**: Oracle (via APIs REST, não acesso direto)
- **APIs REST**: Feign Clients customizados
- **Encoding**: ISO-8859-1 para mensagens JMS
- **Cloud**: Google Cloud Platform (PubSub)

---

### 4. Principais Endpoints REST

O sistema **não expõe** endpoints REST próprios. Atua como **consumidor** de APIs externas:

| Método | Endpoint (Externo) | Cliente/Classe | Descrição |
|--------|-------------------|----------------|-----------|
| POST | `/advice/validar` | AdviceApi | Valida advice com autorizador |
| POST | `/advice/processar` | AdviceApi | Processa advice final |
| POST | `/advice/log` | AdviceApi | Registra log de erros |
| GET | `/advice/autorizacoes` | AdviceApi | Consulta autorizações sem advice |
| PUT | `/advice/sequencial-bloqueio` | AdviceApi | Atualiza sequencial de bloqueio |
| PUT | `/advice/checklist` | CheckListApi | Marca checklist de advice processado |
| POST | `/transferencia` | TransferenciaApi | Executa transferência TED/TEF |
| DELETE | `/conta-corrente/bloqueio` | CancelarBloqueioApi | Cancela bloqueio de saldo |
| POST | `/solicitar-debito` | SolicitarDebitoApi | Solicita débito/rebloqueio |
| GET | `/movimentacoes/bloqueios` | ConsultarBloqueiosApi | Lista bloqueios da conta |
| PUT | `/limites/finalizar` | LimiteDasTransaesApi | Finaliza limite transacional |
| GET | `/global/conta` | GetContasByNuContaApi | Busca dados cadastrais |

---

### 5. Principais Regras de Negócio

1. **Validação de Advice**: Valida transações recusadas, voucher BNK base1/base2, compra com saque Mastercard, AFT negado e confirmação parcial
2. **Bloqueio/Desbloqueio Código 34**: Gerencia bloqueio preventivo de saldo (código 34) antes da transferência e desbloqueio após confirmação
3. **Transferências Bancárias**: Define remetente e favorecido conforme tipo de advice (APROVADO: banco→cliente, ESTORNO: cliente→banco)
4. **IOF**: Calcula e cobra IOF quando aplicável em transferências
5. **Confirmação Parcial**: Aplica diferença de valor em confirmações parciais (valor original vs valor confirmado)
6. **Limites Transacionais**: Controla consumo e finalização de limites por transação
7. **Rebloqueio em Erro**: Em caso de erro no SPAG, rebloqueia saldo código 34 para garantir consistência
8. **Idempotência**: Gera chave de idempotência para débito (limitada a 30 caracteres)
9. **Retentativas e DLQ**: Implementa política de retentativas com envio para Dead Letter Queue em falhas persistentes
10. **Replicação de Eventos**: Consolida eventos de tentativas e publica para sistemas downstream (Salesforce, replicação)
11. **Conversão de Bancos**: Converte código de banco conforme necessário (436→413, 161)
12. **Validação de Produtos**: Bloqueia processamento de produtos específicos (compra+saque, voucher BNK em bases específicas)

---

### 6. Relação entre Entidades

**Entidades Principais:**

- **DebitoAdvice**: Entidade raiz contendo dados da transação (identificador, código transação/processamento, valores, moedas, datas)
  - Relaciona-se com **Cartao** (1:1): dados do cartão emissor
  - Relaciona-se com **Estabelecimento** (1:1): dados do estabelecimento comercial
  - Relaciona-se com **TrilhaDadosCartao** (1:1): dados da trilha do cartão
  - Relaciona-se com **TransacaoAdvice** (1:1): dados de liquidação e evento

- **ValidarAdviceRequest/Response**: Request/response de validação
  - Response contém **TipoAdviceEnum**, sequenciais de bloqueio/limite, dados de transação

- **Transferencia**: Entidade de transferência bancária
  - Relaciona-se com **Participante** (1:2): remetente e favorecido
  - Relaciona-se com **Protocolo** (1:1): protocolo de resposta

- **ContaCorrenteResponse**: Dados cadastrais da conta
  - Mapeado para **Participante** em transferências

- **AutorizacaoDebito**: Autorizações de débito sem advice
  - Lista em **AutorizacoesDebito**

- **Eventos de Replicação**:
  - **TransacaoConsolidadaDeb**: Consolida **ReplicacaoAdvice** (confirmação ou estorno) + **TentativaAdvice** (lista de eventos)
  - **EventosAdvice**: Lista de eventos por tipo de classe monitorada

---

### 7. Estruturas de Banco de Dados Lidas

não se aplica

**Observação**: O sistema não acessa banco de dados diretamente. Todas as operações de leitura são realizadas via APIs REST que encapsulam o acesso aos dados.

---

### 8. Estruturas de Banco de Dados Atualizadas

não se aplica

**Observação**: O sistema não acessa banco de dados diretamente. Todas as operações de escrita são realizadas via APIs REST que encapsulam o acesso aos dados.

---

### 9. Arquivos Lidos e Gravados

não se aplica

**Observação**: O sistema não manipula arquivos diretamente. Trabalha exclusivamente com mensagens de filas (JMS/PubSub) e chamadas REST.

---

### 10. Filas Lidas

| Nome da Fila | Tecnologia | Classe Responsável | Descrição |
|--------------|------------|-------------------|-----------|
| **CCBD** (IBM MQ) | JMS | DebitoAdviceListener | Fila principal de entrada para mensagens de débito advice |
| **Subscription PubSub** (configurável) | Google Cloud PubSub | DebitoAdviceListener | Subscription de entrada para mensagens de advice via PubSub (proxy DXC) |

---

### 11. Filas Geradas

| Nome da Fila/Tópico | Tecnologia | Classe Responsável | Descrição |
|---------------------|------------|-------------------|-----------|
| **CPBD** (IBM MQ) | JMS | AdviceRepositoryImpl | Fila de saída para notificação de advice processado |
| **Tópico Advice** | Google Cloud PubSub | NotificarPubSubRepositoryImpl | Tópico para publicação de advice processado |
| **Tópico DLQ** | Google Cloud PubSub | NotificarPubSubRepositoryImpl | Dead Letter Queue para mensagens com falha persistente |
| **Tópico Replicação** | Google Cloud PubSub | NotificarPubSubRepositoryImpl | Tópico para eventos de replicação consolidados |
| **Tópico Salesforce** | Google Cloud PubSub | NotificarPubSubRepositoryImpl | Tópico para envio de dados ao Salesforce |

---

### 12. Integrações Externas

| Sistema/API | Tipo | Descrição | Classe Responsável |
|-------------|------|-----------|-------------------|
| **API Advice** | REST (OAuth2) | Validação, processamento, log e consulta de autorizações de advice | AdviceRepositoryImpl |
| **API SPAG (Transferência)** | REST (OAuth2) | Execução de transferências TED/TEF | TransferenciaRepositoryImpl |
| **API Global** | REST (OAuth2) | Consulta de dados cadastrais de clientes e contas | GlobalRepositoryImpl |
| **API Conta Corrente** | REST (OAuth2) | Cancelamento de bloqueios de saldo | ContaCorrenteRepositoryImpl |
| **API Solicitar Débito** | REST (OAuth2) | Solicitação de débito e rebloqueio de saldo (código 34) | SolicitarDebitorRepositoryImpl |
| **API Movimentações** | REST (OAuth2) | Consulta de bloqueios ativos na conta | MovimentacoesRepositoryImpl |
| **API Limites Transacionais** | REST (OAuth2) | Finalização de consumo de limite transacional | LimitesTransacionaisRepositoryImpl |
| **API Checklist** | REST (OAuth2) | Atualização de checklist de advice processado | AdviceRepositoryImpl |
| **IBM MQ (CCBD/CPBD)** | JMS | Filas de entrada e saída de mensagens | JmsListenerConfiguration, JmsSendConfiguration |
| **Google Cloud PubSub** | Mensageria Cloud | Tópicos de entrada/saída para replicação e notificações | PubSubListenerConfiguration, NotificarPubSubRepositoryImpl |

---

### 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- **Arquitetura bem definida**: Implementa arquitetura hexagonal com separação clara entre domínio, aplicação e infraestrutura (ports/adapters)
- **Uso adequado de padrões**: Apache Camel para orquestração complexa, Lombok para redução de boilerplate, mappers para conversão de dados
- **Tratamento robusto de erros**: Hierarquia de exceções customizadas, política de retentativas, DLQ para falhas persistentes
- **Configuração externalizada**: Uso de AppProperties e application.yml para diferentes ambientes
- **Segurança**: OAuth2 com renovação automática de token antes da expiração
- **Rastreabilidade**: Sistema de eventos de replicação consolidados com tentativas
- **Modularização**: Separação clara de responsabilidades entre processors, repositories e services

**Pontos de Melhoria:**
- **Complexidade das rotas Camel**: Rotas muito extensas (DebitoAdviceRouter) com múltiplas validações e bifurcações, dificultando manutenção
- **Acoplamento com Camel**: Lógica de negócio fortemente acoplada ao framework Camel (processors), dificultando testes unitários isolados
- **Falta de documentação inline**: Ausência de JavaDoc em classes e métodos críticos
- **Validações dispersas**: Regras de negócio espalhadas entre múltiplos processors, dificultando visão holística
- **Tratamento de exceções genérico**: Alguns pontos com catch genérico de Exception
- **Testes**: Não há evidências de testes automatizados no resumo fornecido

O código demonstra maturidade arquitetural e boas práticas de engenharia, mas a complexidade inerente ao domínio e ao uso intensivo do Camel impacta a manutenibilidade.

---

### 14. Observações Relevantes

1. **Proxy DXC→PubSub**: Sistema atua como ponte entre filas JMS legadas (IBM MQ) e arquitetura cloud (PubSub)

2. **Encoding ISO-8859-1**: Mensagens JMS utilizam encoding específico, requerendo converter customizado

3. **Renovação Proativa de Token**: Implementação customizada (PDECAccessTokenProviderChain) renova token OAuth2 60 segundos antes da expiração, evitando falhas por token expirado

4. **Idempotência Limitada**: Chave de idempotência de débito limitada a 30 caracteres, requerendo estratégia de geração específica

5. **Bloqueio Código 34**: Código específico para bloqueio preventivo de saldo durante processamento de advice

6. **Conversão de Bancos**: Lógica específica de conversão de códigos de banco (436→413, 161) em operações de desbloqueio

7. **Confirmação Parcial**: Tratamento especial para casos onde valor confirmado difere do valor original da transação

8. **Validações de Produto**: Regras específicas para bloquear processamento de produtos não suportados (compra+saque Mastercard, voucher BNK em bases específicas)

9. **Eventos Consolidados**: Sistema de replicação consolida múltiplas tentativas e eventos em estrutura única (TransacaoConsolidadaDeb)

10. **Múltiplos Ambientes**: Configuração para 5 ambientes (local, des, qa, uat, prd) com URLs e credenciais específicas

11. **Tratamento de Mensagens Inválidas**: Converter customizado (MappingMessageLocalConverter) evita quebra do listener em mensagens JMS malformadas

12. **Rebloqueio em Erro**: Estratégia de compensação que rebloqueia saldo (código 34) em caso de erro no SPAG, garantindo consistência

---