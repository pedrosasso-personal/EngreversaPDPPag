# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de orquestração de consulta de saldo bancário desenvolvido em Java com Spring Boot. O sistema atua como uma camada de orquestração que integra serviços de dados cadastrais de clientes e consulta de saldo, fornecendo endpoints REST para consulta de saldo de contas correntes, saldo negativo, limites de conta e consultas por grupo comercial. Utiliza Apache Camel para orquestração de fluxos e segue arquitetura hexagonal (ports and adapters).

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application.java` | Classe principal que inicializa a aplicação Spring Boot |
| `SaldoController.java` | Controlador REST que expõe os endpoints de consulta de saldo |
| `SaldoService.java` | Serviço de domínio que orquestra as chamadas via Apache Camel |
| `SaldoRouter.java` | Define as rotas do Apache Camel para orquestração dos fluxos |
| `SaldoRepositoryImpl.java` | Implementação do repositório para consulta de saldo em serviços externos |
| `ClienteDadosCadastraisRepositoryImpl.java` | Implementação do repositório para consulta de dados cadastrais |
| `ConsultaSaldoRepositoryImpl.java` | Implementação do repositório para consultas de saldo por CPF/CNPJ |
| `SaldoConversor.java` | Classe utilitária para conversão entre objetos de domínio e representação |
| `AccountBalanceMapper.java` | Mapper para conversão de objetos de saldo de conta |
| `AccountLimitsMapper.java` | Mapper MapStruct para conversão de objetos de limites de conta |
| `ExceptionControllerHandler.java` | Tratamento centralizado de exceções |
| `CamelContextWrapper.java` | Wrapper para configuração do contexto do Apache Camel |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Apache Camel 3.22.0** (orquestração de fluxos)
- **Spring Security OAuth2** (autenticação e autorização JWT)
- **RestTemplate** (cliente HTTP)
- **Swagger/OpenAPI 3.0** (documentação de APIs)
- **Springfox 3.0.0** (geração de documentação Swagger)
- **MapStruct 1.5.5** (mapeamento de objetos)
- **Lombok** (redução de boilerplate)
- **Logback** (logging)
- **Micrometer + Prometheus** (métricas)
- **JUnit 5 + Mockito** (testes unitários)
- **Rest Assured** (testes funcionais)
- **Pact** (testes de contrato)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Kubernetes/OpenShift** (orquestração de containers)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/saldo-bancario` | `SaldoController` | Consulta saldo bancário por banco, agência, conta e CPF/CNPJ |
| POST | `/v1/consultarSaldoContaCorrente` | `SaldoController` | Consulta saldo de múltiplas contas correntes por CPF/CNPJ |
| POST | `/v1/consultarContasPorGrupoComercialSaldo` | `SaldoController` | Consulta saldo de contas por grupo comercial |
| GET | `/v1/saldo-bancario/negativo` | `SaldoController` | Consulta contas com saldo negativo por modalidade |
| GET | `/v1/digital-bank/{bank}/balances` | `SaldoController` | Consulta saldo de conta por banco (padrão digital) |
| GET | `/v1/digital-bank/{bank}/limits` | `SaldoController` | Consulta limites de conta por banco |
| GET | `/actuator/health` | Spring Actuator | Health check da aplicação |
| GET | `/actuator/prometheus` | Spring Actuator | Métricas para Prometheus |

---

## 5. Principais Regras de Negócio

1. **Validação de Titularidade**: Valida se o CPF/CNPJ informado corresponde ao titular da conta consultada
2. **Validação de Conta Ativa**: Verifica se a conta não possui data de encerramento antes de consultar saldo
3. **Validação de Entrada Numérica**: Campos como agência devem conter apenas números
4. **Autenticação JWT**: Utiliza CPF/CNPJ do token JWT quando não informado no header
5. **Consulta de Saldo por Modalidade**: Permite filtrar contas com saldo negativo por tipo de modalidade
6. **Agregação de Dados**: Combina informações de dados cadastrais com saldo bancário
7. **Tratamento de Contas Encerradas**: Retorna valores zerados para contas encerradas ou não localizadas
8. **Filtro por Tipo de Conta**: Permite filtrar consultas por tipo de conta (5 ou 6)
9. **Consulta por Grupo Comercial**: Agrupa consultas de saldo por divisão comercial
10. **Validação de Data de Referência**: Aceita data de referência no formato YYYY-MM-DD para consultas históricas

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **ClienteSaldo**: Representa o saldo de um cliente com informações de conta e valores
  - Atributos: codigoBanco, agencia, conta, cpfCnpj, valorTotal, valorDisponivel, valorIndisponivel, valorBloqueado, valorLimiteContaCorrente, dataConsulta, tipoConta

- **ListaCliente**: Representa um cliente com suas contas
  - Relacionamento: 1:N com ListaConta
  - Atributos: numeroCpfCnpj, codigoPessoaGlobal, nomeTitular, codigoPessoa

- **ListaConta**: Representa uma conta bancária com seus saldos
  - Atributos: numeroConta, numeroAgencia, tipoConta, valorTotal, valorDisponivel, valorIndisponivel, valorBloqueado, valorLimiteContaCorrente

- **AccountBalance**: Representa saldo de conta no padrão digital
  - Atributos: grossAmount, netAmount, unavailableAmount, blockedAmount, creditLimit, referenceDate

- **AccountLimits**: Representa limites de crédito de uma conta
  - Relacionamento: 1:1 com AccountId, 1:N com Limit
  - Atributos: accountId, limits

- **SaldoNegativo**: Representa contas com saldo negativo
  - Atributos: cdBanco, cdAgencia, nuContaCorrente, cdTipoConta, vrSaldoDisponivel, nmModalidadeConta, cdModalidadeConta

**Relacionamentos:**
- ClienteSaldo é composto por dados de conta e saldo
- ConsultarSaldoContaResponse contém lista de ListaCliente
- ListaCliente contém lista de ListaConta
- AccountLimits contém AccountId e lista de Limit

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

*Observação: O sistema não acessa diretamente banco de dados. Todas as consultas são realizadas através de APIs REST de outros microserviços.*

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

*Observação: O sistema não realiza operações de escrita em banco de dados. É um serviço de orquestração read-only.*

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `application.yml` | Leitura | Spring Boot | Arquivo de configuração da aplicação com propriedades de ambiente |
| `logback-spring.xml` | Leitura | Logback | Configuração de logs da aplicação (console e JSON) |
| `sboot-ccbd-base-orch-saldo.yaml` | Leitura | Swagger Codegen | Especificação OpenAPI dos endpoints do serviço |
| `sboot-ccbd-base-atom-saldo.yaml` | Leitura | Swagger Codegen | Especificação OpenAPI do cliente de saldo |
| `sboot-glob-base-atom-cliente-dados-cadastrais.yaml` | Leitura | Swagger Codegen | Especificação OpenAPI do cliente de dados cadastrais |

---

## 10. Filas Lidas

não se aplica

*Observação: O sistema não consome mensagens de filas.*

---

## 11. Filas Geradas

não se aplica

*Observação: O sistema não publica mensagens em filas.*

---

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| `sboot-glob-base-atom-cliente-dados-cadastrais` | API REST | Serviço de consulta de dados cadastrais de clientes e contas |
| `sboot-ccbd-base-atom-saldo` | API REST | Serviço atômico de consulta de saldo bancário |
| `sboot-ccbd-base-atom-saldo` (consultar-saldo) | API REST | Serviço de consulta de saldo por conta |
| `sboot-ccbd-base-atom-saldo` (saldo-negativo) | API REST | Serviço de consulta de contas com saldo negativo |
| `sboot-ccbd-base-atom-saldo` (account-balance) | API REST | Serviço de consulta de saldo no padrão digital bank |
| `sboot-ccbd-base-atom-saldo` (account-limits) | API REST | Serviço de consulta de limites de conta |
| OAuth2 JWT Provider | API REST | Serviço de autenticação e autorização via JWT |

**Ambientes:**
- **DES**: `*.des-*.svc.cluster.local:8080` (interno Kubernetes)
- **UAT**: `*.uat-*.svc.cluster.local:8080` (interno Kubernetes)
- **PRD**: `*.prd-*.svc.cluster.local:8080` (interno Kubernetes)

---

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura hexagonal (domain, application, ports/adapters)
- Uso adequado de padrões como Repository, Service e Mapper
- Implementação de testes unitários, integração e funcionais
- Uso de MapStruct para mapeamento automático de objetos
- Tratamento centralizado de exceções
- Documentação OpenAPI/Swagger bem estruturada
- Configuração adequada de logs e métricas
- Uso de Lombok para reduzir boilerplate

**Pontos de Melhoria:**
- Classe `SaldoConversor` muito extensa (>500 linhas) com múltiplas responsabilidades - deveria ser quebrada em conversores específicos
- Método `consultarContas` em `ConsultaSaldoRepositoryImpl` com lógica complexa e aninhada - dificulta manutenção
- Falta de documentação JavaDoc em classes e métodos principais
- Alguns métodos com muitos parâmetros (ex: `accountLimitBalance` com 7 parâmetros)
- Uso de `ArrayList` específico ao invés de `List` em alguns pontos
- Tratamento genérico de exceções em alguns fluxos (catch Exception)
- Código comentado em alguns testes
- Falta de validação de entrada em alguns endpoints (delegado ao Swagger)

---

## 14. Observações Relevantes

1. **Arquitetura**: Sistema segue arquitetura hexagonal com separação clara entre domain, application e infrastructure
2. **Orquestração**: Utiliza Apache Camel para orquestração de chamadas a múltiplos serviços
3. **Segurança**: Implementa autenticação OAuth2 com JWT, permitindo CPF/CNPJ via token ou header
4. **Resiliência**: Implementa tratamento de erros com retorno de valores zerados quando serviços externos falham
5. **Observabilidade**: Configurado com Prometheus, Grafana e logs estruturados em JSON
6. **Containerização**: Preparado para deploy em Kubernetes/OpenShift com configurações de health check e recursos
7. **Testes**: Boa cobertura de testes com separação entre unit, integration e functional
8. **Versionamento**: API versionada com prefixo `/v1/`
9. **Multi-ambiente**: Configurações específicas para local, des, uat e prd
10. **Geração de Código**: Utiliza Swagger Codegen para gerar clientes REST automaticamente
11. **Limitação**: Sistema não possui cache, todas as consultas são síncronas aos serviços downstream
12. **Performance**: Configurado com limites de CPU (1 core) e memória (1GB) no Kubernetes