# Ficha Técnica do Sistema

---

## 1. Descrição Geral

O **sboot-pgft-base-atom-consulta-contabil** é um serviço atômico (microserviço) desenvolvido em Java com Spring Boot, responsável por realizar consultas contábeis relacionadas a lançamentos financeiros. O sistema consulta dados de movimentações contábeis em um banco de dados Sybase, agregando valores por evento contábil e data de movimento. A aplicação expõe uma API REST para que outros sistemas possam consultar débitos de contas contábeis de forma consolidada.

---

## 2. Principais Classes e Responsabilidades

| Classe/Interface | Responsabilidade |
|------------------|------------------|
| **Application** | Classe principal que inicializa a aplicação Spring Boot com segurança OAuth2 habilitada. |
| **DebitoContaContabilController** | Controlador REST que expõe o endpoint de consulta de débitos contábeis. |
| **LancamentoService** | Serviço de domínio que orquestra a lógica de negócio para consulta de lançamentos. |
| **JdbiLancamentoRepository** | Repositório de infraestrutura que realiza consultas SQL no banco de dados usando JDBI. |
| **LancamentoRowMapper** | Mapper responsável por converter ResultSet em objetos de domínio Lancamento. |
| **DebitoContaContabilMapper** | Mapper que converte objetos de domínio em representações de resposta da API. |
| **Lancamento** | Entidade de domínio que representa um lançamento contábil. |
| **ConsultaContabilConfiguration** | Configuração do Spring que define beans de repositório, serviço e JDBI. |
| **CustomExceptionHandler** | Tratador global de exceções para a aplicação. |
| **OpenApiConfiguration** | Configuração do Swagger/OpenAPI para documentação da API. |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Spring Security OAuth2** (autenticação e autorização)
- **JDBI 3.9.1** (acesso a dados via SQL)
- **Sybase ASE** (banco de dados)
- **Swagger/Springfox 2.9.2** (documentação de API)
- **Lombok** (redução de boilerplate)
- **Micrometer + Prometheus** (métricas e monitoramento)
- **Spring Actuator** (endpoints de saúde e métricas)
- **HikariCP** (pool de conexões)
- **Logback** (logging)
- **JUnit 5 + Mockito** (testes unitários)
- **RestAssured** (testes funcionais)
- **Pact** (testes de contrato)
- **Maven** (gerenciamento de dependências e build)
- **Docker** (containerização)
- **Grafana + Prometheus** (observabilidade)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/debito-conta-contabil/consultar` | DebitoContaContabilController | Retorna a soma dos valores dos movimentos para os eventos contábeis informados em uma data específica. Recebe lista de códigos de eventos, código do banco e data de movimento. |

---

## 5. Principais Regras de Negócio

1. **Consulta de Lançamentos por Evento e Data**: O sistema busca lançamentos contábeis filtrando por uma lista de códigos de eventos contábeis, código do banco e data de movimento específica.

2. **Agregação de Valores**: Os valores dos lançamentos são somados (agregados) por código de evento contábil, retornando o total consolidado para cada evento.

3. **Filtro de Status**: Apenas lançamentos com status ativo (`Val_Status = 1`) são considerados na consulta.

4. **Filtro por Banco Remetente**: A consulta considera apenas lançamentos do banco remetente especificado (`Num_Banco_Remetente`).

5. **Cálculo de Total Geral**: Além do total por evento, o sistema calcula e retorna o valor total somando todos os eventos consultados.

6. **Tratamento de Resultados Vazios**: Quando não há lançamentos para os critérios informados, o sistema retorna uma lista vazia com valor total zero.

---

## 6. Relação entre Entidades

**Entidade Principal:**
- **Lancamento**: Representa um lançamento contábil com os atributos:
  - `cdEventoContabil` (Long): Código do evento contábil
  - `valor` (BigDecimal): Valor do lançamento
  - `dtMovimento` (LocalDate): Data do movimento

**Relacionamentos:**
- Não há relacionamentos JPA explícitos, pois a aplicação utiliza JDBI para acesso direto ao banco via SQL.
- A entidade Lancamento é mapeada a partir da tabela `TBL_LANCAMENTO` através do `LancamentoRowMapper`.

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TBL_LANCAMENTO | Tabela | SELECT | Tabela de lançamentos contábeis. Contém informações sobre eventos contábeis, valores, datas de movimento, status e banco remetente. A consulta agrupa por código de evento e data, somando os valores. |

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema realiza apenas operações de leitura (SELECT).

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | Spring Boot (startup) | Arquivo de configuração da aplicação contendo propriedades de datasource, segurança, servidor e logging. |
| logback-spring.xml | Leitura | Logback (runtime) | Configuração de logging da aplicação, definindo appenders, níveis de log e formato de saída. |
| consulta-contabil-contract.yaml | Leitura | Swagger Codegen (build time) | Contrato OpenAPI usado para gerar interfaces e representações de API durante o build. |
| getByListCodEventoAndDtMovimento.sql | Leitura | JDBI (runtime) | Query SQL utilizada pelo repositório para consultar lançamentos contábeis. |

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

---

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| API Gateway OAuth2 | Autenticação | O sistema integra-se com um API Gateway para validação de tokens JWT OAuth2. A URL do gateway é configurada por ambiente (des, qa, uat, prd). |
| Banco de Dados Sybase | Banco de Dados | Conexão JDBC com banco Sybase ASE (DBPGF_TES) para consulta de lançamentos contábeis. Credenciais e URLs variam por ambiente. |
| Prometheus | Monitoramento | Exposição de métricas via endpoint `/actuator/prometheus` para coleta pelo Prometheus. |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem organizada seguindo princípios de Clean Architecture (separação em camadas: domain, application, infrastructure)
- Uso adequado de padrões como Repository, Service e Mapper
- Boa cobertura de testes (unitários, integração e funcionais)
- Configuração adequada de segurança OAuth2
- Documentação via Swagger/OpenAPI
- Uso de Lombok para reduzir boilerplate
- Configuração de observabilidade (métricas, health checks)
- Separação clara de responsabilidades entre classes

**Pontos de Melhoria:**
- Falta de validação de entrada mais robusta nos controllers (Bean Validation)
- Ausência de logs estruturados em pontos críticos do código
- Configuração de segurança desabilitada em ambientes locais/des pode ser um risco
- Falta de tratamento específico para diferentes tipos de exceções de banco de dados
- Ausência de cache para consultas frequentes
- Documentação inline (JavaDoc) poderia ser mais completa

---

## 14. Observações Relevantes

1. **Ambientes**: A aplicação está preparada para múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas de datasource e segurança.

2. **Segurança**: A segurança OAuth2 está desabilitada em ambientes local e des, mas habilitada em qa, uat e prd.

3. **Monitoramento**: A aplicação expõe métricas detalhadas via Actuator/Prometheus, incluindo métricas de JVM, HikariCP, HTTP e logs.

4. **Infraestrutura como Código**: O projeto inclui configurações completas de infraestrutura (infra.yml) para deploy em Kubernetes/OpenShift.

5. **CI/CD**: Configuração Jenkins presente (jenkins.properties) indicando pipeline automatizado.

6. **Observabilidade Local**: Inclui stack completa de observabilidade local com Docker Compose (Prometheus + Grafana) para desenvolvimento.

7. **Testes**: Estrutura de testes bem organizada com separação clara entre testes unitários, de integração e funcionais.

8. **Padrão de Nomenclatura**: Segue convenções do Banco Votorantim (prefixo sboot-pgft-base-atom).

9. **Versionamento**: Projeto na versão 0.16.0, indicando maturidade em desenvolvimento.

10. **Pool de Conexões**: Utiliza HikariCP com configurações de monitoramento detalhadas.