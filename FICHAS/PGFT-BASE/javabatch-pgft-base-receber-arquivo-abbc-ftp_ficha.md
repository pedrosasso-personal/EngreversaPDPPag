# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java responsável por receber arquivos da ABBC (Associação Brasileira de Bancos) via protocolo SFTP. O sistema conecta-se a um servidor SFTP, busca arquivos com sintaxes específicas (COB, CHQ, DOC) em diretórios configurados, filtra por data de modificação e copia os arquivos para diretórios locais de destino. Utiliza o framework Spring Batch para orquestração do processamento em lote.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê as configurações de movimentação de arquivos do arquivo properties e cria uma lista de DTOs com origem, destino, sintaxe e tempo de modificação |
| **ItemProcessor** | Estabelece conexão SFTP e obtém a lista de arquivos que atendem aos critérios configurados (sintaxe e tempo de modificação) |
| **ItemWriter** | Grava os arquivos obtidos do SFTP nos diretórios locais de destino |
| **SFTPUtils** | Utilitário para gerenciar conexão SFTP, listar e baixar arquivos do servidor remoto |
| **PropertiesReader** | Utilitário para leitura de propriedades de configuração |
| **MyResumeStrategy** | Estratégia de recuperação de erros que desconecta o SFTP e registra erros |
| **MovimentacaoArquivoDTO** | DTO que encapsula informações de origem, destino, sintaxe e lista de arquivos |
| **ArquivoFTPDTO** | DTO que representa um arquivo com nome e InputStream |
| **PgftException** | Exceção customizada do sistema com código de erro |

---

## 3. Tecnologias Utilizadas

- **Java** (linguagem de programação)
- **Spring Batch** (framework para processamento em lote)
- **Maven** (gerenciamento de dependências e build)
- **JSch (com.jcraft.jsch)** (biblioteca para conexão SFTP)
- **BV Framework Batch** (framework proprietário BV Sistemas)
- **BV Crypto** (criptografia de senhas)
- **Log4j** (logging)
- **JUnit** (testes unitários)
- **Bitronix** (gerenciador de transações JTA)

---

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch sem exposição de endpoints REST.

---

## 5. Principais Regras de Negócio

1. **Filtragem por Sintaxe de Arquivo**: O sistema busca apenas arquivos que correspondam aos padrões configurados (*COB*.PRN, *CHQ*.PRN, *DOC*.PRN)

2. **Filtragem por Data de Modificação**: Arquivos são baixados apenas se foram modificados dentro do período configurado (em minutos). Se o parâmetro de minutos for 0 ou nulo, a data é desconsiderada

3. **Múltiplas Configurações de Movimentação**: O sistema suporta múltiplas configurações de origem/destino através de propriedades indexadas (sftp[0], sftp[1], sftp[2])

4. **Exclusão de Diretórios**: Diretórios são ignorados durante a listagem de arquivos

5. **Sobrescrita de Arquivos**: Se o arquivo de destino já existir, ele é deletado antes da cópia

6. **Criação Automática de Diretórios**: Diretórios de destino são criados automaticamente se não existirem

7. **Descriptografia de Senha**: A senha SFTP é armazenada criptografada e descriptografada em tempo de execução usando chave configurada

---

## 6. Relação entre Entidades

**MovimentacaoArquivoDTO** (1) ----> (N) **ArquivoFTPDTO**

- MovimentacaoArquivoDTO contém:
  - origem (String): diretório de origem no SFTP
  - destino (String): diretório de destino local
  - sintaxeArquivo (String): padrão de nome de arquivo
  - minutos (Integer): janela de tempo para filtro de modificação
  - arquivos (List<ArquivoFTPDTO>): lista de arquivos encontrados

- ArquivoFTPDTO contém:
  - nome (String): nome do arquivo
  - inputStream (InputStream): stream de dados do arquivo

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBPGF_TES (database) | database | SELECT | Banco de dados configurado para testes, mas não há evidências de uso efetivo no código analisado |

**Observação**: O arquivo job-resources.xml configura conexão com banco Sybase (DBPGF_TES), mas não há queries ou operações de banco de dados implementadas no código fornecido.

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. Não há operações de INSERT, UPDATE ou DELETE em banco de dados no código analisado.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| config.properties | Leitura | PropertiesReader | Arquivo de configuração com credenciais SFTP e configurações de movimentação |
| *COB*.PRN | Leitura | SFTPUtils/ItemProcessor | Arquivos de cobrança baixados do SFTP |
| *CHQ*.PRN | Leitura | SFTPUtils/ItemProcessor | Arquivos de cheque baixados do SFTP |
| *DOC*.PRN | Leitura | SFTPUtils/ItemProcessor | Arquivos de DOC baixados do SFTP |
| entradaCOB/* | Gravação | ItemWriter | Arquivos de cobrança gravados localmente |
| entradaCHQ/* | Gravação | ItemWriter | Arquivos de cheque gravados localmente |
| entradaDOC/* | Gravação | ItemWriter | Arquivos de DOC gravados localmente |
| log/robo.log | Gravação | Log4j | Arquivo de log da aplicação |
| log/statistics-{executionId}.log | Gravação | Log4j | Arquivo de estatísticas de execução |

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
| Servidor SFTP ABBC | SFTP | Servidor FTP seguro (portalarquivosDES.bvnet.bv:22) de onde são baixados os arquivos da ABBC |

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Uso adequado do padrão Spring Batch (Reader/Processor/Writer)
- Separação de responsabilidades em classes distintas
- Uso de DTOs para transferência de dados
- Tratamento de exceções customizado
- Logging adequado das operações

**Pontos Negativos:**
- **Hardcoding de índices**: Uso de loop infinito com índices numéricos para ler propriedades (sftp[0], sftp[1], etc.) é frágil
- **Falta de validações**: Não há validação de parâmetros nulos ou vazios em vários métodos
- **Gestão de recursos**: Streams não são fechados em caso de exceção no ItemWriter (uso de try-finally ao invés de try-with-resources)
- **Comentários em português com caracteres especiais**: Comentários com encoding incorreto (ex: "execu��o", "usu�rio")
- **Senha vazia no properties**: Arquivo de configuração com senha vazia pode causar confusão
- **Falta de testes**: Apenas um teste de integração básico
- **Magic numbers**: Código de erro "10" hardcoded sem constante
- **Acoplamento**: Dependência forte do framework proprietário BV

---

## 14. Observações Relevantes

1. **Ambiente de Desenvolvimento**: As configurações apontam para ambiente de desenvolvimento (portalarquivosDES, DBPGF_TES, sybdesspb)

2. **Segurança**: O sistema utiliza criptografia BV Crypto para proteger a senha SFTP, mas a chave de criptografia está no mesmo arquivo de propriedades

3. **Versionamento**: Versão atual do componente é 0.3.0, indicando que ainda está em fase inicial de desenvolvimento

4. **Framework Proprietário**: Forte dependência do framework BV Sistemas (bv-framework-batch, bv-crypto), o que pode dificultar portabilidade

5. **Estratégia de Retry**: O sistema não implementa retry automático em caso de falha (MyResumeStrategy retorna false)

6. **Processamento Síncrono**: O batch processa sequencialmente cada configuração de movimentação

7. **Módulo**: Pertence ao módulo PGFT (Plataforma de Gestão Financeira e Tesouraria) - Base ABBC

8. **Encoding**: Projeto utiliza ISO-8859-1 em alguns arquivos XML, o que pode causar problemas com caracteres especiais