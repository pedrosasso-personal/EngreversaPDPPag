# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-saca-scco-acl-registro-was** é um serviço stateless desenvolvido em Spring Boot que atua como uma camada de integração (ACL - Anti-Corruption Layer) para emissão de carnês de contratos. O sistema recebe requisições REST, processa através de rotas Apache Camel e consome um webservice legado (WAS - WebSphere Application Server) para gerar carnês em formato PDF codificado em Base64.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application.java` | Classe principal Spring Boot que inicializa a aplicação com segurança OAuth2 habilitada |
| `RegistroWasController.java` | Controller REST que expõe o endpoint de emissão de carnê |
| `RegistroWasService.java` | Serviço de domínio que orquestra a chamada via Apache Camel |
| `RegistroWasRouter.java` | Rota Apache Camel que define o fluxo de processamento |
| `RegistroWasProcessor.java` | Processador Camel que manipula a resposta do repositório |
| `RegistroWasRepositoryImpl.java` | Implementação do repositório que consome o webservice externo |
| `CamelContextWrapper.java` | Wrapper do contexto Camel para gerenciamento de rotas e templates |
| `CarneRequest.java` | Objeto de domínio representando a requisição de carnê |
| `CarneResponse.java` | Objeto de domínio representando a resposta com o PDF em Base64 |
| `OpenApiConfiguration.java` | Configuração do Swagger/OpenAPI para documentação |
| `RegistroWasConfiguration.java` | Configuração dos beans Spring do domínio |
| `RestConfiguration.java` | Configuração do RestTemplate com autenticação básica |

---

## 3. Tecnologias Utilizadas

- **Java 11** (OpenJDK com OpenJ9)
- **Spring Boot** (framework principal)
- **Apache Camel 3.0.1** (orquestração e integração)
- **Spring Security OAuth2** (autenticação e autorização via JWT)
- **Swagger/Springfox 2.9.2** (documentação de API)
- **RestTemplate** (cliente HTTP)
- **Lombok** (redução de boilerplate)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Logback** (logging)
- **Micrometer/Prometheus** (métricas e monitoramento)
- **MapStruct 1.3.1** (mapeamento de objetos)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/emitirCarne` | `RegistroWasController` | Emite carnê de contrato em formato PDF Base64. Recebe `numeroContrato` (obrigatório), `codigoParceiroComercial` e `codigoProduto` (opcionais) como query parameters |

---

## 5. Principais Regras de Negócio

1. **Emissão de Carnê**: O sistema recebe um número de contrato e solicita a geração do carnê ao sistema legado WAS
2. **Autenticação Básica**: Todas as chamadas ao webservice externo utilizam autenticação básica com credenciais configuradas por ambiente
3. **Conversão para Base64**: O PDF retornado pelo webservice é convertido para Base64 antes de ser enviado ao cliente
4. **Segurança OAuth2**: Todos os endpoints são protegidos por OAuth2 com validação de JWT
5. **Tratamento de Erros**: Erros na comunicação com o webservice são capturados e convertidos em `BusinessException`

---

## 6. Relação entre Entidades

O sistema possui uma estrutura de domínio simples:

- **CarneRequest**: Entidade de entrada contendo:
  - `numeroContrato` (String)
  - `codigoParceiroComercial` (Integer)
  - `codigoProduto` (Integer)

- **CarneResponse**: Entidade de saída contendo:
  - `imageBase64` (String) - PDF do carnê codificado em Base64

Não há relacionamentos complexos entre entidades, pois o sistema atua como um proxy/adaptador.

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
| `logback-spring.xml` | Leitura | `/usr/etc/log/` (runtime) | Arquivo de configuração de logs carregado em tempo de execução conforme ambiente |
| `application.yml` | Leitura | `application/src/main/resources/` | Arquivo de configuração da aplicação Spring Boot |
| `sboot-saca-scco-acl-registro-was.yaml` | Leitura | `application/src/main/resources/swagger/` | Especificação OpenAPI/Swagger do serviço |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| **saca-scco-webservice-registro-was-rs** | REST API | Webservice legado hospedado em WebSphere que gera carnês em PDF. Endpoints variam por ambiente (DES, QA, UAT, PRD). Autenticação via Basic Auth |
| **API Gateway BV** | OAuth2 Provider | Provedor de autenticação OAuth2 para validação de tokens JWT. URLs variam por ambiente |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões de Clean Architecture (separação em módulos: domain, application, common)
- Uso adequado de Apache Camel para orquestração
- Implementação de segurança OAuth2
- Documentação via Swagger
- Uso de Lombok para reduzir boilerplate
- Configuração adequada de profiles por ambiente
- Implementação de health checks e métricas

**Pontos de Melhoria:**
- Logging de credenciais em `RestConfiguration` (linha com `log.info` expondo user/password) - **risco de segurança**
- Falta de tratamento de exceções mais granular no controller
- Ausência de validações de entrada nos parâmetros opcionais
- Conversão manual de Base64 poderia usar utilitários mais modernos (Base64 do Java 8+)
- Falta de documentação inline (JavaDoc) nas classes principais
- Processador Camel (`RegistroWasProcessor`) apenas repassa dados sem lógica adicional aparente
- Configuração de timeout não explícita no RestTemplate

---

## 14. Observações Relevantes

1. **Ambiente Multi-Cloud**: O sistema está preparado para deploy em Google Cloud Platform (conforme `jenkins.properties`)

2. **Segurança**: 
   - Credenciais são gerenciadas via secrets do Kubernetes
   - Certificados Java são montados via volume global
   - Proxy desabilitado por padrão

3. **Monitoramento**: 
   - Actuator exposto na porta 9090
   - Métricas Prometheus habilitadas
   - Health checks configurados com tempos adequados

4. **Containerização**: 
   - Imagem Docker baseada em Alpine Linux com OpenJ9
   - JVM configurada com heap mínimo de 64MB e máximo de 128MB

5. **Pipeline CI/CD**: 
   - Integração com Jenkins
   - Suporte a testes unitários, integração e funcionais separados
   - Validação arquitetural via ArchUnit

6. **Limitações Identificadas**:
   - Sistema não possui cache, cada requisição gera nova chamada ao webservice
   - Não há retry automático em caso de falha na comunicação
   - Parâmetros `codigoParceiroComercial` e `codigoProduto` são recebidos mas não utilizados

7. **Dependências de Infraestrutura**:
   - Requer conectividade com rede interna BV (bvnet.bv)
   - Depende de LDAP global para autenticação de service accounts