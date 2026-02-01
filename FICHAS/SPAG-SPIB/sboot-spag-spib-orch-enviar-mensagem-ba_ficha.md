# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-spag-spib-orch-enviar-mensagem-ba** é um orquestrador responsável por enviar mensagens do Sistema de Pagamentos Instantâneos (PIX) ao Banco Central do Brasil (BACEN). Ele consome mensagens de uma fila PubSub, processa XMLs de transações PIX (pagamentos, devoluções, confirmações), assina digitalmente utilizando HSM Dinamo, envia ao BACEN via HTTPS, registra auditoria e métricas, e publica eventos para remoção de tokens de rate limiting. O sistema atua como intermediário crítico na comunicação entre o Banco Votorantim e o Sistema de Pagamentos Instantâneos (SPI) do BACEN.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot que inicializa a aplicação |
| `EnviarMensagemRouter` | Roteador Camel principal que orquestra o fluxo de envio de mensagens |
| `RemoveTokenRouter` | Roteador Camel responsável pelo fluxo de remoção de tokens de rate limiting |
| `EnviarMensagemListener` | Listener que consome mensagens da fila PubSub para iniciar o processamento |
| `EnviarMensagemService` | Serviço que dispara o processamento via template Camel |
| `EnviarMensagemRepositoryImpl` | Implementação que realiza a comunicação com BACEN via HSM Dinamo |
| `PubSubPublisher` | Publica mensagens de auditoria e métricas em tópicos PubSub |
| `RemoveTokenPublisherRepositoryImpl` | Publica mensagens para remoção de tokens de rate limiting |
| `StartMetricasProcessor` | Processor que inicia a coleta de métricas de liquidação |
| `EndMetricasProcessor` | Processor que finaliza e publica métricas de liquidação |
| `IdentifyTypeMessageProcessor` | Identifica o tipo de mensagem PIX e extrai ISPB para remoção de token |
| `RemoveTokenProcessor` | Prepara payload para remoção de token |
| `AuditJsonToDocumentProcessor` | Converte objeto de auditoria para JSON |
| `AuditJson` | Domínio que representa dados de auditoria da comunicação |
| `SpiMetrics` | Domínio que representa métricas de liquidação SPI |
| `RemoveTokenPayload` | Domínio que representa payload de remoção de token |
| `TypeMessageEnum` | Enum que define tipos de mensagens PIX e tags XML correspondentes |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.5.x** - Framework base da aplicação
- **Apache Camel** - Framework de integração e roteamento de mensagens
- **Google Cloud Pub/Sub** - Sistema de mensageria para consumo e publicação de eventos
- **HSM Dinamo (TacNDJavaLib 4.7.38)** - Hardware Security Module para assinatura digital de mensagens
- **Maven** - Gerenciamento de dependências e build
- **Java 11** - Linguagem de programação
- **Spring Cloud GCP** - Integração com serviços Google Cloud Platform
- **Atlante (Framework interno Banco Votorantim)** - Bibliotecas de segurança, mensageria e sidecar
- **Lombok** - Redução de boilerplate code
- **Jackson** - Serialização/deserialização JSON
- **SLF4J/Logback** - Framework de logging
- **Docker** - Containerização da aplicação
- **Actuator** - Monitoramento e health checks

---

## 4. Principais Endpoints REST

Não se aplica. O sistema não expõe endpoints REST públicos. A comunicação é baseada em mensageria assíncrona (PubSub) e o único endpoint disponível é o Actuator para health checks (`/actuator/health` na porta 9090).

---

## 5. Principais Regras de Negócio

1. **Processamento de Mensagens PIX**: Consome mensagens XML de transações PIX (PACS.008, PACS.004, PACS.002, CAMT.060, PIBR.001, REDA.022) de uma fila PubSub
2. **Assinatura Digital com HSM**: Utiliza HSM Dinamo para assinar digitalmente as mensagens antes do envio ao BACEN, garantindo autenticidade e integridade
3. **Compressão GZIP**: Comprime o XML antes do envio para otimizar a transmissão
4. **Envio ao BACEN**: Realiza POST HTTPS para a API do BACEN com certificados digitais gerenciados pelo HSM
5. **Validação de Resposta**: Valida status code 201 como sucesso, caso contrário lança exceção
6. **Auditoria Completa**: Registra request/response headers, bodies, timestamps, certificados utilizados, PI-ResourceId retornado pelo BACEN
7. **Métricas de Liquidação**: Coleta métricas de tempo de processamento (t1', t3') para mensagens PACS.008, PACS.004 e PACS.002
8. **Remoção de Token de Rate Limiting**: Identifica ISPB da mensagem e publica evento para liberar token de rate limiting após envio bem-sucedido
9. **Retry Automático**: Configurado para 2 tentativas em caso de falha
10. **Identificação de Tipo de Mensagem**: Extrai tipo de mensagem do XML e identifica ISPB correspondente para diferentes fluxos (pagamento, devolução, confirmação)
11. **Tratamento de Ambientes**: Suporta configurações distintas para DES, UAT e PRD (URLs, credenciais, certificados)

---

## 6. Relação entre Entidades

**Entidades de Domínio:**

- **AuditJson**: Representa dados completos de auditoria de uma transação (request, response, headers, certificados, timestamps, identificadores PIX)
- **SpiMetrics**: Agregador de métricas contendo listas de `IndicatorsMetrics` e `LiquidationMetrics`
- **LiquidationMetrics**: Métricas de eventos de liquidação (endToEnd, instruction, messageType, messageFlow, eventTime, eventType, operationFlow, ispbCode)
- **IndicatorsMetrics**: Métricas de indicadores de performance (tempos de execução)
- **RemoveTokenPayload**: Payload para remoção de token contendo API, ISPB, statusCode e originService fixo como "CORE"
- **TypeMessageEnum**: Enum que mapeia tipos de mensagens PIX (CAMT060, PACS002, PACS004, PACS008, PIBR001, REDA022) com suas respectivas tags XML para extração de ISPB

**Relacionamentos:**
- `SpiMetrics` contém listas de `IndicatorsMetrics` e `LiquidationMetrics` (composição)
- `AuditJson` é independente, representa um registro completo de auditoria
- `RemoveTokenPayload` é construído a partir de informações extraídas do XML processado

---

## 7. Estruturas de Banco de Dados Lidas

Não se aplica. O sistema não realiza leitura direta de banco de dados. Toda comunicação é baseada em mensageria (PubSub) e APIs REST (BACEN).

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema não atualiza diretamente estruturas de banco de dados. A persistência de auditoria e métricas é realizada através de publicação em tópicos PubSub, sendo responsabilidade de outros sistemas consumidores persistir essas informações.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `logback-spring.xml` | leitura | `/usr/etc/log/` (ConfigMap montado) | Arquivo de configuração de logs, específico por ambiente (DES/UAT/PRD) |
| `application.yml` | leitura | `src/main/resources/` | Arquivo de configuração principal da aplicação Spring Boot |
| `application-local.yml` | leitura | `src/main/resources/` | Arquivo de configuração para perfil local de desenvolvimento |
| Bibliotecas HSM Dinamo (`.so`) | leitura | `/opt/java/openjdk/lib/` | Bibliotecas nativas do HSM Dinamo copiadas no Dockerfile para assinatura digital |

---

## 10. Filas Lidas

**Fila/Subscription consumida:**
- **business-spag-pixx-envio-mensagem-spi-ba-sub** (GCP Pub/Sub Subscription)
  - **Listener:** `EnviarMensagemListener`
  - **Descrição:** Consome mensagens XML de transações PIX que devem ser enviadas ao BACEN. A mensagem contém o XML completo e atributos como `ispbToRemoveToken` para controle de rate limiting.

---

## 11. Filas Geradas

**Tópicos publicados:**

1. **business-spag-pixx-salvar-mensagem** (GCP Pub/Sub Topic)
   - **Publisher:** `PubSubPublisher.publishMessageAudit()`
   - **Descrição:** Publica dados de auditoria completos (AuditJson serializado) contendo request/response da comunicação com BACEN para persistência histórica

2. **business-spag-pixx-metricas-liquidacao** (GCP Pub/Sub Topic)
   - **Publisher:** `PubSubPublisher.publishMessageMetrics()`
   - **Descrição:** Publica métricas de liquidação (SpiMetrics serializado) contendo tempos de processamento e eventos para análise de performance

3. **business-spag-pixx-remover-ficha-bucket** (GCP Pub/Sub Topic)
   - **Publisher:** `RemoveTokenPublisherRepositoryImpl.removeToken()`
   - **Descrição:** Publica evento para remoção de token de rate limiting após envio bem-sucedido ao BACEN, liberando capacidade para novas requisições do ISPB

---

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| **BACEN - Sistema de Pagamentos Instantâneos (SPI)** | API REST HTTPS | Endpoint principal para envio de mensagens PIX. URLs variam por ambiente: `https://icom.pi.rsfn.net.br:16422/api/v1/in/13140088/msgs` (PRD), `https://icom-h.pi.rsfn.net.br:16522/api/v1/in/13140088/msgs` (UAT). Requer autenticação via certificado digital gerenciado por HSM |
| **HSM Dinamo** | Biblioteca Nativa (TacNDJavaLib) | Hardware Security Module para assinatura digital de mensagens. Conexão via TCP em hosts específicos por ambiente (ex: `hsmpixspib.bvnet.bv:4433` PRD). Gerencia chaves privadas, certificados e cadeia de certificação PIX |
| **Google Cloud Pub/Sub** | Mensageria | Plataforma de mensageria para consumo de mensagens de entrada e publicação de eventos de auditoria, métricas e remoção de tokens. Projetos GCP específicos por ambiente |
| **Atlante Sidecar Mensageria** | Framework Interno | Abstração sobre GCP Pub/Sub fornecida pelo framework Atlante do Banco Votorantim para facilitar integração com mensageria |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com uso de padrões como Repository, Service e Processors
- Uso adequado de Lombok para reduzir boilerplate
- Logging estruturado e informativo em pontos críticos
- Configuração externalizada por ambiente (DES/UAT/PRD)
- Tratamento de exceções com retry configurado
- Uso de interfaces (ports) para abstrair implementações
- Documentação básica presente no README

**Pontos de Melhoria:**
- **Hardcoding de valores**: Strings como tags XML, nomes de propriedades e constantes espalhadas pelo código (ex: `"<MsgDefIdr>(.+?)</MsgDefIdr>"`)
- **Métodos longos**: `EnviarMensagemRepositoryImpl.enviarSolicitacaoPagamentoBacen()` possui lógica extensa e complexa que poderia ser refatorada em métodos menores
- **Duplicação de código**: Lógica de extração de XML via regex repetida em múltiplos processors
- **Falta de testes unitários enviados**: Apenas classes de teste foram marcadas como NÃO_ENVIAR, impossibilitando avaliar cobertura
- **Tratamento de exceções genérico**: `EnviarMensagemException` não possui contexto específico, dificultando troubleshooting
- **Acoplamento com HSM**: Lógica de comunicação com Dinamo fortemente acoplada ao repositório, dificultando testes e manutenção
- **Falta de validação de entrada**: Não há validação explícita do formato XML antes do processamento
- **Comentários escassos**: Código complexo (especialmente regex e lógica HSM) carece de comentários explicativos

O código é funcional e segue padrões arquiteturais adequados, mas há espaço significativo para melhorias em manutenibilidade, testabilidade e clareza.

---

## 14. Observações Relevantes

1. **Segurança Crítica**: O sistema manipula certificados digitais e chaves privadas através de HSM, sendo componente crítico de segurança. As credenciais são injetadas via secrets do Kubernetes.

2. **Ambientes Segregados**: Configurações completamente distintas para DES, UAT e PRD, incluindo URLs BACEN, credenciais HSM, certificados e projetos GCP diferentes.

3. **Dependência de Infraestrutura Específica**: Requer bibliotecas nativas do HSM Dinamo (`.so`) copiadas para o container, tornando a aplicação dependente de arquitetura Linux específica.

4. **Monitoramento**: Expõe métricas via Actuator/Prometheus na porta 9090, separada da porta de aplicação (8080).

5. **Rate Limiting Distribuído**: Integração com sistema de limitador de fluxo através de remoção de tokens, indicando arquitetura de controle de vazão distribuída.

6. **Processamento Assíncrono**: Todo fluxo é assíncrono baseado em eventos, sem endpoints síncronos expostos.

7. **Retry Limitado**: Configurado para apenas 2 tentativas de reenvio, o que pode ser insuficiente para falhas transitórias de rede.

8. **Compressão Obrigatória**: Todas as mensagens são comprimidas com GZIP antes do envio, requisito da API BACEN.

9. **Auditoria Completa**: Registra absolutamente todos os detalhes da comunicação (headers, bodies, certificados, timestamps), essencial para conformidade regulatória.

10. **Tipos de Mensagem PIX**: Suporta múltiplos tipos de mensagens do ecossistema PIX (pagamentos, devoluções, confirmações, consultas de conta, gerenciamento de chaves).