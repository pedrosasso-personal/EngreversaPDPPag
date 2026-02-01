# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **springboot-spbb-base-ispb-bff** é um **Backend For Frontend (BFF)** desenvolvido em Java 11 com Spring Boot, que atua como camada intermediária de integração para o **Sistema de Pagamentos Brasileiro (SPB)** da Votorantim. 

Sua finalidade é orquestrar e consolidar chamadas a múltiplos microsserviços especializados (Mensageria, Cadastros, Operações, Lote, Piloto Reserva, Calendário, Contingência), expondo APIs REST simplificadas para consumo por frontends. O sistema gerencia operações financeiras complexas do ISPB (Identificador do Sistema de Pagamentos Brasileiro), incluindo:

- Movimentações bancárias (STR, TES, SELIC, Câmaras diversas)
- Cadastros operacionais (instituições, usuários, alcadas, perfis)
- Piloto de reservas bancárias e controle de liquidez
- Processamento de lotes e mensagens duplicadas
- Geração de relatórios Excel (extratos, conciliações, interface contábil)
- Gestão de contingências (circuit breaker, feature toggles)

O sistema integra-se com APIs externas via OAuth2, processa mensagens padronizadas do Banco Central (BACEN) em diversos formatos (BMA, BMC, BMD, CAM, CCR, CIR, DDA, LDL, LEI, LTR, PAG, RCO, SEL, STR, etc), e implementa regras de negócio específicas do mercado financeiro brasileiro.

---

## 2. Principais Classes e Responsabilidades

| Classe/Pacote | Responsabilidade |
|---------------|------------------|
| **ExcelService** | Geração de arquivos Excel para movimentos ISPB (entrada/saída, RCO0006, formatação financeira) |
| **AlcadaOperacionalService/Impl** | CRUD de alçadas operacionais via API externa |
| **AltrAlcadaTransacaoService/Impl** | CRUD de alçadas de transação |
| **BatimentoMensagemService/Impl** | Batimento de mensagens, atualização de movimentos (30+ tipos), geração de número de controle |
| **CadastroMensagemService/Impl** | Cadastro de mensagens, inserção/atualização de movimentos diversos grupos (MCA, MCL, MCS, etc), geração de número de controle, validações de lock/alteração |
| **MensagemDuplicadaService/Impl** | Gestão de mensagens duplicadas, geração de Excel RCO, tratamento específico RCO0006 |
| **ModuloCamaraService/Impl** | Consultas piloto de múltiplas câmaras (BMA, BMC, BMD, CBL, CMP, CTP, LDL, LTR, PAG), verificação de ciclos, atualização de status |
| **ModuloOperacionalService/Impl** | Consultas de movimentos operacionais (50+ tipos), paginação, enriquecimento de dados |
| **PilotoReservaService/Impl** | Gestão de piloto de reservas bancárias, circuit breaker, validação de alertas, controle de montantes STR/PAG |
| **ConsultaReservaService/Impl** | Consulta de valores de reserva, atualização de movimentos, verificação de ciclos |
| **InterfaceContabilService/Impl** | Interface contábil, geração de Excel formato legado |
| **RelatorioAnaliticoReservaService/Impl** | Relatório analítico de reserva, geração de Excel extrato |
| **StrEnviadaService/Impl** | Geração de Excel de quantidade STR enviadas por período (validação máx 90 dias) |
| **ManualOperacoesService/Impl** | Geração de Excel com layouts de mensagens Bacen |
| **CircuitBreakService** | Gestão de circuit breaker para contingência |
| **FeatureToggleService** | Consulta de feature toggles |
| **LoteService/Impl** | Gestão de lotes, número de controle, contingência |
| **CalendarioService** | Consulta de dias úteis em calendário |
| **NSUService** | Geração de NSU (Número Sequencial Único) |
| **PopupServicosService/Impl** | Operações popup (mensagens SPB), execução de procedures BD |
| **MovimentoService** | Consulta de movimentos paginados, fluxo de movimento, erros |
| **AppConfiguration** | Configuração de beans OAuth2RestTemplate para microsserviços |
| **ExcelDtoMapper** | Mapeamento de movimentos para ExcelDto (MapStruct) |
| **CircuitBreakMapper** | Mapeamento de domains circuit break (MapStruct) |
| **MovimentoMapper** | Mapeamento de consulta movimento/fluxo/erros (MapStruct) |
| **Domain (DTOs)** | 200+ DTOs para transporte de dados de mensagens SPB/Bacen (BMA, BMC, BMD, CAM, CCR, CIR, DDA, LDL, LEI, LTR, PAG, RCO, SEL, STR, TES, etc) |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot** (Framework principal)
- **Spring Security** (Autenticação/Autorização via @Secured)
- **OAuth2** (OAuth2RestTemplate para integração com microsserviços)
- **Apache POI** (Geração de arquivos Excel XLSX)
- **Jackson** (Serialização/Deserialização JSON)
- **Lombok** (Redução de boilerplate)
- **MapStruct** (Mapeamento de DTOs)
- **Swagger/OpenAPI** (Documentação de APIs)
- **Logback** (Logs em formato JSON, níveis WARN/INFO)
- **Docker** (Containerização - Dockerfile com base Java 11)
- **Kubernetes** (Configuração infra multi-ambiente: des/uat/prd)
- **RestTemplate** (Chamadas HTTP síncronas)
- **BigDecimal** (Precisão financeira)
- **LocalDate/LocalDateTime** (Manipulação de datas)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET/PUT/DELETE | `/v1/dbispb/cadastros/alcada-operacional` | AlcadaOperacionalService | CRUD de alçadas operacionais |
| GET/POST/PUT/DELETE | `/v1/dbispb/cadastros/alcada-transacao` | AltrAlcadaTransacaoService | CRUD de alçadas de transação |
| GET/POST/PUT/DELETE | `/v1/dbispb/cadastros/alcada` | AlcadaService | CRUD de alçadas |
| GET | `/v1/dbispb/cadastros/aviso/{date}` | AvisoService | Lista mensagens de avisos por data |
| GET/POST/DELETE | `/v1/dbispb/cadastros/cliente-operacao` | ClienteOperacaoService | Gestão cliente-operação |
| GET | `/v1/dbispb/cadastros/consulta-erros/{dataDe}/{dataAte}` | ConsultaErrosService | Consulta erros de mensagens por período |
| GET | `/v1/dbispb/cadastros/consulta-prev-provisao` | ConsultaPrevProvisaoService | Consulta previsão provisão |
| GET | `/v1/dbispb/cadastros/controle-pendencias` | ControlePendenciasService | Controle de pendências |
| GET/POST/PUT/DELETE | `/v1/dbispb/cadastros/grupo-servico` | GrupoServicoService | CRUD de grupo serviço |
| GET/POST/PUT/DELETE | `/v1/dbispb/cadastros/holding` | HoldingService | CRUD de holdings |
| GET/POST/PUT/DELETE | `/v1/dbispb/cadastros/instituicao-financeira` | InstituicaoFinanceiraService | CRUD de instituições financeiras |
| GET/POST/PUT/DELETE | `/v1/dbispb/cadastros/instituicao-mercado` | InstituicaoMercadoService | CRUD de instituições de mercado |
| GET/POST | `/v1/dbispb/cadastros/interface-contabil` | InterfaceContabilService | Interface contábil, gera Excel |
| GET/PUT | `/v1/dbispb/cadastros/login-usuario` | LoginUsuarioService | Dados login usuário, alçadas, perfis, holdings |
| GET/POST/PUT/DELETE | `/v1/dbispb/cadastros/operacoes` | OperacaoService | CRUD de operações |
| GET/PUT | `/v1/dbispb/cadastros/parametros-controle-envio` | ParametroControleEnvioService | Parâmetros controle envio |
| GET/PUT | `/v1/dbispb/cadastros/participante` | ParticipanteService | Lista e atualiza participantes |
| GET/POST/PUT/DELETE | `/v1/dbispb/cadastros/perfil` | PerfilService | CRUD de perfis |
| GET/POST/DELETE | `/v1/dbispb/cadastros/perfilOperacao` | PerfilOperacaoService | Gestão perfil-operação |
| GET/PUT | `/v1/dbispb/cadastros/pmge-parametro-geral` | PmgeParametroGeralService | CRUD pmge parâmetro geral |
| GET/POST/PUT/DELETE | `/v1/dbispb/cadastros/previsao-provisao` | PrevisaoProvisaoService | CRUD previsão provisão |
| GET | `/v1/dbispb/cadastros/prioridade-restricao-cliente` | PrioridadeRestricaoClienteService | Lista prioridades/restrições cliente |
| GET/POST/PUT/DELETE | `/v1/dbispb/cadastros/prioridade` | PrioridadeService | CRUD de prioridades |
| GET/POST/PUT/DELETE | `/v1/dbispb/cadastros/programa` | ProgramaService | CRUD de programas |
| GET/POST/PUT/DELETE | `/v1/dbispb/cadastros/range-reserva` | RangeReservaService | CRUD de range reservas |
| GET | `/v1/dbispb/cadastros/relatorio-analitico-reserva` | RelatorioAnaliticoReservaService | Relatório analítico reserva, gera Excel |
| GET/PUT | `/v1/dbispb/cadastros/reset-senha` | ResetSenhaService | Reset senha usuários |
| GET/POST/PUT/DELETE | `/v1/dbispb/cadastros/restricao-cliente` | RestricaoClienteService | CRUD restrição cliente |
| GET/POST | `/v1/dbispb/cadastros/roteiro-contabil` | RoteiroContabilService | CRUD roteiro contábil |
| GET | `/v1/dbispb/cadastros/saldo-contabil` | SaldoContabilService | Busca data max saldo contábil |
| GET/POST/DELETE | `/v1/dbispb/cadastros/segregacao-perfil` | SegregacaoPerfilService | CRUD segregação perfil |
| GET | `/v1/dbispb/cadastros/seleciona-alcada/listar` | SelecionaAlcadaService | Lista alçadas |
| GET/POST/PUT/DELETE | `/v1/dbispb/cadastros/situacao-reserva` | SituacaoReservaService | CRUD situação reserva |
| GET | `/v1/dbispb/cadastros/str-enviada/listar/{dtIni}/{dtFim}` | StrEnviadaService | Gera Excel qtd STR enviadas (validação máx 90 dias) |
| GET/POST/PUT/DELETE | `/v1/dbispb/cadastros/unidade-org` | UnidadeOrgService | CRUD unidade organizacional |
| GET/POST/PUT/DELETE | `/v1/dbispb/cadastros/usuario` | UsuarioService | CRUD usuários, perfis |
| GET | `/v1/calendario/retornar-dias-uteis/{dataInicial}/{diasUteis}/{praca}` | CalendarioService | Consulta dias úteis calendário |
| GET/POST | `/v1/contingencia/circuit-break` | CircuitBreakService | Gestão circuit break contingência |
| PUT | `/v1/lotes/conciliacao-lote` | ConciliacaoLoteService | Atualiza conciliação lote |
| GET/PUT | `/v1/lotes/monitoramento-lote` | DbintegracaoSpbService | Gestão lotes dbintegração SPB |
| GET | `/v1/dbispb/cadastros/vw-mvsr-movimento-str-ctg/listar` | MvsrMovimentoStrCtgService | Lista movimento STR contingência |
| GET/POST | `/v1/lote/monitoramento-lote/{grmsId}/{moviId}` | LoteService | Gestão lotes, num controle, contingência |
| DELETE/GET/POST/PUT | `/v1/mensagem/batimento-mensagem` | BatimentoMensagemService | Batimento mensagens, updates movimentos (30+ tipos), gera num controle |
| DELETE/GET/POST/PUT | `/v1/mensagem/cadastro-mensagem` | CadastroMensagemService | Cadastro mensagens, insere/atualiza movimentos (30+ tipos), deleta fluxo, gera num controle, verifica alteração |
| GET | `/v1/mensagem/consulta-operacao-automatica` | ConsultaOperacaoAutomaticaService | Consulta operações automáticas |
| GET | `/v1/mensagem/erro-mensagem` | ErroMensagemService | Busca erros mensagens |
| GET | `/v1/mensagem/fluxo-mensagem` | FluxoMensagemService | Consultas fluxo mensagens |
| GET | `/v1/mensagem/fluxo-movimento` | FluxoMovimentoService | Consultas fluxo movimento |
| GET | `/v1/mensagem/geracao-extrato-cip` | GeracaoExtratoCipService | Gera extrato CIP, exportação Excel |
| GET | `/v1/mensagem/grade-horario` | GradeHorarioService | Consulta grade horário mensagens |
| GET | `/v1/mensagem/informe/operProcessadas/movimento/sel` | InformeOperProcessadasService | Informes operações processadas SEL |
| GET | `/v1/mensagem/liquidacao-termo/movimento/mvse-termo` | ModuloLiquidacaoService | Módulo liquidação termo |
| DELETE/GET/POST/PUT | `/v1/mensagem/cadastro-mensagem-duplicada` | MensagemDuplicadaService | Gestão mensagens duplicadas, gera Excel RCO |
| GET/PUT/POST | `/v1/mensagem/modulo-camara-dtvm` | ModuloCamaraDtvmService | Módulo câmara DTVM |
| GET/PUT/POST | `/v1/mensagem/modulo-camara` | ModuloCamaraService | Consultas piloto câmaras (BMA, BMC, BMD, CBL, CMP, CTP, LDL, LTR, PAG), verifica ciclo, atualiza status |
| GET | `/v1/gerar-nsu` | NSUService | Geração NSU |
| GET | `/v1/mensagem/modulo-operacional` | ModuloOperacionalService | Consultas movimento (50+ tipos), paginação |
| GET/POST/PUT | `/v1/mensagem/popup-servicos` | PopupServicosService | Operações popup, exec procedures BD |
| GET | `/v1/movimentos/search` | MovimentoService | Consulta movimentos paginados |
| GET | `/v1/operacoes/agenda-operacao` | AgendaOperacaoService | Lista params, busca msbcId, data max movimento |
| GET | `/v1/operacoes/console-operacoes` | ConsoleOperacoesService | Lista params, busca data max, fluxo por ida/volta |
| GET | `/v1/operacoes/enviar-operacoes` | EnviarOperacoesService | Busca GRMs, instituições, mensagens Bacen |
| GET | `/v1/operacoes/historico-operacoes` | HistoricoOperacoesService | Busca histórico operações |
| GET | `/v1/operacoes/manual-operacoes` | ManualOperacoesService | Gera Excel layouts mensagens Bacen |
| GET | `/v1/operacoes/popup-console` | PopUpConsoleOperacaoService | Retorna resp por operId/msbcId |
| POST/GET/PUT | `/v1/piloto/reserva/ajuste-reserva` | AjusteReservaService | Insere ajuste, retorna valor, atualiza saldos |
| GET | `/v1/piloto/reserva/compulsorio-avista` | CompulsorioAvistaService | Gera extrato, cálculo compulsório à vista |
| GET/POST/PUT | `/v1/piloto/reserva/consulta-reserva` | ConsultaReservaService | Consulta valores, atualiza movs, insere fluxo, verifica ciclo |
| GET | `/v1/piloto/reserva/envia-pendentes` | EnviaPendentesService | Retorna hora sistema, busca instituição, data max, ops |
| PUT | `/v1/piloto/reserva/incluir-excecao` | IncluirExcecaoService | Atualiza parâmetro controle envio |
| GET | `/v1/piloto/reserva/mudanca-horario` | MudancaHorarioService | Valida mudança horário |
| GET/POST/PUT/DELETE | `/v1/piloto/reserva/parametros-automaticos` | ParametrosAutomaticosService | Retorna data, tipos, situações, msgs Bacen, insere/atualiza/deleta |
| GET/PUT | `/v1/piloto/reserva/piloto-reserva` | PilotoReservaService | Atualiza movs, valores, circuit break, validação alertas |

---

## 5. Principais Regras de Negócio

1. **Geração de Número de Controle**: Geração automática de números de controle para mensagens ISPB (IF-023).
2. **Batimento de Mensagens**: Validação e batimento de mensagens recebidas/enviadas, atualização de status de movimentos (30+ tipos: STR, TES, STN, SML, SLC, SLB, RCO, SCG, SEL, RDC, PTX, PAG, PGF, LTR, LPI, LFL, LEI, LDL, GEN, DDA, CCS, CIR, CQL, CTP, COR, CMP, CBL, CCR, CAM, BVF, BMD, BMC, BMA).
3. **Mensagens Duplicadas**: Tratamento específico para mensagens RCO0006 (adiciona sufixo R1), geração de Excel customizado.
4. **Circuit Breaker**: Cálculo de valores de corte amarelo/vermelho para contingência, validação de montante STR/PAG.
5. **Validação de Alertas**: Regras complexas de validação de alertas em piloto de reservas (lógica não detalhada no código fornecido).
6. **Compulsório à Vista**: Integração com CalendarioService para cálculo de dias úteis, geração de extrato.
7. **Validação de Período**: Validação de período máximo de 90 dias para consulta de STR enviadas.
8. **Validação de Data**: Validação de data inicial <= data final em consultas de previsão provisão.
9. **Validação de Hora**: Validação de hora início < hora fim em consultas de fluxo de mensagens.
10. **Geração de Excel**: Formatação específica de Excel para múltiplos relatórios (extrato CIP, interface contábil, relatório analítico reserva, STR enviadas, manual operações, movimentos ISPB).
11. **Sanitização de Logs**: Uso de Sanitizador para sanitização de dados sensíveis em logs.
12. **Lock de Usuário**: Controle de lock de usuário para evitar edições concorrentes.
13. **Verificação de Alteração de Movimento**: Verificação se movimento foi alterado antes de atualização.
14. **Fechamento/Abertura CIP**: Controle de fechamento e abertura de CIP (Câmara Interbancária de Pagamentos).
15. **Paginação**: Suporte a paginação em consultas de movimentos (STR, DDA, PAG).
16. **Enriquecimento de Dados**: Enriquecimento de dados de movimentos com informações adicionais (valor, horário).
17. **Verificação de Ciclo**: Verificação de ciclo de liquidação em operações de câmara.
18. **Verificação de ASOP**: Verificação de ASOP (Autorização de Saída de Operação) em operações de câmara.
19. **Atualização de Status**: Atualização de status de movimentos em múltiplos cenários (003, 008).
20. **Operação Automática**: Suporte a operações automáticas em piloto de reservas.

---

## 6. Relação entre Entidades

O sistema trabalha com entidades do domínio financeiro/bancário, organizadas hierarquicamente:

**Entidades Principais:**
- **Holding** → **Instituição Financeira** → **Unidade Organizacional** → **Usuário**
- **Operação** → **Mensagem Bacen** → **Movimento** → **Fluxo Movimento**
- **Alçada** → **Alçada Operacional** / **Alçada Transação**
- **Perfil** → **Perfil Operação** → **Segregação Perfil**
- **Grupo Serviço** → **Cliente Operação**
- **Prioridade** → **Restrição Cliente**
- **Range Reserva** → **Situação Reserva**
- **Previsão Provisão** → **Consulta Previsão Provisão**
- **Parâmetro Geral** → **Parâmetro Controle Envio**
- **Roteiro Contábil** → **Interface Contábil** → **Saldo Contábil**
- **Lote** → **Conciliação Lote** → **Monitoramento Lote**
- **Movimento** (30+ tipos especializados: STR, TES, SELIC, CAM, CCR, CIR, DDA, LDL, LEI, LTR, PAG, RCO, SEL, etc)

**Relacionamentos:**
- Holding 1:N Instituição Financeira
- Instituição Financeira 1:N Unidade Organizacional
- Unidade Organizacional 1:N Usuário
- Operação 1:N Movimento
- Movimento 1:N Fluxo Movimento
- Perfil N:M Operação (via Perfil Operação)
- Usuário N:M Perfil
- Instituição Financeira N:M Cliente Operação (via Grupo Serviço)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| ALCADA_OPERACIONAL | tabela | SELECT | Alçadas operacionais |
| ALCADA_TRANSACAO | tabela | SELECT | Alçadas de transação |
| ALCADA | tabela | SELECT | Alçadas gerais |
| AVISO | tabela | SELECT | Mensagens de avisos |
| CLIENTE_OPERACAO | tabela | SELECT | Relação cliente-operação |
| CONSULTA_ERROS | tabela | SELECT | Erros de mensagens |
| CONSULTA_PREV_PROVISAO | tabela | SELECT | Previsão provisão |
| CONTROLE_PENDENCIAS | tabela | SELECT | Pendências |
| GRUPO_SERVICO | tabela | SELECT | Grupos de serviço |
| HOLDING | tabela | SELECT | Holdings |
| INSTITUICAO_FINANCEIRA | tabela | SELECT | Instituições financeiras |
| INSTITUICAO_MERCADO | tabela | SELECT | Instituições de mercado |
| INTERFACE_CONTABIL | tabela | SELECT | Interface contábil |
| LOGIN_USUARIO | tabela | SELECT | Dados login usuário |
| OPERACAO | tabela | SELECT | Operações |
| PARAMETRO_CONTROLE_ENVIO | tabela | SELECT | Parâmetros controle envio |
| PARTICIPANTE | tabela | SELECT | Participantes |
| PERFIL | tabela | SELECT | Perfis |
| PERFIL_OPERACAO | tabela | SELECT | Relação perfil-operação |
| PMGE_PARAMETRO_GERAL | tabela | SELECT | Parâmetros gerais |
| PREVISAO_PROVISAO | tabela | SELECT | Previsão provisão |
| PRIORIDADE_RESTRICAO_CLIENTE | tabela | SELECT | Prioridades/restrições cliente |
| PRIORIDADE | tabela | SELECT | Prioridades |
| PROGRAMA | tabela | SELECT | Programas |
| RANGE_RESERVA | tabela | SELECT | Range reservas |
| RELATORIO_ANALITICO_RESERVA | tabela | SELECT | Relatório analítico reserva |
| RESTRICAO_CLIENTE | tabela | SELECT | Restrições cliente |
| ROTEIRO_CONTABIL | tabela | SELECT | Roteiro contábil |
| SALDO_CONTABIL | tabela | SELECT | Saldo contábil |
| SEGREGACAO_PERFIL | tabela | SELECT | Segregação perfil |
| SITUACAO_RESERVA | tabela | SELECT | Situação reserva |
| STR_ENVIADA | tabela | SELECT | STR enviadas |
| UNIDADE_ORG | tabela | SELECT | Unidade organizacional |
| USUARIO | tabela | SELECT | Usuários |
| CALENDARIO | tabela | SELECT | Calendário dias úteis |
| CIRCUIT_BREAK | tabela | SELECT | Circuit break contingência |
| CONCILIACAO_LOTE | tabela | SELECT | Conciliação lote |
| DBINTEGRACAO_SPB | tabela | SELECT | Lotes dbintegração SPB |
| VW_MVSR_MOVIMENTO_STR_CTG | view | SELECT | Movimento STR contingência |
| LOTE | tabela | SELECT | Lotes |
| OPERACAO_AUTOMATICA | tabela | SELECT | Operações automáticas |
| ERRO_MENSAGEM | tabela | SELECT | Erros mensagens |
| FLUXO_MENSAGEM | tabela | SELECT | Fluxo mensagens |
| FLUXO_MOVIMENTO | tabela | SELECT | Fluxo movimento |
| GRADE_EVENTO | tabela | SELECT | Grade horário mensagens |
| MOVIMENTO_SEL | tabela | SELECT | Movimentos SEL |
| MOVIMENTO_TERMO | tabela | SELECT | Movimentos termo |
| CONT_LEG_FLUXO_MOVIMENTO | tabela | SELECT | Contador legado fluxo movimento |
| GRUPO_MENSAGEM | tabela | SELECT | Grupos mensagem |
| DATA_ATUAL | tabela | SELECT | Data atual sistema |
| INSTITUICAO | tabela | SELECT | Instituições |
| MOVIMENTO_RESERVA | tabela | SELECT | Movimentos reserva |
| LANCAMENTO_LTR | tabela | SELECT | Lançamentos LTR |
| LANCAMENTO_DTVM | tabela | SELECT | Lançamentos DTVM |
| CAM_PILOTO | tabela | SELECT | Piloto CAM |
| BMA_PILOTO | tabela | SELECT | Piloto BMA |
| BMC_PILOTO | tabela | SELECT | Piloto BMC |
| BMD_PILOTO | tabela | SELECT | Piloto BMD |
| CBL_PILOTO | tabela | SELECT | Piloto CBL |
| CMP_PILOTO | tabela | SELECT | Piloto CMP |
| CTP_PILOTO | tabela | SELECT | Piloto CTP |
| LDL_PILOTO | tabela | SELECT | Piloto LDL |
| LTR_PILOTO | tabela | SELECT | Piloto LTR |
| PAG_PILOTO | tabela | SELECT | Piloto PAG |
| ASOP | tabela | SELECT | ASOP |
| MOVIMENTO (TES, STR, STN, BVF, CCR, COR, CQL, DDA, LEI, LFL, LPI, SLC, SLB, CIR, PGF, SEL, RDC, GEN, CCS, PTX, SCG, RCO) | tabela | SELECT | Movimentos diversos tipos |
| LAYOUT_MENSAGEM | tabela | SELECT | Layouts mensagens |
| OPER_MSBC_LAME | tabela | SELECT | Operação mensagem layout |
| DOAT_DOMINIO | tabela | SELECT | Domínios |
| ISPB | tabela | SELECT | ISPBs |
| MENSAGEM_BACEN | tabela | SELECT | Mensagens Bacen |
| LAYOUT | tabela | SELECT | Layouts |
| DATA_MOVIMENTO | tabela | SELECT | Data movimento |
| VLDF_VALOR_DEFAULT | tabela | SELECT | Valores default |
| LAOP | tabela | SELECT | Layout operação |
| RESP | tabela | SELECT | Responsáveis |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| ALCADA_OPERACIONAL | tabela | INSERT/UPDATE/DELETE | Alçadas operacionais |
| ALCADA_TRANSACAO | tabela | INSERT/UPDATE/DELETE | Alçadas de transação |
| ALCADA | tabela | INSERT/UPDATE/DELETE | Alçadas gerais |
| CLIENTE_OPERACAO | tabela | INSERT/DELETE | Relação cliente-operação |
| GRUPO_SERVICO | tabela | INSERT/UPDATE/DELETE | Grupos de serviço |
| HOLDING | tabela | INSERT/UPDATE/DELETE | Holdings |
| INSTITUICAO_FINANCEIRA | tabela | INSERT/UPDATE/DELETE | Instituições financeiras |
| INSTITUICAO_MERCADO | tabela | INSERT/UPDATE/DELETE | Instituições de mercado |
| INTERFACE_CONTABIL | tabela | INSERT | Interface contábil |
| LOGIN_USUARIO | tabela | UPDATE | Dados login usuário |
| OPERACAO | tabela | INSERT/UPDATE/DELETE | Operações |
| PARAMETRO_CONTROLE_ENVIO | tabela | UPDATE | Parâmetros controle envio |
| PARTICIPANTE | tabela | UPDATE | Participantes |
| PERFIL | tabela | INSERT/UPDATE/DELETE | Perfis |
| PERFIL_OPERACAO | tabela | INSERT/DELETE | Relação perfil-operação |
| PMGE_PARAMETRO_GERAL | tabela | UPDATE | Parâmetros gerais |
| PREVISAO_PROVISAO | tabela | INSERT/UPDATE/DELETE | Previsão provisão |
| PRIORIDADE | tabela | INSERT/UPDATE/DELETE | Prioridades |
| PROGRAMA | tabela | INSERT/UPDATE/DELETE | Programas |
| RANGE_RESERVA | tabela | INSERT/UPDATE/DELETE | Range reservas |
| RESET_SENHA | tabela | UPDATE | Reset senha |
| RESTRICAO_CLIENTE | tabela | INSERT/UPDATE/DELETE | Restrições cliente |
| ROTEIRO_CONTABIL | tabela | INSERT | Roteiro contábil |
| SEGREGACAO_PERFIL | tabela | INSERT/DELETE | Segregação perfil |
| SITUACAO_RESERVA | tabela | INSERT/UPDATE/DELETE | Situação reserva |
| UNIDADE_ORG | tabela | INSERT/UPDATE/DELETE | Unidade organizacional |
| USUARIO | tabela | INSERT/UPDATE/DELETE | Usuários |
| CONCILIACAO_LOTE | tabela | UPDATE | Conciliação lote |
| DBINTEGRACAO_SPB | tabela | UPDATE | Lotes dbintegração SPB |
| LOTE | tabela | INSERT | Lotes |
| FLUXO_MOVIMENTO | tabela | INSERT/DELETE/UPDATE | Fluxo movimento |
| MOVIMENTO (30+ tipos: STR, TES, STN, SML, SLC, SLB, RCO, SCG, SEL, RDC, PTX, PAG, PGF, LTR, LPI, LFL, LEI, LDL, GEN, DDA, CCS, CIR, CQL, CTP, COR, CMP, CBL, CCR, CAM, BVF, BMD, BMC, BMA) | tabela | INSERT/UPDATE | Movimentos diversos tipos |
| USUA_LOCK | tabela | UPDATE | Lock usuário |
| STATUS_MOVIMENTO | tabela | UPDATE | Status movimento |
| CONT_LEG_FLUXO_MOVIMENTO | tabela | INSERT | Contador legado fluxo movimento |
| MOVIMENTO_RESERVA | tabela | UPDATE | Movimentos reserva |
| AJUSTE_RESERVA | tabela | INSERT | Ajuste reserva |
| SALDO_RESERVA | tabela | UPDATE | Saldo reserva |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| Excel XLSX (movimentos ISPB) | gravação | ExcelService | Arquivos Excel com movimentos entrada/saída, tabelas RCO0006, formatação financeira |
| Excel XLSX (extrato CIP) | gravação | GeracaoExtratoCipService | Relatório operacional quantidade CIP3 com agrupamento por grade/faixa tarifa |
| Excel XLSX (interface contábil) | gravação | InterfaceContabilService | Formato legado contábil |
| Excel XLSX (relatório analítico reserva) | gravação | RelatorioAnaliticoReservaService | Extrato analítico reserva |
| Excel XLSX (STR enviadas) | gravação | StrEnviadaService | Quantidade STR enviadas por período |
| Excel XLSX (manual operações) | gravação | ManualOperacoesService | Layouts mensagens Bacen com estrutura (tag, descrição, tipo, tamanho) |
| Excel XLSX (RCO) | gravação | MensagemDuplicadaService | Excel específico para mensagens RCO duplicadas |
| Logs JSON | gravação | Logback | Logs estruturados em formato JSON (níveis WARN/INFO) |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| **API Mensageria** | REST OAuth2 | Operações CRUD movimento, consultas cadastrais, fechamento/abertura, batimento mensagens, cadastro mensagens, mensagens duplicadas, módulo câmara, módulo operacional, popup serviços, fluxo mensagem, fluxo movimento, grade horário, geração extrato CIP, NSU |
| **API Cadastro** | REST OAuth2 | CRUD alçadas, avisos, cliente-operação, consulta erros, consulta previsão provisão, controle pendências, grupo serviço, holding, instituição financeira, instituição mercado, interface contábil, login usuário, operação, parâmetro controle envio, participante, perfil, perfil operação, pmge parâmetro geral, previsão provisão, prioridade, programa, range reserva, relatório analítico reserva, reset senha, restrição cliente, roteiro contábil, saldo contábil, segregação perfil, situação reserva, STR enviada, unidade org, usuário |
| **API Operação** | REST OAuth2 | Agenda operação, console operações, enviar operações, histórico operações, manual operações, popup console |
| **API Lote** | REST OAuth2 | Conciliação lote, monitoramento lote, gestão lotes |
| **API Piloto Reserva** | REST OAuth2 | Ajuste reserva, compulsório à vista, consulta reserva, envia pendentes, incluir exceção, mudança horário, parâmetros automáticos, piloto reserva |
| **API Calendário** | REST OAuth2 | Consulta dias úteis |
| **API Contingência** | REST OAuth2 | Circuit break, feature toggles |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 6/10

**Justificativa:**

**Pontos Positivos:**
- Uso adequado de padrões Spring Boot (Services, DTOs, Configuration)
- Segurança implementada via OAuth2 e @Secured
- Uso de BigDecimal para valores financeiros (precisão)
- Sanitização de logs para dados sensíveis
- Mapeamento automatizado com MapStruct
- Documentação Swagger/OpenAPI
- Separação clara de responsabilidades (BFF pattern)
- Uso de Lombok para redução de boilerplate
- Configuração multi-ambiente (des/uat/prd)

**Pontos Negativos:**
- **Alta duplicação de código**: Múltiplas classes Service/Impl com estrutura quase idêntica (ex: MvxxDTO vs MvxxDTORepresentation), sugerindo falta de refatoração
- **Métodos muito extensos**: Classes como CadastroMensagemServiceImpl e BatimentoMensagemServiceImpl possuem dezenas de métodos similares que poderiam ser generalizados
- **Falta de abstração**: Muitos métodos repetitivos para diferentes tipos de movimento (30+ tipos) sem uso de generics ou padrão Template Method
- **Try-catch genérico**: Tratamento de exceções muito amplo (catch Exception) sem diferenciação de tipos de erro
- **Acoplamento alto**: Dependência direta de múltiplos RestTemplates OAuth2, dificultando testes unitários
- **Falta de testes**: Código fornecido não inclui testes unitários/integração
- **Nomenclatura inconsistente**: Mistura de português/inglês, nomes de variáveis pouco descritivos (ex: mvxxTg*)
- **Complexidade ciclomática alta**: Métodos com muitas condicionais e lógica de negócio embutida
- **Falta de documentação inline**: Poucos comentários explicativos em lógicas complexas
- **Possível violação SRP**: Classes com múltiplas responsabilidades (ex: PilotoReservaService com 40+ métodos)

**Recomendações:**
1. Refatorar classes duplicadas usando herança/composição
2. Implementar padrão Strategy para diferentes tipos de movimento
3. Criar camada de abstração para chamadas REST (ex: ApiClient genérico)
4. Adicionar testes unitários com cobertura mínima de 70%
5. Melhorar tratamento de exceções com tipos específicos
6. Padronizar nomenclatura (preferencialmente inglês)
7. Aplicar princípios SOLID (especialmente SRP e DIP)
8. Documentar regras de negócio complexas (ex: circuit breaker, validação alertas)

---

## 14. Observações Relevantes

1. **Arquitetura BFF**: O sistema atua como Backend For Frontend, consolidando chamadas a múltiplos microsserviços especializados, simplificando a integração para frontends.

2. **Domínio Financeiro Complexo**: O sistema lida com 30+ tipos de movimentos financeiros padronizados pelo Banco Central (BACEN), cada um com estrutura de dados específica e regras de negócio distintas.

3. **Segurança Granular**: Controle de acesso via @Secured com múltiplos perfis (MN_*), permitindo autorização fine-grained por funcionalidade.

4. **Geração de Relatórios**: Uso intensivo de Apache POI para geração de relatórios Excel complexos com formatação específica (estilos, fontes, cores, merge cells).

5. **Integração OAuth2**: Todas as integrações com microsserviços externos utilizam OAuth2RestTemplate, garantindo autenticação/autorização em todas as chamadas.

6. **Contingência**: Implementação de circuit breaker para gestão de contingências, com cálculo de valores de corte amarelo/vermelho.

7. **Paginação**: Suporte a paginação em consultas de movimentos (STR, DDA, PAG), melhorando performance em grandes volumes.

8. **Enriquecimento de Dados**: Lógica de enriquecimento de dados de movimentos com informações adicionais (valor, horário) via forEach.

9. **Validações de Negócio**: Múltiplas validações de negócio (período máximo, data inicial <= final, hora início < fim, lock usuário, alteração movimento).

10. **Mensagens Duplicadas**: Tratamento específico para mensagens RCO0006 (adiciona sufixo R1), indicando lógica de negócio especializada.

11. **Calendário de Dias Úteis**: Integração com serviço de calendário para cálculo de dias úteis, essencial para operações financeiras.

12. **Geração de NSU**: Geração de Número Sequencial Único para controle de mensagens.

13. **Procedures BD**: Execução de procedures de banco de dados via PopupServicosService, indicando lógica de negócio legada no BD.

14. **Configuração Multi-Ambiente**: Suporte a múltiplos ambientes (des/uat/prd) via arquivos de configuração Kubernetes (infra.yml).

15. **Logs Estruturados**: Uso de Logback com formato JSON, facilitando análise e monitoramento.

16. **Sanitização de Logs**: Uso de Sanitizador para remover dados sensíveis de logs, atendendo requisitos de segurança/LGPD.

17. **Mapeamento Automatizado**: Uso de MapStruct para mapeamento de DTOs, reduzindo código boilerplate e erros manuais.

18. **Alta Granularidade de DTOs**: 200+ DTOs para representar diferentes tipos de mensagens ISPB, refletindo complexidade do domínio financeiro.

19. **Padrão Naming Tags**: Atributos seguem padrão "mvXxTg*" indicando tags de mensageria padronizada ISPB/BACEN.

20. **Possível Código Legado**: Estrutura sugere migração de sistema legado (procedures BD, nomenclatura tags, duplicação de classes), indicando necessidade de refatoração contínua.