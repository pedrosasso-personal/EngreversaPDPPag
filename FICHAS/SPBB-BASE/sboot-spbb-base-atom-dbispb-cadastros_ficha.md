# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de gerenciamento de cadastros para o DBISPB (Deutsche Bank ISPB Brasil) no contexto do Sistema de Pagamentos Brasileiro (SPB). A aplicação fornece uma API REST completa para administração de entidades fundamentais do sistema financeiro, incluindo holdings, instituições financeiras, usuários, perfis de acesso, operações, reservas STR, alçadas de aprovação, prioridades e parâmetros operacionais. O sistema atua como base cadastral para operações do SPB, integrando-se com mensagens BACEN e mantendo controle rigoroso de permissões e segregação de funções.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **AlcadaApiDelegateImpl** | Controller REST para CRUD de alçadas (limites de valores para aprovações) |
| **AlcadaOperacionalApiDelegateImpl** | Controller REST para alçadas operacionais e grupos de mensagem |
| **AlcadaTransacaoApiDelegateImpl** | Controller REST para alçadas por transação |
| **ClienteOperacaoApiDelegateImpl** | Controller REST para relacionamento cliente-operação (permissões operacionais) |
| **ConsultaErrosApiDelegateImpl** | Controller REST para consulta de erros em mensagens |
| **ConsultaPrevProvisaoApiDelegateImpl** | Controller REST para consulta de previsões/provisões financeiras |
| **ControlePendenciasApiDelegateImpl** | Controller REST para controle de mensagens pendentes |
| **GrupoServicoDelegateImpl** | Controller REST para CRUD de grupos de serviço |
| **HoldingApiDelegateImpl** | Controller REST para CRUD de holdings |
| **InstituicaoFinanceiraApiDelegateImpl** | Controller REST para cadastro de instituições financeiras e reservas |
| **InstituicaoMercadoApiDelegateImpl** | Controller REST para instituições não-bancárias |
| **InterfaceContabilApiDelegateImpl** | Controller REST para interface contábil (geração de lançamentos) |
| **LoginUsuarioApiDeletateImpl** | Controller REST para autenticação e autorização de usuários |
| **OperacoesApiDelegateImpl** | Controller REST para CRUD de operações |
| **ParametroControleEnvioApiDelegateImpl** | Controller REST para parâmetros de controle de envio |
| **ParticipanteApiDelegateImpl** | Controller REST para participantes SPB (ISPB) |
| **PerfilApiDelegateImpl** | Controller REST para CRUD de perfis de acesso |
| **PerfilOperacaoApiDelegateImpl** | Controller REST para controle de acesso (Perfil x Operação x Ações) |
| **PmgeParametroGeralApiDelegateImpl** | Controller REST para parâmetros gerais do sistema |
| **PrevisaoProvisaoApiDelegateImpl** | Controller REST para CRUD de previsões/provisões |
| **PrioridadeApiDelegateImpl** | Controller REST para CRUD de prioridades |
| **PrioridadeRestricaoClienteApiDelegateImpl** | Controller REST para consulta de prioridades com restrições |
| **ProgramaApiDelegateImpl** | Controller REST para CRUD de programas (menu/telas) |
| **RangeReservaApiDelegateImpl** | Controller REST para ranges de reserva STR |
| **RelatorioAnaliticoReservaApiDelegateImpl** | Controller REST para relatório analítico de reservas |
| **ResetSenhaApiDelegateImpl** | Controller REST para reset de senha |
| **RestricaoClienteApiDelegateImpl** | Controller REST para restrições operacionais de clientes |
| **RoteiroContabilApiDelegateImpl** | Controller REST para roteiros contábeis |
| **SaldoContabilApiDelegateImpl** | Controller REST para consulta de saldos contábeis |
| **SegregacaoPerfilApiDelegateImpl** | Controller REST para segregação de campos por perfil |
| **SelecionaAlcadaApiDelegateImpl** | Controller REST para listagem de alçadas |
| **SituacaoReservaApiDelegateImpl** | Controller REST para CRUD de situações de reserva |
| **StrEnviadaApiDelegateImpl** | Controller REST para consulta de STRs enviadas |
| **UnidadeOrgApiDelegateImpl** | Controller REST para CRUD de unidades organizacionais |
| **UsuarioApiDelegateImpl** | Controller REST para CRUD de usuários |
| **VwMvsrMovimentoStrCtgApiDelegateImpl** | Controller REST para consulta de movimentos STR contingência |
| **Services (diversos)** | Camada de negócio com validações e orquestração de operações |
| **Repositories (diversos)** | Camada de persistência usando JDBI3 SQL Object |
| **Mappers (MapStruct)** | Conversão entre DTOs e entidades |

---

## 3. Tecnologias Utilizadas

- **Framework Backend**: Spring Boot 2.7.7
- **Linguagem**: Java 11
- **Persistência**: JDBI 3.9.1 (SQL Object)
- **Banco de Dados**: Sybase ASE (jdbc:sybase, driver jconn4 16.3)
- **Mapeamento Objeto-Relacional**: MapStruct
- **Segurança**: OAuth2 JWT (JWKS), LDAP, roles AD
- **Documentação API**: OpenAPI 3.0 / Swagger
- **Auditoria**: br.com.bancobv.atle.base.trilha.auditoria-web 0.0.4
- **Métricas**: Micrometer/Prometheus
- **Logging**: Logback com formato JSON, async appender
- **Build**: Maven
- **Containerização**: Docker, Kubernetes
- **Utilitários**: Lombok, Apache Commons
- **Testes**: JUnit, Mockito
- **Monitoramento**: Grafana dashboards

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | /alcadas | AlcadaApiDelegateImpl | Lista todas as alçadas |
| GET | /alcadas/{id} | AlcadaApiDelegateImpl | Busca alçada por ID |
| POST | /alcadas | AlcadaApiDelegateImpl | Insere nova alçada |
| PUT | /alcadas | AlcadaApiDelegateImpl | Atualiza alçada existente |
| DELETE | /alcadas/{id} | AlcadaApiDelegateImpl | Remove alçada |
| GET | /alcada-operacional | AlcadaOperacionalApiDelegateImpl | Lista alçadas operacionais |
| PUT | /alcada-operacional | AlcadaOperacionalApiDelegateImpl | Atualiza alçada operacional |
| GET | /grupo-mensagem | AlcadaOperacionalApiDelegateImpl | Lista grupos de mensagem |
| GET | /cliente-operacao | ClienteOperacaoApiDelegateImpl | Consulta operações permitidas por cliente |
| GET | /consulta-erros | ConsultaErrosApiDelegateImpl | Consulta erros de mensagens por período |
| GET | /consulta-prev-provisao | ConsultaPrevProvisaoApiDelegateImpl | Consulta previsões/provisões |
| GET | /controle-pendencias | ControlePendenciasApiDelegateImpl | Lista mensagens pendentes |
| GET/POST/PUT/DELETE | /grupo-servico | GrupoServicoDelegateImpl | CRUD de grupos de serviço |
| GET/POST/PUT/DELETE | /holding | HoldingApiDelegateImpl | CRUD de holdings |
| GET/POST/PUT/DELETE | /instituicao-financeira | InstituicaoFinanceiraApiDelegateImpl | CRUD de instituições financeiras |
| GET/POST/PUT/DELETE | /instituicao-mercado | InstituicaoMercadoApiDelegateImpl | CRUD de instituições de mercado |
| POST | /interface-contabil | InterfaceContabilApiDelegateImpl | Gera lançamentos contábeis |
| GET | /login-usuario | LoginUsuarioApiDeletateImpl | Consultas de autenticação/autorização |
| GET/POST/PUT/DELETE | /operacoes | OperacoesApiDelegateImpl | CRUD de operações |
| GET/PUT | /parametro-controle-envio | ParametroControleEnvioApiDelegateImpl | Consulta/atualiza parâmetros de controle |
| GET/PUT | /participante | ParticipanteApiDelegateImpl | Lista/atualiza participantes SPB |
| GET/POST/PUT/DELETE | /perfil | PerfilApiDelegateImpl | CRUD de perfis |
| GET/POST/DELETE | /perfil-operacao | PerfilOperacaoApiDelegateImpl | Gerencia acessos perfil-operação |
| GET/PUT | /pmge-parametro-geral | PmgeParametroGeralApiDelegateImpl | Consulta/atualiza parâmetros gerais |
| GET/POST/PUT/DELETE | /previsao-provisao | PrevisaoProvisaoApiDelegateImpl | CRUD de previsões/provisões |
| GET/POST/PUT/DELETE | /prioridade | PrioridadeApiDelegateImpl | CRUD de prioridades |
| GET | /prioridade-restricao-cliente | PrioridadeRestricaoClienteApiDelegateImpl | Consulta prioridades com restrições |
| GET/POST/PUT/DELETE | /programa | ProgramaApiDelegateImpl | CRUD de programas |
| GET/POST/PUT/DELETE | /range-reserva | RangeReservaApiDelegateImpl | CRUD de ranges de reserva |
| GET | /relatorio-analitico-reserva | RelatorioAnaliticoReservaApiDelegateImpl | Gera relatório analítico |
| PUT | /reset-senha | ResetSenhaApiDelegateImpl | Reset de senha de usuário |
| GET/POST/PUT/DELETE | /restricao-cliente | RestricaoClienteApiDelegateImpl | CRUD de restrições de cliente |
| GET | /roteiro-contabil | RoteiroContabilApiDelegateImpl | Consulta roteiros contábeis |
| GET | /saldo-contabil | SaldoContabilApiDelegateImpl | Consulta data máxima de movimento |
| GET/POST/DELETE | /segregacao-perfil | SegregacaoPerfilApiDelegateImpl | Gerencia segregação de perfis |
| GET | /seleciona-alcada | SelecionaAlcadaApiDelegateImpl | Lista alçadas disponíveis |
| GET/POST/PUT/DELETE | /situacao-reserva | SituacaoReservaApiDelegateImpl | CRUD de situações de reserva |
| GET | /str-enviada | StrEnviadaApiDelegateImpl | Consulta STRs enviadas |
| GET/POST/PUT/DELETE | /unidade-org | UnidadeOrgApiDelegateImpl | CRUD de unidades organizacionais |
| GET/POST/PUT/DELETE | /usuario | UsuarioApiDelegateImpl | CRUD de usuários |
| GET | /vw-mvsr-movimento-str-ctg | VwMvsrMovimentoStrCtgApiDelegateImpl | Consulta movimentos STR contingência |

---

## 5. Principais Regras de Negócio

1. **Validação de Duplicidade**: Impede inserção de registros duplicados em alçadas, prioridades, operações e usuários (login único)
2. **Validação de Ranges de Reserva**: Verifica sobreposição de valores em ranges de reserva STR antes de inserção/atualização
3. **Hierarquia Organizacional**: Valida circularidade em unidades organizacionais (pai não pode ser filho de si mesmo)
4. **Exclusão Condicional de Perfis**: Perfil só pode ser excluído se não estiver vinculado a usuários, acessos de operação ou programas
5. **Exclusão em Cascata**: Ao excluir instituição financeira, remove também reserva vinculada
6. **Controle de Acesso Granular**: Sistema de permissões baseado em perfil-operação-ação (consultar/incluir/alterar/excluir/confirmar)
7. **Segregação de Perfis**: Controle de visibilidade de campos XML de mensagens BACEN por perfil
8. **Validação de Período**: Consultas de STR enviadas limitadas a 3 meses, com data inicial menor que final
9. **Restrições Operacionais**: Controle de limites de risco e operações permitidas por cliente institucional
10. **Alçadas de Aprovação**: Sistema de limites de valores para aprovação de transações
11. **Geração de Lançamentos Contábeis**: Interface contábil gera lançamentos por instituição e data
12. **Validação de Existência**: Verifica existência de situação de reserva antes de inserir range
13. **Auto-incremento de Sequenciais**: Geração automática de sequenciais para previsões/provisões e situações de reserva
14. **Validação de Atualização de Usuário**: Exige idUsuario ou usuaDsLogin para atualização
15. **Controle de Pendências**: Unifica consulta de pendências em 11 tipos de mensagens (BMC/CBL/CIR/CTP/GEN/LDL/LTR/PAG/RCO/RDC/SEL/SLB/STN/TES/STR)

---

## 6. Relação entre Entidades

**Hierarquia Principal:**
- **Holding** (tb_hold_holding) → contém múltiplas **Instituições Financeiras** (tb_inst_instituicao)
- **Instituição Financeira** → possui **Reserva** (tb_rese_reserva) e múltiplas **Unidades Organizacionais** (tb_unor_unidade_org)
- **Unidade Organizacional** → estrutura hierárquica (auto-relacionamento pai-filho)
- **Unidade Organizacional** ↔ **Perfil** (tb_perf_perfil) via tb_cz_unor_perf (N:N)
- **Usuário** (tb_usua_usuario) → vinculado a **Instituição**, **Unidade Organizacional** e **Perfil**
- **Perfil** ↔ **Operação** (tb_oper_operacao) via tb_asop_acesso_operacao com níveis de acesso (tb_nias)
- **Perfil** ↔ **Programa** (tb_prog_programa) via tb_aspr_acesso_programa
- **Operação** → pertence a **Grupo de Serviço** (tb_grse_grupo_servico) e **Subgrupo** (tb_sgse_subgrupo_servico)
- **Operação** ↔ **Mensagem BACEN** (tb_msbc_mensagem_bacen)
- **Cliente Instituição** (tb_clin_cliente_instituicao) ↔ **Operação** via tb_cz_clin_oper
- **Cliente Instituição** → possui **Prioridade** (tb_prio_prioridade) e restrições operacionais
- **Instituição Mercado** (tb_inme_instituicao_mercado) → instituições não-bancárias
- **Alçada** (tb_alca_alcada) ↔ **Transação** via tb_altr_alcada_transacao
- **Reserva** → possui **Ranges** (tb_cz_rese_stre) com **Situação** (tb_stre_situacao_reserva) e **Tipo** (tb_tpre_tipo_reserva)
- **Previsão/Provisão** (tb_pepo_previsao_provisao) → vinculada a Holding/Instituição/Unidade Org
- **Movimento** (tb_movi_movimento) → relacionado a múltiplas tabelas específicas por tipo de mensagem
- **Segregação Perfil** (tb_sgpe_segregacao_perfil) → controla visibilidade de **Atributos BACEN** (tb_atbc_atributo_bacen) por perfil

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| tb_alca_alcada | tabela | SELECT | Alçadas (limites de valores) |
| tb_altr_alcada_transacao | tabela | SELECT | Alçadas por transação |
| tb_grms_grupo_mensagem | tabela | SELECT | Grupos de mensagens |
| tb_cz_clin_oper | tabela | SELECT | Relacionamento cliente-operação |
| tb_oper_operacao | tabela | SELECT | Operações do sistema |
| tb_grse_grupo_servico | tabela | SELECT | Grupos de serviço |
| tb_movi_movimento | tabela | SELECT | Movimentos/mensagens |
| tb_erms_erro_mensagem | tabela | SELECT | Erros de mensagens |
| tb_cder_codigo_erro | tabela | SELECT | Códigos de erro |
| tb_pmge_parametro_geral | tabela | SELECT | Parâmetros gerais do sistema |
| tb_pepo_previsao_provisao | tabela | SELECT | Previsões/provisões financeiras |
| tb_inst_instituicao | tabela | SELECT | Instituições financeiras |
| tb_unor_unidade_org | tabela | SELECT | Unidades organizacionais |
| tb_stop_situacao_operacao | tabela | SELECT | Situações de operação |
| tb_msbc_mensagem_bacen | tabela | SELECT | Mensagens BACEN |
| tb_hold_holding | tabela | SELECT | Holdings |
| tb_rese_reserva | tabela | SELECT | Reservas |
| tb_ispb | tabela | SELECT | Participantes SPB (ISPB) |
| tb_inme_instituicao_mercado | tabela | SELECT | Instituições de mercado |
| tb_rtco_roteiro_contabil | tabela | SELECT | Roteiros contábeis |
| tb_usua_usuario | tabela | SELECT | Usuários |
| tb_perf_perfil | tabela | SELECT | Perfis de acesso |
| tb_prog_programa | tabela | SELECT | Programas (menu/telas) |
| tb_sgpe_segregacao_perfil | tabela | SELECT | Segregação de perfis |
| tb_pmce_prmtro_controle_envio | tabela | SELECT | Parâmetros controle envio |
| tb_pmmp_prmtro_montante_prdo | tabela | SELECT | Parâmetros montante período |
| tb_nias | tabela | SELECT | Níveis de acesso |
| tb_asop_acesso_operacao | tabela | SELECT | Acessos operação |
| tb_aspr_acesso_programa | tabela | SELECT | Acessos programa |
| tb_cz_unor_perf | tabela | SELECT | Relacionamento unidade-perfil |
| tb_prio_prioridade | tabela | SELECT | Prioridades |
| tb_clin_cliente_instituicao | tabela | SELECT | Clientes institucionais |
| tb_cz_rese_stre | tabela | SELECT | Ranges de reserva |
| tb_stre_situacao_reserva | tabela | SELECT | Situações de reserva |
| tb_tpre_tipo_reserva | tabela | SELECT | Tipos de reserva |
| tb_mvsr_movimento_str_ctg | tabela | SELECT | Movimentos STR contingência |
| tb_coan_contabil_analitico | tabela | SELECT | Contábil analítico |
| tb_pmco_parametro_contabil | tabela | SELECT | Parâmetros contábeis |
| tb_lame_layout_mensagem | tabela | SELECT | Layout de mensagens |
| tb_atbc_atributo_bacen | tabela | SELECT | Atributos BACEN |
| tb_atin_atributo_instituicao | tabela | SELECT | Atributos instituição |
| tb_sgse_subgrupo_servico | tabela | SELECT | Subgrupos de serviço |
| tb_doat_dominio_atributo | tabela | SELECT | Domínio de atributos |
| vw_mvsr_movimento_str_ctg | view | SELECT | View movimentos STR contingência |
| tb_mvgn_movimento_gen | tabela | SELECT | Movimentos GEN (avisos) |
| tb_mvbmc_movimento_bmc | tabela | SELECT | Movimentos BMC |
| tb_mvcbl_movimento_cbl | tabela | SELECT | Movimentos CBL |
| tb_mvcir_movimento_cir | tabela | SELECT | Movimentos CIR |
| tb_mvctp_movimento_ctp | tabela | SELECT | Movimentos CTP |
| tb_mvldl_movimento_ldl | tabela | SELECT | Movimentos LDL |
| tb_mvltr_movimento_ltr | tabela | SELECT | Movimentos LTR |
| tb_mvpag_movimento_pag | tabela | SELECT | Movimentos PAG |
| tb_mvrco_movimento_rco | tabela | SELECT | Movimentos RCO |
| tb_mvrdc_movimento_rdc | tabela | SELECT | Movimentos RDC |
| tb_mvsel_movimento_sel | tabela | SELECT | Movimentos SEL |
| tb_mvslb_movimento_slb | tabela | SELECT | Movimentos SLB |
| tb_mvstn_movimento_stn | tabela | SELECT | Movimentos STN |
| tb_mvtes_movimento_tes | tabela | SELECT | Movimentos TES |
| tb_mvsr_movimento_str | tabela | SELECT | Movimentos STR |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| tb_alca_alcada | tabela | INSERT/UPDATE/DELETE | Alçadas (limites de valores) |
| tb_altr_alcada_transacao | tabela | INSERT/UPDATE/DELETE | Alçadas por transação |
| tb_grms_grupo_mensagem | tabela | UPDATE | Grupos de mensagens (flag alçada) |
| tb_cz_clin_oper | tabela | INSERT/UPDATE/DELETE | Relacionamento cliente-operação |
| tb_grse_grupo_servico | tabela | INSERT/UPDATE/DELETE | Grupos de serviço |
| tb_hold_holding | tabela | INSERT/UPDATE/DELETE | Holdings |
| tb_inst_instituicao | tabela | INSERT/UPDATE/DELETE | Instituições financeiras |
| tb_rese_reserva | tabela | INSERT/UPDATE/DELETE | Reservas |
| tb_inme_instituicao_mercado | tabela | INSERT/UPDATE/DELETE | Instituições de mercado |
| tb_oper_operacao | tabela | INSERT/UPDATE/DELETE | Operações do sistema |
| tb_pmce_prmtro_controle_envio | tabela | UPDATE | Parâmetros controle envio |
| tb_pmmp_prmtro_montante_prdo | tabela | UPDATE | Parâmetros montante período |
| tb_ispb | tabela | UPDATE | Participantes SPB (ISPB) |
| tb_perf_perfil | tabela | INSERT/UPDATE/DELETE | Perfis de acesso |
| tb_cz_unor_perf | tabela | INSERT/DELETE | Relacionamento unidade-perfil |
| tb_asop_acesso_operacao | tabela | INSERT/DELETE | Acessos operação |
| tb_pmge_parametro_geral | tabela | UPDATE | Parâmetros gerais do sistema |
| tb_pepo_previsao_provisao | tabela | INSERT/UPDATE/DELETE | Previsões/provisões financeiras |
| tb_prio_prioridade | tabela | INSERT/UPDATE/DELETE | Prioridades |
| tb_prog_programa | tabela | INSERT/UPDATE/DELETE | Programas (menu/telas) |
| tb_cz_rese_stre | tabela | INSERT/UPDATE/DELETE | Ranges de reserva |
| tb_usua_usuario | tabela | INSERT/UPDATE/DELETE | Usuários |
| tb_clin_cliente_instituicao | tabela | INSERT/UPDATE/DELETE | Clientes institucionais |
| tb_rtco_roteiro_contabil | tabela | INSERT | Roteiros contábeis |
| tb_sgpe_segregacao_perfil | tabela | INSERT/DELETE | Segregação de perfis |
| tb_stre_situacao_reserva | tabela | INSERT/UPDATE/DELETE | Situações de reserva |
| tb_unor_unidade_org | tabela | INSERT/UPDATE/DELETE | Unidades organizacionais |
| TbArquivoInterfaceContabil | tabela | INSERT | Arquivo interface contábil (nome exato não especificado) |
| Tabelas temporárias de acesso | tabela | CREATE/DROP/INSERT | Tabelas temp para processamento acessos perfil-operação |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application*.yml | leitura | Spring Boot Config | Configurações por ambiente (datasource, OAuth2, logging) |
| openapi.yaml | leitura | OpenAPI Generator | Especificação OpenAPI 3.0 da API |
| logback-spring.xml | leitura | Logback | Configuração de logs (formato JSON, async) |
| roles/*.yml | leitura | Security Config | Mapeamento de roles AD por ambiente |
| lombok.config | leitura | Lombok | Configurações Lombok |
| pom.xml | leitura | Maven | Dependências e build |
| infra-as-code/infra.yml | leitura | Kubernetes | Manifesto K8s (secrets, configmaps, probes) |
| Dockerfile | leitura | Docker | Imagem Java 11 |
| jenkins.properties | leitura | Jenkins | Configurações CI/CD |
| Logs JSON | gravação | Logback/Application | Logs estruturados da aplicação |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **BACEN (Banco Central)** | Mensageria SPB | Integração com mensagens do Sistema de Pagamentos Brasileiro (BMC, CBL, CIR, CTP, GEN, LDL, LTR, PAG, RCO, RDC, SEL, SLB, STN, TES, STR) |
| **LDAP/Active Directory** | Autenticação | Autenticação de usuários via LDAP e mapeamento de grupos AD |
| **OAuth2 Provider** | Autorização | Validação de tokens JWT via JWKS |
| **Sistema Legado SGIR** | Integração | Referências a sistema legado (contexto não detalhado) |
| **Prometheus** | Métricas | Exportação de métricas via Micrometer |
| **Grafana** | Monitoramento | Dashboards de monitoramento |
| **Sybase ASE** | Banco de Dados | Banco de dados principal (jdbc:sybase) |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 8/10

**Justificativa:**

**Pontos Positivos:**
- Excelente separação de responsabilidades em camadas (Controller/Service/Repository/Mapper/DTO)
- Uso consistente de padrões de projeto (Delegate, Repository, Service)
- Boa utilização de ferramentas modernas (Lombok, MapStruct, JDBI3)
- Código bem estruturado e organizado por domínio
- Validações de regras de negócio implementadas nos services
- Tratamento de exceções customizadas (BusinessException, RegraNegocioException)
- Logs estruturados em JSON para facilitar análise
- Testes unitários abrangentes com Mockito
- Documentação OpenAPI completa
- Auditoria integrada via trilha-auditoria-web
- Configurações externalizadas por ambiente

**Pontos de Melhoria:**
- Alguns métodos de repository com queries SQL hardcoded muito longas (dificulta manutenção)
- Falta de documentação inline (JavaDoc) em algumas classes
- Alguns services com múltiplas responsabilidades (ex: PerfilOperacaoService com lógica de tabelas temporárias)
- Validações de negócio poderiam estar mais centralizadas
- Alguns nomes de tabelas e campos pouco descritivos (ex: tb_cz_*, siglas não documentadas)
- Ausência de testes de integração
- Falta de cache para consultas frequentes (ex: parâmetros gerais)

---

## 14. Observações Relevantes

1. **Modelo de Dados Complexo**: Sistema possui mais de 50 tabelas com relacionamentos complexos, refletindo a complexidade do domínio SPB
2. **Segurança Multicamadas**: Implementa segurança em múltiplos níveis (OAuth2, perfis, segregação de campos, alçadas)
3. **Auditoria Completa**: Todas as operações são auditadas via trilha-auditoria-web
4. **Suporte a Contingência**: Sistema possui estruturas específicas para operação em modo contingência (STR)
5. **Integração BACEN**: Forte integração com mensagens do Sistema de Pagamentos Brasileiro (15+ tipos de mensagens)
6. **Multitenancy**: Suporte a múltiplas holdings, instituições e unidades organizacionais
7. **Controle Granular de Acesso**: Sistema de permissões baseado em perfil-operação-ação com 5 níveis (consultar/incluir/alterar/excluir/confirmar)
8. **Validações Rigorosas**: Múltiplas validações de integridade e regras de negócio antes de persistência
9. **Configuração por Ambiente**: Suporte a múltiplos ambientes (local/des/qa/uat/prd) com configurações específicas
10. **Observabilidade**: Métricas Prometheus, logs estruturados JSON, health checks Kubernetes
11. **Padrão de Nomenclatura**: Tabelas seguem padrão tb_XXXX_nome_completo (4 letras + nome)
12. **Uso de Views**: Sistema utiliza views para consultas complexas (ex: vw_mvsr_movimento_str_ctg)
13. **Auto-incremento Manual**: Alguns sequenciais são gerenciados manualmente via MAX+1 (ex: previsões/provisões)
14. **Tabelas Temporárias**: Uso de tabelas temporárias para processamento de acessos perfil-operação
15. **Versionamento**: Sistema está na versão 0.12.0, indicando maturidade em desenvolvimento

---