# Ficha Técnica do Sistema

## 1. Descrição Geral
O sistema **springboot-spag-base-boleto-calculado** é um serviço REST (BFF - Backend For Frontend) desenvolvido em Spring Boot que realiza cálculos de valores de boletos bancários. Ele consulta informações de boletos na CIP (Câmara Interbancária de Pagamentos), calcula juros, multas e descontos aplicáveis conforme regras de negócio específicas, e retorna os valores calculados para o pagamento. O sistema também considera dias úteis e feriados para os cálculos, integrando-se com serviços externos de calendário bancário.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `BoletoCalculadoApi` | Controller REST que expõe o endpoint de consulta e cálculo de boleto |
| `BoletoCalculadoFacade` | Orquestra o fluxo de consulta na CIP e execução dos cálculos |
| `CalculaBoletoCipService` | Serviço principal que coordena os cálculos de juros, multa e desconto |
| `CalculoJurosHelper` | Realiza cálculos de juros com base em diferentes estratégias |
| `CalculoMultaHelper` | Realiza cálculos de multa sobre boletos vencidos |
| `CalculoDescontoHelper` | Realiza cálculos de descontos aplicáveis ao boleto |
| `BoletoPagamentoHelper` | Fornece métodos auxiliares para manipulação de dados de boleto |
| `CalendarioBancoService` | Gerencia cálculos de dias úteis e corridos |
| `ConsultaCipRepository` | Integra com a API da CIP para consultar dados de boletos |
| `FeriadoRepository` | Integra com serviço de calendário para obter feriados e dias úteis |
| `CalculoND2Service` | Implementa padrão Strategy para diferentes tipos de cálculo de juros |
| `BoletoCalculado` | Entidade de domínio que representa um boleto com seus cálculos |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.x** (framework principal)
- **Spring Web** (REST APIs)
- **Spring Security** (autenticação e autorização)
- **Spring Cloud Sleuth** (rastreamento distribuído)
- **OpenTelemetry** (observabilidade)
- **Swagger/OpenAPI 3** (documentação de API)
- **Jackson** (serialização JSON)
- **Lombok** (redução de boilerplate)
- **Logback** (logging)
- **RestTemplate** (cliente HTTP)
- **JUnit** (testes unitários)
- **Docker** (containerização)
- **Kubernetes/OpenShift** (orquestração)
- **Maven** (gerenciamento de dependências)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/atacado/pagamentos/consultaBoletoCalculado` | `BoletoCalculadoApi` | Consulta boleto na CIP e retorna valores calculados (juros, multa, desconto) |

---

## 5. Principais Regras de Negócio

1. **Cálculo de Juros**: Aplicado sobre boletos vencidos, com 10 estratégias diferentes (valor fixo, percentual, dias corridos, dias úteis, etc.)
2. **Cálculo de Multa**: Aplicado sobre boletos vencidos, podendo ser valor fixo ou percentual
3. **Cálculo de Desconto**: Aplicado sobre boletos não vencidos, considerando data de validade e tipo de desconto
4. **Verificação de Vencimento**: Considera dias úteis para determinar se o boleto está vencido
5. **Pagamento Parcial**: Identifica se o boleto permite pagamento parcial e se está na última parcela
6. **Valor Residual**: Determina se o valor a pagar é residual (menor que o mínimo permitido)
7. **Boleto Divergente**: Identifica boletos com autorização para recebimento de valor divergente
8. **Abatimentos**: Considera abatimentos no cálculo do valor total
9. **Baixas**: Considera baixas operacionais e efetivas no saldo devedor
10. **Modalidades de Cálculo**: Suporta 4 tipos de modelo de cálculo (recebedora a calcular, destinatário calculado, etc.)

---

## 6. Relação entre Entidades

- **BoletoCalculado**: Entidade principal que agrega todas as informações do boleto
  - Contém `PessoaBeneficiarioOriginal` (1:1)
  - Contém `PessoaPagador` (1:1)
  - Contém `PessoaBeneficiarioFinal` (0:1)
  - Contém `SacadorAvalista` (0:1)
  - Contém lista de `Titulo` para descontos (1:N)
  - Contém lista de `Titulo` para juros (1:N)
  - Contém lista de `Titulo` para multas (1:N)
  - Contém lista de `CalculoTitulo` (1:N)
  - Contém lista de `BaixaTitulo` operacional (1:N)
  - Contém lista de `BaixaEfetiva` (1:N)

- **BaixaEfetiva**: Contém `BaixaTitulo` (1:1) e informações de canal/meio de pagamento

- **Titulo**: Representa informações de desconto, juros ou multa com código, data, valor e percentual

- **CalculoTitulo**: Representa cálculo pré-processado com valores de desconto, juros, multa e total

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `logback-spring.xml` | leitura | Configuração de logging | Arquivo de configuração do Logback para logs em JSON |
| `application.yml` | leitura | Spring Boot | Arquivo de configuração principal da aplicação |
| `application-local.yml` | leitura | Spring Boot | Configurações específicas do ambiente local |
| `openapi.yaml` | leitura | Swagger/OpenAPI | Especificação da API REST |
| `roles/*.yml` | leitura | Spring Security | Configuração de roles por ambiente |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| **CIP (Câmara Interbancária de Pagamentos)** | REST API | Consulta informações completas de boletos de pagamento via código de barras |
| **Serviço de Dias Úteis (DCOR)** | REST API | Consulta próximo dia útil e lista de dias não úteis (feriados) para cálculos de calendário bancário |

**Detalhes das Integrações:**

1. **CIP**: 
   - URL configurável por ambiente
   - Autenticação Basic Auth
   - Timeout de 30 segundos
   - Retorna dados completos do boleto incluindo baixas, descontos, juros e multas

2. **Serviço de Dias Úteis**:
   - Dois endpoints: próximo dia útil e lista de dias não úteis
   - Autenticação Basic Auth
   - Utilizado para cálculos de NDC (número de dias corridos) e NDU (número de dias úteis)

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com uso de Helpers, Services e Facades
- Implementação do padrão Strategy para cálculo de juros (StrategyND2)
- Uso adequado de DTOs/Representations para separar camadas
- Configurações externalizadas e organizadas por ambiente
- Uso de Lombok para reduzir boilerplate
- Tratamento de exceções customizado
- Logs estruturados em JSON

**Pontos de Melhoria:**
- Presença de código comentado e datas fixas hardcoded no `FeriadoRepository` (feriados extras)
- Alguns métodos muito extensos (ex: `convertRetornoCip` com mais de 100 linhas)
- Uso de `@SneakyThrows` que mascara exceções checked
- Falta de documentação JavaDoc em algumas classes importantes
- Alguns métodos com muitos parâmetros (ex: `calcularDescontoListaTitulo`)
- Lógica de negócio complexa poderia ter mais testes unitários evidentes
- Algumas validações poderiam ser mais explícitas
- Uso de `BigDecimal` sem escala definida em alguns pontos pode gerar inconsistências

---

## 14. Observações Relevantes

1. **Estratégias de Cálculo de Juros**: O sistema implementa 10 estratégias diferentes de cálculo de juros (códigos 0 a 9), incluindo isento, valor fixo, percentuais diversos, dias corridos e dias úteis.

2. **Modalidades de Cálculo**: Suporta 4 tipos de modelo de cálculo (tipoModeloCalculo: 1, 2, 3, 4) que determinam se os valores são calculados pela recebedora ou já vêm calculados pelo destinatário.

3. **Feriados Hardcoded**: Existe uma lista de feriados extras hardcoded no `FeriadoRepository` que deveria ser removida ou externalizada.

4. **Segurança**: Implementa autenticação via JWT e Basic Auth, com suporte a LDAP e usuários in-memory para testes.

5. **Observabilidade**: Integrado com OpenTelemetry e Spring Cloud Sleuth para rastreamento distribuído.

6. **Multi-ambiente**: Configurações específicas para ambientes local, des, uat e prd.

7. **Containerização**: Dockerfile otimizado com multi-layer para melhor cache de dependências.

8. **Dependências Votorantim**: Utiliza bibliotecas internas do Banco Votorantim (atle, arqt) para funcionalidades comuns.

9. **Swagger**: API documentada com Swagger/OpenAPI 3, com interface habilitada apenas em ambientes não produtivos.

10. **Tratamento de Valores**: Utiliza truncamento de valores em 2 casas decimais e percentuais em 6 casas para garantir precisão nos cálculos financeiros.