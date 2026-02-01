## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um orquestrador de mensagens utilizando Apache Camel, projetado para processar e integrar mensagens do Sistema de Pagamentos Brasileiro (SPB). Ele realiza operações de recebimento, descriptografia, conversão e envio de mensagens, integrando-se com serviços externos via APIs REST e Kafka.

### 2. Principais Classes e Responsabilidades
- **AtualizaMovimentoProcessor**: Processa a atualização de movimentos com base em mensagens recebidas.
- **ExtracaoMensagemBacenProcessor**: Extrai e processa mensagens do Bacen.
- **MensagemCriptografadaProcessor**: Descriptografa mensagens recebidas.
- **MensagemRecebidaProcessor**: Processa mensagens recebidas e prepara para envio.
- **SPBBVAclProcessor**: Publica eventos de mensagens recebidas.
- **MensagemRecebidaSPBRouter**: Define rotas para processamento de mensagens recebidas.
- **ProcessamentoMensagemCoreRouter**: Define rotas para processamento de mensagens core.
- **RecebimentoMensagemSpbRouter**: Define rotas para recebimento de mensagens SPB.
- **RouterProperties**: Configura propriedades de roteamento.
- **AuthProperties**: Configura propriedades de autenticação.
- **GatewayOAuthServiceConfig**: Configura o serviço OAuth do gateway.
- **RestTemplateConfiguration**: Configura o RestTemplate para chamadas HTTP.
- **MqConfigurationProperties**: Configura propriedades de conexão com MQ.
- **PubSubRecebimentoMensagemSpbConfiguration**: Configura o recebimento de mensagens via Pub/Sub.
- **ApiClientConfiguration**: Configura clientes de API para integração.
- **DecryptConfiguration**: Configura o serviço de descriptografia.
- **RecebimentoMensagemSpbConfiguration**: Configura serviços de recebimento de mensagens SPB.
- **MensagemDescriptografar**: Representa uma mensagem a ser descriptografada.
- **MensagemRecebida**: Representa uma mensagem recebida.
- **RecebimentoMensagemDomain**: Domínio de mensagens recebidas.
- **EnvioMensagemProcessadaRepository**: Interface para envio de mensagens processadas.
- **EnvioMensagemRecebidaRepository**: Interface para envio de mensagens recebidas.
- **RecebimentoMensagemSpbServiceImpl**: Implementação do serviço de recebimento de mensagens SPB.
- **SpbAtomIntegracaoServiceImpl**: Implementação do serviço de integração com SPB Atom.
- **SpbAtomMensageriaServiceImpl**: Implementação do serviço de mensageria SPB Atom.
- **DecryptService**: Serviço de descriptografia de mensagens.
- **FeatureToggleService**: Serviço para controle de funcionalidades.
- **ConstantUtils**: Utilitário para constantes do sistema.
- **LoggerHelper**: Utilitário para sanitização de logs.
- **StopWatchUtil**: Utilitário para controle de tempo de execução.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- Apache Camel
- Apache Kafka
- Google Cloud Pub/Sub
- Maven
- Docker

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST   | /v1/processarMensagemCore | ProcessamentoMensagemCoreRouter | Processa mensagens core. |
| POST   | /v1/conversor/recebimento-mensagem | RecebimentoMensagemSpbRouter | Converte mensagens XML para JSON. |
| PUT    | /v1/atualiza-movimento | RecebimentoMensagemSpbRouter | Atualiza o movimento no SPB Core. |
| GET    | /storageIntegration | N/A | Retorna informações de armazenamento. |

### 5. Principais Regras de Negócio
- Descriptografia de mensagens utilizando SPBSecJava.
- Conversão de mensagens XML para JSON.
- Atualização de movimentos no SPB Core.
- Publicação de eventos de mensagens recebidas via Kafka.
- Integração com APIs externas para processamento de mensagens.

### 6. Relação entre Entidades
- **MensagemDescriptografar** e **MensagemRecebida** são utilizadas para processamento de mensagens.
- **RecebimentoMensagemDomain** encapsula informações de mensagens recebidas.
- **EnvioMensagemProcessadaRepository** e **EnvioMensagemRecebidaRepository** são responsáveis por enviar mensagens processadas e recebidas, respectivamente.

### 7. Estruturas de Banco de Dados Lidas
Não se aplica.

### 8. Estruturas de Banco de Dados Atualizadas
Não se aplica.

### 9. Filas Lidas
- Kafka: `spbb-base-mensagem-recebida-spb`
- Google Cloud Pub/Sub: `business-spbb-base-recebimento-mensagem-spb-sub`

### 10. Filas Geradas
- Kafka: `spbb-base-mensagem-processada`

### 11. Integrações Externas
- Integração com APIs REST do SPB Atom para processamento de mensagens.
- Integração com Google Cloud Pub/Sub para recebimento de mensagens.
- Integração com Kafka para publicação de eventos de mensagens.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de programação, como injeção de dependências e separação de responsabilidades. No entanto, poderia haver mais documentação e comentários para facilitar a compreensão de partes complexas.

### 13. Observações Relevantes
- O sistema utiliza feature toggles para controle de funcionalidades.
- A configuração de segurança é feita via OAuth2.
- O projeto está configurado para ser executado em ambientes de desenvolvimento, teste e produção, com diferentes perfis de configuração.