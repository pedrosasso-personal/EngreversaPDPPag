# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-ccbd-base-orch-efet-tef-digital** é um microserviço orquestrador responsável por realizar transferências eletrônicas de fundos (TEF) internas em contas correntes do Banco Votorantim. O sistema atua como uma camada de orquestração que coordena chamadas a múltiplos serviços atômicos (conta corrente, stand-in, bloqueios de saldo, monitoramento) para efetivar operações de transferência, incluindo tratamento de cenários de contingência (stand-in) quando o sistema principal está indisponível. Suporta também efetivação de TEF a partir de monitoramentos de saldo previamente criados.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **EfetTefController** | Controller REST que expõe os endpoints para efetivação de TEF e TEF com monitoramento |
| **EfetTefService** | Serviço de domínio que orquestra o fluxo de efetivação de TEF simples |
| **EfetTefMonitoramentoService** | Serviço de domínio que orquestra o fluxo de efetivação de TEF a partir de monitoramento |
| **EfetTefRouter** | Rota Camel para processamento de TEF simples |
| **EfetTefMonitoramentoRouter** | Rota Camel para processamento de TEF com monitoramento, incluindo cancelamento de bloqueios |
| **EnriqueceTefMonitoramentoProcessor** | Processor Camel que enriquece dados do TEF consultando informações do monitoramento |
| **CancelarBloqueiosMonitoramentoProcessor** | Processor Camel que cancela bloqueios de saldo após efetivação |
| **EfetTefRepositoryImpl** | Implementação de repositório que efetiva TEF no sistema de conta corrente |
| **EfetTefStandinRepositoryImpl** | Implementação de repositório que efetiva TEF no sistema stand-in (contingência) |
| **ConsultarTransacaoStandinRepositoryImpl** | Implementação de repositório que consulta transações pendentes no stand-in |
| **CancelarBloqueioRepositoryImpl** | Implementação de repositório que cancela bloqueios de saldo |
| **ConsultaMonitoramentoRepositoryImpl** | Implementação de repositório que consulta dados de monitoramento de saldo |
| **InativarMonitoramentoRepositoryImpl** | Implementação de repositório que inativa monitoramento após processamento |
| **EfetTef** | Entidade de domínio representando uma transferência eletrônica de fundos |
| **EfetTefMonitoramento** | Entidade de domínio representando TEF vinculado a monitoramento |
| **MonitoramentoSaldo** | Entidade de domínio representando monitoramento de saldo |
| **BloqueioSaldo** | Entidade de domínio representando bloqueio de saldo |
| **Conta** | Entidade de domínio representando dados de conta bancária |
| **ValidaContasStandin** | Utilitário para validação de contas elegíveis para stand-in |
| **ErrorFormat** | Utilitário para formatação e conversão de erros |

---

## 3. Tecnologias Utilizadas

- **Spring Boot** (framework base)
- **Apache Camel 3.0.1** (orquestração e roteamento de mensagens)
- **Spring Security OAuth2** (autenticação e autorização via JWT)
- **Springfox/Swagger** (documentação de API)
- **RestTemplate** (cliente HTTP para integração com serviços)
- **Lombok** (redução de boilerplate)
- **Logback** (logging)
- **Micrometer/Prometheus** (métricas)
- **Spring Actuator** (health checks e monitoramento)
- **JUnit 5** (testes unitários)
- **Pact** (testes de contrato)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Kubernetes/OpenShift** (orquestração de containers)
- **Java 11**

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/banco-digital/contas/tef` | EfetTefController | Efetiva uma transferência eletrônica de fundos (TEF) |
| POST | `/v1/banco-digital/contas/tef/monitoramento/{cdMonitoramentoSaldo}` | EfetTefController | Efetiva TEF a partir de um monitoramento de saldo existente |

---

## 5. Principais Regras de Negócio

1. **Validação de Stand-In**: Verifica se a conta está na lista de contas elegíveis para operação em modo stand-in (contingência)
2. **Consulta de Transações Pendentes**: Antes de efetivar, consulta se há transações pendentes no stand-in para a conta remetente
3. **Roteamento Condicional**: Se houver transação pendente no stand-in OU se o sistema de conta corrente estiver indisponível, roteia para efetivação no stand-in
4. **Efetivação Principal**: Tenta efetivar no sistema principal de conta corrente
5. **Efetivação Stand-In**: Em caso de indisponibilidade ou transação pendente, efetiva no sistema stand-in
6. **Enriquecimento de Dados**: Para TEF com monitoramento, enriquece dados consultando informações do monitoramento
7. **Validação de Monitoramento Ativo**: Valida se o monitoramento está ativo antes de processar
8. **Cálculo de Valor**: Calcula valor total da operação somando valores de bloqueios associados ao monitoramento
9. **Cancelamento de Bloqueios**: Após efetivação bem-sucedida, cancela bloqueios de saldo associados
10. **Inativação de Monitoramento**: Após processamento completo, inativa o monitoramento
11. **Tratamento de Erros**: Converte erros de serviços externos em exceções de negócio padronizadas
12. **Lançamento Incondicional**: Suporta flag para lançamento sem validação de saldo

---

## 6. Relação entre Entidades

- **EfetTef** possui:
  - 1 **Conta** remetente
  - 1 **Conta** favorecido
  
- **EfetTefMonitoramento** herda de **EfetTef** e adiciona:
  - Referência a código de monitoramento (cdMonitoramentoSaldo)

- **MonitoramentoSaldo** possui:
  - Lista de **BloqueioSaldo**
  - Dados de conta (banco, agência, conta, tipo)

- **BloqueioSaldo** contém:
  - Sequencial do bloqueio
  - Valor da operação

---

## 7. Estruturas de Banco de Dados Lidas

Não se aplica. O sistema não acessa diretamente banco de dados, apenas consome APIs REST de outros microserviços.

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema não atualiza diretamente banco de dados, apenas invoca APIs REST de outros microserviços que realizam as operações de persistência.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | Leitura | /usr/etc/log/ (runtime) | Arquivo de configuração de logs, carregado em tempo de execução |
| application.yml | Leitura | Classpath resources | Arquivo de configuração da aplicação com profiles (local, des, qa, uat, prd) |

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

---

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas.

---

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| **sboot-ccbd-base-atom-conta-corrente** | API REST | Serviço atômico de conta corrente para efetivação de TEF e cancelamento de bloqueios |
| **sboot-ccbd-base-atom-conta-corrente-stdin** | API REST | Serviço atômico de conta corrente stand-in para operações em modo contingência |
| **sboot-ccbd-base-atom-bloqueios-saldo** | API REST | Serviço atômico de gerenciamento de bloqueios e monitoramentos de saldo |
| **OAuth2 JWT Provider** | OAuth2/JWT | Servidor de autenticação para validação de tokens JWT (diferentes URLs por ambiente) |

**Endpoints integrados:**
- POST `/v1/banco-digital/contas/tef/` - Efetivação de TEF
- GET `/v1/banco-digital/contas/transacao` - Consulta transações stand-in
- POST `/v1/banco-digital/contas/bloqueio/cancelar` - Cancelamento de bloqueios
- GET `/v1/contas/monitoramentos/{id}` - Consulta monitoramento
- DELETE `/v1/contas/monitoramentos/{id}` - Inativação de monitoramento

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (domain/application)
- Uso adequado de padrões como Repository, Service e Controller
- Utilização de Apache Camel para orquestração, facilitando manutenção de fluxos
- Tratamento de exceções estruturado com enums e classes específicas
- Configuração externalizada por profiles
- Uso de Lombok reduzindo boilerplate
- Documentação via Swagger/OpenAPI
- Testes estruturados (unit, integration, functional)

**Pontos de Melhoria:**
- Classe `ValidaContasStandin` possui método que sempre retorna `true` (flag hardcoded), ignorando parâmetros
- Uso de `@SneakyThrows` em configuração pode ocultar problemas
- Falta de validações de entrada mais robustas nos controllers
- Alguns métodos poderiam ter melhor tratamento de null safety
- Logs poderiam ser mais estruturados com MDC para rastreabilidade
- Falta de circuit breaker para chamadas externas (resiliência)
- Configuração de timeouts não explícita para RestTemplate
- Alguns nomes de variáveis em português misturados com inglês
- Falta de cache para consultas repetitivas

---

## 14. Observações Relevantes

1. **Modo Stand-In**: O sistema possui lógica de contingência (stand-in) para operar quando o sistema principal está indisponível, garantindo continuidade do negócio.

2. **Lista de Contas Stand-In**: Existe uma lista configurável de contas elegíveis para operação stand-in, porém a validação atual está desabilitada (sempre retorna true).

3. **Monitoramento de Saldo**: Suporta efetivação de TEF vinculada a monitoramentos de saldo, com cancelamento automático de bloqueios após sucesso.

4. **Segurança**: Utiliza OAuth2 com JWT para autenticação, com diferentes provedores por ambiente.

5. **Observabilidade**: Possui endpoints Actuator, métricas Prometheus e logs estruturados em JSON.

6. **Multi-ambiente**: Configuração preparada para múltiplos ambientes (des, qa, uat, prd) com URLs específicas.

7. **Containerização**: Preparado para deploy em Kubernetes/OpenShift com configurações de probes, volumes e secrets.

8. **Arquitetura Hexagonal**: Utiliza ports (interfaces) e adapters (implementações) para desacoplamento.

9. **Tratamento de Redirecionamento**: Trata HTTP 307 (Temporary Redirect) como indicador de indisponibilidade do sistema.

10. **Auditoria**: Integração com biblioteca de trilha de auditoria do Banco Votorantim.