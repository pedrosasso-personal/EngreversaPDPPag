# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de processamento em lote (batch) desenvolvido em Java com Spring Batch para tratamento de arquivos de contingência do sistema PGFT (Pagamento de Fornecedores e Tesouraria) do Banco Votorantim. O sistema processa diversos tipos de arquivos bancários (cheques, DOC, cobrança, liquidação bilateral) provenientes do sistema SPB (Sistema de Pagamentos Brasileiro), validando, transformando e inserindo os dados na base de dados para posterior processamento. Opera em modo de contingência, processando arquivos depositados em diretório específico e movendo-os após o processamento bem-sucedido.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê arquivos do diretório de processamento e os disponibiliza para o pipeline do batch |
| **ItemProcessor** | Processa e valida os arquivos conforme tipo (cheque, DOC, cobrança, etc.), aplicando regras de negócio e transformações |
| **ItemWriter** | Move arquivos processados para diretório de arquivos processados |
| **BFilesDBItp** | Camada de negócio para operações no banco DBITP (consultas, validações, movimentação de arquivos) |
| **BFilesDBPGTes** | Camada de negócio para operações no banco DBPGF_TES (consultas de configuração de tesouraria) |
| **DAOArquivosDBItpImpl** | Implementação de acesso a dados para o banco DBITP |
| **DAOArquivosDBPGFTesImpl** | Implementação de acesso a dados para o banco DBPGF_TES |
| **SQLResourcesArquivoDBItp** | Centraliza queries SQL para o banco DBITP |
| **SQLResourcesArquivoDBPGFTes** | Centraliza queries SQL para o banco DBPGF_TES |
| **ParametrosCaixaEntrada** | Modelo de dados para parâmetros de inclusão na caixa de entrada |
| **Arquivo** | Modelo representando arquivo a ser processado |
| **ContigenciaResumeStrategy** | Estratégia de tratamento de erros e retomada do job |
| **VerificacaoArquivo** | Utilitário para validação e logging de erros em arquivos |

---

## 3. Tecnologias Utilizadas

- **Java** (versão não especificada explicitamente, provavelmente Java 6/7 pela sintaxe)
- **Spring Batch** - Framework para processamento em lote
- **Spring Framework 2.0** - Injeção de dependências e configuração
- **Maven** - Gerenciamento de dependências e build
- **Bitronix** - Gerenciador de transações JTA
- **Sybase/SQL Server** (JTDS Driver) - Banco de dados
- **Log4j** - Framework de logging
- **JUnit** - Testes unitários
- **BV Framework Batch** - Framework proprietário do Banco Votorantim para batch

---

## 4. Principais Endpoints REST

não se aplica

---

## 5. Principais Regras de Negócio

1. **Validação de Arquivos ABBC**: Verifica se o arquivo está cadastrado na tabela TBL_ARQUIVO_ABBC antes do processamento
2. **Verificação de Processamento Anterior**: Impede reprocessamento de arquivos já processados no mesmo dia
3. **Validação de CPF/CNPJ**: Valida dígitos verificadores de CPF e CNPJ de remetentes e favorecidos
4. **Verificação de Conta NOP**: Identifica contas que não são de ordem de pagamento para tratamento de CPMF
5. **Cálculo de CPMF**: Calcula e estorna CPMF quando aplicável (contas NOP em DOCs devolvidos)
6. **Validação de Finalidade SPB**: Verifica se a finalidade informada está relacionada ao tipo de liquidação
7. **Validação de Transação SPB**: Consulta se a combinação de código de transação, liquidação e origem é válida
8. **Tratamento de Cheques Administrativos**: Identifica e registra cheques administrativos separadamente
9. **Processamento por Tipo de Arquivo**: Aplica regras específicas para cada tipo (CheqCompInfe, CheqCompSupe, DocRece, DocDev, CobrRece, CheqLiqBilat, CobrLiqBilat)
10. **Validação de Agência**: Verifica se a agência do arquivo corresponde à agência configurada da filial
11. **Normalização de Dados**: Remove acentos e caracteres especiais de nomes
12. **Registro de Log de Processamento**: Grava log detalhado de erros e processamento na tabela TBL_LOG_ABBC
13. **Validação de Layout**: Verifica tamanho e formato dos registros conforme layout esperado

---

## 6. Relação entre Entidades

**Arquivo** (1) -----> (N) **Registros de Processamento**
- Um arquivo contém múltiplos registros a serem processados

**ParametrosCaixaEntrada** representa os dados de uma transação financeira com:
- Dados do Remetente (CNPJ/CPF, Agência, Conta, Nome, Endereço)
- Dados do Favorecido (CNPJ/CPF, Agência, Conta, Nome, Endereço)
- Dados da Transação (Código, Liquidação, Origem, Valor, Finalidade)
- Dados de Controle (Filial, Data Movimento, Histórico)

**Global** representa configurações da filial bancária:
- Código da Filial
- Agência
- Conta
- CNPJ
- Nome do Banco

**FinalidadeSPB** representa finalidades de transações SPB:
- Código de Liquidação
- Código de Finalidade
- Tipo de Finalidade
- Descrição

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TBL_ARQUIVO_ABBC | tabela | SELECT | Consulta tipo de arquivo ABBC pelo nome |
| TBL_LOG_ABBC | tabela | SELECT | Verifica se arquivo já foi processado no dia |
| TBL_FILIAL_SPB | tabela | SELECT | Consulta dados da filial (agência, conta, CNPJ) |
| TBL_FINALIDADE_SPB | tabela | SELECT | Consulta finalidades SPB por liquidação e tipo |
| TBL_TRANSACAO_SPB | tabela | SELECT | Valida combinação de transação, liquidação e origem |
| TBL_SETUP_TESOURARIA | tabela | SELECT | Verifica se CPMF está ativa para a filial |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TBL_LOG_ABBC | tabela | INSERT | Insere log de processamento de arquivos |
| TBL_CAIXA_ENTRADA (via procedure) | tabela | INSERT | Insere transações na caixa de entrada via procedure BV_INCLUSAO_CAIXA_ENTRADA |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| Arquivos ABBC diversos | leitura | ItemReader / BFilesDBItp | Arquivos de contingência depositados em D:\_robos\javabatch-pgft-base-contingencia-arquivo-abbc\processar\ |
| Arquivos processados | gravação | ItemWriter / BFilesDBItp | Move arquivos para D:\_robos\javabatch-pgft-base-contingencia-arquivo-abbc\processados\ após processamento |
| statistics-*.log | gravação | Scripts .bat/.sh | Arquivos de estatísticas do batch (removidos no início da execução) |
| *.tlog | gravação/remoção | Bitronix | Arquivos de log de transações do Bitronix (removidos ao final) |

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
| DBITP (Sybase) | Banco de Dados | Base de dados principal para consultas e inserções de transações SPB |
| DBPGF_TES (Sybase) | Banco de Dados | Base de dados de tesouraria para consultas de configuração |
| Sistema SPB | Arquivos | Recebe arquivos de contingência do Sistema de Pagamentos Brasileiro |

---

## 13. Avaliação da Qualidade do Código

**Nota: 3/10**

**Justificativa:**

**Pontos Negativos:**
- Código legado com práticas antigas (Spring 2.0, sintaxe Java 6/7)
- Métodos extremamente longos e complexos (ItemProcessor com mais de 2000 linhas)
- Lógica de negócio misturada com acesso a dados e apresentação
- Falta de tratamento adequado de exceções (muitos catch genéricos)
- Uso excessivo de variáveis globais e estado mutável
- Nomes de variáveis em português misturados com inglês
- Comentários em português com caracteres mal codificados
- Código duplicado em vários pontos
- Falta de testes unitários adequados
- Strings SQL construídas manualmente (risco de SQL injection)
- Hardcoded de caminhos de diretórios (D:\_robos\...)
- Credenciais de banco de dados em texto plano nos XMLs
- Métodos com responsabilidades múltiplas violando Single Responsibility Principle
- Falta de documentação JavaDoc
- Uso de tipos primitivos wrapper desnecessariamente (new Integer(), new Double())

**Pontos Positivos:**
- Separação em camadas (DAO, Business, Model)
- Uso de interfaces para DAOs
- Configuração externalizada via Spring
- Uso de framework de batch consolidado (Spring Batch)

O código necessita de refatoração significativa para melhorar manutenibilidade, testabilidade e segurança.

---

## 14. Observações Relevantes

1. **Ambiente de Desenvolvimento**: O sistema parece estar configurado para ambiente de desenvolvimento (credenciais "mgomes/mgomes123", servidor "sybdesspb.bvnet.bv")

2. **Caminhos Hardcoded**: Diretórios estão fixos em "D:\_robos\..." o que pode causar problemas em ambientes diferentes

3. **Segurança**: Credenciais de banco expostas em arquivos XML de configuração

4. **Encoding**: Problemas de encoding em comentários (caracteres � indicam problemas de codificação)

5. **Tipos de Arquivo Suportados**: 
   - CheqCompInfe/CheqCompSupe (Cheques Compensação)
   - CheqDevoDiur/CheqDevoNotu (Cheques Devolução)
   - DocRece/DocDev (DOC Recebimento/Devolução)
   - CobrRece (Cobrança Recebimento)
   - CheqLiqBilat/CobrLiqBilat (Liquidação Bilateral)

6. **Processamento Concorrente**: Configurado para permitir execução concorrente (--concurrentExecution=true)

7. **Memória JVM**: Configurado com -Xms512M -Xmx512M

8. **Framework Proprietário**: Utiliza framework BV (Banco Votorantim) para batch, o que pode dificultar manutenção fora do contexto do banco

9. **Validações Complexas**: Implementa validações de CPF/CNPJ com algoritmo de dígito verificador

10. **Procedures**: Faz uso intensivo de stored procedures do banco (BV_INCLUSAO_CAIXA_ENTRADA, BV_CONSULTA_CONTA_NOP, BV_CALCULA_CPMF, etc.)