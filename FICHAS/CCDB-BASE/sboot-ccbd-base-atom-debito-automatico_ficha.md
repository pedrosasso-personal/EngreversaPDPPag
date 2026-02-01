## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um microsserviço corporativo atômico responsável por gerenciar débitos automáticos dos produtos do banco digital. Ele oferece funcionalidades para agendamento, consulta, cancelamento e monitoramento de pagamentos em débito automático.

### 2. Principais Classes e Responsabilidades
- **DebitoAutomaticoConfiguration**: Configurações de Jdbi e repositórios para débito automático.
- **JmsConfiguration**: Configuração de JMS para mensagens.
- **RabbitConfiguration**: Configuração de RabbitMQ para mensagens.
- **PagamentoDebitoAutomaticoRepositoryImpl**: Implementação do repositório de pagamentos de débito automático.
- **DebitoAutomaticoController**: Controlador REST para gerenciar endpoints de débito automático.
- **DebitoAutomaticoService**: Serviço principal para lógica de negócios de débito automático.
- **PagamentoDebitoAutomaticoService**: Serviço para operações de pagamento de débito automático.
- **DebitoAutomaticoEfetivadoEventProducer**: Produtor de eventos Kafka para débito automático efetivado.
- **DebitoAutomaticoEfetivadoEventProducerV2**: Produtor de eventos Kafka para débito automático efetivado versão 2.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- RabbitMQ
- Kafka
- Jdbi
- MySQL
- Swagger
- Lombok

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST   | /v1/banco-digital/conta/debito-automatico/agendar | DebitoAutomaticoController | Agendar pagamento em débito automático |
| GET    | /v1/banco-digital/conta/debito-automatico/consultarPagamentoPorNuProtocoloPagamento/{numeroProcotoloSolicitacao} | DebitoAutomaticoController | Consultar pagamento por número de protocolo |
| PUT    | /v1/banco-digital/conta/debito-automatico/cancela-agendamento-debito-por-numero-contrato/{numeroContrato} | DebitoAutomaticoController | Cancelar agendamento de débito por número de contrato |
| GET    | /v1/banco-digital/conta/debito-automatico/consultar | DebitoAutomaticoController | Consultar pagamentos por data de pagamento |
| GET    | /v1/banco-digital/conta/debito-automatico/consultarTotalPagamentosPorConvenio | DebitoAutomaticoController | Consultar total de pagamentos por convênio |

### 5. Principais Regras de Negócio
- Agendamento de pagamentos de débito automático com validação de convenios e arquivos.
- Atualização de status de pagamento com base em tentativas e condições de saldo.
- Cancelamento de agendamentos anteriores para contratos com sequência anterior.
- Produção de eventos Kafka para notificações de débito automático efetivado.

### 6. Relação entre Entidades
- **PagamentoDebitoAutomatico**: Relacionado a **PessoaPagamentoDebitoAutomatico**, **ConvenioDebitoAutomatico**, **ArquivoDebitoAutomatico**, e **StatusPagamentoDebitoAutomatico**.
- **ConvenioDebitoAutomatico**: Relacionado a **TipoProdutoDebitoAutomatico**.
- **EventoDebitoAutomaticoEfetivado**: Extende **PagamentoDebitoAutomaticoBase**.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbPagamentoDebitoAutomatico | tabela | SELECT | Armazena informações de pagamentos de débito automático |
| TbConvenioDebitoAutomatico | tabela | SELECT | Armazena informações de convênios de débito automático |
| TbArquivoDebitoAutomatico | tabela | SELECT | Armazena informações de arquivos de débito automático |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbPagamentoDebitoAutomatico | tabela | INSERT/UPDATE | Atualiza status e informações de pagamentos de débito automático |
| TbConvenioDebitoAutomatico | tabela | INSERT | Insere novos convênios de débito automático |
| TbArquivoDebitoAutomatico | tabela | INSERT | Insere novos arquivos de débito automático |

### 9. Filas Lidas
- **queueCancelamentoAgendamentoFatura**: Fila JMS para cancelamento de agendamentos de fatura.

### 10. Filas Geradas
- **debito_automatico.proc.pagamento**: Fila RabbitMQ para processamento de pagamentos.

### 11. Integrações Externas
- Kafka para produção de eventos de débito automático efetivado.
- RabbitMQ para mensageria de cancelamento e processamento de pagamentos.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de programação, como injeção de dependências e uso de interfaces para repositórios. A documentação e os logs são adequados, facilitando a manutenção e entendimento do fluxo de dados. No entanto, poderia haver uma maior cobertura de testes automatizados.

### 13. Observações Relevantes
- O sistema utiliza configurações de feature toggle para controlar funcionalidades específicas.
- A integração com Kafka e RabbitMQ é essencial para o funcionamento do sistema, garantindo a comunicação assíncrona entre componentes.