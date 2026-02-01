# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **springboot-gdcc-base-multi-produtos** é uma aplicação Java Spring Boot voltada para a gestão de débitos em conta corrente para multiprodutos. Seu objetivo principal é receber solicitações de inclusão de débito via mensageria JMS (IBM MQ), validar as informações (conta, agência, CPF/CNPJ, autorizações, datas, valores), persistir os registros de débito em banco de dados Sybase e enviar respostas (sucesso ou erro) para filas de retorno. O sistema também expõe endpoints REST para testes e envio manual de mensagens.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Server.java** | Classe principal (main) que inicializa a aplicação Spring Boot. |
| **InclusaoDebitoMultiprodutosListener** | Listener JMS que consome mensagens da fila de inclusão de débito, valida e processa a inclusão. |
| **InclusaoDebitoMultiprodutosService** | Serviço de negócio que orquestra validações, preenchimento de dados, cálculo de datas de agendamento e inclusão de débito. |
| **InclusaoDebitoJmsService** | Serviço responsável por enviar mensagens JMS (inclusão e retorno). |
| **ContaConvenioService** | Consulta parâmetros de conta convênio no banco de dados. |
| **SistemaOrigemService** | Busca informações do sistema de origem. |
| **ParametroSistemaService** | Consulta data de exercício do sistema. |
| **ModeloAutorizacaoService** | Busca modelo de autorização por banco. |
| **RegistroAutorizacaoDebitoService** | Valida se a autorização de débito está aprovada. |
| **ContaConvenioSistemaOrigemService** | Busca código de conta convênio sistema origem. |
| **ObterSequencialService** | Obtém sequencial para registro de débito via stored procedure. |
| **InclusaoDebitoRepository** | Persiste registro de débito no banco de dados. |
| **InclusaoDebitoEnvioRepository** | Envia mensagens para fila de débito (topic). |
| **InclusaoDebitoRetornoRepository** | Envia mensagens de retorno para fila de retorno (topic). |
| **AutorizacaoDebitoApi** | Endpoint REST de teste para listar autorizações de débito. |
| **InclusaoDebitoApi** | Endpoint REST para envio manual de inclusão de débito. |
| **JmsConfiguration** | Configuração de conversores e listeners JMS. |
| **DocketConfiguration** | Configuração do Swagger para documentação da API. |

---

## 3. Tecnologias Utilizadas

- **Java 8** (OpenJ9)
- **Spring Boot 2.0.0.RELEASE**
- **Spring JMS** (integração com IBM MQ)
- **IBM MQ** (mensageria)
- **Sybase jConnect 4** (driver JDBC para Sybase)
- **Spring JDBC / NamedParameterJdbcTemplate** (acesso a banco de dados)
- **Lombok** (redução de boilerplate)
- **Swagger / Springfox** (documentação de API REST)
- **Logback** (logging)
- **Gradle** (build)
- **Docker** (containerização)
- **JaCoCo** (cobertura de testes)
- **SonarQube** (análise de qualidade de código)
- **Spring Security** (autenticação básica e LDAP)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/autorizacao-debito` | AutorizacaoDebitoApi | Teste de conexão com banco de dados, lista autorizações de débito. |
| POST | `/varejo/contratosGestao` | InclusaoDebitoApi | Envia mensagem de inclusão de débito para fila JMS (uso manual/teste). |

---

## 5. Principais Regras de Negócio

1. **Validação de Parâmetros Obrigatórios**: Código do sistema de origem, veículo legal, banco, agência, conta, CPF/CNPJ, data de débito e valor devem ser informados.
2. **Validação de CPF/CNPJ**: Deve conter apenas números, com tamanho válido (11 para CPF, 14 para CNPJ).
3. **Validação de Tipo de Pessoa**: Se informado, deve ser consistente com o tamanho do CPF/CNPJ.
4. **Validação de Data de Débito**: Deve ser maior ou igual à data de exercício do sistema.
5. **Validação de Data de Agendamento**: Se não informada, é calculada subtraindo o prazo de débito da data de vencimento. Deve estar dentro da faixa de prazo mínimo e máximo da conta convênio.
6. **Validação de Conta Convênio**: Deve existir e estar ativa para o sistema de origem, veículo legal, banco e agrupamento informados.
7. **Validação de Modelo de Autorização**: O banco informado deve possuir modelo de autorização cadastrado.
8. **Validação de Autorização de Débito**: Se o banco exigir (ex: banco 104), a autorização deve estar aprovada (status 300 ou 301).
9. **Geração de Sequencial**: Obtém sequencial único para o registro de débito via stored procedure.
10. **Persistência de Débito**: Insere registro de débito com status "Aguardando Geração" (código 3).
11. **Envio de Retorno**: Envia mensagem de retorno (sucesso ou erro) para fila de retorno, com correlationId da mensagem original.

---

## 6. Relação entre Entidades

- **TbRegistroDebito**: Entidade principal que armazena os débitos. Relaciona-se com:
  - **TbContaConvenioSistemaOrigem** (via `CdContaConvenioSistemaOrigem`)
  - **TbStatusDebito** (via `CdStatusDebito`)
  - **TbRegistroAutorizacaoDebito** (via `CdRegistroAutorizacaoDebito`)
  
- **TbContaConvenioSistemaOrigem**: Relaciona conta convênio com sistema de origem. Relaciona-se com:
  - **TbContaConvenio** (via `CdContaConvenio`)
  - **TbSistemaOrigem** (via `CdSistemaOrigem`)

- **TbContaConvenio**: Armazena parâmetros de conta convênio (prazos, banco, agência, etc.).

- **TbRegistroAutorizacaoDebito**: Armazena autorizações de débito. Relaciona-se com:
  - **TbEventoRegistroAutorizacaoDbo** (eventos de autorização)
  - **TbParametroAutorizacaoDebito** (modelo de autorização)

- **TbParametroSistema**: Armazena data de exercício e processamento do sistema.

- **TbSistemaOrigem**: Cadastro de sistemas de origem.

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbAutorizacaoDebitoPrpsaCntro | Tabela | SELECT | Leitura de autorizações de débito (proposta/contrato). |
| TbContaConvenio | Tabela | SELECT | Consulta parâmetros de conta convênio (prazos, banco, agência). |
| TbContaConvenioSistemaOrigem | Tabela | SELECT | Busca código de conta convênio sistema origem. |
| TbSistemaOrigem | Tabela | SELECT | Busca nome do sistema de origem. |
| TbParametroSistema | Tabela | SELECT | Consulta data de exercício do sistema. |
| TbParametroAutorizacaoDebito | Tabela | SELECT | Busca modelo de autorização por banco. |
| TbRegistroAutorizacaoDebito | Tabela | SELECT | Valida se autorização de débito está aprovada. |
| TbEventoRegistroAutorizacaoDbo | Tabela | SELECT | Consulta eventos de autorização (status 300/301). |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbRegistroDebito | Tabela | INSERT | Insere novo registro de débito em conta corrente. |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | Leitura | Logback (Spring Boot) | Configuração de logs (console). |
| application.yml | Leitura | Spring Boot | Configuração de datasource, JMS, LDAP, etc. |
| application-local.yml | Leitura | Spring Boot | Configuração específica para ambiente local. |
| *-sql.xml | Leitura | BvSql (biblioteca) | Arquivos XML contendo queries SQL. |

---

## 10. Filas Lidas

- **${GDCC_JMS_INCLUIR_DEBITO_CONTA_QUEUE}** (ex: `DEV.QUEUE.1` em local): Fila de onde o listener `InclusaoDebitoMultiprodutosListener` consome mensagens de inclusão de débito.

---

## 11. Filas Geradas

- **${GDCC_JMS_TP_DEBITO_EM_CONTA_TP}** (ex: `dev/` em local): Tópico para onde são enviadas mensagens de inclusão de débito (operação `debitar`).
- **${GDCC_JMS_TP_RETORNO_DEBITO_EM_CONTA_TP}** (ex: `operacao` em local): Tópico para onde são enviadas mensagens de retorno de inclusão de débito (sucesso ou erro).

---

## 12. Integrações Externas

- **IBM MQ**: Integração via JMS para consumo e publicação de mensagens em filas/tópicos.
- **Banco de Dados Sybase**: Acesso via JDBC para leitura e escrita de dados (TbRegistroDebito, TbContaConvenio, etc.).
- **LDAP (opcional)**: Autenticação de usuários via LDAP (configurável por ambiente).

---

## 13. Avaliação da Qualidade do Código

**Nota:** 6/10

**Justificativa:**

**Pontos Positivos:**
- Uso de Spring Boot e boas práticas de injeção de dependência.
- Separação de responsabilidades (services, repositories, listeners).
- Uso de Lombok para reduzir boilerplate.
- Configuração de Swagger para documentação de API.
- Uso de transações e propagação adequada em repositórios.
- Tratamento de exceções em pontos críticos.

**Pontos Negativos:**
- **Métodos muito longos e complexos**: `InclusaoDebitoMultiprodutosService` possui métodos com muitas responsabilidades (ex: `preencheInclusaoVO`, `validarParametrosInclusaoRegistroDebito`), dificultando manutenção e testes.
- **Falta de testes unitários e de integração**: Diretórios de teste estão vazios (`.keep` files), indicando ausência de cobertura de testes.
- **Uso excessivo de `System.out.println`**: Em `AutorizacaoDebitoRepository`, há uso de `System.out.println` ao invés de logger.
- **Tratamento de exceções genérico**: Muitos blocos `catch (Exception e)` sem tratamento específico, apenas log de erro.
- **Código duplicado**: Métodos `validarParametrosInclusaoRegistroDebito1`, `validarParametrosInclusaoRegistroDebito2`, etc., poderiam ser refatorados para reduzir duplicação.
- **Falta de validação de entrada em endpoints REST**: Endpoint `InclusaoDebitoApi` não valida parâmetros de entrada (ex: `@Valid`).
- **Uso de `Date` ao invés de `LocalDate/LocalDateTime`**: Uso de API legada de datas (`java.util.Date`), quando `java.time` seria mais adequado.
- **Falta de documentação interna**: Poucos comentários explicativos em métodos complexos.
- **Configuração de segurança básica**: Uso de usuários in-memory em produção pode ser inseguro.

---

## 14. Observações Relevantes

- O sistema utiliza uma stored procedure (`prObterSequencialDisponivel`) para gerar sequenciais únicos para registros de débito.
- A configuração de JMS utiliza conversores customizados (`ConverterJms`, `MappingMessageConverterCuston`) para lidar com mensagens JSON e BytesMessage.
- O sistema suporta múltiplos ambientes (local, des, qa, uat, prd) via profiles do Spring.
- A infraestrutura como código (IaC) está definida em `infra.yml` para deploy em Kubernetes/OpenShift.
- O sistema utiliza a biblioteca `springboot-arqt-base` da Votorantim para trilha de auditoria, segurança e acesso a banco de dados.
- O Dockerfile utiliza a imagem `adoptopenjdk/openjdk8-openj9` para execução da aplicação.
- O sistema possui integração com SonarQube e JaCoCo para análise de qualidade e cobertura de código.