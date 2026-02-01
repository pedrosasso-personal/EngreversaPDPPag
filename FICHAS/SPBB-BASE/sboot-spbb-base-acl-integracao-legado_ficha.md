# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-spbb-base-acl-integracao-legado** é um Anti Corruption Layer (ACL) desenvolvido para intermediar a comunicação entre o SPB Core (Sistema de Pagamentos Brasileiro moderno) e o SPB legado. O sistema recebe mensagens via Google Cloud Pub/Sub, processa e encaminha para filas IBM MQ específicas de acordo com a instituição bancária (Banco Votorantim - código ISPB 59588111 ou Banco BVSA - código ISPB 01858774). Utiliza Apache Camel para orquestração de rotas e Spring Boot como framework base.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal que inicializa a aplicação Spring Boot |
| **RecebimentoMensagemPubSubListener** | Listener que consome mensagens do Google Pub/Sub |
| **RecebimentoMensagemSpbRouter** | Rota Apache Camel que orquestra o processamento de mensagens |
| **SPBBVProcessor** | Processor Camel responsável por processar e enviar mensagens para IBM MQ |
| **RecebimentoMensagemSpbService** | Serviço que inicia o processamento via Camel |
| **IbmMQService** | Serviço responsável pela lógica de envio para filas IBM MQ |
| **JmsConfig** | Configuração de conexões JMS para IBM MQ (Votorantim e BVSA) |
| **MensagemRecebida** | Entidade de domínio representando mensagem recebida |
| **MensagemRecebidaMQ** | Entidade de domínio para envio ao MQ |
| **JwtAuthorizationHeaderGenerator** | Gerador de tokens de autenticação JWT |
| **PubSubRecebimentoMensagemSpbConfiguration** | Configuração do subscriber Google Pub/Sub |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.7.x** - Framework base da aplicação
- **Apache Camel** - Orquestração de rotas e integração
- **Google Cloud Pub/Sub** - Mensageria de entrada
- **IBM MQ (JMS)** - Mensageria de saída para sistemas legados
- **Spring Security OAuth2** - Segurança e autenticação JWT
- **MapStruct** - Mapeamento de objetos
- **Lombok** - Redução de código boilerplate
- **Maven** - Gerenciamento de dependências
- **Docker** - Containerização
- **Google Cloud Platform (GCP)** - Infraestrutura cloud
- **JUnit 5 + Mockito** - Testes unitários
- **Gson** - Serialização/deserialização JSON
- **Java 11** - Linguagem de programação

---

## 4. Principais Endpoints REST

não se aplica

(O sistema não expõe endpoints REST próprios, apenas endpoints do Spring Actuator para monitoramento)

---

## 5. Principais Regras de Negócio

1. **Roteamento por Instituição Bancária**: O sistema identifica a instituição bancária através do código ISPB extraído do nome da fila (4º segmento separado por ponto), direcionando para a fila IBM MQ correspondente (Banco Votorantim ou BVSA).

2. **Validação de Banco**: Apenas mensagens de bancos válidos (ISPB 59588111 - Votorantim ou 01858774 - BVSA) são processadas. Mensagens de outros bancos geram exceção `BancoInvalidoException`.

3. **Processamento Assíncrono**: Mensagens são consumidas do Pub/Sub de forma assíncrona e processadas através de rotas Apache Camel.

4. **Controle de Fluxo**: Implementa controle de fluxo no Pub/Sub com limite de 2000 elementos e 100MB de requisições pendentes.

5. **Reconhecimento de Mensagens**: Mensagens processadas com sucesso recebem ACK, enquanto falhas recebem NACK para reprocessamento.

6. **Autenticação JWT**: Suporte a autenticação via JWT com validação de credenciais Basic Auth.

---

## 6. Relação entre Entidades

**MensagemRecebida** (entidade principal)
- Atributos: `nomeFila` (String), `mensagemCriptografada` (byte[])
- Representa a mensagem recebida do Pub/Sub

**MensagemRecebidaMQ** (entidade de saída)
- Atributos: `nomeFila` (String), `mensagemCriptografada` (byte[])
- Representa a mensagem a ser enviada para IBM MQ
- Mapeada de `MensagemRecebida` via `MensagemRecebidaMQMapper`

**JmsIntegracaoLegado** (entidade de configuração)
- Atributos: `jmsTemplate` (JmsTemplate), `queue` (String)
- Encapsula configuração de conexão JMS por instituição

**Relacionamento**: MensagemRecebida → (mapeamento) → MensagemRecebidaMQ → (envio via) → JmsIntegracaoLegado

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
| logback-spring.xml | leitura | /usr/etc/log/ | Arquivo de configuração de logs montado via ConfigMap |
| application.yml | leitura | src/main/resources | Arquivo de configuração principal da aplicação |
| application-des.yml | leitura | src/main/resources | Configurações específicas do ambiente de desenvolvimento |
| application-local.yml | leitura | src/main/resources | Configurações para execução local |
| openapi.yaml | leitura | src/main/resources/swagger | Especificação OpenAPI da aplicação |

---

## 10. Filas Lidas

**Google Cloud Pub/Sub:**
- **Subscription**: `business-spbb-base-integracao-legado-sub`
  - **Listener**: `RecebimentoMensagemPubSubListener`
  - **Descrição**: Subscription que consome mensagens de recebimento do SPB Core
  - **Configuração**: Controle de fluxo com max 2000 elementos e 100MB
  - **Project ID**: Variável por ambiente (bv-spbb-des, bv-spbb-uat, bv-spbb-prd)

---

## 11. Filas Geradas

**IBM MQ - Banco Votorantim (ISPB 59588111):**
- **Fila**: `QL.SPBB.RECEBIMENTO_MENSAGENS_CONVIVENCIA`
- **Queue Manager**: Variável por ambiente (QM.ATA.01 em DES, QM.59588111.01 em PRD/UAT)
- **Classe Responsável**: `IbmMQServiceImpl` via `jmsTemplateBV`

**IBM MQ - Banco BVSA (ISPB 01858774):**
- **Fila**: `QL.SPBB.RECEBIMENTO_MENSAGENS_CONVIVENCIA`
- **Queue Manager**: Variável por ambiente (QM.ATA.01 em DES, QM.01858774.01 em PRD/UAT)
- **Classe Responsável**: `IbmMQServiceImpl` via `jmsTemplateBVSA`

---

## 12. Integrações Externas

1. **Google Cloud Pub/Sub**
   - **Tipo**: Mensageria de entrada
   - **Descrição**: Recebe mensagens do SPB Core para processamento
   - **Configuração**: Via Spring Cloud GCP

2. **IBM MQ - Banco Votorantim**
   - **Tipo**: Mensageria JMS de saída
   - **Descrição**: Envia mensagens para sistema legado do Banco Votorantim
   - **Conexão**: Client mode com reconexão automática (timeout 1800s)

3. **IBM MQ - Banco BVSA**
   - **Tipo**: Mensageria JMS de saída
   - **Descrição**: Envia mensagens para sistema legado do Banco BVSA
   - **Conexão**: Client mode com reconexão automática (timeout 1800s)

4. **API Gateway BV**
   - **Tipo**: Autenticação OAuth2/JWT
   - **Descrição**: Validação de tokens JWT via JWKS
   - **Endpoints**: Variáveis por ambiente (des, uat, prd)

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem definida seguindo padrões ACL e separação de responsabilidades
- Uso adequado de frameworks consolidados (Spring Boot, Apache Camel)
- Boa cobertura de testes unitários com uso de mocks
- Configuração externalizada por ambiente
- Uso de Lombok reduzindo boilerplate
- Tratamento de exceções específicas do domínio
- Implementação de controle de fluxo no Pub/Sub
- Documentação básica presente (README, OpenAPI)

**Pontos de Melhoria:**
- Falta de logs estruturados em alguns pontos críticos
- Ausência de métricas customizadas de negócio
- Configurações hardcoded em algumas constantes (MAX_OUTSTANDING_ELEMENT_COUNT)
- Falta de documentação JavaDoc nas classes principais
- Tratamento de erro genérico em alguns pontos (Exception catch)
- Ausência de circuit breaker para chamadas externas
- Falta de testes de integração end-to-end

---

## 14. Observações Relevantes

1. **Segurança**: O sistema utiliza autenticação via JWT com validação de issuer e JWKS, mas as credenciais do IBM MQ são gerenciadas via variáveis de ambiente e cofre de senhas.

2. **Resiliência**: Implementa reconexão automática para IBM MQ com timeout de 30 minutos e controle de fluxo no Pub/Sub para evitar sobrecarga.

3. **Multi-tenancy**: Suporta múltiplas instituições bancárias através de configurações separadas de JMS templates e filas.

4. **Containerização**: Utiliza imagem base customizada do Banco Votorantim com suporte a multi-layer para otimização de build.

5. **Monitoramento**: Expõe endpoints do Spring Actuator na porta 9090 para health checks e métricas Prometheus.

6. **Ambientes**: Suporta múltiplos ambientes (local, des, uat, prd) com configurações específicas via profiles do Spring.

7. **Infraestrutura como Código**: Possui arquivo `infra.yml` para provisionamento automatizado no GCP via ATLE.

8. **Sanitização de Logs**: Implementa sanitização de mensagens nos logs para evitar injection attacks.

9. **Feature Toggle**: Integração com ConfigCat para gerenciamento de features via chave configurável.

10. **Pipeline CI/CD**: Configurado para Jenkins com geração automática de releases e deploy no Google Cloud Platform.