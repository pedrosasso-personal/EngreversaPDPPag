```markdown
## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um serviço atômico de pagamento de boletos, que permite a convivência entre os sistemas SPAG e SITP para o registro de pagamentos de boletos do tipo Normal ou STR26. Ele expõe APIs REST para registrar pagamentos e buscar informações sobre o sistema de origem.

### 2. Principais Classes e Responsabilidades
- **Application**: Classe principal que inicia a aplicação Spring Boot.
- **OpenApiConfiguration**: Configurações do Swagger para documentação da API.
- **PagamentoBoletoConfiguration**: Configuração do Jdbi e dos serviços de pagamento de boleto.
- **SistemaOrigemRowMapper**: Mapeia o resultado de consultas SQL para objetos `SistemaOrigem`.
- **PagamentoBoletoRepositoryImpl**: Implementação do repositório para operações de pagamento de boleto.
- **PagamentoBoletoExceptionHandler**: Tratamento de exceções específicas do domínio de pagamento de boleto.
- **RegistroPagamentoBoletoMapper**: Mapeamento entre representações de pagamento de boleto e objetos de domínio.
- **SistemaOrigemMapper**: Mapeamento entre representações de sistema de origem e objetos de domínio.
- **PagamentoBoletoController**: Controlador REST para registrar pagamentos de boletos.
- **SistemaOrigemController**: Controlador REST para buscar informações sobre o sistema de origem.
- **Protocolo**: Classe de domínio que representa um protocolo de pagamento.
- **RegistroPagamentoBoleto**: Classe de domínio que representa um registro de pagamento de boleto.
- **RegistroPagamentoBoletoSTR26**: Classe de domínio específica para registros do tipo STR26.
- **SistemaOrigem**: Classe de domínio que representa o sistema de origem.
- **TipoPessoaEnum**: Enumeração para tipos de pessoa (Física ou Jurídica).
- **PagamentoBoletoException**: Exceção de domínio para erros gerais de pagamento de boleto.
- **PagamentoBoletoNegocioException**: Exceção de domínio para erros de negócio específicos.
- **PagamentoBoletoService**: Serviço de domínio para operações de pagamento de boleto.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- Jdbi
- Sybase
- MapStruct
- Swagger
- Prometheus
- Grafana
- Docker

### 4. Principais Endpoints REST
| Método | Endpoint                     | Classe Controladora         | Descrição                                                                 |
|--------|------------------------------|-----------------------------|---------------------------------------------------------------------------|
| GET    | /v1/sistema-origem           | SistemaOrigemController     | Busca informações sobre o sistema de origem.                             |
| POST   | /v1/registra-pagamento-boleto| PagamentoBoletoController   | Registra um pagamento de boleto do tipo Normal ou STR26 no sistema SITP. |

### 5. Principais Regras de Negócio
- O código de lançamento é obrigatório para registrar um pagamento de boleto.
- O tipo de liquidação deve ser NORMAL ou STR_26.
- Verificação se o lançamento já foi registrado antes de realizar um novo registro.
- Determinação do tipo de lançamento Fintech baseado em atributos específicos.

### 6. Relação entre Entidades
- **Protocolo**: Relacionado a `RegistroPagamentoBoleto` e `RegistroPagamentoBoletoSTR26` como resultado de um registro.
- **RegistroPagamentoBoleto**: Contém informações detalhadas sobre o pagamento de boleto.
- **RegistroPagamentoBoletoSTR26**: Variante de `RegistroPagamentoBoleto` para o tipo STR26.
- **SistemaOrigem**: Representa o sistema de origem associado a um pagamento.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo      | Operação | Breve Descrição                                      |
|-----------------------------|-----------|----------|------------------------------------------------------|
| TBL_CAIXA_ENTRADA_SPB       | tabela    | SELECT   | Busca protocolo de pagamento de boleto.              |
| TBL_SIST_ORIGEM_SPB         | tabela    | SELECT   | Busca informações do sistema de origem.              |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo      | Operação          | Breve Descrição                                      |
|-----------------------------|-----------|-------------------|------------------------------------------------------|
| TBL_CAIXA_ENTRADA_SPB       | tabela    | INSERT            | Registra um novo pagamento de boleto.                |

### 9. Filas Lidas
não se aplica

### 10. Filas Geradas
não se aplica

### 11. Integrações Externas
- Integração com sistema SITP para registro de pagamentos de boletos.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código está bem estruturado, com uso adequado de padrões de projeto e boas práticas de desenvolvimento. A documentação é clara e os testes cobrem as principais funcionalidades. No entanto, poderia haver uma maior cobertura de testes e otimização de algumas partes do código.

### 13. Observações Relevantes
- O sistema utiliza o Swagger para documentação da API, facilitando o entendimento e uso dos endpoints.
- A configuração de monitoramento com Prometheus e Grafana está bem estabelecida, permitindo a observação de métricas importantes do sistema.
- O uso de Docker facilita a implantação e execução do sistema em diferentes ambientes.
```