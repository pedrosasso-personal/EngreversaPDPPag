# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de processamento batch desenvolvido em Spring Batch para gestão de saldos de contas correntes. O sistema realiza a consolidação de informações de contas correntes provenientes de diferentes bases de dados (BCO, SPB e GLOBAL), processando dados de clientes, fundos, veículos e variações de saldo. Os dados são agregados e armazenados em tabelas temporárias para posterior consulta por sistemas front-end.

O sistema opera em dois modos principais:
- **Modo Legado**: Processa dados sintéticos do BCO (clientes credores, fundos, nomes/veículos e variações)
- **Modo Global**: Processa dados analíticos de contas de fundos e veículos do banco GLOBAL, consultando saldos via API REST

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `SpringBatchApplication` | Classe principal da aplicação Spring Boot |
| `JobOrchestrator` | Orquestra a execução dos jobs batch com base em parâmetros de linha de comando |
| `JobBatch` | Configura os jobs legados (jobSetUpTemporary e jobSetUpFinal) |
| `JobContaGlobal` | Configura os jobs de processamento de contas do GLOBAL |
| `CCConfiguration` | Configuração central de beans (DataSources, Repositórios, Serviços, Clientes REST) |
| `DataSourceConfig` | Configuração dos três DataSources (SPB, BCO, GLOBAL) |
| `CCTempService` | Processa e consolida dados temporários com totalizadores |
| `CCVariacaoService` | Processa variações de saldo de contas correntes |
| `CCTotalClienteCredorService` | Processa totais de clientes credores |
| `CCTotalFundoService` | Processa totais de fundos |
| `CCTotalNomeService` | Processa totais por nome/veículo |
| `ContaVeiculoService` | Processa contas de veículos do GLOBAL |
| `ContaFundoService` | Processa contas de fundos do GLOBAL |
| `DatabaseSaldoResponseHandler` | Trata respostas da API de saldo e persiste na base temporária |
| `SaldoApiClient` | Cliente REST para consulta de saldos |
| `BalancesApiClient` | Cliente REST para consulta de balances (contas especiais) |
| `ContaEspecialService` | Gerencia cache de contas especiais que requerem consulta diferenciada |

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x**
- **Spring Batch** - Framework de processamento batch
- **JDBI 3** - Framework de acesso a dados SQL
- **Sybase ASE (jConnect 16.3)** - Banco de dados principal
- **Maven 3.5.3+** - Gerenciamento de dependências
- **Lombok 1.18.20+** - Redução de código boilerplate
- **Spring Security OAuth2** - Autenticação via OAuth2 Client Credentials
- **Logback** - Framework de logging
- **JUnit 5 (Jupiter)** - Testes unitários
- **Docker** - Containerização
- **Kubernetes** - Orquestração (arquivos de configuração presentes)

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch que não expõe endpoints REST próprios. Ele consome endpoints externos:

- **API de Saldo**: `{baseUrl}/consultarSaldoContaCorrente` (POST)
- **API de Balances**: `{baseUrl}/digital-bank/{banco}/balances` (GET)

## 5. Principais Regras de Negócio

1. **Exclusão de Contas Específicas**: Códigos de pessoa 3083, 14273, 1505830, 1505829 e 9097448 são excluídos do processamento
2. **Processamento de Variações**: Quando há múltiplos registros de variação, o segundo é usado como saldo vigente e o primeiro como saldo anterior
3. **Totalizadores**: O sistema calcula totais gerais, parciais por tipo (clientes, fundos, veículos) e linhas individuais
4. **Controle de Execução**: Utiliza campo `DsControleConsulta` com timestamp (formato DDMMAAAAhhmmss) para controlar processamentos
5. **Tipos de Retorno**: 
   - 'T' = Total (amarelo no front)
   - 'P' = Parcial (azul no front)
   - 'L' = Linha (branco no front)
   - 'C' = Cliente, 'F' = Fundo, 'N' = Nome/Veículo, 'V' = Variação
   - 'U' = Fundo (Global), 'E' = Veículo (Global)
6. **Contas Especiais**: Contas com tipo 5 ou 6 são tratadas de forma diferenciada, consultando API de balances
7. **Saldo Anterior**: Sistema busca último processamento anterior para calcular variação de saldo
8. **Limpeza de Temporários**: Remove registros temporários com mais de 30 dias ou de processamentos incompletos
9. **Formatação de Agência**: Agências são formatadas com 4 dígitos, preenchidas com zeros à esquerda
10. **Truncamento de Nomes**: Nomes de clientes são limitados a 100 caracteres

## 6. Relação entre Entidades

**Entidades Principais:**

- **ContaGlobal**: Representa contas do banco GLOBAL (fundos e veículos)
  - Atributos: indicador, cdPessoa, nmApelido, nuCpfCnpj, cdBanco

- **CCTemp**: Registro temporário de saldo
  - Atributos: vrValorMovimentoDiaVigente, vrMovimentoDiaAnterior, nmCliente, cdPessoa, tpRetorno, dsControleConsulta

- **CCVariacao**: Variação de saldo por data
  - Atributos: dtApuracao, vrDisponivel

- **CCTotalClienteCredor**: Total de clientes credores
  - Atributos: vrSaldoTotalDisponivel, vrSaldoInicioDiaDisponivel, nmConta

- **CCTotalFundo**: Total de fundos
  - Atributos: vrSaldoTotalDisponivel, vrSaldoInicioDiaDisponivel, nmConta

- **CCTotalNome**: Total por nome/pessoa
  - Atributos: vrSaldoTotalDisponivel, vrSaldoInicioDiaDisponivel, nmPessoa, cdPessoa

- **ContaEspecialDTO**: Conta que requer tratamento especial
  - Atributos: banco, agencia, conta

**Relacionamentos:**
- Todas as entidades convergem para a tabela temporária `TbTempAgrupamentoContaCorrente`
- ContaGlobal é consultada no DBGLOBAL e seus saldos são buscados via API REST
- CCTemp é a entidade central que armazena todos os tipos de saldo processados

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBGLOBAL..TBEMPRESABV | tabela | SELECT | Empresas BV (fundos e veículos) |
| DBGLOBAL..TbPessoaTitularidade | tabela | SELECT | Titularidade de pessoas |
| DBGLOBAL..TbPessoa | tabela | SELECT | Dados cadastrais de pessoas |
| DBGLOBAL..TbContaRelacionamento | tabela | SELECT | Relacionamento de contas |
| DBCONTACORRENTE..TbConta | tabela | SELECT | Contas correntes |
| DBCONTACORRENTE..TbHistoricoSaldo | tabela | SELECT | Histórico de saldos |
| DBGLOBAL..TbPessoaJuridica | tabela | SELECT | Dados de pessoas jurídicas |
| DBGLOBAL..TbTipoTitularFGCCNAE | tabela | SELECT | Tipos de titular por CNAE |
| DBCAIXA..TbTempAgrupamentoContaCorrente | tabela | SELECT | Registros temporários de saldo (leitura para processamento) |
| DBCAIXA..TbParametrosGestaoCaixa | tabela | SELECT | Parâmetros de controle (DsControleConsultaAtual) |
| DBPGF..bv_pegautil | procedure | EXEC | Busca último dia útil |
| DBPGF..bv_next_dres | procedure | EXEC | Calcula próxima data de resolução |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBCAIXA..TbTempAgrupamentoContaCorrente | tabela | INSERT | Inserção de registros temporários de saldo |
| DBCAIXA..TbTempAgrupamentoContaCorrente | tabela | DELETE | Limpeza de registros temporários antigos ou incompletos |
| DBCAIXA..TbTempAgrupamentoContaCorrente | tabela | UPDATE | Atualização do campo DsControleConsulta |
| DBCAIXA..TbParametrosGestaoCaixa | tabela | UPDATE | Atualização do DsControleConsultaAtual |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot / resources | Configurações da aplicação (datasources, URLs de API, credenciais) |
| logback-spring.xml | leitura | Logback / resources | Configuração de logging |
| *.sql (resources) | leitura | JDBI / repositories | Queries SQL para operações de banco de dados |

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas.

## 12. Integrações Externas

| Sistema/API | Descrição | Método de Integração |
|-------------|-----------|---------------------|
| API Gateway OAuth2 | Autenticação via Client Credentials | REST (OAuth2RestTemplate) |
| sboot-ccbd-base-orch-saldo | Consulta de saldos de contas correntes | REST POST - endpoint `/consultarSaldoContaCorrente` |
| sboot-ccbd-base-orch-saldo | Consulta de balances para contas especiais | REST GET - endpoint `/digital-bank/{banco}/balances` |
| Sybase ASE (DBCONTACORRENTE - SPB) | Banco de dados de contas correntes SPB | JDBC/JDBI |
| Sybase ASE (DBCONTACORRENTE - BCO) | Banco de dados de contas correntes BCO | JDBC/JDBI |
| Sybase ASE (DBGLOBAL) | Banco de dados global de cadastros | JDBC/JDBI |

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões Spring Batch
- Separação clara de responsabilidades (config, domain, dto, service, repository)
- Uso adequado de interfaces e abstrações
- Boa utilização de Lombok para reduzir boilerplate
- Logging bem implementado com níveis apropriados
- Tratamento de exceções customizado
- Uso de JDBI para queries SQL externalizadas
- Configuração externalizada em application.yml
- Testes unitários presentes
- Documentação inline em pontos críticos

**Pontos de Melhoria:**
- Algumas classes de serviço com lógica complexa que poderiam ser refatoradas (ex: `DatabaseSaldoResponseHandler` com método de 200+ linhas)
- Uso de constantes "magic strings" em alguns pontos (ex: "99999999999999", "88888888888888")
- Falta de documentação JavaDoc em algumas classes públicas
- Alguns métodos privados longos que poderiam ser quebrados em métodos menores
- Tratamento de erros poderia ser mais granular em alguns pontos
- Falta de validação de entrada em alguns métodos públicos

## 14. Observações Relevantes

1. **Dois Modos de Operação**: O sistema pode ser executado em modo legado (sem parâmetros) ou modo global (com `--runGlobalJob`), processando diferentes conjuntos de dados

2. **Controle Temporal**: Utiliza campo `DsControleConsulta` com formato DDMMAAAAhhmmss para controlar execuções e evitar reprocessamento

3. **Tabela Temporária Compartilhada**: A tabela `TbTempAgrupamentoContaCorrente` é usada tanto para dados sintéticos (BCO) quanto analíticos (GLOBAL), diferenciados pelo campo `TpRetorno`

4. **Processamento Paralelo**: Utiliza `SimpleAsyncTaskExecutor` para executar steps em paralelo, melhorando performance

5. **Cache de Contas Especiais**: Sistema mantém cache em memória de contas especiais para evitar consultas repetidas ao banco

6. **Limpeza Automática**: Remove automaticamente registros temporários com mais de 30 dias

7. **Múltiplos DataSources**: Conecta-se a três bancos Sybase distintos (SPB, BCO, GLOBAL) com configurações independentes

8. **Integração com Front-end**: Os valores de `TpRetorno` ('T', 'P', 'L') são usados pelo front-end para colorir linhas da tabela (amarelo, azul, branco)

9. **Tratamento de Contas Especiais**: Contas com tipo 5 ou 6 são consultadas em API separada (balances) e podem gerar múltiplos registros

10. **Histórico de Saldo**: Sistema busca saldo do dia anterior para calcular variações, usando a última `DsControleConsulta` anterior à data atual

11. **Containerização**: Projeto preparado para execução em containers Docker e orquestração Kubernetes

12. **Ambientes Múltiplos**: Suporta configurações para ambientes local, des, qa, uat e prd