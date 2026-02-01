## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é uma aplicação batch desenvolvida em Java utilizando o framework Spring Batch. Seu objetivo é processar transações financeiras, realizando operações de leitura, processamento e escrita de dados relacionados a ocorrências de transações. A aplicação integra-se com serviços externos para obter dados de transações e realizar operações de reversão de pagamentos.

### 2. Principais Classes e Responsabilidades
- **BatchConfiguration**: Configura o job de processamento de transações.
- **StepConfiguration**: Define os steps do job, incluindo leitores, processadores e escritores de itens.
- **BankAccountProperties, GatewayProperties, ServicesProperties**: Classes de configuração de propriedades da aplicação.
- **DataSourceConfig**: Configura as fontes de dados SQL Server e Sybase.
- **TransactionOccurrencyService**: Serviço principal para operações de transações, incluindo obtenção de ocorrências e reversão de pagamentos.
- **TransactionOccurrencyItemProcessor**: Processador de itens que transforma ocorrências de transações em transações de pagamento.
- **TransactionOccurrencyBVItemReader, TransactionOccurrencyBVSAItemReader**: Leitores de itens para ocorrências de transações de diferentes bancos.
- **TransactionOccurrencyItemWriter**: Escritor de itens que realiza a reversão de pagamentos.
- **HttpTransferenciaRepositoryImpl, TransactionOccurrencyRepositoryImpl**: Implementações de repositórios para integração com serviços HTTP.
- **PaymentTransactionMapper, TransferRepresentationMapper**: Mapeadores para transformar dados entre diferentes representações.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Batch
- Spring Boot
- JDBI
- SQL Server
- Sybase
- Maven

### 4. Principais Endpoints REST
Não se aplica.

### 5. Principais Regras de Negócio
- Processamento de transações financeiras de diferentes bancos.
- Reversão de pagamentos com base em condições específicas.
- Integração com serviços externos para obtenção de dados de transações e tokens de autenticação.

### 6. Relação entre Entidades
- **TransactionOccurrency**: Entidade de domínio representando uma ocorrência de transação.
- **PaymentTransaction**: Entidade de domínio representando uma transação de pagamento.
- **Participant**: Entidade representando participantes de transações, como remetente e favorecido.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo (tabela/view/coleção) | Operação (SELECT/READ) | Breve Descrição |
|-----------------------------|----------------------------|------------------------|-----------------|
| TbControleMigracaoParticipante | tabela | SELECT | Obtém dados de migração de clientes. |
| TbLancamento | tabela | SELECT | Obtém dados de lançamentos de transações. |
| TbLancamentoPessoa | tabela | SELECT | Obtém dados de pessoas envolvidas em lançamentos. |
| TbLancamentoClienteFintech | tabela | SELECT | Obtém dados de clientes fintech envolvidos em lançamentos. |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo (tabela/view/coleção) | Operação (INSERT/UPDATE/DELETE) | Breve Descrição |
|-----------------------------|----------------------------|-------------------------------|-----------------|
| TBL_CAIXA_ENTRADA_SPB | tabela | UPDATE | Atualiza protocolo de devolução. |
| tbl_lancamento | tabela | UPDATE | Atualiza protocolo de devolução. |
| TbLancamento | tabela | UPDATE | Confirma reversão de lançamento. |

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- **API Gateway**: Integração para autenticação e obtenção de tokens.
- **Serviço de Transações**: Integração para obtenção de ocorrências de transações.
- **Serviço de Transferências**: Integração para realizar transferências de pagamento.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de programação, como injeção de dependências e uso de mapeadores. A documentação interna é adequada, e os testes unitários cobrem uma boa parte das funcionalidades. No entanto, a complexidade de algumas classes pode ser reduzida para melhorar a legibilidade.

### 13. Observações Relevantes
- A aplicação utiliza configurações específicas para diferentes ambientes (local, des, qa, uat, prd).
- O sistema possui integração com ferramentas de monitoramento como Prometheus e Grafana, além de suporte para RabbitMQ.
- A documentação do projeto está incompleta no arquivo README.md, necessitando de uma descrição mais detalhada do projeto.