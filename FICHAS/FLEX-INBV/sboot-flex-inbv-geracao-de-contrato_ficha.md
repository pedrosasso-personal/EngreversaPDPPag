# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de orquestração para geração de contratos financeiros FLEX INBV (Investimento Não Bancário Varejo) utilizando Camunda BPM como motor de workflow. O sistema processa mensagens JMS contendo solicitações de contratos, executa validações pré-contrato, cria o contrato no FlexCube, e realiza integrações pós-contrato (pagamentos, seguros, comissões, controladoria). Suporta fluxos regulares e irregulares (FGTS), produtos diversos (solar, estudantil), e integra com mais de 30 sistemas legados via SOAP e REST.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Entry point Spring Boot, configuração Camunda/OAuth2/JMS/Cache |
| `GeracaoContratoProcessFlow` | Orquestra fluxo Camunda, decide entre nova esteira ou legado BPEL |
| `GeracaoContratoListenerController` | REST API para controle do listener JMS (bloqueio/liberação) |
| `ManipulaGeracaoContratoListener` | Listener JMS que consome mensagens XML de contratos |
| `GeracaoContratoSchedule` | Scheduler que monitora Redis para controlar listener (circuit breaker) |
| `PreContratoServiceImpl` | Orquestra etapas pré-contrato (validações, taxas, alíquotas, cliente, hierarquia) |
| `PosContratoServiceImpl` | Orquestra etapas pós-contrato (criar contrato, controladoria, pendência, pagamento, comissão, seguros) |
| `CriarContratoDelegate` | Delegate Camunda que cria contrato no FlexCube, ajusta IOF, converte custos |
| `CustomIncidentHandler` | Handler de incidentes Camunda que envia notificação de erro via email |
| `WorkflowHelper` | Inicializa variáveis workflow para evitar OptimisticLocking Camunda |
| `GeracaoContratoMapper` | MapStruct mapper para conversão GeracaoContratoMensagem (XML/JMS) ↔ domínio interno |
| `WebServiceConnector` | Estende WebServiceTemplate, adiciona tracing e log request/response XML |
| `MetricContractService` | Gera métricas Micrometer para contratos (gerados, bloqueados, devolvidos, valores) |

---

## 3. Tecnologias Utilizadas

- **Framework**: Spring Boot 2.2.1, Spring Security, Spring JMS
- **Orquestração**: Camunda BPM 7.12.0 / Spring Boot Starter 3.4.0
- **Mensageria**: IBM MQ JMS 2.2.2
- **Integração**: JAX-WS (SOAP), Spring RestTemplate, OAuth2 Client
- **Mapeamento**: MapStruct 1.4.2, JAXB (XML marshalling)
- **Cache/Estado**: Redis (Spring Data Redis)
- **Banco de Dados**: PostgreSQL (Camunda), SQL Server (DBFLEX_WORK - via APIs)
- **Observabilidade**: Micrometer, Actuator, Logback JSON, Prometheus, Grafana
- **Testes**: JUnit 5, Mockito, Spring Test, MockServer
- **Build**: Maven, Swagger Codegen, OpenAPI Generator
- **Infraestrutura**: Kubernetes (GKE), Docker Compose

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| PUT | `/v1/contrato/listener/bloqueio` | `GeracaoContratoListenerController` | Bloqueia consumo de mensagens JMS |
| PUT | `/v1/contrato/listener/liberacao` | `GeracaoContratoListenerController` | Libera consumo de mensagens JMS |
| GET | `/v1/contrato/listener` | `GeracaoContratoListenerController` | Consulta status do listener JMS |
| POST | `/test` | `GeracaoContratoListenerController` (profile local-mock) | Envia mensagem para fila de teste |

**Observação**: Sistema consome APIs REST externas (30+ endpoints) mas expõe apenas endpoints de controle operacional.

---

## 5. Principais Regras de Negócio

- **Piloto de Funcionalidade**: Valida se produto/modalidade usa nova esteira Camunda ou encaminha para BPEL legado
- **Validação Contrato Existente**: Verifica se contrato já foi gerado para evitar duplicidade
- **Cálculo Financeiro**: Taxas (CET, pactuada, gerencial), IOF, alíquotas tributos, subsídios
- **Fluxos Irregulares**: Tratamento específico para FGTS (saque-aniversário) com cálculo de fluxo irregular
- **Integração Seguros**: Envio de dados para seguradoras (Cardif e outros) com mapeamento de participantes
- **Liberação Pagamentos**: Inclusão de pagamentos TED/boleto com validação de boletos FGTS
- **Comissões**: Liberação de pagamento de comissão parcelada ou total para parceiros comerciais
- **Controladoria**: Envio de dados para carga GGER (sistema contábil)
- **Pendências**: Criação de pendências de formalização de contrato
- **Hierarquia Comercial**: Obtenção de estrutura comercial (loja, operador, colaboradores)
- **Carnê Online**: Consulta e registro de lâminas de carnê
- **Retries Camunda**: Gerenciamento de retries com lançamento de BpmnError quando esgotados
- **Circuit Breaker**: Controle de listener JMS via Redis para evitar sobrecarga

---

## 6. Relação entre Entidades

**Entidade Raiz**: `GeracaoContrato`

**Relacionamentos principais**:
- `GeracaoContrato` 1 → 1 `Contrato`
- `GeracaoContrato` 1 → 1 `Proposta`
- `GeracaoContrato` 1 → 1 `Desembolso`
- `GeracaoContrato` 1 → N `Participante` (proponente, avalista, cônjuge)
- `GeracaoContrato` 1 → N `FavorecidoPrincipal` (destinatários desembolso)
- `GeracaoContrato` 1 → N `FavorecidoComissao` (recebedores comissão)
- `GeracaoContrato` 1 → 0..1 `BoletoPagamento` (FGTS)
- `Contrato` 1 → 1 `Produto` (código, modalidade, subproduto)
- `Contrato` 1 → N `Custo` (custos financiamento)
- `Contrato` 1 → N `Seguro` (apólices)
- `Contrato` 1 → N `Garantia` (veículos, imóveis)
- `Contrato` 1 → N `Parcela` (cronograma pagamento)
- `Contrato` 1 → 1 `Taxa` (CET, IOF, pactuada, gerencial)
- `Contrato` 1 → 0..1 `Subsidio`
- `Participante` 1 → 1 `PessoaFisica` ou `PessoaJuridica`
- `Participante` 1 → N `Endereco`
- `Participante` 1 → N `Telefone`
- `Participante` 1 → N `ReferenciaPessoal`
- `Participante` 1 → N `ReferenciaBancaria`
- `PessoaFisica` 1 → N `Documento`
- `PessoaFisica` 1 → N `Emprego`
- `PessoaFisica` 1 → N `Receita`
- `PessoaJuridica` 1 → N `FaturamentoMensal`

**Observação**: Modelo de domínio rico com entidades financeiras complexas seguindo padrões DDD.

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| N/A | N/A | N/A | Sistema não acessa banco de dados diretamente. Todas as leituras são realizadas via APIs REST/SOAP de sistemas legados (FlexCube, controladoria, seguros, etc). |

**Observação**: PostgreSQL é usado apenas para persistência do Camunda BPM (schema `flexgeracaocontrato`).

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| N/A | N/A | N/A | Sistema não atualiza banco de dados diretamente. Todas as escritas são realizadas via APIs REST/SOAP de sistemas legados. |

**Observação**: Redis é usado para controle de estado do listener JMS (variável de bloqueio/liberação).

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `email-template.html` | Leitura | `EmailConfiguration` (ClassPath) | Template HTML para envio de emails de notificação de erro |
| `GeracaoContratoMensagem.xsd` | Leitura | JAXB (compilação) | Schema XML para validação de mensagens JMS |
| Logs JSON | Gravação | Logback (stdout) | Logs estruturados em formato JSON |

---

## 10. Filas Lidas

| Nome da Fila | Tecnologia | Classe Responsável | Descrição |
|--------------|-----------|-------------------|-----------|
| `QL.FLEX.GERAR_CONTRATO_MENSAGEM.INT` | IBM MQ JMS | `ManipulaGeracaoContratoListener` | Fila de entrada para mensagens XML de solicitação de geração de contratos |

**Observação**: Nome da fila configurável via `${flex.inbv.jms.queue-name}`. Listener controlado por Redis (circuit breaker).

---

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Responsável | Descrição |
|--------------|-----------|-------------------|-----------|
| `QL.FLEX.GERAR_CONTRATO_MENSAGEM_BPEL.INT` | IBM MQ JMS | `GeracaoContratoJmsSenderImpl` | Fila de saída para sistema legado BPEL (quando piloto desabilitado) |
| Filas de callback Camunda | IBM MQ JMS | `GeracaoContratoProcessFlow` | Mensagens de correlação para processos Camunda (callback pré/pós-contrato) |

---

## 12. Integrações Externas

**SOAP (20+ endpoints)**:
- `ManutencaoContratoFinanceiroFlexIntegrationService`: Inserir contrato/desembolso, alterar pagamento, validar/completar dados, informar retorno geração
- `ManutencaoContratoFinanceiroBackendService`: Validar/completar dados contrato, converter custos
- `ClienteFlexBusinessService`: Manter/consultar cliente FlexCube (PF/PJ), endereços, telefones
- `CalcularDataVencimentoVarejoBusinessService`: Calcular data 1º vencimento
- `TaxaFinanciamentoFlexBusinessService`: Listar taxas financiamento, criar contrato controladoria
- `TributoBusinessService`: Listar alíquotas tributos
- `HierarquiaComercialBusinessService`: Obter hierarquia comercial
- `FilialContabilBusinessService`: Buscar filial contábil por parceiro
- `LiberarComissaoParceiroFinanciamentoBusinessService`: Incluir pagamento comissão
- `SolicitarPagamentoBusinessService`: Incluir pagamento
- `PendenciaFormalizacaoContratoBusinessService`: Incluir pendência formalização
- `OriginacaoCardifBusinessService`: Enviar originação seguro Cardif
- `MapeamentoDominiosTechinicalService`: Obter/listar domínios mapeamento

**REST (30+ endpoints)**:
- `sboot-flex-inbv-orch-cliente-flex`: Manter/consultar cliente
- `sboot-flex-inbv-orch-contrato-financeiro-flex`: Consultar contratos/liberação
- `sboot-dcor-base-acl-taxa-financiamento-flex`: Listar taxas financiamento
- `sboot-calc-base-atom-calculo-fluxo-irregular`: Cálculo taxas/valores fluxos irregulares (FGTS)
- `sboot-gger-base-atom-controladoria-carga`: Criar contrato controladoria
- `sboot-pseg-base-orch-originacao-cardif` e `-seguros`: Enviar contratos seguradoras
- `sboot-pagm-base-orch-processar-pagamento`: Incluir pagamento (v1/v2)
- `sboot-sgcm-base-orch-entrada-comissao`: Entrada comissões
- `sboot-apro-base-acl-func-piloto-cmrcl-varejo`: Verificar produto piloto habilitado
- `sboot-apro-fgts-atom-fluxo-proposta-saque-aniversario`: Salvar/atualizar/consultar proposta FGTS
- `sboot-flex-inbv-orch-atualiza-dado-cliente`: Atualizar dados cliente
- `caapi-gnms-base-envio-email`: Enviar emails notificação erro

**Outros**:
- **Redis**: Controle de estado listener JMS (bloqueio/liberação)
- **Camunda BPM**: Orquestração workflow BPMN (`esteira_implantacao_contratos.bpmn`)

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões hexagonais (ports/adapters)
- Separação clara de responsabilidades (delegates, services, mappers, repositories)
- Uso adequado de MapStruct para mapeamento type-safe entre domínios
- Tratamento robusto de exceções com hierarquia customizada (BusinessException)
- Configuração externalizada e organizada (ApplicationProperties, profiles)
- Observabilidade completa (métricas Micrometer, health checks, logs estruturados JSON)
- Cobertura extensa de testes unitários com mocks bem estruturados
- Uso de padrões de projeto (Factory, Strategy, Template Method)
- Documentação técnica presente (README, comentários XML)
- Circuit breaker implementado para controle de listener JMS

**Pontos de Melhoria:**
- Presença de código deprecated (OriginacaoCardifBusinessServiceMapper, PagamentoDesembolsoClient) indica refatoração incompleta
- Comentários XML muito extensos em alguns arquivos (poluição visual)
- Falta de testes de integração evidentes (apenas unitários)
- Complexidade alta em alguns delegates (CriarContratoDelegate com múltiplas responsabilidades)
- Acoplamento com sistemas legados via SOAP (dificulta manutenção)
- Falta de documentação de APIs (Swagger/OpenAPI) para endpoints REST expostos

---

## 14. Observações Relevantes

1. **Workflow Camunda Complexo**: Processo BPMN com execução paralela de etapas pré/pós-contrato, gateways para fluxos irregulares, seguros, comissões e boletos. Uso de message correlation para callbacks.

2. **Circuit Breaker Operacional**: Scheduler monitora Redis para controlar listener JMS, permitindo bloqueio/liberação via API REST para manutenções ou sobrecarga.

3. **Suporte Multi-Produto**: Sistema suporta múltiplos produtos financeiros (FGTS, solar, estudantil, etc) com fluxos específicos configurados via piloto de funcionalidade.

4. **Integração Legado BPEL**: Mantém compatibilidade com sistema legado via piloto funcionalidade, encaminhando mensagens para fila BPEL quando produto não habilitado na nova esteira.

5. **Listeners de Métricas**: Execution/TaskListeners Camunda registram eventos para métricas (sumário valor contratos, bloqueios, devoluções).

6. **Configuração Extensiva**: Properties complexas (EsteiraImplantacaoDominioProperties, ProcessFlowProperties) com configurações específicas por domínio/filial.

7. **Geração Automática de Clients**: Uso de Swagger Codegen e OpenAPI Generator para gerar clients REST a partir de especificações, reduzindo código boilerplate.

8. **Multi-Ambiente**: Suporte completo para ambientes DES/QA/UAT/PRD com configurações específicas via profiles Spring.

9. **Segurança**: Implementação OAuth2 Client Credentials para autenticação em APIs externas, JWT para endpoints internos.

10. **Infraestrutura Kubernetes**: Deployment GKE com configuração de recursos (CPU/memória), probes (liveness/readiness), secrets e volumes.

11. **Domínio Rico**: Modelo de domínio complexo com entidades financeiras detalhadas seguindo princípios DDD (Value Objects, Aggregates).

12. **Tratamento de Retries**: Gerenciamento inteligente de retries Camunda com lançamento de BpmnError quando esgotados, evitando loops infinitos.