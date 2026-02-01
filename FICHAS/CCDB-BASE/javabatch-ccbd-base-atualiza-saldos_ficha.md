## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema "javabatch-ccbd-base-atualiza-saldos" é um componente Java Batch que realiza a atualização de saldos de contas correntes. Ele utiliza o framework Spring para gerenciar beans e configurações, e integra-se com bancos de dados e sistemas de mensageria para executar rotinas de processamento de dados de contas bancárias.

### 2. Principais Classes e Responsabilidades
- **DateUtil**: Utilitário para manipulação de datas.
- **QueryReader**: Lê consultas SQL de arquivos XML.
- **ItemProcessor**: Processa dados de controle de contas.
- **ItemReader**: Lê dados de controle de contas.
- **ItemWriter**: Escreve dados de controle de contas.
- **MyResumeStrategy**: Estratégia de retomada de execução em caso de erro.
- **AtualizaFaixaContaRequest**: Representa uma solicitação de atualização de faixa de contas.
- **CodigoRotina**: Enumeração para códigos de rotina.
- **ContaRequest**: Representa uma solicitação de conta.
- **ControleData**: Representa dados de controle de movimentação de contas.
- **Parametro**: Representa parâmetros de configuração.
- **Rotina**: Representa uma rotina de execução.
- **RotinaExecucaoAgencia**: Representa a execução de uma rotina em uma agência.
- **RotinaStatus**: Enumeração para status de rotina.
- **ViradaDataThread**: Representa uma thread de virada de data.
- **ContaRepositoryImpl**: Implementação do repositório de contas.
- **ControleDataRepositoryImpl**: Implementação do repositório de dados de controle.
- **ParametroRepositoryImpl**: Implementação do repositório de parâmetros.
- **RotinaExecucaoAgenciaRepositoryImpl**: Implementação do repositório de execução de rotina em agência.
- **RotinaExecucaoRepositoryImpl**: Implementação do repositório de execução de rotina.
- **ViradaDataThreadRepositoryImpl**: Implementação do repositório de threads de virada de data.
- **ControleDataMapper**: Mapeia resultados de consultas para objetos ControleData.
- **MaximoDataInicioExecucaoMapper**: Mapeia resultados de consultas para datas de início de execução.
- **ParametroMapper**: Mapeia resultados de consultas para parâmetros.
- **RotinaExecucaoMapper**: Mapeia resultados de consultas para objetos Rotina.
- **TotalMapper**: Mapeia resultados de consultas para totais.
- **ContaService**: Serviço para manipulação de contas.
- **ControleDataService**: Serviço para manipulação de dados de controle.
- **FaixasThreadProcessor**: Processador de faixas de threads.
- **MessageService**: Serviço de mensageria.
- **ParametroService**: Serviço para manipulação de parâmetros.
- **RotinaExecucaoAgenciaService**: Serviço para execução de rotina em agência.
- **RotinaExecucaoService**: Serviço para execução de rotina.
- **ViradaThreadService**: Serviço para manipulação de threads de virada de data.

### 3. Tecnologias Utilizadas
- Java
- Apache Maven
- Spring Framework
- RabbitMQ
- MySQL
- Log4j
- Gson

### 4. Principais Endpoints REST
Não se aplica.

### 5. Principais Regras de Negócio
- Atualização de saldos de contas correntes.
- Verificação de dias úteis para movimentação de contas.
- Processamento de faixas de contas em threads.
- Envio de mensagens para atualização de valores de contas.

### 6. Relação entre Entidades
- **ControleData**: Relaciona-se com **ViradaDataThread** para gerenciar faixas de contas.
- **RotinaExecucaoAgencia**: Relaciona-se com **ControleData** para execução de rotinas em agências.
- **Rotina**: Utiliza **CodigoRotina** e **RotinaStatus** para definir o tipo e status da rotina.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo (tabela/view/coleção) | Operação (SELECT/READ) | Breve Descrição |
|-----------------------------|----------------------------|------------------------|-----------------|
| TbConta                     | tabela                     | SELECT                 | Contas correntes não encerradas |
| TbControleData              | tabela                     | SELECT                 | Datas de controle de movimentação |
| TbParametro                 | tabela                     | SELECT                 | Parâmetros de configuração |
| TbRotinaExecucaoAgencia     | tabela                     | SELECT                 | Execução de rotina em agência |
| TbRotinaExecucao            | tabela                     | SELECT                 | Execução de rotina |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo (tabela/view/coleção) | Operação (INSERT/UPDATE/DELETE) | Breve Descrição |
|-----------------------------|----------------------------|---------------------------------|-----------------|
| TbControleData              | tabela                     | UPDATE                          | Atualização de dados de controle |
| TbRotinaExecucaoAgencia     | tabela                     | UPDATE                          | Atualização de execução de rotina em agência |
| TbRotinaExecucao            | tabela                     | UPDATE                          | Atualização de execução de rotina |
| TbViradaDataThread          | tabela                     | INSERT/UPDATE/DELETE            | Manipulação de threads de virada de data |

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
- **ex.ccbd.viraConta**: Utilizada para enviar mensagens de atualização de contas.

### 11. Integrações Externas
- RabbitMQ: Utilizado para envio de mensagens.
- Banco de dados MySQL: Utilizado para armazenamento de dados de contas e controle.
- Banco de dados Sybase: Utilizado para verificação de dias úteis.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado, utiliza boas práticas de programação e está organizado em pacotes e classes com responsabilidades bem definidas. A integração com o Spring Framework facilita o gerenciamento de dependências e configurações. No entanto, a documentação poderia ser mais detalhada em alguns pontos para facilitar o entendimento de novos desenvolvedores.

### 13. Observações Relevantes
- O sistema utiliza procedimentos armazenados para verificar dias úteis e calcular próximos dias úteis, o que pode impactar a portabilidade para outros bancos de dados.
- A configuração de segurança para acesso ao banco de dados utiliza criptografia, garantindo a proteção de credenciais sensíveis.