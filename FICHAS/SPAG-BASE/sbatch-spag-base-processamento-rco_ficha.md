# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sbatch-spag-base-processamento-rco** é uma aplicação batch desenvolvida em Java com Spring Batch, responsável pelo processamento de arquivos RCO (Relatório de Conciliação de Operações) do sistema de pagamentos. O sistema realiza a leitura de arquivos ZIP contendo dados de movimentações bancárias da CIP (Câmara Interbancária de Pagamentos), processa e consolida informações de transações PAG e STR, e envia os dados processados para o sistema SPAG (Sistema de Pagamentos). Adicionalmente, o sistema gera arquivos físicos e envia notificações por e-mail em caso de contingência.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application.java` | Classe principal que inicializa a aplicação Spring Boot |
| `BatchConfiguration.java` | Configuração do job batch principal |
| `StepConfiguration.java` | Configuração dos steps do processamento batch |
| `ProcessamentoRcoReader.java` | Leitura e preparação dos dados de arquivos RCO para processamento |
| `ProcessamentoRcoProcessor.java` | Processamento e transformação dos dados RCO (filtragem, ordenação) |
| `SpagApiWriter.java` | Envio dos dados processados para a API do SPAG |
| `ArquivoFisicoWriter.java` | Gravação de arquivos RCO no sistema de arquivos |
| `EnvioEmailWriter.java` | Envio de e-mails com arquivos RCO em contingência |
| `SpbService.java` | Serviço de acesso aos dados do banco SPB (Sistema de Pagamentos Brasileiro) |
| `SpagService.java` | Serviço de integração com o sistema SPAG |
| `ArquivoRcoService.java` | Serviço de leitura e parsing de arquivos RCO |
| `ArquivoZipService.java` | Serviço de descompactação de arquivos ZIP |
| `EmailService.java` | Serviço de envio de e-mails via API Gateway |
| `FileServerImpl.java` | Implementação de acesso a arquivos via SMB/CIFS |
| `RcoProcessor.java` | Processador FFPojo para parsing de arquivos RCO posicionais |
| `LayoutArquivoRco.java` | Representação do layout completo do arquivo RCO |

## 3. Tecnologias Utilizadas

- **Framework Principal**: Spring Boot 2.x, Spring Batch
- **Linguagem**: Java 11
- **Gerenciamento de Dependências**: Maven
- **Bancos de Dados**: 
  - Microsoft SQL Server (DBSPAG)
  - Sybase ASE (DBISPB - SPB)
- **Bibliotecas de Parsing**: FFPojo (arquivos posicionais)
- **Acesso a Arquivos**: JCIFS (SMB/CIFS)
- **Segurança**: Spring Security, OAuth2
- **Logging**: Logback, SLF4J
- **Testes**: JUnit 5 (Jupiter), Mockito
- **Utilitários**: Lombok, Apache Commons IO
- **Containerização**: Docker
- **Orquestração**: Kubernetes (Google Cloud Platform)
- **API Gateway**: CA API Gateway (OAuth2)

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch que não expõe endpoints REST próprios. Ele consome APIs externas:

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `${SPAG_BASE_GESTAO_URL}/rco/uploadRco` | Envio de arquivo RCO processado para o SPAG |
| POST | `${CAAPI_EMAIL_URL}` | Envio de e-mails via API Gateway |

## 5. Principais Regras de Negócio

1. **Processamento de Arquivos RCO**: Leitura de arquivos ZIP da CIP contendo movimentações bancárias semanais
2. **Validação de Banco**: Apenas processa arquivos dos bancos Votorantim (655/ISPB 59588111) e BV S.A. (413/ISPB 01858774)
3. **Consolidação de Movimentos**: Agrupa movimentos STR e PAG por ISPB, data e código de mensagem
4. **Filtragem de Bancos Ativos**: Remove movimentos de bancos não pagantes (não ativos na CIP)
5. **Remoção de Movimentos STR0004**: Exclui especificamente movimentos com código STR0004
6. **Verificação de Duplicidade**: Não processa arquivos RCO já enviados anteriormente ao SPAG
7. **Modo Contingência**: Permite processamento manual de arquivos via diretório de entrada
8. **Ordenação de Detalhes**: Ordena registros por código de mensagem e data de movimento
9. **Geração de Arquivo Físico**: Grava arquivo TXT processado em diretório de saída
10. **Notificação por E-mail**: Envia e-mail com arquivo anexo em caso de contingência
11. **Movimentação de Arquivos**: Move arquivos processados para diretório específico (processado/erro)

## 6. Relação entre Entidades

**Entidades Principais:**

- **ProcessamentoArquivoRco**: Entidade agregadora que contém MovimentoCip e LayoutArquivoRco
- **MovimentoCip**: Representa um movimento da CIP com informações do arquivo ZIP
- **LayoutArquivoRco**: Estrutura completa do arquivo RCO (Header, Detalhes, Trailer)
- **LayoutHeaderArquivoRco**: Cabeçalho do arquivo com ISPB, datas inicial/final
- **LayoutDetalheArquivoRco**: Detalhe de movimento (ISPB contraparte, data, código mensagem, quantidades)
- **LayoutTrailerArquivoRco**: Trailer com quantidade total de registros
- **MovimentoRco**: Movimento individual do SPB (débito/crédito, ISPB, data, MSBC, quantidade)
- **MovimentoRcoIspb**: Movimento consolidado por ISPB (quantidades de crédito e débito)
- **Email**: Estrutura de e-mail com remetente, destinatários, assunto, conteúdo e anexos

**Relacionamentos:**
- ProcessamentoArquivoRco (1) -> (1) MovimentoCip
- ProcessamentoArquivoRco (1) -> (1) LayoutArquivoRco
- LayoutArquivoRco (1) -> (1) LayoutHeaderArquivoRco
- LayoutArquivoRco (1) -> (N) LayoutDetalheArquivoRco
- LayoutArquivoRco (1) -> (1) LayoutTrailerArquivoRco

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBSPAG..TbArquivoRCO | tabela | SELECT | Verifica existência de arquivo RCO já processado |
| dbispb..tb_movi_movimento | tabela | SELECT | Consulta movimentos da CIP |
| dbispb..tb_mvgn_movimento_gen | tabela | SELECT | Consulta movimentos genéricos da CIP |
| dbispb..tb_mgum_movimento_gen_usermsg | tabela | SELECT | Recupera partes do arquivo RCO ZIP em Base64 |
| dbispb..tb_ispb_ispb | tabela | SELECT | Lista bancos ativos na CIP |
| sp_se_movimento_tib_369 | stored procedure | EXEC | Consulta movimentos STR/PAG por período |

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema apenas realiza consultas (SELECT) nos bancos de dados.

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| RCO_*.ZIP | leitura | FileServerImpl / SpbService | Arquivo ZIP da CIP com movimentos semanais |
| RCO_*.TXT | leitura | ArquivoRcoService | Arquivo TXT posicional descompactado do ZIP |
| RCO_*.TXT | gravação | ArquivoFisicoWriter | Arquivo TXT processado gravado em diretório de saída |
| Arquivos de contingência (*.ZIP) | leitura | FileServerImpl / ProcessamentoRcoReader | Arquivos manuais para processamento em contingência |
| logback-spring.xml | leitura | Logback | Configuração de logs da aplicação |

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas.

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| SPAG Base Gestão | API REST | Envio de arquivos RCO processados via endpoint `/rco/uploadRco` |
| CA API Gateway | API REST OAuth2 | Envio de e-mails corporativos via endpoint `/v1/corporativo/email` |
| File Server SMB/CIFS | Compartilhamento de arquivos | Leitura/gravação de arquivos RCO em diretórios de rede Windows |
| Banco DBSPAG (SQL Server) | Banco de dados | Consulta de arquivos RCO já processados |
| Banco DBISPB (Sybase) | Banco de dados | Consulta de movimentos CIP e dados do SPB |

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com uso de camadas (config, domain, service, infrastructure, item)
- Uso adequado de padrões Spring Batch (Reader, Processor, Writer)
- Testes unitários abrangentes com boa cobertura
- Uso de Lombok para reduzir boilerplate
- Configurações externalizadas em arquivos YAML
- Uso de interfaces (ports) para abstrair repositórios
- Documentação inline em alguns pontos críticos

**Pontos de Melhoria:**
- Algumas classes com múltiplas responsabilidades (ex: SpbService com muitos métodos)
- Falta de documentação JavaDoc em classes e métodos públicos
- Tratamento de exceções genérico em alguns pontos (catch Exception)
- Uso de variáveis estáticas mutáveis (ArquivoRcoService.arquivoAsBytes)
- Alguns métodos longos que poderiam ser refatorados
- Falta de validações de entrada em alguns serviços
- Configurações hardcoded em alguns testes
- Uso de `System.gc()` explícito (não recomendado)

## 14. Observações Relevantes

1. **Arquitetura Batch**: Sistema projetado para execução agendada (job Kubernetes) com processamento em lote
2. **Modo Contingência**: Suporta processamento manual via diretório de entrada quando parâmetros não são informados
3. **Multi-banco**: Processa arquivos de dois bancos distintos (Votorantim e BV S.A.) com lógica unificada
4. **Segurança**: Utiliza autenticação básica para SPAG e OAuth2 para API Gateway
5. **Infraestrutura**: Preparado para deploy em Kubernetes (Google Cloud Platform) com configurações por ambiente
6. **Parsing Posicional**: Utiliza biblioteca FFPojo para leitura de arquivos de layout fixo
7. **Composite Writer**: Implementa padrão Composite para executar múltiplos writers (arquivo físico + API)
8. **Auditoria**: Integrado com framework de trilha de auditoria do Banco Votorantim
9. **Ambientes**: Suporta múltiplos ambientes (local, des, uat, qa, prd) com configurações específicas
10. **Monitoramento**: Expõe endpoints Actuator para health check e monitoramento