---
## Ficha Técnica do Sistema


### 1. Descrição Geral
O sistema **sboot-pgft-base-atom-processamento** é um microserviço atômico desenvolvido em Java com Spring Boot, responsável pelo processamento e gerenciamento de operações relacionadas ao robô PGFT (Plataforma de Gestão Financeira e Tesouraria). O sistema atua como intermediário entre o robô de processamento e o banco de dados, gerenciando o ciclo de vida de lançamentos financeiros, atualizações de status, controle de contas correntes e integração com sistemas legados. Sua principal função é receber requisições REST para incluir, atualizar e consultar dados de processamento, mantendo o controle transacional e a integridade das operações financeiras.


### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ProcessamentoServiceImpl** | Implementa a lógica de negócio para inclusão e atualização de dados de processamento, gerenciando transações e chamadas ao repositório |
| **ProcessamentoController** | Controlador REST que expõe os endpoints da API, recebe requisições HTTP e delega para a camada de serviço |
| **ProcessamentoRepositoryImpl** | Interface de repositório que define operações de banco de dados usando JDBI, com queries SQL externalizadas |
| **ProcessamentoMapper** | Responsável por converter objetos de representação (DTOs) em objetos de domínio |
| **Processamento** | Entidade de domínio que representa os dados de processamento do robô |
| **AtualizarProcessamento** | Entidade de domínio para operações de atualização de status e informações de processamento |
| **ProcessamentoConfiguration** | Classe de configuração Spring que define beans e configurações do JDBI |
| **OpenApiConfiguration** | Configuração do Swagger/OpenAPI para documentação da API |
| **SecureLogUtil** | Utilitário para sanitização de mensagens de log, prevenindo injeção de código |


### 3. Tecnologias Utilizadas
- **Spring Boot 2.x** (framework principal)
- **Spring Web** (REST APIs)
- **Spring JDBC** (acesso a dados)
- **JDBI 3.9.1** (mapeamento objeto-relacional)
- **Sybase jConnect 16.3-SP03-PL07** (driver de banco de dados)
- **Swagger/Springfox 3.0.0** (documentação de API)
- **Lombok** (redução de boilerplate)
- **Micrometer/Prometheus** (métricas e monitoramento)
- **Logback** (logging)
- **JUnit 5** e **Mockito** (testes unitários)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Grafana e Prometheus** (observabilidade)


### 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/banco-digital/processamentos | ProcessamentoController | Inclui novos dados de processamento do robô |
| POST | /v1/banco-digital/atualizarStatusProcessamento | ProcessamentoController | Atualiza o status de processamento de um lançamento |
| POST | /v1/banco-digital/atualizarStatusProcessamentoComErro | ProcessamentoController | Atualiza o status de processamento com erro |
| POST | /v1/banco-digital/atualizarValorLancamento | ProcessamentoController | Atualiza o valor de um lançamento |
| POST | /v1/banco-digital/atualizar/conta-sem-saldo | ProcessamentoController | Atualiza informações de conta sem saldo |
| PUT | /v1/banco-digital/atualizar/descricao-caixa-entrada | ProcessamentoController | Atualiza descrição na caixa de entrada SPB |
| PUT | /v1/banco-digital/atualiza-lancamento/{codigoLancamento} | ProcessamentoController | Atualiza lançamento PGFT com novo status |


### 5. Principais Regras de Negócio
- **Controle de Status de Processamento**: O sistema gerencia diferentes estados de processamento (W-Waiting, R-Read, S-Selected, O-OK, E-Error) para controlar o fluxo de execução do robô
- **Gestão de Tentativas**: Incrementa contador de tentativas quando há falhas, com limite máximo de 999 tentativas
- **Controle de Conta Corrente Processada**: Mantém flag indicando se a conta corrente foi processada (S-Sim, N-Não, E-Estornado)
- **Transacionalidade**: Todas as operações de atualização são transacionais com rollback em caso de exceção
- **Atualização em Cascata**: Ao atualizar status com erro, também atualiza o valor do lançamento automaticamente
- **Sincronização entre Tabelas**: Operações de atualização de lançamento PGFT atualizam múltiplas tabelas (TBL_LANCAMENTO e TbProcessamentoRoboPGFT) de forma atômica
- **Sanitização de Logs**: Utiliza SecureLogUtil para prevenir injeção de código malicioso em logs


### 6. Relação entre Entidades
- **Processamento**: Entidade principal contendo dados completos do processamento (código lançamento, datas, status, descrições, flags)
- **AtualizarProcessamento**: Entidade para operações de atualização, contendo código do lançamento, status, descrição de erro e flag de conta corrente processada
- **Enums**:
  - **StatusProcessamentoEnum**: Define os possíveis status (W, R, S, O, E)
  - **FlContaCorrenteProcessadoEnum**: Define se conta foi processada (S, N, E)
- **Relacionamento**: As entidades se relacionam através do campo `codigoLancamento` que é a chave primária/estrangeira nas operações de banco de dados


### 7. Estruturas de Banco de Dados Lidas
não se aplica (o sistema não realiza operações de leitura/consulta, apenas inserções e atualizações)


### 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbProcessamentoRoboFilaPGFT | tabela | INSERT | Insere novos registros de processamento na fila do robô PGFT |
| TbProcessamentoRoboPGFT | tabela | UPDATE | Atualiza status, datas, erros e flags de processamento do robô |
| TBL_LANCAMENTO | tabela | UPDATE | Atualiza status e flags de lançamentos financeiros |
| tbl_caixa_entrada_spb | tabela | UPDATE | Atualiza descrição de devolução SPB na caixa de entrada |


### 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | leitura | Configuração Spring Boot | Arquivo de configuração de logs (múltiplas versões por ambiente: local, des, qa, uat, prd) |
| application.yml | leitura | Configuração Spring Boot | Arquivo de configuração da aplicação com profiles por ambiente |
| *.sql (8 arquivos) | leitura | ProcessamentoRepositoryImpl | Arquivos SQL com queries externalizadas para operações de banco de dados |
| sboot-pgft-base-atom-processamento.yaml | leitura | OpenApiConfiguration | Especificação OpenAPI/Swagger da API |


### 10. Filas Lidas
não se aplica


### 11. Filas Geradas
não se aplica


### 12. Integrações Externas
- **Banco de Dados Sybase (DBPGF_TES)**: Integração principal com banco de dados Sybase para persistência de dados de processamento, lançamentos e caixa de entrada SPB
- **OAuth2/JWT**: Integração com servidor de autenticação para validação de tokens JWT (URLs variam por ambiente: des, qa, uat, prd)
- **Prometheus/Grafana**: Exposição de métricas via endpoint `/actuator/prometheus` para monitoramento externo


### 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (presentation, business, domain, infrastructure)
- Uso adequado de anotações Lombok para redução de boilerplate
- Queries SQL externalizadas em arquivos separados, facilitando manutenção
- Implementação de testes unitários com boa cobertura
- Uso de transações declarativas com `@Transactional`
- Configuração adequada de segurança com OAuth2/JWT
- Sanitização de logs para prevenir injeção de código

**Pontos de Melhoria:**
- Tratamento de exceções genérico no controller (captura `Exception` e retorna status HTTP genéricos)
- Falta de validação de entrada nos endpoints (não há uso de `@Valid` ou validações customizadas)
- Logs de erro não incluem stack trace completo, dificultando troubleshooting
- Alguns métodos retornam `ResponseEntity<Void>` mas não documentam claramente os códigos de retorno
- Falta de documentação JavaDoc nas classes e métodos principais
- Uso de strings literais para status em alguns pontos ao invés de constantes/enums
- Configuração de banco de dados hardcoded no profile local (credenciais expostas)


### 14. Observações Relevantes
- O sistema utiliza banco de dados Sybase, tecnologia menos comum atualmente, o que pode dificultar manutenção futura
- Há configuração completa de observabilidade com Prometheus e Grafana, incluindo dashboards pré-configurados
- O projeto segue padrões corporativos do Banco Votorantim (namespace `br.com.votorantim`)
- Existe infraestrutura como código (infra-as-code) para deploy em múltiplos ambientes
- O sistema está preparado para execução em containers Docker e Kubernetes/OpenShift
- Há configuração de HikariCP para pool de conexões de banco de dados
- O projeto utiliza arquitetura hexagonal/ports and adapters (interfaces de repositório como ports)
- Configuração de LDAP e proxy está presente mas desabilitada por padrão
- O sistema possui integração com Jenkins para CI/CD (jenkins.properties)