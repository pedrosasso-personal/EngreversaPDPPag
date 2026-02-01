## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um serviço atômico de pagamentos desenvolvido para o Banco Votorantim. Ele é responsável por consultar e processar pagamentos realizados no banco digital, incluindo a listagem de pagamentos, consulta de totais de pagamentos sem boletos do tipo BV e BVF, e operações relacionadas a pagamentos com cartão de crédito. O sistema utiliza o framework Spring Boot e está configurado para rodar em ambientes de desenvolvimento e produção.

### 2. Principais Classes e Responsabilidades
- **Application**: Classe principal que inicia a aplicação Spring Boot.
- **PagamentosController**: Controlador REST que gerencia as requisições relacionadas aos pagamentos.
- **PagamentosService**: Serviço que contém a lógica de negócios para manipulação de pagamentos.
- **PagamentosRepositoryImpl**: Implementação do repositório que interage com o banco de dados para operações de leitura de pagamentos.
- **PagamentosResumidoRowMapper**: Mapeador de linhas SQL para objetos PagamentosResumido.
- **PagamentosRowMapper**: Mapeador de linhas SQL para objetos Pagamentos.
- **TotalPagamentosRowMapper**: Mapeador de linhas SQL para objetos TotalPagamentos.
- **TotalPagamentosSaldoCartaoRowMapper**: Mapeador de linhas SQL para objetos TotalPagamentosSaldoCartao.
- **DatabaseConfiguration**: Configuração do Jdbi para acesso ao banco de dados.
- **OpenApiConfiguration**: Configuração do Swagger para documentação de APIs.
- **PagamentosConfiguration**: Configuração de beans relacionados ao serviço de pagamentos.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- Jdbi
- Swagger
- RabbitMQ
- Docker
- SQL Server

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET    | /v1/pagamentos/consultar | PagamentosController | Lista de pagamentos. |
| GET    | /v1/pagamentos/listar-fechados | PagamentosController | Listar pagamentos fechados. |
| GET    | /v1/pagamentos/resumir-fechados | PagamentosController | Resumir pagamentos fechados. |
| GET    | /v1/pagamentos/total-sem-bv | PagamentosController | Total de pagamentos sem boletos do tipo BV e BVF. |
| GET    | /v1/pagamentos/total-sem-bv/noturno | PagamentosController | Consultar total de pagamentos noturnos sem boletos do tipo BV e BVF. |
| GET    | /v1/pagamentos/total-sem-bv-saldo-cartao | PagamentosController | Total de pagamentos sem boletos do tipo BV e BVF e forma de pagamento cartão e saldo. |
| GET    | /v1/pagamentos/total-sem-bv-saldo-cartao/noturno | PagamentosController | Total de pagamentos noturnos sem boletos do tipo BV e BVF e forma de pagamento cartão e saldo. |
| GET    | /v1/pagamentos-cartao-credito/total-sem-bv | PagamentosController | Total de pagamentos realizados com cartão de crédito sem boletos do tipo BV e BVF. |

### 5. Principais Regras de Negócio
- Validação de datas para operações de consulta de pagamentos.
- Cálculo de totais de pagamentos excluindo boletos do tipo BV e BVF.
- Manipulação de pagamentos com cartão de crédito sem boletos BV.
- Resumo de pagamentos fechados.
- Cálculo de totais de pagamentos noturnos.

### 6. Relação entre Entidades
- **Pagamentos**: Entidade que representa um pagamento, incluindo informações como data de lançamento, valor, e beneficiário.
- **PagamentosResumido**: Entidade que representa um resumo de pagamentos, incluindo o número da conta e valor resumido.
- **TipoPagamento**: Entidade que representa o tipo de pagamento, com código e descrição.
- **TotalPagamentos**: Entidade que representa o total de pagamentos, incluindo o número da conta e quantidade de pagamentos.
- **TotalPagamentosSaldoCartao**: Entidade que representa o total de pagamentos com saldo de cartão.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbLancamentoBoleto          | tabela | SELECT | Armazena lançamentos de boletos. |
| TbDetalheBoleto             | tabela | SELECT | Armazena detalhes de boletos. |
| TbTransacaoBoleto           | tabela | SELECT | Armazena transações de boletos. |

### 8. Estruturas de Banco de Dados Atualizadas
Não se aplica.

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- Integração com RabbitMQ para gerenciamento de mensagens.
- Integração com SQL Server para operações de banco de dados.
- Integração com OAuth2 para autenticação e autorização.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e segue boas práticas de desenvolvimento, como o uso de injeção de dependências e mapeamento de entidades. A documentação via Swagger é um ponto positivo, facilitando a compreensão dos endpoints disponíveis. No entanto, a complexidade de algumas consultas SQL pode ser um ponto de atenção para manutenção futura.

### 13. Observações Relevantes
- O projeto está configurado para diferentes ambientes (desenvolvimento, QA, UAT, produção) através do uso de perfis no `application.yml`.
- O uso de Docker facilita a implantação e execução do serviço em diferentes ambientes.
- A documentação do Swagger fornece uma visão clara dos endpoints disponíveis e suas funcionalidades.