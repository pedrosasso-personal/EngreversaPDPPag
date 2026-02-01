# Ficha Técnica do Sistema

---

## 1. Descrição Geral

O sistema **sboot-spag-base-orch-registra-boleto** é um serviço de orquestração para registro de pagamentos de boletos no ecossistema SPAG (Sistema de Pagamentos) do Banco Votorantim. Trata-se de uma aplicação Spring Boot que atua como orquestrador, integrando múltiplos sistemas (SITP, PGFT, SPAG) para processar registros de boletos com diferentes tipos de liquidação (Normal e STR_26). O sistema consome comandos via Google Cloud Pub/Sub, processa validações de negócio, registra pagamentos em sistemas legados, publica eventos de resultado e, em casos específicos (STR_26), envia mensagens para filas IBM MQ para processamento de transferências TED.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal Spring Boot que inicializa a aplicação |
| **RegistraBoletoService** | Serviço de domínio que coordena o processamento de registros de boleto através de rotas Camel |
| **RegistraBoletoSubscriber** | Subscriber que consome mensagens do Pub/Sub e direciona para o serviço apropriado |
| **CamelContextWrapper** | Wrapper do contexto Apache Camel que gerencia as rotas de integração |
| **RegistroSucessoPagamentoBoletoRouter** | Rota Camel para processar registros bem-sucedidos de pagamento de boleto |
| **RegistroErroPagamentoBoletoRouter** | Rota Camel para processar registros com erro (negócio ou técnico) |
| **PagamentoBoletoSitpImpl** | Implementação de integração com sistema SITP para registro de boletos |
| **PagamentoBoletoPgftImpl** | Implementação de integração com sistema PGFT para registro de lançamentos |
| **PagamentoBoletoSpagImpl** | Implementação de integração com sistema SPAG para consulta e atualização de lançamentos |
| **PagamentoSpagImpl** | Implementação para atualização de situação de lançamentos no SPAG |
| **EventoPublisherImpl** | Publicador de eventos de resultado de processamento via Pub/Sub |
| **TedPublisherImpl** | Publicador de mensagens TED para fila IBM MQ |
| **EventoFactory** | Factory para criação de eventos de sucesso, rejeição e falha |
| **LancamentoSpag** | Entidade de domínio representando um lançamento de pagamento |
| **EventoRegistro** | Entidade de domínio representando evento de resultado de registro |

---

## 3. Tecnologias Utilizadas

- **Java 11** - Linguagem de programação
- **Spring Boot 2.x** - Framework principal
- **Apache Camel 3.0.1** - Framework de integração e orquestração
- **Maven** - Gerenciamento de dependências e build
- **Google Cloud Pub/Sub** - Mensageria assíncrona (entrada e saída)
- **IBM MQ** - Fila de mensagens para integração TED
- **Spring Integration** - Integração com Pub/Sub
- **MapStruct** - Mapeamento de objetos
- **Lombok** - Redução de código boilerplate
- **EhCache 3.x** - Cache em memória (para Sistema Origem)
- **Apache Velocity** - Template engine para geração de XML
- **Springfox/Swagger** - Documentação de API
- **Micrometer/Prometheus** - Métricas e monitoramento
- **Logback** - Logging com formato JSON
- **JUnit 5 + Mockito** - Testes unitários
- **RestAssured** - Testes funcionais
- **Pact** - Testes de contrato

---

## 4. Principais Endpoints REST

Não se aplica. O sistema não expõe endpoints REST próprios, atuando apenas como consumidor de mensagens Pub/Sub e cliente de APIs externas.

---

## 5. Principais Regras de Negócio

1. **Validação de Grade Horária**: Pagamentos STR_26 só podem ser processados dentro da grade horária da câmara de liquidação (ValidacaoCamaraLiquidacaoProcessor)

2. **Roteamento por Banco Compensação**: 
   - Banco 655: Fluxo específico (comentado no código)
   - Banco 413: Fluxo com possibilidade de STR_26 e geração de TED

3. **Tipos de Liquidação**:
   - **NORMAL**: Registro padrão de boleto
   - **STR_26**: Registro de boleto de alto valor com geração de transferência TED

4. **Processamento de Erros**:
   - Erros de negócio geram eventos de rejeição com código e descrição
   - Erros técnicos geram eventos de falha
   - Ambos atualizam situação do lançamento no SPAG

5. **Consulta de Sistema Origem**: Busca código de entidade via cache (60 minutos TTL)

6. **Atualização de Protocolos**: Relaciona lançamentos SPAG com protocolos ITP e PGFT

7. **Geração de TED**: Para boletos STR_26, cria transferência e envia XML para fila MQ

8. **Publicação de Eventos**: Notifica resultado do processamento (realizado, rejeitado ou falhou) via Pub/Sub

---

## 6. Relação entre Entidades

**Principais Entidades de Domínio:**

- **LancamentoSpag**: Entidade central contendo todos os dados do lançamento de pagamento (remetente, favorecido, valores, datas, códigos)

- **Protocolo**: Representa identificadores de protocolo (ITP, PGFT, STR26)

- **SistemaOrigem**: Contém código de entidade do sistema de origem

- **CamaraLiquidacao**: Define grade horária para processamento

- **EventoRegistro**: Evento de resultado contendo código lançamento, protocolo, datas e erros

- **Erro**: Representa erro de negócio com código e descrição

**Relacionamentos:**
- LancamentoSpag possui múltiplos Protocolos (ITP, PGFT, STR26)
- LancamentoSpag relaciona-se com SistemaOrigem via numeroOrigemOperacao
- EventoRegistro referencia LancamentoSpag e Protocolo
- EventoRegistro pode conter lista de Erros (negócio) ou erro técnico (string)

---

## 7. Estruturas de Banco de Dados Lidas

Não se aplica. O sistema não acessa diretamente banco de dados, realizando todas as operações via APIs REST de outros microserviços.

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema não acessa diretamente banco de dados, realizando todas as operações via APIs REST de outros microserviços.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação (leitura/gravação) | Local/Classe Responsável | Breve Descrição |
|-----------------|----------------------------|-------------------------|-----------------|
| dicionario-esteira-pagamento.xml | Leitura (template) | MqAdapter / resources/dicionarios | Template Velocity para geração de XML de TED |
| logback-spring.xml | Leitura | Configuração Spring Boot | Arquivo de configuração de logs (JSON format) |
| ehcache.xml | Leitura | CacheConfiguration | Configuração de cache para SistemaOrigem (60min TTL) |
| application.yml | Leitura | Spring Boot | Arquivo de configuração da aplicação |
| swagger/*.yaml | Leitura | Swagger Codegen | Especificações OpenAPI para geração de clientes REST |

---

## 10. Filas Lidas

**Google Cloud Pub/Sub:**
- **Subscription**: `business-spag-registrada-boleto-sub` (mapeada para canal `registraBoletoInputChannel`)
  - **Descrição**: Consome comandos de registro de boleto (sucesso, erro negócio, erro técnico)
  - **Classe Responsável**: RegistraBoletoSubscriber
  - **Formato**: JSON com header (comandoHeader) e payload (RegistroSucesso, RegistroErroNegocio ou RegistroErroTecnico)
  - **Modo ACK**: Manual

---

## 11. Filas Geradas

**Google Cloud Pub/Sub:**
- **Topic**: `business-spag-retorno-processo-pagamento-boleto` (mapeado para canal `retornoProcessoPagamentoBoletoOutputChannel`)
  - **Descrição**: Publica eventos de resultado do processamento (registro realizado, rejeitado ou falhou)
  - **Classe Responsável**: EventoPublisherImpl
  - **Formato**: JSON com header (eventoHeader) e payload (EventoRegistro)

**IBM MQ:**
- **Fila**: `QL.SPAG.SOLICITAR_PAGAMENTO_TED_REQ.INT`
  - **Descrição**: Envia solicitações de transferência TED para boletos STR_26
  - **Classe Responsável**: TedPublisherImpl
  - **Formato**: XML gerado via template Velocity
  - **Queue Manager**: QM.ATA.01
  - **Canal**: SPAG.SRVCONN

---

## 12. Integrações Externas

| Sistema/API | Tipo | Descrição |
|-------------|------|-----------|
| **sboot-spag-base-atom-pagamento-boleto (SITP)** | REST API | Registro de pagamento de boleto (Normal/STR_26) e consulta de sistema origem |
| **sboot-spag-base-atom-validacao-pagamento** | REST API | Consulta de dados de lançamento, atualização de protocolos e registro de transferência STR_26 |
| **sboot-spag-base-atom-registra-boleto (PGFT)** | REST API | Registro de lançamento no sistema PGFT |
| **sboot-spag-base-atom-pagamento** | REST API | Atualização de situação de lançamento (sucesso/falha) |
| **API Gateway BV** | OAuth2 | Autenticação via OAuth2 para acesso às APIs (GatewayOAuthService) |
| **IBM MQ** | Message Queue | Envio de mensagens TED para esteira de pagamentos |
| **Google Cloud Pub/Sub** | Message Queue | Consumo de comandos e publicação de eventos |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada com separação clara de responsabilidades (domain, application)
- Uso adequado de padrões como Ports & Adapters (Hexagonal Architecture)
- Boa cobertura de testes unitários
- Uso de MapStruct para mapeamento de objetos
- Configuração externalizada e suporte a múltiplos ambientes
- Implementação de cache para otimização de consultas
- Tratamento estruturado de exceções (negócio vs técnico)
- Uso de Apache Camel para orquestração complexa

**Pontos de Melhoria:**
- Código de rotas Camel comentado em produção (RegistroSucessoPagamentoBoletoRouter), indicando funcionalidades incompletas ou em transição
- Falta de documentação inline em classes críticas
- Alguns métodos com responsabilidades múltiplas (ex: PagamentoSpagImpl.criarOcorrecia)
- Constantes mágicas em alguns pontos (ex: códigos numéricos 3, 99, 500)
- Logs de erro com stack trace completo em alguns casos, mas apenas mensagem em outros (inconsistência)
- Falta de validação de entrada em alguns pontos (ex: conversão de String para Integer sem try-catch em alguns mappers)
- Nomenclatura inconsistente em alguns pontos (ex: "NotificaoResultadoRegistroRouter" com erro de digitação)

---

## 14. Observações Relevantes

1. **Arquitetura de Orquestração**: O sistema utiliza Apache Camel como motor de orquestração, com rotas bem definidas para cada fluxo de negócio (sucesso, erro negócio, erro técnico).

2. **Processamento Assíncrono**: Todo o processamento é baseado em eventos assíncronos via Pub/Sub, com ACK manual para garantir processamento.

3. **Resiliência**: Implementa tratamento de exceções em múltiplos níveis (Camel, Spring, aplicação) com geração de eventos mesmo em caso de falha.

4. **Multi-tenant**: Suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas.

5. **Observabilidade**: Integração completa com Prometheus/Grafana para métricas, além de logs estruturados em JSON.

6. **Segurança**: Autenticação OAuth2 para todas as chamadas de API externas.

7. **Cache Inteligente**: Implementa cache com TTL de 60 minutos para consultas de sistema origem, reduzindo chamadas externas.

8. **Código Legado em Transição**: Presença de código comentado sugere que o sistema está em processo de evolução/migração de funcionalidades.

9. **Template XML**: Uso de Apache Velocity para geração dinâmica de XML para integração com esteira de pagamentos via MQ.

10. **Testes**: Boa estrutura de testes separada em unit, integration e functional, com uso de Pact para testes de contrato.

11. **Deployment**: Preparado para deploy em Kubernetes/OpenShift com configurações de probes, secrets e configmaps.

12. **Limitação Temporal**: Validação de grade horária apenas para boletos STR_26, impedindo processamento fora do horário permitido pela câmara de liquidação.

---