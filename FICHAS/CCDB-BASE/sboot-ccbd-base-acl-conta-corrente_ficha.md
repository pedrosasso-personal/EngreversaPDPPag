```markdown
## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um serviço de orquestração para descomissionamento do NCCS, disponibilizando funcionalidades de consulta de titularidade de conta, tipo de transações, agências e outras configurações. Ele é desenvolvido em Java com Spring Boot e utiliza uma arquitetura hexagonal.

### 2. Principais Classes e Responsabilidades
- **Application**: Classe principal que inicia a aplicação Spring Boot.
- **GlobalExceptionHandler**: Trata exceções globais no contexto de controladores REST.
- **HttpClientErrorExceptionHandler**: Manipula exceções de erro de cliente HTTP.
- **AccountClosureRequestRepresentationMapper**: Mapeia representações de requisições de encerramento de conta.
- **AccountHolderRepresentationMapper**: Mapeia representações de titulares de conta.
- **AccountHoldersResponseMapper**: Mapeia respostas de titulares de conta.
- **AccountIdRepresentationMapper**: Mapeia representações de identificadores de conta.
- **AccountRepresentationMapper**: Mapeia representações de contas.
- **BranchDetailResponseMapper**: Mapeia respostas de detalhes de agência.
- **HolderRepresentationMapper**: Mapeia representações de titulares.
- **PaginationRepresentationMapper**: Mapeia representações de paginação.
- **PersonRepresentationMapper**: Mapeia representações de pessoas.
- **TransactionApiDelegateImplMapper**: Mapeia implementações de delegados de API de transações.
- **TransactionResponseMapper**: Mapeia respostas de transações.
- **AccountBranchApiDelegateImpl**: Implementação de delegados de API para detalhes de agência.
- **AccountHoldersApiDelegateImpl**: Implementação de delegados de API para titulares de conta.
- **TransactionApiDelegateImpl**: Implementação de delegados de API para tipos de transações.
- **RequestDateControlMapper**: Mapeia controles de data de requisição.
- **ResponseControlDateMappper**: Mapeia respostas de controle de data.
- **ResponseTransactionTypeMapper**: Mapeia tipos de transações de resposta.
- **SearchDateControl**: Serviço para buscar controle de data.
- **SearchTransactionTypeWithFilter**: Serviço para buscar tipos de transações com filtro.
- **SearchTransactionTypeWithId**: Serviço para buscar tipos de transações por ID.
- **AccountClosureRequestMapper**: Mapeia requisições de encerramento de conta.
- **AccountHolderMapper**: Mapeia titulares de conta.
- **AccountIdMapper**: Mapeia identificadores de conta.
- **AccountMapper**: Mapeia contas.
- **BasicRecordInformationMapper**: Mapeia informações básicas de registros.
- **HolderMapper**: Mapeia titulares.
- **PaginationMapper**: Mapeia paginação.
- **GetAccountById**: Serviço para obter conta por ID.
- **GetAccountByModalityList**: Serviço para obter contas por lista de modalidades.
- **GetAccountIdByPerson**: Serviço para obter ID de conta por pessoa.
- **GetHolderByAccountId**: Serviço para obter titular por ID de conta.
- **GetPersonIdByTaxIdNumber**: Serviço para obter ID de pessoa por número de CPF/CNPJ.
- **SearchBranchDomainMapper**: Mapeia domínios de agências.
- **SearchBranchDomain**: Serviço para buscar domínios de agências.
- **BranchDetailMapper**: Mapeia detalhes de agência.
- **Validator**: Interface para validação.
- **Get**: Interface para execução de operações de obtenção.
- **AccountIdValidator**: Validador de identificadores de conta.
- **AccountNumberValidator**: Validador de números de conta.
- **BankIdValidator**: Validador de IDs de banco.
- **TaxIdNumberValidator**: Validador de números de CPF/CNPJ.
- **GetAccountHolders**: Caso de uso para obter titulares de conta.
- **GetAccountHoldersByAccount**: Caso de uso para obter titulares de conta por conta.
- **GetAccountHoldersByModality**: Caso de uso para obter titulares de conta por modalidade.
- **GetAccountHoldersByTaxIdNumber**: Caso de uso para obter titulares de conta por CPF/CNPJ.
- **SearchBranchDetail**: Caso de uso para buscar detalhes de agência.
- **SearchTransactionType**: Caso de uso para buscar tipos de transações.
- **AccountOwnershipType**: Enum para tipos de propriedade de conta.
- **HolderType**: Enum para tipos de titular.
- **OperationType**: Enum para tipos de operação.
- **ErrorCode**: Interface para códigos de erro.
- **InvalidParameterException**: Exceção para parâmetros inválidos.
- **NotFoundException**: Exceção para recursos não encontrados.
- **Account**: Modelo de conta.
- **AccountClosureRequest**: Modelo de requisição de encerramento de conta.
- **AccountHolder**: Modelo de titular de conta.
- **AccountHolderRequest**: Modelo de requisição de titular de conta.
- **AccountId**: Modelo de identificador de conta.
- **BasicRecordInformation**: Interface para informações básicas de registros.
- **FilterCheck**: Modelo para verificação de filtros.
- **Holder**: Modelo de titular.
- **ListAccountHolderPaginated**: Modelo de lista paginada de titulares de conta.
- **ListAccountPaginated**: Modelo de lista paginada de contas.
- **Pagination**: Modelo de paginação.
- **Person**: Modelo de pessoa.
- **RequestAccountByBank**: Modelo de requisição de conta por banco.
- **RequestAccountByPerson**: Modelo de requisição de conta por pessoa.
- **RequestAccountModalityByBankPaginated**: Modelo de requisição de modalidade de conta por banco paginada.
- **RequestBranchDetail**: Modelo de requisição de detalhes de agência.
- **RequestDateControl**: Modelo de controle de data de requisição.
- **RequestPersonByBank**: Modelo de requisição de pessoa por banco.
- **RequestTransactionType**: Modelo de requisição de tipo de transação.
- **ResponseBranchDetail**: Modelo de resposta de detalhes de agência.
- **ResponseBranchDomain**: Modelo de resposta de domínio de agência.
- **ResponseControlDate**: Modelo de resposta de controle de data.
- **ResponseTransactionType**: Modelo de resposta de tipo de transação.
- **TransactionCategory**: Modelo de categoria de transação.
- **ApiConfiguration**: Configuração de APIs.
- **BooleanConverter**: Conversor de valores booleanos.
- **DateTimeConverter**: Conversor de valores de data e hora.
- **ApiProperties**: Propriedades de configuração de API.
- **OAuth2ClientConfig**: Configuração de cliente OAuth2.
- **OAuth2ClientHttpRequestInterceptorBv**: Interceptor de requisições HTTP para OAuth2.

### 3. Tecnologias Utilizadas
- Java 21
- Spring Boot
- Maven
- Logback
- OAuth2
- OpenAPI

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | /v1/digital-bank/{bank}/account-holders | AccountHoldersApiDelegateImpl | Obtém todas as contas e titulares por filtro. |
| GET | /v1/digital-bank/{bank}/branchs/{branchNumber} | AccountBranchApiDelegateImpl | Busca detalhes de agência. |
| GET | /v1/digital-bank/{bank}/transaction-types/{id} | TransactionApiDelegateImpl | Busca tipo de transação por ID. |
| GET | /v1/digital-bank/{bank}/transaction-types | TransactionApiDelegateImpl | Busca tipos de transação. |

### 5. Principais Regras de Negócio
- Validação de parâmetros de entrada para operações de busca.
- Mapeamento de entidades de domínio para representações de API.
- Tratamento de exceções globais e específicas de cliente HTTP.
- Integração com serviços externos para obtenção de dados de conta e transação.

### 6. Relação entre Entidades
- **Account** possui um **AccountId** e pode ter um **AccountClosureRequest**.
- **AccountHolder** possui uma **Account** e uma coleção de **Holder**.
- **Holder** possui uma **Person** e um **HolderType**.
- **TransactionCategory** está associada a **ResponseTransactionType**.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo (tabela/view/coleção) | Operação (SELECT/READ) | Breve Descrição |
|-----------------------------|----------------------------|------------------------|-----------------|
| DBGlobal.TbBanco | tabela | SELECT | Tabela de bancos. |
| DBGlobal.TbTipoConta | tabela | SELECT | Tabela de tipos de conta. |
| DBGlobal.TbAgencia | tabela | SELECT | Tabela de agências. |
| DBContaCorrente.TbMotivoEncerramentoConta | tabela | SELECT | Tabela de motivos de encerramento de conta. |
| DBContaCorrente.TbModalidade | tabela | SELECT | Tabela de modalidades de conta. |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo (tabela/view/coleção) | Operação (INSERT/UPDATE/DELETE) | Breve Descrição |
|-----------------------------|----------------------------|-------------------------------|-----------------|
| Não se aplica | | | |

### 9. Filas Lidas
Não se aplica

### 10. Filas Geradas
Não se aplica

### 11. Integrações Externas
- **sboot-glob-base-atom-cliente-dados-cadastrais**: Serviço para dados cadastrais de clientes.
- **sboot-glob-base-atom-lista-bancos**: Serviço para lista de bancos.
- **sboot-ccbd-base-atom-conta-corrente-dominio**: Serviço para operações nas tabelas de domínio do conta-corrente.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e segue boas práticas de desenvolvimento, como a utilização de uma arquitetura hexagonal. A documentação está presente e os mapeamentos são claros. No entanto, poderia haver uma maior cobertura de testes automatizados.

### 13. Observações Relevantes
O sistema utiliza uma arquitetura hexagonal, o que facilita a manutenção e evolução do código. A integração com serviços externos é feita através de clientes REST gerados a partir de especificações OpenAPI.
```