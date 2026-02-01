---
## Ficha Técnica do Sistema

### 1. Descrição Geral
Sistema orquestrador responsável por sensibilizar contas em operações de pagamento de boletos para parceiros Fintech. O sistema realiza três operações principais:
- Atualização de valores de pagamento de boleto de parceiros Fintech (processo assíncrono)
- Estorno de valores de pagamento de boleto de parceiros Fintech em caso de exceção (processo assíncrono)
- Estorno de valores já debitados de clientes Cash em caso de exceção (processo síncrono)

O sistema utiliza arquitetura orientada a eventos com Apache Camel para orquestração de fluxos e Google Cloud Pub/Sub para mensageria assíncrona.

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `SensibilizaContaService` | Serviço de domínio que coordena as operações de sensibilização de conta |
| `SensibilizaContaSubscriber` | Subscriber que recebe comandos via Pub/Sub e delega ao serviço |
| `ContaCorrenteImpl` | Implementação de integração com serviço de conta corrente (PGFT) |
| `PosicaoFintechImpl` | Implementação de integração com serviço de posição Fintech (SPAG) |
| `SaldoFintechImpl` | Implementação de consulta de saldo Fintech (CCBD) |
| `EventoPublisherImpl` | Publicador de eventos de retorno via Pub/Sub |
| `CamelContextWrapper` | Wrapper do contexto Apache Camel para orquestração |
| `ClienteCashEstonoRouter` | Rota Camel para estorno em conta corrente |
| `PosicaoFintechAtualizacaoRouter` | Rota Camel para atualização de posição Fintech |
| `PosicaoFintechEstornoRouter` | Rota Camel para estorno de posição Fintech |
| `ValidacaoCamaraLiquidacaoRouter` | Rota Camel para validação de câmara de liquidação |
| `CamaraLiquidacaoProcessor` | Processador que valida grade horária e data de movimento |

### 3. Tecnologias Utilizadas
- **Framework:** Spring Boot 2.x
- **Orquestração:** Apache Camel 3.0.1
- **Mensageria:** Google Cloud Pub/Sub (Spring Cloud GCP 2.0.4)
- **Integração:** Spring Integration
- **Pool de Conexões:** HikariCP
- **Documentação API:** Swagger/Springfox 2.9.2
- **Serialização:** Jackson
- **Monitoramento:** Spring Actuator + Prometheus + Grafana
- **Segurança:** OAuth2/JWT
- **Auditoria:** BV Trilha Auditoria 2.2.1
- **Build:** Maven
- **Java:** JDK 11
- **Container:** Docker (OpenJ9 Alpine)
- **Plataforma:** Google Cloud Platform (GKE)

### 4. Principais Endpoints REST
Não se aplica. O sistema não expõe endpoints REST públicos, operando exclusivamente via mensageria assíncrona (Pub/Sub).

### 5. Principais Regras de Negócio
- **Validação de Grade Horária:** Atualização de posição Fintech só é permitida dentro da grade horária da câmara de liquidação
- **Validação de Data de Movimento:** Atualização só é permitida se a data de movimento for igual à data atual
- **Consulta de Saldo Disponível:** Antes de atualizar posição Fintech, consulta o saldo disponível na conta
- **Conversão de Código de Banco:** Converte código COMPE para código interno do banco (BV SA: 413→436, Votorantim SA: 655→161)
- **Tratamento de Exceções:** Diferencia exceções de negócio (rejeitadas) de exceções técnicas (falhas)
- **Publicação de Eventos:** Publica eventos específicos para cada resultado (realizado, rejeitado, falhou)
- **Tipo de Conta:** Utiliza tipo de conta 6 (Conta Controle) para consultas de saldo
- **Sistema de Origem:** Utiliza código de sistema 4 para operações de conta corrente

### 6. Relação entre Entidades

**Entidades de Domínio:**
- `ContaCorrenteEstorno`: Contém código de lançamento para estorno em conta corrente
- `PosicaoFintechAtualizacao`: Contém dados para atualização (código lançamento, banco COMPE, agência, conta, valor, data movimento, câmara liquidação)
- `PosicaoFintechEstorno`: Contém dados para estorno (código lançamento, conta, valor)
- `CamaraLiquidacaoResponse`: Contém código liquidação e grade horária (início/fim)

**Eventos:**
- Hierarquia base: `Evento` (contém código lançamento)
  - `ErroEvento`: Evento com descrição de erro
  - `ErroNegocioEvento`: Evento com lista de erros de negócio
  - Eventos específicos de Posição Fintech (Atualização/Estorno: Realizada, Rejeitada, Falhou)
  - Eventos específicos de Conta Corrente (Estorno: Realizado, Rejeitado, Falhou)

**Relacionamentos:**
- PosicaoFintechAtualizacao → CamaraLiquidacaoResponse (composição)
- Todos os eventos herdam de Evento

### 7. Estruturas de Banco de Dados Lidas

Não se aplica. O sistema não acessa diretamente estruturas de banco de dados, realizando todas as operações via APIs REST de outros microserviços.

### 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema não atualiza diretamente estruturas de banco de dados, delegando todas as operações de escrita para outros microserviços via APIs REST.

### 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `logback-spring.xml` | Leitura | `/usr/etc/log` (ConfigMap) | Configuração de logs da aplicação |
| `application.yml` | Leitura | `src/main/resources` | Configurações da aplicação Spring Boot |
| Swagger YAML (3 arquivos) | Leitura | `src/main/resources/swagger/client` | Especificações OpenAPI para geração de clientes |

### 10. Filas Lidas

| Nome da Fila | Tecnologia | Classe Consumidora | Breve Descrição |
|--------------|-----------|-------------------|-----------------|
| `business-spag-sensibilizacao-conta-sub` | Google Cloud Pub/Sub | `SensibilizaContaSubscriber` | Recebe comandos de sensibilização de conta (atualizar/estornar posição Fintech, estornar cliente Cash) |

### 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Produtora | Breve Descrição |
|--------------|-----------|-----------------|-----------------|
| `business-spag-retorno-processo-pagamento-boleto` | Google Cloud Pub/Sub | `EventoPublisherImpl` | Publica eventos de retorno do processo de sensibilização (realizados, rejeitados, falhas) |

### 12. Integrações Externas

| Sistema Externo | Tipo | Classe Responsável | Breve Descrição |
|-----------------|------|-------------------|-----------------|
| `sboot-pgft-base-orch-pagamentos` | API REST | `ContaCorrenteImpl` | Orquestrador de pagamentos PGFT - realiza estorno de documentos em conta corrente |
| `sboot-spag-base-atom-posicao-fintech` | API REST | `PosicaoFintechImpl` | Atômico de posição Fintech - atualiza e estorna valores de posição |
| `sboot-ccbd-base-atom-saldo` | API REST | `SaldoFintechImpl` | Atômico de saldo CCBD - consulta saldo disponível em contas |
| API Gateway OAuth | OAuth2 | `GatewayOAuthService` | Serviço de autenticação para obtenção de tokens de acesso |

### 13. Avaliação da Qualidade do Código

**Nota:** 8/10

**Justificativa:**
- **Pontos Positivos:**
  - Arquitetura bem estruturada com separação clara de responsabilidades (domain, application, common)
  - Uso adequado de padrões como Ports & Adapters (Hexagonal Architecture)
  - Boa cobertura de testes unitários e de integração
  - Uso de Apache Camel para orquestração de fluxos complexos
  - Tratamento diferenciado de exceções de negócio e técnicas
  - Configuração externalizada e adequada para múltiplos ambientes
  - Uso de Lombok para redução de boilerplate
  - Documentação via Swagger
  - Monitoramento com Actuator/Prometheus

- **Pontos de Melhoria:**
  - Alguns processadores Camel poderiam ter lógica mais simplificada
  - Falta documentação JavaDoc em algumas classes críticas
  - Alguns métodos de conversão poderiam ser extraídos para classes utilitárias
  - Validações de entrada poderiam ser mais explícitas com Bean Validation
  - Alguns nomes de variáveis poderiam ser mais descritivos (ex: "sadoDisponivel" com typo)

### 14. Observações Relevantes

- **Arquitetura Assíncrona:** Sistema predominantemente orientado a eventos, com processamento assíncrono via Pub/Sub
- **Orquestração com Camel:** Uso extensivo de Apache Camel para orquestração de fluxos complexos com tratamento de exceções
- **Validações Temporais:** Implementa validações rigorosas de grade horária e data de movimento para garantir integridade das operações
- **Multi-tenant:** Suporta múltiplos bancos (BV SA e Votorantim SA) com conversão de códigos
- **Resiliência:** Implementa padrão de retry e tratamento de falhas com publicação de eventos específicos
- **Observabilidade:** Configuração completa de métricas, logs e dashboards Grafana
- **Infraestrutura como Código:** Configuração completa para deploy em Kubernetes/OpenShift via GCP
- **Segurança:** Integração com OAuth2/JWT para autenticação em APIs externas
- **Auditoria:** Integração com trilha de auditoria corporativa do BV
- **Versionamento:** Sistema versionado (0.2.0) com controle de mudanças