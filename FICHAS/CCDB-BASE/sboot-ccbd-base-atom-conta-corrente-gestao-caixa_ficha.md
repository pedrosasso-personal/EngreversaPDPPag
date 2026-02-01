# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de gestão de conta corrente e caixa do Banco Votorantim (CCBD - Centro Corporativo de Banco de Dados). Trata-se de um serviço atômico REST que fornece consultas e operações relacionadas a saldos de contas correntes, históricos, variações e lançamentos, segmentados por clientes, fundos, veículos e nomes. O sistema realiza consultas em banco de dados Sybase e oferece endpoints para visualização de informações consolidadas e analíticas de movimentações financeiras.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot que inicializa a aplicação |
| `ContaCorrenteGestaoCaixaController` | Controlador REST que expõe os endpoints da API |
| `ContaCorrenteGestaoCaixaService` | Camada de serviço que implementa a lógica de negócio |
| `JdbiContaCorrenteGestaoCaixaRepository` | Interface de repositório JDBI para acesso ao banco de dados |
| `ContaCorrenteGestaoCaixaConfiguration` | Configuração de beans e dependências do Spring |
| `GlobalExceptionHandler` | Tratamento centralizado de exceções da aplicação |
| `AppPropertiesController` | Controlador para exposição de propriedades da aplicação (apenas ambientes não produtivos) |
| Classes de domínio (`CCHistoricoCliente`, `CCTotalCliente`, etc.) | Entidades de domínio representando os dados de negócio |
| Classes Mapper | Conversão entre entidades de domínio e representações REST |
| Classes RowMapper | Mapeamento de ResultSet JDBC para objetos de domínio |

---

## 3. Tecnologias Utilizadas

- **Framework Principal**: Spring Boot 2.x
- **Linguagem**: Java 11
- **Banco de Dados**: Sybase ASE (via driver JDBC jconn4 16.3-SP03-PL07)
- **Acesso a Dados**: JDBI 3.9.1 (SQL Object API)
- **Documentação API**: Swagger/OpenAPI 3.0.0 (Springfox)
- **Segurança**: Spring Security OAuth2 (JWT) - sboot-arqt-base-security 0.22.3
- **Monitoramento**: Spring Boot Actuator + Micrometer + Prometheus
- **Visualização**: Grafana (configuração incluída)
- **Auditoria**: springboot-arqt-base-trilha-auditoria-web 2.3.3
- **Build**: Maven
- **Containerização**: Docker
- **Testes**: JUnit 5, Mockito, Rest Assured, Pact (contract testing)
- **Logging**: Logback com formato JSON

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/conta-corrente-gestao-caixa/getCCHistoricoClientes` | `ContaCorrenteGestaoCaixaController` | Retorna histórico de saldos de clientes por data |
| GET | `/v1/conta-corrente-gestao-caixa/getCCHistoricoClientesCredor` | `ContaCorrenteGestaoCaixaController` | Retorna histórico de saldos de clientes credores |
| GET | `/v1/conta-corrente-gestao-caixa/getCCHistoricoFundos` | `ContaCorrenteGestaoCaixaController` | Retorna histórico de saldos de fundos |
| GET | `/v1/conta-corrente-gestao-caixa/getCCHistoricoNomes` | `ContaCorrenteGestaoCaixaController` | Retorna histórico de saldos por nome/pessoa |
| GET | `/v1/conta-corrente-gestao-caixa/getCCHistoricoVeiculos` | `ContaCorrenteGestaoCaixaController` | Retorna histórico de saldos de veículos |
| GET | `/v1/conta-corrente-gestao-caixa/getCCTotalClientes` | `ContaCorrenteGestaoCaixaController` | Retorna totais consolidados de clientes |
| GET | `/v1/conta-corrente-gestao-caixa/getCCTotalClientesAnalitico` | `ContaCorrenteGestaoCaixaController` | Retorna totais analíticos de clientes (detalhado) |
| GET | `/v1/conta-corrente-gestao-caixa/getCCTotalClientesCredor` | `ContaCorrenteGestaoCaixaController` | Retorna totais de clientes credores |
| GET | `/v1/conta-corrente-gestao-caixa/getCCTotalFundos` | `ContaCorrenteGestaoCaixaController` | Retorna totais consolidados de fundos |
| GET | `/v1/conta-corrente-gestao-caixa/getCCTotalFundosAnalitico` | `ContaCorrenteGestaoCaixaController` | Retorna totais analíticos de fundos |
| GET | `/v1/conta-corrente-gestao-caixa/getCCTotalNomes` | `ContaCorrenteGestaoCaixaController` | Retorna totais por nome/pessoa |
| GET | `/v1/conta-corrente-gestao-caixa/getCCTotalNomesAnalitico` | `ContaCorrenteGestaoCaixaController` | Retorna totais analíticos por nome (com filtro opcional por cdPessoa) |
| GET | `/v1/conta-corrente-gestao-caixa/getCCTotalVeiculos` | `ContaCorrenteGestaoCaixaController` | Retorna totais de veículos |
| GET | `/v1/conta-corrente-gestao-caixa/getCCVariacao` | `ContaCorrenteGestaoCaixaController` | Retorna variação de saldos entre datas |
| GET | `/v1/conta-corrente-gestao-caixa/getCCVariacaoAnalitico` | `ContaCorrenteGestaoCaixaController` | Retorna variação analítica de saldos |
| GET | `/v1/conta-corrente-gestao-caixa/getLancamentosNCC` | `ContaCorrenteGestaoCaixaController` | Retorna lançamentos NCC (Nota de Crédito Corrente) por data |
| POST | `/v1/conta-corrente-gestao-caixa/inserirTempAgrupContaCorrente` | `ContaCorrenteGestaoCaixaController` | Insere dados temporários de agrupamento |
| GET | `/v1/conta-corrente-gestao-caixa/getTempAgrupContaCorrente` | `ContaCorrenteGestaoCaixaController` | Consulta dados temporários de agrupamento |
| POST | `/v1/conta-corrente-gestao-caixa/excluirTempAgrupContaCorrente` | `ContaCorrenteGestaoCaixaController` | Exclui dados temporários de agrupamento |
| GET | `/v1/app-properties` | `AppPropertiesController` | Retorna propriedades da aplicação (apenas ambientes não produtivos) |

---

## 5. Principais Regras de Negócio

1. **Filtragem de Pessoas Específicas**: Códigos de pessoa 3221, 3083, 14273, 1505830, 1505829 e 9097448 são filtrados e não aparecem nos resultados de histórico de nomes (implementado nos Mappers para otimização de performance).

2. **Cálculo de Dia Útil Anterior**: Para consultas de variação, quando a data de apuração é igual à data atual, o sistema busca automaticamente o dia útil anterior através da procedure `bv_pegautil`.

3. **Separação de Dados Históricos e Correntes**: Lançamentos NCC são consultados em tabelas diferentes dependendo se a data é atual (`TbMovimentoDia`) ou histórica (`TbHistoricoMovimento`).

4. **Exclusão de Empresas BV**: Consultas excluem contas onde `CdPessoa = 839` e aplicam filtros específicos baseados em flags da tabela `TBEMPRESABV` (FlIndicadorFundo, FlAtivo, FlVeiculoLegal).

5. **Agrupamento Temporário**: Sistema permite inserção e consulta de dados temporários de agrupamento com controle por token (`dsControleConsulta`), com limpeza automática de dados antigos.

6. **Saldos Positivos**: Várias consultas filtram apenas saldos com valores diferentes de zero ou maiores que zero, dependendo do contexto.

7. **Isolamento de Transação**: Queries executadas com `AT ISOLATION 0` (read uncommitted) para melhor performance em consultas.

---

## 6. Relação entre Entidades

**Entidades Principais de Domínio:**

- **CCHistoricoCliente/ClienteCredor/Fundo/Nome/Veiculo**: Representam históricos de saldos por categoria
  - Atributos: dtApuracao, vrDisponivel, nmConta, cdPessoa (quando aplicável)

- **CCTotalCliente/ClienteCredor/Fundo/Nome/Veiculo**: Representam totais consolidados por categoria
  - Atributos: vrSaldoTotalDisponivel, vrSaldoInicioDiaDisponivel, nmConta

- **CCTotalClienteAnalitico/FundoAnalitico/NomesAnalitico**: Versões detalhadas dos totais
  - Atributos adicionais: cdPessoa, nmPessoa, nuContaCorrente, nuCpfCnpj

- **CCVariacao/CCVariacaoAnalitico**: Representam variações de saldos entre períodos
  - Atributos: dtApuracaoSaldo, vrSaldoTotalDisponivel, dados da pessoa (na versão analítica)

- **LancamentoNCC**: Lançamentos de Nota de Crédito Corrente
  - Atributos: nuOrigemOperacao, cdLiquidacao, nmContaOrigem, nmLiquidacao, vrLancamento

- **TempAgrupCC**: Dados temporários de agrupamento
  - Atributos: vrMovimentoDiaVigente, vrMovimentoDiaAnterior, nmCliente, cdPessoa, tpRetorno, dsControleConsulta

**Relacionamentos:**
- Todas as entidades se relacionam com dados de contas correntes do banco Sybase
- Entidades analíticas são extensões das entidades consolidadas com mais detalhes
- TempAgrupCC é uma entidade auxiliar para processamento temporário

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| `DBCONTACORRENTE..TbConta` | Tabela | SELECT | Dados de contas correntes |
| `DBCONTACORRENTE..TbHistoricoSaldo` | Tabela | SELECT | Histórico de saldos das contas |
| `DBCONTACORRENTE..TbMovimentoDia` | Tabela | SELECT | Movimentações do dia corrente |
| `DBCONTACORRENTE..TbHistoricoMovimento` | Tabela | SELECT | Histórico de movimentações |
| `DBCONTACORRENTE..VwContaCorrente` | View | SELECT | View de contas correntes |
| `DBGLOBAL..TbContaRelacionamento` | Tabela | SELECT | Relacionamento de contas |
| `DBGLOBAL..TbPessoaTitularidade` | Tabela | SELECT | Titularidade de pessoas nas contas |
| `DBGLOBAL..TbPessoa` | Tabela | SELECT | Dados cadastrais de pessoas |
| `DBGLOBAL..TBEMPRESABV` | Tabela | SELECT | Dados de empresas do grupo BV |
| `DBGLOBAL..TbPessoaJuridica` | Tabela | SELECT | Dados de pessoas jurídicas |
| `DBGLOBAL..TbTipoTitularFgcCnae` | Tabela | SELECT | Tipos de titulares e CNAEs |
| `DBCAIXA..TbTempAgrupamentoContaCorrente` | Tabela | SELECT | Tabela temporária de agrupamento |
| `DBPGF..bv_next_dres` | Procedure | EXEC | Calcula próxima data útil |
| `DBPGF..bv_pegautil` | Procedure | EXEC | Obtém dia útil anterior |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| `DBCAIXA..TbTempAgrupamentoContaCorrente` | Tabela | INSERT | Inserção de dados temporários de agrupamento |
| `DBCAIXA..TbTempAgrupamentoContaCorrente` | Tabela | DELETE | Exclusão de dados temporários antigos (limpeza por data) |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `logback-spring.xml` | Leitura | Configuração de logging | Arquivo de configuração de logs (JSON format) |
| `application.yml` | Leitura | Spring Boot | Configurações da aplicação por ambiente |
| Arquivos SQL (*.sql) | Leitura | `JdbiContaCorrenteGestaoCaixaRepository` | Queries SQL carregadas via classpath |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| API Gateway BV | OAuth2/JWT | Validação de tokens JWT através do endpoint jwks.json para autenticação e autorização |
| Banco de Dados Sybase | JDBC | Conexão com múltiplos databases (DBCONTACORRENTE, DBGLOBAL, DBCAIXA, DBPGF) |
| Prometheus | Métricas | Exportação de métricas da aplicação via `/actuator/prometheus` |
| Grafana | Visualização | Dashboard de monitoramento (configuração incluída no projeto) |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem organizada seguindo padrões hexagonais (ports/adapters)
- Separação clara entre camadas (domain, application, presentation)
- Uso adequado de JDBI para acesso a dados
- Boa cobertura de testes unitários
- Documentação Swagger bem implementada
- Uso de Lombok reduzindo boilerplate
- Configuração adequada de profiles Spring
- Implementação de tratamento de exceções centralizado

**Pontos de Melhoria:**
- Queries SQL muito complexas e extensas embutidas em arquivos separados (dificulta manutenção)
- Lógica de negócio (filtros de cdPessoa) implementada nos Mappers ao invés de estar no Service
- Comentários em português misturados com código
- Alguns hardcodes de valores (ex: conta 10524771, transação 1546)
- Falta de validação de entrada em alguns endpoints
- Uso de `AT ISOLATION 0` pode causar leituras inconsistentes
- Código de teste com alguns mocks muito simples
- Ausência de DTOs específicos (usa mesma classe para domínio e representação em alguns casos)

---

## 14. Observações Relevantes

1. **Ambientes**: Sistema configurado para múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas de banco de dados e segurança.

2. **Performance**: Comentários no código indicam que filtros foram movidos de procedures para código Java para melhorar performance.

3. **Segurança**: Autenticação OAuth2 habilitada, com endpoints públicos apenas para actuator e swagger.

4. **Monitoramento**: Infraestrutura completa de observabilidade com Prometheus e Grafana pré-configurados.

5. **Deployment**: Preparado para deploy em OpenShift (Google Cloud Platform) com configurações de infra-as-code.

6. **Dados Sensíveis**: Sistema trabalha com dados financeiros sensíveis (saldos, CPF/CNPJ, contas correntes).

7. **Tabela Temporária**: Uso de tabela temporária (`TbTempAgrupamentoContaCorrente`) para processamento intermediário com controle por token.

8. **Datas**: Sistema trabalha com datas em múltiplos formatos (LocalDate, String "dd/MM/yyyy", "yyyy-MM-dd") - atenção para conversões.

9. **Isolation Level**: Queries executadas com isolation level 0 (read uncommitted) para melhor performance, mas pode retornar dados inconsistentes.

10. **Versão**: Projeto na versão 0.31.0, indicando maturidade moderada.