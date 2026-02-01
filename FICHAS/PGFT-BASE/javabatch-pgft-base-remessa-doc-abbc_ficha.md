# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java responsável pela geração e conciliação de arquivos de remessa de documentos (DOC) para o banco ABBC (código 655). O sistema possui dois módulos principais:

- **Módulo de Geração**: Gera arquivos no formato DCR605 contendo lançamentos de tesouraria para compensação bancária
- **Módulo de Conciliação**: Valida os arquivos gerados, verificando consistência de dados, duplicidades e totalizadores antes do envio

O sistema processa lançamentos diários do banco de dados Sybase, gera arquivos padronizados e realiza validações de integridade para garantir a corretude das informações enviadas ao sistema de compensação bancária.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** (geracao) | Lê lançamentos do banco de dados e prepara dados para processamento |
| **ItemProcessor** (geracao) | Processa cada detalhe de lançamento (atualmente apenas repassa) |
| **ItemWriter** (geracao) | Escreve arquivos DCR605 e persiste detalhes no banco |
| **MultiFileWriterAdapter** | Gerencia a escrita de múltiplos arquivos DCR605 |
| **ArquivoDcr605Writer** | Escreve header, detalhes e trailer dos arquivos DCR605 |
| **GeracaoABBCBusinessImpl** | Lógica de negócio para geração de arquivos |
| **GeracaoABBCDaoImpl** | Acesso a dados para geração de arquivos |
| **ItemReader** (conciliacao) | Lê arquivos físicos da pasta de entrada |
| **ItemProcessor** (conciliacao) | Valida arquivos físicos contra dados do banco |
| **ItemWriter** (conciliacao) | Move arquivos validados para pastas apropriadas |
| **ConciliacaoABBCBusinessImpl** | Lógica de negócio para conciliação |
| **ConciliacaoDiariaHelper** | Executa validações diárias (duplicidades, totais, não processados) |
| **ConciliacaoDAOImpl** | Acesso a dados para conciliação |

## 3. Tecnologias Utilizadas

- **Java** (versão não especificada no código)
- **Maven** - Gerenciamento de dependências e build
- **Spring Framework 2.0** - Injeção de dependências e configuração
- **BV Framework Batch** - Framework proprietário para processamento batch
- **Sybase ASE** - Banco de dados (via jConnect 4)
- **BVDriver JDBC** - Driver JDBC customizado da BV Sistemas
- **Log4j** - Logging
- **JUnit** - Testes unitários

## 4. Principais Endpoints REST

Não se aplica - este é um sistema batch sem endpoints REST.

## 5. Principais Regras de Negócio

1. **Geração de Arquivos DCR605**:
   - Apenas lançamentos com código de liquidação 21, status 1, tipo 'S' e banco remetente 655 são processados
   - Lançamentos já processados (status > 2) são ignorados
   - Arquivos são gerados com versionamento sequencial
   - Suporta reprocessamento de arquivos do dia

2. **Validação de Concorrência**:
   - Não permite geração se existem arquivos pendentes (status 1) criados há mais de 15 minutos
   - Arquivos pendentes recentes (< 15 min) bloqueiam nova geração

3. **Conciliação Diária**:
   - Valida se todos os lançamentos do dia foram processados
   - Verifica duplicidade de lançamentos no processamento
   - Compara totalizadores (quantidade e valor) entre banco e arquivos gerados
   - Valida nome do arquivo contra data de processamento

4. **Validação de Arquivos Físicos**:
   - Compara quantidade de registros do arquivo físico com banco
   - Valida valor total do arquivo contra banco
   - Arquivos regerados (status 11) são identificados e tratados diferentemente

5. **Movimentação de Arquivos**:
   - Arquivos validados → pasta "saida"
   - Arquivos com erro → pasta "erro"
   - Arquivos com nome inválido → pasta "devolucao"
   - Arquivos regerados → pasta "saida" (com status especial)

## 6. Relação entre Entidades

**ArquivoCompensacaoVO** (1) ----< (N) **DetalheArquivoCompensacaoVO**
- Um arquivo de compensação contém múltiplos detalhes

**DetalheArquivoCompensacaoVO** (1) ---- (1) **LancamentoVO**
- Cada detalhe está associado a um lançamento de tesouraria

**ArquivoCompensacaoVO**:
- cdgArquivoCompensacao (PK)
- versaoArquivo
- nomeArquivoCompensacao
- cdgStatusCompensacao
- dataMovimento

**DetalheArquivoCompensacaoVO**:
- cdgDetalheArquivoCompensacao (PK)
- cdgArquivoCompensacao (FK)
- cdgStatusCompensacao
- descProcessamentoCompensacao

**LancamentoVO**:
- codigoLancamento (PK)
- valorDocumento
- dados de remetente e destinatário

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TBL_LANCAMENTO | tabela | SELECT | Lançamentos de tesouraria para geração de arquivos |
| TbArquivoCompensacao | tabela | SELECT | Arquivos de compensação gerados |
| TbDetalheArquivoCompensacao | tabela | SELECT | Detalhes dos arquivos de compensação |
| TBL_LANC_RELACIONADO | tabela | SELECT | Relacionamento entre lançamentos (para filtrar duplicidades) |
| tbbanco (dbglobal) | tabela | SELECT | Dados de bancos (ISPB, código COMPE) |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbArquivoCompensacao | tabela | INSERT | Criação de novos registros de arquivo via PrCriarNovaRemessa |
| TbArquivoCompensacao | tabela | UPDATE | Atualização de status, tamanho, totais e data de envio |
| TbArquivoCompensacao | tabela | DELETE | Exclusão de arquivos em caso de erro ou reprocessamento |
| TbDetalheArquivoCompensacao | tabela | INSERT | Inserção de detalhes via prInserirDetArqCompensacaoV2 |
| TbDetalheArquivoCompensacao | tabela | UPDATE | Atualização de status dos detalhes |
| TbDetalheArquivoCompensacao | tabela | DELETE | Exclusão de detalhes em caso de rollback |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| DCR605*.doc | gravação | MultiFileWriterAdapter / ArquivoDcr605Writer | Arquivos de remessa no formato DCR605 |
| DCR605*.doc | leitura | ItemProcessor (conciliacao) | Validação de arquivos gerados |
| config.properties | leitura | Resources | Configurações do sistema (path home) |
| job-resources.xml | leitura | Spring | Configuração de datasources |
| log4j.xml | leitura | Log4j | Configuração de logs |
| statistics-${executionId}.log | gravação | BvDailyRollingFileAppender | Logs de estatísticas do batch |
| robo.log | gravação | RollingFileAppender | Logs da aplicação |

## 10. Filas Lidas

Não se aplica - o sistema não consome mensagens de filas.

## 11. Filas Geradas

Não se aplica - o sistema não publica mensagens em filas.

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Sybase ASE (DBPGF_TES) | Banco de Dados | Banco principal com dados de lançamentos e compensação |
| Sistema de Arquivos | File System | Leitura/escrita de arquivos DCR605 em pastas específicas (entrada, saida, erro, devolucao) |
| BV Framework Batch | Framework | Framework proprietário para execução de jobs batch |

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Separação clara de responsabilidades entre módulos de geração e conciliação
- Uso de padrões de projeto (Strategy, Template Method via framework)
- Tratamento de exceções customizado (PgftException)
- Logging estruturado e detalhado
- Uso de constantes para valores fixos

**Pontos Negativos:**
- **Código comentado**: Múltiplas seções de código comentado nos XMLs de configuração (credenciais alternativas)
- **Strings SQL hardcoded**: Queries SQL complexas definidas como strings em interfaces, dificultando manutenção
- **Falta de documentação**: Javadoc ausente ou incompleto na maioria das classes
- **Mistura de idiomas**: Comentários e mensagens em português e inglês
- **Acoplamento**: Forte dependência do framework proprietário BV, dificultando portabilidade
- **Testes limitados**: Apenas testes de integração básicos, sem cobertura de testes unitários
- **Tratamento de exceções genérico**: Muitos catch(Exception) sem tratamento específico
- **Magic numbers**: Códigos numéricos sem constantes explicativas (ex: status 1, 3, 11)

## 14. Observações Relevantes

1. **Ambiente de Desenvolvimento**: O código contém configurações hardcoded para ambiente de desenvolvimento (sybdesspb.bvnet.bv:6500) com credenciais expostas

2. **Stored Procedures**: O sistema depende fortemente de stored procedures do Sybase (PrCriarNovaRemessa, prInserirDetArqCompensacaoV2, PrConsultarTotalArquivoCompensacao)

3. **Formato DCR605**: Arquivo de layout fixo posicional com 255 caracteres por linha, seguindo padrão específico do ABBC

4. **Códigos de Status**:
   - 1: Pendente
   - 3: Gerado
   - 4: Validado
   - 5: Erro
   - 8: Devolução
   - 11: Regerado

5. **Limitações**:
   - Processamento síncrono e sequencial
   - Sem paralelização de processamento
   - Dependência de estrutura de pastas específica no filesystem

6. **Segurança**: Credenciais de banco de dados expostas em arquivos de configuração XML (não recomendado para produção)

7. **Versionamento**: Sistema utiliza versionamento sequencial de arquivos baseado em procedure do banco