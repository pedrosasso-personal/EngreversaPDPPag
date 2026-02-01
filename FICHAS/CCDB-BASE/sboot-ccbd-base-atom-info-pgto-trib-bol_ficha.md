## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um microserviço corporativo atômico responsável por gerenciar informações de pagamento de tributos e boletos. Ele permite consultar e salvar informações de pagamento, além de validar horários de pagamento e consultar segunda via de boletos.

### 2. Principais Classes e Responsabilidades
- **Application**: Classe principal que inicia o aplicativo Spring Boot.
- **InfoPgtoTribBolController**: Controlador REST que gerencia endpoints para operações de consulta e gravação de boletos.
- **InfoPgtoTribBolService**: Interface que define os métodos de serviço para operações de boletos.
- **InfoPgtoTribBolServiceImpl**: Implementação da interface de serviço, contendo lógica de negócios para manipulação de boletos.
- **InfoPgtoTribBolRepository**: Interface de repositório que define operações de banco de dados relacionadas a boletos.
- **BoletoAdapter**: Classe que transforma representações de boletos em objetos de domínio e vice-versa.
- **TbBoleto, TbDetalheBoleto, TbDetalheBoletoPgmCartao**: Classes de domínio que representam entidades de boletos e seus detalhes.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- Maven
- Jdbi
- Swagger
- Lombok
- Microsoft SQL Server

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET    | /v1/corporativo/pagamentos/boleto-info | InfoPgtoTribBolController | Consulta informações de pagamento de boleto. |
| POST   | /v1/corporativo/pagamentos/boleto-info | InfoPgtoTribBolController | Grava informações de pagamento de boleto. |
| GET    | /v1/corporativo/pagamentos/segunda-via | InfoPgtoTribBolController | Consulta segunda via de boleto. |
| GET    | /v1/corporativo/pagamentos/segunda-via-agendamento | InfoPgtoTribBolController | Consulta segunda via de agendamento de boleto. |
| GET    | /v1/corporativo/pagamentos/boleto-info/validar-horario | InfoPgtoTribBolController | Valida horários de pagamento de boleto. |

### 5. Principais Regras de Negócio
- Gravação de boletos e seus detalhes no banco de dados.
- Consulta de boletos por código de barras, linha digitável, NSU, protocolo, e código de autorização de pagamento.
- Validação de pagamentos duplicados em um intervalo de 48 horas.

### 6. Relação entre Entidades
- **TbBoleto**: Relacionado a **TbDetalheBoleto** por `cdDetalheBoleto`.
- **TbDetalheBoleto**: Contém informações detalhadas do boleto.
- **TbDetalheBoletoPgmCartao**: Extensão de **TbDetalheBoleto** com informações adicionais para pagamentos com cartão.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbBoleto                    | tabela | SELECT | Armazena informações básicas de boletos. |
| TbDetalheBoleto             | tabela | SELECT | Armazena detalhes de boletos. |
| TbTransacaoBoleto           | tabela | SELECT | Armazena transações de boletos. |
| TbLancamentoBoleto          | tabela | SELECT | Armazena lançamentos de boletos. |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbBoleto                    | tabela | INSERT/UPDATE | Armazena informações básicas de boletos. |
| TbDetalheBoleto             | tabela | INSERT | Armazena detalhes de boletos. |
| TbTransacaoBoleto           | tabela | INSERT | Armazena transações de boletos. |

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- Integração com Microsoft SQL Server para operações de banco de dados.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado, utilizando boas práticas de programação como injeção de dependências e separação de responsabilidades. A documentação via Swagger é clara, e o uso de Lombok reduz a verbosidade. No entanto, poderia haver mais comentários explicativos em partes complexas do código.

### 13. Observações Relevantes
- O sistema utiliza configuração de segurança OAuth2 para proteger os endpoints.
- O projeto é configurado para diferentes ambientes (local, des, qa, uat, prd) através do arquivo `application.yml`.
- A documentação do serviço está disponível via Swagger UI.