# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-spag-base-atom-limites** é um serviço atômico REST desenvolvido em Spring Boot que fornece informações sobre limites de tributos para pagamentos. O sistema consulta dados de configuração de pagamento de tributos em um banco de dados SQL Server, retornando informações sobre limites de valores, contas bancárias e prestadores de serviço associados.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal que inicializa a aplicação Spring Boot com segurança OAuth2 |
| **LimitesController** | Controlador REST que expõe o endpoint de consulta de limites de tributos |
| **LimitesService** | Serviço de domínio que implementa a lógica de negócio para validação e recuperação de tributos |
| **JdbiLimitesRepository** | Interface de repositório que utiliza JDBI para acesso ao banco de dados |
| **Tributos** | Entidade de domínio que representa os dados de limite de tributos |
| **LimitesMapper** | Classe responsável por converter objetos de domínio em representações REST |
| **TributosRowMapper** | Mapper JDBI que converte ResultSet em objetos Tributos |
| **JdbiConfiguration** | Configuração do JDBI e registro de plugins e mappers |
| **LimitesConfiguration** | Configuração de beans do domínio de limites |
| **OpenApiConfiguration** | Configuração do Swagger/OpenAPI para documentação da API |
| **LimitesException** | Exceção customizada do domínio de limites |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Spring Security OAuth2** (autenticação e autorização)
- **JDBI 3.9.1** (acesso a banco de dados)
- **SQL Server** (banco de dados)
- **Swagger/Springfox 2.10.5** (documentação de API)
- **Lombok** (redução de boilerplate)
- **Micrometer/Prometheus** (métricas e monitoramento)
- **Logback** (logging)
- **JUnit 5** (testes unitários)
- **Mockito** (mocks para testes)
- **RestAssured** (testes funcionais)
- **Pact** (testes de contrato)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Grafana/Prometheus** (observabilidade)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/limites/tributos/{codigoBanco}` | LimitesController | Busca informações de limite de tributos por código do banco |

---

## 5. Principais Regras de Negócio

1. **Validação de Tributos**: O sistema valida se os tributos foram encontrados para o código do banco informado. Caso não sejam encontrados, retorna HTTP 204 (No Content).

2. **Filtro de Parâmetros Ativos**: A consulta ao banco considera apenas registros com `FlAtivo = 'S'` (flag de ativo).

3. **Finalidade de Conta Específica**: Apenas contas com `CdFinalidadeConta = 1` são consideradas.

4. **Parâmetro de Pagamento Fixo**: A consulta filtra por `CdParametroPagamentoTributo = 1`.

5. **Relacionamento Obrigatório**: É necessário que exista relacionamento entre `TbParametroPagamentoTributo` e `TbContaFornecedorTributo`.

---

## 6. Relação entre Entidades

**Tributos** (entidade principal):
- Contém informações de limite de pagamento de tributos
- Relaciona-se com dados de banco (código, agência, conta)
- Contém dados do favorecido (CPF/CNPJ, nome, tipo de pessoa)
- Possui informações do prestador de serviço e valor limite

**Relacionamento no banco de dados**:
- `TbParametroPagamentoTributo` (1) ←→ (N) `TbContaFornecedorTributo`
- Join realizado por `CdParametroPagamentoTributo`

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbParametroPagamentoTributo | Tabela | SELECT | Armazena parâmetros de pagamento de tributos, incluindo prestador de serviço e valor limite |
| TbContaFornecedorTributo | Tabela | SELECT | Armazena dados de contas bancárias de fornecedores para pagamento de tributos |

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| getLimiteTributos.sql | Leitura | JdbiLimitesRepository | Query SQL para buscar limites de tributos |
| application.yml | Leitura | Spring Boot | Configurações da aplicação |
| application-local.yml | Leitura | Spring Boot | Configurações para ambiente local |
| logback-spring.xml | Leitura | Logback | Configuração de logs |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| SQL Server (DBSPAG) | Banco de Dados | Banco de dados principal contendo tabelas de tributos e fornecedores |
| API Gateway OAuth2 | Autenticação | Servidor de autenticação OAuth2 para validação de tokens JWT |
| Prometheus | Monitoramento | Coleta de métricas da aplicação |
| Grafana | Visualização | Dashboard de monitoramento e métricas |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem organizada seguindo princípios de Clean Architecture (separação em módulos domain, application, common)
- Uso adequado de padrões como Repository, Service e Mapper
- Boa cobertura de testes (unitários, integração e funcionais)
- Configuração adequada de segurança OAuth2
- Uso de JDBI para queries SQL de forma organizada
- Documentação OpenAPI/Swagger configurada
- Observabilidade implementada (Prometheus, Grafana)
- Uso de Lombok para reduzir boilerplate

**Pontos de Melhoria:**
- Falta de tratamento de exceções mais específico (apenas LimitesException genérica)
- Ausência de paginação no endpoint (embora retorne apenas um registro)
- Configurações de banco hardcoded no application-local.yml (credenciais expostas)
- Alguns testes vazios (LimitesConfigurationTest, LimitesRepositoryImplTest)
- Falta de validação de entrada no controller (código do banco)
- Documentação técnica poderia ser mais detalhada no README

---

## 14. Observações Relevantes

1. **Segurança**: O sistema utiliza OAuth2 Resource Server com validação de tokens JWT via API Gateway.

2. **Ambiente Multi-Profile**: Suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas.

3. **Containerização**: Possui Dockerfile configurado para deploy em OpenShift/Kubernetes.

4. **Monitoramento**: Implementa métricas do Micrometer expostas via Actuator para Prometheus.

5. **Infraestrutura como Código**: Possui arquivo `infra.yml` para provisionamento automatizado.

6. **Pipeline CI/CD**: Configurado para Jenkins com propriedades específicas (jenkins.properties).

7. **Testes de Contrato**: Preparado para Pact (testes de contrato entre consumidor e provedor).

8. **Arquitetura Hexagonal**: Utiliza ports (interfaces) e adapters (implementações) para desacoplamento.

9. **Banco de Dados**: Conecta-se ao banco DBSPAG (SQL Server) em servidor SQLBVFDES05:2500.

10. **Limitação Funcional**: O sistema atualmente suporta apenas consulta de um tipo específico de tributo (CdParametroPagamentoTributo = 1).