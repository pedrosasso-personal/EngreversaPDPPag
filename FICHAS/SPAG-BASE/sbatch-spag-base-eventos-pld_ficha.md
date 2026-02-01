# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sbatch-spag-base-eventos-pld** é um sistema batch desenvolvido em Spring Boot para processamento de eventos relacionados a PLD (Prevenção à Lavagem de Dinheiro) e Open Finance. O sistema lê arquivos JSON contendo eventos de transações, cadastros, contas, cartões de crédito e contratos, processa esses eventos e persiste as informações no Google Cloud Firestore. Adicionalmente, publica mensagens em tópicos do Google Cloud Pub/Sub para integração com outros sistemas. Foi desenvolvido para atender requisitos regulatórios e carregar dados históricos de eventos.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal que inicializa a aplicação Spring Boot Batch |
| `JobConfig` | Configuração do job batch, definindo steps de leitura, processamento, escrita e movimentação de arquivos |
| `JsonStreamReader` | Lê eventos do arquivo JSON linha a linha |
| `Processor` | Processa cada evento lido, identificando seu tipo |
| `Writer` / `WriterService` | Grava os eventos processados no Firestore e publica no Pub/Sub |
| `OpfService` | Serviço principal para persistência de dados de Open Finance no Firestore |
| `BusinessService` | Serviço para persistência de dados de empresas (PJ) |
| `TransactionPldTempService` | Gerencia transações temporárias de PLD |
| `OPFMapper` | Mapeia eventos JSON para objetos de domínio de Open Finance |
| `GenericRepository` | Repositório genérico base para operações no Firestore |
| `OpfRepositoryFireStoreImpl` | Implementação do repositório para persistência de eventos OPF |
| `PubSubRepositoryImpl` | Implementação para publicação de mensagens no Google Pub/Sub |
| `FileServerImpl` | Gerencia operações de leitura/escrita em file server SMB |
| `MoverArquivoTasklet` | Tasklet responsável por mover arquivos processados |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.7.7** (framework principal)
- **Spring Batch** (processamento batch)
- **Google Cloud Firestore** (banco de dados NoSQL)
- **Google Cloud Pub/Sub** (mensageria)
- **Maven** (gerenciamento de dependências)
- **Lombok** (redução de código boilerplate)
- **Jackson** (serialização/deserialização JSON)
- **H2 Database** (banco em memória para metadados do Spring Batch)
- **JCIFS** (acesso a file server SMB/CIFS)
- **Logback** (logging em formato JSON)
- **ConfigCat** (feature toggle)
- **Docker** (containerização)
- **Swagger/OpenAPI** (documentação de API)

---

## 4. Principais Endpoints REST

Não se aplica. Este é um componente batch que não expõe endpoints REST para consumo externo. Possui apenas endpoints de monitoramento via Spring Actuator (health, metrics, prometheus) na porta 9090.

---

## 5. Principais Regras de Negócio

1. **Processamento de Eventos por Tipo**: Identifica e processa diferentes tipos de eventos (cadastro PF/PJ, transações, contas, cartões, contratos, faturas)
2. **Geração de Hash para Contas**: Gera identificador único (SHA3-256) para contas baseado em compeCode + branchCode + number
3. **TTL de Registros**: Aplica timestamp de expiração configurável (padrão 12 meses) para registros temporários
4. **Validação de Duplicidade**: Verifica existência de registros antes de inserir/atualizar
5. **Consolidação de Pagamentos**: Mescla pagamentos de faturas de cartão evitando duplicidades
6. **Mapeamento de Status**: Converte status de eventos para padrões Open Finance (ATIVA, ENCERRADA, BLOQUEADA, etc)
7. **Classificação de Transações**: Classifica transações em tipos (TED, PIX, BOLETO, PAGAMENTO_CONTA, AUTORIZACAO)
8. **Tratamento de Crédito/Débito**: Identifica se transação é crédito ou débito baseado no tipo de evento
9. **Processamento Paralelo**: Utiliza ExecutorService com pool de threads para processamento concorrente
10. **Movimentação de Arquivos**: Move arquivos processados para diretório específico após conclusão

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **Registration (Cadastro PF)**: Contém dados pessoais, documentos, contatos e qualificação
  - Relaciona-se com `PersonalDocument`, `PersonalContacts`, `PersonalQualificationData`
  
- **Business (Cadastro PJ)**: Dados de empresas
  - Relaciona-se com `Owner` (sócios) e `LegalRepresentative` (representantes legais)

- **Account (Conta)**: Dados de contas bancárias
  - Relaciona-se com `Transaction` através de `accountId`

- **Transaction (Transação)**: Movimentações financeiras
  - Referencia `Account` através de `accountId`
  - Possui `TransactionAmount` e dados da parte envolvida

- **CreditContract (Contrato de Crédito)**: Contratos de crédito
  - Relaciona-se com `CreditCard` através de `contractNumber`

- **CreditCard (Cartão de Crédito)**: Dados de cartões
  - Relaciona-se com `CreditContract`, `CreditBill` e `CreditTransaction`

- **CreditBill (Fatura)**: Faturas de cartão
  - Contém lista de `PaymentBill` (pagamentos)
  - Relaciona-se com `CreditTransaction`

- **CreditTransaction (Transação de Crédito)**: Transações de cartão de crédito
  - Relaciona-se com `CreditBill` através de `billId`

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| `transactionsV2` | coleção Firestore | SELECT/READ | Transações financeiras consolidadas |
| `transactionsTempV2` | coleção Firestore | SELECT/READ | Transações temporárias em processamento |
| `transactionPldTempV2` | coleção Firestore | SELECT/READ | Transações temporárias específicas de PLD |
| `accounts` | coleção Firestore | SELECT/READ | Contas bancárias |
| `accountsTemp` | coleção Firestore | SELECT/READ | Contas temporárias em processamento |
| `customers` | coleção Firestore | SELECT/READ | Cadastros de clientes pessoa física |
| `legalRepresentatives` | coleção Firestore | SELECT/READ | Representantes legais de empresas |
| `owners` | coleção Firestore | SELECT/READ | Sócios/proprietários de empresas |
| `business` | coleção Firestore | SELECT/READ | Cadastros de empresas (PJ) |
| `creditContracts` | coleção Firestore | SELECT/READ | Contratos de crédito |
| `creditCards` | coleção Firestore | SELECT/READ | Cartões de crédito |
| `creditTransactionsV2` | coleção Firestore | SELECT/READ | Transações de cartão de crédito |
| `creditBillsV2` | coleção Firestore | SELECT/READ | Faturas de cartão de crédito |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| `transactionsV2` | coleção Firestore | INSERT/UPDATE | Inserção e atualização de transações |
| `transactionsTempV2` | coleção Firestore | INSERT/UPDATE | Inserção de transações temporárias |
| `transactionPldTempV2` | coleção Firestore | INSERT/UPDATE | Inserção de transações PLD temporárias |
| `accounts` | coleção Firestore | INSERT/UPDATE | Inserção e atualização de contas |
| `accountsTemp` | coleção Firestore | INSERT/UPDATE | Inserção de contas temporárias |
| `customers` | coleção Firestore | INSERT/UPDATE | Inserção e atualização de cadastros PF |
| `legalRepresentatives` | coleção Firestore | INSERT/UPDATE | Inserção de representantes legais |
| `owners` | coleção Firestore | INSERT/UPDATE | Inserção de sócios/proprietários |
| `business` | coleção Firestore | INSERT/UPDATE | Inserção e atualização de cadastros PJ |
| `creditContracts` | coleção Firestore | INSERT/UPDATE | Inserção de contratos de crédito |
| `creditCards` | coleção Firestore | INSERT/UPDATE | Inserção e atualização de cartões |
| `creditTransactionsV2` | coleção Firestore | INSERT/UPDATE | Inserção de transações de crédito |
| `creditBillsV2` | coleção Firestore | INSERT/UPDATE | Inserção e atualização de faturas |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `template_eventos.json` | Leitura | `JsonStreamReader` / `ArquivoJobUtil` | Arquivo JSON contendo eventos a serem processados |
| Arquivos de entrada (*.json) | Leitura | `FileServerImpl` / `ArquivoJobUtil` | Arquivos de eventos lidos do file server SMB |
| Arquivos processados | Gravação/Movimentação | `MoverArquivoTasklet` / `FileServerImpl` | Arquivos movidos para diretório de processados após conclusão |
| `logback-spring.xml` | Leitura | Logback | Configuração de logs em formato JSON |

**Diretórios configuráveis:**
- Entrada: `${FILESERVER}${DIRETORIO_ARQUIVOS}/entrada/`
- Processamento: `${FILESERVER}${DIRETORIO_ARQUIVOS}/entrada/temp/`
- Processado: `${FILESERVER}${DIRETORIO_ARQUIVOS}/entrada/processado/`
- Rejeitado: `${FILESERVER}${DIRETORIO_ARQUIVOS}/entrada/rejeitado/`

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas, apenas publica.

---

## 11. Filas Geradas

| Nome da Fila/Tópico | Tecnologia | Classe Responsável | Descrição |
|---------------------|------------|-------------------|-----------|
| `business-spag-base-ingestao-dados-parceiro` | Google Cloud Pub/Sub | `PubSubRepositoryImpl` | Tópico para ingestão de dados de parceiros (transações e cadastros) |

**Filtros aplicados nas mensagens:**
- Para transações: `filter=business-spag-base-ingestao-dados-parceiro-transacao-sub`
- Para cadastros: `filter=business-spag-base-ingestao-dados-parceiro-cadastro-sub`
- Atributos adicionais: `entityId`, `companyKey`

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Google Cloud Firestore | Banco NoSQL | Persistência de dados de Open Finance e PLD |
| Google Cloud Pub/Sub | Mensageria | Publicação de eventos processados |
| File Server SMB/CIFS | Storage | Leitura de arquivos de entrada via protocolo SMB (//pta-appsdes.bvnet.bv) |
| ConfigCat | Feature Toggle | Gerenciamento de configurações dinâmicas (TTL de coleções) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com uso de camadas (domain, repository, service, mapper)
- Uso adequado de padrões como Repository, Service e Mapper
- Tratamento de exceções customizado com enums específicos
- Uso de Lombok reduzindo boilerplate
- Configuração externalizada e profiles para diferentes ambientes
- Logs estruturados em JSON
- Uso de feature toggle para configurações dinâmicas
- Processamento paralelo com ExecutorService

**Pontos de Melhoria:**
- Código com muitos comentários desabilitados e código morto
- Classes muito extensas (OPFMapper, WriterService) com múltiplas responsabilidades
- Métodos estáticos em mappers dificultam testes e manutenção
- Uso excessivo de strings literais sem constantes em alguns pontos
- Lógica de negócio complexa em mappers (deveria estar em services)
- Falta de documentação JavaDoc em métodos críticos
- Tratamento genérico de exceções em alguns pontos (catch Exception)
- Variáveis estáticas públicas para contadores (WriterService, JsonStreamReader) não são thread-safe
- Mistura de responsabilidades (mapeamento + lógica de negócio + validação)

---

## 14. Observações Relevantes

1. **Arquitetura Híbrida**: O sistema combina funcionalidades de dois serviços anteriores (sboot-spag-base-orch-pld-service e sboot-spag-base-atom-opf-service) para atender requisitos regulatórios urgentes.

2. **Processamento em Lote**: Configurado com chunk size de 10.000 registros para otimização de performance.

3. **Ambientes**: Suporta múltiplos ambientes (local, des, uat, prd) com configurações específicas via profiles Spring.

4. **Segurança**: Utiliza autenticação NTLM para acesso ao file server e JWT para APIs (quando aplicável).

5. **Monitoramento**: Expõe métricas via Actuator e Prometheus na porta 9090.

6. **TTL Configurável**: Tempo de vida dos registros no Firestore é configurável via feature toggle (padrão 12 meses).

7. **Tipos de Eventos Suportados**:
   - Cadastro PF: CUSTOMER_WAS_RECEIVED, CUSTOMER_WAS_APPROVED, etc.
   - Cadastro PJ: BUSINESS_WAS_APPROVED, BUSINESS_WAS_RECEIVED, etc.
   - Contas: ACCOUNT_WAS_CREATED, ACCOUNT_WAS_CLOSED, etc.
   - Transações: PIX, TED, BOLETO, PAGAMENTO_CONTA, AUTORIZACAO
   - Cartões: CARD_WAS_ISSUED, CARD_STATUS_WAS_MODIFIED, etc.
   - Contratos: CREDIT_CARD_CONTRACT_ACCEPTED, etc.
   - Faturas: INVOICE_CLOSED, INVOICE_PAYMENT_PROCESSED

8. **Execução**: O job é executado via linha de comando passando o nome do arquivo como parâmetro.

9. **Logs Estruturados**: Todos os logs são gerados em formato JSON para facilitar análise e monitoramento.

10. **Tratamento de Erros**: Sistema registra contadores de eventos lidos, processados com sucesso e com erro, disponibilizando métricas ao final da execução.