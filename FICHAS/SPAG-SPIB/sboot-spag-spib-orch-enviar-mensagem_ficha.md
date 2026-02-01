# Ficha Técnica do Sistema

## 1. Descrição Geral
Sistema responsável por enviar mensagens XML do Sistema de Pagamentos Instantâneos (SPI/PIX) para o Banco Central do Brasil (BACEN). O serviço consome mensagens de filas do Google Pub/Sub, processa mensagens nos formatos PACS.002, PACS.004 e PACS.008, realiza assinatura digital via HSM Dinamo, envia para o BACEN via HTTPS e registra métricas e auditoria do processamento.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot que inicializa a aplicação |
| `EnviarMensagemListener` | Listener que consome mensagens do Pub/Sub e aciona o serviço de envio |
| `EnviarMensagemService` | Serviço de domínio que orquestra o envio de mensagens via Apache Camel |
| `EnviarMensagemRouter` | Roteador Apache Camel que define o fluxo de processamento das mensagens |
| `EnviarMensagemRepositoryImpl` | Implementação que realiza comunicação com HSM Dinamo e envio ao BACEN |
| `RemoveTokenRouter` | Roteador responsável por publicar eventos de remoção de token |
| `RemoveTokenPublisherRepositoryImpl` | Publica mensagens para remoção de tokens em filas Pub/Sub |
| `IdentifyTypeMessageProcessor` | Processador que identifica o tipo de mensagem XML (PACS.002/004/008) |
| `StartMetricasProcessor` | Processador que inicia coleta de métricas de liquidação |
| `EndMetricasProcessor` | Processador que finaliza e publica métricas de liquidação |
| `AuditJsonToDocumentProcessor` | Converte objeto de auditoria para JSON |
| `RemoveTokenProcessor` | Prepara payload para remoção de token |

## 3. Tecnologias Utilizadas
- **Framework**: Spring Boot 2.x
- **Integração**: Apache Camel 3.2.0
- **Mensageria**: Google Cloud Pub/Sub
- **HSM**: Dinamo Networks (biblioteca tacndjavalib 4.7.38)
- **Documentação API**: Springfox Swagger 3.0.0
- **Monitoramento**: Spring Actuator, Micrometer, Prometheus
- **Serialização**: Jackson 2.13.4
- **Logging**: Logback com formato JSON
- **Testes**: JUnit 5, Mockito, Rest Assured, Pact
- **Build**: Maven
- **Container**: Docker com OpenJ9 JDK 11
- **Cloud**: Google Cloud Platform (GCP)
- **Auditoria**: springboot-arqt-base-trilha-auditoria-web 2.1.3

## 4. Principais Endpoints REST
Não se aplica. O sistema não expõe endpoints REST públicos, apenas endpoints de monitoramento via Actuator na porta 9090 (/actuator/health, /actuator/metrics, /actuator/prometheus).

## 5. Principais Regras de Negócio
- Consumo de mensagens XML do SPI via Google Pub/Sub
- Identificação automática do tipo de mensagem (PACS.002, PACS.004, PACS.008, CAMT.060, PIBR.001, REDA.022)
- Compressão GZIP do XML antes do envio ao BACEN
- Assinatura digital das mensagens via HSM Dinamo
- Envio HTTPS para o BACEN com certificados gerenciados pelo HSM
- Validação de resposta HTTP 201 do BACEN para considerar sucesso
- Extração de PI-ResourceId do header de resposta do BACEN
- Geração de métricas de liquidação para mensagens PACS
- Publicação de eventos para remoção de tokens de participantes
- Registro de auditoria completa (request/response) em fila específica
- Retry automático (até 2 tentativas) em caso de falha
- Tratamento específico para participantes indiretos (extração de ISPB do MmbId)

## 6. Relação entre Entidades

**Entidades de Domínio:**
- `AuditJson`: Contém dados completos de auditoria da transação (headers, bodies, certificados, timestamps)
- `RemoveTokenPayload`: Payload para remoção de token (api, ispb, statusCode, originService)
- `SpiMetrics`: Métricas do SPI contendo indicadores e eventos de liquidação
- `LiquidationMetrics`: Métricas de eventos de liquidação (endToEnd, instruction, messageType, flow, eventTime)
- `IndicatorsMetrics`: Métricas de indicadores (tempos de execução)
- `TypeMessageEnum`: Enum com tipos de mensagens e suas tags XML correspondentes

**Relacionamentos:**
- `SpiMetrics` contém listas de `IndicatorsMetrics` e `LiquidationMetrics`
- `AuditJson` é gerado após envio bem-sucedido ao BACEN
- `RemoveTokenPayload` é criado com base no tipo de mensagem identificado

## 7. Estruturas de Banco de Dados Lidas
Não se aplica. O sistema não realiza leitura direta de banco de dados.

## 8. Estruturas de Banco de Dados Atualizadas
Não se aplica. O sistema não realiza escrita direta em banco de dados.

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| libdinamo.so | leitura | EnviarMensagemRepositoryImpl | Biblioteca nativa do HSM Dinamo |
| libTacNDJavaLib.so | leitura | EnviarMensagemRepositoryImpl | Biblioteca Java do HSM Dinamo |
| libtacndlib.so | leitura | EnviarMensagemRepositoryImpl | Biblioteca nativa do HSM Dinamo |
| libtacndp11.so | leitura | EnviarMensagemRepositoryImpl | Biblioteca PKCS#11 do HSM Dinamo |
| logback-spring.xml | leitura | Aplicação Spring Boot | Configuração de logs (montado via ConfigMap) |

## 10. Filas Lidas

| Nome da Fila | Tipo | Classe Responsável | Descrição |
|--------------|------|-------------------|-----------|
| business-spag-pixx-envio-mensagem-spi-sub | Google Pub/Sub Subscription | PubSubMensagemRecebidaConfig / EnviarMensagemListener | Subscription que consome mensagens XML do SPI para envio ao BACEN |

## 11. Filas Geradas

| Nome da Fila | Tipo | Classe Responsável | Descrição |
|--------------|------|-------------------|-----------|
| business-spag-pixx-remover-ficha-bucket | Google Pub/Sub Topic | RemoveTokenPublisherRepositoryImpl | Publica eventos para remoção de tokens de participantes |
| business-spag-pixx-metricas-liquidacao | Google Pub/Sub Topic | EnviarMensagemRouter | Publica métricas de liquidação das transações SPI |
| business-spag-pixx-salvar-mensagem | Google Pub/Sub Topic | EnviarMensagemRouter | Publica dados de auditoria completos das mensagens enviadas |

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| BACEN (Banco Central) | API HTTPS | Envio de mensagens SPI via endpoint https://icom.pi.rsfn.net.br/api/v1/in/59588111/msgs (produção) |
| HSM Dinamo | TCP/IP (porta 4433) | Gerenciamento de certificados digitais e assinatura de mensagens |
| Google Cloud Pub/Sub | Mensageria Cloud | Consumo e publicação de mensagens assíncronas |
| sboot-spag-pixx-atom-limitador-fluxo | HTTP REST | Serviço de limitação de fluxo (referenciado na configuração) |

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**
- **Pontos Positivos:**
  - Boa separação de responsabilidades com arquitetura em camadas (application, domain, common)
  - Uso adequado de padrões como Repository, Service e Processor
  - Cobertura de testes unitários presente
  - Configuração externalizada via application.yml e variáveis de ambiente
  - Uso de Apache Camel para orquestração de fluxos complexos
  - Tratamento de exceções com retry configurado
  - Logs estruturados em JSON

- **Pontos de Melhoria:**
  - Classe `EnviarMensagemRepositoryImpl` muito extensa (>300 linhas) com múltiplas responsabilidades
  - Uso de regex para parsing de XML em vez de parser XML apropriado
  - Métodos privados com lógica complexa que dificultam testes isolados
  - Constantes hardcoded em alguns processadores (ex: "CORE", "SNT")
  - Falta de validação de entrada em alguns pontos
  - Comentários em português misturados com código em inglês
  - Alguns testes com mocks excessivos que testam implementação ao invés de comportamento
  - Configuração de timeout e retry poderia ser mais flexível

## 14. Observações Relevantes

1. **Segurança**: O sistema utiliza HSM (Hardware Security Module) Dinamo para gerenciamento seguro de certificados digitais ICP-Brasil, essencial para comunicação com o BACEN.

2. **Resiliência**: Configurado com retry de até 2 tentativas e flow control no Pub/Sub (2000 elementos, 100MB).

3. **Ambientes**: Suporta múltiplos ambientes (des, qa, uat, prd) com configurações específicas de HSM e endpoints do BACEN.

4. **Métricas**: Sistema completo de métricas incluindo tempos de processamento (t1', t3') para diferentes tipos de mensagem.

5. **Auditoria**: Registro completo de todas as transações incluindo headers HTTP, bodies, certificados utilizados e timestamps.

6. **Compressão**: Mensagens XML são comprimidas com GZIP antes do envio ao BACEN para otimização de banda.

7. **Certificados**: Utiliza certificados ICP-Brasil gerenciados pelo HSM com validação de issuer e serial number.

8. **Observabilidade**: Integração com Prometheus/Grafana para monitoramento de métricas customizadas.

9. **Deployment**: Containerizado com Docker, preparado para Kubernetes/OpenShift no GCP.

10. **Limitação de Fluxo**: Integração com serviço de rate limiting para controle de vazão de mensagens.