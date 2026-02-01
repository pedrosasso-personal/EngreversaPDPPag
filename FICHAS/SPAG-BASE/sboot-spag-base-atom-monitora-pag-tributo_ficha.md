# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de monitoramento de pagamentos de tributos e contas de consumo do Banco Votorantim. O serviço atômico fornece APIs REST para consulta de informações analíticas sobre o processamento de pagamentos, incluindo monitoramento de etapas, SLA, duplicidades e portabilidade de salário. Permite acompanhar o ciclo de vida dos lançamentos desde a inclusão até a efetivação, com foco em pagamentos de tributos (liquidação 59) e contas de consumo (liquidação 60).

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `MonitoraPagTributoController` | Controlador REST que expõe endpoints para consultas de monitoramento |
| `MonitoraEtapaPagTributoService` | Serviço que gerencia consultas de etapas do processamento de pagamentos |
| `AnaliticoService` | Serviço para consultas analíticas detalhadas de lançamentos |
| `DuplicidadeService` | Serviço para identificação e consulta de pagamentos duplicados |
| `SlaService` | Serviço para monitoramento de SLA (Service Level Agreement) |
| `PortabilidadeSalarioService` | Serviço para consulta de lançamentos de portabilidade de salário |
| `AnaliticoRepositoryImpl` | Implementação de repositório para consultas analíticas via JDBI |
| `MonitoraDashPagTributoRepositoryImpl` | Implementação de repositório para consultas de dashboard |
| `PortabilidadeSalarioRepositoryImpl` | Implementação de repositório para consultas de portabilidade |
| `AnaliticoConvert` | Conversor de objetos de domínio para representações REST |
| `ConvertEtapaImpl` | Conversor de etapas e duplicidades para representações REST |

## 3. Tecnologias Utilizadas

- **Framework Principal**: Spring Boot 2.x
- **Java**: JDK 11
- **Persistência**: JDBI 3.9.1 (SQL Object)
- **Banco de Dados**: Microsoft SQL Server (driver 7.4.0.jre11)
- **Segurança**: Spring Security OAuth2 com JWT
- **Documentação API**: Swagger/OpenAPI 3.0.0 (Springfox)
- **Monitoramento**: Spring Boot Actuator + Micrometer + Prometheus
- **Visualização**: Grafana
- **Build**: Maven 3.3+
- **Containerização**: Docker
- **Orquestração**: Kubernetes/OpenShift (Google Cloud Platform)
- **Testes**: JUnit 5, Mockito, Rest Assured, Pact
- **Utilitários**: Lombok, Apache Commons Lang3, Apache Commons Text
- **Auditoria**: BV Audit 2.3.5
- **Pool de Conexões**: HikariCP

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/monitora/esteira/etapa` | `MonitoraPagTributoController` | Consulta etapas da esteira de processamento |
| GET | `/v1/monitora/sla` | `MonitoraPagTributoController` | Consulta etapas com violação de SLA |
| GET | `/v1/monitora/analitico` | `MonitoraPagTributoController` | Consulta analítica de lançamentos por data, canal e status |
| GET | `/v1/monitora/analitico-sla` | `MonitoraPagTributoController` | Consulta analítica de lançamentos com violação de SLA |
| GET | `/v1/monitora/duplicidade` | `MonitoraPagTributoController` | Consulta dashboard de duplicidades |
| GET | `/v1/monitora/analitico-duplicidade` | `MonitoraPagTributoController` | Consulta analítica de lançamentos duplicados |
| GET | `/v1/monitoramento/portabilidade-salario/lancamentos` | `MonitoraPagTributoController` | Consulta lançamentos de portabilidade de salário |

## 5. Principais Regras de Negócio

- **Filtro de Liquidação**: Sistema processa apenas pagamentos de tributos (código 59) e contas de consumo (código 60)
- **Origem de Operação**: Filtra operações com origem >= 88 (canais digitais)
- **Etapas de Processamento**: Pré-processamento (status 0,5,7), Em Processamento (status 1), Montagem de Lote (status 2)
- **SLA de Processamento**: 
  - Pré-processamento e Em Processamento: 300 segundos (5 minutos)
  - Montagem de Lote: 3600 segundos (1 hora)
- **Detecção de Duplicidade**: Identifica pagamentos duplicados pelo código de barras no mesmo dia de movimento
- **Status Finais**: Pagamento confirmado (3), Rejeitado (4), Com erro (8), Cancelado (99)
- **Portabilidade de Salário**: Suporta consultas de pagamentos (transação 8941, SPB PAG0137R2) e estornos
- **Ranges de Consulta**: Diária (data específica) ou Mensal (último mês)

## 6. Relação entre Entidades

**Entidades Principais:**

- **Analitico**: Representa informações detalhadas de um lançamento de pagamento
  - Contém dados do remetente, valor, status, protocolos, datas
  
- **Etapa**: Representa uma etapa do processamento
  - Atributos: descrição, quantidade, valorTotal

- **ResultEtapaMelhoria**: Agregação de etapas e resultados
  - Relacionamento: contém lista de Etapas e um ResultConfirma

- **ResultConfirma**: Resultado consolidado de pagamentos processados
  - Relacionamento: contém lista de Lista (detalhamento por status)

- **Duplicidade**: Representa pagamentos duplicados
  - Atributos: codigoBarra, quantidade

- **LancamentoSalario**: Representa lançamento de portabilidade de salário
  - Contém dados completos do lançamento, favorecido e status

- **ConsultaLancamentoSalario**: DTO para filtros de consulta de portabilidade

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbLancamento | Tabela | SELECT | Tabela principal de lançamentos de pagamento |
| TbStatusLancamento | Tabela | SELECT | Tabela de domínio de status de lançamento |
| TbLancamentoPessoa | Tabela | SELECT | Dados de pessoas (remetente/favorecido) do lançamento |
| TbErroProcessamento | Tabela | SELECT | Detalhes de erros ocorridos no processamento |
| TbLotePagamentoTributo | Tabela | SELECT | Informações de lotes de pagamento de tributo |

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | leitura | `/usr/etc/log` (runtime) | Configuração de logs da aplicação |
| application.yml | leitura | `application/src/main/resources` | Configurações da aplicação Spring Boot |
| *.sql | leitura | `resources/.../repository/*RepositoryImpl/` | Queries SQL para consultas ao banco |
| sboot-spag-base-atom-monitora-pag-tributo.yaml | leitura | `resources/swagger/` | Especificação OpenAPI da API |

## 10. Filas Lidas

não se aplica

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| API Gateway BV | REST/OAuth2 | Autenticação e autorização via OAuth2 JWT |
| SQL Server (DBSPAG) | JDBC | Banco de dados principal para consultas de lançamentos |
| Prometheus | Métricas | Exportação de métricas de monitoramento |
| Grafana | Visualização | Dashboard de métricas e monitoramento |

## 13. Avaliação da Qualidade do Código

**Nota:** 7.5/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (application, domain, common)
- Uso adequado de padrões como Repository, Service e DTO
- Implementação de testes unitários com boa cobertura
- Uso de Lombok para reduzir boilerplate
- Configuração adequada de segurança OAuth2
- Documentação OpenAPI/Swagger bem estruturada
- Uso de JDBI para queries SQL organizadas em arquivos separados
- Tratamento de exceções customizado

**Pontos de Melhoria:**
- Algumas classes de serviço com lógica de negócio misturada com formatação (ex: `MonitoraEtapaPagTributoService.formatResultMelhoria`)
- Uso de `LogUtil.escape` inconsistente (nem todos os logs fazem sanitização)
- Conversores poderiam usar MapStruct ao invés de conversão manual
- Alguns métodos longos que poderiam ser refatorados (ex: queries SQL complexas inline)
- Falta de validação de entrada em alguns endpoints
- Comentários em português misturados com código em inglês
- Algumas classes de teste com nomenclatura inconsistente
- Uso de `@Slf4j` mas com logs manuais em alguns lugares

## 14. Observações Relevantes

- **Ambiente Multi-Cloud**: Sistema preparado para deploy em Google Cloud Platform via Kubernetes/OpenShift
- **Monitoramento Robusto**: Integração completa com stack de observabilidade (Actuator, Prometheus, Grafana)
- **Segurança**: Implementa OAuth2 com JWT para autenticação e autorização
- **Configuração por Ambiente**: Suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas
- **Pipeline CI/CD**: Integrado com Jenkins para build e deploy automatizado
- **Testes Arquiteturais**: Utiliza ArchUnit para validação de regras arquiteturais
- **Versionamento**: Sistema de versionamento semântico (0.36.0)
- **Pool de Conexões**: Utiliza HikariCP com monitoramento de métricas
- **Auditoria**: Integração com trilha de auditoria do Banco Votorantim
- **Documentação**: README bem estruturado com links para confluence e documentação técnica
- **Healthcheck**: Endpoints de health configurados para liveness e readiness probes no Kubernetes