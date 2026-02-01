# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-spag-base-atom-callback-parceiro** é um serviço atômico desenvolvido em Spring Boot que gerencia callbacks de parceiros/fintechs. Sua principal função é registrar e controlar retornos de solicitações enviadas para parceiros externos, mantendo um histórico de notificações e controles de retorno. O sistema expõe APIs REST para inserção e atualização de dados relacionados a retornos de solicitações e controles de callback.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal que inicializa a aplicação Spring Boot com segurança OAuth2 |
| **CallbackParceiroController** | Controlador REST que expõe endpoints para gerenciar retornos de solicitação e controles de retorno |
| **CallbackParceiroService** | Serviço de domínio que implementa a lógica de negócio para inserção e atualização de callbacks |
| **CallbackParceiroRepository** | Interface de repositório que define operações de persistência |
| **CallbackParceiroRepositoryImpl** | Implementação do repositório usando JDBI para acesso ao banco de dados |
| **RetornoSolicitacao** | Entidade de domínio que representa um retorno de solicitação de fintech |
| **ControleRetorno** | Entidade de domínio que representa o controle de retorno de callback |
| **CallbackParceiroConfiguration** | Configuração de beans do Spring para injeção de dependências |
| **JdbiConfiguration** | Configuração do JDBI para acesso ao banco de dados |
| **CustomControllerAdvice** | Tratamento centralizado de exceções da aplicação |
| **OpenApiConfiguration** | Configuração do Swagger/OpenAPI para documentação das APIs |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.x** - Framework principal
- **Spring Security OAuth2** - Autenticação e autorização via JWT
- **JDBI 3.9.1** - Framework de acesso a banco de dados
- **Microsoft SQL Server** - Banco de dados relacional
- **Swagger/Springfox 2.9.2** - Documentação de APIs
- **Lombok** - Redução de código boilerplate
- **Micrometer/Prometheus** - Métricas e monitoramento
- **Logback** - Sistema de logs
- **JUnit 5 + Mockito** - Testes unitários
- **Pact** - Testes de contrato
- **Docker** - Containerização
- **Maven** - Gerenciamento de dependências e build
- **Grafana** - Visualização de métricas

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/callback-parceiro/retornoSolicitacao | CallbackParceiroController | Insere um novo retorno de solicitação de fintech |
| POST | /v1/callback-parceiro/controleRetorno | CallbackParceiroController | Insere um novo controle de retorno de callback |
| PUT | /v1/callback-parceiro/controleRetorno/{id} | CallbackParceiroController | Atualiza um controle de retorno existente pelo ID |

---

## 5. Principais Regras de Negócio

- **Registro de Retorno de Solicitação**: O sistema permite registrar retornos de solicitações enviadas para parceiros/fintechs, incluindo informações como URL do parceiro, protocolo de origem, mensagem, código de lançamento e liquidação.

- **Controle de Retorno de Callback**: Mantém controle sobre os retornos recebidos, associando-os a notificações de fintech, com código e descrição de retorno, origem da chamada e usuário responsável.

- **Auditoria Automática**: Todos os registros incluem campos de auditoria (data de inclusão, data de alteração, login do usuário, flag ativo) gerenciados automaticamente pelo banco de dados.

- **Tratamento de Exceções**: Exceções são tratadas centralizadamente, retornando respostas HTTP apropriadas (404 para NullPointer, 422 para erros de SQL, 500 para erros gerais).

---

## 6. Relação entre Entidades

**RetornoSolicitacao** (Tabela: TbRetornoSolicitacaoFintech)
- Representa o retorno de uma solicitação enviada para fintech
- Campos principais: cdRetornoSolicitacaoFintech (PK), dsURLParceiroFintech, dsLoginUsuarioFintech, dsProtocoloOrigem, dsMensagem, cdLancamento, cdLiquidacao, dtRetornoSolicitacaoFintech

**ControleRetorno** (Tabela: TbControleRetornoSlctoFintech)
- Controla os retornos de callbacks
- Campos principais: cdControleRetornoCallback (PK), cdNotificacaoFintech (FK para RetornoSolicitacao), cdRetorno, dsRetorno, cdOrigemChamada

**Relacionamento**: ControleRetorno referencia RetornoSolicitacao através do campo cdNotificacaoFintech (relacionamento 1:N - um retorno de solicitação pode ter múltiplos controles de retorno).

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| não se aplica | - | - | O sistema não realiza operações de leitura explícitas |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbRetornoSolicitacaoFintech | tabela | INSERT | Insere novos registros de retorno de solicitação de fintech |
| TbControleRetornoSlctoFintech | tabela | INSERT | Insere novos registros de controle de retorno de callback |
| TbControleRetornoSlctoFintech | tabela | UPDATE | Atualiza registros existentes de controle de retorno |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | leitura | /usr/etc/log (ambientes) ou classpath (local) | Arquivo de configuração de logs em formato JSON |
| application.yml | leitura | classpath | Arquivo de configuração da aplicação Spring Boot |

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
| API Gateway BV | Autenticação | Validação de tokens JWT através do endpoint jwks.json para autenticação OAuth2 |
| SQL Server (DBSPAG) | Banco de Dados | Persistência de dados de callbacks e controles de retorno |
| Prometheus | Monitoramento | Exportação de métricas da aplicação para monitoramento |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7.5/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem organizada seguindo padrões hexagonais (domain, application, infrastructure)
- Separação clara de responsabilidades entre camadas
- Uso adequado de injeção de dependências
- Implementação de testes unitários e de integração
- Configuração de segurança OAuth2 implementada
- Documentação via Swagger configurada
- Uso de Lombok para reduzir boilerplate
- Tratamento centralizado de exceções

**Pontos de Melhoria:**
- Falta de validações de entrada nos endpoints (Bean Validation)
- Ausência de logs estruturados nas operações de negócio
- Testes unitários com cobertura limitada (classes de teste vazias)
- Falta de documentação inline (JavaDoc) nas classes principais
- Tratamento de exceções genérico poderia ser mais específico
- Ausência de DTOs específicos para requests/responses (uso direto de Representations)
- Configurações de banco de dados com credenciais em texto plano no application.yml (ambiente local)

---

## 14. Observações Relevantes

1. **Ambiente Multi-Profile**: A aplicação suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas para cada um.

2. **Segurança**: Implementa autenticação OAuth2 com JWT, mas os endpoints não possuem anotações de autorização específicas (@PreAuthorize).

3. **Monitoramento**: Infraestrutura completa de observabilidade com Prometheus e Grafana configurados, incluindo dashboards pré-configurados.

4. **Auditoria**: Utiliza biblioteca de trilha de auditoria do Banco Votorantim (springboot-arqt-base-trilha-auditoria-web).

5. **Containerização**: Dockerfile otimizado usando OpenJ9 com configurações de memória ajustáveis via variáveis de ambiente.

6. **CI/CD**: Configuração para Jenkins com propriedades específicas (jenkins.properties) e infraestrutura como código (infra.yml).

7. **Pool de Conexões**: Utiliza HikariCP para gerenciamento de conexões com o banco de dados.

8. **Timestamps Automáticos**: O banco de dados gerencia automaticamente os campos de data (dtInclusao, dtAlteracao) usando CURRENT_TIMESTAMP.

9. **Arquitetura de Testes**: Estrutura bem definida separando testes unitários, de integração e funcionais em diretórios distintos.

10. **Versionamento de API**: Endpoints versionados com prefixo /v1/, facilitando evolução futura da API.