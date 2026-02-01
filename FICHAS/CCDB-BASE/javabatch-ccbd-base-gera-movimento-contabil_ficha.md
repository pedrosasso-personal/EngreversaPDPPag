# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java responsável por gerar arquivos de movimento contábil para integração com o sistema SOFTPAR. O sistema busca movimentações bancárias do dia anterior (ou de uma data específica), agrupa por lote, gera registros de detalhe e rodapé, e produz arquivos texto formatados para processamento contábil. Suporta dois bancos (Banco Votorantim e Banco BV S.A.) e possui flag para formato IRFS09.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê movimentações do banco de dados, busca datas contábeis, agrupa transações por data de movimento |
| **ItemProcessor** | Processa lotes de movimento, grava controle de arquivo, lote e detalhes no banco, calcula totalizadores |
| **ItemWriter** | Gera arquivo texto temporário, renomeia para nome definitivo, atualiza flag de interface total banco |
| **MovimentacaoContabilRepository** | Interface de acesso a dados para operações de leitura e gravação |
| **MovimentacaoContabilRepositoryImpl** | Implementação do repositório usando JDBC Template e queries SQL externas |
| **MovimentacaoMapper** | Converte objetos de domínio para objetos de arquivo (detalhe/rodapé) |
| **LoteMovimentoContabil** | Representa um lote de movimentos contábeis com seus detalhes |
| **DetalheLoteMovimentoContabil** | Representa um movimento individual dentro de um lote |
| **MovimentacaoArquivoConsolidado** | Consolida informações do arquivo a ser gerado |
| **InstituicaoBancaria** | Enum com configurações dos bancos (código, agência, lote) |

---

## 3. Tecnologias Utilizadas

- **Java** (versão não especificada explicitamente)
- **Maven** (gerenciamento de dependências e build)
- **Spring Framework** (IoC, JDBC Template)
- **BV Framework Batch** (framework proprietário para processamento batch)
- **Bitronix** (gerenciador de transações JTA)
- **Sybase ASE** (banco de dados - via jConnect JDBC driver)
- **JUnit 4** (testes unitários)
- **Mockito 2.28.2** (mocks para testes)
- **Apache Commons** (Lang, IO)
- **Log4j** (logging)
- **Apache POI 4.1.0** (manipulação de arquivos Office)

---

## 4. Principais Endpoints REST

não se aplica

---

## 5. Principais Regras de Negócio

1. **Busca de Movimentações**: Busca movimentos do dia anterior (ou data parametrizada) que ainda não foram interfaceados (flInterfaceTB = 'N')
2. **Agrupamento por Data**: Movimentos são agrupados por data de movimento e sequenciados em lotes
3. **Cálculo de Totalizadores**: Soma de débitos e créditos por lote, validação de balanceamento
4. **Geração de Sequência**: Controla sequência de arquivos gerados no mesmo dia para o mesmo lote
5. **Formato IRFS09**: Suporta dois formatos de conta contábil (15 ou 25 caracteres) conforme parâmetro isIRFS09
6. **Controle de Interface**: Marca movimentos como interfaceados após geração bem-sucedida do arquivo
7. **Tratamento de Data**: Se data não informada, busca datas contábeis da tabela TbControleData
8. **Mapeamento de Contas**: Utiliza TbParametroMovimentoContabil para mapear modalidade de conta para contas contábeis de débito/crédito
9. **Consolidação Temporal**: Movimentos com data superior à data inicial são consolidados na data final

---

## 6. Relação entre Entidades

**LoteMovimentoContabil** (1) -----> (N) **DetalheLoteMovimentoContabil**
- Um lote contém múltiplos detalhes de movimento

**MovimentacaoArquivoConsolidado** (1) -----> (1) **MovimentacaoArquivoRodape**
- Arquivo consolidado possui um rodapé

**MovimentacaoArquivoRodape** (1) -----> (N) **MovimentacaoArquivoDetalhe**
- Rodapé contém múltiplas linhas de detalhe para o arquivo

**DetalheLoteMovimentoContabil** (N) -----> (1) **InstituicaoBancaria**
- Cada detalhe está associado a uma instituição bancária

**LoteMovimentoContabil** (N) -----> (1) **InstituicaoBancaria**
- Cada lote pertence a uma instituição bancária

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbMovimentoDia | tabela | SELECT | Movimentos bancários do dia corrente |
| TbHistoricoMovimento | tabela | SELECT | Histórico de movimentos bancários |
| TbParametroMovimentoContabil | tabela | SELECT | Parâmetros de mapeamento de contas contábeis por modalidade |
| TbLoteMovimentoContabil | tabela | SELECT | Lotes de movimento contábil (para buscar sequência) |
| TbControleArquivoContabil | tabela | SELECT | Controle de arquivos gerados (para sequência) |
| TbControleData | tabela | SELECT | Datas contábeis de controle |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbControleArquivoContabil | tabela | INSERT | Registra controle de arquivo gerado |
| TbLoteMovimentoContabil | tabela | INSERT | Registra lote de movimento contábil |
| TbDetalheLoteMovimentoContabil | tabela | INSERT | Registra detalhes dos movimentos do lote |
| TbMovimentoDia | tabela | UPDATE | Atualiza flag flInterfaceTB='S' e dtInterfaceTB |
| TbHistoricoMovimento | tabela | UPDATE | Atualiza flag flInterfaceTB='S' e dtInterfaceTB |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| MVTEMP.tmp | gravação | ItemWriter | Arquivo temporário para escrita dos movimentos |
| MV{lote}{MMDD}{seq}.MV | gravação | ItemWriter | Arquivo definitivo de movimento contábil (ex: MV96710270001.MV) |
| *.sql (vários) | leitura | SQLFileReader | Arquivos SQL externos carregados dinamicamente |
| log/robo.log | gravação | Log4j | Log de execução do batch |
| log/statistics-*.log | gravação | Log4j/BV Framework | Estatísticas de execução |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| SOFTPAR | Arquivo | Sistema contábil que consome os arquivos MV gerados |
| Sybase ASE (DBCONTACORRENTE) | Banco de Dados | Banco de dados de conta corrente (servidores: sybdesbco, moruatbco, morsybbco) |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 6/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades (Reader, Processor, Writer)
- Uso de padrões como Repository e Mapper
- Testes unitários presentes com boa cobertura
- Uso de constantes para valores fixos
- Queries SQL externalizadas em arquivos separados
- Tratamento de exceções customizado

**Pontos Negativos:**
- Código com comentários em português misturados com código em inglês
- Uso de caracteres acentuados que podem causar problemas de encoding
- Queries SQL complexas com tabelas temporárias que poderiam ser otimizadas
- Falta de documentação JavaDoc nas classes principais
- Uso de reflection nos testes (ReflectionUtils) indica possível problema de design
- Hardcoded de valores como "user", "1" em alguns lugares
- Classe SQLFileReader com lógica de leitura baseada em stack trace (frágil)
- Falta de validação de parâmetros de entrada em alguns métodos
- Uso de tipos primitivos onde objetos seriam mais apropriados (ex: int vs Integer)
- Código de tratamento de exceção repetitivo em várias classes

---

## 14. Observações Relevantes

1. **Ambientes**: Sistema possui configurações específicas para DES, UAT e PRD com diferentes servidores Sybase
2. **Senha Parametrizada**: Arquivos de configuração PRD/UAT usam placeholder `{{password}}` para senha
3. **Transação Distribuída**: Utiliza Bitronix para gerenciamento de transações JTA
4. **Framework Proprietário**: Depende fortemente do BV Framework Batch (br.com.bvsistemas)
5. **Formato de Arquivo**: Arquivo gerado é texto posicional com tamanhos fixos de campo
6. **Exit Codes**: Sistema define códigos de saída específicos (10-140) para diferentes tipos de erro
7. **Execução**: Pode ser executado via shell script (.sh) ou batch Windows (.bat)
8. **Parâmetros de Execução**: 
   - idBanco (obrigatório): código do banco
   - dtMovimentacao (opcional): data específica para processar
   - isIRFS09 (opcional): flag para formato IRFS09
9. **Concorrência**: Configurado para permitir execução concurrent (concurrentExecution=true)
10. **Timeout de Transação**: Configurado com timeout alto (1000000) para transações longas