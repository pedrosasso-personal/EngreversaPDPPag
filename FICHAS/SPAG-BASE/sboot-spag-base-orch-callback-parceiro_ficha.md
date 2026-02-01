# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema orquestrador de callbacks de parceiros para o SPAG (Sistema de Pagamentos). O componente é responsável por receber notificações de pagamentos via fila RabbitMQ, consultar APIs de parceiros para confirmação/rejeição de transações, e direcionar o fluxo para os orquestradores específicos (transferências, boletos ou tributos) conforme o tipo de liquidação. Implementa mecanismo de retry com controle de tentativas e registra todo o histórico de retorno de solicitações.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **MainService** | Serviço principal que orquestra todo o fluxo de callback: recebe mensagens da fila, enriquece dados se necessário, chama API do parceiro, registra retorno e direciona para orquestrador específico |
| **FilasRabbitListener** | Listener RabbitMQ que consome mensagens das filas de callback e notificação de esteira |
| **CallbackParceiroRepositoryImpl** | Implementa chamadas HTTP para APIs de callback de parceiros (padrão e tributos) |
| **CallbackQueueParceiroImpl** | Gerencia envio de mensagens para filas RabbitMQ (waiting, notificação esteira) |
| **PagamentoRepositoryImpl** | Consulta detalhes de pagamento via API atom-pagamento |
| **ParceriaRepositoryImpl** | Busca informações de parceria (URL callback, usuário API) |
| **RetornoSolicitacaoRepositoryImpl** | Registra retorno de solicitação e controle de retorno no atom-callback-parceiro |
| **TransferenciaRepositoryImpl** | Envia confirmação para orquestrador de transferências |
| **BoletoRepositoryImpl** | Envia confirmação para orquestrador de boletos |
| **TributosRepositoryImpl** | Envia confirmação para orquestrador de tributos |
| **LancamentoCallbackMapper** | Mapeia representações de lançamento para DTOs de domínio |
| **RetornoSolicitacaoMapper** | Mapeia dados para entidades de retorno de solicitação e controle |
| **CallbackParceirosController** | Controller REST para endpoints de callback (mock e notificação esteira) |
| **CamelContextWrapper** | Wrapper do Apache Camel para roteamento de mensagens |
| **LiquidacaoEnum** | Enum que identifica tipos de liquidação (TED, DOC, Boleto, Tributos) |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.x** (framework base)
- **Java 11**
- **Apache Camel 3.2.0** (roteamento e integração)
- **RabbitMQ** (mensageria assíncrona)
- **Spring AMQP** (integração com RabbitMQ)
- **RestTemplate** (cliente HTTP)
- **Swagger/OpenAPI 3.0** (documentação de API)
- **Springfox 3.0.0** (geração de documentação)
- **Lombok** (redução de boilerplate)
- **JUnit 5** (testes unitários)
- **Mockito** (mocks em testes)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Kubernetes/OpenShift** (orquestração de containers)
- **ConfigCat/Feature Toggle** (gerenciamento de features)
- **Prometheus/Micrometer** (métricas)
- **Logback** (logging)
- **Jackson** (serialização JSON)
- **Gson** (serialização JSON alternativa)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/callback-parceiro/ | CallbackParceirosController | Recebe callback de parceiro e envia para fila (mock/teste) |
| POST | /v1/notificar-esteira/ | CallbackParceirosController | Recebe notificação para processar callback na esteira |
| GET | /actuator/health | Spring Actuator | Health check da aplicação |
| GET | /actuator/metrics | Spring Actuator | Métricas da aplicação |
| GET | /actuator/prometheus | Spring Actuator | Métricas no formato Prometheus |

---

## 5. Principais Regras de Negócio

1. **Controle de Tentativas**: Máximo de 3 tentativas de processamento de callback. Após exceder, rejeita o pagamento automaticamente (retornoConfirmacao = 1)

2. **Enriquecimento de Dados**: Se a mensagem não contém dados do parceiro (clienteEndPoint), busca informações de pagamento e parceria antes de processar

3. **Roteamento por Liquidação**: Direciona callback para orquestrador específico baseado no código de liquidação:
   - Transferências (TED/DOC/TEF): códigos 1, 21, 31, 32
   - Boletos: código 22
   - Tributos/Concessionárias: códigos 59, 60

4. **Registro de Auditoria**: Grava em TbRetornoSolicitacaoFintech e TbControleRetornoSlctoFintech todo histórico de chamadas ao parceiro

5. **Feature Toggle mTLS**: Utiliza toggle para determinar se parceiro usa autenticação mTLS (ft_string_spag_base_mtls_toggle)

6. **Retry com Waiting Queue**: Em caso de falha, envia mensagem para fila waiting para reprocessamento posterior

7. **Validação de Resposta**: Aceita apenas status HTTP 200 como sucesso na chamada ao parceiro

8. **Identificador Único**: Para tributos, utiliza identificadorUnicoTransacao como protocolo origem; para demais, usa numeroProtocoloSolicitacao

---

## 6. Relação entre Entidades

**Principais Entidades de Domínio:**

- **LancamentoCallbackParceiroRepresentation**: Representa solicitação de callback recebida da fila
  - Contém: protocolo, cliente endpoint, usuário serviço, NSU cliente, código liquidação
  
- **CallbackParceiro**: Resposta do parceiro
  - Contém: retornoConfirmacao (0=aprovado, 1=rejeitado), httpStatusCode

- **CallbackResponse**: Dados para notificar esteira
  - Contém: código liquidação, protocolo, NSU, retorno confirmação, login, autenticação

- **Pagamento**: Detalhes completos do pagamento
  - Relaciona-se com: Participante (remetente/favorecido), possui dados de liquidação

- **Parceria**: Informações do parceiro
  - Contém: URL callback, usuário API, tipo integração

- **RetornoSolicitacao**: Registro de tentativa de callback
  - Contém: protocolo, URL parceiro, mensagem, data/hora

- **ControleRetorno**: Registro de resposta do parceiro
  - Relaciona-se com: RetornoSolicitacao (via cdNotificacaoFintech)

**Relacionamentos:**
- LancamentoCallbackParceiroRepresentation → Pagamento (via numeroProtocoloSolicitacao)
- Pagamento → Parceria (via codigoLiquidacao + numeroConta + numeroCpfCnpj)
- RetornoSolicitacao → ControleRetorno (1:N via cdRetornoSolicitacaoFintech)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbPagamento (via API) | tabela | SELECT | Consulta detalhes do pagamento pelo código de lançamento |
| TbParceria (via API) | tabela | SELECT | Busca informações do parceiro por liquidação, conta e CNPJ |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbRetornoSolicitacaoFintech (via API) | tabela | INSERT | Registra tentativa de callback ao parceiro |
| TbControleRetornoSlctoFintech (via API) | tabela | INSERT | Registra resposta recebida do parceiro |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot | Configurações da aplicação por ambiente |
| application-local.yml | leitura | Spring Boot | Configurações específicas para ambiente local |
| logback-spring.xml | leitura | Logback | Configuração de logs da aplicação |
| swagger/sboot-spag-base-orch-callback-parceiro.yml | leitura | Swagger Codegen | Especificação OpenAPI para geração de código |

---

## 10. Filas Lidas

**Filas consumidas pelo sistema:**

1. **events.business.SPAG-BASE.confirmarPagamentoApi**
   - Exchange: events.business.confirmarPagamentoApi
   - Routing Key: SPAG.rk.confirmarPagamentoApi
   - Descrição: Recebe solicitações de callback de parceiro para confirmação de pagamento
   - Listener: FilasRabbitListener.queueGetDadosParceiroToConfirmacao

2. **events.business.SPAG-BASE.notificaCallBackEsteira**
   - Exchange: events.business.notificaCallBackEsteira
   - Routing Key: SPAG.rk.notificaCallBackEsteira
   - Descrição: Recebe notificações para processar callback na esteira de pagamentos
   - Listener: FilasRabbitListener.processarNotificaCallbackEsteira

---

## 11. Filas Geradas

**Filas para as quais o sistema publica:**

1. **events.business.SPAG-BASE.confirmarPagamentoApiWaiting**
   - Routing Key: SPAG.rk.confirmarPagamentoApiWaiting
   - Descrição: Fila de retry para reprocessamento de callbacks com falha
   - Método: CallbackQueueParceiroImpl.enviarMensagemWaitingCallback

2. **events.business.SPAG-BASE.notificaCallBackEsteiraWaiting**
   - Descrição: Fila de retry para notificações de esteira com falha
   - Método: CallbackQueueParceiroImpl.enviarNotificaCallbackEsteiraWaiting

3. **events.business.confirmarPagamentoApi** (mock)
   - Exchange: events.business.confirmarPagamentoApi
   - Routing Key: SPAG.rk.confirmarPagamentoApi
   - Descrição: Publicação para testes/mock de callback
   - Método: CallbackQueueParceiroImpl.enviarMensagemMock

4. **events.business.notificaCallBackEsteira**
   - Exchange: events.business.notificaCallBackEsteira
   - Routing Key: SPAG.rk.notificaCallBackEsteira
   - Descrição: Notifica esteira para prosseguir com processamento
   - Método: CallbackQueueParceiroImpl.enviarNotificaCallbackEsteira

---

## 12. Integrações Externas

**APIs Integradas:**

1. **API Gateway (Parceiros)**
   - Endpoints: 
     - /v1/atacado/callback/confirmar-pagamento (callback padrão)
     - /v2/atacado/callback (callback partner)
     - /v1/atacado/gestao/pagamento-tributo-consumo/validar (tributos)
     - /v2/atacado/gestao/pagamento-tributo-consumo/validar (tributos mTLS)
   - Descrição: Chamadas aos endpoints de callback dos parceiros para confirmação/rejeição
   - Autenticação: OAuth2 JWT via GatewayOAuthService

2. **sboot-spag-base-atom-pagamento**
   - Endpoint: /v1/pagamento/detalhado/{cdLancamento}
   - Descrição: Consulta detalhes do pagamento
   - Método: GET

3. **sboot-spag-base-atom-parcerias**
   - Endpoint: /v1/parcerias/buscarCliente
   - Descrição: Busca informações do parceiro
   - Método: GET
   - Parâmetros: cdLiquidacao, numeroConta, numeroCnpj (header)

4. **sboot-spag-base-atom-callback-parceiro**
   - Endpoints:
     - /v1/callback-parceiro/retornoSolicitacao (POST)
     - /v1/callback-parceiro/controleRetorno (POST)
   - Descrição: Registra histórico de callbacks e respostas

5. **sboot-spag-base-orch-transferencias**
   - Endpoint: /v1/processarCallBackParceiro
   - Descrição: Processa callback para transferências (TED/DOC/TEF)
   - Método: POST

6. **sboot-spag-base-orch-pagamento-boleto-srv**
   - Endpoint: /v1/processar-callback-parceiro
   - Descrição: Processa callback para boletos
   - Método: POST

7. **sboot-spag-base-orch-pagamento-tributo-srv**
   - Endpoint: /v1/processarCallBackParceiro
   - Descrição: Processa callback para tributos
   - Método: POST

8. **ConfigCat**
   - Descrição: Serviço de feature toggles
   - Toggles utilizadas:
     - ft_boolean_spag_base_mtls_toggle
     - ft_string_spag_base_mtls_toggle

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (domain, application)
- Uso adequado de padrões como Repository, Service e Mapper
- Cobertura de testes unitários presente
- Uso de Apache Camel para roteamento facilita manutenção
- Implementação de retry e controle de tentativas
- Logging adequado para troubleshooting
- Uso de feature toggles para controle de funcionalidades

**Pontos de Melhoria:**
- Mistura de Gson e Jackson para serialização JSON (falta de padronização)
- Classe MainService muito extensa com múltiplas responsabilidades (viola Single Responsibility)
- Uso de `@SneakyThrows` esconde tratamento de exceções
- Comentários em código desabilitado (código morto) em testes
- Tratamento de exceções genérico em alguns pontos (catch Exception)
- Falta de validação de entrada em alguns métodos
- Uso de `System.setProperty` para configuração de headers HTTP
- Alguns métodos com complexidade ciclomática alta (muitos ifs aninhados)
- Falta de documentação JavaDoc em classes de domínio
- Configurações hardcoded em algumas classes de teste

O código é funcional e bem estruturado, mas poderia se beneficiar de refatorações para reduzir complexidade, melhorar tratamento de erros e aumentar a padronização.

---

## 14. Observações Relevantes

1. **Ambiente Multi-Cloud**: Sistema preparado para deploy em Google Cloud Platform (GKE) com configurações específicas por ambiente (des, qa, uat, prd)

2. **Observabilidade**: Integrado com Prometheus para métricas e possui health checks configurados para Kubernetes liveness/readiness probes

3. **Segurança**: 
   - Autenticação OAuth2 JWT para chamadas externas
   - Suporte a mTLS para parceiros específicos via feature toggle
   - Configuração de CORS e headers de segurança

4. **Resiliência**:
   - Mecanismo de retry com fila waiting
   - Limite de 3 tentativas antes de rejeitar automaticamente
   - Timeout configurado para chamadas HTTP
   - Circuit breaker implícito via controle de tentativas

5. **Auditoria**: Todo fluxo de callback é registrado em banco para rastreabilidade e compliance

6. **Versionamento**: Sistema usa versionamento semântico (0.7.0) e está na versão de desenvolvimento

7. **Infraestrutura como Código**: Possui arquivo infra.yml com todas as configurações de deploy por ambiente

8. **Documentação**: API documentada via Swagger/OpenAPI com especificação completa de contratos

9. **Padrão de Nomenclatura**: Segue convenção do Banco Votorantim com prefixo "sboot-spag-base"

10. **Dependências Corporativas**: Utiliza bibliotecas internas do BV (arqt-base) para auditoria, segurança e feature toggles