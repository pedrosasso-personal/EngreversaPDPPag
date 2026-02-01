# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java desenvolvido para processar arquivos de baixa efetiva de boletos DDA (Débito Direto Autorizado) retornados pela CIP (Câmara Interbancária de Pagamentos). O sistema lê arquivos compactados em formato .gz contendo XMLs com informações de baixa de títulos, descompacta, valida, processa as informações e registra as baixas efetivas no banco de dados. Após o processamento, move os arquivos para diretórios de processados ou rejeitados conforme o resultado da execução.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê arquivos .gz do diretório de entrada, renomeia se necessário e disponibiliza para processamento |
| **ItemProcessor** | Descompacta e converte arquivos XML em objetos Java (ADDADOCComplexType) |
| **ItemWriter** | Persiste as informações de baixa efetiva no banco de dados através de stored procedures |
| **RegistrarBoletoImpl** | Implementa a lógica de negócio para registro de retorno CIP |
| **RegistrarBoletoDAOImpl** | Executa operações de banco de dados (consultas e inserções de baixa efetiva) |
| **FileUtil** | Utilitário para manipulação de arquivos (compressão, descompressão, conversão XML, movimentação) |
| **DatabaseConnection** | Gerencia conexões com o banco de dados através de DataSource |
| **MyResumeStrategy** | Estratégia de tratamento de erros e definição de códigos de saída |
| **TituloDDA** | DTO representando um título DDA com código e valor |
| **Constants** | Interface com constantes do sistema (códigos de erro, filas, configurações) |

## 3. Tecnologias Utilizadas

- **Framework Batch**: Spring Batch (BV Framework Batch - versão standalone customizada)
- **Linguagem**: Java
- **Gerenciamento de Dependências**: Maven
- **Banco de Dados**: Sybase (servidor: sybdesspb, porta: 6500, database: DBPGF_TES)
- **Driver JDBC**: BVJTDSDataSource (driver customizado BV Sistemas)
- **Gerenciamento de Transações**: Bitronix Transaction Manager
- **Marshalling/Unmarshalling XML**: JAXB (Java Architecture for XML Binding)
- **Compressão**: GZIP
- **Logging**: Log4j + BVLogger (framework customizado)
- **Testes**: JUnit
- **Encoding**: UTF-16BE para arquivos XML

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch que não expõe endpoints REST.

## 5. Principais Regras de Negócio

1. **Processamento de Arquivos RR2**: Apenas arquivos contendo "RR2" no nome são processados para registro de baixa efetiva
2. **Validação de Título**: Antes de registrar a baixa, o sistema busca o título no banco através do número de identificação
3. **Registro Duplo de Baixa**: Para cada título processado, são executadas duas inserções:
   - Baixa efetiva padrão (PrInserirTituloDDABaixaEfetiva)
   - Baixa efetiva compatível com ADDA127 (PrInserirTituloDDABaixaEfetivaADDA127)
4. **Tratamento de Arquivos PRO e ERR**: Sistema diferencia arquivos de processamento (PRO) e erro (ERR) da CIP
5. **Movimentação de Arquivos**: Após processamento, arquivos são movidos para diretórios específicos:
   - Sucesso (exitCode = 0): diretório "processado"
   - Erro: diretório "rejeitado"
6. **Conversão de Valores**: Tratamento especial para conversão de BigInteger para BigDecimal/Integer com validação de nulos
7. **Encoding UTF-16BE**: Arquivos XML são processados em UTF-16BE conforme padrão CIP

## 6. Relação entre Entidades

**TituloDDA** (DTO)
- cdTitulo: Integer (chave primária)
- valorTitulo: BigDecimal

**ADDADOCComplexType** (XML Schema)
- BCARQ: BCARQComplexType (informações do arquivo)
- SISARQ: SISARQComplexType (contém ADDA118RR2)
  - ADDA118RR2: ADDA118RR2ComplexType
    - GrupoADDA118RR2Tit: List<GrupoADDA118RR2TitComplexType> (títulos)

**GrupoADDA118RR2TitComplexType** (Dados do Título)
- numIdentcTit: BigInteger (identificador do título)
- numIdentcBaixaEft: BigInteger
- vlrSldTotAtlPgtoTit: BigDecimal
- sitTitPgto: String (situação título pagamento)
- tpBaixaEft: String (tipo baixa efetiva)
- numCodBarrasBaixaEft: String
- qtdPgtoParclRegtd: BigInteger
- sitTit: String (situação título)
- dtHrSitBaixaEft: XMLGregorianCalendar
- vlrBaixaEftTit: BigDecimal
- numIdentcBaixaOperac: BigInteger

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbTituloDDA | Tabela | SELECT | Busca informações do título DDA (código e valor) através do número de identificação |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbTituloDDABaixaEfetiva | Tabela | INSERT | Registra baixa efetiva do título através da stored procedure PrInserirTituloDDABaixaEfetiva (14 parâmetros) |
| TbTituloDDABaixaEfetiva | Tabela | INSERT | Registra baixa efetiva compatível com ADDA127 através da stored procedure PrInserirTituloDDABaixaEfetivaADDA127 (15 parâmetros) |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| ADDA118*.gz | Leitura | ItemReader / FileUtil | Arquivos compactados contendo XMLs de retorno CIP com baixas efetivas |
| processamento.xml_*.gz | Gravação | FileUtil.salvarArquivoXML | Arquivo XML temporário descompactado para processamento |
| config.properties | Leitura | Resources / Propriedades | Arquivo de configuração com caminhos de diretórios |
| log4j.xml | Leitura | Log4j | Configuração de logs do sistema |
| robo.log | Gravação | Log4j RollingFileAppender | Log de execução do batch (máx 2MB, 5 backups) |
| statistics-${executionId}.log | Gravação | BvDailyRollingFileAppender | Log de estatísticas de execução |

**Diretórios:**
- Entrada: `\\bvnet\mor\BATCH\PGFT\DDA\entrada\`
- Processado: `\\bvnet\mor\BATCH\PGFT\DDA\entrada\processado\`
- Rejeitado: `\\bvnet\mor\BATCH\PGFT\DDA\entrada\rejeitado\`
- Temporário: `\\bvnet\mor\BATCH\PGFT\DDA\entrada\temp\`

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas, embora a classe Constants defina constantes para filas JMS (QL_COBR e QR_COBR), estas não são utilizadas neste componente específico.

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas.

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **CIP (Câmara Interbancária de Pagamentos)** | Arquivo | Recebe arquivos XML compactados com retornos de baixa efetiva de boletos DDA |
| **Banco de Dados Sybase** | JDBC | Conexão com servidor sybdesspb:6500, database DBPGF_TES para persistência de dados |

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Uso adequado do padrão de arquitetura em camadas (batch, business, dao, util)
- Separação de responsabilidades entre leitura, processamento e escrita
- Uso de framework batch estruturado (Spring Batch)
- Tratamento de exceções com códigos de erro padronizados
- Logging adequado em pontos críticos

**Pontos Negativos:**
- **Código comentado em excesso**: Múltiplas configurações de ambiente comentadas no config.properties dificultam manutenção
- **Falta de documentação**: Ausência de JavaDoc nas classes e métodos
- **Hardcoded values**: Credenciais de banco (usuário/senha) expostas em arquivos de configuração
- **Tratamento genérico de exceções**: Uso excessivo de `catch(Exception e)` sem tratamento específico
- **Código duplicado**: Múltiplos PreparedStatements (1 a 8) no AbstractDAO indicam possível necessidade de refatoração
- **Complexidade no FileUtil**: Classe com muitas responsabilidades (compressão, conversão, validação, movimentação)
- **Testes limitados**: Apenas um teste de integração básico
- **Encoding misto**: Uso de ISO-8859-1 e UTF-16BE pode causar problemas de caracteres especiais
- **Falta de validações**: Pouca validação de dados antes de inserir no banco
- **Classes VO não enviadas**: Grande quantidade de classes de erro/validação não incluídas na análise

## 14. Observações Relevantes

1. **Ambiente Multi-Ambiente**: Sistema preparado para múltiplos ambientes (LOCAL, DES, QA, UAT, PROD) através de configurações comentadas
2. **Framework Proprietário**: Utiliza framework BV Sistemas customizado, o que pode dificultar manutenção por equipes externas
3. **Padrão CIP**: Segue padrões específicos da Câmara Interbancária de Pagamentos para arquivos DDA
4. **Transações XA**: Uso de Bitronix para gerenciamento de transações distribuídas
5. **Processamento Síncrono**: Sistema processa um arquivo por vez de forma sequencial
6. **Rollback Automático**: Em caso de erro, conexão executa rollback e arquivo é movido para diretório de rejeitados
7. **Versionamento**: Sistema na versão 0.6.0, indicando ainda em fase de evolução
8. **Dependências Antigas**: Uso de Spring Batch 2.0 e Log4j 1.x (versões antigas)
9. **Stored Procedures**: Lógica de negócio crítica delegada ao banco de dados através de procedures
10. **Parâmetro de Execução**: Sistema recebe nome do arquivo como parâmetro via linha de comando