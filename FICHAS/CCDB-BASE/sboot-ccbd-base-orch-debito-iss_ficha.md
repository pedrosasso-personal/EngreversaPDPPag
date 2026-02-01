---
## Ficha Técnica do Sistema

### 1. Descrição Geral
Sistema orquestrador responsável por processar transações de débito para cálculo e registro de ISS (Imposto Sobre Serviços). O sistema consome mensagens de uma fila RabbitMQ, enriquece os dados consultando múltiplos serviços (dados cadastrais, endereços, cartões), valida as informações e persiste o registro de ISS para posterior geração de arquivo de cobrança municipal.

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `DebitoIssListener` | Listener RabbitMQ que recebe mensagens de débito ISS e aciona o processamento |
| `DebitoIssService` | Interface de serviço para orquestração do fluxo de processamento |
| `DebitoIssServiceImpl` | Implementação do serviço utilizando Apache Camel para orquestração |
| `DebitoIssRouter` | Roteador Apache Camel que define o fluxo completo de processamento |
| `IssRepositoryImpl` | Repositório para consulta e persistência de dados de transação ISS |
| `GlobalRepositoryImpl` | Repositório para consulta de dados cadastrais de pessoa e conta |
| `EnderecoRepositoryImpl` | Repositório para consulta de endereços por CEP |
| `CartRepositoryImpl` | Repositório para consulta de dados de cartão |
| `DebitoIssRepositoryImpl` | Repositório para envio de mensagens de exceção para fila de tratamento |
| Processors (diversos) | Processadores Camel para transformação e enriquecimento de dados |
| Mappers (diversos) | Classes utilitárias para conversão entre objetos de domínio e DTOs |

### 3. Tecnologias Utilizadas
- **Framework**: Spring Boot 2.x
- **Orquestração**: Apache Camel 3.0.1
- **Mensageria**: RabbitMQ com Spring AMQP
- **Cliente HTTP**: RestTemplate (Spring)
- **Documentação API**: Swagger/OpenAPI 2.9.2
- **Observabilidade**: Spring Actuator, Micrometer, Prometheus
- **Validação**: Bean Validation (javax.validation)
- **Build**: Maven
- **Java**: JDK 11
- **Containerização**: Docker
- **Infraestrutura**: Kubernetes/OpenShift (Google Cloud Platform)
- **Auditoria**: Biblioteca BV (springboot-arqt-base-trilha-auditoria-web)

### 4. Principais Endpoints REST
Não se aplica. Este é um sistema orquestrador orientado a eventos (event-driven) que consome mensagens de filas RabbitMQ e não expõe endpoints REST próprios.

### 5. Principais Regras de Negócio
1. **Enriquecimento de Dados**: Consulta dados complementares de múltiplas fontes (Global, Endereço, Cartão) para compor o registro completo de ISS
2. **Validação de Campos Obrigatórios**: Valida presença de todos os campos obrigatórios antes de persistir o registro ISS
3. **Tratamento de Exceções com DLQ**: Implementa mecanismo de Dead Letter Queue com até 2 tentativas de reprocessamento antes de enviar para fila de exceção
4. **Determinação de Tipo de Transação**: Identifica se é débito ou crédito baseado no código de tipo de transação (0100/0200 = débito, 0400/0420 = crédito)
5. **Determinação de Tipo de Documento**: Identifica CPF ou CNPJ baseado no tamanho do documento (11 dígitos = CPF, maior = CNPJ)
6. **Mapeamento de Endereços**: Busca endereços tanto do cliente quanto do estabelecimento comercial para composição do registro ISS
7. **Integração com Dados de Cartão**: Recupera informações de tipo e bandeira do cartão utilizado na transação

### 6. Relação entre Entidades

**Entidades Principais:**
- `DebitoIss`: Mensagem recebida da fila contendo dados básicos da transação
- `Transacao`: Dados completos da transação recuperados do serviço ISS
- `Conta`: Dados da conta corrente do cliente
- `Pessoa`: Dados cadastrais do cliente
- `Endereco`: Dados de endereço (cliente e estabelecimento)
- `Cartao`: Dados do cartão utilizado na transação
- `Iss`: Entidade completa com todos os dados para registro de ISS

**Relacionamentos:**
- DebitoIss → Transacao (1:1) - via número de protocolo
- Transacao → Conta (1:1) - via número da conta
- Conta → Pessoa (1:1) - via CPF/CNPJ
- Pessoa → Endereco (1:1) - via CEP do cliente
- Transacao → Endereco (1:1) - via CEP do estabelecimento
- Pessoa → Cartao (1:1) - via CPF/CNPJ
- Todos convergem para → Iss (entidade final)

### 7. Estruturas de Banco de Dados Lidas
Não se aplica. O sistema não acessa diretamente banco de dados, apenas consome APIs REST de outros microserviços.

### 8. Estruturas de Banco de Dados Atualizadas
Não se aplica. O sistema não atualiza diretamente banco de dados, apenas invoca APIs REST de outros microserviços para persistência.

### 9. Arquivos Lidos e Gravados
Não se aplica. O sistema não realiza leitura ou gravação direta de arquivos.

### 10. Filas Lidas

| Nome da Fila | Descrição |
|--------------|-----------|
| `events.business.CCBD-BASE.debitoIss` | Fila principal que recebe mensagens de transações de débito para processamento de ISS |
| `events.business.CCBD-BASE.reenvioDebitoIss` | Fila de reenvio com TTL de 30 segundos para reprocessamento de mensagens que falharam |

### 11. Filas Geradas

| Nome da Fila | Descrição |
|--------------|-----------|
| `events.business.CCBD-BASE.trataErroDebitoIss` | Fila para tratamento de exceções quando o processamento falha após todas as tentativas de reprocessamento |

**Exchanges utilizados:**
- `events.ex.business.ccbd.debitoIss` (direct)
- `events.ex.business.ccbd.debitoIssDLQ` (fanout)
- `events.ex.business.ccbd.reenvioDebitoIss` (fanout)
- `events.ex.business.ccbd.trataErroDebitoIss` (direct)

### 12. Integrações Externas

| Sistema/API | Descrição |
|-------------|-----------|
| `sboot-ccbd-base-atom-debito-iss` | API para consulta de transações ISS por protocolo e persistência de registros ISS |
| `sboot-glob-base-atom-cliente-dados-cadastrais` | API para consulta de dados cadastrais de pessoa (por CPF/CNPJ) e conta corrente |
| `sboot-vucl-base-atom-endereco` | API para consulta de endereços por CEP |
| `sboot-cart-base-atom-cliente` | API para consulta de dados de cartão priorizado por CPF/CNPJ |
| **Gateway OAuth** | Serviço de autenticação para obtenção de tokens JWT para chamadas às APIs |

Todas as integrações utilizam RestTemplate com autenticação OAuth2 via `GatewayOAuthService`.

### 13. Avaliação da Qualidade do Código

**Nota:** 8/10

**Justificativa:**
- **Pontos Positivos:**
  - Arquitetura bem estruturada seguindo padrões hexagonais (ports/adapters)
  - Separação clara de responsabilidades em módulos (common, domain, application)
  - Uso adequado de Apache Camel para orquestração de fluxos complexos
  - Implementação robusta de tratamento de erros com DLQ e reprocessamento
  - Boa cobertura de testes unitários e de integração
  - Uso de mappers para isolamento de transformações
  - Configuração externalizada e adequada para múltiplos ambientes
  - Observabilidade bem implementada (Actuator, Prometheus, Grafana)
  
- **Pontos de Melhoria:**
  - Alguns processadores Camel poderiam ter lógica mais simplificada
  - Validações poderiam ser mais granulares com mensagens de erro específicas
  - Falta documentação inline em alguns pontos críticos do fluxo
  - Alguns métodos de mapeamento poderiam usar bibliotecas como MapStruct para reduzir código boilerplate
  - Configuração de timeouts e retry policies poderia estar mais explícita

### 14. Observações Relevantes

1. **Padrão de Reprocessamento**: O sistema implementa um mecanismo sofisticado de DLQ com contagem de tentativas (máximo 2) antes de enviar para fila de exceção definitiva.

2. **Orquestração com Camel**: O uso de Apache Camel permite uma orquestração declarativa e visual do fluxo de processamento, facilitando manutenção e evolução.

3. **Segurança**: Todas as chamadas externas são autenticadas via OAuth2 com tokens JWT obtidos dinamicamente.

4. **Ambientes**: O sistema está preparado para múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas.

5. **Monitoramento**: Infraestrutura completa de observabilidade com Prometheus, Grafana e dashboards pré-configurados.

6. **Containerização**: Projeto totalmente containerizado com Dockerfile otimizado usando OpenJ9 para melhor performance de memória.

7. **CI/CD**: Integração com Jenkins configurada via arquivo `jenkins.properties` para pipeline automatizado.

8. **Arquitetura de Testes**: Estrutura bem organizada com separação de testes unitários, integração e funcionais em diretórios distintos.

9. **Validação Arquitetural**: Suporte a ArchUnit para validação de regras arquiteturais via profile Maven.

10. **Dependências BV**: Utiliza bibliotecas corporativas do Banco Votorantim para auditoria, tratamento de erros e padrões arquiteturais.