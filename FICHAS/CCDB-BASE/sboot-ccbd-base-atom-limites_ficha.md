---
## Ficha Técnica do Sistema


### 1. Descrição Geral
Sistema atômico de gerenciamento de limites transacionais para operações bancárias do Banco Votorantim. O sistema permite consultar, alterar e controlar limites personalizados e padrões para diferentes tipos de transações (PIX, TED, TEF, Boleto, Débito), considerando divisões comerciais, agências, contas e origens de transação. Implementa controle de limites consumidos por transação e mantém histórico de alterações.


### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **LimitesController** | Controlador REST que expõe endpoints para consulta, alteração e controle de limites |
| **LimiteServiceImpl** | Implementa lógica de negócio para consulta e alteração de limites, incluindo validações |
| **LimitePadraoServiceImpl** | Gerencia consulta de limites padrão por divisão comercial ou divisão topo |
| **LimiteRepositoryImpl** | Interface de acesso a dados para operações de limite personalizado |
| **LimitePadraoRepositoryImpl** | Interface de acesso a dados para limites padrão |
| **HistoricoLimiteRepositoryImpl** | Gerencia inserção de histórico de alterações de limites |
| **LimitesMapper** | Converte entre DTOs de domínio e representações REST |
| **LimiteMapper** | Mapeia ResultSet para entidade Limite |
| **LimitePadraoMapper** | Mapeia ResultSet para entidade LimitePadrao |
| **LimiteConsumidoMapper** | Mapeia ResultSet para resposta de limite consumido |
| **CodigoBancoEnum** | Enumera códigos de bancos (Votorantim, BV S.A.) |
| **TipoLiquidacaoEnum** | Enumera tipos de liquidação (PIX, TED, TEF, BOL, DEB) |
| **ExceptionReasonEnum** | Define códigos e mensagens de erro de negócio |


### 3. Tecnologias Utilizadas
- **Framework**: Spring Boot 2.x
- **Linguagem**: Java 11
- **Persistência**: JDBI 3.9.1 com MySQL 8.0.22
- **Documentação API**: Swagger/OpenAPI 2.0 com Springfox 3.0.0
- **Observabilidade**: Spring Actuator, Micrometer Prometheus
- **Monitoramento**: Grafana + Prometheus
- **Build**: Maven 3.3+
- **Testes**: JUnit 5, Mockito, Rest Assured, Pact
- **Auditoria**: springboot-arqt-base-trilha-auditoria-web 2.2.1
- **Containerização**: Docker com OpenJDK 11 OpenJ9
- **Orquestração**: OpenShift/Kubernetes


### 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | /v1/limite | LimitesController | Consulta limite disponível para conta/agência/banco/origem/tipo liquidação |
| PUT | /v1/limite/atualizar | LimitesController | Altera valor do limite personalizado |
| POST | /v1/limite/controleLimiteConsumido | LimitesController | Registra controle de limite consumido por transação |
| GET | /v1/limite/consulta/controleLimiteConsumido | LimitesController | Consulta limite consumido por NSU de transação |


### 5. Principais Regras de Negócio

1. **Consulta de Limite**: Busca primeiro limite personalizado; se não existir, busca limite padrão por divisão comercial ou divisão topo
2. **Hierarquia de Limites**: Divisão Comercial tem prioridade sobre Divisão Topo na busca de limites padrão
3. **Validação de Limite Máximo**: Ao alterar limite, valida se valor proposto não excede o limite máximo configurado
4. **Histórico de Alterações**: Toda alteração de limite gera registro de histórico antes da atualização
5. **Criação Automática**: Se não existe limite personalizado ao alterar, cria novo registro com limite padrão como máximo
6. **Múltiplos Tipos de Liquidação**: Suporta agrupamento de tipos de liquidação (ex: TED agrupa códigos 31 e 32)
7. **Controle de Consumo**: Registra NSU de limite e NSU de transação para rastreabilidade
8. **Validação de Banco**: Aceita apenas códigos de banco Votorantim (655/161) e BV S.A. (413/436)


### 6. Relação entre Entidades

**Entidades Principais:**
- **Limite**: Representa limite personalizado (1:1 com Agência/Conta/Banco/Origem/TipoLiquidação)
- **LimitePadrao**: Representa limite padrão (1:N com Origem/TipoLiquidação/DivisãoComercial)
- **HistoricoLimite**: Histórico de alterações de limites (N:1 com Limite)
- **ControleLimiteDto**: Controle de limites consumidos por transação (N:1 com Limite)

**Relacionamentos:**
- Limite → HistoricoLimite (1:N) - Um limite pode ter múltiplos históricos
- Limite → ControleLimiteDto (1:N) - Um limite pode ter múltiplos controles de consumo
- LimitePadrao é consultado quando Limite não existe (fallback)


### 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbLimitePersonalizado | tabela | SELECT | Consulta limites personalizados por agência/conta/banco/origem/tipo liquidação |
| TbLimitePadrao | tabela | SELECT | Consulta limites padrão por origem/tipo liquidação/divisão comercial |
| TbControleAumentoLimite | tabela | SELECT | Consulta limites consumidos por agência/conta/banco/NSU transação |


### 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbLimitePersonalizado | tabela | INSERT | Insere novo limite personalizado |
| TbLimitePersonalizado | tabela | UPDATE | Atualiza valor de limite personalizado existente |
| TbLogLimitePersonalizado | tabela | INSERT | Insere histórico de alterações de limite |
| TbControleAumentoLimite | tabela | INSERT | Insere controle de limite consumido por transação |


### 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot | Configuração da aplicação (datasource, profiles, actuator) |
| logback-spring.xml | leitura | Logback | Configuração de logs (console, JSON format) |
| *.sql | leitura | JDBI/SqlLocator | Queries SQL para operações de banco de dados |
| swagger/sboot-ccbd-base-atom-limites.yml | leitura | Swagger Codegen | Especificação OpenAPI para geração de interfaces |


### 10. Filas Lidas
não se aplica


### 11. Filas Geradas
não se aplica


### 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| MySQL (CCBDLIMITES) | Banco de Dados | Persistência de limites, histórico e controles |
| Prometheus | Observabilidade | Coleta de métricas da aplicação |
| Grafana | Monitoramento | Visualização de métricas e dashboards |


### 13. Avaliação da Qualidade do Código

**Nota:** 8/10

**Justificativa:**

**Pontos Positivos:**
- Arquitetura hexagonal bem estruturada (domain, application, infrastructure)
- Separação clara de responsabilidades entre camadas
- Uso adequado de interfaces (ports) para inversão de dependência
- Testes unitários abrangentes com boa cobertura
- Uso de enums para valores fixos (tipos de liquidação, bancos, erros)
- Configuração externalizada e suporte a múltiplos ambientes
- Documentação OpenAPI completa
- Uso de Lombok para redução de boilerplate
- Tratamento de exceções centralizado
- Logs estruturados em JSON

**Pontos de Melhoria:**
- Falta de validação de entrada em alguns endpoints (ex: valores negativos)
- Queries SQL em arquivos separados dificultam manutenção (considerar JPA/Hibernate)
- Ausência de cache para limites padrão (consultados frequentemente)
- Falta de testes de integração com banco de dados real
- Comentários em código poderiam ser mais descritivos
- Ausência de rate limiting nos endpoints


### 14. Observações Relevantes

1. **Segurança**: Sistema utiliza OAuth2 para autenticação (configurado no Swagger)
2. **Multi-tenant**: Suporta múltiplos bancos (Votorantim 655/161 e BV S.A. 413/436)
3. **Auditoria**: Integração com trilha de auditoria do BV (bv-arqt-base-trilha-auditoria-web)
4. **Deployment**: Preparado para OpenShift/Kubernetes com configurações de probes e recursos
5. **Observabilidade**: Endpoints Actuator expostos na porta 9090 (separada da aplicação 8080)
6. **Profiles**: Suporta ambientes local, des, qa, uat, prd
7. **Conexão BD**: Configurada para MySQL com timezone UTC
8. **Usuário BD**: CCBDLIMITES_appl (senha em cofre)
9. **Arquitetura**: Segue padrões de microserviços atômicos do Banco Votorantim
10. **Versionamento**: API versionada (v1) permitindo evolução futura