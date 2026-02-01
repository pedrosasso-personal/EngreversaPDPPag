# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema Java EE para processamento de baixa de parcelas de contratos financeiros do sistema Flex. A aplicação recebe mensagens via fila JMS contendo informações de pagamento de parcelas, processa a baixa integrando-se com o sistema Flexcube (Oracle FCUBS) via SOAP, calcula descontos aplicáveis (mora, multa, juros e principal), valida o tipo de baixa (antecipada ou normal) e persiste logs de processamento em banco de dados. O sistema atua como middleware de integração entre sistemas legados e o core bancário Flexcube.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **BaixaParcelaFlexMDB** | Message-Driven Bean que escuta a fila JMS e orquestra o processamento de baixa de parcelas |
| **BaixaParcelaServiceImpl** | Serviço principal que coordena a lógica de negócio de baixa de parcelas, incluindo mapeamento de domínios e determinação do tipo de baixa |
| **BaixaParcelaConsumerImpl** | Consumer responsável pela integração com Flexcube, realizando consultas e modificações de pagamentos manuais |
| **ContratoFinanceiroConsumerImpl** | Consumer para consulta de informações de contratos e parcelas via serviços SOAP |
| **MapeamentoDominioConsumerImpl** | Consumer para buscar mapeamentos de domínios técnicos necessários ao processamento |
| **BaixaParcelaMapperImpl** | Mapper que converte mensagens JMS em objetos de requisição e log |
| **LogProcessamentoDaoImpl** | DAO para persistência de logs de processamento em banco de dados |
| **LogProcessamento** | Entidade de domínio representando o log de processamento de baixa |
| **Parcela** | Entidade de domínio para cálculos de valores de parcela e descontos |
| **MensagemBaixaParcelaSender** | Componente para envio de mensagens de teste para a fila de baixa de parcelas |

---

## 3. Tecnologias Utilizadas

- **Java EE 7+** (EJB 3.x, JMS 2.0)
- **IBM WebSphere Application Server (WAS)**
- **JAX-WS** (Web Services SOAP)
- **JAXB** (XML Binding)
- **JAX-RS** (REST API)
- **Spring JDBC** (JdbcTemplate, NamedParameterJdbcTemplate)
- **IBM MQ** (JMS Provider - inferido)
- **Oracle Flexcube (FCUBS)** - Sistema core bancário
- **Oracle Database** (inferido pelo uso de Flexcube)
- **Maven** (Build e gerenciamento de dependências)
- **Log4j2** (Logging)
- **Swagger** (Documentação API REST)
- **arqt-base-lib 1.0.19** (Biblioteca base arquitetura)
- **fjee-base-lib 1.1.10** (Biblioteca base Java EE)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| N/A | /api/* | BaseAppConfig | Configuração base da API REST com Swagger (tags: clientes, credito) |
| N/A | /api-security/* | SecurityAppConfig | Endpoints de autenticação e autorização via SecurityRestApi |
| N/A | /api-utils/* | UtilsAppConfig | Endpoints utilitários de log via LogRestApi |
| GET | /TestServlet | TestServlet | Servlet de teste para envio de mensagens à fila de baixa de parcelas |

**Observação:** A aplicação é primariamente orientada a mensageria (JMS), com endpoints REST secundários para testes e utilitários.

---

## 5. Principais Regras de Negócio

1. **Determinação do Tipo de Baixa**: Compara a data de pagamento com a data de vencimento da parcela para classificar como baixa antecipada (ANTE) ou normal (NORM)

2. **Cálculo de Descontos**: Aplica descontos em ordem específica: mora, multa, principal e juros, baseado na diferença entre valores pagos e valores devidos

3. **Validação de Valores**: Valida que descontos calculados não sejam negativos, ajustando para casos de pagamento maior ou menor que o devido

4. **Mapeamento de Domínios**: Extrai código do agente recebedor a partir de mapeamento de domínios técnicos (interface BAIXA-PARCELA)

5. **Remoção de Zeros à Esquerda**: Normaliza códigos e identificadores removendo zeros à esquerda antes do processamento

6. **Integração com Flexcube**: Realiza sequência de operações: QueryContractSummary → QueryManualPymntNPV → ModifyManualPymntNPV → ModifyManualPymntNPVFS

7. **Persistência de Log**: Registra todas as tentativas de processamento com status (S=Sucesso, E=Erro) e detalhes de retorno

8. **Auditoria**: Adiciona informações de auditoria (ticket, sistema, usuário, IP) nos headers SOAP das chamadas aos serviços

---

## 6. Relação entre Entidades

**LogProcessamento** (Entidade Principal de Log)
- Contém: número do contrato, sequência financeira, número da parcela, data de vencimento
- Relaciona-se com: código do veículo legal, código do convênio, código do agente recebedor
- Armazena: valores recebidos, valores da parcela, descontos aplicados, tarifas baixadas
- Status: flag de processamento (S/E), código e descrição de retorno

**Parcela** (Entidade de Cálculo)
- Composição de valores: total, multa, mora, juros, principal
- Descontos aplicados: desconto de multa, mora, juros e principal
- Valor para descontar: montante a ser aplicado como desconto

**ParcelaDTO** (Transferência de Dados)
- Identificação: número do contrato, número da parcela
- Temporal: data de vencimento

**BaixarParcelaRequest** (Requisição de Baixa)
- Dados do contrato: número, sequência financeira, parcela
- Dados de pagamento: valores, datas, agente recebedor, convênio
- Tipo de baixa: antecipada ou normal

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| N/A | N/A | N/A | Sistema não realiza leituras diretas de banco de dados. Consultas são realizadas via serviços SOAP (Flexcube, ContratoFinanceiro) |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbLogProcessamento | Tabela | INSERT | Tabela de log de processamento de baixa de parcelas. Armazena dados do contrato, parcela, valores recebidos/devidos, descontos aplicados, status de processamento e códigos de retorno |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| LogProcessamentoDaoImpl-sql.xml | Leitura | BaseDaoImpl / ArquivoQueries | Arquivo XML contendo queries SQL para operações de persistência de log |
| errorMessages.properties | Leitura | Configuração | Arquivo de mensagens de erro da aplicação |
| roles.properties | Leitura | Configuração | Arquivo de configuração de roles de segurança (flex-integracao, intr-middleware) |
| log4j2.xml | Leitura | Configuração | Arquivo de configuração do framework de logging |
| beans.xml | Leitura | Configuração CDI | Arquivo de configuração de beans CDI |
| ejb-jar.xml | Leitura | Configuração EJB | Arquivo de configuração de EJBs |
| ibm-ejb-jar-bnd.xml | Leitura | Configuração WAS | Arquivo de binding de EJBs para WebSphere |
| web.xml | Leitura | Configuração Web | Arquivo de configuração da aplicação web |

---

## 10. Filas Lidas

**Fila JMS Consumida:**
- **Nome:** FLEXBaixaParcela (queue/baixaParcela)
- **Connection Factory:** jms/baixaParcelaCF
- **Formato:** XML (ParcelasMensagem / BaixaParcelaMensagemType)
- **Consumidor:** BaixaParcelaFlexMDB
- **Roles Necessárias:** flex-integracao, intr-middleware
- **Tipos de Mensagem:** BytesMessage, TextMessage
- **Descrição:** Fila que recebe mensagens contendo dados de pagamento de parcelas para processamento de baixa

---

## 11. Filas Geradas

**Fila JMS Produzida:**
- **Nome:** queue/baixaParcela
- **Connection Factory:** jms/baixaParcelaCF
- **Formato:** XML (ParcelasMensagem)
- **Produtor:** MensagemBaixaParcelaSender
- **Descrição:** Fila utilizada para envio de mensagens de teste de baixa de parcelas (via TestServlet)

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **Oracle Flexcube (FCUBS)** | SOAP/Web Service | Sistema core bancário. Operações: QueryContractSummary, QueryInstallment, QueryManualPymntNPV, ModifyManualPymntNPV, ModifyManualPymntNPVFS. Endpoint via JNDI: FLEX_ORACLE_SERVICE_ENDPOINT |
| **ContratoFinanceiroFlexBusinessService** | SOAP/Web Service | Serviço para consulta de parcelas de contratos financeiros. Operações: consultarParcelas |
| **MapeamentoDominiosTechinicalService** | SOAP/Web Service | Serviço para consulta de mapeamentos de domínios técnicos. Busca domínio FLEX, interface BAIXA-PARCELA |
| **ParcelasFlexBusinessService** | SOAP/Web Service | Serviço de negócio para operações com parcelas (geração de stubs via JAX-WS) |
| **Banco de Dados Oracle** | JDBC | Persistência de logs via DataSource: jdbc/flexBaseDBFLEX |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades em camadas (MDB, Service, Consumer, DAO)
- Uso adequado de padrões de projeto (DTO, Mapper, Consumer, Exception customizadas)
- Tratamento de exceções estruturado com classes específicas
- Uso de utilitários para operações comuns (DateUtil, StringUtil, CollectionUtil)
- Logging estruturado com handlers SOAP customizados
- Configuração externalizada (XML, properties)
- Uso de injeção de dependências e interfaces

**Pontos de Melhoria:**
- Lógica de negócio complexa concentrada em BaixaParcelaConsumerImpl (cálculo de descontos poderia ser extraído)
- Falta de documentação JavaDoc nas classes principais
- Uso de reflection em alguns utilitários (FaultUtil, CollectionUtil) pode impactar performance
- Código de teste misturado com código de produção (TestServlet, MensagemBaixaParcelaSender)
- Falta de testes unitários evidentes na estrutura apresentada
- Algumas classes com múltiplas responsabilidades (ex: BaixaParcelaConsumerImpl faz consulta, cálculo e modificação)
- Uso de Singleton em conversores pode causar problemas de concorrência

O código demonstra maturidade arquitetural e boas práticas de integração enterprise, mas poderia se beneficiar de maior modularização da lógica de negócio e melhor cobertura de testes.

---

## 14. Observações Relevantes

1. **Arquitetura Multi-Módulo Maven**: Projeto estruturado em módulos (commons, domain, persistence, integration, business, jms, rs, ear) facilitando manutenção e reuso

2. **Geração Automática de Stubs**: Utiliza plugin JAX-WS Maven para gerar stubs de serviços SOAP a partir de WSDLs, garantindo sincronização com contratos de serviço

3. **Trilha de Auditoria**: Sistema implementa filtros web customizados (InicializadorContextoRequisicao, CapturadorTrilhaInbound) para captura de trilha de auditoria

4. **Segurança**: Autenticação BASIC configurada, roles específicas para acesso (flex-integracao, intr-middleware)

5. **Lookup JNDI**: Uso de NameSpaceBindingEnum e NameSpaceBindingUtil para centralizar lookups JNDI de recursos (DataSources, endpoints)

6. **Conversão XML**: Uso de JAXB com conversores singleton (MensagemRetornoConverter, MensagemSenderConverter) para marshal/unmarshal de mensagens

7. **Configuração WAS**: Plugin arqt-wascontroller no POM para setup automatizado de datasources Oracle e filas no WebSphere

8. **Dados Sensíveis**: Sistema processa informações financeiras sensíveis (valores de parcelas, descontos, pagamentos)

9. **Usuário Técnico**: Operações executadas com usuário técnico MDB_BAIXA_PARCELA_USER

10. **Timezone**: Utilitários incluem ajuste de timezone para datas, indicando processamento potencialmente multi-regional

11. **Swagger Habilitado**: API REST documentada com Swagger, facilitando integração e testes

12. **Dependências de Bibliotecas Base**: Uso de bibliotecas corporativas (arqt-base-lib, fjee-base-lib) sugere padrões arquiteturais organizacionais estabelecidos