# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-ccbd-base-atom-conciliacao-transacao** é um serviço atômico desenvolvido em Spring Boot para processar e conciliar transações de cartão de débito provenientes de diferentes bandeiras (Visa, Mastercard, TIF, FormC). 

O sistema consome mensagens de uma fila RabbitMQ contendo dados de transações processadas por diferentes arquivos de bandeiras, realiza validações, persiste informações em banco de dados SQL Server e publica os dados completos em um tópico Google Cloud Pub/Sub para consumo por outros sistemas.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal que inicializa a aplicação Spring Boot |
| **ConciliacaoTransacaoListener** | Listener RabbitMQ que consome mensagens de transações, processa e encaminha para persistência e Pub/Sub |
| **ConciliacaoTransacaoServiceImpl** | Implementa a lógica de negócio para validação e persistência de transações no banco de dados |
| **CCBDRepositoryImpl** | Interface JDBI para acesso ao banco de dados SQL Server |
| **PubSubPublishServiceImpl** | Serviço responsável por publicar mensagens no Google Cloud Pub/Sub |
| **ConciliacaoTransacaoConfiguration** | Configuração de beans Spring (RabbitMQ, JDBI, serviços) |
| **DataBaseConfiguration** | Configuração de datasource e JDBI para acesso ao SQL Server |
| **TifCompleto, VisaBase2Completo, MasterT464Completo, MasterT112Base2Completo, FormcCompleto** | Mappers que transformam DTOs genéricos em DTOs específicos de cada tipo de arquivo de bandeira |
| **ConciliacaoTransacaoDTO** | DTO principal que representa uma transação recebida da fila |
| **TipoArquivoBandeiraEnum, TipoTransacaoEnum** | Enums que definem tipos de arquivos e transações suportados |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot** (Web, AMQP, JDBC, Actuator)
- **Maven** (gerenciamento de dependências e build)
- **JDBI 3.9.1** (acesso a banco de dados)
- **Microsoft SQL Server** (banco de dados relacional)
- **RabbitMQ** (mensageria para consumo de eventos)
- **Google Cloud Pub/Sub** (publicação de eventos processados)
- **Springfox/Swagger 3.0.0** (documentação de APIs)
- **Jackson** (serialização/deserialização JSON)
- **Logback** (logging)
- **JUnit 5 e Mockito** (testes unitários)
- **Docker** (containerização)
- **Prometheus e Micrometer** (métricas)

---

## 4. Principais Endpoints REST

Não se aplica. O sistema não expõe endpoints REST públicos, funcionando como um consumidor de mensagens (listener) e publicador em filas/tópicos.

---

## 5. Principais Regras de Negócio

1. **Consumo de mensagens RabbitMQ**: O sistema consome mensagens da fila `events.business.CCBD-BASE.registroBandeira` contendo dados de transações de diferentes bandeiras.

2. **Identificação do tipo de arquivo**: Com base no campo `tipoArquivoProcessado`, o sistema identifica qual bandeira originou a transação (TIF, Visa Base II, Master Base II, Master T464, FormC).

3. **Persistência seletiva em SQL Server**: Apenas transações dos tipos TIF, Visa Base II e Master Base II são persistidas no banco de dados relacional, desde que o tipo de transação seja válido (0100, 0200, 0400, 0420).

4. **Ajuste de código autorizador**: Se o código do emissor do cartão (`cdEmissorCartao`) for 1002, o código autorizador é ajustado para 0.

5. **Validação de campos obrigatórios**: Antes da persistência, o sistema valida campos obrigatórios usando Bean Validation.

6. **Geração de JSON completo**: Para todos os tipos de arquivo, o sistema gera um JSON completo com todos os campos da transação e publica no Google Cloud Pub/Sub.

7. **Tratamento de erros e DLQ**: Em caso de erro no processamento, a mensagem é repostada em uma fila de Dead Letter Queue (DLQ) para reprocessamento posterior.

8. **Montagem de identificação de cartão (quina)**: O sistema monta um identificador único do cartão combinando produto, conta e correlativo, ou utiliza o número mascarado quando disponível.

---

## 6. Relação entre Entidades

**Entidades principais:**

- **ConciliacaoTransacaoDTO**: Representa a transação recebida da fila RabbitMQ
- **ConciliacaoTransacao**: Entidade de domínio para persistência na tabela `TbConciliacaoTransacao`
- **ConciliacaoTransacaoComplementares**: Entidade para persistência de campos complementares na tabela `TbComplementoConciliacaoTrnso`

**DTOs específicos por bandeira:**
- **TifDTO**: Dados completos de transações TIF
- **VisaBase2DTO**: Dados completos de transações Visa Base II (com complemento Tcr5VisaBase2DTO)
- **MasterT464DTO**: Dados completos de transações Master T464 (com complementos HeaderT464DTO e ComplementoT464DTO)
- **MasterT112Base2DTO**: Dados completos de transações Master Base II
- **FormcDTO**: Dados completos de transações FormC (com complemento ComplementoFormcDTO)

**Relacionamentos:**
- ConciliacaoTransacao → ConciliacaoTransacaoComplementares (1:1, via `cdComplementoConciliacaoTrnso`)
- ConciliacaoTransacao referencia TbArquivoOrigem, TbTipoTransacao e TbStatusProcessamento

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbArquivoOrigem | tabela | SELECT | Busca o código do tipo de arquivo processado |
| TbTipoTransacao | tabela | SELECT | Busca o código do tipo de transação |
| TbStatusProcessamento | tabela | SELECT | Busca o código de status "REGISTRO_PROCESSADO" |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbConciliacaoTransacao | tabela | INSERT | Insere dados principais da transação conciliada |
| TbComplementoConciliacaoTrnso | tabela | INSERT | Insere campos complementares da transação (JSON) |

---

## 9. Arquivos Lidos e Gravados

Não se aplica. O sistema não lê ou grava arquivos diretamente no sistema de arquivos. Os dados são recebidos via mensageria e os "arquivos" referenciados são metadados sobre a origem dos dados.

---

## 10. Filas Lidas

- **events.business.CCBD-BASE.registroBandeira** (RabbitMQ): Fila principal de onde o sistema consome mensagens de transações processadas.

---

## 11. Filas Geradas

- **events.ex.business.ccbd.registroBandeiraDLQ** (RabbitMQ): Fila de Dead Letter Queue para onde mensagens com erro são enviadas para reprocessamento.
- **Tópico Google Cloud Pub/Sub** (configurável por ambiente): Tópico onde são publicadas as transações processadas em formato JSON completo. Exemplos:
  - DES: `projects/bv-cart-des/topics/business-cart-base-arquivos-debito`
  - UAT: `projects/bv-cart-uat/topics/business-cart-base-arquivos-debito`
  - PRD: `projects/bv-cart-prd/topics/business-cart-base-arquivos-debito`

---

## 12. Integrações Externas

1. **RabbitMQ**: Consumo de mensagens de transações e publicação em DLQ em caso de erro.
2. **Google Cloud Pub/Sub**: Publicação de transações processadas para consumo por outros sistemas.
3. **SQL Server (DBCCBD)**: Persistência de transações e consulta de tabelas de referência.

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (application, domain, common)
- Uso adequado de padrões como Strategy para processamento de diferentes tipos de arquivo
- Configuração externalizada e suporte a múltiplos ambientes
- Presença de testes unitários
- Uso de JDBI para queries SQL organizadas em arquivos separados
- Tratamento de exceções e mecanismo de DLQ para reprocessamento

**Pontos de Melhoria:**
- Código com alguns trechos comentados e logs excessivos que poderiam ser removidos
- Validações e tratamento de erros poderiam ser mais específicos e informativos
- Alguns métodos longos (ex: `listener` em ConciliacaoTransacaoListener) que poderiam ser refatorados
- Falta de documentação JavaDoc em classes e métodos principais
- Uso de Optional de forma inconsistente em alguns pontos
- Alguns campos e variáveis com nomes em português, outros em inglês (falta de padronização)
- Testes poderiam ter melhor cobertura de cenários de erro

---

## 14. Observações Relevantes

1. **Ambiente de execução**: O sistema está preparado para rodar em Kubernetes (OpenShift) com configurações específicas para cada ambiente (DES, QA, UAT, PRD).

2. **Segurança**: Utiliza Service Account do Google Cloud (ksa-ccbd-base-12736) para autenticação no Pub/Sub.

3. **Monitoramento**: Expõe métricas via Actuator e Prometheus na porta 9090.

4. **Auditoria**: Integra com biblioteca de auditoria do Banco Votorantim (springboot-arqt-base-trilha-auditoria-web).

5. **Configuração de logs**: Utiliza Logback com formato JSON para facilitar ingestão em sistemas de log centralizados.

6. **Profiles Spring**: Suporta profiles para local, des, qa, uat e prd com configurações específicas de datasource, RabbitMQ e Pub/Sub.

7. **Reprocessamento**: Mensagens com erro são enviadas para DLQ e reprocessadas após 30 segundos (configurado no RabbitMQ).

8. **Tipos de transação suportados**: 0100 (múltiplo), 0200 (single), 0400 (estorno), 0420 (desfazimento).

9. **Bandeiras suportadas**: TIF, Visa Base II, Master Base II (T112), Master T464, FormC30.