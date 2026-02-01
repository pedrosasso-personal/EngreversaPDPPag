# Ficha Técnica do Sistema

---

## 1. Descrição Geral

Sistema batch Java responsável por enviar arquivos de compensação bancária ABBC via FTP. O sistema realiza a leitura de arquivos gerados em diretório local, valida seu conteúdo contra dados armazenados em banco de dados Sybase, e move os arquivos validados para uma pasta de saída (caixa postal FTP). Inclui rotinas de conciliação diária para garantir a integridade dos dados processados.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê arquivos do diretório de entrada e inicializa contexto do job com parâmetros (data movimento, validação, código banco) |
| **ItemProcessor** | Valida arquivos fisicamente (nome, conteúdo, totalizadores) e compara com dados do banco de dados |
| **ItemWriter** | Move arquivos validados para pasta de saída/erro/devolução e atualiza status no banco de dados |
| **ArquivoCompensacaoDAOImpl** | Implementa acesso ao banco de dados Sybase para consultas e atualizações de arquivos de compensação |
| **ConciliacaoDiariaHelper** | Executa rotinas de conciliação: valida registros não processados, duplicidades e totais diários |
| **FileUtil** | Utilitário para manipulação de arquivos (mover, copiar, obter caminhos configurados) |
| **MyResumeStrategy** | Estratégia de tratamento de erros e devolução de arquivos em caso de falha |
| **ValidacaoArquivoDTO** | DTO que encapsula dados de validação de arquivo (quantidades, valores, status) |

---

## 3. Tecnologias Utilizadas

- **Spring Batch** (framework de processamento batch)
- **Spring Framework** 2.0 (injeção de dependências, configuração XML)
- **Maven** (gerenciamento de dependências e build)
- **Sybase ASE** (banco de dados - driver jConnect 4)
- **BV Framework Batch** (framework proprietário BV Sistemas)
- **BV JDBC Driver** (driver JDBC customizado com criptografia)
- **Log4j** (logging)
- **JUnit** (testes unitários)

---

## 4. Principais Endpoints REST

**Não se aplica** - Sistema batch sem endpoints REST.

---

## 5. Principais Regras de Negócio

1. **Validação de Nome de Arquivo**: O arquivo deve conter a data de processamento no formato ddMM no nome
2. **Validação de Arquivo Regerado**: Arquivos com status 11 (regerado) são movidos para pasta de erro
3. **Validação de Conteúdo**: Compara quantidade de registros e valor total do arquivo físico com dados do banco
4. **Conciliação Diária**: Executada após horário configurado (padrão 22h), valida:
   - Registros não processados no dia
   - Duplicidades de lançamentos
   - Divergências entre totais do banco e arquivos gerados
5. **Movimentação de Arquivos**: Arquivos validados vão para saída, com erro para pasta de erro, e fora do padrão para devolução
6. **Atualização de Status**: Arquivos enviados recebem status 4 (STATUS_COMPENSACAO_ENVIADO) no banco
7. **Tratamento por Banco**: Sistema suporta múltiplos bancos (código banco parametrizável, padrão 655)
8. **Validação de Valores STR**: Consulta valor configurado em TBL_SETUP_TESOURARIA para filtrar lançamentos

---

## 6. Relação entre Entidades

**Entidades principais identificadas:**

- **TbArquivoCompensacao**: Armazena metadados dos arquivos de compensação
  - Campos: cdArquivoCompensacao (PK), nmArquivoCompensacao, cdStatusCompensacao, dtEnvioArquivo, dtAlteracao
  
- **TbDetalheArquivoCompensacao**: Detalhes/linhas dos arquivos de compensação
  - Relacionamento: N:1 com TbArquivoCompensacao via cdArquivoCompensacao
  - Campos: cdLancamentoTesouraria, cdStatusCompensacao, dtAlteracao

- **TBL_LANCAMENTO**: Lançamentos de tesouraria
  - Campos: Cod_Lancamento (PK), Dat_Movimento, Num_Banco_Remetente
  - Relacionamento: 1:N com TbDetalheArquivoCompensacao

- **TBL_SETUP_TESOURARIA**: Configurações de tesouraria
  - Campo: VrBoletoSPB (valor limite STR)

**Relacionamentos:**
- TbArquivoCompensacao 1 → N TbDetalheArquivoCompensacao
- TBL_LANCAMENTO 1 → N TbDetalheArquivoCompensacao

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TBL_SETUP_TESOURARIA | Tabela | SELECT | Consulta valor limite STR (VrBoletoSPB) para filtros |
| TbArquivoCompensacao | Tabela | SELECT | Busca metadados de arquivos (totais, status, verificação de regeração) |
| TbDetalheArquivoCompensacao | Tabela | SELECT | Busca detalhes de lançamentos, duplicidades e totalizadores |
| TBL_LANCAMENTO | Tabela | SELECT | Consulta lançamentos de tesouraria por data e banco |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbArquivoCompensacao | Tabela | UPDATE | Atualiza status de compensação (cdStatusCompensacao=4) e data de envio após validação |
| TbDetalheArquivoCompensacao | Tabela | UPDATE | Atualiza status de compensação dos detalhes vinculados ao arquivo |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| Arquivos de compensação (padrão nome com data ddMM) | Leitura | ItemReader / ItemProcessor | Arquivos texto com lançamentos de compensação bancária |
| config.properties | Leitura | PropertiesReader | Arquivo de configuração com paths, emails e horário de conciliação |
| job-resources.xml | Leitura | Spring Context | Configuração de datasource Sybase |
| Arquivos validados | Gravação/Movimentação | ItemWriter / FileUtil | Move arquivos para pasta de saída após validação |
| Arquivos com erro | Gravação/Movimentação | ItemWriter / FileUtil | Move arquivos inválidos para pasta de erro |
| Arquivos devolvidos | Gravação/Movimentação | ItemWriter / FileUtil | Move arquivos fora do padrão para pasta de devolução |

---

## 10. Filas Lidas

**Não se aplica** - Sistema não consome mensagens de filas.

---

## 11. Filas Geradas

**Não se aplica** - Sistema não publica mensagens em filas.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Banco Sybase ASE (DBPGF_TES) | Banco de Dados | Consulta e atualização de dados de compensação bancária via JDBC |
| Servidor FTP (implícito) | Transferência de Arquivos | Pasta de saída configurada para envio via FTP (integração externa ao batch) |
| Servidor SMTP (smtpduqrelay.bvnet.bv) | Email | Configurado para envio de emails (funcionalidade não implementada no código analisado) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Estrutura bem organizada seguindo padrão Spring Batch (Reader/Processor/Writer)
- Separação clara de responsabilidades (DAO, DTO, Helper, Util)
- Uso de logging adequado
- Tratamento de exceções customizado (PgftException)
- Configuração externalizada (properties)

**Pontos Negativos:**
- **Código legado**: Uso de Spring 2.0 e configuração XML (tecnologia desatualizada)
- **Encoding problemático**: Comentários com caracteres corrompidos (ISO-8859-1)
- **Hardcoding**: Strings SQL diretamente nas interfaces DAO
- **Falta de testes**: Apenas estrutura de teste, sem implementação
- **Tratamento de erros inconsistente**: Alguns métodos retornam null, outros lançam exceções
- **Código comentado**: Trechos de configuração comentados no XML
- **Falta de documentação**: JavaDoc incompleto ou ausente em muitos métodos
- **Validações frágeis**: Parsing de strings sem tratamento robusto de erros
- **Acoplamento**: Dependência forte do framework proprietário BV

---

## 14. Observações Relevantes

1. **Ambiente**: Configuração aponta para ambiente de desenvolvimento (sybdesspb.bvnet.bv:6500/DBPGF_TES)
2. **Versão**: Sistema na versão 0.12.0, indicando maturidade moderada
3. **Parametrização**: Suporta execução com parâmetros: DATA_MOVIMENTO, VALIDAR (S/N), COD_BANCO
4. **Códigos de Saída**: Sistema retorna códigos específicos (0-15) para diferentes cenários de erro
5. **Conciliação Opcional**: Validação completa só ocorre após horário configurado (padrão 22h)
6. **Multi-banco**: Suporta processamento para diferentes bancos através de subpastas organizadas por código
7. **Formato de Arquivo**: Arquivos possuem estrutura posicional com header, detalhes e trailer
8. **Validação de Valores**: Valores são armazenados em centavos (divisão por 100) no arquivo
9. **Framework Proprietário**: Forte dependência do BV Framework, dificultando portabilidade
10. **Estratégia de Recuperação**: Em caso de erro, arquivos são automaticamente devolvidos para pasta de devolução

---