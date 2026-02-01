# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema orquestrador responsável por gerar QR Codes para o fluxo de Open Banking - Iniciação de Pagamentos Pix. O serviço recebe um `interactId` (ID de redirecionamento) e orquestra a geração de um QR Code através de integração com um serviço atômico especializado. Utiliza Apache Camel para orquestração de fluxo e Spring Boot como framework base.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `OpenBankingQrcodeController` | Controller REST que expõe o endpoint GET para geração de QR Code |
| `OpenBankingQrcodeService` | Serviço de domínio que coordena a execução do fluxo Camel |
| `OpenBankingQrcodeRouter` | Rota Camel que define o fluxo de orquestração |
| `QrCodeRequestProcessor` | Processor Camel que monta o request com parâmetros fixos (160x160, JPG) |
| `OpenBankingQrcodeRepositoryImpl` | Implementação do repositório que integra com o serviço atômico de QR Code |
| `OpenBankingQrcodeMapper` | Classe utilitária para conversão entre objetos de domínio e representações |
| `CamelContextWrapper` | Wrapper para gerenciar o contexto Camel e templates de produção/consumo |
| `ResourceExceptionHandler` | Handler global de exceções para tratamento de erros |
| `ApplicationConfiguration` | Configuração do cliente REST para integração com serviço atômico |
| `OpenBankingQrcodeConfiguration` | Configuração dos beans de domínio e Camel |

---

## 3. Tecnologias Utilizadas

- **Framework:** Spring Boot 2.x
- **Linguagem:** Java 11
- **Orquestração:** Apache Camel 3.0.1
- **Segurança:** Spring Security OAuth2 (JWT)
- **Documentação API:** Swagger/OpenAPI 2.0 (Springfox 2.9.2)
- **Cliente HTTP:** RestTemplate
- **Monitoramento:** Spring Actuator + Prometheus + Grafana
- **Build:** Maven 3.3+
- **Containerização:** Docker (OpenJDK 11 com OpenJ9)
- **Testes:** JUnit 5, RestAssured, Pact (Consumer Contract Testing)
- **Utilitários:** Lombok, Logback
- **Infraestrutura:** OpenShift (Google Cloud Platform)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/banco-digital/qrcode` | `OpenBankingQrcodeController` | Gera QR Code a partir do interactId fornecido no header |

**Parâmetros:**
- Header: `interactId` (obrigatório) - ID do redirecionamento (interaction-id)

**Respostas:**
- 200: QR Code gerado com sucesso (Base64)
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 422: Unprocessable Entity (erro de negócio)
- 500: Internal Server Error

---

## 5. Principais Regras de Negócio

1. **Geração de QR Code com parâmetros fixos:** O sistema sempre gera QR Codes com dimensões 160x160 pixels no formato JPG
2. **Validação de interactId:** O interactId recebido é utilizado como texto a ser codificado no QR Code
3. **Tratamento de erros:** Erros na geração do QR Code são capturados e transformados em exceções de negócio (`OpenBankingQrcodeException`)
4. **Orquestração via Camel:** O fluxo de geração passa obrigatoriamente pela rota Camel que processa e delega para o repositório
5. **Segurança OAuth2:** Todas as requisições devem conter token JWT válido no header Authorization

---

## 6. Relação entre Entidades

**Entidades de Domínio:**

- `OpenBankingQrcodeRequest`: Representa a requisição de geração de QR Code
  - Atributos: texto (String), largura (Integer), altura (Integer), tipoImagem (String)
  
- `OpenBankingQrcodeResponse`: Representa a resposta com o QR Code gerado
  - Atributos: qrcode (String - Base64)

**Fluxo de dados:**
```
Controller → Service → CamelContext → Router → Processor → Repository → API Externa
                                                                ↓
                                                          QrCodeResponse
                                                                ↓
                                                    OpenBankingQrcodeResponse
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
| `application.yml` | leitura | Spring Boot | Configuração da aplicação (URLs, profiles, segurança) |
| `logback-spring.xml` | leitura | Logback | Configuração de logs (console e arquivo JSON) |
| `sboot-ccbd-base-orch-open-banking-qrcode.yaml` | leitura | Swagger Codegen | Especificação OpenAPI do serviço |
| `sboot-ccbd-base-atom-qrcode.yaml` | leitura | Swagger Codegen | Especificação OpenAPI do cliente consumido |

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
| `sboot-ccbd-base-atom-qrcode` | API REST | Serviço atômico responsável pela geração efetiva do QR Code. Endpoint: POST `/v1/banco-digital/qrcode` |
| OAuth2 JWT Provider | Segurança | Provedor de tokens JWT para autenticação. URL configurável por ambiente (ex: `https://api-digitaluat.bancovotorantim.com.br/openid/connect/jwks.json`) |
| Prometheus | Monitoramento | Coleta de métricas da aplicação via endpoint `/actuator/prometheus` |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões de Clean Architecture (separação domain/application/infrastructure)
- Uso adequado de Apache Camel para orquestração
- Boa separação de responsabilidades entre camadas
- Uso de Lombok reduzindo boilerplate
- Configuração adequada de segurança OAuth2
- Documentação OpenAPI bem estruturada
- Testes organizados em unit/integration/functional

**Pontos de Melhoria:**
- Classes de teste vazias (`OpenBankingQrcodeConfigurationTest`, `OpenBankingQrcodeControllerTest`, `OpenBankingQrcodeServiceTest`)
- Falta de tratamento de exceções mais granular
- Hardcoding de valores (dimensões 160x160, tipo JPG) que poderiam ser configuráveis
- Ausência de validações de entrada no controller
- Logs poderiam ser mais descritivos (mensagens genéricas como "Inicio do fluxo")
- Falta de documentação inline (JavaDoc) nas classes principais
- Configuração de timeout e retry não explícita para chamadas externas

---

## 14. Observações Relevantes

1. **Padrão de Orquestração:** O uso de Apache Camel para um fluxo simples pode ser considerado over-engineering, mas demonstra preparação para expansão futura do fluxo

2. **Segurança:** Sistema protegido por OAuth2 com JWT, seguindo padrões do Open Banking Brasil

3. **Observabilidade:** Infraestrutura completa de monitoramento com Prometheus e Grafana pré-configurada

4. **Multi-ambiente:** Configuração preparada para múltiplos ambientes (local, des, qa, uat, prd)

5. **Containerização:** Dockerfile otimizado usando OpenJ9 para redução de consumo de memória

6. **Testes de Contrato:** Implementação de Pact para testes de contrato consumer-driven

7. **Arquitetura de Referência:** Projeto segue template de scaffolding do Banco Votorantim (plugin versão 0.51.7)

8. **Limitações:** Sistema não possui persistência própria, funcionando como orquestrador puro

9. **Dependências Críticas:** Sistema totalmente dependente do serviço atômico `sboot-ccbd-base-atom-qrcode` para funcionamento

10. **Configuração de Recursos:** JVM configurada com limites conservadores (Xms64m, Xmx128m) adequados para um orquestrador leve