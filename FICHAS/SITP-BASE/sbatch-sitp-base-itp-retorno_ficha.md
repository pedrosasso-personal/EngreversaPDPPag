# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sbatch-sitp-base-itp-retorno** é um serviço de processamento em lote (batch) desenvolvido em Spring Batch para processar pagamentos. O sistema realiza a leitura de dados de pagamentos a partir de um arquivo CSV, processa essas informações e persiste os dados em banco de dados. Trata-se de um componente stateful que segue o padrão arquitetural Atlante do Banco Votorantim, executando jobs batch com processamento chunk-oriented (lotes de 100 registros).

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal que inicializa a aplicação Spring Boot |
| `JobConfig` | Configuração do job batch, definindo steps e fluxo de execução |
| `Reader` | Responsável pela leitura do arquivo CSV de pagamentos |
| `Processor` | Processa cada registro de pagamento lido (implementa transformações/validações) |
| `Writer` | Persiste os pagamentos processados no banco de dados via repository |
| `Pagamento` | Entidade de domínio representando um pagamento (JPA Entity) |
| `TemplateRepository` | Interface de repositório JPA para operações de persistência |
| `ItemProcessorListener` | Listener que monitora o ciclo de vida do processamento de itens |

---

## 3. Tecnologias Utilizadas

- **Spring Boot** (framework base)
- **Spring Batch** (processamento em lote)
- **Spring Data JPA** (persistência de dados)
- **Maven** (gerenciamento de dependências)
- **H2 Database** (banco em memória para ambiente local)
- **MySQL Connector** (driver para MySQL)
- **Logback** (logging com suporte a JSON)
- **Docker** (containerização - OpenJDK 11 com OpenJ9)
- **Actuator** (monitoramento e health checks)
- **Swagger/OpenAPI** (documentação de APIs)
- **Lombok** (redução de boilerplate)
- **Java 11+**

---

## 4. Principais Endpoints REST

Não se aplica. Este é um componente batch que não expõe endpoints REST para processamento de negócio. Apenas endpoints de infraestrutura do Actuator estão disponíveis:

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | /actuator/health | Health check da aplicação |
| GET | /actuator/info | Informações da aplicação |
| GET | /actuator/metrics | Métricas da aplicação |
| GET | /actuator/prometheus | Métricas no formato Prometheus |

---

## 5. Principais Regras de Negócio

Com base no código fornecido, as regras de negócio específicas não estão explicitamente implementadas no `Processor`, que apenas registra logs dos dados. O sistema está estruturado como template/base para:

- Leitura de arquivo CSV com estrutura: nome, email, data_nascimento, idade, id
- Processamento em chunks de 100 registros por vez
- Persistência de entidades Pagamento no banco de dados
- Tratamento de erros durante o processamento com logging

**Nota:** O processador atual é um template básico que pode ser estendido com regras de validação, transformação e enriquecimento de dados conforme necessidades específicas.

---

## 6. Relação entre Entidades

**Entidade Principal:**
- `Pagamento`: Entidade JPA mapeada para a tabela `PAGAMENTO`
  - Atributos: id (PK, auto-incremento), name, email, data, age
  - Estratégia de geração de ID: SEQUENCE

**Relacionamentos:** Não há relacionamentos entre entidades no modelo atual. A entidade Pagamento é independente.

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| PAGAMENTO | tabela | SELECT | Leitura implícita pelo Spring Batch para controle de execução de jobs (metadata tables) |
| BATCH_JOB_INSTANCE | tabela | SELECT | Tabela de metadados do Spring Batch para instâncias de jobs |
| BATCH_JOB_EXECUTION | tabela | SELECT | Tabela de metadados do Spring Batch para execuções de jobs |
| BATCH_STEP_EXECUTION | tabela | SELECT | Tabela de metadados do Spring Batch para execuções de steps |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| PAGAMENTO | tabela | INSERT | Inserção de novos registros de pagamento processados do CSV |
| BATCH_JOB_INSTANCE | tabela | INSERT | Registro de novas instâncias de jobs pelo Spring Batch |
| BATCH_JOB_EXECUTION | tabela | INSERT/UPDATE | Registro e atualização de execuções de jobs |
| BATCH_STEP_EXECUTION | tabela | INSERT/UPDATE | Registro e atualização de execuções de steps |
| BATCH_JOB_EXECUTION_CONTEXT | tabela | INSERT/UPDATE | Contexto de execução dos jobs |
| BATCH_STEP_EXECUTION_CONTEXT | tabela | INSERT/UPDATE | Contexto de execução dos steps |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| spreadsheet.csv | leitura | `src/main/resources/` / Classe `Reader` | Arquivo CSV contendo dados de pagamentos (nome, email, data, idade, id) |
| logback-spring.xml | leitura | `src/main/resources/` e `/usr/etc/log/` | Arquivo de configuração de logs (formato JSON em produção) |
| application.yml | leitura | `src/main/resources/` | Arquivo de configuração da aplicação |
| application-local.yml | leitura | `src/main/resources/` | Configurações específicas do ambiente local |

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas (JMS, Kafka, RabbitMQ, etc.).

---

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas.

---

## 12. Integrações Externas

Não se aplica. O sistema não possui integrações com APIs externas, serviços externos ou sistemas de terceiros. Opera de forma isolada processando arquivos locais e persistindo em banco de dados.

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Estrutura bem organizada seguindo padrões do Spring Batch
- Uso adequado de anotações e injeção de dependências
- Separação clara de responsabilidades (Reader, Processor, Writer)
- Configuração de logs estruturados (JSON) para ambientes produtivos
- Uso de Lombok para reduzir boilerplate
- Configuração de health checks e monitoramento
- Dockerização adequada com otimizações de memória JVM

**Pontos de Melhoria:**
- O `Processor` está praticamente vazio, apenas logando dados sem implementar lógica de negócio real
- Falta tratamento de exceções específico e estratégias de retry
- Ausência de testes unitários e de integração nos arquivos fornecidos
- Falta validação dos dados lidos do CSV
- Configurações hardcoded em alguns pontos (chunk size de 100)
- Documentação inline limitada (poucos comentários explicativos)
- Falta configuração de skip policies e error handling robusto
- Ausência de métricas customizadas de negócio

O código serve bem como template/base, mas necessita de implementações adicionais para um cenário produtivo real.

---

## 14. Observações Relevantes

1. **Ambiente Local**: Utiliza H2 em memória com console web disponível em `/h2-console`

2. **Segurança**: Configurado com OAuth2 Resource Server usando JWT (JWKS) para autenticação em ambientes não-locais

3. **Portas**: 
   - Aplicação: 8080
   - Actuator/Management: 9090

4. **Profiles**: Suporta múltiplos ambientes (local, des, uat, prd) com configurações específicas

5. **Inicialização do Schema**: Em ambiente local, o Spring Batch inicializa automaticamente as tabelas de metadados (`jdbc.initialize-schema: always`)

6. **Logging Assíncrono**: Utiliza appender assíncrono com fila de 500 mensagens para melhor performance

7. **Infraestrutura como Código**: Possui configuração completa de deployment (infra.yml) com probes de liveness e readiness

8. **Arquivo CSV de Exemplo**: Contém 1000 registros de teste com dados fictícios de pessoas

9. **Framework Atlante**: Componente desenvolvido seguindo padrões do framework proprietário do Banco Votorantim

10. **Job Incremental**: Utiliza `RunIdIncrementer` permitindo múltiplas execuções do mesmo job