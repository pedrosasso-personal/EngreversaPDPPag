# Ficha Técnica do Sistema

---

## 1. Descrição Geral

O sistema **spag-base-monta-dicionario** é um componente de integração do sistema de pagamentos (SPAG) do Banco Votorantim. Sua principal função é montar e retornar um dicionário de pagamento completo a partir de um protocolo de transação. O sistema consulta informações de lançamentos de pagamento no banco de dados, incluindo dados do remetente, favorecido e clientes fintech, consolidando essas informações em um objeto `DicionarioPagamento` que é retornado em formato JSON via API REST.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `MontaDicionarioBean` | EJB Stateless que implementa a lógica de negócio principal para montagem do dicionário de pagamento |
| `MontaDicionario` | Endpoint REST que expõe o serviço de montagem de dicionário via HTTP |
| `MontaDicionarioDAO` / `MontaDicionarioDAOImpl` | Interface e implementação da camada de acesso a dados para consulta de informações de pagamento |
| `MontaDicionarioRowMapper` | Mapper responsável por transformar ResultSet do banco em objetos de domínio |
| `DicionarioPag` | Entidade de domínio que encapsula o objeto `DicionarioPagamento` |
| `MontaRequest` | DTO que representa a requisição com protocolo e código do cliente |
| `RestExceptionMapper` | Mapeador de exceções para respostas REST padronizadas |

---

## 3. Tecnologias Utilizadas

- **Java EE 6/7** (EJB 3.1, JAX-RS, CDI, JMS)
- **IBM WebSphere Application Server** (servidor de aplicação)
- **Maven** (gerenciamento de dependências e build multi-módulo)
- **Spring JDBC** (NamedParameterJdbcTemplate para acesso a dados)
- **Gson** (serialização/deserialização JSON)
- **Swagger** (documentação de APIs REST)
- **JUnit, Mockito, PowerMock** (testes unitários)
- **Log4j2 / SLF4J** (logging)
- **Oracle JDBC** (driver de banco de dados)
- **Apache Commons Lang3** (utilitários)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/spag-base-monta-dicionario-rs/v1/atacado/pagamentos/montaDicionario` | `MontaDicionario` | Recebe um `MontaRequest` (JSON) contendo idprotocolo e cdCliente, e retorna um `DicionarioPagamento` completo com todas as informações do lançamento |

---

## 5. Principais Regras de Negócio

1. **Consulta de Dicionário por Protocolo**: O sistema recebe um identificador de protocolo no formato `{CdLancamento}-{NuProtocoloTransacaoPagamento}` e realiza a busca no banco de dados.

2. **Enriquecimento com Código do Cliente**: Se o código do cliente (`cdCliente`) for informado na requisição, ele é adicionado ao dicionário de pagamento retornado.

3. **Consolidação de Dados de Múltiplas Tabelas**: O sistema realiza LEFT JOINs entre `TbLancamento`, `TbLancamentoPessoa`, `TbLancamentoClienteFintech` e `TbParametroPagamentoFintech` para montar um dicionário completo.

4. **Conversão de Flags Booleanas**: Converte flags do tipo 'S'/'N' para '1'/'0' (ex: `FlPreConfirmado`).

5. **Tratamento de Tipo de Pessoa**: Determina o tipo de pessoa (Física/Jurídica) baseado no tamanho do CPF/CNPJ (>= 13 caracteres = Jurídica).

6. **Segurança por Roles**: O acesso ao EJB é restrito às roles `spag-integracao` e `intr-middleware`.

7. **Transações NOT_SUPPORTED**: O componente não participa de transações gerenciadas pelo container.

---

## 6. Relação entre Entidades

**Entidades de Domínio:**
- `MontaRequest`: Contém `idprotocolo` (String) e `cdCliente` (Integer)
- `DicionarioPag`: Wrapper que contém um objeto `DicionarioPagamento`
- `DicionarioPagamento`: Classe complexa da biblioteca `votorantim.spag.lib.datatype` com dezenas de atributos relacionados a pagamentos

**Relacionamentos:**
- `MontaDicionarioBean` → utiliza → `MontaDicionarioDAO`
- `MontaDicionarioDAO` → retorna → `DicionarioPag`
- `DicionarioPag` → contém → `DicionarioPagamento`
- `MontaDicionario` (REST) → invoca → `MontaDicionarioBeanLocal`

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbLancamento | Tabela | SELECT | Tabela principal de lançamentos de pagamento, contém informações como valor, tipo, datas, códigos de barras, etc. |
| TbLancamentoPessoa | Tabela | SELECT | Contém dados de remetente e favorecido (CPF/CNPJ, agência, conta, banco) |
| TbLancamentoClienteFintech | Tabela | SELECT | Dados específicos de clientes fintech (remetente e favorecido fintech) |
| TbParametroPagamentoFintech | Tabela | SELECT | Parâmetros de configuração para pagamentos fintech (usado no JOIN) |

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| MontaDicionarioDAOImpl-sql.xml | Leitura | `MontaDicionarioDAOImpl` / `ArquivoQueries` | Arquivo XML contendo a query SQL nomeada "consultaDicionario" para busca de dados de pagamento |
| errorMessages.properties | Leitura | Commons (recursos) | Arquivo de mensagens de erro do sistema |
| roles.properties | Leitura | Commons (recursos) | Lista de roles da aplicação |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

**Banco de Dados Oracle:**
- **JNDI**: `jdbc/spagBaseDBSPAGDS`
- **Descrição**: Datasource principal para consulta de informações de pagamentos no schema do SPAG

**Bibliotecas Externas:**
- `votorantim.spag.lib.datatype.DicionarioPagamento`: Biblioteca compartilhada do SPAG contendo o modelo de dados de pagamento
- `br.com.votorantim.fjee.base.commons`: Framework base da arquitetura Votorantim (FJEE) para persistência, trilha de auditoria, handlers, etc.

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada em camadas (presentation, business, persistence, domain)
- Uso adequado de padrões Java EE (EJB, CDI, JAX-RS)
- Separação clara de responsabilidades entre camadas
- Uso de interfaces para contratos de serviço (Local/Remote)
- Testes unitários presentes com uso de mocks
- Configuração de segurança com roles declarativas
- Uso de RowMapper customizado para mapeamento de dados

**Pontos de Melhoria:**
- Query SQL extremamente longa e complexa embutida em XML (dificulta manutenção)
- Uso excessivo de LTRIM/RTRIM na query (deveria ser tratado na aplicação)
- Tratamento de exceções genérico com apenas log (catch Exception sem especificidade)
- Conversão manual de tipos na query SQL (ex: FlPreConfirmado com CASE)
- Falta de validações de entrada no endpoint REST
- Código comentado em vários arquivos POM e de configuração
- Dependência forte de biblioteca externa (`votorantim.spag.lib.datatype`)
- Falta de documentação JavaDoc nas classes principais
- Uso de `TOP 1` sem ORDER BY na query (resultado não determinístico)

---

## 14. Observações Relevantes

1. **Arquitetura Multi-Módulo**: O projeto segue uma estrutura Maven modular bem organizada (business, commons, domain, persistence, rs, ws, ear, integration, jms).

2. **Compatibilidade WebSphere**: O sistema foi desenvolvido especificamente para IBM WebSphere Application Server, com configurações específicas (ibm-ejb-jar-bnd.xml, ibm-web-bnd.xml, etc.).

3. **Versionamento**: A versão atual do componente é 0.5.0, indicando que ainda está em fase de desenvolvimento/estabilização.

4. **Handlers de Auditoria**: O sistema utiliza handlers JAX-RS e JAX-WS para captura de trilha de auditoria e inicialização de contexto de requisição.

5. **Segurança**: Implementa autenticação BASIC e autorização baseada em roles do WebSphere.

6. **Swagger**: Possui configuração para geração automática de documentação Swagger das APIs REST.

7. **Módulos Desabilitados**: Os módulos WS (Web Services SOAP), JMS e Integration estão comentados no POM, indicando que o sistema atualmente expõe apenas APIs REST.

8. **Classloader PARENT_LAST**: Configurado no deployment.xml para permitir que bibliotecas da aplicação tenham precedência sobre as do servidor.

9. **Shared Libraries**: Utiliza bibliotecas compartilhadas do WebSphere (arqt-base-lib, fjee-base-lib) para componentes comuns de arquitetura.

10. **Pipeline CI/CD**: Possui arquivo jenkins.properties indicando integração com pipeline de build automatizado.