# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-spbb-base-atom-mensageria-historico** é um serviço atômico Spring Boot responsável por consumir mensagens do Kafka relacionadas ao SPB (Sistema de Pagamentos Brasileiro), processar essas mensagens e armazená-las em um banco de dados MySQL para fins de histórico e auditoria. O sistema também expõe uma API REST para consulta de movimentos existentes, verificando se determinado movimento já foi processado anteriormente. Utiliza schema Avro para serialização das mensagens Kafka e JDBI para acesso ao banco de dados.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application.java` | Classe principal de inicialização da aplicação Spring Boot |
| `KafkaConsumer.java` | Listener Kafka que consome mensagens do tópico configurado e processa os eventos |
| `MovimentoHistoricoService.java` | Serviço de negócio que implementa a lógica de persistência e validação de duplicidade |
| `MovimentoHistoricoRepository.java` | Interface JDBI para acesso ao banco de dados (operações de insert e consulta) |
| `MensageriaHistoricoApiDelegateImpl.java` | Implementação do delegate da API REST para consulta de movimentos |
| `MovimentoHistoricoMapper.java` | Mapper MapStruct para conversão entre `MensagemProcessadaSPB` e `MovimentoHistorico` |
| `MovimentoHistorico.java` | Entidade de domínio representando um movimento histórico |
| `JdbiConfiguration.java` | Configuração do JDBI e registro de plugins e mappers |
| `Utils.java` | Classe utilitária para geração de hash SHA-256 |
| `SqlLoggerImpl.java` | Implementação customizada de logger SQL para JDBI |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.7.8** - Framework principal
- **Apache Kafka** - Mensageria para consumo de eventos
- **Confluent Schema Registry** - Gerenciamento de schemas Avro
- **Apache Avro 1.11.4** - Serialização de mensagens
- **JDBI 3.14.4** - Framework de acesso a banco de dados
- **MySQL 8.4.0** - Banco de dados relacional
- **MapStruct** - Mapeamento de objetos
- **Lombok** - Redução de boilerplate
- **Maven** - Gerenciamento de dependências
- **Docker** - Containerização
- **OpenAPI/Swagger** - Documentação de API
- **Spring Security OAuth2** - Segurança JWT
- **Actuator** - Monitoramento e health checks

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/movimentos/{cdMovimento}/existente` | `MensageriaHistoricoApiDelegateImpl` | Verifica se um movimento existe no histórico pelo código do movimento |
| GET | `/actuator/health` | Spring Actuator | Endpoint de health check da aplicação |
| GET | `/swagger-ui/index.html` | Swagger UI | Documentação interativa da API |

---

## 5. Principais Regras de Negócio

1. **Validação de Duplicidade**: Antes de inserir uma mensagem no banco, o sistema gera um hash SHA-256 do XML da mensagem e verifica se já existe um registro com o mesmo hash. Se existir, a mensagem é considerada duplicada e não é inserida novamente.

2. **Geração de Identificador Único**: Cada mensagem recebe um identificador único (`cdIdentificadorMensagem`) gerado através do hash SHA-256 do conteúdo XML.

3. **Tratamento de Código de Movimento Vazio**: Se o campo `cdMovimento` estiver em branco, é convertido para `null` antes da persistência.

4. **Registro de Origem**: Todas as mensagens persistidas recebem automaticamente o valor "sboot-spbb-base-atom-mensageria-historico" no campo `dsLogin` para identificar a origem do registro.

5. **Acknowledgment Manual**: O sistema utiliza acknowledgment manual do Kafka, confirmando o processamento apenas após a persistência bem-sucedida.

6. **Consulta de Existência**: Permite verificar se um movimento específico já foi processado através do código do movimento.

---

## 6. Relação entre Entidades

**MovimentoHistorico** (Entidade Principal):
- Representa um registro de mensagem processada do SPB
- Contém informações sobre instituições emissoras e destinatárias
- Armazena o XML completo da mensagem
- Possui identificador único baseado em hash
- Relaciona-se com o conceito de movimento SPB através de `cdMovimento`

**MensagemProcessadaSPB** (Schema Avro):
- Representa a mensagem recebida via Kafka
- É mapeada para `MovimentoHistorico` através do `MovimentoHistoricoMapper`
- Contém metadados do SPB (ISPB, tipo de mensagem, operação, etc.)

Não há relacionamentos JPA/Hibernate tradicionais, pois o sistema utiliza JDBI para acesso direto ao banco.

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| `SPBBMensageriaHistorico.TbMovimentoHistorico` | Tabela | SELECT | Consulta para verificar existência de mensagem duplicada através do hash (índice `IuTbMovimentoHistorico`) |
| `SPBBMensageriaHistorico.TbMovimentoHistorico` | Tabela | SELECT | Consulta para verificar existência de movimento pelo código do movimento |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| `SPBBMensageriaHistorico.TbMovimentoHistorico` | Tabela | INSERT | Inserção de novos registros de mensagens processadas do SPB com todos os metadados e XML |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `logback-spring.xml` | Leitura | Configuração Spring Boot | Arquivo de configuração de logs carregado em runtime conforme ambiente |
| `openapi.yaml` | Leitura | OpenAPI Generator | Contrato da API REST usado para geração de código |
| `MensagemProcessadaSPB.avsc` | Leitura | Avro Maven Plugin | Schema Avro usado para geração de classes Java de serialização |
| `*.sql` | Leitura | JDBI SqlLocator | Arquivos SQL carregados dinamicamente pelo JDBI para execução de queries |

---

## 10. Filas Lidas

**Tópico Kafka Consumido:**
- **Nome**: `spbb-base-mensagem-processada` (configurável via `spring.kafka.consumer-topic`)
- **Formato**: Mensagens serializadas em Avro seguindo o schema `MensagemProcessadaSPB`
- **Consumer Group**: `sboot-spbb-base-atom-mensageria-historico`
- **Classe Responsável**: `KafkaConsumer.java`
- **Descrição**: Consome eventos de mensagens processadas pelo SPB para armazenamento em histórico

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **Confluent Cloud Kafka** | Mensageria | Cluster Kafka gerenciado para consumo de mensagens SPB (diferentes clusters por ambiente: des, uat, prd) |
| **Confluent Schema Registry** | Schema Management | Registro centralizado de schemas Avro para validação e versionamento |
| **Google Cloud SQL (MySQL)** | Banco de Dados | Instâncias MySQL gerenciadas no GCP para persistência (gcmysatdes32, gcmysatuat32, gcmysatprd32) |
| **API Gateway BV** | Segurança | Validação de tokens JWT através de JWKS endpoint |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com camadas bem definidas (config, domain, repository, service, rest)
- Uso adequado de frameworks modernos (Spring Boot, JDBI, MapStruct, Lombok)
- Implementação de validação de duplicidade através de hash
- Configuração adequada para múltiplos ambientes
- Uso de SQL externalizado em arquivos separados
- Logging estruturado e tratamento de erros SQL
- Documentação OpenAPI bem estruturada

**Pontos de Melhoria:**
- Falta de tratamento de exceções mais robusto (ex: falhas de conexão Kafka/DB)
- Ausência de testes unitários nos arquivos enviados
- Classe `Utils` com método estático poderia ser um bean Spring para melhor testabilidade
- Imports não utilizados em algumas classes (ex: `Field`, `Ingres9Dialect` no Service)
- Falta de validações de entrada mais rigorosas
- Ausência de métricas customizadas além do Actuator padrão
- Poderia ter circuit breaker para resiliência
- Documentação inline (JavaDoc) ausente na maioria das classes

---

## 14. Observações Relevantes

1. **Ambiente Local**: O sistema possui configuração específica para execução local com Kafka e Schema Registry dockerizados (docker-compose.yaml fornecido).

2. **Segurança**: Utiliza autenticação JWT com validação via API Gateway do Banco Votorantim. Endpoints públicos incluem Swagger e Actuator.

3. **Infraestrutura como Código**: Arquivo `infra.yml` bem estruturado com configurações específicas por ambiente (des, uat, prd) incluindo secrets gerenciados por cofre.

4. **Performance**: Utiliza índice específico (`IuTbMovimentoHistorico`) para otimizar consultas de duplicidade por hash.

5. **Monitoramento**: Probes de liveness e readiness configurados com timeouts adequados (liveness com 420s de delay inicial para startup).

6. **Multi-layer Docker**: Dockerfile otimizado com múltiplas camadas para melhor cache e rebuild mais rápido.

7. **Versionamento**: Sistema está na versão 0.13.0, indicando ainda estar em desenvolvimento/evolução.

8. **Dependências de Segurança**: Utiliza versões atualizadas de bibliotecas com correções de vulnerabilidades conhecidas (ex: protobuf-java 3.25.5, tomcat-embed-core 9.0.111).