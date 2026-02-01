# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de validação e consulta de títulos de pagamento (boletos) integrado com a CIP (Câmara Interbancária de Pagamentos). O sistema permite consultar informações detalhadas de boletos através do código de barras, incluindo dados de juros, multas, descontos, baixas operacionais e efetivas. Implementa regras de negócio para validação de pagamentos e controle de contingência, armazenando histórico de consultas e transações.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `ConsultarCalculoBeanImpl` | EJB para consulta e inserção de cálculos de títulos |
| `ConsultarDescontoBeanImpl` | EJB para consulta e inserção de descontos |
| `ConsultarEfetivaBeanImpl` | EJB para consulta e inserção de baixas efetivas |
| `ConsultarOperacionalBeanImpl` | EJB para consulta e inserção de baixas operacionais |
| `ConsultarTituloCipBeanImpl` | EJB para consulta de títulos CIP por código de barras |
| `JurosBoletoTituloBeanImpl` | EJB para consulta e inserção de juros de boletos |
| `MultaBoletoTituloBeanImpl` | EJB para consulta e inserção de multas de boletos |
| `RecuperarTituloCipBeanImpl` | EJB para recuperação completa de títulos CIP |
| `TituloBeanImpl` | EJB para recuperação de parâmetros de integração CIP |
| `Conversores` | Utilitário para conversão de código de barras e datas |
| `TituloCIPUtil` | Utilitário para operações com juros e multas de boletos CIP |
| `*DaoImpl` | Implementações DAO para acesso a dados via JDBC |
| `*RowMapper` | Mapeadores Spring JDBC para conversão ResultSet → VO |
| `*VO` | Value Objects representando entidades de domínio |

## 3. Tecnologias Utilizadas

- **Java EE / Jakarta EE** - Plataforma base
- **IBM WebSphere Application Server (WAS)** - Servidor de aplicação
- **EJB 3.1** - Enterprise JavaBeans (Singleton Session Beans)
- **CDI (Contexts and Dependency Injection)** - Injeção de dependências
- **Spring JDBC** - Acesso a dados (NamedParameterJdbcTemplate)
- **Maven** - Gerenciamento de dependências e build (estrutura multi-módulo)
- **JAX-WS** - Web Services SOAP
- **JAX-RS** - REST API
- **JMS** - Mensageria
- **JDBC** - Conectividade com banco de dados
- **Log4j2** - Logging
- **JUnit / PowerMock / Mockito** - Testes unitários
- **Sybase/SQL Server** - Banco de dados (schema DBPGF_TES)

## 4. Principais Endpoints REST

Não se aplica. O projeto possui módulos para REST (rs) e SOAP (ws), mas os arquivos de implementação dos endpoints não foram fornecidos no JSON.

## 5. Principais Regras de Negócio

1. **Validação de Código de Barras**: Conversão e validação de códigos de barras de boletos (44 dígitos), com tratamento especial para banco 988
2. **Validação de CPF**: Algoritmo de validação de CPF com cálculo de dígitos verificadores
3. **Cálculo de Juros e Multas**: Seleção da data futura mais próxima para aplicação de juros/multas baseada na data atual
4. **Controle de Contingência**: Parâmetros configuráveis para operação em modo contingência (FlRecebimentoContingenciaCIP)
5. **Validação de Valores**: Controle de valores mínimos e máximos para validação e autorização CIP
6. **Histórico de Consultas**: Registro de todas as consultas realizadas com código de barras e timestamp
7. **Pagamento Parcial**: Controle de quantidade de pagamentos parciais e saldo atual
8. **Bloqueio de Pagamento**: Flag para bloqueio de pagamentos de títulos
9. **Autorização de Valor Divergente**: Controle de autorização para pagamentos com valores diferentes do título
10. **Modelo de Cálculo**: Suporte a diferentes tipos de modelos de cálculo de juros/multas

## 6. Relação entre Entidades

- **TituloVO**: Entidade principal representando um título/boleto
  - Contém `TituloCipVO` (dados completos do boleto)
  
- **TituloCipVO** (herda de TituloCip2VO): Dados completos do título CIP
  - Relacionamento 1:N com `TituloJurosCipVO` (juros)
  - Relacionamento 1:N com `TituloMultaCipVO` (multas)
  - Relacionamento 1:N com `TituloDescontoCipVO` (descontos)
  - Relacionamento 1:N com `TituloCalculoCipVO` (cálculos)
  - Relacionamento 1:N com `BaixaOperacionalCipVO` (baixas operacionais)
  - Relacionamento 1:N com `BaixaEfetivaCipVO` (baixas efetivas)

- **TituloCip2VO**: Dados complementares do título (beneficiários, pagador)

- **ParametrosIntegracaoCipVO**: Parâmetros de configuração da integração CIP

- **CodigoBarraVO**: Representação estruturada do código de barras

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbSolicitacaoConsultaTitulo | Tabela | SELECT | Consulta de títulos por código de barras e histórico de consultas |
| TbBaixaEfetivaTitulo | Tabela | SELECT | Consulta de baixas efetivas de títulos |
| TbBaixaOperacionalTitulo | Tabela | SELECT | Consulta de baixas operacionais de títulos |
| TbCalculoTitulo | Tabela | SELECT | Consulta de cálculos de títulos (juros, multas, descontos) |
| TbDescontoBoleto | Tabela | SELECT | Consulta de descontos de boletos |
| TbJurosBoleto | Tabela | SELECT | Consulta de juros de boletos |
| TbMultaBoleto | Tabela | SELECT | Consulta de multas de boletos |
| TbParametroInterfaceCIP | Tabela | SELECT | Consulta de parâmetros de integração CIP |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbSolicitacaoConsultaTitulo | Tabela | INSERT | Inclusão de novas consultas de código de barras e dados completos de títulos |
| TbBaixaEfetivaTitulo | Tabela | INSERT | Inclusão de baixas efetivas de títulos |
| TbBaixaOperacionalTitulo | Tabela | INSERT | Inclusão de baixas operacionais de títulos |
| TbCalculoTitulo | Tabela | INSERT | Inclusão de cálculos de títulos |
| TbDescontoBoleto | Tabela | INSERT | Inclusão de descontos de boletos |
| TbJurosBoleto | Tabela | INSERT | Inclusão de juros de boletos |
| TbMultaBoleto | Tabela | INSERT | Inclusão de multas de boletos |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| errorMessages.properties | Leitura | commons/src/main/resources | Mensagens de erro do sistema |
| roles.properties | Leitura | commons/src/main/resources | Definição de roles de segurança |
| *-sql.xml | Leitura | persistence/src/main/resources | Queries SQL nomeadas para operações de banco |
| log4j2.xml | Leitura | Diversos módulos | Configuração de logging |

## 10. Filas Lidas

Não se aplica. O módulo JMS está presente na estrutura, mas não há implementações de MDBs (Message-Driven Beans) nos arquivos fornecidos.

## 11. Filas Geradas

Não se aplica. Não há evidências de publicação em filas nos arquivos fornecidos.

## 12. Integrações Externas

1. **CIP (Câmara Interbancária de Pagamentos)**: Integração para consulta e validação de títulos de pagamento. A integração é configurada através de parâmetros na tabela TbParametroInterfaceCIP, incluindo URLs de retorno e flags de contingência.

2. **Banco de Dados Sybase/SQL Server**: Schema DBPGF_TES via DataSource JNDI `jdbc/PgftDS`

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades em camadas (business, persistence, domain)
- Uso adequado de padrões Java EE (EJB, CDI, JNDI)
- Implementação de segurança com roles declarativas
- Uso de RowMappers do Spring JDBC para mapeamento objeto-relacional
- Queries SQL externalizadas em arquivos XML
- Tratamento de exceções com fallback para listas vazias
- Uso de Value Objects imutáveis (clonagem de datas nos getters)
- Documentação JavaDoc presente

**Pontos Negativos:**
- Código com comentários em português e inglês misturados
- Algumas classes com responsabilidades muito similares (duplicação de lógica)
- Falta de tratamento adequado de exceções (catch genérico com retorno de lista vazia)
- Uso de convenção de nomenclatura inconsistente (CdSolicitacaoConsultaTitulo vs cdSolicitacaoConsultaTitulo)
- Queries SQL com schema hardcoded (DBPGF_TES..)
- Falta de validações de entrada em alguns métodos
- Código legado com estruturas antigas (uso de BigInteger/BigDecimal onde int/long seriam suficientes)
- Ausência de logs estruturados para auditoria

## 14. Observações Relevantes

1. **Arquitetura Multi-Módulo**: O projeto está bem estruturado em módulos Maven (business, commons, domain, persistence, integration, jms, ws, rs, ear)

2. **Segurança**: Implementa segurança baseada em roles com a role `intr-middleware` configurada para todos os EJBs

3. **Transações**: Todos os EJBs de negócio utilizam `TransactionAttributeType.REQUIRES_NEW`, garantindo transações independentes

4. **Banco Específico**: O código está fortemente acoplado ao banco Sybase/SQL Server (uso de `coalesce`, sintaxe específica)

5. **Padrão de Nomenclatura**: Utiliza prefixos húngaros nas colunas do banco (Cd, Dt, Vr, Fl, Nm, etc.)

6. **Histórico**: O sistema mantém histórico completo de consultas, permitindo auditoria e análise de uso

7. **Configuração Externa**: Parâmetros de integração CIP são configuráveis via banco de dados

8. **Código de Barras**: Implementa lógica específica para tratamento do banco 988 (código COMPE)

9. **WebSphere**: Configurações específicas para IBM WebSphere (ibm-ejb-jar-bnd.xml, deployment.xml, policy attachments)

10. **Versionamento**: Versão do projeto: 19.7.1.SAT-444.2-SNAPSHOT