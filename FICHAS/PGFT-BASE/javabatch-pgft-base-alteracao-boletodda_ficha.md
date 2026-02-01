# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java responsável por processar arquivos de retorno da CIP (Câmara Interbancária de Pagamentos) relacionados ao DDA (Débito Direto Autorizado) para alteração de boletos. O sistema lê arquivos compactados (.gz) em formato XML, descompacta, valida e processa as informações de títulos de cobrança, atualizando as informações no banco de dados Sybase. O processamento inclui tratamento de alterações em dados de beneficiários, pagadores, instruções de pagamento, juros, multas, descontos e notas fiscais, além de aplicar regras específicas para pagamento parcial.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `ItemReader` | Lê arquivos XML compactados do diretório de entrada e os disponibiliza para processamento |
| `ItemProcessor` | Descompacta e converte arquivos XML em objetos Java (ADDADOCComplexType) |
| `ItemWriter` | Persiste as informações processadas no banco de dados através da camada de negócio |
| `RegistrarBoletoImpl` | Implementa a lógica de negócio para registro/atualização de boletos DDA |
| `RegistrarBoletoDAOImpl` | Executa operações de banco de dados (consultas e atualizações) relacionadas aos títulos DDA |
| `FileUtil` | Utilitário para manipulação de arquivos (compressão, descompressão, conversão XML, movimentação) |
| `DatabaseConnection` | Gerencia conexões com o banco de dados Sybase |
| `MyResumeStrategy` | Define estratégia de tratamento de erros e códigos de saída do job batch |
| `AbstractDAO` | Classe base para operações de banco de dados com gerenciamento de PreparedStatements |

---

## 3. Tecnologias Utilizadas

- **Java** (versão não especificada no código)
- **Maven** - Gerenciamento de dependências e build
- **Spring Framework 2.0** - Configuração e injeção de dependências
- **BV Framework Batch** (bv-framework-batch.standalone) - Framework proprietário para processamento batch
- **JAXB** - Marshalling/Unmarshalling de XML
- **Sybase** - Banco de dados (servidor: sybdesspb, porta: 6500, database: DBPGF_TES)
- **Bitronix** - Gerenciador de transações (bitronix.tm.resource.jdbc.PoolingDataSource)
- **Log4j 1.2.17** - Logging
- **Apache Commons IO** - Utilitários de I/O
- **JUnit 4.12** - Testes unitários
- **Mockito 1.10.19** - Mocks para testes
- **XStream** - Processamento XML (Base64Encoder)

---

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch sem endpoints REST.

---

## 5. Principais Regras de Negócio

1. **Processamento de Arquivos CIP**: Lê arquivos compactados (.gz) em formato XML UTF-16BE do diretório de entrada
2. **Validação de Títulos**: Busca títulos DDA existentes no banco antes de processar alterações
3. **Regra de Pagamento Parcial**: Quando um título aceita pagamento parcial e há alteração em data de vencimento, data limite de pagamento ou valor do título, o sistema desativa todas as baixas existentes e zera os campos de quantidade de pagamentos parciais e saldo total
4. **Atualização Condicional**: Campos são atualizados apenas quando o indicador de manutenção é "A" (Alterar) ou "E" (Excluir)
5. **Normalização de Datas**: Datas são normalizadas (zerando horas, minutos, segundos e milissegundos) para comparação
6. **Tratamento de Caracteres Especiais**: Remove acentos e caracteres especiais para conformidade com padrões BACEN/CIP
7. **Movimentação de Arquivos**: Após processamento, arquivos são movidos para diretório "processado" (sucesso) ou "rejeitado" (erro)
8. **Formatação de CNPJ/CPF**: Aplica padding à esquerda com zeros (11 dígitos para CPF, 14 para CNPJ)
9. **Gestão de Transações**: Commit/rollback automático por transação de processamento

---

## 6. Relação entre Entidades

**Entidade Principal: TituloDDA**
- Possui relacionamento 1:N com:
  - BeneficiarioOriginal (1:1)
  - BeneficiarioFinal (1:1)
  - Pagador (1:1)
  - SacadorAvalista (0:1)
  - DocumentoTitulo (1:1)
  - InstrucaoPagamentoTitulo (1:1)
  - InstrucaoValorRecebimento (0:1)
  - JurosTitulo (0:N)
  - MultaTitulo (0:N)
  - DescontoTitulo (0:N)
  - NotaFiscal (0:N)
  - Calculo (0:N)
  - BaixaOperacional (0:N)

**DTOs:**
- `TituloDDADTO`: Representa dados básicos do título (código, datas, valor, flag pagamento parcial)
- `TituloCobrancaDTO`: Representa título de cobrança (código, estado CIP, código de barras)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbTituloDDA | Tabela | SELECT | Busca informações de títulos DDA por número de identificação |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbTituloDDA | Tabela | UPDATE | Atualiza informações gerais do título DDA via procedure `PrAtualizarTitulosDda` |
| TbTituloDDABaixaOperacional | Tabela | UPDATE | Desativa baixas operacionais quando há alteração em pagamento parcial |
| TbBeneficiarioOriginalDDA | Tabela | UPDATE | Atualiza dados do beneficiário original via procedure `PrAtualizarBeneficiarioOriginalDda` |
| TbBeneficiarioFinalDDA | Tabela | UPDATE | Atualiza dados do beneficiário final via procedure `PrAtualizarBeneficiarioFinalDda` |
| TbPagadorDDA | Tabela | UPDATE | Atualiza dados do pagador via procedure `PrAtualizarPagadorDda` |
| TbSacadorAvalistaDDA | Tabela | UPDATE | Atualiza dados do sacador avalista via procedure `PrAtualizarSacadorAvalistaDda` |
| TbDocumentoTituloDDA | Tabela | UPDATE | Atualiza documento do título via procedure `PrAtualizarDocTituloDda` |
| TbInstrucaoPagamentoTituloDDA | Tabela | UPDATE | Atualiza instruções de pagamento via procedure `PrAtualizarInstrucaoPagamentoTituloDda` |
| TbInstrucaoValorRecebimentoDDA | Tabela | UPDATE | Atualiza instruções de valor de recebimento via procedure `PrAtualizarInstrucaoValorRecebimentoDda` |
| TbJurosTituloDDA | Tabela | INSERT/DELETE | Gerencia registros de juros via procedures `PrInserirJurosTitulosDda` e `PrExcluirJurosTitulosDda` |
| TbMultaTituloDDA | Tabela | INSERT/DELETE | Gerencia registros de multa via procedures `PrInserirMultaTitulosDda` e `PrExcluirMultaTitulosDda` |
| TbDescontoTituloDDA | Tabela | INSERT/DELETE | Gerencia registros de desconto via procedures `PrInserirDescontoTitulosDda` e `PrExcluirDescontoTitulosDda` |
| TbNotaFiscalDDA | Tabela | INSERT/DELETE | Gerencia notas fiscais via procedures `PrInserirNotaFiscalTitulosDda` e `PrExcluirNotaFiscalTitulosDda` |
| TbCalculoDDA | Tabela | INSERT/DELETE | Gerencia cálculos via procedures `PrInserirCalculoTitulosDda` e `PrExcluirCalculoTitulosDda` |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| Arquivos XML compactados (.gz) | Leitura | `ItemReader` / Diretório configurado em `CAMINHO_RET` | Arquivos de retorno da CIP contendo alterações de boletos DDA |
| Arquivos XML temporários | Gravação/Leitura | `FileUtil` / Diretório `CAMINHO_PROCESSAMENTO_ROBO` | Arquivos XML descompactados temporariamente para processamento |
| Arquivos processados | Gravação | `ItemReader.handleDispose()` / Diretório `CAMINHO_RET_PROCESSADO` | Arquivos movidos após processamento bem-sucedido |
| Arquivos rejeitados | Gravação | `ItemReader.handleDispose()` / Diretório `CAMINHO_RET_REJEITADO` | Arquivos movidos após erro no processamento |
| robo.log | Gravação | Log4j / Diretório `log/` | Log de execução do sistema |
| statistics-{executionId}.log | Gravação | Log4j / Diretório `log/` | Log de estatísticas de execução |

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

---

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas (embora existam constantes definidas para filas JMS no código, elas não são utilizadas neste componente).

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| CIP (Câmara Interbancária de Pagamentos) | Arquivo | Recebe arquivos XML de retorno com alterações de boletos DDA |
| Banco de Dados Sybase (DBPGF_TES) | JDBC | Persiste e consulta informações de títulos DDA |

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades em camadas (batch, business, DAO, util)
- Uso adequado de interfaces e implementações
- Tratamento de exceções com códigos de erro específicos
- Uso de DTOs para transferência de dados
- Logging estruturado com BVLogger
- Testes unitários presentes (embora não enviados completos)

**Pontos Negativos:**
- **Código comentado em excesso**: Múltiplas configurações comentadas nos arquivos de propriedades dificultam manutenção
- **Métodos muito longos**: `RegistrarBoletoDAOImpl.registrarRetornoCIP()` e métodos de atualização são extensos e complexos
- **Duplicação de código**: Múltiplos métodos `prepareStatement` (1 a 8) no `AbstractDAO` indicam design inadequado
- **Hardcoding**: Valores como CNPJ (123), servidor de banco, credenciais em XML
- **Falta de constantes**: Strings mágicas como "A", "E", "S", "N" espalhadas pelo código
- **Tratamento de encoding inconsistente**: Conversões UTF-8/UTF-16BE em múltiplos pontos
- **Métodos com muitos parâmetros**: Alguns métodos possuem mais de 5 parâmetros
- **Falta de validações**: Poucos null-checks antes de operações críticas
- **Comentários em português**: Mistura de português e inglês no código
- **Uso de `System.out.println()`**: Presente em código de produção (`converterXmlParaObjetoErr`)
- **Gestão manual de recursos**: Múltiplos `close()` manuais ao invés de try-with-resources

---

## 14. Observações Relevantes

1. **Ambiente Multi-Ambiente**: O sistema possui configurações para DES, QA, UAT e PROD comentadas, sugerindo deploy manual de configurações
2. **Framework Proprietário**: Utiliza framework BV-Sistemas, o que pode dificultar portabilidade
3. **Processamento Transacional**: Cada arquivo é processado em uma transação única com commit/rollback automático
4. **Encoding Específico**: Arquivos CIP utilizam UTF-16BE, requerendo conversão específica
5. **XSD Schemas**: Existem schemas XSD para validação (ADDA102.xsd, etc.) mas não foram enviados
6. **Procedures Sybase**: Toda persistência é feita via stored procedures, encapsulando lógica no banco
7. **Nomenclatura de Arquivos**: Segue padrão CIP com sufixos PRO (processamento), ERR (erro), RR2 (retorno tipo 2)
8. **Código de Erro 0000**: Definido como `CODIGO_ERRO_TITULO_REJEITADO_CIP` mas não utilizado no código enviado
9. **Dependências Antigas**: Log4j 1.2.17 (EOL), Spring 2.0 (muito antiga), JUnit 4 (JUnit 5 é atual)
10. **Segurança**: Credenciais de banco expostas em arquivos XML de configuração