---
## Ficha Técnica do Sistema

### 1. Descrição Geral
Sistema de gestão de movimentações bancárias e bloqueios de conta corrente. Oferece funcionalidades de consulta de extratos, movimentações (incluindo PIX), gerenciamento de bloqueios (crédito, débito e valor), agendamentos, movimentos priorizados e relatórios contábeis. Implementa APIs REST versionadas (v1, v2, v3) com controle transacional manual para operações críticas de bloqueio/desbloqueio. Utiliza arquitetura em camadas com separação clara entre adapter (controllers/repositories), domain (business logic) e application (configuração).

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **MovimentacoesControllerV1** | Controller REST v1 - endpoints movimentações, priorizados e saldos bloqueados |
| **MovimentacoesControllerV2** | Controller REST v2 - endpoints extrato, bloqueios, débitos indevidos, agendamentos, limites |
| **MovimentacoesControllerV3** | Controller REST v3 - evolução endpoints bloqueios e consulta por documento |
| **MovimentacaoPixController** | Controller REST específico para consultas de movimentações PIX |
| **Bloqueio** | Bridge para operações de bloqueio/desbloqueio com controle transacional manual |
| **BloqueioMovimentacoesServiceImpl** | Service principal de bloqueios - orquestra classes de negócio |
| **MovimentacoesServiceV2** | Service principal de movimentações - consultas, extrato, agendamentos |
| **IncluirBloqueioMovimentacoes** | Classe de negócio para inclusão de bloqueios (crédito/débito/valor) |
| **LiberarBloqueioMovimentacoes** | Classe de negócio para liberação de bloqueios com publicação em fila |
| **ExtratoMovimentacoes** | Classe de negócio para geração de extrato com cálculo de saldos |
| **SaldoBloqueadoService** | Service para consulta de saldos bloqueados |
| **MovimentacoesRepository** | Repository JDBI para operações de movimentações |
| **BloqueioMovimentacoesRepository** | Repository JDBI para operações de bloqueios |
| **BloqueiosMonitoradosRepositoryImpl** | Repository para publicação de mensagens de bloqueios monitorados (PubSub) |
| **DadosEntradaValidation** | Validação centralizada de parâmetros de entrada |
| **CategoriaTransacao** | Enum com categorização de transações (TED, TEF, PIX, Boleto, etc) |

### 3. Tecnologias Utilizadas

- **Framework Principal**: Spring Boot 2.x
- **Linguagem**: Java 11
- **Persistência**: JDBI 3.12.0
- **Bancos de Dados**: Sybase (jConnect 7.0), SQL Server (JDBC 7.2.2)
- **Mensageria**: Spring Cloud GCP PubSub 1.2.8, Spring Integration
- **Mapeamento**: MapStruct 1.4.2
- **Segurança**: Spring Security OAuth2 Resource Server, BV Security JWT 0.22.1
- **Documentação API**: Springfox 3.0.0 (Swagger/OpenAPI)
- **Auditoria**: BV Audit 2.3.5
- **Monitoramento**: Spring Actuator, Prometheus
- **Logging**: Logback (async console)
- **Testes**: JUnit 5, Mockito
- **Build**: Maven
- **Utilitários**: Lombok, Apache Commons Lang3, Jackson (JSON)

### 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | /v1/movimentacao-bancaria/detalhe | MovimentacoesControllerV1 | Detalhe de movimentação por NSU ou ID |
| GET | /v1/movimentacao-priorizado | MovimentacoesControllerV1 | Consulta movimentações priorizadas |
| POST | /v1/movimentacao-priorizado | MovimentacoesControllerV1 | Incluir movimentação priorizada |
| POST | /v1/movimentacao-priorizado/atualizarStatus | MovimentacoesControllerV1 | Atualizar status de movimentação priorizada |
| GET | /v1/consulta/saldos/bloqueados | MovimentacoesControllerV1 | Consultar saldos bloqueados |
| GET | /v2/movimentacao-bancaria/categoria | MovimentacoesControllerV2 | Obter categoria de movimentação |
| GET | /v2/movimentacao-bancaria | MovimentacoesControllerV2 | Consultar extrato de movimentações |
| POST | /v2/movimentacao-bancaria/pesquisas | MovimentacoesControllerV2 | Pesquisa de movimentações com filtros dinâmicos |
| GET | /v2/movimentacao-bancaria/total | MovimentacoesControllerV2 | Total de movimentações por período |
| GET | /v2/movimentacao-bancaria/extrato | MovimentacoesControllerV2 | Extrato detalhado de movimentações |
| GET | /v2/movimentacao-bancaria/lancamentosPorFaixaValores | MovimentacoesControllerV2 | Lançamentos agrupados por faixa de valores |
| POST | /v2/movimentacao-bancaria/bloqueio | MovimentacoesControllerV2 | Incluir bloqueio (deprecated - usar v3) |
| GET | /v2/movimentacao-bancaria/bloqueio | MovimentacoesControllerV2 | Listar bloqueios |
| POST | /v2/movimentacao-bancaria/bloqueio/liberarbloqueio | MovimentacoesControllerV2 | Liberar bloqueio (deprecated - usar v3) |
| GET | /v2/movimentacao-bancaria/bloqueio/conta/{conta}/banco/{banco}/tipoConta/{tipoConta} | MovimentacoesControllerV2 | Consultar bloqueios por conta |
| GET | /v2/movimentacao-bancaria/bloqueio/motivos/tipo/{tipo} | MovimentacoesControllerV2 | Listar motivos de bloqueio/desbloqueio |
| POST | /v2/consulta/debito-indevido | MovimentacoesControllerV2 | Consultar débitos indevidos |
| GET | /v2/movimentacao-bancaria/consulta/{protocolo} | MovimentacoesControllerV2 | Consultar movimentação por protocolo |
| GET | /v2/movimentacao-contabil/conciliada | MovimentacoesControllerV2 | Movimentos contábeis conciliados |
| GET | /v2/movimentacao-contabil/analitico | MovimentacoesControllerV2 | Movimentos contábeis analíticos |
| GET | /v2/movimentacao-contabil/maiores-saldo | MovimentacoesControllerV2 | Movimentos contábeis com maiores saldos |
| GET | /v2/movimentacao-bancaria/agendamento/{id} | MovimentacoesControllerV2 | Consultar agendamento por ID |
| PUT | /v2/movimentacao-bancaria/agendamento/{id} | MovimentacoesControllerV2 | Atualizar agendamento |
| GET | /v2/movimentacao-bancaria/agendamento/duplicidade/{linhadigitavel} | MovimentacoesControllerV2 | Verificar duplicidade de agendamento |
| GET | /v2/movimentacao-bancaria/limite-saque | MovimentacoesControllerV2 | Consultar limite de saque |
| GET | /v2/movimentacao-bancaria/limite-debito | MovimentacoesControllerV2 | Consultar limite de débito |
| GET | /v2/movimentacao-bancaria/relatorios/credito/nao-reclamados | MovimentacoesControllerV2 | Relatório de créditos não reclamados |
| POST | /v3/movimentacao-bancaria/bloqueio | MovimentacoesControllerV3 | Incluir bloqueio (versão atual) |
| POST | /v3/movimentacao-bancaria/bloqueio/liberarbloqueio | MovimentacoesControllerV3 | Liberar bloqueio (versão atual) |
| GET | /v3/movimentacao-bancaria/movimentacaoPorDocumento | MovimentacoesControllerV3 | Consultar movimentação por documento |
| GET | /v1/pix-movimentacao/{nsu} | MovimentacaoPixController | Consultar movimentação PIX por NSU |

### 5. Principais Regras de Negócio

- **Bloqueios de Conta**: Sistema suporta três tipos de bloqueio (CREDITO, DEBITO, VALOR) com validações específicas:
  - Bloqueio de valor requer saldo disponível maior ou igual ao valor bloqueado
  - Não permite bloqueio duplicado de crédito ou débito na mesma conta
  - Validação de motivos de bloqueio/desbloqueio cadastrados
  - Controle de vigência com data início e fim
  - Reserva de sequencial único para cada bloqueio (TbConta.SqUltimoBloqueioSaldo)

- **Processamento Transacional**: Commit/rollback individual para cada tipo de bloqueio (crédito, débito, valor) usando TransactionTemplate

- **Extrato de Movimentações**: 
  - Cálculo automático de saldo inicial e final
  - Suporte a filtros dinâmicos (14 tipos: débito/crédito, documento, NSU, estorno, transação, datas, valor, etc)
  - Paginação por quantidade de registros ou por data
  - Período padrão de consulta: 5 anos ou últimos N dias configurável
  - Tipo conta corrente fixo = 5, banco legado = 161

- **Categorização de Transações**: Identificação automática de tipo de comprovante (TEF/TED/BOLETO/PIX/NAO_INFORMADO) baseada em código de liquidação e transação

- **Movimentações PIX**: Utiliza data de comando para consultas, enquanto demais transações usam data de efetivação

- **Faixas de Valores**: Sistema suporta 11 faixas de valores para lançamentos (até 10k, 10-30k, 30-50k, 50-100k, 100-500k, 500k-5M, 5-10M, 10-20M, 20-50M, 50-100M, >100M)

- **Validações de Entrada**:
  - Validação de CPF/CNPJ versus conta
  - Validação de banco versus conta
  - Validação de formato de datas (yyyy-MM-dd)
  - Data início < data fim, data fim <= hoje
  - Validação de ranges de dias (7, 15, 30, 60, 90)
  - Limite de 225 caracteres para campos varchar

- **Movimentações Priorizadas**: Controle de duplicidade por número sequencial

- **Agendamentos**: Verificação de duplicidade por linha digitável, atualização de status

- **Saldos Bloqueados**: Quando motivo = 11 (bloqueio total), utiliza saldo disponível da conta

- **Auditoria**: Registro de todas alterações de bloqueios em TbLogAlteracao

- **Sanitização de Logs**: Uso de StringEscapeUtils para segurança em logs

- **Débitos Indevidos**: Monitoramento e consulta de transações monitoráveis

- **Isolamento de Transações**: Queries com isolation level 0 (dirty read) para performance

### 6. Relação entre Entidades

**Entidades Principais:**

- **TbConta**: Entidade central de conta corrente
  - Relaciona-se com TbSaldoBloqueado (1:N) - bloqueios de valor
  - Contém campos de bloqueio de crédito/débito (CdMotivoBloqueioCredito, CdMotivoBloqueioDebito)
  - Relaciona-se com TbMovimentoDia e TbHistoricoMovimento (1:N) - movimentações
  - Relaciona-se com TbAgendamentoContaCorrente (1:N) - agendamentos
  - Relaciona-se com TbHistoricoSaldo (1:N) - histórico de saldos
  - Relaciona-se com TbLogAlteracao (1:N) - auditoria

- **TbSaldoBloqueado**: Bloqueios de valor específico
  - Relaciona-se com TbConta (N:1)
  - Relaciona-se com TbMotivoBloqueio (N:1)
  - Relaciona-se com TbMotivoDesbloqueio (N:1)
  - Relaciona-se com TbHistoricoSaldoBloqueado (1:N) - histórico

- **TbMovimentoDia / TbHistoricoMovimento**: Movimentações bancárias (atual e histórico)
  - Relaciona-se com TbConta (N:1)
  - Relaciona-se com TbDetalheBoleto (1:1) - detalhes de boleto quando aplicável

- **TbAgendamentoContaCorrente**: Agendamentos de pagamentos
  - Relaciona-se com TbConta (N:1)

- **TbBanco**: Cadastro de bancos
  - Relaciona-se com TbConta (1:N)

- **TbPessoa**: Cadastro de pessoas (titulares)
  - Relaciona-se com TbConta via TbContaRelacionamento e TbPessoaTitularidade

- **TbMovimentoPriorizado**: Movimentações priorizadas
  - Relaciona-se com TbConta (N:1)

- **TbLoteMovimentoContabil**: Lotes de movimentos contábeis
  - Relaciona-se com movimentações para conciliação

**Relacionamentos Auxiliares:**
- TbFuncionario e TbDivisaoComercial: dados de usuários ISG para lançamentos por faixa
- TBL_CAIXA_ENTRADA_SPB (DBITP): movimentações SPB/PIX
- VwContaCorrenteSaldoDia, VwClienteSemDivisao: views para consultas otimizadas

### 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbConta | tabela | SELECT | Dados de contas correntes (saldos, bloqueios, agência) |
| TbSaldoBloqueado | tabela | SELECT | Bloqueios de valor ativos e históricos |
| TbHistoricoSaldoBloqueado | tabela | SELECT | Histórico de bloqueios de valor |
| TbMovimentoDia | tabela | SELECT | Movimentações bancárias do dia atual |
| TbHistoricoMovimento | tabela | SELECT | Movimentações bancárias históricas |
| TbMotivoBloqueio | tabela | SELECT | Cadastro de motivos de bloqueio |
| TbMotivoDesbloqueio | tabela | SELECT | Cadastro de motivos de desbloqueio |
| TbBanco | tabela | SELECT | Cadastro de bancos |
| TbAgendamentoContaCorrente | tabela | SELECT | Agendamentos de pagamentos |
| TbDetalheBoleto | tabela | SELECT | Detalhes de boletos pagos |
| TbLancamentoBoleto | tabela | SELECT | Lançamentos de boletos |
| TbHistoricoSaldo | tabela | SELECT | Histórico de saldos apurados |
| TbControleData | tabela | SELECT | Data de processamento do sistema |
| TbMovimentoPriorizado | tabela | SELECT | Movimentações priorizadas |
| TbLoteMovimentoContabil | tabela | SELECT | Lotes de movimentos contábeis |
| VwContaCorrenteSaldoDia | view | SELECT | View de saldos consolidados do dia |
| TbPessoa | tabela | SELECT | Cadastro de pessoas (titulares) |
| TbContaRelacionamento | tabela | SELECT | Relacionamento conta-pessoa |
| TbPessoaTitularidade | tabela | SELECT | Titularidade de contas |
| VwClienteSemDivisao | view | SELECT | View de clientes sem divisão comercial |
| TbFuncionario | tabela | SELECT | Cadastro de funcionários |
| TbDivisaoComercial | tabela | SELECT | Divisões comerciais |
| TBL_CAIXA_ENTRADA_SPB | tabela | SELECT | Movimentações SPB/PIX (banco DBITP) |

### 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbConta | tabela | UPDATE | Atualização de campos de bloqueio (CdMotivoBloqueioCredito, CdMotivoBloqueioDebito, VrSaldoBloqueioCredito, VrSaldoBloqueioDebito, SqUltimoBloqueioSaldo) |
| TbSaldoBloqueado | tabela | INSERT/UPDATE | Inclusão e atualização de bloqueios de valor (data vigência, motivos, protocolo, quantidade dias) |
| TbLogAlteracao | tabela | INSERT | Registro de auditoria de alterações em bloqueios |
| TbMovimentoPriorizado | tabela | INSERT/UPDATE | Inclusão e atualização de status de movimentações priorizadas |
| TbAgendamentoContaCorrente | tabela | UPDATE | Atualização de dados de agendamentos |

### 9. Arquivos Lidos e Gravados

não se aplica

### 10. Filas Lidas

não se aplica

### 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Responsável | Breve Descrição |
|--------------|------------|-------------------|-----------------|
| business-ccbd-base-credito-bloqueado (configurável) | Google Cloud PubSub | BloqueiosMonitoradosRepositoryImpl | Publicação de mensagens de bloqueios monitorados ao liberar bloqueio de valor. Payload JSON com dados do bloqueio e UUID de correlação |

### 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| DBCONTACORRENTE (Sybase) | Banco de Dados | Banco principal com dados de contas, movimentações, bloqueios, saldos, agendamentos e movimentos priorizados |
| DBGLOBAL (Sybase) | Banco de Dados | Banco com dados globais: cadastro de bancos, pessoas, relacionamentos conta-pessoa, funcionários e divisões comerciais |
| DBITP (Sybase) | Banco de Dados | Banco com dados de movimentações SPB/PIX (TBL_CAIXA_ENTRADA_SPB) |
| DBCCBD (SQL Server) | Banco de Dados | Banco de pagamento de contas com detalhes e lançamentos de boletos |
| Google Cloud PubSub | Mensageria | Publicação de mensagens de bloqueios monitorados para tópico configurável |
| OAuth2 Authorization Server | Segurança | Autenticação e autorização via OAuth2 Resource Server |

### 13. Avaliação da Qualidade do Código

**Nota:** 8/10

**Justificativa:**

**Pontos Positivos:**
- **Arquitetura bem estruturada**: Separação clara em camadas (adapter, domain, application) seguindo princípios de Clean Architecture
- **Versionamento de API**: Implementação de versionamento (v1, v2, v3) permitindo evolução sem quebrar contratos
- **Padrões de projeto**: Uso adequado de patterns como Bridge (classe Bloqueio), Strategy (validações de filtros), Repository, Service Layer
- **Separação de responsabilidades**: Classes de negócio focadas (IncluirBloqueio, LiberarBloqueio, ExtratoMovimentacoes)
- **Validações centralizadas**: Classes DadosEntradaValidation e TipoValidation concentram lógica de validação
- **Uso de enums**: Enumerações bem definidas para categorias, tipos, filtros, faixas de valores
- **Tratamento de exceções**: Handler centralizado com mapeamento adequado para status HTTP
- **Auditoria**: Registro de alterações em TbLogAlteracao
- **Segurança**: Sanitização de logs, OAuth2, controle transacional
- **Documentação**: Swagger/OpenAPI configurado
- **Tecnologias modernas**: Spring Boot, JDBI, MapStruct, PubSub

**Pontos de Melhoria:**
- **Queries SQL externas**: Uso de arquivos .sql separados dificulta manutenção e versionamento (preferível usar JPA/Hibernate ou query builders)
- **Isolation level 0**: Uso de dirty read pode causar inconsistências em cenários de alta concorrência
- **Controle transacional manual**: Classe Bloqueio com commit/rollback manual aumenta complexidade e risco de erros
- **Código legado**: Presença de endpoints deprecated (v2 bloqueios) indica dívida técnica
- **Acoplamento com banco**: Lógica de negócio conhece detalhes de tabelas (campos CdMotivoBloqueio*, SqUltimoBloqueio)
- **Falta de testes**: Não foram fornecidos testes unitários ou de integração no resumo
- **Constantes hardcoded**: Valores como tipo conta = 5, banco = 161 deveriam estar em configuração
- **Complexidade em converters**: Classe MovimentacaoConverter com 200+ linhas indica necessidade de refatoração

O código demonstra maturidade arquitetural e boas práticas, mas possui oportunidades de melhoria principalmente na camada de persistência e controle transacional.

### 14. Observações Relevantes

- **Múltiplos Bancos de Dados**: Sistema integra 4 datasources diferentes (3 Sybase + 1 SQL Server), cada um com propósito específico, exigindo atenção especial em transações distribuídas

- **Endpoints Deprecated**: Versões v2 de bloqueio/desbloqueio foram substituídas pela v3, mas mantidas para compatibilidade. Recomenda-se plano de descontinuação

- **Profiles de Ambiente**: Sistema configurado para 5 ambientes (local, des, qa, uat, prd) com datasources e configurações específicas

- **Controle de Sequencial**: Sistema utiliza campo SqUltimoBloqueioSaldo em TbConta para garantir unicidade de bloqueios, exigindo update na conta a cada novo bloqueio

- **Histórico de Dados**: Queries utilizam UNION ALL entre tabelas atuais (TbMovimentoDia, TbSaldoBloqueado) e históricas (TbHistoricoMovimento, TbHistoricoSaldoBloqueado) para consultas completas

- **Paginação Flexível**: Sistema suporta dois tipos de paginação - por quantidade de registros (TOP/ROWS LIMIT) ou por data

- **Categorização Automática PIX**: Sistema identifica automaticamente 9 categorias de transações PIX (transferência, pagamento, devolução, saque, troco, Open Finance)

- **Monitoramento**: Integração com Prometheus via Spring Actuator para métricas operacionais

- **Segurança de Logs**: Uso de StringEscapeUtils para sanitização de dados sensíveis em logs

- **Faixas de Valores Extensas**: Sistema suporta consultas de lançamentos até valores superiores a 100 milhões de reais

- **Validação de Titularidade**: Sistema valida CPF/CNPJ do titular versus conta antes de permitir operações

- **Dados Funcionais**: Para usuários ISG, sistema popula automaticamente dados de divisão comercial e tipo officer em consultas de lançamentos

- **Período de Retenção**: Consultas de extrato suportam até 5 anos de histórico por padrão

- **Débitos Indevidos**: Sistema possui módulo específico para monitoramento e consulta de transações suspeitas

- **Créditos Não Reclamados**: Relatório específico para identificação de créditos não reclamados pelos clientes

- **Limites Operacionais**: Sistema consulta e valida limites de saque e débito configurados por conta