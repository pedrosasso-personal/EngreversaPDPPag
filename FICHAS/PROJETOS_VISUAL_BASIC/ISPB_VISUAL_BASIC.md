# Ficha Técnica Consolidada do Sistema Visual Basic

## 1. Finalidade e Objetivo do Sistema

O sistema ISPB (Interface do Sistema de Pagamentos Brasileiro) é uma aplicação bancária corporativa desenvolvida para gerenciar e processar operações financeiras do Sistema de Pagamentos Brasileiro (SPB). Serve como interface central para instituições financeiras (Banco Votorantim e BVSA) realizarem operações de transferência de recursos, liquidação de câmaras de compensação, gestão de reservas bancárias e controle de mensagens financeiras junto ao Banco Central do Brasil.

**Principais objetivos:**
- Processar e monitorar mensagens financeiras entre instituições e o Banco Central
- Gerenciar reservas bancárias obrigatórias e compulsórios
- Controlar operações de múltiplas câmaras de compensação (STR, LDL, PAG, SEL, etc.)
- Garantir conformidade regulatória e auditoria de operações financeiras
- Fornecer contingência operacional para o SPB

## 2. Principais Funcionalidades

### 2.1 Gestão de Operações Financeiras
- **Cadastro de Mensagens**: Inclusão, alteração e consulta de mensagens financeiras de 35+ tipos de câmaras (STR, LDL, RDC, CIR, SEL, SLB, STN, TES, PGF, SML, PAG, BMA, BMC, BMD, GEN, CCS, CBL, CTP, LTR, DDA, CCR, BVF, PTX, COR, CQL, CMP, SCG, LEI, LPI, LFL, SLC)
- **Confirmação de Operações**: Sistema de confirmação simples ou dupla com validação de usuários autorizados
- **Agendamento**: Programação de operações para execução futura
- **Reenvio de Mensagens**: Reprocessamento de mensagens com erro

### 2.2 Piloto de Reservas Bancárias
- **Monitoramento em Tempo Real**: Acompanhamento de saldo de reserva, débitos e créditos pendentes
- **Circuit Break**: Controle manual de envio de operações em situações críticas
- **Gestão de Fila**: Seleção e confirmação de mensagens pendentes de envio
- **Controle de Compulsório**: Monitoramento de recolhimento compulsório à vista com alertas de desenquadramento

### 2.3 Console de Operações
- **Monitoramento Centralizado**: Visualização de mensagens de entrada e saída em tempo real
- **Refresh Automático**: Atualização periódica das informações (configurável)
- **Acesso Rápido**: Navegação direta para módulos específicos de serviços

### 2.4 Gestão de Câmaras de Compensação
- **Liquidação de Câmaras**: Controle de liquidações CBLC, SILOC, BMF, BACEN
- **Ciclos Operacionais**: Monitoramento de horários de abertura/fechamento
- **Saldos**: Cálculo de NET, Pendente e A Realizar (PAG)
- **Confirmações**: Processamento de confirmações de câmaras (BMA, BMC, LDL, LTR)

### 2.5 Controle de Acesso e Segurança
- **Autenticação Dupla**: Login com senha + token RSA para Security Officers
- **Perfis de Acesso**: Gestão de perfis (Autorizador, Digitador, Consulta)
- **Alçadas Operacionais**: Controle de limites de valores por transação
- **Segregação de Perfis**: Restrições granulares sobre conteúdos de mensagens

### 2.6 Contingência SPB
- **Geração de Lotes STR**: Criação de arquivos XML para envio ao Banco Central
- **Chaves RdList**: Gerenciamento de chaves de segurança para operações de contingência
- **Conciliação**: Reconciliação de transferências enviadas com retornos do BACEN
- **Validação de Arquivos**: Validação de XMLs contra schema XSD

### 2.7 Relatórios e Interfaces
- **Interface Contábil**: Geração de arquivos para sistema legado (formato MV61)
- **Relatórios Excel**: Exportação de operações, custos CIP, fluxo de mensagens
- **Extrato de Reserva**: Relatório analítico de mensagens BACEN relacionadas a reservas
- **Manual de Operações**: Geração automática de documentação de operações

## 3. Fluxo entre Componentes

### 3.1 Fluxo de Autenticação
```
frmLoginUsuario → BVLoginUsuario (DLL VFAcesso) → Validação de Credenciais
                                                  ↓
                                    Carregamento de Perfis e Permissões
                                                  ↓
                                    mdiISPB (Menu Principal) → Habilitação de Menus
```

### 3.2 Fluxo de Cadastro de Mensagens
```
frmConsultaOperacao → Seleção de Operação → frmCadastroMensagem/frmCadMsgRepet
                                                      ↓
                                    Validação de Campos (modGeral)
                                                      ↓
                                    Stored Procedures (sp_in_mvXX_movi)
                                                      ↓
                                    Registro de Fluxo (tb_flmv)
```

### 3.3 Fluxo de Confirmação de Operações
```
frmModulosCamaras/frmModulosOperacionais → Seleção de Mensagens Digitadas
                                                      ↓
                                    Validação de Usuário e Alçada (modGeral)
                                                      ↓
                                    Atualização de Status (gsAtualizaStatus)
                                                      ↓
                                    Envio para Fila de Saída
```

### 3.4 Fluxo do Piloto de Reservas
```
frmPilotoReserva → Consulta de Saldo (sp_se_rese_308)
                                ↓
                  Exibição de Fila de Operações Pendentes
                                ↓
                  Seleção Manual ou Circuit Break
                                ↓
                  Confirmação → Envio para Legado/BACEN
```

### 3.5 Fluxo de Contingência
```
frmMonitoramentoLoteSTR → Geração de Lote (modContingencia)
                                      ↓
                        Criação de XML ASPB005
                                      ↓
                        Validação contra XSD
                                      ↓
                        Conversão UTF-16BE + ZIP
                                      ↓
                        Envio Manual ao BACEN
                                      ↓
                        Conciliação Posterior
```

## 4. Tabelas de Banco de Dados

### 4.1 Tabelas/Views Lidas

#### Movimentos e Operações
- **tb_movi_movimento**: Movimentos financeiros gerais (cabeçalho)
- **tb_mvse_movimento_sel**: Movimentos SEL (SELIC)
- **tb_mvsr_movimento_str**: Movimentos STR (Transferências)
- **tb_mvld_movimento_ldl**: Movimentos LDL (Liquidação)
- **tb_mvca_movimento_cam**: Movimentos CAM (Câmara)
- **tb_mvpg_movimento_pag**: Movimentos PAG (CIP)
- **tb_mvba_movimento_bma**: Movimentos BMA
- **tb_mvbc_movimento_bmc**: Movimentos BMC
- **tb_mvbd_movimento_bmd**: Movimentos BMD
- **tb_mvcl_movimento_cbl**: Movimentos CBL
- **tb_mvcp_movimento_ctp**: Movimentos CTP
- **tb_mvlr_movimento_ltr**: Movimentos LTR
- **tb_mvda_movimento_dda**: Movimentos DDA
- **tb_mvcc_movimento_ccr**: Movimentos CCR
- **tb_mvbf_movimento_bvf**: Movimentos BVF
- **tb_mvpx_movimento_ptx**: Movimentos PTX
- **tb_mvco_movimento_cor**: Movimentos COR
- **tb_mvcq_movimento_cql**: Movimentos CQL
- **tb_mvcm_movimento_cmp**: Movimentos CMP
- **tb_mvsg_movimento_scg**: Movimentos SCG
- **tb_mvli_movimento_lei**: Movimentos LEI
- **tb_mvlp_movimento_lpi**: Movimentos LPI
- **tb_mvll_movimento_lfl**: Movimentos LFL
- **tb_mvsc_movimento_slc**: Movimentos SLC
- **tb_mvcr_movimento_cir**: Movimentos CIR
- **tb_mvsb_movimento_slb**: Movimentos SLB
- **tb_mvsn_movimento_stn**: Movimentos STN
- **tb_mvts_movimento_tes**: Movimentos TES
- **tb_mvpf_movimento_pgf**: Movimentos PGF
- **tb_mvro_movimento_rco**: Movimentos RCO
- **tb_mvrd_movimento_rdc**: Movimentos RDC
- **tb_mvgn_movimento_gen**: Movimentos GEN (Genéricos)
- **tb_mvcs_movimento_ccs**: Movimentos CCS

#### Cadastros e Configurações
- **tb_usua_usuario**: Usuários do sistema
- **tb_perf_perfil**: Perfis de acesso
- **tb_hold_holding**: Holdings
- **tb_inst_instituicao**: Instituições financeiras
- **tb_unor_unidade_organizacional**: Unidades organizacionais
- **tb_oper_operacao**: Operações disponíveis
- **tb_msbc_mensagem_bacen**: Mensagens do Banco Central
- **tb_grse_grupo_servico**: Grupos de serviços
- **tb_sgse_subgrupo_servico**: Subgrupos de serviços
- **tb_prio_prioridade**: Prioridades de envio
- **tb_stop_status_operacao**: Status de operações
- **tb_ispb**: Cadastro de ISPBs (instituições participantes)
- **tb_inme_instituicao_mercado**: Clientes/IFs do mercado

#### Layouts e Parâmetros
- **tb_laop_layout_operacao**: Layout de operações (dicionário de dados)
- **tb_lame_layout_mensagem**: Layout de mensagens
- **tb_doat_dominio_atributo**: Domínios de atributos
- **tb_vldf_valor_default**: Valores padrão
- **tb_pmge_parametros_gerais**: Parâmetros gerais do sistema
- **tb_grade_evento**: Grade de eventos/horários

#### Controle e Auditoria
- **tb_flmv_fluxo_movimento**: Fluxo/histórico de movimentos
- **tb_aspr_acesso_sistema_perfil**: Acessos de perfis a programas
- **tb_asop_acesso_operacao**: Acessos de perfis a operações
- **tb_alca_alcada**: Alçadas de aprovação
- **tb_altr_alcada_transacao**: Alçadas por transação
- **tb_sgpe_segregacao_perfil**: Segregação de conteúdos por perfil

#### Reservas e Compulsório
- **tb_rese_reserva**: Saldos de reserva bancária
- **tb_cz_rese_stre**: Status de reserva e circuit break
- **tb_pepo_previsao_provisao**: Previsões e provisões
- **tb_mvro_movimento_rco**: Movimentos de compulsório

#### Contingência
- **DBISPB_RDLIST..TbChaveRdlist**: Chaves RdList disponíveis
- **DBISPB_RDLIST..TbOperacaoRdlist**: Operações RdList registradas
- **DBISPB_RDLIST..TbValorOperacao**: Valores de operação para chaves
- **DBINTEGRACAOSPB..prConsultarLotesContSTR**: Lotes de contingência STR
- **DBINTEGRACAOSPB..prConsultarContingenciaSTR**: Transferências de lote

### 4.2 Tabelas/Views Atualizadas

#### Movimentos
- **tb_movi_movimento**: Atualização de status, confirmações, agendamentos, locks
- **tb_mvse_movimento_sel**: Dados específicos de movimentos SEL
- **tb_mvsr_movimento_str**: Dados específicos de movimentos STR
- **tb_mvld_movimento_ldl**: Dados específicos de movimentos LDL
- **tb_mvca_movimento_cam**: Dados específicos de movimentos CAM
- **tb_mvpg_movimento_pag**: Dados específicos de movimentos PAG
- **tb_mvba_movimento_bma**: Dados específicos de movimentos BMA
- **tb_mvbc_movimento_bmc**: Dados específicos de movimentos BMC
- **tb_mvbd_movimento_bmd**: Dados específicos de movimentos BMD
- (E demais tabelas de movimento específicas por serviço)

#### Controle e Auditoria
- **tb_flmv_fluxo_movimento**: Inserção de registros de auditoria (Digitou, Confirmou, Alterou, Excluiu, Reenviou)
- **tb_aspr_acesso_sistema_perfil**: Inclusão/exclusão de acessos de perfis a programas
- **tb_asop_acesso_operacao**: Inclusão/exclusão de acessos de perfis a operações
- **tb_sgpe_segregacao_perfil**: Inclusão/exclusão de segregações de conteúdo

#### Reservas
- **tb_rese_reserva**: Atualização de saldos de reserva
- **tb_cz_rese_stre**: Atualização de circuit break
- **tb_pepo_previsao_provisao**: Inclusão/alteração/exclusão de previsões e provisões

#### Contingência
- **DBISPB_RDLIST..TbChaveRdlist**: Atualização de flag de chave utilizada
- **DBISPB_RDLIST..TbOperacaoRdlist**: Inserção de operações RdList
- **DBINTEGRACAOSPB..prAtualizarContingenciaSTR**: Atualização de status de lotes
- **DBINTEGRACAOSPB..prAtualizarLancamentoContSTR**: Atualização de status de transferências

#### Parâmetros
- **tb_pmge_parametros_gerais**: Atualização de data de movimento
- **tb_parametro_controle_envio**: Atualização de parâmetros de controle de envio

## 5. Arquivos Gerados ou Manipulados

### 5.1 Arquivos de Configuração
- **ispb.ini**: Configurações do sistema (servidor, banco, ambiente, paths, e-mails, parâmetros)

### 5.2 Arquivos de Log
- **agente[YYYYMMDD].log**: Logs diários de operações do agente
- **AUD[CONTINGENCIA][YYYYMMDD].log**: Logs de auditoria de contingência
- **Logs SQL**: Registro de queries executadas
- **Logs de Erro**: Registro de erros do sistema
- **Logs de Token**: Registro de