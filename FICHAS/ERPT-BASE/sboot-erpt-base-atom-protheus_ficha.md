# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-erpt-base-atom-protheus** é um microserviço atômico desenvolvido em Java com Spring Boot, que atua como integrador entre o ERP Protheus e outros sistemas corporativos (como o Projuris). O sistema é responsável por:

- Consultar e atualizar informações de Centros de Custo no banco de dados do Protheus
- Consultar e processar informações de retorno de pagamentos
- Expor APIs REST para consumo por outros sistemas
- Realizar operações de leitura e escrita em tabelas do SQL Server do ERP Protheus

O componente segue a arquitetura de microserviços do Banco Votorantim, utilizando o framework Atlante e padrões corporativos estabelecidos.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application.java` | Classe principal de inicialização da aplicação Spring Boot |
| `ProtheusApiDelegateImpl` | Implementa os endpoints REST definidos no contrato OpenAPI |
| `ProtheusService` | Contém a lógica de negócio para operações de consulta e atualização |
| `ProtheusRepository` | Interface JDBI para operações de banco de dados usando SQL nomeado |
| `ProtheusRepositoryJDBC` | Implementação JDBC para consultas complexas (retorno de pagamento) |
| `ProtheusConfiguration` | Configuração de beans e dependências do sistema |
| `BusinessActionConfiguration` | Configuração para trilha de auditoria |
| `GlobalExceptionHandler` | Tratamento centralizado de exceções da API |
| `ProtheusMapper` | Mapeamento entre objetos de domínio e representação (MapStruct) |
| `ListarRetornoPagamentoMapper` | Mapper customizado para resultados de consulta de pagamentos |
| `DefinidorBusinessActionCustom` | Define ações de negócio para auditoria baseado no método HTTP |

---

## 3. Tecnologias Utilizadas

- **Framework Principal**: Spring Boot 2.x
- **Linguagem**: Java 11
- **Gerenciamento de Dependências**: Maven
- **Banco de Dados**: Microsoft SQL Server
- **Acesso a Dados**: 
  - JDBI 3.9.1 (SQL Object, StringTemplate4)
  - Spring JDBC
  - HikariCP (connection pool)
- **Mapeamento de Objetos**: MapStruct
- **Documentação de API**: OpenAPI 3.0 / Swagger UI / SpringDoc
- **Segurança**: Spring Security com OAuth2 Resource Server (JWT)
- **Logging**: Logback com formato JSON
- **Containerização**: Docker
- **Infraestrutura**: Google Cloud Platform (GCP)
- **Observabilidade**: Spring Actuator, Micrometer, Prometheus
- **Utilitários**: Lombok, Apache Commons

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/centros-custo` | `ProtheusApiDelegateImpl` | Retorna lista de centros de custo não exportados do Protheus |
| PUT | `/v1/centros-custo/{id}` | `ProtheusApiDelegateImpl` | Atualiza a data de exportação de um centro de custo específico |
| GET | `/v1/retorno-pagamento` | `ProtheusApiDelegateImpl` | Retorna lista de pagamentos dos últimos 7 dias |
| PUT | `/v1/retorno-pagamento/{id}` | `ProtheusApiDelegateImpl` | Atualiza a data de retorno de um pagamento específico |

**Observação**: Todos os endpoints requerem autenticação JWT (Bearer Token).

---

## 5. Principais Regras de Negócio

1. **Consulta de Centros de Custo**:
   - Retorna apenas centros de custo que não foram exportados (CTT_MSEXP vazio ou nulo)
   - Filtra apenas registros não bloqueados (CTT_BLOQ = '2')
   - Exclui registros deletados logicamente (D_E_L_E_T_ = '')

2. **Atualização de Centros de Custo**:
   - Valida se o ID (RECNO) existe antes de atualizar
   - Valida formato de data (yyyyMMdd) antes de persistir
   - Atualiza o campo CTT_MSEXP com a data fornecida

3. **Consulta de Retorno de Pagamento**:
   - Busca pagamentos dos últimos 7 dias (data atual - 7 dias até data atual)
   - Filtra por sistema específico (E2_XIDSIST = '0000000012' e E2_XIDFINA = '0001')
   - Realiza joins complexos entre tabelas SE5700, SE2700, CTK700 e SYS_COMPANY
   - Exclui pagamentos já processados (E5_DTARET vazio)

4. **Atualização de Retorno de Pagamento**:
   - Valida existência do RECNO antes de atualizar
   - Atualiza campo E5_DTARET com a data atual no formato yyyyMMdd

5. **Validações Gerais**:
   - IDs devem ser maiores que zero
   - Retorna HTTP 404 quando ID não encontrado
   - Retorna HTTP 400 para parâmetros inválidos
   - Retorna HTTP 204 (No Content) quando consultas não retornam dados

6. **Performance**:
   - Registra tempo de execução de consultas em logs
   - Utiliza índices de banco (NOLOCK hints para leitura)

---

## 6. Relação entre Entidades

**Entidades de Domínio**:

- **ListarCentroCustoDomain**: Representa um centro de custo
  - `recno` (Integer): Chave primária
  - `cttDescricao` (String): Descrição do centro de custo
  - `cttCusto` (Integer): Código do centro de custo

- **AtualizarRegistrosDomain**: Representa dados para atualização de centro de custo
  - `id` (int): RECNO do registro
  - `cttMsexp` (String): Data de exportação

- **ListarRetornoPagamentoDomain**: Representa informações de pagamento
  - `recno` (Integer): Chave primária
  - `idSist`, `idFina`, `m0CGC`, `e2XCGC`, `e2Lancame`, `e2XIdFlui`, `xnrPgto`, `e2Baixa`, `ctkDebito`, `e2IdCnab`, `eaDatabor` (String): Campos diversos do pagamento

**Relacionamentos**:
- As entidades são mapeadas diretamente de tabelas do SQL Server
- Não há relacionamentos JPA/Hibernate, pois o sistema utiliza JDBI para acesso direto via SQL
- Os relacionamentos são estabelecidos através de JOINs nas queries SQL

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| CTT700 | Tabela | SELECT | Tabela de centros de custo do Protheus |
| SE5700 | Tabela | SELECT | Tabela de movimentações bancárias/financeiras |
| SE2700 | Tabela | SELECT | Tabela de contas a pagar |
| CTK700 | Tabela | SELECT | Tabela de lançamentos contábeis |
| SYS_COMPANY | Tabela | SELECT | Tabela de empresas do sistema |
| #tmpCTK | Tabela Temporária | SELECT | Tabela temporária criada para otimização de consulta de pagamentos |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| CTT700 | Tabela | UPDATE | Atualiza campo CTT_MSEXP (data de exportação) |
| SE5700 | Tabela | UPDATE | Atualiza campo E5_DTARET (data de retorno) |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | Leitura | Configuração Spring Boot | Arquivo de configuração de logs (JSON format) |
| application.yml | Leitura | Configuração Spring Boot | Arquivo de propriedades da aplicação |
| application-local.yml | Leitura | Configuração Spring Boot | Propriedades para ambiente local |
| getRecno.sql | Leitura | ProtheusRepository | Query SQL para validar existência de RECNO |
| getRegistros.sql | Leitura | ProtheusRepository | Query SQL para listar centros de custo |
| putRegistros.sql | Leitura | ProtheusRepository | Query SQL para atualizar centro de custo |
| putRetornoPagamento.sql | Leitura | ProtheusRepository | Query SQL para atualizar retorno de pagamento |
| sboot-erpt-base-atom-protheus.yaml | Leitura | OpenAPI Generator | Contrato OpenAPI da API |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| ERP Protheus (SQL Server) | Banco de Dados | Integração direta com banco de dados do Protheus para leitura e escrita de dados |
| API Gateway BV | Autenticação | Validação de tokens JWT através de JWKS endpoint |
| Projuris (implícito) | Sistema Externo | Sistema consumidor das APIs de centros de custo (mencionado no README) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7.5/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades (camadas bem definidas: rest, service, repository, domain)
- Uso adequado de padrões como MapStruct para mapeamento
- Implementação de tratamento centralizado de exceções
- Documentação via OpenAPI/Swagger
- Uso de Lombok para reduzir boilerplate
- Logs estruturados em JSON
- Medição de performance das consultas
- Validações de entrada adequadas
- Configuração adequada para múltiplos ambientes

**Pontos de Melhoria:**
- Query SQL complexa hardcoded na classe `Constants` (deveria estar em arquivo .sql separado)
- Falta de testes unitários implementados (arquivos de teste existem mas não foram fornecidos)
- Classe `Constants` mistura constantes de mensagens com SQL complexo
- Método `calcularTempoExecucao` usa variáveis de instância para controle de tempo (não thread-safe)
- Falta de documentação JavaDoc nas classes
- Alguns métodos poderiam ser mais coesos (ex: `updateCentroCusto` faz muitas validações)
- Uso de `new ArrayList<>()` em catch poderia retornar Optional ou lançar exceção customizada
- Falta de paginação nas consultas que podem retornar muitos registros

---

## 14. Observações Relevantes

1. **Arquitetura Atlante**: O projeto segue os padrões do framework Atlante do Banco Votorantim, incluindo estrutura de camadas específica para Docker e configurações de infraestrutura como código.

2. **Segurança**: Todos os endpoints são protegidos por JWT, com validação através do API Gateway corporativo.

3. **Ambientes**: O sistema está preparado para 3 ambientes: DES (desenvolvimento), UAT (homologação) e PRD (produção), cada um com suas próprias configurações de banco e logs.

4. **Performance**: O sistema utiliza hints NOLOCK nas queries para melhorar performance de leitura, assumindo que inconsistências temporárias são aceitáveis.

5. **Observabilidade**: Integração com Prometheus e logs estruturados em JSON facilitam monitoramento e troubleshooting.

6. **Banco de Dados**: Todas as tabelas seguem nomenclatura do Protheus (sufixo 700 indica empresa/filial específica).

7. **Retry e Timeout**: Existe infraestrutura de bootstrap para gerenciamento de retry e timeout (bootstrap.sh), embora não esteja implementado no código Java.

8. **Multi-layer Docker**: Utiliza estratégia de camadas Docker otimizada para reduzir tempo de build e deploy.

9. **Auditoria**: Sistema integrado com trilha de auditoria corporativa através do `DefinidorBusinessAction`.

10. **Limitação Temporal**: A consulta de retorno de pagamento está hardcoded para buscar apenas os últimos 7 dias, o que pode ser uma limitação dependendo do caso de uso.