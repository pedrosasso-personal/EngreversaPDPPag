# Ficha Técnica do Sistema

---

## 1. Descrição Geral

Sistema batch Java para gestão de débito automático em conta corrente corporativa (GDCC), voltado para produtos de crédito pessoal Banco do Brasil (CPBB - subproduto 55). O sistema realiza:

- **Cadastro automático** de novos contratos elegíveis para débito automático
- **Agendamento** de parcelas a vencer via integração com webservices GDCC
- **Processamento pontual** de débitos via arquivo texto posicional
- **Processamento de retornos** bancários com classificação de ações (baixa, suspensão, geração de tarefas SAC)

O sistema integra múltiplos bancos de dados legados (DBCOR, DBGESTAOCP, DBCRED) com o banco de controle (DBGESTAO), aplicando regras de negócio complexas como validação de prazos, antecipação de vencimentos para dias úteis, controle de suspensões por inadimplência/fraude/cessão, e geração de cargas para sistemas de baixa.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **GravaContaReader/Processor/Writer** | Job batch que identifica novos contratos CPBB elegíveis e os cadastra na TbContratoDebito |
| **PreparaAgendaReader/Processor/Writer** | Job batch que agenda parcelas a vencer, validando dados legados, calculando datas de agendamento e integrando com WS GDCC |
| **ProcessaPontualReader/Processor/Writer** | Job batch que processa arquivo texto de débitos pontuais, validando CPF/contratos/parcelas e gerando arquivo de retorno |
| **ProcessaRetornoReader/Processor/Writer** | Job batch que consulta retornos GDCC, classifica ações (baixa/suspensão/SAC) e atualiza parcelas |
| **IntegracaoAgendaBusinessImpl** | Implementa regras de negócio para integração com agenda GDCC (validação prazos, geração registros débito/cancelamento) |
| **ContratoDebitoDao** | DAO para operações CRUD em TbContratoDebito (contratos elegíveis para débito) |
| **ParcelaDebitoDao** | DAO para operações CRUD em TbParcelaDebito (parcelas agendadas/processadas) |
| **RegistroDebitoDao** | DAO para TbRegistroDebito (registros enviados ao GDCC) |
| **GestaoContratosDao** | DAO para consulta de dados em sistemas legados (DBCOR, DBGESTAOCP) com BD dinâmico |
| **ControleArquivoRetornoDao** | DAO para controle de processamento de arquivos retorno e geração de cargas de baixa |
| **GerarTarefaSacDao** | DAO para criação de solicitações/tarefas SAC em débitos com problemas |
| **AgendamentoRemessaWSClient** | Cliente Axis para WS de agendamento/cancelamento de remessas GDCC |
| **ConsultarRetornoWSClient** | Cliente Axis para WS de consulta de retornos GDCC |
| **ArquivosProcessadosWSClient** | Cliente Axis para WS de consulta de arquivos processados GDCC |
| **ConsultaBancosConveniadosWSClient** | Cliente Axis para WS de consulta de parâmetros de conta convênio |
| **BatchKeyGenerator** | Utilitário para geração de chaves sequenciais via stored procedure |
| **PositionalRecordParser** | Utilitário para parsing de arquivos texto posicionais |

---

## 3. Tecnologias Utilizadas

- **Java** (versão não especificada, provavelmente Java 6/7 pela presença de Axis 1.x)
- **Spring Batch** (framework de processamento batch)
- **Spring Framework** (injeção de dependências, transações)
- **Apache Axis 1.x** (cliente SOAP para webservices)
- **JDBC** (acesso a banco de dados)
- **Bitronix JTA** (gerenciador de transações distribuídas)
- **Sybase ASE** (banco de dados via driver JTDS)
- **Apache Commons** (utilitários diversos)
- **JMX** (monitoramento - domínio nnegocios.gdcf)

---

## 4. Principais Endpoints REST

**Não se aplica** - O sistema não expõe endpoints REST. Trata-se de um sistema batch que **consome** webservices SOAP externos (GDCC).

---

## 5. Principais Regras de Negócio

1. **Elegibilidade para Débito Automático:**
   - Subproduto = 55 (CPBB - Crédito Pessoal Banco do Brasil)
   - Banco = 001 (Banco do Brasil)
   - Tipo Cobrança = 7 (Débito em Conta)
   - Situação Contrato = 1 (Aberto)
   - Motivo Contrato Financeiro IN (1, 2)
   - Contrato não pode existir previamente em TbContratoDebito

2. **Validação de Prazos de Agendamento (RN002):**
   - Data débito deve ser >= Data Exercício (parâmetro sistema)
   - Se data agendamento não informada, usa DdPrazoDebito do convênio
   - Data agendamento deve estar entre DdPrazoMinimoDebito e DdPrazoMaximoDebito

3. **Antecipação de Vencimento para Dias Úteis:**
   - Produto CPBB: se vencimento cai em feriado/fim de semana, antecipa para dia útil anterior
   - Utiliza cache de feriados (TbFeriado) para validação

4. **Suspensão Automática de Débito:**
   - Contrato Quitado (motivo 1)
   - Cessão de Particulares (motivo 2)
   - Fraude (motivo 3)
   - Cadastro Inconsistente (motivo 4)
   - Troca Tipo Cobrança ≠ 7 (motivo 5)
   - Contrato em Cobrança (motivo 6)
   - Parcela com atraso > 60 dias (exceto veículos legais 10 e 12)

5. **Validação de CPF:**
   - Algoritmo completo de validação de dígitos verificadores
   - CPF com 11 dígitos = Pessoa Física, demais = Pessoa Jurídica

6. **Classificação de Retornos Bancários:**
   - TpAcao 1: Baixa automática da parcela (status RETORNADO_BAIXA)
   - TpAcao 2: Suspensão do débito (FlDebitoAtivo = 'N')
   - TpAcao 3: Nenhuma ação
   - TpAcao 4: Geração de tarefa SAC (prazo 15 dias úteis)
   - TpAcao 5: Geração de tarefa SAC + Suspensão

7. **Cancelamento de Agendamento:**
   - Status AGUARDANDO_GERACAO: cancela diretamente alterando status
   - Status PROCESSANDO_ARQUIVO ou ARQUIVO_ENVIADO: cria novo registro tipo CANCELAMENTO (movimento "1")
   - Validação: dtVencimento > dtExercicio

8. **Geração de Carga de Baixa:**
   - Lotes de 7000 registros por arquivo
   - Modalidade definida por cdAgenteRecebedor (1119=CP, 1193=CDC, 1163=CPC)
   - Procedures: PrGerarControleCarga, SP_IN_TBINFORMACAOBAIXA, PrAtualizaControleCarga

9. **Processamento Pontual:**
   - Arquivo texto posicional 87 bytes
   - Validação de duplicidade no mesmo arquivo (cache memória)
   - Rejeição de parcelas quitadas, contratos fechados, parcelas já cadastradas
   - Geração de arquivo retorno com códigos 00-12

10. **Controle de Status:**
    - Parcela: STATUS_INICIAL → AGENDADO → RETORNADO_BAIXA/RETORNADO_INCONSISTENTE/CANCELADO/ERRO/ESTORNO
    - Registro: AGUARDANDO_GERACAO → REGISTRO_GERADO → ARQUIVO_GERADO → ARQUIVO_ENVIADO → PROCESSANDO_ARQUIVO → PROCESSADO_COM_SUCESSO

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **TbContratoDebito**: Contratos elegíveis para débito automático
  - Relaciona-se com TbContrato (legado) via nuContrato
  - Contém: nuContrato, sqContratoFinanceiroAtivo, nuCpfCnpj, banco/agência/conta, flDebitoAtivo, motivoSuspensao

- **TbParcelaDebito**: Parcelas agendadas/processadas
  - Relaciona-se com TbContratoDebito via nuContrato
  - Relaciona-se com TbRegistroDebito via cdRegistroDebito
  - Contém: cdParcelaDebito, nuContrato, sqContratoFinanceiro, nuParcela, dtVencimento, dtAgendamento, vrParcela, stDebito, cdRegistroDebito, valores efetivos, códigos retorno

- **TbRegistroDebito**: Registros enviados ao GDCC
  - Relaciona-se com TbContaConvenioSistemaOrigem via cdContaConvenioSistemaOrigem
  - Contém: cdRegistroDebito, statusDebito, banco/agência/conta, dtEnvioRegistroDebito, dtVencimento, vrDebito, tpMovimentoDebito (débito/cancelamento)

- **TbContaConvenioSistemaOrigem**: Parâmetros de convênio por sistema origem
  - Relaciona-se com TbContaConvenio
  - Contém: cdVeiculoLegal, cdSistemaOrigem, nuBanco, dsAgrupamento, prazos (min/max/prazo), qtTentativa, vrCusto, layout arquivo

- **TbLogArquivoDebito**: Log de arquivos processados GDCC
  - Relaciona-se com TbEventoRegistroDebito
  - Contém: cdLogArquivoDebito, cdStatusDebito

- **TbEventoRegistroDebito**: Eventos de retorno por registro
  - Relaciona-se com TbRegistroDebito
  - Relaciona-se com TbRetornoDebitoAutomatico
  - Contém: cdEventoRegistroDebito, cdRegistroDebito, cdRetornoDebitoAutomatico, dtRetorno, valores efetivos

- **TbControleArquivoRetorno**: Controle de processamento de retornos
  - Contém: sqArquivo, cdAgenteRecebedor, flProcessado, dtProcessamento

- **TbControleCarga / TbInformacaoBaixa**: Cargas de baixa para sistemas downstream
  - Geradas via procedures a partir de parcelas com status RETORNADO_BAIXA

**Relacionamentos Legados (consulta apenas):**
- TbContrato (DBGESTAOCP) → TbContratoFinanceiro → TbContratoLiberacao
- TbProposta (DBCRED) → TbPropostaCreditoPessoal
- TbFeriado (DBCOR)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbContratoDebito | Tabela | SELECT | Contratos elegíveis para débito automático |
| TbParcelaDebito | Tabela | SELECT | Parcelas agendadas/processadas |
| TbRegistroDebito | Tabela | SELECT | Registros enviados ao GDCC |
| TbContaConvenio | Tabela | SELECT | Parâmetros de convênio |
| TbContaConvenioSistemaOrigem | Tabela | SELECT | Parâmetros de convênio por sistema origem |
| TbLogArquivoDebito | Tabela | SELECT | Log de arquivos processados GDCC |
| TbEventoRegistroDebito | Tabela | SELECT | Eventos de retorno por registro |
| TbRetornoDebitoAutomatico | Tabela | SELECT | Códigos de retorno bancário |
| TbParametroRetornoDebito | Tabela | SELECT | Parâmetros de retorno |
| TbRetornoDebitoSistemaOrigem | Tabela | SELECT | Mapeamento retornos por sistema origem |
| TbParametroSistema | Tabela | SELECT | Parâmetros globais (DtExercicio) |
| TbControleArquivoRetorno | Tabela | SELECT | Controle de processamento de retornos |
| TbNaturezaSolicitacao | Tabela | SELECT | Naturezas de solicitação SAC |
| tb_ntz_slt_tb_area_tb_filial | Tabela | SELECT | Relacionamento natureza/área/filial SAC |
| TbFeriado (DBCOR) | Tabela | SELECT | Feriados nacionais/bancários |
| TbConexao (DBCOR) | Tabela | SELECT | Mapeamento contrato → banco de dados origem |
| TbProduto (DBCOR) | Tabela | SELECT | Produtos financeiros |
| TbContrato (DBGESTAOCP) | Tabela | SELECT | Contratos legados (múltiplos BDs dinâmicos) |
| TbContratoFinanceiro (DBGESTAOCP) | Tabela | SELECT | Contratos financeiros ativos |
| TbContratoLiberacao (DBGESTAOCP) | Tabela | SELECT | Liberações de contratos |
| TbProposta (DBCRED) | Tabela | SELECT | Propostas de crédito |
| TbPropostaCreditoPessoal (DBCRED) | Tabela | SELECT | Propostas crédito pessoal |
| TbConvenioCreditoPessoalVignca (DBCRED) | Tabela | SELECT | Convênios crédito pessoal vigentes |
| vwTbContrato | View | SELECT | View de contratos com dados de pessoa/operador |
| TbPessoa | Tabela | SELECT | Dados de pessoas (clientes) |
| TbOperador | Tabela | SELECT | Operadores/usuários |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbContratoDebito | Tabela | INSERT/UPDATE | Inclusão de novos contratos elegíveis; atualização de suspensão (flDebitoAtivo, motivoSuspensao) e dados bancários |
| TbParcelaDebito | Tabela | INSERT/UPDATE | Inclusão de parcelas agendadas; atualização de status, valores efetivos, códigos retorno |
| TbRegistroDebito | Tabela | INSERT/UPDATE | Inclusão de registros débito/cancelamento; atualização de status |
| TbLogArquivoDebito | Tabela | UPDATE | Atualização de status de processamento (cdStatusDebito) |
| TbControleArquivoRetorno | Tabela | INSERT/UPDATE | Controle de arquivos retorno processados (flProcessado) |
| TbControleCarga (DBGESTAO) | Tabela | INSERT | Geração de cargas de baixa via procedure PrGerarControleCarga |
| TbInformacaoBaixa (DBGESTAO) | Tabela | INSERT | Informações de baixa via procedure SP_IN_TBINFORMACAOBAIXA |
| TbSolicitacao (DBSLT) | Tabela | INSERT | Solicitações SAC para débitos com problemas |
| TbSltCliente (DBSLT) | Tabela | INSERT | Relacionamento solicitação/cliente |
| TbTarefaEspecial (DBSLT) | Tabela | INSERT | Tarefas SAC via procedure PrIncluirSolicitacao |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| Arquivo débito pontual (parametrizado) | Leitura | ProcessaPontualReader (inputFileDir/inputFileName) | Arquivo texto posicional 87 bytes com débitos pontuais (contrato+parcela+movimento+banco+agência+conta+CPF+dtVenc+valor+dtAgend) |
| Arquivo retorno débito pontual (parametrizado) | Gravação | ProcessaPontualWriter (outputFileDir/outputFileName) | Arquivo texto com resultado do processamento: [linha original][código retorno 00-12][descrição] |

---

## 10. Filas Lidas

**Não se aplica** - O sistema não consome mensagens de filas (JMS, Kafka, RabbitMQ, etc).

---

## 11. Filas Geradas

**Não se aplica** - O sistema não publica mensagens em filas.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **GDCC - Agendamento** | SOAP WS | Agendamento e cancelamento de remessas de débito (BVBvfNnegociosGdccAgendamentoPortType) |
| **GDCC - Consulta Retorno** | SOAP WS | Consulta de retornos de débito por arquivo (BVBvfNnegociosGdccConsultaRetornoPortType) |
| **GDCC - Arquivos Processados** | SOAP WS | Consulta de arquivos processados, confirmação de baixa/inconsistência (BVBvfNnegociosGdccArquivosProcessadosConsultarArquivosProcessadosPortType) |
| **GDCC - Conta Convênio** | SOAP WS | Consulta de parâmetros de conta convênio e bancos conveniados (BVBvfNnegociosGdccContaConvenioConsultaBancosConveniadosPortType) |
| **Sistema Legado Gestão Contratos** | JDBC | Consulta de dados de contratos, parcelas, propostas em múltiplos bancos de dados (DBCOR, DBGESTAOCP, DBCRED) com BD dinâmico |
| **Sistema SAC (DBSLT)** | JDBC | Geração de solicitações e tarefas SAC para débitos com problemas |
| **Sistema de Baixa** | Procedures | Geração de cargas de baixa (TbControleCarga, TbInformacaoBaixa) via stored procedures |

**Endpoints WS (ambiente desenvolvimento - parametrizados):**
- Agendamento: mor-gridprd.bvnet.bv:18888 (domínio JMX: nnegocios.gdcf)
- Demais serviços: endpoints parametrizados via job-definitions-*.xml

**Banco de Dados:**
- **DBGESTAO** (Sybase): ptasybdes15.bvnet.bv:6010 (pool máximo 20 conexões, usuário plat_processamento_dbo)
- **DBCOR, DBGESTAOCP, DBCRED, DBSLT**: bancos legados acessados via JDBC (conexões não detalhadas nos arquivos analisados)

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Separação clara de responsabilidades (Reader/Processor/Writer pattern do Spring Batch)
- Uso de DAOs para encapsular acesso a dados
- Enums para constantes e códigos de retorno (boa prática)
- VOs/DTOs bem estruturados
- Uso de transações gerenciadas (Bitronix JTA)
- Tratamento de exceções customizadas (DadosInconsistentesException)
- Cache de parâmetros e feriados para otimização

**Pontos Negativos:**
- **Acoplamento excessivo**: DAOs acessam múltiplos bancos de dados com SQL dinâmico (replace ${nomeBD}), dificultando manutenção e testes
- **Falta de documentação**: ausência de Javadoc nas classes analisadas
- **Queries SQL hardcoded**: queries complexas embutidas em arquivos de recursos, dificultando refatoração
- **Mistura de responsabilidades**: algumas classes (ex: PreparaAgendaProcessor) possuem lógica de negócio extensa e complexa
- **Dependência de tecnologias legadas**: Axis 1.x (descontinuado), Sybase (menos comum), dificultando evolução
- **Falta de testes unitários**: não foram identificados testes automatizados nos arquivos analisados
- **Nomenclatura inconsistente**: alguns nomes de classes/métodos em português, outros em inglês
- **Código procedural**: algumas classes possuem métodos longos com múltiplas responsabilidades (ex: validações + persistência)
- **Falta de logs estruturados**: logs informativos, mas sem padrão estruturado (ex: JSON, MDC)

**Recomendações:**
1. Refatorar DAOs para usar ORM (Hibernate/JPA) e eliminar SQL dinâmico
2. Adicionar camada de serviço para isolar regras de negócio
3. Implementar testes unitários e de integração
4. Migrar de Axis 1.x para JAX-WS ou Spring WS
5. Adicionar Javadoc e documentação técnica
6. Padronizar nomenclatura (preferencialmente inglês)
7. Implementar logs estruturados com correlationId
8. Extrair constantes mágicas para classes de configuração

---

## 14. Observações Relevantes

1. **Arquitetura Multi-Banco de Dados:**
   - O sistema acessa 5 bancos de dados distintos (DBGESTAO, DBCOR, DBGESTAOCP, DBCRED, DBSLT)
   - Utiliza estratégia de BD dinâmico (replace ${nomeBD}) para acessar múltiplas instâncias de bancos legados
   - Requer gerenciamento cuidadoso de transações distribuídas (Bitronix JTA)

2. **Jobs Batch:**
   - **GravaConta**: Execução periódica (diária?) para cadastrar novos contratos
   - **PreparaAgenda**: Execução periódica para agendar parcelas a vencer (janela de 3 dias + prazo débito)
   - **ProcessaDebitoPontual**: Execução sob demanda via arquivo texto
   - **ProcessaParcelasRetorno**: Execução periódica para processar retornos bancários

3. **Usuários Robô:**
   - ROBO.GRAVACONTA (job GravaConta)
   - ROBO.PREPARAAGENDA (job PreparaAgenda)
   - ROBO.DEBITOPONTUAL (job ProcessaPontual)
   - ROBO.PROCESSAPARCELASRETORNO (job ProcessaRetorno)

4. **Códigos de Retorno Padronizados:**
   - 0: Sucesso
   - 10: Erro de banco de dados
   - 20: Conta convênio inexistente
   - 30: Erro de acesso a webservice
   - 40: Erro de validação de parâmetros
   - 50: Erro de integração agenda
   - 60: Erro ao incluir registro débito
   - 70: Erro ao incluir parcela débito
   - 110: Inconsistência de dados

5. **Produto Específico:**
   - Sistema focado em Crédito Pessoal Banco do Brasil (CPBB - subproduto 55)
   - Banco 001 (Banco do Brasil)
   - Tipo cobrança 7 (débito em conta)
   - Veículos legais específicos (10, 12 com tratamento diferenciado para atraso 60 dias)

6. **Monitoramento:**
   - JMX habilitado (domínio nnegocios.gdcf)
   - URL produção: mor-gridprd.bvnet.bv:18888

7. **Segurança:**
   - Usuário banco: plat_processamento_dbo (permissões DBO - Data Base Owner)
   - Validação de CPF com algoritmo completo de dígitos verificadores
   - Controle de acesso via login em todas as operações de alteração

8. **Performance:**
   - Pool de conexões: máximo 20 conexões
   - Lotes de 7000 registros para cargas de baixa
   - Cache de parâmetros e feriados para reduzir consultas
   - CommitInterval=1 para job de retorno (transações individuais)

9. **Dependências Críticas:**
   - Disponibilidade dos webservices GDCC
   - Disponibilidade dos bancos de dados legados (DBCOR, DBGESTAOCP, DBCRED)
   - Stored procedures (prObterSequencialDisponivel, PrGerarControleCarga, SP_IN_TBINFORMACAOBAIXA, PrAtualizaControleCarga, PrIncluirSolicitacao)

10. **Limitações Identificadas:**
    - Falta de retry automático em falhas de WS (ResumeStrategy retorna false)
    - Ausência de mecanismo de reprocessamento de registros com erro
    - Dependência de tecnologias legadas (Axis 1.x, Sybase)
    - Falta de testes automatizados

---

**Documento gerado em:** 2024
**Versão:** 1.0
**Responsável pela análise:** Agente de Engenharia Reversa IA