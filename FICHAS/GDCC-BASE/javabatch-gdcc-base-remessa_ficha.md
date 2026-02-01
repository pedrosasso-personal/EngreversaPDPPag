# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java responsável pela geração de arquivos de remessa de débito automático em conta corrente para diversos bancos (Banco do Brasil, Itaú, Bradesco, Santander, HSBC e Caixa Econômica Federal). O sistema consulta registros de débito pendentes no banco de dados, valida as informações, gera arquivos posicionais conforme layout específico de cada banco e registra logs de processamento. Também possui funcionalidade para processar autorizações de débito.

O sistema opera em modo batch, lendo registros do banco de dados Sybase, processando-os e gerando arquivos texto com layout posicional de 150 caracteres por linha, contendo cabeçalho, detalhes e rodapé.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê registros de débito do banco de dados que estão prontos para processamento |
| **ItemReaderAut** | Lê registros de autorização de débito pendentes de envio |
| **ItemProcessor** | Processa registros de débito, adicionando data de geração |
| **ItemProcessorAut** | Processa registros de autorização de débito |
| **ItemWriter** | Gera arquivos de remessa posicionais para os bancos e persiste logs |
| **ItemWriterAut** | Gera arquivos de remessa de autorização e persiste logs |
| **RegistroVO** | Value Object contendo dados do registro de débito |
| **RegistroAutDebitoVo** | Value Object para autorização de débito |
| **EventoRegistroDebitoDAO** | Insere eventos de registro de débito |
| **LogArquivoDebitoDAO** | Gerencia logs de arquivos de débito gerados |
| **ControleArquivoDAO** | Controla metadados dos arquivos gerados |
| **QuebraLinhaRemessaUtils** | Utilitário para parsing de linhas de arquivo conforme layout do banco |
| **BatchKeyGenerator** | Gerador de sequenciais para chaves primárias |
| **CommonConstants** | Constantes do sistema (códigos de banco, status, mensagens) |

---

## 3. Tecnologias Utilizadas

- **Java** (versão não especificada explicitamente)
- **Maven** - Gerenciamento de dependências e build
- **Spring Framework 2.0** - Injeção de dependências e configuração
- **Spring Batch** (framework BV customizado: `bv-framework-batch.standalone`)
- **Sybase ASE** - Banco de dados (driver jconn4 versão 7.07-SP136)
- **JDBC** - Acesso a dados
- **Log4j** - Logging
- **JUnit** - Testes unitários
- **Apache Commons Lang** - Utilitários
- **Apache Commons IO** - Manipulação de arquivos

---

## 4. Principais Endpoints REST

não se aplica

---

## 5. Principais Regras de Negócio

1. **Validação de Data de Vencimento**: Verifica se a diferença entre a data de processamento e a data de vencimento do débito é maior ou igual ao prazo mínimo configurado na conta convênio
2. **Geração de Arquivo por Conta Convênio**: Cada conta convênio gera um arquivo separado
3. **Controle de Sequencial de Arquivo**: Incrementa número de arquivo de envio para cada conta convênio
4. **Validação de Código de Autorização**: Para layout 08 e Caixa Econômica Federal, valida existência de código de autorização de débito
5. **Tratamento de Registros Inválidos**: Registros com data de vencimento inválida ou sem autorização são separados em arquivo de inválidos
6. **Cálculo de Custo**: Aplica custo de débito conforme flag `FlGeraCusto` do retorno
7. **Formatação Específica por Banco**: Aplica regras de formatação de CPF/CNPJ, conta corrente e outros campos conforme especificação de cada banco
8. **Layout Versão 08**: Suporta layout especial versão 08 com campos adicionais (TipoOperacao, UsaChequeEspecial, PermiteDebitoParcial, prazo indeterminado)
9. **Tipos de Movimento**: Diferencia agendamento (tipo 0 ou 5) de cancelamento (tipo 1)
10. **Status de Processamento**: Controla status dos registros (aguardando geração=3, processando=5, gerado=1, erro=8)

---

## 6. Relação entre Entidades

**Principais entidades e relacionamentos:**

- **TbContaConvenio**: Representa convênios com bancos para débito automático
  - Relaciona-se com **TbContaConvenioSistemaOrigem** (1:N)
  
- **TbRegistroDebito**: Registro individual de débito a ser processado
  - Pertence a **TbContaConvenioSistemaOrigem** (N:1)
  - Gera **TbEventoRegistroDebito** (1:N)
  
- **TbLogArquivoDebito**: Log de arquivo gerado
  - Relaciona-se com **TbContaConvenio** (N:1)
  - Contém **TbEventoRegistroDebito** (1:N)
  - Possui **TbLogSumarioArquivoDebito** (1:N)
  
- **TbRegistroAutorizacaoDebito**: Autorização de débito do cliente
  - Gera **TbEventoRegistroAutorizacaoDbo** (1:N)
  - Relaciona-se com **tbAutorizacaoDebitoPrpsaCntro** para vincular proposta/contrato

- **TbControleArquivoDebitoAtmto**: Controle de arquivos processados
  - Contém **TbConteudoLinhaArquivo** (1:N)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbContaConvenio | tabela | SELECT | Consulta dados do convênio (prazo mínimo/máximo, número arquivo, custos) |
| TbContaConvenioSistemaOrigem | tabela | SELECT | Relacionamento entre conta convênio e sistema origem |
| TbRegistroDebito | tabela | SELECT | Busca registros de débito prontos para processamento (status 3 ou 5) |
| TbParametroSistema | tabela | SELECT | Obtém data de exercício do sistema |
| TbRetornoDebitoSistemaOrigem | tabela | SELECT | Consulta flag de geração de custo |
| TbParametroRetornoDebito | tabela | SELECT | Parâmetros de retorno por convênio |
| TbRegistroAutorizacaoDebito | tabela | SELECT | Consulta autorizações de débito pendentes de envio |
| TbEventoRegistroAutorizacaoDbo | tabela | SELECT | Eventos de autorização de débito |
| tbAutorizacaoDebitoPrpsaCntro | tabela | SELECT | Vinculação de autorização com proposta/contrato |
| TbContrato (DbGestaoCP) | tabela | SELECT | Validação de contrato |
| TbProposta (DbCRED) | tabela | SELECT | Validação de subproduto da proposta |
| TbVeiculoLegal (dbcor) | tabela | SELECT | Nome da empresa |
| TbBanco (dbcor) | tabela | SELECT | Nome do banco |
| TbParametroAutorizacaoDebito | tabela | SELECT | Modelo de autorização por banco |
| TbStatusAutorizacaoDebito | tabela | SELECT | Validação de código de status |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbEventoRegistroDebito | tabela | INSERT | Insere evento de processamento do registro de débito |
| TbLogArquivoDebito | tabela | INSERT/UPDATE | Insere/atualiza log do arquivo gerado |
| TbLogSumarioArquivoDebito | tabela | INSERT | Insere sumário consolidado por banco e código retorno |
| TbLogArquivoDebitoTipoInvalido | tabela | INSERT | Registra linhas inválidas do arquivo |
| TbRegistroDebito | tabela | UPDATE | Atualiza status do registro (CdStatusDebito) |
| TbContaConvenio | tabela | UPDATE | Atualiza número do arquivo de envio/retorno |
| TbEventoRegistroAutorizacaoDbo | tabela | INSERT/UPDATE | Insere/atualiza eventos de autorização |
| TbLogEventoRegistroAtrzoDbto | tabela | INSERT | Log de eventos de autorização |
| TbRegistroAutorizacaoDebito | tabela | UPDATE | Atualiza status de processamento da autorização |
| TbControleArquivoDebitoAtmto | tabela | INSERT | Controle de arquivos processados |
| TbConteudoLinhaArquivo | tabela | INSERT | Conteúdo das linhas dos arquivos |
| TbLinhaCabecalhoArquivo | tabela | INSERT | Dados do cabeçalho do arquivo |
| TbLInhaDetalheArquivo | tabela | INSERT | Dados das linhas de detalhe |
| TbLInhaRodapeArquivo | tabela | INSERT | Dados do rodapé do arquivo |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| conf.properties | leitura | ItemWriter (handleInit) | Configuração de layouts de arquivo por banco |
| conf-layout-08.properties | leitura | ItemWriter (handleInit) | Configuração de layouts versão 08 |
| conf_aut.properties | leitura | ItemWriterAut (handleInit) | Configuração para arquivos de autorização |
| subproduto.properties | leitura | ContratoDAO | Lista de códigos de subprodutos permitidos |
| DBT{banco}{convenio}{sequencial}.REM | gravação | ItemWriter | Arquivo de remessa gerado (padrão geral) |
| BBM.TRN.DBT627.BVT{convenio}.T{hora} | gravação | ItemWriter | Arquivo de remessa Banco do Brasil |
| E9C.FTG.VIND / E9C.IED.H002 | gravação | ItemWriter | Arquivo de remessa HSBC |
| DEB_104_{conta}_{data}.REM.32529 | gravação | ItemWriter | Arquivo de remessa Caixa Econômica Federal |
| {arquivo}.ERR_Ivalido | gravação | ItemWriter | Arquivo com registros inválidos |
| log/robo.log | gravação | Log4j | Log de execução do sistema |
| log/statistics-{executionId}.log | gravação | Log4j | Log de estatísticas de execução |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **Bancos Parceiros** | Arquivo | Geração de arquivos de débito automático para: Banco do Brasil (001), Santander (033), Itaú (341), Bradesco (237), HSBC (399), Caixa Econômica Federal (104) |
| **DbGestaoDebitoContaCorrente** | Banco de dados Sybase | Base principal de gestão de débito em conta corrente |
| **DbGestaoCP** | Banco de dados Sybase | Consulta dados de contratos |
| **DbCRED** | Banco de dados Sybase | Consulta dados de propostas |
| **dbcor** | Banco de dados Sybase | Consulta dados corporativos (bancos, veículos legais) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 4/10**

**Justificativa:**

**Pontos Negativos:**
- **Código legado com problemas graves**: Comentários indicam correções para resolver problemas do SonarQube de forma superficial (ex: métodos `erroSonarZeros`, `erroSonarBrancos`)
- **Mistura de idiomas**: Código mescla português e inglês de forma inconsistente
- **Falta de tratamento de exceções adequado**: Diversos `printStackTrace()` e tratamentos genéricos
- **Métodos muito longos**: Classes como `ItemWriter` possuem métodos com centenas de linhas
- **Acoplamento alto**: Lógica de negócio misturada com acesso a dados e geração de arquivos
- **Falta de testes**: Apenas testes de integração básicos
- **Hardcoded values**: Strings de conexão, paths e configurações fixas no código
- **Uso de reflection desnecessário**: Complexidade excessiva na geração de linhas
- **Comentários em português com encoding incorreto**: Caracteres especiais mal formatados
- **Violações de princípios SOLID**: Classes com múltiplas responsabilidades
- **Código comentado**: Diversos trechos de código comentado sem remoção

**Pontos Positivos:**
- Separação em camadas (DAO, VO, batch)
- Uso de framework batch estruturado
- Configuração externalizada em properties
- Logging implementado

---

## 14. Observações Relevantes

1. **Framework Proprietário**: Sistema utiliza framework batch customizado da BV Sistemas (`bv-framework-batch.standalone`)

2. **Múltiplos Layouts**: Suporta dois layouts principais (padrão e versão 08) com diferenças significativas nos campos

3. **Processamento por Conta Convênio**: Gera um arquivo separado para cada conta convênio, mudando de arquivo quando detecta mudança no código da conta

4. **Controle de Sequencial**: Utiliza procedure `prObterSequencialDisponivel` para geração de chaves primárias

5. **Arquivos Posicionais**: Todos os arquivos gerados seguem formato posicional de 150 caracteres por linha

6. **Tratamento Especial CEF**: Caixa Econômica Federal possui lógica específica diferenciada dos demais bancos

7. **Validação de Subprodutos**: Apenas determinados subprodutos (configurados em properties) permitem uso de código de autorização

8. **Ambiente de Execução**: Sistema preparado para execução via UC4 (scheduler) com parâmetros de linha de comando

9. **Encoding**: Sistema possui problemas de encoding (ISO-8859-1) com caracteres acentuados

10. **Transações**: Configurado como `noTransactionJobTemplate`, indicando que não utiliza transações gerenciadas pelo Spring

11. **Banco de Dados Sybase**: Utiliza sintaxe específica do Sybase (ex: `getdate()`, `replicate()`, notação `..` para schemas)

12. **Código de Retorno**: Sistema define códigos de retorno específicos (10-70) para diferentes tipos de erro