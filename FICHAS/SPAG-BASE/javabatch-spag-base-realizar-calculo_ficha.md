# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **javabatch-spag-base-realizar-calculo** é um job batch Java responsável por iniciar e monitorar o processo de cálculo mensal de rebate. O sistema envia uma mensagem para uma fila MQ solicitando o início do cálculo e aguarda a resposta em outra fila, validando se o processamento foi concluído com sucesso. Trata-se de um orquestrador que dispara o cálculo e aguarda confirmação do resultado.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `ItemReader` | Lê o item a ser processado (cria uma mensagem única indicando que o cálculo deve ser iniciado) |
| `ItemWriter` | Envia mensagem para fila de início de cálculo e aguarda resposta na fila de retorno |
| `MyResumeStrategy` | Estratégia de tratamento de erros do batch, define códigos de saída em caso de exceção |
| `MensagemFila` | Entidade de domínio representando a mensagem enviada para iniciar o cálculo |
| `RetornoCalculoRebate` | Entidade representando a resposta do cálculo (sucesso ou falha) |
| `FilaMQServiceImpl` | Implementação do serviço de integração com filas MQ |
| `MQConnectionProvider` | Provedor de conexão e operações com IBM MQ |
| `ConverterJsonUtils` | Utilitário para conversão de objetos para JSON e vice-versa |
| `UC4CodigoSaida` | Enum com códigos de saída do job (0=sucesso, 10=erro runtime, 20=erro fila, 30=erro apuração) |
| `StatusRetorno` | Enum com status de retorno (SUCESSO/FALHA) |

---

## 3. Tecnologias Utilizadas

- **Java** (linguagem de programação)
- **Maven** (gerenciamento de dependências e build)
- **BV Framework Batch** (framework proprietário para jobs batch)
- **IBM MQ 7.0.1.10** (middleware de mensageria)
- **Spring Framework 2.0** (injeção de dependências e configuração)
- **GSON** (serialização/deserialização JSON)
- **JMS** (Java Message Service para integração com filas)
- **Log4j** (logging)
- **JUnit e Mockito** (testes unitários)

---

## 4. Principais Endpoints REST

Não se aplica. Este é um job batch que não expõe endpoints REST.

---

## 5. Principais Regras de Negócio

1. **Disparo de Cálculo Mensal**: O job cria uma mensagem indicando que o cálculo mensal de rebate deve ser iniciado
2. **Envio para Fila de Processamento**: A mensagem é enviada para a fila `QL.INICIAR_CALCULO_REBATE.INT`
3. **Aguardo de Resposta**: O sistema aguarda até 60 segundos (timeout configurável) por mensagens na fila de retorno `QL.RETORNO_CALCULO_REBATE.INT`
4. **Validação de Sucesso**: O job verifica se pelo menos uma mensagem de retorno possui status "SUCESSO"
5. **Tratamento de Erros**: Em caso de falha na comunicação com filas ou ausência de resposta de sucesso, o job finaliza com código de erro específico (20 para erro de fila, 30 para erro de apuração)

---

## 6. Relação entre Entidades

**Entidades principais:**

- **MensagemFila**: Entidade simples com atributo booleano `deveCalcular` que indica se o cálculo deve ser executado
- **RetornoCalculoRebate**: Contém o atributo `statusRetorno` do tipo `StatusRetorno` (enum)
- **StatusRetorno**: Enum com valores SUCESSO ou FALHA
- **UC4CodigoSaida**: Enum com códigos de saída do job

**Relacionamentos:**
- `MensagemFila` é construída via `MensagemFilaBuilder` (padrão Builder)
- `RetornoCalculoRebate` contém um `StatusRetorno`
- Não há relacionamentos complexos entre entidades, pois são DTOs simples para comunicação via fila

---

## 7. Estruturas de Banco de Dados Lidas

Não se aplica. O sistema não realiza leitura direta em banco de dados.

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema não realiza operações de escrita em banco de dados.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `catalogo-filas.xml` | Leitura | Configuração do framework MQ | Catálogo de filas MQ utilizadas pelo sistema |
| `bv-framework-integration-mq-conf.properties` | Leitura | Configuração do framework MQ | Propriedades de configuração da integração MQ |
| `job-resources.xml` | Leitura | Spring Context | Configuração de recursos do job (conexão MQ, credenciais, filas) |
| `job-definitions.xml` | Leitura | Spring Context | Definição do job batch e seus componentes |
| `log4j.xml` / `log4j.properties` | Leitura | Log4j | Configuração de logging |
| `log/robo.log` | Gravação | Log4j RollingFileAppender | Log de execução do job |
| `log/statistics-${executionId}.log` | Gravação | BvDailyRollingFileAppender | Log de estatísticas do framework batch |

---

## 10. Filas Lidas

| Nome da Fila | Tipo | Descrição |
|--------------|------|-----------|
| `QL.RETORNO_CALCULO_REBATE.INT` | IBM MQ Queue | Fila de retorno contendo o resultado do processamento de cálculo de rebate |

---

## 11. Filas Geradas

| Nome da Fila | Tipo | Descrição |
|--------------|------|-----------|
| `QL.INICIAR_CALCULO_REBATE.INT` | IBM MQ Queue | Fila para envio de solicitação de início do cálculo mensal de rebate |

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **IBM MQ (QM.ATA.01)** | Middleware de Mensageria | Queue Manager para comunicação assíncrona. Conexão via canal `SPAG.SRVCONN` na porta 1414 do host `qm_ata_des.bvnet.bv` |
| **Sistema de Cálculo de Rebate** | Sistema Interno | Sistema que consome mensagens da fila `QL.INICIAR_CALCULO_REBATE.INT` e publica resultados em `QL.RETORNO_CALCULO_REBATE.INT` |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 6/10

**Justificativa:**

**Pontos Positivos:**
- Uso de padrões como Builder para construção de objetos
- Separação de responsabilidades em camadas (batch, service, domain, mq)
- Tratamento de exceções com códigos de erro específicos
- Uso de framework batch estruturado
- Presença de testes unitários

**Pontos Negativos:**
- **Credenciais hardcoded**: Usuário e senha do MQ expostos em arquivos de configuração (`_spag_des` / `Swi59blp`)
- **Comentários em português com caracteres especiais mal codificados**: Diversos comentários apresentam problemas de encoding (ex: "pr�ximo", "transa��o", "Apura��o")
- **Lógica de negócio no Writer**: O `ItemWriter` contém lógica complexa que poderia estar em uma camada de serviço
- **Timeout fixo**: O timeout de 60 segundos está configurado de forma rígida
- **Falta de validações**: Não há validação robusta dos dados recebidos das filas
- **Logs misturados**: Logs de negócio e técnicos não estão bem separados
- **Código de teste incompleto**: O teste de integração não possui asserções, apenas executa o job

---

## 14. Observações Relevantes

1. **Ambiente**: As configurações apontam para ambiente de desenvolvimento (`qm_ata_des.bvnet.bv`, usuário `_spag_des`)
2. **Segurança**: É crítico remover as credenciais hardcoded e utilizar mecanismos seguros de gestão de secrets
3. **Timeout**: O sistema aguarda até 60 segundos por resposta. Se o cálculo demorar mais, o job falhará
4. **Processamento Único**: O `ItemReader` cria apenas um item para processamento, indicando que o job executa uma única operação por execução
5. **Framework Proprietário**: O sistema utiliza o BV Framework Batch, que é um framework proprietário da organização
6. **Versionamento**: Versão atual do componente é 0.1.0, indicando estar em fase inicial de desenvolvimento
7. **Encoding**: Recomenda-se revisar todos os arquivos para corrigir problemas de codificação de caracteres especiais