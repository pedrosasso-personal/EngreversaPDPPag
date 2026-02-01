```markdown
## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um serviço atômico responsável por gerenciar as transações executadas pelos parceiros para o pagamento de rebate. Ele utiliza Java com Spring Boot e integra-se com IBM MQ para processamento de mensagens, além de expor APIs REST para consulta e manipulação de dados de transações.

### 2. Principais Classes e Responsabilidades
- **Application**: Classe principal que inicia a aplicação Spring Boot.
- **ConsolidadoTransacaoController**: Controlador que gerencia endpoints relacionados a transações consolidadas.
- **DetalheTransacaoController**: Controlador que gerencia endpoints relacionados a transações detalhadas.
- **ConsolidadoTransacaoService**: Serviço que contém a lógica de negócios para transações consolidadas.
- **DetalheTransacaoService**: Serviço que contém a lógica de negócios para transações detalhadas.
- **JdbiConsolidadoTransacaoRepository**: Repositório para operações de banco de dados relacionadas a transações consolidadas.
- **JdbiDetalheTransacaoRepository**: Repositório para operações de banco de dados relacionadas a transações detalhadas.
- **MQAdapter**: Adaptador para conversão de objetos em mensagens JSON para envio via MQ.
- **TransacaoErrorHandler**: Handler para tratamento de erros em operações de MQ.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- JDBI
- IBM MQ
- Swagger
- Prometheus
- Grafana

### 4. Principais Endpoints REST
| Método | Endpoint          | Classe Controladora             | Descrição                                                                 |
|--------|-------------------|---------------------------------|---------------------------------------------------------------------------|
| GET    | /consolidados     | ConsolidadoTransacaoController  | Lista transações consolidadas com base em parâmetros de apuração bancária.|
| GET    | /transacoes       | DetalheTransacaoController      | Lista transações detalhadas com base em filtros de cliente e datas.       |

### 5. Principais Regras de Negócio
- Consolidação de transações rebate por dia, com inativação de registros existentes antes de nova inserção.
- Apuração bancária diferenciada entre mesmo banco, outros bancos ou ambos.
- Publicação de mensagens de sucesso ou falha após processamento de transações.

### 6. Relação entre Entidades
- **ConsolidadoTransacao**: Representa uma transação consolidada, incluindo informações como produto, cliente e valores totais.
- **DetalheTransacao**: Representa uma transação detalhada, incluindo informações como produto, cliente, valor e detalhes de movimentação.
- **RetornoConsolidado** e **RetornoDetalhado**: Entidades para retorno de status de processamento de transações.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção               | Tipo     | Operação | Breve Descrição                                                                 |
|-------------------------------------------|----------|----------|---------------------------------------------------------------------------------|
| TbTransacaoConsolidadoRebate              | tabela   | SELECT   | Armazena transações consolidadas de rebate.                                     |
| TbTransacaoDetalheRebate                  | tabela   | SELECT   | Armazena transações detalhadas de rebate.                                       |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção               | Tipo     | Operação          | Breve Descrição                                                                 |
|-------------------------------------------|----------|-------------------|---------------------------------------------------------------------------------|
| TbTransacaoConsolidadoRebate              | tabela   | INSERT/UPDATE     | Inserção e inativação de registros consolidados de rebate.                      |
| TbTransacaoDetalheRebate                  | tabela   | INSERT            | Inserção de registros detalhados de rebate.                                     |

### 9. Filas Lidas
- DEV.QUEUE.1
- DEV.QUEUE.3

### 10. Filas Geradas
- DEV.QUEUE.2
- DEV.QUEUE.4

### 11. Integrações Externas
- IBM MQ para processamento de mensagens de transações.
- APIs REST expostas via Swagger para consulta de transações.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de desenvolvimento, como injeção de dependências e uso de padrões de projeto. A documentação está presente e os testes cobrem funcionalidades principais. Poderia melhorar em aspectos de tratamento de exceções e cobertura de testes.

### 13. Observações Relevantes
- O sistema utiliza Docker para facilitar a execução de serviços como IBM MQ, Prometheus e Grafana.
- A configuração de ambientes é gerida por arquivos YAML, permitindo flexibilidade na configuração de diferentes ambientes de execução.
```