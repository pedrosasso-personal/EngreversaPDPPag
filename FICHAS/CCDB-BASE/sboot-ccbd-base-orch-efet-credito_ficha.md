# Ficha Técnica do Sistema

## 1. Descrição Geral
Sistema orquestrador responsável por efetivar movimentações de crédito em conta corrente do Banco Digital. O sistema implementa um fluxo de orquestração que valida se há transações pendentes no Stand-In (sistema de contingência), tenta efetivar o crédito na conta corrente principal e, em caso de indisponibilidade ou transações pendentes, direciona a operação para o Stand-In. Utiliza Apache Camel para orquestração de fluxos e Spring Boot como framework base.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `EfetCreditoController` | Controller REST que recebe requisições de efetivação de crédito |
| `EfetCreditoService` | Serviço de domínio que coordena a execução do fluxo via Camel |
| `EfetCreditoRouter` | Define a rota Camel para orquestração do fluxo de efetivação |
| `EfetCreditoRepositoryImpl` | Implementação que efetiva crédito na conta corrente principal |
| `EfetCreditoStandinRepositoryImpl` | Implementação que efetiva crédito no sistema Stand-In |
| `ConsultarTransacaoStandinRepositoryImpl` | Consulta transações pendentes no Stand-In |
| `EfetCreditoMapper` | Converte representações de requisição para objetos de domínio |
| `ValidaContasStandin` | Valida se a conta está habilitada para operação Stand-In |
| `ErrorFormat` | Utilitário para formatação e conversão de erros |
| `AppProperties` | Configurações da aplicação (URLs de serviços, listas de contas) |
| `EfetCredito` | Entidade de domínio representando a operação de crédito |
| `InfoConta` | Value Object com informações da conta corrente |

## 3. Tecnologias Utilizadas
- **Spring Boot** (framework base)
- **Apache Camel 3.0.1** (orquestração de fluxos)
- **Spring Security OAuth2** (autenticação e autorização com JWT)
- **Springfox/Swagger** (documentação de API)
- **Micrometer/Prometheus** (métricas e monitoramento)
- **Logback** (logging)
- **RestTemplate** (cliente HTTP)
- **Lombok** (redução de boilerplate)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **GCP (Google Cloud Platform)** (infraestrutura)
- **JUnit 5** (testes unitários)
- **Pact** (testes de contrato)

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/banco-digital/contas/credito` | `EfetCreditoController` | Efetiva movimentação de crédito em conta corrente. Recebe headers com dados da conta (codigoBanco, numeroAgencia, numeroConta, tipoConta) e body com dados da operação |

## 5. Principais Regras de Negócio
1. **Validação de Conta Stand-In**: Verifica se a conta está na lista de contas permitidas para operação Stand-In
2. **Consulta de Transações Pendentes**: Antes de efetivar, consulta se há transações pendentes no Stand-In para a conta
3. **Fluxo de Contingência**: Se a conta corrente principal estiver indisponível (HTTP 307) ou houver transações pendentes, direciona para Stand-In
4. **Efetivação Condicional no Stand-In**: Só efetiva no Stand-In se a conta estiver habilitada E (houver transações pendentes OU conta corrente indisponível)
5. **Propagação de Headers**: Informações da conta são propagadas via headers HTTP nas chamadas aos serviços downstream
6. **Validação de Stand-In**: Flag `STANDIN` (constante true) controla se o sistema Stand-In está online
7. **Tratamento de Erros**: Erros HTTP 4xx e 5xx são convertidos em exceções de negócio customizadas

## 6. Relação entre Entidades

**EfetCredito** (entidade principal)
- Contém: `InfoConta` (composição)
- Atributos: dados da operação (valor, data, protocolo, códigos de transação/liquidação, flags de controle)
- Flags de controle: `transacaoPendenteStandin`, `contaCorrenteIndisponivel`

**InfoConta** (value object)
- Atributos: codigoBanco, agencia, conta, tipoConta
- Utilizado para identificação da conta nas operações

**Relacionamento**: EfetCredito possui (has-a) InfoConta, representando uma operação de crédito em uma conta específica.

## 7. Estruturas de Banco de Dados Lidas

não se aplica

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `application.yml` | leitura | Spring Boot (startup) | Arquivo de configuração da aplicação com propriedades, URLs de serviços, configurações de segurança |
| `logback-spring.xml` | leitura | Logback (runtime) | Configuração de logging (níveis, appenders, formato) |
| `sboot-ccbd-base-orch-efet-credito.yaml` | leitura | Swagger Codegen (build time) | Especificação OpenAPI para geração de interfaces REST |

## 10. Filas Lidas

não se aplica

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| `sboot-ccbd-base-atom-conta-corrente` | REST API | Serviço atômico de conta corrente para efetivação de crédito no sistema principal |
| `sboot-ccbd-base-atom-conta-corrente-stdin` (consulta) | REST API | Serviço de consulta de transações pendentes no Stand-In |
| `sboot-ccbd-base-atom-conta-corrente-stdin` (efetivação) | REST API | Serviço de efetivação de crédito no sistema Stand-In (contingência) |
| OAuth2 JWT Provider | REST API | Serviço de autenticação e autorização (tokenUrl configurável por ambiente) |

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com módulos domain e application
- Uso adequado de padrões como Repository, Service e Controller
- Implementação de orquestração com Apache Camel demonstra conhecimento de integração
- Configuração externalizada e suporte a múltiplos ambientes
- Presença de testes (unitários, integração, funcionais)
- Uso de Lombok reduz boilerplate
- Documentação via Swagger/OpenAPI

**Pontos de Melhoria:**
- Constantes hardcoded (`STANDIN = true`, `FINTECH = false`) deveriam ser configuráveis
- Método `ValidaContasStandin.verificarListaConta()` sempre retorna `true`, ignorando parâmetros
- Tratamento de exceções genérico em alguns pontos (catch de `Exception`)
- Falta de validações de entrada mais robustas
- Logs poderiam ser mais estruturados (uso de MDC para correlationId)
- Ausência de circuit breaker ou retry para chamadas externas
- Código de conversão de erros poderia ser mais elegante
- Falta documentação inline em métodos mais complexos

O código é funcional e bem estruturado, mas há espaço para melhorias em resiliência, configurabilidade e tratamento de erros.

## 14. Observações Relevantes

1. **Arquitetura Hexagonal**: O projeto segue princípios de arquitetura hexagonal com separação clara entre domain (regras de negócio) e application (infraestrutura)

2. **Orquestração com Camel**: O uso do Apache Camel para orquestração é interessante, mas para um fluxo relativamente simples pode ser considerado over-engineering

3. **Sistema Stand-In**: Implementa padrão de contingência para garantir disponibilidade mesmo quando o sistema principal está indisponível

4. **Segurança**: Implementa OAuth2 com JWT, mas endpoints públicos incluem Swagger (adequado apenas para ambientes de desenvolvimento)

5. **Observabilidade**: Boa instrumentação com Actuator, Prometheus e logs estruturados

6. **Multi-ambiente**: Configuração preparada para múltiplos ambientes (des, qa, uat, prd) com URLs específicas

7. **Deployment**: Preparado para Kubernetes/OpenShift com configurações de probes, service accounts e volumes

8. **Validação de Contas Stand-In**: A lista de contas permitidas é configurável por ambiente, mas a implementação atual sempre retorna `true`

9. **Flags de Controle**: Uso de flags booleanas (`transacaoPendenteStandin`, `contaCorrenteIndisponivel`) para controlar o fluxo de execução

10. **Versionamento de API**: Usa versionamento via path (`/v1/`) seguindo boas práticas REST