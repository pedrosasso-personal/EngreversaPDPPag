# Ficha Técnica do Sistema

---

## 1. Descrição Geral

Sistema batch Java desenvolvido para gerar arquivos de remessa de autorização de débito automático em conta corrente para o Banco do Brasil. O sistema consulta registros pendentes de envio no banco de dados, processa as informações, gera arquivos no formato específico do banco (layout posicional de 150 caracteres) e atualiza o status dos registros processados. Utiliza Spring Batch para orquestração do processamento em lote.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê registros de autorização de débito pendentes do banco de dados |
| **ItemProcessor** | Processa cada registro, calculando a data de vencimento com base em dias configurados |
| **ItemWriter** | Gera o arquivo de remessa no formato posicional e persiste logs de controle |
| **MyResumeStrategy** | Estratégia de tratamento de erros e retomada do job |
| **RegistroDebitoAutDAO** | Acesso aos dados de registros de autorização de débito |
| **ContaConvenioDAO** | Atualiza número de arquivo de envio nas contas convênio |
| **LogArquivoDebitoAutDAO** | Registra logs dos arquivos de débito gerados |
| **ControleArquivoDAO** | Persiste controle detalhado do arquivo (header, detail, footer) |
| **SequencialDAO** | Obtém sequenciais para chaves primárias |
| **RegistroAutDebitoVO** | Value Object principal com dados do registro de débito |
| **HeaderVO, DetailVO, FooterVO** | Value Objects para estruturas do arquivo |
| **ExitCode** | Enum com códigos de erro do sistema |
| **CommonConstants** | Constantes do sistema |
| **Util** | Utilitários para formatação de campos |
| **PropertiesUtil** | Carregamento de propriedades de configuração |

---

## 3. Tecnologias Utilizadas

- **Spring Batch** (framework de processamento batch)
- **Spring Framework** (injeção de dependências, configuração XML)
- **Maven** (gerenciamento de dependências e build)
- **Sybase jConnect 4** (driver JDBC para Sybase ASE - versão 7.07-SP136)
- **BV Framework Batch** (framework proprietário BV Sistemas)
- **BV Crypto** (criptografia de senhas)
- **JUnit** (testes unitários)
- **Log4j** (logging)
- **Apache Commons Lang** (utilitários)

---

## 4. Principais Endpoints REST

Não se aplica (sistema batch sem endpoints REST).

---

## 5. Principais Regras de Negócio

1. **Seleção de Registros**: Busca registros com status "pendente de envio" (1), conta convênio específica (2), status de autorização "pendente cliente" (2) e banco 001 (Banco do Brasil)
2. **Cálculo de Vencimento**: Adiciona 29 dias (configurável via properties) à data atual para definir o prazo de autorização do cliente
3. **Formatação de Arquivo**: Gera arquivo posicional de 150 caracteres por linha com header (tipo A), detalhes (tipo E) e footer (tipo Z)
4. **Nomenclatura de Arquivo**: Formato `BBM.TRN.DBT627.BVT{CdContaConvenio}.T{hhmmss}`
5. **Controle de Sequencial**: Incrementa número de arquivo de envio a cada geração
6. **Validação de CPF**: Formata CPF com zeros à esquerda (15 posições)
7. **Controle Transacional**: Registra todas as linhas do arquivo em tabelas de controle para auditoria
8. **Atualização de Status**: Marca registros como processados após geração bem-sucedida do arquivo
9. **Rollback em Erro**: Deleta arquivo físico em caso de erro durante geração

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **TbRegistroAutorizacaoDebito**: Registro de solicitação de débito automático
  - Relaciona-se com **TbEventoRegistroAutorizacaoDbo** (1:N) - eventos do registro
  - Relaciona-se com **TbContaConvenio** (N:1) via NuBanco

- **TbContaConvenio**: Conta convênio da empresa com o banco
  - Relaciona-se com **TbVeiculoLegal** (N:1) - dados da empresa
  - Relaciona-se com **TbBanco** (N:1) - dados do banco

- **TbLogArquivoDebito**: Log de arquivos gerados
  - Relaciona-se com **TbContaConvenio** (N:1)

- **TbControleArquivoDebitoAtmto**: Controle de arquivos processados
  - Relaciona-se com **TbConteudoLinhaArquivo** (1:N) - linhas do arquivo
  - Relaciona-se com **TbLinhaCabecalhoArquivo** (1:1) - header
  - Relaciona-se com **TbLInhaDetalheArquivo** (1:N) - detalhes
  - Relaciona-se com **TbLInhaRodapeArquivo** (1:1) - footer

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbRegistroAutorizacaoDebito | Tabela | SELECT | Registros de autorização de débito pendentes de envio |
| TbEventoRegistroAutorizacaoDbo | Tabela | SELECT | Eventos associados aos registros de autorização |
| TbContaConvenio | Tabela | SELECT | Contas convênio das empresas com bancos |
| TbVeiculoLegal | Tabela | SELECT | Dados das empresas (razão social) |
| TbBanco | Tabela | SELECT | Dados dos bancos |
| TbParametroSistema | Tabela | SELECT | Parâmetros do sistema (data de exercício) |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbRegistroAutorizacaoDebito | Tabela | UPDATE | Atualiza status de processamento dos registros |
| TbContaConvenio | Tabela | UPDATE | Atualiza número do arquivo de envio |
| TbLogArquivoDebito | Tabela | INSERT | Insere log do arquivo gerado |
| TbControleArquivoDebitoAtmto | Tabela | INSERT | Insere controle do arquivo processado |
| TbConteudoLinhaArquivo | Tabela | INSERT | Insere cada linha do arquivo para auditoria |
| TbLinhaCabecalhoArquivo | Tabela | INSERT | Insere dados do header do arquivo |
| TbLInhaDetalheArquivo | Tabela | INSERT | Insere dados dos detalhes do arquivo |
| TbLInhaRodapeArquivo | Tabela | INSERT | Insere dados do footer do arquivo |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| conf.properties | Leitura | PropertiesUtil | Configurações de layout do arquivo e dias de vencimento |
| monitoring.properties | Leitura | Configuração | Propriedades de monitoramento JMX |
| BBM.TRN.DBT627.BVT{codigo}.T{hora} | Gravação | ItemWriter | Arquivo de remessa de débito automático para Banco do Brasil |
| log4j.xml | Leitura | Framework | Configuração de logs |
| statistics-*.log | Gravação | Framework Batch | Estatísticas de execução do job |
| btm1.tlog, btm2.tlog | Gravação | Bitronix | Logs transacionais (removidos ao final) |

---

## 10. Filas Lidas

Não se aplica.

---

## 11. Filas Geradas

Não se aplica.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Banco do Brasil | Arquivo | Geração de arquivo de remessa no formato posicional específico do banco para autorização de débito automático |
| Banco de Dados Sybase ASE | JDBC | Acesso ao banco DbGestaoDebitoContaCorrente para leitura e gravação de dados |

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades (Reader, Processor, Writer)
- Uso adequado do Spring Batch
- Tratamento de erros com códigos específicos
- Documentação JavaDoc presente
- Controle transacional e auditoria detalhada

**Pontos Negativos:**
- **Código comentado**: Múltiplas linhas comentadas sem remoção (ex: DataSourceUtils)
- **Hardcoding**: Valores fixos espalhados pelo código (ex: tamanhos de campos, constantes mágicas)
- **Complexidade excessiva**: Método `geradorLinhaStr` com lógica complexa de reflexão
- **Mistura de responsabilidades**: ItemWriter faz persistência de múltiplas tabelas além de gerar arquivo
- **Falta de testes**: Apenas um teste de integração, sem testes unitários
- **Encoding inconsistente**: Comentários em ISO-8859-1 com caracteres corrompidos
- **Uso de reflexão desnecessário**: Poderia ser substituído por mapeamento direto
- **Tratamento de exceções genérico**: Catch de Exception sem especificidade
- **Código duplicado**: Lógica de formatação repetida em várias classes
- **Falta de validações**: Pouca validação de dados de entrada

---

## 14. Observações Relevantes

1. **Banco de Dados**: Sistema utiliza Sybase ASE (DbGestaoDebitoContaCorrente) com schema específico
2. **Configuração de Ambiente**: Diferentes configurações para QA, UAT e PROD comentadas no código
3. **Criptografia**: Senhas de banco podem ser criptografadas usando propriedade "sistema"
4. **Commit Interval**: Configurado para 100 registros por commit
5. **Memória JVM**: Configurada com -Xms256M -Xmx512M
6. **Timeout Transacional**: 3600 segundos (1 hora)
7. **Execução Concorrente**: Habilitada (concurrentExecution=true)
8. **Framework Proprietário**: Utiliza BV Framework Batch (br.com.bvsistemas.framework.batch)
9. **Versionamento**: Projeto versionado em Git
10. **Build**: Maven multi-módulo (core + dist)
11. **Deployment**: Geração de ZIP com estrutura completa (lib, conf, scripts)
12. **Monitoramento**: Integração com agente JMX para monitoramento
13. **Rollback**: Em caso de erro, o arquivo físico é deletado e transação revertida
14. **Auditoria**: Todas as linhas do arquivo são persistidas em tabelas de controle para rastreabilidade completa