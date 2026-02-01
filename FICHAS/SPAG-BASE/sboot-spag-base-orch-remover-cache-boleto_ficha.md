# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema orquestrador responsável por remover cache de boletos no contexto de baixa de boletos. O sistema consome mensagens de filas do Google Cloud Pub/Sub (solicitações de baixa e contingência), busca informações do boleto em sistemas externos (SPAG e PGFT), valida o código de barras e solicita a remoção do cache através de um serviço de consulta de boletos.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `RemoverCacheBoletoService` | Serviço de domínio que orquestra o fluxo de remoção de cache através do Apache Camel |
| `RemoverCacheBoletoRouter` | Define a rota Camel com os processadores e integrações necessários |
| `RemoverCacheBoletoSubscriber` | Subscriber que consome mensagens das filas Pub/Sub |
| `BoletoRepositoryImpl` | Implementação de repositório para buscar dados de boleto no SPAG e PGFT |
| `RemoverCacheBoletoRepositoryImpl` | Implementação de repositório para chamar o serviço de remoção de cache |
| `RemoverCacheBoletoInitProcessor` | Processador Camel que inicializa o fluxo extraindo dados da mensagem |
| `BuscarBoletoProcessor` | Processador Camel que verifica se o boleto foi encontrado |
| `VerificaCodBarrasProcessor` | Processador Camel que valida e formata o código de barras |
| `AppProperties` | Classe de configuração com propriedades da aplicação |
| `CamelContextWrapper` | Wrapper para gerenciar o contexto do Apache Camel |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.x** (framework base)
- **Apache Camel 3.22.4** (orquestração e integração)
- **Google Cloud Pub/Sub** (mensageria)
- **Spring Cloud GCP 3.9.11** (integração com GCP)
- **Micrometer/Prometheus** (métricas)
- **Swagger/OpenAPI 3.0.0** (documentação de API)
- **Logback** (logging)
- **HikariCP** (pool de conexões)
- **RestTemplate** (cliente HTTP)
- **JUnit 5 + Mockito** (testes)
- **Maven** (build)
- **Docker** (containerização)
- **Grafana + Prometheus** (observabilidade)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| N/A | N/A | `RemoverCacheBoletoController` | Controlador vazio, sem endpoints REST implementados |

**Observação:** O sistema funciona primariamente através de consumo de mensagens de filas Pub/Sub, não expondo endpoints REST para operações de negócio.

---

## 5. Principais Regras de Negócio

1. **Busca de Boleto**: Tenta buscar informações do boleto primeiro no SPAG (sistema de pagamento). Se não encontrar, busca no PGFT (sistema de registro de boleto).

2. **Validação de Código de Barras**: Valida se o código de barras/linha digitável existe e não está vazio. Se a linha digitável tiver mais de 44 caracteres, realiza conversão para código de barras padrão.

3. **Remoção de Cache**: Após obter e validar o código de barras, solicita a remoção do cache através do serviço de consulta de boletos.

4. **Tratamento de Erros**: Captura exceções específicas (`RemoverCacheBoletoException`) e retorna mensagem de erro genérica em caso de falha não crítica.

5. **Processamento Assíncrono**: Consome mensagens de duas filas distintas (solicitação e contingência) e realiza ACK manual após processamento.

---

## 6. Relação entre Entidades

**Entidades principais:**

- **Mensagem**: Representa a mensagem recebida da fila Pub/Sub
  - Atributos: `codMsg`, `numCtrlPart`, `ispbPartRecbdrPrincipal`
  
- **DadosBoleto**: Representa os dados do boleto obtidos dos sistemas externos
  - Atributos: `valor`, `dataMovimento`, `dataLancamento`, `status`, `nuCodigoBarraDigitacao`, `flBoletoBaixa`

**Relacionamento:**
- Uma `Mensagem` contém o `numCtrlPart` (código de lançamento) que é usado para buscar um `DadosBoleto`
- O `DadosBoleto` contém o `nuCodigoBarraDigitacao` necessário para remover o cache

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
| logback-spring.xml | leitura | `/usr/etc/log` (runtime) | Arquivo de configuração de logs |
| application.yml | leitura | `src/main/resources` | Arquivo de configuração da aplicação |

---

## 10. Filas Lidas

- **business-spag-base-baixa-boleto-remover-cache-sub**: Fila principal para solicitações de remoção de cache de boleto após baixa
- **business-spag-base-contingencia-baixa-boleto-remover-cache-sub**: Fila de contingência para solicitações de remoção de cache

Ambas as filas são do Google Cloud Pub/Sub e são consumidas através do Spring Cloud GCP.

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| SPAG (sboot-spag-base-atom-pagamento) | REST API | Busca detalhes de pagamento através do endpoint `/v1/pagamento/detalhado/{cdLancamento}` |
| PGFT (sboot-spag-base-atom-registra-boleto) | REST API | Busca dados de boleto através do endpoint `/v1/obter-dados-boleto/{cdLancamentoPgft}` |
| Consulta Boleto (springboot-spag-base-consulta-boleto) | REST API | Remove cache de boleto através do endpoint `/v1/boleto/removerCacheBoleto/{nuCodBarras}` |
| Google Cloud Pub/Sub | Mensageria | Consome mensagens de duas filas (solicitação e contingência) |
| API Gateway BV | OAuth2 | Autenticação para chamadas aos serviços internos |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (domain, application)
- Uso adequado do Apache Camel para orquestração de fluxos
- Testes unitários presentes para as principais classes
- Configuração adequada de observabilidade (Prometheus, Grafana)
- Uso de padrões de projeto (Repository, Service)
- Documentação OpenAPI presente

**Pontos de Melhoria:**
- Tratamento de exceções genérico em alguns pontos (catch de `Exception`)
- Logs com informações sensíveis (códigos de barras) sem sanitização consistente
- Falta de validação mais robusta de entrada de dados
- Alguns métodos com múltiplas responsabilidades (ex: `receberComandoMessage`)
- Configurações de timeout e retry não explicitamente definidas
- Falta de circuit breaker para chamadas externas
- Código de testes com alguns `lenient()` desnecessários
- Ausência de testes de integração mais abrangentes

---

## 14. Observações Relevantes

1. **Autenticação**: O sistema utiliza OAuth2 através do API Gateway do Banco Votorantim para autenticar chamadas aos serviços internos.

2. **Ambientes**: Suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas por ambiente.

3. **Monitoramento**: Possui dashboards Grafana pré-configurados para monitoramento de métricas JVM, HTTP, HikariCP e logs.

4. **Contingência**: Possui fila separada para processamento de contingência, garantindo resiliência.

5. **ACK Manual**: Utiliza ACK manual nas mensagens do Pub/Sub, garantindo que mensagens só sejam confirmadas após processamento completo.

6. **Timeout**: Configuração de timeout de 30 segundos para chamadas ao serviço de consulta de boletos.

7. **Credenciais**: Utiliza cofre de senhas para armazenamento seguro de credenciais (client_id, client_secret, passwords).

8. **Plataforma**: Projetado para execução em Google Cloud Platform (GCP) com Kubernetes.