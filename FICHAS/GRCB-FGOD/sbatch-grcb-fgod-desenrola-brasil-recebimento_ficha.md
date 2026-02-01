# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de processamento em lote (Spring Batch) para recebimento e tratamento de arquivos CSV relacionados ao programa "Desenrola Brasil". O sistema realiza a leitura de arquivos de quitação de contratos, valida as informações contra bases de dados MySQL e Sybase, efetua baixas de parcelas e gera arquivos de inconsistências quando necessário. O processamento inclui validação de valores, CPF, contratos e parcelas, além de controle de carga e movimentação de arquivos entre diretórios de um file server.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `JobConfig` | Configuração principal do job Spring Batch, define steps e fluxo de execução |
| `CheckFileTasklet` | Verifica existência de arquivos CSV no diretório de origem |
| `FileExistDecider` | Decide o fluxo baseado na existência e status de processamento do arquivo |
| `MoveArquivoDuplicadoTasklet` | Move arquivos duplicados para diretório específico |
| `CsvReader` | Lê e parseia arquivos CSV linha a linha |
| `Processor` | Processa e valida registros do arquivo contra bases de dados |
| `BaixaParcelaWriter` | Grava baixas de parcelas no Sybase e registros no MySQL |
| `InconsistenciaFileWriter` | Gera arquivo CSV com registros inconsistentes |
| `FileUtils` | Utilitário para operações com file server (SMB/CIFS) |
| `SRCGRepositoryImpl` | Acesso aos dados de lotes e parcelas no MySQL SRCG |
| `GRCBRepositoryImpl` | Acesso aos dados de arquivos e quitações no MySQL GRCB |
| `ControleCargaRepositoryImpl` | Gerencia controle de carga no Sybase |
| `BaixarParcelaRepositoryImpl` | Insere baixas de parcelas no Sybase |

---

## 3. Tecnologias Utilizadas

- **Framework Principal**: Spring Boot 2.x, Spring Batch
- **Persistência**: Spring Data JPA, JDBI 3.9.1
- **Bancos de Dados**: MySQL 8.0.33, Sybase ASE (jConnect 16.3)
- **File Server**: JCIFS 2.1.31 (protocolo SMB/CIFS)
- **Logging**: Logback com formato JSON
- **Build**: Maven 3.8+
- **Java**: JDK 11
- **Containerização**: Docker
- **Infraestrutura**: Google Cloud Platform (GCP)
- **Utilitários**: Lombok, Apache Commons IO 2.14.0

---

## 4. Principais Endpoints REST

Não se aplica. Este é um componente batch que não expõe endpoints REST. A execução é iniciada via linha de comando ou scheduler.

---

## 5. Principais Regras de Negócio

1. **Validação de Arquivo Duplicado**: Verifica se o arquivo já foi processado anteriormente consultando o nome no banco GRCB
2. **Validação de CPF**: Compara o CPF do registro com o CPF do contrato no lote
3. **Validação de Valor**: Calcula valor esperado (valor lançamento + fees + desconto à vista) e compara com valor do lote, aceitando variação configurável (0.05)
4. **Validação de Contrato**: Verifica existência do contrato nos lotes do Desenrola Brasil
5. **Validação de Parcelas**: Verifica existência de parcelas ativas para o contrato
6. **Cálculo de Desconto**: Aplica percentual de lance negociado sobre valor real das parcelas (presente + mora + multa)
7. **Validação de Soma**: Verifica se soma dos valores das parcelas calculadas bate com valor do lote
8. **Validação de Total do Arquivo**: Compara soma dos registros com valor total informado no cabeçalho
9. **Controle de Carga**: Gera sequencial de controle via stored procedure no Sybase
10. **Movimentação de Arquivos**: Move arquivos processados para pasta específica, duplicados para pasta com sufixo "_D", e gera arquivo de inconsistências com sufixo "_I"

---

## 6. Relação entre Entidades

**RegistroArquivo**: Representa uma linha do arquivo CSV com dados de quitação
- Relaciona-se com **LoteDesenrolaBrasil** via `nuContratoOriginal`
- Contém lista de **ParcelaContrato**

**LoteDesenrolaBrasil**: Dados do lote de negociação do Desenrola Brasil
- Relaciona-se com **ParcelaContrato** via `nuContrato`
- Contém informações de CPF, CNPJ, percentual de lance e valor de desconto

**ParcelaContrato**: Representa parcelas de um contrato
- Relaciona-se com **ContratoParcela** para baixa
- Contém valores de principal, juros, mora, multa e taxa

**ContratoParcela**: Estrutura para baixa de parcela no Sybase
- Derivada de **ParcelaContrato** com informações adicionais de pagamento

**DadosContratoParcela**: Dados complementares de contrato e parcela (não utilizada no fluxo principal)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| `SRCGRenegociacaoDivida.TbLoteDesenrolaBrasil` | Tabela | SELECT | Consulta dados do lote de negociação por número de contrato |
| `SRCGRenegociacaoDivida.TbParcelaLoteDesenrolaBrasil` | Tabela | SELECT | Consulta parcelas ativas de um contrato no lote |
| `GRCBRenegociacaoDivida.TbArquivo` | Tabela | SELECT | Verifica se arquivo já foi processado anteriormente |
| `DBGESTAOCDCSG..TbParcela` | Tabela | SELECT | Consulta parcelas ativas de contratos CDC SG |
| `DBGESTAOCDCSG..TbContrato` | Tabela | SELECT | Consulta dados de contratos CDC SG |
| `DBGESTAOCP..TbParcela` | Tabela | SELECT | Consulta parcelas ativas de contratos CP |
| `DBGESTAOCP..TbContrato` | Tabela | SELECT | Consulta dados de contratos CP |
| `DBGESTAOCPC..TbParcela` | Tabela | SELECT | Consulta parcelas ativas de contratos CPC |
| `DBGESTAOCPC..TbContrato` | Tabela | SELECT | Consulta dados de contratos CPC |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| `DBGESTAO..TbInformacaoBaixa` | Tabela | INSERT | Insere informações de baixa de parcelas |
| `DBGESTAO..TbControleCarga` | Tabela | INSERT/UPDATE | Gera e atualiza controle de carga via stored procedure |
| `GRCBRenegociacaoDivida.TbArquivo` | Tabela | INSERT | Registra arquivo processado |
| `GRCBRenegociacaoDivida.TbArquivoQuitacao` | Tabela | INSERT | Registra cada linha do arquivo de quitação |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `YYYYMMDD_DESENROLA_XX.csv` | Leitura | `CsvReader` / Pasta `Recebido/` | Arquivo CSV de entrada com registros de quitação |
| `YYYYMMDD_DESENROLA_XX.csv` | Gravação | `CsvStepListener` / Pasta `Processado/` | Arquivo original movido após processamento bem-sucedido |
| `YYYYMMDD_DESENROLA_XX_D.csv` | Gravação | `MoveArquivoDuplicadoTasklet` / Pasta `Processado/` | Arquivo duplicado (já processado anteriormente) |
| `YYYYMMDD_DESENROLA_XX_I.csv` | Gravação | `InconsistenciaFileWriter` / Pasta `Inconsistencia/` | Arquivo com registros inconsistentes e erros de validação |
| Arquivo temporário | Leitura/Gravação | `FileUtils` / `java.io.tmpdir` | Cópia temporária do arquivo para processamento |

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

---

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| File Server SMB/CIFS | Leitura/Escrita | Acesso a diretórios compartilhados para leitura de arquivos CSV e gravação de resultados |
| MySQL GRCB | Banco de Dados | Base de controle de arquivos e registros de quitação |
| MySQL SRCG | Banco de Dados | Base de lotes e parcelas do Desenrola Brasil |
| Sybase DBGESTAO | Banco de Dados | Base de contratos, parcelas e controle de carga para baixas |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com uso adequado de Spring Batch (Reader, Processor, Writer)
- Uso de JDBI para acesso a dados de forma declarativa e limpa
- Configuração externalizada em arquivos YAML
- Uso de Lombok para reduzir boilerplate
- Tratamento de exceções customizado
- Logs informativos em pontos estratégicos
- Uso de constantes para valores fixos
- Estrutura de camadas bem definida (config, domain, repository, utils)

**Pontos de Melhoria:**
- Classe `Processor` muito extensa com múltiplas responsabilidades (validações, cálculos, persistência)
- Lógica de negócio misturada com lógica de infraestrutura em alguns pontos
- Falta de testes unitários nos arquivos fornecidos (apenas estrutura de testes)
- Uso de flags booleanas (`configuracaoNaoRealizada`) para controle de estado
- Queries SQL hardcoded em arquivos separados, mas com UNIONs complexos que poderiam ser otimizados
- Falta de documentação JavaDoc em métodos complexos
- Alguns métodos poderiam ser extraídos para melhorar legibilidade (ex: `processaRegistro`)
- Tratamento de exceções genérico em alguns pontos (`catch (Exception e)`)

---

## 14. Observações Relevantes

1. **Ambiente Multi-Tenant**: O sistema possui configurações específicas para ambientes DES, UAT e PRD com diferentes credenciais e endpoints
2. **Segurança**: Senhas e credenciais são gerenciadas via cofre de senhas (variáveis de ambiente)
3. **Monitoramento**: Exposição de métricas via Actuator e Prometheus
4. **Logging Estruturado**: Logs em formato JSON para ambientes não-locais
5. **Controle de Versão**: Sistema de versionamento semântico (0.6.0)
6. **Infraestrutura como Código**: Configuração de infraestrutura via arquivo `infra.yml` para deploy no GCP
7. **Processamento Batch**: Execução única por arquivo, com controle de duplicidade
8. **Tolerância a Falhas**: Sistema continua processamento mesmo com registros inconsistentes, gerando relatório ao final
9. **Auditoria**: Todos os registros são gravados no banco, independente de serem consistentes ou não, com flag de status
10. **Performance**: Uso de chunk size de 10 registros para processamento em lote