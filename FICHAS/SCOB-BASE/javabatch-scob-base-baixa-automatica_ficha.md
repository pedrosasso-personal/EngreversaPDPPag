# Ficha Técnica do Sistema

---

## 1. Descrição Geral

Sistema batch Java responsável por executar o processo de **Baixa Automática** no contexto de cobrança (SCOB). O sistema orquestra um fluxo de processamento assíncrono utilizando filas IBM MQ, onde:

1. Registra o início do processamento
2. Consulta a quantidade de registros a serem processados
3. Dispara o processamento de baixa automática
4. Aguarda notificações de conclusão via filas
5. Implementa mecanismo de retry configurável (até 3 tentativas)
6. Registra o fim do processamento e atualiza data final em caso de sucesso

O sistema não processa dados diretamente, mas atua como **orquestrador** enviando comandos e aguardando respostas através de filas MQ.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Implementa leitura mínima (executa apenas uma vez) para iniciar o fluxo batch |
| **ItemProcessor** | Processador passthrough - não realiza transformações |
| **ItemWriter** | Classe principal que orquestra todo o fluxo de baixa automática via filas MQ |
| **MQConnectionProvider** | Gerencia conexões, sessões e operações com filas IBM MQ |
| **MQClientResources** | Encapsula configurações de filas (nome, usuário, senha) |
| **NotificaoFimProcessamentoEntrada** | Representa notificação de conclusão do processamento recebida via fila |
| **LogProcessamento** | Armazena estatísticas de processamento (total, sucesso, erro, tentativa) |
| **ConsultaQtdDadosBaixa** | Representa resposta com quantidade de dados a processar |
| **Propriedades** | Gerencia propriedades de configuração do sistema |
| **Resources** | Carrega arquivo de propriedades (job-config.properties) |
| **JsonUtil** | Utilitário para conversão de texto para JSON |
| **MyResumeStrategy** | Estratégia de retomada (atualmente desabilitada) |

---

## 3. Tecnologias Utilizadas

- **Java 6** (maven.compiler.target/source = 1.6)
- **Maven** (gerenciamento de dependências e build)
- **BV Framework Batch** (framework proprietário para jobs batch)
- **IBM MQ (WebSphere MQ)** - versão 9.x (filas JMS)
- **Spring Framework 2.0** (injeção de dependências e configuração)
- **JSON Simple 1.1.1** (manipulação de JSON)
- **Log4j** (logging)
- **JUnit** (testes)
- **BV Crypto Core** (criptografia)
- **BV JDBC Driver** (acesso a banco de dados)

---

## 4. Principais Endpoints REST

**não se aplica** - Sistema batch sem endpoints REST.

---

## 5. Principais Regras de Negócio

1. **Orquestração de Baixa Automática**: Sistema coordena processo de baixa através de múltiplas filas MQ
2. **Mecanismo de Retry**: Até 3 tentativas configuráveis para reprocessamento em caso de falha
3. **Validação de Quantidade**: Consulta quantidade de registros antes de iniciar processamento
4. **Controle de Timeout**: Timeout de 1 hora (3600000ms) para aguardar mensagens nas filas
5. **Controle de Falhas Críticas**: Identifica falhas críticas (código COD002) que impedem continuidade
6. **Sincronização de Mensagens**: Aguarda recebimento de todas as notificações antes de prosseguir
7. **Limpeza de Filas**: Limpa filas de resposta antes de iniciar novo processamento
8. **Exit Codes**: 
   - Exit code 0 = sucesso total
   - Exit code 10 = processamento com erros
9. **Atualização de Data Final**: Só atualiza data final se processamento for 100% bem-sucedido
10. **Logging Detalhado**: Registra estatísticas por tentativa (total, sucesso, erro)

---

## 6. Relação entre Entidades

**Entidades de Domínio:**

- **LogProcessamento**: Entidade independente para estatísticas
  - Atributos: qtdMsgEnviada, qtdMsgComErro, qtdMsgSucesso, reprocessamento

- **NotificaoFimProcessamentoEntrada**: Entidade de notificação
  - Atributos: sucesso (boolean)
  - Relacionamento: Lista mantida em ItemWriter

- **ConsultaQtdDadosBaixa**: Entidade de consulta
  - Atributos: qtdDadosBaixa (int)

**Entidades de Infraestrutura:**

- **MQClientResources**: Configuração de fila
  - Atributos: queueName, user, password

- **MQConnectionProvider**: Gerenciador de conexão
  - Relacionamento: Usa MQClientResources e MQConnectionFactory

---

## 7. Estruturas de Banco de Dados Lidas

**não se aplica** - O sistema não acessa diretamente banco de dados. Toda comunicação é feita via filas MQ, e os serviços consumidores das filas é que realizam operações de banco.

---

## 8. Estruturas de Banco de Dados Atualizadas

**não se aplica** - O sistema não atualiza diretamente banco de dados. As atualizações são realizadas pelos serviços que consomem as mensagens enviadas às filas.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| job-config.properties | Leitura | Resources / Propriedades | Arquivo de configuração com quantidade de reprocessamentos |
| log/robo.log | Gravação | Log4j (RollingFileAppender) | Log principal da aplicação (max 2MB, 5 backups) |
| log/statistics-${executionId}.log | Gravação | Log4j (BvDailyRollingFileAppender) | Log de estatísticas do framework BV |

---

## 10. Filas Lidas

| Nome da Fila | Tipo | Descrição |
|--------------|------|-----------|
| QL.SCOB.BATCH_BAIXA_CONSULTA_QTD_REGISTROS.RSP | IBM MQ | Recebe resposta com quantidade de registros a processar |
| QL.SCOB.BATCH_BAIXA_FIM_BAIXA_AUTOMATICA.RSP | IBM MQ | Recebe notificações de conclusão do processamento de baixa |

---

## 11. Filas Geradas

| Nome da Fila | Tipo | Descrição |
|--------------|------|-----------|
| QL.SCOB.BATCH_BAIXA_REGISTRA_INICIO_PROCESSO.INT | IBM MQ | Notifica início do processo de baixa |
| QL.SCOB.BATCH_BAIXA_REGISTRA_FIM_PROCESSO.INT | IBM MQ | Notifica fim do processo de baixa |
| QL.SCOB.BATCH_BAIXA_CONSULTA_QTD_REGISTROS.INT | IBM MQ | Solicita quantidade de registros a processar |
| QL.SCOB.BATCH_BAIXA_INICIA_BAIXA_AUTOMATICA.INT | IBM MQ | Dispara processamento de baixa automática |
| QL.SCOB.BATCH_BAIXA_ATUALIZA_DATA_FIM.IN | IBM MQ | Solicita atualização da data final de processamento |

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| IBM MQ (WebSphere MQ) | Middleware de Mensageria | Todas as integrações são realizadas via filas MQ. O sistema não conhece os consumidores finais, apenas envia comandos e aguarda respostas. |
| Serviços SCOB (não identificados) | Consumidores de Filas | Serviços que processam as mensagens enviadas às filas e executam operações de baixa, consultas e atualizações no banco de dados. |

---

## 13. Avaliação da Qualidade do Código

**Nota: 4/10**

**Justificativa:**

**Pontos Negativos:**
- **Nomenclatura inconsistente**: "Notificao" ao invés de "Notificacao" (erro de digitação em nome de classe)
- **Classe ItemWriter com responsabilidades excessivas**: Viola princípio de responsabilidade única (SRP) - orquestra todo o fluxo, gerencia filas, controla retry, logging
- **Lógica complexa concentrada**: Método `init()` com múltiplos níveis de aninhamento e lógica difícil de testar
- **Tratamento de exceções genérico**: Catch de `Exception` sem tratamento específico
- **Código comentado**: Presença de código comentado no XML de configuração
- **Falta de constantes**: Strings hardcoded ("consultaDadosBaixa", "COD002", etc.)
- **Timeout fixo**: Valor de timeout hardcoded (3600000L) deveria ser configurável
- **Uso de tecnologias antigas**: Java 6, Spring 2.0 (descontinuados e sem suporte)
- **Falta de testes unitários**: Apenas teste de integração presente
- **Logging excessivo**: Muitos logs de workflow que poluem a saída

**Pontos Positivos:**
- **Separação em módulos Maven**: Estrutura core/dist bem definida
- **Uso de framework batch**: Aproveita framework proprietário BV
- **Mecanismo de retry**: Implementado de forma funcional
- **Logging de estatísticas**: Bom controle de métricas por tentativa
- **Configuração externalizada**: Uso de properties e Spring XML

---

## 14. Observações Relevantes

1. **Sistema Legado**: Utiliza Java 6 e Spring 2.0, tecnologias descontinuadas que representam risco de segurança e manutenibilidade

2. **Arquitetura Event-Driven**: Sistema totalmente baseado em mensageria assíncrona, sem acesso direto a banco de dados

3. **Dependência do Framework BV**: Forte acoplamento com framework proprietário (bv-framework-batch), dificultando portabilidade

4. **Configuração Híbrida**: Mistura configuração em properties, XML Spring e código Java

5. **Ausência de Documentação**: Código sem JavaDoc ou comentários explicativos

6. **Potencial Deadlock**: Sistema aguarda mensagens com timeout, mas não há garantia de ordem ou recebimento

7. **Falta de Monitoramento**: Não há integração com ferramentas de APM ou métricas modernas

8. **Segurança**: Credenciais de MQ configuradas em XML (mesmo que em variáveis, expõe estrutura)

9. **Escalabilidade Limitada**: Processamento sequencial, não aproveita paralelismo

10. **Necessidade de Modernização**: Sistema candidato a refatoração para Spring Boot, Java 11+, e padrões modernos de mensageria

---