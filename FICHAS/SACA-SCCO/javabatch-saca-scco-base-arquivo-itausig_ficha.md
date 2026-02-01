# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de processamento batch desenvolvido em Java para leitura e carga de arquivos de remessa bancária no formato CNAB400 do Itaú SIG. O sistema realiza a leitura de arquivos de cobrança bancária, valida os dados conforme o layout CNAB400, e persiste as informações de boletos e instrumentos de cobrança em banco de dados (DBCARNE e DBCOR). O processamento segue o padrão Reader-Processor-Writer do Spring Batch.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê arquivos CNAB400 do diretório configurado e carrega linhas em memória |
| **ItemProcessor** | Converte strings CNAB em objetos de domínio (RemessaVO) através de conversores específicos |
| **ItemWriter** | Valida dados e persiste informações de boletos no banco de dados |
| **DatabaseConnection** | Gerencia conexões JDBC com controle manual de transações |
| **ManipulaBoletoDAO** | Executa operações de inserção nas tabelas de instrumento de cobrança |
| **ValidarHeader/DetalhesPrincipal/DetalhesSacador/Boleto/Trailler** | Classes de validação de layout CNAB400 |
| **ConverteStringTo[Header/DetalhePrincipal/etc]** | Conversores de string CNAB para objetos VO |
| **RemessaVO/DetalheRemessaVO/HeaderVO/TraillerVO** | Value Objects representando estrutura CNAB400 |

---

## 3. Tecnologias Utilizadas

- **Java** (versão não especificada no código)
- **Spring Batch** (framework de processamento batch)
- **Maven** (gerenciamento de dependências e build)
- **BV Framework Batch** (framework proprietário da BV Sistemas)
- **JDBC** (acesso a banco de dados)
- **Sybase/SQL Server** (banco de dados - schemas DBCARNE e DBCOR)
- **Spring Framework** (injeção de dependências)
- **Log4j** (logging)

---

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch sem endpoints REST.

---

## 5. Principais Regras de Negócio

1. **Validação de Layout CNAB400**: Validação rigorosa de todos os campos obrigatórios conforme especificação Itaú (tipo de registro, códigos, literais, etc.)
2. **Tipo de Registro**: Header (0), Detalhe Principal (1), Detalhe Sacador (5), Boleto Frente (7), Boleto Verso (8), Trailler (9)
3. **Código Banco**: Deve ser sempre 341 (Itaú)
4. **Aceite**: Apenas valores "A" (aceito) ou "N" (não aceito)
5. **Tipo de Pessoa**: Conversão de códigos CNAB (01=PF, 02=PJ) para formato interno (F/J)
6. **Situação de Processamento**: Boletos inseridos com situação "Pendente de Registro" (código 1)
7. **Consolidação de Múltiplos Arquivos**: Sistema processa múltiplos arquivos CNAB em um único lote, consolidando em um único header/trailler
8. **Controle Transacional**: Rollback completo em caso de erro durante processamento

---

## 6. Relação entre Entidades

**RemessaVO** (1:1) → **HeaderVO**: Cabeçalho do arquivo  
**RemessaVO** (1:N) → **DetalheRemessaVO**: Detalhes de boletos  
**RemessaVO** (1:1) → **TraillerVO**: Rodapé do arquivo  

**DetalheRemessaVO** contém:
- (1:1) → **DetalhesRemessaDadosEmpresaVO**: Dados da empresa beneficiária
- (1:1) → **DetalhesRemessaDadosBancarios**: Dados bancários do título
- (1:1) → **DetalheRemessaInformFinanceirasVO**: Informações financeiras
- (1:1) → **DetalheRemessaSacadoVO**: Dados do sacado (pagador)
- (0:1) → **DetalheSacadorVO**: Dados do sacador/avalista (opcional)
- (1:N) → **DetalheBoletoVO**: Mensagens do boleto

**DetalheBoletoVO** contém:
- (1:1) → **BoletoFrenteVO**: Mensagens da frente do boleto
- (0:1) → **BoletoVersoVO**: Mensagens do verso (opcional)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TB_CONTA_CORRENTE | Tabela | SELECT | Consulta dados da conta corrente para obter cd_oco_conta |
| TB_CARNE_PARAMETRO_REMESSA | Tabela | SELECT | Busca código do veículo legal e instrumento de cobrança por conta |
| TBSISTEMAEMISSORBOLETO | Tabela | SELECT | Obtém código do sistema emissor de boleto (ITAUSIG) |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TBREGISTROINSTRUMENTOCOBRANCA | Tabela | INSERT | Insere dados principais do instrumento de cobrança/boleto |
| TBREGISTROINSTOCBRNARCLHO | Tabela | INSERT | Insere dados complementares de cobrança (descontos, mora) |
| TBSITUACAOPROCESSAMENTOINSTO | Tabela | INSERT | Registra situação de processamento do boleto (pendente registro) |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| Arquivos CNAB400 (*.txt) | Leitura | ItemReader / diretório configurável | Arquivos de remessa bancária Itaú SIG no formato CNAB400 |
| C[timestamp].txt | Gravação (comentado) | ItemWriter / outputPath | Arquivo de saída CNAB (funcionalidade desabilitada no código) |
| statistics-*.log | Gravação | Framework BV Batch | Logs de estatísticas de execução |

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
| Banco de Dados Sybase (DBCARNE/DBCOR) | JDBC | Persistência de dados de instrumentos de cobrança e boletos |
| Sistema Itaú SIG | Arquivo | Recebe arquivos CNAB400 de remessa bancária (integração via arquivo) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades (Reader/Processor/Writer)
- Uso adequado de Value Objects para representar estrutura CNAB
- Validações específicas e bem organizadas
- Tratamento de exceções customizadas por tipo de erro

**Pontos Negativos:**
- **Código comentado**: Funcionalidade de geração de arquivo CNAB está comentada (gerarCNABItauSig)
- **Gestão manual de transações**: Uso de autoCommit(false) e commits/rollbacks manuais é propenso a erros
- **Falta de injeção de dependências**: Muitas classes instanciadas com `new` ao invés de injeção
- **Hardcoded values**: Strings e números mágicos espalhados pelo código (ex: "ITAUSIG", "341", posições fixas)
- **Métodos longos**: Alguns métodos com muitas responsabilidades (ex: populaPrimeiraMetadeParametros)
- **Falta de testes**: Apenas um teste de integração vazio
- **Logging inconsistente**: Mistura de workflow.info e workflow.error
- **Clone defensivo desnecessário**: Uso excessivo de clone() em getters/setters de Date
- **Falta de documentação**: Javadoc incompleto em várias classes

---

## 14. Observações Relevantes

1. **Processamento Consolidado**: O sistema lê múltiplos arquivos CNAB mas consolida em um único header/trailler, o que pode causar inconsistências
2. **Funcionalidade Desabilitada**: A geração de arquivo CNAB de saída está comentada no ItemWriter
3. **Controle de Sequência**: Sistema manipula números sequenciais dos registros CNAB mas não valida continuidade
4. **Situação Fixa**: Todos os boletos são inseridos com situação "Pendente de Registro" independente do conteúdo do arquivo
5. **Dependência de Framework Legado**: Uso intenso do BV Framework (proprietário) dificulta manutenção e migração
6. **Ausência de Retry**: Não há mecanismo de retry em caso de falhas parciais
7. **Parâmetros de Execução**: Sistema espera parâmetro executionId mas não valida sua presença
8. **Encoding**: Não há tratamento explícito de encoding dos arquivos (pode causar problemas com caracteres especiais)