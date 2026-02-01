# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-ccbd-base-consome-fila-stand-in** é um serviço atômico Spring Boot desenvolvido para processar transações de cartão de débito em modo Stand-In (contingência). O sistema consome mensagens de uma fila IBM MQ contendo transações de cartão, valida saldo em conta corrente, realiza bloqueio de saldo e registra as transações em bancos de dados SQL Server (CCBD) e Sybase (Conta Corrente). Também oferece um endpoint REST para gerenciamento de cache de transações.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal que inicializa a aplicação Spring Boot |
| `DebConsomeFilaStandInListener` | Listener JMS que consome mensagens da fila de transações Stand-In |
| `DebConsomeFilaStandInService` | Serviço principal que orquestra o processamento de transações |
| `CacheService` | Gerencia operações de cache de transações |
| `CacheController` | Controller REST para operações de cache |
| `ContaCorrenteRepositoryImpl` | Repositório para operações no banco Sybase (Conta Corrente) |
| `CCBDRepositoryImpl` | Repositório para operações no banco SQL Server (CCBD) |
| `CacheRepositoryImpl` | Repositório para operações de cache no banco CCBD |
| `ConfigurationListener` | Configuração do listener JMS e conversores de mensagem |
| `DataSourceConfiguration` | Configuração dos datasources Sybase e SQL Server |
| `JDBIConfiguration` | Configuração do framework JDBI para acesso a dados |
| `MappingMessageLocalConverter` | Conversor customizado de mensagens JMS com tratamento de erros |
| `TransactionValidatorUtil` | Utilitário para validação de campos obrigatórios de transações |
| `MapperUtil` | Utilitário para mapeamento entre objetos de domínio e entidades |

---

## 3. Tecnologias Utilizadas

- **Framework:** Spring Boot 2.x
- **Linguagem:** Java 11
- **Mensageria:** IBM MQ (JMS)
- **Bancos de Dados:** 
  - SQL Server (DBCCBD)
  - Sybase (DBCONTACORRENTE)
- **Acesso a Dados:** JDBI 3.9.1
- **Documentação API:** Swagger/OpenAPI 2.9.2
- **Monitoramento:** Spring Actuator, Micrometer, Prometheus
- **Auditoria:** springboot-arqt-base-trilha-auditoria (2.2.1)
- **Build:** Maven
- **Containerização:** Docker
- **Orquestração:** OpenShift (OCP)
- **Testes:** JUnit 5, Mockito, Rest Assured, Pact

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/transacao-cache/inserir` | `CacheController` | Insere uma transação no cache para processamento Stand-In |

---

## 5. Principais Regras de Negócio

1. **Validação de NCC (Núcleo de Conta Corrente):** Verifica se o sistema de conta corrente está disponível antes de processar transações
2. **Validação de Campos Obrigatórios:** Valida presença de campos essenciais da transação (identificador, conta, agência, valor, NSU, cartão, estabelecimento)
3. **Verificação de Duplicidade:** Impede processamento de transações já existentes no sistema
4. **Validação de Saldo:** Verifica se a conta possui saldo disponível suficiente (saldo total + limite - bloqueios - indisponível)
5. **Bloqueio de Saldo:** Realiza bloqueio preventivo do valor da transação (valor + IOF) na conta corrente
6. **Tratamento de Transações Não Autorizadas:** Registra transações reprovadas por saldo insuficiente com status específico (V4)
7. **Gerenciamento de Cache:** Remove transações do cache após processamento bem-sucedido
8. **Cálculo de IOF:** Considera IOF nas operações, com valor padrão zero se não informado
9. **Mapeamento de Códigos:** Converte códigos de sistema origem (DXC) e tipo de transação (0200=Aprovada, 0400=Estorno)
10. **Data de Movimento:** Define data atual se não informada na transação

---

## 6. Relação entre Entidades

**Entidades de Domínio:**
- `Transacao`: Entidade principal contendo dados da transação de cartão
  - Relacionamento 1:1 com `Cartao`
  - Relacionamento 1:1 com `Estabelecimento`
- `Cartao`: Dados do cartão utilizado na transação
- `Estabelecimento`: Dados do estabelecimento comercial
- `Cache`: Entidade para controle de cache de transações

**Entidades de Persistência:**
- `InsertTransactionEntity`: Dados para inserção na tabela de controle de transações
- `InsertCardTransactionEntity`: Dados do cartão para persistência
- `InsertCommercialPlaceEntity`: Dados do estabelecimento para persistência
- `InsertBlockBalanceEntity`: Dados para bloqueio de saldo
- `InsertCacheTransactionEntity`: Dados para cache de transações

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| `TbConta` | Tabela (Sybase) | SELECT | Consulta saldo disponível e sequência de bloqueio |
| `TbControleData` | Tabela (Sybase) | SELECT | Verifica se NCC aceita movimentação |
| `CCBDTransacaoCartaoDebito.TbControleTransacaoCartao` | Tabela (SQL Server) | SELECT | Verifica existência de transação pelo identificador |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| `TbConta` | Tabela (Sybase) | UPDATE | Atualiza valor de saldo bloqueado e sequência |
| `TbSaldoBloqueado` | Tabela (Sybase) | INSERT | Registra bloqueio de saldo da transação |
| `CCBDTransacaoCartaoDebito.TbControleTransacaoCartao` | Tabela (SQL Server) | INSERT | Insere registro de transação autorizada ou não autorizada |
| `CCBDTransacaoCartaoDebito.TbTransacaoCartao` | Tabela (SQL Server) | INSERT | Insere dados do cartão da transação |
| `CCBDTransacaoCartaoDebito.TbEstabelecimentoComercial` | Tabela (SQL Server) | INSERT | Insere dados do estabelecimento comercial |
| `CCBDTransacaoCartaoDebito.TbProcessamentoContaStandIn` | Tabela (SQL Server) | INSERT | Insere transação no cache |
| `CCBDTransacaoCartaoDebito.TbProcessamentoContaStandIn` | Tabela (SQL Server) | DELETE | Remove transação do cache após processamento |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `application.yml` | Leitura | Spring Boot | Configurações da aplicação (datasources, filas, profiles) |
| `logback-spring.xml` | Leitura | Logback | Configuração de logs da aplicação |
| `*.sql` | Leitura | JDBI/Repositórios | Queries SQL para operações de banco de dados |
| `sboot-ccbd-base-deb-consome-fila-stand-in.yaml` | Leitura | Swagger | Especificação OpenAPI da API REST |

---

## 10. Filas Lidas

- **Fila:** `QL.CCBD_PROC_TRANSAC_STAND_IN.INT`
- **Queue Manager:** `QM.DIG.01`
- **Canal:** `CCBD.SRVCONN`
- **Tecnologia:** IBM MQ
- **Listener:** `DebConsomeFilaStandInListener`
- **Descrição:** Consome mensagens contendo transações de cartão de débito em modo Stand-In para processamento

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| IBM MQ | Mensageria | Consumo de mensagens de transações Stand-In |
| SQL Server (DBCCBD) | Banco de Dados | Persistência de transações de cartão de débito |
| Sybase (DBCONTACORRENTE) | Banco de Dados | Consulta e atualização de saldo em conta corrente |
| Prometheus | Monitoramento | Exportação de métricas da aplicação |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com módulos domain e application
- Uso adequado de padrões Spring Boot e injeção de dependências
- Cobertura de testes unitários presente
- Uso de JDBI com SQL externalizado facilita manutenção
- Tratamento de exceções customizadas
- Configuração adequada de múltiplos datasources
- Uso de Lombok reduz boilerplate

**Pontos de Melhoria:**
- Lógica de negócio concentrada em `DebConsomeFilaStandInService.makeTransaction()` (método muito extenso)
- Falta de transações distribuídas entre Sybase e SQL Server (risco de inconsistência)
- Tratamento de erro no `MappingMessageLocalConverter` retorna objeto vazio ao invés de rejeitar mensagem
- Valores hardcoded em vários pontos (ex: códigos de usuário = 1, códigos de motivo)
- Falta de documentação JavaDoc nas classes principais
- Alguns métodos utilitários poderiam ser mais testados
- Configuração de segurança básica (Basic Auth) pode ser insuficiente para produção

---

## 14. Observações Relevantes

1. **Modo Stand-In:** O sistema opera em modo de contingência quando o sistema principal de autorização está indisponível
2. **Múltiplos Bancos:** Utiliza dois bancos de dados distintos (Sybase para conta corrente, SQL Server para CCBD)
3. **Profiles:** Suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas
4. **Auditoria:** Integrado com framework de trilha de auditoria do Banco Votorantim
5. **Containerização:** Preparado para deploy em OpenShift com configurações de infraestrutura como código
6. **Healthcheck:** Endpoints de health configurados para liveness e readiness probes
7. **Segurança:** Credenciais gerenciadas via cofre de senhas (variáveis de ambiente)
8. **Bloqueio Temporário:** Bloqueios de saldo têm vigência de 1000 dias a partir da data de movimento
9. **Códigos de Retorno:** Transações autorizadas recebem código 00, não autorizadas recebem V4
10. **Processamento Assíncrono:** Mensagens são processadas de forma assíncrona via JMS listener