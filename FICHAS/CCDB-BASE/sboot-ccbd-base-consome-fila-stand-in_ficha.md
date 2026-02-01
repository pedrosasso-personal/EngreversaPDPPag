## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema "DebConsomeFilaStandIn" é um serviço atômico desenvolvido em Java utilizando o framework Spring Boot. Ele é responsável por consumir mensagens de uma fila JMS, processar transações financeiras e interagir com bancos de dados para gerenciar informações de contas correntes e transações de cartão de débito.

### 2. Principais Classes e Responsabilidades
- **Application**: Classe principal que inicia a aplicação Spring Boot.
- **ConfigurationListener**: Configura o listener JMS para consumir mensagens da fila.
- **DataSourceConfiguration**: Configura as fontes de dados para Sybase e SQL Server.
- **DebConsomeFilaStandInConfiguration**: Configura os serviços e repositórios utilizados na aplicação.
- **CacheController**: Controlador REST para operações de cache.
- **DebConsomeFilaStandInListener**: Listener JMS que processa mensagens de transações.
- **CacheService**: Serviço que gerencia operações de cache.
- **DebConsomeFilaStandInService**: Serviço que processa transações financeiras.
- **Transacao**: Classe de domínio que representa uma transação financeira.
- **CacheRepositoryImpl, CCBDRepositoryImpl, ContaCorrenteRepositoryImpl**: Implementações de repositórios para interações com o banco de dados.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- JDBI
- Swagger
- Sybase
- SQL Server
- JMS (IBM MQ)
- Docker

### 4. Principais Endpoints REST
| Método | Endpoint                     | Classe Controladora | Descrição                                    |
|--------|------------------------------|---------------------|----------------------------------------------|
| POST   | /v1/transacao-cache/inserir  | CacheController     | Insere uma transação no cache.               |

### 5. Principais Regras de Negócio
- Verificação de existência de transação antes de inserção.
- Validação de saldo de conta antes de realizar transações.
- Inserção de transações não autorizadas em caso de saldo insuficiente.
- Atualização de saldo bloqueado em contas correntes.

### 6. Relação entre Entidades
- **Transacao** possui relação com **Cartao** e **Estabelecimento**.
- **InsertTransactionEntity** mapeia dados de transações para persistência.
- **InsertBlockBalanceEntity** mapeia dados de bloqueio de saldo.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção                      | Tipo       | Operação | Breve Descrição                                      |
|--------------------------------------------------|------------|----------|------------------------------------------------------|
| TbControleTransacaoCartao                        | tabela     | SELECT   | Verifica existência de transações.                   |
| TbConta                                          | tabela     | SELECT   | Verifica saldo de contas correntes.                  |
| TbControleData                                   | tabela     | SELECT   | Verifica aceitação de movimentação.                  |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção                      | Tipo       | Operação | Breve Descrição                                      |
|--------------------------------------------------|------------|----------|------------------------------------------------------|
| TbProcessamentoContaStandIn                      | tabela     | INSERT   | Insere transações de cache.                          |
| TbTransacaoCartao                                | tabela     | INSERT   | Insere transações de cartão.                         |
| TbEstabelecimentoComercial                       | tabela     | INSERT   | Insere dados de estabelecimentos comerciais.         |
| TbControleTransacaoCartao                        | tabela     | INSERT   | Insere transações autorizadas e não autorizadas.     |
| TbSaldoBloqueado                                 | tabela     | INSERT   | Insere dados de saldo bloqueado.                     |

### 9. Filas Lidas
- QL.CCBD_PROC_TRANSAC_STAND_IN.INT

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- IBM MQ para consumo de mensagens.
- Sybase e SQL Server para operações de banco de dados.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de programação, como injeção de dependências e uso de interfaces para repositórios. A documentação e os testes são adequados, mas poderiam ser mais detalhados em algumas áreas para melhorar a manutenibilidade.

### 13. Observações Relevantes
- O projeto utiliza o Swagger para documentação de APIs.
- A configuração de filas JMS e fontes de dados é feita através de arquivos de configuração YAML.
- O sistema é projetado para ser executado em ambientes de contêineres, com suporte a Docker e Kubernetes.