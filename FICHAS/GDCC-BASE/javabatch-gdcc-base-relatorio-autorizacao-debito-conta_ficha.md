# Ficha Técnica do Sistema

## 1. Descrição Geral
Sistema batch Java desenvolvido para gerar relatórios de autorização de débito em conta corrente. O sistema consulta registros de débitos automáticos processados, enriquece as informações com dados de contratos, parcelas e clientes, e gera um arquivo Excel (.xls) consolidado com todas as informações relevantes para análise e acompanhamento das autorizações de débito.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê os registros de autorização de débito do banco de dados, enriquece com informações complementares e prepara para processamento |
| **ItemProcessor** | Processa os registros e gera a planilha Excel (HSSFWorkbook) com cabeçalho e linhas de detalhe |
| **ItemWriter** | Grava o arquivo Excel no diretório configurado com timestamp no nome |
| **RegistroAutDebtoDAOImpl** | Implementa acesso aos dados de autorização de débito, parcelas, contratos e bancos |
| **RegistroAutDebtoQueriesImpl** | Constrói dinamicamente as queries SQL para consulta dos dados |
| **RegistroAutDebitoVO** | Value Object que representa um registro de autorização de débito com todos os atributos |
| **ConexaoBancoDados** | Gerencia conexões com banco de dados Sybase |
| **MyResumeStrategy** | Estratégia de tratamento de erros e definição de exit codes |

## 3. Tecnologias Utilizadas
- **Framework Batch**: Spring Batch (BV Framework Batch Standalone)
- **Linguagem**: Java
- **Build**: Maven (multi-módulo)
- **Banco de Dados**: Sybase (driver jConnect 7.07-SP136)
- **Geração de Excel**: Apache POI (HSSF)
- **Logging**: Log4j
- **Injeção de Dependência**: Spring Framework
- **Gerenciamento de Transações**: Bitronix

## 4. Principais Endpoints REST
Não se aplica. Este é um sistema batch sem endpoints REST.

## 5. Principais Regras de Negócio
- Consulta registros de autorização de débito de uma data específica (parâmetro opcional, default D-1)
- Diferencia processamento entre registros tipo "B" (autorização) e "F" (débito efetivado)
- Enriquece dados de parcela quando valor de débito está preenchido
- Enriquece dados de autorização quando valor de débito não está preenchido
- Mapeia códigos de retorno do Banco do Brasil para descrições internas do sistema
- Busca informações complementares por CPF quando ID de autorização tem mais de 10 caracteres
- Valida data de processamento (não pode ser futura)
- Permite execução eventual com data específica via parâmetro
- Consolida informações de múltiplas tabelas (contratos, propostas, parcelas, pessoas, lojas, produtos)

## 6. Relação entre Entidades
- **TbControleArquivoDebitoAtmto** (1) → (N) **TbConteudoLinhaArquivo** → (N) **TbLinhaDetalheArquivo**
- **TbLinhaDetalheArquivo** → **TbRegistroDebito** → **TbParcelaDebito**
- **TbParcelaDebito** → **TbContratoPrincipal** → **TbProposta**
- **TbContratoPrincipal** → **TbContratoDebito** → **TbPessoa**
- **TbRegistroAutorizacaoDebito** → **TbAutorizacaoDebitoPrpsaCntro** → **TbProposta**
- **TbRetornoDebitoAutomatico** e **TbStatusAutorizacaoDebito** fornecem descrições dos códigos de retorno
- **TbBanco** fornece informações dos bancos ativos

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DbGestaoDebitoContaCorrente..TbLInhaDetalheArquivo | Tabela | SELECT | Detalhes das linhas dos arquivos de débito |
| DbGestaoDebitoContaCorrente..TbConteudoLinhaArquivo | Tabela | SELECT | Conteúdo completo das linhas dos arquivos |
| DbGestaoDebitoContaCorrente..TbControleArquivoDebitoAtmto | Tabela | SELECT | Controle dos arquivos de débito automático |
| DbGestaoDebitoContaCorrente..TbRegistroDebito | Tabela | SELECT | Registros de débito |
| DbGestaoDebitoContaCorrente..TbRegistroAutorizacaoDebito | Tabela | SELECT | Registros de autorização de débito |
| DbGestaoDebitoContaCorrente..TbAutorizacaoDebitoPrpsaCntro | Tabela | SELECT | Vínculo autorização x proposta/contrato |
| DbGestaoDebitoContaCorrente..TbRetornoDebitoAutomatico | Tabela | SELECT | Códigos e descrições de retorno de débito |
| DbGestaoDebitoContaCorrente..TbStatusAutorizacaoDebito | Tabela | SELECT | Status de autorização de débito |
| DbGestaoDebitoContaCorrente..TbParametroRetornoDebito | Tabela | SELECT | Parâmetros de retorno de débito |
| DbGestaoDebitoContaCorrente..TbRetornoDebitoSistemaOrigem | Tabela | SELECT | Descrições resumidas de retorno |
| DBGESTAO..TbParcelaDebito | Tabela | SELECT | Parcelas de débito |
| DBGESTAO..TbContratoDebito | Tabela | SELECT | Contratos de débito |
| DBCOR..TbContratoPrincipal | Tabela | SELECT | Contratos principais |
| DBCOR..TbProduto | Tabela | SELECT | Produtos |
| DBCOR..TbBanco | Tabela | SELECT | Bancos ativos |
| DBCOR..TbLoja | Tabela | SELECT | Lojas |
| DBCOR..TbPessoa | Tabela | SELECT | Pessoas/clientes |
| DBCOR..TbSituacaoContrato | Tabela | SELECT | Situações de contrato |
| DBCOR..TbSubProduto | Tabela | SELECT | Sub-produtos |
| DBCOR..TbModalidadeProduto | Tabela | SELECT | Modalidades de produto |
| DBCRED..TbProposta | Tabela | SELECT | Propostas |
| DBCRED..TbPessoaSobAnalise | Tabela | SELECT | Pessoas em análise |
| DBCRED..TbPropostaFavorecido | Tabela | SELECT | Favorecidos de proposta |
| DBGESTAOCP..TbContrato | Tabela | SELECT | Contratos (gestão CP) |
| DBGESTAOCP..TBContratoFinanceiro | Tabela | SELECT | Contratos financeiros |

## 8. Estruturas de Banco de Dados Atualizadas
Não se aplica. O sistema apenas realiza leitura de dados.

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| config.properties | Leitura | ConfiguracoesProperties | Arquivo de configuração com diretório de saída |
| PROCESSAMENTO_DEBITO_CONTA_yyyyMMdd_HHmm.xls | Gravação | ItemWriter | Relatório Excel com registros de débito |
| PROCESSAMENTO_DEBITO_CONTA_yyyyMMdd_HHmm_EVENTUAL.xls | Gravação | ItemWriter | Relatório Excel eventual (com data específica) |
| robo.log | Gravação | Log4j | Log de execução do batch |
| statistics-{executionId}.log | Gravação | Log4j | Estatísticas de execução |

## 10. Filas Lidas
Não se aplica. O sistema não consome mensagens de filas.

## 11. Filas Geradas
Não se aplica. O sistema não publica mensagens em filas.

## 12. Integrações Externas
Não se aplica. O sistema não integra com sistemas externos, apenas com banco de dados interno Sybase.

## 13. Avaliação da Qualidade do Código

**Nota: 5/10**

**Justificativa:**

**Pontos Positivos:**
- Estrutura bem organizada seguindo padrão Spring Batch (Reader/Processor/Writer)
- Separação de responsabilidades com DAOs e interfaces
- Uso de Value Objects para transporte de dados
- Tratamento de exceções com exit codes específicos
- Logging adequado em pontos críticos

**Pontos Negativos:**
- **Código duplicado**: Classe `ConexaoBancoDados` existe em dois pacotes diferentes
- **Queries SQL hardcoded**: Queries complexas construídas via concatenação de strings, dificultando manutenção
- **Lógica de negócio no DAO**: Métodos como `preencherInformacoesParcela` misturam acesso a dados com lógica
- **Métodos muito longos**: `ItemReader.verificaRegistrosDeAut()` e queries no `RegistroAutDebtoQueriesImpl` são extensos
- **Falta de testes**: Estrutura de testes presente mas não implementada
- **Magic numbers e strings**: Códigos como "B", "F", "237" espalhados pelo código
- **Comentários em português misturados com código**: Dificulta padronização
- **Uso de System.out.println**: Em vez de logger apropriado em alguns pontos
- **Tratamento genérico de exceções**: Vários blocos catch(Exception) muito amplos
- **Código comentado**: Query deprecated comentada em vez de removida

## 14. Observações Relevantes
- Sistema preparado para execução em ambiente Windows (.bat) e Unix (.sh)
- Suporta execução agendada (D-1) ou eventual (data específica via parâmetro)
- Configuração de memória JVM: -Xms1024M -Xmx1024M (Windows) / -Xmx512M (Unix)
- Utiliza framework proprietário BV Sistemas para batch
- Arquivo Excel gerado com 30 colunas de informações consolidadas
- Sistema específico para Banco do Brasil (código 237) com tratamentos especiais
- Dependência do driver Sybase jConnect versão 7.07-SP136
- Versionamento: 19.4.1.DEB35-389.2