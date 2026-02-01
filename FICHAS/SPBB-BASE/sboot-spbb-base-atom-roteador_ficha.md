# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-spbb-base-atom-roteador** é um serviço atômico desenvolvido em Java com Spring Boot, responsável por rotear mensagens de consulta de boletos para o Sistema de Pagamentos Brasileiro (SPB). O sistema recebe mensagens via fila IBM MQ, criptografa utilizando o serviço EVALCryptoSPB, gera mensagens no formato DDA0110 (padrão SPB) e as envia para o CIP (Câmara Interbancária de Pagamentos). Também expõe endpoints REST para consulta de boletos por código de barras.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal que inicializa a aplicação Spring Boot com suporte a JMS, Feature Toggle e OAuth2 |
| `RoteadorService` | Serviço principal que orquestra a consulta de boletos, validação, geração de mensagens DDA0110 e envio para filas |
| `EncryptService` | Responsável pela criptografia de mensagens utilizando a biblioteca SPBSecJava e comunicação com servidores EVAL |
| `RoteadorListener` | Listener JMS que consome mensagens da fila de entrada e processa consultas de boletos |
| `ConsultaBoletoController` | Controller REST que expõe endpoint para consulta de boletos por código de barras |
| `MensagemUtil` | Utilitário para geração de mensagens XML no formato DDA0110 do SPB |
| `JmsConfiguration` | Configuração de conexões JMS com IBM MQ, incluindo reconnect e cache |
| `GlobalUtils` | Utilitários globais incluindo geração de número de operação (NuOp) |
| `DadosUtils` | Utilitários para manipulação de dados e conexões |
| `FilaUtils` | Utilitários para identificação e manipulação de filas por ISPB |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Spring JMS** (integração com filas)
- **IBM MQ** (middleware de mensageria)
- **SPBSecJava 1.0.6** (biblioteca de criptografia do SPB)
- **Spring Security OAuth2** (autenticação e autorização)
- **Springfox/Swagger 3.0.0** (documentação de APIs)
- **Spring Actuator + Prometheus** (métricas e monitoramento)
- **Logback** (logging)
- **Feature Toggle (ConfigCat)** (gerenciamento de features)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **JUnit 5 + Mockito** (testes)
- **Lombok** (redução de boilerplate)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/consultaboleto` | `ConsultaBoletoController` | Consulta boleto por código de barras (44 dígitos) |
| GET | `/v1/inicia` | `IniciaController` | Endpoint de inicialização/health check |
| GET | `/v1/verifica` | `VerificaController` | Endpoint de verificação com múltiplas opções (versão, NuOp, conexão) |
| GET | `/actuator/health` | Spring Actuator | Health check da aplicação |
| GET | `/actuator/prometheus` | Spring Actuator | Métricas no formato Prometheus |
| GET | `/swagger-ui.html` | Springfox | Documentação interativa da API |

---

## 5. Principais Regras de Negócio

1. **Validação de Boleto**: Boletos devem ter 68 caracteres (linha digitável) ou 44 caracteres (código de barras)
2. **Geração de NuOp**: Número de operação único gerado com prefixo aleatório (6-7) + sequencial embaralhado de 8 dígitos
3. **Prevenção de Colisão**: NuOp com prefixo "8" não pode iniciar com "9" para evitar colisão com baixa de boleto
4. **Geração de NumCtrlPart**: Para código de barras, gera "DDA" + data (yyyyMMdd) + NuOp; para boleto completo, extrai da posição 4-24
5. **Horário de Processamento DDA**: Mensagens DDA0110 consideram D-1 se processadas antes das 06:00 (com janela de 05:50 a 06:00)
6. **Criptografia Obrigatória**: Todas as mensagens enviadas ao SPB devem ser criptografadas via SPBSecJava
7. **Retry de Criptografia**: Até 2 tentativas com backoff de 500ms em caso de falha
8. **Roteamento por ISPB**: Mensagens são roteadas para filas específicas baseadas no ISPB (BV: 59588111, CIP: 17423302)
9. **Reconexão Automática**: Conexões JMS possuem reconexão automática configurada
10. **Feature Toggle**: Funcionalidades podem ser habilitadas/desabilitadas via ConfigCat

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **Mensagem**: Representa uma mensagem genérica com campo `dadosMensagem`
- **TipoBoletoEnum**: Enumeração que define tipos de boleto (CODIGO_BARRAS, BOLETO)

**Relacionamentos:**
- O sistema não possui entidades de domínio complexas com relacionamentos JPA/Hibernate
- Trabalha principalmente com DTOs e mensagens XML no formato DDA0110
- A estrutura é orientada a processamento de mensagens e não a persistência de entidades

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
| `application.yml` | Leitura | Spring Boot | Configurações da aplicação por ambiente (local, des, qa, uat, prd) |
| `logback-spring.xml` | Leitura | Logback | Configuração de logs em formato JSON |
| `prometheus.yml` | Leitura | Prometheus | Configuração de scraping de métricas |
| `grafana.ini` | Leitura | Grafana | Configuração do Grafana para visualização de métricas |

---

## 10. Filas Lidas

| Nome da Fila | Tipo | Descrição |
|--------------|------|-----------|
| `QL.SPAG.BANCO_LIQUIDANTE_RECEBIMENTO_REQ.INT` (DES) | IBM MQ | Fila de entrada para recebimento de requisições de consulta de boletos em desenvolvimento |
| `QL.SPBB.ROTEADOR_CIP.REQ` (PRD/QA/UAT) | IBM MQ | Fila de entrada para recebimento de requisições de consulta de boletos em produção |

**Configurações:**
- Concorrência: 5 consumidores simultâneos
- Reconexão automática: 1800s (DES) / 60000s (PRD)
- Queue Manager: QM.ATA.01 (DES) / QM.59588111.01 (PRD)

---

## 11. Filas Geradas

| Nome da Fila | Tipo | Descrição |
|--------------|------|-----------|
| `QL.SPAG.BANCO_LIQUIDANTE_ER_RECEBIMENTO_REQ.INT` (DES) | IBM MQ | Fila de saída para envio de mensagens criptografadas ao SPB em desenvolvimento |
| `QR.REQ.59588111.17423302.05` (PRD/QA/UAT) | IBM MQ | Fila de saída para envio de mensagens criptografadas ao CIP em produção |

**Formato das Mensagens:**
- Mensagens XML DDA0110 criptografadas em UTF-16BE
- Contém: NUOp, NumCtrlPart, ISPB, Código de Barras, Data de Movimento

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **EVALCryptoSPB** | TCP Socket | Servidores de criptografia (srv-eval01/02 em PRD, srv-evaluat01/02 em DES/QA/UAT) na porta 10000 para criptografia de mensagens SPB |
| **IBM MQ** | Mensageria | Middleware de filas para recebimento e envio de mensagens (QM.ATA.01 em DES, QM.59588111.01 em PRD) |
| **CIP (Câmara Interbancária de Pagamentos)** | SPB | Sistema de destino das mensagens DDA0110 (ISPB: 17423302) |
| **ConfigCat** | Feature Toggle | Serviço de gerenciamento de feature flags |
| **API Gateway BV** | OAuth2/JWT | Autenticação e autorização via JWT (apigatewaydes.bvnet.bv em DES, apigateway.bvnet.bv em PRD) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades em módulos (application, domain, common)
- Uso adequado de injeção de dependências e configuração Spring
- Cobertura de testes unitários presente
- Uso de Lombok para redução de boilerplate
- Configuração de retry e reconexão automática
- Logs estruturados em JSON
- Documentação Swagger configurada

**Pontos de Melhoria:**
- Classe `VerificaController` com lógica de negócio misturada (acesso direto a `DadosUtils`)
- Uso de `Thread.sleep` em testes e código de produção (`DadosUtils.conecta()`)
- Tratamento de exceções genérico em alguns pontos (catch Exception)
- Falta de validação de entrada mais robusta nos controllers
- Código de geração de NuOp com lógica complexa que poderia ser melhor documentada
- Uso de `synchronized` em `EncryptService` pode gerar contenção
- Alguns métodos `protected` em classes utilitárias sem justificativa clara
- Falta de testes de integração mais abrangentes
- Configurações hardcoded em alguns pontos (ex: timeouts, tamanhos de cache)

---

## 14. Observações Relevantes

1. **Ambiente Multi-Cloud**: Sistema preparado para execução em Google Cloud Platform (GCP) com suporte a OpenShift
2. **Segurança**: Implementa autenticação OAuth2 com JWT e criptografia SPB obrigatória
3. **Resiliência**: Configurado com retry automático, reconexão de filas e health checks
4. **Monitoramento**: Integração completa com Prometheus/Grafana para observabilidade
5. **Versionamento**: Sistema na versão 0.19.0, indicando ainda em fase de evolução
6. **Dependência Crítica**: SPBSecJava 1.0.6 é uma biblioteca legada fundamental para operação
7. **Horário Sensível**: Lógica de data/hora para DDA0110 considera janela específica (05:50-06:00)
8. **Configuração por Ambiente**: Múltiplos ambientes configurados (local, des, qa, uat, prd) com parâmetros específicos
9. **Auditoria**: Integração com trilha de auditoria BV para rastreabilidade
10. **Docker**: Aplicação containerizada com imagem base Java 11 otimizada

---