## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é uma aplicação batch desenvolvida em Java utilizando o framework Spring Batch. Seu objetivo é realizar a integração contábil, processando lançamentos financeiros entre diferentes sistemas e bancos de dados. A aplicação lê, processa e escreve dados relacionados a lançamentos contábeis, utilizando diversas configurações e serviços para garantir a integridade e eficiência das operações.

### 2. Principais Classes e Responsabilidades
- **Application**: Classe principal que inicia a aplicação Spring Boot.
- **BatchConfiguration**: Configura o job de processamento batch, definindo o step inicial.
- **BatchSkipListener**: Implementa o listener para tratamento de erros durante leitura, processamento e escrita de itens.
- **StepConfiguration**: Configura o step do batch, definindo leitor, processador e escritor de itens.
- **DataSourceConfig**: Configura as fontes de dados utilizadas na aplicação.
- **DefaultBatchConfigurerConfig**: Configura o batch para utilizar uma fonte de dados específica.
- **IntegracaoContabilConfiguration**: Configura beans necessários para a integração contábil, como RestTemplate e serviços.
- **JdbiConfiguration**: Configura o Jdbi para acesso ao banco de dados.
- **TaskConfig**: Configura o task para utilizar uma fonte de dados específica.
- **CaixaEntradaSPBDTO**: DTO para representar dados de entrada de caixa.
- **ChaveSequencialDTO**: DTO para representar chave sequencial.
- **ClienteConta**: Representa informações de conta de cliente.
- **FavorecidoRemetenteConta**: Representa informações de conta de favorecido/remetente.
- **LancamentoPgftDTO**: DTO para representar lançamentos no PGFT.
- **LancamentoSpagDTO**: DTO para representar lançamentos no SPAG.
- **Helper**: Classe utilitária com métodos para manipulação de strings e valores numéricos.
- **JdbiSpagRepositoryImpl**: Implementação do repositório para operações no banco SPAG.
- **JdbiSpbRepositoryImpl**: Implementação do repositório para operações no banco SPB.
- **IntegracaoContabilItemProcessor**: Processador de itens para integração contábil.
- **IntegracaoContabilItemReader**: Leitor de itens para integração contábil.
- **IntegracaoContabilItemWriter**: Escritor de itens para integração contábil.
- **CaixaEntradaSPBDTOMapper**: Mapeador para converter entre DTOs de lançamento SPAG e caixa de entrada SPB.
- **ClienteContaRowMapper**: Mapeador de linhas para ClienteConta.
- **LancamentoPgftDTOMapper**: Mapeador para converter entre DTOs de lançamento SPAG e PGFT.
- **SpagRepository**: Interface para operações no banco SPAG.
- **SpbRepository**: Interface para operações no banco SPB.
- **IntegracaoContabilService**: Serviço principal que coordena a lógica de integração contábil.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Batch
- Spring Boot
- Jdbi
- Sybase JDBC
- Microsoft SQL Server JDBC
- Logback
- Lombok

### 4. Principais Endpoints REST
Não se aplica.

### 5. Principais Regras de Negócio
- Processamento de lançamentos contábeis entre sistemas SPAG e PGFT.
- Atualização de protocolos e códigos de lançamento.
- Tratamento de devoluções para boletos, tributos e concessionárias.
- Validação e preenchimento de informações de cliente e conta.

### 6. Relação entre Entidades
- **LancamentoSpagDTO** e **LancamentoPgftDTO**: Representam lançamentos contábeis em diferentes sistemas.
- **CaixaEntradaSPBDTO**: Representa dados de entrada de caixa, mapeados a partir de lançamentos SPAG.
- **ClienteConta**: Relaciona informações de cliente com contas bancárias.
- **FavorecidoRemetenteConta**: Relaciona informações de favorecido e remetente com contas bancárias.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbLancamento                | tabela | SELECT | Lê lançamentos confirmados no SPAG. |
| TbDeParaLegado              | tabela | SELECT | Lê mapeamentos de clientes e contas. |
| TBL_CAIXA_ENTRADA_SPB       | tabela | SELECT | Lê protocolos de lançamentos no SPB. |
| TBL_LANCAMENTO              | tabela | SELECT | Lê lançamentos no PGFT. |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbLancamento                | tabela | UPDATE | Atualiza protocolos e códigos de lançamento no SPAG. |
| TBL_CAIXA_ENTRADA_SPB       | tabela | INSERT | Insere dados de entrada de caixa no SPB. |
| TBL_LANCAMENTO              | tabela | INSERT | Insere lançamentos no PGFT. |
| TBL_LANCAMENTO              | tabela | UPDATE | Atualiza devoluções de lançamentos no PGFT. |

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- APIs de autenticação e autorização via OAuth2.
- Banco de dados SQL Server e Sybase para operações de leitura e escrita.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado, utilizando boas práticas de programação como injeção de dependências e uso de DTOs para transferência de dados. A utilização de mapeadores e serviços facilita a manutenção e extensão do sistema. No entanto, a complexidade das operações de banco de dados e a ausência de documentação detalhada podem dificultar o entendimento inicial.

### 13. Observações Relevantes
- O sistema utiliza configurações específicas para diferentes ambientes (local, des, qa, uat, prd), o que permite flexibilidade na implantação.
- A aplicação é configurada para rodar em ambientes Kubernetes, utilizando configurações de deploy específicas.
- A utilização de Jdbi para acesso ao banco de dados permite uma abordagem mais flexível e modular para operações SQL.