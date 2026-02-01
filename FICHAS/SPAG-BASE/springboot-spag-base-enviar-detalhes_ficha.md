## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema "springboot-spag-base-enviar-detalhes" é um serviço REST desenvolvido em Spring Boot, que tem como objetivo facilitar a comunicação de notificações entre sistemas, especialmente para fintechs. Ele possui funcionalidades para consulta de detalhes de notificações e solicitação de reenvio de mensagens.

### 2. Principais Classes e Responsabilidades
- **NotificacaoDetalheService**: Serviço principal que gerencia as operações de consulta e reenvio de notificações.
- **AppConfigurationListener**: Configurações de listener para JMS, incluindo conversão de mensagens.
- **AppPropertiesFintech**: Propriedades de configuração específicas para fintechs.
- **AppPropertiesMq**: Propriedades de configuração para integração com filas de mensagens.
- **DocketConfiguration**: Configuração do Swagger para documentação de APIs.
- **MappingMessageLocalConverter**: Conversor de mensagens personalizado para integração com JMS.
- **UtilSpag**: Classe utilitária para manipulação de datas e conversão de objetos para JSON.
- **ControleRetornoNotificacao**: Modelo de dados para controle de retorno de notificações.
- **EventoNotificacao**: Modelo de dados para eventos de notificações.
- **Fintech**: Modelo de dados para informações de fintechs.
- **NotificacaoFintech**: Modelo de dados para notificações específicas de fintechs.
- **MockDomain**: Classe para criar objetos de domínio mock para testes.
- **RequestConsultaDetalhe**: Modelo de dados para requisições de consulta de detalhes.
- **RequestNotificacao**: Modelo de dados para requisições de notificações.
- **RequestReenvio**: Modelo de dados para requisições de reenvio de notificações.
- **ResponseConsultaDetalhe**: Modelo de dados para respostas de consulta de detalhes.
- **ResponseReenvio**: Modelo de dados para respostas de reenvio de notificações.
- **NotificacaoDetalheRepository**: Repositório para operações de banco de dados relacionadas a notificações.
- **NotificacaoMQRepository**: Repositório para operações de envio de mensagens para filas JMS.
- **NotificacaoDetalheApi**: API REST para operações de consulta e reenvio de notificações.
- **Server**: Classe principal para inicialização do aplicativo Spring Boot.

### 3. Tecnologias Utilizadas
- Spring Boot
- Spring Data JDBC
- JMS (Java Message Service)
- Swagger (para documentação de APIs)
- SQL Server (para persistência de dados)
- Docker (para containerização)
- Gradle (para build e dependências)
- JMeter (para testes funcionais)

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST   | /v1/buscaDetalheMensagem | NotificacaoDetalheApi | Busca detalhes de uma mensagem de notificação. |
| POST   | /v1/solicitaReenvioMensagem | NotificacaoDetalheApi | Solicita o reenvio de uma mensagem de notificação. |

### 5. Principais Regras de Negócio
- Validação de CNPJ e protocolo para operações de consulta e reenvio.
- Limite de reenvio de notificações por dia.
- Verificação de confidencialidade de eventos de notificação.
- Expiração de protocolos de notificação após um tempo configurado.

### 6. Relação entre Entidades
- **NotificacaoFintech** está relacionada a **EventoNotificacao** através do campo `cdEventoNotificacao`.
- **ControleRetornoNotificacao** está relacionada a **NotificacaoFintech** através do campo `cdNotificacaoFintech`.
- **Fintech** pode ser associada a múltiplas **NotificacaoFintech**.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| tbNotificacaoFintech        | tabela | SELECT | Armazena notificações enviadas para fintechs. |
| TbEventoNotificacao         | tabela | SELECT | Armazena eventos de notificações. |
| TbControleRetornoNotificacao| tabela | SELECT | Armazena logs de retorno de notificações. |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| tbNotificacaoFintech        | tabela | UPDATE | Atualiza detalhes de envio de notificações. |
| TbControleRetornoNotificacao| tabela | INSERT | Insere logs de retorno de notificações. |

### 9. Filas Lidas
- Não se aplica.

### 10. Filas Geradas
- QL.SPAG.NOTIFICAR_PARCEIRO_REQ.INT: Fila JMS para envio de notificações.

### 11. Integrações Externas
- Integração com IBM MQ para envio de mensagens.
- Integração com SQL Server para persistência de dados.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de desenvolvimento, como injeção de dependências e uso de annotations do Spring. A documentação via Swagger é um ponto positivo. No entanto, algumas partes do código poderiam ser mais claras, especialmente em relação ao tratamento de exceções e logs.

### 13. Observações Relevantes
- O projeto possui um README.md que orienta sobre como iniciar o serviço e utilizar o repositório.
- A configuração do projeto está bem organizada, com uso de arquivos YAML para diferentes ambientes.
- O uso de Docker e Gradle facilita a construção e implantação do projeto.