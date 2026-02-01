## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é uma aplicação batch desenvolvida em Java utilizando o framework Spring Batch. Seu objetivo é integrar e processar baixas de boletos, realizando operações de leitura, processamento e escrita de dados relacionados a boletos. A aplicação utiliza o Google Cloud Pub/Sub para publicação de mensagens e integra-se com bancos de dados Sybase e SQL Server para manipulação de registros de pagamento.

### 2. Principais Classes e Responsabilidades
- **BatchConfiguration**: Configura o job de processamento de boletos, definindo os steps a serem executados.
- **StepConfiguration**: Define os steps de leitura, processamento e escrita de boletos.
- **PubSubProperties**: Gerencia as propriedades de configuração do Google Cloud Pub/Sub.
- **DataSourceConfig**: Configura as fontes de dados para conexão com os bancos de dados.
- **DefaultBatchConfigurerConfig**: Configura o batch para utilizar uma fonte de dados específica.
- **IntegracaoBaixaBoletoConfiguration**: Configura serviços e conversores de mensagens para integração de baixa de boletos.
- **JdbiConfiguration**: Configura o Jdbi para acesso ao banco de dados.
- **TaskConfig**: Configura tarefas do Spring Cloud Task.
- **BaixaBoleto**: Representa um boleto a ser processado.
- **NotificacaoBaixaBoleto**: Representa uma notificação de baixa de boleto.
- **RegistroPagamento**: Representa um registro de pagamento.
- **BatchExitCodeGenerator**: Gera códigos de saída para o batch.
- **JdbiPgftRepositoryImpl**: Implementação do repositório Jdbi para operações no banco PGFT.
- **JdbiSpagRepositoryImpl**: Implementação do repositório Jdbi para operações no banco SPAG.
- **IntegracaoBaixaBoletoPublisherImpl**: Implementação do publisher para envio de notificações de baixa de boleto.
- **BaixaBoletoProcessor**: Processa boletos para gerar notificações de baixa.
- **BaixaBoletoSpagProcessor**: Processa boletos SPAG para gerar notificações de baixa.
- **BaixaBoletoReader**: Lê boletos do banco PGFT.
- **BaixaBoletoSpagReader**: Lê boletos do banco SPAG.
- **BaixaBoletoSpagWriter**: Escreve notificações de baixa de boletos SPAG.
- **BaixaBoletoWriter**: Escreve notificações de baixa de boletos.
- **CodigoBarrasUtils**: Utilitário para manipulação de códigos de barras.
- **LocalDateUtils**: Utilitário para manipulação de datas.
- **BaixaBoletoRowMapper**: Mapeia resultados de consultas para objetos BaixaBoleto.
- **NotificacaoBaixaBoletoMapper**: Mapeia objetos BaixaBoleto para NotificacaoBaixaBoleto.
- **IntegracaoBaixaBoletoPublisher**: Interface para publicação de notificações de baixa de boleto.
- **JdbiRepository**: Interface para operações de banco de dados.
- **BoletoPgftService**: Serviço para manipulação de boletos PGFT.
- **BoletoService**: Serviço base para manipulação de boletos.
- **BoletoSpagService**: Serviço para manipulação de boletos SPAG.
- **Application**: Classe principal para inicialização da aplicação.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Batch
- Spring Boot
- Google Cloud Pub/Sub
- Jdbi
- Sybase
- SQL Server
- Maven

### 4. Principais Endpoints REST
Não se aplica.

### 5. Principais Regras de Negócio
- Processamento de boletos para geração de notificações de baixa.
- Atualização de status de notificação de baixa no banco de dados.
- Publicação de notificações de baixa de boletos no Google Cloud Pub/Sub.

### 6. Relação entre Entidades
- **BaixaBoleto**: Entidade principal representando um boleto a ser processado.
- **NotificacaoBaixaBoleto**: Entidade derivada de BaixaBoleto para notificação.
- **RegistroPagamento**: Entidade para registro de status de pagamento.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo (tabela/view/coleção) | Operação (SELECT/READ) | Breve Descrição |
|-----------------------------|----------------------------|------------------------|-----------------|
| TbRetornoBaixaOperacionalCIP | tabela | SELECT | Armazena retornos de baixa operacional de boletos. |
| TbRegistroPagamentoCIP | tabela | SELECT | Armazena registros de pagamento de boletos. |
| TBL_LANCAMENTO | tabela | SELECT | Armazena lançamentos relacionados a boletos. |
| TBL_CAIXA_ENTRADA_SPB | tabela | SELECT | Armazena entradas de caixa relacionadas a boletos. |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo (tabela/view/coleção) | Operação (INSERT/UPDATE/DELETE) | Breve Descrição |
|-----------------------------|----------------------------|-------------------------------|-----------------|
| TbRegistroPagamentoCIP | tabela | UPDATE | Atualiza o status de notificação de baixa de boletos. |

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
- **Google Cloud Pub/Sub**: Publicação de notificações de baixa de boletos.

### 11. Integrações Externas
- **Google Cloud Pub/Sub**: Utilizado para publicação de mensagens de notificação de baixa de boletos.
- **Sybase**: Banco de dados utilizado para armazenamento de registros de pagamento.
- **SQL Server**: Banco de dados utilizado para armazenamento de registros de pagamento.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de programação, como injeção de dependências e uso de interfaces para abstração. A documentação e os testes unitários estão presentes, garantindo a manutenibilidade e clareza do código. No entanto, a descrição do projeto no README está incompleta, o que pode dificultar o entendimento inicial do sistema.

### 13. Observações Relevantes
- A aplicação utiliza o Spring Batch para processamento de dados em lote, o que é adequado para o tipo de operação realizada.
- A integração com o Google Cloud Pub/Sub permite escalabilidade na publicação de mensagens de notificação.
- O uso de Jdbi facilita o acesso e manipulação de dados nos bancos de dados Sybase e SQL Server.