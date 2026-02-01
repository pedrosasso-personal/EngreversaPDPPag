# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java desenvolvido com Spring Batch para processamento de arquivos de retorno de baixa de cobrança bancária. O sistema consome mensagens de filas IBM MQ contendo dados de retorno de cobrança (liquidações, baixas, rejeições, etc.), processa e formata esses dados conforme layouts específicos (CNAB 400 e CNAB 240), e gera arquivos de retorno para clientes, disponibilizando-os em diretórios VAN (Value Added Network). O processamento inclui enriquecimento de dados, consolidação de registros, validação de arquivos e rastreamento de status.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **RetornoBaixaReader** | Lê mensagens das filas MQ (formatadas e orquestração), controla o fluxo de leitura e gerencia timeouts |
| **RetornoBaixaWriter** | Processa mensagens recebidas, consolida dados por arquivo, formata e grava arquivos de retorno, envia atualizações |
| **ItemProcessor** | Processador intermediário (implementação simples que apenas repassa o JSONObject) |
| **RetornoBaixaStrategy** | Estratégia de retomada do job (não implementa retomada) |
| **FormatadorService** | Formata arquivos de retorno conforme layouts CNAB 400/240, valida arquivos gerados |
| **AtualizarService** | Envia mensagens de atualização de status dos títulos para filas MQ |
| **RastreioService** | Registra eventos de rastreamento (fim de arquivo, erro, fim de processo) |
| **MQConnectionProvider** | Gerencia conexões com IBM MQ (criação de producers/consumers, envio/leitura de mensagens) |
| **ControleArquivo** | Controla o processamento de cada arquivo (contadores, status, consolidação) |
| **FileUtil** | Utilitários para manipulação de arquivos e diretórios (criação, movimentação, limpeza) |

---

## 3. Tecnologias Utilizadas

- **Java** (versão não especificada explicitamente, mas compatível com Java 6+)
- **Spring Batch** (framework de processamento batch)
- **Spring Framework** (injeção de dependências, configuração XML)
- **IBM MQ** (WebSphere MQ) - mensageria
- **Maven** - gerenciamento de dependências e build
- **Log4j** (1.2.8) - logging
- **JSON Simple** (1.1.1) - manipulação de JSON
- **Gson** (2.8.6) - serialização/deserialização JSON
- **Apache Commons IO** - utilitários de I/O
- **Apache Commons Lang** - utilitários gerais
- **JUnit** (4.13.2) - testes unitários
- **Mockito** (2.28.2) - mocks para testes
- **PowerMock** (2.0.9) - mocks avançados

---

## 4. Principais Endpoints REST

não se aplica

---

## 5. Principais Regras de Negócio

1. **Processamento por Tipo de Execução**: Suporta execução COMPLETA (8 tipos de enriquecimento) ou PARCIAL (2 tipos: liquidação e baixa)

2. **Consolidação de Registros de Rejeição**: Múltiplas rejeições do mesmo título são consolidadas em um único registro com códigos de erro concatenados (máximo 4 erros)

3. **Particionamento por Lote (Layout 240)**: Arquivos CNAB 240 são particionados em lotes por convênio, com headers e trailers específicos

4. **Validação de Arquivos Gerados**: Valida quantidade de registros de liquidação e valor total contra valores esperados

5. **Controle de Duplicidade**: Detecta e rejeita arquivos com registros duplicados

6. **Timeout de Processamento**: Implementa timeouts configuráveis para leitura de filas (padrão 20 minutos)

7. **Rastreamento de Arquivos**: Registra início, fim e erros de processamento de cada arquivo

8. **Movimentação para VAN**: Arquivos processados são movidos para diretórios VAN específicos do cliente, com cópias para Internet Banking quando aplicável

9. **Tratamento de Arquivos EDI**: Arquivos EDI seguem fluxo diferenciado (não são enviados diretamente para IB)

10. **Consolidação de Valores**: Calcula valores totais por carteira (simples, caucionada) e por arquivo

---

## 6. Relação entre Entidades

**Principais Entidades e Relacionamentos:**

- **ControleArquivo**: Entidade central que controla o processamento de um arquivo
  - Contém: Cliente, Convenios[], MensagemPosicaoRetornoArquivo, ArquivosEntidade, ClientReturnFileConsolidation
  - Relacionamento 1:1 com ArquivosEntidade (arquivos temporários de cada tipo de enriquecimento)
  - Relacionamento 1:1 com ClientReturnFileConsolidation (consolidação de valores e contadores)

- **MensagemPosicaoRetornoArquivo**: Representa os dados de entrada de um arquivo
  - Contém: Cliente, Convenios[], arquivos de entidades por tipo
  - Relacionamento 1:1 com Cliente

- **Cliente**: Dados do cliente
  - Contém: Lista de Convenio
  - Relacionamento 1:N com Convenio

- **Entidade**: Representa um registro de retorno (título)
  - Contém: Portador (opcional), Bolepix (opcional)
  - Relacionamento 0:1 com Portador
  - Relacionamento 0:1 com Bolepix

- **ArquivosEntidade**: Gerencia arquivos temporários por tipo de enriquecimento
  - Contém: File e Writer para cada tipo (entrada, rejeição, instrução, liquidação, baixa, cartório, inconsistência, transferência)

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
| layouts.tmp | Leitura | FileUtil, RetornoBaixaReader | Arquivo JSON com definições de layouts CNAB 400/240 |
| listaEntidade_*.tmp | Leitura/Gravação | ArquivosEntidade, RetornoBaixaWriter | Arquivos temporários com entidades por tipo de enriquecimento |
| *.RET | Gravação | FormatadorService, FileUtil | Arquivos de retorno formatados CNAB 400/240 |
| Arquivos VAN | Gravação | FileUtil.criarArquivoVan | Arquivos movidos para diretórios VAN dos clientes |
| Arquivos IB | Gravação | FileUtil.createIBFiles | Cópias de arquivos para Internet Banking |

---

## 10. Filas Lidas

| Nome da Fila | Descrição |
|--------------|-----------|
| **QL.SCOB.BATCH_BAIXA_ARQ_FORMATADO.INT** | Fila principal de processamento contendo mensagens com dados formatados de retorno de cobrança |
| **QL.SCOB.BATCH_BAIXA_FIM_JOB.INT** | Fila de controle para mensagens de orquestração (início/fim de processo) e retorno de atualizações |

---

## 11. Filas Geradas

| Nome da Fila | Descrição |
|--------------|-----------|
| **QL.SCOB.BATCH_BAIXA_INICIO_JOB.INT** | Fila para enviar mensagem de início de processamento ao orquestrador |
| **QL.SCOB.BATCH_BAIXA_STATUS_RETORNO.RSP** | Fila para enviar atualizações de status dos títulos processados |
| **QL.SCOB.BATCH_BAIXA_FIM_ARQ.INT** | Fila para registrar conclusão de processamento de arquivos |
| **QL.SCOB.BATCH_BAIXA_DEL_ARQ.INT** | Fila para registrar arquivos deletados (sem registros) |
| **QL.SCOB.BATCH_RASTREIO_FIM_PROCESSO.INT** | Fila para registrar fim do processo batch |
| **QL.SCOB.BATCH_RASTREIO_ERRO_ARQUIVO.INT** | Fila para registrar erros no processamento de arquivos |

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **IBM MQ (WebSphere MQ)** | Mensageria | Sistema de filas para comunicação assíncrona com outros componentes |
| **Orquestrador de Clientes** | Serviço Interno | Sistema que coordena o processamento, envia lista de arquivos e layouts |
| **VAN (Value Added Network)** | Sistema de Arquivos | Diretórios de rede para disponibilização de arquivos aos clientes |
| **Internet Banking** | Sistema de Arquivos | Diretórios para disponibilização de arquivos ao IB |

---

## 13. Avaliação da Qualidade do Código

**Nota: 5/10**

**Justificativa:**

**Pontos Positivos:**
- Estrutura bem organizada com separação de responsabilidades (reader, writer, services)
- Uso adequado de enums para constantes e tipos
- Logging presente em pontos críticos
- Tratamento de exceções customizadas

**Pontos Negativos:**
- **Código comentado e mock**: Presença de código comentado e variáveis de mock (listaRetornoMock, orchClienteMock) indicando falta de limpeza
- **Complexidade excessiva**: Classes como RetornoBaixaWriter têm mais de 800 linhas com múltiplas responsabilidades
- **Threads não gerenciadas adequadamente**: Uso de threads sem pool ou gerenciamento adequado (FormatarThread, AtualizarThread)
- **Acoplamento alto**: Dependência direta de IBM MQ sem abstração adequada
- **Falta de testes**: Arquivos de teste presentes mas marcados como NAO_ENVIAR
- **Hardcoded values**: Valores como timeouts e paths hardcoded em várias classes
- **Nomenclatura inconsistente**: Mistura de português e inglês, nomes pouco descritivos (ex: "nussoNumero")
- **Tratamento de erros genérico**: Muitos catch(Exception) sem tratamento específico
- **Falta de documentação**: Ausência de JavaDoc na maioria das classes

---

## 14. Observações Relevantes

1. **Arquitetura Batch**: Sistema segue padrão Spring Batch com Reader-Processor-Writer, mas o Processor é praticamente vazio

2. **Processamento Assíncrono**: Utiliza threads para formatação de arquivos e leitura de retornos de atualização, mas sem controle adequado de concorrência

3. **Configuração XML**: Toda configuração do job está em XML (job-definitions.xml), incluindo beans do Spring e definições de filas MQ

4. **Workspace Temporário**: Utiliza diretório temporário (retCliente/cobProp/proc/) que é limpo ao final da execução

5. **Exit Codes Customizados**: Define códigos de saída específicos (0=sucesso, 10=erro geral, 11=erro atualização, 12=inconsistência)

6. **Suporte a Múltiplos Layouts**: Processa tanto CNAB 400 quanto CNAB 240 com lógica específica para cada formato

7. **Consolidação Complexa**: Lógica de consolidação de valores e contadores distribuída entre múltiplas classes

8. **Dependências Legadas**: Uso de versões antigas de bibliotecas (Log4j 1.2.8, JSON Simple 1.1.1)

9. **Segurança**: Credenciais de MQ configuradas via Spring, mas sem indicação de criptografia ou vault

10. **Performance**: Processamento em lote de 100 registros para envio de atualizações, mas sem paralelização efetiva