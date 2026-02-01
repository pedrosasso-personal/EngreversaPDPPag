# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java responsável pela geração de arquivos de compensação bancária no formato ABBC (Associação Brasileira de Bancos Comerciais). O sistema processa lançamentos financeiros armazenados em banco de dados, gera arquivos de remessa no padrão DOC (Documento de Crédito) e registra o processamento. Opera em ambiente batch utilizando framework proprietário BV Sistemas para processamento em lote com padrão Reader-Processor-Writer.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê registros de processamento de compensação pendentes (status '1') do banco de dados |
| **ItemProcessor** | Processa cada registro, busca lançamentos associados, gera arquivo de compensação no formato ABBC/DOC |
| **ItemWriter** | Atualiza status do processamento e registra informações do arquivo gerado |
| **BDbPgfTes** | Camada de negócio para acesso ao banco DBPGF_TES (tabelas de controle) |
| **BDbPgf** | Camada de negócio para acesso ao banco DBPGF (dados de filiais) |
| **DAODbPgfTesImpl** | Implementação DAO para operações no banco DBPGF_TES |
| **DAODbPgfImpl** | Implementação DAO para operações no banco DBPGF |
| **ProcessamentoCompensacao** | Entidade representando um processamento de arquivo de compensação |
| **Lancamento** | Entidade representando um lançamento financeiro a ser processado |
| **Filial** | Entidade representando dados de uma filial |
| **RegistroArquivoCompensacao** | Entidade para registro de arquivos gerados |
| **AbbcResumeStrategy** | Estratégia de tratamento de erros e retomada do job |
| **StringUtil** | Utilitários para formatação de strings e valores para o arquivo ABBC |
| **LogUtil** | Utilitários para logging centralizado |
| **ConnectionHelper** | Utilitários para gerenciamento de conexões JDBC |

---

## 3. Tecnologias Utilizadas

- **Java** (versão não especificada no código)
- **Maven** - Gerenciamento de dependências e build
- **Spring Framework 2.0** - Injeção de dependências e configuração
- **BV Framework Batch** - Framework proprietário para processamento batch
- **Bitronix** - Gerenciador de transações JTA
- **JTDS Driver** - Driver JDBC para Sybase
- **Sybase ASE** - Banco de dados (servidor: sybdesspb.bvnet.bv)
- **Log4j** - Framework de logging
- **JUnit** - Testes unitários
- **Apache POI 3.16** - Manipulação de arquivos Office (dependência declarada)

---

## 4. Principais Endpoints REST

não se aplica

---

## 5. Principais Regras de Negócio

1. **Seleção de Processamentos**: Busca registros com tipo de arquivo = 1 (ABBC) e status = '1' (pendente)
2. **Geração de Arquivo DOC**: Cria arquivo no formato específico ABBC com prefixo "655" + data + "1.doc"
3. **Formatação de Valores**: Valores monetários formatados com 13 dígitos (11 inteiros + 2 decimais)
4. **Validação de Agências**: Trata agências com ou sem dígito verificador, padronizando para 4 dígitos + 1 DV
5. **Tipo de Documento**: Diferencia DOC tipo "D" (débito) e outros tipos, aplicando regras específicas de conta
6. **Código de Finalidade**: Valida códigos entre 01 e 13, defaultando para "01" se inválido
7. **Remoção de Acentos**: Remove acentuação de nomes para compatibilidade com formato do arquivo
8. **Filtro de Lançamentos**: Seleciona apenas lançamentos com código de liquidação = 21, tipo = 'S' (saída) e status in (1,2,4)
9. **Estrutura do Arquivo**: Cabeçalho + Detalhes + Trailer com totalizadores
10. **Atualização de Status**: Marca processamento como '3' (sucesso) ou '4' (erro) após execução
11. **Registro de Auditoria**: Insere registro em TbRegistroArquivoCompensacao para cada arquivo gerado
12. **Data de Movimento**: Utiliza data atual do sistema para processamento

---

## 6. Relação entre Entidades

**ProcessamentoCompensacao** (1) → (N) **RegistroArquivoCompensacao**
- Um processamento pode gerar múltiplos registros de arquivo

**ProcessamentoCompensacao** (N) → (1) **Filial**
- Cada processamento está associado a uma filial (cdFilial)

**Filial** (1) → (N) **Lancamento**
- Uma filial possui múltiplos lançamentos a processar

**Lancamento** - Entidade independente com dados de favorecido, remetente e valores

As entidades são POJOs simples sem anotações JPA, utilizando JDBC puro para persistência.

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbProcessamentoCompensacao | tabela | SELECT | Busca processamentos pendentes de compensação (tipo=1, status='1') |
| TBL_FILIAL | tabela | SELECT | Recupera dados da filial (mnemônico) pelo código |
| Tbl_Lancamento | tabela | SELECT | Busca lançamentos financeiros por filial, data, liquidação=21, tipo='S', status in (1,2,4) |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbProcessamentoCompensacao | tabela | UPDATE | Atualiza status do processamento (3=sucesso, 4=erro) |
| TbRegistroArquivoCompensacao | tabela | INSERT | Insere registro do arquivo gerado com flag de sucesso e nome do arquivo |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| 655[ddMM]1.doc | gravação | ItemProcessor (CAMINHO_ARQUIVO = "D:\\_robos\\javabatch-pgft-base-arquivo-abbc\\gerados\\") | Arquivo de compensação ABBC no formato DOC com lançamentos do dia |
| robo.log | gravação | Log4j (log/) | Arquivo de log da aplicação com rotação de 2MB e 5 backups |
| statistics-${executionId}.log | gravação | Log4j (log/) | Log de estatísticas de execução do batch |

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
| Sybase DBPGF_TES | Banco de Dados | Base de controle e processamento (sybdesspb.bvnet.bv:6500) |
| Sybase DBPGF | Banco de Dados | Base de dados operacionais de filiais (sybdesspb.bvnet.bv:6500) |
| UC4 | Orquestrador | Sistema agendador que recebe códigos de retorno (10, 20) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 4/10**

**Justificativa:**

**Pontos Negativos:**
- Código legado com práticas antigas (Spring 2.0, JDBC puro sem ORM)
- Hardcoded de caminhos absolutos (D:\\_robos\\...)
- Credenciais de banco expostas em arquivos XML de configuração
- Lógica de negócio complexa concentrada em uma única classe (ItemProcessor com 400+ linhas)
- Métodos muito longos e com múltiplas responsabilidades
- Falta de tratamento adequado de exceções (printStackTrace, catch genérico)
- Comentários em português com caracteres mal codificados
- Uso excessivo de Strings mágicas e números literais
- Falta de constantes para valores fixos
- Código de formatação repetitivo e verboso
- Ausência de testes unitários significativos
- Mistura de lógica de apresentação (formatação) com lógica de negócio

**Pontos Positivos:**
- Separação em camadas (DAO, Business, Batch)
- Uso de interfaces para DAOs
- Logging estruturado
- Padrão Reader-Processor-Writer bem implementado
- Documentação básica via JavaDoc em alguns métodos

---

## 14. Observações Relevantes

1. **Ambiente**: Sistema configurado para ambiente de desenvolvimento/teste (DBPGF_TES)
2. **Segurança**: Credenciais expostas nos XMLs de configuração representam risco de segurança
3. **Portabilidade**: Caminho hardcoded impede execução em outros ambientes sem modificação
4. **Manutenibilidade**: Código necessita refatoração urgente para facilitar manutenção
5. **Encoding**: Problemas de encoding em comentários sugerem migração de sistemas legados
6. **Framework Proprietário**: Dependência de framework BV Sistemas pode dificultar migração futura
7. **Formato ABBC**: Arquivo gerado segue padrão específico de compensação bancária brasileiro
8. **Processamento Diário**: Sistema processa lançamentos do dia atual (data de movimento)
9. **Banco Votorantim**: Código específico 655 indica Banco Votorantim como remetente
10. **Status de Processamento**: Sistema utiliza controle de status (1=pendente, 3=sucesso, 4=erro)