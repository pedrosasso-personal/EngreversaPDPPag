---
## Ficha Técnica do Sistema

### 1. Descrição Geral
Sistema batch desenvolvido em Spring Batch para extração de dados de tributos com auto-retenção do sistema ERP Protheus e geração de arquivo CSV para integração com a plataforma Easy Tributos. O processo lê dados de uma view no banco de dados SQL Server, processa os registros em chunks e grava o resultado em arquivo CSV no Google Cloud Storage (GCS).

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal de inicialização da aplicação Spring Boot |
| `JobConfiguration` | Configuração do job Spring Batch, steps, transaction managers e task executor com virtual threads |
| `DataSourceConfiguration` | Configuração de dois datasources: batch (H2 em memória) e origin (SQL Server) |
| `TributoReader` | Configuração do reader JDBC para leitura da view `VwAutoRetencaoEasyTributos` |
| `TributoProcessor` | Processador de itens (atualmente pass-through, sem transformação) |
| `TributoWriter` | Writer responsável por gerar arquivo CSV e gravar no Google Cloud Storage |
| `TributoDomain` | Entidade de domínio representando os dados de tributo |
| `TributoDomainRowMapper` | Mapper para conversão de ResultSet em TributoDomain |
| `TributoContabilStatementSetter` | Setter de parâmetros para prepared statement (datas inicial e final) |
| `StorageConfiguration` | Configuração do cliente Google Cloud Storage |
| `JobNotificationListener` | Listener para notificação de conclusão do job |
| `ItemReaderListener` | Listener para tratamento de erros na leitura |
| `ItemProcessorListener` | Listener para tratamento de erros no processamento |
| `ItemWriterListener` | Listener para tratamento de erros na escrita |
| `SBatchException` | Exceção customizada para erros do batch |
| `DataUtils` | Utilitário para formatação de datas |

### 3. Tecnologias Utilizadas
- **Java 21** (com suporte a Virtual Threads)
- **Spring Boot 3.x** (baseado no parent pom-atle-base-sbatch-parent 3.2.1)
- **Spring Batch** (framework de processamento batch)
- **SQL Server** (banco de dados origem - ERP Protheus)
- **H2 Database** (banco de dados em memória para metadados do Spring Batch)
- **Google Cloud Storage** (armazenamento de arquivos CSV)
- **Google Cloud Platform (GCP)** - projeto bv-erpt-des/uat/prd
- **Maven** (gerenciamento de dependências)
- **Lombok** (redução de boilerplate)
- **Docker** (containerização)
- **Kubernetes** (orquestração - evidenciado pelo infra.yml)
- **Logback** (logging)
- **Spring Security OAuth2** (segurança com JWT)
- **Actuator** (monitoramento e health checks)

### 4. Principais Endpoints REST
Não se aplica. Este é um componente batch sem endpoints REST expostos para processamento de negócio. Apenas endpoints de infraestrutura (Actuator) estão disponíveis:
- `/actuator/health` (porta 9090)
- `/actuator/info` (porta 9090)
- `/actuator/metrics` (porta 9090)
- `/actuator/prometheus` (porta 9090)

### 5. Principais Regras de Negócio
- Extração de dados de tributos com auto-retenção do ERP Protheus filtrados por período (data inicial e data final)
- Processamento em chunks de 50.000 registros para otimização de performance
- Geração de arquivo CSV com delimitador ponto-e-vírgula (;) contendo 12 campos de tributos
- Nomenclatura do arquivo segue padrão: `tributo-auto-retencao-{dataFinal}.csv`
- Tratamento de valores nulos convertendo para string vazia após trim
- Utilização de Virtual Threads (Java 21) para processamento assíncrono
- Política de fault tolerance: não permite skip de `SBatchException`
- Inicialização automática de schema H2 em ambientes local e des para testes

### 6. Relação entre Entidades
**TributoDomain** (entidade principal):
- Representa um registro de tributo com auto-retenção
- Campos: empresa, cnpjCliente, documento, emissao, codigo, valorBruto, total, valorIRRF, serie, tipo, aliqIRRF, tpDocumento
- Não possui relacionamentos com outras entidades (estrutura flat)
- Serializable para suporte ao processamento batch

### 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| VwAutoRetencaoEasyTributos | View | SELECT | View do ERP Protheus contendo dados de tributos com auto-retenção filtrados por período de emissão |

### 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| BATCH_JOB_INSTANCE | Tabela | INSERT | Tabela de metadados do Spring Batch para controle de instâncias de jobs (gerenciada automaticamente pelo framework) |
| BATCH_JOB_EXECUTION | Tabela | INSERT/UPDATE | Tabela de metadados do Spring Batch para controle de execuções de jobs (gerenciada automaticamente pelo framework) |
| BATCH_STEP_EXECUTION | Tabela | INSERT/UPDATE | Tabela de metadados do Spring Batch para controle de execuções de steps (gerenciada automaticamente pelo framework) |

### 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| schema.sql | Leitura | DataSourceConfiguration / db-h2/ddl/ | Script DDL para criação da estrutura da view VwAutoRetencaoEasyTributos em H2 (ambientes local/des) |
| data.sql | Leitura | DataSourceConfiguration / db-h2/dml/ | Script DML para carga de dados de teste em H2 (ambientes local/des) |
| tributo-auto-retencao-{dataFinal}.csv | Gravação | TributoWriter / GCS bucket | Arquivo CSV com dados de tributos gerado no Google Cloud Storage |
| logback-spring.xml | Leitura | Configuração de logging | Arquivo de configuração de logs (diferentes versões por ambiente: des/uat/prd) |

### 10. Filas Lidas
Não se aplica.

### 11. Filas Geradas
Não se aplica.

### 12. Integrações Externas
- **ERP Protheus (SQL Server)**: Leitura de dados de tributos através da view `VwAutoRetencaoEasyTributos`
  - Ambientes: PTASQLDES01 (des), PTASQLUAT01 (uat), SQLERPPRD (prd)
  - Database: DBERPPROTHEUS
  - Usuário: ERPTDBERPPROTHEUS_BATCH
- **Google Cloud Storage**: Gravação de arquivos CSV
  - Buckets: erpt-base-system-tributos-federais-{ambiente}
  - Pasta: arquivos/easy/auto-retencao/
- **OAuth2/JWT**: Autenticação via API Gateway BV
  - JWKS URLs por ambiente (des/uat/prd)

### 13. Avaliação da Qualidade do Código

**Nota:** 8/10

**Justificativa:**
- **Pontos Positivos:**
  - Boa separação de responsabilidades com pacotes bem organizados (config, domain, listener, mapper, utils)
  - Uso adequado de recursos modernos do Java 21 (Virtual Threads)
  - Configuração externalizada e parametrizada por ambiente
  - Implementação de listeners para tratamento de erros em todas as fases do batch
  - Uso de Lombok para redução de boilerplate
  - Configuração de múltiplos datasources bem estruturada
  - Documentação básica presente no README
  
- **Pontos de Melhoria:**
  - Processor atualmente não realiza nenhuma transformação (pass-through)
  - Falta de testes unitários (diretório test vazio)
  - Tratamento de exceções poderia ser mais granular
  - Ausência de validações de negócio nos dados lidos
  - Falta de documentação inline (JavaDoc) nas classes
  - Configuração de chunk size (50.000) hardcoded, poderia ser parametrizável

### 14. Observações Relevantes
- O sistema utiliza dois datasources distintos: um para metadados do Spring Batch (H2 em memória) e outro para leitura dos dados de origem (SQL Server)
- Em ambientes local e des, utiliza H2 com scripts de inicialização para simular a view do SQL Server
- O job é configurado com `allowStartIfComplete(true)`, permitindo reexecução mesmo após conclusão bem-sucedida
- Utiliza Virtual Threads do Java 21 para melhor performance no processamento assíncrono
- A aplicação encerra automaticamente após conclusão do job (`System.exit`)
- Probes de liveness e readiness configurados para Kubernetes com timeouts específicos
- Service Account Kubernetes: ksa-erpt-base-44735
- Senhas armazenadas em cofre de senhas (referenciadas no infra.yml)
- Porta 8080 para aplicação e 9090 para endpoints de management/actuator

### 15. Histórico da Iteração

**Iteração 1:**
- Análise inicial do projeto completo sbatch-erpt-base-tributo-auto-retencao
- Identificação da arquitetura Spring Batch com leitura de SQL Server e gravação em GCS
- Mapeamento de todas as classes principais, configurações e estrutura do projeto
- Documentação de tecnologias utilizadas (Java 21, Spring Batch, SQL Server, GCS)
- Identificação da view VwAutoRetencaoEasyTributos como fonte de dados
- Documentação de arquivos lidos/gravados e integrações externas
- Avaliação inicial da qualidade do código: 8/10