# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de processamento batch Java para gestão de débito em conta corrente (GDCC), responsável por gerar arquivos de remessa e processar arquivos de retorno de débitos automáticos junto a diversos bancos (Banco do Brasil, Itaú, Bradesco, HSBC, Santander). O sistema utiliza Spring Batch para processamento em lote, realizando leitura de registros do banco de dados, geração de arquivos posicionais conforme layout de cada banco, e processamento de arquivos de retorno para atualização do status dos débitos.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** (remessa) | Lê registros de débito do banco de dados para geração de arquivo de remessa |
| **ItemProcessor** (remessa) | Processa e valida registros de débito antes da gravação |
| **ItemWriter** (remessa) | Gera arquivos de remessa no formato posicional específico de cada banco |
| **ItemReader** (retorno) | Lê linhas de arquivos de retorno recebidos dos bancos |
| **ItemProcessor** (retorno) | Processa e valida linhas do arquivo de retorno |
| **ItemWriter** (retorno) | Atualiza status dos débitos no banco de dados com base no retorno |
| **RegistroVO** | Value Object para transporte de dados de registro de débito |
| **RegistroAutDebitoVo** | Value Object para autorização de débito |
| **LogArquivoDebitoDAO** | Gerencia logs de arquivos de débito processados |
| **EventoRegistroDebitoDAO** | Registra eventos de processamento de débitos |
| **QuebraLinhaRemessaUtils** | Utilitário para parsing de linhas de arquivo de remessa |
| **QuebraLinhaRetornoUtils** | Utilitário para parsing de linhas de arquivo de retorno |

---

## 3. Tecnologias Utilizadas

- **Java** (versão não especificada explicitamente)
- **Spring Batch** - Framework para processamento em lote
- **Spring Framework** - Injeção de dependência e configuração
- **Maven** - Gerenciamento de dependências e build
- **Sybase ASE** - Banco de dados (via JTDS driver)
- **JTDS** - Driver JDBC para Sybase
- **Bitronix** - Gerenciador de transações JTA
- **Apache Commons IO** - Utilitários para manipulação de arquivos
- **Apache Commons Lang** - Utilitários gerais
- **Log4j** - Framework de logging (via BVLogger)

---

## 4. Principais Endpoints REST

não se aplica

---

## 5. Principais Regras de Negócio

1. **Validação de Data de Vencimento**: Verifica se a diferença entre data de processamento e data de vencimento respeita o prazo mínimo configurado na conta convênio
2. **Geração de Arquivo por Banco**: Cada banco possui layout específico (posicional) para arquivo de remessa
3. **Controle de Sequencial de Arquivo**: Número sequencial de arquivo é incrementado a cada geração
4. **Validação de Conta Convênio**: Verifica existência da conta convênio antes de processar retorno
5. **Validação de Código de Retorno**: Valida se código de retorno do banco existe na tabela de parâmetros
6. **Registro de Eventos**: Cada processamento gera evento com status (gerado, processado, erro)
7. **Tratamento de Registros Inválidos**: Registros com erro são gravados em arquivo separado (.ERR)
8. **Uso de Código de Autorização**: Para subprodutos específicos, utiliza código de autorização de débito
9. **Atualização de Status**: Status dos registros é atualizado conforme processamento (aguardando, processando, gerado, erro)
10. **Sumário de Arquivo**: Gera sumário com totalizadores por código de retorno

---

## 6. Relação entre Entidades

**Principais Entidades e Relacionamentos:**

- **TbRegistroDebito**: Registro principal de débito
  - Relaciona-se com TbContaConvenioSistemaOrigem (N:1)
  - Relaciona-se com TbEventoRegistroDebito (1:N)
  
- **TbEventoRegistroDebito**: Eventos de processamento do débito
  - Relaciona-se com TbRegistroDebito (N:1)
  - Relaciona-se com TbLogArquivoDebito (N:1)
  
- **TbLogArquivoDebito**: Log de arquivos processados
  - Relaciona-se com TbContaConvenio (N:1)
  - Relaciona-se com TbEventoRegistroDebito (1:N)
  
- **TbContaConvenio**: Conta convênio com banco
  - Relaciona-se com TbContaConvenioSistemaOrigem (1:N)
  
- **TbRegistroAutorizacaoDebito**: Autorização de débito em conta
  - Relaciona-se com TbEventoRegistroAutorizacaoDbo (1:N)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbRegistroDebito | tabela | SELECT | Registros de débito a serem processados |
| TbContaConvenio | tabela | SELECT | Contas convênio cadastradas |
| TbContaConvenioSistemaOrigem | tabela | SELECT | Relacionamento conta convênio com sistema origem |
| TbParametroSistema | tabela | SELECT | Parâmetros gerais do sistema (data exercício) |
| TbRetornoDebitoAutomatico | tabela | SELECT | Códigos de retorno válidos por banco |
| TbVeiculoLegal | tabela | SELECT | Dados da empresa (razão social) |
| TbBanco | tabela | SELECT | Dados dos bancos |
| TbContrato | tabela | SELECT | Contratos para validação de uso de código autorização |
| TbProposta | tabela | SELECT | Propostas relacionadas a contratos |
| TbRegistroAutorizacaoDebito | tabela | SELECT | Registros de autorização de débito |
| TbEventoRegistroAutorizacaoDbo | tabela | SELECT | Eventos de autorização de débito |
| TbStatusAutorizacaoDebito | tabela | SELECT | Status de autorização válidos |
| TbParametroAutorizacaoDebito | tabela | SELECT | Parâmetros de autorização por banco |
| TbParcelaDebito | tabela | SELECT | Parcelas de débito |
| TbContratoPrincipal | tabela | SELECT | Contratos principais |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbRegistroDebito | tabela | UPDATE | Atualiza status do registro de débito |
| TbEventoRegistroDebito | tabela | INSERT | Insere eventos de processamento |
| TbLogArquivoDebito | tabela | INSERT/UPDATE | Registra e atualiza logs de arquivos |
| TbLogArquivoDebitoTipoInvalido | tabela | INSERT | Registra linhas inválidas do arquivo |
| TbLogSumarioArquivoDebito | tabela | INSERT | Insere sumário de processamento |
| TbContaConvenio | tabela | UPDATE | Atualiza número de arquivo enviado/retornado |
| TbControleArquivoDebitoAtmto | tabela | INSERT | Controle de arquivos processados |
| TbConteudoLinhaArquivo | tabela | INSERT | Conteúdo das linhas dos arquivos |
| TbLinhaCabecalhoArquivo | tabela | INSERT | Dados do cabeçalho do arquivo |
| TbLinhaDetalheArquivo | tabela | INSERT | Dados de detalhe do arquivo |
| TbLinhaRodapeArquivo | tabela | INSERT | Dados do rodapé do arquivo |
| TbEventoRegistroAutorizacaoDbo | tabela | INSERT/UPDATE | Eventos de autorização de débito |
| TbLogEventoRegistroAtrzoDbto | tabela | INSERT | Log de eventos de autorização |
| TbRegistroAutorizacaoDebito | tabela | UPDATE | Atualiza status de processamento da autorização |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| conf.properties | leitura | ItemWriter, ItemProcessor | Configurações de layout dos arquivos por banco |
| conf_aut.properties | leitura | ItemWriterAut, ItemProcessorAut | Configurações para autorização de débito |
| subproduto.properties | leitura | ContratoDAO | Códigos de subprodutos que permitem uso de código autorização |
| DBT{banco}{convenio}{seq}.REM | gravação | ItemWriter (remessa) | Arquivo de remessa gerado para envio ao banco |
| DBT{banco}{convenio}{seq}.RET | leitura | ItemReader (retorno) | Arquivo de retorno recebido do banco |
| *.ERR | gravação | ItemWriter | Arquivo com registros inválidos |
| *.ERR_Invalido | gravação | ItemWriter | Arquivo com registros inválidos (remessa) |
| BBM.TRN.DBT627.BVT*.T* | gravação | ItemWriter | Arquivo específico Banco do Brasil |
| E9C.FTG.VIND / E9C.IED.H002 | gravação | ItemWriter | Arquivo específico HSBC |
| DM.REMS.*.CONNECT | gravação | ItemWriter | Arquivo específico Itaú |

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
| Banco do Brasil (001) | Arquivo | Troca de arquivos de débito automático |
| Santander (033) | Arquivo | Troca de arquivos de débito automático |
| Itaú (341) | Arquivo | Troca de arquivos de débito automático |
| Bradesco (237) | Arquivo | Troca de arquivos de débito automático |
| HSBC (399) | Arquivo | Troca de arquivos de débito automático |
| Sybase ASE | Banco de Dados | Base de dados principal (DbGestaoDebitoContaCorrente) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 5/10**

**Justificativa:**

**Pontos Positivos:**
- Uso adequado de padrões Spring Batch (Reader/Processor/Writer)
- Separação de responsabilidades em DAOs
- Uso de Value Objects para transporte de dados
- Tratamento de exceções customizado

**Pontos Negativos:**
- **Código comentado**: Diversas seções de código comentado sem remoção
- **Complexidade excessiva**: Classes ItemWriter com mais de 800 linhas
- **Duplicação de código**: Lógica similar entre remessa e remessa_aut, retorno e retorno_aut
- **Hardcoded values**: Muitos valores fixos no código (códigos de banco, paths)
- **Falta de documentação**: Javadoc incompleto ou ausente
- **Tratamento de exceções genérico**: Muitos catch(Exception) sem tratamento específico
- **Uso de System.out.println**: Misturado com logger
- **Métodos muito longos**: Métodos com mais de 100 linhas
- **Acoplamento alto**: Classes com muitas dependências diretas
- **Falta de testes unitários**: Apenas classes de teste comentadas como NAO_ENVIAR
- **SQL em strings**: Queries SQL construídas manualmente em strings
- **Magic numbers**: Números mágicos sem constantes nomeadas

---

## 14. Observações Relevantes

1. **Arquitetura Batch**: Sistema segue padrão Spring Batch com commit interval de 100 registros
2. **Multi-banco**: Suporta múltiplos bancos com layouts diferentes através de arquivos de configuração
3. **Controle Transacional**: Utiliza Bitronix para gerenciamento de transações JTA
4. **Resiliência**: Implementa MyResumeStrategy para permitir continuação após erros
5. **Auditoria**: Registra todas as operações em tabelas de log e evento
6. **Versionamento**: Sistema versionado (18.11.3.DEB35-208.1)
7. **Ambiente**: Configurações separadas para QA, UAT e Produção
8. **Encoding**: Arquivos XML em ISO-8859-1
9. **Monitoramento**: Integração com sistema de monitoramento JMX (bv-monitoring)
10. **Geração de Sequencial**: Utiliza stored procedure prObterSequencialDisponivel para geração de IDs
11. **Movimentação de Arquivos**: Arquivos processados são movidos entre diretórios (recebido, sucesso, erro, invalido)
12. **Exit Codes**: Sistema retorna códigos específicos para diferentes tipos de erro (10-70)