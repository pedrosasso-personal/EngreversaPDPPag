## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema "IntegrarPagamento" é um serviço atômico desenvolvido para integrar e gerenciar pagamentos na base de dados do sistema ITP. Ele utiliza o framework Spring Boot e é projetado para operar em ambientes de contêineres, utilizando Docker. O sistema oferece funcionalidades de cadastro, consulta e atualização de informações relacionadas a pagamentos, bancos, contas e transações, além de verificar circuit breaks e realizar conversões de TED.

### 2. Principais Classes e Responsabilidades
- **Application.java**: Classe principal que inicia a aplicação Spring Boot.
- **CadastroController**: Controlador responsável por operações de cadastro e consulta de dados de bancos, filiais, contas e transações.
- **CircuitBreakController**: Controlador que verifica se o circuit break está ativo.
- **LancamentoCaixaEntradaListener**: Listener para mensagens de cadastro de caixa de entrada via RabbitMQ.
- **CadastroGlobalService**: Serviço que gerencia operações de cadastro global, incluindo bancos e filiais.
- **ConversaoService**: Serviço responsável por realizar conversões de TED.
- **FeatureToggleService**: Serviço que gerencia feature toggles, incluindo circuit breaks.
- **JdbiBancoRepository**: Repositório para operações de banco utilizando JDBI.
- **TransacaoDomain**: Classe de domínio que representa uma transação.

### 3. Tecnologias Utilizadas
- Java 21
- Spring Boot
- JDBI
- RabbitMQ
- Redis
- Docker
- Prometheus
- Grafana
- Sybase

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET    | /cadastro/v1/protocolo | CadastroController | Consulta dados de um protocolo PGFT/ITP |
| PUT    | /cadastro/v1/atualiza-historico-documento | CadastroController | Atualiza histórico no PGFT |
| GET    | /circuit-break/ | CircuitBreakController | Consulta se circuit break está ativo |
| POST   | /parametrizacao/v1/conversao-ted | ParametrizacaoController | Parametrização para conversão de TED |

### 5. Principais Regras de Negócio
- Verificação de circuit break para transações com base em feature toggles.
- Conversão automática de TED entre diferentes tipos de liquidação (CIP e STR) com base em regras de valor e finalidade.
- Atualização de flags de migração e recebimento para bancos e contas.

### 6. Relação entre Entidades
- **BancoDomain**: Relacionado com entidades de transação e filial.
- **TransacaoDomain**: Relacionado com entidades de liquidação e conta.
- **FilialDomain**: Relacionado com entidades de banco e tesouraria.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| tb_ispb_ispb | tabela | SELECT | Consulta informações de bancos por código ISPB |
| TbParametroCamaraLiquidacao | tabela | SELECT | Consulta parâmetros de câmaras de liquidação |
| TbParametroInterfaceCIP | tabela | SELECT | Consulta configurações de integração com CIP |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbControleMigracaoSPAG | tabela | UPDATE | Atualiza flag de migração de clientes |
| TBL_PARAMETROS | tabela | UPDATE | Atualiza flags de recebimento SPBBV |

### 9. Filas Lidas
- events.business.SPAG-BASE.integrarPagamentoITP

### 10. Filas Geradas
- events.business.retornoPagamentoITP

### 11. Integrações Externas
- RabbitMQ para mensageria
- Redis para cache
- Prometheus para monitoramento
- Grafana para visualização de métricas

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de desenvolvimento, como injeção de dependências e uso de padrões de projeto. A documentação e os mapeamentos de entidades são claros, facilitando a manutenção. No entanto, a complexidade de algumas classes pode ser reduzida para melhorar a legibilidade.

### 13. Observações Relevantes
- O sistema utiliza feature toggles para gerenciar funcionalidades de forma dinâmica.
- A configuração de monitoramento e métricas é robusta, utilizando Prometheus e Grafana.
- A integração com RabbitMQ é essencial para o processamento de mensagens de pagamento.