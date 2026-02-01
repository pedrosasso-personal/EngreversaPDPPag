# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema REST API desenvolvido em Spring Boot para consulta de informações de contratos financeiros do sistema Flex Oracle. O sistema fornece um endpoint para consultar a sequência financeira de contratos, realizando consultas no banco de dados Oracle Flex e retornando informações sobre eventos e motivos de contratos financeiros.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Server.java` | Classe principal da aplicação Spring Boot, responsável por inicializar o servidor |
| `ContratoFinanceiroFlexApi.java` | Controller REST que expõe o endpoint de consulta de sequência financeira |
| `SequenciaFinanceiraService.java` | Interface de serviço para lógica de negócio |
| `SequenciaFinanceiraServiceImpl.java` | Implementação do serviço, processa código do contrato e invoca repositório |
| `SequenciaFinanceiraRepository.java` | Interface de repositório para acesso a dados |
| `SequenciaFinanceiraRepositoryImpl.java` | Implementação do repositório, executa queries SQL no banco Oracle |
| `SequenciaFinanceiraMapper.java` | Interface para mapeamento entre Model e Representation |
| `SequenciaFinanceiraMapperImpl.java` | Implementação do mapper usando ModelMapper |
| `SequenciaFinanceiraRowMapper.java` | RowMapper para conversão de ResultSet em Model |
| `SequenciaFinanceiraModel.java` | Modelo de domínio representando sequência financeira |
| `ContractSummaryModel.java` | Modelo de domínio para resumo de contrato |
| `DatabaseConfiguration.java` | Configuração de beans relacionados ao banco de dados |
| `SpringSecurityConfig.java` | Configuração de segurança (desabilitada para todos endpoints) |
| `WebServiceTemplateConfiguration.java` | Configuração para consumo de Web Services SOAP |

## 3. Tecnologias Utilizadas

- **Framework Principal**: Spring Boot 2.0.0.RELEASE
- **Linguagem**: Java 8
- **Build Tool**: Gradle 4.5.1
- **Banco de Dados**: Oracle Database (JDBC Driver ojdbc8 19.3.0.0)
- **Segurança**: Spring Security (Basic Authentication)
- **Documentação API**: Swagger 2 (Springfox 2.9.2)
- **Mapeamento de Objetos**: ModelMapper 2.3.8
- **Logging**: Logback/SLF4J, Lombok
- **Bibliotecas Internas**: 
  - springboot-arqt-base-trilha-auditoria-web 2.0.0
  - springboot-arqt-base-security-basic 1.2.0
  - springboot-arqt-base-lib-database 0.2.2
- **Testes**: JUnit, Mockito, Rest-Assured, JMeter
- **Containerização**: Docker
- **Orquestração**: OpenShift (OCP)

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/corporativo/garantia/recuperacaoCredito/contrato/{codigoContrato}/financeiro/` | `ContratoFinanceiroFlexApi` | Consulta a sequência financeira de um contrato específico pelo código |

## 5. Principais Regras de Negócio

1. **Normalização do Código do Contrato**: O código do contrato deve ter no mínimo 13 dígitos. Se o código informado tiver menos dígitos, zeros à esquerda são adicionados automaticamente.

2. **Filtragem de Eventos**: A consulta exclui eventos do sistema (MAKER_ID = 'SYSTEM') e eventos específicos (REOP, INIT, VAMB, STCH, VAMI) que não são considerados sequências financeiras válidas.

3. **Seleção da Sequência**: Retorna apenas o evento mais recente (ROWNUM = 1) após ordenação por event_seq_no e version_no em ordem decrescente.

4. **Cálculo da Sequência Financeira**: Utiliza função de janela (ROW_NUMBER) particionada por account_number para numerar sequencialmente os eventos de cada contrato.

5. **Validação de Existência**: Lança exceção `SequenciaFinanceiraNaoEncontradoException` quando não encontra sequência financeira para o contrato informado.

6. **Conversão de Formato**: Remove zeros à esquerda do código do contrato no retorno da API para apresentação ao cliente.

## 6. Relação entre Entidades

**SequenciaFinanceiraModel**
- `numeroContrato` (String): Código do contrato com zeros à esquerda
- `sequenciaFinanceiraContrato` (Integer): Número sequencial do evento financeiro
- `codigoMotivoContratoFinanceiro` (String): Código do evento (ex: BOOK)

**ContractSummaryModel** (não utilizado ativamente no fluxo principal)
- Contém informações detalhadas do contrato incluindo dados do cliente, valores, parcelas e datas
- Relacionamento: Um contrato pode ter múltiplas sequências financeiras

**Relacionamento**: A aplicação consulta eventos da tabela `cltb_account_events_diary` e retorna a sequência financeira mais recente associada a um `account_number` (contrato).

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| `FLEX.cltb_account_events_diary` | Tabela | SELECT | Tabela de diário de eventos de contas do sistema Flex, contém histórico de eventos financeiros dos contratos |

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `sequenciafinanceirarepositoryimpl-sql.xml` | Leitura | `SequenciaFinanceiraRepositoryImpl` (via BvSql) | Arquivo XML contendo queries SQL parametrizadas para consulta de sequência financeira |
| `logback-spring.xml` | Leitura | Configuração de logging | Arquivo de configuração do Logback para definir padrões e níveis de log |
| `application.yml` / `application-local.yml` | Leitura | Spring Boot | Arquivos de configuração da aplicação por ambiente |
| `roles/*.yml` | Leitura | Configuração de segurança | Arquivos de configuração de roles e grupos por ambiente (des, qa, uat, prd, local) |

## 10. Filas Lidas

não se aplica

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Oracle Database Flex | Banco de Dados | Conexão JDBC com banco Oracle contendo dados de contratos financeiros. Ambientes: DES (orades29), UAT (orauat29), PRD (oraprd29) |
| LDAP BVNet | Autenticação | Servidor LDAP para autenticação de usuários (configurado mas desabilitado no código) |
| FCUBSCLService | Web Service SOAP | Serviço SOAP do Flex Cube para consulta de resumo de contratos (configurado via WebServiceTemplate, mas não utilizado no fluxo principal) |

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades em camadas (controller, service, repository, mapper)
- Uso adequado de interfaces para abstrair implementações
- Tratamento de exceções customizadas
- Logging estruturado com informações contextuais
- Uso de bibliotecas modernas (ModelMapper, Lombok)
- Configuração externalizada por ambiente
- Documentação via Swagger

**Pontos de Melhoria:**
- Configuração de segurança completamente desabilitada (`web.ignoring().antMatchers("/**")`) representa risco de segurança
- Classe `ContractSummaryModel` e configuração de WebService não são utilizadas, indicando código morto
- Falta de testes unitários e de integração implementados (apenas estrutura)
- Conversão manual de String para Long poderia ser tratada de forma mais elegante
- Hardcoded de valores como lista de eventos excluídos na query SQL
- Falta de validação de entrada no controller
- Uso de `@SuppressWarnings("static-access")` em testes indica má prática
- Comentários em português misturados com código em inglês

## 14. Observações Relevantes

1. **Ambiente de Execução**: A aplicação está preparada para execução em containers Docker e deploy no OpenShift (Google Cloud Platform).

2. **Configuração de Memória**: JVM configurada com `-Xms256m -Xmx384m -XX:MaxPermSize=384m` no Dockerfile.

3. **Healthcheck**: Endpoint `/api-utils/status` configurado para probes de liveness e readiness no Kubernetes.

4. **Segurança Desabilitada**: A configuração atual desabilita completamente a segurança Spring Security, o que pode ser inadequado para produção.

5. **Múltiplos Ambientes**: Suporte para ambientes local, des, qa, uat e prd com configurações específicas.

6. **Biblioteca Proprietária**: Uso extensivo de bibliotecas internas da Votorantim (`arqt-base`), indicando padrões corporativos.

7. **Código Não Utilizado**: Presença de classes e configurações (WebService, ContractSummaryModel) que não são utilizadas no fluxo principal, sugerindo funcionalidades planejadas ou legado.

8. **Testes Funcionais**: Estrutura de testes com JMeter configurada, mas sem implementação efetiva de casos de teste.

9. **Pipeline CI/CD**: Integração com Jenkins configurada via `jenkins.properties` e scripts Gradle para build, testes e deploy automatizados.

10. **Versionamento**: Uso do plugin Gradle Release para gerenciamento automático de versões.