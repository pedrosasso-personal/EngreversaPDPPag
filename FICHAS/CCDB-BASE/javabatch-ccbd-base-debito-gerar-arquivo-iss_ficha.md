# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java responsável por gerar arquivo CSV de movimentações de débito ISS (Imposto Sobre Serviços) para transações de cartão de débito. O processo consulta transações do dia anterior no banco de dados DBCCBD, processa os dados aplicando regras de negócio e formatação, e gera um arquivo CSV com nome padrão `MovDebito_ddMMyyyy.csv` contendo detalhes das transações para fins fiscais/contábeis.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê registros de transações de cartão de débito do banco de dados através do repositório DetalheLoteIssRepository |
| **ItemProcessor** | Processa cada registro DetalheLoteIss e converte para RegistroIss utilizando o mapper |
| **ItemWriter** | Escreve os registros processados em arquivo CSV temporário e ao final renomeia para arquivo definitivo; grava controle na tabela TbControleArquivoIss |
| **DetalheLoteIssRepository** | Interface de acesso a dados para consulta de transações e gravação de controle de arquivo |
| **DetalheLoteIssRepositoryImpl** | Implementação do repositório usando Spring JDBC Template |
| **RegistroIssMapper** | Realiza mapeamento/conversão de DetalheLoteIss para RegistroIss aplicando regras de negócio |
| **ArquivoIssMapper** | Responsável por gerar header e linhas do arquivo CSV usando reflection |
| **DetalheLoteIss** | Entidade de domínio representando detalhes de transação lida do banco |
| **RegistroIss** | DTO representando linha do arquivo CSV a ser gerado |
| **ControleArquivo** | Entidade para controle de geração de arquivos |
| **MyResumeStrategy** | Estratégia de retomada do batch (não permite resume) |

---

## 3. Tecnologias Utilizadas

- **Java 1.6**
- **Maven 3.3+**
- **Spring Framework** (IoC/DI, JDBC Template, Transactions)
- **BV Framework Batch** (framework proprietário para processamento batch)
- **Bitronix** (gerenciador de transações JTA)
- **SQL Server** (banco de dados DBCCBD)
- **Log4j** (logging)
- **Apache Commons IO** (manipulação de arquivos)
- **JUnit e Mockito** (testes)
- **Reflection API** (geração dinâmica de arquivo)

---

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch sem endpoints REST.

---

## 5. Principais Regras de Negócio

1. **Seleção de Transações**: Busca apenas transações de lotes com status 'A' (Aberto) e data final do lote igual ao dia anterior (D-1)
2. **Mascaramento de Cartão**: Extrai BIN (6 primeiros dígitos) e 4 últimos dígitos do número de cartão mascarado
3. **Mapeamento de Bandeiras**: Aplica dados fixos específicos por bandeira (Visa/Mastercard) incluindo razão social, CNPJ, CEP, município e conta contábil
4. **Tipo de Operação**: Classifica transação como Presente (código 1) ou Virtual (código 2) baseado no flag flCartaoPresente (S/N)
5. **Natureza de Operação**: Define como "2" (Cartão Débito) fixo para todas as transações
6. **Formatação de Datas**: Converte datas para formato dd/MM/yyyy no arquivo de saída
7. **Geração de Arquivo**: Cria arquivo temporário (.tmp), escreve header e linhas, e ao final renomeia para .csv
8. **Controle de Geração**: Registra na tabela TbControleArquivoIss informações sobre arquivo gerado (lote, quantidade de registros, data)
9. **Sequenciamento**: Adiciona número sequencial a cada linha do arquivo
10. **Validação de Registros**: Se não houver registros, encerra com exit code 10 sem gerar arquivo

---

## 6. Relação entre Entidades

**DetalheLoteIss** (entidade principal de transação)
- Relaciona-se com **LoteIss** através de `cdLoteIss`
- Contém dados de cliente, estabelecimento, cartão e transação
- É mapeada para **RegistroIss** para geração do arquivo

**LoteIss**
- Agrupa transações por período (data inicial/final)
- Possui status (Aberto/Fechado)

**ControleArquivo**
- Registra metadados de arquivos gerados
- Relaciona-se com **LoteIss** através de `cdLoteIss`

**RegistroIss**
- DTO que representa linha do arquivo CSV
- Não possui relacionamento direto com banco, apenas estrutura de saída

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBCCBD.CCBDTransacaoCartaoDebito.TbLoteIss | Tabela | SELECT | Tabela de lotes ISS contendo períodos de processamento e status |
| DBCCBD.CCBDTransacaoCartaoDebito.TbDetalheLoteIss | Tabela | SELECT | Tabela de detalhes de transações de cartão de débito vinculadas a lotes |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBCCBD.CCBDTransacaoCartaoDebito.TbControleArquivoIss | Tabela | INSERT | Tabela de controle de arquivos gerados, registra metadados de cada geração |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| MovDebitoTEMP_ddMMyyyy.tmp | Gravação | ItemWriter / diretório /arquivo/ | Arquivo temporário durante geração do CSV |
| MovDebito_ddMMyyyy.csv | Gravação | ItemWriter / diretório /arquivo/ | Arquivo CSV final com movimentações de débito ISS |
| robo.log | Gravação | Log4j / diretório /log/ | Arquivo de log da aplicação |
| statistics-{executionId}.log | Gravação | Log4j / diretório /log/ | Arquivo de estatísticas de execução do batch |

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
| SQL Server (DBCCBD) | Banco de Dados | Banco de dados principal contendo tabelas de transações de cartão de débito e controle de lotes ISS. Conexão via JDBC (jTDS driver) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades entre Reader, Processor e Writer
- Uso adequado de padrões como Repository e Mapper
- Tratamento de exceções customizado com exit codes específicos
- Uso de enums para valores fixos
- Presença de testes unitários
- Logging adequado em pontos críticos

**Pontos Negativos:**
- Código legado usando Java 1.6 e frameworks antigos
- Uso excessivo de reflection para geração de arquivo (ArquivoIssMapper) tornando código menos legível
- Comentários em português misturados com código
- Caracteres especiais mal codificados (encoding issues)
- Classe RegistroIss com muitos campos (38 propriedades) sem agrupamento lógico
- Lógica de negócio espalhada entre Mapper e Writer
- Falta de validações mais robustas nos dados de entrada
- Queries SQL como strings hardcoded (embora em classe separada)
- Uso de modificadores de acesso inconsistente
- Alguns métodos muito longos (ex: handleWrite, gerarArquivoDefinitivo)

---

## 14. Observações Relevantes

1. **Framework Proprietário**: O sistema utiliza o BV Framework Batch, um framework proprietário da organização, o que pode dificultar manutenção por desenvolvedores externos
2. **Configuração por Ambiente**: Possui configurações específicas para DES, UAT e PRD em arquivos XML separados
3. **Transações JTA**: Utiliza Bitronix como gerenciador de transações distribuídas
4. **Processamento D-1**: O batch processa sempre transações do dia anterior à execução
5. **Exit Codes Customizados**: Define 12 códigos de saída específicos (10 a 120) para diferentes cenários de erro
6. **Commit Interval**: Configurado para commit a cada 10.000 registros
7. **Geração Dinâmica de CSV**: Usa reflection para gerar header e linhas do arquivo baseado na estrutura da classe RegistroIss
8. **Sem Estratégia de Resume**: O batch não permite retomada em caso de falha (MyResumeStrategy retorna false)
9. **Dados Sensíveis**: Manipula dados de cartão (mesmo que mascarados) e informações fiscais
10. **Scripts Shell e Batch**: Fornece scripts de execução para ambientes Windows (.bat) e Unix (.sh)