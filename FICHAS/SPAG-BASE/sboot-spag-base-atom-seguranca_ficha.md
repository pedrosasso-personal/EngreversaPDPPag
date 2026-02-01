---
## Ficha Técnica do Sistema


### 1. Descrição Geral
O sistema **sboot-spag-base-atom-seguranca** é um serviço atômico de segurança desenvolvido em Spring Boot, responsável por validar e gerenciar informações de clientes/parceiros no contexto de pagamentos. Ele realiza autenticação baseada em JWT (OAuth2), valida credenciais de clientes através de CPF/CNPJ e códigos de origem, e fornece endpoints REST para consulta e validação de dados de clientes cadastrados na base de dados SPAG (Sistema de Pagamentos).


---
### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal que inicializa a aplicação Spring Boot com suporte a OAuth2 Resource Server |
| **SegurancaController** | Controlador REST que expõe endpoints para validação de clientes e consulta por api-key-parceiro |
| **SegurancaService** | Serviço de domínio que implementa as regras de negócio de validação de clientes e extração de clientId |
| **ClienteRepositoryImpl** | Implementação do repositório de acesso a dados de clientes usando JDBI |
| **SegurancaRepositoryImpl** | Implementação do repositório para extração de clientId do token JWT |
| **JdbiConfiguration** | Configuração do JDBI para acesso ao banco de dados SQL Server |
| **SegurancaConfiguration** | Configuração de beans do domínio de segurança |
| **OpenApiConfiguration** | Configuração do Swagger/OpenAPI para documentação da API |
| **Cliente** | Entidade de domínio representando um cliente/parceiro |
| **ClienteDTO** | DTO para transferência de dados de cliente |
| **SegurancaException** | Exceção customizada para erros de segurança |
| **ExceptionReasonEnum** | Enumeração de códigos e mensagens de erro |


---
### 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Spring Security OAuth2** (autenticação e autorização JWT)
- **JDBI 3.9.1** (acesso a banco de dados)
- **SQL Server** (banco de dados)
- **Swagger/Springfox 3.0.0** (documentação de API)
- **Lombok** (redução de boilerplate)
- **Micrometer/Prometheus** (métricas e monitoramento)
- **Grafana** (visualização de métricas)
- **Logback** (logging)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **JUnit 5 + Mockito** (testes unitários)
- **RestAssured** (testes funcionais)
- **Pact** (testes de contrato)


---
### 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/seguranca/validar | SegurancaController | Valida se um cliente (CPF/CNPJ + código origem) está autorizado com base no token JWT ou api-key-parceiro |
| GET | /v1/seguranca | SegurancaController | Obtém dados de um cliente através do header api-key-parceiro |


---
### 5. Principais Regras de Negócio

1. **Validação de Cliente**: Verifica se o CPF/CNPJ e código de origem fornecidos correspondem a um cliente ativo na base de dados e se o clientId extraído do token JWT ou fornecido via header corresponde ao indicador de interface do cliente cadastrado.

2. **Extração de ClientId do JWT**: Decodifica o payload do token JWT Bearer e extrai o campo "aud" (audience) que representa o clientId do parceiro.

3. **Consulta por API Key**: Permite consultar dados de cliente utilizando o header "api-key-parceiro" como identificador.

4. **Filtro de Clientes Ativos**: Apenas clientes com flag ativo (FlAtivo = 'S') e tipo de integração externa (TpIntegracao = 'E' ou null) são considerados válidos.

5. **Tratamento de Exceções**: Retorna códigos HTTP apropriados (401 Unauthorized, 404 Not Found, 204 No Content, 500 Internal Server Error) conforme o tipo de erro encontrado.


---
### 6. Relação entre Entidades

**Cliente**
- Atributos: cdParametroPagamentoFintech (Integer), dsIndicadorInterfaceCliente (String), nuCpfCnpj (String)
- Representa um parceiro/cliente cadastrado no sistema de pagamentos

**ClienteDTO**
- Atributos: cnpj (String), codigoOrigem (Integer)
- DTO utilizado para receber dados de entrada nas requisições

**Seguranca**
- Atributos: id (String), version (Integer)
- Entidade de domínio base (aparentemente não utilizada diretamente no fluxo principal)

Não há relacionamentos complexos entre entidades. O sistema trabalha principalmente com a entidade Cliente de forma isolada.


---
### 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbParametroPagamentoFintech | tabela | SELECT | Tabela que armazena parâmetros de clientes/parceiros do sistema de pagamentos fintech, incluindo CPF/CNPJ, código de identificação, indicador de interface e flags de ativação |


---
### 8. Estruturas de Banco de Dados Atualizadas

não se aplica


---
### 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot (resources) | Arquivo de configuração da aplicação com profiles (local, des, qa, uat, prd), datasources, security e actuator |
| logback-spring.xml | leitura | Logback (resources) | Configuração de logging em formato JSON para console |
| obterCliente.sql | leitura | ClienteRepositoryImpl | Query SQL para buscar cliente por CPF/CNPJ e código de origem |
| obterClienteCpfCnpj.sql | leitura | ClienteRepositoryImpl | Query SQL para buscar cliente apenas por CPF/CNPJ |
| obterClienteClientId.sql | leitura | ClienteRepositoryImpl | Query SQL para buscar cliente por indicador de interface (clientId) |


---
### 10. Filas Lidas

não se aplica


---
### 11. Filas Geradas

não se aplica


---
### 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| API Gateway OAuth2 | Integração | Validação de tokens JWT através do endpoint jwks.json (URLs variam por ambiente: des, uat, prd) |
| Banco de Dados DBSPAG (SQL Server) | Integração | Acesso à base de dados de parâmetros de pagamento fintech |
| Prometheus | Integração | Exportação de métricas da aplicação via endpoint /actuator/prometheus |
| Grafana | Integração | Visualização de métricas coletadas pelo Prometheus |


---
### 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (presentation, domain, infrastructure)
- Uso adequado de padrões como Repository, Service e DTO
- Configuração clara de profiles para diferentes ambientes
- Testes unitários presentes com boa cobertura
- Uso de Lombok para reduzir boilerplate
- Documentação via Swagger configurada
- Tratamento de exceções customizado
- Uso de JDBI com queries SQL externalizadas

**Pontos de Melhoria:**
- Uso de `StringEscapeUtils.escapeJava()` nos logs pode ser desnecessário e impactar performance
- Alguns métodos poderiam ser mais coesos (ex: validarCliente faz múltiplas responsabilidades)
- Falta de validação de entrada mais robusta (Bean Validation)
- Comentários em código poderiam ser mais descritivos
- Alguns testes mockam demais, reduzindo a confiabilidade
- Configuração de segurança poderia ser mais explícita
- Falta de tratamento de casos edge (ex: clientId vazio ou null em alguns fluxos)


---
### 14. Observações Relevantes

1. **Segurança**: O sistema utiliza OAuth2 com JWT para autenticação, mas também aceita um header alternativo "api-key-parceiro" para autenticação, o que pode representar um ponto de atenção em termos de segurança.

2. **Ambientes**: A aplicação está preparada para múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas de datasource e URLs de validação JWT.

3. **Monitoramento**: Infraestrutura completa de observabilidade com Prometheus e Grafana configurados via Docker Compose.

4. **Banco de Dados**: Utiliza SQL Server com pool de conexões HikariCP, configurado via JDBI ao invés de JPA/Hibernate.

5. **Testes**: Estrutura de testes bem organizada em três níveis (unit, integration, functional) com suporte a testes de contrato via Pact.

6. **CI/CD**: Configuração para Jenkins presente (jenkins.properties) indicando pipeline automatizado.

7. **Arquitetura**: Segue o padrão de microserviços atômicos do Banco Votorantim, com estrutura modular (common, domain, application).

8. **Logs**: Configuração de logs em formato JSON para facilitar integração com ferramentas de agregação de logs.