# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-ccbd-base-orch-consulta-informe** é um serviço stateless desenvolvido em Spring Boot que atua como orquestrador para consulta de informes de rendimento. O sistema recebe requisições do frontend (mobile) contendo CPF e ano, valida os dados, e consome o serviço downstream **sboot-regp-base-orch-informe-rendimentos** para obter o informe de rendimento em formato PDF (codificado em Base64). O serviço implementa autenticação OAuth2/JWT e segue padrões RESTful.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal Spring Boot, inicializa a aplicação e habilita Resource Server OAuth2 |
| **InformeRendimentoController** | Controller REST que expõe o endpoint de geração de PDF |
| **InformeRendimentoService** | Serviço de domínio que orquestra a geração do PDF via Apache Camel |
| **InformeRendimentoRouter** | Rota Apache Camel que define o fluxo de processamento |
| **InformeRendimentoRepositoryImpl** | Implementação do repositório que consome o serviço externo via RestTemplate |
| **ConsultaInformeRendimento** | Entidade de domínio representando os dados da consulta (CPF e ano) |
| **Arquivo** | Entidade de domínio representando o arquivo PDF retornado |
| **ApiExceptionHandler** | Tratador global de exceções para padronização de respostas de erro |
| **ConsultaInformeRendimentoMapper** | Mapper para conversão entre representações e objetos de domínio |
| **ArquivoMapper** | Mapper para conversão do objeto Arquivo para representação |
| **CamelContextWrapper** | Wrapper do contexto Apache Camel para gerenciamento de rotas |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.x** (framework base)
- **Spring Web** (REST APIs)
- **Spring Security OAuth2 Resource Server** (autenticação JWT)
- **Spring Validation** (validação de dados)
- **Apache Camel 3.12.0** (orquestração e integração)
- **Hibernate Validator** (validação de CPF)
- **ModelMapper 2.4.4** (mapeamento de objetos)
- **Springfox/Swagger 3.0.0** (documentação OpenAPI)
- **Micrometer/Prometheus** (métricas e monitoramento)
- **Logback** (logging em formato JSON)
- **RestTemplate** (cliente HTTP)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **JUnit 5** (testes unitários)
- **Rest Assured** (testes funcionais)
- **Pact** (testes de contrato)
- **Java 11** (linguagem)
- **Lombok** (redução de boilerplate)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/informe-redimentos/pdf/por-cliente` | InformeRendimentoController | Gera PDF do informe de rendimento para um cliente PF com base no CPF e ano informados |

**Observação:** O endpoint requer autenticação via Bearer Token (JWT).

---

## 5. Principais Regras de Negócio

1. **Validação de CPF**: O CPF informado deve ser válido segundo o algoritmo de validação brasileiro (implementado via anotação `@CPF` do Hibernate Validator)

2. **Validação de Ano**: O ano deve ser maior ou igual a 2020

3. **Validação de Formato**: O CPF deve conter exatamente 11 dígitos numéricos

4. **Orquestração via Camel**: O processamento da requisição é orquestrado através de rotas Apache Camel, permitindo extensibilidade e desacoplamento

5. **Tratamento de Erros**: Erros de comunicação com o serviço downstream são capturados e transformados em respostas padronizadas (Problem Details)

6. **Validação Programática**: Além das validações declarativas, há validação programática via SmartValidator antes do processamento

---

## 6. Relação entre Entidades

**Entidades de Domínio:**

- **ConsultaInformeRendimento**
  - Atributos: `ano` (Integer), `cpf` (String)
  - Validações: CPF válido, ano >= 2020

- **Arquivo**
  - Atributos: `name` (String), `file` (String - Base64)
  - Representa o PDF retornado pelo serviço downstream

**Relacionamento:**
- ConsultaInformeRendimento é o input do processo
- Arquivo é o output do processo
- Não há relacionamento de persistência entre as entidades (serviço stateless)

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
| application.yml | leitura | Spring Boot (startup) | Arquivo de configuração da aplicação com profiles (local, des, qa, uat, prd) |
| logback-spring.xml | leitura | Logback (startup) | Configuração de logging em formato JSON para stdout |
| messages.properties | leitura | ValidationConfig/MessageSource | Mensagens de validação internacionalizadas |
| swagger-server/*.json | leitura | Swagger Codegen Plugin | Especificação OpenAPI do servidor para geração de código |
| swagger-client/*.json | leitura | Swagger Codegen Plugin | Especificação OpenAPI do cliente downstream para geração de código |

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
| **sboot-regp-base-orch-informe-rendimentos** | API REST | Serviço downstream que gera o PDF do informe de rendimento. Endpoint: `/v1/api/clientes/pf/pdf` (POST). Comunicação via RestTemplate com autenticação JWT. |
| **OAuth2/JWT Provider** | Serviço de Autenticação | Provedor de tokens JWT para autenticação. URLs variam por ambiente (des, qa, uat, prd). Validação via JWK Set URI. |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 8/10

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo Clean Architecture (separação em módulos: domain, application, common)
- Uso adequado de padrões como Repository, Service, Mapper
- Tratamento de exceções centralizado e padronizado (RFC 7807 - Problem Details)
- Configuração externalizada por profiles
- Uso de validações declarativas (Bean Validation)
- Documentação OpenAPI/Swagger
- Separação de testes (unit, integration, functional)
- Uso de Apache Camel para orquestração, facilitando extensibilidade
- Configuração de métricas e health checks
- Uso de Lombok para redução de boilerplate

**Pontos de Melhoria:**
- Falta de logs estruturados no código de negócio (apenas configuração de logging)
- Ausência de testes unitários nos arquivos fornecidos (marcados como NAO_ENVIAR)
- Validação de CPF poderia ter mensagem de erro mais específica
- Falta de circuit breaker ou retry para chamadas ao serviço downstream
- Documentação inline (JavaDoc) ausente na maioria das classes
- Configuração de timeout não explícita no RestTemplate

---

## 14. Observações Relevantes

1. **Arquitetura Modular**: O projeto está organizado em 3 módulos Maven (common, domain, application), seguindo princípios de Clean Architecture

2. **Geração de Código**: Utiliza Swagger Codegen para gerar automaticamente interfaces de API (servidor) e clientes REST (consumidor)

3. **Multi-ambiente**: Suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas via Spring Profiles

4. **Segurança**: Implementa OAuth2 Resource Server com validação JWT via JWK Set

5. **Observabilidade**: Expõe métricas Prometheus e health checks na porta 9090

6. **Containerização**: Dockerfile otimizado usando OpenJ9 (JVM com menor footprint de memória)

7. **Auditoria**: Integração com biblioteca de trilha de auditoria do Banco Votorantim

8. **Infraestrutura como Código**: Arquivo `infra.yml` define configurações de deployment Kubernetes

9. **Versionamento de API**: Utiliza versionamento via path (`/v1/...`)

10. **Padrão de Nomenclatura**: Segue convenção de nomenclatura do Banco Votorantim (sboot-ccbd-base-orch-*)

11. **Limitação de Recursos**: Configuração de JVM com limites conservadores (Xms64m, Xmx128m)

12. **Validação em Camadas**: Validação tanto na camada de apresentação (Bean Validation) quanto na camada de domínio (validação programática)