# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de processamento de instruções de boletos DDA (Débito Direto Autorizado) desenvolvido em Java EE. O sistema consome mensagens JMS contendo instruções de alteração de títulos DDA provenientes da CIP (Câmara Interbancária de Pagamentos), processa as informações e atualiza a base de dados de cobrança DDA. O componente é responsável por receber mensagens XML no formato DDA0102R2, deserializá-las e executar operações de atualização em diversas tabelas relacionadas a títulos, beneficiários, pagadores, juros, multas, descontos e notas fiscais.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `AlterarTituloDDA` | MDB (Message Driven Bean) que consome mensagens da fila JMS e orquestra o processamento |
| `AlterarTituloBean` | EJB Stateless que contém a lógica de negócio para alteração de títulos |
| `AlterarTituloDAOImpl` | Implementação do DAO responsável por todas as operações de persistência |
| `AlterarTituloDAO` | Interface do DAO com métodos de acesso a dados |
| `ConverterUtil` | Utilitário para conversão de mensagens JMS e deserialização XML |
| `Titulo` | Entidade de domínio representando um título DDA |
| `DebitoDiretoAutorizadoDDA0102R2Mensagem` | Classe gerada via JAXB representando a mensagem XML completa |
| `DataTypesUtil` | Utilitário para conversão de tipos de dados (XMLGregorianCalendar, BigDecimal, etc) |
| `TituloMapper` | RowMapper do Spring JDBC para mapear ResultSet em objetos Titulo |
| Stored Procedures (diversas) | Classes que encapsulam chamadas a procedures do banco de dados |

---

## 3. Tecnologias Utilizadas

- **Java EE 6/7** (EJB 3.1, JMS, JAX-WS, JAX-RS, CDI)
- **IBM WebSphere Application Server** (servidor de aplicação)
- **Maven** (gerenciamento de dependências e build)
- **Spring JDBC** (acesso a dados)
- **JAXB** (binding XML/Java)
- **JMS** (Java Message Service para mensageria)
- **Sybase/SQL Server** (banco de dados - DBPGF_TES)
- **SLF4J/Log4j2** (logging)
- **JUnit, Mockito, PowerMock** (testes unitários)
- **Swagger** (documentação de APIs REST)
- **Oracle JDBC Driver** (mencionado nas dependências)

---

## 4. Principais Endpoints REST

não se aplica

(O sistema possui módulos REST configurados - `rs` - mas não foram fornecidos os arquivos de implementação dos endpoints. Apenas as classes de configuração base foram incluídas: `BaseAppConfig`, `SecurityAppConfig` e `UtilsAppConfig`)

---

## 5. Principais Regras de Negócio

1. **Validação de Título Existente**: Antes de processar alterações, o sistema busca o título na base pelo número de identificação. Se não encontrado, a operação é ignorada.

2. **Cancelamento de Baixas em Alterações Críticas**: Quando um título que aceita pagamento parcial sofre alteração em valor, data de vencimento ou data limite de pagamento, todas as baixas operacionais ativas são desativadas e os contadores de pagamento parcial são zerados.

3. **Pagamento Parcial**: Títulos com quantidade de parcelas maior que zero aceitam pagamento parcial. A lógica verifica se houve mudanças significativas que invalidam pagamentos parciais já registrados.

4. **Indicadores de Manutenção**: O sistema respeita indicadores que determinam se dados devem ser atualizados ('A'), excluídos ('E') ou mantidos. Isso se aplica a beneficiários, pagadores, juros, multas, descontos e notas fiscais.

5. **Exclusão e Reinserção**: Para juros, multas, descontos e notas fiscais, quando o indicador é 'A' (atualizar), o sistema primeiro exclui todos os registros existentes e depois insere os novos.

6. **Cálculos**: Os cálculos de valores (juros, multas, descontos) são sempre recalculados, excluindo os anteriores e inserindo os novos.

7. **Rollback em Erro**: Em caso de exceção durante o processamento, o MDB executa `setRollbackOnly()` para garantir que a mensagem seja reprocessada.

---

## 6. Relação entre Entidades

**Entidade Principal:**
- `TbTituloDDA` (Título DDA)

**Entidades Relacionadas (1:N ou 1:1):**
- `TbBeneficiarioOriginalDDA` - Beneficiário original do título
- `TbBeneficiarioFinalDDA` - Beneficiário final do título
- `TbPagadorDDA` - Pagador do título
- `TbSacadorAvalistaDDA` - Sacador/Avalista do título
- `TbDocumentoTituloDDA` - Documentos relacionados ao título
- `TbInstrucaoPagamentoTituloDDA` - Instruções de pagamento
- `TbInstrucaoValorRecebimentoDDA` - Instruções de valor de recebimento
- `TbJurosTituloDDA` - Juros do título (múltiplos registros possíveis)
- `TbMultaTituloDDA` - Multas do título (múltiplos registros possíveis)
- `TbDescontoTituloDDA` - Descontos do título (múltiplos registros possíveis)
- `TbCalculoTituloDDA` - Cálculos do título (múltiplos registros possíveis)
- `TbNotaFiscalTituloDDA` - Notas fiscais relacionadas (múltiplos registros possíveis)
- `TbTituloDDABaixaOperacional` - Baixas operacionais do título

**Relacionamento:** A entidade `TbTituloDDA` é identificada por `CdTituloDDA` (código interno) e `NuIdentificacaoTitulo` (número de identificação externo). Todas as demais entidades se relacionam através de chaves estrangeiras para esses campos.

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbTituloDDA | tabela | SELECT | Busca informações do título DDA por número de identificação para validação e comparação de alterações |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbTituloDDA | tabela | UPDATE | Atualização dos dados principais do título (via procedure PrAtualizarTitulosDda) |
| TbBeneficiarioOriginalDDA | tabela | UPDATE | Atualização dos dados do beneficiário original (via procedure PrAtualizarBeneficiarioOriginalDda) |
| TbBeneficiarioFinalDDA | tabela | UPDATE | Atualização dos dados do beneficiário final (via procedure PrAtualizarBeneficiarioFinalDda) |
| TbPagadorDDA | tabela | UPDATE | Atualização dos dados do pagador (via procedure PrAtualizarPagadorDda) |
| TbSacadorAvalistaDDA | tabela | UPDATE | Atualização dos dados do sacador/avalista (via procedure PrAtualizarSacadorAvalistaDda) |
| TbDocumentoTituloDDA | tabela | UPDATE | Atualização dos documentos do título (via procedure PrAtualizarDocTituloDda) |
| TbInstrucaoPagamentoTituloDDA | tabela | UPDATE | Atualização das instruções de pagamento (via procedure PrAtualizarInstrucaoPagamentoTituloDda) |
| TbInstrucaoValorRecebimentoDDA | tabela | UPDATE | Atualização das instruções de valor de recebimento (via procedure PrAtualizarInstrucaoValorRecebimentoDda) |
| TbJurosTituloDDA | tabela | DELETE/INSERT | Exclusão e inserção de juros do título (via procedures PrExcluirJurosTitulosDda e PrInserirJurosTitulosDda) |
| TbMultaTituloDDA | tabela | DELETE/INSERT | Exclusão e inserção de multas do título (via procedures PrExcluirMultaTitulosDda e PrInserirMultaTitulosDda) |
| TbDescontoTituloDDA | tabela | DELETE/INSERT | Exclusão e inserção de descontos do título (via procedures PrExcluirDescontoTitulosDda e PrInserirDescontoTitulosDda) |
| TbCalculoTituloDDA | tabela | DELETE/INSERT | Exclusão e inserção de cálculos do título (via procedures PrExcluirCalculoTitulosDda e PrInserirCalculoTitulosDda) |
| TbNotaFiscalTituloDDA | tabela | DELETE/INSERT | Exclusão e inserção de notas fiscais (via procedures PrExcluirNotaFiscalTitulosDda e PrInserirNotaFiscalTitulosDda) |
| TbTituloDDABaixaOperacional | tabela | UPDATE | Desativação de baixas operacionais quando há alteração crítica no título (FlAtivo = 'N') |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|--------------------------|-----------------|
| AlterarTituloDAOImpl-sql.xml | leitura | AlterarTituloDAOImpl | Arquivo XML contendo queries SQL parametrizadas para busca de títulos e desativação de baixas |
| DebitoDiretoAutorizadoDDA0102R2Mensagem.xsd | leitura | Domain (build time) | Schema XSD usado pelo JAXB para gerar classes de domínio da mensagem DDA |
| errorMessages.properties | leitura | Commons | Arquivo de propriedades com mensagens de erro do sistema |
| roles.properties | leitura | Commons | Arquivo de propriedades com definição de roles de segurança |

---

## 10. Filas Lidas

- **queue/PGFTInstrucaoTituloClienteDdaCipQueue**: Fila JMS da qual o MDB `AlterarTituloDDA` consome mensagens XML contendo instruções de alteração de títulos DDA provenientes da CIP. A fila está configurada com Activation Spec `as/PGFTInstrucaoTituloClienteDdaCipAS` no WebSphere.

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

- **CIP (Câmara Interbancária de Pagamentos)**: Sistema externo que envia mensagens de instrução de boletos DDA através da fila JMS. O formato da mensagem segue o padrão DDA0102R2 definido pela CIP.

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada em camadas (JMS, Business, Persistence, Domain)
- Uso adequado de padrões Java EE (EJB, MDB, CDI)
- Separação clara de responsabilidades entre camadas
- Uso de Spring JDBC para acesso a dados
- Implementação de testes unitários
- Uso de JAXB para binding XML/Java
- Tratamento de exceções com rollback em MDB

**Pontos Negativos:**
- **Código procedural excessivo**: A classe `AlterarTituloDAOImpl` possui métodos muito longos com lógica repetitiva (ex: métodos de atualização seguem sempre o mesmo padrão)
- **Falta de abstração**: Muita duplicação de código nos métodos de exclusão/inserção (juros, multas, descontos, notas fiscais)
- **Tratamento de exceções genérico**: Captura de `Exception` genérica em vários pontos, dificultando diagnóstico
- **Logging inadequado**: Uso de `printStackTrace` e logs excessivos que poluem a saída
- **Acoplamento com banco de dados**: Uso intensivo de stored procedures dificulta portabilidade e testes
- **Falta de validações**: Pouca validação de dados de entrada antes do processamento
- **Nomenclatura inconsistente**: Mistura de português e inglês nos nomes de variáveis e métodos
- **Comentários ausentes**: Falta de documentação JavaDoc nas classes principais
- **Contador não utilizado**: Variável `contador` no MDB é incrementada mas não tem utilidade prática

---

## 14. Observações Relevantes

1. **Banco de Dados**: O sistema utiliza Sybase/SQL Server (schema DBPGF_TES) e faz uso extensivo de stored procedures para todas as operações de escrita.

2. **Segurança**: O sistema utiliza autenticação BASIC e role `intr-middleware` para controle de acesso aos componentes EJB e JMS.

3. **Reprocessamento**: O MDB está configurado para reprocessar mensagens em caso de erro (através de `setRollbackOnly()`), com controle de tentativas via propriedade `JMSXDeliveryCount`.

4. **Handlers JAX-WS**: O sistema possui configuração de handlers para trilha de auditoria e tratamento de falhas em serviços SOAP, embora não haja implementação de Web Services no código fornecido.

5. **Módulo REST comentado**: O módulo REST (`rs`) está comentado no `application.xml` do EAR, indicando que não está em uso atualmente.

6. **Dependências de Arquitetura**: O sistema depende fortemente de bibliotecas customizadas do Banco Votorantim (`fjee-base-commons`, `arqt-base-lib`) para funcionalidades de infraestrutura.

7. **Classloader**: O EAR está configurado com `PARENT_LAST` classloader mode, indicando que as bibliotecas da aplicação têm precedência sobre as do servidor.

8. **DataSource JNDI**: O sistema utiliza o DataSource `jdbc/PgftCobrancaDDADS` configurado no WebSphere para acesso ao banco de dados.