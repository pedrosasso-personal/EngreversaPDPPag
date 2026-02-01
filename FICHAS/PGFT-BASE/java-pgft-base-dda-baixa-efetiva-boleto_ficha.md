# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema Java EE para processamento de avisos de baixa efetiva de títulos DDA (Débito Direto Autorizado). O sistema recebe mensagens via JMS contendo informações sobre baixas efetivas de boletos no padrão DDA0118R2, valida a existência do título na base de dados e registra a baixa efetiva através de stored procedure no banco de dados SQL Server (Sybase).

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **AvisarBaixaEfetiva** (JMS) | Message-Driven Bean que consome mensagens da fila JMS e orquestra o processamento |
| **ConverterUtil** | Utilitário para conversão de mensagens JMS (TextMessage/BytesMessage) em objetos Java e desserialização XML |
| **AvisarBaixaEfetivaBean** | EJB Stateless que implementa a lógica de negócio principal (busca e registro de baixa) |
| **AvisarBaixaEfetivaDAO** / **AvisarBaixaEfetivaDAOImpl** | Interface e implementação para acesso a dados (busca de título e inserção de baixa) |
| **AvisarBaixaEfetivaStoreProcedure** | Encapsula a chamada à stored procedure `PrInserirTituloDDABaixaEfetiva` |
| **DebitoDiretoAutorizadoDDA0118R2Mensagem** | Entidade de domínio gerada via JAXB representando a mensagem DDA |
| **AvisarBaixaEfetivaOUTMapper** | RowMapper para mapeamento de resultados de consultas SQL |
| **DataTypesUtil** | Utilitário para conversão de tipos de dados (String para BigDecimal/Integer) |

---

## 3. Tecnologias Utilizadas

- **Java EE 6/7** (EJB 3.1, JMS, CDI, JAX-WS)
- **IBM WebSphere Application Server** (runtime)
- **Maven** (gerenciamento de dependências e build)
- **Spring JDBC** (acesso a dados via JDBC)
- **JAXB** (binding XML/Java)
- **SLF4J** (logging)
- **JUnit, Mockito, PowerMock** (testes unitários)
- **SQL Server/Sybase** (banco de dados - schema DBPGF_TES)
- **IBM MQ / JMS** (mensageria)
- **Apache Commons Lang3**

---

## 4. Principais Endpoints REST

**não se aplica**

O sistema não expõe endpoints REST. A comunicação é baseada em mensageria JMS (Message-Driven Bean).

---

## 5. Principais Regras de Negócio

1. **Validação de Existência do Título**: Antes de registrar a baixa efetiva, o sistema verifica se o título existe na base DDA através do número de identificação do título (`NuIdentificacaoTitulo`).

2. **Registro Condicional**: A baixa efetiva só é registrada se o título for localizado na base (`CdTituloDDA` diferente de null e zero). Caso contrário, apenas registra log informativo.

3. **Conversão de Tipos**: Campos numéricos da mensagem XML (strings) são convertidos para tipos apropriados (BigDecimal, Integer) antes da persistência.

4. **Tratamento de Mensagens**: O sistema aceita mensagens JMS tanto no formato TextMessage quanto BytesMessage, realizando conversão automática.

5. **Rollback em Caso de Erro**: Em caso de BusinessException, a transação JMS é marcada para rollback, permitindo reprocessamento da mensagem.

6. **Auditoria**: Todas as inserções de baixa efetiva registram o login do sistema (`java-pgft-base-dda-baixa-efetiva-boleto`) para auditoria.

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **DebitoDiretoAutorizadoDDA0118R2Mensagem**: Representa a mensagem DDA recebida via JMS, contendo todos os dados da baixa efetiva (identificação do título, valores, datas, situações, etc.)

- **AvisarBaixaEfetivaOUT**: Entidade de saída (atualmente sem atributos específicos, apenas herda de EntidadeBase)

**Relacionamento:**
- A mensagem DDA é desserializada do XML e utilizada para buscar o título correspondente na base de dados
- O código do título (`CdTituloDDA`) é recuperado e utilizado como chave para inserção dos dados de baixa efetiva

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| DBPGF_TES..TbTituloDDA | tabela | SELECT | Consulta para buscar o código do título DDA através do número de identificação |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| DBPGF_TES..PrInserirTituloDDABaixaEfetiva | stored procedure | INSERT | Procedure que insere/atualiza dados de baixa efetiva do título DDA com 14 parâmetros (código título, datas, valores, situações, etc.) |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| AvisarBaixaEfetivaDAOImpl-sql.xml | leitura | AvisarBaixaEfetivaDAOImpl | Arquivo XML contendo queries SQL parametrizadas (buscarTitulo) |
| DebitoDiretoAutorizadoDDA0118R2Mensagem.xsd | leitura | Plugin JAXB (build time) | Schema XSD para geração das classes de domínio via JAXB |
| errorMessages.properties | leitura | commons module | Repositório de mensagens de erro do sistema |
| roles.properties | leitura | commons module | Definição de roles de segurança da aplicação |

---

## 10. Filas Lidas

- **queue/PGFTBaixaEfetivaTituloDdaQueue**: Fila JMS da qual o MDB `AvisarBaixaEfetiva` consome mensagens contendo avisos de baixa efetiva de títulos DDA. A fila está vinculada ao Activation Spec `as/PGFTBaixaEfetivaTituloDdaAS` configurado no WebSphere.

---

## 11. Filas Geradas

**não se aplica**

O sistema não publica mensagens em filas. Atua apenas como consumidor JMS.

---

## 12. Integrações Externas

**não se aplica**

O sistema não possui integrações diretas com sistemas externos via APIs REST ou Web Services. A integração ocorre através de:
- **Mensageria JMS**: Recebe mensagens de baixa efetiva (origem não especificada no código)
- **Banco de Dados**: Acessa o schema DBPGF_TES via JDBC/DataSource `jdbc/PgftCobrancaDDADS`

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura em camadas bem definida (JMS, Business, Persistence, Domain)
- Uso de padrões Java EE (EJB, CDI, JMS)
- Separação de responsabilidades entre módulos Maven
- Uso de frameworks consolidados (Spring JDBC)
- Tratamento de exceções com logging estruturado
- Testes unitários presentes (embora básicos)

**Pontos Negativos:**
- **Logging excessivo e inadequado**: Uso de `e.printStackTrace(System.out)` e múltiplos logs de erro redundantes
- **Tratamento genérico de exceções**: Catch de `Exception` genérica em vários pontos
- **Falta de validações**: Não há validação dos dados da mensagem antes do processamento
- **Código comentado**: Testes com código comentado indicam falta de manutenção
- **Entidade vazia**: `AvisarBaixaEfetivaOUT` não possui atributos, questionando sua necessidade
- **Hardcoded values**: Login do sistema hardcoded na DAO
- **Falta de documentação**: Ausência de Javadoc nas classes principais
- **Contador não utilizado**: Variável `contador` no MDB incrementada mas não utilizada efetivamente
- **Conversão manual de tipos**: Poderia usar bibliotecas mais robustas para conversão

---

## 14. Observações Relevantes

1. **Segurança**: O sistema utiliza role `intr-middleware` com `ALL_AUTHENTICATED_USERS`, permitindo acesso a qualquer usuário autenticado.

2. **Transações**: O EJB de negócio está configurado com `TransactionAttributeType.NOT_SUPPORTED`, delegando o controle transacional ao MDB.

3. **Reprocessamento**: O sistema conta tentativas de delivery (`JMSXDeliveryCount`) mas não implementa lógica de dead letter queue ou limite de tentativas.

4. **Adaptadores de Data**: Implementa adaptadores JAXB customizados para conversão de datas XML (DateAdapter e DateTimeAdapter).

5. **Dependências Externas**: O sistema depende de bibliotecas corporativas Votorantim (`fjee-base-commons`, `arqt-base-lib`) não disponíveis publicamente.

6. **Ambiente**: Configurado especificamente para IBM WebSphere Application Server com políticas de segurança WS-Security.

7. **Schema XSD**: A mensagem DDA segue padrão específico com 24 campos obrigatórios e opcionais definidos no XSD.

8. **Versionamento**: Sistema na versão 0.1.0, indicando fase inicial de desenvolvimento.