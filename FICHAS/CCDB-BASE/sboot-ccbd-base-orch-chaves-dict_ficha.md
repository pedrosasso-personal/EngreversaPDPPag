# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de orquestração de chaves DICT (Diretório de Identificadores de Contas Transacionais) para o ecossistema PIX do Banco Votorantim. O microserviço stateless gerencia o ciclo de vida completo das chaves PIX (consulta, inclusão, remoção e listagem), integrando-se com o DICT do Banco Central, sistemas internos de dados cadastrais, validação de contatos seguros e análise de fraudes. Suporta operações para dois bancos: BV (ISPB 59588111) e BVSA (ISPB 01858774), com autenticação OAuth2 JWT separada para cada instituição.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ChavesDictController** | Controller REST V1 - endpoints de consulta, inclusão, remoção e listagem de chaves PIX |
| **ChavesDictControllerV2/V3/V4** | Controllers REST versionados com melhorias incrementais (headers, body, novos endpoints) |
| **ChavesDictService** | Serviço principal de orquestração - coordena fluxos de negócio das chaves PIX |
| **ChavesDictConfiguration** | Configuração Spring - beans Camel, routers, repositories, RestTemplates com timeouts e segurança |
| **ApplicationConfiguration** | Configuração de clientes REST para APIs externas (dados cadastrais, contato seguro) |
| **AppProperties** | Propriedades de configuração (@ConfigurationProperties) - URLs, credenciais OAuth, constantes |
| **ConsultarChavesRepositoryImpl** | Repository para consulta de chaves no DICT via API REST |
| **IncluirChavesRepositoryImpl** | Repository para inclusão de chaves no DICT |
| **RemoverChavesRepositoryImpl** | Repository para remoção de chaves do DICT |
| **ListarChavesRepositoryImpl** | Repository para listagem de chaves por filtros |
| **ConsultarDadosCadastraisRepositoryImpl** | Repository para obtenção de dados cadastrais de contas |
| **ConsultarIsContatoSeguroRepositoryImpl** | Repository para validação de contato seguro |
| **ConsultarIsContatoSalvoRepositoryImpl** | Repository para verificação de contato salvo |
| **PubSubRepositoryImpl** | Repository para envio de estatísticas de fraude via Google Cloud PubSub |
| **GerarTokenJwtRepositoryImpl** | Repository para geração de token JWT BV (cache handler) |
| **GerarTokenJwtBvsaRepositoryImpl** | Repository para geração de token JWT BVSA (cache handler) |
| **ChavesDictMapper** | Mapper para conversões entre DTOs, Entities e Representations |
| **CamelContextWrapper** | Wrapper do contexto Apache Camel (ProducerTemplate, ConsumerTemplate) |
| **Routers Camel** | Rotas de orquestração (ConsultarChavesRouter, IncluirChavesRouter, RemoverChavesRouter, etc.) |
| **Processors Camel** | Processadores de transformação e enriquecimento de dados nos fluxos Camel |
| **ErrorFormat** | Utilitário para conversão de exceções em ResponseEntity padronizado |
| **ObterCpf** | Utilitário para extração de CPF/CNPJ do SecurityContext JWT ou request body |
| **DateFormat** | Utilitário para formatação de datas (LocalDate, LocalDateTime, OffsetDateTime) |

---

## 3. Tecnologias Utilizadas

- **Framework:** Spring Boot 2.x (parent arqt-base-master-springboot:4.0.3)
- **Linguagem:** Java 11
- **Build:** Maven 3.9
- **Orquestração:** Apache Camel 3.22.4
- **Segurança:** Spring Security 5.7.13, OAuth2 JWT (BV Security JWT 0.22.4)
- **Mensageria:** Google Cloud PubSub 1.2.8
- **Documentação:** Swagger/OpenAPI 3.0.0
- **Logging:** Logback com formato JSON (Jackson)
- **Testes:** JUnit 5, Mockito, RestAssured, ArchUnit 0.19.0
- **Cobertura:** Jacoco
- **Infraestrutura:** Kubernetes/OpenShift (GCP)
- **CI/CD:** Jenkins (springboot-ocp)
- **Bibliotecas:** JAXB, Tomcat 9.0.106, Protobuf 3.25.5, BV Audit 3.0.0

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | /v1/banco-digital/dict/chaves/{chave} | ChavesDictController | Consulta chave PIX por valor |
| POST | /v1/banco-digital/dict/chaves | ChavesDictController | Inclui nova chave PIX |
| GET | /v1/banco-digital/dict/chaves | ChavesDictController | Lista chaves PIX por filtros (conta/agência/banco) |
| GET | /v1/banco-digital/dict/chaves-identificacao | ChavesDictController | Lista chaves por identificação do titular |
| GET | /v1/banco-digital/dict/chaves/disponiveis | ChavesDictController | Lista chaves disponíveis para cadastro (CPF, CNPJ, EMAIL, PHONE, EVP) |
| DELETE | /v1/banco-digital/dict/chaves/{chave} | ChavesDictController | Remove chave PIX |
| GET | /v1/digital-bank/dict/keys/{keyValue} | ChavesDictController | Consulta chave com documento favorecido criptografado (Base64 reverse) |
| GET | /v2/banco-digital/dict/chaves/consultarChave | ChavesDictControllerV2 | Consulta chave V2 com parâmetros opcionais (bankCode, branch, accountNumber) |
| POST | /v2/banco-digital/dict/chaves/consultar | ChavesDictControllerV2 | Consulta chave PIX via body (RequestChavePixRepresentation) |
| DELETE | /v2/banco-digital/dict/chaves/excluirChave | ChavesDictControllerV2 | Remove chave V2 via body |
| DELETE | /v3/banco-digital/dict/chaves/excluirChave | ChavesDictControllerV3 | Remove chave V3 com headers (codigoBanco, codigoAgencia, numeroConta) |
| GET | /v3/banco-digital/dict/chaves/{chave} | ChavesDictControllerV3 | Consulta chave V3 com headers (bankCode, branch, accountNumber, document) |
| POST | /v4/banco-digital/dict/chaves/excluirChave | ChavesDictControllerV4 | Remove chave V4 via POST com headers |
| DELETE | /v4/banco-digital/dict/remove/chaves/{chave} | ChavesDictControllerV4 | Remove chave em encerramento de conta (header cpfCnpj) |

---

## 5. Principais Regras de Negócio

1. **Validação de Titularidade:** Verifica se a conta informada pertence ao CPF/CNPJ do titular antes de operações de inclusão/remoção
2. **Contato Seguro:** Valida se a chave consultada está cadastrada como contato seguro do usuário logado
3. **Contato Salvo:** Verifica se a chave está na lista de contatos salvos do usuário
4. **Dual Bank:** Suporta operações para BV (códigos 161/655, ISPB 59588111) e BVSA (códigos 436/413, ISPB 01858774) com tokens JWT separados
5. **Normalização de Nomes:** Remove acentos e caracteres especiais dos nomes de titulares (conversão ASCII)
6. **Tipos de Chave:** Suporta CPF, CNPJ, EMAIL, PHONE (celular) e EVP (chave aleatória)
7. **Tipos de Conta:** CACC (conta corrente), SVGS (poupança), TRAN (pagamento), SLRY (salário)
8. **EndToEndId:** Gera identificador único para transações PIX
9. **Análise de Fraude:** Envia estatísticas de chaves consultadas para análise via PubSub (KeyStatistics, OwnerStatistics)
10. **Validação CPF RBF:** Valida CPF do titular antes de inclusão de chaves
11. **Recuperação de Dados Cadastrais:** Busca nome, telefone e email do titular em múltiplas fontes (VUCL, GLOB)
12. **Tratamento de Erros DICT:** Converte códigos de erro do DICT BACEN (1001-5100) para exceções de negócio padronizadas
13. **Participantes PIX:** Enriquece dados com nome do banco participante (361 participantes mapeados)
14. **Chaves Disponíveis:** Identifica quais tipos de chave o usuário pode cadastrar (CPF, CNPJ, EMAIL, PHONE, EVP)

---

## 6. Relação entre Entidades

**Entry (Chave PIX):**
- Contém: key (valor da chave), keyType (tipo), owner (titular), account (conta), creationDate, statistics
- Relaciona-se com Owner (1:1) e Account (1:1)

**Owner (Titular):**
- Contém: taxIdNumber (CPF/CNPJ), name (nome), type (PF/PJ)
- Relaciona-se com Entry (1:N)

**Account (Conta):**
- Contém: participant (ISPB), branch (agência), accountNumber, accountType, accountBank (código banco)
- Relaciona-se com Entry (1:N)

**ContatoSeguro:**
- Contém: isContatoSeguro (boolean), dataEfetivacao, dataInclusao
- Relaciona-se com Entry via chave PIX

**DadosPessoais:**
- Contém: cpfCnpj, email, phone, nome
- Relaciona-se com Owner via taxIdNumber

**ContaCorrente:**
- Contém: codigo, cpfCnpj, nomeTitular, numeroBanco, numeroAg, numeroConta, tipoModalidade
- Relaciona-se com Account via numeroConta/numeroAg/numeroBanco

**ParticipanteInfo:**
- Contém: ispb, nomeParticipante
- Relaciona-se com Account via participant (ISPB)

**KeyStatistics/OwnerStatistics:**
- Estatísticas de fraude relacionadas a Entry
- Enviadas via PubSub para análise

---

## 7. Estruturas de Banco de Dados Lidas

Não se aplica. O sistema não acessa diretamente bancos de dados relacionais ou NoSQL. Todas as operações são realizadas via APIs REST de sistemas externos.

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema não realiza operações diretas de INSERT/UPDATE/DELETE em bancos de dados. Todas as alterações são realizadas via APIs REST de sistemas externos (DICT, dados cadastrais, contatos).

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | Spring Boot | Configurações da aplicação (URLs, credenciais, timeouts) |
| logback-local.xml | Leitura | Logback | Configuração de logging para ambiente local |
| logback-spring.xml | Leitura | Logback | Configuração de logging para ambientes (des/qa/uat/prd) |
| infra.yml | Leitura | Kubernetes/OpenShift | Manifesto de infraestrutura (configmaps, secrets, deployment) |
| jenkins.properties | Leitura | Jenkins CI/CD | Configurações de build e deploy |
| cacerts | Leitura | JVM | Certificados Java montados via volume Kubernetes |

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas (JMS, Kafka, RabbitMQ).

---

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Responsável | Breve Descrição |
|--------------|-----------|-------------------|-----------------|
| business-ccbd-base-chaves-pix | Google Cloud PubSub | PubSubRepositoryImpl | Envia estatísticas de chaves PIX consultadas para análise de fraude (DadosEstatisticasChavesDTO com KeyStatistics e OwnerStatistics) |

---

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| **DICT PIX (BACEN)** | API REST | Consulta, inclusão, remoção e listagem de chaves PIX no diretório centralizado |
| **API EndToEndId** | API REST | Geração de identificadores únicos para transações PIX |
| **API Consulta Pessoa** | API REST (Basic Auth) | Recuperação de dados de pessoa por número de conta |
| **API Dados Pessoais (VUCL)** | API REST (OAuth2 JWT) | Obtenção de dados cadastrais (CPF/CNPJ, telefone, email, nome) |
| **API Lista de Contas** | API REST (Basic Auth) | Consulta de contas correntes por CPF/CNPJ |
| **API Contato Seguro** | API REST (OAuth2 JWT) | Validação de contato seguro (isContatoSeguro) |
| **API Contato Salvo** | API REST (OAuth2 JWT) | Verificação de contato salvo na lista do usuário |
| **API Participantes SPI** | API REST (OAuth2 JWT) | Consulta de dados de participantes PIX por ISPB |
| **API Global (GetContasByCpfCnpjApi)** | API REST | Consulta de dados cadastrais globais (numeroBanco, contas correntes) |
| **API Token JWT BV** | API REST (OAuth2) | Geração de token de autenticação para APIs do Banco Votorantim |
| **API Token JWT BVSA** | API REST (OAuth2) | Geração de token de autenticação para APIs do Banco Votorantim S.A. |
| **Google Cloud PubSub** | Mensageria | Publicação de estatísticas de fraude (tópico business-ccbd-base-chaves-pix) |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 8/10

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada em camadas (controllers, services, repositories, domain)
- Uso adequado de padrões de projeto (Repository, Service, Mapper, Builder)
- Separação clara de responsabilidades entre módulos (common, domain, application)
- Orquestração com Apache Camel bem organizada (routers e processors separados)
- Tratamento de exceções padronizado e centralizado (ErrorFormat, ExceptionHandler)
- Configuração externalizada e versionada (application.yml, infra.yml)
- Cobertura de testes unitários e funcionais (JUnit5, Mockito, RestAssured)
- Documentação via Swagger/OpenAPI versionada (V1, V2, V3, V4)
- Uso de cache para tokens JWT (TokenCacheHandlerAbstract)
- Logging estruturado em JSON
- Suporte a múltiplos ambientes (des, qa, uat, prd)

**Pontos de Melhoria:**
- Alguns métodos com alta complexidade ciclomática (ChavesDictService, routers Camel)
- Duplicação de lógica entre versões de controllers (V1, V2, V3, V4)
- Falta de documentação inline em algumas classes complexas (processors Camel)
- Alguns nomes de variáveis poderiam ser mais descritivos (ex: "nu", "cd", "tp")
- Ausência de testes de integração end-to-end documentados
- Configurações hardcoded em alguns enums (ParticipanteEnum com 361 participantes)
- Falta de circuit breaker/retry explícito para chamadas externas (apenas timeouts)
- Alguns DTOs com muitos campos opcionais (Entry, Account)

O código demonstra maturidade técnica, boas práticas de engenharia de software e preocupação com manutenibilidade. A arquitetura baseada em Camel permite flexibilidade e extensibilidade. A nota reflete um sistema bem construído, com espaço para melhorias incrementais em complexidade e documentação.

---

## 14. Observações Relevantes

1. **Versionamento de API:** Sistema possui 4 versões de API REST (V1, V2, V3, V4) com evolução incremental de funcionalidades, mantendo retrocompatibilidade
2. **Dual Bank:** Arquitetura suporta operações simultâneas para BV e BVSA com tokens JWT e configurações separadas
3. **Segurança:** Implementa OAuth2 JWT com propagação de contexto de segurança (REST_API_TIMEOUT_SECURITY) e Basic Auth para APIs legadas
4. **Resiliência:** Configuração de timeouts (10s conexão/leitura), pool de conexões (max 50, max 5 por rota), retry implícito via Camel
5. **Observabilidade:** Endpoints de health/metrics/prometheus em porta separada (9090), logging estruturado JSON, trilha de auditoria (BV Audit 3.0.0)
6. **Infraestrutura:** Deploy em Kubernetes/OpenShift (GCP) com probes, resources definidos (1CPU/1Gi), ServiceAccount específico
7. **Compliance PIX:** Implementa especificações do DICT BACEN para chaves PIX, incluindo tratamento de códigos de erro padronizados
8. **Análise de Fraude:** Integração com sistema de detecção de fraudes via PubSub, enviando estatísticas de consultas (KeyStatistics, OwnerStatistics, FraudMarkers)
9. **Normalização de Dados:** Tratamento de caracteres especiais em nomes (remoção de acentos), formatação de telefones (ranking de melhor número), seleção de email mais recente
10. **Extensibilidade:** Uso de Apache Camel facilita adição de novos fluxos e integrações sem impacto em código existente
11. **Mapeamento de Participantes:** Enum com 361 participantes PIX mapeados (ISPB -> nome banco) para enriquecimento de dados
12. **Tipos de Chave Suportados:** CPF, CNPJ, EMAIL, PHONE (celular), EVP (chave aleatória)
13. **Tipos de Conta Suportados:** CACC (corrente), SVGS (poupança), TRAN (pagamento), SLRY (salário)
14. **Geração de EndToEndId:** Identificador único para transações PIX gerado via API externa
15. **Validação de Contatos:** Dupla validação (contato seguro + contato salvo) para operações sensíveis
16. **CI/CD:** Pipeline Jenkins com profiles de teste (unit, integration, functional, architecture), cobertura Jacoco, build Maven multi-módulo

---

**Documento gerado em:** 2025-01-XX  
**Versão do Sistema:** 0.48.0  
**Responsável pela Análise:** Agente de Engenharia Reversa IA