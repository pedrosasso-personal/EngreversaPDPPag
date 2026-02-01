# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **java-spag-base-pagamento-tributo** é uma aplicação Java EE voltada para o processamento de solicitações de pagamento de tributos. Permite que clientes (incluindo fintechs) solicitem pagamentos de tributos através de APIs REST, realizando validações de origem, cadastro de parceiros comerciais e registro das transações em banco de dados. O sistema suporta fluxos diferenciados para contas de pagamento (fintechs) e contas correntes tradicionais, substituindo dados do cliente pelos dados da fintech quando aplicável.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `SolicitacaoPagamentoTributoBean` | Bean EJB que contém a lógica de negócio principal para processar solicitações de pagamento de tributos, validar campos, determinar código de liquidação e tratar fluxos de fintech. |
| `SolicitarPagamentoTributo` | Endpoint REST que expõe a API `/atacado/pagamentos/incluirPagamento` para receber solicitações de pagamento em formato JSON. |
| `SolicitacaoLancamentoTributoDAO` / `SolicitacaoLancamentoTributoDAOImpl` | Interface e implementação DAO responsáveis por executar a stored procedure `PrSolicitaPagamentoTributos` para registrar o pagamento no banco de dados. |
| `ValidacaoOrigemPagamentoDAO` / `ValidacaoOrigemPagamentoDAOImpl` | Interface e implementação DAO para consultar cadastro de fintechs na tabela `TbValidacaoOrigemPagamento`, validar existência de contas e protocolos de solicitação. |
| `SolicitacaoLancamentoTributoStoredProcedure` | Classe que encapsula a chamada à stored procedure de registro de pagamento de tributos. |
| `Solicitacao` | Entidade de domínio que representa os dados da solicitação de pagamento. |
| `SolicitacaoRetorno` | Entidade de domínio que representa o retorno da solicitação (protocolo, status). |
| `ValidacaoOrigemPagamentoDTO` | DTO que armazena dados de validação de origem de pagamento (fintech). |
| `NuBanco` | Enum que representa os números dos bancos (161, 413, 436, 655). |
| `TipoContaCorrenteEnum` | Enum que representa os tipos de conta corrente (CC, PG, CI, IF, PP, CO, CT). |
| `RestExceptionMapper` | Mapeador de exceções REST para tratamento de erros. |

---

## 3. Tecnologias Utilizadas

- **Java EE 7** (EJB 3.1, JAX-RS, CDI)
- **Maven** (gerenciamento de dependências e build)
- **IBM WebSphere Application Server** (servidor de aplicação)
- **Spring JDBC** (acesso a dados via JDBC Template)
- **Oracle Database** (banco de dados relacional)
- **Gson** (serialização/deserialização JSON)
- **SLF4J / Log4j** (logging)
- **JUnit, Mockito, PowerMock** (testes unitários)
- **Swagger** (documentação de APIs REST)
- **Apache Commons Lang3** (utilitários)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/spag-base-pagamento-tributo-rs/v1/atacado/pagamentos/incluirPagamento` | `SolicitarPagamentoTributo` | Recebe uma solicitação de pagamento de tributo em JSON e retorna o protocolo e status da solicitação. |

---

## 5. Principais Regras de Negócio

1. **Validação de Campos Obrigatórios**: Verifica se campos essenciais da solicitação (CNPJ, agência, nome, conta, data, tipo de conta, linha digitável, data de vencimento, tipo de lançamento) estão preenchidos. Caso contrário, lança exceção.

2. **Tratamento de Número de Banco**: Substitui o número do banco 655 por 161 e o 413 por 436, conforme regras de negócio específicas.

3. **Determinação do Código de Liquidação**: Com base no segundo dígito da linha digitável, define o código de liquidação (59 ou 60).

4. **Fluxo Fintech (Conta Pagamento - PG)**: Quando o tipo de conta é "PG", o sistema consulta a tabela `TbValidacaoOrigemPagamento` para obter dados da fintech (parceiro comercial) e substitui os dados do remetente pelos dados da fintech. Valida se a conta do usuário está vinculada à fintech.

5. **Validação de Protocolo de Solicitação Cliente**: Verifica se já existe uma solicitação em processamento com o mesmo protocolo de cliente e CPF/CNPJ do remetente, evitando duplicidade.

6. **Registro de Lançamento**: Chama a stored procedure `PrSolicitaPagamentoTributos` para registrar o lançamento de pagamento de tributo no banco de dados, retornando um protocolo único.

7. **Tratamento de Exceções**: Em caso de erro, retorna um objeto `SolicitacaoRetorno` com código de status "99" e mensagem de erro.

---

## 6. Relação entre Entidades

- **Solicitacao**: Contém dados da solicitação de pagamento (remetente, valores, tributo, conta).
- **SolicitacaoRetorno**: Retorna protocolo e status da solicitação.
- **ValidacaoOrigemPagamentoDTO**: Armazena dados de validação de fintech (parceiro comercial, cliente, conta).
- **Agencia**: Representa dados de agência bancária.
- **ContaCorrente**: Representa dados de conta corrente (número, dígito, agência).
- **ListaContaCorrente**: Lista de contas correntes associadas.
- **ValidaProtocoloSolicitacaoCliente**: Entidade para validação de protocolo de solicitação do cliente.

**Relacionamentos**:
- `Solicitacao` possui uma `ListaContaCorrente`.
- `ContaCorrente` possui uma `Agencia`.
- `ValidacaoOrigemPagamentoDTO` é consultado a partir de dados da `Solicitacao` (tipo de conta PG).

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| `TbValidacaoOrigemPagamento` | Tabela | SELECT | Consulta cadastro de fintechs (parceiros comerciais) para validação de origem de pagamento. |
| `tbparametropagamentofintech` | Tabela | SELECT | Consulta parâmetros de pagamento de fintech. |
| `tbcontapagamentofintech` | Tabela | SELECT | Consulta contas de pagamento de fintech. |
| `tbcontausuariofintech` | Tabela | SELECT | Consulta contas de usuários de fintech. |
| `tbusuariocontafintech` | Tabela | SELECT | Consulta usuários de fintech. |
| `tbrelacaocontausuariofintech` | Tabela | SELECT | Consulta relacionamento entre contas e usuários de fintech. |
| `TbLancamento` | Tabela | SELECT | Consulta lançamentos para validação de protocolo de solicitação cliente. |
| `TbLancamentoPessoa` | Tabela | SELECT | Consulta dados de pessoa associados a lançamentos. |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| `TbLancamento` | Tabela | INSERT | Insere registro de lançamento de pagamento de tributo via stored procedure `PrSolicitaPagamentoTributos`. |
| `TbLancamentoPessoa` | Tabela | INSERT | Insere dados de pessoa (remetente) associados ao lançamento via stored procedure. |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `SolicitacaoLancamentoTributoDAOImpl-sql.xml` | Leitura | `SolicitacaoLancamentoTributoDAOImpl` | Arquivo XML contendo queries SQL (não utilizado diretamente, pois a implementação usa stored procedure). |
| `ValidacaoOrigemPagamentoDAOImpl-sql.xml` | Leitura | `ValidacaoOrigemPagamentoDAOImpl` | Arquivo XML contendo queries SQL para consultas de validação de origem de pagamento e protocolo de cliente. |
| `errorMessages.properties` | Leitura | Commons | Arquivo de propriedades com mensagens de erro do sistema. |
| `roles.properties` | Leitura | Commons | Arquivo de propriedades com definição de roles de segurança. |

---

## 10. Filas Lidas

Não se aplica.

---

## 11. Filas Geradas

Não se aplica.

---

## 12. Integrações Externas

Não se aplica. O sistema não integra diretamente com APIs externas ou serviços de terceiros. Toda a comunicação é feita via banco de dados Oracle.

---

## 13. Avaliação da Qualidade do Código

**Nota:** 6/10

**Justificativa:**

**Pontos Positivos:**
- Estrutura modular bem definida (separação em camadas: domain, persistence, business, rs).
- Uso de padrões Java EE (EJB, CDI, JAX-RS).
- Presença de testes unitários (JUnit, Mockito, PowerMock).
- Uso de enums para representar tipos de conta e bancos, melhorando legibilidade.
- Tratamento de exceções com retorno estruturado.

**Pontos Negativos:**
- **Mistura de responsabilidades**: A classe `SolicitacaoPagamentoTributoBean` contém lógica de validação, transformação de dados e chamada de DAO, tornando-a extensa e de difícil manutenção.
- **Código procedural**: Métodos longos com múltiplos `if/else` e `switch/case`, dificultando leitura e manutenção.
- **Falta de documentação**: Ausência de JavaDoc em métodos críticos.
- **Hardcoded values**: Valores como "0001" (agência), "J" (tipo pessoa), códigos de transação e filial estão hardcoded, reduzindo flexibilidade.
- **Tratamento de exceções genérico**: Captura de `Exception` genérica, dificultando diagnóstico de problemas.
- **Uso de reflection desnecessário**: No método `validaCamposSolicitacao`, usa reflection para validar campos, quando poderia usar getters diretamente.
- **Nomenclatura inconsistente**: Algumas variáveis e métodos possuem nomes pouco descritivos (ex: `filNuSProtSolicCli`).
- **Dependência de stored procedure**: Lógica de negócio crítica está na stored procedure, dificultando testes e manutenção.

---

## 14. Observações Relevantes

- O sistema suporta dois fluxos principais: **fluxo tradicional** (conta corrente) e **fluxo fintech** (conta de pagamento - PG).
- No fluxo fintech, os dados do remetente são substituídos pelos dados da fintech (parceiro comercial) cadastrada na tabela `TbValidacaoOrigemPagamento`.
- A validação de protocolo de solicitação cliente evita duplicidade de solicitações em processamento no mesmo dia.
- O sistema utiliza IBM WebSphere Application Server e requer configuração de datasources JNDI (`jdbc/spagBaseDBSPAGDS`).
- A aplicação está configurada para autenticação BASIC e utiliza roles de segurança (`spag-integracao`, `intr-middleware`).
- A documentação Swagger está configurada para as APIs REST, facilitando integração.
- O projeto utiliza Maven multi-módulo, facilitando organização e build.
- Há configurações específicas para deployment no WebSphere (arquivos `ibm-*.xml`).