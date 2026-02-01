## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um microserviço atômico responsável por gerenciar os pagamentos de rebate. Ele utiliza o framework Spring Boot e JDBI para acesso ao banco de dados, permitindo operações de CRUD e consulta de relatórios sobre pagamentos de rebate.

### 2. Principais Classes e Responsabilidades
- **Application**: Classe principal que inicia a aplicação Spring Boot.
- **PagamentoRebateController**: Controlador responsável por expor endpoints para operações de pagamento de rebate.
- **PagamentoRebateService**: Serviço que contém a lógica de negócio para manipulação de pagamentos de rebate.
- **JdbiPagamentoRebateRepository**: Repositório que utiliza JDBI para realizar operações no banco de dados relacionadas a pagamentos de rebate.
- **PagamentoRebate**: Classe de domínio que representa um pagamento de rebate.
- **PagamentoRebateMapper**: Classe responsável por mapear objetos de domínio para representações de resposta e vice-versa.
- **RestResponseEntityExceptionHandler**: Classe que trata exceções globais na aplicação.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- JDBI
- Swagger
- Prometheus
- Grafana
- Docker

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET    | /pagamentos | PagamentoRebateController | Busca pagamento por filtro de duplicidade. |
| GET    | /pagamentos/relatorio | PagamentoRebateController | Busca pagamentos por data de apuração. |
| GET    | /pagamentos/extrato | PagamentoRebateController | Busca pagamentos cadastrados hoje. |
| GET    | /pagamentos/processamento | PagamentoRebateController | Busca pagamentos por data de pagamento. |
| POST   | /pagamentos | PagamentoRebateController | Salva um novo pagamento de rebate. |
| PATCH  | /pagamentos/{idPagamento}/statusProcessamentoExtrato | PagamentoRebateController | Altera o status de processamento do extrato. |
| PATCH  | /pagamentos/{idPagamento}/statusPagamento | PagamentoRebateController | Altera o status do pagamento. |
| PATCH  | /pagamentos/{idPagamento}/codigoProtocolo | PagamentoRebateController | Altera o código de protocolo do pagamento. |

### 5. Principais Regras de Negócio
- Verificação de duplicidade de pagamento antes de salvar um novo pagamento.
- Alteração de status de pagamento e status de processamento de extrato.
- Geração de relatórios de pagamentos por data de apuração.

### 6. Relação entre Entidades
- **PagamentoRebate**: Entidade principal que contém informações sobre o pagamento, como valores, datas, status, e cliente.
- **FiltroDuplicidade**: Utilizado para verificar duplicidade de pagamentos.
- **FiltroAprovacao**: Utilizado para buscar pagamentos por critérios de aprovação.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbPagamentoRebate | tabela | SELECT | Armazena informações sobre pagamentos de rebate. |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbPagamentoRebate | tabela | INSERT, UPDATE | Armazena e atualiza informações sobre pagamentos de rebate. |

### 9. Filas Lidas
não se aplica

### 10. Filas Geradas
não se aplica

### 11. Integrações Externas
- **Swagger**: Para documentação de APIs.
- **Prometheus e Grafana**: Para monitoramento e métricas.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de programação, como injeção de dependências e tratamento de exceções. A documentação está presente e os testes são abrangentes. Poderia melhorar em termos de simplificação de algumas lógicas e maior cobertura de testes.

### 13. Observações Relevantes
O sistema utiliza Docker para facilitar a implantação e execução em diferentes ambientes. Além disso, possui integração com ferramentas de monitoramento como Prometheus e Grafana para métricas customizadas.