## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema "DebAutorizador" é um serviço atômico desenvolvido para autorizar transações de débito. Ele utiliza o framework Spring Boot e é estruturado como um microserviço. O sistema processa e valida transações de débito, interagindo com um banco de dados SQL Server para realizar operações de inserção e atualização de dados relacionados a transações financeiras.

### 2. Principais Classes e Responsabilidades
- **Application**: Classe principal que inicia a aplicação Spring Boot.
- **AutorizacaoDebtController**: Controlador REST que gerencia endpoints para validação e processamento de transações de débito.
- **ProcessarServiceImpl**: Implementação do serviço que processa transações de débito, incluindo inserções e atualizações no banco de dados.
- **ValidarServiceImpl**: Implementação do serviço que valida transações de débito, calculando o IOF quando necessário.
- **CCBDRepositoryImpl**: Implementação do repositório que interage com o banco de dados para realizar operações CRUD relacionadas a transações.
- **TransacaoMapper**: Classe utilitária para mapear representações de transações para objetos de domínio.
- **ResourceExceptionHandler**: Classe que trata exceções específicas relacionadas a transações.

### 3. Tecnologias Utilizadas
- Spring Boot
- Jdbi
- Swagger
- Maven
- Java 11
- SQL Server
- Lombok

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST   | /v1/autorizar-transacao/validar | AutorizacaoDebtController | Valida uma transação de débito. |
| POST   | /v1/autorizar-transacao/processar | AutorizacaoDebtController | Processa uma transação de débito. |
| POST   | /v1/autorizar-transacao/processarInsert | AutorizacaoDebtController | Insere uma nova transação de débito. |
| PUT    | /v1/autorizar-transacao/processarUpdate | AutorizacaoDebtController | Atualiza uma transação de débito existente. |
| POST   | /v1/autorizar-transacao/processarInsertQuina | AutorizacaoDebtController | Insere dados relacionados à Quina. |

### 5. Principais Regras de Negócio
- Validação de transações para verificar se já foram processadas.
- Cálculo do IOF para transações internacionais.
- Inserção e atualização de dados de transações no banco de dados.
- Tratamento de exceções específicas para transações já processadas ou erros de inserção.

### 6. Relação entre Entidades
- **Transacao**: Entidade principal que representa uma transação de débito, incluindo detalhes como valor, moeda, e status.
- **Cartao**: Entidade que representa informações do cartão associado à transação.
- **Estabelecimento**: Entidade que representa informações do estabelecimento comercial onde a transação ocorreu.
- **Quina**: Entidade que representa dados específicos relacionados à Quina.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbControleTransacaoCartao   | tabela | SELECT | Verifica existência de transações processadas. |
| TbTipoTransacao             | tabela | SELECT | Obtém o tipo de transação. |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbControleTransacaoCartao   | tabela | INSERT/UPDATE | Insere ou atualiza dados de controle de transações. |
| TbEstabelecimentoComercial  | tabela | INSERT | Insere dados de estabelecimento comercial. |
| TbTransacaoCartao           | tabela | INSERT/UPDATE | Insere ou atualiza dados de transações de cartão. |
| TbCheckListTransacaoArquivo | tabela | INSERT | Insere dados de checklist de transações. |

### 9. Filas Lidas
não se aplica

### 10. Filas Geradas
não se aplica

### 11. Integrações Externas
- Integração com SQL Server para operações de banco de dados.
- Utilização de Swagger para documentação de APIs.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de desenvolvimento, como injeção de dependências e tratamento de exceções. A documentação via Swagger é um ponto positivo. No entanto, poderia haver mais comentários explicativos em algumas partes complexas do código.

### 13. Observações Relevantes
- O projeto utiliza o padrão de microserviços atômicos, o que facilita a escalabilidade e manutenção.
- A configuração do banco de dados é gerenciada via arquivos YAML, permitindo flexibilidade em diferentes ambientes.
- O sistema possui testes unitários e de integração para garantir a qualidade das funcionalidades implementadas.