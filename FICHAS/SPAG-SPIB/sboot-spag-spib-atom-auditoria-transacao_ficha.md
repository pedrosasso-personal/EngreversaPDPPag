## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um serviço atômico de auditoria de transações, desenvolvido para registrar e gerenciar informações de auditoria relacionadas a transações financeiras, especialmente no contexto de transações PIX. Utiliza o framework Spring Boot e integra-se com RabbitMQ para mensageria.

### 2. Principais Classes e Responsabilidades
- **Application**: Classe principal que inicia a aplicação Spring Boot.
- **AuditTransactionController**: Controlador responsável por gerenciar endpoints relacionados a transações de auditoria.
- **DictAuditTransactionController**: Controlador para gerenciar endpoints relacionados a transações de auditoria do DICT.
- **AuditTransactionService**: Serviço que encapsula a lógica de negócios para manipulação de transações de auditoria.
- **AuditDictTransactionService**: Serviço que encapsula a lógica de negócios para manipulação de transações de auditoria do DICT.
- **AuditTransaction**: Classe de domínio que representa uma transação de auditoria.
- **AuditDictTransaction**: Classe de domínio que representa uma transação de auditoria do DICT.
- **JdbiAuditTransactionRepository**: Repositório que utiliza JDBI para operações de banco de dados relacionadas a transações de auditoria.
- **JdbiAuditDictTransactionRepository**: Repositório que utiliza JDBI para operações de banco de dados relacionadas a transações de auditoria do DICT.
- **AuditTransactionMapper**: Classe utilitária para conversão entre objetos de domínio e representações.
- **AuditDictTransactionMapper**: Classe utilitária para conversão entre objetos de domínio e representações.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- JDBI
- RabbitMQ
- Swagger
- Docker

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST   | /v1/audit-transaction | AuditTransactionController | Insere uma nova transação de auditoria. |
| PUT    | /v1/audit-transaction | AuditTransactionController | Atualiza uma transação de auditoria existente. |
| GET    | /v1/audit-transaction | AuditTransactionController | Consulta uma transação de auditoria por ID. |
| GET    | /v1/audit-transaction/{message_type}/{end_to_end_identification}/{original_instruction_identification}/{message_flow} | AuditTransactionController | Consulta transações de auditoria por parâmetros específicos. |
| POST   | /dict/audit-transaction | DictAuditTransactionController | Insere uma nova transação de auditoria do DICT. |

### 5. Principais Regras de Negócio
- Validação de campos obrigatórios em transações de auditoria.
- Inserção e atualização de registros de auditoria no banco de dados.
- Conversão de objetos de domínio para representações e vice-versa.

### 6. Relação entre Entidades
- **AuditTransaction** e **AuditDictTransaction** são entidades principais que representam transações de auditoria.
- **DTOAuditDictTransaction** é uma representação de dados transferidos para operações de banco de dados.
- **AuditXml** encapsula informações XML relacionadas a transações de auditoria.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| SPAGAuditoriaBacen.transactional_audit | tabela | SELECT | Armazena registros de auditoria de transações. |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| SPAGAuditoriaBacen.transactional_audit | tabela | INSERT/UPDATE | Armazena registros de auditoria de transações. |
| SPAGAuditoriaBacen.audit_transactional_dict | tabela | INSERT | Armazena registros de auditoria de transações do DICT. |

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- Integração com RabbitMQ para mensageria.
- Integração com SQL Server para operações de banco de dados.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de programação, como injeção de dependências e uso de padrões de projeto. A documentação é clara e os testes estão bem organizados. No entanto, poderia haver uma maior cobertura de testes e otimização em algumas partes do código.

### 13. Observações Relevantes
- O projeto utiliza o Swagger para documentação de APIs.
- A configuração de segurança é realizada via OAuth2.
- O sistema é configurado para diferentes ambientes (des, qa, uat, prd) através de arquivos de configuração.