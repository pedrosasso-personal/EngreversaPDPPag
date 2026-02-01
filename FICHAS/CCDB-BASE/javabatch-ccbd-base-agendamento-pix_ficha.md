# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java responsável por processar agendamentos PIX do banco de dados CCBD. O sistema recupera lançamentos agendados para uma data específica, processa-os e publica mensagens em filas RabbitMQ para processamento posterior. Trata-se de um job batch que executa em lote, lendo registros do banco SQL Server e enviando para fila de mensageria.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê lançamentos agendados do banco de dados para a data de processamento informada |
| **ItemProcessor** | Processa cada lançamento (atualmente apenas repassa o objeto sem transformações) |
| **ItemWriter** | Converte lançamentos em JSON e publica na fila RabbitMQ |
| **MyResumeStrategy** | Estratégia de retomada do job em caso de falha |
| **AgendamentoRepository** | Interface para acesso aos dados de agendamento |
| **AgendamentoRepositoryImpl** | Implementação do repositório usando JDBC Template |
| **LancamentoMapper** | Mapeia ResultSet do banco para objetos Lancamento |
| **Lancamento** | Value Object representando um lançamento/agendamento PIX |
| **Pessoa** | Value Object representando remetente ou favorecido |
| **AgendamentoUtil** | Utilitário para carregar queries SQL de arquivos XML |

## 3. Tecnologias Utilizadas

- **Java** (linguagem principal)
- **Maven** (gerenciamento de dependências e build)
- **Spring Framework** (IoC/DI, JDBC Template)
- **Spring AMQP / RabbitMQ** (mensageria)
- **BV Framework Batch** (framework proprietário para jobs batch)
- **Bitronix** (gerenciador de transações JTA)
- **SQL Server** (banco de dados - via driver JTDS)
- **Log4j** (logging)
- **Gson** (serialização JSON)
- **JUnit / Mockito** (testes)

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch que não expõe endpoints REST.

## 5. Principais Regras de Negócio

- Processa apenas agendamentos com status = 1 (status ativo/pendente)
- Filtra apenas lançamentos com código de liquidação = 63 (PIX)
- Limita a leitura a 500 registros por execução (TOP 500)
- Aceita parâmetro de data de processamento, caso não informado utiliza a data atual
- Converte lançamentos para formato JSON antes de enviar para fila
- Implementa controle de tentativas de liquidação (QtTentativaLiquidacao)
- Suporta diferentes ambientes (DES, UAT, PRD) com configurações específicas

## 6. Relação entre Entidades

**Lancamento** (entidade principal)
- Contém: idLancamento, codigoTransacao, codigoLiquidacao, codigoFinalidade, dataAgendamento, valorAgendado, nsu, etc.
- Relacionamento 1:1 com **Pessoa** (remetente)
- Relacionamento 1:1 com **Pessoa** (favorecido)

**Pessoa** (entidade de dados pessoais)
- Contém: codigoBanco, agencia, numeroConta, tipoConta, cpfCnpj, nome, tipoPessoa, chavePix, codigoISPB
- Pode representar tanto remetente quanto favorecido

**Relacionamento com Banco:**
- TbAgendamento (1) --- (1) TbPessoaAgendamento
- TbAgendamento (N) --- (1) TbStatusAgendamento

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| ccbdagendamento.TbAgendamento | Tabela | SELECT | Tabela principal de agendamentos PIX |
| ccbdagendamento.TbPessoaAgendamento | Tabela | SELECT | Dados de remetente e favorecido do agendamento |
| ccbdagendamento.TbStatusAgendamento | Tabela | SELECT | Descrição dos status de agendamento |

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema apenas realiza leitura de dados, não executa operações de INSERT, UPDATE ou DELETE.

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| AgendamentoRepositoryImpl-sql.xml | Leitura | AgendamentoUtil / AgendamentoRepositoryImpl | Arquivo XML contendo queries SQL parametrizadas |
| job-resources.xml | Leitura | Spring Context | Configuração de recursos (datasource, RabbitMQ) por ambiente |
| job-definitions.xml | Leitura | Spring Context | Definição do job batch, beans e metadados |
| log4j.xml | Leitura | Log4j | Configuração de logging |
| statistics-{executionId}.log | Gravação | BvDailyRollingFileAppender | Log de estatísticas de execução do job |

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Responsável | Descrição |
|--------------|------------|-------------------|-----------|
| ex.ccbd.agendamento (exchange) com routing key "pix" | RabbitMQ | ItemWriter | Publica lançamentos PIX em formato JSON para processamento posterior |

**Configurações por ambiente:**
- **DES**: rabbit-ccbd-base-lb.appdes.bvnet.bv:5672 (usuário: _ccbd_des)
- **UAT**: rabbit-ccbd-base-lb.appuat.bvnet.bv:5672 (usuário: _ccbd_uat)
- **PRD**: rabbit-ccbd-base-lb.app.bvnet.bv:5672 (usuário: _ccbd_prd)

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| SQL Server (DBCCBD) | Banco de Dados | Banco de dados principal contendo agendamentos PIX |
| RabbitMQ | Mensageria | Sistema de filas para publicação de lançamentos processados |

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades (Reader, Processor, Writer)
- Uso adequado de padrões batch (framework BV)
- Configuração externalizada por ambiente
- Uso de logging apropriado
- Mapeamento de objetos bem estruturado

**Pontos Negativos:**
- ItemProcessor não realiza nenhum processamento real (apenas repassa o objeto)
- Falta tratamento de exceções mais granular
- Código de saída hardcoded (10, 20) sem constantes
- Falta validação de dados antes de enviar para fila
- Ausência de documentação JavaDoc
- Query SQL embutida em XML (dificulta manutenção)
- Limite fixo de 500 registros pode causar problemas de escalabilidade
- Falta de testes unitários para classes críticas (apenas testes básicos)
- Senhas em texto claro nos arquivos de configuração (DES)
- Uso de tipos primitivos misturados com wrappers (Integer vs int)

## 14. Observações Relevantes

- O sistema utiliza framework proprietário BV (bv-framework-batch) que encapsula funcionalidades batch
- Existe suporte a retomada de execução através de MyResumeStrategy
- O parâmetro "dataProcessamento" é obrigatório mas tem fallback para data atual
- Códigos de saída definidos: 0 (OK), 10 (erro leitura BD), 20 (erro publicação fila)
- Sistema preparado para múltiplos ambientes com configurações específicas
- Utiliza transações locais (allowLocalTransactions=true)
- Pool de conexões configurado: min=1, max=10
- O ItemProcessor está implementado mas não realiza transformações, sugerindo possível expansão futura
- Versão do projeto: 0.6.0 (indica que ainda está em desenvolvimento/evolução)