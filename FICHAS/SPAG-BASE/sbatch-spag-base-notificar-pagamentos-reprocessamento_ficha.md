# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de processamento em lote (Spring Batch) responsável por identificar e reprocessar lançamentos de pagamentos pendentes no sistema SPAG (Sistema de Pagamentos). O componente consulta lançamentos que estão em estados específicos (pendentes, em processamento, etc.) e que não foram atualizados nos últimos 40 minutos, publicando essas informações em um tópico Kafka para processamento downstream. O sistema utiliza Feature Toggles para controle de execução e classificação de tipos de transação (débitos veiculares e tributos).

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal de inicialização do Spring Boot Batch |
| `JobConfig` | Configuração do job batch, datasources (H2 e SQL Server), transaction managers e steps |
| `Reader` | ItemReader que busca lançamentos pendentes através do `LancamentoService` |
| `Processor` | ItemProcessor que converte `TransacaoPagamentoDTO` em `TransacaoPagamentoProcessada` |
| `Writer` | ItemWriter que publica mensagens no Kafka através do repositório |
| `LancamentoService` | Serviço de negócio para buscar lançamentos pendentes no banco de dados |
| `LancamentoRepository` | Repositório JPA para acesso à tabela `TbLancamento` |
| `TransacaoPagamentoMapper` | Mapper MapStruct para conversão entre DTOs e entidades Avro |
| `EnvioLancamentoPendenteRepositoryImpl` | Implementação que publica mensagens no Kafka |
| `FeatureToggleService` | Serviço para gerenciamento de feature flags (ConfigCat) |
| `FeatureToggleLoader` | Carrega configurações de feature toggles na inicialização |
| `KafkaConfiguration` | Configuração do produtor Kafka e schema registry |
| `Lancamento` | Entidade JPA representando a tabela `TbLancamento` |
| `LancamentoPessoa` | Entidade JPA representando a tabela `TbLancamentoPessoa` |

---

## 3. Tecnologias Utilizadas

- **Java 21**
- **Spring Boot 3.x** (via parent `pom-atle-base-sbatch-parent:3.3.2`)
- **Spring Batch** - Framework de processamento em lote
- **Spring Data JPA / Hibernate** - Persistência e ORM
- **Apache Kafka** - Mensageria (Confluent Cloud)
- **Apache Avro** - Serialização de mensagens (schema registry)
- **MapStruct** - Mapeamento de objetos
- **SQL Server** - Banco de dados principal (DBSPAG)
- **H2 Database** - Banco em memória para metadados do Spring Batch
- **Lombok** - Redução de boilerplate
- **ConfigCat** - Feature Toggle (via `sbootlib-arqt-base-feature-toggle`)
- **Maven** - Gerenciamento de dependências
- **Docker** - Containerização
- **Logback** - Logging
- **Actuator** - Monitoramento e health checks

---

## 4. Principais Endpoints REST

Não se aplica. Este é um componente batch que não expõe endpoints REST. A execução é iniciada via job do Spring Batch.

---

## 5. Principais Regras de Negócio

1. **Seleção de Lançamentos Pendentes**: Busca lançamentos com data de inclusão igual à data de referência (parâmetro do job), que estejam em status específicos (0, 1, 7, 11, 12), com códigos de liquidação válidos (1, 31, 32, 22, 59, 60) e que não tenham sido atualizados nos últimos 40 minutos.

2. **Controle por Feature Toggle**: A execução do batch é controlada pela feature flag `ft_boolean_publicacao_transacao_consolidado`. Se desabilitada, o processamento é interrompido.

3. **Classificação de Tipo de Liquidação**: O sistema classifica transações em diferentes tipos (TEF, TED, BOLETOS, TRIBUTOS, DEBITOS_VEICULARES) baseado no código de liquidação e código de transação, utilizando listas configuradas via Feature Toggles.

4. **Mapeamento de Tipo de Entrada/Saída**: Converte o tipo de lançamento ("E" para Entrada, "S" para Saída).

5. **Processamento em Chunks**: Processa lançamentos em lotes de 1 registro por vez.

6. **Publicação Kafka**: Cada lançamento processado é publicado individualmente no tópico Kafka com o identificador do pagamento como chave.

7. **Rastreabilidade**: Mantém traceId (MDC) nas mensagens Kafka para correlação de logs.

---

## 6. Relação entre Entidades

**Entidades JPA:**

- `Lancamento` (TbLancamento) - Entidade principal representando um lançamento de pagamento
  - Chave primária: `cdLancamento`
  - Relacionamento implícito com `LancamentoPessoa` via `cdLancamento`

- `LancamentoPessoa` (TbLancamentoPessoa) - Entidade contendo informações de pessoas (remetente/favorecido)
  - Chave primária: `cdLancamento`
  - Relacionamento 1:1 com `Lancamento`

**DTOs:**

- `TransacaoPagamentoDTO` - DTO principal contendo dados consolidados do lançamento
  - Contém: `FavorecidoDTO` (dados do favorecido)
  - Contém: `RemetenteDTO` (dados do remetente)

**Avro Schema:**

- `TransacaoPagamentoProcessada` - Mensagem Kafka
  - Contém: `Favorecido` (nested record)
  - Contém: `Remetente` (nested record)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| DBSPAG.dbo.TbLancamento | Tabela | SELECT | Tabela principal de lançamentos de pagamentos |
| DBSPAG.dbo.TbLancamentoPessoa | Tabela | SELECT | Tabela com informações de pessoas (remetente/favorecido) relacionadas aos lançamentos |

**Query principal:** Consulta com JOIN entre `TbLancamentoPessoa` e `TbLancamento` filtrando por data de referência, status, código de liquidação e tempo desde última atualização (>= 40 minutos).

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema apenas realiza leituras do banco de dados DBSPAG. As tabelas do Spring Batch (metadados) são gerenciadas automaticamente pelo framework no banco H2 em memória.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | Leitura | Configuração de logging | Arquivo de configuração de logs (diferentes versões por ambiente) |
| application.yml | Leitura | Spring Boot | Arquivo de configuração principal da aplicação |
| application-local.yml | Leitura | Spring Boot | Configurações específicas para ambiente local |
| kafkaschema-spag-base-transacao-pagamento-processada.avsc | Leitura | Maven Avro Plugin | Schema Avro para geração de classes de mensagens Kafka |

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas, apenas produz.

---

## 11. Filas Geradas

| Nome da Fila/Tópico | Tecnologia | Breve Descrição |
|---------------------|------------|-----------------|
| spag-base-transacao-pagamento-processada | Apache Kafka (Confluent Cloud) | Tópico para publicação de transações de pagamento processadas. Mensagens no formato Avro com schema registry. Chave: identificador do pagamento (cdLancamento). |

**Configurações:**
- Bootstrap servers: Configurado por ambiente via variável `KAFKA_HOST`
- Schema Registry: Configurado via `KAFKA_SCHEMA_REGISTRY`
- Autenticação: SASL/PLAIN com credenciais via variáveis de ambiente
- Protocolo: SASL_SSL

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Confluent Cloud Kafka | Mensageria | Plataforma de streaming para publicação de eventos de pagamento |
| Confluent Schema Registry | Schema Management | Gerenciamento de schemas Avro para mensagens Kafka |
| ConfigCat | Feature Toggle | Serviço de gerenciamento de feature flags para controle de funcionalidades |
| SQL Server (DBSPAG) | Banco de Dados | Base de dados principal contendo lançamentos de pagamento |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões Spring Batch (Reader/Processor/Writer)
- Uso adequado de DTOs e separação de camadas (domain, service, repository, infrastructure)
- Implementação de MapStruct para mapeamento de objetos, reduzindo código manual
- Uso de Lombok para redução de boilerplate
- Tratamento de exceções customizado (`NotificarPagamentoException`)
- Configuração adequada de múltiplos datasources (H2 para batch metadata, SQL Server para dados)
- Uso de Feature Toggles para controle de execução e configurações dinâmicas
- Logging estruturado com MDC para rastreabilidade
- Uso de records Java para DTOs imutáveis
- Schema Avro bem documentado com descrições dos campos

**Pontos de Melhoria:**
- Falta de tratamento de retry em caso de falha na publicação Kafka
- Chunk size de 1 pode impactar performance (poderia ser configurável)
- Ausência de testes unitários nos arquivos analisados (marcados como NAO_ENVIAR)
- Query SQL hardcoded em constante (poderia estar em arquivo separado ou usar Criteria API)
- Falta de validações mais robustas nos DTOs
- Documentação JavaDoc ausente em várias classes
- Configuração de transação poderia ser mais explícita no Writer
- Falta de métricas customizadas para monitoramento do batch

O código demonstra boas práticas de desenvolvimento, uso adequado de frameworks modernos e organização clara, mas há espaço para melhorias em aspectos de resiliência, performance e documentação.

---

## 14. Observações Relevantes

1. **Execução Agendada**: O README menciona uma "malha responsável por chamar o batch - PROC_LANC_PENDENTE", indicando que há um scheduler externo que dispara a execução.

2. **Parâmetro de Execução**: O job recebe um parâmetro `dataReferencia` que define a data de inclusão dos lançamentos a serem processados. Se não informado, utiliza a data atual.

3. **Ambiente Multi-Cloud**: Configurado para Google Cloud Platform (GCP) com suporte a múltiplos ambientes (des, uat, prd).

4. **Segurança**: Implementa OAuth2 JWT para autenticação (embora seja um batch, mantém a estrutura do framework Atlante).

5. **Monitoramento**: Expõe endpoints Actuator na porta 9090 para health checks e métricas.

6. **Containerização**: Utiliza imagem base customizada do Banco Votorantim com Java 21 e suporte a multi-layer.

7. **Infraestrutura como Código**: Possui arquivo `infra.yml` com configurações para deploy automatizado via pipeline Jenkins.

8. **Tempo de Processamento**: Considera apenas lançamentos não atualizados há pelo menos 40 minutos, evitando reprocessamento de transações recentes.

9. **Feature Toggles Dinâmicos**: Utiliza ConfigCat para gerenciar listas de códigos de transação (débitos veiculares e tributos) de forma dinâmica, sem necessidade de redeploy.

10. **Finalização Automática**: A aplicação executa `System.exit()` após conclusão do job, comportamento típico de aplicações batch.