## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um aplicativo Java que utiliza o framework Spring Batch para processar e enviar PDFs de carnês de pagamento. Ele integra-se com o RabbitMQ para publicar mensagens e utiliza um banco de dados Sybase para obter dados de contratos e carnês.

### 2. Principais Classes e Responsabilidades
- **BusinessException**: Classe de exceção para erros de negócio.
- **RecepcaoMQException**: Classe de exceção para erros na recepção de mensagens MQ.
- **Carne**: Modelo que representa um carnê de pagamento.
- **Cliente**: Modelo que representa um cliente, incluindo informações de endereço.
- **Contrato**: Modelo que representa um contrato, incluindo dados de entrega de documentos e pessoa.
- **ContratoLote**: Modelo que encapsula um contrato.
- **DadosCarne**: Modelo que contém uma lista de carnês e informações de cliente e veículo legal.
- **Endereco**: Modelo que representa um endereço.
- **EntregaDocumento**: Modelo que representa a entrega de documentos.
- **InputUnitOfWork**: Modelo que representa uma unidade de trabalho de entrada, contendo contratos.
- **OutputUnitOfWork**: Modelo que representa uma unidade de trabalho de saída, contendo contratos.
- **Pessoa**: Modelo que representa uma pessoa, incluindo informações de contato e endereço.
- **VeiculoLegal**: Modelo que representa um veículo legal, incluindo informações de endereço.
- **RabbitRepositoryImpl**: Implementação do repositório MQ para conexão e publicação de mensagens no RabbitMQ.
- **MQRepository**: Interface para operações de MQ.
- **Repository**: Classe para operações de repositório, como obtenção de dados de contratos.
- **MQServiceImpl**: Implementação do serviço MQ para gerenciar transações e publicação de mensagens.
- **MQService**: Interface para operações de serviço MQ.
- **CarneContratoSQL**: Classe que contém consultas SQL para obtenção de dados de contratos e carnês.
- **ExitCodeEnum**: Enumeração para códigos de saída do processo batch.
- **JobUtil**: Utilitário para validação de parâmetros de job.
- **ItemProcessor**: Classe para processamento de itens no batch.
- **ItemReader**: Classe para leitura de itens no batch.
- **ItemWriter**: Classe para escrita de itens no batch.
- **MyResumeStrategy**: Estratégia de retomada de execução de jobs.
- **CarneContratoDAOImpl**: Implementação do DAO para obtenção de dados de contratos e carnês.
- **CarneContratoDAO**: Interface para operações de DAO de contratos e carnês.
- **CarneRowMapper**: Mapeador de linhas para objetos Carne.
- **ContratoRowMapper**: Mapeador de linhas para objetos Contrato.

### 3. Tecnologias Utilizadas
- Java
- Spring Batch
- Maven
- RabbitMQ
- Sybase (Driver JDBC)
- Gson
- JUnit

### 4. Principais Endpoints REST
Não se aplica.

### 5. Principais Regras de Negócio
- Validação de parâmetros de entrada para o job batch.
- Obtenção de dados de contratos e carnês a partir de consultas SQL.
- Publicação de mensagens no RabbitMQ após processamento de contratos.
- Tratamento de exceções específicas para erros de negócio e MQ.

### 6. Relação entre Entidades
- **Contrato** possui um **DadosCarne**, que contém uma lista de **Carne** e um **Cliente**.
- **Cliente** possui um **Endereco**.
- **VeiculoLegal** possui um **Endereco**.
- **EntregaDocumento** está associado a um **Contrato**.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo (tabela/view/coleção) | Operação (SELECT/READ) | Breve Descrição |
|-----------------------------|----------------------------|------------------------|-----------------|
| STGTXT_FLEX.TbContrato      | tabela                     | SELECT                 | Dados de contratos. |
| STGTXT_FLEX.TbPessoa        | tabela                     | SELECT                 | Dados de pessoas associadas aos contratos. |
| STGTXT_FLEX.TbPessoaEndereco| tabela                     | SELECT                 | Endereços das pessoas. |
| DBCOR.TbVeiculoLegal        | tabela                     | SELECT                 | Dados de veículos legais. |
| STGTXT_FLEX.CLTM_BOLETO_DET | tabela                     | SELECT                 | Detalhes de boletos para carnês. |

### 8. Estruturas de Banco de Dados Atualizadas
Não se aplica.

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
- RabbitMQ: Publicação de mensagens de contratos processados.

### 11. Integrações Externas
- RabbitMQ: Utilizado para publicação de mensagens.
- Banco de dados Sybase: Utilizado para leitura de dados de contratos e carnês.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de programação, como a separação de responsabilidades em classes distintas e o uso de interfaces para abstração. A integração com RabbitMQ e o uso de Spring Batch são bem implementados. No entanto, poderia haver mais comentários explicativos em algumas partes do código para melhorar a legibilidade e manutenção.

### 13. Observações Relevantes
- O sistema possui uma configuração robusta para integração com RabbitMQ e leitura de dados de um banco de dados Sybase.
- A validação de parâmetros de entrada é crítica para o funcionamento correto do job batch.
- O uso de mapeadores de linha facilita a conversão de resultados de consultas SQL em objetos de modelo.