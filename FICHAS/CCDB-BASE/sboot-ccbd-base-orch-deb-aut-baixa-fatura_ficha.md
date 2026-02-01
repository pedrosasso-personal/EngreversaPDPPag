# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-ccbd-base-orch-deb-aut-baixa-fatura** é um orquestrador de baixa de faturas de cartão de crédito via débito automático. Ele consome mensagens de uma fila RabbitMQ contendo dados de pagamentos, consulta informações da fatura em um sistema Atom (via API REST), e em seguida atualiza a cobrança do boleto correspondente em outro sistema (CAAPI), aplicando abatimento no valor da fatura. O sistema utiliza Apache Camel para orquestração de fluxos e Spring Boot como framework base.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot que inicializa a aplicação |
| `BaixaFaturaListener` | Listener RabbitMQ que consome mensagens da fila `debito_automatico.baixa.fatura` |
| `BaixaFaturaService` | Serviço de domínio que orquestra o processo de baixa de fatura usando Apache Camel |
| `BaixaFaturaRouter` | Define as rotas Camel para orquestração (objeto único ou lista) |
| `BaixaFaturaRepositoryImpl` | Implementação do repositório que integra com APIs externas (Atom e CAAPI) |
| `BaixaFaturaMapper` | Utilitário para conversão de JSON em objetos de domínio |
| `CamelContextWrapper` | Wrapper do contexto Camel para gerenciamento de rotas |
| `BaixaFaturaConfiguration` | Configuração de beans do Spring |
| `RabbitMqConfiguration` | Configuração de conexão e listeners RabbitMQ |
| `RestConfiguration` | Configuração de clientes REST para APIs externas |
| `GatewayOAuthServiceConfig` | Configuração de autenticação OAuth2 para chamadas externas |

---

## 3. Tecnologias Utilizadas

- **Spring Boot** (framework base)
- **Apache Camel 3.0.1** (orquestração de fluxos)
- **RabbitMQ** (mensageria)
- **Spring AMQP** (integração com RabbitMQ)
- **RestTemplate** (cliente HTTP)
- **OAuth2** (autenticação via Gateway)
- **Swagger/OpenAPI** (documentação de APIs)
- **Springfox 3.0.0** (geração de documentação Swagger)
- **Lombok** (redução de boilerplate)
- **Jackson** (serialização/deserialização JSON)
- **MapStruct** (mapeamento de objetos)
- **JUnit 5** (testes unitários)
- **Mockito** (mocks em testes)
- **Pact** (testes de contrato)
- **Rest Assured** (testes funcionais)
- **Micrometer/Prometheus** (métricas)
- **Logback** (logging)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)

---

## 4. Principais Endpoints REST

não se aplica

(O sistema não expõe endpoints REST próprios; ele apenas consome de fila RabbitMQ e chama APIs externas)

---

## 5. Principais Regras de Negócio

1. **Consumo de mensagens de débito automático**: O sistema escuta a fila `debito_automatico.baixa.fatura` e processa pagamentos de faturas de cartão.

2. **Identificação de fatura**: A partir do código `cdSeuNumero` (15 dígitos), extrai-se emissor (4 dígitos), produto (2 dígitos) e conta cartão (9 dígitos) para consultar dados da fatura no sistema Atom.

3. **Consulta de dados da fatura**: Chama API do Atom (`TransacoesCartaoApi.recuperarDadosDeFatura`) para obter o número do nosso número do boleto associado à fatura.

4. **Atualização de cobrança**: Com o nosso número obtido, chama API CAAPI (`AtualizarCobrancaBoletosApi.atualizarCobrancaBoletos`) para aplicar instrução de abatimento (código 4) no valor do pagamento.

5. **Processamento em lote ou individual**: O sistema suporta processar um único pagamento (`pagamentoDebitoAutomatico`) ou uma lista de pagamentos (`listaPagamentoDebitoAutomatico`).

6. **Tratamento de erros**: Em caso de falha nas chamadas externas, o sistema loga o erro e retorna resposta com código 500 e mensagem "Requisicao Invalida".

7. **Autenticação OAuth2**: Todas as chamadas externas utilizam token OAuth2 obtido via `GatewayOAuthService`.

---

## 6. Relação entre Entidades

**Entidades de Domínio:**

- `BaixaFaturaRequestDomain`: Representa a requisição de baixa de fatura, contendo `LotePagamentosDomain`
- `LotePagamentosDomain`: Contém `PagamentoDebitoAutomaticoDomain` (objeto único) ou `listaPagamentoDebitoAutomatico` (lista)
- `PagamentoDebitoAutomaticoDomain` / `BaixaFaturaDomain`: Dados do pagamento (CPF/CNPJ, código seu número, valor, data vencimento)
- `CobrancaPropriaRequestDomain`: Requisição para atualização de cobrança (convênio, nosso número, instrução)
- `InstrucaoDomain`: Instrução de cobrança (código 4 = abatimento)
- `AbatimentoDomain`: Valor do abatimento a ser aplicado
- `CobrancaPropriaResponseDomain`: Resposta da atualização de cobrança
- `RetornoDomain`: Código e mensagem de retorno

**Relacionamentos:**
- `BaixaFaturaRequestDomain` 1 ---> 1 `LotePagamentosDomain`
- `LotePagamentosDomain` 1 ---> 0..1 `PagamentoDebitoAutomaticoDomain`
- `LotePagamentosDomain` 1 ---> 0..* `BaixaFaturaDomain`
- `CobrancaPropriaRequestDomain` 1 ---> 1 `InstrucaoDomain`
- `InstrucaoDomain` 1 ---> 1 `AbatimentoDomain`
- `CobrancaPropriaResponseDomain` 1 ---> 1 `RetornoDomain`

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

(O sistema não acessa diretamente banco de dados; todas as operações são via APIs REST)

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

(O sistema não acessa diretamente banco de dados; todas as operações são via APIs REST)

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `logback-spring.xml` | leitura | `/usr/etc/log` (configurado via ConfigMap) | Arquivo de configuração de logs, carregado em runtime conforme ambiente |
| `application.yml` | leitura | `application/src/main/resources` | Arquivo de configuração da aplicação Spring Boot |
| Arquivos Swagger YAML | leitura | `application/src/main/resources/swagger` | Especificações OpenAPI para geração de clientes REST |

---

## 10. Filas Lidas

- **Fila**: `debito_automatico.baixa.fatura`
- **Exchange**: `ex.ccbd.debito.automatico`
- **Tecnologia**: RabbitMQ
- **Classe consumidora**: `BaixaFaturaListener`
- **Método**: `rabbitMqQueue(@Payload String jsonEntrada)`
- **Formato**: JSON contendo `BaixaFaturaRequestDomain`

---

## 11. Filas Geradas

não se aplica

(O sistema não publica mensagens em filas; apenas consome)

---

## 12. Integrações Externas

| Sistema/API | Tipo | Descrição |
|-------------|------|-----------|
| **Atom - Fatura Cartão** | API REST | Consulta dados de fatura de cartão (endpoint: `v2/trasacao-cartao-credito/contaCartao/{numeroContaCartao}/produto/{codigoProduto}/emissor/{codigoEmissor}/recuperarDadosFatura`). Retorna informações do boleto associado à fatura. |
| **CAAPI - Cobrança Boletos** | API REST | Atualiza cobrança de boletos aplicando instrução de abatimento (endpoint: `v1/atacado/cobranca/boletos/atualizar`). |
| **API Gateway OAuth2** | Serviço de autenticação | Fornece tokens OAuth2 para autenticação nas chamadas às APIs externas. |
| **RabbitMQ** | Fila de mensagens | Recebe mensagens de débito automático para processamento de baixa de faturas. |

**URLs por ambiente:**
- **DES**: 
  - Atom: `https://sboot-cart-base-fatura-cartao.appdes.bvnet.bv`
  - CAAPI: `https://apigatewaydes.bvnet.bv`
- **QA**: 
  - Atom: `https://sboot-cart-base-fatura-cartao.appqa.bvnet.bv`
  - CAAPI: `https://apigatewayqa.bvnet.bv`
- **UAT**: 
  - Atom: `https://sboot-cart-base-fatura-cartao.appuat.bvnet.bv`
  - CAAPI: `https://apigatewayuat.bvnet.bv`
- **PRD**: 
  - Atom: `https://sboot-cart-base-fatura-cartao.app.bvnet.bv`
  - CAAPI: `https://apigateway.bvnet.bv`

---

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades em camadas (application, domain, common)
- Uso adequado de padrões como Repository, Service e Domain-Driven Design
- Configuração externalizada e parametrizada por ambiente
- Testes unitários presentes (cobertura razoável)
- Uso de Lombok reduz boilerplate
- Logging estruturado e adequado
- Uso de Apache Camel para orquestração é apropriado
- Configuração de segurança OAuth2 bem implementada

**Pontos de Melhoria:**
- Tratamento de exceções genérico (catch Exception) em vários pontos, sem diferenciação de tipos de erro
- Falta de validação de entrada mais robusta (ex: validação de formato de `cdSeuNumero`)
- Código de parsing de `cdSeuNumero` (substring) é frágil e poderia ser encapsulado em método específico com validações
- Alguns testes unitários com mocks muito simples, não testando cenários de erro
- Falta de documentação JavaDoc em classes e métodos
- Variáveis de configuração hardcoded em alguns testes
- Listener não injeta o service corretamente (campo `service` não é `@Autowired`)
- Código duplicado entre `realizarBaixaFaturaObjeto` e `realizarBaixaFaturaLista`
- Falta de circuit breaker ou retry para chamadas externas
- Mensagens de log poderiam ser mais descritivas em alguns pontos

---

## 14. Observações Relevantes

1. **Arquitetura Hexagonal**: O projeto segue princípios de arquitetura hexagonal com separação clara entre domínio (domain), aplicação (application) e infraestrutura (ports/adapters).

2. **Geração de código**: Utiliza Swagger Codegen Maven Plugin para gerar automaticamente clientes REST a partir de especificações OpenAPI.

3. **Multi-módulo Maven**: Projeto estruturado em módulos (application, domain, common) para melhor organização.

4. **Configuração por ambiente**: Utiliza profiles Spring (`local`, `des`, `qa`, `uat`, `prd`) com configurações específicas por ambiente.

5. **Infraestrutura como código**: Possui arquivo `infra.yml` para deploy em Kubernetes/OpenShift com ConfigMaps e Secrets.

6. **Observabilidade**: Integrado com Prometheus para métricas e possui endpoints Actuator para health checks.

7. **Segurança**: Implementa OAuth2 Resource Server e integração com API Gateway do Banco Votorantim.

8. **Testes**: Estrutura de testes separada em unit, integration e functional, com suporte a testes de contrato (Pact).

9. **Containerização**: Dockerfile otimizado usando OpenJDK 11 com OpenJ9 (Alpine) para imagens leves.

10. **Auditoria**: Integrado com biblioteca de trilha de auditoria do Banco Votorantim (`springboot-arqt-base-trilha-auditoria-web`).

11. **Limitação conhecida**: O listener `BaixaFaturaListener` possui o campo `service` não injetado corretamente, o que pode causar NullPointerException em runtime. Deveria usar `@Autowired` ou injeção via construtor.

12. **Convenção de nomenclatura**: Segue padrão de nomenclatura do Banco Votorantim com prefixos `sboot-ccbd-base-orch-deb-aut`.