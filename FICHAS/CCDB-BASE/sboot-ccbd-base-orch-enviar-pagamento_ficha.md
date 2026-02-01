# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema orquestrador responsável por enviar pagamentos de diferentes tipos (boletos de cobrança, boletos de tributo e transferências TED) para sistemas externos de processamento. O sistema atua como intermediário entre o recebimento de solicitações via filas RabbitMQ e o envio para APIs de pagamento (SPAG), incluindo tratamento de estornos e atualização de lançamentos. Utiliza Apache Camel para orquestração de fluxos e Spring Boot como framework base.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal de inicialização da aplicação Spring Boot |
| **EnviarPagamentoConfiguration** | Configuração central dos beans do sistema, incluindo rotas Camel e serviços |
| **BoletoCobrancaListener** | Consumidor de mensagens de pagamento de boleto de cobrança da fila RabbitMQ |
| **BoletoTributoListener** | Consumidor de mensagens de pagamento de boleto de tributo da fila RabbitMQ |
| **TransferenciaTedListener** | Consumidor de mensagens de transferência TED da fila RabbitMQ |
| **EstornoListener** | Consumidor de mensagens de estorno da fila RabbitMQ |
| **BoletoCobrancaRepositoryImpl** | Implementação de envio de pagamento de boleto de cobrança para API SPAG |
| **BoletoTributoRepositoryImpl** | Implementação de envio de pagamento de boleto de tributo para API SPAG |
| **TransferenciaRepositoryImpl** | Implementação de envio de transferência para API SPAG |
| **EstornoRepositoryImpl** | Implementação de envio de estorno e publicação em filas |
| **LancamentoBoletoRepositoryImpl** | Implementação de atualização de lançamentos de boletos |
| **EnviarBolCobrancaRouter** | Rota Camel para orquestração de pagamento de boleto de cobrança |
| **EnviarBolTributoRouter** | Rota Camel para orquestração de pagamento de boleto de tributo |
| **EnviarTransferenciaRouter** | Rota Camel para orquestração de transferências |
| **EstornoRouter** | Rota Camel para processamento de estornos |
| **CamelContextWrapper** | Wrapper para gerenciamento do contexto Apache Camel |

## 3. Tecnologias Utilizadas

- **Java 11** (OpenJ9)
- **Spring Boot 2.x** (framework base)
- **Apache Camel 3.0.1** (orquestração de fluxos)
- **RabbitMQ** (mensageria)
- **Spring AMQP** (integração com RabbitMQ)
- **MapStruct 1.4.1** (mapeamento de objetos)
- **Lombok** (redução de boilerplate)
- **Swagger/OpenAPI** (documentação de APIs)
- **Prometheus + Grafana** (métricas e monitoramento)
- **Logback** (logging)
- **RestTemplate** (cliente HTTP)
- **OAuth2** (autenticação via Gateway)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **JUnit 5 + Mockito** (testes)
- **Pact** (testes de contrato)

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | /v1/enviar-pagamento | EnviarPagamentoController | Endpoint de exemplo/teste (retorna dados mockados) |
| GET | /actuator/health | Spring Actuator | Health check da aplicação |
| GET | /actuator/prometheus | Spring Actuator | Métricas para Prometheus |
| GET | /swagger-ui.html | Springfox | Documentação Swagger da API |

**Observação:** O sistema é primariamente orientado a eventos (event-driven), consumindo mensagens de filas RabbitMQ. Os endpoints REST são principalmente para monitoramento e documentação.

## 5. Principais Regras de Negócio

1. **Processamento de Pagamento de Boleto de Cobrança:**
   - Recebe solicitação via fila RabbitMQ
   - Envia para API SPAG de boleto de cobrança
   - Atualiza lançamento com protocolo retornado
   - Em caso de erro, aciona processo de estorno

2. **Processamento de Pagamento de Boleto de Tributo:**
   - Recebe solicitação via fila RabbitMQ
   - Envia para API SPAG de boleto de tributo
   - Extrai código de lançamento do protocolo retornado
   - Atualiza lançamento com status
   - Em caso de erro, aciona processo de estorno

3. **Processamento de Transferência TED:**
   - Recebe solicitação via fila RabbitMQ
   - Envia para API SPAG de transferências
   - Em caso de erro, aciona processo de estorno

4. **Processamento de Estorno:**
   - Recebe solicitação de estorno via fila
   - Envia estorno para API de pagamentos (PGFT)
   - Publica notificação de estorno em fila específica

5. **Retry com Backoff Exponencial:**
   - Configurado retry automático para consumo de filas
   - Intervalo inicial: 100ms
   - Intervalo máximo: 1000ms
   - Máximo de 3 tentativas

6. **Autenticação OAuth2:**
   - Todas as chamadas para APIs externas utilizam token OAuth2
   - Token obtido via Gateway OAuth Service

## 6. Relação entre Entidades

**Entidades Principais:**

- **BoletoCobrancaInbound**: Dados de entrada para pagamento de boleto de cobrança
  - Contém: Remetente, Favorecido, dados do boleto, valores
  
- **BoletoTributoInbound**: Dados de entrada para pagamento de boleto de tributo
  - Contém: Remetente, dados do tributo, valores (documento, juros, multa, desconto)
  
- **TransferenciaInbound**: Dados de entrada para transferência
  - Contém: Remetente, Favorecido, dados da transferência
  
- **EstornoInbound**: Dados de entrada para estorno
  - Contém: NSU do estorno, tipo de pagamento, CPF, datas
  
- **Remetente/Pessoa**: Dados do remetente do pagamento
  - Contém: CPF/CNPJ, nome, banco, agência, conta, tipo de pessoa
  
- **Favorecido**: Dados do favorecido do pagamento
  - Contém: CPF/CNPJ, nome, banco, tipo de pessoa

**DTOs de Processamento:**

- **BoletoCobrancaDto**: Encapsula BoletoCobrancaInbound + número de protocolo
- **BoletoTributoDto**: Encapsula BoletoTributoInbound + número de protocolo
- **TransferenciaDto**: Encapsula TransferenciaInbound
- **LancamentoBoleto**: Dados para atualização de lançamento

**Relacionamentos:**
- BoletoCobrancaInbound → Remetente (1:1)
- BoletoCobrancaInbound → Favorecido (1:1)
- BoletoTributoInbound → Remetente (1:1)
- TransferenciaInbound → Remetente (1:1)
- TransferenciaInbound → Favorecido (1:1)

## 7. Estruturas de Banco de Dados Lidas

não se aplica

**Observação:** O sistema não acessa diretamente banco de dados. Toda persistência é delegada para APIs externas.

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

**Observação:** O sistema não atualiza diretamente banco de dados. Toda persistência é delegada para APIs externas.

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | leitura | /usr/etc/log (runtime) | Configuração de logging da aplicação |
| application.yml | leitura | src/main/resources | Configurações da aplicação (profiles, RabbitMQ, URLs) |
| swagger/*.yaml | leitura | Swagger Codegen Plugin | Especificações OpenAPI para geração de clientes REST |

## 10. Filas Lidas

| Nome da Fila | Exchange | Routing Key | Classe Consumidora | Descrição |
|--------------|----------|-------------|-------------------|-----------|
| eventos.transacional.envio.spag.boleto.cobranca | N/A | N/A | BoletoCobrancaListener | Recebe solicitações de pagamento de boleto de cobrança |
| eventos.transacional.envio.spag.boleto.tributo | N/A | N/A | BoletoTributoListener | Recebe solicitações de pagamento de boleto de tributo |
| eventos.transacional.envio.spag.transferencia.ted | N/A | N/A | TransferenciaTedListener | Recebe solicitações de transferência TED |
| eventos.transacional.estorno | N/A | N/A | EstornoListener | Recebe solicitações de estorno |

## 11. Filas Geradas

| Nome da Fila/Exchange | Routing Key | Classe Produtora | Descrição |
|-----------------------|-------------|-----------------|-----------|
| ex.ccbd.eventos.transacional | ccbd.rk.transacional.estorno | EstornoRepositoryImpl | Publica solicitações de estorno quando ocorre erro no processamento |
| ex.ccbd.eventos.transacional | ccbd.rk.transacional.notificar.estorno | EstornoRepositoryImpl | Publica notificações de estorno processado com sucesso |

## 12. Integrações Externas

| Sistema/API | Tipo | Classe Responsável | Descrição |
|-------------|------|-------------------|-----------|
| SPAG - Pagamento Boleto Cobrança | REST API | BoletoCobrancaRepositoryImpl | API para processamento de pagamento de boleto de cobrança |
| SPAG - Pagamento Boleto Tributo | REST API | BoletoTributoRepositoryImpl | API para processamento de pagamento de boleto de tributo |
| SPAG - Transferências | REST API | TransferenciaRepositoryImpl | API para processamento de transferências TED |
| PGFT - Pagamentos | REST API | EstornoRepositoryImpl | API para processamento de estornos |
| Lançamento Boleto | REST API | LancamentoBoletoRepositoryImpl | API para atualização de lançamentos de boletos |
| Gateway OAuth | REST API | GatewayOAuthService | Serviço de autenticação OAuth2 para obtenção de tokens |

**URLs por Ambiente:**
- **DES:** URLs apontam para appdes.bvnet.bv
- **QA:** URLs apontam para appqa.bvnet.bv
- **UAT:** URLs apontam para appuat.bvnet.bv
- **PRD:** URLs apontam para app.bvnet.bv

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (domain, application, infrastructure)
- Uso adequado de padrões como Repository, Service e Mapper
- Implementação de retry com backoff exponencial para resiliência
- Tratamento de exceções estruturado com exceções customizadas
- Uso de Apache Camel para orquestração de fluxos complexos
- Configuração externalizada por profiles
- Boa cobertura de testes unitários
- Uso de MapStruct para mapeamento de objetos
- Logging estruturado e adequado

**Pontos de Melhoria:**
- Código comentado em várias classes (estornos desabilitados), indicando funcionalidade incompleta ou em transição
- Algumas classes com responsabilidades múltiplas (ex: EstornoRepositoryImpl faz publicação em fila e chamada REST)
- Falta de validação de entrada em alguns pontos
- Uso de strings hardcoded para nomes de filas e exchanges (poderia ser externalizado)
- Alguns métodos com lógica de negócio misturada com infraestrutura
- Falta de documentação JavaDoc em classes críticas
- Tratamento genérico de exceções em alguns listeners (catch Exception)
- Código de teste com alguns métodos vazios ou incompletos

## 14. Observações Relevantes

1. **Arquitetura Event-Driven:** O sistema é primariamente orientado a eventos, consumindo mensagens de filas RabbitMQ e orquestrando chamadas para APIs externas.

2. **Apache Camel:** Utiliza Apache Camel para orquestração de fluxos, com rotas específicas para cada tipo de pagamento e tratamento de erro com estorno automático.

3. **Resiliência:** Implementa retry automático com backoff exponencial para consumo de filas (3 tentativas, intervalo inicial 100ms, máximo 1000ms).

4. **Multi-ambiente:** Configurado para múltiplos ambientes (local, des, qa, uat, prd) com URLs e credenciais específicas.

5. **Monitoramento:** Integrado com Prometheus e Grafana para métricas, com dashboard pré-configurado.

6. **Segurança:** Todas as chamadas externas utilizam OAuth2 via Gateway, com tokens gerenciados automaticamente.

7. **Funcionalidade de Estorno:** Código comentado indica que a funcionalidade de estorno automático está desabilitada, possivelmente em fase de testes ou aguardando homologação.

8. **Geração de Código:** Utiliza Swagger Codegen para gerar clientes REST a partir de especificações OpenAPI, garantindo conformidade com contratos.

9. **Containerização:** Preparado para execução em containers Docker/OpenShift com Dockerfile otimizado usando OpenJ9.

10. **Testes:** Estrutura de testes bem organizada (unit, integration, functional) com suporte a testes de contrato via Pact.