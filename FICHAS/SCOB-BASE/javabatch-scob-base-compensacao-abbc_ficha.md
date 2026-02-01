# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java responsável pelo processamento de arquivos de compensação bancária ABBC (Associação Brasileira de Bancos) e Nuclea. O sistema realiza a leitura de arquivos de retorno bancário, processa as informações de compensação de títulos/boletos, envia mensagens para filas (IBM MQ e RabbitMQ), valida dados, atualiza status de processamento e movimenta arquivos entre diretórios conforme o resultado do processamento (sucesso/erro).

O componente possui dois fluxos principais:
- **Fluxo ABBC/SILOC**: Processa arquivos de retorno do sistema de compensação tradicional
- **Fluxo Nuclea**: Processa arquivos de retorno do novo sistema de compensação (formato específico com lotes)

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** (ABBC) | Lê arquivos de retorno ABBC do diretório pendente, move para processando e disponibiliza linhas para processamento |
| **ItemReader** (Nuclea) | Lê arquivos de retorno Nuclea (formato ACMP), valida nome do arquivo, processa linhas em lotes de até 100 registros |
| **ItemProcessor** (ABBC) | Processa cada linha do arquivo (transformação mínima) |
| **ItemProcessor** (Nuclea) | Transforma linhas em mensagens tipadas (Cabecalho, Detalhe, FechamentoLote, Trailer) |
| **ItemWriter** (ABBC) | Envia detalhes para filas MQ, controla reprocessamento, valida arquivo, registra início/fim de processo |
| **ItemWriter** (Nuclea) | Agrupa mensagens em lotes, envia para RabbitMQ, valida processamento dos lotes |
| **LoteNuclea** | Representa um lote de até 100 mensagens Nuclea, controla envio e validação |
| **BuscaMensagemSaida** | Thread que consome mensagens de retorno das filas, controla reprocessamento e timeout |
| **ControleProcessamentoMensagemSaida** | Controla estatísticas de envio/recebimento de mensagens e erros |
| **MQConnectionProvider** | Gerencia conexões com IBM MQ (criação de producers, consumers, envio/leitura de mensagens) |
| **LoteRepositoryRabbit** | Envia lotes Nuclea para RabbitMQ e valida processamento |
| **FileUtil / FileUtilNuclea** | Utilitários para manipulação de arquivos (mover, validar, compactar/descompactar GZIP) |
| **ControleArquivoDaoImpl** | Registra início/fim de processamento no banco de dados |

---

## 3. Tecnologias Utilizadas

- **Java 7** (JDK 7)
- **Maven** (gerenciamento de dependências e build)
- **BV Framework Batch** (framework proprietário para processamento batch)
- **IBM MQ** (WebSphere MQ) - filas de mensageria
- **RabbitMQ** (Spring AMQP) - mensageria para fluxo Nuclea
- **Spring Framework** (IoC/DI, configuração XML)
- **JDBC** (acesso a banco de dados SQL Server/Sybase)
- **Log4j** (logging)
- **Gson** (serialização/deserialização JSON)
- **JSON Simple** (manipulação JSON)
- **JUnit / Mockito / PowerMock** (testes unitários)

---

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch que não expõe endpoints REST.

---

## 5. Principais Regras de Negócio

1. **Validação de Nome de Arquivo Nuclea**: Arquivos devem seguir o padrão `ACMP615_59588111_YYYYMMDD_655XX` (onde XX é o sequencial)
2. **Processamento em Lotes**: Mensagens Nuclea são agrupadas em lotes de até 100 registros para envio
3. **Reprocessamento Automático**: Sistema tenta reprocessar mensagens com erro até 3 vezes (configurável)
4. **Timeout de Processamento**: Aguarda até 3 minutos (Nuclea) ou 10 minutos (ABBC) por respostas das filas
5. **Exclusão de Outros Bancos**: Linhas com código de barras que não iniciam com "655" (Banco Votorantim) são ignoradas no fluxo Nuclea
6. **Validação de Arquivo**: Compara quantidade e valor total de registros processados com totais do arquivo
7. **Processamento STR 250000**: Para tipo de processo "TOBE", busca lançamentos STR online adicionais
8. **Controle de Duplicidade**: Utiliza chave `nuNossoNumero + nuConvenio` para evitar duplicação de registros
9. **Movimentação de Arquivos**: Arquivos são movidos para diretórios específicos (sucesso/erro) conforme resultado
10. **Compactação/Descompactação**: Arquivos são convertidos de encoding original para UTF-8 via GZIP

---

## 6. Relação entre Entidades

**Fluxo ABBC:**
- `ArquivoRetornoBanco` (1) -> (N) `DetalheMensagemSaida`
- `CabecalhoMensagemSaida` (1) -> (N) `DetalheMensagemSaida`
- `RegraCompensacao` (N) -> (N) `DetalheMensagemSaida`
- `ISPBBanco` (N) -> (N) `DetalheMensagemSaida`

**Fluxo Nuclea:**
- `LoteNuclea` (1) -> (N) `Mensagem<T>`
- `Mensagem<T>` pode conter: `CabecalhoNuclea`, `DetalheNuclea`, `FechamentoLoteNuclea` ou `TrailerNuclea`
- Cada tipo de mensagem possui referência a `LinhaNuclea` (linha original do arquivo)
- `MensagemRetornoNuclea` representa o retorno do processamento de um lote

**Relacionamentos de Controle:**
- `ControleProcessamentoMensagemSaida` agrega `LogProcessamento` e `NotificaoFimProcessamentoEntrada`
- `BuscaMensagemSaida` (Thread) consome `NotificaoFimProcessamentoEntrada` das filas

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| DbCobrancabco..TbCadastroArquivoRetornoBanco | Tabela | SELECT | Recupera configurações de cadastro de arquivos de retorno |
| DbCobrancabco..tbarquivoRetornoBanco | Tabela | SELECT | Verifica se arquivo já foi processado anteriormente |
| DbCobrancabco..TbArquivoRetornoBancoDetalhe | Tabela | SELECT | Consulta detalhes de arquivos processados (quantidade, registros rejeitados) |
| DBISPB..vw_mvsr_movimento_str_online | View | SELECT | Consulta lançamentos STR 250000 (Sistema de Transferência de Reservas) |
| dbispb..tb_ispb_ispb | Tabela | SELECT | Consulta informações de bancos por código ISPB |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| DBCOBRANCABCO..TBARQUIVORETORNOBANCO | Tabela | INSERT/UPDATE | Insere/atualiza informações do arquivo de retorno processado |
| DBCOBRANCABCO..TBARQUIVORETORNOBANCODETALHE | Tabela | INSERT/UPDATE | Insere detalhes das linhas do arquivo; atualiza UF dos lotes |
| DbGestaoCobranca..TbControleExecucaoProcesso | Tabela | UPDATE (via SP) | Registra início/fim de execução do processo batch |
| DbCobrancabco..TbStatusProcessamentoArquivoRetornoBanco | Tabela | UPDATE (via SP) | Atualiza status de processamento do arquivo |

**Stored Procedures Executadas:**
- `DbGestaocobranca..PrControleExecucaoProcesso` - Controla execução do processo
- `DbCobrancaBco..PrGerarStatusProcesArqRetBanco` - Gera status final do processamento
- `DbGestaoCobranca..PrProcessamentoCompensacao` - Processa compensação de títulos
- `DbCobrancabco..SpGerarNovoSequencial` - Gera novo sequencial

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| ACMP615_59588111_YYYYMMDD_655XX | Leitura | ItemReader (Nuclea) | Arquivo de retorno Nuclea (formato posicional 199 caracteres) |
| COB615*.RET | Leitura | ItemReader (ABBC) | Arquivo de retorno ABBC/SILOC |
| *.gz | Leitura/Gravação | FileUtilNuclea | Arquivos compactados GZIP (conversão de encoding) |
| robo.log | Gravação | Log4j | Log de execução do batch |
| statistics-{executionId}.log | Gravação | BvDailyRollingFileAppender | Log de estatísticas de execução |

**Diretórios utilizados:**
- `carga.pendente` / `carga.nuclea.pendente` - Arquivos aguardando processamento
- `carga.processando` / `carga.nuclea.processando` - Arquivos em processamento
- `carga.sucesso` / `carga.nuclea.sucesso` - Arquivos processados com sucesso
- `carga.erro` / `carga.nuclea.erro` - Arquivos com erro no processamento

---

## 10. Filas Lidas

**IBM MQ (Fluxo ABBC):**
- `QL.SCOB.BATCH_COMP_INSERE_CABECALHO.RSP` - Resposta de inserção de cabeçalho
- `QL.SCOB.BATCH_COMP_BUSCA_REGRAS.RSP` - Resposta com regras de compensação
- `QL.SCOB.BATCH_COMP_FIM_PROCESSAMENTO.RSP` - Notificações de fim de processamento de detalhes
- `QL.SCOB.BATCH_COMP_PROCESSA_STR_ONLINE.RSP` - Resposta com registros STR 250000

**RabbitMQ (Fluxo Nuclea):**
- `events.business.SCOB.CompensacaoRetorno` - Retorno do processamento de lotes Nuclea

---

## 11. Filas Geradas

**IBM MQ (Fluxo ABBC):**
- `QL.SCOB.BATCH_COMP_PROCESSA_ABBC.INT` - Envio de detalhes para processamento
- `QL.SCOB.BATCH_COMP_INSERE_CABECALHO.INT` - Envio de cabeçalho do arquivo
- `QL.SCOB.BATCH_COMP_BUSCA_REGRAS.INT` - Solicitação de regras de compensação
- `QL.SCOB.BATCH_COMP_REGISTRA_INICIO_PROCESSO.INT` - Registro de início de processo
- `QL.SCOB.BATCH_COMP_REGISTRA_FIM_PROCESSO.INT` - Registro de fim de processo
- `QL.SCOB.BATCH_ATUALIZA_STATUS.INT` - Atualização de status do arquivo
- `QL.SCOB.BATCH_COMP_PROCESSA_STR_ONLINE.INT` - Solicitação de registros STR 250000

**RabbitMQ (Fluxo Nuclea):**
- `events.business.SCOB.CompensacaoEnvio` (routing key: `SCOB.CompensacaoEnvio.v1`) - Envio de lotes para processamento
- `events.business.SCOB.ConfirmacaoProcessamentoNuclea` (routing key: `SCOB.ConfirmacaoProcessamentoNuclea.v1`) - Confirmação de processamento do arquivo

---

## 12. Integrações Externas

1. **IBM MQ (WebSphere MQ)** - Comunicação assíncrona com componentes de processamento de compensação
2. **RabbitMQ** - Comunicação assíncrona para fluxo Nuclea (novo sistema de compensação)
3. **Banco de Dados SQL Server/Sybase** - Persistência de dados de compensação e controle de processamento
   - Schemas: `DbCobrancabco`, `DbGestaoCobranca`, `DBISPB`
4. **Sistema de Arquivos** - Leitura/gravação de arquivos de retorno bancário em diretórios compartilhados
5. **Componentes Orquestradores** (via filas):
   - `orch-suporte-negocio` - Fornece regras de compensação
   - Componentes de processamento de detalhes e cabeçalhos
   - Componente de consulta STR online

---

## 13. Avaliação da Qualidade do Código

**Nota:** 5/10

**Justificativa:**

**Pontos Positivos:**
- Separação clara entre fluxos ABBC e Nuclea
- Uso de padrões de projeto (Factory, Repository)
- Tratamento de exceções e logs detalhados
- Testes unitários presentes (JUnit, Mockito)
- Uso de enums para tipos e status

**Pontos Negativos:**
- **Código legado com muitas responsabilidades misturadas**: Classes como `ItemWriter` (ABBC) possuem mais de 600 linhas com múltiplas responsabilidades
- **Acoplamento alto**: Dependência forte de frameworks proprietários (BV Framework) e configurações XML
- **Falta de documentação**: Comentários escassos, nomes de variáveis em português misturados com inglês
- **Tratamento de erros genérico**: Muitos `catch (Exception e)` sem tratamento específico
- **Código duplicado**: Lógica de movimentação de arquivos repetida em várias classes
- **Hardcoded values**: Valores como tamanho de lote (100, 50) e timeouts espalhados pelo código
- **Complexidade ciclomática alta**: Métodos longos com múltiplos níveis de aninhamento
- **Uso de tipos obsoletos**: `Date` ao invés de `LocalDateTime`, `JSONObject` ao invés de DTOs
- **Thread management manual**: Controle de threads sem uso de ExecutorService
- **Falta de injeção de dependências adequada**: Muitas dependências criadas manualmente

---

## 14. Observações Relevantes

1. **Ambiente de Execução**: Sistema batch executado via UC4 (agendador) em ambiente Windows (caminhos com `D:\\_robos\\`)

2. **Encoding**: Sistema realiza conversão de encoding via compactação/descompactação GZIP para garantir UTF-8

3. **Controle de Concorrência**: Utiliza stored procedure `PrControleExecucaoProcesso` para evitar execuções simultâneas

4. **Versionamento**: Versão atual 0.55.0, com histórico de evolução no Git

5. **Piloto TOBE/ASIS**: Sistema possui lógica condicional baseada em tipo de processo piloto, indicando transição entre sistemas

6. **Reprocessamento Inteligente**: Sistema identifica registros com timeout e os reprocessa separadamente

7. **Validação de Integridade**: Compara totais do arquivo com dados processados para garantir consistência

8. **Correlação de Mensagens**: Utiliza `correlationId` baseado em timestamp para rastrear mensagens relacionadas

9. **Configuração por Ambiente**: Arquivos de propriedades separados para local (`-local`) e produção

10. **Dependências de Segurança**: Utiliza versões antigas de bibliotecas (Jackson 2.12.7.1) que podem ter vulnerabilidades conhecidas