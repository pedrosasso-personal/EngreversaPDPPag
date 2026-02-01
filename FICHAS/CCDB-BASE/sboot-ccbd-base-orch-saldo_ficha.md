```markdown
## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um serviço de saldo bancário que fornece funcionalidades para consultar saldos de contas, limites de contas e saldos negativos. Ele integra-se com serviços externos para obter dados cadastrais de clientes e informações de saldo.

### 2. Principais Classes e Responsabilidades
- **Application**: Classe principal que inicia a aplicação Spring Boot.
- **SaldoController**: Controlador REST que expõe endpoints para operações de saldo.
- **SaldoService**: Serviço que utiliza Camel para orquestrar chamadas a diferentes repositórios de dados.
- **SaldoRouter**: Define rotas Camel para operações de saldo.
- **ClienteDadosCadastraisRepositoryImpl**: Implementação do repositório para obter dados cadastrais de clientes.
- **ConsultaSaldoRepositoryImpl**: Implementação do repositório para consultar saldos de contas.
- **SaldoRepositoryImpl**: Implementação do repositório para operações de saldo, incluindo saldo negativo e limites de conta.
- **AccountBalanceMapper, AccountLimitsMapper, SaldoNegativoMapper**: Mappers para conversão entre entidades de domínio e representações de API.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- Apache Camel
- Swagger
- Prometheus
- Grafana
- Docker

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET    | /v1/saldo-bancario | SaldoController | Consulta saldo bancário. |
| POST   | /v1/consultarSaldoContaCorrente | SaldoController | Consulta saldo de conta corrente. |
| POST   | /v1/consultarContasPorGrupoComercialSaldo | SaldoController | Consulta contas por grupo comercial. |
| GET    | /v1/saldo-bancario/negativo | SaldoController | Consulta saldo negativo. |
| GET    | /v1/digital-bank/{bank}/balances | SaldoController | Consulta saldo por banco. |
| GET    | /v1/digital-bank/{bank}/limits | SaldoController | Consulta limites de conta por banco. |

### 5. Principais Regras de Negócio
- Validação de CPF/CNPJ para operações de consulta de saldo.
- Integração com serviços externos para obtenção de dados cadastrais e saldos.
- Tratamento de exceções específicas para erros de consulta de saldo e dados cadastrais.

### 6. Relação entre Entidades
- **ClienteSaldo**: Representa informações de saldo de um cliente.
- **AccountBalance**: Representa o saldo de uma conta bancária.
- **AccountLimits**: Representa limites de crédito de uma conta.
- **SaldoNegativo**: Representa informações de saldo negativo de uma conta.

### 7. Estruturas de Banco de Dados Lidas
Não se aplica.

### 8. Estruturas de Banco de Dados Atualizadas
Não se aplica.

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- Serviço de dados cadastrais de clientes.
- Serviço de consulta de saldo bancário.
- Serviço de consulta de saldo negativo.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado, utiliza boas práticas de programação e integrações com serviços externos de forma clara. A utilização de Apache Camel para orquestração de chamadas é bem implementada. Poderia melhorar em termos de documentação interna e testes mais abrangentes.

### 13. Observações Relevantes
- O sistema utiliza Swagger para documentação de APIs, facilitando a integração e testes.
- A configuração do sistema é gerida por arquivos YAML, permitindo fácil adaptação para diferentes ambientes.
- O uso de Prometheus e Grafana para monitoramento de métricas é um ponto positivo para a observabilidade do sistema.

--- 
```