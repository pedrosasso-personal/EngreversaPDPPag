# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java desenvolvido para processar arquivos de retorno da ABBC (Associação Brasileira de Bancos). O sistema lê arquivos `.PRN` de uma pasta de entrada, processa informações sobre arquivos de compensação bancária, atualiza o status no banco de dados e envia notificações por email com os resultados do processamento. Após o processamento bem-sucedido, os arquivos são movidos para uma pasta de saída; em caso de erro, são movidos para uma pasta de erro.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê arquivos `.PRN` do diretório de entrada configurado |
| **ItemProcessor** | Processa o conteúdo dos arquivos, extraindo informações de compensação e detalhes |
| **ItemWriter** | Atualiza o banco de dados com as informações processadas e move os arquivos |
| **ArquivoCompensacaoDAO** | Realiza operações de banco de dados (consulta e atualização) |
| **MyResumeStrategy** | Estratégia de recuperação de erros, move arquivos com erro para pasta específica |
| **ArquivoCompensacaoDTO** | Representa dados de arquivo de compensação |
| **ArquivoRetornoDTO** | Encapsula arquivo físico e lista de arquivos de compensação |
| **DetalheArquivoCompensacaoDTO** | Representa detalhes de linhas com erro no arquivo |
| **FileUtil** | Utilitário para movimentação de arquivos |
| **MailSender / SmtpMail** | Envio de emails com anexos dos arquivos processados |
| **PropertiesReader** | Leitura de propriedades de configuração |
| **PgftException** | Exceção customizada com código de erro |

---

## 3. Tecnologias Utilizadas

- **Spring Batch** (framework de processamento batch)
- **Spring Framework** (injeção de dependências e configuração)
- **Maven** (gerenciamento de dependências e build)
- **Sybase ASE** (banco de dados - servidor: sybdesspb.bvnet.bv)
- **Bitronix** (gerenciador de transações JTA)
- **JavaMail API** (envio de emails)
- **BV Framework Batch** (framework proprietário da BV Sistemas)
- **BV JDBC Driver** (driver JDBC customizado)
- **Log4j** (logging)
- **JUnit** (testes unitários)

---

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch sem endpoints REST.

---

## 5. Principais Regras de Negócio

1. **Processamento de Status de Compensação**: O sistema identifica e atualiza diferentes status de compensação:
   - Status 4: ENVIADO
   - Status 5: REJEITADO
   - Status 6: CONFIRMADO (quando arquivo é aceito)
   - Status 12: RECEBIDO (para arquivos .doc)

2. **Validação de Formato de Arquivo**: Processa apenas arquivos com extensão `.PRN` e valida estrutura interna com linhas específicas (header, transmissão, detalhes)

3. **Atualização Condicional**: Atualiza apenas registros com status 3, 4 ou 11 no banco de dados

4. **Tratamento de Detalhes de Erro**: Captura e armazena detalhes de linhas com problemas no processamento

5. **Notificação por Email**: Envia email com anexos dos arquivos processados (sucesso e erro) ao final da execução

6. **Movimentação de Arquivos**: Arquivos processados com sucesso vão para pasta de saída; arquivos com erro vão para pasta de erro

7. **Identificação de Arquivos COB**: Utiliza prefixo configurável para identificar arquivos de cobrança

8. **Extração de Data de Retorno**: Extrai data/hora do cabeçalho e da linha de transmissão dos arquivos

---

## 6. Relação entre Entidades

**ArquivoRetornoDTO** (1) -----> (N) **ArquivoCompensacaoDTO** (1) -----> (N) **DetalheArquivoCompensacaoDTO**

- Um arquivo de retorno físico contém múltiplos arquivos de compensação
- Cada arquivo de compensação pode ter múltiplos detalhes de erro
- Relacionamento é mantido em memória durante o processamento

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBPGF_TES..TbArquivoCompensacao | tabela | SELECT | Busca o código do arquivo de compensação pelo nome do arquivo |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBPGF_TES..TbArquivoCompensacao | tabela | UPDATE | Atualiza status, data de recebimento, chave ABBC e resultado do processamento |
| DBPGF_TES..TbDetalheArquivoCompensacao | tabela | UPDATE | Atualiza status de todos os detalhes do arquivo e detalhes específicos com descrição de erro |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| *.PRN | leitura | ItemReader / pasta configurada em `pasta.entrada` | Arquivos de retorno da ABBC |
| *.PRN | gravação (movimentação) | ItemWriter / pasta configurada em `pasta.saida` | Arquivos processados com sucesso |
| *.PRN | gravação (movimentação) | MyResumeStrategy / pasta configurada em `pasta.erro` | Arquivos com erro no processamento |
| statistics-*.log | gravação/remoção | Scripts .bat/.sh | Arquivos de estatísticas removidos no início da execução |
| *.tlog | gravação/remoção | Scripts .bat/.sh | Arquivos de log do Bitronix removidos ao final |

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
| **ABBC** | Arquivo | Sistema recebe arquivos de retorno da Associação Brasileira de Bancos |
| **Servidor SMTP** | Email | Envio de notificações via `smtpduqrelay.bvnet.bv` |
| **Banco Sybase** | Banco de Dados | Conexão com `sybdesspb.bvnet.bv:6500` database `DBPGF_TES` |

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Estrutura bem organizada seguindo padrão Spring Batch (Reader/Processor/Writer)
- Separação de responsabilidades em camadas (DAO, DTO, batch, util)
- Tratamento de exceções customizado com códigos de erro
- Uso de framework consolidado (Spring Batch)
- Documentação básica presente (JavaDoc em algumas classes)

**Pontos Negativos:**
- **Encoding problemático**: Uso de ISO-8859-1 e conversões manuais de encoding podem causar problemas
- **Hardcoded values**: Múltiplos valores fixos no código (status de compensação, strings de validação)
- **Tratamento de exceções genérico**: Catch de `Exception` em vários pontos
- **Falta de constantes**: Strings literais repetidas ao longo do código
- **Comentários em português com caracteres especiais**: Podem causar problemas de encoding
- **Lógica complexa no Processor**: Método `processarLinha` com múltiplas responsabilidades
- **Falta de testes**: Apenas estrutura de teste presente, sem implementação
- **Configuração de senha em texto claro**: Embora haja comentário sobre criptografia, a senha está exposta
- **Uso de `LinkedHashMap` sem justificativa clara**: Poderia ser simplificado
- **Falta de validações**: Pouca validação de dados de entrada

---

## 14. Observações Relevantes

1. **Ambiente**: Configuração atual aponta para ambiente de desenvolvimento (DES). Há comentários indicando necessidade de ajustes para QA/UAT/PROD, especialmente relacionados à criptografia de senha.

2. **Códigos de Retorno**: Sistema utiliza códigos de saída específicos (0, 11-17) para indicar diferentes tipos de erro, facilitando monitoramento.

3. **Processamento Concorrente**: Configurado para permitir execução concorrente (`concurrentExecution=true`).

4. **Memória**: Scripts configurados com 512MB de heap (`-Xms512M -Xmx512M`).

5. **Dependências Proprietárias**: Sistema depende fortemente de frameworks proprietários da BV Sistemas, dificultando portabilidade.

6. **Versionamento**: Versão atual 0.6.0, indicando que ainda está em desenvolvimento/evolução.

7. **Encoding**: Sistema trabalha com conversão entre UTF-8 (arquivo) e ISO-8859-1 (banco), o que pode ser fonte de problemas com caracteres especiais.

8. **Estratégia de Recuperação**: Implementa estratégia customizada de recuperação de erros, permitindo que o batch continue processando outros arquivos mesmo quando um falha.