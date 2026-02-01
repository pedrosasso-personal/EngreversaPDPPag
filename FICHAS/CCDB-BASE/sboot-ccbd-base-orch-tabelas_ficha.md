# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-ccbd-base-orch-tabelas** é um microsserviço orquestrador desenvolvido em Spring Boot que gerencia consultas e manutenções de tabelas de domínio do sistema de conta corrente do Banco Digital (CCBD). O componente atua como intermediário entre clientes e serviços atômicos, orquestrando chamadas para obter dados cadastrais de clientes e parâmetros MT940 (padrão SWIFT para extratos bancários eletrônicos). Utiliza Apache Camel para orquestração de fluxos e integra-se com outros microsserviços através de APIs REST.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application.java` | Classe principal que inicializa a aplicação Spring Boot com segurança OAuth2 habilitada |
| `TabelasController.java` | Controlador REST que expõe o endpoint de consulta de parâmetros MT940 |
| `ParametroMt940ServiceImpl.java` | Implementação do serviço que orquestra a consulta de parâmetros MT940 usando Apache Camel |
| `ParametroMt940Router.java` | Roteador Camel que define o fluxo de orquestração entre repositórios |
| `ContasGlobalRepositoryImpl.java` | Implementação do repositório que consulta contas globais via API externa |
| `ParametroMt940RepositoryImpl.java` | Implementação do repositório que consulta parâmetros MT940 via API externa |
| `ContaGlobalMapper.java` | Mapeador de objetos de domínio para representações de contas globais |
| `ParametroMt940Mapper.java` | Mapeador de objetos de domínio para representações de parâmetros MT940 |
| `ResourceExceptionHandler.java` | Tratador global de exceções HTTP |
| `CamelContextWrapper.java` | Wrapper para gerenciamento do contexto Apache Camel |
| `AppProperties.java` | Propriedades de configuração da aplicação |

---

## 3. Tecnologias Utilizadas

- **Framework Principal**: Spring Boot 2.x
- **Linguagem**: Java 11
- **Orquestração**: Apache Camel 3.0.1
- **Segurança**: Spring Security OAuth2 (Resource Server) com JWT
- **Documentação API**: Swagger/OpenAPI 2.0 (Springfox 2.9.2)
- **Geração de Código**: Swagger Codegen Maven Plugin
- **Monitoramento**: Spring Boot Actuator, Micrometer, Prometheus
- **Logs**: Logback com formato JSON
- **Testes**: JUnit 5, Rest Assured, Pact (Consumer Contract Testing)
- **Build**: Maven 3.3+
- **Containerização**: Docker
- **Infraestrutura**: OpenShift (Google Cloud Platform)
- **Auditoria**: BV Audit 2.2.1
- **Utilitários**: Lombok, Apache Commons Collections

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/manutencao-tabela/parametro-mt940/{cpfcnpj}` | `TabelasController` | Consulta parâmetros MT940 cadastrados nas contas ativas do banco digital para um CPF/CNPJ específico |

**Observação**: O endpoint requer autenticação OAuth2 com token JWT.

---

## 5. Principais Regras de Negócio

1. **Consulta de Parâmetros MT940**: O sistema busca todas as contas ativas de um cliente (por CPF/CNPJ) e retorna os parâmetros MT940 configurados para cada conta
2. **Orquestração de Chamadas**: Utiliza Apache Camel para orquestrar sequencialmente:
   - Consulta de contas globais do cliente
   - Consulta de parâmetros MT940 para as contas encontradas
3. **Filtragem de Contas Ativas**: Apenas contas sem data de encerramento são consideradas para consulta de parâmetros
4. **Mapeamento de Dados**: Conversão entre representações de API externa e objetos de domínio interno
5. **Tratamento de Erros**: Exceções customizadas com códigos de erro padronizados (BDCC_ERRO_CONSULTAR, BDCC_ERRO_INTERNO, etc.)
6. **Validação de Respostas**: Verifica se as respostas das APIs externas não são nulas antes de processar

---

## 6. Relação entre Entidades

**Entidades de Domínio:**

- **ContaGlobalDTO**: Agregador que contém CPF/CNPJ e lista de contas
  - Atributos: `cpfCnpj` (String), `contas` (List<ContaGlobal>)
  
- **ContaGlobal**: Representa uma conta corrente
  - Atributos: `cdBanco` (Integer), `numeroConta` (Long), `tipoConta` (Integer), `dataEncerramento` (String)
  
- **ParametroMt940**: Representa parâmetros MT940 de uma conta
  - Atributos: `cdBanco` (Integer), `nuCpfCnpj` (String), `nuContaCorrente` (Long), `dsLogin` (String), `isStatus` (String), `bancos` (List<ParametroBanco>)
  
- **ParametroBanco**: Representa configurações de banco para MT940
  - Atributos: `cdParametro` (String), `dsBancoDestino` (String), `periodicidades` (List<String>), `isExtrato` (String)

**Relacionamentos:**
- ContaGlobalDTO (1) ----> (N) ContaGlobal
- ParametroMt940 (1) ----> (N) ParametroBanco

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

**Observação**: O sistema não acessa diretamente banco de dados. Todas as consultas são realizadas através de APIs REST de outros microsserviços.

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

**Observação**: O sistema não realiza operações de escrita em banco de dados. É um componente de consulta/orquestração apenas.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `application.yml` | Leitura | Spring Boot Configuration | Arquivo de configuração da aplicação com URLs de serviços externos e configurações de ambiente |
| `logback-spring.xml` | Leitura | Logback Framework | Configuração de logs em formato JSON para diferentes ambientes (des, qa, uat, prd) |
| `swagger/*.yaml` | Leitura | Swagger Codegen Plugin | Especificações OpenAPI para geração de código de clientes e providers |

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
| **sboot-ccbd-base-atom-conta-corrente-dominio** | API REST | Microsserviço atômico que fornece operações nas tabelas de domínio de conta corrente. Endpoint: `/v1/manutencao-tabela/parametro-mt940/{cpfcnpj}` (POST) |
| **sboot-glob-base-atom-cliente-dados-cadastrais** | API REST | Microsserviço atômico que fornece dados cadastrais de clientes. Endpoint: `/v1/banco-digital/conta/doc/{cpfCnpj}` (GET) |
| **OAuth2 Token Service** | Autenticação | Serviço de autenticação JWT para validação de tokens. URLs variam por ambiente (des, qa, uat, prd) |
| **Prometheus** | Monitoramento | Coleta de métricas através do endpoint `/actuator/prometheus` |

**Observação**: Todas as integrações utilizam RestTemplate com segurança JWT configurada.

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões de Clean Architecture (separação em módulos: application, domain, common)
- Uso adequado de padrões de projeto (Repository, Service, Mapper)
- Boa separação de responsabilidades entre camadas
- Uso de Lombok para reduzir boilerplate
- Configuração adequada de testes (unit, integration, functional)
- Documentação OpenAPI bem estruturada
- Uso de Apache Camel para orquestração de forma apropriada
- Tratamento de exceções centralizado

**Pontos de Melhoria:**
- Falta de JavaDoc em várias classes importantes
- Alguns métodos privados nos Mappers poderiam ter melhor nomenclatura
- Ausência de validações de entrada nos endpoints (Bean Validation)
- Testes unitários não foram fornecidos para análise completa
- Configurações hardcoded em alguns lugares (poderia usar mais externalização)
- Falta de logs estruturados em pontos críticos do fluxo
- Ausência de circuit breakers ou retry policies para chamadas externas
- Código de geração Swagger poderia ser melhor organizado

---

## 14. Observações Relevantes

1. **Arquitetura Multi-Módulo**: O projeto está organizado em três módulos Maven (application, domain, common), seguindo boas práticas de separação de responsabilidades

2. **Geração de Código**: Utiliza Swagger Codegen para gerar automaticamente clientes REST e interfaces de API, reduzindo código manual e garantindo conformidade com contratos

3. **Ambientes Múltiplos**: Configuração preparada para múltiplos ambientes (local, des, qa, uat, prd) com URLs e configurações específicas

4. **Segurança**: Implementa OAuth2 Resource Server com validação JWT, integrando com o padrão de segurança do Banco Votorantim

5. **Observabilidade**: Bem instrumentado com Actuator, Prometheus e Grafana para monitoramento de métricas

6. **Testes por Contrato**: Implementa Pact para testes de contrato entre consumidor e provedor

7. **Infraestrutura como Código**: Possui arquivo `infra.yml` com configurações para deploy em OpenShift/Kubernetes

8. **Padrão de Nomenclatura**: Segue convenção de nomenclatura do Banco Votorantim (sboot-ccbd-base-orch-*)

9. **Auditoria**: Integrado com biblioteca de auditoria corporativa do BV (trilha de auditoria)

10. **Limitações Identificadas**: 
    - Não possui mecanismos de resiliência (circuit breaker, retry)
    - Ausência de cache para otimizar chamadas repetidas
    - Não implementa paginação (pode ser problema com grandes volumes)

11. **Tecnologia Legacy**: Uso de Swagger 2.0 (poderia migrar para OpenAPI 3.0)

12. **Docker**: Imagem otimizada usando OpenJ9 Alpine para reduzir footprint de memória