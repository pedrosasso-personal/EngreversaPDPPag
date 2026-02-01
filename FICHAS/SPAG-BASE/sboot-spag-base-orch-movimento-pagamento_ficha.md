# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-spag-base-orch-movimento-pagamento** é um serviço orquestrador desenvolvido em Spring Boot que consolida dados de movimentação de pagamentos do sistema PGFT para o sistema SPAG. O componente atua como intermediário, consultando pagamentos no PGFT por data e inserindo essas informações no SPAG, realizando a consolidação diária de movimentos de pagamento entre os dois sistemas.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal que inicializa a aplicação Spring Boot |
| **MovimentoPagamentoController** | Controller REST que expõe o endpoint de processamento de movimentos |
| **MovimentoPagamentoService** | Serviço de domínio que orquestra o fluxo de consolidação usando Apache Camel |
| **MovimentoPagamentoRouter** | Define as rotas Apache Camel para processamento dos pagamentos |
| **MovimentoPagamentoPgftProcessor** | Processor Camel que processa os dados retornados do PGFT |
| **PgftMovimentoPagamentoRepositoryImpl** | Implementação do repositório para consulta de pagamentos no PGFT |
| **SpagMovimentoPagamentoRepositoryImpl** | Implementação do repositório para inserção de pagamentos no SPAG |
| **MovimentoPagamento** | Entidade de domínio representando um movimento de pagamento |
| **MovimentoPagamentoConfiguration** | Configuração dos beans Spring e Apache Camel |
| **OpenApiConfiguration** | Configuração do Swagger/OpenAPI para documentação |
| **ExceptionHandler** | Tratamento centralizado de exceções |

---

## 3. Tecnologias Utilizadas

- **Java 11** (OpenJDK)
- **Spring Boot** (framework principal)
- **Apache Camel 3.0.1** (orquestração e roteamento de mensagens)
- **Spring Web** (REST APIs)
- **RestTemplate** (cliente HTTP para integrações)
- **Swagger/Springfox 2.9.2** (documentação de APIs)
- **Lombok** (redução de boilerplate)
- **Spring Actuator** (monitoramento e health checks)
- **Micrometer/Prometheus** (métricas)
- **Logback** (logging)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Kubernetes/OpenShift** (orquestração de containers)
- **BV Security JWT** (segurança e autenticação)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/processar-registros?dataMovimento={data} | MovimentoPagamentoController | Processa e consolida os movimentos de pagamento de uma data específica do PGFT para o SPAG |

---

## 5. Principais Regras de Negócio

1. **Consolidação por Data**: O sistema processa movimentos de pagamento com base em uma data específica fornecida como parâmetro
2. **Validação de Retorno**: Verifica se houve retorno de dados do PGFT antes de prosseguir com a consolidação no SPAG
3. **Fluxo Sequencial**: Primeiro consulta os dados no PGFT, processa-os e então insere no SPAG
4. **Tratamento de Erros**: Captura e trata exceções específicas de negócio (MovimentoPagamentoException) e exceções genéricas
5. **Processamento em Lote**: Processa arrays de movimentos de pagamento de uma única vez

---

## 6. Relação entre Entidades

**MovimentoPagamento** (entidade principal):
- Representa um movimento de pagamento consolidado
- Atributos:
  - codigoOrigemPagamento: código da origem do pagamento
  - nomeOrigemPagamento: nome da origem
  - codLiquidacao: código de liquidação
  - nomeLiquidacao: nome da liquidação
  - documentoRemetente: documento do remetente
  - nomeRemetente: nome do remetente
  - quantidade: quantidade de transações
  - valorTotal: valor total consolidado
  - dataMovimento: data do movimento

Não há relacionamentos complexos entre entidades. A entidade MovimentoPagamento é utilizada como DTO para transferência de dados entre os sistemas PGFT e SPAG.

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

*Observação: O sistema não acessa diretamente bancos de dados. As consultas são realizadas através de APIs REST de outros microserviços.*

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

*Observação: O sistema não atualiza diretamente bancos de dados. As atualizações são realizadas através de APIs REST de outros microserviços.*

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot (startup) | Arquivo de configuração da aplicação com URLs de serviços e perfis |
| logback-spring.xml | leitura | Logback (startup) | Configuração de logs da aplicação |
| sboot-spag-base-orch-movimento-pagamento.yml | leitura | Swagger Codegen | Especificação OpenAPI para geração de interfaces |

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
| **pgft-base-atom-movimento-pagamento** | API REST (GET) | Microserviço que fornece dados de movimentos de pagamento do sistema PGFT. Endpoint: `/v1/consulta-pgft-pagamento/` |
| **spag-base-atom-movimento-pagamento** | API REST (POST) | Microserviço que recebe e armazena dados consolidados de movimentos de pagamento no sistema SPAG. Endpoint: `/v1/movimenta-pagamento/` |

**URLs por Ambiente:**
- DES: URLs internas do cluster Kubernetes (*.des-*.svc.cluster.local)
- QA: URLs internas do cluster Kubernetes (*.qa-*.svc.cluster.local)
- UAT: URLs internas do cluster Kubernetes (*.uat-*.svc.cluster.local)
- PRD: URLs internas do cluster Kubernetes (*.prd-*.svc.cluster.local)

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (domain, application)
- Uso adequado de padrões como Repository e Service
- Implementação de Apache Camel para orquestração, demonstrando conhecimento de integração empresarial
- Configuração adequada de segurança JWT e auditoria
- Presença de testes unitários, integração e funcionais
- Documentação OpenAPI/Swagger implementada
- Uso de Lombok para reduzir boilerplate
- Configuração de health checks e métricas

**Pontos de Melhoria:**
- Falta de tratamento mais granular de exceções (apenas uma exceção genérica de negócio)
- Logs em português misturados com código em inglês (falta de padronização)
- Métodos com nomes inconsistentes (ex: `setspagtMovimentoPagamentoUrl` com typo)
- Falta de validações de entrada mais robustas no controller
- Ausência de circuit breaker ou retry para chamadas externas
- Documentação inline limitada (poucos comentários JavaDoc)
- Configuração de timeouts não explícita para RestTemplate
- Poderia utilizar WebClient (reativo) ao invés de RestTemplate (legado)

---

## 14. Observações Relevantes

1. **Arquitetura Hexagonal**: O projeto segue princípios de arquitetura hexagonal com separação clara entre domain (portas) e infrastructure (adaptadores)

2. **Apache Camel**: Uso interessante do Apache Camel para orquestração, com rotas bem definidas e processadores específicos

3. **Segurança**: Integração com framework de segurança BV (Banco Votorantim) para autenticação JWT

4. **Multi-ambiente**: Configuração robusta para múltiplos ambientes (local, des, qa, uat, prd)

5. **Containerização**: Dockerfile otimizado usando OpenJ9 para melhor performance de memória

6. **Monitoramento**: Endpoints Actuator configurados na porta 9090 separada da aplicação (8080)

7. **CI/CD**: Configuração para Jenkins e deploy em Kubernetes/OpenShift (Google Cloud Platform)

8. **Auditoria**: Integração com trilha de auditoria do BV

9. **Profiles Maven**: Separação de testes por tipo (unit, integration, functional, architecture)

10. **Geração de Código**: Uso de Swagger Codegen para gerar interfaces a partir da especificação OpenAPI

11. **Limitação de Escopo**: O serviço é stateless e focado apenas em orquestração, não mantém estado ou dados próprios