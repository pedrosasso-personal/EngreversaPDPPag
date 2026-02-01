## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um serviço atômico de MovimentoPagamento, desenvolvido em Java utilizando o framework Spring Boot. Ele é responsável por gerenciar informações de pagamentos e correspondências TED, integrando-se com um banco de dados Sybase para realizar consultas e operações relacionadas a movimentações financeiras.

### 2. Principais Classes e Responsabilidades
- **Application**: Classe principal que inicia a aplicação Spring Boot.
- **MovimentoPagamentoController**: Controlador responsável por expor endpoints para consulta de informações de pagamentos e correspondências TED.
- **MovimentoPagamentoService**: Serviço que contém a lógica de negócio para manipulação de dados de MovimentoPagamento.
- **CorrespondenciaTedService**: Serviço que contém a lógica de negócio para manipulação de dados de CorrespondenciaTed.
- **MovimentoPagamentoRepositoryImpl**: Implementação do repositório que realiza consultas SQL para obter dados de MovimentoPagamento.
- **CorrespondenciaTedRepositoryImpl**: Implementação do repositório que realiza consultas SQL para obter dados de CorrespondenciaTed.
- **MovimentoPagamento**: Classe de domínio que representa uma movimentação de pagamento.
- **CorrespondenciaTed**: Classe de domínio que representa uma correspondência TED.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- JDBI
- Swagger
- Sybase
- Maven
- Docker

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET    | /v1/consulta-pgft-pagamento | MovimentoPagamentoController | Retorna informações de pagamentos no PGFT por período. |
| GET    | /v1/correspondencia-ted | MovimentoPagamentoController | Retorna informações de correspondências TED. |

### 5. Principais Regras de Negócio
- Validação de parâmetros de entrada para consultas de correspondências TED.
- Conversão de formatos de data para consultas SQL.
- Tratamento de exceções específicas de negócio para correspondências TED.

### 6. Relação entre Entidades
- **MovimentoPagamento**: Relaciona-se com dados de origem e liquidação de pagamentos.
- **CorrespondenciaTed**: Relaciona-se com dados de favorecido e remetente em transações TED.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TBL_LANCAMENTO              | tabela | SELECT   | Armazena dados de lançamentos financeiros. |
| TBL_SIST_ORIGEM_SPB         | tabela | SELECT   | Armazena dados de origem de sistemas SPB. |
| TBL_LIQUIDACAO_SPB          | tabela | SELECT   | Armazena dados de liquidação de sistemas SPB. |

### 8. Estruturas de Banco de Dados Atualizadas
Não se aplica.

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- Banco de dados Sybase para consultas de dados de pagamentos e correspondências TED.
- Swagger para documentação de APIs.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado, utilizando boas práticas de desenvolvimento como injeção de dependências e separação de responsabilidades. A utilização de testes unitários e de integração é um ponto positivo. No entanto, a documentação poderia ser mais detalhada em algumas partes para facilitar o entendimento de novos desenvolvedores.

### 13. Observações Relevantes
- O sistema utiliza o padrão de projeto de microserviços atômicos, facilitando a escalabilidade e manutenção.
- A configuração de segurança OAuth2 está presente, garantindo a proteção dos endpoints expostos.
- O uso de Dockerfile indica que o sistema pode ser facilmente containerizado para implantação em ambientes de nuvem.