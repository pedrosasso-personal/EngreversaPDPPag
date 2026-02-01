## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é responsável por validar e processar pagamentos de boletos, integrando-se com a CIP (Câmara Interbancária de Pagamentos) para verificar a validade dos boletos e valores de pagamento. Ele utiliza diversas regras de negócio para calcular multas, juros e descontos, além de verificar datas úteis para processamento.

### 2. Principais Classes e Responsabilidades
- **CalculoBoletoBusinessImpl**: Implementa a lógica de negócio para cálculo de multas, juros e descontos de boletos.
- **CalculoBoletoService**: Interface que define os métodos para cálculo de valores relacionados a boletos.
- **CalculoND2**: Enum que define estratégias de cálculo de juros com base em diferentes parâmetros.
- **CalculoND2Param**: Classe que encapsula os parâmetros necessários para o cálculo de juros.
- **StrategyND2**: Interface que define o método de cálculo de juros.
- **ValidaRetornoCipRemote**: Interface para validação de retorno de boletos da CIP.
- **ValidaValoresCipRemote**: Interface para validação de valores de boletos da CIP.
- **ValidaRetornoCipFacade**: Implementa a lógica de validação de retorno de boletos da CIP.
- **ValidaValoresCipFacade**: Implementa a lógica de validação de valores de boletos da CIP.
- **BoletoPagamentoHelper**: Classe auxiliar para operações relacionadas a boletos.
- **CalculoDescontoHelper**: Classe auxiliar para cálculo de descontos em boletos.
- **CalculoJurosHelper**: Classe auxiliar para cálculo de juros em boletos.
- **CalculoMultaHelper**: Classe auxiliar para cálculo de multas em boletos.
- **FeriadoDAO**: Interface para operações de consulta de feriados.
- **FeriadoDAOImpl**: Implementação da interface FeriadoDAO, utilizando JDBC para interagir com o banco de dados.
- **FeriadoRowMapper**: Mapeia resultados de consultas SQL para objetos FeriadoDTO.
- **SPAGVerificaDiaUtilProcedure**: Procedimento armazenado para verificar se uma data é útil.
- **SPAGVerificaProximoDiaUtilProcedure**: Procedimento armazenado para calcular o próximo dia útil.
- **DtSpagCalcPagUtil**: Utilitário para manipulação de datas.
- **ValorUtil**: Utilitário para manipulação de valores monetários.
- **RestExceptionMapper**: Mapeador de exceções para endpoints REST.
- **BaseAppConfig**: Configuração base para APIs REST.
- **SecurityAppConfig**: Configuração de segurança para APIs REST.
- **UtilsAppConfig**: Configuração de utilidades para APIs REST.
- **ValidaProcessamentoApi**: API REST para validação de boletos e valores de pagamento.

### 3. Tecnologias Utilizadas
- Java
- Maven
- EJB
- JAX-RS
- Spring JDBC
- Apache Commons Lang
- SLF4J
- Swagger
- WebSphere Application Server

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST   | /atacado/pagamentos/boletos/validarBoleto/ | ValidaProcessamentoApi | Valida dados de boletos com a CIP. |
| POST   | /atacado/pagamentos/valores/validarValorPagamento/ | ValidaProcessamentoApi | Valida valores de pagamento de boletos com a CIP. |

### 5. Principais Regras de Negócio
- Validação de data limite para pagamento de boletos.
- Cálculo de multas, juros e descontos para boletos vencidos.
- Verificação de beneficiário e situação de boletos na CIP.
- Aceitação de boletos não vencidos em contingência da CIP.
- Pagamento integral ou parcial de boletos com base em regras específicas.

### 6. Relação entre Entidades
- **FeriadoDTO**: Representa um feriado, utilizado para cálculos de dias úteis.
- **DicionarioPagamento**: Contém informações sobre o pagamento de boletos, utilizado em diversas validações e cálculos.
- **CalculoTituloDTO**: Utilizado para cálculos de valores de títulos de pagamento.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbFeriado                   | tabela | SELECT   | Armazena feriados utilizados para cálculo de dias úteis. |

### 8. Estruturas de Banco de Dados Atualizadas
Não se aplica.

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- Integração com a CIP para validação de boletos e valores de pagamento.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código está bem estruturado, com separação clara de responsabilidades entre classes e interfaces. Utiliza boas práticas de programação, como injeção de dependências e uso de interfaces para definir contratos. No entanto, poderia ser melhorado com mais comentários explicativos e documentação detalhada para facilitar a manutenção.

### 13. Observações Relevantes
- O sistema utiliza procedimentos armazenados para cálculos de dias úteis, o que pode ser uma dependência crítica do banco de dados.
- A configuração de segurança e utilidades REST é feita através de classes dedicadas, facilitando a gestão de APIs.