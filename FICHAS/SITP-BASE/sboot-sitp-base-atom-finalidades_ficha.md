# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-sitp-base-atom-finalidades** é um serviço atômico (microserviço) desenvolvido em Java com Spring Boot que tem como objetivo fornecer consultas de finalidades de transferências bancárias (TED e DOC). O sistema expõe APIs REST para listar finalidades de transferência, com suporte a cache (Redis) para otimização de performance. Permite também a remoção manual do cache. O serviço consulta dados de um banco de dados Sybase e utiliza autenticação via JWT.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal que inicializa a aplicação Spring Boot |
| **FinalidadesController** | Controlador REST que expõe os endpoints de consulta e remoção de cache de finalidades |
| **FinalidadesService** | Serviço de domínio que implementa a lógica de negócio, incluindo cache |
| **FinalidadesRepository** | Interface de porta (port) que define os métodos de acesso a dados |
| **FinalidadesRepositoryImpl** | Implementação do repositório utilizando JDBI para consultas SQL |
| **FinalidadeTransferencia** | Entidade de domínio representando uma finalidade de transferência |
| **TipoFinalidadeEnum** | Enum que define os tipos de finalidade (TED, DOC) e suas regras |
| **RazaoExceptionEnum** | Enum que define os códigos e mensagens de erro do sistema |
| **FinalidadesException** | Exceção customizada para erros de negócio |
| **ResourceExceptionHandler** | Tratador global de exceções para padronizar respostas de erro |
| **FinalidadesMapper** | Classe utilitária para conversão entre objetos de domínio e representação |
| **DatabaseConfiguration** | Configuração do JDBI para acesso ao banco de dados |
| **FinalidadesConfiguration** | Configuração dos beans de serviço e repositório |
| **OpenApiConfiguration** | Configuração do Swagger/OpenAPI para documentação da API |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Spring Web** (APIs REST)
- **Spring Security OAuth2** (autenticação JWT)
- **Spring Cache** (abstração de cache)
- **Spring Data Redis** (implementação de cache com Redis)
- **Spring Actuator** (monitoramento e métricas)
- **JDBI 3.9.1** (acesso a banco de dados)
- **Sybase jConnect 16.3** (driver JDBC para Sybase)
- **Swagger/Springfox 2.9.2** (documentação de API)
- **Lombok** (redução de boilerplate)
- **Micrometer + Prometheus** (métricas)
- **Logback** (logging)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **OpenShift/Kubernetes** (orquestração)
- **HikariCP** (pool de conexões)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/banco-digital/listar-finalidades` | FinalidadesController | Lista finalidades de transferência (TED ou DOC) com cache. Parâmetros: `tipoFinalidade` (TED/DOC), `todos` (boolean) |
| DELETE | `/v1/banco-digital/listar-finalidades/cache` | FinalidadesController | Remove o cache da lista de finalidades |

---

## 5. Principais Regras de Negócio

1. **Tipos de Finalidade**: O sistema suporta dois tipos de finalidade - TED (códigos de liquidação 31 e 32) e DOC (código de liquidação 21).

2. **Filtro de Finalidades TED**: Para TED, quando `todos=false`, retorna apenas finalidades com descrições específicas (Crédito em conta, Pagamento à Concessionárias, Pagamento de impostos, etc.). Quando `todos=true`, retorna todas as finalidades TED ativas, exceto código 99999.

3. **Filtro de Finalidades DOC**: Para DOC, quando `todos=true`, retorna todas as finalidades ativas. Quando `todos=false`, aplica filtro por descrições (lista vazia no enum).

4. **Cache**: As consultas são cacheadas com chave composta por tipo de finalidade e flag "todos". O cache pode ser removido manualmente via endpoint DELETE.

5. **Validação de Tipo**: Tipo de finalidade inválido resulta em exceção `BDCC_TIPO_FINALIDADE_INVALIDO` com status HTTP 400.

6. **Filtro de Status**: Apenas finalidades com status 'A' (ativo) são retornadas.

---

## 6. Relação entre Entidades

**FinalidadeTransferencia** (Entidade de Domínio):
- `codigo` (Long): Código identificador da finalidade
- `descricao` (String): Descrição textual da finalidade

**TipoFinalidadeEnum** (Enum):
- TED: possui lista de códigos de liquidação [31, 32] e lista de descrições permitidas
- DOC: possui lista de códigos de liquidação [21] e lista de descrições vazia

Não há relacionamentos complexos entre entidades. O modelo é simples e focado em consultas de dados de referência.

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TBL_FINALIDADE_SPB | Tabela | SELECT | Tabela que armazena as finalidades de transferências do SPB (Sistema de Pagamentos Brasileiro). Campos consultados: Cod_Finalidade, Descr_Finalidade, Cod_Liquidacao, Status, Tp_Finalidade |

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema realiza apenas operações de leitura (SELECT).

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| consultarFinalidades.sql | Leitura | FinalidadesRepositoryImpl | Query SQL para consultar finalidades com filtros específicos |
| consultarTodasFinalidadesDoc.sql | Leitura | FinalidadesRepositoryImpl | Query SQL para consultar todas as finalidades DOC ativas |
| consultarTodasFinalidadesTed.sql | Leitura | FinalidadesRepositoryImpl | Query SQL para consultar todas as finalidades TED ativas (exceto 99999) |
| application.yml | Leitura | Spring Boot | Arquivo de configuração da aplicação (datasource, cache, security, etc.) |
| logback-spring.xml | Leitura | Logback | Configuração de logs da aplicação |

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
| Banco de Dados Sybase (DBITP) | Banco de Dados | Consulta de finalidades de transferência. Conexão via JDBC (Sybase jConnect) |
| Redis | Cache | Armazenamento em cache das consultas de finalidades para otimização de performance |
| Servidor JWT | Autenticação | Validação de tokens JWT para autenticação das requisições. URL configurável por ambiente (jwks.json) |
| Prometheus | Monitoramento | Exportação de métricas da aplicação via endpoint `/actuator/prometheus` |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo princípios de Clean Architecture (separação em camadas: domain, application, infrastructure)
- Uso adequado de padrões como Repository, Service, Mapper e Exception Handler
- Configuração clara e separada por responsabilidade (Database, Security, OpenAPI)
- Uso de cache para otimização de performance
- Documentação via Swagger/OpenAPI
- Testes estruturados em diferentes níveis (unit, integration, functional)
- Uso de Lombok para redução de boilerplate
- Configuração de métricas e observabilidade (Actuator, Prometheus, Grafana)
- Uso de JDBI com SQL externalizado em arquivos separados

**Pontos de Melhoria:**
- Falta de tratamento de exceções específicas do banco de dados
- Enum `TipoFinalidadeEnum` com lista de descrições hardcoded poderia ser mais flexível
- Ausência de validação de entrada nos parâmetros dos endpoints
- Falta de logs estruturados em alguns pontos críticos
- Configuração de cache com TTL fixo poderia ser mais configurável

O código demonstra boas práticas de desenvolvimento, organização clara e preocupação com manutenibilidade, mas há espaço para melhorias em validações e tratamento de erros.

---

## 14. Observações Relevantes

1. **Ambientes**: O sistema está configurado para múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas de datasource, Redis e URLs de autenticação.

2. **Cache Redis**: O cache possui TTL configurável por ambiente (5 minutos em DEV, 24 horas em UAT/PRD) e pode ser removido manualmente via endpoint DELETE.

3. **Segurança**: Todas as APIs requerem autenticação via Bearer Token (JWT). A validação é feita contra um servidor OAuth2 externo.

4. **Monitoramento**: A aplicação expõe métricas detalhadas via Actuator/Prometheus, incluindo JVM, HTTP, HikariCP e logs. Dashboard Grafana pré-configurado disponível.

5. **Infraestrutura**: O projeto inclui configuração completa de infraestrutura como código (infra-as-code) para deploy em OpenShift/Kubernetes.

6. **Pool de Conexões**: Utiliza HikariCP para gerenciamento eficiente de conexões com o banco de dados Sybase.

7. **Auditoria**: Integração com biblioteca de auditoria do Banco Votorantim (springboot-arqt-base-trilha-auditoria-web).

8. **Arquitetura de Testes**: Estrutura de testes bem definida com separação entre testes unitários, de integração e funcionais, incluindo testes de contrato (Pact).