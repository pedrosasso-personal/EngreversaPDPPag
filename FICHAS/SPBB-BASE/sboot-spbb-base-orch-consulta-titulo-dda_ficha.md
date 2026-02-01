# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema orquestrador responsável por processar e enviar mensagens de consulta de títulos DDA (Débito Direto Autorizado) para o SPB (Sistema de Pagamentos Brasileiro) através do Bacen. O sistema consome mensagens de um tópico Kafka, valida, gera XML no formato SPB, criptografa utilizando biblioteca Evaltec e envia para filas IBM MQ. Utiliza Apache Camel para orquestração de rotas e processamento assíncrono.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot, inicializa a aplicação |
| `ConsultaTituloDDAService` | Serviço principal que processa envio de mensagens SPB via Camel |
| `EncryptService` | Serviço de criptografia de mensagens usando biblioteca SPBSecJava (Evaltec) |
| `FeatureToggleService` | Gerencia feature toggles (ex: troca de servidores EVAL) |
| `MensagemSPBConsumer` | Listener Kafka que consome mensagens do tópico de consulta de títulos DDA |
| `MensagemSPBController` | Controller REST para publicação manual de mensagens (apenas ambientes não-produtivos) |
| `DdaRouterJMSRepositoryImpl` | Implementação de envio de mensagens para filas IBM MQ |
| `RecepcaoMensagemRouter` | Rota Camel principal que orquestra todo o fluxo de processamento |
| `ValidacaoMensagemRouter` | Rota Camel para validação de campos obrigatórios |
| `GeracaoXMLSPBRouter` | Rota Camel para geração de XML no formato SPB |
| `CriptografiaMensagemRouter` | Rota Camel para criptografia de mensagens |
| `EnvioMesagemSPBRouter` | Rota Camel para envio final à fila IBM MQ |
| `ConversaoMensagemMapper` | Mapper MapStruct para conversão de mensagens Avro para domínio Bacen |
| `CamelContextWrapper` | Wrapper do contexto Camel para gerenciamento de rotas |

---

## 3. Tecnologias Utilizadas

- **Framework:** Spring Boot 2.x
- **Orquestração:** Apache Camel 3.x
- **Mensageria:** Apache Kafka (Confluent Cloud), IBM MQ
- **Serialização:** Apache Avro, Jackson
- **Criptografia:** SPBSecJava (Evaltec) versão 1.0.6
- **Mapeamento:** MapStruct
- **Feature Toggle:** ConfigCat (via biblioteca arqt-base-feature-toggle)
- **Observabilidade:** Spring Actuator, Micrometer, Prometheus, OpenTelemetry
- **Documentação API:** SpringDoc OpenAPI (Swagger)
- **Logging:** Logback com formato JSON
- **Build:** Maven
- **Container:** Docker
- **Infraestrutura:** Google Cloud Platform (GCP), Kubernetes/OpenShift
- **Java:** JDK 11

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/publicarMensagem` | `MensagemSPBController` | Publica mensagem no tópico Kafka (apenas não-produtivo) |
| POST | `/v1/publicarMensagem/sincrona` | `MensagemSPBController` | Processa mensagem de forma síncrona via Camel (apenas não-produtivo) |
| GET | `/actuator/health` | Spring Actuator | Health check da aplicação |
| GET | `/actuator/metrics` | Spring Actuator | Métricas da aplicação |
| GET | `/actuator/prometheus` | Spring Actuator | Métricas no formato Prometheus |
| GET | `/swagger-ui.html` | SpringDoc | Documentação Swagger (apenas não-produtivo) |

---

## 5. Principais Regras de Negócio

1. **Validação de Campos Obrigatórios:** Verifica se todos os campos essenciais da mensagem estão preenchidos (sigla origem, código movimento, data inclusão, código mensagem SPB, código instituição, versão catálogo, JSON mensagem)

2. **Geração de Número de Operação (NUOp):** Gera identificador único composto por: ISPB emissor (59588111) + data atual (yyMMdd) + código fixo (98) + últimos 7 dígitos do timestamp em milissegundos

3. **Identificação de Instituição:** Suporta duas instituições: Banco Votorantim (código 655, ISPB 59588111) e Banco BV (código 413, ISPB 01858774)

4. **Domínio do Sistema:** Utiliza domínio fixo SPB02 para comunicação com o Bacen

5. **Criptografia com Retry:** Implementa retry automático (3 tentativas) em caso de falha de conexão com servidores EVAL de criptografia

6. **Troca Dinâmica de Servidores EVAL:** Permite alternar entre servidores antigos e novos via feature toggle sem necessidade de redeploy

7. **Reconexão Automática:** Gerencia pool de conexões com servidores EVAL, reconectando automaticamente em caso de falha

8. **Tratamento de Erros de Criptografia:** Diferencia erros de conexão (que permitem retry) de erros de processamento (que rejeitam a mensagem)

9. **Envio para Fila Específica por Instituição:** Roteia mensagens para filas IBM MQ específicas baseado no código da instituição

10. **Processamento Assíncrono:** Utiliza acknowledgment manual do Kafka para garantir processamento completo antes de confirmar consumo

---

## 6. Relação entre Entidades

**ConsultaTitulosDDA (Avro):**
- Entidade principal que representa a mensagem de consulta de títulos DDA
- Campos: nmSiglaOrigem, cdMovimentoOrigem, dtInclusao, cdMensagemSPB, cdCompeInstituicao, nuVersaoCatalogo, jsMensagem, controleSPB (opcional)

**MensagemBacen:**
- Representa o cabeçalho BCMSG da mensagem SPB
- Campos: identificadorEmissor, identificadorDestinatario, dominioDoSistema, nuOp
- Relacionamento: Gerada a partir de ConsultaTitulosDDA

**MensagemCriptografiaRequest:**
- Representa requisição de criptografia
- Campos: domain, identificadorEmissor, identificadorDestinatario, mensagem
- Relacionamento: Criada a partir de MensagemBacen + XML gerado

**MensagemEnvioSPBRequest:**
- Representa mensagem final para envio à fila
- Campos: ispb, mensagem (byte[]), nuOp
- Relacionamento: Criada após criptografia bem-sucedida

**Fluxo de Transformação:**
ConsultaTitulosDDA → MensagemBacen → XML → MensagemCriptografiaRequest → byte[] criptografado → MensagemEnvioSPBRequest → Fila IBM MQ

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `logback-spring.xml` | leitura | Configuração Logback | Arquivo de configuração de logs em formato JSON |
| `application.yml` | leitura | Spring Boot | Configurações da aplicação por ambiente |
| `application-local.yml` | leitura | Spring Boot | Configurações para ambiente local |
| `EnvioMensagemSPB.avsc` | leitura | Maven Avro Plugin | Schema Avro para geração de classes |
| `openapi.yaml` | leitura | SpringDoc | Especificação OpenAPI da API |
| `layers.xml` | leitura | Spring Boot Layertools | Configuração de camadas para otimização de imagem Docker |

---

## 10. Filas Lidas

**Kafka:**
- **Tópico:** `spbb-base-consulta-titulos-dda`
- **Formato:** Apache Avro (schema registry Confluent)
- **Consumer Group:** `sboot-spbb-base-orch-consulta-titulo-dda`
- **Classe Consumidora:** `MensagemSPBConsumer`
- **Descrição:** Consome mensagens de consulta de títulos DDA para processamento e envio ao SPB

---

## 11. Filas Geradas

**IBM MQ:**

| Fila | Ambiente | Queue Manager | Descrição |
|------|----------|---------------|-----------|
| `QL.SPAG.BANCO_LIQUIDANTE_ER_RECEBIMENTO_REQ.INT` | DES | QM.ATA.01 | Fila de envio para ambiente de desenvolvimento |
| `QR.REQ.59588111.17423302.05` | UAT/PRD | QM.59588111.01 | Fila de envio para ambientes de homologação e produção |

**Classe Responsável:** `DdaRouterJMSRepositoryImpl`

**Formato:** Mensagem criptografada em byte array

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **Servidores EVAL (Evaltec)** | TCP/IP | Servidores de criptografia SPB. Suporta dois conjuntos de servidores (antigo e novo) com troca via feature toggle. Portas: 10000. Ambientes: mor-spbuat1.bvnet.bv (antigo), srv-evaluat01/02.bvnet.bv (novo) |
| **Confluent Cloud Kafka** | Mensageria | Cluster Kafka gerenciado para consumo de mensagens. Autenticação SASL/SSL |
| **Confluent Schema Registry** | Schema Management | Registro de schemas Avro. Autenticação via API Key/Secret |
| **IBM MQ** | Mensageria | Filas IBM MQ para envio de mensagens ao SPB/Bacen |
| **ConfigCat** | Feature Toggle | Serviço de gerenciamento de feature flags |
| **SPB/Bacen** | Sistema Financeiro | Sistema de Pagamentos Brasileiro (destino final das mensagens via IBM MQ) |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com uso de padrões como Repository, Service e Processor
- Utilização adequada de Apache Camel para orquestração de fluxos complexos
- Implementação de retry e tratamento de erros de conexão
- Uso de MapStruct para mapeamento de objetos
- Testes unitários presentes para a maioria das classes
- Configuração adequada de observabilidade (logs estruturados, métricas)
- Feature toggle para troca de servidores sem redeploy
- Uso de Avro para serialização eficiente

**Pontos de Melhoria:**
- Código de criptografia (`EncryptService`) muito complexo e com lógica de reconexão misturada
- Uso de `@SneakyThrows` em `ExceptionProcessor` pode mascarar exceções
- Classe `CodigoErro` com mapa estático poderia ser enum
- Falta de documentação JavaDoc em classes críticas
- Alguns processadores Camel poderiam ser simplificados
- Configuração de conexão com servidores EVAL poderia ser mais clara
- Testes de integração ausentes
- Algumas classes de configuração muito acopladas
- Uso de `synchronized` em singleton pode causar contenção

---

## 14. Observações Relevantes

1. **Arquitetura de Transição:** O sistema é descrito como arquitetura de transição até o SPB ficar pronto, com previsão de descontinuação para final de 2024

2. **Ambientes:** Suporta três ambientes principais (DES, UAT, PRD) com configurações distintas de servidores EVAL e filas IBM MQ

3. **Segurança:** Implementa autenticação OAuth2/JWT via API Gateway, com validação de tokens

4. **Monitoramento:** Expõe métricas Prometheus e health checks na porta 9090

5. **Docker Multi-layer:** Utiliza estratégia de camadas Docker otimizada para reduzir tempo de build e tamanho de imagem

6. **Profile Específico:** Controller REST só está ativo em ambientes não-produtivos (`@Profile("!prd")`)

7. **Retry Configurável:** Implementa retry com backoff exponencial (1s inicial, multiplicador 1.5) para falhas de criptografia

8. **ISPB CIP:** Utiliza ISPB fixo 17423302 (CIP - Câmara Interbancária de Pagamentos) como destinatário

9. **Versionamento de Catálogo:** Suporta diferentes versões do catálogo de mensagens do Bacen (ex: 5.07)

10. **Infraestrutura como Código:** Possui arquivo `infra.yml` com definições completas de deployment no Kubernetes/OpenShift