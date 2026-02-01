# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema responsável pelo cancelamento de baixa operacional de boletos DDA (Débito Direto Autorizado). O sistema recebe mensagens via fila JMS contendo informações sobre cancelamento de baixa operacional de títulos DDA e processa essas informações atualizando o banco de dados correspondente. Trata-se de um componente de integração que consome mensagens XML do padrão DDA0115R2 e executa stored procedures no banco de dados para efetuar o cancelamento.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `CancelarBaixaOperacional` (JMS) | Message-Driven Bean que consome mensagens da fila JMS e orquestra o processo de cancelamento |
| `CancelarBaixaOperacionalBean` (Business) | Contém a lógica de negócio para cancelamento de baixa operacional |
| `CancelarBaixaOperacionalDAO` / `CancelarBaixaOperacionalDAOImpl` | Interface e implementação para acesso a dados relacionados ao cancelamento |
| `CancelarBaixaOperacionalStoreProcedure` | Encapsula a chamada à stored procedure de cancelamento no banco |
| `ConverterUtil` | Utilitário para conversão de mensagens JMS (XML) em objetos Java |
| `DebitoDiretoAutorizadoDDA0115R2Mensagem` | Entidade de domínio representando a mensagem DDA0115R2 |
| `DataTypesUtil` | Utilitário para conversão de tipos de dados |
| `DateAdapter` / `DateTimeAdapter` | Adaptadores JAXB para conversão de datas |

## 3. Tecnologias Utilizadas

- **Java EE 6/7**: EJB 3.1, JMS, JAX-WS, JAX-RS, CDI
- **Servidor de Aplicação**: IBM WebSphere Application Server (WAS)
- **Framework de Persistência**: Spring JDBC (para execução de queries e stored procedures)
- **Banco de Dados**: Oracle (via JDBC)
- **Mensageria**: JMS (IBM MQ)
- **Build**: Maven 3.x
- **Logging**: SLF4J com Log4j2
- **Testes**: JUnit 4, Mockito, PowerMock
- **Binding XML**: JAXB 2.x
- **Arquitetura Base**: Framework proprietário Votorantim (fjee-base, arqt-base)
- **Versionamento**: Git

## 4. Principais Endpoints REST

não se aplica

(O sistema possui módulos RS e WS configurados, mas não há implementação de endpoints REST ou Web Services nos arquivos fornecidos)

## 5. Principais Regras de Negócio

1. **Validação de Título**: Antes de cancelar a baixa operacional, o sistema verifica se o título existe na base DDA através do número de identificação do título
2. **Cancelamento Condicional**: O cancelamento só é executado se o título for localizado (cdTitulo diferente de null e zero)
3. **Logging de Título Não Localizado**: Quando o título não é encontrado, o sistema registra log informativo sem gerar erro
4. **Retry em Caso de Erro**: Em caso de BusinessException, o sistema marca a transação para rollback, permitindo reprocessamento da mensagem JMS
5. **Controle de Tentativas**: O sistema conta e registra o número de tentativas de processamento da mensagem
6. **Conversão de Mensagens**: Suporta conversão tanto de TextMessage quanto BytesMessage do JMS
7. **Segurança**: Utiliza role "intr-middleware" com RunAs para execução dos componentes

## 6. Relação entre Entidades

**Entidade Principal:**
- `DebitoDiretoAutorizadoDDA0115R2Mensagem`: Representa a mensagem de cancelamento de baixa operacional DDA

**Relacionamentos:**
- A mensagem contém informações sobre o título (numeroIdentificacaoTitulo) que é usado para localizar o registro no banco
- O sistema busca o código interno do título (CdTituloDDA) através do número de identificação
- Não há relacionamentos JPA/ORM tradicionais, pois o sistema utiliza Spring JDBC e stored procedures

**Estrutura da Mensagem DDA0115R2:**
- Código da mensagem
- ISPBs (participante principal e administrado)
- Número de controle DDA
- Número de identificação do título
- Data/hora de cancelamento
- Valores e situações do título

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| DBPGF_TES..TbTituloDDA | Tabela | SELECT | Tabela de títulos DDA, consultada para buscar o código interno do título através do número de identificação |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| DBPGF_TES (via stored procedure) | Schema | EXEC PROCEDURE | Execução da stored procedure `PrCancelarTituloDDABaixaOperacional` que realiza o cancelamento da baixa operacional |

**Parâmetros da Stored Procedure:**
- NumIdentcBaixaOperac (NUMERIC)
- DtHrCanceltBaixaOperac (DATE)
- CdTitulo (INTEGER)
- Valor (NUMERIC)
- SitTitPgto (INTEGER)

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| log4j2.xml | Leitura | Configuração de logging | Arquivo de configuração do Log4j2 para definição de appenders e níveis de log |
| errorMessages.properties | Leitura | commons/src/main/resources | Arquivo de mensagens de erro do sistema |
| roles.properties | Leitura | commons/src/main/resources | Definição de roles de segurança da aplicação |
| CancelarBaixaOperacionalDAOImpl-sql.xml | Leitura | Persistence layer | Arquivo XML contendo queries SQL utilizadas pelo DAO |
| DebitoDiretoAutorizadoDDA0115R2Mensagem.xsd | Leitura | Domain layer | Schema XSD para validação e geração de classes JAXB da mensagem DDA |

## 10. Filas Lidas

**Fila de Entrada:**
- **Nome**: `queue/PGFTCancelamentoBaixaTituloDdaQueue`
- **Activation Spec**: `as/PGFTCancelamentoBaixaTituloDdaAS`
- **Consumidor**: `CancelarBaixaOperacional` (Message-Driven Bean)
- **Formato**: Mensagens XML no padrão DDA0115R2 (TextMessage ou BytesMessage)
- **Descrição**: Fila que recebe mensagens de cancelamento de baixa operacional de títulos DDA

## 11. Filas Geradas

não se aplica

(O sistema não publica mensagens em filas, apenas consome)

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Banco de Dados Oracle (DBPGF_TES) | JDBC | Integração com banco de dados Oracle para consulta e atualização de títulos DDA via DataSource `jdbc/PgftCobrancaDDADS` |
| Sistema DDA (Débito Direto Autorizado) | JMS | Recebe mensagens de cancelamento de baixa operacional através de fila JMS |
| Framework Votorantim (fjee-base) | Biblioteca | Utiliza componentes de arquitetura base para trilha de auditoria, handlers, segurança e persistência |

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades em camadas (JMS, Business, Persistence, Domain)
- Uso adequado de injeção de dependências (CDI)
- Tratamento de exceções com logging detalhado
- Testes unitários presentes com uso de mocks
- Configuração adequada de segurança com roles
- Uso de stored procedures para operações críticas de banco

**Pontos Negativos:**
- Logging excessivo e verboso em blocos catch (printStackTrace no System.out)
- Variável `contador` no MDB não é thread-safe e não tem utilidade prática
- Falta de validação de dados de entrada antes do processamento
- Comentários de código desabilitado (módulo RS comentado)
- Mistura de português e inglês em nomes de variáveis e comentários
- Falta de constantes para strings literais (nomes de filas, datasources)
- Tratamento genérico de Exception em alguns pontos
- Código de teste com dependências desnecessárias (JFixture não utilizado adequadamente)
- Falta de documentação JavaDoc nas classes principais

## 14. Observações Relevantes

1. **Arquitetura Multi-módulo**: O projeto segue uma estrutura Maven multi-módulo bem organizada (commons, domain, persistence, business, jms, ws, rs, ear, integration)

2. **Framework Proprietário**: O sistema depende fortemente de frameworks proprietários do Banco Votorantim (fjee-base, arqt-base), o que pode dificultar manutenção por equipes externas

3. **Versionamento**: Versão atual do sistema é 19.9.1.P1883-1.9, sugerindo um sistema maduro em produção

4. **Ambiente IBM**: Configurado especificamente para IBM WebSphere Application Server com bindings e extensões específicas

5. **Trilha de Auditoria**: Sistema integrado com framework de trilha de auditoria através de handlers (CapturadorTrilhaInbound/Outbound)

6. **Segurança**: Implementa autenticação básica e controle de acesso baseado em roles

7. **Módulos Não Utilizados**: Os módulos WS (Web Services) e RS (REST) estão configurados mas não possuem implementações efetivas

8. **Padrão de Mensagem**: Utiliza padrão DDA0115R2 específico do sistema de Débito Direto Autorizado brasileiro

9. **Resiliência**: Implementa mecanismo de retry através do rollback de transações JMS

10. **Build e Deploy**: Configurado para deploy via Jenkins com propriedades específicas (jenkins.properties)