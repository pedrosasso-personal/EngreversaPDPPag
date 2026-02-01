# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java desenvolvido para gerar arquivos no formato SoftPar contendo lançamentos contábeis consolidados. O sistema consulta dados de lançamentos contábeis em um banco de dados Sybase IQ, processa as informações agrupando cabeçalhos e detalhes de lotes contábeis, e gera arquivos de saída em formato posicional específico para integração com o sistema SoftPar de gestão contábil.

O processamento considera regras de negócio relacionadas a dias úteis, feriados e finais de semana para determinar a data inicial de processamento, executando procedures armazenadas que consolidam os lançamentos por veículo legal, agência, carteira e outros parâmetros.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê dados do banco de dados executando procedures de cabeçalho e detalhe, valida parâmetros de entrada e determina a data inicial de processamento |
| **ItemProcessor** | Processa os dados lidos, agrupando detalhes aos seus respectivos cabeçalhos formando lotes contábeis |
| **ItemWriter** | Gera o arquivo de saída em formato posicional utilizando a biblioteca FFPojo |
| **ProcedureLancamentoContabil** | Executa as stored procedures no banco de dados e mapeia os resultados para objetos Java |
| **DataUtil** | Utilitário para cálculo de datas, validação de dias úteis, feriados e finais de semana |
| **JobUtil** | Gerencia e valida os parâmetros de execução do job |
| **HeaderSoftparVO** | Entidade que representa o cabeçalho de um lote contábil com anotações para geração de arquivo posicional |
| **DetailSoftparVO** | Entidade que representa o detalhe de um lançamento contábil com anotações para geração de arquivo posicional |
| **HeaderSoftParRowMapper** | Mapeia ResultSet do banco para objetos HeaderSoftparVO |
| **DetailSoftParRowMapper** | Mapeia ResultSet do banco para objetos DetailSoftparVO |
| **ApplicationProperties** | Carrega e gerencia propriedades da aplicação, incluindo mapeamento de códigos de veículo legal |
| **Util** | Utilitários gerais para formatação de decimais e obtenção de mapeamentos de/para |

## 3. Tecnologias Utilizadas

- **Java** (linguagem de programação)
- **Spring Batch** (framework para processamento batch)
- **Spring Framework** (injeção de dependências e configuração)
- **Maven** (gerenciamento de dependências e build)
- **Sybase IQ** (banco de dados)
- **JDBC Driver Sybase jConnect4** (conectividade com banco de dados)
- **FFPojo** (biblioteca para geração de arquivos posicionais)
- **Log4j** (logging)
- **JUnit** (testes unitários)
- **BV Framework Batch** (framework proprietário para jobs batch)

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch sem endpoints REST.

## 5. Principais Regras de Negócio

- **Validação de Data de Processamento**: O sistema valida se a data de processamento informada é um dia útil válido, considerando finais de semana e feriados
- **Cálculo de Data Inicial**: Determina a data inicial de processamento retroagindo até 4 dias úteis anteriores quando necessário
- **Processamento em Final de Semana/Feriado**: Se a data de processamento cair em final de semana ou feriado e for o último dia do mês, o sistema busca o último dia útil do mês
- **Interrupção por Regra de Negócio**: O sistema não processa se a data cair em final de semana/feriado e não for último dia do mês
- **Agrupamento de Lançamentos**: Agrupa detalhes de lançamentos contábeis aos seus respectivos cabeçalhos baseado em: código de veículo legal, agência, ano/mês/dia de movimento e número de lote
- **Mapeamento de Veículo Legal**: Realiza conversão (de/para) entre códigos de veículo legal do sistema online e códigos do sistema de gestão contábil
- **Formatação de Valores**: Valores negativos em lançamentos são convertidos para zero no arquivo de saída
- **Geração de Arquivo Posicional**: Gera arquivo com layout de 320 posições por linha, contendo cabeçalho, detalhes e linha em branco ao final de cada lote

## 6. Relação entre Entidades

**SoftparVO** (interface marcadora)
- Implementada por: HeaderSoftparVO, DetailSoftparVO

**HeaderSoftparVO** (Cabeçalho de Lote)
- Atributos principais: cdVeiculoLegal, cdAgencia, nuLote, dtAnoMesMovimento, dtDiaMovimento
- Contém totalizadores: vrSomaDebito, vrSomaCredito, qtLancamentoLote

**DetailSoftparVO** (Detalhe de Lançamento)
- Atributos principais: cdVeiculoLegal, cdAgencia, nuLote, nuSequencial, vrLancamento
- Relaciona-se com HeaderSoftparVO através dos campos: cdVeiculoLegal, cdAgencia, dtAnoMesMovimento, dtDiaMovimento, nuLote

**SoftParLote** (Agregador)
- Contém: 1 HeaderSoftparVO + Lista de DetailSoftparVO
- Representa um lote completo para geração no arquivo

**SoftParData** (Container de Dados)
- Contém: Lista de SoftparVO (headers) + Lista de SoftparVO (details)
- Estrutura intermediária entre leitura e processamento

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| DBCOR.TbFeriado | Tabela | SELECT | Consulta feriados para validação de dias úteis (CdPraca=1, CdTipoFeriado=1) |
| STGTXT_FLEX.SP_LancamentoConsolidadoCabec | Stored Procedure | EXEC | Retorna cabeçalhos de lotes de lançamentos contábeis consolidados |
| STGTXT_FLEX.SP_LancamentoConsolidadoDetail | Stored Procedure | EXEC | Retorna detalhes de lançamentos contábeis consolidados |

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema apenas realiza leitura de dados, não executa operações de INSERT, UPDATE ou DELETE.

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| Application.properties | Leitura | ApplicationProperties | Arquivo de propriedades contendo mapeamento de códigos de veículo legal (de/para entre sistema online e gestão contábil) |
| {nmArquivo} (dinâmico) | Gravação | ItemWriter | Arquivo de saída em formato posicional SoftPar contendo cabeçalhos e detalhes de lançamentos contábeis (320 posições por linha) |
| robo.log | Gravação | Log4j (roboFile appender) | Log de execução do robô com informações de processamento |
| statistics-{executionId}.log | Gravação | Log4j (statistics appender) | Log de estatísticas de execução do job batch |

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas.

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **Sybase IQ (IQ_BI)** | Banco de Dados | Banco de dados principal onde são executadas as procedures de consolidação de lançamentos contábeis. Configurado para ambientes DES, QA, UAT e PRD |
| **Sistema SoftPar** | Sistema Externo | Sistema de gestão contábil que receberá os arquivos gerados. A integração é via arquivo posicional com layout específico de 320 posições |

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Uso adequado do padrão Spring Batch com separação clara de responsabilidades (Reader, Processor, Writer)
- Utilização de builders/fluent interface em algumas classes (ProcedureLancamentoContabil, DataUtil)
- Tratamento de exceções customizado com códigos de saída específicos
- Uso de anotações FFPojo para geração de arquivos posicionais de forma declarativa
- Testes unitários presentes para classe DataUtil

**Pontos Negativos:**
- Código com comentários em português misturados com código, incluindo TODOs não resolvidos
- Lógica de negócio complexa de cálculo de datas com múltiplos métodos recursivos dificulta manutenibilidade
- Classes de modelo (VO) muito extensas com muitos getters/setters e lógica de formatação misturada
- Senhas de banco de dados expostas em arquivos de configuração XML
- Falta de documentação JavaDoc nas classes e métodos
- Uso de System.out.println misturado com logging adequado
- Código com caracteres especiais mal codificados (encoding issues)
- Métodos muito longos em algumas classes (ex: DetailSoftparVO com mais de 500 linhas)
- Falta de constantes para valores mágicos (ex: números de posições, tamanhos de campos)
- Tratamento genérico de exceções em alguns pontos sem logging adequado

## 14. Observações Relevantes

- O sistema possui configurações específicas para 4 ambientes: DES, QA, UAT e PRD, cada um com suas próprias credenciais de banco de dados
- A execução do job é controlada por um arquivo batch (.bat) que recebe 7 parâmetros de entrada
- O sistema utiliza um framework proprietário BV (BV Framework Batch) que encapsula o Spring Batch
- Existe um mapeamento de códigos de veículo legal entre o sistema online e o sistema de gestão contábil, configurado via arquivo de propriedades
- O layout do arquivo de saída é fixo em 320 posições por linha, com campos posicionais específicos
- O sistema implementa uma estratégia de resume (MyResumeStrategy) que não permite retomada em caso de erro
- Logs de estatísticas são gerados com identificador de execução único para rastreabilidade
- O processamento considera até 4 dias úteis retroativos (D-1, D-2, D-3, D-4) para determinar a data inicial
- Arquivos de log do Bitronix (gerenciador de transações) são removidos automaticamente ao final da execução