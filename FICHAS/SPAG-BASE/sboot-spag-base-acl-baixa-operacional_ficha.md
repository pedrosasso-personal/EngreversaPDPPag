# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-spag-base-acl-baixa-operacional** é um serviço ACL (Anti-Corruption Layer) desenvolvido em Spring Boot que atua como camada de integração para processar baixas operacionais de boletos de pagamento. O sistema recebe requisições de baixa de boletos, registra o envio em um sistema de processamento e solicita a baixa através de um roteador (Atom DDA Router). Utiliza Apache Camel para orquestração de fluxos e integra-se com serviços SOAP legados e APIs REST modernas.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `BaixaOperacionalController` | Controller REST que expõe o endpoint `/v1/api/baixa-operacional` para receber requisições de baixa de boletos |
| `BaixaOperacionalService` | Serviço de domínio que orquestra o processo de baixa de boleto através do Apache Camel |
| `BaixaOperacionalRouter` | Rota Camel que define o fluxo de processamento: registrar envio → solicitar baixa |
| `RegistrarBaixaBoletoImpl` | Implementação que registra o envio da baixa no sistema de processamento via REST |
| `SolicitaBaixaImpl` | Implementação que solicita a baixa do boleto através do Atom DDA Router |
| `BoletoCompletoInfoMapperImpl` | Mapper que converte representações REST em objetos de domínio |
| `RegistroPagamentoCIPMapper` | Mapper que converte informações de boleto em registro de pagamento CIP |
| `BaixaOperacionalExceptionHandler` | Handler global de exceções para tratamento centralizado de erros |
| `CamelContextWrapper` | Wrapper que encapsula o contexto do Apache Camel |
| `ScanFaultCIP` | Utilitário para extrair mensagens de erro de respostas SOAP |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.x** (framework principal)
- **Java 11** (linguagem e runtime)
- **Apache Camel 3.0.1** (orquestração de fluxos)
- **Spring Security OAuth2** (autenticação e autorização JWT)
- **Swagger/OpenAPI 3.0** (documentação de API)
- **Micrometer + Prometheus** (métricas e monitoramento)
- **Grafana** (visualização de métricas)
- **Logback** (logging)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **OpenShift/Kubernetes** (orquestração de containers)
- **MapStruct** (mapeamento de objetos)
- **Lombok** (redução de boilerplate)
- **JUnit 5 + Mockito** (testes unitários)
- **RestAssured** (testes funcionais)
- **Pact** (testes de contrato)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/api/baixa-operacional` | `BaixaOperacionalController` | Recebe informações completas do boleto para processar baixa operacional |
| GET | `/actuator/health` | Spring Actuator | Verifica o status de saúde da aplicação |
| GET | `/actuator/metrics` | Spring Actuator | Expõe métricas da aplicação |
| GET | `/actuator/prometheus` | Spring Actuator | Expõe métricas no formato Prometheus |
| GET | `/swagger-ui/*` | Springfox | Interface de documentação Swagger |

---

## 5. Principais Regras de Negócio

1. **Validação de Meio de Pagamento**: Se o meio de pagamento não for informado, o sistema assume "Débito em Conta" (código 2) como padrão
2. **Identificação de Operação Intrabancária**: Verifica se a operação é intrabancária através dos 3 primeiros dígitos do código de barras (655 = BVSA)
3. **Flag de Notificação**: Para operações intrabancárias, a flag de notificação é definida como "N" (Não); para outras operações, não é preenchida
4. **Processamento CIP**: Todas as baixas são marcadas com flag de processamento CIP como "S" (Sim)
5. **Orquestração de Fluxo**: O processo segue obrigatoriamente a ordem: registrar envio da baixa → solicitar baixa ao roteador
6. **Tratamento de Erros SOAP**: Extrai e formata mensagens de erro de respostas SOAP do serviço legado
7. **Autenticação OAuth2**: Todas as chamadas externas utilizam token JWT obtido via OAuth2 Client Credentials

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **BoletoCompletoInfoRepresentation**: Representação REST completa do boleto recebido na API
  - Contém: `BoletoInfoRepresentation`, dados do portador, valores, datas, canal/meio de pagamento
  
- **BoletoInfoBaixa**: Objeto de domínio com informações da baixa
  - Relaciona-se com: participantes (ISPB), valores, datas, indicadores
  
- **RegistroPagamentoCIP**: Registro de pagamento no formato CIP
  - Derivado de: `BoletoInfoBaixa`
  - Contém: códigos de meio/canal, ISPBs, valores, flags de controle

**Fluxo de Transformação:**
```
BoletoCompletoInfoRepresentation → BoletoInfoBaixa → RegistroPagamentoCIP
```

**Enumerações:**
- `BancoEnum`: Códigos de bancos (BV=413, BVSA=655)
- `MeioPagamentoEnum`: Tipos de meio de pagamento (Dinheiro, Débito, Crédito, Cheque)
- `FlagSimNaoEnum`: Flags booleanas (S/N)

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
| `logback-spring.xml` | Leitura | `/usr/etc/log` (runtime) | Arquivo de configuração de logs carregado em tempo de execução |
| `application.yml` | Leitura | `src/main/resources` | Arquivo de configuração da aplicação Spring Boot |
| `BoletoPagamentoIntegrationServiceContract*.wsdl` | Leitura | `src/main/resources/wsdl` | Contratos WSDL dos serviços SOAP de boleto (DES/UAT/PRD) |
| `sboot-spag-base-acl-baixa-operacional.yaml` | Leitura | `src/main/resources/swagger` | Especificação OpenAPI da API REST |

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
| **Atom DDA Router** | REST API | Roteador que processa solicitações de baixa de boletos. Endpoints: `/v1/solicitarBaixaBoleto` |
| **Processar Retorno Baixa Boleto** | REST API | Sistema que registra o envio de baixas de boletos. Endpoint: `/v1/incluirEnvioBaixaBoletoSPAG` |
| **Boleto Pagamento Integration Service** | SOAP/WSDL | Serviço legado de integração de boletos de pagamento (Service Bus) |
| **API Gateway BV** | OAuth2 | Gateway de autenticação para obtenção de tokens JWT. Endpoint: `/auth/oauth/v2/token-jwt` |
| **Prometheus** | Métricas | Sistema de coleta de métricas via endpoint `/actuator/prometheus` |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (application, domain, common)
- Uso adequado de padrões como Mapper, Repository (Port), Service
- Implementação de testes unitários, funcionais e de integração
- Configuração adequada de profiles para diferentes ambientes
- Uso de Apache Camel para orquestração de fluxos complexos
- Documentação OpenAPI/Swagger bem estruturada
- Configuração de observabilidade (métricas, logs, health checks)

**Pontos de Melhoria:**
- Código comentado em alguns testes (ex: `ConfirmaPagamentoClientImplTest`, `ApplicationTest`)
- Classe `ScanFaultCIP` com lógica de parsing de XML manual e pouco testável
- Falta de validações de entrada mais robustas nos controllers
- Alguns métodos com múltiplas responsabilidades (ex: `RegistroPagamentoCIPMapper.fromBoletoInfo`)
- Tratamento de exceções genérico no `BaixaOperacionalExceptionHandler`
- Falta de logs estruturados em alguns pontos críticos
- Configurações hardcoded em algumas classes (ex: login "sboot-spag-base-acl-baixa-operacional")

---

## 14. Observações Relevantes

1. **Arquitetura ACL**: O sistema atua como Anti-Corruption Layer, isolando o domínio interno de integrações externas legadas e modernas

2. **Múltiplos Ambientes**: Suporte completo para ambientes local, des, qa, uat e prd com configurações específicas

3. **Segurança**: Implementa OAuth2 com JWT para autenticação e autorização, com endpoints públicos configuráveis

4. **Resiliência**: Não há evidências de implementação de circuit breaker ou retry policies para chamadas externas

5. **Monitoramento**: Infraestrutura completa de observabilidade com Prometheus, Grafana e dashboards pré-configurados

6. **Containerização**: Dockerfile otimizado com OpenJ9 JVM e configurações de timezone

7. **CI/CD**: Integração com Jenkins através de `jenkins.properties` e configuração de infraestrutura como código

8. **Testes**: Estrutura de testes bem organizada (unit, integration, functional) com suporte a testes de arquitetura via ArchUnit

9. **Dependências Legadas**: Mantém compatibilidade com serviços SOAP legados através de WSDLs versionados

10. **Versionamento de API**: API versionada com prefixo `/v1/api`