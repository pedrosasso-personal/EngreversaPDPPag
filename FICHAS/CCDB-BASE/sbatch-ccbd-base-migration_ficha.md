## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um serviço Spring Batch responsável por migrar registros da base histórica do DBCONTACORRENTE para o Spanner. O controle da job é feito através do tipo de migração: 'Movimento'. Ele realiza a leitura da tabela TbMovimentoHistorico e publica na fila business-ccbd-base-migration.

### 2. Principais Classes e Responsabilidades
- **MovementByAccountReader**: Lê movimentos de conta a partir do repositório de movimentos.
- **MovementByAccountWriter**: Escreve movimentos de conta no PubSub e registra contas migradas.
- **ReaderPort**: Interface para leitura de itens.
- **WriterPort**: Interface para escrita de itens.
- **MigrationAccount**: Representa uma conta a ser migrada.
- **Movement**: Representa um movimento financeiro.
- **MigrationTypeEnum**: Enumeração para tipos de migração.
- **BatchProperties**: Propriedades de configuração do batch.
- **PubSubProperties**: Propriedades de configuração do PubSub.
- **BatchConfig**: Configuração do batch, incluindo mapeamento de objetos e criação de publishers.
- **DataSourceConfig**: Configuração de fontes de dados e transações.
- **DefaultBatchConfig**: Configuração padrão do batch.
- **JdbiConfig**: Configuração do Jdbi para acesso a dados.
- **MigrationTypeDecider**: Decisor de tipo de migração.
- **ValidateAccountFlow**: Fluxo de validação de contas.
- **JobConfig**: Configuração de jobs do batch.
- **ParamsJobScope**: Escopo de parâmetros de job.
- **JobLogListener**: Listener para log de execução de jobs.
- **StepLogListener**: Listener para log de execução de passos.
- **AccountPartitioner**: Particionador de contas para migração.
- **AccountRepository**: Repositório para operações de conta.
- **MigrationRepository**: Repositório para operações de migração.
- **MovementRepository**: Repositório para operações de movimento.
- **ProcessMovementsByAccountStep**: Passo para processar movimentos por conta.
- **PublishMovementsStep**: Passo para publicar movimentos por conta.
- **ValidateAccountInfoStep**: Passo para validar informações de conta.
- **ValidateAccountMigratedStep**: Passo para validar se a conta já foi migrada.
- **ValidateInitialParamsStep**: Passo para validar parâmetros iniciais.
- **Constants**: Classe de constantes utilizadas no sistema.
- **HashUtil**: Utilitário para geração de hash de contas.
- **Application**: Classe principal para inicialização do Spring Boot.
- **JobRunner**: Executa a job com parâmetros fornecidos.

### 3. Tecnologias Utilizadas
- Java 21
- Spring Batch
- Maven
- Google Cloud PubSub
- Sybase
- JDBI

### 4. Principais Endpoints REST
Não se aplica.

### 5. Principais Regras de Negócio
- Migração de registros de movimentos financeiros de contas.
- Validação de contas antes da migração.
- Publicação de movimentos no PubSub.
- Registro de contas migradas.

### 6. Relação entre Entidades
- **MigrationAccount** e **Movement** são entidades principais.
- **MigrationAccount** possui atributos como banco, número de conta, tipo de conta, etc.
- **Movement** possui atributos como valor da operação, saldo anterior, saldo após lançamento, etc.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbConta                     | tabela | SELECT   | Contém informações de contas correntes. |
| TbMigracaoContaCorrente     | tabela | SELECT   | Contém informações de contas migradas. |
| tbHistoricoMovimento        | tabela | SELECT   | Contém histórico de movimentos financeiros. |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbMigracaoContaCorrente     | tabela | INSERT  | Registra contas que foram migradas. |

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
- **business-ccbd-base-migration**: Fila no Google Cloud PubSub onde os movimentos são publicados.

### 11. Integrações Externas
- Google Cloud PubSub para publicação de mensagens de movimentos.
- Sybase para acesso a dados de contas e movimentos.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado, utiliza boas práticas de programação e organização de pacotes. A utilização de Spring Batch e JDBI é adequada para o propósito do sistema. No entanto, poderia haver mais documentação interna para facilitar o entendimento de partes específicas do código.

### 13. Observações Relevantes
- O sistema utiliza Docker para containerização, conforme indicado no Dockerfile.
- A configuração de segurança inclui OAuth2 com JWT para autenticação.
- O projeto é configurado para rodar em diferentes ambientes (des, uat, prd) com variáveis específicas para cada um.