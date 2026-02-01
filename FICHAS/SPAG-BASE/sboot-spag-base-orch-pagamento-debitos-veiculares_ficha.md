# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema orquestrador de pagamento de débitos veiculares (IPVA, licenciamento, multas) que gerencia o fluxo completo de liquidação através de integração com múltiplas APIs e processamento assíncrono via RabbitMQ. O sistema valida credenciais, efetiva débitos/créditos em contas correntes, integra com o arrecadador Celcoin para processamento de pagamentos, e notifica parceiros sobre o resultado das transações. Utiliza Apache Camel para orquestração de rotas e segue arquitetura hexagonal (ports and adapters).

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **PagamentoDebitosVeicularesService** | Serviço principal que orquestra todo o fluxo de liquidação via rotas Camel |
| **PagamentoDebitosVeicularesController** | Controller REST que expõe endpoints para solicitação de liquidação e callbacks |
| **SolicitaLiquidacaoRouter** | Rota Camel que valida segurança, parcerias, liquidação e confirma pagamento |
| **EfetivaPagamentoCelcoinRouter** | Rota Camel que consulta status no Celcoin e decide entre estorno ou sucesso |
| **PagamentoDebitosVeicularesRouter** | Rota Camel que orquestra débito fintech, crédito BV e atualização de liquidação |
| **EfetivaPagamentoCelcoinListener** | Listener RabbitMQ que processa mensagens de efetivação de pagamento Celcoin |
| **ContaCorrenteRepositoryImpl** | Repository que efetiva débitos e créditos em conta corrente |
| **DebitosVeicularesRepositoryImpl** | Repository que monta solicitação de liquidação e consulta pagamentos no Celcoin |
| **ParceriasRepositoryImpl** | Repository que valida correspondente e busca dados do cliente |
| **SegurancaRepositoryImpl** | Repository que valida permissões do cliente para liquidação |
| **ValidaLiquidacaoRepositoryImpl** | Repository que busca pagamentos pendentes e valida arrecadador |
| **ArrecadadorProcessor** | Processor Camel que busca dados do arrecadador Celcoin |
| **DebitoContaFintechProcessor** | Processor Camel que monta dados para débito da conta fintech |
| **CreditoContaBaldeBVProcessor** | Processor Camel que monta dados para crédito na conta balde BV (UAT/PRD) |

---

## 3. Tecnologias Utilizadas

- **Framework Principal**: Spring Boot 2.x
- **Orquestração**: Apache Camel
- **Mensageria**: RabbitMQ (Spring AMQP)
- **Segurança**: Spring Security OAuth2 (Client Credentials)
- **Mapeamento**: MapStruct
- **Documentação**: Springfox (Swagger/OpenAPI 3.0)
- **Serialização**: Jackson (JSON/XML)
- **HTTP Client**: RestTemplate
- **Pool de Conexões**: HikariCP
- **Utilitários**: Lombok
- **Build**: Maven (multi-módulo)
- **Monitoramento**: Prometheus/Grafana (métricas)
- **Conversão de Mensagens**: Jackson2JsonMessageConverter

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/solicitacao/liquidar | PagamentoDebitosVeicularesController | Solicita liquidação de débitos veiculares |
| POST | /v1/processarCallBackParceiro | PagamentoDebitosVeicularesController | Processa callback de retorno do parceiro |
| POST | /v1/debito-veicular/callback | PagamentoDebitosVeicularesController | Recebe callback de processamento de débito veicular |

---

## 5. Principais Regras de Negócio

1. **Validação de Segurança**: Cliente/parceiro deve ter permissão para liquidação (origem padrão = 88)
2. **Validação de Correspondente**: Correspondente deve ser válido e cliente deve existir (liquidação = 66)
3. **Validação de Arrecadador**: Arrecadador deve estar ativo e cadastrado (Celcoin CNPJ: 13935893000109)
4. **Validação de Pagamentos Pendentes**: Não pode haver pagamentos pendentes para o mesmo débito
5. **Débito Fintech**: Debita valor da conta da fintech antes de processar pagamento
6. **Crédito Conta Balde BV**: Credita valor em conta específica BV (UAT: 153145064, PRD: 11743573)
7. **Consulta Status Celcoin**: Verifica status do pagamento no Celcoin antes de confirmar
8. **Estorno Automático**: Em caso de falha no Celcoin, realiza estorno automático na conta corrente
9. **Atualização de Status**: Atualiza flag `fl_lancado_conta_corrente` e `st_lancamento` na tabela de liquidação
10. **Notificação Assíncrona**: Envia notificações via RabbitMQ para sistemas dependentes
11. **Tratamento de Ocorrências**: Registra ocorrências com códigos específicos (0-14, 99) para rastreamento

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **SolicitaLiquidacaoRequestDomain**: Agregador principal contendo fintech, cliente, devedor, veículo, arrecadador, validação e autenticação
  - Contém: **Debtor** (dados bancários do devedor)
  - Contém: **Vehicle** (protocolo e lista de débitos)
  - Contém: **Arrecadador** (código e CNPJ)
  - Referencia: **Origin** (código e sistema de origem)

- **ValidaResponseDomain**: Resposta de validação contendo dados completos para confirmação
  - Contém: **PartResponseDomain** (remetente e favorecido)
  - Contém: **CoParticipanteDomain** (co-titulares)
  - Contém: **ContaCorrenteDomain** (códigos de transação)

- **PagamentoOcorrencia**: Registro de ocorrência de pagamento
  - Contém: **Ocorrencia** (código, descrição, erro)
  - Referencia: **SituacaoLancamentoEnum** (status 0-14, 99)

- **DadosConta**: Dados da conta para finalidade específica
  - Referencia: **TipoContaEnum** (tipo de conta)
  - Referencia: **TipoPessoaEnum** (física/jurídica)

**Relacionamentos:**
- 1 SolicitaLiquidacaoRequest → N VehicleDebts
- 1 Vehicle → N Debts
- 1 PagamentoOcorrencia → 1 Ocorrencia
- 1 ValidaResponseDomain → N CoParticipanteDomain

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| tb_liquidacao | tabela | SELECT | Consulta pagamentos solicitados e status de liquidação |
| tb_arrecadador | tabela | SELECT | Busca dados do arrecadador cadastrado |
| tb_debito_veicular | tabela | SELECT | Consulta débitos veiculares pendentes |
| tb_conta_arrecadador | tabela | SELECT | Busca dados bancários da conta do arrecadador |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| tb_liquidacao | tabela | UPDATE | Atualiza `fl_lancado_conta_corrente` e `st_lancamento` após processamento |
| tb_debito_veicular_liquidacao | tabela | INSERT | Insere registro de débito veicular liquidado |

---

## 9. Arquivos Lidos e Gravados

não se aplica

---

## 10. Filas Lidas

| Nome da Fila | Tecnologia | Classe Responsável | Descrição |
|--------------|------------|-------------------|-----------|
| events.business.SPAG-BASE.debitoVeicular.efetivar | RabbitMQ | EfetivaPagamentoCelcoinListener | Consome mensagens para efetivar pagamento no Celcoin (formato XML) |

---

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Responsável | Descrição |
|--------------|------------|-------------------|-----------|
| {exchange configurável}/{routingkey configurável} | RabbitMQ | AtualizarLiquidacaoDebitosVeicularesRepositoryImpl | Envia notificação de atualização de liquidação |
| events.business.confirmarPagamentoApi / SPAG.rk.confirmarPagamentoApi | RabbitMQ | ConfirmarPagamentoRepositoryImpl | Envia confirmação de pagamento processado |

---

## 12. Integrações Externas

| Sistema/API | Tipo | Classe Responsável | Descrição |
|-------------|------|-------------------|-----------|
| sboot-spag-base-atom-valida-debitos-veiculares | REST API | ArrecadadorRepositoryImpl | Valida e busca dados de arrecadadores |
| sboot-spag-base-atom-registrar-debitos-veiculares | REST API | AtualizarLiquidacaoRepositoryImpl | Registra e atualiza liquidação de débitos |
| API Conta Corrente (EfetivarDebito/Credito) | REST API | ContaCorrenteRepositoryImpl | Efetiva débitos e créditos em conta corrente |
| API Débitos Veiculares | REST API | DebitosVeicularesRepositoryImpl | Consulta e gerencia débitos veiculares |
| API Celcoin (DefaultApi) | REST API | DebitosVeicularesRepositoryImpl | Consulta status de pagamentos no Celcoin |
| API Parcerias (ValidarCorrespondente/BuscarClientes) | REST API | ParceriasRepositoryImpl | Valida correspondentes e busca dados de clientes |
| API Segurança (SegurancaController) | REST API | SegurancaRepositoryImpl | Valida permissões de clientes/parceiros |
| API Suporte Negócio (ValidaPagamentoDebitoVeicular) | REST API | ValidaPagamentoDebitoVeicularRepositoryImpl | Valida regras de negócio para pagamento |
| API Liquidar Pagamento | REST API | RealizarEstornoPagamentoCelcoinRepositoryImpl | Realiza estorno de pagamentos no Celcoin |

**Autenticação**: OAuth2 Client Credentials para APIs internas, Basic Auth para APIs externas (Celcoin)

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura hexagonal bem definida com separação clara entre domain, ports e adapters
- Uso adequado de padrões de projeto (Repository, Service, Factory)
- Boa separação de responsabilidades com uso de Apache Camel para orquestração
- Configurações externalizadas via @ConfigurationProperties
- Uso de MapStruct para mapeamento de objetos, reduzindo código boilerplate
- Tratamento de exceções centralizado com handlers específicos
- Documentação via Swagger/OpenAPI
- Uso de Lombok para reduzir verbosidade
- Estrutura modular (Maven multi-módulo)

**Pontos de Melhoria:**
- Falta de testes unitários e de integração evidentes na documentação
- Algumas classes de repository implementam lógica de negócio que poderia estar em services
- Configurações hardcoded em alguns processors (contas balde UAT/PRD)
- Falta de documentação inline (JavaDoc) em classes críticas
- Alguns nomes de variáveis e métodos poderiam ser mais descritivos
- Tratamento de erro poderia ser mais granular em alguns fluxos

O código demonstra maturidade arquitetural e boas práticas de desenvolvimento, mas há espaço para melhorias em testabilidade e documentação.

---

## 14. Observações Relevantes

1. **Contas Balde BV**: Sistema utiliza contas específicas por ambiente (UAT: 153145064, PRD: 11743573) para crédito de valores
2. **Arrecadador Padrão**: Celcoin (CNPJ: 13935893000109) é o arrecadador principal integrado
3. **Fluxo Crítico**: O fluxo de liquidação é crítico e envolve múltiplas validações sequenciais antes de efetivar o pagamento
4. **Processamento Assíncrono**: Utiliza RabbitMQ para desacoplar processamento de efetivação do Celcoin
5. **Resiliência**: Implementa mecanismo de estorno automático em caso de falha no processamento
6. **Ambientes**: Sistema diferencia comportamento entre UAT e PRD através de Spring Profiles
7. **Rastreabilidade**: Utiliza protocolo de transação e códigos de lançamento para rastreamento completo
8. **Estados de Liquidação**: Sistema gerencia 16 estados diferentes de liquidação (0-14, 99) via enum
9. **Segurança**: Implementa validação de permissões em múltiplas camadas (segurança, parcerias, correspondente)
10. **Monitoramento**: Preparado para integração com Prometheus/Grafana para observabilidade
11. **Formato de Mensagens**: Listener processa mensagens XML do Celcoin, enquanto notificações são enviadas em JSON
12. **Error Handling**: RabbitMQ configurado para rejeitar mensagens com erro sem requeue, evitando loops infinitos