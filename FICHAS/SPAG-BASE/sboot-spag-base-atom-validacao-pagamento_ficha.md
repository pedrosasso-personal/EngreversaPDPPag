## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema "Serviço Atômico de ValidacaoPagamento" é um microserviço desenvolvido para validar solicitações de pagamento, realizar operações de baixa de boletos e registrar transferências. Ele utiliza o framework Spring Boot e está configurado para operar em um ambiente de contêineres Docker. O sistema expõe endpoints REST para interagir com o serviço de validação de pagamentos e manipulação de boletos.

### 2. Principais Classes e Responsabilidades
- **Application**: Classe principal que inicia o aplicativo Spring Boot.
- **OpenApiConfiguration**: Configurações do Swagger para documentação de APIs.
- **ValidacaoPagamentoConfiguration**: Configuração de beans e integração com o Jdbi para acesso ao banco de dados.
- **ValidacaoPagamentoExceptionHandler**: Manipulador de exceções para o serviço de validação de pagamentos.
- **JdbiLancamentoRepository**: Interface para operações de banco de dados relacionadas a lançamentos.
- **JdbiValidacaoPagamentoRepository**: Interface para operações de banco de dados relacionadas à validação de pagamentos.
- **BoletoCompletoInfoController**: Controlador para operações de informações completas de boletos.
- **LancamentoController**: Controlador para operações de lançamentos.
- **ValidacaoPagamentoController**: Controlador para operações de validação de pagamentos.
- **BoletoCompletoInfoServiceImpl**: Implementação do serviço para obter informações completas de boletos.
- **LancamentoServiceImpl**: Implementação do serviço para operações de lançamentos.
- **ValidacaoPagamentoServiceImpl**: Implementação do serviço para validação de pagamentos.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- Jdbi
- Swagger
- Prometheus
- Grafana
- Docker

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST   | /validacao-pagamento | ValidacaoPagamentoController | Valida solicitação de pagamento. |
| GET    | /lancamento/{codigoLancamento}/baixa-boleto-cip | LancamentoController | Consulta a situação de um boleto junto à CIP. |
| POST   | /boleto-completo-info | BoletoCompletoInfoController | Gera informações para baixa de um boleto junto à CIP. |
| PUT    | /lancamento/{codLancamento}/baixa-boleto-cip | LancamentoController | Atualiza o indicador de baixa de um boleto junto à CIP. |
| PUT    | /lancamento/{codigoLancamento}/numero-protocolo | LancamentoController | Relaciona o lançamento à caixa de entrada SPB. |
| PUT    | /lancamento/{codigoLancamento}/codigo-lancamento-pgft | LancamentoController | Relaciona o lançamento ao lançamento (PGFT). |
| GET    | /lancamento/{codigoLancamento}/dados-registro-boleto | LancamentoController | Retorna dados para registro de boleto. |
| POST   | /lancamento/{codigoLancamento}/registro-transferencia | LancamentoController | Registra uma transferência (TED) de um boleto STR26. |

### 5. Principais Regras de Negócio
- Validação de solicitações de pagamento com base em horários de grade e dias úteis.
- Atualização de status de lançamentos e códigos de clientes.
- Registro de transferências de boletos com validações de dados de movimento e identificação de transações.

### 6. Relação entre Entidades
- **Lancamento**: Entidade principal que representa um lançamento financeiro.
- **Boleto**: Entidade que representa um boleto bancário.
- **Cliente**: Entidade que representa um cliente, incluindo informações de conta.
- **Portador**: Entidade que representa o portador de um boleto.
- **DadosTransferencia**: Entidade que encapsula informações necessárias para registrar uma transferência.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbLancamento                | tabela | SELECT  | Armazena informações de lançamentos financeiros. |
| TbLancamentoPessoa          | tabela | SELECT  | Armazena informações de pessoas relacionadas a lançamentos. |
| TbLancamentoClienteFintech  | tabela | SELECT  | Armazena informações de clientes fintech relacionados a lançamentos. |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbLancamento                | tabela | UPDATE  | Atualiza informações de lançamentos financeiros. |

### 9. Filas Lidas
não se aplica

### 10. Filas Geradas
não se aplica

### 11. Integrações Externas
- **OAuth2**: Integração para autenticação e autorização de APIs.
- **Prometheus**: Integração para monitoramento de métricas.
- **Grafana**: Integração para visualização de métricas.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e organizado, seguindo boas práticas de desenvolvimento com uso de padrões de projeto e integração de tecnologias modernas. A documentação e os testes estão presentes, mas poderiam ser mais abrangentes para cobrir todos os casos de uso.

### 13. Observações Relevantes
- O sistema utiliza o Swagger para documentação de APIs, facilitando a integração e uso dos serviços expostos.
- A configuração do Docker e do Prometheus/Grafana indica um foco em ambientes de contêineres e monitoramento contínuo.