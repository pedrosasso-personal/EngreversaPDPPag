## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema "javabatch-ccbd-base-debito-auto-notificacao" é um projeto Java que utiliza o framework Maven para gerenciar notificações automáticas de débitos. Ele processa lançamentos de débitos automáticos, lê dados de um banco de dados e envia notificações através de filas RabbitMQ.

### 2. Principais Classes e Responsabilidades
- **ItemProcessor**: Processa cada item de lançamento, atualmente apenas logando o processamento.
- **ItemReader**: Lê lançamentos do banco de dados, utilizando o `NotificacaoRepository` para recuperar dados.
- **ItemWriter**: Escreve os lançamentos em filas RabbitMQ, enviando notificações.
- **MyResumeStrategy**: Define a estratégia de retomada de execução de jobs.
- **ExitCodeEnum**: Enumeração de códigos de saída para o sistema.
- **ProdutoEnum**: Enumeração de tipos de produtos.
- **NotificacaoException**: Exceção personalizada para erros de notificação.
- **NotificacaoMapper**: Mapeia resultados de consultas SQL para objetos `Lancamento`.
- **NotificacaoRepository**: Interface para recuperação de lançamentos.
- **NotificacaoRepositoryImpl**: Implementação da interface `NotificacaoRepository`, utilizando JDBC para consultas.
- **NotificacaoUtil**: Utilitário para manipulação de datas e leitura de SQL de arquivos.
- **Dados**: Classe de valor que representa dados de um lançamento.
- **Lancamento**: Classe de valor que representa um lançamento de débito automático.

### 3. Tecnologias Utilizadas
- Java
- Maven
- Spring Framework
- RabbitMQ
- MySQL
- Log4j
- Jackson

### 4. Principais Endpoints REST
Não se aplica.

### 5. Principais Regras de Negócio
- Recuperação de lançamentos de débitos automáticos com base na data de vencimento.
- Envio de notificações para diferentes filas dependendo do tipo de produto.
- Tratamento de exceções específicas para falhas na recuperação de dados ou envio de mensagens.

### 6. Relação entre Entidades
- **Lancamento** possui um relacionamento com **Dados**.
- **ProdutoEnum** é utilizado para definir o tipo de produto em **Lancamento**.

### 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo (tabela/view/coleção) | Operação (SELECT/READ) | Breve Descrição |
|-----------------------------|----------------------------|------------------------|-----------------|
| TbPagamentoDebitoAutomatico | tabela                     | SELECT                 | Armazena informações de pagamentos de débitos automáticos. |
| TbPessoaDebitoAutomatico    | tabela                     | SELECT                 | Armazena informações de pessoas associadas aos débitos automáticos. |
| TbConvenioDebitoAutomatico  | tabela                     | SELECT                 | Armazena informações de convênios de débitos automáticos. |

### 8. Estruturas de Banco de Dados Atualizadas
Não se aplica.

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
- **ex.ccbd.debito.automatico**: Fila para notificações de vencimento de débitos automáticos.
- **ex.ccbd.notificacao.vencimentoDebitoAutomatico**: Fila para notificações de vencimento de crédito pessoal.

### 11. Integrações Externas
- RabbitMQ: Utilizado para envio de mensagens de notificação.
- MySQL: Banco de dados utilizado para armazenar e recuperar informações de lançamentos.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado, utilizando boas práticas de programação como separação de responsabilidades e uso de padrões de projeto. A utilização de enums para códigos de saída e tipos de produtos é adequada. No entanto, poderia haver mais documentação e tratamento de exceções para melhorar a robustez.

### 13. Observações Relevantes
- O sistema utiliza criptografia para gerenciar senhas de acesso ao banco de dados.
- A configuração do sistema é dividida em diferentes ambientes (DES, PRD, UAT), cada um com suas próprias configurações de banco de dados e filas.