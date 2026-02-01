# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema orquestrador responsável por verificar se um cliente está pré-aprovado para produtos de crédito (Crédito Pessoal, Crédito com Veículo em Garantia e Crédito Mar Aberto). O serviço expõe uma API REST que consulta informações de pré-aprovação através de integração com outro microserviço e retorna URLs para contratação dos produtos disponíveis. Trata-se de uma aplicação Spring Boot stateless que utiliza Apache Camel para orquestração de fluxos.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot que inicializa a aplicação |
| `PreaprovadoController` | Controller REST que expõe o endpoint de verificação de pré-aprovado |
| `PreaprovadoService` | Serviço de domínio que orquestra o fluxo via Apache Camel |
| `PreaprovadoRepositoryImpl` | Implementação do repositório que integra com serviço externo via RestTemplate |
| `PreaprovadoRouter` | Roteador Apache Camel que define o fluxo de orquestração |
| `PreaprovadoMapper` | Mapper responsável por converter dados de domínio para representação REST |
| `ObterCpf` | Utilitário para extrair CPF/CNPJ do contexto de segurança (token JWT) |
| `ErrorFormat` | Utilitário para formatação de erros e conversão para ResponseEntity |
| `PreaprovadoConfiguration` | Configuração Spring que define beans do Apache Camel e serviços |
| `AppProperties` | Classe de propriedades de configuração da aplicação |

---

## 3. Tecnologias Utilizadas

- **Java 11** - Linguagem de programação
- **Spring Boot 2.x** - Framework principal
- **Spring Security OAuth2** - Autenticação e autorização via JWT
- **Apache Camel 3.0.1** - Orquestração de fluxos
- **Swagger/OpenAPI 2.9.2** - Documentação de API
- **Lombok** - Redução de boilerplate
- **RestTemplate** - Cliente HTTP para integrações
- **Micrometer/Prometheus** - Métricas e monitoramento
- **Spring Actuator** - Endpoints de health check e métricas
- **Logback** - Framework de logging
- **Maven** - Gerenciamento de dependências
- **Docker** - Containerização
- **Grafana** - Visualização de métricas
- **JUnit 5** - Testes unitários
- **Pact** - Testes de contrato

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/banco-digital/ccbd/preaprovado` | `PreaprovadoController` | Verifica se o cliente autenticado está pré-aprovado para produtos de crédito e retorna URLs de contratação |

---

## 5. Principais Regras de Negócio

1. **Autenticação obrigatória**: O endpoint requer autenticação OAuth2 via JWT, extraindo o CPF/CNPJ do token
2. **Validação de CPF/CNPJ**: Verifica se o CPF/CNPJ está presente no contexto de segurança, lançando exceção caso não esteja
3. **Retorno padronizado**: Sempre retorna estrutura com três produtos (Crédito Pessoal, Crédito com Veículo em Garantia e Crédito Mar Aberto)
4. **Crédito Mar Aberto sempre disponível**: O produto "Crédito Mar Aberto" sempre retorna flag "S" (pré-aprovado), enquanto os demais retornam "N"
5. **Valor disponível zerado**: Todos os produtos retornam valor disponível como zero (BigDecimal.ZERO)
6. **URLs configuráveis**: As URLs de contratação são configuradas por ambiente via properties
7. **Tratamento de erros**: Erros de integração são capturados e convertidos em erro interno genérico

---

## 6. Relação entre Entidades

**Entidades de Domínio:**

- **Preaprovado**: Entidade principal que contém informações de pré-aprovação
  - Possui relacionamento com `Produto` (creditoPessoal, creditoVeiculoGarantia)
  
- **Produto**: Representa um produto de crédito
  - Atributos: url (String), flPreAprovado (String), vlDisponivel (BigDecimal)

**Representações REST:**

- **PreAprovadoResponseRepresentation**: DTO de resposta da API
  - Contém: creditoPessoal, creditoVeiculoGarantia, creditoMarAberto (todos do tipo ProdutoRepresentation)
  
- **ProdutoRepresentation**: DTO que representa um produto na resposta
  - Mesma estrutura da entidade Produto

- **ErroNegocioRepresentation**: DTO para erros de negócio
  - Atributos: codigo, descricaoCodigo

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
| `application.yml` | leitura | Spring Boot / AppProperties | Arquivo de configuração da aplicação com URLs de serviços e configurações por ambiente |
| `logback-spring.xml` | leitura | Logback Framework | Configuração de logging da aplicação |
| `sboot-ccbd-base-orch-preaprovado.yaml` | leitura | Swagger Codegen | Especificação OpenAPI para geração de interfaces REST |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| `sboot-prea-base-atom-preaprovado` | API REST | Microserviço consultado para obter informações de pré-aprovação do cliente. Endpoint: `/v1/interface-preaprovado`. Integração via RestTemplate com autenticação. |
| OAuth2 JWT Provider | Autenticação | Serviço de autenticação OAuth2 para validação de tokens JWT. URL configurável por ambiente (api-digitaldes/api-digital.bancovotorantim.com.br). |

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com módulos domain, application e common
- Uso adequado de padrões como Repository, Service e Controller
- Configuração adequada de segurança OAuth2
- Documentação OpenAPI presente
- Testes estruturados (unit, integration, functional)
- Uso de Lombok para redução de boilerplate
- Configuração de métricas e observabilidade (Prometheus/Grafana)

**Pontos Negativos:**
- **Lógica de negócio questionável**: O mapper sempre retorna valores fixos (flag "N" para CP e CVG, "S" para Mar Aberto, valores zerados), ignorando completamente a resposta do serviço consultado
- **Integração não utilizada**: O `PreaprovadoRepositoryImpl` faz chamada ao serviço externo mas o resultado nunca é usado no controller
- **Tratamento de erro genérico**: Todos os erros HTTP são convertidos em erro interno genérico, perdendo informações importantes
- **Código morto**: A classe `PreaprovadoService` e o fluxo Camel não são utilizados no controller
- **Falta de validações**: Não há validação de dados de entrada além da presença do CPF
- **Configuração de segurança incompleta**: RestTemplate de segurança configurado mas não há evidência de propagação de contexto
- **Documentação técnica insuficiente**: README genérico sem informações específicas do projeto

---

## 14. Observações Relevantes

1. **Inconsistência arquitetural**: O projeto foi estruturado para usar Apache Camel como orquestrador, mas o controller não utiliza o `PreaprovadoService` que encapsula o Camel, chamando diretamente o mapper com valores fixos

2. **Funcionalidade limitada**: A aplicação atual não consulta efetivamente o serviço de pré-aprovação, apenas retorna URLs configuradas com flags fixas

3. **Ambiente multi-cloud**: Configurado para deploy em Google Cloud Platform (GKE) conforme jenkins.properties

4. **Segurança**: Utiliza autenticação OAuth2 com JWT, extraindo CPF/CNPJ do token para identificação do usuário

5. **Observabilidade**: Bem configurada com Actuator, Prometheus e Grafana, incluindo dashboards prontos

6. **Containerização**: Dockerfile otimizado usando OpenJ9 JVM com configurações de memória ajustáveis

7. **CI/CD**: Integrado com Jenkins conforme propriedades definidas

8. **Versionamento**: Projeto na versão 0.2.0, indicando fase inicial de desenvolvimento

9. **Padrão BV**: Segue padrões arquiteturais do Banco Votorantim com parent POM `arqt-base-master-springboot`

10. **Possível refatoração necessária**: O código sugere que houve mudança de requisitos ou implementação incompleta, pois a infraestrutura de integração existe mas não é utilizada