# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-ccbd-base-atom-extrato** é um serviço atômico desenvolvido em Spring Boot para gerenciar extratos bancários do Banco Digital (CCBD). O sistema permite consultar movimentações financeiras, histórico de saldos e exportar extratos em diferentes formatos (PDF e OFX). Utiliza tanto banco de dados relacional (Sybase) quanto Elasticsearch para consultas otimizadas, além de integração com Google Cloud Pub/Sub para processamento assíncrono de exportações.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application.java` | Classe principal que inicializa a aplicação Spring Boot |
| `ExtratoV1Controller.java` | Controlador REST que expõe endpoints de consulta e exportação de extratos |
| `ExtratoService.java` | Serviço de domínio que orquestra a lógica de negócio de extratos |
| `ExtratoElasticsearchRepositoryImpl.java` | Implementação de repositório para consultas no Elasticsearch |
| `ConsultaMovimentacoesRepositoryImpl.java` | Repositório para consulta de movimentações no banco Sybase |
| `HistoricoSaldoRepositoryImpl.java` | Repositório para consulta de histórico de saldos no banco Sybase |
| `EnviarMensagemTopicoExportarExtratoRepositoryImpl.java` | Repositório responsável por enviar mensagens para fila Pub/Sub |
| `ExtratoConverter.java` | Conversor de entidades de domínio para representações de API |
| `SearchSourceRequestBuilder.java` | Construtor de queries Elasticsearch com filtros, paginação e agregações |
| `FeatureToggleService.java` | Serviço para gerenciar feature toggles via ConfigCat |
| `ExtratoExceptionHandler.java` | Tratador global de exceções específicas do domínio de extrato |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.x** (framework principal)
- **Java 11**
- **Elasticsearch 7.10.0** (consultas otimizadas de movimentações)
- **Sybase jConnect 16.3** (banco de dados relacional)
- **JDBI 3.9.1** (acesso a dados SQL)
- **Google Cloud Pub/Sub** (mensageria assíncrona)
- **Spring Cloud GCP 1.2.8** (integração com GCP)
- **Swagger/OpenAPI 3.0** (documentação de API)
- **MapStruct 1.5.5** (mapeamento de objetos)
- **Lombok** (redução de boilerplate)
- **Micrometer + Prometheus** (métricas e monitoramento)
- **Grafana** (visualização de métricas)
- **ConfigCat** (feature toggles)
- **JUnit 5 + Mockito** (testes unitários)
- **RestAssured** (testes funcionais)
- **Pact** (testes de contrato)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/extrato/exportar` | `ExtratoV1Controller` | Solicita exportação de extrato (envia para fila Pub/Sub) |
| POST | `/v1/extrato/pesquisas` | `ExtratoV1Controller` | Realiza pesquisa de movimentações com filtros avançados no Elasticsearch |

---

## 5. Principais Regras de Negócio

1. **Validação de Período**: Data de início não pode ser maior que data fim
2. **Limite de Movimentações**: Exportação limitada a quantidade configurada via Feature Toggle (padrão: 500 movimentações)
3. **Categorização de Transações**: Movimentações são categorizadas automaticamente com base no código de transação (PIX, TED, TEF, Boletos, Tarifas, etc.)
4. **Ajuste de Timezone**: Datas são ajustadas (+3h) para compensar diferenças de fuso horário entre aplicação e Elasticsearch
5. **Cálculo de Saldos**: Sistema calcula saldo antes e após cada lançamento, além de totais de entradas e saídas
6. **Histórico de Saldo Sintético**: Cria registros sintéticos de saldo para datas que possuem movimentações mas não têm histórico de saldo registrado
7. **Filtros Avançados**: Suporta filtros por valor, data, tipo débito/crédito, NSU, número documento, código transação, etc.
8. **Validação de Filtros**: Cada tipo de filtro possui estratégia de validação específica (Strategy Pattern)
9. **Destaque de Resultados**: Permite destacar termos de busca nos resultados (highlight do Elasticsearch)
10. **Paginação**: Suporta paginação de resultados com controle de página atual e próxima página

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **ConsultaExtrato**: Agregador de parâmetros de consulta (conta, período, filtros, paginação)
- **Extrato**: Contém lista de `HistoricoSaldo` e lista de `Movimentacao`
- **HistoricoSaldo**: Representa saldo diário de uma conta (1:N com Extrato)
- **Movimentacao**: Representa uma transação financeira (1:N com Extrato)
- **MensagemFilaExportarExtrato**: Mensagem enviada para fila Pub/Sub contendo extrato completo
- **PesquisaElasticsearchRequest**: Parâmetros de pesquisa no Elasticsearch
- **PesquisaElasticsearchResponse**: Resultado de pesquisa com movimentações e paginação

**Relacionamentos:**
- Um `Extrato` possui múltiplos `HistoricoSaldo` (um por dia)
- Um `Extrato` possui múltiplas `Movimentacao` (transações do período)
- Uma `ConsultaExtrato` pode conter uma `PesquisaElasticsearchRequest` (filtros avançados)
- Uma `MensagemFilaExportarExtrato` encapsula um `Extrato` completo para exportação

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| `DBCONTACORRENTE..TbHistoricoMovimento` | Tabela | SELECT | Histórico de movimentações da conta corrente |
| `DBCONTACORRENTE..TbMovimentoDia` | Tabela | SELECT | Movimentações do dia atual |
| `DBCONTACORRENTE.dbo.TbHistoricoSaldo` | Tabela | SELECT | Histórico de saldos diários |
| `DBCONTACORRENTE.dbo.TbConta` | Tabela | SELECT | Dados cadastrais da conta (usado em JOIN) |
| `movimentacoes` (Elasticsearch) | Índice | SEARCH | Índice Elasticsearch com movimentações indexadas para busca otimizada |

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `logback-spring.xml` | Leitura | Configuração Spring Boot | Arquivo de configuração de logs (JSON format) |
| `application.yml` | Leitura | Configuração Spring Boot | Arquivo de configuração da aplicação |
| `consultarMovimentacoes.sql` | Leitura | `ConsultaMovimentacoesRepositoryImpl` | Query SQL para buscar movimentações |
| `consultarQuantidadeMovimentacoes.sql` | Leitura | `ConsultaMovimentacoesRepositoryImpl` | Query SQL para contar movimentações |
| `consultaHistoricoSaldo.sql` | Leitura | `HistoricoSaldoRepositoryImpl` | Query SQL para buscar histórico de saldos |
| `sboot-ccbd-base-atom-extrato.yaml` | Leitura | Swagger Codegen | Especificação OpenAPI para geração de código |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Responsável | Descrição |
|--------------|------------|-------------------|-----------|
| `business-ccbd-base-exportar-extrato` | Google Cloud Pub/Sub | `EnviarMensagemTopicoExportarExtratoRepositoryImpl` | Fila para processamento assíncrono de exportação de extratos em PDF/OFX |

**Atributos da mensagem:**
- `routing_key`: `ccbd.exportar.extrato`
- Payload: JSON contendo dados completos do extrato, informações do cliente e formatos solicitados

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **Elasticsearch** | Banco NoSQL | Consulta otimizada de movimentações com suporte a busca textual, filtros avançados e agregações |
| **Sybase (DBCONTACORRENTE)** | Banco Relacional | Consulta de movimentações históricas e do dia, além de histórico de saldos |
| **Google Cloud Pub/Sub** | Mensageria | Publicação de mensagens para processamento assíncrono de exportação de extratos |
| **ConfigCat** | Feature Toggle | Gerenciamento de configurações dinâmicas (ex: limite de movimentações para exportação) |
| **OAuth2** | Autenticação | Autenticação e autorização via JWT (integração com API Gateway) |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 8/10

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo princípios de Clean Architecture (separação em camadas: domain, application)
- Uso adequado de padrões de projeto (Strategy Pattern para validação de filtros)
- Boa cobertura de testes unitários e separação clara entre testes unit/integration/functional
- Uso de bibliotecas modernas e adequadas (MapStruct, Lombok, JDBI)
- Tratamento de exceções centralizado e bem organizado
- Configuração externalizada e suporte a múltiplos ambientes
- Documentação OpenAPI completa
- Uso de Feature Toggles para configurações dinâmicas
- Logs estruturados em JSON
- Métricas e observabilidade bem implementadas (Prometheus/Grafana)

**Pontos de Melhoria:**
- Algumas classes com responsabilidades múltiplas (ex: `SearchSourceRequestBuilder` poderia ser dividida)
- Uso de "magic numbers" em alguns locais (ex: timeout de 15 segundos hardcoded)
- Alguns métodos longos que poderiam ser refatorados (ex: `toMovimentacao` nos mappers)
- Falta de documentação JavaDoc em algumas classes importantes
- Alguns testes poderiam ter melhor nomenclatura e organização
- Uso de `AT ISOLATION 0` nas queries SQL (pode ter implicações de consistência)

---

## 14. Observações Relevantes

1. **Ajuste de Timezone**: O sistema adiciona 3 horas às datas de consulta para compensar diferenças de fuso horário entre a aplicação e o Elasticsearch (BCI-672)

2. **Dual Source**: As movimentações são consultadas tanto em `TbHistoricoMovimento` (histórico) quanto em `TbMovimentoDia` (dia atual) através de UNION ALL

3. **Categorização Inteligente**: O sistema possui um enum extenso (`CategoriaTransacao`) que mapeia mais de 100 códigos de transação para categorias amigáveis (PIX, TED, Boletos, etc.)

4. **Saldos Sintéticos**: Para datas que possuem movimentações mas não têm registro de saldo, o sistema cria registros sintéticos com flag `ignorarSaldo=true`

5. **Segurança**: Integração com módulo de segurança BV (`sboot-arqt-security`) para autenticação JWT e controle de acesso

6. **Observabilidade**: Dashboard Grafana pré-configurado com métricas de JVM, HTTP, HikariCP e logs

7. **Multi-ambiente**: Suporte completo para ambientes local, des, uat e prd com configurações específicas

8. **Validação Robusta**: Cada tipo de filtro possui estratégia de validação específica implementada via Strategy Pattern

9. **Performance**: Uso de índices Elasticsearch para consultas rápidas e paginação eficiente (max 10.000 registros por consulta)

10. **Exportação Assíncrona**: Exportações são processadas de forma assíncrona via Pub/Sub, evitando timeouts em grandes volumes

11. **Feature Toggle**: Limite de movimentações para exportação é configurável dinamicamente via ConfigCat (padrão: 500)

12. **Destaque de Resultados**: Suporta highlight de termos de busca nos campos `nm_transacao_reduzida` e `ds_complemento_operacao`