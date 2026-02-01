# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de processamento em lote (batch) para gestão de retornos de débitos automáticos em conta corrente. O sistema processa arquivos de retorno enviados por diversos bancos (Banco do Brasil, Itaú, Bradesco, HSBC, Santander, Caixa Econômica Federal), validando registros, atualizando status de débitos e autorizações, persistindo informações em banco de dados Sybase e publicando mensagens em filas MQ para notificação de sistemas origem.

O processamento segue o padrão Spring Batch com leitura de arquivos posicionais, validação de registros (header, detail, footer), tratamento de diferentes layouts bancários (incluindo layout 08 Febraban), e geração de arquivos de registros inválidos.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê arquivos de retorno linha a linha, valida estrutura (cabeçalho/rodapé), verifica conta convênio e número de arquivo |
| **ItemReaderAut** | Lê arquivos de retorno de autorização, similar ao ItemReader mas específico para fluxo de autorização |
| **ItemProcessor** | Processa cada linha do arquivo, identifica tipo (A/F/Z/C/B), carrega dados em RegistroVO usando reflection e properties de layout |
| **ItemProcessorAut** | Processa linhas de arquivo de autorização, carrega dados em RegistroAutDebitoVo |
| **ItemWriter** | Grava registros processados no banco, insere eventos, valida regras de negócio, gera arquivos de inválidos, publica em tópico MQ |
| **ItemWriterAut** | Grava registros de autorização, atualiza eventos e status de autorização |
| **MyResumeStrategy** | Estratégia de recuperação de erros durante processamento batch |
| **RegistroVO** | Value Object principal contendo dados do registro de débito |
| **RegistroAutDebitoVo** | Value Object para registros de autorização de débito |
| **EventoRegistroDebitoDAO** | Persiste e atualiza eventos de registro de débito |
| **EventoRegistroDebitoAutDAO** | Persiste e atualiza eventos de autorização de débito |
| **LogArquivoDebitoDAO** | Gerencia log de arquivos de débito processados |
| **RegistroDebitoDAO** | Operações sobre registros de débito |
| **ControleArquivoDAO** | Controla arquivos processados (header, detail, footer) |
| **QuebraLinhaRetornoUtils** | Utilitário para parsing de linhas de arquivo por banco e layout |
| **SimpleMessageSenderImpl** | Implementação de envio de mensagens JMS para filas MQ |

---

## 3. Tecnologias Utilizadas

- **Java 7** (JDK 7)
- **Spring Batch** (framework de processamento em lote)
- **Spring Framework 2.0** (injeção de dependências, transações)
- **Maven** (gerenciamento de dependências e build)
- **Sybase ASE** (banco de dados principal - DbGestaoDebitoContaCorrente)
- **JDBC** (acesso a dados via DriverManagerDataSource)
- **IBM WebSphere MQ / MQ Series** (mensageria JMS)
- **BV Framework** (framework proprietário Banco Votorantim - batch, logging, MQ integration)
- **Apache Commons IO** (manipulação de arquivos)
- **Apache Commons Lang** (utilitários)
- **Gson** (serialização JSON)
- **Log4j** (logging)
- **JUnit** (testes unitários)

---

## 4. Principais Endpoints REST

não se aplica

---

## 5. Principais Regras de Negócio

1. **Validação de Arquivo de Retorno**: Verifica presença obrigatória de registros tipo A (header), B/F (body) e Z (footer)
2. **Validação de Conta Convênio**: Verifica se conta convênio do arquivo existe no cadastro antes de processar
3. **Validação de Sequência de Arquivo**: Número do arquivo de retorno deve ser sequencial ao último processado (NuArquivoRetorno + 1)
4. **Processamento por Banco**: Suporta layouts específicos de múltiplos bancos (001-BB, 237-Bradesco, 341-Itaú, 033-Santander, 399-HSBC, 104-CEF)
5. **Suporte a Layout 08 Febraban**: Identifica e processa layout versão 08 com regras específicas
6. **Tratamento de CPF/CNPJ**: Remove zeros à esquerda conforme regras específicas por banco
7. **Validação de Código de Retorno**: Verifica se código de retorno do banco existe na tabela de parâmetros
8. **Validação de Registro Origem**: Verifica se registro de débito referenciado existe antes de processar retorno
9. **Processamento de Autorização CEF**: Tratamento especial para códigos AA, AB, 78, BD da Caixa Econômica Federal
10. **Processamento Optin Bradesco**: Validação específica para arquivo de retorno de cadastro optante (tipo C)
11. **Cancelamento de Débito Automático**: Suspende contratos vinculados a autorizações canceladas (tipo B, movimento 1, layout 08)
12. **Geração de Arquivo de Inválidos**: Registros com erro são gravados em arquivo .ERR separado
13. **Movimentação de Arquivos**: Arquivos processados com sucesso vão para pasta "sucesso", com erro para "erro"
14. **Publicação em Tópico MQ**: Envia notificação para sistemas origem (código > 3) com status do débito
15. **Controle de Sumário**: Agrupa registros por código de retorno para geração de sumário estatístico
16. **Validação de Subprodutos**: Verifica se contrato permite uso de código de autorização baseado em lista de subprodutos
17. **Tratamento de Prazo Indeterminado**: Identifica e trata data de vencimento "99999999" como prazo indeterminado

---

## 6. Relação entre Entidades

**Principais Entidades e Relacionamentos:**

- **TbControleArquivoDebitoAtmto**: Controle geral do arquivo processado
  - 1:N → **TbConteudoLinhaArquivo**: Linhas do arquivo
    - 1:1 → **TbLinhaCabecalhoArquivo**: Cabeçalho (tipo A)
    - 1:1 → **TbLinhaDetalheArquivo**: Detalhe (tipo F/B/C)
    - 1:1 → **TbLinhaRodapeArquivo**: Rodapé (tipo Z)

- **TbLogArquivoDebito**: Log de processamento do arquivo
  - N:1 → **TbContaConvenio**: Conta convênio do banco
  - 1:N → **TbEventoRegistroDebito**: Eventos de débito processados
  - 1:N → **TbLogSumarioArquivoDebito**: Sumário estatístico por código retorno
  - 1:N → **TbLogArquivoDebitoTipoInvalido**: Registros inválidos

- **TbRegistroDebito**: Registro de débito original
  - N:1 → **TbContaConvenioSistemaOrigem**: Convênio do sistema origem
  - 1:N → **TbEventoRegistroDebito**: Histórico de eventos do débito

- **TbRegistroAutorizacaoDebito**: Autorização de débito
  - 1:N → **TbEventoRegistroAutorizacaoDbo**: Eventos de autorização
  - 1:N → **TbLogEventoRegistroAtrzoDbto**: Log histórico de eventos
  - 1:N → **TbAutorizacaoDebitoPrpsaCntro**: Vínculo com proposta/contrato

- **TbContratoDebito**: Débito vinculado a contrato
  - N:1 → **TbRegistroAutorizacaoDebito**: Autorização vinculada

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbParametroSistema | tabela | SELECT | Lê data de exercício e parâmetros gerais do sistema |
| TbContaConvenio | tabela | SELECT | Consulta dados de conta convênio por número e banco |
| TbRegistroDebito | tabela | SELECT | Verifica existência de registro de débito original |
| TbRegistroAutorizacaoDebito | tabela | SELECT | Consulta autorizações de débito por CPF/banco/agência/conta ou por código |
| TbRetornoDebitoAutomatico | tabela | SELECT | Valida códigos de retorno de débito automático |
| TbParametroRetornoDebito | tabela | SELECT | Busca mapeamento de código de retorno para sistema origem |
| TbRetornoDebitoSistemaOrigem | tabela | SELECT | Obtém descrição de status de retorno para sistema origem |
| TbContaConvenioSistemaOrigem | tabela | SELECT | Consulta dados de convênio do sistema origem |
| TbSistemaOrigem | tabela | SELECT | Obtém informações do sistema origem |
| TbEventoRegistroDebito | tabela | SELECT | Verifica eventos já processados para evitar duplicidade |
| TbEventoRegistroAutorizacaoDbo | tabela | SELECT | Consulta eventos de autorização existentes |
| TbStatusAutorizacaoDebito | tabela | SELECT | Valida códigos de status de autorização |
| TbContrato (DbGestaoCP) | tabela | SELECT | Verifica dados de contrato |
| TbProposta (DbCred) | tabela | SELECT | Valida subproduto da proposta |
| TbParametroAutorizacaoDebito | tabela | SELECT | Consulta modelo de autorização por banco |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbControleArquivoDebitoAtmto | tabela | INSERT | Insere controle de arquivo processado |
| TbConteudoLinhaArquivo | tabela | INSERT | Insere conteúdo de cada linha do arquivo |
| TbLinhaCabecalhoArquivo | tabela | INSERT | Insere dados do cabeçalho do arquivo |
| TbLinhaDetalheArquivo | tabela | INSERT | Insere dados de detalhe do arquivo |
| TbLinhaRodapeArquivo | tabela | INSERT | Insere dados do rodapé do arquivo |
| TbLogArquivoDebito | tabela | INSERT/UPDATE | Insere log de arquivo e atualiza com dados do footer |
| TbEventoRegistroDebito | tabela | INSERT | Insere eventos de processamento de débito |
| TbEventoRegistroAutorizacaoDbo | tabela | INSERT/UPDATE | Insere e atualiza eventos de autorização |
| TbLogEventoRegistroAtrzoDbto | tabela | INSERT | Insere log histórico de eventos de autorização |
| TbLogSumarioArquivoDebito | tabela | INSERT | Insere sumário estatístico do arquivo processado |
| TbLogArquivoDebitoTipoInvalido | tabela | INSERT | Registra linhas inválidas do arquivo |
| TbContaConvenio | tabela | UPDATE | Atualiza número de arquivo de envio e retorno |
| TbRegistroDebito | tabela | UPDATE | Atualiza status de processamento do registro |
| TbContratoDebito | tabela | UPDATE | Suspende débito ativo e define motivo de suspensão |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| conf.properties | leitura | ItemProcessor, ItemWriter | Configuração de layouts de arquivo por banco |
| conf-layout-08.properties | leitura | ItemProcessor, ItemWriter | Configuração específica para layout 08 Febraban |
| conf_aut.properties | leitura | ItemProcessorAut, ItemWriterAut | Configuração de layouts para autorização |
| subproduto.properties | leitura | ContratoDAO | Lista de códigos de subprodutos permitidos |
| Arquivos de retorno bancários (*.txt) | leitura | ItemReader, ItemReaderAut | Arquivos posicionais de retorno dos bancos (diretório fileDir) |
| Arquivos de erro (*.ERR) | gravação | ItemWriter, ItemWriterAut | Registros inválidos separados (path_invalido) |
| log4j.xml | leitura | Framework | Configuração de logging |
| bv-framework-integration-mq-conf.properties | leitura | Framework MQ | Configuração de integração com MQ |
| catalogo-filas.xml | leitura | Framework MQ | Catálogo de filas JMS |

**Diretórios de Processamento:**
- **path_recebido**: Arquivos recebidos para processamento
- **path_sucesso**: Arquivos processados com sucesso
- **path_erro**: Arquivos com erro no processamento
- **path_invalido**: Arquivos com registros inválidos (.ERR)

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

| Nome da Fila | Tipo | Descrição |
|--------------|------|-----------|
| TP.VAREJO.RETORNO_DEBITO_EM_CONTA | Tópico JMS (IBM MQ) | Publica notificações de retorno de débito para sistemas origem com código > 3. Mensagens em formato JSON contendo dados do débito/autorização processado |

**Operações publicadas:**
- **"debitar"**: Retorno de débito processado
- **"autenticar"**: Retorno de autorização (CEF ou cadastro optante)

**Header Properties:**
- `operacao`: tipo de operação (debitar/autenticar)
- `siglasistema`: sigla do sistema origem em lowercase

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| IBM WebSphere MQ | Mensageria | Publicação de mensagens em tópico para notificar sistemas origem sobre status de débitos |
| Bancos Depositários | Arquivo | Recebe arquivos de retorno de débito automático (BB, Itaú, Bradesco, HSBC, Santander, CEF) |
| DbGestaoCP | Banco de Dados | Consulta dados de contrato (TbContrato) |
| DbCred | Banco de Dados | Consulta dados de proposta (TbProposta) para validação de subproduto |

---

## 13. Avaliação da Qualidade do Código

**Nota: 4/10**

**Justificativa:**

**Pontos Negativos:**
- **Código legado com má qualidade**: Uso excessivo de reflection, strings concatenadas para SQL (vulnerável a SQL injection), mistura de português e inglês
- **Violações graves de segurança**: Credenciais hardcoded (ItemStatus.java), SQL injection via concatenação de strings
- **Falta de padrões**: Inconsistência entre classes similares (ItemWriter vs ItemWriterAut), código duplicado
- **Métodos muito longos**: handleWrite com centenas de linhas, múltiplas responsabilidades
- **Tratamento inadequado de exceções**: Catch genérico com re-throw, perda de contexto
- **Comentários em português**: Dificulta manutenção internacional
- **Código morto**: Métodos comentados, variáveis não utilizadas
- **Falta de testes**: Apenas classes de teste vazias
- **Acoplamento alto**: Dependência direta de múltiplos DAOs, lógica de negócio no Writer
- **Magic numbers e strings**: Constantes espalhadas pelo código sem centralização adequada

**Pontos Positivos:**
- Uso de Spring Batch para processamento estruturado
- Separação de responsabilidades em DAOs
- Uso de Value Objects para transporte de dados
- Logging estruturado com BVLogger
- Tratamento de múltiplos layouts bancários

---

## 14. Observações Relevantes

1. **Arquitetura Legada**: Sistema desenvolvido em padrões antigos (Spring 2.0, Java 7), necessita modernização urgente
2. **Segurança Crítica**: Credenciais expostas no código-fonte (ItemStatus.java) representam risco grave de segurança
3. **Layouts Posicionais**: Sistema processa arquivos de texto com campos em posições fixas, configurados via properties
4. **Suporte Multi-Banco**: Implementa lógica específica para 6 bancos diferentes com variações de layout
5. **Processamento Transacional**: Usa Spring Batch com controle transacional, mas ItemWriterAut usa autoCommit=true
6. **Estratégia de Recuperação**: MyResumeStrategy permite continuar processamento mesmo com erros (canResume sempre true)
7. **Geração de Sequenciais**: Usa BatchKeyGenerator customizado para gerar IDs sequenciais
8. **Encoding**: Arquivos configurados com charset ISO-8859-1 (iso_1)
9. **Ambiente**: Configurações apontam para ambiente de desenvolvimento (ptasybdes15.bvnet.bv:6010)
10. **Dependências Proprietárias**: Forte dependência do BV Framework, dificultando portabilidade
11. **Processamento de Autorização**: Dois fluxos distintos (retorno normal e retorno de autorização) com jobs separados
12. **Validação de Data**: Sistema valida prazo mínimo entre data de processamento e vencimento
13. **Tratamento de Registros Tipo B**: Arquivos legados do Banco do Brasil têm registros tipo B removidos automaticamente
14. **Notificação Assíncrona**: Sistemas origem são notificados via MQ apenas ao final do processamento bem-sucedido