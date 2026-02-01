# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de gerenciamento de contas Fintech para o Banco Votorantim (SPAG - Sistema de Pagamentos). O sistema é responsável por operações de abertura, encerramento, bloqueio/desbloqueio de contas de usuários Fintech, além de implementar mecanismos de validação e circuit breaker para controle de transações. Trata-se de um microserviço atômico desenvolvido em arquitetura RESTful.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal de inicialização da aplicação Spring Boot |
| `UsuarioFintechController` | Controller REST para operações de conta Fintech (abertura, encerramento, bloqueio/desbloqueio) |
| `CircuitBreakerController` | Controller REST para validação de circuit breaker em transações |
| `FintechService` | Serviço principal contendo lógica de negócio para operações de conta Fintech |
| `UsuarioFintechService` | Serviço para gerenciamento de usuários Fintech e protocolos |
| `ContaService` | Serviço para operações relacionadas a contas de usuários |
| `CallbackService` | Serviço para comunicação com sistemas parceiros via callback |
| `FeatureToggleService` | Serviço para gerenciamento de feature toggles e validações de circuit breaker |
| `FintechValidate` | Classe de validação de regras de negócio para operações Fintech |
| `EncerramentoValidate` | Validações específicas para encerramento de contas |
| `CpfCnpjValidate` | Validação de documentos CPF/CNPJ |
| `UsuarioFintechRepository` | Interface de acesso a dados de usuários Fintech |
| `ContaRepository` | Interface de acesso a dados de contas |
| `ClienteRepository` | Interface de acesso a dados de clientes |

## 3. Tecnologias Utilizadas

- **Framework:** Spring Boot 2.x (baseado no parent pom-atle-base-sboot-atom-parent 2.5.8)
- **Linguagem:** Java 11
- **Persistência:** JDBI 3.19.0 (SQL Object)
- **Banco de Dados:** Microsoft SQL Server (driver mssql-jdbc 12.8.1.jre11)
- **Segurança:** Spring Security OAuth2 Resource Server com JWT
- **Cache:** Caffeine
- **Feature Toggle:** ConfigCat (biblioteca sbootlib-arqt-base-feature-toggle)
- **Documentação API:** OpenAPI 3.0 / Swagger
- **Geração de código:** Swagger Codegen Maven Plugin 3.0.34
- **Mapeamento:** MapStruct
- **Build:** Maven 3.8+
- **Containerização:** Docker
- **Monitoramento:** Spring Actuator (porta 9090)
- **Telemetria:** Atlante Telemetry
- **Logging:** Logback com formato JSON para ambientes não-locais

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/usuarioFintechApi/abrirContaFintech` | `UsuarioFintechController` | Abertura ou edição de conta Fintech |
| POST | `/usuarioFintechApi/bloquearDesbloquearContaFintech` | `UsuarioFintechController` | Bloqueio ou desbloqueio de conta Fintech |
| POST | `/usuarioFintechApi/encerramentoContaFintech` | `UsuarioFintechController` | Encerramento de conta Fintech |
| POST | `/circuit-break-v2/` | `CircuitBreakerController` | Validação de circuit breaker com mecanismo de trava |
| GET | `/actuator/health` | Spring Actuator | Health check da aplicação |

## 5. Principais Regras de Negócio

- **Validação de Cliente:** Verifica se o CPF/CNPJ do cliente está autorizado através do token JWT e se existe no sistema
- **Validação de CompanyKey:** Banco 655 não deve ter companyKey; Banco 413 deve ter companyKey obrigatório
- **Validação de Data de Início:** 
  - Banco 655: data deve ser hoje
  - Banco 413: data deve ser ontem ou hoje (se ontem, hora atual deve ser menor que 2h)
- **Tipo de Movimento:** Inclusão (1) ou Alteração (2) com validações específicas de status
- **Status de Conta:** Pré-cadastro, Aberta, Bloqueada, Encerrada
- **Circuit Breaker:** Validação de transações com base em documentos, tipo de lançamento, liquidação e valores configuráveis via feature toggle
- **Validação de Encerramento:** Verifica se conta está aberta, valida usuários e protocolo de abertura
- **Bloqueio/Desbloqueio:** Valida status atual da conta antes de permitir operação
- **Protocolo:** Geração de protocolo único para cada operação usando hash SHA-256
- **Callback:** Comunicação assíncrona com sistemas parceiros para validação de operações (configurável via feature toggle)

## 6. Relação entre Entidades

- **TbParametroPagamentoFintech (Fintech):** Entidade principal representando a Fintech
  - Relaciona-se com TbCliente através de CdCliente
  - Possui CdIdentificacaoFintech e CdIdentificacaoContaFintech

- **TbContaUsuarioFintech (Conta):** Representa uma conta de usuário Fintech
  - Relaciona-se com TbParametroPagamentoFintech através de CdParametroPagamentoFintech
  - Relaciona-se com TbStatusContaFintech através de CdStatusContaFintech
  - Relaciona-se com TbTipoConta através de CdTipoConta

- **TbUsuarioContaFintech (Usuário):** Representa um usuário da conta Fintech
  - Relaciona-se com TbParametroPagamentoFintech através de CdParametroPagamentoFintech

- **TbRelacaoContaUsuarioFintech (Relação):** Tabela associativa entre Conta e Usuário
  - Relaciona-se com TbContaUsuarioFintech através de CdContaUsuarioFintech
  - Relaciona-se com TbUsuarioContaFintech através de CdUsuarioContaFintech
  - Relaciona-se com TbTipoVinculoConta através de CdTipoVinculoConta

- **TbControleAcaoAplicacao (Controle):** Registra ações realizadas nas contas
  - Relaciona-se com TbContaUsuarioFintech através de CdContaUsuarioFintech
  - Relaciona-se com TbAcaoAplicacao através de CdAcaoAplicacao
  - Relaciona-se com TbStatusContaFintech através de CdStatusContaFintech

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbParametroPagamentoFintech | tabela | SELECT | Consulta dados da Fintech pelo código de identificação ou CPF/CNPJ |
| TbContaUsuarioFintech | tabela | SELECT | Consulta contas de usuários Fintech por diversos critérios |
| TbUsuarioContaFintech | tabela | SELECT | Consulta usuários Fintech por documento ou ID |
| TbRelacaoContaUsuarioFintech | tabela | SELECT | Consulta relações entre contas e usuários |
| TbStatusContaFintech | tabela | SELECT | Consulta lista de status de contas disponíveis |
| TbAcaoAplicacao | tabela | SELECT | Consulta lista de ações de aplicação disponíveis |
| TbTipoVinculoConta | tabela | SELECT | Consulta tipos de vínculo de conta (Titular, Co-Titular) |
| TbParametroConsultaCliente | tabela | SELECT | Consulta URLs e parâmetros para integração com parceiros |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbContaUsuarioFintech | tabela | INSERT | Inclusão de nova conta de usuário Fintech |
| TbContaUsuarioFintech | tabela | UPDATE | Atualização de dados da conta (status, data encerramento, etc) |
| TbUsuarioContaFintech | tabela | INSERT | Inclusão de novo usuário Fintech |
| TbUsuarioContaFintech | tabela | UPDATE | Atualização de dados do usuário (nome, documento, status) |
| TbRelacaoContaUsuarioFintech | tabela | INSERT | Inclusão de nova relação entre conta e usuário |
| TbRelacaoContaUsuarioFintech | tabela | UPDATE | Atualização de relação (tipo vínculo, status ativo) |
| TbControleAcaoAplicacao | tabela | INSERT | Registro de ações realizadas (abertura, encerramento, bloqueio) |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | leitura | Configuração de logging | Arquivo de configuração de logs (formato JSON em produção) |
| application.yml | leitura | Spring Boot | Arquivo de configuração principal da aplicação |
| application-local.yml | leitura | Spring Boot | Configurações específicas para ambiente local |
| openapi.yaml | leitura | Swagger Codegen | Contract first da API REST |
| consulta.sts.parceiro.yml | leitura | Swagger Codegen | Contract para cliente de callback |
| *.sql | leitura | JDBI SqlObject | Arquivos SQL para queries do repositório |

## 10. Filas Lidas

não se aplica

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|----------------|------|-----------|
| API Gateway BV | REST | Autenticação OAuth2 para obtenção de tokens de acesso |
| Sistema Parceiro Fintech | REST (Callback) | Validação de abertura, encerramento e bloqueio/desbloqueio de contas via callback |
| ConfigCat | Feature Toggle | Gerenciamento de feature flags para controle de funcionalidades |
| SQL Server (DBSPAG) | JDBC | Banco de dados principal para persistência |

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com camadas bem definidas (controller, service, repository, domain)
- Uso adequado de padrões como Repository, Service e DTO/Domain
- Implementação de validações centralizadas em classes específicas
- Uso de MapStruct para mapeamento de objetos
- Documentação via OpenAPI/Swagger
- Implementação de feature toggles para controle de funcionalidades
- Uso de cache para otimização de consultas frequentes
- Tratamento de exceções centralizado com ExceptionHandlerAdvice

**Pontos de Melhoria:**
- Algumas classes de serviço estão muito extensas (ex: FintechService, UsuarioFintechService) e poderiam ser decompostas
- Presença de lógica de negócio em mappers (métodos default com lógica complexa)
- Uso excessivo de comentários em português misturado com código
- Alguns métodos com muitos parâmetros (ex: validarDadosContaFintech com 5 parâmetros)
- Falta de testes unitários no código analisado (apenas estrutura de testes presente)
- Uso de `@SneakyThrows` que pode ocultar exceções importantes
- Algumas queries SQL poderiam estar em procedures para melhor performance
- Validações de CPF/CNPJ com lógica duplicada e complexa

## 14. Observações Relevantes

- O sistema utiliza JDBI ao invés de JPA/Hibernate, o que proporciona maior controle sobre as queries SQL
- Implementa mecanismo de circuit breaker configurável via feature toggle para controle de transações
- Suporta dois bancos diferentes (655 e 413) com regras de validação específicas para cada um
- Utiliza geração de protocolo com hash SHA-256 para garantir unicidade
- Sistema preparado para multi-tenancy através do conceito de Fintech
- Implementa callback assíncrono para validação com sistemas parceiros (habilitável via feature toggle)
- Logs estruturados em JSON para ambientes não-locais facilitando análise e monitoramento
- Segurança baseada em JWT com validação de client_id no token
- Arquitetura preparada para deploy em OpenShift (Google Cloud Platform)
- Utiliza o chassi Atlante do Banco Votorantim para padronização