# Ficha Técnica do Sistema

---

## 1. Descrição Geral

Sistema batch Java responsável por consultar transações de débito de ISS (Imposto Sobre Serviços) no banco de dados DBCONTACORRENTE e publicar essas informações em uma fila RabbitMQ para processamento posterior. O batch busca transações dos últimos 3 dias, filtra por critérios específicos de transação e liquidação, e envia os dados em formato JSON para consumo por outros sistemas.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê transações de débito do banco de dados através do TransacaoRepository e disponibiliza para processamento em lote |
| **ItemProcessor** | Processa cada transação individualmente (atualmente apenas repassa o objeto sem transformações) |
| **ItemWriter** | Converte transações em JSON e publica na fila RabbitMQ |
| **TransacaoDebito** | Entidade de domínio representando uma transação de débito com dados bancários |
| **TransacaoRepository / TransacaoRepositoryImpl** | Repositório responsável pela consulta de transações no banco de dados |
| **TransacaoDebitoMapper** | Mapper que converte ResultSet do banco em objetos TransacaoDebito |
| **MyResumeStrategy** | Estratégia de retomada do batch em caso de falha (atualmente não permite retomada) |
| **Query** | Classe utilitária contendo as queries SQL utilizadas no sistema |
| **ConstantsUtils** | Constantes do sistema, incluindo códigos de erro |
| **DateUtils** | Utilitários para manipulação e formatação de datas |
| **TransacaoDebitoException** | Exceção customizada para erros relacionados a transações de débito |

---

## 3. Tecnologias Utilizadas

- **Java 1.6**
- **Maven 3.3+** - Gerenciamento de dependências e build
- **Spring Framework** - Injeção de dependências e configuração
- **Spring AMQP / RabbitMQ** - Mensageria para publicação de eventos
- **BV Framework Batch** - Framework proprietário para processamento batch
- **Bitronix** - Gerenciador de transações JTA
- **Sybase jConnect (jconn4)** - Driver JDBC para conexão com banco Sybase
- **Jackson** - Serialização/deserialização JSON
- **Log4j** - Logging
- **JUnit / Mockito** - Testes unitários
- **Apache POI** - Manipulação de arquivos (dependência presente)

---

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch sem endpoints REST.

---

## 5. Principais Regras de Negócio

1. **Filtro Temporal**: Busca transações com data de efetivação igual a 3 dias antes da data de execução do batch
2. **Filtro de Transações**: Exclui transações com códigos específicos (5284, 5530, 5531, 5210, 5211)
3. **Filtro de Liquidação**: Considera apenas transações com código de liquidação 61 ou 62
4. **Processamento em Lote**: Processa transações em chunks de 10.000 registros (commitInterval)
5. **Publicação Assíncrona**: Cada transação válida é convertida em JSON e publicada individualmente na fila RabbitMQ
6. **Tratamento de Erros**: Em caso de erro na busca ou publicação, o batch é interrompido com código de saída específico
7. **Isolamento de Leitura**: Utiliza isolation level 0 (READ UNCOMMITTED) na consulta ao banco

---

## 6. Relação entre Entidades

**TransacaoDebito** (Entidade Principal):
- `cdBanco` (Integer): Código do banco
- `nuContaCorrente` (Long): Número da conta corrente
- `cdTipoConta` (Integer): Código do tipo de conta
- `cdProtocolo` (String): Código do protocolo/documento
- `dtLancamentoContabil` (Date): Data de lançamento contábil
- `vrOperacao` (BigDecimal): Valor da operação

Não há relacionamentos entre entidades, pois o sistema trabalha com uma única entidade de domínio.

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBCONTACORRENTE.dbo.TbHistoricoMovimento | Tabela | SELECT | Tabela de histórico de movimentações bancárias, consultada para obter transações de débito de ISS dos últimos 3 dias |

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema apenas realiza leitura de dados, não executa operações de INSERT, UPDATE ou DELETE.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| robo.log | Gravação | Log4j (RollingFileAppender) | Arquivo de log principal da aplicação com informações de execução |
| statistics-{executionId}.log | Gravação | Log4j (BvDailyRollingFileAppender) | Arquivo de estatísticas de execução do batch |
| {PARAM_NOME_ROBO}{PARAM_EXECUTION_ID}1.tlog | Gravação/Leitura | Bitronix Transaction Manager | Arquivo de log de transações do Bitronix (removido ao final) |
| {PARAM_NOME_ROBO}{PARAM_EXECUTION_ID}2.tlog | Gravação/Leitura | Bitronix Transaction Manager | Arquivo de log de transações do Bitronix (removido ao final) |

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

---

## 11. Filas Geradas

**Exchange**: `events.ex.business.ccbd.debitoIss`  
**Routing Key**: `CCBD.debitoIss`  
**Tipo**: RabbitMQ  
**Descrição**: Fila para publicação de eventos de transações de débito de ISS. Cada mensagem contém um objeto TransacaoDebito serializado em JSON.

**Configurações por Ambiente**:
- **DES**: Host 10.39.216.137:5672, usuário _ccbd_des
- **UAT**: Host 10.39.88.213:5672, usuário _ccbd_uat
- **PRD**: Host 10.39.49.197:5672, usuário _ccbd_prd

---

## 12. Integrações Externas

1. **Banco de Dados Sybase**:
   - **Sistema**: DBCONTACORRENTE
   - **Tipo**: Banco de dados Sybase
   - **Descrição**: Consulta de transações de débito através da tabela TbHistoricoMovimento
   - **Ambientes**:
     - DES: sybdesbco.bvnet.bv:7500
     - UAT: moruatbco.bvnet.bv:4400
     - PRD: morsybbco.bvnet.bv:3000

2. **RabbitMQ**:
   - **Sistema**: Message Broker RabbitMQ
   - **Tipo**: Mensageria
   - **Descrição**: Publicação de eventos de transações de débito para consumo por outros sistemas
   - **Protocolo**: AMQP

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com padrão Reader/Processor/Writer
- Uso adequado de injeção de dependências
- Presença de testes unitários com boa cobertura
- Tratamento de exceções customizado
- Uso de constantes para códigos de erro
- Logging adequado em pontos críticos

**Pontos Negativos:**
- Query SQL hardcoded em String dentro do código (Query.java), dificultando manutenção
- ItemProcessor não realiza nenhum processamento real, apenas repassa o objeto
- Uso de isolation level 0 (READ UNCOMMITTED) pode causar leituras sujas
- Data hardcoded para 3 dias atrás (DATEADD(DAY, -3, GETDATE())), deveria ser parametrizável
- Falta de documentação JavaDoc nas classes
- Uso de Java 1.6 (versão muito antiga e sem suporte)
- Classe Query com construtor privado e método estático (anti-pattern para testabilidade)
- Falta de validação mais robusta dos dados antes de publicar na fila
- Código de retomada (MyResumeStrategy) não implementado, sempre retorna false
- Mistura de português e inglês nos nomes de variáveis e comentários

---

## 14. Observações Relevantes

1. **Execução Agendada**: O batch é executado via scripts shell/bat, sugerindo agendamento via cron ou scheduler corporativo
2. **Concorrência**: Configurado para permitir execução concorrente (concurrentExecution=true)
3. **Commit Interval**: Processa 10.000 registros por commit, o que pode ser ajustado conforme volume
4. **Códigos de Saída**: Sistema utiliza códigos de saída específicos (10 para erro MQ, 20 para erro de consulta)
5. **Ambientes**: Possui configurações específicas para DES, UAT e PRD
6. **Segurança**: Senhas em produção utilizam placeholders {{password}} para substituição em tempo de deploy
7. **Framework Proprietário**: Utiliza framework batch proprietário da BV Sistemas, o que pode dificultar migração futura
8. **Dependências Legadas**: Uso de versões antigas de bibliotecas (Jackson 2.0.0, Spring AMQP sem versão explícita)
9. **Documentação**: README.md presente com instruções básicas de execução e configuração
10. **Pipeline CI/CD**: Possui arquivo jenkins.properties indicando integração com Jenkins