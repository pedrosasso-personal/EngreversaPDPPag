# Ficha Técnica do Sistema

---

## 1. Descrição Geral

O sistema **sboot-ccbd-base-atom-conta-corrente-fecha** é um serviço atômico Spring Boot responsável pelo processamento de fechamento de contas correntes do Banco Votorantim. Suas principais funcionalidades incluem:

- **Fechamento diário de contas correntes**: Criação de histórico de saldos, atualização de limites, bloqueios e valores indisponíveis
- **Virada de data**: Processamento de faixas de contas durante a virada do dia
- **Geração de arquivo M06**: Arquivo de interface contábil com movimentações do dia
- **Importação de limites**: Importação de limites de crédito e contratos agendados
- **Sincronização de modalidades**: Sincronização de códigos de modalidade entre sistemas
- **Reprocessamento**: Capacidade de reprocessar movimentações para interface contábil

O sistema opera através de listeners RabbitMQ e Google Pub/Sub para processamento assíncrono, além de expor APIs REST para operações síncronas.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal Spring Boot que inicializa a aplicação |
| **ContaCorrenteFechaController** | Controller REST principal que expõe endpoints da API |
| **ListenerContaCorrenteFecha** | Listener RabbitMQ para atualização pós-desbloqueio |
| **ListenerAtualizaFaixaConta** | Listener RabbitMQ para atualização de faixas de contas |
| **ListenerFechamentoDoDia** | Listener Pub/Sub para processamento de fechamento diário |
| **FechamentoDoDiaService** | Orquestra o processo de fechamento diário de contas |
| **HistoricoSaldoService** | Cria histórico de saldo sem composição |
| **HistoricoSaldoCompostoService** | Cria histórico de saldo com composição de valores |
| **ValidaFechamentoDoDiaService** | Valida contas elegíveis para fechamento |
| **ContaService** | Atualiza saldos das contas de forma assíncrona |
| **AtualizaFaixaContaService** | Processa virada de data para faixas de contas |
| **ReprocessamentoServiceImpl** | Gera arquivo M06 para interface contábil |
| **ImportarLimiteCreditoService** | Importa limites de crédito |
| **ImportarContratoAgendadoService** | Importa contratos agendados |
| **SincronizarModalidadesService** | Sincroniza modalidades de conta |
| **ContaRepositoryAsyncImpl** | Atualiza contas de forma assíncrona usando JDBI |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Spring Security** (autenticação e autorização JWT)
- **JDBI 3.39.1** (acesso a banco de dados)
- **RabbitMQ** (mensageria assíncrona)
- **Google Cloud Pub/Sub** (mensageria em nuvem)
- **MySQL 8.4.0** (banco de dados CCBDContaCorrente)
- **Sybase ASE** (banco de dados DBContaCorrente - legado)
- **Swagger/OpenAPI 3.0** (documentação de API)
- **Prometheus + Grafana** (monitoramento e métricas)
- **MapStruct 1.5.5** (mapeamento de objetos)
- **Lombok** (redução de boilerplate)
- **Logback** (logging)
- **Docker** (containerização)
- **Maven** (gerenciamento de dependências)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/conta-corrente-fecha/atualizaFaixaConta` | ContaCorrenteFechaController | Atualiza faixa de contas durante virada de data |
| POST | `/v1/conta-corrente-fecha/atualizaFaixaPosDesbloqueio` | ContaCorrenteFechaController | Atualiza faixa após desbloqueio de conta |
| GET | `/v1/conta-corrente-fecha/downloadMontado` | ContaCorrenteFechaController | Download do arquivo M06 montado |
| GET | `/v1/conta-corrente-fecha/download` | ContaCorrenteFechaController | Gera arquivo M06 em base64 |
| POST | `/v1/conta-corrente-fecha/limite/credito/importar` | ImportarController | Importa limites de crédito |
| POST | `/v1/conta-corrente-fecha/contrato/agendado/importar` | ImportarController | Importa contratos agendados |
| GET | `/v1/conta-corrente-fecha/sincronizacao/obter-data-inicial` | SincronizarModalidadesController | Obtém data inicial para sincronização |
| GET | `/v1/conta-corrente-fecha/sincronizacao/obter-modalidade-conta` | SincronizarModalidadesController | Obtém código de modalidade |
| GET | `/v1/conta-corrente-fecha/sincronizacao/obter-conta` | SincronizarModalidadesController | Obtém conta por modalidade |
| POST | `/v1/conta-corrente-fecha/sincronizacao/atualizar-modalidade` | SincronizarModalidadesController | Atualiza modalidade da conta |
| POST | `/v1/conta-corrente-fecha/sincronizacao/inserir-tb-log-alteracao` | SincronizarModalidadesController | Registra log de alteração |
| POST | `/v1/conta-corrente-fecha/interface-contabil/inserir` | ContaCorrenteFechaController | Insere registro de processamento contábil |
| GET | `/v1/conta-corrente-fecha/interface-contabil/consultar` | ContaCorrenteFechaController | Consulta processamentos contábeis |
| GET | `/v1/conta-corrente-fecha/rotinas-execucoes` | RotinasExecucoesController | Obtém status de execução de rotinas |
| GET | `/v1/conta-corrente-fecha/compensacoes-status/{cdAgencia}` | CompensacoesStatusController | Obtém status de compensação por agência |

---

## 5. Principais Regras de Negócio

1. **Fechamento Diário de Contas**:
   - Contas só podem ter histórico de saldo criado se a data de apuração for posterior à data de abertura
   - Contas encerradas não participam do fechamento se a data de encerramento for anterior à data de apuração
   - Existem dois tipos de criação de histórico: com composição (para datas retroativas) e sem composição (para data atual)

2. **Atualização de Saldos**:
   - Contas são atualizadas se: tiveram lançamento no dia, possuem saldo bloqueado diferente de zero, saldo indisponível diferente de zero ou limite diferente de zero
   - Bloqueios vencidos são removidos do saldo bloqueado durante a virada

3. **Virada de Data**:
   - Processo transacional que inclui: criação de histórico de saldo, atualização de limites/bloqueios/indisponíveis, migração de movimentos para histórico, limpeza de movimentos recusados

4. **Geração de Arquivo M06**:
   - Arquivo de interface contábil com layout posicional específico
   - Suporta reprocessamento baseado em flag de interface
   - Apenas movimentos com indicador de interface = 'S' são incluídos
   - Exclui contas do tipo 6

5. **Importação de Limites**:
   - Limite de Crédito: limpa tabela completa e reinsere todos os limites
   - Contrato Agendado: atualiza registros existentes e insere novos
   - Zera limites de contas que não possuem registro na tabela de limites

6. **Sincronização de Modalidades**:
   - Atualiza código de modalidade tanto em TbConta quanto em TbHistoricoSaldo
   - Registra alterações em TbLogAlteracao para auditoria

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **Conta**: Entidade central representando conta corrente (CdBanco, NuContaCorrente, CdTipoConta)
- **HistoricoSaldo**: Histórico diário de saldos da conta
- **Movimento**: Movimentações financeiras (débito/crédito)
- **LimiteContaCorrente**: Limites de crédito vigentes
- **SaldoBloqueado**: Bloqueios judiciais ou administrativos
- **SaldoIndisponivel**: Valores indisponíveis para saque
- **MovimentoRecusado**: Movimentos que foram recusados

**Relacionamentos:**
- Conta (1) → (N) HistoricoSaldo
- Conta (1) → (N) Movimento
- Conta (1) → (N) LimiteContaCorrente
- Conta (1) → (N) SaldoBloqueado
- Conta (1) → (N) SaldoIndisponivel
- Conta (1) → (N) MovimentoRecusado

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbConta | tabela | SELECT | Consulta dados de contas correntes |
| TbHistoricoSaldo | tabela | SELECT | Verifica existência de histórico de saldo |
| TbLimiteContaCorrente | tabela | SELECT | Consulta limites vigentes |
| TbSaldoBloqueado | tabela | SELECT | Consulta bloqueios ativos |
| TbSaldoIndisponivel | tabela | SELECT | Consulta valores indisponíveis |
| TbMovimentoDia | tabela | SELECT | Consulta movimentos do dia |
| TbHistoricoMovimento | tabela | SELECT | Consulta movimentos históricos |
| TbTransacao | tabela | SELECT | Consulta tipos de transação |
| TbControleData | tabela | SELECT | Consulta datas de controle do sistema |
| TbModalidadeConta | tabela | SELECT | Consulta modalidades de conta |
| TbRotinaExecucao | tabela | SELECT | Consulta status de execução de rotinas |
| TbProcessamentoInterfaceContbl | tabela | SELECT | Consulta processamentos contábeis |
| TbHistoricoLimiteContaCorrente | tabela | SELECT | Verifica limites históricos |
| TbHistoricoSaldoBloqueado | tabela | SELECT | Consulta bloqueios históricos |
| TbHistoricoSaldoIndisponivel | tabela | SELECT | Consulta indisponíveis históricos |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbConta | tabela | UPDATE | Atualiza limites, saldos bloqueados, indisponíveis e modalidade |
| TbHistoricoSaldo | tabela | INSERT | Insere histórico de saldo diário |
| TbHistoricoSaldo | tabela | UPDATE | Atualiza modalidade em históricos |
| TbViradaDataThread | tabela | UPDATE | Atualiza status de processamento da virada |
| TbHistoricoMovimento | tabela | INSERT | Migra movimentos do dia para histórico |
| TbHistoricoMovimento | tabela | UPDATE | Marca movimentos como interfaceados |
| TbMovimentoDia | tabela | DELETE | Remove movimentos após migração |
| TbMovimentoDia | tabela | UPDATE | Marca movimentos como interfaceados |
| TbSaldoBloqueado | tabela | DELETE | Remove bloqueios vencidos |
| TbHistoricoSaldoBloqueado | tabela | INSERT | Arquiva bloqueios vencidos |
| TbSaldoIndisponivel | tabela | DELETE | Remove indisponíveis vencidos |
| TbHistoricoSaldoIndisponivel | tabela | INSERT | Arquiva indisponíveis vencidos |
| TbLimiteContaCorrente | tabela | INSERT | Insere novos limites |
| TbLimiteContaCorrente | tabela | UPDATE | Atualiza limites existentes |
| TbLimiteContaCorrente | tabela | DELETE | Remove todos os limites (importação) |
| TbHistoricoLimiteContaCorrente | tabela | INSERT | Arquiva limites vencidos |
| TbHistoricoLimiteContaCorrente | tabela | DELETE | Remove limites históricos vencidos |
| TbMovimentoRecusado | tabela | DELETE | Remove movimentos recusados |
| TbHistoricoMovimentoRecusado | tabela | INSERT | Arquiva movimentos recusados |
| TbMotivoRecusaMovimento | tabela | DELETE | Remove motivos de recusa |
| TbHistoricoMotivoRecusaMov | tabela | INSERT | Arquiva motivos de recusa |
| TbAvisoLancamento | tabela | DELETE | Remove avisos de lançamento |
| TbLogAlteracao | tabela | INSERT | Registra alterações para auditoria |
| TbProcessamentoInterfaceContbl | tabela | INSERT | Registra processamento de interface contábil |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| arquivo.m06 | gravação | ReprocessamentoServiceImpl | Arquivo de interface contábil com movimentações formatadas em layout posicional |

---

## 10. Filas Lidas

**RabbitMQ:**
- **atualiza_conta_faixa**: Consumida por `ListenerAtualizaFaixaConta` para processar atualização de faixas de contas durante virada de data
- **atualiza_conta_faixa_pos_desbloqueio**: Consumida por `ListenerContaCorrenteFecha` para atualizar faixas após desbloqueio

**Google Pub/Sub:**
- **business-ccbd-base-conta-ativa-sub**: Consumida por `ListenerFechamentoDoDia` para processar solicitações de criação de histórico de saldo

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **MySQL (CCBDContaCorrente)** | Banco de Dados | Banco principal com dados de contas correntes, limites, bloqueios e históricos |
| **Sybase ASE (DBContaCorrente)** | Banco de Dados | Banco legado com dados de movimentações e controle |
| **RabbitMQ** | Mensageria | Processamento assíncrono de virada de data e desbloqueios |
| **Google Cloud Pub/Sub** | Mensageria | Processamento assíncrono de fechamento diário |
| **Prometheus** | Monitoramento | Coleta de métricas da aplicação |
| **Grafana** | Visualização | Dashboards de monitoramento |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (domain, application)
- Uso adequado de padrões como Repository, Service e Controller
- Implementação de processamento assíncrono com CompletableFuture
- Uso de JDBI com SQL externalizado em arquivos .sql (facilita manutenção)
- Configuração adequada de múltiplos datasources
- Logs estruturados e informativos
- Uso de MapStruct para mapeamento de DTOs
- Tratamento de exceções customizadas

**Pontos de Melhoria:**
- Alguns métodos muito extensos (ex: `getMovimento` e `getMovimentoReprocessamento` com lógica duplicada)
- Uso de concatenação de strings para construção de valores formatados (poderia usar String.format)
- Falta de documentação JavaDoc em várias classes
- Alguns nomes de variáveis em português misturados com inglês
- Lógica de negócio complexa em alguns services poderia ser melhor modularizada
- Uso de números mágicos em alguns locais (ex: `cdUsuario = 551`)
- Queries SQL complexas que poderiam se beneficiar de views ou procedures
- Falta de validações mais robustas em alguns endpoints

---

## 14. Observações Relevantes

1. **Arquitetura Multi-Banco**: O sistema trabalha com dois bancos de dados distintos (MySQL e Sybase), sendo o MySQL o banco principal e o Sybase um banco legado em processo de migração.

2. **Processamento Paralelo**: Utiliza intensivamente processamento assíncrono com CompletableFuture e JdbiExecutor para melhorar performance, especialmente na atualização de contas e criação de históricos.

3. **Transacionalidade**: Operações críticas como virada de data e importação de limites são transacionais com rollback em caso de erro.

4. **Ambientes**: Suporta múltiplos ambientes (local, des, uat, prd) com configurações específicas via profiles Spring.

5. **Segurança**: Implementa autenticação JWT através do framework de segurança do BV (sboot-arqt-security).

6. **Monitoramento**: Possui integração completa com Prometheus/Grafana para observabilidade, incluindo métricas de JVM, HTTP, HikariCP e logs.

7. **Deployment**: Preparado para deploy em Kubernetes/OpenShift na Google Cloud Platform.

8. **Padrão de Código**: Segue padrões arquiteturais do Banco Votorantim com validação via ArchUnit.

9. **Reprocessamento**: Sistema possui capacidade de reprocessar movimentações já interfaceadas, identificando através de flags específicas.

10. **Formato M06**: Arquivo de interface contábil segue layout posicional específico com header, registros de detalhe e trailer.