# Ficha Técnica do Sistema

## 1. Descrição Geral

O **springboot-spag-base-gestao-bff** é um Backend For Frontend (BFF) desenvolvido em Spring Boot que atua como camada de integração e orquestração para o Sistema de Pagamentos (SPAG). O sistema centraliza a comunicação entre frontends e diversos microserviços backend, gerenciando operações de pagamentos (TED, Boleto, PIX), DICT (Diretório de Identificadores de Contas Transacionais), gestão de fraudes, contestações, escrow, rebates, contingência, saque de agentes e relatórios regulatórios. Implementa padrão de arquitetura de microserviços com configurações multi-ambiente (desenvolvimento, homologação e produção), utilizando OAuth2 para autenticação e RestTemplate para integrações síncronas.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **AppConfigurationEndPoint** | Centraliza constantes de 300+ endpoints REST para integração com microserviços backend |
| **SpagExceptionHandler** | Handler global de exceções do sistema, tratando BusinessException, NotFoundException e erros HTTP |
| **BffInterceptor** | Interceptor que adiciona token Bearer nas requisições HTTP |
| **OAuth2BVSARestTemplate** | RestTemplate customizado com renovação automática de token OAuth2 |
| **SpagRestResponseUtilBff** | Utilitário para padronização de respostas REST no formato SPAG |
| **GlobConfiguration** | Configuração de RestTemplate para consultas de pessoa no serviço Global |
| **RebateConfiguration** | Configuração de RestTemplate para regras e pagamentos de rebate |
| **EscrowConfiguration** | Configuração de RestTemplate para operações de conta escrow |
| **DocketConfiguration** | Configuração do Swagger para documentação de APIs |
| **ObjectMapperConfig** | Configuração customizada do Jackson ObjectMapper |
| **CachedHttpServletRequest** | Wrapper para cache de request body permitindo reutilização |
| **MockDomainBFF** | Classe utilitária extensa com mocks para testes e geração de massa de dados |
| **Domain Classes (400+)** | DTOs e entidades representando objetos de negócio (Pagamento, Rebate, Saque, SPI, DICT, Fraude, etc) |

---

## 3. Tecnologias Utilizadas

- **Framework Principal:** Spring Boot, Spring MVC, Spring Security
- **Autenticação/Autorização:** OAuth2 (Client Credentials), Basic Authentication
- **Comunicação HTTP:** RestTemplate, RestTemplateBuilder, ClientHttpRequestInterceptor
- **Serialização:** Jackson (JSON), Lombok (redução boilerplate)
- **Documentação API:** Swagger/Springfox, OpenAPI 3
- **Logs:** Logback com formato JSON estruturado
- **Containerização:** Docker (multi-layer Java 11)
- **Orquestração:** Kubernetes (configurações YAML multi-ambiente)
- **Validação:** javax.validation
- **Utilitários:** SimpleDateFormat, LocalDateTime, conversores customizados Jackson
- **Testes:** Mocks extensivos (MockDomainBFF)
- **Gerenciamento Configuração:** @ConfigurationProperties, YAML multi-ambiente (des/uat/prd)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET/POST | /v1/banco-digital/pessoa/doc | GlobalEndpoints | Consulta dados de pessoa por documento |
| GET | /v1/banco-digital/conta/doc | GlobalEndpoints | Consulta conta por documento |
| GET | /v1/banco-digital/conta/pessoa | GlobalEndpoints | Consulta conta por pessoa |
| GET | /produtos | RegrasRebateEndpoints | Lista produtos rebate |
| GET/POST/PUT | /parametrizacao/cliente | RegrasRebateEndpoints | Gestão parametrização cliente rebate |
| GET/POST/PUT | /parametrizacao/produto | RegrasRebateEndpoints | Gestão parametrização produto rebate |
| GET/POST | /pagamentos | RegrasRebateEndpoints | Consulta e aprovação pagamentos rebate |
| GET | /historico | RegrasRebateEndpoints | Histórico parametrizações rebate |
| GET/POST/PUT | /escrow-account/contract/v1 | EscrowEndPoints | Gestão contratos conta escrow |
| GET | /escrow-account/contract/v1 (filtros) | EscrowEndPoints | Consulta contratos escrow com filtros |
| GET/POST | /conta/v1 | EscrowEndPoints | Operações conta escrow |
| GET/POST | /document/v1 | EscrowEndPoints | Gestão documentos escrow |
| GET/POST | /sitp/v1 | EscrowEndPoints | Integração SITP para escrow |
| POST | /v1/withdraw | AppConfigurationEndPoint | Operações saque agente |
| GET/POST | /v1/dict | AppConfigurationEndPoint | Operações DICT (portabilidade, reivindicações) |
| POST | /v1/fraude | AppConfigurationEndPoint | Registro e consulta fraudes |
| GET/POST | /v1/ordem-judicial | AppConfigurationEndPoint | Gestão ordens judiciais |
| GET/POST | /v1/bloqueio-conta | AppConfigurationEndPoint | Bloqueio/desbloqueio contas |
| GET/POST | /sitp-gestao-fintech/* | AppConfigurationEndPoint | Endpoints gestão SITP |
| GET/POST | /ted-fintech/* | AppConfigurationEndPoint | Operações TED |
| GET/POST | /boleto-fintech/* | AppConfigurationEndPoint | Operações Boleto |
| GET/POST | /contigencia/* | AppConfigurationEndPoint | Operações contingência |
| GET | /dashboard/* | AppConfigurationEndPoint | Consultas dashboard gerencial |

---

## 5. Principais Regras de Negócio

1. **Rebate:**
   - Cálculo de rebate por percentual ou valor fixo sobre transações
   - Periodicidade configurável (diária, semanal, mensal)
   - Apuração por quantidade de transações ou valor total
   - Retenção automática de impostos (ISS e IR) sobre pagamentos
   - Aprovação obrigatória de pagamentos acima de limites configurados
   - Formas de rebate: rede bancária ou corban
   - Parametrização por cliente e produto com histórico de alterações

2. **Saque de Agentes:**
   - Gestão de contratos de agentes com faixas de valor RCO
   - Cálculo de repasse mensal por modalidade de agente
   - Controle de limites por faixa de valor de saque
   - Histórico completo de transferências e operações

3. **Pagamentos:**
   - Suporte múltiplos tipos de liquidação (TED, DOC, Boleto, STN, PIX)
   - Controle de status de processamento (pendente, processado, erro, cancelado)
   - Autenticação e rastreamento por protocolo único
   - Priorização de pagamentos conforme regras de negócio
   - Validação de dados bancários (CPF/CNPJ, agência, conta)

4. **SPI (Sistema de Pagamentos Instantâneos):**
   - Consulta de saldos e extratos de contas PI
   - Detalhamento completo de lançamentos com dados pacs
   - Conferência de saldos entre sistemas
   - Histórico de operações instantâneas

5. **DICT:**
   - Gestão de portabilidade de chaves PIX
   - Processamento de reivindicações (claims)
   - Validação de tipos de chave (CPF, CNPJ, Email, Telefone, EVP)

6. **Fraude:**
   - Registro e acompanhamento de infrações
   - Análise de padrões suspeitos
   - Integração com sistemas de prevenção

7. **Contingência:**
   - Processamento alternativo de boletos
   - Validações CIP (Câmara Interbancária de Pagamentos)
   - Gestão de parâmetros de interface

8. **Zeragem CP:**
   - Parametrização de contas de pagamento
   - Consulta de saldos CCBD (Conta Centralizadora Banco do Brasil)
   - Processamento automático de zeragem

9. **Escrow:**
   - Gestão de contas garantia vinculadas a contratos
   - Controle de documentação e compliance
   - Integração com SITP para movimentações

---

## 6. Relação entre Entidades

**Principais Entidades e Relacionamentos:**

- **Rebate:**
  - `ParametrizacaoCliente` 1:N `FaixaParametrizacao` (cliente possui múltiplas faixas de cálculo)
  - `ParametrizacaoProduto` 1:N `FaixaParametrizacao` (produto possui múltiplas faixas)
  - `PagamentoRebate` N:1 `ParametrizacaoCliente` (pagamento vinculado a parametrização)
  - `HistoricoParametrizacaoCliente` N:1 `ParametrizacaoCliente` (auditoria alterações)

- **Saque:**
  - `AgenteDeSaque` 1:N `ContratoDoAgenteDeSaqueRepresentation` (agente possui múltiplos contratos)
  - `ContratoDoAgenteDeSaqueRepresentation` 1:N `AgentAmountRangeInsertRequest` (contrato possui faixas valor)
  - `AgenteDeSaque` 1:N `TransferHistory` (histórico transferências do agente)

- **Pagamento:**
  - `LancamentoDTO` 1:1 `DadosGerais` (dados principais)
  - `LancamentoDTO` 1:1 `DadosRemetente` (origem)
  - `LancamentoDTO` 1:1 `DadosFavorecido` (destino)
  - `LancamentoDTO` 0:1 `DadosBoleto` (específico boleto)
  - `LancamentoDTO` 0:1 `DadosTributo` (específico tributo)
  - `TransactionOperation` 1:1 `Account` (débito)
  - `TransactionOperation` 1:1 `Account` (crédito)

- **SPI:**
  - `ConsultaInfoConta` 1:N `Extrato` (conta possui múltiplos extratos)
  - `Extrato` 1:N `DetalhesLancamentosResponse` (extrato possui lançamentos)
  - `ConsultaDetalheLancamentoResponse` 1:1 `PacsResponse` (detalhe vinculado a mensagem pacs)

- **Multiconta:**
  - `MultiConta` 1:N `ContaWallet` (multiconta agrupa wallets)
  - `ContaWallet` 1:1 `ParametroWallet` (wallet possui parametrização)

- **DICT:**
  - `Entry` (chave DICT) possui relacionamento com `Claim` (reivindicação)
  - `Entry` vinculada a `Account` (conta proprietária)

- **Escrow:**
  - Contrato escrow vinculado a documentos e contas SITP
  - Relacionamento com participantes e histórico movimentações

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| N/A | N/A | N/A | O sistema atua como BFF, não acessa diretamente banco de dados. Todas as consultas são realizadas via APIs REST dos microserviços backend (SPAG, SITP, COBR, GLOB, PIXX atoms/orchs). |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| N/A | N/A | N/A | O sistema atua como BFF, não atualiza diretamente banco de dados. Todas as operações de escrita são realizadas via APIs REST dos microserviços backend. |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | Leitura | Configuração Logback | Arquivo de configuração de logs em formato JSON para ambientes des/uat/prd |
| infra.yml | Leitura | Configuração Kubernetes | Arquivo de configuração de infraestrutura multi-ambiente com 200+ variáveis |
| Dockerfile | Leitura | Build Docker | Configuração de deploy da aplicação Java 11 em camadas |
| application.yml | Leitura | Spring Boot | Configurações da aplicação (properties OAuth2, URLs, timeouts) |
| ArquivoLancamentoRco | Gravação | Domain/RCO | Geração de arquivos de lançamentos RCO para processamento |
| ArquivoConsolidadoRco | Gravação | Domain/RCO | Geração de arquivos consolidados RCO |
| ReportFileResponse | Gravação | Domain/Reports | Geração de relatórios (IN200, Demonstrativo TIR) |

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas. Todas as integrações são síncronas via REST.

---

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas. Todas as integrações são síncronas via REST.

---

## 12. Integrações Externas

| Sistema Externo | Tipo Integração | Descrição |
|----------------|-----------------|-----------|
| **SPAG (Sistema de Pagamentos)** | REST API OAuth2 | Microserviços core de pagamentos (TED, Boleto, PIX) |
| **SITP (Sistema Instantâneo de Pagamentos)** | REST API | Gestão de contas PI, extratos, saldos, lançamentos SPI |
| **COBR (Cobrança)** | REST API | Operações de boletos e cobrança |
| **GLOB (Global)** | REST API Basic Auth | Consultas de dados cadastrais de pessoas e contas |
| **PIXX (PIX)** | REST API | Operações PIX, DICT, portabilidade, claims |
| **Rebate Atoms/Orchs** | REST API | Microserviços de regras e pagamentos de rebate |
| **Escrow Services** | REST API | Gestão de contas escrow e contratos |
| **Fraude Services** | REST API | Registro e consulta de fraudes e infrações |
| **Dashboard Services** | REST API | Consultas gerenciais e relatórios |
| **Contingência Services** | REST API | Processamento alternativo e validações CIP |
| **Agent Withdraw Services** | REST API | Gestão de agentes de saque e contratos |
| **BVSA (Banco Virtual)** | REST API OAuth2 | Serviços bancários virtuais com token auto-renovável |
| **API Gateway** | REST API | Gateway de entrada para roteamento de requisições |
| **Dias Úteis Atom** | REST API | Consulta de calendário de dias úteis |
| **Lista Bancos ISPB** | REST API | Consulta de códigos ISPB de instituições financeiras |
| **Métricas Services** | REST API | Coleta e exposição de métricas operacionais |

**Observação:** O sistema integra com mais de 50 microserviços backend diferentes, todos via REST síncrono. As URLs são configuráveis por ambiente (des/uat/prd) através do arquivo infra.yml.

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Excelente uso de Lombok reduzindo significativamente boilerplate code
- Separação clara de responsabilidades com padrão BFF bem implementado
- Configurações externalizadas e multi-ambiente bem estruturadas
- Handlers de exceção centralizados e organizados por domínio
- Uso adequado de padrões Spring (RestTemplate, Interceptors, Configuration)
- Documentação Swagger configurada
- Logs estruturados em JSON facilitando observabilidade
- Conversores Jackson customizados para padronização de datas
- Classes de domínio bem modeladas com validações
- Extensa classe de mocks facilitando testes

**Pontos de Melhoria:**
- Classe AppConfigurationEndPoint com 300+ constantes poderia ser modularizada
- Falta de testes unitários evidentes na análise
- Algumas classes de domínio muito extensas (ex: MockDomainBFF)
- Ausência de cache para otimizar chamadas repetidas aos backends
- Falta de circuit breakers para resiliência em integrações
- Documentação inline (JavaDoc) limitada
- Alguns métodos utilitários poderiam ser extraídos para classes especializadas
- Configurações OAuth2 poderiam ser mais abstraídas
- Falta de métricas de performance e SLA das integrações
- Ausência de versionamento explícito de APIs

O código demonstra maturidade arquitetural e boas práticas Spring Boot, mas há espaço para melhorias em resiliência, testes automatizados e modularização de componentes muito extensos.

---

## 14. Observações Relevantes

1. **Arquitetura BFF:** O sistema implementa corretamente o padrão Backend For Frontend, atuando como camada de agregação e simplificação para frontends, sem lógica de negócio complexa.

2. **Multi-tenancy:** Configurações robustas para múltiplos ambientes (des/uat/prd) com mais de 200 variáveis de configuração por ambiente.

3. **Segurança:** Implementa múltiplos mecanismos de autenticação (OAuth2 Client Credentials, Basic Auth) conforme necessidade de cada integração.

4. **Domínios Complexos:** Abrange domínios financeiros complexos (Pagamentos, PIX, DICT, Rebate, Escrow, Fraude) com regras específicas do mercado brasileiro.

5. **Integrações Massivas:** Integra com mais de 50 microserviços diferentes, demonstrando alta complexidade de orquestração.

6. **Padronização:** Uso consistente de padrões de resposta (SpagRestResponse) e tratamento de erros.

7. **Observabilidade:** Logs estruturados em JSON com MDC para rastreamento de requisições (ticket).

8. **Regulatório:** Suporte a relatórios regulatórios (IN200, Demonstrativo TIR) e conformidade com normas do Banco Central.

9. **Containerização:** Preparado para deploy em Kubernetes com Dockerfile otimizado multi-layer.

10. **Evolução:** Sistema em evolução ativa, evidenciado por múltiplas versões de endpoints (v1, v2) e configurações de contingência.

11. **Limitações Identificadas:**
    - Integrações síncronas podem gerar latência acumulada
    - Ausência de cache pode impactar performance
    - Falta de circuit breakers pode comprometer resiliência
    - Dependência forte de disponibilidade dos backends

12. **Recomendações:**
    - Implementar cache distribuído (Redis) para consultas frequentes
    - Adicionar Resilience4j para circuit breakers e retry
    - Implementar testes de contrato (Pact) para integrações
    - Adicionar métricas Prometheus/Grafana
    - Considerar migração gradual para comunicação assíncrona em operações não críticas
    - Implementar API Gateway pattern com rate limiting