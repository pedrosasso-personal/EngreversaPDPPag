## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um projeto Java que utiliza o framework Maven para gerenciamento de dependências e construção. Ele é responsável pelo agendamento de transações financeiras via PIX, realizando operações de leitura, processamento e envio de dados para filas RabbitMQ.

### 2. Principais Classes e Responsabilidades
- **ItemProcessor**: Processa objetos do tipo `Lancamento`, registrando logs durante o processo.
- **ItemReader**: Lê dados de agendamentos do banco de dados e os transforma em objetos `Lancamento`.
- **ItemWriter**: Envia objetos `Lancamento` para uma fila RabbitMQ após convertê-los para JSON.
- **MyResumeStrategy**: Define a estratégia de retomada de execução de jobs.
- **LancamentoMapper**: Mapeia resultados de consultas SQL para objetos `Lancamento`.
- **AgendamentoRepository**: Interface para recuperação de lançamentos de agendamentos.
- **AgendamentoRepositoryImpl**: Implementação da interface `AgendamentoRepository`, realizando consultas SQL para recuperar lançamentos.
- **AgendamentoUtil**: Utilitário para carregar consultas SQL de arquivos XML.
- **Lancamento**: Representa um agendamento financeiro com diversos atributos relacionados à transação.
- **Pessoa**: Representa uma pessoa envolvida na transação, seja remetente ou favorecido.

### 3. Tecnologias Utilizadas
- Java
- Maven
- Spring Framework
- RabbitMQ
- Log4j
- Gson
- JUnit
- Mockito

### 4. Principais Endpoints REST
Não se aplica.

### 5. Principais Regras de Negócio
- Recuperação de lançamentos de agendamentos com base na data de agendamento.
- Envio de lançamentos para fila RabbitMQ após processamento.
- Estratégia de retomada de execução de jobs baseada em códigos de saída.

### 6. Relação entre Entidades
- **Lancamento** possui relação com **Pessoa** através dos atributos `remetente` e `favorecido`.
- **LancamentoMapper** mapeia dados de tabelas SQL para objetos `Lancamento`.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo (tabela/view/coleção) | Operação (SELECT/READ) | Breve Descrição |
|-----------------------------|----------------------------|------------------------|-----------------|
| TbAgendamento               | tabela                     | SELECT                 | Contém dados de agendamentos financeiros. |
| TbPessoaAgendamento         | tabela                     | SELECT                 | Contém dados de pessoas envolvidas nos agendamentos. |
| TbStatusAgendamento         | tabela                     | SELECT                 | Contém dados de status dos agendamentos. |

### 8. Estruturas de Banco de Dados Atualizadas
Não se aplica.

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
- **ex.ccbd.agendamento**: Fila RabbitMQ para onde os lançamentos são enviados após processamento.

### 11. Integrações Externas
- RabbitMQ: Utilizado para envio de mensagens de lançamentos processados.
- Banco de dados SQL: Utilizado para leitura de dados de agendamentos.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado, utilizando boas práticas de programação como separação de responsabilidades e uso de padrões de projeto. A documentação e os logs são claros, facilitando a manutenção e entendimento do fluxo de processamento. No entanto, a segurança dos dados sensíveis, como senhas, poderia ser melhor tratada.

### 13. Observações Relevantes
- As senhas e informações sensíveis estão expostas nos arquivos de configuração, o que pode representar um risco de segurança.
- O sistema utiliza uma estratégia de retomada de execução de jobs que pode ser aprimorada para lidar com diferentes tipos de erros de forma mais robusta.