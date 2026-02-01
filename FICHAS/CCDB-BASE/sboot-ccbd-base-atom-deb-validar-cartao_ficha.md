# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema atômico de validação de cartão de débito (Debt Card) desenvolvido em Spring Boot. O sistema consome mensagens de uma fila IBM MQ contendo informações sobre cartões de débito e realiza operações de validação, inserção e atualização no banco de dados SQL Server. Quando um cartão já está cadastrado, o sistema registra um log histórico e atualiza suas informações; caso contrário, realiza um novo cadastro.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application.java` | Classe principal que inicializa a aplicação Spring Boot |
| `CartaoContaListener.java` | Listener JMS que consome mensagens da fila de cartões |
| `CartaoContaService.java` | Serviço de domínio contendo a lógica de negócio para validação de cartões |
| `CartaoContaRepositoryImpl.java` | Implementação do repositório com operações de banco de dados |
| `CartaoConta.java` | Entidade de domínio representando um cartão de débito vinculado a uma conta |
| `CartaoContaWrapper.java` | Mapper para conversão de ResultSet em objeto de domínio |
| `AppConfigurationListener.java` | Configuração do listener JMS e conversores de mensagem |
| `CartaoContaConfiguration.java` | Configuração de beans do Spring para repositório e serviço |
| `MappingMessageLocalConverter.java` | Conversor customizado de mensagens JSON com tratamento de erros |
| `DateFormatUtil.java` | Utilitário para formatação de datas |

## 3. Tecnologias Utilizadas

- **Java 11** (OpenJ9)
- **Spring Boot 2.1.9.RELEASE**
- **Spring Data JDBC**
- **IBM MQ JMS** (mq-jms-spring-boot-starter 2.0.9)
- **SQL Server** (Microsoft JDBC Driver 7.4.0)
- **Sybase jConnect 4** (7.07-ESD-5)
- **Lombok 1.18.10**
- **Swagger/Springfox 2.9.2** (documentação de API)
- **Micrometer 1.1.6** (métricas e monitoramento)
- **Logback 1.2.3** (logging)
- **JUnit Jupiter 5.5.2** (testes)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)

## 4. Principais Endpoints REST

não se aplica

(O sistema não expõe endpoints REST - é um consumer de mensagens JMS)

## 5. Principais Regras de Negócio

1. **Validação de Cartão Existente**: Verifica se o cartão de débito já está cadastrado no sistema através de chave composta (banco, conta, emissor, filial, produto, número do cartão e correlativo)

2. **Inserção de Novo Cartão**: Quando o cartão não existe, realiza cadastro completo com data de ativação, status, código de bloqueio e flag ativo

3. **Atualização de Cartão Existente**: Quando o cartão já está cadastrado, atualiza o status do cartão e código de motivo de bloqueio

4. **Registro de Histórico**: Antes de atualizar um cartão existente, insere um registro de log na tabela de histórico preservando o estado anterior

5. **Tratamento de Mensagens Inválidas**: Mensagens JSON malformadas são logadas com detalhes completos mas não interrompem o processamento

## 6. Relação entre Entidades

**CartaoConta** (Entidade Principal):
- Representa um cartão de débito vinculado a uma conta bancária
- Atributos principais: banco, conta débito, tipo cartão, emissor, produto, filial, correlativo, número conta cartão
- Atributos de controle: status destino, código bloqueio, data ativação, flag ativo, login
- Relacionamento implícito com conta bancária através dos campos: banco, conta débito, correlativo

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| CCBDTransacaoCartaoDebito.TbCartaoConta | tabela | SELECT | Consulta cartão de débito existente por chave composta (banco, conta, emissor, filial, produto, número cartão, correlativo) |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| CCBDTransacaoCartaoDebito.TbCartaoConta | tabela | INSERT | Insere novo registro de cartão de débito com todos os dados do cartão |
| CCBDTransacaoCartaoDebito.TbCartaoConta | tabela | UPDATE | Atualiza status do cartão e código de motivo de bloqueio |
| CCBDTransacaoCartaoDebito.TbLogCartaoConta | tabela | INSERT | Insere registro de log histórico antes de atualizar cartão existente |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| cartaocontarepositoryimpl-sql.xml | leitura | CartaoContaRepositoryImpl (via BvSql) | Arquivo XML contendo as queries SQL parametrizadas |
| application.yml | leitura | Spring Boot | Arquivo de configuração principal da aplicação |
| application-local.yml | leitura | Spring Boot | Configurações específicas para ambiente local |
| logback-spring.xml | leitura | Logback | Configuração de logging da aplicação |

## 10. Filas Lidas

- **Fila**: `QL.CCBD.STATUS_CARTAO.INT`
- **Tecnologia**: IBM MQ
- **Queue Manager**: QM.DIG.01
- **Channel**: CCBD.SRVCONN
- **Formato**: JSON (ISO-8859-1)
- **Descrição**: Fila de entrada contendo mensagens com informações de status de cartões de débito para validação e processamento
- **Listener**: `CartaoContaListener.checkDebtCard()`

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| IBM MQ | Mensageria | Consumo de mensagens da fila de status de cartões |
| SQL Server (DBCCBD) | Banco de Dados | Persistência de dados de cartões e logs históricos |
| Prometheus | Monitoramento | Exposição de métricas via endpoint /actuator/prometheus |

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com módulos domain e application
- Uso adequado de padrões Spring Boot (Repository, Service, Listener)
- Implementação de logging estruturado
- Uso de Lombok reduzindo boilerplate
- Externalização de queries SQL em arquivo XML
- Tratamento de mensagens inválidas sem quebrar o fluxo

**Pontos de Melhoria:**
- Classes de teste vazias (CartaoContaConfigurationTest, CartaoContaRepositoryImplTest, CartaoContaServiceTest)
- Tratamento de exceções genérico no serviço (catch Exception)
- Falta de validações de negócio mais robustas
- Conversor customizado (MappingMessageLocalConverter) com lógica complexa e código comentado
- Ausência de documentação JavaDoc nas classes
- Hardcoded de valores como "dsLogin = 1" no repositório
- Falta de testes unitários implementados
- Exception customizada (CustomerException) vazia e não utilizada

## 14. Observações Relevantes

1. **Arquitetura Modular**: O projeto segue arquitetura hexagonal com separação clara entre domain e application

2. **Ambientes**: Suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas via YAML e secrets

3. **Infraestrutura**: Preparado para deploy em OpenShift/Kubernetes com configurações de probes (liveness e readiness)

4. **Segurança**: Senhas e credenciais gerenciadas via secrets e cofre de senhas corporativo

5. **Monitoramento**: Integrado com Actuator e Prometheus para observabilidade

6. **Containerização**: Dockerfile otimizado usando OpenJ9 Alpine com configurações de memória JVM

7. **Pipeline**: Integrado com Jenkins para CI/CD (jenkins.properties)

8. **Nomenclatura**: Segue padrão corporativo Banco Votorantim (prefixo sboot-ccbd-base-atom)

9. **Dependências Corporativas**: Utiliza bibliotecas internas como `springboot-arqt-base-lib-database`

10. **Limitação de Testes**: Apesar da estrutura de testes estar presente, as classes de teste estão vazias, indicando ausência de cobertura de testes automatizados