## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um serviço Spring Batch desenvolvido para gerar relatórios mensais de IRRF. Ele realiza a leitura de dados de contas bancárias, processa essas informações e as grava em arquivos CSV. Além disso, transfere os arquivos gerados para um servidor de arquivos.

### 2. Principais Classes e Responsabilidades
- **Application**: Classe principal que inicia o aplicativo Spring Boot.
- **ValidaExecucaoDecider**: Decider que determina o fluxo de execução do job com base no status de saída do step.
- **JobConfig**: Configuração do job que define os steps e o fluxo de execução.
- **ConsultaSaldoListener**: Listener que registra logs antes e depois da execução de um step.
- **ContaSaldoProcessor**: Processador que transforma objetos `ContaSaldo` em `ContaSaldoCSV`.
- **JdbiContaSaldoReader**: Leitor que consulta dados de contas bancárias de um repositório.
- **TransfereArquivoLocalParaFileServerTasklet**: Tasklet que transfere arquivos locais para um servidor de arquivos.
- **VerificaDataTasklet**: Tasklet que verifica e configura parâmetros de data para execução do job.
- **FileCsvWriter**: Writer que escreve dados em arquivos CSV.
- **DbContaCorrenteDataSourceConfig**: Configuração do datasource para conexão com o banco de dados de contas correntes.
- **DefaultBatchConfig**: Configuração padrão do batch que define o datasource.
- **JdbiConfig**: Configuração do Jdbi para interação com o banco de dados.
- **ContaSaldoMapper**: Mapper que converte objetos `ContaSaldo` para `ContaSaldoCSV`.
- **ContaSaldoRepositoryImpl**: Implementação do repositório que realiza consultas SQL para obter dados de contas.
- **FileServerServiceImpl**: Serviço que interage com o servidor de arquivos usando CIFS.

### 3. Tecnologias Utilizadas
- Spring Batch
- Spring Boot
- JDBI
- Sybase
- JCIFS
- Maven

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET    | /actuator/health | Não se aplica | Verifica o estado da aplicação |
| GET    | /swagger-ui/index.html | Não se aplica | Exibe a documentação das APIs |

### 5. Principais Regras de Negócio
- Processamento de contas bancárias para geração de relatórios mensais de IRRF.
- Transferência de arquivos CSV gerados para um servidor de arquivos.
- Verificação de parâmetros de data para execução automática ou manual do job.

### 6. Relação entre Entidades
- **ContaSaldo**: Representa os dados de saldo de uma conta bancária.
- **ContaSaldoCSV**: Representa os dados de saldo de uma conta bancária formatados para CSV.
- **InfoTransferenciaArquivo**: Contém informações sobre a transferência de arquivos.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbConta | tabela | SELECT | Contém informações sobre contas bancárias |
| TbSituacaoCadastral | tabela | SELECT | Contém informações sobre a situação cadastral das contas |
| TbModalidadeConta | tabela | SELECT | Contém informações sobre modalidades de contas |
| TbHistoricoSaldo | tabela | SELECT | Contém informações sobre o histórico de saldo das contas |

### 8. Estruturas de Banco de Dados Atualizadas
Não se aplica

### 9. Filas Lidas
Não se aplica

### 10. Filas Geradas
Não se aplica

### 11. Integrações Externas
- Servidor de arquivos via CIFS para transferência de arquivos CSV.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código está bem estruturado, com uso adequado de padrões do Spring Batch e boas práticas de programação. A documentação e os logs são claros, facilitando a manutenção. No entanto, poderia haver uma melhor separação de responsabilidades em algumas classes.

### 13. Observações Relevantes
- O sistema utiliza o banco de dados Sybase para leitura de dados de contas bancárias.
- A configuração do sistema é feita através de arquivos YAML, permitindo fácil adaptação para diferentes ambientes (local, des, uat, prd).
- A aplicação é containerizada usando Docker, facilitando a implantação em diferentes plataformas.