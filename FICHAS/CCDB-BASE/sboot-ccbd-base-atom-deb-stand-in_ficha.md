## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema "Serviço Atômico de DebStandIn" é um microserviço desenvolvido para realizar a autorização de transações de débito em um ambiente de Stand-In. Ele utiliza o framework Spring Boot e integra-se com diversas tecnologias para gerenciar transações financeiras, incluindo verificação de saldo e inserção de transações em cache. O serviço expõe endpoints REST para autorização de transações e consome mensagens de filas JMS.

### 2. Principais Classes e Responsabilidades
- **Application**: Classe principal que inicia o aplicativo Spring Boot.
- **DebtAuthorizationController**: Controlador responsável por gerenciar a autorização de transações de débito.
- **CacheTransactionService**: Serviço que gerencia a inserção de transações em cache.
- **DebStandInService**: Serviço que realiza operações de transações de débito, incluindo validações e inserções no banco de dados.
- **CacheTransactionRepositoryImpl**: Implementação do repositório para operações de cache de transações.
- **CCBDRepositoryImpl**: Implementação do repositório para operações de transações de débito no banco de dados.
- **CacheTransaction**: Classe de domínio que representa uma transação em cache.
- **DebtTransaction**: Classe de domínio que representa uma transação de débito.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- JDBI
- Swagger
- Microsoft SQL Server
- JMS (IBM MQ)
- Maven

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST   | /v1/transacao-debito/autorizar-transacao | DebtAuthorizationController | Autoriza uma transação de débito. |

### 5. Principais Regras de Negócio
- Verificação de saldo disponível antes de autorizar a transação.
- Inserção de transações em cache após autorização.
- Cálculo de IOF para transações internacionais.
- Validação de transações já existentes para evitar duplicidade.

### 6. Relação entre Entidades
- **DebtTransaction**: Relaciona-se com **CacheTransaction** para operações de cache.
- **Cartao** e **Estabelecimento** são partes da **Transacao**, representando detalhes do cartão e do estabelecimento comercial.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbConta | tabela | SELECT | Verifica o saldo disponível. |
| TbAutorizacaoStandIn | tabela | SELECT | Verifica se a transação já existe e obtém sequência de Stand-In. |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbAutorizacaoStandIn | tabela | INSERT | Insere nova transação de débito Stand-In. |

### 9. Filas Lidas
- Não se aplica

### 10. Filas Geradas
- QL.CCBD_PROC_TRANSAC_STAND_IN.INT: Fila JMS para onde as transações são enviadas após autorização.

### 11. Integrações Externas
- API Gateway para autenticação OAuth e operações de cache.
- Banco de dados Microsoft SQL Server para operações de transações.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código está bem estruturado e segue boas práticas de desenvolvimento, como uso de injeção de dependência e separação de responsabilidades. A documentação é clara e o uso de testes unitários é abrangente. No entanto, poderia haver melhorias na clareza dos logs e na gestão de exceções.

### 13. Observações Relevantes
- O projeto utiliza Swagger para documentação de APIs, facilitando a integração e testes.
- A configuração do sistema é gerida através de arquivos YAML, permitindo fácil adaptação a diferentes ambientes (desenvolvimento, produção, etc.).
- O uso de Docker é empregado para facilitar a implantação e execução do serviço em ambientes padronizados.