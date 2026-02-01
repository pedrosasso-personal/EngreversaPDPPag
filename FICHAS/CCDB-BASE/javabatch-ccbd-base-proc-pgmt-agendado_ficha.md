# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java responsável pelo processamento de agendamentos de pagamentos do CCBD (Conta Corrente Banco Digital). O sistema lê lançamentos agendados de um banco de dados SQL Server, processa-os e envia mensagens para uma fila IBM MQ para posterior liquidação. Opera com base em uma data de processamento parametrizável e prioriza transações BVIN (código 497) no processamento.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê lançamentos agendados do banco de dados para a data de processamento especificada e ordena por prioridade |
| **ItemProcessor** | Processa cada lançamento (atualmente apenas repassa o objeto sem transformações) |
| **ItemWriter** | Serializa lançamentos em JSON e envia para fila IBM MQ |
| **AgendamentoRepositoryImpl** | Implementa acesso ao banco de dados SQL Server para recuperar lançamentos |
| **LancamentoMapper** | Mapeia ResultSet do banco de dados para objetos Lancamento |
| **MqWriter** | Gerencia conexão e envio de mensagens para IBM MQ |
| **MqConnectionProperties** | Encapsula propriedades de conexão com IBM MQ |
| **AgendamentoUtil** | Utilitário para carregar queries SQL de arquivos XML |
| **Lancamento** | Value Object representando um lançamento agendado com dados de remetente, favorecido e transação |
| **Pessoa** | Value Object representando dados bancários de remetente ou favorecido |
| **MyResumeStrategy** | Estratégia de retomada do job em caso de falha |

---

## 3. Tecnologias Utilizadas

- **Java** (linguagem principal)
- **Maven** (gerenciamento de dependências e build)
- **Spring Framework 2.0** (injeção de dependências e configuração)
- **BV Framework Batch** (framework proprietário para processamento batch)
- **IBM MQ 7.0.1.10** (mensageria)
- **SQL Server** (banco de dados - driver JTDS)
- **Bitronix** (gerenciador de transações JTA)
- **Jackson 2.0.0** (serialização JSON)
- **Log4j 1.2.17** (logging)
- **JUnit** (testes)
- **SLF4J** (facade de logging)

---

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch sem endpoints REST.

---

## 5. Principais Regras de Negócio

1. **Priorização de Transações**: Lançamentos com código de liquidação BVIN (1) e código de transação BVIN (497) são processados prioritariamente através do método `compareTo()` da classe Lancamento
2. **Filtro por Status**: Apenas lançamentos com status "1" (presumivelmente "Pendente" ou "Agendado") são processados
3. **Filtro por Data**: Processa apenas lançamentos cuja data de agendamento corresponde à data de processamento informada
4. **Data Default**: Se a data de processamento não for informada, utiliza a data atual no formato "yyyyMMdd"
5. **Ordenação**: Lista de lançamentos é ordenada antes do processamento para garantir prioridade de execução
6. **Serialização JSON**: Lançamentos são convertidos para JSON antes do envio para fila MQ
7. **Controle de Tentativas**: Sistema registra quantidade de tentativas de liquidação (campo QtTentativaLiquidacao)

---

## 6. Relação entre Entidades

**Lancamento** (entidade principal)
- Contém 1 **Pessoa** como remetente (composição)
- Contém 1 **Pessoa** como favorecido (composição)
- Referencia 1 **Produto** (através de codigoProduto)
- Possui dados de transação (codigoTransacao, codigoLiquidacao, codigoFinalidade)
- Possui dados de boleto (codigoDetalheBoleto, codigoBarra, linhaDigitavel)
- Possui dados de investimento (codigoEnvelopeInvestimento, codigoParametroAgendaOperacao)

**Pessoa**
- Representa dados bancários (banco, agência, conta, tipo de conta)
- Representa dados pessoais (CPF/CNPJ, nome, tipo de pessoa)

**Produto**
- Entidade simples com apenas código identificador

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| ccbdagendamento.TbAgendamento | Tabela | SELECT | Tabela principal contendo dados dos agendamentos de pagamento |
| ccbdagendamento.TbStatusAgendamento | Tabela | SELECT | Tabela de status dos agendamentos (join para descrição) |
| ccbdagendamento.TbPessoaAgendamento | Tabela | SELECT | Tabela contendo dados de remetente e favorecido do agendamento |
| ccbdagendamento.TbParametroAgendaOperacao | Tabela | SELECT | Tabela com parâmetros de operação (left join - dados opcionais de investimento) |

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema apenas lê dados do banco, não realiza operações de INSERT, UPDATE ou DELETE.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| AgendamentoRepositoryImpl-sql.xml | Leitura | AgendamentoUtil.getSqlFromFile() | Arquivo XML contendo queries SQL parametrizadas |
| log/statistics-${executionId}.log | Gravação | Log4j (BvDailyRollingFileAppender) | Arquivo de log de estatísticas do processamento batch |
| Console output | Gravação | Log4j (ConsoleAppender) | Saída de logs no console |

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

---

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Responsável | Breve Descrição |
|--------------|-----------|-------------------|-----------------|
| QL.CCBD.PROC_AGENDAMENTO_DIG.INT | IBM MQ (Queue Manager: QM.DIG.01) | MqWriter / ItemWriter | Fila para envio de lançamentos agendados serializados em JSON para processamento de liquidação |

**Configuração da Fila:**
- Host: qm_dig_des.bvnet.bv
- Porta: 1419
- Canal: CCBD.SRVCONN
- Usuário: _ccbd_des

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| SQL Server (SQLDES35:17035) | Banco de Dados | Banco DBCCBD - leitura de agendamentos, status, pessoas e parâmetros |
| IBM MQ (qm_dig_des.bvnet.bv:1419) | Mensageria | Envio de mensagens JSON com lançamentos para processamento posterior |

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades (Reader, Processor, Writer)
- Uso adequado de padrões batch (framework BV)
- Logging estruturado e presente nas principais operações
- Configuração externalizada em XML
- Uso de Value Objects (Lancamento, Pessoa)
- Tratamento de exceções com códigos de saída específicos

**Pontos Negativos:**
- **ItemProcessor vazio**: não realiza nenhuma transformação, questionável sua necessidade
- **Comentários em português com caracteres especiais**: podem causar problemas de encoding
- **Falta de validações**: não valida dados antes de enviar para fila
- **Hardcoded values**: constantes CODIGO_TRANSACAO_BVIN e CODIGO_LIQUIDACAO_BVIN poderiam ser configuráveis
- **Tratamento de exceções genérico**: captura Exception em vez de exceções específicas
- **Falta de testes unitários**: apenas teste de integração presente
- **Dependências desatualizadas**: Spring 2.0, Jackson 2.0.0, Log4j 1.2.17 são versões muito antigas
- **Código de comparação confuso**: lógica do `compareTo()` não é intuitiva
- **Falta de documentação JavaDoc**: classes não possuem documentação formal
- **Senhas em texto claro**: credenciais expostas no arquivo de configuração XML

---

## 14. Observações Relevantes

1. **Ambiente**: Configuração aponta para ambiente de desenvolvimento (SQLDES35, qm_dig_des)
2. **Credenciais Expostas**: Senhas de banco de dados e MQ estão em texto claro no arquivo job-resources.xml - **RISCO DE SEGURANÇA**
3. **Framework Proprietário**: Sistema depende fortemente do BV Framework Batch, dificultando portabilidade
4. **Versão**: Sistema está na versão 0.2.0, indicando estágio inicial de desenvolvimento
5. **Exit Codes Documentados**: 
   - 0: Sucesso
   - 10: Erro ao ler dados do banco
   - 20: Erro ao postar mensagem na fila
6. **Parâmetro Obrigatório**: dataProcessamento é obrigatório (formato: yyyyMMdd)
7. **Transações**: Sistema configurado com `allowLocalTransactions=true` no datasource
8. **Pool de Conexões**: Configurado com mínimo 1 e máximo 10 conexões
9. **Produto Relacionado**: Sistema faz parte da plataforma CCBD (Conta Corrente Banco Digital) da Votorantim
10. **Build**: Utiliza assembly Maven para gerar distribuível ZIP com scripts shell e bat