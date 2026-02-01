# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **java-gdcc-base-consulta-geral-debito-conta** é um serviço backend desenvolvido em Java EE que fornece funcionalidades de consulta geral de débitos em conta. O sistema expõe Web Services SOAP para consultar totalizações de débitos por data de vencimento e por data de remessa, agregando informações sobre quantidades e valores de débitos em diferentes estados (vencimento, remessa, retorno, efetivado, pendente).

O sistema segue uma arquitetura em camadas (EAR, EJB, Web Services) e utiliza o padrão DAO para acesso a dados em banco Sybase, realizando consultas complexas com agregações e cálculos de totalizações.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `ConsultaGeralDebitoContaBeanImpl` | EJB Stateless que implementa a lógica de negócio, orquestrando as consultas aos DAOs |
| `ConsultaGeralDebitoContaEndPoint` | Endpoint JAX-WS que expõe os serviços SOAP e realiza conversões entre objetos de domínio e DTOs do contrato |
| `ConsultaGeralDebitoVencimentoDAOImpl` | DAO responsável por executar consultas de débitos agrupados por data de vencimento |
| `ConsultaGeralDebitoRemessaDAOImpl` | DAO responsável por executar consultas de débitos agrupados por data de remessa |
| `ConsultaGeralDebitoVencimentoMapper` | Mapper Spring JDBC para conversão de ResultSet em objetos DTO (consulta por vencimento) |
| `ConsultaGeralDebitoRemessaMapper` | Mapper Spring JDBC para conversão de ResultSet em objetos DTO (consulta por remessa) |
| `ConsultaGeralVencimentoRemessa` | Objeto de domínio que encapsula os parâmetros de entrada das consultas |
| `ConsultaGeralDebitoVencimentoRemessaDTO` | DTO que representa o resultado das consultas com totalizações |

---

## 3. Tecnologias Utilizadas

- **Java EE 7** (JAX-WS, EJB 3.1, CDI)
- **Maven** (gerenciamento de dependências e build multi-módulo)
- **JAX-WS** (Web Services SOAP)
- **Spring JDBC** (acesso a dados via NamedParameterJdbcTemplate)
- **Sybase ASE** (banco de dados)
- **WebSphere Application Server** (IBM WAS)
- **SLF4J + Log4j2** (logging)
- **JUnit, PowerMock, Mockito** (testes unitários)
- **Framework FJEE Base** (framework corporativo Votorantim)

---

## 4. Principais Endpoints REST

Não se aplica. O sistema expõe apenas Web Services SOAP.

**Endpoints SOAP:**

| Operação | Descrição | Classe Controladora |
|----------|-----------|---------------------|
| `consultarTotalDebitoPorVencimento` | Consulta totalizações de débitos agrupados por data de vencimento e banco | `ConsultaGeralDebitoContaEndPoint` |
| `consultarTotalRemessaDebitoPorVencimento` | Consulta totalizações de débitos agrupados por data de remessa e banco | `ConsultaGeralDebitoContaEndPoint` |

---

## 5. Principais Regras de Negócio

1. **Consulta por Vencimento**: Agrupa débitos por número do banco e data de vencimento, calculando quantidades e valores totais em diferentes estados (vencimento, remessa, retorno, efetivado)

2. **Consulta por Remessa**: Agrupa débitos por número do banco e data de remessa, calculando as mesmas totalizações da consulta por vencimento

3. **Cálculo de Pendentes**: Quantidade pendente = quantidade remessa - (quantidade efetivada + quantidade retorno). Valor pendente = valor remessa - (valor efetivado + valor retorno)

4. **Filtros Opcionais**: As consultas permitem filtros opcionais por código de veículo legal, código de sistema origem e número do banco

5. **Segurança**: Todas as operações exigem autenticação e autorização com a role "intr-middleware"

6. **Transações**: As operações são executadas com `TransactionAttributeType.NOT_SUPPORTED` (sem transação gerenciada)

---

## 6. Relação entre Entidades

**Entidades de Domínio:**

- `ConsultaGeralVencimentoRemessa`: Entidade de entrada contendo filtros (codigoVeiculoLegal, codigoSistemaOrigem, numeroBanco, dataVencimentoDebito, dataRemessaDebito)

- `ConsultaGeralDebitoVencimentoRemessaDTO`: Entidade de saída contendo totalizações (numeroBanco, dataVencimentoDebito/dataRemessaDebito, quantidades e valores totais de vencimento, remessa, retorno, pendente, efetivado)

**Relacionamento:** As entidades não possuem relacionamentos JPA tradicionais, pois o sistema utiliza consultas SQL nativas com agregações. Os dados são provenientes de múltiplas tabelas relacionadas no banco de dados.

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| `TbRegistroDebito` | Tabela | SELECT | Tabela principal contendo registros de débitos |
| `TbContaConvenioSistemaOrigem` | Tabela | SELECT | Tabela de relacionamento entre contas convênio e sistemas origem |
| `TbContaConvenio` | Tabela | SELECT | Tabela de contas convênio |
| `TbEventoRegistroDebito` | Tabela | SELECT | Tabela de eventos relacionados aos registros de débito |
| `TbParametroRetornoDebito` | Tabela | SELECT | Tabela de parâmetros de retorno de débito |
| `TbRetornoDebitoSistemaOrigem` | Tabela | SELECT | Tabela de retornos de débito por sistema origem |

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema realiza apenas operações de leitura (SELECT).

---

## 9. Arquivos Lidos e Gravados

Não se aplica. O sistema não realiza leitura ou gravação de arquivos físicos.

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

---

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas.

---

## 12. Integrações Externas

Não se aplica. O sistema não integra com sistemas externos. Ele expõe serviços SOAP para serem consumidos por outros sistemas.

**Serviços Expostos:**
- `ConsultaGeralDebitoContaBackendService` (SOAP) - Expõe operações de consulta de débitos para sistemas clientes

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada em camadas (domain, persistence, business, ws)
- Uso adequado de padrões (DAO, DTO, Mapper)
- Separação clara de responsabilidades
- Uso de injeção de dependências (CDI/EJB)
- Logging implementado com SLF4J
- Testes unitários presentes
- Uso de framework corporativo padronizado

**Pontos de Melhoria:**
- Queries SQL complexas embutidas em arquivos XML (dificulta manutenção e testes)
- Uso de tabelas temporárias (#TB_MONITOR) nas queries pode impactar performance
- Tratamento de exceções genérico (apenas log e re-throw)
- Falta de validação de parâmetros de entrada
- Código com alguns comentários em português misturados com código
- Conversões manuais entre tipos (Date/XMLGregorianCalendar) poderiam ser encapsuladas
- Cálculos de negócio (pendentes) no endpoint ao invés da camada de negócio
- Falta de documentação JavaDoc em algumas classes

---

## 14. Observações Relevantes

1. **DataSource**: O sistema utiliza o DataSource `jdbc/GDCCSybaseDS` configurado no WebSphere para conexão com banco Sybase

2. **Segurança**: Implementa autenticação BASIC e autorização baseada em roles (intr-middleware)

3. **Trilha de Auditoria**: O sistema utiliza handlers JAX-WS para captura de trilha de auditoria (ArqtBasePropertiesEndpointHandler, CapturadorTrilhaOutbound, FormatadorTrilhaOutbound)

4. **Classloader**: Configurado com modo PARENT_LAST no deployment.xml para isolamento de bibliotecas

5. **Versionamento**: O sistema está na versão 19.6.2.DEB35-477.0

6. **Ambiente Multi-módulo**: Projeto Maven estruturado em 9 módulos (commons, domain, persistence, integration, business, jms, ws, rs, ear)

7. **Módulo JMS**: Presente na estrutura mas sem implementação (preparado para futuras integrações assíncronas)

8. **Módulo RS**: Presente na estrutura mas sem implementação (preparado para futuras APIs REST)

9. **Framework Corporativo**: Utiliza bibliotecas corporativas Votorantim (arqt-base-lib, fjee-base-lib) para padronização

10. **Queries Complexas**: As consultas SQL realizam múltiplos UPDATEs em tabelas temporárias antes da agregação final, o que pode ser otimizado