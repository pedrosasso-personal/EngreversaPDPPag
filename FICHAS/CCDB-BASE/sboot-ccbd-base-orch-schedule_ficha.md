# Ficha Técnica do Sistema

## 1. Descrição Geral
O **sboot-ccbd-base-orch-schedule** é um microsserviço orquestrador responsável pelo agendamento e execução de processos bancários relacionados à consolidação de movimentações Fintech. O sistema utiliza Spring Boot com agendamento automático (via `@Scheduled`) e também expõe um endpoint REST para execução manual do processamento. Ele integra-se com o serviço atômico de conta corrente para solicitar o processamento de movimentações Fintech.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal que inicializa a aplicação Spring Boot |
| `ScheduleController` | Controller REST que expõe endpoint para execução manual do processamento Fintech |
| `ScheduledContaCorrente` | Componente que executa o agendamento automático do processamento Fintech |
| `ProcessamentoFintechService` | Interface de serviço para processamento Fintech |
| `ProcessamentoFintechServiceImpl` | Implementação do serviço que utiliza Apache Camel para orquestração |
| `ProcessamentoFintechRepository` | Interface de repositório para comunicação com serviços externos |
| `ProcessamentoFintechRepositoryImpl` | Implementação do repositório que chama a API de conta corrente |
| `ProcessamentoFintechRouter` | Rota Apache Camel que define o fluxo de processamento |
| `CamelContextWrapper` | Wrapper para gerenciar o contexto do Apache Camel |
| `ScheduleConfiguration` | Classe de configuração dos beans do Spring |
| `ApplicationConfiguration` | Configuração do cliente REST para integração externa |
| `AppProperties` | Propriedades de configuração da aplicação |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.x** (framework principal)
- **Spring Web** (REST APIs)
- **Spring Security OAuth2** (autenticação JWT)
- **Apache Camel 3.0.1** (orquestração de processos)
- **Springfox/Swagger 3.0.0** (documentação de API)
- **Micrometer + Prometheus** (métricas e monitoramento)
- **Logback** (logging)
- **Lombok** (redução de boilerplate)
- **RestTemplate** (cliente HTTP)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **JUnit 5 + Mockito** (testes unitários)
- **Rest Assured** (testes funcionais)
- **Pact** (testes de contrato)
- **Java 11**

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/executar/fintech` | `ScheduleController` | Executa manualmente o processamento de movimentações Fintech |
| GET | `/actuator/health` | Spring Actuator | Verifica o status de saúde da aplicação |
| GET | `/actuator/prometheus` | Spring Actuator | Expõe métricas no formato Prometheus |
| GET | `/swagger-ui.html` | Springfox | Interface de documentação Swagger |

---

## 5. Principais Regras de Negócio

1. **Agendamento Automático**: O sistema executa automaticamente o processamento Fintech em intervalos configuráveis (definido pela propriedade `bv.time`)
2. **Execução Manual**: Permite execução sob demanda através do endpoint REST
3. **Integração com Conta Corrente**: Solicita o processamento de movimentações Fintech ao serviço atômico de conta corrente
4. **Autenticação OAuth2**: Obtém token de acesso via Gateway OAuth antes de realizar chamadas externas
5. **Tratamento de Erros**: Captura exceções HTTP e lança `ProcessamentoFintechException` em caso de falha
6. **Orquestração via Camel**: Utiliza rotas Apache Camel para gerenciar o fluxo de processamento

---

## 6. Relação entre Entidades

O sistema possui uma estrutura de domínio simples:

- **Schedule**: Entidade de domínio básica com `id` e `version` (aparentemente não utilizada ativamente no fluxo principal)

**Fluxo de Processamento**:
```
ScheduleController/ScheduledContaCorrente 
    → ProcessamentoFintechService 
    → CamelContextWrapper (ProducerTemplate) 
    → ProcessamentoFintechRouter 
    → ProcessamentoFintechRepository 
    → ConsolidaApi (cliente REST)
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
| `application.yml` | Leitura | Spring Boot | Arquivo de configuração da aplicação com profiles (local, des, qa, uat, prd) |
| `logback-spring.xml` | Leitura | Logback | Configuração de logging da aplicação |
| `sboot-ccbd-base-orch-schedule.yaml` | Leitura | Swagger Codegen | Especificação OpenAPI do serviço provider |
| `sboot-ccbd-base-atom-conta-corrente.yaml` | Leitura | Swagger Codegen | Especificação OpenAPI do serviço cliente (conta corrente) |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|----------------|------|-----------|
| **sboot-ccbd-base-atom-conta-corrente** | API REST | Serviço atômico de conta corrente. Endpoint: `/v1/banco-digital/processo/fintech` (POST). Responsável por processar movimentações Fintech |
| **API Gateway OAuth** | API REST | Serviço de autenticação para obtenção de tokens JWT. URLs variam por ambiente (des, uat, prd) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (application, domain, common)
- Uso adequado de interfaces para abstrair implementações
- Configuração externalizada em arquivos YAML
- Testes unitários, de integração e funcionais estruturados
- Uso de Lombok para reduzir boilerplate
- Documentação via Swagger/OpenAPI
- Monitoramento com Prometheus e Grafana configurado
- Uso de Apache Camel para orquestração

**Pontos de Melhoria:**
- Classe `Schedule` no domínio parece não ser utilizada
- Tratamento de exceções genérico (poderia ser mais específico)
- Falta de validações de entrada nos endpoints
- Ausência de logs estruturados em alguns pontos críticos
- Testes com baixa cobertura (classes de teste vazias ou com pouca implementação)
- Configuração de segurança poderia ser mais robusta
- Falta de circuit breaker ou retry para chamadas externas
- Documentação inline (JavaDoc) ausente em várias classes

---

## 14. Observações Relevantes

1. **Agendamento Configurável**: O intervalo de execução do agendamento é configurado via propriedade `bv.time` (ex: PT30S para 30 segundos)

2. **Múltiplos Ambientes**: O sistema possui configurações específicas para ambientes local, des, qa, uat e prd

3. **Segurança**: Utiliza OAuth2 Resource Server com validação de tokens JWT

4. **Monitoramento**: Infraestrutura completa de observabilidade com Prometheus e Grafana pré-configurada

5. **Containerização**: Dockerfile otimizado usando OpenJ9 JVM com configurações de memória ajustáveis

6. **CI/CD**: Integração com Jenkins configurada via `jenkins.properties`

7. **Arquitetura**: Segue padrões de microserviços do Banco Votorantim com scaffolding padronizado

8. **Dependências**: Utiliza bibliotecas corporativas do Banco Votorantim (arqt-base)

9. **Testes de Contrato**: Suporte para testes Pact configurado

10. **Health Check**: Endpoints de health check expostos na porta 9090 (management port separada)