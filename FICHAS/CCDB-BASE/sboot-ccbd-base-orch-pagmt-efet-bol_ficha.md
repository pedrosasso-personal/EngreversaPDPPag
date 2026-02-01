# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema orquestrador de pagamentos e efetivação de boletos bancários (cobrança, consumo e tributos) para ambiente de banco digital. Processa pagamentos via conta corrente ou cartão de crédito, realizando validações de negócio, integrações com sistemas legados e externos, controle de fraudes, cálculo de tarifas/tributos, e gerenciamento de agendamentos. Utiliza arquitetura de microsserviços com Spring Boot e Apache Camel para orquestração de fluxos complexos.

---

## 2. Principais Classes e Responsabilidades

| Classe/Componente | Responsabilidade |
|-------------------|------------------|
| `Application.java` | Classe main inicializadora da aplicação Spring Boot |
| `EfetPagmtBolService` | Orquestra lógica de negócio de pagamento de boletos, validação de dias úteis e agendamentos |
| `NotificarFraudeService` | Gerencia notificações de análise de fraudes |
| `ValidarStatusService` | Valida status de transações em análise de fraude |
| `EfetivarRouter` | Rota Apache Camel para efetivação de pagamentos (débito conta/cartão crédito) |
| `AgendarRouter` | Rota Apache Camel para agendamento de pagamentos futuros |
| `AnaliseFraudeRouter` | Rota para consulta de status de fraude |
| `NotificarFraudeRouter` | Rota para notificação de fraudes |
| `ValidaPagamentoBoletoAlteracaoValor` | Processor para validação de alteração de valores em boletos |
| `DesfazerLancamentoProcessor` | Processor para estorno de lançamentos em caso de erro |
| `ErrorProcessor` | Processor centralizado de tratamento de erros |
| `BoletoCobracaRegraStrategy` | Strategy para validação de valores de boletos de cobrança |
| `BoletoConsumoTributoRegraStrategy` | Strategy para validação de valores de boletos de consumo/tributo |
| Controllers V1-V5 | Endpoints REST multi-versão para efetivação de pagamentos |
| Repositories (18+) | Interfaces de integração com APIs externas e sistemas legados |
| Mappers | Conversão entre DTOs (AgendamentoMapper, PagamentoCobrancaMapper, etc) |

---

## 3. Tecnologias Utilizadas

- **Framework Principal:** Spring Boot 2.x
- **Orquestração:** Apache Camel 3.0.1
- **Mensageria:** RabbitMQ (AMQP), IBM MQ (JMS)
- **Segurança:** Spring Security OAuth2 JWT
- **Mapeamento Objetos:** MapStruct
- **Documentação API:** Swagger/OpenAPI, Springfox
- **Logging:** Logback com formato JSON estruturado
- **Métricas:** Micrometer, Prometheus (porta 9090)
- **Servidor Web:** Undertow
- **Build:** Maven (multi-módulo)
- **Testes:** JUnit 5, Mockito, RestAssured, Pact (testes contrato)
- **Feature Toggle:** ConfigCat
- **Clientes REST:** Feign, RestTemplate, WebClient
- **Banco de Dados:** Acesso via APIs (não acesso direto)
- **Linguagem:** Java 11
- **Containerização:** Docker (RabbitMQ local)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/efetivar-pagamento-boleto` | Controller V1 | Efetivação de pagamento de boleto (versão 1) |
| POST | `/v2/efetivar-pagamento-boleto` | Controller V2 | Efetivação de pagamento de boleto (versão 2) |
| POST | `/v3/efetivar-pagamento-boleto` | Controller V3 | Efetivação com headers: codigoBanco, numeroAgencia, numeroConta, cpfCnpj |
| POST | `/v4/efetivar-pagamento-boleto` | Controller V4 | Efetivação com headers similares à V3 (evolutiva) |
| POST | `/v5/efetivar-pagamento-boleto/{idTransacao}` | Controller V5 | Efetivação com validação de fraude integrada |

**Observação:** Múltiplas versões mantidas para compatibilidade evolutiva sem quebra de contratos.

---

## 5. Principais Regras de Negócio

1. **Validação de Dia Útil:** Pagamentos só são processados em dias úteis; caso contrário, são agendados para o próximo dia útil disponível
2. **Comparação Data Entrada vs Próximo Dia Útil:** Decisão automática entre agendar ou efetivar imediatamente
3. **Validação de Alteração de Valor:** Regras específicas por tipo de boleto (Cobrança vs Consumo/Tributo) - verifica se permite alteração, valores mínimos/máximos
4. **Validação de Duplicidade:** Verifica boletos já pagos nas últimas 48 horas (NSU/linha digitável) - inclui efetivados e agendados
5. **Validação de Limites Transacionais:** Consulta limites diurno/noturno/valor antes da efetivação
6. **Grade Horária:** Validação de horário permitido para pagamento (tributos até 16h25, transferências até 17h, valores > R$ 250k até 17h)
7. **Diferenciação Boleto Cobrança vs Consumo/Tributo:** Fluxos e validações específicas por tipo
8. **Forma de Pagamento:** Suporte a conta corrente (débito) ou cartão de crédito (com IOF e tarifas)
9. **Bloqueio Pagamento Fatura BV/BVF:** Não permite pagamento de fatura dos bancos BV (436/413) e Votorantim (161/655) com cartão de crédito
10. **Validação Valor Mínimo Cartão:** R$ 1,00 para pagamentos com cartão
11. **Feature Toggle Desacoplamento:** Flag controla fluxo novo (esteira SPAG) vs legado
12. **Resiliência:** Retry automático (3 tentativas, delay 1500ms), desfazimento de lançamentos em caso de erro
13. **Análise de Fraude:** Consulta status, notificação via fila RabbitMQ, bloqueio se reprovado
14. **Cálculo Tarifas/Encargos/Tributos:** Integração com tarifador DXC para cálculo de custos
15. **Autorização Cartão:** Validação com autorizador antes de efetivar pagamento
16. **Validação CPF Pagador:** Para espécie cash-in (33) e forma de pagamento cartão
17. **Conta Balde:** Operações especiais configuráveis para BV/Votorantim
18. **Protocolo Múltiplo:** Geração de protocolos inicial, pagamento e devolução (NSU)
19. **Validação Boleto Vencido:** Rejeita boletos com vencimento expirado
20. **Compensação Automática:** Desfaz lançamentos e autorizações em caso de falha no fluxo

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **EfetPagmtBolDTO** (Entidade Central)
  - Contém: `InfoTribBolDTO` (dados do boleto)
  - Contém: `CartaoSelecionado` (opcional, se pagamento via cartão)
  - Relaciona-se com: `OperacaoPagmtBolDTO` (wrapper da operação)

- **OperacaoPagmtBolDTO**
  - Agrega: `EfetPagmtBolDTO`
  - Contém: dados remetente/favorecido (CPF/CNPJ, nome, banco, conta, agência)

- **Agendamento**
  - Relaciona-se com: `Pessoa` (remetente e favorecido)
  - Contém: datas, valores, tipo transação

- **TransferenciaDTO**
  - Contém: `InfoConta` (remetente e favorecido)
  - Usado para transferências entre contas balde

- **StatusFraudeResponse**
  - Contém: `PayloadBoleto`
  - Relaciona-se com: idTransacao, idFraudes, idEfetivacao

**Relacionamentos:**
- 1:1 entre EfetPagmtBolDTO e InfoTribBolDTO
- 0:1 entre EfetPagmtBolDTO e CartaoSelecionado
- 1:N entre Agendamento e Pessoa (remetente/favorecido)
- Composição entre OperacaoPagmtBolDTO e EfetPagmtBolDTO

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| Tabelas de Agendamento | Tabela | SELECT | Consulta agendamentos existentes via API `sboot-ccbd-base-atom-agendamento` |
| Movimentações Conta Corrente | Tabela | SELECT | Consulta movimentações via API `sboot-ccbd-base-atom-movimentacoes` |
| Dados Cadastrais Cliente | Tabela | SELECT | Consulta dados pessoa (CPF/CNPJ) via API `sboot-glob-base-atom-cliente-dados-cadastrais` |
| Comprovantes Pagamento | Tabela | SELECT | Consulta comprovantes via API `sboot-ccbd-base-atom-pgto-trib-bol` |
| Limites Transacionais | Tabela | SELECT | Consulta limites diurno/noturno via API específica |
| Dias Úteis | Tabela | SELECT | Validação calendário via API `sboot-dcor-base-atom-dias-uteis` |
| Status Boleto | Tabela | SELECT | Recuperação dados boleto via API legado |
| Tarifas | Tabela | SELECT | Consulta tarifas via API `sboot-trbd-base-atom-tarifador` |

**Observação:** Acesso indireto via APIs REST - não há acesso direto ao banco de dados.

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| Agendamentos | Tabela | INSERT/UPDATE | Inserção/atualização de agendamentos via API `sboot-ccbd-base-atom-agendamento` |
| Lançamentos Contábeis | Tabela | INSERT/DELETE | Débitos/créditos em conta corrente, estornos via API movimentações |
| Comprovantes | Tabela | INSERT/UPDATE | Inserção comprovante inicial e atualização com dados finais via API `sboot-ccbd-base-atom-pgto-trib-bol` |
| Status Boletos | Tabela | UPDATE | Atualização status após pagamento via APIs SPAG |
| Movimentações Bancárias | Tabela | INSERT | Registro de movimentações via API `sboot-pgft-base-orch-pagamentos` |
| Autorizações Cartão | Tabela | INSERT/DELETE | Registro e estorno de autorizações via API `sboot-cart-svhp-atom-autorizador` |
| Transações Fraude | Tabela | UPDATE | Atualização status fraude via API `sboot-gtbd-base-atom-gestao-transacoes` |

**Observação:** Todas as operações realizadas via APIs REST - não há acesso direto ao banco de dados.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `application.yml` | Leitura | Raiz do projeto | Configurações multi-perfil (local, des, qa, uat, prd) |
| `application-{profile}.yml` | Leitura | Raiz do projeto | Configurações específicas por ambiente |
| Logs JSON | Gravação | Logback | Logs estruturados em formato JSON |
| Swagger YAMLs | Leitura | Diretório de recursos | Contratos OpenAPI para geração de clientes |
| `pom.xml` | Leitura | Maven | Configuração de build e dependências |
| `docker-compose.yml` | Leitura | Infra local | Configuração RabbitMQ para ambiente local |

---

## 10. Filas Lidas

| Nome da Fila | Tecnologia | Descrição |
|--------------|-----------|-----------|
| `QM.DIG.01` (canal `CCBD.SRVCONN`) | IBM MQ (JMS) | Integração com sistemas legados - consumo de mensagens de liquidação |

**Observação:** Consumo de filas RabbitMQ não explícito neste pacote (possivelmente em outros microsserviços).

---

## 11. Filas Geradas

| Nome da Fila/Exchange | Tecnologia | Routing Key | Descrição |
|-----------------------|-----------|-------------|-----------|
| `ex.ccbd.notificacao.fraudes` | RabbitMQ | N/A | Exchange para notificação de transações em análise de fraude |
| `ex.ccbd.eventos.transacional` | RabbitMQ | `ccbd.rk.transacional.envio.spag.boleto.cobranca` | Envio de pagamentos de boleto de cobrança para esteira SPAG |
| `ex.ccbd.eventos.transacional` | RabbitMQ | `ccbd.rk.transacional.envio.spag.boleto.tributo` | Envio de pagamentos de boleto de tributo para esteira SPAG |
| `exchangeFraudes` | RabbitMQ | `ccbd.atualizarStatusFraude.v1` | Atualização de status de fraude |
| `QL.CCBD.LIQ_PAGMT_CONTAS_DIG.INT` | IBM MQ (JMS) | N/A | Fila de liquidação de pagamentos para sistemas legados |
| `queueNameCash` | IBM MQ (JMS) | N/A | Fila de transferências (configurável) |

---

## 12. Integrações Externas

| Sistema/API | Tipo | Descrição |
|-------------|------|-----------|
| `sboot-spag-base-orch-pagamento-boleto-srv` | REST | Envio de pagamentos de boleto de cobrança |
| `sboot-spag-base-orch-pagamento-tributo-srv` | REST | Envio de pagamentos de tributo/consumo |
| `sboot-spag-base-orch-suporte-negocio` | REST | Validação de regras de negócio de pagamento |
| `sboot-pgft-base-orch-pagamentos` | REST | Efetivação de movimentos contábeis |
| `sboot-gtbd-base-atom-gestao-transacoes` | REST | Gestão de transações e análise de fraude |
| `sboot-ccbd-base-atom-movimentacoes` | REST | Consulta e registro de movimentações |
| `sboot-ccbd-base-atom-agendamento` | REST | CRUD de agendamentos de pagamentos |
| `sboot-glob-base-atom-cliente-dados-cadastrais` | REST | Consulta de dados cadastrais de clientes |
| `sboot-trbd-base-atom-tarifador` | REST | Cálculo de tarifas (DXC) |
| `sboot-cart-svhp-atom-autorizador` | REST | Autorização de pagamentos com cartão de crédito |
| `sboot-dcor-base-atom-dias-uteis` | REST | Validação de dias úteis |
| `sboot-ccbd-base-atom-pgto-trib-bol` | REST | Gestão de comprovantes de pagamento |
| Sistemas Legados ESB | SOAP/EJB | Integração com sistemas legados via facade `br.com.bvsistemas.contacorrente.*` |
| API Gateway OAuth2 | REST | Autenticação e autorização JWT |
| ConfigCat | REST | Feature Toggle (chave: `Zp3ZCM4oLE6Bd-_HU_Uvlw/udgRUjxGRkK1VwHfHRYh0Q`) |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada com separação clara entre camadas (application/domain)
- Uso adequado de design patterns (Builder, DTO, Repository, Strategy)
- Rotas Apache Camel bem organizadas com tratamento de exceções robusto
- Multi-versionamento de API permite evolução sem quebra de contratos
- Logs estruturados em JSON facilitam observabilidade
- Configuração externalizada por perfis (ambientes)
- Resiliência implementada com retry e fallback
- Testes automatizados (JUnit 5, Mockito, RestAssured, Pact)
- Documentação OpenAPI/Swagger
- Feature Toggle para controle de funcionalidades

**Pontos Negativos:**
- Código comentado em várias classes indica débito técnico
- Alto acoplamento com múltiplas APIs externas (18+ repositories)
- Lógica de validação de dias úteis distribuída entre service e router (falta coesão)
- Contratos gerados automaticamente (não editáveis diretamente) podem dificultar manutenção
- Exceções específicas poderiam centralizar mensagens de erro
- Enums muito extensos (TipoBancoEnum com 200+ bancos, ExceptionReasonEnum com 70+ exceções)
- Falta de documentação inline em métodos complexos
- Alguns métodos com muitos parâmetros (baixa coesão)

**Recomendações:**
- Remover código comentado
- Refatorar lógica de dias úteis para um único componente
- Considerar uso de cache para consultas frequentes (bancos, dias úteis)
- Implementar circuit breaker para integrações externas
- Adicionar mais testes de integração
- Documentar regras de negócio complexas

---

## 14. Observações Relevantes

1. **Feature Toggle:** Sistema utiliza ConfigCat para controle de funcionalidades, especialmente para desacoplamento entre agendamento e esteira SPAG (chave: `FT_DESACOPLAMENTO_AGENDAMENTO_ATIVO`)

2. **Conta Balde BVF:** Configuração especial para operações com contas balde dos bancos BV (413) e Votorantim (655)

3. **NSU (Número Sequencial Único):** Utilizado para rastreabilidade de transações em todo o fluxo

4. **Protocolo Múltiplo:** Sistema gera três tipos de protocolos: inicial, pagamento e devolução

5. **IOF:** Calculado automaticamente para operações com cartão de crédito

6. **Retry Configurável:** Sistema implementa retry com 3 tentativas e delay de 1500ms entre tentativas

7. **Autenticação:** JWT via API Gateway OAuth2

8. **Health/Metrics:** Porta 9090 dedicada para Prometheus (métricas)

9. **Swagger Codegen:** Geração automática de clientes de APIs a partir de contratos YAML

10. **Pré-processamento:** Validações extensivas antes de chamadas externas para evitar processamento desnecessário

11. **Pós-processamento:** Atualização de comprovantes e limites após efetivação

12. **Compensação:** Mecanismo de desfazimento de lançamentos e autorizações em caso de falha

13. **Multi-versão:** Suporte a 5 versões de API simultaneamente para compatibilidade

14. **Tipos de Boleto:** Sistema diferencia boletos de cobrança, consumo e tributo com fluxos específicos

15. **Grade Horária:** Restrições de horário específicas por tipo de operação (tributos até 16h25, transferências até 17h, valores altos até 17h)

16. **Validação 48h:** Sistema valida duplicidade considerando janela de 48 horas

17. **Conta Corrente vs Cartão:** Fluxos distintos com validações específicas (IOF, tarifas, autorização)

18. **Esteira SPAG:** Nova esteira de pagamentos com desacoplamento configurável via feature toggle

19. **Bancos BV/BVF:** Tratamento especial para bancos do grupo (códigos 436, 413, 161, 655)

20. **Valor Mínimo:** R$ 1,00 para pagamentos com cartão de crédito

21. **Container:** Utiliza Undertow ao invés de Tomcat para melhor performance

22. **Build:** Maven multi-módulo (domain + application)

23. **Ambiente Local:** Docker Compose para RabbitMQ local (portas 5672, 15672, 15692)

24. **Pact:** Testes de contrato configurados (broker localhost:9292)

25. **ArchUnit:** Testes de arquitetura para garantir conformidade com padrões