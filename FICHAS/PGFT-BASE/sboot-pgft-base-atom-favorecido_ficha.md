# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-pgft-base-atom-favorecido** é um serviço atômico REST desenvolvido em Java com Spring Boot, responsável por consultar informações de favorecidos (beneficiários de pagamentos) no sistema PGFT (Plataforma de Gestão Financeira e Tesouraria) do Banco Votorantim. O sistema expõe endpoints REST para recuperar dados de favorecidos a partir de protocolos de lançamento, consultando diretamente a tabela `TBL_LANCAMENTO` do banco de dados Sybase (DBPGF_TES). Trata-se de um microserviço de consulta (read-only) que segue arquitetura hexagonal (ports and adapters) com separação clara entre camadas de domínio, aplicação e infraestrutura.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application.java** | Classe principal Spring Boot que inicializa a aplicação e habilita o servidor de recursos OAuth2 |
| **FavorecidoController.java** | Controlador REST que expõe os endpoints de consulta de favorecidos |
| **FavorecidoService.java** | Serviço de domínio que implementa a lógica de negócio para recuperação de favorecidos |
| **FavorecidoRepositoryImpl.java** | Implementação do repositório usando JDBI para acesso ao banco Sybase |
| **Favorecido.java** | Entidade de domínio representando um favorecido (id, nome, nuDocumento) |
| **FavorecidoRowMapper.java** | Mapper JDBI para conversão de ResultSet em objetos Favorecido |
| **FavorecidoRepresentationMapper.java** | Mapper para conversão de entidades de domínio em representações REST |
| **ExceptionHandlerConfiguration.java** | Tratamento centralizado de exceções REST |
| **JdbiConfiguration.java** | Configuração do JDBI para acesso a dados |
| **FavorecidoConfiguration.java** | Configuração de beans do domínio Favorecido |
| **OpenApiConfiguration.java** | Configuração do Swagger/OpenAPI para documentação |

---

## 3. Tecnologias Utilizadas

- **Java 11** (OpenJDK 11 com OpenJ9)
- **Spring Boot 2.x** (framework principal)
- **Spring Security OAuth2** (autenticação via JWT/JWK)
- **JDBI 3.9.1** (acesso a dados SQL)
- **Sybase jConnect 16.3** (driver JDBC para Sybase ASE)
- **Springfox Swagger 3.0.0** (documentação OpenAPI)
- **Spring Boot Actuator** (health checks e métricas)
- **Micrometer + Prometheus** (métricas customizadas)
- **Logback** (logging com suporte a JSON)
- **Lombok** (redução de boilerplate)
- **JUnit 5 + Mockito** (testes unitários)
- **Rest Assured** (testes funcionais)
- **Pact** (testes de contrato)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **OpenShift/Kubernetes** (orquestração)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/consultarFavorecido` | FavorecidoController | Consulta um único favorecido por ID (via header) |
| GET | `/v1/consultarFavorecidos` | FavorecidoController | Consulta múltiplos favorecidos por IDs (via header CSV) |
| GET | `/v1/consultarFavorecidosV2` | FavorecidoController | Consulta múltiplos favorecidos por IDs (via body JSON) |

**Observação:** Todos os endpoints requerem autenticação OAuth2 via token Bearer JWT.

---

## 5. Principais Regras de Negócio

1. **Conversão de IDs**: Os IDs de favorecidos recebidos como String são convertidos para Long (protocolo) antes da consulta ao banco
2. **Tratamento de IDs nulos/vazios**: IDs nulos ou vazios são substituídos pelo valor padrão `1L` para evitar erros de conversão
3. **Retorno vazio**: Quando não há favorecidos encontrados, retorna HTTP 204 (No Content) ao invés de lista vazia
4. **Consulta única vs múltipla**: A consulta de um único favorecido reutiliza internamente a lógica de consulta múltipla
5. **Validação de entrada**: Listas de IDs nulas resultam em Optional.empty() e log de erro
6. **Mapeamento de dados**: Conversão entre entidades de domínio e representações REST através de mappers dedicados

---

## 6. Relação entre Entidades

**Entidade Principal:**
- **Favorecido** (domínio)
  - `id: Long` - Código do protocolo (chave primária)
  - `nome: String` - Nome do favorecido
  - `nuDocumento: String` - Número do documento (CPF/CNPJ)

**Representação REST:**
- **FavorecidoRepresentation**
  - `id: String` - ID convertido para String
  - `nome: String` - Nome do favorecido
  - `nuDocumento: String` - Número do documento

**Relacionamento:** Não há relacionamentos complexos entre entidades. O sistema trabalha com uma única entidade de domínio (Favorecido) que é mapeada diretamente de uma tabela de banco de dados.

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBPGF_TES.dbo.TBL_LANCAMENTO | Tabela | SELECT | Tabela de lançamentos financeiros contendo informações de favorecidos (Cod_Protocolo, Nome_Favorecido, Num_Cgc_Favorecido) |

**Query SQL utilizada:**
```sql
SELECT 
  TBL.Cod_Protocolo AS "id",
  TBL.Nome_Favorecido as "nome",
  TBL.Num_Cgc_Favorecido AS "nuDocumento"
FROM DBPGF_TES.dbo.TBL_LANCAMENTO TBL
WHERE TBL.Cod_Protocolo IN (<ids>)
```

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema é exclusivamente de consulta (read-only), não realizando operações de INSERT, UPDATE ou DELETE.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | Spring Boot (startup) | Configurações da aplicação (datasource, OAuth2, profiles) |
| logback-spring.xml | Leitura | Logback (startup) | Configuração de logging (console/file, formato JSON) |
| getFavorecidosByProtocolos.sql | Leitura | FavorecidoRepositoryImpl (JDBI) | Query SQL para consulta de favorecidos |
| sboot-pgft-base-atom-favorecido.yml | Leitura | Swagger Codegen (build) | Especificação OpenAPI para geração de interfaces |

**Observação:** Não há geração de arquivos pelo sistema em tempo de execução. Logs são escritos em console/arquivo conforme configuração do Logback.

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas (JMS, Kafka, RabbitMQ, etc).

---

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **API Gateway (CA API)** | OAuth2/JWK | Validação de tokens JWT através do endpoint JWK (https://apigateway.bvnet.bv/openid/connect/jwks.json) |
| **Banco Sybase ASE** | Banco de Dados | Consulta à base DBPGF_TES para recuperação de dados de favorecidos |
| **Prometheus** | Métricas | Exportação de métricas via endpoint `/actuator/prometheus` |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura hexagonal bem definida com separação clara de camadas (domain, application, infrastructure)
- Uso adequado de padrões como Repository, Service e Mapper
- Boa cobertura de testes unitários e estrutura para testes de integração/funcionais
- Configuração adequada de segurança OAuth2
- Documentação OpenAPI/Swagger presente
- Uso de Lombok para redução de boilerplate
- Configuração de métricas e observabilidade (Actuator, Prometheus)

**Pontos de Melhoria:**
- **Tratamento de erros inconsistente**: IDs nulos/vazios são substituídos por `1L` silenciosamente, o que pode mascarar problemas
- **Lógica de negócio no Service**: O método `getFavorecidos` contém lógica de conversão e validação que poderia estar em camadas mais apropriadas
- **Falta de validação de entrada**: Não há validação formal dos parâmetros de entrada (Bean Validation)
- **Comentários em português**: Mistura de português e inglês no código
- **Testes comentados**: Alguns testes estão comentados (ApplicationTest, FavorecidoServiceTest)
- **Código duplicado**: `consultarFavorecidosV2` apenas delega para `consultarFavorecidos`
- **Falta de paginação**: Consultas múltiplas sem limite de resultados podem causar problemas de performance
- **Exception genérica**: Captura de `Exception` genérica no service ao invés de exceções específicas

---

## 14. Observações Relevantes

1. **Ambientes**: O sistema suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas de datasource e OAuth2
2. **Pool de conexões**: Configuração de HikariCP com tamanhos diferentes por ambiente (2 conexões em dev, 5 em produção)
3. **Segurança**: Autenticação obrigatória via OAuth2 JWT em todos os endpoints
4. **Auditoria**: Integração com biblioteca de trilha de auditoria do BV (`springboot-arqt-base-trilha-auditoria-web`)
5. **Monitoramento**: Health checks expostos em porta separada (9090) para facilitar orquestração Kubernetes
6. **Charset**: Uso de charset `iso_1` na conexão Sybase para compatibilidade com dados legados
7. **Versão duplicada**: Endpoint V2 criado especificamente para receber IDs via body ao invés de header (requisito de integração)
8. **Arquitetura de testes**: Separação clara entre testes unitários, integração e funcionais em diretórios distintos
9. **CI/CD**: Configuração para Jenkins com propriedades específicas (jenkins.properties) e infraestrutura como código (infra.yml)
10. **Containerização**: Dockerfile otimizado usando OpenJDK 11 com OpenJ9 (menor footprint de memória)