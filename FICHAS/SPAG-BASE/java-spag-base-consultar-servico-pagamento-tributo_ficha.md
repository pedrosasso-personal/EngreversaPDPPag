# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **java-spag-base-consultar-servico-pagamento-tributo** é um componente Java EE responsável por consultar e validar serviços de pagamento de tributos. Ele atua como intermediário entre sistemas internos do Banco Votorantim e o parceiro IS2B, realizando validações de negócio (datas, valores, horários) antes de encaminhar as solicitações de pagamento. O sistema verifica fornecedores cadastrados, valida limites, datas úteis e regras específicas de pagamento de tributos via código de barras.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `ConsultarServicoPagamentoTributoBean` | EJB Stateless que orquestra a lógica de negócio principal: consulta fornecedor, valida dados, chama IS2B e trata retornos |
| `ConsultarServicoPagamentoTributo` (REST) | Endpoint REST que expõe o serviço de consulta de pagamento de tributos |
| `FornecedorDAOImpl` | DAO para consulta de fornecedores de pagamento de tributos no banco de dados |
| `ObterDataUtilDAOImpl` | DAO para obtenção de datas úteis via stored procedures |
| `ConsultarServicoIntegrationServices` | Serviço de integração HTTP com a API do parceiro IS2B |
| `HttpCaapiIntegration` | Classe abstrata base para chamadas HTTP à CA-API |
| `Fornecedor` | Entidade de domínio representando fornecedor de serviço de pagamento |
| `RetornosIS2BEnum` | Enum com códigos de retorno da IS2B e mapeamento de erros |
| `NumeroBanco` | Enum com códigos de bancos (BVSA=413, Banco Votorantim=655) |

---

## 3. Tecnologias Utilizadas

- **Java EE 7** (EJB 3.1, JAX-RS, CDI)
- **IBM WebSphere Application Server** (WAS)
- **Maven** (gerenciamento de dependências e build)
- **Spring JDBC** (acesso a dados)
- **Oracle Database** (banco de dados principal)
- **Apache HttpClient** (integração HTTP)
- **Gson** (serialização/deserialização JSON)
- **SLF4J/Log4j2** (logging)
- **JUnit, Mockito, PowerMock** (testes)
- **Swagger** (documentação de APIs REST)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/atacado/pagamentos/consultarServPagamentoTributo` | `ConsultarServicoPagamentoTributo` | Consulta e valida serviço de pagamento de tributo |

**Context Root:** `/spag-base-consultar-servico-pagamento-tributo-rs/v1`

---

## 5. Principais Regras de Negócio

1. **Validação de Fornecedor**: Verifica se existe fornecedor cadastrado (IS2B) para o banco remetente e parâmetro de pagamento
2. **Configuração de Conta Favorecido**: Define conta do favorecido conforme banco remetente (BVSA usa banco 436, Votorantim usa 161)
3. **Validação de Data de Vencimento**: Não permite pagamento se data de vencimento for anterior à data de movimento
4. **Validação de Data de Agendamento**: Verifica se data de agendamento é dia útil e não ultrapassa vencimento
5. **Validação de Horário**: Pagamentos com grade horária 16:00 devem ser feitos até 15:45
6. **Validação de Valor**: Verifica se valor está entre mínimo e máximo aceito pela IS2B e não excede limite do fornecedor
7. **Tratamento de Retornos IS2B**: Mapeia códigos de erro da IS2B para ações (tentar novamente, outro parceiro, finalizar)
8. **Retry Automático**: Tenta novamente em caso de falha de comunicação (máximo 2 tentativas)
9. **Conversão de Tipo de Conta**: Mapeia tipos de conta (CI, IF, PP, CO, CC, CT, PG) para códigos numéricos

---

## 6. Relação entre Entidades

**Fornecedor**
- Representa empresa prestadora de serviço de pagamento (ex: IS2B)
- Contém dados bancários do favorecido (banco, agência, conta, CPF/CNPJ)
- Possui limite de valor para pagamentos
- Relacionado a parâmetro de pagamento de tributo

**DicionarioPagamento** (biblioteca externa)
- Objeto principal que trafega entre camadas
- Contém dados do pagamento, remetente, favorecido, tributo
- Inclui lista de ocorrências/erros

**TributoDTO** (biblioteca externa)
- Dados específicos do tributo a ser pago
- Contém código de erro, mensagem, valores, datas

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbParametroPagamentoTributo | Tabela | SELECT | Parâmetros de pagamento de tributo |
| TbContaFornecedorTributo | Tabela | SELECT | Contas de fornecedores para pagamento de tributo |
| (Stored Procedure) prRetornaDataUtil | Procedure | CALL | Retorna data útil para uma data e praça |
| (Stored Procedure) PrProximoDiaUtil | Procedure | CALL | Retorna próximo dia útil para uma data e praça |

**DataSources utilizados:**
- `jdbc/spagBaseDBSPAGDS` (banco SPAG)
- `jdbc/globBaseDbGlobalDS` (banco Global para datas úteis)

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema realiza apenas consultas (SELECT/READ), não há operações de INSERT/UPDATE/DELETE.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| config-arqt-base.properties | Leitura | `ConfigArqtrBaseProperties` | Configurações de URLs de webservices e API Gateway |
| config-spag.properties | Leitura | `ConfigSpagBaseProperties` | Configurações específicas do SPAG (servidor WAS, URIs) |
| errorMessages.properties | Leitura | Commons | Mensagens de erro do sistema |
| roles.properties | Leitura | Commons | Definição de roles de segurança |
| FornecedorDAOImpl-sql.xml | Leitura | `FornecedorDAOImpl` | Queries SQL para consulta de fornecedores |
| log4j2.xml | Leitura | Diversos | Configuração de logging |

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas JMS, Kafka ou RabbitMQ.

---

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| IS2B (via API interna) | REST/HTTP | Parceiro para consulta e efetivação de pagamentos de tributos. Chamado via `ConsultarServicoIntegrationServices` |
| java-spag-base-consultar-pagamento-tributo-consumo | EJB Remoto | Componente interno que encapsula chamadas à IS2B. Lookup: `ejb/spag-base/ConsultarPagamentoTributoBean` |
| CA-API (API Gateway) | REST/HTTP | Gateway de integração corporativo do Banco Votorantim |

**URL Base (configurável):** `https://appbvdes.bvnet.bv/spag-base-consultar-pagamento-tributo-consumo-rs/api/tributo/consultarPagamento`

---

## 13. Avaliação da Qualidade do Código

**Nota:** 6/10

**Justificativa:**

**Pontos Positivos:**
- Separação clara de responsabilidades em camadas (business, persistence, integration, rs)
- Uso de padrões Java EE (EJB, CDI, JAX-RS)
- Tratamento estruturado de exceções com mapeamento de códigos de erro
- Testes unitários presentes com boa cobertura de mocks
- Uso de enums para constantes e códigos de retorno

**Pontos Negativos:**
- Classe `ConsultarServicoPagamentoTributoBean` muito extensa (>400 linhas) com múltiplas responsabilidades
- Strings hardcoded para mensagens de erro ao invés de usar arquivo de properties
- Métodos privados muito longos (ex: `executarChamadaIS2B`, `tratarErrosIS2B`)
- Lógica de negócio misturada com tratamento de erros
- Comentários de código desabilitado (código morto) em vários arquivos
- Falta de documentação JavaDoc nas classes principais
- Uso excessivo de variáveis de instância na classe Bean (deveria ser stateless de verdade)
- Conversão manual de tipos de conta poderia usar um mapper dedicado
- Dependência de biblioteca externa (`votorantim.spag.lib.datatype`) sem controle de versão aparente

---

## 14. Observações Relevantes

1. **Segurança**: Sistema protegido por autenticação BASIC e roles (`spag-integracao`, `intr-middleware`)

2. **Transações**: Operações marcadas como `NOT_SUPPORTED`, indicando que não participam de transações gerenciadas

3. **Retry Logic**: Sistema implementa retry automático em caso de falha de comunicação (máximo 2 tentativas)

4. **Ambiente**: Configurações apontam para ambiente de desenvolvimento (DES), com URLs específicas do Banco Votorantim

5. **Dependências Externas**: Sistema depende fortemente de bibliotecas internas do banco (`fjee-base`, `arqt-base`, `spag-base-pagamentos-commons`)

6. **Versionamento**: Versão atual 0.11.1, indicando que ainda está em fase de evolução

7. **Deploy**: Aplicação empacotada como EAR com múltiplos módulos (EJB, WAR REST)

8. **Banco de Dados**: Utiliza dois datasources distintos (SPAG e Global), sugerindo separação de bases de dados

9. **Logging**: Uso de SLF4J com implementação Log4j2, seguindo boas práticas de logging

10. **Código Legado**: Presença de módulos comentados (WS, JMS) sugere evolução de arquitetura SOAP para REST