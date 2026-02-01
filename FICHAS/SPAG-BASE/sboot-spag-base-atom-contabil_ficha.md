# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-spag-base-atom-contabil** é um serviço atômico (microserviço) desenvolvido em Java com Spring Boot, responsável por processar notificações contábeis de pagamentos. O sistema consome mensagens de uma fila Google Cloud Pub/Sub, valida e persiste eventos contábeis em um banco de dados MySQL. Seu principal objetivo é registrar lançamentos contábeis relacionados a transações de pagamento confirmadas, evitando duplicações e aplicando regras de negócio específicas (como tratamento de liquidações STN e exclusão de devoluções).

---

## 2. Principais Classes e Responsabilidades

| Classe/Interface | Responsabilidade |
|------------------|------------------|
| `Application` | Classe principal de inicialização da aplicação Spring Boot. |
| `NotificacaoContabilListener` | Listener que consome mensagens do Pub/Sub, valida status e código de transação, e aciona o serviço de persistência. |
| `NotificacaoContabilService` | Serviço de negócio que valida duplicação de lançamentos e persiste eventos contábeis. |
| `NotificacaoContabilRepository` | Interface JDBI para acesso ao banco de dados (inserção e validação de lançamentos). |
| `NotificationEntry` | Entidade de domínio representando uma notificação de evento contábil. |
| `BillingEntry`, `StatusEntry`, `SPBEntry`, etc. | Entidades auxiliares que compõem a estrutura de dados da notificação. |
| `PubsubConfiguration` | Configuração do subscriber do Google Cloud Pub/Sub. |
| `JdbiConfiguration` | Configuração do JDBI para acesso ao banco de dados MySQL. |
| `NotificationHelper` | Classe utilitária para validação e ajuste de dados de credores/devedores em transações STN. |
| `JsonUtil`, `LoggerHelper`, `SqlLoggerImpl` | Classes utilitárias para manipulação de JSON, sanitização de logs e logging de SQL. |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.7.x** (baseado no parent POM Atlante)
- **Maven 3.8+**
- **MySQL 8.2.0** (banco de dados relacional)
- **JDBI 3.19.0** (framework de acesso a dados SQL)
- **Google Cloud Pub/Sub** (mensageria)
- **Spring Cloud GCP 1.2.8.RELEASE** (integração com GCP)
- **Lombok** (redução de boilerplate)
- **Gson** (serialização/deserialização JSON)
- **Swagger/OpenAPI 3.0** (documentação de API)
- **JUnit 5 e Mockito** (testes unitários)
- **Docker** (containerização)
- **Logback** (gerenciamento de logs)
- **Spring Actuator** (monitoramento e health checks)

---

## 4. Principais Endpoints REST

Não se aplica.

O sistema não expõe endpoints REST de negócio. A aplicação é orientada a eventos (event-driven), consumindo mensagens de filas Pub/Sub. O único endpoint disponível é o de monitoramento:

- **GET** `/actuator/health` (porta 9090) - Health check da aplicação.

---

## 5. Principais Regras de Negócio

1. **Validação de Status de Pagamento**: Apenas eventos com `status.code = 3` (pagamento confirmado) são processados e persistidos.
2. **Exclusão de Devoluções**: Transações com `transactionCode = 7400` (devolução) são ignoradas, mesmo que o status seja confirmado.
3. **Prevenção de Duplicação**: Antes de inserir um lançamento, o sistema verifica se o protocolo (`CdLancamento`) já existe na base. Caso exista, a mensagem é reconhecida (ack) sem nova inserção.
4. **Tratamento de Liquidação STN**: Quando `settlementMethod = 46` (liquidação STN), os dados de credor e devedor são ajustados para valores padrão (banco = 0) caso estejam nulos.
5. **Valores Padrão**: Campos `record` e `subsidiaryCode` recebem valores padrão (`""` e `1`, respectivamente) caso não sejam informados.
6. **Persistência Atômica**: Cada evento contábil é inserido na tabela `TbLancamentoContabil` com informações detalhadas (protocolo, valor, evento contábil, data de movimento, filial, tipo de lançamento, contas, bancos, etc.).

---

## 6. Relação entre Entidades

As entidades de domínio representam a estrutura de uma notificação contábil:

- **NotificationEntry**: Entidade principal contendo todos os dados da notificação.
  - Contém: `protocol`, `type`, `amount`, `effectiveDateTime`, `accountingEvent`, `status`, `debtor`, `creditor`, `reverse`, `purpose`, `payment`, `origin`, etc.
  - Relaciona-se com:
    - **BillingEntry** (debtor e creditor): dados de conta, banco, documento, tipo de pessoa.
    - **StatusEntry**: código e mensagem de status da transação.
    - **SPBEntry**: informações do Sistema de Pagamentos Brasileiro.
    - **ReverseEntry**: dados de estorno (se aplicável).
    - **PurposeEntry**: finalidade do pagamento.
    - **PaymentEntry**: canal e método de pagamento.
    - **OriginEntry**: origem da transação.
    - **PayerEntry**: dados do pagador.
    - **AccountEntry**: número e tipo de conta.

Não há relacionamento JPA/Hibernate, pois o sistema utiliza JDBI para acesso direto ao banco via SQL.

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| `TbLancamentoContabil` | Tabela | SELECT | Validação de existência de lançamento contábil pelo código (`CdLancamento`). |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| `TbLancamentoContabil` | Tabela | INSERT | Inserção de novos eventos contábeis com dados completos (protocolo, valor, evento, data, filial, contas, bancos, etc.). |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `logback-spring.xml` | Leitura | Configuração de logs (local e ambientes) | Arquivo de configuração de logs da aplicação. |
| `application.yml` / `application-local.yml` | Leitura | Spring Boot | Arquivos de propriedades da aplicação. |
| `inserirEventoContabil.sql` | Leitura | `NotificacaoContabilRepository` | Script SQL para inserção de eventos contábeis. |
| `validacaoLancamentoExiste.sql` | Leitura | `NotificacaoContabilRepository` | Script SQL para validação de duplicação de lançamentos. |

---

## 10. Filas Lidas

| Nome da Fila | Tecnologia | Breve Descrição |
|--------------|-----------|-----------------|
| `business-spag-base-contabil-notification-service-sub` | Google Cloud Pub/Sub | Fila de notificações contábeis de pagamentos. Consome mensagens JSON com dados de transações para processamento e persistência. |

---

## 11. Filas Geradas

Não se aplica.

O sistema não publica mensagens em filas. Apenas consome da fila de entrada.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Breve Descrição |
|-----------------|------|-----------------|
| Google Cloud Pub/Sub | Mensageria | Consumo de mensagens de notificações contábeis. |
| MySQL (Cloud SQL) | Banco de Dados | Persistência de eventos contábeis na base `SPAGContabilPagamento`. |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 8/10

**Justificativa:**

O código apresenta boa organização e clareza, seguindo padrões de arquitetura em camadas (listener, service, repository, domain). Utiliza boas práticas como:

- Separação de responsabilidades (SRP).
- Uso de Lombok para redução de boilerplate.
- Configuração externalizada (application.yml, infra.yml).
- Testes unitários com cobertura razoável.
- Uso de JDBI para acesso a dados, evitando complexidade desnecessária de ORMs.
- Tratamento de exceções e logs estruturados.

Pontos de melhoria:

- Falta de documentação JavaDoc em algumas classes.
- Alguns valores "mágicos" (como códigos de status e transação) poderiam ser melhor centralizados em constantes.
- Testes de integração não estão presentes (apenas testes unitários).
- Validações de negócio poderiam ser mais explícitas com uso de validadores dedicados.

---

## 14. Observações Relevantes

- O sistema é **stateful** e orientado a eventos, não expondo APIs REST de negócio.
- A aplicação utiliza o **chassi Atlante** do Banco Votorantim, seguindo padrões corporativos de desenvolvimento.
- A configuração de infraestrutura é gerenciada via arquivo `infra.yml`, com suporte a múltiplos ambientes (des, uat, prd).
- O sistema utiliza **multi-layer Docker** para otimização de builds e deploys.
- A aplicação está preparada para execução em **Google Cloud Platform (GCP)**, com integração nativa ao Pub/Sub e Cloud SQL.
- O projeto segue o modelo de **microserviços atômicos**, com responsabilidade única e baixo acoplamento.
- A aplicação possui monitoramento via **Spring Actuator** e métricas expostas para Prometheus.
- O sistema utiliza **JWT** para autenticação (configurado via API Gateway), embora não exponha endpoints REST de negócio.