# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sbatch-spag-base-integracao-contabil** é um sistema batch desenvolvido em Java com Spring Batch que realiza a integração contábil entre os sistemas SPAG (Sistema de Pagamentos), ITP (Sistema de Integração de Tesouraria e Pagamentos) e PGFT (Sistema de Gestão Financeira e Tesouraria). 

O sistema busca lançamentos confirmados no SPAG que ainda não foram integrados aos sistemas contábeis, realiza o mapeamento e transformação dos dados, insere os registros nas bases ITP e PGFT, e atualiza o status no SPAG. Também trata devoluções de boletos, tributos e concessionárias, vinculando-as aos lançamentos originais.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal que inicializa a aplicação Spring Batch |
| **BatchConfiguration** | Configura o Job principal de integração contábil |
| **StepConfiguration** | Define o Step do batch com reader, processor e writer |
| **IntegracaoContabilItemReader** | Lê lançamentos confirmados do SPAG pendentes de integração |
| **IntegracaoContabilItemProcessor** | Processa cada lançamento: verifica existência no ITP/PGFT, insere se necessário, trata devoluções |
| **IntegracaoContabilItemWriter** | Atualiza os lançamentos no SPAG com os protocolos ITP e códigos PGFT |
| **IntegracaoContabilService** | Serviço principal com lógica de negócio para integração |
| **JdbiSpagRepositoryImpl** | Repositório de acesso ao banco SPAG (SQL Server) |
| **JdbiSpbRepositoryImpl** | Repositório de acesso aos bancos ITP e PGFT (Sybase) |
| **CaixaEntradaSPBDTOMapper** | Mapeia LancamentoSpagDTO para CaixaEntradaSPBDTO (ITP) |
| **LancamentoPgftDTOMapper** | Mapeia LancamentoSpagDTO para LancamentoPgftDTO (PGFT) |
| **Helper** | Classe utilitária com funções auxiliares (limpeza de strings, conversões, validações) |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x**
- **Spring Batch** - Framework para processamento batch
- **Spring Cloud Task** - Gerenciamento de tarefas batch
- **JDBI 3.9.1** - Framework de acesso a dados SQL
- **SQL Server** (DBSPAG) - Banco de dados do sistema SPAG
- **Sybase ASE** (DBITP, DBPGF_TES) - Bancos de dados dos sistemas ITP e PGFT
- **Lombok** - Redução de código boilerplate
- **Logback** - Framework de logging
- **Docker** - Containerização da aplicação
- **Kubernetes** - Orquestração de containers (Jobs)
- **Maven** - Gerenciamento de dependências e build

---

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch que não expõe endpoints REST. A aplicação é executada como um Job Kubernetes agendado.

---

## 5. Principais Regras de Negócio

1. **Seleção de Lançamentos**: Busca lançamentos no SPAG com status confirmado (3), sem protocolo ITP ou código PGFT, de tipos específicos de liquidação (DOC, TED, Boleto, Tributo, etc.), alterados nas últimas 24 horas.

2. **Preenchimento de Código Cliente (CdBuc)**: Identifica o código do cliente (BUC) para remetente e favorecido através de consulta à base DBGLOBAL, relacionando banco, conta e tipo de relacionamento.

3. **Inserção no ITP**: Se o lançamento não existir no ITP, cria registro na tabela TBL_CAIXA_ENTRADA_SPB com status pré-confirmado.

4. **Geração de Sequencial PGFT**: Obtém sequencial disponível através da procedure prObterSequencialDisponivel para gerar o código do lançamento PGFT.

5. **Inserção no PGFT**: Se o lançamento não existir no PGFT, cria registro na tabela TBL_LANCAMENTO com status confirmado (1).

6. **Tratamento de Devoluções**: Para transações de devolução de boleto (8408), tributo (8680) e concessionária (8678), localiza o lançamento original e atualiza campos de devolução no PGFT.

7. **Normalização de Dados**: Remove caracteres especiais de nomes e endereços, valida tipos de conta, formata valores monetários com 2 casas decimais.

8. **Tratamento de Cliente Fintech**: Identifica e processa separadamente dados de clientes fintech (remetente e favorecido).

9. **Geração de Linha Digitável**: Converte código de barras em linha digitável para boletos.

10. **Skip de Erros**: Configurado para pular até 100 registros com erro, registrando em log através do BatchSkipListener.

---

## 6. Relação entre Entidades

**LancamentoSpagDTO** (origem - SPAG)
- Contém todos os dados do lançamento financeiro
- Relaciona-se com dados de Pessoa (remetente/favorecido)
- Relaciona-se com dados de Cliente Fintech (quando aplicável)

**CaixaEntradaSPBDTO** (destino - ITP)
- Mapeado a partir de LancamentoSpagDTO
- Representa entrada na caixa do SPB (Sistema de Pagamentos Brasileiro)
- Chave: Cod_Protocolo (gerado automaticamente)

**LancamentoPgftDTO** (destino - PGFT)
- Mapeado a partir de LancamentoSpagDTO
- Representa lançamento contábil na tesouraria
- Chave: Cod_Lancamento (obtido via sequencial)
- Relaciona-se com CaixaEntradaSPBDTO via Cod_Protocolo

**ClienteConta**
- Entidade auxiliar para identificação de código cliente (CdBuc)
- Relaciona conta bancária com código do cliente no sistema

**FavorecidoRemetenteConta**
- DTO para consulta de dados de conta de remetente e favorecido
- Usado para buscar código cliente (CdBuc)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBSPAG..TbLancamento | Tabela | SELECT | Lançamentos financeiros do sistema SPAG |
| DBSPAG..TbLancamentoPessoa | Tabela | SELECT | Dados de pessoas (remetente/favorecido) dos lançamentos |
| DBSPAG..TbLancamentoClienteFintech | Tabela | SELECT | Dados de clientes fintech relacionados aos lançamentos |
| DBITP..TBL_CAIXA_ENTRADA_SPB | Tabela | SELECT | Verifica existência de lançamento no ITP |
| DBPGF_TES..TBL_LANCAMENTO | Tabela | SELECT | Verifica existência de lançamento no PGFT e busca lançamentos origem para devoluções |
| DBGLOBAL..VwClienteContaCorrente | View | SELECT | Consulta dados de conta corrente de clientes |
| DBGLOBAL..TbDeParaLegado | Tabela | SELECT | Mapeamento entre código de pessoa e código BUC (cliente) |
| DBGLOBAL..TbBanco | Tabela | SELECT | Dados de bancos |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBSPAG..TbLancamento | Tabela | UPDATE | Atualiza NuProtocolo (ITP), CdLancamentoPGFT, CdBucRemetente e CdBucFavorecido |
| DBITP..TBL_CAIXA_ENTRADA_SPB | Tabela | INSERT | Insere novos lançamentos na caixa de entrada do ITP |
| DBPGF_TES..TBL_LANCAMENTO | Tabela | INSERT | Insere novos lançamentos contábeis no PGFT |
| DBPGF_TES..TBL_LANCAMENTO | Tabela | UPDATE | Atualiza campos de devolução (CdProtocoloDevolucao, Login_Devolucao, datas) |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | Leitura | /usr/etc/log (runtime) | Configuração de logging da aplicação |
| application.yml | Leitura | src/main/resources | Configurações da aplicação (datasources, profiles) |

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

---

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas.

---

## 12. Integrações Externas

| Sistema | Tipo | Descrição |
|---------|------|-----------|
| **SPAG (DBSPAG)** | Banco de Dados SQL Server | Sistema de origem dos lançamentos financeiros |
| **ITP (DBITP)** | Banco de Dados Sybase | Sistema de integração de tesouraria - destino dos lançamentos |
| **PGFT (DBPGF_TES)** | Banco de Dados Sybase | Sistema de gestão financeira e tesouraria - destino dos lançamentos contábeis |
| **DBGLOBAL** | Banco de Dados Sybase | Base global com dados de clientes, contas e bancos |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7,5/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com uso de padrões (Repository, Service, Mapper)
- Uso adequado de Spring Batch com configuração clara de Job, Step, Reader, Processor e Writer
- Implementação de tratamento de erros com skip listener
- Uso de JDBI para acesso a dados, facilitando manutenção de queries SQL
- Queries SQL externalizadas em arquivos separados
- Uso de Lombok para reduzir boilerplate
- Logging adequado com informações relevantes
- Configuração multi-ambiente (local, des, qa, uat, prd)

**Pontos de Melhoria:**
- Falta de documentação JavaDoc nas classes e métodos
- Mappers com métodos muito extensos (CaixaEntradaSPBDTOMapper e LancamentoPgftDTOMapper)
- Classe Helper com métodos estáticos genéricos que poderiam ser melhor organizados
- Ausência de testes unitários para as principais classes de negócio
- Algumas constantes "mágicas" no código (números de transação, códigos de status)
- Tratamento de exceções genérico em alguns pontos (catch Exception)
- Falta de validações mais robustas de entrada de dados
- Configuração de retry com limite 0 no Step (desabilitado)

O código é funcional e bem estruturado, mas poderia se beneficiar de melhor documentação, refatoração de métodos longos e maior cobertura de testes.

---

## 14. Observações Relevantes

1. **Execução como Job Kubernetes**: A aplicação é executada como um Job Kubernetes agendado, não como serviço contínuo.

2. **Processamento em Chunk**: Configurado para processar 1 registro por vez (chunk size = 1), o que pode impactar performance em grandes volumes.

3. **Isolamento de Transação**: Queries utilizam "AT ISOLATION 0" e hints "WITH (NOLOCK)" para evitar locks em leituras.

4. **Múltiplos Bancos de Dados**: Integra 3 sistemas diferentes (SPAG em SQL Server, ITP e PGFT em Sybase), exigindo configuração de múltiplos datasources.

5. **Janela de Processamento**: Processa apenas lançamentos alterados nas últimas 24 horas.

6. **Limite de Erros**: Configurado para pular até 100 registros com erro antes de falhar o job.

7. **Pré-confirmação**: Lançamentos são inseridos com status "pré-confirmado" no ITP e "confirmado" no PGFT.

8. **Tratamento Especial para Fintech**: Sistema identifica e processa separadamente dados de clientes fintech.

9. **Geração de Sequencial**: Utiliza procedure específica do PGFT para obter sequenciais de lançamento.

10. **Infraestrutura como Código**: Possui configurações completas de infraestrutura (Kubernetes, Docker) versionadas no repositório.