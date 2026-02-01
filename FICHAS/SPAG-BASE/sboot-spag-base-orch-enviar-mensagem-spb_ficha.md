# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema orquestrador responsável por processar e enviar mensagens de pagamento para o Sistema de Pagamentos Brasileiro (SPB). O sistema recebe solicitações de integração com o SPB, valida as informações, monta as mensagens no formato adequado conforme o catálogo do Banco Central, e publica essas mensagens em tópicos Kafka para processamento. Também consome mensagens de status de retorno do SPB via Kafka e publica notificações de confirmação via Google Cloud Pub/Sub.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal Spring Boot que inicializa a aplicação |
| **ClientRouter** | Roteador Camel que recebe requisições REST de integração SPB |
| **EnvioMensagemSpbRouter** | Roteador principal que orquestra o fluxo de envio de mensagens ao SPB |
| **StatusEnvioMensagemRouter** | Processa mensagens de status recebidas do SPB via Kafka |
| **ConsultarTedSPBCoreRouter** | Roteador para consulta de movimentos no SPB Core |
| **LancamentoServiceImpl** | Serviço que processa a movimentação e gera o objeto do catálogo BCB |
| **SpbAtomMensageriaServiceImpl** | Serviço que consulta movimentos no sistema Atom Mensageria |
| **KafkaConsumer** | Listener que consome mensagens de status do SPB via Kafka |
| **EnvioMensagemSPBRepositoryImpl** | Repositório que publica mensagens de envio no tópico Kafka |
| **RetornoPagamentoRepositoryImpl** | Repositório que publica retornos de pagamento no Pub/Sub |
| **ParamsMapper** | Mapper que direciona para a implementação correta conforme operação SPB |
| **MovimentacaoDTOMapper** | Converte DicionarioPagamento para MovimentacaoDTO |
| **DicionarioPagamentoMapper** | Converte representações REST para domínio DicionarioPagamento |

---

## 3. Tecnologias Utilizadas

- **Spring Boot** 2.x (framework base)
- **Apache Camel** 3.x (orquestração e roteamento)
- **Apache Kafka** (mensageria assíncrona - Confluent Cloud)
- **Google Cloud Pub/Sub** (publicação de eventos de retorno)
- **Avro** (serialização de mensagens Kafka)
- **Spring Cloud GCP** (integração com Google Cloud Platform)
- **Spring Security OAuth2** (autenticação JWT)
- **Logback** com formato JSON (logging estruturado)
- **MapStruct** (mapeamento de objetos)
- **OpenAPI/Swagger** (documentação de APIs)
- **Hibernate Validator** (validação de dados)
- **Lombok** (redução de boilerplate)
- **JUnit 5 + Mockito** (testes unitários)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Kubernetes/OpenShift** (orquestração de containers)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /integracaoSpbCore | ClientRouter (Camel REST) | Recebe solicitação de integração com SPB e processa envio de mensagem |
| GET | /movimento/consultarByCdMovimentoOrigem/{cdMovimentoOrigem} | ConsultarTedSPBCoreRouter (Camel REST) | Consulta movimento no SPB Core pelo código de movimento origem |
| GET | /actuator/health | Spring Actuator | Endpoint de health check |
| GET | /swagger-ui/index.html | SpringDoc OpenAPI | Documentação interativa da API |

---

## 5. Principais Regras de Negócio

1. **Validação de Operações SPB**: O sistema valida diferentes tipos de operações (OPPAG, OPSTR) e determina o tipo de mensagem BCB adequado (PAG0108, STR0006, etc.) com base em critérios como tipo de conta, tipo de liquidação ITP, código de transação e finalidade.

2. **Roteamento por Tipo de Liquidação**: Mensagens são roteadas para CIP (código 31) ou STR (códigos 32, 57) conforme o tipo de liquidação configurado.

3. **Tratamento de Contas Especiais**: Lógica específica para contas tipo "PG" (Pagamento), "IF" (Instituição Financeira), "CI" (Conta de Investimento), "CO" (Conta Ordem) e "CT" (Conta Transitória).

4. **Validação de Finalidade**: Verifica se o código de finalidade informado é válido para o tipo de mensagem SPB sendo gerada.

5. **Tratamento de Portabilidade**: Identifica e processa operações de portabilidade de crédito consignado (INSS).

6. **Processamento de Ocorrências**: Captura e estrutura ocorrências/erros durante o processamento, retornando-as de forma padronizada.

7. **Enriquecimento de Movimento**: Adiciona informações de ação e número de controle SPB ao movimento antes do envio.

8. **Controle de Fluxo de Retorno**: Encerra o fluxo de retorno para mensagens específicas (PAG0111, STR0010) que representam devoluções de TED.

9. **Formatação de CPF/CNPJ**: Padroniza documentos com zeros à esquerda conforme tipo de pessoa (Física ou Jurídica).

10. **Geração de Número de Controle**: Monta número de controle único combinando tipo de operação, data e código de lançamento.

11. **Filtragem de Mensagens**: Processa apenas mensagens originadas do sistema SPAG-BASE e dos tipos PAG ou STR.

---

## 6. Relação entre Entidades

**DicionarioPagamento** (entidade central):
- Contém todos os dados da transação de pagamento
- Possui relacionamento 1:1 com **DicionarioPagamentoListaOcorrencia**
- É convertido para **MovimentacaoDTO** para processamento interno
- É mapeado para objetos do catálogo BCB (PAG0108, STR0006, etc.)

**MovimentacaoDTO**:
- Representa dados de movimentação processados internamente
- Contém relacionamento 1:1 com **ParametrosGeraisDTO**
- É utilizado para gerar objetos específicos do catálogo BCB

**EnvioMensagemSPB** (Avro):
- Mensagem publicada no Kafka para envio ao SPB
- Contém dados essenciais da mensagem e JSON serializado

**StatusEnvioMensagemSPB** (Avro):
- Mensagem consumida do Kafka com status de processamento SPB
- Convertida para **StatusEnvioMensagemSPBDomain** para processamento

**RetornoSPB**:
- Representa retorno de processamento SPB
- Publicado no Google Pub/Sub para notificação de sistemas consumidores

**Movimento**:
- Representa consulta de movimento no SPB Core
- Enriquecido com informações de ação e controle SPB

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|--------------------------|-----------------|
| logback-spring.xml | Leitura | /usr/etc/log/ (ConfigMap montado) | Configuração de logging em formato JSON |
| openapi.yaml | Leitura | src/main/resources/swagger/ | Especificação OpenAPI da API REST |
| sboot-spbb-base-atom-mensageria.yaml | Leitura | src/main/resources/swagger/consumers/ | Contrato do cliente Atom Mensageria |
| EnvioMensagemSPB.avsc | Leitura | src/main/resources/avro/ | Schema Avro para mensagens de envio SPB |
| StatusEnvioMensagemSPB.avsc | Leitura | src/main/resources/avro/ | Schema Avro para status de mensagens SPB |
| application.yml | Leitura | src/main/resources/ | Configurações da aplicação |
| layers.xml | Leitura | src/main/resources/ | Configuração de camadas Docker multi-layer |

---

## 10. Filas Lidas

**Kafka:**
- **Tópico**: `spbb-base-status-envio-mensagem`
- **Consumer Group**: `sboot-spag-base-orch-enviar-mensagem-spb`
- **Formato**: Avro (StatusEnvioMensagemSPB)
- **Descrição**: Consome mensagens de status de processamento de mensagens SPB enviadas ao Banco Central
- **Classe Responsável**: KafkaConsumer
- **Filtros**: Processa apenas mensagens com origem "SPAG-BASE" e tipos "PAG" ou "STR"

---

## 11. Filas Geradas

**Kafka:**
- **Tópico**: `spbb-base-envio-mensagem-spb`
- **Formato**: Avro (EnvioMensagemSPB)
- **Descrição**: Publica mensagens de pagamento formatadas para envio ao SPB
- **Classe Responsável**: EnvioMensagemSPBRepositoryImpl

**Google Cloud Pub/Sub:**
- **Tópico**: `business-spag-base-confirmacao-spb`
- **Formato**: JSON (RetornoSPB)
- **Descrição**: Publica notificações de retorno de processamento SPB para sistemas consumidores
- **Classe Responsável**: RetornoPagamentoRepositoryImpl
- **Configuração**: PubSubOutputChannelConfiguration

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **sboot-spbb-base-atom-mensageria** | API REST | Serviço para consulta de movimentos no SPB Core. Endpoint: `/v1/movimentos` |
| **Confluent Cloud Kafka** | Mensageria | Cluster Kafka gerenciado para publicação e consumo de mensagens SPB |
| **Confluent Schema Registry** | Serviço | Registro de schemas Avro para validação de mensagens Kafka |
| **Google Cloud Pub/Sub** | Mensageria | Publicação de eventos de retorno de pagamento |
| **API Gateway BV** | Autenticação | Obtenção de tokens JWT para autenticação em APIs internas (OAuth2 Client Credentials) |
| **Catálogo de Mensagens BCB** | Biblioteca | Biblioteca interna (sbootlib-spbb-base-catalogo-mensagens v0.0.38) para geração de mensagens no formato do Banco Central |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com uso de camadas (router, processor, service, port, mapper)
- Uso adequado de padrões como Strategy (ParamMapperInterface) e Repository
- Cobertura de testes unitários presente
- Uso de Lombok reduzindo boilerplate
- Configurações externalizadas e separadas por ambiente
- Logging estruturado em JSON
- Uso de MapStruct para mapeamento de objetos
- Tratamento de exceções customizado e estruturado

**Pontos de Melhoria:**
- Classes de processamento (Processor) com lógica complexa que poderia ser melhor modularizada
- Classe `ValidarOperacaoMethodUtils` com métodos muito extensos e complexos (alta complexidade ciclomática)
- Uso excessivo de variáveis estáticas booleanas em `ValidarOperacaoMethodUtils`
- Alguns métodos com muitos parâmetros (ex: `setOperacao` com 4 parâmetros)
- Falta de documentação JavaDoc em classes e métodos principais
- Alguns nomes de variáveis poderiam ser mais descritivos (ex: `dto`, `dic`)
- Lógica de negócio misturada com mapeamento em algumas classes
- Testes poderiam ter melhor cobertura de cenários de exceção
- Algumas classes de operação (OPPAG001, OPPAG004, etc.) apenas lançam exceção "não implementado"

---

## 14. Observações Relevantes

1. **Arquitetura Multi-Camadas**: O sistema utiliza uma arquitetura bem definida com separação clara entre camadas de apresentação (routers), processamento (processors), serviço (service), porta (port) e domínio (domain).

2. **Processamento Assíncrono Bidirecional**: O sistema opera em dois fluxos principais:
   - **Fluxo de Envio**: REST → Validação → Geração Mensagem BCB → Publicação Kafka
   - **Fluxo de Retorno**: Consumo Kafka → Processamento Status → Publicação Pub/Sub

3. **Suporte a Múltiplas Operações SPB**: O sistema suporta 24 tipos diferentes de operações (OPPAG e OPSTR), cada uma gerando um tipo específico de mensagem BCB (PAG0108, PAG0111, STR0006, STR0010, etc.).

4. **Integração com Catálogo BCB**: Utiliza biblioteca interna que encapsula as complexidades do catálogo de mensagens do Banco Central, incluindo validação de schemas e conversão para XML/JSON.

5. **Configuração por Ambiente**: Possui configurações específicas para ambientes DES, UAT e PRD, incluindo diferentes clusters Kafka e projetos GCP.

6. **Segurança**: Implementa autenticação OAuth2 JWT com validação de tokens via API Gateway do Banco Votorantim.

7. **Observabilidade**: Configurado com Spring Actuator, Micrometer, Prometheus e OpenTelemetry para monitoramento e rastreamento distribuído.

8. **Tratamento Especial para Fintech**: Possui lógica específica para processar transações originadas de fintechs (ex: Neon - CNPJ 20855875000182).

9. **Containerização Otimizada**: Utiliza estratégia de multi-layer Docker para otimizar builds e deploys, separando dependências em camadas específicas.

10. **Resiliência**: Implementa tratamento de exceções em múltiplos níveis com processors dedicados para diferentes tipos de erro.

11. **Versionamento de Mensagens**: Mantém controle de versão do catálogo BCB utilizado para geração das mensagens.

12. **Validações de Negócio**: Implementa validações complexas de finalidade, tipo de conta, ISPB, e outros atributos específicos do domínio de pagamentos.