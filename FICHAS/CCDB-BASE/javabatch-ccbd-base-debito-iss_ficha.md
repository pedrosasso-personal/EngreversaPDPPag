## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um projeto Java Batch que executa consultas no banco de dados DBCONTACORRENTE para recuperar informações que compõem o arquivo DebitoIss. Após a consulta bem-sucedida, os dados são postados em uma fila MQ.

### 2. Principais Classes e Responsabilidades
- **ItemProcessor**: Processa objetos `TransacaoDebito` e os prepara para serem escritos.
- **ItemReader**: Lê transações de débito do repositório e as prepara para processamento.
- **ItemWriter**: Escreve objetos `TransacaoDebito` em uma fila RabbitMQ.
- **MyResumeStrategy**: Define a estratégia de retomada do job em caso de falhas.
- **TransacaoDebito**: Representa uma transação de débito com atributos como banco, conta corrente, tipo de conta, protocolo, data de lançamento e valor da operação.
- **TransacaoDebitoException**: Exceção personalizada para erros relacionados a transações de débito.
- **TransacaoDebitoMapper**: Mapeia resultados de consultas SQL para objetos `TransacaoDebito`.
- **TransacaoRepository**: Interface para operações de consulta de transações de débito.
- **TransacaoRepositoryImpl**: Implementação da interface `TransacaoRepository` usando `NamedParameterJdbcTemplate`.
- **ConstantsUtils**: Define constantes utilizadas no sistema.
- **DateUtils**: Utilitário para manipulação de datas.

### 3. Tecnologias Utilizadas
- Java
- Maven
- Spring Framework
- RabbitMQ
- JUnit
- Mockito
- Sybase JDBC Driver
- Apache POI
- Jackson

### 4. Principais Endpoints REST
Não se aplica.

### 5. Principais Regras de Negócio
- Consultar transações de débito dos últimos 7 dias.
- Postar transações de débito em uma fila RabbitMQ.
- Manipulação de exceções específicas para transações de débito.

### 6. Relação entre Entidades
- **TransacaoDebito**: Entidade principal representando uma transação de débito.
- **TransacaoDebitoMapper**: Mapeia resultados de consultas SQL para `TransacaoDebito`.

### 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo (tabela/view/coleção) | Operação (SELECT/READ) | Breve Descrição |
|-----------------------------|----------------------------|------------------------|-----------------|
| TbHistoricoMovimento        | tabela                     | SELECT                 | Consulta transações de débito com base na data de efetivação da operação. |

### 8. Estruturas de Banco de Dados Atualizadas
Não se aplica.

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
- **events.ex.business.ccbd.debitoIss**: Fila RabbitMQ onde são postadas as transações de débito processadas.

### 11. Integrações Externas
- RabbitMQ: Utilizado para postar mensagens de transações de débito.
- Banco de dados DBCONTACORRENTE: Consultas para recuperar transações de débito.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de programação, como o uso de interfaces e exceções personalizadas. A integração com RabbitMQ e o uso de Spring Framework são bem implementados. Poderia haver uma documentação mais detalhada sobre algumas classes e métodos.

### 13. Observações Relevantes
- O projeto requer Java 1.6 e Maven 3.3+ para compilação e execução.
- É necessário configurar o RabbitMQ localmente para testes.
- O projeto utiliza um modelo de batch para processamento de dados em massa.