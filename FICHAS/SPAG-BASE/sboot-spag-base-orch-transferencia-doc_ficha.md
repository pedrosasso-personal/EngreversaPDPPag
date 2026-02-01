# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-spag-base-orch-transferencia-doc** é um serviço de orquestração de transferências DOC (Documento de Ordem de Crédito) do Banco Votorantim. Trata-se de um microserviço stateless desenvolvido em Spring Boot que coordena o fluxo completo de processamento de pagamentos DOC, desde a validação inicial até as notificações aos sistemas legados (SITP, PGFT e SPAG). O sistema utiliza Apache Camel para orquestração de rotas e integra-se com múltiplos serviços backend via REST, além de consumir mensagens de filas IBM MQ.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal Spring Boot que inicializa a aplicação |
| **TransferenciaDocController** | Controller REST que expõe endpoint POST para processar transferências DOC |
| **TransferenciaDocListener** | Listener JMS que consome mensagens da fila de DOC e processa pagamentos |
| **PagamentoService** | Serviço que orquestra o processamento de transferências DOC via Camel |
| **TransferenciaDocRouter** | Define as rotas Camel para orquestração do fluxo de pagamento |
| **ValidarPagamentoRepositoryImpl** | Implementação de integração REST com serviço de validação de pagamento |
| **DebitarCreditarContaRepositoryImpl** | Implementação de integração REST para débito/crédito e estorno |
| **NotificarPagamentoSITPRepositoryImpl** | Implementação de integração REST para notificação ao SITP |
| **NotificarPagamentoPGFTRepositoryImpl** | Implementação de integração REST para notificação ao PGFT |
| **NotificarPagamentoSPAGRepositoryImpl** | Implementação de integração REST para notificação ao SPAG |
| **TratarOcorrenciasRepositoryImpl** | Implementação de integração REST para tratamento de ocorrências |
| **CamelContextWrapper** | Wrapper do contexto Camel para gerenciamento de rotas |
| **EstornoProcessor** | Processor Camel para tratamento de estorno em caso de erro |
| **NotificacaoAggregation** | Strategy de agregação Camel para consolidar respostas de notificações |
| **OcorrenciaUtil** | Classe utilitária para criação de ocorrências de erro |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.x** - Framework base da aplicação
- **Apache Camel 3.0.1** - Orquestração de rotas e integração
- **IBM MQ (JMS)** - Mensageria para consumo de solicitações de pagamento
- **RestTemplate** - Cliente HTTP para integração com serviços backend
- **Lombok** - Redução de boilerplate code
- **Swagger/OpenAPI (Springfox 2.9.2)** - Documentação de APIs
- **Spring Actuator** - Monitoramento e health checks
- **Micrometer/Prometheus** - Métricas e observabilidade
- **Jackson** - Serialização/deserialização JSON
- **JAXB** - Unmarshalling de XML
- **Maven** - Gerenciamento de dependências e build
- **Docker** - Containerização
- **Java 11** - Linguagem de programação

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/transferencia-doc | TransferenciaDocController | Processa uma solicitação de transferência DOC recebendo um DicionarioPagamento |

---

## 5. Principais Regras de Negócio

1. **Validação de Pagamento**: Antes de processar, o pagamento é validado através do serviço atom-validar-pagamento. Se a validação falhar (flRetornoValidaSolicitacaoPagto != 0), o fluxo é interrompido e segue para estorno.

2. **Débito/Crédito de Conta**: Após validação bem-sucedida, realiza-se o débito da conta através do serviço atom-debitar-creditar-conta. Se falhar (flRetornoSolicitacaoDebitoConta != 0), aciona o fluxo de estorno.

3. **Estorno Automático**: Em caso de erro nas etapas de validação ou débito, o sistema executa automaticamente o estorno do pagamento e registra as ocorrências.

4. **Notificações Paralelas**: Após débito bem-sucedido, o sistema notifica três sistemas legados de forma sequencial: SITP, PGFT e SPAG. Erros nessas notificações não acionam estorno.

5. **Tratamento de Ocorrências**: Após estorno, o sistema registra as ocorrências através do serviço atom-tratar-ocorrencias.

6. **Retry com Backoff**: O sistema possui política de retry (3 tentativas com delay de 15 segundos) para falhas de comunicação.

7. **Agregação de Respostas**: As respostas das notificações são agregadas no DicionarioPagamento através da estratégia NotificacaoAggregation.

---

## 6. Relação entre Entidades

O sistema trabalha principalmente com a entidade **DicionarioPagamento** (proveniente da biblioteca java-spag-base-pagamentos-commons), que é o objeto central trafegado em todo o fluxo.

**Estrutura de DTOs:**
- Cada integração possui um par Request/Response (ex: ValidarPagamentoRequest/Response)
- Cada Request/Response é encapsulado em um DTO (ex: ValidarPagamentoRequestDTO/ResponseDTO)
- Todos os DTOs encapsulam o DicionarioPagamento

**Mappers:**
- Cada integração possui um Mapper responsável por converter DicionarioPagamento para o formato específico do serviço e vice-versa

**Ports (Interfaces):**
- Definem contratos de integração (ex: ValidarPagamentoRepository)
- Implementados pelas classes Repository na camada de infraestrutura

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | leitura | /usr/etc/log (runtime) | Arquivo de configuração de logs carregado em ambientes des/qa/uat/prd |
| application.yml | leitura | classpath (resources) | Arquivo de configuração principal da aplicação |
| application-local.yml | leitura | classpath (resources) | Arquivo de configuração para ambiente local |

---

## 10. Filas Lidas

**Fila:** QL.SPAG.SOLICITAR_PAGAMENTO_DOC_REQ.INT

**Tipo:** IBM MQ (JMS)

**Classe Consumidora:** TransferenciaDocListener

**Descrição:** Fila de entrada que recebe solicitações de pagamento DOC em formato XML/SOAP. O listener extrai o elemento PagamentoMensagem, remove prefixos SOAP e converte para DicionarioPagamento via JAXB.

**Configuração:**
- Queue Manager: QM.ATA.01
- Channel: SPAG.SRVCONN
- Autenticação: usuário/senha específicos por ambiente

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **atom-validar-pagamento** | REST (POST) | Valida a solicitação de pagamento antes do processamento. Endpoint: /spag-base-validar-pagamento-rs/v1/atacado/pagamentos/validarPagamento/ |
| **atom-debitar-creditar-conta** | REST (POST) | Realiza débito/crédito em conta corrente. Endpoints: /nccs-base-debitar-creditar-conta-rs/v1/atacado/pagamentos/debitarCreditarConta e /estornarPagamento |
| **atom-notificar-pagamento-sitp** | REST (POST) | Notifica o sistema legado SITP sobre o pagamento. Endpoint: /sitp-base-notificar-pagamento-sitp-rs/v1/atacado/pagamentos/notificarPagamentoSITP |
| **atom-notificar-pagamento-pgft** | REST (POST) | Notifica o sistema legado PGFT sobre o pagamento. Endpoint: /pgft-base-notificar-pagamento-pgft-rs/v1/atacado/pagamentos/notificarPagamentoPGFT |
| **atom-notificar-pagamento-spag** | REST (POST) | Notifica o sistema SPAG sobre o pagamento. Endpoint: /spag-base-notifica-pagamento-rs/v1/atacado/pagamentos/notificarPagamentoSPAG |
| **atom-tratar-ocorrencias** | REST (POST) | Registra e trata ocorrências de erro no processamento. Endpoint: /spag-base-tratar-ocorrencias-rs/v1/atacado/pagamentos/tratarOcorrencias |

**Observações:**
- Todas as integrações utilizam autenticação básica (usuário/senha)
- URLs variam por ambiente (des/qa/uat/prd)
- Timeout configurado: 60 segundos (connect e read)
- Logging de request/response habilitado em modo DEBUG

---

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (application, domain, common)
- Uso adequado de padrões como Repository, Mapper e Builder
- Configuração externalizada e parametrizada por ambiente
- Implementação de retry e tratamento de exceções
- Uso de Lombok reduzindo boilerplate
- Documentação via Swagger configurada
- Estrutura de testes organizada (unit/integration/functional)

**Pontos de Melhoria:**
- Falta de tratamento de exceções mais granular (captura genérica de Exception)
- Ausência de validações de entrada nos controllers
- Logging poderia ser mais estruturado (falta de MDC/correlation ID)
- Falta de testes unitários implementados (apenas estrutura)
- Configuração de timeout hardcoded (60s) poderia ser parametrizável
- Ausência de circuit breaker para resiliência nas integrações
- Código de parsing XML no Listener poderia ser extraído para classe específica
- Falta de documentação inline (JavaDoc) nas classes principais
- Configuração de retry no Camel poderia ser externalizada

---

## 14. Observações Relevantes

1. **Arquitetura Multi-Módulo**: O projeto está organizado em 3 módulos Maven (application, domain, common), seguindo boas práticas de separação de concerns.

2. **Dependência de Biblioteca Proprietária**: O sistema depende fortemente da biblioteca `java-spag-base-pagamentos-commons` (versão 0.20.12) que define o DicionarioPagamento e outras estruturas de dados.

3. **Orquestração com Camel**: A lógica de orquestração está centralizada no TransferenciaDocRouter, que define 8 rotas diferentes para o fluxo completo.

4. **Dual Interface**: O sistema pode ser acionado tanto via REST (síncrono) quanto via JMS (assíncrono), ambos convergindo para o mesmo serviço de processamento.

5. **Estratégia de Estorno**: O sistema implementa compensação automática (estorno) em caso de falha nas etapas críticas, mas não nas notificações aos sistemas legados.

6. **Configuração por Ambiente**: Utiliza ConfigMaps e Secrets do Kubernetes para parametrização, com suporte a ambientes local/des/qa/uat/prd.

7. **Observabilidade**: Integração com Prometheus para métricas e health checks via Actuator na porta 9090.

8. **Containerização**: Dockerfile otimizado usando OpenJ9 Alpine com configuração de timezone.

9. **Parsing XML Customizado**: O listener implementa lógica específica para extrair e limpar tags SOAP antes do unmarshalling JAXB.

10. **Versionamento de API**: Endpoint REST versionado (v1), seguindo boas práticas de design de APIs.