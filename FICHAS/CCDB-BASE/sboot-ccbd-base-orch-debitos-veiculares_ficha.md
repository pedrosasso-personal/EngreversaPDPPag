# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-ccbd-base-orch-debitos-veiculares** é um microserviço orquestrador responsável por centralizar e processar operações relacionadas a débitos veiculares (IPVA, DPVAT, Licenciamento, Multas e RENAINF). O sistema atua como intermediário entre canais digitais do Banco Votorantim e múltiplos sistemas legados (ACL Banco Rendimento, SPAG, DXC), consolidando consultas de débitos, processando pagamentos via conta corrente ou cartão de crédito, gerando recibos e extratos, além de realizar transferências bancárias e notificações assíncronas.

A arquitetura utiliza Apache Camel para orquestração de fluxos complexos, Spring Boot para infraestrutura REST/SOAP, e mensageria (RabbitMQ/GCP PubSub) para processamento assíncrono de liquidações.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application.java** | Bootstrap Spring Boot com habilitação de OAuth2 Resource Server e Feature Toggle |
| **DebitosVeicularesController** | Endpoints REST v1 para consulta débitos, pagamento, cálculo parcelas e extrato |
| **DebitosVeicularesControllerV2** | Endpoints REST v2 com body Renavam (POST /v2/consulta) |
| **DebitosVeicularesService** | Orquestração de consultas e pagamentos de débitos veiculares |
| **PagarDebitosService** | Orquestração de efetivação de pagamentos (conta corrente e cartão) |
| **BuscarRecibosService** | Orquestração de busca e salvamento de recibos/comprovantes fiscais |
| **ConsultaDebitosVeicularesRouter** | Rota Camel para consulta paralela de 5 tipos de débitos (multicast) |
| **PagamentoRouter/PagamentoLotesRouter** | Rotas Camel para orquestração de pagamentos individuais e em lote |
| **EfetivacaoPagamento[Tipo]Router** | Rotas específicas para efetivação de pagamentos por tipo de débito |
| **TransferenciaSpagRouter** | Rota Camel para transferências TEF/TED via SPAG |
| **DebitosVeicularesListener** | Listener GCP PubSub para processamento assíncrono de liquidações |
| **RecibosVeicularesListener** | Listener RabbitMQ para processamento de recibos |
| **PagamentoAclMapper** | MapStruct para conversão entre domínios ACL e internos |
| **TransferenciaTefMapper** | MapStruct para montagem de requests SPAG (transferências e estornos) |
| **[Tipo]RepositoryImpl** | Implementações de repositórios para integrações externas (ACL, Atom, SPAG, DXC) |

---

## 3. Tecnologias Utilizadas

- **Framework Base**: Spring Boot 2.2.0, Java 11
- **Orquestração**: Apache Camel 3.0.1 / 3.7.0
- **Segurança**: Spring Security OAuth2, JWT (jjwt), SAML (OpenSAML)
- **Mensageria**: RabbitMQ (Spring AMQP), GCP PubSub
- **Mapeamento**: MapStruct 1.4.2, Lombok
- **Web Services**: Spring WS (SOAP), JAX-WS, JAXB
- **Documentação API**: Swagger/Springfox 3.0.0, OpenAPI
- **Testes**: JUnit 5, Mockito, Pact 4.0.3 (testes de contrato)
- **Persistência**: RestTemplate (integrações REST), HikariCP (pool conexões)
- **Observabilidade**: Micrometer, Prometheus, Logback (JSON)
- **Utilitários**: iText PDF 5.5.13, Jackson (serialização JSON)
- **Feature Toggle**: ConfigCat
- **Cloud**: AWS SDK (S3, KMS - criptografia)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/consulta` | DebitosVeicularesController | Consulta débitos veiculares por Renavam (query param) |
| POST | `/v2/consulta` | DebitosVeicularesControllerV2 | Consulta débitos veiculares por Renavam (body) |
| POST | `/v1/pagamento` | DebitosVeicularesController | Efetua pagamento de débitos (conta corrente ou cartão) |
| POST | `/v1/calc-parcelas` | DebitosVeicularesController | Calcula parcelamento de débitos para cartão de crédito |
| POST | `/v1/processaExtrato` | DebitosVeicularesController | Processa e insere extrato bancário de débitos |
| POST | `/v1/transacao` (Atom) | - | Cria nova transação de débitos veiculares (integração) |
| POST | `/v1/pagamento-debito` (Atom) | - | Registra pagamento de débito (integração) |
| GET | `/v1/debito/{tipo}` (Atom) | - | Consulta débito específico por tipo (integração) |
| POST | `/v1/atualizacao-transacao` (Atom) | - | Atualiza status de transação (integração) |
| GET | `/v1/veiculo` (Atom) | - | Consulta veículo por Renavam (integração) |
| POST | `/v1/recibos` (Atom) | - | Salva recibos de pagamento (integração) |

---

## 5. Principais Regras de Negócio

1. **Validação de Veículo**: Renavam deve ser válido (11 dígitos com leftPad zeros). Códigos de ocorrência: 02=inválido, 03=inexistente, 04=sem débitos.

2. **Consolidação de Débitos**: Consulta paralela (multicast Camel) de 5 tipos de débitos (IPVA, DPVAT, Licenciamento, Multas, RENAINF) com agregação de resultados.

3. **Validação de Titularidade**: Verifica se CPF/CNPJ do pagador é titular da conta corrente via serviço de dados cadastrais.

4. **Validação de Limites**: Valida limite diário disponível para pagamentos via serviço Orch Limites.

5. **Pagamento Conta Corrente**: Transfere valores via SPAG (débito conta origem → crédito conta balde). Suporta estorno em caso de rejeição.

6. **Pagamento Cartão de Crédito**: Integra com ACL Débitos Cartão e DXC (validação CVV, RG, validade). Não realiza estorno SPAG.

7. **Processamento em Lote**: Multas e RENAINF podem ser pagos em lote (múltiplos débitos em uma transação).

8. **Quitação de Débitos**: Marca débitos como quitados (flags `veiculoValido=true`, `debitoQuitado=true`) e busca recibos pós-pagamento.

9. **Cálculo de Parcelas**: Calcula parcelamento com IOF e CET via serviço externo (apenas para cartão de crédito).

10. **Vencimento Licenciamento**: Calcula data de vencimento baseado no final da placa (enum `VencimentoLicenciamentoEnum`).

11. **Filtro de Comprovantes**: Filtra recibos por valor+ano exercício (IPVA/DPVAT/Lic) ou valor+data quitação (Multas/Renainf).

12. **Feature Toggle**: Controla validação síncrona de pagamento SPAG via flag `ft_boolean_ccbd_base_debitos_veiculares_validar_pagamento_sincrono_spag`.

13. **Tracking de Débitos**: Utiliza UUID para rastreamento entre consulta e pagamento.

14. **Status de Transação**: PAGO (código ocorrência 00), REJEITADO (códigos 01-99 exceto 00), PENDENTE (inicial).

15. **Extrato Bancário**: Valida dia útil e último dia útil antes de processar extrato.

---

## 6. Relação entre Entidades

```
DebitosVeiculares (agregador)
├── Veiculo (renavam, placa, cpfcnpj, proprietário, município)
├── DebitosIpva[] (exercício, valor, dataVencimento, codigoOcorrencia)
├── DebitosDpvat[] (exercício, valor, dataVencimento, codigoOcorrencia)
├── DebitosLicenciamento[] (exercício, valor, dataVencimento, codigoOcorrencia)
├── DebitosMultas[] (numeroAuto, valor, dataInfracao, dataVencimento)
└── DebitosRenainf[] (numeroAuto, valor, dataInfracao, dataVencimento)

PagamentoOperacao (orquestrador)
├── DadosConta (agencia, conta, banco, cpfcnpj)
├── FormaPagamento (SALDO_CONTA | CARTAO_CREDITO)
├── DadosCartao (numero, cvv, validade, rg, cpf)
├── ListaConsultaDebitos[] (tipoDebito, idTransacao, uuid, exercicio, valor)
└── Pagamento (valor, qtParcelas, debitos[])

DebitoPagamento
├── cdDebito (identificador único débito)
├── idTransacao (ID transação Atom)
├── tipoDebito (IPVA | DPVAT | LICENCIAMENTO | MULTA | RENAINF)
├── exercicio (ano)
└── valor (BigDecimal)

TransacaoDebito (Atom)
├── cdTransacaoPagamento (ID pagamento)
├── status (PAGO | REJEITADO | PENDENTE)
├── nsu (número sequencial único)
└── dataPagamento (timestamp)
```

**Relacionamentos:**
- 1 Veículo possui N Débitos (por tipo)
- 1 PagamentoOperacao processa N DebitoPagamento
- 1 TransacaoDebito vincula-se a 1 DebitoPagamento
- 1 Pagamento pode ter N Parcelas (cartão crédito)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TB_TRANSACAO_DEBITO_VEICULAR | Tabela | SELECT | Consulta transações de débitos veiculares por Renavam/ID |
| TB_IPVA | Tabela | SELECT | Consulta débitos de IPVA por veículo |
| TB_DPVAT | Tabela | SELECT | Consulta débitos de DPVAT por veículo |
| TB_MULTAS | Tabela | SELECT | Consulta multas de trânsito por veículo |
| TB_LICENCIAMENTO | Tabela | SELECT | Consulta débitos de licenciamento por veículo |
| TB_RENAINF | Tabela | SELECT | Consulta débitos RENAINF por veículo |
| TB_VEICULO | Tabela | SELECT | Consulta dados cadastrais de veículo por Renavam |
| TB_CONTA_CORRENTE | Tabela | SELECT | Validação de titularidade de conta corrente |
| TB_CLIENTE_DADOS_CADASTRAIS | Tabela | SELECT | Consulta contas por CPF/CNPJ do cliente |
| TB_RECIBOS_VEICULARES | Tabela | SELECT | Consulta recibos/comprovantes fiscais de pagamentos |
| TB_EXTRATO_BANCARIO | Tabela | SELECT | Consulta extrato consolidado de débitos veiculares |
| TB_DIAS_UTEIS | Tabela | SELECT | Validação de dias úteis bancários |
| TB_LIMITES_DIARIOS | Tabela | SELECT | Consulta limites diários de pagamento por conta |
| TB_CARTOES_CLIENTE | Tabela | SELECT | Consulta cartões ativos do cliente (via DXC SOAP) |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TB_TRANSACAO_DEBITO_VEICULAR | Tabela | INSERT/UPDATE | Cria e atualiza status de transações (PAGO/REJEITADO/PENDENTE) |
| TB_PAGAMENTO_DEBITO | Tabela | INSERT | Registra pagamentos efetuados (cdTransacaoPagamento, nsu, data) |
| TB_ERRO_PAGAMENTO | Tabela | INSERT | Insere erros de pagamento Banco Rendimento (código ocorrência) |
| TB_RECIBOS_VEICULARES | Tabela | INSERT | Salva recibos/comprovantes fiscais de pagamentos |
| TB_EXTRATO_BANCARIO | Tabela | INSERT | Insere registros de extrato consolidado diário |
| TB_TRANSFERENCIA_SPAG | Tabela | INSERT | Registra transferências TEF/TED realizadas via SPAG |
| TB_ESTORNO_SPAG | Tabela | INSERT | Registra estornos de transferências SPAG |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| HPEdsWS.xml | Leitura | SOAPConfiguration | WSDL para integração SOAP com DXC EDS (consulta dados veículo) |
| NEIBCardService.xml | Leitura | SOAPConfiguration | WSDL para integração SOAP com DXC NEIBCard (consulta cartões) |
| swagger-acl-*.yaml | Leitura | AppConfiguration | Contratos OpenAPI para geração de clientes REST (ACL débitos) |
| swagger-atom-*.yaml | Leitura | AppConfiguration | Contratos OpenAPI para geração de clientes REST (Atom) |
| swagger-spag-*.yaml | Leitura | AppConfiguration | Contratos OpenAPI para geração de clientes REST (SPAG) |
| comprovante-fiscal.pdf | Leitura | PDFUtil | Extração de ano exercício de comprovantes fiscais (base64) |
| application.yml | Leitura | Spring Boot | Configurações de ambiente (URLs, credenciais, filas) |
| logback-spring.xml | Leitura | Logback | Configuração de logs estruturados (JSON) |

---

## 10. Filas Lidas

| Nome da Fila | Tipo | Classe Responsável | Descrição |
|--------------|------|-------------------|-----------|
| business-ccbd-base-liquidacao-debitos-veiculares-sub | GCP PubSub Subscription | DebitosVeicularesListener | Consome mensagens de liquidação de débitos veiculares (atributo `operacao=liquidacaoDebitosVeiculares`) |
| ccbd_debitos_veiculares_comprovantes | RabbitMQ Queue | RecibosVeicularesListener | Consome mensagens para busca e salvamento de recibos/comprovantes fiscais |

---

## 11. Filas Geradas

| Nome da Fila | Tipo | Classe Responsável | Descrição |
|--------------|------|-------------------|-----------|
| business-ccbd-base-liquidacao-debitos-veiculares | GCP PubSub Topic | PagamentoFilaRepositoryImpl | Publica eventos de sucesso/falha de pagamentos de débitos veiculares |
| notificacaoPagamentos | RabbitMQ Exchange | NotificacaoPagamentoRepositoryImpl | Publica notificações de pagamentos (routing key: `pagamento.debitos.veiculares`) |

---

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| **ACL Banco Rendimento** | REST | Consulta e pagamento de débitos IPVA, DPVAT, Licenciamento, Multas, RENAINF (APIs específicas por tipo) |
| **ACL Débitos Cartão** | REST | Processamento de pagamentos com cartão de crédito |
| **ACL Cálculo Parcelas** | REST | Cálculo de parcelamento com IOF e CET |
| **ACL Consulta Extrato** | REST | Consulta extrato bancário consolidado de débitos veiculares |
| **Atom Débitos Veiculares** | REST | CRUD de transações, pagamentos, recibos, veículos e extratos |
| **Atom Cliente Dados Cadastrais** | REST | Consulta contas por CPF/CNPJ para validação de titularidade |
| **Atom Dias Úteis** | REST | Validação de dias úteis bancários |
| **SPAG Transferências** | REST | Efetivação de transferências TEF/TED e estornos entre contas |
| **Orch Limites** | REST | Validação de limites diários de pagamento |
| **Orch Consulta CC Cliente** | REST | Validação de conta corrente do cliente |
| **DXC HPE EDS** | SOAP | Consulta dados de veículo e operações com cartão |
| **DXC NEIBCardService** | SOAP | Consulta cartões ativos e dados do cliente |
| **Gateway API BV** | OAuth2 | Autenticação e autorização via JWT |
| **GCP PubSub** | Mensageria | Publicação/consumo de eventos de liquidação |
| **RabbitMQ** | Mensageria | Publicação/consumo de notificações e recibos |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada com separação clara de camadas (domain, application, infrastructure)
- Uso adequado de padrões de projeto (Repository, Mapper, Strategy)
- MapStruct reduz significativamente boilerplate de conversão de DTOs
- Exception handling centralizado via `@ControllerAdvice`
- Configurações externalizadas via `@ConfigurationProperties`
- Feature Toggles permitem controle de comportamento em runtime
- Segurança OAuth2 implementada corretamente
- Testes unitários abrangentes (JUnit 5 + Mockito)
- Logs estruturados em JSON para observabilidade
- Uso de Apache Camel para orquestração complexa de fluxos

**Pontos de Melhoria:**
- Alta complexidade em routers Camel (alguns com mais de 200 linhas), dificultando manutenção
- Acoplamento elevado entre routers e processors Camel
- Falta de documentação técnica inline (JavaDoc) em classes críticas
- Alguns métodos com muitos parâmetros (code smell)
- Necessidade de testes de integração end-to-end mais robustos
- Versionamento de APIs REST poderia ser mais consistente (v1 vs v2)
- Tratamento de exceções em alguns fluxos Camel poderia ser mais granular

---

## 14. Observações Relevantes

1. **Arquitetura Multi-Módulo**: Projeto Maven dividido em `application`, `domain` e `common` para melhor organização e reuso de código.

2. **Orquestração Camel**: Apache Camel é utilizado extensivamente para orquestração de fluxos complexos (consultas paralelas, pagamentos em lote, estornos), com mais de 15 routers identificados.

3. **Processamento Assíncrono**: Utiliza GCP PubSub para processamento assíncrono de liquidações, permitindo escalabilidade horizontal.

4. **Integração Legado**: Convivência de integrações REST modernas com SOAP legado (DXC), demonstrando transição tecnológica.

5. **Múltiplos Tipos de Débito**: Suporta 5 tipos distintos de débitos veiculares (IPVA, DPVAT, Licenciamento, Multas, RENAINF), cada um com fluxos específicos.

6. **Dois Modos de Pagamento**: Suporta pagamento via saldo em conta corrente (com transferência SPAG) e cartão de crédito (sem transferência SPAG).

7. **Estorno Automático**: Implementa estorno automático de transferências SPAG em caso de rejeição de pagamento (apenas para saldo em conta).

8. **Validações Robustas**: Múltiplas validações (titularidade, limites, conta corrente, dias úteis, dados cartão) antes de efetuar pagamento.

9. **Tracking de Transações**: Utiliza UUID para rastreamento de débitos entre consulta e pagamento, garantindo idempotência.

10. **Filtro Inteligente de Recibos**: Implementa lógica de filtro de comprovantes fiscais por valor+ano exercício ou valor+data quitação, dependendo do tipo de débito.

11. **Métricas e Observabilidade**: Exposição de métricas via Prometheus (`/actuator/prometheus`) para monitoramento em Grafana.

12. **Ambientes Segregados**: Configurações específicas por ambiente (dev, hml, prd) via profiles Spring Boot.

13. **Segurança de Dados**: Criptografia de dados sensíveis (cartão) via ZPK e integração com AWS KMS.

14. **Versionamento de Contratos**: Utiliza Swagger/OpenAPI para versionamento e documentação de contratos de API.

15. **Processamento em Lote**: Suporta pagamento de múltiplas multas e RENAINF em uma única transação, otimizando custos de transferência SPAG.