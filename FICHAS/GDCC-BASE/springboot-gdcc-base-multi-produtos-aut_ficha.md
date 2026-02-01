# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de autenticação e autorização de débito em conta corrente para múltiplos produtos bancários. O sistema recebe solicitações de débito via fila JMS, valida os dados bancários, registra autorizações de débito no banco de dados e envia mensagens para processamento posterior. Também disponibiliza endpoints REST para consulta de bancos conveniados e envio de solicitações de autenticação.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **AutenticarDebitoContaListener** | Listener JMS que recebe mensagens de autenticação de débito e orquestra o fluxo de validação e registro |
| **AutenticacarDebitoContaBusinessService** | Serviço de negócio principal que valida campos da requisição, busca dados de sistema origem e conta convênio |
| **AutorizacaoDebitoBusinessService** | Gerencia inclusão de registros de autorização de débito e logs no banco de dados |
| **AutenticarDebitoContaAPI** | Controller REST para envio de solicitações de autenticação de débito |
| **ListaBancosConveniadosAPI** | Controller REST para consulta de bancos conveniados |
| **AutenticarDebitoContaJmsService** | Serviço para envio de mensagens JMS (autenticação, autorização e retorno) |
| **AutorizacaoDebitoRepository** | Repository para operações de insert de autorização de débito no banco |
| **ContaConvenioService** | Consulta parâmetros de conta convênio no banco de dados |
| **SistemaOrigemService** | Busca informações de sistema origem |
| **ObterSequencialService** | Obtém sequenciais para geração de IDs via stored procedure |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.0.0.RELEASE** - Framework principal
- **Spring JMS** - Mensageria
- **IBM MQ** - Gerenciador de filas
- **JDBC/Spring JDBC** - Acesso a banco de dados
- **Sybase jConnect 4 (7.07-ESD-5)** - Driver JDBC para Sybase
- **Swagger/Springfox 2.8.0** - Documentação de API
- **Lombok 1.16.20** - Redução de boilerplate
- **Jackson** - Serialização/deserialização JSON
- **Gradle 4.5.1** - Build tool
- **JUnit/Mockito** - Testes unitários
- **JMeter** - Testes funcionais
- **Jacoco** - Cobertura de testes
- **SonarQube** - Análise de qualidade de código
- **Docker** - Containerização

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/autenticarDebitoConta | AutenticarDebitoContaAPI | Envia solicitação de autenticação de débito para fila JMS |
| GET | /v1/listarBancoConveniado | ListaBancosConveniadosAPI | Lista bancos conveniados para um sistema origem e veículo legal |

---

## 5. Principais Regras de Negócio

1. **Validação de Campos Obrigatórios**: Código do sistema origem, identificador do sistema origem, número do banco, conta corrente, agência, CPF/CNPJ e agrupamento devem ser informados
2. **Validação de CPF/CNPJ**: Valida formato e tamanho (11 dígitos para CPF, 14 para CNPJ)
3. **Validação de Tipo de Pessoa**: Tipo de pessoa deve corresponder ao tamanho do CPF/CNPJ informado (F para CPF, J para CNPJ)
4. **Validação de Agência**: Máximo 4 dígitos, dígito verificador máximo 1 caractere
5. **Validação de Conta Corrente**: Deve ser numérica, dígito verificador máximo 1 caractere
6. **Validação de Tipo de Moeda**: Máximo 2 dígitos, padrão "03" se não informado
7. **Validação de Veículo Legal**: Padrão 1 se não informado
8. **Busca de Sistema Origem**: Verifica se o código do sistema origem existe no cadastro
9. **Busca de Conta Convênio**: Valida se existe convênio ativo para o banco, sistema origem, veículo legal e agrupamento informados
10. **Geração de Código de Autorização**: Obtém sequencial via stored procedure para registro de autorização
11. **Registro de Autorização CEF**: Inclui registro de autorização, proposta/contrato e log de evento
12. **Registro de Débito**: Inclui registro de débito com status 3 (aguardando autorização)
13. **Modelo de Autorização**: Busca modelo de autorização específico por banco
14. **Envio de Mensagens**: Envia mensagens para filas de autorização e tópicos de retorno com correlationId

---

## 6. Relação entre Entidades

**Principais entidades e relacionamentos:**

- **TbSistemaOrigem**: Cadastro de sistemas origem (1:N com TbContaConvenioSistemaOrigem)
- **TbContaConvenio**: Cadastro de contas convênio por banco (1:N com TbContaConvenioSistemaOrigem)
- **TbContaConvenioSistemaOrigem**: Relacionamento entre conta convênio e sistema origem (N:1 com TbContaConvenio, N:1 com TbSistemaOrigem, 1:N com TbRegistroDebito)
- **TbRegistroAutorizacaoDebito**: Registro de autorização de débito (1:N com TbEventoRegistroAutorizacaoDbo, 1:1 com TbAutorizacaoDebitoPrpsaCntro, 1:N com TbRegistroDebito)
- **TbEventoRegistroAutorizacaoDbo**: Log de eventos de autorização (N:1 com TbRegistroAutorizacaoDebito)
- **TbAutorizacaoDebitoPrpsaCntro**: Relacionamento entre autorização e proposta/contrato (1:1 com TbRegistroAutorizacaoDebito)
- **TbRegistroDebito**: Registro de débito a ser processado (N:1 com TbContaConvenioSistemaOrigem, N:1 com TbRegistroAutorizacaoDebito)
- **TbParametroAutorizacaoDebito**: Parâmetros de modelo de autorização por banco
- **TbBanco**: Cadastro de bancos (relacionamento via NuBanco)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbSistemaOrigem | Tabela | SELECT | Consulta dados do sistema origem pelo código |
| TbContaConvenio | Tabela | SELECT | Consulta parâmetros de conta convênio por banco, veículo legal e agrupamento |
| TbContaConvenioSistemaOrigem | Tabela | SELECT | Consulta relacionamento entre conta convênio e sistema origem |
| TbParametroAutorizacaoDebito | Tabela | SELECT | Consulta modelo de autorização por banco |
| TbRegistroAutorizacaoDebito | Tabela | SELECT | Consulta registros de autorização existentes |
| TbEventoRegistroAutorizacaoDbo | Tabela | SELECT | Consulta eventos de autorização |
| TbAutorizacaoDebitoPrpsaCntro | Tabela | SELECT | Consulta relacionamento autorização/proposta/contrato |
| TbBanco (DBCOR) | Tabela | SELECT | Consulta dados de bancos conveniados |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbRegistroAutorizacaoDebito | Tabela | INSERT | Insere novo registro de autorização de débito |
| TbAutorizacaoDebitoPrpsaCntro | Tabela | INSERT | Insere relacionamento entre autorização e proposta/contrato |
| TbEventoRegistroAutorizacaoDbo | Tabela | INSERT | Insere log de evento de autorização |
| TbRegistroDebito | Tabela | INSERT | Insere registro de débito a ser processado |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | Spring Boot | Configurações da aplicação por ambiente |
| application-local.yml | Leitura | Spring Boot | Configurações específicas do ambiente local |
| logback-spring.xml | Leitura | Logback | Configuração de logs |
| *-sql.xml | Leitura | BvSql (repositories) | Queries SQL externalizadas |
| roles/*.yml | Leitura | Spring Security | Configuração de roles por ambiente |

---

## 10. Filas Lidas

- **${GDCC_JMS_AUTENTICAR_DEBITO_CONTA_QUEUE}** (DEV.QUEUE.1 em local): Fila de entrada para solicitações de autenticação de débito em conta. Listener: `AutenticarDebitoContaListener`

---

## 11. Filas Geradas

- **${GDCC_JMS_AUTORIZAR_DEBITO_CONTA_QUEUE}** (DEV.QUEUE.2 em local): Fila para envio de solicitações de autorização de débito (formato XML)
- **${GDCC_JMS_TP_DEBITO_EM_CONTA_TP}** (dev/ em local): Tópico para publicação de solicitações de autenticação de débito
- **${GDCC_JMS_TP_RETORNO_DEBITO_EM_CONTA_TP}** (operacao em local): Tópico para publicação de retornos de autenticação de débito

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| IBM MQ | Mensageria | Gerenciador de filas para comunicação assíncrona |
| Sybase Database (DbGestaoDebitoContaCorrente) | Banco de Dados | Banco principal para gestão de débito em conta corrente |
| DBCOR (Sybase) | Banco de Dados | Banco corporativo para consulta de dados de bancos |
| LDAP (bvnet.bv) | Autenticação | Autenticação de usuários via LDAP corporativo |

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Estrutura de pacotes bem organizada seguindo padrão MVC/camadas
- Uso adequado de injeção de dependências e anotações Spring
- Separação clara entre camadas (controller, service, business, repository)
- Uso de Lombok para reduzir boilerplate
- Configuração de testes unitários, integração e funcionais
- Externalização de queries SQL em arquivos XML
- Uso de RowMappers para mapeamento de resultados
- Configuração de ambientes separados

**Pontos Negativos:**
- Métodos muito longos e com alta complexidade ciclomática (ex: `validaCamposRequest` dividido em 8 métodos)
- Uso excessivo de `System.out.println` em vez de logs estruturados
- Tratamento de exceções genérico com apenas log de erro
- Falta de validação de nullability em vários pontos
- Código comentado e mensagens de log em português misturadas com código
- Uso de `@AllArgsConstructor` pode dificultar manutenção futura
- Falta de documentação JavaDoc nas classes e métodos
- Conversão manual de XML em String (método `toXml()`) em vez de usar bibliotecas
- Uso de `Date` em vez de `LocalDate/LocalDateTime` (Java 8+)
- Configurações hardcoded em `StaticValues` poderiam estar em properties
- Falta de tratamento específico de erros de banco de dados
- Métodos de validação poderiam usar Bean Validation (JSR-303)

---

## 14. Observações Relevantes

1. **Ambiente Multi-Tenant**: O sistema suporta múltiplos sistemas origem e veículos legais, permitindo uso por diferentes produtos bancários
2. **Processamento Assíncrono**: Utiliza padrão de mensageria para processamento assíncrono de débitos
3. **Correlação de Mensagens**: Usa JMSCorrelationID para rastreamento de mensagens entre filas
4. **Modelo CEF**: Implementação específica para modelo de autorização da Caixa Econômica Federal (banco 104)
5. **Versionamento de Layout**: Sistema trabalha com versão específica de layout de arquivo (08)
6. **Segurança**: Implementa autenticação básica e LDAP, com roles configuráveis por ambiente
7. **Observabilidade**: Configuração de logs com MDC (ticket e fase) para rastreabilidade
8. **Containerização**: Preparado para deploy em containers Docker/OpenShift
9. **Pipeline CI/CD**: Integrado com Jenkins para build e deploy automatizado
10. **Stored Procedures**: Utiliza stored procedure `prObterSequencialDisponivel` para geração de IDs sequenciais
11. **Transações**: Uso de anotações `@Transactional` com propagação configurada (REQUIRES_NEW, NOT_SUPPORTED)
12. **Swagger**: Documentação de API disponível via Swagger UI