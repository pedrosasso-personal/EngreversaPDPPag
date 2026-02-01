## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um serviço atômico responsável por sintetizar transações efetivadas para geração de movimentação contábil. Ele registra movimentações para contas normais e contas espelhos.

### 2. Principais Classes e Responsabilidades
- **Application**: Classe principal para inicialização do Spring Boot.
- **BCODataBaseConfiguration**: Configuração do banco de dados BCO utilizando Jdbi.
- **CCBDDataBaseConfiguration**: Configuração do banco de dados CCBD com suporte a JPA.
- **MovimentoContabilService**: Serviço responsável pelo processamento de movimentações contábeis.
- **ListenerTransacaoContaCorrente**: Listener para processamento de mensagens de transações efetivadas.
- **MovimentoContabilMapper**: Mapper para conversão entre entidades de transação e movimentação contábil.
- **LoteContabilCacheService**: Serviço para criação e recuperação de códigos de lote contábil.
- **PubSubService**: Serviço para gerenciamento de assinaturas de mensagens via Pub/Sub.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- JPA/Hibernate
- Jdbi
- Maven
- Docker
- Lombok
- Sybase JDBC
- MySQL JDBC
- Caffeine Cache
- Spring Security
- Atlante PubSub

### 4. Principais Endpoints REST
Não se aplica.

### 5. Principais Regras de Negócio
- Processamento de transações efetivadas para geração de movimentações contábeis.
- Criação de lotes contábeis e atualização de detalhes de lote.
- Tratamento de exceções específicas para duplicidade de lote e erros de banco de dados.

### 6. Relação entre Entidades
- **MovimentoContabil**: Entidade principal representando uma movimentação contábil.
- **LoteMovimentoContabil**: Representa um lote de movimentações contábeis.
- **DetalheLoteMovimentoContabil**: Detalhes de um lote de movimentações.
- **TransacaoEfetivada**: Representa uma transação efetivada que gera movimentações contábeis.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbDetalheLoteMovimentoContabil | tabela | SELECT | Detalhes de lote de movimentações contábeis |
| TbLoteMovimentoContabil | tabela | SELECT | Lote de movimentações contábeis |
| TbParametroMovimentoContabil | tabela | SELECT | Parâmetros de movimentação contábil |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbDetalheLoteMovimentoContabil | tabela | UPDATE, INSERT | Atualização e criação de detalhes de lote de movimentações |
| TbLoteMovimentoContabil | tabela | INSERT | Criação de lote de movimentações contábeis |

### 9. Filas Lidas
- GCP Pub/Sub: Subscription para mensagens de transações efetivadas.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- Integração com GCP Pub/Sub para consumo de mensagens de transações.
- Banco de dados Sybase e MySQL para persistência de dados contábeis.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado, utilizando boas práticas de programação como injeção de dependências, uso de mapeamento de entidades e tratamento de exceções. A documentação está presente e o uso de testes unitários é evidente. No entanto, a complexidade de algumas classes pode ser reduzida para melhorar a legibilidade.

### 13. Observações Relevantes
- O sistema utiliza o Spring Boot para facilitar a configuração e execução do serviço.
- A configuração de segurança é feita através do Spring Security com OAuth2.
- O uso de Docker é indicado para facilitar o deploy e execução em ambientes controlados.