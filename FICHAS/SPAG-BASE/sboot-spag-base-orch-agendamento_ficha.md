# Ficha Técnica do Sistema

---

## 1. Descrição Geral

O **sboot-spag-base-orch-agendamento** é um serviço stateless desenvolvido em Spring Boot que gerencia o processamento de agendamentos de lançamentos financeiros (pagamentos). O sistema consulta lançamentos agendados, atualiza seus status e os envia para processamento em diferentes esteiras (boletos, transferências ou sistema legado WAS), de acordo com o tipo de liquidação. Utiliza Apache Camel para orquestração de fluxos e integra-se com múltiplos serviços via REST.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot, ponto de entrada da aplicação |
| `AgendamentoController` | Controller REST que expõe endpoint para obter agendamentos |
| `AgendamentoService` | Serviço de domínio que orquestra o fluxo de agendamentos via Camel |
| `EnviarEsteiraService` | Serviço que decide e executa o envio para a esteira apropriada (boleto, transferência ou WAS) |
| `AgendamentoRouter` | Define as rotas Camel para processamento de agendamentos |
| `PagamentoRepositoryImpl` | Implementação de repositório para comunicação com serviço de pagamentos |
| `BoletoRepositoryImpl` | Implementação de repositório para processamento de boletos |
| `TransferenciaRepositoryImpl` | Implementação de repositório para processamento de transferências |
| `WasRepositoryImpl` | Implementação de repositório para envio ao sistema legado WAS |
| `AgendamentoMapper` | Mapper para conversão entre objetos de domínio e representação |
| `ExceptionControllerHandler` | Tratamento centralizado de exceções |

---

## 3. Tecnologias Utilizadas

- **Spring Boot** (framework principal)
- **Spring MVC** (controllers REST)
- **Spring Security OAuth2** (autenticação e autorização)
- **Apache Camel 3.4.1** (orquestração de fluxos)
- **RestTemplate** (cliente HTTP)
- **Swagger/OpenAPI 2.0** (documentação de API)
- **Springfox** (geração de documentação Swagger)
- **Lombok** (redução de boilerplate)
- **Logback** (logging)
- **Micrometer/Prometheus** (métricas)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Kubernetes/OpenShift** (orquestração de containers)
- **GSON** (serialização JSON)
- **JUnit 5** (testes unitários)
- **Mockito** (mocks em testes)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/agendamento` | `AgendamentoController` | Obtém lançamentos agendados por data de movimento, código do banco e flag de lançamento manual |

---

## 5. Principais Regras de Negócio

1. **Consulta de Agendamentos**: Busca lançamentos agendados com base em data de movimento, código do banco remetente e flag de lançamento manual.

2. **Atualização de Status**: Após obter os agendamentos, atualiza o status dos lançamentos para "Solicitação Incluída" (status 0).

3. **Roteamento por Tipo de Liquidação**: 
   - Lançamentos com liquidação CC, CIP, STR, Saque Banco Digital ou Compras Cartões → processados como transferência manual
   - Lançamentos com liquidação Boleto → processados como pagamento de boleto manual
   - Demais tipos → enviados para o sistema legado WAS (esteira)

4. **Processamento Assíncrono**: Utiliza Apache Camel para orquestrar o fluxo de processamento de forma assíncrona e desacoplada.

5. **Autenticação via OAuth2**: Todas as chamadas a serviços externos utilizam token JWT obtido via API Gateway.

6. **Tratamento de Erros**: Erros em integrações são capturados e transformados em exceções customizadas (`ApiException`) com status HTTP apropriado.

---

## 6. Relação entre Entidades

- **Agendamento**: Representa os critérios de busca (dataMovimento, codigoBanco, flLancamentoManual)
- **Agendamentos**: Contém lista de códigos de lançamentos (cdLancamento) retornados pela consulta
- **SituacaoLancamento**: Representa a atualização de status dos lançamentos (dsLogin, lancamentos, stLancamento)
- **Pagamento**: Contém detalhes completos de um pagamento (cdLancamento, cdLiquidacao, stLancamento, etc.)
- **EnviarEsteira**: Payload para envio ao sistema WAS (idprotocolo)

**Relacionamentos**:
- Um `Agendamento` resulta em múltiplos `Agendamentos` (lista de cdLancamento)
- Cada `cdLancamento` pode ser consultado individualmente como `Pagamento`
- O `cdLiquidacao` do `Pagamento` determina o tipo de processamento

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| não se aplica | não se aplica | não se aplica | O sistema não acessa diretamente banco de dados; todas as operações são via APIs REST |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| não se aplica | não se aplica | não se aplica | O sistema não atualiza diretamente banco de dados; todas as operações são via APIs REST |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `application.yml` | leitura | Spring Boot | Arquivo de configuração da aplicação (URLs, credenciais, profiles) |
| `logback-spring.xml` | leitura | Logback | Configuração de logging (console, formato JSON) |
| Arquivos Swagger YAML | leitura | Swagger Codegen Maven Plugin | Especificações OpenAPI para geração de clientes REST |

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
| **sboot-spag-base-atom-pagamento** | API REST | Serviço de pagamentos - consulta agendamentos, atualiza situação de lançamentos, consulta dados de pagamento |
| **sboot-spag-base-orch-pagamento-boleto-srv** | API REST | Serviço de pagamento de boletos - processa pagamento manual de boletos |
| **sboot-spag-base-orch-transferencias** | API REST | Serviço de transferências - processa transferências manuais (TED/TEF/DOC) |
| **WAS (Sistema Legado)** | API REST | Sistema legado - recebe lançamentos para processamento na esteira tradicional |
| **API Gateway** | OAuth2 | Gateway de autenticação - fornece tokens JWT para autenticação nas APIs |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (application, domain, common)
- Uso adequado de padrões como Repository, Service e Mapper
- Utilização de Apache Camel para orquestração de fluxos complexos
- Tratamento centralizado de exceções
- Configuração adequada de profiles para diferentes ambientes
- Uso de Lombok para reduzir boilerplate
- Documentação via Swagger/OpenAPI
- Logs estruturados em JSON

**Pontos de Melhoria:**
- Falta de testes unitários e de integração (diretórios de teste vazios ou não enviados)
- Algumas classes com responsabilidades misturadas (ex: `PagamentoRepositoryImpl` faz chamadas HTTP diretamente)
- Uso de `RestTemplate` (considerado legado; recomenda-se `WebClient`)
- Configurações sensíveis (usuário/senha) em `application.yml` do profile local
- Falta de validação de entrada nos endpoints
- Código de sanitização de logs poderia ser mais robusto
- Ausência de circuit breakers ou retry policies para resiliência
- Comentários em código poderiam ser mais descritivos

---

## 14. Observações Relevantes

1. **Arquitetura Hexagonal**: O projeto segue princípios de arquitetura hexagonal com separação clara entre domínio (domain), aplicação (application) e infraestrutura (repositories).

2. **Multi-Módulo Maven**: Projeto organizado em três módulos: `common`, `domain` e `application`, facilitando a reutilização e manutenção.

3. **Apache Camel**: Uso extensivo de Camel para orquestração de fluxos, permitindo processamento assíncrono e desacoplado.

4. **Geração de Código**: Utiliza Swagger Codegen para gerar automaticamente clientes REST a partir de especificações OpenAPI.

5. **Segurança**: Integração com OAuth2 e JWT para autenticação e autorização.

6. **Observabilidade**: Endpoints de health check e métricas Prometheus configurados.

7. **Containerização**: Dockerfile configurado para deploy em Kubernetes/OpenShift.

8. **Feature Toggle**: Dependência de biblioteca de feature toggle presente, permitindo ativação/desativação de funcionalidades.

9. **Profiles de Ambiente**: Configurações específicas para local, des, qa, uat e prd.

10. **Logging**: Configuração de logging com formato JSON para facilitar análise em ferramentas de agregação de logs.