---
## Ficha Técnica do Sistema

### 1. Descrição Geral
O **sboot-ccbd-base-orch-proc-agendmt** é um microsserviço orquestrador responsável pelo processamento automatizado de agendamentos bancários digitais. O sistema consome mensagens de filas (IBM MQ e RabbitMQ), valida regras de negócio (limites transacionais, grades horárias, dados cadastrais), e efetiva operações financeiras como pagamentos de boletos, tributos, transferências (TED/DOC/TEF), PIX e aplicações em investimentos. Atua como hub de integração entre múltiplos serviços bancários, garantindo a execução coordenada de agendamentos conforme data programada.

---

### 2. Principais Classes e Responsabilidades

| Classe/Componente | Responsabilidade |
|-------------------|------------------|
| `ProcAgendmtService` | Orquestra fluxos de processamento de agendamentos, coordenando validações e efetivações |
| `ProcAgendmtRouter` | Roteador Camel principal que direciona mensagens para fluxos específicos por tipo de operação |
| `AgendmtCobrancaRouter` | Processa agendamentos de boletos de cobrança |
| `AgendmtTransferenciaRouter` | Processa agendamentos de transferências (TED/DOC/TEF) |
| `EfetivarPixRouter` | Efetiva transferências PIX agendadas |
| `AgendmtInvestimentoRouter` | Processa aplicações em investimentos agendadas |
| `ProcessarAgendamentoListener` | Listener JMS que consome mensagens de agendamento da fila IBM MQ |
| `ProcessarAgendamentoPixListener` | Listener RabbitMQ específico para agendamentos PIX |
| `RecuperarAgendamentoRepository` | Recupera informações de agendamentos via API atom-movimentacoes |
| `EfetivarPagamentoBoletoRepository` | Efetiva pagamentos de boletos e tributos via APIs específicas |
| `LimiteTransacionalRepository` | Valida e reserva limites transacionais via SGLT |
| `TransferenciaRepository` | Efetiva transferências via API orch-transferencias |
| `InvestimentoRepository` | Aplica investimentos via API envelope-investimento |
| `NotificacaoPushRepository` | Envia notificações push aos clientes |
| `HorarioPermitidoUtil` | Valida grades horárias permitidas para cada tipo de operação |
| `FeatureToggleService` | Controla ativação/desativação de funcionalidades por ambiente |

---

### 3. Tecnologias Utilizadas

- **Framework:** Spring Boot 2.x
- **Linguagem:** Java 11
- **Integração:** Apache Camel 3.22.4
- **Mensageria:** RabbitMQ (AMQP), IBM MQ (JMS)
- **Build:** Maven (multi-módulo)
- **Segurança:** OAuth2, JWT
- **Documentação:** Swagger/OpenAPI 2.0
- **Resiliência:** Resilience4j (circuit breaker)
- **Observabilidade:** Prometheus, Grafana
- **Serialização:** Jackson (JSON)
- **Testes:** JUnit, Mockito, profiles segregados (unit/integration/functional/architecture)
- **Deploy:** Kubernetes/OpenShift
- **Versionamento:** Git

---

### 4. Principais Endpoints REST

O sistema **não expõe endpoints REST públicos** diretamente. Atua como consumidor de filas e integrador de APIs externas. A documentação Swagger (`sboot-ccbd-base-orch-proc-agendmt.yaml`) descreve um endpoint interno:

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/corporativo/pagamentos/processar/agendamento` | Não aplicável (interno) | Endpoint documentado para processamento de agendamento (possivelmente para testes ou chamadas internas síncronas) |

**Observação:** O fluxo principal é assíncrono via mensageria.

---

### 5. Principais Regras de Negócio

1. **Validação de Grade Horária:**
   - Tributos/consumo: permitidos até 16h25
   - Transferências: horários variáveis conforme tipo (TED/DOC/TEF)
   - Boletos cobrança: validação específica por valor

2. **Validação de Limites Transacionais:**
   - Integração com SGLT (Sistema de Gestão de Limites Transacionais)
   - Reserva de limite antes da efetivação
   - Liberação de limite em caso de erro
   - Boletos BV (CNPJs específicos) isentos de validação de limite
   - Controlado por feature toggle

3. **Roteamento por Código de Liquidação:**
   - `PAGAMENTO_TRIBUTOS` (59) / `CONCESSIONARIA` (60) → Pagamento tributos
   - `LIQUIDACAO_POR_COBRANCA` (61/62) → Pagamento boletos cobrança
   - `CC_TEF` (1) / `CIP_TED` (21) / `STR_TED` (31/32) → Transferências

4. **Agendamento PIX:**
   - Validação de chave DICT (CPF/CNPJ/EMAIL/PHONE/EVP)
   - Decodificação de QRCode quando aplicável
   - Validação de favorecido
   - Canal primário/secundário (fallback em timeout)
   - Tratamento de erros específicos: saldo insuficiente, limites, timeout Bacen

5. **Tentativas de Processamento:**
   - Investimentos: até 7 tentativas
   - Reenvio para fila de atualização em caso de erro

6. **Fluxo de Status:**
   - `AGENDADO` → `EFETIVADO` / `CANCELADO` / `NAO_EFETIVADO` / `ERRO`

7. **Notificações Push:**
   - Enviadas em caso de sucesso ou erro
   - Tipos: saldo insuficiente, favorecido inválido, QRCode inválido, limites excedidos

---

### 6. Relação entre Entidades

**Entidades Principais:**

- **Lancamento:** Representa um agendamento bancário
  - Relaciona-se com `ContaCorrente` (remetente e favorecido)
  - Contém `InfoLancamentoDTO` (detalhes boleto/tributo)
  - Contém `DadosAgendamento` (datas, status)

- **LancamentoDTO:** Agregador de dados de lançamento
  - Composição: `Lancamento` + `InfoLancamentoDTO` + `DadosAgendamento`

- **EfetivarAgendamentoPix:** Entidade específica para PIX
  - Relaciona-se com `MensagemPix`
  - Contém `ChaveDomain` (dados chave DICT)
  - Contém `PagamentoDomain` (dados QRCode decodificado)

- **ContaCorrente:** Dados bancários (banco, agência, conta, CPF/CNPJ)

**Relacionamentos:**
```
Lancamento (1) ─── (1) ContaCorrente (remetente)
           (1) ─── (1) ContaCorrente (favorecido)
           (1) ─── (0..1) InfoLancamentoDTO
           (1) ─── (1) DadosAgendamento

EfetivarAgendamentoPix (1) ─── (1) MensagemPix
                       (1) ─── (0..1) ChaveDomain
                       (1) ─── (0..1) PagamentoDomain
```

---

### 7. Estruturas de Banco de Dados Lidas

Não se aplica diretamente. O sistema não acessa bancos de dados via JDBC/JPA. Todas as leituras são realizadas via APIs REST de outros microsserviços (atom-movimentacoes, atom-info-pgto-trib-bol, dados-cadastrais).

---

### 8. Estruturas de Banco de Dados Atualizadas

Não se aplica diretamente. Atualizações são realizadas via APIs REST:
- **atom-movimentacoes:** Atualização de status de agendamentos
- **atom-info-pgto-trib-bol:** Gravação de detalhes de boletos
- **envelope-investimento:** Registro de aplicações

---

### 9. Arquivos Lidos e Gravados

Não se aplica. O sistema não manipula arquivos diretamente. Toda comunicação é via mensageria (filas) e APIs REST.

---

### 10. Filas Lidas

| Nome da Fila | Tecnologia | Descrição |
|--------------|-----------|-----------|
| `QL.CCBD.PROC_AGENDAMENTO_DIG.INT` | IBM MQ (QM.DIG.01) | Fila principal de entrada para agendamentos gerais (boletos, tributos, transferências) |
| `ccbd_agendamento_pix` | RabbitMQ | Fila específica para agendamentos PIX |

**Observação:** Configurações de filas definidas em `AppProperties` (inQueueName, queueNameCash, queueAtualizaAgend, queueNotificacaoPush).

---

### 11. Filas Geradas

| Nome da Fila | Tecnologia | Descrição |
|--------------|-----------|-----------|
| `QL.CCBD.LIQ_PAGMT_CONTAS_DIG.INT` | IBM MQ | Fila para envio de pagamentos à esteira de liquidação (queueNameCash) |
| `QL.CCBD.PROC_PGMT_AGENDADOS_DIG.INT` | IBM MQ | Fila para atualização de status de agendamentos (queueAtualizaAgend) |
| `notificacao_agendamento_pix` | RabbitMQ | Fila para notificações push de agendamentos PIX (exchange: `ex.ccbd.agendamento`) |

---

### 12. Integrações Externas

| Sistema/API | Finalidade |
|-------------|-----------|
| **sboot-ccbd-base-orch-efet-transf-pix** | Efetivação de transferências PIX |
| **sboot-ccbd-base-orch-chaves-dict** | Consulta e validação de chaves DICT (PIX) |
| **sboot-ccbd-base-orch-pix-qrcode** | Decodificação de QRCode PIX |
| **sboot-spag-base-orch-pagamento-boleto-srv** | Efetivação de pagamentos de boletos de cobrança |
| **sboot-spag-base-orch-pagamento-tributo-srv** | Efetivação de pagamentos de tributos e consumo |
| **sboot-spag-base-orch-transferencias** | Efetivação de transferências (TED/DOC/TEF) |
| **sboot-sglt-base-orch-limites-transacionais** | Validação e reserva de limites transacionais |
| **sboot-ccbd-base-atom-movimentacoes** | Consulta e atualização de dados de agendamentos |
| **sboot-ccbd-base-atom-info-pgto-trib-bol** | Consulta e gravação de informações de boletos/tributos |
| **sboot-glob-base-atom-cliente-dados-cadastrais** | Consulta de dados cadastrais de clientes |
| **sboot-binv-base-orch-envelope-investimento** | Aplicação de investimentos agendados |
| **sboot-gnms-base-orch-envio-push** | Envio de notificações push aos clientes |
| **ESB Adapter (Legacy)** | Transferências TEF para conta balde (endpoint: `/esb-adapter/v1/legacy/request`) |
| **API Gateway OAuth2** | Geração de tokens de autenticação para chamadas entre serviços |

---

### 13. Avaliação da Qualidade do Código

**Nota:** 8/10

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada em camadas (domain, application, common)
- Uso adequado de Apache Camel para orquestração de fluxos complexos
- Segregação clara de responsabilidades (routers, repositories, mappers)
- Tratamento robusto de exceções com handlers específicos
- Implementação de feature toggles para controle de funcionalidades
- Resiliência com circuit breaker (Resilience4j)
- Logs estruturados em JSON para observabilidade
- Testes segregados por tipo (unit/integration/functional/architecture)
- Documentação via Swagger/OpenAPI
- Uso de mappers para conversão entre DTOs e entidades de domínio

**Pontos de Melhoria:**
- Dependência de múltiplas APIs externas pode gerar acoplamento
- Configurações hardcoded em alguns pontos (ex: códigos de produto, sistema)
- Falta de documentação inline em alguns métodos complexos
- Alguns métodos com múltiplas responsabilidades (ex: validação + efetivação)
- Necessidade de melhor tratamento de timeouts e retries configuráveis

O código demonstra maturidade técnica, boas práticas de engenharia de software e preocupação com manutenibilidade, justificando a nota 8.

---

### 14. Observações Relevantes

1. **Projeto Multi-Módulo Maven:** Estrutura modular facilita manutenção e evolução independente de componentes.

2. **Profiles de Ambiente:** Configurações específicas para des/uat/prd, garantindo segregação de ambientes.

3. **Segurança:** Implementação de OAuth2 com JWT para autenticação entre serviços. Secrets gerenciados externamente.

4. **Deploy Cloud-Native:** Preparado para Kubernetes/OpenShift com infraestrutura como código.

5. **Feature Toggles:** Controle granular de funcionalidades por ambiente, incluindo hash UUID de CPF para testes A/B.

6. **Estratégias de Agregação Camel:** Unificação de respostas de múltiplos serviços em fluxos paralelos.

7. **Tratamento de Erros Específicos:**
   - `SaldoInsuficienteException`: Notificação ao cliente
   - `TimeOutBacenException`: Fallback para canal secundário PIX
   - `LimitesException`: Liberação de reserva e notificação
   - `ForaGradeHorarioException`: Reagendamento automático

8. **Observabilidade:** Integração com Prometheus/Grafana para monitoramento de métricas e saúde do sistema.

9. **Versionamento de APIs:** Suporte a múltiplas versões (v1/v2/v3) para retrocompatibilidade.

10. **Processamento Assíncrono:** Arquitetura orientada a eventos garante escalabilidade e desacoplamento.

---