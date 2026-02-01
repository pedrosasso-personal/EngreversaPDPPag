# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema responsável por enviar mensagens SPI (Sistema de Pagamentos Instantâneos) para o BACEN (Banco Central do Brasil) através do protocolo PIX. O sistema consome mensagens de uma fila PubSub do Google Cloud, processa mensagens XML (pacs.002, pacs.004, pacs.008, entre outras), realiza comunicação segura com o BACEN via HSM Dinamo, e publica eventos de auditoria e métricas. Atua como orquestrador no fluxo de envio de mensagens do Banco Votorantim para o Sistema de Pagamentos Instantâneos.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot que inicializa a aplicação |
| `EnviarMensageListener` | Listener que consome mensagens do PubSub e aciona o serviço de envio |
| `EnviarMensagemService` | Serviço de domínio que orquestra o envio de mensagens via Apache Camel |
| `EnviarMensagemRepositoryImpl` | Implementação da comunicação com BACEN via HSM Dinamo |
| `RemoveTokenPublisherRepositoryImpl` | Publica eventos para remoção de tokens de rate limit |
| `EnviarMensagemRouter` | Rota Apache Camel principal que orquestra o fluxo de processamento |
| `RemoveTokenRouter` | Rota Apache Camel para processamento de remoção de tokens |
| `StartMetricasProcessor` | Processador que inicia coleta de métricas de liquidação |
| `EndMetricasProcessor` | Processador que finaliza e publica métricas de liquidação |
| `IdentifyTypeMessageProcessor` | Identifica o tipo de mensagem SPI e extrai ISPB para controle de token |
| `AuditJsonProcessor` | Converte objeto de auditoria para JSON |
| `EnviarMensagemSPIHTTPProcessor` | Prepara mensagem para envio HTTP |
| `RemoveTokenProcessor` | Processa payload para remoção de token |
| `CamelContextWrapper` | Wrapper do contexto Apache Camel com configurações customizadas |

---

## 3. Tecnologias Utilizadas

- **Java 11** (OpenJ9)
- **Spring Boot 2.x** (framework base)
- **Apache Camel 3.2.0** (orquestração e roteamento de mensagens)
- **Google Cloud PubSub** (mensageria)
- **HSM Dinamo 4.1.6** (criptografia e comunicação segura com BACEN)
- **Jackson** (serialização JSON)
- **Springfox/Swagger 3.0.0** (documentação de API)
- **Micrometer/Prometheus** (métricas)
- **Logback** (logging)
- **JUnit 5 + Mockito** (testes)
- **Maven** (build)
- **Docker** (containerização)
- **Kubernetes/OpenShift** (orquestração)

---

## 4. Principais Endpoints REST

Não se aplica. O sistema não expõe endpoints REST públicos, apenas endpoints de gerenciamento do Spring Actuator (health, metrics, prometheus) na porta 9090.

---

## 5. Principais Regras de Negócio

1. **Consumo de Mensagens**: Consome mensagens XML do PubSub (subscription `business-spag-pixx-envio-mensagem-spi-bvsa-sub`)
2. **Identificação de Tipo de Mensagem**: Identifica tipo de mensagem SPI (pacs.002, pacs.004, pacs.008, camt.060, pibr.001, reda.022) e extrai ISPB
3. **Compressão GZIP**: Comprime mensagens XML em GZIP antes do envio ao BACEN
4. **Comunicação Segura**: Utiliza certificados digitais via HSM Dinamo para comunicação com BACEN
5. **Validação de Resposta**: Valida status HTTP 201 do BACEN para considerar envio bem-sucedido
6. **Auditoria**: Registra todas as requisições e respostas (headers, body, timestamps, certificados)
7. **Métricas de Liquidação**: Coleta métricas de tempo de processamento (t1', t3') para mensagens pacs
8. **Controle de Rate Limit**: Publica eventos para remoção de tokens de rate limit após envio bem-sucedido
9. **Retry**: Implementa retry (2 tentativas) em caso de falha no envio
10. **Extração de Dados**: Extrai EndToEndId, InstructionId, ISPB, certificados e outros metadados das mensagens XML

---

## 6. Relação entre Entidades

**Entidades de Domínio:**

- **AuditJson**: Representa dados de auditoria (request/response, certificados, timestamps, identificadores)
- **SpiMetrics**: Agregador de métricas (eventos de liquidação + indicadores)
- **LiquidationMetrics**: Métricas de eventos de liquidação (tempos t1', t3')
- **IndicatorsMetrics**: Métricas de indicadores de performance
- **RemoveTokenPayload**: Payload para remoção de token de rate limit
- **RateLimitResponse**: Resposta de operações de rate limit
- **TypeMessageEnum**: Enumeração de tipos de mensagens SPI (PACS002, PACS004, PACS008, CAMT060, PIBR001, REDA022)

**Relacionamentos:**
- `SpiMetrics` contém lista de `LiquidationMetrics` e `IndicatorsMetrics`
- `AuditJson` é gerado a partir do retorno do BACEN
- `RemoveTokenPayload` é criado após processamento bem-sucedido

---

## 7. Estruturas de Banco de Dados Lidas

Não se aplica. O sistema não realiza leitura direta de banco de dados.

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema não realiza escrita direta em banco de dados.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `application.yml` | Leitura | Spring Boot | Configurações da aplicação (profiles, endpoints, credenciais) |
| `logback-spring.xml` | Leitura | Logback | Configuração de logs (formato JSON, níveis, appenders) |
| Bibliotecas HSM Dinamo (*.so) | Leitura | `EnviarMensagemRepositoryImpl` | Bibliotecas nativas para comunicação com HSM |

---

## 10. Filas Lidas

| Nome da Fila | Tecnologia | Classe Consumidora | Descrição |
|--------------|------------|-------------------|-----------|
| `business-spag-pixx-envio-mensagem-spi-bvsa-sub` | Google Cloud PubSub | `PubSubEnviarMensagemConfig` / `EnviarMensageListener` | Subscription que recebe mensagens XML SPI para envio ao BACEN |

**Configurações:**
- Max Outstanding Elements: 2000
- Max Outstanding Request Bytes: 100MB
- Limit Exceeded Behavior: Block
- Acknowledge automático após processamento

---

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Produtora | Descrição |
|--------------|------------|-----------------|-----------|
| `business-spag-pixx-remover-ficha-bucket` | Google Cloud PubSub | `RemoveTokenPublisherRepositoryImpl` | Publica eventos para remoção de tokens de rate limit |
| `business-spag-pixx-metricas-liquidacao` | Google Cloud PubSub | `EnviarMensagemRouter` | Publica métricas de liquidação (tempos de processamento) |
| `business-spag-pixx-salvar-mensagem` | Google Cloud PubSub | `EnviarMensagemRouter` | Publica dados de auditoria das mensagens enviadas |

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **BACEN - SPI** | API REST HTTPS | Envio de mensagens PIX para o Sistema de Pagamentos Instantâneos do Banco Central (endpoints icom-h.pi.rsfn.net.br e icom.pi.rsfn.net.br) |
| **HSM Dinamo** | TCP/IP (porta 4433) | Hardware Security Module para criptografia, assinatura digital e gerenciamento de certificados |
| **Google Cloud PubSub** | Mensageria | Consumo e publicação de mensagens em filas |
| **Atom Limitador de Fluxo** | API REST HTTP | Serviço interno para controle de rate limit (não utilizado diretamente, apenas referenciado) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades (domain, application, infrastructure)
- Uso adequado de padrões (Repository, Service, Processor)
- Testes unitários presentes
- Configuração externalizada
- Uso de Lombok para reduzir boilerplate
- Tratamento de exceções com retry
- Logging estruturado

**Pontos de Melhoria:**
- Uso excessivo de regex e parsing manual de XML (poderia usar JAXB/XPath)
- Métodos muito longos em `EnviarMensagemRepositoryImpl` (violação de Single Responsibility)
- Acoplamento forte com biblioteca Dinamo proprietária
- Falta de validação de entrada em alguns pontos
- Comentários escassos em lógicas complexas
- Uso de `ReflectionTestUtils` nos testes indica possível problema de design
- Configuração de rotas Camel poderia ser mais declarativa
- Falta de tratamento específico para diferentes tipos de erro do BACEN

---

## 14. Observações Relevantes

1. **Segurança**: Sistema utiliza certificados ICP-Brasil para comunicação com BACEN, gerenciados via HSM Dinamo
2. **Ambientes**: Configurado para 4 ambientes (des, qa, uat, prd) com endpoints e credenciais distintas
3. **Resiliência**: Implementa retry automático (2 tentativas) e controle de flow control no PubSub
4. **Observabilidade**: Métricas Prometheus, logs estruturados JSON, auditoria completa de requisições
5. **Performance**: Usa compressão GZIP para reduzir tráfego de rede
6. **Compliance**: Registra certificados digitais e números de série para rastreabilidade
7. **Infraestrutura**: Preparado para Kubernetes/OpenShift com probes de liveness e readiness
8. **Limitações**: Timeout fixo de 2000ms para comunicação com BACEN
9. **Dependências Nativas**: Requer bibliotecas .so do Dinamo no container (Linux)
10. **Versionamento**: Sistema suporta múltiplas versões de mensagens SPI (1.3, 1.4, 1.10)