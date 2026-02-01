# Ficha Técnica do Sistema

---

## 1. Descrição Geral

O sistema **java-pgft-base-dda-cliente-atacado** é uma aplicação Java EE voltada para o gerenciamento de clientes DDA (Débito Direto Autorizado) no segmento atacado. Ele oferece funcionalidades para inclusão, alteração, exclusão, confirmação e consulta de clientes DDA, além de permitir a rejeição de títulos DDA. O sistema expõe suas funcionalidades através de Web Services SOAP e interage com um banco de dados via stored procedures. A aplicação segue uma arquitetura em camadas (business, persistence, domain, ws) e é empacotada como um EAR (Enterprise Archive) para deploy em servidores de aplicação compatíveis com Java EE (especificamente IBM WebSphere).

---

## 2. Principais Classes e Responsabilidades

| Classe/Interface | Responsabilidade |
|------------------|------------------|
| **ClienteDdaBeanImpl** | EJB Stateless que implementa a lógica de negócio para operações de cliente DDA (gravar, excluir, confirmar, listar). |
| **ClienteDdaBeanLocal** | Interface local do EJB de negócio para cliente DDA. |
| **TituloDdaBeanImpl** | EJB Stateless que implementa a lógica de negócio para operações de título DDA (rejeitar). |
| **TituloDdaBeanLocal** | Interface local do EJB de negócio para título DDA. |
| **ClienteDdaDaoImpl** | DAO (Data Access Object) que gerencia a persistência de dados de cliente DDA via JDBC e stored procedures. |
| **ClienteDdaDaoLocal** | Interface local do DAO de cliente DDA. |
| **TituloDdaDaoImpl** | DAO que gerencia a persistência de dados de título DDA via JDBC e stored procedures. |
| **TituloDdaDaoLocal** | Interface local do DAO de título DDA. |
| **DdaClienteAtacadoEndPoint** | Endpoint do Web Service SOAP que expõe as operações de cliente e título DDA. |
| **InclusaoClienteDdaVO** | Value Object que representa os dados de inclusão de cliente DDA. |
| **ExclusaoClienteDdaVO** | Value Object que representa os dados de exclusão de cliente DDA. |
| **ConsultaClienteDdaVO** | Value Object que representa os dados de consulta de cliente DDA. |
| **RetornoPadraoDdaVO** | Value Object que representa o retorno padrão de operações DDA. |
| **GravarClienteDdaStoredProcedure** | Classe que encapsula a chamada à stored procedure de gravação de cliente DDA. |
| **ExcluirClienteDdaStoredProcedure** | Classe que encapsula a chamada à stored procedure de exclusão de cliente DDA. |
| **ConfirmarClienteDdaStoredProcedure** | Classe que encapsula a chamada à stored procedure de confirmação de cliente DDA. |
| **ListarClienteDdaStoredProcedure** | Classe que encapsula a chamada à stored procedure de listagem de cliente DDA. |
| **RejeitarTituloDdaStoredProcedure** | Classe que encapsula a chamada à stored procedure de rejeição de título DDA. |
| **Mappers (diversos)** | Classes responsáveis por mapear ResultSets JDBC para Value Objects. |

---

## 3. Tecnologias Utilizadas

- **Java EE 6/7** (EJB 3.1, JAX-WS, CDI, JNDI)
- **Maven** (gerenciamento de dependências e build)
- **Spring JDBC** (para acesso a dados via JDBC e stored procedures)
- **IBM WebSphere Application Server** (servidor de aplicação alvo)
- **SOAP Web Services** (JAX-WS)
- **Oracle Database** (inferido pelo driver oracle-ojdbc6 e sintaxe de stored procedures)
- **SLF4J / Log4j2** (logging)
- **JUnit, PowerMock, Mockito, EasyMock** (testes unitários)
- **JAXB** (binding XML/Java)

---

## 4. Principais Endpoints REST

**Não se aplica.** O sistema utiliza Web Services SOAP (JAX-WS), não REST.

---

## 5. Principais Regras de Negócio

- **Inclusão de Cliente DDA**: Permite cadastrar um novo cliente DDA informando CPF/CNPJ ou código do cliente, e-mail, operadora telefônica, concordância com condições gerais e autorização por arquivo. Retorna dados de controle e identificação do cliente no sistema DDA.
- **Alteração de Cliente DDA**: Permite atualizar informações de e-mail, SMS, condições gerais e indicador de arquivo de varredura de um cliente DDA já cadastrado.
- **Exclusão de Cliente DDA**: Remove o cadastro de um cliente DDA do sistema, retornando dados de controle da operação.
- **Confirmação de Cliente DDA**: Grava dados de confirmação de cliente DDA recebidos de sistemas externos (CIP), incluindo códigos de identificação, referência e controle.
- **Listagem de Cliente DDA**: Consulta informações de clientes DDA cadastrados por CPF/CNPJ ou código do cliente.
- **Rejeição de Título DDA**: Altera a situação de um título DDA para rejeitado, com base no código de barras.
- **Validação de Dados**: O sistema valida a presença de informações obrigatórias e formatos de dados (ex: CPF/CNPJ, e-mail, telefone).
- **Controle de Transações**: As operações de negócio são executadas com controle transacional (NOT_SUPPORTED), delegando o controle de transação para a camada de persistência.
- **Segurança**: Utiliza roles de segurança (intr-middleware) para controle de acesso aos EJBs e Web Services.

---

## 6. Relação entre Entidades

- **BaseClienteDdaVO**: Entidade base que contém atributos comuns de cliente DDA (código de mensagem, número de controle, ISPB, tipo de pessoa, CPF/CNPJ, identificadores, data de movimento).
- **InclusaoClienteDdaVO**: Estende BaseClienteDdaVO e adiciona lista de contas do cliente e indicador de adesão.
- **ExclusaoClienteDdaVO**: Estende BaseClienteDdaVO, utilizada para representar dados de exclusão.
- **ConsultaClienteDdaVO**: Entidade independente que representa dados de consulta de cliente DDA (datas de adesão/cancelamento, CPF/CNPJ, código, e-mail, SMS, operadora, condições gerais, arquivo de varredura).
- **InclusaoClienteDdaContaVO**: Representa uma conta associada a um cliente DDA (tipo de agência, agência, tipo de conta, conta, data de adesão).
- **RetornoPadraoDdaVO**: Entidade simples com código e mensagem de retorno.
- **BaseTituloDdaVO**: Entidade base para título DDA (atualmente sem atributos específicos).
- **RejeitarTituloDdaVO**: Estende BaseTituloDdaVO, utilizada para representar dados de rejeição de título.

**Relacionamentos**:
- InclusaoClienteDdaVO possui uma lista de InclusaoClienteDdaContaVO (1:N).
- As demais entidades são independentes e utilizadas para transferência de dados entre camadas.

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| **DBPGF_TES..PrListarClienteDDA** | Stored Procedure | SELECT/READ | Consulta informações de clientes DDA cadastrados por código ou CPF/CNPJ. |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| **DBPGF_TES..PrIncluirAlterarClienteDDA** | Stored Procedure | INSERT/UPDATE | Inclui ou altera dados de cliente DDA no banco de dados. |
| **DBPGF_TES..PrExcluirClienteDDA** | Stored Procedure | DELETE | Exclui um cliente DDA do banco de dados. |
| **DBPGF_TES..PrConfirmarClienteDDA** | Stored Procedure | UPDATE | Atualiza dados de confirmação de cliente DDA recebidos de sistemas externos. |
| **DBPGF_TES..PrAlterarSituacaoTituloDDA** | Stored Procedure | UPDATE | Altera a situação de um título DDA (ex: para rejeitado). |

---

## 9. Arquivos Lidos e Gravados

**Não se aplica.** Não foram identificados arquivos de entrada/saída processados diretamente pelo sistema nos códigos analisados. O sistema opera principalmente via Web Services e banco de dados.

---

## 10. Filas Lidas

**Não se aplica.** Não foram identificadas filas (JMS, Kafka, RabbitMQ) das quais o sistema consome mensagens.

---

## 11. Filas Geradas

**Não se aplica.** Não foram identificadas filas para as quais o sistema publica mensagens.

---

## 12. Integrações Externas

- **CIP (Câmara Interbancária de Pagamentos)**: O sistema recebe dados de confirmação de cliente DDA de sistemas externos (provavelmente via integração com a CIP), incluindo códigos de identificação, referência e controle. Esses dados são processados pela operação `confirmarClienteDDA`.
- **Banco de Dados Oracle (DBPGF_TES)**: Integração via JDBC e stored procedures para persistência de dados de clientes e títulos DDA. O DataSource utilizado é `jdbc/PgftCobrancaDDADS`.
- **Sistemas Consumidores do Web Service**: O sistema expõe um Web Service SOAP que pode ser consumido por outros sistemas internos ou externos para gerenciar clientes e títulos DDA.

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- **Arquitetura em Camadas**: O código segue uma arquitetura bem definida em camadas (business, persistence, domain, ws), facilitando a manutenção e evolução.
- **Uso de Padrões Java EE**: Utiliza EJBs, CDI, JAX-WS e outros padrões Java EE de forma adequada.
- **Separação de Responsabilidades**: As classes têm responsabilidades bem definidas (DAOs para persistência, Beans para lógica de negócio, Endpoints para exposição de serviços).
- **Uso de Stored Procedures**: A utilização de stored procedures encapsuladas em classes específicas facilita a manutenção e reutilização.
- **Mappers**: O uso de mappers para conversão de ResultSets em VOs é uma boa prática.
- **Documentação**: Há comentários JavaDoc em algumas classes e interfaces, embora não seja completo.

**Pontos Negativos:**
- **Tratamento de Exceções Genérico**: O tratamento de exceções é muito genérico (catch Exception), dificultando a identificação de problemas específicos e a tomada de decisões adequadas.
- **Falta de Validações Robustas**: Não há validações robustas de entrada de dados (ex: validação de CPF/CNPJ, e-mail, telefone) na camada de negócio ou endpoint.
- **Código Comentado**: Há código comentado em algumas classes (ex: `ClienteDdaBeanImpl`, `DdaClienteAtacadoEndPoint`), o que pode indicar falta de clareza ou código legado.
- **Falta de Testes Unitários Implementados**: Embora haja estrutura para testes, os arquivos de teste não foram enviados completos, impossibilitando avaliar a cobertura de testes.
- **Logging Insuficiente**: O logging é básico, apenas registrando erros. Faltam logs de auditoria e rastreamento de operações importantes.
- **Hardcoded Strings**: Há strings hardcoded em vários pontos do código (ex: nomes de stored procedures, mensagens de erro), dificultando a internacionalização e manutenção.
- **Falta de Constantes**: Valores como "S", "N", "F", "J" poderiam ser definidos como constantes para melhorar a legibilidade e manutenibilidade.
- **Complexidade no Endpoint**: A classe `DdaClienteAtacadoEndPoint` possui métodos longos e com lógica de transformação de dados que poderia ser extraída para classes auxiliares.

---

## 14. Observações Relevantes

- **Ambiente de Deploy**: O sistema é projetado para deploy em IBM WebSphere Application Server, conforme indicado pelos arquivos de configuração (ibm-ejb-jar-bnd.xml, ibm-web-bnd.xml, ibm-web-ext.xml, deployment.xml).
- **Segurança**: O sistema utiliza WS-Security (UsernameToken e Certificate) para autenticação e autorização de Web Services, conforme configurado nos arquivos de policy attachments.
- **Trilha de Auditoria**: O sistema possui handlers para captura de trilha de auditoria (CapturadorTrilhaInbound, InicializadorContextoRequisicao), indicando preocupação com rastreabilidade de operações.
- **Versionamento**: O sistema possui versionamento de API (v1), facilitando a evolução e manutenção de compatibilidade.
- **Dependências Externas**: O sistema depende de bibliotecas externas (arqt-base-lib, fjee-base-lib) que não foram fornecidas, mas são referenciadas no deployment.xml.
- **Banco de Dados**: O sistema utiliza um DataSource JNDI (`jdbc/PgftCobrancaDDADS`) para acesso ao banco de dados, que deve ser configurado no servidor de aplicação.
- **Stored Procedures**: Todas as operações de banco de dados são realizadas via stored procedures, o que pode indicar uma arquitetura legada ou requisitos específicos de performance/segurança.
- **Adaptador de Data**: O sistema utiliza um adaptador customizado (DateAdapter) para conversão de datas entre XML e Java, garantindo formato consistente.

---