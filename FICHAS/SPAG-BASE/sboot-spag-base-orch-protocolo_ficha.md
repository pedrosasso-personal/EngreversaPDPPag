# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-spag-base-orch-protocolo** é um orquestrador de consulta de protocolos de pagamento desenvolvido em Java com Spring Boot e Apache Camel. O sistema integra múltiplas fontes de dados de protocolos (ITP e SPAG), realizando consultas sequenciais com fallback. Primeiro, valida a autorização do solicitante via CNPJ/CPF, depois busca o protocolo no sistema ITP e, caso não encontre, realiza uma busca no sistema SPAG. O componente atua como uma camada de orquestração que unifica o acesso a diferentes sistemas de protocolo de pagamentos.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal que inicializa a aplicação Spring Boot |
| **ProtocoloRouter** | Orquestra o fluxo principal de consulta de protocolos usando Apache Camel, definindo as rotas e sequência de execução |
| **ValidarClientIdProcessor** | Processa e prepara os dados para validação do CNPJ/CPF do solicitante |
| **ProtocoloItpRetornoProcessor** | Analisa a resposta do ITP e decide se deve buscar no SPAG |
| **ThrowExceptionProcessor** | Centraliza o tratamento de exceções e formatação de respostas de erro |
| **ProtocoloRepositoryImpl** | Implementa a integração com o serviço ITP de consulta de protocolos |
| **ProtocoloSpagRepositoryImpl** | Implementa a integração com o serviço SPAG de consulta de protocolos |
| **SegurancaRepositoryImpl** | Implementa a validação de autorização do documento do parceiro |
| **ProtocoloMapper** | Realiza mapeamento entre objetos de representação e domínio |
| **ApiClientConfiguration** | Configura os clientes HTTP para comunicação com APIs externas |
| **ProtocoloConfiguration** | Configura RestTemplate com autenticação básica para SPAG |
| **RouterProperties** | Armazena propriedades de configuração das URLs dos serviços |

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.7.18** (Framework principal)
- **Apache Camel 3.x** (Orquestração e roteamento)
- **Spring Security OAuth2** (Autenticação e autorização JWT)
- **ModelMapper** (Mapeamento de objetos)
- **Auth0 JWT** (Manipulação de tokens JWT)
- **RestTemplate** (Cliente HTTP)
- **OpenAPI Generator** (Geração de clientes a partir de especificações)
- **Logback** (Logging em formato JSON)
- **Spring Actuator** (Monitoramento e health checks)
- **Micrometer/Prometheus** (Métricas)
- **OpenTelemetry** (Observabilidade)
- **Maven** (Gerenciamento de dependências)
- **Docker** (Containerização)

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /protocolo/v1/consulta | Interface gerada via OpenAPI | Consulta integrada de protocolo de pagamento, buscando primeiro no ITP e depois no SPAG se necessário |

## 5. Principais Regras de Negócio

1. **Validação de Autorização**: Antes de consultar qualquer protocolo, o sistema valida se o CNPJ/CPF do solicitante está autorizado através do serviço de segurança (atom-seguranca)

2. **Busca Sequencial com Fallback**: O sistema primeiro tenta buscar o protocolo no ITP. Se não encontrar (erro "Protocolo nao encontrado"), automaticamente realiza uma segunda tentativa no sistema SPAG

3. **Extração de Client ID do Token JWT**: O sistema extrai o client ID do token JWT Bearer para validação de autorização

4. **Tratamento Centralizado de Exceções**: Todas as exceções são capturadas e tratadas de forma padronizada, retornando códigos HTTP apropriados (400, 401, 500)

5. **Autenticação Diferenciada por Sistema**: Utiliza Bearer Token (OAuth2) para ITP e autenticação básica (usuário/senha) para SPAG

6. **Sanitização de Logs**: Todos os logs são sanitizados para prevenir injection attacks

## 6. Relação entre Entidades

**Entidades de Request:**
- `ProtocoloRepresentation` → `ProtocoloDomainRequest`: Contém cnpjSolicitante, numeroProtocoloSolicitacao, numeroProtocoloSolicitacaoCliente, dataMovimento

**Entidades de Response:**
- `ProtocoloDomainResponse` (agregadora principal)
  - Contém `DadosProtocoloDomainResponse` (dados do protocolo)
  - Contém `DadosMovimentacaoDomainResponse` (dados da movimentação financeira)
  - Contém `ParticipanteDomainResponse` (beneficiário)
  - Contém `ParticipanteDomainResponse` (remetente)

**Relacionamento**: A resposta é composta por um objeto principal que agrega informações do protocolo, movimentação e participantes (beneficiário e remetente).

## 7. Estruturas de Banco de Dados Lidas

não se aplica

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | leitura | /usr/etc/log/ | Arquivo de configuração de logs em formato JSON, carregado em runtime |
| application.yml | leitura | src/main/resources | Arquivo de configuração principal da aplicação |
| application-local.yml | leitura | src/main/resources | Configurações específicas para ambiente local |
| layers.xml | leitura | src/main/resources | Configuração de camadas para otimização de build Docker |

## 10. Filas Lidas

não se aplica

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

| Sistema | Tipo | Descrição |
|---------|------|-----------|
| **sboot-sitp-base-atom-protocolo** | API REST (OAuth2) | Serviço de consulta de protocolos no sistema ITP. Endpoint: GET /protocolo |
| **sboot-spag-base-atom-seguranca** | API REST (OAuth2) | Serviço de validação de autorização de documentos de parceiros. Endpoint: POST /v1/seguranca/validar |
| **springboot-spag-base-consulta-conta-fintech** | API REST (Basic Auth) | Serviço de consulta de protocolos no sistema SPAG. Endpoint: POST /consulta/v2/consultaProtocolo |
| **Gateway OAuth** | Serviço de Autenticação | Serviço de geração de tokens JWT para autenticação nas APIs. Endpoint: /auth/oauth/v2/token-jwt |

## 13. Avaliação da Qualidade do Código

**Nota: 7.5/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com uso de padrões Repository e Processor
- Uso adequado de Apache Camel para orquestração de fluxos complexos
- Tratamento centralizado de exceções
- Sanitização de logs para segurança
- Configuração externalizada e separada por ambiente
- Uso de interfaces para abstrair implementações
- Documentação OpenAPI bem estruturada

**Pontos de Melhoria:**
- Constante duplicada `SHOULD_SEARCH_PROTOCOL_SPAG` e `VALIDATION_CLIENT_ID` com mesmo valor em RouterConstants
- Mensagens de erro hardcoded em várias classes (poderia usar arquivo de mensagens)
- Falta de validação de entrada mais robusta nos processors
- Uso de `ObjectMapper` instanciado localmente em ProtocoloSpagRepositoryImpl (deveria ser injetado)
- Alguns logs com informações sensíveis mesmo após sanitização
- Falta de testes unitários incluídos na análise
- Tratamento genérico de exceções em alguns pontos poderia ser mais específico
- Documentação inline limitada em algumas classes complexas

## 14. Observações Relevantes

1. **Arquitetura Multi-camadas**: O projeto utiliza uma estrutura de layers bem definida no Docker (layers.xml) para otimizar builds e deploys

2. **Ambientes Múltiplos**: Suporta configurações para DES, UAT e PRD com credenciais e URLs específicas gerenciadas via ConfigMaps e Secrets do Kubernetes

3. **Observabilidade**: Integração completa com OpenTelemetry, Prometheus e logs estruturados em JSON para facilitar monitoramento

4. **Segurança**: Implementa validação JWT com múltiplos issuers, sanitização de logs e autenticação diferenciada por sistema integrado

5. **Health Checks**: Configuração de probes de liveness e readiness para Kubernetes com tempos ajustados (liveness com 420s de delay inicial)

6. **Geração de Código**: Utiliza OpenAPI Generator para criar automaticamente clientes HTTP a partir das especificações Swagger, garantindo consistência

7. **Padrão Atlante**: Segue o padrão arquitetural Atlante do Banco Votorantim, utilizando chassis específico (pom-atle-base-sboot-orch-stateless-parent)

8. **Fallback Inteligente**: A lógica de fallback entre ITP e SPAG é transparente para o cliente, que recebe uma resposta unificada independente da origem