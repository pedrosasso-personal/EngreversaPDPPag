---
## Ficha Técnica do Sistema

### 1. Descrição Geral
Sistema de efetivação de transferências bancárias TED (Transferência Eletrônica Disponível) desenvolvido em Spring Boot com arquitetura hexagonal. O sistema orquestra o fluxo completo de transferências TED, incluindo validações de limites, grade horária, integração com sistema antifraude, efetivação ou agendamento da operação, e notificações. Suporta múltiplas versões de API (v2, v3, v4, v5) com evoluções incrementais, sendo a v5 a mais recente com integração obrigatória ao sistema antifraude.

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **EfetTransfTEDBusiness** | Orquestra o fluxo completo de efetivação de TED: validações, limites, efetivação/agendamento, notificações |
| **EfetTransfTEDControllerV2/V3/V4/V5** | Endpoints REST para efetivação de TED em diferentes versões da API |
| **EfetuarTransfTEDService** | Serviço que encapsula chamadas às rotas Camel para processamento |
| **EfetTransfTEDRouter** | Rota Camel principal que orquestra todo o fluxo de transferência |
| **ApplicationConfiguration** | Configuração de clients REST para integração com serviços externos |
| **RabbitMQConfiguration** | Configuração de mensageria RabbitMQ com conversores JSON |
| **ExceptionControllerHandler** | Handler centralizado de exceções com mapeamento para códigos de erro |
| **PagamentoTedConversor** | Converte representações v4 para domain e monta mensagens para fila |
| **EfetTedConversor** | Converte requests/responses entre camadas de apresentação e domínio |
| **LimitesRepositoryImpl** | Consulta limites transacionais disponíveis |
| **GradeHorariaTEDRepositoryImpl** | Valida horário operacional e calcula próxima data útil |
| **EnviarTEDRepositoryImpl** | Publica mensagens de efetivação na fila RabbitMQ |
| **NotificacaoFraudesImpl** | Notifica sistema de fraudes sobre status da transação |

### 3. Tecnologias Utilizadas

- **Framework Principal**: Spring Boot 2.x
- **Segurança**: Spring Security OAuth2 (Resource Server), JWT
- **Mensageria**: RabbitMQ com Spring AMQP
- **Orquestração**: Apache Camel 3.2.0
- **Documentação API**: Swagger/OpenAPI
- **Monitoramento**: Spring Actuator, Prometheus, Grafana
- **Build**: Maven
- **Containerização**: Docker
- **Testes**: JUnit, Mockito, ArchUnit
- **Qualidade**: Jacoco (cobertura de código)
- **Bibliotecas**: Lombok, Apache Commons Lang 3, Jackson
- **Geração de Código**: swagger-codegen-maven-plugin
- **JDK**: OpenJDK 11 (OpenJ9)

### 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v2/transferencia-bancaria/doc-ted | EfetTransfTEDControllerV2 | Efetiva/agenda TED com validações básicas |
| POST | /v3/transferencia-bancaria/doc-ted | EfetTransfTEDControllerV3 | Versão com camada de negócio refatorada |
| POST | /v4/transferencia-bancaria/doc-ted | EfetTransfTEDControllerV4 | Versão com representações v4 otimizadas |
| POST | /v5/transferencia-bancaria/doc-ted | EfetTransfTEDControllerV5 | Versão com integração obrigatória ao antifraude via header idTransacao |

### 5. Principais Regras de Negócio

1. **Validação de Data**: Não permite transferências com data retroativa; valida formato de data
2. **Validação de Limites**: Verifica limite diário disponível antes de efetivar; se insuficiente, sugere agendamento para próximo dia útil
3. **Grade Horária**: Valida se operação está dentro do horário operacional TED; se fora do horário, redireciona automaticamente para agendamento
4. **Agendamento Automático**: Quando limite diário excedido ou fora da grade horária, calcula próxima data útil e agenda automaticamente
5. **Normalização de Agência**: Agências com 3 dígitos são completadas com zero à esquerda
6. **Mapeamento de Bancos**: Bancos específicos são convertidos para ITP (161→655 Votorantim, 436→413 BVSA)
7. **Antifraude (v5)**: Consulta obrigatória ao sistema de fraudes antes da efetivação; bloqueia operação se status não for APROVADA
8. **Favorecidos**: Permite salvar favorecido opcionalmente após efetivação bem-sucedida
9. **Geração de NSU**: Gera NSU único para cada transação
10. **Notificações**: Envia notificações de status para sistema de fraudes via fila RabbitMQ
11. **Retry de Notificações**: Sistema de retry (17 tentativas, delay 500ms) para notificações de fraude

### 6. Relação entre Entidades

**Entidades Principais:**

- **EfetuarTransferenciaDTO**: Entidade central contendo dados completos da transferência (remetente, favorecido, valor, data, finalidade)
- **OperacaoTransferenciaTEDDTO**: Representa o resultado da operação (protocolo, NSU, NCU, dados efetivação)
- **Participante/ParticipanteTedResponse**: Dados de remetente e favorecido (nome, CPF/CNPJ, banco, agência, conta)
- **LimiteDTO/LimiteDiarioResponse**: Informações de limites transacionais (disponível, total, autorizado)
- **StatusFraudeTedResponse**: Status da análise de fraude da transação
- **MsgEfetivarTedDTO**: Mensagem para fila de efetivação assíncrona

**Relacionamentos:**
- EfetuarTransferenciaDTO contém 2 Participantes (remetente e favorecido)
- OperacaoTransferenciaTEDDTO referencia dados de remetente e favorecido
- StatusFraudeTedResponse contém PayloadTedResponse com detalhes da transação
- MsgEfetivarTedDTO é derivado de EfetuarTransferenciaDTO para processamento assíncrono

### 7. Estruturas de Banco de Dados Lidas

não se aplica

*Observação: O sistema não acessa banco de dados diretamente, toda persistência é realizada via APIs de serviços externos.*

### 8. Estruturas de Banco de Dados Atualizadas

não se aplica

*Observação: O sistema não atualiza banco de dados diretamente, todas as operações de escrita são realizadas via APIs de serviços externos.*

### 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot | Configurações da aplicação (URLs, credenciais, RabbitMQ) |
| rabbitmq.conf | leitura | Docker Compose | Configurações do RabbitMQ |
| rabbitmq_definitions.json | leitura | Docker Compose | Definições de filas, exchanges e bindings |
| infra.yml | leitura | OpenShift | Configurações de infraestrutura por ambiente |
| jenkins.properties | leitura | Jenkins CI/CD | Propriedades de build e deploy |

### 10. Filas Lidas

não se aplica

*Observação: O sistema não consome mensagens de filas, apenas publica.*

### 11. Filas Geradas

| Nome da Fila/Exchange | Routing Key | Tipo de Mensagem | Descrição |
|-----------------------|-------------|------------------|-----------|
| ex.ccbd.eventos.transacional | ccbd.rk.transacional.envio.spag.transferencia.ted | MsgEfetivarTedDTO | Fila para efetivação assíncrona de TED no sistema SPAG |
| exchangeFraudes (ex.ccbd.notificacao.fraudes) | ccbd.atualizarStatusFraude.v1 | StatusFraudeTedResponse | Fila para notificação de status de fraude ao sistema antifraude |

### 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| **ESB Legado (JBoss)** | REST/JSON-RPC | Agendamento de transferências TED via facade legado |
| **SPAG Transferências** | REST | Efetivação de transferências bancárias (TransferenciaApi) |
| **Global Dados Cadastrais** | REST | Consulta de dados cadastrais do titular da conta (GetContasByNuContaApi) |
| **Global Lista Bancos** | REST | Consulta de lista de bancos com ordenação configurável (ConsultarBancosApi) |
| **Serviço Grade Horária** | REST | Validação de horário operacional TED e cálculo de próxima data útil |
| **Serviço Limites** | REST | Consulta de limites transacionais diários e de agendamento |
| **Serviço Validação TED** | REST | Validação de regras de negócio antes da efetivação |
| **API Pagamentos (Movimento)** | REST | Débito/crédito em conta corrente (MovimentoApi) |
| **API Contatos** | REST | Salvamento de contatos/favorecidos (ContatosApi) |
| **API Favorecidos** | REST | Salvamento de favorecidos no sistema legado |
| **Gestão Transações (Antifraude)** | REST | Consulta de status de análise de fraude por idTransacao |
| **Envio Push Orchestrator** | REST | Envio de notificações push mobile (Deprecated) |

### 13. Avaliação da Qualidade do Código

**Nota: 7,5/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura hexagonal bem definida com separação clara entre camadas (presentation, business, domain, repository)
- Uso adequado de padrões de projeto (Repository, Service, Converter)
- Boa cobertura de testes unitários para componentes críticos
- Versionamento de API bem estruturado (v2, v3, v4, v5)
- Uso de enums para constantes e códigos de erro, facilitando manutenção
- Tratamento centralizado de exceções com mapeamento para códigos de negócio
- Configuração externalizada via properties
- Uso de Lombok reduzindo boilerplate

**Pontos de Melhoria:**
- Forte acoplamento com serviços legado via ESB JSON-RPC dificulta evolução
- Múltiplas versões de API coexistindo aumentam complexidade de manutenção
- Uso de Apache Camel para orquestração pode ser excessivo para o caso de uso
- Classe NotificacaoPushImpl marcada como @Deprecated mas ainda presente no código
- Conversores com lógica de negócio (ex: tratamento de bancos específicos) poderiam estar em services
- Falta de documentação inline em classes complexas
- Alguns métodos com múltiplas responsabilidades (ex: EfetTransfTEDBusiness.efetuarTransferenciaTed)
- Configuração de retry hardcoded em rotas Camel (17 tentativas, 500ms)

### 14. Observações Relevantes

1. **Evolução de Versões**: O sistema mantém 4 versões de API simultaneamente (v2, v3, v4, v5), sendo v5 a mais recente com integração obrigatória ao antifraude. Recomenda-se plano de deprecação das versões antigas.

2. **Arquitetura de Mensageria**: Utiliza RabbitMQ para processamento assíncrono de efetivação de TED, desacoplando a resposta ao cliente da efetivação real no sistema SPAG.

3. **Sistema Antifraude**: A partir da v5, toda transação deve passar por análise de fraude antes da efetivação. O sistema consulta status via idTransacao e bloqueia operações não aprovadas.

4. **Resiliência**: Implementa retry automático (17 tentativas) para notificações de fraude, garantindo entrega eventual da mensagem.

5. **Infraestrutura**: Configurado para deploy em OpenShift com probes de liveness (420s) e readiness (3s), suportando ambientes des/qa/uat/prd.

6. **Monitoramento**: Integrado com Prometheus e Grafana para métricas, além de Spring Actuator para health checks.

7. **Segurança**: Utiliza OAuth2 Resource Server com JWT para autenticação e autorização de requisições.

8. **Limitações de Recursos**: Container configurado com JVM limitada (Xms64m, Xmx128m), adequado para microserviço mas pode ser restritivo sob alta carga.

9. **Dependência de Serviços Legado**: Sistema fortemente dependente de facade legado (JBoss) para agendamentos, representando risco de acoplamento e dificuldade de evolução.

10. **Qualidade de Código**: Projeto utiliza ArchUnit para validação de regras arquiteturais e Jacoco para cobertura de testes, demonstrando preocupação com qualidade.