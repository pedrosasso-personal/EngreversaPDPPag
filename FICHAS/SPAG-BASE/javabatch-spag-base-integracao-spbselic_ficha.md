# Ficha Técnica do Sistema

## 1. Descrição Geral
O sistema **javabatch-spag-base-integracao-spbselic** é um job batch Java desenvolvido para integração com o sistema SELIC (Sistema Especial de Liquidação e Custódia) do Banco Central do Brasil. Sua principal função é realizar o download de arquivos ARASEL023 via FTP do servidor SELIC, processar esses arquivos descriptografando-os através do sistema SPB (Sistema de Pagamentos Brasileiro), extrair informações de movimentações financeiras e enviar relatórios por e-mail para áreas responsáveis. O sistema opera em duas etapas: DOWNLOAD (busca arquivos via FTP) e PROCESSING (processa e envia relatórios).

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Responsável por inicializar o job, definir a etapa de execução (download ou processamento) e fornecer os dados para processamento |
| **ItemProcessor** | Processa cada linha do arquivo ARASEL023, convertendo strings em objetos ARASEL023Line através do mapper |
| **ItemWriter** | Grava as informações processadas no repositório de e-mail para posterior envio |
| **SpbSelicService** | Serviço principal que orquestra o download de arquivos FTP, processamento e envio de relatórios |
| **SelicFTPRepository** | Implementa operações de FTP para conexão e download de arquivos do servidor SELIC |
| **EmailRepository** | Gerencia a construção e envio de e-mails com arquivos CSV anexados |
| **ARASEL023Mapper** | Realiza o mapeamento (parsing) das linhas do arquivo ARASEL023 para objetos de domínio |
| **MovimentoDaoImpl** | DAO para consulta de movimentos no banco de dados ISPB (atualmente comentado) |
| **FTPHelper** | Classe utilitária com métodos auxiliares para operações FTP |
| **FileUtil** | Utilitário para manipulação de arquivos (leitura, verificação de existência, geração de nomes) |
| **DateUtil** | Utilitário para conversão e manipulação de datas em diversos formatos |

---

## 3. Tecnologias Utilizadas

- **Java** (linguagem principal)
- **Maven** (gerenciamento de dependências e build)
- **Spring Framework** (injeção de dependências e configuração via XML)
- **BV Framework Batch** (framework proprietário para jobs batch)
- **Apache Commons Net** (cliente FTP)
- **Apache Commons IO** (manipulação de I/O)
- **Apache Commons Logging/Log4j** (logging)
- **JavaMail API** (envio de e-mails)
- **Bitronix** (gerenciador de transações JTA)
- **JUnit** (testes unitários)
- **Mockito** (mocks para testes)
- **MockFtpServer** (servidor FTP mock para testes)

---

## 4. Principais Endpoints REST
não se aplica

---

## 5. Principais Regras de Negócio

1. **Download de Arquivos SELIC**: O sistema conecta-se ao servidor FTP da SELIC usando ISPBs específicos (59588111 e 01858774) como credenciais de acesso
2. **Validação de Data**: O arquivo processado deve ter data de movimento dentro de um intervalo válido (data de processamento + até 3 dias), caso contrário o arquivo é descartado
3. **Descriptografia via SPB**: Arquivos baixados são copiados para diretório do SPB para descriptografia antes do processamento
4. **Filtragem por ISPB**: O sistema processa apenas movimentações relacionadas aos ISPBs do Banco Votorantim
5. **Geração de Relatórios CSV**: Para cada ISPB encontrado no arquivo, gera um CSV separado com as movimentações
6. **Envio de E-mail**: Envia e-mail com anexos CSV para lista de destinatários configurada por ambiente (DES/UAT/PRD)
7. **Controle de Reprocessamento**: Verifica se arquivo já foi processado anteriormente para evitar duplicidade
8. **Execução em Etapas**: Permite execução separada de download e processamento através do parâmetro ETAPA
9. **Parametrização Flexível**: Aceita parâmetros de data, ISPB específico e etapa de execução

---

## 6. Relação entre Entidades

**Entidades de Domínio:**

- **ARASEL023File**: Representa o arquivo completo com header, linhas e trailer
  - Contém: 1 ARASEL023Header, N ARASEL023Line, 1 ARASEL023Trailer

- **ARASEL023Header**: Cabeçalho do arquivo
  - Atributos: tipoRegistro, dataMovimento, dataGeracaoArquivo, horaMinutoGeracaoArquivo

- **ARASEL023Line**: Linha de detalhe com informações de movimentação
  - Atributos: tipoRegistro, codigoOperacao, numeroOperacaoPagamento, numeroContaCedente, iSelicResponsavelCedente, numeroContaCessionaria, iSelicResponsavelCessionaria, indicadorDebitoCredito, codigoIdentificacaoTitulo, dataVencimentoTitulo, codigoIsin, precoUnitarioPagamento, quantidadeTitulos, valorFinanceiroPagamento, numeroControleSTR, situacaoOperacaoSelic, dataHoraRegistroSituacao, ispb

- **ARASEL023Trailer**: Rodapé do arquivo
  - Atributos: tipoRegistro, totalRegistros

- **Movimento**: Entidade para consulta no banco de dados
  - Atributos: identdArq, nomArq

- **SelicFTPProperties**: Configurações para conexão FTP e processamento
  - Atributos: ispbList, processDate, host, port, fileName, downloadDir, processingDir, processedDir

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| tb_movi_movimento | tabela | SELECT | Tabela de movimentos (código comentado, não utilizado atualmente) |
| tb_mvgn_movimento_gen | tabela | SELECT | Tabela de movimentos genéricos (código comentado, não utilizado atualmente) |

**Observação**: As consultas ao banco de dados estão comentadas no código atual, indicando que o sistema não está utilizando banco de dados na versão analisada.

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| ARASEL023 | leitura | SelicFTPRepository / SpbSelicService | Arquivo de movimentações SELIC baixado via FTP |
| ARASEL023_{ISPB}_{DATA}#01#47#000#00038121#{ispb}#SPB.dda | gravação | SpbSelicService.downloadFile() | Arquivo baixado salvo no diretório de processamento para descriptografia |
| ARASEL023_{ISPB}_{DATA} | leitura | SpbSelicService.processFile() | Arquivo descriptografado lido do diretório processado |
| ARASEL023-{ISPB}-{DATA}.csv | gravação | EmailRepository | Arquivo CSV gerado e anexado ao e-mail com movimentações por ISPB |
| roboIntegracaoSpbSelic.log | gravação | Log4j | Arquivo de log da aplicação |
| statistics-{executionId}.log | gravação | BvDailyRollingFileAppender | Arquivo de estatísticas de execução do batch |

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
| **Servidor FTP SELIC** | FTP | Servidor do Banco Central (ftp-p.selic.rsfn.net.br em PRD, ftp-t.selic.rsfn.net.br em DES/UAT) para download de arquivos ARASEL023 |
| **Sistema SPB (CriptoSFNArq)** | Sistema de Arquivos | Sistema de descriptografia de arquivos do SPB através de diretórios compartilhados (in/ e out2/) |
| **Servidor SMTP** | E-mail | Servidor de e-mail (smtprelay.bvnet.bv em PRD, smtpduqrelay.bvnet.bv em DES/UAT) para envio de relatórios |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 6/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com uso de padrões (DAO, Repository, Service)
- Uso adequado de interfaces para abstrair implementações
- Configuração externalizada por ambiente (DES/UAT/PRD)
- Presença de testes unitários e de integração
- Uso de enums para códigos de saída e steps
- Logging adequado em pontos críticos

**Pontos Negativos:**
- Código de acesso a banco de dados comentado, indicando funcionalidade incompleta ou abandonada
- Mistura de português e inglês em nomes de variáveis e comentários
- Falta de tratamento de exceções mais específico em alguns pontos
- Hardcoding de strings em várias partes do código (ex: sufixos de arquivo, formatos)
- Falta de documentação JavaDoc nas classes e métodos
- Uso de encoding ISO-8859-1 em alguns arquivos XML
- Dependência de diretórios de rede Windows (\\bvnet\mor\...) que dificulta portabilidade
- Classe MyResumeStrategy com implementação vazia (TODO não implementado)
- Uso de framework proprietário (BV Framework) que dificulta manutenção por terceiros

---

## 14. Observações Relevantes

1. **Ambientes**: O sistema possui configurações específicas para três ambientes (DES, UAT, PRD) com diferentes servidores FTP, diretórios e destinatários de e-mail

2. **ISPBs do Banco Votorantim**: O sistema trabalha com dois ISPBs: 59588111 e 01858774

3. **Formato do Arquivo ARASEL023**: Arquivo posicional com três tipos de registro:
   - Tipo 0: Header
   - Tipo 1: Detalhe (movimentações)
   - Tipo 2: Trailer

4. **Execução Parametrizada**: O job aceita três parâmetros opcionais:
   - DATA (formato AAAAMMDD)
   - ISPB (para processar apenas um ISPB específico)
   - ETAPA (DOWNLOAD ou PROCESSING)

5. **Fluxo de Descriptografia**: O sistema depende de um processo externo (SPB CriptoSFNArq) para descriptografar os arquivos baixados

6. **Validação de Data Flexível**: Aceita arquivos com data de movimento de até 3 dias após a data de processamento

7. **Código Legado**: Presença de código comentado e TODOs não implementados sugerem que o sistema passou por evoluções e possui funcionalidades planejadas não concluídas

8. **Framework Proprietário**: Uso intensivo do BV Framework Batch, que é um framework proprietário do Banco Votorantim