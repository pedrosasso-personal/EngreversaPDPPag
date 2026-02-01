# Ficha Técnica do Sistema

## 1. Descrição Geral

O **springboot-spag-base-gestao** é um sistema backend REST API desenvolvido em Spring Boot para gestão e controle de operações do SPAG (Sistema de Pagamentos). O sistema gerencia o ciclo completo de pagamentos, incluindo cadastro de fintechs/wallets, processamento de lançamentos manuais e automáticos, contingência de boletos, reconciliação de arquivos RCO (Registro Controle Operacional), dashboards de transações financeiras, zeragem de contas pagamento, gestão de tributos e múltiplas integrações com sistemas externos (SITP, Global, parceiros fintech).

A aplicação suporta operações críticas como validação de alçadas de aprovação, controle de status de lançamentos, processamento batch de arquivos posicionais, notificações via mensageria (IBM MQ e RabbitMQ), callbacks para parceiros e gestão de contas de usuários fintech com controle de bloqueio/desbloqueio/encerramento.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **FintechService** | Gestão completa de fintechs: cadastro, atualização, inativação, controle de múltiplas contas (wallet), validação CNPJ, integração SITP/Global, notificações PIX |
| **ContigenciaService** | Inclusão e aprovação de lançamentos manuais/contingência, validação de alçadas, controle de duplicidade (NSU, protocolo), tratamento TED Out |
| **RcoService** | Processamento de arquivos RCO: parse layout posicional (FFPojo), validação estrutura, cálculo tarifas, controle status, integração movimentos SPB |
| **DashboardSaService** | Consultas dashboard operações SA: resumos e detalhes de TED, DOC, TEF, Boletos, Tributos, Transferências, Saques, Compras Cartões com paginação |
| **DashboardService** | Dashboard específico de tributos por fintech/banco/período |
| **UsuarioFintechService** | Gestão ciclo de vida de contas usuário fintech: abertura, confirmação, bloqueio/desbloqueio, encerramento, validações KMV, callbacks parceiro |
| **ZeragemCpService** | Gestão de zeragem de Contas Pagamento: parametrização, validação data referência, controle tipos zeragem (Automática/Manual/Resgate) |
| **AlcadaService** | Validação de alçadas de aprovação por perfil usuário e valor de lançamento, cache de perfis |
| **ArrecadadorService** | Gestão de cadastro de arrecadadores e parâmetros de pagamento |
| **LancamentoService** | Operações sobre lançamentos: atualização de devoluções, consulta códigos status |
| **FilaMQService / FilaRabbitService** | Envio de mensagens de notificação/confirmação de pagamento para filas IBM MQ e RabbitMQ |
| **GatewayRepository** | Integração OAuth2 com Gateway externo para validação de operações fintech (abertura conta, bloqueio, encerramento) |
| **SitpRepository** | Integração com SITP para replicação de origens de pagamento e consulta de bancos ativos CIP |
| **GlobalRepository** | Integração com sistema Global para obtenção de clientId por documento |
| **ContaFintechRepository** | Gerenciamento de contas usuário fintech: CRUD, validações de titular único, geração de protocolos SHA-256 |
| **FintechRepository** | CRUD completo de fintechs: cadastro multi-tabela transacional, gestão logos, múltiplas contas pagamento, controle migração participante |
| **DashboardBvSaRepository** | Consultas complexas de dashboard com joins múltiplos, filtros por banco/status/tipo lançamento, consolidação de valores |
| **MonitorRepository** | Consultas para monitoramento operacional: notificações cash-in, status lançamentos, tributos, contas fintech |
| **IncluirLancamentoProcedure** | Execução de stored procedure para inclusão de lançamentos com 80+ parâmetros |

---

## 3. Tecnologias Utilizadas

- **Framework:** Spring Boot 2.7.18, Spring Security 5.7.12+, Spring JDBC
- **Linguagem:** Java 8 (OpenJDK 8 com OpenJ9)
- **Banco de Dados:** Microsoft SQL Server (JDBC direto, sem JPA/Hibernate)
- **Mensageria:** RabbitMQ, IBM MQ (JMS)
- **Build:** Gradle 7.5.1
- **Containerização:** Docker, Kubernetes/OpenShift
- **Logs:** Logback (formato JSON estruturado)
- **Documentação API:** Swagger/OpenAPI 3.0
- **Testes:** JUnit 4/5, Mockito, Jacoco (cobertura)
- **Qualidade Código:** SonarQube
- **Feature Toggles:** ConfigCat
- **Parsing Arquivos:** FFPojo (arquivos posicionais RCO)
- **HTTP Client:** Apache HttpClient, RestTemplate
- **Serialização:** Jackson, JAXB
- **Utilitários:** Lombok, Apache Commons, Guava, ESAPI (sanitização)
- **Segurança:** Spring Security (LDAP), OAuth2, mTLS (toggle)
- **Cache:** Spring Cache (ConcurrentMapCache)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| **Fintech** ||||
| GET | /fintech/listar | FintechApi | Listar fintechs cadastradas |
| GET | /fintech/buscar/{filtro} | FintechApi | Buscar fintech por filtro |
| POST | /fintech/cadastrar | FintechApi | Cadastrar nova fintech |
| PUT | /fintech/atualizar | FintechApi | Atualizar dados fintech |
| PUT | /fintech/atualizarFintech | FintechApi | Desativar fintech |
| POST | /fintech/notificacao-pix | FintechApi | Obter dados notificação PIX |
| **Dashboard SA** ||||
| GET | /dashboard-bvsa/resumo | DashboardBvSaApi | Resumo utilização operações |
| GET | /dashboard-bvsa/detalhes/ted-pagamentos | DashboardBvSaApi | Detalhes pagamentos TED |
| GET | /dashboard-bvsa/detalhes/boletos | DashboardBvSaApi | Detalhes pagamentos boletos |
| GET | /dashboard-bvsa/detalhes/tributos | DashboardBvSaApi | Detalhes tributos liquidados |
| **Dashboard Tributos** ||||
| GET | /dashboard/detalhes/tributos | DashboardApi | Detalhes tributos por fintech |
| GET | /dashboard/dash/tributos | DashboardApi | Resumo tributos |
| POST | /dashboard/reenvio-protocolos | DashboardApi | Reenvio protocolos MQ |
| POST | /dashboard/reenvio-protocolos-rabbit | DashboardApi | Reenvio protocolos RabbitMQ |
| **RCO** ||||
| POST | /rco/upload | RcoApi | Upload arquivo RCO |
| GET | /rco/buscar-arquivos | RcoApi | Buscar arquivos RCO |
| GET | /rco/detalhes-analiticos/{id} | RcoApi | Registros analíticos arquivo |
| GET | /rco/detalhes-consolidado/{id} | RcoApi | Registros consolidados arquivo |
| PUT | /rco/rejeitar/{cdArquivo} | RcoApi | Rejeitar arquivo RCO |
| POST | /rco/incluir-lancamento | RcoApi | Incluir lançamento RCO |
| **Contingência** ||||
| POST | /contigencia/incluir-lancamento | ContigenciaApi | Incluir lançamento manual |
| GET | /contigencia/lancamento/{cdLancamento} | ContigenciaApi | Detalhes lançamento |
| PUT | /contigencia/atualizar-lancamento/{cdStatusAlcada} | ContigenciaApi | Atualizar lançamento |
| PUT | /contigencia/lancamento-acao | ContigenciaApi | Aprovar/cancelar lançamento |
| **Usuário Fintech** ||||
| POST | /usuario-fintech/cadastrar-conta | UsuarioFintechApi | Cadastrar conta usuário |
| PUT | /usuario-fintech/bloquear-desbloquear-conta | UsuarioFintechApi | Bloquear/desbloquear conta |
| PUT | /usuario-fintech/encerramento-conta | UsuarioFintechApi | Encerrar conta usuário |
| **Zeragem CP** ||||
| POST | /zeragem-cp/inserir-registro | ZeragemCpApi | Inserir registro zeragem |
| POST | /zeragem-cp/inserir-parametrizacao | ZeragemCpApi | Inserir parametrização |
| GET | /zeragem-cp/consultar-zeragem/{id} | ZeragemCpApi | Consultar zeragem por ID |
| PUT | /zeragem-cp/atualizar-zeragem/{id} | ZeragemCpApi | Atualizar registro zeragem |
| GET | /zeragem-cp/listar-paginado-zeragem | ZeragemCpApi | Listar zeragens paginado |
| **Lançamento** ||||
| PUT | /lancamento/atualizar-lancamento-devolvido | LancamentoApi | Atualizar lançamento devolvido |
| GET | /lancamento/codigo-status | LancamentoApi | Códigos status lançamento |
| **Monitor** ||||
| GET | /monitor/consultar-operacao/{cdOperacao} | MonitorApi | Consultar operação por código |
| **Arrecadador** ||||
| GET | /arrecadador | ArrecadadorApi | Listar arrecadadores |
| PUT | /arrecadador/parametro-pagamento | ArrecadadorApi | Atualizar parâmetros arrecadador |
| **Cancelamento** ||||
| PUT | /cancelamento-lancamento | CancelamentoLancamentoApi | Cancelar lançamentos em lote |
| **Reprocessamento** ||||
| POST | /reprocessamento-pagamento/enviar-esteira | ReprocessamentoPagamentoApi | Reprocessar pagamentos |

---

## 5. Principais Regras de Negócio

1. **Validação de Alçadas**: Lançamentos acima de determinado valor requerem aprovação por perfil específico (TESOURARIA, CAMBIO, COBRANCA). Sistema valida se aprovador possui alçada suficiente e se não é o mesmo usuário inclusor.

2. **Controle de Duplicidade**: Validação de lançamentos duplicados por múltiplos critérios: NSU (NuProtocoloSolicitacaoCliente), protocolo interno, combinação conta+valor+data+tipo operação.

3. **Gestão Status Lançamentos**: Controle de ciclo de vida com status: Pendente Aprovação, Aprovado (0), Cancelado (4), Rejeitado, Devolvido, Em Processamento, Processado com Sucesso.

4. **Arquivo RCO**: Parse de arquivo posicional SPB com validação de estrutura (header/detalhe/trailer), cálculo de tarifas, validação de totalizadores, controle de duplicidade por banco+data, processamento batch de 100 registros por lote.

5. **Zeragem CP**: Validação de data referência única por conta, controle de tipos (Automática/Manual/Resgate), validação de valores conta CP, parametrização por fintech com aprovação/reprovação.

6. **Contingência Boletos**: Validação de valores mínimos/máximos CIP, controle de flags de validação/contingência, tratamento específico para código liquidação 46 (STN), validação de datas de vencimento.

7. **Gestão Fintech**: Validação de CNPJ único, conta base única, código origem PGFT, distinção Wallet vs Fintech tradicional, controle de migração participante (entrada/saída SPAG), sincronização com SITP para origens de pagamento.

8. **Conta Usuário Fintech**: Validação de titular único por conta, controle de status (Pre-Cadastro, Aberta, Bloqueio, Encerrada), geração de protocolo SHA-256, callbacks para parceiro após operações, validação de período vigência, suporte mTLS para autenticação.

9. **Dashboard Transações**: Consolidação de valores por status (Enviadas, Em Processamento, Processadas com Sucesso, Recusadas), filtros por banco (Votorantim/BVSA), tipo lançamento (Entrada/Saída), código liquidação, paginação de grandes volumes.

10. **Notificações**: Envio de mensagens para filas IBM MQ e RabbitMQ conforme status de tributo (A-Aprovado, E-Em Processamento, P-Processado), suporte a diferentes tipos de mensagem (CashIn, CashOut, Callback).

11. **Reprocessamento**: Busca de lançamentos por protocolo, validação de status elegível para reprocessamento, envio para esteira de pagamento com retry automático (máximo 5 tentativas).

12. **Funcionalidades Parceiro**: Controle de habilitação/desabilitação de funcionalidades por parceiro com fluxo de solicitação e aprovação, validação por código liquidação e finalidade.

---

## 6. Relação entre Entidades

### Entidades Principais e Relacionamentos:

**TbParametroPagamentoFintech** (Fintech)
- 1:N → TbOrigemPagamento (origens de pagamento)
- 1:N → TbContaPagamentoFintech (contas pagamento)
- 1:N → TbOrigemPagamentoMultiplaConta (contas wallet)
- 1:N → TbParametroImagemFintech (logos)
- 1:1 → TbControleMigracaoParticipante (migração)
- 1:N → TbControleTipoNotificacao (notificações PIX)

**TbContaUsuarioFintech** (Conta Usuário)
- N:1 → TbParametroPagamentoFintech (fintech)
- 1:N → TbRelacaoContaUsuarioFintech (relações usuário-conta)
- N:1 → TbStatusContaFintech (status)
- 1:N → TbControleAcaoAplicacao (protocolos operações)

**TbRelacaoContaUsuarioFintech** (Relação Usuário-Conta)
- N:1 → TbContaUsuarioFintech (conta)
- N:1 → TbUsuarioContaFintech (usuário)
- N:1 → TbTipoVinculoConta (tipo vínculo: titular/co-titular)

**TbLancamento** (Lançamento)
- N:1 → TbStatusLancamento (status)
- 1:1 → TbLancamentoPessoa (dados remetente/favorecido)
- 1:1 → TbLancamentoClienteFintech (dados fintech)
- 1:1 → TbBoleto (dados boleto, se aplicável)
- 1:1 → TbTributo (dados tributo, se aplicável)
- N:1 → TbParametroPagamentoFintech (fintech origem)

**TbArquivoRCO** (Arquivo RCO)
- 1:N → TbDetalheArquivoRCO (detalhes registros)
- N:1 → TbParametroRCO (parâmetros tarifa)

**TbZeragemCp** (Zeragem CP)
- N:1 → TbParametrizacaoCp (parametrização)
- N:1 → TbParametroPagamentoFintech (fintech)

**TbArrecadador** (Arrecadador)
- 1:1 → TbParametroPgmnoArrecadador (parâmetros pagamento)

**TbControleFuncionalidadeParceiro** (Funcionalidade Parceiro)
- N:1 → TbParametroPagamentoFintech (parceiro)
- N:1 → TbTipoFuncionalidade (funcionalidade)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View | Tipo | Operação | Breve Descrição |
|---------------------|------|----------|-----------------|
| TbParametroPagamentoFintech | Tabela | SELECT | Dados cadastrais fintechs/wallets |
| TbContaPagamentoFintech | Tabela | SELECT | Contas pagamento fintechs |
| TbOrigemPagamento | Tabela | SELECT | Origens pagamento (TED, DOC, Tributo) |
| TbOrigemPagamentoMultiplaConta | Tabela | SELECT | Contas múltiplas (wallet) |
| TbContaUsuarioFintech | Tabela | SELECT | Contas usuários fintech |
| TbUsuarioContaFintech | Tabela | SELECT | Usuários fintech |
| TbRelacaoContaUsuarioFintech | Tabela | SELECT | Relacionamento usuário-conta |
| TbStatusContaFintech | Tabela | SELECT | Status contas fintech |
| TbLancamento | Tabela | SELECT | Lançamentos financeiros |
| TbLancamentoPessoa | Tabela | SELECT | Dados remetente/favorecido |
| TbLancamentoClienteFintech | Tabela | SELECT | Dados fintech lançamento |
| TbStatusLancamento | Tabela | SELECT | Status lançamentos |
| TbBoleto | Tabela | SELECT | Dados boletos |
| TbTributo | Tabela | SELECT | Dados tributos |
| TbArquivoRCO | Tabela | SELECT | Arquivos RCO processados |
| TbDetalheArquivoRCO | Tabela | SELECT | Detalhes registros RCO |
| TbParametroRCO | Tabela | SELECT | Parâmetros tarifa RCO |
| TbZeragemCp | Tabela | SELECT | Registros zeragem CP |
| TbParametrizacaoCp | Tabela | SELECT | Parametrização zeragem CP |
| TbArrecadador | Tabela | SELECT | Cadastro arrecadadores |
| TbParametroPgmnoArrecadador | Tabela | SELECT | Parâmetros arrecadadores |
| TbParametroPagamentoTributo | Tabela | SELECT | Parâmetros tributos |
| TbParametroInterfaceCIP | Tabela | SELECT | Parâmetros contingência CIP |
| TbAlcadaAprovacao | Tabela | SELECT | Alçadas aprovação por perfil |
| TbControleFuncionalidadeParceiro | Tabela | SELECT | Funcionalidades parceiros |
| TbTipoFuncionalidade | Tabela | SELECT | Tipos funcionalidades |
| TbParametroImagemFintech | Tabela | SELECT | Logos fintechs |
| TbControleMigracaoParticipante | Tabela | SELECT | Controle migração SPAG |
| TbControleTipoNotificacao | Tabela | SELECT | Tipos notificação PIX |
| TbNotificacaoFintech | Tabela | SELECT | Notificações cash-in |
| TbControleRetornoNotificacao | Tabela | SELECT | Retornos notificações |
| TbErroProcessamento | Tabela | SELECT | Erros processamento |
| TbDetalheFornecedorLote | Tabela | SELECT | Detalhes fornecedor lote |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View | Tipo | Operação | Breve Descrição |
|---------------------|------|----------|-----------------|
| TbParametroPagamentoFintech | Tabela | INSERT/UPDATE | Cadastro/atualização fintechs |
| TbOrigemPagamento | Tabela | INSERT/UPDATE | Inclusão/atualização origens pagamento |
| TbOrigemPagamentoMultiplaConta | Tabela | INSERT/UPDATE/DELETE | Gestão contas wallet |
| TbContaPagamentoFintech | Tabela | INSERT | Cadastro contas pagamento |
| TbParametroImagemFintech | Tabela | INSERT/UPDATE | Gestão logos fintechs |
| TbControleMigracaoParticipante | Tabela | INSERT/UPDATE | Controle migração participante |
| TbControleTipoNotificacao | Tabela | INSERT/UPDATE | Tipos mensagem notificação |
| TbContaUsuarioFintech | Tabela | INSERT/UPDATE | Cadastro/atualização contas usuário |
| TbUsuarioContaFintech | Tabela | INSERT/UPDATE | Cadastro/atualização usuários |
| TbRelacaoContaUsuarioFintech | Tabela | INSERT/UPDATE | Relacionamento usuário-conta |
| TbControleAcaoAplicacao | Tabela | INSERT | Protocolos operações conta |
| TbLancamento | Tabela | INSERT/UPDATE | Inclusão/atualização lançamentos |
| TbLancamentoManual | Tabela | INSERT/UPDATE | Lançamentos manuais contingência |
| TbLancamentoManualBoleto | Tabela | INSERT | Dados boleto lançamento manual |
| TbLancamentoManualLog | Tabela | INSERT | Log alterações lançamentos |
| TbArquivoRCO | Tabela | INSERT/UPDATE | Upload/atualização arquivos RCO |
| TbDetalheArquivoRCO | Tabela | INSERT/UPDATE | Detalhes registros RCO (batch) |
| TbParametroRCO | Tabela | INSERT/UPDATE | Parâmetros tarifa RCO |
| TbZeragemCp | Tabela | INSERT/UPDATE | Registros zeragem CP |
| TbParametrizacaoCp | Tabela | INSERT/UPDATE/DELETE | Parametrização zeragem CP |
| TbArrecadador | Tabela | INSERT/UPDATE | Cadastro arrecadadores |
| TbParametroPgmnoArrecadador | Tabela | INSERT/UPDATE | Parâmetros arrecadadores |
| TbParametroPagamentoTributo | Tabela | UPDATE | Atualização parâmetros tributos |
| TbParametroInterfaceCIP | Tabela | UPDATE | Atualização parâmetros CIP |
| TbControleFuncionalidadeParceiro | Tabela | INSERT/UPDATE | Solicitação/aprovação funcionalidades |
| TbLogOgmPagamentoMultiplaConta | Tabela | INSERT | Log operações múltiplas contas |
| TbLogParametroPagamentoTributo | Tabela | INSERT | Log alterações parâmetros tributos |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| Arquivo RCO (formato posicional SPB) | Leitura | RcoService, LeituraArquivoRcoService | Parse arquivo RCO com layout header/detalhe/trailer, validação estrutura, extração dados movimentação bancária |
| Logs aplicação (JSON) | Gravação | Logback (logback-spring.xml) | Logs estruturados JSON com contexto ticket/fase, nível INFO, console appender |
| Anexos usuário fintech | Leitura | GestaoControleAtacadoService, GatewayRepository | Busca anexos documentação usuário via API Gateway |

---

## 10. Filas Lidas

| Nome da Fila | Tecnologia | Classe Responsável | Breve Descrição |
|--------------|------------|-------------------|-----------------|
| não se aplica | - | - | Sistema não consome mensagens de filas (apenas publica) |

---

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Responsável | Breve Descrição |
|--------------|------------|-------------------|-----------------|
| TB_SPAG_NOTIFICA_PGMNO_TRIBUTO | IBM MQ | FilaMQService, MqNotificacaoService | Notificações confirmação/pagamento tributos (status A/E/P) |
| Fila pagamento (configurável) | IBM MQ | MqPagamentoService | Mensagens pagamento |
| SPAG.notificacoes.notificacaoSpag | RabbitMQ | FilaRabbitService, NotificacaoSpagRepository | Notificações pagamento SPAG (status E/P), exchange: SPAG.notificacoes |
| SPAG.esteiraPagamento | RabbitMQ | ReprocessamentoPagamentoRepository | Reprocessamento pagamentos, routing keys dinâmicas: SPAG.esteiraPagamentoOk.{cdOrigem}, SPAG.esteiraPagamentoErro.{cdOrigem} |

---

## 12. Integrações Externas

| Sistema/API | Tipo | Classe Responsável | Breve Descrição |
|-------------|------|-------------------|-----------------|
| **SITP (Sistema Integração Transações Pagamento)** | REST | SitpRepository | Replicação origens pagamento (incluir/atualizar/excluir), consulta bancos ativos CIP |
| **Global (Sistema Cliente)** | REST | GlobalRepository | Obtenção clientId por documento (CPF/CNPJ), autenticação Basic/OAuth |
| **Gateway Fintech (OAuth2)** | REST | GatewayRepository | Validação operações fintech (abertura conta, bloqueio, encerramento), busca dados cliente PF/PJ, gestão token OAuth2 com cache, retry automático (max 5 tentativas) |
| **APIs Fintechs (Callbacks)** | REST | ContaFintechRepository, FintechRepository | Callbacks para parceiros: solicitação/validação/retorno pagamento, notificações, busca usuário/anexos, confirmação abertura/bloqueio/encerramento conta, suporte mTLS (toggle) |
| **APIs Arrecadadores** | REST | ArrecadadorRepository | Consulta/confirmação/efetivação pagamento, lista/arquivo conciliação |
| **Esteira Pagamento** | REST | ReprocessamentoPagamentoRepository | Reenvio pagamentos para reprocessamento |
| **API ITP (Consulta Movimentos RCO)** | REST | ConsultaMovimentoRcoRepository | Consulta movimentos RCO para reconciliação |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Separação clara de camadas (API/Service/Repository) seguindo boas práticas arquiteturais
- Uso adequado de DTOs para transferência de dados entre camadas
- Lombok reduz significativamente boilerplate
- Cobertura de testes unitários razoável com Mockito/JUnit
- Validações de entrada com Bean Validation (JSR-303)
- Tratamento de exceções centralizado com ControllerAdvice
- Feature toggles (ConfigCat) para controle de funcionalidades
- Logs estruturados em JSON
- Configuração multi-ambiente (dev/hom/prd)
- Documentação Swagger/OpenAPI
- Uso de patterns (Repository, DTO, Builder, Factory)
- Segurança com Spring Security, OAuth2, mTLS

**Pontos de Melhoria:**
- **Classes extensas**: Algumas classes de serviço ultrapassam 800 linhas (DashboardSaService, FintechService), violando princípio SRP (Single Responsibility Principle)
- **Métodos longos**: Métodos complexos com múltiplas responsabilidades necessitam refatoração
- **Duplicação de código**: Validações similares repetidas em múltiplos pontos
- **Acoplamento**: Alto acoplamento entre algumas classes de serviço
- **Comentários escassos**: Lógicas complexas de negócio carecem de documentação inline
- **Magic numbers/strings**: Constantes literais espalhadas pelo código (devem ser centralizadas)
- **Queries SQL**: Strings literais em XML (considerar QueryDSL ou JPQL para type-safety)
- **Testes de integração**: Limitados comparado aos unitários (necessário expandir)
- **Cache**: Uso básico de cache em memória (considerar Redis para ambientes distribuídos)
- **Observabilidade**: Falta integração com ferramentas de monitoramento (Prometheus, Grafana)

---

## 14. Observações Relevantes

1. **Arquitetura Monolítica Modular**: Aplicação bem estruturada em camadas, mas monolítica. Considerar migração futura para microserviços para melhor escalabilidade.

2. **Domínio Complexo**: Sistema lida com domínio financeiro crítico (pagamentos, contingência, conciliação) com múltiplas regras de negócio e integrações.

3. **Processamento Batch**: Suporte a processamento batch de arquivos RCO com 100 registros por lote, otimizado para performance.

4. **Feature Toggles Críticas**:
   - `ft_boolean_spag_base_mtls_toggle`: Habilita autenticação mTLS para parceiros
   - `ft_string_spag_base_mtls_toggle`: Lista de parceiros com mTLS habilitado

5. **Segurança Robusta**: Implementação de múltiplas camadas de segurança (Spring Security, OAuth2, mTLS, ESAPI sanitização, HTTPS).

6. **Gestão Transacional**: Uso adequado de `@Transactional` para garantir consistência de dados em operações críticas.

7. **Paginação**: Implementação de paginação customizada para consultas de grandes volumes, essencial para performance.

8. **Integração Síncrona/Assíncrona**: Sistema combina integrações REST síncronas com mensageria assíncrona (IBM MQ, RabbitMQ).

9. **Controle de Versão API**: Suporte a versionamento de APIs externas (v2/v3) via feature toggle.

10. **Vulnerabilidades Corrigidas**: Dependências atualizadas para versões seguras (Spring Web 5.3.31-custom_cve, Spring Security 5.7.12+, Jackson 2.15.0+, SnakeYAML 2.0).

11. **Deploy Containerizado**: Aplicação preparada para deploy em Docker/Kubernetes/OpenShift com configurações de probes (liveness/readiness).

12. **Banco de Dados**: Uso de JDBC direto sem ORM (JPA/Hibernate), com stored procedures para operações críticas. Considerar migração para JPA para melhor manutenibilidade.

13. **Gradle Build Avançado**: Pipeline de build com múltiplos estágios (unit/integration/functional tests), análise Jacoco/SonarQube, automação de release.

14. **Necessidade de Refatoração**: Classes grandes e métodos complexos necessitam refatoração urgente para melhorar manutenibilidade e testabilidade.

15. **Documentação**: Necessário expandir documentação técnica (javadoc, README, diagramas arquiteturais) para facilitar onboarding de novos desenvolvedores.