## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um serviço atômico de conciliação de transações, desenvolvido para processar e conciliar transações de cartão de débito. Ele utiliza o framework Spring Boot e integra-se com RabbitMQ e Google Cloud Pub/Sub para comunicação assíncrona. O sistema lê e grava dados em um banco de dados SQL Server, realizando operações de inserção e consulta.

### 2. Principais Classes e Responsabilidades
- **ConciliacaoTransacaoConfiguration**: Configurações de beans para RabbitMQ, PubSub e repositório.
- **DataBaseConfiguration**: Configuração do banco de dados utilizando Jdbi para interação com SQL Server.
- **OpenApiConfiguration**: Configuração do Swagger para documentação de APIs.
- **PubSubProperties**: Propriedades de configuração para tópicos do Google Cloud Pub/Sub.
- **CCBDRepositoryImpl**: Implementação do repositório para operações de banco de dados.
- **ConciliacaoTransacaoListener**: Listener para mensagens do RabbitMQ, processando transações.
- **PubSubPublishServiceImpl**: Implementação do serviço de publicação de mensagens no PubSub.
- **ConciliacaoTransacaoServiceImpl**: Implementação do serviço de conciliação de transações.
- **ConciliacaoTransacaoDTO**: DTO para transferência de dados de transações.
- **ConciliacaoTransacao**: Entidade representando uma transação conciliada.
- **ConciliacaoTransacaoComplementares**: Entidade representando dados complementares de uma transação.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- Maven
- SQL Server
- Jdbi
- RabbitMQ
- Google Cloud Pub/Sub
- Swagger
- Docker

### 4. Principais Endpoints REST
Não se aplica.

### 5. Principais Regras de Negócio
- Processamento de transações de cartão de débito.
- Verificação de tipos de arquivos e transações para decidir o método de processamento.
- Inserção de dados de transações e complementares no banco de dados.
- Publicação de mensagens no PubSub para arquivos não relacionais.

### 6. Relação entre Entidades
- **ConciliacaoTransacao**: Relaciona-se com **ConciliacaoTransacaoComplementares** para armazenar dados complementares.
- **ConciliacaoTransacaoDTO**: Utilizado para transferir dados entre camadas.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbArquivoOrigem             | tabela | SELECT   | Consulta o código de origem do arquivo. |
| TbTipoTransacao             | tabela | SELECT   | Consulta o tipo de transação. |
| TbStatusProcessamento       | tabela | SELECT   | Consulta o status de processamento. |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbConciliacaoTransacao      | tabela | INSERT   | Insere dados de transações conciliadas. |
| TbComplementoConciliacaoTrnso | tabela | INSERT | Insere dados complementares de transações. |

### 9. Filas Lidas
- **events.business.CCBD-BASE.registroBandeira**: Fila RabbitMQ para leitura de mensagens de transações.

### 10. Filas Geradas
- **events.ex.business.ccbd.registroBandeiraDLQ**: Fila RabbitMQ para mensagens de erro.
- **Google Cloud Pub/Sub**: Publicação de mensagens para arquivos não relacionais.

### 11. Integrações Externas
- RabbitMQ: Para comunicação assíncrona de mensagens de transações.
- Google Cloud Pub/Sub: Para publicação de mensagens de arquivos não relacionais.
- SQL Server: Banco de dados para armazenamento de transações e dados complementares.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de programação, como injeção de dependências e uso de DTOs para transferência de dados. A documentação e configuração de Swagger para APIs são adequadas. No entanto, a ausência de endpoints REST pode limitar a interação com o sistema.

### 13. Observações Relevantes
- O sistema utiliza Docker para containerização, facilitando a implantação e execução em ambientes diversos.
- A configuração de segurança e variáveis de ambiente é gerida por arquivos YAML e propriedades, garantindo flexibilidade e segurança na operação.