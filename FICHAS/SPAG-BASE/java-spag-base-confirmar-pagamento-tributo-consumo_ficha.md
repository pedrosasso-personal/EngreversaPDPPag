# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **java-spag-base-confirmar-pagamento-tributo-consumo** é um componente responsável pela confirmação de pagamentos de tributos realizados através da plataforma SPAG (Sistema de Pagamentos). O sistema atua como intermediário entre o sistema SPAG e a IS2B (Celcoin), realizando a confirmação de pagamentos previamente efetuados, atualizando os status dos lançamentos no banco de dados e tratando possíveis erros durante o processo. Utiliza arquitetura multi-módulo Maven com EJB, JAX-RS (REST) e integração com APIs externas via HTTP.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ConfirmarPagamentoTributoBean** | EJB Stateless que orquestra o processo de confirmação de pagamento, validando status do lançamento, chamando APIs externas e atualizando banco de dados |
| **ConfirmarIntegrationServices** | Responsável pela integração HTTP com a API CAAPI/IS2B para confirmar pagamentos de tributos |
| **ConsultarIntegrationServices** | Realiza consultas à API Apigee/IS2B para verificar o status de transações de pagamento |
| **SpagDAOImpl** | Implementação DAO para acesso ao banco de dados SPAG, realizando consultas e atualizações de lançamentos |
| **HttpCaapiIntegration / HttpApigeeIntegration** | Classes base para integração HTTP com CAAPI e Apigee, gerenciando autenticação OAuth e requisições |
| **CriarTokenIntegration / CriarTokenOauthIntegration** | Gerenciam a criação e renovação de tokens OAuth para autenticação nas APIs externas |
| **AclFeatureToggleIntegrationServiceImpl** | Implementa controle de feature toggles via ACL para habilitar/desabilitar funcionalidades dinamicamente |
| **ConfirmarPagamentoTributo** (REST) | Endpoint REST que expõe o serviço de confirmação de pagamento via JAX-RS |
| **ErrosIS2BEnum** | Enumeração que mapeia códigos de erro da IS2B para ocorrências de negócio do SPAG |

---

## 3. Tecnologias Utilizadas

- **Java EE / Jakarta EE** (EJB 3.1, CDI, JAX-RS, JAX-WS)
- **IBM WebSphere Application Server** (servidor de aplicação)
- **Maven** (gerenciamento de dependências e build multi-módulo)
- **Spring JDBC** (acesso a dados via JDBC Template)
- **Apache HttpClient** (requisições HTTP para APIs externas)
- **Gson** (serialização/deserialização JSON)
- **SLF4J / Log4j2** (logging)
- **JUnit, PowerMock, Mockito** (testes unitários)
- **Swagger** (documentação de APIs REST)
- **OAuth 2.0** (autenticação em APIs externas)
- **SQL Server** (banco de dados SPAG - DBSPAG)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/atacado/pagamentos/confirmarPagamento` | ConfirmarPagamentoTributo | Recebe requisição de confirmação de pagamento de tributo e retorna o resultado do processamento |

---

## 5. Principais Regras de Negócio

1. **Validação de Lançamento Pendente**: Verifica se o lançamento está com status pendente (status 3) antes de confirmar o pagamento
2. **Confirmação com IS2B**: Envia requisição de confirmação para a API IS2B/Celcoin com protocolo do pagamento
3. **Consulta de Status**: Em caso de erro na confirmação, realiza até 3 tentativas de consulta para validar o status real da transação
4. **Tratamento de Erros IS2B**: Mapeia códigos de erro da IS2B (183, 258, 619, 621, etc.) para ocorrências de negócio específicas
5. **Atualização de Status**: Atualiza status do lançamento (confirmado=03, erro=99) e status do fornecedor (pago=01, recusado=99)
6. **Feature Toggle**: Utiliza feature toggle para alternar entre fluxos antigos e novos de confirmação (CAAPI v1 vs v2)
7. **Controle de Banco**: Ajusta código do banco (655 ou 413) conforme banco remetente (413 ou 436)
8. **Validação de Transações Desfeitas**: Identifica transações com status 1 (desfeito) ou 6 (pendente desfazimento) e gera ocorrências de erro
9. **Atualização de Lote**: Atualiza status do lote de pagamento conforme status dos detalhes (acatado, parcial ou encerrado)

---

## 6. Relação entre Entidades

**Principais entidades e relacionamentos:**

- **TbLancamento**: Entidade principal que representa um lançamento de pagamento
  - Campos: CdLancamento (PK), StLancamento, CdAutenticacaoBancaria, DtAlteracao
  
- **TbDetalheFornecedorLote**: Detalhe de fornecedor associado ao lançamento
  - Relacionamento: N:1 com TbLancamento (via CdLancamento)
  - Relacionamento: N:1 com TbLotePagamentoTributo (via CdLotePagamentoTributo)
  - Campos: CdStatusDetalheFonecedorLote, DtAlteracao

- **TbLotePagamentoTributo**: Lote de pagamentos de tributos
  - Relacionamento: 1:N com TbDetalheFornecedorLote
  - Campos: CdLotePagamentoTributo (PK), CdStatusLotePagamentoTributo, DtAlteracao

- **TbParametroPagamentoTributo**: Parâmetros de configuração
  - Campos: DsUrlConfirmaPagamento

**Objetos de domínio:**
- **DicionarioPagamento**: DTO principal que trafega entre camadas
- **ConfirmarRequest/Response**: DTOs de integração com IS2B
- **ConsultaResponse**: DTO de resposta de consulta de status

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbLancamento | Tabela | SELECT | Consulta lançamentos pendentes (status 3) e obtém protocolo IS2B (CdAutenticacaoBancaria) |
| TbParametroPagamentoTributo | Tabela | SELECT | Busca URL de confirmação de pagamento configurada (DsUrlConfirmaPagamento) |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbLancamento | Tabela | UPDATE | Atualiza status do lançamento (StLancamento) e código de autenticação bancária (CdAutenticacaoBancaria) |
| TbDetalheFornecedorLote | Tabela | UPDATE | Atualiza status do detalhe fornecedor lote (CdStatusDetalheFonecedorLote) |
| TbLotePagamentoTributo | Tabela | UPDATE | Atualiza status do lote de pagamento (CdStatusLotePagamentoTributo) baseado nos status dos detalhes |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| config-arqt-base.properties | Leitura | ConfigArqtrBaseProperties | Configurações de endpoints de APIs (API Gateway, OAuth, ambiente) |
| config_toggle.properties | Leitura | AclFeatureToggleProperties | URLs do serviço ACL Feature Toggle por ambiente (DES/UAT/PRD) |
| errorMessages.properties | Leitura | commons | Mensagens de erro do sistema |
| roles.properties | Leitura | commons | Definição de roles de segurança |
| SpagDAOImpl-sql.xml | Leitura | SpagDAOImpl | Queries SQL para operações no banco SPAG |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| **IS2B/Celcoin (via CAAPI)** | API REST | Confirmação de pagamentos de tributos - endpoints `/v1/atacado/is2b/pagamentos/confirmar` e `/v2/atacado/is2b/pagamentos/confirmar` |
| **IS2B/Celcoin (via Apigee)** | API REST | Consulta de status de transações - endpoint `/v1/atacado/pagamentos/transactions/{banco}/status-consult` |
| **API Gateway OAuth** | API REST | Geração de tokens JWT para autenticação - endpoint `/auth/oauth/v2/token-jwt` |
| **ACL Feature Toggle** | API REST | Consulta de feature toggles - endpoint `/v1/feature-toggle/{feature}` |
| **SPAG Base Consultar Pagamento Tributo** | EJB Remoto | Consulta de pagamentos de tributos (referenciado mas não utilizado diretamente no código analisado) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades em camadas (business, integration, persistence, domain)
- Uso adequado de injeção de dependências (CDI/EJB)
- Tratamento de exceções estruturado com retry e fallback
- Logging adequado em pontos críticos
- Uso de enums para mapear erros de negócio
- Testes unitários presentes (embora não analisados em detalhe)

**Pontos Negativos:**
- **Variável estática mutável**: `sucesso` é static e mutável, causando problemas de concorrência em ambiente multi-thread
- **Código duplicado**: Lógica de retry e tratamento de erro repetida em vários métodos
- **Métodos muito longos**: `confirmarPagamento()` e `confirmaPagamentoIS2B()` têm muitas responsabilidades
- **Magic numbers**: Constantes como 3, 99, 655, 413 espalhadas pelo código
- **Mistura de responsabilidades**: Classe de negócio fazendo parsing de URL e controle de fluxo baseado em strings
- **Falta de validação**: Inputs não são validados antes do processamento
- **Comentários desnecessários**: Código comentado deveria ser removido
- **Nomenclatura inconsistente**: Mistura de português e inglês
- **Acoplamento**: Dependência direta de classes de integração em vez de interfaces

---

## 14. Observações Relevantes

1. **Segurança**: O sistema utiliza autenticação BASIC e roles (`spag-integracao`, `intr-middleware`) para controle de acesso aos EJBs e endpoints REST

2. **Transações**: Os EJBs utilizam `TransactionAttributeType.NOT_SUPPORTED`, delegando controle transacional para camadas inferiores

3. **Feature Toggle**: O sistema implementa feature toggle para alternar entre fluxos antigos (v1) e novos (v2) de confirmação, permitindo rollback sem deploy

4. **Retry Logic**: Implementa até 3 tentativas de consulta em caso de falha na confirmação, com lógica de validação de status

5. **Mascaramento de Dados**: Utiliza `CpfUtils` para mascarar CPF/CNPJ em logs, atendendo LGPD

6. **Ambientes**: Suporta múltiplos ambientes (DES, QAS, UAT, PRD) com configurações específicas

7. **Dependências Externas**: Utiliza bibliotecas do framework interno `fjee-base` e `arqt-base` do Banco Votorantim

8. **Banco de Dados**: Utiliza SQL Server (DBSPAG) com queries parametrizadas via Spring JDBC Template

9. **Documentação API**: Utiliza Swagger para documentação dos endpoints REST

10. **Deployment**: Empacotado como EAR com múltiplos módulos (EJB, WAR REST, JARs de domínio/integração/persistência)