# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **SITP Base WebService** é uma aplicação Java EE que fornece serviços de gestão de pagamentos e transferências financeiras. Implementado como um webservice SOAP, o sistema recebe solicitações de transações financeiras entre contas (mesma instituição ou instituições diferentes), valida as informações, registra os dados em banco de dados Oracle através de stored procedures e retorna um protocolo de confirmação. A aplicação é executada no IBM WebSphere Application Server (WAS) e segue uma arquitetura modular baseada em EJB, JAX-WS e Spring JDBC.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `GestaoPagamentoBusinessServiceImpl` | Implementação do webservice SOAP que expõe a operação `inserirTransacao`. Valida dados de entrada, orquestra chamadas ao EJB de negócio e trata exceções. |
| `GestaoPagamentoBeanImpl` | EJB Singleton que implementa a lógica de negócio para inclusão de lançamentos assíncronos de transferências. |
| `GestaoPagamentoBeanLocal` | Interface local do EJB de negócio. |
| `GestaoPagamentoDaoImpl` | Implementação do DAO responsável por executar a stored procedure de inclusão de transferências no banco de dados. |
| `GestaoPagamentoDao` | Interface do DAO. |
| `TransferenciaAssincronaStoredProcedure` | Classe que encapsula a chamada à stored procedure `BV_INCLUSAO_CAIXA_ENTRADA` usando Spring JDBC. |
| `Transferencia` | Entidade de domínio que representa uma transferência financeira com todos os seus atributos (remetente, favorecido, valores, datas, etc). |
| `TransferenciaRetorno` | Entidade que representa o retorno da stored procedure com código de retorno, protocolo e informações de erro. |
| `TransferenciaMapper` | RowMapper do Spring JDBC para mapeamento de resultados (implementação vazia no código fornecido). |
| `TransferenciaRetornoMapper` | RowMapper para mapear o retorno da stored procedure. |
| `BaseAppConfig`, `SecurityAppConfig`, `UtilsAppConfig` | Classes de configuração JAX-RS para APIs REST (módulo RS). |
| `RestExceptionMapper` | Mapeador de exceções para endpoints REST. |

---

## 3. Tecnologias Utilizadas

- **Java EE 6/7** (EJB 3.1, JAX-WS 2.1, JAX-RS, JMS, JPA, CDI)
- **IBM WebSphere Application Server (WAS)** - Servidor de aplicação
- **Maven** - Gerenciamento de dependências e build (estrutura multi-módulo)
- **Spring JDBC** - Acesso a dados e execução de stored procedures
- **Oracle Database** - Banco de dados (driver OJDBC6)
- **Log4j2** - Framework de logging
- **Swagger** - Documentação de APIs REST
- **Apache Commons Lang3** - Utilitários
- **Joda-Time** - Manipulação de datas
- **Google Guava e Gson** - Utilitários e serialização JSON
- **JUnit, Mockito, PowerMock** - Testes unitários

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| N/A | `/sitp-base-webservice-was-rs/api` | `BaseAppConfig` | Configuração base para APIs REST do sistema |
| N/A | `/sitp-base-webservice-was-rs/api-security` | `SecurityAppConfig` | APIs de segurança e OAuth (delegadas para `SecurityRestApi` e `OauthRestApi`) |
| N/A | `/sitp-base-webservice-was-rs/api-utils` | `UtilsAppConfig` | APIs utilitárias de arquitetura (log) |

**Observação:** O sistema é primariamente um webservice SOAP. Os endpoints REST são para funcionalidades auxiliares de arquitetura (segurança, log). Não há endpoints REST de negócio implementados no código fornecido.

---

## 5. Principais Regras de Negócio

1. **Validação de Trilha de Auditoria**: Todas as operações exigem informações de auditoria (login do usuário final) no header SOAP.

2. **Validação de Dados Obrigatórios**: Remetente, favorecido, finalidade, filial, tipo de lançamento, data de movimento, valor, código de tipo de transação, sistema de origem, forma de liquidação e titularidade são obrigatórios.

3. **Formatação de Contas e Agências**: O sistema formata automaticamente números de conta e agência com seus dígitos verificadores quando presentes.

4. **Controle de Lançamento Manual**: Flag `flLancamentoManual` é sempre definida como "N" (não manual).

5. **Controle de Terceiros**: Flag `indTerceiro` é sempre definida como "N".

6. **Data de Lançamento**: Sempre definida como a data atual do sistema.

7. **Protocolo de Retorno**: Após inclusão bem-sucedida, retorna um protocolo com status "OK" e número do protocolo gerado.

8. **Tratamento de Erros**: Erros de negócio (código de retorno diferente de 1) e erros sistêmicos são tratados e retornados como SOAP Faults com detalhamento.

9. **Baixa Automática de Previsão**: Se informado protocolo de gestão de caixa, o sistema efetua baixa automática da previsão.

10. **Suporte a Múltiplos Tipos de Transação**: Suporta diversos tipos incluindo boletos, DARF, GPS, portabilidade de crédito, etc.

---

## 6. Relação entre Entidades

**Transferencia** (entidade principal)
- Contém dados do **Remetente** (pessoa + conta + banco)
- Contém dados do **Favorecido** (pessoa + conta + banco)
- Relaciona-se com **Filial** (código da filial)
- Relaciona-se com **Sistema de Origem** (sigla e código)
- Possui **Finalidade** (código e tipo)
- Possui **Protocolo** (número e status)
- Possui múltiplas datas (agendamento, movimento, lançamento, vencimento, referência)
- Possui valores diversos (principal, multa, juros, descontos, etc)

**TransferenciaRetorno**
- Retorna código de retorno (sucesso/erro)
- Retorna número do protocolo (em caso de sucesso)
- Retorna código e descrição de erro (em caso de falha)
- Contém dados do cliente debitado e creditado
- Contém dados complementares da transação

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| não se aplica | - | - | O sistema não realiza operações de leitura direta em tabelas. Toda interação é via stored procedure. |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| BV_INCLUSAO_CAIXA_ENTRADA | Stored Procedure | EXECUTE | Procedure responsável por incluir lançamentos de transferência no sistema ITP (Integração de Tesouraria e Pagamentos). Recebe 103 parâmetros incluindo dados de remetente, favorecido, valores, datas, tributos, boletos, etc. |

**Observação:** As tabelas específicas alteradas pela stored procedure não são visíveis no código da aplicação, pois a lógica de persistência está encapsulada dentro da procedure `BV_INCLUSAO_CAIXA_ENTRADA`.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `errorMessages.properties` | Leitura | `commons/src/main/resources` | Arquivo de mensagens de erro do sistema |
| `roles.properties` | Leitura | `commons/src/main/resources` | Lista de roles de segurança da aplicação |
| `log4j2.xml` | Leitura | Diversos módulos | Configuração do framework de logging |
| `GestaoPagamentoDaoImpl-sql.xml` | Leitura | `persistence/src/main/resources` | Arquivo XML para queries SQL (vazio no código fornecido) |
| Arquivos WSDL/XSD | Leitura | `ws/src/main/webapp/WEB-INF/wsdl/gestaoPagamento` | Contratos de serviço e schemas XML do webservice |

---

## 10. Filas Lidas

não se aplica

**Observação:** Embora exista um módulo JMS no projeto (`java-sitp-base-webservice-was-jms`), não há código de implementação de MDBs (Message Driven Beans) nos arquivos fornecidos.

---

## 11. Filas Geradas

não se aplica

**Observação:** Não há evidências no código fornecido de publicação de mensagens em filas JMS.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Oracle Database (ITP) | Banco de Dados | Integração via stored procedure `BV_INCLUSAO_CAIXA_ENTRADA` para registro de transações financeiras no sistema ITP |
| DataSource JNDI | Recurso WAS | `jdbc/sitpBaseDbItpDS` - DataSource configurado no WebSphere para acesso ao banco Oracle |

**Observação:** O sistema é primariamente um provedor de serviços (webservice SOAP), não um consumidor. Não há evidências de chamadas a webservices externos no código fornecido.

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura modular bem definida (separação em camadas: domain, business, persistence, ws, rs)
- Uso adequado de padrões Java EE (EJB, JAX-WS, CDI)
- Tratamento de exceções estruturado com SOAP Faults
- Uso de injeção de dependências
- Separação de responsabilidades entre camadas

**Pontos Negativos:**
- **Classe `GestaoPagamentoBusinessServiceImpl` muito extensa** (mais de 500 linhas) com lógica de validação e mapeamento misturada
- **Método `inserirTransacao` extremamente longo** (mais de 200 linhas) violando princípios de clean code
- **Classe `GestaoPagamentoDaoImpl` com método de mais de 150 linhas** apenas para mapear parâmetros
- **Falta de documentação JavaDoc** na maioria das classes
- **Código comentado** deixado no fonte (`getObjDao()`)
- **Validadores em classe interna estática** (`Validadores`) sem coesão clara
- **Mappers vazios** (`TransferenciaMapper`) indicando código incompleto ou não utilizado
- **Falta de testes unitários** (apenas estrutura de diretórios de teste)
- **Acoplamento forte com stored procedure** (103 parâmetros) dificulta manutenção
- **Uso de `String.format` excessivo** para formatação de contas/agências
- **Tratamento de exceções genérico** em alguns pontos
- **Falta de constantes** para valores literais repetidos

**Recomendações:**
- Refatorar métodos longos em métodos menores e mais coesos
- Extrair validações para classes de serviço específicas
- Implementar padrão Builder para construção de objetos complexos
- Adicionar documentação JavaDoc
- Implementar testes unitários
- Considerar uso de frameworks de mapeamento (MapStruct, ModelMapper)
- Revisar necessidade de todos os 103 parâmetros da stored procedure

---

## 14. Observações Relevantes

1. **Versão do Sistema**: 16.6.3.2-SNAPSHOT (em desenvolvimento)

2. **Segurança**: O sistema utiliza autenticação BASIC e role-based access control com a role `sitp.pagamento` definida no EJB.

3. **Handlers SOAP**: Implementa handlers customizados para trilha de auditoria, captura de requisições e tratamento de falhas.

4. **Arquitetura Multi-Módulo**: O projeto está organizado em 9 módulos Maven (commons, domain, persistence, integration, business, jms, ws, rs, ear).

5. **Dependências de Arquitetura**: O sistema depende de bibliotecas corporativas (`fjee-base-commons`, `arqt-base-lib`) que fornecem funcionalidades comuns de arquitetura.

6. **Configuração WAS**: Utiliza arquivos de configuração específicos do WebSphere (ibm-ejb-jar-bnd.xml, ibm-web-bnd.xml, ibm-web-ext.xml).

7. **Policy Attachments**: Configurado para usar políticas de segurança WS-Security com diferentes níveis (Low, Medium, High) através de Username Token e Certificate.

8. **ClassLoader**: Configurado com modo PARENT_LAST para isolamento de bibliotecas.

9. **Shared Libraries**: Utiliza bibliotecas compartilhadas do WAS (arqt-base-lib-1.0, fjee-base-lib-1.0).

10. **Swagger**: Configurado para documentação de APIs REST, embora o foco principal seja SOAP.

11. **Stored Procedure Complexa**: A procedure `BV_INCLUSAO_CAIXA_ENTRADA` aceita 103 parâmetros, indicando alta complexidade de negócio encapsulada no banco de dados.

12. **Suporte a Diversos Tipos de Pagamento**: Boletos, DARF, GPS, TED, DOC, portabilidade de crédito consignado, entre outros.