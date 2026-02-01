```markdown
## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um serviço de cálculo de boletos, desenvolvido como um microserviço atômico utilizando Java com Spring Boot. Ele expõe endpoints para calcular valores de boletos, incluindo multas, juros e descontos, e fornece informações detalhadas sobre o estado dos boletos.

### 2. Principais Classes e Responsabilidades
- **ModelMapperConfiguration**: Configura o ModelMapper para mapeamento de objetos.
- **BoletoException**: Exceção específica para erros relacionados a boletos.
- **BusinessException**: Exceção genérica para erros de negócio.
- **BaixaEfetiva**: Representa a baixa efetiva de um título.
- **BaixaTitulo**: Representa a baixa de um título com detalhes de processamento.
- **BoletoCalculado**: Contém informações detalhadas sobre o cálculo de um boleto.
- **BoletoRequest**: Representa uma solicitação de cálculo de boleto.
- **CalculoTitulo**: Contém detalhes sobre cálculos de títulos, como descontos e juros.
- **PessoaBeneficiarioFinal**: Representa o beneficiário final de um boleto.
- **PessoaBeneficiarioOriginal**: Representa o beneficiário original de um boleto.
- **PessoaPagador**: Representa o pagador de um boleto.
- **SacadorAvalista**: Representa o sacador avalista de um boleto.
- **Titulo**: Representa um título com informações de valor e data.
- **BoletoMapper**: Interface para mapeamento de objetos relacionados a boletos.
- **BoletoRepository**: Interface de repositório para operações com boletos.
- **BoletoApiDelegateImpl**: Implementação dos endpoints da API de boletos.
- **BoletoService**: Serviço responsável pelo cálculo de boletos.
- **BoletoCalculoUtil**: Utilitário para cálculos relacionados a boletos.
- **JsonUtil**: Utilitário para manipulação de JSON.
- **MultaUtil**: Utilitário para cálculo de multas.
- **SaldoUtil**: Utilitário para cálculo de saldo devedor.
- **ValorUtil**: Utilitário para manipulação de valores monetários.
- **Application**: Classe principal para inicialização da aplicação.

### 3. Tecnologias Utilizadas
- Java 11+
- Spring Boot
- Maven
- ModelMapper
- Gson

### 4. Principais Endpoints REST
| Método | Endpoint                  | Classe Controladora       | Descrição                                      |
|--------|---------------------------|---------------------------|------------------------------------------------|
| POST   | /boleto/v1/calculo        | BoletoApiDelegateImpl     | Calcula valores de boletos e retorna informações detalhadas. |

### 5. Principais Regras de Negócio
- Cálculo de multas, juros e descontos para boletos vencidos ou não.
- Determinação de valores máximos e mínimos de pagamento.
- Identificação de boletos parciais, divergentes e residuais.
- Verificação de última parcela e autorização de recebimento de valores divergentes.

### 6. Relação entre Entidades
- **BoletoCalculado** possui relações com várias entidades, como **PessoaBeneficiarioOriginal**, **PessoaPagador**, **SacadorAvalista**, e listas de **BaixaEfetiva**, **BaixaTitulo**, **Titulo**, e **CalculoTitulo**.

### 7. Estruturas de Banco de Dados Lidas
Não se aplica.

### 8. Estruturas de Banco de Dados Atualizadas
Não se aplica.

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- Integração com serviços de autenticação via JWT.
- Exposição de APIs através do Swagger.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de desenvolvimento, como injeção de dependências e uso de utilitários para cálculos complexos. A documentação está presente, mas poderia ser mais detalhada em algumas áreas para facilitar a manutenção e compreensão do sistema.

### 13. Observações Relevantes
- O sistema utiliza um perfil de configuração local para desenvolvimento, permitindo o uso de um banco de dados em memória (H2) para testes.
- A documentação do Swagger facilita a interação com os endpoints expostos.
```