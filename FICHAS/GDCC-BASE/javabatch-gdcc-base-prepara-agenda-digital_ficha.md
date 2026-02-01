# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java responsável por preparar a agenda de débitos automáticos em conta corrente. O sistema processa contratos de débito ativos, valida informações junto ao sistema legado (Gestão de Contratos), calcula datas de agendamento e vencimento, e gera registros de débito para posterior envio aos bancos conveniados. Utiliza arquitetura Reader-Processor-Writer do framework BV para processamento em lote.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê contratos de débito ativos, consulta dados no sistema legado, busca parâmetros de conta convênio e prepara DTOs para processamento |
| **ItemProcessor** | Aplica regras de negócio, valida contratos, calcula datas de agendamento/vencimento, gera parcelas de débito e cancelamentos |
| **ItemWriter** | Persiste parcelas de débito, atualiza contratos, integra com agenda GDCC e executa cancelamentos |
| **MyResumeStrategy** | Estratégia de recuperação de erros, define códigos de retorno e permite continuidade do processamento |
| **IntegracaoAgendaBusinessImpl** | Implementa integração com sistema de agendamento, valida parâmetros e cria registros de débito |
| **GestaoContratosDao** | Acessa dados de contratos e parcelas no sistema legado (múltiplos bancos de dados) |
| **ContratoDebitoDao** | Gerencia operações CRUD na tabela TbContratoDebito |
| **ParcelaDebitoDao** | Gerencia operações CRUD na tabela TbParcelaDebito |
| **RegistroDebitoDao** | Gerencia registros de débito para envio aos bancos |

## 3. Tecnologias Utilizadas

- **Java** com Maven para gerenciamento de dependências
- **Spring Framework** para injeção de dependências e configuração
- **BV Framework Batch** (framework proprietário para processamento batch)
- **Sybase ASE** (jConnect 4) como banco de dados principal
- **Apache Axis 1.4** para integração com Web Services
- **Log4j** para logging
- **JUnit** para testes
- **JDBC** para acesso a dados

## 4. Principais Endpoints REST

não se aplica

## 5. Principais Regras de Negócio

- **RN001**: Atualização de sequencial financeiro do contrato quando divergente do sistema legado
- **RN002**: Cálculo de data de agendamento baseado em prazo de débito parametrizado (DtVencimento - DdPrazoDebito)
- **RN003**: Suspensão automática de débito para contratos fechados, com cessão de particulares, fraude confirmada ou restrição judicial
- **RN004**: Validação de prazos mínimo e máximo entre agendamento e débito conforme parametrização
- **RN005**: Antecipação de vencimento para dia útil anterior quando permitido (apenas CPBB)
- **UC002 - Passo 6**: Sincronização de sequencial financeiro entre GDCF e sistema legado
- Geração de cancelamentos para parcelas quitadas antecipadamente ou de contratos renegociados
- Validação de conta convênio por veiculo legal, banco, agrupamento e versão de layout
- Controle de tentativas de débito conforme parametrização (QtTentativaDebito)
- Suspensão por inatividade (60 dias sem movimentação)
- Tratamento especial para débito optante (tipo movimento 5)

## 6. Relação entre Entidades

**ContratoDebito** (1) → (N) **ParcelaDebito**
- Relacionamento: Um contrato possui múltiplas parcelas
- Chave: NuContrato, SqContratoFinanceiro

**ParcelaDebito** (N) → (1) **RegistroDebito**
- Relacionamento: Cada parcela referencia um registro de débito
- Chave: CdRegistroDebito

**ContratoDebito** (N) → (1) **ContaConvenio**
- Relacionamento: Contratos vinculados a contas convênio por banco/agência
- Chave: NuBanco, CdAgencia

**ContratoDebito** (1) → (1) **Contrato (Legado)**
- Relacionamento: Sincronização com sistema de origem
- Chave: NuContrato

**ParcelaDebito** (1) → (1) **Parcela (Legado)**
- Relacionamento: Correspondência com parcelas do sistema de origem
- Chave: NuContrato, SqContratoFinanceiro, NuParcela

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| DBGESTAO..TbContratoDebito | tabela | SELECT | Contratos com débito ativo para processamento |
| DBGESTAO..TbParcelaDebito | tabela | SELECT | Situação de parcelas já cadastradas |
| DbGestaoDebitoContaCorrente..TbContaConvenio | tabela | SELECT | Parâmetros de contas convênio |
| DbGestaoDebitoContaCorrente..TbContaConvenioSistemaOrigem | tabela | SELECT | Vinculação conta convênio com sistema origem |
| DbGestaoDebitoContaCorrente..TbParametroSistema | tabela | SELECT | Data de exercício e processamento |
| DbGestaoDebitoContaCorrente..TbRegistroDebito | tabela | SELECT | Registros de débito existentes |
| DBCOR..TbContratoPrincipal | tabela | SELECT | Identificação do banco de dados de origem |
| DBCOR..TbFeriado | tabela | SELECT | Datas de feriados para cálculo de dias úteis |
| DBCOR..TbProduto | tabela | SELECT | Informações de produto do contrato |
| DBCRED..TbProposta | tabela | SELECT | Dados da proposta vinculada ao contrato |
| ${nomeBD}..TbContrato | tabela | SELECT | Dados do contrato no sistema legado |
| ${nomeBD}..TbContratoFinanceiro | tabela | SELECT | Dados financeiros do contrato |
| ${nomeBD}..TbParcela | tabela | SELECT | Parcelas a vencer no sistema legado |
| ${nomeBD}..TbEventoSuspCobranca | tabela | SELECT | Motivos de suspensão de cobrança |
| SCC_FIN..SAJ_PROCESSO | tabela | SELECT | Restrições judiciais do contrato |
| SCC_FIN..TB_SITUACAO_CONTRATO | tabela | SELECT | Situação de fraude do contrato |
| DbGestaoDebitoContaCorrente..TbAutorizacaoDebitoPrpsaCntro | tabela | SELECT | Autorizações de débito por proposta/contrato |
| DbGestaoDebitoContaCorrente..TbEventoRegistroAutorizacaoDbo | tabela | SELECT | Eventos de autorização de débito |
| DbGestaoDebitoContaCorrente..TbParametroAutorizacaoDebito | tabela | SELECT | Parâmetros de autorização por banco |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| DBGESTAO..TbContratoDebito | tabela | UPDATE | Atualização de sequencial financeiro, suspensão e código de autorização |
| DBGESTAO..TbParcelaDebito | tabela | INSERT | Inclusão de novas parcelas de débito |
| DBGESTAO..TbParcelaDebito | tabela | UPDATE | Atualização de status e registro de cancelamento |
| DbGestaoDebitoContaCorrente..TbRegistroDebito | tabela | INSERT | Inclusão de registros de débito e cancelamento |
| DbGestaoDebitoContaCorrente..TbRegistroDebito | tabela | UPDATE | Atualização de status de registro de débito |
| DbGestaoDebitoContaCorrente..TbRegistroAutorizacaoDebito | tabela | INSERT | Inclusão de autorizações de débito (CEF) |
| DbGestaoDebitoContaCorrente..TbAutorizacaoDebitoPrpsaCntro | tabela | INSERT | Vinculação autorização com proposta/contrato |
| DbGestaoDebitoContaCorrente..TbAutorizacaoDebitoPrpsaCntro | tabela | UPDATE | Desativação de autorizações antigas |
| DbGestaoDebitoContaCorrente..TbEventoRegistroAutorizacaoDbo | tabela | INSERT | Log de eventos de autorização |

## 9. Arquivos Lidos e Gravados

não se aplica

## 10. Filas Lidas

não se aplica

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

| Sistema/Serviço | Descrição |
|-----------------|-----------|
| **Sistema Legado (Gestão de Contratos)** | Consulta dados de contratos, parcelas e parâmetros em múltiplos bancos de dados Sybase (DBGESTAOCP, DBGESTAOCDCCG, etc) |
| **GDCC (Gestão de Débito Conta Corrente Corporativa)** | Integração para agendamento e cancelamento de débitos via IntegracaoAgendaBusinessImpl |
| **SCC_FIN** | Consulta restrições judiciais e fraudes confirmadas |
| **DBCOR** | Consulta dados corporativos (feriados, produtos, contratos principais) |

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem definida com separação clara de responsabilidades (Reader-Processor-Writer)
- Uso de enums para representar estados e tipos
- Logging estruturado e detalhado
- Tratamento de exceções específicas (DadosInconsistentesException)
- Uso de DTOs para transferência de dados entre camadas

**Pontos Negativos:**
- Métodos muito extensos com múltiplas responsabilidades (ex: ItemReader.handleNext, ItemProcessor.handleProcess)
- Alto acoplamento com framework proprietário BV
- Código gerado por ferramentas (Axis) misturado com código de negócio
- Falta de testes unitários (apenas teste de integração)
- Queries SQL hardcoded em constantes de recursos
- Métodos com muitos parâmetros (ex: validarParametrosAgendarRemessa)
- Comentários em português misturados com código
- Uso excessivo de flags e códigos mágicos
- Complexidade ciclomática elevada em alguns métodos
- Falta de documentação JavaDoc em métodos críticos

## 14. Observações Relevantes

- Sistema legado utiliza múltiplos bancos de dados Sybase, identificados dinamicamente por contrato
- Processamento específico para produtos CPBB (código 55) com regras diferenciadas de antecipação
- Suporte a novo modelo de layout de arquivo (versão '08') para bancos 104 e 655
- Tratamento especial para débito optante (parcela 0) em determinados cenários
- Sistema preparado para executar em ambiente UC4 com códigos de retorno específicos
- Utiliza procedure customizada (prObterSequencialDisponivelOut) para geração de sequenciais
- Integração com sistema de autorização de débito CEF com múltiplos modelos
- Controle de execução via data de exercício parametrizada
- Suporte a renegociação de contratos com cancelamento automático de parcelas antigas
- Filtros dinâmicos por produto/subproduto via enum FiltroQueryContratoDebiAutoEnum