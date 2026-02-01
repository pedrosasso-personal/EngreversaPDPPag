# Ficha Técnica do Sistema

## 1. Descrição Geral

O **java-saca-scco-webservice-registro-was** é um sistema corporativo de gestão de cobrança bancária desenvolvido para o Banco Votorantim. Sua finalidade principal é gerenciar o ciclo completo de registro, emissão e controle de boletos bancários e carnês de pagamento, integrando-se com múltiplos bancos (Banco do Brasil, Bradesco, Itaú, Santander, Votorantim) e com a Câmara Interbancária de Pagamentos (CIP) para registro de títulos de cobrança.

O sistema opera em duas modalidades: **registro online** (integração direta com bancos via webservices) e **registro batch** (processamento em lote via arquivos de remessa). Suporta diversos produtos financeiros como Crédito Pessoal (CP), Crédito Pessoal Consignado (CPC), CDC Sem Garantia (CDCSG), CDC Com Garantia (CDCCG) e Leasing (LSG), além de operações de cessão de crédito e FIDC.

O sistema é responsável por validar dados de cobrança, calcular encargos (multa, mora, desconto), gerar imagens de boletos em PDF via JasperReports, controlar estados de processamento (pendente, enviado, acatado, rejeitado, baixado) e manter histórico completo de ocorrências e rejeições.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **BoletoEndpoint** | Endpoint SOAP principal para operações de registro, consulta, baixa e confirmação de boletos |
| **BoletoEndpointV2** | Endpoint SOAP v2 para geração de imagens de boleto com instruções customizadas |
| **CarneEndpoint** | Endpoint SOAP para emissão de carnês (múltiplos boletos por contrato) |
| **ImageBoletoRestApi** | API REST para geração de PDFs de boletos e carnês |
| **DadosBoletoBeanImpl** | EJB para gerenciamento completo de dados de boleto (consulta, registro, atualização, validações) |
| **EmissaoBoletoBeanImpl** | EJB para geração de imagens PDF de boletos via JasperReports |
| **COBRRegistroCobrancaPropriaBeanImpl** | EJB para integração com CIP/SPB no registro de cobrança própria |
| **ConvenioBeanImpl** | EJB para busca de convênios bancários adequados ao registro |
| **CarneBeanImpl** | EJB para listagem de boletos de carnê por produto financeiro |
| **BoletoAdapter** | Adaptador para conversão entre entidades de domínio e estruturas de integração CIP |
| **RegistroScco** | Entidade principal representando registro de boleto no sistema SCCO |
| **DadosBoleto** | Entidade de domínio com dados completos do boleto bancário |
| **ImpressaoBoleto** | Entidade para geração de layout de impressão de boletos |
| **Util** | Classe utilitária com funções de geração de hash MD5, cálculo de fator de vencimento e dígitos verificadores |
| **GerarDadosBoleto** | Utilitário para geração de linha digitável e código de barras específicos por banco |

---

## 3. Tecnologias Utilizadas

- **JavaEE 7** (EJB 3.x, CDI, JAX-WS, JAX-RS, Servlet 3.0)
- **IBM WebSphere Application Server (WAS)** - servidor de aplicação
- **Spring JDBC** - acesso a dados via RowMappers
- **JasperReports 5.6.0 / 6.21.3** - geração de relatórios PDF
- **iText 2.1.7** - manipulação de PDFs
- **JAX-WS** - webservices SOAP
- **Jersey 2.22.2** - framework REST (JAX-RS)
- **Swagger** - documentação APIs REST
- **Log4j2** - logging
- **Joda-Time** - manipulação de datas
- **Guava, Gson, Apache Commons** - bibliotecas utilitárias
- **Maven** - gerenciamento de dependências e build
- **Oracle Database** - banco de dados (datasources SccoDS, CobrDbIntegracaoSPBDS, CobrDbCobrancaBcoDS, CobrDbGestaoCobrancaDS)
- **JMS** - mensageria (implícito para filas de processamento)
- **WS-Security** - segurança SOAP (UsernameToken, Certificate)
- **Bootstrap 2.x** - interface web (testes)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/api/image/boleto` | ImageBoletoRestApi | Gera PDF de boleto individual |
| GET | `/api/image/boleto/{hashCode}` | ImageBoletoRestApi | Recupera PDF de boleto por hash |
| GET | `/api/image/carne/{hashCode}` | ImageBoletoRestApi | Gera PDF de carnê por hash de boleto |
| GET | `/api/image/carne/contrato/{codigoContrato}` | ImageBoletoRestApi | Gera PDF de carnê completo por contrato |
| GET | `/api/token` | RestTokenApi | Gerenciamento de token OAuth |

**Endpoints SOAP (via JAX-WS):**
- `solicitarRegistroBoleto` - Registra novo boleto
- `listarStatusBoleto` - Consulta status de registro
- `solicitarBaixaRegistroBoleto` - Solicita baixa de boleto
- `listarRegistroBoleto` - Lista dados de registro
- `obterConvenioBoleto` - Obtém convênio bancário
- `confirmarRegistroBoleto` - Confirma registro após retorno banco
- `gerarBoletoInstrucao` (v2) - Gera boleto com instruções customizadas
- `emitirCarnePorContrato` - Emite carnê completo

---

## 5. Principais Regras de Negócio

1. **Validação Sistêmica de Registro**: Flag `FlValidacaoSistemicaRgstoBlto` determina se registro é online (S) ou batch (N). Sistemas com flag 'S' enviam para registro imediato no banco; flag 'N' gera status PRE_ACATADO para processamento posterior.

2. **Carteiras Registradas vs Não-Registradas**: Carteiras com `FlCarteiraRegistrada='N'` recebem confirmação automática sem envio ao banco. Carteiras registradas seguem fluxo completo de integração.

3. **Migração de Boletos Legado**: Boletos com data de emissão anterior à data de inclusão do sistema emissor recebem status ACATADO automaticamente, sem validações de registro.

4. **Exceções de Encargos**: Instrumentos de cobrança 2, 12, 13 e 14 enviam valores de mora/multa normalmente; demais instrumentos zeram esses valores no registro.

5. **Geração de Hash**: Hash MD5 é gerado a partir de: instrumento cobrança + veículo legal + nosso número + banco + convênio + contrato gestão + contrato financeiro. Para Banco do Brasil (001), hash só é gerado após acatação; Votorantim (655) gera imediatamente.

6. **Integração CIP/SPB**: Boletos dentro da faixa de valores CIP (VrMinimoCargaCIP a VrMaximoCargaCIP) são enviados para registro via CIP. Sistema aguarda retorno assíncrono do Bacen. Em caso de falha, há fallback para registro manual DDA.

7. **Cálculo de Multa e Mora**: Multa calculada como `VrTitulo * PcMulta / 100`. Mora calculada como `VrTitulo * TxComissaoPermanenciaMes / 30 / 100` por dia de atraso.

8. **Verbas Rescisórias Consignado**: Contratos consignados privados com data início >= 06/03/2023 usam percentual 35%; anteriores usam 30%.

9. **Fator de Vencimento**: Calculado como dias entre 07/10/1997 e data vencimento. Após 21/02/2025, reinicia contagem a partir dessa data (limite FEBRABAN).

10. **Validação Boleto Quitação**: Boletos com instrumento cobrança 14 (quitação) não podem ter valores de mora, multa ou desconto.

11. **Auto-confirmação FIDC/Cessão**: Contratos de cessão ou FIDC recebem confirmação automática de registro sem aguardar retorno bancário.

12. **Piloto RMBCP**: Reemissão de boletos consignados privados com tratamento especial para verbas rescisórias, controlado por feature flag.

13. **Priorização de Convênios**: Sistema ignora convênios Votorantim se valor estiver dentro do range CIP. Diferencia busca de convênio para carnês vs outros instrumentos.

14. **Estados de Processamento**: Fluxo sequencial: PENDENTE REGISTRO → ENVIADO REGISTRO/PRE ACATADO → ACATADO/REJEITADO → PENDENTE BAIXA → BAIXA ACATADA.

15. **Tratamento de Rejeições**: Boletos rejeitados podem ser reenviados para batch ou online dependendo da configuração do sistema emissor.

---

## 6. Relação entre Entidades

**Entidades Principais e Relacionamentos:**

- **RegistroScco** (entidade central)
  - Relaciona-se com **Convenio** (convenioRegistro)
  - Contém dados de **DadosVeiculoLegal** (beneficiário)
  - Referencia **InstrumentoCobranca**
  - Vincula-se a **Contrato** (gestão, financeiro, legado)

- **DadosBoleto**
  - Relaciona-se com **DadosVeiculoLegal**
  - Referencia **InstrumentoCobranca**
  - Contém **Taxa** (multa, mora, bancária)

- **RegistroInstrumentoCobranca** (persistência)
  - Possui múltiplos **StatusRegistro** (histórico)
  - Relaciona-se com **EstadoProcessamento**
  - Contém **MotivoRegistro** (rejeições)
  - Vincula-se a **RegistroInstCobrancaChave** (índices)
  - Possui **RegistroInstoCbrnaRclho** (complemento desconto/multa/mora)

- **Convenio**
  - Relaciona-se com **Banco**
  - Contém **Agencia** e **Conta**
  - Referencia **Carteira**

- **ImpressaoBoleto**
  - Derivada de **RegistroInstCobrancaChave** ou **DadosBoleto**
  - Contém **DadosVeiculoLegal**
  - Referencia **VerbasRecisoriasEnum**

- **CarneControleCobranca**
  - Relaciona-se com **Contrato**
  - Contém **Taxa**
  - Referencia **IndicadorTaxaBancaria**

**Hierarquia de Herança:**
- **EntidadeBase** ← DadosBoleto, DadosVeiculoLegal

**Agregações:**
- **StatusRegistro** agrega lista de **MotivoRegistro**
- **COBRRegistroCobrancaPropriaOUT** agrega dados de retorno CIP/SPB

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbRegistroInstrumentoCobranca | Tabela | SELECT | Registro principal de boletos |
| TbRegistroInstoCbrnaRclho | Tabela | SELECT | Complemento de registro (desconto/multa/mora) |
| TbSituacaoProcessamentoInsto | Tabela | SELECT | Histórico de situações de processamento |
| vwSituacaoProcessamentoUltimoEstado | View | SELECT | Último estado de processamento por registro |
| TbEstadoProcessamento | Tabela | SELECT | Catálogo de estados (ACATADO, REJEITADO, etc) |
| TbOcorrenciaRejeicaoPrcso | Tabela | SELECT | Motivos de rejeição de registro |
| TB_CARNE_CONTROLE_COBRANCA | Tabela | SELECT | Controle de cobrança de carnês |
| TB_CARNE_PARAMETRO_REMESSA | Tabela | SELECT | Parâmetros de remessa bancária |
| TB_CARNE_CONTROLE_ENVIO | Tabela | SELECT | Controle de envios de arquivos |
| TB_CONTA_CORRENTE | Tabela | SELECT | Contas correntes bancárias |
| TB_BANCO | Tabela | SELECT | Cadastro de bancos |
| TB_INSTRUMENTO_COBRANCA | Tabela | SELECT | Tipos de instrumentos de cobrança |
| TbSistemaEmissorBoleto | Tabela | SELECT | Sistemas emissores e flags de validação |
| TbVeiculoLegal | Tabela | SELECT | Veículos legais (beneficiários/cedentes) |
| TbFilial | Tabela | SELECT | Filiais da empresa |
| TbPessoa | Tabela | SELECT | Cadastro de pessoas (pagadores) |
| TbPessoaEndereco | Tabela | SELECT | Endereços de pessoas |
| VwtbContrato | View | SELECT | Contratos (DBGESTAO) |
| TbContrato | Tabela | SELECT | Contratos (várias bases produto) |
| TbContratoFinanceiro | Tabela | SELECT | Contratos financeiros (várias bases) |
| TbParcela | Tabela | SELECT | Parcelas de contratos |
| VwTbParcela | View | SELECT | View de parcelas (DBGESTAO) |
| TbContratoCessao | Tabela | SELECT | Contratos de cessão de crédito |
| TbCarteiraCessao | Tabela | SELECT | Carteiras de cessão FIDC |
| TBCARTEIRACESSAO | Tabela | SELECT | Carteiras de cessão |
| TbConfigCobranca | Tabela | SELECT | Configurações de cobrança (parâmetros CIP) |
| TbControleExecucaoProcesso | Tabela | SELECT | Controle de execução de processos (data CIP) |
| TB_INDICADOR_TX_BANCARIA | Tabela | SELECT | Indicador de cobrança de taxa bancária |
| TB_TAXA_BANCARIA | Tabela | SELECT | Taxas bancárias vigentes |
| TbTipoPiloto | Tabela | SELECT | Pilotos/feature flags ativos |
| TbContratoPrincipal | Tabela | SELECT | Contratos principais (DBCOR) |
| TbProduto | Tabela | SELECT | Produtos financeiros |
| TbConexao | Tabela | SELECT | Conexões de banco de dados |
| TB_PARCELA_BOLETO | Tabela | SELECT | Parcelas de boletos |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbRegistroInstrumentoCobranca | Tabela | INSERT/UPDATE | Inserção e atualização de registros de boleto (hash, linha digitável, dados pagador) |
| TbRegistroInstoCbrnaRclho | Tabela | INSERT/UPDATE | Inserção e atualização de complementos (desconto, multa, mora) |
| TbSituacaoProcessamentoInsto | Tabela | INSERT | Inserção de novos estados de processamento (histórico) |
| TbOcorrenciaRejeicaoPrcso | Tabela | INSERT | Inserção de ocorrências de rejeição |

**Stored Procedures Executadas:**
- **prIncluirIntegracaoPGFTDDA** (CobrDbIntegracaoSPBDS) - INSERT - Inclusão de integração CIP/SPB
- **PrCobrRegBoletoProp** (CobrDbGestaoCobrancaDS) - INSERT/UPDATE - Registro de cobrança própria DDA
- **PrCobrRegBoletoPropVerificaRetBacen** (CobrDbGestaoCobrancaDS) - SELECT - Verificação de retorno Bacen
- **PrSpb_DDA0101_RET** (CobrDbGestaoCobrancaDS) - INSERT - Registro manual de retorno DDA
- **PrIdentificarBancoCarne** (DBCARNE) - SELECT - Identificação de banco para carnê

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `boleto.jrxml` | Leitura | EmissaoBoletoBeanImpl, ImageBoletoRestApi | Template JasperReports para boleto padrão |
| `boleto_bv.jrxml` | Leitura | EmissaoBoletoBeanImpl, ImageBoletoRestApi | Template JasperReports para boleto Banco Votorantim |
| `boleto_santander.jrxml` | Leitura | EmissaoBoletoBeanImpl, ImageBoletoRestApi | Template JasperReports para boleto Santander |
| `carne_bv.jrxml` | Leitura | CarneEndpoint, ImageBoletoRestApi | Template JasperReports para carnê BV |
| `carne_santander.jrxml` | Leitura | CarneEndpoint, ImageBoletoRestApi | Template JasperReports para carnê Santander |
| `s_rel_carne_meios_recebimento.jrxml` | Leitura | CarneEndpoint, RelCarneMeiosRecebimento | Template JasperReports para carnê múltiplos meios |
| `*.pdf` (temporários) | Gravação | ImageBoletoRestApi | PDFs de boletos/carnês gerados em `resources/pdf/` |
| `*.jpg` (código barras) | Gravação | CodigoBarras.java | Imagens de código de barras padrão 2 de 5 intercalado |
| `log4j2.xml` | Leitura | Sistema | Configuração de logging |
| `jaxws.bindings.xml` | Leitura | JAX-WS runtime | Configuração de handlers SOAP |

---

## 10. Filas Lidas

**Não se aplica** - O sistema não consome mensagens de filas JMS/Kafka/RabbitMQ de forma explícita no código analisado. A arquitetura sugere processamento síncrono via webservices SOAP/REST e assíncrono via stored procedures de banco de dados.

---

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Responsável | Descrição |
|--------------|------------|-------------------|-----------|
| Fila de baixa de registro | JMS (implícito) | BaixaRegistroBeanImpl | Inclusão de solicitações de baixa de boleto (referenciado como "inclusão fila baixa registro boleto") |

**Observação:** O código faz referência a "inclusão em fila" para processamento de baixa de registro, mas a implementação específica de JMS não está explícita nos arquivos analisados. A integração com filas provavelmente ocorre via infraestrutura do WebSphere (WAS) configurada externamente.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Classe/Método Responsável | Descrição |
|-----------------|------|--------------------------|-----------|
| **CIP (Câmara Interbancária de Pagamentos)** | SOAP/Stored Procedure | COBRIntegracaoSPBCIPBeanImpl, COBRRegistroCobrancaPropriaBeanImpl | Registro de títulos de cobrança no sistema CIP/SPB, aguarda retorno assíncrono do Bacen |
| **SPB (Sistema de Pagamentos Brasileiro)** | Stored Procedure | COBRRegistroCobrancaPropriaBeanImpl | Integração com sistema de pagamentos para registro de cobrança própria |
| **Banco do Brasil - Registro de Cobrança** | SOAP | RegistroCobrancaService (WSDL) | Registro de boletos via webservice BB (endpoint: https://cobranca.desenv.bb.com.br:7101/registrarBoleto) |
| **Gestão Parceiro Comercial v4** | SOAP | CarneEndpoint | Consulta de dados de parceiros comerciais para operações de cessão (método listarParceirosComerciaisDadosBasicos) |
| **Múltiplos Bancos (Bradesco, Itaú, Santander, Votorantim)** | Arquivo Remessa/Retorno | ConvenioBeanImpl, DadosBoletoBeanImpl | Integração via arquivos de remessa bancária e processamento de retornos (implícito) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada em camadas (domain, business, persistence, integration, ws, rs)
- Uso adequado de padrões JavaEE (EJB, CDI, JAX-WS, JAX-RS)
- Separação clara de responsabilidades entre EJBs
- Uso de DAOs com RowMappers para acesso a dados
- Implementação de adapters para conversão entre entidades
- Documentação via XSD/WSDL bem estruturada
- Uso de feature flags (pilotos) para controle de funcionalidades

**Pontos Negativos:**
- **Código legado comentado extenso** (método solicitarRegistroBoleto v1 com centenas de linhas comentadas)
- **Encodings ruins** em comentários (caracteres Ã¯Â¿Â½ indicando problemas de charset)
- **Mistura de idiomas** (português e inglês) em comentários e nomes de variáveis
- **Logs com System.out.println** misturados com LOGGER adequado
- **Complexidade ciclomática alta** em métodos como BoletoEndpoint.solicitarRegistroBoleto (múltiplos ifs aninhados)
- **Validações inline longas** dificultando leitura
- **Falta de testes unitários** para classes críticas (apenas estrutura de teste presente)
- **Duplicação de código** entre templates JasperReports (boleto_bv, boleto_santander)
- **Métodos muito extensos** (DadosBoletoBeanImpl com 400+ linhas, BoletoEndpoint com 100kb+)
- **Falta de documentação JavaDoc** em classes críticas
- **Hardcoding de valores** (ex: CNPJ avalista "01149953000189", veículo legal padrão 15)
- **Tratamento genérico de exceções** em alguns pontos (catch Exception)

**Recomendações:**
1. Refatorar métodos extensos em métodos menores e mais coesos
2. Remover código comentado obsoleto
3. Padronizar idioma (preferencialmente inglês) em código e comentários
4. Eliminar System.out.println, usar apenas framework de logging
5. Adicionar testes unitários com cobertura adequada
6. Extrair constantes hardcoded para arquivos de configuração
7. Adicionar documentação JavaDoc em classes e métodos públicos
8. Revisar e simplificar lógica condicional complexa
9. Corrigir problemas de encoding em arquivos fonte

---

## 14. Observações Relevantes

1. **Múltiplas Bases de Dados**: O sistema acessa dinamicamente diferentes bases de dados conforme o produto financeiro (DBGESTAOCPC, DBGESTAOLSG, DBGESTAOCPC, DBGESTAOCDCCG, DBGESTAOCDCSG), utilizando enum `ProdutoRSEnum` para roteamento.

2. **Versionamento de APIs**: Coexistência de v1 e v2 de endpoints SOAP (BoletoEndpoint e BoletoEndpointV2), mantendo compatibilidade com sistemas legados.

3. **Ambientes Múltiplos**: WSDLs específicos para DEV, QA, UAT e PRD, com endpoints distintos por ambiente.

4. **Segurança**: Implementação de WS-Security com três níveis (Low/Medium/High) usando UsernameToken e Certificate. Roles JavaEE: "intr-middleware", "saca-geraimagem".

5. **Tratamento de Data CIP**: Cache singleton (DataCache) para otimização de consultas à data CIP, com refresh automático diário.

6. **Migração de Sistema Legado**: Lógica específica para migração de boletos de sistema carnê antigo (DBCARNE) para novo sistema SCCO, com validações de data de implantação.

7. **Contingência**: Sistema possui mecanismos de fallback (ex: registro manual DDA em caso de falha CIP, auto-confirmação para FIDC/cessão).

8. **Auditoria**: Trilha de auditoria completa via header `trilhaAuditoriaHeader` (ticket, sistema, usuário, IP, fase) em todas as operações SOAP.

9. **Geração de Documentos**: Uso intensivo de JasperReports para geração de PDFs, com templates específicos por banco e tipo de documento (boleto individual vs carnê).

10. **Cálculo de Fator de Vencimento**: Implementação do limite FEBRABAN de 21/02/2025 para reinício da contagem de fator de vencimento.

11. **Tratamento Específico por Banco**: Lógica diferenciada para cada banco (BB, Bradesco, Itaú, Santander, Votorantim) em formatação de nosso número, carteira e código de barras.

12. **Stored Procedures Complexas**: Uso extensivo de stored procedures Oracle com múltiplos parâmetros (ex: PrCobrRegBoletoProp com 66 parâmetros), indicando lógica de negócio no banco de dados.

13. **Handlers SOAP**: Implementação de handlers customizados para captura de trilha (CapturadorTrilhaInbound/Outbound), formatação e inicialização de contexto.

14. **Sanitização de Logs**: Uso de sanitizador para prevenir CWE-117 (log injection) em logs de aplicação.

15. **Dependências Corporativas**: Forte dependência de frameworks internos Votorantim (arqt-base, fjee-base), dificultando portabilidade.