## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema "spag.base.monitoramento-contas" é um serviço REST desenvolvido em Java utilizando o framework Spring Boot. Ele tem como objetivo realizar operações de bloqueio e desbloqueio de contas financeiras, integrando-se com serviços de Fintech para gerenciar solicitações judiciais de bloqueio de valores. O sistema também inclui funcionalidades para consulta de saldo e envio de notificações via filas JMS.

### 2. Principais Classes e Responsabilidades
- **BloqueioService**: Serviço responsável por gerenciar operações de bloqueio e desbloqueio de contas, interagindo com repositórios e gateways.
- **AppConfigurantionFintech**: Configuração do RestTemplate para comunicação com serviços Fintech.
- **AppConfigurationListener**: Configuração de listeners JMS para processamento de mensagens.
- **FintechRepository**: Repositório para operações de banco de dados relacionadas a processos e solicitações judiciais.
- **GatewayRepository**: Repositório para comunicação com serviços externos via REST, incluindo geração de tokens de autenticação.
- **MonitoramentoAPI**: Classe controladora REST que expõe endpoints para operações de bloqueio e desbloqueio.
- **SolicitacaoMQListener**: Listener JMS para processamento de mensagens de bloqueio e desbloqueio recebidas via fila.

### 3. Tecnologias Utilizadas
- Spring Boot
- Spring MVC
- Spring JMS
- Spring Data JDBC
- Swagger
- Jackson
- Microsoft SQL Server
- IBM MQ
- Gradle

### 4. Principais Endpoints REST
| Método | Endpoint                  | Classe Controladora | Descrição                                      |
|--------|---------------------------|---------------------|------------------------------------------------|
| POST   | /monitoramento/bloquear   | MonitoramentoAPI    | Envia solicitação de bloqueio para Fintechs.   |
| POST   | /monitoramento/desBloquearIntraday | MonitoramentoAPI | Envia solicitação de desbloqueio intraday.     |
| POST   | /monitoramento/desBloquearPorValor | MonitoramentoAPI | Envia solicitação de desbloqueio por valor.    |

### 5. Principais Regras de Negócio
- Bloqueio de contas baseado em solicitações judiciais.
- Desbloqueio de contas intraday e por valor solicitado.
- Consulta de saldo de contas para validação de operações.
- Envio de notificações via filas JMS após processamento de bloqueio/desbloqueio.

### 6. Relação entre Entidades
- **BloqueioVO**: Representa os dados de uma solicitação de bloqueio.
- **ProcessoJuridico**: Entidade que representa um processo jurídico associado a uma conta.
- **SolicitacaoJuridico**: Entidade que representa uma solicitação jurídica de bloqueio ou desbloqueio.
- **DadosFintechDomain**: Contém informações de integração com parceiros Fintech.
- **ContaFintech**: Representa uma conta financeira com detalhes de saldo e bloqueios.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbUsuarioContaFintech       | tabela | SELECT   | Consulta dados de contas de usuários Fintech. |
| TbProcessoJuridico          | tabela | SELECT   | Consulta processos jurídicos associados.      |
| TbSolicitacaoJuridico       | tabela | SELECT   | Consulta solicitações jurídicas registradas.  |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbProcessoJuridico          | tabela | INSERT/UPDATE | Registra ou atualiza processos jurídicos.     |
| TbSolicitacaoJuridico       | tabela | INSERT/UPDATE | Registra ou atualiza solicitações jurídicas.  |
| TbProcessamentoMovimentoJuridico | tabela | INSERT/UPDATE | Registra ou atualiza movimentações de bloqueio. |

### 9. Filas Lidas
- QL.ATACADO.BLOQUEIO_VALORES_JUDICIAIS_OUT.INT

### 10. Filas Geradas
- QL.ATACADO.BLOQUEIO_VALORES_JUDICIAIS_IN.INT

### 11. Integrações Externas
- API Gateway para operações Fintech.
- Serviços de autenticação via OAuth2 para geração de tokens.
- Filas JMS para envio e recebimento de notificações.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado, utilizando boas práticas de desenvolvimento como injeção de dependências e separação de responsabilidades. A documentação via Swagger facilita a compreensão dos endpoints REST. No entanto, algumas áreas poderiam ser melhoradas em termos de clareza e tratamento de exceções.

### 13. Observações Relevantes
- O sistema utiliza configuração de segurança básica e LDAP para autenticação.
- As operações de bloqueio e desbloqueio são críticas e devem ser monitoradas para garantir a integridade dos dados financeiros.
- A configuração de logging é feita via Logback, permitindo ajustes de nível de log conforme o ambiente.