## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema "Serviço Atômico de DebitoIssExc" é um microserviço desenvolvido para gerenciar exceções de débito de ISS. Ele utiliza o framework Spring Boot e é configurado para operar com RabbitMQ para mensageria e SQL Server como banco de dados. O serviço expõe endpoints REST e utiliza Swagger para documentação de APIs.

### 2. Principais Classes e Responsabilidades
- **Application**: Classe principal que inicia a aplicação Spring Boot.
- **DataBaseConfiguration**: Configurações de banco de dados, incluindo Jdbi para interações com SQL.
- **DebitoIssExcConfiguration**: Configurações específicas do serviço, incluindo RabbitMQ e repositórios.
- **OpenApiConfiguration**: Configuração do Swagger para documentação de APIs.
- **CCBDRepositoryImpl**: Implementação do repositório para operações de banco de dados.
- **DebitoIssExcListener**: Componente que escuta mensagens de RabbitMQ e processa exceções de débito.
- **DebitoIssExc**: Classe de domínio que representa a entidade de exceção de débito.
- **DebitoIssExcService**: Interface de serviço para operações de exceção de débito.
- **DebitoIssExcServiceImpl**: Implementação do serviço para manipulação de exceções de débito.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- Maven
- Jdbi
- RabbitMQ
- SQL Server
- Swagger
- Prometheus
- Grafana

### 4. Principais Endpoints REST
Não se aplica.

### 5. Principais Regras de Negócio
- Inserção de exceções de débito no banco de dados.
- Processamento de mensagens de exceção de débito recebidas via RabbitMQ.

### 6. Relação entre Entidades
- **DebitoIssExc**: Entidade principal que contém informações sobre exceções de débito, como código do banco, número da conta corrente, tipo de conta, protocolo, data de lançamento, valor da operação e descrição da exceção.

### 7. Estruturas de Banco de Dados Lidas
Não se aplica.

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo (tabela/view/coleção) | Operação (INSERT/UPDATE/DELETE) | Breve Descrição |
|-----------------------------|----------------------------|-------------------------------|-----------------|
| TbLoteErro                  | tabela                     | INSERT                        | Armazena exceções de débito de ISS. |

### 9. Filas Lidas
- **events.business.CCBD-BASE.trataErroDebitoIss**: Fila RabbitMQ de onde o sistema consome mensagens de exceção de débito.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- **RabbitMQ**: Utilizado para mensageria.
- **SQL Server**: Banco de dados para armazenamento de exceções de débito.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de desenvolvimento, como injeção de dependências e uso de interfaces para serviços. A documentação via Swagger e a configuração de monitoramento com Prometheus e Grafana são pontos positivos. No entanto, a ausência de endpoints REST documentados pode ser uma limitação para integração com outros sistemas.

### 13. Observações Relevantes
- O sistema utiliza Docker para facilitar a execução de serviços como RabbitMQ e Prometheus.
- A configuração de segurança e autenticação do Grafana está desabilitada por padrão, o que pode ser um ponto de atenção para ambientes de produção.
- O projeto possui testes automatizados, incluindo testes funcionais, de integração e unitários, o que contribui para a robustez do sistema.