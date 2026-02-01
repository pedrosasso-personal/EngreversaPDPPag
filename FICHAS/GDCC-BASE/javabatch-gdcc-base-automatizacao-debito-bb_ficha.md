# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java desenvolvido para automação de débito em conta corrente do Banco do Brasil (BB) no contexto de gestão de débito em conta corrente (GDCC). O sistema processa propostas de crédito que possuem débito em conta como forma de pagamento, consultando e registrando autorizações de débito conforme o modelo parametrizado para cada banco. Executa em lotes (batch) utilizando o framework BV-Sistemas, lendo propostas aprovadas, verificando elegibilidade para débito automático e gerenciando o ciclo de vida das autorizações de débito.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê registros de propostas elegíveis para débito em conta do banco de dados (propostas aprovadas dos últimos 2 dias) |
| **ItemProcessor** | Processa cada proposta, verifica se é Banco do Brasil, consulta status de autorização e solicita débito quando necessário |
| **ItemWriter** | Grava registros de controle de débito processados na tabela TbControleDebitoProposta |
| **AutorizacaoDebitoBusiness** | Orquestra a lógica de negócio de autorização de débito: consulta, validação de modelo e inserção de registros |
| **RegraAutorizacaoDebitoBusiness** | Implementa regras específicas de autorização por modelo (sem autorização, única vez, por proposta) |
| **RegistroDebitoPropostaDAO** | Acesso a dados para operações relacionadas a registros de débito e autorização |
| **ControleDebitoPropostaDAO** | Insere registros de controle de débito processados |
| **SequencialDAO** | Obtém sequenciais de tabelas via stored procedure |
| **Queries** | Carrega e gerencia queries XML para execução no banco de dados |

---

## 3. Tecnologias Utilizadas

- **Java** (versão não especificada explicitamente, provavelmente Java 6-8 pela estrutura)
- **Maven** (gerenciamento de dependências e build)
- **Spring Framework** (configuração e injeção de dependências)
- **BV-Framework Batch** (framework proprietário para processamento batch)
- **JAXB** (marshalling/unmarshalling XML)
- **Log4j** (logging)
- **Bitronix** (gerenciamento de transações JTA)
- **JTDS Driver** (conexão com SQL Server/Sybase)
- **JUnit** (testes unitários)
- **IBM MQ Series** (mensageria - código comentado)
- **SQL Server/Sybase** (banco de dados)

---

## 4. Principais Endpoints REST

não se aplica

---

## 5. Principais Regras de Negócio

1. **Elegibilidade de Propostas**: Processa apenas propostas do produto 10 (crédito), com tipo de cobrança 7 (débito em conta), em status 'A' (aprovada) ou 'PA' (parcialmente aprovada), alteradas nos últimos 2 dias.

2. **Modelos de Autorização de Débito**:
   - **Sem Autorização (1)**: Débito autorizado automaticamente sem necessidade de confirmação do cliente
   - **Única Vez (2)**: Autorização válida por período parametrizado (dias de expiração), requer nova autorização após expiração
   - **Por Proposta (3)**: Cada proposta requer autorização específica do cliente

3. **Processamento Específico Banco do Brasil**: Sistema processa apenas contas do Banco do Brasil (código 001).

4. **Controle de Status de Processamento**:
   - Status 1 (PROCESSAR): Registro pendente de processamento
   - Status 2 (PROCESSADO): Registro já processado

5. **Status de Autorização**:
   - Pendente Envio (1)
   - Pendente Autorização Cliente (2)
   - Pendente Dados Pagamento (3)
   - Débito Não Autorizado (4)
   - Débito Autorizado (5)

6. **Validação de Expiração**: Para modelo "Única Vez", verifica se a autorização anterior ainda está válida baseado na quantidade de dias de expiração parametrizada.

7. **Registro de Eventos**: Mantém histórico completo de eventos de autorização com log de alterações de status.

8. **Sistema de Origem**: Identifica origem da solicitação (GDCC) para rastreabilidade.

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **RegistroDebitoContaVO**: Representa uma proposta elegível para débito (nuProposta, nuCpfCnpj, nuBanco, cdAgencia, dvAgencia, nuContaCorrenteFavorecido, tpPagamento)

- **ControleDebitoContaVO**: Controle de processamento (cdControleDebitoConta, nuProposta, nuBanco, flEnvio)

- **RegistroAutorizacaoDebitoDTO**: Registro completo de autorização (cdRegistroAutorizacaoDebito, cdModeloAutorizacaoDebito, numeroCpfCnpj, contaAutorizacaoDebito, sistemaOrigem, stProcessamento)

- **EventoRegistroAutorizacaoDebitoVO**: Evento de mudança de status (statusAutDebito, dsAutorizacaoDebito, dtEvento, cpfCliente, nuConta, nuBanco)

- **ContaAutorizacaoDebitoVO**: Dados da conta (nuBanco, cdAgencia, dvAgencia, nuContaCorrente, dvContaCorrente)

- **ModeloAutorizacaoDebitoVO**: Parametrização do modelo (cdModeloAutorizacaoDebito, nuBanco, qtDiasExpiracao)

**Relacionamentos:**
- RegistroAutorizacaoDebitoDTO possui ContaAutorizacaoDebitoVO e SistemaOrigemAutorizacaoDebitoVO
- RegistroAutorizacaoDebitoDTO possui lista de EventoRegistroAutorizacaoDebitoVO
- ControleDebitoContaVO é gerado a partir de RegistroDebitoContaVO após processamento

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| DBCRED..TbProposta | tabela | SELECT | Propostas de crédito |
| DBCRED..TbPropostaFavorecido | tabela | SELECT | Dados do favorecido da proposta (conta para débito) |
| DBCOR..TbSubProduto | tabela | SELECT | Subprodutos para filtrar produto 10 (crédito) |
| DbGestaoDebitoContaCorrente..TbControleDebitoProposta | tabela | SELECT | Controle de propostas já processadas |
| DBCRED..TbPropostaFinanceiro | tabela | SELECT | Dados financeiros da proposta (tipo cobrança) |
| DbGestaoDebitoContaCorrente..TbRegistroAutorizacaoDebito | tabela | SELECT | Registros de autorização de débito |
| DbGestaoDebitoContaCorrente..TbEventoRegistroAutorizacaoDbo | tabela | SELECT | Eventos de autorização de débito |
| DbGestaoDebitoContaCorrente..TbStatusAutorizacaoDebito | tabela | SELECT | Descrições de status de autorização |
| DbGestaoDebitoContaCorrente..TbParametroAutorizacaoDebito | tabela | SELECT | Parametrização de modelos de autorização por banco |
| DbGestaoDebitoContaCorrente..TbSistemaOrigem | tabela | SELECT | Sistemas origem das solicitações |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| DbGestaoDebitoContaCorrente..TbControleDebitoProposta | tabela | INSERT | Insere controle de propostas processadas |
| DbGestaoDebitoContaCorrente..TbRegistroAutorizacaoDebito | tabela | INSERT | Insere novos registros de autorização |
| DbGestaoDebitoContaCorrente..TbRegistroAutorizacaoDebito | tabela | UPDATE | Atualiza modelo de autorização e status de processamento |
| DbGestaoDebitoContaCorrente..TbEventoRegistroAutorizacaoDbo | tabela | INSERT | Insere eventos de mudança de status |
| DbGestaoDebitoContaCorrente..TbEventoRegistroAutorizacaoDbo | tabela | UPDATE | Atualiza status de autorização |
| DbGestaoDebitoContaCorrente..TbLogEventoRegistroAtrzoDbto | tabela | INSERT | Insere log histórico de eventos |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| queries/*.xml | leitura | Queries.java | Arquivos XML contendo queries SQL parametrizadas |
| conf/wsdebitoconta.properties | leitura | PropertiesUtil.java | Configurações de acesso a webservices (endpoint, credenciais, timeout) |
| conf/job-resources.xml | leitura | Spring Framework | Configuração de datasources e recursos do job |
| conf/catalogo-filas.xml | leitura | Framework MQ | Catálogo de filas MQ (código comentado) |
| log/robo.log | gravação | Log4j | Logs de execução do batch |
| log/statistics-*.log | gravação | BvDailyRollingFileAppender | Logs de estatísticas de execução |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Responsável | Breve Descrição |
|--------------|-----------|-------------------|-----------------|
| TP.VAREJO.STATUS_AUTORIZACAO_DEBITO_CONTA | IBM MQ Series | ItemProcessor (código comentado) | Notificação de status de autorização de débito (funcionalidade desabilitada) |

**Observação**: O código de publicação em fila MQ está comentado no ItemProcessor, indicando que esta funcionalidade foi desabilitada ou está em desenvolvimento.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Service Bus BV | REST/SOAP | Endpoint configurado em wsdebitoconta.properties para serviço de débito em conta (https://servicebus[-ambiente].bvnet.bv/varejo/processamentoProdutoContrato/debitoContaBusinessService/v1) - código de integração não presente nos arquivos fornecidos |
| SQL Server/Sybase | JDBC | Banco de dados principal (DbGestaoDebitoContaCorrente, DBCRED, DBCOR) |
| IBM MQ Series | JMS | Mensageria (código comentado, não ativo) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Separação clara de responsabilidades (DAO, Business, Step)
- Uso de enums para constantes e códigos
- Tratamento de exceções com códigos de erro padronizados
- Logging adequado em pontos críticos
- Uso de framework batch estruturado
- Queries externalizadas em XML

**Pontos Negativos:**
- **Código comentado extensivamente**: Classes inteiras de integração MQ comentadas, indicando funcionalidades incompletas ou abandonadas
- **Encoding inconsistente**: Comentários em português com caracteres mal codificados (�)
- **Falta de documentação**: Javadoc incompleto ou genérico ("TODO Descrição do tipo")
- **Mistura de idiomas**: Código em inglês, comentários e mensagens em português
- **Clonagem defensiva excessiva**: Uso de clone() em datas pode ser substituído por tipos imutáveis (Java 8+ Date/Time API)
- **Tratamento de exceções genérico**: Muitos catch(Exception) sem tratamento específico
- **Hardcoded values**: Strings e números mágicos espalhados pelo código
- **Falta de testes**: Apenas um teste de integração básico
- **Dependências de versões antigas**: Framework e bibliotecas parecem desatualizados
- **SQL em strings**: Queries concatenadas em código (retornaSQLconsultaAutorizacaoPrevia)

---

## 14. Observações Relevantes

1. **Ambiente Multi-tenant**: Sistema possui configurações específicas para 4 ambientes (DES, QA, UAT, PRD) com diferentes servidores e credenciais.

2. **Segurança**: Senhas em alguns ambientes estão vazias ou criptografadas, com propriedade "sistema" usada no algoritmo de criptografia.

3. **Transações Distribuídas**: Uso de Bitronix para gerenciamento de transações JTA, com arquivos .tlog removidos após execução.

4. **Processamento Batch**: 
   - Commit interval: 1 registro
   - Checkpoint interval: 100.000 registros
   - Timeout de transação: 4 horas (14400000ms)
   - Execução concorrente habilitada

5. **Funcionalidade Desabilitada**: Todo código relacionado a publicação em filas MQ está comentado, sugerindo que a notificação assíncrona foi desabilitada.

6. **Geração de Código**: Classes de modelo JAXB foram geradas automaticamente a partir de XSDs (NotificacaoStatusAutorizacaoDebitoContaMensagem, StatusAutorizacaoDebitoConta).

7. **Framework Proprietário**: Sistema depende fortemente do framework BV-Sistemas, dificultando portabilidade.

8. **Banco de Dados**: Utiliza SQL Server/Sybase com múltiplos databases (DbGestaoDebitoContaCorrente, DBCRED, DBCOR, DBCOR).

9. **Execução**: Sistema pode ser executado via scripts .bat (Windows) ou .sh (Linux/Unix) com parâmetros de nome do job, execution ID e ambiente.

10. **Monitoramento**: Configuração de monitoramento JMX presente mas comentada (bv-monitoring.properties).