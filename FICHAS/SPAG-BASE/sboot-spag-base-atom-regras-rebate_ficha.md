## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um serviço atômico desenvolvido em Java utilizando o framework Spring Boot, responsável por gerenciar regras e parametrizações de rebate. Ele interage com um banco de dados para realizar operações de CRUD sobre entidades relacionadas a clientes, contas de apuração, faixas de parametrização e serviços.

### 2. Principais Classes e Responsabilidades
- **Application**: Classe principal que inicia a aplicação Spring Boot.
- **JdbiConfiguration**: Configura o JDBI para interações com o banco de dados.
- **OpenApiConfiguration**: Configura o Swagger para documentação de APIs.
- **RegrasRebateConfiguration**: Configura os serviços de parametrização de cliente e produto.
- **RestResponseEntityExceptionHandler**: Manipula exceções de resposta REST.
- **ClienteRepository**: Interface para operações de banco de dados relacionadas a clientes.
- **ContaApuracaoRepository**: Interface para operações de banco de dados relacionadas a contas de apuração.
- **FaixaParametrizacaoClienteRepository**: Interface para operações de banco de dados relacionadas a faixas de parametrização de cliente.
- **FaixaParametrizacaoProdutoRepository**: Interface para operações de banco de dados relacionadas a faixas de parametrização de produto.
- **ServicoRepository**: Interface para operações de banco de dados relacionadas a serviços.
- **ParametrizacaoClienteService**: Serviço para gerenciar parametrizações de cliente.
- **ParametrizacaoProdutoService**: Serviço para gerenciar parametrizações de produto.
- **ServicoService**: Serviço para gerenciar serviços de rebate.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- JDBI
- Swagger
- SQL Server
- Docker

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | /parametrizacao/faixas/cliente/{id} | FaixaParametrizacaoClienteController | Busca faixa de parametrização de cliente por ID. |
| GET | /historico/faixas/cliente/{id} | HistoricoFaixaParametrizacaoClienteController | Busca histórico de faixa de parametrização de cliente por ID e data. |
| GET | /historico/parametrizacao/cliente/{idParametrizacao} | HistoricoParametrizacaoClienteController | Busca histórico de parametrização de cliente por ID. |
| GET | /historico/parametrizacao/produto/{idParametrizacao} | HistoricoParametrizacaoProdutoController | Lista histórico de parametrização de produto por ID. |
| GET | /parametrizacao/cliente/periodicidade/{periodicidade} | ParametrizacaoClienteController | Busca parametrização de cliente por periodicidade. |
| POST | /parametrizacao/cliente | ParametrizacaoClienteController | Cadastra nova parametrização de cliente. |
| PATCH | /parametrizacao/cliente/{id} | ParametrizacaoClienteController | Altera parametrização de cliente. |
| DELETE | /parametrizacao/cliente/{id} | ParametrizacaoClienteController | Exclui parametrização de cliente. |
| GET | /parametrizacao/produto/{id} | ParametrizacaoProdutoController | Busca parametrização de produto por ID. |
| POST | /parametrizacao/produto | ParametrizacaoProdutoController | Cadastra nova parametrização de produto. |
| PUT | /parametrizacao/produto/{id} | ParametrizacaoProdutoController | Altera parametrização de produto. |
| DELETE | /parametrizacao/produto/{id} | ParametrizacaoProdutoController | Exclui parametrização de produto. |
| GET | /produtos | ServicoController | Lista todos os serviços. |
| POST | /produtos | ServicoController | Cadastra novo serviço. |

### 5. Principais Regras de Negócio
- Cadastro e alteração de parametrizações de cliente e produto.
- Validação de existência de parametrizações antes de exclusão.
- Histórico de alterações de parametrizações.
- Gerenciamento de serviços de rebate.

### 6. Relação entre Entidades
- **Cliente**: Relacionado a parametrizações de cliente.
- **ContaApuracao**: Relacionada a parametrizações de cliente.
- **FaixaParametrizacaoCliente**: Relacionada a parametrizações de cliente.
- **FaixaParametrizacaoProduto**: Relacionada a parametrizações de produto.
- **Servico**: Relacionado a parametrizações de cliente e produto.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbClienteRebate | tabela | SELECT | Armazena informações de clientes. |
| TbContaApuracaoCliente | tabela | SELECT | Armazena informações de contas de apuração. |
| TbParametroFaixaCliente | tabela | SELECT | Armazena informações de faixas de parametrização de cliente. |
| TbParametroFaixaServico | tabela | SELECT | Armazena informações de faixas de parametrização de produto. |
| TbParametroCliente | tabela | SELECT | Armazena informações de parametrizações de cliente. |
| TbParametroServico | tabela | SELECT | Armazena informações de parametrizações de produto. |
| TbServicoRebate | tabela | SELECT | Armazena informações de serviços de rebate. |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbClienteRebate | tabela | INSERT | Insere informações de clientes. |
| TbContaApuracaoCliente | tabela | INSERT/UPDATE/DELETE | Gerencia informações de contas de apuração. |
| TbParametroFaixaCliente | tabela | INSERT/UPDATE/DELETE | Gerencia informações de faixas de parametrização de cliente. |
| TbParametroFaixaServico | tabela | INSERT/UPDATE/DELETE | Gerencia informações de faixas de parametrização de produto. |
| TbParametroCliente | tabela | INSERT/UPDATE/DELETE | Gerencia informações de parametrizações de cliente. |
| TbParametroServico | tabela | INSERT/UPDATE/DELETE | Gerencia informações de parametrizações de produto. |
| TbServicoRebate | tabela | INSERT/UPDATE/DELETE | Gerencia informações de serviços de rebate. |

### 9. Filas Lidas
não se aplica

### 10. Filas Geradas
não se aplica

### 11. Integrações Externas
- Swagger para documentação de APIs.
- Prometheus e Grafana para monitoramento e métricas.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de desenvolvimento, como injeção de dependências e separação de responsabilidades. A documentação está presente e o uso de testes unitários é evidente. Poderia melhorar em termos de comentários explicativos e simplificação de algumas lógicas.

### 13. Observações Relevantes
- O projeto utiliza Docker para containerização e possui configurações para diferentes ambientes.
- A aplicação está configurada para utilizar o Spring Actuator para monitoramento de saúde.