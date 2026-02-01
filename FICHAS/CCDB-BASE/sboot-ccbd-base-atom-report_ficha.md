# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-ccbd-base-atom-report** é um serviço atômico Spring Boot desenvolvido para gerenciar movimentações financeiras de contas bancárias. O sistema possui duas funcionalidades principais:

1. **Replicação de Movimentos**: Consome mensagens de filas Pub/Sub (Google Cloud) contendo dados de transações financeiras e persiste essas informações no Google Cloud Spanner.

2. **Consulta de Extratos**: Expõe APIs REST (v1 e v2) para consulta de transações bancárias com suporte a paginação (offset e cursor), filtros por data, busca textual e ordenação.

O sistema utiliza arquitetura hexagonal (ports and adapters), com separação clara entre domínio, aplicação e infraestrutura.

---

## 2. Principais Classes e Responsabilidades

| Classe/Interface | Responsabilidade |
|------------------|------------------|
| `Application` | Classe principal de inicialização do Spring Boot |
| `MovementSubscriber` | Subscriber para consumir mensagens de replicação de movimentos via Pub/Sub |
| `MigrationSubscriber` | Subscriber para consumir mensagens de migração de dados via Pub/Sub |
| `ProcessMovementUseCase` | Caso de uso para processar e persistir movimentos financeiros |
| `GetEntriesUseCase` | Caso de uso para consulta de transações com paginação por cursor |
| `OffsetGetEntriesUseCase` | Caso de uso para consulta de transações com paginação por offset |
| `GetMovementControllerAdapterV1` | Controlador REST v1 para consulta de transações (paginação offset) |
| `GetMovementControllerAdapterV2` | Controlador REST v2 para consulta de transações (paginação cursor) |
| `CursorEntryQueryRepository` | Repositório para consultas com paginação baseada em cursor |
| `OffsetEntryQueryRepository` | Repositório para consultas com paginação baseada em offset |
| `MovementReplicationCommandRepository` | Repositório para persistência de movimentos no Spanner |
| `TbAccountLedger` | Entidade JPA representando o livro-razão de contas |
| `FinancialMovement` | Modelo de domínio representando uma movimentação financeira |
| `AccountEntryQuery` | Objeto de valor encapsulando critérios de consulta |
| `CategoriaTransacao` | Enum para categorização de tipos de transação |
| `RestExceptionHandler` | Tratamento centralizado de exceções REST |

---

## 3. Tecnologias Utilizadas

- **Java 21** (com Virtual Threads habilitadas)
- **Spring Boot 3.x** (parent: pom-atle-base-sboot-atom-parent 3.5.1)
- **Spring Cloud Stream** (integração com Pub/Sub)
- **Google Cloud Pub/Sub** (mensageria)
- **Google Cloud Spanner** (banco de dados NoSQL distribuído)
- **Hibernate 6.6.1** (ORM com dialeto customizado para Spanner)
- **MapStruct 1.6.3** (mapeamento de objetos)
- **OpenAPI/Swagger** (documentação de APIs)
- **OpenTelemetry** (observabilidade e tracing)
- **Micrometer** (métricas)
- **Feature Toggle** (ConfigCat - gerenciamento de features)
- **Maven** (gerenciamento de dependências)
- **Lombok** (redução de boilerplate)
- **Jackson** (serialização JSON)
- **Spring Security OAuth2** (autenticação JWT)
- **Resilience4j** (circuit breaker)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/digital-bank/{bankId}/accounts/{accountId}/transactions` | `GetMovementControllerAdapterV1` | Consulta transações com paginação offset (v1) |
| GET | `/v2/digital-bank/{bankId}/accounts/{accountId}/transactions` | `GetMovementControllerAdapterV2` | Consulta transações com paginação cursor (v2) |
| GET | `/actuator/health` | Spring Actuator | Health check da aplicação |
| GET | `/swagger-ui/index.html` | Swagger UI | Documentação interativa das APIs |

**Parâmetros de consulta comuns:**
- `bankId`: Código do banco
- `accountId`: Hash SHA-256 identificador da conta
- `pageSize`: Quantidade de registros por página
- `term`: Busca textual em campos específicos
- `bookingDateFrom/To`: Filtro por data contábil
- `settlementDateFrom/To`: Filtro por data de transação
- `orderDirection`: ASC ou DESC

---

## 5. Principais Regras de Negócio

1. **Geração de Hash de Conta**: O identificador da conta é gerado via SHA-256 concatenando: `cdBanco + cdAgenciaOperacao + nuContaCorrente + cdTipoConta`.

2. **Validação de Payload**: Mensagens Pub/Sub são validadas usando Bean Validation antes do processamento.

3. **Categorização de Transações**: Transações são categorizadas automaticamente com base no código legado (`legacyFinancialTransactionId`) usando o enum `CategoriaTransacao`.

4. **Validação de Intervalo de Datas**: O sistema valida que:
   - Datas "from" e "to" devem ser fornecidas em pares
   - Pelo menos um intervalo de datas (contábil ou transação) deve ser informado
   - O intervalo máximo é configurável via Feature Toggle (padrão: 12 meses)

5. **Paginação Cursor vs Offset**:
   - **V1 (Offset)**: Paginação tradicional com número de página e total de elementos
   - **V2 (Cursor)**: Paginação baseada em cursor (mais eficiente para grandes volumes)

6. **Busca Textual**: Utiliza função `SEARCH_SUBSTRING` do Spanner para buscar em campos tokenizados.

7. **Ordenação**: Ordenação primária por `insertTime` e desempate por `accountLedgerId`.

8. **Tratamento de Duplicatas**: Violações de constraint único são tratadas como avisos (registro já existe).

9. **Retry de Mensagens**: Mensagens de migração possuem limite de tentativas configurável.

10. **Flag de Saldo Incondicional**: Transações com `flLancamentoIncondicional = 'S'` são marcadas como compulsórias.

---

## 6. Relação entre Entidades

**Principais entidades e relacionamentos:**

- **TbAccountLedger** (Livro-Razão de Contas)
  - Representa uma transação financeira individual
  - Chave primária: `accountLedgerId` (UUID)
  - Constraint único: `(accountId, accountOwnerTransactionId, accountServiceTransactionId, legacyFinancialTransactionId)`
  - Campos principais: datas, valores, identificadores, tipo de transação

- **TbFinancialTransactionType** (Tipos de Transação Financeira)
  - Representa tipos de transação (não utilizada diretamente nas consultas principais)
  - Chave primária: `financialTransactionTypeId`

- **MovementReplication** (Modelo de Domínio)
  - Record imutável representando dados de replicação
  - Mapeado de `MovementDto` (entrada Pub/Sub)
  - Convertido para `FinancialMovement` (domínio)
  - Persistido como `TbAccountLedger` (entidade)

**Fluxo de transformação:**
```
MovementDto (Pub/Sub) 
  → MovementReplication (domínio) 
  → FinancialMovement (domínio) 
  → TbAccountLedger (persistência)
```

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbAccountLedger | Tabela | SELECT | Consulta de transações financeiras com filtros diversos |
| TbFinancialTransactionType | Tabela | SELECT | Tipos de transação financeira (não utilizada nas queries principais) |

**Observação**: As consultas utilizam JPA Criteria API com Specifications para construção dinâmica de queries baseadas nos filtros fornecidos.

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbAccountLedger | Tabela | INSERT | Inserção de novas transações financeiras recebidas via Pub/Sub |

**Observação**: O sistema não realiza UPDATE ou DELETE. Todas as operações são de inserção (append-only).

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | Spring Boot | Configurações da aplicação |
| application-local.yml | Leitura | Spring Boot | Configurações para ambiente local |
| logback-spring.xml | Leitura | Logback | Configuração de logs |
| openapi.yaml | Leitura | OpenAPI Generator | Especificação da API REST |

---

## 10. Filas Lidas

| Nome da Fila | Tipo | Classe Consumidora | Descrição |
|--------------|------|-------------------|-----------|
| `${PUBSUB_REPLICATION_SUB}` | Google Cloud Pub/Sub | `MovementSubscriber` | Fila de replicação de movimentos financeiros em tempo real |
| `${PUBSUB_MIGRATION_SUB}` | Google Cloud Pub/Sub | `MigrationSubscriber` | Fila de migração de dados históricos com retry configurável |

**Configurações:**
- Modo de ACK: MANUAL (controle explícito de confirmação)
- Retry: Até 5 tentativas para mensagens de migração
- Error Handler: `errorHandler` bean para tratamento de erros

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Google Cloud Spanner | Banco de Dados | Armazenamento de transações financeiras |
| Google Cloud Pub/Sub | Mensageria | Consumo de eventos de movimentação |
| ConfigCat | Feature Toggle | Gerenciamento de configurações dinâmicas (ex: range máximo de datas) |
| OAuth2 JWT Provider | Autenticação | Validação de tokens JWT para endpoints protegidos |
| OpenTelemetry/Cloud Trace | Observabilidade | Tracing distribuído e métricas |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura hexagonal bem implementada com separação clara de responsabilidades
- Uso adequado de records Java para imutabilidade
- Validação robusta com Bean Validation
- Tratamento de exceções centralizado e estruturado
- Uso de MapStruct para mapeamento eficiente
- Código bem documentado com Javadoc em pontos críticos
- Uso de padrões modernos (Virtual Threads, Records, Pattern Matching)
- Testes estruturados (embora não enviados para análise)
- Uso de Feature Toggle para configurações dinâmicas
- Implementação de Template Method Pattern para processamento de mensagens

**Pontos de Melhoria:**
- Algumas classes poderiam ser mais coesas (ex: `AbstractFetchSpannerData` com múltiplas responsabilidades)
- Falta de documentação em alguns métodos complexos (ex: lógica de cursor)
- Enum `CategoriaTransacao` muito extenso (poderia ser externalizado)
- Uso de `assert` para validações em produção (não recomendado)
- Algumas strings hardcoded que poderiam ser constantes
- Falta de logs estruturados em alguns pontos críticos

---

## 14. Observações Relevantes

1. **Segurança**: O sistema utiliza autenticação JWT via OAuth2, mas os endpoints de documentação e health check são públicos.

2. **Performance**: 
   - Uso de Virtual Threads do Java 21 para melhor throughput
   - Paginação cursor é mais eficiente que offset para grandes volumes
   - Queries otimizadas com índices implícitos do Spanner

3. **Observabilidade**: 
   - Integração completa com OpenTelemetry
   - Baggage propagation para contexto de rastreamento
   - Métricas expostas via Prometheus

4. **Resiliência**:
   - Circuit breaker configurado (Resilience4j)
   - Retry automático para mensagens Pub/Sub
   - Tratamento de duplicatas

5. **Ambiente Local**: 
   - Suporte a emulador do Spanner
   - Suporte a emulador do Pub/Sub
   - Profile `local` com configurações específicas

6. **Versionamento de API**: 
   - Duas versões da API (v1 e v2) coexistem
   - V2 introduz paginação cursor mais eficiente

7. **Compliance**: 
   - Uso de OWASP Encoder para sanitização de logs
   - Validação rigorosa de entrada
   - Padrões de segurança do Banco Votorantim

8. **Limitações**:
   - Não há suporte a UPDATE/DELETE de transações
   - Range máximo de datas configurável (padrão 12 meses)
   - Busca textual limitada a campos específicos

9. **Dependências Internas**: 
   - Utiliza bibliotecas proprietárias do Banco Votorantim (Atlante, Feature Toggle)
   - Parent POM customizado (`pom-atle-base-sboot-atom-parent`)