```markdown
## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema "EnviarMensagem" é um serviço stateless desenvolvido para enviar mensagens ao Banco Central (Bacen) e gerenciar tokens de participantes. Ele utiliza o Google Cloud Pub/Sub para comunicação assíncrona e Apache Camel para roteamento de mensagens.

### 2. Principais Classes e Responsabilidades
- **Application**: Classe principal que inicia a aplicação Spring Boot.
- **EnviarMensagemService**: Serviço responsável por enviar mensagens utilizando o Camel.
- **EnviarMensagemRepositoryImpl**: Implementação do repositório para enviar solicitações de pagamento ao Bacen.
- **RemoveTokenPublisherRepositoryImpl**: Implementação do repositório para publicar mensagens de remoção de tokens.
- **EnviarMensageListener**: Listener que consome mensagens do Pub/Sub e aciona o serviço de envio.
- **AuditJsonProcessor**: Processador Camel que converte objetos AuditJson em JSON.
- **StartMetricasProcessor**: Processador Camel que inicia métricas de liquidação.
- **RemoveTokenProcessor**: Processador Camel que prepara o payload para remoção de tokens.

### 3. Tecnologias Utilizadas
- Spring Boot
- Apache Camel
- Google Cloud Pub/Sub
- Maven
- Docker
- Prometheus
- Grafana

### 4. Principais Endpoints REST
Não se aplica.

### 5. Principais Regras de Negócio
- Envio de mensagens ao Bacen utilizando o protocolo PIX.
- Remoção de tokens de participantes após o processamento de mensagens.
- Geração e publicação de métricas de liquidação.

### 6. Relação entre Entidades
- **AuditJson**: Contém informações de auditoria de mensagens enviadas.
- **RemoveTokenPayload**: Representa o payload para remoção de tokens.
- **SpiMetrics**: Contém métricas relacionadas a eventos de liquidação.

### 7. Estruturas de Banco de Dados Lidas
Não se aplica.

### 8. Estruturas de Banco de Dados Atualizadas
Não se aplica.

### 9. Filas Lidas
- **sendMessageSpiBvsa**: Fila do Google Cloud Pub/Sub para envio de mensagens SPI.

### 10. Filas Geradas
- **removeToken**: Fila do Google Cloud Pub/Sub para remoção de tokens.
- **liquidationMetrics**: Fila do Google Cloud Pub/Sub para métricas de liquidação.
- **saveMessage**: Fila do Google Cloud Pub/Sub para salvar mensagens.

### 11. Integrações Externas
- Banco Central (Bacen) via API PIX.
- Google Cloud Pub/Sub para comunicação assíncrona.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código está bem estruturado e utiliza boas práticas de programação, como injeção de dependências e uso de padrões de projeto. A documentação e os testes são adequados, mas poderiam ser mais detalhados em algumas áreas.

### 13. Observações Relevantes
- O sistema utiliza configuração baseada em YAML para gerenciar diferentes ambientes (desenvolvimento, QA, UAT, produção).
- A aplicação é containerizada utilizando Docker, facilitando a implantação em ambientes de nuvem.
- Métricas customizadas são geradas e visualizadas através do Prometheus e Grafana.

---
```