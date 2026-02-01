# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema orquestrador de auditoria para mensagens PIX (Sistema de Pagamentos Instantâneos Brasileiro). O componente é responsável por receber mensagens de auditoria via Google Cloud Pub/Sub, armazenar XMLs no FileNet (via serviço IGED) e registrar metadados em um banco de dados de auditoria. Utiliza Apache Camel para orquestração de rotas e integração entre sistemas.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot que inicializa a aplicação |
| `AuditDictListener` | Listener que consome mensagens de auditoria DICT do Pub/Sub |
| `SalvarMensagemListener` | Listener que consome mensagens genéricas de auditoria do Pub/Sub |
| `AuditService` | Serviço de domínio que orquestra o processamento de auditoria |
| `AuditDictRouter` | Rota Camel para processar auditoria DICT (request/response) |
| `AuditRouter` | Rota Camel para processar mensagens de auditoria genéricas |
| `AuditTransactionRouter` | Rota Camel para enviar dados ao serviço de auditoria transacional |
| `IgedRouter` | Rota Camel para interação com o FileNet via IGED |
| `AuditTransactionRepositoryImpl` | Implementação de repositório para comunicação com serviço de auditoria |
| `IgedRepositoryImpl` | Implementação de repositório para comunicação com FileNet/IGED |
| `TransactionOperationRepositoryImpl` | Implementação de repositório para consulta de operações de transação |
| `AuditDictMapper` | Mapeamento entre representações e domínio de auditoria DICT |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.x** - Framework principal
- **Apache Camel 3.2.0** - Orquestração de rotas e integração
- **Google Cloud Pub/Sub** - Mensageria (consumo de mensagens)
- **Spring Cloud GCP 1.2.8.RELEASE** - Integração com Google Cloud Platform
- **Jackson** - Serialização/deserialização JSON
- **ModelMapper 2.3.2** - Mapeamento de objetos
- **RestTemplate** - Cliente HTTP para chamadas REST
- **Lombok** - Redução de boilerplate
- **Maven** - Gerenciamento de dependências
- **Java 11** - Linguagem de programação
- **Swagger/OpenAPI 3.0.0** - Documentação de APIs
- **Spring Security OAuth2** - Segurança e autenticação
- **Logback** - Framework de logging

---

## 4. Principais Endpoints REST

Não se aplica. Este é um componente orquestrador que consome mensagens de filas (Pub/Sub) e não expõe endpoints REST próprios. Apenas endpoints do Actuator para monitoramento:

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | /actuator/health | Health check da aplicação |
| GET | /actuator/metrics | Métricas da aplicação |
| GET | /actuator/prometheus | Métricas no formato Prometheus |

---

## 5. Principais Regras de Negócio

1. **Processamento de Auditoria DICT**: Recebe mensagens de auditoria do DICT contendo XMLs de request e response, armazena no FileNet e registra metadados no banco de auditoria
2. **Processamento de Mensagens Genéricas**: Recebe mensagens JSON de auditoria, converte para XML, armazena no FileNet e registra no banco
3. **Armazenamento Condicional**: XMLs de request só são armazenados quando existem (operações GET não possuem request body)
4. **Organização por Data**: Documentos são organizados em pastas do FileNet por data (formato /BV/PIX/yyyy/MM/dd)
5. **Codificação Base64**: Todos os XMLs são codificados em Base64 antes do armazenamento no FileNet
6. **Retry com Backoff**: Implementa retry automático com backoff exponencial (3 tentativas, delay inicial de 1s, multiplicador 2x) para falhas de comunicação
7. **Enriquecimento de Metadados**: Adiciona propriedades customizadas aos documentos (objectStore, origem, título, resourceId, messageType)
8. **Timeout Configurável**: Timeout específico para chamadas ao IGED/FileNet (10 segundos configurável por ambiente)

---

## 6. Relação entre Entidades

**Entidades de Domínio:**

- **AuditDict**: Entidade principal de auditoria DICT
  - Contém: correlationId, xmlRequest, xmlResponse, ispbCode, logDateTime, piRequestId, piPayerId, piResource, messageType, piEndToEndId
  - Relacionamento: 1:1 com AuditDictXml (request e response)

- **AuditDictXml**: Representa um XML de auditoria (request ou response)
  - Contém: httpHeader, httpUrl, auditId, certificateIssuerName, certificateSerialNumber, messageFlow, fileNetUuId, body

- **AuditJson**: Representa mensagem de auditoria genérica
  - Contém: httpRequestHeader, httpRequestUrl, requestBody, logDateTime, httpResponseHeader, httpResponseUrl, responseBody, piResourceId, messageLogType, messageType, certName, certNumber, orinalEndToEnd, originalInstruction, messageVersion, messageFlow, ispbCode, settlementType

- **AuditRequest**: Representa requisição de consulta de auditoria
  - Contém: statusCode, messageType, quantity

**Relacionamentos:**
- AuditDict possui dois AuditDictXml (request e response)
- Após processamento, AuditDict é convertido em AuditTransactionRepresentation para persistência
- AuditJson é convertido em NovoDocumentoRepresentation para armazenamento no FileNet

---

## 7. Estruturas de Banco de Dados Lidas

Não se aplica. O sistema não lê diretamente de banco de dados. Consome mensagens de filas e consulta dados via APIs REST de outros serviços.

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica diretamente. O sistema envia dados para o serviço `sboot-spag-spib-atom-auditoria-transacao` que é responsável pela persistência em banco de dados. As estruturas são:

| Nome da Tabela | Tipo | Operação | Breve Descrição |
|----------------|------|----------|-----------------|
| transaction_audit (via API) | tabela | INSERT | Registros de auditoria de transações PIX via serviço REST |
| dict_audit_transaction (via API) | tabela | INSERT | Registros de auditoria específicos do DICT via serviço REST |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot / Application | Configurações da aplicação (URLs, credenciais, timeouts) |
| logback-spring.xml | leitura | Logback / Application | Configuração de logs (montado via ConfigMap) |
| XMLs PIX (*.xml) | gravação | IgedRouter / IgedRepositoryImpl | XMLs de mensagens PIX armazenados no FileNet via IGED |

---

## 10. Filas Lidas

| Nome da Fila | Tecnologia | Classe Consumidora | Breve Descrição |
|--------------|------------|-------------------|-----------------|
| business-spag-pixx-auditoria-dict-sub | Google Cloud Pub/Sub | AuditDictListener | Mensagens de auditoria do DICT (request/response XMLs) |
| business-spag-pixx-salvar-mensagem-sub | Google Cloud Pub/Sub | SalvarMensagemListener | Mensagens genéricas de auditoria em formato JSON |

**Configurações:**
- Max Outstanding Elements: 3000
- Max Outstanding Request Bytes: 100MB
- Flow Control: Block quando limite excedido
- Ack automático após processamento bem-sucedido
- Nack em caso de erro

---

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas, apenas consome.

---

## 12. Integrações Externas

| Sistema Externo | Tipo | URL/Endpoint | Descrição |
|-----------------|------|--------------|-----------|
| IGED (FileNet) | REST API | springboot-iged-base-documentos-inclui.app*.bvnet.bv | Armazenamento de documentos XML no FileNet |
| Auditoria Transação | REST API | sboot-spag-spib-atom-auditoria-transacao.{env}.svc.cluster.local:8080/v1 | Persistência de metadados de auditoria |
| Transação Operação | REST API | sboot-spag-pixx-atom-transacao-pagamento.{env}.svc.cluster.local:8080/v1 | Consulta de operações de transação PIX |
| API Gateway | OAuth2 | apigateway*.bvnet.bv | Autenticação OAuth2 para chamadas aos serviços |
| Google Cloud Pub/Sub | Mensageria | GCP Project IDs por ambiente | Consumo de mensagens de auditoria |

**Autenticação:**
- IGED: Basic Auth (usuário/senha por ambiente)
- Demais serviços: OAuth2 Bearer Token via API Gateway
- Pub/Sub: Service Account do GCP

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura hexagonal bem definida (domain, application, infrastructure)
- Uso adequado de Apache Camel para orquestração
- Separação clara de responsabilidades entre camadas
- Uso de Lombok reduzindo boilerplate
- Implementação de retry com backoff exponencial
- Configuração externalizada por ambiente
- Uso de ModelMapper para conversões
- Tratamento de erros com logging adequado

**Pontos de Melhoria:**
- Falta de testes unitários nos arquivos fornecidos (apenas estrutura de testes presente)
- Hardcoding de valores em algumas classes (ex: MAX_OUTSTANDING_ELEMENT_COUNT, timeouts)
- Uso de Strings literais em várias partes do código (poderia usar constantes)
- Falta de validação de entrada em alguns processadores
- Documentação JavaDoc ausente na maioria das classes
- Alguns métodos longos que poderiam ser refatorados (ex: prepareRepresentation)
- Uso de Optional poderia ser mais consistente
- Falta de tratamento específico para diferentes tipos de exceção
- Configuração de retry poderia ser externalizada

---

## 14. Observações Relevantes

1. **Ambiente Multi-Cloud**: Sistema preparado para rodar em Google Cloud Platform (GKE) com integração nativa ao Pub/Sub

2. **Configuração por Ambiente**: Possui configurações específicas para local, des, qa, uat e prd via ConfigMaps e Secrets do Kubernetes

3. **Monitoramento**: Integrado com Prometheus para coleta de métricas via Actuator

4. **Segurança**: Implementa OAuth2 Resource Server com validação de JWT via API Gateway

5. **Timeout Específico**: Implementa RestTemplate com timeout configurável especificamente para chamadas ao IGED/FileNet (10 segundos)

6. **Organização de Documentos**: XMLs são organizados em estrutura de pastas por data no FileNet (/BV/PIX/yyyy/MM/dd)

7. **Resiliência**: Implementa retry automático com backoff exponencial (3 tentativas) para falhas de comunicação

8. **Processamento Assíncrono**: Utiliza Pub/Sub para desacoplamento e processamento assíncrono de mensagens de auditoria

9. **Service Account**: Utiliza Service Account do Kubernetes (ksa-spag-spib-14472) para autenticação com GCP

10. **Probes Configurados**: Health checks configurados com liveness (420s initial delay) e readiness (3s initial delay) para gerenciamento pelo Kubernetes

11. **Recursos Limitados**: CPU limitado a 1 core e memória a 512Mi, com requests de 100m CPU

12. **Certificados Globais**: Monta cacerts global do Java via volume do Kubernetes para validação SSL