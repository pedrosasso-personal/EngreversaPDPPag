## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um serviço REST que atua como um Backend For Frontend (BFF) para cálculo de boletos. Ele utiliza o framework Spring Boot e possui uma estrutura básica para componentes BFF, incluindo diretórios, arquivos de configuração, Dockerfile e dependências comuns. O sistema realiza consultas na CIP para obter informações sobre boletos e calcula valores como juros, multas e descontos.

### 2. Principais Classes e Responsabilidades
- **BoletoCalculadoFacade**: Responsável por consultar e calcular boletos, integrando diferentes serviços e helpers para realizar cálculos de juros, multas e descontos.
- **BoletoPagamentoHelper**: Auxilia na verificação de tipos de cálculo e na obtenção de valores de descontos e cobranças.
- **CalculoDescontoHelper**: Realiza cálculos de desconto para boletos.
- **CalculoJurosHelper**: Realiza cálculos de juros para boletos.
- **CalculoMultaHelper**: Realiza cálculos de multa para boletos.
- **CalendarioBancoService**: Fornece serviços relacionados a datas, como listar dias úteis e não úteis, e calcular dias corridos e úteis.
- **ConsultaCipRepository**: Realiza consultas na CIP para obter informações sobre boletos.
- **FeriadoRepository**: Consulta serviços externos para listar feriados e obter o próximo dia útil.
- **BoletoCalculadoApi**: Exposição de endpoints REST para consulta de boletos calculados.
- **Application**: Classe principal que inicia a aplicação Spring Boot.

### 3. Tecnologias Utilizadas
- Spring Boot
- Swagger
- Lombok
- Jackson
- Maven

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST   | /v1/atacado/pagamentos/consultaBoletoCalculado | BoletoCalculadoApi | Realiza a consulta de boletos calculados na CIP |

### 5. Principais Regras de Negócio
- Cálculo de juros, multas e descontos para boletos vencidos ou não.
- Verificação de tipos de cálculo para determinar como os valores devem ser calculados.
- Determinação de dias úteis e não úteis para cálculos de datas.
- Integração com a CIP para obter informações detalhadas sobre boletos.

### 6. Relação entre Entidades
- **BoletoCalculado**: Entidade principal que contém informações sobre o boleto, como valores, datas e indicadores.
- **PessoaBeneficiarioOriginal**, **PessoaBeneficiarioFinal**, **PessoaPagador**, **SacadorAvalista**: Entidades relacionadas aos participantes do boleto.
- **CalculoTitulo**, **Titulo**: Entidades que representam cálculos e títulos associados ao boleto.

### 7. Estruturas de Banco de Dados Lidas
Não se aplica.

### 8. Estruturas de Banco de Dados Atualizadas
Não se aplica.

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- **CIP**: Serviço externo para consulta de boletos.
- **Serviço de Feriados**: Serviço externo para listar feriados e obter o próximo dia útil.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de programação, como a injeção de dependências e o uso de interfaces para estratégias de cálculo. A documentação e os comentários são adequados, facilitando a compreensão do fluxo de negócios. No entanto, poderia haver uma maior modularização em algumas partes para melhorar a manutenibilidade.

### 13. Observações Relevantes
- O sistema utiliza o padrão BFF para facilitar a integração com diferentes interfaces de usuário.
- A configuração do Swagger permite uma documentação clara dos endpoints disponíveis.
- O uso de Lombok reduz a verbosidade do código, facilitando a leitura e manutenção.