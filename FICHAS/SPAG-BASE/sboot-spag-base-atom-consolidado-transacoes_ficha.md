# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de consolidação de transações de pagamento desenvolvido em Java com Spring Boot. O componente atua como um serviço atômico responsável por consumir eventos de transações de pagamento processadas via Kafka, consolidar essas informações em banco de dados MySQL e expor endpoints REST para consulta de dados consolidados. O sistema processa diferentes tipos de liquidação (PIX, TED, Boletos, Tributos, TEF, Débitos Veiculares) e mantém consolidações por tipo de operação (entrada/saída) e status (efetivado, pendente, rejeitado).

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal de inicialização da aplicação Spring Boot |
| `TransacaoPagamentoConsumer` | Listener Kafka que consome eventos de transações processadas |
| `TransacaoConsolidadoService` | Serviço principal que processa eventos e gerencia consolidações |
| `TransacaoAnaliticoService` | Gerencia operações sobre detalhes analíticos de transações |
| `PessoaTransacaoService` | Gerencia dados de pessoas (favorecidos e remetentes) |
| `ConsolidadoTransacoesApiDelegateImpl` | Implementação dos endpoints REST da API |
| `TbTransacaoConsolidado` | Entidade JPA representando dados consolidados |
| `TbDetalheTransacaoPagamento` | Entidade JPA representando detalhes analíticos de pagamentos |
| `TbDadoPessoaTransacao` | Entidade JPA representando dados de pessoas envolvidas |
| `ConsolidadoTransacoesConfiguration` | Configurações do Kafka e beans do sistema |
| `ExceptionHandlerConfiguration` | Tratamento centralizado de exceções |
| `ConsolidadoTransacaoMapper` | Mapeamento entre DTOs e entidades de consolidado |
| `TbDetalheTransacaoPagamentoMapper` | Mapeamento entre eventos Avro e entidades de detalhe |

---

## 3. Tecnologias Utilizadas

- **Framework Principal**: Spring Boot 3.x (baseado no parent `pom-atle-base-sboot-atom-parent` versão 3.5.0)
- **Linguagem**: Java 21
- **Persistência**: 
  - Spring Data JPA
  - Hibernate
  - MySQL Connector (mysql-connector-j)
- **Mensageria**: 
  - Apache Kafka
  - Confluent Kafka Avro Serializer (versão 7.7.1)
  - Spring Kafka
- **Mapeamento de Objetos**: MapStruct 1.5.5.Final
- **Documentação API**: 
  - OpenAPI 3.0
  - Swagger UI (SpringDoc)
- **Logging**: 
  - Logback
  - Logback JSON (versão 0.1.5)
- **Utilitários**:
  - Lombok
  - Apache Commons Text 1.12.0
  - Joda Time 2.14.0
- **Containerização**: Docker
- **Infraestrutura**: Google Cloud Platform (GCP)
- **Build**: Maven 3.8+
- **Testes**: JUnit 5, Mockito
- **Observabilidade**: Spring Actuator, Micrometer, Prometheus

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/transactions-report` | `ConsolidadoTransacoesApiDelegateImpl` | Retorna dados consolidados de transações por período, documento, conta e tipo de liquidação |
| GET | `/v1/legado/max-lancamento` | `ConsolidadoTransacoesApiDelegateImpl` | Retorna o maior código de lançamento legado para uma data de referência específica |

**Parâmetros do endpoint `/v1/transactions-report`:**
- `dtInicial` (obrigatório): Data inicial do período
- `dtFinal` (obrigatório): Data final do período
- `nuDocumento` (obrigatório): Número do documento (CPF/CNPJ)
- `nuConta` (opcional): Número da conta corrente
- `cdBanco` (opcional): Código do banco
- `tpLiquidacao` (opcional): Lista de tipos de liquidação (PIX, TED, BOLETOS, TRIBUTOS, TEF, DEBITOS_VEICULARES)

**Parâmetros do endpoint `/v1/legado/max-lancamento`:**
- `dtReferencia` (opcional): Data de referência para busca

---

## 5. Principais Regras de Negócio

1. **Consolidação de Transações**: O sistema consolida transações agrupando por banco, conta, tipo de liquidação, tipo de entrada/saída e status, acumulando valores e quantidades.

2. **Processamento de Eventos Kafka**: Ao receber um evento de transação processada, o sistema:
   - Verifica se a transação já existe (por `cdIdentificadorPagamento`)
   - Se existir e o status mudou de Pendente para Efetivado/Rejeitado, decrementa o consolidado anterior e incrementa o novo
   - Se não existir, cria novo registro analítico e incrementa o consolidado correspondente

3. **Tratamento Especial para TEF**: Transações do tipo TEF consolidam tanto para favorecido quanto para remetente separadamente.

4. **Validação de Período**: Consultas de dados consolidados não podem exceder 30 dias e a data inicial não pode ser posterior à data final.

5. **Gestão de Pessoas**: O sistema busca ou cria registros de favorecidos e remetentes automaticamente, evitando duplicações através de busca por banco, conta, agência e documento.

6. **Sanitização de Strings Avro**: Todos os campos string dos eventos Avro são automaticamente trimados para remover espaços em branco.

7. **Validação de Código de Barras**: Códigos de barra/digitação com mais de 47 caracteres são descartados (setados como null).

8. **Retry com Backoff**: O sistema implementa retry com backoff exponencial para falhas de processamento Kafka (máximo 10 tentativas) e para deadlocks de banco de dados (máximo 3 tentativas).

9. **Lock Pessimista**: Utiliza lock pessimista (PESSIMISTIC_WRITE) ao buscar consolidados para evitar condições de corrida em ambientes concorrentes.

10. **Auditoria**: Todos os registros mantêm informações de auditoria (data inclusão, alteração, login, flag ativo, data ingestão).

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **TbTransacaoConsolidado**: Representa dados consolidados de transações
  - Relacionamento ManyToOne com `TbDadoPessoaTransacao` (pessoa associada ao consolidado)
  - Contém: tipo liquidação, tipo entrada/saída, status, quantidade total, valor total, data referência

- **TbDetalheTransacaoPagamento**: Representa detalhes analíticos de cada pagamento
  - Referencia `TbDadoPessoaTransacao` via `cdDadoFavorecido` (pode ser null)
  - Referencia `TbDadoPessoaTransacao` via `cdDadoRemetente`
  - Contém: identificador pagamento, data, tipo liquidação, status, valor, códigos de transação/evento/finalidade, histórico, protocolo, códigos de barra

- **TbDadoPessoaTransacao**: Representa dados de pessoas (favorecidos/remetentes)
  - Contém: banco, conta, tipo conta, agência, nome banco, CPF/CNPJ, tipo pessoa, nome pessoa

- **AuditoriaBase**: Embeddable utilizado em todas as entidades
  - Contém: data inclusão, data alteração, login, flag ativo, data ingestão

**Relacionamentos:**
- Um consolidado está associado a uma pessoa (1:N)
- Um detalhe de transação referencia um favorecido e um remetente (N:1 para cada)
- Todas as entidades incorporam dados de auditoria

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbTransacaoConsolidado | tabela | SELECT | Leitura de dados consolidados de transações para consultas e verificação de existência |
| TbDetalheTransacaoPagamento | tabela | SELECT | Busca de detalhes de transações por ID de pagamento e busca do maior código de lançamento legado por data |
| TbDadoPessoaTransacao | tabela | SELECT | Busca de dados de pessoas por ID ou por combinação de banco, conta, agência e documento |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbTransacaoConsolidado | tabela | INSERT/UPDATE | Criação de novos consolidados e atualização de valores/quantidades consolidadas |
| TbDetalheTransacaoPagamento | tabela | INSERT/UPDATE | Inserção de novos detalhes de transações e atualização de status de transações existentes |
| TbDadoPessoaTransacao | tabela | INSERT | Criação de novos registros de favorecidos e remetentes quando não existem |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | leitura | Configuração de logging | Arquivo de configuração de logs (diferentes versões por ambiente: des, uat, prd, local) |
| application.yml | leitura | Spring Boot | Arquivo principal de configuração da aplicação |
| application-local.yml | leitura | Spring Boot | Configurações específicas para perfil local |
| sboot-spag-base-atom-consolidado-transacoes.yaml | leitura | OpenAPI Generator | Contract-first da API REST |
| kafkaschema-spag-base-transacao-pagamento-processada.avsc | leitura | Avro Maven Plugin | Schema Avro para eventos de transações processadas |
| layers.xml | leitura | Spring Boot Layered JAR | Configuração de camadas para otimização de imagem Docker |

---

## 10. Filas Lidas

**Tópico Kafka:**
- **Nome**: `spag-base-transacao-pagamento-processada`
- **Formato**: Avro (schema registry Confluent)
- **Consumer Group**: `sboot-spag-base-atom-consolidado-transacoes`
- **Classe Consumidora**: `TransacaoPagamentoConsumer`
- **Schema**: `TransacaoPagamentoProcessada` (definido em `kafkaschema-spag-base-transacao-pagamento-processada.avsc`)
- **Configuração**: 
  - Ack Mode: MANUAL_IMMEDIATE
  - Retry: 10 tentativas com backoff exponencial (inicial 30s, multiplicador 1.5, máximo 300s)
  - Commit Recovered: true

**Ambientes:**
- DES: `pkc-z70q7.southamerica-east1.gcp.confluent.cloud:9092`
- UAT: `pkc-kymnv.southamerica-east1.gcp.confluent.cloud:9092`
- PRD: `pkc-9vdn5.southamerica-east1.gcp.confluent.cloud:9092`

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Confluent Schema Registry | API REST | Registro e validação de schemas Avro para mensagens Kafka |
| MySQL Cloud SQL (GCP) | Banco de Dados | Persistência de dados consolidados e analíticos |
| API Gateway BV | Autenticação/Autorização | Validação de tokens JWT via JWKS |

**Detalhes de Integração:**

1. **Confluent Schema Registry**:
   - DES: `https://psrc-j98yq.us-central1.gcp.confluent.cloud`
   - UAT/PRD: `https://psrc-30dr2.us-central1.gcp.confluent.cloud`
   - Autenticação: Basic Auth via API Key/Secret

2. **MySQL Cloud SQL**:
   - DES: `gcmysatdes24.psc.cloudsql:3306/SPAGTransacaoConsolidado`
   - UAT: `gcmysatuat24.psc.cloudsql:3306/SPAGTransacaoConsolidado`
   - PRD: `gcmysatprd24.psc.cloudsql:3306/SPAGTransacaoConsolidado`
   - Usuário: `SPAGTransacaoConsolidado_APPL`

3. **API Gateway**:
   - DES: `https://apigatewaydes.bvnet.bv`
   - UAT: `https://apigatewayuat.bvnet.bv`
   - PRD: `https://apigateway.bvnet.bv`
   - JWKS URL para validação de tokens JWT

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões de microserviços atômicos
- Separação clara de responsabilidades (service, repository, mapper, rest)
- Uso adequado de padrões como MapStruct para mapeamento de objetos
- Implementação robusta de retry e tratamento de erros
- Boa cobertura de testes unitários (classes de teste para todas as camadas)
- Uso de locks pessimistas para evitar condições de corrida
- Configuração adequada de logging estruturado (JSON)
- Documentação OpenAPI bem definida
- Uso de DTOs e Projections para otimização de queries
- Tratamento centralizado de exceções

**Pontos de Melhoria:**
- Algumas classes de serviço estão extensas (ex: `TransacaoConsolidadoService` com múltiplas responsabilidades)
- Poderia haver mais uso de constantes para strings literais repetidas
- Alguns métodos poderiam ser quebrados em métodos menores para melhor legibilidade
- Falta documentação JavaDoc em algumas classes e métodos públicos
- Alguns testes poderiam ter nomes mais descritivos seguindo padrão BDD (Given/When/Then)
- Configurações hardcoded em alguns lugares poderiam ser externalizadas

O código demonstra maturidade técnica e boas práticas de desenvolvimento, com espaço para pequenos refinamentos que elevariam ainda mais a qualidade.

---

## 14. Observações Relevantes

1. **Infraestrutura como Código**: O projeto utiliza arquivo `infra.yml` para gerenciar configurações por ambiente (DES, UAT, PRD), incluindo secrets, configmaps, probes de saúde e recursos computacionais.

2. **Multi-layer Docker**: Implementa estratégia de camadas Docker otimizada para reduzir tempo de build e tamanho de imagens, separando dependências comuns, específicas e código da aplicação.

3. **Observabilidade**: Expõe métricas via Actuator na porta 9090 (separada da porta de aplicação 8080) com endpoints de health, metrics e prometheus.

4. **Segurança**: 
   - Autenticação via JWT com validação de issuer e JWKS
   - Endpoints públicos configuráveis (swagger, actuator)
   - Cookies com flags httpOnly e secure

5. **Profiles**: Suporta múltiplos profiles (local, des, uat, prd) com configurações específicas por ambiente.

6. **Retry Strategies**: Implementa duas estratégias de retry:
   - Kafka: 10 tentativas com backoff exponencial
   - JPA: 3 tentativas com backoff para deadlocks

7. **Sanitização de Logs**: Utiliza `LogUtils.sanitizeMessage()` para escapar caracteres especiais e prevenir log injection.

8. **Versionamento de API**: API versionada com prefixo `/v1/`.

9. **Compatibilidade**: Código preparado para diferentes versões do Spring Kafka através de uso de reflection em testes.

10. **CI/CD**: Configurado para Jenkins com propriedades específicas (`jenkins.properties`) e suporte a geração de releases automáticas.

11. **Lombok**: Configurado para adicionar anotação `@Generated` em código gerado, facilitando análise de cobertura de testes.

12. **Validação de Dados**: Utiliza Bean Validation (Jakarta Validation) para validação de entrada de dados nos endpoints.