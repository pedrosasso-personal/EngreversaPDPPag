## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um serviço de devolução de transferências Pix, desenvolvido para orquestrar operações de devolução de valores entre contas bancárias. Ele utiliza o framework Spring Boot e integra-se com diversas APIs e serviços para realizar operações de consulta, validação, geração de identificadores e envio de notificações relacionadas às transações Pix.

### 2. Principais Classes e Responsabilidades
- **AppProperties**: Gerencia as propriedades de configuração do aplicativo.
- **DevolucaoPixConfiguration**: Configurações de beans e serviços relacionados à devolução de Pix.
- **OpenApiConfiguration**: Configuração do Swagger para documentação de APIs.
- **PubSubConfiguration**: Configuração para integração com Google Pub/Sub.
- **RabbitMQConfiguration**: Configuração para integração com RabbitMQ.
- **ExceptionControllerHandler**: Manipula exceções específicas do sistema.
- **ResourceExceptionHandler**: Manipula exceções gerais do sistema.
- **ConsultarOperacaoPixNotificacaoRepositoryImpl**: Implementação de consulta de operações Pix para notificações.
- **EnviarDevolucaoRepositoryImpl**: Implementação para envio de solicitações de devolução Pix.
- **DevolucaoPixController**: Controlador REST para operações de devolução de Pix.
- **DevolucaoPixService**: Serviço para efetuar a devolução de transferências Pix.
- **NotificacaoService**: Serviço para envio de notificações relacionadas a devoluções Pix.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- RabbitMQ
- Kafka
- Apache Camel
- Google Pub/Sub
- Swagger
- Prometheus
- Grafana

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST   | /v1/banco-digital/transferencia-pix/devolver | DevolucaoPixController | Realiza a devolução de uma transferência Pix. |

### 5. Principais Regras de Negócio
- Validação de conta antes de realizar a devolução.
- Geração de token de autorização para operações Pix.
- Geração de identificador único para devoluções Pix.
- Envio de notificações para o banco digital e via Salesforce.
- Reprocessamento de operações em caso de falha.

### 6. Relação entre Entidades
- **DevolucaoPix**: Entidade principal que representa uma devolução de Pix, incluindo informações como valor, data, motivo, remetente e favorecido.
- **ComprovantePix**: Representa o comprovante de uma transação Pix.
- **Agente**: Representa um participante da transação, podendo ser remetente ou favorecido.
- **Conta**: Detalhes da conta bancária associada a um agente.
- **Participante**: Representa um participante do sistema financeiro.
- **TokenAuthorization**: Representa o token de autorização para operações Pix.

### 7. Estruturas de Banco de Dados Lidas
Não se aplica.

### 8. Estruturas de Banco de Dados Atualizadas
Não se aplica.

### 9. Filas Lidas
- RabbitMQ: `ccbd_devolver_pix`
- Google Pub/Sub: `devolucaoPixInputChannel`

### 10. Filas Geradas
- Kafka: `ppbd-pixx-enviar-notificacao-usuario-cmd`

### 11. Integrações Externas
- APIs de geração de token e envio de notificações.
- Serviços de consulta de operações e participantes Pix.
- Google Pub/Sub para mensagens de devolução.
- RabbitMQ para mensagens de notificação.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de programação, como injeção de dependências e uso de padrões de projeto. A documentação e os testes são abrangentes, mas a complexidade de algumas classes pode ser reduzida para melhorar a legibilidade.

### 13. Observações Relevantes
- O sistema utiliza configurações específicas para diferentes ambientes (local, des, qa, uat, prd).
- A integração com sistemas externos é feita principalmente via REST e mensageria.
- O sistema possui suporte para métricas customizadas através do Prometheus e Grafana.