## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um serviço de transferência TED, projetado para ser um microserviço stateless. Ele realiza operações de débito e crédito em contas, integra com o SPB (Sistema de Pagamentos Brasileiros), e notifica pagamentos através de diversas APIs. O serviço utiliza o framework Spring Boot e Apache Camel para orquestrar as rotas de processamento de pagamentos.

### 2. Principais Classes e Responsabilidades
- **IbmMqConfig**: Configurações para integração com IBM MQ, incluindo listeners e feature toggles.
- **RabbitMQConfiguration**: Configurações para integração com RabbitMQ, incluindo conexão e tratamento de erros.
- **TransferenciaTedController**: Controlador REST para processar pagamentos TED e obter retornos do SPB.
- **TransferenciaTedService**: Serviço que utiliza Apache Camel para processar pagamentos e retornos SPB.
- **TransferenciaTedRouter**: Define as rotas de processamento de pagamentos usando Apache Camel.
- **DebitarCreditarContaRepositoryImpl**: Implementação do repositório para operações de débito e crédito em contas.
- **IntegrarSPBRepositoryImpl**: Implementação do repositório para integração com o SPB.
- **NotificarPagamentoSpagRepositoryImpl**: Implementação do repositório para notificação de pagamentos via RabbitMQ.
- **PgftBvSaMensagemDTO**: DTO para mensagens de retorno do SPB.
- **CamelContextWrapper**: Wrapper para o contexto do Apache Camel, gerenciando rotas e templates de produtor/consumidor.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- Apache Camel
- RabbitMQ
- IBM MQ
- Swagger/OpenAPI
- Maven

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST   | /v1/transferencia-ted/pagamento-ted | TransferenciaTedController | Processa um pagamento TED. |
| POST   | /v1/transferencia-ted/retorno-spb | TransferenciaTedController | Obtém o retorno do SPB. |
| POST   | /validarBoleto | Swagger/OpenAPI | Valida um boleto. |

### 5. Principais Regras de Negócio
- Validação de pagamentos antes de realizar débito/crédito.
- Integração com o SPB para confirmação de transações.
- Notificação de pagamentos através de RabbitMQ.
- Tratamento de ocorrências e estornos em caso de falhas.

### 6. Relação entre Entidades
- **DicionarioPagamento**: Entidade central que representa os dados de pagamento.
- **SituacaoPagamento**: Representa a situação de um pagamento, incluindo protocolo e status.
- **Ocorrencia**: Detalha erros ou eventos durante o processamento de pagamentos.

### 7. Estruturas de Banco de Dados Lidas
Não se aplica.

### 8. Estruturas de Banco de Dados Atualizadas
Não se aplica.

### 9. Filas Lidas
- QL.SPAG.SOLICITAR_PAGAMENTO_TED_REQ.INT
- QL.SPAG.RETORNO_PAGAMENTO_TED.INT

### 10. Filas Geradas
- events.business.notificationService (RabbitMQ)

### 11. Integrações Externas
- APIs de serviços de pagamento (SPB, PGFT, SITP, SPAG)
- RabbitMQ para notificação de pagamentos
- IBM MQ para processamento de mensagens TED

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código está bem estruturado e utiliza boas práticas de programação, como injeção de dependências e uso de DTOs para transferência de dados. A integração com Apache Camel e RabbitMQ está bem implementada. No entanto, a documentação poderia ser mais detalhada em algumas partes para facilitar a manutenção.

### 13. Observações Relevantes
- O sistema utiliza feature toggles para ativar/desativar funcionalidades dinamicamente.
- A configuração de segurança utiliza OAuth2 para autenticação em APIs externas.
- O projeto está configurado para ser executado em ambientes de desenvolvimento e produção, com suporte a Docker e Prometheus/Grafana para monitoramento.