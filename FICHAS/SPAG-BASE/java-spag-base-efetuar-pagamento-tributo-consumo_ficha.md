# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema responsável por efetuar pagamentos de tributos através de integração com a API IS2B (CA-API). O sistema recebe requisições REST contendo dados de pagamento de tributos, consulta parâmetros no banco de dados SPAG, realiza a autenticação OAuth2, e efetua o pagamento através de chamadas HTTP à API externa. Implementado em Java EE com arquitetura modular Maven (EJB, JAX-RS, JDBC).

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `EfetuarPagamentoTributoBean` | EJB Stateless que implementa a lógica de negócio para efetuação de pagamentos de tributos |
| `EfetuarPagamentoTributo` | Endpoint REST que expõe o serviço de pagamento via JAX-RS |
| `EfetuarIntegrationServices` | Serviço de integração responsável por chamar a API externa IS2B para efetuar pagamentos |
| `HttpCaapiIntegration` | Classe abstrata que gerencia chamadas HTTP para a CA-API com tratamento de token OAuth |
| `CriarTokenIntegration` | Responsável por obter e gerenciar tokens OAuth2 para autenticação na API |
| `PagamentoTributoSpagDaoImpl` | DAO que acessa o banco SPAG para buscar URL de efetuação de pagamento |
| `EfetivaRowMapper` | Mapper Spring JDBC para conversão de ResultSet em objeto EfetivaUrl |
| `RestExceptionMapper` | Provider JAX-RS para tratamento centralizado de exceções REST |

---

## 3. Tecnologias Utilizadas

- **Java EE 7** (EJB 3.1, JAX-RS, CDI)
- **Maven** (gerenciamento de dependências e build)
- **IBM WebSphere Application Server** (servidor de aplicação)
- **Spring JDBC** (acesso a dados)
- **Apache HttpClient** (chamadas HTTP)
- **Gson** (serialização/deserialização JSON)
- **OAuth2** (autenticação)
- **JUnit, Mockito, PowerMock** (testes)
- **Swagger** (documentação de APIs)
- **Log4j2/SLF4J** (logging)
- **Apache Commons Lang3** (utilitários)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/spag-base-efetuar-pagamento-tributo-consumo-rs/v1/atacado/pagamentos/efetuarPagamento` | `EfetuarPagamentoTributo` | Efetua pagamento de tributo recebendo DicionarioPagamento e retornando resultado da operação |

---

## 5. Principais Regras de Negócio

1. **Validação de Banco Remetente**: Se o código do banco remetente for 413 ou 436, o código do banco é ajustado para 413 na requisição
2. **Tratamento de Valores Nulos**: Valores bruto, desconto e acréscimo são tratados como BigDecimal(0) quando nulos
3. **Formatação de Data**: Datas de vencimento têm o sufixo "-03:00" removido antes do envio
4. **Retry de Integração**: Em caso de falha na chamada da API, o sistema tenta novamente uma vez antes de lançar exceção
5. **Validação de Sucesso**: Apenas respostas com código de erro "000" são consideradas bem-sucedidas e têm os dados de pagamento preenchidos
6. **Gerenciamento de Token OAuth**: Token é renovado automaticamente em caso de erro 401 (Unauthorized) ou 403 (Forbidden)
7. **Forma de Pagamento Fixa**: Sempre utiliza "DINHEIRO" como forma de pagamento

---

## 6. Relação entre Entidades

**Entidades de Domínio:**

- `EfetuarPagamentoRequest` → contém → `EfetuarPagamento` → contém → `DicionarioPagamento` (com `TributoDTO`)
- `EfetuarPagamentoResponse` → contém → `EfetuarPagamento` → contém → `DicionarioPagamento` (com `TributoDTO` atualizado)
- `EfetuarRequest` → objeto de requisição para API IS2B
- `EfetuarResponse` → contém → `Pagamento` (resposta da API IS2B)
- `EfetivaUrl` → entidade que armazena URL da API de efetuação

**Relacionamentos:**
- `DicionarioPagamento` possui um `TributoDTO` com dados do tributo a ser pago
- `EfetuarResponse` possui um objeto `Pagamento` com resultado da transação
- Não há relacionamentos JPA/ORM, apenas objetos de transferência de dados (DTOs)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| `DBSPAG..TbParametroPagamentoTributo` | Tabela | SELECT | Busca a URL de efetuação de pagamento (campo DsUrlEfetivaPagamento) |

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema não realiza operações de INSERT, UPDATE ou DELETE em banco de dados.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `config-arqt-base.properties` | Leitura | `ConfigArqtrBaseProperties` | Configurações de URLs de API Gateway e OAuth |
| `errorMessages.properties` | Leitura | Commons | Mensagens de erro do sistema |
| `roles.properties` | Leitura | Commons | Definição de roles de segurança |
| `PagamentoTributoSpagDaoImpl-sql.xml` | Leitura | `PagamentoTributoSpagDaoImpl` | Queries SQL para acesso ao banco SPAG |

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas JMS, Kafka ou RabbitMQ.

---

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas.

---

## 12. Integrações Externas

| Sistema/API | Tipo | Descrição |
|-------------|------|-----------|
| **API IS2B (CA-API)** | REST/HTTP | API externa para efetuação de pagamentos de tributos. Endpoint configurável via propriedade `api.gateway.address` + URL dinâmica do banco |
| **OAuth2 Service** | REST/HTTP | Serviço de autenticação OAuth2 para obtenção de tokens JWT. URL configurada em `rest.url.oauth.intranet` |
| **Banco SPAG (SQL Server)** | JDBC | Banco de dados para consulta de parâmetros de pagamento. DataSource: `jdbc/spagBaseDBSPAGDS` |

**Detalhes da Integração IS2B:**
- Autenticação: OAuth2 Client Credentials (client_id e client_secret via JNDI)
- Formato: JSON
- Método: POST
- Headers: Trilha de auditoria (ticket, siglaSistema, loginUsuarioFinal, enderecoIpCliente)
- Retry: 1 tentativa adicional em caso de falha

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura modular bem organizada (separação em camadas: domain, business, persistence, integration, rs)
- Uso adequado de padrões Java EE (EJB, CDI, JAX-RS)
- Tratamento de exceções estruturado
- Testes unitários presentes
- Uso de injeção de dependências

**Pontos Negativos:**
- **Código comentado**: Diversos trechos de código comentado (módulos ws, jms) que deveriam ser removidos
- **Hardcoding**: Valores fixos como "DINHEIRO", "CART", código 655 no código
- **Tratamento de erro genérico**: Múltiplos `catch (Exception e)` sem tratamento específico
- **Falta de validações**: Não há validação de entrada nos endpoints REST
- **Logging inconsistente**: Mistura de `Logger` do java.util.logging e SLF4J
- **Retry manual**: Lógica de retry implementada manualmente com try-catch aninhado
- **Acoplamento**: Classe `HttpCaapiIntegration` com múltiplas responsabilidades
- **Configuração via JNDI**: Busca de propriedades via JNDI com tratamento de erro inadequado
- **Documentação**: Falta de Javadoc em métodos importantes
- **Magic strings**: Strings literais espalhadas pelo código sem constantes

---

## 14. Observações Relevantes

1. **Segurança**: O sistema utiliza autenticação BASIC e roles declarativas (`spag-integracao`, `intr-middleware`)

2. **Transações**: Todos os componentes principais utilizam `@TransactionAttribute(TransactionAttributeType.NOT_SUPPORTED)`, indicando que não há gerenciamento transacional

3. **Configuração de Ambiente**: O sistema suporta múltiplos ambientes (DES, QA, UAT, PRD) através de propriedades configuráveis

4. **Dependências Externas**: O sistema depende de bibliotecas customizadas do Banco Votorantim:
   - `java-spag-base-pagamentos-commons`
   - `fjee-base-lib`
   - `arqt-base-lib`

5. **Formato de Data**: O sistema trabalha com datas no formato ISO com timezone "-03:00" (horário de Brasília)

6. **Token Management**: Implementa cache de token OAuth2 em sessão (`@SessionScoped`) para evitar requisições desnecessárias

7. **Trilha de Auditoria**: Implementa captura de trilha de auditoria através de handlers JAX-RS e filtros

8. **Deployment**: Aplicação empacotada como EAR com classloader PARENT_LAST e bibliotecas compartilhadas

9. **Swagger**: Documentação de API disponível, mas configuração básica sem detalhamento de schemas

10. **Código Legado**: Presença de módulos desabilitados (ws, jms) sugere evolução arquitetural de SOAP para REST