# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de migração em lote (batch) desenvolvido em Spring Batch para migrar registros históricos de movimentações bancárias do banco de dados Sybase (DBCONTACORRENTE) para o Google Cloud Spanner. O sistema lê movimentações da tabela `TbHistoricoMovimento`, processa em chunks configuráveis e publica as mensagens no Google Cloud Pub/Sub para posterior consumo e persistência no Spanner. Utiliza particionamento por conta corrente para processamento paralelo e controla o status de migração através da tabela `TbMigracaoContaCorrente`.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot que inicializa a aplicação batch |
| `JobRunner` | Implementa `ApplicationRunner` para executar o job batch com parâmetros da linha de comando |
| `JobConfig` | Configura o job principal de migração com steps, flows e deciders |
| `ParamsJobScope` | Bean com escopo de job que armazena parâmetros de execução (tipo migração, quantidade, banco, conta) |
| `MovementByAccountReader` | ItemReader paginado que lê movimentos do Sybase por conta corrente |
| `MovementByAccountWriter` | ItemWriter que publica movimentos no Google Pub/Sub com controle de sucesso/falha |
| `AccountPartitioner` | Particionador que divide o processamento por contas correntes |
| `MigrationTypeDecider` | Decider que valida e roteia o fluxo baseado no tipo de migração |
| `ValidateAccountFlow` | Flow de validação que verifica existência e status de migração da conta |
| `ProcessMovementsByAccountStep` | Step worker que processa movimentos de uma conta específica |
| `PublishMovementsStep` | Step master que coordena o particionamento e execução paralela |
| `MovementRepository` | Interface JDBI para consultas de movimentos no Sybase |
| `MigrationRepository` | Interface JDBI para controle de contas migradas |
| `AccountRepository` | Interface JDBI para validação de contas |
| `BatchConfig` | Configurações gerais do batch (ObjectMapper, Executor, Publisher factory) |
| `DataSourceConfig` | Configuração de datasources (Sybase e H2 para metadados do batch) |
| `HashUtil` | Utilitário para geração de hash SHA-256 de identificação de contas |

---

## 3. Tecnologias Utilizadas

- **Java 21** (com Virtual Threads habilitadas)
- **Spring Boot 3.x** (baseado no parent `pom-atle-base-sbatch-parent:3.2.1`)
- **Spring Batch** (framework principal para processamento batch)
- **Maven** (gerenciamento de dependências)
- **Sybase jConnect 16.3** (driver JDBC para Sybase)
- **JDBI 3.9.1** (framework de acesso a dados SQL)
- **Google Cloud Pub/Sub 1.127.3** (mensageria)
- **Google Cloud Platform** (infraestrutura)
- **Jackson** (serialização JSON com módulo Afterburner)
- **H2 Database** (armazenamento de metadados do Spring Batch)
- **Logback** (logging com encoder JSON)
- **Docker** (containerização)
- **Lombok** (redução de boilerplate)

---

## 4. Principais Endpoints REST

não se aplica

---

## 5. Principais Regras de Negócio

1. **Validação de Parâmetros**: O tipo de migração deve ser válido (atualmente apenas "Movimento" é suportado)
2. **Validação de Conta**: Antes de migrar, verifica se a conta existe no Sybase
3. **Controle de Migração**: Verifica se a conta já foi migrada anteriormente através da tabela `TbMigracaoContaCorrente`
4. **Particionamento por Conta**: Cada conta corrente é processada em uma partição separada para paralelização
5. **Leitura Paginada**: Movimentos são lidos em páginas configuráveis (chunk size padrão: 1000)
6. **Publicação em Lote**: Mensagens são publicadas no Pub/Sub em lotes com controle de backpressure
7. **Controle de Estado**: Utiliza `ExecutionContext` para manter o último item processado (lastItem) permitindo restart
8. **Retry com Backoff**: Configurado retry de até 5 tentativas com backoff fixo de 5 minutos
9. **Registro de Migração**: Ao finalizar com sucesso, registra a conta como migrada com informações de falhas
10. **Hash de Identificação**: Gera hash SHA-256 dos primeiros 16 caracteres para identificação única de contas nos logs

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **MigrationAccount**: Representa uma conta corrente a ser migrada
  - Atributos: bank (Integer), accountNumber (Long), accountType (Integer), accountHash (String), branchNumber (String)
  
- **Movement**: Representa uma movimentação bancária
  - Atributos: cdBanco, nuContaCorrente, cdTipoConta, cdAgenciaOperacao, dtComandoOperacao, dtEfetivacaoOperacao, flLancamentoIncondicional, nuSequencialUnicoLancamento, dsComplementoOperacao, nuDocumento, vrOperacao, vrSaldoDisponivelAnterior, vrSaldoAposLancamento, cdSistema, cdUsuario, cdTransacao, tpDebitoCredito, cdLiquidacao, nmTransacao, nmTransacaoReduzida, dtInclusao, dtAlteracao, sqMovimentoConta

**Relacionamentos:**
- Uma `MigrationAccount` possui múltiplos `Movement` (1:N)
- O relacionamento é estabelecido através dos campos: cdBanco, nuContaCorrente, cdTipoConta

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBCONTACORRENTE.dbo.TbConta | tabela | SELECT | Validação de existência de conta corrente |
| DBCONTACORRENTE.dbo.TbMigracaoContaCorrente | tabela | SELECT | Verificação de status de migração de contas |
| DBCONTACORRENTE.dbo.TbHistoricoMovimento | tabela | SELECT | Leitura de movimentações históricas para migração |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBCONTACORRENTE.dbo.TbMigracaoContaCorrente | tabela | INSERT | Registro de contas migradas com sucesso e informações de falhas |
| BATCH_JOB_EXECUTION (H2) | tabela | INSERT/UPDATE | Metadados de execução do Spring Batch |
| BATCH_STEP_EXECUTION (H2) | tabela | INSERT/UPDATE | Metadados de execução de steps do Spring Batch |
| BATCH_JOB_EXECUTION_CONTEXT (H2) | tabela | INSERT/UPDATE | Contexto de execução para restart |
| BATCH_STEP_EXECUTION_CONTEXT (H2) | tabela | INSERT/UPDATE | Contexto de step para controle de estado (lastItem) |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot | Configurações da aplicação |
| application-local.yml | leitura | Spring Boot | Configurações específicas do ambiente local |
| logback-spring.xml | leitura | Logback | Configuração de logging |
| spreadsheet.csv | leitura | Recursos | Arquivo CSV de exemplo (não utilizado no fluxo principal) |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

**Tópico Pub/Sub:**
- **Nome**: `business-ccbd-base-migration`
- **Projeto GCP**: 
  - DES: `bv-ccbd-des`
  - UAT: `bv-ccbd-uat`
  - PRD: `bv-ccbd-prd`
- **Formato**: Mensagens JSON com atributo `tipo=Movimento`
- **Conteúdo**: Objetos `Movement` serializados
- **Configuração de Batching**:
  - Element Count: 1000
  - Request Bytes: 1MB
  - Delay: 100ms
  - Timeout: 120s
  - Max Outstanding Elements: 10000
  - Max Outstanding Bytes: 10MB

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Sybase DBCONTACORRENTE | Banco de Dados | Leitura de contas e movimentações históricas |
| Google Cloud Pub/Sub | Mensageria | Publicação de movimentos para processamento assíncrono |
| H2 Database | Banco de Dados | Armazenamento de metadados do Spring Batch (em memória) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões hexagonais (ports/adapters)
- Uso adequado de Spring Batch com particionamento e paralelização
- Implementação de retry e backoff para resiliência
- Controle de estado para restart de jobs
- Logging estruturado com informações de rastreabilidade (hash de conta)
- Uso de Virtual Threads do Java 21 para melhor performance
- Configurações externalizadas e separadas por ambiente
- Uso de JDBI para queries SQL organizadas em arquivos separados
- Implementação de métricas e listeners para monitoramento

**Pontos de Melhoria:**
- Falta de testes unitários incluídos na análise (marcados como NAO_ENVIAR)
- Algumas constantes poderiam estar em enums ao invés de classe Constants
- Documentação JavaDoc ausente em várias classes
- Tratamento de exceções poderia ser mais específico em alguns pontos
- Configuração de retry hardcoded (5 tentativas) poderia ser parametrizável

O código demonstra maturidade técnica, boas práticas de engenharia de software e preocupação com aspectos não-funcionais como observabilidade, resiliência e performance.

---

## 14. Observações Relevantes

1. **Execução**: O job é executado via linha de comando com parâmetros: `--tipoMigracao`, `--quantidade`, `--banco`, `--numeroConta`, `--tipoConta`

2. **Ambientes**: Suporta três ambientes (DES, UAT, PRD) com configurações específicas de datasource, Pub/Sub e logging

3. **Paralelização**: Configurado para processar até 1000 contas simultaneamente com Virtual Threads

4. **Monitoramento**: Implementa listeners customizados (`JobLogListener`, `StepLogListener`) para rastreamento detalhado

5. **Segurança**: Integração com OAuth2/JWT para autenticação (configuração presente mas não utilizada no batch)

6. **Infraestrutura**: Preparado para deploy no Google Cloud Platform via Docker e Kubernetes

7. **Controle de Versão**: Utiliza incrementador de RunId para garantir unicidade de execuções

8. **Chunk Size**: Configurável via properties (padrão: 1000 registros por chunk)

9. **Grid Size**: Configurável para controlar número de partições (padrão: 1000)

10. **Charset**: Utiliza ISO-1 para conexão com Sybase