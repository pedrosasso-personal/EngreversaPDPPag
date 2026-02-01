# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de orquestração para recebimento de mensagens secundárias do Banco Central (BACEN) através do canal BA (Banco Agente) no contexto do SPI (Sistema de Pagamentos Instantâneos - PIX). O sistema realiza polling periódico no BACEN utilizando comunicação segura via HSM Dinamo, processa mensagens XML (PACS.002, PACS.004, PACS.008, ADMI.002), e publica em filas do Google Cloud Pub/Sub para processamento posterior e auditoria.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot para inicialização da aplicação |
| `ReceiveBaMessagesRouter` | Rota Camel que agenda polling periódico para buscar mensagens do BACEN |
| `SendMessagesRouter` | Processa e roteia mensagens recebidas do BACEN |
| `PublishReceivedMessagesRouter` | Publica mensagens recebidas na fila de processamento |
| `PublishAuditMessagesRouter` | Publica mensagens de auditoria |
| `ReceiveMessageBARepositoryAdapter` | Adaptador para comunicação com BACEN via HSM Dinamo |
| `TratarBoundaryProcessor` | Processa boundary multipart e extrai informações das mensagens XML |
| `PrepareToPublishReceivedMessageProcessor` | Prepara mensagens para publicação na fila de recebimento |
| `PrepareToPublishAuditMessageProcessor` | Prepara mensagens de auditoria para publicação |
| `PixProcessor` | Processador auxiliar para limpeza de contexto |
| `BaseRoute` | Classe base com tratamento de exceções para rotas Camel |
| `PublisherRepositoryImpl` | Implementação de publicação em filas Pub/Sub |
| `JwtAuthorizationHeaderGenerator` | Gerador de tokens de autorização JWT |

## 3. Tecnologias Utilizadas

- **Framework Principal**: Spring Boot 2.7.x
- **Orquestração**: Apache Camel 3.x
- **Mensageria**: Google Cloud Pub/Sub (via Atlante Sidecar)
- **Segurança**: Spring Security OAuth2, JWT, HSM Dinamo (TacNDJavaLib 4.7.38)
- **Comunicação HTTP**: Apache HttpClient
- **Logging**: Logback com formato JSON
- **Containerização**: Docker
- **Infraestrutura**: Google Cloud Platform (GCP)
- **Monitoramento**: Spring Actuator, Micrometer, Prometheus
- **Observabilidade**: OpenTelemetry
- **Build**: Maven
- **Testes**: JUnit 5, Mockito

## 4. Principais Endpoints REST

não se aplica

(O sistema não expõe endpoints REST públicos, funciona como orquestrador baseado em timer/polling)

## 5. Principais Regras de Negócio

- **Polling Periódico**: Busca mensagens do BACEN em intervalos configuráveis (padrão: 2000ms)
- **Long Polling**: Implementa long polling com timeout configurável para otimizar comunicação com BACEN
- **Processamento Multipart**: Processa respostas multipart/mixed do BACEN separando múltiplas mensagens XML
- **Extração de Metadados**: Extrai informações como PI-ResourceId, ISPB, tipo de mensagem, certificados digitais
- **Identificação de Tipos de Mensagem**: Diferencia PACS.002 (confirmação), PACS.004 (devolução), PACS.008 (pagamento), ADMI.002 (rejeição)
- **Cálculo de Delay**: Calcula tempo de processamento entre recebimento BACEN e processamento interno
- **Gestão de Stream**: Mantém controle do PI-Pull-Next para continuidade do stream de mensagens
- **Tratamento de Status HTTP**: Processa códigos 200 (sucesso), 204 (sem conteúdo), 400+ (erro)
- **Delete Automático**: Remove mensagens processadas do BACEN via DELETE HTTP
- **Auditoria Completa**: Registra headers, bodies, timestamps e metadados de todas as transações
- **Retry com Backoff**: Implementa retry automático (2 tentativas) em caso de falhas
- **Paralelização**: Processa múltiplas mensagens em paralelo quando recebidas em batch

## 6. Relação entre Entidades

**Entidades de Domínio:**

- `AuditJson`: Contém dados completos de auditoria (headers HTTP, bodies, timestamps, certificados, ISPB, tipo de mensagem)
- `DinamoProperties`: Configurações de conexão com HSM Dinamo
- `EndpointProperties`: Configurações de endpoints do BACEN
- `CredentialProperties`: Credenciais e certificados para autenticação
- `RouterConstants`: Constantes e estado da rota (paths, delays)
- `IndicatorsMetrics`: Métricas de indicadores de performance
- `LiquidationMetrics`: Métricas de liquidação de transações
- `SpiMetrics`: Agregador de métricas do SPI

**Relacionamentos:**
- `DinamoProperties` contém `EndpointProperties` e `CredentialProperties`
- `RouterProperties` contém `DinamoProperties`
- `SpiMetrics` contém listas de `IndicatorsMetrics` e `LiquidationMetrics`
- `AuditJson` é criado e enriquecido ao longo do fluxo de processamento

## 7. Estruturas de Banco de Dados Lidas

não se aplica

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | leitura | Configuração Spring Boot | Configuração de logging em formato JSON |
| application.yml | leitura | Configuração Spring Boot | Configurações da aplicação por ambiente |
| application-local.yml | leitura | Configuração Spring Boot | Configurações específicas do ambiente local |
| layers.xml | leitura | Build Maven | Configuração de camadas para otimização de imagem Docker |

## 10. Filas Lidas

não se aplica

(O sistema não consome de filas, apenas publica)

## 11. Filas Geradas

| Nome da Fila | Tipo | Descrição |
|--------------|------|-----------|
| business-spag-pixx-receber-mensagem-spi-canal-secundario | Google Cloud Pub/Sub | Fila para publicação de mensagens XML recebidas do BACEN para processamento posterior |
| business-spag-pixx-salvar-mensagem | Google Cloud Pub/Sub | Fila para publicação de mensagens de auditoria contendo todos os metadados da transação |

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| BACEN SPI (icom-sec.pi.rsfn.net.br) | API REST HTTPS | Sistema de Pagamentos Instantâneos do Banco Central - recebimento de mensagens via long polling |
| HSM Dinamo | Biblioteca Nativa (TacNDJavaLib) | Hardware Security Module para criptografia e autenticação mútua TLS com BACEN |
| Google Cloud Pub/Sub | Mensageria | Publicação de mensagens recebidas e auditoria |
| API Gateway BV | OAuth2/JWT | Autenticação e autorização via tokens JWT |

**Detalhes da Integração BACEN:**
- Protocolo: HTTPS com autenticação mútua via certificados digitais
- Endpoints: `/api/v1/out/{ISPB}/stream/start` (GET para long polling, DELETE para confirmação)
- Formato: Multipart/mixed com mensagens XML assinadas digitalmente
- Timeouts: GET (7000ms produção), DELETE (2000ms)

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com uso de padrões (Repository, Processor, Router)
- Uso adequado de Apache Camel para orquestração
- Tratamento de exceções estruturado com retry automático
- Logging detalhado em formato JSON para observabilidade
- Testes unitários presentes com boa cobertura
- Uso de fixtures para geração de dados de teste
- Configuração externalizada por ambiente
- Documentação básica presente (README)

**Pontos de Melhoria:**
- Classe `ReceiveMessageRepository` muito extensa (>300 linhas) com múltiplas responsabilidades
- Lógica de parsing XML com regex em `TratarBoundaryProcessor` poderia usar parser XML adequado
- Hardcoded strings e magic numbers em vários pontos (ex: "200", "204", "410")
- Falta de validação de entrada em alguns processadores
- Comentários escassos no código
- Alguns métodos longos que poderiam ser refatorados (ex: `longPolling`, `getBacenDate`)
- Uso de variáveis estáticas mutáveis em `RouterConstants` (DELAY_GET_BACEN, etc.)
- Tratamento genérico de Exception em alguns pontos poderia ser mais específico
- Falta de documentação JavaDoc nas classes públicas

## 14. Observações Relevantes

1. **Segurança Crítica**: Sistema lida com comunicação sensível com Banco Central usando certificados digitais e HSM, requer atenção especial em ambientes produtivos

2. **Dependência de Biblioteca Nativa**: Uso de bibliotecas .so do Dinamo (libdinamo.so, libTacNDJavaLib.so) requer configuração específica no container Docker

3. **Ambientes Segregados**: Configurações distintas para DES, UAT e PRD com ISPBs e endpoints diferentes (homologação vs produção do BACEN)

4. **Timezone UTC**: Sistema opera em UTC para sincronização com timestamps do BACEN

5. **Processamento Assíncrono**: Mensagens são processadas em paralelo quando recebidas em batch, otimizando throughput

6. **Resiliência**: Implementa retry automático e tratamento de falhas de rede/timeout

7. **Observabilidade**: Integração com OpenTelemetry para tracing distribuído e métricas Prometheus

8. **Infraestrutura como Código**: Configuração de infraestrutura GCP presente em `infra.yml`

9. **Multi-layer Docker**: Otimização de build com camadas separadas para dependências comuns, reduzindo tempo de deploy

10. **Conformidade PIX**: Sistema segue especificações do SPI/PIX do Banco Central para mensageria ISO 20022