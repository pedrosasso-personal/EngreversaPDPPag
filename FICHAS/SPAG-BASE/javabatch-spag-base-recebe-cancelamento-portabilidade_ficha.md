# Ficha Técnica do Sistema

---

## 1. Descrição Geral

O sistema **javabatch-spag-base-recebe-cancelamento-portabilidade** é um job batch Java desenvolvido para processar arquivos XML de retorno de cancelamento de portabilidade de conta salário, oriundos da CIP (Câmara Interbancária de Pagamentos). 

O sistema lê arquivos XML no padrão APCS105 (retorno ou erro), processa as informações de portabilidades canceladas (aceitas ou recusadas), e publica mensagens em filas RabbitMQ para notificar outros sistemas sobre o resultado do processamento. Após o processamento bem-sucedido, os arquivos são movidos para diretórios específicos (processados ou erro).

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê arquivos XML (APCS105_RET ou APCS105_ERR) do diretório de recebimento, faz o parse e extrai as portabilidades. Move os arquivos para diretórios de processados ou erro ao final. |
| **ItemProcessor** | Processa cada portabilidade lida, criando um objeto `PortabilidadeArquivo` contendo a portabilidade e o grupo de cancelamento. |
| **ItemWriter** | Envia as portabilidades processadas para filas RabbitMQ, diferenciando entre portabilidades canceladas com sucesso e aquelas com erro. |
| **CancelamentoRepository** | Responsável por publicar mensagens nas filas RabbitMQ (`SPAG.retornoCancelamentoPortabilidade` e `SPAG.retornoCancelamentoArqPortabilidade`). |
| **APCS105Ret** | Faz o parse de arquivos XML de retorno (APCS105_RET), extraindo cabeçalho e portabilidades aceitas ou recusadas. |
| **APCS105Err** | Faz o parse de arquivos XML de erro (APCS105_ERR), extraindo informações de erro do arquivo. |
| **CancelamentoMapper** | Mapeia objetos de domínio entre as diferentes representações (Portabilidade, ControleArquivo, DTOs). |
| **EstruturaArquivoFactory** | Factory para criação de objetos `Document` (DOM) a partir de InputStreams XML, com configurações de segurança. |
| **MyResumeStrategy** | Estratégia de retomada do job batch (atualmente não permite retomada). |
| **Portabilidade** | Entidade de domínio representando uma portabilidade de conta salário. |
| **ControleArquivo** | Entidade representando informações de controle do arquivo processado. |

---

## 3. Tecnologias Utilizadas

- **Java** (linguagem de programação)
- **Maven** (gerenciamento de dependências e build)
- **Framework BV Batch** (framework proprietário para jobs batch - `br.com.bvsistemas.framework.batch`)
- **Spring Framework** (injeção de dependências, configuração XML)
- **RabbitMQ / Spring AMQP** (mensageria)
- **Jackson** (serialização/deserialização JSON)
- **Apache Commons IO** (manipulação de arquivos)
- **Log4j** (logging)
- **JUnit / Mockito** (testes unitários)
- **XML DOM Parser** (parse de arquivos XML)

---

## 4. Principais Endpoints REST

**Não se aplica.** Este é um job batch que não expõe endpoints REST.

---

## 5. Principais Regras de Negócio

1. **Processamento de Arquivos APCS105**: O sistema processa arquivos XML no formato APCS105_RET (retorno de cancelamento) ou APCS105_ERR (erro no arquivo).

2. **Diferenciação de Portabilidades Aceitas e Recusadas**: Arquivos de retorno podem conter portabilidades com cancelamento aceito (`Grupo_APCS105RET_CanceltPortddCtSalrActo`) ou recusado (`Grupo_APCS105RET_CanceltPortddCtSalrRecsd`).

3. **Tratamento de Erros em Arquivos**: Arquivos com erro (APCS105_ERR) são processados separadamente, extraindo o código de erro associado.

4. **Publicação em Filas Distintas**: 
   - Portabilidades canceladas com sucesso são enviadas para a fila `SPAG.retornoCancelamentoPortabilidade`.
   - Portabilidades com erro são enviadas para a fila `SPAG.retornoCancelamentoArqPortabilidade`.

5. **Movimentação de Arquivos**: Após processamento bem-sucedido (exit code 0), arquivos são movidos para o diretório "processados". Em caso de erro, são movidos para o diretório "erro".

6. **Validação de ISPB**: O sistema valida ISPBs do emissor (Votorantim: 59588111) e destinatário (CIP: 02992335).

7. **Controle de Arquivo**: Cada portabilidade processada mantém informações de controle do arquivo de origem (nome, data de envio/recebimento, número de controle).

---

## 6. Relação entre Entidades

**Principais Entidades e Relacionamentos:**

- **Portabilidade**: Entidade central representando uma solicitação de cancelamento de portabilidade.
  - Contém: `identdPartAdmtd`, `numCtrlPart`, `nuPortddPCS`, `cancelamentoRecusado`, `dtCanceltPortddCtSalr`, `codeErro`
  - Relaciona-se com `ControleArquivo` (1:1) - informações do arquivo de origem
  - Relaciona-se com `CabecalhoArquivoRet` (N:1) - cabeçalho do arquivo de retorno

- **ControleArquivo**: Informações de controle do arquivo processado.
  - Contém: `nmArquivo`, `dtEnvioCip`, `nuCtrlEmis`, `dtRecebimentoCip`

- **PortabilidadeArquivo**: Wrapper que agrupa `Portabilidade` e `GrupoCancelamentoPortabilidade` para processamento.

- **GrupoCancelamentoPortabilidade**: Dados específicos do grupo de cancelamento no arquivo XML.

- **DominioPortabilidadeDTO**: DTO para publicação na fila de portabilidades canceladas.
  - Contém `PortabilidadeRet`

- **DominioArquivo**: DTO para publicação na fila de erros de arquivo.
  - Contém `ControleArquivo`, código de erro e situação

---

## 7. Estruturas de Banco de Dados Lidas

**Não se aplica.** O sistema não realiza leitura direta de banco de dados. Toda informação é obtida de arquivos XML e filas RabbitMQ.

---

## 8. Estruturas de Banco de Dados Atualizadas

**Não se aplica.** O sistema não realiza operações de escrita em banco de dados. As saídas são publicadas em filas RabbitMQ.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| APCS105_RET.xml | Leitura | `ItemReader` / diretório `arquivo/recebido/` | Arquivo XML de retorno de cancelamento de portabilidade, contendo portabilidades aceitas ou recusadas |
| APCS105_ERR.xml | Leitura | `ItemReader` / diretório `arquivo/recebido/` | Arquivo XML de erro no processamento do arquivo de cancelamento |
| APCS105_*.xml (processados) | Gravação (movimentação) | `ItemReader.handleDispose()` / diretório `arquivo/processados/` | Arquivos processados com sucesso são movidos para este diretório |
| APCS105_*.xml (erro) | Gravação (movimentação) | `ItemReader.handleDispose()` / diretório `arquivo/erro/` | Arquivos com erro no processamento são movidos para este diretório |
| robo.log | Gravação | Log4j / diretório `log/` | Arquivo de log da aplicação |
| statistics-*.log | Gravação | Log4j / diretório `log/` | Arquivo de estatísticas do framework batch |

---

## 10. Filas Lidas

| Nome da Fila | Tecnologia | Classe Responsável | Breve Descrição |
|--------------|-----------|-------------------|-----------------|
| events.business.SPAG-BASE.cancelamento.portabilidade.cip | RabbitMQ | `PortabilidadeInterator` | Fila de onde o sistema poderia consumir mensagens de portabilidade (código presente mas não utilizado no fluxo principal do batch) |

**Observação:** O código da classe `PortabilidadeInterator` sugere consumo de fila, mas o fluxo principal do batch utiliza leitura de arquivos XML via `ItemReader`. A fila mencionada não é efetivamente consumida no fluxo documentado.

---

## 11. Filas Geradas

| Nome da Fila/Routing Key | Tecnologia | Exchange | Classe Responsável | Breve Descrição |
|--------------------------|-----------|----------|-------------------|-----------------|
| SPAG.retornoCancelamentoPortabilidade | RabbitMQ | events.business.portabilidade | `CancelamentoRepository.sendPortabilidadeCancelada()` | Fila para publicação de portabilidades canceladas com sucesso (aceitas ou recusadas pelo CIP) |
| SPAG.retornoCancelamentoArqPortabilidade | RabbitMQ | events.business.portabilidade | `CancelamentoRepository.sendPortabilidadeCancelErroArquivo()` | Fila para publicação de portabilidades com erro no arquivo |

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **CIP (Câmara Interbancária de Pagamentos)** | Arquivo XML | Recebe arquivos XML de retorno de cancelamento de portabilidade no padrão APCS105 |
| **RabbitMQ** | Mensageria | Publica mensagens de resultado do processamento para consumo por outros sistemas do SPAG |
| **Sistema SPAG (downstream)** | Fila RabbitMQ | Consome as mensagens publicadas nas filas de retorno de cancelamento |

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Estrutura bem organizada seguindo padrão batch (Reader/Processor/Writer)
- Uso adequado de DTOs e separação de responsabilidades
- Configuração externalizada por ambiente (DES/UAT/PRD)
- Tratamento de exceções customizado com códigos de erro
- Presença de testes unitários
- Uso de factory pattern para criação de documentos XML com configurações de segurança

**Pontos Negativos:**
- Código com comentários em português misturados com código em inglês (falta de padronização)
- Caracteres especiais mal codificados em strings (ex: "N�o foi possivel")
- Classe `PortabilidadeInterator` presente mas não utilizada no fluxo principal (código morto)
- Falta de documentação JavaDoc nas classes principais
- Testes unitários comentados em `ItemReaderTest` (cobertura incompleta)
- Uso de `System.out` em alguns logs ao invés de logger consistente
- Configurações de segurança XML poderiam estar centralizadas
- Falta de validação mais robusta dos dados de entrada
- Alguns métodos muito longos (ex: `getPortabilidades` em APCS105Ret)
- Tratamento de erro genérico em alguns pontos poderia ser mais específico

---

## 14. Observações Relevantes

1. **Ambientes Configurados**: O sistema possui configurações específicas para três ambientes (DES, UAT, PRD) com credenciais e hosts RabbitMQ distintos.

2. **Framework Proprietário**: Utiliza framework batch proprietário da BV Sistemas (`bv-framework-batch`), o que pode dificultar manutenção por equipes externas.

3. **Padrão APCS105**: O sistema implementa o padrão APCS105 da CIP para cancelamento de portabilidade de conta salário, incluindo validação de XSD.

4. **Segurança XML**: Implementa proteções contra XXE (XML External Entity) e outras vulnerabilidades XML através de configurações no `DocumentBuilderFactory`.

5. **Parâmetro de Execução**: O job recebe como parâmetro obrigatório o nome do arquivo a ser processado (`nomeArquivo`).

6. **Exit Codes Customizados**: Define códigos de saída específicos (10-17) para diferentes tipos de erro, facilitando troubleshooting.

7. **Encoding**: Há preocupação com encoding UTF-16BE em algumas partes do código, sugerindo integração com sistemas legados.

8. **Versionamento**: Versão atual do sistema é 0.4.0, indicando que ainda está em fase de evolução.

9. **Dependências**: Utiliza versões específicas de bibliotecas (Jackson 2.9.10, Spring AMQP) que podem estar desatualizadas.

10. **Scripts de Execução**: Fornece scripts tanto para Windows (.bat) quanto Linux (.sh) para execução do batch.