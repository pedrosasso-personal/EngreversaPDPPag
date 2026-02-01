# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema orquestrador responsável por receber mensagens PIX do canal secundário BVSA (Banco Votorantim S.A.) através do BACEN (Banco Central do Brasil). O sistema realiza polling periódico no endpoint do BACEN utilizando comunicação segura via HSM Dinamo, processa as mensagens recebidas (PACS.002 e PACS.008), e as publica em filas do Google Cloud Pub/Sub para processamento posterior. Também gera mensagens de auditoria para rastreabilidade das operações.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal Spring Boot que inicializa a aplicação |
| **ReceiveBvsaMessagesRouter** | Rota Camel que agenda polling periódico para buscar mensagens do BACEN |
| **SendMessagesRouter** | Rota Camel que processa e distribui mensagens recebidas |
| **PublishReceivedMessagesRouter** | Rota Camel que publica mensagens recebidas no tópico de processamento |
| **PublishAuditMessagesRouter** | Rota Camel que publica mensagens de auditoria |
| **ReceiveMessageBVSARepositoryAdapter** | Adaptador que implementa a comunicação com BACEN via Dinamo |
| **ReceiveMessageRepository** | Classe abstrata com lógica de long polling e comunicação HTTP com BACEN |
| **TratarBoundaryProcessor** | Processa mensagens multipart, extrai XMLs e popula dados de auditoria |
| **PrepareToPublishReceivedMessageProcessor** | Prepara headers para publicação de mensagens recebidas |
| **PrepareToPublishAuditMessageProcessor** | Serializa objeto de auditoria em JSON |
| **PixProcessor** | Processador auxiliar para limpar estado após processamento |
| **AuditJson** | Modelo de dados para auditoria de mensagens |
| **DinamoProperties** | Propriedades de configuração do HSM Dinamo e endpoints BACEN |
| **RouterConstants** | Constantes e estado compartilhado entre rotas |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.7.2** - Framework base da aplicação
- **Apache Camel** - Framework de integração e orquestração de rotas
- **Google Cloud Pub/Sub** - Sistema de mensageria para publicação de eventos
- **Dinamo HSM (v4.7.38)** - Hardware Security Module para comunicação segura com BACEN
- **Java 11** - Linguagem de programação
- **Maven** - Gerenciamento de dependências e build
- **Docker** - Containerização da aplicação
- **Kubernetes** - Orquestração de containers (infra-as-code)
- **Lombok** - Redução de boilerplate code
- **Jackson** - Serialização/deserialização JSON
- **SLF4J/Logback** - Framework de logging
- **Spring Actuator** - Monitoramento e health checks

---

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema orquestrador baseado em Apache Camel que não expõe endpoints REST de negócio, apenas endpoints de monitoramento via Spring Actuator (health, metrics, prometheus) na porta 9090.

---

## 5. Principais Regras de Negócio

1. **Polling Periódico**: Sistema realiza polling configurável (padrão 2000ms) para buscar mensagens do BACEN
2. **Long Polling com Stream**: Utiliza endpoint `/stream/start` do BACEN para iniciar stream de mensagens
3. **Processamento Multipart**: Mensagens retornam em formato multipart/mixed com boundary, sendo necessário split e parsing
4. **Extração de Metadados XML**: Extrai informações como MsgDefIdr, CreDt, BizMsgIdr, certificado digital, ISPB do XML
5. **Identificação de Tipo de Mensagem**: Diferencia entre PACS.002 (resposta) e PACS.008 (transferência) para extração correta de EndToEndId e InstructionId
6. **Controle de Fluxo com PI-Pull-Next**: Utiliza header `PI-Pull-Next` retornado pelo BACEN para controlar próxima requisição
7. **Tratamento de Status HTTP**: Processa códigos 200 (sucesso com mensagens), 204 (sem mensagens), 410 (recurso expirado)
8. **Delete de Mensagens**: Após processamento, realiza DELETE no BACEN para confirmar recebimento
9. **Auditoria Completa**: Registra request/response headers, URLs, bodies, timestamps, certificados e identificadores de mensagem
10. **Timeout Configurável**: Timeouts distintos para GET (7000ms) e DELETE (2000ms)
11. **Cálculo de Delay**: Calcula tempo entre recebimento do BACEN e processamento local
12. **Tratamento de Exceções**: Retry configurado (2 tentativas) para falhas de comunicação

---

## 6. Relação entre Entidades

**Entidades de Domínio:**

- **AuditJson**: Entidade principal de auditoria contendo todos os metadados da transação
  - Relaciona-se com informações de request/response HTTP
  - Contém dados extraídos do XML (certificado, ISPB, tipo de mensagem, EndToEndId, InstructionId)

- **DinamoProperties**: Configuração hierárquica
  - Contém **EndpointProperties** (URLs e credenciais BACEN)
  - Contém **CredentialProperties** (configuração HSM Dinamo)

- **RouterConstants**: Estado compartilhado entre rotas
  - Mantém path do BACEN para próxima requisição
  - Armazena delays calculados

- **SpiMetrics**: Métricas de processamento
  - Contém lista de **IndicatorsMetrics** (indicadores de performance)
  - Contém lista de **LiquidationMetrics** (eventos de liquidação)

**Fluxo de Dados:**
```
BACEN → ReceiveMessageRepository → RouterConstants → TratarBoundaryProcessor → AuditJson
                                                    ↓
                                              XML Message → Pub/Sub Topics
```

---

## 7. Estruturas de Banco de Dados Lidas

Não se aplica. O sistema não realiza leitura direta de banco de dados.

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema não realiza operações diretas em banco de dados.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | Leitura | /usr/etc/log/ (runtime) | Arquivo de configuração de logs montado via ConfigMap |
| application.yml | Leitura | src/main/resources | Arquivo de configuração da aplicação Spring Boot |
| libdinamo.so | Leitura | /opt/java/openjdk/lib/ | Biblioteca nativa do HSM Dinamo |
| libTacNDJavaLib.so | Leitura | /opt/java/openjdk/lib/ | Biblioteca Java do HSM Dinamo |
| libtacndlib.so | Leitura | /opt/java/openjdk/lib/ | Biblioteca nativa TacND |
| libtacndp11.so | Leitura | /opt/java/openjdk/lib/ | Biblioteca PKCS#11 do Dinamo |
| cacerts | Leitura | /opt/java/openjdk/lib/security/ | Certificados SSL/TLS montados via Secret |

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas, apenas publica.

---

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Responsável | Descrição |
|--------------|-----------|-------------------|-----------|
| business-spag-pixx-receber-mensagem-spi-canal-secundario | Google Cloud Pub/Sub | PublishReceivedMessagesRouter | Fila para mensagens PIX recebidas do BACEN (PACS.002 e PACS.008) para processamento posterior |
| business-spag-pixx-salvar-mensagem | Google Cloud Pub/Sub | PublishAuditMessagesRouter | Fila para mensagens de auditoria contendo logs completos de request/response |

---

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição | Classe Responsável |
|-----------------|------|-----------|-------------------|
| **BACEN - Banco Central** | API REST HTTPS | Sistema de Pagamentos Instantâneos (SPI/PIX). Endpoints: `/api/v1/out/01858774/stream/start` (GET para receber mensagens) e DELETE para confirmar recebimento. Comunicação via mTLS com certificados gerenciados pelo HSM Dinamo | ReceiveMessageRepository |
| **HSM Dinamo** | API Nativa | Hardware Security Module para gerenciamento de chaves criptográficas e certificados digitais. Porta 4433. Utilizado para estabelecer conexão segura com BACEN | ReceiveMessageRepository, Dinamo API |
| **Google Cloud Pub/Sub** | Mensageria | Sistema de mensageria para publicação assíncrona de mensagens recebidas e auditoria | PublishReceivedMessagesRouter, PublishAuditMessagesRouter |

**Detalhes da Integração BACEN:**
- Protocolo: HTTPS com mTLS
- Formato: Multipart/Mixed com XMLs ISO20022
- Autenticação: Certificado digital via HSM Dinamo
- Timeout GET: 7000ms (configurável)
- Timeout DELETE: 2000ms (configurável)
- Ambientes: Homologação (porta 17522) e Produção (porta 17422)

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Uso adequado de padrões arquiteturais (Ports & Adapters, Repository)
- Separação clara de responsabilidades entre rotas Camel
- Tratamento de exceções estruturado com retry
- Uso de Lombok para reduzir boilerplate
- Configuração externalizada via application.yml
- Logging adequado em pontos críticos

**Pontos Negativos:**
- **Código legado com práticas questionáveis**: Uso de variáveis estáticas mutáveis em `RouterConstants` (DELAY_GET_BACEN, DELAY_POOL_NEXT, DELAY_GET_DINAMO) que podem causar problemas de concorrência
- **Parsing manual de XML com Regex**: A classe `TratarBoundaryProcessor` usa regex para extrair dados do XML ao invés de parser XML adequado (SAX, DOM, JAXB), tornando o código frágil e difícil de manter
- **Tratamento genérico de exceções**: Múltiplos blocos catch com `Exception.class` que mascaram problemas específicos
- **Falta de testes unitários nos arquivos enviados**: Embora existam testes no projeto, não foram incluídos na análise
- **Acoplamento com infraestrutura**: Dependência direta de bibliotecas nativas do Dinamo dificulta testes
- **Falta de documentação inline**: Métodos complexos como `longPolling` e `getBacenDate` carecem de JavaDoc
- **Magic numbers e strings**: Valores hardcoded como "200", "204", "410", timeouts, etc.
- **Responsabilidade excessiva**: `ReceiveMessageRepository` faz muitas coisas (HTTP, parsing, controle de estado)
- **Singleton implícito**: Método `getInstance()` em `ReceiveMessageRepository` implementa singleton de forma não thread-safe

**Recomendações:**
1. Refatorar parsing XML para usar JAXB ou Jackson XML
2. Eliminar estado mutável estático
3. Criar constantes para códigos HTTP e strings mágicas
4. Adicionar JavaDoc em métodos públicos
5. Melhorar tratamento de exceções com tipos específicos
6. Considerar uso de Circuit Breaker para chamadas ao BACEN

---

## 14. Observações Relevantes

1. **Segurança Crítica**: Sistema lida com transações financeiras PIX, utilizando HSM para gerenciamento de certificados digitais e comunicação mTLS com BACEN

2. **Dependência de Bibliotecas Nativas**: Requer bibliotecas .so do Dinamo HSM (versão 4.7.38) instaladas no container, o que pode dificultar portabilidade

3. **Ambientes Múltiplos**: Configuração para DES, UAT e PRD com diferentes endpoints BACEN (homologação vs produção) e credenciais HSM distintas

4. **Monitoramento**: Expõe métricas Prometheus na porta 9090 para observabilidade

5. **Resiliência**: Implementa retry (2 tentativas) para falhas de comunicação e tratamento específico para diferentes códigos HTTP do BACEN

6. **Performance**: Polling configurável permite ajuste de throughput vs latência. Timeout de 7 segundos no GET pode impactar SLA em cenários de alta carga

7. **Auditoria Completa**: Registra request/response completos incluindo headers, bodies, certificados e timestamps para compliance e troubleshooting

8. **Processamento Assíncrono**: Desacopla recepção de mensagens do processamento através de Pub/Sub, permitindo escalabilidade independente

9. **ISPB Identificado**: Sistema processa mensagens para ISPB 01858774 (Banco Votorantim)

10. **Tipos de Mensagem PIX**: Suporta PACS.002 (Payment Status Report) e PACS.008 (Customer Credit Transfer) do padrão ISO20022

11. **Infraestrutura como Código**: Deployment automatizado via Kubernetes com configuração em `infra.yml` incluindo probes, resources e secrets

12. **Service Account**: Utiliza KSA (Kubernetes Service Account) `ksa-spag-spib-29946` para acesso a recursos GCP