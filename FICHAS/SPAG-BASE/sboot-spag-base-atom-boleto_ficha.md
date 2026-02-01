# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-spag-base-atom-boleto** é um serviço atômico (microserviço) desenvolvido em Java com Spring Boot, destinado ao cálculo de valores de boletos bancários. O sistema recebe informações de um boleto e realiza cálculos complexos envolvendo multas, juros, descontos, abatimentos e saldos devedores, considerando diferentes modalidades de cálculo, pagamentos parciais, baixas operacionais e efetivas. O serviço expõe uma API REST para processamento de boletos calculados e retorna informações detalhadas sobre valores a pagar, indicadores de parcialidade, divergência e outras características do título.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application.java` | Classe principal de inicialização da aplicação Spring Boot. |
| `BoletoApiDelegateImpl.java` | Implementação do delegate da API REST, recebe requisições de cálculo de boleto e delega ao serviço. |
| `BoletoService.java` | Serviço de domínio responsável por orquestrar os cálculos de boleto (multa, saldo devedor, valores máximo/mínimo, indicadores). |
| `BoletoCalculoUtil.java` | Classe utilitária com métodos estáticos para cálculos gerais de boleto (multa, saldo, valores máximo/mínimo, indicadores). |
| `MultaUtil.java` | Classe utilitária específica para cálculo de multa com base em diferentes modalidades. |
| `SaldoUtil.java` | Classe utilitária para cálculo do saldo devedor do título, considerando baixas e valores adicionais. |
| `ValorUtil.java` | Classe utilitária para tratamento e validação de valores (truncamento, verificação de nulos e negativos). |
| `JsonUtil.java` | Classe utilitária para serialização/deserialização JSON com suporte a LocalDate e LocalDateTime. |
| `BoletoCalculado.java` | Entidade de domínio representando um boleto com todos os dados e resultados de cálculo. |
| `BoletoRequest.java` | Objeto de requisição contendo dados de entrada para consulta de boleto. |
| `BaixaEfetiva.java`, `BaixaTitulo.java` | Entidades representando baixas (pagamentos parciais) de títulos. |
| `CalculoTitulo.java` | Entidade representando cálculos pré-definidos de título (desconto, juros, multa, total). |
| `Titulo.java` | Entidade genérica representando informações de título (código, data, percentual, valor). |
| `PessoaBeneficiarioOriginal.java`, `PessoaBeneficiarioFinal.java`, `PessoaPagador.java`, `SacadorAvalista.java` | Entidades representando pessoas envolvidas no boleto. |
| `BoletoException.java`, `BusinessException.java` | Classes de exceção customizadas para tratamento de erros de negócio. |
| `ModelMapperConfiguration.java` | Configuração do bean ModelMapper para mapeamento de objetos. |
| `BoletoMapper.java` | Interface Mapper (MapStruct) para conversão entre objetos de domínio e representação. |
| `BoletoRepository.java` | Interface de repositório (vazia no código fornecido, possivelmente para futuras implementações). |

---

## 3. Tecnologias Utilizadas

- **Java 11+**
- **Spring Boot** (framework principal)
- **Spring Security OAuth2 Resource Server** (autenticação JWT)
- **Spring Web** (REST API)
- **Spring Actuator** (monitoramento e health checks)
- **Maven** (gerenciamento de dependências)
- **Lombok** (redução de boilerplate)
- **MapStruct** (mapeamento de objetos)
- **ModelMapper** (mapeamento de objetos)
- **Gson** (serialização/deserialização JSON)
- **OpenAPI 3.0 / Swagger** (documentação de API)
- **Atlante** (framework interno do Banco Votorantim para telemetria e segurança)
- **Tomcat Embed** (servidor de aplicação embutido)
- **SLF4J / Logback** (logging)
- **JUnit / Spring Boot Test** (testes unitários - arquivos não enviados)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/boleto/v1/calculo` | `BoletoApiDelegateImpl` | Recebe um objeto `BoletoCalculadoRepresentation` com dados do boleto e retorna o mesmo objeto com cálculos realizados (multa, juros, saldo devedor, indicadores, valores máximo/mínimo). |

---

## 5. Principais Regras de Negócio

1. **Cálculo de Multa**: A multa é calculada com base no tipo de modelo de cálculo (01, 02, 03, 04) e na situação de vencimento do boleto. Pode ser valor fixo, percentual ou pré-calculado.

2. **Cálculo de Saldo Devedor**: O saldo devedor considera o valor do título, juros, multa, descontos, abatimentos e baixas (operacionais e efetivas).

3. **Valores Máximo e Mínimo de Pagamento**: Calculados com base em percentuais ou valores fixos configurados, considerando descontos, juros e multa.

4. **Indicadores de Boleto**:
   - **Boleto Parcial**: Indica se o boleto permite pagamento parcial.
   - **Boleto Divergente**: Indica se há autorização para recebimento de valor divergente.
   - **Última Parcela**: Verifica se é a última parcela permitida de pagamento parcial.
   - **Valor Residual**: Verifica se o saldo devedor é menor que o valor mínimo permitido.

5. **Modalidades de Cálculo**: O sistema suporta diferentes modalidades (01 a 04), onde a recebedora calcula (01, 04) ou o destinatário fornece valores pré-calculados (02, 03).

6. **Tratamento de Baixas**: Considera baixas operacionais e efetivas para cálculo do saldo devedor.

7. **Data de Referência**: Todos os cálculos consideram uma data de referência (padrão: data atual).

---

## 6. Relação entre Entidades

- **BoletoCalculado** é a entidade central, contendo:
  - Listas de **Titulo** (descontos, juros, multas)
  - Listas de **CalculoTitulo** (cálculos pré-definidos)
  - Listas de **BaixaTitulo** e **BaixaEfetiva** (pagamentos parciais)
  - **PessoaBeneficiarioOriginal**, **PessoaBeneficiarioFinal**, **PessoaPagador**, **SacadorAvalista** (pessoas envolvidas)

- **BaixaEfetiva** contém um **BaixaTitulo** e informações de canal/meio de pagamento.

- **Titulo** é uma entidade genérica usada para representar descontos, juros e multas.

- **CalculoTitulo** representa cálculos pré-definidos com data de validade.

---

## 7. Estruturas de Banco de Dados Lidas

Não se aplica. O código fornecido não demonstra acesso direto a banco de dados. A interface `BoletoRepository` está vazia, sugerindo que a implementação de persistência pode estar em outro módulo ou não foi incluída no escopo analisado.

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O código fornecido não demonstra operações de escrita em banco de dados.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Descrição |
|-----------------|----------|-------------------------|-----------|
| `application.yml` | Leitura | Spring Boot | Arquivo de configuração principal da aplicação. |
| `application-local.yml` | Leitura | Spring Boot | Arquivo de configuração para perfil local. |
| `logback-spring.xml` | Leitura | Logback | Configuração de logs (não enviado, mas referenciado). |
| `sboot-spag-base-atom-boleto.yaml` | Leitura | OpenAPI Generator | Contrato OpenAPI para geração de código da API. |

---

## 10. Filas Lidas

Não se aplica. O código fornecido não demonstra consumo de filas (JMS, Kafka, RabbitMQ, etc.).

---

## 11. Filas Geradas

Não se aplica. O código fornecido não demonstra publicação em filas.

---

## 12. Integrações Externas

- **OAuth2 Resource Server**: Integração com servidor de autenticação JWT (issuer-uri e jwk-set-uri configurados em `application.yml`).
- **Atlante Telemetry**: Integração com sistema de telemetria interno do Banco Votorantim (endpoint collector configurado para ambiente local).

Não há evidências de integrações com APIs externas, bancos de dados externos ou outros sistemas no código fornecido.

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Código bem organizado em camadas (domain, service, rest, util, config).
- Uso adequado de Lombok para redução de boilerplate.
- Separação clara de responsabilidades (service, utils).
- Documentação OpenAPI bem estruturada.
- Uso de classes utilitárias para cálculos específicos (MultaUtil, SaldoUtil, ValorUtil).
- Tratamento de exceções customizadas.
- Configuração adequada de segurança OAuth2.

**Pontos de Melhoria:**
- **Falta de documentação JavaDoc**: Métodos complexos de cálculo não possuem documentação detalhada.
- **Classes utilitárias com métodos estáticos**: Dificulta testes unitários e injeção de dependências.
- **Lógica de negócio complexa em utils**: Parte da lógica deveria estar em serviços de domínio.
- **Uso de `JsonUtil` com Gson**: Mistura de bibliotecas (ModelMapper, MapStruct, Gson) para serialização/mapeamento.
- **Falta de validações de entrada**: Não há validações explícitas (Bean Validation) nos objetos de domínio.
- **Código com "code smells"**: Métodos longos, múltiplos níveis de aninhamento, uso excessivo de `if/else`.
- **Falta de testes**: Arquivos de teste não foram enviados, impossibilitando avaliação de cobertura.
- **Constantes mágicas**: Strings e números hardcoded ("03", "02", "S", "V", etc.) deveriam ser constantes nomeadas.

---

## 14. Observações Relevantes

1. **Arquitetura Atômica**: O sistema segue o padrão de microserviços atômicos do Banco Votorantim, com estrutura padronizada e uso do framework Atlante.

2. **Contract-First**: A API é definida primeiro via OpenAPI (YAML), com geração automática de código.

3. **Perfis de Ambiente**: Suporte a múltiplos perfis (local, des, uat, prd) com configurações específicas.

4. **Segurança**: Autenticação via JWT com Bearer Token, endpoints públicos configuráveis.

5. **Monitoramento**: Actuator exposto na porta 9090 com métricas e health checks.

6. **Cálculos Complexos**: O sistema implementa lógica sofisticada de cálculo de boletos, considerando múltiplas variáveis e modalidades.

7. **Data de Referência**: Todos os cálculos são baseados em uma data de referência, permitindo simulações e cálculos retroativos.

8. **Repositório Vazio**: A interface `BoletoRepository` está vazia, sugerindo que a persistência pode ser implementada futuramente ou está em outro módulo.

9. **Dependência de Parent POM**: O projeto herda de `pom-atle-base-sboot-atom-parent`, centralizando configurações e dependências comuns.

10. **Versionamento**: Projeto na versão 0.2.0, indicando fase inicial de desenvolvimento.