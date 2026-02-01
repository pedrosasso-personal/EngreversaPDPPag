# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **springboot-pgft-base-dash-boleto-bff** é um componente BFF (Backend For Frontend) desenvolvido em Spring Boot. Sua função principal é atuar como intermediário entre o frontend (aplicação Angular) e os serviços backend (orquestradores ou atômicos), gerenciando autenticação, autorização baseada em roles, e roteamento dinâmico de requisições HTTP. O BFF também implementa um mecanismo de refresh automático de token JWT para integração com API Gateway, além de aplicar filtros de segurança e sanitização de headers nas requisições e respostas.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Server** | Classe principal que inicializa a aplicação Spring Boot. |
| **DashBoletoApi** | Controller REST que recebe todas as requisições do frontend e as encaminha para o backend apropriado. |
| **DashBoletoService / DashBoletoServiceImpl** | Serviço responsável por validar roles do usuário e encaminhar requisições ao repositório. |
| **DashBoletoRepository / DashBoletoRepositoryImpl** | Repositório que executa as chamadas HTTP para os serviços backend via RestTemplate. |
| **TokenJwtService / TokenJwtServiceImpl** | Serviço que gerencia o refresh periódico do token JWT. |
| **TokenJwtRepository / TokenJwtRepositoryImpl** | Repositório que busca o token JWT no API Gateway. |
| **TokenJwtInterceptorImpl** | Interceptor HTTP que adiciona o token JWT no header Authorization de todas as requisições de saída. |
| **TokenJwtProvider** | Provider que armazena o token JWT atual e o intervalo para próxima execução do refresh. |
| **TokenJwtConfiguration** | Configuração do scheduler que executa o refresh do token JWT periodicamente. |
| **DashBoletoConfiguration** | Configuração dos RestTemplates (com e sem interceptor de token). |
| **DashBoletoProperties** | Propriedades de configuração do BFF (endpoints, API Gateway, redirect pattern, token JWT). |
| **EndpointProperties** | Representa um endpoint configurado (URI, método HTTP, roles necessárias). |
| **BaseBffCorsFilter** | Filtro CORS customizado para permitir requisições de origens específicas. |
| **DashBoletoExceptionHandler** | Handler global de exceções. |
| **HeaderUtils** | Utilitário para sanitização de headers HTTP (request e response). |
| **RoleResultEnum** | Enum que representa o resultado da validação de roles (OK, FORBIDDEN, NOT_FOUND). |
| **TokenJwtResponse** | DTO que representa a resposta do serviço de token JWT. |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.0.0.RELEASE**
- **Spring Security** (autenticação Form Auth e LDAP)
- **Spring Web** (REST APIs)
- **RestTemplate** (cliente HTTP)
- **Apache HttpClient**
- **Lombok** (redução de boilerplate)
- **Swagger / Springfox** (documentação de API)
- **Gradle 4.5.1** (build)
- **Docker** (containerização)
- **Prometheus + Grafana** (métricas e monitoramento)
- **JUnit + Mockito** (testes unitários)
- **Spring Boot Test** (testes de integração)
- **JMeter** (testes funcionais)
- **Logback** (logging)
- **Micrometer** (métricas para Prometheus)
- **HikariCP** (pool de conexões)
- **Java 8**

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET, POST, PUT, DELETE | `/dash-boleto/**` | DashBoletoApi | Endpoint genérico que encaminha requisições para o backend. Valida roles e redireciona dinamicamente para o serviço apropriado. |

**Observação:** O BFF não expõe endpoints de negócio diretamente. Ele atua como proxy, validando permissões e redirecionando requisições para os serviços backend configurados em `application.yml`.

---

## 5. Principais Regras de Negócio

- **Validação de Roles por Endpoint:** Cada endpoint configurado pode exigir roles específicas. O BFF valida se o usuário autenticado possui as roles necessárias antes de encaminhar a requisição.
- **Roteamento Dinâmico:** O BFF extrai o nome da aplicação backend da URI e constrói dinamicamente a URL de destino usando um padrão configurável (`redirectPattern`).
- **Refresh Automático de Token JWT:** O BFF mantém um token JWT válido, renovando-o automaticamente antes de expirar (90% do tempo de expiração).
- **Sanitização de Headers:** Remove headers sensíveis ou desnecessários das requisições e respostas (mantém apenas Content-Type, Content-Length e headers de auditoria BV).
- **Tratamento de Erros HTTP:** Captura exceções de clientes HTTP e retorna respostas apropriadas ao frontend.

---

## 6. Relação entre Entidades

O sistema não possui entidades de domínio complexas. As principais estruturas de dados são:

- **TokenJwtResponse:** Contém `accessToken` e `expiresIn` retornados pelo API Gateway.
- **EndpointProperties:** Representa a configuração de um endpoint (URI, método, roles).
- **DashBoletoProperties:** Agrega configurações gerais do BFF (API Gateway, redirect pattern, token JWT, lista de endpoints).
- **RoleResultEnum:** Enum que representa o resultado da validação de roles.

Não há relacionamentos JPA ou banco de dados. O BFF é stateless e não persiste dados.

---

## 7. Estruturas de Banco de Dados Lidas

Não se aplica. O sistema não acessa diretamente banco de dados.

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema não altera dados em banco de dados.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Descrição |
|-----------------|----------|-------------------------|-----------|
| `application.yml` | Leitura | Spring Boot | Arquivo de configuração principal da aplicação. |
| `application-local.yml` | Leitura | Spring Boot | Configurações específicas do perfil local. |
| `roles/*.yml` | Leitura | Spring Security | Mapeamento de roles por ambiente (des, qa, uat, prd, local, integration). |
| `logback-spring.xml` | Leitura | Logback | Configuração de logging. |
| `.env.sample` | Leitura (manual) | Desenvolvedor | Template de variáveis de ambiente. |
| `Dockerfile` | Leitura | Docker | Definição da imagem Docker. |
| `build/libs/*.jar` | Gravação | Gradle (bootJar) | Artefato JAR gerado pelo build. |

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

---

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas.

---

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| **API Gateway** | REST | Utilizado para obter token JWT (`/auth/oauth/v2/token-jwt`). Configurado via `dash-boleto.api-gateway` e credenciais OAuth2. |
| **Serviços Backend (Atômicos/Orquestradores)** | REST | O BFF redireciona requisições para serviços backend dinamicamente, construindo a URL a partir do padrão `redirectPattern` e do nome da aplicação extraído da URI. |
| **LDAP** | LDAP | Autenticação de usuários via LDAP (configurável, pode ser desabilitado para usar autenticação in-memory). |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades (camadas de service, repository, configuration).
- Uso adequado de injeção de dependências e anotações Spring.
- Testes unitários e de integração presentes.
- Configuração de métricas (Prometheus/Grafana) e logging estruturado.
- Uso de Lombok para reduzir boilerplate.
- Documentação Swagger configurada.

**Pontos de Melhoria:**
- **Tratamento de Exceções:** O `DashBoletoExceptionHandler` apenas relança exceções, sem tratamento específico ou logging adequado.
- **Validação de Entrada:** Falta validação de parâmetros de entrada (ex: URI, headers).
- **Segurança:** Credenciais OAuth2 são configuradas via variáveis de ambiente, mas não há menção a uso de cofres de senhas (Vault, etc).
- **Testes:** Cobertura de testes poderia ser maior, especialmente em cenários de erro e edge cases.
- **Documentação:** Falta documentação inline (Javadoc) em algumas classes e métodos.
- **Hardcoded Values:** Alguns valores estão hardcoded (ex: `DELAY_TIME_PERCENT_REFRESH_TOKEN = 0.9`), poderiam ser configuráveis.
- **Complexidade:** A lógica de roteamento dinâmico e sanitização de headers poderia ser melhor documentada e testada.

---

## 14. Observações Relevantes

- **Perfis de Ambiente:** O sistema suporta múltiplos perfis (local, des, qa, uat, prd, integration), com configurações específicas de roles e endpoints.
- **Autenticação Flexível:** Suporta autenticação LDAP ou in-memory (útil para testes locais).
- **CORS Configurado:** Permite requisições de origens específicas (ambientes des, qa, uat, prd).
- **Métricas e Monitoramento:** Integração com Prometheus e Grafana para observabilidade.
- **Docker e CI/CD:** Dockerfile e configurações Jenkins presentes para deploy automatizado.
- **Testes Funcionais:** Inclui testes JMeter para validação funcional.
- **Refresh de Token Assíncrono:** O refresh do token JWT é executado em uma thread separada via scheduler, garantindo que o token esteja sempre válido.
- **Sanitização de Headers:** Remove headers sensíveis (ex: Authorization) antes de encaminhar requisições, mantendo apenas os necessários.

---

**Conclusão:** O sistema é um BFF bem estruturado, com boas práticas de arquitetura e separação de responsabilidades. Há espaço para melhorias em tratamento de exceções, validação de entrada, documentação e cobertura de testes, mas no geral é um código de qualidade aceitável para produção.