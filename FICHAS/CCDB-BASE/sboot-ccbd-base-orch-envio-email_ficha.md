# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-ccbd-base-orch-envio-email** é um serviço stateless desenvolvido em Java com Spring Boot, responsável por orquestrar o envio de e-mails transacionais no contexto do Banco Votorantim (CCBD - Conta Corrente Banco Digital). O sistema atua como um orquestrador que recebe solicitações de envio de e-mail através de filas Pub/Sub do Google Cloud Platform e encaminha para APIs de envio de e-mail (SendGrid/CAAPI).

O sistema suporta três tipos principais de envio:
- **Envio de extrato bancário** (PDF e OFX) para clientes PF e PJ
- **Notificação de encerramento de conta**
- **Notificação de divergência de saldo**

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application.java` | Classe principal que inicializa a aplicação Spring Boot |
| `EnvioEmailExtratoListener.java` | Listener que consome mensagens de envio de extrato do Pub/Sub |
| `EnvioEmailEncerramentoContaListener.java` | Listener que consome mensagens de encerramento de conta do Pub/Sub |
| `EnvioEmailDivergenciaSaldoListener.java` | Listener que consome mensagens de divergência de saldo do Pub/Sub |
| `EnvioEmailExtratoServiceImpl.java` | Implementa a lógica de negócio para envio de extrato |
| `EnvioEmailEncerramentoServiceImpl.java` | Implementa a lógica de negócio para envio de e-mail de encerramento |
| `EnvioEmailDivergenciaSaldoServiceImpl.java` | Implementa a lógica de negócio para envio de e-mail de divergência |
| `EnvioEmailExtratoRepositoryImpl.java` | Implementa a comunicação com a API de envio de e-mail (extrato) |
| `EnvioEmailEncerramentoRepositoryImpl.java` | Implementa a comunicação com a API de envio de e-mail (encerramento) |
| `EnvioEmailDivergenciaSaldoRepositoryImpl.java` | Implementa a comunicação com a API de envio de e-mail (divergência) |
| `TemplateFileRepositoryImpl.java` | Responsável por carregar templates HTML de e-mail |
| `EnvioEmailExtratoMapper.java` | Mapeia objetos de domínio para representações de API |
| `CamelContextWrapper.java` | Wrapper para contexto Apache Camel |
| `EnvioEmailEncerramentoRouter.java` | Define rotas Camel para processamento de encerramento |

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x**
- **Spring Cloud GCP** (versão 1.2.8.RELEASE) - Integração com Google Cloud Pub/Sub
- **Apache Camel** (versão 3.0.1) - Orquestração e roteamento de mensagens
- **Apache Avro** (versão 1.12.0) - Serialização de mensagens
- **Swagger/OpenAPI** (Springfox 3.0.0) - Documentação de API
- **Prometheus/Micrometer** - Métricas e monitoramento
- **Grafana** - Visualização de métricas
- **Logback** - Logging
- **Lombok** - Redução de boilerplate
- **JUnit 5 + Mockito** - Testes unitários
- **Rest Assured** - Testes funcionais
- **Pact** (versão 4.0.3) - Testes de contrato
- **Maven** - Gerenciamento de dependências
- **Docker** - Containerização
- **Google Cloud Platform** - Infraestrutura (Pub/Sub, Cloud Storage)
- **HikariCP** - Pool de conexões
- **Jackson** - Serialização JSON

## 4. Principais Endpoints REST

Não se aplica. O sistema não expõe endpoints REST públicos, funcionando primariamente como consumidor de mensagens Pub/Sub. Os endpoints disponíveis são apenas de monitoramento (Actuator):

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/actuator/health` | Health check da aplicação |
| GET | `/actuator/metrics` | Métricas da aplicação |
| GET | `/actuator/prometheus` | Métricas no formato Prometheus |

## 5. Principais Regras de Negócio

1. **Processamento de Extrato Bancário:**
   - Identifica o tipo de conta (PF ou PJ) com base no tamanho do documento (CPF=11 dígitos, CNPJ=14 dígitos)
   - Seleciona o template HTML apropriado para cada tipo de conta
   - Anexa arquivos PDF e OFX ao e-mail
   - Envia e-mail com extrato para o endereço cadastrado do cliente

2. **Processamento de Encerramento de Conta:**
   - Recebe dados de encerramento via Pub/Sub
   - Utiliza Apache Camel para orquestração do fluxo
   - Envia notificação de encerramento para o cliente via API do Salesforce Marketing Cloud

3. **Processamento de Divergência de Saldo:**
   - Detecta inconsistências de saldo em contas
   - Gera relatório em PDF com informações da divergência
   - Envia notificação para múltiplos destinatários (suporta lista separada por ponto-e-vírgula)
   - Ignora mensagens com `routing_key` (mensagens de controle)

4. **Autenticação e Segurança:**
   - Obtém token JWT OAuth2 antes de cada chamada às APIs externas
   - Utiliza credenciais armazenadas em secrets do Kubernetes

5. **Tratamento de Erros:**
   - Mensagens com erro são confirmadas (ack) para evitar reprocessamento infinito
   - Logs detalhados de erros para troubleshooting
   - Exceções customizadas para diferentes tipos de falha

## 6. Relação entre Entidades

**Entidades de Domínio:**

- **EnvioEmailEncerramento**: Representa uma solicitação de envio de e-mail de encerramento
  - Contém: `deExternalKey`, lista de `RequestBody`
  
- **RequestBody**: Corpo da requisição de encerramento
  - Contém: `Key` (chave do subscriber), `Value` (valores dos dados)

- **Key**: Identificador do destinatário
  - Contém: `subscriberKey`

- **Value**: Dados do cliente e da conta
  - Contém: CPF/CNPJ, nome, data de encerramento, agência, conta, endereço, e-mail, telefone, etc.

- **EnvioEmailExtratoDTO**: Representa uma solicitação de envio de extrato
  - Contém: dados da conta, período, movimentações, arquivos (PDF/OFX)

- **InformacoesEmailExtrato**: Informações consolidadas para envio de e-mail
  - Contém: assunto, destinatário, conteúdo HTML, arquivos anexos

- **MovimentacaoDTO**: Representa uma movimentação bancária
  - Contém: categoria, título, valor, saldo, data, NSU, etc.

- **MovimentacaoConsolidadaDTO**: Consolidação de movimentações por período
  - Contém: saldo inicial/final, total de entradas/saídas, lista de datas

**Relacionamentos:**
- `EnvioEmailEncerramento` 1:N `RequestBody`
- `RequestBody` 1:1 `Key`
- `RequestBody` 1:1 `Value`
- `EnvioEmailExtratoDTO` 1:N `MovimentacaoDTO`
- `EnvioEmailExtratoDTO` 1:1 `MovimentacaoConsolidadaDTO`

## 7. Estruturas de Banco de Dados Lidas

Não se aplica. O sistema não acessa diretamente banco de dados. Todas as informações são recebidas via mensagens Pub/Sub.

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema não realiza operações de escrita em banco de dados.

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `email/extrato/pf/template.html` | Leitura | `TemplateFileRepositoryImpl` | Template HTML para e-mail de extrato de pessoa física |
| `email/extrato/pj/template.html` | Leitura | `TemplateFileRepositoryImpl` | Template HTML para e-mail de extrato de pessoa jurídica |
| `logback-spring.xml` | Leitura | Logback (framework) | Configuração de logs da aplicação |
| `application.yml` | Leitura | Spring Boot | Configurações da aplicação |
| `EmailRequest.avsc` | Leitura | Apache Avro | Schema Avro para serialização de mensagens de e-mail |

**Observação:** Arquivos PDF e OFX são recebidos como strings Base64 nas mensagens Pub/Sub e não são gravados em disco, sendo enviados diretamente como anexos de e-mail.

## 10. Filas Lidas

| Nome da Fila | Tecnologia | Descrição |
|--------------|------------|-----------|
| `business-ccbd-base-envio-email-encerramento-conta-sub` | Google Cloud Pub/Sub | Fila para receber solicitações de envio de e-mail de encerramento de conta |
| `business-ccbd-base-envio-email-extrato-pdf-sub` | Google Cloud Pub/Sub | Fila para receber solicitações de envio de extrato bancário (PDF/OFX) |
| `business-ccbd-base-envio-email-sub` | Google Cloud Pub/Sub | Fila para receber solicitações de envio de e-mail de divergência de saldo |

**Configuração:**
- Modo de confirmação: MANUAL (ack/nack explícito)
- Tipo de payload: String (JSON)
- Projeto GCP: `bv-ccbd-des` (DES), `bv-ccbd-uat` (UAT), `bv-ccbd-prd` (PRD)

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas, apenas consome.

## 12. Integrações Externas

| Sistema/API | Tipo | Descrição |
|-------------|------|-----------|
| **CAAPI - Envio Email Extrato** | REST API | API para envio de e-mails de extrato bancário via SendGrid. Endpoint: `/v1/corporativo/email` |
| **CAAPI - Salesforce Marketing Cloud** | REST API | API para envio de e-mails de encerramento via Salesforce. Endpoint: `/v1/banco-digital/encerramento/envio-email` |
| **Gateway OAuth** | REST API | Serviço de autenticação para obtenção de tokens JWT. URLs variam por ambiente (DES/UAT/PRD) |
| **Google Cloud Pub/Sub** | Messaging | Sistema de mensageria para recebimento de solicitações de envio de e-mail |
| **Google Cloud Storage** | Object Storage | Armazenamento de arquivos anexos (referenciado mas não diretamente utilizado no código analisado) |

**Detalhes de Autenticação:**
- Todas as chamadas às APIs externas requerem token JWT OAuth2
- Credenciais: `API_CLIENT_ID` e `API_CLIENT_SECRET` (armazenadas em secrets)
- Token obtido via `GatewayOAuthService.getAccessToken()`

## 13. Avaliação da Qualidade do Código

**Nota: 7.5/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo princípios de Clean Architecture (separação em camadas: domain, application, common)
- Uso adequado de padrões de projeto (Repository, Service, Mapper, Listener)
- Boa cobertura de testes unitários e de integração
- Uso de Lombok para reduzir boilerplate
- Configuração externalizada e separada por ambiente
- Logs estruturados em JSON para facilitar análise
- Documentação OpenAPI/Swagger configurada
- Uso de métricas e monitoramento (Prometheus/Grafana)
- Tratamento de exceções customizado
- Uso de Apache Camel para orquestração complexa

**Pontos de Melhoria:**
- Alguns métodos poderiam ser mais granulares (ex: `EnvioEmailExtratoMapper.toRepresentation` é extenso)
- Falta documentação JavaDoc em algumas classes e métodos públicos
- Alguns nomes de variáveis poderiam ser mais descritivos (ex: `obj` em mocks)
- Configurações hardcoded em alguns lugares (ex: `CHAVE_PADRAO` em `MessageRequestMapper`)
- Tratamento de erro genérico em alguns listeners (catch Exception)
- Falta validação de entrada em alguns pontos
- Alguns testes poderiam ter assertions mais específicas
- Código de geração de clientes OpenAPI poderia estar em módulo separado
- Dependências com versões SNAPSHOT em produção (não recomendado)

**Recomendações:**
1. Adicionar validação de entrada com Bean Validation
2. Melhorar documentação JavaDoc
3. Refatorar métodos longos em métodos menores
4. Implementar circuit breaker para chamadas externas
5. Adicionar testes de carga/performance
6. Revisar tratamento de exceções para ser mais específico
7. Remover dependências SNAPSHOT antes de produção

## 14. Observações Relevantes

1. **Arquitetura Multi-módulo:** O projeto está organizado em três módulos Maven (common, domain, application), facilitando a separação de responsabilidades e reutilização de código.

2. **Ambientes:** O sistema suporta múltiplos ambientes (local, des, uat, prd) com configurações específicas para cada um.

3. **Containerização:** Aplicação preparada para execução em containers Docker e deploy no OpenShift/Kubernetes (GCP).

4. **Observabilidade:** Sistema bem instrumentado com:
   - Health checks (Spring Actuator)
   - Métricas (Prometheus)
   - Dashboards (Grafana)
   - Logs estruturados (Logback JSON)

5. **Segurança:** 
   - Autenticação JWT em todas as chamadas externas
   - Secrets gerenciados via Kubernetes
   - HTTPS configurado

6. **Testes:** Boa estrutura de testes com separação clara entre:
   - Testes unitários
   - Testes de integração
   - Testes funcionais
   - Testes de contrato (Pact)
   - Testes de arquitetura (ArchUnit)

7. **CI/CD:** Configuração Jenkins presente (`jenkins.properties`) indicando pipeline automatizado.

8. **Limitações Identificadas:**
   - Sistema não possui retry automático em caso de falha de envio
   - Não há DLQ (Dead Letter Queue) configurada explicitamente
   - Falta circuit breaker para proteção contra falhas em cascata

9. **Dependências Críticas:**
   - Google Cloud Pub/Sub (se indisponível, sistema para de processar)
   - APIs de envio de e-mail (CAAPI/SendGrid)
   - Serviço de autenticação OAuth

10. **Performance:** Sistema configurado para processar mensagens de forma assíncrona, com pool de threads gerenciado pelo Spring Integration.