# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema orquestrador responsável por notificar parceiros (fintechs) sobre o status de pagamentos processados no sistema SPAG (Sistema de Pagamentos) do Banco Votorantim. O sistema consome mensagens de filas RabbitMQ contendo informações de lançamentos de pagamento, notifica os parceiros através de callbacks HTTP, e registra os envios, retornos e erros em um sistema atômico de notificações. Suporta diferentes tipos de liquidação (TED, DOC, Boletos, Tributos, Concessionárias) e implementa mecanismo de retentativas com controle de tentativas.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot que inicializa a aplicação |
| `MainService` | Orquestra o fluxo principal de notificação: recebe mensagem da fila, notifica parceiro, registra envio/retorno/erro |
| `FilasRabbitListener` | Listener RabbitMQ que consome mensagens da fila de notificação de pagamentos |
| `NotificarParceiroRepositoryImpl` | Implementa chamadas HTTP aos endpoints de notificação dos parceiros (com e sem mTLS) |
| `NotificacaoRepositoryImpl` | Implementa chamadas HTTP aos serviços atômicos de registro de notificações |
| `NotificarQueueParceiroImpl` | Gerencia envio de mensagens para filas RabbitMQ (retentativas e mock) |
| `NotificarParceiroController` | Controller REST para endpoint de teste/mock de notificação |
| `LancamentoNotificarMapper` | Mapeia representações de lançamentos entre camadas |
| `NotificacaoEnvioMapper` | Mapeia DTOs de envio de notificação |
| `NotificacaoRetornoMapper` | Mapeia DTOs de retorno de notificação |
| `NotificacaoErroMapper` | Mapeia DTOs de erro de notificação |
| `FeatureToggleUtils` | Gerencia feature toggles (ConfigCat) para habilitar/desabilitar funcionalidades |
| `CamelContextWrapper` | Wrapper do Apache Camel para orquestração de rotas |
| `NotificacaoRouter` | Define rotas Camel para operações de notificação |
| `NotificarParceiroRouter` | Define rota Camel para fluxo de orquestração |

---

## 3. Tecnologias Utilizadas

- **Framework**: Spring Boot 2.x
- **Linguagem**: Java 11
- **Mensageria**: RabbitMQ (Spring AMQP)
- **Orquestração**: Apache Camel
- **HTTP Client**: RestTemplate
- **Documentação API**: Swagger/OpenAPI 3.0 (Springfox)
- **Segurança**: OAuth2 (JWT), mTLS (feature toggle)
- **Feature Toggle**: ConfigCat
- **Monitoramento**: Spring Actuator, Micrometer Prometheus
- **Testes**: JUnit 5, Mockito, RestAssured, Pact
- **Build**: Maven
- **Containerização**: Docker
- **Infraestrutura**: Kubernetes (Google Cloud Platform)
- **Logging**: Logback
- **Serialização**: Gson, Jackson

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/notificar-pagamento/` | `NotificarParceiroController` | Endpoint de teste/mock para enviar mensagem de notificação para a fila |

**Observação**: Este é um serviço orientado a eventos (event-driven), com processamento assíncrono via RabbitMQ. O endpoint REST é principalmente para testes.

---

## 5. Principais Regras de Negócio

1. **Controle de Retentativas**: Sistema verifica quantidade de tentativas de processamento através do header `x-death` do RabbitMQ. Se exceder o limite configurado (`quantidadeRetentativas`), registra erro e não reenvia.

2. **Roteamento por Tipo de Liquidação**: 
   - Tributos (código 59) e Concessionárias (código 60) utilizam endpoint específico e formato diferente de notificação
   - Demais tipos (TED, DOC, Boletos) utilizam endpoint padrão

3. **Feature Toggle para mTLS**: Sistema verifica toggles do ConfigCat para decidir se usa autenticação mTLS ou OAuth2 padrão na comunicação com parceiros.

4. **Registro Triplo de Notificação**:
   - Registra envio da notificação (TB_NOTIFICACAO_FINTECH)
   - Registra retorno do parceiro (TB_CONTROLE_RETORNO_NOTIFICACAO)
   - Em caso de falha após retentativas, registra erro (TB_NOTIFICACAO_ERRO_FINTECH)

5. **Enriquecimento de Dados para Tributos**: Para pagamentos de tributos, busca informações adicionais (wallet) antes de notificar o parceiro.

6. **Sanitização de Logs**: Dados sensíveis são sanitizados antes de serem logados.

7. **Tratamento de Exceções HTTP**: Diferentes status HTTP (422, 500, 404, 401) são tratados e mapeados para exceções específicas de negócio.

---

## 6. Relação entre Entidades

**Entidades de Domínio Principais**:

- **LancamentoNotificarParceiroDTO**: Representa dados de um lançamento de pagamento a ser notificado (TED, DOC, Boletos)
  - Contém: endpoint do cliente, usuário, protocolo, status, autenticação, datas

- **LancamentoNotificarTributoParceiroDTO**: Representa dados de um lançamento de tributo/concessionária
  - Contém: campos similares ao DTO padrão, mas com estrutura específica para tributos

- **NotificacaoEnvioDTO**: Representa registro de envio de notificação
  - Relaciona-se com: código de lançamento, código de liquidação

- **NotificacaoRetornoDTO**: Representa registro de retorno da notificação
  - Relaciona-se com: NotificacaoEnvioDTO (via cdNotificacaoFintech)

- **NotificacaoErroFintechDTO**: Representa registro de erro na notificação
  - Contém: protocolo, mensagem de erro, dados do parceiro

- **NotificacaoWallet**: Representa dados complementares de wallet para tributos
  - Relaciona-se com: código de lançamento

**Relacionamentos**:
- Um Lançamento gera uma NotificacaoEnvio
- Uma NotificacaoEnvio gera um NotificacaoRetorno
- Falhas após retentativas geram NotificacaoErroFintech
- Lançamentos de Tributos requerem consulta a NotificacaoWallet

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TB_NOTIFICACAO_WALLET_TRIBUTOS | tabela | SELECT | Consulta dados complementares de wallet para notificação de tributos (via serviço atômico) |

**Observação**: As leituras são realizadas através de chamadas HTTP a serviços atômicos, não há acesso direto ao banco de dados.

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TB_NOTIFICACAO_FINTECH | tabela | INSERT | Registra envio de notificação ao parceiro (via serviço atômico) |
| TB_CONTROLE_RETORNO_NOTIFICACAO | tabela | INSERT | Registra retorno recebido do parceiro após notificação (via serviço atômico) |
| TB_NOTIFICACAO_ERRO_FINTECH | tabela | INSERT | Registra erros de notificação quando retentativas são excedidas (via serviço atômico) |

**Observação**: As inserções são realizadas através de chamadas HTTP a serviços atômicos (`sboot-spag-base-atom-notifica-pagamento`), não há acesso direto ao banco de dados.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `logback-spring.xml` | leitura | `/usr/etc/log` (runtime) | Configuração de logging da aplicação |
| `application.yml` | leitura | `src/main/resources` | Configurações principais da aplicação |
| `application-local.yml` | leitura | `src/main/resources` | Configurações específicas para ambiente local |
| `sboot-spag-base-orch-notificar-parceiro.yml` | leitura | `src/main/resources/swagger` | Especificação OpenAPI/Swagger da API |

---

## 10. Filas Lidas

**Fila Principal**:
- **Nome**: `events.business.SPAG-BASE.notificacaoPagamentoApi`
- **Exchange**: `events.business.notificacaoPagamentoApi`
- **Routing Key**: `SPAG.rk.notificacaoPagamentoApi`
- **Listener**: `FilasRabbitListener.queueGetDadosParceiroToNotificacao`
- **Descrição**: Consome mensagens contendo dados de lançamentos de pagamento que precisam ser notificados aos parceiros
- **Configuração**: Concurrent consumers configurável, recovery interval de 10s

---

## 11. Filas Geradas

**Fila de Retentativa (DLQ/Waiting)**:
- **Nome**: `events.business.SPAG-BASE.notificacaoPagamentoApiWaiting`
- **Routing Key**: `SPAG.rk.notificacaoPagamentoApiDLQ`
- **Método**: `NotificarQueueParceiroImpl.enviarMensagemWaitingNotificar`
- **Descrição**: Fila para retentativas de mensagens que falham no processamento

**Fila de Mock/Teste**:
- **Exchange**: `events.business.notificacaoPagamentoApi`
- **Routing Key**: `SPAG.rk.notificacaoPagamentoApi`
- **Método**: `NotificarQueueParceiroImpl.enviarMensagemMock`
- **Descrição**: Utilizada para testes, envia mensagens de volta para a fila principal

---

## 12. Integrações Externas

**APIs Integradas**:

1. **API Gateway de Notificação de Parceiros**
   - **Endpoint Padrão**: `${API_GATEWAY}/v1/atacado/notificar-pagamento`
   - **Endpoint mTLS**: `${API_GATEWAY}/v1/atacado/notificar-pagamento` (com autenticação mTLS)
   - **Endpoint Tributos**: `${API_GATEWAY}/v1/atacado/gestao/pagamento-tributo-consumo/confirmar`
   - **Método**: POST
   - **Autenticação**: OAuth2 JWT ou mTLS (via feature toggle)
   - **Descrição**: Notifica parceiros sobre status de pagamentos

2. **Serviço Atômico de Notificação - Envio**
   - **Endpoint**: `${SPAG_ATOM_NOTIFICAR_PAGAMENTO_URL}/v1/inserirNotificacaoFintech`
   - **Método**: POST
   - **Descrição**: Registra envio de notificação na base de dados

3. **Serviço Atômico de Notificação - Retorno**
   - **Endpoint**: `${SPAG_ATOM_NOTIFICAR_PAGAMENTO_URL}/v1/inserirControleRetornoNotificacao`
   - **Método**: POST
   - **Descrição**: Registra retorno recebido do parceiro

4. **Serviço Atômico de Notificação - Erro**
   - **Endpoint**: `${SPAG_ATOM_NOTIFICAR_PAGAMENTO_URL}/v1/inserirNotificacaoErroFintech`
   - **Método**: POST
   - **Descrição**: Registra erros de notificação

5. **Serviço Atômico de Notificação - Wallet Tributos**
   - **Endpoint**: `${SPAG_ATOM_NOTIFICAR_PAGAMENTO_URL}/v1/obterNotificacaoParceiroWalletTributos/{cdLancamento}`
   - **Método**: GET
   - **Descrição**: Busca dados complementares de wallet para notificação de tributos

6. **ConfigCat (Feature Toggle)**
   - **Serviço**: ConfigCat
   - **Chave**: Configurada via variável de ambiente `FT_KEY`
   - **Descrição**: Gerencia feature toggles para habilitar/desabilitar funcionalidades (ex: mTLS)

7. **OAuth2 Token Service**
   - **Endpoint**: `${API_GATEWAY}/auth/oauth/v2/token-jwt`
   - **Descrição**: Serviço de autenticação para obtenção de tokens JWT

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (domain, application)
- Uso adequado de padrões como Repository, Mapper, DTO
- Cobertura de testes unitários presente
- Uso de feature toggles para controle de funcionalidades
- Tratamento de exceções estruturado com enums
- Configuração externalizada
- Uso de Apache Camel para orquestração

**Pontos de Melhoria:**
- Código comentado em vários locais (ex: `NotificacaoRepositoryImpl`, `MainService`)
- Alguns métodos muito longos e com múltiplas responsabilidades (ex: `MainService.processarNotificacaoParceiro`)
- Uso de `System.setProperty` em código de produção (`NotificarParceiroRepositoryImpl`)
- Tratamento de exceções genérico em alguns pontos (catch Exception)
- Falta de documentação JavaDoc em várias classes
- Alguns nomes de variáveis poderiam ser mais descritivos
- Uso de `@SneakyThrows` que oculta tratamento de exceções
- Lógica de negócio misturada com infraestrutura em alguns pontos
- Código de teste com dependências de ambiente (variáveis de sistema)

---

## 14. Observações Relevantes

1. **Arquitetura Event-Driven**: Sistema fortemente baseado em processamento assíncrono via RabbitMQ, com padrão de retentativas e DLQ.

2. **Feature Toggles Críticos**: 
   - `ft_boolean_spag_base_mtls_toggle`: Habilita/desabilita mTLS globalmente
   - `ft_string_spag_base_mtls_toggle`: Lista de parceiros específicos que usam mTLS

3. **Ambientes Suportados**: DES, QA, UAT, PRD com configurações específicas por ambiente.

4. **Infraestrutura Cloud**: Aplicação preparada para deploy em Kubernetes no Google Cloud Platform.

5. **Monitoramento**: Endpoints Actuator expostos na porta 9090 para health checks e métricas Prometheus.

6. **Segurança**: Suporte a OAuth2 JWT e mTLS, com sanitização de logs para dados sensíveis.

7. **Versionamento**: Projeto na versão 0.8.0, indicando ainda em fase de desenvolvimento/estabilização.

8. **Dependências Internas**: Forte dependência de serviços atômicos do SPAG para persistência de dados.

9. **Padrão de Nomenclatura**: Segue convenções do Banco Votorantim (prefixo `sboot-spag-base`).

10. **Documentação**: README.md presente com instruções de setup e links para documentação corporativa no Confluence.