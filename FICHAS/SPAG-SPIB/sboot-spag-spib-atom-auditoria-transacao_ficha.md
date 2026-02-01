# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-spag-spib-atom-auditoria-transacao** é um serviço atômico desenvolvido em Java com Spring Boot, responsável por registrar e consultar auditorias de transações do sistema PIX (Sistema de Pagamentos Instantâneos Brasileiro). O sistema armazena informações detalhadas sobre requisições e respostas de transações PIX, incluindo dados de certificados digitais, headers HTTP, URLs, identificadores de mensagens e metadados de transações tanto do SPI (Sistema de Pagamentos Instantâneos) quanto do DICT (Diretório de Identificadores de Contas Transacionais).

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal que inicializa a aplicação Spring Boot com segurança OAuth2 |
| `AuditTransactionController` | Controlador REST para operações de auditoria de transações (inserção, atualização e consulta) |
| `DictAuditTransactionController` | Controlador REST específico para auditorias de transações do DICT |
| `AuditTransactionService` | Serviço de domínio que implementa regras de negócio para auditoria de transações |
| `AuditDictTransactionService` | Serviço de domínio para auditoria de transações DICT |
| `JdbiAuditTransactionRepository` | Repositório de acesso a dados usando JDBI para transações de auditoria |
| `JdbiAuditDictTransactionRepository` | Repositório de acesso a dados usando JDBI para transações DICT |
| `AuditTransaction` | Entidade de domínio representando uma auditoria de transação |
| `AuditDictTransaction` | Entidade de domínio representando uma auditoria de transação DICT |
| `AuditTransactionMapper` | Mapper para conversão entre representações e domínio de auditoria |
| `AuditDictTransactionMapper` | Mapper para conversão de auditorias DICT com tratamento de truncamento de headers |
| `AuditTransactionRowMapper` | Mapper JDBI para conversão de ResultSet em entidades de domínio |
| `AuditoriaTransacaoConfiguration` | Configuração de beans do Spring (JDBI, repositórios, serviços, ModelMapper) |
| `OpenApiConfiguration` | Configuração do Swagger/OpenAPI para documentação da API |
| `Validate` | Classe utilitária para validações de campos |
| `ValidationException` | Exception customizada para erros de validação |
| `ErrorMessage` | Classe para padronização de mensagens de erro |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot** (framework principal)
- **Spring Security OAuth2** (autenticação e autorização via JWT)
- **JDBI 3.9.1** (acesso a banco de dados)
- **SQL Server** (banco de dados)
- **Swagger/Springfox 3.0.0** (documentação de API)
- **Lombok** (redução de boilerplate)
- **ModelMapper 3.1.0** (mapeamento de objetos)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **RabbitMQ** (mensageria - configurado mas não utilizado no código analisado)
- **Micrometer/Prometheus** (métricas e monitoramento)
- **JUnit 5** (testes unitários)
- **Mockito** (mocks para testes)
- **Rest Assured** (testes funcionais)
- **Pact** (testes de contrato)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/audit-transaction` | `AuditTransactionController` | Insere um novo registro de auditoria de transação |
| PUT | `/v1/audit-transaction?auditId={id}` | `AuditTransactionController` | Atualiza um registro de auditoria existente |
| GET | `/v1/audit-transaction?auditId={id}` | `AuditTransactionController` | Consulta auditoria por ID |
| GET | `/v1/audit-transaction/{message_type}/{end_to_end_identification}/{original_instruction_identification}/{message_flow}` | `AuditTransactionController` | Consulta auditoria por parâmetros de mensagem |
| POST | `/dict/audit-transaction` | `DictAuditTransactionController` | Insere registros de auditoria DICT (request e response) |

---

## 5. Principais Regras de Negócio

1. **Validação de campos obrigatórios**: Os campos `logDateTime` e `messageLogType` são obrigatórios para inserção de auditoria
2. **Restrição de ID em inserção**: O campo `auditId` deve ser nulo ao inserir uma nova auditoria (gerado automaticamente pelo banco)
3. **Truncamento de headers HTTP**: Headers HTTP maiores que 700 caracteres são truncados automaticamente para evitar estouro de coluna no banco de dados
4. **Auditoria dupla para DICT**: Para transações DICT, são registradas duas auditorias separadas (uma para request e outra para response)
5. **Conversão de timestamps**: Timestamps são convertidos para formato ISO-8601 com timezone UTC
6. **Tratamento de erros**: Erros de inserção são logados mas não impedem o fluxo da aplicação (retorna BAD_REQUEST)
7. **Consulta por múltiplos critérios**: Permite buscar auditorias por tipo de mensagem, end-to-end ID, instruction ID e fluxo de mensagem

---

## 6. Relação entre Entidades

**Entidades principais:**

- **AuditTransaction**: Entidade principal de auditoria contendo informações completas de uma transação (ID, timestamps, certificados, headers HTTP, URLs, tipos de mensagem, identificadores PIX)

- **AuditDictTransaction**: Entidade específica para auditorias DICT, contendo informações de correlação, participantes, recursos PIX e dois objetos AuditXml (request e response)

- **AuditXml**: Entidade auxiliar que encapsula informações de certificado, headers HTTP, URL, UUID do FileNet e fluxo de mensagem

- **DTOAuditDictTransaction**: DTO para transferência de dados de auditoria DICT, versão "achatada" sem objetos aninhados

**Relacionamentos:**
- `AuditDictTransaction` possui dois `AuditXml` (xmlRequest e xmlResponse)
- `DTOAuditDictTransaction` é uma representação plana de `AuditDictTransaction` para persistência

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| `SPAGAuditoriaBacen.transactional_audit` | Tabela | SELECT | Consulta de registros de auditoria de transações por ID ou por critérios de mensagem (message_type, end_to_end_id, original_instruction_id, message_flow) |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| `SPAGAuditoriaBacen.transactional_audit` | Tabela | INSERT | Inserção de novos registros de auditoria de transações com todos os campos (log_datetime, message_log_type, certificados, headers HTTP, URLs, tipos de mensagem, identificadores) |
| `SPAGAuditoriaBacen.transactional_audit` | Tabela | UPDATE | Atualização de registros existentes de auditoria por ID |
| `SPAGAuditoriaBacen.audit_transactional_dict` | Tabela | INSERT | Inserção de registros de auditoria específicos para transações DICT, incluindo correlation_id, participantes, recursos PIX, certificados, headers, URLs e timestamps |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `application.yml` | Leitura | Spring Boot | Arquivo de configuração da aplicação contendo datasources, profiles, segurança OAuth2 e configurações de pool de conexões |
| `logback-spring.xml` | Leitura | Logback | Configuração de logs em formato JSON para stdout com níveis configuráveis por pacote |
| `sboot-auditoria-transacao.yaml` | Leitura | Swagger Codegen | Especificação OpenAPI 2.0 usada para gerar interfaces de API automaticamente |
| Arquivos SQL (*.sql) | Leitura | JDBI | Queries SQL parametrizadas para operações de banco (insert, update, select) carregadas via classpath |

---

## 10. Filas Lidas

Não se aplica. Embora o projeto tenha configuração de RabbitMQ no docker-compose, não há consumo de filas implementado no código analisado.

---

## 11. Filas Geradas

Não se aplica. Não há publicação de mensagens em filas implementada no código analisado.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **Servidor OAuth2/JWT** | API REST | Integração para validação de tokens JWT via endpoint `/openid/connect/jwks.json` configurado por ambiente (des, qa, uat, prd) |
| **SQL Server** | Banco de Dados | Conexão JDBC com banco de dados SQL Server (DBSPAG1) em diferentes ambientes com credenciais gerenciadas por cofre de senhas |
| **FileNet** | Sistema de Arquivos | Referenciado através do campo `fileNetUuId` para armazenamento de documentos base64, mas sem integração direta no código |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem organizada seguindo padrões hexagonais (domain, application, common)
- Separação clara de responsabilidades entre camadas
- Uso adequado de padrões como Repository, Service e Mapper
- Boa cobertura de testes unitários
- Uso de Lombok reduzindo boilerplate
- Configuração externalizada e por ambiente
- Documentação OpenAPI/Swagger
- Uso de validações customizadas
- Tratamento de casos especiais (truncamento de headers)

**Pontos de Melhoria:**
- Tratamento de exceções genérico em alguns pontos (catch Exception)
- Logs de erro sem contexto suficiente em alguns casos
- Falta de validações mais robustas em alguns endpoints
- Código de testes com alguns mocks desnecessários
- Ausência de testes de integração mais completos
- Algumas classes de configuração poderiam ser mais modulares
- Falta de documentação inline em métodos mais complexos
- Conversão de timestamps poderia ser mais centralizada
- Alguns métodos de mapper com lógica condicional que poderia ser extraída

O código demonstra boas práticas de desenvolvimento, mas há espaço para melhorias em tratamento de erros, validações e modularização.

---

## 14. Observações Relevantes

1. **Segurança**: O sistema utiliza OAuth2 com JWT para autenticação, com endpoints públicos configurados apenas para Swagger
2. **Multi-ambiente**: Configuração robusta para múltiplos ambientes (des, qa, uat, prd) com datasources e credenciais específicas
3. **Monitoramento**: Integração com Prometheus e Actuator para métricas e health checks
4. **Auditoria**: Sistema de auditoria próprio usando biblioteca `springboot-arqt-base-trilha-auditoria-web`
5. **Containerização**: Dockerfile otimizado usando OpenJ9 com configurações de memória parametrizadas
6. **Infraestrutura como Código**: Arquivo `infra.yml` com configurações completas para deploy em Kubernetes/OpenShift
7. **Geração de código**: Uso de Swagger Codegen para gerar automaticamente interfaces de API a partir da especificação OpenAPI
8. **Pool de conexões**: Configuração de HikariCP com tamanhos de pool específicos por ambiente
9. **Timezone**: Todas as datas são tratadas em UTC para consistência
10. **Versionamento de API**: Endpoints versionados com prefixo `/v1` e `/dict`
11. **Profiles Maven**: Suporte a diferentes perfis de teste (unit, integration, functional, architecture)
12. **ArchUnit**: Testes arquiteturais automatizados para garantir conformidade com padrões