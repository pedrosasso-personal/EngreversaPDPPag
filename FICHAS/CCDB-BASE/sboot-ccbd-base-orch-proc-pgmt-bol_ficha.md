# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-ccbd-base-orch-proc-pgmt-bol** é um serviço de orquestração stateless desenvolvido em Java com Spring Boot, responsável por processar pagamentos de boletos (tributos, consumo e duplicatas) no contexto do Banco Votorantim. 

O sistema consome mensagens de uma fila IBM MQ contendo dados de boletos a serem pagos, realiza a autenticação via token OAuth2, envia as solicitações de pagamento para APIs externas (CASH) de acordo com o tipo de boleto, e atualiza o status do pagamento em um sistema interno. Utiliza Apache Camel para orquestração de fluxos e implementa padrões de retry em caso de falhas de comunicação.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal que inicializa a aplicação Spring Boot |
| `ProcessarPgmtBoletoListener` | Listener JMS que consome mensagens da fila e inicia o processamento |
| `ProcessarPgmtBoletoService` | Serviço de domínio que direciona o fluxo para a rota Camel apropriada (duplicata ou tributo/consumo) |
| `ProcessarPgmtBoletoRouter` | Rota Camel para processamento de pagamentos de tributos e consumo |
| `ProcessarPgmtBoletoDuplicataRouter` | Rota Camel para processamento de pagamentos de duplicatas |
| `GerarTokenOutboundImpl` | Implementação responsável por gerar token OAuth2 para autenticação nas APIs |
| `EnviarPagamentoOutboundImpl` | Implementação que envia pagamentos de tributos e consumo para API CASH |
| `EnviarPagamentoDuplicataOutboundImpl` | Implementação que envia pagamentos de duplicatas para API CASH |
| `AtualizarPagamentoOutboundImpl` | Implementação que atualiza o status do pagamento no sistema interno |
| `CamelContextWrapper` | Wrapper do contexto Camel para gerenciamento de rotas |
| `AppProperties` | Classe de configuração com propriedades da aplicação |
| `Boleto` | Entidade de domínio representando um boleto a ser pago |
| `TipoPagamentoEnum` | Enum que define os tipos de pagamento (duplicata, tributo, concessionária) |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Apache Camel 3.0.1** (orquestração de rotas e integração)
- **IBM MQ** (mensageria - consumo de filas)
- **Spring JMS** (integração com filas JMS)
- **RestTemplate** (cliente HTTP para chamadas REST)
- **Lombok** (redução de boilerplate)
- **Springfox/Swagger 3.0.0** (documentação de APIs)
- **Spring Actuator** (monitoramento e health checks)
- **Micrometer/Prometheus** (métricas)
- **Logback** (logging)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **OpenShift/Kubernetes** (orquestração de containers)

---

## 4. Principais Endpoints REST

Não se aplica. O sistema não expõe endpoints REST próprios - ele atua como consumidor de filas e cliente de APIs externas.

---

## 5. Principais Regras de Negócio

1. **Roteamento por tipo de pagamento**: O sistema identifica o tipo de pagamento através do código de liquidação e direciona para a rota apropriada (duplicata vs tributo/consumo).

2. **Autenticação OAuth2**: Antes de enviar qualquer pagamento, o sistema gera um token de acesso via OAuth2 client credentials flow.

3. **Diferenciação de remetente por forma de pagamento**: Para pagamentos com cartão de crédito, utiliza-se o CNPJ do Banco Digital como remetente e o CNPJ da BV Financeira como CNPJ Fintech. Para débito em conta, utiliza-se os dados da conta balde.

4. **Atualização de status**: Após envio bem-sucedido do pagamento, o sistema atualiza o status para "EM PROCESSAMENTO" (código 2) no sistema interno.

5. **Retry em caso de falha de comunicação**: Quando ocorre `ComunicacaoException`, a mensagem é repostada na fila para nova tentativa de processamento.

6. **Validação de retorno das APIs**: O sistema valida se o código de status do protocolo retornado é "00" (sucesso), caso contrário lança exceção.

7. **Valores padrão**: Define valores padrão para campos obrigatórios quando não informados (ex: data de vencimento "2050-12-31", valores de desconto/juros/multa zerados).

---

## 6. Relação entre Entidades

**Entidade Principal: Boleto**
- Contém informações do pagamento (valores, datas, códigos)
- Possui relacionamento com **Beneficiario** (remetente e favorecido)
- Gera **PagamentoTributoConsumo** ou **PagamentoDuplicata** dependendo do tipo
- Recebe **Token** para autenticação
- Retorna **SolicitacaoPagamento** com **Protocolo** após processamento

**Relacionamentos:**
- `Boleto` 1 ---> 1 `Beneficiario` (remetente)
- `Boleto` 1 ---> 1 `Beneficiario` (favorecido)
- `Boleto` 1 ---> 1 `Token` (gerado)
- `Boleto` 1 ---> 1 `PagamentoTributoConsumo` OU `PagamentoDuplicata` (transformação)
- `PagamentoTributoConsumo/PagamentoDuplicata` 1 ---> 1 `SolicitacaoPagamento` (retorno)
- `SolicitacaoPagamento` 1 ---> 1 `Protocolo` (para duplicatas)

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação (leitura/gravação) | Local/Classe Responsável | Breve Descrição |
|-----------------|----------------------------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot | Arquivo de configuração da aplicação com propriedades por ambiente |
| logback-spring.xml | leitura | Logback | Configuração de logging da aplicação |

---

## 10. Filas Lidas

**Fila:** `QL.CCBD.LIQ_PAGMT_CONTAS_DIG.INT`

- **Tipo:** IBM MQ
- **Classe Consumidora:** `ProcessarPgmtBoletoListener`
- **Formato da Mensagem:** JSON convertido para objeto `Boleto`
- **Descrição:** Fila de entrada contendo solicitações de pagamento de boletos a serem processados
- **Configuração:** Queue Manager `QM.DIG.01`, Canal `CCBD.SRVCONN`

---

## 11. Filas Geradas

**Fila:** `QL.CCBD.LIQ_PAGMT_CONTAS_DIG.INT` (mesma fila de entrada)

- **Tipo:** IBM MQ
- **Classe Produtora:** `ProcessarPgmtBoletoListener`
- **Descrição:** Em caso de `ComunicacaoException`, a mensagem original é repostada na mesma fila para retry
- **Mecanismo:** Utiliza `JmsTemplate.convertAndSend()`

---

## 12. Integrações Externas

| Sistema/API | Tipo | Descrição |
|-------------|------|-----------|
| **API Gateway - Token OAuth2** | REST | Geração de token de acesso via client credentials. Endpoint: `/auth/oauth/v2/token` |
| **API CASH - Pagamento Tributo e Consumo** | REST | Envio de pagamentos de tributos e consumo. Endpoint: `/v1/atacado/gestao/pagamento-tributo-consumo/incluir` |
| **API CASH - Pagamento Duplicata** | REST | Envio de pagamentos de duplicatas/boletos de cobrança. Endpoint: `/v1/atacado/boleto/pagamento` |
| **Atom - Pagamento Tributo Boleto** | REST | Atualização do status do pagamento no sistema interno. Endpoint: `/v1/pagamento-boleto/efetivar` |
| **IBM MQ** | Mensageria | Consumo e publicação de mensagens na fila de pagamentos |

**Observações:**
- Todas as APIs externas utilizam autenticação Bearer Token
- URLs variam por ambiente (des, qa, uat, prd)
- Comunicação via HTTPS para APIs externas

---

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (application, domain, common)
- Uso adequado de padrões como Ports & Adapters (Hexagonal Architecture)
- Implementação de tratamento de exceções customizadas
- Uso de Lombok para reduzir boilerplate
- Configuração externalizada por ambiente
- Implementação de health checks e métricas
- Uso de Apache Camel para orquestração de fluxos complexos

**Pontos de Melhoria:**
- Falta de documentação inline (JavaDoc) nas classes e métodos
- Método `popularPagamentoTributoConsumo` muito extenso e com lógica condicional que poderia ser refatorada
- Uso de valores hardcoded em alguns pontos (ex: código status 2, filial 1)
- Tratamento genérico de exceções em alguns pontos (`catch (Exception e)`)
- Falta de validações de entrada mais robustas
- Logs poderiam ser mais estruturados e informativos
- Ausência de testes unitários nos arquivos analisados (marcados como NAO_ENVIAR)
- Configuração de retry poderia ser mais sofisticada (atualmente apenas reposta na fila)

---

## 14. Observações Relevantes

1. **Arquitetura Modular**: O projeto está organizado em três módulos Maven (application, domain, common), seguindo boas práticas de separação de responsabilidades.

2. **Estratégia de Retry**: O sistema implementa retry simples repostando mensagens na fila em caso de falhas de comunicação, mas não há controle de número máximo de tentativas ou dead letter queue.

3. **Segurança**: Utiliza bibliotecas de segurança BV (`sboot-arqt-base-security-*`) para autenticação e autorização, além de trilha de auditoria.

4. **Observabilidade**: Implementa Actuator com Prometheus para métricas, facilitando monitoramento em ambientes Kubernetes/OpenShift.

5. **Multi-ambiente**: Configuração preparada para múltiplos ambientes (local, des, qa, uat, prd) com variáveis externalizadas.

6. **Containerização**: Dockerfile otimizado usando OpenJ9 Alpine para reduzir tamanho da imagem.

7. **Infraestrutura como Código**: Arquivo `infra.yml` define toda a configuração de deployment no OpenShift/Kubernetes.

8. **Dependência de APIs Externas**: O sistema é fortemente dependente da disponibilidade das APIs CASH e do sistema Atom, sem mecanismos de circuit breaker aparentes.

9. **Conversão de Códigos**: Implementa enums para conversão de códigos de banco e tipo de conta entre diferentes padrões.

10. **Auditoria**: Integração com biblioteca de trilha de auditoria BV para rastreabilidade de operações.