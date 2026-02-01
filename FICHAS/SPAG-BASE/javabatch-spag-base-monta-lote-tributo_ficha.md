# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **javabatch-spag-base-monta-lote-tributo** é um batch Java desenvolvido com Spring Batch para processar pagamentos de tributos em lote. Sua principal função é consolidar movimentos de pagamento de tributos, criar lotes agrupados por fornecedor e banco, e enviar esses lotes para processamento via TED (Transferência Eletrônica Disponível) ou PIX, dependendo de configuração via feature toggle. O sistema busca movimentos pendentes do dia, agrupa-os em lotes, trata estornos de erros do dia anterior, e envia para processamento através de APIs REST ou filas MQ.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê os movimentos de pagamento de tributos pendentes do dia para um fornecedor específico |
| **ItemProcessor** | Processa cada registro de lote (atualmente apenas repassa o item sem transformação) |
| **ItemWriter** | Grava os registros no banco, acumula valores do lote e dispara o envio via TED ou PIX |
| **MontaLoteTributo** | Classe de negócio principal que orquestra busca de dados, tratamento de estornos e envio de pagamentos |
| **MontaLoteTributoDAO** | Acesso a dados para consultas e inserções nas tabelas de lote, movimento e conta |
| **RestRequestUtil** | Utilitário para chamadas REST (obtenção de token, envio de PIX, consulta de EndToEndId, feature toggle) |
| **RestTemplateBV** | Template customizado para requisições HTTP com retry e tratamento de erros |
| **FilaMqWriterImpl** | Implementação para envio de mensagens para filas IBM MQ |
| **AgendaPagamentoServiceImpl** | Converte objetos de pagamento para XML no formato esperado pela fila MQ |
| **TransferenciaRepresentationMapper** | Mapeia objetos CapaLoteVO para TransferenciaRepresentationVO (usado na API de transferências) |

---

## 3. Tecnologias Utilizadas

- **Spring Batch** (processamento em lote)
- **Spring Framework** (injeção de dependências, configuração XML)
- **Maven** (gerenciamento de dependências)
- **IBM MQ / JMS** (filas de mensagens)
- **Microsoft SQL Server** (banco DBSPAG)
- **Sybase** (banco DBITP)
- **Bitronix** (gerenciador de transações XA)
- **Apache HttpClient** (requisições HTTP)
- **Gson** (serialização/deserialização JSON)
- **JAXB** (serialização XML)
- **BV Framework** (framework proprietário do Banco Votorantim para batch, logging, criptografia)
- **Log4j** (logging)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Responsável | Descrição |
|--------|----------|-------------------|-----------|
| POST | `{url_orch_transferencias}/v2/transferencia` | RestRequestUtil | Envia transferência TED via orquestrador |
| POST | `{url_token}` | RestRequestUtil | Obtém token de autenticação OAuth2 |
| GET | `{url_orch_integracao}` | RestRequestUtil | Consulta feature toggle para habilitar PIX |
| POST | `{url_api_endtoend}` | RestRequestUtil | Obtém EndToEndId para pagamento PIX |
| POST | `{url_api_pix}` | RestRequestUtil | Envia pagamento PIX |

---

## 5. Principais Regras de Negócio

1. **Agrupamento de Movimentos**: Busca movimentos de pagamento de tributos do dia atual para um fornecedor e banco específicos, agrupando-os em um único lote
2. **Tratamento de Estornos**: Antes de enviar o lote, busca lançamentos com erro do dia útil anterior e os estorna, subtraindo seus valores do lote atual
3. **Escolha de Meio de Pagamento**: Utiliza feature toggle para decidir entre envio via PIX ou TED
4. **Validação de Conta**: Verifica se existe conta configurada para o fornecedor antes de processar
5. **Consolidação de Valores**: Para BVSA (banco 413), consolida o valor total do lote em uma única transferência TED
6. **Atualização de Status**: Atualiza status dos movimentos (0=pendente, 10=enviado ao lote, 99=erro, 100=erro no envio)
7. **Geração de Protocolo**: Registra número de protocolo da transação para rastreabilidade
8. **Retry de Requisições**: Implementa retry automático (até 5 tentativas) para chamadas REST

---

## 6. Relação entre Entidades

**CapaLoteVO** (Cabeçalho do Lote)
- Contém: código do lote, parâmetro de pagamento, valor total, status, dados da conta (banco, agência, conta, CPF/CNPJ, favorecido)
- Relaciona-se com: múltiplos **RegistroLoteVO**

**RegistroLoteVO** (Detalhe do Lote)
- Contém: código do movimento, código do lote, código do lançamento, protocolo, valor, status
- Pertence a: um **CapaLoteVO**

**MovimentoVO** (Agregador)
- Contém: uma **CapaLoteVO** e lista de **RegistroLoteVO**
- Usado para transportar dados entre camadas

**InclusaoLancamentoVO** (Lançamento TED)
- Contém: dados completos para inclusão de lançamento via procedure (remetente, favorecido, valores, datas)
- Construído a partir de: **CapaLoteVO** (remetente e favorecido)

**TransferenciaRepresentationVO** (Transferência via API)
- Contém: participantes (remetente/favorecido), datas, códigos de transação, valor
- Mapeado de: **CapaLoteVO**

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbMovimentoLotePagamentoTrbto | Tabela | SELECT | Busca movimentos de pagamento de tributos pendentes do dia para um fornecedor |
| TbContaFornecedorTributo | Tabela | SELECT | Busca dados da conta configurada para TED/PIX do fornecedor |
| TbLancamento | Tabela | SELECT | Busca lançamentos com erro do dia anterior para estorno |
| TbDetalheFornecedorLote | Tabela | SELECT | Busca detalhes de lotes anteriores (usado no estorno) |
| TbLancamentoPessoa | Tabela | SELECT | Busca dados de pessoa relacionados ao lançamento (usado no estorno) |
| TBL_CAIXA_ENTRADA_SPB (DBITP) | Tabela | SELECT | Verifica status do protocolo de pagamento no ITP |
| dbglobal..PrDiaUtilAnterior (DBITP) | Procedure | EXEC | Obtém o dia útil anterior para busca de erros |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbLotePagamentoTributo | Tabela | INSERT | Insere cabeçalho do lote de pagamento de tributos |
| TbLotePagamentoTributo | Tabela | UPDATE | Atualiza valor total, protocolo, status e EndToEndId do lote |
| TbDetalheFornecedorLote | Tabela | INSERT | Insere detalhes de cada movimento no lote |
| TbMovimentoLotePagamentoTrbto | Tabela | UPDATE | Atualiza status do movimento para "enviado ao lote" (status 10) |
| DBITP..BV_INCLUSAO_CAIXA_ENTRADA | Procedure | EXEC | Executa inclusão de lançamento TED no sistema ITP (para Banco Votorantim) |
| PrIncluirLancamento | Procedure | EXEC | Executa inclusão de lançamento TED no SPAG (para BVSA) |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| conf/auth.properties | Leitura | AuthProperties | Contém URLs de APIs, credenciais OAuth2 e configurações de integração |
| log/*.log | Gravação | BVLogger (framework) | Arquivos de log da execução do batch |
| statistics-*.log | Gravação/Exclusão | Scripts .bat/.sh | Arquivos de estatísticas removidos no início da execução |
| *.tlog | Gravação/Exclusão | Bitronix | Arquivos de log de transação XA, removidos ao final da execução |

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

---

## 11. Filas Geradas

| Nome da Fila | Tipo | Classe Responsável | Descrição |
|--------------|------|-------------------|-----------|
| QL.SPAG.SOLICITAR_PAGAMENTO_TED_REQ.INT | IBM MQ | FilaMqWriterImpl | Fila para envio de solicitações de pagamento TED (usado para BVSA) |

**Observação**: Embora o enum MqQueueEnum defina outras filas (BOLETO, DOC, CC, TRIBUTO), apenas a fila TED é efetivamente utilizada neste batch.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| API Gateway OAuth2 | REST | Autenticação via OAuth2 para obtenção de token JWT |
| Orquestrador de Transferências | REST | Envio de transferências TED via API v2 |
| Orquestrador de Integração Tributo PIX | REST | Consulta de feature toggle, obtenção de EndToEndId e envio de pagamentos PIX |
| IBM MQ (QM.ATA.01) | MQ | Envio de mensagens de pagamento TED para processamento assíncrono |
| Banco DBSPAG (SQL Server) | JDBC | Banco de dados principal do sistema SPAG |
| Banco DBITP (Sybase) | JDBC | Banco de dados do sistema ITP (Integração de Transferências e Pagamentos) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Estrutura bem organizada seguindo padrão Spring Batch (Reader/Processor/Writer)
- Separação clara de responsabilidades (DAO, Service, Util, Domain)
- Uso de enums para constantes e tipos
- Implementação de retry em chamadas REST
- Tratamento de transações XA com Bitronix
- Logging adequado em pontos críticos

**Pontos Negativos:**
- **Código comentado**: Diversas seções de código comentado (ex: getTokenBV, getFeatureToggle original) indicam falta de limpeza
- **Mistura de idiomas**: Comentários e mensagens em português, código em inglês, inconsistência
- **Acoplamento**: Forte dependência de frameworks proprietários (BV Framework) dificulta portabilidade
- **Tratamento de exceções genérico**: Muitos blocos catch vazios ou com tratamento superficial
- **Falta de testes**: Arquivos de teste marcados como NAO_ENVIAR, indicando cobertura insuficiente
- **Hardcoding**: Valores fixos em código (ex: ISPB "13935893", códigos de transação)
- **Complexidade**: Métodos longos com múltiplas responsabilidades (ex: enviarTed, montarPagamento)
- **SQL inline**: Queries SQL como strings concatenadas ao invés de usar recursos do framework
- **Falta de documentação**: Javadoc incompleto ou ausente na maioria das classes
- **Configuração XML**: Uso de XML Spring legado ao invés de anotações modernas

---

## 14. Observações Relevantes

1. **Feature Toggle Duplo**: O sistema possui dois feature toggles - um para escolher entre TED via API ou Procedure, e outro para escolher entre TED ou PIX. Atualmente o primeiro está desabilitado (hardcoded como false).

2. **Múltiplos Bancos**: O sistema suporta processamento para Banco Votorantim (655) e BVSA (413), com lógicas diferentes de envio de TED.

3. **Estorno Automático**: Implementa lógica sofisticada de estorno automático de lançamentos com erro do dia anterior, subtraindo valores do lote atual.

4. **Execução Parametrizada**: O batch recebe como parâmetros o código do fornecedor e o código do banco remetente, permitindo execuções paralelas para diferentes fornecedores.

5. **Ambiente**: Configurações apontam para ambiente UAT (User Acceptance Testing), com URLs de homologação.

6. **Segurança**: Utiliza criptografia BV_CRYPTO_TOKEN para descriptografar credenciais OAuth2.

7. **Transações Distribuídas**: Usa Bitronix para gerenciar transações XA entre múltiplos bancos de dados (SQL Server e Sybase).

8. **Formato de Mensagem**: Mensagens MQ são formatadas em XML com namespace específico do padrão SPAG.

9. **Limitações**: O ItemProcessor atualmente não realiza nenhuma transformação, apenas repassa o item (possível ponto de extensão futura).

10. **Dependências Legadas**: Uso de bibliotecas antigas (Sybase jConnect 3.0, frameworks proprietários BV) pode dificultar manutenção e evolução.