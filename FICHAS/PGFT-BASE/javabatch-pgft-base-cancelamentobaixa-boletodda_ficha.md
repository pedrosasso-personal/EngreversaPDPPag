# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java desenvolvido para processar arquivos de cancelamento de baixa operacional de boletos DDA (Débito Direto Autorizado) retornados pela CIP (Câmara Interbancária de Pagamentos). O sistema lê arquivos XML compactados (.gz), descompacta, valida, processa as informações de cancelamento de baixa operacional e atualiza o banco de dados, movendo os arquivos processados para diretórios específicos conforme o resultado do processamento (processado ou rejeitado).

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê arquivos XML compactados do diretório de entrada, renomeia se necessário e disponibiliza para processamento |
| **ItemProcessor** | Converte o arquivo XML em objeto Java (ADDADOCComplexType) utilizando a classe FileUtil |
| **ItemWriter** | Processa os dados convertidos, identifica o tipo de arquivo (RR2) e executa o registro do retorno CIP no banco de dados |
| **RegistrarBoletoImpl** | Implementa a lógica de negócio para registrar o retorno da CIP |
| **RegistrarBoletoDAOImpl** | Executa operações de banco de dados: busca baixa, busca título e atualiza/cancela baixa operacional |
| **FileUtil** | Utilitário para manipulação de arquivos: descompactação, conversão XML/Objeto, movimentação de arquivos |
| **DatabaseConnection** | Gerencia conexões com o banco de dados através de DataSource |
| **MyResumeStrategy** | Estratégia de tratamento de erros e definição de códigos de saída do job |
| **Baixa** | DTO representando uma baixa operacional |
| **TituloDDA** | DTO representando um título DDA |

## 3. Tecnologias Utilizadas

- **Framework Batch**: Spring Batch (BV Framework Batch Standalone)
- **Linguagem**: Java
- **Build**: Maven
- **Banco de Dados**: Sybase (driver JTDS)
- **Pool de Conexões**: Bitronix Transaction Manager
- **Marshalling/Unmarshalling XML**: JAXB
- **Compressão**: GZIP
- **Logging**: Log4j + BVLogger
- **Testes**: JUnit
- **Encoding**: UTF-16BE para arquivos XML

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch que não expõe endpoints REST.

## 5. Principais Regras de Negócio

1. **Processamento de Arquivos RR2**: Apenas arquivos contendo "RR2" no nome são processados para cancelamento de baixa operacional
2. **Validação de Baixa**: Busca a baixa operacional pelo número de identificação antes de processar o cancelamento
3. **Validação de Título**: Verifica a existência do título DDA associado à baixa antes de cancelar
4. **Recálculo de Valor**: Ao cancelar a baixa, o valor do título é recalculado somando o valor atual com o valor da baixa cancelada
5. **Movimentação de Arquivos**: Arquivos processados com sucesso são movidos para diretório "processado", arquivos com erro vão para "rejeitado"
6. **Renomeação de Arquivos**: Arquivos sem extensão .gz são automaticamente renomeados para incluir a extensão
7. **Tratamento de Erros**: Erros são categorizados com códigos específicos (11-15) para facilitar diagnóstico

## 6. Relação entre Entidades

**TituloDDA** (1) ←→ (N) **Baixa**
- Um título DDA pode ter múltiplas baixas operacionais
- Relacionamento através do campo `CdTituloDDA`

**ADDADOCComplexType** (estrutura XML)
- Contém BCARQ (informações do arquivo)
- Contém SISARQ (informações do sistema)
  - ADDA115RR2 (cancelamento de baixa)
    - Grupo_ADDA115RR2_Tit (lista de títulos)

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbTituloDDABaixaOperacional | Tabela | SELECT | Busca informações da baixa operacional pelo número de identificação |
| TbTituloDDA | Tabela | SELECT | Busca informações do título DDA e seu valor atual/saldo |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbTituloDDABaixaOperacional | Tabela | UPDATE | Cancela a baixa operacional através da procedure PrCancelarTituloDDABaixaOperacional |
| TbTituloDDA | Tabela | UPDATE | Atualiza o valor do título após cancelamento da baixa (via procedure) |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| ADDA115RR2_*.gz | Leitura | ItemReader / FileUtil | Arquivo XML compactado com dados de cancelamento de baixa operacional retornado pela CIP |
| processamento.xml | Gravação | FileUtil.salvarArquivoXML | Arquivo XML temporário descompactado para processamento |
| ADDA115RR2_*.gz | Movimentação | ItemReader.handleDispose | Arquivo movido para diretório "processado" ou "rejeitado" conforme resultado |
| robo.log | Gravação | Log4j | Log de execução do sistema |
| statistics-*.log | Gravação | BvDailyRollingFileAppender | Log de estatísticas de execução |

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas.

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| CIP (Câmara Interbancária de Pagamentos) | Arquivo | Recebe arquivos XML de retorno de cancelamento de baixa operacional de boletos DDA |
| Banco de Dados Sybase (DBPGF_TES) | JDBC | Conexão para leitura e atualização de dados de títulos e baixas operacionais |

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades entre camadas (Reader, Processor, Writer, DAO, Business)
- Uso adequado de DTOs para transferência de dados
- Tratamento de exceções com códigos de erro específicos
- Logging estruturado em pontos importantes
- Uso de interfaces para contratos de serviço

**Pontos Negativos:**
- Código com comentários em português e encoding ISO-8859-1, dificultando manutenção
- Classe `AbstractDAO` com múltiplos PreparedStatements (1 a 8) sem justificativa clara, indicando possível design inadequado
- Falta de tratamento adequado de recursos (try-with-resources) em várias classes
- Hardcoded de credenciais de banco de dados nos arquivos de configuração
- Falta de testes unitários (apenas um teste de integração)
- Uso de `printStackTrace()` em alguns pontos ao invés de logging adequado
- Classe `FileUtil` muito extensa com múltiplas responsabilidades
- Falta de validações de entrada em vários métodos
- Uso de `System.out.println()` em código de produção (FileUtil)

## 14. Observações Relevantes

1. **Ambiente de Desenvolvimento**: O sistema possui configurações para múltiplos ambientes (DES, QA, UAT, PROD) comentadas no arquivo de propriedades
2. **Encoding Específico**: O sistema trabalha com encoding UTF-16BE para os arquivos XML da CIP, o que é crítico para o correto processamento
3. **XSD Schemas**: O projeto inclui schemas XSD completos (ADDA115.xsd, ADDA115ERR.xsd, ADDA115PRO.xsd, ADDATIPOS.xsd) para validação dos arquivos XML
4. **Procedure de Banco**: O cancelamento da baixa é realizado através da stored procedure `PrCancelarTituloDDABaixaOperacional`
5. **Versionamento**: Projeto configurado para uso com Git e integração com Jenkins
6. **Framework Proprietário**: Utiliza framework BV-Sistemas, indicando que é um sistema desenvolvido para o Banco Votorantim
7. **Processamento em Lote**: O sistema está preparado para processar múltiplos arquivos em sequência
8. **Tipos de Arquivo**: O sistema diferencia entre arquivos de protocolo (PRO), erro (ERR) e retorno (RR2), processando apenas os RR2 para cancelamento de baixa