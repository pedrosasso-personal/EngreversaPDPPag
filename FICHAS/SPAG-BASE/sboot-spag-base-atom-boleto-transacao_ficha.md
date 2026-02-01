# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-spag-base-atom-boleto-transacao** é um serviço atômico desenvolvido em Java com Spring Boot, responsável por gerenciar e registrar transações relacionadas ao fluxo de pagamento de boletos. O sistema mantém um histórico completo de eventos (estado atual) de cada transação de pagamento, desde a solicitação inicial até a conclusão ou interrupção do processo, permitindo rastreabilidade e auditoria de todas as etapas do ciclo de vida de um pagamento de boleto.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal que inicializa a aplicação Spring Boot com segurança OAuth2 |
| `BoletoTransacaoController` | Controlador REST que expõe endpoints para registro de eventos de transações de boleto |
| `BoletoTransacaoService` | Serviço de domínio que implementa as regras de negócio para registro e consulta de transações |
| `BoletoTransacaoRepository` | Interface de repositório que define operações de persistência |
| `BoletoTransacaoRepositoryImpl` | Implementação do repositório usando JDBI para acesso ao banco SQL Server |
| `BoletoTransacaoConfiguration` | Configuração de beans do Spring (ObjectMapper, JDBI, repositórios, serviços) |
| `OpenApiConfiguration` | Configuração do Swagger/OpenAPI para documentação da API |
| `BoletoTransacaoExceptionHandler` | Tratador global de exceções da aplicação |
| `EventoBoletoTransacao` | Entidade de domínio que representa um evento de transação de boleto |
| `EstadoAtual` | Entidade que representa o estado consolidado atual de uma transação |
| `PagamentoSolicitado` | Entidade que representa uma solicitação de pagamento |
| `BoletoValidado` | Entidade que representa um boleto validado |
| `PagamentoInterrompido` | Entidade que representa uma interrupção no pagamento |
| `BoletoTransacaoMapper` | Mapper JDBI para conversão de ResultSet em objetos de domínio |
| Mappers de Presentation | Classes MapStruct para conversão entre representations e domínio |

---

## 3. Tecnologias Utilizadas

- **Java 11** - Linguagem de programação
- **Spring Boot 2.x** - Framework principal
- **Spring Security OAuth2** - Autenticação e autorização via JWT
- **JDBI 3.9.1** - Framework de acesso a banco de dados
- **SQL Server** (Microsoft SQL Server JDBC Driver 7.4.0) - Banco de dados relacional
- **MapStruct 1.3.1** - Mapeamento de objetos
- **Lombok** - Redução de código boilerplate
- **Swagger/Springfox 2.9.2** - Documentação de API
- **Jackson** - Serialização/deserialização JSON
- **Micrometer/Prometheus** - Métricas e monitoramento
- **Logback** - Framework de logging
- **JUnit 5** - Testes unitários
- **Mockito** - Mocks para testes
- **Rest Assured** - Testes de API REST
- **Pact** - Testes de contrato
- **H2 Database** - Banco em memória para testes
- **Maven** - Gerenciamento de dependências e build
- **Docker** - Containerização
- **Grafana/Prometheus** - Observabilidade

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/api/boleto-transacao/pagamento-solicitado` | `BoletoTransacaoController` | Registra uma transação de pagamento solicitado |
| POST | `/v1/api/boleto-transacao/sucesso` | `BoletoTransacaoController` | Registra uma transação de sucesso |
| POST | `/v1/api/boleto-transacao/boleto-validado` | `BoletoTransacaoController` | Registra uma transação de boleto validado |
| POST | `/v1/api/boleto-transacao/pagamento-interrompido` | `BoletoTransacaoController` | Registra uma interrupção de pagamento (erro negocial ou técnico) |
| GET | `/v1/api/boleto-transacao/estado-atual` | `BoletoTransacaoController` | Recupera o estado atual de um pagamento pelo código de lançamento |

---

## 5. Principais Regras de Negócio

1. **Registro de Eventos de Transação**: Cada evento no ciclo de vida de um pagamento de boleto é registrado com tipo de evento, data/hora, payload JSON e código de lançamento
2. **Máquina de Estados**: O sistema gerencia diferentes tipos de eventos (30 tipos) que representam estados do fluxo de pagamento (solicitado, validado, rejeitado, falhou, etc.)
3. **Rastreabilidade Completa**: Mantém histórico completo de todas as transações por código de lançamento
4. **Estado Atual Consolidado**: Consolida o histórico de eventos para retornar o estado atual de uma transação, incluindo último evento e contagem de tentativas
5. **Tratamento de Erros**: Diferencia erros de negócio (validações, rejeições) de erros técnicos (falhas de sistema)
6. **Suporte a Múltiplos Tipos de Cliente**: Diferencia transações de clientes FINTECH e CASH
7. **Validação de Boleto**: Suporta validação via CIP ou contingência
8. **Auditoria**: Registra login/usuário responsável por cada operação

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **EventoBoletoTransacao**: Representa um evento individual no histórico de uma transação
  - Atributos: id, codigoLancamento, tipoEvento, dataHoraTransacao, evento (JSON), flagAtivo, dsLogin

- **EstadoAtual**: Agregação que representa o estado consolidado de uma transação
  - Contém: codigoLancamento, pagamentoSolicitado, boletoValidado, erroNegocio, erroTecnico, ultimoEvento

- **UltimoEvento**: Representa o último evento processado
  - Atributos: tipo, tentativas, dataHoraTransacao

**Payloads (armazenados como JSON):**
- PagamentoSolicitadoPayload: dados da solicitação (cliente, valor, favorecido, remetente, boleto)
- BoletoValidadoPayload: dados do boleto validado (tipo validação, boleto calculado)
- ErroNegocioPayload: lista de erros de negócio
- ErroTecnicoPayload: descrição de erro técnico

**Relacionamentos:**
- Um código de lançamento pode ter múltiplos eventos (1:N)
- Cada evento está associado a um tipo de evento da tabela TbTipoEvento (N:1)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbEventoBoletoTransacao | Tabela | SELECT | Consulta histórico de eventos de transações de boleto por código de lançamento |
| TbTipoEvento | Tabela | SELECT | Consulta tipos de eventos (implícito via foreign key) |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbEventoBoletoTransacao | Tabela | INSERT | Insere novos eventos de transação de boleto com payload JSON |
| TbTipoEvento | Tabela | INSERT | Carga inicial de tipos de eventos (via data.sql) |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | Spring Boot | Configurações da aplicação (datasource, OAuth2, logging) |
| logback-spring.xml | Leitura | Logback | Configuração de logs em formato JSON |
| schema.sql | Leitura | Spring Boot | Script de criação de estrutura de banco (H2 para testes) |
| data.sql | Leitura | Spring Boot | Script de carga inicial de tipos de eventos |
| sboot-spag-base-atom-boleto-transacao.yaml | Leitura | Swagger Codegen | Especificação OpenAPI para geração de interfaces |
| registrarTransacao.sql | Leitura | JDBI | Query SQL para inserção de eventos |
| transacoes.sql | Leitura | JDBI | Query SQL para consulta de eventos |

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
| API Gateway OAuth2 | Autenticação | Validação de tokens JWT via JWK endpoint (apigateway.bvnet.bv) |
| SQL Server (DBSPAG) | Banco de Dados | Persistência de eventos de transações |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo princípios de Clean Architecture (separação em módulos: common, domain, application)
- Uso adequado de padrões de projeto (Repository, Service, Mapper)
- Boa cobertura de testes (unitários, integração, funcionais)
- Configuração adequada de segurança OAuth2
- Uso de frameworks modernos e bem estabelecidos
- Documentação via Swagger/OpenAPI
- Observabilidade com Prometheus/Grafana
- Uso de Lombok para reduzir boilerplate
- Separação clara entre camadas de apresentação, domínio e infraestrutura

**Pontos de Melhoria:**
- Algumas classes de teste com mocks excessivos que poderiam ser simplificados
- Falta de validações mais robustas em alguns payloads
- Tratamento de exceções genérico (captura Exception ao invés de exceções específicas)
- Poderia ter mais documentação inline (JavaDoc) nas classes de domínio
- Alguns métodos no Service poderiam ser quebrados em métodos menores para melhor legibilidade
- Configurações hardcoded em alguns lugares (ex: DS_LOGIN como constante)

---

## 14. Observações Relevantes

1. **Arquitetura Modular**: O projeto está organizado em 3 módulos Maven (common, domain, application), seguindo boas práticas de separação de responsabilidades

2. **Versionamento de API**: Utiliza versionamento na URL (`/v1/api/`)

3. **Ambientes**: Suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas

4. **Containerização**: Possui Dockerfile para deploy em containers (OpenShift/Kubernetes)

5. **Infraestrutura como Código**: Possui arquivo `infra.yml` para provisionamento automatizado

6. **Métricas**: Configuração completa de métricas com Prometheus e dashboards Grafana

7. **Auditoria**: Integração com biblioteca de auditoria do Banco Votorantim

8. **Testes de Arquitetura**: Possui profile Maven para validação de regras arquiteturais com ArchUnit

9. **Geração de Código**: Utiliza Swagger Codegen para gerar interfaces a partir da especificação OpenAPI

10. **Banco de Dados**: Utiliza SQL Server em produção e H2 em memória para testes

11. **Padrão de Nomenclatura**: Segue convenções do Banco Votorantim (prefixo `sboot-spag-base-atom-`)

12. **Pipeline CI/CD**: Possui configuração para Jenkins (`jenkins.properties`)

13. **Tipos de Evento**: Sistema suporta 30 tipos diferentes de eventos no ciclo de vida de pagamento de boleto

14. **Payload JSON**: Eventos são armazenados com payload completo em formato JSON para flexibilidade e auditoria