# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java responsável pela geração de arquivos de remessa de boletos no formato COB605 para a ABBC (Associação Brasileira de Bancos). O sistema consulta lançamentos de tesouraria pendentes no banco de dados Sybase, gera arquivos de compensação seguindo o layout específico da ABBC, valida a consistência dos dados e move os arquivos gerados para o diretório de saída. Utiliza o framework BV Sistemas para processamento batch com controle transacional e estratégia de recuperação em caso de falhas.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê lançamentos de tesouraria do banco de dados e controla o fluxo de processamento em loop |
| **ItemProcessor** | Processa os itens lidos (implementação passthrough sem transformações) |
| **ItemWriter** | Escreve os arquivos COB605, valida duplicidades e consistência dos dados |
| **MultiFileWriterAdapter** | Gerencia a criação de múltiplos arquivos de compensação e controla mudanças de arquivo |
| **ArquivoCob605Writer** | Escreve registros no formato COB605 (header, detalhe, fechamento de lote e trailer) |
| **ArquivoCob605Layout** | Define o layout posicional dos registros do arquivo COB605 |
| **GeracaoABBCBusinessImpl** | Camada de negócio que orquestra operações de banco de dados |
| **GeracaoABBCDaoImpl** | Acesso a dados via JDBC para consultas e atualizações |
| **GlobalContext** | Contexto global com parâmetros de execução do job |
| **MyResumeStrategy** | Estratégia de recuperação em caso de falhas, realizando rollback |

## 3. Tecnologias Utilizadas

- **Java** (versão não especificada explicitamente)
- **Spring Framework** (configuração XML, injeção de dependências)
- **Spring Batch** (framework BV Sistemas baseado em Spring Batch)
- **Maven** (gerenciamento de dependências e build)
- **Sybase ASE** (banco de dados - DBPGF_TES)
- **JDBC** (acesso a dados via DriverManager e PreparedStatement)
- **BV JDBC Driver** (driver customizado com suporte a transações)
- **Bitronix** (gerenciador de transações JTA)
- **Log4j** (logging)
- **JUnit** (testes unitários)

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch sem endpoints REST.

## 5. Principais Regras de Negócio

1. **Limite STR**: Apenas lançamentos com valor abaixo do limite STR são processados
2. **Arquivos Completos**: Opcionalmente, só gera arquivos se houver pelo menos 20.000 registros
3. **Agrupamento por Favorecido**: Detalhes são agrupados em lotes por ISPB do favorecido
4. **Tamanho Máximo de Lote**: Cada lote contém no máximo 400 registros
5. **Validação de Duplicidade**: Verifica duplicações tanto no arquivo quanto no banco de dados
6. **Validação de Totalizadores**: Valida quantidade de registros e valor total entre arquivo físico e banco
7. **Controle de Concorrência**: Não permite geração se houver arquivos pendentes recentes (últimos 15 minutos)
8. **Geração de Código de Barras**: Converte código de barras digitável para formato de 44 posições
9. **Versionamento de Arquivos**: Controla versão sequencial dos arquivos gerados
10. **Status de Compensação**: Gerencia status dos lançamentos (pendente=1, selecionado=2, gerado=3, rejeitado=5)

## 6. Relação entre Entidades

**ArquivoCompensacaoVO** (1) ----< (N) **DetalheArquivoCompensacaoVO** (N) >---- (1) **LancamentoVO**

- **ArquivoCompensacaoVO**: Representa o arquivo de compensação gerado, contendo metadados como nome, versão, quantidade de registros e valor total
- **DetalheArquivoCompensacaoVO**: Representa cada linha de detalhe do arquivo, associando um arquivo de compensação a um lançamento
- **LancamentoVO**: Representa um lançamento de tesouraria (boleto) a ser incluído no arquivo

Relacionamentos adicionais:
- **ArquivoCob605Header**: Dados do cabeçalho do arquivo COB605
- **ArquivoCob605Detalhe**: Dados de cada registro de detalhe no formato COB605
- **ArquivoCob605Sumarizador**: Acumuladores e contadores para geração do arquivo

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TBL_SETUP_TESOURARIA | Tabela | SELECT | Consulta valor limite STR para processamento de boletos |
| TbArquivoCompensacao | Tabela | SELECT | Verifica arquivos pendentes e busca totalizadores |
| TbDetalheArquivoCompensacao | Tabela | SELECT | Valida duplicidades de lançamentos |
| PrConsultaDadosCompensacaoV2 | Procedure | EXECUTE | Consulta lançamentos de tesouraria para geração do arquivo |
| PrConsultarTotalArquivoCompensacao | Procedure | EXECUTE | Obtém totalizadores do arquivo gerado |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbArquivoCompensacao | Tabela | INSERT/UPDATE/DELETE | Cria novo registro de arquivo, atualiza status ou exclui em caso de erro |
| TbDetalheArquivoCompensacao | Tabela | INSERT/DELETE | Insere detalhes dos lançamentos processados ou exclui em rollback |
| PrCriarNovaRemessa | Procedure | EXECUTE | Cria novo registro de remessa no banco |
| PrInserirDetArqCompensacaoV2 | Procedure | EXECUTE | Insere detalhe do arquivo de compensação |
| PrInserirArquivoCompensacao | Procedure | EXECUTE | Atualiza arquivo de compensação com totalizadores finais |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| config.properties | Leitura | Resources/Propriedades | Configurações de diretórios e prefixos de arquivo |
| HCB*.txt (COB605) | Gravação | MultiFileWriterAdapter/FileCreator | Arquivos de remessa de boletos no formato COB605 |
| robo.log | Gravação | Log4j (roboFile appender) | Log de execução do robô |
| statistics-{executionId}.log | Gravação | Log4j (statistics appender) | Log de estatísticas de execução |

**Diretórios:**
- `{abbc.path.processamento}`: Diretório temporário onde arquivos são gerados
- `{abbc.path.home}/{cod_banco}/{abbc.dir.saida}`: Diretório final para arquivos processados

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas.

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Banco de Dados Sybase (DBPGF_TES) | JDBC | Consulta lançamentos de tesouraria e persiste informações dos arquivos gerados |
| ABBC (Associação Brasileira de Bancos) | Arquivo | Gera arquivos de remessa no formato COB605 para compensação bancária |

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Separação clara de responsabilidades (DAO, Business, Batch)
- Uso de padrões de projeto (Strategy, Adapter, Template Method)
- Validações consistentes de duplicidade e totalizadores
- Tratamento de exceções centralizado
- Uso de framework batch consolidado

**Pontos Negativos:**
- Código com comentários em português misturados com código
- Strings SQL hardcoded em interface (GeracaoABBCDaoQueries)
- Falta de documentação JavaDoc nas classes principais
- Uso de `StringBuffer` em vez de `StringBuilder` em alguns pontos
- Lógica de negócio misturada com código de infraestrutura em algumas classes
- Configurações hardcoded (ex: tamanho máximo de lote = 400)
- Falta de testes unitários abrangentes (apenas teste de integração)
- Uso de encoding ISO-8859-1 em vez de UTF-8
- Código de formatação posicional complexo e pouco legível (ArquivoCob605Layout)
- Tratamento de exceções genérico em alguns pontos

## 14. Observações Relevantes

1. **Ambiente de Execução**: Sistema configurado para ambientes DEV/UAT com conexões Sybase específicas
2. **Formato de Arquivo**: Layout posicional fixo de 160 caracteres por linha no formato COB605
3. **Controle de Versão**: Arquivos possuem versionamento sequencial automático
4. **Processamento em Loop**: Sistema pode executar continuamente (parâmetro LOOP_GERACAO)
5. **Código de Barras**: Conversão específica de 47 para 44 posições seguindo regra da ABBC
6. **Rollback Automático**: Em caso de erro, a estratégia MyResumeStrategy remove registros e arquivos gerados
7. **Validação Rigorosa**: Múltiplas validações garantem integridade dos dados (duplicidade, totalizadores, arquivo físico)
8. **Prefixo Configurável**: Prefixo do arquivo (HCB) é configurável via properties
9. **Banco Remetente**: Suporta múltiplos bancos remetentes (parâmetro COD_BANCO, default 655)
10. **Framework Proprietário**: Utiliza framework BV Sistemas, o que pode dificultar manutenção por equipes externas