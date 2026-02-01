---
## Ficha Técnica do Sistema

### 1. Descrição Geral
Sistema batch desenvolvido em Spring Batch para geração de arquivos contábeis posicionais com extensão .MV destinados ao sistema Softpar. O componente realiza a leitura de dados consolidados da base CCBD (Conta Corrente Banco Digital), processa movimentações contábeis, gera arquivos no formato posicional específico e transfere os arquivos via protocolo SMB para diretórios de rede. Suporta dois formatos de arquivo: IFRS9 (contas com 25 posições) e formato legado (contas com 15 posições). A execução é automatizada via UC4, rodando de terça a sábado às 04:00h, com possibilidade de execução manual e regeração de arquivos.

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot que inicializa a aplicação batch |
| `JobConfig` | Configuração central do job Spring Batch, definindo readers, processors, writers e fluxos |
| `DetalheMovimentoContabilReader` | Reader que consulta detalhes de movimentação contábil do banco Sybase |
| `DetalheMovimentoRegerarReader` | Reader específico para regeração de arquivos já processados |
| `TotalizaLoteContabilReader` | Reader que busca totalizadores de lotes contábeis |
| `DetalhesMovimentoLoteProcessor` | Processor que consolida detalhes de movimentação em estrutura de arquivo |
| `CalculaValoresLotesProcessor` | Processor que calcula valores totais de crédito/débito por lote |
| `DetalheMovimentoContabilWriter` | Writer que grava arquivos posicionais no sistema de arquivos local |
| `TotalizaLoteContabilWriter` | Writer que atualiza valores totalizados nas tabelas de lote |
| `ControleArquivoContabilTasklet` | Tasklet que cria registro de controle de arquivo gerado |
| `ObterDatasContabeisTasklet` | Tasklet que obtém datas contábeis de referência |
| `ValidaDataExecucaoTasklet` | Tasklet que valida a data de execução informada |
| `ValidaTipoExecucao` | Tasklet que determina se é execução automática ou regeração |
| `TipoExecucaoIfrs` | Tasklet que ajusta tamanho de campos conforme padrão IFRS9 |
| `TransfereArquivoLocalParaFileServerTasklet` | Tasklet que transfere arquivos via SMB para file server |
| `FileServerServiceImpl` | Serviço de integração com file server via protocolo SMB/CIFS |
| `RegrasCabecalhoLinha` | Enum com regras de formatação do cabeçalho do arquivo |
| `RegrasDetalheLinha` | Enum com regras de formatação das linhas de detalhe |
| `ConversorNumericoStrategy` | Strategy para conversão de campos numéricos |
| `ConversorAlfaNumericoStrategy` | Strategy para conversão de campos alfanuméricos |
| `ConversorDataYYMMDDStrategy` | Strategy para conversão de datas no formato YYMMDD |
| `ConversorDataDDMMYYStrategy` | Strategy para conversão de datas no formato DDMMYY |

### 3. Tecnologias Utilizadas
- **Framework Principal**: Spring Boot 2.x, Spring Batch
- **Linguagem**: Java 11
- **Gerenciamento de Dependências**: Maven
- **Banco de Dados**: 
  - Sybase ASE (DBCONTACORRENTE) - leitura de dados contábeis
  - MySQL (CCBDContaCorrente) - controle de execução
- **Acesso a Dados**: JDBI 3.9.1, Spring Data JPA, Hibernate
- **Protocolo de Transferência**: SMB/CIFS (jcifs 2.1.31)
- **Observabilidade**: Micrometer, Prometheus, Spring Cloud Sleuth, OpenTelemetry
- **Segurança**: Spring Security OAuth2 Resource Server
- **Utilitários**: Lombok, Apache Commons IO, MapStruct
- **Containerização**: Docker
- **Orquestração**: UC4 (Automic)
- **Infraestrutura**: Google Cloud Platform

### 4. Principais Endpoints REST
não se aplica (aplicação batch sem endpoints REST expostos)

### 5. Principais Regras de Negócio
1. **Validação de Data de Execução**: Valida se a data informada é válida ou utiliza data contábil atual do sistema
2. **Controle de Sequência de Arquivo**: Gera número sequencial único por dia e instituição bancária para cada arquivo
3. **Separação por Lote**: Agrupa movimentações por lote contábil (código de instituição bancária)
4. **Totalização de Valores**: Calcula totais de débito e crédito por lote, garantindo balanceamento contábil
5. **Formatação IFRS9**: Ajusta tamanho de campos de conta contábil (15 ou 25 posições) conforme padrão IFRS9
6. **Controle de Regeração**: Permite regerar arquivos já processados sem duplicar registros
7. **Validação de Instituição Bancária**: Identifica e valida instituição bancária (Banco BV SA - código 51)
8. **Geração de Arquivo Posicional**: Formata dados em layout posicional específico com cabeçalho e detalhes
9. **Controle de Geração**: Marca lotes como gerados (FlGeracaoLoteMovimento='S') após processamento
10. **Encoding Condicional**: Utiliza UTF-8 para IFRS9 e ISO-8859-1 para formato legado
11. **Sequenciamento de Detalhes**: Ordena detalhes por sequência dentro de cada lote
12. **Nomenclatura de Arquivo**: Gera nome no formato MVnnnMMDDsss.MV (lote+data+sequência)

### 6. Relação entre Entidades

**Entidades Principais:**

- **ControleData**: Armazena datas contábeis (atual, anterior, próxima)
- **ControleArquivoContabil**: Controla arquivos gerados (sequência, data, sistema)
- **LoteMovimentoContabil**: Representa um lote de movimentações (totais, quantidade, flag de geração)
- **DetalheMovimentoContabil**: Detalhe individual de movimentação contábil
- **TotalizadorLoteContabil**: Totalizadores de débito/crédito por lote
- **MovimentacaoArquivoConsolidado**: Estrutura consolidada para geração do arquivo

**Relacionamentos:**
- ControleArquivoContabil (1) → (N) LoteMovimentoContabil
- LoteMovimentoContabil (1) → (N) DetalheMovimentoContabil
- DetalheMovimentoContabil (N) → (1) Transacao
- LoteMovimentoContabil (1) → (N) TotalizadorLoteContabil (agregação)

### 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbControleData | tabela | SELECT | Consulta datas contábeis de referência (atual, anterior, próxima) |
| TbDetalheLoteMovimentoContabil | tabela | SELECT | Lê detalhes de movimentações contábeis para geração de arquivo |
| TbLoteMovimentoContabil | tabela | SELECT | Consulta informações de lotes contábeis e totalizadores |
| TbTransacao | tabela | SELECT | Busca tipo de débito/crédito das transações |
| TbControleArquivoContabil | tabela | SELECT | Verifica existência e sequência de arquivos já gerados |

### 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbControleArquivoContabil | tabela | INSERT | Cria registro de controle para cada arquivo gerado |
| TbLoteMovimentoContabil | tabela | UPDATE | Atualiza valores totais (crédito/débito), quantidade de registros, flag de geração e código de controle de arquivo |

### 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| MVnnnMMDDsss.MV | gravação | DetalheMovimentoContabilWriter / diretório local temporário | Arquivo posicional contábil gerado localmente antes da transferência |
| MVnnnMMDDsss.MV | gravação | TransfereArquivoLocalParaFileServerTasklet / file server SMB | Arquivo transferido para diretório de rede (\\APPS\CCBD\Interface\Contabil\CC\enviar\) |
| logback-spring.xml | leitura | Configuração de logging | Arquivo de configuração de logs em formato JSON |

### 10. Filas Lidas
não se aplica

### 11. Filas Geradas
não se aplica

### 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Sybase ASE (DBCONTACORRENTE) | Banco de Dados | Leitura de dados contábeis consolidados do CCBD |
| MySQL (CCBDContaCorrente) | Banco de Dados | Controle de execução e metadados do batch |
| File Server SMB | Protocolo de Rede | Transferência de arquivos via SMB/CIFS para diretórios compartilhados (\\bvnet\MOR\APPS) |
| UC4 (Automic) | Orquestrador | Agendamento e execução automatizada do job (terça a sábado, 04:00h) |
| Softpar | Sistema Legado | Sistema destino que consome os arquivos .MV gerados |

### 13. Avaliação da Qualidade do Código

**Nota:** 8/10

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões Spring Batch com separação clara de responsabilidades (readers, processors, writers, tasklets)
- Uso adequado de design patterns (Strategy para conversores, Builder para entidades)
- Boa cobertura de testes unitários com uso de mocks
- Configuração externalizada em arquivos YAML por ambiente
- Uso de Lombok reduzindo boilerplate
- Documentação presente (README, comentários em código)
- Tratamento de exceções em pontos críticos
- Uso de constantes centralizadas evitando magic numbers/strings

**Pontos de Melhoria:**
- Algumas classes com múltiplas responsabilidades (ex: JobConfig com muitas configurações)
- Supressão de warning SonarQube em RegrasDetalheLinha sem justificativa clara
- Falta de validações mais robustas em alguns pontos (ex: validação de tamanho de campos)
- Logs poderiam ser mais estruturados com MDC para rastreabilidade
- Ausência de circuit breakers para integrações externas (file server, banco)
- Testes de integração poderiam ser mais abrangentes

O código demonstra maturidade técnica e boas práticas, com espaço para melhorias incrementais em resiliência e observabilidade.

### 14. Observações Relevantes

1. **Execução Dual Mode**: Sistema suporta dois modos de execução - geração automática de novos arquivos e regeração de arquivos já processados
2. **Compatibilidade IFRS9**: Implementa suporte a dois formatos de arquivo (15 e 25 posições em contas) para atender norma IFRS9
3. **Controle de Concorrência**: Utiliza READPAST em queries para evitar locks em execuções concorrentes
4. **Encoding Dinâmico**: Ajusta encoding do arquivo (UTF-8 ou ISO-8859-1) baseado no tipo de execução
5. **Nomenclatura Padronizada**: Arquivos seguem padrão MVnnnMMDDsss.MV onde nnn=lote, MMDD=data, sss=sequência
6. **Infraestrutura Cloud**: Preparado para execução em Google Cloud Platform com configurações específicas
7. **Segurança**: Credenciais de file server e bancos gerenciadas via secrets externos
8. **Layered Docker**: Dockerfile otimizado com múltiplas camadas para melhor cache e deploy
9. **Observabilidade**: Integrado com OpenTelemetry e Prometheus para monitoramento
10. **Malha UC4**: Faz parte de malha complexa com 4 jobs (JOBP.BD.CCBD.GERA_MVTO_CONTABIL.S009 e derivados)