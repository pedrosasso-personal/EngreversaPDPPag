---
## Ficha Técnica do Sistema

### 1. Descrição Geral
Sistema batch desenvolvido em Spring Boot para extração de dados jurídicos de tributos a partir de uma view do SQL Server (VwJuridicoEasyTributos) e geração de arquivo CSV no Google Cloud Storage. O sistema é utilizado para integração com o sistema Easy Tributos, processando informações de tributos jurídicos em lotes de 50.000 registros, com filtro por período de emissão configurável via parâmetros de job.

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Entry point da aplicação batch Spring Boot |
| **JobConfiguration** | Configuração do job Spring Batch com step de leitura-processamento-escrita |
| **TributoReader** | Leitura de dados via JDBC cursor do SQL Server/H2 |
| **TributoProcessor** | Processador pass-through sem transformação de dados |
| **TributoWriter** | Geração de arquivo CSV e gravação no Google Cloud Storage |
| **DataSourceConfiguration** | Configuração de dois datasources (H2 para metadata batch e SQL Server para origem) |
| **TributoDomain** | Entidade de domínio com 27 campos de tributos jurídicos |
| **TributoDomainRowMapper** | Mapeamento de ResultSet JDBC para objeto de domínio |
| **ItemReaderListener** | Listener para log de eventos de leitura |
| **ItemProcessorListener** | Listener para log de eventos de processamento |
| **ItemWriterListener** | Listener para log de eventos de escrita |
| **JobNotificationListener** | Listener para notificação de eventos do job |
| **SBatchException** | Exception customizada para tratamento de erros do batch |

### 3. Tecnologias Utilizadas
- **Framework Principal**: Spring Boot 3.x
- **Batch Processing**: Spring Batch
- **Linguagem**: Java 21 (com Virtual Threads)
- **Banco de Dados**: 
  - SQL Server (mssql-jdbc 12.10) - origem dos dados
  - H2 Database - metadata batch e mock local
- **Cloud Storage**: Google Cloud Storage SDK
- **Build**: Maven
- **Containerização**: Docker
- **Orquestração**: Kubernetes (GCP)
- **Utilitários**: Lombok
- **Logging**: Logback
- **Testes**: JUnit 5, Mockito

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | /actuator/health | Spring Actuator | Health check da aplicação (porta 9090) |

**Observação**: Não há endpoints REST de negócio, apenas endpoints de monitoramento do Spring Actuator.

### 5. Principais Regras de Negócio
1. **Filtro por Período**: Extração de dados filtrada por período de emissão (dataInicial/dataFinal) configurável via jobParameters
2. **Query de Extração**: `SELECT 27 campos FROM VwJuridicoEasyTributos WHERE EMISSAO between ? and ?`
3. **Processamento em Chunks**: Lotes de 50.000 registros por vez para otimização de performance
4. **Formato de Saída**: Arquivo CSV com 27 colunas separadas por ponto-e-vírgula (`;`), encoding UTF-8
5. **Nomenclatura de Arquivo**: Padrão `tributo-juridico-{dataFinal}.csv` em path configurável no GCS
6. **Tratamento de Falhas**: Falhas em leitura/escrita são registradas via listeners e o job é interrompido em caso de SBatchException
7. **Processamento Pass-Through**: Dados são extraídos e gravados sem transformação de negócio

### 6. Relação entre Entidades
**Fluxo de Dados**:
```
VwJuridicoEasyTributos (SQL Server) 
    ↓ (leitura JDBC)
TributoDomain (entidade batch)
    ↓ (processamento pass-through)
CSV no Google Cloud Storage
```

**Entidade TributoDomain** (27 campos):
- Dados da Empresa: EMPRESA, CNPJ
- Dados do Documento: DOCUMENTO, EMISSAO, TPOPERACAO, TPDOCUMENTO
- Valores Financeiros: VALORDOCUMENTO, VALORLIQUIDO, VALOR, VALINSSEMP, VALINSSFONTE, VALORTOTAL, DESPESASJURI, VALDESPADV
- Bases de Cálculo: BASEIRRF, BASEINSS, ISENCAOIRRF
- Datas: DTVENCIMENTO, DTCREDITO
- Informações Complementares: OBSERVACAO, NUMEROMESES, TPPAGAMENTO
- Controle DARF: GERADARFIIN, DARFJAEMITIDA
- Dados Jurídicos: NUMEROPROCESSO, CNPJADVOGADO, NOMEADVOGADO

### 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| VwJuridicoEasyTributos | View | SELECT | View no SQL Server (DBERPPROTHEUS) contendo dados consolidados de tributos jurídicos com 27 campos, filtrada por período de emissão |
| BATCH_JOB_INSTANCE | Tabela | SELECT | Tabela de metadata do Spring Batch (H2) para controle de instâncias de jobs |
| BATCH_JOB_EXECUTION | Tabela | SELECT | Tabela de metadata do Spring Batch (H2) para controle de execuções de jobs |
| BATCH_STEP_EXECUTION | Tabela | SELECT | Tabela de metadata do Spring Batch (H2) para controle de execuções de steps |

### 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| BATCH_JOB_INSTANCE | Tabela | INSERT | Registro de novas instâncias de jobs no H2 |
| BATCH_JOB_EXECUTION | Tabela | INSERT/UPDATE | Registro e atualização de execuções de jobs no H2 |
| BATCH_STEP_EXECUTION | Tabela | INSERT/UPDATE | Registro e atualização de execuções de steps no H2 |
| BATCH_JOB_EXECUTION_CONTEXT | Tabela | INSERT/UPDATE | Contexto de execução de jobs no H2 |
| BATCH_STEP_EXECUTION_CONTEXT | Tabela | INSERT/UPDATE | Contexto de execução de steps no H2 |

### 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| tributo-juridico-{dataFinal}.csv | Gravação | TributoWriter / Google Cloud Storage | Arquivo CSV com dados de tributos jurídicos, 27 colunas separadas por `;`, encoding UTF-8 |
| data.sql | Leitura | H2 Database (profile local) | Script SQL para carga de dados mock em ambiente local |
| schema.sql | Leitura | H2 Database (db-h2/ddl/) | DDL da view VwJuridicoEasyTributos para mock local |
| application-{profile}.properties | Leitura | Spring Boot Configuration | Arquivos de configuração por ambiente (local, des, uat, prd) |
| logback-spring.xml | Leitura | Logback | Configuração de logs por ambiente |

**Path GCS**: `erpt-base-system-tributos-federais-{env}/arquivos/easy/juridico/tributo-juridico-{data}.csv`

### 10. Filas Lidas
Não se aplica.

### 11. Filas Geradas
Não se aplica.

### 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|----------------|------|-----------|
| **SQL Server** | Banco de Dados | Leitura da view VwJuridicoEasyTributos via JDBC. Ambientes: DES (PTASQLDES01/PTASQLUAT01), UAT (PTASQLUAT01), PRD (SQLERPPRD) |
| **Google Cloud Storage** | Cloud Storage | Gravação de arquivos CSV via SDK com autenticação GoogleCredentials default. Buckets configuráveis por ambiente |
| **Easy Tributos** | Sistema Legado | Sistema destino que consome os arquivos CSV gerados (integração via arquivo) |

### 13. Avaliação da Qualidade do Código

**Nota:** 8/10

**Justificativa:**

**Pontos Positivos:**
- Excelente separação de responsabilidades com classes bem definidas (Reader, Processor, Writer)
- Uso adequado de profiles para diferentes ambientes (local, des, uat, prd)
- Implementação de listeners para rastreabilidade e log de eventos
- Testes unitários implementados com JUnit 5 e Mockito
- Uso de Lombok para redução de boilerplate
- Aproveitamento de recursos modernos do Java 21 (Virtual Threads) para paralelismo
- Configuração modular e bem organizada (datasources, job, storage)
- Exception customizada (SBatchException) para tratamento específico
- Dockerfile multi-layer otimizado
- Infraestrutura como código (jenkins.properties, infra.yml)

**Pontos de Melhoria:**
- Ausência de testes de integração
- Falta de validação explícita de regras de negócio nos dados extraídos
- Políticas de retry não explicitamente configuradas
- Skip policy limitada (apenas noSkip para SBatchException)
- Documentação técnica poderia ser mais detalhada no código
- Falta de métricas de negócio (ex: quantidade de registros processados por tipo)

O código demonstra maturidade técnica e boas práticas de desenvolvimento, com arquitetura bem estruturada e uso adequado do framework Spring Batch. As melhorias sugeridas são incrementais e não comprometem a qualidade geral da solução.

### 14. Observações Relevantes

1. **Estratégia de Banco de Dados Dual**: O sistema utiliza H2 em memória para metadata do Spring Batch em todos os ambientes, enquanto o SQL Server é usado exclusivamente para leitura dos dados de negócio.

2. **Mock Local Completo**: Ambiente local totalmente funcional com H2 contendo DDL da view (schema.sql) e dados de teste (data.sql), permitindo desenvolvimento e testes sem dependência de infraestrutura externa.

3. **Processamento Assíncrono**: Job launcher configurado com VirtualThreadTaskExecutor do Java 21, aproveitando threads virtuais para melhor performance e escalabilidade.

4. **Chunk Size Otimizado**: Processamento em lotes de 50.000 registros balanceia performance e consumo de memória.

5. **Parametrização Flexível**: Período de extração (dataInicial/dataFinal) configurável via jobParameters, permitindo execuções sob demanda ou agendadas.

6. **Ambientes Segregados**: Configuração específica para cada ambiente (DES, UAT, PRD) com servidores SQL Server e buckets GCS distintos.

7. **Monitoramento**: Endpoint actuator/health na porta 9090 para health checks do Kubernetes.

8. **Formato de Integração**: CSV com separador `;` e encoding UTF-8 é o contrato de integração com o sistema Easy Tributos.

9. **Ausência de Transformação**: O TributoProcessor é pass-through, indicando que a view VwJuridicoEasyTributos já fornece os dados no formato esperado pelo sistema destino.

10. **Infraestrutura Cloud-Native**: Solução preparada para execução em Kubernetes no GCP com configurações de deployment via infra.yml.