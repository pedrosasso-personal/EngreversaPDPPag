# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sbatch-saca-scco-reabertura-parcela** é uma aplicação Spring Batch desenvolvida para realizar a extração e processamento de parcelas que necessitam de reabertura após estorno. O batch consulta múltiplos bancos de dados Sybase (DbGestaoCDCCG, DbGestaoCPC, DbGestaoCP, DbGestaoCDCSG, DbGestaoLSG) em busca de parcelas estornadas dentro de um período específico, valida se o contrato financeiro está ativo e publica as informações em uma fila Google Cloud Pub/Sub para processamento posterior.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `SpringBatchApplication` | Classe principal que inicializa a aplicação Spring Batch |
| `BatchConfiguration` | Configura o Job principal do batch com seus steps |
| `StepConfiguration` | Define os steps do processamento batch (leitura, processamento, escrita) |
| `ReadersConfiguration` | Configura o reader JDBC para leitura das parcelas de estorno do Sybase |
| `ParcelaEstornoWriter` | Writer responsável por publicar mensagens no Google Cloud Pub/Sub |
| `ParcelaEstorno` | Entidade de domínio representando uma parcela de estorno |
| `ParcelaEstornoRowMapper` | Mapper para conversão de ResultSet em objeto ParcelaEstorno |
| `H2DatasourceConfiguration` | Configuração do datasource H2 para metadados do Spring Batch |
| `SybaseDatasourceConfiguration` | Configuração do datasource Sybase para leitura de dados de negócio |
| `PubSubProperties` | Propriedades de configuração do Google Cloud Pub/Sub |
| `ReaberturaParcelaException` | Exception customizada para erros no processo de reabertura |

## 3. Tecnologias Utilizadas

- **Java 11** (OpenJ9)
- **Spring Boot 2.x**
- **Spring Batch** (processamento em lote)
- **Spring Cloud Task** (gerenciamento de tarefas)
- **Spring Cloud GCP Pub/Sub** (mensageria)
- **Sybase Database** (via driver JTDS)
- **H2 Database** (para metadados do Spring Batch)
- **Lombok** (redução de boilerplate)
- **Logback** (logging com formato JSON)
- **Docker** (containerização)
- **Kubernetes** (orquestração - evidenciado pelos arquivos YAML)
- **Maven** (gerenciamento de dependências)
- **Google Cloud Platform** (infraestrutura)
- **JUnit Jupiter 5+** (testes)
- **Swagger/SpringFox 3.0.0** (documentação de API)

## 4. Principais Endpoints REST

Não se aplica. Trata-se de uma aplicação Spring Batch executada como job, não expõe endpoints REST para processamento de negócio. Possui apenas endpoints do Spring Boot Actuator para health check (`/actuator/health`).

## 5. Principais Regras de Negócio

1. **Período de Processamento**: O batch processa parcelas estornadas dentro de um intervalo de datas específico (dataInicio e dataFinal passados como parâmetros do job)

2. **Validação de Contrato Ativo**: Apenas parcelas cujo contrato financeiro está ativo (SqContratoFinanceiro = SqContratoFinanceiroAtivo) são consideradas para reabertura

3. **Múltiplas Bases de Dados**: O sistema consulta 5 bases de dados diferentes (DbGestaoCDCCG, DbGestaoCPC, DbGestaoCP, DbGestaoCDCSG, DbGestaoLSG) através de UNION ALL para consolidar as parcelas de estorno

4. **Limitação de Registros**: A query utiliza "TOP 1" em cada UNION, sugerindo processamento limitado ou incremental

5. **Publicação Assíncrona**: As parcelas identificadas são publicadas em fila Pub/Sub para processamento assíncrono posterior

6. **Tratamento de Erros**: Falhas na publicação de mensagens geram exceções customizadas (ReaberturaParcelaException) que interrompem o processamento

## 6. Relação entre Entidades

**ParcelaEstorno** (entidade principal):
- `nuContrato` (Long): Número do contrato
- `nuParcela` (Integer): Número da parcela
- `sqContratoFinanceiro` (Integer): Sequencial do contrato financeiro

**Relacionamentos identificados na query SQL**:
- `TbParcelaEstorno` relaciona-se com `TbContrato` através de:
  - `NuContrato` (chave de junção)
  - `SqContratoFinanceiro` = `SqContratoFinanceiroAtivo` (validação de contrato ativo)

Não há relacionamentos JPA/Hibernate mapeados, pois o sistema utiliza JDBC puro para leitura.

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DbGestaoCDCCG..TbParcelaEstorno | Tabela | SELECT | Tabela de parcelas estornadas do sistema CDC CG |
| DbGestaoCDCCG..TbContrato | Tabela | SELECT | Tabela de contratos do sistema CDC CG |
| DbGestaoCPC..TbParcelaEstorno | Tabela | SELECT | Tabela de parcelas estornadas do sistema CPC |
| DbGestaoCPC..TbContrato | Tabela | SELECT | Tabela de contratos do sistema CPC |
| DbGestaoCP..TbContrato | Tabela | SELECT | Tabela de contratos do sistema CP |
| DbGestaoCDCSG..TbContrato | Tabela | SELECT | Tabela de contratos do sistema CDC SG |
| DbGestaoLSG..TbContrato | Tabela | SELECT | Tabela de contratos do sistema LSG |

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema apenas realiza leitura de dados, não executa operações de INSERT, UPDATE ou DELETE nas bases de dados de negócio. As tabelas de controle do Spring Batch (H2) são gerenciadas automaticamente pelo framework.

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| parcelasEstorno.sql | Leitura | ReadersConfiguration | Query SQL para busca de parcelas de estorno nas múltiplas bases |
| logback-spring.xml | Leitura | Configuração Spring Boot | Arquivo de configuração de logs (JSON format) por ambiente |
| application.yml | Leitura | Spring Boot | Arquivo de configuração da aplicação |

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas, apenas publica.

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Responsável | Breve Descrição |
|--------------|-----------|-------------------|-----------------|
| business-gopr-blto-reabertura-parcela | Google Cloud Pub/Sub | ParcelaEstornoWriter | Fila para publicação de parcelas que necessitam reabertura após estorno |

**Configuração por ambiente**:
- **Local/DES**: Tópico configurado como `business-gopr-blto-reabertura-parcela` no projeto `bv-gopr-des`
- **QA/UAT/PRD**: Tópico configurado via variável `${pubsub.topic}` no projeto `${GCP_GOPR_PROJECT_ID}`

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Google Cloud Pub/Sub | Mensageria | Publicação de mensagens com dados de parcelas para reabertura |
| API Gateway BV | Autenticação | Obtenção de token JWT para autenticação (endpoints: `/auth/oauth/v2/token-jwt`) |
| Sybase Databases (múltiplas instâncias) | Banco de Dados | Leitura de dados de parcelas estornadas e contratos de diferentes sistemas legados |

**Endpoints API Gateway por ambiente**:
- DES: https://apigatewaydes.bvnet.bv
- QA: https://apigatewayqa.bvnet.bv
- UAT: https://apigatewayuat.bvnet.bv
- PRD: https://apigateway.bvnet.bv

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com pacotes bem organizados (config, domain, mapper, writer, exception)
- Uso adequado de anotações Lombok reduzindo boilerplate
- Configuração externalizada por ambiente (application.yml)
- Tratamento de exceções customizado
- Uso de builders para construção de objetos
- Logging estruturado em JSON
- Testes unitários presentes
- Documentação básica no README

**Pontos de Melhoria:**
- **Chunk size configurado como 0** no StepConfiguration, o que desabilita o processamento em lote do Spring Batch, processando item a item (ineficiente)
- **Query SQL com "TOP 1"** em cada UNION sugere lógica incompleta ou limitação artificial não justificada
- **Substituição de parâmetros SQL via String.replace()** é insegura e propensa a SQL injection (deveria usar PreparedStatement)
- **Falta de processor**: O step está configurado sem processor, apenas reader e writer
- **Tratamento de erro no callback assíncrono** lança exceção mas não garante rollback adequado
- **Falta de documentação inline** em métodos e classes críticas
- **Configurações hardcoded** em alguns pontos (ex: chunk size 0)
- **Ausência de retry/skip policies** para tratamento de falhas transientes

## 14. Observações Relevantes

1. **Arquitetura de Execução**: O batch é executado como Kubernetes Job (CronJob), não como aplicação contínua, evidenciado pelos arquivos `job.yaml` e configuração `createJob: true`

2. **Múltiplos Ambientes**: Infraestrutura bem estruturada para 5 ambientes (local, des, qa, uat, prd) com configurações específicas via ConfigMaps e Secrets

3. **Segurança**: Implementa OAuth2 Resource Server com integração ao API Gateway do Banco Votorantim para autenticação

4. **Monitoramento**: Expõe endpoints do Actuator para health checks utilizados pelos probes do Kubernetes (liveness e readiness)

5. **Processamento Limitado**: A query com "TOP 1" em cada UNION sugere que o batch processa apenas 5 registros por execução (1 de cada base), o que pode indicar execução frequente ou necessidade de revisão da lógica

6. **Dependência de Parâmetros**: O job requer parâmetros obrigatórios `dataInicio` e `dataFinal` para execução

7. **Banco H2 para Metadados**: Utiliza H2 em memória para tabelas de controle do Spring Batch, o que significa que o histórico de execuções não é persistido entre execuções

8. **Pipeline CI/CD**: Integrado com Jenkins conforme arquivo `jenkins.properties`, com validações de vulnerabilidade e quality gate habilitadas

9. **Timezone**: Dockerfile configura timezone via `apk add tzdata` para garantir consistência de datas

10. **Service Account**: Utiliza RBAC do Kubernetes com service account customizado para gerenciar pods e jobs