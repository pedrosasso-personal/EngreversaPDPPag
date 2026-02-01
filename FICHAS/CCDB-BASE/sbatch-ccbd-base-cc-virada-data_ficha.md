## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é uma aplicação Spring Batch desenvolvida para realizar o processo de atualização da data contábil em um banco de dados. Ele utiliza o framework Spring Batch para orquestrar tarefas de processamento de dados, incluindo leitura, processamento e escrita de informações relacionadas a contas correntes e execução de rotinas.

### 2. Principais Classes e Responsabilidades
- **SpringBatchApplication**: Classe principal que inicia a aplicação Spring Batch.
- **BatchConfiguration**: Configura o job principal do Spring Batch, definindo os steps e o listener para tratamento de erros.
- **DbContaCorrenteDataSourceConfig**: Configuração do datasource para conexão com o banco de dados Sybase.
- **ControleDataService**: Serviço responsável por validar e calcular datas relacionadas ao controle de dados.
- **RotinaExecucaoService**: Serviço que gerencia a execução de rotinas, incluindo inicialização e finalização.
- **CalendarioRepositoryImpl**: Implementação do repositório que interage com a API de calendário para verificar dias úteis.
- **PubSubContasWriter**: Writer que publica mensagens em um tópico Pub/Sub do Google Cloud.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Batch
- Spring Boot
- JDBI
- Google Cloud Pub/Sub
- Sybase JDBC
- Swagger

### 4. Principais Endpoints REST
Não se aplica.

### 5. Principais Regras de Negócio
- Validação de datas contábeis para garantir que sejam dias úteis.
- Atualização de parâmetros de data no banco de dados.
- Publicação de mensagens em tópicos Pub/Sub para contas ativas.
- Execução de rotinas de processamento de dados contábeis.

### 6. Relação entre Entidades
- **Conta**: Representa uma conta corrente com atributos como banco, número da conta e tipo de conta.
- **ControleData**: Contém informações sobre datas de movimento e controle, como datas passadas e futuras.
- **RotinaExecucao**: Representa a execução de uma rotina, incluindo status e problemas associados.
- **RotinaExecucaoAgencia**: Similar à RotinaExecucao, mas específica para agências bancárias.

### 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo (tabela/view/coleção) | Operação (SELECT/READ) | Breve Descrição |
|-----------------------------|----------------------------|------------------------|-----------------|
| TbConta                     | tabela                     | SELECT                 | Consulta contas não encerradas. |
| TbControleData              | tabela                     | SELECT                 | Consulta dados de controle de datas. |
| TbRotinaExecucaoAgencia     | tabela                     | SELECT                 | Consulta execução de rotinas por agência. |
| TbRotinaExecucao            | tabela                     | SELECT                 | Consulta execução de rotinas. |

### 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo (tabela/view/coleção) | Operação (INSERT/UPDATE/DELETE) | Breve Descrição |
|-----------------------------|----------------------------|-------------------------------|-----------------|
| TbControleData              | tabela                     | UPDATE                        | Atualiza dados de controle de datas. |
| TbParametro                 | tabela                     | UPDATE                        | Atualiza parâmetros de data. |
| TbRotinaExecucaoAgencia     | tabela                     | INSERT/UPDATE                 | Insere e atualiza execução de rotinas por agência. |
| TbRotinaExecucaoProblema    | tabela                     | INSERT/DELETE                 | Insere e deleta problemas de execução de rotinas. |
| TbRotinaExecucao            | tabela                     | INSERT/UPDATE                 | Insere e atualiza execução de rotinas. |

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
- **business-ccbd-base-conta-ativa**: Tópico Pub/Sub onde são publicadas mensagens sobre contas ativas.

### 11. Integrações Externas
- **API de Calendário**: Utilizada para verificar dias úteis e calcular prazos.
- **Google Cloud Pub/Sub**: Utilizado para publicação de mensagens sobre contas ativas.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de programação, como injeção de dependências e uso de annotations do Spring. A organização em pacotes é clara e facilita a manutenção. No entanto, a complexidade de algumas classes pode ser reduzida para melhorar a legibilidade.

### 13. Observações Relevantes
- O sistema utiliza o framework Spring Batch para gerenciar tarefas de processamento de dados de forma eficiente.
- A integração com o Google Cloud Pub/Sub permite escalabilidade na publicação de mensagens sobre contas ativas.
- A validação de datas contábeis é crítica para o funcionamento correto do sistema, garantindo que operações sejam realizadas apenas em dias úteis.