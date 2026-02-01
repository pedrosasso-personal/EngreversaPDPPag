# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-ccbd-base-orch-processa-stdin** é um serviço de orquestração desenvolvido em Spring Boot que processa transações financeiras stand-in (operações offline/contingência) de contas correntes do Banco Digital. O sistema consome mensagens de uma fila RabbitMQ, valida o status das contas, efetiva operações de débito, crédito ou TEF (Transferência Entre Contas) através de chamadas a APIs externas, e inativa as transações stand-in após o processamento. Implementa mecanismo de retry para garantir que as operações sejam processadas apenas quando as contas estiverem abertas.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `ProcessaStdinListener` | Listener RabbitMQ que consome mensagens da fila `ccbd_liquida_standin` e inicia o processamento |
| `ProcessaStdinService` | Serviço de domínio que orquestra o fluxo de liquidação baseado no tipo de transação (D/C/TEF) |
| `ProcessaStdinRouter` | Roteador Apache Camel que define as rotas de processamento com retry automático |
| `ProcessaStdinMapper` | Mapper que converte DTOs de entrada em objetos de domínio |
| `StatusContaRepositoryImpl` | Verifica se a conta corrente está aberta/disponível para operação |
| `EfetDebitoRepositoryImpl` | Efetiva operações de débito em conta corrente |
| `EfetCreditoRepositoryImpl` | Efetiva operações de crédito em conta corrente |
| `EfetTefRepositoryImpl` | Efetiva transferências entre contas (TEF) |
| `CancelarDebitoRepositoryImpl` | Cancela débitos previamente bloqueados |
| `InativarTransacaoRepositoryImpl` | Inativa transações stand-in após processamento |
| `GerarTokenJwtRepositoryImpl` | Gera token JWT para autenticação nas APIs |
| `Operacao` | Entidade de domínio que representa uma operação financeira |
| `Transacao` | Entidade que representa transações de débito/crédito |
| `TransacaoTef` | Entidade que representa transações TEF |

## 3. Tecnologias Utilizadas

- **Framework**: Spring Boot 2.x
- **Linguagem**: Java 11
- **Mensageria**: RabbitMQ com Spring AMQP
- **Orquestração**: Apache Camel 3.0.1
- **Cliente HTTP**: RestTemplate (Spring)
- **Documentação API**: Swagger/OpenAPI (Springfox 3.0.0)
- **Monitoramento**: Spring Actuator + Micrometer Prometheus
- **Logging**: Logback com formato JSON
- **Build**: Maven
- **Containerização**: Docker
- **Auditoria**: Biblioteca BV Trilha Auditoria (2.2.1)
- **Testes**: JUnit 5, Mockito, Rest Assured, Pact (4.0.3)
- **Utilitários**: Lombok, Apache Commons Lang3

## 4. Principais Endpoints REST

Não se aplica. Este é um serviço orientado a eventos (event-driven) que consome mensagens de filas RabbitMQ. Não expõe endpoints REST de negócio, apenas endpoints de monitoramento via Actuator.

**Endpoints de Monitoramento:**
- `GET /actuator/health` (porta 9090) - Health check
- `GET /actuator/metrics` (porta 9090) - Métricas
- `GET /actuator/prometheus` (porta 9090) - Métricas formato Prometheus

## 5. Principais Regras de Negócio

1. **Validação de Status da Conta**: Antes de processar qualquer operação, verifica se a conta corrente está aberta/disponível. Se estiver fechada, entra em retry por até 180 minutos (tentativas a cada 30 segundos).

2. **Tipos de Transação**: Suporta três tipos de operações:
   - **D (Débito)**: Efetiva débito ou cancela débito previamente bloqueado
   - **C (Crédito)**: Efetiva crédito em conta
   - **TEF**: Transferência entre contas (débito em uma conta e crédito em outra)

3. **Débito com NSU vs Débito Legado**: Para débitos, se houver NSU (Número Sequencial Único), utiliza o serviço de confirmação de débito; caso contrário, utiliza o serviço de cancelamento de débito bloqueado.

4. **Débito com Bloqueio**: Diferencia entre débito com sequência de bloqueio (novo) e débito legado (sem sequência de bloqueio), direcionando para endpoints diferentes.

5. **Autenticação JWT**: Gera token JWT via OAuth2 (client_credentials) para autenticar todas as chamadas às APIs de conta corrente.

6. **Inativação de Transação Stand-in**: Após processar com sucesso qualquer operação, inativa a transação stand-in correspondente para evitar reprocessamento.

7. **Tratamento de Erros**: Erros nas chamadas HTTP resultam em exceção `ProcessaStdinException`, encerrando o processamento da mensagem.

8. **Stand-in Flag**: Todas as operações são marcadas com `standIn=true` nos headers das requisições.

## 6. Relação entre Entidades

**Entidades Principais:**

- **Operacao**: Entidade raiz que contém:
  - `tipoTransacao` (D/C/TEF)
  - `TokenAuthorization` (token JWT)
  - Dados da conta (codigoBanco, agencia, numeroContaCorrente, codigoTipoConta)
  - `Transacao` (para débito/crédito) OU `TransacaoTef` (para TEF)

- **Transacao**: Representa débito ou crédito:
  - Dados da operação (valor, NSU, protocolo, data)
  - Sequência de bloqueio de saldo
  - Código de liquidação e transação

- **TransacaoTef**: Representa transferência entre contas:
  - `Conta` remetente
  - `Conta` favorecido
  - Dados da operação (valor, NSU, protocolo)
  - Códigos de transação para remetente e favorecido

- **Conta**: Dados bancários (codigoBanco, numeroAgencia, numeroConta, tipoConta)

- **TokenAuthorization**: Token JWT com access_token, tipo, expiração e scope

**Relacionamentos:**
- Operacao 1 --- 0..1 Transacao
- Operacao 1 --- 0..1 TransacaoTef
- TransacaoTef 1 --- 1 Conta (remetente)
- TransacaoTef 1 --- 1 Conta (favorecido)
- Operacao 1 --- 1 TokenAuthorization

## 7. Estruturas de Banco de Dados Lidas

Não se aplica. O sistema não acessa diretamente banco de dados. Todas as operações são realizadas via APIs REST.

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema não acessa diretamente banco de dados. Todas as operações de atualização são realizadas via APIs REST que, por sua vez, atualizam as estruturas de dados.

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | Spring Boot (startup) | Arquivo de configuração da aplicação com profiles (local, des, qa, uat, prd) |
| logback-spring.xml | Leitura | Logback (startup) | Configuração de logs em formato JSON para stdout |
| /usr/etc/log/logback-spring.xml | Leitura | Logback (ambientes) | Configuração de logs específica por ambiente (montada via ConfigMap) |

## 10. Filas Lidas

**Fila Consumida:**
- **Nome**: `ccbd_liquida_standin`
- **Tecnologia**: RabbitMQ
- **Formato**: JSON
- **Listener**: `ProcessaStdinListener`
- **Descrição**: Fila que recebe notificações de transações stand-in (débito, crédito ou TEF) que precisam ser liquidadas/efetivadas quando as contas estiverem disponíveis

**Estrutura da Mensagem (NotificacaoInbound):**
- Tipo de transação (D/C/TEF)
- Dados da conta (banco, agência, conta, tipo)
- Dados da transação (valor, NSU, protocolo, códigos)
- Para TEF: dados da conta favorecida
- Datas de movimentação e comando

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas, apenas consome.

## 12. Integrações Externas

| Sistema/API | Tipo | Descrição |
|-------------|------|-----------|
| **API Gateway OAuth** | REST | Geração de token JWT para autenticação (endpoint: `/auth/oauth/v2/token-jwt`) |
| **sboot-ccbd-base-atom-conta-corrente** | REST | API de conta corrente com múltiplos endpoints: status da conta, crédito, débito, débito legado, TEF, cancelamento de débito |
| **sboot-ccbd-base-atom-conta-corrente-stdin** | REST | API para inativação de transações stand-in após processamento |

**Endpoints Integrados:**
1. `/v1/banco-digital/conta/status` - Verifica status da conta (aberta/fechada)
2. `/v1/banco-digital/contas/credito` - Efetiva crédito
3. `/v1/banco-digital/contas/debito/confirmar` - Confirma débito com bloqueio
4. `/v1/banco-digital/contas/debito-legado/confirmar` - Confirma débito legado (sem bloqueio)
5. `/v1/banco-digital/contas/tef` - Efetiva transferência entre contas
6. `/v1/banco-digital/contas/bloqueio/cancelar` - Cancela débito bloqueado
7. `/v1/banco-digital/contas/transacao/inativar` - Inativa transação stand-in

**Autenticação**: Todas as chamadas utilizam Bearer Token (JWT) no header Authorization.

## 13. Avaliação da Qualidade do Código

**Nota: 7,5/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões hexagonais (ports/adapters)
- Separação clara entre camadas (application, domain, common)
- Uso adequado de Apache Camel para orquestração com retry automático
- Implementação de mecanismo de retry robusto para garantir processamento
- Uso de Lombok reduzindo boilerplate
- Configuração por profiles bem organizada
- Logs estruturados em JSON
- Testes unitários, integração e funcionais separados

**Pontos de Melhoria:**
- Código comentado no `ProcessaStdinRouter` (geração de token) indica possível inconsistência
- Falta tratamento de exceções mais granular (todos os erros HTTP viram `ProcessaStdinException`)
- Ausência de circuit breaker para chamadas externas
- `StatusContaRepositoryImpl` duplica lógica de geração de token (deveria usar `GerarTokenJwtRepository`)
- Falta validação de dados de entrada mais robusta
- Ausência de testes de contrato (Pact configurado mas não utilizado)
- Documentação inline escassa
- Hardcoded de valores como tempo de retry (180 minutos, 30 segundos)

## 14. Observações Relevantes

1. **Mecanismo de Retry**: O sistema implementa retry inteligente que aguarda até 180 minutos (2 horas) com tentativas a cada 30 segundos quando a conta está fechada, garantindo que operações stand-in sejam processadas assim que possível.

2. **Inconsistência de Token**: Há código comentado nas rotas Camel para geração de token, mas o `StatusContaRepositoryImpl` gera seu próprio token. Isso pode indicar refatoração incompleta.

3. **Ambientes**: Suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas via profiles Spring.

4. **Monitoramento**: Expõe métricas Prometheus na porta 9090 para observabilidade.

5. **Auditoria**: Integra biblioteca BV de trilha de auditoria para rastreabilidade.

6. **Segurança**: Utiliza OAuth2 client_credentials flow para autenticação máquina-a-máquina.

7. **Containerização**: Dockerfile otimizado usando OpenJ9 Alpine com configurações de memória JVM.

8. **Infraestrutura como Código**: Possui arquivo `infra.yml` para deploy em Kubernetes/OpenShift com ConfigMaps, Secrets e probes configurados.

9. **RabbitMQ Local**: Inclui docker-compose para execução local do RabbitMQ com configurações pré-definidas.

10. **Arquitetura Multi-módulo**: Projeto Maven organizado em módulos (common, domain, application) seguindo boas práticas de separação de responsabilidades.