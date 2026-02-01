# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de orquestração de débito automático para produtos financeiros (Cartão de Crédito e Financiamento de Veículos) do Banco Votorantim. Gerencia o ciclo completo de agendamento, processamento, liquidação e cancelamento de pagamentos automáticos, integrando-se com múltiplos sistemas legados (FLEX, GDCC, CART, SPAG, Global) através de APIs REST e mensageria assíncrona (RabbitMQ e Google Pub/Sub). Implementa controle de rollout por CPF para novos produtos, feature toggles para ativação gradual de funcionalidades e validações de saldo/conta bancária.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot que inicializa a aplicação |
| `DebitoAutomaticoConfiguration` | Configuração de beans de serviços e rotas Apache Camel |
| `DebitoAutomaticoController` | Controlador REST para endpoints de consulta e gestão de débito automático |
| `FinanciamentoService` | Orquestra operações de débito automático para financiamentos de veículos |
| `CartaoService` | Orquestra operações de débito automático para cartões de crédito |
| `PagamentoService` | Gerencia agendamentos e cancelamentos de pagamentos |
| `SpagService` | Processa transferências bancárias via SPAG e verifica status de pagamentos |
| `NotificacaoService` | Centraliza envio de notificações (RabbitMQ e Push) |
| `AgendarPagamentoDebitoAutomaticoRepositoryImpl` | Gerencia agendamentos no sistema atomico |
| `SpagRepositoryImpl` | Realiza transferências SPAG e validação de protocolos |
| `DadosCadastraisRepositoryImpl` | Consulta dados cadastrais de clientes no sistema Global |
| `CartaoRepositoryImpl` | Consulta cartões de crédito em débito automático |
| `DebitoAutomaticoFinanciamentoRepositoryImpl` | Consulta contratos de financiamento em débito automático |
| `AgendamentoPagamentoDebitoAutomaticoListener` | Consumidor RabbitMQ para eventos de agendamento |
| `RemessaDebitoAutomaticoListener` | Consumidor RabbitMQ para eventos de remessa |
| `LiquidacaoListener` | Consumidor RabbitMQ para eventos de liquidação |
| `AtualizaStatusListener` | Consumidor Google Pub/Sub para atualização de status |
| `ExceptionHandler` | Tratamento global de exceções REST |
| `ValidacaoUtils` | Utilitários de validação (CPF, data, NSU) |
| `Utilitario` | Geração de NSU de 30 posições |

---

## 3. Tecnologias Utilizadas

- **Framework**: Spring Boot 2.x, Apache Camel 3.0.1
- **Linguagem**: Java 11
- **Mensageria**: RabbitMQ, Google Cloud Pub/Sub
- **Segurança**: Spring Security OAuth2, JWT, Basic Auth
- **Persistência**: HikariCP (pool de conexões)
- **Mapeamento**: MapStruct
- **Documentação**: Swagger/OpenAPI
- **Monitoramento**: Prometheus, Grafana, Spring Actuator
- **Logging**: Logback (JSON estruturado)
- **Feature Toggle**: ConfigCat
- **Testes**: JUnit 5, Mockito, CamelTestSupport, Pact
- **Build**: Maven 3.3+
- **Containerização**: Docker, Kubernetes (OpenShift)
- **CI/CD**: Jenkins

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/debito-automatico/produtos` | `DebitoAutomaticoController` | Lista produtos em débito automático por CPF |
| GET | `/v1/debito-automatico/status` | `DebitoAutomaticoController` | Consulta status de débito automático |
| POST | `/v1/debito-automatico/atualizar-status` | `DebitoAutomaticoController` | Atualiza status de débito automático (ativar/desativar) |
| GET | `/v1/debito-automatico/faturas-efetivadas-cartao` | `DebitoAutomaticoController` | Lista faturas efetivadas de cartão por período |
| DELETE | `/v1/debito-automatico/cancelar-pagamento/{nsu}` | `DebitoAutomaticoController` | Cancela pagamento por NSU |
| GET | `/actuator/health` | Spring Actuator | Health check (porta 9090) |
| GET | `/actuator/prometheus` | Spring Actuator | Métricas Prometheus (porta 9090) |
| GET | `/swagger-ui.html` | Swagger UI | Documentação interativa da API |

---

## 5. Principais Regras de Negócio

1. **Controle de Rollout por CPF**: Financiamentos só são habilitados para CPFs autorizados via feature toggle
2. **Validação de Produtos Ativos**: 
   - Financiamentos: status < 10, modalidade ≠ 87
   - Cartões: processadora = 1 (Quina)
3. **Validação de Conta Bancária**: Agência deve ser 2020, validação de banco (436/413/161/655)
4. **Geração de NSU**: Formato 30 posições (CodOrigem(5) + CPF/CNPJ(14) + UUID(11)), controlado por feature toggle
5. **Validação de Saldo**: Consulta saldo antes de transferência (controlado por toggle)
6. **Ajuste de Vencimento**: Vencimentos em dias não úteis são ajustados para próximo dia útil (praça BR=1)
7. **Tratamento de Erros SPAG**: 
   - Conta inválida/encerrada/bloqueada: status `PAGAMENTO_ERRO`
   - Saldo insuficiente: status `SALDO_INSUFICIENTE`
   - Serviço indisponível: status `SERVICO_INDISPONIVEL`
   - Status 208 (Already Reported): tratamento específico
8. **Cancelamento de Agendamento**: Por contrato ou NSU, com envio de baixa para GDCC
9. **Notificações**: 
   - Push para Crédito Pessoal/Fácil
   - RabbitMQ para demais produtos
10. **Controle de Tentativas**: Retry exponencial para falhas de comunicação
11. **Filtro de Modalidade CVG**: Contratos com modalidade CVG podem ser filtrados via toggle
12. **Vinculação de Garantias**: Contratos de financiamento são vinculados a garantias de veículos
13. **Validação de Linha Digitável**: Limpeza e formatação de linha digitável de faturas
14. **Mapeamento de Status Protocolo SPAG**: Conversão de códigos SPAG para status internos

---

## 6. Relação entre Entidades

**Modelo de Domínio Principal:**

```
Pessoa (CPF, conta bancária)
  └── Produto (CARTAO | FINANCIAMENTO)
       ├── CartaoCredito (número, convênio, status)
       │    └── Fatura (vencimento, valor, linha digitável)
       │
       └── ContratoFinanciamento (número, modalidade, status)
            └── Garantia
                 └── GarantiaVeiculo (placa, chassi, marca, modelo)

PagamentoDebitoAutomatico
  ├── AgendamentoInfo (data, valor, NSU)
  └── PagamentoInfo (status, protocolo SPAG)

PagamentoEnviado (NSU, protocolo, status, tentativas)
  └── StatusProcessoPagamentoEnum (PAGAMENTO_ENVIADO, PAGO, PAGAMENTO_ERRO, etc.)

PagamentoBaixa (contrato, parcela, status=9 CANCELADO)
```

**Relacionamentos:**
- 1 Pessoa → N Produtos (Cartão ou Financiamento)
- 1 CartaoCredito → N Faturas
- 1 ContratoFinanciamento → N Garantias
- 1 PagamentoDebitoAutomatico → 1 PagamentoEnviado
- 1 PagamentoEnviado → 1 Protocolo SPAG

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| Contratos Financiamento (FLEX) | Tabela | SELECT | Consulta contratos de financiamento ativos |
| Garantias Veículos (FLEX) | Tabela | SELECT | Consulta garantias vinculadas a contratos |
| Débito Automático Financiamento (GDCC) | Tabela | SELECT | Consulta contratos em débito automático |
| Cartões Crédito (CART) | Tabela | SELECT | Consulta cartões de crédito por CPF |
| Dados Cadastrais (Global) | Tabela | SELECT | Consulta dados cadastrais de clientes |
| Saldo Conta (CCBD) | Tabela | SELECT | Consulta saldo disponível em conta |
| Faturas Cartão (CART) | Tabela | SELECT | Consulta faturas efetivadas de cartão |
| Convênio Quina (CART) | Tabela | SELECT | Consulta processadora de cartão |
| Dias Úteis (DCOR) | Tabela | SELECT | Validação de dias úteis bancários |
| Protocolo SPAG | Tabela | SELECT | Validação de status de protocolo de pagamento |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| Agendamentos Débito Automático (atomico) | Tabela | INSERT/UPDATE/DELETE | Criação, atualização e cancelamento de agendamentos |
| Pagamentos Enviados (atomico) | Tabela | INSERT/UPDATE | Registro e atualização de status de pagamentos enviados ao SPAG |
| Linha Digitável Faturas (atomico) | Tabela | UPDATE | Atualização de linha digitável de faturas de cartão |
| Baixa Parcelas GDCC | Fila/Tabela | INSERT | Envio de baixa de parcelas para GDCC |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | Spring Boot Config | Configurações da aplicação por ambiente (local/des/qa/uat/prd) |
| logback-spring.xml | Leitura | Logback | Configuração de logs estruturados em JSON |
| rabbitmq_definitions.json | Leitura | RabbitMQ | Definição de filas, exchanges e bindings |
| prometheus.yml | Leitura | Prometheus | Configuração de scraping de métricas |
| grafana.ini | Leitura | Grafana | Configuração do servidor Grafana |
| default.json | Leitura | Grafana | Dashboard de monitoramento |
| infra.yml | Leitura | Kubernetes | ConfigMaps e Secrets para deploy |

---

## 10. Filas Lidas

| Nome da Fila | Tecnologia | Classe Consumidora | Descrição |
|--------------|-----------|-------------------|-----------|
| `debito_automatico.agendar.pagamento` | RabbitMQ | `AgendamentoPagamentoDebitoAutomaticoListener` | Eventos de agendamento de pagamento |
| `events.remessaDebitoAutomatico` | RabbitMQ | `RemessaDebitoAutomaticoListener` | Eventos de remessa de débito automático |
| `debito_automatico.liquidacao` | RabbitMQ | `LiquidacaoListener` | Eventos de liquidação de pagamentos |
| `business-ccbd-base-atualizacao-status-pgto-debauto` | Google Pub/Sub | `AtualizaStatusListener` | Atualização de status de pagamentos enviados |

---

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Produtora | Descrição |
|--------------|-----------|-----------------|-----------|
| `ex.ccbd.debito.automatico` (routing key: `agendar.pagamento`) | RabbitMQ | `NotificacaoDebitoAutomaticoRepositoryImpl` | Notificação de agendamento de pagamento |
| `ex.ccbd.debito.automatico` (routing key: `liquidacao`) | RabbitMQ | `PagamentoDebitoAutomaticoRepositoryImpl` | Notificação de liquidação de pagamento |
| `ex.ccbd.debito.automatico` (routing key: `ccbd.remessa.debito.automatico`) | RabbitMQ | `NotificacaoDebitoAutomaticoRepositoryImpl` | Notificação de remessa |
| `ex.ccbd.baixa.debito.automatico` | RabbitMQ | `EnviarBaixaGDCCRepositoryImpl` | Envio de baixa de parcelas para GDCC |
| Topic de verificação de liquidação | Google Pub/Sub | `PagamentosEnviadosRepositoryImpl` | Solicitação de verificação de liquidação no SPAG |

---

## 12. Integrações Externas

| Sistema | Tipo | Endpoints/Filas | Descrição |
|---------|------|----------------|-----------|
| **FLEX** (Gestão Contrato) | REST API | GET contratos, dados complementares | Consulta contratos de financiamento |
| **FLEX** (Garantia Contrato) | REST API | GET garantias veículos | Consulta garantias vinculadas a contratos |
| **GDCC** (Débito Automático) | REST API | GET contrato débito automático | Consulta contratos em débito automático |
| **CART** (Cartão) | REST API | GET cartões por CPF, convênio Quina | Consulta cartões de crédito |
| **CART** (Fatura) | REST API | GET dados fatura, faturas efetivadas | Consulta faturas de cartão |
| **SPAG** (Transferências) | REST API | POST transferência, GET validar protocolo | Realiza transferências bancárias |
| **CRBD** (Notificação Push) | REST API | POST push agendamento/pagamento | Envia notificações push para Crédito Pessoal/Fácil |
| **CCBD** (Saldo) | REST API | GET saldo conta | Consulta saldo disponível |
| **CCBD** (Atomico Débito Auto) | REST API | POST/PUT/DELETE agendamentos | Gerencia agendamentos |
| **Global** (Dados Cadastrais) | REST API | GET por conta/CPF | Consulta dados cadastrais de clientes |
| **DCOR** (Validar Dia Útil) | REST API | GET validar dia útil | Validação de dias úteis bancários |
| **RabbitMQ** | Mensageria | Múltiplas filas | Comunicação assíncrona entre sistemas |
| **Google Pub/Sub** | Mensageria | Topics/Subscriptions | Comunicação assíncrona para atualização de status |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- **Arquitetura bem estruturada**: Separação clara entre camadas (domain, application, infra) seguindo princípios de Clean Architecture
- **Testes abrangentes**: Cobertura de testes unitários para controllers, services, repositories, processors e listeners
- **Uso de padrões**: Implementação de Repository Pattern, Service Layer, Exception Handlers globais
- **Observabilidade**: Integração completa com Prometheus/Grafana, logs estruturados em JSON, métricas detalhadas
- **Feature Toggles**: Uso de ConfigCat para controle de rollout e ativação gradual de funcionalidades
- **Validações centralizadas**: Classe `ValidacaoUtils` concentra validações reutilizáveis
- **Mapeamento automatizado**: Uso de MapStruct para conversão de DTOs
- **Documentação**: Swagger/OpenAPI para documentação de APIs
- **Tratamento de erros robusto**: Exception handlers específicos, retry com backoff exponencial
- **Segurança**: OAuth2, JWT, Basic Auth implementados

**Pontos de Melhoria:**
- **Complexidade de rotas Camel**: Algumas rotas Camel poderiam ser simplificadas ou melhor documentadas
- **Acoplamento com feature toggles**: Muitas decisões de negócio dependem de toggles, dificultando testes
- **Falta de testes de integração**: Poucos testes de integração end-to-end documentados
- **Documentação inline**: Alguns métodos complexos carecem de JavaDoc explicativo
- **Hardcoded values**: Alguns valores mágicos (ex: status=9, modalidade=87) poderiam ser constantes nomeadas

---

## 14. Observações Relevantes

1. **Feature Toggles Críticos**:
   - `FT_CONSULTAR_LINHA_DIGITAVEL_*`: Controla consulta de linha digitável de faturas
   - `FT_BLOQUEAR_DEBITO_AUTOMATICO`: Bloqueia débito automático por processadora
   - Validação de saldo: Controlada por toggle
   - Envio de NSU 30 posições: Controlado por toggle
   - Rollout de financiamento: Controlado por lista de CPFs

2. **Ambientes**:
   - Local: Desenvolvimento local com RabbitMQ via Docker Compose
   - DES/QA/UAT/PRD: Ambientes na nuvem Google com configurações específicas

3. **Portas**:
   - 8080: API REST
   - 9090: Actuator (health, metrics)
   - 9060: Prometheus
   - 3000: Grafana
   - 5672: RabbitMQ AMQP
   - 15672: RabbitMQ Management
   - 15692: RabbitMQ Prometheus

4. **Retry e Resiliência**:
   - RabbitMQ: Retry com exponential backoff
   - Google Pub/Sub: Manual ACK para controle de reprocessamento
   - Tratamento específico para status 208 (Already Reported) do SPAG

5. **Segurança**:
   - Autenticação via OAuth2 e Basic Auth
   - Secrets gerenciados via Kubernetes Secrets
   - Contexto de segurança Spring (`BvUserDetails`)

6. **Monitoramento**:
   - Métricas JVM (heap, GC, threads)
   - Métricas HikariCP (pool de conexões)
   - Métricas HTTP (request count, response time)
   - Métricas Logback (contadores por nível)
   - Dashboard Grafana pré-configurado

7. **CI/CD**:
   - Pipeline Jenkins configurado
   - Deploy em OpenShift (Kubernetes)
   - Profiles Maven para diferentes tipos de testes (unit, integration, functional, architecture)

8. **Bancos Suportados**:
   - Banco BV: 436, 413
   - Banco Votorantim: 161, 655
   - Agência padrão: 2020

9. **Tipos de Produto**:
   - Financiamento de Veículo: código 2 ou 12
   - Crédito Pessoal: código 3
   - Crédito Fácil: código 4
   - Cartão de Crédito: identificado por processadora

10. **Formato NSU**:
    - Legado: formato variável
    - Novo: 30 posições (CodOrigem(5) + CPF/CNPJ(14) + UUID(11))
    - Transição controlada por feature toggle