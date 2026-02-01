# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **java-flex-inbv-solicitacao-boleto-avulso** é uma aplicação Java EE voltada para a solicitação de boletos avulsos de financiamento. Permite que usuários solicitem a geração de boletos avulsos para contratos de financiamento, com opções de envio por e-mail ou SMS. O sistema registra as solicitações em banco de dados, incluindo informações sobre parcelas quando aplicável, e retorna um código de solicitação para rastreamento.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **SolicitacaoBoletoAvulsoBeanImpl** | EJB Stateless que implementa a lógica de negócio principal para solicitação de boletos avulsos |
| **BoletoFinanciamentoFlexBackendServiceEndpoint** | Endpoint do Web Service SOAP que expõe a operação de solicitação de boleto avulso |
| **SolicitacaoBoletoAvulsoDaoImpl** | DAO responsável pela persistência de solicitações de boleto no banco de dados |
| **BoletoAvulsoDmnsoParcelaDaoImpl** | DAO responsável pela persistência de parcelas associadas às solicitações |
| **SolicitacaoBoletoValidateImpl** | Implementa validações de negócio para os dados da solicitação |
| **SolicitaBoletoAvulsoMapperImpl** | Converte objetos de requisição SOAP em objetos de domínio |
| **FaultBuilderImpl** | Constrói objetos de falha (fault) padronizados para retorno em caso de erro |
| **ResponseBuilderImpl** | Constrói respostas padronizadas de sucesso |
| **SolicitacaoBoletoAvulso** | Entidade de domínio representando uma solicitação de boleto avulso |
| **BoletoAvulsoDmnsoParcela** | Entidade de domínio representando parcelas de uma solicitação |

---

## 3. Tecnologias Utilizadas

- **Java EE 6+** (EJB 3.1, JAX-WS, CDI)
- **Maven** (gerenciamento de dependências e build)
- **JAX-WS** (Web Services SOAP)
- **Spring JDBC** (acesso a dados)
- **IBM WebSphere Application Server** (servidor de aplicação)
- **Oracle Database** (banco de dados - JDBC)
- **Log4j2 / SLF4J** (logging)
- **JUnit / Mockito / PowerMock** (testes unitários)
- **Apache Commons Lang3**
- **JAXB** (binding XML)

---

## 4. Principais Endpoints REST

não se aplica

---

## 5. Principais Regras de Negócio

1. **Validação de Tipo de Envio**: O tipo de envio deve ser "10" (e-mail) ou "25" (SMS)
2. **Validação de E-mail**: Quando tipo de envio é e-mail, valida formato do endereço eletrônico
3. **Validação de SMS**: Quando tipo de envio é SMS, valida DDD (mínimo 2 dígitos, não pode ser zeros) e número de celular (não pode ser vazio ou apenas zeros)
4. **Validação de Nosso Número**: Deve conter apenas dígitos numéricos
5. **Persistência Transacional**: Solicitações com parcelas são salvas em transação única (solicitação + parcelas)
6. **Geração de Código de Solicitação**: Retorna ID gerado automaticamente pelo banco de dados
7. **Flag de Status**: Solicitações são criadas com status "A" (aguardando) e flag ativo "S"
8. **Auditoria**: Registra login do usuário, data de inclusão e alteração

---

## 6. Relação entre Entidades

**SolicitacaoBoletoAvulso** (1) ----< (N) **BoletoAvulsoDmnsoParcela**

- Uma solicitação de boleto avulso pode ter zero ou várias parcelas associadas
- A relação é estabelecida através do campo `cdSolicitacaoBoletoAvulso` na entidade `BoletoAvulsoDmnsoParcela`
- Ambas as entidades possuem campos de auditoria (login, flAtivo, dtInclusao, dtAlteracao)

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBFLEX..TbSolicitacaoBoletoAvulso | tabela | INSERT | Armazena as solicitações de boleto avulso com dados do contrato, tipo de envio, contato e flags de controle |
| DBFLEX..TbBoletoAvulsoDmnsoParcela | tabela | INSERT | Armazena as parcelas específicas associadas a uma solicitação de boleto avulso |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| *-sql.xml | leitura | BaseDaoImpl / ArquivoQueries | Arquivos XML contendo queries SQL parametrizadas para operações de persistência |
| errorMessages.properties | leitura | commons/resources | Arquivo de propriedades contendo mensagens de erro do sistema |
| roles.properties | leitura | commons/resources | Arquivo de propriedades contendo definição de roles de segurança |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

O sistema expõe um Web Service SOAP mas não consome serviços externos. A integração é de entrada (inbound):

- **BoletoFinanciamentoFlexBackendService**: Web Service SOAP que recebe solicitações de boleto avulso de sistemas clientes
- **Segurança**: Utiliza WS-Security com UsernameToken (classificação baixa/média) ou Certificate (classificação alta)
- **Handlers**: Implementa handlers para trilha de auditoria, captura de contexto e tratamento de falhas

---

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades em camadas (WS, Business, DAO, Domain)
- Uso adequado de padrões Java EE (EJB, CDI, JAX-WS)
- Implementação de validações de negócio centralizadas
- Uso de builders para padronização de respostas e falhas
- Testes unitários implementados para validações
- Queries SQL externalizadas em arquivos XML
- Tratamento de transações adequado

**Pontos de Melhoria:**
- Código hardcoded: `model.setNuNossoNumero("324324353")` no mapper (deveria vir da requisição)
- Falta de documentação JavaDoc nas classes
- Validações poderiam usar Bean Validation (JSR-303) ao invés de implementação manual
- Uso de `PreparedStatement` manual ao invés de frameworks ORM mais modernos
- Falta de logs estruturados em pontos críticos
- Exceções genéricas em alguns pontos (catch Exception)
- Poderia utilizar mais recursos do Spring (está usando apenas Spring JDBC)

---

## 14. Observações Relevantes

1. **Ambiente IBM WebSphere**: O sistema é específico para WebSphere Application Server, com configurações IBM proprietárias (ibm-ejb-jar-bnd.xml, ibm-web-bnd.xml, etc.)

2. **Segurança**: Implementa controle de acesso baseado em roles ("intr-middleware") com grupos específicos por ambiente (DES, QA, UAT, PRD)

3. **Múltiplos Ambientes**: Possui WSDLs específicos para cada ambiente (DES, QA, UAT, PRD) com URLs diferentes

4. **Trilha de Auditoria**: Implementa handlers customizados para captura de trilha de auditoria em todas as requisições SOAP

5. **Arquitetura Modular**: Projeto Maven multi-módulo bem estruturado (commons, domain, persistence, business, ws, ear)

6. **DataSource JNDI**: Utiliza lookup JNDI `jdbc/flexBaseDBFLEX` para acesso ao banco de dados

7. **Transações Declarativas**: Usa anotações EJB para controle transacional (`@TransactionAttribute`)

8. **Versionamento**: Sistema versionado (v1) permitindo evolução futura da API

9. **Classloader**: Configuração específica de classloader com modo PARENT_LAST e bibliotecas compartilhadas (arqt-base-lib, fjee-base-lib)

10. **Código de Solicitação**: O sistema retorna um código numérico único gerado pelo banco de dados para rastreamento da solicitação