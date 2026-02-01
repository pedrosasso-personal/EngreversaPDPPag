# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java responsável pela geração de arquivos de extrato bancário no formato CNAB 240 para clientes do Banco Votorantim/BV. O sistema processa extratos de contas correntes com diferentes periodicidades (diário, semanal, quinzenal e mensal), realizando leitura de saldos históricos, movimentações bancárias e gerando arquivos estruturados conforme layout CNAB 240. Suporta três tipos de processamento (1, 2 e 3) e implementa lógica de reprocessamento para divergências detectadas.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê configurações de clientes e filtra conforme periodicidade e parâmetros |
| **ItemProcessor** | Processa cada cliente, obtém contas ativas, saldos e executa processamento/reprocessamento |
| **ItemWriter** | Gera arquivos CNAB 240 físicos no sistema de arquivos |
| **TabelasCnabService** | Centraliza operações de leitura/escrita nas tabelas CNAB do banco de dados |
| **HistoricoSaldoService** | Busca saldos iniciais e finais das contas no histórico |
| **ArquivoService** | Coordena a geração física dos arquivos CNAB com headers, lotes, detalhes e trailers |
| **ProcessamentoService** | Executa fluxo de processamento normal (primeira geração) |
| **ReprocessamentoService** | Executa fluxo de reprocessamento com validações de divergências |
| **ConfiguradorProcessoService** | Configura parâmetros iniciais do job (datas, periodicidade, filtros) |
| **ControleDataService** | Gerencia datas de processamento conforme tipo de execução |
| **Cliente** | Entidade de domínio representando cliente e suas configurações |
| **Conta** | Entidade de domínio representando conta corrente |
| **Detalhe** | Entidade representando lançamento/movimentação bancária |
| **Lote** | Entidade representando lote de extrato (agrupamento por conta) |

## 3. Tecnologias Utilizadas

- **Framework Batch**: BV Framework Batch (proprietário baseado em Spring Batch)
- **Linguagem**: Java
- **Build**: Maven
- **Banco de Dados**: Sybase ASE
- **Driver JDBC**: BVDriver (wrapper) + Sybase jConnect (jconn4)
- **Spring Framework**: 2.0 (injeção de dependências, JDBC Template)
- **Logging**: Log4j / Reload4j 1.2.22
- **Testes**: JUnit 4, Mockito 2.28.2
- **Gerenciamento de Transações**: Bitronix (JTA)
- **Padrão de Arquivo**: CNAB 240

## 4. Principais Endpoints REST

não se aplica

## 5. Principais Regras de Negócio

1. **Periodicidade de Extratos**: Sistema suporta 4 periodicidades (Diário, Semanal, Quinzenal, Mensal) com lógicas específicas de cálculo de datas
2. **Tipos de Processamento**:
   - Tipo 1: Processamento dia corrido
   - Tipo 2: Processamento dia útil (padrão)
   - Tipo 3: Processamento D0
3. **Reprocessamento**: Detecta divergências em saldos iniciais, finais e data de alteração, reprocessando apenas contas divergentes
4. **Validações de Reprocessamento**:
   - Conta igual ao lote
   - Saldo inicial divergente
   - Saldo final divergente
   - Data de alteração posterior à geração
5. **Contas Novas**: Contas abertas após data inicial do período têm saldo anterior zerado
6. **Exclusão de Clientes**: Lista hardcoded de clientes excluídos do processamento (861, 1276, etc.)
7. **Cálculo de Datas**: Ajusta datas de início/fim conforme periodicidade e data de encerramento de contas
8. **Geração de Arquivo**: Apenas gera arquivo físico se tipo de transferência diferente de Internet Banking
9. **Sequencial de Extrato**: Incrementa sequencial na tabela TbConta a cada geração
10. **Formato CNAB 240**: Estrutura com Header Arquivo, Header Lote, Detalhes (segmento E), Trailer Lote e Trailer Arquivo

## 6. Relação entre Entidades

**Cliente** (1) ----< (N) **Conta**
- Cliente possui múltiplas contas ativas
- Relacionamento através de CdPessoa

**Conta** (1) ----< (N) **Detalhe**
- Cada conta possui múltiplos lançamentos/detalhes
- Relacionamento através de CdSequencialLote

**Cliente** (1) ----< (N) **Lote**
- Cliente possui um lote por conta no arquivo
- Relacionamento através de CdCnabExtratoArquivo

**Conta** (1) ---- (1) **Lote**
- Cada conta gera um lote no arquivo CNAB
- Relacionamento através de CdSequencialLote

**Conta** (1) ---- (N) **HistoricoSaldoVO**
- Conta possui histórico de saldos diários
- Relacionamento através de CdBanco + NuContaCorrente + CdTipoConta

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|----------------------------|------|----------|-----------------|
| TbCnabExtratoConfiguracao | Tabela | SELECT | Configurações de clientes para geração de extrato |
| TbConta | Tabela | SELECT | Dados cadastrais de contas correntes |
| TbPessoa | Tabela | SELECT | Dados cadastrais de pessoas (clientes) |
| TbPessoaTitularidade | Tabela | SELECT | Relacionamento pessoa-titularidade |
| TbContaRelacionamento | Tabela | SELECT | Relacionamento conta-titularidade |
| TbHistoricoSaldo | Tabela | SELECT | Histórico de saldos diários das contas |
| TbControleData | Tabela | SELECT | Controle de datas de processamento por banco |
| TbAgencia | Tabela | SELECT | Dados de agências bancárias |
| TbCnabExtratoArquivo | Tabela | SELECT | Arquivos de extrato já gerados |
| TbCnabExtratoArquivoLote | Tabela | SELECT | Lotes de arquivos de extrato |
| TbCnabExtratoDetalhe | Tabela | SELECT | Detalhes/lançamentos dos extratos |
| TbCnabExtratoContaInvalida | Tabela | SELECT | Contas inválidas para geração de extrato |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|----------------------------|------|----------|-----------------|
| TbCnabExtratoArquivo | Tabela | INSERT/UPDATE | Insere novos arquivos e atualiza nome/quantidade de registros |
| TbCnabExtratoArquivoLote | Tabela | INSERT/UPDATE | Insere lotes e atualiza saldos/totalizadores |
| TbCnabExtratoDetalhe | Tabela | INSERT | Insere detalhes via procedure PrInserirDetalheCnab |
| TbConta | Tabela | UPDATE | Atualiza sequencial de extrato (NuSeqExtratoConciliacao) |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| FB240EXTRATOBV_{CPFCNPJ}_{DATAHORA}.RET | Gravação | ArquivoService | Arquivo CNAB 240 com extratos gerados |
| job-resources.xml | Leitura | Spring Context | Configurações de datasources por ambiente |
| job-definitions.xml | Leitura | Spring Context | Definições de beans e parâmetros do job |
| *-sql.xml | Leitura | QueryReader | Queries SQL externalizadas em XML |
| log/statistics-{executionId}.log | Gravação | Log4j/BvDailyRollingFileAppender | Logs de estatísticas do batch |
| log/robo.log | Gravação | Log4j/RollingFileAppender | Logs gerais da aplicação |

## 10. Filas Lidas

não se aplica

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| DBCONTACORRENTE (Sybase) | Banco de Dados | Base principal com dados de contas, extratos e configurações |
| DBGLOBAL (Sybase) | Banco de Dados | Base com dados cadastrais de pessoas e agências |
| Sistema de Arquivos | File System | Geração de arquivos CNAB em diretórios específicos por tipo de transferência |

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com camadas bem definidas (batch, service, repository, domain)
- Uso adequado de padrões como Builder, Factory e Strategy
- Externalização de queries SQL em arquivos XML
- Tratamento de exceções customizadas
- Uso de interfaces para repositories
- Testes unitários presentes (embora limitados)

**Pontos Negativos:**
- Lista hardcoded de clientes excluídos no SQL (manutenção difícil)
- Comentários em português misturados com código
- Uso de framework batch proprietário (vendor lock-in)
- Falta de documentação JavaDoc
- Alguns métodos longos (ex: gerarCampos em ArquivoService)
- Uso de versões antigas de bibliotecas (Spring 2.0, Log4j)
- Falta de testes de integração mais abrangentes
- Código com caracteres especiais mal codificados (�)
- Constantes mágicas em alguns lugares (ex: CONSTANTE_QTDE = 50000)

## 14. Observações Relevantes

1. **Ambientes**: Sistema configurado para DES, UAT e PRD com datasources específicos
2. **Execução**: Batch executado via UC4 com scripts .bat (Windows) e .sh (Linux)
3. **Parâmetros Obrigatórios**: processamento, cdBanco, periodicidadeExtrato
4. **Parâmetros Opcionais**: dataReferencia, cdPessoa (permite processar cliente específico)
5. **Códigos de Banco**: 655 (Banco Votorantim) e 413 (Banco BV)
6. **Tipos de Transferência**: Nexxera, Accesstage, Finnet, Connect, Interno (Internet Banking não gera arquivo)
7. **Procedure Crítica**: PrInserirDetalheCnab realiza inserção massiva de detalhes
8. **Estratégia de Retomada**: MyResumeStrategy permite continuar processamento após falhas em arquivos específicos
9. **Paginação**: Detalhes lidos em lotes de 50.000 registros para evitar estouro de memória
10. **Transação**: Timeout configurado para 1.200.000ms (20 minutos)
11. **Segurança**: Uso de BVDriver com criptografia de credenciais
12. **Veracode**: Código contém comentário sobre restrição do Veracode impedindo uso de QueryReader em TbControleDataRepositoryImpl