# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-spag-spib-orch-receber-mensagem-bvsa** é um serviço stateless desenvolvido em Java com Spring Boot, responsável por receber mensagens do Sistema de Pagamentos Instantâneos (SPI/PIX) do Banco Central do Brasil. O componente atua como orquestrador que:

- Realiza polling periódico no endpoint do Banco Central (BACEN) para buscar mensagens PIX
- Utiliza HSM (Hardware Security Module) Dinamo para comunicação segura com certificados digitais
- Processa mensagens nos formatos PACS.002, PACS.004 e PACS.008 (padrões ISO 20022)
- Publica mensagens recebidas em tópicos do Google Cloud Pub/Sub para processamento posterior
- Gera métricas de liquidação e indicadores de performance
- Registra auditoria de todas as operações realizadas

O sistema opera em modo contínuo (timer), buscando mensagens a cada 1ms, processando-as em paralelo e garantindo a rastreabilidade completa do fluxo.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal que inicializa a aplicação Spring Boot |
| `ReceberMensagemRouter` | Roteador Apache Camel que orquestra o fluxo de recebimento, processamento e publicação de mensagens |
| `ReceberMensagemRepositoryImpl` | Implementação da comunicação com o HSM Dinamo e Banco Central (GET/DELETE de mensagens PIX) |
| `ReceberMensagemProducerRepositoryImpl` | Implementação da publicação de mensagens nos tópicos do Google Pub/Sub |
| `TratarBoundaryProcessor` | Processador que extrai e trata o boundary multipart, parseando headers e XML das mensagens |
| `EndMetricasProcessor` | Processador que gera métricas de liquidação e indicadores de performance |
| `PixProcessor` | Processador auxiliar para limpeza de estado em caso de erro |
| `RouterConstants` | Classe singleton que mantém estado compartilhado (paths, delays) entre execuções |
| `PubSubProperties` | Configuração dos tópicos e subscrições do Google Pub/Sub |
| `AuditJson` | Modelo de dados para auditoria das mensagens processadas |
| `SpiMetrics`, `LiquidationMetrics`, `IndicatorsMetrics` | Modelos de dados para métricas de liquidação e indicadores |

## 3. Tecnologias Utilizadas

- **Java 11** - Linguagem de programação
- **Spring Boot 2.x** - Framework base da aplicação
- **Apache Camel 3.0.1** - Framework de integração e roteamento de mensagens
- **Google Cloud Pub/Sub** - Sistema de mensageria para publicação de eventos
- **Dinamo HSM (TacNDJavaLib 4.1.6)** - Hardware Security Module para comunicação segura com certificados
- **Lombok** - Redução de boilerplate code
- **Springfox Swagger 3.0.0** - Documentação de APIs
- **Micrometer/Prometheus** - Métricas e monitoramento
- **Logback** - Logging com formato JSON
- **JUnit 5 + Mockito** - Testes unitários
- **Maven** - Gerenciamento de dependências e build
- **Docker** - Containerização da aplicação
- **OpenShift/Kubernetes** - Plataforma de execução (GCP)

## 4. Principais Endpoints REST

Não se aplica. O sistema não expõe endpoints REST para consumo externo. Trata-se de um componente batch/streaming que opera via timer do Apache Camel, realizando polling contínuo no Banco Central.

## 5. Principais Regras de Negócio

1. **Polling Contínuo**: Executa busca de mensagens a cada 1ms no endpoint do Banco Central via HSM Dinamo
2. **Processamento Multipart**: Trata respostas HTTP multipart/mixed com boundary, extraindo múltiplas mensagens XML
3. **Validação de Status HTTP**: Aceita apenas status 200 (mensagens disponíveis) ou 204 (sem mensagens) do BACEN
4. **Controle de Fluxo PI-Pull-Next**: Mantém estado do próximo endpoint a ser consultado via header `PI-Pull-Next`
5. **Processamento Paralelo**: Divide mensagens por boundary e processa em paralelo usando split do Camel
6. **Tipos de Mensagem Suportados**: PACS.002 (confirmação), PACS.004 (devolução) e PACS.008 (transferência)
7. **Cálculo de Métricas**: Calcula delays entre disponibilização BACEN e recebimento (DELAY_GET_BACEN)
8. **Geração de Auditoria**: Registra headers HTTP, corpo da mensagem, certificados e timestamps
9. **Métricas de Liquidação**: Gera eventos de timeline (tdis, tlei) e indicadores de execução (tipo 003)
10. **Tratamento de Erros**: Em caso de falha, executa DELETE no endpoint para liberar fila do BACEN
11. **Retry Policy**: Até 2 tentativas de reprocessamento em caso de exceção
12. **Extração de Metadados**: Extrai EndToEndId, InstructionId, ISPB, certificados e timestamps do XML

## 6. Relação entre Entidades

**Entidades de Domínio:**

- `AuditJson`: Contém dados completos de auditoria (request/response HTTP, metadados da mensagem PIX)
- `SpiMetrics`: Agregador que contém listas de `LiquidationMetrics` e `IndicatorsMetrics`
- `LiquidationMetrics`: Eventos de timeline da liquidação (tdis, tlei) com EndToEndId, timestamps e tipo de mensagem
- `IndicatorsMetrics`: Indicadores de performance (tempo de execução, tipo 003)
- `RouterConstants`: Singleton que mantém estado compartilhado (paths do BACEN, delays calculados)

**Relacionamentos:**
- `SpiMetrics` 1:N `LiquidationMetrics` (eventos de liquidação)
- `SpiMetrics` 1:N `IndicatorsMetrics` (indicadores de performance)
- Todas as entidades são DTOs simples sem relacionamento JPA (não há persistência local)

## 7. Estruturas de Banco de Dados Lidas

Não se aplica. O sistema não realiza leitura direta de banco de dados. Toda a entrada de dados ocorre via API REST do Banco Central.

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema não realiza escrita direta em banco de dados. A persistência de dados ocorre de forma assíncrona através da publicação em tópicos Pub/Sub, sendo responsabilidade de outros componentes downstream.

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `logback-spring.xml` | Leitura | `/usr/etc/log` (runtime) | Configuração de logging em formato JSON para stdout |
| `application.yml` | Leitura | Classpath resources | Configurações da aplicação (URLs, timeouts, credenciais) |
| Bibliotecas `.so` do Dinamo | Leitura | `/opt/java/openjdk/lib` | Bibliotecas nativas do HSM Dinamo (libdinamo, libTacNDJavaLib, libtacndlib, libtacndp11) |

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas. A entrada de dados ocorre via polling HTTP no endpoint do Banco Central.

## 11. Filas Geradas

O sistema publica mensagens em três tópicos do Google Cloud Pub/Sub:

| Nome do Tópico | Ambiente | Descrição |
|----------------|----------|-----------|
| `business-spag-pixx-receber-mensagem-spi-bvsa` | Todos | Mensagens PIX recebidas do BACEN para processamento downstream |
| `business-spag-pixx-metricas-liquidacao` | Todos | Métricas de liquidação e indicadores de performance |
| `business-spag-pixx-salvar-mensagem` | Todos | Dados de auditoria completos das mensagens processadas |

**Headers adicionados:**
- `rabbitmq.receiveDateTimePacs008`: Timestamp UTC de recebimento da mensagem (formato ISO)

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **Banco Central (BACEN) - SPI** | API REST HTTPS | Endpoint de recebimento de mensagens PIX via protocolo PI-Pull. URLs: `https://icom.pi.rsfn.net.br:16422` (PRD), `https://icom-h.pi.rsfn.net.br:16522` (UAT/DES) |
| **HSM Dinamo** | Biblioteca Nativa | Hardware Security Module para comunicação segura com certificados digitais. Hosts: `hsmpixspib.bvnet.bv:4433` (PRD), `hsmcertpixuat.bvnet.bv:4433` (UAT/DES) |
| **Google Cloud Pub/Sub** | Mensageria Cloud | Publicação de mensagens, métricas e auditoria. Projetos: `bv-atacado-cib-pix-prd`, `bv-atacado-cib-pix-uat`, `bv-atacado-cib-pix-des` |

**Detalhes da integração BACEN:**
- Método GET: `/api/v1/out/01858774/stream/start` (timeout: 7s em PRD/UAT)
- Método DELETE: Mesmo endpoint (timeout: 2s)
- Autenticação: Certificado digital via HSM Dinamo
- Headers: `Host`, `Accept: multipart/mixed`, `Accept-Encoding: gzip`
- Resposta: Multipart/mixed com boundary contendo XMLs ISO 20022

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades em camadas (application, domain, infrastructure)
- Uso adequado de interfaces (ports) para abstrair repositórios
- Cobertura de testes unitários presente
- Uso de Lombok para reduzir boilerplate
- Configuração externalizada via application.yml
- Logs estruturados em JSON

**Pontos Negativos:**
- **Singleton com estado mutável**: `RouterConstants` é um singleton com campos estáticos mutáveis (`DELAY_GET_BACEN`, `DELAY_POOL_NEXT`), o que pode causar problemas de concorrência e dificulta testes
- **Acoplamento forte com Dinamo**: A classe `ReceberMensagemRepositoryImpl` está fortemente acoplada à biblioteca do HSM, dificultando testes e manutenção
- **Processamento de XML via regex**: Uso de regex para parsing de XML (`Pattern.compile`) é frágil e propenso a erros; deveria usar parser XML adequado
- **Tratamento de exceções genérico**: Captura de `Exception` genérica em vários pontos, mascarando possíveis problemas
- **Falta de validação de entrada**: Pouca validação dos XMLs recebidos antes do processamento
- **Código comentado**: Presença de código comentado em testes (`CamelContextWrapperTest`)
- **Hardcoded strings**: Muitas strings hardcoded (tags XML, nomes de headers) que poderiam ser constantes
- **Complexidade ciclomática alta**: Métodos como `process()` em `EndMetricasProcessor` e `TratarBoundaryProcessor` são extensos e complexos
- **Falta de documentação JavaDoc**: Classes e métodos públicos sem documentação adequada
- **Configuração de timeout zero em DES/QA**: Timeouts configurados como 0 em alguns ambientes pode causar comportamento inesperado

**Recomendações:**
1. Refatorar `RouterConstants` para usar ThreadLocal ou contexto do Camel
2. Introduzir parser XML robusto (JAXB, Jackson XML)
3. Adicionar validação de schema XSD para mensagens PIX
4. Quebrar métodos grandes em métodos menores e mais testáveis
5. Adicionar JavaDoc nas interfaces públicas
6. Remover código comentado e strings hardcoded
7. Implementar circuit breaker para chamadas ao BACEN

## 14. Observações Relevantes

1. **Criticidade**: Sistema crítico para operação PIX do banco, operando 24x7 com alta disponibilidade
2. **Performance**: Polling a cada 1ms pode gerar carga significativa; considerar backoff exponencial quando não há mensagens
3. **Segurança**: Uso de HSM garante segurança na comunicação com BACEN, mas credenciais estão em variáveis de ambiente
4. **Observabilidade**: Boa instrumentação com métricas Prometheus e logs estruturados, facilitando troubleshooting
5. **Resiliência**: Implementa retry e tratamento de erro com DELETE para liberar fila do BACEN
6. **Escalabilidade**: Processamento paralelo de mensagens permite throughput elevado
7. **Conformidade**: Implementa padrões ISO 20022 para mensagens PIX conforme especificação do Banco Central
8. **Ambientes**: Suporta múltiplos ambientes (DES, QA, UAT, PRD) com configurações específicas
9. **Dependência Externa**: Fortemente dependente da disponibilidade do HSM Dinamo e conectividade com BACEN
10. **Timezone**: Todo processamento em UTC, garantindo consistência temporal
11. **Certificados**: Usa cadeia de certificados específica para PIX armazenada no HSM
12. **ISPB**: Código ISPB do banco (01858774) hardcoded na URL do BACEN