# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-spag-base-orch-boleto-transacao** é um serviço orquestrador de pagamentos de boletos desenvolvido em Spring Boot. Atua como intermediário na esteira de processamento de pagamentos, coordenando a validação, registro, baixa e liquidação de boletos. O sistema recebe solicitações de pagamento via mensageria (Google Cloud Pub/Sub), orquestra chamadas a serviços externos (validação de boleto, integração com sistemas legados ITP, sensibilização de contas), e publica eventos de retorno para outros componentes da arquitetura. Utiliza Apache Camel para orquestração de fluxos complexos e implementa padrões de arquitetura hexagonal (ports and adapters).

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal que inicializa a aplicação Spring Boot |
| **BoletoTransacaoService** | Serviço de domínio que coordena o processamento de solicitações e retornos de pagamento de boletos |
| **SolicitacaoPagamentoBoletoSubscriber** | Subscriber que consome mensagens de solicitação de pagamento de boletos do Pub/Sub |
| **RetornoProcessoPagamentoBoletoSubscriber** | Subscriber que consome mensagens de retorno de processamento de pagamento |
| **BoletoTransacaoRouter** | Router Camel que define as rotas principais de orquestração do fluxo de pagamento |
| **ValidacaoPagamentoBoletoRouter** | Router Camel para validação de pagamento |
| **ValidacaoBoletoRouter** | Router Camel para validação de boleto |
| **SensibilizacaoContaRouter** | Router Camel para sensibilização e estorno de contas |
| **BaixaOperacionalBoletoRouter** | Router Camel para baixa operacional de boletos |
| **RegistraBoletoRouter** | Router Camel para registro de boletos |
| **LiquidarPagamentoRouter** | Router Camel para liquidação de pagamentos |
| **IntegrarPagamentoRouter** | Router Camel para integração com serviços de pagamento |
| **BoletoTransacaoClientImpl** | Implementação do cliente REST para comunicação com o serviço atômico de boleto transação |
| **IntegrarPagamentoClientImpl** | Implementação do cliente REST para comunicação com o serviço de integração de pagamentos |
| **Publishers (diversos)** | Implementações de publicadores de mensagens para diferentes tópicos Pub/Sub |
| **Processors (diversos)** | Processadores Camel que executam lógica de negócio em pontos específicos das rotas |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.x** - Framework principal da aplicação
- **Spring Cloud GCP** - Integração com Google Cloud Platform (Pub/Sub)
- **Apache Camel 3.0.1** - Framework de integração e orquestração de rotas
- **Spring Integration** - Integração com sistemas de mensageria
- **Google Cloud Pub/Sub** - Sistema de mensageria assíncrona
- **Swagger/OpenAPI 2.9.2** - Documentação de APIs
- **MapStruct 1.3.1** - Mapeamento entre objetos
- **Lombok** - Redução de código boilerplate
- **Jackson** - Serialização/deserialização JSON
- **Micrometer/Prometheus** - Métricas e monitoramento
- **Grafana** - Visualização de métricas
- **JUnit 5** - Testes unitários
- **Mockito** - Mocks para testes
- **RestTemplate** - Cliente HTTP
- **HikariCP** - Pool de conexões (implícito)
- **Logback** - Framework de logging
- **Maven** - Gerenciamento de dependências e build
- **Docker** - Containerização
- **Kubernetes/OpenShift** - Orquestração de containers (GCP)

---

## 4. Principais Endpoints REST

Não se aplica. Este é um serviço orquestrador orientado a eventos (event-driven) que consome e publica mensagens via Pub/Sub. Não expõe endpoints REST próprios, apenas endpoints de monitoramento (Actuator).

**Endpoints de Monitoramento:**
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | /actuator/health | Health check da aplicação |
| GET | /actuator/metrics | Métricas da aplicação |
| GET | /actuator/prometheus | Métricas no formato Prometheus |

---

## 5. Principais Regras de Negócio

1. **Validação de Limite de Boleto**: Verifica se o valor do boleto excede o limite configurado na tesouraria para determinar o tipo de liquidação (NORMAL ou STR_26)
2. **Diferenciação de Tipo de Cliente**: Processa de forma diferente clientes FINTECH e CASH, aplicando regras específicas de sensibilização de conta
3. **Orquestração de Fluxo de Pagamento**: Coordena sequencialmente as etapas: solicitação → validação de pagamento → validação de boleto → atualização de posição (se FINTECH) → baixa operacional → registro → liquidação
4. **Tratamento de Erros com Estorno**: Em caso de falha em qualquer etapa, executa estorno apropriado (estorno de posição Fintech ou estorno cliente Cash)
5. **Consulta de Câmara de Liquidação**: Determina janelas de liquidação consultando configurações de câmara, ajustando para STR_26 quando necessário
6. **Registro de Estado**: Mantém registro de todos os eventos e estados do pagamento através de chamadas ao serviço atômico
7. **Validação de Boleto CIP ou Contingência**: Suporta dois tipos de validação de boleto com fluxos específicos
8. **Controle de Tentativas**: Rastreia tentativas de processamento através do campo "ultimoEvento"

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **PagamentoSolicitadoPayload**: Entidade raiz que representa uma solicitação de pagamento
  - Contém: codigoLancamento, cliente (FINTECH/CASH), dataMovimento, valor
  - Relaciona-se com: Cliente (remetente e favorecido), Boleto, Pessoa (portador)

- **Cliente** (extends Pessoa): Representa participantes da transação
  - Contém: tipoPessoa, numeroCpfCnpj, nome
  - Relaciona-se com: ContaCliente

- **ContaCliente**: Dados da conta bancária
  - Contém: codigoBancoCompe, numeroAgencia, numeroConta

- **Boleto**: Dados do boleto a ser pago
  - Contém: codigoDeBarras, valor, dataVencimento

- **BoletoValidadoPayload**: Resultado da validação do boleto
  - Contém: codigoLancamento, tipoValidacaoBoleto (CIP/CONTINGENCIA)
  - Relaciona-se com: BoletoCalculado

- **BoletoCalculado**: Dados calculados do boleto após validação
  - Contém: numeroIdentificacaoTitulo, codigoEspecieTitulo, dataVencimentoTitulo
  - Relaciona-se com: Lista de BaixaTitulo

- **EstadoAtualResponse**: Representa o estado atual de um pagamento
  - Agrega: PagamentoSolicitadoPayload, BoletoValidadoPayload, ErroNegocioPayload, ErroTecnicoPayload, UltimoEventoResponse

**Relacionamentos:**
- PagamentoSolicitadoPayload 1 --- 1 Cliente (remetente)
- PagamentoSolicitadoPayload 1 --- 0..1 Cliente (favorecido)
- PagamentoSolicitadoPayload 1 --- 1 Boleto
- Cliente 1 --- 1 ContaCliente
- BoletoValidadoPayload 1 --- 1 BoletoCalculado
- BoletoCalculado 1 --- 0..* BaixaTitulo

---

## 7. Estruturas de Banco de Dados Lidas

Não se aplica. O sistema não acessa diretamente banco de dados. Todas as consultas são realizadas através de APIs REST de serviços atômicos (sboot-spag-base-atom-boleto-transacao e sboot-sitp-base-atom-integrar-pagamento).

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema não atualiza diretamente banco de dados. Todas as operações de escrita são realizadas através de APIs REST de serviços atômicos ou publicação de mensagens em tópicos Pub/Sub.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot (resources) | Arquivo de configuração da aplicação com profiles (local, des, qa, uat, prd) |
| logback-spring.xml | leitura | Logback (resources) | Configuração de logging da aplicação |
| integrar-pagamento-contracts.yaml | leitura | Swagger Codegen | Contrato OpenAPI para geração de cliente REST do serviço de integração de pagamento |
| sboot-spag-base-atom-boleto-transacao.yaml | leitura | Swagger Codegen | Contrato OpenAPI para geração de cliente REST do serviço atômico de boleto transação |

---

## 10. Filas Lidas

**Subscriptions do Google Cloud Pub/Sub:**

| Nome da Fila/Subscription | Descrição |
|---------------------------|-----------|
| business-spag-solicitacao-pagamento-boleto-sub | Recebe solicitações de pagamento de boletos para processamento |
| business-spag-retorno-processo-pagamento-boleto-sub | Recebe retornos de processamento das etapas de validação, registro, baixa e liquidação |

---

## 11. Filas Geradas

**Topics do Google Cloud Pub/Sub:**

| Nome da Fila/Topic | Descrição |
|--------------------|-----------|
| business-spag-validacao-pagamento-boleto | Publica solicitações de validação de pagamento |
| business-spag-validacao-boleto | Publica solicitações de validação de boleto (CIP ou contingência) |
| business-spag-sensibilizacao-conta | Publica comandos de sensibilização de conta (atualização/estorno de posição Fintech ou estorno cliente Cash) |
| business-spag-baixa-operacional-boleto | Publica solicitações de baixa operacional de boleto no CIP |
| business-spag-registrada-boleto | Publica solicitações de registro de boleto no sistema legado |
| business-spag-resultado-solicitacao-pagamento-boleto | Publica resultado final da solicitação de pagamento (liquidação) |

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **sboot-spag-base-atom-boleto-transacao** | API REST | Serviço atômico para registro de estados e transações de pagamento de boletos (endpoints: pagamento-solicitado, sucesso, boleto-validado, pagamento-interrompido, estado-atual) |
| **sboot-sitp-base-atom-integrar-pagamento** | API REST | Serviço atômico de integração com base de pagamentos ITP (endpoints: consulta tesouraria, consulta câmara liquidação, consulta cadastros) |
| **Google Cloud Pub/Sub** | Mensageria | Sistema de mensageria para comunicação assíncrona entre microserviços |
| **API Gateway BV** | OAuth2 | Gateway de autenticação para obtenção de tokens de acesso às APIs |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões hexagonais (ports and adapters)
- Separação clara de responsabilidades em módulos (common, domain, application)
- Uso adequado de padrões de projeto (Strategy, Factory, Gateway)
- Boa cobertura de testes unitários
- Uso de frameworks consolidados (Spring Boot, Apache Camel)
- Configuração externalizada e suporte a múltiplos ambientes
- Logging estruturado e consistente
- Uso de MapStruct para mapeamento de objetos
- Documentação OpenAPI dos contratos
- Configuração de cache para otimização de consultas

**Pontos de Melhoria:**
- Alguns processadores Camel com lógica de negócio complexa que poderiam ser melhor modularizados
- Falta de documentação inline (JavaDoc) em várias classes
- Tratamento de exceções genérico em alguns pontos (catch Exception)
- Alguns métodos longos que poderiam ser refatorados (ex: BoletoTransacaoService.receberRetornoProcessamento)
- Ausência de testes de integração mais abrangentes
- Configuração de rotas Camel poderia ser mais declarativa

---

## 14. Observações Relevantes

1. **Arquitetura Event-Driven**: O sistema é totalmente orientado a eventos, não expondo APIs REST próprias, apenas consumindo e publicando mensagens

2. **Orquestração com Apache Camel**: Utiliza Apache Camel para definir rotas complexas de processamento, permitindo composição de fluxos de forma declarativa

3. **Padrão Saga**: Implementa compensação de transações através de estornos em caso de falha em qualquer etapa do processo

4. **Cache de Consultas**: Implementa cache com TTL diferenciado (5 minutos para câmara liquidação, 60 minutos para tesouraria) para otimizar consultas frequentes

5. **Multi-tenant**: Suporta diferentes tipos de cliente (FINTECH e CASH) com fluxos específicos

6. **Geração de Código**: Utiliza Swagger Codegen para gerar clientes REST a partir de contratos OpenAPI

7. **Monitoramento**: Integrado com Prometheus e Grafana para observabilidade completa

8. **Deployment**: Preparado para deploy em Kubernetes/OpenShift no Google Cloud Platform

9. **Profiles de Ambiente**: Suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas

10. **Segurança**: Integrado com API Gateway para autenticação OAuth2

11. **Resiliência**: Implementa ACK manual de mensagens Pub/Sub para garantir processamento confiável

12. **Tipos de Evento**: Define 29 tipos de eventos diferentes para rastreamento completo do ciclo de vida do pagamento