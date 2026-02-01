## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema "Serviço Atômico de LancamentoGestaoCaixa" é um microserviço desenvolvido em Java utilizando o framework Spring Boot. Ele é responsável por gerenciar lançamentos financeiros, oferecendo funcionalidades para obter lançamentos sintéticos e analíticos de entrada e saída. O serviço expõe endpoints REST para interagir com os dados de lançamentos, utilizando um banco de dados SQL Server.

### 2. Principais Classes e Responsabilidades
- **LancamentoGestaoCaixaConfiguration**: Configurações de beans para Jdbi e serviços relacionados aos lançamentos.
- **OpenApiConfiguration**: Configurações para documentação de API usando Swagger.
- **JdbiLancamentoGestaoCaixaRepository**: Implementação do repositório de lançamentos utilizando Jdbi.
- **LancamentosAnaliticoSpagMapper**: Mapeamento de entidades analíticas para representações.
- **LancamentosSinteticoSpagMapper**: Mapeamento de entidades sintéticas para representações.
- **LancamentoGestaoCaixaController**: Controlador REST que expõe endpoints para obter lançamentos.
- **Application**: Classe principal para inicialização do Spring Boot.
- **LancamentosAnaliticoSpag**: Entidade de domínio para lançamentos analíticos.
- **LancamentosSinteticoSpag**: Entidade de domínio para lançamentos sintéticos.
- **LancamentoGestaoCaixaException**: Exceção de domínio para erros relacionados a lançamentos.
- **LancamentoGestaoCaixaRepository**: Interface de repositório para operações de lançamentos.
- **LancamentoGestaoCaixaService**: Serviço de domínio que realiza operações de negócio sobre lançamentos.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- Jdbi
- Swagger
- SQL Server
- Maven

### 4. Principais Endpoints REST
| Método | Endpoint                          | Classe Controladora                  | Descrição                                      |
|--------|-----------------------------------|--------------------------------------|------------------------------------------------|
| GET    | /v1/lancamento-gestao-caixa/getLancamentosSinteticoSpag | LancamentoGestaoCaixaController | Retorna lançamentos sintéticos SPAG            |
| GET    | /v1/lancamento-gestao-caixa/getLancamentosEntradaSpag  | LancamentoGestaoCaixaController | Retorna lançamentos analíticos de entrada SPAG |
| GET    | /v1/lancamento-gestao-caixa/getLancamentosSaidaSpag    | LancamentoGestaoCaixaController | Retorna lançamentos analíticos de saída SPAG   |

### 5. Principais Regras de Negócio
- Filtrar lançamentos por data de movimento.
- Diferenciar lançamentos de entrada e saída.
- Aplicar regras de negócio específicas para cálculo de valores de lançamentos.

### 6. Relação entre Entidades
- **LancamentosAnaliticoSpag** e **LancamentosSinteticoSpag** são entidades de domínio que representam diferentes tipos de lançamentos financeiros.
- **LancamentoGestaoCaixaRepository** atua como interface para operações de persistência dessas entidades.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo     | Operação | Breve Descrição                     |
|-----------------------------|----------|----------|-------------------------------------|
| TbLancamento                | tabela   | SELECT   | Armazena dados de lançamentos       |
| TbLancamentoPessoa          | tabela   | SELECT   | Armazena dados de pessoas relacionadas aos lançamentos |

### 8. Estruturas de Banco de Dados Atualizadas
Não se aplica.

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- Integração com API Gateway para autenticação via OAuth2.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado, utilizando boas práticas de desenvolvimento como injeção de dependências e separação de responsabilidades. A documentação via Swagger facilita a compreensão dos endpoints. No entanto, poderia haver mais comentários explicativos em algumas partes do código para melhorar a clareza.

### 13. Observações Relevantes
- O sistema utiliza o padrão de projeto de microserviços atômicos, o que facilita a escalabilidade e manutenção.
- A configuração de segurança está habilitada, garantindo que apenas endpoints públicos sejam acessíveis sem autenticação.