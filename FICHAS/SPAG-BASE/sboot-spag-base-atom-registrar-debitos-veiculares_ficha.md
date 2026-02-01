## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema "Registrar Débitos Veiculares" é um serviço atômico desenvolvido para registrar e atualizar débitos veiculares. Ele utiliza o framework Spring Boot e integra-se com bancos de dados SQL Server para operações de consulta e atualização de débitos. O sistema expõe APIs RESTful para inserção, atualização e consulta de débitos veiculares, além de lidar com liquidações e erros de arrecadação.

### 2. Principais Classes e Responsabilidades
- **Application**: Classe principal para inicialização do Spring Boot.
- **RegistrarDebitosVeicularesController**: Controlador que gerencia as requisições HTTP relacionadas aos débitos veiculares.
- **RegistrarDebitosVeicularesService**: Serviço que contém a lógica de negócios para registrar e atualizar débitos veiculares.
- **RegistrarDebitosVeicularesRepository**: Interface de repositório para operações de banco de dados relacionadas aos débitos veiculares.
- **OpenApiConfiguration**: Configuração do Swagger para documentação das APIs.
- **ResourceExceptionHandler**: Manipulador de exceções para erros de validação e internos.
- **ValidaCamposDebitoVeicular**: Classe de validação de campos para débitos veiculares.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- Maven
- JDBI
- SQL Server
- Swagger
- Docker
- Prometheus
- Grafana

### 4. Principais Endpoints REST
| Método | Endpoint                                      | Classe Controladora                       | Descrição                                           |
|--------|-----------------------------------------------|-------------------------------------------|-----------------------------------------------------|
| POST   | /registrar-debitos-veiculares/inserir         | RegistrarDebitosVeicularesController      | Insere um novo débito veicular                      |
| POST   | /registrar-debitos-veiculares/atualizar       | RegistrarDebitosVeicularesController      | Atualiza um débito veicular existente               |
| GET    | /registrar-debitos-veiculares/buscar-ocorrencia-erro-consulta | RegistrarDebitosVeicularesController | Busca erro na consulta de débito veicular           |
| PATCH  | /registrar-debitos-veiculares/atualizar-liquidacao | RegistrarDebitosVeicularesController | Atualiza o status da liquidação de débito veicular  |
| POST   | /registrar-debitos-veiculares/inserir-liquidacao | RegistrarDebitosVeicularesController | Insere liquidação de débito veicular                |
| POST   | /registrar-debitos-veiculares/inserir-liquidacao-lote | RegistrarDebitosVeicularesController | Insere movimentos para lote de pagamento de débitos |
| GET    | /registrar-debitos-veiculares/monta-solicitacao-liquidacao | RegistrarDebitosVeicularesController | Monta solicitação de liquidação                     |

### 5. Principais Regras de Negócio
- Validação de campos obrigatórios para inserção e atualização de débitos veiculares.
- Verificação de códigos de arrecadador e status de lançamento antes de operações de banco de dados.
- Tratamento de erros de consulta e validação com respostas apropriadas.
- Integração com sistemas de liquidação para registrar pagamentos e atualizações.

### 6. Relação entre Entidades
- **RegistrarDebitosVeiculares**: Entidade principal para débitos veiculares.
- **AtualizaLiquidacao**: Entidade para atualização de liquidações.
- **ContaDomain**: Entidade representando informações de conta bancária.
- **VehicleDomain**: Entidade representando informações do veículo.
- **OcorrenciaErroDebitoVeicular**: Entidade para erros de débito veicular.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção         | Tipo       | Operação (SELECT/READ) | Breve Descrição                                      |
|-------------------------------------|------------|------------------------|------------------------------------------------------|
| TbArrecadador                       | tabela     | SELECT                 | Consulta código do arrecadador                       |
| TbMovimentoLotePagamentoTrbto       | tabela     | SELECT                 | Consulta código de lançamento de movimento de lote   |
| TbLancamento                        | tabela     | SELECT                 | Consulta código de lançamento                        |
| TbLiquidacao                        | tabela     | SELECT                 | Consulta código de liquidação                        |
| TbOcorrenciaErroArrecadador         | tabela     | SELECT                 | Consulta código de erro do arrecadador               |
| TbOcorrenciaErroPagamento           | tabela     | SELECT                 | Consulta erro de ocorrência de pagamento             |
| TbConsultaDebitoVeicular            | tabela     | SELECT                 | Consulta código de débito veicular                   |
| TbStatusLancamento                  | tabela     | SELECT                 | Consulta status de lançamento                        |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção         | Tipo       | Operação (INSERT/UPDATE/DELETE) | Breve Descrição                                      |
|-------------------------------------|------------|---------------------------------|------------------------------------------------------|
| TbMovimentoLotePagamentoTrbto       | tabela     | INSERT                         | Insere movimento de liquidação de lote               |
| TbLancamento                        | tabela     | UPDATE                         | Atualiza informações de lançamento                   |
| TbLancamentoDebitoVeicular          | tabela     | UPDATE                         | Atualiza informações de débito veicular              |
| TbConsultaDebitoVeicular            | tabela     | INSERT/UPDATE                  | Insere ou atualiza consulta de débito veicular       |

### 9. Filas Lidas
não se aplica

### 10. Filas Geradas
não se aplica

### 11. Integrações Externas
- Integração com sistemas de liquidação para registrar e atualizar pagamentos.
- Integração com Prometheus e Grafana para monitoramento de métricas.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código está bem estruturado e segue boas práticas de desenvolvimento, como a utilização de injeção de dependência e separação de responsabilidades. A documentação das APIs via Swagger é um ponto positivo. No entanto, poderia haver uma melhor organização dos testes unitários e integração para garantir maior cobertura.

### 13. Observações Relevantes
- O sistema utiliza o framework JDBI para operações de banco de dados, facilitando a integração com SQL Server.
- A configuração do Swagger permite fácil acesso à documentação das APIs expostas.
- O uso de Docker facilita a implantação e execução do sistema em ambientes diversos.