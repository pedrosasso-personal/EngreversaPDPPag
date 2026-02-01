---
## Ficha Técnica do Sistema

### 1. Descrição Geral
Sistema de gestão de pagamentos bancários (TED, TEF, DOC, Tributos, Saque Digital) desenvolvido em arquitetura de microserviços Spring Boot. Oferece APIs REST para inclusão, atualização e consulta de transações, com controle de duplicidade via NSU, gestão de participantes (incluindo clientes fintech e co-titulares), histórico de alterações e integração com feature toggles para regras de correspondência TED. Suporta agendamentos, estornos, devoluções e geração de autenticação bancária.

---

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **PagamentoController** / **PagamentoV2Controller** | Controladores REST para operações de pagamento (inclusão, atualização, consulta) |
| **PagamentoService** | Serviço core com regras de negócio (validação NSU, controle situações, gestão fintech, histórico, feature toggles) |
| **ArquivoRetornoService** | Consulta pagamentos em processamento via NSU |
| **PagamentoRepository** / **PagamentoRepositoryImpl** | Persistência JDBI (CRUD lançamentos, consultas protocolo, atualização situação/participantes) |
| **ArquivoRetornoRepository** / **ArquivoRetornoRepositoryImpl** | Consulta lançamentos com ocorrências |
| **ExceptionHandlerConfiguration** | Tratamento global de exceções REST (mapeia para status HTTP e códigos padronizados) |
| **PagamentoMapper** / **DadosPagamentoMapper** / **DicionarioPagamentoMapper** | Conversão entre entidades de domínio e DTOs/representações |
| **FeatureToggleService** | Gestão de feature flags (ConfigCat) |
| **Pagamento** / **Participante** / **Protocolo** / **SaqueDigital** | Entidades de domínio principais |
| **StatusLancamentoEnum** / **CodigoLiquidacaoEnum** / **ExceptionReasonEnum** | Enumerações de domínio e controle |
| **PagamentoUtils** / **DataHoraUtil** / **LoggerHelper** / **TipoContaUtils** | Utilitários de conversão, validação e logging seguro |

---

### 3. Tecnologias Utilizadas
- **Framework:** Spring Boot 2.x
- **Persistência:** JDBI 3.9.1 (sem JPA)
- **Banco de Dados:** SQL Server (driver 7.4)
- **Documentação API:** Springfox Swagger 3.0 / OpenAPI
- **Segurança:** Spring Security OAuth2, JWT
- **Métricas:** Spring Actuator, Micrometer Prometheus
- **Feature Toggle:** arqt-base-feature-toggle 3.0.1 (ConfigCat)
- **Testes:** JUnit 5, Mockito, Spring Boot Test
- **Build:** Maven, Docker
- **Orquestração:** Kubernetes/OpenShift (OCP)
- **Logging:** Logback (JSON console)
- **Bibliotecas Internas:** arqt-base-microservices-error, sbootlib-spag-base-correspondencia-ted, bv-framework-commons-datatypes, java-spag-base-pagamentos-commons
- **Outros:** Gson, XStream 1.4.21, Tomcat 9.0.109

---

### 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/incluirPagamento` | PagamentoController | Insere novo pagamento com validação NSU |
| PUT | `/v1/atualizarSituacao` | PagamentoController | Atualiza status do lançamento |
| PUT | `/v1/atualizarSituacaoCodigoBarras` | PagamentoController | Atualiza status com código de barras |
| PUT | `/v1/atualizarClienteRemetenteFintech` | PagamentoController | Atualiza cliente fintech remetente |
| PUT | `/v1/atualizarClienteFavorecidoFintech` | PagamentoController | Atualiza cliente fintech favorecido |
| PUT | `/v1/atualizarCoTitularRemetente` | PagamentoController | Atualiza co-titular remetente |
| PUT | `/v1/atualizarCoTitularFavorecido` | PagamentoController | Atualiza co-titular favorecido |
| PUT | `/v1/atualizarSaqueDigital` | PagamentoController | Atualiza dados de saque digital |
| GET | `/v1/pagamento/{cdLancamento}` | PagamentoController | Busca dados básicos do pagamento |
| GET | `/v1/pagamento/protocoloTransacao/{protocolo}` | PagamentoController | Busca pagamento por protocolo |
| GET | `/v1/pagamento/detalhado/{cdLancamento}` | PagamentoController | Retorna detalhes completos do pagamento |
| GET | `/v1/pagamento/original/detalhado/{nuControleSPB}` | PagamentoController | Busca pagamento original por controle SPB |
| POST | `/v1/pagamento/gerarAutenticacaoBancaria/{cdLancamento}` | PagamentoController | Gera código de autenticação bancária |
| GET | `/v1/agendamentos` | PagamentoController | Lista agendamentos (filtro data/manual) |
| PUT | `/v2/atualizarSituacaoLancamento` | PagamentoV2Controller | Atualiza situação de múltiplos lançamentos |
| POST | `/v1/atualizarProtocoloDevolucao` | PagamentoController | Atualiza protocolo de devolução |
| POST | `/v1/verificarDuplicidadeNSU` | PagamentoController | Valida duplicidade de NSU (retorna 208 se duplicado) |
| POST | `/v1/parametrizacao-correspondencia` | PagamentoController | Verifica correspondência TED conforme parametrização |

---

### 5. Principais Regras de Negócio
- **Validação NSU Duplicado:** Impede inclusão de pagamento com NSU já existente (retorna status HTTP 208 com protocolo anterior)
- **Controle de Situações:** Gerencia transições de status (aguardando, confirmado, rejeitado, erro processamento - status 99, 4, 8)
- **Gestão Fintech:** Permite associação de clientes fintech distintos para remetente e favorecido
- **Histórico de Alterações:** Registra todas as modificações em tabelas de log (TbLancamentoLog, TbLogLancamento*)
- **Bloqueio de Saldo:** Controla sequência de bloqueio (sqUltimoBloqueioSaldo)
- **Estorno/Devolução:** Suporta operações de reversão com atualização de protocolo
- **Saque Digital:** Integração com TecBan (UUID, hash, PC, cédulas, QRCode)
- **Agendamentos:** Filtragem por data e tipo (manual/automático)
- **Feature Toggles:** Controle dinâmico de funcionalidades (FT_BOOLEAN_SPAG_TED_IDENTIFICADOR_UNICO, FT_TEXT_SPAG_BASE_REGRAS_CORRESPONDENCIA_TED)
- **Controle de Duplicidade:** Usa TbLancamentoControleUnico para evitar reprocessamento (timeout 30s)
- **Correspondência TED:** Validação de regras de correspondência via biblioteca externa (sbootlib-spag-base-correspondencia-ted)
- **Códigos de Liquidação:** Suporta múltiplos tipos (conta corrente, DOC, CIP, STR, tributo, concessionária, saque digital, cartões)
- **Sanitização de Logs:** Escape de caracteres especiais para segurança (LoggerHelper)
- **Validação Tempo Processamento:** Verifica se NSU está dentro do período permitido para reprocessamento

---

### 6. Relação entre Entidades
- **TbLancamento** (1:1) **TbLancamentoPessoa** (remetente e favorecido separados)
- **TbLancamento** (0:1) **TbLancamentoClienteFintech** (dados fintech opcionais)
- **TbLancamento** (1:N) **TbErroProcessamento** (múltiplas ocorrências de erro)
- **TbLancamento** (1:N) **TbLancamentoLog** / **TbLogLancamento*** (histórico de alterações)
- **TbLancamento** (0:1) **TbLancamentoControleUnico** (controle duplicidade NSU)
- **TbLancamento** (0:1) **TbLancamentoSaqueDigital** (dados específicos saque digital)
- **Pagamento** (domínio) contém **Participante** (remetente/favorecido), **Protocolo**, **SaqueDigital**

---

### 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbLancamento (SPAG_LANCAMENTO) | Tabela | SELECT | Consulta dados de lançamentos/pagamentos |
| TbLancamentoPessoa (SPAG_LANCAMENTO_PESSOA) | Tabela | SELECT | Consulta dados de participantes (remetente/favorecido) |
| TbLancamentoClienteFintech (SPAG_LANCAMENTO_CLIENTE_FINTECH) | Tabela | SELECT | Consulta dados de clientes fintech |
| TbErroProcessamento (SPAG_LANCAMENTO_OCORRENCIA) | Tabela | SELECT | Consulta ocorrências/erros de processamento |
| TbOcorrenciaErroPagamento | Tabela | SELECT | Consulta dicionário de erros |
| TbParametroPagamentoFintech | Tabela | SELECT | Consulta parametrizações fintech |
| TbLancamentoControleUnico | Tabela | SELECT | Verifica duplicidade NSU |
| TbLancamentoSaqueDigital | Tabela | SELECT | Consulta dados de saque digital |
| TbLancamentoLog / TbLogLancamento* | Tabela | SELECT | Consulta histórico de alterações |

---

### 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbLancamento (SPAG_LANCAMENTO) | Tabela | INSERT/UPDATE | Inclusão e atualização de lançamentos (situação, código barras, autenticação, etc) |
| TbLancamentoPessoa (SPAG_LANCAMENTO_PESSOA) | Tabela | INSERT/UPDATE | Inclusão e atualização de participantes |
| TbLancamentoClienteFintech (SPAG_LANCAMENTO_CLIENTE_FINTECH) | Tabela | INSERT/UPDATE | Inclusão e atualização de dados fintech |
| TbErroProcessamento (SPAG_LANCAMENTO_OCORRENCIA) | Tabela | INSERT | Registro de ocorrências/erros |
| TbLancamentoControleUnico | Tabela | INSERT/DELETE | Controle de duplicidade NSU (inserção e remoção após timeout) |
| TbLancamentoSaqueDigital | Tabela | INSERT/UPDATE | Inclusão e atualização de dados saque digital |
| TbLancamentoLog / TbLogLancamento* | Tabela | INSERT | Registro de histórico de alterações (auditoria) |

---

### 9. Arquivos Lidos e Gravados
não se aplica

---

### 10. Filas Lidas
não se aplica

---

### 11. Filas Geradas
não se aplica

---

### 12. Integrações Externas
- **ConfigCat (Feature Toggle):** Serviço de feature flags para controle dinâmico de funcionalidades (biblioteca arqt-base-feature-toggle 3.0.1)
- **Biblioteca de Correspondência TED:** Validação de regras de correspondência TED via sbootlib-spag-base-correspondencia-ted (ValidadorCampoCorrespondencia)
- **TecBan (Saque Digital):** Integração implícita para geração de UUID, hash e PC de saque digital

---

### 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**
- **Pontos Positivos:**
  - Separação clara de camadas (domain, service, controller, repository)
  - Uso de DTOs para comunicação REST
  - Tratamento global de exceções padronizado (ExceptionHandlerConfiguration)
  - Cobertura de testes unitários (PagamentoServiceTest, utilitários)
  - Uso de feature toggles para controle de funcionalidades
  - Logging seguro com sanitização (LoggerHelper)
  - Documentação Swagger/OpenAPI
  - Enumerações bem definidas para domínio

- **Pontos de Atenção:**
  - **Complexidade:** PagamentoService com mais de 500 linhas, concentrando muitas responsabilidades (poderia ser refatorado em serviços menores)
  - **Persistência:** Uso de JDBI com SQLs externos em arquivos de recursos (não utiliza JPA/Hibernate, dificultando manutenção)
  - **Mapeamentos Manuais:** Conversão manual entre entidades e DTOs (RowMappers JDBI), sem uso de frameworks como MapStruct
  - **Método com 78 Parâmetros:** `incluirPagamento` no repositório possui assinatura extremamente longa (poderia usar objetos de transferência)
  - **Acoplamento:** Dependência forte de bibliotecas internas específicas do banco (bv-framework, arqt-base)
  - **Documentação:** Falta de JavaDoc em algumas classes críticas

---

### 14. Observações Relevantes
- **Domínio:** Sistema especializado em pagamentos bancários (TED, TEF, DOC, Tributos, Saque Digital)
- **Arquitetura:** Microserviço Spring Boot com deploy em Kubernetes/OpenShift (GCP)
- **Controle de Duplicidade:** Mecanismo robusto usando NSU + TbLancamentoControleUnico com timeout de 30 segundos
- **Auditoria:** Histórico completo de alterações em tabelas de log (TbLancamentoLog, TbLogLancamento*)
- **Fintech:** Suporte a clientes fintech com participantes remetente/favorecido separados
- **Co-titularidade:** Gestão de co-titulares para remetente e favorecido
- **Saque Digital:** Integração com TecBan (UUID, hash, PC, cédulas, QRCode)
- **Agendamentos:** Suporte a pagamentos agendados com filtros por data e tipo
- **Feature Toggles:** Controle dinâmico de funcionalidades (correspondência TED, identificador único)
- **Métricas:** Integração com Prometheus/Grafana via Actuator
- **Segurança:** OAuth2 + JWT para autenticação/autorização
- **Ambientes:** Configurações para local, des, qa, uat, prd (infra.yml)
- **CI/CD:** Pipeline Jenkins configurado (jenkins.properties)
- **Timeout Inclusão:** Controle de 30 segundos para evitar duplicidade em inclusões concorrentes
- **Status HTTP Customizado:** Retorna 208 (Already Reported) para NSU duplicado, 422 para erros de negócio
- **Validação Reprocessamento:** Verifica se NSU está dentro do período permitido para reprocessamento
- **Correspondência TED:** Validação de regras de correspondência via feature toggle e biblioteca externa