# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de liberação e gestão de pagamentos desenvolvido em Java EE, responsável por processar operações de pagamento, reapresentação de pagamentos devolvidos/rejeitados, validação de pagamentos de crédito estudantil e cálculo de valor presente. O sistema atua como backend de serviços SOAP para integração com outros sistemas corporativos da Votorantim.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **DadosPagamentoBeanImpl** | Gerencia inclusão, consulta e remoção de dados de pagamento na tabela TbLiberacaoRecursoOperacao |
| **LiberarPagamentoBeanImpl** | Calcula valor presente de operações financeiras considerando taxa de juros, IOF, parcelas e carência |
| **ReapresentacaoPagamentoBeanImpl** | Processa reapresentação de pagamentos devolvidos/rejeitados, atualizando dados bancários e histórico |
| **ValidacaoPagamentoBeanImpl** | Valida pagamentos complementares de crédito estudantil, verificando limites e regras de parceria |
| **LiberacaoPagamentoEndpoint** | Endpoint SOAP que expõe os serviços de liberação, reapresentação e validação de pagamentos |
| **ConsultaPagamentoDao** | Acesso a dados de pagamentos para consulta e histórico |
| **ReapresentacaoPagamentoDao** | Persistência de operações de reapresentação de pagamentos |
| **HistoricoReapresentacaoPagamentoDao** | Gerencia histórico de reapresentações e status |
| **TabelaInfoDao** | Gera IDs sequenciais para novas entidades via stored procedure |

## 3. Tecnologias Utilizadas

- **Java EE 6/7** (EJB 3.1, JAX-WS, CDI)
- **IBM WebSphere Application Server** (runtime e descritores específicos)
- **Spring JDBC** (para acesso a dados)
- **Maven** (gerenciamento de dependências e build)
- **Microsoft SQL Server** (banco de dados - DataSource: jdbc/aproBaseDBCORDS)
- **Apache Commons BeanUtils** (manipulação de objetos)
- **SLF4J** (logging)
- **SOAP Web Services** (JAX-WS com handlers customizados)
- **JUnit, PowerMock, EasyMock** (testes unitários)

## 4. Principais Endpoints REST

Não se aplica. O sistema utiliza Web Services SOAP, não REST.

## 5. Principais Regras de Negócio

1. **Cálculo de Valor Presente**: Calcula o valor presente de operações financeiras considerando taxa de juros mensal, quantidade de parcelas, carência, IOF, taxa de cadastro e outros valores. Valida se a diferença entre valor total e valor presente calculado não excede R$ 1,00 (para mais ou para menos).

2. **Reapresentação de Pagamentos**: Permite reapresentar pagamentos com situações específicas (devolvido, rejeitado, cancelado ITP, etc.), atualizando informações bancárias do favorecido e mantendo histórico completo das alterações.

3. **Validação de Pagamento Crédito Estudantil**: Valida pagamentos complementares verificando:
   - Limite de R$ 50.000 (ou R$ 70.000 com exceção)
   - Máximo de 2 pagamentos para instituição de ensino
   - Máximo de 1 pagamento para parceiro comercial
   - Valor total dos pagamentos deve corresponder ao valor total da operação (diferença máxima de R$ 1,00)

4. **Gestão de Dados de Pagamento**: Armazena e gerencia dados complementares de operações de crédito estudantil (número de contrato e valor total da operação).

5. **Histórico de Reapresentação**: Mantém histórico completo de todas as reapresentações, incluindo dados bancários anteriores, situações e datas.

6. **Correção de Carência**: Implementa correção no cálculo de dias corridos considerando horário de verão para evitar erros de um dia na carência.

## 6. Relação entre Entidades

**Entidades Principais:**

- **TbPagamento**: Entidade central de pagamentos
  - Relaciona-se com **TbPessoaPagamento** (sacador, favorecido, proponente)
  - Relaciona-se com **TbInformacaoBancariaPagamento** (dados bancários cedente/favorecido)
  - Relaciona-se com **TbSituacaoPagamento** (situação atual)
  - Relaciona-se com **TbFormaPagto** (forma de pagamento)
  - Relaciona-se com **TbPagamentoContrato** (vínculo com contrato)

- **TbHistoricoReapresentacao**: Histórico de reapresentações
  - Relaciona-se com **TbPagamento** (pagamento reapresentado)
  - Relaciona-se com **TbHistoricoStatus** (histórico de situações)

- **TbLiberacaoRecursoOperacao**: Dados complementares de operações
  - Armazena número de contrato e valor total da operação

- **TbEstornoOrdemPagamento**: Estornos de ordens de pagamento
  - Relaciona-se com **TbPagamento**

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| DBPAGAMENTO..TbPagamento | Tabela | SELECT | Consulta dados completos de pagamentos |
| DBPAGAMENTO..TbPessoaPagamento | Tabela | SELECT | Consulta dados de pessoas envolvidas no pagamento (sacador, favorecido, proponente) |
| DBPAGAMENTO..TbInformacaoBancariaPagamento | Tabela | SELECT | Consulta informações bancárias de cedente e favorecido |
| DBPAGAMENTO..TbPagamentoContrato | Tabela | SELECT | Consulta vínculo entre pagamento e contrato |
| DBPAGAMENTO..TbEstornoOrdemPagamento | Tabela | SELECT | Consulta estornos de ordens de pagamento |
| DBGESTAOCPC..TbContratoLiberacao | Tabela | SELECT | Consulta liberações de contratos CPC |
| DBGESTAOLSG..TbContratoLiberacao | Tabela | SELECT | Consulta liberações de contratos LSG |
| DBGESTAOCDCCG..TbContratoLiberacao | Tabela | SELECT | Consulta liberações de contratos CDCCG |
| DBPAGAMENTO..TbLiberacaoRecursoOperacao | Tabela | SELECT | Consulta dados complementares de operações |
| DBPAGAMENTO..TbHistoricoReapresentacao | Tabela | SELECT | Consulta histórico de reapresentações (para obter próximo ID) |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| DBPAGAMENTO..TbPagamento | Tabela | UPDATE | Atualiza situação, operação e dados do pagamento para reapresentação |
| DBPAGAMENTO..TbInformacaoBancariaPagamento | Tabela | UPDATE | Atualiza dados bancários do favorecido na reapresentação |
| DBPAGAMENTO..TbHistoricoReapresentacao | Tabela | INSERT | Insere histórico de reapresentações realizadas |
| DBPAGAMENTO..TbHistoricoStatus | Tabela | INSERT | Insere histórico de mudanças de status do pagamento |
| DBPAGAMENTO..TbLiberacaoRecursoOperacao | Tabela | INSERT/DELETE | Insere/remove dados complementares de operações de crédito estudantil |

## 9. Arquivos Lidos e Gravados

Não se aplica. O sistema não realiza leitura ou gravação de arquivos em disco.

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas.

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **Sistemas Clientes via SOAP** | Web Service Provider | Expõe serviços SOAP para liberação, reapresentação e validação de pagamentos |
| **Microsoft SQL Server** | Banco de Dados | Acesso aos bancos DBPAGAMENTO, DBGESTAOCPC, DBGESTAOLSG, DBGESTAOCDCCG via JDBC |
| **IBM WebSphere** | Application Server | Runtime e infraestrutura de segurança (WS-Security) |
| **Stored Procedure SP_GERA_SEQUENCIAL** | Database | Geração de IDs sequenciais para novas entidades |

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades em camadas (business, persistence, domain, ws)
- Uso adequado de EJBs e injeção de dependências
- Tratamento de exceções estruturado com faults SOAP padronizados
- Logging implementado com SLF4J
- Uso de mappers para conversão de ResultSet
- Documentação JavaDoc presente em várias classes

**Pontos Negativos:**
- Código de cálculo de valor presente extremamente complexo e difícil de manter (LiberarPagamentoBeanImpl)
- Lógica de negócio misturada com código de apresentação no endpoint SOAP
- Uso excessivo de arrays de Object[] para passar parâmetros SQL (baixa legibilidade)
- Queries SQL hardcoded em arquivos XML (dificulta manutenção)
- Falta de validação de entrada em vários métodos
- Código duplicado no tratamento de exceções nos endpoints
- Uso de BeanUtils.copyProperties pode ocultar erros de mapeamento
- Comentários em português e inglês misturados
- Falta de testes unitários para classes críticas (apenas estrutura de teste presente)
- Acoplamento forte com estruturas específicas do WebSphere/IBM

## 14. Observações Relevantes

1. **Segurança**: Sistema utiliza WS-Security com diferentes níveis (Low, Medium, High) configurados via PolicySets do WebSphere. Role "intr-middleware" requerida para acesso aos EJBs.

2. **Cálculo de Valor Presente**: Implementa correção específica para problema de cálculo de carência relacionado ao horário de verão brasileiro. Mantém dois cálculos (correto e incorreto) para fins de debug.

3. **Reapresentação**: Apenas pagamentos com situações específicas podem ser reapresentados (códigos: 7, 13, 16, 17, 40, 41, 42, 43, 56). Sistema valida CPF/CNPJ do favorecido.

4. **Crédito Estudantil**: Regras específicas para validação de pagamentos complementares, com limite diferenciado para casos com exceção (R$ 70.000 vs R$ 50.000).

5. **Histórico**: Sistema mantém histórico completo de reapresentações, incluindo snapshot dos dados bancários anteriores.

6. **Transações**: Operações de reapresentação são transacionais (REQUIRED), garantindo consistência entre atualização de pagamento, informação bancária e histórico.

7. **DataSource**: Utiliza DataSource JNDI "jdbc/aproBaseDBCORDS" para acesso ao banco SQL Server.

8. **Classloader**: Configurado com PARENT_LAST para isolamento de bibliotecas no WebSphere.