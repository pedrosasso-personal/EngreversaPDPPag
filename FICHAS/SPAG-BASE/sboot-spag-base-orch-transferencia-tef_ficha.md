## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um serviço stateless de transferência TEF, desenvolvido para realizar operações de débito e crédito em contas, além de notificar pagamentos e tratar ocorrências. Ele utiliza o framework Spring Boot e integrações com RabbitMQ e IBM MQ para comunicação assíncrona e processamento de mensagens.

### 2. Principais Classes e Responsabilidades
- **MQAdapter**: Converte objetos em mensagens JSON para serem enviadas via MQ.
- **IbmMqConfig**: Configura o IBM MQ para o sistema, incluindo listeners e feature toggles.
- **AtualizarSituacaoSpagEndpoints**: Define propriedades de configuração para endpoints de atualização de situação SPAG.
- **DebitarCreditarContaEndpoints**: Define propriedades de configuração para endpoints de débito e crédito de conta.
- **IntegrarPagamentoEndpoints**: Define propriedades de configuração para endpoints de integração de pagamento.
- **TransferenciaTefController**: Controlador REST para processar pagamentos de transferência TEF.
- **TransferenciaTefListener**: Listener para processar mensagens recebidas via IBM MQ.
- **TransferenciaTefService**: Serviço que utiliza Camel para processar transferências TEF.
- **CircuitBreakProcessor**: Processador Camel que verifica e aplica circuit break em transações.
- **EstornoProcessor**: Processador Camel que trata estornos de transações.
- **NotificarPagamentoSPAGRepositoryImpl**: Implementação de repositório para notificar pagamentos via RabbitMQ.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- RabbitMQ
- IBM MQ
- Apache Camel
- Swagger
- Prometheus
- Grafana
- Maven

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST   | /v1/transferencia-tef | TransferenciaTefController | Processa pagamentos de transferência TEF |

### 5. Principais Regras de Negócio
- Circuit Break: Implementação de circuit break para rejeitar pagamentos em determinadas condições.
- Estorno de Pagamentos: Estorno de pagamentos em caso de falhas ou inconsistências.
- Notificação de Pagamentos: Envio de notificações de pagamento para diferentes sistemas.

### 6. Relação entre Entidades
- **DicionarioPagamento**: Entidade principal que representa os dados de pagamento.
- **SituacaoPagamento**: Representa a situação de um pagamento, incluindo protocolo e status.
- **Ocorrencia**: Representa ocorrências ou erros associados a transações.

### 7. Estruturas de Banco de Dados Lidas
Não se aplica.

### 8. Estruturas de Banco de Dados Atualizadas
Não se aplica.

### 9. Filas Lidas
- **QL.SPAG.SOLICITAR_PAGAMENTO_CC_REQ.INT**: Fila IBM MQ para receber solicitações de pagamento.

### 10. Filas Geradas
- **events.business.notificationService**: Fila RabbitMQ para enviar notificações de pagamento.

### 11. Integrações Externas
- APIs de serviços Atom para validação, integração, débito/crédito e notificação de pagamentos.
- IBM MQ para recebimento de mensagens de pagamento.
- RabbitMQ para envio de notificações de pagamento.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de programação, como injeção de dependências e uso de padrões de projeto. A documentação e configuração são claras, facilitando a manutenção. No entanto, a complexidade de algumas classes pode ser reduzida para melhorar a legibilidade.

### 13. Observações Relevantes
- O sistema utiliza feature toggles para gerenciar configurações dinâmicas.
- A integração com RabbitMQ e IBM MQ permite alta disponibilidade e escalabilidade para o processamento de mensagens.
- A configuração do Prometheus e Grafana permite monitoramento e métricas customizadas do sistema.