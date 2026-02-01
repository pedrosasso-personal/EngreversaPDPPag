---
## Ficha Técnica do Sistema

### 1. Descrição Geral
Sistema de validação de transações financeiras para processamento de pagamentos diversos (boletos, TEDs, DOCs, tributos, transferências). O sistema atua como orquestrador de validações, aplicando regras de negócio específicas para cada tipo de transação, verificando saldos, limites, grades horárias, parâmetros de câmaras de liquidação e integrações com sistemas bancários (SPB, CIP, STR). Utiliza arquitetura EJB com DAOs especializados para diferentes bases de dados (SPAG, PGFT, ITP, Global) e executa stored procedures para validações complexas.

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ValidacaoLogicaBean** | Orquestrador principal: atualiza status do lançamento, executa validações CNAB/genéricas/específicas conforme tipo de liquidação, trata exceções |
| **ValidarTransacaoBusiness / ValidarTransacaoBusinessImpl** | Interface e implementação para validação de transações: saldo insuficiente, pagamento eventual, grade horária, conversão CIP/STR |
| **ValidarPagamentoBoleto** | Validações específicas de boletos: NSU, linha digitável, código de barras, fator de vencimento, DV |
| **ValidarPagamentoTed** | Validações de TED/DOC: bancos remetente/favorecido, conta espelho, conversão CIP↔STR, validação ISPB |
| **ValidarPagamentoTef** | Validações de TEF/LDL: grade horária, contas favorecido, validação entre IFs, bancos BV (655/413) |
| **ValidarPagamentoTributo** | Validações de tributos: linha digitável 48 dígitos, DAC mod10/mod11, segmento válido |
| **ValidarPagamentoCnab** | Define código de liquidação conforme forma de pagamento CNAB |
| **ValidarPagamentoGenerico** | Validações comuns a todos os tipos: preenchimento de campos, validação de datas, valores, contas |
| **GlobalDAOImpl** | DAO para base Global: consultas de contas, bancos, datas úteis, relacionamentos |
| **PgftDAOImpl** | DAO para base PGFT: parâmetros de câmaras, robô cliente/empresa, ISPB, limites automáticos |
| **SpagDAOImpl** | DAO para base SPAG: atualização de status, consulta duplicados, flags CC, conta espelho |
| **FilialSpbDaoImpl** | DAO para base ITP: consultas de filial SPB, transações, liquidações |
| **ProcedureExecutorImpl** | Executor genérico de stored procedures via Spring JDBC |
| **PagamentoValidaResolverImpl** | Resolver para montagem de DTOs de entrada/saída de validação de pagamentos |
| **TransferenciaValidaResolverImpl** | Resolver para montagem de DTOs de validação de transferências |
| **ValidaSolicitacaoApi** | API REST para validação de pagamentos (endpoint POST /atacado/pagamentos/validarPagamento/) |
| **SegmentoStrategy** | Strategy para tratamento de segmentos CNAB (A/B/Z/J/J52/C) |

### 3. Tecnologias Utilizadas

- **Java EE**: EJB 3.x (@Stateless, @EJB)
- **JAX-RS**: API REST (endpoints)
- **Spring JDBC**: Acesso a banco de dados e execução de stored procedures
- **Swagger**: Documentação de APIs
- **RowMapper (Spring)**: Mapeamento de ResultSet para DTOs
- **Enums Java**: Modelagem de domínios (tipos de conta, bancos, status, etc)
- **Exception Handling**: Tratamento customizado de exceções (PagamentoValidationException)
- **Design Patterns**: Strategy (SegmentoStrategy), DAO, DTO, Resolver

### 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/atacado/pagamentos/validarPagamento/ | ValidaSolicitacaoApi | Valida solicitação de pagamento recebendo DicionarioPagamento e retornando resultado da validação com ocorrências |

### 5. Principais Regras de Negócio

1. **Validação de Saldo**: Verifica saldo disponível conforme parâmetros do robô (obrigatorioSaldoDisponivel), aceita pagamento sem saldo conforme configuração
2. **Grade Horária**: Valida horários permitidos para cada câmara de liquidação (CIP, STR, CNAB)
3. **Conversão Automática CIP↔STR**: Converte transações entre câmaras conforme valor e parâmetros (VrMaximoConversaoCamara, ConversaoAutomaticaCamara)
4. **Validação de Pagamento a Terceiros**: Verifica se pagamento a terceiro é permitido conforme parâmetro (aceitaPagamentoTerceiro)
5. **Validação de Boletos**: Valida linha digitável, código de barras, fator de vencimento, DV (mod10/mod11)
6. **Validação de Tributos**: Valida linha digitável de 48 dígitos, DAC, segmento válido, produto=8
7. **Validação de TED/DOC**: Verifica ISPB ativo, finalidade válida, recebimento de fundos, devolução
8. **Validação de TEF**: Verifica transferências entre mesma conta, entre IFs, validação específica bancos BV (655/413)
9. **Limite Automático**: Aplica limites de processamento DOC e devolução TED
10. **Validação de Duplicados**: Verifica pagamentos duplicados por CdLancamentoOrigem
11. **Validação de Conta Espelho**: Verifica conta espelho para banco digital
12. **Validação de Datas**: Verifica data de movimento (não pode ser futura), data útil
13. **Validação CNAB**: Define código de liquidação conforme forma de pagamento (CREDITO_EM_CONTA→CC, LIQUIDACAO_TITULO→BOLETO, DOC_TED→STR/DOC)
14. **Tratamento de Ocorrências**: Insere ocorrências de erro/validação no lançamento
15. **Status de Processamento**: Atualiza status do lançamento para "1-EmProcessamento" antes das validações

### 6. Relação entre Entidades

**Principais Entidades e Relacionamentos:**

- **TbLancamento**: Entidade central de lançamentos financeiros
  - Relaciona-se com **TbLancamentoPessoa** (pessoas envolvidas no lançamento)
  - Possui **TbParametroRoboCliente** e **TbParametroRoboEmpresa** (parâmetros de validação)
  - Vincula-se a **TbContaRelacionamento** e **TbContaDestino** (contas origem/destino)

- **TbConta**: Conta bancária
  - Relaciona-se com **TbAgencia** (agência da conta)
  - Relaciona-se com **TbBanco** (banco da conta)
  - Possui **VTipoConta** (tipo: corrente, poupança, investimento, etc)
  - Possui **VTitularidade** (titularidade da conta)
  - Relaciona-se com **TbPessoa** via **VPessoaRelacionamento** (titulares, cotitulares, procuradores)

- **TbParametroCamaraLiquidacao**: Parâmetros de câmaras (CIP, STR, CNAB)
  - Define grades horárias, valores máximos, conversões automáticas

- **DBISPB**: Base de ISPBs (bancos) ativos
  - Relaciona-se com **TbBanco** para validação de bancos ativos

- **TBL_FILIAL_SPB**: Filial SPB (Sistema de Pagamentos Brasileiro)
  - Relaciona-se com **TBL_TRANSACAO_SPB** (transações SPB)
  - Relaciona-se com **TBL_LIQUIDACAO_SPB** (liquidações)

### 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbLancamento | tabela | SELECT | Consulta lançamentos financeiros para validação |
| TbParametroRoboCliente | tabela | SELECT | Consulta parâmetros de validação por cliente |
| TbParametroRoboEmpresa | tabela | SELECT | Consulta parâmetros de validação por empresa |
| TbParametrosLimiteAutomatico | tabela | SELECT | Consulta limites automáticos (DOC, TED) |
| TbParametroCamaraLiquidacao | tabela | SELECT | Consulta parâmetros de câmaras (CIP, STR, CNAB) |
| DBISPB | tabela | SELECT | Consulta ISPBs (bancos) ativos |
| TbContaRelacionamento | tabela | SELECT | Consulta contas de relacionamento (origem) |
| TbContaDestino | tabela | SELECT | Consulta contas de destino (favorecido) |
| TbBanco | tabela | SELECT | Consulta dados de bancos |
| TbPessoa | tabela | SELECT | Consulta dados de pessoas (titulares, favorecidos) |
| TBCONTA | tabela | SELECT | Consulta dados de contas |
| VwContaCorrenteSaldoDia | view | SELECT | Consulta saldo do dia de contas correntes |
| TbEmpresaBv | tabela | SELECT | Consulta dados de empresas BV |
| TbContaEspelho | tabela | SELECT | Consulta contas espelho para banco digital |
| TbUsuarioContaFintech | tabela | SELECT | Consulta flags de conta fintech |
| TbContaUsuarioFintech | tabela | SELECT | Consulta usuários fintech |
| TbParametroPagamentoFintech | tabela | SELECT | Consulta parâmetros de pagamento fintech |
| TBL_FILIAL_SPB | tabela | SELECT | Consulta filial SPB |
| TBL_CAIXA_ENTRADA_SPB | tabela | SELECT | Consulta caixa de entrada SPB |
| TBL_TRANSACAO_SPB | tabela | SELECT | Consulta transações SPB |
| TBL_LIQUIDACAO_SPB | tabela | SELECT | Consulta liquidações SPB |

### 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbLancamento | tabela | UPDATE | Atualiza status do lançamento (EmProcessamento), dados de validação |
| TbLancamentoPessoa | tabela | UPDATE | Atualiza dados de pessoas relacionadas ao lançamento |

### 9. Arquivos Lidos e Gravados

não se aplica

### 10. Filas Lidas

não se aplica

### 11. Filas Geradas

não se aplica

### 12. Integrações Externas

1. **Sistema SPB (Sistema de Pagamentos Brasileiro)**: Integração via base ITP (TBL_FILIAL_SPB, TBL_TRANSACAO_SPB, TBL_LIQUIDACAO_SPB) para validação de transações SPB
2. **Câmara CIP**: Validação de transações CIP (TEDs), conversão CIP↔STR, validação de ISPBs ativos
3. **Câmara STR**: Validação de transações STR, conversão automática conforme valor
4. **CNAB**: Processamento de arquivos CNAB com segmentos A/B/Z/J/J52/C
5. **Base ISPB**: Consulta de bancos ativos via stored procedure BV_CONSULTA_ISPB_ATIVO
6. **Stored Procedures**: Execução de procedures de validação (prValidarPagamentoBoleto, prValidarTransferenciaTed, prValidarPagamentoTributos, sp_ge_verifica_ciclo_025, prValidaRecebDevolucao, PrConsultarBancoAtivo)

### 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com uso de DAOs especializados por base de dados
- Uso adequado de Design Patterns (Strategy, DAO, DTO, Resolver)
- Enums bem estruturados para domínios de negócio
- Uso de RowMappers para mapeamento objeto-relacional
- Tratamento de exceções customizado (PagamentoValidationException)
- Documentação Swagger para APIs REST
- Modularização por tipo de validação (Boleto, TED, TEF, Tributo)

**Pontos de Melhoria:**
- Falta de documentação inline (JavaDoc) em muitas classes
- Acoplamento com stored procedures dificulta testes unitários e manutenção
- Uso excessivo de "DicionarioPagamento" como estrutura genérica (Map) reduz type-safety
- Falta de logs estruturados para rastreabilidade
- Alguns métodos muito extensos (ex: validações complexas em uma única classe)
- Falta de testes unitários evidentes no código fornecido
- Nomenclatura inconsistente em alguns pontos (mix de português/inglês)
- Dependência forte de múltiplas bases de dados (SPAG, PGFT, ITP, Global) aumenta complexidade

### 14. Observações Relevantes

1. **Arquitetura Multi-Base**: O sistema acessa 4 bases de dados distintas (SPAG, PGFT, ITP, Global), cada uma com seu DAO especializado, o que indica uma arquitetura legada complexa.

2. **Stored Procedures**: Grande dependência de stored procedures para validações críticas (prValidarPagamentoBoleto, prValidarTransferenciaTed, prValidarPagamentoTributos), o que pode dificultar migração de banco de dados e testes.

3. **Conversão Automática de Câmaras**: O sistema possui lógica sofisticada de conversão automática entre câmaras CIP e STR baseada em valores e horários, o que é crítico para o negócio.

4. **Validações Específicas por Banco**: Há validações específicas para bancos BV (códigos 655 e 413), indicando regras de negócio particulares.

5. **Grade Horária**: Sistema valida grades horárias específicas para cada câmara de liquidação, o que é essencial para operações bancárias em tempo real.

6. **Segmentos CNAB**: Suporte a múltiplos segmentos CNAB (A/B/Z/J/J52/C) com transformações específicas por segmento.

7. **Validações de Boleto e Tributo**: Implementa validações complexas de linha digitável, código de barras, DAC (mod10/mod11), fator de vencimento.

8. **Parâmetros Configuráveis**: Sistema altamente parametrizável via tabelas de parâmetros (robô cliente/empresa, câmaras, limites), permitindo flexibilidade sem alteração de código.

9. **Status de Processamento**: Controle de status do lançamento (EmProcessamento) para evitar processamento duplicado.

10. **Tratamento de Ocorrências**: Sistema de ocorrências estruturado para registrar erros e validações, facilitando auditoria e troubleshooting.

---