# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema orquestrador de integração para processamento de pagamentos de tributos via PIX. O sistema consome mensagens de um tópico PubSub do Google Cloud Platform contendo notificações de pagamentos PIX realizados para tributos, processa essas notificações e atualiza o status no sistema ATOM. Em caso de erro no processamento, envia notificações por e-mail. Utiliza Apache Camel para orquestração de rotas e integra-se com APIs PIX do Banco Votorantim (BV) e Banco Votorantim S.A. (BVSA) para obtenção de EndToEndId e efetivação de pagamentos.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot que inicializa a aplicação |
| `TributoPixRouter` | Roteador Apache Camel que define rotas para obtenção de EndToEndId e processamento de pagamentos |
| `TributoPixPubSubListener` | Listener que consome mensagens do PubSub e aciona o processamento |
| `TributoPixService` | Serviço responsável por processar notificações de tributo PIX e atualizar o sistema ATOM |
| `PagamentoPixServiceImpl` | Implementação do serviço de pagamento PIX, integrando com APIs externas |
| `EmailService` | Serviço para envio de e-mails de notificação de erro |
| `FeatureToggleService` | Serviço para gerenciamento de feature toggles |
| `JwtClientCredentialInterceptor` | Interceptor Camel para injeção de tokens de autenticação |
| `TributoPixDeserializer` | Deserializador customizado para objetos TributoPix |

## 3. Tecnologias Utilizadas

- **Framework Principal**: Spring Boot 2.x
- **Orquestração**: Apache Camel
- **Mensageria**: Google Cloud PubSub
- **Autenticação**: OAuth2 JWT, Spring Security
- **Cliente HTTP**: RestTemplate, Apache HttpComponents
- **Serialização**: Jackson (com módulo JavaTime)
- **Geração de Código**: Swagger Codegen (para clientes de API)
- **Testes**: JUnit 5, Mockito
- **Utilitários**: Lombok, Spring Mail (JavaMail)
- **Monitoramento**: Spring Actuator, Prometheus
- **Feature Toggle**: ConfigCat (biblioteca customizada Votorantim)
- **Trilha de Auditoria**: Biblioteca customizada Votorantim

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/feature-toggle/ft_boolean_spag_base_lote_tributo_via_pix` | `FeatureToggleController` | Verifica se a feature de pagamento PIX está habilitada |
| GET | `/actuator/health` | Spring Actuator | Endpoint de health check |
| GET | `/actuator/metrics` | Spring Actuator | Métricas da aplicação |
| GET | `/actuator/prometheus` | Spring Actuator | Métricas no formato Prometheus |

**Nota**: Os endpoints de pagamento PIX (`/endToEndId` e `/payments`) definidos no OpenAPI são consumidos de APIs externas, não expostos por este serviço.

## 5. Principais Regras de Negócio

1. **Processamento de Notificações PIX**: Consome mensagens do PubSub contendo notificações de pagamentos PIX de tributos
2. **Roteamento por Banco**: Seleciona credenciais OAuth2 apropriadas (BV ou BVSA) baseado no código do banco (655 para BV, 413 para BVSA)
3. **Tratamento de Sucesso/Erro**: Identifica se a notificação indica sucesso ou erro através do campo `descricaoErro` e roteia para endpoints diferentes no ATOM
4. **Notificação de Erro**: Envia e-mail automático quando o processamento de pagamento falha
5. **Feature Toggle**: Controla habilitação/desabilitação da funcionalidade de pagamento PIX via tributo
6. **Autenticação Automática**: Injeta tokens JWT automaticamente nas requisições através de interceptor Camel
7. **Construção de Payload PIX**: Monta estrutura complexa de pagamento PIX conforme especificação do Swagger, incluindo dados de pagador, recebedor, valores e metadados

## 6. Relação entre Entidades

**Entidades Principais:**

- **TributoPixPubSub**: Envelope da mensagem PubSub contendo id, document, actionType e message
  - Contém: **TributoPix** (deserializado do campo message)
  
- **TributoPix**: Dados completos da transação PIX incluindo:
  - endToendId, statusOperacao, descricaoErro
  - Dados do pagador (ISPB, CPF/CNPJ, nome, agência, conta)
  - Dados do recebedor (ISPB, CPF/CNPJ, nome, agência, conta)
  - Dados da operação (valor, data/hora, prioridade, forma de iniciação)

- **PagamentoRequest**: Request para efetivação de pagamento
  - Contém: lista de **PagamentoPix** e código do banco
  
- **PagamentoPix**: Detalhes do pagamento a ser efetuado
  - Contém: **InterbankSettlementAmount** (valor e moeda)
  - Dados completos de débito e crédito

- **EmailContent**: Estrutura para envio de e-mail de erro
  - id, emailRemetente, emailDestinatario, emailAssunto, erro

**Relacionamentos:**
- TributoPixPubSub (1) --contém--> (1) TributoPix
- PagamentoRequest (1) --contém--> (N) PagamentoPix
- PagamentoPix (1) --contém--> (1) InterbankSettlementAmount

## 7. Estruturas de Banco de Dados Lidas

não se aplica

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot | Arquivo de configuração principal da aplicação |
| application-des.yml | leitura | Spring Boot | Configurações específicas do ambiente de desenvolvimento |
| application-local.yml | leitura | Spring Boot | Configurações para execução local |
| logback-spring.xml | leitura | Logback | Configuração de logs da aplicação |

## 10. Filas Lidas

**Google Cloud PubSub:**

| Nome da Fila/Subscription | Descrição |
|---------------------------|-----------|
| `business-spag-pixx-notificacao-parceiro-interno-spag-base-sub` | Subscription que consome notificações de pagamentos PIX de tributos do tópico `business-spag-pixx-notificacao-parceiro-interno` |

**Configuração:**
- Channel: `pagamentoPixChannel`
- Modo de Acknowledge: MANUAL
- Polling: fixedDelay de 100ms
- Payload Type: String (JSON)

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

| Sistema/API | Tipo | Descrição |
|-------------|------|-----------|
| **PIX BV/BVSA** | API REST | APIs de pagamento PIX do Banco Votorantim (https://pix-h.bancobv.com.br) para obtenção de EndToEndId |
| **SPAG PIX Enviar Pagamento** | API REST | API para efetivação de pagamentos PIX (sboot-spag-pixx-orch-enviar-pagamento) |
| **ATOM Integração Tributo PIX** | API REST | Sistema ATOM para atualização de status de pagamentos (endpoints `/integracao-tributo-pix-success/` e `/integracao-tributo-pix-fail/`) |
| **OAuth2 Token Service** | API REST | Serviço de autenticação para obtenção de tokens JWT (BV e BVSA possuem credenciais separadas) |
| **SMTP Server** | SMTP | Servidor de e-mail (smtpduqrelay.bvnet.bv) para envio de notificações de erro |
| **ConfigCat** | Feature Toggle | Serviço de feature toggle para controle de funcionalidades |
| **Google Cloud PubSub** | Mensageria | Plataforma de mensageria para consumo de notificações PIX |

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com camadas bem definidas (presentation, service, domain, config)
- Uso adequado de padrões Spring Boot e injeção de dependências
- Implementação de testes unitários com boa cobertura
- Uso de Lombok para redução de boilerplate
- Configuração externalizada em arquivos YAML
- Implementação de interceptor para autenticação automática
- Logs estruturados e informativos

**Pontos de Melhoria:**
- Código com muitos comentários em português misturados com código em inglês, prejudicando legibilidade
- Classe `PagamentoPixServiceImpl` muito extensa (método `buildRequestPayment` com mais de 50 linhas)
- Uso de `System.setProperty` em testes pode causar efeitos colaterais
- Falta de tratamento de exceções mais específico em alguns pontos
- Alguns métodos poderiam ser extraídos para melhorar legibilidade (ex: `buildRequestPayment`)
- Uso de strings hardcoded em alguns lugares onde constantes seriam mais apropriadas
- Mock excessivamente complexo em `MockDomainCommon` com JSONs embutidos no código
- Falta de validação de entrada em alguns endpoints

## 14. Observações Relevantes

1. **Segurança**: O sistema utiliza OAuth2 com JWT para autenticação, com credenciais separadas para BV (código 655) e BVSA (código 413)

2. **Resiliência**: Implementa acknowledge manual no PubSub, garantindo que mensagens só sejam removidas após processamento bem-sucedido

3. **Monitoramento**: Expõe métricas via Actuator e Prometheus na porta 9090

4. **Ambientes**: Suporta múltiplos ambientes (local, des, uat, prd) com configurações específicas

5. **Trilha de Auditoria**: Integrado com biblioteca customizada de auditoria do Votorantim

6. **Feature Toggle**: Permite habilitar/desabilitar funcionalidade de pagamento PIX via tributo sem necessidade de deploy

7. **Geração de Código**: Utiliza Swagger Codegen para gerar clientes de API automaticamente a partir de especificações OpenAPI

8. **Dependências Customizadas**: Utiliza várias bibliotecas proprietárias do Banco Votorantim (prefixo `br.com.votorantim.arqt.base` e `br.com.votorantim.spag`)

9. **Configuração de E-mail**: Template de e-mail configurável via properties, com substituição de placeholders (#ID# e #ERRO#)

10. **Versionamento de API**: Endpoints versionados (v1, v2) indicando evolução da API