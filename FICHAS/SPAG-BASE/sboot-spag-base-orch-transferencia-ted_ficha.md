# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema orquestrador de transferências TED (Transferência Eletrônica Disponível) do Banco Votorantim. O sistema é responsável por processar pagamentos via TED, coordenando a validação, débito/crédito em conta, integração com SPB (Sistema de Pagamentos Brasileiro), tratamento de ocorrências e notificações aos sistemas legados (SITP, PGFT e SPAG). Implementa fluxo completo com estorno automático em caso de falhas.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot, ponto de entrada da aplicação |
| `TransferenciaTedRouter` | Orquestrador Apache Camel que define as rotas de processamento de TED |
| `TransferenciaTedService` | Serviço de domínio que expõe métodos para processar pagamentos e retornos SPB |
| `TransferenciaTedController` | Controller REST que expõe endpoints HTTP para processamento de TED |
| `TransferenciaTedListener` | Listener JMS que consome mensagens de solicitação de TED da fila IBM MQ |
| `TransferenciaRetornoTedListener` | Listener JMS que consome mensagens de retorno do SPB |
| `CamelContextWrapper` | Wrapper do contexto Apache Camel para gerenciamento de rotas |
| `EstornoProcessor` | Processador Camel responsável por tratar estornos em caso de erro |
| `NotificacaoAggregation` | Estratégia de agregação Camel para consolidar notificações |
| Mappers (ValidarPagamentoMapper, etc.) | Conversão entre DTOs e objetos de domínio |
| Repositories (ValidarPagamentoRepository, etc.) | Interfaces de portas para comunicação com serviços externos |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot** (framework principal)
- **Apache Camel 3.0.1** (orquestração e integração)
- **IBM MQ** (mensageria para comunicação assíncrona)
- **RabbitMQ** (mensageria para notificações)
- **RestTemplate** (cliente HTTP para chamadas REST)
- **Lombok** (redução de boilerplate)
- **Swagger/OpenAPI** (documentação de APIs)
- **Spring Actuator + Prometheus** (métricas e monitoramento)
- **Logback** (logging)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Feature Toggle** (controle de funcionalidades)
- **OAuth2/JWT** (segurança e autenticação)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/transferencia-ted/pagamento-ted | TransferenciaTedController | Processa um pagamento TED de forma síncrona |
| POST | /v1/transferencia-ted/retorno-spb | TransferenciaTedController | Processa retorno do SPB para um pagamento TED |

---

## 5. Principais Regras de Negócio

1. **Validação de Pagamento**: Valida dados do pagamento antes de processar (ValidarPagamento)
2. **Débito em Conta**: Realiza débito na conta do remetente antes de enviar ao SPB
3. **Integração SPB**: Envia transação TED para o Sistema de Pagamentos Brasileiro
4. **Processamento de Retorno**: Processa retorno assíncrono do SPB via fila IBM MQ
5. **Estorno Automático**: Em caso de falha em qualquer etapa, realiza estorno automático do débito
6. **Tratamento de Ocorrências**: Registra e trata ocorrências/erros durante o processamento
7. **Notificações Múltiplas**: Notifica sistemas legados (SITP, PGFT, SPAG) sobre o resultado
8. **Atualização de Situação**: Atualiza status do lançamento no sistema SPAG
9. **Retry com Backoff**: Implementa retry automático com delay de 15 segundos (até 3 tentativas)
10. **Feature Toggle**: Controla ativação/desativação do listener de retorno via feature toggle
11. **Concorrência Dinâmica**: Ajusta número de consumidores JMS dinamicamente via feature toggle

---

## 6. Relação entre Entidades

**DicionarioPagamento**: Entidade central que trafega por todo o fluxo, contendo:
- Dados do remetente (conta, agência, CPF/CNPJ)
- Dados do favorecido (conta, agência, CPF/CNPJ)
- Valor da transferência
- Finalidade e histórico
- Flags de retorno de cada etapa
- Lista de ocorrências

**RetornoSPBRequest**: Representa retorno do SPB contendo:
- Código do lançamento
- Resultado (R1)
- Número de controle SPB

**SituacaoPagamento**: Representa situação do pagamento para atualização:
- Protocolo da transação
- Status do lançamento
- Ocorrências

**Relacionamentos**:
- Um DicionarioPagamento pode ter múltiplas Ocorrências
- Um DicionarioPagamento gera um RetornoSPBRequest
- Um DicionarioPagamento resulta em uma SituacaoPagamento

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
| application.yml | leitura | Spring Boot | Configurações da aplicação |
| application-local.yml | leitura | Spring Boot | Configurações para ambiente local |
| logback-spring.xml | leitura | Logback | Configuração de logs |
| sboot-spag-base-orch-transferencia-ted.swagger | leitura | Swagger Codegen | Especificação OpenAPI |

---

## 10. Filas Lidas

- **QL.SPAG.SOLICITAR_PAGAMENTO_TED_REQ.INT** (IBM MQ): Fila de entrada para solicitações de pagamento TED
- **QL.SPAG.RETORNO_PAGAMENTO_TED.INT** (IBM MQ): Fila de retorno do SPB com resultado do processamento

---

## 11. Filas Geradas

- **events.business.notificationService** (RabbitMQ): Exchange para notificação de pagamentos ao sistema SPAG
  - Routing Key: `SPAG.rk.notificationService`

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| atom-validar-pagamento | REST | Valida dados do pagamento antes do processamento |
| atom-debitar-creditar-conta (NCCS) | REST | Realiza débito/crédito e estorno em conta corrente |
| atom-integrarspb | REST | Integra com Sistema de Pagamentos Brasileiro (SPB) |
| atom-notificar-pagamento-sitp (SITP) | REST | Notifica sistema legado SITP sobre resultado |
| atom-notificar-pagamento-pgft (PGFT) | REST | Notifica sistema legado PGFT sobre resultado |
| atom-atualizar-situacao-spag | REST | Atualiza situação do lançamento no SPAG |
| atom-tratar-ocorrencias | REST | Registra e trata ocorrências do processamento |
| IBM MQ | JMS | Mensageria para recebimento de solicitações e retornos |
| RabbitMQ | AMQP | Mensageria para notificações assíncronas |
| API Gateway | OAuth2 | Autenticação e autorização via JWT |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões hexagonais (ports/adapters)
- Separação clara de responsabilidades em módulos (application, domain, common)
- Uso adequado de Apache Camel para orquestração complexa
- Implementação de retry e tratamento de erros robusto
- Uso de mappers para conversão de dados
- Configuração externalizada e suporte a múltiplos ambientes
- Implementação de estorno automático em caso de falhas
- Logs estruturados e informativos

**Pontos de Melhoria:**
- Falta de testes unitários e de integração nos arquivos analisados
- Configurações hardcoded em alguns pontos (ex: delays, tentativas)
- Uso de `simple()` do Camel em vez de constantes tipadas
- Falta de documentação inline em classes complexas
- Alguns métodos poderiam ser mais granulares
- Tratamento genérico de exceções em alguns pontos
- Dependência forte de bibliotecas legadas (votorantim.spag.lib.datatype)

---

## 14. Observações Relevantes

1. **Feature Toggle Dinâmico**: O sistema utiliza feature toggles para controlar dinamicamente o número de consumidores JMS e ativar/desativar o listener de retorno TED, permitindo ajustes em tempo de execução sem restart.

2. **Fluxo Assíncrono Híbrido**: Combina processamento síncrono (REST) e assíncrono (JMS/RabbitMQ), com listeners IBM MQ para entrada e RabbitMQ para notificações.

3. **Estorno Automático**: Implementa compensação automática (estorno) em caso de falha em qualquer etapa do processamento, garantindo consistência transacional.

4. **Orquestração Camel**: Utiliza Apache Camel para orquestrar fluxo complexo com múltiplas etapas sequenciais e paralelas, incluindo agregação de resultados.

5. **Retry Configurável**: Implementa retry automático com 3 tentativas e delay de 15 segundos, exceto para erros de notificação (5 tentativas).

6. **Segurança OAuth2**: Integração com API Gateway para obtenção de tokens JWT para chamadas autenticadas aos serviços downstream.

7. **Monitoramento**: Exposição de métricas Prometheus e endpoints Actuator para observabilidade.

8. **Multi-tenant**: Suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas.

9. **Processamento XML**: Utiliza JAXB para unmarshalling de mensagens XML recebidas via IBM MQ.

10. **Arquitetura Modular**: Projeto dividido em 3 módulos Maven (application, domain, common) seguindo princípios de Clean Architecture.