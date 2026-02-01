# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema orquestrador responsável por receber e processar mensagens do SPB (Sistema de Pagamentos Brasileiro) provenientes das câmaras de liquidação PAG (Pagamentos) e STR (Sistema de Transferência de Reservas). O sistema consome mensagens de um tópico Kafka, realiza o mapeamento e transformação dos dados conforme o tipo de mensagem (PAG0107R2, PAG0108R2, STR0004R2, STR0005R2, etc.), consulta informações cadastrais de bancos, e publica os eventos processados em tópicos do Google Pub/Sub para consumo por outros sistemas. Também trata devoluções, confirmações e mensagens não processadas, enviando-as para filas específicas.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application.java** | Classe principal que inicializa a aplicação Spring Boot com suporte ao catálogo de mensagens BCB |
| **KafkaConsumer.java** | Listener que consome mensagens do Kafka (tópico de mensagens recebidas do SPB) e aciona o processamento |
| **RecebimentoService.java** | Serviço principal que orquestra o processamento das mensagens: identifica o tipo, mapeia para CaixaEntradaDTO, transforma em TedInRepresentation e envia para Pub/Sub |
| **TransferenciaService.java** | Serviço responsável por enviar as transferências (TED In), confirmações e mensagens não processadas para os tópicos Pub/Sub |
| **CadastroRepository.java** | Interface de repositório para consulta de dados cadastrais de bancos (código COMPE a partir do ISPB) |
| **CadastroRepositoryImpl.java** | Implementação do repositório que consulta a API externa (sboot-sitp-base-atom-integrar-pagamento) para obter dados de bancos |
| **EnvioTransferenciaRepository.java** | Interface de repositório para envio de mensagens ao Pub/Sub |
| **EnvioTransferenciaRepositoryImpl.java** | Implementação que utiliza os publishers (TedInPublisher, ConfirmationPublisher, MensagemNaoProcessadaPublisher) para publicar no Pub/Sub |
| **ICaixaEntradaDTO.java** | Interface para mapeamento de mensagens SPB em CaixaEntradaDTO |
| **PAG0107R2.java, PAG0108R2.java, PAG0111R2.java, etc.** | Implementações específicas de mapeamento para cada tipo de mensagem PAG |
| **STR0004R2.java, STR0005R2.java, STR0006R2.java, etc.** | Implementações específicas de mapeamento para cada tipo de mensagem STR |
| **MensagemDesconhecida.java** | Implementação padrão que lança exceção quando a mensagem não é mapeada |
| **CaixaEntradaDTO.java** | DTO que representa os dados de entrada da caixa (lançamento financeiro) com ajustes e validações |
| **TedInRepresentation.java** | Representação da transferência (TED In) a ser enviada para o SPAG |
| **MensagemRecebida.java** | Domínio que representa a mensagem recebida do SPB via Kafka |
| **RespostaRequisitantePayload.java** | Payload de resposta/confirmação enviado ao requisitante |
| **PubSubPublisher.java** | Componente genérico para publicação de mensagens no Google Pub/Sub |
| **GenericPublisher.java** | Classe abstrata base para publishers específicos |
| **TedInPublisher.java, ConfirmationPublisher.java, MensagemNaoProcessadaPublisher.java** | Publishers especializados para cada tipo de evento |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.7.x** (framework base)
- **Apache Camel** (orquestração e roteamento)
- **Apache Kafka** (consumo de mensagens do SPB via Confluent Cloud)
- **Apache Avro** (serialização de mensagens Kafka)
- **Google Cloud Pub/Sub** (publicação de eventos processados)
- **Google Cloud Platform (GCP)** (infraestrutura)
- **Confluent Schema Registry** (gerenciamento de schemas Avro)
- **MapStruct** (mapeamento de objetos)
- **Lombok** (redução de boilerplate)
- **Logback com JSON** (logging estruturado)
- **JUnit 5 e Mockito** (testes unitários)
- **Swagger/OpenAPI** (documentação de APIs)
- **Docker** (containerização)
- **Kubernetes/OpenShift** (orquestração de containers)
- **Jenkins** (CI/CD)
- **RestTemplate** (cliente HTTP para integração com APIs externas)
- **OAuth 2.0** (autenticação via API Gateway)
- **Hibernate Validator** (validação de dados)

---

## 4. Principais Endpoints REST

Não se aplica. O sistema é um consumidor Kafka e publisher Pub/Sub, não expõe endpoints REST de negócio. Apenas endpoints de monitoramento (Actuator) e documentação (Swagger UI) estão disponíveis.

---

## 5. Principais Regras de Negócio

1. **Filtragem de Mensagens**: Apenas mensagens com código iniciando por "PAG" ou "STR" são processadas; demais são descartadas com acknowledge.

2. **Tratamento de Mensagens R1 e E**: Mensagens do tipo R1 (resposta) ou E (erro) geram apenas confirmação ao requisitante, sem processamento de transferência.

3. **Mapeamento por Tipo de Mensagem**: Cada tipo de mensagem SPB (PAG0107R2, PAG0108R2, STR0004R2, etc.) possui um mapper específico que popula o CaixaEntradaDTO com as regras de negócio correspondentes.

4. **Validação de CNPJ**: Verifica se o CNPJ do favorecido é do Banco Votorantim (59588111000103) ou BV SA (01858774000110) para determinar o código de transação (crédito para banco ou crédito em conta corrente).

5. **Conta Especial 10000001**: Quando o favorecido é o BV SA e a conta é "10000001", a transação é tratada como crédito para o banco.

6. **Ajuste de Conta Pagamento**: Contas do tipo "PG" (Pagamento) são limitadas a 10 caracteres.

7. **Formatação de Dados**: Remoção de caracteres especiais, acentos, ajuste de padding com zeros à esquerda para CPF/CNPJ, formatação de agências e contas.

8. **Tratamento de Fintech**: Identifica lançamentos de contas fintech (agências 1111 ou 655 do Banco Votorantim com conta PG > 12 caracteres) e ajusta a conta para "0".

9. **Conversão de Tipos de Conta**: Mapeia tipos de conta numéricos (1-7) para códigos alfabéticos (CI, IF, PP, CO, CC, CT, PG).

10. **Consulta de Banco por ISPB**: Realiza consulta ao serviço externo para obter o código COMPE a partir do código ISPB.

11. **Tratamento de Devoluções**: Mensagens PAG0111R2 e STR0010R2 são tratadas como devoluções, populando campos específicos como código de devolução e número de controle original.

12. **Envio para DLQ**: Mensagens que falham no processamento (banco não encontrado, erro genérico) são enviadas para tópico de mensagens não processadas (DLQ).

13. **Publicação Assíncrona**: Utiliza callbacks para verificar sucesso/falha na publicação no Pub/Sub.

---

## 6. Relação entre Entidades

**MensagemRecebidaSPB** (Kafka/Avro)
- Consumida do Kafka
- Mapeada para **MensagemRecebida** (domínio interno)

**MensagemRecebida**
- Contém: código da mensagem SPB, movimento SPB, operação SPB, status, JSON da mensagem
- Processada pelo **RecebimentoService**

**CaixaEntradaDTO**
- DTO intermediário populado pelos mappers específicos (PAG0107R2, STR0005R2, etc.)
- Contém dados de remetente, favorecido, valores, datas, códigos de transação
- Transformado em **TedInRepresentation**

**TedInRepresentation**
- Representação final da transferência
- Contém: **ParticipanteRepresentation** (remetente e favorecido), valores, datas, códigos
- Publicada no tópico Pub/Sub de recebimento de mensagens

**RespostaRequisitantePayload**
- Payload de confirmação/resposta
- Publicado no tópico Pub/Sub de confirmação

**BancoDomain**
- Domínio de dados cadastrais de banco
- Obtido via consulta à API externa (CadastroApi)

---

## 7. Estruturas de Banco de Dados Lidas

Não se aplica. O sistema não acessa diretamente banco de dados. As consultas de cadastro são realizadas via API REST externa (sboot-sitp-base-atom-integrar-pagamento).

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema não realiza operações de escrita em banco de dados.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml, application-des.yml, application-local.yml | Leitura | Spring Boot (startup) | Arquivos de configuração da aplicação por ambiente |
| logback-spring.xml | Leitura | Logback (startup) | Configuração de logging em formato JSON |
| MensagemRecebidaSPB.avsc | Leitura | Avro Maven Plugin (build) | Schema Avro para deserialização de mensagens Kafka |
| openapi.yaml | Leitura | Swagger UI (runtime) | Documentação OpenAPI da aplicação |
| sboot-sitp-base-atom-integrar-pagamento.yaml | Leitura | OpenAPI Generator (build) | Especificação para geração de cliente REST |

---

## 10. Filas Lidas

**Kafka:**
- **Tópico**: `spbb-base-mensagem-recebida-spb`
- **Descrição**: Tópico Kafka (Confluent Cloud) que recebe mensagens do SPB processadas pelas câmaras de liquidação (PAG e STR)
- **Consumer Group**: `sboot-spag-base-orch-receber-mensagem-spb`
- **Formato**: Avro (schema MensagemRecebidaSPB)
- **Classe Responsável**: KafkaConsumer.java

---

## 11. Filas Geradas

**Google Pub/Sub:**

1. **Tópico**: `business-spag-base-recebimento-mensagem-spb`
   - **Descrição**: Recebe as transferências (TED In) processadas para consumo pelo SPAG
   - **Formato**: JSON (TedInRepresentation)
   - **Classe Responsável**: TedInPublisher.java

2. **Tópico**: `business-spag-base-confirmacao-spb`
   - **Descrição**: Recebe confirmações/respostas para o requisitante original
   - **Formato**: JSON (RespostaRequisitantePayload)
   - **Classe Responsável**: ConfirmationPublisher.java

3. **Tópico**: `business-spag-base-mensagem-recebida-spb-dlq`
   - **Descrição**: Dead Letter Queue para mensagens que falharam no processamento (banco não encontrado, erros genéricos)
   - **Formato**: JSON (MensagemRecebida)
   - **Classe Responsável**: MensagemNaoProcessadaPublisher.java

---

## 12. Integrações Externas

1. **sboot-sitp-base-atom-integrar-pagamento**
   - **Tipo**: API REST
   - **Descrição**: Serviço de integração com base de pagamentos ITP para consulta de dados cadastrais de bancos (conversão ISPB para COMPE)
   - **Endpoint**: Configurável por ambiente (des/uat/prd)
   - **Autenticação**: OAuth 2.0 via API Gateway (client credentials)
   - **Classe Responsável**: CadastroRepositoryImpl.java, CadastroApi.java

2. **API Gateway Votorantim**
   - **Tipo**: Serviço de autenticação OAuth 2.0
   - **Descrição**: Fornece tokens JWT para autenticação nas APIs internas
   - **Endpoint**: `/auth/oauth/v2/token-jwt`
   - **Classe Responsável**: GatewayOAuthService.java

3. **Confluent Schema Registry**
   - **Tipo**: Serviço de gerenciamento de schemas
   - **Descrição**: Armazena e valida schemas Avro das mensagens Kafka
   - **Autenticação**: Basic Auth (API Key/Secret)

4. **Catálogo de Mensagens BCB**
   - **Tipo**: Biblioteca interna
   - **Descrição**: Biblioteca para deserialização e validação de mensagens do Banco Central (formato XML/JSON)
   - **Classe Responsável**: CatalogoMensagemService.java

---

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades (service, repository, mapper, domain)
- Uso adequado de padrões como Strategy (ICaixaEntradaDTO) e Factory (getCaixaEntradaDTOImp)
- Cobertura de testes unitários presente
- Uso de MapStruct para mapeamento de objetos
- Logging estruturado em JSON
- Tratamento de exceções específicas (BancoNaoEncontradoException, MensagemNaoMapeadaException, EnvioPubSubException)
- Configuração externalizada por ambiente
- Uso de Lombok para redução de boilerplate

**Pontos de Melhoria:**
- Classes de mapeamento (PAG0107R2, STR0005R2, etc.) possuem lógica complexa e repetitiva que poderia ser refatorada
- Métodos muito longos em algumas classes (ex: CaixaEntradaDTO.ajustaGeral())
- Uso de constantes mágicas espalhadas pelo código (ex: "10000001", "1111", "655")
- Falta de documentação JavaDoc em métodos complexos
- Alguns métodos estáticos em classes utilitárias poderiam ser melhor organizados
- Tratamento genérico de exceções em alguns pontos (catch Exception)
- Código legado comentado (VB6) presente como referência, mas poderia ser removido após validação
- Alguns nomes de variáveis poderiam ser mais descritivos (ex: msg, ack)

---

## 14. Observações Relevantes

1. **Migração de Sistema Legado**: O código contém comentários em VB6 indicando que é uma migração/reescrita de sistema legado, o que explica algumas estruturas e nomenclaturas.

2. **Múltiplos Ambientes**: Sistema preparado para execução em múltiplos ambientes (local, des, uat, prd) com configurações específicas.

3. **Infraestrutura como Código**: Possui arquivos de infraestrutura (infra.yml) para deploy automatizado no GCP/Kubernetes.

4. **Emulador Local**: Disponibiliza docker-compose para emulação local de Kafka e Pub/Sub, facilitando desenvolvimento.

5. **Segurança**: Implementa autenticação OAuth 2.0 e JWT para comunicação com APIs internas.

6. **Observabilidade**: Integrado com Prometheus, Actuator e logging estruturado para monitoramento.

7. **Mensagens Suportadas**: Suporta 20 tipos diferentes de mensagens SPB (PAG0107R2, PAG0108R2, PAG0111R2, PAG0137R2, PAG0141R2, PAG0142R2, PAG0143R2, PAG0151R2, STR0004R2, STR0005R2, STR0006R2, STR0007R2, STR0008R2, STR0010R2, STR0026R2, STR0037R2, STR0040R2, STR0041R2, STR0051R2, STR0052R2).

8. **Tratamento de Devoluções**: Mensagens PAG0111R2 e STR0010R2 são tratadas especificamente como devoluções de transferências.

9. **Resiliência**: Implementa retry via Kafka (nack) e DLQ para mensagens não processadas.

10. **Catálogo BCB**: Utiliza biblioteca interna (sbootlib-spbb-base-catalogo-mensagens) para parsing de mensagens do Banco Central em diferentes versões do catálogo.