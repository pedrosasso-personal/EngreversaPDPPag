## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema "Registra Boleto" é um serviço stateless desenvolvido em Java utilizando o framework Spring Boot. Ele tem como objetivo registrar boletos de pagamento, integrando-se com sistemas externos para validação e processamento dos registros. O sistema utiliza Apache Camel para integração e orquestração de processos, além de Google Cloud Pub/Sub para comunicação assíncrona.

### 2. Principais Classes e Responsabilidades
- **ApiConfiguration**: Configura as APIs externas utilizadas pelo sistema.
- **CacheConfiguration**: Habilita o uso de cache no sistema.
- **OpenApiConfiguration**: Configura o Swagger para documentação das APIs.
- **PubSubInputChannelConfiguration**: Define canais e adaptadores do PubSub para o Spring Integration.
- **PubSubMessagingGatewayConfiguration**: Configura o gateway de mensagens para PubSub.
- **RegistraBoletoConfiguration**: Configurações gerais do sistema, incluindo Camel e serviços.
- **VelocityEngineConfiguration**: Configura o motor de templates Velocity.
- **PagamentoBoletoPgftImpl**: Implementação do cliente para registrar pagamentos de boletos via PGFT.
- **PagamentoBoletoSitpImpl**: Implementação do cliente para registrar pagamentos de boletos via SITP.
- **PagamentoBoletoSpagImpl**: Implementação do cliente para registrar pagamentos de boletos via SPAG.
- **PagamentoSpagImpl**: Implementação do cliente para atualizar a situação de lançamentos de pagamentos.
- **LancamentoTedSpagMapper**: Mapper para conversão de objetos de domínio para representação.
- **EventoPublisherImpl**: Implementação do publisher de eventos para PubSub.
- **TedPublisherImpl**: Implementação do publisher de eventos para TED via MQ.
- **RegistraBoletoSubscriber**: Subscriber para receber comandos de registro de boletos via PubSub.
- **RegistraBoletoService**: Serviço principal para registrar boletos de sucesso, erro de negócio e erro técnico.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- Apache Camel
- Google Cloud Pub/Sub
- Swagger
- Ehcache
- IBM MQ
- MapStruct
- Velocity

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST   | /registra-boleto | RegistraBoletoSubscriber | Registra um boleto. |
| POST   | /registra-lancamento | RegistraBoletoSubscriber | Registra um lançamento de pagamento. |
| GET    | /sistema-origem | PagamentoBoletoSitpImpl | Busca informações sobre o sistema de origem. |
| POST   | /registra-pagamento-boleto | PagamentoBoletoSitpImpl | Registra um pagamento de boleto. |
| PUT    | /atualizarSituacao | PagamentoSpagImpl | Atualiza a situação de um pagamento. |

### 5. Principais Regras de Negócio
- Validação de grade horária para processamento de câmaras de liquidação.
- Registro de boletos com diferentes tipos de liquidação (NORMAL, STR_26).
- Atualização de situação de lançamentos de pagamento com sucesso ou falha.
- Integração com sistemas externos para validação e registro de boletos.

### 6. Relação entre Entidades
- **LancamentoSpag**: Representa um lançamento de pagamento.
- **Protocolo**: Representa um protocolo de registro de pagamento.
- **EventoRegistro**: Representa um evento de registro de pagamento.
- **Erro**: Representa um erro de negócio ou técnico.
- **CamaraLiquidacao**: Representa uma câmara de liquidação com horários de operação.

### 7. Estruturas de Banco de Dados Lidas
Não se aplica.

### 8. Estruturas de Banco de Dados Atualizadas
Não se aplica.

### 9. Filas Lidas
- **registraBoletoInputChannel**: Canal de entrada para comandos de registro de boletos via PubSub.

### 10. Filas Geradas
- **retornoProcessoPagamentoBoletoOutputChannel**: Canal de saída para retorno de processos de pagamento de boletos via PubSub.
- **QL.SPAG.SOLICITAR_PAGAMENTO_TED_REQ.INT**: Fila para solicitação de pagamento TED via IBM MQ.

### 11. Integrações Externas
- **SITP**: Sistema de integração para registro de pagamentos de boletos.
- **SPAG**: Sistema de validação e registro de pagamentos.
- **PGFT**: Sistema de registro de pagamentos via protocolo PGFT.
- **Google Cloud Pub/Sub**: Utilizado para comunicação assíncrona.
- **IBM MQ**: Utilizado para integração de pagamentos TED.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado, com uso adequado de padrões de projeto e boas práticas de programação. A utilização de frameworks como Spring Boot e Apache Camel facilita a integração e orquestração de processos. No entanto, a documentação poderia ser mais detalhada em algumas partes para melhorar a compreensão do fluxo de dados e regras de negócio.

### 13. Observações Relevantes
- O sistema utiliza Swagger para documentação das APIs, facilitando o entendimento e uso dos endpoints disponíveis.
- A configuração de cache é feita utilizando Ehcache, com eventos de criação e expiração logados.
- A integração com sistemas externos é feita principalmente via REST APIs, com autenticação OAuth2.