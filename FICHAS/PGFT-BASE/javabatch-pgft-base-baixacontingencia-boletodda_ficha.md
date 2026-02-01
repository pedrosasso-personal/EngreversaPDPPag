# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java responsável pelo processamento de arquivos de baixa operacional de boletos DDA (Débito Direto Autorizado) em contingência. O sistema lê arquivos compactados (.gz) retornados pela CIP (Câmara Interbancária de Pagamentos), descompacta, converte de XML para objetos Java, valida e registra as informações de baixa operacional de boletos no banco de dados. Trata arquivos de processamento (PRO), retorno (RR2) e erro (ERR), movendo-os para diretórios específicos conforme o resultado do processamento.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê arquivos .gz do diretório de entrada, renomeia se necessário e disponibiliza para processamento |
| **ItemProcessor** | Descompacta e converte arquivos XML em objetos Java (ADDADOCComplexType) |
| **ItemWriter** | Persiste informações de baixa operacional no banco de dados através da camada de negócio |
| **RegistrarBoletoImpl** | Camada de negócio que orquestra o registro de retorno CIP |
| **RegistrarBoletoDAOImpl** | Camada de acesso a dados, executa procedures e queries no banco Sybase |
| **FileUtil** | Utilitário para manipulação de arquivos: compressão/descompressão, conversão XML, movimentação |
| **DatabaseConnection** | Gerencia conexões com banco de dados usando DataSource |
| **MyResumeStrategy** | Estratégia de tratamento de erros e definição de exit codes |
| **TituloDDA** | DTO para transporte de dados de títulos DDA |
| **ADDADOCComplexType** | Classe gerada por JAXB representando estrutura XML de documentos DDA |

## 3. Tecnologias Utilizadas

- **Java** (versão não especificada no código fornecido)
- **Maven** - Gerenciamento de dependências e build
- **Spring Framework** - Configuração e injeção de dependências
- **BV Framework Batch** (bv-framework-batch.standalone) - Framework proprietário para processamento batch
- **JAXB** (Java Architecture for XML Binding) - Conversão XML/Objeto
- **Bitronix** - Gerenciador de transações XA
- **Sybase** - Banco de dados (servidor: sybdesspb, database: DBPGF_TES)
- **JUnit 4.12** - Testes unitários
- **Mockito 1.10.19** - Mocks para testes
- **Log4j** - Logging
- **Commons IO** - Manipulação de arquivos
- **XStream** - Processamento XML adicional

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch sem endpoints REST.

## 5. Principais Regras de Negócio

1. **Processamento de Arquivos de Retorno CIP**: Lê arquivos compactados (.gz) retornados pela CIP contendo informações de baixa de boletos DDA
2. **Validação de Tipo de Arquivo**: Identifica e processa diferentes tipos de arquivo (PRO - processamento, RR2 - retorno, ERR - erro)
3. **Busca de Título**: Localiza título DDA no banco através do número de identificação antes de registrar baixa
4. **Registro de Baixa Operacional**: Insere informações de baixa operacional através de procedure `PrInserirTituloDDABaixaOperacional` com 26 parâmetros
5. **Cálculo de Saldo**: Calcula saldo do título subtraindo valor da baixa do valor original
6. **Movimentação de Arquivos**: Move arquivos processados para diretório de sucesso ou rejeição conforme exit code
7. **Tratamento de Contingência**: Processa operações em contingência identificadas pelo indicador `IndrOpContg`
8. **Conversão de Encoding**: Converte arquivos de UTF-16BE para UTF-8 durante descompressão
9. **Validação de Situação de Pagamento**: Processa diferentes situações de título (código 12 - baixa por decurso de prazo, código 10 - baixa por solicitação)

## 6. Relação entre Entidades

**TituloDDA** (DTO)
- Atributos: cdTitulo (Integer), valorTitulo (BigDecimal)
- Representa título DDA recuperado do banco

**ADDADOCComplexType** (Entidade XML)
- Contém: BCARQ (cabeçalho), SISARQ (sistema de arquivo)
- SISARQ contém ADDA114RR2 com lista de GrupoADDA114RR2TitComplexType

**GrupoADDA114RR2TitComplexType** (Detalhes do Título)
- Informações de baixa: numIdentcBaixa, vlrBaixaTit, dtHrSitBaixa
- Informações de pagamento: qtdPgtoRegtd, vlrTotPgto, sitTitPgto
- Informações do portador: codPartRecbdrBaixa, nomRzSocPort

**Relacionamento**: Um arquivo ADDADOC pode conter múltiplos títulos (GrupoADDA114RR2Tit), cada um vinculado a um TituloDDA no banco de dados através do NumIdentcTit.

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbTituloDDA | tabela | SELECT | Busca título DDA por número de identificação, retornando código e valor do título |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbTituloDDABaixaOperacional (via procedure) | tabela | INSERT | Insere registro de baixa operacional através da procedure `PrInserirTituloDDABaixaOperacional` com 26 parâmetros incluindo dados do título, baixa, pagamento e portador |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| ADDA114_*.gz | leitura | ItemReader / FileUtil | Arquivos compactados retornados pela CIP contendo XMLs de baixa de boletos |
| processamento.xml | gravação | FileUtil.salvarArquivoXML | Arquivo XML temporário descompactado para processamento |
| ADDA114_*_PRO.gz | leitura | ItemProcessor / FileUtil | Arquivo de processamento (confirmação) |
| ADDA114_*_RR2.gz | leitura | ItemProcessor / FileUtil | Arquivo de retorno com dados de baixa |
| ADDA114_*_ERR.gz | leitura | ItemProcessor / FileUtil | Arquivo de erro com códigos de rejeição |
| robo.log | gravação | Log4j | Log de execução do robô |
| statistics-{executionId}.log | gravação | Log4j / BvDailyRollingFileAppender | Log de estatísticas de execução |

**Diretórios configuráveis por ambiente:**
- Entrada: `CAMINHO_RET` (ex: \\\\bvnet\\mor\\BATCH\\PGFT\\DDA\\entrada\\)
- Processados: `CAMINHO_RET_PROCESSADO`
- Rejeitados: `CAMINHO_RET_REJEITADO`
- Temporário: `CAMINHO_PROCESSAMENTO_ROBO`

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas, apenas processa arquivos do sistema de arquivos.

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas, apenas grava no banco de dados.

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **CIP (Câmara Interbancária de Pagamentos)** | Arquivo | Recebe arquivos de retorno de baixa de boletos DDA através de diretório compartilhado (\\\\bvnet\\mor\\BATCH\\PGFT\\DDA\\entrada\\) |
| **Banco Sybase** | Banco de Dados | Servidor sybdesspb:6500, database DBPGF_TES, charset iso-8859-1 |

## 13. Avaliação da Qualidade do Código

**Nota: 5/10**

**Justificativa:**

**Pontos Positivos:**
- Separação clara de responsabilidades em camadas (batch, business, dao, util)
- Uso de interfaces para contratos (RegistrarBoleto, RegistrarBoletoDAO)
- Tratamento de exceções com códigos de erro específicos
- Testes unitários com Mockito
- Logging estruturado

**Pontos Negativos:**
- **Código comentado**: Métodos inteiros comentados (inserirBaixaPagamento, inserirBaixaPessoa, inserirBaixaReferencia) indicando funcionalidades incompletas ou abandonadas
- **Hardcoded values**: Credenciais de banco em XML de configuração (usuário/senha)
- **Encoding inconsistente**: Comentários em ISO-8859-1 com caracteres corrompidos (�)
- **Falta de documentação**: Ausência de JavaDoc em métodos críticos
- **Gestão de recursos**: Múltiplos PreparedStatements (até 8) na classe AbstractDAO sem justificativa clara
- **Tratamento de erros genérico**: Muitos catch(Exception) sem tratamento específico
- **Acoplamento**: DatabaseConnection usa singleton estático dificultando testes
- **Magic numbers**: Valores numéricos sem constantes explicativas (ex: 26 parâmetros na procedure)
- **Complexidade**: Classe FileUtil com muitas responsabilidades (compressão, conversão, validação, movimentação)

## 14. Observações Relevantes

1. **Ambientes Configurados**: O sistema possui configurações comentadas para LOCAL, DES, QA, UAT e PROD, com apenas PROD ativo
2. **Framework Proprietário**: Utiliza framework BV Sistemas (bv-framework-batch) que não é público
3. **Processamento Transacional**: Usa controle transacional manual com commit/rollback explícitos
4. **Padrão de Nomenclatura CIP**: Arquivos seguem padrão ADDA114_ISPB_DATA_SEQUENCIA_TIPO.gz
5. **Códigos de Erro Customizados**: Sistema define códigos de erro específicos (11-15, 26, 57-58) para diferentes falhas
6. **Classes Geradas por JAXB**: Grande quantidade de classes no pacote `err` geradas automaticamente a partir de XSD
7. **Funcionalidades Incompletas**: Código comentado sugere que funcionalidades de baixa de pagamento, pessoa e referência não foram implementadas
8. **Charset Específico**: Arquivos CIP usam UTF-16BE, convertidos para UTF-8 no processamento
9. **Validação XML**: Código possui método de validação contra XSD mas não está sendo utilizado no fluxo principal
10. **Versionamento**: Projeto na versão 0.6.0, indicando ainda em desenvolvimento/evolução