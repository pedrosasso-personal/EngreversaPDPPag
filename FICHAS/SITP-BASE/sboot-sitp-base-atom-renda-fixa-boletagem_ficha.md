# Ficha Técnica do Sistema

---

## 1. Descrição Geral

Sistema atômico de consulta de transações ITP (Sistema de Pagamentos Brasileiro) para operações de Renda Fixa e Boletagem. O serviço expõe uma API REST que permite consultar códigos de transação com base no código do grupo de produto e tipo de lançamento, realizando consultas diretas no banco de dados Sybase.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application.java` | Classe principal Spring Boot que inicializa a aplicação |
| `TransacaoItpController.java` | Controlador REST que expõe o endpoint de consulta de transações |
| `TransacaoItpService.java` | Camada de serviço que implementa a lógica de negócio |
| `TransacaoItpRepository.java` | Interface de repositório (port) |
| `JdbiTransacaoItpRepositoryImpl.java` | Implementação do repositório usando JDBI |
| `TransacaoItp.java` | Entidade de domínio representando uma transação ITP |
| `JdbiConfiguration.java` | Configuração do JDBI e beans de repositório |
| `OpenApiConfiguration.java` | Configuração do Swagger/OpenAPI para documentação |

---

## 3. Tecnologias Utilizadas

- **Framework**: Spring Boot 2.x
- **Linguagem**: Java 11
- **Persistência**: JDBI 3.9.1
- **Banco de Dados**: Sybase ASE (jConnect 16.3)
- **Documentação API**: Swagger/Springfox 2.9.2
- **Segurança**: Spring Security OAuth2 com JWT
- **Monitoramento**: Spring Actuator + Micrometer + Prometheus
- **Visualização**: Grafana
- **Build**: Maven
- **Container**: Docker (OpenJDK 11 com OpenJ9)
- **Logging**: Logback com suporte a JSON
- **Auditoria**: BV Audit 2.2.1
- **Pool de Conexões**: HikariCP

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/transacao-itp/consultar/{codigoGrupoProduto}/{tipoLancamento}` | `TransacaoItpController` | Consulta código de transação ITP baseado no grupo de produto e tipo de lançamento |

---

## 5. Principais Regras de Negócio

1. **Consulta de Transação ITP**: O sistema busca o código de transação SPB (Sistema de Pagamentos Brasileiro) com base em dois parâmetros:
   - Código do Grupo de Produto (ex: 11)
   - Tipo de Lançamento (ex: "E" para entrada)

2. **Validação de Entrada**: Os parâmetros são obrigatórios e validados via path variables

3. **Tratamento de Erros**: Exceções são capturadas e retornam HTTP 500 com log de erro

---

## 6. Relação entre Entidades

**Entidade Principal:**
- `TransacaoItp`: Contém apenas o atributo `codigoTransacao` (Long)

**Relacionamentos:**
- Não há relacionamentos entre entidades. O sistema trabalha com uma única entidade simples que representa o resultado da consulta.

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TBL_DESCRICAO_TRANSACAO_SPB | Tabela | SELECT | Tabela que armazena as descrições e códigos de transações do Sistema de Pagamentos Brasileiro, relacionando grupos de produtos com tipos de lançamento |

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema realiza apenas operações de leitura (consulta).

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | Spring Boot | Arquivo de configuração principal da aplicação |
| application-local.yml | Leitura | Spring Boot | Configurações específicas para ambiente local |
| logback-spring.xml | Leitura | Logback | Configuração de logs da aplicação |
| getCodigoTransacao.sql | Leitura | JdbiTransacaoItpRepositoryImpl | Query SQL para consulta de transações |

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
| Banco Sybase DBITP | Banco de Dados | Conexão com banco Sybase para consulta de transações ITP |
| API Gateway OAuth2 | Autenticação | Validação de tokens JWT via JWK (JSON Web Key) do API Gateway |
| Prometheus | Monitoramento | Exportação de métricas da aplicação |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7.5/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura hexagonal bem definida (domain, port, infrastructure)
- Separação clara de responsabilidades entre camadas
- Uso de JDBI com SQL externalizado em arquivos
- Configuração adequada de segurança OAuth2
- Implementação de observabilidade (Actuator, Prometheus, Grafana)
- Uso de Lombok para reduzir boilerplate
- Documentação via Swagger/OpenAPI

**Pontos de Melhoria:**
- Tratamento de exceções genérico no controller (apenas Exception)
- Falta de validação de parâmetros de entrada
- Ausência de DTOs específicos para request/response
- Configuração de OAuth2 com credenciais hardcoded no código
- Falta de testes unitários e de integração nos arquivos enviados
- Logs poderiam ser mais estruturados e informativos
- Ausência de cache para consultas frequentes
- Falta de documentação inline (JavaDoc)

---

## 14. Observações Relevantes

1. **Ambiente Multi-Plataforma**: O sistema está preparado para deploy em múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas via ConfigMaps e Secrets do Kubernetes/OpenShift.

2. **Monitoramento Completo**: Infraestrutura de observabilidade robusta com Prometheus e Grafana, incluindo dashboards pré-configurados para métricas de JVM, HTTP, HikariCP e logs.

3. **Segurança**: Implementa autenticação via OAuth2 com JWT, integrado ao API Gateway do Banco Votorantim.

4. **Performance**: Utiliza HikariCP para pool de conexões e OpenJ9 JVM para otimização de memória.

5. **Banco de Dados Legacy**: Integração com Sybase ASE, sistema legado, com configurações específicas de charset e parâmetros de conexão.

6. **Arquitetura Atômica**: Segue o padrão de microserviços atômicos do Banco Votorantim, com estrutura modular (common, domain, application).

7. **CI/CD**: Preparado para pipeline Jenkins com propriedades específicas e deploy em plataforma Google Cloud (conforme jenkins.properties).

8. **Limitações**: Sistema muito específico e simples, realizando apenas uma operação de consulta. Não há operações de escrita, processamento complexo ou integrações com outros sistemas além do banco de dados.