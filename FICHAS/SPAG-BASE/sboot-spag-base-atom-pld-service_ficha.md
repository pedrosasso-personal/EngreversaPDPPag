## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema "Serviço Atômico de PLD" é um microserviço desenvolvido para gerenciar dados de cadastro e transações de parceiros do Banco Votorantim. Ele utiliza o framework Spring Boot para criar endpoints REST que permitem o registro e consulta de dados de transações e cadastros, integrando-se com o banco de dados SQL Server para armazenamento e recuperação de informações.

### 2. Principais Classes e Responsabilidades
- **DateUtil**: Utilitário para conversão de strings de data em objetos `OffsetDateTime`.
- **HibernateConfiguration**: Configuração do Hibernate para gerenciar entidades JPA.
- **OpenApiConfiguration**: Configuração do Swagger para documentação das APIs.
- **PldServiceConfiguration**: Configuração geral do serviço, incluindo o `ObjectMapper`.
- **FlagPepEnumConverter, TipoRendaEnumConverter, TipoTransacaoEnumConverter**: Converters para mapeamento de enums para strings no banco de dados.
- **DadosCadastroEntity, DadosTransacaoEntity**: Entidades JPA que representam os dados de cadastro e transação.
- **DadosCadastroRepository, DadosTransacaoRepository**: Repositórios JPA para acesso às entidades de cadastro e transação.
- **DadosCadastroTransactional, DadosTransacaoTransactional**: Implementações de portas transacionais para operações de cadastro e transação.
- **DadosCadastroMapper, DadosTransacaoMapper**: Mappers para conversão entre entidades e objetos de domínio.
- **ExceptionHandler**: Manipulador de exceções para o serviço.
- **PldServiceController**: Controlador REST que expõe os endpoints do serviço.
- **Application**: Classe principal para inicialização do Spring Boot.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- Hibernate
- Swagger/OpenAPI
- SQL Server
- Lombok
- MapStruct

### 4. Principais Endpoints REST
| Método | Endpoint                        | Classe Controladora       | Descrição                                           |
|--------|---------------------------------|---------------------------|-----------------------------------------------------|
| POST   | /v1/transactional               | PldServiceController      | Registra um novo dado de transação para parceiro.   |
| GET    | /v1/transactional               | PldServiceController      | Obtém dados de transação para um parceiro.          |
| POST   | /v1/registration                | PldServiceController      | Registra um novo dado de cadastro para parceiro.    |
| GET    | /v1/registration                | PldServiceController      | Obtém dados de cadastro para um parceiro.           |
| GET    | /v1/registration/{document}     | PldServiceController      | Obtém dados de cadastro por documento.              |

### 5. Principais Regras de Negócio
- Validação de dados de cadastro e transação antes da inserção no banco.
- Conversão de enums para strings para persistência no banco de dados.
- Auditoria de dados com preenchimento automático de informações de inclusão e alteração.
- Manipulação de exceções específicas do domínio com retorno de status HTTP apropriado.

### 6. Relação entre Entidades
- **DadosCadastroEntity** e **DadosTransacaoEntity** são entidades JPA que representam tabelas no banco de dados.
- **DadosCadastroEntity** possui relacionamento com enums `TipoRendaEnum` e `FlagPepEnum`.
- **DadosTransacaoEntity** possui relacionamento com enum `TipoTransacaoEnum`.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo     | Operação | Breve Descrição                           |
|-----------------------------|----------|----------|-------------------------------------------|
| TbDadoCadastroPLD           | tabela   | SELECT   | Tabela que armazena dados de cadastro.    |
| TbDadoTransacaoPLD          | tabela   | SELECT   | Tabela que armazena dados de transação.   |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo     | Operação | Breve Descrição                           |
|-----------------------------|----------|----------|-------------------------------------------|
| TbDadoCadastroPLD           | tabela   | INSERT   | Tabela que armazena dados de cadastro.    |
| TbDadoTransacaoPLD          | tabela   | INSERT   | Tabela que armazena dados de transação.   |

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- Integração com SQL Server para persistência de dados.
- Utilização de Swagger para documentação de APIs.
- Autenticação via OAuth2.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de desenvolvimento, como o uso de mappers para conversão de objetos e configuração centralizada. A documentação das APIs com Swagger é um ponto positivo. No entanto, poderia haver mais comentários explicativos em algumas partes do código para melhorar a legibilidade e manutenção.

### 13. Observações Relevantes
- O projeto utiliza o padrão de microserviços atômicos, o que facilita a escalabilidade e manutenção.
- A configuração do Swagger permite fácil acesso e teste dos endpoints expostos.
- O uso de Lombok reduz a quantidade de código boilerplate, melhorando a legibilidade.