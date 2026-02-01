---
## Ficha Técnica do Sistema

### 1. Descrição Geral
O **sboot-ccbd-base-orch-cockpit** é um orquestrador de backoffice para operações de Conta Corrente Banco Digital (CCBD). Trata-se de uma API REST desenvolvida em Spring Boot que centraliza e orquestra múltiplas operações bancárias, incluindo consultas de saldo, movimentações, bloqueios/desbloqueios, encerramentos de conta, geração de relatórios, manutenção de tabelas paramétricas, transferências de balanceamento, contabilidade e migração de chaves PIX. O sistema atua como agregador de diversos serviços externos (atoms), utilizando Apache Camel para orquestração de fluxos de negócio e seguindo arquitetura hexagonal (ports/adapters).

---

### 2. Principais Classes e Responsabilidades

| Classe/Componente | Responsabilidade |
|-------------------|------------------|
| **ConsultaController** | Endpoints REST para consultas de saldo, histórico de conta, contas ativas/inativas e funcionários |
| **MovimentacaoController** | Endpoints para extrato, bloqueios/desbloqueios, totalizações de movimentações |
| **EncerramentoContaController** | Gerencia demandas de encerramento (banco/cliente/emergencial/desinteresse), validações e confirmações |
| **RelatorioController** | Geração de cartas PDF (encerramento, histórico, ativas/inativas) e integração IGED |
| **ManutencaoTabelaController** | CRUD de tabelas paramétricas (motivos bloqueio/desbloqueio/encerramento, modalidades, categorias, parâmetros MT940, tipos transação) |
| **TransferenciaController** | Operações de transferência para balanceamento TEF entre contas |
| **ContabilController** | Movimentos contábeis, maiores saldos, parâmetros contábeis |
| **MigracaoController** | Migração e portabilidade de chaves PIX |
| **GeracaoController** | Geração de arquivo M06 |
| **InterfaceContabilController** | Processamento de interface contábil |
| **CategoriaBridge** | Intermediação entre camada apresentação e serviço de Categoria |
| **MotivoBloqueioBridge** | CRUD motivos bloqueio, gestão bloqueios monitorados com ordenação |
| **MotivoDesbloqueioBridge** | CRUD motivos desbloqueio com flag ativo |
| **SaldoNegativoBridge** | Gestão contas com saldo credor/negativo |
| **Mappers (70+ classes)** | Conversão bidirecional entre DTOs, VOs, Representations e objetos de domínio (MapStruct) |
| **Services (25+)** | Camada de serviço que invoca routers Camel via ProducerTemplate |
| **Routers Camel** | Orquestração de fluxos de negócio (BalanceamentoContas, BloqueioContas, EncerramentoConta, Movimentações, etc.) |
| **Repositories (30+)** | Interfaces port para integração com serviços externos via REST |

---

### 3. Tecnologias Utilizadas

- **Spring Boot 2.x** (framework principal)
- **Spring Security** (OAuth2 Resource Server, JWT token validation)
- **Apache Camel 3.0.1** (orquestração de fluxos)
- **MapStruct** (mapeamento objeto-objeto)
- **Lombok** (redução de boilerplate)
- **Swagger/OpenAPI 2.0** (documentação API)
- **Springfox Swagger2** (geração documentação)
- **Maven** (build multi-module)
- **RestTemplate** (cliente HTTP com security)
- **OpenFeign** (clientes REST declarativos)
- **Swagger Codegen** (geração clientes API)
- **Logback** (logging JSON)
- **Spring Actuator** (métricas e health checks)
- **Prometheus + Grafana** (observabilidade)
- **ArchUnit 0.19.0** (validação arquitetural)
- **Tomcat Embed 9.0.109**
- **Java 11**
- **Kubernetes/OpenShift** (deployment)

---

### 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/consulta/saldo-conta-corrente/banco/{banco}/conta/{conta}/tipo/{tipo}` | ConsultaController | Consulta saldo de conta corrente |
| GET | `/consulta/historico-conta/...` | ConsultaController | Histórico de movimentações da conta |
| GET | `/movimentacao-bancaria/extrato/...` | MovimentacaoController | Extrato de movimentações bancárias |
| POST | `/movimentacao-bancaria/bloqueio` | MovimentacaoController | Incluir bloqueio em conta |
| POST | `/movimentacao-bancaria/bloqueio/liberarbloqueio` | MovimentacaoController | Liberar bloqueio de conta |
| GET | `/movimentacao-bancaria/bloqueio` | MovimentacaoController | Listar bloqueios ativos |
| POST | `/encerramento-conta/demandar` | EncerramentoContaController | Demandar encerramento de conta |
| PUT | `/encerramento-conta/confirmar` | EncerramentoContaController | Confirmar encerramento de conta |
| GET | `/encerramento-conta/listar/banco/{banco}` | EncerramentoContaController | Listar encerramentos por banco |
| POST | `/relatorios/encerramento-conta` | RelatorioController | Gerar carta de encerramento PDF |
| GET | `/relatorios/iged` | RelatorioController | Consultar documentos IGED |
| POST | `/manutencao-tabela/motivo-bloqueio` | ManutencaoTabelaController | CRUD motivos de bloqueio |
| POST | `/transferencia` | TransferenciaController | Efetuar transferência de balanceamento |
| GET | `/contabil/dash/...` | ContabilController | Dashboard contábil |
| POST | `/migracao/chave-pix` | MigracaoController | Migração de chave PIX |
| GET | `/v2/movimentacao-contabil/maiores-saldos` | MovimentacaoController | Maiores saldos contábeis |

---

### 5. Principais Regras de Negócio

1. **Encerramento de Conta**: Suporta 3 iniciativas (BANCO/CLIENTE/EMERGENCIAL) com validações de BVIN pendente, saldo adequado e ausência de bloqueios impeditivos. Gera demandas de desinteresse ou imediatas com prazos específicos e emissão de carta de encerramento.

2. **Bloqueio de Conta**: Tipos de bloqueio (CRÉDITO/DÉBITO/VALOR) com motivos monitorados ordenados por prioridade. Validação de limites e configuração para ignorar bloqueios de débito/crédito específicos.

3. **Saldo Negativo/Credor**: Monitoramento e gestão de contas com saldo credor, permitindo associação/remoção de contas ao saldo credor por banco.

4. **Validações de Encerramento**: Cliente deve estar apto (sem BVIN pendente, saldo adequado, sem bloqueios impeditivos) para encerramento.

5. **Motivos Bloqueio Monitorado**: Ordenação de prioridade alterável para controle de bloqueios críticos.

6. **Extrato**: Filtros por data, nome, CPF/CNPJ, últimos N dias, respeitando roles do usuário autenticado.

7. **Balanceamento de Contas**: Transferências TEF entre contas por entidade para ajuste de saldos.

8. **Parâmetros MT940**: Configuração de periodicidades para bancos destino em exportações.

9. **Interface Contábil**: Controle de processamento com status (P/R/F - Pendente/Realizado/Falha).

10. **Migração PIX**: Portabilidade de chaves PIX com tracking de status e validações.

11. **Consulta Colaborador**: Validação de permissão para consulta de dados de funcionários.

12. **Débitos Indevidos**: Registro e consulta de débitos indevidos para tratamento.

13. **Agendamentos**: CRUD de agendamentos de movimentações bancárias.

14. **Categorização de Lançamentos**: Gestão de categorias e tipos de transação para classificação contábil.

15. **Parâmetros Gerais do Sistema**: Manutenção de configurações globais do sistema.

---

### 6. Relação entre Entidades

**Principais Entidades e Relacionamentos:**

- **ContaCorrente**: Entidade central (banco, conta, tipo, agência)
  - 1:N com **SaldoBloqueado** (sequência, vigência, valor)
  - 1:N com **HistoricoSaldoConta**
  - 1:N com **MovimentacaoBancaria**
  - N:1 com **ModalidadeConta**
  - N:1 com **Funcionario** (titular)

- **Funcionario**: (pessoa, cpfCnpj, cargo, área, divisão)
  - N:1 com **Pessoa**
  - 1:N com **ContaCorrente**

- **ModalidadeConta**: (categoria, tipo pessoa, flags investimento/caução)
  - N:1 com **Categoria**
  - 1:N com **ContaCorrente**

- **MotivoBloqueio/Desbloqueio/Encerramento**: Tabelas paramétricas
  - 1:N com **BloqueioSaldo**
  - 1:N com **EncerramentoConta**

- **TipoTransacao**: (categoria lançamento, flags estorno/CPMF)
  - N:1 com **CategoriaLancamento**
  - 1:N com **MovimentacaoBancaria**

- **BalanceamentoContas**: Relaciona contas origem/destino para transferências

- **MigracaoChavePix**: Controla portabilidade de chaves PIX por conta

- **ParametroMt940**: Configurações de exportação por banco

---

### 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbContaCorrente | Tabela | SELECT | Dados cadastrais de contas correntes |
| TbSaldoContaCorrente | Tabela | SELECT | Saldos atuais das contas |
| TbHistoricoSaldo | Tabela | SELECT | Histórico de saldos por período |
| TbMotivoBloqueio | Tabela | SELECT | Motivos parametrizados de bloqueio |
| TbMotivoDesbloqueio | Tabela | SELECT | Motivos parametrizados de desbloqueio |
| TbMotivoEncerramento | Tabela | SELECT | Motivos parametrizados de encerramento |
| TbModalidadeConta | Tabela | SELECT | Modalidades de conta disponíveis |
| TbCategoria | Tabela | SELECT | Categorias de contas |
| TbFuncionario | Tabela | SELECT | Dados de funcionários/colaboradores |
| TbPessoa | Tabela | SELECT | Dados cadastrais de pessoas |
| TbEndereco | Tabela | SELECT | Endereços de pessoas/contas |
| TbMovimentacao | Tabela | SELECT | Movimentações bancárias |
| TbBloqueioSaldo | Tabela | SELECT | Bloqueios ativos em contas |
| TbProcessamentoInterfaceContabil | Tabela | SELECT | Status processamento interface contábil |
| TbTipoTransacao | Tabela | SELECT | Tipos de transação parametrizados |
| TbCategoriaLancamento | Tabela | SELECT | Categorias de lançamento contábil |
| TbParametroMt940 | Tabela | SELECT | Parâmetros exportação MT940 |
| TbBalanceamentoContas | Tabela | SELECT | Configurações balanceamento |
| TbMigracaoChavePix | Tabela | SELECT | Status migrações PIX |
| TbParametroGeralSistema | Tabela | SELECT | Parâmetros gerais do sistema |
| TbOrdenacaoMotivoBloqueio | Tabela | SELECT | Ordenação prioridade bloqueios |
| TbParametroMovimentoContabil | Tabela | SELECT | Parâmetros movimentos contábeis |
| TbTipoContaContabil | Tabela | SELECT | Tipos de conta contábil |

**Observação:** Acesso via APIs REST (atoms) que abstraem acesso direto ao banco. Sybase e Elasticsearch mencionados em especificações YAML.

---

### 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbEncerramentoConta | Tabela | INSERT/UPDATE | Registro de demandas e confirmações de encerramento |
| TbBloqueioSaldo | Tabela | INSERT/UPDATE | Inclusão e atualização de vigência de bloqueios |
| TbMotivoBloqueio | Tabela | INSERT/UPDATE/DELETE | CRUD motivos de bloqueio |
| TbMotivoDesbloqueio | Tabela | INSERT/UPDATE/DELETE | CRUD motivos de desbloqueio |
| TbMotivoEncerramento | Tabela | INSERT/UPDATE/DELETE | CRUD motivos de encerramento |
| TbModalidadeConta | Tabela | INSERT/UPDATE/DELETE | CRUD modalidades de conta |
| TbCategoria | Tabela | INSERT/UPDATE/DELETE | CRUD categorias |
| TbOrdenacaoMotivoBloqueio | Tabela | UPDATE | Atualização ordenação prioridade bloqueios |
| TbParametroMovimentoContabil | Tabela | INSERT/UPDATE | Manutenção parâmetros contábeis |
| TbTipoContaContabil | Tabela | INSERT/UPDATE | Manutenção tipos conta contábil |
| TbParametroMt940 | Tabela | INSERT/UPDATE/DELETE | CRUD parâmetros MT940 |
| TbParametroGeralSistema | Tabela | UPDATE | Atualização parâmetros gerais |
| TbBalanceamentoContas | Tabela | INSERT/UPDATE | Registro transferências balanceamento |
| TbMigracaoChavePix | Tabela | INSERT/UPDATE | Registro e atualização status migrações PIX |
| TbEndereco | Tabela | UPDATE | Atualização endereços |
| TbProcessamentoInterfaceContabil | Tabela | UPDATE | Atualização status processamento |

**Observação:** Operações realizadas via APIs REST (atoms) que encapsulam persistência.

---

### 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | Spring Boot | Configurações aplicação (URLs, OAuth, DB, portas) |
| logback-spring.xml | Leitura | Logback | Configuração logging JSON |
| prometheus.yml | Leitura | Prometheus | Configuração scraping métricas |
| grafana.ini | Leitura | Grafana | Configuração dashboards |
| infra.yml | Leitura | Kubernetes/OpenShift | Configuração deployment e integrações |
| jenkins.properties | Leitura | Jenkins CI/CD | Configuração pipeline build |
| Cartas PDF | Gravação | RelatorioController/GeracaoController | Cartas encerramento, histórico, relatórios |
| Arquivo M06 | Gravação | GeracaoController | Arquivo gerado para processamento |
| Logs JSON | Gravação | Logback | Logs estruturados da aplicação |
| cacerts | Leitura | Volumes K8s | Certificados SSL/TLS |

---

### 10. Filas Lidas

**Não se aplica.** Não foram identificadas filas JMS, Kafka ou RabbitMQ sendo consumidas pelo sistema. Embora o README mencione "RabbitMQ support", não há evidências de implementação de consumers de filas no código analisado.

---

### 11. Filas Geradas

**Não se aplica.** Não foram identificadas filas JMS, Kafka ou RabbitMQ sendo produzidas pelo sistema. Todas as integrações identificadas são síncronas via REST.

---

### 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| **sboot-ccbd-base-atom-movimentacoes** | REST API | Extrato, movimento contábil, maiores saldos, bloqueios, agendamentos |
| **sboot-ccbd-base-orch-extrato** | REST API | Extrato movimentações Sybase/Elastic, extrato PIX, exportação |
| **sboot-ccbd-base-atom-conta-corrente-fecha** | REST API | Interface contábil, atualizações faixa conta |
| **sboot-glob-base-atom-cliente-dados-cadastrais** | REST API | Dados pessoa, endereços, co-titulares |
| **sboot-pgan-base-atom-consulta-colaborador-cartoes** | REST API | Consulta colaborador por CPF |
| **IGED** | REST API | Armazenamento e consulta de documentos (cartas PDF) |
| **BPM Segura/Consulta** | REST API | Workflows TED e encerramento |
| **Serviço Geração PDFs** | REST API | Geração de cartas encerramento e relatórios |
| **OAuth2 JWT Provider** | OAuth2 | Autenticação e autorização via token JWT |
| **Prometheus** | Métricas | Coleta métricas via /actuator/prometheus |
| **Grafana** | Dashboards | Visualização métricas |
| **Atom Saldo** | REST API | Consultas de saldo |
| **Atom Encerramento** | REST API | Operações encerramento conta |
| **Atom Transferências** | REST API | Transferências balanceamento |
| **Atom Gestão Fintech** | REST API | Operações fintech |
| **Atom Migração** | REST API | Migração chaves PIX |
| **Atom Tabelas** | REST API | Manutenção tabelas paramétricas |
| **Atom Backoffice Consulta** | REST API | Consultas backoffice |
| **Atom Conta Corrente Domínio** | REST API | Operações domínio conta corrente |
| **Atom Relatórios** | REST API | Geração relatórios |

**Total:** 37+ URLs de serviços externos configuradas em application.yml e infra.yml.

---

### 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- **Arquitetura bem definida**: Separação clara de camadas (controller → service → bridge → repository) seguindo arquitetura hexagonal (ports/adapters)
- **Uso de padrões consolidados**: Spring Boot, Apache Camel, MapStruct, Lombok reduzem boilerplate e aumentam produtividade
- **Desacoplamento**: 70+ mappers garantem separação entre representations e domain objects
- **Documentação API**: Especificações OpenAPI/Swagger completas para todos os endpoints
- **Segurança**: OAuth2 + JWT implementados, validação de roles
- **Observabilidade**: Actuator, Prometheus, Grafana configurados
- **Tratamento de exceções centralizado**: HttpException, CodigoErroEnum padronizam respostas de erro
- **Configuração externalizada**: application.yml, infra.yml permitem ajustes sem rebuild
- **Validação arquitetural**: ArchUnit 0.19.0 para garantir conformidade
- **Multi-module Maven**: Organização clara (common/domain/application)

**Pontos de Melhoria:**
- **Falta de testes explícitos**: Não foram identificados testes unitários/integração no contexto analisado (embora profiles de teste existam no POM)
- **Complexidade de mapeamento**: 70+ mappers indicam alta complexidade de transformação de dados, potencial para consolidação
- **Dependência de serviços externos**: 37+ integrações REST síncronas podem gerar latência e pontos de falha
- **Documentação técnica**: Ausência de diagramas arquiteturais e fluxos de negócio documentados
- **Logs**: Necessidade de sanitização (LoggerHelper presente, mas uso não verificado em todos os pontos)

---

### 14. Observações Relevantes

1. **Orquestrador Central**: O sistema atua como orquestrador de múltiplos serviços (atoms) para operações de backoffice de conta corrente banco digital.

2. **Apache Camel Core**: Toda orquestração de fluxos de negócio é realizada via routers Camel, com uso de ProducerTemplate nos services.

3. **Geração de Clientes API**: Swagger Codegen gera automaticamente clientes REST para ~10 serviços externos durante build Maven.

4. **Multi-ambiente**: Configurações específicas para des/qa/uat/prd em infra.yml com credenciais em cofre.

5. **Health Checks**: Actuator em porta separada (9090) para health checks e métricas.

6. **Profiles Spring**: activeProfile influencia comportamento de extrato e outras funcionalidades.

7. **Token Budget**: Análise completa requer chunking devido aos 200K tokens de contexto.

8. **Sistema Legado**: Referências a TotalBanco indicam integração com sistemas legados.

9. **Recursos K8s**: Memory 1Gi-2Gi, volumes para cacerts e logback configs por ambiente.

10. **CI/CD**: Jenkins configurado para build e deploy em plataforma Google Cloud (OpenShift).

11. **Versão Atual**: v0.36.0 do projeto.

12. **Java 11**: Versão mínima requerida.

13. **Tomcat Embed**: Versão 9.0.109 com patches de segurança.

14. **Spring Security**: Versão 5.7.13 para mitigação de vulnerabilidades.

15. **Scaffolding**: Template stateless 0.50.0 utilizado para geração inicial do projeto.

---

**Documento gerado em:** 2025-01-XX  
**Versão do Sistema:** 0.36.0  
**Responsável pela Análise:** Agente de Engenharia Reversa