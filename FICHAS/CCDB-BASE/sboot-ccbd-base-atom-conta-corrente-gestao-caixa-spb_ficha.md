# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de gestão de conta corrente para controle de caixa SPB (Sistema de Pagamentos Brasileiro) do Banco Votorantim. O sistema fornece APIs REST para consulta de saldos, históricos e movimentações de contas correntes de clientes, fundos, veículos e nomes (empresas BV), além de gerenciar agrupamentos temporários de dados para análises específicas.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot que inicializa a aplicação |
| `ContaCorrenteGestaoCaixaSpbController` | Controller REST que expõe os endpoints da API |
| `ContaCorrenteGestaoCaixaSpbService` | Camada de serviço que implementa a lógica de negócio |
| `JdbiCCGestaoCaixaSpbRepository` | Interface de repositório que define operações de banco de dados usando JDBI |
| `ContaCorrenteGestaoCaixaSpbConfiguration` | Configuração do Spring para beans e dependências |
| `GlobalExceptionHandler` | Tratamento centralizado de exceções |
| `AppPropertiesController` | Controller para expor propriedades da aplicação (apenas ambientes não produtivos) |
| Classes de domínio (CCHistorico*, CCTotal*, CCVariacao*, etc.) | Entidades de domínio representando diferentes tipos de consultas |
| Classes Mapper | Conversão entre entidades de domínio e representations (DTOs) |
| Classes RowMapper | Mapeamento de ResultSet do banco para objetos de domínio |

## 3. Tecnologias Utilizadas

- **Framework**: Spring Boot 2.x
- **Linguagem**: Java 11
- **Persistência**: JDBI 3.9.1 (acesso a banco de dados via SQL)
- **Banco de Dados**: Sybase ASE (jConnect 16.3)
- **Documentação API**: Swagger/OpenAPI 3.0 (SpringFox)
- **Segurança**: Spring Security OAuth2 (Resource Server com JWT)
- **Monitoramento**: Spring Actuator + Micrometer + Prometheus
- **Auditoria**: springboot-arqt-base-trilha-auditoria-web 2.3.3
- **Build**: Maven 3.3+
- **Containerização**: Docker
- **Logging**: Logback com formato JSON

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/conta-corrente-gestao-caixa-spb/getCCHistoricoClientes` | ContaCorrenteGestaoCaixaSpbController | Retorna histórico de saldos de clientes |
| GET | `/v1/conta-corrente-gestao-caixa-spb/getCCHistoricoClientesCredor` | ContaCorrenteGestaoCaixaSpbController | Retorna histórico de saldos de clientes credores |
| GET | `/v1/conta-corrente-gestao-caixa-spb/getCCHistoricoFundos` | ContaCorrenteGestaoCaixaSpbController | Retorna histórico de saldos de fundos |
| GET | `/v1/conta-corrente-gestao-caixa-spb/getCCHistoricoNomes` | ContaCorrenteGestaoCaixaSpbController | Retorna histórico de saldos por nome (empresa) |
| GET | `/v1/conta-corrente-gestao-caixa-spb/getCCHistoricoVeiculos` | ContaCorrenteGestaoCaixaSpbController | Retorna histórico de saldos de veículos |
| GET | `/v1/conta-corrente-gestao-caixa-spb/getCCTotalClientes` | ContaCorrenteGestaoCaixaSpbController | Retorna totais consolidados de clientes |
| GET | `/v1/conta-corrente-gestao-caixa-spb/getCCTotalClientesAnalitico` | ContaCorrenteGestaoCaixaSpbController | Retorna totais analíticos de clientes |
| GET | `/v1/conta-corrente-gestao-caixa-spb/getCCTotalClientesCredor` | ContaCorrenteGestaoCaixaSpbController | Retorna totais de clientes credores |
| GET | `/v1/conta-corrente-gestao-caixa-spb/getCCTotalFundos` | ContaCorrenteGestaoCaixaSpbController | Retorna totais consolidados de fundos |
| GET | `/v1/conta-corrente-gestao-caixa-spb/getCCTotalFundosAnalitico` | ContaCorrenteGestaoCaixaSpbController | Retorna totais analíticos de fundos |
| GET | `/v1/conta-corrente-gestao-caixa-spb/getCCTotalNomes` | ContaCorrenteGestaoCaixaSpbController | Retorna totais por nome |
| GET | `/v1/conta-corrente-gestao-caixa-spb/getCCTotalNomesAnalitico` | ContaCorrenteGestaoCaixaSpbController | Retorna totais analíticos por nome (com filtro opcional por cdPessoa) |
| GET | `/v1/conta-corrente-gestao-caixa-spb/getCCTotalVeiculos` | ContaCorrenteGestaoCaixaSpbController | Retorna totais de veículos |
| GET | `/v1/conta-corrente-gestao-caixa-spb/getCCVariacao` | ContaCorrenteGestaoCaixaSpbController | Retorna variação de saldos |
| GET | `/v1/conta-corrente-gestao-caixa-spb/getCCVariacaoAnalitico` | ContaCorrenteGestaoCaixaSpbController | Retorna variação analítica de saldos |
| GET | `/v1/conta-corrente-gestao-caixa-spb/getLancamentosNCC` | ContaCorrenteGestaoCaixaSpbController | Retorna lançamentos NCC (atual ou histórico) |
| POST | `/v1/conta-corrente-gestao-caixa-spb/inserirTempAgrupContaCorrente` | ContaCorrenteGestaoCaixaSpbController | Insere dados temporários de agrupamento |
| GET | `/v1/conta-corrente-gestao-caixa-spb/getTempAgrupContaCorrente` | ContaCorrenteGestaoCaixaSpbController | Consulta dados temporários de agrupamento |
| POST | `/v1/conta-corrente-gestao-caixa-spb/excluirTempAgrupContaCorrente` | ContaCorrenteGestaoCaixaSpbController | Exclui dados temporários de agrupamento |
| GET | `/v1/app-properties` | AppPropertiesController | Retorna propriedades da aplicação (apenas local/des/qa/uat) |

## 5. Principais Regras de Negócio

1. **Filtro de Códigos de Pessoa**: Alguns códigos de pessoa específicos (3221, 3083, 14273, 1505830, 1505829, 9097448) são filtrados e não aparecem nos resultados de histórico e totais de nomes, conforme requisito de negócio.

2. **Cálculo de Dia Útil Anterior**: Para consultas de variação, o sistema calcula automaticamente o dia útil anterior à data de apuração informada, utilizando procedure do banco (bv_pegautil/bv_next_dres).

3. **Separação de Contas**: O sistema separa contas em categorias: Clientes, Clientes Credores, Fundos, Nomes (empresas BV) e Veículos, cada uma com suas regras específicas de filtro.

4. **Exclusão de Contas Encerradas**: Contas com data de encerramento são excluídas dos cálculos de saldo disponível.

5. **Lançamentos NCC**: Diferencia consultas de lançamentos atuais (tabela TbMovimentoDia) de históricos (tabela TbHistoricoMovimento) baseado na data de movimento.

6. **Agrupamento Temporário**: Permite inserção, consulta e exclusão de dados temporários para análises específicas, com controle por token (dsControleConsulta).

7. **Filtro de Banco Digital**: Contas do banco 436 (digital) são identificadas com sufixo "(DIGITAL)" no nome.

## 6. Relação entre Entidades

**Entidades Principais:**

- **CCHistorico[Tipo]**: Representam históricos de saldos por categoria (Cliente, ClienteCredor, Fundo, Nome, Veiculo)
- **CCTotal[Tipo]**: Representam totais consolidados por categoria
- **CCTotal[Tipo]Analitico**: Versões analíticas com detalhamento por conta
- **CCVariacao/CCVariacaoAnalitico**: Representam variações de saldo ao longo do tempo
- **LancamentoNCC**: Representa lançamentos específicos de NCC
- **TempAgrupCC**: Entidade temporária para agrupamentos customizados
- **CCDiaUtilAnterior**: Entidade auxiliar para cálculo de datas úteis

**Relacionamentos:**
- Todas as entidades de domínio são mapeadas a partir de consultas SQL complexas que relacionam tabelas de conta corrente (TbConta, TbHistoricoSaldo, TbMovimentoDia) com tabelas de relacionamento (TbContaRelacionamento, TbPessoaTitularidade) e cadastro (TbPessoa, TbEmpresaBV).

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| DBCONTACORRENTE..TbConta | tabela | SELECT | Tabela principal de contas correntes |
| DBCONTACORRENTE..TbHistoricoSaldo | tabela | SELECT | Histórico de saldos das contas |
| DBCONTACORRENTE..TbMovimentoDia | tabela | SELECT | Movimentações do dia atual |
| DBCONTACORRENTE..TbHistoricoMovimento | tabela | SELECT | Histórico de movimentações |
| DBGLOBAL..TbContaRelacionamento | tabela | SELECT | Relacionamento entre contas e titulares |
| DBGLOBAL..TbPessoaTitularidade | tabela | SELECT | Titularidade de pessoas em contas |
| DBGLOBAL..TbPessoa | tabela | SELECT | Cadastro de pessoas |
| DBGLOBAL..TbEmpresaBV | tabela | SELECT | Cadastro de empresas do grupo BV |
| DBGLOBAL..TbPessoaJuridica | tabela | SELECT | Dados de pessoas jurídicas |
| DBGLOBAL..TbTipoTitularFGCCNAE | tabela | SELECT | Tipos de titulares por CNAE |
| DBCAIXA..TbTempAgrupamentoContaCorrente | tabela | SELECT | Tabela temporária de agrupamentos |
| DBPGF..bv_next_dres | procedure | EXEC | Procedure para cálculo de data útil anterior |
| DBPGF..bv_pegautil | procedure | EXEC | Procedure para cálculo de data útil |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| DBCAIXA..TbTempAgrupamentoContaCorrente | tabela | INSERT | Inserção de dados temporários de agrupamento |
| DBCAIXA..TbTempAgrupamentoContaCorrente | tabela | DELETE | Exclusão de dados temporários antigos |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot | Arquivo de configuração da aplicação |
| logback-spring.xml | leitura | Logback | Configuração de logs |
| *.sql | leitura | JDBI/JdbiCCGestaoCaixaSpbRepository | Arquivos SQL para queries do repositório |

## 10. Filas Lidas

não se aplica

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| API Gateway OAuth2 | Autenticação | Validação de tokens JWT via JWK endpoint configurável por ambiente |
| Prometheus | Monitoramento | Exportação de métricas via Actuator |

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões de Clean Architecture (separação em camadas: domain, application)
- Uso adequado de padrões como Repository, Service, Mapper
- Boa documentação via Swagger/OpenAPI
- Tratamento centralizado de exceções
- Uso de Lombok para reduzir boilerplate
- Testes estruturados (unit, integration, functional)
- Configuração adequada de segurança e monitoramento

**Pontos de Melhoria:**
- Queries SQL muito complexas e extensas embutidas em arquivos .sql, dificultando manutenção
- Lógica de negócio (filtros de códigos de pessoa) implementada em mappers ao invés de serviços
- Comentários em português misturados com código em inglês
- Alguns comentários desnecessários (ex: "sonar 1", "b1", "s1") indicando possíveis correções de análise estática
- Falta de validação de entrada em alguns endpoints
- Código com dependências de valores hardcoded (ex: conta 10524771, códigos de pessoa específicos)
- Ausência de cache para consultas frequentes
- Isolamento de transação configurado como 0 (dirty read) em várias queries

## 14. Observações Relevantes

1. **Ambientes**: O sistema possui configurações específicas para ambientes local, des, qa, uat e prd, com datasources e URLs de autenticação configuráveis.

2. **Segurança**: Implementa OAuth2 Resource Server com validação JWT. Alguns endpoints do Actuator e Swagger são públicos.

3. **Performance**: Utiliza isolation level 0 (dirty read) em várias consultas para melhorar performance, o que pode resultar em leituras inconsistentes.

4. **Auditoria**: Integrado com biblioteca de trilha de auditoria do BV (springboot-arqt-base-trilha-auditoria-web).

5. **Formato de Data**: Utiliza formato dd/MM/yyyy para entrada de datas nos endpoints.

6. **Containerização**: Aplicação preparada para execução em container Docker com imagem base customizada do GCP.

7. **Monitoramento**: Expõe métricas via Prometheus na porta 9090 (separada da porta da aplicação 8080).

8. **Profiles Maven**: Possui profiles específicos para diferentes tipos de teste (unit, integration, functional, architecture).

9. **Limitação de Código**: Alguns códigos de pessoa são filtrados por requisito de negócio, mas essa lógica está implementada nos mappers, não na camada de serviço.

10. **Dados Temporários**: Sistema permite armazenamento temporário de agrupamentos com limpeza automática de dados antigos.