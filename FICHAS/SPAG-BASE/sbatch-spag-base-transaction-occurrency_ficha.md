# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sbatch-spag-base-transaction-occurrency** é uma aplicação Spring Batch desenvolvida para processar devoluções de transações financeiras (ocorrências de transação). O sistema consulta ocorrências de transações via API externa (Celcoin), identifica transações que necessitam devolução e executa o processo de estorno/devolução tanto para o Banco Votorantim (BV - código 655) quanto para o Banco BV S.A. (BVSA - código 413). O processamento é executado em lote (batch) e integra-se com múltiplos bancos de dados (SQL Server e Sybase) e APIs REST para orquestração de transferências.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal que inicializa a aplicação Spring Batch |
| `BatchConfiguration` | Configura o Job principal com dois steps (BV e BVSA) |
| `StepConfiguration` | Define os steps do batch com reader, processor e writer |
| `TransactionOccurrencyBVItemReader` | Lê ocorrências de transações do Banco BV via API Celcoin |
| `TransactionOccurrencyBVSAItemReader` | Lê ocorrências de transações do Banco BVSA via API Celcoin |
| `TransactionOccurrencyItemProcessor` | Processa cada ocorrência, buscando dados da transação original |
| `TransactionOccurrencyItemWriter` | Executa a devolução das transações processadas |
| `TransactionOccurrencyService` | Serviço de domínio que orquestra a lógica de devolução |
| `JdbiTransactionRepositoryImpl` | Repositório para operações no banco SPAG (SQL Server) |
| `JdbiPgftTransactionRepositoryImpl` | Repositório para operações no banco ITP/PGFT (Sybase) |
| `HttpTransferenciaRepositoryImpl` | Cliente HTTP para integração com orquestrador de transferências |
| `TransactionOccurrencyRepositoryImpl` | Cliente HTTP para consulta de ocorrências na API Celcoin |
| `PaymentTransactionMapper` | Mapeia transações originais para transações de devolução |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x**
- **Spring Batch** - Framework de processamento em lote
- **Spring Cloud Task** - Gerenciamento de tarefas batch
- **JDBI 3.9.1** - Framework de acesso a dados SQL
- **SQL Server** (driver mssql-jdbc 7.4.0) - Banco de dados SPAG
- **Sybase jConnect 16.3** - Banco de dados ITP/PGFT
- **RestTemplate** - Cliente HTTP para integrações REST
- **Lombok** - Redução de boilerplate
- **Logback** - Framework de logging
- **JUnit 5 + Mockito** - Testes unitários
- **Docker** - Containerização
- **Kubernetes** - Orquestração (configurações presentes)
- **Maven** - Gerenciamento de dependências

---

## 4. Principais Endpoints REST

Este é um sistema batch que **não expõe endpoints REST próprios**. Ele **consome** endpoints externos:

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `{APIGEE_URL}/transaction-occurency/v1/transactions/{bank}?startDate={begin}&endDate={end}` | Consulta ocorrências de transações na API Celcoin |
| GET | `{APIGEE_URL}/transaction-occurency/v1/transactions/{bank}/authorize` | Obtém token de autenticação para API Celcoin |
| POST | `{SPAG_BASE_TRANSFERENCIAS_ENDPOINT}/v1/transferencia` | Executa transferência via orquestrador (para devoluções BVSA) |

---

## 5. Principais Regras de Negócio

1. **Processamento por Banco**: O batch executa dois steps separados, um para BV (655) e outro para BVSA (413)
2. **Consulta de Ocorrências**: Busca transações com ocorrências no dia anterior (ou desde sexta-feira se for segunda-feira)
3. **Identificação de Transações**: Localiza transações originais no banco SPAG usando código de autenticação bancária
4. **Validação de Devolução**: Apenas processa transações com liquidação CS (60) ou TB (59) que estejam lançadas em conta corrente e sem devolução prévia
5. **Devolução BV (655)**: Cria lançamento no SPAG, depois no ITP, atualiza lançamento original no PGFT e ITP, e confirma no SPAG
6. **Devolução BVSA (413)**: Chama API de orquestração de transferências e atualiza lançamento original no SPAG
7. **Mapeamento de Contas**: Utiliza contas específicas configuradas para BV e BVSA como remetentes da devolução
8. **Tratamento de Erros**: Transações com erro são logadas e serão reprocessadas na próxima execução
9. **Normalização de Dados**: Remove caracteres especiais de nomes e formata agências com 4 dígitos

---

## 6. Relação entre Entidades

**Principais Entidades:**

- **TransactionOccurrency**: Representa uma ocorrência de transação retornada pela API Celcoin
  - Atributos: date, createDate, descriptionMotivo, externalNSU, transactionId, value
  
- **PaymentTransaction**: Representa uma transação de pagamento completa
  - Relacionamentos:
    - `remetente` (Participant): Participante remetente
    - `favorecido` (Participant): Participante favorecido
    - `remetenteFintech` (Participant): Remetente fintech (opcional)
    - `favorecidoFintech` (Participant): Favorecido fintech (opcional)
  
- **Participant**: Representa um participante da transação (pessoa física/jurídica)
  - Atributos: tipoPessoa, numeroCpfCnpj, nome, numeroBanco, numeroAgencia, numeroConta, tipoConta

- **TransferRepresentation**: Representação de transferência para API de orquestração

**Fluxo de Relacionamento:**
1. TransactionOccurrency → busca PaymentTransaction original
2. PaymentTransaction original → mapeada para PaymentTransaction de devolução (inversão de remetente/favorecido)
3. PaymentTransaction devolução → persistida nos bancos ou enviada via API

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View | Tipo | Operação | Breve Descrição |
|---------------------|------|----------|-----------------|
| TbLancamento | Tabela | SELECT | Tabela principal de lançamentos no SPAG (SQL Server) |
| TbLancamentoPessoa | Tabela | SELECT | Dados de pessoas (remetente/favorecido) dos lançamentos |
| TbLancamentoClienteFintech | Tabela | SELECT | Dados de clientes fintech relacionados aos lançamentos |
| TbControleMigracaoParticipante | Tabela | SELECT | Controle de migração de participantes |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View | Tipo | Operação | Breve Descrição |
|---------------------|------|----------|-----------------|
| TbLancamento (SPAG) | Tabela | INSERT | Insere novo lançamento de devolução via procedure `PrIncluirLancamentoV2` |
| TbLancamento (SPAG) | Tabela | UPDATE | Atualiza lançamento original com código de devolução (`updateFromReversal`) |
| TbLancamento (SPAG) | Tabela | UPDATE | Confirma devolução atualizando status e protocolo (`confirmFromReversal`) |
| TBL_CAIXA_ENTRADA_SPB (ITP) | Tabela | INSERT | Insere lançamento de devolução no ITP via procedure `PrIncluirCaixaEntProtCliCtrl` |
| TBL_CAIXA_ENTRADA_SPB (ITP) | Tabela | UPDATE | Atualiza protocolo de devolução no ITP |
| tbl_lancamento (PGFT) | Tabela | UPDATE | Atualiza protocolo de devolução no PGFT (Sybase) |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | Leitura | Configuração de logging | Arquivo de configuração do Logback para diferentes ambientes |
| application.yml | Leitura | Configuração Spring | Configurações da aplicação para diferentes profiles (local, des, qa, uat, prd) |
| *.sql (resources) | Leitura | JDBI SqlLocator | Arquivos SQL para queries e procedures executadas via JDBI |

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

---

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas.

---

## 12. Integrações Externas

| Sistema/API | Tipo | Descrição |
|-------------|------|-----------|
| API Celcoin (Transaction Occurency) | REST | Consulta ocorrências de transações para BV e BVSA, obtém token de autenticação |
| Orquestrador de Transferências SPAG | REST | Executa transferências de devolução para transações BVSA (413) |
| Gateway OAuth | REST | Serviço de autenticação para obtenção de tokens JWT (via `GatewayOAuthService`) |
| Banco SPAG (SQL Server) | JDBC | Banco de dados principal para lançamentos e controle de transações |
| Banco ITP/PGFT (Sybase) | JDBC | Banco de dados legado para registro de transações no sistema ITP |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com uso de padrões (ports/adapters, mappers, services)
- Uso adequado de Spring Batch com configuração clara de steps
- Testes unitários presentes com boa cobertura de cenários
- Uso de Lombok reduzindo boilerplate
- Configurações externalizadas por ambiente
- Logging estruturado com JSON

**Pontos de Melhoria:**
- Tratamento de exceções genérico em alguns pontos (catch Exception sem especificidade)
- Lógica de negócio complexa concentrada em `TransactionOccurrencyService.reversalPayment655` poderia ser refatorada
- Comentários em código misturando português e inglês
- Alguns métodos longos que poderiam ser quebrados em métodos menores
- Falta de validações mais robustas em alguns fluxos
- Código comentado presente (ex: linha 161 em `PaymentTransactionMapper`)
- Uso de `lenient()` em testes indica possível problema de design nos testes

---

## 14. Observações Relevantes

1. **Execução Agendada**: O batch é executado via Kubernetes Job, recebendo parâmetro `dataOcorrencia` (formato yyyyMMdd)

2. **Processamento Assíncrono**: Cada step processa um banco diferente, mas de forma sequencial (stepBV → stepBVSA)

3. **Resiliência**: Transações com erro não interrompem o processamento e serão reprocessadas na próxima execução

4. **Múltiplos Bancos de Dados**: Integração simultânea com SQL Server (SPAG) e Sybase (ITP/PGFT) usando JDBI

5. **Segurança**: Utiliza OAuth2 JWT para autenticação nas APIs externas via Gateway

6. **Ambientes**: Configurado para múltiplos ambientes (local, des, qa, uat, prd) com parâmetros específicos

7. **Containerização**: Preparado para execução em containers Docker e orquestração Kubernetes

8. **Auditoria**: Integração com framework de auditoria BV (`arqt-base-trilha-auditoria-web`)

9. **Normalização**: Implementa normalização de caracteres especiais para compatibilidade com sistemas legados

10. **Códigos de Banco**: Trata códigos 655 (BV), 161 (BV legado) e 413 (BVSA) com lógicas específicas para cada instituição