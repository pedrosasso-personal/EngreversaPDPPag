# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de consulta de pagamentos vinculados a contratos, desenvolvido em Java EE utilizando arquitetura de camadas (EJB, Web Services SOAP). O sistema permite obter informações detalhadas de pagamentos através de código de pagamento ou número de contrato, expondo essas funcionalidades via Web Services SOAP para integração com outros sistemas.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `PagamentoContratolBeanImpl` | EJB Singleton que implementa a lógica de negócio para consulta de pagamentos |
| `PagamentoContratolBeanLocal` | Interface local do EJB que define os métodos de consulta |
| `PagamentoContratoEndpoint` | Endpoint SOAP que expõe os serviços de consulta de pagamento |
| `ConsultaPagamentoDaoImpl` | DAO que realiza consultas ao banco de dados de pagamentos |
| `ConsultaPagamentoDao` | Interface do DAO de consulta de pagamentos |
| `PagamentoContratoMapper` | Mapper que converte ResultSet em objetos de domínio |
| `PagamentoContratoVO` | Value Object que representa os dados de pagamento e contrato |
| `PagamentoVO` | Value Object que representa um pagamento completo com todas as entidades relacionadas |

## 3. Tecnologias Utilizadas

- **Java EE 6+** (EJB 3.1, JAX-WS, CDI)
- **IBM WebSphere Application Server** (servidor de aplicação)
- **Spring JDBC** (acesso a dados)
- **Apache Commons BeanUtils** (manipulação de beans)
- **SLF4J/Log4j2** (logging)
- **Oracle Database** (banco de dados - via JDBC)
- **SOAP Web Services** (JAX-WS)
- **Maven** (gerenciamento de dependências e build)
- **IBM WebSphere Security** (autenticação e autorização)

## 4. Principais Endpoints REST

Não se aplica. O sistema utiliza Web Services SOAP, não REST.

**Endpoints SOAP:**

| Operação | Endpoint | Classe Controladora | Descrição |
|----------|----------|---------------------|-----------|
| `obterPagamentoContrato` | PagamentoContratoBackendService | `PagamentoContratoEndpoint` | Obtém dados de um pagamento específico por código |
| `listarPagamentosContrato` | PagamentoContratoBackendService | `PagamentoContratoEndpoint` | Lista todos os pagamentos de um contrato |

## 5. Principais Regras de Negócio

- Consulta de pagamentos por código de pagamento individual
- Consulta de pagamentos por número de contrato (com filtro opcional por sequência do contrato)
- Mapeamento de dados de pagamento incluindo informações de: remetente, favorecido, contas bancárias, produto, modalidade, operador comercial, parceiro comercial, protocolo e situação
- Formatação de datas do formato banco de dados para XMLGregorianCalendar
- Controle de acesso baseado em roles (role "intr-middleware" requerida)
- Tratamento de exceções de negócio e técnicas com retorno padronizado via BvFault
- Validação de existência de pagamentos para número de contrato informado

## 6. Relação entre Entidades

**Entidade Principal: PagamentoContratoVO/PagamentoVO**

Relacionamentos:
- **PagamentoVO** possui:
  - `SistemaVO` (sistema origem)
  - `SituacaoPagamentoVO` (situação do pagamento)
  - `FormaPagamentoVO` (forma de pagamento)
  - `FilialComercialDadosBasicosVO` (filial comercial)
  - `VeiculoLegalVO` (veículo legal)
  - `ProdutoVO` (produto, que contém listas de Modalidades e SubProdutos)
  - `ModalidadeVO` (modalidade)
  - `ParceiroComercialDadosBasicosVO` (parceiro comercial, que contém TipoParceiroComercial e PessoaDadosBasicos)
  - `OperadorComercialVO` (operador, herda de ColaboradorComercial, contém NivelCargo e PessoaDadosBasicos)
  - `PessoaDadosBasicosVO` (remetente)
  - `PessoaDadosBasicosVO` (favorecido)
  - `ContaVO` (conta remetente e favorecido, que contém TipoConta, Agencia e SituacaoConta)
  - `AgenciaVO` (que contém BancoVO)
  - `OperacaoPagamentoVO` (operação de pagamento)
  - `OrigemPagamentoVO` (origem do pagamento)
  - `TipoTransacaoFinanceiraVO` (tipo de transação)
  - `ContratoDadosBasicosVO` (dados do contrato)
  - `ProtocoloVO` (protocolo de pagamento)

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBPAGAMENTO..TbPagamento | tabela | SELECT | Tabela principal de pagamentos |
| DBPAGAMENTO..TbPagamentoContrato | tabela | SELECT | Tabela de relacionamento pagamento-contrato |
| DBPAGAMENTO..TbInformacaoBancariaPagamento | tabela | SELECT | Informações bancárias do favorecido |
| DBPAGAMENTO..TbPessoaPagamento | tabela | SELECT | Dados de pessoas (favorecido e proponente) |
| DBPAGAMENTO..TbSituacaoPagamento | tabela | SELECT | Situações possíveis de pagamento |
| DBCOR..TbFormaPagto | tabela | SELECT | Formas de pagamento disponíveis |

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema realiza apenas operações de leitura (SELECT).

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| ConsultaPagamentoDaoImpl-sql.xml | leitura | `ConsultaPagamentoDaoImpl` | Arquivo XML contendo as queries SQL utilizadas pelo DAO |
| errorMessages.properties | leitura | commons/resources | Arquivo de mensagens de erro do sistema |
| roles.properties | leitura | commons/resources | Arquivo de configuração de roles de segurança |
| beans.xml | leitura | META-INF (diversos módulos) | Arquivos de configuração CDI |
| ejb-jar.xml | leitura | business/META-INF | Descritor de deployment de EJBs |
| web.xml | leitura | ws/WEB-INF | Descritor de deployment da aplicação web |
| application.xml | leitura | ear/META-INF | Descritor de deployment do EAR |
| *.wsdl e *.xsd | leitura | ws/WEB-INF/wsdl | Contratos WSDL e schemas XSD dos Web Services |

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas.

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Banco de Dados Oracle (DBPAGAMENTO) | JDBC | Consulta de dados de pagamentos e contratos |
| Banco de Dados Oracle (DBCOR) | JDBC | Consulta de dados corporativos (formas de pagamento) |
| Sistemas Consumidores SOAP | Web Service Provider | Sistemas externos que consomem os serviços de consulta de pagamento |
| IBM WebSphere Security | Autenticação/Autorização | Controle de acesso baseado em roles e políticas de segurança WS-Security |

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades em camadas (domain, persistence, business, ws)
- Uso adequado de padrões Java EE (EJB, JAX-WS, CDI)
- Documentação JavaDoc presente nas classes principais
- Tratamento de exceções estruturado com retorno padronizado
- Uso de Value Objects para transferência de dados
- Configuração externalizada (properties, XML)

**Pontos de Melhoria:**
- Método `mapearRetornoDadosPagamento` muito extenso (mais de 100 linhas), violando princípio de responsabilidade única
- Classe `PagamentoContratoEndpoint` com métodos muito longos e complexos
- Duplicação de código no tratamento de exceções nos endpoints SOAP
- Uso excessivo de `BeanUtils.copyProperties` que pode ocultar erros em tempo de execução
- Falta de testes unitários (apenas estrutura de diretórios test presente)
- Conversão manual de tipos poderia ser melhorada com frameworks de mapeamento (MapStruct, ModelMapper)
- Alguns métodos privados de mapeamento poderiam ser extraídos para classes utilitárias dedicadas
- Código com alguns "code smells" como métodos com muitos parâmetros implícitos via objetos complexos

## 14. Observações Relevantes

- O sistema utiliza arquitetura legada baseada em EJB 3.1 e Web Services SOAP, tecnologias ainda comuns em ambientes corporativos mas consideradas menos modernas
- Há forte dependência do IBM WebSphere Application Server, incluindo configurações específicas (ibm-*.xml)
- O sistema implementa trilha de auditoria através de handlers SOAP customizados
- Utiliza políticas de segurança WS-Security configuradas no WebSphere (BvWsSecurityUsernameToken, BvWsSecurityCertificate)
- DataSource configurado via JNDI: `jdbc/aproBaseDBCORDS`
- O sistema faz parte de um contexto maior (módulo pagm-base) e depende de bibliotecas corporativas (fjee-base, arqt-base)
- Versionamento semântico utilizado: 17.1.3.1-SNAPSHOT
- Build gerenciado via Maven com estrutura multi-módulo
- Preparado para deploy em cluster WebSphere com configurações de classloader específicas (PARENT_LAST)