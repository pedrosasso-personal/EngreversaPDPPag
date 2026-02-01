---
## Ficha Técnica do Sistema


### 1. Descrição Geral
Sistema atômico de consulta de dados de boletos bancários desenvolvido em Spring Boot. O serviço expõe uma API REST para consulta de informações detalhadas de boletos através de diversos parâmetros (hash do boleto, número de contrato, sequência de contrato, nosso número, código do veículo legal e código do instrumento de cobrança). Os dados são recuperados de um banco de dados Sybase (DBCARNE) e retornados em formato JSON.


### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal que inicializa a aplicação Spring Boot com segurança OAuth2 |
| `DadosBoletoController` | Controlador REST que expõe o endpoint de consulta de dados de boletos |
| `DadosBoletoService` | Serviço de domínio que orquestra a lógica de negócio de consulta |
| `JdbiDadosBoletoRepository` | Interface de repositório que define operações de acesso a dados usando JDBI |
| `DadosBoletoConfiguration` | Classe de configuração Spring que define beans (JDBI, repositório, serviço) |
| `DadosBoleto` | Entidade de domínio que representa os dados de um boleto |
| `RequestConsultaDadosBoleto` | DTO que encapsula os parâmetros de consulta |
| `DadosBoletoRowMapper` | Mapper responsável por converter ResultSet em objetos DadosBoleto |
| `ControllerUtil` | Classe utilitária para conversão de objetos de domínio em representações REST |
| `OpenApiConfiguration` | Configuração do Swagger/OpenAPI para documentação da API |


### 3. Tecnologias Utilizadas
- **Framework:** Spring Boot 2.x
- **Linguagem:** Java 11
- **Persistência:** JDBI 3.9.1 com Sybase jConnect 16.3
- **Banco de Dados:** Sybase ASE (DBCARNE)
- **Segurança:** Spring Security OAuth2 (Resource Server com JWT)
- **Documentação:** Swagger 2.9.2 / SpringFox
- **Monitoramento:** Spring Boot Actuator, Micrometer, Prometheus
- **Pool de Conexões:** HikariCP
- **Logging:** Logback
- **Build:** Maven
- **Testes:** JUnit 5, Mockito, Rest Assured, Pact
- **Container:** Docker (OpenJDK 11 com OpenJ9)
- **Observabilidade:** Grafana + Prometheus


### 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/varejo/gestao-contrato/boleto/dados` | `DadosBoletoController` | Consulta dados de boletos por diversos parâmetros (hashBoleto, numeroContrato, sequenciaContrato, codigoNossoNumero, codigoVeiculoLegal, codigoInstrumentoCobranca) |


### 5. Principais Regras de Negócio
- A consulta de boletos permite filtros combinados através de múltiplos parâmetros opcionais
- O parâmetro `numeroContrato` é obrigatório conforme especificação do Swagger
- A consulta retorna apenas a situação de processamento mais recente do boleto (através de subconsulta MAX na data de situação)
- Strings são tratadas com remoção de espaços em branco (trim) antes do processamento
- Retorna HTTP 404 quando nenhum boleto é encontrado com os critérios informados
- Retorna HTTP 400 em caso de erro no processamento da requisição
- O sistema utiliza flags booleanas para controlar dinamicamente quais filtros aplicar na query SQL


### 6. Relação entre Entidades

**Entidade Principal:**
- `DadosBoleto`: Representa os dados completos de um boleto bancário

**Relacionamentos identificados na query SQL:**
- `TbRegistroInstrumentoCobranca` (registro): Tabela principal com dados do boleto
- `TbSituacaoProcessamentoInsto` (situacao): Relacionamento 1:N com registro, contém histórico de situações
- `TbEstadoProcessamento` (estado): Relacionamento N:1 com situacao, descreve o estado de processamento
- `TbOcorrenciaRejeicaoPrcso` (rejeicao): Relacionamento 1:1 opcional com registro, contém dados de rejeição

**Estrutura de domínio:**
- `RequestConsultaDadosBoleto`: DTO de entrada para consultas
- `DadosBoletoResponseRepresentation`: DTO de saída (gerado via Swagger Codegen)
- `ListaDadosBoletoResponseRepresentation`: Wrapper para lista de boletos


### 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBCARNE..TbRegistroInstrumentoCobranca | tabela | SELECT | Tabela principal contendo registros de instrumentos de cobrança (boletos) |
| DBCARNE..TbSituacaoProcessamentoInsto | tabela | SELECT | Histórico de situações de processamento dos instrumentos de cobrança |
| DBCARNE..TbEstadoProcessamento | tabela | SELECT | Tabela de domínio com descrição dos estados de processamento |
| DBCARNE..TbOcorrenciaRejeicaoPrcso | tabela | SELECT | Tabela com ocorrências de rejeição no processamento de boletos |


### 8. Estruturas de Banco de Dados Atualizadas
não se aplica


### 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot (startup) | Arquivo de configuração da aplicação com profiles (local, des, uat, prd) |
| logback-spring.xml | leitura | Logback (startup) | Configuração de logging da aplicação |
| getDadosBoleto.sql | leitura | JdbiDadosBoletoRepository | Query SQL para consulta de dados de boletos (template StringTemplate4) |
| sboot-saca-scco-atom-dados-boleto.yaml | leitura | Swagger Codegen (build) | Especificação OpenAPI para geração de interfaces REST |


### 10. Filas Lidas
não se aplica


### 11. Filas Geradas
não se aplica


### 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Banco Sybase (DBCARNE) | Banco de Dados | Banco de dados principal para consulta de informações de boletos |
| Servidor OAuth2/JWT | Autenticação | Validação de tokens JWT para autenticação e autorização (URLs variam por ambiente: apigatewaydes.bvnet.bv, apigatewayqa.bvnet.bv, apigatewayuat.bvnet.bv, apigateway.bvnet.bv) |
| Prometheus | Monitoramento | Exportação de métricas da aplicação via endpoint /actuator/prometheus |


### 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões hexagonais (ports/adapters)
- Separação clara entre camadas (domain, application, infrastructure)
- Uso adequado de padrões como Builder, Repository, Service
- Configuração de segurança OAuth2 implementada
- Boa cobertura de testes (unitários, integração, funcionais)
- Uso de JDBI com SQL externalizado e templates dinâmicos
- Documentação OpenAPI/Swagger bem definida
- Configuração de observabilidade (Actuator, Prometheus, Grafana)

**Pontos de Melhoria:**
- Classe `ControllerUtil` com métodos estáticos e lógica de conversão que poderia ser um componente Spring
- Tratamento de exceções genérico no controller (catch Exception retornando apenas badRequest)
- Falta de validação de entrada mais robusta (Bean Validation)
- Alguns testes vazios ou comentados (DadosBoletoApiFunctionalTest, DadosBoletoControllerPactTest)
- Query SQL complexa poderia ser quebrada em views ou procedures para melhor manutenibilidade
- Falta de logs estruturados para rastreabilidade de requisições
- Ausência de cache para consultas frequentes
- Código de testes com alguns anti-patterns (uso de `MockitoAnnotations.initMocks` deprecated)


### 14. Observações Relevantes

1. **Ambiente e Deploy:** O projeto está preparado para deploy em OpenShift (Google Cloud Platform) com configurações específicas por ambiente (des, qa, uat, prd)

2. **Segurança:** Implementa OAuth2 Resource Server com validação de JWT, mas não há controle de autorização granular por endpoint

3. **Monitoramento:** Stack completa de observabilidade configurada (Prometheus + Grafana) com dashboards pré-configurados para métricas de JVM, HTTP, HikariCP e logs

4. **Banco de Dados:** Utiliza Sybase com charset ISO-1, importante considerar encoding em operações com strings

5. **Arquitetura de Testes:** Estrutura bem organizada com separação de testes unitários, integração e funcionais em diretórios distintos

6. **Geração de Código:** Utiliza Swagger Codegen para gerar interfaces de API a partir da especificação OpenAPI, garantindo contrato consistente

7. **Versionamento:** API versionada (v1) no path, facilitando evolução futura

8. **Infraestrutura como Código:** Configurações de infraestrutura (infra.yml) para provisionamento automatizado em Kubernetes/OpenShift

9. **Pool de Conexões:** HikariCP configurado com métricas expostas para monitoramento de performance de conexões

10. **Template SQL:** Uso de StringTemplate4 para queries dinâmicas, permitindo construção condicional de filtros SQL