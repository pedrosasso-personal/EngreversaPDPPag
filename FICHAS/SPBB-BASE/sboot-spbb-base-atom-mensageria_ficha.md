# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-spbb-base-atom-mensageria** é um serviço atômico (microserviço) desenvolvido em Java com Spring Boot, responsável por gerenciar o processamento e conversão de mensagens do Sistema de Pagamentos Brasileiro (SPB). O sistema atua como intermediário entre sistemas internos e o SPB, realizando conversão de mensagens entre formatos JSON e XML, controle de movimentos financeiros, gestão de circuit breakers para contingência e auditoria de transações. Ele consome mensagens via Kafka, persiste dados em MySQL e expõe APIs REST para consulta e gestão de movimentos.

---

## 2. Principais Classes e Responsabilidades

| Classe/Componente | Responsabilidade |
|-------------------|------------------|
| **Application** | Classe principal de inicialização da aplicação Spring Boot |
| **KafkaConsumer** | Listener Kafka que consome mensagens de status de envio do SPB |
| **ConversaoMensagemService** | Serviço responsável pela conversão de mensagens entre JSON/XML e processamento de recebimento/envio |
| **MovimentoService** | Gerencia operações de CRUD e lógica de negócio relacionadas a movimentos financeiros |
| **CircuitBreakService** | Controla a ativação/desativação de circuit breakers para contingência de envio de mensagens |
| **FeatureToggleService** | Gerencia feature flags para habilitar/desabilitar funcionalidades dinamicamente |
| **NSUService** | Gera números sequenciais únicos (NSU) para identificação de mensagens |
| **MovimentoRepository** | Interface JDBI para acesso aos dados de movimentos no banco MySQL |
| **CircuitBreakRepository** | Interface JDBI para acesso aos dados de circuit break |
| **MensageriaApiDelegateImpl** | Implementação dos endpoints REST da API de mensageria |
| **DominiosApiDelegateImpl** | Implementação dos endpoints REST para consulta de domínios e erros |
| **ConversaoMensagemMapper** | Mapper MapStruct para conversão entre entidades de domínio e representações |
| **CustomStatusEnvioListenerErrorHandler** | Tratador de erros customizado para o listener Kafka |
| **RestResponseEntityExceptionHandler** | Tratador global de exceções REST |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.7.3** (via parent POM Atlante)
- **Spring Kafka** (consumo de mensagens)
- **Apache Kafka** (mensageria)
- **Apache Avro** (serialização de mensagens Kafka)
- **MySQL 8.4.0** (banco de dados relacional)
- **JDBI 3.14.4** (acesso a dados SQL)
- **MapStruct** (mapeamento de objetos)
- **Spring Security OAuth2** (autenticação JWT)
- **Swagger/OpenAPI 3.0** (documentação de APIs)
- **Logback** (logging)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **ConfigCat** (feature toggle)
- **H2 Database** (testes e ambiente local)
- **Jackson** (processamento JSON)
- **Lombok** (redução de boilerplate)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/conversor/mensagem-envio` | MensageriaApiDelegateImpl | Converte mensagem JSON para XML e registra movimento de envio |
| POST | `/v1/conversor/recebimento-mensagem` | MensageriaApiDelegateImpl | Converte mensagem XML recebida para JSON e registra movimento |
| PUT | `/v1/atualiza-movimento` | MensageriaApiDelegateImpl | Atualiza status de um movimento existente |
| GET | `/v1/movimentos` | MensageriaApiDelegateImpl | Consulta movimentos por diversos critérios (cdMovimento, nuOperacao, etc) |
| POST | `/v1/movimentos/search` | MensageriaApiDelegateImpl | Busca paginada de movimentos com filtros |
| GET | `/v1/movimentos/{cdMovimento}/fluxo` | MensageriaApiDelegateImpl | Consulta histórico de fluxo de um movimento |
| POST | `/v1/contingencia/circuit-break` | MensageriaApiDelegateImpl | Cria ou atualiza configuração de circuit break |
| GET | `/v1/contingencia/circuit-break` | MensageriaApiDelegateImpl | Consulta configurações de circuit break |
| GET | `/v1/contingencia/circuit-break/historico` | MensageriaApiDelegateImpl | Consulta histórico paginado de alterações de circuit break |
| GET | `/v1/gerar-nsu` | MensageriaApiDelegateImpl | Gera número sequencial único (NSU) para mensagens |
| GET | `/dominios` | DominiosApiDelegateImpl | Consulta domínios e códigos de erro do SPB |

---

## 5. Principais Regras de Negócio

1. **Conversão de Mensagens**: Converte mensagens entre formatos JSON (sistema interno) e XML (SPB/BACEN), validando estrutura e conteúdo.

2. **Controle de Movimentos**: Registra e rastreia movimentos financeiros com estados (Digitada, Enviada, Respondida, Erro, etc), evitando duplicação através de hash SHA-256.

3. **Circuit Break**: Permite bloquear temporariamente o envio de mensagens por instituição e grupo de mensagem para contingência operacional.

4. **Feature Toggle**: Controla dinamicamente o processamento de mensagens por instituição (655-Votorantim, 413-BV), agência, tipo de mensagem e valor.

5. **Geração de NuOp**: Monta número de operação único no formato: ISPB + Data (yyyyMMdd) + "7" + CdMovimento (6 dígitos).

6. **Processamento R1/R2/E**: Diferencia tipos de mensagens (Requisição inicial, Resposta, Erro) aplicando lógicas específicas de persistência.

7. **Validação de Duplicidade**: Verifica existência de mensagens através de hash do conteúdo antes de processar.

8. **Auditoria**: Registra trilha completa de alterações com timestamps, usuário e flags de ativo/inativo.

9. **Tratamento de Erros**: Captura e persiste códigos de erro do SPB com descrições detalhadas.

10. **Geração de NSU**: Cria identificadores únicos para mensagens ISPB no formato: TipoMensagem + Data (yyyyMMdd) + 12 dígitos aleatórios.

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **TbMovimento**: Entidade central representando um movimento financeiro no SPB
  - Relacionamento 1:N com **TbDetalheMovimento** (detalhes/versões da mensagem)
  - Relacionamento 1:N com **TbFluxoMovimento** (histórico de mudanças de status)
  - Relacionamento 1:N com **TbErroMovimento** (erros associados ao movimento)

- **TbDetalheMovimento**: Armazena o JSON da mensagem e metadados
  - Relacionamento N:1 com **TbMovimento**
  - Relacionamento 1:N com **TbErroMovimento**

- **TbFluxoMovimento**: Histórico de transições de estado do movimento
  - Relacionamento N:1 com **TbMovimento**

- **TbErroMovimento**: Erros ocorridos no processamento
  - Relacionamento N:1 com **TbMovimento**
  - Relacionamento N:1 com **TbDetalheMovimento**

- **TbControleEnvioMovimento**: Configuração de circuit break
  - Relacionamento 1:N com **TlControleEnvioMovimento** (histórico)

- **TbMovimentoHistorico**: Histórico de movimentos (banco separado)

**Diagrama Textual:**
```
TbMovimento (1) ----< (N) TbDetalheMovimento
TbMovimento (1) ----< (N) TbFluxoMovimento
TbMovimento (1) ----< (N) TbErroMovimento
TbDetalheMovimento (1) ----< (N) TbErroMovimento
TbControleEnvioMovimento (1) ----< (N) TlControleEnvioMovimento
```

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbMovimento | Tabela | SELECT | Consulta movimentos financeiros por diversos critérios |
| TbDetalheMovimento | Tabela | SELECT | Consulta detalhes de mensagens por hash identificador |
| TbFluxoMovimento | Tabela | SELECT | Consulta histórico de fluxo/status de movimentos |
| TbErroMovimento | Tabela | SELECT | Consulta erros associados a movimentos |
| TbControleEnvioMovimento | Tabela | SELECT | Consulta configurações de circuit break |
| TlControleEnvioMovimento | Tabela | SELECT | Consulta histórico de alterações de circuit break |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbMovimento | Tabela | INSERT/UPDATE | Insere novos movimentos e atualiza status/flags |
| TbDetalheMovimento | Tabela | INSERT | Insere detalhes de mensagens processadas |
| TbFluxoMovimento | Tabela | INSERT | Insere registros de mudança de status |
| TbErroMovimento | Tabela | INSERT | Insere erros capturados no processamento |
| TbControleEnvioMovimento | Tabela | INSERT/UPDATE | Upsert de configurações de circuit break |
| TlControleEnvioMovimento | Tabela | INSERT | Insere histórico de alterações de circuit break |
| TbMovimentoHistorico | Tabela | INSERT | Insere histórico de movimentos (banco separado) |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| openapi.yaml | Leitura | src/main/resources/swagger/ | Contract-first da API REST |
| application.yml | Leitura | src/main/resources/ | Configurações da aplicação |
| application-local.yml | Leitura | src/main/resources/ | Configurações para ambiente local |
| logback-spring.xml | Leitura | src/main/resources/ e infra-as-code/arquivos/ | Configuração de logs |
| StatusEnvioMensagemSPB.avsc | Leitura | src/main/resources/avro/ | Schema Avro para mensagens Kafka |
| *.sql | Leitura | src/main/resources/br/.../repository/ | Queries SQL do JDBI |

---

## 10. Filas Lidas

- **spbb-base-status-envio-mensagem** (Kafka): Fila de consumo de mensagens de status de envio do SPB, contendo atualizações de situação de movimentos processados. Schema Avro: `StatusEnvioMensagemSPB`.

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Apache Kafka (Confluent Cloud) | Mensageria | Consumo de mensagens de status do SPB |
| Schema Registry (Confluent) | Serviço | Gerenciamento de schemas Avro |
| MySQL (Cloud SQL) | Banco de Dados | Persistência de movimentos e configurações |
| ConfigCat | Feature Toggle | Gerenciamento de feature flags |
| SPB/BACEN | Sistema Externo | Sistema de Pagamentos Brasileiro (conversão de mensagens) |
| OAuth2/JWT | Autenticação | Validação de tokens JWT via API Gateway |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões de microserviços e separação de responsabilidades (service, repository, mapper, rest)
- Uso adequado de frameworks modernos (Spring Boot, JDBI, MapStruct, Kafka)
- Implementação de tratamento de exceções customizado e centralizado
- Uso de feature toggles para controle dinâmico de funcionalidades
- Documentação via OpenAPI/Swagger
- Separação de configurações por ambiente
- Uso de Lombok para redução de boilerplate
- Implementação de circuit breaker para contingência
- Auditoria de operações
- Testes unitários presentes (embora não enviados)

**Pontos de Melhoria:**
- Algumas classes de serviço com muitas responsabilidades (ex: ConversaoMensagemService)
- Métodos longos em algumas classes (ex: processarRecebimento)
- Uso de `@SneakyThrows` pode mascarar exceções
- Alguns comentários em português misturados com código em inglês
- Poderia ter mais validações de entrada em alguns endpoints
- Algumas queries SQL poderiam ser otimizadas (uso de LIKE com wildcard inicial)
- Falta de documentação inline em alguns métodos complexos

---

## 14. Observações Relevantes

1. **Bancos de Dados Separados**: O sistema utiliza dois bancos MySQL distintos: `SPBBMensageriaExterna` (dados operacionais) e `SPBBMensageriaHistorico` (histórico).

2. **Segurança**: Implementa autenticação via JWT com validação de tokens através de API Gateway.

3. **Resiliência**: Implementa circuit breaker para contingência operacional e retry de conexões via bootstrap.sh.

4. **Observabilidade**: Expõe métricas via Actuator (health, metrics, prometheus) na porta 9090.

5. **Multi-Instituição**: Suporta processamento para múltiplas instituições (655-Votorantim, 413-BV) com regras específicas.

6. **Idempotência**: Utiliza hash SHA-256 para garantir que mensagens duplicadas não sejam reprocessadas.

7. **Versionamento**: Controla versão do catálogo de mensagens SPB.

8. **Ambiente Local**: Suporta execução local com H2 in-memory e Kafka local.

9. **Deploy**: Preparado para deploy em Kubernetes/OpenShift (Google Cloud Platform) com configurações via infra.yml.

10. **Chassi Atlante**: Utiliza o framework Atlante do Banco Votorantim para padronização de microserviços.