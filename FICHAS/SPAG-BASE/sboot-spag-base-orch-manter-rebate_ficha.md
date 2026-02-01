# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-spag-base-orch-manter-rebate** é um serviço de orquestração desenvolvido em Java com Spring Boot, responsável pela parametrização de produtos de rebate. Trata-se de um microserviço stateless que atua como camada de orquestração, recebendo requisições REST para parametrização de produtos e delegando o processamento para um serviço atômico externo através de integração HTTP. O sistema utiliza Apache Camel para roteamento de mensagens e segue uma arquitetura em camadas (presentation, domain, infrastructure).

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application.java` | Classe principal que inicializa a aplicação Spring Boot |
| `ParametrizacaoProdutoController.java` | Controlador REST que expõe o endpoint de parametrização de produto |
| `ParametrizacaoProdutoService.java` | Serviço de domínio que orquestra a parametrização utilizando Apache Camel |
| `ParametrizacaoRebateProdutoRouter.java` | Rota Camel que define o fluxo de processamento da parametrização |
| `ParametrizacaoRebateProdutoRepositoryImpl.java` | Implementação do repositório que realiza chamadas HTTP ao serviço atômico |
| `CamelContextWrapper.java` | Wrapper para gerenciar o contexto do Apache Camel |
| `ParametrizacaoProdutoMapper.java` | Mapper para conversão entre objetos de domínio e representações REST |
| `ManterRebateConfiguration.java` | Classe de configuração Spring que define os beans da aplicação |
| `RestResponseEntityExceptionHandler.java` | Tratador global de exceções para requisições REST |
| `OpenApiConfiguration.java` | Configuração do Swagger/OpenAPI para documentação da API |

---

## 3. Tecnologias Utilizadas

- **Java 11** - Linguagem de programação
- **Spring Boot** - Framework principal para desenvolvimento da aplicação
- **Apache Camel 3.0.1** - Framework de integração e roteamento de mensagens
- **Spring Web** - Para criação de APIs REST
- **Spring Actuator** - Para monitoramento e métricas da aplicação
- **Micrometer/Prometheus** - Para coleta de métricas
- **Swagger/Springfox 2.9.2** - Para documentação de APIs
- **Lombok** - Para redução de código boilerplate
- **RestTemplate** - Cliente HTTP para integração com serviços externos
- **Maven** - Gerenciamento de dependências e build
- **Docker** - Containerização da aplicação
- **JUnit 5** - Framework de testes unitários
- **Mockito** - Framework para criação de mocks em testes
- **Rest Assured** - Testes funcionais de APIs REST
- **Pact** - Testes de contrato entre consumidor e provedor

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/parametrizacao/produto` | `ParametrizacaoProdutoController` | Recebe uma requisição de parametrização de produto de rebate e retorna os dados parametrizados |

---

## 5. Principais Regras de Negócio

1. **Parametrização de Produto de Rebate**: O sistema recebe dados de parametrização de produtos incluindo periodicidade, forma de rebate (valor ou percentual), aprovação, emails, tipo de entrada (rede ou corban), tipo de apuração e faixas de parametrização.

2. **Validação de Faixas**: Suporta múltiplas faixas de parametrização com valores "de" e "até", percentuais, valores fixos e modo de apuração (quantidade ou valor).

3. **Tipos de Periodicidade**: Suporta diferentes periodicidades para rebate: SEMANAL, MENSAL, DIARIA e PERSONALIZADO.

4. **Formas de Rebate**: Permite rebate por VALOR fixo ou PERCENTUAL.

5. **Tipos de Apuração**: Suporta apuração para OUTROS_BANCOS, MESMO_BANCO ou AMBOS.

6. **Contagem de Prazo**: Permite definir se o prazo de pagamento é contado em dias UTEIS ou CORRIDOS.

7. **Fluxo de Aprovação**: Sistema suporta fluxo de aprovação com configuração de emails para caixa, aprovação e cópia.

8. **Orquestração via Camel**: Utiliza Apache Camel para orquestrar a chamada ao serviço atômico de parametrização.

---

## 6. Relação entre Entidades

**Entidades principais:**

- **ParametrizacaoProduto**: Entidade principal que representa a parametrização de um produto de rebate
  - Atributos: periodicidade, quantidadeDias, formaRebate, percentualImposto, aprovacao, emailCaixa, emailsEmCopia, emailsAprovacao, tipoEntrada, apuracao, valorRede, valorCorban, prazoPagamento, contagemPrazo, codProduto
  - Relacionamento: Possui uma lista de FaixaParametrizacaoProduto (1:N)

- **FaixaParametrizacaoProduto**: Representa uma faixa de valores/quantidades para parametrização
  - Atributos: de, ate, percentual, valor, tipoEntrada, modoApuracao
  - Relacionamento: Pertence a uma ParametrizacaoProduto (N:1)

- **ParametrizacaoProdutoResponse**: Entidade de resposta após parametrização
  - Atributos: Herda todos de ParametrizacaoProduto + id, ativo, dataPagamento

**Enums utilizados:**
- ContagemPrazo (UTEIS, CORRIDOS)
- FormaRebate (VALOR, PERCENTUAL)
- ModoApuracao (QUANTIDADE, VALOR)
- Periodicidade (SEMANAL, MENSAL, DIARIA, PERSONALIZADO)
- TipoApuracao (OUTROS_BANCOS, MESMO_BANCO, AMBOS)
- TipoEntrada (REDE, CORBAN)

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
| `application.yml` | leitura | Spring Boot | Arquivo de configuração da aplicação com propriedades de ambiente, URLs de serviços externos e configurações do servidor |
| `logback-spring.xml` | leitura | Logback | Configuração de logs da aplicação em formato JSON e console |

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
| **sboot-spag-base-manter-regras** | API REST (HTTP POST) | Serviço atômico responsável pela parametrização efetiva do produto. Endpoint: `/parametrizacao/produto`. Configurado via propriedade `bv.spag-base.manter-regras.url` (padrão: http://localhost:8081) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (presentation, domain, infrastructure)
- Uso adequado de padrões como Repository, Service e Mapper
- Utilização de Lombok para redução de boilerplate
- Configuração adequada de testes (unitários, integração e funcionais)
- Documentação via Swagger configurada
- Uso de Apache Camel para orquestração, demonstrando conhecimento de padrões de integração
- Configuração de métricas e monitoramento (Actuator, Prometheus)
- Estrutura modular com separação em módulos Maven (common, domain, application)

**Pontos de Melhoria:**
- Classes de teste vazias (ManterRebateServiceTest, ManterRebateControllerTest, ManterRebateConfigurationTest)
- Falta de validações de entrada nos endpoints REST (sem anotações @Valid, @NotNull, etc)
- Ausência de tratamento específico de exceções de negócio
- Uso de RestTemplate (considerado legado, poderia usar WebClient)
- Falta de logs estruturados nas classes de serviço
- Ausência de documentação JavaDoc nas classes principais
- Configuração de segurança não implementada
- Testes funcionais com implementação vazia

O código demonstra boas práticas arquiteturais e organização, mas carece de implementações completas em áreas críticas como validação, tratamento de erros e testes.

---

## 14. Observações Relevantes

1. **Arquitetura de Orquestração**: O sistema atua como um orquestrador, não realizando processamento de negócio direto, apenas delegando para o serviço atômico `manter-regras`.

2. **Apache Camel**: A utilização do Apache Camel adiciona uma camada de abstração para integração, permitindo futura expansão para outros tipos de integração (mensageria, arquivos, etc) sem grandes alterações no código.

3. **Configuração Multi-Ambiente**: O sistema está preparado para múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas de log para cada ambiente.

4. **Infraestrutura como Código**: Possui configuração completa para deploy em OpenShift/Kubernetes através do arquivo `infra.yml`.

5. **Observabilidade**: Configuração completa de métricas com Prometheus e Grafana, incluindo docker-compose para ambiente local.

6. **Auditoria**: Dependências configuradas para trilha de auditoria (`springboot-arqt-base-trilha-auditoria-web`).

7. **Testes de Contrato**: Configuração de Pact para testes de contrato, demonstrando preocupação com integração entre serviços.

8. **RabbitMQ**: Embora não utilizado no código atual, há configuração completa de RabbitMQ disponível, sugerindo possível evolução futura para arquitetura orientada a eventos.

9. **Padrão BV**: O projeto segue os padrões arquiteturais do Banco Votorantim, utilizando parent POM `arqt-base-master-springboot` e bibliotecas corporativas.

10. **Versionamento**: Sistema está na versão 0.2.0, indicando que ainda está em fase de desenvolvimento/evolução.