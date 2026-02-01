# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-spag-base-orch-processar-retorno-baixa-boleto** é um serviço de orquestração desenvolvido em Spring Boot que processa retornos de baixa de boletos DDA (Débito Direto Autorizado). O sistema atua como intermediário entre diferentes bases de dados (PGFT e SPAG), processando mensagens DDA recebidas via Google Cloud Pub/Sub, atualizando registros de lançamentos, gerenciando devoluções e integrando com filas IBM MQ para processamento de pagamentos. Utiliza Apache Camel para orquestração de fluxos complexos de processamento de retornos de baixa de boletos, incluindo cenários de sucesso, erro e contingência.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal que inicializa a aplicação Spring Boot |
| `ProcessarRetornoBaixaBoletoService` | Serviço de domínio que coordena o processamento de retornos DDA |
| `ProcessarRetornoBaixaBoletoRouter` | Roteador Camel principal que orquestra os fluxos de processamento |
| `CancelarBaixaBoletoRouter` | Roteador Camel para processar cancelamentos de baixa (DDA0116R2) |
| `ProcessarRetornoBaixaBoletoPubsubListener` | Listener que consome mensagens do Google Pub/Sub |
| `DDAPGFTRepositoryImpl` | Implementação de repositório para integração com base PGFT |
| `DDASPAGRepositoryImpl` | Implementação de repositório para integração com base SPAG |
| `EsteiraRepositoryImpl` | Implementação de repositório para envio de mensagens para fila IBM MQ |
| `ProcessarRetornoBaixaBoletoProcessor` | Processor Camel que identifica tipo de DDA e define propriedades de processamento |
| `DDAProcessor` | Processor que armazena DDA original como propriedade do exchange |
| `BoletoSpagProcessor` | Processor que monta objeto BoletoSpag para atualização |
| `DadosBoletoProcessor` | Processor que monta objeto DadosBoleto para inserção de retorno |
| `IncluirDevolucaoITPProcessor` | Processor que prepara devolução para ITP (PGFT) |
| `IncluirDevolucaoSPAGProcessor` | Processor que prepara devolução para SPAG via TEF |
| `TransferenciaDevolucaoMapper` | Mapper para conversão de TransacaoPagamento para TransferenciaRepresentation |
| `FeatureToggleService` | Serviço para gerenciamento de feature toggles |

---

## 3. Tecnologias Utilizadas

- **Framework Principal**: Spring Boot 2.x
- **Linguagem**: Java 11
- **Orquestração**: Apache Camel 3.22.4
- **Mensageria Cloud**: Google Cloud Pub/Sub
- **Mensageria On-Premise**: IBM MQ (JMS)
- **Cliente HTTP**: Spring RestTemplate
- **Segurança**: Spring Security com JWT, OAuth2
- **Template Engine**: Apache Velocity 2.3
- **Documentação API**: Swagger/OpenAPI (Springfox 3.0.0)
- **Monitoramento**: Spring Actuator, Prometheus, Grafana
- **Serialização**: Jackson, Gson
- **Testes**: JUnit 5, Mockito, RestAssured, Pact
- **Build**: Maven
- **Feature Toggle**: ConfigCat (via biblioteca BV)
- **Auditoria**: Biblioteca BV de trilha de auditoria
- **Containerização**: Docker

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/processar-retorno-baixa-boleto` | `ProcessarRetornoBaixaBoletoController` | Recebe payload JSON de retorno DDA e inicia processamento |
| GET | `/actuator/health` | Spring Actuator | Endpoint de health check |
| GET | `/actuator/prometheus` | Spring Actuator | Métricas para Prometheus |
| GET | `/swagger-ui.html` | Springfox | Documentação interativa da API |

---

## 5. Principais Regras de Negócio

1. **Processamento de Mensagens DDA**: O sistema processa diferentes tipos de mensagens DDA (DDA0108R1, DDA0108E, DDA0114RET, DDA0116R2), cada uma com tratamento específico.

2. **Roteamento por Instituição Financeira**: Identifica se o lançamento pertence ao banco 655 (BV) ou 413 (BVSA) e roteia para base correspondente (PGFT ou SPAG).

3. **Tratamento de Sucesso e Erro**: Diferencia retornos de sucesso (DDA0108R1) de retornos de erro (DDA0108E, DDA0114RET não confirmado) e aplica lógica específica.

4. **Gestão de Devoluções**: Quando há erro ou cancelamento de baixa, cria devoluções automáticas via ITP (para PGFT) ou TEF (para SPAG).

5. **Detecção de Duplicidade**: Identifica erro EDDA0852 (número de operação duplicado) e trata de forma especial, não atualizando flag de baixa.

6. **Contingência**: Processa mensagens DDA0114 que representam operações em contingência.

7. **Cancelamento de Baixa**: Processa mensagens DDA0116R2 que representam cancelamento de baixa, criando devoluções quando necessário.

8. **Feature Toggle para Devolução**: Utiliza feature toggle `ft_boolean_spag_base_devolucao_cancelamento_baixa` para habilitar/desabilitar criação automática de devoluções em caso de erro.

9. **Atualização de Número de Identificação de Título**: Para mensagens DDA0114, atualiza o número de identificação do título no protocolo ITP.

10. **Validação de Baixa Anterior**: Verifica se já existe baixa anterior bem-sucedida antes de processar devolução.

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **DDA (interface)**: Representa mensagens DDA genéricas
  - **DDA0108R1**: Retorno de sucesso de baixa operacional
  - **DDA0108E**: Retorno de erro de baixa operacional
  - **DDA0114RET**: Retorno de confirmação/rejeição de baixa em contingência
  - **DDA0116R2**: Aviso de cancelamento de baixa

- **Lancamento**: Representa um lançamento na base PGFT
  - Relaciona-se com DDA através de `numCtrlPart` (código de controle do participante)
  - Pode ter `cdLancamentoSPAG` quando participante é migrado

- **DadosBoleto**: Representa dados de boleto na base SPAG
  - Relaciona-se com Lancamento através de `cdLancamentoSPAG`

- **BoletoResumido**: Visão resumida de boleto, pode vir de PGFT ou SPAG
  - Contém informações de remetente, favorecido e valores

- **TransacaoPagamento**: Representa transação de pagamento/devolução
  - Contém Participante (remetente e favorecido)
  - Pode ser convertida para TransferenciaRepresentation (para SPAG/TEF)

- **TransacaoPagamentoITP**: Representa transação de devolução para ITP (PGFT)

**Relacionamentos:**
- DDA → Lancamento (1:1 via numCtrlPart)
- Lancamento → DadosBoleto (1:0..1 via cdLancamentoSPAG)
- BoletoResumido → TransacaoPagamento (para criação de devoluções)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| Lancamentos PGFT | tabela | SELECT | Busca lançamentos por código de lançamento (cdLancamento) |
| Boletos PGFT | tabela | SELECT | Busca boletos por número de identificação de baixa ou código de lançamento |
| Boletos SPAG | tabela | SELECT | Busca boletos por código de lançamento SPAG |
| Boletos SPAG por Identificação Baixa | tabela | SELECT | Busca boletos por número de identificação de baixa |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| Lancamentos PGFT | tabela | INSERT | Inclui retorno de baixa DDA (DDA0108R1, DDA0108E, DDA0114) |
| Lancamentos PGFT | tabela | UPDATE | Atualiza flag de baixa operacional e número de identificação de título |
| Retornos Solicitação SPAG | tabela | INSERT | Insere retorno de solicitação de baixa |
| Boletos SPAG | tabela | UPDATE | Atualiza flag de baixa de boleto CIP |
| Devoluções ITP | tabela | INSERT | Inclui devolução para processamento ITP |
| Devoluções SPAG | tabela | UPDATE | Atualiza lançamento de devolução com protocolo e motivo |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|--------------------------|-----------------|
| `pagamento.xml` | leitura | `XMLUtil` (template Velocity) | Template Velocity para geração de XML de dicionário de pagamento |
| `application.yml` | leitura | Spring Boot | Arquivo de configuração da aplicação |
| `logback-spring.xml` | leitura | Logback | Configuração de logs (diferentes por ambiente) |

---

## 10. Filas Lidas

- **business-spag-base-baixa-boleto-sub** (Google Pub/Sub): Recebe mensagens de retorno de baixa de boleto (DDA0108R1, DDA0108E, DDA0114)
- **business-spag-base-recebimento-cancelamento-baixa-boleto-sub** (Google Pub/Sub): Recebe mensagens de cancelamento de baixa (DDA0116R2)
- **business-spag-base-contingencia-baixa-boleto-sub** (Google Pub/Sub): Recebe mensagens de contingência de baixa
- **business-spag-base-resiliencia-baixa-boleto-dlq-sub** (Google Pub/Sub): Dead Letter Queue para mensagens com falha de processamento

---

## 11. Filas Geradas

- **QL.SPAG.SOLICITAR_PAGAMENTO_CC_REQ.INT** (IBM MQ): Envia mensagens XML de dicionário de pagamento para esteira de integração

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **sboot-spag-base-atom-processar-retorno-baixa-boleto** | REST API | Serviço atômico para operações em bases PGFT e SPAG (buscar/atualizar lançamentos, incluir devoluções) |
| **sboot-spag-base-orch-transferencias** | REST API | Serviço de orquestração de transferências para criação de devoluções TEF |
| **API Gateway BV** | OAuth2 | Autenticação e autorização via OAuth2 para chamadas entre serviços |
| **Google Cloud Pub/Sub** | Mensageria Cloud | Consumo de mensagens DDA de diferentes tópicos |
| **IBM MQ** | Mensageria On-Premise | Envio de mensagens para esteira de pagamentos |
| **ConfigCat** | Feature Toggle | Gerenciamento de feature toggles via serviço externo |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com uso de camadas (domain, application, infrastructure)
- Uso adequado de padrões de projeto (Repository, Processor, Router)
- Implementação de testes unitários, integração e funcionais
- Uso de Apache Camel para orquestração complexa de forma declarativa
- Configuração externalizada e suporte a múltiplos ambientes
- Uso de feature toggles para controle de funcionalidades
- Documentação via Swagger/OpenAPI
- Monitoramento com Actuator e Prometheus

**Pontos de Melhoria:**
- Algumas classes com responsabilidades muito amplas (ex: `DDAPGFTRepositoryImpl`, `DDASPAGRepositoryImpl` com muitos métodos)
- Lógica de negócio presente em Processors do Camel, dificultando testes isolados
- Tratamento de exceções genérico em alguns pontos (catch Exception)
- Falta de validações de entrada em alguns endpoints
- Código com alguns "magic numbers" e strings hardcoded
- Documentação inline (JavaDoc) ausente ou incompleta em várias classes
- Alguns métodos longos que poderiam ser refatorados (ex: `definirObjetoDDA0114`)

---

## 14. Observações Relevantes

1. **Arquitetura Multi-Base**: O sistema trabalha com duas bases distintas (PGFT e SPAG), roteando operações conforme instituição financeira (655 ou 413).

2. **Processamento Assíncrono**: Utiliza Google Pub/Sub para consumo assíncrono de mensagens, com suporte a DLQ para resiliência.

3. **Orquestração Complexa**: Apache Camel é usado extensivamente para orquestrar fluxos complexos com múltiplas decisões e integrações.

4. **Geração de XML via Template**: Utiliza Apache Velocity para gerar XML de dicionário de pagamento a partir de objetos Java.

5. **Segurança**: Implementa autenticação OAuth2 para comunicação entre serviços via API Gateway.

6. **Observabilidade**: Possui instrumentação completa com métricas Prometheus, health checks e logs estruturados.

7. **Ambientes**: Suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas.

8. **Containerização**: Preparado para execução em containers Docker/Kubernetes (OpenShift).

9. **Padrão de Nomenclatura**: Segue convenção de nomenclatura do Banco Votorantim (sboot-spag-base-*).

10. **Versionamento de API**: Utiliza versionamento de API via path (/v1/).

11. **Testes Automatizados**: Possui estrutura completa de testes (unit, integration, functional) com uso de Pact para testes de contrato.

12. **CI/CD**: Integrado com Jenkins conforme arquivo `jenkins.properties`.