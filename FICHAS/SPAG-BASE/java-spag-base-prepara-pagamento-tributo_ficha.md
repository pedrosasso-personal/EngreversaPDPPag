# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **java-spag-base-prepara-pagamento-tributo** é um componente Java EE responsável por preparar pagamentos de tributos no contexto do sistema SPAG (Sistema de Pagamentos) do Banco Votorantim. Sua principal função é receber solicitações de preparação de pagamento de tributos, validar se o pagamento já não está aguardando processamento em lote, e caso não esteja, gravar os dados na tabela `TbMovimentoLotePagamentoTrbto` e atualizar o status do lançamento na tabela `TbLancamento`. O sistema expõe suas funcionalidades através de uma API REST.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `PreparaPagamentoBean` | EJB Stateless que contém a lógica de negócio principal para preparar pagamentos de tributos |
| `PreparaPagamentoDAO` / `PreparaPagamentoDAOImpl` | Interface e implementação do padrão DAO para acesso aos dados de pagamento |
| `PreparaPagamentoRowMapper` | Mapper Spring JDBC para conversão de ResultSet em objetos de domínio |
| `PreparaPagamento` (REST) | Endpoint REST que expõe o serviço de preparação de pagamento via HTTP |
| `PagamentoRetorno` | Entidade de domínio representando o retorno de um pagamento |
| `PreparaPagamentoTributo` / `PreparaPagamentoTributoRequest` / `PreparaPagamentoTributoResponse` | DTOs para requisição e resposta do serviço |
| `RestExceptionMapper` | Mapeador de exceções para tratamento de erros em endpoints REST |
| `BaseAppConfig` / `SecurityAppConfig` / `UtilsAppConfig` | Configurações de aplicação JAX-RS para diferentes contextos |

---

## 3. Tecnologias Utilizadas

- **Java EE 7** (EJB 3.1, JAX-RS 2.0, CDI, JMS)
- **IBM WebSphere Application Server** (servidor de aplicação)
- **Maven** (gerenciamento de dependências e build multi-módulo)
- **Spring JDBC** (acesso a dados via NamedParameterJdbcTemplate)
- **SLF4J / Log4j2** (logging)
- **Swagger** (documentação de APIs REST)
- **JUnit / Mockito / PowerMock** (testes unitários)
- **Oracle Database** (banco de dados - driver OJDBC6)
- **Arquitetura Votorantim** (fjee-base-commons, arqt-base-lib)
- **Biblioteca SPAG** (java-spag-base-pagamentos-commons)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/spag-base-prepara-pagamento-tributo-rs/v1/atacado/pagamentos/preparaPagamentoTributo` | `PreparaPagamento` | Recebe uma requisição de preparação de pagamento de tributo e processa a gravação dos dados |

---

## 5. Principais Regras de Negócio

1. **Validação de Duplicidade**: Antes de gravar um novo pagamento, o sistema verifica se já existe um registro para o mesmo código de lançamento (`CdLancamento`) na tabela `TbMovimentoLotePagamentoTrbto`.

2. **Gravação Condicional**: Se o pagamento não existir, o sistema grava um novo registro com status inicial `00` (aguardando lote).

3. **Atualização de Status do Lançamento**: Após gravar o movimento de lote, o sistema atualiza o status do lançamento (`StLancamento`) para `02` na tabela `TbLancamento`.

4. **Tratamento de Erros**: Em caso de exceção, o sistema adiciona uma ocorrência genérica ao dicionário de pagamento com código de erro e descrição, além de definir a flag de retorno `flRetornoPreparaPagtoTributo` com valor indicativo de erro.

5. **Segurança**: O acesso ao serviço é restrito às roles `spag-integracao` e `intr-middleware` através de anotações `@RolesAllowed`.

6. **Transação**: O bean de negócio opera com `TransactionAttributeType.NOT_SUPPORTED`, delegando o controle transacional para camadas inferiores.

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **DicionarioPagamento**: Objeto central que transporta todas as informações do pagamento (código de lançamento, valor, parâmetros, protocolo, etc.)
- **PagamentoRetorno**: Entidade de domínio que representa o retorno de consultas de pagamento
- **PreparaPagamentoTributo**: Wrapper para o DicionarioPagamento
- **PreparaPagamentoTributoRequest/Response**: DTOs de entrada e saída do serviço REST

**Relacionamentos:**
- `PreparaPagamentoTributoRequest` contém `PreparaPagamentoTributo`
- `PreparaPagamentoTributo` contém `DicionarioPagamento`
- `PreparaPagamentoTributoResponse` retorna `PreparaPagamentoTributo` com o `DicionarioPagamento` processado

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbMovimentoLotePagamentoTrbto | Tabela | SELECT | Consulta para verificar se já existe um pagamento aguardando lote para o código de lançamento informado |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbMovimentoLotePagamentoTrbto | Tabela | INSERT | Insere novo registro de movimento de lote de pagamento de tributo com status inicial 00 |
| TbLancamento | Tabela | UPDATE | Atualiza o status do lançamento para 02 (preparado para pagamento) e a data de alteração |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| PreparaPagamentoDAOImpl-sql.xml | Leitura | `PreparaPagamentoDAOImpl` | Arquivo XML contendo as queries SQL utilizadas pelo DAO (checaPagamento, inserirPagamento) |
| errorMessages.properties | Leitura | commons/resources | Arquivo de propriedades contendo mensagens de erro do sistema |
| roles.properties | Leitura | commons/resources | Arquivo de propriedades contendo definição de roles de segurança |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

não se aplica

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura modular bem organizada (separação em módulos: business, persistence, domain, rs, commons)
- Uso adequado de padrões Java EE (EJB, CDI, JAX-RS)
- Implementação do padrão DAO para isolamento da camada de persistência
- Uso de injeção de dependências
- Presença de testes unitários
- Documentação Swagger para APIs REST

**Pontos Negativos:**
- **Tratamento de exceções genérico**: O catch captura `Exception` de forma muito ampla, dificultando diagnóstico de problemas específicos
- **Logging insuficiente**: Falta de logs detalhados em pontos críticos do fluxo
- **Hardcoding de valores**: Strings como "java-spag-base-prepara-pagamento-tributo" e códigos numéricos (00, 02) estão hardcoded
- **Falta de validações**: Não há validação dos dados de entrada antes do processamento
- **Nomenclatura inconsistente**: Pacote `br.com.vototantim` (com erro de digitação) vs `br.com.votorantim`
- **RowMapper vazio**: `PreparaPagamentoRowMapper` retorna objeto vazio, indicando possível código não finalizado
- **Comentários em código**: Diversos trechos comentados no POM e em outras classes
- **Falta de documentação JavaDoc**: Classes e métodos sem documentação adequada

---

## 14. Observações Relevantes

1. **Datasource JNDI**: O sistema utiliza o datasource `jdbc/spagBaseDBSPAGDS` configurado no WebSphere.

2. **Dependências de Arquitetura Corporativa**: O projeto depende fortemente de bibliotecas proprietárias do Banco Votorantim (fjee-base, arqt-base, spag-base-pagamentos-commons), o que indica forte acoplamento com a arquitetura corporativa.

3. **Módulos Desabilitados**: Os módulos `jms` e `ws` estão comentados no POM principal, sugerindo que funcionalidades de mensageria e web services SOAP foram desabilitadas ou não estão em uso.

4. **Handlers de Trilha de Auditoria**: O sistema possui handlers configurados para captura de trilha de auditoria tanto em REST quanto em Web Services (se habilitado).

5. **Segurança**: Autenticação BASIC configurada no web.xml com realm "default".

6. **Versionamento**: O projeto utiliza versionamento semântico (0.4.0) e está configurado para integração com Git e Jenkins.

7. **ClassLoader Policy**: Configurado como `PARENT_LAST` no deployment.xml, permitindo que bibliotecas da aplicação tenham precedência sobre as do servidor.

8. **Bibliotecas Compartilhadas**: Utiliza shared libraries do WebSphere (arqt-base-lib-1.0, fjee-base-lib-1.1).