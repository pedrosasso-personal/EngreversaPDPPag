# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema atômico de consulta de contas Fintech do Banco Votorantim. O serviço expõe APIs REST para consultar informações completas de contas de usuários da Fintech, incluindo dados da conta, usuários vinculados e contas de pagamento associadas (CP1/CP2). Utiliza arquitetura hexagonal (ports and adapters) com separação clara entre camadas de domínio, aplicação e infraestrutura.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot que inicializa a aplicação |
| `FintechAccountController` | Controller REST que expõe endpoints de consulta de contas |
| `FintechAccountService` | Serviço de domínio com regras de negócio para consulta de contas |
| `FintechAccountRepository` | Interface (port) que define operações de acesso a dados |
| `FintechAccountRepositoryImpl` | Implementação do repositório usando JDBI para acesso ao SQL Server |
| `ConsultaContaFintechConfiguration` | Configuração Spring para beans, datasource e validação |
| `RestResponseEntityExceptionHandler` | Tratamento centralizado de exceções da API |
| `DadosContaCompletaMapper` | Mapper para conversão de entidades de domínio em DTOs de resposta |
| `DadosContaCompletaReducer` | Reducer JDBI para agregação de resultados de queries com joins |
| `DadosConta`, `DadosContaCompleta` | Entidades de domínio representando dados de conta |
| `Conta`, `Usuario` | Entidades de domínio para contas e usuários |

## 3. Tecnologias Utilizadas

- **Framework**: Spring Boot 2.x
- **Linguagem**: Java 11
- **Persistência**: JDBI 3.9.1 (SQL Object)
- **Banco de Dados**: Microsoft SQL Server (driver 7.4.0.jre11)
- **Documentação API**: Swagger/OpenAPI 2.9.2
- **Segurança**: Spring Security OAuth2 (Resource Server com JWT)
- **Métricas**: Spring Actuator + Micrometer + Prometheus
- **Auditoria**: BV Audit 2.2.1
- **Build**: Maven
- **Containerização**: Docker
- **Logging**: Logback com formato JSON
- **Testes**: JUnit 5, Rest Assured, Pact (contract testing)

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/consultaContaUsuarioFintech` | `FintechAccountController` | Consulta dados completos de conta Fintech (versão atual) |
| POST | `/consultaContaUsuarioFintech` | `FintechAccountController` | Consulta dados de conta Fintech (versão deprecated) |

**Request Body**: `ContaRequest` com `numeroConta` e `numeroAgencia`

**Response**: `DadosContaResponse` com informações completas da conta, lista de contas associadas e lista de usuários

## 5. Principais Regras de Negócio

1. **Validação de Agência**: Se a agência for nula ou "0", é tratada como string vazia na consulta
2. **Filtro de Status**: Apenas contas com `statusConta = 2` (ativa) são retornadas
3. **Conta Não Encontrada**: Lança `NotFoundException` quando não há resultados ou nenhuma conta ativa
4. **Tratamento de Erros**: Erros de banco de dados são convertidos em `InternalServerErrorException`
5. **Agregação de Dados**: A consulta completa agrega dados de múltiplas tabelas (conta, usuários, contas de pagamento) em uma única resposta
6. **Trim de Strings**: Campos de texto são automaticamente trimados antes de retornar na resposta
7. **Deduplicação**: O reducer garante que não haja duplicação de contas e usuários na resposta

## 6. Relação entre Entidades

**Modelo de Domínio:**

- `DadosContaCompleta` (entidade principal)
  - Contém: numeroConta, numeroAgencia, statusConta, codigoClienteGlobal, razaoSocial, tipoPessoa, numeroDocumento, statusFintech, dtAberturaConta
  - Possui lista de `Conta` (1:N)
  - Possui lista de `Usuario` (1:N)

- `Conta`
  - Representa contas de pagamento (CP1/CP2)
  - Atributos: numeroConta, numeroAgencia, tipoConta, descricaoConta

- `Usuario`
  - Representa usuários vinculados à conta
  - Atributos: tipoPessoa, codigoTipoVinculo, numeroDocumento, nome

**Relacionamentos no Banco:**
- TbContaUsuarioFintech (1) ←→ (N) TbRelacaoContaUsuarioFintech ←→ (1) TbUsuarioContaFintech
- TbContaUsuarioFintech (N) ←→ (1) TbParametroPagamentoFintech ←→ (1:N) TbContaPagamentoFintech

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbContaUsuarioFintech | Tabela | SELECT | Tabela principal de contas de usuários Fintech |
| TbParametroPagamentoFintech | Tabela | SELECT | Parâmetros de pagamento associados às contas |
| TbRelacaoContaUsuarioFintech | Tabela | SELECT | Relacionamento entre contas e usuários |
| TbUsuarioContaFintech | Tabela | SELECT | Dados dos usuários vinculados às contas |
| TbTipoVinculoConta | Tabela | SELECT | Tipos de vínculo dos usuários com as contas |
| TbContaPagamentoFintech | Tabela | SELECT | Contas de pagamento (CP1/CP2) da Fintech |

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | Spring Boot | Configurações da aplicação por ambiente |
| logback-spring.xml | Leitura | Logback | Configuração de logs (console e JSON) |
| messages.properties | Leitura | MessageSource | Mensagens de erro internacionalizadas |
| consultaContaCompleta.sql | Leitura | FintechAccountRepositoryImpl | Query SQL para consulta completa de conta |
| consultaContaFintech.sql | Leitura | FintechAccountRepositoryImpl | Query SQL para consulta de contas Fintech |
| consultaContaUsuario.sql | Leitura | FintechAccountRepositoryImpl | Query SQL para consulta de dados de conta |
| consultaUsuariosConta.sql | Leitura | FintechAccountRepositoryImpl | Query SQL para consulta de usuários da conta |

## 10. Filas Lidas

não se aplica

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| SQL Server (DBSPAG) | Banco de Dados | Banco de dados principal com tabelas de contas Fintech |
| OAuth2 JWT Provider | Autenticação | Validação de tokens JWT via JWK endpoint (api-uat.bancovotorantim.com.br ou api.bancovotorantim.com.br) |
| Prometheus | Métricas | Exportação de métricas via endpoint /actuator/prometheus |

## 13. Avaliação da Qualidade do Código

**Nota:** 8/10

**Justificativa:**

**Pontos Positivos:**
- Arquitetura hexagonal bem implementada com separação clara de responsabilidades (domain, application, infrastructure)
- Uso adequado de padrões como Repository, Service, Mapper e DTO
- Tratamento de exceções centralizado e consistente
- Configuração externalizada por ambiente
- Boa cobertura de testes (unitários, integração, funcionais, contract tests)
- Uso de Lombok reduzindo boilerplate
- Documentação OpenAPI/Swagger
- Observabilidade com métricas e health checks
- Segurança com OAuth2/JWT

**Pontos de Melhoria:**
- Método `consultaContaUsuarioFintech` marcado como deprecated mas ainda presente (deveria ser removido em versão futura)
- Conversão de String para JSON no log poderia usar biblioteca específica ao invés de try-catch genérico
- Algumas queries SQL poderiam ser otimizadas (múltiplos JOINs)
- Falta de paginação nas consultas que retornam listas
- Validação de entrada (ContaRequest) poderia ser mais robusta com Bean Validation
- Código de configuração poderia ser simplificado com uso de @ConfigurationProperties

## 14. Observações Relevantes

1. **Versão Deprecated**: Existe uma versão antiga do endpoint de consulta marcada como `@Deprecated`, indicando migração para nova versão com query otimizada
2. **Segurança**: Aplicação configurada como Resource Server OAuth2, requerendo token JWT válido para acesso
3. **Multi-ambiente**: Configuração preparada para múltiplos ambientes (local, des, qa, uat, prd)
4. **Auditoria**: Integração com biblioteca de auditoria BV para trilha de eventos
5. **Métricas**: Stack completa de observabilidade com Prometheus e Grafana configurados
6. **Containerização**: Dockerfile otimizado usando OpenJ9 Alpine para redução de footprint
7. **CI/CD**: Configuração Jenkins presente (jenkins.properties) para pipeline automatizado
8. **Infraestrutura como Código**: Arquivo infra.yml com configurações Kubernetes/OpenShift
9. **Connection Pool**: HikariCP configurado com pool de 20 conexões máximas e 10 mínimas
10. **Encoding**: Queries SQL configuradas com `sendStringParametersAsUnicode=false` para otimização