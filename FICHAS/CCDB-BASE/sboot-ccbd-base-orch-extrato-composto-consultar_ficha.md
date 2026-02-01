## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um microserviço desenvolvido utilizando o modelo de microserviços Atômicos, com o objetivo de consultar extratos compostos de contas bancárias. Ele utiliza o framework Spring Boot e está configurado para funcionar em ambientes de desenvolvimento, homologação e produção. O serviço expõe endpoints REST para realizar consultas de transações bancárias, integrando-se com APIs externas para autenticação e autorização.

### 2. Principais Classes e Responsabilidades
- **Application.java**: Classe principal que inicializa a aplicação Spring Boot.
- **AuthProperties.java**: Configurações de autenticação, incluindo clientId, clientSecret e gatewayUrl.
- **ExtratoCompostoConsultarConfiguration.java**: Configuração de beans, incluindo RestTemplate e ObjectMapper.
- **OpenApiConfiguration.java**: Configuração do OpenAPI para documentação da API.
- **RouteProperties.java**: Configurações de rota para a API de extrato composto.
- **ExtratoRequest.java**: DTO para requisições de consulta de extrato.
- **ErrosExtrato.java**: Enumeração de erros específicos do serviço de extrato.
- **ExtratoCompostoHandler.java**: Tratamento de exceções relacionadas ao serviço de extrato.
- **ExtratoException.java**: Exceção personalizada para erros de extrato.
- **ExtratoCompostoMapper.java**: Interface de mapeamento de objetos de apresentação.
- **ExtratoApiDelegateImpl.java**: Implementação dos endpoints REST para consulta de extrato.
- **ExtratoServiceImpl.java**: Implementação do serviço de consulta de extrato.
- **ExtratoService.java**: Interface do serviço de consulta de extrato.

### 3. Tecnologias Utilizadas
- Spring Boot
- Maven
- Java 11
- Swagger/OpenAPI
- MapStruct
- Spring Security
- Apache Camel

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET    | /v1/extrato | ExtratoApiDelegateImpl | Consulta de transações bancárias com parâmetros de pesquisa. |

### 5. Principais Regras de Negócio
- Validação de parâmetros de consulta de extrato.
- Autenticação e autorização via OAuth2.
- Tratamento de exceções específicas para erros de consulta de extrato.

### 6. Relação entre Entidades
Não se aplica.

### 7. Estruturas de Banco de Dados Lidas
Não se aplica.

### 8. Estruturas de Banco de Dados Atualizadas
Não se aplica.

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- API Gateway para autenticação OAuth2.
- Serviço de consulta de extrato composto via API externa.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de desenvolvimento, como injeção de dependências e tratamento de exceções. A documentação via Swagger/OpenAPI está presente, facilitando a compreensão dos endpoints disponíveis. No entanto, poderia haver mais comentários explicativos em algumas partes do código para melhorar a legibilidade e manutenção.

### 13. Observações Relevantes
- O projeto utiliza um Dockerfile para empacotamento e execução em ambientes de contêiner.
- A configuração de segurança e rotas é feita através de arquivos YAML, permitindo fácil adaptação para diferentes ambientes.
- A documentação do projeto está incompleta no README.md, necessitando de uma descrição mais detalhada do funcionamento e objetivos do sistema.