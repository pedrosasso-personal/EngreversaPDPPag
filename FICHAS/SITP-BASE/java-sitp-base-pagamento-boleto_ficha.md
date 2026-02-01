---
## Ficha Técnica do Sistema

### 1. Descrição Geral
Sistema de solicitação e processamento de pagamentos de boletos bancários (cobrança e consumo) desenvolvido em Java EE. O sistema recebe requisições via Web Service SOAP, valida as informações, processa pagamentos através de stored procedures no banco de dados (ITP e SPAG), e envia notificações via filas JMS. Suporta operações para clientes tradicionais e fintechs, com validação de grades horárias, representantes bancários e reprocessamento de transações.

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `SolicitarPagamentoBoletoBackendServiceImpl` | Implementação do Web Service SOAP que recebe solicitações de pagamento de boletos |
| `GestaoPagamentoBeanImpl` | EJB que gerencia a lógica de negócio para inclusão de lançamentos assíncronos e envio para filas de callback |
| `GestaoSPAGBeanImpl` | EJB que valida representantes bancários no sistema SPAG |
| `GestaoPagamentoDaoImpl` | DAO para acesso ao banco ITP, execução de stored procedures e consultas |
| `GestaoPagamentoDaoSpagImpl` | DAO para acesso ao banco SPAG e processamento de transações |
| `GestaoSPAGDaoImpl` | DAO para validação de correspondentes bancários no SPAG |
| `ValidateRequest` | Validador de requisições para clientes tradicionais |
| `ValidateFintechRequest` | Validador de requisições para clientes fintech com regras específicas |
| `TransferenciaAssincronaStoredProcedure` | Encapsula chamadas para stored procedures de transferência no ITP |
| `TransferenciaAssincronaStoredProcedureSpag` | Encapsula chamadas para stored procedures de transferência no SPAG |
| `EnvioFilaCallbackJmsProducer` | Produtor JMS para envio de mensagens de callback para o ITP |
| `EnvioFilaCallbackSpagJmsProducer` | Produtor JMS para envio de mensagens de callback para o SPAG |

### 3. Tecnologias Utilizadas
- **Java EE 7** (EJB 3.1, JAX-WS, JMS, CDI)
- **Maven** (gerenciamento de dependências e build)
- **Spring JDBC** (acesso a dados e execução de stored procedures)
- **IBM WebSphere Application Server** (servidor de aplicação)
- **SOAP Web Services** (JAX-WS)
- **JMS** (Java Message Service para filas)
- **Oracle Database** (banco de dados principal)
- **SQL Server** (banco SPAG)
- **Log4j 2 / SLF4J** (logging)
- **JAXB** (marshalling/unmarshalling XML)
- **Gson** (serialização JSON para logs)

### 4. Principais Endpoints REST
não se aplica (o sistema utiliza Web Services SOAP, não REST)

**Endpoints SOAP:**

| Operação | Endpoint | Classe | Descrição |
|----------|----------|--------|-----------|
| `solicitarPagamentoBoletoCobranca` | `/sitp-base-pagamento-boleto-ws/SolicitarPagamentoBoletoBackendService` | `SolicitarPagamentoBoletoBackendServiceImpl` | Solicita pagamento de boleto (versão 1) |
| `solicitarPagamentoBoletoCobrancaV2` | `/sitp-base-pagamento-boleto-ws/SolicitarPagamentoBoletoBackendService` | `SolicitarPagamentoBoletoBackendServiceImpl` | Solicita pagamento de boleto com suporte a reprocessamento (versão 2) |

### 5. Principais Regras de Negócio

- **Validação de Grade Horária**: Verifica se a solicitação está dentro do horário permitido para a câmara de liquidação
- **Validação de Representante Bancário**: Para canal de pagamento 5, valida se o CNPJ está autorizado como correspondente bancário
- **Validação de Fintech**: Valida status da fintech (ativo/bloqueado/inativo) e status da conta (aberta/pré-cadastrada/encerrada/bloqueada)
- **Validação de Favorecido**: Para valores >= R$ 250.000,00 ou contas de pagamento, exige informações completas do favorecido
- **Validação de CPF/CNPJ**: Valida dígitos verificadores de CPF e CNPJ, rejeita sequências repetidas
- **Validação de Linha Digitável**: Para boletos de cobrança (liquidação 22), exige linha digitável com 47 dígitos
- **Reprocessamento**: Na V2, verifica tentativas anteriores e tempo de vida da transação para decidir entre retornar status ou reprocessar
- **Callback Assíncrono**: Após inclusão bem-sucedida, envia protocolo para fila de callback para processamento posterior
- **Distinção ITP/SPAG**: Roteia transações para banco ITP (código 413) ou SPAG baseado no código do banco remetente
- **Validação de Portador**: Para pagamentos com portador, valida nome e CPF/CNPJ obrigatórios
- **Validação de Meio de Pagamento**: Valida código do meio de pagamento (espécie, débito, crédito, cheque)

### 6. Relação entre Entidades

**Entidades Principais:**
- `Transferencia`: Entidade central contendo todos os dados da transação de pagamento (remetente, favorecido, valores, datas, códigos)
- `FintechOb`: Dados específicos de transações fintech (cliente fintech remetente e favorecido)
- `TransferenciaRetorno`: Resultado do processamento da stored procedure (código de retorno, protocolo, erros)
- `ProtocoloSolicitacaoPagamento`: Verificação de existência de protocolo anterior
- `ValidaReprocessamentoDTO`: Informações sobre tentativas anteriores de processamento
- `RepresentanteBancario`: Dados de correspondentes bancários autorizados
- `ParametrosCamaraLiquidacaoDTO`: Configurações de grade horária por tipo de liquidação

**Relacionamentos:**
- `Transferencia` 1:1 `FintechOb` (opcional, apenas para transações fintech)
- `Transferencia` 1:1 `TransferenciaRetorno` (resultado do processamento)
- `Transferencia` N:1 `ParametrosCamaraLiquidacaoDTO` (via código de liquidação)

### 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| `TbParametroCamaraLiquidacao` | tabela | SELECT | Consulta grades horárias de liquidação por câmara |
| `Tbl_Caixa_Entrada_SPB` | tabela | SELECT | Verifica existência de protocolo anterior (ITP) |
| `TbLancamento` | tabela | SELECT | Verifica existência de protocolo anterior (SPAG) |
| `TbCorrespondenteBancario` | tabela | SELECT | Valida correspondente bancário no SPAG |
| `TbContaCorrespondenteBancario` | tabela | SELECT | Valida conta do correspondente bancário |
| `TbMovimentoChamada` | tabela | SELECT | Consulta tentativas de reprocessamento |
| `tbl_status_unico_spb` | tabela | SELECT | Consulta descrição de status de processamento |

### 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| `Tbl_Caixa_Entrada_SPB` | tabela | INSERT | Inclusão de lançamento via stored procedure `BV_INCLUSAO_CAIXA_ENTRADA` ou `PrIncluirCaixaEntProtCliCtrl` |
| `TbLancamento` | tabela | INSERT | Inclusão de lançamento SPAG via stored procedure `PrIncluirLancamento` |
| `TbMovimentoChamada` | tabela | UPDATE | Zera flag ativo para forçar reprocessamento |

### 9. Arquivos Lidos e Gravados
não se aplica

### 10. Filas Lidas
não se aplica (o sistema não consome mensagens de filas, apenas produz)

### 11. Filas Geradas

| Nome da Fila | JNDI | Classe Responsável | Descrição |
|--------------|------|-------------------|-----------|
| `SITPValidarPagamentoQueue` | `queue/SITPValidarPagamentoQueue` | `EnvioFilaCallbackJmsProducer` | Fila de callback para validação de pagamentos ITP |
| `spagBaseValidacaoPagamentoQueue` | `jms/spagBaseValidacaoPagamentoQueue` | `EnvioFilaCallbackSpagJmsProducer` | Fila de callback para validação de pagamentos SPAG |

### 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **ITP (Sistema de Pagamentos)** | Banco de Dados Oracle | Banco principal para processamento de pagamentos via stored procedures |
| **SPAG (Sistema de Pagamentos Alternativos)** | Banco de Dados SQL Server | Banco secundário para pagamentos do banco 413 (BVSA) |
| **Filas JMS** | Mensageria | Envio de protocolos para processamento assíncrono de callbacks |
| **Sistemas Clientes** | Web Service SOAP | Recebe solicitações de pagamento de sistemas externos via SOAP |

### 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de camadas (WS, Business, Persistence, Domain)
- Uso adequado de EJBs e transações
- Validações de negócio bem estruturadas em classes específicas
- Uso de enums para códigos de retorno
- Logging presente em pontos críticos

**Pontos Negativos:**
- **Código comentado**: Diversos trechos de código comentado não removidos
- **Duplicação**: Lógica similar entre ITP e SPAG poderia ser melhor abstraída
- **Métodos longos**: Alguns métodos com muitas responsabilidades (ex: `validate()`, `solicitarPagamentoBoletoCobrancaV2`)
- **Magic numbers**: Constantes hardcoded (ex: 250000, 413, códigos de status)
- **Tratamento de exceções**: Uso genérico de `Exception` em várias assinaturas
- **Falta de documentação**: JavaDoc ausente ou incompleto na maioria das classes
- **Complexidade ciclomática**: Métodos de validação com muitos ifs aninhados
- **Testes**: Arquivos de teste presentes mas marcados como NAO_ENVIAR, não foi possível avaliar cobertura

### 14. Observações Relevantes

- O sistema possui duas versões da operação principal: V1 (síncrona) e V2 (com suporte a reprocessamento)
- Existe distinção clara entre processamento para banco ITP e SPAG (código 413)
- O sistema implementa mecanismo de retry com limite de 3 tentativas e timeout de 5 minutos
- Suporte específico para operações fintech com validações adicionais de conta e status
- Utiliza stored procedures para garantir atomicidade das operações no banco
- Implementa trilha de auditoria via SOAP headers
- Configuração de ambientes via WSDLs específicos (DES, QA, UAT, PRD)
- Uso de handlers JAX-WS para interceptação de mensagens SOAP
- Sistema preparado para deployment em IBM WebSphere Application Server
- Dependências gerenciadas via shared libraries do WAS (arqt-base-lib, fjee-base-lib)