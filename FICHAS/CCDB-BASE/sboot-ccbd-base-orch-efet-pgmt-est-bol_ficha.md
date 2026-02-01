# Ficha Técnica do Sistema

## 1. Descrição Geral
Sistema responsável por processar estornos de pagamentos de boletos (tributos e consumo) realizados via CCBD (Conta Corrente Banco Digital). O sistema consome mensagens de uma fila IBM MQ, efetua transferências de estorno entre contas através de serviços legados (ESB Adapter) e atualiza o status do pagamento em uma API REST de pagamento de boletos.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot que inicializa a aplicação |
| `ProcessarEstornoPgmtBoletoListener` | Listener JMS que consome mensagens da fila de estorno |
| `EfetPgmtEstBolService` | Serviço de domínio que orquestra o processo de estorno |
| `EfetPgmtEstBolRouter` | Roteador Apache Camel que define o fluxo de processamento |
| `EstornoOutboundImpl` | Implementação que efetua a transferência de estorno via ESB Adapter |
| `AtualizarPgmtEstornoOutboundImpl` | Implementação que atualiza o status do estorno na API de boletos |
| `Boleto` | Entidade de domínio representando os dados do boleto a ser estornado |
| `ObjetoEstornoBalde` | DTO para requisição de transferência de estorno |
| `CodigoTipoTransacao` | Enum que mapeia códigos de liquidação para códigos de transação |
| `TipoConta` | Enum que mapeia tipos de conta (CC, CP, CT, PG) |

---

## 3. Tecnologias Utilizadas
- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Apache Camel 3.0.1** (orquestração de fluxos)
- **IBM MQ 2.0.9** (mensageria)
- **Spring JMS** (integração com filas)
- **RestTemplate** (cliente HTTP)
- **Lombok** (redução de boilerplate)
- **Swagger/OpenAPI 3.0** (documentação de APIs)
- **Spring Actuator** (monitoramento e health checks)
- **Micrometer/Prometheus** (métricas)
- **Logback** (logging)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **OpenShift/Kubernetes** (orquestração de containers)

---

## 4. Principais Endpoints REST
Não se aplica. Este é um sistema orientado a eventos (event-driven) que consome mensagens de filas. Não expõe endpoints REST para processamento de negócio, apenas endpoints de monitoramento via Actuator.

---

## 5. Principais Regras de Negócio
1. **Validação de Elegibilidade para Estorno**: Apenas boletos com `codigoFormaPagamento = 1` (CCBD) e `codigoStatus = 5` são elegíveis para estorno
2. **Inversão de Papéis na Transferência**: No estorno, o remetente original torna-se favorecido e o favorecido original torna-se remetente
3. **Conversão de Código de Banco**: Código de banco 655 é convertido para 161 nas transferências
4. **Mapeamento de Códigos de Transação**: Códigos de liquidação são mapeados para códigos de transação específicos:
   - Liquidação 59 → Transação 8680 (Estorno Tributo)
   - Liquidação 60 → Transação 8678 (Estorno Consumo)
5. **Atualização de Status**: Após estorno bem-sucedido, o status é atualizado para 6 (estorno realizado com sucesso)
6. **Data de Efetivação**: Utiliza sempre a data atual do sistema para efetivação do estorno
7. **Produto e Sistema Fixos**: Utiliza código de produto 171 e código de sistema 1 para todas as transferências

---

## 6. Relação entre Entidades

**Boleto** (entidade principal)
- Contém: `ContaCorrente remetente` (1:1)
- Contém: `ContaCorrente favorecido` (1:1)
- Atributos: idBoleto, valorPagamento, codigoStatus, protocoloDevolucao, etc.

**ContaCorrente**
- Atributos: codigoBanco, numeroConta, codigoTipoConta, agencia, nomeBeneficiario, numeroCpfCnpj

**ObjetoEstornoBalde** (DTO para transferência)
- Contém: `Beneficiario contaCorrenteFavorecidoPK` (1:1)
- Contém: `Beneficiario contaCorrenteRemetentePK` (1:1)
- Atributos: valores, datas, códigos de transação

**Beneficiario**
- Atributos: cdBanco, nuContaCorrente, tpContaCorrente

**ObjetoAtualizaEstorno** (DTO para atualização)
- Atributos: codigoLancamento, numeroProtocoloDevolucao, codigoStatus

---

## 7. Estruturas de Banco de Dados Lidas
Não se aplica. O sistema não acessa diretamente estruturas de banco de dados. Consome dados via fila JMS e APIs REST.

---

## 8. Estruturas de Banco de Dados Atualizadas
Não se aplica. O sistema não atualiza diretamente estruturas de banco de dados. Realiza atualizações via APIs REST de outros serviços.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `application.yml` | Leitura | Spring Boot | Arquivo de configuração da aplicação com propriedades de ambiente |
| `logback-spring.xml` | Leitura | Logback | Configuração de logging da aplicação |
| Logs da aplicação | Gravação | Logback (console) | Logs de execução, erros e informações de processamento |

---

## 10. Filas Lidas

**Fila de Entrada:**
- **Nome**: `QL.CCBD.PROC_PAGMT_CONTAS.INT`
- **Tipo**: IBM MQ
- **Queue Manager**: `QM.DIG.01`
- **Classe Consumidora**: `ProcessarEstornoPgmtBoletoListener`
- **Descrição**: Fila que recebe mensagens com dados de boletos que necessitam estorno
- **Formato da Mensagem**: Objeto `Boleto` serializado em JSON

---

## 11. Filas Geradas
Não se aplica. O sistema não publica mensagens em filas, apenas consome.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **ESB Adapter (JBoss Legacy)** | API REST | Serviço legado que executa transferências entre contas através do método `CCPagamento.Transferencia.efetuarTransferenciaEntreContasBancoValidarSaldo` |
| **sboot-ccbd-base-atom-pgto-trib-bol** | API REST | Serviço de pagamento de boletos que atualiza o status do estorno via endpoint PUT `/v1/pagamento-boleto/efetivar/{protocolo}/estorno` |
| **IBM MQ** | Mensageria | Sistema de filas para consumo de mensagens de estorno |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com módulos `domain` e `application`
- Uso adequado de padrões como Ports & Adapters (Hexagonal Architecture)
- Utilização de Apache Camel para orquestração de fluxos
- Configuração externalizada e separada por ambiente
- Uso de Lombok para redução de boilerplate
- Implementação de health checks e métricas
- Logging estruturado e adequado

**Pontos de Melhoria:**
- Tratamento de exceções muito genérico no listener (captura `Exception` sem tratamento específico)
- Falta de validações de entrada mais robustas
- Ausência de testes unitários e de integração nos arquivos enviados
- Valores "mágicos" hardcoded (ex: `codStatusEstorno = 5`, `formaPagamento = 1`, `cdProduto = 171`)
- Comentários em português misturados com código em inglês
- Falta de documentação JavaDoc nas classes principais
- Método `tipoBanco()` com lógica de conversão específica sem documentação clara do motivo
- Ausência de retry e circuit breaker para chamadas externas
- Falta de validação de resposta das APIs externas

---

## 14. Observações Relevantes

1. **Arquitetura Event-Driven**: Sistema totalmente orientado a eventos, sem exposição de APIs REST próprias
2. **Dependência de Sistemas Legados**: Forte dependência do ESB Adapter (JBoss) para efetivação de transferências
3. **Ambientes Múltiplos**: Configuração preparada para 4 ambientes (local, des, qa, uat, prd)
4. **Autenticação Basic**: Utiliza autenticação básica para chamadas ao ESB Adapter
5. **Segurança**: Implementa módulos de segurança JWT e trilha de auditoria do BV
6. **Containerização**: Preparado para execução em containers Docker/OpenShift
7. **Monitoramento**: Expõe métricas Prometheus na porta 9090
8. **Processamento Síncrono**: Apesar de consumir de fila, o processamento é síncrono (não há paralelização explícita)
9. **Conversão de Dados**: Realiza conversões específicas de códigos de banco e tipos de conta
10. **Status de Estorno**: Utiliza código de status 6 para indicar estorno realizado com sucesso