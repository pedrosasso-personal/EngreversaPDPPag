# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de **Portabilidade de Salário** desenvolvido em Spring Boot que gerencia o processo de transferência automática de salários entre instituições financeiras, conforme regulamentação do Banco Central. O sistema integra-se com a **CIP (Câmara Interbancária de Pagamentos)** via mensageria RabbitMQ para processar solicitações, confirmações e cancelamentos de portabilidade. Também gerencia o recebimento de TEDs de salário e fornece APIs REST para cadastro, consulta e monitoramento de portabilidades.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **PortabilidadeController** | Controlador REST - endpoints cadastro, consulta, cancelamento e monitoramento |
| **CadastroSolicitacaoServiceImpl** | Lógica de negócio para cadastro de novas solicitações de portabilidade |
| **CancelaSolicitacaoServiceImpl** | Processamento de cancelamentos (pendentes e não-pendentes) |
| **ConfirmacaoPortabilidadeServiceImpl** | Atualização de situações/motivos recebidos da CIP |
| **SolicitacaoPortabilidadeServiceImpl** | Processamento de aceites, recusas e cancelamentos diretos da CIP |
| **TedSalarioServiceImpl** | Consolidação e publicação de TEDs de salário recebidos |
| **MonitoramentoPortabilidadeServiceImpl** | Consultas analíticas e sintéticas para monitoramento |
| **PortabilidadeRepositoryImpl** | Acesso a dados (JDBI) - CRUD de portabilidades |
| **TedSalarioRepositoryImpl** | Persistência de TEDs de salário |
| **EnvioRepositoryImpl** | Publicação de mensagens RabbitMQ |
| **EnvioTopicoRepositoryImpl** | Publicação de mensagens Google PubSub |
| **ConfirmacaoPortabilidadeListener** | Consumidor de eventos de situação e cancelamento |
| **SolicitacaoPortabilidadeListener** | Consumidor de retornos de solicitações CIP |
| **TedSalarioListener** | Consumidor de TEDs de salário |
| **PortabilidadeApplicationMapper** | Conversão Domain ↔ Representation (REST) |
| **PortabilidadeDomainMapper** | Conversão VO → Entity |
| **FilaPortabilidadeMapper** | Conversão VO → Mensagens RabbitMQ |
| **DateUtils** | Utilitários de cálculo de dias úteis e validações de período |
| **PortabilidadeUtils** | Validações de status e filtros de portabilidades |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.x** (framework base)
- **JDBI 3** (acesso a dados type-safe)
- **MySQL** (banco de dados SPAGPortabilidadeSalario)
- **RabbitMQ** (mensageria para integração CIP)
- **Google Cloud Pub/Sub** (notificações push)
- **Lombok** (redução de boilerplate)
- **Spring Cloud Stream** (abstração mensageria)
- **OAuth2/JWT** (autenticação/autorização)
- **Micrometer/Prometheus** (métricas)
- **Grafana** (dashboards)
- **Docker/Kubernetes** (containerização/orquestração)
- **JUnit 5 + Mockito** (testes unitários)
- **Pact** (testes de contrato)
- **JaCoCo** (cobertura de testes)
- **OWASP ESAPI 2.5.3.1** (segurança)
- **Feature Toggle** (flags de funcionalidades)
- **Logback** (logs estruturados JSON)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/banco-digital/portabilidade` | PortabilidadeController | Cadastro de nova solicitação de portabilidade |
| GET | `/v1/banco-digital/portabilidade` | PortabilidadeController | Consulta status de portabilidade por CPF/CNPJ empregador e banco folha |
| POST | `/v1/banco-digital/portabilidade/cancelar` | PortabilidadeController | Cancelamento de portabilidade pendente |
| GET | `/v1/banco-digital/portabilidade/consultaClienteTedSalario` | PortabilidadeController | Consulta TEDs de salário recebidos |
| GET | `/v1/banco-digital/monitoramento/analitico` | PortabilidadeController | Relatório analítico de portabilidades (filtros data/status) |
| GET | `/v1/banco-digital/monitoramento/sintetico` | PortabilidadeController | Relatório sintético agregado por situação |
| GET | `/v1/banco-digital/portabilidade/pesquisa-situacao` | PortabilidadeController | Pesquisa portabilidades por situação |
| GET | `/v1/banco-digital/cancelamento/motivos` | PortabilidadeController | Lista motivos de cancelamento |
| POST | `/v1/banco-digital/cancelamento/motivos` | PortabilidadeController | Cadastra novo motivo de cancelamento |
| GET | `/v1/banco-digital/portabilidades` | PortabilidadeController | Lista todas portabilidades com filtros |

---

## 5. Principais Regras de Negócio

1. **Validação de Duplicidade**: Não permite cadastrar portabilidade duplicada para mesmo empregador/banco folha
2. **Geração de NSU**: Gera Número Sequencial Único (UUID 20 caracteres) para cada solicitação
3. **Mock CIP**: Em ambientes não-produtivos, simula resposta da CIP (feature toggle `useMock`)
4. **Status Permitidos para Cancelamento**: Apenas portabilidades com status PENDENTE (1) podem ser canceladas pelo cliente
5. **Fluxo de Cancelamento Versionado**: Feature toggle controla fluxo v1 (legado) vs v2 (novo) de cancelamento
6. **Validação NuUnicoCip**: Cancelamento não-pendente exige NuUnicoCip preenchido
7. **Atualização de Status Finais**: Status 2 (aprovada), 3 (reprovada), 4 (cancelada), 6 (compulsório), 14 (erro) setam data de conclusão
8. **Mapeamento de Erros CIP**: Códigos de erro CIP (EPCS0017, EPCS0012, etc) são mapeados para motivos internos
9. **Cancelamento Recusado**: Se CIP recusa cancelamento, portabilidade volta para status PENDENTE
10. **Validação NSU TED Único**: Não permite duplicar TED com mesmo NSU
11. **Push Transacional**: Publica alterações de status em tópico PubSub para notificações
12. **Regra 30 Dias**: Consultas excluem portabilidades canceladas/erro com mais de 30 dias
13. **Validação de Período**: Monitoramento analítico valida período máximo de 30 dias entre datas
14. **Cálculo Dias Úteis**: Calcula dias úteis decorridos desde solicitação até conclusão
15. **Validação Conta/Cliente**: Valida duplicidade de conta e cliente antes de cadastrar

---

## 6. Relação entre Entidades

**Entidade Principal: Portabilidade**
- Relaciona-se com **ClientePortabilidade** (1:N) - um cliente pode ter múltiplas portabilidades
- Relaciona-se com **ContaClientePortabilidade** (1:N) - uma portabilidade pode ter múltiplas contas
- Referencia **Banco** (N:1) - banco folha e banco destino
- Referencia **StatusPortabilidadeSalario** (N:1) - situação atual da portabilidade
- Referencia **MotivoPortabilidadeSalario** (N:1) - motivo de recusa/cancelamento
- Relaciona-se com **Empregador** (N:1) - empresa pagadora do salário

**Entidade ClienteTEDPortabilidade**
- Armazena TEDs de salário recebidos
- Relaciona-se com **Cliente** via cdPessoaGlobal

**Entidade CancelamentoPortabilidade**
- Relaciona-se com **MotivoCnclmntPortabilidade** (N:1)
- Vincula-se a **Portabilidade** via nuSequencialUnico

**Fluxo de Estados:**
```
PENDENTE (1) → APROVADA (2) / REPROVADA (3) / CANCELADA (4) / ERRO (14)
PENDENTE (1) → EM_CANCELAMENTO (13) → CANCELADA (4)
```

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbPortabilidade | Tabela | SELECT | Consulta portabilidades por filtros (empregador, banco, status, datas) |
| TbClientePortabilidade | Tabela | SELECT | Consulta dados do cliente vinculado à portabilidade |
| TbContaClientePortabilidade | Tabela | SELECT | Consulta contas do cliente na portabilidade |
| TbBanco | Tabela | SELECT | Consulta dados de bancos (folha/destino) por código Bacen/ISPB |
| TbStatusPortabilidadeSalario | Tabela | SELECT | Consulta mapeamento de status CIP para status interno |
| TbMotivoPortabilidadeSalario | Tabela | SELECT | Consulta motivos de recusa/cancelamento |
| TbClienteTEDPortabilidade | Tabela | SELECT | Consulta TEDs de salário por NSU, datas, Bacen |
| TbMotivoCnclmntPortabilidade | Tabela | SELECT | Consulta motivos de cancelamento cadastrados |
| TbCancelamentoPortabilidade | Tabela | SELECT | Consulta histórico de cancelamentos |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbPortabilidade | Tabela | INSERT/UPDATE | Cadastra novas portabilidades e atualiza status/motivo/datas |
| TbClientePortabilidade | Tabela | INSERT | Cadastra cliente vinculado à portabilidade |
| TbContaClientePortabilidade | Tabela | INSERT | Cadastra contas do cliente na portabilidade |
| TbClienteTEDPortabilidade | Tabela | INSERT | Registra TEDs de salário recebidos |
| TbCancelamentoPortabilidade | Tabela | INSERT | Registra solicitações de cancelamento |
| TbMotivoCnclmntPortabilidade | Tabela | INSERT | Cadastra novos motivos de cancelamento |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | Leitura | Configuração Logback | Configuração de logs estruturados JSON por ambiente |
| application.yml | Leitura | Spring Boot | Configurações da aplicação (BD, RabbitMQ, PubSub) |
| rabbitmq_definitions.json | Leitura | RabbitMQ | Definições de exchanges, filas e bindings |
| prometheus.yml | Leitura | Prometheus | Configuração de scraping de métricas |
| grafana.ini | Leitura | Grafana | Configuração do Grafana (usuários, dashboards) |
| default.json | Leitura | Grafana | Dashboard de métricas Spring Boot |

---

## 10. Filas Lidas

| Nome da Fila | Tecnologia | Classe Consumidora | Descrição |
|--------------|------------|-------------------|-----------|
| queuePortabilidade | RabbitMQ | SolicitacaoPortabilidadeListener | Retornos de solicitações enviadas à CIP (aceite/recusa) |
| queueSituacao | RabbitMQ | ConfirmacaoPortabilidadeListener | Atualizações de situação de portabilidades |
| queueSituacaoCancelamento | RabbitMQ | ConfirmacaoPortabilidadeListener | Confirmações de cancelamento |
| queueCancelamentoDireto | RabbitMQ | SolicitacaoPortabilidadeListener | Cancelamentos diretos processados pela CIP |
| queueTransbordo | RabbitMQ | SolicitacaoPortabilidadeListener | Transbordos de portabilidades por NSU CIP |
| queueTedSalario | RabbitMQ | TedSalarioListener | TEDs de salário recebidos |

---

## 11. Filas Geradas

| Nome da Fila/Exchange | Tecnologia | Classe Produtora | Descrição |
|-----------------------|------------|------------------|-----------|
| exchange portabilidade | RabbitMQ | EnvioRepositoryImpl | Exchange para envio de solicitações à CIP |
| queueCancelamento | RabbitMQ | EnvioRepositoryImpl | Fila de cancelamentos a serem processados pela CIP |
| queuePortabilidadePendenteParaCancelar | RabbitMQ | EnvioRepositoryImpl | Fila de portabilidades pendentes para cancelamento |
| business-spag-base-pushes-portabilidade (TedSalario) | Google PubSub | EnvioTopicoRepositoryImpl | Tópico de notificações de TEDs de salário |
| business-spag-base-pushes-portabilidade-status | Google PubSub | EnvioTopicoRepositoryImpl | Tópico de notificações de alteração de status |

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Protocolo/Tecnologia | Descrição |
|-----------------|------|---------------------|-----------|
| **CIP (Câmara Interbancária de Pagamentos)** | Sistema Externo | RabbitMQ | Envio de solicitações de portabilidade e recebimento de confirmações/cancelamentos. Routing keys: SPAG.solicitacaoPortablidade, SPAG.retornoSolicitacaoPortabilidade, SPAG.confirmacaoPortablidade, SPAG.cancelamentoPortabilidade |
| **Google Cloud Pub/Sub** | Serviço de Mensageria | gRPC/HTTP | Publicação de notificações push para clientes (TEDs e alterações de status) |
| **MySQL SPAGPortabilidadeSalario** | Banco de Dados | JDBC/JDBI | Persistência de dados de portabilidades, clientes, contas e TEDs |
| **Prometheus** | Monitoramento | HTTP (scraping) | Coleta de métricas da aplicação via /actuator/prometheus |
| **Grafana** | Visualização | HTTP | Dashboards de monitoramento de métricas e logs |
| **Feature Toggle Service** | Serviço de Configuração | HTTP/REST | Controle de flags de funcionalidades (ex: fluxo novo cancelamento, mock CIP) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- **Arquitetura bem estruturada**: Separação clara de camadas (domain, application, infrastructure) seguindo princípios de Clean Architecture
- **Uso de tecnologias modernas**: JDBI3 para SQL type-safe, Lombok para redução de boilerplate, Spring Boot best practices
- **Testabilidade**: Boa cobertura de testes unitários com mocks (JUnit 5 + Mockito), testes de contrato (Pact)
- **Observabilidade**: Integração com Prometheus/Grafana, logs estruturados JSON, métricas detalhadas
- **Feature Toggles**: Permite ativação/desativação de funcionalidades sem deploy
- **Segurança**: Uso de OAuth2/JWT, OWASP ESAPI
- **Documentação técnica**: Código bem comentado, uso de Optional e Streams

**Pontos de Melhoria:**
- **Exception Handling**: Tratamento de exceções poderia ser mais específico e granular, com hierarquia de exceções customizadas mais rica
- **Logs**: Alguns logs muito verbosos, falta padronização de níveis (INFO vs DEBUG)
- **Mappers repetitivos**: Muita conversão manual entre VOs/DTOs/Entities, poderia usar MapStruct
- **Validações**: Algumas validações espalhadas em múltiplas camadas, poderia centralizar com Bean Validation
- **Documentação API**: Falta Swagger/OpenAPI para documentação automática dos endpoints
- **Testes de integração**: Poderiam ser mais abrangentes, testando fluxos completos end-to-end

---

## 14. Observações Relevantes

1. **Conformidade Regulatória**: Sistema implementa Resolução do Banco Central sobre portabilidade de salário, com mapeamento de status e motivos conforme especificação CIP

2. **Status da Portabilidade**:
   - 1 = PENDENTE (aguardando processamento CIP)
   - 2 = APROVADA (portabilidade efetivada)
   - 3 = REPROVADA (recusada pela CIP)
   - 4 = CANCELADA (cancelada pelo cliente ou CIP)
   - 6 = COMPULSÓRIO (portabilidade compulsória)
   - 13 = EM_CANCELAMENTO (cancelamento em processamento)
   - 14 = ERRO (erro no processamento)

3. **NSU (Número Sequencial Único)**: Gerado localmente como UUID de 20 caracteres, usado para rastreabilidade de solicitações

4. **Mock CIP**: Feature toggle `useMock` ativa simulação de respostas CIP em ambientes não-produtivos (des, qa, uat), facilitando testes

5. **Regra de Limpeza**: Portabilidades canceladas ou com erro há mais de 30 dias são excluídas das consultas de status

6. **Versionamento de Fluxos**: Feature toggle `fluxoNovoCancelamento` permite migração gradual entre versões de cancelamento (v1 legado → v2 novo)

7. **Infraestrutura**: 
   - Kubernetes com probes de health (liveness/readiness)
   - Resources: CPU 30m-200m, memória 256Mi-512Mi
   - Service Account: ksa-spag-base-16256
   - Secrets gerenciados por ambiente (BD_PASS, RABBIT_SPAG_PASSWORD, FT_KEY)

8. **Ambientes**: Configurações específicas para des, local, prd, qa, uat com URLs de BD e RabbitMQ distintas

9. **Monitoramento**: Dashboard Grafana com métricas de uptime, heap, CPU, threads, GC, HikariCP, HTTP requests, logs

10. **Mensageria RabbitMQ**: Exchange `events.business.portabilidade` com routing keys prefixadas `SPAG.*` para segregação de mensagens

11. **Auditoria**: Logs estruturados JSON com informações de audit trail para rastreabilidade de operações

12. **Performance**: Uso de HikariCP para pool de conexões, métricas de latência de requisições HTTP

---

**Documento gerado em:** 2024  
**Versão do Sistema:** 0.32.0  
**Tecnologia Base:** Spring Boot 2.x + JDBI 3 + RabbitMQ + Google Pub/Sub