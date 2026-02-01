# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java desenvolvido com Spring Batch para preparação e agendamento de débitos automáticos em conta corrente. O sistema processa contratos de débito ativos, valida informações junto ao sistema legado (Gestão de Contratos), calcula datas de agendamento considerando prazos e feriados, e integra com o sistema GDCC para efetivação dos débitos. Realiza também tratamento de cancelamentos, renegociações e autorizações de débito, especialmente para contratos da Caixa Econômica Federal.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê contratos de débito ativos, consulta dados no sistema legado, busca parâmetros de conta convênio e lista de feriados |
| **ItemProcessor** | Aplica regras de negócio: valida contratos, calcula datas de agendamento/vencimento, gera autorizações CEF, identifica suspensões |
| **ItemWriter** | Persiste parcelas de débito, registros de débito, atualiza contratos, integra com agenda GDCC |
| **ContratoDebitoDao** | Acesso à tabela TbContratoDebito (DBGESTAO) |
| **ParcelaDebitoDao** | Acesso à tabela TbParcelaDebito (DBGESTAO) |
| **GestaoContratosDao** | Consulta dados de contratos e parcelas no sistema legado (múltiplos BDs) |
| **RegistroDebitoDao** | Acesso à tabela TbRegistroDebito (DbGestaoDebitoContaCorrente) |
| **AutorizacaoDebitoDAO** | Gerencia autorizações de débito (TbRegistroAutorizacaoDebito) |
| **IntegracaoAgendaBusinessImpl** | Implementa lógica de integração com sistema de agendamento GDCC |
| **MyResumeStrategy** | Estratégia de tratamento de erros e continuidade do batch |

## 3. Tecnologias Utilizadas

- **Framework Batch**: Spring Batch (via bv-framework-batch)
- **Build**: Maven (multi-módulo)
- **Banco de Dados**: Sybase ASE (jConnect 4 driver versão 7.07-SP136)
- **Web Services**: Apache Axis 1.4 (cliente SOAP)
- **Logging**: BVLogger (framework proprietário)
- **Utilitários**: Apache Commons Lang
- **Criptografia**: bv-crypto.core
- **Java Version**: Compatível com Java 6+ (baseado nas dependências)

## 4. Principais Endpoints REST

não se aplica

## 5. Principais Regras de Negócio

- **RN001**: Verificação e atualização do sequencial do contrato financeiro ativo
- **RN002**: Cálculo de data de agendamento baseado em prazo de débito parametrizado
- **RN003**: Suspensão automática de débito para contratos fechados, com cessão de particulares, fraude confirmada ou restrição judicial
- **RN004**: Cálculo de data de agendamento: DataAgendamento = DataVencimento - (DdPrazoDebito - 1)
- **RN005**: Antecipação de vencimento para dia útil anterior (apenas para CPBB com flag ativo)
- Validação de prazos mínimo e máximo entre agendamento e débito
- Geração automática de autorização de débito para CEF (banco 104) e layout 08
- Cancelamento automático de parcelas quitadas antecipadamente
- Cancelamento de parcelas de contratos renegociados (sequencial financeiro anterior)
- Validação de data de exercício para agendamentos
- Tratamento especial para débito de optante (parcela 0 com valor zero)
- Inativação de contrato após 60 dias em atraso (comentado no código)

## 6. Relação entre Entidades

**ContratoDebito** (1) -----> (N) **ParcelaDebito**
- Relacionamento: Um contrato possui múltiplas parcelas
- Chaves: NuContrato, SqContratoFinanceiro

**ParcelaDebito** (N) -----> (1) **RegistroDebito**
- Relacionamento: Cada parcela referencia um registro de débito
- Chave: CdRegistroDebito

**RegistroDebito** (N) -----> (1) **ContaConvenio**
- Relacionamento: Registros vinculados a uma conta convênio
- Chave: CdContaConvenioSistemaOrigem

**ContratoDebito** (N) -----> (1) **RegistroAutorizacaoDebito**
- Relacionamento: Contrato pode ter autorização de débito
- Chave: CdRegistroAutorizacaoDebito

**ContratoDebito** -----> **TbContrato** (Sistema Legado)
- Relacionamento: Sincronização de dados entre GDCF e Gestão de Contratos
- Chave: NuContrato

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| DBGESTAO..TbContratoDebito | tabela | SELECT | Contratos com débito ativo |
| DBGESTAO..TbParcelaDebito | tabela | SELECT | Situação de parcelas de débito |
| DBCOR..TbContratoPrincipal | tabela | SELECT | Identificação do BD de origem do contrato |
| DBCOR..TbFeriado | tabela | SELECT | Datas de feriados para cálculo de dias úteis |
| ${nomeBD}..TbContrato | tabela | SELECT | Dados do contrato no sistema legado |
| ${nomeBD}..TbContratoFinanceiro | tabela | SELECT | Dados financeiros do contrato |
| ${nomeBD}..TbParcela | tabela | SELECT | Parcelas a vencer no sistema legado |
| DBCRED..TbProposta | tabela | SELECT | Dados da proposta (subproduto, convênio) |
| DBCRED..TbConvenioCreditoPessoalVignca | tabela | SELECT | Flag de antecipação de pagamento |
| DbGestaoDebitoContaCorrente..TbContaConvenio | tabela | SELECT | Parâmetros da conta convênio |
| DbGestaoDebitoContaCorrente..TbParametroSistema | tabela | SELECT | Data de exercício do sistema |
| DbGestaoDebitoContaCorrente..TbRegistroAutorizacaoDebito | tabela | SELECT | Autorizações de débito existentes |
| DbGestaoDebitoContaCorrente..TbAutorizacaoDebitoPrpsaCntro | tabela | SELECT | Vínculo autorização-contrato-proposta |
| SCC_FIN..SAJ_PROCESSO | tabela | SELECT | Processos judiciais (restrição) |
| SCC_FIN..TB_SITUACAO_CONTRATO | tabela | SELECT | Situação de fraude do contrato |
| ${nomeBD}..TbEventoSuspCobranca | tabela | SELECT | Motivos de suspensão de cobrança |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| DBGESTAO..TbContratoDebito | tabela | UPDATE | Atualização de sequencial, suspensão, dados bancários e código de autorização |
| DBGESTAO..TbParcelaDebito | tabela | INSERT | Inclusão de novas parcelas de débito |
| DBGESTAO..TbParcelaDebito | tabela | UPDATE | Atualização de status e código de registro de débito/cancelamento |
| DbGestaoDebitoContaCorrente..TbRegistroDebito | tabela | INSERT | Inclusão de registros de débito/cancelamento |
| DbGestaoDebitoContaCorrente..TbRegistroDebito | tabela | UPDATE | Atualização de status do registro |
| DbGestaoDebitoContaCorrente..TbRegistroAutorizacaoDebito | tabela | INSERT | Inclusão de novas autorizações CEF |
| DbGestaoDebitoContaCorrente..TbAutorizacaoDebitoPrpsaCntro | tabela | INSERT | Vínculo de autorização com contrato/proposta |
| DbGestaoDebitoContaCorrente..TbAutorizacaoDebitoPrpsaCntro | tabela | UPDATE | Desativação de autorizações antigas |
| DbGestaoDebitoContaCorrente..TbEventoRegistroAutorizacaoDbo | tabela | INSERT | Log de eventos de autorização |
| DBGESTAO..TbAgendaDebito | tabela | UPDATE | Atualização de agenda via stored procedure |

## 9. Arquivos Lidos e Gravados

não se aplica

## 10. Filas Lidas

não se aplica

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Sistema Legado Gestão de Contratos | Database | Consulta de contratos, parcelas e parâmetros em múltiplos bancos de dados (DBGESTAOCDCCG, etc) |
| GDCC - Conta Convênio WebService | SOAP | Consulta de parâmetros de conta convênio (endpoint configurável) |
| GDCC - Agendamento WebService | SOAP | Integração de agendamentos e cancelamentos (endpoint configurável) |
| DBCOR | Database | Consulta de feriados e dados corporativos |
| SCC_FIN | Database | Consulta de restrições judiciais e fraudes |

## 13. Avaliação da Qualidade do Código

**Nota:** 6/10

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrão Spring Batch (Reader/Processor/Writer)
- Separação clara de responsabilidades entre DAOs
- Uso de enums para valores fixos (StatusParcelaDebitoEnum, TipoMovimentoDebitoEnum)
- Logging adequado em pontos críticos
- Tratamento de exceções customizadas (DadosInconsistentesException)

**Pontos Negativos:**
- Métodos extremamente longos (ItemProcessor.handleProcess com mais de 200 linhas, ItemWriter.gravarParcelasDebito)
- Código comentado em diversos locais sem remoção
- Complexidade ciclomática alta em vários métodos
- Falta de testes unitários (apenas estrutura de teste presente)
- Queries SQL hardcoded em classes de recursos ao invés de arquivos externos
- Uso de código legado (Apache Axis 1.4, padrões antigos de SOAP)
- Métodos com muitos parâmetros (validarParametrosAgendarRemessa com 4+ validações)
- Duplicação de lógica em alguns pontos (validações repetidas)
- Nomes de métodos pouco descritivos (validacao1, validacao2, hash1, hash2)
- Mistura de português e inglês nos nomes

## 14. Observações Relevantes

- O sistema foi desenvolvido para o Banco Votorantim (BV Financeira) e processa débitos em conta corrente
- Possui tratamento especial para Caixa Econômica Federal (banco 104) com geração automática de autorizações
- Implementa novo modelo de layout (versão 08) com lógica diferenciada
- Utiliza framework proprietário BV (bv-framework-batch) que encapsula Spring Batch
- Código gerado automaticamente por ferramentas WSDL2Java (Apache Axis) para classes de webservice
- Sistema multi-tenant: acessa múltiplos bancos de dados conforme produto do contrato
- Estratégia de resume permite continuidade do processamento mesmo com erros em registros individuais
- Códigos de retorno customizados para integração com UC4 (scheduler)
- Versão atual: 0.28.0
- Dependências desatualizadas representam risco de segurança e manutenibilidade

---

*Documentação gerada através de análise de código-fonte do projeto javabatch-gdcc-base-prepara-agenda*