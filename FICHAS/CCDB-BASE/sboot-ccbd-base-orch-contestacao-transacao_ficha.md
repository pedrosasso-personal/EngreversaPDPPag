# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-ccbd-base-orch-contestacao-transacao** é um serviço orquestrador desenvolvido em Spring Boot responsável por gerenciar o ciclo de vida completo de contestações de transações PIX. O sistema permite que clientes contestem transações suspeitas de fraude, realizando validações de elegibilidade, bloqueio automático de valores, e integração com o SPAG (Sistema de Pagamentos Instantâneos) para criação de relatos de infração. O serviço também consulta o status de contestações através do MED (Mecanismo Especial de Devolução) e mantém controle sobre bloqueios de saldo nas contas envolvidas.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ContestacaoTransacaoController** | Expõe endpoints REST para criação e consulta de contestações |
| **ContestacaoTransacaoService** | Orquestra o fluxo de contestação utilizando Apache Camel |
| **ContestacaoTransacaoRouter** | Define o fluxo Camel (validação → bloqueio → relato infração) |
| **GlobalRepositoryImpl** | Consulta dados cadastrais do cliente para validação de titularidade |
| **ConsultaPagamentoRepositoryImpl** | Obtém detalhes da transação PIX a ser contestada |
| **MovimentacaoRepositoryImpl** | Realiza bloqueio/desbloqueio de saldo e consulta bloqueios existentes |
| **RelatoInfracaoRepositoryImpl** | Cria relato de infração no SPAG e consulta status via MED |
| **ConsultaTransacaoMedRepositoryImpl** | Consulta informações do Mecanismo Especial de Devolução |
| **RelatoInfracaoUtil** | Utilitário para validações de elegibilidade de contestação |
| **ConversorRetornoSPAG** | Converte erros e respostas do SPAG para formato interno |
| **ContestacaoTransacao** | Entidade de domínio representando uma contestação |
| **Questao** | Entidade representando perguntas/respostas do questionário de contestação |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.x** - Framework base da aplicação
- **Apache Camel 3.0.1** - Orquestração de fluxos e integração
- **OAuth2/JWT** - Autenticação e autorização
- **Swagger/OpenAPI** - Documentação de APIs
- **RestTemplate** - Cliente HTTP para integrações
- **Lombok** - Redução de boilerplate
- **JUnit 5** - Testes unitários
- **Mockito** - Mocks para testes
- **ArchUnit 0.19.0** - Testes de arquitetura
- **Logback** - Logging em formato JSON
- **Maven** - Gerenciamento de dependências
- **Docker/Docker Compose** - Containerização
- **Prometheus** - Métricas
- **Grafana** - Visualização de métricas
- **RabbitMQ** - Mensageria (configurado mas não utilizado no fluxo principal)
- **Java 11** - Linguagem de programação

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/banco-digital/transferencia-pix/contestacoes` | ContestacaoTransacaoController | Cria uma nova contestação de transação PIX |
| GET | `/v1/banco-digital/transferencia-pix/contestacoes/{id}` | ContestacaoTransacaoController | Consulta o status de uma contestação existente |

**Endpoints Adicionais (Actuator):**
- GET `/actuator/health` (porta 9090) - Health check
- GET `/actuator/prometheus` (porta 9090) - Métricas para Prometheus

**Documentação:**
- `/swagger-ui` (porta 8080) - Interface Swagger UI

---

## 5. Principais Regras de Negócio

1. **Elegibilidade de Contestação:**
   - Transação não pode ser do tipo saque
   - Deve estar dentro do prazo de 80 dias para transações normais
   - Deve estar dentro do prazo de 30 dias para devoluções especiais (MED)
   - Motivos específicos permitidos: FR01 (fraude) ou BE08 (coerção)

2. **Validação de Titularidade:**
   - CPF/CNPJ informado deve corresponder ao titular da conta
   - End2EndId da transação deve pertencer à conta informada

3. **Bloqueio Automático:**
   - Valor da transação é bloqueado automaticamente se a contestação for elegível
   - Falha no bloqueio (status 400) não impede continuidade, mas marca flag `blockedBefore=true`

4. **Mapeamento de Status MED:**
   - Status do MED é convertido para status interno:
     - PRE_RELATO_CRIADO (contestação criada)
     - ACATADO (contestação aceita)
     - RECUSADO (contestação negada)

5. **Situação do Relato:**
   - Baseada em questionário respondido pelo cliente
   - Tipos: ACCOUNT_TAKEOVER (invasão de conta) ou COERCION (coerção)

6. **Contestação Duplicada:**
   - Sistema valida se já existe contestação aberta para a mesma transação
   - Retorna erro se houver duplicidade

7. **Tipos de Transação Suportados:**
   - PIX transferência (efetivação - tipo "E")
   - PIX devolução especial (MED com motivo FR01)

---

## 6. Relação entre Entidades

**Entidade Principal: ContestacaoTransacao**
- `idTransacao` (String): Identificador único da transação PIX
- `codigoBanco` (String): Código do banco (BV/BVSA)
- `numeroAgencia` (String): Número da agência
- `numeroConta` (String): Número da conta
- `cpfCnpj` (String): CPF/CNPJ do titular
- `tipoConta` (String): Tipo da conta
- `status` (Enum): Status da contestação
- `valorTransacao` (BigDecimal): Valor contestado
- `dataTransacao` (LocalDateTime): Data da transação original
- `questionario` (List<Questao>): Respostas do questionário
- `tokenAuthorization` (String): Token JWT para autenticação
- `deviceDna` (String): Identificador do dispositivo
- `tipoPix` (String): Tipo de operação PIX
- `sequencialBloqueio` (String): Identificador do bloqueio de saldo
- `motivo` (String): Motivo da contestação (FR01/BE08)
- `tipoTransacao` (String): Tipo da transação (E=efetivação)
- `pixOut` (Boolean): Flag indicando PIX de saída
- `iniciadoCliente` (Boolean): Flag indicando se foi iniciado pelo cliente

**Entidade Relacionada: Questao**
- `pergunta` (String): Texto da pergunta
- `resposta` (String): Resposta fornecida pelo cliente

**Relacionamento:** ContestacaoTransacao possui uma lista de Questao (composição 1:N)

---

## 7. Estruturas de Banco de Dados Lidas

Não se aplica. O sistema não acessa diretamente estruturas de banco de dados. Todas as operações são realizadas através de integrações com APIs de outros microserviços.

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema não realiza operações diretas de escrita em banco de dados. As atualizações são realizadas através de chamadas a APIs de outros microserviços.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | Leitura | Configuração Spring Boot | Configuração de logs em formato JSON |
| application.yml | Leitura | Configuração Spring Boot | Configurações da aplicação (URLs, credenciais, profiles) |
| infra.yml | Leitura | Deploy/Infraestrutura | Configurações de infraestrutura como código (multi-platform) |
| prometheus.yml | Leitura | Prometheus | Configuração de scraping de métricas |
| grafana.ini | Leitura | Grafana | Configurações do Grafana (datasources, dashboards) |
| rabbitmq.conf | Leitura | RabbitMQ | Configurações do RabbitMQ |
| rabbitmq_definitions.json | Leitura | RabbitMQ | Definições de filas, exchanges e bindings |

---

## 10. Filas Lidas

Não se aplica. Embora o sistema tenha configuração de RabbitMQ (queue `sample-queue`, exchange `sample-exchange`), não há evidências no código analisado de consumo efetivo de mensagens de filas no fluxo principal de contestação.

---

## 11. Filas Geradas

Não se aplica. Não há evidências no código analisado de publicação de mensagens em filas no fluxo principal de contestação.

---

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| **sboot-glob-base-atom-cliente-dados-cadastrais** | API REST | Valida titularidade da conta através de CPF/CNPJ |
| **sboot-ccbd-base-atom-movimentacoes** | API REST | Realiza bloqueio/desbloqueio de saldo e consulta bloqueios existentes |
| **sboot-spag-pixx-orch-aviso** | API REST | Consulta detalhes completos do pagamento PIX (end2endId, valor, data) |
| **sboot-spag-pixx-orch-fraude-pagamento** | API REST | Cria relato de infração (InfractionReportV2) no SPAG e consulta status via MED |
| **API Geração Token JWT** (apiGerarToken) | API REST | Gera token de autenticação para comunicação com SPAG |
| **SPAG (Sistema de Pagamentos Instantâneos)** | Sistema Externo | Sistema do Banco Central para gestão de transações PIX e infrações |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- **Arquitetura Hexagonal bem definida**: Separação clara entre domain, application, port e infrastructure
- **Uso adequado de padrões de projeto**: Builder, UtilityClass, Mappers dedicados
- **Orquestração com Apache Camel**: Facilita manutenção de fluxos complexos
- **Exception handling centralizado**: Tratamento consistente de erros
- **Testes unitários presentes**: Cobertura com JUnit 5 e Mockito
- **Configurações externalizadas**: Facilita deploy em diferentes ambientes
- **Observabilidade**: Integração com Prometheus/Grafana para métricas
- **Documentação**: Swagger para APIs, README com informações relevantes
- **Uso de Lombok**: Reduz boilerplate significativamente

**Pontos de Melhoria:**
- **Testes incompletos**: ContestacaoTransacaoServiceTest está vazio
- **Acoplamento com APIs externas**: Muitas dependências de serviços externos podem dificultar testes
- **Tratamento de falhas de bloqueio**: Continua fluxo mesmo com falha (status 400), pode gerar inconsistências
- **Documentação técnica**: Poderia ter mais comentários em lógicas complexas de negócio
- **Configuração RabbitMQ não utilizada**: Infraestrutura configurada mas não usada no fluxo principal

O código demonstra maturidade técnica e boas práticas de engenharia de software, com estrutura bem organizada e separação adequada de responsabilidades. As melhorias sugeridas são incrementais e não comprometem a qualidade geral do sistema.

---

## 14. Observações Relevantes

1. **Enumerações Importantes:**
   - Mapeamento de bancos (BV/BVSA)
   - Status de contestação (PRE_RELATO_CRIADO, ACATADO, RECUSADO)
   - Motivos de devolução (FR01 - fraude, BE08 - coerção)

2. **Conversão de Erros SPAG:**
   - Classe `ConversorRetornoSPAG` customiza tratamento de erros do sistema externo
   - Facilita manutenção e padronização de respostas

3. **Validação de Período Contestável:**
   - Lógica crítica implementada em `DataUtil` e `RelatoInfracaoUtil`
   - Diferencia prazos para transações normais (80 dias) e devoluções MED (30 dias)

4. **Swagger Codegen:**
   - Clientes das APIs consumidas são gerados automaticamente
   - Reduz erros de integração e facilita manutenção

5. **Tratamento Especial de Bloqueio:**
   - Falha no bloqueio (status 400) não interrompe o fluxo
   - Sistema marca flag `blockedBefore=true` e continua processamento
   - Pode indicar que o valor já estava bloqueado anteriormente

6. **Suporte a Múltiplos Tipos PIX:**
   - PIX devolução especial (MED)
   - PIX transferência normal
   - Diferenciação através de flags e tipos de transação

7. **Profiles de Ambiente:**
   - Configurações específicas para diferentes ambientes (dev, hom, prod)
   - Facilita deploy e gestão de configurações

8. **Monitoramento Completo:**
   - Dashboard Grafana pré-configurado com métricas JVM, HTTP, HikariCP
   - Prometheus configurado para scraping automático
   - Health checks via Spring Actuator

9. **Segurança:**
   - Autenticação via OAuth2/JWT
   - Token gerado dinamicamente para comunicação com SPAG
   - Validação de titularidade antes de processar contestação

10. **Modularização:**
    - Projeto dividido em módulos Maven (common, domain, application)
    - Facilita reuso e manutenção independente de componentes