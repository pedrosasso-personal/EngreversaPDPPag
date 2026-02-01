# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **javabatch-ccbd-base-bolsao-inicial** é um processamento batch Java desenvolvido para ler arquivos de movimentação bancária no formato M06, processar os dados e publicar mensagens em filas RabbitMQ. O sistema lê arquivos de um diretório específico, extrai informações de movimentações financeiras (débitos/créditos), converte os dados para o formato JSON e publica em uma fila para processamento posterior. Após o processamento bem-sucedido, os arquivos são movidos para um diretório de processados.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê arquivos do diretório pendente e disponibiliza para processamento |
| **ItemProcessor** | Processa cada arquivo M06, extraindo e validando os detalhes das movimentações |
| **ItemWriter** | Publica as mensagens no RabbitMQ e move arquivos processados para diretório de sucesso |
| **ArquivoM06** | Representa um arquivo M06 com sua lista de detalhes de movimentação |
| **Detalhe** | Representa uma linha de detalhe do arquivo M06 com dados da movimentação |
| **MovimentoPriorizado** | Entidade de domínio que representa o movimento priorizado a ser enviado para a fila |
| **MQService/MQServiceImpl** | Serviço responsável pela comunicação com o RabbitMQ |
| **RabbitRepositoryImpl** | Implementação do repositório para operações com RabbitMQ |
| **LayoutUtil** | Utilitário para parsing do layout posicional do arquivo M06 |
| **FileUtil** | Utilitário para operações com arquivos (validação, movimentação) |
| **MyResumeStrategy** | Estratégia de retomada em caso de erros durante o processamento |

---

## 3. Tecnologias Utilizadas

- **Java** (linguagem de programação)
- **Maven** (gerenciamento de dependências e build)
- **Spring Framework** (injeção de dependências e configuração)
- **BV Framework Batch** (framework proprietário para processamento batch)
- **RabbitMQ** (message broker para filas)
- **Spring AMQP** (integração com RabbitMQ)
- **Gson** (serialização/deserialização JSON)
- **Log4j** (logging)
- **JUnit** (testes unitários)

---

## 4. Principais Endpoints REST

não se aplica

---

## 5. Principais Regras de Negócio

1. **Validação de Arquivos**: Apenas arquivos com extensão `.M06` são processados
2. **Filtro de Linhas**: Apenas linhas que começam com "1" e possuem registro auxiliar vazio são processadas
3. **Parsing Posicional**: Os dados são extraídos de posições fixas no arquivo conforme layout definido
4. **Conversão de Valores**: Valores monetários são divididos por 100 para obter o valor real
5. **Transacionalidade**: Cada arquivo é processado em uma transação, com commit apenas após sucesso total
6. **Movimentação de Arquivos**: Arquivos processados com sucesso são movidos para diretório de processados
7. **Publicação em Fila**: Cada detalhe do arquivo gera uma mensagem individual na fila RabbitMQ
8. **Formato de Data**: Datas são processadas no formato `ddMMyyyy` e convertidas para `yyyy-MM-dd` no JSON

---

## 6. Relação entre Entidades

**ArquivoM06** (1) ---contém---> (N) **Detalhe**
- Um arquivo M06 contém múltiplos detalhes de movimentação

**Detalhe** (1) ---transforma-se em---> (1) **MovimentoPriorizado**
- Cada detalhe do arquivo é convertido em um objeto MovimentoPriorizado para publicação na fila

**Relacionamentos principais:**
- ArquivoM06 mantém referência ao File original e lista de Detalhes
- Detalhe extrai dados do layout posicional do arquivo
- MovimentoPriorizado é construído a partir de um Detalhe

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
| *.M06 | Leitura | ItemReader / ItemProcessor | Arquivos de movimentação bancária no formato posicional |
| robo.log | Gravação | Log4j (RollingFileAppender) | Log de execução do processo |
| statistics-{executionId}.log | Gravação | Log4j (BvDailyRollingFileAppender) | Log de estatísticas do framework batch |
| job-config.properties | Leitura | Resources | Arquivo de configuração com diretórios |
| job-resources.xml | Leitura | Spring Context | Configuração de beans (RabbitMQ, propriedades) |
| job-definitions.xml | Leitura | Spring Context | Definição do job batch |

**Diretórios utilizados:**
- `./recebidos` - Diretório de arquivos pendentes (leitura)
- `./processados/` - Diretório de arquivos processados com sucesso (gravação)

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Exchange | Routing Key | Breve Descrição |
|--------------|-----------|----------|-------------|-----------------|
| events.business.CCBD-BASE.gravarMovimento | RabbitMQ | ex.ccbd.movimento | CCBD-BASE.gravarMovimento | Fila para publicação de movimentos priorizados em formato JSON |

**Configurações por ambiente:**
- **Local/Teste**: localhost:5672, usuário guest
- **DES**: 10.179.172.71:5672, usuário _ccbd_des
- **UAT**: 10.183.100.70:5672, usuário _ccbd_uat
- **PRD**: 10.39.49.197:5672, usuário _ccbd_prd

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| RabbitMQ | Message Broker | Publicação de mensagens de movimentação priorizada para processamento assíncrono |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 6/10

**Justificativa:**

**Pontos Positivos:**
- Separação clara de responsabilidades (Reader, Processor, Writer)
- Uso de padrões de projeto (Repository, Service)
- Configuração externalizada por ambiente
- Tratamento de transações no RabbitMQ
- Uso de utilitários para operações comuns

**Pontos Negativos:**
- Comentários em português misturados com código
- Falta de tratamento adequado de exceções em alguns pontos
- Código de exemplo não utilizado (ExampleOfInputOfWork, ExampleOfOutputOfWork)
- Falta de validações mais robustas nos dados de entrada
- Conversões de tipo com tratamento genérico (retornando null em caso de erro)
- Falta de testes unitários (apenas teste de integração)
- Uso de framework proprietário (BV Framework) que dificulta manutenção
- Logging excessivo em alguns pontos (workflow.info para cada linha)
- Classe Resources com comentários confusos sobre execução local
- Falta de documentação JavaDoc nas classes

---

## 14. Observações Relevantes

1. **Framework Proprietário**: O sistema utiliza o BV Framework Batch, um framework proprietário da BV Sistemas, o que pode dificultar a manutenção por desenvolvedores não familiarizados

2. **Layout Posicional**: O arquivo M06 possui layout posicional fixo documentado no código (LayoutUtil), com campos específicos em posições definidas

3. **Estratégia de Erro**: A classe MyResumeStrategy está configurada para NÃO retomar o processamento em caso de erro (retorna false), causando rollback e finalização

4. **Versionamento**: Projeto na versão 0.1.0, indicando fase inicial de desenvolvimento

5. **Ambientes**: Sistema preparado para 4 ambientes (Local, DES, UAT, PRD) com configurações específicas de RabbitMQ

6. **Processamento Síncrono**: Cada arquivo é processado completamente antes de passar para o próximo

7. **Persistência de Mensagens**: Mensagens são publicadas com propriedade PERSISTENT_TEXT_PLAIN, garantindo durabilidade

8. **Formato de Data no JSON**: Datas são serializadas no formato `yyyy-MM-dd` através da configuração do Gson

9. **Dependências**: Projeto depende de bibliotecas BV específicas (bv-framework-batch, bv-crypto, bv-jdbcdriver) que não estão disponíveis em repositórios públicos