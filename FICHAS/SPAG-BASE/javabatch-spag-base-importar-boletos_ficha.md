# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **javabatch-spag-base-importar-boletos** é um job batch Java responsável por importar transações de boletos do sistema legado (Sybase) e enviá-las para processamento via fila MQ (IBM MQ). O processo busca transações de boletos liquidados em um período específico, filtra por contas apuradas e/ou CNPJs de clientes parametrizados, converte os dados para JSON e envia para uma fila de processamento. Aguarda resposta em fila de retorno para confirmar o sucesso da importação. Utiliza paginação para processar grandes volumes de dados.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê transações de boletos do banco Sybase em páginas, filtra por contas apuradas e CNPJs, gerencia conexão com fila MQ |
| **ItemWriter** | Envia transações para fila MQ e aguarda confirmação de processamento na fila de resposta |
| **MyResumeStrategy** | Estratégia de tratamento de erros do batch, define códigos de saída customizados |
| **TransacaoBoletoServiceImpl** | Serviço de negócio para buscar transações de boletos |
| **ContaApuracaoServiceImpl** | Serviço para buscar contas com apuração ativa |
| **ClienteServiceImpl** | Serviço para buscar CNPJs de clientes com forma de apuração por cliente |
| **FilaMQServiceImpl** | Serviço para comunicação com filas IBM MQ |
| **MQConnectionProvider** | Provedor de conexão e operações com IBM MQ |
| **TransacaoDetalheRebate** | Entidade de domínio representando uma transação de boleto |
| **ParametrosExecucao** | Classe para validação e armazenamento de parâmetros de execução do job |

---

## 3. Tecnologias Utilizadas

- **Java** com Maven
- **Spring Framework** (IoC/DI, JDBC)
- **BV Framework Batch** (framework proprietário para jobs batch)
- **IBM MQ** (WebSphere MQ) para mensageria
- **Sybase ASE** (banco de dados legado - DBPGF_TES)
- **Microsoft SQL Server** (banco de dados DBSPAG2 - spagRegraRebate)
- **JDBC** (jConnect para Sybase, JTDS para SQL Server)
- **Gson** para serialização/deserialização JSON
- **Log4j** para logging
- **Bitronix** para gerenciamento de transações XA
- **JUnit, PowerMock, Mockito** para testes

---

## 4. Principais Endpoints REST

não se aplica

---

## 5. Principais Regras de Negócio

1. **Filtro de Transações**: Busca apenas transações com código de liquidação 22, status 1 (liquidado), origem diferente de 2, no período especificado
2. **Apuração por Conta**: Filtra transações de contas cadastradas como apuradas no sistema SPAG (forma de apuração 'CON')
3. **Apuração por Cliente**: Filtra transações de clientes com forma de apuração 'CLI' e parametrização ativa
4. **Validação de Parâmetros**: Data inicial não pode ser posterior à data final; datas devem ser posteriores a 1990
5. **Paginação**: Processa registros em lotes de 10.000 para evitar sobrecarga de memória
6. **Confirmação de Processamento**: Aguarda resposta da fila de retorno com timeout de 10 segundos para confirmar sucesso
7. **Produto Fixo**: Todas as transações são marcadas com sigla de produto "PGBOLETO"
8. **Período Padrão**: Se não informado, processa o dia anterior (D-1)

---

## 6. Relação entre Entidades

**TransacaoDetalheRebate** (entidade principal):
- dataMovimento: data/hora da transação
- codLiquidacao: código de liquidação (22)
- cpfCnpjCliente: identificação do cliente remetente
- codOrigem: código de origem da transação
- valorTransacao: valor do boleto
- codigoBarra: código de barras do boleto
- banco: código do banco (3 primeiros dígitos do código de barras)
- siglaProduto: sempre "PGBOLETO"

**Relacionamentos com tabelas**:
- TBL_LANCAMENTO (Sybase): fonte das transações
- TbParametroCliente (SQL Server): parametrização de clientes
- TbContaApuracaoCliente (SQL Server): contas apuradas
- TbClienteRebate (SQL Server): cadastro de clientes

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| DBPGF_TES..TBL_LANCAMENTO | tabela | SELECT | Tabela de lançamentos/transações de boletos no Sybase |
| spagRegraRebate.TbParametroCliente | tabela | SELECT | Parametrização de clientes para rebate |
| spagRegraRebate.TbContaApuracaoCliente | tabela | SELECT | Contas configuradas para apuração |
| spagRegraRebate.TbClienteRebate | tabela | SELECT | Cadastro de clientes elegíveis para rebate |

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| log/robo.log | gravação | Log4j (RollingFileAppender) | Log principal da aplicação com rotação de 2MB |
| log/statistics-${executionId}.log | gravação | BvDailyRollingFileAppender | Log de estatísticas do framework batch |
| catalogo-filas.xml | leitura | MQConnectionProvider | Catálogo de configuração de filas MQ |
| job-resources.xml | leitura | Spring Context | Configuração de recursos (datasources, filas) |
| job-definitions.xml | leitura | Spring Context | Definição do job batch e beans |

---

## 10. Filas Lidas

- **QL.RETORNO_TRANSACAO_REBATE.INT**: Fila de resposta onde o sistema aguarda confirmação do processamento das transações enviadas. Timeout de 10 segundos.

---

## 11. Filas Geradas

- **QL.TRANSACAO_REBATE.INT**: Fila de envio onde o sistema publica as transações de boletos em formato JSON para processamento pelo sistema de rebate.

---

## 12. Integrações Externas

1. **IBM MQ (QM.ATA.01)**: Integração via filas para envio de transações e recebimento de confirmações
   - Host: qm_ata_des.bvnet.bv:1414
   - Canal: SPAG.SRVCONN
   - Usuário: _spag_des

2. **Sybase ASE (DBPGF_TES)**: Banco de dados legado fonte das transações de boletos
   - Servidor: sybdesspb.bvnet.bv:6500
   - Usuário: SPAG_BATCH

3. **SQL Server (DBSPAG2)**: Banco de dados de parametrização do sistema SPAG
   - Servidor: SQLDES27:17027
   - Usuário: SPAGRegraRebate

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades em camadas (repository, service, batch)
- Uso de interfaces para abstrair implementações
- Utilização de builders para construção de objetos complexos
- Tratamento de erros com códigos customizados
- Paginação implementada para grandes volumes

**Pontos Negativos:**
- Código com comentários e mensagens em português misturados com inglês
- Credenciais hardcoded nos arquivos de configuração (grave problema de segurança)
- Falta de documentação JavaDoc nas classes
- Uso de encoding ISO-8859-1 em alguns arquivos (deveria ser UTF-8)
- Tratamento de exceções genérico em alguns pontos (catch Exception)
- Falta de constantes para valores mágicos (ex: código de liquidação 22, status 1)
- Queries SQL embutidas em arquivos XML sem versionamento adequado
- Dependências com versões antigas (Spring 2.0)
- Falta de validação mais robusta de parâmetros de entrada
- Logs com informações sensíveis (senhas visíveis em configuração)

---

## 14. Observações Relevantes

1. **Ambiente**: Configurações apontam para ambiente de desenvolvimento/homologação (sufixos "des" nos hosts)
2. **Segurança**: Credenciais expostas em texto plano nos arquivos de configuração representam risco crítico de segurança
3. **Framework Proprietário**: Utiliza framework BV Systems, o que pode dificultar manutenção por equipes externas
4. **Versionamento**: Versão atual 0.8.4 indica que o sistema ainda está em fase de maturação
5. **Processamento**: O job não possui controle de reprocessamento ou checkpoint, reinicia do zero em caso de falha
6. **Timeout**: Timeout de 10 segundos para resposta pode ser insuficiente em cenários de alta carga
7. **Transações**: Não utiliza controle transacional entre banco e fila, possível inconsistência em caso de falha
8. **Encoding**: Uso de ISO-8859-1 pode causar problemas com caracteres especiais
9. **Dependências MQ**: Grande quantidade de JARs do IBM MQ indica versão antiga do cliente