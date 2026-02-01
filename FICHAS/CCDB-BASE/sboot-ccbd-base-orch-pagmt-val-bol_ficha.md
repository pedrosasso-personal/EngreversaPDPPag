---
## Ficha Técnica do Sistema

### 1. Descrição Geral
Sistema de validação de pagamento de boletos bancários desenvolvido em Java com Spring Boot e Apache Camel. O sistema orquestra a validação completa de boletos (cobrança, consumo e tributos), realizando consultas em múltiplos serviços externos (CIP, Celcoin), validações de limites, saldo, grade horária, calendário de dias úteis, elegibilidade para cashback e listagem de cartões do usuário. Oferece APIs REST versionadas (V1 a V4) com evolução incremental de funcionalidades. Implementa regras complexas de agendamento automático quando limites são excedidos ou pagamentos ocorrem fora do horário permitido.

---

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ValidarPagamentoBoletoController** | Controller REST V1 - validação básica de boletos |
| **ValidarPagamentoBoletoControllerV2** | Controller REST V2 - adiciona consulta de saldo via headers opcionais |
| **ValidarPagamentoBoletoControllerV3** | Controller REST V3 - adiciona listagem de cartões do usuário |
| **ValidarPagamentoBoletoControllerV4** | Controller REST V4 - estrutura de resposta detalhada e otimizada |
| **ValidarPagamentoBoletoService** | Serviço V1 - orquestra validação via BoletoRouter (Camel) |
| **ValidarPagamentoBoletoServiceV2** | Serviço V2 - orquestra via ConsultarBoletoRouter com lógica recursiva de agendamento |
| **CartaoService** | Serviço para listagem de cartões do usuário |
| **ConsultarBoletoRouter** | Rota Camel principal - consulta paralela (saldo, boleto CIP/Celcoin, cartões, cashback) |
| **ValidacaoLimiteRouter** | Rota Camel - validação de limites, grade horária e vencimento |
| **SalvarDadosCIPRouter** | Rota Camel - cálculo, persistência e consulta calendário (CIP) |
| **SalvarDadosCellcoinRouter** | Rota Camel - conversão, persistência e consulta calendário (Celcoin) |
| **BoletoRouter** | Rota Camel legada (V1) - fluxo sequencial de validação |
| **BoletoCIPRepositoryImpl** | Consulta boletos de cobrança via API CIP |
| **ConsultarCelcoinRepositoryImpl** | Consulta boletos de consumo/tributos via API Celcoin (IS2B) |
| **ConsultarLimitesRepositoryImpl** | Verifica limites diários/noturnos de transação |
| **ConsultarSaldoRepositoryImpl** | Consulta saldo de conta corrente |
| **CalcularBoletoRepositoryImpl** | Calcula juros, multa, desconto e abatimento |
| **ListaCartoesUsuarioRepositoryImpl** | Lista cartões do usuário autenticado |
| **ConsultaAdesaoCashbackRepositoryImpl** | Verifica adesão do cliente ao programa cashback |
| **ConsultaSaldoClienteCashbackRepositoryImpl** | Consulta saldo disponível de cashback |
| **ValidarDataRepositoryImpl** | Valida se data de transferência é dia útil |
| **ValidarGradeHorarioValorRepositoryImpl** | Valida grade horária (cobrança 6h-22h, tributo 7:35-16:25) |
| **VerificaDataVencimentoUtilRepositoryImpl** | Ajusta data de vencimento para próximo dia útil |
| **SalvarDadosBoletoRepositoryImpl** | Persiste comprovante de boleto |
| **AccessTokenRepositoryImpl** | Gera token OAuth2 para integração Celcoin (IS2B) |
| **ValidarBoletoMapper** | Converte requisições REST para objetos de domínio |
| **ValidarBoletoResponseMapper** | Converte objetos de domínio para respostas REST |
| **ConversorCartaoDTO** | Converte lista de cartões para representação REST |
| **CodigoBarrasUtil** | Utilitário para conversão linha digitável ↔ código de barras |
| **GradeHorarioUtil** | Valida horários permitidos para pagamento |
| **ObterCpf** | Extrai CPF do usuário autenticado (JWT ou header) |
| **ValidarCpfPagadorUtil** | Valida CPF pagador vs beneficiário (fraude cashback) |
| **ExceptionUtil** | Converte exceções Camel para ResponseEntity padronizado |
| **CamelContextWrapper** | Wrapper para inicialização e acesso ao contexto Camel |
| **MdcThreadPoolExecutor** | ThreadPoolExecutor customizado para propagação de MDC (logs) |
| **BoletoCompleto** | Entidade de domínio agregadora (boleto + cartões + cashback + limites) |
| **ExceptionReasonEnum** | Enum com 64+ códigos de erro de negócio |
| **TipoBancoEnum** | Enum com 200+ bancos mapeados |
| **TipoEspecieTituloCobrancaEnum** | Enum com 35 espécies de títulos (DM, CH, NP, CC, etc) |

---

### 3. Tecnologias Utilizadas

- **Java 11** (JDK 11)
- **Spring Boot 2.1.9.RELEASE**
- **Apache Camel 3.0.1** (orquestração de rotas e integrações)
- **Spring Security OAuth2** (autenticação via JWT)
- **Spring Web** (REST Controllers)
- **Spring RestTemplate** (cliente HTTP para APIs externas)
- **Lombok** (redução de boilerplate)
- **Jackson** (serialização JSON)
- **SLF4J + Logback** (logging com MDC para rastreabilidade)
- **Swagger/OpenAPI 3.0** (documentação de APIs)
- **JUnit 5** (testes unitários)
- **Mockito** (mocks para testes)
- **Maven** (gerenciamento de dependências e build)
- **OpenShift Container Platform (OCP)** (deployment)
- **Jenkins** (CI/CD)

---

### 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/pagamento-boleto/validar` | ValidarPagamentoBoletoController | Validação básica de boleto (linha digitável ou código de barras) |
| POST | `/v2/banco-digital/pagamentos-boleto/validacao` | ValidarPagamentoBoletoControllerV2 | Validação com consulta de saldo via headers opcionais (codigoBanco, numeroAgencia, numeroConta, numeroCpfCnpj) |
| POST | `/v3/banco-digital/pagamentos-boleto/validacao` | ValidarPagamentoBoletoControllerV3 | Validação com listagem de cartões do usuário (exceto boletos BV) |
| POST | `/v4/banco-digital/pagamentos-boleto/validacao` | ValidarPagamentoBoletoControllerV4 | Validação com estrutura de resposta detalhada (beneficiário, avalista, pagador, emissor, limites, cartões, cashback) |

---

### 5. Principais Regras de Negócio

1. **Validação de Data de Transferência**: Verifica se a data de transferência é dia útil. Ajusta automaticamente para o próximo dia útil caso não seja. Tratamento especial para véspera de Réveillon (31/12) e grade especial 2022 (30/12 → 02/01/2023).

2. **Grade Horária de Pagamento**:
   - **Boletos de Cobrança**: Permitido entre 06:00 e 22:00
   - **Boletos de Tributo/Consumo**: Permitido entre 07:35 e 16:25
   - **Véspera de Natal**: Grade ajustada
   - Pagamentos fora do horário são automaticamente agendados para o próximo dia útil

3. **Validação de Limites**:
   - Verifica limite diário e noturno de transações
   - Compara valor do boleto com limite disponível
   - Se limite insuficiente e `permiteAgendamentoAutomatico=true`, agenda automaticamente para D+1
   - Advertência de limite noturno não bloqueia, apenas informa

4. **Consulta de Saldo**: Consulta saldo da conta corrente e emite advertência se saldo indisponível (não bloqueia transação)

5. **Bifurcação por Tipo de Boleto**:
   - **Boletos de Cobrança** (linha digitável 47 posições, não inicia com "8"): Consulta via CIP
   - **Boletos de Consumo/Tributo** (linha digitável 48 posições, inicia com "8"): Consulta via Celcoin (IS2B)

6. **Cálculo de Valores**: Calcula juros, multa, desconto e abatimento sobre o valor original do boleto

7. **Validação de Vencimento**:
   - Permite pagamento de boleto vencido se dentro do limite
   - Ajusta data de vencimento para próximo dia útil se não for dia útil
   - Valida se data de vencimento >= data de transferência (Celcoin)

8. **Validação de Duplicidade**: Verifica situação do título (baixado, bloqueado, apto para pagamento)

9. **Validação de CPF Pagador**: Para boletos de espécie "33" (cash-in/cartão de crédito), valida se CPF do pagador é diferente do CPF do beneficiário para evitar fraude de cashback

10. **Elegibilidade para Cashback**:
    - Verifica adesão do cliente ao programa cashback
    - Consulta saldo disponível de cashback
    - Valida se boleto é elegível (não BV, não cash-in)

11. **Listagem de Cartões**: Lista cartões do usuário autenticado, exceto para boletos BV ou cash-in (código espécie "33")

12. **Advertências Mapeadas**: Sistema emite advertências sem bloquear transação (ex: boleto vencido, cedente não autorizado, valor fora do mínimo/máximo, fatura de cartão duplicada, mesmo beneficiário)

13. **Agendamento Recursivo**: Se limite insuficiente e agendamento automático permitido, tenta agendar recursivamente até encontrar data com limite disponível

14. **Validação de Boleto BV**: Identifica boletos do próprio banco (BV/BVF/CISAO) pelo CNPJ do beneficiário original

15. **Fatura de Cartão Vencida**: Para código de espécie "31" (fatura cartão), se vencimento anterior à data de transferência, ajusta vencimento para data de transferência

---

### 6. Relação entre Entidades

**Principais Entidades e Relacionamentos:**

- **BoletoCompleto** (agregador raiz):
  - Contém **Boleto** (dados CIP ou Celcoin)
  - Contém **SaldoContaCorrente**
  - Contém **LimiteAgendamento**
  - Contém **ListaDetalheCartao** (lista de **DetalheCartao**)
  - Contém **ConsultaAdesaoCashbackResponse**
  - Contém **ConsultaSaldoClienteCashbackResponse**

- **Boleto**:
  - Contém **Beneficiario**
  - Contém **Avalista**
  - Contém **Pagador**
  - Contém **Emissor**
  - Contém **ValorDocumento**
  - Contém **CalcularBoleto** (juros, multa, desconto, abatimento)

- **DetalheCartao**:
  - Contém **Bandeira**
  - Contém **Modalidade**
  - Contém **Limite**
  - Contém **Fatura**

- **LimiteAgendamento**:
  - Contém lista de **Advertencia**
  - Relaciona-se com **TipoLimiteEnum** (DIARIO, NOTURNO)

**Fluxo de Dados:**
1. Controller recebe requisição REST
2. Mapper converte para objetos de domínio
3. Service orquestra via Camel Routes
4. Repositories consultam APIs externas
5. Processors/Aggregators consolidam respostas
6. Mapper converte para representação REST
7. Controller retorna resposta

---

### 7. Estruturas de Banco de Dados Lidas

não se aplica

**Observação**: O sistema não acessa banco de dados diretamente. Todas as consultas são realizadas via APIs REST externas (CIP, Celcoin, Saldo, Limites, Cartões, Cashback, etc). A persistência de dados é delegada para serviços externos via chamadas HTTP.

---

### 8. Estruturas de Banco de Dados Atualizadas

não se aplica

**Observação**: O sistema não atualiza banco de dados diretamente. A persistência de comprovantes de boleto é realizada via API externa (`serviceGuardaBoletoComprovante`).

---

### 9. Arquivos Lidos e Gravados

não se aplica

**Observação**: O sistema não lê ou grava arquivos locais. Toda entrada/saída de dados ocorre via APIs REST e logs (SLF4J/Logback).

---

### 10. Filas Lidas

não se aplica

**Observação**: O sistema não consome mensagens de filas (JMS, Kafka, RabbitMQ, etc).

---

### 11. Filas Geradas

não se aplica

**Observação**: O sistema não publica mensagens em filas (JMS, Kafka, RabbitMQ, etc).

---

### 12. Integrações Externas

| Sistema Externo | Tipo | Descrição | Classe Responsável |
|-----------------|------|-----------|-------------------|
| **CIP** | API REST | Consulta boletos de cobrança | BoletoCIPRepositoryImpl |
| **Celcoin (IS2B)** | API REST OAuth2 | Consulta boletos de consumo/tributos | ConsultarCelcoinRepositoryImpl, AccessTokenRepositoryImpl |
| **API Saldo** | API REST | Consulta saldo de conta corrente | ConsultarSaldoRepositoryImpl |
| **API Limites** | API REST | Verifica limites diários/noturnos de transação | ConsultarLimitesRepositoryImpl |
| **API Dias Úteis** | API REST | Valida dias úteis e obtém próximo dia útil | ValidarDataRepositoryImpl, ObterProximoDiaUtilRepositoryImpl |
| **API Cálculo Boleto** | API REST | Calcula juros, multa, desconto e abatimento | CalcularBoletoRepositoryImpl |
| **API Cartões** | API REST | Lista cartões do usuário | ListaCartoesUsuarioRepositoryImpl |
| **API Cashback Adesão** | API REST | Verifica adesão ao programa cashback | ConsultaAdesaoCashbackRepositoryImpl |
| **API Cashback Saldo** | API REST | Consulta saldo disponível de cashback | ConsultaSaldoClienteCashbackRepositoryImpl |
| **API Salvar Boleto** | API REST | Persiste comprovante de boleto | SalvarDadosBoletoRepositoryImpl |
| **API Calendário** | API REST | Consulta data limite de pagamento de título | ConsultarDataCalendarioRepositoryImpl |
| **JBoss EJB (SCalendario)** | EJB Legado | Validação de calendário (legado) | ConsultarDataCalendarioRepositoryImpl |

**Configuração de Endpoints**: URLs configuradas via variáveis de ambiente (ENV VARS) para ambientes des/qa/uat/prd. Secrets para credenciais (usuário/senha, client_id/client_secret Celcoin).

---

### 13. Avaliação da Qualidade do Código

**Nota:** 8.5/10

**Justificativa:**

**Pontos Positivos:**
- **Arquitetura Modular**: Separação clara entre camadas (domain, application, infrastructure). Uso de Apache Camel para orquestração de rotas facilita manutenção e evolução.
- **Testes Abrangentes**: Cobertura extensiva de testes unitários (JUnit 5 + Mockito) para controllers, services, repositories, utils e rotas Camel. Profiles Maven para diferentes tipos de testes (unit/integration/functional/architecture).
- **Boas Práticas Spring Boot**: Uso adequado de anotações, injeção de dependências, configuração externalizada (application.yml + ENV VARS), profiles para ambientes.
- **Tratamento de Exceções**: Exceções tipadas de domínio (BoletoInvalidoException, AgendarPagamentoException, TimeoutServiceException) com mapeamento para códigos de erro padronizados (ExceptionReasonEnum com 64+ códigos).
- **Documentação de API**: Swagger/OpenAPI 3.0 para documentação interativa dos endpoints REST.
- **Rastreabilidade**: Uso de MDC (SLF4J) para propagação de contexto de logs entre threads (MdcThreadPoolExecutor customizado).
- **Versionamento de API**: Evolução incremental de funcionalidades através de versões (V1 a V4) mantendo compatibilidade.
- **Redução de Boilerplate**: Uso de Lombok para getters/setters/builders.
- **Enums para Mapeamentos**: Enums bem estruturados para bancos, espécies de títulos, situações, tipos de limite, códigos de erro Celcoin.

**Pontos de Melhoria:**
- **Documentação Inline**: Falta de JavaDoc em algumas classes e métodos críticos. Comentários explicativos poderiam melhorar a compreensão de regras de negócio complexas.
- **Complexidade de Rotas Camel**: Algumas rotas (ConsultarBoletoRouter) possuem lógica complexa com múltiplos processadores e agregadores. Poderia ser refatorado em sub-rotas menores.
- **Hardcoding de Valores**: Alguns valores hardcoded (ex: códigos de banco "200", "201", praças "SP", "BR", código espécie "33", "31") poderiam ser externalizados para constantes ou configuração.
- **Tratamento de Timeout**: Retry de 3 tentativas para timeout é fixo. Poderia ser configurável.
- **Validações de Entrada**: Algumas validações de entrada (ex: tamanho de linha digitável, formato de data) poderiam usar Bean Validation (JSR-303) para maior padronização.
- **Testes de Integração**: Embora haja testes unitários extensivos, não há evidências de testes de integração end-to-end com ambientes de homologação.

---

### 14. Observações Relevantes

1. **Evolução de Versões**:
   - **V1**: Validação básica via BoletoRouter (fluxo sequencial legado)
   - **V2**: Adiciona consulta de saldo via headers opcionais + ConsultarBoletoRouter (fluxo paralelo otimizado)
   - **V3**: Adiciona listagem de cartões do usuário
   - **V4**: Estrutura de resposta detalhada e otimizada (beneficiário, avalista, pagador, emissor, limites, cartões, cashback)

2. **Processamento Paralelo**: ConsultarBoletoRouter utiliza multicast para consultas paralelas (saldo, boleto CIP/Celcoin, cartões, cashback), reduzindo latência total.

3. **Agendamento Automático Recursivo**: Lógica sofisticada em ValidarPagamentoBoletoServiceV2 que tenta agendar recursivamente até encontrar data com limite disponível (máximo 30 dias).

4. **Grade Horária Especial**: Tratamento de datas especiais (véspera de Natal, Réveillon, grade 2022) demonstra atenção a requisitos de negócio complexos.

5. **Segurança**: Autenticação via OAuth2 JWT. Extração de CPF do usuário autenticado para validações de fraude.

6. **Resiliência**: Retry automático (3 tentativas) para timeouts em integrações externas. Tratamento de exceções HTTP (4xx, 5xx) com mapeamento para códigos de erro de negócio.

7. **Configuração Multi-Ambiente**: Suporte para ambientes des/qa/uat/prd via profiles Spring e variáveis de ambiente.

8. **Logging Estruturado**: Logs em formato JSON (Logback) com MDC para rastreabilidade distribuída.

9. **CI/CD**: Integração com Jenkins para build e deploy automatizado no OpenShift.

10. **Mapeamento de Bancos**: Enum TipoBancoEnum com 200+ bancos brasileiros mapeados, demonstrando abrangência do sistema.

11. **Advertências vs Bloqueios**: Sistema diferencia advertências (informativas, não bloqueiam) de erros (bloqueiam transação), proporcionando melhor experiência ao usuário.

12. **Validação de Fraude Cashback**: Regra específica para evitar fraude em boletos de cash-in (espécie "33") onde pagador e beneficiário são a mesma pessoa.

13. **Compatibilidade com Legado**: Integração com sistema legado JBoss EJB (SCalendario) para validação de calendário.

14. **Modularização Maven**: Projeto dividido em módulos (domain, application) para melhor organização e reuso.

15. **Swagger Desabilitado em Produção**: Profile `!prod` garante que documentação Swagger não seja exposta em ambiente produtivo.

---

**Conclusão**: Sistema robusto e bem estruturado para validação de pagamento de boletos, com arquitetura modular, testes abrangentes, tratamento de exceções sofisticado e integração com múltiplos serviços externos. Demonstra maturidade técnica e atenção a requisitos de negócio complexos do setor bancário brasileiro.