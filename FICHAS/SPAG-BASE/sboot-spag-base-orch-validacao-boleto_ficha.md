# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-spag-base-orch-validacao-boleto** é um serviço stateless desenvolvido em Spring Boot que atua como orquestrador para validação de boletos de pagamento. O sistema recebe solicitações de validação de boletos através de filas do Google Cloud Pub/Sub, realiza a validação consultando serviços externos (CIP - Câmara Interbancária de Pagamentos), e retorna o resultado do processamento através de outra fila.

O componente implementa um fluxo de orquestração utilizando Apache Camel para coordenar as chamadas aos serviços de validação e integração com a base de pagamentos, tratando tanto cenários de sucesso quanto de erro (técnico e de negócio).

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal que inicializa a aplicação Spring Boot |
| **ValidacaoBoletoService** | Serviço de domínio que orquestra o processo de validação de boleto |
| **ValidacaoBoletoSubscriber** | Subscriber que consome mensagens da fila de entrada para validação de boletos |
| **ValidacaoBoletoRouter** | Roteador Apache Camel que define o fluxo de validação de boleto |
| **IntegrarPagamentoRouter** | Roteador Apache Camel para integração com serviço de parametrização |
| **RetornoProcessoPagamentoBoletoRouter** | Roteador Apache Camel para publicação de retorno do processamento |
| **ValidacaoBoletoClientImpl** | Implementação do cliente para chamada ao serviço de validação CIP |
| **IntegrarPagamentoClientImpl** | Implementação do cliente para consulta de configurações CIP |
| **RetornoProcessoPagamentoBoletoPublisherImpl** | Implementação do publisher para envio de retorno à fila |
| **ValidarBoletoCallbackProcessor** | Processador Camel que prepara a requisição de validação |
| **RetornoProcessoPagamentoBoletoCallbackProcessor** | Processador Camel que trata a resposta da validação |
| **ExceptionCallbackProcessor** | Processador Camel para tratamento de exceções |
| **CamelContextWrapper** | Wrapper do contexto Apache Camel |

---

## 3. Tecnologias Utilizadas

- **Java 11** (OpenJDK)
- **Spring Boot 2.x** (framework base)
- **Spring Cloud GCP 2.0.4** (integração com Google Cloud Platform)
- **Google Cloud Pub/Sub** (mensageria)
- **Apache Camel 3.0.1** (orquestração e integração)
- **Swagger/OpenAPI 2.9.2** (documentação de APIs)
- **MapStruct 1.3.1** (mapeamento de objetos)
- **Lombok** (redução de boilerplate)
- **Micrometer/Prometheus** (métricas e monitoramento)
- **Logback** (logging)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Kubernetes/OpenShift** (orquestração de containers)
- **Grafana** (visualização de métricas)
- **JUnit 5** (testes unitários)
- **Mockito** (mocks para testes)
- **RestAssured** (testes funcionais)
- **Pact** (testes de contrato)

---

## 4. Principais Endpoints REST

**não se aplica** - O sistema não expõe endpoints REST públicos. A comunicação é realizada exclusivamente através de filas Google Cloud Pub/Sub (arquitetura orientada a eventos).

---

## 5. Principais Regras de Negócio

1. **Validação de Boleto via CIP**: O sistema valida boletos consultando a Câmara Interbancária de Pagamentos (CIP) para verificar a autenticidade e dados do título.

2. **Validação por Valor Mínimo**: Existe um valor mínimo configurável para que a validação CIP seja realizada. Valores abaixo deste limite podem seguir fluxo de contingência.

3. **Tipos de Liquidação**: O sistema suporta diferentes tipos de liquidação (NORMAL e STR_26), que influenciam o processo de validação.

4. **Tratamento de Boletos Divergentes**: O sistema identifica e trata boletos com divergências, verificando se a divergência é permitida.

5. **Boletos Parciais**: Suporta validação de boletos que permitem pagamento parcial, controlando quantidade de parcelas.

6. **Boletos Vencidos**: Identifica e trata boletos vencidos de acordo com as regras de negócio.

7. **Baixa Operacional**: Processa informações de baixa operacional de títulos já pagos.

8. **Contingência**: Implementa fluxo de contingência quando a validação CIP não está disponível ou falha.

9. **Validação de Favorecido**: Valida dados do favorecido (CPF/CNPJ e tipo de pessoa) contra os dados retornados pela CIP.

10. **Configurações Dinâmicas**: Consulta configurações CIP dinamicamente (valores mínimos/máximos, indicadores de validação e contingência).

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **ValidarBoletoPayload**: Entidade de entrada contendo dados da solicitação de validação
  - Contém: codigoLancamento, valorPagamento, boleto, favorecido, tipoLiquidacao

- **Boleto**: Representa os dados do boleto a ser validado
  - Contém: codigoDeBarras, valor, dataVencimento

- **Pessoa**: Representa dados do favorecido ou remetente
  - Contém: tipoPessoa, numeroCpfCnpj

- **BoletoValidadoPayload**: Entidade de retorno com resultado da validação
  - Contém: codigoLancamento, tipoValidacaoBoleto, boletoCalculado

- **BoletoCalculado**: Dados detalhados do boleto validado
  - Contém: numeroIdentificacaoTitulo, codigoEspecieTitulo, dataVencimentoTitulo, indicadorBoletoParcial, listaBaixaOperacional

- **RetornoProcessoPagamentoBoletoPayload**: Envelope de resposta
  - Contém: payload (pode ser BoletoValidadoPayload, ErroNegocioPayload ou ErroTecnicoPayload), tipoEvento

- **ConfigCipResponse**: Configurações da integração CIP
  - Contém: indicadores de validação/contingência, valores mínimos/máximos

**Relacionamentos:**
- ValidarBoletoPayload **contém** Boleto (1:1)
- ValidarBoletoPayload **contém** Pessoa (favorecido) (1:1)
- BoletoValidadoPayload **contém** BoletoCalculado (1:1)
- BoletoCalculado **contém** lista de BaixaTitulo (1:N)
- RetornoProcessoPagamentoBoletoPayload **contém** payload polimórfico (1:1)

---

## 7. Estruturas de Banco de Dados Lidas

**não se aplica** - O sistema não acessa diretamente estruturas de banco de dados. Toda a persistência e consulta de dados é realizada através de chamadas a serviços externos (APIs REST).

---

## 8. Estruturas de Banco de Dados Atualizadas

**não se aplica** - O sistema não realiza operações de escrita em banco de dados. É um componente stateless que apenas orquestra chamadas a serviços externos.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot (startup) | Arquivo de configuração da aplicação com profiles (local, des, qa, uat, prd) |
| logback-spring.xml | leitura | Logback (startup) | Configuração de logs da aplicação |
| integrar-pagamento-contracts.yaml | leitura | Swagger Codegen (build time) | Contrato OpenAPI para geração de client do serviço de integração de pagamento |
| springboot-spag-base-valida-retorno-cip.yaml | leitura | Swagger Codegen (build time) | Contrato OpenAPI para geração de client do serviço de validação CIP |

---

## 10. Filas Lidas

**Fila de Entrada:**
- **Nome**: `business-spag-validacao-boleto-sub` (subscription)
- **Tópico**: `business-spag-validacao-boleto`
- **Tecnologia**: Google Cloud Pub/Sub
- **Payload**: ValidarBoletoPayload (JSON)
- **Classe Responsável**: ValidacaoBoletoSubscriber
- **Descrição**: Recebe solicitações de validação de boletos para processamento

---

## 11. Filas Geradas

**Fila de Saída:**
- **Nome**: `business-spag-retorno-processo-pagamento-boleto` (topic)
- **Tecnologia**: Google Cloud Pub/Sub
- **Payload**: RetornoProcessoPagamentoBoletoPayload (JSON)
- **Classe Responsável**: RetornoProcessoPagamentoBoletoPublisherImpl
- **Descrição**: Publica o resultado do processamento de validação de boleto (sucesso, erro de negócio ou erro técnico)
- **Tipos de Evento**: 
  - BOLETO_VALIDADO (sucesso)
  - BOLETO_REJEITADO (erro de negócio)
  - VALIDACAO_BOLETO_FALHOU (erro técnico)

---

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| **springboot-spag-base-valida-retorno-cip** | API REST | Serviço de validação de boletos via CIP. Realiza a consulta efetiva dos dados do boleto na Câmara Interbancária de Pagamentos. Autenticação via Basic Auth. |
| **sboot-sitp-base-atom-integrar-pagamento** | API REST | Serviço de integração com base de pagamentos ITP. Consulta configurações CIP (valores mínimos/máximos, indicadores). Autenticação via OAuth2 (API Gateway). |
| **API Gateway BV** | OAuth2 | Gateway de autenticação para obtenção de tokens de acesso aos serviços internos. |
| **Google Cloud Pub/Sub** | Mensageria | Plataforma de mensageria para comunicação assíncrona (entrada e saída de mensagens). |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo princípios de Clean Architecture (separação em módulos: domain, application, common)
- Uso adequado de padrões de projeto (Strategy, Template Method via Camel, Dependency Injection)
- Boa separação de responsabilidades com uso de interfaces (ports) e implementações
- Código bem organizado com uso de Lombok para redução de boilerplate
- Implementação de testes unitários, funcionais e de integração
- Uso de MapStruct para mapeamento de objetos de forma eficiente
- Configuração adequada de profiles para diferentes ambientes
- Boa cobertura de logs e tratamento de exceções
- Uso de Apache Camel para orquestração, facilitando manutenção do fluxo
- Documentação via Swagger/OpenAPI
- Configuração de métricas e monitoramento (Prometheus/Grafana)

**Pontos de Melhoria:**
- Alguns processadores Camel poderiam ter lógica mais simples e delegada para services
- Falta de validações mais robustas em alguns pontos (ex: validação de CPF/CNPJ)
- Ausência de circuit breaker para chamadas externas (resiliência)
- Alguns testes unitários com baixa cobertura de cenários alternativos
- Configurações sensíveis (senhas) ainda presentes em alguns arquivos (deveria usar apenas secrets)
- Falta de documentação inline (JavaDoc) em algumas classes importantes
- Alguns métodos poderiam ser quebrados em métodos menores para melhor legibilidade

---

## 14. Observações Relevantes

1. **Arquitetura Event-Driven**: O sistema é totalmente orientado a eventos, não expondo APIs REST síncronas, o que garante desacoplamento e escalabilidade.

2. **Multi-Ambiente**: Configuração bem estruturada para múltiplos ambientes (local, des, qa, uat, prd) com uso de profiles Spring e variáveis de ambiente.

3. **Resiliência**: O sistema implementa tratamento de exceções em múltiplas camadas (Camel, Spring) e retorna erros estruturados para a fila de saída.

4. **Observabilidade**: Boa instrumentação com métricas Prometheus, logs estruturados JSON e dashboards Grafana pré-configurados.

5. **Containerização**: Dockerfile otimizado usando OpenJ9 JVM para melhor performance e menor consumo de memória.

6. **CI/CD**: Configuração para Jenkins com propriedades específicas e suporte a múltiplas plataformas (OpenShift, Google Cloud).

7. **Testes**: Estrutura de testes bem organizada (unit, integration, functional) com uso de Pact para testes de contrato.

8. **Segurança**: Uso de autenticação OAuth2 para serviços internos e Basic Auth para serviço CIP. Secrets gerenciados via Kubernetes.

9. **Geração de Código**: Uso de Swagger Codegen para geração automática de clients a partir de contratos OpenAPI, garantindo consistência.

10. **Arquitetura Hexagonal**: Uso de ports (interfaces) e adapters (implementações) facilita testes e manutenção.

11. **Versionamento de API**: Contratos OpenAPI versionados garantem compatibilidade e evolução controlada.

12. **Monitoramento de Saúde**: Endpoints Actuator configurados para health checks e métricas detalhadas da aplicação.