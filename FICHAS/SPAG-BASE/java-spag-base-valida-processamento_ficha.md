# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **java-spag-base-valida-processamento** é um componente de validação de processamento de pagamentos de boletos bancários. Sua principal função é validar dados retornados pela CIP (Câmara Interbancária de Pagamentos), calcular valores de juros, multas e descontos, e verificar se os valores de pagamento estão corretos conforme as regras de negócio estabelecidas. O sistema atua como uma camada de validação intermediária entre o sistema de pagamentos e a CIP, garantindo a integridade dos dados antes da efetivação dos pagamentos.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ValidaProcessamentoApi** | Endpoint REST que expõe serviços de validação de boletos e valores de pagamento |
| **ValidaRetornoCipFacade** | Facade para validação dos dados retornados pela CIP (situação, beneficiário) |
| **ValidaValoresCipFacade** | Facade para validação de valores de pagamento, cálculo de juros, multas e descontos |
| **CalculoBoletoBusinessImpl** | Implementação das regras de negócio para cálculo de valores de boletos |
| **CalculoJurosHelper** | Helper para cálculo de juros sobre boletos vencidos |
| **CalculoMultaHelper** | Helper para cálculo de multas sobre boletos vencidos |
| **CalculoDescontoHelper** | Helper para cálculo de descontos aplicáveis aos boletos |
| **BoletoPagamentoHelper** | Utilitários para manipulação de dados de boletos |
| **FeriadoDAO/FeriadoDAOImpl** | Acesso a dados de feriados para cálculo de dias úteis |
| **DtSpagCalcPagUtil** | Utilitários para cálculos de datas e prazos |
| **CalculoND2** | Enum com estratégias de cálculo de juros (dias corridos, dias úteis, percentuais) |

## 3. Tecnologias Utilizadas

- **Java EE 7** (EJB 3.1, JAX-RS, CDI)
- **Maven** (gerenciamento de dependências e build)
- **IBM WebSphere Application Server** (servidor de aplicação)
- **Spring JDBC** (acesso a dados)
- **Oracle Database** (banco de dados via JDBC)
- **Apache Commons Lang3** (utilitários)
- **SLF4J/Log4j2** (logging)
- **Swagger** (documentação de APIs REST)
- **JUnit, Mockito, PowerMock** (testes unitários)

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /spag-base-valida-processamento-rs/v1/atacado/pagamentos/boletos/validarBoleto/ | ValidaProcessamentoApi | Valida dados do boleto retornados pela CIP (situação, beneficiário) |
| POST | /spag-base-valida-processamento-rs/v1/atacado/pagamentos/valores/validarValorPagamento/ | ValidaProcessamentoApi | Valida valores de pagamento, calcula juros, multas e descontos |

## 5. Principais Regras de Negócio

- **Validação de Situação do Boleto**: Boleto deve estar em situação "05" (Em análise emissora), "11" (Em análise outra emissora) ou "12" (Cliente beneficiário apto)
- **Validação de Beneficiário**: Para boletos acima de R$ 250.000,00, valida se o beneficiário corresponde ao cadastrado na CIP
- **Validação de Data Limite**: Verifica se a data de pagamento não excede a data limite permitida
- **Cálculo de Juros**: Calcula juros sobre boletos vencidos conforme código de cálculo (dias corridos, dias úteis, percentuais diversos)
- **Cálculo de Multa**: Calcula multa sobre boletos vencidos (valor fixo ou percentual)
- **Cálculo de Desconto**: Calcula descontos aplicáveis dentro do prazo de validade
- **Validação de Pagamento Parcial**: Verifica se o boleto permite pagamento parcial e se o valor está dentro dos limites permitidos
- **Validação de Pagamento Divergente**: Verifica se o valor divergente está dentro das regras estabelecidas (tipos 1 a 4)
- **Validação de Boleto Vencido em Contingência**: Durante contingência da CIP, não permite pagamento de boletos vencidos
- **Cálculo de Dias Úteis**: Considera feriados nacionais e dias não úteis para cálculos de prazos

## 6. Relação entre Entidades

- **DicionarioPagamento**: Entidade central que contém todos os dados do pagamento
  - Contém **BoletoPagamentoCompletoDTO**: dados completos do boleto retornados pela CIP
    - Contém **ListaJurosTitulo**: lista de configurações de juros
    - Contém **ListaMultaTitulo**: lista de configurações de multa
    - Contém **ListaDescontoTitulo**: lista de configurações de desconto
    - Contém **ListaCalculoTitulo**: lista de valores calculados pela instituição financeira
    - Contém **ListaBaixaOperacional** e **ListaBaixaEfetiva**: baixas já realizadas no boleto
  - Contém **ListaOcorrencia**: lista de erros/validações encontradas
- **FeriadoDTO**: representa um feriado cadastrado no sistema
- **Request/Response/Service**: estruturas para requisição e resposta dos serviços REST

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBGLOBAL..TbFeriado | Tabela | SELECT | Consulta feriados para cálculo de dias úteis |

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema não realiza operações de INSERT, UPDATE ou DELETE em banco de dados.

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| FeriadoDAOImpl-sql.xml | Leitura | FeriadoDAOImpl | Arquivo XML contendo queries SQL para consulta de feriados |
| errorMessages.properties | Leitura | commons/resources | Arquivo de propriedades com mensagens de erro do sistema |
| roles.properties | Leitura | commons/resources | Arquivo de propriedades com definição de roles de segurança |

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas.

## 12. Integrações Externas

- **CIP (Câmara Interbancária de Pagamentos)**: O sistema valida dados retornados pela CIP através do objeto `BoletoPagamentoCompletoDTO` que é recebido como entrada nos serviços. Não há chamada direta à CIP neste componente, apenas validação dos dados já consultados.
- **Banco de Dados Oracle (DBGLOBAL)**: Consulta tabela de feriados via DataSource JNDI `jdbc/sitpBaseDbItpDS`
- **Stored Procedures**: 
  - `DBGLOBAL..PrVerificaDataUtil`: verifica se uma data é dia útil
  - `DBGLOBAL..PrProximoDiaUtil`: retorna o próximo dia útil a partir de uma data

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades em camadas (API, Facade, Business, DAO, Helpers)
- Uso adequado de padrões como Strategy (CalculoND2), Facade e DAO
- Código bem documentado com JavaDoc em pontos-chave
- Uso de injeção de dependências (CDI/EJB)
- Tratamento de exceções e logging adequados
- Testes unitários presentes (embora não enviados para análise)

**Pontos de Melhoria:**
- Métodos muito extensos em algumas classes (ex: `validarValorPagamentoBoleto` com mais de 100 linhas)
- Lógica de negócio complexa concentrada em poucas classes (ValidaValoresCipFacade)
- Uso excessivo de Strings literais para comparações (poderia usar enums)
- Alguns métodos privados muito longos que poderiam ser refatorados
- Falta de constantes para valores mágicos (ex: "0.05" para tolerância de valores)
- Comentários em português misturados com código em inglês
- Algumas validações poderiam ser extraídas para classes especializadas
- Código com algumas duplicações que poderiam ser eliminadas

## 14. Observações Relevantes

- O sistema utiliza **autenticação BASIC** para os endpoints REST
- Implementa **trilha de auditoria** através de filtros (InicializadorContextoRequisicao, CapturadorTrilhaInbound)
- Possui **segurança declarativa** com anotações `@DeclareRoles` e `@RolesAllowed`
- Utiliza **transações NOT_SUPPORTED** nos EJBs, indicando que não gerencia transações próprias
- O sistema trabalha com **tolerância de R$ 0,05** para comparações de valores monetários
- Implementa **10 estratégias diferentes** de cálculo de juros (CalculoND2 enum)
- Possui **contingência para CIP**: quando a CIP está indisponível, apenas boletos não vencidos são aceitos
- O cálculo de dias úteis considera **feriados das praças 1, 2 e 16**
- Sistema preparado para **paginação** (estrutura presente mas não utilizada nos endpoints atuais)
- Documentação Swagger configurada mas não gerada por padrão (execução comentada no pom.xml)