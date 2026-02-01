# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-ccbd-base-orch-token-pix** é um microserviço orquestrador responsável por disparar tokens de validação para funcionalidades do PIX. O sistema recebe requisições contendo informações de chave PIX (email ou telefone), gera um token JWT de autenticação junto a um serviço externo e envia o token OTP (One-Time Password) para o usuário através do canal especificado (email ou SMS). O serviço atua como intermediário entre o cliente e os serviços de geração e envio de tokens, implementando lógica de orquestração através do Apache Camel.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application.java` | Classe principal Spring Boot que inicializa a aplicação e habilita o Resource Server OAuth2 |
| `TokenPixController.java` | Controller REST v1 que expõe endpoint para envio de token PIX |
| `TokenPixControllerV2.java` | Controller REST v2 com suporte a canal e token JWT customizado |
| `TokenPixServiceImpl.java` | Implementação do serviço de domínio que orquestra o envio de tokens via Camel |
| `EnviarTokenRouter.java` | Rota Camel que define o fluxo de geração e envio de tokens, com suporte a canais privados |
| `GerarTokenJwtRepositoryImpl.java` | Repositório que consome API externa para gerar token JWT de autenticação |
| `TokenPixRepositoryImpl.java` | Repositório que envia requisição de token OTP para serviço externo |
| `TokenPixMapper.java` | Mapper que converte representações de API para objetos de domínio |
| `CamelContextWrapper.java` | Wrapper do contexto Camel para gerenciamento de rotas e templates |
| `AppProperties.java` | Classe de configuração que carrega propriedades da aplicação |
| `ObterCpf.java` | Utilitário que extrai CPF/CNPJ do contexto de segurança Spring |
| `ErrorFormat.java` | Utilitário para formatação de erros e conversão para ResponseEntity |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.x** - Framework principal da aplicação
- **Spring Security OAuth2** - Autenticação e autorização via JWT
- **Apache Camel 3.0.1** - Orquestração e integração de serviços
- **Springfox Swagger 3.0.0** - Documentação de APIs REST
- **Spring Actuator** - Monitoramento e métricas da aplicação
- **Micrometer Prometheus** - Exportação de métricas
- **RestTemplate** - Cliente HTTP para consumo de APIs externas
- **Apache HttpClient 4.5.14** - Cliente HTTP configurável
- **Lombok** - Redução de boilerplate code
- **JUnit 5** - Framework de testes unitários
- **Pact 4.0.3** - Testes de contrato (contract testing)
- **Rest Assured** - Testes funcionais de APIs REST
- **Logback** - Framework de logging
- **Maven** - Gerenciamento de dependências e build
- **Docker** - Containerização da aplicação
- **Java 11** - Linguagem e plataforma

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/banco-digital/dict/token` | `TokenPixController` | Envia token PIX para validação (versão 1) |
| POST | `/v2/banco-digital/dict/token` | `TokenPixControllerV2` | Envia token PIX com suporte a canal e token customizado (versão 2) |
| GET | `/actuator/health` | Spring Actuator | Verifica saúde da aplicação |
| GET | `/actuator/metrics` | Spring Actuator | Expõe métricas da aplicação |
| GET | `/actuator/prometheus` | Spring Actuator | Expõe métricas no formato Prometheus |
| GET | `/swagger-ui.html` | Springfox | Interface de documentação Swagger |

---

## 5. Principais Regras de Negócio

1. **Validação de MfaoPolicyID obrigatório**: O parâmetro `mfaoPolicyID` deve ser informado em todas as requisições, identificando o tipo de token a ser enviado.

2. **Validação de tipo de chave**: O tipo de chave (EMAIL ou PHONE) deve ser informado e determina o canal de envio do token.

3. **Validação de código da chave**: O código da chave (email ou telefone) é obrigatório e deve ser fornecido no corpo da requisição.

4. **Extração de CPF/CNPJ do contexto de segurança**: O documento do usuário é extraído automaticamente do token JWT através do Spring Security Context.

5. **Geração de token JWT para autenticação**: Antes de enviar o token OTP, o sistema gera um token JWT de autenticação usando credenciais client_credentials.

6. **Roteamento por canal**: A versão 2 da API suporta roteamento diferenciado baseado no canal (ex: "private" usa endpoint diferente).

7. **Tratamento de erros padronizado**: Todos os erros são convertidos para formato padronizado com código e descrição através do enum `ExceptionReasonEnum`.

8. **Suporte a múltiplos ambientes**: Configurações específicas por ambiente (local, des, qa, uat, prd) através de profiles Spring.

---

## 6. Relação entre Entidades

**Entidades de Domínio:**

- **TokenPixRequest**: Entidade principal que representa a requisição de envio de token
  - Atributos: username (CPF/CNPJ), telefone, email, mfaoPolicyID, notificationID, devicePushID, otpType
  
- **TokenAuthorization**: Representa o token JWT de autenticação
  - Atributos: accessToken, tokenType, expiresIn, scope
  
- **RequestDTO**: DTO que encapsula a requisição completa
  - Relacionamento: Contém 1 TokenPixRequest e 1 TokenAuthorization

- **TokenPixResponse**: Representa a resposta do serviço de envio de token
  - Atributos: statusCode, statusMsg, username, telefone, email, mfaoPolicyID, notification, devicePushID, transactionID

- **DadosTokenRepresentation**: Representação da API gerada pelo Swagger
  - Atributos: tipoChave (enum: PHONE/EMAIL), codigo
  - Relacionamento: Mapeada para TokenPixRequest pelo TokenPixMapper

**Fluxo de Relacionamento:**
```
DadosTokenRepresentation → [TokenPixMapper] → TokenPixRequest
TokenPixRequest + TokenAuthorization → RequestDTO → Enviado para API externa
```

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
| `application.yml` | Leitura | Spring Boot / AppProperties | Arquivo de configuração principal com propriedades por ambiente |
| `logback-spring.xml` | Leitura | Logback Framework | Configuração de logging (console e formato JSON) |
| `sboot-ccbd-base-orch-token-pix.yaml` | Leitura | Swagger Codegen Plugin | Especificação OpenAPI para geração de interfaces REST |
| `infra.yml` | Leitura | Infraestrutura (Kubernetes/OpenShift) | Configurações de infraestrutura como código (configmaps, secrets, probes) |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **API de Geração de Token JWT** | REST API | Serviço externo para geração de token JWT usando client_credentials OAuth2. Endpoints variam por ambiente (apigateway*.bvnet.bv/auth/oauth/v2/token-jwt) |
| **API de Envio de Token OTP** | REST API | Serviço que efetivamente envia o token OTP para o usuário via email ou SMS. Endpoints variam por ambiente (apigateway*.bvnet.bv/v1/banco-digital/token/otp-enviar) |
| **API de Envio de Token Privado** | REST API | Endpoint alternativo para canal privado (api-digital*.bancovotorantim.com.br/v1/private/token/enviar/interna) |
| **Serviço de JWK (JSON Web Key)** | REST API | Serviço para validação de tokens JWT OAuth2 (api-digital*.bancovotorantim.com.br/openid/connect/jwks.json) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (application, domain, common)
- Uso adequado de padrões como Repository, Service e Mapper
- Implementação de testes (unitários, integração e funcionais)
- Uso de Apache Camel para orquestração, facilitando manutenção de fluxos
- Configuração adequada de profiles Spring para múltiplos ambientes
- Documentação via Swagger/OpenAPI
- Uso de Lombok para reduzir boilerplate
- Tratamento de exceções centralizado com enum de erros
- Configuração de segurança OAuth2 adequada

**Pontos de Melhoria:**
- Alguns métodos com lógica duplicada entre v1 e v2 dos controllers
- Falta de validações mais robustas em alguns pontos (ex: formato de email/telefone)
- Comentários em código são escassos, dificultando entendimento de lógicas específicas
- Alguns nomes de variáveis poderiam ser mais descritivos (ex: "template" ao invés de "restTemplate")
- Falta de tratamento específico para timeouts e circuit breakers em integrações externas
- Configurações hardcoded em algumas classes (ex: valores padrão em TokenPixRequest)
- Ausência de cache para tokens JWT gerados, gerando chamadas desnecessárias

---

## 14. Observações Relevantes

1. **Versionamento de API**: O sistema implementa versionamento de API (v1 e v2), sendo que a v2 adiciona suporte a canal e token JWT customizado.

2. **Segurança**: A aplicação utiliza Spring Security OAuth2 Resource Server, validando tokens JWT em todas as requisições através de JWK.

3. **Monitoramento**: Configurado com Spring Actuator e Prometheus para observabilidade em produção.

4. **Infraestrutura**: Preparado para deploy em Kubernetes/OpenShift com configurações de probes (liveness e readiness).

5. **Ambientes**: Suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas via profiles e variáveis de ambiente.

6. **Logging**: Implementa logging estruturado em formato JSON para facilitar análise em ferramentas de log management.

7. **Testes de Contrato**: Utiliza Pact para testes de contrato, garantindo compatibilidade entre consumidores e provedores.

8. **Build e Deploy**: Utiliza Maven multi-módulo e Docker para empacotamento, com pipeline Jenkins configurado.

9. **Padrão de Nomenclatura**: Segue convenções do Banco Votorantim (prefixo "sboot-ccbd-base").

10. **Dependências de Segurança**: Algumas dependências possuem versões específicas para correção de vulnerabilidades (ex: tomcat-embed-core 9.0.96, httpclient 4.5.14).