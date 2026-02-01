# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **flex-calc-controladoria-carga** é um componente de integração desenvolvido em Java EE que expõe um serviço web (SOAP/JAX-WS) para receber e armazenar dados de contratos financeiros oriundos do sistema Flex. O principal objetivo é realizar a carga de informações de contratos na base de dados gerencial (controladoria), permitindo que sistemas externos enviem dados de contratos de financiamento para posterior análise e processamento. O sistema recebe requisições com informações detalhadas de contratos (valores, parcelas, taxas, dados do cliente, parceiro comercial, etc.), valida os dados de entrada e persiste as informações na tabela `TbIntegracaoContrato`.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `ControladoriaLegadoServiceEndpoint` | Endpoint do Web Service que expõe a operação `criarContratoControladoria`. Recebe requisições SOAP, valida dados e orquestra a chamada ao serviço de negócio. |
| `ControladoriaCargaFlexServiceImpl` | Implementação EJB Stateless do serviço de negócio. Delega a persistência ao DAO. |
| `ControladoriaCargaFlexDaoImpl` | Implementação do DAO responsável pela inserção de registros na base de dados usando Spring JDBC. |
| `CriarContratoControladoriaRequestTO` | Transfer Object que representa a requisição do serviço com validações via anotações customizadas. |
| `IntegracaoContratoTO` | Transfer Object que representa os dados do contrato a serem persistidos. |
| `WebserviceBeanMapperImpl` | Mapper genérico que converte objetos Stub (gerados do WSDL) para Transfer Objects usando reflexão. |
| `BeanValidatorServiceImpl` | Serviço de validação customizado que processa anotações de validação nos TOs. |
| `IntegracaoContratoTOBuilder` | Builder para construir o objeto `IntegracaoContratoTO` a partir do request. |
| `ControladoriaLegadoFaultBuilder` | Builder para construção de falhas (faults) SOAP padronizadas. |

---

## 3. Tecnologias Utilizadas

- **Java EE 6/7** (EJB 3.1, JAX-WS, CDI)
- **Maven** (gerenciamento de dependências e build)
- **Spring JDBC** (acesso a dados via NamedParameterJdbcTemplate)
- **JAX-WS** (Web Services SOAP)
- **WebSphere Application Server** (servidor de aplicação)
- **Oracle Database** (banco de dados - inferido pelo JDBC Provider Type)
- **SLF4J/Log4j2** (logging)
- **JUnit, Mockito, PowerMock** (testes unitários)
- **IBM WebSphere handlers** (handlers de auditoria e trilha)

---

## 4. Principais Endpoints REST

**não se aplica** - O sistema utiliza Web Services SOAP (JAX-WS), não REST.

### Endpoint SOAP:

| Operação | Endpoint | Classe Controladora | Descrição |
|----------|----------|---------------------|-----------|
| `criarContratoControladoria` | `/flex-calc-controladoria-carga-ws/ControladoriaFlexService` | `ControladoriaLegadoServiceEndpoint` | Recebe dados de contrato financeiro e persiste na base gerencial |

---

## 5. Principais Regras de Negócio

1. **Validação de Campos Obrigatórios**: Campos marcados com `@NotNull` e `@GreaterThanZero` são validados antes do processamento. Caso haja erros de validação, uma falha de negócio é retornada.

2. **Cálculo do Valor de Financiamento**: Se o valor de IOF for informado, ele é somado ao valor de financiamento (`valorFinanciamento + valorIof`).

3. **Valores Padrão**: Alguns campos recebem valores fixos definidos em enumerações:
   - `SqContratoFinanceiro` = 1 (sequência)
   - `CdMotivoContratoFinanceiro` = 1 (implantação)
   - `CdSituacaoContrato` = 1 (aberto)
   - `FlAtivo` = "S" (ativo)

4. **Validação de Parceiro Comercial**: O objeto `ParceiroComercialInfo` possui validação customizada que verifica campos obrigatórios internos.

5. **Conversão de Tipos**: Datas são convertidas de `XMLGregorianCalendar` (formato SOAP) para `java.util.Date`.

6. **Arredondamento de Taxa de Juros**: A taxa de juros é arredondada para 10 casas decimais usando `ROUND_DOWN`.

7. **Tratamento de Campos Opcionais**: Diversos campos são opcionais e só são incluídos na inserção se informados.

---

## 6. Relação entre Entidades

O sistema trabalha principalmente com Transfer Objects (TOs) que não representam entidades JPA, mas sim estruturas de dados para transferência:

- **CriarContratoControladoriaRequestTO**: Contém todos os dados da requisição do serviço, incluindo:
  - Dados do contrato (número, valores, datas, taxas)
  - Dados do cliente (CPF/CNPJ, score, data nascimento)
  - **ParceiroComercialInfoTO**: Informações do parceiro comercial (código, região, tipo atividade)
  - Dados operacionais (operador, promotor, login)

- **IntegracaoContratoTO**: Representa o registro a ser inserido no banco, contendo todos os campos da tabela `TbIntegracaoContrato`.

**Relacionamento**: `CriarContratoControladoriaRequestTO` é transformado em `IntegracaoContratoTO` através do `IntegracaoContratoTOBuilder`, que desmembra o objeto aninhado `ParceiroComercialInfoTO` em campos individuais.

---

## 7. Estruturas de Banco de Dados Lidas

**não se aplica** - O sistema não realiza operações de leitura (SELECT) no banco de dados. Apenas insere registros.

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| `DBGERENCIAL..TbIntegracaoContrato` | Tabela | INSERT | Tabela que armazena os dados de integração de contratos financeiros para controladoria. Contém informações completas do contrato, cliente, parceiro comercial, valores, taxas e datas. |

**Campos inseridos** (37 campos): NuContrato, SqContratoFinanceiro, DtProcessamento, CdMotivoContratoFinanceiro, CdVeiculoLegal, CdProduto, VrIof, QtParcelas, VrContrato, VrEntrada, VrRetencao, VrComissaoTotal, VrComissaoParcelada, VrFinanciamento, VlFinanciadoAtual, VrPrestacao, TxJuros, CdSituacaoContrato, TpPrePos, DtPrimeiroVencimento, DtUltimoVencimento, CdTabelaFinanciamento, CdParceiroComercial, CdOperador, CdPromotor, CdModalidadeProduto, CdRegiao, TpAtividade, NuCpfCnpj, NuScore, VrMercado, TxInternaRetorno, PcFpr, DtNascimento, DsLogin, FlAtivo, DtInclusao.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `ControladoriaCargaFlexDaoImpl-sql.xml` | Leitura | `ControladoriaCargaFlexDaoImpl` | Arquivo XML contendo as queries SQL parametrizadas utilizadas pelo DAO. |
| `errorMessages.properties` | Leitura | Commons (resources) | Arquivo de propriedades contendo mensagens de erro padrão do sistema. |
| `roles.properties` | Leitura | Commons (resources) | Arquivo de propriedades contendo definição de roles de segurança. |

---

## 10. Filas Lidas

**não se aplica** - O sistema não consome mensagens de filas (JMS, Kafka, RabbitMQ, etc).

---

## 11. Filas Geradas

**não se aplica** - O sistema não publica mensagens em filas.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **Sistema Flex** | Cliente SOAP | Sistema externo que invoca o serviço `ControladoriaFlexService` para enviar dados de contratos financeiros. |
| **Base Gerencial (Oracle)** | Banco de Dados | DataSource JNDI `jdbc/flexBaseDBGerencialDS` utilizado para persistir dados na tabela `TbIntegracaoContrato`. |
| **WSRR (WebSphere Service Registry)** | Registro de Serviços | Referenciado nos comentários para download de schemas XSD corporativos (Comum.xsd). |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades em camadas (WS, Business, Persistence, Commons)
- Uso de padrões como Builder, DAO, Transfer Objects
- Framework de validação customizado bem estruturado com anotações
- Uso adequado de EJB e CDI
- Logging presente nas classes principais
- Tratamento de exceções com faults SOAP padronizados
- Uso de Spring JDBC para acesso a dados de forma limpa

**Pontos Negativos:**
- Código com alguns "code smells": métodos muito longos (ex: `IntegracaoContratoTOBuilder.build()` dividido em 4 métodos sequenciais)
- Uso excessivo de reflexão no `WebserviceBeanMapperImpl` pode impactar performance e dificultar manutenção
- Falta de testes unitários (apenas estrutura de diretórios de teste)
- Comentários em português misturados com código em inglês (falta de padronização)
- Alguns TODOs não implementados (ex: `ParceiroComercialInfoStubTOConverter.convertFromTO()`)
- Validações customizadas poderiam usar Bean Validation (JSR-303) padrão ao invés de framework próprio
- Falta documentação JavaDoc nas classes principais
- Configurações hardcoded em enumerações (valores "mágicos")

---

## 14. Observações Relevantes

1. **Segurança**: O sistema utiliza autenticação BASIC e role `intr-middleware` para controle de acesso. Handlers IBM WebSphere são configurados para trilha de auditoria e segurança WS-Security.

2. **Transações**: O EJB de serviço está configurado com `TransactionAttributeType.NOT_SUPPORTED`, delegando o controle transacional para camadas inferiores ou para o container.

3. **DataSource**: Utiliza lookup JNDI `jdbc/flexBaseDBGerencialDS` configurado no WebSphere.

4. **Versionamento**: O projeto segue versionamento semântico (0.1.0) e está integrado com Git.

5. **Deploy**: O sistema é empacotado como EAR contendo um EJB JAR (business) e um WAR (ws), com bibliotecas compartilhadas configuradas no `deployment.xml`.

6. **Políticas WS-Security**: Configuradas via `policyAttachments.xml` com diferentes níveis de segurança (Low, Medium, High) usando UsernameToken e Certificate.

7. **Classloader**: Configurado como `PARENT_LAST` para evitar conflitos de bibliotecas com o servidor.

8. **Dependências Corporativas**: O projeto depende de bibliotecas corporativas Votorantim (`arqt-base-lib`, `fjee-base-lib`) que fornecem funcionalidades comuns de auditoria, logging e handlers.