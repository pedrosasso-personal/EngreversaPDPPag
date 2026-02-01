# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **java-pgft-base-dda-agregado-atacado** é um componente backend desenvolvido em Java EE que gerencia operações relacionadas ao DDA (Débito Direto Autorizado) para agregados no contexto de contas correntes atacado. O sistema permite a gestão completa de agregados DDA, incluindo operações de inclusão, alteração, exclusão, listagem, aceitação e recusa de convites de agregação. O sistema expõe suas funcionalidades através de Web Services SOAP e integra-se com banco de dados através de stored procedures.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `DdaAgregadoBeanImpl` | EJB Stateless que implementa a lógica de negócio para operações de agregado DDA |
| `DdaAgregadoBeanLocal` | Interface local do EJB de negócio |
| `DDAAgregadoEndpoint` | Endpoint SOAP que expõe os serviços web para operações de agregado DDA |
| `DdaAgregadoDaoImpl` | Implementação DAO para acesso a dados de agregados DDA usando JDBC/Spring |
| `DdaAgregadoDaoLocal` | Interface local do DAO |
| `AgregadoDdaVO` | Value Object representando um agregado DDA com informações completas |
| `AceiteAgregadoDdaVO` | Value Object para aceite de agregado DDA |
| `BaseAgregadoDdaVO` | Value Object base com informações de agregado e cliente |
| `RetornoPadraoDdaVO` | Value Object para retornos padronizados |
| `*StoredProcedure` | Classes que encapsulam chamadas a stored procedures específicas |
| `*Mapper` | Classes responsáveis por mapear ResultSets para Value Objects |

---

## 3. Tecnologias Utilizadas

- **Java EE 6/7** (EJB 3.1, JAX-WS, CDI)
- **Maven** (gerenciamento de dependências e build)
- **Spring JDBC** (acesso a dados)
- **JAX-WS** (Web Services SOAP)
- **IBM WebSphere Application Server** (servidor de aplicação)
- **Oracle Database** (banco de dados via JDBC)
- **Log4j2** (logging)
- **SLF4J** (facade de logging)
- **JUnit, Mockito, PowerMock** (testes unitários)
- **Framework FJEE Base** (framework corporativo Votorantim)
- **Framework ARQT Base** (arquitetura base Votorantim)

---

## 4. Principais Endpoints REST

Não se aplica. O sistema utiliza Web Services SOAP, não REST.

**Endpoints SOAP disponíveis:**

| Operação | Descrição |
|----------|-----------|
| `listarAceiteAgregado` | Consulta aceites de agregados DDA |
| `listarAgregado` | Consulta agregados DDA |
| `aceitarSerAgregadoDDA` | Aceita convite para ser agregado |
| `confirmarAgregadoDDA` | Confirma operação de agregado DDA |
| `incluirAgregadoDDA` | Inclui novo agregado DDA |
| `excluirAgregadoDDA` | Exclui agregado DDA |
| `alterarAgregado` | Altera dados de agregado |
| `recusarSerAgregado` | Recusa convite para ser agregado |

---

## 5. Principais Regras de Negócio

1. **Gestão de Agregados DDA**: Permite que clientes gerenciem agregados (outras pessoas/empresas) vinculados à sua conta DDA
2. **Controle de Convites**: Sistema de convite/aceite/recusa para agregação de clientes
3. **Validação de CPF/CNPJ**: Identificação de tipo de pessoa (física/jurídica) baseada no tamanho do documento
4. **Auditoria**: Todas as operações registram informações de auditoria (login, data/hora)
5. **Integração CIP**: Comunicação com a Câmara Interbancária de Pagamentos para operações DDA
6. **Segurança**: Controle de acesso via role "intr-middleware"
7. **Transações**: Operações configuradas como NOT_SUPPORTED para controle transacional específico
8. **Tratamento de Erros**: Padronização de exceções através de Fault SOAP

---

## 6. Relação entre Entidades

**Entidades principais:**

- **AgregadoDdaVO**: Representa um agregado completo com dados pessoais, datas de aceite e ativação
  - Herda de: `EntidadeBase<Long>`
  - Atributos: codigoPessoa, numeroCpfCnpj, nomeCompleto, tipoPessoa, dataNascimento, formaAceite, dataAceite, emailAgregado, dataAtivacaoDDA

- **AceiteAgregadoDdaVO**: Representa aceite de agregado
  - Herda de: `EntidadeBase<Long>`
  - Atributos: codigoCliente, numeroCpfCnpj, nomeCompleto

- **BaseAgregadoDdaVO**: Informações base de agregado e cliente
  - Herda de: `BaseClienteDdaVO`
  - Atributos: tpPessoaAgregado, cnpjCpfAgregado, indManutencaoAgregadoDDA

- **BaseClienteDdaVO**: Informações base do cliente DDA
  - Herda de: `EntidadeBase<Long>`
  - Atributos: codMsg, numCtrlPart, iSPBPartRecbdrPrincipal, iSPBPartRecbdrADmtd, tpPessoaPagdr, cnpjCpfPagdr, numIdentcPagdr, numRefAtlCadCliPagdr, dtMovto

- **RetornoPadraoDdaVO**: Retorno padronizado
  - Atributos: codigo, mensagem

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| Resultado de `PrListarAgregadoDDA` | Stored Procedure | SELECT/READ | Lista agregados DDA de um cliente |
| Resultado de `PrListarAceiteAgregadoDDA` | Stored Procedure | SELECT/READ | Lista aceites de agregados DDA pendentes |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| `PrIncluirAlterarAgregadoDDA` | Stored Procedure | INSERT/UPDATE | Inclui ou altera agregado DDA |
| `PrExcluirAgregadoDDA` | Stored Procedure | DELETE | Exclui agregado DDA |
| `PrAceitarConviteAgregadoDDA` | Stored Procedure | UPDATE | Aceita convite de agregação |
| `PrRecusarConviteAgregadoDDA` | Stored Procedure | UPDATE | Recusa convite de agregação |
| `PrConfirmarAgregadoDDA` | Stored Procedure | UPDATE | Confirma operação de agregado DDA |

**Observação**: Todas as operações são realizadas através de stored procedures no schema `DBPGF_TES`.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `errorMessages.properties` | Leitura | commons/src/main/resources | Mensagens de erro do sistema |
| `roles.properties` | Leitura | commons/src/main/resources | Definição de roles de segurança |
| `DdaAgregadoDaoImpl-sql.xml` | Leitura | persistence/src/main/resources | Queries SQL (arquivo vazio no projeto) |
| `log4j2.xml` | Leitura | Diversos módulos | Configuração de logging |
| `*.wsdl` e `*.xsd` | Leitura | ws/src/main/webapp/WEB-INF/wsdl | Contratos de Web Services |

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
| **Banco de Dados Oracle** | JDBC | Acesso via DataSource `jdbc/PgftCobrancaDDADS` para operações de persistência |
| **CIP (Câmara Interbancária de Pagamentos)** | Integração | Sistema externo para operações DDA, referenciado nos códigos de controle e identificação |
| **Framework FJEE Base** | Biblioteca | Framework corporativo para funcionalidades comuns (trilha de auditoria, handlers, etc) |
| **IBM WebSphere** | Servidor de Aplicação | Container EJB e Web Services |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades em camadas (domain, persistence, business, ws)
- Uso adequado de padrões Java EE (EJB, JAX-WS, CDI)
- Implementação de interfaces para desacoplamento
- Uso de Value Objects para transferência de dados
- Tratamento de exceções padronizado
- Documentação presente nos WSDLs e alguns comentários em código
- Uso de frameworks corporativos estabelecidos

**Pontos de Melhoria:**
- Código com alguns comentários em português misturados com inglês
- Falta de validações de entrada em alguns métodos
- Uso de `@SuppressWarnings("unchecked")` sem justificativa adequada
- Alguns métodos com muitos parâmetros (ex: `confirmarAgregadoDda` com 11 parâmetros)
- Tratamento genérico de exceções em alguns pontos (`catch(Exception e)`)
- Falta de testes unitários implementados (apenas estrutura)
- Código de mapeamento de tipo de pessoa baseado em tamanho de string poderia ser mais robusto
- Alguns Value Objects com lógica de negócio (getters com `new Date()`)
- Falta de constantes para strings literais repetidas

O código é funcional e segue boas práticas gerais, mas há espaço para melhorias em validação, tratamento de erros específicos e redução de acoplamento em alguns pontos.

---

## 14. Observações Relevantes

1. **Ambiente Multi-Ambiente**: O sistema possui WSDLs específicos para cada ambiente (DES, QA, UAT, PRD)

2. **Segurança**: Implementa autenticação BASIC e controle de acesso via roles. Utiliza políticas de segurança WS-Security (UsernameToken e Certificate)

3. **Handlers SOAP**: Implementa handlers customizados para trilha de auditoria, inicialização de contexto e tratamento de falhas

4. **Versionamento**: Sistema versionado (19.3.1.P1883-1.0) seguindo padrão corporativo

5. **DataSource JNDI**: Utiliza `jdbc/PgftCobrancaDDADS` como nome JNDI do DataSource

6. **Classloader**: Configurado com modo PARENT_LAST no deployment.xml para isolamento de bibliotecas

7. **Shared Libraries**: Utiliza bibliotecas compartilhadas `arqt-base-lib-1.0` e `fjee-base-lib-1.1`

8. **Stored Procedures**: Toda a lógica de persistência é delegada a stored procedures no banco de dados

9. **Padrão de Nomenclatura**: Segue convenção corporativa Votorantim (prefixos `Pr` para procedures, `Cd` para códigos, `Nu` para números, etc)

10. **Maven Multi-Module**: Projeto organizado em múltiplos módulos Maven (commons, domain, persistence, business, ws, ear)