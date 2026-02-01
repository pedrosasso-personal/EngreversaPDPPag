# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **java-pgft-base-dda-beneficiario-atacado** é um serviço backend desenvolvido em Java EE para gerenciamento de beneficiários DDA (Débito Direto Autorizado) no contexto de clientes atacado do Banco Votorantim. O sistema expõe operações via Web Services SOAP para inclusão, alteração, listagem e exclusão de beneficiários DDA, integrando-se com o banco de dados através de stored procedures. A aplicação segue uma arquitetura em camadas (WS, Business, Persistence, Domain) e é implantada em IBM WebSphere Application Server.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **DDABeneficiarioEndpoint** | Endpoint SOAP que expõe as operações de gerenciamento de beneficiários (incluir, alterar, listar, excluir) |
| **DdaBeneficiarioBeanImpl** | EJB Stateless que implementa a lógica de negócio para operações de beneficiários |
| **DdaBeneficiarioDaoImpl** | DAO que gerencia o acesso aos dados através de stored procedures |
| **ListarBeneficiarioDdaStoredProcedure** | Encapsula a chamada à stored procedure de listagem de beneficiários |
| **IncluirBeneficiarioDdaStoredProcedure** | Encapsula a chamada à stored procedure de inclusão/alteração de beneficiários |
| **ExcluirBeneficiarioDdaStoredProcedure** | Encapsula a chamada à stored procedure de exclusão de beneficiários |
| **ListaBeneficiarioDdaMapper** | RowMapper do Spring JDBC para mapear resultados de consultas em objetos BeneficiarioDdaVO |
| **BeneficiarioDdaVO** | Value Object que representa um beneficiário DDA |
| **BaseClienteDdaVO** | Value Object base com informações comuns de cliente DDA |

---

## 3. Tecnologias Utilizadas

- **Java EE 6** (EJB 3.1, JAX-WS, CDI)
- **IBM WebSphere Application Server** (servidor de aplicação)
- **Spring JDBC** (acesso a dados via stored procedures)
- **Maven** (gerenciamento de dependências e build)
- **JAX-WS** (Web Services SOAP)
- **Log4j2 / SLF4J** (logging)
- **JUnit, PowerMock, Mockito** (testes unitários)
- **Oracle Database** (banco de dados - inferido pelo uso de ojdbc6)
- **Sybase/SQL Server** (inferido pela sintaxe das stored procedures: DBPGF_TES..)

---

## 4. Principais Endpoints REST

Não se aplica. O sistema utiliza Web Services SOAP, não REST.

**Endpoints SOAP:**

| Operação | Descrição |
|----------|-----------|
| **incluirBeneficiario** | Inclui um novo beneficiário DDA para um cliente |
| **alterarBeneficiario** | Altera os dados de um beneficiário DDA existente |
| **listarBeneficiario** | Lista beneficiários DDA de um cliente (por código, nome ou CPF/CNPJ) |
| **excluirBeneficiario** | Exclui um beneficiário DDA de um cliente |

**WSDL:** `DDABeneficiarioAtacadoBackendService_v1.wsdl`

**Namespace:** `http://votorantim.com.br/pgft/serv/ws/DDABeneficiarioAtacadoBackendService/v1`

---

## 5. Principais Regras de Negócio

1. **Inclusão/Alteração de Beneficiário**: Permite cadastrar ou atualizar informações de beneficiários DDA, incluindo nome, CPF/CNPJ, email, configurações de pagamento automático, valor limite, antecipação de pagamento e rejeição automática de boletos.

2. **Conversão de Flags**: O sistema converte valores inteiros (0/1) em flags de caractere ('N'/'S') para comunicação com as stored procedures do banco de dados.

3. **Listagem com Filtros**: Permite listar beneficiários por código de cliente, nome do beneficiário ou CPF/CNPJ, com suporte a filtros opcionais.

4. **Exclusão de Beneficiário**: Remove o vínculo de um beneficiário DDA com um cliente específico através do código do cliente e CPF/CNPJ do beneficiário.

5. **Auditoria**: Todas as operações registram o login do usuário/sistema que executou a ação (campo dsLogin).

6. **Tratamento de Exceções**: Exceções são capturadas e convertidas em BvFault padronizado com código de erro, mensagem e informações de origem.

---

## 6. Relação entre Entidades

**Entidades principais:**

- **BeneficiarioDdaVO**: Representa um beneficiário DDA com atributos como CPF/CNPJ, nome completo, email, flags de pagamento automático, valor limite, antecipação e rejeição automática.

- **BaseClienteDdaVO**: Classe base que contém informações comuns de cliente DDA (código de mensagem, número de controle, ISPB, tipo de pessoa, CPF/CNPJ do pagador, data de movimento).

- **ExclusaoBeneficiarioDdaVO**: Estende BaseClienteDdaVO e adiciona informações específicas para exclusão (tipo de pessoa do beneficiário, CPF/CNPJ, indicador de manutenção).

- **RetornoPadraoDdaVO**: Objeto de retorno padronizado com código e mensagem.

**Relacionamentos:**
- ExclusaoBeneficiarioDdaVO herda de BaseClienteDdaVO
- BeneficiarioDdaVO e BaseClienteDdaVO estendem EntidadeBase (framework)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| **DBPGF_TES..PrListarBeneficiarioDDA** | Stored Procedure | SELECT/READ | Consulta beneficiários DDA por código de cliente, nome ou CPF/CNPJ |

**Observação:** O sistema acessa o banco através do DataSource `jdbc/PgftCobrancaDDADS`.

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| **DBPGF_TES..PrIncluirAlterarBeneficiarioDDA** | Stored Procedure | INSERT/UPDATE | Inclui ou altera dados de beneficiário DDA |
| **DBPGF_TES..PrExcluirBeneficiarioDDA** | Stored Procedure | DELETE | Exclui beneficiário DDA de um cliente |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| **errorMessages.properties** | Leitura | commons/src/main/resources | Arquivo de mensagens de erro do sistema |
| **roles.properties** | Leitura | commons/src/main/resources | Definição de roles de segurança da aplicação |
| **log4j2.xml** | Leitura | Diversos módulos | Configuração de logging (não incluído no EAR final) |
| **DdaBeneficiarioDAO-sql.xml** | Leitura | persistence/src/main/resources | Arquivo de queries SQL (vazio no código analisado) |

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

---

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **Banco de Dados DBPGF_TES** | JDBC/Stored Procedures | Banco de dados principal para operações de beneficiários DDA (via DataSource jdbc/PgftCobrancaDDADS) |
| **Framework FJEE Base** | Biblioteca Interna | Framework corporativo Votorantim para funcionalidades comuns (trilha de auditoria, handlers, persistência) |
| **Framework ARQT Base** | Biblioteca Interna | Framework de arquitetura base do Banco Votorantim |

**Observação:** O sistema é um backend service que expõe Web Services SOAP para consumo por outros sistemas (provavelmente frontend de Internet Banking).

---

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Arquitetura em camadas bem definida (WS, Business, Persistence, Domain)
- Uso adequado de padrões Java EE (EJB, CDI, JAX-WS)
- Separação clara de responsabilidades entre camadas
- Uso de Value Objects para transferência de dados
- Implementação de handlers para tratamento de auditoria e exceções
- Testes unitários presentes (embora não enviados completos)
- Uso de Spring JDBC para acesso a stored procedures de forma estruturada

**Pontos de Melhoria:**
- Arquivos SQL vazios (DdaBeneficiarioDAO-sql.xml) indicam possível código não utilizado
- Conversão manual de flags (0/1 para N/S) poderia ser centralizada em utilitário
- Tratamento de exceções genérico (catch Exception) em alguns pontos
- Falta de validações de entrada nos endpoints SOAP
- Documentação JavaDoc incompleta em algumas classes
- Código de tratamento de exceção repetido no endpoint (poderia ser extraído para método auxiliar ou interceptor)
- Uso de String literal "java-pgft-base-dda-beneficiario-atacado" hardcoded como login em várias operações

O código é funcional, segue padrões corporativos e está bem estruturado, mas há espaço para melhorias em validações, tratamento de erros e eliminação de código duplicado.

---

## 14. Observações Relevantes

1. **Segurança**: O sistema utiliza autenticação BASIC e role "intr-middleware" para controle de acesso aos EJBs.

2. **Políticas de Segurança WS-Security**: O sistema está configurado para usar políticas de segurança BvWsSecurityUsernameToken (classificações baixa e média) e BvWsSecurityCertificate (classificação alta).

3. **Classloader**: A aplicação utiliza classloader PARENT_LAST e referencia bibliotecas compartilhadas (arqt-base-lib, fjee-base-lib).

4. **Versionamento**: Versão atual do sistema: 18.10.4.P1883.2

5. **Ambientes**: Existem WSDLs específicos para diferentes ambientes (DES, QA, UAT, PRD), embora apenas o de DES seja usado no código.

6. **Handlers SOAP**: O sistema implementa handlers customizados para captura de trilha de auditoria, inicialização de contexto de requisição e tratamento de faults.

7. **Transações**: Os EJBs estão configurados com TransactionAttributeType.NOT_SUPPORTED, indicando que as transações são gerenciadas pelas stored procedures no banco de dados.

8. **Maven Multi-módulo**: O projeto está organizado em 6 módulos Maven (commons, domain, persistence, business, ws, ear).