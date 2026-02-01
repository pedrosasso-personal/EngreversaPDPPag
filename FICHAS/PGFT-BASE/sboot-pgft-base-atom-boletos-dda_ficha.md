## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um serviço atômico desenvolvido para gerenciar boletos DDA (Débito Direto Autorizado) de clientes. Ele permite listar boletos, calcular encargos, aplicar descontos e realizar operações de baixa de forma operacional e efetiva. O serviço é construído utilizando o framework Spring Boot e integra-se com um banco de dados Sybase para operações de leitura e escrita.

### 2. Principais Classes e Responsabilidades
- **BoletoConfiguration**: Configura os beans de repositório e serviço para boletos DDA.
- **DatabaseConfiguration**: Configura o acesso ao banco de dados utilizando Jdbi.
- **OpenApiConfiguration**: Configura o Swagger para documentação de APIs.
- **BoletosDDAController**: Controlador REST que implementa a API para listar boletos DDA.
- **ConverteParaRepresentation**: Classe utilitária para converter entidades de domínio em representações para API.
- **BoletoRepositoryImpl**: Implementação do repositório para operações de banco de dados relacionadas a boletos DDA.
- **Application**: Classe principal para inicialização do aplicativo Spring Boot.
- **BaixaEfetivaRowMapper, BaixaOperacionalRowMapper, BoletoRowMapper, CalculoTituloRowMapper, DescontoRowMapper, EncargoRowMapper**: Mapeadores de linhas de resultado de consultas SQL para objetos de domínio.
- **Boleto, BaixaEfetiva, BaixaOperacional, CalculoTitulo, Desconto, Encargo**: Classes de domínio que representam entidades do sistema.
- **BoletoDDARequest**: Classe de domínio para encapsular parâmetros de requisição de boletos DDA.
- **TipoBoletosDDAEnum**: Enumeração para tipos de boletos DDA.
- **BoletoException**: Exceção específica para erros de domínio relacionados a boletos.
- **BoletoDDARepository**: Interface de repositório para operações de banco de dados.
- **BoletoDDAService**: Serviço que encapsula lógica de negócios para manipulação de boletos DDA.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- Jdbi
- Swagger
- Sybase JDBC Driver
- Maven

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST   | /v1/cliente/dda/boletos | BoletosDDAController | Lista os boletos DDA do cliente. |

### 5. Principais Regras de Negócio
- Listagem de boletos DDA com base em CPF/CNPJ e período de vencimento.
- Aplicação de descontos, juros e multas a boletos.
- Realização de baixa operacional e efetiva de boletos.
- Cálculo de valores totais a cobrar considerando encargos.

### 6. Relação entre Entidades
- **Boleto** possui relacionamentos com **CalculoTitulo**, **Desconto**, **Encargo**, **BaixaOperacional**, e **BaixaEfetiva**.
- **BoletoDDARequest** encapsula parâmetros de requisição para operações de listagem de boletos.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbTituloDDA | tabela | SELECT | Armazena informações sobre títulos DDA. |
| TbTituloDDABaixaEfetiva | tabela | SELECT | Armazena informações sobre baixas efetivas de títulos DDA. |
| TbTituloDDABaixaOperacional | tabela | SELECT | Armazena informações sobre baixas operacionais de títulos DDA. |
| TbCalculoTituloDDA | tabela | SELECT | Armazena cálculos de títulos DDA. |
| TbDescontoTituloDDA | tabela | SELECT | Armazena descontos aplicados a títulos DDA. |
| TbJuroTituloDDA | tabela | SELECT | Armazena juros aplicados a títulos DDA. |
| TbMultaTituloDDA | tabela | SELECT | Armazena multas aplicadas a títulos DDA. |

### 8. Estruturas de Banco de Dados Atualizadas
Não se aplica.

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- Integração com banco de dados Sybase para operações de leitura e escrita.
- Documentação de APIs via Swagger.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de programação, como injeção de dependências e uso de mapeadores para conversão de dados. A documentação via Swagger é um ponto positivo. No entanto, poderia haver mais comentários explicativos em algumas partes do código para melhorar a clareza.

### 13. Observações Relevantes
- O projeto utiliza o padrão de microserviços atômicos, o que facilita a manutenção e escalabilidade.
- A configuração do banco de dados é feita de forma dinâmica, permitindo fácil adaptação a diferentes ambientes (desenvolvimento, produção, etc.).