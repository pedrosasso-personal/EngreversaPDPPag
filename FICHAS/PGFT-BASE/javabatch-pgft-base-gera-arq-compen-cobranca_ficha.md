# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java responsável por gerar arquivos de compensação bancária de cobrança no formato COB605. O sistema consulta lançamentos de tesouraria pendentes de compensação no banco de dados DBPGF_TES, agrupa por banco favorecido (ISPB), gera arquivos texto estruturados com header, detalhes e trailers, e atualiza o status dos processamentos. É executado de forma agendada para processar remessas de compensação bancária.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê registros de processamento de compensação pendentes (status '1', tipo '2') do banco de dados |
| **ItemProcessor** | Processa cada arquivo de compensação, gerando o arquivo físico COB605 com formatação específica |
| **ItemWriter** | Atualiza status do processamento e registra informações do arquivo gerado no banco |
| **BDbPgfTes** | Camada de negócio que orquestra chamadas aos DAOs |
| **DAODbPgfTesImpl** | Implementação de acesso a dados, executa queries e procedures no banco DBPGF_TES |
| **CompensacaoCobranca** | Modelo de dados representando um lançamento de cobrança a compensar |
| **ProcessamentoCompensacao** | Modelo representando um processamento de compensação |
| **RegistroCompensacao** | Modelo para registro de arquivo gerado |
| **Remessa** | Modelo contendo número de remessa e versão do arquivo |
| **BarCodeBuilder** | Utilitário para decodificar código de barras em representação numérica |
| **CompResumeStrategy** | Estratégia de tratamento de erros e resumo do job |

## 3. Tecnologias Utilizadas

- **Framework Batch**: Spring Batch (BV Framework Batch Standalone)
- **Build Tool**: Maven
- **Linguagem**: Java
- **Banco de Dados**: Sybase (DBPGF_TES via JTDS driver)
- **Gerenciador de Transações**: Bitronix (JTA)
- **Logging**: Log4j e Apache Commons Logging
- **Testes**: JUnit
- **Utilitários**: Apache Commons Lang

## 4. Principais Endpoints REST

Não se aplica - sistema batch sem endpoints REST.

## 5. Principais Regras de Negócio

- Processa apenas arquivos de compensação com tipo '2' (cobrança) e status '1' (pendente)
- Agrupa lançamentos por banco favorecido (ISPB) em lotes de até 1000 documentos
- Gera arquivo COB605 com estrutura: Header (1 linha) + Detalhes (N linhas) + Trailer de Lote + Trailer de Arquivo
- Código de barras é decodificado em representação numérica específica (47 posições)
- Valores monetários são formatados com 2 casas decimais sem separador
- Arquivo gerado tem nome recuperado do banco de dados
- Status de processamento: 1=Pendente, 2=Em Processamento, 3=Gerado com Sucesso, 4=Erro
- Centro processador extraído da 8ª posição do nome do arquivo
- Banco remetente fixo: 018 (código) / 59588111 (ISPB)
- Agência remetente fixa: 0001
- Arquivos salvos em: `D:\_robos\javabatch-pgft-base-gera-arq-compen-cobranca\gerados\`

## 6. Relação entre Entidades

**ProcessamentoCompensacao** (1) -----> (N) **RegistroCompensacao**
- Um processamento pode gerar múltiplos registros de arquivo

**ProcessamentoCompensacao** (1) -----> (N) **CompensacaoCobranca**
- Um processamento contém múltiplos lançamentos de cobrança

**CompensacaoCobranca** (N) -----> (1) **Banco** (via ISPB)
- Cada lançamento está associado a um banco favorecido

**Remessa** - Entidade auxiliar para controle de numeração sequencial de arquivos

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbProcessamentoCompensacao | Tabela | SELECT | Consulta processamentos pendentes de compensação |
| TbArquivoCompensacao | Tabela | SELECT | Consulta códigos de arquivos pendentes e nomes de arquivo |
| TBL_LANCAMENTO | Tabela | SELECT | Consulta lançamentos de tesouraria para compensação |
| TbDetalheArquivoCompensacao | Tabela | SELECT | Consulta detalhes dos lançamentos por arquivo |
| TbStatusCompensacao | Tabela | SELECT | Consulta descrição dos status de compensação |
| dbglobal..tbbanco | Tabela | SELECT | Consulta código ISPB dos bancos favorecidos |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbProcessamentoCompensacao | Tabela | UPDATE | Atualiza status do processamento (1→3 ou 4) |
| TbRegistroArquivoCompensacao | Tabela | INSERT | Insere registro do arquivo gerado com sucesso/erro |
| TbArquivoCompensacao | Tabela | UPDATE | Atualiza status, quantidade de registros, tamanho e valor total |
| TbDetalheArquivoCompensacao | Tabela | INSERT | Insere detalhe de lançamento no arquivo (via procedure) |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| COB605_*.txt | Gravação | ItemProcessor.processarArquivoCOB605() | Arquivo de compensação bancária gerado com header, detalhes e trailers |
| job-definitions.xml | Leitura | Spring Context | Configuração do job batch |
| job-resources.xml | Leitura | Spring Context | Configuração de datasources e recursos |
| log4j.xml | Leitura | Log4j | Configuração de logging |

## 10. Filas Lidas

Não se aplica - sistema não consome filas.

## 11. Filas Geradas

Não se aplica - sistema não publica em filas.

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Banco Sybase DBPGF_TES | Banco de Dados | Banco principal de tesouraria para leitura e atualização de dados de compensação |
| Banco dbglobal | Banco de Dados | Banco auxiliar para consulta de códigos ISPB dos bancos |
| Sistema de Arquivos | File System | Gravação de arquivos COB605 em diretório específico |

## 13. Avaliação da Qualidade do Código

**Nota: 4/10**

**Justificativa:**

**Pontos Negativos:**
- Código legado com comentários em encoding incorreto (caracteres especiais corrompidos)
- Hardcoded de paths absolutos (`D:\_robos\...`) tornando o código não portável
- Valores mágicos espalhados pelo código (códigos de banco, status, tamanhos)
- Lógica de negócio complexa concentrada no ItemProcessor (classe com mais de 400 linhas)
- Tratamento de exceções genérico e pouco informativo
- Falta de validações de entrada em diversos pontos
- Manipulação manual de strings para formatação de valores monetários (propenso a erros)
- SQL embutido em classe separada mas ainda como strings concatenadas
- Falta de testes unitários (apenas um teste de integração básico)
- Uso de tipos primitivos onde objetos seriam mais apropriados
- Nomenclatura inconsistente (mix de português e inglês)

**Pontos Positivos:**
- Uso de padrão DAO para acesso a dados
- Separação em camadas (DAO, Business, Batch)
- Uso de framework batch consolidado (Spring Batch)
- Gerenciamento transacional com JTA

## 14. Observações Relevantes

- Sistema crítico para operação de compensação bancária - falhas podem impactar fluxo de caixa
- Procedure `PrObterNovaRemessa` e `PrInserirDetArqCompensacao` são chamadas mas não temos visibilidade do código
- Formato COB605 parece ser padrão específico do Banco Votorantim
- Sistema aparenta ser legado migrado de VB6 (comentários mencionam "sistema do PGFT, em VB6")
- Commit interval configurado para 1, processando item a item
- Timeout de transação configurado para 10 segundos (pode ser insuficiente para grandes volumes)
- Não há mecanismo de retry em caso de falha
- Logs em português dificultam troubleshooting em ambientes internacionais
- Ausência de documentação técnica inline adequada
- Sistema não possui mecanismo de rollback em caso de falha parcial na geração do arquivo