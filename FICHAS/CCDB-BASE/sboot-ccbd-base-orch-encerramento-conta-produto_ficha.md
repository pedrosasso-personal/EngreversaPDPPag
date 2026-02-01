# Ficha Técnica do Sistema

## 1. Descrição Geral

Este componente é um **Orquestrador de Encerramento de Produtos** desenvolvido em Java com Spring Boot. Seu objetivo principal é gerenciar o encerramento de produtos relacionados às contas de clientes do Banco Votorantim. 

Atualmente, o componente é responsável pelo encerramento de cartões (DXC) quando uma conta é encerrada. Ele escuta mensagens publicadas no tópico Google Cloud Pub/Sub `business-ccbd-base-encerramento-conta` e orquestra o processo de encerramento através de chamadas a serviços externos, incluindo:
- Listagem de cartões associados à conta
- Bloqueio de cartões digitais
- Cancelamento de contas de cartão
- Encerramento de cartões no sistema DXC (via componente CART)

O componente utiliza Apache Camel para orquestração de fluxos e integra-se com diversos serviços através de APIs REST.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot que inicializa a aplicação |
| `CartPubSubListener` | Listener que consome mensagens do Pub/Sub para encerramento de contas |
| `EncerramentoContaDxcService` | Serviço de domínio que orquestra o encerramento de conta DXC via Camel |
| `DeletaCartRouter` | Rota Camel que define o fluxo de encerramento de cartões |
| `TokenRouter` | Rota Camel para geração de tokens de autenticação |
| `CamelContextWrapper` | Wrapper do contexto Camel para gerenciamento de rotas |
| `BloqueioCartaoDigitalRepositoryImpl` | Implementação de chamada ao serviço de bloqueio de cartões |
| `CancelamentoContaCartaoRepositoryImpl` | Implementação de chamada ao serviço de cancelamento de conta cartão |
| `ListaCartoesRepositoryImpl` | Implementação de chamada ao serviço de listagem de cartões |
| `DeletaCartRepositoryImpl` | Implementação de chamada ao serviço de encerramento Cart/DXC |
| `TokenRepositoryImpl` | Implementação de geração de token JWT BV |
| `EncerramentoContaProdutoConfiguration` | Configuração de beans Spring e Camel |
| `PubSubConfiguration` | Configuração do Google Cloud Pub/Sub |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Spring Cloud GCP** (integração com Google Cloud Pub/Sub)
- **Apache Camel 3.0.1** (orquestração de fluxos)
- **Spring Security OAuth2** (autenticação e autorização)
- **RestTemplate** (cliente HTTP para chamadas REST)
- **Lombok** (redução de boilerplate)
- **Springfox Swagger 3.0.0** (documentação de API)
- **Micrometer/Prometheus** (métricas e monitoramento)
- **JUnit 5 + Mockito** (testes unitários)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Logback** (logging com formato JSON)
- **Google Cloud Pub/Sub** (mensageria)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/encerra-conta-dxc` | `CartPubSubController` | Endpoint de teste para encerramento de conta DXC (disponível apenas em ambientes local, des e uat) |

**Observação:** Este componente é primariamente orientado a eventos (event-driven) via Pub/Sub, com endpoint REST disponível apenas para testes em ambientes não produtivos.

---

## 5. Principais Regras de Negócio

1. **Consumo de Mensagens de Encerramento**: O sistema escuta mensagens de encerramento de conta publicadas no tópico Pub/Sub e processa automaticamente.

2. **Validação de Fluxo Completo (Puro Débito)**: Verifica se a conta é "puro débito" para determinar se deve executar o fluxo completo de tratamento de cartões.

3. **Listagem de Cartões Ativos**: Busca todos os cartões associados à conta, filtrando apenas cartões com status de débito positivo (ativos).

4. **Bloqueio de Cartões**: Para cartões ativos encontrados, realiza o bloqueio automático com status 31 e motivo 141.

5. **Cancelamento de Conta Cartão**: Cancela a conta do cartão no sistema DXC com status 87 (Cancelado por solicitação do cliente) e motivo 108.

6. **Encerramento no Sistema Cart/DXC**: Aciona o componente externo para encerramento definitivo dos cartões.

7. **Tratamento de Erros com Retry**: Implementa retry automático (3 tentativas com delay de 3 segundos) para geração de tokens.

8. **Rastreabilidade**: Gera hash único de rastreamento para cada operação, facilitando auditoria e troubleshooting.

9. **Processamento Assíncrono**: Utiliza thread pool configurável para processamento paralelo de mensagens.

10. **Acknowledgement Manual**: Controla manualmente o ACK das mensagens Pub/Sub para garantir processamento completo.

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **MensagemEncerramentoConta**: Representa a mensagem recebida do Pub/Sub contendo dados da conta a ser encerrada (cpfCnpj, codigoBanco, codigoAgencia, numeroConta, puroDebito, hashRastreioLog).

- **EncerramentoConta**: Entidade de domínio que encapsula os dados de encerramento processados.

- **Cartoes**: Coleção de cartões associados a uma conta.

- **Cartao**: Representa um cartão individual com seus atributos (quina, modalidade, tipo, situação de pagamento, status).

- **Quina**: Identificação única do cartão no sistema (emissor, filial, produto, contaCartao, correlativo).

- **MensagemCart**: Resposta do serviço de encerramento Cart/DXC.

**Relacionamentos:**
- Uma `MensagemEncerramentoConta` é transformada em `EncerramentoConta`
- Um `EncerramentoConta` pode ter múltiplos `Cartoes`
- Cada `Cartao` possui uma `Quina` (identificação única)
- O processamento retorna uma `MensagemCart` com o resultado

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

**Observação:** Este componente não acessa diretamente banco de dados. Todas as operações são realizadas via APIs REST de outros serviços.

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

**Observação:** Este componente não atualiza diretamente banco de dados. As atualizações são realizadas através de chamadas a serviços externos que gerenciam suas próprias bases de dados.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Descrição |
|-----------------|----------|-------------------------|-----------|
| `application.yml` | Leitura | `src/main/resources` | Arquivo de configuração da aplicação com propriedades de ambiente |
| `logback-spring.xml` | Leitura | `src/main/resources` e `/usr/etc/log` | Configuração de logging em formato JSON |
| `Dockerfile` | Leitura | `docker/` | Definição da imagem Docker para deploy |
| Logs da aplicação | Gravação | Console/STDOUT | Logs estruturados em JSON para observabilidade |

---

## 10. Filas Lidas

**Google Cloud Pub/Sub - Subscription:**
- **Nome da Subscription**: `business-ccbd-base-encerramento-conta-cart-sub`
- **Tópico Origem**: `business-ccbd-base-encerramento-conta`
- **Tipo de Mensagem**: `MensagemEncerramentoConta` (JSON)
- **Modo de Acknowledgement**: Manual
- **Classe Consumidora**: `CartPubSubListener`
- **Descrição**: Recebe mensagens de encerramento de contas para processar o encerramento de cartões associados

---

## 11. Filas Geradas

não se aplica

**Observação:** Este componente não publica mensagens em filas. Ele apenas consome mensagens do Pub/Sub e realiza chamadas síncronas a APIs REST.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **sboot-cart-base-orch-encerramento-conta-dxc** | API REST | Serviço de encerramento de cartões no sistema DXC |
| **sboot-cart-svhp-orch-lista-cartoes** | API REST | Serviço de listagem de cartões associados a uma conta |
| **sboot-cart-base-orch-bloq-desbloq-cartao-bd** | API REST | Serviço de bloqueio/desbloqueio de cartões digitais |
| **sboot-cart-base-orch-cancelamento-conta** | API REST | Serviço de cancelamento de conta cartão no DXC |
| **API Gateway BV** | API REST OAuth2 | Serviço de geração de tokens JWT para autenticação |
| **Google Cloud Pub/Sub** | Mensageria | Plataforma de mensageria para consumo de eventos de encerramento |

**Observações:**
- Todas as integrações REST utilizam autenticação via token JWT obtido do API Gateway
- As URLs dos serviços são configuráveis via variáveis de ambiente
- Implementa tratamento de erros e logging detalhado para cada integração

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades em módulos (common, domain, application)
- Uso adequado de padrões de projeto (Repository, Service, Builder)
- Implementação de testes unitários com boa cobertura
- Uso de Lombok para redução de boilerplate
- Configuração adequada de logging estruturado (JSON)
- Implementação de retry e tratamento de erros
- Rastreabilidade através de hash único
- Documentação README clara sobre o propósito do componente

**Pontos de Melhoria:**
- Alguns testes unitários são superficiais (apenas verificam `assertNotNull`)
- Falta de testes de integração mais robustos
- Uso de `RestTemplate` (deprecated) ao invés de `WebClient`
- Configurações hardcoded em alguns pontos (ex: status de bloqueio 31, motivo 141)
- Falta de validação mais robusta de entrada de dados
- Comentários em código poderiam ser mais descritivos
- Algumas classes de exceção customizadas poderiam ter mais contexto
- Falta de circuit breaker para chamadas externas
- Configuração de thread pool poderia ser mais detalhada
- Alguns nomes de variáveis em português misturados com inglês

**Recomendações:**
1. Migrar de `RestTemplate` para `WebClient` (reativo)
2. Implementar circuit breaker (Resilience4j)
3. Adicionar validações com Bean Validation
4. Melhorar testes com cenários mais complexos
5. Padronizar nomenclatura (inglês ou português)
6. Adicionar métricas customizadas de negócio
7. Implementar health checks mais detalhados

---

## 14. Observações Relevantes

1. **Transição de Responsabilidades**: Este componente está em processo de transição. Anteriormente era responsável por encerrar Pix, DDA e Cartões. Atualmente encerra apenas Cartões, e no futuro esta responsabilidade será transferida para o domínio CART.

2. **Ambientes**: O endpoint REST está disponível apenas em ambientes `local`, `des` e `uat`, não sendo exposto em produção por questões de segurança.

3. **Configuração por Ambiente**: Utiliza arquivos de configuração específicos por ambiente (`logback-spring.xml` em `/usr/etc/log` para ambientes des/uat/prd).

4. **Segurança**: Implementa OAuth2 Resource Server com validação de JWT via JWK Set URI.

5. **Observabilidade**: Expõe métricas Prometheus na porta 9090 através do Spring Actuator.

6. **Containerização**: Utiliza imagem base customizada do Banco Votorantim (`pacotedocker-atle-base-java11`).

7. **Versionamento**: Versão atual 0.14.0, seguindo versionamento semântico.

8. **Arquitetura**: Segue arquitetura hexagonal com separação clara entre camadas de apresentação, domínio e infraestrutura.

9. **Processamento Assíncrono**: Configurado com thread pool de 2-5 threads e fila de 50 mensagens para processamento paralelo.

10. **Dependências Internas**: Utiliza bibliotecas internas do Banco Votorantim para auditoria, segurança e tratamento de erros.

11. **Documentação Técnica**: Possui links para Confluence com documentação detalhada dos fluxos de negócio.

12. **Qualidade de Código**: Implementa testes de arquitetura com ArchUnit para garantir conformidade com padrões estabelecidos.