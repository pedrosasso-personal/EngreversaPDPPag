```markdown
## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um microserviço orquestrador que realiza a liquidação de agendamentos de pagamentos. Ele consome mensagens de filas do PubSub, processa essas mensagens e interage com outros serviços para efetuar transferências e atualizar o status de agendamentos. Utiliza o Camel para integração com filas e o WebClient para chamadas HTTP.

### 2. Principais Classes e Responsabilidades
- **Application**: Classe principal que inicia a aplicação Spring Boot.
- **MessageConverter**: Converte mensagens recebidas em objetos de transferência.
- **StatusAgendamentoSgatMapper**: Mapeia notificações de pagamento para objetos de status de agendamento.
- **NotifySchedulingStatusConsumerAdapter**: Consome notificações de status de agendamento do PubSub.
- **SettleSchedulingConsumerAdapter**: Consome agendamentos para liquidação do PubSub.
- **AccountTypeLookupAdapter**: Consulta siglas de tipos de conta.
- **SchedulingStatusProducer**: Produz mensagens de status de agendamento para o Kafka.
- **SettleSchedulingAdapter**: Realiza chamadas HTTP para efetuar agendamentos de transferência.
- **FindAccountTypeUseCase**: Caso de uso para obter tipos de conta.
- **NotifySchedulingStatusUsecase**: Caso de uso para notificar status de agendamento.
- **SettleSchedulingUseCase**: Caso de uso para processar agendamentos de transferência.
- **PayloadDeserializer**: Deserializa payloads de mensagens.
- **InvalidPayload**: Exceção para payloads inválidos.
- **LiquidaAgendamentoStatusException**: Exceção para status de agendamento desconhecidos.
- **RouterProperties**: Propriedades de configuração de roteamento.
- **JacksonConfig**: Configuração do ObjectMapper para serialização/deserialização.
- **WebClientConfig**: Configuração do WebClient para chamadas HTTP.

### 3. Tecnologias Utilizadas
- Spring Boot
- Apache Camel
- Google Cloud PubSub
- Kafka
- WebFlux
- OAuth2
- Jackson
- Maven

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST   | /v1/transferencia | Não se aplica | Transferência entre contas via TED, TEF ou DOC |

### 5. Principais Regras de Negócio
- Conversão de mensagens de agendamento em objetos de transferência.
- Mapeamento de notificações de pagamento para status de agendamento.
- Consulta de siglas de tipos de conta.
- Produção de mensagens de status de agendamento para o Kafka.
- Processamento de agendamentos de transferência.

### 6. Relação entre Entidades
- **ScheduleLiquidation**: Contém informações de agendamento e financeiro.
- **FinancialInfo**: Detalhes financeiros de uma transferência.
- **AccountInformation**: Informações de conta bancária.
- **Payload**: Detalhes adicionais de uma transação.

### 7. Estruturas de Banco de Dados Lidas
Não se aplica.

### 8. Estruturas de Banco de Dados Atualizadas
Não se aplica.

### 9. Filas Lidas
- business-sgat-base-executa-agendamento
- business-spag-base-notification-service

### 10. Filas Geradas
- Kafka tópico de status de agendamento

### 11. Integrações Externas
- Serviço de transferências `sboot-spag-base-orch-transferencias`
- Serviço de consulta de tipos de conta

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de programação, como injeção de dependências e uso de padrões de projeto. A documentação é clara e os componentes são bem separados. No entanto, poderia haver mais comentários explicativos em algumas partes complexas do código.

### 13. Observações Relevantes
- O sistema utiliza o padrão Proxy para desacoplar o Camel do domínio da aplicação.
- A configuração do WebClient é feita para permitir autenticação OAuth2 fora do contexto do ServerWebExchange.
- A aplicação requer Java 11+ e Maven 3.8+ para compilação e execução.
```