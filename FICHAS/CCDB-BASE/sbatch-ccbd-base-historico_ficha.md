# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sbatch-ccbd-base-historico** é um sistema batch desenvolvido em Java com Spring Batch, responsável pela consolidação e movimentação diária de dados históricos de contas correntes. O sistema realiza a migração de dados de tabelas operacionais para tabelas de histórico, incluindo movimentações, saldos indisponíveis, saldos bloqueados, avisos de lançamento e limites de conta corrente. A execução ocorre de forma paralela através de múltiplos flows, otimizando o processamento de grandes volumes de dados.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `SpringBatchApplication` | Classe principal que inicializa a aplicação Spring Batch |
| `BatchConfiguration` | Configuração principal do job, orquestrando os flows paralelos |
| `HistoricoMovimentosWriter` | Grava movimentações no histórico e remove da tabela operacional |
| `HistoricoSaldoIndisponivelWriter` | Processa saldos indisponíveis para histórico |
| `AvisoLancamentoWriter` | Remove avisos de lançamento antigos |
| `HistoricoLimiteContaCorrenteWriter` | Migra limites de conta corrente para histórico |
| `SaldoBloqueadoParaHistoricoSaldoBloqueadoWriter` | Movimenta saldos bloqueados para histórico |
| `JdbiMovimentoContaRepository` | Interface de acesso a dados de movimentações usando JDBI |
| `JdbiSaldoIndisponivelContaRepository` | Interface de acesso a dados de saldo indisponível |
| `AppProperties` | Configurações da aplicação (chunk size, paginação, thread pool) |
| `StepUtils` | Utilitários para manipulação de contexto de steps |
| `DateUtils` | Utilitários para manipulação de datas |
| `JobUtils` | Utilitários para manipulação de contexto de jobs |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x**
- **Spring Batch** - Framework para processamento batch
- **Spring Cloud Task** - Gerenciamento de tarefas
- **JDBI 3.9.1** - Framework de acesso a dados
- **Sybase jConnect 16.3** - Driver de conexão com banco Sybase
- **Logback** - Framework de logging
- **Lombok** - Redução de código boilerplate
- **Docker** - Containerização
- **Kubernetes** - Orquestração (deploy via Job)
- **Maven** - Gerenciamento de dependências
- **JUnit 5 + Mockito** - Testes unitários
- **HikariCP** - Pool de conexões

---

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch sem endpoints REST expostos. A aplicação possui apenas endpoints do Spring Actuator para monitoramento:
- `/actuator/health`
- `/actuator/metrics/*`
- `/actuator/prometheus`

---

## 5. Principais Regras de Negócio

1. **Movimentação de Histórico**: Dados são movidos de tabelas operacionais para tabelas de histórico com base na data de execução do job
2. **Processamento em Lote (Chunk)**: Dados são processados em chunks configuráveis para otimização de performance
3. **Paginação de Movimentos**: Movimentações são processadas em páginas para evitar sobrecarga de memória
4. **Execução Paralela**: Cinco flows são executados em paralelo usando ThreadPoolTaskExecutor
5. **Tolerância a Falhas**: Sistema configurado com `faultTolerant()` e `skip(SQLException.class)` para continuar processamento em caso de erros pontuais
6. **Zeragem de Hora**: Data de execução tem hora zerada para comparações consistentes
7. **Remoção Condicional**: Registros só são removidos após confirmação de gravação no histórico
8. **Filtro por Data**: Apenas registros anteriores à data de execução são processados
9. **Validação de Duplicidade**: Verificação com LEFT JOIN para evitar duplicação de registros no histórico
10. **Saldo Bloqueado**: Movimenta registros com motivo de desbloqueio ou com data de fim de vigência anterior à execução

---

## 6. Relação entre Entidades

**Entidades principais:**

- **MovimentoContaRange**: Representa um range de movimentações (sequência inicial e final) de uma conta
  - Atributos: cdBanco, nuContaCorrente, cdTipoConta, sqInicial, sqFinal

- **SaldoIndisponivelConta**: Representa saldo indisponível de uma conta
  - Atributos: cdBanco, nuContaCorrente, cdTipoConta

- **AvisoLancamentoConta**: Representa avisos de lançamento de uma conta
  - Atributos: cdBanco, nuContaCorrente, cdTipoConta

- **LimiteContaCorrente**: Representa limites de conta corrente
  - Atributos: cdBanco, nuContaCorrente, cdTipoConta

- **SaldoBloqueadoConta**: Representa saldos bloqueados com diversos atributos de controle
  - Atributos: cdBanco, nuContaCorrente, cdTipoConta, sqBloqueioSaldo, dtInicioVigenciaRegistro, cdMotivoBloqueio, cdMotivoDesbloqueio, dtFimVigenciaRegistro, vrOperacao, entre outros

**Relacionamentos:**
- Todas as entidades são identificadas pela chave composta: cdBanco + nuContaCorrente + cdTipoConta
- Não há relacionamentos diretos entre as entidades no código (processamento independente)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbMovimentoDia | Tabela | SELECT | Busca movimentações do dia agrupadas por conta com range de sequências |
| TbSaldoIndisponivel | Tabela | SELECT | Busca saldos indisponíveis com data de fim de vigência anterior à execução |
| TbAvisoLancamento | Tabela | SELECT | Busca avisos de lançamento com data de inclusão anterior à execução |
| TbLimiteContaCorrente | Tabela | SELECT | Busca limites de conta corrente com data de fim de vigência anterior à execução |
| TbSaldoBloqueado | Tabela | SELECT | Busca saldos bloqueados com motivo de desbloqueio ou data de fim de vigência expirada |
| TbHistoricoMovimento | Tabela | SELECT | Verificação de duplicidade antes de inserir movimentos |
| TbHistoricoSaldoIndisponivel | Tabela | SELECT | Verificação implícita durante inserção |
| TbHistoricoLimiteContaCorrente | Tabela | SELECT | Verificação de duplicidade com LEFT JOIN |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbHistoricoMovimento | Tabela | INSERT | Insere movimentações históricas a partir de TbMovimentoDia |
| TbMovimentoDia | Tabela | DELETE | Remove movimentações após gravação no histórico |
| TbHistoricoSaldoIndisponivel | Tabela | INSERT | Insere saldos indisponíveis históricos |
| TbSaldoIndisponivel | Tabela | DELETE | Remove saldos indisponíveis após gravação no histórico |
| TbAvisoLancamento | Tabela | DELETE | Remove avisos de lançamento antigos |
| TbHistoricoLimiteContaCorrente | Tabela | INSERT | Insere limites de conta corrente históricos |
| TbLimiteContaCorrente | Tabela | DELETE | Remove limites após gravação no histórico |
| TbHistoricoSaldoBloqueado | Tabela | INSERT | Insere saldos bloqueados históricos |
| TbSaldoBloqueado | Tabela | DELETE | Remove saldos bloqueados após gravação no histórico |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| buscaMovimentacoesDia.sql | Leitura | resources/sql/reader | Query para buscar movimentações do dia |
| buscaSaldoIndisponivel.sql | Leitura | resources/sql/reader | Query para buscar saldos indisponíveis |
| buscaAvisoLancamento.sql | Leitura | resources/sql/reader | Query para buscar avisos de lançamento |
| buscaLimiteContaCorrente.sql | Leitura | resources/sql/reader | Query para buscar limites de conta corrente |
| buscaSaldosBloqueados.sql | Leitura | resources/sql/reader | Query para buscar saldos bloqueados |
| gravaHistoricoMovimentosRange.sql | Leitura | JdbiMovimentoContaRepository | Query para inserir movimentos no histórico |
| removeMovimentosRange.sql | Leitura | JdbiMovimentoContaRepository | Query para remover movimentos processados |
| gravaHistoricoSaldoIndisponivel.sql | Leitura | JdbiSaldoIndisponivelContaRepository | Query para inserir saldo indisponível no histórico |
| removeSaldoIndisponivel.sql | Leitura | JdbiSaldoIndisponivelContaRepository | Query para remover saldo indisponível |
| removeAvisoLancamento.sql | Leitura | JdbiAvisoLancamentoRepository | Query para remover avisos de lançamento |
| gravaHistoricoLimiteContaCorrente.sql | Leitura | JdbiLimiteContaCorrenteRepository | Query para inserir limite no histórico |
| removeLimiteContaCorrente.sql | Leitura | JdbiLimiteContaCorrenteRepository | Query para remover limite |
| gravaHistoricoSaldoBloqueado.sql | Leitura | JdbiSaldoBloqueadoRepository | Query para inserir saldo bloqueado no histórico |
| removeSaldoBloqueado.sql | Leitura | JdbiSaldoBloqueadoRepository | Query para remover saldo bloqueado |
| logback-spring.xml | Leitura | Configuração de logging | Configuração de logs da aplicação |
| application.yml | Leitura | Configuração Spring | Configurações da aplicação |

---

## 10. Filas Lidas

Não se aplica.

---

## 11. Filas Geradas

Não se aplica.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Banco de Dados Sybase (DBCONTACORRENTE) | Banco de Dados | Banco principal contendo tabelas operacionais e de histórico de contas correntes |
| Spring Batch Metadata | Banco de Dados | Tabelas de controle do Spring Batch para gerenciamento de jobs e steps |
| Kubernetes | Orquestração | Deploy e execução do job batch via Kubernetes Job |
| Google Cloud Platform | Cloud | Infraestrutura de execução (registry de imagens Docker) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Código bem estruturado seguindo padrões do Spring Batch
- Separação clara de responsabilidades (config, domain, infrastructure, writers, mappers, utils)
- Uso adequado de injeção de dependências e inversão de controle
- Testes unitários bem implementados com boa cobertura
- Uso de JDBI para queries SQL externalizadas, facilitando manutenção
- Tratamento de erros com fault tolerance configurado
- Logging adequado para rastreabilidade
- Uso de Lombok para reduzir boilerplate
- Configurações externalizadas por ambiente
- Processamento paralelo bem implementado

**Pontos de Melhoria:**
- Falta de documentação JavaDoc em algumas classes críticas
- Alguns métodos poderiam ser mais granulares (ex: `realizaMovimentacaoEntreTabelas`)
- Ausência de testes de integração
- Configurações de chunk size e page size poderiam ter valores default mais claros
- Falta de métricas customizadas para monitoramento de negócio
- Alguns nomes de variáveis em português misturados com inglês
- Tratamento genérico de exceções em alguns writers (catch Exception)

---

## 14. Observações Relevantes

1. **Execução Agendada**: O sistema é executado como um Kubernetes Job, provavelmente agendado via CronJob para execução diária

2. **Performance**: O sistema utiliza processamento paralelo com 5 flows simultâneos e paginação configurável para otimizar o processamento de grandes volumes

3. **Configuração por Ambiente**: Possui configurações específicas para ambientes local, des, uat e prd

4. **Pool de Conexões**: Configurado com HikariCP com parâmetros ajustáveis por ambiente (max-pool-size, max-lifetime)

5. **Monitoramento**: Integrado com Prometheus para coleta de métricas via Spring Actuator

6. **Segurança**: Utiliza secrets do Kubernetes para credenciais de banco de dados

7. **Auditoria**: Logs estruturados em JSON para facilitar análise e auditoria

8. **Tolerância a Falhas**: Configurado para pular SQLExceptions e continuar processamento, evitando falha total do job por erros pontuais

9. **Data de Execução**: Sistema salva a data de execução no contexto do job para uso consistente em todos os steps

10. **Transações**: Cada writer opera dentro de transações gerenciadas pelo Spring, garantindo consistência dos dados

11. **Versionamento**: Projeto está na versão 0.13.0, indicando estar em fase de evolução/maturação

12. **CI/CD**: Integrado com Jenkins conforme arquivo jenkins.properties, com pipeline configurado para deploy automático