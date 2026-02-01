```markdown
## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um orquestrador de boletos utilizando Apache Camel e Spring Boot. Ele realiza cálculos de boletos, consulta informações de boletos via API, valida documentos de parceiros e integra com serviços externos para obter dados de calendário e segurança.

### 2. Principais Classes e Responsabilidades
- **ProcessorCalculoBoleto**: Processa o cálculo de boletos.
- **ProcessorCalculoBoletoVencido**: Verifica se o boleto está vencido.
- **RequestConsultaBoletoCIPProcessor**: Processa requisições de consulta de boletos CIP.
- **ResponseConsultaBoletoCipProcessor**: Processa respostas de consulta de boletos CIP.
- **ThrowExceptionProcessor**: Lida com exceções durante o processamento.
- **BoletoRouter**: Define rotas de processamento de boletos.
- **RouterProperties**: Configura propriedades de roteamento.
- **BoletoConfiguration**: Configura beans e integrações com APIs externas.
- **CalcularBoletoException**: Exceção personalizada para erros de cálculo de boletos.
- **CustomException**: Exceção personalizada genérica.
- **ValidarDataReferenciaException**: Exceção para erros de validação de data de referência.
- **ValidarParceiroException**: Exceção para erros de validação de parceiro.
- **BoletoCalculado**: Representa um boleto calculado com suas propriedades.
- **BoletoParametroRoute**: Parâmetros para roteamento de boletos.
- **CalculoTitulo**: Representa cálculos relacionados a títulos.
- **PessoaBeneficiarioFinal**: Representa o beneficiário final de um boleto.
- **PessoaBeneficiarioOriginal**: Representa o beneficiário original de um boleto.
- **PessoaPagador**: Representa o pagador de um boleto.
- **SacadorAvalista**: Representa o sacador avalista de um boleto.
- **Titulo**: Representa um título financeiro.
- **FaultDto**: DTO para falhas.
- **FaultResponseDto**: DTO para respostas de falhas.
- **BoletoCalculadoMapper**: Mapeia representações de boletos calculados.
- **BoletoCipApiRepositoryImpl**: Implementação de repositório para consulta de boletos CIP.
- **CalcularBoletoRepositoryApiImpl**: Implementação de repositório para cálculo de boletos.
- **CalendarioApiRepositoryImpl**: Implementação de repositório para consulta de calendário.
- **SegurancaApiRepositoryImpl**: Implementação de repositório para validação de documentos de parceiros.
- **BoletoCipApiRepository**: Interface de repositório para consulta de boletos CIP.
- **CalcularBoletoRepositoryApi**: Interface de repositório para cálculo de boletos.
- **CalendarioApiRepository**: Interface de repositório para consulta de calendário.
- **SegurancaApiRepository**: Interface de repositório para validação de documentos de parceiros.
- **Isento**: Estratégia de cálculo de juros isento.
- **PercentualAnoDiasCorridos**: Estratégia de cálculo de juros por percentual anual em dias corridos.
- **PercentualAnoDiaUtil**: Estratégia de cálculo de juros por percentual anual em dias úteis.
- **PercentualDiasCorridos**: Estratégia de cálculo de juros por percentual em dias corridos.
- **PercentualDiaUtil**: Estratégia de cálculo de juros por percentual em dias úteis.
- **PercentualMesDiasCorridos**: Estratégia de cálculo de juros por percentual mensal em dias corridos.
- **PercentualMesDiaUtil**: Estratégia de cálculo de juros por percentual mensal em dias úteis.
- **ValorDiasCorridos**: Estratégia de cálculo de juros por valor em dias corridos.
- **ValorDiaUtil**: Estratégia de cálculo de juros por valor em dias úteis.
- **ValorPadrao**: Estratégia padrão de cálculo de juros.
- **CalculoND2Param**: Parâmetros para cálculo de juros.
- **CalculoND2Service**: Serviço para cálculo de juros ND2.
- **StrategyND2**: Interface para estratégias de cálculo de juros ND2.
- **BoletoCalculadoServiceImpl**: Implementação de serviço para cálculos de boletos.
- **CalculoDescontoServiceImpl**: Implementação de serviço para cálculo de descontos.
- **CalculoJurosServiceImpl**: Implementação de serviço para cálculo de juros.
- **CalendarioBancoServiceImpl**: Implementação de serviço para cálculos de calendário bancário.
- **BoletoCalculadoService**: Interface de serviço para cálculos de boletos.
- **CalculoDescontoService**: Interface de serviço para cálculo de descontos.
- **CalculoJurosService**: Interface de serviço para cálculo de juros.
- **CalendarioBancoService**: Interface de serviço para cálculos de calendário bancário.
- **JsonUtil**: Utilitário para manipulação de JSON.
- **LocalDateUtils**: Utilitário para manipulação de datas.
- **LogUtil**: Utilitário para sanitização de logs.
- **Application**: Classe principal para inicialização da aplicação.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- Apache Camel
- Maven
- JWT (Java JWT)
- ModelMapper
- Tomcat Embed
- Spring Security
- Easy Random
- Woodstox

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /atacado/pagamentos/consultaBoletoCalculado | BoletoRouter | Consulta e calcula boletos. |
| GET | /v1/boleto/{numeroCodigoBarras} | ConsultaBoletoCipApi | Consulta boleto por número de código de barras. |
| POST | /v1/seguranca/validar | ValidarDocumentoParceiroApi | Valida o documento do parceiro. |
| GET | /v1/calendar/useful-day | CalendarioApi | Verifica se é dia útil. |
| GET | /v1/calendar/calculate-expiration | CalendarioApi | Calcula prazo de dias úteis. |

### 5. Principais Regras de Negócio
- Cálculo de juros e descontos em boletos baseado em diferentes estratégias.
- Validação de documentos de parceiros antes de processar boletos.
- Consulta de boletos via CIP e atualização de informações.
- Integração com serviços de calendário para determinar dias úteis.

### 6. Relação entre Entidades
- **BoletoCalculado** possui várias listas de entidades como **BaixaEfetiva**, **BaixaTitulo**, **CalculoTitulo**, **Titulo**.
- **PessoaBeneficiarioOriginal**, **PessoaBeneficiarioFinal**, **PessoaPagador**, **SacadorAvalista** são entidades relacionadas a **BoletoCalculado**.

### 7. Estruturas de Banco de Dados Lidas
Não se aplica.

### 8. Estruturas de Banco de Dados Atualizadas
Não se aplica.

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- **CalendarioApi**: Serviço para consulta de dias úteis.
- **ConsultaBoletoCipApi**: Serviço para consulta de boletos CIP.
- **ValidarDocumentoParceiroApi**: Serviço para validação de documentos de parceiros.
- **BoletoCalculoApi**: Serviço para cálculo de boletos.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de programação, como injeção de dependências e separação de responsabilidades. No entanto, poderia haver uma documentação mais detalhada em algumas partes do código para facilitar o entendimento.

### 13. Observações Relevantes
- O projeto utiliza o modelo de microserviços atômicos.
- A configuração de segurança é feita através de JWT.
- O sistema possui testes unitários para validar suas funcionalidades principais.

---
```