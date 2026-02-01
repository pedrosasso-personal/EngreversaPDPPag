# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de gestão operacional PIX desenvolvido em Angular para administração de transações instantâneas, participantes, chaves DICT, antifraude, conciliação, relatórios regulatórios e mecanismos especiais (MED, FRV, PIX Automático). Atende regulamentação BACEN e integra-se ao SPI (Sistema de Pagamentos Instantâneos).

---

## 2. Principais Classes e Responsabilidades

| Classe/Componente | Responsabilidade |
|-------------------|------------------|
| **AgentWithdrawComponent** | Gestão agentes saque (listagem, filtros, export CSV) |
| **AgentDetailComponent** | Cadastro/edição agentes (dados gerais, contratos, faixas valores) |
| **AgentWithdrawTransferComponent** | Gestão repasses agentes (aprovação, rejeição, recálculo, pagamento) |
| **AntifraudTableComponent** | Visualização/gerenciamento regras antifraude (frequência, limite horário) |
| **AutoDisapprovalComponent** | Configuração reprovação automática e calendário feriados |
| **AntifraudClientsComponent** | Gestão exceções clientes (whitelist CPF/CNPJ) |
| **BatchConciliationComponent** | Reprocessamento lote transações PIX por protocolo |
| **ConciliationComponent** | Painel conciliação operacional/financeira (Core vs Contábil) |
| **DashboardMedComponent** | Dashboard prazos MED (relatos infração, devoluções especiais) |
| **DetalheTributosComponent** | Detalhes pagamentos/recebimentos (TED, TEF, Tributos, Boletos) |
| **DictClaimsComponent** | Gerência reivindicações chaves DICT (portabilidade, posse) |
| **DictContingencyActionsComponent** | Importação relatórios contingência DICT |
| **DictDashboardComponent** | Dashboard métricas operacionais DICT |
| **DictKeysComponent** | Gerenciamento chaves PIX (listagem, exclusão, cadastro) |
| **DictKeysDetailComponent** | Detalhamento chave PIX (histórico, bloqueio judicial) |
| **FraudTaggingComponent** | Marcação/gerenciamento fraude PIX |
| **FormIndirectComponent** | Gestão participantes indiretos (registro SPI, circuit breaker) |
| **GeradorArquivoComponent** | Geração arquivos regulatórios (IN32) |
| **IgaImportComponent** | Importação métricas IGA/IGAT via CSV |
| **InfoPanelComponent** | Relatórios IN200 (saques/trocos fora SPI) |
| **KeyConciliationComponent** | Conciliação chaves DICT (gestão parceiros) |
| **ManagementPiComponent** | Gestão responsáveis PI (REDA022) |
| **ManualConciliationComponent** | Conciliação manual transações PIX |
| **MessageSendingComponent** | Envio manual mensagens PACS008/004 |
| **PacTableComponent** | Histórico mensagens PACS (filtros, paginação) |
| **PacDetailComponent** | Detalhe transação PACS (timeline, reenvio notificação) |
| **AntifraudComponent** | Análise manual antifraude (timer, liberação/bloqueio) |
| **PartnerManagementComponent** | Manutenção parceiros indiretos (ativação BACEN via REDA) |
| **PartnerRegistrationComponent** | Cadastro/edição parceiros PIX (DIRETO/INDIRETO/CASH_PURO) |
| **PixAuthorizationComponent** | Consulta autorizações PIX Automático (recorrências) |
| **PixAuthorizationDetailComponent** | Detalhe autorização PIX Automático (agendamentos, histórico) |
| **PixOperacionalFailuresComponent** | Lista falhas operacionais PIX Automático |
| **PixOperationalFailureDetailComponent** | Detalhe falha operacional (aprovação/rejeição ressarcimento) |
| **PreReportComponent** | Gestão pré-relatos MED (contestação PIX) |
| **CreateRecoveryValuesComponent** | Criação FRV (Funds Recovery Values) |
| **DetailsRecoveryValuesComponent** | Consulta/detalhe FRV (cancelamento) |
| **RenotificationComponent** | Reenvio notificações falhas sistema PIX |
| **BucketComponent** | Monitoramento baldes fichas (rate limiting) |
| **InternalChannelComponent** | Cadastro/edição canais internos (webhooks) |

---

## 3. Tecnologias Utilizadas

- **Frontend**: Angular 7+, TypeScript, RxJS
- **UI**: Angular Material Design, Saturn Datepicker, ngx-mat-select-search
- **Máscaras**: TextMask, CurrencyMask
- **Testes**: Jasmine, Karma, Jest, ng-bullet
- **Sanitização**: DOMPurify
- **Datas**: moment-timezone
- **HTTP**: HttpClient, Interceptors (Universal SSR)
- **Autenticação**: JWT (BvRolesService)
- **Storage**: LocalStorage (ISPB, user, token)
- **Build**: Node.js, json-server (mocks)
- **SSR**: Angular Universal
- **Integração**: APIs REST (JSON), WebSockets (notificações)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/agente-saque/listar` | AgentWithdrawService | Lista agentes saque c/ filtros |
| POST | `/v1/agente-saque` | AgentWithdrawService | Cadastra agente saque |
| PUT | `/v1/agente-saque/{id}` | AgentWithdrawService | Atualiza agente saque |
| POST | `/v1/historico/repasses` | AgentWithdrawTransferService | Lista repasses agentes |
| POST | `/v1/agente-saque/repasse` | AgentWithdrawTransferService | Aprova/rejeita repasse |
| GET | `/gestao-fintech/anti-fraud/pagamento/horarioComParametros` | AntifraudHistoryService | Lista limites horário antifraude |
| POST | `/gestao-fintech/anti-fraud/pagamento/horario` | AntifraudHistoryService | Cadastra limite horário |
| POST | `/v1/batch-conciliation` | BatchConciliationService | Reprocessa lote protocolos |
| GET | `/gestao-spi/consultaMovimentacoesCoreContabil` | ConciliationService | Conciliação Core vs Contábil |
| GET | `/dashbord/totalizadores-med` | DashboardMedService | Totalizadores MED |
| POST | `/fraude/relatos/listar` | DashboardMedService | Lista relatos infração |
| POST | `/v1/devolucao-especial/listar` | DashboardMedService | Lista devoluções especiais |
| POST | `/dict/listaReivindicacoesDict` | DictClaimsService | Lista reivindicações DICT |
| POST | `/v2/contingencies/import/infraction-report` | DictContingencyActionsService | Importa relatório infração |
| GET | `/dict/listarMetricasTempo` | DictDashboardService | Métricas tempo DICT |
| POST | `/dict/listaChavesDict` | DictKeysService | Lista chaves PIX |
| DELETE | `/v1/entries/{chave}` | DictKeysService | Exclui chave PIX |
| POST | `/v1/entries` | DictKeysService | Cadastra chave PIX |
| GET | `/dict/{id}` | DictKeysService | Detalhes chave PIX |
| PATCH | `/v1/entries/{key}/judicial` | DictKeysService | Bloqueio judicial chave |
| POST | `/fraud-marker` | FraudTaggingService | Marca fraude PIX |
| GET | `/fraud-markers` | FraudTaggingService | Lista marcações fraude |
| POST | `/gestao-fintech/incluirParceiroSpi` | FormIndirectService | Registra parceiro SPI |
| POST | `/v1/report-request` | GeradorArquivoService | Solicita arquivo IN32 |
| POST | `/v1/metrics-igat` | IgaImportService | Upload CSV métricas IGAT |
| POST | `/v1/reports/in-200` | InfoPanelService | Gera relatório IN200 |
| GET | `/conciliation-dict/active-partners` | KeyConciliationService | Parceiros ativos conciliação |
| POST | `/gestao-fintech/envia-mensagem-reda22` | ManagementPiService | Envia REDA022 |
| POST | `/v1/manual-conciliation/list` | ManualConciliationService | Lista transações conciliação manual |
| PUT | `/v1/manual-conciliation/finalize/{id}` | ManualConciliationService | Finaliza conciliação |
| POST | `/gestao-fintech/manual-send` | ManualHistoryService | Envia mensagem PACS manual |
| GET | `/gestao-fintech/findMessageHistory` | MessageHistoryService | Histórico mensagens REDA |
| GET | `/gestao-fintech/findMessages` | PacHistoryService | Busca mensagens PACS |
| GET | `/gestao-fintech/message-detail/{code}` | PacHistoryService | Detalhe mensagem PACS |
| POST | `/gestao-fintech/reenvio-notificacao` | PacHistoryService | Reenvia notificação |
| GET | `/gestao-fintech/roles-antifraude` | PacHistoryService | Regras antifraude |
| PUT | `/gestao-fintech/liberar-envio` | PacHistoryService | Libera transação antifraude |
| GET | `/v1/parceiros` | PartnerService | Lista parceiros PIX |
| POST | `/v1/parceiros` | PartnerService | Cadastra parceiro |
| POST | `/v1/parceiros/indiretos/reda` | PartnerService | Ativa/desativa parceiro BACEN |
| GET | `/v1/pix-automatic/authorization` | PixAutomaticService | Lista autorizações PIX Auto |
| GET | `/v1/pix-automatic/authorization/{id}` | PixAutomaticService | Detalhe autorização |
| PUT | `/v1/pix-automatic/authorization/cancel` | PixAutomaticService | Cancela autorização |
| GET | `/v1/med/pix-automatic/refunds` | PixOperacionalFailuresService | Lista falhas operacionais |
| GET | `/v1/med/pix-automatic/refunds/{id}` | PixAutomaticService | Detalhe falha operacional |
| PATCH | `/v1/med/pix-automatic/refunds/{id}` | PixAutomaticService | Aprova/rejeita ressarcimento |
| POST | `/contestacao/listar` | PreReportService | Lista pré-relatos |
| POST | `/contestacao/salvar` | PreReportService | Cria pré-relato |
| PUT | `/contestacao/update` | PreReportService | Aceita/rejeita pré-relato |
| POST | `/v1/manual-pacs-message` | RecoveryValuesService | Cria FRV |
| GET | `/v1/notifications` | RenotificationService | Lista notificações falhas |
| POST | `/v1/notifications/retry` | RenotificationService | Reenvia notificações |

---

## 5. Principais Regras de Negócio

- **Agentes Saque**: Validação relação PSS/FSS (interno/parceiro), cálculo valor contrato por % RCO, agendamento alteração faixas dia 1 do mês
- **Antifraude**: Configuração frequência/limite horário, whitelist clientes, análise manual c/ timer, reprovação automática por janela horária
- **Conciliação**: Comparação Core vs Contábil por messageType/flow/settlement, marcação divergências, conciliação manual c/ validação horário motor (2h)
- **DICT**: Bloqueio judicial chaves (perfil específico), reivindicações portabilidade/posse, exclusão chaves (motivos regulatórios), validação chave bloqueada impede transações
- **MED**: Prazos relatos infração/devoluções especiais, classificação vencimento (ON_TIME/ABOUT_TO_EXPIRE/EXPIRING/EXPIRED)
- **Participantes**: Registro SPI via REDA014/031, circuit breaker (CASH-IN/OUT, DICT), validação CNPJ Global, webhooks notificação por tipo parceiro
- **PIX Automático**: Autorização recorrências, agendamentos, cancelamento (validações D+0 SLBD), retry policy, falhas operacionais c/ ressarcimento (aprovação dual)
- **Fraude**: Marcação tipos (APPLICATION_FRAUD, MULE_ACCOUNT, SCAMMER_ACCOUNT), validação CPF/CNPJ, status REGISTERED/CANCELLED
- **Mensagens Manuais**: PACS008/004 c/ aprovação dupla (solicitante≠aprovador), validação chave DICT bloqueada, finalidades IPAY/GSCB/OTHR
- **FRV**: Validação acesso perfil CPIX_OPERACIONAL_TRANSACIONAL, cancelamento por status (CREATED/TRACKED/AWAITING_ANALYSIS/ANALYSED)
- **Pré-Relatos**: Tipos contestação (FRAUD/REFUND_REQUEST/OPERATIONAL_FLAW/NOT_FRAUD), status interno (CRIADO/ACEITO/REJEITADO), validação ID transação padrão BACEN
- **Renotificação**: Tipos notificação (PIX_NOTIFICATION_CREATE_CLAIM, UPDATE_CLAIM, CREATE/UPDATE_INFRACTION_V2, etc), seleção múltipla, reenvio assíncrono (até 30min)
- **Validações Gerais**: Período máximo consultas (30-31 dias), máscaras CPF/CNPJ/telefone, formatação moeda, validação campos obrigatórios contextuais, paginação customizada (20-500 itens)

---

## 6. Relação entre Entidades

- **AgentWithdraw** 1:N **AgentContract** (agente possui múltiplos contratos históricos)
- **AgentContract** 1:N **AgentAmountRange** (contrato possui faixas valores)
- **AgentWithdraw** 1:N **AgentServicePoint** (agente possui pontos atendimento)
- **AgentServicePoint** 1:N **AgentOpeningHour** (ponto possui horários funcionamento)
- **Partner** 1:N **InternalChannel** (parceiro possui canais internos)
- **InternalChannel** 1:N **Account** (canal possui contas)
- **Account** 1:N **Webhook** (conta possui webhooks notificação)
- **DictEntry** 1:N **DictEntryHistory** (chave possui histórico mudanças)
- **PixAutomaticAuthorization** 1:N **Schedule** (autorização possui agendamentos)
- **PixAutomaticAuthorization** 1:N **HistoryAuth** (autorização possui histórico atualizações)
- **Schedule** 1:N **HistoryPayment** (agendamento possui histórico pagamentos)
- **OperationalFailure** 1:1 **MedPixAutomaticAuthorization** (falha vinculada a autorização)
- **OperationalFailure** 1:N **RefundHistory** (falha possui histórico devolução)
- **PreReport** 1:1 **PACS008** (pré-relato vinculado a pagamento original)
- **PreReport** 0:1 **PACS004** (pré-relato pode ter devolução)
- **FundsRecovery** 1:N **InfractionReport** (FRV possui notificações infração)
- **FundsRecovery** 1:N **SpecialRefund** (FRV possui devoluções especiais)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| agentWithdrawList | view | SELECT | Lista agentes saque c/ filtros |
| agentContractList | view | SELECT | Histórico contratos agentes |
| agentAmountRangeList | view | SELECT | Faixas valores contratos |
| agent_service_point | tabela | SELECT | Pontos atendimento agentes |
| agent_opening_hour | tabela | SELECT | Horários funcionamento pontos |
| antifraud_rules | tabela | SELECT | Regras antifraude (frequência, horário) |
| whitelist_client | tabela | SELECT | Exceções clientes antifraude |
| historico_repasses | tabela | SELECT | Histórico repasses agentes |
| entries | tabela | SELECT | Chaves PIX DICT |
| entries_history | tabela | SELECT | Histórico mudanças chaves |
| fraud_markers | tabela | SELECT | Marcações fraude PIX |
| parceiros_internos | tabela | SELECT | Participantes PIX |
| circuit_break | tabela | SELECT | Configurações circuit breaker |
| report_indicator_months | tabela | SELECT | Métricas IGA/IGAT |
| metricasTempo | view | SELECT | Métricas tempo DICT |
| consultasDict | view | SELECT | Consultas DICT |
| cadastroExclusao | view | SELECT | Cadastros/exclusões DICT |
| reivindicacoes | view | SELECT | Reivindicações DICT |
| mensagens_pacs | tabela | SELECT | Histórico mensagens PACS008/004 |
| notificacoes | tabela | SELECT | Notificações parceiros |
| transacoes_conciliacao | tabela | SELECT | Transações conciliação manual |
| movimentacoes_cc | tabela | SELECT | Movimentações conta corrente |
| lancamentos_contabeis | tabela | SELECT | Lançamentos contábeis |
| pix_automatic_authorization | tabela | SELECT | Autorizações PIX Automático |
| pix_automatic_schedule | tabela | SELECT | Agendamentos PIX Automático |
| pix_automatic_history_auth | tabela | SELECT | Histórico autorizações |
| pix_automatic_history_payment | tabela | SELECT | Histórico pagamentos |
| operational_failure | tabela | SELECT | Falhas operacionais PIX Auto |
| refund_history | tabela | SELECT | Histórico devoluções |
| pre_relatos | tabela | SELECT | Pré-relatos MED |
| funds_recovery | tabela | SELECT | FRV (Funds Recovery Values) |
| infraction_reports | tabela | SELECT | Notificações infração |
| special_refunds | tabela | SELECT | Devoluções especiais |
| canais_internos | tabela | SELECT | Canais internos webhooks |
| webhooks_notificacao | tabela | SELECT | Webhooks notificação |
| bucket_tokens | tabela | SELECT | Baldes fichas rate limiting |
| holiday | tabela | SELECT | Calendário feriados |
| parameter_time | tabela | SELECT | Janelas reprovação automática |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| agente_saque | tabela | INSERT/UPDATE/DELETE | CRUD agentes saque |
| agent_contract | tabela | INSERT/UPDATE | CRUD contratos agentes |
| agent_amount_range | tabela | INSERT/UPDATE/DELETE | CRUD faixas valores |
| agent_service_point | tabela | INSERT/UPDATE/DELETE | CRUD pontos atendimento |
| agent_opening_hour | tabela | INSERT/UPDATE/DELETE | CRUD horários funcionamento |
| historico_repasses | tabela | UPDATE | Atualiza status repasses (aprovado, rejeitado, pago) |
| antifraud_rules | tabela | INSERT/UPDATE/DELETE | CRUD regras antifraude |
| whitelist_client | tabela | INSERT/DELETE | CRUD exceções clientes |
| entries | tabela | INSERT/UPDATE/DELETE | CRUD chaves PIX (flJudBloq) |
| fraud_markers | tabela | INSERT/UPDATE | CRUD marcações fraude |
| parceiros_internos | tabela | INSERT/UPDATE | CRUD participantes PIX |
| circuit_break | tabela | UPDATE | Atualiza flags circuit breaker |
| report_indicator_months | tabela | INSERT | Importação métricas IGA |
| mensagens_manuais | tabela | INSERT/UPDATE | Controle mensagens PACS manuais |
| transacoes_conciliacao | tabela | UPDATE | Atualiza status conciliação |
| movimentacoes_cc | tabela | INSERT | Lançamentos conta corrente |
| lancamentos_contabeis | tabela | INSERT | Lançamentos contábeis |
| notificacoes | tabela | INSERT/UPDATE | Controle notificações parceiros |
| pix_automatic_authorization | tabela | UPDATE | Cancela autorizações PIX Auto |
| pix_automatic_schedule | tabela | UPDATE | Cancela agendamentos |
| operational_failure | tabela | UPDATE | Aprova/rejeita ressarcimento |
| pre_relatos | tabela | INSERT/UPDATE | CRUD pré-relatos MED |
| funds_recovery | tabela | INSERT/UPDATE | CRUD FRV |
| canais_internos | tabela | INSERT/UPDATE | CRUD canais internos |
| webhooks_notificacao | tabela | INSERT/UPDATE | CRUD webhooks |
| holiday | tabela | INSERT/UPDATE | CRUD calendário feriados |
| parameter_time | tabela | INSERT/UPDATE/DELETE | CRUD janelas reprovação |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| CSV métricas IGA/IGAT | leitura | IgaImportComponent | Importação métricas indicadores gestão |
| IN32.xml | gravação | GeradorArquivoComponent | Arquivo regulatório BACEN (base64) |
| IN200.xlsx | gravação | InfoPanelComponent | Relatório saques/trocos fora SPI |
| CSV exportação | gravação | Múltiplos componentes | Export dados tabelas (agentes, transações, históricos) |
| PDF comprovante | gravação | PixAuthorizationDetailComponent, MessageSendingV2Component | Comprovantes autorizações/pagamentos PIX |
| mocks/data.json | leitura | json-server | Dados mock desenvolvimento |
| routes.json | leitura | json-server | Rotas mock desenvolvimento |

---

## 10. Filas Lidas

**não se aplica** (sistema não consome filas diretamente, recebe notificações via webhooks HTTP)

---

## 11. Filas Geradas

| Nome da Fila | Tipo | Descrição |
|--------------|------|-----------|
| Mensagens PACS p/ SPI | Fila interna | Envio mensagens PACS008/004 manuais para processamento SPI |
| Notificações parceiros | Fila interna | Reenvio notificações falhas (webhooks assíncronos) |

---

## 12. Integrações Externas

| Sistema Externo | Tipo Integração | Descrição |
|-----------------|-----------------|-----------|
| **SPI (Sistema Pagamentos Instantâneos)** | API REST | Envio/recebimento mensagens PACS, REDA, consultas DICT |
| **BACEN (Banco Central)** | API REST | Ativação participantes (REDA014/031), consultas regulatórias |
| **DICT (Diretório Identificadores)** | API REST | CRUD chaves PIX, consultas, reivindicações |
| **Global (Sistema Cadastro)** | API REST | Validação CNPJ clientes |
| **Sistema Contábil** | API REST | Lançamentos contábeis, conciliação |
| **Sistema Conta Corrente** | API REST | Movimentações CC, bloqueio/desbloqueio saldo |
| **PowerBI** | Redirect URL | Dashboards métricas IGA/IGAT |
| **Webhooks Parceiros** | HTTP POST | Notificações eventos PIX (pagamentos, devoluções, infrações) |
| **Sistema Antifraude BV** | API REST | Análise manual transações, regras frequência/horário |
| **APIs gestao-fintech** | API REST | Múltiplas operações (histórico PACS, mensagens manuais, parceiros, etc) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Componentização adequada seguindo padrões Angular
- Tipagem TypeScript forte (interfaces, enums)
- Separação responsabilidades (components, services, models)
- Validações formulários reativos
- Sanitização inputs (DOMPurify)
- Testes unitários presentes (>80% coverage indicado)
- Uso de pipes customizados (máscaras, formatação)
- Tratamento erros com feedback usuário (AlertaService)
- Controle acesso por perfis (BvRolesService)
- Lazy loading módulos

**Pontos de Atenção:**
- **Complexidade ciclomática alta**: Métodos extensos (>100 linhas) em componentes como `ManualConciliationComponent`, `PacTableComponent`, `DetalheTributosComponent`
- **Lógica negócio em componentes**: Deveria estar em services (ex: validações, cálculos, formatações)
- **Timeouts hardcoded**: Valores mágicos (5s, 25min) sem constantes
- **Strings mágicas**: URLs, mensagens, status sem enums/constantes
- **Código morto comentado**: Testes E2E comentados (`cadastro.e2e-spec1.ts`, `login.e2e-spec.ts`)
- **Tratamento erros genérico**: Falta especificidade em alguns catches
- **Memory leaks potenciais**: Timers não destruídos em `ngOnDestroy` (ex: `AntifraudComponent`)
- **Duplicação código**: Lógica similar em múltiplos componentes (filtros, paginação, export CSV)
- **Falta documentação**: JSDoc ausente em métodos complexos
- **Acoplamento**: Dependência direta de múltiplos services em componentes

**Recomendações:**
1. Refatorar métodos grandes em funções menores
2. Extrair lógica negócio para services/utils
3. Criar constantes para timeouts, URLs, mensagens
4. Implementar unsubscribe automático (takeUntil pattern)
5. Adicionar JSDoc em métodos públicos
6. Criar componentes reutilizáveis (filtros, tabelas, modais)
7. Implementar error handling strategy centralizada
8. Remover código comentado
9. Adicionar testes E2E funcionais

---

## 14. Observações Relevantes

- **Arquitetura**: SPA Angular com SSR (Universal), modular por features
- **Autenticação**: JWT armazenado em LocalStorage, interceptor adiciona token em requests
- **Multi-tenancy**: Suporte múltiplos ISPBs (bancos) via seleção dinâmica
- **LGPD**: Base64 encoding dados sensíveis (CPF, CNPJ, contas) em requests
- **Regulatório**: Forte aderência regulamentação BACEN (prazos MED, formatos mensagens, validações)
- **Responsividade**: Material Design responsivo, suporte fullscreen
- **Acessibilidade**: Uso adequado ARIA labels, navegação teclado
- **Performance**: Lazy loading, paginação server-side, debounce em filtros
- **Segurança**: Sanitização XSS, validação client/server-side, controle acesso por perfis
- **Manutenibilidade**: Estrutura modular facilita evolução, mas necessita refatoração componentes grandes
- **Observabilidade**: Logs em console (dev), integração com sistema alertas (AlertaService)
- **Ambiente**: Suporte UAT/PRD com configs específicas (URLs PowerBI, endpoints)
- **Versionamento**: Código sugere múltiplas versões componentes (v1, v2) indicando evolução incremental