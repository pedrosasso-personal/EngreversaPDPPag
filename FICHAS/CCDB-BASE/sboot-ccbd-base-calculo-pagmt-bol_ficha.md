## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um microserviço desenvolvido em Java utilizando o framework Spring Boot. Ele é responsável por realizar cálculos relacionados ao pagamento de boletos, incluindo descontos, juros, multas e validação de dados do boleto para pagamento.

### 2. Principais Classes e Responsabilidades
- **CalcularDescontosServiceImpl**: Implementa a lógica de cálculo de descontos para boletos.
- **CalcularJurosServiceImpl**: Implementa a lógica de cálculo de juros para boletos.
- **CalcularMultaServiceImpl**: Implementa a lógica de cálculo de multas para boletos.
- **CalcularTotalServiceImpl**: Implementa a lógica de cálculo do valor total do boleto, considerando baixas operacionais e efetivas.
- **CalcularPagmtBoletoController**: Controlador REST que expõe endpoints para validação de boletos.
- **CalcularPagmtBoletoServiceImpl**: Serviço que coordena o cálculo de pagamento de boletos, integrando os cálculos de descontos, juros, multas e total.
- **AppProperties**: Classe de configuração que carrega propriedades do aplicativo.
- **OpenApiConfiguration**: Configuração do Swagger para documentação de APIs.
- **CalculatorUtil**: Utilitário para operações comuns de cálculo.
- **DataUtil**: Utilitário para manipulação de datas.
- **HorarioUtil**: Utilitário para obter a data atual.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- Swagger
- Lombok
- Logback
- Maven

### 4. Principais Endpoints REST
| Método | Endpoint                             | Classe Controladora              | Descrição                                      |
|--------|--------------------------------------|----------------------------------|------------------------------------------------|
| POST   | /v1/pagamento-boleto/validar         | CalcularPagmtBoletoController    | Valida os dados do boleto para pagamento.      |

### 5. Principais Regras de Negócio
- Cálculo de descontos, juros e multas baseado em diferentes modelos de cálculo.
- Validação de datas de vencimento e transferência para determinar se o boleto está vencido ou inválido.
- Verificação de duplicidade de pagamento de boletos.
- Determinação de possibilidade de alteração de valor do pagamento baseado em regras de autorização.

### 6. Relação entre Entidades
- **BoletoCalcular**: Contém informações necessárias para calcular o pagamento de um boleto.
- **BoletoCalculado**: Representa o resultado do cálculo de um boleto, incluindo valores de desconto, juros, multa e saldo atual.
- **BaixaEfetiva** e **BaixaOperacional**: Representam informações de baixas relacionadas ao boleto.
- **CalculoTitulo**: Contém valores de juros, multa, desconto e total a cobrar para um título específico.
- **Titulo**: Representa um título financeiro com código, data, valor e percentual.

### 7. Estruturas de Banco de Dados Lidas
Não se aplica.

### 8. Estruturas de Banco de Dados Atualizadas
Não se aplica.

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- Integração com serviços externos para obter dias úteis e não úteis através de REST APIs configuradas nas propriedades do aplicativo.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de programação, como injeção de dependências e uso de utilitários para operações comuns. A documentação via Swagger facilita a compreensão dos endpoints disponíveis. Poderia haver melhorias na organização dos pacotes e na documentação interna para aumentar ainda mais a clareza.

### 13. Observações Relevantes
- O sistema utiliza OAuth2 para autenticação e segurança dos endpoints.
- A configuração do Swagger está habilitada apenas para ambientes não produtivos.
- O projeto está configurado para ser executado em um ambiente de contêiner Docker.