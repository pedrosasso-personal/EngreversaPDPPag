---
## Ficha Técnica do Sistema

### 1. Descrição Geral
Sistema batch de processamento de baixa operacional de boletos DDA (Débito Direto Autorizado) integrado com a CIP (Câmara Interbancária de Pagamentos). O sistema lê arquivos de retorno CIP em formato XML compactado (.gz), valida e converte os dados usando JAXB, busca informações de títulos no banco de dados, registra a baixa operacional através de stored procedures e move os arquivos processados para diretórios específicos conforme o resultado do processamento (sucesso ou rejeição).

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê arquivos de retorno CIP do diretório configurado, valida existência, renomeia arquivos .gz e move para diretórios de processado/rejeitado |
| **ItemProcessor** | Converte arquivos File em objetos ADDADOCComplexType usando FileUtil |
| **ItemWriter** | Persiste dados de baixa operacional através do RegistrarBoletoImpl |
| **RegistrarBoletoImpl** | Camada de negócio que delega operações para o DAO |
| **RegistrarBoletoDAOImpl** | Camada de persistência que busca títulos DDA e insere baixa operacional via stored procedures |
| **FileUtil** | Utilitário para processamento de arquivos: descompactação GZIP, conversão XML/JAXB, validação XSD, movimentação de arquivos |
| **DatabaseConnection** | Gerenciamento singleton de conexões com pool e controle de transações (autoCommit=false) |
| **MyResumeStrategy** | Estratégia de tratamento de erros do batch, define exit codes baseados em exceções |
| **ADDADOCComplexType** | VO raiz do documento DDA (BCARQ, SISARQ, ESTARQ) |
| **ADDA108RR2ComplexType** | VO de retorno RR2 com lista de títulos de baixa |
| **GrupoADDA108RR2TitComplexType** | VO com dados completos de baixa operacional (27 campos) |
| **ConnectionHelper** | Utilitário para gestão de recursos JDBC e conversões nullable |
| **Constants** | Constantes do sistema incluindo códigos de erro e nomes de filas JMS |

### 3. Tecnologias Utilizadas

- **Framework Batch**: Spring Batch (BV Framework customizado)
- **Persistência**: JDBC, Bitronix JTA
- **Banco de Dados**: Sybase (DBPGF_TES)
- **Marshalling XML**: JAXB 2.3
- **DataSource**: BVJTDSDataSource com Bitronix PoolingDataSource
- **Compressão**: GZIP
- **Encoding**: UTF-16BE, ISO-8859-1
- **Build**: Maven
- **Bibliotecas**: 
  - bv-framework-batch.standalone
  - bv-crypto.core
  - bv-jdbcdriver.driver
  - commons-io
  - javassist
- **JVM**: -Xms512M -Xmx1024M

### 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch sem endpoints REST.

### 5. Principais Regras de Negócio

1. **Validação de Reprocessamento**: Impede o reprocessamento de arquivos já processados anteriormente
2. **Processamento Tipo RR2**: Processa apenas arquivos de retorno tipo RR2 (retorno CIP)
3. **Validação de Título**: Valida existência do título DDA antes de inserir a baixa operacional
4. **Cálculo de Saldo**: Calcula saldo do título como ValorTitulo + VlrBaixaTit (valor negativo)
5. **Conversão de Tipos**: Converte BigInteger para Int em campos específicos durante persistência
6. **Gestão de Arquivos**: Move arquivos para diretórios específicos conforme resultado (processado/rejeitado)
7. **Tratamento de Campos Nullable**: Trata adequadamente campos opcionais (vlrBaixaTit, qtdPgtoRegtd, codPartRecbdrBaixa, etc.)
8. **Validação XSD**: Valida estrutura XML contra schema BCB antes do processamento
9. **Detecção de Tipo**: Detecta automaticamente tipo de arquivo (PRO/ERR) e extrai códigos de erro
10. **Controle Transacional**: Commit/Rollback manual de transações de banco de dados

### 6. Relação entre Entidades

**Entidades Principais:**

- **TituloDDA** (Tabela BD)
  - Identificador: CdTituloDDA
  - Atributos: VrSaldoAtualPagmentoTitulo, VrTitulo, NuIdentificacaoTitulo

- **BaixaOperacional** (Stored Procedure)
  - Relacionamento: N:1 com TituloDDA (via NumIdentcTit)
  - Atributos: 30 parâmetros incluindo identificação, valores, datas, partes envolvidas

- **ADDADOCComplexType** (XML Raiz)
  - Contém: BCARQ (cabeçalho), SISARQ (mensagens), ESTARQ (status)
  - SISARQ contém: ADDA108RR2ComplexType

- **ADDA108RR2ComplexType**
  - Contém: Lista de GrupoADDA108RR2TitComplexType

- **GrupoADDA108RR2TitComplexType**
  - Representa: Dados completos de baixa operacional de um título
  - Relaciona: ISPBs (participantes), portador, pagamento, referências

### 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbTituloDDA | Tabela | SELECT | Busca título DDA por NuIdentificacaoTitulo para obter CdTituloDDA, VrSaldoAtualPagmentoTitulo/VrTitulo |

### 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| PrInserirTituloDDABaixaOperacional | Stored Procedure | INSERT | Insere registro de baixa operacional com 30 parâmetros incluindo identificação, valores, datas, ISPBs, dados do portador e pagamento |
| PrInserirTituloDDABaixaPagamento | Stored Procedure | INSERT | Insere dados de pagamento da baixa (referenciada mas não implementada no código analisado) |
| PrInserirTituloDDABaixaPessoa | Stored Procedure | INSERT | Insere dados de pessoa relacionada à baixa (referenciada mas não implementada no código analisado) |
| PrInserirTituloDDABaixaReferencia | Stored Procedure | INSERT | Insere referências da baixa (referenciada mas não implementada no código analisado) |

### 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| *.gz (arquivos retorno CIP) | Leitura | \\\\bvnet\\mor\\BATCH\\PGFT\\DDA\\entrada\\ / ItemReader | Arquivos XML compactados com retornos CIP tipo RR2 |
| processamento.xml | Gravação | \\\\bvnet\\mor\\BATCH\\PGFT\\DDA\\entrada\\temp\\ / FileUtil | Arquivo temporário de processamento |
| *.gz processados | Movimentação | \\\\bvnet\\mor\\BATCH\\PGFT\\DDA\\entrada\\processed\\ / ItemReader | Arquivos processados com sucesso |
| *.gz rejeitados | Movimentação | \\\\bvnet\\mor\\BATCH\\PGFT\\DDA\\entrada\\rejeitado\\ / ItemReader | Arquivos rejeitados por erro |
| tlogs Bitronix | Remoção | Diretório de execução / Script BAT | Logs transacionais do Bitronix removidos após execução |

### 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas. As filas JMS definidas em Constants são apenas constantes de referência não utilizadas neste batch específico.

### 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas. As filas JMS definidas em Constants (QL_COBR.*, QR.COBR.*) são apenas constantes de referência não utilizadas neste batch específico.

### 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **CIP (Câmara Interbancária de Pagamentos)** | Arquivo | Recebe arquivos de retorno RR2 em formato XML/GZIP com dados de baixa operacional de boletos DDA |
| **Banco de Dados Sybase (DBPGF_TES)** | JDBC | Servidor sybdesspb:6500 para consulta de títulos e registro de baixas operacionais |
| **Sistema de Arquivos de Rede** | File System | Rede Windows \\\\bvnet\\mor\\BATCH\\PGFT\\DDA\\ para leitura/gravação de arquivos |
| **Schema BCB (Banco Central)** | XSD | Validação de estrutura XML contra schema http://www.bcb.gov.br/ARQ/ADDA108.xsd |

### 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades em camadas (Reader, Processor, Writer, DAO, VO)
- Uso adequado de padrões como DAO, DTO e Strategy
- Tratamento estruturado de exceções com códigos específicos
- Uso de JAXB para marshalling/unmarshalling XML
- Gestão adequada de recursos JDBC com helpers
- Configuração externalizada em properties
- Controle transacional explícito

**Pontos de Melhoria:**
- Falta de documentação JavaDoc nas classes principais
- Código de teste misturado com código de produção em alguns pacotes
- Uso de singleton para DatabaseConnection pode dificultar testes
- Hardcoding de alguns valores (ex: CNPJ_BV = 123)
- Falta de logs estruturados para auditoria
- Conversões manuais de tipos poderiam usar bibliotecas especializadas
- Stored procedures com 30 parâmetros indicam possível necessidade de refatoração do modelo de dados
- Falta de tratamento de encoding em alguns pontos (mistura UTF-16BE e ISO-8859-1)
- Código de utilitários muito acoplado (FileUtil com múltiplas responsabilidades)

### 14. Observações Relevantes

1. **Ambiente de Produção**: Sistema configurado para ambiente PROD com caminhos de rede específicos (\\\\bvnet\\mor\\BATCH\\PGFT\\DDA\\)

2. **Códigos de Erro Padronizados**: Sistema utiliza códigos de erro específicos (0, 11-15, 26, 57-58) para diferentes situações de falha

3. **Charset Específico**: Utiliza ISO-8859-1 para conexão com banco e UTF-16BE para arquivos XML

4. **Pool de Conexões**: Configurado com máximo de 5 conexões simultâneas

5. **Parâmetros de Execução**: Batch recebe três parâmetros via linha de comando: PARAM_NOME_ROBO, PARAM_EXECUTION_ID, PARAM_NOME_ARQUIVO

6. **Namespace BCB**: Todos os VOs seguem o schema do Banco Central (http://www.bcb.gov.br/ARQ/ADDA108.xsd)

7. **Controle de Reprocessamento**: Sistema previne reprocessamento através de movimentação de arquivos e validação de existência

8. **Gestão de Memória**: JVM configurada com heap mínimo de 512MB e máximo de 1024MB

9. **Framework Customizado**: Utiliza framework batch customizado do Banco Votorantim (bv-framework-batch.standalone)

10. **Status de Título**: Sistema trabalha com status específicos como "Baixa decurso prazo" (12) e "Baixa solicitação banco cedente" (10)

11. **Filas JMS Não Utilizadas**: Apesar de definidas 10 filas JMS em Constants, elas não são utilizadas neste batch específico, sugerindo que fazem parte de um framework maior ou foram planejadas para uso futuro

12. **Bitronix Transaction Manager**: Sistema utiliza Bitronix para gerenciamento de transações JTA, com limpeza automática de tlogs após execução