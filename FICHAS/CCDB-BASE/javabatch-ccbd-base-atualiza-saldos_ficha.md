# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java responsável pela virada de data de contas correntes (atualização de saldos). O processo realiza a movimentação das datas de controle das agências, bloqueando temporariamente as movimentações, processando as contas em faixas paralelas (threads) e atualizando os saldos para o próximo dia útil. Utiliza mensageria RabbitMQ para distribuir o processamento das faixas de contas e integra-se com banco de dados MySQL (CCBDContaCorrente) e Sybase (dbglobal) para controle de calendário e dias úteis.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê as agências com status de virada pendente, valida se é dia útil e se existe processo em aberto |
| **ItemProcessor** | Calcula próximos dias úteis, busca contas não encerradas e monta faixas de processamento por thread |
| **ItemWriter** | Orquestra todo o processo de virada: bloqueio, envio de mensagens, aguardo de processamento e liberação |
| **ContaService** | Gerencia operações relacionadas a contas correntes (busca, contagem, cálculo de dias úteis) |
| **ControleDataService** | Gerencia operações na tabela de controle de datas das agências |
| **RotinaExecucaoService** | Controla o ciclo de vida da rotina de virada (iniciar, processar, sucesso, erro) |
| **ViradaThreadService** | Gerencia as faixas de processamento (threads) e aguarda conclusão |
| **MessageService** | Envia mensagens para filas RabbitMQ para processamento distribuído |
| **FaixasThreadProcessor** | Divide as contas em faixas para processamento paralelo |
| **MyResumeStrategy** | Estratégia de tratamento de erros do framework batch |

---

## 3. Tecnologias Utilizadas

- **Java** com Apache Maven
- **Framework BV Batch** (br.com.bvsistemas.framework.batch) - framework proprietário para processamento batch
- **Spring Framework** 2.0 (IoC/DI, JDBC)
- **MySQL 8.0.22** (banco principal - CCBDContaCorrente)
- **Sybase ASE** via jTDS (banco dbglobal - calendário e dias úteis)
- **RabbitMQ** via Spring AMQP (mensageria para processamento distribuído)
- **Bitronix** (gerenciador de transações JTA)
- **Log4j** (logging)
- **Gson 2.8.9** (serialização JSON)
- **JUnit** (testes)
- **BV Crypto** (criptografia de senhas)

---

## 4. Principais Endpoints REST

não se aplica

---

## 5. Principais Regras de Negócio

1. **Validação de Dia Útil**: O processo só executa em dias úteis, verificado via stored procedure no banco Sybase
2. **Controle de Execução Única**: Verifica se já existe processo em aberto para a data antes de iniciar
3. **Bloqueio de Movimentações**: Bloqueia movimentações nas agências durante a virada (FlAceitaMovimentacao = 'N')
4. **Processamento em Faixas**: Divide contas em faixas configuráveis (QtMaximaContasPorThread) para processamento paralelo
5. **Liberação Gradual**: Libera stand-in antes da conclusão total, depois libera completamente após todas as threads
6. **Cálculo de Dias Úteis**: Calcula e mantém janela de 11 dias (5 passados + atual + 5 futuros)
7. **Exclusão de Contas Encerradas**: Processa apenas contas com DtEncerramentoConta IS NULL
8. **Controle de Status**: Gerencia status da rotina (0=Iniciar, 1=Processamento, 2=Sucesso, 3=Erro)
9. **Agendamento Automático**: Insere automaticamente rotina para o próximo dia útil
10. **Sincronização de Threads**: Aguarda conclusão de todas as faixas antes de liberar agências

---

## 6. Relação entre Entidades

**ControleData**: Entidade central que representa o controle de datas de uma agência
- Relaciona-se com **ViradaDataThread** (1:N) - uma agência possui múltiplas faixas de processamento
- Contém 11 datas (5 passadas + atual + 5 futuras) para janela de movimentação

**Rotina**: Representa a execução da rotina de virada
- Código fixo: 30 (VIRA_CONTAS)
- Status: 0=Iniciar, 1=Processamento, 2=Sucesso, 3=Erro

**RotinaExecucaoAgencia**: Controla execução por agência
- Registra timestamps de início, fim de bloqueio e fim de execução

**ViradaDataThread**: Representa uma faixa de contas para processamento
- Contém range de contas (NuContaCorrenteIni/Fim)
- Status de processamento e grid

**Parametro**: Configurações do sistema
- QtMaximaContasPorThread: define tamanho das faixas

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbControleData | tabela | SELECT | Busca agências com status de virada pendente (StViradaData = 0 ou 1) |
| TbConta | tabela | SELECT | Busca contas não encerradas para processamento (COUNT e lista de NuContaCorrente) |
| TbParametro | tabela | SELECT | Busca quantidade máxima de contas por thread |
| TbRotinaExecucao | tabela | SELECT | Verifica se existe rotina em execução para a data |
| TbRotinaExecucaoAgencia | tabela | SELECT | Busca máxima data de início de execução por agência |
| TbViradaDataThread | tabela | SELECT | Conta threads em bloqueio e threads restantes para processamento |
| DBGLOBAL..PrVerificaDataUtil | stored procedure | EXECUTE | Verifica se data é dia útil (retorna 'S' ou 'N') |
| DBGLOBAL..PrProximoDiaUtil | stored procedure | EXECUTE | Calcula próximo dia útil a partir de uma data |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbControleData | tabela | UPDATE | Atualiza janela de 11 datas, status de virada e flag de movimentação |
| TbRotinaExecucao | tabela | INSERT | Insere nova rotina para próximo dia útil |
| TbRotinaExecucao | tabela | UPDATE | Atualiza status da rotina (processamento, sucesso, erro) e timestamps |
| TbRotinaExecucaoAgencia | tabela | UPDATE | Atualiza timestamps de execução (início, fim bloqueio, fim execução) |
| TbViradaDataThread | tabela | INSERT | Insere faixas de contas para processamento |
| TbViradaDataThread | tabela | UPDATE | Atualiza status e datas das faixas |
| TbViradaDataThread | tabela | DELETE | Limpa faixas antigas antes de novo processamento |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| job-resources.xml | leitura | Spring Context | Configuração de datasources e recursos por ambiente (DES/UAT/PRD) |
| job-definitions.xml | leitura | Spring Context | Definição dos beans do job batch |
| *-sql.xml | leitura | QueryReader | Arquivos XML contendo queries SQL para cada Repository |
| log4j.xml | leitura | Log4j | Configuração de logging |
| log/robo.log | gravação | Log4j RollingFileAppender | Log principal da aplicação |
| log/statistics-{executionId}.log | gravação | BvDailyRollingFileAppender | Log de estatísticas do framework batch |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

**Exchange**: ex.ccbd.viraConta

**Routing Keys**:
1. **atualizacao.conta.faixa** - Mensagens para inserir/atualizar valores das faixas de contas durante bloqueio
2. **atualizacao.conta.faixa.pos.desbloqueio** - Mensagens para atualizar valores após desbloqueio

**Payload**: JSON serializado via Gson contendo:
- **AtualizaFaixaContaRequest**: codigoBanco, codigoAgencia, numeroContaCorrenteInicio/Fim, dataAntesDaVirada, dataDepoisDaVirada
- **ContaRequest**: codigoBanco, codigoAgencia, numeroContaCorrenteInicio/Fim, codigoTipoConta

---

## 12. Integrações Externas

1. **Banco MySQL (CCBDContaCorrente)**: Banco principal com dados de contas, controle de datas e rotinas
2. **Banco Sybase (dbglobal)**: Banco corporativo para validação de dias úteis e cálculo de calendário
3. **RabbitMQ**: Fila de mensagens para distribuição do processamento de faixas de contas entre workers
4. **BV Crypto**: Serviço de criptografia para descriptografar senhas de banco em produção

---

## 13. Avaliação da Qualidade do Código

**Nota:** 6/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades em camadas (batch, service, repository, domain)
- Uso adequado de injeção de dependências via Spring
- Externalização de queries SQL em arquivos XML
- Tratamento de erros com estratégia customizada (MyResumeStrategy)
- Uso de padrão Command para aguardar processamento

**Pontos Negativos:**
- Código legado com tecnologias antigas (Spring 2.0, framework proprietário)
- Falta de documentação JavaDoc nas classes
- Uso de polling ativo (loop com 1000 iterações) para aguardar threads - poderia usar mecanismos mais eficientes
- Hardcoded de valores (usuário 551, código de rotina 30, código de tipo conta "5")
- Falta de testes unitários (apenas teste de integração)
- Comentários em português misturados com código
- Uso de `@SuppressWarnings("unchecked")` sem justificativa
- Falta de validações de entrada em alguns métodos
- Acoplamento com framework proprietário BV dificulta manutenção e testes

---

## 14. Observações Relevantes

1. **Execução Agendada**: O sistema é executado via UC4 (agendador) com parâmetro opcional `dataRotina`
2. **Processamento Distribuído**: Utiliza arquitetura de mensageria para distribuir processamento entre múltiplos workers
3. **Resiliência**: Em caso de erro, insere automaticamente rotina para próximo dia e marca status como erro
4. **Ambientes**: Possui configurações específicas para DES, UAT e PRD com diferentes credenciais e endpoints
5. **Transação**: Usa gerenciador de transações Bitronix com timeout de 1200000ms (20 minutos)
6. **Exit Codes**: Define códigos de saída customizados (10, 20) para integração com UC4
7. **Criptografia**: Em produção, usa BV_CRYPTO_TOKEN para descriptografar senhas
8. **Janela de Datas**: Mantém janela móvel de 11 dias úteis para controle de movimentações
9. **Sincronização**: Processo crítico que bloqueia movimentações - requer monitoramento rigoroso
10. **Dependência de Calendário**: Totalmente dependente das stored procedures do Sybase para cálculo de dias úteis