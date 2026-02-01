## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um serviço de mensageria que utiliza o framework Spring Boot para gerenciar operações de envio e recebimento de mensagens, integrando-se com o Apache Kafka para mensageria e MySQL como banco de dados. Ele é projetado para processar mensagens do SPB (Sistema de Pagamentos Brasileiro), realizando operações de consulta, atualização e gerenciamento de circuit breaks.

### 2. Principais Classes e Responsabilidades
- **Application.java**: Classe principal que inicia a aplicação Spring Boot.
- **CustomStatusEnvioListenerErrorHandler.java**: Manipulador de erros para o Kafka Listener, tratando exceções específicas.
- **JdbiConfiguration.java**: Configuração do Jdbi para integração com o banco de dados.
- **MensageriaConfiguration.java**: Configuração de serviços e mapeadores relacionados à mensageria.
- **MovimentoService.java**: Serviço responsável por operações de inserção e atualização de movimentos.
- **CircuitBreakService.java**: Serviço para gerenciar circuit breaks, incluindo consulta e atualização.
- **KafkaConsumer.java**: Componente que consome mensagens do Kafka e processa atualizações de movimento.
- **MovimentoMapper.java**: Interface de mapeamento para converter entre entidades de movimento e representações.
- **ErroMovimentoMapper.java**: Interface de mapeamento para converter entre entidades de erro de movimento e representações.
- **RestResponseEntityExceptionHandler.java**: Manipulador global de exceções para respostas REST.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- Apache Kafka
- MySQL
- JDBI
- OpenAPI
- Lombok

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET    | /dominios | DominiosApiDelegateImpl | Consulta de domínios e erros |
| POST   | /v1/conversor/mensagem-envio | MensageriaApiDelegateImpl | Envio de mensagem para processamento |
| POST   | /v1/conversor/recebimento-mensagem | MensageriaApiDelegateImpl | Recebimento de mensagem para processamento |
| PUT    | /v1/atualiza-movimento | MensageriaApiDelegateImpl | Atualização de movimento |
| GET    | /v1/movimentos | MensageriaApiDelegateImpl | Consulta de movimentos no SPB Core |
| GET    | /v1/contingencia/circuit-break/historico | MensageriaApiDelegateImpl | Consulta do histórico de alterações de circuit break |
| POST   | /v1/contingencia/circuit-break | MensageriaApiDelegateImpl | Criação ou atualização de registro de circuit break |
| GET    | /v1/movimentos/search | MensageriaApiDelegateImpl | Pesquisa de movimentos paginados |
| GET    | /v1/movimentos/{cdMovimento}/fluxo | MensageriaApiDelegateImpl | Consulta de fluxo de movimento |
| GET    | /v1/gerar-nsu | MensageriaApiDelegateImpl | Geração de NSU |

### 5. Principais Regras de Negócio
- Processamento de mensagens do SPB, incluindo validação de circuit breaks.
- Conversão de mensagens entre formatos JSON e XML.
- Gerenciamento de movimentos, incluindo inserção, atualização e consulta.
- Implementação de circuit breaks para controle de envio de mensagens.
- Validação de dados de entrada e tratamento de erros específicos.

### 6. Relação entre Entidades
- **Movimento**: Entidade principal representando um movimento no sistema, relacionada a detalhes, erros e fluxos de movimento.
- **CircuitBreak**: Entidade representando o estado de circuit breaks, com histórico de alterações.
- **MensagemEnvio**: Entidade representando mensagens enviadas para processamento.
- **ErroMovimento**: Entidade representando erros associados a movimentos.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbMovimento                 | tabela | SELECT | Armazena informações de movimentos do SPB |
| TbDetalheMovimento          | tabela | SELECT | Detalhes específicos de cada movimento |
| TbFluxoMovimento            | tabela | SELECT | Fluxo de ações realizadas em cada movimento |
| TbErroMovimento             | tabela | SELECT | Erros associados aos movimentos |
| TlControleEnvioMovimento    | tabela | SELECT | Controle de envio de movimentos, utilizado para circuit breaks |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbMovimento                 | tabela | INSERT/UPDATE | Inserção e atualização de movimentos do SPB |
| TbDetalheMovimento          | tabela | INSERT | Inserção de detalhes de movimentos |
| TbFluxoMovimento            | tabela | INSERT | Inserção de fluxos de ações em movimentos |
| TbErroMovimento             | tabela | INSERT | Inserção de erros associados a movimentos |
| TlControleEnvioMovimento    | tabela | INSERT/UPDATE | Inserção e atualização de registros de circuit breaks |

### 9. Filas Lidas
- Kafka: spbb-base-status-envio-mensagem

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- Kafka para mensageria.
- MySQL para armazenamento de dados.
- APIs externas para autenticação e autorização via OAuth2.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de programação, como injeção de dependências e uso de mapeadores para conversão de entidades. A documentação é clara e os componentes são bem separados, facilitando a manutenção. No entanto, poderia haver uma maior cobertura de testes unitários para garantir a robustez do sistema.

### 13. Observações Relevantes
- O sistema utiliza o conceito de circuit break para controlar o envio de mensagens, garantindo que operações não sejam realizadas quando o sistema está em estado crítico.
- A configuração do sistema é gerenciada por meio de arquivos YAML, permitindo flexibilidade na definição de ambientes e variáveis de configuração.