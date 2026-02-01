# Ficha Técnica do Sistema

---

## 1. Descrição Geral

O sistema **sboot-ccbd-base-atom-conta-corrente-fintech** é um serviço atômico desenvolvido em Java com Spring Boot, responsável por processar movimentações financeiras (débito e crédito) em contas correntes de produtos Fintech. O sistema consome mensagens de filas (RabbitMQ e Google Pub/Sub), valida transações, verifica duplicidade e registra movimentações no banco de dados MySQL (CCBDContaCorrente). Atua como um componente de efetivação de transações financeiras, garantindo a integridade e rastreabilidade das operações.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal que inicializa a aplicação Spring Boot |
| `ContaCorrenteFintechServiceImpl` | Implementa a lógica de negócio para efetivação de transações, validações e tratamento de erros |
| `ContaCorrenteFintechRepositoryImpl` | Interface de acesso ao banco de dados usando JDBI para operações SQL |
| `ContaCorrenteFintechListener` | Listener RabbitMQ que consome mensagens das filas de débito e crédito |
| `PubSubListener` | Listener Google Pub/Sub para consumo de mensagens de movimentações fintech |
| `MovimentoMapper` | Utilitário para mapeamento e transformação de objetos de domínio |
| `ContaCorrenteFintechConfiguration` | Configuração de beans, datasources e dependências |
| `RabbitMQConfiguration` | Configuração do RabbitMQ (converters, factories) |
| `PubSubConfiguration` | Configuração do Google Pub/Sub (channels, adapters) |
| `DadosEfetivacao` | Entidade de domínio representando dados de efetivação de transação |
| `Movimento` | Entidade de domínio representando uma movimentação financeira |
| `Transacao` | Entidade de domínio representando uma transação cadastrada |
| `ContaCorrente` | Entidade de domínio representando uma conta corrente |
| `BancoEnum` | Enumeração para conversão de códigos de banco (interno/externo) |
| `ExceptionReasonEnum` | Enumeração de razões de exceções de negócio |
| `ContaCorrenteFintechException` | Exceção customizada para erros de negócio |
| `DuplicidadeFintechException` | Exceção customizada para transações duplicadas |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Spring AMQP / RabbitMQ** (mensageria)
- **Spring Cloud GCP Pub/Sub** (mensageria Google Cloud)
- **JDBI 3.19.0** (acesso a dados SQL)
- **MySQL** (banco de dados)
- **HikariCP** (pool de conexões)
- **Lombok** (redução de boilerplate)
- **Springfox Swagger 3.0.0** (documentação de API)
- **Micrometer / Prometheus** (métricas)
- **Logback** (logging)
- **JUnit 5 / Mockito** (testes unitários)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Grafana / Prometheus** (monitoramento)

---

## 4. Principais Endpoints REST

não se aplica

(O sistema não expõe endpoints REST públicos, funcionando apenas como consumidor de mensagens de filas)

---

## 5. Principais Regras de Negócio

1. **Validação de Transação**: Verifica se a transação existe, está ativa e se o tipo (débito/crédito) corresponde ao esperado
2. **Validação de Duplicidade**: Impede o processamento de transações já efetivadas com base em NSU (Número Sequencial Único de Lançamento)
3. **Validação de Conta Corrente**: Verifica a existência da conta corrente antes de processar a movimentação
4. **Conversão de Códigos de Banco**: Converte códigos externos (655, 436) para códigos internos (161, 413) usando `BancoEnum`
5. **Tratamento de Campos Nulos**: Preenche valores padrão para campos opcionais antes do processamento
6. **Diferenciação Débito/Crédito**: Processa débitos e créditos com validações específicas para cada tipo
7. **Reprocessamento em Caso de Erro**: Devolve mensagens para a fila em caso de erro não tratado
8. **Idempotência**: Garante que transações duplicadas sejam identificadas e não reprocessadas
9. **Registro de Movimentação**: Insere movimentação na tabela `TbMovimentoDiaFintech` após validações

---

## 6. Relação entre Entidades

- **DadosEfetivacao**: Contém informações da transação a ser efetivada (NSU, valor, conta, tipo, etc.)
- **ContaCorrente**: Representa a conta corrente onde a movimentação será registrada (relacionada por codigoBanco, numeroConta, tipoConta)
- **Transacao**: Representa o tipo de transação cadastrada no sistema (relacionada por codigoTransacao)
- **Movimento**: Entidade resultante da combinação de DadosEfetivacao, ContaCorrente e Transacao, que será persistida no banco

**Relacionamentos:**
- DadosEfetivacao → ContaCorrente (N:1 via codigoBanco, numeroConta, tipoConta)
- DadosEfetivacao → Transacao (N:1 via codigoTransacao)
- Movimento é gerado a partir de DadosEfetivacao + ContaCorrente + Transacao

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| CCBDContaCorrente.TbConta | tabela | SELECT | Consulta dados da conta corrente (banco, agência, conta, tipo, modalidade) |
| CCBDContaCorrente.TbTransacao | tabela | SELECT | Consulta dados da transação (código, tipo débito/crédito, status ativo, nomes) |
| CCBDContaCorrente.TbMovimentoDiaFintech | tabela | SELECT | Verifica existência de movimentação (validação de duplicidade) |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| CCBDContaCorrente.TbMovimentoDiaFintech | tabela | INSERT | Registra nova movimentação financeira fintech (débito ou crédito) |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot | Configurações da aplicação (datasources, RabbitMQ, Pub/Sub, etc.) |
| logback-spring.xml | leitura | Logback | Configuração de logs (console, formato JSON) |
| *.sql (resources) | leitura | JDBI/ContaCorrenteFintechRepositoryImpl | Queries SQL para operações no banco de dados |

---

## 10. Filas Lidas

- **RabbitMQ:**
  - `debito_movimento_fintech` (consumo de mensagens de débito)
  - `credito_movimento_fintech` (consumo de mensagens de crédito)

- **Google Pub/Sub:**
  - Subscription: `business-spag-pixx-movimento-fintech-credito-sub` (crédito)
  - Subscription: `business-spag-pixx-movimento-fintech-debito-sub` (débito)

---

## 11. Filas Geradas

- **RabbitMQ:**
  - Exchange: `ex.ccbd.movimentoFintech`
  - Routing Key Débito: `ccbd.movimento.fintech.debito`
  - Routing Key Crédito: `ccbd.movimento.fintech.credito`
  
(Mensagens são devolvidas para as filas em caso de erro não tratado para reprocessamento)

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| MySQL (CCBDContaCorrente) | Banco de Dados | Armazena dados de contas correntes, transações e movimentações fintech |
| RabbitMQ | Mensageria | Consome mensagens de débito e crédito para processamento |
| Google Cloud Pub/Sub | Mensageria | Consome mensagens de movimentações fintech (alternativa ao RabbitMQ) |
| Prometheus | Monitoramento | Exporta métricas da aplicação |
| Grafana | Visualização | Dashboards de monitoramento |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades (domain, application, infrastructure)
- Uso adequado de padrões (Repository, Service, Listener)
- Tratamento de exceções customizado
- Testes unitários presentes
- Uso de Lombok para redução de boilerplate
- Configuração externalizada
- Suporte a múltiplas fontes de mensageria (RabbitMQ e Pub/Sub)

**Pontos de Melhoria:**
- Lógica de negócio extensa em `ContaCorrenteFintechServiceImpl` (método `efetivaTransacao` com try-catch genérico)
- Uso de strings literais em vários pontos ("D", "C", "N", "S") que poderiam ser constantes
- Falta de validação de entrada mais robusta (nulls tratados após recebimento)
- Logs de erro genéricos em alguns pontos
- Comentários escassos no código
- Alguns métodos poderiam ser quebrados em métodos menores para melhor legibilidade
- Falta de documentação JavaDoc nas classes principais
- Testes de integração e funcionais praticamente vazios

---

## 14. Observações Relevantes

1. **Dual Messaging**: O sistema suporta tanto RabbitMQ quanto Google Pub/Sub, com configuração condicional via propriedade `spring.cloud.gcp.pubsub.enabled`

2. **Conversão de Códigos de Banco**: Implementa conversão entre códigos externos (655→161, 436→413) para padronização interna

3. **Idempotência**: Implementa verificação de duplicidade baseada em NSU para garantir processamento único

4. **Reprocessamento**: Em caso de erro não tratado, mensagens são devolvidas para a fila para nova tentativa

5. **Ambientes**: Configurado para múltiplos ambientes (des, qa, uat, prd) com datasources e credenciais específicas

6. **Monitoramento**: Integração completa com Prometheus/Grafana para observabilidade

7. **Segurança**: Credenciais gerenciadas via cofre de senhas (referências `{{ cofre_senha.*}}`)

8. **Arquitetura Hexagonal**: Estrutura modular com separação clara entre domain, application e infrastructure

9. **Transações**: Uso de anotação `@Transaction` do JDBI para garantir atomicidade nas operações de banco

10. **Logs Estruturados**: Configuração de logs em formato JSON para facilitar análise e integração com ferramentas de observabilidade