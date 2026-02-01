# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **javabatch-spag-base-gerar-relatorio** é uma aplicação batch Java desenvolvida para gerar relatórios de pagamentos de rebate e extratos de transações. O sistema consome mensagens de filas IBM MQ, processa dados de pagamentos e transações, e gera arquivos CSV com informações detalhadas. Possui dois fluxos principais:

1. **Geração de Relatório de Pagamentos Rebate**: Processa pagamentos, calcula impostos (IR e ISS), e gera relatório consolidado em CSV.
2. **Geração de Extrato de Transações (Callback)**: Processa extratos de transações por cliente, gerando arquivos CSV individualizados com resumos.

O sistema utiliza o framework BV Batch para processamento em lote, seguindo o padrão Reader-Processor-Writer.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê mensagens da fila MQ contendo listas de pagamentos rebate |
| **ItemProcessor** | Transforma objetos de domínio (PagamentoRebate) em DTOs para relatório |
| **ItemWriter** | Escreve dados processados em arquivos CSV |
| **MyResumeStrategy** | Estratégia de tratamento de erros e códigos de saída do batch |
| **MQConnectionProvider** | Gerencia conexões e operações com filas IBM MQ |
| **MQService / MQServiceImpl** | Serviço de abstração para operações de mensageria |
| **FileService / FileServiceImpl** | Serviço para manipulação de arquivos (criação, escrita, renomeação) |
| **ConverterJsonUtils** | Utilitário para conversão entre objetos Java e JSON (usando Gson) |
| **PagamentoRebate** | Entidade de domínio representando um pagamento de rebate |
| **Parametrizacao** | Entidade contendo parâmetros de configuração do pagamento |
| **ExtratoTransacao** | Entidade representando uma transação de extrato |
| **RelatorioPagamentoDTO** | DTO para geração do relatório de pagamentos |
| **ExtratoDTO** | DTO para geração do extrato de transações |

---

## 3. Tecnologias Utilizadas

- **Java** (linguagem principal)
- **Maven** (gerenciamento de dependências e build)
- **Spring Framework** (injeção de dependências e configuração)
- **BV Framework Batch** (framework proprietário para processamento batch)
- **IBM MQ (WebSphere MQ)** (mensageria)
- **JMS** (Java Message Service)
- **Gson** (serialização/deserialização JSON)
- **Log4j** (logging)
- **JUnit** (testes unitários)
- **Mockito/PowerMock** (mocks para testes)

---

## 4. Principais Endpoints REST

**Não se aplica** - O sistema é uma aplicação batch sem endpoints REST.

---

## 5. Principais Regras de Negócio

1. **Cálculo de Impostos**: Calcula valores de IR e ISS sobre pagamentos brutos, gerando valores líquidos
2. **Apuração por Periodicidade**: Suporta apuração diária, semanal, mensal e personalizada
3. **Tipos de Apuração**: Permite apuração por quantidade de transações ou por valor
4. **Forma de Rebate**: Suporta rebate por valor fixo ou percentual
5. **Aprovação de Pagamentos**: Controla fluxo de aprovação com flag de necessidade, nome do aprovador e observações
6. **Status de Pagamento**: Gerencia estados (Pago, Pendente, Pendente de Aprovação, Recusado, Cancelado)
7. **Apuração Bancária**: Diferencia transações do próprio banco, outros bancos ou ambos
8. **Contagem de Prazo**: Calcula prazos em dias úteis ou corridos
9. **Geração de Arquivos Temporários**: Cria arquivos com sufixo "-temp" e renomeia ao final do processamento
10. **Processamento por Lotes**: Consome mensagens da fila em lotes até receber status FINALIZADO/TODOS_FINALIZADOS
11. **Geração de Resumos**: Para extratos, gera resumo consolidado no início do arquivo CSV

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **PagamentoRebate**: Contém informações de um pagamento individual
  - Relacionamento 1:1 com **Parametrizacao** (configurações do pagamento)
  - Relacionamento 0:1 com **FaixaResponse** (faixa de valores/percentuais aplicada)
  
- **Parametrizacao**: Configurações de apuração e pagamento
  - Contém enums: Periodicidade, TipoApuracao, FormaRebate, TipoEntrada, ApuracaoBancaria, ContagemPrazo

- **ListaPagamentosRebate**: Agregador de pagamentos
  - Relacionamento 1:N com **PagamentoRebate**
  - Contém StatusProcessamento (controle de fluxo)

- **ExtratoTransacao**: Representa uma transação individual
  
- **ListaExtratoTransacao**: Agregador de transações
  - Relacionamento 1:N com **ExtratoTransacao**
  - Relacionamento 1:1 com **ResumoExtrato**

- **ItemExtrato**: Composição de ExtratoTransacao + ResumoExtrato para processamento

---

## 7. Estruturas de Banco de Dados Lidas

**Não se aplica** - O sistema não acessa diretamente banco de dados. Recebe dados via filas MQ.

---

## 8. Estruturas de Banco de Dados Atualizadas

**Não se aplica** - O sistema não atualiza banco de dados diretamente. Apenas consome e produz mensagens em filas.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| PR{MM}{YYYY}.csv | Gravação | ItemWriter (batch principal) | Relatório mensal de pagamentos rebate consolidado |
| PR{MM}{YYYY}-temp.csv | Gravação/Leitura | FileServiceImpl | Arquivo temporário durante geração do relatório |
| ER{CPF/CNPJ}{P/S/M/D}{SIGLA}{ddMMyyyy}.csv | Gravação | ItemWriter (callback extrato) | Extrato de transações por cliente (P=Personalizado, S=Semanal, M=Mensal, D=Diário) |
| ER{CPF/CNPJ}{P/S/M/D}{SIGLA}{ddMMyyyy}-temp.csv | Gravação/Leitura | FileServiceImpl | Arquivo temporário do extrato |
| log/robo.log | Gravação | Log4j | Log principal da aplicação |
| log/statistics-{executionId}.log | Gravação | BvDailyRollingFileAppender | Log de estatísticas do framework batch |

---

## 10. Filas Lidas

| Nome da Fila | Tipo | Descrição |
|--------------|------|-----------|
| QL.RETORNO_RELATORIO_REBATE.INT | IBM MQ | Fila de retorno com listas de pagamentos rebate para processamento do relatório principal |
| QL.RETORNO_RELATORIO_PARCEIRO_REBATE.INT | IBM MQ | Fila de retorno com listas de extratos de transações para processamento do callback |

---

## 11. Filas Geradas

| Nome da Fila | Tipo | Descrição |
|--------------|------|-----------|
| QL.ENVIO_RELATORIO_REBATE.INT | IBM MQ | Fila de envio para iniciar geração do relatório de pagamentos rebate |
| QL.TRANSACAO_REBATE.INT | IBM MQ | Fila alternativa de envio (configurada em catalogo-filas.xml) |
| QL.ENVIO_RELATORIO_PARCEIRO_REBATE.INT | IBM MQ | Fila de envio para iniciar geração do extrato de transações (callback) |

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| IBM MQ (QM.ATA.01) | Mensageria | Queue Manager IBM MQ para comunicação assíncrona. Host: qm_ata_des.bvnet.bv, Porta: 1414, Canal: SPAG.SRVCONN |
| Sistema Produtor de Pagamentos | Integração via Fila | Sistema não identificado que publica mensagens de pagamentos rebate nas filas de retorno |
| Sistema Produtor de Extratos | Integração via Fila | Sistema não identificado que publica mensagens de extratos de transações nas filas de retorno |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com padrão Reader-Processor-Writer
- Uso adequado de padrão Builder para construção de objetos complexos
- Tratamento de erros com códigos de saída customizados
- Cobertura de testes unitários presente
- Uso de interfaces para abstração de serviços (MQService, FileService)
- Logging adequado em pontos críticos

**Pontos de Melhoria:**
- Credenciais hardcoded nos arquivos de configuração (usuário e senha do MQ)
- Comentários em português misturados com código em inglês
- Caracteres especiais mal codificados (encoding issues) em comentários
- Falta de documentação JavaDoc nas classes principais
- Uso de `Collections.EMPTY_LIST` (deprecated) ao invés de `Collections.emptyList()`
- Tratamento genérico de exceções em alguns pontos (catch Exception)
- Falta de validações de entrada em alguns métodos
- Código de conversão de mensagem poderia ser mais robusto
- Configurações de timeout e nomes de filas poderiam estar externalizadas em properties

---

## 14. Observações Relevantes

1. **Ambiente de Desenvolvimento**: As configurações apontam para ambiente de desenvolvimento (qm_ata_des.bvnet.bv, usuário _spag_des)

2. **Framework Proprietário**: O sistema utiliza o BV Framework Batch, um framework proprietário do Banco Votorantim, o que pode dificultar manutenção por equipes externas

3. **Processamento Assíncrono**: O sistema trabalha com processamento assíncrono via filas, aguardando mensagens com timeout de 120 segundos (2 minutos)

4. **Dois Fluxos Distintos**: Existem dois jobs batch independentes:
   - Job principal: Relatório consolidado de pagamentos
   - Job callback-extrato: Extratos individualizados por cliente

5. **Controle de Status**: O sistema utiliza enums de StatusProcessamento (EM_ANDAMENTO, FINALIZADO, TODOS_FINALIZADOS, ERROR) para controlar o fluxo de processamento

6. **Arquivos Temporários**: Implementa estratégia de arquivos temporários com sufixo "-temp" para garantir atomicidade na geração dos relatórios

7. **Formato de Saída**: Todos os relatórios são gerados em formato CSV com separador ";" (ponto e vírgula)

8. **Versionamento**: Projeto na versão 0.7.0, indicando ainda estar em fase de desenvolvimento/estabilização

9. **Build e Deploy**: Utiliza Maven Assembly Plugin para gerar pacote ZIP distribuível com todas as dependências

10. **Execução**: Scripts .sh e .bat disponíveis para execução em ambientes Unix/Linux e Windows