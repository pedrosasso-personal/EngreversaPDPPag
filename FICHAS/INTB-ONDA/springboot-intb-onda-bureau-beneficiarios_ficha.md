## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema "springboot-intb-onda-bureau-beneficiarios" é uma aplicação Java desenvolvida com o framework Spring Boot. Seu objetivo é fornecer um serviço REST para consulta de sócios de empresas, integrando-se com serviços externos de crédito e bureau para obter informações detalhadas sobre os sócios.

### 2. Principais Classes e Responsabilidades
- **HelloService**: Serviço que retorna uma mensagem de saudação.
- **ObterSociosService**: Serviço responsável por consultar e obter informações sobre sócios de empresas.
- **DocketConfiguration**: Configuração do Swagger para documentação de APIs.
- **WebServiceTemplateConfiguration**: Configuração de templates para chamadas a serviços web.
- **ConsultaSocios**: Classe de domínio que representa uma consulta de sócios.
- **DetalhesSocio**: Classe de domínio que representa os detalhes de um sócio.
- **BusinessException**: Classe de exceção para erros de negócio.
- **DetalhesSocioRowMapper**: Mapper para mapear resultados de consultas SQL para objetos DetalhesSocio.
- **BureauCreditoRepository**: Repositório para integração com o serviço de crédito bureau.
- **SocioRepository**: Repositório para consulta de sócios no banco de dados.
- **ListaSocioRepresentation**: Representação de uma lista de sócios.
- **ObterSociosRequestRepresentation**: Representação de uma requisição para obter sócios.
- **ObterSociosResponseRepresentation**: Representação de uma resposta com informações de sócios.
- **SocioRepresentation**: Representação de um sócio.
- **HelloApi**: API REST para expor um serviço de saudação.
- **ObterSociosApi**: API REST para obter informações de sócios.
- **Sanitizador**: Utilitário para sanitização de entradas.
- **StringUtils**: Utilitário para manipulação de strings.
- **ValidaCNPJ**: Utilitário para validação de CNPJ.
- **Server**: Classe principal para inicialização da aplicação Spring Boot.

### 3. Tecnologias Utilizadas
- Spring Boot
- Swagger
- Sybase JDBC
- Apache Commons
- JUnit
- Mockito
- Docker
- Prometheus
- Grafana

### 4. Principais Endpoints REST
| Método | Endpoint       | Classe Controladora | Descrição                              |
|--------|----------------|---------------------|----------------------------------------|
| GET    | /hello         | HelloApi            | Retorna uma mensagem de saudação.      |
| POST   | /obterSocios   | ObterSociosApi      | Obtém informações sobre sócios.        |

### 5. Principais Regras de Negócio
- Limite de consultas a sócios definido por configuração.
- Validação de CNPJ antes de realizar consultas.
- Integração com serviços externos para obtenção de informações de crédito e restrições.

### 6. Relação entre Entidades
- **ConsultaSocios** possui uma coleção de **DetalhesSocio**.
- **DetalhesSocio** contém informações detalhadas sobre cada sócio, como CNPJ, nome, participação, etc.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbSerasaPjCTSocietarioDetalhe | tabela | SELECT | Detalhes de sócios consultados. |

### 8. Estruturas de Banco de Dados Atualizadas
Não se aplica.

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- Serviço de crédito bureau para consulta de restrições e informações de sócios.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de desenvolvimento, como injeção de dependências e separação de responsabilidades. A documentação via Swagger é um ponto positivo. Poderia melhorar em aspectos de tratamento de exceções e cobertura de testes.

### 13. Observações Relevantes
- O sistema utiliza Docker para containerização e Prometheus/Grafana para monitoramento.
- A configuração de segurança inclui autenticação básica e integração com LDAP.