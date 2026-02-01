---
## Ficha Técnica do Sistema

### 1. Descrição Geral
O **GDCC (Gestão de Débito em Conta Corrente)** é um sistema corporativo desenvolvido para gerenciar o processo completo de débito automático em contas correntes. O sistema permite o agendamento e cancelamento de remessas de débito, consulta de retornos bancários, parametrização de contas convênio, monitoramento de processamento de arquivos, tratamento de inconsistências e estornos. Atende múltiplos sistemas origem (multiproduto) e bancos conveniados, com controle de autorização de débito, histórico de alterações e auditoria completa das operações.

---

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **AgendamentoRemessaBusinessImpl** | Implementa regras de negócio para agendamento e cancelamento de remessas de débito automático |
| **ConsultaRetornoBusinessImpl** | Gerencia consultas de retorno de débito e histórico de autorizações |
| **ContaConvenioBusinessImpl** | Gerencia contas convênio (bancos conveniados) e seus parâmetros |
| **ParametroRetornoDebitoBusinessImpl** | Associa retornos automáticos do banco com retornos de sistema origem e contas convênio |
| **LogArquivoServicesImpl** | Consulta logs de arquivos de débito processados |
| **ConsultaMonitorServicesImpl** | Integra com backend SOAP para consultar totais de débito por vencimento/remessa |
| **RegistroDebitoDaoImpl** | DAO para persistência de registros de débito |
| **ConsultaRetornoDaoImpl** | DAO para consultas complexas de retorno e histórico de autorização |
| **ContaConvenioDaoImpl** | DAO para operações de conta convênio e bancos conveniados |
| **AlterarContaAction** | Action Struts para alteração de conta bancária de contratos |
| **MonitorDebitoAction** | Action Struts para monitoramento de débitos (vencimento/remessa/retorno) |
| **VisualizarInconsistenciaAction** | Action Struts para visualização e exportação de inconsistências |
| **TratarEstornoAction** | Action Struts para tratamento de estornos de débito |
| **AgendamentoRemessaWebService** | WebService Axis2 para agendamento/cancelamento de remessas |
| **ConsultaBancosConveniadosWebService** | WebService Axis2 para consulta de bancos conveniados |
| **Filtro** | ServletFilter para autenticação e controle de acesso via VFAcesso |

---

### 3. Tecnologias Utilizadas

- **Backend:** Java EE, EJB 2.1, JDBC
- **Framework Web:** Struts 1.2.7, JSP, JSTL, Tiles
- **WebServices:** Axis2 1.3 (SOAP), JAX-WS
- **Servidor de Aplicação:** JBoss 4.2.3
- **Banco de Dados:** Sybase (inferido pela sintaxe SQL: getDate(), convert, TOP)
- **Build:** Maven
- **Frontend:** jQuery 1.4.2, jQuery UI 1.8.6, Highcharts 2.0.5, DisplayTag
- **Relatórios:** Apache POI (Excel), iText (PDF)
- **Segurança:** WS-Security (UsernameToken), VFAcesso (autenticação/autorização)
- **Utilitários:** BVCrypto (criptografia), Commons Validator, Gson
- **Integração:** RemoteProxyCreator (EJB remoto), ESB (Enterprise Service Bus)

---

### 4. Principais Endpoints REST

**Não se aplica.** O sistema utiliza arquitetura Struts 1.x com Actions mapeadas em `.do` e WebServices SOAP Axis2. Não foram identificados endpoints REST.

**Principais Actions Struts:**
- `/agendarRemessa.do` - Agendamento de remessa
- `/cancelarRemessa.do` - Cancelamento de remessa
- `/monitorDebito.do` - Monitor de débitos
- `/logArquivo.do` - Consulta log de arquivos
- `/alterarConta.do` - Alteração de conta bancária
- `/tratarEstorno.do` - Tratamento de estornos
- `/visualizarInconsistencia.do` - Visualização de inconsistências
- `/visualizarSac.do` - Visualização SAC
- `/parametrizar*.do` - Parametrizações diversas

**WebServices SOAP:**
- `AgendamentoRemessaWebService` - agendarRemessa, cancelarRemessa
- `ConsultaRetornoWebService` - consultarRetorno
- `ConsultaBancosConveniadosWebService` - listarBancosConveniados, consultarParametrosContaConvenio
- `ConsultarArquivosProcessadosWebService` - consultarArquivosProcessados, confirmarBaixa/Inconsistencia

---

### 5. Principais Regras de Negócio

1. **Validação de Prazos de Débito:** Data de débito deve ser maior ou igual à data de exercício do sistema. Data de agendamento deve estar entre prazos mínimo e máximo configurados por conta convênio.

2. **Cancelamento de Remessa:** Permitido apenas para registros com status `AGUARDANDO_GERACAO` ou enviados com vencimento maior ou igual à data de exercício.

3. **Agendamento de Cancelamento:** Gera novo registro de débito do tipo `CANCELAMENTO` vinculado ao registro original.

4. **Autorização de Débito:** Bancos CEF (001) e Caixa (104) exigem validação de código de autorização de débito (`cdRegistroAutorizacaoDebito`).

5. **Suspensão de Débito:** Contratos com tipo de cobrança 7 possuem regras especiais de suspensão. Motivo de suspensão 5 aplica-se a casos específicos.

6. **Associação de Retornos:** Retornos automáticos do banco são associados a retornos de sistema origem e contas convênio através de parâmetros. Alterações inativam associações anteriores.

7. **Multiproduto:** Sistemas origem podem ter URLs de notificação únicas ou separadas por operação (Autenticar/Debitar/Cancelar). Validação de formato de URL sem parâmetros.

8. **Tentativas de Débito:** Quantidade de tentativas configurável por conta convênio (`qtTentativaDebito`).

9. **Custo de Débito Automático:** Valor de custo configurável por conta convênio (`vrCustoDebitoAutomatico`).

10. **Histórico de Alterações:** Todas as alterações em contas convênio, parâmetros de retorno e autorizações geram registros de log para auditoria.

11. **Processamento de Arquivos:** Arquivos de remessa e retorno seguem layout FEBRABAN (versão configurável). Status de processamento rastreado em `TbLogArquivoDebito`.

12. **Inconsistências:** Débitos com status `ERRO` são identificados como inconsistências e podem ser tratados via interface específica.

---

### 6. Relação entre Entidades

**Principais Entidades e Relacionamentos:**

- **ContaConvenio** (1) ↔ (N) **ContaConvenioSistemaOrigem**: Uma conta convênio pode ter múltiplos agrupamentos de sistema origem.
- **ContaConvenioSistemaOrigem** (N) ↔ (N) **ParametroRetornoDebito** ↔ (N) **RetornoDebitoAutomatico**: Associação N:N entre contas convênio, retornos automáticos e retornos de sistema origem.
- **ContaConvenio** (1) ↔ (N) **RegistroDebito**: Uma conta convênio possui múltiplos registros de débito.
- **RegistroDebito** (N) ↔ (1) **StatusDebito**: Cada registro possui um status.
- **RegistroDebito** (1) ↔ (N) **EventoRegistroDebito**: Histórico de eventos de um registro.
- **LogArquivoDebito** (1) ↔ (N) **EventoRegistroDebito**: Log de arquivo contém múltiplos eventos.
- **Banco** (1) ↔ (N) **ContaConvenio**: Um banco possui múltiplas contas convênio.
- **Banco** (1) ↔ (N) **ParametroAutorizacaoDebito**: Parâmetros de autorização por banco.
- **SistemaOrigem** (1) ↔ (N) **EnderecoEletronicoAvisoDbto**: URLs de notificação por sistema origem.
- **Contrato** (1) ↔ (N) **ParcelaDebito**: Um contrato possui múltiplas parcelas de débito.
- **ParcelaDebito** (N) ↔ (1) **RegistroDebito**: Parcelas vinculadas a registros de débito.

---

### 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbContaConvenio | Tabela | SELECT | Contas convênio (bancos conveniados) |
| TbParametroSistema | Tabela | SELECT | Parâmetros do sistema (data exercício, processamento) |
| TbRegistroDebito | Tabela | SELECT | Registros de débito agendados/processados |
| TbLogArquivoDebito | Tabela | SELECT | Logs de arquivos de débito processados |
| TbEventoRegistroDebito | Tabela | SELECT | Eventos de registros de débito |
| TbRetornoDebitoAutomatico | Tabela | SELECT | Retornos automáticos dos bancos |
| TbRetornoDebitoSistemaOrigem | Tabela | SELECT | Retornos de sistema origem |
| TbParametroRetornoDebito | Tabela | SELECT | Associações entre retornos e contas convênio |
| TbContaConvenioSistemaOrigem | Tabela | SELECT | Agrupamentos de sistema origem por conta convênio |
| TbBanco | Tabela | SELECT | Cadastro de bancos |
| TbProduto | Tabela | SELECT | Produtos financeiros |
| TbInformacaoBaixa | Tabela | SELECT | Informações de baixa de débito |
| TbRegistroAutorizacaoDebito | Tabela | SELECT | Histórico de autorizações de débito |
| TbStatusDebito | Tabela | SELECT | Status de débito |
| TbLogSumarioArquivoDebito | Tabela | SELECT | Sumário de logs de arquivo |
| TbLogArquivoDebitoTipoInvalido | Tabela | SELECT | Registros inválidos de arquivo |
| TbVeiculoLegal | Tabela | SELECT | Veículos legais ativos |
| TbParametroAutorizacaoDebito | Tabela | SELECT | Parâmetros de autorização de débito por banco |
| TbModeloAutorizacaoDebito | Tabela | SELECT | Modelos de autorização de débito |
| TbSistemaOrigem | Tabela | SELECT | Sistemas origem multiproduto |
| TbEnderecoEletronicoAvisoDbto | Tabela | SELECT | URLs de notificação de débito |
| GDCF_CONTA_CONVENIO | Tabela | SELECT | Contas convênio (nomenclatura alternativa) |
| GDCF_PARCELA_DEBITO | Tabela | SELECT | Parcelas de débito de contratos |
| GDCF_SUSPENSAO | Tabela | SELECT | Suspensões de débito |
| GDCF_HISTORICO_ALTERACAO | Tabela | SELECT | Histórico de alterações de conta |

---

### 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbRegistroDebito | Tabela | INSERT/UPDATE | Inserção de novos registros de débito e atualização de status |
| TbContaConvenio | Tabela | UPDATE | Atualização de parâmetros de conta convênio |
| TbLogContaConvenio | Tabela | INSERT | Log de alterações de conta convênio |
| TbContaConvenioSistemaOrigem | Tabela | INSERT/UPDATE/DELETE | Gestão de agrupamentos de sistema origem |
| TbLogContaConvenioSistemaOrigem | Tabela | INSERT | Log de alterações de agrupamentos |
| TbParametroRetornoDebito | Tabela | INSERT/UPDATE | Associações entre retornos e contas convênio |
| TbLogParametroRetornoDebito | Tabela | INSERT | Log de alterações de parâmetros de retorno |
| TbRetornoDebitoAutomatico | Tabela | INSERT/UPDATE | Cadastro de retornos automáticos |
| TbRetornoDebitoSistemaOrigem | Tabela | INSERT/UPDATE | Cadastro de retornos de sistema origem |
| TbLogArquivoDebito | Tabela | UPDATE | Atualização de status de log de arquivo |
| TbParametroAutorizacaoDebito | Tabela | INSERT/UPDATE | Parametrização de autorização de débito (inativa anterior, insere novo) |
| TbSistemaOrigem | Tabela | INSERT/UPDATE | Cadastro de sistemas origem multiproduto |
| TbEnderecoEletronicoAvisoDbto | Tabela | INSERT/UPDATE/DELETE | URLs de notificação de débito |
| GDCF_CONTA_CONVENIO | Tabela | UPDATE | Alteração de conta bancária de contratos |
| GDCF_HISTORICO_ALTERACAO | Tabela | INSERT | Histórico de alterações de conta |
| GDCF_PARCELA_DEBITO | Tabela | UPDATE | Alteração de data de estorno de parcelas |

---

### 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| Arquivos de Remessa FEBRABAN | Leitura/Gravação | LogArquivoServicesImpl, processamento batch (não detalhado) | Arquivos de remessa de débito enviados aos bancos |
| Arquivos de Retorno FEBRABAN | Leitura | LogArquivoServicesImpl, processamento batch (não detalhado) | Arquivos de retorno de débito recebidos dos bancos |
| Relatórios PDF | Gravação | LogArquivoAction, VisualizarInconsistenciaAction (iText) | Relatórios de logs, inconsistências e retornos |
| Relatórios Excel | Gravação | LogArquivoAction, RelDetalheRetornoAction, VisualizarInconsistenciaAction (Apache POI) | Exportação de dados para Excel |
| Relatórios TXT | Gravação | LogArquivoAction | Exportação de registros não processados |
| GDCCConsultaGeralDebitoContaBackend.properties | Leitura | PropertiesUtil | Configurações de conexão com backend SOAP |
| gdcc-wsconf.properties | Leitura | Util.java | Configurações de WebServices |
| jndi.properties | Leitura | Testes unitários | Configurações JNDI para testes |

**Observação:** O sistema processa arquivos de remessa e retorno em formato FEBRABAN (layout configurável por versão). A leitura/gravação desses arquivos ocorre em componentes batch não detalhados nos códigos fornecidos.

---

### 10. Filas Lidas

**Não se aplica.** Não foram identificadas integrações com sistemas de mensageria (JMS, Kafka, RabbitMQ) nos códigos analisados.

---

### 11. Filas Geradas

**Não se aplica.** Não foram identificadas publicações em filas de mensageria nos códigos analisados.

---

### 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| **VFAcesso** | WebService SOAP | Autenticação e autorização de usuários. Validação de transações e permissões. Endpoint configurável. |
| **ConsultaGeralDebitoContaBackend** | WebService SOAP | Consulta de totais de débito por vencimento e remessa. Operações: `consultarTotalDebitoPorVencimento`, `consultarTotalRemessaDebitoPorVencimento`. |
| **GestaoDeContratos (SPersisteContratoEJB)** | EJB Remoto | Alteração de instrumento de cobrança de contratos. Método: `alteraInstrumentoCobranca`. |
| **LogContaConvenioServices** | EJB Remoto | Registro de logs de alterações de conta convênio. |
| **LogContaConvenioSistemaOrigemServices** | EJB Remoto | Registro de logs de alterações de agrupamentos de sistema origem. |
| **Sistemas Origem Multiproduto** | HTTP/REST | Notificações de débito via URLs configuradas (callbacks). Operações: Autenticar, Debitar, Cancelar. |

---

### 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura em camadas bem definida (Business, DAO, RowMapper, Actions, Services)
- Uso de padrões de projeto (DAO, Proxy, DTO)
- Separação de SQLs em arquivos `.bv-sql` (configuração externa)
- Injeção de dependências via Spring
- Testes unitários presentes (AgendamentoRemessaBusinessUnitTest)
- Histórico de alterações (logs de auditoria)
- Validações de negócio implementadas

**Pontos de Atenção:**
- **Tecnologias Legadas:** Struts 1.x, EJB 2.1, Axis2 1.3, JBoss 4.2.3 (descontinuados)
- **Encoding:** Arquivos em ISO-8859-1 (não UTF-8)
- **Comentários TODO:** Indicam campos opcionais não validados (ex: `DtEnvioRegistroDebito`)
- **Validações Básicas:** Uso de `IllegalArgumentException` genérico em vez de exceptions customizadas
- **Scriptlets em JSPs:** Presença de código Java embutido em JSPs (má prática)
- **Complexidade de JSPs:** JSPs extensas com lógica de apresentação misturada
- **Dependências Remotas:** Uso de `RemoteProxyCreator` para chamadas EJB (acoplamento)
- **Falta de Documentação:** Javadoc ausente ou incompleto em muitas classes
- **Segurança:** WS-Security básico (UsernameToken), sem menção a HTTPS/TLS
- **Manutenibilidade:** Código legado dificulta evolução e manutenção

**Recomendações:**
- Migração para tecnologias modernas (Spring Boot, REST, JPA/Hibernate)
- Refatoração de JSPs para uso de frameworks frontend (Angular, React, Vue)
- Implementação de testes automatizados (cobertura atual baixa)
- Adoção de UTF-8 como encoding padrão
- Melhoria de documentação técnica
- Revisão de segurança (autenticação/autorização, criptografia)

---

### 14. Observações Relevantes

1. **Sistema Legado Crítico:** O GDCC é um sistema legado em produção que gerencia operações financeiras críticas (débito automático). Qualquer alteração requer testes rigorosos.

2. **Multiproduto:** O sistema suporta múltiplos sistemas origem (multiproduto) com callbacks HTTP configuráveis, permitindo integração com diversos produtos financeiros.

3. **Auditoria Completa:** Todas as operações críticas (alterações de conta, parâmetros, retornos) geram logs de auditoria com usuário, data/hora e valores anteriores.

4. **Processamento Batch:** Embora não detalhado nos códigos fornecidos, o sistema possui componentes batch para processamento de arquivos FEBRABAN (remessa/retorno).

5. **Controle de Acesso:** Integração com VFAcesso para autenticação e autorização baseada em transações (BVF_GDCC_*, BVF_GDCF_*).

6. **Relatórios:** Geração de relatórios em múltiplos formatos (PDF, Excel, TXT) para análise de logs, inconsistências e retornos.

7. **Monitoramento:** Interface de monitoramento de débitos com consolidação por vencimento, remessa e retorno, incluindo gráficos (Highcharts).

8. **Tratamento de Inconsistências:** Funcionalidade específica para identificação e tratamento de débitos com erro, incluindo alteração de data de estorno.

9. **Parametrização Flexível:** Sistema altamente parametrizável (contas convênio, retornos, autorizações, prazos, custos), permitindo adaptação a diferentes bancos e produtos.

10. **Integração com Gestão de Contratos:** Alterações de conta bancária integram com sistema de gestão de contratos para atualização de instrumento de cobrança.

11. **Suporte a Múltiplos Bancos:** Sistema preparado para trabalhar com diversos bancos conveniados, cada um com parâmetros específicos.

12. **Histórico de Autorizações:** Rastreamento completo de autorizações de débito por CPF/CNPJ, banco, conta e contrato.

---

**Documento gerado em:** 2025-01-10  
**Versão do Sistema:** 0.19.0  
**Responsável pela Análise:** Agente de Engenharia Reversa