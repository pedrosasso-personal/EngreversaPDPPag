# Ficha Técnica do Sistema

---

## 1. Descrição Geral

Sistema de cálculo de taxas de financiamento para produtos Flex do Banco Votorantim. Trata-se de uma camada ACL (Anti-Corruption Layer) que expõe uma API REST moderna e consome um serviço SOAP legado para obter taxas de financiamento, incluindo CET, IOF, taxas pactuadas e informações de controladoria.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `TaxaFinanciamentoController` | Controller REST que expõe o endpoint de listagem de taxas de financiamento |
| `TaxaFinanciamentoFlexService` | Serviço de domínio que orquestra o fluxo de cálculo de taxas via Apache Camel |
| `TaxaFinanciamentoFlexRouter` | Roteador Apache Camel que define o fluxo de processamento |
| `TaxaFinanciamentoRepositoryImpl` | Implementação do repositório que consome o serviço SOAP backend |
| `TaxaFinanciamentoBackendConnector` | Conector SOAP que realiza a comunicação com o serviço legado |
| `TaxaFinanciamentoMapper` | Mapper MapStruct para conversão entre representações REST e SOAP |
| `SOAPConfiguration` | Configuração de segurança e headers SOAP (WS-Security) |
| `CamelContextWrapper` | Wrapper do contexto Apache Camel para integração com Spring |
| `LogInfo` | Utilitário centralizado de logging com mascaramento de dados sensíveis |
| `ExceptionProcessor` | Processador Camel para tratamento de exceções |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.x** (framework base)
- **Java 11** (linguagem e runtime)
- **Apache Camel 3.0.1** (orquestração e integração)
- **Spring Web Services** (cliente SOAP)
- **MapStruct 1.4.1** (mapeamento de objetos)
- **Swagger/OpenAPI 2.0** (documentação de API)
- **Lombok** (redução de boilerplate)
- **Micrometer + Prometheus** (métricas)
- **Logback** (logging)
- **Maven** (build)
- **Docker** (containerização)
- **Grafana** (visualização de métricas)
- **WS-Security** (segurança SOAP)
- **JAXB** (binding XML)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/varejo/contratos/gestao/taxa/financiamento` | `TaxaFinanciamentoController` | Lista taxas de financiamento calculadas com base nos parâmetros fornecidos (produto, modalidade, valor, parcelas, etc) |

---

## 5. Principais Regras de Negócio

- Cálculo de taxas de financiamento para produtos Flex considerando:
  - Código do produto e modalidade
  - Tipo de pessoa (física/jurídica)
  - Indicador de proposta
  - Informações de subsídio (retenção e liberação)
  - Valor financiado sem custos
  - Taxa de juros
  - Quantidade de dias de carência
  - Período de pagamento
  - Datas de cálculo e primeiro vencimento
  - Quantidade de parcelas e valor da prestação
  - Custos adicionais por tipo

- Retorno de taxas calculadas:
  - Taxa CET anual e mensal
  - Taxa pactuada anual e mensal (com e sem arredondamento)
  - Taxa gerencial
  - Taxa de retenção
  - Taxa e valor de IOF

- Tratamento de erros de negócio com códigos específicos:
  - Erro ao chamar serviço backend (código 200)
  - Serviço não retornou taxas (código 205)
  - Erro ao mapear dados (código 300)

- Mascaramento de dados sensíveis em logs (últimos 6 caracteres visíveis)

---

## 6. Relação entre Entidades

**Entidades principais:**

- `TaxaFinanciamento`: Entidade raiz contendo todos os parâmetros de entrada e saída
  - Contém 1 `InformacaoSubsidio` (opcional)
  - Contém 1 `Taxa` (resultado)
  - Contém N `Custo` (lista de custos)

- `Taxa`: Contém todas as taxas calculadas (CET, pactuada, IOF, etc)

- `Custo`: Representa um custo adicional com código de tipo e valor

- `InformacaoSubsidio`: Informações de retenção e liberação de subsídio

- `Controladoria`: Entidade de controladoria (presente no domínio mas não utilizada no fluxo principal)
  - Contém 1 `ParceiroComercial`

**Relacionamentos:**
- TaxaFinanciamento 1 ---> 0..1 InformacaoSubsidio
- TaxaFinanciamento 1 ---> 0..1 Taxa
- TaxaFinanciamento 1 ---> 0..N Custo
- Controladoria 1 ---> 0..1 ParceiroComercial

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
| `application.yml` | leitura | Spring Boot | Configuração da aplicação (profiles, endpoints, credenciais) |
| `logback-spring.xml` | leitura | Logback | Configuração de logging |
| `TaxaFinanciamentoFlexBackendService.wsdl` | leitura | JAXB/Spring WS | Contrato SOAP do serviço backend |
| `*.xsd` (schemas) | leitura | JAXB | Schemas XML para validação SOAP |
| `sboot-flex-calc-acl-taxa-financiamento-flex.yaml` | leitura | Swagger Codegen | Especificação OpenAPI para geração de código |

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
| `TaxaFinanciamentoFlexBackendService` | SOAP/HTTPS | Serviço legado de cálculo de taxas de financiamento. Endpoint configurável por ambiente (DES/UAT/PRD). Utiliza WS-Security com usuário/senha e trilha de auditoria customizada no header SOAP. |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7.5/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões de Clean Architecture (separação em módulos: common, domain, application)
- Uso adequado de padrões como Repository, Mapper, e Anti-Corruption Layer
- Boa separação de responsabilidades entre camadas
- Uso de MapStruct para mapeamento automático reduzindo código boilerplate
- Implementação de logging estruturado com mascaramento de dados sensíveis
- Configuração adequada de métricas e observabilidade (Prometheus/Grafana)
- Uso de Apache Camel para orquestração de forma adequada
- Tratamento de exceções customizado e estruturado

**Pontos de Melhoria:**
- Falta de testes unitários e de integração (diretórios vazios)
- Comentários em português misturados com código em inglês
- Algumas classes com responsabilidades que poderiam ser melhor distribuídas
- Configuração de segurança SOAP com credenciais em variáveis de ambiente (bom), mas código de montagem do header SOAP poderia ser mais limpo
- Falta de validações de entrada mais robustas nos endpoints
- Documentação inline limitada em algumas classes críticas
- Uso de `@SuppressWarnings` sem justificativa clara em alguns pontos

---

## 14. Observações Relevantes

1. **Arquitetura Multi-módulo**: O projeto está organizado em 3 módulos Maven (common, domain, application), seguindo boas práticas de separação de responsabilidades.

2. **Profiles Maven**: Existem profiles específicos para diferentes tipos de teste (unit, integration, functional, architecture), embora os testes não estejam implementados.

3. **Segurança SOAP**: Implementa WS-Security com username/password token e trilha de auditoria customizada no header SOAP, incluindo informações como ticket, sistema origem, usuário final, IP e fase.

4. **Configuração por Ambiente**: Suporta múltiplos ambientes (local, des, uat, prd) com configurações específicas via Spring Profiles.

5. **Containerização**: Inclui Dockerfile otimizado usando OpenJ9 (JVM com menor footprint de memória).

6. **Infraestrutura como Código**: Possui arquivo `infra.yml` para deploy em OpenShift/Kubernetes com configurações de probes, volumes, secrets e configmaps.

7. **Observabilidade**: Stack completa de métricas com Prometheus e Grafana, incluindo dashboards pré-configurados para monitoramento de JVM, HTTP, HikariCP e logs.

8. **Geração de Código**: Utiliza plugins Maven para geração automática de código a partir de WSDL (JAXB) e OpenAPI (Swagger Codegen).

9. **Auditoria**: Integração com biblioteca corporativa de trilha de auditoria (`springboot-arqt-base-trilha-auditoria-web`).

10. **Padrão de Nomenclatura**: Segue convenção de nomenclatura corporativa do Banco Votorantim (prefixo `sboot-flex-calc-acl-`).