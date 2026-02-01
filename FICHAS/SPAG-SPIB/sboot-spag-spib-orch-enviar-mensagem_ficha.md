```markdown
## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema "EnviarMensagem" é um serviço stateless desenvolvido para enviar mensagens de pagamento ao Bacen e realizar operações de remoção de tokens. Ele utiliza o Spring Boot e integra-se com o Google Cloud Pub/Sub para publicação e consumo de mensagens. O sistema também possui funcionalidades de monitoramento e métricas através do Prometheus e Grafana.

### 2. Principais Classes e Responsabilidades
- **Application**: Classe principal que inicia a aplicação Spring Boot.
- **EnviarMensagemService**: Serviço responsável por enviar mensagens utilizando o Camel.
- **EnviarMensagemRepositoryImpl**: Implementação do repositório que interage com o Bacen para enviar solicitações de pagamento.
- **RemoveTokenPublisherRepositoryImpl**: Implementação do repositório que publica mensagens de remoção de tokens no Pub/Sub.
- **EnviarMensagemListener**: Componente que escuta mensagens do Pub/Sub e aciona o serviço de envio.
- **CamelContextWrapper**: Wrapper para o contexto do Camel, gerencia rotas e componentes.
- **AuditJsonToDocumentProcessor**: Processador Camel que converte objetos AuditJson para JSON.
- **StartMetricasProcessor**: Processador Camel que inicia o processamento de métricas.
- **EndMetricasProcessor**: Processador Camel que finaliza o processamento de métricas.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- Apache Camel
- Google Cloud Pub/Sub
- Prometheus
- Grafana
- Docker

### 4. Principais Endpoints REST
Não se aplica.

### 5. Principais Regras de Negócio
- Envio de solicitações de pagamento ao Bacen.
- Remoção de tokens de participantes através do Pub/Sub.
- Processamento de métricas de liquidação e indicadores.

### 6. Relação entre Entidades
- **AuditJson**: Armazena informações de auditoria relacionadas ao envio de mensagens.
- **RemoveTokenPayload**: Representa o payload para remoção de tokens.
- **SpiMetrics**: Contém eventos e indicadores de métricas SPI.
- **LiquidationMetrics**: Armazena métricas de liquidação de mensagens.

### 7. Estruturas de Banco de Dados Lidas
Não se aplica.

### 8. Estruturas de Banco de Dados Atualizadas
Não se aplica.

### 9. Filas Lidas
- **sendMessageSPI**: Fila do Pub/Sub para envio de mensagens SPI.

### 10. Filas Geradas
- **removeToken**: Fila do Pub/Sub para remoção de tokens.
- **settlementMetrics**: Fila do Pub/Sub para métricas de liquidação.
- **saveMessage**: Fila do Pub/Sub para salvar mensagens.

### 11. Integrações Externas
- **Bacen API**: Integração para envio de solicitações de pagamento.
- **Google Cloud Pub/Sub**: Utilizado para publicação e consumo de mensagens.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de desenvolvimento, como injeção de dependências e uso de padrões de projeto. A documentação está presente, e os testes cobrem uma boa parte das funcionalidades. No entanto, a ausência de endpoints REST pode limitar a interação externa.

### 13. Observações Relevantes
- O sistema utiliza Docker para empacotamento e execução, facilitando a implantação em ambientes de nuvem.
- As métricas são geradas e monitoradas através do Prometheus e Grafana, permitindo uma análise detalhada do desempenho do sistema.
- A configuração do sistema é gerenciada através de arquivos YAML e propriedades do Spring Boot, permitindo flexibilidade na configuração de diferentes ambientes.

---
```