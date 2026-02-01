```markdown
## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um microsserviço corporativo atômico responsável por monitorar os bloqueios de saldo das contas correntes de clientes. Ele realiza operações de consulta, inclusão, atualização e deleção de monitoramentos de bloqueio de saldo.

### 2. Principais Classes e Responsabilidades
- **MdcSettingChannelInterceptor**: Intercepta mensagens para adicionar/remover informações de contexto de log (MDC).
- **CreditoBloqueadoListener**: Escuta mensagens de crédito recebido e processa o crédito.
- **MonitoramentoSaldoListener**: Escuta mensagens de atualização de monitoramento de saldo e processa a atualização.
- **MonitoramentoConcluidoPublisher**: Publica mensagens de conclusão de monitoramento.
- **TopicDefaultPublisher**: Publica mensagens em um tópico padrão.
- **MonitoramentoValidator**: Valida monitoramentos de saldo.
- **MonitoramentoApiDelegateImpl**: Implementa a API REST para operações de monitoramento de saldo.
- **MonitoramentoSaldoService**: Serviço principal para operações de monitoramento de saldo.
- **MotivoBloqueioService**: Serviço para operações relacionadas a motivos de bloqueio.

### 3. Tecnologias Utilizadas
- Spring Boot
- Spring Integration
- Spring Security
- JDBI
- MySQL
- Swagger
- Google Cloud Pub/Sub
- MapStruct

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | /v1/contas/monitoramentos/{cdMonitoramentoSaldo} | MonitoramentoApiDelegateImpl | Retorna informações de um monitoramento específico. |
| DELETE | /v1/contas/monitoramentos/{cdMonitoramentoSaldo} | MonitoramentoApiDelegateImpl | Altera a flag do bloqueio para 'N'. |
| GET | /v1/contas/monitoramentos/pendentes | MonitoramentoApiDelegateImpl | Retorna informações dos monitoramentos pendentes. |
| POST | /v1/contas/monitoramentos | MonitoramentoApiDelegateImpl | Cria um novo monitoramento de saldo. |
| PUT | /v1/contas/monitoramentos/{cdMonitoramentoSaldo}/bloqueios | MonitoramentoApiDelegateImpl | Atualiza bloqueios de saldo para um monitoramento específico. |
| GET | /v1/motivos-bloqueio/{cdMotivoBloqueio} | MonitoramentoApiDelegateImpl | Retorna informações de um motivo de bloqueio. |

### 5. Principais Regras de Negócio
- Validação de valores de operação para não serem nulos, negativos ou zero.
- Validação de motivos de bloqueio para serem ativos e monitorados.
- Verificação de conclusão de monitoramento baseado em valores bloqueados e solicitados.
- Publicação de mensagens em tópicos após operações de bloqueio.

### 6. Relação entre Entidades
- **MonitoramentoSaldo**: Contém informações de monitoramento de saldo e uma lista de **MonitoramentoSaldoBloqueado**.
- **MonitoramentoSaldoBloqueado**: Representa um saldo bloqueado específico.
- **MotivoBloqueio**: Contém informações sobre o motivo do bloqueio.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbMonitoramentoSaldo | tabela | SELECT | Armazena informações de monitoramento de saldo. |
| TbMonitoramentoSaldoBloqueado | tabela | SELECT | Armazena informações de saldos bloqueados. |
| TbMotivoBloqueio | tabela | SELECT | Armazena informações de motivos de bloqueio. |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbMonitoramentoSaldo | tabela | INSERT/UPDATE/DELETE | Armazena e atualiza informações de monitoramento de saldo. |
| TbMonitoramentoSaldoBloqueado | tabela | INSERT | Armazena novos saldos bloqueados. |

### 9. Filas Lidas
- **ATUALIZA_MONITORAMENTO_CHANNEL**: Consome mensagens de atualização de monitoramento.
- **CREDITO_RECEBIDO_CHANNEL**: Consome mensagens de crédito recebido.

### 10. Filas Geradas
- **monitoramentoConcluido**: Publica mensagens de conclusão de monitoramento.
- **default**: Publica mensagens em um tópico padrão.

### 11. Integrações Externas
- Google Cloud Pub/Sub: Utilizado para publicação e consumo de mensagens.
- MySQL: Banco de dados utilizado para persistência de dados.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de desenvolvimento, como injeção de dependências e separação de responsabilidades. No entanto, algumas áreas poderiam ter melhor documentação e tratamento de exceções mais detalhado.

### 13. Observações Relevantes
- O sistema utiliza OAuth2 para autenticação e autorização.
- A documentação do serviço está disponível via Swagger.
- O sistema está configurado para diferentes ambientes (des, uat, prd) com variáveis específicas para cada um.

--- 
```