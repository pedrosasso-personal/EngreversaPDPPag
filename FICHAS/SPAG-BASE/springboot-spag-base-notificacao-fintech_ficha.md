# Ficha Técnica do Sistema

---

## 1. Descrição Geral

O sistema **springboot-spag-base-notificacao-fintech** é uma API REST desenvolvida em Spring Boot para gerenciar notificações relacionadas a operações de Fintech. Seu objetivo principal é receber requisições de notificação contendo informações sobre movimentações financeiras ou extratos, validar e persistir essas informações em banco de dados SQL Server. O sistema atua como um serviço de backend que registra eventos de notificação para posterior consulta e auditoria.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Server.java** | Classe principal que inicializa a aplicação Spring Boot |
| **NotificacaoFintechApi.java** | Controller REST que expõe o endpoint POST /notificar para receber notificações |
| **NotificacaoFintechService.java** | Camada de serviço que orquestra a lógica de negócio de notificação |
| **NotificacaoFintechRepository.java** | Camada de acesso a dados responsável por inserir notificações no banco de dados |
| **NotificacaoFintechRequest.java** | DTO de entrada contendo os dados da notificação |
| **NotificacaoFintechResponse.java** | DTO de resposta com código de retorno da operação |
| **NotificacaoFintech.java** | Entidade de domínio representando uma notificação |
| **TipoNotificacaoEnum.java** | Enum que define os tipos de notificação (Movimentação e Extrato) |
| **DocketConfiguration.java** | Configuração do Swagger para documentação da API |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.0.0.RELEASE** - Framework principal
- **Spring Web** - Para construção da API REST
- **Spring JDBC** - Para acesso ao banco de dados
- **SQL Server** - Banco de dados relacional (driver mssql-jdbc 7.0.0)
- **Swagger/Springfox 2.8.0** - Documentação da API
- **Lombok 1.16.20** - Redução de código boilerplate
- **Logback** - Framework de logging
- **JUnit** - Testes unitários
- **Mockito** - Mocks para testes
- **Gradle 4.5.1** - Ferramenta de build
- **Docker** - Containerização (OpenJDK 8 com OpenJ9)
- **JaCoCo** - Cobertura de código
- **SonarQube** - Análise de qualidade de código
- **Bibliotecas internas Votorantim** (springboot-arqt-base-*)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /notificar | NotificacaoFintechApi | Recebe e registra uma notificação de Fintech contendo informações sobre movimentações ou extratos |

---

## 5. Principais Regras de Negócio

1. **Validação de Tipo de Notificação**: O sistema aceita dois tipos de notificação - "1" para Movimentação (código "M") e "2" para Extrato (código "E"). Caso o tipo não seja reconhecido, assume-se Movimentação como padrão.

2. **Conversão de Data**: A data de notificação é recebida como string no formato "yyyy-MM-dd HH:mm:ss" e convertida para objeto Date antes da persistência.

3. **Tratamento de Valores Vazios**: Campos numéricos como código da Fintech e número de protocolo ITP são convertidos para 0 (zero) quando recebidos como string vazia.

4. **Auditoria Automática**: Toda notificação inserida recebe automaticamente a flag ativa "S", data de inclusão com timestamp atual e login "API" como usuário responsável.

5. **Tratamento de Exceções**: Erros durante o processamento são capturados, logados e convertidos em BusinessException com mensagem padronizada.

---

## 6. Relação entre Entidades

**NotificacaoFintech** (Entidade Principal):
- Representa uma notificação registrada no sistema
- Contém informações sobre data de envio, tipo, protocolo ITP, identificação da conta Fintech, CNPJ, descrição, nome do arquivo e dados de auditoria

**Relacionamentos**:
- Não há relacionamentos explícitos com outras entidades no código analisado
- A entidade mapeia diretamente para a tabela TbControleArquivoContaFintech

**DTOs**:
- **NotificacaoFintechRequest**: Objeto de entrada da API
- **NotificacaoFintechResponse**: Objeto de resposta da API
- **TipoNotificacaoEnum**: Enumeração para tipos de notificação

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbControleArquivoContaFintech | Tabela | INSERT | Tabela que armazena as notificações de Fintech, incluindo data de envio, tipo de notificação, protocolo ITP, código da conta Fintech, CNPJ, descrição, nome do arquivo e dados de auditoria (login, flag ativo, datas de inclusão e alteração) |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | Leitura | Configuração Spring Boot | Arquivo de configuração de logs do sistema, carregado em tempo de execução para definir padrões de logging |
| notificacaofintechrepository-sql.xml | Leitura | NotificacaoFintechRepository | Arquivo XML contendo queries SQL utilizadas pelo repositório (carregado via BvSql) |

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
| SQL Server (DBSPAG) | Banco de Dados | Banco de dados principal onde são persistidas as notificações na tabela TbControleArquivoContaFintech |
| LDAP BVNet | Autenticação | Serviço de autenticação LDAP utilizado para validar usuários que acessam a API (configurado via variáveis de ambiente em ambientes não-locais) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Estrutura de camadas bem definida (Controller, Service, Repository)
- Uso adequado de DTOs para separar entrada/saída da API
- Implementação de testes unitários
- Configuração de Swagger para documentação
- Uso de Lombok para reduzir boilerplate
- Tratamento de exceções com logging

**Pontos Negativos:**
- **Violação de princípios SOLID**: O Repository possui lógica de negócio (conversão de tipos, validações) que deveria estar no Service
- **Código comentado**: Testes comentados indicam possível instabilidade ou falta de manutenção
- **Tratamento genérico de exceções**: Captura de Exception genérica ao invés de exceções específicas
- **Falta de validação de entrada**: Não há validação dos dados recebidos na API (Bean Validation)
- **Acoplamento**: Uso de SimpleJdbcInsert diretamente no Repository sem abstração
- **Conversão manual de datas**: Uso de SimpleDateFormat (não thread-safe) ao invés de LocalDateTime/DateTimeFormatter
- **Mensagens hardcoded**: Strings de erro e mensagens não externalizadas
- **Falta de documentação**: Ausência de JavaDoc nas classes principais
- **Testes incompletos**: Teste principal comentado no NotificacaoFintechRepositoryTest

---

## 14. Observações Relevantes

1. **Ambiente de Execução**: O sistema está preparado para execução em containers Docker com OpenJDK 8 e OpenJ9, com configurações específicas de memória (Xms64m, Xmx128m).

2. **Múltiplos Ambientes**: Possui configurações separadas para ambientes local, des, qa, uat e prd, com diferentes configurações de autenticação (LDAP em ambientes não-locais, in-memory para local).

3. **Segurança**: Implementa autenticação básica (Basic Auth) e integração com LDAP corporativo, com controle de roles por ambiente.

4. **Pipeline CI/CD**: Configurado para Jenkins com propriedades específicas (jenkins.properties) e scripts Gradle para build, testes e deploy.

5. **Infraestrutura como Código**: Possui arquivo infra.yml com configurações de probes (liveness e readiness) para Kubernetes/OpenShift.

6. **Cobertura de Testes**: Configurado JaCoCo para análise de cobertura e SonarQube para qualidade de código.

7. **Limitação de Funcionalidade**: O sistema atualmente apenas insere notificações, não há endpoints para consulta, atualização ou exclusão.

8. **Dependências Internas**: Utiliza bibliotecas proprietárias da Votorantim (arqt-base) para trilha de auditoria, segurança e acesso a dados.