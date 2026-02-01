# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-spbb-base-atom-dda-return-router** é um serviço atômico Spring Boot responsável por rotear mensagens de retorno DDA (Débito Direto Autorizado) provenientes do CIP (Câmara Interbancária de Pagamentos). O sistema consome mensagens criptografadas de filas IBM MQ, realiza a descriptografia utilizando o serviço SPBSecJava (EVAL), analisa o conteúdo XML das mensagens, e as roteia para diferentes destinos (filas JMS ou tópicos Google Pub/Sub) de acordo com regras de negócio baseadas no tipo de mensagem e no dígito sequencial da operação. O sistema também registra logs de transações e suporta reprocessamento de mensagens com controle de tentativas.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal Spring Boot que inicializa a aplicação |
| **RouterService** | Serviço principal que orquestra o processamento: recebe mensagens JMS, descriptografa, analisa XML e roteia para destinos apropriados |
| **JmsService** | Gerencia o envio de mensagens para diferentes filas JMS (legado, MS, consulta V2, cancelamento baixa, roteador, log) |
| **DecryptService** | Responsável pela descriptografia de mensagens utilizando SPBSecJava (EVAL) com retry automático |
| **LogService** | Constrói objetos JSON de log a partir de mensagens XML DDA para diferentes tipos de mensagem |
| **FeatureToggleService** | Gerencia feature toggles para habilitar/desabilitar funcionalidades dinamicamente |
| **JmsConfig** | Configura múltiplas conexões JMS (IBM MQ) e templates para diferentes filas |
| **RouterConfiguration** | Configura beans do Spring para injeção de dependências |
| **JMSRepository (interface)** | Interface base para repositórios de envio de mensagens JMS |
| **JMSRepositoryRoteadorImpl** | Implementação para envio de mensagens à fila roteador |
| **JMSRepositoryLegadoImpl** | Implementação para envio de mensagens ao sistema legado |
| **JMSRepositoryConsultaV2Impl** | Implementação para envio de mensagens à fila de consulta V2 |
| **JMSRepositoryMSImpl** | Implementação para envio de mensagens à fila MS |
| **JMSRepositoryCancelamentoBaixaImpl** | Implementação para envio de mensagens de cancelamento de baixa |
| **JMSRepositoryLogImpl** | Implementação para envio de logs |
| **BaixaBoletoMapper** | Mapeia mensagens XML DDA para objetos de domínio (BoletoBaixaDDA0108, DDA0116R2) |
| **FilaDestinoEnum** | Enumeração dos destinos possíveis de roteamento |
| **BoletoBaixaDDA0108** | Entidade de domínio representando baixa de boleto DDA0108R1 |
| **DDA0116R2** | Entidade de domínio representando cancelamento de baixa |
| **RouterException** | Exceção customizada para erros de roteamento |
| **MqUtil** | Utilitário para controle de tentativas de reprocessamento de mensagens |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.x** (framework principal)
- **Java 11**
- **IBM MQ 9.3.0.20** (mensageria JMS)
- **Google Cloud Pub/Sub** (mensageria cloud)
- **SPBSecJava 1.0.6** (biblioteca de criptografia EVAL para SPB)
- **Spring JMS** (integração com IBM MQ)
- **Spring Cloud GCP 1.2.8** (integração com Google Cloud)
- **Jackson** (serialização/deserialização JSON)
- **org.json** (manipulação de XML/JSON)
- **Lombok** (redução de boilerplate)
- **Logback** (logging com formato JSON)
- **Springfox Swagger 3.0.0** (documentação de API)
- **Spring Retry** (retry automático)
- **ConfigCat** (feature toggle)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **OpenShift/OCP** (plataforma de execução)

---

## 4. Principais Endpoints REST

Não se aplica. O sistema é orientado a eventos (event-driven), consumindo mensagens de filas JMS via listeners. Não expõe endpoints REST de negócio, apenas endpoints de monitoramento (Actuator).

**Endpoints de Monitoramento (Actuator):**
- `GET /actuator/health` - Health check
- `GET /actuator/metrics/*` - Métricas
- `GET /actuator/prometheus` - Métricas no formato Prometheus

---

## 5. Principais Regras de Negócio

1. **Roteamento baseado em tipo de mensagem DDA:**
   - **DDA0110R1**: Roteado para CONSULTA_V2 (se dígito 6-9) ou MS (se dígito 1-5) ou LEGADO (outros casos)
   - **DDA0108R1**: Baixa de boleto - enviado para Pub/Sub (se dígito 6-9) ou fila legado (dígito 1-5)
   - **DDA0115R1**: Cancelamento de baixa - enviado para CANCELAMENTO_BAIXA (se dígito 6-9) ou LEGADO (outros casos)
   - **DDA0116R2**: Recebimento de cancelamento - enviado para Pub/Sub
   - Mensagens de erro (DDA0108E, DDA0110E): tratadas como suas versões R1

2. **Critério de roteamento por dígito sequencial:**
   - Extrai o 15º dígito do campo `NUOp` (número de operação)
   - Dígitos 6-9: sistemas novos (MS/V2/Pub/Sub)
   - Dígitos 1-5: sistema MS
   - Outros: sistema legado

3. **Descriptografia obrigatória:**
   - Todas as mensagens recebidas são criptografadas (envelope SPB)
   - Descriptografia via servidores EVAL com retry automático (2 tentativas)
   - Falha na descriptografia resulta em reprocessamento (até 20 tentativas)

4. **Reprocessamento com backoff:**
   - Mensagens com erro são reenviadas à fila roteador com delay de 20 minutos
   - Máximo de 20 tentativas antes de descartar
   - Controle via propriedade `MQDeliveryCount`

5. **Envio paralelo para legado (configurável):**
   - Flag `alwaysSendLegado` permite envio duplicado para sistema legado além do destino principal

6. **Logging assíncrono:**
   - Logs de transação enviados de forma assíncrona para fila específica
   - Não bloqueia processamento principal

7. **Validação de certificados:**
   - Verifica status de servidores EVAL antes de descriptografar
   - Reconexão automática em caso de falha

---

## 6. Relação entre Entidades

**Entidades de Domínio:**

- **BoletoBaixaDDA0108**: Representa uma baixa de boleto bem-sucedida (DDA0108R1)
  - Contém: código mensagem, número controle participante, ISPBs, identificação título, identificação baixa, data/hora, etc.

- **BoletoBaixaDDA0108Error**: Representa uma baixa de boleto com erro (DDA0108E)
  - Estende informações de BoletoBaixaDDA0108 com lista de erros

- **DDA0116R2**: Representa cancelamento de baixa de boleto
  - Contém: ISPBs, identificação título/baixa, motivo cancelamento, situação título, etc.

- **Erro**: Representa um erro específico em uma mensagem
  - Atributos: atributo com erro, código do erro

- **BaixaOperacional**: Entidade auxiliar para status de baixa
  - Atributos: identificação título CIP, status

**Relacionamentos:**
- BoletoBaixaDDA0108Error **contém** lista de Erro (1:N)
- Não há relacionamentos JPA/Hibernate (entidades são DTOs para transferência de dados)

---

## 7. Estruturas de Banco de Dados Lidas

Não se aplica. O sistema não acessa diretamente bancos de dados relacionais ou NoSQL.

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema não realiza operações de escrita em bancos de dados.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | Spring Boot (startup) | Arquivo de configuração principal com propriedades do sistema |
| application-local.yml | Leitura | Spring Boot (profile local) | Configurações específicas para ambiente local |
| logback-spring.xml | Leitura | Logback (startup) | Configuração de logging (console, formato JSON) |
| DDA*.xml (assets) | Leitura | Testes unitários | Arquivos XML de exemplo para testes |

**Observação:** O sistema não grava arquivos em disco, apenas lê configurações e assets de teste.

---

## 10. Filas Lidas

| Nome da Fila | Tipo | Classe Responsável | Descrição |
|--------------|------|-------------------|-----------|
| `${ibm.mq.queue}` (QL.RSP.17423302.01858774.05) | IBM MQ | RouterService (@JmsListener) | Fila principal de entrada com mensagens DDA criptografadas do CIP |

**Configuração:**
- Queue Manager: QM.01858774.01 (produção) / QM.ATA.01 (outros ambientes)
- Channel: SYSTEM.AUTO.SVRCONN (produção) / CASH.SRVCONN (outros)
- Concorrência: 4 listeners simultâneos

---

## 11. Filas Geradas

| Nome da Fila | Tipo | Classe Responsável | Descrição |
|--------------|------|-------------------|-----------|
| `${ibm.mqms.queue.ms}` (QL.CASH.DDA_RETORNO_CIP_MSA.RSP) | IBM MQ | JMSRepositoryMSImpl | Fila para mensagens destinadas ao microserviço (MS) |
| `${ibm.mqms.queue.old}` (QL.CASH.DDA_RETORNO_CIP_LEGADO_BVSA.RSP) | IBM MQ | JMSRepositoryLegadoImpl | Fila para sistema legado |
| `${ibm.mqms.queue.vdois}` (QL.SPAG.ROTEADOR_CIP.RSP) | IBM MQ | JMSRepositoryConsultaV2Impl | Fila para consultas versão 2 (SPAG) |
| `${ibm.mqms.queue.solBaixa}` (QL.SPAG.RETORNO_SOL_BAIXA.RSP) | IBM MQ | JMSRepositoryCancelamentoBaixaImpl | Fila para cancelamento de baixa |
| `${ibm.mq.queue}` (mesma fila de entrada) | IBM MQ | JMSRepositoryRoteadorImpl | Fila de reprocessamento (mensagens com erro) |
| `${ibm.mqms.queue.logs}` (QL.CASH.DDA_LOG_TRANSACAO_CIP.INT) | IBM MQ | JMSRepositoryLogImpl | Fila para logs de transação |

**Tópicos Pub/Sub:**
| Nome do Tópico | Classe Responsável | Descrição |
|----------------|-------------------|-----------|
| `business-spag-base-baixa-boleto` | RouterService | Tópico para baixas de boleto (DDA0108R1) |
| `business-spag-base-recebimento-cancelamento-baixa-boleto` | RouterService | Tópico para cancelamentos de baixa (DDA0116R2) |

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **SPBSecJava (EVAL)** | TCP/IP (porta 10000) | Servidores de criptografia para descriptografia de mensagens SPB. Endereços: srv-eval01/02.bvnet.bv (produção), srv-evaluat01/02.bvnet.bv (outros ambientes) |
| **IBM MQ (CIP)** | JMS | Fila de entrada com mensagens do CIP (Câmara Interbancária de Pagamentos) |
| **IBM MQ (CASH)** | JMS | Filas de destino para sistemas internos (legado, MS, logs) |
| **IBM MQ (SPAG)** | JMS | Filas de destino para sistema SPAG (consulta V2, cancelamento baixa) |
| **Google Cloud Pub/Sub** | gRPC | Tópicos para publicação de eventos de baixa e cancelamento de boletos |
| **ConfigCat** | HTTPS | Serviço de feature toggle para controle de funcionalidades |

**Parâmetros de integração EVAL:**
- Domínio: SPB
- ISPB BV: 01858774
- ISPB CIP: 17423302
- Timeout conexão: 5000ms
- Timeout leitura: 5000ms
- Retry: 5 tentativas

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades entre camadas (service, repository, config)
- Uso adequado de injeção de dependências e configuração Spring
- Tratamento de exceções com retry automático
- Logging estruturado em JSON
- Uso de Lombok para reduzir boilerplate
- Configuração externalizada via YAML
- Suporte a múltiplos ambientes
- Testes unitários presentes (embora não enviados)

**Pontos de Melhoria:**
- **Complexidade ciclomática alta** em `RouterService.getQueueList()` e `RouterService.listener()` - métodos muito longos com múltiplas responsabilidades
- **Acoplamento forte** com IBM MQ e estrutura XML específica - dificulta testes e manutenção
- **Falta de validação** de dados de entrada antes do processamento
- **Tratamento genérico de exceções** em vários pontos (catch Exception) - perde informações importantes
- **Código duplicado** em métodos de parsing XML (LogService)
- **Falta de documentação** JavaDoc nas classes principais
- **Configuração de retry hardcoded** em alguns pontos (MqUtil.QTD_MAX_RETENTATIVAS)
- **Uso de strings mágicas** para nomes de tags XML espalhadas pelo código
- **Método `buildDDA0108E` muito extenso** com muitas chamadas repetitivas
- **Falta de testes de integração** para validar fluxo completo

**Recomendações:**
1. Refatorar métodos longos em métodos menores e mais coesos
2. Criar classes de validação de entrada
3. Implementar padrão Strategy para roteamento baseado em tipo de mensagem
4. Adicionar JavaDoc nas classes e métodos públicos
5. Extrair constantes para strings mágicas
6. Melhorar tratamento de exceções com tipos específicos
7. Adicionar mais testes de integração

---

## 14. Observações Relevantes

1. **Arquitetura Event-Driven:** O sistema é totalmente orientado a eventos, não expondo APIs REST de negócio. Toda comunicação é via mensageria.

2. **Resiliência:** Implementa múltiplos mecanismos de resiliência:
   - Retry automático na descriptografia (2 tentativas)
   - Reprocessamento de mensagens com erro (até 20 tentativas)
   - Reconexão automática com servidores EVAL
   - Reconexão automática com IBM MQ (timeout 1800s)

3. **Segurança:** Mensagens trafegam criptografadas (padrão SPB) e são descriptografadas apenas no momento do processamento.

4. **Observabilidade:** 
   - Logs estruturados em JSON para facilitar análise
   - Métricas expostas via Actuator/Prometheus
   - Logs de transação enviados para fila específica

5. **Deployment:** 
   - Containerizado via Docker
   - Deploy em OpenShift (OCP)
   - Configuração via ConfigMaps e Secrets
   - Service Account específico (ksa-spbb-base-26713)

6. **Ambientes:** Suporta 4 ambientes (des, qa, uat, prd) com configurações específicas via profiles Spring.

7. **Feature Toggle:** Utiliza ConfigCat para controle de funcionalidades, permitindo ativar/desativar features sem redeploy.

8. **Limitações:**
   - Não há persistência de estado - mensagens perdidas em caso de falha catastrófica
   - Dependência crítica dos servidores EVAL - falha total impede processamento
   - Lógica de roteamento baseada em dígito sequencial pode ser frágil

9. **Versão:** 0.9.0 (ainda não é versão 1.0, indicando que pode estar em fase de estabilização)

10. **Organização:** Projeto segue padrão de microserviços atômicos do Banco Votorantim, com estrutura modular (application + domain).