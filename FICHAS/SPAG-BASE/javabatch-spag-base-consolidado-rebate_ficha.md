# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **javabatch-spag-base-consolidado-rebate** é um job batch Java desenvolvido para processar consolidação de rebates. Ele funciona enviando mensagens para uma fila IBM MQ solicitando a geração de consolidados de rebate para um período específico, aguardando o processamento e validando o retorno através de outra fila. O batch utiliza o framework BV Sistemas para gerenciamento de jobs e integração com filas MQ.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê os parâmetros de entrada (datas inicial/final e CNPJs), valida e prepara a mensagem para processamento |
| **ItemWriter** | Envia mensagem para fila de envio, aguarda resposta na fila de retorno e valida o status do processamento |
| **MyResumeStrategy** | Estratégia de tratamento de erros e definição de códigos de saída do job |
| **MensagemFila** | Entidade que representa a mensagem enviada para fila (contém flag deveGerar e datas) |
| **RetornoConsolidadoRebate** | Entidade que representa o retorno do processamento (status e detalhe) |
| **ParametrosExecucao** | Valida e armazena os parâmetros de execução do job |
| **FilaMQServiceImpl** | Implementação do serviço de integração com filas IBM MQ |
| **MQConnectionProvider** | Gerencia conexões, sessões e operações com IBM MQ |
| **ConverterJsonUtils** | Utilitário para conversão de objetos para JSON e vice-versa |
| **ParseDateUtils** | Utilitário para conversão e formatação de datas |
| **ExtracaoPalavras** | Utilitário para extração de CNPJs a partir de string delimitada |

---

## 3. Tecnologias Utilizadas

- **Java** (linguagem de programação)
- **Maven** (gerenciamento de dependências e build)
- **Spring Framework 2.0** (injeção de dependências e configuração)
- **BV Framework Batch** (framework proprietário para jobs batch)
- **IBM MQ 7.0.1.10** (middleware de mensageria)
- **JMS** (Java Message Service para integração com filas)
- **Gson** (serialização/deserialização JSON)
- **Log4j** (logging)
- **JUnit e Mockito** (testes unitários)
- **Apache Commons Lang** (utilitários)

---

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch que não expõe endpoints REST.

---

## 5. Principais Regras de Negócio

1. **Validação de Parâmetros**: O job valida que a data inicial não pode ser posterior à data final
2. **Datas Padrão**: Se não informadas, utiliza o dia anterior à execução como data inicial e final
3. **Validação de Ano**: Datas devem ter ano igual ou superior a 1990
4. **Tentativas de Leitura**: O sistema realiza até 5 tentativas para obter resposta da fila de retorno, com intervalo de 10 segundos entre tentativas
5. **Timeout de Resposta**: Aguarda até 60 segundos (configurável) por mensagem na fila de retorno
6. **Validação de Sucesso**: O processamento só é considerado bem-sucedido se o retorno contiver status "SUCESSO"
7. **Processamento de CNPJs**: Aceita lista de CNPJs delimitados por 'v' (ex: v78537397000142v59588111000104v)
8. **Aguardo entre Operações**: Aguarda 10 segundos entre o envio da mensagem e a primeira tentativa de leitura da resposta

---

## 6. Relação entre Entidades

**MensagemFila** (enviada para fila):
- deveGerar: boolean
- dataInicial: String (formato yyyyMMdd)
- dataFinal: String (formato yyyyMMdd)

**RetornoConsolidadoRebate** (recebida da fila):
- statusRetorno: StatusRetorno (enum: SUCESSO, FALHA, PARCIAL)
- detalhe: String

**ParametrosExecucao** (parâmetros do job):
- sDataInicial, sDataFinal: String
- sCnpjs: String
- dDataInicial, dDataFinal: Date
- lCnpjs: List<String>

**Enums**:
- **StatusRetorno**: SUCESSO, FALHA, PARCIAL
- **UC4CodigoSaida**: SUCESSO(0), ERRO_RUNTIME(10), ERRO_FILA(20), ERRO_APURACAO(30), ERRO_PARAMETRO(40)
- **MascaraData**: DDMMAAAA, AAAAMMDD, DD_MM_AAAA

---

## 7. Estruturas de Banco de Dados Lidas

Não se aplica. O sistema não realiza leitura direta em banco de dados.

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema não realiza operações diretas em banco de dados.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| catalogo-filas.xml | Leitura | Configuração Spring (job-resources.xml) | Catálogo de definição das filas MQ utilizadas |
| bv-framework-integration-mq-conf.properties | Leitura | Configuração Spring | Propriedades de configuração do framework de integração MQ |
| job-resources.xml | Leitura | Configuração Spring | Recursos do job (conexão MQ, credenciais, filas) |
| job-definitions.xml | Leitura | Configuração Spring | Definições do job batch (reader, writer, estratégias) |
| log4j.xml / log4j.properties | Leitura | Log4j | Configuração de logging |
| robo.log | Gravação | Log4j (RollingFileAppender) | Logs de execução do job |
| statistics-{executionId}.log | Gravação | BvDailyRollingFileAppender | Logs de estatísticas do framework BV |
| *.tlog | Gravação/Leitura | Bitronix (gerenciador transacional) | Arquivos de log transacional (removidos ao final) |

---

## 10. Filas Lidas

| Nome da Fila | Tipo | Descrição |
|--------------|------|-----------|
| QL.RETORNO_CONSOLIDADO_REBATE.INT | IBM MQ Queue | Fila de retorno contendo o resultado do processamento de consolidação de rebate |

**Configuração**:
- Queue Manager: QM.ATA.01
- Host: qm_ata_des.bvnet.bv
- Channel: SPAG.SRVCONN
- Port: 1414
- User: _spag_des
- Timeout: 60000ms

---

## 11. Filas Geradas

| Nome da Fila | Tipo | Descrição |
|--------------|------|-----------|
| QL.ENVIO_CONSOLIDADO_REBATE.INT | IBM MQ Queue | Fila de envio contendo a solicitação de geração do consolidado de rebate com período especificado |

**Configuração**:
- Queue Manager: QM.ATA.01
- Host: qm_ata_des.bvnet.bv
- Channel: SPAG.SRVCONN
- Port: 1414
- User: _spag_des

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| IBM MQ (QM.ATA.01) | Middleware de Mensageria | Sistema de filas para comunicação assíncrona. O batch envia solicitações e aguarda respostas através de filas específicas |
| Sistema Processador de Rebate | Sistema Externo (via MQ) | Sistema não identificado que consome mensagens da fila QL.ENVIO_CONSOLIDADO_REBATE.INT e retorna o resultado em QL.RETORNO_CONSOLIDADO_REBATE.INT |

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Uso adequado de padrões como Builder (MensagemFilaBuilder)
- Separação de responsabilidades entre camadas (batch, service, domain, utils)
- Tratamento de exceções customizado com códigos de erro específicos
- Presença de testes unitários
- Uso de enums para constantes e status
- Logging adequado em pontos críticos

**Pontos Negativos:**
- **Hardcoded sleeps**: Uso de `TimeUnit.SECONDS.sleep(10)` prejudica testabilidade e performance
- **Lógica de retry manual**: Implementação de tentativas com loop poderia usar bibliotecas especializadas
- **Configurações hardcoded**: Credenciais e configurações de ambiente em arquivos XML (job-resources.xml)
- **Comentários em português com caracteres especiais**: Problemas de encoding (�) indicam falta de padronização
- **Falta de constantes**: Números mágicos como 5 (tentativas), 10 (segundos) deveriam ser constantes configuráveis
- **Acoplamento com framework proprietário**: Dependência forte do BV Framework dificulta portabilidade
- **Falta de documentação JavaDoc**: Classes e métodos sem documentação adequada
- **Tratamento de transação inconsistente**: Comentários indicam controle transacional mas implementação não está clara
- **Código legado**: Uso de Spring 2.0 e padrões antigos

---

## 14. Observações Relevantes

1. **Ambiente**: As configurações apontam para ambiente de desenvolvimento (qm_ata_des.bvnet.bv, usuário _spag_des)

2. **Segurança**: Credenciais expostas em arquivos de configuração (password: "Swi59blp") - recomenda-se uso de vault ou variáveis de ambiente

3. **Versionamento**: Projeto na versão 0.4.0, indicando ainda em fase de desenvolvimento/estabilização

4. **Execução**: O job pode ser executado via linha de comando (.bat para Windows, .sh para Linux) com parâmetros:
   - Nome do robô
   - Execution ID
   - Data início (formato yyyyMMdd)
   - Data fim (formato yyyyMMdd)
   - CNPJs (opcional, delimitado por 'v')

5. **Códigos de Saída**:
   - 0: Sucesso
   - 10: Erro de Runtime
   - 20: Erro ao interagir com fila
   - 30: Erro ao realizar apuração
   - 40: Erro de parâmetro

6. **Limitações de Memória**: JVM configurada com -Xms512M -Xmx512M

7. **Framework Proprietário**: Forte dependência do BV Framework (bv-sistemas), o que pode dificultar manutenção e migração futura

8. **Processamento Síncrono**: Apesar de usar filas, o processamento é síncrono (aguarda resposta), o que pode gerar timeouts em processamentos longos