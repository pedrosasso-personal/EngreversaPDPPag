# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de Portabilidade de Crédito para Open Finance Brasil (OFB), desenvolvido pelo Banco Votorantim. Permite que clientes transfiram operações de crédito e arrendamento mercantil entre instituições financeiras em busca de melhores condições. O sistema atua como instituição credora, gerenciando o ciclo completo de solicitações de portabilidade, desde o recebimento até a conclusão ou cancelamento, incluindo validações de elegibilidade, gestão de contrapropostas, liquidação e integração com sistemas externos via mensageria (Google Pub/Sub).

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal de inicialização da aplicação Spring Boot |
| **PortabilityConfiguration** | Configuração central de beans, repositórios e serviços |
| **PortabilityService** | Serviço principal contendo regras de negócio de portabilidade |
| **ManagementService** | Gerenciamento de status e jobs agendados |
| **PortabilityEventService** | Conversão e envio de eventos para tópicos Pub/Sub |
| **JdbiPortabilityRepository** | Interface de acesso a dados de portabilidade (JDBI) |
| **JdbiManagementRepository** | Interface de acesso a dados de gestão de status |
| **CreditPortabilityController** | Controlador REST para operações de portabilidade |
| **ConcurrencyManagementController** | Controlador para verificação de elegibilidade |
| **PaymentsController** | Controlador para notificações de pagamento |
| **RejectedPortabilityConsumer** | Consumidor de mensagens de retenção/cancelamento |
| **BusinessDayCalculator** | Cálculo de dias úteis considerando feriados |
| **PortabilityMapper** | Mapeamento entre DTOs e entidades de domínio |
| **RestResponseExceptionHandler** | Tratamento centralizado de exceções REST |

---

## 3. Tecnologias Utilizadas

- **Java 21** (OpenJDK)
- **Spring Boot 3.x** (framework principal)
- **Spring Security** (OAuth2 Resource Server com JWT)
- **Spring Cloud GCP** (integração com Google Cloud Platform)
- **Google Cloud Pub/Sub** (mensageria assíncrona)
- **JDBI 3.27.0** (acesso a dados SQL)
- **MySQL 8.2.0** (banco de dados relacional)
- **Maven 3.8+** (gerenciamento de dependências)
- **Docker** (containerização)
- **OpenAPI 3.0** (especificação de API)
- **Lombok** (redução de boilerplate)
- **OWASP ESAPI 2.7.0.0** (segurança e logging)
- **Jackson 2.17.3** (serialização JSON)
- **Micrometer/Prometheus** (métricas e observabilidade)
- **OpenTelemetry** (telemetria distribuída)
- **Logback** (logging estruturado)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/portabilities` | CreditPortabilityController | Cria nova solicitação de portabilidade |
| GET | `/v1/portabilities/{portabilityId}` | CreditPortabilityController | Consulta portabilidade por ID |
| PATCH | `/v1/portabilities/{portabilityId}/cancel` | CreditPortabilityController | Cancela portabilidade |
| POST | `/v1/portabilities/{portabilityId}/payment` | PaymentsController | Notifica pagamento/liquidação |
| GET | `/v1/credit-operations/{contractId}/portability-eligibility` | ConcurrencyManagementController | Verifica elegibilidade do contrato |
| GET | `/v1/portabilities/{portabilityId}/summary` | InternalController | Busca dados simplificados da portabilidade |
| POST | `/v1/portabilities/{portabilityId}/finish` | InternalController | Notifica conclusão da portabilidade |
| POST | `/v1/portabilities/{portabilityId}/payment-issue` | InternalController | Notifica problema no pagamento |
| GET | `/v1/portabilities/status/{portabilityId}` | ManagementController | Lista status disponíveis |
| PUT | `/v1/portabilities/{portabilityId}/status` | ManagementController | Atualiza status de portabilidade |
| PUT | `/v1/status/{statusId}` | ManagementController | Atualiza definição de status |
| PUT | `/v1/job/atualiza-status` | SchedulerController | Job para atualização automática de status |

---

## 5. Principais Regras de Negócio

1. **Máquina de Estados**: Portabilidade segue fluxo sequencial (RECEIVED → PENDING → ACCEPTED_SETTLEMENT_IN_PROGRESS → ACCEPTED_SETTLEMENT_COMPLETED → PORTABILITY_COMPLETED), com estados alternativos (REJECTED, CANCELLED, PAYMENT_ISSUE)

2. **Cálculo de Prazos**: Utiliza dias úteis considerando feriados nacionais e configuráveis via Feature Toggle, com prazos específicos por estado (ex: 3 dias úteis para PENDING)

3. **Validação de Elegibilidade**: Verifica se contrato já possui portabilidade em andamento (OFB ou Registradora) antes de aceitar nova solicitação

4. **Cancelamento Condicional**: Permite cancelamento apenas nos estados RECEIVED, PENDING ou ACCEPTED_SETTLEMENT_IN_PROGRESS

5. **Notificação de Pagamento**: Aceita notificações apenas nos estados ACCEPTED_SETTLEMENT_IN_PROGRESS ou PAYMENT_ISSUE

6. **Divergência de Valores**: Rejeita liquidações com divergência superior a 15% do valor original

7. **Retenção de Cliente**: Processa eventos de retenção via Pub/Sub, atualizando status para REJECTED com assinatura digital quando aplicável

8. **Histórico de Estados**: Mantém histórico completo de transições de estado em tabela separada

9. **Idempotência**: Utiliza UUID como identificador único de portabilidade para garantir idempotência

10. **Atualização Automática**: Job periódico verifica portabilidades com prazo expirado e atualiza status automaticamente

11. **Validação de Documentos**: Mascara documentos sensíveis em logs para conformidade com LGPD

12. **Integração Assíncrona**: Publica eventos em tópico Pub/Sub após cada mudança de estado para sistemas analíticos

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **TbPortabilidadeCredito**: Entidade central contendo dados da portabilidade (portabilityId, contractId, status, valores, datas)
  - Relaciona-se 1:1 com **TbPortabilidadeInstituicao** (dados credora/proponente)
  - Relaciona-se 1:N com **TbPortabilidadeContato** (contatos cliente e proponente)
  - Relaciona-se 1:N com **TbPortabilidadeTarifa** (tarifas pactuadas)
  - Relaciona-se 1:N com **TbPortabilidadeJuro** (taxas de juros)
  - Relaciona-se 1:N com **TbPortabilidadeEncargo** (encargos financeiros)
  - Relaciona-se 1:1 com **TbPortabilidadeCancelada** (dados de cancelamento, quando aplicável)
  - Relaciona-se 1:1 com **TbPortabilidadeRecibo** (recibo de liquidação, quando aplicável)
  - Relaciona-se 1:N com **TbPortabilidadeRazaoRecusa** (motivos de recusa)
  - Relaciona-se 1:N com **TbPortabilidadeControleEstado** (histórico de estados)
  - Referencia **TbPortabilidadeEstado** (definição de estados possíveis)

**Relacionamentos:**
- Portabilidade → Instituição (1:1)
- Portabilidade → Contatos (1:N, discriminado por tipo: PORTABILIDADE/PROPONENTE)
- Portabilidade → Tarifas (1:N)
- Portabilidade → Juros (1:N)
- Portabilidade → Encargos (1:N)
- Portabilidade → Estado (N:1, referência)
- Portabilidade → Histórico Estados (1:N)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbPortabilidadeCredito | tabela | SELECT | Dados principais da portabilidade |
| TbPortabilidadeEstado | tabela | SELECT | Definições de estados possíveis |
| TbPortabilidadeInstituicao | tabela | SELECT | Dados de credora e proponente |
| TbPortabilidadeContato | tabela | SELECT | Contatos do cliente e proponente |
| TbPortabilidadeTarifa | tabela | SELECT | Tarifas pactuadas no contrato |
| TbPortabilidadeJuro | tabela | SELECT | Taxas de juros do contrato |
| TbPortabilidadeEncargo | tabela | SELECT | Encargos financeiros pactuados |
| TbPortabilidadeCancelada | tabela | SELECT | Dados de cancelamento |
| TbPortabilidadeRecibo | tabela | SELECT | Recibo de liquidação |
| TbPortabilidadeRazaoRecusa | tabela | SELECT | Motivos de recusa/rejeição |
| TbPortabilidadeControleEstado | tabela | SELECT | Histórico de transições de estado |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbPortabilidadeCredito | tabela | INSERT/UPDATE | Criação e atualização de portabilidades |
| TbPortabilidadeEstado | tabela | INSERT/UPDATE | Gerenciamento de definições de estados |
| TbPortabilidadeInstituicao | tabela | INSERT | Registro de instituições participantes |
| TbPortabilidadeContato | tabela | INSERT | Registro de contatos |
| TbPortabilidadeTarifa | tabela | INSERT | Registro de tarifas |
| TbPortabilidadeJuro | tabela | INSERT | Registro de taxas de juros |
| TbPortabilidadeEncargo | tabela | INSERT | Registro de encargos |
| TbPortabilidadeCancelada | tabela | INSERT | Registro de cancelamentos |
| TbPortabilidadeRecibo | tabela | INSERT | Registro de recibos de liquidação |
| TbPortabilidadeRazaoRecusa | tabela | INSERT/DELETE | Registro e remoção de motivos de recusa |
| TbPortabilidadeControleEstado | tabela | INSERT | Registro de histórico de estados |
| TbPortabilidadePagamento | tabela | INSERT | Registro de pagamentos efetuados |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| openapi.yaml | leitura | src/main/resources/swagger/ | Especificação OpenAPI 3.0 da API |
| application.yml | leitura | src/main/resources/ | Configurações da aplicação |
| application-local.yml | leitura | src/main/resources/ | Configurações para ambiente local |
| logback-spring.xml | leitura | src/main/resources/ e infra-as-code/arquivos/ | Configuração de logs |
| ESAPI.properties | leitura | src/main/resources/ | Configurações de segurança OWASP |
| layers.xml | leitura | src/main/resources/ | Configuração de camadas Docker |
| *.sql | leitura | src/main/resources/br/com/votorantim/open/pcre/portability/repository/ | Queries SQL para JDBI |

---

## 10. Filas Lidas

**Fila:** `business-port-retn-portability-retention-cancelled-v1-sub` (Google Cloud Pub/Sub)
- **Consumidor:** RejectedPortabilityConsumer
- **Formato:** JSON (EventMessageRetention)
- **Propósito:** Recebe notificações de retenção/cancelamento de portabilidade originadas de outros sistemas
- **Modo:** MANUAL ACK
- **Configuração:** Pull com bloqueio, max 100 mensagens por fetch

---

## 11. Filas Geradas

**Tópico:** `business-open-pcre-portability-state-machine` (Google Cloud Pub/Sub)
- **Produtor:** PortabilityEventService via TopicMessageRepositoryImpl
- **Formato:** JSON (PortabilityEvent)
- **Propósito:** Publica eventos de mudança de estado da portabilidade para sistemas analíticos e de auditoria
- **Trigger:** Após cada transição de estado (criação, atualização, cancelamento, conclusão)

---

## 12. Integrações Externas

1. **Google Cloud Pub/Sub**
   - Consumo de eventos de retenção/cancelamento
   - Publicação de eventos de mudança de estado
   - Comunicação assíncrona com sistemas analíticos

2. **API Gateway OAuth2**
   - Validação de tokens JWT
   - Endpoints: apigatewaydes.bvnet.bv, apigatewayuat.bvnet.bv, apigateway.bvnet.bv
   - JWKS para validação de assinaturas

3. **MySQL Cloud SQL (Google Cloud)**
   - Banco de dados principal (OPENPortabilidadeCredora)
   - Instâncias: gcmysiddes01, gcmysiduat01, gcmysidprd01s

4. **Feature Toggle (ConfigCat)**
   - Configuração dinâmica de feriados
   - Chave de configuração: ft_json_bvopen_feriados

5. **Sistemas Externos (inferidos)**
   - Sistema de Retenção (publica em fila de cancelamento)
   - Sistema Analítico (consome eventos de estado)
   - Operações Internas (notificam conclusão e problemas de pagamento)

---

## 13. Avaliação da Qualidade do Código

**Nota:** 7.5/10

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões Spring Boot e separação de responsabilidades (controllers, services, repositories)
- Uso adequado de JDBI para acesso a dados com SQL externalizado
- Implementação de tratamento centralizado de exceções
- Logging estruturado com mascaramento de dados sensíveis
- Uso de DTOs gerados via OpenAPI garantindo contrato consistente
- Configuração adequada de segurança OAuth2/JWT
- Implementação de Feature Toggle para configurações dinâmicas
- Testes unitários presentes (embora não enviados para análise)

**Pontos de Melhoria:**
- Métodos muito extensos em PortabilityService e PortabilityEventService (violam Single Responsibility Principle)
- Uso excessivo de Optional.ofNullable encadeados dificulta leitura (ex: convertToPortabilityEvent)
- Falta de documentação JavaDoc em classes e métodos críticos
- Lógica de negócio complexa em PortabilityRowReducer poderia ser refatorada
- Alguns métodos com muitos parâmetros (ex: updateStatus com 5 parâmetros)
- Conversões de data repetidas em múltiplos locais (DateUtils poderia ser mais centralizado)
- Falta de constantes para strings mágicas (ex: "PORTABILIDADE", "PROPONENTE")
- Alguns métodos poderiam ser extraídos para melhorar testabilidade

---

## 14. Observações Relevantes

1. **Conformidade Open Finance Brasil**: Sistema implementa especificação completa da API de Portabilidade de Crédito v1.0.0-beta.3 do OFB

2. **Segurança**: Implementa OWASP ESAPI para logging seguro e mascaramento de dados sensíveis (CPF/CNPJ)

3. **Observabilidade**: Integração com OpenTelemetry, Prometheus e logs estruturados JSON para ambientes não-locais

4. **Multi-ambiente**: Configuração diferenciada para DES, UAT e PRD via profiles Spring e infra-as-code

5. **Containerização**: Dockerfile otimizado com múltiplas camadas para melhor cache e deploy

6. **Idempotência**: Uso de UUID v4 para identificadores de portabilidade garante unicidade

7. **Dias Úteis**: Implementação sofisticada de cálculo de dias úteis com suporte a feriados nacionais fixos e configuráveis

8. **Auditoria**: Histórico completo de transições de estado mantido em tabela separada

9. **Resiliência**: Uso de AsyncAppender para logging não-bloqueante e configuração de retry em consumidores Pub/Sub

10. **Padrão Atlante**: Segue padrões e convenções do framework Atlante do Banco Votorantim (versão 3.5.1)

11. **Limitações Identificadas**: 
    - Não há implementação de circuit breaker para integrações externas
    - Falta de rate limiting explícito nos endpoints
    - Ausência de cache para consultas frequentes (ex: elegibilidade)

12. **Dependências Críticas**: Sistema depende fortemente de Google Cloud Platform (Pub/Sub, Cloud SQL) e Feature Toggle externo

---