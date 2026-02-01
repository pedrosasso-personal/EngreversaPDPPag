## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um orquestrador de mensagens utilizando Apache Camel, desenvolvido em Java com Spring Boot. Ele processa e envia mensagens para o Banco Central (BACEN) e realiza auditoria e métricas de liquidação, integrando-se com o serviço de mensageria Atlante PubSub.

### 2. Principais Classes e Responsabilidades
- **Application**: Classe principal que inicia a aplicação Spring Boot.
- **AuditJsonToDocumentProcessor**: Processa objetos `AuditJson` para convertê-los em formato JSON.
- **EndMetricasProcessor**: Finaliza o processamento de métricas, ajustando o tipo de evento e o tempo.
- **IdentifyTypeMessageProcessor**: Identifica o tipo de mensagem a partir de um XML.
- **RemoveTokenProcessor**: Processa a remoção de tokens, configurando o payload para a operação.
- **StartMetricasProcessor**: Inicia o processamento de métricas a partir de um XML.
- **EnviarMensagemRouter**: Define rotas de processamento de mensagens, incluindo publicação em tópicos PubSub.
- **RemoveTokenRouter**: Define rotas para remoção de tokens.
- **CamelContextWrapper**: Envolve o contexto Camel, permitindo a adição de rotas e componentes.
- **PubSubConfig**: Configura o conversor de mensagens PubSub usando Jackson.
- **EnviarMensagemBaConfiguration**: Configuração base do sistema, incluindo beans para Camel e RestTemplate.
- **EnviarMensagemRepositoryImpl**: Implementação do repositório para enviar solicitações de pagamento ao BACEN.
- **PubSubPublisher**: Publica mensagens em tópicos PubSub.
- **RemoveTokenPublisherRepositoryImpl**: Implementação do repositório para publicar remoção de tokens.
- **EnviarMensagemService**: Serviço que envia mensagens utilizando o template do Camel.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- Apache Camel
- Google Cloud PubSub
- Atlante PubSub Service
- Dinamo Networks

### 4. Principais Endpoints REST
Não se aplica.

### 5. Principais Regras de Negócio
- Envio de solicitações de pagamento ao BACEN.
- Processamento de métricas de liquidação.
- Identificação e remoção de tokens.
- Publicação de mensagens de auditoria e métricas em tópicos PubSub.

### 6. Relação entre Entidades
- **AuditJson**: Entidade que representa dados de auditoria de mensagens.
- **IndicatorsMetrics**: Entidade que representa métricas de indicadores.
- **LiquidationMetrics**: Entidade que representa métricas de liquidação.
- **RemoveTokenPayload**: Entidade que representa o payload para remoção de tokens.
- **SpiMetrics**: Entidade que contém listas de métricas de indicadores e liquidação.
- **TypeMessageEnum**: Enumeração que define tipos de mensagens e suas tags XML.

### 7. Estruturas de Banco de Dados Lidas
Não se aplica.

### 8. Estruturas de Banco de Dados Atualizadas
Não se aplica.

### 9. Filas Lidas
- **sendMessageSPI**: Subscrição para receber mensagens SPI.

### 10. Filas Geradas
- **removeToken**: Tópico para publicar remoção de fichas.
- **settlementMetrics**: Tópico para publicar métricas de liquidação.
- **saveMessage**: Tópico para publicar mensagens de auditoria.

### 11. Integrações Externas
- **BACEN**: Envio de mensagens para o Banco Central.
- **Dinamo Networks**: Utilizado para comunicação segura com o BACEN.
- **Google Cloud PubSub**: Utilizado para publicação e subscrição de mensagens.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código está bem estruturado, com uso adequado de padrões de projeto e boas práticas de programação. A utilização de Apache Camel para orquestração de mensagens é eficiente. No entanto, poderia haver mais documentação interna para facilitar a compreensão de algumas partes complexas.

### 13. Observações Relevantes
- O sistema utiliza variáveis de ambiente para configuração, o que facilita a adaptação a diferentes ambientes (desenvolvimento, homologação, produção).
- A integração com o serviço de mensageria Atlante PubSub é um ponto chave para a comunicação assíncrona do sistema.