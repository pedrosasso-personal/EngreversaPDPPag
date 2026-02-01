# Ficha Técnica do Sistema

---

## 1. Descrição Geral

O **springboot-spag-base-manter-regras** é um projeto template/base para criação de serviços REST seguindo o padrão BFF (Backend For Frontend). Trata-se de um projeto Spring Boot que fornece uma estrutura inicial com configurações básicas, incluindo segurança via LDAP/Form Auth, documentação Swagger, suporte a múltiplos ambientes (local, des, qa, uat, prd) e infraestrutura como código para deploy em containers Docker/Kubernetes. O projeto possui apenas um endpoint de exemplo (Hello World) e serve como ponto de partida para desenvolvimento de novos componentes da área SPAG (Sistema de Pagamentos) do Banco Votorantim.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Server.java** | Classe principal da aplicação Spring Boot, responsável por inicializar o contexto e habilitar o Swagger |
| **HelloApi.java** | Controller REST que expõe o endpoint de exemplo `/hello` |
| **HelloService.java** | Camada de serviço que implementa a lógica de negócio do exemplo (formatação de mensagem) |
| **DocketConfiguration.java** | Configuração do Swagger/Springfox para documentação automática da API |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.0.0.RELEASE** - Framework principal
- **Java 8** - Linguagem de programação
- **Gradle 4.5.1** - Ferramenta de build
- **Springfox Swagger 2.8.0** - Documentação de API
- **Spring Security** - Segurança e autenticação
- **LDAP** - Autenticação via diretório corporativo
- **Logback** - Framework de logging
- **Docker** - Containerização
- **Kubernetes/OpenShift** - Orquestração de containers
- **JMeter** - Testes funcionais
- **JaCoCo** - Cobertura de código
- **SonarQube** - Análise de qualidade de código
- **Lombok** - Redução de código boilerplate
- **REST Assured** - Testes de API REST
- **Bibliotecas internas Votorantim**:
  - springboot-arqt-base-trilha-auditoria-web
  - springboot-arqt-base-security-form
  - sbootlib-arqt-base-tracing
  - springboot-arqt-base-security

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | /hello | HelloApi | Endpoint de exemplo que retorna uma mensagem "Hello {name}" personalizada |
| GET | /api-utils/status | N/A (biblioteca base) | Health check da aplicação usado pelos probes do Kubernetes |
| GET | /swagger-ui.html | N/A (Springfox) | Interface de documentação Swagger |

---

## 5. Principais Regras de Negócio

O projeto é um template/base e não possui regras de negócio complexas implementadas. A única regra presente é:

- **Formatação de mensagem personalizada**: O serviço HelloService recebe um nome como parâmetro e retorna uma mensagem formatada "Hello {nome}".

Este é apenas um exemplo didático para demonstrar a estrutura de camadas (Controller → Service).

---

## 6. Relação entre Entidades

Não se aplica. O projeto não possui entidades de domínio implementadas, apenas estrutura de diretórios vazios (`.keep` files) preparados para futuras implementações.

---

## 7. Estruturas de Banco de Dados Lidas

Não se aplica. O projeto não realiza operações de leitura em banco de dados.

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O projeto não realiza operações de escrita em banco de dados.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | Spring Boot (resources) | Arquivo principal de configuração da aplicação |
| application-local.yml | Leitura | Spring Boot (resources) | Configurações específicas do ambiente local |
| roles/*.yml | Leitura | Spring Boot (resources/roles) | Configuração de roles e permissões por ambiente (des, qa, uat, prd, local) |
| logback-spring.xml | Leitura | Logback | Configuração de logs da aplicação |
| .env | Leitura | Docker/Runtime | Variáveis de ambiente para execução local |

---

## 10. Filas Lidas

Não se aplica. O projeto não consome mensagens de filas.

---

## 11. Filas Geradas

Não se aplica. O projeto não publica mensagens em filas.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **LDAP Corporativo (BVNET)** | Autenticação | Integração com servidor LDAP para autenticação de usuários nos ambientes des, qa, uat e prd |
| **Nexus** | Repositório de artefatos | Repositório Maven/Gradle para dependências e publicação de artefatos |
| **SonarQube** | Análise de código | Integração para análise de qualidade e cobertura de código |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Estrutura bem organizada seguindo padrões de arquitetura em camadas (controller, service, domain, repository)
- Separação clara de testes (unit, integration, functional)
- Configuração adequada para múltiplos ambientes
- Uso de ferramentas modernas (Spring Boot, Swagger, Docker, Kubernetes)
- Implementação de probes de saúde para Kubernetes
- Configuração de segurança com LDAP e autenticação in-memory para testes
- Documentação básica presente (README, comentários)

**Pontos de Melhoria:**
- Ausência de testes unitários, de integração e funcionais implementados (apenas estrutura)
- Falta de tratamento de exceções customizado
- Configurações hardcoded em alguns pontos (ex: versões de bibliotecas)
- Ausência de validações de entrada nos endpoints
- Falta de logs estruturados e rastreabilidade completa
- Documentação Swagger básica, poderia ser mais detalhada
- Ausência de métricas e monitoramento (Prometheus, Micrometer)

O código serve bem ao seu propósito como template inicial, mas necessita de implementações adicionais para ser considerado production-ready.

---

## 14. Observações Relevantes

1. **Projeto Template**: Este é um projeto base/template destinado a ser clonado e customizado através de um script gerador de projetos. Não deve ser usado diretamente em produção sem implementações adicionais.

2. **Padrão BFF**: O projeto segue o padrão Backend For Frontend, adequado para criar APIs específicas para diferentes tipos de clientes (Web, Mobile).

3. **Ambientes Configurados**: O projeto está preparado para 5 ambientes: local, des (desenvolvimento), qa (quality assurance), uat (user acceptance testing) e prd (produção).

4. **Segurança Configurável**: Suporta autenticação via LDAP (ambientes corporativos) e in-memory (desenvolvimento/testes).

5. **Infraestrutura como Código**: Possui configuração completa para deploy em Kubernetes/OpenShift através do arquivo `infra.yml`.

6. **Pipeline CI/CD**: Configurado para integração com Jenkins (jenkins.properties) e possui tasks Gradle para build, testes e publicação.

7. **Repositórios de Referência**: O README menciona outros repositórios de referência para implementações específicas (CRUD, WS Client, REST Client).

8. **Rede Corporativa**: O projeto está configurado para funcionar na rede interna do Banco Votorantim (bvnet.bv), com proxies e repositórios internos.

9. **Monitoramento**: Configurado com health checks (`/api-utils/status`) para liveness e readiness probes do Kubernetes.

10. **Logging Contextual**: Os logs incluem informações de contexto como ticket e fase através do MDC (Mapped Diagnostic Context).