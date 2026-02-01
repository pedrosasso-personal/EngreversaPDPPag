# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema atômico de notificação de pagamentos desenvolvido em Spring Boot. O sistema é responsável por gerenciar e enviar notificações de eventos de pagamento para parceiros/fintechs, controlando tentativas de envio, registrando erros e mantendo histórico de notificações. Suporta diferentes tipos de notificação (CashIn, CashOut, Callback) e integra-se com banco de dados SQL Server para persistência de dados.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `NotificaPagamentoService` | Serviço de domínio que orquestra as operações de notificação de pagamentos |
| `NotificaPagamentoController` | Controlador REST que expõe os endpoints da API |
| `NotificaPagamentoRepositoryImpl` | Implementação do repositório usando JDBI para acesso ao banco de dados |
| `NotificaPagamentoConfiguration` | Configuração principal da aplicação |
| `JdbiConfiguration` | Configuração do JDBI para acesso a dados |
| `OpenApiConfiguration` | Configuração do Swagger/OpenAPI para documentação |
| `ExceptionControllerHandler` | Tratamento centralizado de exceções |
| `NotificacaoPagamentoFintech` | Entidade de domínio representando notificação de pagamento |
| `ControleRetornoNotificacao` | Entidade de domínio para controle de retorno de notificações |
| `NotificacaoErroFintech` | Entidade de domínio para registro de erros de notificação |
| Diversos Mappers | Classes responsáveis por conversão entre entidades de domínio e representações REST |

## 3. Tecnologias Utilizadas

- **Framework Principal**: Spring Boot 2.x
- **Linguagem**: Java 11
- **Persistência**: JDBI 3.9.1
- **Banco de Dados**: Microsoft SQL Server (driver 7.4.0.jre11)
- **Documentação API**: Swagger/Springfox 3.0.0
- **Monitoramento**: Spring Boot Actuator + Micrometer + Prometheus
- **Visualização**: Grafana
- **Build**: Maven
- **Segurança**: Spring Security + JWT (bv-security 0.22.4)
- **Auditoria**: BV Audit 2.3.5
- **Testes**: JUnit 5, Mockito, Rest Assured, Pact
- **Serialização**: Gson
- **Utilitários**: Lombok
- **Container**: Docker

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/inserirNotificacaoFintech | NotificaPagamentoController | Insere dados de notificação de pagamento |
| POST | /v1/inserirControleRetornoNotificacao | NotificaPagamentoController | Insere retorno da notificação |
| POST | /v1/inserirNotificacaoErroFintech | NotificaPagamentoController | Insere erro de notificação |
| PUT | /v1/atualizarFlagAtivo | NotificaPagamentoController | Atualiza flag ativo de uma notificação |
| PUT | /v1/atualizarDataNotificacao | NotificaPagamentoController | Atualiza data de envio da notificação |
| GET | /v1/buscarEventoNotificacao/{cdEventoNotificacao} | NotificaPagamentoController | Consulta evento de notificação |
| GET | /v1/buscarNotificacao | NotificaPagamentoController | Consulta notificação por protocolo e evento |
| GET | /v1/buscarNotificacaoPorCodigo | NotificaPagamentoController | Consulta notificação por código |
| GET | /v1/buscarParametrosPagamentoFintech | NotificaPagamentoController | Consulta parâmetros da fintech |
| GET | /v1/buscarParametrosNotificacao | NotificaPagamentoController | Consulta parâmetros de notificação |
| GET | /v1/buscarDadosNotificacaoCashOut | NotificaPagamentoController | Consulta dados para notificação CashOut |
| GET | /v1/buscarDadosNotificacaoCashIn | NotificaPagamentoController | Consulta dados para notificação CashIn |
| GET | /v1/buscarDadosNotificacaoCallback | NotificaPagamentoController | Consulta dados para notificação Callback |
| GET | /v1/buscarEndPointFintech | NotificaPagamentoController | Consulta endpoint da fintech |
| GET | /v1/obterNotificacaoParceiroWalletTributos/{cdLiquidacao} | NotificaPagamentoController | Obtém notificação do parceiro wallet |

## 5. Principais Regras de Negócio

- **Controle de Tentativas**: Sistema controla quantidade de tentativas de envio de notificações por parceiro/fintech
- **Gestão de Status**: Mantém flag ativo/inativo para controlar ciclo de vida das notificações
- **Registro de Erros**: Captura e persiste erros de notificação para análise posterior
- **Controle de Retorno**: Registra retornos das notificações enviadas com código HTTP e origem da chamada
- **Validação de Sucesso**: Consulta quantidade de notificações bem-sucedidas e com erro por protocolo
- **Tipos de Notificação**: Suporta diferentes tipos (CashIn, CashOut, Callback) com configurações específicas
- **Atualização de Data**: Registra data/hora de envio das notificações
- **Parametrização por Parceiro**: Busca parâmetros específicos (URL, usuário, tentativas) por parceiro/fintech
- **Eventos de Notificação**: Gerencia diferentes eventos de notificação com configurações de segurança
- **Integração com Liquidação**: Relaciona notificações com códigos de liquidação e lançamento

## 6. Relação entre Entidades

**Entidades Principais:**

- **NotificacaoPagamentoFintech**: Entidade central que representa uma notificação de pagamento
  - Relaciona-se com EventoNotificacao (N:1)
  - Possui múltiplos ControleRetornoNotificacao (1:N)
  
- **ControleRetornoNotificacao**: Registra retornos de tentativas de notificação
  - Pertence a uma NotificacaoPagamentoFintech (N:1)
  
- **NotificacaoErroFintech**: Registra erros de notificação
  - Independente, mas relacionada conceitualmente com NotificacaoPagamentoFintech
  
- **EventoNotificacao**: Define tipos de eventos de notificação
  - Possui múltiplas NotificacaoPagamentoFintech (1:N)
  
- **DadosNotificacaoCallback/CashIn/CashOut**: Value Objects com dados específicos por tipo de notificação

- **EndPointFintech**: Contém informações de endpoint do parceiro

- **ParametroPagamentoFintech**: Parâmetros de configuração por fintech

- **NotificacaoWallet**: Dados de notificação para wallet/tributos

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbEventoNotificacao | Tabela | SELECT | Consulta eventos de notificação configurados |
| TbNotificacaoFintech | Tabela | SELECT | Consulta notificações de pagamento registradas |
| TbControleRetornoNotificacao | Tabela | SELECT | Consulta retornos de notificações (implícito nas queries) |
| TbParametroPagamentoFintech | Tabela | SELECT | Consulta parâmetros de configuração da fintech |
| TbParametroConsultaCliente | Tabela | SELECT | Consulta parâmetros de cliente para validação |
| TbValidacaoOrigemPagamento | Tabela | SELECT | Consulta dados de origem e validação de pagamento |
| TbOrigemPagamentoMultiplaConta | Tabela | SELECT | Consulta origem de pagamento com múltiplas contas |
| TbRelacaoLiquidacaoGrupo | Tabela | SELECT | Consulta relação entre liquidação e grupo |
| TbContaPagamentoFintech | Tabela | SELECT | Consulta contas de pagamento da fintech |
| TbLancamento | Tabela | SELECT | Consulta lançamentos de pagamento |
| TbLancamentoPessoa | Tabela | SELECT | Consulta pessoas relacionadas ao lançamento |
| TbStatusLancamento | Tabela | SELECT | Consulta status do lançamento |
| TbErroProcessamento | Tabela | SELECT | Consulta erros de processamento de pagamento |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbNotificacaoFintech | Tabela | INSERT | Insere nova notificação de pagamento |
| TbNotificacaoFintech | Tabela | UPDATE | Atualiza flag ativo e data de notificação |
| TbControleRetornoNotificacao | Tabela | INSERT | Insere controle de retorno de notificação |
| TbNotificacaoErroFintech | Tabela | INSERT | Insere registro de erro de notificação |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| *.sql (queries) | Leitura | NotificaPagamentoRepositoryImpl | Arquivos SQL com queries parametrizadas do JDBI |
| application.yml | Leitura | Spring Boot | Configurações da aplicação por ambiente |
| application-local.yml | Leitura | Spring Boot | Configurações específicas do ambiente local |
| logback-spring.xml | Leitura | Logback | Configuração de logs da aplicação |
| sboot-spag-base-atom-notifica-pagamento.yml | Leitura | Swagger | Especificação OpenAPI da API |

## 10. Filas Lidas

não se aplica

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Fintechs/Parceiros | HTTP REST | Envio de notificações de pagamento para endpoints configurados dos parceiros |
| SQL Server (DBSPAG) | JDBC | Banco de dados principal para persistência de notificações e configurações |
| Prometheus | HTTP | Exportação de métricas de monitoramento |
| API Gateway BV | OAuth2/JWT | Autenticação e autorização via JWT |

## 13. Avaliação da Qualidade do Código

**Nota: 7.5/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem organizada seguindo padrões hexagonais (domain, application, infrastructure)
- Separação clara de responsabilidades entre camadas
- Uso adequado de padrões como Repository, Service, Mapper
- Boa cobertura de testes unitários, integração e funcionais
- Documentação OpenAPI completa
- Uso de Lombok reduzindo boilerplate
- Configuração adequada de monitoramento (Actuator, Prometheus, Grafana)
- Tratamento centralizado de exceções

**Pontos de Melhoria:**
- Alguns mappers poderiam usar MapStruct ao invés de conversões manuais com Gson
- Queries SQL embutidas em arquivos separados (bom), mas poderiam usar JPA/Hibernate para maior abstração
- Falta de validação de entrada em alguns endpoints (Bean Validation)
- Comentários em português misturados com código em inglês
- Algumas classes de teste com setup manual que poderia usar @TestConfiguration
- Segurança OAuth2 comentada na classe Application (possível código morto)
- Dependências com versões antigas que podem ter vulnerabilidades conhecidas

## 14. Observações Relevantes

- O sistema utiliza JDBI ao invés de JPA/Hibernate, o que oferece mais controle sobre SQL mas requer mais código manual
- Há infraestrutura completa de observabilidade com Prometheus e Grafana configurados
- O projeto segue padrões do Banco Votorantim com bibliotecas customizadas (bv-security, bv-audit)
- Existe estrutura para testes de contrato com Pact, mas não há implementação efetiva
- O sistema está preparado para deployment em OpenShift/Kubernetes (infra-as-code)
- Há configuração de múltiplos ambientes (local, des, qa, uat, prd)
- O código possui testes de arquitetura com ArchUnit para validar padrões
- Sistema utiliza profile spring para diferentes ambientes
- Há dependências com vulnerabilidades conhecidas que devem ser atualizadas (Spring Security 5.7.13, Tomcat 9.0.x)