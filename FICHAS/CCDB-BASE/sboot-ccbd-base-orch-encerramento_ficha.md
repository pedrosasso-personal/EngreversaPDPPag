# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema orquestrador de encerramento de contas bancárias que gerencia diferentes modalidades de encerramento: por desinteresse comercial, ocorrências imediatas, solicitações via Salesforce e Cockpit. O sistema realiza validações de requisitos (saldo, bloqueios, investimentos BVIN), orquestra o processo de encerramento em múltiplos sistemas (Conta Corrente, Global, Produtos), gerencia bloqueios de movimentações e envia notificações por email. Utiliza Apache Camel para orquestração de fluxos e Google Cloud Pub/Sub para comunicação assíncrona.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **EncerramentoController** | Controller REST que expõe endpoints para consulta, validação e demanda de encerramentos |
| **EncerramentoContaService** | Service principal que orquestra processos de encerramento |
| **ConsultaEncerramentoService** | Service para consulta e detalhamento de encerramentos |
| **EnviarMensagemTopicoService** | Service para envio de mensagens aos tópicos Pub/Sub |
| **SolicitarEncerramentoListener** | Listener que consome mensagens de solicitação de encerramento do Pub/Sub |
| **ContaCorrenteRepositoryImpl** | Repository para operações de encerramento em Conta Corrente |
| **GlobalRepositoryImpl** | Repository para operações no sistema Global (dados cadastrais, contas) |
| **BloqueioRepositoryImpl** | Repository para inclusão e consulta de bloqueios de movimentação |
| **ConsultaPosicaoRepositoryImpl** | Repository para consulta de posições em investimentos BVIN |
| **EncerramentoDesinteresseImediatasRepositoryImpl** | Repository para encerramentos por desinteresse e imediatas |
| **EmailEncerramentoPubSubRepositoryImpl** | Repository para envio de emails via Pub/Sub |
| **CamelContextWrapper** | Wrapper do contexto Camel que inicializa as rotas de orquestração |
| **DemandaEncerramentoDesinteresseRouter** | Router Camel para orquestração de encerramento por desinteresse |
| **DemandaEncerramentoImediatasRouter** | Router Camel para orquestração de encerramento por ocorrências imediatas |
| **EncerramentoCockpitRouter** | Router Camel para encerramento via Cockpit |
| **EncerramentoContaSalesforceRouter** | Router Camel para encerramento via Salesforce |
| **ResourceExceptionHandler** | Handler global de exceções REST |

---

## 3. Tecnologias Utilizadas

- **Framework Principal:** Spring Boot 2.x
- **Linguagem:** Java 11
- **Orquestração:** Apache Camel 3.0.1
- **Mensageria:** Google Cloud Pub/Sub
- **Plataforma Cloud:** GCP (Google Kubernetes Engine)
- **Build:** Maven
- **Documentação API:** Swagger/OpenAPI
- **Serialização:** Jackson (com deserializer customizado para OffsetDateTime)
- **HTTP Client:** RestTemplate
- **Segurança:** OAuth2
- **Monitoramento:** Spring Actuator (porta 9090)
- **Testes:** ArchUnit (testes de arquitetura)
- **Utilitários:** Lombok

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/encerramento-conta/acompanhamento/banco/{banco}` | EncerramentoController | Consulta encerramentos por banco |
| GET | `/v1/banco-digital/encerramento/detalhamento/banco/{banco}/conta/{conta}/tipoConta/{tipoConta}` | EncerramentoController | Detalha encerramento específico |
| POST | `/v1/encerramento-conta/efetiva-encerramento` | EncerramentoController | Efetiva encerramento de conta |
| POST | `/v1/banco-digital/encerramento/confirmarDemanda` | EncerramentoController | Confirma demanda de encerramento |
| POST | `/v1/encerramento-conta/desinteresse/validar-requisitos` | EncerramentoController | Valida requisitos para encerramento por desinteresse |
| POST | `/v1/encerramento-conta/imediatas/validar-requisitos` | EncerramentoController | Valida requisitos para encerramento imediato |
| GET | `/v1/encerramento-conta/acompanhamento/desinteresseImediatas/banco/{banco}` | EncerramentoController | Consulta encerramentos desinteresse/imediatas |
| POST | `/v1/encerramento-conta/desinteresse/demandar` | EncerramentoController | Demanda encerramento por desinteresse |
| POST | `/v1/encerramento-conta/imediatas/demandar` | EncerramentoController | Demanda encerramento imediato |

---

## 5. Principais Regras de Negócio

1. **Validação de Saldo:** Conta deve estar zerada para encerramento
2. **Validação de Bloqueios:** Verifica existência de bloqueios que impedem encerramento
3. **Validação BVIN:** Verifica se conta possui posição em investimentos BVIN
4. **Validação de Situação:** Conta não pode estar previamente encerrada
5. **Validação de Titular:** CPF/CNPJ do solicitante deve corresponder ao titular da conta
6. **Filtro de Agência:** Filtra contas da agência 2020 em processamentos específicos
7. **Bloqueio Automático:** Insere bloqueio de CRÉDITO (motivo 12) em encerramentos por desinteresse
8. **Bloqueio Duplo:** Insere bloqueio de CRÉDITO e DÉBITO (motivo 12) em encerramentos imediatos
9. **Encerramento Global Condicional:** Encerra conta Global apenas quando aplicável
10. **Cancelamento de Produtos:** Envia mensagem para cancelamento de produtos vinculados
11. **Notificação por Email:** Envia email de confirmação em encerramentos por desinteresse
12. **Retry de Encerramento Global:** Tenta encerramento Global até 3 vezes com backoff exponencial (1s, multiplicador 2)
13. **Registro de Intenção BVIN:** Registra intenção de encerramento quando há posição BVIN

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **IntencaoEncerramento:** Representa solicitação de encerramento recebida via Pub/Sub
  - Atributos: cpfCnpj, banco, agencia, conta, tipoConta, motivo, ticket
  
- **EnvioEmailEncerramento:** Representa email de notificação de encerramento
  - Atributos: destinatario, assunto, corpo, anexos
  
- **MensagemFila:** Representa mensagem genérica para tópicos Pub/Sub
  - Atributos: conteudo, metadados

- **DemandaEncerramento:** Representa demanda de encerramento
  - Relacionamento: N demandas para 1 conta

- **Bloqueio:** Representa bloqueio de movimentação
  - Tipos: CREDITO, DEBITO
  - Motivo: código 12 para encerramentos

**Relacionamentos:**
- Conta → N Bloqueios
- Conta → 1 Posição BVIN (opcional)
- Conta → 1 Modalidade
- Pessoa → N Contas
- Encerramento → 1 Motivo

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| N/A | N/A | N/A | Sistema não acessa diretamente banco de dados. Todas as consultas são realizadas via APIs REST de sistemas externos (Conta Corrente, Global, BVIN, Movimentações, Pessoa). |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| N/A | N/A | N/A | Sistema não atualiza diretamente banco de dados. Todas as operações de escrita são realizadas via APIs REST de sistemas externos. |

---

## 9. Arquivos Lidos e Gravados

não se aplica

---

## 10. Filas Lidas

| Nome da Fila | Tecnologia | Classe Responsável | Descrição |
|--------------|-----------|-------------------|-----------|
| `solicitar-encerramento-conta-sub` | Google Cloud Pub/Sub | SolicitarEncerramentoListener | Recebe solicitações de encerramento (IntencaoEncerramento) para processamento assíncrono |

---

## 11. Filas Geradas

| Nome da Fila/Tópico | Tecnologia | Classe Responsável | Descrição |
|---------------------|-----------|-------------------|-----------|
| `envio-email-topic` | Google Cloud Pub/Sub | EmailEncerramentoPubSubRepositoryImpl | Envia mensagens para disparo de emails de encerramento |
| `encerramento-conta-topic` | Google Cloud Pub/Sub | EnviarMensagemTopicoPubSubRepositoryImpl | Envia mensagens de encerramento de conta |
| `topico-produtos` | Google Cloud Pub/Sub | ProdutosRouter | Envia mensagens para cancelamento de produtos vinculados |

---

## 12. Integrações Externas

| Sistema/API | Tipo | Descrição |
|-------------|------|-----------|
| **API Conta Corrente (CCBD)** | REST | Operações de encerramento, consulta status, situação e detalhamento de contas corrente |
| **API Global (GLOB)** | REST | Consulta dados cadastrais, endereços, contas e encerramento no sistema Global |
| **API Movimentações (INEO)** | REST | Inclusão e consulta de bloqueios de movimentação (crédito/débito) |
| **API Investimentos BVIN** | REST | Consulta posições em investimentos |
| **API Pessoa BD** | REST | Consulta dados cadastrais de pessoas |
| **API Mascaramento CPF** | REST | Geração de hash de CPF para mascaramento |
| **API Motivo Encerramento** | REST | Consulta motivos de encerramento |
| **API Consulta Contas** | REST | Consulta contas por número |
| **API Modalidade** | REST | Consulta modalidade de contas |
| **API Encerramento Desinteresse/Imediatas** | REST | Operações específicas de encerramento por desinteresse e ocorrências imediatas |
| **Google Cloud Pub/Sub** | Mensageria | Comunicação assíncrona para solicitações de encerramento, envio de emails e cancelamento de produtos |
| **OAuth2 Server** | Autenticação | Autenticação e autorização para APIs externas |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com uso de camadas (Controller, Service, Repository)
- Uso adequado de Apache Camel para orquestração de fluxos complexos
- Implementação de tratamento de exceções centralizado
- Configuração externalizada via properties
- Uso de mappers para conversão entre camadas
- Implementação de testes de arquitetura (ArchUnit)
- Documentação de API com Swagger/OpenAPI
- Uso de Lombok para redução de boilerplate

**Pontos de Melhoria:**
- Routers Camel muito extensos e com lógica complexa embutida (violação do princípio de responsabilidade única)
- Falta de documentação inline em pontos críticos do código
- Nomenclatura de endpoints REST inconsistente (mix de português e inglês)
- Alguns processors Camel poderiam ser refatorados em services reutilizáveis
- Ausência de logs estruturados em pontos importantes do fluxo
- Configurações hardcoded em alguns pontos (ex: motivo de bloqueio "12", agência "2020")
- Falta de validação de entrada mais robusta em alguns endpoints
- Código poderia se beneficiar de mais testes unitários e de integração documentados

---

## 14. Observações Relevantes

1. **Profiles de Execução:** Sistema possui profiles separados para unit, integration e functional tests

2. **Retry Strategy:** Implementa retry com backoff exponencial para encerramento Global (3 tentativas, 1s inicial, multiplicador 2)

3. **Filtros Específicos:** Aplica filtro para agência 2020 em processamentos de desinteresse e imediatas

4. **Propagação de Contexto:** Utiliza MDC (Mapped Diagnostic Context) para propagação de ticket através das mensagens

5. **Deserialização Customizada:** Implementa deserializer customizado para OffsetDateTime/LocalDateTime

6. **Monitoramento:** Actuator exposto na porta 9090 para health checks e métricas

7. **Encoding:** Utilitários para conversão entre UTF-8 e ISO-8859-1

8. **Códigos de Erro:** Sistema possui enum extenso de códigos de erro categorizados (BDCC_*, GLOB_*, VUCL_*)

9. **Orquestração Complexa:** Utiliza múltiplos routers Camel para diferentes fluxos de encerramento (Desinteresse, Imediatas, Salesforce, Cockpit)

10. **Integração Assíncrona:** Combina processamento síncrono (REST) com assíncrono (Pub/Sub) para diferentes cenários

11. **Validações em Múltiplas Camadas:** Implementa validações tanto em processors Camel quanto em services

12. **Gestão de Bloqueios:** Sistema responsável por criar bloqueios de movimentação como parte do processo de encerramento