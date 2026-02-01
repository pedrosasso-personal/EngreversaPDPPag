## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um microserviço atômico responsável por validar as informações de conta no ITP (Interbank Payment). Ele utiliza o framework Spring Boot para gerenciar suas operações e está configurado para rodar em um ambiente de container Docker. O serviço expõe endpoints REST para validação de dados de transação e utiliza Prometheus e Grafana para monitoramento de métricas.

### 2. Principais Classes e Responsabilidades
- **Application**: Classe principal que inicia a aplicação Spring Boot.
- **DatabaseConfiguration**: Configura o Jdbi para interações com o banco de dados.
- **OpenApiConfiguration**: Configura o Swagger para documentação de APIs.
- **ValidarConfiguration**: Configura os beans de serviço e repositório.
- **ValidarController**: Controlador REST que gerencia as requisições de validação.
- **ValidarService**: Serviço que contém a lógica de validação de dados.
- **ValidarRepositoryImpl**: Implementação do repositório que interage com o banco de dados.
- **ValidacaoMapper**: Mapeia representações de requisição para objetos de domínio.
- **ValidacaoRowMapper**: Mapeia resultados de SQL para objetos de domínio.
- **DadosValidacao**: Classe de domínio que representa os dados de validação.
- **Validacao**: Classe de domínio que representa o resultado da validação.
- **TransacaoInvalidaException**: Exceção lançada quando a validação falha.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- Jdbi
- Swagger
- Sybase
- Docker
- Prometheus
- Grafana

### 4. Principais Endpoints REST
| Método | Endpoint                          | Classe Controladora | Descrição                                      |
|--------|-----------------------------------|---------------------|-----------------------------------------------|
| POST   | /v1/banco-digital/validar         | ValidarController   | Valida as informações de conta no ITP.        |

### 5. Principais Regras de Negócio
- Validação de dados de transações bancárias.
- Lançamento de exceção em caso de dados inválidos.
- Mapeamento de dados de requisição para objetos de domínio.

### 6. Relação entre Entidades
- **DadosValidacao**: Contém informações de transação como código de filial, origem, transação e liquidação.
- **Validacao**: Resultado da validação, incluindo tipo de lançamento e indicadores de crédito e débito.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo    | Operação | Breve Descrição                                      |
|-----------------------------|---------|----------|------------------------------------------------------|
| TBL_TRANSACAO_SPB           | tabela  | SELECT   | Armazena transações do SPB.                          |
| TBL_DESCRICAO_TRANSACAO_SPB | tabela  | SELECT   | Descrição das transações do SPB.                     |
| TBL_TRANSACAO_CCON          | tabela  | SELECT   | Transações de conta corrente.                        |

### 8. Estruturas de Banco de Dados Atualizadas
Não se aplica.

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- OAuth2 para autenticação via JSON Web Token.
- Sybase como banco de dados.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código está bem estruturado, utilizando boas práticas de programação como injeção de dependências e separação de responsabilidades. A documentação via Swagger é um ponto positivo, assim como o uso de exceções específicas para tratamento de erros. No entanto, poderia haver mais comentários explicativos para facilitar o entendimento de partes complexas.

### 13. Observações Relevantes
- O sistema utiliza o Prometheus e Grafana para monitoramento de métricas, o que é uma boa prática para observabilidade.
- A configuração do Dockerfile é simples e eficiente, permitindo fácil implantação do serviço.
- A documentação do Swagger facilita a integração e uso dos endpoints expostos.