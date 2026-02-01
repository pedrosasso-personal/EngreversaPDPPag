# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema orquestrador responsável pelo envio automatizado de transferências TED (Transferência Eletrônica Disponível) para débitos automáticos de produtos do banco digital. O sistema realiza a conciliação de pagamentos por tipo de produto (Financiamento de Veículos, Crédito Pessoal e Crédito Fácil), consulta dados cadastrais, valida dias úteis, calcula valores totais e efetua as transferências via TED para as contas de convênio apropriadas.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `EnviaTedService` | Serviço principal que orquestra o fluxo de envio de TED |
| `EnviaTedRouter` | Roteador Apache Camel que define o fluxo de processamento |
| `EnviaTedController` | Controlador REST que expõe endpoints para iniciar processos |
| `ClienteDadosCadastraisRepositoryImpl` | Consulta dados cadastrais de remetente e favorecido |
| `TransferenciaRepositoryImpl` | Realiza o envio da transferência TED |
| `ObterUltimoDiaUtilRepositoryImpl` | Valida e obtém dias úteis para processamento |
| `TotalSumarizadoRepositoryImpl` | Consulta e gerencia totais de pagamentos por convênio |
| `InicioTransferenciaConsumer` | Consumidor de mensagens do Google Pub/Sub |
| `TipoProdutoEnum` | Enum que define os tipos de produtos e suas configurações |
| `EnviaTedDTO` | DTO principal que transporta dados entre as camadas |

## 3. Tecnologias Utilizadas

- **Framework**: Spring Boot 2.x
- **Integração**: Apache Camel 3.0.1
- **Mensageria**: Google Cloud Pub/Sub, RabbitMQ
- **Segurança**: Spring Security OAuth2 com JWT
- **Documentação**: Swagger/OpenAPI 3.0
- **Resiliência**: Resilience4j (Circuit Breaker e Retry)
- **Monitoramento**: Spring Actuator, Prometheus, Grafana
- **Banco de Dados**: HikariCP (pool de conexões)
- **Build**: Maven
- **Containerização**: Docker
- **Linguagem**: Java 11
- **Mapeamento**: MapStruct
- **Logging**: Logback

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/financiamento/veiculo` | `EnviaTedController` | Envia TED para financiamento de veículos |
| POST | `/v1/automacao-debito/{codTipoProduto}` | `EnviaTedController` | Automação de débito por tipo de produto específico |

## 5. Principais Regras de Negócio

1. **Validação de Dia Útil**: O sistema valida se o dia atual é útil antes de processar transferências
2. **Cálculo de Valores**: Soma todos os pagamentos com status "4" (aprovado) para determinar o valor total a transferir
3. **Conversão de Códigos Bancários**: Converte códigos internos de bancos (161, 436, 152) para códigos externos (655, 413, 633)
4. **Tipos de Produto**: Suporta três tipos de produtos:
   - Financiamento de Veículos (código 2, convênio 4)
   - Crédito Pessoal (código 3, convênio 3)
   - Crédito Fácil (código 4, convênio 7)
5. **Status de Processamento**: Controla execução com status: Executado (1), Pendente (2), Falha (3), Sem Valor para Transferir (4)
6. **Transferência Condicional**: Só realiza transferência se o valor total for maior que zero
7. **Histórico Personalizado**: Cada tipo de produto possui histórico específico para a transferência
8. **Praça**: Utiliza praça de São Paulo (código 2) para validação de dias úteis

## 6. Relação entre Entidades

**Entidades Principais:**

- **EnviaTedDTO**: Entidade central que agrega:
  - `DadosCadastrais` (remetente e favorecido)
  - `ultimaDataUtil` (LocalDate)
  - `totalSumarizadoConvenio` (BigDecimal)
  - `cdTipoProduto` (Integer)
  - `cdPagamento` (List<Integer>)

- **DadosCadastrais**: Contém informações bancárias:
  - Dados pessoais (CPF/CNPJ, nome)
  - Dados bancários (banco, agência, conta, tipo conta)
  - Dados de relacionamento (código, modalidade)

- **ExecucaoEnvioDebtoAutomatico**: Controla execução:
  - Status de processamento
  - Código de protocolo
  - Data e valor total
  - Lista de pagamentos

- **ProtocoloResponse**: Resposta da transferência:
  - Número do protocolo
  - Status
  - Código de autenticação bancária
  - Erros (se houver)

**Relacionamentos:**
- EnviaTedDTO (1) -> (2) DadosCadastrais (remetente/favorecido)
- EnviaTedDTO (1) -> (N) Pagamentos (via cdPagamento)
- ExecucaoEnvioDebtoAutomatico (1) -> (1) EnviaTedDTO

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| N/A | N/A | N/A | O sistema não acessa diretamente banco de dados, apenas consome APIs REST |

**Observação**: O sistema consome dados através de APIs REST de outros microserviços, não acessando diretamente estruturas de banco de dados.

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| N/A | N/A | N/A | O sistema não atualiza diretamente banco de dados, apenas consome e publica em APIs REST |

**Observação**: Atualizações são realizadas através de chamadas REST para outros microserviços.

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `application.yml` | Leitura | Spring Boot | Configurações da aplicação por ambiente |
| `logback-spring.xml` | Leitura | Logback | Configuração de logs |
| `swagger/*.yaml` | Leitura | Swagger Codegen | Contratos OpenAPI para geração de código |
| `prometheus.yml` | Leitura | Prometheus | Configuração de métricas |
| `grafana.ini` | Leitura | Grafana | Configuração de dashboards |

## 10. Filas Lidas

**Google Cloud Pub/Sub:**
- **Subscription**: `business-ccbd-base-inicio-transferencia-debito-sub`
  - **Classe**: `InicioTransferenciaConsumer`, `PubSubInputChannelConfiguration`
  - **Payload**: `PayloadListener` (contém `codigoTipoProduto`)
  - **Descrição**: Recebe eventos de início de transferência de débito automático
  - **Configuração**: 
    - Modo ACK: Manual
    - Block on Pull: true
    - Max Fetch Size: 100
    - Polling: Fixed Delay de 100ms

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

**APIs REST Consumidas:**

1. **sboot-glob-base-atom-cliente-dados-cadastrais**
   - Endpoint: `/v1/banco-digital/conta/{nuConta}`
   - Descrição: Consulta dados cadastrais de contas (remetente e favorecido)
   - Método: GET

2. **sboot-spag-base-orch-transferencias**
   - Endpoint: `/v1/transferencia`
   - Descrição: Realiza transferências TED/TEF/DOC
   - Método: POST

3. **sboot-dcor-base-atom-dias-uteis**
   - Endpoints: 
     - `/v1/corporativo/calendario/dias-uteis/{data}/ultimo` (GET)
     - `/v1/corporativo/calendario/validar-dia-util/{data}` (GET)
   - Descrição: Valida e obtém dias úteis bancários

4. **sboot-ccbd-base-atom-debito-automatico**
   - Endpoints:
     - `/v1/banco-digital/conta/debito-automatico/consultar-pgmt-subproduto` (GET)
     - `/v1/banco-digital/conta/debito-automatico/consultarTotalPagamentosPorConvenio` (GET)
     - `/v1/banco-digital/conta/debito-automatico/iniciar-execucao-envio` (POST)
     - `/v1/banco-digital/conta/debito-automatico/finalizar-execucao-envio` (POST)
   - Descrição: Gerencia pagamentos de débito automático

**Autenticação:**
- Todas as integrações utilizam OAuth2 com JWT
- Token obtido via `GatewayOAuthService`

**Resiliência:**
- Circuit Breaker configurado para todas as integrações
- Retry com backoff exponencial (3 tentativas, 2s inicial)

## 13. Avaliação da Qualidade do Código

**Nota: 7.5/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (domain, application, common)
- Uso adequado de padrões como Repository, DTO e Mapper
- Implementação de resiliência com Circuit Breaker e Retry
- Testes unitários presentes para a maioria das classes
- Uso de Lombok reduzindo boilerplate
- Configuração adequada de logs e monitoramento
- Documentação OpenAPI bem estruturada
- Uso de enums para constantes e tipos

**Pontos de Melhoria:**
- Alguns métodos com lógica complexa poderiam ser refatorados (ex: `transferenciaRequest`)
- Tratamento de exceções genérico em alguns pontos (catch Exception)
- Falta de validações de entrada em alguns métodos
- Alguns logs poderiam ser mais informativos
- Ausência de testes de integração mais abrangentes
- Configurações hardcoded em alguns enums (contas, bancos)
- Documentação inline (JavaDoc) ausente em várias classes
- Alguns métodos com múltiplas responsabilidades

**Recomendações:**
1. Adicionar validações de entrada com Bean Validation
2. Melhorar tratamento de exceções com exceções customizadas mais específicas
3. Adicionar mais JavaDoc nas classes de domínio
4. Extrair configurações de contas/bancos para arquivo de propriedades
5. Aumentar cobertura de testes de integração

## 14. Observações Relevantes

1. **Arquitetura**: O sistema segue arquitetura hexagonal com separação clara entre domain, application e infrastructure

2. **Processamento Assíncrono**: Utiliza Google Pub/Sub para processamento assíncrono de transferências iniciadas por eventos

3. **Fluxo Apache Camel**: O fluxo principal é orquestrado via Apache Camel com processadores específicos para cada etapa:
   - Validação de dia útil
   - Consulta de dados cadastrais
   - Cálculo de totais
   - Envio de transferência
   - Finalização com registro de status

4. **Ambientes**: Suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas

5. **Monitoramento**: Integração completa com Prometheus e Grafana para observabilidade

6. **Segurança**: Implementa OAuth2 com JWT para todas as integrações externas

7. **Contas Específicas**: Cada tipo de produto possui contas específicas de remetente e favorecido configuradas no enum `TipoProdutoEnum`

8. **Conversão de Códigos**: Sistema realiza conversão entre códigos internos e externos de bancos (BV: 161↔655, BVSA: 436↔413, Rendimento: 152↔633)

9. **Status de Processamento**: Controle rigoroso de status de execução com registro de início e fim de processamento

10. **Infraestrutura como Código**: Possui configuração completa para deploy em Kubernetes/OpenShift via arquivo `infra.yml`