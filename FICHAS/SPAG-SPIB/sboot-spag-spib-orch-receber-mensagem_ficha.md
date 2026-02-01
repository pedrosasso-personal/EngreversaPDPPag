# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-spag-spib-orch-receber-mensagem** é um serviço stateless desenvolvido em Java com Spring Boot para receber mensagens do Sistema de Pagamentos Instantâneos (SPI/PIX) do Banco Central do Brasil. O sistema realiza polling periódico no endpoint do BACEN para buscar mensagens PIX (PACS.002, PACS.004, PACS.008), processa essas mensagens, extrai informações de auditoria e métricas, e as encaminha para filas do Google Cloud Pub/Sub para processamento posterior. A comunicação com o BACEN é realizada através de HSM (Hardware Security Module) da Dinamo Networks para garantir segurança criptográfica.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal que inicializa a aplicação Spring Boot |
| `ReceberMensagemRouter` | Roteador Apache Camel que orquestra o fluxo de recebimento de mensagens do BACEN |
| `ReceberMensagemRepositoryImpl` | Implementação da comunicação com o BACEN via HSM Dinamo para GET e DELETE de mensagens |
| `ReceberMensagemProducerRepositoryImpl` | Implementação do envio de mensagens para filas Google Cloud Pub/Sub |
| `TratarBoundaryProcessor` | Processador Camel que extrai e trata o conteúdo multipart das mensagens recebidas |
| `EndMetricasProcessor` | Processador que gera métricas de liquidação e indicadores de performance |
| `PixProcessor` | Processador auxiliar para limpeza de estado após processamento |
| `PubSubProperties` | Configuração de propriedades dos tópicos Pub/Sub |
| `ReceberMensagemConfiguration` | Classe de configuração Spring para beans do domínio |
| `OpenApiConfiguration` | Configuração do Swagger/OpenAPI para documentação |
| `RouterConstants` | Classe singleton que mantém estado do path de polling do BACEN |
| `AuditJson` | Modelo de dados para auditoria de mensagens |
| `SpiMetrics`, `LiquidationMetrics`, `IndicatorsMetrics` | Modelos de dados para métricas |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Apache Camel 3.0.1** (orquestração e integração)
- **Google Cloud Pub/Sub** (mensageria)
- **Dinamo HSM 4.1.6** (comunicação segura com BACEN via biblioteca nativa)
- **Lombok** (redução de boilerplate)
- **Swagger/Springfox 3.0.0** (documentação de API)
- **Micrometer/Prometheus** (métricas e observabilidade)
- **JUnit 5 + Mockito** (testes unitários)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Logback** (logging em formato JSON)

---

## 4. Principais Endpoints REST

Não se aplica. O sistema não expõe endpoints REST para consumo externo. Trata-se de um serviço de polling/consumer que busca mensagens periodicamente do BACEN e as encaminha para filas.

---

## 5. Principais Regras de Negócio

1. **Polling Periódico**: Executa requisições GET ao BACEN a cada 1ms (timer configurado) para buscar novas mensagens PIX
2. **Controle de Fluxo**: Mantém o path de "pull-next" fornecido pelo BACEN para continuidade do stream de mensagens
3. **Processamento Multipart**: Divide mensagens multipart usando boundary e processa cada XML individualmente
4. **Validação de Status HTTP**: Aceita apenas respostas 200 (com mensagens) ou 204 (sem mensagens) do BACEN
5. **Extração de Metadados**: Extrai informações como ISPB, EndToEndId, InstructionId, tipo de mensagem (PACS002/004/008), certificado digital
6. **Cálculo de Métricas**: Calcula delay entre timestamp do BACEN e recebimento local para métricas de performance
7. **Auditoria Completa**: Registra headers HTTP, corpo da requisição/resposta, timestamps para auditoria
8. **Tratamento de Erros**: Em caso de erro, executa DELETE no BACEN para limpar o stream e reiniciar
9. **Retry Logic**: Implementa retry (2 tentativas) para falhas de comunicação
10. **Filtragem de Mensagens para Métricas**: Apenas mensagens PACS.002, PACS.004 e PACS.008 geram métricas de liquidação

---

## 6. Relação entre Entidades

O sistema trabalha com modelos de domínio simples sem relacionamentos JPA/ORM:

- **AuditJson**: Entidade que encapsula todos os dados de auditoria de uma mensagem (headers, body, timestamps, certificados, identificadores)
- **SpiMetrics**: Agregador que contém listas de `LiquidationMetrics` e `IndicatorsMetrics`
- **LiquidationMetrics**: Representa eventos de liquidação (tlei - tempo de leitura, tdis - tempo de disponibilização)
- **IndicatorsMetrics**: Representa indicadores de performance (tempo de execução, tipo 003)
- **RouterConstants**: Singleton que mantém estado do path de polling e URLs do BACEN

Não há relacionamentos de banco de dados tradicionais, pois o sistema não persiste dados localmente.

---

## 7. Estruturas de Banco de Dados Lidas

Não se aplica. O sistema não realiza leitura direta de banco de dados.

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema não realiza operações de escrita em banco de dados.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `application.yml` | Leitura | Spring Boot | Arquivo de configuração da aplicação com parâmetros de conexão BACEN, HSM e Pub/Sub |
| `logback-spring.xml` | Leitura | Logback | Configuração de logging em formato JSON para stdout |
| Bibliotecas nativas HSM (.so) | Leitura | Dinamo/JNI | Bibliotecas nativas do HSM Dinamo carregadas em `/opt/java/openjdk/lib/` |

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas, apenas produz.

---

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Responsável | Descrição |
|--------------|------------|-------------------|-----------|
| `business-spag-pixx-receber-mensagem-spi` | Google Cloud Pub/Sub | `ReceberMensagemProducerRepositoryImpl.sendReceivedMessage()` | Fila para mensagens PIX recebidas do BACEN (XML completo + timestamp) |
| `business-spag-pixx-salvar-mensagem` | Google Cloud Pub/Sub | `ReceberMensagemProducerRepositoryImpl.sendAudit()` | Fila para auditoria completa das mensagens (headers, body, metadados) |
| `business-spag-pixx-metricas-liquidacao` | Google Cloud Pub/Sub | `ReceberMensagemProducerRepositoryImpl.sendMetrics()` | Fila para métricas de liquidação e indicadores de performance |

---

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| **BACEN SPI** | API REST HTTPS | Endpoint do Banco Central para recebimento de mensagens PIX via protocolo PI-Pull. Operações: GET (buscar mensagens) e DELETE (confirmar recebimento) |
| **HSM Dinamo Networks** | Biblioteca Nativa (JNI) | Hardware Security Module para comunicação segura com BACEN usando certificados digitais e chaves criptográficas |
| **Google Cloud Pub/Sub** | Mensageria Cloud | Plataforma de mensageria para publicação de mensagens recebidas, auditoria e métricas |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (application, domain, common)
- Uso adequado de padrões como Repository e Processor
- Cobertura de testes unitários presente
- Uso de Lombok para reduzir boilerplate
- Configuração externalizada e suporte a múltiplos ambientes
- Logging estruturado em JSON
- Tratamento de exceções com retry

**Pontos de Melhoria:**
- Uso de variáveis estáticas mutáveis em `RouterConstants` (DELAY_GET_BACEN, DELAY_POOL_NEXT) que podem causar problemas de concorrência
- Classe `ReceberMensagemRepositoryImpl` muito extensa (>300 linhas) com múltiplas responsabilidades
- Parsing de XML usando regex ao invés de parser XML apropriado (frágil e propenso a erros)
- Hardcoding de strings e magic numbers em vários locais
- Comentários em português misturados com código em inglês
- Falta de validação de entrada em alguns métodos
- Alguns testes comentados/desabilitados
- Acoplamento forte com biblioteca HSM proprietária dificulta testes

---

## 14. Observações Relevantes

1. **Segurança**: O sistema utiliza HSM para comunicação criptografada com o BACEN, garantindo conformidade com requisitos de segurança do SPI
2. **Performance**: Timer configurado para 1ms pode gerar carga significativa; considerar ajuste baseado em volume real
3. **Estado Compartilhado**: O uso de variáveis estáticas em `RouterConstants` pode causar problemas em ambientes com múltiplas instâncias
4. **Dependência de Biblioteca Nativa**: As bibliotecas .so do Dinamo são copiadas para a imagem Docker, criando dependência de plataforma Linux
5. **Ambientes**: Sistema configurado para 4 ambientes (des, qa, uat, prd) com configurações específicas de HSM e BACEN
6. **Observabilidade**: Integração com Prometheus/Grafana para métricas customizadas
7. **Resiliência**: Implementa retry e tratamento de erros, mas pode melhorar com circuit breaker
8. **Documentação**: README básico presente, mas falta documentação técnica detalhada do fluxo de negócio