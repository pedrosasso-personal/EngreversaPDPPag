## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um serviço REST desenvolvido em Java utilizando o framework Spring Boot. Ele é responsável por enviar notificações para fintechs, tratando tanto notificações ativas quanto passivas. O sistema também gerencia erros de notificações e integra-se com um gateway para envio de mensagens.

### 2. Principais Classes e Responsabilidades
- **NotificacaoErrorService**: Gerencia o envio de notificações de erro.
- **NotificacaoPassivaService**: Lida com notificações passivas, buscando e atualizando notificações.
- **NotificacaoService**: Responsável pelo envio de notificações ativas.
- **AppConfigurationFintech**: Configura o RestTemplate para comunicação com o backend.
- **AppConfigurationListener**: Configura o listener de JMS para mensagens.
- **ControllerExceptionHandler**: Trata exceções de recursos inválidos.
- **DocketConfiguration**: Configura o Swagger para documentação da API.
- **MappingMessageLocalConverter**: Converte mensagens de JMS utilizando Jackson.
- **UtilSpag**: Utilitário para manipulação de datas e conversão de objetos para JSON.
- **GatewayRepository**: Interage com o gateway para envio de mensagens.
- **NotificacaoRepository**: Gerencia operações de banco de dados relacionadas a notificações.
- **SpagRepository**: Lida com operações de banco de dados relacionadas a clientes wallet.

### 3. Tecnologias Utilizadas
- Spring Boot
- Spring Data
- Spring Security
- Swagger
- JMS (IBM MQ)
- SQL Server
- Docker
- JUnit
- Mockito

### 4. Principais Endpoints REST
| Método | Endpoint                | Classe Controladora       | Descrição                                      |
|--------|-------------------------|---------------------------|------------------------------------------------|
| POST   | /v1/sendMessage         | NotificacaoApi            | Envia uma nova mensagem de notificação.        |
| POST   | /v1/processaPendentes   | NotificacaoApi            | Processa notificações pendentes.               |
| POST   | /v1/getNotification     | NotificacaoPassivaApi     | Captura notificações passivas.                 |

### 5. Principais Regras de Negócio
- Envio de notificações para fintechs com tratamento de erros.
- Captura de notificações passivas com validação de datas.
- Integração com gateway para envio de mensagens.
- Uso de feature toggles para controle de fluxo de autenticação.

### 6. Relação entre Entidades
- **NotificacaoFintech**: Representa uma notificação enviada para fintechs.
- **NotificacaoErroFintech**: Representa uma notificação de erro.
- **EventoNotificacao**: Define eventos de notificação.
- **ClienteWallet**: Representa informações de clientes wallet.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbNotificacaoFintech        | tabela | SELECT | Armazena notificações enviadas. |
| TbNotificacaoErroFintech    | tabela | SELECT | Armazena notificações de erro. |
| TbEventoNotificacao         | tabela | SELECT | Armazena eventos de notificação. |
| TbParametroPagamentoFintech | tabela | SELECT | Armazena parâmetros de pagamento. |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbNotificacaoFintech        | tabela | INSERT/UPDATE | Armazena notificações enviadas. |
| TbNotificacaoErroFintech    | tabela | INSERT/UPDATE | Armazena notificações de erro. |

### 9. Filas Lidas
- QL.SPAG.NOTIFICAR_PARCEIRO_REQ.INT
- QL.ATACADO.NOTIFICACAO_ERRO.INT

### 10. Filas Geradas
- QL.ATACADO.NOTIFICACAO_ERRO.INT

### 11. Integrações Externas
- Gateway de mensagens para envio de notificações.
- ConfigCat para gerenciamento de feature toggles.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de desenvolvimento, como injeção de dependências e tratamento de exceções. A documentação através do Swagger é um ponto positivo. No entanto, algumas áreas poderiam ter melhor cobertura de testes e otimização de consultas SQL.

### 13. Observações Relevantes
- O sistema utiliza Docker para facilitar o deploy e execução em ambientes de desenvolvimento e produção.
- A configuração de segurança é feita através de Spring Security, com suporte a autenticação básica.
- O uso de feature toggles permite flexibilidade na configuração de rotas e autenticação.