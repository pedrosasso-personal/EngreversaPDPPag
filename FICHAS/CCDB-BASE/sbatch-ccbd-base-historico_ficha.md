## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema "sbatch-ccbd-base-historico" é um projeto Spring Batch responsável pela migração histórica diária das tabelas do processo de virada de data. Ele realiza operações de leitura e escrita em diversas tabelas relacionadas a contas correntes, consolidando dados históricos de avisos de lançamento, limites de conta corrente, movimentações, saldos bloqueados e saldos indisponíveis.

### 2. Principais Classes e Responsabilidades
- **SpringBatchApplication**: Classe principal que inicia a aplicação Spring Batch.
- **DbContaCorrenteDataSourceConfig**: Configuração do datasource para conexão com o banco de dados Sybase.
- **JdbiConfig**: Configuração do Jdbi para interação com o banco de dados.
- **TaskConfig**: Configuração padrão de tarefas do Spring Cloud Task.
- **BatchConfiguration**: Configuração do job batch, definindo o fluxo de execução.
- **Constants**: Classe utilitária que define constantes usadas no sistema.
- **AppProperties**: Classe que mapeia propriedades de configuração da aplicação.
- **DefaultBatchConfig**: Configuração padrão do batch, definindo o datasource.
- **AvisoLancamentoStepConfig**: Configuração do step para processamento de avisos de lançamento.
- **HistoricoLimiteContaCorrenteStepConfig**: Configuração do step para processamento de limites de conta corrente.
- **HistoricoMovimentacaoContaStepConfig**: Configuração do step para processamento de movimentações de conta.
- **HistoricoSaldoBloqueadoConfig**: Configuração do step para processamento de saldos bloqueados.
- **HistoricoSaldoIndisponivelStepConfig**: Configuração do step para processamento de saldos indisponíveis.
- **SaveHoraExecucaoStepConfig**: Configuração do step para salvar a hora de execução do job.
- **AvisoLancamentoConta**: Entidade que representa um aviso de lançamento de conta.
- **LimiteContaCorrente**: Entidade que representa um limite de conta corrente.
- **MovimentoContaRange**: Entidade que representa um intervalo de movimentações de conta.
- **SaldoBloqueadoConta**: Entidade que representa um saldo bloqueado de conta.
- **SaldoIndisponivelConta**: Entidade que representa um saldo indisponível de conta.
- **DateUtils, JobUtils, StepUtils**: Classes utilitárias para manipulação de datas e contexto de execução.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Batch
- Spring Boot
- Jdbi
- Sybase JDBC
- Maven

### 4. Principais Endpoints REST
Não se aplica.

### 5. Principais Regras de Negócio
- Migração diária de dados históricos de contas correntes.
- Processamento de avisos de lançamento, limites de conta corrente, movimentações, saldos bloqueados e saldos indisponíveis.
- Execução de jobs de forma tolerante a falhas, com possibilidade de reprocessamento em caso de erros.

### 6. Relação entre Entidades
- **AvisoLancamentoConta**: Relaciona-se com a tabela `TbAvisoLancamento`.
- **LimiteContaCorrente**: Relaciona-se com as tabelas `TbLimiteContaCorrente` e `TbHistoricoLimiteContaCorrente`.
- **MovimentoContaRange**: Relaciona-se com as tabelas `TbMovimentoDia` e `TbHistoricoMovimento`.
- **SaldoBloqueadoConta**: Relaciona-se com as tabelas `TbSaldoBloqueado` e `TbHistoricoSaldoBloqueado`.
- **SaldoIndisponivelConta**: Relaciona-se com as tabelas `TbSaldoIndisponivel` e `TbHistoricoSaldoIndisponivel`.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo (tabela/view/coleção) | Operação (SELECT/READ) | Breve Descrição |
|-----------------------------|----------------------------|------------------------|-----------------|
| TbAvisoLancamento           | tabela                     | SELECT                 | Lê avisos de lançamento anteriores à data de execução do job. |
| TbLimiteContaCorrente       | tabela                     | SELECT                 | Lê limites de conta corrente com fim de vigência anterior à data de execução do job. |
| TbMovimentoDia              | tabela                     | SELECT                 | Lê movimentações do dia agrupadas por conta. |
| TbSaldoIndisponivel         | tabela                     | SELECT                 | Lê saldos indisponíveis com fim de vigência anterior à data de execução do job. |
| TbSaldoBloqueado            | tabela                     | SELECT                 | Lê saldos bloqueados com motivo de desbloqueio ou fim de vigência anterior à data de execução do job. |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo (tabela/view/coleção) | Operação (INSERT/UPDATE/DELETE) | Breve Descrição |
|-----------------------------|----------------------------|-------------------------------|-----------------|
| TbHistoricoLimiteContaCorrente | tabela                  | INSERT                        | Insere histórico de limites de conta corrente. |
| TbLimiteContaCorrente       | tabela                     | DELETE                        | Remove limites de conta corrente com fim de vigência anterior à data de execução do job. |
| TbHistoricoMovimento        | tabela                     | INSERT                        | Insere histórico de movimentações de conta. |
| TbMovimentoDia              | tabela                     | DELETE                        | Remove movimentações do dia após inserção no histórico. |
| TbHistoricoSaldoBloqueado   | tabela                     | INSERT                        | Insere histórico de saldos bloqueados. |
| TbSaldoBloqueado            | tabela                     | DELETE                        | Remove saldos bloqueados após inserção no histórico. |
| TbHistoricoSaldoIndisponivel | tabela                    | INSERT                        | Insere histórico de saldos indisponíveis. |
| TbSaldoIndisponivel         | tabela                     | DELETE                        | Remove saldos indisponíveis após inserção no histórico. |
| TbAvisoLancamento           | tabela                     | DELETE                        | Remove avisos de lançamento após inserção no histórico. |

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- Banco de dados Sybase para leitura e escrita de dados.
- Configuração de segurança via URL JWT para diferentes ambientes.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código está bem estruturado e organizado, seguindo boas práticas de programação. As classes estão divididas de forma lógica e o uso de Spring Batch é apropriado para o tipo de processamento realizado. No entanto, poderia haver uma documentação mais detalhada sobre o fluxo de dados e as regras de negócio específicas.

### 13. Observações Relevantes
- O projeto utiliza o framework Spring Batch para processamento de dados em massa, o que é adequado para o tipo de tarefa realizada.
- A configuração de datasource e Jdbi permite uma integração eficiente com o banco de dados Sybase.
- O sistema possui testes unitários abrangentes para garantir a qualidade e a correção do processamento de dados.