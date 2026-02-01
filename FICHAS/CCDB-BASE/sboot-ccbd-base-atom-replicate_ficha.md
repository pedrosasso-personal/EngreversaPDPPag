# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-ccbd-base-atom-replicate** é um serviço atômico desenvolvido em Spring Boot para replicação de dados de conta corrente. Sua principal função é consumir mensagens de uma fila Google Cloud Pub/Sub e replicar informações em bancos de dados Sybase, incluindo operações de abertura de conta, movimentações financeiras, histórico de saldos e dados de efetivação de transações.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal que inicializa a aplicação Spring Boot |
| `ReplicateConfiguration` | Configuração de beans, incluindo JDBI, repositórios e adaptadores Pub/Sub |
| `OpenApiConfiguration` | Configuração do Swagger para documentação de APIs |
| `ReplicateContaCorrenteListener` | Listener que consome mensagens do Pub/Sub e processa diferentes tipos de operações |
| `ReplicateContaCorrenteService` | Serviço de domínio que orquestra as operações de replicação |
| `ReplicateContaCorrenteRepositoryImpl` | Implementação do repositório que executa comandos SQL no banco de dados |
| `DadosEfetivacao` | Entidade de domínio representando dados de efetivação de operações |
| `Movimento` | Entidade de domínio representando movimentações financeiras |
| `HistoricoMovimentacao` | Entidade de domínio representando histórico de movimentações |
| `AberturaConta` | Entidade de domínio representando dados de abertura de conta |
| `TipoTransacaoEnum` | Enumeração para tipos de transação (Débito/Crédito) |

---

## 3. Tecnologias Utilizadas

- **Spring Boot** (framework principal)
- **Spring Cloud GCP Pub/Sub** (integração com Google Cloud Pub/Sub)
- **JDBI 3** (acesso a banco de dados)
- **Sybase jConnect** (driver JDBC para Sybase)
- **Swagger/Springfox** (documentação de APIs)
- **Lombok** (redução de boilerplate)
- **Jackson** (serialização/deserialização JSON)
- **Logback** (logging)
- **Micrometer/Prometheus** (métricas)
- **JUnit 5 + Mockito** (testes unitários)
- **Pact** (testes de contrato)
- **Docker** (containerização)
- **Maven** (gerenciamento de dependências)

---

## 4. Principais Endpoints REST

não se aplica

(O sistema não expõe endpoints REST públicos, funcionando apenas como consumidor de mensagens)

---

## 5. Principais Regras de Negócio

1. **Processamento de Mensagens por Operação**: O sistema identifica o tipo de operação através do atributo "operacao" na mensagem Pub/Sub e roteia para o processamento adequado
2. **Replicação de Dados de Efetivação**: Atualiza saldo bloqueado e sequencial de bloqueio na tabela TbConta
3. **Registro de Movimentos**: Insere movimentações na tabela TbMovimentoDia (Sybase) e TbMovimentoDiaFintech (MySQL)
4. **Atualização de Histórico**: Atualiza saldos totais em TbHistoricoSaldo para todas as datas >= data de efetivação
5. **Abertura de Conta**: Insere novo registro na tabela TbConta com valores iniciais zerados
6. **Tratamento de Erros**: Captura exceções de conversão JSON e erros gerais, registrando em log sem reprocessamento automático
7. **Confirmação Manual**: Utiliza AckMode.MANUAL para controle explícito de confirmação de mensagens

---

## 6. Relação entre Entidades

**Entidades principais:**

- **DadosEfetivacao**: Representa dados para atualização de saldo bloqueado
- **Movimento**: Representa uma movimentação financeira completa
- **HistoricoMovimentacao**: Representa atualização de histórico de saldo
- **AberturaConta**: Representa dados para criação de nova conta

**Relacionamentos:**
- Todas as entidades se relacionam com a tabela TbConta através dos campos: codigoBanco (cdBanco), numeroConta (nuContaCorrente) e tipoConta (cdTipoConta)
- Movimento possui relacionamento com TipoTransacaoEnum através do campo tipoTransacao

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

(O sistema não realiza operações de leitura, apenas escrita/atualização)

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| DBCONTACORRENTE.dbo.TbConta | tabela | UPDATE | Atualiza saldo bloqueado e sequencial de bloqueio |
| DBCONTACORRENTE.dbo.TbConta | tabela | INSERT | Insere nova conta corrente |
| DBCONTACORRENTE.dbo.TbMovimentoDia | tabela | INSERT | Registra movimentação diária |
| CCBDContaCorrente.TbMovimentoDiaFintech | tabela | INSERT | Registra movimentação fintech |
| DBCONTACORRENTE.dbo.TbHistoricoSaldo | tabela | UPDATE | Atualiza histórico de saldos |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot | Configurações da aplicação por ambiente |
| logback-spring.xml | leitura | Logback | Configuração de logs |
| doReplicateAberturaConta.sql | leitura | JDBI/ReplicateContaCorrenteRepositoryImpl | Script SQL para abertura de conta |
| doReplicateDadosEfetivacao.sql | leitura | JDBI/ReplicateContaCorrenteRepositoryImpl | Script SQL para atualização de efetivação |
| doReplicateHistoricoMovimento.sql | leitura | JDBI/ReplicateContaCorrenteRepositoryImpl | Script SQL para atualização de histórico |
| doReplicateMovimento.sql | leitura | JDBI/ReplicateContaCorrenteRepositoryImpl | Script SQL para registro de movimento |
| doReplicateMovimentoFintech.sql | leitura | JDBI/ReplicateContaCorrenteRepositoryImpl | Script SQL para registro de movimento fintech |

---

## 10. Filas Lidas

**Fila:** `projects/bv-ccbd-des/subscriptions/business-ccbd-replicate-sub` (Google Cloud Pub/Sub)

**Operações suportadas:**
- `atualizar_saldo`: Processa dados de efetivação
- `registrar_movimento`: Registra movimento em TbMovimentoDia
- `registrar_movimento_fintech`: Registra movimento em TbMovimentoDiaFintech
- `registrar_historico`: Atualiza histórico de movimentação
- `criar_conta`: Cria nova conta corrente

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Google Cloud Pub/Sub | Fila de Mensagens | Consumo de mensagens de replicação |
| Sybase Database (DBCONTACORRENTE) | Banco de Dados | Persistência de dados de conta corrente |
| MySQL Database (CCBDContaCorrente) | Banco de Dados | Persistência de movimentos fintech |

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura hexagonal bem definida (domain, application, infrastructure)
- Uso adequado de injeção de dependências
- Separação clara de responsabilidades entre camadas
- Uso de Lombok para reduzir boilerplate
- Testes unitários presentes
- Configuração externalizada por ambiente

**Pontos Negativos:**
- **Tratamento de erros inadequado**: Exceções são apenas logadas, sem estratégia de retry ou dead letter queue
- **Código duplicado**: Os 5 métodos do listener possuem estrutura quase idêntica, violando DRY
- **Falta de validação**: Não há validação dos dados recebidos antes do processamento
- **Logs com nível inadequado**: Uso de `log.error` para início de operação normal
- **Falta de documentação**: Classes e métodos sem JavaDoc
- **Testes incompletos**: Testes unitários com muita repetição e pouca cobertura de cenários de erro
- **Hardcoding**: Nome da subscription hardcoded na configuração
- **Falta de transações explícitas**: Embora use @Transaction, não há controle de rollback em caso de falha parcial

---

## 14. Observações Relevantes

1. **Ambientes**: O sistema suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas
2. **Monitoramento**: Integração com Prometheus/Grafana para observabilidade
3. **Segurança**: Credenciais de banco armazenadas em cofre (referenciadas via `{{ cofre_senha }}`)
4. **Infraestrutura**: Preparado para deploy em Kubernetes/OpenShift (arquivos de infra-as-code presentes)
5. **Limitação de Bancos**: Opera em dois bancos diferentes (Sybase e MySQL) para movimentos regulares e fintech
6. **Processamento Assíncrono**: Todo processamento é event-driven via Pub/Sub
7. **Ausência de API REST**: Sistema não expõe endpoints REST, apenas consome mensagens
8. **Dependência de Ordem**: Não há garantia de processamento ordenado de mensagens, o que pode causar inconsistências em cenários de alta concorrência