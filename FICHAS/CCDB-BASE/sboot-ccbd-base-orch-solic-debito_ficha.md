## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um microserviço corporativo orquestrador responsável por solicitar débito e bloquear saldo de conta corrente. Ele expõe endpoints para realizar operações de débito em contas correntes, integrando-se com serviços externos para consultar informações de contas e motivos de bloqueio, além de gerenciar monitoramentos de saldo.

### 2. Principais Classes e Responsabilidades
- **Application**: Classe principal que inicia a aplicação Spring Boot.
- **SolicDebitoController**: Controlador responsável por expor os endpoints REST para solicitar débito e débito disponível.
- **SolicDebitoService**: Serviço que orquestra as chamadas de débito utilizando o Camel.
- **AppProperties**: Classe de configuração que carrega propriedades do sistema.
- **SolicDebitoConfiguration**: Configuração do Camel e beans necessários para o funcionamento do sistema.
- **CamelContextWrapper**: Wrapper para o contexto do Camel, gerenciando rotas e templates de produtor/consumidor.
- **SolicDebitoRouter**: Define as rotas do Camel para o fluxo de orquestração de débito.
- **SolicDebitoDiponivelRouter**: Define as rotas do Camel para o fluxo de orquestração de débito disponível.
- **AtualizaMonitoramentoRepositoryImpl**: Implementação do repositório para atualizar monitoramentos de saldo.
- **ConsultaContaRepositoryImpl**: Implementação do repositório para consultar informações de conta.
- **ConsultaMotivoBloqueioRepositoryImpl**: Implementação do repositório para consultar motivos de bloqueio.
- **SolicDebitoRepositoryImpl**: Implementação do repositório para solicitar débito.
- **SolicDebitoStandInRepositoryImpl**: Implementação do repositório para solicitar débito em stand-in.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- Apache Camel
- Swagger
- Maven
- Docker

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST   | /v1/banco-digital/contas/debito | SolicDebitoController | Solicita débito em conta corrente. |
| POST   | /v1/banco-digital/contas/debito-valor-disponivel | SolicDebitoController | Solicita débito disponível em conta corrente. |

### 5. Principais Regras de Negócio
- Validação de código de banco e motivo de bloqueio.
- Verificação de transações pendentes em stand-in.
- Atualização de monitoramento de saldo após operações de débito.
- Bloqueio de saldo baseado em condições específicas (valor solicitado, protocolo, etc.).

### 6. Relação entre Entidades
- **SolicDebito**: Representa uma solicitação de débito, incluindo informações de conta e operação.
- **SolicDebitoProcesso**: Extende SolicDebito, adicionando informações sobre o processo de débito.
- **SolicDebitoDiponivelProcesso**: Extende SolicDebitoProcesso, adicionando informações sobre monitoramento de saldo e motivo de bloqueio.
- **MonitoramentoSaldo**: Representa o monitoramento de saldo de uma conta.
- **MotivoBloqueio**: Representa o motivo pelo qual um saldo pode ser bloqueado.

### 7. Estruturas de Banco de Dados Lidas
Não se aplica.

### 8. Estruturas de Banco de Dados Atualizadas
Não se aplica.

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- Serviço Atom Bloqueio Saldo: Utilizado para gerenciar bloqueios de saldo.
- Serviço Atom Conta Corrente: Utilizado para consultar informações de conta corrente.
- Serviço Atom Conta Corrente StandIn: Utilizado para verificar transações pendentes em stand-in.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de programação, como injeção de dependências e uso de padrões de projeto. A documentação e os testes são adequados, mas poderiam ser mais detalhados em alguns pontos para melhorar a manutenibilidade.

### 13. Observações Relevantes
- O sistema utiliza o Apache Camel para orquestrar as chamadas de serviço, o que facilita a integração e o processamento de mensagens.
- A configuração do Swagger permite a documentação e teste dos endpoints expostos.
- O uso de Docker facilita a implantação e execução do serviço em ambientes diversos.