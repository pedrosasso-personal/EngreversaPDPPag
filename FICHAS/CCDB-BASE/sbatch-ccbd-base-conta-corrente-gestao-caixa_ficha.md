```markdown
## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é uma aplicação Spring Batch para processamento de dados de contas correntes. Ele realiza operações de leitura, escrita e atualização em tabelas temporárias e finais, utilizando múltiplas fontes de dados e integrações com APIs externas para obtenção de saldos de contas. O sistema é configurado para executar diferentes jobs e steps, que processam dados de clientes, fundos, veículos e variações de saldo.

### 2. Principais Classes e Responsabilidades
- **SpringBatchApplication**: Classe principal que inicia a aplicação Spring Batch.
- **JobBatch**: Configura jobs relacionados ao setup temporário e final.
- **JobContaGlobal**: Configura jobs para contas globais.
- **JobOrchestrator**: Orquestra a execução dos jobs com base nos parâmetros de entrada.
- **StepClearCCTempGlobal**: Step para limpar dados temporários globais.
- **StepContaFundoGlobal**: Step para processar contas de fundo globais.
- **StepContaVeiculoGlobal**: Step para processar contas de veículo globais.
- **StepUpdateTemporaryGlobal**: Step para atualizar dados temporários globais.
- **CCTempGlobalService**: Serviço para manipulação de dados temporários globais.
- **ContaFundoService**: Serviço para processamento de contas de fundo.
- **ContaVeiculoService**: Serviço para processamento de contas de veículo.
- **BalancesApiClient**: Cliente para integração com API de saldos.
- **SaldoApiClient**: Cliente para integração com API de consulta de saldo.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot 2+
- Spring Batch
- JDBI
- Sybase
- Maven 3.5.3+
- JUnit Jupiter 5+
- Lombok 1.18.20+

### 4. Principais Endpoints REST
Não se aplica.

### 5. Principais Regras de Negócio
- Processamento de saldos de contas correntes com base em diferentes tipos de contas (clientes, fundos, veículos).
- Atualização de registros temporários com base em consultas de saldo.
- Integração com APIs externas para obtenção de dados de saldo.
- Agrupamento e ordenação de registros para visualização sintética e analítica.

### 6. Relação entre Entidades
- **ContaGlobal**: Entidade que representa uma conta global com atributos como indicador, código de pessoa, apelido, CPF/CNPJ e código do banco.
- **CCTemp**: Entidade que representa dados temporários de contas correntes.
- **CCTotalClienteCredor**, **CCTotalFundo**, **CCTotalNome**: Entidades que representam totais de saldo para diferentes tipos de contas.
- **CCVariacao**: Entidade que representa variações de saldo.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo (tabela/view/coleção) | Operação (SELECT/READ) | Breve Descrição |
|-----------------------------|----------------------------|------------------------|-----------------|
| TbTempAgrupamentoContaCorrente | tabela | SELECT | Tabela temporária para agrupamento de dados de contas correntes. |
| TbConta | tabela | SELECT | Tabela de contas utilizada para obter saldos totais e de início de dia. |
| TbPessoaTitularidade | tabela | SELECT | Tabela de titularidade de pessoas. |
| TbContaRelacionamento | tabela | SELECT | Tabela de relacionamento de contas. |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo (tabela/view/coleção) | Operação (INSERT/UPDATE/DELETE) | Breve Descrição |
|-----------------------------|----------------------------|-------------------------------|-----------------|
| TbTempAgrupamentoContaCorrente | tabela | INSERT/UPDATE/DELETE | Tabela temporária para inserção e atualização de dados de contas correntes. |

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- **API de Saldos**: Integração para consulta de saldos de contas correntes.
- **API de Consulta de Saldo**: Integração para obtenção de saldos de contas de veículos.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e organizado, seguindo boas práticas de desenvolvimento com uso de Spring Batch e integração com APIs externas. A nomenclatura das classes e métodos é clara, facilitando a compreensão. No entanto, a complexidade das regras de negócio pode dificultar a manutenção em longo prazo.

### 13. Observações Relevantes
- O sistema utiliza múltiplas fontes de dados e integrações externas, o que pode aumentar a complexidade de configuração e operação.
- As consultas SQL são configuradas para otimização de performance, utilizando índices e agrupamentos específicos.
- A aplicação possui mecanismos de logging e monitoramento para facilitar o acompanhamento das operações de batch.
```