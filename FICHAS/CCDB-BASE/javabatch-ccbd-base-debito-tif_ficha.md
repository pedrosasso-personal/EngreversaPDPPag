# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de processamento batch Java responsável por ler arquivos TIF (Transaction Interchange Format) contendo transações de débito de cartões, processar os registros e publicar as informações em uma fila RabbitMQ para conciliação. O sistema faz parte do módulo CCBD (Centro de Controle de Base de Débito) da Votorantim e processa arquivos posicionais com dados de transações financeiras, realizando parsing, transformação e envio para sistemas downstream via mensageria.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê arquivos TIF do diretório de recebidos, faz parsing linha a linha e identifica registros de detalhe (tipo 30) |
| **ItemProcessor** | Transforma objetos Tif em RecordConciliation, adicionando metadados do arquivo processado |
| **ItemWriter** | Publica mensagens JSON na fila RabbitMQ para processamento downstream |
| **TifMapper** | Realiza o mapeamento posicional das linhas do arquivo TIF para objetos Tif |
| **RecordConciliationMapper** | Converte objetos Tif em RecordConciliation, formatando valores monetários |
| **Tif** | Modelo de dados representando uma transação TIF com todos os campos posicionais |
| **RecordConciliation** | Modelo de dados para conciliação enviado à fila |
| **FileUtil** | Utilitário para movimentação de arquivos entre diretórios (recebidos/processados/erro) |
| **StringUtil** | Utilitário para extração de substrings posicionais e conversões de tipos |
| **MyResumeStrategy** | Estratégia de retomada do job em caso de falha |

---

## 3. Tecnologias Utilizadas

- **Spring Batch** - Framework de processamento batch
- **Spring AMQP / RabbitMQ** - Mensageria (versão 1.2.0.M1)
- **Maven** - Gerenciamento de dependências e build
- **Log4j** - Logging
- **Jackson** (2.12.7) - Serialização JSON
- **BV Framework Batch** - Framework proprietário da BV Sistemas para jobs batch
- **Java** - Linguagem de programação
- **JUnit / Mockito** - Testes unitários

---

## 4. Principais Endpoints REST

não se aplica

---

## 5. Principais Regras de Negócio

1. **Filtragem de Registros**: Apenas registros do tipo "30" (DETAIL) são processados; registros de header (10) e trailer (31) são ignorados
2. **Filtragem de Arquivos**: Somente arquivos com extensão ".DAT" e contendo "TIF" no nome são processados
3. **Conversão Monetária**: Valores monetários são convertidos de formato inteiro para decimal com 2 casas decimais (divisão por 100)
4. **Mascaramento de Cartão**: Números de cartão são mantidos mascarados durante todo o processamento
5. **Movimentação de Arquivos**: Arquivos processados com sucesso são movidos para diretório "processados"; em caso de erro, para diretório "erro"
6. **Enriquecimento de Dados**: Cada registro é enriquecido com o nome do arquivo de origem
7. **Indicador Wallet**: Campo indicadorTransacaoWallet é definido como "S" se presente, "N" se vazio
8. **Serialização Completa**: Objeto Tif completo é serializado em JSON e armazenado no campo camposComplementares
9. **Tipo de Arquivo**: Todos os registros são marcados com tipoArquivoProcessado = "TIF"

---

## 6. Relação entre Entidades

**Tif** (1) -----> (1) **RecordConciliation**

- **Tif**: Entidade de entrada representando uma linha de detalhe do arquivo TIF com 57 campos posicionais incluindo dados de transação, cartão, estabelecimento, valores monetários e informações de chip
- **RecordConciliation**: Entidade de saída para conciliação contendo campos resumidos da transação (valor, data, moeda, tipo, cartão mascarado, autorizador) e o objeto Tif completo serializado em JSON no campo camposComplementares

O mapeamento é realizado pelo **RecordConciliationMapper** que extrai campos específicos do Tif e converte valores monetários de String para BigDecimal.

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| *.DAT (contendo "TIF") | Leitura | ItemReader / FileUtil | Arquivos posicionais TIF com transações de débito |
| robo.log | Gravação | Log4j (RollingFileAppender) | Log de execução do batch (máx 2MB, 5 backups) |
| statistics-{executionId}.log | Gravação | BvDailyRollingFileAppender | Log de estatísticas do framework BV |
| Arquivos processados | Movimentação | ItemReader.handleDispose() | Arquivos movidos de /recebidos para /processados após sucesso |
| Arquivos com erro | Movimentação | ItemReader.handleDispose() | Arquivos movidos de /recebidos para /erro em caso de falha |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

**Exchange**: `events.ex.business.ccbd.registroBandeira`  
**Routing Key**: `CCBD.registroBandeira`  
**Tipo de Mensagem**: JSON (RecordConciliation serializado)  
**Classe Responsável**: ItemWriter  
**Configuração**: RabbitMQ configurado via job-resources.xml com hosts diferentes por ambiente (DES: 10.39.216.137, UAT: 10.39.88.213, PRD: 10.39.49.197)

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **RabbitMQ** | Mensageria | Publicação de registros de conciliação para processamento downstream. Conexão via Spring AMQP com confirmação de publicação habilitada (publisherConfirms=true, publisherReturns=true) |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 6/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades entre Reader, Processor e Writer
- Uso adequado do padrão Spring Batch
- Mappers dedicados para transformação de dados
- Tratamento de erros com códigos de saída específicos
- Movimentação organizada de arquivos por status

**Pontos Negativos:**
- Classe Tif com 57 atributos sem encapsulamento lógico (poderia ser dividida em subdomínios)
- Parsing posicional hardcoded com números mágicos (posições 1-2, 3-11, etc.) sem constantes ou documentação do layout
- Variável estática mutável em FileUtil (total) que pode causar problemas em execuções concorrentes
- Falta de validações de dados (campos obrigatórios, formatos, ranges)
- Comentários em português misturados com código em inglês
- Caracteres especiais mal codificados em comentários (�)
- Uso de versões antigas de bibliotecas (Spring AMQP 1.2.0.M1 de 2012)
- Falta de tratamento específico para diferentes tipos de erro
- Logs com informações sensíveis (objeto completo com dados de transação)
- Método getString com try-catch genérico que mascara erros

---

## 14. Observações Relevantes

1. **Ambientes**: Sistema configurado para 3 ambientes (DES, UAT, PRD) com credenciais e hosts RabbitMQ específicos
2. **Formato do Arquivo**: Arquivo TIF posicional com 1166 caracteres por linha, contendo header (tipo 10), detalhes (tipo 30) e trailer (tipo 31)
3. **Concorrência**: Job configurado com concurrentExecution=true, mas FileUtil usa lista estática que não é thread-safe
4. **Exit Codes**: Sistema define códigos de saída específicos (10=erro leitura, 20=erro processamento, 30=erro fila MQ, 40=erro posting)
5. **Framework Proprietário**: Utiliza framework BV Sistemas (bv-framework-batch) que encapsula Spring Batch
6. **Encoding**: Arquivos lidos em UTF-8 conforme Scanner no ItemReader
7. **Memória**: JVM configurada com -Xms512M -Xmx512M
8. **Bitronix**: Referências a remoção de arquivos .tlog do Bitronix (gerenciador de transações) nos scripts de execução
9. **Versionamento**: Projeto na versão 0.16.0, indicando maturidade moderada
10. **Deploy**: Propriedade disableQADeploy=true indica que deploy em QA está desabilitado