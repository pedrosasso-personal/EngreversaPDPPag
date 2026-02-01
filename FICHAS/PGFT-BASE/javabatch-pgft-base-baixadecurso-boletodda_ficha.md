---
## Ficha Técnica do Sistema

### 1. Descrição Geral
Sistema batch Java desenvolvido para processar arquivos de retorno DDA (Débito Direto Autorizado) relacionados a baixa de boletos por decurso de prazo. O sistema lê arquivos XML compactados (.gz) enviados pela CIP (Câmara Interbancária de Pagamentos), descompacta, valida e processa as informações de baixa de títulos, atualizando o banco de dados com as informações de baixa efetiva dos boletos.

O processamento segue o padrão Spring Batch com arquitetura Reader-Processor-Writer, onde:
- **Reader**: Lê arquivos compactados do diretório de entrada
- **Processor**: Descompacta e converte XML para objetos Java (JAXB)
- **Writer**: Registra as baixas de títulos no banco de dados

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `ItemReader` | Lê arquivos .gz do diretório de entrada e gerencia o fluxo de processamento |
| `ItemProcessor` | Descompacta arquivos e converte XML para objetos ADDADOCComplexType |
| `ItemWriter` | Persiste informações de baixa de títulos no banco de dados |
| `RegistrarBoletoImpl` | Implementa lógica de negócio para registro de retorno CIP |
| `RegistrarBoletoDAOImpl` | Acesso a dados para buscar títulos e inserir baixas efetivas |
| `FileUtil` | Utilitários para manipulação de arquivos (compressão, conversão, validação) |
| `DatabaseConnection` | Gerenciamento de conexões com banco de dados |
| `MyResumeStrategy` | Estratégia de tratamento de erros e códigos de saída |
| `TituloDDA` | DTO representando título DDA |
| Classes `vo.*` | Value Objects gerados por JAXB a partir dos XSDs ADDA120 e ADDATIPOS |

### 3. Tecnologias Utilizadas
- **Java** (versão não especificada no código)
- **Spring Batch** (framework de processamento batch)
- **Spring Framework** (injeção de dependências e configuração)
- **Maven** (gerenciamento de dependências e build)
- **JAXB** (Java Architecture for XML Binding - conversão XML/Objeto)
- **Bitronix** (gerenciador de transações JTA)
- **BV Framework** (framework proprietário BV Sistemas para batch, logging e JDBC)
- **Sybase** (banco de dados - servidor sybdesspb, database DBPGF_TES)
- **JUnit** (testes unitários)
- **Commons IO** (manipulação de arquivos)
- **XStream** (processamento XML e Base64)

### 4. Principais Endpoints REST
Não se aplica. Este é um sistema batch sem endpoints REST.

### 5. Principais Regras de Negócio
1. **Processamento de Arquivos DDA**: O sistema processa exclusivamente arquivos ADDA120 (baixa por decurso de prazo) enviados pela CIP
2. **Descompactação e Validação**: Arquivos são recebidos compactados em formato .gz e codificados em UTF-16BE, sendo descompactados e validados contra XSD
3. **Busca de Títulos**: Para cada título informado no arquivo, o sistema busca no banco de dados pelo número de identificação do título
4. **Registro de Baixa Efetiva**: Apenas títulos encontrados no banco têm suas baixas registradas através da procedure `PrInserirTituloDDABaixaEfetiva`
5. **Movimentação de Arquivos**: Após processamento, arquivos são movidos para diretório "processado" (sucesso) ou "rejeitado" (erro)
6. **Tratamento de Erros**: Sistema possui códigos de erro específicos (11-15) para diferentes tipos de falha no processamento
7. **Transacionalidade**: Cada arquivo é processado em uma transação independente com commit/rollback automático

### 6. Relação entre Entidades
**Entidades Principais:**
- `TituloDDA`: Representa um título DDA no banco de dados
  - Atributos: cdTitulo (Integer), valorTitulo (BigDecimal)

**Entidades XML (geradas por JAXB):**
- `ADDADOCComplexType`: Documento raiz do arquivo DDA
  - Contém: BCARQ (cabeçalho), SISARQ (sistema/arquivo), ESTARQ (estímulo)
- `BCARQComplexType`: Cabeçalho do arquivo com metadados
- `SISARQComplexType`: Container do tipo de mensagem
- `ADDA120ComplexType`: Mensagem específica de baixa por decurso de prazo
  - Contém lista de: GrupoADDA120TitComplexType
- `GrupoADDA120TitComplexType`: Informações de cada título baixado
  - Atributos principais: NumIdentcTit, DtHrSitTit, VlrTotPgto, NumUltIdentcBaixa, SitTitPgto

**Relacionamentos:**
- ADDADOCComplexType 1 ---> 1 SISARQComplexType
- SISARQComplexType 1 ---> 1 ADDA120ComplexType
- ADDA120ComplexType 1 ---> N GrupoADDA120TitComplexType
- GrupoADDA120TitComplexType N ---> 1 TituloDDA (via NumIdentcTit)

### 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbTituloDDA | Tabela | SELECT | Busca títulos DDA por número de identificação para validar existência antes de registrar baixa |

### 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbTituloDDABaixaEfetiva (via procedure) | Tabela | INSERT | Registra baixa efetiva de títulos DDA através da stored procedure PrInserirTituloDDABaixaEfetiva |

### 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| ADDA120_*.gz | Leitura | ItemReader / FileUtil | Arquivos compactados de retorno DDA da CIP contendo informações de baixa de títulos |
| processamento.xml_* | Gravação temporária | FileUtil.salvarArquivoXML | Arquivo XML temporário descompactado para conversão JAXB (deletado após processamento) |
| ADDA120_*.gz | Movimentação | ItemReader.handleDispose | Arquivo original movido para diretório "processado" ou "rejeitado" conforme resultado |
| config.properties | Leitura | Resources / Propriedades | Arquivo de configuração com caminhos de diretórios |
| job-definitions.xml | Leitura | Spring Context | Definições de beans e configuração do job batch |
| job-resources.xml | Leitura | Spring Context | Configuração de datasources e recursos |

### 10. Filas Lidas
Não se aplica. O sistema não consome mensagens de filas.

### 11. Filas Geradas
Não se aplica. O sistema não publica mensagens em filas.

### 12. Integrações Externas
1. **CIP (Câmara Interbancária de Pagamentos)**: Sistema recebe arquivos de retorno DDA gerados pela CIP contendo informações de baixa de boletos por decurso de prazo
2. **Banco de Dados Sybase**: Integração com servidor `sybdesspb` porta 6500, database `DBPGF_TES`, para consulta e atualização de títulos DDA

### 13. Avaliação da Qualidade do Código

**Nota: 5/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem definida seguindo padrão Spring Batch (Reader-Processor-Writer)
- Uso de JAXB para binding XML/Objeto garante type-safety
- Separação de responsabilidades em camadas (DAO, Business, Util)
- Tratamento de erros com códigos específicos
- Uso de framework de logging estruturado

**Pontos Negativos:**
- **Código legado com práticas desatualizadas**: Uso de classes deprecated, comentários em português misturados com código
- **Gerenciamento manual de conexões**: DatabaseConnection com singleton estático é anti-pattern, deveria usar pool gerenciado pelo Spring
- **Falta de tratamento de exceções específico**: Muitos blocos catch genéricos com apenas log
- **Hardcoded values**: Credenciais de banco em XML, caminhos de arquivo em properties
- **Falta de testes**: Apenas um teste de integração básico, sem testes unitários
- **Código duplicado**: Múltiplos PreparedStatements (1-8) no AbstractDAO sem justificativa clara
- **Falta de documentação**: Javadoc incompleto ou ausente na maioria das classes
- **Mistura de responsabilidades**: FileUtil tem métodos muito diversos (compressão, conversão, validação, Base64)
- **Uso de tipos primitivos wrapper desnecessariamente**: Muitos Integer onde int seria suficiente
- **Falta de validações**: Pouca validação de entrada antes de processar

### 14. Observações Relevantes
1. **Ambiente Multi-Ambiente**: Sistema possui configurações para DES, QA, UAT e PROD comentadas no config.properties
2. **Encoding Específico**: Arquivos DDA utilizam encoding UTF-16BE, requerendo conversão específica
3. **Formato de Arquivo**: Arquivos seguem padrão XML da CIP com schemas ADDA120.xsd e ADDATIPOS.xsd
4. **Processamento Assíncrono**: Sistema suporta execução concorrente (concurrentExecution=true)
5. **Cleanup Automático**: Sistema remove arquivos de log do Bitronix (.tlog) após execução
6. **Versionamento**: Projeto usa versionamento semântico (0.1.0)
7. **Framework Proprietário**: Forte dependência do BV Framework (bv-sistemas), dificultando portabilidade
8. **Stored Procedure**: Lógica de inserção de baixa está encapsulada em procedure `PrInserirTituloDDABaixaEfetiva` com 11 parâmetros
9. **Parâmetros de Execução**: Job recebe nome do arquivo como parâmetro via linha de comando
10. **Estratégia de Retry**: Sistema não implementa retry automático, falhas resultam em movimentação para diretório rejeitado