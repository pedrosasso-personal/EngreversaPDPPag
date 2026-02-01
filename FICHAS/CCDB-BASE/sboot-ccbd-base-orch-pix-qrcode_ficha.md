---
## Ficha Técnica do Sistema

### 1. Descrição Geral
Sistema orquestrador de operações PIX para geração e consulta de QRCodes, integrado ao ecossistema de pagamentos instantâneos do Banco Central. O sistema atua como intermediário entre aplicações cliente e serviços externos (DICT, SPAG, CCBD, VUCL), realizando validações de titularidade, enriquecimento de dados (saldo, cartões, dados cadastrais), verificação de contato seguro e envio de estatísticas para análise de fraudes. Suporta operações para dois bancos (BV - ISPB 161 e BVSA - ISPB 436) com autenticação OAuth2 específica para cada instituição. Implementa fluxos para QRCode estático/dinâmico, PIX Automático (recorrência) e operações de saque-troco.

---

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **PixQrcodeController** | Controlador REST v1 - endpoints de geração e consulta de QRCode PIX |
| **PixQrCodeControllerV2** | Controlador REST v2 - consulta QRCode com suporte a recorrência e saque-troco |
| **PixQrcodeService** | Serviço orquestrador principal - coordena fluxos de geração/consulta via Apache Camel |
| **PixQrcodeMapper** | Mapeamento entre objetos de domínio e representações REST (v1/v2) |
| **ConsultarQRCodeRouter** | Roteador Camel - orquestra consulta QRCode com validações e enriquecimento de dados |
| **GerarQRCodeRouter** | Roteador Camel - orquestra geração de QRCode estático/dinâmico |
| **ConsultarChaveDictRouter** | Roteador Camel - consulta chaves no DICT com roteamento BV/BVSA |
| **ValidarTitularidadeRouter** | Roteador Camel - valida titularidade de documento/conta |
| **EnviarEstatisticasChaveParaFraudesRouter** | Roteador Camel - envia estatísticas PIX para análise de fraudes via PubSub |
| **ConsultarQRCodeRepositoryImpl** | Decodifica QRCode via API externa, trata PIX Automático e recorrência |
| **ConsultarChaveRepositoryImpl** | Consulta chaves DICT (interno/externo) via REST |
| **GerarQRCodeRepositoryImpl** | Gera QRCode estático/dinâmico via API externa |
| **ValidarTitularidadeRepositoryImpl** | Valida titular de conta via dados cadastrais |
| **ConsultarIsContatoSeguroRepositoryImpl** | Verifica se destinatário é contato seguro cadastrado |
| **ConsultarSaldoRepositoryImpl** | Consulta saldo bancário da conta |
| **ListaCartoesUsuarioRepositoryImpl** | Lista cartões do usuário |
| **ObterDadosCadastraisRepositoryImpl** | Consulta dados pessoais/cadastrais do cliente |
| **ParticipantesPixRepositoryImpl** | Consulta participantes PIX (bancos) por ISPB |
| **PubSubRepositoryImpl** | Publica estatísticas de chaves PIX em fila GCP PubSub para fraudes |
| **GerarTokenJwtRepositoryImpl / BvsaRepositoryImpl** | Gera tokens OAuth2 para BV e BVSA |
| **GerarEndToEndIdRepositoryImpl** | Gera identificador único de transação (EndToEndId) |
| **ErrorFormat** | Converte exceções em representações de erro padronizadas |
| **ObterCpf** | Extrai CPF/CNPJ de token JWT ou body da requisição |

---

### 3. Tecnologias Utilizadas

- **Framework**: Spring Boot 2.x
- **Orquestração**: Apache Camel 3.x (roteamento, integração)
- **Segurança**: Spring Security OAuth2 (Resource Server), JWT
- **Mensageria**: Google Cloud PubSub (Spring Cloud GCP)
- **HTTP Client**: RestTemplate, Apache HttpClient (pool de conexões)
- **Documentação**: Swagger/OpenAPI 3.0
- **Persistência**: Não há acesso direto a banco de dados (integração via APIs REST)
- **Logging**: Logback, SLF4J
- **Testes**: JUnit 5, Mockito
- **Build**: Maven
- **Serialização**: Jackson (JSON)
- **Utilitários**: Lombok, Apache Commons

---

### 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/banco-digital/pix/qrcode` | PixQrcodeController | Gera QRCode PIX estático ou dinâmico |
| POST | `/v1/banco-digital/pix/qrcode/decodificar` | PixQrcodeController | Consulta/decodifica QRCode PIX (versão 1) |
| POST | `/v2/banco-digital/pix/qrcode/decodificar` | PixQrCodeControllerV2 | Consulta/decodifica QRCode PIX com suporte a recorrência, saque-troco e contato seguro (versão 2) |

**Headers obrigatórios para consulta**: `codigoBanco`, `agencia`, `conta`, `Authorization` (Bearer token)

---

### 5. Principais Regras de Negócio

1. **Validação de Titularidade**: Verifica se o CPF/CNPJ do usuário autenticado corresponde ao titular da conta informada, consultando dados cadastrais.

2. **Roteamento BV/BVSA**: Diferencia operações entre Banco Votorantim (ISPB 161, CNPJ 59.588.111) e BV S.A. (ISPB 436, CNPJ 01.858.774), gerando tokens OAuth2 específicos para cada instituição.

3. **Tipo de Conta Favorecido**: Para contas BV/BVSA, se o CNPJ do favorecido for igual ao ISPB do banco, classifica como CONTA_CONTROLE (código 6), caso contrário CONTA_CORRENTE (código 5).

4. **Validação de Chave DICT**: Antes de gerar QRCode, valida se a chave PIX existe no DICT e se o documento do titular corresponde ao owner da chave.

5. **Enriquecimento de Dados**: Ao consultar QRCode, enriquece resposta com:
   - Saldo bancário da conta
   - Lista de cartões do usuário
   - Nome do banco destinatário (via ISPB)
   - Status de contato seguro do destinatário
   - Dados cadastrais do titular

6. **PIX Automático (Recorrência)**: Identifica e processa QRCodes de PIX recorrente, extraindo status, datas de criação/efetivação e valores.

7. **Saque-Troco**: Calcula valores finais considerando operações de saque e troco, adicionando ao valor original da transação.

8. **Geração de EndToEndId**: Gera identificador único de transação para rastreabilidade no sistema PIX.

9. **Estatísticas de Fraude**: Envia dados estatísticos de chaves PIX (keyStatistics, ownerStatistics) para fila de análise de fraudes via PubSub quando disponíveis.

10. **Tratamento de Erros**: Converte erros de APIs externas em códigos de exceção padronizados (ExceptionReasonEnum), com fallback para erro genérico em casos não mapeados.

---

### 6. Relação entre Entidades

**Entidades Principais:**

- **Entry**: Representa uma chave DICT com dados do proprietário (owner), conta (account) e estatísticas (keyStatistics, ownerStatistics).
  - Relacionamento: 1 Entry possui 1 Owner, 1 Account, 0..1 KeyStatistics, 0..1 OwnerStatistics

- **QRCodeQueryResponse**: Agregador de resposta de consulta QRCode.
  - Relacionamento: 1 QRCodeQueryResponse possui 1 Entry, 0..1 Withdrawal, 0..1 Recurrence, 0..N DetalheCartao, 1 saldoAtual, 0..1 ContatoSeguro

- **QRCodeRequest / QRCodeStaticRequest**: Requisições de geração de QRCode.
  - Relacionamento: 1 Request possui 1 Debtor, 1 Creditor, 0..1 Withdrawal

- **Withdrawal**: Dados de saque-troco.
  - Relacionamento: 1 Withdrawal possui 0..1 Change (troco), 0..1 Withdraw (saque)

- **Recurrence**: Dados de PIX Automático.
  - Relacionamento: 1 Recurrence possui valores, datas e status de recorrência

- **ContatoSeguro**: Dados de contato seguro do destinatário.
  - Relacionamento: Vinculado a Entry via chave PIX ou dados bancários

**Fluxo de Relacionamentos:**
```
QRCodeQueryResponse
├── Entry (chave DICT)
│   ├── Owner (proprietário)
│   ├── Account (conta)
│   ├── KeyStatistics (estatísticas chave)
│   └── OwnerStatistics (estatísticas proprietário)
├── Withdrawal (saque-troco)
│   ├── Change (troco)
│   └── Withdraw (saque)
├── Recurrence (PIX Automático)
├── List<DetalheCartao> (cartões)
├── BigDecimal saldoAtual
└── ContatoSeguro (contato seguro)
```

---

### 7. Estruturas de Banco de Dados Lidas

não se aplica

*O sistema não acessa diretamente bancos de dados. Todas as consultas são realizadas via APIs REST externas.*

---

### 8. Estruturas de Banco de Dados Atualizadas

não se aplica

*O sistema não realiza operações de escrita em bancos de dados. Todas as atualizações são realizadas via APIs REST externas.*

---

### 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | Spring Boot (startup) | Configurações de profiles (local, des, qa, uat, prd), URLs de serviços externos, credenciais OAuth, logging |
| logback-local.xml | Leitura | Logback (startup) | Configuração de logs para ambiente local (console appender) |
| swagger YAML specs | Leitura | OpenApiConfiguration | Especificações OpenAPI v1/v2 para documentação de APIs |
| infra.yml | Leitura | Kubernetes (deploy) | ConfigMaps, Secrets, recursos, probes para ambientes des/qa/uat/prd |

*Observação: O sistema não gera arquivos de saída. Logs são direcionados para console/stdout.*

---

### 10. Filas Lidas

não se aplica

*O sistema não consome mensagens de filas. Atua apenas como produtor.*

---

### 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Responsável | Descrição |
|--------------|------------|-------------------|-----------|
| Tópico PubSub Fraudes | Google Cloud PubSub | PubSubRepositoryImpl, EnviarEstatisticasChaveParaFraudesRouter | Publica estatísticas de chaves PIX (keyStatistics, ownerStatistics) para análise de fraudes. Payload: DadosEstatisticasChavesDTO com CPF consultante, chave PIX e estatísticas |

**Configuração por ambiente:**
- DES: `projects/bv-pix-des/topics/fraudes-estatisticas-chaves-pix`
- QA: `projects/bv-pix-qa/topics/fraudes-estatisticas-chaves-pix`
- UAT: `projects/bv-pix-uat/topics/fraudes-estatisticas-chaves-pix`
- PRD: `projects/bv-pix-prd/topics/fraudes-estatisticas-chaves-pix`

---

### 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição | Endpoints Principais |
|-----------------|------|-----------|---------------------|
| **SPAG (Sistema de Pagamentos)** | REST API | Geração/consulta QRCode, consulta chaves DICT, geração EndToEndId, consulta participantes PIX | `/qrcode`, `/dict/entries`, `/end-to-end-id`, `/participants` |
| **CCBD (Core Bancário)** | REST API | Consulta saldo bancário e lista de cartões do usuário | `/saldo`, `/cartoes` |
| **VUCL (Dados Cadastrais)** | REST API | Consulta dados pessoais/cadastrais do cliente | `/dados-cadastrais` |
| **GLOB (Dados Cliente)** | REST API | Consulta dados do cliente (alternativa VUCL) | `/cliente` |
| **Contato Seguro API** | REST API (atom-contato-seguro) | Verifica se destinatário está cadastrado como contato seguro | `/contato-seguro/consultar` |
| **OAuth BV** | REST API | Geração de token JWT para autenticação em serviços BV | `/oauth/token` (grant_type: client_credentials) |
| **OAuth BVSA** | REST API | Geração de token JWT para autenticação em serviços BVSA | `/oauth/token` (grant_type: client_credentials) |
| **Google Cloud PubSub** | Mensageria | Publicação de estatísticas de chaves PIX para análise de fraudes | Tópico: `fraudes-estatisticas-chaves-pix` |

**Autenticação:**
- APIs SPAG/CCBD/VUCL: Bearer token OAuth2 (BV ou BVSA)
- Contato Seguro: ApiClient configurado via Spring
- PubSub: Credenciais GCP via Spring Cloud

**Headers customizados:**
- `document`: CNPJ do banco (BV ou BVSA)
- `taxIdNumber`: CPF/CNPJ do usuário
- `endToEndId`: Identificador único de transação
- `codigoBanco`, `agencia`, `conta`: Dados da conta para consultas

---

### 13. Avaliação da Qualidade do Código

**Nota:** 8/10

**Justificativa:**

**Pontos Positivos:**
- **Arquitetura bem estruturada**: Separação clara de responsabilidades com uso de padrões (Repository, Service, Controller, Mapper).
- **Uso adequado de Apache Camel**: Orquestração de fluxos complexos com roteadores bem definidos e reutilizáveis.
- **Tratamento de erros robusto**: Conversão padronizada de exceções com enum ExceptionReasonEnum e classe ErrorFormat.
- **Cobertura de testes abrangente**: Testes unitários para todos os componentes principais (controllers, repositories, mappers, utils).
- **Configuração externalizada**: Uso de ConfigProperties e profiles Spring para diferentes ambientes.
- **Documentação de APIs**: Swagger/OpenAPI configurado para v1 e v2.
- **Segurança**: Integração com OAuth2 Resource Server e validação de tokens JWT.

**Pontos de Melhoria:**
- **Tratamento silencioso de erros**: Alguns repositórios (ConsultarSaldo, ListaCartoes, ObterDadosCadastrais, ContatoSeguro) tratam erros HTTP apenas com log, sem propagar exceções, o que pode ocultar falhas importantes.
- **Acoplamento a RestTemplate**: Uso direto de RestTemplate em vez de abstrações mais modernas (WebClient) ou clientes declarativos (Feign).
- **Constantes hardcoded**: CNPJs e ISPBs de bancos em múltiplos locais (AppProperties, BankEnum, PixQrcodeMapper), dificultando manutenção.
- **Lógica de negócio em Mapper**: PixQrcodeMapper contém regras de negócio (tipo conta favorecido), deveria estar em Service.
- **Falta de circuit breaker**: Integrações externas sem proteção contra falhas em cascata (Hystrix/Resilience4j).
- **Documentação inline limitada**: Poucos comentários JavaDoc em classes complexas.

**Recomendações:**
1. Migrar de RestTemplate para WebClient (reativo) ou Feign (declarativo).
2. Implementar circuit breaker e retry policies para integrações externas.
3. Centralizar constantes de bancos em enum único.
4. Mover lógica de negócio de Mapper para Service.
5. Propagar exceções em repositórios críticos (saldo, cartões) em vez de tratamento silencioso.
6. Adicionar JavaDoc em classes principais e métodos complexos.

---

### 14. Observações Relevantes

1. **Dual Banking Support**: Sistema projetado para operar com dois bancos distintos (BV e BVSA), com roteamento automático de tokens OAuth2 e headers específicos por instituição.

2. **Orquestração Camel**: Uso extensivo de Apache Camel para orquestração de fluxos assíncronos, permitindo composição de operações complexas (validação → consulta → enriquecimento → estatísticas).

3. **Versionamento de API**: Implementação de v1 e v2 de endpoints, com v2 adicionando suporte a PIX Automático (recorrência) e saque-troco.

4. **Segurança em Camadas**: Validação de titularidade em múltiplos pontos (token JWT, dados cadastrais, owner da chave DICT).

5. **Resiliência Parcial**: Falhas em serviços não críticos (saldo, cartões, contato seguro) não impedem conclusão da operação principal (consulta QRCode).

6. **Compliance PIX**: Implementação de regras do Banco Central (geração EndToEndId, estatísticas de fraude, validação de participantes).

7. **Configuração por Ambiente**: Infraestrutura Kubernetes com ConfigMaps/Secrets específicos por ambiente (des, qa, uat, prd).

8. **Timeouts Configurados**: Conexões HTTP com timeout de 10s (conexão e leitura), pool de 50 conexões máximas (5 por rota).

9. **Observabilidade**: Endpoints Actuator para health checks (liveness/readiness probes) na porta 9090.

10. **Limitações Conhecidas**: 
    - Não há cache de tokens OAuth2 (gerados a cada requisição).
    - Ausência de métricas de performance (Micrometer/Prometheus).
    - Logs em português, dificultando internacionalização.

11. **Dependências Críticas**: Sistema depende fortemente de disponibilidade de APIs externas (SPAG, CCBD, VUCL). Falha em SPAG impede operações principais.

12. **Modelo de Dados Rico**: QRCodeQueryResponse agrega dados de múltiplas fontes (DICT, saldo, cartões, participantes, contato seguro), fornecendo visão completa para cliente.

---

**Documento gerado em:** 2025-01-XX  
**Versão do Sistema:** Não especificada (inferida como 1.x/2.x baseado em versionamento de APIs)  
**Responsável pela Análise:** Agente de Engenharia Reversa