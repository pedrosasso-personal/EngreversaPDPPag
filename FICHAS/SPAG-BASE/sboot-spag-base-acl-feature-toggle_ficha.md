---
## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema **sboot-spag-base-acl-feature-toggle** é uma Anti-Corruption Layer (ACL) desenvolvida em Java com Spring Boot e Apache Camel. Seu objetivo é fornecer uma API REST para consulta de feature flags (feature toggles) de forma centralizada, isolando o domínio interno de mudanças em sistemas externos de gerenciamento de features. O sistema atua como intermediário entre consumidores e o provedor de feature toggles (ConfigCat), garantindo a integridade do modelo de negócio e facilitando a ativação/desativação de funcionalidades em tempo de execução.

---

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application.java** | Classe principal que inicializa a aplicação Spring Boot e habilita o módulo de Feature Toggle |
| **FeatureToggleRouter.java** | Roteador Apache Camel que define o fluxo de processamento das requisições de feature toggle |
| **FeatureToggleApi.java** | Define a API REST usando Camel REST DSL, expondo o endpoint GET `/feature-toggle/{feature}` |
| **FeatureToggleService.java** | Serviço que encapsula a lógica de consulta ao provedor de feature toggles (ConfigCat) |
| **FeatureToggleProcessor.java** | Processador Camel que valida os parâmetros da requisição (feature name e isBoolean) |
| **ExceptionProcessor.java** | Processador Camel responsável pelo tratamento de exceções e formatação de respostas de erro |
| **FeatureToggleMapper.java** | Interface MapStruct para conversão de String em objeto FeatureResult |
| **JwtClientCredentialInterceptor.java** | Interceptor que injeta token de autorização nas requisições |
| **JwtAuthorizationHeaderGenerator.java** | Implementação que gera tokens de autorização a partir de credenciais Basic Auth |
| **FeatureToogleException.java** | Exceção customizada que encapsula erros relacionados a feature toggles com status HTTP |
| **FeatureToggleConfiguration.java** | Classe de configuração Spring que registra beans necessários |

---

### 3. Tecnologias Utilizadas

- **Java 11+**
- **Spring Boot** (framework principal)
- **Apache Camel** (integração e roteamento)
- **Spring Security OAuth2** (autenticação e autorização JWT)
- **MapStruct** (mapeamento de objetos)
- **ConfigCat** (provedor de feature toggles - biblioteca `sbootlib-arqt-base-feature-toggle`)
- **OpenAPI/Swagger** (documentação de API)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Spring Boot Actuator** (monitoramento e health checks)
- **OpenTelemetry** (observabilidade e tracing)
- **JUnit 5 + Mockito** (testes unitários)
- **Logback** (logging)

---

### 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/feature-toggle/{feature}` | FeatureToggleApi.java | Consulta o valor de uma feature toggle específica. Aceita parâmetro query `isBoolean` (default: true) para indicar se a feature é booleana ou textual |

---

### 5. Principais Regras de Negócio

1. **Validação de Parâmetros**: O sistema valida se o nome da feature e o tipo (booleano ou texto) foram informados corretamente, retornando erro 400 (Bad Request) caso contrário.

2. **Consulta Tipada**: O sistema diferencia entre features booleanas (flags on/off) e features textuais (valores string), direcionando para métodos específicos de consulta.

3. **Tratamento de Erros**: Quando uma feature não é encontrada ou ocorre erro na consulta ao provedor, o sistema retorna erro 500 (Internal Server Error) com mensagem descritiva.

4. **Autenticação JWT**: Todas as requisições devem conter token JWT válido no header Authorization, validado contra o API Gateway configurado.

5. **Interceptação de Segurança**: O sistema intercepta todas as chamadas diretas do Camel para injetar automaticamente tokens de autorização.

6. **Cache de Features**: Configurado com duração de cache de 180 segundos (3 minutos) para otimizar consultas ao provedor externo.

---

### 6. Relação entre Entidades

O sistema possui uma estrutura simples de entidades:

- **FeatureResult**: Entidade de resposta que encapsula o resultado da consulta (contém apenas o atributo `result` do tipo String)

**Relacionamentos**: Não há relacionamentos complexos entre entidades. O sistema atua como proxy/adaptador, convertendo requisições REST em consultas ao provedor ConfigCat e retornando resultados simples.

---

### 7. Estruturas de Banco de Dados Lidas

não se aplica

---

### 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

### 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot | Arquivo de configuração principal da aplicação |
| application-des.yml | leitura | Spring Boot | Configurações específicas do ambiente de desenvolvimento |
| application-local.yml | leitura | Spring Boot | Configurações para execução local |
| logback-spring.xml | leitura | Logback (via LOGGING_CONFIG) | Configuração de logs, montado via ConfigMap em `/usr/etc/log` |
| openapi.yaml | leitura | Swagger/OpenAPI | Especificação da API REST |

---

### 10. Filas Lidas

não se aplica

---

### 11. Filas Geradas

não se aplica

---

### 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **ConfigCat** | API/SDK | Provedor de feature toggles utilizado através da biblioteca `sbootlib-arqt-base-feature-toggle` (versão 3.0.5). Requer chave de API configurada via variável de ambiente `FT_KEY` |
| **API Gateway BV** | OAuth2/JWT | Sistema de autenticação e autorização. URLs variam por ambiente (des/uat/prd). Valida tokens JWT e fornece JWKS para validação |

---

### 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Código bem organizado seguindo padrões de arquitetura limpa (separação clara entre camadas: presentation, service, config, security)
- Uso adequado de frameworks modernos (Spring Boot, Camel, MapStruct)
- Implementação de tratamento de exceções customizado
- Boa cobertura de testes unitários
- Uso de interceptors para cross-cutting concerns (segurança)
- Configuração externalizada por ambiente
- Documentação OpenAPI presente
- Logs estruturados e informativos

**Pontos de Melhoria:**
- Falta de comentários JavaDoc em algumas classes importantes
- A classe `JwtAuthorizationHeaderGenerator` possui lógica de parsing manual de credenciais Basic Auth que poderia ser mais robusta
- Ausência de testes de integração mais abrangentes
- Configuração de cache hardcoded (180 segundos) poderia ser parametrizável
- Mensagens de erro poderiam ser mais descritivas e internacionalizadas
- Falta de validação mais rigorosa de entrada (ex: regex para nome de features)

---

### 14. Observações Relevantes

1. **Arquitetura Atlante**: O projeto segue o padrão arquitetural Atlante do Banco Votorantim, utilizando o parent POM `pom-atle-base-sboot-acl-parent` versão 2.3.1.

2. **Deployment Multi-Cloud**: A aplicação está preparada para deployment em ambiente Google Cloud Platform (GCP), conforme indicado no `jenkins.properties` e configurações de infraestrutura.

3. **Observabilidade**: Integração com OpenTelemetry habilitada via anotação `@CamelOpenTelemetry` para tracing distribuído.

4. **Health Checks**: Endpoints do Actuator expostos na porta 9090 para monitoramento (health, metrics, prometheus).

5. **Segurança**: 
   - Endpoints públicos configuráveis por ambiente
   - Swagger desabilitado em produção
   - Cookies com flags `http-only` e `secure`

6. **Ambientes**: Suporta múltiplos ambientes (local, des, uat, prd) com configurações específicas via profiles Spring.

7. **CI/CD**: Integração com Jenkins configurada, com geração automática de releases e suporte a JDK 11.

8. **Containerização**: Dockerfile multi-layer otimizado para reduzir tamanho da imagem e melhorar cache de builds.