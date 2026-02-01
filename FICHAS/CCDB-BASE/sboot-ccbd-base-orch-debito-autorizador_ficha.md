# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-ccbd-base-orch-debito-autorizador** é um orquestrador Spring Boot desenvolvido em Java 11 para autorização de transações de débito em cartões. O sistema recebe requisições de autorização, valida limites transacionais, consulta saldo em conta-corrente, solicita débito/bloqueio de valores, persiste autorizações em banco de dados, publica eventos de replicação via PubSub e envia mensagens para fila JMS (IBM MQ). Suporta duas processadoras: DXC (legado) e BNK (nova processadora), implementando regras de negócio complexas como cálculo de IOF, validação de limites diários, tratamento de transações parciais e bloqueio de operações específicas.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **DebitoAutorizadorController** | Expõe endpoints REST para autorização de transações de débito |
| **DebitoAutorizadorRouter** | Orquestra fluxo de autorização via Apache Camel, integrando múltiplos serviços |
| **DebitoAutorizadorServiceImpl** | Implementa lógica de serviço, invocando CamelContext para processar fluxo |
| **ProcessorAutorizadorInsert** | Processor Camel para inserção de novas transações |
| **ProcessorAutorizadorUpdate** | Processor Camel para atualização de transações existentes |
| **ProcessorAutorizadorValidacao** | Processor Camel para validação de transações |
| **AutorizadorCPBDProcessor** | Envia mensagens para fila JMS CPBD (IBM MQ) |
| **AutorizadorRepositoryImpl** | Integra com API autorizador para validar, processar e persistir transações |
| **ContaCorrenteRepositoryImpl** | Integra com APIs de conta-corrente para validação e consulta de saldo |
| **SolicitarDebitorRepositoryImpl** | Integra com API para solicitar débito e bloqueio de saldo |
| **LimitesTransacionaisRepositoryImpl** | Integra com API para validar e finalizar limites transacionais |
| **GlobalRepositoryImpl** | Integra com API de dados cadastrais para buscar informações do cliente |
| **PubSubPublishRepositoryImpl** | Publica eventos de replicação em tópico GCP PubSub |
| **DebitoAutorizadorMapper** | Mapeia requests/responses entre camadas, valida e sanitiza inputs |
| **InputValidationFilter** | Filtro de validação de entrada HTTP (headers/params), protege contra SQL Injection e XSS |
| **ResourceExceptionHandler** | Handler global de exceções, retorna respostas padronizadas |
| **LocalDateTypeAdapter** | Adaptador Gson para serialização/deserialização de LocalDate (formato yyyy-MM-dd) |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.x** - Framework principal
- **Apache Camel 2.x** - Orquestração de fluxos e integração
- **Java 11** - Linguagem de programação
- **IBM MQ (JMS)** - Mensageria para fila CPBD
- **Google Cloud PubSub** - Publicação de eventos de replicação
- **RestTemplate** - Cliente HTTP para integrações REST
- **Gson** - Serialização/deserialização JSON
- **Swagger/OpenAPI 3.0** - Documentação de APIs
- **OAuth2/JWT** - Segurança e autenticação
- **JUnit 5** - Testes unitários
- **Mockito** - Mocks para testes
- **Maven** - Gerenciamento de dependências
- **Logback** - Logging

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/transacao-debito/autorizar-transacao | DebitoAutorizadorController | Autoriza transação de débito (processadora DXC) |
| POST | /v1/transacao-debito/autorizar-transacao-nova-processadora | DebitoAutorizadorController | Autoriza transação de débito (nova processadora BNK) |
| GET | /actuator/health | Spring Actuator | Health check do sistema |

---

## 5. Principais Regras de Negócio

- **Validação de Limites Transacionais**: Valida limite diário de saque e débito por grupo de meio de pagamento antes de autorizar transação
- **Validação de Saldo**: Consulta saldo disponível em conta-corrente antes de processar débito
- **Bloqueio de Transações Específicas**: 
  - Compra-saque MasterCard (código AN4492)
  - Transações AFT (Account Funding Transaction - código 10*)
  - Transações internacionais BNK Mastercard
- **Suporte a Transação Parcial Visa**: Permite aprovação parcial quando saldo insuficiente para valor total
- **Cálculo de IOF**: Aplica IOF de 5,38% em transações internacionais
- **Operações de Crédito em Conta**: 
  - OCT - Original Credit Transaction (código 26*)
  - Devolução de mercadoria (código 20*)
  - Voucher (código 202000)
- **Operações de Débito em Conta**:
  - Saque (código 012000)
  - Débito/compra (código 002000)
- **Cancelamento de Limite/Bloqueio**: Cancela limite transacional e bloqueio de saldo em caso de saldo insuficiente
- **Identificação de Transação Duplicada**: Detecta e trata transações duplicadas
- **Aprovação de Transação Valor Zero**: Aprova automaticamente transações com valor zero sem realizar bloqueio de saldo
- **Sanitização de Entrada**: Valida e sanitiza todos os inputs para proteção contra SQL Injection, XSS e LDAP Injection
- **Determinação de Moeda**: Define código de moeda baseado em currency (BRL=986, USD=840, EUR=978)
- **Determinação de Produto**: Define produto por bandeira do cartão (MasterCard como padrão)

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **DebitoAutorizador**: Entidade principal representando uma transação de débito
  - Relacionamento 1:1 com **Cartao** (dados do cartão utilizado)
  - Relacionamento 1:1 com **Estabelecimento** (dados do merchant)

- **ProcessarAutorizadorRequest**: Request para processamento de autorização
  - Relacionamento 1:1 com **Cartao**
  - Relacionamento 1:1 com **Estabelecimento**

- **AutorizadorPub**: Evento de publicação para replicação
  - Relacionamento 1:1 com **ReplicacaoAutorizacao** (dados da autorização a replicar)

**Estrutura de Dados:**
- Cartao: número, bandeira, produto
- Estabelecimento: código, nome, MCC (Merchant Category Code)
- Conta: número, agência, saldo disponível
- Transação: valor, moeda, timestamp, MTI (Message Type Indicator), códigos de processamento

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TB_CONTROLE_TRANSACAO_CARTAO | Tabela | SELECT | Consulta transações de cartão existentes para validação de duplicidade (via API atom-deb-autorizador) |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TB_CONTROLE_TRANSACAO_CARTAO | Tabela | INSERT | Insere nova transação de autorização de débito (via API atom-deb-autorizador) |
| TB_CONTROLE_TRANSACAO_CARTAO | Tabela | UPDATE | Atualiza transação existente com resultado do processamento (via API atom-deb-autorizador) |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | Leitura | Configuração Spring Boot | Arquivo de configuração de logs para ambientes des/uat/prd |
| application.yml | Leitura | Configuração Spring Boot | Arquivo de propriedades da aplicação com configurações por profile (local, des, qa, uat, prd) |

---

## 10. Filas Lidas

Não se aplica - o sistema não consome mensagens de filas.

---

## 11. Filas Geradas

**IBM MQ (JMS):**
- **Fila**: CPBD (configurada via propriedade queueNameCPBD)
- **Queue Manager**: QM.DIG.01 (des/uat/prd)
- **Classe Responsável**: AutorizadorCPBDRepositoryImpl
- **Descrição**: Envia mensagens AutorizadorCPBD com dados da transação autorizada de forma assíncrona

**Google Cloud PubSub:**
- **Tópico**: business-cart-base-replicacao-dados-debito (configurado via replicacaoQuotesOutputChannel)
- **Classe Responsável**: PubSubPublishRepositoryImpl
- **Descrição**: Publica eventos AutorizadorPub para replicação de dados de autorização

---

## 12. Integrações Externas

| Sistema Integrado | Tipo | Descrição |
|-------------------|------|-----------|
| **sboot-ccbd-base-atom-deb-autorizador** | REST API | Valida, processa e persiste transações de débito. Realiza cálculo de IOF, insert e update em TB_CONTROLE_TRANSACAO_CARTAO |
| **sboot-ccbd-base-orch-solic-debito** | REST API | Solicita débito em conta-corrente e realiza bloqueio de saldo |
| **sboot-glob-base-atom-cliente-dados-cadastrais** | REST API | Busca dados cadastrais do cliente (CPF/CNPJ, tipo de conta, flag funcionário) |
| **sboot-ccbd-base-atom-conta-corrente** | REST API | Valida situação da conta, consulta saldo disponível e cancela bloqueios |
| **sboot-sglt-base-orch-limites-transacionais** | REST API | Valida limites transacionais diários (saque/débito) e finaliza controle de limite após processamento |
| **IBM MQ (CPBD)** | JMS Queue | Envia mensagens de autorização processadas para fila CPBD |
| **Google Cloud PubSub** | Message Broker | Publica eventos de replicação de dados de autorização |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 8/10

**Justificativa:**

**Pontos Positivos:**
- Estrutura bem organizada seguindo padrões de arquitetura em camadas (domain/application/common)
- Uso adequado de Apache Camel DSL para orquestração de fluxos complexos
- Implementação de segurança robusta com InputValidator e Sanitizer protegendo contra SQL Injection, XSS e LDAP Injection
- Exception handling customizado e padronizado via ResourceExceptionHandler
- Cobertura de testes unitários para Controllers, Processors e Routers
- Uso de design patterns apropriados (Builder, Strategy para Processors)
- Configuração externalizada via configmaps/secrets
- Logs sanitizados para segurança
- Separação clara de responsabilidades entre classes
- Mappers dedicados para conversão entre DTOs
- Health checks configurados

**Pontos de Melhoria:**
- Dependência de múltiplas integrações síncronas pode impactar performance e resiliência
- Falta de circuit breakers explícitos para proteção contra falhas em cascata
- Código poderia se beneficiar de mais documentação inline em fluxos complexos
- Algumas classes de configuração poderiam ser mais modulares
- Ausência de métricas de observabilidade explícitas (além de health checks)

---

## 14. Observações Relevantes

- **Projeto CCBD**: Sistema faz parte do projeto de cartões de débito do Core Banking
- **Suporte a Duas Processadoras**: DXC (processadora legado) e BNK (nova processadora), com endpoints distintos
- **Fluxo Camel Complexo**: Orquestra 7+ integrações em um único fluxo de autorização
- **Replicação de Dados**: Eventos publicados via PubSub para auditoria e replicação
- **Integração CPBD**: Envia dados via JMS IBM MQ para sistema CPBD
- **Warmup Automático**: ReadinessStatusService executa warmup após startup da aplicação
- **Múltiplos Ambientes**: Configurações específicas para des/uat/prd
- **UUIDs para Transações**: Utiliza identificadores únicos XBNK para rastreabilidade
- **Códigos de Processamento Padronizados**:
  - 012000: Saque
  - 002000: Débito/Compra
  - 202000: Voucher
  - 26*: OCT (Original Credit Transaction)
  - 10*: AFT (Account Funding Transaction)
  - 20*: Devolução de mercadoria
  - 09*: Compra-saque
- **Produtos Suportados**: Visa (1), MasterCard (2)
- **Bancos**: BV (161/655), BVSA (436/413)
- **Proteção de Segurança**: Filtro de validação com bypass para endpoints de infraestrutura (/actuator, /swagger, /v2/api-docs, /webjars)
- **Serialização Customizada**: LocalDateTypeAdapter para formato yyyy-MM-dd em JSON
- **OAuth2/JWT**: Segurança via token JWT com validação de URL configurável por ambiente