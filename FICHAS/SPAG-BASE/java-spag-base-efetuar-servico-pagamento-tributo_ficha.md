# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **java-spag-base-efetuar-servico-pagamento-tributo** é um componente de pagamentos de tributos que atua como orquestrador entre sistemas internos e a plataforma IS2B (Itaú). Sua principal função é efetuar pagamentos de tributos e concessionárias, realizando a integração com o sistema IS2B através de chamadas HTTP, persistindo informações de autenticação bancária e atualizando o status dos lançamentos e lotes de pagamento no banco de dados.

O sistema recebe requisições via API REST, valida os parâmetros, efetua o pagamento através da integração com outro componente (java-spag-base-efetuar-pagamento-tributo-consumo), trata os retornos da IS2B (incluindo cenários de sucesso, erro e retry), atualiza as tabelas de controle e retorna o resultado da operação.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **EfetuarServicoPagamentoTributoBean** | Bean EJB principal que orquestra o fluxo de efetuação de pagamento, chamando a IS2B e atualizando o banco de dados |
| **EfetuarServicoPagamentoTributo** (REST) | Endpoint REST que expõe o serviço de efetuação de pagamento via HTTP |
| **EfetuarServicoPagamentoDAOImpl** | Implementação DAO responsável por operações de banco de dados (consulta de protocolo, atualização de lançamentos e lotes) |
| **EfetuarIntegrationServices** | Classe de integração que realiza chamadas HTTP para os serviços de efetuação e confirmação de pagamento |
| **HttpCaapiIntegration** | Classe abstrata base para integrações HTTP, gerenciando headers, autenticação e execução de requisições POST |
| **ErrosIS2BEnum** | Enumeração que mapeia códigos de erro da IS2B para códigos de ocorrência internos com mensagens amigáveis |
| **LancamentoRowMapper** | Mapper Spring JDBC para conversão de ResultSet em objetos Lancamento |

---

## 3. Tecnologias Utilizadas

- **Java EE 7 / Jakarta EE** - Plataforma de desenvolvimento
- **EJB 3.1** - Enterprise JavaBeans para lógica de negócio
- **JAX-RS 2.0** - RESTful Web Services
- **CDI (Contexts and Dependency Injection)** - Injeção de dependências
- **Spring JDBC** - Acesso a dados via JDBC
- **Apache HttpClient** - Cliente HTTP para integrações
- **Gson** - Serialização/deserialização JSON
- **IBM WebSphere Application Server** - Servidor de aplicação
- **Maven** - Gerenciamento de dependências e build
- **JUnit / Mockito / PowerMock** - Testes unitários
- **SLF4J / Log4j2** - Logging
- **SQL Server** - Banco de dados (inferido pelos scripts SQL)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /atacado/pagamentos/efetuarServicoPagamento | EfetuarServicoPagamentoTributo | Efetua o pagamento de tributo ou concessionária, validando parâmetros e integrando com IS2B |

---

## 5. Principais Regras de Negócio

1. **Validação de Tipo de Pagamento**: Apenas pagamentos com `cdLiquidacaoITP` igual a 59 ou 60 e `cdParametroPagamentoTributo` igual a 1 são processados
2. **Tratamento de Pagamento Já Efetuado**: Se o código de retorno IS2B for 183 (pagamento já efetuado) ou 621 (pendente confirmação) e já existir protocolo, o sistema considera sucesso
3. **Atualização de Status em Cascata**: Ao atualizar um lançamento, o sistema também atualiza o status do detalhe do fornecedor e do lote de pagamento
4. **Retry em Erros HTTP Específicos**: Em caso de erros 401, 403, 500, 503 ou 504, o sistema tenta reexecutar a requisição uma vez
5. **Mapeamento de Erros IS2B**: Códigos de erro da IS2B são mapeados para códigos de ocorrência internos com mensagens padronizadas
6. **Status de Lote Dinâmico**: O status do lote é calculado com base nos status dos detalhes (acatado, acatado parcialmente ou encerrado)
7. **Registro de Ocorrências**: Erros são registrados como ocorrências no dicionário de pagamento para rastreabilidade

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **Lancamento**: Representa um lançamento de pagamento individual
  - Atributos: CdLancamento (PK), CdAutenticacaoBancaria
  
- **DetalheFornecedorLote**: Detalhe de fornecedor dentro de um lote
  - Relacionamento: N:1 com Lancamento (via CdLancamento)
  - Relacionamento: N:1 com LotePagamentoTributo (via CdLotePagamentoTributo)
  - Atributos: CdStatusDetalheFonecedorLote

- **LotePagamentoTributo**: Lote de pagamentos
  - Relacionamento: 1:N com DetalheFornecedorLote
  - Atributos: CdLotePagamentoTributo (PK), CdStatusLotePagamentoTributo

**Relacionamentos:**
- Um Lançamento pode estar associado a um DetalheFornecedorLote
- Um LotePagamentoTributo contém múltiplos DetalheFornecedorLote
- O status do lote é derivado dos status dos detalhes

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbLancamento | Tabela | SELECT | Consulta o código de autenticação bancária (protocolo IS2B) de um lançamento específico |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbLancamento | Tabela | UPDATE | Atualiza o código de autenticação bancária e data de alteração após efetuação do pagamento |
| TbDetalheFornecedorLote | Tabela | UPDATE | Atualiza o status do detalhe do fornecedor (1=acatado, 99=recusado) e data de alteração |
| TbLotePagamentoTributo | Tabela | UPDATE | Atualiza o status do lote (2=acatado, 3=acatado parcialmente, 99=encerrado) baseado nos status dos detalhes |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| config-spag.properties | Leitura | ConfigSpagBaseProperties | Arquivo de configuração contendo URL do servidor WAS e endpoints da API |
| config-arqt-base.properties | Leitura | ConfigArqtrBaseProperties | Arquivo de configuração de arquitetura com endereços de webservices e API Gateway |
| errorMessages.properties | Leitura | commons/resources | Mensagens de erro padronizadas do sistema |
| EfetuarServicoPagamentoDAOImpl-sql.xml | Leitura | EfetuarServicoPagamentoDAOImpl | Arquivo XML contendo as queries SQL utilizadas pelo DAO |

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas JMS, Kafka ou RabbitMQ.

---

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **java-spag-base-efetuar-pagamento-tributo-consumo** | EJB Remoto | Sistema interno que realiza a integração efetiva com a IS2B para efetuação de pagamentos de tributos |
| **java-spag-base-confirmar-pagamento-tributo-consumo** | REST API | Sistema interno para confirmação de pagamentos de tributos (método presente mas não utilizado no fluxo principal) |
| **IS2B (Itaú)** | Indireta | Plataforma de pagamentos do Itaú, acessada através dos componentes de consumo mencionados acima |

**Observação**: A integração com IS2B é feita de forma indireta através de outros componentes internos, não diretamente por este sistema.

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Separação clara de responsabilidades em camadas (business, persistence, integration, domain, REST)
- Uso adequado de padrões Java EE (EJB, CDI, JAX-RS)
- Tratamento de exceções estruturado com mapeamento de erros
- Presença de testes unitários
- Uso de enums para padronização de códigos de erro
- Logging adequado em pontos críticos

**Pontos Negativos:**
- **Código comentado**: Diversos trechos de código comentado no pom.xml e classes (módulos ws, jms)
- **Tratamento de exceções genérico**: Uso excessivo de `catch (Exception e)` sem tratamento específico
- **Lógica de negócio no REST**: Validação de parâmetros (`cdLiquidacaoITP` e `cdParametroPagamentoTributo`) deveria estar na camada de negócio
- **Métodos longos**: `efetuarServicoPagamento` e `efetuaPagamentoIS2B` poderiam ser refatorados em métodos menores
- **Falta de documentação**: Ausência de JavaDoc em classes e métodos importantes
- **Hardcoded values**: Constantes como códigos de status (99, 59, 60) poderiam estar em enums
- **Conversões desnecessárias**: Múltiplas conversões JSON usando Gson poderiam ser otimizadas
- **Nomenclatura inconsistente**: Mistura de português e inglês em nomes de variáveis e métodos
- **SQL em XML**: Queries SQL complexas em arquivo XML dificultam manutenção e versionamento

---

## 14. Observações Relevantes

1. **Arquitetura Multi-Módulo**: O projeto utiliza uma estrutura Maven multi-módulo bem organizada (business, domain, persistence, integration, rs, ear)

2. **Segurança**: O sistema utiliza autenticação BASIC e roles declarativas (`spag-integracao`, `intr-middleware`)

3. **Transações**: As operações são marcadas como `NOT_SUPPORTED`, indicando que não participam de transações gerenciadas pelo container

4. **Módulos Desabilitados**: Os módulos WS (SOAP) e JMS estão presentes na estrutura mas comentados no EAR, sugerindo que foram desativados

5. **Configuração por Ambiente**: O sistema suporta múltiplos ambientes (DES, QA, UAT, PRD) através de arquivos properties

6. **Dependências Externas**: O sistema depende de bibliotecas internas do Banco Votorantim (fjee-base, arqt-base, spag-base-pagamentos-commons)

7. **Versionamento**: Versão atual 0.9.0 sugere que o sistema está em fase de estabilização pré-release

8. **Retry Mechanism**: Implementa retry automático para erros HTTP específicos, aumentando a resiliência

9. **Auditoria**: Utiliza trilha de auditoria através de handlers JAX-RS e filtros

10. **Status Codes IS2B**: O sistema mapeia 25 códigos de erro diferentes da IS2B, demonstrando maturidade no tratamento de cenários