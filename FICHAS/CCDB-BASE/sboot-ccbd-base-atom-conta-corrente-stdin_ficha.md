# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-ccbd-base-atom-conta-corrente-stdin** é um microserviço atômico desenvolvido em Java com Spring Boot, responsável por gerenciar transações de conta corrente em modo Stand-In (contingência). Quando o sistema principal de conta corrente está indisponível, este serviço registra e processa operações de crédito, débito, bloqueios e transferências (TEF), armazenando-as temporariamente em banco de dados SQL Server e enviando para processamento posterior via RabbitMQ. O sistema garante a continuidade operacional do banco durante indisponibilidades do sistema principal.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ContaCorrenteStdinController** | Controlador REST que expõe endpoints para operações de crédito, débito, TEF, bloqueios e consultas |
| **ContaCorrenteStdinService** | Serviço de domínio contendo regras de negócio para validação e processamento de transações |
| **TransactionalContaCorrenteStdinService** | Wrapper transacional do serviço principal, gerenciando transações de banco de dados |
| **ContaCorrenteStdinRepositoryImpl** | Implementação do repositório usando JDBI para acesso ao SQL Server |
| **ProcessaContaCorrenteStdinRepositoryImpl** | Repositório responsável por enviar transações para fila RabbitMQ |
| **TransacaoMapper** | Mapper para conversão de objetos de domínio em transações |
| **DadosEfetivacaoMapper** | Mapper para conversão de requisições REST em objetos de domínio |
| **ContaCorrenteSimplificado** | Entidade de domínio representando dados simplificados da conta corrente |
| **Transacao** | Entidade de domínio representando uma transação financeira |
| **BancoEnum** | Enum para conversão entre códigos internos e externos de bancos |
| **ExceptionReasonEnum** | Enum com códigos e mensagens de erro de negócio |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Spring MVC** (REST APIs)
- **Spring Security OAuth2** (autenticação JWT)
- **JDBI 3.9.1** (acesso a dados SQL)
- **Microsoft SQL Server** (banco de dados)
- **RabbitMQ** (mensageria)
- **Springfox/Swagger 3.0.0** (documentação de API)
- **Logback** (logging com formato JSON)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Lombok** (redução de boilerplate)
- **JUnit 5** e **Mockito** (testes)
- **Micrometer/Prometheus** (métricas)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/banco-digital/contas/transacao` | ContaCorrenteStdinController | Verifica se existe transação pendente no stand-in |
| PUT | `/v1/banco-digital/contas/transacao/inativar` | ContaCorrenteStdinController | Inativa transação stand-in por NSU ou sequência de bloqueio |
| POST | `/v1/banco-digital/contas/credito` | ContaCorrenteStdinController | Efetiva operação de crédito em stand-in |
| POST | `/v1/banco-digital/contas/debito` | ContaCorrenteStdinController | Solicita bloqueio para débito |
| POST | `/v1/banco-digital/contas/debito/confirmar` | ContaCorrenteStdinController | Confirma/efetiva operação de débito |
| POST | `/v1/banco-digital/contas/tef` | ContaCorrenteStdinController | Efetiva transferência entre contas (TEF) |
| POST | `/v1/banco-digital/contas/bloqueio/cancelar` | ContaCorrenteStdinController | Cancela bloqueio de saldo |
| PUT | `/v1/banco-digital/contas/transacao/circuitbreaker` | ContaCorrenteStdinController | Inativa todas as transações ativas (circuit breaker) |
| PUT | `/v1/banco-digital/contas/transacao/conta/circuitbreaker` | ContaCorrenteStdinController | Inativa transações de uma conta específica |
| GET | `/v1/banco-digital/contas/transacao/conta/consultar-bloqueios-standin/{params}` | ContaCorrenteStdinController | Consulta bloqueios stand-in ativos |

---

## 5. Principais Regras de Negócio

1. **Validação de Situação da Conta**: Verifica se a conta está ativa (situação 2 ou 6) antes de processar operações
2. **Bloqueio de Crédito**: Impede créditos em contas bloqueadas para crédito
3. **Bloqueio de Débito**: Impede débitos em contas bloqueadas para débito
4. **Validação de Saldo**: Verifica saldo disponível considerando saldo total, limite, bloqueios e transações cash in/out
5. **Prevenção de Duplicidade**: Valida NSU para evitar processamento duplicado de transações
6. **Lançamento Retroativo**: Impede lançamentos com data anterior à data atual
7. **Conversão de Códigos de Banco**: Converte entre códigos internos (161) e externos (655) do Banco Votorantim
8. **Geração de Sequência de Bloqueio**: Gera sequência única para cada bloqueio de saldo
9. **Processamento TEF**: Valida débito do remetente e crédito do favorecido em transações entre contas
10. **Circuit Breaker**: Permite inativação em massa de transações pendentes
11. **Truncamento de Complemento**: Limita descrição de operação a 40 caracteres

---

## 6. Relação entre Entidades

**Principais Entidades e Relacionamentos:**

- **ContaCorrenteSimplificado**: Representa uma conta corrente com saldos e bloqueios
  - Possui múltiplas **Transacao** (1:N)
  - Possui múltiplos **BloqueioSimplificado** (1:N)

- **Transacao**: Representa uma movimentação financeira
  - Pertence a uma **ContaCorrenteSimplificado** (N:1)
  - Pode referenciar um **BloqueioSimplificado** via sequência (N:1 opcional)

- **TransacaoTef**: Especialização de Transacao para transferências
  - Herda de **Transacao**
  - Referencia conta remetente e favorecido

- **DadosEfetivacao**: DTO para receber dados de efetivação
  - Convertido em **Transacao** pelos mappers

- **InfoConta**: Identificador de conta (banco, agência, número, tipo)

- **BloqueioSimplificado**: Representa um bloqueio de saldo
  - Associado a uma **ContaCorrenteSimplificado** (N:1)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| CCBDAutorizacaoDebito.TbConta | Tabela | SELECT | Consulta dados simplificados da conta corrente (saldos, bloqueios, situação) |
| CCBDAutorizacaoDebito.TbEfetivacaoCashStandIn | Tabela | SELECT | Consulta transações stand-in ativas, bloqueios e operações pendentes |
| CCBDAutorizacaoDebito.TbCotroleBloqueioConta | Tabela | SELECT | Consulta sequência de controle de bloqueio de conta |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| CCBDAutorizacaoDebito.TbEfetivacaoCashStandIn | Tabela | INSERT | Insere transações de crédito, débito e bloqueios stand-in |
| CCBDAutorizacaoDebito.TbEfetivacaoCashStandIn | Tabela | UPDATE | Atualiza transações para inativar ou atualizar dados de bloqueio |
| CCBDAutorizacaoDebito.TbCotroleBloqueioConta | Tabela | INSERT/UPDATE | Gera e atualiza sequência de controle de bloqueio |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | Spring Boot (startup) | Configurações da aplicação por ambiente (datasource, rabbitmq, security) |
| logback-spring.xml | Leitura | Logback (startup) | Configuração de logs em formato JSON |
| *.sql (resources) | Leitura | JDBI/ContaCorrenteStdinRepositoryImpl | Queries SQL para operações de banco de dados |
| swagger/*.yaml | Leitura | Springfox (startup) | Especificação OpenAPI da API REST |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Responsável | Descrição |
|--------------|------------|-------------------|-----------|
| ex.ccbd.standin | RabbitMQ (Exchange) | ProcessaContaCorrenteStdinRepositoryImpl | Exchange para envio de transações stand-in para processamento posterior |

**Observação**: O sistema publica mensagens do tipo `Transacao` e `TransacaoTef` no exchange configurado (ex.ccbd.standin) com routing key "*".

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| SQL Server (DBCCBD) | Banco de Dados | Armazena transações stand-in e dados de contas correntes |
| RabbitMQ | Mensageria | Recebe transações para processamento assíncrono |
| OAuth2/JWT Provider | Autenticação | Valida tokens JWT para autenticação de requisições (URLs configuráveis por ambiente) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões hexagonais (domain, application, infrastructure)
- Separação clara de responsabilidades entre camadas
- Uso adequado de mappers para conversão de objetos
- Boa cobertura de testes unitários
- Uso de enums para padronização de códigos e mensagens
- Tratamento centralizado de exceções
- Configuração adequada de transações
- Documentação OpenAPI/Swagger completa
- Uso de Lombok para reduzir boilerplate

**Pontos de Melhoria:**
- Algumas classes de serviço muito extensas (ContaCorrenteStdinService com múltiplas responsabilidades)
- Lógica de negócio complexa poderia ser quebrada em métodos menores
- Alguns métodos com muitos parâmetros (poderiam usar objetos de transferência)
- Falta de comentários JavaDoc em métodos públicos importantes
- Queries SQL embutidas em arquivos separados (boa prática), mas sem documentação sobre o propósito de cada uma
- Uso de strings mágicas em alguns pontos ("S", "N", "C", "D")
- Alguns testes poderiam ser mais descritivos nos nomes
- Falta de validação de entrada em alguns endpoints (confiança excessiva no contrato OpenAPI)

---

## 14. Observações Relevantes

1. **Modo Stand-In**: O sistema opera como contingência quando o sistema principal de conta corrente está indisponível, registrando operações para processamento posterior.

2. **Processamento Assíncrono**: Todas as transações são enviadas para fila RabbitMQ para processamento assíncrono, garantindo desacoplamento.

3. **Controle de Sequência**: Sistema mantém controle de sequência de bloqueios através de tabela específica (TbCotroleBloqueioConta).

4. **Circuit Breaker**: Implementa funcionalidade de circuit breaker para inativar transações em massa em caso de necessidade.

5. **Conversão de Códigos**: Sistema trabalha com conversão entre códigos internos (161) e externos (655) do Banco Votorantim.

6. **Segurança**: Todos os endpoints são protegidos por OAuth2 com validação JWT.

7. **Ambientes**: Configuração para múltiplos ambientes (local, des, uat, prd) com diferentes datasources e filas.

8. **Monitoramento**: Integração com Prometheus para métricas e health checks via Actuator.

9. **Auditoria**: Uso de biblioteca de auditoria BV (springboot-arqt-base-trilha-auditoria-web).

10. **Validação de Saldo**: Sistema considera saldo total, limite, bloqueios, indisponibilidades e transações cash in/out para validar operações.

11. **Prevenção de Duplicidade**: Validação de NSU para evitar processamento duplicado de transações.

12. **Truncamento de Dados**: Descrições de operação são limitadas a 40 caracteres para compatibilidade com banco de dados.