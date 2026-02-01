# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-spag-spib-orch-receber-mensagem-secundario** é um orquestrador baseado em Apache Camel e Spring Boot responsável por receber mensagens do Sistema de Pagamentos Instantâneos (SPI/PIX) através de um canal secundário do Banco Central (BACEN). 

O componente realiza polling periódico no endpoint do BACEN utilizando comunicação segura via HSM Dinamo, processa as mensagens recebidas (principalmente PACS.002 e PACS.008), extrai informações de auditoria e metadados, e publica as mensagens em filas do Google Cloud Pub/Sub para processamento posterior. O sistema também gerencia o ciclo de vida das mensagens no BACEN (GET e DELETE).

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal Spring Boot que inicializa a aplicação |
| **ReceiveBvMessagesRouter** | Rota Camel que agenda o polling periódico de mensagens do BACEN |
| **SendMessagesRouter** | Rota que processa e distribui as mensagens recebidas |
| **PublishReceivedMessagesRouter** | Rota que publica mensagens recebidas no tópico Pub/Sub |
| **PublishAuditMessagesRouter** | Rota que publica mensagens de auditoria no tópico Pub/Sub |
| **ReceiveMessageBVRepositoryAdapter** | Adaptador que implementa a comunicação com o BACEN via Dinamo |
| **ReceiveMessageRepository** | Classe abstrata que contém a lógica de long polling e gerenciamento de mensagens |
| **TratarBoundaryProcessor** | Processa mensagens multipart, extrai XMLs e metadados do BACEN |
| **PrepareToPublishReceivedMessageProcessor** | Prepara headers para publicação de mensagens recebidas |
| **PrepareToPublishAuditMessageProcessor** | Prepara mensagens de auditoria em formato JSON |
| **PixProcessor** | Processador auxiliar para mensagens PIX |
| **AuditJson** | Modelo de dados para auditoria de mensagens |
| **RouterConstants** | Constantes e estado compartilhado entre rotas |

---

## 3. Tecnologias Utilizadas

- **Java 11** (OpenJ9)
- **Spring Boot 2.7.3**
- **Apache Camel** (integração e orquestração)
- **Google Cloud Pub/Sub** (mensageria)
- **Dinamo HSM** (comunicação segura com BACEN via biblioteca tacndjavalib 4.7.38)
- **Lombok** (redução de boilerplate)
- **Jackson** (serialização JSON)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Logback** (logging)
- **Spring Actuator** (monitoramento e métricas)
- **Swagger/OpenAPI 3.0** (documentação de API)

---

## 4. Principais Endpoints REST

Não se aplica. O sistema é um orquestrador baseado em Camel que não expõe endpoints REST de negócio, apenas endpoints de monitoramento via Spring Actuator (health, metrics, prometheus) na porta 9090.

---

## 5. Principais Regras de Negócio

1. **Polling Periódico**: Realiza consultas periódicas ao BACEN conforme configuração (BACEN_PULL_PERIOD)
2. **Long Polling**: Utiliza técnica de long polling com timeout configurável (7000ms para GET)
3. **Processamento Multipart**: Processa mensagens no formato multipart/mixed com boundary
4. **Extração de Metadados**: Extrai informações como MsgDefIdr, CreDt, BizMsgIdr, certificados digitais e ISPB
5. **Cálculo de Delay**: Calcula o delay entre o timestamp do BACEN e o recebimento da mensagem
6. **Identificação de Tipo de Mensagem**: Identifica e processa mensagens PACS.002 (confirmação) e PACS.008 (transferência)
7. **Gerenciamento de Estado**: Mantém controle do PI-Pull-Next para continuidade do stream
8. **Tratamento de Status HTTP**: Processa códigos 200 (sucesso), 204 (sem conteúdo) e 410 (recurso removido)
9. **Auditoria Completa**: Registra headers, URLs, bodies de request/response para auditoria
10. **Retry com Limite**: Implementa retry com máximo de 2 tentativas em caso de falha
11. **Limpeza de Recursos**: Executa DELETE no BACEN após processamento bem-sucedido

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **AuditJson**: Contém informações completas de auditoria (headers HTTP, URLs, bodies, certificados, timestamps, tipos de mensagem, fluxo)
- **RouterConstants**: Mantém estado de navegação (bacennPath, pixGetUrlPath) e métricas de delay
- **DinamoProperties**: Configurações de conexão com HSM Dinamo e BACEN
- **EndpointProperties**: URLs e credenciais dos endpoints do BACEN
- **CredentialProperties**: Credenciais do HSM (host, porta, chaves, certificados)
- **IndicatorsMetrics**: Métricas de indicadores de performance
- **LiquidationMetrics**: Métricas de eventos de liquidação
- **SpiMetrics**: Agregador de métricas do SPI

**Relacionamentos:**
- DinamoProperties contém EndpointProperties e CredentialProperties
- AuditJson é propagado via Exchange properties entre processadores
- RouterConstants é singleton compartilhado entre rotas

---

## 7. Estruturas de Banco de Dados Lidas

Não se aplica. O sistema não acessa banco de dados diretamente.

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema não atualiza banco de dados diretamente.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | Leitura | /usr/etc/log/ (runtime) | Configuração de logging em ambientes des/uat/prd |
| application.yml | Leitura | Classpath resources | Configurações da aplicação (profiles, endpoints, credenciais) |
| libdinamo.so | Leitura | /opt/java/openjdk/lib/ | Biblioteca nativa do HSM Dinamo |
| libTacNDJavaLib.so | Leitura | /opt/java/openjdk/lib/ | Biblioteca Java do HSM Dinamo |
| libtacndlib.so | Leitura | /opt/java/openjdk/lib/ | Biblioteca auxiliar do HSM Dinamo |
| libtacndp11.so | Leitura | /opt/java/openjdk/lib/ | Biblioteca PKCS#11 do HSM Dinamo |

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas, apenas produz.

---

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Responsável | Descrição |
|--------------|------------|-------------------|-----------|
| business-spag-pixx-receber-mensagem-spi-canal-secundario | Google Cloud Pub/Sub | PublishReceivedMessagesRouter | Publica mensagens XML recebidas do BACEN para processamento downstream |
| business-spag-pixx-salvar-mensagem | Google Cloud Pub/Sub | PublishAuditMessagesRouter | Publica mensagens de auditoria em formato JSON |

---

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| **BACEN SPI (icom-sec-h.pi.rsfn.net.br:17522)** | API REST HTTPS | Sistema de Pagamentos Instantâneos do Banco Central - canal secundário para recebimento de mensagens PIX via long polling |
| **HSM Dinamo** | Biblioteca Nativa | Hardware Security Module para comunicação segura com BACEN utilizando certificados digitais e chaves criptográficas |
| **Google Cloud Pub/Sub** | Mensageria | Plataforma de mensageria para publicação de mensagens recebidas e auditoria |

**Detalhes da Integração BACEN:**
- Endpoint GET: `/api/v1/out/59588111/stream/start` (long polling)
- Endpoint DELETE: Para confirmação de recebimento
- Autenticação: Certificado digital via HSM Dinamo
- Formato: multipart/mixed com XMLs ISO 20022
- Timeout GET: 7000ms
- Timeout DELETE: 2000ms

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com uso de padrões (Processor, Router, Repository)
- Uso adequado de Apache Camel para orquestração
- Tratamento de exceções estruturado com retry
- Logging apropriado em pontos críticos
- Uso de Lombok para reduzir boilerplate
- Configuração externalizada via application.yml
- Documentação básica presente (README, Swagger)

**Pontos de Melhoria:**
- Classe `ReceiveMessageRepository` muito extensa (>300 linhas) com múltiplas responsabilidades
- Uso de singleton manual em `RouterConstants` (poderia ser gerenciado pelo Spring)
- Parsing de strings com regex poderia ser mais robusto (TratarBoundaryProcessor)
- Falta de testes unitários incluídos na análise
- Tratamento genérico de exceções em alguns pontos
- Hardcoded strings e magic numbers em alguns locais
- Falta de validação de entrada em alguns métodos
- Comentários em português misturados com código em inglês
- Algumas classes de domínio poderiam ter validações (Bean Validation)

---

## 14. Observações Relevantes

1. **Segurança Crítica**: O sistema lida com comunicação financeira crítica via HSM Dinamo, utilizando certificados digitais para autenticação mútua com o BACEN.

2. **Resiliência**: Implementa mecanismos de retry (2 tentativas) e tratamento de falhas para garantir continuidade do serviço.

3. **Observabilidade**: Expõe métricas via Prometheus e health checks via Actuator na porta 9090.

4. **Multi-ambiente**: Suporta profiles Spring (local, des, uat, prd) com configurações específicas.

5. **Containerização**: Dockerfile otimizado com OpenJ9 e bibliotecas nativas do Dinamo.

6. **Mensagens ISO 20022**: Processa mensagens no padrão internacional ISO 20022 (PACS.002, PACS.008).

7. **Timezone UTC**: Todo processamento de timestamps é feito em UTC para consistência.

8. **Long Polling**: Utiliza técnica de long polling com controle de estado (PI-Pull-Next) para recebimento contínuo de mensagens.

9. **Auditoria Completa**: Registra todos os detalhes de comunicação HTTP para fins de auditoria e troubleshooting.

10. **Dependência Externa**: Forte dependência da biblioteca proprietária Dinamo (tacndjavalib) versão 4.7.38.

11. **Performance**: Configurações de JVM otimizadas para uso de memória (MaxRAMPercentage=70%).

12. **Processamento Paralelo**: Utiliza split paralelo do Camel para processar múltiplas mensagens multipart simultaneamente.