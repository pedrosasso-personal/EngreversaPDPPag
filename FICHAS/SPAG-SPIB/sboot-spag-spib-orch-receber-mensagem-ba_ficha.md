# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-spag-spib-orch-receber-mensagem-ba** é um orquestrador desenvolvido em Java com Spring Boot e Apache Camel, responsável por receber mensagens do Sistema de Pagamentos Instantâneos (PIX) do Banco Central do Brasil (BACEN). 

O componente realiza polling periódico no endpoint do BACEN via HSM Dinamo, processa mensagens no formato multipart/mixed contendo XMLs de transações PIX (PACS.002, PACS.004, PACS.008), extrai informações relevantes, gera métricas de liquidação e indicadores de performance, e publica as mensagens processadas em filas do Google Cloud Pub/Sub para consumo por outros componentes do ecossistema.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal que inicializa a aplicação Spring Boot |
| `ReceberMensagemRouter` | Roteador Apache Camel que orquestra o fluxo de recebimento, processamento e publicação de mensagens |
| `ReceberMensagemRepositoryImpl` | Implementação responsável pela comunicação com o BACEN via HSM Dinamo (GET e DELETE de mensagens) |
| `ReceberMensagemProducerRepositoryImpl` | Implementação responsável por publicar mensagens nas filas do Pub/Sub (auditoria, métricas e mensagens recebidas) |
| `TratarBoundaryProcessor` | Processor que trata mensagens multipart, extrai headers e XMLs, e popula objeto de auditoria |
| `EndMetricasProcessor` | Processor que gera métricas de liquidação e indicadores de performance para mensagens PACS |
| `PixProcessor` | Processor auxiliar para manipulação de constantes de roteamento |
| `AuditJson` | Entidade de domínio que representa dados de auditoria das mensagens |
| `SpiMetrics` | Entidade de domínio que encapsula métricas de liquidação e indicadores |
| `ReceberMensagemConfiguration` | Classe de configuração Spring que define beans necessários |
| `PubSubProperties` | Classe de propriedades para configuração dos tópicos do Pub/Sub |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Apache Camel** (orquestração e integração)
- **Maven** (gerenciamento de dependências)
- **Google Cloud Pub/Sub** (mensageria)
- **HSM Dinamo** (comunicação segura com BACEN via biblioteca tacndjavalib 4.7.38)
- **Logback com JSON Layout** (logging estruturado)
- **Spring Cloud Sleuth + OpenTelemetry** (observabilidade e tracing)
- **Micrometer + Prometheus** (métricas)
- **Docker** (containerização)
- **Kubernetes/OpenShift** (orquestração de containers)
- **Jackson** (serialização/deserialização JSON)
- **Lombok** (redução de boilerplate)

---

## 4. Principais Endpoints REST

Não se aplica. O sistema não expõe endpoints REST próprios, apenas endpoints de gerenciamento do Spring Boot Actuator na porta 9090 (/actuator/health, /actuator/metrics, /actuator/prometheus).

---

## 5. Principais Regras de Negócio

1. **Polling Periódico**: Executa requisições GET ao BACEN a cada 1 segundo via timer do Camel para buscar novas mensagens PIX
2. **Autenticação HSM**: Utiliza certificados digitais armazenados no HSM Dinamo para comunicação segura com o BACEN
3. **Processamento Multipart**: Trata mensagens no formato multipart/mixed, extraindo boundaries e separando múltiplos XMLs
4. **Validação de Tipos de Mensagem**: Identifica e processa apenas mensagens PACS.002, PACS.004 e PACS.008
5. **Extração de Metadados**: Captura informações como EndToEndId, InstructionId, ISPB, certificado digital, timestamps
6. **Cálculo de Delays**: Calcula latências entre disponibilização pelo BACEN e processamento interno
7. **Geração de Métricas**: Cria eventos de liquidação (tlei, tdis) e indicadores de performance (tipo 003)
8. **Auditoria Completa**: Registra headers HTTP, URLs, bodies de request/response para rastreabilidade
9. **Gestão de Pull-Next**: Mantém controle do endpoint de continuação (PI-Pull-Next) para polling sequencial
10. **Tratamento de Erros**: Implementa retry (2 tentativas) e DELETE de mensagens em caso de falha
11. **Publicação Assíncrona**: Envia mensagens processadas para 3 filas distintas (recepção, auditoria, métricas)
12. **Paralelização**: Processa múltiplos XMLs de uma mesma resposta multipart em paralelo

---

## 6. Relação entre Entidades

**Entidades de Domínio:**

- **AuditJson**: Representa dados de auditoria de uma transação PIX
  - Contém: headers HTTP, URLs, bodies, PI-ResourceId, tipo de mensagem, certificado, EndToEndId, InstructionId, ISPB, timestamps

- **SpiMetrics**: Agrega métricas de uma transação
  - Contém: lista de `LiquidationMetrics` e lista de `IndicatorsMetrics`

- **LiquidationMetrics**: Representa eventos de liquidação
  - Contém: EndToEndId, InstructionId, tipo de mensagem, fluxo, timestamp do evento, tipo de evento (tlei/tdis), ISPB

- **IndicatorsMetrics**: Representa indicadores de performance
  - Contém: EndToEndId, InstructionId, tempo de execução, timestamp, tipo de indicador (003)

**Relacionamentos:**
- `SpiMetrics` 1 ---> N `LiquidationMetrics`
- `SpiMetrics` 1 ---> N `IndicatorsMetrics`
- Não há persistência em banco de dados, as entidades são DTOs para transporte de informações

---

## 7. Estruturas de Banco de Dados Lidas

Não se aplica. O sistema não realiza leitura de banco de dados.

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema não realiza operações de escrita em banco de dados.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | Leitura | Configuração do Logback | Arquivo de configuração de logs em formato JSON, carregado em tempo de execução |
| application.yml | Leitura | Spring Boot | Arquivo de configuração principal da aplicação com propriedades de ambiente |
| application-local.yml | Leitura | Spring Boot | Arquivo de configuração para perfil local de desenvolvimento |
| layers.xml | Leitura | Docker/Maven | Define camadas de dependências para otimização de build de imagem Docker |

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas, apenas realiza polling HTTP no BACEN.

---

## 11. Filas Geradas

O sistema publica mensagens em 3 tópicos do Google Cloud Pub/Sub:

1. **business-spag-pixx-receber-mensagem-spi-ba**: Recebe os XMLs das mensagens PIX processadas com header contendo timestamp de recepção
2. **business-spag-pixx-salvar-mensagem**: Recebe objetos JSON de auditoria completa (AuditJson) para persistência
3. **business-spag-pixx-metricas-liquidacao**: Recebe objetos JSON de métricas (SpiMetrics) para análise de performance e liquidação

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **BACEN - Sistema de Pagamentos Instantâneos (SPI)** | API REST HTTPS | Integração principal via endpoints `/api/v1/out/13140088/stream/start` para receber mensagens PIX. Utiliza autenticação mútua TLS com certificados do HSM |
| **HSM Dinamo** | Biblioteca nativa (tacndjavalib) | Hardware Security Module para gerenciamento de chaves criptográficas e certificados digitais. Comunicação via socket na porta 4433 |
| **Google Cloud Pub/Sub** | Mensageria | Publicação de mensagens processadas, auditoria e métricas via biblioteca Atlante Sidecar |

**Detalhes da integração com BACEN:**
- Método GET: Busca mensagens disponíveis (timeout 7s em PRD, 0s em DES)
- Método DELETE: Confirma processamento de mensagens (timeout 2s)
- Headers customizados: PI-ResourceId, PI-Pull-Next, Content-Type multipart/mixed
- Autenticação: Certificado digital + chave privada armazenados no HSM

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com uso de interfaces (ports) e implementações (infrastructure)
- Uso adequado de padrões arquiteturais (Hexagonal Architecture)
- Tratamento de exceções customizado e específico
- Logging estruturado em JSON para observabilidade
- Configuração externalizada e parametrizada por ambiente
- Uso de Lombok para reduzir boilerplate
- Implementação de retry e tratamento de erros

**Pontos de Melhoria:**
- Classe `ReceberMensagemRepositoryImpl` muito extensa e com múltiplas responsabilidades (comunicação HSM, parsing de headers, conversão de datas)
- Uso de regex com `Pattern.quote` e `Matcher` de forma repetitiva poderia ser refatorado para métodos utilitários
- Variáveis estáticas públicas em `RouterConstants` (DELAY_GET_BACEN, DELAY_POOL_NEXT) quebram encapsulamento e podem causar problemas de concorrência
- Falta de testes unitários nos arquivos enviados (apenas estrutura de testes presente)
- Alguns métodos com lógica complexa de parsing XML poderiam usar bibliotecas especializadas (JAXB, XPath) ao invés de regex
- Comentários em português e inglês misturados
- Alguns logs com concatenação de strings ao invés de placeholders
- Falta de validação de nulidade em alguns pontos críticos
- Classe `TratarBoundaryProcessor` com método `process` muito extenso

O código é funcional e bem estruturado no nível arquitetural, mas poderia se beneficiar de refatorações para melhorar legibilidade, manutenibilidade e testabilidade.

---

## 14. Observações Relevantes

1. **Segurança**: O sistema utiliza HSM (Hardware Security Module) para armazenamento seguro de certificados digitais, garantindo conformidade com requisitos de segurança do BACEN

2. **Resiliência**: Implementa mecanismo de retry (2 tentativas) e DELETE automático de mensagens em caso de falha para evitar bloqueio do fluxo

3. **Performance**: Utiliza processamento paralelo para múltiplos XMLs em uma mesma resposta multipart, otimizando throughput

4. **Observabilidade**: Integração com OpenTelemetry e Prometheus para tracing distribuído e métricas de performance

5. **Multi-ambiente**: Configuração diferenciada para DES, UAT e PRD, incluindo timeouts, URLs e credenciais específicas

6. **Timezone**: Todo o sistema opera em UTC para garantir consistência temporal

7. **Containerização**: Dockerfile otimizado com múltiplas camadas de dependências para melhor cache e rebuild

8. **Infraestrutura como Código**: Arquivo `infra.yml` define toda a configuração de deployment no Kubernetes/OpenShift

9. **Métricas de Negócio**: Calcula delays específicos (DELAY_GET_BACEN, DELAY_POOL_NEXT) para monitoramento de SLA

10. **Bibliotecas Proprietárias**: Dependência de biblioteca Dinamo (tacndjavalib) não disponível em repositórios públicos

11. **Atlante Framework**: Utiliza framework interno do Banco Votorantim (Atlante) para padronização de microsserviços

12. **Limitação de Escala**: Uso de variáveis estáticas para controle de estado pode limitar escalabilidade horizontal

---