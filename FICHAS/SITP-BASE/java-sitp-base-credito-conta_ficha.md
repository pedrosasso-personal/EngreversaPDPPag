# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **java-sitp-base-credito-conta** é um componente de integração responsável por registrar lançamentos de pagamentos no sistema ITP (Sistema de Transferências e Pagamentos). Ele recebe solicitações de crédito em conta via REST API, valida se o lançamento já existe, insere novos registros na tabela de caixa de entrada do SPB (Sistema de Pagamentos Brasileiro) e atualiza o status no sistema SPAG. O sistema atua como uma ponte entre sistemas de pagamento, garantindo idempotência nas operações e rastreabilidade através de protocolos únicos.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **CreditoContaController** | Controlador REST que expõe o endpoint de lançamento de pagamentos |
| **CreditoContaBean** | EJB de negócio que orquestra a inclusão de lançamentos e atualização no SPAG |
| **CreditoContaServiceImpl** | Implementação do serviço de negócio com conversão de dados e validações |
| **CreditoContaDAOImpl** | DAO para operações na tabela TBL_CAIXA_ENTRADA_SPB (banco ITP) |
| **DbSpagDAOImpl** | DAO para atualização de lançamentos na tabela TbLancamento (banco SPAG) |
| **CaixaEntradaSPBDTO** | DTO com mais de 100 atributos representando um lançamento no SPB |
| **DicionarioPagamento** | Objeto de domínio externo contendo dados do pagamento |
| **ServiceException** | Exceção customizada para erros de serviço |
| **RestExceptionMapper** | Mapeador de exceções para respostas REST padronizadas |

---

## 3. Tecnologias Utilizadas

- **Java EE 6/7** (EJB 3.1, JAX-RS, CDI, JMS)
- **IBM WebSphere Application Server** (servidor de aplicação)
- **Maven** (gerenciamento de dependências e build)
- **Spring JDBC** (acesso a dados via JDBC Template)
- **Oracle Database** (banco de dados principal)
- **SQL Server** (banco SPAG)
- **Log4j 2 / SLF4J** (logging)
- **Apache Commons Lang3** (utilitários)
- **Swagger** (documentação de APIs REST)
- **JAX-WS** (web services SOAP - módulo preparado mas sem implementação)
- **Arquitetura Votorantim** (fjee-base-commons, arqt-base-lib)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/atacado/pagamentos/lancarPagamento/` | CreditoContaController | Recebe solicitação de lançamento de pagamento, valida duplicidade, insere no ITP e atualiza SPAG |

---

## 5. Principais Regras de Negócio

1. **Idempotência**: Antes de inserir um lançamento, o sistema verifica se já existe um registro com os mesmos critérios (Cod_Liquidacao, Dt_Movimento, CNPJ_CPF_Remetente, CdLancamentoOrigem). Se existir, retorna o protocolo existente sem duplicar.

2. **Geração de Protocolo ITP**: Ao inserir um novo lançamento, o sistema gera automaticamente um código de protocolo único (Cod_Protocolo) que identifica a transação no ITP.

3. **Conversão de Dados**: O sistema converte objetos `DicionarioPagamento` (formato SPAG) para `CaixaEntradaSPBDTO` (formato ITP), mapeando campos e aplicando transformações (ex: substring em datas, formatação de timestamps).

4. **Status Padrão**: Novos lançamentos são inseridos com `Cod_Status = 9` (status inicial).

5. **Atualização Bidirecional**: Após inserir no ITP, o sistema atualiza o lançamento original no banco SPAG com o número do protocolo gerado, mantendo sincronização entre os sistemas.

6. **Tratamento de Erros**: Em caso de falha, o sistema registra ocorrências no objeto de retorno com código de erro genérico e flag `FlRetornoSolicitacaoCreditoConta = 1`.

7. **Auditoria**: O sistema registra logs detalhados de todas as operações (inserção, duplicidade, erros).

---

## 6. Relação entre Entidades

**CaixaEntradaSPBDTO** (Entidade Principal):
- Representa um lançamento de pagamento no SPB
- Contém dados de remetente, favorecido, valores, datas, códigos de transação
- Relaciona-se com múltiplas tabelas de domínio (não explicitadas no código)
- Campos principais: Cod_Protocolo (PK), Cod_Liquidacao, Dt_Movimento, CNPJ_CPF_Remetente, Valor

**DicionarioPagamento** (Entidade Externa):
- Objeto de integração do sistema SPAG
- Contém CodLancamento (identificador no SPAG)
- Convertido para CaixaEntradaSPBDTO antes da persistência
- Atualizado com CodProtocolo após inserção no ITP

**Relacionamento**: DicionarioPagamento (1) -> (1) CaixaEntradaSPBDTO através do campo CdLancamentoOrigem

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TBL_CAIXA_ENTRADA_SPB | Tabela | SELECT | Consulta para verificar se lançamento já existe (checaLancamento) |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TBL_CAIXA_ENTRADA_SPB | Tabela | INSERT | Inserção de novos lançamentos de pagamento no sistema ITP (incluirLancamento) |
| TbLancamento | Tabela | UPDATE | Atualização do protocolo ITP no lançamento original do sistema SPAG (atualizarLancamentoSpag) |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| CreditoContaDAOImpl-sql.xml | Leitura | CreditoContaDAOImpl | Arquivo XML contendo queries SQL parametrizadas (checaLancamento, incluirLancamento) |
| DbSpagDAOImpl-sql.xml | Leitura | DbSpagDAOImpl | Arquivo XML contendo query SQL para atualização no SPAG (atualizarLancamentoSpag) |
| errorMessages.properties | Leitura | Sistema | Arquivo de mensagens de erro internacionalizadas |
| roles.properties | Leitura | Sistema | Arquivo de configuração de roles de segurança |

---

## 10. Filas Lidas

Não se aplica. O módulo JMS está preparado (estrutura de diretórios e configurações existem), mas não há implementação de MDBs ou consumidores de fila no código fornecido.

---

## 11. Filas Geradas

Não se aplica. Não há código de publicação em filas JMS, Kafka ou RabbitMQ no componente analisado.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **Sistema SPAG** | Banco de Dados (SQL Server) | Sistema de origem dos lançamentos. O componente lê dados do DicionarioPagamento e atualiza a tabela TbLancamento com o protocolo ITP gerado |
| **Sistema ITP** | Banco de Dados (Oracle) | Sistema de destino onde são registrados os lançamentos na tabela TBL_CAIXA_ENTRADA_SPB |
| **Biblioteca java-spag-base-pagamentos-commons** | Dependência Maven | Biblioteca compartilhada contendo classes de domínio (DicionarioPagamento, ListaOcorrencia, enums) |
| **Arquitetura Votorantim (fjee-base, arqt-base)** | Framework Corporativo | Frameworks de infraestrutura para persistência (CrudDaoJdbc), trilha de auditoria, handlers SOAP/REST |

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Separação clara de responsabilidades em camadas (controller, service, DAO)
- Uso de padrões Java EE (EJB, CDI, JAX-RS)
- Externalização de queries SQL em arquivos XML
- Tratamento de exceções com logging
- Uso de NamedParameterJdbcTemplate para queries parametrizadas
- Estrutura modular Maven bem organizada

**Pontos Negativos:**
- **DTO com mais de 100 atributos** (CaixaEntradaSPBDTO) - violação do princípio de coesão, dificulta manutenção
- **Método com 100+ linhas** (defineSqlParamSourceCaixaEntradaSPB) - baixa legibilidade
- **Falta de validações de entrada** - não há validação dos dados recebidos no controller
- **Tratamento genérico de exceções** - captura Exception ao invés de exceções específicas
- **Código comentado** em vários arquivos (pom.xml, configurações)
- **Falta de testes unitários** para classes críticas (apenas estrutura de teste vazia)
- **Acoplamento com biblioteca externa** (DicionarioPagamento) sem interface de abstração
- **Logging inconsistente** - mistura de logger.info e logger.error sem padrão claro
- **Falta de documentação JavaDoc** nas classes principais
- **RowMapper vazio** (CreditoContaRowMapper) - método mapRow retorna null

---

## 14. Observações Relevantes

1. **DataSources JNDI**: O sistema utiliza dois datasources distintos:
   - `jdbc/sitpBaseDbItpDS` (Oracle - sistema ITP)
   - `jdbc/spagBaseDBSPAGDS` (SQL Server - sistema SPAG)

2. **Segurança**: Configurado com autenticação BASIC e role `intr-middleware` para todos os EJBs e endpoints REST.

3. **Transações**: Todos os componentes de negócio utilizam `@TransactionAttribute(TransactionAttributeType.NOT_SUPPORTED)`, delegando controle transacional para camadas inferiores.

4. **Arquitetura Multi-módulo**: O projeto segue estrutura modular Maven com 9 módulos (commons, domain, persistence, integration, business, jms, ws, rs, ear).

5. **Preparado para SOAP**: Existe módulo WS completo com handlers e configurações, mas sem implementação de serviços.

6. **Trilha de Auditoria**: Integração com framework corporativo de auditoria através de handlers (CapturadorTrilhaInbound, FormatadorTrilhaOutbound).

7. **Versionamento**: Sistema em versão 0.5.0, indicando fase de desenvolvimento/homologação.

8. **Classloader**: Configurado com `PARENT_LAST` no deployment.xml, priorizando bibliotecas da aplicação sobre as do servidor.

9. **Swagger**: Configuração presente para documentação de APIs, mas comentada no pom.xml do módulo RS.

10. **Dependências Corporativas**: Forte dependência de bibliotecas internas Votorantim (arqt-base-lib 1.0.19, fjee-base-lib 1.1.10), dificultando portabilidade.