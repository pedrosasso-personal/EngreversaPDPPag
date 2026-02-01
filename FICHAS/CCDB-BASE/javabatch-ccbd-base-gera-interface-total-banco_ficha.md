# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java responsável por gerar interface contábil (arquivo M06) com movimentações bancárias do Total Banco. O sistema busca movimentações de contas correntes (tipo conta 5, banco 161) em bases de dados Sybase e MySQL, processa os dados considerando dias úteis e não úteis, gera arquivo texto formatado e atualiza flags de controle de processamento. Suporta processamento inicial e reprocessamento de datas específicas.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê registros de processamento pendentes, busca movimentações do dia ou reprocessamento, valida status |
| **ItemProcessor** | Processa movimentações (atualmente apenas repassa dados, lógica comentada) |
| **ItemWriter** | Gera arquivo M06 formatado, atualiza flags de processamento nas tabelas |
| **MyResumeStrategy** | Estratégia de tratamento de erros do framework batch |
| **TbMovimentoDiaRepositoryImpl** | Acesso a dados de movimentações (Sybase) |
| **TbProcessamentoInterfaceContblRepositoryImpl** | Controle de processamento (MySQL) |
| **InterfaceContabil** | Entidade de controle de processamento |
| **Movimento** | Entidade de movimentação bancária |
| **DatasApuradas** | Entidade para controle de datas (dias úteis/não úteis) |
| **Loader** | Utilitário para configuração de pasta de saída |

## 3. Tecnologias Utilizadas

- **Framework**: BV Sistemas Framework Batch (proprietário)
- **Linguagem**: Java 8
- **Build**: Apache Maven
- **Bancos de Dados**: 
  - Sybase ASE (TbMovimentoDia, TbHistoricoMovimento)
  - MySQL 8.0 (TbProcessamentoInterfaceContbl)
- **Gerenciamento de Transações**: Bitronix JTA
- **JDBC**: Spring JDBC Template (NamedParameterJdbcTemplate)
- **Logging**: Log4j
- **Criptografia**: BV Crypto (senhas)
- **Testes**: JUnit

## 4. Principais Endpoints REST

Não se aplica (sistema batch, não possui endpoints REST).

## 5. Principais Regras de Negócio

1. **Seleção de Movimentações**: Busca apenas movimentações do tipo conta 5 (conta corrente) e banco 161
2. **Processamento vs Reprocessamento**: 
   - Processamento (P): busca movimentações não processadas (flInterfaceTB = 'N')
   - Reprocessamento (R): busca movimentações já processadas em data específica (flInterfaceTB = 'S')
3. **Tratamento de Dias Não Úteis**: Consulta TbControleData para identificar se deve buscar movimentações de finais de semana/feriados acumulados
4. **Geração de Arquivo M06**: Formato fixo com header (tipo 00), registros de movimentação (tipo 1) e trailer (tipo 2)
5. **Formatação de Campos**: Aplica zeros à esquerda em campos numéricos conforme layout específico
6. **Atualização de Flags**: Marca movimentações como processadas (flInterfaceTB = 'S') após geração do arquivo
7. **Controle de Status**: Atualiza status de processamento para 'F' (finalizado) após conclusão

## 6. Relação entre Entidades

**InterfaceContabil** (1) ← controla → (N) **Movimento**
- InterfaceContabil: tabela de controle com data de movimento e status de processamento
- Movimento: representa uma movimentação bancária individual

**DatasApuradas**: entidade auxiliar que armazena datas de referência para busca de movimentações em períodos com dias não úteis

**Relacionamento com Tabelas**:
- TbProcessamentoInterfaceContbl (MySQL) → controla execução
- TbMovimentoDia (Sybase) → movimentações do dia corrente
- TbHistoricoMovimento (Sybase) → movimentações históricas
- TbControleData (Sybase) → controle de datas úteis/não úteis

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbProcessamentoInterfaceContbl | Tabela (MySQL) | SELECT | Controle de processamentos pendentes (status 'P') |
| TbMovimentoDia | Tabela (Sybase) | SELECT | Movimentações bancárias do dia corrente |
| TbHistoricoMovimento | Tabela (Sybase) | SELECT | Movimentações bancárias históricas |
| TbControleData | Tabela (Sybase) | SELECT | Controle de datas úteis e não úteis por banco/agência |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbProcessamentoInterfaceContbl | Tabela (MySQL) | UPDATE | Atualiza status para 'F' (finalizado) após processamento |
| TbMovimentoDia | Tabela (Sybase) | UPDATE | Marca movimentações como processadas (flInterfaceTB='S', dtInterfaceTB) |
| TbHistoricoMovimento | Tabela (Sybase) | UPDATE | Marca movimentações históricas como processadas |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| {data}.M06 | Gravação | ItemWriter / pasta configurada em Loader | Arquivo de interface contábil formatado com movimentações |
| statistics-{executionId}.log | Gravação | Framework Batch / pasta log/ | Log de estatísticas de execução |
| robo.log | Gravação | Log4j / pasta log/ | Log de aplicação |
| *-sql.xml | Leitura | QueryReader | Arquivos XML com queries SQL |

## 10. Filas Lidas

Não se aplica (sistema não consome filas).

## 11. Filas Geradas

Não se aplica (sistema não publica em filas).

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Sybase ASE (DBCONTACORRENTE) | Banco de Dados | Base principal com movimentações bancárias (TbMovimentoDia, TbHistoricoMovimento) |
| MySQL (CCBDContaCorrente) | Banco de Dados | Base de controle de processamento (TbProcessamentoInterfaceContbl) |
| Sistema Contábil (consumidor) | Arquivo | Sistema que consome o arquivo M06 gerado |

## 13. Avaliação da Qualidade do Código

**Nota: 5/10**

**Justificativa:**

**Pontos Positivos:**
- Estrutura organizada seguindo padrão batch (Reader/Processor/Writer)
- Uso de framework proprietário consolidado
- Separação de responsabilidades em camadas (repository, service, domain)
- Uso de injeção de dependências via Spring
- Queries SQL externalizadas em arquivos XML

**Pontos Negativos:**
- **Código comentado**: ItemProcessor possui lógica inteira comentada, indicando refatoração incompleta
- **Mistura de responsabilidades**: ItemReader executa lógica de negócio que deveria estar no Processor
- **Falta de tratamento de erros**: Ausência de validações e tratamentos específicos
- **Código duplicado**: Lógica de formatação com zeros repetida múltiplas vezes no ItemWriter
- **Nomes de variáveis**: Uso de nomes genéricos e pouco descritivos (ex: "m", "arq")
- **Hardcoded values**: Valores fixos espalhados pelo código (banco 161, tipo conta 5)
- **Falta de documentação**: Ausência de JavaDoc e comentários explicativos
- **SQL complexo**: Queries com tabelas temporárias e lógica complexa que poderia ser simplificada
- **Encoding**: Comentários com caracteres corrompidos (encoding incorreto)
- **Classes não utilizadas**: ExampleOf* classes ainda presentes no código

## 14. Observações Relevantes

1. **Ambientes**: Sistema configurado para DES, UAT e PRD com conexões distintas
2. **Formato M06**: Layout proprietário com registros de tamanho fixo (header tipo 00, detalhe tipo 1, trailer tipo 2)
3. **Transações**: Uso de JTA com Bitronix para gerenciamento transacional distribuído
4. **Senhas**: Utiliza criptografia BV Crypto com token "BV_CRYPTO_TOKEN"
5. **Execução**: Batch executável via shell script (.sh) ou batch Windows (.bat)
6. **Concorrência**: Suporta execução concorrente (concurrentExecution=true)
7. **Tabelas Temporárias**: Uso de tabelas temporárias (#M06BV655) no Sybase para otimização
8. **Refatoração Pendente**: Código indica migração de lógica do Processor para Reader não finalizada
9. **Framework Proprietário**: Dependência forte do framework BV Sistemas, dificultando portabilidade
10. **Versionamento**: Versão 0.6.0 indica sistema ainda em evolução