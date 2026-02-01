# Ficha Técnica do Sistema

## 1. Descrição Geral

O **Notification Service** é um microsserviço responsável por gerenciar notificações de pagamentos para clientes Fintech, BaaS (Banking as a Service) e Wallet. O sistema oferece APIs REST para inserção, consulta e atualização de notificações de transações financeiras, incluindo operações de cash-in, cash-out e callbacks. Implementa validações de segurança (JWT, mTLS), controle de protocolo de notificações, tratamento de erros e devoluções, além de integração com feature toggles para controle de funcionalidades por ambiente.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **NotificationServiceController** | Controller REST que expõe endpoints para operações de notificação (inserir, consultar, atualizar) |
| **NotificationServiceService** | Serviço principal contendo regras de negócio: validações de cliente, hash, expiração, tipos de notificação |
| **NotificationServiceRepositoryImpl** | Repositório de acesso a dados de notificações usando JDBI, executa queries SQL complexas |
| **ClientRepositoryImpl** | Repositório para consulta de dados de clientes por CPF/CNPJ |
| **NotificationProtocolOperationRepository** | Repositório JPA para operações com entidade Lancamento (protocolo de pagamento) |
| **FeatureToggleService** | Serviço para consulta de feature flags (ConfigCat) |
| **NotificationEntryMapper** | Mapeia entidade Lancamento para NotificationEntry, incluindo lógica de reverso |
| **ExceptionControllerHandler** | Tratador global de exceções REST, retorna respostas padronizadas de erro |
| **JdbiConfiguration** | Configuração de beans JDBI para acesso ao banco de dados |
| **ModelMapperConfiguration** | Configuração do ModelMapper para conversão entre entidades e representations |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (Spring MVC, Spring Security OAuth2)
- **JDBI 3.x** (acesso a dados SQL)
- **JPA/Hibernate** (entidades de domínio)
- **SQL Server** (banco de dados DBSPAG)
- **Sybase jConnect** (driver adicional)
- **Swagger/OpenAPI 3** (documentação de API)
- **Spring Actuator** (health checks, métricas)
- **Prometheus/Grafana** (observabilidade)
- **ConfigCat** (feature toggles)
- **JWT** (autenticação/autorização)
- **mTLS** (autenticação mutual TLS para parceiros)
- **Maven** (build multi-módulo)
- **Docker** (containerização)
- **OpenShift/Kubernetes** (deploy)
- **Logback** (logs em formato JSON)
- **Pact** (testes de contrato)
- **RestAssured** (testes funcionais)
- **Mockito/JUnit** (testes unitários)
- **ArchUnit** (testes de arquitetura)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/notificacao` | NotificationServiceController | Insere nova notificação de pagamento |
| POST | `/notificacao/controle` | NotificationServiceController | Insere controle de retorno de notificação |
| POST | `/notificacao/erro` | NotificationServiceController | Registra erro de notificação |
| PUT | `/notificacao/flag` | NotificationServiceController | Atualiza flag de notificação |
| PUT | `/notificacao/data` | NotificationServiceController | Atualiza data de notificação |
| GET | `/notificacao/evento` | NotificationServiceController | Busca eventos de notificação |
| GET | `/notificacao/parametros` | NotificationServiceController | Busca parâmetros de notificação |
| GET | `/notificacao/cashIn` | NotificationServiceController | Busca dados de cash-in |
| GET | `/notificacao/cashOut` | NotificationServiceController | Busca dados de cash-out |
| GET | `/notificacao/callback` | NotificationServiceController | Busca dados de callback |
| GET | `/notificacao/endpoint` | NotificationServiceController | Busca endpoint Fintech |
| GET | `/notificacao/detalhe` | NotificationServiceController | Consulta detalhe de notificação |
| POST | `/notificacao/parceiro` | NotificationServiceController | Notifica parceiro |
| POST | `/notificacao/wallet` | NotificationServiceController | Notifica wallet |
| GET | `/notificacao/protocolo/{protocolo}` | NotificationServiceController | Lista notificações por protocolo |
| GET | `/notificacao/data` | NotificationServiceController | Lista notificações por período |

---

## 5. Principais Regras de Negócio

1. **Validação de Cliente**: Verifica se o CNPJ/CPF do cliente está cadastrado e ativo antes de processar notificação
2. **Validação de Hash e Expiração**: Valida hash de protocolo e verifica se não expirou (baseado em validade configurada em AppPropertiesFintech)
3. **Determinação de Tipo de Notificação**: Classifica notificação como FullBaas, Wallet ou Fintech baseado em dados do cliente
4. **Validação de JWT**: Extrai e valida clientId do token JWT para autorização
5. **Feature Toggle para URL CashOut**: Valida URL de cashOut apenas se feature toggle estiver ativa
6. **Tratamento de Reverso**: Identifica e processa transações de devolução/reverso com códigos específicos (1-108)
7. **Controle de Retorno**: Registra tentativas de notificação e respostas recebidas
8. **Registro de Erros**: Captura e persiste erros ocorridos durante processamento de notificações
9. **Consulta de Quantidade de Notificações**: Retorna contagem de notificações por protocolo
10. **Autenticação mTLS**: Habilita autenticação mutual TLS para parceiros específicos via feature toggle
11. **Validação de Participantes**: Seleciona debtor ou creditor correto baseado no tipo de lançamento
12. **Controle de Status**: Gerencia status de lançamento (processamento, sucesso, erro, aguardando, devolvido)

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **TbLancamento**: Representa um lançamento/pagamento (chave primária: protocolo)
  - Relaciona-se com **TbLancamentoPessoa** (1:N) - dados de participantes (debtor/creditor)
  - Relaciona-se com **TbLancamentoClienteFintech** (1:N) - dados Fintech dos participantes
  - Relaciona-se com **TbNotificacaoErroFintech** (1:N) - erros de notificação

- **TbNotificacaoFintech**: Registro de notificação enviada
  - Relaciona-se com **TbControleRetornoNotificacao** (1:N) - controle de tentativas e respostas
  - Relaciona-se com **TbEventoNotificacao** (N:1) - tipo de evento notificado

- **TbContaUsuarioFintech**: Conta de usuário Fintech
  - Relaciona-se com **TbUsuarioContaFintech** (1:1)
  - Relaciona-se com **TbRelacaoContaUsuarioFintech** (1:N)

- **TbParametroPagamentoFintech**: Parâmetros de configuração
  - Relaciona-se com **TbValidacaoOrigemPagamento** (1:N)
  - Relaciona-se com **TbContaPagamentoFintech** (1:N)

**Relacionamentos:**
- Lancamento → LancamentoPessoa (1:N): Um lançamento possui múltiplos participantes
- Lancamento → NotificacaoErroFintech (1:N): Um lançamento pode ter múltiplos erros
- NotificacaoFintech → ControleRetornoNotificacao (1:N): Uma notificação pode ter múltiplas tentativas

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbLancamento | Tabela | SELECT | Lançamentos/pagamentos com dados de transação |
| TbLancamentoPessoa | Tabela | SELECT | Dados de participantes (debtor/creditor) |
| TbLancamentoClienteFintech | Tabela | SELECT | Dados Fintech dos participantes |
| TbNotificacaoFintech | Tabela | SELECT | Histórico de notificações enviadas |
| TbControleRetornoNotificacao | Tabela | SELECT | Controle de retornos de notificações |
| TbNotificacaoErroFintech | Tabela | SELECT | Erros de notificação |
| TbEventoNotificacao | Tabela | SELECT | Tipos de eventos de notificação |
| TbParametroPagamentoFintech | Tabela | SELECT | Parâmetros de configuração |
| TbValidacaoOrigemPagamento | Tabela | SELECT | Validações de origem de pagamento |
| TbContaPagamentoFintech | Tabela | SELECT | Contas de pagamento Fintech |
| TbOrigemPagamentoMultiplaConta | Tabela | SELECT | Origens com múltiplas contas |
| TbConsultaDebitoVeicular | Tabela | SELECT | Consultas de débito veicular |
| TbContaUsuarioFintech | Tabela | SELECT | Contas de usuários Fintech |
| TbUsuarioContaFintech | Tabela | SELECT | Usuários de contas Fintech |
| TbRelacaoContaUsuarioFintech | Tabela | SELECT | Relação entre contas e usuários |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbNotificacaoFintech | Tabela | INSERT | Inserção de novas notificações |
| TbNotificacaoFintech | Tabela | UPDATE | Atualização de flags e datas de notificação |
| TbControleRetornoNotificacao | Tabela | INSERT | Inserção de controle de retorno |
| TbNotificacaoErroFintech | Tabela | INSERT | Inserção de erros de notificação |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | Spring Boot Config | Configurações por ambiente (datasource, security, actuator) |
| logback-spring.xml | Leitura | Logback | Configuração de logs JSON por ambiente |
| jwks.json | Leitura | Spring Security OAuth2 | Chaves públicas para validação JWT |
| queries SQL (resources) | Leitura | NotificationServiceRepositoryImpl | Queries SQL externalizadas |
| infra.yml | Leitura | OpenShift/Kubernetes | Configuração de infraestrutura e deploy |
| Logs JSON | Gravação | Logback Appender | Logs da aplicação em formato JSON |

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
| **ConfigCat** | Feature Toggle | Consulta de feature flags para controle de funcionalidades (mTLS, validação cashOut) |
| **OAuth2 Authorization Server** | Autenticação | Validação de tokens JWT via jwks.json |
| **Parceiros Fintech** | API REST | Envio de notificações via callbacks configurados (URLs parametrizadas) |
| **Wallet** | API REST | Envio de notificações para sistema Wallet |
| **FullBaas** | API REST | Envio de notificações para sistema FullBaas |
| **Prometheus** | Observabilidade | Exportação de métricas via /actuator/prometheus |
| **Grafana** | Observabilidade | Visualização de métricas e dashboards |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada em camadas (controller, service, repository, domain)
- Separação clara de responsabilidades com uso de padrões (Repository, Service, Mapper)
- Externalização de queries SQL em arquivos de recursos, facilitando manutenção
- Uso adequado de DTOs/Representations para separar modelo de domínio de API
- Configuração robusta de segurança (OAuth2, JWT, mTLS)
- Boa cobertura de testes (unitários, integração, contrato, funcionais, arquitetura)
- Observabilidade bem implementada (Actuator, Prometheus, logs estruturados JSON)
- Documentação de API com Swagger/OpenAPI
- Feature toggles para controle de funcionalidades por ambiente
- Uso de profiles Spring para diferentes ambientes

**Pontos de Melhoria:**
- Algumas classes de mapper possuem lógica complexa que poderia ser melhor documentada
- Nomenclatura de algumas tabelas poderia seguir padrão mais consistente
- Alguns métodos de serviço são extensos e poderiam ser refatorados em métodos menores
- Falta documentação inline (JavaDoc) em algumas classes críticas de negócio

---

## 14. Observações Relevantes

1. **Multi-módulo Maven**: Projeto estruturado em 3 módulos (common, domain, application) facilitando reuso e separação de concerns

2. **Feature Toggles Críticos**:
   - `ft_boolean_spag_base_mtls_toggle`: Habilita/desabilita autenticação mTLS
   - `ft_string_spag_base_mtls_toggle`: Lista de parceiros que utilizam mTLS
   - Feature toggle para validação de URL cashOut

3. **Segurança em Camadas**:
   - OAuth2 com JWT para autenticação de APIs
   - mTLS para parceiros específicos
   - Validação de hash e expiração de protocolo
   - Validação de clientId no token

4. **Ambientes**: Suporta 5 ambientes (local, des, qa, uat, prd) com configurações específicas

5. **Banco de Dados**: SQL Server (DBSPAG) com uso híbrido de JDBI (queries complexas) e JPA (entidades de domínio)

6. **Portas**:
   - 8080: API REST e Swagger UI
   - 9090: Actuator (health checks e métricas)

7. **Correções de Segurança**: Projeto inclui overrides de dependências para correção de CVEs conhecidos (spring-security-web 5.7.13, tomcat-embed-core 9.0.104)

8. **CI/CD**: Integração com Jenkins usando plataforma Google e deploy em OpenShift

9. **Recursos Kubernetes**: Configuração de liveness/readiness probes, limits/requests de CPU e memória, volumes para certificados e datasources

10. **Auditoria**: Integração com trilha-auditoria-web para registro de operações

11. **Validação de Protocolo**: Sistema valida validade de protocolo Fintech configurável via AppPropertiesFintech

12. **Tipos de Conta Suportados**: CI, IF, PP, CO, CC, CT, PG (enum TipoContaEnum)

13. **Códigos de Reverso**: Suporta 108 códigos diferentes de motivos de devolução (enum ReverseEnum)