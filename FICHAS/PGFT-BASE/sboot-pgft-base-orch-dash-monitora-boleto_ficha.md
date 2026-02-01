# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-pgft-base-orch-dash-monitora-boleto** é um serviço de orquestração stateless desenvolvido em Spring Boot que atua como intermediário para consulta e agregação de dados de monitoramento de boletos. Ele expõe endpoints REST para visualização de lançamentos e dashboards, integrando-se com um serviço atômico (dash-atomico) para obtenção dos dados. Utiliza Apache Camel para orquestração de fluxos e processamento de mensagens.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal que inicializa a aplicação Spring Boot |
| **DashMonitoraBoletoController** | Controlador REST que expõe endpoint para consulta de dados do dashboard de monitoramento |
| **LancamentoController** | Controlador REST que expõe endpoints para consulta de lançamentos (visão geral atual e comparativa de 7 dias) |
| **DashMonitoraBoletoService** | Serviço de domínio que orquestra o fluxo de obtenção de dados do dashboard via Camel |
| **LancamentoService** | Serviço de domínio que orquestra o fluxo de obtenção de lançamentos via Camel |
| **DashMonitoraBoletoRouter** | Roteador Camel que define o fluxo de processamento para dashboard |
| **LancamentoRouter** | Roteador Camel que define o fluxo de processamento para lançamentos |
| **DashMonitoraBoletoRepositoryImpl** | Implementação do repositório para acesso a dados do dashboard (mock) |
| **LancamentoRepositoryImpl** | Implementação do repositório que realiza chamadas HTTP ao serviço atômico |
| **CamelContextWrapper** | Wrapper que encapsula o contexto do Apache Camel |
| **DashMonitoraBoletoConfiguration** | Classe de configuração Spring que define os beans da aplicação |
| **HttpUtil** | Utilitário para realizar requisições HTTP (GET e POST) |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Apache Camel 3.0.1** (orquestração e roteamento)
- **Spring Web** (REST APIs)
- **RestTemplate** (cliente HTTP)
- **Lombok** (redução de boilerplate)
- **Swagger/OpenAPI 2.9.2** (documentação de APIs)
- **Spring Actuator** (monitoramento e métricas)
- **Micrometer + Prometheus** (métricas)
- **Logback** (logging)
- **JUnit 5** (testes unitários)
- **Mockito** (mocks em testes)
- **Rest Assured** (testes funcionais)
- **Pact** (testes de contrato)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Grafana + Prometheus** (observabilidade)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | /v1/dash-monitora-boleto | DashMonitoraBoletoController | Retorna dados do dashboard de monitoramento de boletos |
| GET | /v1/dash-monitoramento/visao-geral/{id} | LancamentoController | Retorna lista de lançamentos da visão geral para a data atual |
| GET | /v1/dash-monitoramento/visao-geral-compare7/{id} | LancamentoController | Retorna lista de lançamentos da visão geral para comparação com 7 dias atrás |

---

## 5. Principais Regras de Negócio

- **Consulta de Lançamentos por Visão**: O sistema permite consultar lançamentos filtrados por ID de visão, retornando dados da data atual ou de 7 dias atrás para comparação.
- **Orquestração via Camel**: Todos os fluxos de negócio passam por rotas Apache Camel, permitindo processamento assíncrono e desacoplamento.
- **Integração com Serviço Atômico**: Os dados de lançamentos são obtidos de um serviço externo (dash-atomico) via REST.
- **Tratamento de Respostas Vazias**: Quando não há dados, o sistema retorna HTTP 204 (No Content).
- **Processamento de Datas**: O sistema calcula automaticamente a data de 7 dias atrás para comparações temporais.

---

## 6. Relação entre Entidades

**Entidades principais:**

- **DashMonitoraBoleto**: Entidade de domínio com atributos `id` (String) e `version` (Integer)
- **Lancamento**: Entidade de domínio representando um lançamento com atributos:
  - `quantidade` (Integer)
  - `valor` (Double)
  - `codOrigem` (Integer)
  - `numContaRemetente` (String)
  - `flLancamentoFintech` (String)
- **LancamentoRequest**: DTO de requisição contendo `idVisao` (String) e `localDate` (LocalDate)

**Relacionamentos:**
- Não há relacionamentos diretos entre as entidades. São objetos independentes utilizados em contextos diferentes.
- DashMonitoraBoleto é utilizado no fluxo de dashboard
- Lancamento e LancamentoRequest são utilizados no fluxo de consulta de lançamentos

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
| application.yml | leitura | Spring Boot (resources) | Arquivo de configuração da aplicação com propriedades, URLs e perfis |
| logback-spring.xml | leitura | Logback (resources) | Configuração de logging em formato JSON para console |
| swagger.yaml | leitura | Swagger/OpenAPI (resources) | Definição da documentação da API |

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
| **sboot-pgft-base-atom-dash-boleto** | REST API | Serviço atômico que fornece dados de lançamentos. Integração realizada via RestTemplate na classe `LancamentoRepositoryImpl`. URL configurável via propriedade `spring.bv.url.dash-atomico` (padrão: https://sboot-pgft-base-atom-dash-boleto.appdes.bvnet.bv/v1/dash-monitoramento) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões hexagonais (ports/adapters)
- Separação clara entre camadas (domain, application, infrastructure)
- Uso adequado de Apache Camel para orquestração
- Configuração externalizada e profiles para diferentes ambientes
- Presença de testes unitários, integração e funcionais
- Uso de Lombok para reduzir boilerplate
- Documentação via Swagger
- Observabilidade com Actuator, Prometheus e Grafana

**Pontos de Melhoria:**
- Implementação mock no `DashMonitoraBoletoRepositoryImpl` (retorna dados fixos)
- Classe `HttpUtil` com métodos estáticos e construtor privado que lança exceção (anti-pattern)
- Falta de tratamento de exceções específico nas chamadas HTTP
- Ausência de validações de entrada nos controllers
- Testes unitários vazios ou incompletos em algumas classes
- Falta de documentação inline (JavaDoc) em várias classes
- Uso de `@Deprecated` sem justificativa no construtor de `DashMonitoraBoletoRepresentation`
- Configuração de segurança presente mas não implementada efetivamente

---

## 14. Observações Relevantes

1. **Ambiente de Desenvolvimento**: O sistema está configurado para múltiplos ambientes (local, des, qa, uat, prd) com arquivos de configuração específicos.

2. **Containerização**: Dockerfile presente utilizando OpenJDK 11 com OpenJ9 em Alpine Linux, otimizado para baixo consumo de memória.

3. **CI/CD**: Configuração Jenkins presente (`jenkins.properties`) indicando pipeline automatizado.

4. **Infraestrutura como Código**: Arquivo `infra.yml` com configurações para deploy em Kubernetes/OpenShift.

5. **Monitoramento**: Stack completa de observabilidade com Prometheus e Grafana configurados via Docker Compose.

6. **Segurança**: Dependências de segurança BV presentes (JWT, LDAP) mas não efetivamente implementadas no código analisado.

7. **Arquitetura de Testes**: Estrutura bem organizada com separação de testes unitários, integração e funcionais em diretórios distintos.

8. **Padrão de Nomenclatura**: Segue convenções do Banco Votorantim com prefixos específicos (sboot-pgft-base).

9. **Versionamento**: Projeto na versão 1.0.0, indicando primeira release estável.

10. **Limitação Atual**: O endpoint de dashboard (`/v1/dash-monitora-boleto`) retorna dados mockados, não implementando integração real.