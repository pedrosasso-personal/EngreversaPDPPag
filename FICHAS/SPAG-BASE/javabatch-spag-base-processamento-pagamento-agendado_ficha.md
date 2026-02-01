# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **javabatch-spag-base-processamento-pagamento-agendado** é um conjunto de jobs batch Java desenvolvidos para processar agendamentos de pagamentos e notificações no contexto do sistema SPAG (Sistema de Pagamentos). 

O sistema possui três fluxos principais:
- **Processamento de Agendamentos de Pagamento**: Busca agendamentos pendentes (DOC, TED, Transferências, Boletos, Tributos) e envia para filas MQ para processamento
- **Reenvio de Confirmações**: Reprocessa confirmações de pagamento que falharam no envio para a Fintech
- **Reenvio de Notificações**: Reprocessa notificações de pagamento (tributos e recebíveis/cash-in) que falharam no envio, incluindo sincronização de status

O sistema utiliza o framework BV Batch para processamento em lote com padrão Reader-Processor-Writer.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **br.com.votorantim.spag.nccs.batch.ItemReader** | Lê agendamentos de pagamento pendentes do banco de dados |
| **br.com.votorantim.spag.nccs.batch.ItemProcessor** | Processa agendamentos, converte para DicionarioPagamento e valida parâmetros Fintech |
| **br.com.votorantim.spag.nccs.batch.ItemWriter** | Envia agendamentos processados para filas MQ |
| **br.com.votorantim.spag.callback.confirmacao.batch.ItemReader** | Lê confirmações pendentes de reenvio |
| **br.com.votorantim.spag.callback.notificacao.batch.ItemReader** | Lê notificações pendentes de reenvio (tributos e recebíveis) |
| **br.com.votorantim.spag.callback.notificacao.batch.SincroniaReader** | Lê notificações para sincronização de status |
| **br.com.votorantim.spag.callback.notificacao.batch.SincroniaWriter** | Atualiza status de notificações e envia para fila MQ |
| **AgendamentoPagamentoDAOImpl** | Acesso a dados de agendamentos de pagamento |
| **NotificacaoRecebivelRepository** | Repositório para notificações de recebíveis |
| **SincroniaRecebivelRespository** | Repositório para sincronização de notificações |
| **AgendaPagamentoServiceImpl** | Converte agendamentos para XML e DicionarioPagamento |
| **FilaMqWriterImpl** | Envia mensagens para filas IBM MQ |

---

## 3. Tecnologias Utilizadas

- **Java** (versão não especificada explicitamente)
- **Maven** (gerenciamento de dependências e build)
- **Spring Framework** (IoC/DI, JDBC)
- **BV Framework Batch** (framework proprietário para processamento batch)
- **IBM MQ 7.0.1.10** (mensageria)
- **JAXB** (serialização XML)
- **Sybase jConnect 4** (driver JDBC)
- **SQL Server** (banco DBSPAG)
- **Sybase ASE** (bancos DBITP, DBGLOBAL, DBCONTACORRENTE)
- **JUnit** (testes)
- **Log4j** (logging)
- **Gson 2.3.1** (serialização JSON)
- **Bitronix** (gerenciamento de transações)

---

## 4. Principais Endpoints REST

não se aplica

---

## 5. Principais Regras de Negócio

1. **Processamento de Agendamentos**:
   - Apenas agendamentos com status "NOVO_AGENDAMENTO" (0) são processados
   - Verifica se o dia atual é dia útil antes de processar
   - Suporta antecipação de pagamento (flag FlAntecipaPagamento)
   - Valida parâmetros Fintech para lançamento incondicional de saldo
   - Atualiza status para "EM_PROCESSAMENTO" (1) durante processamento

2. **Reenvio de Confirmações**:
   - Reprocessa confirmações que retornaram com erro (código diferente de 200)
   - Limita tentativas de reenvio (padrão: 5 tentativas)
   - Considera apenas registros do dia atual

3. **Reenvio de Notificações de Tributos**:
   - Reprocessa notificações com código de liquidação 59 e 60
   - Limita tentativas de reenvio (padrão: 5 tentativas)
   - Filtra por data de inclusão atual

4. **Reenvio de Notificações de Recebíveis (Cash-in)**:
   - Valida se cliente está habilitado para reprocessamento (flag FlReprocessamentoNotificacao)
   - Verifica se pagamento existe na caixa de entrada SPB
   - Filtra por contas configuradas com retry
   - Considera liquidações tipo 31, 32, 21 (cash-in)

5. **Sincronização de Notificações**:
   - Busca protocolos de lançamentos que não possuem notificação
   - Atualiza status na tabela IntegracaoItpVolta
   - Permite filtro por data de movimento e protocolo específico

---

## 6. Relação entre Entidades

**Principais Entidades:**

- **AgendamentoPagamento**: Representa um agendamento de pagamento
  - Relaciona-se com **AgendamentoFavorecido** (1:N) - múltiplos favorecidos por agendamento
  
- **ConfirmacaoPendente**: Confirmação de pagamento pendente de reenvio
  - Relaciona-se com **ConfirmacaoPagamento** (1:1) - conversão para reenvio

- **NotificacaoPendente**: Notificação pendente de reenvio (tributos)
  - Relaciona-se com **NotificacaoPagamento** (1:1) - conversão para reenvio

- **NotificacaoFintech**: Notificação de pagamento para Fintech
  - Relaciona-se com **CaixaEntrada** (N:1) - validação de pagamento

- **DicionarioPagamento**: DTO para envio de pagamentos via MQ
  - Agregação de dados de AgendamentoPagamento e AgendamentoFavorecido

**Relacionamentos de Banco de Dados:**
- TbAgendamentoPagamento ↔ TbAgendamentoFavorecido (1:N)
- TbNotificacaoFintech ↔ TbControleRetornoNotificacao (1:N)
- TbRetornoSolicitacaoFintech ↔ TbControleRetornoSlctoFintech (1:N)
- TBL_CAIXA_ENTRADA_SPB ↔ TbIntegracaoItpVolta (1:1)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbAgendamentoPagamento | tabela | SELECT | Agendamentos de pagamento pendentes |
| TbAgendamentoFavorecido | tabela | SELECT | Favorecidos dos agendamentos |
| TbParametroPagamentoFintech | tabela | SELECT | Parâmetros de configuração Fintech |
| TbControleRetornoSlctoFintech | tabela | SELECT | Controle de retorno de confirmações |
| TbRetornoSolicitacaoFintech | tabela | SELECT | Retornos de solicitações Fintech |
| TbControleRetornoNotificacao | tabela | SELECT | Controle de retorno de notificações |
| TbNotificacaoFintech | tabela | SELECT | Notificações para Fintech |
| TBL_CAIXA_ENTRADA_SPB | tabela | SELECT | Caixa de entrada SPB (DBITP) |
| TBL_LANCAMENTO | tabela | SELECT | Lançamentos financeiros (DBPGF_TES) |
| TbValidacaoOrigemPagamento | tabela | SELECT | Validação de origem de pagamentos |
| DBGLOBAL..PrProximoDiaUtil | procedure | EXEC | Calcula próximo dia útil |
| DBGLOBAL..PrDiaUtilAnterior | procedure | EXEC | Calcula dia útil anterior |
| DBGLOBAL..PrVerificaDataUtil | procedure | EXEC | Verifica se data é dia útil |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbAgendamentoPagamento | tabela | UPDATE | Atualiza status do agendamento (CdStatusAgendamento, DtAlteracao) |
| DbIntegracaoItp..TbIntegracaoItpVolta | tabela | INSERT/UPDATE | Insere/atualiza status de processamento de notificações (StProcessamento='W') |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| catalogo-filas.xml | leitura | Configuração MQ | Catálogo de filas MQ para envio de mensagens |
| bv-framework-integration-mq-conf.properties | leitura | Configuração MQ | Propriedades de integração com MQ |
| job-resources.xml | leitura | Spring Context | Configuração de recursos (datasources, beans) |
| job-definitions.xml | leitura | Spring Context | Definição dos jobs batch |
| log4j.xml | leitura | Log4j | Configuração de logging |
| statistics-${executionId}.log | gravação | BvDailyRollingFileAppender | Log de estatísticas de execução do batch |
| robo.log | gravação | RollingFileAppender | Log geral da aplicação |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Breve Descrição |
|--------------|-----------|-----------------|
| QL.SPAG.SOLICITAR_PAGAMENTO_BOLETO_REQ.INT | IBM MQ | Solicitações de pagamento de boleto |
| QL.SPAG.SOLICITAR_PAGAMENTO_DOC_REQ.INT | IBM MQ | Solicitações de pagamento DOC |
| QL.SPAG.SOLICITAR_PAGAMENTO_TED_REQ.INT | IBM MQ | Solicitações de pagamento TED |
| QL.SPAG.SOLICITAR_PAGAMENTO_CC_REQ.INT | IBM MQ | Solicitações de transferência conta corrente |
| QL.SPAG.SOLICITAR_PAGAMENTO_TRIBUTO_REQ.INT | IBM MQ | Solicitações de pagamento de tributo |
| QL.SPAG.VALIDAR_PAGAMENTO_REQ.INT | IBM MQ | Confirmações de pagamento (reenvio) |
| QL.SPAG.NOTIFICAR_PAGAMENTO_REQ.INT | IBM MQ | Notificações de pagamento tributos (reenvio) |
| QL.SPAG.NOTIFICAR_PARCEIRO_REQ.INT | IBM MQ | Notificações de pagamento recebíveis (reenvio) |

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Breve Descrição |
|-----------------|------|-----------------|
| IBM MQ (QM.ATA.01) | Mensageria | Envio de solicitações de pagamento e notificações |
| DBSPAG (SQL Server) | Banco de Dados | Base principal de agendamentos e notificações |
| DBITP (Sybase ASE) | Banco de Dados | Base de integração ITP (caixa entrada SPB, lançamentos) |
| DBGLOBAL (Sybase ASE) | Banco de Dados | Base global (procedures de dias úteis) |
| DBCONTACORRENTE (Sybase ASE) | Banco de Dados | Base de conta corrente |
| BV Crypto | Serviço | Descriptografia de senhas |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 6/10

**Justificativa:**

**Pontos Positivos:**
- Uso de padrão arquitetural Reader-Processor-Writer bem definido
- Separação de responsabilidades em camadas (DAO, Service, Batch)
- Uso de interfaces para abstrair repositórios
- Configuração externalizada via Spring XML
- Tratamento de exceções customizado (BatchExecutionException)

**Pontos Negativos:**
- **Código legado com comentários em português e encoding issues** (caracteres especiais mal formatados)
- **Strings SQL hardcoded** nas classes DAO ao invés de arquivos separados
- **Falta de documentação JavaDoc** na maioria das classes
- **Mistura de responsabilidades**: classes DAO executando lógica de negócio
- **Código duplicado**: múltiplas implementações similares de ItemReader/Writer/Processor
- **Configurações hardcoded**: credenciais e URLs em arquivos XML de configuração
- **Falta de testes unitários**: apenas testes de integração presentes
- **Uso de tipos primitivos e wrappers inconsistente**
- **Nomenclatura inconsistente**: mistura de português e inglês
- **Dependências desatualizadas**: Gson 2.3.1 (2014), IBM MQ 7.0 (2008)
- **Tratamento de erros genérico**: muitos catch blocks vazios ou apenas com log

---

## 14. Observações Relevantes

1. **Múltiplos Fluxos**: O sistema possui 4 jobs distintos configuráveis:
   - Processamento de agendamentos (NCCS)
   - Reenvio de confirmações
   - Reenvio de notificações de tributos
   - Reenvio de notificações de recebíveis (com sincronização)

2. **Configuração por Ambiente**: Existem múltiplos arquivos de configuração para diferentes ambientes (DEV, UAT, PROD)

3. **Framework Proprietário**: Utiliza framework BV Batch proprietário, dificultando portabilidade

4. **Segurança**: Senhas criptografadas usando BVCrypto, mas chaves expostas em configuração

5. **Processamento Condicional**: Valida dia útil antes de processar agendamentos

6. **Retry Mechanism**: Implementa mecanismo de retry para notificações falhadas (limite configurável)

7. **Sincronização**: Fluxo de sincronização atualiza tabela IntegracaoItpVolta para reprocessamento

8. **Contas Específicas**: Filtro por contas específicas (Neon, Dock, Ipiranga) para notificações de recebíveis

9. **Limite de Cláusula IN**: Implementa paginação para queries com IN clause (limite 2000 itens)

10. **Conversão XML/JSON**: Suporta serialização em XML (JAXB) e JSON (Gson) conforme necessidade