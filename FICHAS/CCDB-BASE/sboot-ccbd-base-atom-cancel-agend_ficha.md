## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um serviço atômico de cancelamento de agendamentos futuros no Banco Votorantim. Ele permite cancelar lançamentos futuros de contas correntes e boletos, utilizando informações como número de conta, NSU e consentimento.

### 2. Principais Classes e Responsabilidades
- **CancelAgendConfiguration**: Configura os beans para os repositórios e serviços de cancelamento de agendamentos.
- **DatabaseConfiguration**: Configura as fontes de dados e Jdbi para interação com o banco de dados.
- **OpenApiConfiguration**: Configura o Swagger para documentação das APIs REST.
- **CancelAgendController**: Controlador que expõe os endpoints para cancelamento de agendamentos.
- **ValidarDadosBoletoRowMapper**: Mapeia os resultados de consultas SQL para objetos CancelAgendBoleto.
- **ValidarDadosRowMapper**: Mapeia os resultados de consultas SQL para objetos CancelAgend.
- **CancelAgendBoletoRepositoryImpl**: Implementação do repositório para operações de cancelamento de agendamentos de boletos.
- **CancelAgendRepositoryImpl**: Implementação do repositório para operações de cancelamento de agendamentos de contas correntes.
- **LoggerHelper**: Utilitário para sanitização de mensagens de log.
- **Application**: Classe principal para inicialização do Spring Boot.
- **CancelAgend**: Entidade de domínio para agendamentos de contas correntes.
- **CancelAgendBoleto**: Entidade de domínio para agendamentos de boletos.
- **CancelAgendException**: Exceção de domínio para erros de cancelamento.
- **DadosInvalidosException**: Exceção para dados inválidos fornecidos.
- **CancelAgendBoletoService**: Serviço para operações de cancelamento de agendamentos de boletos.
- **CancelAgendService**: Serviço para operações de cancelamento de agendamentos de contas correntes.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot 2+
- Maven 3.5.3
- JUnit Jupiter 5+
- Lombok 1.18.10
- Swagger
- Jdbi
- Sybase JDBC
- Microsoft SQL Server JDBC

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST   | /v1/agendamentos-movimentacao/cancelar | CancelAgendController | Cancela lançamentos futuros de contas correntes. |
| POST   | /v1/agendamentos-movimentacao/cancelar-por-consentimento | CancelAgendController | Cancela lançamentos futuros de boletos por consentimento. |

### 5. Principais Regras de Negócio
- Cancelamento de agendamentos futuros de contas correntes e boletos.
- Validação de dados de agendamento antes do cancelamento.
- Exceção lançada para dados inválidos fornecidos.

### 6. Relação entre Entidades
- **CancelAgend**: Relaciona-se com agendamentos de contas correntes.
- **CancelAgendBoleto**: Extende CancelAgend para incluir consentimento em agendamentos de boletos.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbAgendamento | tabela | SELECT | Armazena agendamentos de contas correntes e boletos. |
| VwContaCorrenteSaldoDia | view | SELECT | Visualiza saldo diário de contas correntes. |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbAgendamento | tabela | UPDATE | Atualiza status de agendamentos para cancelado. |
| TbAgendamentoContaCorrente | tabela | UPDATE | Atualiza status de agendamentos de contas correntes. |

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- OAuth2 para autenticação e autorização.
- Swagger para documentação de APIs.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código está bem estruturado, com uso adequado de padrões de projeto e boas práticas de desenvolvimento. A documentação via Swagger e o uso de exceções específicas para tratamento de erros são pontos positivos. Poderia melhorar em termos de comentários e documentação interna.

### 13. Observações Relevantes
O projeto segue o modelo de microserviços atômicos, com uma arquitetura bem definida e uso de tecnologias modernas para desenvolvimento de serviços web. A configuração de segurança e integração com OAuth2 é um diferencial importante para garantir a proteção dos endpoints.