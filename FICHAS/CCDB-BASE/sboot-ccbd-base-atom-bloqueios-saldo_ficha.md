# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-ccbd-base-atom-bloqueios-saldo** é um microsserviço atômico corporativo responsável por gerenciar o monitoramento de bloqueios de saldo em contas correntes de clientes. Ele permite consultar, incluir, atualizar e deletar monitoramentos de bloqueios, além de processar eventos de crédito recebido e atualização de bloqueios através de mensageria (Google Cloud Pub/Sub). O sistema integra-se com banco de dados MySQL para persistência e publica/consome mensagens em tópicos para orquestração de bloqueios.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot que inicializa a aplicação |
| `MonitoramentoApiDelegateImpl` | Controlador REST que implementa os endpoints da API de monitoramento |
| `MonitoramentoSaldoService` | Serviço de negócio para operações CRUD de monitoramento de saldo |
| `AtualizaSaldoBloqueadoService` | Processa atualizações de saldo bloqueado vindas de mensagens |
| `CreditoRecebidoService` | Processa eventos de crédito recebido e cria bloqueios conforme necessário |
| `GetMonitoramentoSaldoService` | Serviço especializado para consulta de monitoramentos |
| `MotivoBloqueioService` | Gerencia motivos de bloqueio e suas validações |
| `MonitoramentoSaldoRepositoryImpl` | Implementação de repositório para operações de monitoramento no banco |
| `MonitoramentoSaldoBloqueadoRepositoryImpl` | Implementação de repositório para operações de saldos bloqueados |
| `MotivoBloqueioRepositoryImpl` | Implementação de repositório para consulta de motivos de bloqueio |
| `CreditoBloqueadoListener` | Listener que consome mensagens de crédito recebido do Pub/Sub |
| `MonitoramentoSaldoListener` | Listener que consome mensagens de atualização de monitoramento |
| `TopicDefaultPublisher` | Publisher para envio de mensagens ao tópico default |
| `MonitoramentoConcluidoPublisher` | Publisher para envio de mensagens de monitoramento concluído |
| `MonitoramentoSaldo` | Entidade de domínio representando um monitoramento de saldo |
| `MonitoramentoSaldoBloqueado` | Entidade de domínio representando um bloqueio de saldo específico |
| `MotivoBloqueio` | Entidade de domínio representando um motivo de bloqueio |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.x** (framework principal)
- **Spring Security OAuth2** (autenticação e autorização JWT)
- **Spring Integration** (integração com mensageria)
- **Google Cloud Pub/Sub** (mensageria assíncrona)
- **JDBI 3.x** (acesso a dados SQL)
- **MySQL 8.x** (banco de dados relacional)
- **Apache Avro** (serialização de mensagens)
- **Swagger/OpenAPI 3.0** (documentação de API)
- **Springfox** (geração de documentação Swagger)
- **MapStruct** (mapeamento de objetos)
- **Lombok** (redução de boilerplate)
- **Logback** (logging com formato JSON)
- **Micrometer/Prometheus** (métricas e monitoramento)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Kubernetes/GCP** (orquestração e deploy)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/contas/monitoramentos/{cdMonitoramentoSaldo}` | `MonitoramentoApiDelegateImpl` | Consulta um monitoramento específico por código |
| GET | `/v1/contas/monitoramentos/pendentes` | `MonitoramentoApiDelegateImpl` | Lista monitoramentos pendentes por conta |
| POST | `/v1/contas/monitoramentos` | `MonitoramentoApiDelegateImpl` | Cria um novo monitoramento de saldo |
| PUT | `/v1/contas/monitoramentos/{cdMonitoramentoSaldo}/bloqueios` | `MonitoramentoApiDelegateImpl` | Atualiza bloqueios de um monitoramento |
| DELETE | `/v1/contas/monitoramentos/{cdMonitoramentoSaldo}` | `MonitoramentoApiDelegateImpl` | Inativa um monitoramento (soft delete) |
| GET | `/v1/motivos-bloqueio/{cdMotivoBloqueio}` | `MonitoramentoApiDelegateImpl` | Consulta um motivo de bloqueio por código |

---

## 5. Principais Regras de Negócio

1. **Validação de Motivo de Bloqueio**: Ao criar um monitoramento, valida-se se o motivo de bloqueio está ativo e é monitorado.

2. **Validação de Valores**: Valores de bloqueio devem ser maiores que zero. Valor bloqueado não pode exceder o valor solicitado.

3. **Processamento de Crédito Recebido**: Ao receber um crédito, o sistema verifica monitoramentos pendentes e cria bloqueios automaticamente, respeitando prioridades e valores disponíveis.

4. **Marcação por NSU**: Créditos podem ser marcados com NSU (Número Sequencial Único de Lançamento) para associação direta com monitoramentos específicos.

5. **Priorização de Bloqueios**: Monitoramentos são processados por ordem de prioridade do motivo de bloqueio e data de criação.

6. **Conclusão de Monitoramento**: Quando o valor bloqueado iguala o valor solicitado e todos os bloqueios foram efetivados, o monitoramento é considerado concluído e uma mensagem é publicada.

7. **Soft Delete**: Monitoramentos não são excluídos fisicamente, apenas marcados como inativos (flag `FlAtivo = 'N'`).

8. **Validação de Divergências**: Ao atualizar bloqueios, valida-se que banco, tipo de conta e número da conta correspondem ao monitoramento.

9. **Chave Primária Duplicada**: Tratamento específico para evitar duplicação de bloqueios.

10. **Publicação de Eventos**: Eventos de criação e cancelamento de bloqueios são publicados em tópicos para processamento downstream.

---

## 6. Relação entre Entidades

**MonitoramentoSaldo** (1) ----< (N) **MonitoramentoSaldoBloqueado**
- Um monitoramento pode ter vários bloqueios associados

**MonitoramentoSaldo** (N) ----< (1) **MotivoBloqueio**
- Cada monitoramento possui um motivo de bloqueio

**Relacionamentos principais:**
- `MonitoramentoSaldo.cdMotivoBloqueio` → `MotivoBloqueio.cdMotivoBloqueio`
- `MonitoramentoSaldo.cdMonitoramentoSaldo` → `MonitoramentoSaldoBloqueado.cdMonitoramentoSaldo`

**Atributos de identificação de conta:**
- `cdBancoMonitoramentoSaldo` (código do banco)
- `nuContaCorrenteMonitoramento` (número da conta)
- `cdTipoConta` (tipo da conta)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| `CCBDContaCorrente.TbMonitoramentoSaldo` | Tabela | SELECT | Consulta monitoramentos de saldo por ID, dados da conta ou pendentes |
| `CCBDContaCorrente.TbMonitoramentoSaldoBloqueado` | Tabela | SELECT | Consulta bloqueios associados a um monitoramento |
| `CCBDContaCorrente.TbMotivoBloqueio` | Tabela | SELECT | Consulta motivos de bloqueio por código |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| `CCBDContaCorrente.TbMonitoramentoSaldo` | Tabela | INSERT | Criação de novos monitoramentos |
| `CCBDContaCorrente.TbMonitoramentoSaldo` | Tabela | UPDATE | Atualização de valor bloqueado e data de alteração |
| `CCBDContaCorrente.TbMonitoramentoSaldo` | Tabela | UPDATE (soft delete) | Inativação de monitoramento (FlAtivo = 'N') |
| `CCBDContaCorrente.TbMonitoramentoSaldoBloqueado` | Tabela | INSERT | Registro de bloqueios individuais |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `application.yml` | Leitura | Spring Boot | Configurações da aplicação |
| `logback-spring.xml` | Leitura | Logback | Configuração de logs em formato JSON |
| `openapi.yaml` | Leitura | Swagger Codegen | Especificação OpenAPI para geração de código |
| Arquivos `.avsc` (Avro schemas) | Leitura | Avro Maven Plugin | Schemas para serialização de mensagens |
| Arquivos `.sql` | Leitura | JDBI | Queries SQL para operações de banco |

---

## 10. Filas Lidas

- **Subscription**: `business-ccbd-base-atualiza-monitoramento-sub`
  - **Listener**: `MonitoramentoSaldoListener`
  - **Descrição**: Consome mensagens de atualização de monitoramento com informações de bloqueios criados

- **Subscription**: `business-ccbd-base-credito-bloqueado-sub`
  - **Listener**: `CreditoBloqueadoListener`
  - **Descrição**: Consome mensagens de crédito recebido para processamento de bloqueios automáticos

---

## 11. Filas Geradas

- **Tópico**: `business-ccbd-base-monitoramento-saldo` (default)
  - **Publisher**: `TopicDefaultPublisher`
  - **Descrição**: Publica mensagens de criação e cancelamento de bloqueios com atributo "etapa"

- **Tópico**: `business-ccbd-base-monitoramento-saldo-concluido`
  - **Publisher**: `MonitoramentoConcluidoPublisher`
  - **Descrição**: Publica mensagens quando um monitoramento é concluído ou deletado, com atributo "cdMotivoBloqueio"

---

## 12. Integrações Externas

1. **Google Cloud Pub/Sub**
   - **Tipo**: Mensageria assíncrona
   - **Descrição**: Consumo e publicação de eventos de bloqueio e crédito

2. **Banco de Dados MySQL (CCBDContaCorrente)**
   - **Tipo**: Banco de dados relacional
   - **Descrição**: Persistência de monitoramentos, bloqueios e motivos

3. **Serviço de Autenticação OAuth2/JWT**
   - **Tipo**: API externa
   - **Descrição**: Validação de tokens JWT para autenticação de requisições

4. **Prometheus/Grafana**
   - **Tipo**: Monitoramento
   - **Descrição**: Coleta de métricas e visualização (configuração local para desenvolvimento)

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com camadas bem definidas (domain, application, infrastructure)
- Uso adequado de padrões como Repository, Service e Mapper
- Tratamento de exceções customizadas e específicas de negócio
- Configuração externalizada e uso de profiles
- Documentação OpenAPI bem estruturada
- Uso de tecnologias modernas e adequadas ao contexto
- Logs estruturados em JSON
- Testes unitários presentes (embora não enviados)

**Pontos de Melhoria:**
- Presença de código deprecated (`@Deprecated` em métodos ainda utilizados)
- Alguns métodos com múltiplas responsabilidades (ex: `CreditoRecebidoService.processarCreditoRecebido`)
- Falta de comentários em lógicas de negócio mais complexas
- Uso de strings mágicas em alguns pontos (ex: "S", "N" para flags)
- Alguns métodos poderiam ser quebrados em métodos menores para melhor legibilidade
- Tratamento genérico de exceções em alguns listeners (catch Exception)
- Falta de validação de nulos em alguns pontos críticos

---

## 14. Observações Relevantes

1. **Arquitetura Hexagonal**: O projeto segue princípios de arquitetura hexagonal com separação clara entre domínio, aplicação e infraestrutura.

2. **Mensageria Assíncrona**: O sistema é fortemente baseado em eventos, utilizando Pub/Sub para comunicação assíncrona e desacoplamento.

3. **Multi-ambiente**: Configurações específicas para ambientes DES, UAT e PRD através de profiles e ConfigMaps.

4. **Segurança**: Implementa OAuth2 com JWT, com endpoints públicos configuráveis.

5. **Observabilidade**: Integração com Prometheus para métricas e logs estruturados em JSON para facilitar análise.

6. **Soft Delete**: Padrão de exclusão lógica para manter histórico de monitoramentos.

7. **MDC (Mapped Diagnostic Context)**: Uso de MDC para rastreamento de requisições através de "ticket".

8. **Avro para Serialização**: Uso de Apache Avro para definição de schemas de mensagens, garantindo compatibilidade e evolução de contratos.

9. **JDBI ao invés de JPA**: Escolha de JDBI para acesso a dados, oferecendo mais controle sobre SQL e melhor performance.

10. **Kubernetes Ready**: Configuração de probes (liveness/readiness) e recursos adequados para deploy em Kubernetes/GCP.