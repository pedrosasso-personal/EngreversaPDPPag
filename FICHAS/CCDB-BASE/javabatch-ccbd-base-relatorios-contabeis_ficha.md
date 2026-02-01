# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **javabatch-ccbd-base-relatorios-contabeis** é um job batch desenvolvido em Java utilizando o framework Spring Batch. Seu objetivo é gerar relatórios contábeis diários em formato Excel (XLSX) a partir de dados de movimentações bancárias e saldos de contas correntes armazenados em banco de dados Sybase.

O sistema consulta duas categorias principais de informações:
- **Maiores Saldos**: Contas com saldos totais diferentes de zero em uma data específica
- **Movimentações Analíticas**: Detalhamento de todas as transações realizadas nas contas

Os relatórios são gerados em lotes de até 200.000 registros por arquivo, processando dados do dia anterior (D-1) por padrão, ou de uma data específica informada como parâmetro.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê dados de movimentações do banco de dados de forma paginada, controlando o fluxo de leitura entre maiores saldos e movimentações analíticas |
| **ItemProcessor** | Processa os registros lidos (atualmente apenas repassa os dados sem transformação) |
| **ItemWriter** | Gera arquivos Excel (.xlsx) com os dados processados no diretório `/gerados/` |
| **AbstractPagingItemReader** | Classe abstrata que implementa leitura paginada de dados |
| **RelatorioContabil** | Classe abstrata que representa um relatório contábil genérico com métodos para geração de arquivos Excel |
| **RelatorioContabilParaMaioresSaldos** | Implementação concreta para geração de relatórios de maiores saldos |
| **RelatorioContabilParaMovAnaliticas** | Implementação concreta para geração de relatórios de movimentações analíticas |
| **RelatorioContabilRepository** | Interface de repositório para consultas ao banco de dados |
| **RelatorioContabilRepositoryImpl** | Implementação do repositório usando Spring JDBC Template |
| **Queries** | Classe utilitária contendo as queries SQL para consulta de dados |
| **MaioresSaldo** | Entidade representando dados de saldos de contas |
| **MovAnalitico** | Entidade representando movimentações analíticas de contas |
| **MovimentacaoMapper** | Responsável por mapear objetos Java para células de planilhas Excel |
| **DateUtils** | Utilitários para manipulação de datas |
| **ConstantsUtils** | Constantes do sistema, incluindo códigos de erro |

---

## 3. Tecnologias Utilizadas

- **Java 11** (JDK 11.0.16)
- **Spring Batch** (framework de processamento batch)
- **Spring Framework** (injeção de dependências e configuração)
- **Spring JDBC** (acesso a dados via NamedParameterJdbcTemplate)
- **Apache POI 3.9** (geração de arquivos Excel XLSX)
- **Sybase jConnect 4** (driver JDBC para Sybase ASE)
- **Bitronix Transaction Manager** (gerenciamento de transações JTA)
- **Log4j** (logging)
- **JUnit** (testes unitários)
- **Mockito** (mocks para testes)
- **Maven** (gerenciamento de dependências e build)
- **Framework BV Sistemas** (framework proprietário para batch jobs)

---

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch que não expõe endpoints REST.

---

## 5. Principais Regras de Negócio

1. **Data de Processamento**: Por padrão, o sistema processa dados do dia anterior (D-1). Se informado o parâmetro `dtMovimentacao`, processa a data especificada menos 1 dia.

2. **Paginação de Consultas**: As consultas ao banco são executadas em lotes de 200.000 registros para evitar problemas de memória e performance.

3. **Ordem de Processamento**: O sistema primeiro processa todos os registros de "Maiores Saldos" e, somente após finalizar, inicia o processamento de "Movimentações Analíticas".

4. **Filtro de Banco**: O sistema filtra apenas registros do Banco BV (código interno 436, código de compensação 413, agência operação 2020).

5. **Filtro de Saldos**: Apenas contas com saldo total diferente de zero são incluídas no relatório de maiores saldos.

6. **Geração de Múltiplos Arquivos**: Quando há mais de 200.000 registros, o sistema gera múltiplos arquivos numerados sequencialmente.

7. **Nomenclatura de Arquivos**: 
   - Maiores Saldos: `maiores_saldos_YYYYMMDD_N.xlsx`
   - Movimentações Analíticas: `mov_analitico_YYYYMMDD_N.xlsx`
   - Onde N é o índice sequencial do arquivo

8. **Tratamento de Documentos**: Para liquidações do tipo 63, utiliza `nuSequencialUnicoLancamento`; para outros tipos, utiliza `nuDocumento`.

9. **Isolation Level**: As consultas são executadas com `ISOLATION 0` (dirty read) para melhor performance.

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **MaioresSaldo**: Representa contas com saldos significativos
  - Relaciona-se com Pessoa (titular da conta)
  - Relaciona-se com Conta Corrente
  - Relaciona-se com Banco
  - Relaciona-se com Modalidade de Conta

- **MovAnalitico**: Representa movimentações individuais em contas
  - Relaciona-se com Conta Corrente
  - Relaciona-se com Tipo de Transação
  - Relaciona-se com Modalidade de Conta

- **RelatorioContabil**: Classe abstrata que encapsula uma lista de MaioresSaldo ou MovAnalitico
  - Possui duas implementações concretas:
    - RelatorioContabilParaMaioresSaldos (contém List<MaioresSaldo>)
    - RelatorioContabilParaMovAnaliticas (contém List<MovAnalitico>)

**Relacionamentos no Banco de Dados:**
- TbConta → TbHistoricoSaldo (1:N)
- TbConta → TbModalidadeConta (N:1)
- TbConta → tbcontarelacionamento (1:N)
- tbcontarelacionamento → TbPessoaTitularidade (N:1)
- TbPessoaTitularidade → TbPessoa (N:1)
- TbConta → TbBanco (N:1)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBCONTACORRENTE.dbo.TbConta | Tabela | SELECT | Dados cadastrais de contas correntes |
| DBCONTACORRENTE.dbo.TbHistoricoSaldo | Tabela | SELECT | Histórico de saldos diários das contas |
| DBCONTACORRENTE.dbo.TbModalidadeConta | Tabela | SELECT | Modalidades de contas (tipos de conta) |
| DBGLOBAL.dbo.tbcontarelacionamento | Tabela | SELECT | Relacionamento entre contas e titulares |
| DBGLOBAL.dbo.TbPessoaTitularidade | Tabela | SELECT | Titularidade de pessoas em contas |
| DBGLOBAL.dbo.TbPessoa | Tabela | SELECT | Dados cadastrais de pessoas (clientes) |
| DBGLOBAL.dbo.TbBanco | Tabela | SELECT | Dados cadastrais de bancos |
| DBCONTACORRENTE.dbo.TbHistoricoMovimento | Tabela | SELECT | Histórico de movimentações de contas |
| DBCONTACORRENTE.dbo.TbMovimentoDia | Tabela | SELECT | Movimentações do dia corrente |

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema apenas realiza consultas (SELECT), não executa operações de INSERT, UPDATE ou DELETE.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| maiores_saldos_YYYYMMDD_N.xlsx | Gravação | ItemWriter / RelatorioContabilParaMaioresSaldos | Arquivo Excel contendo relatório de contas com maiores saldos |
| mov_analitico_YYYYMMDD_N.xlsx | Gravação | ItemWriter / RelatorioContabilParaMovAnaliticas | Arquivo Excel contendo movimentações analíticas detalhadas |
| robo.log | Gravação | Log4j (RollingFileAppender) | Log de execução do batch |
| statistics-{executionId}.log | Gravação | Log4j (BvDailyRollingFileAppender) | Log de estatísticas de execução |
| job-resources.xml | Leitura | SpringJobRunner | Configuração de recursos (datasources) por ambiente |
| job-definitions.xml | Leitura | SpringJobRunner | Definição do job batch e seus componentes |
| log4j.xml | Leitura | Log4j | Configuração de logging |

**Diretórios:**
- `/gerados/`: Diretório onde os arquivos Excel são gravados
- `/log/`: Diretório onde os arquivos de log são gravados

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

---

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Banco de Dados Sybase ASE | Database | Banco de dados principal contendo informações de contas correntes, movimentações e clientes. Acesso via JDBC aos databases DBCONTACORRENTE e DBGLOBAL |

**Configurações por Ambiente:**
- **DES**: sybdesbco.bvnet.bv:7500
- **UAT**: moruatbco.bvnet.bv:4400
- **PRD**: morsybbco.bvnet.bv:3000

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com uso de padrões como Repository, Mapper e classes de domínio
- Uso adequado de abstrações (RelatorioContabil, AbstractPagingItemReader)
- Logging bem distribuído para rastreabilidade
- Tratamento de exceções com códigos de erro específicos
- Uso de constantes para valores fixos
- Paginação implementada para evitar problemas de memória

**Pontos Negativos:**
- **Código comentado**: Várias dependências e trechos de código comentados no pom.xml e classes
- **Hardcoded values**: Valores como código de banco (413, 436) e agência (2020) estão espalhados pelo código
- **Reflection desnecessária**: Uso de reflection no MovimentacaoMapper poderia ser substituído por métodos específicos
- **Falta de testes**: Apenas um teste de integração básico
- **Documentação**: Ausência de Javadoc nas classes e métodos
- **Complexidade na lógica de paginação**: A lógica de controle de última página e índices poderia ser mais clara
- **ItemProcessor vazio**: A classe ItemProcessor não realiza nenhum processamento, apenas repassa dados
- **Tratamento genérico de exceções**: Vários blocos catch genéricos (Exception, Error, NoClassDefFoundError)
- **Mistura de responsabilidades**: A classe ItemWriter também gerencia o ciclo de vida do FileOutputStream
- **Configurações sensíveis**: Senhas em texto claro nos arquivos de configuração (embora haja placeholder em PRD)

**Recomendações:**
1. Remover código comentado
2. Externalizar constantes de negócio para arquivo de configuração
3. Implementar testes unitários para as classes de negócio
4. Adicionar documentação Javadoc
5. Refatorar tratamento de exceções para ser mais específico
6. Considerar uso de biblioteca de mapeamento como MapStruct ao invés de reflection
7. Implementar criptografia para senhas de banco de dados

---

## 14. Observações Relevantes

1. **Framework Proprietário**: O sistema utiliza o framework BV Sistemas (br.com.bvsistemas.framework.batch), que é proprietário e encapsula funcionalidades do Spring Batch.

2. **Versão do Apache POI**: O sistema utiliza Apache POI 3.9, que é uma versão antiga (2012). Há dependências comentadas de versões mais recentes (4.1.0) que poderiam melhorar performance e funcionalidades.

3. **Estratégia de Retomada**: A classe MyResumeStrategy sempre retorna `false` no método `canResume`, indicando que o job não suporta retomada em caso de falha.

4. **Execução Concorrente**: O job está configurado com `concurrentExecution=true`, permitindo múltiplas execuções simultâneas.

5. **Parâmetro Opcional**: O parâmetro `dtMovimentacao` é opcional. Se não informado, o sistema automaticamente processa D-1.

6. **Formato de Data do Parâmetro**: O parâmetro `dtMovimentacao` deve ser informado no formato `yyyyMMdd` (ex: 20220203).

7. **Códigos de Saída Customizados**:
   - 10: Erro ao gravar arquivo permanente
   - 20: Erro ao finalizar arquivo permanente
   - 30: Erro durante consulta do relatório contábil
   - 40: Erro durante geração do arquivo

8. **Limpeza de Logs**: Os scripts de execução (.bat e .sh) removem arquivos de log do Bitronix e statistics antes de cada execução.

9. **Memória JVM**: Configuração de memória diferente entre Windows (1024M-1536M) e Linux (512M-1028M).

10. **Banco Específico**: O sistema está focado no Banco BV (código 413/436), mas a estrutura permite extensão para outros bancos através do enum BancoEnum.