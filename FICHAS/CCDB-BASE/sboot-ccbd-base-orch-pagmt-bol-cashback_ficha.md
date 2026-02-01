## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um serviço de orquestração para o resgate de cashback, desenvolvido em Java utilizando o framework Spring Boot. Ele integra-se com RabbitMQ e Apache Camel para gerenciar fluxos de pagamento e estorno de boletos e transferências bancárias, atualizando saldos de cashback e status de protocolos de pagamento.

### 2. Principais Classes e Responsabilidades
- **OpenApiConfiguration**: Configurações para a documentação da API usando Swagger.
- **PagmtBolCashbackConfiguration**: Configurações gerais do sistema, incluindo integração com Camel e serviços REST.
- **RabbitMQConfiguration**: Configurações para conexão com RabbitMQ.
- **AtualizaSaldoCashbackRepositoryImpl**: Implementação para atualizar saldo de cashback.
- **AtualizaStatusBoletoRepositoryImpl**: Implementação para atualizar status de boletos.
- **AtualizaStatusProtocoloPagmtoRepositoryImpl**: Implementação para atualizar status de protocolos de pagamento.
- **AtualizaStatusTransfRepositoryImpl**: Implementação para atualizar status de transferências.
- **BuscarSaldoRepositoryImpl**: Implementação para buscar saldo de cashback.
- **ConsultaAdesaoClienteCashbackRepositoryImpl**: Implementação para consultar adesão de clientes ao cashback.
- **EfetuarPagmtoBolRepositoryImpl**: Implementação para efetuar pagamento de boletos.
- **IdentificaOperacaoProtocoloRepositoryImpl**: Implementação para identificar operações de protocolo.
- **RecuperaDadosBoletoRepositoryImpl**: Implementação para recuperar dados de boletos.
- **RecuperaDadosPagamentoDetalhadoRepositoryImpl**: Implementação para recuperar dados detalhados de pagamento.
- **TransferenciaBancariaRepositoryImpl**: Implementação para realizar transferências bancárias.
- **EventListener**: Escuta eventos de RabbitMQ para processar pagamentos e estornos.
- **RabbitMQFilas**: Define constantes para filas e exchanges do RabbitMQ.
- **PagmtBolCashbackService**: Serviço principal para efetuar pagamentos e estornos de cashback.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- Apache Camel
- RabbitMQ
- Swagger
- Resilience4j
- Maven

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST   | /pagamento/cashback | PagmtBolCashbackRouter | Efetua pagamento com saldo de cashback |
| POST   | /processa/boleto | PagmtBolCashbackRouter | Processa pagamento de boleto |
| POST   | /processa/boleto/estorno | PagmtBolCashbackRouter | Processa estorno de boleto |

### 5. Principais Regras de Negócio
- Atualização de saldo de cashback após pagamento ou estorno.
- Identificação de operações de protocolo para determinar tipo de fluxo (pagamento ou estorno).
- Verificação de adesão do cliente ao programa de cashback antes de efetuar operações.
- Gerenciamento de status de protocolos de pagamento e transferências.

### 6. Relação entre Entidades
- **TransferenciaMensagem**: Contém informações sobre a transferência, como protocolo e status.
- **EfetuarPagmtoBolRequest**: Detalhes do pagamento de boleto, incluindo remetente e favorecido.
- **Protocolo**: Representa o protocolo de operação, incluindo status e erros.
- **ContaRequest**: Detalhes da conta bancária para operações de transferência.

### 7. Estruturas de Banco de Dados Lidas
Não se aplica.

### 8. Estruturas de Banco de Dados Atualizadas
Não se aplica.

### 9. Filas Lidas
- `events.business.CCBD-BASE.retornoPagmtoCabkSucesso`
- `events.business.CCBD-BASE.retornoPagmtoCabkErro`

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- APIs para atualização de saldo e status de cashback.
- APIs para consulta de adesão ao cashback.
- APIs para recuperação de dados de pagamento detalhado.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de programação, como injeção de dependência e uso de padrões de projeto. A documentação está presente, e o uso de tecnologias como Resilience4j para resiliência é um ponto positivo. No entanto, a complexidade do sistema pode ser reduzida em algumas áreas para melhorar a manutenibilidade.

### 13. Observações Relevantes
- O sistema utiliza o padrão de projeto Builder para construir objetos de requisição e resposta.
- A configuração do RabbitMQ é feita através de arquivos de configuração externos, facilitando a gestão em diferentes ambientes.
- O sistema possui integração com Prometheus e Grafana para monitoramento de métricas.