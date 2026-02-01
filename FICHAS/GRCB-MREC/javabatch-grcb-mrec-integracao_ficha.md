# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java responsável pela integração entre o sistema de Gestão de Recebimentos e Cobrança Bancária (GRCB) e o sistema MREC (Meios de Recebimento). O sistema processa arquivos de retorno de cobrança bancária com assessoria, gerando arquivos CSV contendo informações detalhadas sobre títulos processados, incluindo valores pagos, despesas e honorários de assessoria. O processamento é realizado em lote, buscando arquivos processados nos últimos 5 dias e atualizando o status dos retornos após a geração bem-sucedida dos arquivos.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê os arquivos de retorno de cobrança processados do banco de dados, preparando a lista de arquivos para processamento |
| **ItemProcessor** | Processa cada arquivo, buscando os detalhes dos títulos e preparando as informações para geração do arquivo de saída |
| **ItemWriter** | Gera o arquivo CSV com os dados de assessoria e atualiza o status do retorno de cobrança no banco |
| **ArquivoAssessoriaBusinessImpl** | Implementa as regras de negócio para listagem de arquivos, busca de detalhes e preparação das informações |
| **ArquivoAssessoriaDAOImpl** | Executa as consultas SQL para recuperar dados de arquivos e detalhes de cobrança |
| **AssessoriaLayoutWritter** | Responsável pela formatação e geração do conteúdo do arquivo CSV no layout esperado |
| **AlterarStatusRetornoCobranca** | Stored Procedure para atualizar o status do retorno de cobrança após processamento |
| **FileUtil** | Utilitário para gravação de arquivos no sistema de arquivos |
| **MyResumeStrategy** | Estratégia de tratamento de erros e definição de códigos de saída do job |

---

## 3. Tecnologias Utilizadas

- **Java** (versão não especificada no código)
- **Maven** - Gerenciamento de dependências e build
- **Spring Framework** - Configuração e injeção de dependências
- **BV Framework Batch** - Framework proprietário para processamento batch (bv-framework-batch.standalone)
- **JDBC** - Acesso a banco de dados
- **Bitronix** - Gerenciador de transações JTA
- **jTDS Driver** - Driver JDBC para SQL Server/Sybase
- **Log4j** - Logging
- **JUnit** - Testes unitários
- **SQL Server/Sybase** - Banco de dados (baseado no driver jTDS e sintaxe SQL)

---

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch sem endpoints REST.

---

## 5. Principais Regras de Negócio

1. **Período de Processamento**: O sistema busca arquivos processados nos últimos 5 dias retroativos à data de execução (configurado em `UtilHelper.CINCO_DIAS_RETROATIVOS`)

2. **Filtro de Arquivos**: Apenas arquivos com parâmetro de assessoria de cobrança ativo (`FlAssessoriaCobranca = 'S'`) e evento de status 10 são processados

3. **Processamento de Títulos**: Somente títulos com ocorrências que processam baixa (`FlProcessaBaixa = 'S'`) são incluídos no arquivo

4. **Determinação de Status Processado**: Um título é considerado processado ('S') quando `StProcessamento = 'P'` e não possui inconsistências (`CdInconsistenciaCobranca is null`), caso contrário é marcado como 'N'

5. **Nomenclatura de Arquivo**: O arquivo gerado segue o padrão: `{nmArquivoCobranca}-{cdRetornoCobranca}.csv`

6. **Atualização de Status**: Após geração bem-sucedida do arquivo, o status do retorno é atualizado para evento 16 (EVENTO_INTEGRACAO_MREC_REALIZADA) com código de colaborador fixo 78

7. **Tratamento de Valores Nulos**: Valores numéricos nulos são convertidos para zero, strings nulas para vazio no arquivo de saída

---

## 6. Relação entre Entidades

**ArquivoAssessoriaDTO** (Entidade Principal)
- Representa um arquivo de retorno de cobrança
- Atributos: cdRetornoCobranca, nmArquivoCobranca, codigoArquivo
- Relacionamento: 1:N com ArquivoDetalheAssessoriaDTO

**ArquivoDetalheAssessoriaDTO** (Detalhe)
- Representa cada título/ocorrência dentro de um arquivo
- Atributos: cdRetornoCobranca, cdOcorrenciaConta, cdEmpresaBanco, cdCarteiraBanco, cdRetornoCobrancaOcorrencia, dsRetornoCobrancaOcorrencia, cdNossoNumero, vrPago, vrDespesaAssessoria, vrHonorarioAssessoria, processado, dsInconsistenciaCobranca, dtRecebimento, dtFimProcessamento
- Relacionamento: N:1 com ArquivoAssessoriaDTO

**AssessoriaCobrancaVO** (Value Object)
- Encapsula informações para geração do arquivo
- Atributos: nmArquivo, dtGeracao, qtRegistro, arquivoAssessoriaDTO
- Relacionamento: 1:1 com ArquivoAssessoriaDTO

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbRetornoCobranca | Tabela | SELECT | Armazena informações dos arquivos de retorno de cobrança bancária |
| TbParametroCobrancaBancaria | Tabela | SELECT | Contém parâmetros de configuração de cobrança, incluindo flag de assessoria |
| TB_CARNE_ARQUIVO | Tabela | SELECT | Tabela de arquivos do sistema de carnê, usada para obter código do arquivo |
| TbRetornoCobrancaDetalhe | Tabela | SELECT | Detalhes dos títulos contidos em cada arquivo de retorno |
| TbRetornoCobrancaOcorrencia | Tabela | SELECT | Tipos de ocorrências de retorno de cobrança |
| TbInconsistenciaCobranca | Tabela | SELECT | Descrições de inconsistências encontradas no processamento |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbRetornoCobranca | Tabela | UPDATE | Atualização do status do retorno via stored procedure PrAlterarStatusRetornoCobranca, alterando para evento 16 (integração MREC realizada) |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| {nmArquivoCobranca}-{cdRetornoCobranca}.csv | Gravação | ItemWriter / AssessoriaLayoutWritter | Arquivo CSV contendo detalhes de assessoria de cobrança com cabeçalho e registros de títulos processados |
| log/robo.log | Gravação | Log4j (roboFile appender) | Arquivo de log principal do sistema com rotação de 2MB e 5 backups |
| log/statistics-{executionId}.log | Gravação | Log4j (statistics appender) | Arquivo de estatísticas de execução do batch |

**Observação**: O diretório de saída dos arquivos CSV é configurável via parâmetro `srcDir` na execução do job.

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
| **DBGESTAO** | Banco de Dados SQL Server/Sybase | Base de dados principal contendo tabelas de retorno de cobrança, parâmetros, ocorrências e inconsistências |
| **DBCARNE** | Banco de Dados SQL Server/Sybase | Base de dados do sistema de carnê, consultada para obter código do arquivo |
| **Sistema de Arquivos** | File System | Gravação dos arquivos CSV gerados no diretório configurado via parâmetro srcDir |

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades entre camadas (DAO, Business, Batch)
- Uso adequado de DTOs e VOs para transferência de dados
- Tratamento de exceções customizado
- Logging estruturado em pontos importantes
- Uso de framework batch consolidado (BV Framework)
- Configuração externalizada via Spring

**Pontos Negativos:**
- **Hardcoding de valores**: Código de colaborador fixo (78), evento fixo (16), período retroativo (-5 dias)
- **Encoding inconsistente**: Comentários em ISO-8859-1 com caracteres corrompidos (�)
- **Falta de validações**: Não há validação de parâmetros de entrada ou dados recuperados
- **Gerenciamento de recursos**: Fechamento manual de conexões JDBC (try-finally) ao invés de try-with-resources
- **Testes limitados**: Apenas um teste de integração básico
- **Documentação**: Ausência de Javadoc nas classes principais
- **Magic numbers**: Códigos de erro e eventos sem constantes descritivas em alguns pontos
- **Acoplamento**: Dependência forte do framework proprietário BV, dificultando portabilidade
- **SQL inline**: Queries SQL como strings em interface, dificultando manutenção

---

## 14. Observações Relevantes

1. **Dependência de Framework Proprietário**: O sistema utiliza extensivamente o BV Framework (bv-framework-batch), um framework proprietário da organização, o que pode dificultar manutenção por equipes externas

2. **Configuração de Ambiente**: O arquivo `job-resources.xml` de teste contém credenciais de banco de dados em texto claro, com comentário indicando que em ambientes superiores (QA/UAT/PROD) as senhas devem ser criptografadas

3. **Período de Busca**: O sistema busca arquivos dos últimos 5 dias, mas este valor está hardcoded. Seria recomendável torná-lo configurável

4. **Encoding**: O código fonte apresenta problemas de encoding (caracteres � nos comentários), sugerindo conversão inadequada entre charsets

5. **Versionamento**: O projeto está em versão SNAPSHOT (17.8.3.1-SNAPSHOT), indicando desenvolvimento ativo

6. **Estrutura de Diretórios**: O projeto segue estrutura Maven multi-módulo (core e dist), com módulo dist responsável pela geração do pacote distribuível

7. **Servidor de Banco**: Configuração de teste aponta para servidor `ptasybdes15.bvnet.bv` porta 6010, ambiente de desenvolvimento

8. **Códigos de Saída**: O sistema define códigos de erro específicos (11-15) para diferentes tipos de falha, facilitando troubleshooting em ambiente de produção

9. **Formato de Data**: Datas no arquivo CSV são formatadas como `yyyyMMdd`

10. **Separador CSV**: Utiliza ponto-e-vírgula (;) como separador, padrão brasileiro