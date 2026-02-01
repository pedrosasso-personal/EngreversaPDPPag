```markdown
## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um serviço atômico desenvolvido em Java utilizando o Spring Boot. Ele é responsável por gerenciar notificações contábeis, realizando operações de inserção e validação de eventos contábeis em um banco de dados MySQL. O serviço também consome mensagens de um sistema de mensageria Pub/Sub do Google Cloud Platform.

### 2. Principais Classes e Responsabilidades
- **Application**: Classe principal que inicia a aplicação Spring Boot.
- **PubSubProperties**: Configurações das assinaturas do Pub/Sub.
- **JdbiConfiguration**: Configuração do Jdbi para interação com o banco de dados.
- **PubsubConfiguration**: Configuração do consumidor de mensagens do Pub/Sub.
- **AccountEntry, BillingEntry, NotificationEntry, OriginEntry, PayerEntry, PaymentEntry, PurposeEntry, ReverseEntry, ReverseOriginalEntry, SPBEntry, StatusEntry**: Classes de domínio representando entidades contábeis.
- **NotificacaoContabilException**: Exceção personalizada para erros de notificação contábil.
- **NotificacaoContabilListener**: Listener para consumir mensagens do Pub/Sub e processar notificações contábeis.
- **NotificacaoContabilRepository**: Interface de repositório para operações no banco de dados.
- **NotificacaoContabilService**: Serviço que encapsula a lógica de negócio para inserção e validação de eventos contábeis.
- **ConstantUtil, JsonUtil, LoggerHelper, NotificationHelper, SqlLoggerImpl**: Utilitários para diversas operações como manipulação de JSON, logging e validação de notificações.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- Maven
- MySQL
- Jdbi
- Google Cloud Pub/Sub
- Swagger

### 4. Principais Endpoints REST
| Método | Endpoint  | Classe Controladora | Descrição |
|--------|-----------|---------------------|-----------|
| GET    | /contabil | Não se aplica       | Endpoint para teste de operação contábil |

### 5. Principais Regras de Negócio
- Validação de lançamento contábil já inserido para evitar duplicidade.
- Inserção de eventos contábeis somente se a transação for efetivada com sucesso e não for uma devolução.
- Ajuste de credor e devedor para bancos zerados quando o método de liquidação é STN.

### 6. Relação entre Entidades
- **NotificationEntry** possui relações com várias outras entidades como BillingEntry, StatusEntry, ReverseEntry, etc., representando um evento contábil completo.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbLancamentoContabil        | tabela | SELECT | Validação de existência de lançamento contábil |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbLancamentoContabil        | tabela | INSERT | Inserção de novos eventos contábeis |

### 9. Filas Lidas
- Google Cloud Pub/Sub: business-spag-base-contabil-notification-service-sub

### 10. Filas Geradas
Não se aplica

### 11. Integrações Externas
- Google Cloud Pub/Sub: para consumo de mensagens de notificações contábeis.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado, utilizando boas práticas de programação como injeção de dependências e uso de padrões de projeto. A documentação e os testes unitários são adequados, mas poderia haver mais comentários explicativos em algumas partes complexas do código.

### 13. Observações Relevantes
- O sistema utiliza variáveis de ambiente para configuração de perfis e credenciais, facilitando a adaptação a diferentes ambientes de execução.
- A configuração de segurança JWT está integrada para proteger os endpoints expostos.
```