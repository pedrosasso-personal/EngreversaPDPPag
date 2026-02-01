---
## Ficha Técnica do Sistema

### 1. Descrição Geral
Sistema de gerenciamento de cobrança bancária (boletos) voltado para ambiente intranet corporativo Votorantim. O sistema permite parametrizar ocorrências de rejeição de boletos, realizar correções manuais de boletos rejeitados pelos bancos, consultar histórico de processamento, gerar relatórios de conferência (analítico e sintético) e gerenciar validações sistêmicas de sistemas emissores. Integra-se com serviços externos SCCO para reenvio de boletos corrigidos e mantém auditoria completa de todas as operações.

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **BancosBeanImpl** | EJB para buscar dados de bancos cadastrados |
| **EstadoProcessamentoBeanImpl** | EJB para buscar estados de processamento de boletos |
| **InstrumentoCobrancaBeanImpl** | EJB para buscar instrumentos de cobrança disponíveis |
| **ParametrizacaoOcorrenciaBeanImpl** | EJB para gerenciar parametrização de ocorrências e sub-ocorrências de rejeição, incluindo campos editáveis/não-editáveis |
| **RegistroInstrumentoCobrancaBeanImpl** | EJB para gerenciar registros de boletos, obter rejeitados e enviar correções via integração SCCO |
| **RelatorioConferenciaBeanImpl** | EJB para gerar relatórios de conferência (analítico e sintético) consolidando quantidades por estado |
| **SistemaOrigemBeanImpl** | EJB para buscar sistemas de origem de boletos |
| **SistemaEmissorBeanImpl** | EJB para gerenciar sistemas emissores e atualizar flags de validação sistêmica |
| **SubOcorrenciaRejeicaoBoletoBeanImpl** | EJB para gerenciar sub-ocorrências de rejeição, marcando motivos como editáveis ou não-editáveis |
| **ClienteSCCOConsumer** | Cliente JAX-WS para consumir serviços SCCO (solicitarRegistroBoleto) |
| **ClienteSCCOConsumerFactory** | Factory para criar instâncias do cliente SCCO com configurações de endpoint e credenciais |
| **CorrecaoRestApi** | API REST para buscar e enviar boletos rejeitados corrigidos |
| **MotivoRejeicaoRestApi** | API REST para gerenciar motivos de rejeição editáveis/não-editáveis por sistema emissor |
| **ParametrizacaoOcorrenciaRestApi** | API REST para parametrização de ocorrências e sub-ocorrências |
| **RelatorioConferenciaRestApi** | API REST para gerar relatórios de conferência em PDF/CSV |
| **ValidacaoRestApi** | API REST para gerenciar validação de sistemas emissores |
| **DAOs (BancoDao, ParametrizacaoOcorrenciaDao, etc.)** | Camada de acesso a dados via JDBC e Stored Procedures |
| **Mappers (BancoMapper, OcorrenciaBoletoMapper, etc.)** | RowMappers Spring JDBC para conversão ResultSet em objetos de domínio |
| **ImprimirRelatorioJasper** | Gerador de relatórios PDF usando JasperReports |

### 3. Tecnologias Utilizadas

- **Java EE 7** (JDK 1.7_64)
- **EJB 3.x** (Enterprise JavaBeans)
- **CDI** (Contexts and Dependency Injection)
- **JAX-RS** (REST APIs)
- **JAX-WS** (SOAP Web Services)
- **WS-Security** (UsernameToken para autenticação)
- **JDBC** (acesso direto ao banco de dados)
- **Spring JDBC** (RowMappers, StoredProcedures)
- **Oracle Database** (via DataSource jdbc/SccoDS)
- **IBM WebSphere Application Server (WAS)**
- **JasperReports** (geração de relatórios PDF)
- **iText** (manipulação de PDF)
- **Apache Commons CSV** (exportação CSV)
- **Log4j2** (logging)
- **Swagger** (documentação de APIs REST)
- **Maven** (gerenciamento de dependências e build multi-módulo)
- **Guava, Gson, Joda-Time** (bibliotecas utilitárias)
- **JUnit, Mockito** (testes unitários)
- **Frameworks Votorantim**: arqt-base-lib v1.0.14, fjee-base-lib v1.1.3

### 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/api/correcao/buscar` | CorrecaoRestApi | Busca boletos rejeitados com filtros |
| GET | `/api/correcao/buscarHistorico` | CorrecaoRestApi | Busca histórico de boletos rejeitados |
| GET | `/api/correcao/obterRegistroRejeitado/{id}` | CorrecaoRestApi | Obtém detalhes de um boleto rejeitado específico |
| GET | `/api/correcao/obterCampoEditavel/{id}` | CorrecaoRestApi | Obtém campos editáveis para correção de boleto |
| GET | `/api/correcao/obterHistoricoRegistroRejeitado/{id}/{status}` | CorrecaoRestApi | Obtém histórico de um registro rejeitado por status |
| POST | `/api/correcao/enviarRegistroCorrigido` | CorrecaoRestApi | Envia boleto corrigido para reprocessamento (JSON VBoletoRejeitado) |
| GET | `/api/motivorejeicao/buscarMotivosNaoEditaveis/{cdSist}/{cdBanco}` | MotivoRejeicaoRestApi | Busca motivos não-editáveis por sistema e banco |
| GET | `/api/motivorejeicao/buscarMotivosEditaveis` | MotivoRejeicaoRestApi | Busca todos os motivos editáveis |
| POST | `/api/motivorejeicao/marcarTodosComoNaoEditaveis` | MotivoRejeicaoRestApi | Marca todos os motivos como não-editáveis |
| POST | `/api/motivorejeicao/marcarTodosComoEditaveis` | MotivoRejeicaoRestApi | Marca todos os motivos como editáveis |
| POST | `/api/motivorejeicao/marcarComoNaoEditavel/{cdSist}/{cdOcor}/{cdSubOcor}` | MotivoRejeicaoRestApi | Marca motivo específico como não-editável |
| POST | `/api/motivorejeicao/marcarComoEditavel` | MotivoRejeicaoRestApi | Marca motivo específico como editável |
| GET | `/api/ocorrenciaretorno/estadoprocessamento` | OcorrenciaRetornoRestApi | Retorna lista de estados de processamento |
| POST | `/api/parametrizacaoocorrencia/busca` | ParametrizacaoOcorrenciaRestApi | Busca parametrizações com filtros (form data) |
| POST | `/api/parametrizacaoocorrencia/atualiza` | ParametrizacaoOcorrenciaRestApi | Atualiza parametrização de ocorrência |
| POST | `/api/parametrizacaoocorrencia/exclui` | ParametrizacaoOcorrenciaRestApi | Exclui parametrização de ocorrência |
| POST | `/api/parametrizacaoocorrencia/salvar` | ParametrizacaoOcorrenciaRestApi | Salva nova parametrização |
| POST | `/api/parametrizacaoocorrencia/buscarSubMotivo` | ParametrizacaoOcorrenciaRestApi | Busca sub-motivos de rejeição |
| POST | `/api/parametrizacaoocorrencia/marcarComoEditaveis` | ParametrizacaoOcorrenciaRestApi | Marca campos como editáveis (JSON List<VCampoCorrecao>) |
| POST | `/api/parametrizacaoocorrencia/marcarComoNaoEditaveis` | ParametrizacaoOcorrenciaRestApi | Marca campos como não-editáveis |
| GET | `/api/relatorioconferencia/instrumentocobranca` | RelatorioConferenciaRestApi | Lista instrumentos de cobrança |
| GET | `/api/relatorioconferencia/bancos` | RelatorioConferenciaRestApi | Lista bancos |
| GET | `/api/relatorioconferencia/sistemaorigem` | RelatorioConferenciaRestApi | Lista sistemas de origem |
| POST | `/api/relatorioconferencia/analitico/pdf` | RelatorioConferenciaRestApi | Gera relatório analítico em PDF (form data) |
| POST | `/api/relatorioconferencia/analitico/csv` | RelatorioConferenciaRestApi | Gera relatório analítico em CSV |
| POST | `/api/relatorioconferencia/sintetico/pdf` | RelatorioConferenciaRestApi | Gera relatório sintético em PDF |
| POST | `/api/relatorioconferencia/sintetico/csv` | RelatorioConferenciaRestApi | Gera relatório sintético em CSV |
| POST | `/api/relatorioconferencia/sintetico/verifica` | RelatorioConferenciaRestApi | Verifica dados para relatório sintético (JSON VDadosRelatorio) |
| POST | `/api/relatorioconferencia/analitico/verifica` | RelatorioConferenciaRestApi | Verifica dados para relatório analítico |
| GET | `/api/validacao/buscaremissor` | ValidacaoRestApi | Busca sistemas emissores |
| POST | `/api/validacao/atualizarStatus/{sistema}/{flag}` | ValidacaoRestApi | Atualiza flag de validação sistêmica de emissor |

### 5. Principais Regras de Negócio

1. **Parametrização de Ocorrências**: Permite configurar quais campos de boletos rejeitados podem ser editados para correção, associando ocorrências e sub-ocorrências bancárias a campos específicos do sistema.

2. **Correção de Boletos Rejeitados**: Usuários podem corrigir manualmente boletos rejeitados pelos bancos através de interface web, alterando apenas campos parametrizados como editáveis.

3. **Reenvio de Boletos Corrigidos**: Após correção, boletos são reenviados automaticamente ao sistema SCCO via integração SOAP para novo processamento bancário.

4. **Histórico Auditável**: Mantém histórico completo de todas as situações de processamento de cada boleto, utilizando a data mais recente (MAX(DtSituacaoProcessamentoInsto)) para determinar o status atual.

5. **Relatórios de Conferência**: 
   - **Analítico**: Detalha cada boleto individualmente com todas as informações de processamento
   - **Sintético**: Totaliza quantidades por tipo de comando (ação) e estado de processamento (enviadas, acatadas, rejeitadas, pendentes)

6. **Validação Sistêmica**: Controla flag de validação sistêmica (FlValidacaoSistemicaRgstoBlto) por sistema emissor, permitindo habilitar/desabilitar validações específicas.

7. **Filtros de Sistema Origem**: Algumas consultas excluem automaticamente sistemas específicos (ITAUSIG=1, CARTOES=2) das listagens.

8. **Estados de Processamento**: Sistema trabalha com estados principais como Rejeitado (código 3), Acatado, Pendente, entre outros.

9. **Integração Bancária**: Processa arquivos de retorno bancário (TpArquivoBanco) com comandos de solicitação tipo Remessa (R) ou Baixa (B).

10. **Segurança por Roles**: Acesso controlado por perfis ADMIN, PECD e intr-middleware em todos os EJBs.

### 6. Relação entre Entidades

**Entidades Principais:**

- **Banco**: Representa instituições bancárias cadastradas
- **InstrumentoCobranca**: Tipos de instrumentos de cobrança (boleto, etc.)
- **SistemaOrigem**: Sistemas que originam solicitações de cobrança
- **SistemaEmissor**: Sistemas emissores de boletos com flag de validação
- **EstadoProcessamento**: Estados possíveis do processamento (Enviado, Acatado, Rejeitado, Pendente)
- **OcorrenciaBoleto**: Ocorrências de rejeição retornadas pelos bancos
- **SubOcorrenciaRejeicaoBoleto**: Detalhamento de motivos de rejeição
- **RegistroInstrumentoCobranca**: Registro principal de boleto com dados completos
- **LogRegistroInstrumentoCobranca**: Histórico de situações do registro
- **Cliente**: Dados do cliente/sacado do boleto
- **VeiculoLegal**: Entidade jurídica relacionada ao boleto
- **ManutencaoCamposEditaveis**: Associação entre ocorrências e campos editáveis
- **VBoletoRejeitado**: View/DTO para boletos rejeitados com dados consolidados
- **VCampoCorrecao**: View/DTO para campos disponíveis para correção

**Relacionamentos:**

- RegistroInstrumentoCobranca **N:1** Banco (cdBanco)
- RegistroInstrumentoCobranca **N:1** InstrumentoCobranca (cdInstrumentoCobranca)
- RegistroInstrumentoCobranca **N:1** SistemaOrigem (cdSistemaOrigem)
- RegistroInstrumentoCobranca **N:1** SistemaEmissor (cdSistemaEmissor)
- RegistroInstrumentoCobranca **N:1** Cliente (nuCpfCnpj)
- RegistroInstrumentoCobranca **N:1** VeiculoLegal (cdVeiculoLegal)
- RegistroInstrumentoCobranca **1:N** LogRegistroInstrumentoCobranca (histórico)
- LogRegistroInstrumentoCobranca **N:1** EstadoProcessamento (cdEstadoProcessamento)
- LogRegistroInstrumentoCobranca **N:1** OcorrenciaBoleto (cdOcorrenciaBoleto)
- OcorrenciaBoleto **1:N** SubOcorrenciaRejeicaoBoleto
- OcorrenciaBoleto **N:M** CamposEditaveis (via TbAssociaCampoOcorrenciaRjco)
- SubOcorrenciaRejeicaoBoleto **N:M** CamposEditaveis (via TbAssociaCampoOcorrenciaRjco)
- SistemaEmissor **N:M** CamposEditaveis (via TbAssociaCampoOcorrenciaStma)

### 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TB_BANCO | Tabela | SELECT | Cadastro de bancos |
| TbEstadoProcessamento | Tabela | SELECT | Estados de processamento de boletos |
| TB_INSTRUMENTO_COBRANCA | Tabela | SELECT | Tipos de instrumentos de cobrança |
| TbSistemaOrigem | Tabela | SELECT | Sistemas de origem de solicitações |
| TbSistemaEmissorBoleto | Tabela | SELECT | Sistemas emissores de boletos |
| TbOcorrenciaBoleto | Tabela | SELECT | Ocorrências de rejeição bancária |
| TbSubOcorrenciaRejeicaoBoleto | Tabela | SELECT | Sub-ocorrências/motivos de rejeição |
| TbRegistroInstrumentoCobranca | Tabela | SELECT | Registros de boletos |
| TbLogRegistroInstrumentoCobranca | Tabela | SELECT | Histórico de situações de boletos |
| TbSituacaoProcessamentoInsto | Tabela | SELECT | Situações de processamento com timestamps |
| TbOcorrenciaRejeicaoPrcso | Tabela | SELECT | Ocorrências de rejeição no processamento |
| TbVeiculoLegal | Tabela | SELECT | Entidades jurídicas |
| TbRegistroInstoCbrnaRclho | Tabela | SELECT | Registros de recolhimento |
| TbAssociaCampoOcorrenciaRjco | Tabela | SELECT | Associação campos editáveis x ocorrências |
| TbAssociaCampoOcorrenciaStma | Tabela | SELECT | Associação campos editáveis x sistemas |
| TbParametroAlteracaoColuna | Tabela | SELECT | Parâmetros de alteração de colunas |
| VBoletoRejeitado | View | SELECT | View consolidada de boletos rejeitados |
| VCampoCorrecao | View | SELECT | View de campos disponíveis para correção |

**Stored Procedures Lidas:**
- **PrConsultarBoletosRejeitados**: Consulta boletos rejeitados com filtros
- **PrConsHistBoletosRejeitados**: Consulta histórico de boletos rejeitados
- **PrConsRelatorioBolRejeitados**: Gera relatório analítico de boletos rejeitados
- **PrConsRelatorioSinteticoBolRejeitados**: Gera relatório sintético de boletos rejeitados

### 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbOcorrenciaBoleto | Tabela | INSERT, UPDATE, DELETE | Cadastro de ocorrências de rejeição |
| TbSubOcorrenciaRejeicaoBoleto | Tabela | INSERT, UPDATE, DELETE | Cadastro de sub-ocorrências/motivos |
| TbAssociaCampoOcorrenciaRjco | Tabela | INSERT, DELETE | Associação campos editáveis x ocorrências |
| TbAssociaCampoOcorrenciaStma | Tabela | INSERT, DELETE | Associação campos editáveis x sistemas |
| TbSistemaEmissorBoleto | Tabela | UPDATE | Atualização de flag de validação sistêmica (FlValidacaoSistemicaRgstoBlto) |
| TbRegistroInstrumentoCobranca | Tabela | UPDATE | Atualização implícita de dados de boletos corrigidos (via EJB) |

### 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| config-saca-base.properties | Leitura | ClienteSCCOConsumerFactory (via ServicesAdmResources) | Configurações de endpoint e credenciais SCCO |
| relatorio_analitico.jasper | Leitura | ImprimirRelatorioJasper | Template JasperReports para relatório analítico PDF |
| relatorio_sintetico.jasper | Leitura | ImprimirRelatorioJasper | Template JasperReports para relatório sintético PDF |
| relatorio_analitico.jrxml | Leitura | Recursos JasperReports | Fonte XML do template analítico |
| relatorio_sintetico.jrxml | Leitura | Recursos JasperReports | Fonte XML do template sintético |
| log4j2.xml | Leitura | Configuração Log4j2 | Configuração de logging da aplicação |
| beans.xml | Leitura | CDI Container | Configuração CDI |
| ejb-jar.xml | Leitura | EJB Container | Configuração de EJBs |
| deployment.xml | Leitura | WebSphere | Configuração de deployment WAS |
| web.xml | Leitura | Servlet Container | Configuração web (autenticação BASIC, filtros) |
| ibm-web-bnd.xml | Leitura | WebSphere | Binding de virtual-host WAS |
| roles.properties | Leitura | Segurança | Definição de roles de acesso |
| pom.xml | Leitura | Maven | Configuração de build e dependências |
| *.csv | Gravação | RelatorioConferenciaAnaliticoCSVProviderImpl, RelatorioConferenciaSinteticoCSVProviderImpl | Exportação de relatórios em formato CSV |
| *.pdf | Gravação | RelatorioConferenciaAnaliticoPDFProviderImpl, RelatorioConferenciaSinteticoPDFProviderImpl, ImprimirRelatorioJasper | Geração de relatórios em formato PDF |

### 10. Filas Lidas

não se aplica

### 11. Filas Geradas

não se aplica

### 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **SCCO (Sistema de Cobrança)** | SOAP Web Service | Integração via ClienteSCCOConsumer para reenvio de boletos corrigidos através do método solicitarRegistroBoleto. Utiliza WS-Security com UsernameToken para autenticação. Endpoints configurados por ambiente (DES/QA/UAT/PRD) via config-saca-base.properties. |
| **Oracle Database** | JDBC | Acesso direto ao banco de dados Oracle via DataSource jdbc/SccoDS (siglModlSchemaDS) configurado no WebSphere. Utiliza Oracle Thin JDBC Driver e autenticação via alias siglModlDatabaseAuth. |
| **Frameworks Votorantim** | Bibliotecas Corporativas | arqt-base-lib v1.0.14 (framework de arquitetura) e fjee-base-lib v1.1.3 (framework Java EE) fornecem componentes base, utilitários e padrões corporativos. |

### 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Estrutura bem organizada com separação clara de responsabilidades por camadas (rs, business, persistence, domain)
- Uso adequado de padrões Java EE (EJB, CDI, JAX-RS, JAX-WS)
- Implementação correta de DAOs com RowMappers e Stored Procedures
- Separação de DTOs e entidades de domínio
- Uso de frameworks corporativos padronizados (arqt-base-lib, fjee-base-lib)
- Logging estruturado com SLF4J/Log4j2
- Documentação de APIs via Swagger
- Trilha de auditoria implementada com handlers
- Segurança por roles bem definida

**Pontos Negativos:**
- **SQL hardcoded em arquivos XML**: Dificulta manutenção e versionamento, aumenta risco de erros
- **Concatenação de SQL via StringBuilder** (ParametrizacaoOcorrenciaUtil, RelatorioConferenciaUtil): Risco potencial de SQL injection se validações não forem robustas nos EJBs, código verboso e propenso a erros
- **Validação de entrada básica**: Método isNullOrEmpty simples, falta validação mais robusta de parâmetros nas APIs REST
- **Exception handling genérico**: Try/catch básico retornando apenas status codes HTTP, sem tratamento específico de exceções de negócio
- **Comentários mínimos**: Código legível mas falta documentação JavaDoc em classes e métodos
- **Ausência de testes unitários evidentes**: Não foram identificados testes no material analisado
- **Código exemplo não removido**: ClienteMapper e ContarClientesStoredProcedure parecem ser exemplos/templates não utilizados em produção
- **Dependência de versão Java antiga**: JDK 1.7_64 está desatualizado e sem suporte

### 14. Observações Relevantes

1. **Contexto Corporativo**: Sistema desenvolvido para ambiente intranet da Votorantim, com foco em gestão de cobrança bancária (boletos).

2. **Arquitetura Multi-Módulo**: Projeto Maven estruturado em 9 módulos (commons, domain, persistence, integration, business, jms, ws, rs, ear) facilitando manutenibilidade e reuso.

3. **Histórico Auditável**: Todas as operações mantêm histórico completo na tabela TbSituacaoProcessamentoInsto, utilizando MAX(DtSituacaoProcessamentoInsto) para determinar situação mais recente.

4. **Relatórios Limitados**: Enum OFFICE_XLS presente mas não implementado - sistema gera apenas PDF e CSV, não Excel.

5. **Handlers de Segurança**: Implementação de handlers JAX-WS (AuditoriaHandler, UsernameTokenHandler, WSSecurityUtil) garante trilha rastreável e autenticação em integrações SOAP.

6. **Filtros de Sistema**: Algumas queries excluem automaticamente sistemas ITAUSIG (código 1) e CARTOES (código 2) das listagens.

7. **Estados de Processamento**: Sistema trabalha principalmente com estados Rejeitado (código 3), Acatado e Pendente.

8. **Integração Bancária**: Processa arquivos de retorno bancário com tipos de comando Remessa (R) e Baixa (B).

9. **WebSphere Application Server**: Aplicação deployada em WAS com configurações específicas (virtual-host, datasources, auth aliases).

10. **Autenticação BASIC**: Web.xml configurado com autenticação HTTP BASIC para acesso às APIs.

11. **Templates Jasper**: Relatórios PDF gerados via JasperReports com templates separados (relatorio_analitico.jrxml, relatorio_sintetico.jrxml).

12. **Código Legado**: Presença de código exemplo não utilizado (ClienteMapper, ContarClientesStoredProcedure) sugere necessidade de limpeza.

13. **Versionamento**: Versão atual 17.9.4.33161.1-SNAPSHOT indica desenvolvimento ativo com numeração de build automatizada.

14. **Tecnologia Desatualizada**: Uso de Java 7 e Java EE 7 indica sistema legado que pode necessitar modernização futura.