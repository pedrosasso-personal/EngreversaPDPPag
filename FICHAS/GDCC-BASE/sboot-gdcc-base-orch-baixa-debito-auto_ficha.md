# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema orquestrador responsável por processar baixas de débito automático para produtos financeiros (Crédito Pessoal e Financiamento de Veículo). A aplicação consome mensagens de uma fila RabbitMQ contendo informações de remessas de débito automático, processa essas informações e envia para um serviço atômico que realiza a persistência dos dados de baixa. Utiliza Apache Camel para orquestração de rotas e Spring Boot como framework base.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal de inicialização da aplicação Spring Boot |
| `RemessaDTOListener` | Listener que consome mensagens da fila RabbitMQ `gdcc_baixa_debito_automatico` |
| `RemessaDTOservice` | Serviço que processa e envia RemessaDTO para a rota Camel |
| `BaixaDebitoAutoService` | Serviço de domínio que orquestra o processamento de baixa de débito |
| `BaixaDebitoAutoRouter` | Rota Apache Camel que direciona o processamento para o repositório |
| `BaixaDebitoAutoRepositoryImpl` | Implementação do repositório que chama o serviço atômico via REST |
| `BaixaDebitoAutoProcessor` | Processador Camel para manipulação de mensagens |
| `RemessaDTO` | Entidade de domínio representando dados da remessa de débito automático |
| `ApplicationConfiguration` | Configuração de beans e clientes REST para APIs externas |
| `RabbitConfiguration` | Configuração do RabbitMQ e conversores de mensagem |
| `CamelContextWrapper` | Wrapper para gerenciamento do contexto Apache Camel |

---

## 3. Tecnologias Utilizadas

- **Framework:** Spring Boot 2.x
- **Linguagem:** Java 11
- **Orquestração:** Apache Camel 3.0.1
- **Mensageria:** RabbitMQ com Spring AMQP
- **Cliente HTTP:** RestTemplate (Spring)
- **Documentação API:** Swagger/OpenAPI (Springfox 3.0.0)
- **Segurança:** OAuth2 (integração via Gateway)
- **Monitoramento:** Spring Actuator, Prometheus, Grafana
- **Testes:** JUnit 5, Mockito, RestAssured, Pact
- **Build:** Maven
- **Containerização:** Docker
- **Infraestrutura:** OpenShift (Kubernetes)
- **Auditoria:** Biblioteca BV Trilha Auditoria (versão 2.2.1)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| N/A | N/A | N/A | Esta aplicação não expõe endpoints REST próprios. Atua como consumidor de fila e cliente de APIs externas. |

**Observação:** A aplicação consome serviços REST externos através dos clientes configurados em `ApplicationConfiguration`:
- `RealizaBaixaDebitoAutomaticoApi` - para Crédito Pessoal
- `RealizaBaixaDebitoAutomaticoFinanciamentoVeiculoApi` - para Financiamento de Veículo

---

## 5. Principais Regras de Negócio

1. **Consumo de Mensagens:** Consome mensagens da fila `gdcc_baixa_debito_automatico` contendo dados de remessas de débito automático.

2. **Mapeamento de Código de Retorno:** Converte o código de status de pagamento recebido para código de retorno de débito automático através do enum `RetornoDebitoAutomaticoEnum` (DF, CE, SI, CS).

3. **Identificação de Produto:** Determina o nome do produto financeiro baseado no código do produto através do enum `TipoProdutoEnum` (Financiamento de Veículo, Crédito Pessoal, Crédito Fácil).

4. **Autenticação OAuth2:** Obtém token de acesso via `GatewayOAuthService` antes de chamar o serviço atômico.

5. **Tratamento de Erros:** Captura exceções durante o processamento e lança `BaixaDebitoAutoException` com razão `GDCC_BAD_REQUEST`.

6. **Orquestração via Camel:** Utiliza rota Camel (`direct:baixaDebito`) para processar as mensagens de forma assíncrona.

---

## 6. Relação entre Entidades

**Entidades principais:**

- **RemessaDTO:** Entidade central contendo todos os dados da remessa de débito automático
  - Atributos: codigoStatusPagamentoDebitoAutomatico, dataVencimento, dataPagamento, vrPagamento, numeroCpfCnpj, codigoBanco, codigoAgencia, numeroContaCorrente, codigoBancoConvenio, codigoAgenciaConvenio, numeroContaConvenio, numeroContrato, codigoProduto, nomeProduto, numeroSequenciaContratoFinanceiro, numeroParcelaDebito

- **BaixaDebitoAuto:** Entidade de domínio básica (id, version) - aparentemente não utilizada no fluxo principal

- **LogArquivoRequestRepresentation:** Representação gerada pelo Swagger para envio ao serviço atômico, mapeada a partir de RemessaDTO

**Relacionamentos:**
- RemessaDTO é consumida da fila → processada pelos serviços → transformada em LogArquivoRequestRepresentation → enviada ao serviço atômico

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

**Observação:** A persistência é realizada pelo serviço atômico externo (`sboot-gdcc-base-atom-baixa-debito-auto`), não diretamente por esta aplicação.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot | Arquivo de configuração da aplicação com profiles (local, des, qa, uat, prd) |
| logback-spring.xml | leitura | Logback | Configuração de logs da aplicação |
| swagger-cli/sboot-gdcc-base-atom-baixa-debito-auto.yml | leitura | Swagger Codegen Plugin | Especificação OpenAPI do serviço atômico consumido |

---

## 10. Filas Lidas

**Fila:** `gdcc_baixa_debito_automatico`

- **Tipo:** RabbitMQ
- **Exchange:** `ex.gdcc.baixa.debito.automatico` (direct)
- **Routing Key:** `gdcc.baixaDebitoAutomatico`
- **Listener:** `RemessaDTOListener`
- **Formato:** JSON (convertido automaticamente para `RemessaDTO`)
- **Descrição:** Fila que recebe mensagens contendo dados de remessas de débito automático para processamento de baixa

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| `sboot-gdcc-base-atom-baixa-debito-auto` | REST API | Serviço atômico que persiste os dados de baixa de débito automático. Endpoints: `/v1/credito-pessoal/inserir/log-arquivo` e `/v1/financiamento-veiculo/inserir/log-arquivo` |
| API Gateway OAuth2 | REST API | Serviço de autenticação para obtenção de token JWT. Endpoint: `/auth/oauth/v2/token-jwt` |
| RabbitMQ | Message Broker | Sistema de mensageria para consumo de remessas de débito automático |
| Prometheus | Monitoring | Sistema de coleta de métricas da aplicação via endpoint `/actuator/prometheus` |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (application, domain, common)
- Uso adequado de padrões como Repository, Service e configuração via beans Spring
- Implementação de testes unitários, integração e funcionais
- Configuração de profiles para diferentes ambientes
- Uso de Lombok para redução de boilerplate
- Documentação via Swagger/OpenAPI
- Implementação de monitoramento e métricas

**Pontos de Melhoria:**
- Classe `ConsultarContaConvenioMapper` está vazia/comentada, indicando código não utilizado
- Entidade `BaixaDebitoAuto` parece não ser utilizada no fluxo principal
- Tratamento de exceções genérico em alguns pontos (catch Exception)
- Falta de validações mais robustas nos DTOs
- Alguns testes estão vazios ou com implementação mínima
- Configuração de segurança OAuth2 poderia ser mais modular
- Documentação inline (JavaDoc) limitada em algumas classes

O código está bem estruturado e segue boas práticas, mas há espaço para melhorias em tratamento de erros, validações e remoção de código não utilizado.

---

## 14. Observações Relevantes

1. **Arquitetura Hexagonal:** O projeto segue princípios de arquitetura hexagonal com separação clara entre domínio (domain), aplicação (application) e comum (common).

2. **Apache Camel:** Utiliza Apache Camel para orquestração de rotas de processamento, permitindo flexibilidade e desacoplamento.

3. **Multiambiente:** Configuração robusta para múltiplos ambientes (local, des, qa, uat, prd) com uso de variáveis de ambiente e secrets.

4. **Infraestrutura como Código:** Possui configuração completa de infraestrutura (infra.yml) para deploy em OpenShift/Kubernetes.

5. **Observabilidade:** Implementa stack completa de observabilidade com Prometheus, Grafana e dashboards pré-configurados.

6. **Testes Contratuais:** Implementa testes de contrato com Pact para garantir compatibilidade entre serviços.

7. **Segurança:** Integração com API Gateway para autenticação OAuth2 e obtenção de tokens JWT.

8. **Auditoria:** Utiliza biblioteca específica do Banco Votorantim para trilha de auditoria.

9. **Docker:** Configuração completa para containerização da aplicação e serviços auxiliares (RabbitMQ, Prometheus, Grafana).

10. **Validação Arquitetural:** Possui profile Maven específico para validação de regras arquiteturais usando ArchUnit.