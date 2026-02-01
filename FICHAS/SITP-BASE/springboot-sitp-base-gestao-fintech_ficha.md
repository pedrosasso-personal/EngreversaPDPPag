# Ficha Técnica do Sistema

## 1. Descrição Geral

O **springboot-sitp-base-gestao-fintech** é um sistema backend desenvolvido em Spring Boot que gerencia operações financeiras de Fintechs integradas ao SITP (Sistema Integrado de Transferências e Pagamentos). O sistema oferece funcionalidades para consulta consolidada e detalhada de transações de TEDs (Transferências Eletrônicas Disponíveis) e Boletos, tanto para pagamentos quanto recebimentos. Além disso, gerencia cadastros de origens de pagamento, entidades, bancos, finalidades e outros parâmetros necessários para operações de contingência e conciliação de remessas DOC. O sistema também permite cancelamento e estorno de lançamentos, consulta de movimentos RCO e integração com o ISPB (Identificador do Sistema de Pagamentos Brasileiro).

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Server.java** | Classe principal que inicializa a aplicação Spring Boot e configura o timezone padrão como UTC. |
| **CancelamentoService** | Gerencia operações de cancelamento e estorno de lançamentos, incluindo inversão de remetente/favorecido e atualização de status. |
| **ContigenciaService** | Fornece serviços para consulta de dados de contingência (filiais, origens, transações, liquidações, bancos, finalidades, tipos de conta, canais de pagamento, eventos contábeis). |
| **EntidadeService** | Consulta entidades do PGFT (Pagamentos e Transferências). |
| **ISPBService** | Consulta informações do ISPB, como descrição de operações e bancos ativos na CIP. |
| **RcoService** | Consulta movimentos RCO (Registro de Controle de Operações) e bancos ativos na CIP. |
| **SITPGestaoFintechService** | Serviço principal que gerencia consultas consolidadas e detalhadas de TEDs e Boletos (pagamentos e recebimentos), além de operações de atualização, inclusão e exclusão de origens de pagamento. |
| **SumarizacaoDocService** | Gerencia consultas de itens de remessa DOC e conciliação de remessas. |
| **CancelamentoRepository** | Acessa o banco de dados para consultar transações de lançamentos e atualizar status de cancelamento. |
| **ContigenciaRepository** | Realiza consultas de dados de contingência no banco de dados. |
| **SITPGestaoFintechRepository** | Executa consultas consolidadas e detalhadas de transações, além de operações de insert/update/delete em tabelas de validação de origem de pagamento. |
| **SumarizacaoDocRepository** | Consulta itens de remessa e conciliação de arquivos DOC. |
| **CancelamentoApi** | Expõe endpoints REST para operações de cancelamento de lançamentos. |
| **ContigenciaApi** | Expõe endpoints REST para consultas de dados de contingência. |
| **EntidadeApi** | Expõe endpoint REST para consulta de entidades PGFT. |
| **ISPBApi** | Expõe endpoints REST para consultas ISPB. |
| **RcoApi** | Expõe endpoints REST para consultas de movimentos RCO. |
| **SITPGestaoFintechApi** | Expõe endpoints REST para consultas consolidadas e detalhadas de TEDs e Boletos, além de operações de gestão de origens de pagamento. |
| **SumarizacaoDocApi** | Expõe endpoints REST para consultas de sumarização de remessas DOC. |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.7.18** - Framework principal para desenvolvimento da aplicação
- **Spring Web** - Para criação de APIs REST
- **Spring Data JDBC** - Para acesso a banco de dados
- **Spring Security** - Para autenticação e autorização (Basic Auth e LDAP)
- **Gradle 7.5.1** - Sistema de build
- **Sybase jConnect 16.3** - Driver JDBC para banco de dados Sybase
- **Swagger/Springfox 3.0.0** - Documentação de APIs
- **Logback** - Framework de logging com saída em JSON
- **Lombok** - Redução de código boilerplate
- **JUnit 4.13.2** - Framework de testes unitários
- **Mockito** - Framework para criação de mocks em testes
- **Docker** - Containerização da aplicação
- **AdoptOpenJDK 8 com OpenJ9** - JVM utilizada no container
- **Jackson** - Serialização/deserialização JSON
- **Apache Commons Lang3** - Utilitários diversos
- **JaCoCo** - Cobertura de código
- **SonarQube** - Análise de qualidade de código
- **Bibliotecas internas Votorantim** (springboot-arqt-base-*)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/cancelamento/lancamento/transacao` | CancelamentoApi | Obtém lançamentos para estorno/cancelamento |
| PUT | `/cancelamento/lancamento/status/itp/{status}` | CancelamentoApi | Atualiza status de lançamento na caixa entrada SPB |
| PUT | `/cancelamento/lancamento/status/pgf/{status}` | CancelamentoApi | Atualiza status de lançamento no PGFTES |
| GET | `/contigencia/filiais` | ContigenciaApi | Lista filiais ativas |
| GET | `/contigencia/filiais/{id}` | ContigenciaApi | Consulta filial por ID |
| GET | `/contigencia/origens` | ContigenciaApi | Lista origens de pagamento |
| GET | `/contigencia/origens/id` | ContigenciaApi | Lista origens por IDs |
| GET | `/contigencia/transacoes` | ContigenciaApi | Lista transações por origem |
| GET | `/contigencia/liquidacoes` | ContigenciaApi | Lista liquidações por origem e transação |
| GET | `/contigencia/bancos` | ContigenciaApi | Lista bancos ativos |
| GET | `/contigencia/finalidades` | ContigenciaApi | Lista finalidades |
| GET | `/contigencia/tipos-conta` | ContigenciaApi | Lista tipos de conta |
| GET | `/contigencia/canais-pagamento` | ContigenciaApi | Lista canais de pagamento |
| GET | `/contigencia/evento-contabil/{id}` | ContigenciaApi | Consulta evento contábil por ID |
| GET | `/entidade` | EntidadeApi | Lista entidades do PGFT |
| GET | `/ispb/operation-description/{codigo}` | ISPBApi | Obtém descrição de operação ISPB |
| GET | `/ispb/active-banks` | ISPBApi | Lista bancos ativos no ISPB |
| GET | `/rco/consultaMovimentosRco` | RcoApi | Consulta movimentos RCO por período |
| GET | `/rco/bancosAtivosCip` | RcoApi | Lista bancos ativos na CIP |
| POST | `/sitp-gestao-fintech/ted-fintech` | SITPGestaoFintechApi | Consulta consolidada de TEDs enviadas |
| POST | `/sitp-gestao-fintech/boleto-fintech` | SITPGestaoFintechApi | Consulta consolidada de Boletos pagos |
| POST | `/sitp-gestao-fintech/ted-fintech-recebimento` | SITPGestaoFintechApi | Consulta consolidada de TEDs recebidas |
| POST | `/sitp-gestao-fintech/ted-fintech-detalhe-pgto` | SITPGestaoFintechApi | Consulta detalhada de TEDs enviadas |
| POST | `/sitp-gestao-fintech/ted-fintech-detalhe-recebimento` | SITPGestaoFintechApi | Consulta detalhada de TEDs recebidas |
| POST | `/sitp-gestao-fintech/boleto-fintech-detalhe-pgto` | SITPGestaoFintechApi | Consulta detalhada de Boletos pagos |
| POST | `/sitp-gestao-fintech/atualizarOrigemPagamento` | SITPGestaoFintechApi | Atualiza/insere origem de pagamento |
| POST | `/sitp-gestao-fintech/detativarOrigemPagamento` | SITPGestaoFintechApi | Desativa origem de pagamento |
| POST | `/sitp-gestao-fintech/incluir-origem-pagamento` | SITPGestaoFintechApi | Inclui parceiro Wallet |
| DELETE | `/sitp-gestao-fintech/excluir-origem-pagamento/cod-origem/{codOrigem}/cod-cliente/{codCliente}` | SITPGestaoFintechApi | Exclui origem de pagamento Wallet |
| GET | `/sumarizacao-doc` | SumarizacaoDocApi | Lista itens de remessa DOC com paginação |
| GET | `/sumarizacao-doc/conciliacao` | SumarizacaoDocApi | Lista conciliação de remessas DOC |

---

## 5. Principais Regras de Negócio

- **Consulta Consolidada de Transações**: Agrupa transações de TEDs e Boletos por status (enviadas, em processamento, sucesso, erro) para Fintechs específicas em um período.
- **Consulta Detalhada de Transações**: Retorna detalhes completos de cada transação (remetente, favorecido, valores, datas, status, motivos de erro).
- **Cancelamento e Estorno**: Permite cancelar lançamentos, invertendo remetente e favorecido, e atualizando status nas tabelas de caixa entrada e lançamentos.
- **Gestão de Origens de Pagamento**: Permite incluir, atualizar, desativar e excluir origens de pagamento de Fintechs e parceiros Wallet no sistema.
- **Contingência**: Fornece dados de apoio para operações de contingência (filiais, origens, transações, liquidações, bancos, finalidades, tipos de conta, canais de pagamento).
- **Sumarização DOC**: Permite consultar itens de remessa DOC e conciliação de arquivos, com suporte a paginação.
- **Consulta RCO**: Permite consultar movimentos RCO (mensagens do SPB) para geração de arquivos de controle.
- **Validação de Segurança**: Suporta dois tipos de segurança para validação de mensagens (tipo 1 ou tipo 2).
- **Conversão de Códigos Bancários**: Converte códigos de banco entre padrão COMPE e código global.

---

## 6. Relação entre Entidades

**Principais entidades e relacionamentos identificados:**

- **LancamentoDTO**: Entidade principal que representa um lançamento financeiro, composta por:
  - **LancamentoGeralDTO**: Dados gerais (transação, liquidação, filial, valor, protocolo, status)
  - **LancamentoClienteDTO**: Dados do remetente e favorecido (banco, agência, conta, CPF/CNPJ, nome, tipo de conta)
  - **LancamentoBoletoDTO**: Dados específicos de boleto (código de barras, vencimento, valores de desconto, juros, multa)
  - **LancamentoComplementarDTO**: Dados complementares (login, sistema origem, protocolo cliente, evento contábil, motivo)
  - **LancamentoTransacao**: Dados da transação (código transação, código transação estorno, origem operação, evento)

- **FintechRemetente**: Representa uma Fintech como remetente de TED, com dados do beneficiário e transação.

- **FintechBeneficiario**: Representa uma Fintech como beneficiária de TED, com dados do remetente e transação.

- **FintechPagadora**: Representa uma Fintech pagadora de Boleto, com dados do boleto e status de pagamento.

- **OrigemPagamentoRequest**: Representa uma origem de pagamento com URLs de validação, dados do parceiro comercial e configurações de segurança.

- **MovimentoRco**: Representa um movimento RCO com dados de débito/crédito, ISPB contraparte, data e quantidade.

- **ItemRemessaDoc** e **ConciliacaoRemessaDoc**: Representam itens e conciliação de remessas DOC.

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TBL_CAIXA_ENTRADA_SPB | tabela | SELECT | Lançamentos de entrada do SPB (TEDs e Boletos recebidos/enviados) |
| TBL_TRANSACAO_SPB | tabela | SELECT | Transações configuradas no sistema |
| TBL_LIQUIDACAO_SPB | tabela | SELECT | Tipos de liquidação (TED, DOC, Boleto, etc) |
| TBL_FILIAL_SPB | tabela | SELECT | Filiais ativas do banco |
| TBL_SIST_ORIGEM_SPB | tabela | SELECT | Sistemas/origens de pagamento cadastrados |
| TBL_DESCRICAO_TRANSACAO_SPB | tabela | SELECT | Descrições das transações |
| TBL_FINALIDADE_SPB | tabela | SELECT | Finalidades de pagamento |
| TBL_STATUS_UNICO_SPB | tabela | SELECT | Status dos lançamentos |
| TBL_ERRO_SPB | tabela | SELECT | Códigos e descrições de erros |
| TbBanco (DBGLOBAL) | tabela | SELECT | Cadastro de bancos |
| TbTipoConta (DBGLOBAL) | tabela | SELECT | Tipos de conta corrente |
| TBL_LANCAMENTO (DBPGF_TES) | tabela | SELECT | Lançamentos de tesouraria |
| TBL_ENTIDADE (DBPGF_TES) | tabela | SELECT | Entidades do PGFT |
| TbCanalPagamento (DBPGF_TES) | tabela | SELECT | Canais de pagamento disponíveis |
| TBL_EVENTO_CONTABIL (DBPGF_TES) | tabela | SELECT | Eventos contábeis |
| TbArquivoCompensacao (DBPGF_TES) | tabela | SELECT | Arquivos de compensação DOC |
| TbDetalheArquivoCompensacao (DBPGF_TES) | tabela | SELECT | Detalhes dos arquivos de compensação |
| TbValidacaoOrigemPagamento | tabela | SELECT | Validação de origens de pagamento cadastradas |
| tb_oper_operacao (DBISPB) | tabela | SELECT | Operações do ISPB |
| tb_ispb_ispb (DBISPB) | tabela | SELECT | Bancos cadastrados no ISPB |
| sp_se_movimento_tib_369 (DBISPB) | procedure | EXEC | Consulta movimentos TIB para arquivo RCO |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TBL_CAIXA_ENTRADA_SPB | tabela | UPDATE | Atualiza status de lançamentos para rejeitado |
| TBL_LANCAMENTO (DBPGF_TES) | tabela | UPDATE | Atualiza status, data e login de devolução de lançamentos |
| TbValidacaoOrigemPagamento | tabela | INSERT | Insere nova origem de pagamento ou parceiro |
| TbValidacaoOrigemPagamento | tabela | UPDATE | Atualiza dados de origem de pagamento existente |
| TbValidacaoOrigemPagamento | tabela | DELETE | Remove origem de pagamento (desativação ou exclusão Wallet) |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | leitura | Configuração Spring Boot | Arquivo de configuração de logs (JSON format) |
| application.yml | leitura | Configuração Spring Boot | Configurações da aplicação por ambiente |
| application-local.yml | leitura | Configuração Spring Boot | Configurações específicas do ambiente local |
| roles/*.yml | leitura | Configuração Spring Security | Definição de roles e grupos por ambiente |
| database/*-sql.xml | leitura | BvSql (biblioteca interna) | Queries SQL externalizadas em XML |
| testes-funcionais-jmeter.jmx | leitura | Testes funcionais JMeter | Plano de testes funcionais |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema/Serviço | Descrição |
|-----------------|-----------|
| **Banco de Dados Sybase (DBITP)** | Banco principal do SITP com tabelas de lançamentos, transações, status e configurações |
| **Banco de Dados Sybase (DBGLOBAL)** | Banco com cadastros globais (bancos, tipos de conta) |
| **Banco de Dados Sybase (DBPGF_TES)** | Banco de tesouraria com lançamentos, entidades e eventos contábeis |
| **Banco de Dados Sybase (DBISPB)** | Banco com informações do ISPB e movimentos SPB |
| **LDAP (BVNet)** | Autenticação de usuários via LDAP corporativo |
| **Nexus (nexus.bvnet.bv)** | Repositório de artefatos Maven/Gradle |
| **Swagger UI** | Interface de documentação e teste de APIs |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades em camadas (API, Service, Repository)
- Uso adequado de anotações Lombok para reduzir boilerplate
- Externalização de queries SQL em arquivos XML
- Configuração de múltiplos ambientes (local, des, qa, uat, prd)
- Presença de testes unitários para a maioria das classes
- Uso de Swagger para documentação de APIs
- Tratamento de exceções customizadas
- Configuração de logging estruturado em JSON
- Uso de paginação em consultas que retornam muitos registros

**Pontos de Melhoria:**
- Algumas classes de serviço possuem métodos muito longos e complexos (ex: SITPGestaoFintechRepository)
- Uso excessivo de reflection em testes pode indicar design acoplado
- Falta de validação de entrada em alguns endpoints
- Alguns métodos retornam Optional mas lançam exceção quando vazio, quebrando o contrato do Optional
- Código com comentários em português e inglês misturados
- Algumas classes de domínio implementam getters que clonam Date, mas outras não (inconsistência)
- Falta de documentação JavaDoc em métodos públicos
- Uso de strings mágicas em alguns lugares (ex: status, tipos)
- Alguns testes unitários apenas verificam se o retorno não é nulo, sem validar comportamento
- Tratamento genérico de exceções em alguns pontos (catch Exception)

---

## 14. Observações Relevantes

- O sistema utiliza banco de dados Sybase com múltiplos schemas (DBITP, DBGLOBAL, DBPGF_TES, DBISPB)
- A aplicação está preparada para execução em containers Docker/Kubernetes (OpenShift)
- Utiliza timezone UTC para todas as operações de data/hora
- Possui configuração de probes (liveness e readiness) para Kubernetes
- Autenticação suporta tanto LDAP quanto usuários in-memory (para testes)
- As queries SQL são externalizadas em arquivos XML, facilitando manutenção
- O sistema possui três tipos de testes: unitários, integração e funcionais (JMeter)
- Utiliza bibliotecas internas da Votorantim para segurança, auditoria e acesso a dados
- A aplicação expõe métricas e status via endpoint `/api-utils/status`
- Configuração de memória JVM: Xms64m, Xmx128m, MaxPermSize=128m
- O sistema trabalha com diferentes tipos de liquidação: TED (31, 32), Boleto (22), DOC (21)
- Suporta operações de contingência para lançamentos manuais
- Implementa controle de paginação para consultas que retornam grandes volumes de dados