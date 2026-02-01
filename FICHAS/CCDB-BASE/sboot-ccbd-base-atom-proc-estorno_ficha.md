# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-ccbd-base-atom-proc-estorno** é um serviço atômico desenvolvido em Java com Spring Boot, responsável pelo processamento e gerenciamento de estornos de transações de cartão de débito no contexto do sistema CCBD (Cartão de Crédito e Débito) do Banco Votorantim. 

O sistema recebe mensagens de uma fila RabbitMQ contendo informações sobre estornos, atualiza o status de transações no banco de dados SQL Server, e expõe endpoints REST para consulta de estornos e validação de débitos no TIF (sistema de transações). Sua principal função é manter a consistência dos dados de estorno entre diferentes sistemas e bases de dados.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal que inicializa a aplicação Spring Boot |
| **ProcEstornoListener** | Listener que consome mensagens da fila RabbitMQ para processar estornos |
| **ProcEstornoController** | Controller REST que expõe endpoints para consulta de estornos e débitos TIF |
| **ProcEstornoServiceImpl** | Implementação da lógica de negócio para processamento de estornos |
| **CCBDRepositoryImpl** | Interface JDBI que realiza operações de banco de dados |
| **ProcEstornoConfiguration** | Configuração de beans do Spring (serviços, conversores de mensagens) |
| **JdbiConfiguration** | Configuração do JDBI para acesso ao banco de dados |
| **OpenApiConfiguration** | Configuração do Swagger para documentação da API |
| **EstornoResponseRowMapper** | Mapper para conversão de ResultSet em objetos EstornoResponse |
| **TifDebitoRowMapper** | Mapper para conversão de ResultSet em objetos TifDebito |
| **ProcEstorno** | Entidade de domínio representando dados de estorno |
| **ProcEstornoDTO** | DTO para recebimento de dados da fila RabbitMQ |
| **EstornoResponse/EstornoResult** | Objetos de resposta para consultas de estorno |
| **TifDebito** | Entidade representando débitos no sistema TIF |

---

## 3. Tecnologias Utilizadas

- **Java 11** (OpenJDK com OpenJ9)
- **Spring Boot** (framework principal)
- **Spring Web** (para endpoints REST)
- **Spring AMQP / RabbitMQ** (mensageria)
- **JDBI 3.9.1** (acesso a banco de dados)
- **SQL Server** (Microsoft SQL Server JDBC Driver 7.2.2)
- **Swagger/OpenAPI 2.0** (documentação de API via Springfox 3.0.0)
- **Lombok** (redução de boilerplate)
- **MapStruct 1.5.3** (mapeamento de objetos)
- **Logback** (logging com formato JSON)
- **Spring Actuator + Micrometer Prometheus** (monitoramento e métricas)
- **JUnit 5 + Mockito** (testes unitários)
- **Maven** (gerenciamento de dependências e build)
- **Docker** (containerização)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| PUT | `/v1/proc-estorno/consultarEstornos` | ProcEstornoController | Consulta operações de estorno com base em lista de contas e parâmetros de transação |
| PUT | `/v1/proc-estorno/atualizarStatusEstorno` | ProcEstornoController | Atualiza o campo FlBase2Estornado para 'S' indicando estorno processado |
| GET | `/v1/proc-estorno/consultarDebitoTif` | ProcEstornoController | Consulta débitos no sistema TIF (COD22) por número de conta e NSU |

---

## 5. Principais Regras de Negócio

1. **Processamento de Estorno via Fila**: O sistema consome mensagens da fila `events.business.CCBD-BASE.estornoArquivoBase2Relatorio` e atualiza a tabela `TbConciliacaoTransacao` com flag `FlBase2Estornado='N'` e mensagem de conciliação.

2. **Validação de Campos Obrigatórios**: Antes de atualizar o banco, valida se todos os campos obrigatórios do objeto ProcEstorno estão preenchidos usando Bean Validation.

3. **Consulta de Estornos**: Busca transações de estorno (tipos 0100 e 0200) que possuem protocolo ITP, filtrando por lista de contas, produto do cartão, correlativo, moeda e autorizador.

4. **Atualização de Status de Estorno**: Marca transações como estornadas alterando `FlBase2Estornado` para 'S' e registrando data de alteração.

5. **Consulta TIF**: Valida débitos no sistema TIF formatando o número da conta com zeros à esquerda (9 dígitos) e buscando por conta e NSU.

6. **Formatação de Conta Corrente**: Completa números de conta com zeros à esquerda para atingir tamanho padrão (9 dígitos para TIF, 20 para BACEN).

7. **Tratamento de Exceções**: Captura e loga erros específicos para cada operação (atualização, consulta, validação) com mensagens padronizadas via enum.

---

## 6. Relação entre Entidades

**Principais Entidades e Relacionamentos:**

- **ProcEstorno**: Entidade principal contendo dados completos de uma transação de estorno (código de conciliação, tipo de transação, valores, datas, flags de controle).

- **ProcEstornoDTO**: DTO que espelha ProcEstorno, usado para deserialização de mensagens JSON do RabbitMQ.

- **EstornoResponse**: Representa o resultado de uma consulta de estorno (número de conta, NSU, código de transação processadora, status).

- **EstornoResult**: Objeto de resultado que encapsula EstornoResponse com informações adicionais da conta.

- **Conta**: Entidade que representa dados de uma conta corrente (titular, CPF/CNPJ, agência, banco, número da conta, tipo).

- **TifDebito**: Representa um débito no sistema TIF (conta remetente, identificador de transação, status, tipo, valor, NSU).

**Relacionamentos:**
- EstornoResult contém uma Conta
- ProcEstorno é mapeado de/para ProcEstornoDTO
- EstornoResponse é convertido em EstornoResult com Conta associada

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| CCBDTransacaoCartaoDebito.TbControleTransacaoCartao | tabela | SELECT | Consulta transações de cartão para verificar estornos |
| CCBDTransacaoCartaoDebito.TbTipoTransacao | tabela | SELECT | Consulta tipos de transação (0100, 0200) |
| CCBDTransacaoCartaoDebito.TbTransacaoCartao | tabela | SELECT | Consulta dados complementares de transações de cartão |
| CCBDTransacaoCartaoDebito.TbConciliacaoTransacaoDebito | tabela | SELECT | Consulta débitos no TIF por conta e NSU |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| CCBDTransacaoCartaoDebito.TbConciliacaoTransacao | tabela | UPDATE | Atualiza flag FlBase2Estornado='N' e mensagem de conciliação ao processar estorno da fila |
| CCBDTransacaoCartaoDebito.TbConciliacaoTransacao | tabela | UPDATE | Atualiza flag FlBase2Estornado='S' ao confirmar estorno processado |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | leitura | /usr/etc/log (configurável por ambiente) | Arquivo de configuração de logs em formato JSON |
| application.yml | leitura | classpath:application.yml | Configurações da aplicação (datasource, RabbitMQ, profiles) |
| *.sql (consultarEstorno, updateProcEstorno, etc) | leitura | CCBDRepositoryImpl (via JDBI) | Queries SQL carregadas do classpath para execução |

---

## 10. Filas Lidas

- **events.business.CCBD-BASE.estornoArquivoBase2Relatorio**: Fila RabbitMQ que recebe mensagens JSON com dados de estorno (ProcEstornoDTO) para processamento. Configurada com dead-letter-exchange para tratamento de falhas.

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| SQL Server (DBCCBD) | Banco de Dados | Banco de dados principal contendo tabelas de transações de cartão e conciliação |
| RabbitMQ | Mensageria | Sistema de filas para recebimento assíncrono de eventos de estorno |
| Sistema TIF | Banco de Dados | Sistema de transações integrado via consultas à tabela TbConciliacaoTransacaoDebito |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (application, domain, common)
- Uso adequado de padrões como Repository, Service, DTO
- Configuração clara de infraestrutura (JDBI, RabbitMQ, Swagger)
- Presença de testes unitários para as principais classes
- Uso de Lombok para reduzir boilerplate
- Tratamento de exceções com classes específicas e enum de mensagens
- Documentação OpenAPI/Swagger bem estruturada
- Configuração de ambientes via profiles do Spring

**Pontos de Melhoria:**
- Algumas classes de domínio possuem getters/setters redundantes mesmo usando Lombok @Data
- Falta de validações mais robustas nos DTOs (Bean Validation annotations)
- Logs poderiam ser mais estruturados com MDC para rastreabilidade
- Ausência de testes de integração e funcionais (apenas estrutura preparada)
- Tratamento genérico de exceções em alguns pontos (catch Exception)
- Falta de documentação JavaDoc nas classes e métodos principais
- Alguns métodos longos que poderiam ser refatorados (ex: ProcEstornoServiceImpl.updateProcEstorno)
- Configuração de segurança OAuth2 definida mas não implementada
- Falta de circuit breaker ou retry para operações de banco/fila

---

## 14. Observações Relevantes

1. **Arquitetura Hexagonal**: O projeto segue princípios de arquitetura hexagonal com separação clara entre domain (regras de negócio), application (infraestrutura) e ports (interfaces).

2. **Multi-ambiente**: Configuração preparada para múltiplos ambientes (local, des, qa, uat, prd) com secrets e configmaps gerenciados via Kubernetes.

3. **Observabilidade**: Integração com Prometheus para métricas e Actuator para health checks, preparado para monitoramento em produção.

4. **Auditoria**: Dependência de biblioteca de trilha de auditoria do Banco Votorantim (springboot-arqt-base-trilha-auditoria-web).

5. **Containerização**: Dockerfile otimizado usando AdoptOpenJDK com OpenJ9 para melhor performance de memória.

6. **Testes Arquiteturais**: Estrutura preparada para testes de conformidade arquitetural usando ArchUnit (profile architecture).

7. **Versionamento de API**: Endpoints versionados com prefixo /v1/ seguindo boas práticas REST.

8. **Dead Letter Queue**: Configuração de DLQ no RabbitMQ para tratamento de mensagens com falha.

9. **Formatação de Dados**: Utilitário específico para formatação de números de conta conforme padrões BACEN e TIF.

10. **Geração de Código**: Uso de swagger-codegen-maven-plugin para gerar interfaces de API a partir da especificação OpenAPI.