# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **springboot-spag-base-monitoramento-contas** é uma aplicação Spring Boot desenvolvida para gerenciar bloqueios e desbloqueios judiciais em contas de fintechs. O sistema atua como intermediário entre o sistema BJUD (Bloqueio Judicial) e as APIs de fintechs parceiras, processando solicitações de bloqueio, desbloqueio intraday e desbloqueio por valor em contas bancárias. A aplicação consome mensagens de filas JMS (IBM MQ), executa as operações necessárias via APIs REST das fintechs através de um gateway, registra os processamentos em banco de dados SQL Server e retorna os resultados via fila de resposta.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Server** | Classe principal que inicializa a aplicação Spring Boot |
| **BloqueioService** | Serviço de negócio que orquestra as operações de bloqueio, desbloqueio intraday e desbloqueio por valor |
| **FintechRepository** | Repositório para acesso ao banco de dados, gerenciando processos jurídicos, solicitações e processamentos |
| **GatewayRepository** | Repositório responsável pela comunicação com as APIs das fintechs via gateway, incluindo autenticação OAuth2 |
| **MQPosterRepository** | Repositório para envio de mensagens para filas JMS |
| **SolicitacaoMQListener** | Listener JMS que consome mensagens da fila de entrada e direciona para processamento |
| **MonitoramentoAPI** | Controller REST que expõe endpoints para operações de bloqueio e desbloqueio |
| **UtilSpag** | Classe utilitária com funções de conversão de datas, JSON, validação de CPF/CNPJ |
| **ProcessoJuridico** | Entidade de domínio representando um processo judicial |
| **SolicitacaoJuridico** | Entidade representando uma solicitação de bloqueio/desbloqueio |
| **ProcessamentoMovimentoJuridico** | Entidade representando o processamento de uma movimentação judicial |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.0.0.RELEASE** - Framework principal
- **Spring Web** - Para endpoints REST
- **Spring JDBC** - Para acesso a banco de dados
- **Spring JMS** - Para integração com filas IBM MQ
- **IBM MQ** - Sistema de mensageria
- **SQL Server** - Banco de dados relacional (driver mssql-jdbc 7.0.0)
- **Jackson** - Serialização/deserialização JSON
- **Lombok** - Redução de boilerplate
- **Swagger/Springfox 2.8.0** - Documentação de API
- **Gradle 4.5.1** - Ferramenta de build
- **Docker** - Containerização
- **JUnit/Mockito** - Testes unitários
- **Jacoco** - Cobertura de testes
- **SonarQube** - Análise de qualidade de código
- **RestTemplate** - Cliente HTTP para consumo de APIs
- **Logback** - Framework de logging

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /monitoramento/bloquear | MonitoramentoAPI | Envia solicitação de bloqueio judicial para fintechs |
| POST | /monitoramento/desBloquearIntraday | MonitoramentoAPI | Envia solicitação de desbloqueio intraday (mesmo dia do bloqueio) |
| POST | /monitoramento/desBloquearPorValor | MonitoramentoAPI | Envia solicitação de desbloqueio baseado em valor disponível nas contas |

---

## 5. Principais Regras de Negócio

1. **Bloqueio Judicial**: Processa solicitações de bloqueio de valores em contas de fintechs, distribuindo o valor solicitado entre múltiplas contas até atingir o montante requerido ou esgotar as contas disponíveis.

2. **Desbloqueio Intraday**: Realiza desbloqueio automático no mesmo dia do bloqueio, apenas para contas que tiveram bloqueio bem-sucedido anteriormente.

3. **Desbloqueio por Valor**: Consulta saldos das contas e desbloqueia aquelas cujo saldo seja menor ou igual ao valor especificado.

4. **Gestão de Token OAuth2**: Mantém cache de token de autenticação com renovação automática antes da expiração.

5. **Registro de Processamento**: Todos os processamentos (bloqueios e desbloqueios) são registrados no banco de dados com status, valores atendidos e mensagens de erro.

6. **Validação de CPF/CNPJ**: Valida documentos antes do processamento.

7. **Tratamento de Erros**: Captura exceções de comunicação com APIs e registra como processamentos com erro, sem interromper o fluxo.

8. **Atualização de Status**: Atualiza status de solicitações conforme o processamento avança (Pendente → Atendido/Parcialmente Atendido).

---

## 6. Relação entre Entidades

**Principais entidades e relacionamentos:**

- **TbProcessoJuridico**: Representa um processo judicial único (identificado por CPF/CNPJ, número do processo, protocolo e vara)
  - Relaciona-se com **TbSolicitacaoJuridico** (1:N) - um processo pode ter várias solicitações

- **TbSolicitacaoJuridico**: Representa uma solicitação de bloqueio/desbloqueio
  - Relaciona-se com **TbTipoSolicitacaoJuridico** (N:1) - cada solicitação tem um tipo
  - Relaciona-se com **TbProcessamentoMovimentoJuridico** (1:N) - uma solicitação pode ter vários processamentos

- **TbProcessamentoMovimentoJuridico**: Representa a execução de uma solicitação em uma conta específica
  - Relaciona-se com **TbContaUsuarioFintech** (N:1) - cada processamento é para uma conta específica

- **TbContaUsuarioFintech**: Representa uma conta de usuário em uma fintech
  - Relaciona-se com **TbUsuarioContaFintech** (N:1) via **TbRelacaoContaUsuarioFintech**
  - Relaciona-se com **TbParametroPagamentoFintech** (N:1) - configurações da fintech

- **TbParametroConsultaCliente**: Armazena URLs e credenciais para consultas às fintechs

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbTipoSolicitacaoJuridico | tabela | SELECT | Busca tipos de solicitação (Bloqueio, Desbloqueio, etc) |
| TbProcessoJuridico | tabela | SELECT | Busca processos jurídicos existentes por CPF/CNPJ, número do processo e protocolo |
| TbSolicitacaoJuridico | tabela | SELECT | Busca solicitações jurídicas por código |
| TbUsuarioContaFintech | tabela | SELECT | Lista contas de usuários em fintechs |
| TbRelacaoContaUsuarioFintech | tabela | SELECT | Relacionamento entre usuários e contas |
| TbContaUsuarioFintech | tabela | SELECT | Dados de contas específicas (agência, número) |
| TbParametroPagamentoFintech | tabela | SELECT | Parâmetros e configurações das fintechs |
| TbParametroConsultaCliente | tabela | SELECT | URLs e credenciais para consultas às fintechs |
| TbProcessamentoMovimentoJuridico | tabela | SELECT | Busca processamentos de bloqueios ativos |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbTipoSolicitacaoJuridico | tabela | INSERT | Cadastra novos tipos de solicitação se não existirem |
| TbProcessoJuridico | tabela | INSERT/UPDATE | Insere novos processos jurídicos ou atualiza existentes |
| TbSolicitacaoJuridico | tabela | INSERT/UPDATE | Insere novas solicitações e atualiza valores realizados |
| TbProcessamentoMovimentoJuridico | tabela | INSERT/UPDATE | Registra processamentos de bloqueios/desbloqueios e atualiza status (flAtivo) |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot / resources | Configurações da aplicação por ambiente |
| application-local.yml | leitura | Spring Boot / resources | Configurações específicas do ambiente local |
| logback-spring.xml | leitura | Logback / resources e /usr/etc/log | Configuração de logs |
| fintechrepository-sql.xml | leitura | BvSql / FintechRepository | Queries SQL parametrizadas |
| roles/*.yml | leitura | Spring Security | Configuração de roles por ambiente |
| *.jar | gravação | Gradle build | Artefato compilado da aplicação |

---

## 10. Filas Lidas

- **QL.ATACADO.BLOQUEIO_VALORES_JUDICIAIS_OUT.INT** (configurável via `bv.mq.inQueueName`)
  - Fila de entrada que recebe solicitações de bloqueio/desbloqueio do sistema BJUD
  - Formato: JSON encapsulado em `EnvelopeQueue` com tipos de mensagem (1=Bloqueio, 2=Desbloqueio Intraday, 3=Desbloqueio por Valor)
  - Listener: `SolicitacaoMQListener`

---

## 11. Filas Geradas

- **QL.ATACADO.BLOQUEIO_VALORES_JUDICIAIS_IN.INT** (configurável via `bv.mq.outQueueName`)
  - Fila de saída para envio de respostas ao sistema BJUD
  - Formato: JSON encapsulado em `EnvelopeQueue` contendo logs de execução e resultados dos processamentos
  - Classe responsável: `MQPosterRepository`

---

## 12. Integrações Externas

1. **API Gateway Fintech** (https://apigatewaydes.bvnet.bv)
   - Autenticação OAuth2 (client credentials)
   - Endpoints consumidos:
     - `/auth/oauth/v2/token` - Obtenção de token de acesso
     - `/v1/atacado/operacional/fintech-bloqueio-judicial-valor-conta` - Bloqueio judicial
     - `/v1/atacado/operacional/fintech-desbloqueio-intradia-conta` - Desbloqueio intraday
     - `/v1/atacado/operacional/fintech-desbloqueio-saldo-conta` - Desbloqueio por valor
     - `/v1/atacado/operacional/fintech-consulta-saldo-conta` - Consulta de saldos
   - Classe responsável: `GatewayRepository`

2. **IBM MQ** (Queue Manager configurável por ambiente)
   - Integração via JMS para consumo e publicação de mensagens
   - Configuração: `spring.ibm.mq.*`

3. **SQL Server** (DBSPAG)
   - Banco de dados principal para persistência
   - Acesso via JDBC

4. **LDAP BVNet** (ambientes não-local)
   - Autenticação de usuários
   - Configuração: `bv.security.base.ldap.*`

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Uso adequado de padrões Spring Boot (Services, Repositories, Controllers)
- Separação de responsabilidades entre camadas
- Uso de Lombok para redução de boilerplate
- Configuração por ambiente bem estruturada
- Presença de testes unitários com Mockito
- Documentação Swagger configurada
- Tratamento de exceções implementado

**Pontos Negativos:**
- **Código extenso e complexo**: Métodos muito longos (ex: `bloquear`, `desBloquearPorValor` em `BloqueioService`)
- **Lógica de negócio misturada**: `BloqueioService` acumula muitas responsabilidades
- **Variáveis estáticas em Repository**: `GatewayRepository` usa variáveis estáticas para cache de token, o que pode causar problemas em ambientes concorrentes
- **Tratamento de exceções genérico**: Muitos blocos catch que apenas logam e continuam, dificultando troubleshooting
- **Strings hardcoded**: Valores como "OK", "ERRO", "S", "N" espalhados pelo código
- **Falta de constantes**: Números mágicos e strings repetidas sem constantes nomeadas
- **Comentários em português e inglês misturados**: Inconsistência no idioma
- **Logs excessivos**: Muitos logs de debug em produção
- **Conversões de tipo repetitivas**: Código duplicado para conversões
- **Falta de validações**: Poucas validações de entrada em alguns métodos
- **Nomenclatura inconsistente**: Mistura de português e inglês em nomes de variáveis

---

## 14. Observações Relevantes

1. **Ambientes**: O sistema suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas via profiles do Spring.

2. **Segurança**: Implementa autenticação básica e LDAP, com roles configuráveis por ambiente. Em local, usa autenticação in-memory para testes.

3. **Containerização**: Possui Dockerfile e scripts Gradle para build e deploy em Docker/OpenShift.

4. **Pipeline CI/CD**: Configurado para Jenkins com propriedades específicas (jenkins.properties).

5. **Gestão de Token**: O sistema mantém um cache de token OAuth2 com renovação automática 2 minutos antes da expiração, mas a implementação com variáveis estáticas pode ser problemática em ambientes distribuídos.

6. **Tratamento de Erros de Gateway**: Captura erros HTTP específicos (4xx, 5xx) e registra como processamentos com erro, permitindo rastreabilidade.

7. **Processamento Assíncrono**: Consome mensagens de fila de forma assíncrona via JMS Listener.

8. **Versionamento**: Usa plugin Gradle de release para gestão de versões.

9. **Qualidade**: Integrado com SonarQube e Jacoco para análise de qualidade e cobertura de testes.

10. **Documentação**: README básico presente, mas poderia ser mais detalhado sobre arquitetura e fluxos de negócio.

11. **Dependências Internas**: Utiliza bibliotecas internas da Votorantim (`br.com.votorantim.arqt.base.*`) para funcionalidades comuns como trilha de auditoria, segurança e acesso a banco de dados.