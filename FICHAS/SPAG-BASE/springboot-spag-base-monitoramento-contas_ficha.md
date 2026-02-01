## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um serviço REST desenvolvido em Java utilizando o framework Spring Boot. Ele tem como objetivo realizar o monitoramento de contas, incluindo operações de bloqueio e desbloqueio de valores judiciais em contas de fintechs. O sistema também integra com serviços externos para realizar transferências e consultas de saldo.

### 2. Principais Classes e Responsabilidades
- **BloqueioService**: Serviço principal que gerencia operações de bloqueio e desbloqueio de contas.
- **AppConfigurantionFintech**: Configuração de beans relacionados à integração com fintechs.
- **AppPropertiesFintech**: Propriedades de configuração para integração com fintechs.
- **DBConfigurationSPAG**: Configuração de datasources para acesso ao banco de dados.
- **MonitoramentoAPI**: Controlador REST que expõe endpoints para operações de bloqueio e desbloqueio.
- **SolicitacaoMQListener**: Listener para consumir mensagens de uma fila JMS.
- **FintechRepository**: Repositório para operações de banco de dados relacionadas a fintechs.
- **GatewayRepository**: Repositório para integração com APIs externas de fintechs.
- **AuxDBRepository**: Repositório auxiliar para operações de controle de bloqueio de contas.
- **UtilSpag**: Classe utilitária com métodos estáticos para manipulação de datas e JSON.

### 3. Tecnologias Utilizadas
- Spring Boot
- Spring Data
- Spring JMS
- Swagger
- HikariCP
- Microsoft SQL Server
- IBM MQ
- Jackson
- Lombok

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST   | /monitoramento/bloquear | MonitoramentoAPI | Envia solicitação de bloqueio para fintechs. |
| POST   | /monitoramento/desBloquearIntraday | MonitoramentoAPI | Envia solicitação de desbloqueio intraday para fintechs. |
| POST   | /monitoramento/desBloquearPorValor | MonitoramentoAPI | Envia solicitação de desbloqueio por valor para fintechs. |
| POST   | /monitoramento/desBloqueioJuridico | MonitoramentoAPI | Envia solicitação de desbloqueio jurídico para fintechs. |
| POST   | /monitoramento/solicitacaoTransferenciaJuridico | MonitoramentoAPI | Envia solicitação de transferência jurídica para fintechs. |
| GET    | /monitoramento/{documento}/contasFintech | MonitoramentoAPI | Lista contas fintech vinculadas a um documento. |

### 5. Principais Regras de Negócio
- Validação de tempo mínimo entre processamentos de bloqueio.
- Verificação de bloqueio bem-sucedido antes de realizar desbloqueio intraday.
- Cálculo de valores bloqueados e desbloqueados.
- Integração com APIs externas para operações de bloqueio, desbloqueio e transferência.

### 6. Relação entre Entidades
- **ProcessoJuridico**: Representa um processo jurídico associado a bloqueios e desbloqueios.
- **SolicitacaoJuridico**: Representa uma solicitação jurídica de bloqueio ou desbloqueio.
- **ContaFintech**: Representa uma conta de fintech com informações de saldo e bloqueios.
- **DadosFintechDomain**: Contém informações de integração com fintechs, como endpoints e usuários.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbUsuarioContaFintech       | tabela | SELECT | Armazena informações de usuários de contas fintech. |
| TbProcessoJuridico          | tabela | SELECT | Armazena informações de processos jurídicos. |
| TbSolicitacaoJuridico       | tabela | SELECT | Armazena informações de solicitações jurídicas. |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbControleBloqueioConta     | tabela | UPDATE | Atualiza controle de bloqueio de contas. |
| TbProcessamentoMovimentoJuridico | tabela | INSERT | Insere registros de processamento de movimentos jurídicos. |

### 9. Filas Lidas
- QL.ATACADO.BLOQUEIO_VALORES_JUDICIAIS_OUT.INT

### 10. Filas Geradas
- QL.ATACADO.BLOQUEIO_VALORES_JUDICIAIS_IN.INT

### 11. Integrações Externas
- APIs de fintechs para operações de bloqueio, desbloqueio e transferência.
- ConfigCat para gerenciamento de feature toggles.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de desenvolvimento, como injeção de dependências e uso de annotations do Spring. No entanto, a complexidade de algumas classes pode ser reduzida para melhorar a legibilidade e manutenibilidade.

### 13. Observações Relevantes
- O sistema utiliza feature toggles para controlar o fluxo de autenticação mTls.
- Para executar localmente, é necessário configurar a variável de ambiente FT_KEY com a chave do projeto ConfigCat.