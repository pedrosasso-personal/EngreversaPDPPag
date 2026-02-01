# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-ccbd-base-atom-debito-iss-exc** é um serviço atômico desenvolvido em Spring Boot que tem como objetivo processar exceções relacionadas a débitos de ISS (Imposto Sobre Serviços) no contexto de transações de cartão de débito CCBD. O sistema consome mensagens de uma fila RabbitMQ, processa as exceções recebidas e as persiste em um banco de dados SQL Server para registro e auditoria.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal que inicializa a aplicação Spring Boot |
| `DebitoIssExcListener` | Listener que consome mensagens da fila RabbitMQ e processa exceções de débito ISS |
| `DebitoIssExcService` / `DebitoIssExcServiceImpl` | Interface e implementação do serviço de negócio para processamento de exceções |
| `CCBDRepository` / `CCBDRepositoryImpl` | Interface e implementação do repositório para acesso ao banco de dados usando JDBI |
| `DebitoIssExc` | Entidade de domínio que representa uma exceção de débito ISS |
| `DataBaseConfiguration` | Configuração do datasource e JDBI para acesso ao banco de dados |
| `DebitoIssExcConfiguration` | Configuração de beans do domínio e RabbitMQ |
| `OpenApiConfiguration` | Configuração do Swagger para documentação de APIs |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Maven** (gerenciamento de dependências)
- **JDBI 3.9.1** (acesso a banco de dados)
- **SQL Server** (banco de dados)
- **RabbitMQ** (mensageria)
- **Spring AMQP** (integração com RabbitMQ)
- **Lombok** (redução de código boilerplate)
- **Swagger/Springfox 2.9.2** (documentação de APIs)
- **Micrometer/Prometheus** (métricas e monitoramento)
- **Grafana** (visualização de métricas)
- **Docker** (containerização)
- **HikariCP** (pool de conexões)
- **Logback** (logging)

---

## 4. Principais Endpoints REST

Não se aplica. O sistema não expõe endpoints REST para consumo externo. É um serviço orientado a eventos que consome mensagens de filas.

---

## 5. Principais Regras de Negócio

1. **Consumo de Mensagens de Exceção**: O sistema escuta a fila `events.business.CCBD-BASE.trataErroDebitoIss` e processa mensagens do tipo `DebitoIssExc`.

2. **Persistência de Exceções**: Todas as exceções de débito ISS recebidas são inseridas na tabela `TbLoteErro` do banco de dados para registro e auditoria.

3. **Tratamento de Erros**: Em caso de falha ao salvar no banco de dados, o erro é logado mas não interrompe o processamento (a mensagem não é rejeitada).

4. **Identificação de Origem**: Cada registro de erro é marcado com o identificador 'CCBD_DEBITOISS' para rastreabilidade da origem.

5. **Registro Temporal**: Cada exceção registrada inclui timestamps de criação e atualização automáticos.

---

## 6. Relação entre Entidades

**DebitoIssExc** (Entidade de Domínio):
- `cdBanco` (Integer): Código do banco
- `nuContaCorrente` (Long): Número da conta corrente
- `cdTipoConta` (Integer): Código do tipo de conta
- `cdProtocolo` (String): Código do protocolo da transação
- `dtLancamentoContabil` (String): Data do lançamento contábil
- `vrOperacao` (BigDecimal): Valor da operação
- `descricaoExcecao` (String): Descrição da exceção ocorrida

Não há relacionamentos entre entidades, pois existe apenas uma entidade de domínio no sistema.

---

## 7. Estruturas de Banco de Dados Lidas

Não se aplica. O sistema não realiza operações de leitura no banco de dados.

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| `DBCCBD.CCBDTransacaoCartaoDebito.TbLoteErro` | Tabela | INSERT | Tabela que armazena os registros de exceções de débito ISS, incluindo dados da conta, protocolo, data contábil, valor da operação e descrição do erro |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `application.yml` | Leitura | Spring Boot | Arquivo de configuração da aplicação com propriedades de datasource, RabbitMQ e profiles |
| `logback-spring.xml` | Leitura | Logback | Arquivo de configuração de logs da aplicação |
| `insertIssExcecao.sql` | Leitura | CCBDRepositoryImpl | Script SQL para inserção de exceções na tabela TbLoteErro |

---

## 10. Filas Lidas

- **Fila**: `events.business.CCBD-BASE.trataErroDebitoIss`
  - **Tecnologia**: RabbitMQ
  - **Formato**: JSON (convertido automaticamente para objeto `DebitoIssExc`)
  - **Classe Consumidora**: `DebitoIssExcListener`
  - **Descrição**: Fila que recebe eventos de exceções relacionadas a débitos de ISS para processamento e persistência

---

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas.

---

## 12. Integrações Externas

1. **Banco de Dados SQL Server**
   - **Tipo**: Banco de dados relacional
   - **Servidor**: SQLDES35/SQLUAT35/SQLPRD35 (conforme ambiente)
   - **Database**: DBCCBD
   - **Schema**: CCBDTransacaoCartaoDebito
   - **Usuário**: CCBDTransacaoCartaoDebito
   - **Descrição**: Banco de dados principal para persistência de exceções

2. **RabbitMQ**
   - **Tipo**: Message Broker
   - **Host**: Variável conforme ambiente (rabbit-ccbd-base)
   - **Virtual Host**: /
   - **Usuário**: Variável conforme ambiente (_ccbd_des, _ccbd_uat, _ccbd)
   - **Descrição**: Sistema de mensageria para consumo de eventos de exceções

3. **Prometheus/Grafana**
   - **Tipo**: Monitoramento e métricas
   - **Descrição**: Stack de observabilidade para coleta e visualização de métricas da aplicação

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem organizada seguindo padrões hexagonais (domain, application, infrastructure)
- Uso adequado de injeção de dependências e inversão de controle
- Separação clara de responsabilidades entre camadas
- Uso de Lombok para reduzir boilerplate
- Configuração adequada de observabilidade (métricas, logs)
- Testes unitários presentes
- Documentação básica presente (README)

**Pontos de Melhoria:**
- Tratamento de exceções muito genérico no listener (captura Exception e apenas loga)
- Falta validação dos dados recebidos da fila antes de persistir
- Ausência de testes de integração mais robustos
- Falta de tratamento para mensagens inválidas ou corrompidas
- Configuração de retry/DLQ não está explícita
- Comentários e documentação inline são escassos
- Falta de validação de campos obrigatórios na entidade DebitoIssExc

---

## 14. Observações Relevantes

1. **Ambiente Multi-Profile**: O sistema suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas para cada um.

2. **Segurança de Credenciais**: As credenciais de banco de dados e RabbitMQ são injetadas via variáveis de ambiente, seguindo boas práticas de segurança.

3. **Monitoramento**: O sistema está preparado para monitoramento com Prometheus e Grafana, expondo métricas no endpoint `/actuator/prometheus`.

4. **Containerização**: Dockerfile presente utilizando imagem OpenJ9 otimizada para consumo de memória.

5. **Infraestrutura como Código**: Arquivo `infra.yml` presente para deploy em Kubernetes/OpenShift.

6. **Resiliência**: Configuração de HikariCP para pool de conexões, mas falta configuração explícita de retry e circuit breaker.

7. **Auditoria**: Sistema de trilha de auditoria integrado via biblioteca `springboot-arqt-base-trilha-auditoria-web`.

8. **Versionamento**: Sistema está na versão 0.3.0, indicando que ainda está em fase de desenvolvimento/estabilização.

9. **Padrão Organizacional**: Segue padrões arquiteturais do Banco Votorantim, conforme documentação de referência no README.