# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sbatch-pgft-base-consolidado-transacoes** é um componente batch desenvolvido em Spring Batch responsável por consolidar e processar transações de pagamento do sistema legado PGFT. O sistema realiza a leitura de lançamentos financeiros do banco de dados Sybase, filtra transações com códigos de liquidação específicos (TED, TEF, Boletos, Tributos e Débitos Veiculares), transforma os dados para o formato Avro e publica as transações processadas em um tópico Kafka para consumo por outros sistemas.

O processamento é controlado por Feature Toggles e utiliza autenticação OAuth2 para integração com APIs externas. O componente segue o padrão de arquitetura em camadas (Reader → Processor → Writer) do Spring Batch.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal que inicializa a aplicação Spring Boot e Spring Batch |
| **JobConfig** | Configuração do job batch, datasources (H2 e Sybase), transaction managers e steps |
| **Reader** | ItemReader responsável por buscar transações consolidadas do banco PGFT via service |
| **Processor** | ItemProcessor que filtra transações por código de liquidação e mapeia DTO para Avro |
| **Writer** | ItemWriter que envia as transações processadas para o tópico Kafka |
| **ConsolidadoTransacaoService** | Serviço que busca lançamentos no repositório e converte projections para DTOs |
| **ConsolidadoTransacoesRepository** | Repositório JPA que executa query nativa para buscar lançamentos do PGFT |
| **ConsolidadoTransacaoMapper** | Mapper responsável por converter projections em DTOs e DTOs em objetos Avro |
| **EnviaTransacoesConsolidadasRepositoryImpl** | Implementação que publica eventos Kafka com transações processadas |
| **GatewayOAuthService** | Serviço de autenticação OAuth2 para obtenção e gerenciamento de tokens de acesso |
| **ClientService** | Cliente Feign que consome API para obter o código do último lançamento processado |
| **FeatureToggleService** | Serviço que gerencia feature toggles para habilitar/desabilitar funcionalidades |
| **KafkaConfiguration** | Configuração do producer Kafka e propriedades de conexão |
| **ConsolidadoTransacoesDTO** | DTO que representa uma transação consolidada |
| **ConsolidadoTransacoes** | Entidade JPA mapeada para a tabela TBL_LANCAMENTO do Sybase |

---

## 3. Tecnologias Utilizadas

- **Java 21**
- **Spring Boot 3.x** (baseado no parent pom-atle-base-sbatch-parent 3.5.1)
- **Spring Batch** - Framework para processamento batch
- **Spring Data JPA / Hibernate** - Persistência e ORM
- **Sybase jConnect 4 (16.3-SP03-PL07)** - Driver JDBC para Sybase
- **H2 Database** - Banco em memória para metadados do Spring Batch
- **Apache Kafka** - Mensageria para publicação de eventos
- **Confluent Kafka Avro Serializer** - Serialização de mensagens em formato Avro
- **Schema Registry** - Gerenciamento de schemas Avro
- **Spring Cloud OpenFeign** - Cliente HTTP declarativo para APIs REST
- **OAuth2** - Autenticação e autorização
- **Logback** - Framework de logging com encoder JSON
- **Lombok** - Redução de boilerplate
- **Maven** - Gerenciamento de dependências
- **Docker** - Containerização
- **ConfigCat (Feature Toggle)** - Gerenciamento de feature flags
- **JUnit 5 + Mockito** - Testes unitários
- **Swagger/OpenAPI** - Documentação de APIs (via springdoc-openapi)

---

## 4. Principais Endpoints REST

Não se aplica. Este é um componente batch que não expõe endpoints REST para processamento de negócio. Apenas endpoints do Spring Boot Actuator estão disponíveis:

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | /actuator/health | Health check da aplicação (porta 9090) |
| GET | /actuator/metrics | Métricas da aplicação |
| GET | /actuator/prometheus | Métricas no formato Prometheus |

---

## 5. Principais Regras de Negócio

1. **Filtragem por Código de Liquidação**: Apenas transações com códigos de liquidação 1, 22, 31, 32, 59 e 60 são processadas
2. **Classificação de Tipo de Liquidação**: 
   - Códigos 31 e 32 → TED
   - Código 22 → Boletos
   - Códigos 59 e 60 → Tributos
   - Código 1 → TEF, Débitos Veiculares ou Tributos (dependendo do código de transação)
3. **Filtragem por Status**: Apenas lançamentos com status 1 (Efetivado) ou 3 (Rejeitado) são considerados
4. **Controle de Processamento Incremental**: Utiliza o código do último lançamento processado para buscar apenas novos registros
5. **Feature Toggle**: O processamento só ocorre se a feature "ft_boolean_publicacao_transacao_consolidado" estiver habilitada
6. **Validação de Data de Referência**: O job requer um parâmetro obrigatório "dataReferencia" no formato yyyy-MM-dd
7. **Truncamento de Agência**: Códigos de agência são truncados para no máximo 4 caracteres numéricos
8. **Definição Automática de Tipo de Pessoa**: Se não informado, define como Jurídica (J) para documentos com 14 dígitos, Física (F) caso contrário
9. **Valores Default para Remetente**: Se dados do remetente forem nulos, utiliza valores padrão (tipo conta "CC", conta "00000", agência "000")
10. **Exclusão de Transações Legadas Já Processadas**: Filtra transações onde CdLancamentoSPAG é NULL para evitar reprocessamento

---

## 6. Relação entre Entidades

**Entidade Principal:**
- **ConsolidadoTransacoes**: Representa um lançamento financeiro da tabela TBL_LANCAMENTO

**DTOs e Objetos de Transferência:**
- **ConsolidadoTransacoesDTO**: DTO intermediário para transporte de dados entre camadas
- **LancamentosQueryProjection**: Interface de projeção para queries nativas
- **TransacaoPagamentoProcessada** (Avro): Objeto final publicado no Kafka

**Relacionamentos:**
- ConsolidadoTransacoes é mapeado para ConsolidadoTransacoesDTO via ConsolidadoTransacaoMapper
- ConsolidadoTransacoesDTO é transformado em TransacaoPagamentoProcessada (Avro) para publicação
- TransacaoPagamentoProcessada contém objetos aninhados: Remetente e Favorecido

**Fluxo de Dados:**
```
TBL_LANCAMENTO (Sybase) 
  → LancamentosQueryProjection 
  → ConsolidadoTransacoesDTO 
  → TransacaoPagamentoProcessada (Avro) 
  → Kafka Topic
```

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBPGF_TES.dbo.TBL_LANCAMENTO | Tabela | SELECT | Tabela principal de lançamentos financeiros do sistema PGFT |
| DBITP.dbo.TBL_CAIXA_ENTRADA_SPB | Tabela | SELECT | Tabela de entrada SPB, utilizada em JOIN para obter dados complementares (sistema origem, histórico, protocolo cliente, código de barras) |

**Observação**: A query utiliza INNER JOIN entre TBL_CAIXA_ENTRADA_SPB e TBL_LANCAMENTO através da coluna Cod_Protocolo.

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O componente realiza apenas leitura de dados, sem operações de INSERT, UPDATE ou DELETE.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | Leitura | /usr/etc/log/ (container) | Arquivo de configuração de logs carregado em runtime conforme ambiente |
| application.yml | Leitura | src/main/resources/ | Arquivo de configuração principal da aplicação |
| application-local.yml | Leitura | src/main/resources/ | Configurações específicas para ambiente local |
| kafkaschema-spag-base-transacao-processada.avsc | Leitura | src/main/resources/avro/ | Schema Avro utilizado para serialização de mensagens Kafka |

**Observação**: Não há geração de arquivos físicos. A saída do processamento é publicada em tópico Kafka.

---

## 10. Filas Lidas

Não se aplica. O componente não consome mensagens de filas, apenas produz.

---

## 11. Filas Geradas

| Nome da Fila/Tópico | Tecnologia | Descrição |
|---------------------|------------|-----------|
| spag-base-transacao-pagamento-processada | Apache Kafka (Confluent Cloud) | Tópico Kafka onde são publicadas as transações de pagamento processadas no formato Avro |

**Configurações:**
- **Serializer**: KafkaAvroSerializer (Confluent)
- **Schema Registry**: Confluent Schema Registry (URLs específicas por ambiente)
- **Autenticação**: SASL_SSL com credenciais via API Key/Secret
- **Chave da mensagem**: cdIdentificadorPagamento (código do pagamento)
- **Tipo de evento**: AVRO
- **TraceId**: Propagado via MDC para rastreabilidade

---

## 12. Integrações Externas

| Sistema/API | Tipo | Descrição |
|-------------|------|-----------|
| **sboot-spag-base-atom-consolidado-transacoes** | API REST (Feign Client) | API interna para obter o código do último lançamento processado (endpoint: GET /v1/legado/max-lancamento) |
| **API Gateway BV** | OAuth2 Token Provider | Serviço de autenticação para obtenção de tokens JWT (endpoint: /auth/oauth/v2/token-jwt) |
| **Confluent Schema Registry** | Schema Registry | Serviço de gerenciamento e validação de schemas Avro |
| **Confluent Kafka Cluster** | Message Broker | Cluster Kafka para publicação de eventos |
| **ConfigCat** | Feature Toggle Service | Serviço de gerenciamento de feature flags |

**Observação**: Todas as integrações utilizam autenticação OAuth2 com client credentials flow.

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões do Spring Batch (Reader/Processor/Writer)
- Separação clara de responsabilidades em camadas (config, domain, service, repository, mapper, infrastructure)
- Uso adequado de DTOs e entidades separadas
- Boa cobertura de testes unitários (todas as classes principais possuem testes)
- Uso de Lombok para reduzir boilerplate
- Configuração externalizada por ambiente (infra.yml)
- Implementação de Feature Toggles para controle de funcionalidades
- Logs estruturados em JSON para ambientes produtivos
- Tratamento de exceções customizado
- Uso de projeções JPA para otimizar queries
- Documentação README.md presente e detalhada

**Pontos de Melhoria:**
- Algumas classes com muitas responsabilidades (ex: ConsolidadoTransacaoMapper com lógica de negócio)
- Constantes espalhadas em múltiplas classes (ConstantsFile, QueriesFile)
- Query SQL nativa muito extensa e complexa poderia ser quebrada ou documentada melhor
- Falta de validação mais robusta de parâmetros de entrada no Reader
- Alguns métodos poderiam ter JavaDoc mais detalhado
- Tratamento de erro genérico em alguns pontos (catch Exception)
- Configuração de datasources poderia usar um padrão mais moderno (HikariCP explícito)

O código demonstra maturidade técnica e segue boas práticas de desenvolvimento, com espaço para pequenas melhorias em organização e documentação.

---

## 14. Observações Relevantes

1. **Processamento Batch Agendado**: A aplicação é executada como job batch sob demanda (não há scheduler interno). O parâmetro "dataReferencia" deve ser fornecido externamente.

2. **Múltiplos Datasources**: Utiliza H2 em memória para metadados do Spring Batch e Sybase para dados de negócio (PGFT).

3. **Estratégia de Layering Docker**: O Dockerfile utiliza estratégia de multi-layer para otimizar cache de builds (layers.xml define 13 camadas diferentes).

4. **Ambientes Suportados**: DES, UAT e PRD com configurações específicas em infra.yml.

5. **Segurança**: 
   - Autenticação OAuth2 JWT
   - Secrets gerenciados via cofre (Vault)
   - Comunicação SASL_SSL com Kafka

6. **Observabilidade**:
   - Logs estruturados JSON
   - Métricas Prometheus
   - TraceId para correlação de logs
   - Health checks via Actuator

7. **Chunk Size**: Processamento em chunks de 100 registros por vez.

8. **Compatibilidade**: Utiliza charset ISO-1 para conexão Sybase devido a requisitos legados.

9. **Versionamento**: Versão atual 0.4.0, seguindo semantic versioning.

10. **Pipeline CI/CD**: Integrado com Jenkins (jenkins.properties) e Google Cloud Platform.

11. **Dependências Internas**: Utiliza bibliotecas proprietárias do Banco Votorantim (atle-base, arqt-base).

12. **Tratamento de Dados Nulos**: Implementa valores default para campos obrigatórios do remetente quando dados não estão disponíveis.