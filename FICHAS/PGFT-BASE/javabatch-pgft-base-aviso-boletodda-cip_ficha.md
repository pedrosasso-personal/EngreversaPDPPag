# Ficha Técnica do Sistema

## 1. Descrição Geral
Sistema batch Java desenvolvido para processar arquivos de retorno DDA (Débito Direto Autorizado) provenientes da CIP (Câmara Interbancária de Pagamentos). O sistema realiza a leitura de arquivos compactados (.gz) contendo XMLs com informações de títulos de cobrança (boletos), descompacta, converte para objetos Java, persiste os dados em banco de dados Sybase e envia notificações via RabbitMQ para sistemas consumidores.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê arquivos .gz do diretório de entrada, valida existência e prepara para processamento |
| **ItemProcessor** | Descompacta e converte arquivos XML em objetos Java (ADDADOCComplexType) |
| **ItemWriter** | Persiste dados no banco de dados e envia notificações via RabbitMQ |
| **RegistrarBoletoImpl** | Implementa regras de negócio para registro de retorno CIP |
| **RegistrarBoletoDAOImpl** | Executa operações de banco de dados (insert/delete) via stored procedures |
| **FileUtil** | Utilitário para manipulação de arquivos (descompressão, conversão XML, movimentação) |
| **ADDA101RR2MapperImpl** | Converte objetos de domínio em DTOs para notificação |
| **DatabaseConnection** | Gerencia conexões com banco de dados Sybase |
| **MyResumeStrategy** | Estratégia de tratamento de erros e definição de códigos de saída |

## 3. Tecnologias Utilizadas
- **Framework Batch**: Spring Batch (BV Framework Batch Standalone)
- **Linguagem**: Java
- **Build**: Maven
- **Banco de Dados**: Sybase (DBPGF_TES)
- **Driver JDBC**: BVJTDSDataSource (customizado)
- **Mensageria**: RabbitMQ (Spring AMQP)
- **Gerenciamento de Transações**: Bitronix (JTA)
- **Marshalling/Unmarshalling**: JAXB
- **Logging**: Log4j + BVLogger
- **Serialização JSON**: Gson
- **Criptografia**: BVCrypto

## 4. Principais Endpoints REST
Não se aplica - sistema batch sem endpoints REST.

## 5. Principais Regras de Negócio
1. **Processamento de Arquivos DDA**: Lê arquivos compactados (.gz) contendo XMLs de retorno da CIP com informações de títulos de cobrança
2. **Validação de Formato**: Identifica tipo de arquivo (RR2, PRO, ERR) e aplica parser específico
3. **Exclusão Prévia**: Remove títulos existentes antes de inserir novos dados (evita duplicação)
4. **Persistência Completa**: Insere título principal e entidades relacionadas (juros, multa, descontos, notas fiscais, cálculos)
5. **Sanitização de Dados**: Remove caracteres especiais e acentuação para compatibilidade com padrões BACEN/CIP
6. **Formatação de Documentos**: Padroniza CNPJ/CPF com zeros à esquerda conforme tipo de pessoa
7. **Notificação Assíncrona**: Envia mensagem RabbitMQ para cada título processado (ADDA101RR2)
8. **Movimentação de Arquivos**: Move arquivos processados para diretório específico (processado/rejeitado) conforme resultado
9. **Tratamento de Erros**: Códigos de erro específicos para cada tipo de falha (11-15)
10. **Controle Transacional**: Commit individual por título com rollback em caso de erro

## 6. Relação entre Entidades
- **TituloDDA** (entidade principal)
  - Contém 1 **JurosTitulo** (opcional)
  - Contém 1 **MultaTitulo** (opcional)
  - Contém N **DescontoTitulo** (0..N)
  - Contém N **NotaFiscalTitulo** (0..N)
  - Contém N **CalculoTitulo** (0..N)

Relacionamento: Um título DDA pode ter múltiplos descontos, notas fiscais e cálculos, mas apenas um registro de juros e multa.

## 7. Estruturas de Banco de Dados Lidas
Não se aplica - o sistema não realiza operações de leitura (SELECT) no banco de dados.

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TituloDDA | Tabela | DELETE | Exclusão de títulos existentes via PrExcluirTituloDDA |
| TituloDDA | Tabela | INSERT | Inserção de títulos DDA via PrInserirTitulosDda (65 parâmetros) |
| JurosTituloDDA | Tabela | INSERT | Inserção de juros do título via PrInserirJurosTitulosDda |
| MultaTituloDDA | Tabela | INSERT | Inserção de multa do título via PrInserirMultaTitulosDda |
| DescontoTituloDDA | Tabela | INSERT | Inserção de descontos do título via PrInserirDescontoTitulosDda |
| NotaFiscalTituloDDA | Tabela | INSERT | Inserção de notas fiscais do título via PrInserirNotaFiscalTitulosDda |
| CalculoTituloDDA | Tabela | INSERT | Inserção de cálculos do título via PrInserirCalculoTitulosDda |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| *.gz (entrada) | Leitura | ItemReader / FileUtil | Arquivos compactados contendo XMLs de retorno CIP |
| processamento.xml | Gravação temporária | FileUtil.salvarArquivoXML | XML descompactado temporário para parsing |
| *.gz (processado) | Movimentação | ItemReader.handleDispose | Arquivos processados com sucesso |
| *.gz (rejeitado) | Movimentação | ItemReader.handleDispose | Arquivos com erro no processamento |
| robo.log | Gravação | Log4j | Log de execução do batch |
| statistics-*.log | Gravação | BvDailyRollingFileAppender | Estatísticas de execução |

## 10. Filas Lidas
Não se aplica - o sistema não consome mensagens de filas.

## 11. Filas Geradas

| Nome da Fila/Exchange | Tipo | Descrição |
|-----------------------|------|-----------|
| events.business.tituloPagadorDda | Exchange RabbitMQ | Notificações de títulos processados (ADDA101RR2) contendo código da mensagem e número de identificação do título |

## 12. Integrações Externas
1. **CIP (Câmara Interbancária de Pagamentos)**: Recebe arquivos de retorno DDA via diretório compartilhado
2. **RabbitMQ**: Envia notificações de títulos processados para sistemas consumidores
3. **Banco Sybase (DBPGF_TES)**: Persiste dados de títulos DDA e entidades relacionadas

## 13. Avaliação da Qualidade do Código

**Nota: 5/10**

**Justificativa:**
- **Pontos Positivos**: Uso de framework batch estruturado (Spring Batch), separação de responsabilidades em camadas (Reader/Processor/Writer), uso de interfaces e DTOs, tratamento de erros com códigos específicos
- **Pontos Negativos**: 
  - Código comentado extensivamente (poluição visual)
  - Método `inserirTitulo` extremamente longo (200+ linhas) com 65 parâmetros
  - Falta de testes unitários adequados
  - Uso de código legado comentado sem remoção
  - Mistura de responsabilidades (FileUtil faz parsing, conversão e movimentação)
  - Hardcoded de valores (CNPJ_BV = 123)
  - Falta de documentação JavaDoc
  - Tratamento de exceções genérico em alguns pontos
  - Uso de `System.out` em logs (logger.workflow.error imprimindo objetos)

## 14. Observações Relevantes
1. **Ambiente Configurável**: Sistema possui configurações comentadas para DES/QA/UAT/PROD, mas não utiliza profiles adequadamente
2. **Encoding**: Arquivos XML utilizam UTF-16BE, requerendo tratamento especial na descompressão
3. **Sanitização Obrigatória**: Remove acentuação e caracteres especiais para conformidade com padrões BACEN/CIP
4. **Transações Bitronix**: Utiliza gerenciador de transações JTA com arquivos .tlog que são removidos após execução
5. **Execução via BAT**: Sistema executado via script batch Windows com parâmetros (nome do robô, execution ID, nome do arquivo)
6. **Códigos de Retorno**: Sistema retorna códigos específicos (11-15) para diferentes tipos de erro
7. **Processamento Síncrono**: Apesar de usar Spring Batch, processa um arquivo por vez (não há paralelização)
8. **Dependências Customizadas**: Utiliza bibliotecas proprietárias BV (bv-framework, bv-crypto, bv-jdbcdriver)