---
## Ficha Técnica do Sistema

### 1. Descrição Geral
Sistema orquestrador de consentimentos Open Banking para iniciação de pagamentos Pix. Gerencia o ciclo de vida completo de consentimentos (consulta, aprovação, rejeição, revogação), executando validações de negócio (limite transacional, saldo, status de conta, QRCode) através de um funil de validação. Suporta pagamentos únicos, agendados e recorrentes (Pix Automático, Sweeping Accounts), integrando-se com múltiplos microserviços para orquestrar o fluxo de autorização conforme especificações Open Finance Brasil.

---

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `OpenBankingConsentimentoController` | Controller REST que expõe endpoints para consulta, atualização de status e recuperação de URL de redirecionamento de consentimentos |
| `OpenBankingConsentimentoService` | Serviço de domínio que orquestra as operações de consentimento utilizando rotas Apache Camel |
| `OpenBankingRecuperaConsentimentoRouter` | Rota Camel para recuperação de consentimentos (com ou sem aplicação do funil de validação) |
| `OpenBankingAtualizaConsentimentoRouter` | Rota Camel para atualização de status de consentimento (AUTHORISED/REJECTED/CONSUMED/REVOKED) |
| `OpenBankingFunilConsentimentoRouter` | Rota Camel que executa o funil de validações de negócio (limite, saldo, conta, QRCode) |
| `OpenBankingUrlRedirecionamentoRouter` | Rota Camel para recuperação de URLs de redirecionamento pós-autorização |
| `ContaValidatorProcessor` | Processor que valida status da conta corrente (ativa, permite débito, não bloqueada) |
| `SaldoValidatorProcessor` | Processor que valida saldo disponível suficiente para a transação |
| `LimiteValidator` (chain) | Chain of Responsibility para validação de limites (autorizado, disponível, total) |
| `QrCodeValidatorProcessor` | Processor que valida dados do QRCode Pix (valor, chave, consistência) |
| `MotivoRejeicaoProcessor` | Processor que determina o motivo de rejeição do consentimento baseado nos erros do funil |
| `OpenBankingConsentimentoMapper` | Mapper complexo bidirecional entre DTOs de API, domínio e representações |
| `OpenBankingConsentimentoRepository` | Port para integração com API de consentimentos de pagamentos únicos/agendados |
| `OpenBankingConsentimentoRecorrenteRepository` | Port para integração com API de consentimentos de pagamentos recorrentes |
| `ContaCorrenteRepository` | Port para consulta de status e dados de conta corrente |
| `LimiteRepository` | Port para consulta de limites transacionais diários |
| `GlobalRepository` | Port para consulta de dados cadastrais do cliente |
| `QRCodeRepository` | Port para consulta e validação de QRCode Pix |
| `BancosRepository` | Port para consulta de nome de instituição financeira por ISPB |
| `ResourceExceptionHandler` | Handler global de exceções que padroniza respostas HTTP 422 para erros de negócio |

---

### 3. Tecnologias Utilizadas
- **Framework**: Spring Boot 2.x
- **Orquestração**: Apache Camel 3.2
- **Segurança**: OAuth2 + JWT (Spring Security)
- **Comunicação HTTP**: RestTemplate
- **Documentação API**: Swagger/OpenAPI (Springfox Swagger 2), Swagger Codegen
- **Serialização**: Jackson
- **Utilitários**: Lombok
- **Testes**: JUnit 5, Mockito
- **Build**: Maven 3.3+
- **Java**: 11
- **Logs**: Logback (formato JSON assíncrono)
- **Métricas**: Prometheus + Grafana
- **Containerização**: Docker, Kubernetes/OpenShift
- **CI/CD**: Jenkins
- **Qualidade**: ArchUnit 0.19 (testes arquiteturais)

---

### 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/banco-digital/open-banking/consentimento/{interactId}` | `OpenBankingConsentimentoController` | Recupera dados do consentimento. Headers: `numeroConta`, `codigoBanco`, `applyFunnel` (default true). Se `applyFunnel=true`, executa funil de validações |
| PUT | `/v1/banco-digital/open-banking/consentimento/{interactId}` | `OpenBankingConsentimentoController` | Atualiza status do consentimento (AUTHORISED/REJECTED). Body: `status`, `consentRejectionReasonType`, `canal`. Header obrigatório: `sessionId` (Revelock) |
| GET | `/v1/banco-digital/open-banking/interacao/{interactId}/url-redirecionamento` | `OpenBankingConsentimentoController` | Recupera URL de redirecionamento pós-autorização. Header: `x-payment-type` (PAYMENTS/RECURRING_PAYMENTS, default PAYMENTS) |

---

### 5. Principais Regras de Negócio

1. **Tempo Limite de Consentimento**: Consentimento expira em 5 minutos após criação (status AWAITING_AUTHORISATION). Validação executada no funil, lança `TempoLimiteExcedidoException` se excedido.

2. **Validação de Saldo**: Verifica se saldo disponível na conta é suficiente para o valor da transação. Rejeita com código `SALDO_INSUFICIENTE` se insuficiente.

3. **Validação de Limites Transacionais Pix**:
   - **Limite Autorizado**: Verifica se limite diário está autorizado (`autorizado=true`)
   - **Limite Disponível**: Verifica se `disponivel >= valorTransacao`
   - **Limite Total**: Verifica se `total >= valorTransacao`
   - Rejeita com códigos `BDCC_LIMITE_NAO_AUTORIZADO`, `BDCC_LIMITE_INDISPONIVEL` ou `BDCC_LIMITE_TOTAL_INSUFICIENTE`

4. **Validação de Status de Conta**:
   - Conta deve estar ativa (situação válida)
   - Não pode ter bloqueio de débito
   - Deve permitir operações de pagamento
   - Rejeita com código `CONTA_NAO_PERMITE_PAGAMENTO` se inválida

5. **Validação de Contas Origem/Destino**: Verifica se conta de débito é diferente da conta de crédito. Rejeita com código `CONTAS_ORIGEM_DESTINO_IGUAIS` se iguais.

6. **Validação de CPF Logado**: Extrai CPF do token JWT e valida se corresponde ao CPF do consentimento. Rejeita com código `DADOS_DIVERGENTES` se divergente.

7. **Validação de QRCode Pix**:
   - Valida consistência de valor (se informado no QRCode)
   - Valida chave Pix
   - Valida dados do favorecido
   - Rejeita com código `QRCODE_INVALIDO` se inválido

8. **Funil de Consentimento**: Executa validações em sequência. Se qualquer validação falhar, rejeita consentimento automaticamente de forma assíncrona, atualizando status para REJECTED com motivo apropriado.

9. **Suporte a Agendamento**: Suporta tipos de agendamento: single (único), daily (diário), weekly (semanal), monthly (mensal), custom (customizado).

10. **Revogação de Consentimento**: Usuário ou iniciadora podem revogar consentimento até D-1 da data agendada. Status alterado para REVOKED.

11. **Anonimização de Dados**: CPF/CNPJ são anonimizados nas representações de resposta (formato `***.***.***-**`).

12. **Integração Antifraude**: Requer `sessionId` do Revelock para aprovação/rejeição de consentimentos.

---

### 6. Relação entre Entidades

**Modelo de Domínio (textual):**

- **Consentimento** (entidade raiz)
  - `consentId`: identificador único
  - `status`: AWAITING_AUTHORISATION, AUTHORISED, REJECTED, CONSUMED, REVOKED
  - `creationDateTime`: data/hora criação
  - `expirationDateTime`: data/hora expiração (5min após criação)
  - `statusUpdateDateTime`: data/hora última atualização
  - Contém: `PaymentDTO`, `LoggedUserDTO`, `BusinessEntityDTO`, `CreditorDTO`, `DebtorAccountDTO`

- **PaymentDTO**
  - `type`: tipo pagamento (PIX)
  - `date`: data pagamento
  - `currency`: moeda (BRL)
  - `amount`: valor
  - Contém: `ScheduleDTO`, `DetailsDTO`

- **ScheduleDTO**
  - `single`: pagamento único
  - `daily`: pagamento diário recorrente
  - `weekly`: pagamento semanal recorrente
  - `monthly`: pagamento mensal recorrente
  - `custom`: pagamento customizado recorrente

- **DetailsDTO**
  - `localInstrument`: MANU, DICT, QRDN, QRES, INIC
  - `qrCode`: texto QRCode
  - `proxy`: chave Pix
  - Contém: `CreditorAccountDTO`

- **DebtorAccountDTO** (conta débito)
  - `ispb`: código ISPB banco
  - `issuer`: código agência
  - `number`: número conta
  - `accountType`: tipo conta

- **CreditorAccountDTO** (conta crédito)
  - Similar a DebtorAccountDTO

- **LoggedUserDTO**
  - `document`: CPF/CNPJ usuário logado

- **BusinessEntityDTO**
  - `document`: CPF/CNPJ titular conta

- **CreditorDTO**
  - `name`: nome favorecido
  - `cpfCnpj`: documento favorecido

**Relacionamentos com Respostas de Serviços Externos:**
- `GlobalResponse`: dados cadastrais cliente (CPF, nome, contas)
- `ContaCorrenteResponse`: status conta (saldo, bloqueios, situação)
- `LimiteDiarioResponse`: limites transacionais (disponível, total, autorizado)
- `QRCodeResponse`: dados QRCode Pix (valor, chave, favorecido)

---

### 7. Estruturas de Banco de Dados Lidas

**Não se aplica**. O sistema é um orquestrador que não acessa diretamente banco de dados. Todas as consultas são realizadas via APIs REST de outros microserviços.

---

### 8. Estruturas de Banco de Dados Atualizadas

**Não se aplica**. O sistema não atualiza diretamente banco de dados. Todas as atualizações são realizadas via chamadas REST a outros microserviços (ex: atualização de status de consentimento via API de consentimentos).

---

### 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `application.yml` | Leitura | Spring Boot (startup) | Configurações da aplicação (URLs de integração, timeouts, propriedades) |
| `logback-spring.xml` | Leitura | Logback (startup) | Configurações de logging (formato JSON, níveis, appenders) |
| `infra.yml` | Leitura | Kubernetes/OpenShift | Configurações de infraestrutura (secrets, configmaps, probes, volumes) |
| `prometheus.yml` | Leitura | Prometheus | Configuração de scraping de métricas do endpoint `/actuator/prometheus` |
| `grafana.ini` | Leitura | Grafana | Configurações do Grafana (dashboards, datasources, autenticação) |
| Logs JSON | Gravação | Logback (runtime) | Logs estruturados em JSON (console, async) |

---

### 10. Filas Lidas

**Não se aplica**. O sistema não consome mensagens de filas (JMS, Kafka, RabbitMQ, etc).

---

### 11. Filas Geradas

**Não se aplica**. O sistema não publica mensagens em filas.

---

### 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| `sboot-open-cons-orch-consentimento-pag-canal` | API REST | Gestão de consentimentos de pagamentos únicos e agendados. Operações: recuperar consentimento, atualizar status (AUTHORISED/REJECTED/CONSUMED/REVOKED), recuperar URL de redirecionamento |
| `sboot-open-cons-orch-recurring-payments-channel` | API REST | Gestão de consentimentos de pagamentos recorrentes (Pix Automático, Sweeping Accounts). Operações: recuperar consentimento, recuperar URL de redirecionamento |
| `sboot-glob-base-atom-cliente-dados-cadastrais` | API REST | Consulta de dados cadastrais do cliente (CPF, nome, contas) por número de conta |
| `sboot-ccbd-base-atom-conta-corrente` | API REST | Consulta de status de conta corrente (saldo, bloqueios, situação, permissões de débito) |
| `sboot-ccbd-base-orch-limites-v2` | API REST | Consulta de limites transacionais diários (TED, TEF, BOL, PIX). Retorna: disponível, total, autorizado, máximo configurado |
| `sboot-glob-base-atom-lista-bancos` | API REST | Consulta de nome de instituição financeira por código ISPB |
| `sboot-ccbd-base-orch-pix-qrcode` | API REST | Consulta e validação de QRCode Pix (estático e dinâmico). Retorna: valor, chave, tipo chave, dados favorecido |
| Gateway OAuth | OAuth2/JWT | Geração e validação de tokens JWT para autenticação e autorização. Extração de CPF do usuário logado |
| Revelock | Antifraude | Validação de `sessionId` para operações de aprovação/rejeição de consentimentos (segurança adicional) |

---

### 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- **Arquitetura bem estruturada**: Separação clara de responsabilidades (controller, service, repository, mapper, domain), seguindo princípios de DDD e arquitetura hexagonal (ports/adapters)
- **Uso adequado de Apache Camel**: Rotas Camel bem organizadas para orquestração de fluxos complexos, facilitando manutenção e evolução
- **Tratamento de exceções robusto**: Exceções customizadas para cada tipo de erro de negócio, handler global padronizando respostas HTTP 422
- **Testes unitários**: Presença de testes com JUnit 5 e Mockito, cobertura de cenários principais
- **Logs estruturados**: Formato JSON assíncrono, facilitando análise e integração com ferramentas de observabilidade
- **Segurança**: Integração OAuth2/JWT, validação de sessão antifraude (Revelock)
- **Configuração externalizada**: Uso de YAML para configurações, facilitando gestão de ambientes
- **Documentação de API**: Swagger/OpenAPI para documentação automática
- **Observabilidade**: Integração com Prometheus e Grafana para métricas e dashboards
- **Padrões de código**: Uso de Lombok para redução de boilerplate, enums para padronização, utilities para formatação

**Pontos de Melhoria:**
- **Documentação interna**: Falta de JavaDoc em algumas classes e métodos complexos
- **Testes de integração**: Não foram identificados testes de integração end-to-end (apenas unitários)
- **Validação de entrada**: Algumas validações de input poderiam ser mais rigorosas (ex: Bean Validation/JSR-303)
- **Tratamento de retry**: Não foi identificada estratégia explícita de retry para falhas de integração (embora Camel suporte)
- **Complexidade de mapeamento**: Classe `OpenBankingConsentimentoMapper` é extensa e complexa, poderia ser refatorada em mappers menores

---

### 14. Observações Relevantes

1. **Conformidade Open Finance Brasil**: Sistema implementa especificações Open Finance Brasil para iniciação de pagamentos, incluindo validações de tempo limite, status de consentimento e códigos de erro padronizados.

2. **Funil de Validação Assíncrono**: O funil de consentimento executa validações de forma assíncrona via rotas Camel. Se qualquer validação falhar, o sistema rejeita automaticamente o consentimento sem intervenção manual, atualizando o status para REJECTED com motivo apropriado.

3. **Suporte a Múltiplos Tipos de Pagamento**: Sistema suporta pagamentos únicos (single), agendados (scheduled) e recorrentes (recurring - Pix Automático, Sweeping Accounts), com validações específicas para cada tipo.

4. **Integração com Múltiplos Microserviços**: Orquestra chamadas a 7+ microserviços diferentes, consolidando informações de conta, limite, saldo, QRCode e dados cadastrais para validação completa do consentimento.

5. **Segurança em Camadas**: Além de OAuth2/JWT, sistema integra com Revelock para validação antifraude via `sessionId`, adicionando camada extra de segurança em operações críticas.

6. **Anonimização de Dados Sensíveis**: CPF/CNPJ são anonimizados nas respostas de API (formato `***.***.***-**`), protegendo dados pessoais.

7. **Preparado para Múltiplos Ambientes**: Configurações separadas para desenvolvimento, QA, UAT e produção, facilitando deploy em diferentes ambientes.

8. **Observabilidade Completa**: Integração com Prometheus para métricas (uptime, heap, CPU, threads, GC, HTTP) e Grafana para dashboards visuais, facilitando monitoramento e troubleshooting.

9. **CI/CD Automatizado**: Pipeline Jenkins configurado para build, testes (unitários, integração, funcionais, arquiteturais) e deploy em OpenShift.

10. **Arquitetura Preparada para Resiliência**: Uso de Apache Camel permite implementação de padrões de resiliência (retry, circuit breaker, fallback) de forma declarativa.

11. **Token Budget Configurado**: Sistema configurado com budget de 200.000 tokens, indicando preparação para processamento de alto volume.

12. **Validação de Arquitetura**: Uso de ArchUnit para testes arquiteturais, garantindo conformidade com padrões definidos (ex: dependências entre camadas, nomenclatura de pacotes).

---