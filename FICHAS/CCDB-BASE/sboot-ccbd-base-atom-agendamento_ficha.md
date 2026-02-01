# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de gerenciamento de agendamentos de pagamentos do Banco Votorantim, desenvolvido em Java com Spring Boot. O sistema permite criar, consultar, atualizar e cancelar agendamentos de diversos tipos de transações financeiras (PIX, TED, TEF, boletos de consumo/tributo/cobrança e investimentos em CDB). Integra-se com bancos de dados SQL Server e Sybase, filas IBM MQ e RabbitMQ, e suporta operações via Open Banking/Open Finance.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `AgendamentoController` | Controlador REST que expõe endpoints para operações de agendamento |
| `AgendamentoServiceImpl` | Implementa a lógica de negócio para gerenciamento de agendamentos |
| `OpenBankingScheduleUpdateServiceImpl` | Processa atualizações de agendamentos Open Finance via RabbitMQ |
| `AgendamentoListener` | Consome mensagens da fila IBM MQ para atualizar agendamentos |
| `AgendamentoAdapter` | Converte entre objetos de domínio e representações de API |
| `AgendamentoRepository` | Interface JDBI para acesso ao banco SQL Server (DBCCBD) |
| `AgendamentoCCRepository` | Interface JDBI para acesso ao banco Sybase (DBGLOBAL) |
| `TbAgendamento` | Entidade de domínio representando um agendamento |
| `TbPessoaAgendamento` | Entidade de domínio com dados de remetente e favorecido |
| `TbParametroAgendaOperacao` | Entidade para configuração de agendamentos recorrentes de CDB |

---

## 3. Tecnologias Utilizadas

- **Framework**: Spring Boot 2.x
- **Linguagem**: Java 11
- **Persistência**: JDBI 3.x, JDBC
- **Bancos de Dados**: Microsoft SQL Server, Sybase ASE
- **Mensageria**: IBM MQ (JMS), RabbitMQ (AMQP)
- **Documentação API**: Swagger/OpenAPI 3.0, Springfox
- **Segurança**: Spring Security, OAuth2/JWT
- **Testes**: JUnit 5, Mockito, RestAssured, Pact
- **Build**: Maven
- **Containerização**: Docker
- **Observabilidade**: Spring Actuator, Micrometer, Prometheus
- **Logging**: Logback com formato JSON

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/corporativo/pagamentos/agendamento/boleto` | `AgendamentoController` | Consulta agendamento por NSU |
| POST | `/v1/corporativo/pagamentos/agendamento/boleto` | `AgendamentoController` | Cria novo agendamento de boleto |
| PUT | `/v1/corporativo/pagamentos/agendamento/boleto` | `AgendamentoController` | Atualiza lista de agendamentos |
| GET | `/v1/corporativo/pagamentos/agendamento/consulta/boleto` | `AgendamentoController` | Consulta agendamentos por período |
| GET | `/v1/corporativo/pagamentos/agendamento/total` | `AgendamentoController` | Consulta valor total de agendamentos |
| GET | `/v1/corporativo/pagamentos/agendamento/duplicidade/{linhadigitavel}` | `AgendamentoController` | Verifica duplicidade de agendamento |
| POST | `/v1/banco-digital/agendar/pix` | `AgendamentoController` | Cria agendamento PIX |
| PUT | `/v1/banco-digital/agendar/pix` | `AgendamentoController` | Atualiza agendamento PIX |
| POST | `/v1/pagamento/agendar` | `AgendamentoController` | Agenda transferência TED/TEF/Boleto |
| GET | `/v1/pagamento/consultar` | `AgendamentoController` | Consulta agendamentos de transferência |
| POST | `/v1/banco-digital/investimento/agendar` | `AgendamentoController` | Cria agendamento de aplicação em CDB |
| DELETE | `/v1/banco-digital/investimento/excluir/{schedulingId}` | `AgendamentoController` | Exclui agendamento de CDB |
| PUT | `/v1/agendamento/cancelar/tipo` | `AgendamentoController` | Cancela agendamentos por tipo |
| PUT | `/v1/agendamento/cancelar/nsu` | `AgendamentoController` | Cancela agendamento por NSU |

---

## 5. Principais Regras de Negócio

1. **Validação de Horário**: Impede agendamento de boletos se houver outro agendamento nas últimas 48 horas para o mesmo código de barras
2. **Verificação de Duplicidade**: Valida se já existe agendamento para a mesma linha digitável, data e conta
3. **Controle de Tentativas**: Limita a 11 tentativas de liquidação para agendamentos PIX
4. **Status de Agendamento**: Gerencia ciclo de vida (Agendado → Processando → Efetivado/Cancelado/Não Efetivado)
5. **Agendamentos Recorrentes**: Suporta agendamentos periódicos (diário/mensal) para investimentos em CDB
6. **Tratamento de Favorecido TEF**: Ajusta código do banco favorecido para transferências TEF internas
7. **Integração Open Finance**: Publica eventos de status de pagamento via RabbitMQ para transações Open Banking
8. **Atualização por Canal Secundário**: Processa atualizações de status vindas do sistema SPAG
9. **Validação de Envelope**: Valida dados de envelope e produto para agendamentos de investimento
10. **Geração de NSU**: Gera identificador único (UUID) para cada agendamento quando não fornecido

---

## 6. Relação entre Entidades

**TbAgendamento** (1) ←→ (1) **TbPessoaAgendamento**: Um agendamento possui dados de uma pessoa (remetente e favorecido)

**TbAgendamento** (N) ←→ (1) **TbParametroAgendaOperacao**: Múltiplos agendamentos podem estar vinculados a uma configuração de agendamento recorrente (para CDB)

**TbParametroAgendaOperacao** (1) ←→ (N) **TbExecucaoAgendaOperacao**: Uma configuração de agendamento possui múltiplos logs de execução

**Relacionamentos principais**:
- `TbAgendamento.cdAgendamento` ← `TbPessoaAgendamento.cdAgendamento` (FK)
- `TbAgendamento.cdParametroAgendaOperacao` → `TbParametroAgendaOperacao.cdParametroAgendaOperacao` (FK)
- `TbParametroAgendaOperacao.cdParametroAgendaOperacao` ← `TbExecucaoAgendaOperacao.cdAgendaOperacao` (FK)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View | Tipo | Operação | Breve Descrição |
|---------------------|------|----------|-----------------|
| CCBDAgendamento.TbAgendamento | Tabela | SELECT | Consulta agendamentos de pagamento |
| CCBDAgendamento.TbPessoaAgendamento | Tabela | SELECT | Consulta dados de remetente e favorecido |
| CCBDAgendamento.TbParametroAgendaOperacao | Tabela | SELECT | Consulta configurações de agendamentos recorrentes |
| CCBDAgendamento.TbStatusAgendamento | Tabela | SELECT | Consulta descrições de status |
| dbcontacorrente.dbo.TbAgendamentoContaCorrente | Tabela | SELECT | Consulta agendamentos no Sybase |
| dbcontacorrente.dbo.TbAgendamentoFavorecido | Tabela | SELECT | Consulta favorecidos de agendamentos Sybase |
| dbcontacorrente.dbo.TbSequencial | Tabela | SELECT | Consulta sequencial para geração de IDs |
| dbcontacorrente.dbo.TbTransacao | Tabela | SELECT | Consulta tipos de transação |
| dbcontacorrente.dbo.TbConta | Tabela | SELECT | Consulta saldo de contas |
| DBGLOBAL.dbo.TbContaRelacionamento | Tabela | SELECT | Consulta relacionamento de contas |
| DBGLOBAL.dbo.TbPessoaTitularidade | Tabela | SELECT | Consulta titularidade de pessoas |
| DBGLOBAL.dbo.TbPessoa | Tabela | SELECT | Consulta dados de pessoas |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View | Tipo | Operação | Breve Descrição |
|---------------------|------|----------|-----------------|
| CCBDAgendamento.TbAgendamento | Tabela | INSERT/UPDATE | Grava e atualiza agendamentos |
| CCBDAgendamento.TbPessoaAgendamento | Tabela | INSERT | Grava dados de remetente e favorecido |
| CCBDAgendamento.TbParametroAgendaOperacao | Tabela | INSERT/UPDATE | Grava e atualiza configurações de agendamentos recorrentes |
| CCBDAgendamento.TbExecucaoAgendaOperacao | Tabela | INSERT | Grava logs de execução de agendamentos |
| dbcontacorrente.dbo.TbAgendamentoContaCorrente | Tabela | INSERT/UPDATE | Grava e atualiza agendamentos no Sybase |
| dbcontacorrente.dbo.TbAgendamentoFavorecido | Tabela | INSERT | Grava favorecidos de agendamentos |
| dbcontacorrente.dbo.TbSequencial | Tabela | UPDATE | Incrementa sequencial para geração de IDs |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | Spring Boot | Configurações da aplicação por ambiente |
| logback-spring.xml | Leitura | Logback | Configuração de logs em formato JSON |
| sboot-ccbd-base-atom-agendamento.yaml | Leitura | Swagger Codegen | Especificação OpenAPI para geração de código |
| *.sql | Leitura | JDBI (UseClasspathSqlLocator) | Queries SQL para operações de banco |

---

## 10. Filas Lidas

- **Fila IBM MQ**: `QL.CCBD.PROC_PGMT_AGENDADOS_DIG.INT`
  - **Classe**: `AgendamentoListener`
  - **Descrição**: Consome mensagens de lançamentos para atualizar status de agendamentos processados pelo batch

---

## 11. Filas Geradas

- **Exchange RabbitMQ**: `events.business.statusPagamento`
  - **Routing Key**: `PAYMENTS`
  - **Classe**: `OpenBankingScheduleUpdateServiceImpl`
  - **Descrição**: Publica eventos de atualização de status de pagamentos Open Finance

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| IBM MQ | Mensageria | Recebe notificações de processamento de agendamentos do batch |
| RabbitMQ | Mensageria | Publica eventos de status de pagamentos Open Finance |
| SQL Server (DBCCBD) | Banco de Dados | Armazena agendamentos e configurações |
| Sybase (DBGLOBAL) | Banco de Dados | Armazena agendamentos legados e dados de contas |
| OAuth2/JWT | Autenticação | Valida tokens de acesso às APIs |
| Prometheus | Observabilidade | Expõe métricas da aplicação |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com camadas bem definidas (controller, service, repository, domain)
- Uso adequado de padrões como Adapter, Builder e Repository
- Cobertura de testes razoável com testes unitários, integração e funcionais
- Documentação OpenAPI bem estruturada
- Uso de JDBI com queries SQL externalizadas facilita manutenção
- Tratamento de exceções estruturado
- Configuração por ambiente bem organizada

**Pontos de Melhoria:**
- Presença de código comentado em várias classes (ex: logs com `Encode.forJava` comentados)
- Algumas classes muito extensas (ex: `AgendamentoController` com mais de 600 linhas)
- Lógica de negócio complexa em alguns métodos poderia ser refatorada em métodos menores
- Uso inconsistente de Optional em alguns lugares
- Alguns métodos com muitos parâmetros (ex: `consultarAgendamentoByPeriodo` com 6 parâmetros)
- Falta de documentação JavaDoc em algumas classes e métodos importantes
- Algumas constantes mágicas poderiam ser extraídas para enums ou classes de configuração
- Tratamento de erros genérico em alguns lugares (catch Exception)

---

## 14. Observações Relevantes

1. **Arquitetura Multi-Banco**: O sistema trabalha com dois bancos de dados distintos (SQL Server para dados novos e Sybase para dados legados), o que adiciona complexidade mas permite migração gradual.

2. **Suporte a Open Finance**: Implementa integração completa com Open Banking/Open Finance, incluindo gestão de consentimentos e notificações de status via eventos.

3. **Processamento Assíncrono**: Utiliza filas IBM MQ para processamento assíncrono de agendamentos e RabbitMQ para eventos de Open Finance.

4. **Agendamentos Recorrentes**: Suporta agendamentos periódicos para investimentos em CDB com controle de recorrência.

5. **Controle de Tentativas**: Implementa lógica de retry com limite de tentativas para agendamentos PIX.

6. **Validações de Negócio**: Possui validações robustas como verificação de duplicidade, validação de horário e controle de status.

7. **Configuração por Ambiente**: Bem estruturado com profiles Spring (local, des, qa, uat, prd) e configurações externalizadas.

8. **Observabilidade**: Integrado com Actuator, Prometheus e logs estruturados em JSON para facilitar monitoramento.

9. **Segurança**: Implementa autenticação OAuth2/JWT e possui configurações de segurança por endpoint.

10. **Pipeline CI/CD**: Configurado para deploy em Google Cloud Platform (GCP) com Kubernetes/OpenShift.