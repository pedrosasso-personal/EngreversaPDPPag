# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema orquestrador de validação de pagamentos via boleto, desenvolvido em Spring Boot. O sistema consome mensagens de uma fila PubSub (Google Cloud), realiza validações de negócio consultando serviços externos (dias úteis, dados bancários, contas de clientes), executa a validação do pagamento e publica o resultado em outra fila. Utiliza Apache Camel para orquestração dos fluxos de integração.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application.java` | Classe principal de inicialização do Spring Boot |
| `ValidacaoPagamentoService` | Serviço de domínio que orquestra o processo de validação de pagamento |
| `ValidacaoPagamentoBoletoSubscriber` | Subscriber que consome mensagens da fila de validação de pagamento |
| `ValidacaoPagamentoRouter` | Roteador Camel principal que coordena o fluxo de validação |
| `IntegrarPagamentoRouter` | Roteador Camel para integração com serviços de pagamento |
| `DiasUteisRouter` | Roteador Camel para validação de dias úteis |
| `RetornoProcessoPagamentoBoletoRouter` | Roteador Camel para publicação de retorno |
| `DiasUteisClientImpl` | Cliente para consulta de dias úteis |
| `IntegrarPagamentoClientImpl` | Cliente para consulta de bancos e contas |
| `ValidacaoPagamentoClientImpl` | Cliente para validação de pagamento |
| `RetornoProcessoPagamentoBoletoPublisherImpl` | Publisher de mensagens de retorno |
| `CamelContextWrapper` | Wrapper do contexto Apache Camel |

## 3. Tecnologias Utilizadas

- **Framework Principal**: Spring Boot 2.x
- **Linguagem**: Java 11
- **Orquestração**: Apache Camel 3.0.1
- **Mensageria**: Google Cloud Pub/Sub (Spring Cloud GCP 2.0.4)
- **Cache**: Spring Cache com Guava
- **Mapeamento de Objetos**: MapStruct 1.3.1
- **Documentação API**: Swagger/OpenAPI 2.9.2
- **Segurança**: OAuth2 JWT
- **Monitoramento**: Spring Actuator, Prometheus, Grafana
- **Logging**: Logback com formato JSON
- **Testes**: JUnit 5, Mockito, Rest Assured, Pact
- **Build**: Maven
- **Containerização**: Docker

## 4. Principais Endpoints REST

Não se aplica. O sistema não expõe endpoints REST próprios, apenas consome e publica mensagens em filas PubSub. Os endpoints expostos são apenas do Spring Actuator para monitoramento (`/actuator/health`, `/actuator/prometheus`).

## 5. Principais Regras de Negócio

1. **Validação de Dia Útil**: Verifica se a data de movimento é dia útil bancário considerando praça específica
2. **Validação de Banco**: Consulta dados cadastrais do banco pelo código COMPE, com tratamento especial para Banco BV (código 413)
3. **Validação de Conta Cliente**: Valida existência e dados da conta do favorecido e remetente
4. **Validação de Grade de Câmara**: Verifica se o pagamento está dentro do horário da grade de câmara de liquidação
5. **Cache de Consultas**: Implementa cache com TTL de 60 minutos para consultas de dias úteis e bancos
6. **Tratamento de Erros**: Diferencia erros de negócio (HTTP 4xx) de erros técnicos (HTTP 5xx e exceções)
7. **Publicação de Resultado**: Publica três tipos de eventos: PAGAMENTO_VALIDADO, PAGAMENTO_REJEITADO ou VALIDACAO_PAGAMENTO_FALHOU

## 6. Relação entre Entidades

**Entidades Principais:**

- **ValidarPagamentoPayload**: Entidade raiz contendo dados do pagamento a validar
  - Contém: codigoLancamento, dataMovimento, CamaraLiquidacao, ContaCliente (favorecido e remetente)
  
- **CamaraLiquidacao**: Dados da câmara de liquidação
  - Atributos: codigoLiquidacao, horaInicioGradeCamara, horaFimGradeCamara

- **ContaCliente**: Dados da conta bancária
  - Atributos: codigoBancoCompe, numeroAgencia, numeroConta

- **RetornoProcessoPagamentoBoletoPayload**: Resultado do processamento
  - Pode conter: SucessoPayload, ErroNegocioPayload ou ErroTecnicoPayload
  - Associado a TipoEventoEnum

**Relacionamentos:**
- ValidarPagamentoPayload (1) -> (1) CamaraLiquidacao
- ValidarPagamentoPayload (1) -> (0..2) ContaCliente (favorecido e remetente)
- RetornoProcessoPagamentoBoletoPayload (1) -> (1) TipoEventoEnum

## 7. Estruturas de Banco de Dados Lidas

Não se aplica. O sistema não acessa diretamente banco de dados, apenas consome APIs REST de outros serviços.

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema não realiza operações de escrita em banco de dados.

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | Spring Boot | Arquivo de configuração da aplicação |
| logback-spring.xml | Leitura | Logback | Configuração de logs em formato JSON |
| integrar-pagamento-contracts.yaml | Leitura | Swagger Codegen | Contrato OpenAPI para geração de client |
| sboot-dcor-base-atom-dias-uteis-v1.2.0.yaml | Leitura | Swagger Codegen | Contrato OpenAPI para geração de client |
| sboot-spag-base-atom-validacao-pagamento.yaml | Leitura | Swagger Codegen | Contrato OpenAPI para geração de client |

## 10. Filas Lidas

| Nome da Fila | Tipo | Descrição |
|--------------|------|-----------|
| business-spag-validacao-pagamento-boleto-sub | Google Cloud Pub/Sub Subscription | Fila de entrada que recebe solicitações de validação de pagamento de boleto |

**Configuração:**
- Ambiente Local/DES: `business-spag-validacao-pagamento-boleto-sub`
- Ambientes QA/UAT/PRD: `projects/${PROJECT_ID}/subscriptions/business-spag-validacao-pagamento-boleto-sub`
- Modo de Acknowledge: MANUAL
- Payload Type: ValidarPagamentoPayload

## 11. Filas Geradas

| Nome da Fila | Tipo | Descrição |
|--------------|------|-----------|
| business-spag-retorno-processo-pagamento-boleto | Google Cloud Pub/Sub Topic | Fila de saída que publica o resultado do processamento de validação |

**Configuração:**
- Ambiente Local/DES: `business-spag-retorno-processo-pagamento-boleto`
- Ambientes QA/UAT/PRD: `projects/${PROJECT_ID}/topics/business-spag-retorno-processo-pagamento-boleto`
- Payload Types: SucessoPayload, ErroNegocioPayload ou ErroTecnicoPayload
- Header: EventoHeader com TipoEventoEnum e dataHoraEvento

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| sboot-dcor-base-atom-dias-uteis | REST API | Serviço de validação de dias úteis bancários |
| sboot-sitp-base-atom-integrar-pagamento | REST API | Serviço de consulta de bancos e contas correntes (endpoints: /cadastro/v1/bancos, /cadastro/v1/conta-cliente) |
| sboot-spag-base-atom-validacao-pagamento | REST API | Serviço atômico de validação de pagamento |
| API Gateway OAuth2 | OAuth2/JWT | Serviço de autenticação para obtenção de tokens de acesso |

**URLs por Ambiente:**
- DES: https://apigatewaydes.bvnet.bv, https://sboot-*.appdes.bvnet.bv
- UAT: https://apigatewayuat.bvnet.bv, https://sboot-*.appuat.bvnet.bv
- PRD: https://api.bancovotorantim.com.br, https://sboot-*.app.bvnet.bv

## 13. Avaliação da Qualidade do Código

**Nota: 8.5/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões hexagonais (ports/adapters)
- Separação clara de responsabilidades em módulos (application, domain, common)
- Uso adequado de Apache Camel para orquestração de fluxos complexos
- Implementação de cache para otimização de consultas
- Tratamento robusto de exceções com diferenciação entre erros de negócio e técnicos
- Boa cobertura de testes unitários
- Uso de MapStruct para mapeamento de objetos
- Configuração adequada de observabilidade (Prometheus, Grafana)
- Documentação via Swagger/OpenAPI
- Uso de Lombok para redução de boilerplate

**Pontos de Melhoria:**
- Alguns processadores Camel poderiam ter lógica mais simplificada
- Falta de documentação inline em algumas classes complexas
- Configurações hardcoded em alguns pontos (ex: codigoPraca=1, codigoTipoRelacionamento=1)
- Poderia ter mais testes de integração
- Algumas classes de teste com setup repetitivo que poderia ser abstraído

## 14. Observações Relevantes

1. **Arquitetura Event-Driven**: Sistema totalmente orientado a eventos, sem exposição de APIs REST próprias
2. **Multi-Ambiente**: Configuração preparada para múltiplos ambientes (local, des, qa, uat, prd)
3. **Resiliência**: Implementa cache e tratamento de erros para aumentar resiliência
4. **Monitoramento**: Infraestrutura completa de observabilidade com Prometheus e Grafana
5. **Cloud Native**: Preparado para execução em Google Cloud Platform com Pub/Sub
6. **Segurança**: Integração com OAuth2/JWT para autenticação em APIs externas
7. **Containerização**: Dockerfile otimizado com OpenJ9 para redução de consumo de memória
8. **CI/CD**: Configuração para Jenkins com propriedades específicas (jenkins.properties)
9. **Versionamento**: Sistema versionado (0.4.0) seguindo padrões do Banco Votorantim
10. **Testes**: Estrutura de testes separada em unit, integration e functional
11. **ArchUnit**: Configuração para validação de regras arquiteturais
12. **Pact**: Suporte a testes de contrato para garantir compatibilidade entre serviços