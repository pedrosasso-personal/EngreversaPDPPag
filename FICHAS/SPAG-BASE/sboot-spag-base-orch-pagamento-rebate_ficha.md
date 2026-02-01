# Ficha Técnica do Sistema

---

## 1. Descrição Geral

O sistema **sboot-spag-base-orch-pagamento-rebate** é um orquestrador responsável pelos fluxos de cálculo, relatório e pagamento de rebate (cashback/bonificação) para clientes do Banco Votorantim. Trata-se de uma aplicação Spring Boot que utiliza Apache Camel para roteamento e processamento de mensagens, integrando-se com diversos serviços atômicos e filas IBM MQ. O sistema realiza apurações mensais de transações, calcula valores de rebate conforme parametrizações e faixas cadastradas, efetiva pagamentos via transferência bancária (TEF) e envia relatórios e extratos de transações para sistemas consumidores e clientes via e-mail.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal que inicializa a aplicação Spring Boot com suporte a OAuth2 Resource Server. |
| **PagamentoRebateController** | Controller REST que expõe endpoints para realizar pagamentos e listar pagamentos para aprovação. |
| **EmailController** | Controller REST para envio de e-mails de resumo de pagamento. |
| **PagamentoRebateService** | Serviço de domínio que orquestra os fluxos de cálculo, relatório, extrato e efetivação de pagamentos via rotas Camel. |
| **ApuracaoService** | Serviço responsável por aplicar regras de negócio e calcular valores de rebate (bruto, líquido, impostos, data de pagamento). |
| **DiasUteisService** | Serviço que calcula datas úteis e prazos de pagamento considerando dias não úteis. |
| **MontarEmailService** | Serviço que monta o conteúdo HTML do e-mail de resumo de pagamento a partir de template. |
| **EmailService** | Serviço que dispara o fluxo Camel de envio de e-mails. |
| **ApuracaoPagamentoRouter** | Rota Camel que orquestra o fluxo de apuração e cálculo de pagamentos de rebate. |
| **RelatorioRebateRouter** | Rota Camel que gera relatórios de pagamentos de rebate em lotes e envia para fila. |
| **ExtratoTransacoesRouter** | Rota Camel que gera extratos de transações paginados e envia para fila. |
| **PagamentoRebateRouter** | Rota Camel que efetiva pagamentos de rebate via transferência bancária (TEF). |
| **ListarPagamentosAprovacaoRouter** | Rota Camel que lista pagamentos para aprovação com enriquecimento de dados de serviço. |
| **MontarEmailRouter** | Rota Camel que monta e envia e-mails de resumo de pagamento para clientes. |
| **ApuracaoListener** | Listener JMS que consome mensagens de início de cálculo de rebate. |
| **ExtratoTransacoesListener** | Listener JMS que consome mensagens de processamento de extrato de transações. |
| **RelatorioListener** | Listener JMS que consome mensagens de início de geração de relatório. |
| **PagamentoRebateRepositoryImpl** | Implementação de repositório que integra com o serviço atômico de pagamento de rebate. |
| **RegrasRebateRepositoryImpl** | Implementação de repositório que integra com o serviço atômico de regras de rebate. |
| **RebateTransacaoRepositoryImpl** | Implementação de repositório que integra com o serviço atômico de transações de rebate. |
| **TransferenciaRepositoryImpl** | Implementação de repositório que integra com o orquestrador de transferências bancárias. |
| **DiasUteisRepositoryImpl** | Implementação de repositório que integra com o serviço atômico de dias úteis. |
| **EmailRepositoryImpl** | Implementação de repositório que integra com a API corporativa de envio de e-mail (CAAPI). |
| **ApuracaoRepositoryImpl** | Implementação de repositório que publica mensagens de retorno de apuração em fila. |
| **ExtratoTransacoesRepositoryImpl** | Implementação de repositório que publica mensagens de extrato de transações em fila. |
| **RetornoRelatorioRepositoryImpl** | Implementação de repositório que publica mensagens de relatório em fila. |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Apache Camel 3.0.1** (roteamento e processamento de mensagens)
- **IBM MQ** (mensageria via JMS)
- **Spring Security OAuth2** (autenticação e autorização via JWT)
- **Swagger/Springfox 2.9.2** (documentação de APIs)
- **Lombok** (redução de boilerplate)
- **Jackson** (serialização/deserialização JSON)
- **RestTemplate** (cliente HTTP)
- **Spring Actuator + Micrometer + Prometheus** (métricas e monitoramento)
- **JUnit 5 + Mockito** (testes unitários)
- **Rest Assured** (testes funcionais)
- **Pact** (testes de contrato)
- **Logback** (logging)
- **Maven** (gerenciamento de dependências e build)
- **Docker** (containerização)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/pagamentos` | PagamentoRebateController | Realiza o pagamento de rebate (efetivação via TEF). |
| GET | `/pagamentos` | PagamentoRebateController | Busca pagamentos de rebate para aprovação com filtros (cpfCnpj, idServico, status, periodicidade, paginação). |
| POST | `/emails` | EmailController | Envia e-mails de resumo de pagamento de rebate para clientes. |

---

## 5. Principais Regras de Negócio

1. **Apuração Mensal de Rebate**: O sistema realiza apuração mensal de transações de clientes conforme parametrizações cadastradas (periodicidade, tipo de apuração, forma de rebate, faixas de valores/quantidades).

2. **Cálculo de Rebate por Faixas**: O valor ou quantidade apurado é comparado com faixas de regras cadastradas. A faixa aplicável define o percentual ou valor fixo de rebate a ser pago.

3. **Cálculo de Impostos**: O sistema calcula impostos (IR e ISS) sobre o valor bruto de rebate conforme percentuais parametrizados, gerando o valor líquido a ser pago.

4. **Cálculo de Data de Pagamento**: A data de pagamento é calculada considerando prazo parametrizado (dias corridos ou úteis) e dias não úteis (feriados).

5. **Aprovação de Pagamentos**: Pagamentos podem necessitar de aprovação manual conforme parametrização do cliente. Status: PENDENTE_APROVACAO, PENDENTE, PAGO, RECUSADO, CANCELADO.

6. **Efetivação de Pagamento via TEF**: Pagamentos pendentes com data de pagamento igual ao dia atual são efetivados via transferência bancária (integração com orquestrador de transferências).

7. **Geração de Extrato de Transações**: O sistema gera extratos paginados de transações de rebate por cliente e serviço, enviando para fila consumidora.

8. **Geração de Relatório de Pagamentos**: O sistema gera relatórios paginados de pagamentos de rebate do mês anterior, enviando para fila consumidora.

9. **Envio de E-mail de Resumo**: Após pagamento efetuado, o sistema envia e-mail para o cliente com memória de cálculo (faixas utilizadas, valores, impostos, data de pagamento).

10. **Controle de Processamento**: O sistema controla o status de processamento de extrato (EM_ANDAMENTO, FINALIZADO, ERROR) e envia confirmações para filas.

11. **Retroatividade**: Parametrizações podem ser retroativas, considerando transações desde a data de inclusão da parametrização.

12. **Tipo de Entrada**: Rebate pode ser pago via Rede ou Corban, com contas de crédito distintas.

13. **Apuração Bancária**: Transações podem ser apuradas por banco (Mesmo Banco, Outros Bancos, Ambos).

---

## 6. Relação entre Entidades

**Entidades principais:**

- **PagamentoRebate**: Representa um pagamento de rebate calculado e persistido. Contém valores brutos, líquidos, impostos, datas de apuração e pagamento, status, dados de conta de crédito, etc.

- **ParametrizacaoClienteResponse**: Representa a parametrização de rebate de um cliente (periodicidade, forma de rebate, percentuais de imposto, faixas de regras, contas de crédito, etc).

- **FaixaResponse**: Representa uma faixa de regra de rebate (valor inicial, valor final, percentual ou valor fixo de rebate).

- **ConsolidadoResponse**: Representa o consolidado de transações de um cliente em um período (quantidade total, valor total).

- **ExtratoTransacaoResponse**: Representa uma transação individual de rebate (data, valor, complemento, banco).

- **TransferenciaPagamentoRebate**: Representa uma transferência bancária (TEF) para efetivação de pagamento de rebate.

- **PessoaTransferencia**: Representa remetente ou favorecido de uma transferência (nome, CPF/CNPJ, tipo de pessoa, banco, agência, conta, tipo de conta).

- **ProtocoloPagamento**: Representa o protocolo de retorno de uma transferência bancária (número de protocolo, status).

**Relacionamentos:**

- PagamentoRebate **possui** ParametrizacaoClienteResponse (via codigoParametroCliente).
- ParametrizacaoClienteResponse **possui** lista de FaixaResponse (faixas de regras).
- PagamentoRebate **referencia** FaixaResponse utilizada (via idFaixaParametrizacao).
- ConsolidadoResponse **é gerado a partir de** transações de rebate de um cliente.
- ExtratoTransacaoResponse **compõe** o extrato de transações de um PagamentoRebate.
- TransferenciaPagamentoRebate **é criada a partir de** PagamentoRebate para efetivação.
- TransferenciaPagamentoRebate **possui** PessoaTransferencia (remetente e favorecido).
- ProtocoloPagamento **é retornado após** efetivação de TransferenciaPagamentoRebate.

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| não se aplica | - | - | O sistema não lê diretamente de banco de dados. Todas as leituras são feitas via APIs REST de serviços atômicos. |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbRetornoCalculo | tabela | INSERT | Tabela H2 em memória para testes (schema.sql). Armazena retorno de cálculo (id, cnpj, valorTotal, imposto). Não é utilizada em produção. |

**Observação:** O sistema não atualiza diretamente estruturas de banco de dados em produção. Todas as escritas são feitas via APIs REST de serviços atômicos (atom-pagamento-rebate, atom-regras-rebate, atom-rebate-transacao).

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| email/template.html | leitura | MontarEmailService | Template HTML para montagem do e-mail de resumo de pagamento de rebate. |
| application.yml | leitura | Spring Boot | Arquivo de configuração da aplicação (URLs de serviços, filas, credenciais, etc). |
| logback-spring.xml | leitura | Logback | Arquivo de configuração de logs da aplicação. |
| schema.sql | leitura | Spring Boot | Script SQL para criação de tabela H2 em memória (apenas para testes). |

---

## 10. Filas Lidas

| Nome da Fila | Tecnologia | Classe Responsável | Descrição |
|--------------|------------|-------------------|-----------|
| QL.INICIAR_CALCULO_REBATE.INT | IBM MQ (JMS) | ApuracaoListener | Fila de entrada para iniciar o cálculo de rebate mensal. |
| QL.ENVIO_RELATORIO_REBATE.INT | IBM MQ (JMS) | RelatorioListener | Fila de entrada para iniciar a geração de relatório de pagamentos. |
| QL.ENVIO_RELATORIO_PARCEIRO_REBATE.INT | IBM MQ (JMS) | ExtratoTransacoesListener | Fila de entrada para iniciar/finalizar processamento de extrato de transações. |

---

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Responsável | Descrição |
|--------------|------------|-------------------|-----------|
| QL.RETORNO_CALCULO_REBATE.INT | IBM MQ (JMS) | ApuracaoRepositoryImpl | Fila de saída para retorno de sucesso/falha do cálculo de rebate. |
| QL.RETORNO_RELATORIO_REBATE.INT | IBM MQ (JMS) | RetornoRelatorioRepositoryImpl | Fila de saída para envio de dados de relatório de pagamentos (em lotes). |
| QL.RETORNO_RELATORIO_PARCEIRO_REBATE.INT | IBM MQ (JMS) | ExtratoTransacoesRepositoryImpl | Fila de saída para envio de extrato de transações (paginado) e confirmação de processamento. |

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **atom-pagamento-rebate** | API REST | Serviço atômico de persistência de pagamentos de rebate. Operações: salvar, buscar, atualizar status, atualizar protocolo, listar para aprovação, relatório, extrato. |
| **atom-regras-rebate** | API REST | Serviço atômico de parametrizações e regras de rebate. Operações: buscar parametrizações de cliente, buscar serviços, buscar faixas de regras, buscar histórico de faixas. |
| **atom-rebate-transacao** | API REST | Serviço atômico de transações de rebate. Operações: buscar consolidados de transações, buscar transações paginadas para extrato. |
| **orch-transferencias** | API REST | Orquestrador de transferências bancárias (TEF). Operação: realizar transferência para efetivação de pagamento. |
| **atom-dias-uteis** | API REST | Serviço atômico de calendário de dias úteis. Operações: buscar dias não úteis entre datas, buscar próximo dia útil. |
| **CAAPI - Envio de E-mail** | API REST (OAuth2) | API corporativa de envio de e-mail. Operação: enviar e-mail com template HTML. |
| **IBM MQ** | Mensageria (JMS) | Sistema de filas para comunicação assíncrona entre componentes. |
| **API Gateway BV** | OAuth2 | Gateway de autenticação e autorização via OAuth2 (two-legged). |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada em camadas (application, domain, common) seguindo princípios de Clean Architecture.
- Uso adequado de padrões de projeto (Repository, Service, Mapper, Builder).
- Separação clara de responsabilidades entre classes.
- Uso de Lombok para redução de boilerplate.
- Testes unitários presentes para a maioria das classes críticas.
- Uso de Apache Camel para orquestração de fluxos complexos de forma declarativa.
- Configuração externalizada via application.yml e variáveis de ambiente.
- Tratamento de exceções centralizado (RestResponseEntityExceptionHandler).
- Uso de DTOs para comunicação entre camadas.
- Documentação via Swagger/OpenAPI.

**Pontos de Melhoria:**
- Falta de documentação JavaDoc em muitas classes e métodos.
- Alguns métodos longos e complexos (ex: MontarEmailService.montarEmail, ApuracaoService.calcularPagamento).
- Uso de strings mágicas em alguns pontos (ex: nomes de propriedades, headers).
- Falta de validação de entrada em alguns endpoints REST.
- Testes de integração e funcionais praticamente vazios.
- Falta de tratamento de erros mais granular em alguns fluxos Camel.
- Uso de `@Qualifier` em vários pontos pode indicar configuração de beans não ideal.
- Alguns processadores Camel poderiam ser simplificados ou divididos em métodos menores.
- Falta de logs estruturados em alguns pontos críticos.

---

## 14. Observações Relevantes

1. **Arquitetura Multi-Módulo**: O projeto está organizado em 3 módulos Maven (application, domain, common), facilitando a separação de responsabilidades e reutilização de código.

2. **Profiles Spring**: A aplicação suporta múltiplos ambientes (local, des, qa, uat, prd) via profiles Spring, com configurações específicas por ambiente.

3. **Segurança**: A aplicação utiliza OAuth2 Resource Server para autenticação/autorização via JWT. Integração com API Gateway BV para obtenção de tokens.

4. **Auditoria**: Integração com biblioteca de trilha de auditoria do BV (springboot-arqt-base-trilha-auditoria-web e jms).

5. **Monitoramento**: Exposição de métricas via Actuator e Prometheus. Configuração de Grafana para visualização de métricas customizadas.

6. **Processamento Assíncrono**: Uso intensivo de filas IBM MQ para comunicação assíncrona e desacoplamento entre componentes.

7. **Paginação**: Implementação de paginação para processamento de grandes volumes de dados (relatórios, extratos, listagens).

8. **Agrupamento em Lotes**: Uso de estratégia de agregação do Camel para envio de dados em lotes para filas (BatchSize, ArrayListAggregationStrategy).

9. **Tratamento de Erros**: Tratamento de exceções em rotas Camel com envio de mensagens de erro para filas e logs estruturados.

10. **Testes Automatizados**: Estrutura de testes organizada em unit, integration e functional, embora os testes de integração e funcionais estejam incompletos.

11. **CI/CD**: Configuração de pipeline Jenkins (jenkins.properties) e infraestrutura como código (infra.yml) para deploy em OpenShift.

12. **Containerização**: Dockerfile para geração de imagem Docker da aplicação.

13. **Dependências Internas**: O sistema depende de vários serviços atômicos e orquestradores do ecossistema SPAG (Sistema de Pagamentos) do Banco Votorantim.

14. **Regra de Cálculo Mensal**: Existe uma flag `bv.respeitar-regra` que, quando ativada em produção, garante que o cálculo de rebate só seja executado no primeiro dia do mês.

15. **Retroatividade**: O sistema suporta cálculo retroativo de rebate, considerando transações desde a data de inclusão da parametrização do cliente.

16. **Tipos de Apuração**: O sistema suporta apuração por quantidade de transações ou por valor de transações.

17. **Formas de Rebate**: O sistema suporta rebate por percentual sobre valor base ou valor fixo.

18. **Tipos de Entrada**: Rebate pode ser pago via Rede (estabelecimento) ou Corban (correspondente bancário), com contas de crédito distintas.

---