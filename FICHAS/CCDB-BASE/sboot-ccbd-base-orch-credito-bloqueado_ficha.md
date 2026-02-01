# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-ccbd-base-orch-credito-bloqueado** é um serviço orquestrador stateless desenvolvido em Spring Boot com Apache Camel, responsável por gerenciar o processo de bloqueio de créditos que entram em contas correntes. 

O sistema atua como um orquestrador que:
- Recebe eventos de crédito efetivado via Google Cloud Pub/Sub
- Consulta monitoramentos de bloqueio pendentes para a conta
- Solicita bloqueios de saldo conforme necessário
- Atualiza o status dos monitoramentos
- Cancela bloqueios quando solicitado

O fluxo principal envolve a integração com serviços atômicos de conta corrente e bloqueios de saldo, utilizando mensageria assíncrona (Pub/Sub) e chamadas REST síncronas.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal Spring Boot que inicializa a aplicação |
| **CriaBloqueioRoute** | Rota Camel que orquestra o processo de criação de bloqueios |
| **CancelaBloqueioRoute** | Rota Camel para cancelamento de bloqueios |
| **AtualizaMonitoramentoRoute** | Rota Camel para atualização de monitoramentos |
| **CriaBloqueioListener** | Listener que consome mensagens de criação de bloqueio do Pub/Sub |
| **CancelaBloqueioListener** | Listener que consome mensagens de cancelamento de bloqueio do Pub/Sub |
| **InsereNovoBloqueioRepositoryImpl** | Implementação que solicita débito/bloqueio via API REST |
| **ConsultaMonitoramentosPendentesRepositoryImpl** | Consulta monitoramentos pendentes via API REST |
| **AtualizaMonitoramentoRepositoryImpl** | Publica mensagens de atualização no Pub/Sub |
| **CancelaBloqueioRepositoryImpl** | Cancela bloqueios via API REST |
| **SolicitaNovoBloqueioProcessor** | Processor Camel que prepara solicitação de novo bloqueio |
| **OrdenaPrioridadeEFiltraMonitoramentoProcessor** | Ordena monitoramentos por prioridade (NSU) |
| **AtualizaValorDisponivelProcessor** | Atualiza valor disponível após cada bloqueio |
| **MonitoramentoPendenteMapper** | Mapper MapStruct para conversão de representações |
| **AtualizaMonitoramentoComNovoBloqueioMapper** | Mapper para atualização com novo bloqueio |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 3.3.5** - Framework base da aplicação
- **Apache Camel 4.7.0** - Framework de integração e orquestração
- **Google Cloud Pub/Sub** (spring-cloud-gcp 3.9.14) - Mensageria assíncrona
- **Spring Integration** - Integração com Pub/Sub
- **MapStruct** - Mapeamento de objetos
- **Apache Avro 1.12.0** - Serialização de mensagens
- **Micrometer + Prometheus** - Métricas e monitoramento
- **Spring Actuator** - Health checks e endpoints de gerenciamento
- **Lombok** - Redução de boilerplate
- **Jackson** - Serialização JSON
- **Maven** - Gerenciamento de dependências
- **JUnit 5** - Testes unitários
- **Docker** - Containerização
- **OpenAPI/Swagger** - Documentação de APIs
- **Logback** - Logging em formato JSON

---

## 4. Principais Endpoints REST

**Não se aplica** - Este serviço é um orquestrador orientado a eventos (event-driven) que consome mensagens do Pub/Sub. Não expõe endpoints REST públicos para processamento de negócio, apenas endpoints de gerenciamento (Actuator).

Endpoints de gerenciamento:
- `GET /actuator/health` (porta 9090) - Health check
- `GET /actuator/metrics` (porta 9090) - Métricas
- `GET /actuator/prometheus` (porta 9090) - Métricas formato Prometheus

---

## 5. Principais Regras de Negócio

1. **Priorização por NSU**: Monitoramentos com NSU (Número Sequencial Único) correspondente ao crédito recebido têm prioridade no processamento
2. **Bloqueio Proporcional**: O valor bloqueado é o menor entre o valor solicitado no monitoramento e o valor disponível do crédito
3. **Processamento Sequencial**: Monitoramentos são processados um a um, atualizando o valor disponível após cada bloqueio
4. **Tratamento de Falhas**: 
   - Falhas terminais (ex: conta não encontrada) descartam a mensagem e notificam erro
   - Falhas transitórias (ex: timeout) reprocessam a mensagem
5. **Monitoramento Ativo**: Apenas monitoramentos com flag ativo = 'S' são processados
6. **Conversão de Códigos de Banco**: Códigos externos são convertidos para códigos internos (ex: 655→161, 436→413)
7. **Bloqueio Condicional**: Bloqueios só são criados se houver valor disponível > 0
8. **Atualização Assíncrona**: Após criar bloqueio, publica mensagem de atualização no Pub/Sub

---

## 6. Relação entre Entidades

**Entidades principais:**

- **CriaBloqueio** (Avro): Mensagem de entrada com dados para criar bloqueio
  - Contém: ContaId, cdMonitoramento, cdMotivoBloqueio, nuProtocolo, vrBloqueio

- **BloqueioId** (Avro): Identificador único de bloqueio
  - Contém: ContaId, cdBloqueio

- **ContaId** (Avro): Identificador de conta
  - Contém: cdBanco, cdTipoConta, nuConta

- **AtualizaMonitoramento** (Avro): Mensagem de atualização de monitoramento
  - Contém: cdMonitoramento, BloqueioId, vrBloqueio, ErroId (opcional)

- **MonitoramentoPendente** (Domain): Representa um monitoramento pendente de bloqueio
  - Contém: id, ativo, valorSolicitado, valorBloqueado, conta, motivoBloqueio, numeroProtocolo, NSU

- **SolicitacaoNovoBloqueio** (Domain): Solicitação de novo bloqueio
  - Contém: IdConta, valorOperacao, motivoBloqueio, numeroProtocolo

**Relacionamentos:**
- CriaBloqueio → ContaId (1:1)
- BloqueioId → ContaId (1:1)
- AtualizaMonitoramento → BloqueioId (1:1)
- MonitoramentoPendente → IdConta (1:1)
- SolicitacaoNovoBloqueio → IdConta (1:1)

---

## 7. Estruturas de Banco de Dados Lidas

**Não se aplica** - O sistema não acessa diretamente banco de dados. Todas as consultas são realizadas via APIs REST de serviços atômicos.

---

## 8. Estruturas de Banco de Dados Atualizadas

**Não se aplica** - O sistema não atualiza diretamente banco de dados. Todas as atualizações são realizadas via APIs REST de serviços atômicos ou mensagens Pub/Sub.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | Leitura | /usr/etc/log/ (runtime) | Configuração de logging em JSON |
| application.yml | Leitura | src/main/resources | Configurações da aplicação |
| *.avsc (Avro schemas) | Leitura | src/main/resources/avro | Schemas Avro para serialização de mensagens |
| openapi.yaml | Leitura | src/main/resources/swagger | Especificação OpenAPI das APIs consumidas |

---

## 10. Filas Lidas

O sistema consome mensagens das seguintes subscriptions do Google Cloud Pub/Sub:

1. **business-ccbd-base-cria-bloqueio-sub**
   - Tópico: Criação de bloqueios
   - Mensagem: CriaBloqueio (Avro)
   - Listener: CriaBloqueioListener
   - AckMode: AUTO

2. **business-ccbd-base-cancela-bloqueio-sub**
   - Tópico: Cancelamento de bloqueios
   - Mensagem: BloqueioId (Avro)
   - Listener: CancelaBloqueioListener
   - AckMode: MANUAL

---

## 11. Filas Geradas

O sistema publica mensagens no seguinte tópico do Google Cloud Pub/Sub:

1. **business-ccbd-base-monitoramento-saldo**
   - Mensagem: AtualizaMonitoramento (Avro)
   - Propósito: Notificar atualização de monitoramento após criação de bloqueio
   - Gateway: PubSubAtualizaMonitoramentoOutboundGateway

---

## 12. Integrações Externas

| Sistema/API | Tipo | Descrição |
|-------------|------|-----------|
| **sboot-ccbd-base-atom-conta-corrente** | REST (POST) | Solicita débito/bloqueio de saldo em conta corrente (endpoint: /v1/banco-digital/contas/debito) |
| **sboot-ccbd-base-atom-conta-corrente** | REST (POST) | Cancela bloqueio de saldo (endpoint: /v1/banco-digital/contas/bloqueio/cancelar) |
| **sboot-ccbd-base-atom-bloqueios-saldo** | REST (GET) | Consulta monitoramentos pendentes (endpoint: /v1/contas/monitoramentos/pendentes) |
| **sboot-ccbd-base-atom-bloqueios-saldo** | REST (PUT) | Inclui novo bloqueio em monitoramento (endpoint: /v1/contas/monitoramentos/{id}/bloqueios) |
| **Google Cloud Pub/Sub** | Mensageria | Consumo e publicação de mensagens assíncronas |
| **API Gateway OAuth** | Autenticação | Obtenção de tokens JWT para autenticação nas APIs (tokenUrl configurável por ambiente) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões de microserviços e separação de responsabilidades (domain, infrastructure, presentation)
- Uso adequado de Apache Camel para orquestração de fluxos complexos
- Implementação de tratamento de erros diferenciado (falhas terminais vs transitórias)
- Uso de MapStruct para mapeamento de objetos, reduzindo código boilerplate
- Configuração adequada de profiles para diferentes ambientes
- Uso de Avro para serialização eficiente de mensagens
- Implementação de MDC para rastreabilidade (ticket)
- Testes unitários presentes (embora não enviados para análise)
- Documentação OpenAPI das APIs consumidas
- Configuração de métricas e health checks

**Pontos de Melhoria:**
- Algumas classes com responsabilidades que poderiam ser melhor segregadas (ex: InsereNovoBloqueioRepositoryImpl com lógica de montagem de request)
- Falta de documentação inline em alguns métodos complexos
- Uso de strings literais em alguns pontos onde constantes seriam mais apropriadas
- Tratamento de exceções poderia ser mais granular em alguns pontos
- Falta de validação de entrada em alguns processors Camel
- Configuração de timeouts e retry policies poderia ser mais explícita

O código demonstra maturidade técnica e boas práticas, mas há espaço para melhorias em documentação e refinamento de alguns aspectos de design.

---

## 14. Observações Relevantes

1. **Ambiente Multi-Cloud**: Sistema preparado para rodar em Google Cloud Platform (GKE) com suporte a Pub/Sub nativo

2. **Service Account**: Utiliza service account específica (ksa-ccbd-base-23534) para acesso aos recursos GCP

3. **Segurança**: Implementa autenticação OAuth2 com JWT para comunicação entre serviços

4. **Observabilidade**: 
   - Logs estruturados em JSON
   - Métricas expostas em formato Prometheus
   - Health checks configurados com liveness e readiness probes

5. **Configuração por Ambiente**: Suporta múltiplos ambientes (des, uat, prd) com configurações específicas via ConfigMaps e Secrets

6. **Containerização**: Dockerfile otimizado com imagem base corporativa e configurações de JVM

7. **Pipeline CI/CD**: Integrado com Jenkins (jenkins.properties) e ferramentas corporativas (bvcli)

8. **Monitoramento**: Dashboard Grafana pré-configurado para visualização de métricas

9. **Resiliência**: Implementa padrões de retry e circuit breaker através do tratamento de exceções customizado

10. **Versionamento de Mensagens**: Uso de Avro permite evolução de schemas com compatibilidade

11. **Auditoria**: Integração com framework de trilha de auditoria corporativo (arqt-base-trilha-auditoria)