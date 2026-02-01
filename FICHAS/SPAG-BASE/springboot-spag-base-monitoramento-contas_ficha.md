# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **springboot-spag-base-monitoramento-contas** é uma aplicação Spring Boot desenvolvida para gerenciar operações de bloqueio e desbloqueio judicial de contas em instituições financeiras (Fintechs). O sistema atua como intermediário entre o sistema BJUD (Bacen Jud) e as Fintechs parceiras, processando solicitações de bloqueio, desbloqueio (intraday, por valor e judicial) e transferências judiciais de valores bloqueados. Opera através de filas JMS para receber solicitações e enviar respostas, além de expor endpoints REST para consultas e operações síncronas.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Server.java** | Classe principal da aplicação Spring Boot, configura executor de threads assíncronas |
| **BloqueioService.java** | Serviço principal contendo toda a lógica de negócio para bloqueios, desbloqueios e transferências judiciais |
| **SolicitacaoMQListener.java** | Listener JMS que recebe mensagens da fila de entrada e direciona para processamento assíncrono |
| **MonitoramentoAPI.java** | Controller REST que expõe endpoints para operações de bloqueio, desbloqueio e consulta de saldos |
| **FintechRepository.java** | Repositório para acesso ao banco DBSPAG, gerencia processos jurídicos, solicitações e processamentos |
| **GatewayRepository.java** | Repositório responsável por integração com API Gateway das Fintechs, realiza chamadas HTTP |
| **MQPosterRepository.java** | Repositório para envio de mensagens de retorno para fila JMS |
| **AuxDBRepository.java** | Repositório auxiliar para acesso ao banco DBSPAG2, controla status de processamento |
| **ProcessoJuridico.java** | Entidade de domínio representando um processo judicial |
| **SolicitacaoJuridico.java** | Entidade representando uma solicitação de operação judicial |
| **ProcessamentoMovimentoJuridico.java** | Entidade representando o processamento de uma movimentação judicial |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.7.18** - Framework principal
- **Spring JMS** - Integração com filas IBM MQ
- **Spring JDBC** - Acesso a banco de dados
- **SQL Server** - Banco de dados (DBSPAG e DBSPAG2)
- **IBM MQ** - Sistema de mensageria
- **Gradle 7.5.1** - Gerenciamento de dependências e build
- **Swagger/Springfox 3.0.0** - Documentação de API
- **Logback** - Sistema de logs em formato JSON
- **Jackson** - Serialização/deserialização JSON
- **Lombok** - Redução de código boilerplate
- **HikariCP** - Pool de conexões JDBC
- **Docker** - Containerização (OpenJDK 8 com OpenJ9)
- **ConfigCat/Feature Toggle** - Gerenciamento de feature flags
- **JUnit 4 e Mockito** - Testes unitários
- **JMeter** - Testes funcionais
- **Micrometer/Prometheus** - Métricas e monitoramento

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /monitoramento/bloquear | MonitoramentoAPI | Envia solicitação de bloqueio judicial para Fintechs |
| POST | /monitoramento/desBloquearIntraday | MonitoramentoAPI | Envia solicitação de desbloqueio intraday (libera conta para uso) |
| POST | /monitoramento/desBloquearPorValor | MonitoramentoAPI | Envia solicitação de desbloqueio parcial por valor específico |
| POST | /monitoramento/desBloqueioJuridico | MonitoramentoAPI | Envia solicitação de desbloqueio judicial completo |
| POST | /monitoramento/solicitacaoTransferenciaJuridico | MonitoramentoAPI | Envia solicitação de transferência de valores bloqueados |
| GET | /monitoramento/{documento}/contasFintech | MonitoramentoAPI | Consulta contas e saldos de Fintechs por documento (CPF/CNPJ) |

---

## 5. Principais Regras de Negócio

1. **Validação de Tempo de Processamento**: Não permite reprocessamento de um mesmo protocolo em menos de 300 segundos (5 minutos)
2. **Validação de Valor Total Bloqueado**: Impede novo bloqueio se o valor já bloqueado for maior ou igual ao valor solicitado
3. **Bloqueio Sequencial**: Processa bloqueio em múltiplas contas Fintech até atingir o valor solicitado ou esgotar as contas disponíveis
4. **Desbloqueio Intraday Automático**: Após atingir o valor total de bloqueio solicitado, libera automaticamente as contas para uso
5. **Desbloqueio por Valor**: Desbloqueia valor específico e mantém saldo remanescente bloqueado, seguido de desbloqueio intraday
6. **Desbloqueio Judicial**: Desbloqueia todos os valores bloqueados de um processo judicial específico
7. **Transferência Fintech Puro**: Só processa transferências automáticas se todos os bloqueios forem em Fintechs (CCS válidos)
8. **Validação CPF/CNPJ**: Valida dígitos verificadores de documentos antes do processamento
9. **Controle de Reprocessamento**: Atualiza tabela de controle para evitar duplicidade de processamento
10. **Tratamento de Erros**: Registra erros detalhados e envia resposta ao BJUD mesmo em caso de falha parcial

---

## 6. Relação entre Entidades

**ProcessoJuridico** (1) ----< (N) **SolicitacaoJuridico**
- Um processo judicial pode ter múltiplas solicitações (bloqueio, desbloqueio, transferência)

**SolicitacaoJuridico** (1) ----< (N) **ProcessamentoMovimentoJuridico**
- Uma solicitação pode gerar múltiplos processamentos (um para cada conta Fintech)

**ProcessamentoMovimentoJuridico** (N) >---- (1) **ContaUsuarioFintech**
- Cada processamento está vinculado a uma conta específica de Fintech

**SolicitacaoJuridico** (1) ----< (1) **SolicitacaoTransferencia**
- Uma solicitação de transferência está vinculada a uma solicitação jurídica

**TipoSolicitacaoJuridico** (1) ----< (N) **SolicitacaoJuridico**
- Define o tipo da solicitação (Bloqueio, Desbloqueio, Transferência, etc.)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbTipoSolicitacaoJuridico | tabela | SELECT | Busca tipos de solicitação jurídica cadastrados |
| TbProcessoJuridico | tabela | SELECT | Busca processos judiciais por protocolo |
| TbSolicitacaoJuridico | tabela | SELECT | Busca solicitações jurídicas por ID ou processo |
| TbProcessamentoMovimentoJuridico | tabela | SELECT | Busca processamentos de bloqueios ativos |
| TbUsuarioContaFintech | tabela | SELECT | Lista contas de usuários em Fintechs |
| TbContaUsuarioFintech | tabela | SELECT | Busca dados de contas específicas |
| TbRelacaoContaUsuarioFintech | tabela | SELECT | Relacionamento entre usuários e contas |
| TbParametroPagamentoFintech | tabela | SELECT | Parâmetros de integração com Fintechs |
| TbParametroConsultaCliente | tabela | SELECT | Endpoints e credenciais para consultas |
| TbTipoVinculoConta | tabela | SELECT | Tipos de vínculo (Titular, Co-Titular) |
| TbSolicitacaoTransferencia | tabela | SELECT | Busca última solicitação de transferência |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbTipoSolicitacaoJuridico | tabela | INSERT | Cadastra novos tipos de solicitação |
| TbProcessoJuridico | tabela | INSERT/UPDATE | Insere novos processos ou atualiza existentes |
| TbSolicitacaoJuridico | tabela | INSERT/UPDATE | Insere novas solicitações e atualiza valores realizados |
| TbProcessamentoMovimentoJuridico | tabela | INSERT/UPDATE | Registra processamentos e atualiza status (flAtivo) |
| TbSolicitacaoTransferencia | tabela | INSERT | Registra solicitações de transferência |
| TbControleBloqueioConta (DBSPAG2) | tabela | UPDATE | Atualiza controle de processamento de bloqueios |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | leitura | Configuração Spring Boot | Configuração de logs em formato JSON por ambiente |
| application.yml | leitura | Configuração Spring Boot | Configurações principais da aplicação |
| application-local.yml | leitura | Configuração Spring Boot | Configurações específicas do ambiente local |
| roles/*.yml | leitura | Configuração de segurança | Define roles e permissões por ambiente |
| auxdbrepository-sql.xml | leitura | AuxDBRepository | Queries SQL para banco auxiliar |
| fintechrepository-sql.xml | leitura | FintechRepository | Queries SQL para operações com Fintech |

---

## 10. Filas Lidas

| Nome da Fila | Tecnologia | Classe Consumidora | Descrição |
|--------------|------------|-------------------|-----------|
| QL.ATACADO.BLOQUEIO_VALORES_JUDICIAIS_OUT.INT | IBM MQ | SolicitacaoMQListener | Recebe solicitações do BJUD para processamento (bloqueios, desbloqueios, transferências) |

---

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Produtora | Descrição |
|--------------|------------|------------------|-----------|
| QL.ATACADO.BLOQUEIO_VALORES_JUDICIAIS_IN.INT | IBM MQ | MQPosterRepository | Envia respostas de processamento de volta para o BJUD |

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| API Gateway Fintech | REST API | Integração com Fintechs para operações de bloqueio, desbloqueio e transferência através do API Gateway corporativo |
| BJUD (Bacen Jud) | Fila JMS | Sistema do Banco Central para ordens judiciais de bloqueio |
| DBSPAG (SQL Server) | Banco de Dados | Banco principal com dados de processos, solicitações e processamentos |
| DBSPAG2 (SQL Server) | Banco de Dados | Banco auxiliar para controle de bloqueios |
| ConfigCat | Feature Toggle | Serviço de gerenciamento de feature flags para controle de rotas e funcionalidades |

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Uso adequado de padrões Spring Boot (Services, Repositories, Controllers)
- Implementação de processamento assíncrono para operações demoradas
- Tratamento de exceções estruturado
- Logs detalhados com sanitização de dados sensíveis
- Cobertura de testes unitários presente
- Uso de Lombok para redução de boilerplate
- Configuração adequada de múltiplos ambientes

**Pontos Negativos:**
- **Classe BloqueioService muito extensa** (mais de 600 linhas) com múltiplas responsabilidades, violando o princípio de responsabilidade única
- **Métodos muito longos** dificultando leitura e manutenção
- **Lógica de negócio complexa** sem separação clara de camadas
- **Uso excessivo de variáveis estáticas** em GatewayRepository (token, lastTokenD)
- **Strings hardcoded** espalhadas pelo código (ex: "OK", "ERRO", "S", "N")
- **Comentários em português e inglês misturados**
- **Falta de constantes** para valores mágicos (ex: 300 segundos, códigos de tipo)
- **Tratamento de exceções genérico** em alguns pontos
- **Código comentado** não removido
- **Nomenclatura inconsistente** (mix de português e inglês)

O código funciona e atende aos requisitos, mas necessita refatoração para melhorar manutenibilidade e legibilidade.

---

## 14. Observações Relevantes

1. **Feature Toggles**: O sistema utiliza ConfigCat para controlar rotas de integração (v1 vs v2) com Fintechs através de toggles `ft_boolean_spag_base_mtls_toggle` e `ft_string_spag_base_mtls_toggle`

2. **Processamento Assíncrono**: Todas as operações principais são executadas de forma assíncrona usando ThreadPoolTaskExecutor configurável (poolSize: 12, maxPoolSize: 12, queueCapacity: 12000)

3. **Múltiplos Ambientes**: Suporta 4 ambientes (DES, QA, UAT, PRD) com configurações específicas de banco, filas e API Gateway

4. **Segurança**: Utiliza autenticação básica e LDAP, com suporte a usuários in-memory para testes

5. **Controle de Duplicidade**: Implementa controle temporal (5 minutos) para evitar reprocessamento de mesma solicitação

6. **Logs Estruturados**: Utiliza formato JSON para logs com campos de contexto (ticket, fase)

7. **Monitoramento**: Expõe métricas Prometheus e endpoints de health check

8. **Validação de Documentos**: Implementa validação de CPF/CNPJ com cálculo de dígitos verificadores

9. **Tratamento de Saldo Remanescente**: Em desbloqueios parciais, cria novo registro de bloqueio com valor remanescente

10. **Integração Bidirecional**: Recebe solicitações via fila e pode responder tanto via fila quanto via API REST