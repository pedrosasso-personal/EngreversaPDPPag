---
## Ficha Técnica do Sistema


### 1. Descrição Geral
Sistema atômico responsável por consultar feature toggles (flags de funcionalidades) no ConfigCat para o contexto de PIX. O serviço verifica se determinadas funcionalidades estão habilitadas ou desabilitadas e retorna mensagens personalizadas quando uma funcionalidade está desligada, incluindo informações sobre botões de ação e tipos de janela de mensagem para a interface do usuário.


### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot que inicializa a aplicação |
| `ConfigcatPixController` | Controller REST que expõe o endpoint de consulta de toggles |
| `ConsultaConfigcatPixServiceImpl` | Implementação do serviço de domínio que orquestra a consulta de toggles |
| `ConsultaConfigcatPixRepositoryImpl` | Implementação do repositório que integra com o FeatureToggle do ConfigCat |
| `ConfigcatMapper` | Mapper responsável por transformar DTOs em representações de resposta |
| `FeatureToggleConfiguration` | Configuração do provider de Feature Toggle |
| `ConsultaConfigcatPixConfiguration` | Configuração de beans do domínio |
| `BotaoEnum` | Enumeração com os tipos de botões disponíveis |
| `SucessoRetonoEnum` | Enumeração com mensagens de retorno quando toggles estão desligados |
| `TipoJanelaMensagemEnum` | Enumeração com tipos de janelas de mensagem (Dialog, Page) |


### 3. Tecnologias Utilizadas
- **Framework:** Spring Boot 2.x
- **Java:** JDK 11
- **Build:** Maven
- **Servidor de Aplicação:** Undertow (embedded)
- **Documentação API:** Swagger/OpenAPI (Springfox 3.0.0)
- **Feature Toggle:** ConfigCat (via biblioteca `sbootlib-arqt-base-feature-toggle` versão 1.0.1)
- **Observabilidade:** Spring Actuator, Micrometer, Prometheus
- **Monitoramento:** Grafana (configurado em docker-compose)
- **Logging:** Logback com suporte a JSON
- **Testes:** JUnit 5, Mockito, RestAssured, Pact
- **Containerização:** Docker
- **Orquestração:** OpenShift/Kubernetes
- **Auditoria:** `springboot-arqt-base-trilha-auditoria-web` versão 2.2.1
- **Segurança:** `sboot-arqt-base-security-auto` versão 0.18.0
- **Tracing:** `sbootlib-arqt-base-tracing` versão 0.2.0


### 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/banco-digital/pix/configcat/consultar` | `ConfigcatPixController` | Consulta o status de um toggle no ConfigCat e retorna se está ativo ou desativo, incluindo mensagem personalizada quando desligado |


### 5. Principais Regras de Negócio
1. **Consulta de Feature Toggles:** O sistema consulta o ConfigCat para verificar se uma funcionalidade específica está habilitada ou desabilitada através de uma chave (valorToggle).

2. **Retorno Condicional:** Quando um toggle está ativo (true), retorna apenas o valor booleano. Quando está inativo (false), retorna uma estrutura completa com mensagem, título, botões de ação e tipo de janela.

3. **Mensagens Pré-configuradas:** Existem 4 tipos de mensagens pré-configuradas para diferentes contextos:
   - `TGHOMEDESLIGADO`: Área de limites indisponível (home)
   - `TGPERIODODESLIGADO`: Área de limites indisponível (período)
   - `TGTRANSACAODESLIGADO`: Área de limites indisponível (transação)
   - `TGCONTASEGURADESLIGADO`: Área de Conta Segura indisponível

4. **Botões de Ação:** Cada mensagem possui botões primários e secundários configurados, como "Voltar para o início", "Tentar de novo", "Ir para tela inicial", etc.

5. **Tipos de Janela:** As mensagens podem ser exibidas em diferentes formatos (DIALOG ou PAGE) com imagens específicas (tapumes de atenção, erro, transação incompleta).

6. **Cache de Toggles:** O sistema utiliza cache lazy load com duração configurável (padrão 60 segundos em produção, 5 segundos em outros ambientes).


### 6. Relação entre Entidades

**Entidades de Domínio:**
- `ConsultaConfigcatPix`: Entidade principal com id e version
- `ConfigCatDTO`: DTO com valorToggle (String) e isToggle (Boolean)

**Enumerações:**
- `BotaoEnum`: Contém id, titulo (10 tipos de botões)
- `SucessoRetonoEnum`: Contém codigo, titulo, mensagem, janela, botaoPrimario, botoes
- `TipoJanelaMensagemEnum`: Contém imagem, tipo (DIALOG, PAGE)

**Relacionamentos:**
- `SucessoRetonoEnum` → `TipoJanelaMensagemEnum` (composição)
- `SucessoRetonoEnum` → `BotaoEnum` (lista de botões)
- `ConfigCatDTO` → mapeado para `ResponseToggleRepresentation` via `ConfigcatMapper`


### 7. Estruturas de Banco de Dados Lidas

não se aplica


### 8. Estruturas de Banco de Dados Atualizadas

não se aplica


### 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `application.yml` | leitura | Spring Boot | Arquivo de configuração da aplicação com profiles (local, des, qa, uat, prd) |
| `logback-spring.xml` | leitura | Logback | Configuração de logs (console e arquivo) |
| `sboot-ccbd-base-atom-consulta-configcat-pix.yaml` | leitura | Swagger Codegen | Especificação OpenAPI para geração de código |


### 10. Filas Lidas

não se aplica


### 11. Filas Geradas

não se aplica


### 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| **ConfigCat** | Feature Toggle Service | Serviço de gerenciamento de feature flags. A integração é feita através da biblioteca `sbootlib-arqt-base-feature-toggle` que utiliza chaves de API específicas por ambiente (des, qa, uat, prd). O sistema consulta flags booleanas para controlar funcionalidades de PIX. |
| **Prometheus** | Métricas | Exportação de métricas da aplicação via endpoint `/actuator/prometheus` para monitoramento. |


### 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura hexagonal (domain, application, infrastructure)
- Uso adequado de enums para representar estados e mensagens
- Testes unitários presentes para as principais classes
- Configuração adequada de profiles para diferentes ambientes
- Uso de Lombok para reduzir boilerplate
- Documentação OpenAPI/Swagger bem estruturada
- Configuração de observabilidade (Actuator, Prometheus, Grafana)

**Pontos de Melhoria:**
- Tratamento de exceções genérico no controller (retorna null em caso de erro, deveria retornar ResponseEntity apropriado)
- Falta de validação de entrada no endpoint (parâmetro `valorToggle` não é validado)
- Código comentado na classe `FeatureToggleConfiguration` deveria ser removido
- Falta de logs estruturados em pontos críticos (apenas log de toggle no mapper)
- Classe `ConsultaConfigcatPix` do domínio não é utilizada efetivamente
- Alguns testes estão vazios ou incompletos (ex: `ConsultaConfigcatPixApiFunctionalTest`)
- Falta de documentação inline em métodos mais complexos (especialmente no mapper)
- Configuração de segurança presente mas não há evidência de uso efetivo


### 14. Observações Relevantes

1. **Ambientes:** O sistema está preparado para rodar em múltiplos ambientes (local, des, qa, uat, prd) com chaves ConfigCat específicas para cada um.

2. **Containerização:** Dockerfile otimizado usando OpenJ9 com configurações de memória ajustáveis via variável de ambiente `JAVA_OPTS`.

3. **Infraestrutura como Código:** Arquivo `infra.yml` contém configurações para deploy em OpenShift/Kubernetes, incluindo probes de liveness e readiness.

4. **Monitoramento:** Stack completa de monitoramento com Prometheus e Grafana configurada via docker-compose, com dashboard pré-configurado para métricas Spring Boot.

5. **CI/CD:** Arquivo `jenkins.properties` indica integração com pipeline Jenkins para build e deploy automatizado.

6. **Arquitetura:** Projeto multi-módulo Maven (common, domain, application) seguindo princípios de Clean Architecture.

7. **Feature Toggle:** A biblioteca de Feature Toggle suporta dois modos: LAZY (com cache) e polling mode configurável por ambiente.

8. **Segurança:** Integração com LDAP e certificados globais configurados via volumes no Kubernetes.

9. **Auditoria:** Trilha de auditoria habilitada através da biblioteca `springboot-arqt-base-trilha-auditoria-web`.

10. **Timezone:** Container configurado para adicionar suporte a timezone (apk add tzdata).