# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema orquestrador responsável pelo envio de mensagens do Canal Secundário do PIX para o BACEN (Banco Central do Brasil) via API HSM Dinamo. O sistema consome mensagens de filas PubSub do Google Cloud Platform, processa mensagens XML no padrão ISO 20022 (pacs.008, pacs.002, etc.), realiza assinatura digital via HSM, envia ao BACEN e registra auditoria. Suporta múltiplos ISPBs (BV, BVSA e Bankly) com configurações distintas de certificados e credenciais.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot para inicialização da aplicação |
| `SendMessagesSPIListener` | Consumer de mensagens PubSub para envio de mensagens SPI |
| `SendMessageRouter` | Roteador Camel principal que orquestra o fluxo de envio de mensagens |
| `SenderIspbProcessor` | Identifica o ISPB remetente e seleciona configurações apropriadas (BV/BVSA/Bankly) |
| `PixResponseStatusProcessor` | Valida status HTTP da resposta do BACEN e extrai tipo de mensagem |
| `PixResponseToAuditProcessor` | Converte resposta PIX em payload de auditoria |
| `RemoveBucketTokenProcessor` | Gera payloads para remoção de tokens de rate limiting |
| `SendMessageBvRepositoryAdapter` | Adaptador para envio de mensagens do BV via HSM Dinamo |
| `SendMessageBvsaRepositoryAdapter` | Adaptador para envio de mensagens do BVSA via HSM Dinamo |
| `SendMessageBanklyRepositoryAdapter` | Adaptador para envio de mensagens do Bankly via HSM Dinamo |
| `SendMessageRepository` | Classe base abstrata com lógica comum de envio ao BACEN |
| `PublishMessageRouter` | Roteador para publicação de mensagens em tópicos PubSub |
| `CamelContextWrapper` | Wrapper para gerenciamento do contexto Apache Camel |
| `XmlUtils` | Utilitários para manipulação e compressão de XML |

## 3. Tecnologias Utilizadas

- **Framework Base**: Spring Boot 2.x (Java 11)
- **Orquestração**: Apache Camel
- **Mensageria**: Google Cloud PubSub
- **Segurança**: Spring Security OAuth2 (JWT)
- **HSM**: Dinamo Networks TacNDJavaLib 4.7.38
- **Serialização**: Jackson (JSON/XML), JAXB
- **Logging**: Logback com formato JSON
- **Containerização**: Docker (OpenJDK 11 com OpenJ9)
- **Cloud**: Google Cloud Platform (GCP)
- **Build**: Maven
- **Testes**: JUnit 5, Mockito
- **Infraestrutura**: Kubernetes/OpenShift

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema orientado a eventos (event-driven) que consome mensagens de filas PubSub. Não expõe endpoints REST de negócio, apenas endpoints de gerenciamento (actuator).

## 5. Principais Regras de Negócio

1. **Roteamento por ISPB**: Identifica o ISPB remetente (BV: 59588111, BVSA: 01858774, Bankly: 13140088) e seleciona credenciais HSM e endpoints BACEN correspondentes
2. **Validação de Resposta BACEN**: Aceita apenas respostas HTTP 201 (Created) como sucesso
3. **Compressão de Mensagens**: Todas as mensagens XML são comprimidas com GZIP antes do envio ao BACEN
4. **Assinatura Digital**: Mensagens são assinadas digitalmente via HSM Dinamo com certificados ICP-Brasil
5. **Remoção de Tokens**: Para mensagens específicas (PACS002, PACS008, PIBR001, PAIN013, PAIN014), remove tokens de rate limiting após envio bem-sucedido
6. **Auditoria Completa**: Registra request/response completos incluindo headers, body, certificados e timestamps
7. **Retry**: Implementa retry automático (2 tentativas) em caso de falha de comunicação
8. **Extração de Metadados**: Extrai EndToEndId, InstructionId, tipo de mensagem e versão para auditoria e métricas
9. **Gestão de Sessão HSM**: Abre e fecha sessão HSM para cada envio de mensagem

## 6. Relação entre Entidades

**Entidades de Domínio:**
- `AuditPayload`: Payload completo de auditoria (request, response, certificados, metadados)
- `RemoveTokenPayload`: Payload para remoção de token de rate limiting (api, ispb, statusCode)
- `DinamoProperties`: Configurações de conexão HSM (endpoint, porta, credenciais, certificados)
- `CredentialProperties`: Credenciais HSM (username, password, key, chain, pixChain)
- `EndpointProperties`: URLs de endpoints (BACEN, Dinamo)

**Enums:**
- `DirectPartnerEnum`: Parceiros diretos (BV, BVSA, BANKLY) com seus ISPBs
- `MessageTypeEnum`: Tipos de mensagem PIX (PACS002, PACS008, PIBR001, PAIN013, PAIN014)

**Relacionamentos:**
- DinamoProperties contém CredentialProperties e EndpointProperties
- DirectPartnerEnum mapeia para DinamoProperties específico
- MessageTypeEnum determina se deve remover token de rate limiting

## 7. Estruturas de Banco de Dados Lidas

Não se aplica. O sistema não realiza leitura direta de banco de dados.

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema não realiza escrita direta em banco de dados. Persistência é feita via mensageria (PubSub).

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `pacs.008.spi.1.14.xsd` | Leitura | `src/main/resources/xsd/` | Schema XSD para validação de mensagens PACS.008 do SPI |
| `logback-spring.xml` | Leitura | `src/main/resources/` e `/usr/etc/log/` | Configuração de logging em formato JSON |
| `application.yml` | Leitura | `src/main/resources/` | Configurações da aplicação por ambiente |
| `application-local.yml` | Leitura | `src/main/resources/` | Configurações específicas do ambiente local |

## 10. Filas Lidas

| Nome da Fila | Tecnologia | Classe Consumidora | Descrição |
|--------------|------------|-------------------|-----------|
| `business-spag-pixx-envio-mensagem-secundario-spi-sub` | Google Cloud PubSub | `SendMessagesSPIListener` | Subscription para consumo de mensagens XML PIX a serem enviadas ao BACEN via canal secundário |

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Produtora | Descrição |
|--------------|------------|------------------|-----------|
| `business-spag-pixx-salvar-mensagem` | Google Cloud PubSub | `PublishMessageRouter` | Tópico para salvar mensagens de auditoria completas (request/response) |
| `business-spag-pixx-metricas-liquidacao` | Google Cloud PubSub | `PublishMessageRouter` | Tópico para métricas de liquidação e indicadores de performance |
| `business-spag-pixx-remover-ficha-bucket` | Google Cloud PubSub | `PublishMessageRouter` | Tópico para remoção de tokens de rate limiting após envio bem-sucedido |

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| **BACEN (Banco Central)** | API REST HTTPS | Envio de mensagens PIX via endpoints específicos por ISPB (icom-sec.pi.rsfn.net.br e icom-sec-h.pi.rsfn.net.br) |
| **HSM Dinamo** | API Nativa | Assinatura digital de mensagens XML com certificados ICP-Brasil (portas 4433) |
| **Google Cloud PubSub** | Mensageria | Consumo de mensagens a enviar e publicação de auditoria/métricas |
| **OAuth2/JWKS** | Autenticação | Validação de tokens JWT via endpoints do API Gateway BV |

**Endpoints BACEN por ISPB:**
- BV (59588111): `https://icom-sec.pi.rsfn.net.br:17422/api/v1/in/59588111/msgs`
- BVSA (01858774): `https://icom-sec.pi.rsfn.net.br:17422/api/v1/in/01858774/msgs`
- Bankly (13140088): `https://icom-sec.pi.rsfn.net.br:17422/api/v1/in/13140088/msgs`

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada com separação clara de responsabilidades (processors, routers, adapters)
- Uso adequado de padrões de projeto (Strategy para múltiplos ISPBs, Adapter para repositórios)
- Boa cobertura de testes unitários com uso de fixtures e mocks
- Configuração externalizada por ambiente (des, uat, prd)
- Tratamento de exceções com retry automático
- Logging estruturado em JSON para observabilidade
- Uso de Lombok para reduzir boilerplate
- Documentação presente (README, comentários)

**Pontos de Melhoria:**
- Algumas classes com múltiplas responsabilidades (ex: PixResponseToAuditProcessor faz parsing e mapeamento)
- Strings hardcoded em alguns processadores (tags XML, códigos)
- Falta de validação de entrada em alguns pontos
- Gestão de sessão HSM poderia ser otimizada (pool de conexões)
- Testes de integração ausentes
- Documentação técnica poderia ser mais detalhada

## 14. Observações Relevantes

1. **Segurança Crítica**: Sistema lida com certificados digitais ICP-Brasil e comunicação com infraestrutura crítica nacional (BACEN). Credenciais são gerenciadas via secrets do Kubernetes.

2. **Multi-tenant**: Suporta três instituições financeiras distintas (BV, BVSA, Bankly) com configurações isoladas de HSM e certificados.

3. **Ambientes**: Configurado para três ambientes (DES, UAT, PRD) com endpoints BACEN distintos (homologação e produção).

4. **Performance**: Configurado com paralelismo limitado (1 thread) no PubSub para controle de taxa de envio ao BACEN.

5. **Observabilidade**: Integrado com Prometheus para métricas e logging estruturado para análise centralizada.

6. **Resiliência**: Implementa retry, timeout configurável e tratamento de falhas de sessão HSM.

7. **Compliance**: Mensagens seguem padrão ISO 20022 com schemas XSD validados e assinatura digital obrigatória.

8. **Infraestrutura**: Containerizado com imagem Alpine otimizada, bibliotecas nativas HSM incluídas no container.

9. **Rate Limiting**: Sistema de tokens (bucket) para controle de taxa de envio, com remoção automática após sucesso.

10. **Auditoria Completa**: Todos os envios são auditados com request/response completos, certificados utilizados e timestamps precisos para rastreabilidade e conformidade regulatória.