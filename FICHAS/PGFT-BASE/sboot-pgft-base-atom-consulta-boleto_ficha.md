## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um serviço atômico de consulta de boletos, desenvolvido em Java utilizando o framework Spring Boot. Ele permite a consulta e manipulação de informações relacionadas a boletos, incluindo operações de inclusão, baixa, cálculo e validação de dados de boletos. O sistema também integra com RabbitMQ para consumo de mensagens relacionadas a boletos.

### 2. Principais Classes e Responsabilidades
- **ConsultaBoletoConfiguration**: Configuração de beans para o serviço de consulta de boletos.
- **JdbiConfiguration**: Configuração do Jdbi para acesso ao banco de dados.
- **OpenApiConfiguration**: Configuração do Swagger para documentação de APIs.
- **ConsultaBoletoRepositoryImpl**: Implementação do repositório para operações de banco de dados relacionadas a boletos.
- **EventListener**: Componente que consome mensagens de uma fila RabbitMQ e processa boletos.
- **TituloVoRowMapper**: Mapeador de linhas de resultados de consultas SQL para objetos TituloVO.
- **Application**: Classe principal para inicialização do aplicativo Spring Boot.
- **ConsultaBoletoService**: Serviço que contém lógica de negócio para manipulação de boletos.
- **PagamentoBoletoValidator**: Validador para dados de boletos.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- Maven
- Jdbi
- RabbitMQ
- Swagger
- Sybase

### 4. Principais Endpoints REST
Não se aplica.

### 5. Principais Regras de Negócio
- Validação de dados de boletos, como código de barras, valores e datas.
- Inclusão de informações de boletos no banco de dados.
- Cálculo de valores de juros, multas e descontos para boletos.
- Consumo de mensagens de fila RabbitMQ para processamento de boletos.

### 6. Relação entre Entidades
- **BoletoPagamentoCompleto**: Contém informações detalhadas sobre o pagamento de um boleto, incluindo listas de cálculos, descontos, juros e multas.
- **PessoaCompleta**: Representa uma pessoa completa com informações de endereço, telefone, patrimônio, ocupação, renda, faturamento e relacionamento.
- **TituloCipVO**: Representa um título de pagamento com informações detalhadas para processamento.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo (tabela/view/coleção) | Operação (SELECT/READ) | Breve Descrição |
|-----------------------------|----------------------------|------------------------|-----------------|
| TbSolicitacaoConsultaTitulo | tabela                     | SELECT                 | Consulta de título por código de barras |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo (tabela/view/coleção) | Operação (INSERT/UPDATE/DELETE) | Breve Descrição |
|-----------------------------|----------------------------|-------------------------------|-----------------|
| TbBaixaEfetivaTitulo        | tabela                     | INSERT                        | Inclusão de baixa efetiva de título |
| TbBaixaOperacionalTitulo    | tabela                     | INSERT                        | Inclusão de baixa operacional de título |
| TbRetornoConsultaTitulo     | tabela                     | INSERT                        | Inclusão de retorno de consulta de título |
| TbCalculoTitulo             | tabela                     | INSERT                        | Inclusão de cálculo de título |
| TbSolicitacaoConsultaTitulo | tabela                     | INSERT                        | Inclusão de código de barras de título |
| TbDescontoBoleto            | tabela                     | INSERT                        | Inclusão de desconto de boleto |
| TbJuroBoleto                | tabela                     | INSERT                        | Inclusão de juros de boleto |
| TbMultaBoleto               | tabela                     | INSERT                        | Inclusão de multa de boleto |

### 9. Filas Lidas
- **events.business.PGFT-BASE.inserirBoletoPagamentoCompleto**: Fila RabbitMQ de onde o sistema consome mensagens para processamento de boletos.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- **RabbitMQ**: Integração para consumo de mensagens relacionadas a boletos.
- **Swagger**: Integração para documentação de APIs REST.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de desenvolvimento, como injeção de dependências e uso de padrões de projeto. A documentação e os testes são adequados, mas há espaço para melhorias na clareza dos comentários e na organização de algumas classes.

### 13. Observações Relevantes
- O sistema utiliza o banco de dados Sybase para armazenamento de informações de boletos.
- A configuração do sistema é feita através de arquivos YAML e XML, permitindo flexibilidade para diferentes ambientes.
- O sistema possui integração com Prometheus e Grafana para monitoramento de métricas.