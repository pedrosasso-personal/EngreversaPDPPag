## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um orquestrador de mensagens utilizando Apache Camel para integração com o Sistema de Pagamentos Brasileiro (SPB). Ele processa, valida e envia mensagens para câmaras de liquidação, além de gerenciar o histórico e status das mensagens enviadas.

### 2. Principais Classes e Responsabilidades
- **AtualizarReplicaSpbLegadoProcessor**: Processa a atualização de réplicas no SPB legado.
- **ConstruirMensagemProcessor**: Constrói a mensagem de envio para o SPB.
- **ExceptionProcessor**: Processa exceções ocorridas durante o envio de mensagens.
- **MensagemCamaraProcessor**: Processa mensagens para câmaras de liquidação.
- **MensagemEnvioRetornoProcessor**: Processa o retorno de envio de mensagens.
- **MensagemStatusErrorProcessor**: Processa erros de status de mensagens.
- **MensagemStatusProcessor**: Processa o status de envio de mensagens.
- **MontarMensagemProcessor**: Monta a mensagem processada para envio.
- **PrepararMensagemCriptografarProcessor**: Prepara a mensagem para criptografia.
- **ResilienciaExceptionProcessor**: Processa exceções de resiliência.
- **ValidarMensagemProcessor**: Valida a mensagem antes do envio.
- **ValidarPayloadProcessor**: Valida o payload da mensagem.
- **ValidarReplicaSPBLegadoProcessor**: Valida a necessidade de processamento no SPB legado.
- **VerificarHistoricoProcessor**: Verifica o histórico de mensagens.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- Apache Camel
- Kafka
- IBM MQ
- Swagger
- Maven

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST   | /v1/validar-mensagem | sbp-legado-controller | Validação de mensagens |
| PUT    | /v1/spb-legado/replica | sbp-legado-controller | Atualização de SPB Legado Replica |
| POST   | /v1/conversor/mensagem-envio | mensagemEnvio | Retorna mensagens XML para integração com BACEN |
| GET    | /v1/movimentos/{cdMovimento}/existente | mensageriaHistorico | Verifica a existência de um movimento pelo código |

### 5. Principais Regras de Negócio
- Validação de mensagens antes do envio.
- Criptografia de mensagens para segurança.
- Atualização de réplicas no SPB legado.
- Verificação de histórico de mensagens para evitar duplicidade.
- Envio de mensagens para câmaras de liquidação.

### 6. Relação entre Entidades
- **EnvioMensagemSPBDomain**: Representa a mensagem a ser enviada, contendo informações como tipo, instituição, e conteúdo.
- **ControleSPBDomain**: Informações de controle para o processamento da mensagem no SPB.
- **MensagemCamaraDomain**: Representa a mensagem processada para câmaras de liquidação.
- **MensagemCriptografar**: Contém informações para criptografia da mensagem.

### 7. Estruturas de Banco de Dados Lidas
Não se aplica.

### 8. Estruturas de Banco de Dados Atualizadas
Não se aplica.

### 9. Filas Lidas
- Kafka: Consome mensagens do tópico configurado no `application.yml`.

### 10. Filas Geradas
- Kafka: Publica mensagens processadas e status de envio em tópicos configurados.

### 11. Integrações Externas
- APIs de integração com SPB para validação e envio de mensagens.
- IBM MQ para envio de mensagens a câmaras de liquidação.
- Kafka para processamento de mensagens.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de programação, como injeção de dependências e uso de padrões de projeto. A documentação é clara e os testes são abrangentes. No entanto, poderia haver uma melhor organização dos pacotes para facilitar a navegação.

### 13. Observações Relevantes
- O sistema utiliza feature toggles para habilitar ou desabilitar funcionalidades de forma dinâmica.
- A configuração de segurança é feita através de OAuth2, garantindo a proteção dos endpoints.
- A aplicação é configurada para diferentes ambientes (desenvolvimento, teste, produção) através de arquivos YAML.