# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-spbb-base-orch-envio-mensagem** é um orquestrador baseado em Apache Camel e Spring Boot, responsável por processar e enviar mensagens SPB (Sistema de Pagamentos Brasileiro) para câmaras de liquidação (STR, PAG, SRC). O sistema consome mensagens de tópicos Kafka, realiza validações, conversões, criptografia e envia as mensagens para filas IBM MQ, além de manter histórico e notificar status de processamento.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal que inicializa a aplicação Spring Boot |
| `KafkaConsumer` | Consome mensagens do Kafka e dispara o processamento via Camel |
| `EnvioMensagemSPBRouter` | Rota principal do Camel que orquestra todo o fluxo de envio de mensagens |
| `SpbMensageriaRouter` | Rota responsável por incluir mensagens no atom-mensageria |
| `SpbIntegracaoRouter` | Rota para validação de mensagens e atualização de réplica SPB legado |
| `SpbMensageriaHistoricoRouter` | Rota para verificar existência de movimentos no histórico |
| `CamelService` | Serviço que encapsula a execução de rotas Camel |
| `EncryptService` | Serviço de criptografia de mensagens usando SPBSecJava |
| `EnvioMensagemCamaraService` | Serviço para envio de mensagens para filas IBM MQ |
| `MensagemProcessadaService` | Publica mensagens processadas no Kafka |
| `MensagemStatusService` | Publica status de envio de mensagens no Kafka |
| `SpbAtomMensageriaServiceImpl` | Implementação de integração com atom-mensageria |
| `SpbAtomIntegracaoServiceImpl` | Implementação de integração com atom-integracao |
| `SpbMensageriaHistoricoServiceImpl` | Implementação de integração com atom-mensageria-historico |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.7.7** - Framework base da aplicação
- **Apache Camel** - Framework de integração e orquestração
- **Apache Kafka** - Mensageria para consumo e publicação de eventos
- **Apache Avro** - Serialização de mensagens Kafka
- **IBM MQ** - Filas de mensagens para integração com câmaras
- **SPBSecJava (Evaltec)** - Biblioteca de criptografia para mensagens SPB
- **Hibernate/JPA** - Persistência de dados
- **MapStruct** - Mapeamento de objetos
- **Logback** - Logging em formato JSON
- **OpenAPI/Swagger** - Documentação de APIs
- **ConfigCat (Feature Toggle)** - Gerenciamento de feature flags
- **Docker** - Containerização
- **Maven** - Gerenciamento de dependências

---

## 4. Principais Endpoints REST

não se aplica - O sistema não expõe endpoints REST próprios, apenas consome de outros serviços via clients gerados.

---

## 5. Principais Regras de Negócio

1. **Validação de Payload**: Valida campos obrigatórios da mensagem SPB antes do processamento
2. **Verificação de Duplicidade**: Consulta histórico para evitar reprocessamento de mensagens já enviadas
3. **Conversão de Mensagem**: Converte JSON para XML conforme catálogo do Bacen
4. **Criptografia**: Criptografa mensagens usando algoritmos específicos do SPB
5. **Roteamento por Instituição**: Direciona mensagens para filas específicas baseado no código COMPE (655 - Banco Votorantim, 413 - Banco BV SA)
6. **Roteamento por Tipo de Mensagem**: Direciona para filas STR, PAG ou SRC conforme tipo da mensagem
7. **Réplica SPB Legado**: Atualiza status em sistema legado para mensagens STR e PAG em caso de erro
8. **Resiliência**: Implementa retry para erros de conexão com serviços de criptografia
9. **Notificação de Status**: Publica eventos de status (sucesso/erro) no Kafka
10. **Feature Toggle**: Permite alternar entre servidores de criptografia via feature flag

---

## 6. Relação entre Entidades

**EnvioMensagemSPBDomain** (entidade principal)
- Contém: `ControleSPBDomain` (informações de controle SPB)
- Relaciona-se com: `MensagemCriptografar` (dados para criptografia)
- Gera: `MensagemCamaraDomain` (mensagem para envio à câmara)
- Produz: `MensagemProcessadaSPB` (evento Kafka de mensagem processada)
- Produz: `StatusEnvioMensagemSPB` (evento Kafka de status)

**Fluxo de transformação:**
```
EnvioMensagemSPB (Avro) → EnvioMensagemSPBDomain → ValidarMensagemRequest → 
ConversaoResponse → MensagemCriptografar → MensagemCamaraDomain → 
MensagemProcessadaSPB + StatusEnvioMensagemSPB
```

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica - O sistema não acessa diretamente banco de dados, apenas consome de APIs de outros átomos.

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica - O sistema não atualiza diretamente banco de dados, apenas invoca APIs de outros átomos que realizam as operações.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | leitura | Configuração Spring Boot | Arquivo de configuração de logs |
| ESAPI.properties | leitura | Configuração OWASP | Configurações de segurança ESAPI |
| application.yml | leitura | Configuração Spring Boot | Configurações da aplicação |
| layers.xml | leitura | Build Docker | Definição de camadas para imagem Docker |
| *.avsc | leitura | Avro Maven Plugin | Schemas Avro para geração de classes |
| *.yaml/*.yml | leitura | OpenAPI Generator | Contratos OpenAPI para geração de clients |

---

## 10. Filas Lidas

| Nome da Fila | Tecnologia | Classe Responsável | Descrição |
|--------------|------------|-------------------|-----------|
| spbb-base-envio-mensagem-spb | Kafka | KafkaConsumer | Tópico de entrada com mensagens SPB para envio |

---

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Responsável | Descrição |
|--------------|------------|-------------------|-----------|
| spbb-base-mensagem-processada | Kafka | MensagemProcessadaService | Tópico com mensagens processadas (XML gerado) |
| spbb-base-status-envio-mensagem | Kafka | MensagemStatusService | Tópico com status de envio das mensagens |
| QR.REQ.59588111.00038166.01 | IBM MQ | EnvioMensagemCamaraService | Fila STR - Banco Votorantim (655) |
| QR.REQ.59588111.04391007.01 | IBM MQ | EnvioMensagemCamaraService | Fila PAG - Banco Votorantim (655) |
| QR.REQ.59588111.00038166.03 | IBM MQ | EnvioMensagemCamaraService | Fila SRC - Banco Votorantim (655) |
| QR.REQ.01858774.00038166.01 | IBM MQ | EnvioMensagemCamaraService | Fila STR - Banco BV SA (413) |
| QR.REQ.01858774.04391007.01 | IBM MQ | EnvioMensagemCamaraService | Fila PAG - Banco BV SA (413) |
| QR.REQ.01858774.00038166.03 | IBM MQ | EnvioMensagemCamaraService | Fila SRC - Banco BV SA (413) |

---

## 12. Integrações Externas

| Sistema | Tipo | Classe Responsável | Descrição |
|---------|------|-------------------|-----------|
| sboot-spbb-base-atom-mensageria | REST API | SpbAtomMensageriaServiceImpl | Conversão de mensagens JSON para XML |
| sboot-spbb-base-atom-integracao | REST API | SpbAtomIntegracaoServiceImpl | Validação de mensagens e atualização SPB legado |
| sboot-spbb-base-atom-mensageria-historico | REST API | SpbMensageriaHistoricoServiceImpl | Consulta de movimentos no histórico |
| EVALCryptoSPB | TCP Socket | EncryptService | Serviço de criptografia de mensagens SPB |
| IBM MQ (QM.59588111.01) | MQ | EnvioMensagemCamaraService | Queue Manager Banco Votorantim |
| IBM MQ (QM.01858774.01) | MQ | EnvioMensagemCamaraService | Queue Manager Banco BV SA |
| Kafka Confluent Cloud | Kafka | KafkaConsumer/Producers | Mensageria de eventos |
| ConfigCat | REST API | FeatureToggleService | Gerenciamento de feature flags |
| API Gateway OAuth | REST API | GatewayOAuthService | Autenticação para chamadas entre serviços |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 8/10

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões de orquestração com Apache Camel
- Separação clara de responsabilidades (routers, processors, services, mappers)
- Uso adequado de padrões como Builder, Strategy e Factory
- Boa cobertura de testes unitários (fixtures, mocks bem estruturados)
- Tratamento de exceções customizado e específico por tipo de erro
- Uso de feature toggles para facilitar mudanças em produção
- Configurações externalizadas e separadas por ambiente
- Logging estruturado em JSON
- Uso de MapStruct para mapeamento de objetos

**Pontos de Melhoria:**
- Algumas classes de processor poderiam ser mais coesas (ex: PrepararMensagemCriptografarProcessor faz validação e preparação)
- Falta documentação JavaDoc em várias classes
- Alguns métodos estáticos em mappers poderiam ser instâncias
- Configurações de retry hardcoded em algumas anotações
- Alguns nomes de variáveis poderiam ser mais descritivos (ex: "msg" ao invés de "mensagem")

---

## 14. Observações Relevantes

1. **Segurança**: O sistema utiliza criptografia específica do SPB através da biblioteca SPBSecJava da Evaltec, com conexão a servidores dedicados de criptografia.

2. **Resiliência**: Implementa retry automático para falhas de conexão com servidores de criptografia (3 tentativas com backoff de 1 segundo).

3. **Feature Toggle**: Possui flag `ft_boolean_spbb_base_novo_servidor_eval` para alternar entre servidores de criptografia antigos e novos sem necessidade de deploy.

4. **Multi-tenancy**: Suporta dois bancos (655 - Votorantim e 413 - BV SA) com filas e queue managers separados.

5. **Observabilidade**: Expõe métricas via Actuator na porta 9090 e logs estruturados em JSON para facilitar análise.

6. **Containerização**: Utiliza estratégia de layers no Docker para otimizar builds e deploys.

7. **Versionamento de Schemas**: Utiliza Avro para versionamento de mensagens Kafka com Schema Registry.

8. **Ambientes**: Configurado para 3 ambientes (des, uat, prd) com configurações específicas de infraestrutura.

9. **Dependências Críticas**: Depende de 3 átomos (mensageria, integracao, mensageria-historico) e servidores de criptografia externos.

10. **Processamento Assíncrono**: Todo o fluxo é assíncrono, desde o consumo do Kafka até o envio para as filas MQ.