# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de processamento em lote (batch) desenvolvido em Java com Spring Batch para geração de arquivos CNAB (Centro Nacional de Automação Bancária) de retorno e extrato. O sistema processa arquivos bancários no padrão CNAB 240, realizando a leitura de dados de pagamentos e boletos do banco de dados, gerando arquivos de retorno formatados para os bancos Votorantim e Itaú. Possui dois módulos principais: um para geração de arquivos de retorno de pagamentos e outro para geração de extratos bancários diários.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê arquivos processados do banco de dados e prepara dados para processamento |
| **ItemProcessor** | Processa os dados lidos, gerando o conteúdo dos arquivos CNAB de retorno |
| **ItemWriter** | Grava os arquivos CNAB gerados no sistema de arquivos e atualiza o banco de dados |
| **ArquivoCnabBean** | Regras de negócio para geração de arquivos CNAB, coordena DAOs e parsers |
| **SpagDaoImpl** | Acesso a dados do banco DBSPAG (arquivos, lotes, detalhes) |
| **GlobalDaoImpl** | Acesso a dados do banco DBGLOBAL (domínios de bancos) |
| **CnabLayoutVotorantimObjectTranslator** | Traduz objetos de negócio para layout CNAB do Banco Votorantim |
| **CnabLayoutItauObjectTranslator** | Traduz objetos de negócio para layout CNAB do Banco Itaú |
| **ExtratoMovimentacaoDAOImpl** | Acesso aos dados de extrato bancário via stored procedure |
| **SpagProcessamentoDAOImpl** | Gerencia registros de processamento de arquivos de extrato |
| **ArquivoService** | Serviço para geração de arquivos de extrato CNAB |

---

## 3. Tecnologias Utilizadas

- **Java 1.6**
- **Spring Framework 2.0.2** (Core, JDBC)
- **Spring Batch** (framework BV Sistemas - bv-framework-batch.standalone)
- **Maven** (gerenciamento de dependências e build)
- **FFPojo** (mapeamento de arquivos de texto posicional)
- **Apache Commons Lang 3**
- **Bitronix** (gerenciador de transações JTA)
- **JDBC Drivers:**
  - Sybase jConnect 4 (jconn4)
  - Microsoft SQL Server (mssqlserver)
- **BV Crypto** (criptografia de senhas)
- **JUnit** (testes)

---

## 4. Principais Endpoints REST

não se aplica

---

## 5. Principais Regras de Negócio

1. **Processamento de Arquivos CNAB**: Busca arquivos com processamento finalizado (situação específica) nos últimos 2 dias que ainda não possuem arquivo de retorno gerado
2. **Geração de Layout Bancário**: Converte dados do banco para layouts específicos (Votorantim ou Itaú) conforme padrão CNAB 240
3. **Validação de Registros**: Separa registros aceitos e recusados com base em códigos de ocorrência de pagamento
4. **Nomenclatura de Arquivos**: Gera nomes padronizados para arquivos de retorno incluindo CNPJ, data/hora e tipo
5. **Ajuste de Código de Barras**: Para extratos, converte linha digitável em código de barras (44 posições)
6. **Controle de Processamento**: Registra data/hora de processamento e quantidade de registros processados
7. **Segmentação de Detalhes**: Organiza detalhes em segmentos A, B, C, Z, J e J52 conforme tipo de operação
8. **Tratamento de Bancos**: Diferencia processamento entre Banco Votorantim (655) e Banco BV (413)
9. **Geração de Extrato Diário**: Processa extratos bancários desde a última data de processamento ou D-1 se for o primeiro
10. **Validação de Domingos**: Para extratos, se a data cair em domingo, ajusta para sábado à meia-noite

---

## 6. Relação entre Entidades

**Hierarquia de Entidades CNAB:**

- **CnabArquivoDTO** (Arquivo CNAB)
  - Contém: CnabPessoaConfigDTO, CnabArquivoSituacaoDTO
  - Relacionamento 1:N com **CnabArquivoLoteDTO** (Lote)
    - Relacionamento 1:N com **CnabArquivoDetalheDTO** (Detalhe)
      - Contém: CnabArquivoDetalheSituacaoDTO

**Entidades de Processamento:**

- **ArquivoProcessado**: Representa arquivo processado com estatísticas
- **InputStatementEntry**: Dados de entrada para processamento de extrato
- **ArquivoExtratoInfo**: Informações consolidadas para geração de extrato

**Entidades de Layout CNAB:**

- Hierarquia abstrata: **CnabLayoutPojoAbstractClass** implementa **CnabLayoutPojoInteface**
- Implementações específicas por banco (Votorantim/Itaú) e tipo de registro (Header, Lote, Detalhe, Trailler)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|----------------------------|------|----------|-----------------|
| TbArquivoCnab | tabela | SELECT | Dados principais dos arquivos CNAB |
| TbArquivoCnabPessoa | tabela | SELECT | Informações da pessoa/empresa do arquivo |
| TbArquivoCnabProcessamento | tabela | SELECT | Controle de processamento dos arquivos |
| TbArquivoCnabFinanceiro | tabela | SELECT | Dados financeiros do arquivo (agência, conta) |
| TbArquivoCnabLote | tabela | SELECT | Informações dos lotes dentro do arquivo |
| TbArquivoCnabLotePessoa | tabela | SELECT | Dados da pessoa do lote |
| TbArquivoCnabLoteFinanceiro | tabela | SELECT | Dados financeiros do lote |
| TbArquivoCnabLoteEndereco | tabela | SELECT | Endereço associado ao lote |
| TbArquivoCnabDetalhe | tabela | SELECT | Registros de detalhe do arquivo |
| TbArquivoCnabDetalheDocumento | tabela | SELECT | Documentos/pagamentos dos detalhes |
| TbArquivoCnabDetalhePessoa | tabela | SELECT | Dados de pessoas nos detalhes (favorecido, pagador) |
| TbCnabPessoaConfiguracao | tabela | SELECT | Configurações de pessoa para CNAB |
| TbCnabTipoTransferencia | tabela | SELECT | Tipos de transferência CNAB |
| VwBancoBasico | view | SELECT | Domínio de bancos ativos (DBGLOBAL) |
| TbParametroConsultaCliente | tabela | SELECT | Parâmetros de consulta de clientes |
| TbParametroPagamentoFintech | tabela | SELECT | Parâmetros de pagamento fintech |
| prConsultarBoletoCnabDiario | procedure | EXEC | Busca dados de boletos para extrato diário (DBPGF_TES) |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|----------------------------|------|----------|-----------------|
| TbArquivoCnab | tabela | UPDATE | Atualiza nome do arquivo de retorno e situação |
| TbArquivoCnabProcessamento | tabela | UPDATE | Atualiza data de processamento e quantidades de registros |
| TbArquivoCnab | tabela | INSERT | Insere novo registro de arquivo processado (extrato) |
| TbArquivoCnabPessoa | tabela | INSERT | Insere pessoa associada ao arquivo (extrato) |
| TbArquivoCnabProcessamento | tabela | INSERT | Insere registro de processamento (extrato) |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| Arquivos CNAB de retorno (.RET) | gravação | ItemWriter / pathSaida | Arquivos CNAB 240 gerados com dados de retorno de pagamentos |
| Arquivos CNAB de extrato (.RET) | gravação | ItemWriter (extrato) | Arquivos CNAB 240 com extratos bancários diários |
| job-definitions.xml | leitura | SpringJobRunner | Definições de beans do job Spring Batch |
| job-resources.xml | leitura | SpringJobRunner | Configurações de recursos (datasources, paths) |
| log4j.xml | leitura | Framework | Configuração de logs |

**Padrões de nomenclatura:**
- Retorno: `FBBV_{CNPJ}_{TIMESTAMP}.RET`
- Extrato: `FBBVPAGBOL_{CNPJ}_{TIMESTAMP}.RET`
- Financeira: `BVF65500001_{DATA}_05B.RET-{TIMESTAMP}`

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
| DBSPAG (SQL Server) | Banco de Dados | Base principal com dados de arquivos CNAB, lotes, detalhes e processamento |
| DBGLOBAL (Sybase) | Banco de Dados | Base com domínios e cadastros gerais (bancos) |
| DBPGF_TES (Sybase) | Banco de Dados | Base de tesouraria com dados de boletos para extrato |
| Sistema de Arquivos | File System | Gravação de arquivos CNAB em diretórios de rede (\\bvnet\mor\...) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com padrão DAO e camadas bem definidas
- Uso adequado de Spring Batch para processamento em lote
- Implementação de padrão Strategy para diferentes layouts bancários (Votorantim/Itaú)
- Uso de enums para constantes e tipos
- Logging adequado em pontos críticos

**Pontos Negativos:**
- **Código comentado**: Muitos trechos de código comentado espalhados pelo projeto
- **Mistura de idiomas**: Comentários e mensagens em português, código em inglês, inconsistência
- **Queries SQL hardcoded**: Queries SQL complexas como strings concatenadas nas classes DAO
- **Falta de tratamento de exceções**: Muitos blocos catch genéricos apenas relançando exceções
- **Credenciais expostas**: Senhas de banco de dados visíveis nos arquivos XML de configuração
- **Código duplicado**: Lógica similar entre módulos de retorno e extrato poderia ser consolidada
- **Falta de documentação**: Ausência de JavaDoc nas classes e métodos
- **Uso de tecnologias antigas**: Java 1.6 e Spring 2.0.2 são versões muito desatualizadas
- **Complexidade ciclomática alta**: Métodos muito longos com múltiplas responsabilidades (ex: createDetalheSegmentoA)

---

## 14. Observações Relevantes

1. **Ambiente de Desenvolvimento**: O sistema está configurado para ambiente de desenvolvimento/teste (SQLBVFDES05, SYBDESSPB)

2. **Segurança**: Utiliza biblioteca BVCrypto para descriptografia de senhas, mas as senhas criptografadas estão expostas nos XMLs de configuração

3. **Padrão CNAB 240**: Sistema implementa o padrão bancário brasileiro CNAB 240 com segmentos A, B, C, Z, J e J52

4. **Dois Módulos Principais**:
   - Módulo de retorno: Processa arquivos CNAB já carregados no sistema
   - Módulo de extrato: Gera extratos diários de boletos pagos

5. **Execução**: Sistema pode ser executado via scripts .bat (Windows) ou .sh (Linux)

6. **Transações**: Configurado com timeout de transação de 61200000ms (~17 horas)

7. **Memória**: JVM configurada com -Xms1024m -Xmx2048m para o módulo de retorno

8. **Bitronix**: Utiliza Bitronix como gerenciador de transações JTA

9. **Versionamento**: Projeto versionado em Git (referências no pom.xml)

10. **Build**: Geração de distribuível ZIP com todas as dependências e scripts de execução via Maven Assembly Plugin

11. **Framework Proprietário**: Utiliza framework batch proprietário da BV Sistemas (bv-framework-batch)

12. **Compatibilidade**: Suporta múltiplos bancos através de código de compensação (655 - Votorantim, 413 - BV)