# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **java-spag-base-envio-esteira** é um componente de integração responsável por enviar lançamentos de pagamentos para filas JMS (esteiras de processamento) de acordo com o tipo de liquidação. O sistema recebe requisições via API REST, consulta dados de lançamentos no banco de dados, monta um objeto `DicionarioPagamento` e o envia para a fila JMS apropriada (TEF, DOC, Boleto, TED ou Tributo) conforme o código de liquidação.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `EnvioEsteiraBean` | EJB Stateless que orquestra o processo de envio para esteira. Recebe requisição, consulta dados, determina a fila destino e delega o envio. |
| `EnvioEsteiraBeanLocal` / `EnvioEsteiraBeanRemote` | Interfaces local e remota do EJB. |
| `EnvioEsteiraJmsProducer` | Classe responsável por produzir mensagens JMS e enviá-las para as filas configuradas. |
| `EnvioEsteiraDAOImpl` | Implementação DAO que consulta dados de lançamentos no banco de dados SQL Server. |
| `EnvioEsteiraRowMapper` | Mapper Spring JDBC que converte ResultSet em objetos de domínio. |
| `EnvioEsteira` (REST) | Endpoint REST que expõe a operação de envio para esteira via HTTP. |
| `MontaRequest` | Objeto de domínio que representa a requisição de entrada (protocolo e código cliente). |
| `Lancamento` | Entidade de domínio que encapsula o `DicionarioPagamento`. |
| `DicionarioPagamento` | Objeto de dados complexo (biblioteca externa) que representa todas as informações de um pagamento. |
| `Util` | Classe utilitária para tratamento de tipos de conta. |

---

## 3. Tecnologias Utilizadas

- **Java EE / Jakarta EE** (EJB 3.1, JAX-RS, JAX-WS)
- **Maven** (gerenciamento de dependências e build multi-módulo)
- **IBM WebSphere Application Server** (servidor de aplicação)
- **Spring JDBC** (acesso a dados)
- **JMS** (Java Message Service para mensageria)
- **JAXB** (marshalling/unmarshalling XML)
- **Gson** (serialização JSON)
- **SLF4J / Log4j2** (logging)
- **SQL Server** (banco de dados)
- **Swagger** (documentação de APIs REST)
- **JUnit, Mockito, PowerMock** (testes unitários)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/atacado/pagamentos/enviarEsteira` | `EnvioEsteira` | Recebe um `MontaRequest` (JSON) e envia o lançamento para a fila apropriada. |

---

## 5. Principais Regras de Negócio

1. **Roteamento por Tipo de Liquidação**: O sistema determina a fila JMS de destino com base no código de liquidação (`cdLiquidacaoITP`):
   - **TEF** (1, 61, 62, 55): Transferências eletrônicas, saques, compras com cartão, SLC/LDL.
   - **DOC** (21, 36): Documentos de crédito.
   - **Boleto** (22): Pagamentos de boletos.
   - **TED** (31, 32, 57): Transferências eletrônicas disponíveis (CIP, STR, Boleto STR).
   - **Tributo** (59, 60): Pagamentos de tributos e contas de concessionárias.

2. **Tratamento Especial para TED**: Para códigos 31, 32 e 57, verifica se o lançamento possui flag `flConfirmaSemSPB`. Se sim, envia para fila TEF; caso contrário, para fila TED. Se o tipo de lançamento for "E" (entrada), zera o tipo de conta do favorecido.

3. **Tratamento de Tipo de Conta**: Para DOC (21) com tipo de lançamento "E", o tipo de conta do favorecido é zerado.

4. **Validação de Cliente**: Se o código do cliente estiver presente na requisição, é atribuído ao dicionário de pagamento.

5. **Conversão de Tipos de Conta**: A classe `Util` converte códigos de tipo de conta (ex: "CI", "CC") para valores numéricos.

6. **Formatação de Mensagem XML**: A mensagem JMS é formatada em XML com namespaces específicos antes do envio.

---

## 6. Relação entre Entidades

- **MontaRequest**: Contém `idprotocolo` (String) e `cdCliente` (Integer).
- **Lancamento**: Contém um `DicionarioPagamento`.
- **DicionarioPagamento**: Objeto complexo com dezenas de atributos representando todos os dados de um pagamento (valores, datas, pessoas, contas, etc.).

**Relacionamento**: `MontaRequest` → `EnvioEsteiraBean` → `EnvioEsteiraDAO` → `Lancamento` (contém `DicionarioPagamento`) → `EnvioEsteiraJmsProducer` → Fila JMS.

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View | Tipo | Operação | Breve Descrição |
|---------------------|------|----------|-----------------|
| `TbLancamento` | Tabela | SELECT | Tabela principal de lançamentos de pagamentos. |
| `TbLancamentoPessoa` | Tabela | SELECT | Dados de pessoas (remetente/favorecido) relacionadas ao lançamento. |
| `TbLancamentoClienteFintech` | Tabela | SELECT | Dados de clientes fintech relacionados ao lançamento. |
| `TbParametroPagamentoFintech` | Tabela | SELECT | Parâmetros de pagamento para clientes fintech. |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View | Tipo | Operação | Breve Descrição |
|---------------------|------|----------|-----------------|
| `TbLancamento` | Tabela | UPDATE | Atualização do status do lançamento (`StLancamento`). |

**Observação**: A atualização de status está implementada no DAO (`atualizarStatusTbLancamento`), mas não é invocada no fluxo principal analisado.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `errorMessages.properties` | Leitura | `EnvioEsteiraJmsProducer`, módulos commons/integration | Arquivo de mensagens de erro. |
| `roles.properties` | Leitura | Módulo commons | Definição de roles de segurança. |
| `EnvioEsteiraDAOImpl-sql.xml` | Leitura | `EnvioEsteiraDAOImpl` | Arquivo XML contendo queries SQL. |

**Observação**: Não há evidências de gravação de arquivos no sistema.

---

## 10. Filas Lidas

**não se aplica** - O sistema não consome mensagens de filas JMS, apenas produz.

---

## 11. Filas Geradas

O sistema publica mensagens nas seguintes filas JMS:

| Nome da Fila (JNDI) | Descrição |
|---------------------|-----------|
| `jms/spagSolicitarPagamentoTefQueue` | Fila para pagamentos TEF, saques, compras com cartão, SLC/LDL. |
| `jms/spagSolicitarPagamentoDocQueue` | Fila para pagamentos DOC. |
| `jms/spagSolicitarPagamentoBoletoQueue` | Fila para pagamentos de boletos. |
| `jms/spagSolicitarPagamentoTedQueue` | Fila para pagamentos TED (CIP, STR). |
| `jms/spagSolicitarPagamentoTributoQueue` | Fila para pagamentos de tributos e contas de concessionárias. |

**Connection Factories correspondentes**: `jms/spagSolicitarPagamentoTef`, `jms/spagSolicitarPagamentoDoc`, `jms/spagSolicitarPagamentoBoleto`, `jms/spagSolicitarPagamentoTed`, `jms/spagSolicitarPagamentoTributo`.

---

## 12. Integrações Externas

- **Banco de Dados SQL Server**: Integração via JDBC (DataSource `jdbc/spagBaseDBSPAGDS`) para consulta de lançamentos.
- **Filas JMS**: Integração com sistema de mensageria (provavelmente IBM MQ ou similar) para envio de pagamentos para processamento.
- **Biblioteca Externa**: `votorantim.spag.lib.datatype.DicionarioPagamento` - biblioteca compartilhada de tipos de dados de pagamento.

**Observação**: Não há evidências de chamadas a APIs REST/SOAP externas no código analisado.

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Estrutura modular bem organizada (separação em camadas: domain, persistence, business, integration, rs).
- Uso de padrões Java EE (EJB, JAX-RS, JDBC).
- Separação de responsabilidades (DAO, Service, Producer).
- Uso de injeção de dependências.
- Presença de testes unitários.

**Pontos Negativos:**
- **Lógica de negócio complexa concentrada em um único método** (`enviarEsteira`): O switch-case com múltiplas condições dificulta manutenção e testes.
- **Tratamento de exceções genérico**: Uso de `catch (Exception e)` em vários pontos, o que pode mascarar erros específicos.
- **Código comentado**: Presença de código comentado em vários arquivos (pom.xml, classes), indicando falta de limpeza.
- **Falta de validações**: Não há validações robustas de entrada (ex: protocolo nulo, formato inválido).
- **Acoplamento**: Dependência direta de bibliotecas externas (`DicionarioPagamento`) sem abstrações.
- **Logging inconsistente**: Uso de `Logger` do `java.util.logging` e SLF4J em diferentes classes.
- **Métodos vazios**: Métodos de fechamento de recursos com blocos catch vazios (`closeQueueConnection`, `closeSession`, `closeMessageProducer`).
- **Falta de documentação**: Ausência de Javadoc em classes e métodos críticos.
- **Manipulação de strings XML**: Construção manual de XML via concatenação de strings é frágil e propensa a erros.

---

## 14. Observações Relevantes

1. **Segurança**: O sistema utiliza autenticação BASIC e roles (`spag-integracao`, `intr-middleware`). Configurações de segurança WS-Security estão presentes nos arquivos de deployment.

2. **Transações**: O EJB principal está configurado com `TransactionAttributeType.NOT_SUPPORTED`, ou seja, não participa de transações gerenciadas pelo container.

3. **Arquitetura**: O projeto segue uma arquitetura em camadas típica de aplicações Java EE, com separação clara entre apresentação (REST), negócio (EJB), persistência (DAO) e integração (JMS).

4. **Dependências Externas**: O sistema depende de bibliotecas de arquitetura do Banco Votorantim (`fjee-base`, `arqt-base`) e de uma biblioteca compartilhada de pagamentos (`java-spag-base-pagamentos-commons`).

5. **Deployment**: O sistema é empacotado como EAR (Enterprise Archive) contendo módulos EJB e WAR (REST).

6. **Versionamento**: O projeto utiliza Git para controle de versão e Jenkins para CI/CD (arquivo `jenkins.properties`).

7. **Swagger**: Há configuração para geração de documentação Swagger das APIs REST.

8. **Handlers JAX-WS/JAX-RS**: O sistema utiliza handlers customizados para trilha de auditoria, contexto de requisição e tratamento de falhas.

9. **Conversão de Protocolo**: O protocolo de entrada pode conter sufixo (ex: "12345-67"), que é removido antes da consulta no banco.

10. **Flag `flConfirmaSemSPB`**: Regra específica para TED que verifica se o lançamento deve ser confirmado sem passar pelo SPB (Sistema de Pagamentos Brasileiro).