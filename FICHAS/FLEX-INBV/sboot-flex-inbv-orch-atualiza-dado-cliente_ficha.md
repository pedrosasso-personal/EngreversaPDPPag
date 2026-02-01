# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-flex-inbv-orch-atualiza-dado-cliente** é um orquestrador desenvolvido em Java com Spring Boot e Apache Camel, responsável por receber dados de clientes (pessoa física) e encaminhá-los para o sistema CDSP (Central de Dados de Clientes) através de filas RabbitMQ. O sistema atua como intermediário, realizando transformações, validações, mapeamento de domínios (de-para) e enriquecimento de dados antes de publicá-los na fila de destino para processamento assíncrono pelo CDSP/CADU.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal que inicializa a aplicação Spring Boot |
| **AtualizaDadoClienteRouter** | Rota Camel que orquestra o fluxo de atualização de dados do cliente |
| **DadosGeraisProcessor** | Processa e deserializa o payload JSON recebido em objeto DadosGeraisRequest |
| **DominiosDeParaProcessor** | Realiza mapeamento de domínios (de-para), validações e transformações nos dados |
| **TrataErroResponseProcessor** | Processa exceções e monta respostas de erro padronizadas |
| **IntegracaoCaduRepositoryImpl** | Responsável por enviar mensagens para a fila RabbitMQ do CDSP |
| **MapeamentoDominioRepositoryImpl** | Consulta e carrega mapeamentos de domínios da API de mapeamento |
| **JwtClientCredentialInterceptor** | Interceptor que injeta token JWT de autenticação nas requisições |
| **DadosGeraisMapper** | Mapper MapStruct para conversão entre objetos de request e domain |
| **FlexCubeMapeamentoDominios** | Gerencia cache de mapeamentos de domínios carregados |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework base)
- **Apache Camel** (orquestração e roteamento)
- **RabbitMQ** (mensageria)
- **MapStruct** (mapeamento de objetos)
- **Jackson** (serialização/deserialização JSON)
- **Maven** (gerenciamento de dependências)
- **Lombok** (redução de boilerplate)
- **OpenAPI/Swagger** (documentação de APIs)
- **Spring Security OAuth2** (autenticação JWT)
- **Logback** (logging)
- **Docker** (containerização)
- **Google Cloud Platform** (infraestrutura - desabilitado em alguns perfis)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/atualizar/dados | AtualizaDadoClienteRouter (Camel REST DSL) | Recebe dados de cliente para atualização e envia para processamento assíncrono via fila |

---

## 5. Principais Regras de Negócio

1. **Validação e Filtro de Contatos**: Remove contatos cujo código não existe no mapeamento de domínios CDSP
2. **Validação e Filtro de Endereços**: Remove endereços cujo código não existe no mapeamento, e limpa o campo `paisLogradouro`
3. **Mapeamento de Documentos**: Classifica documentos como RG (código "1") ou OUTROS (código "7")
4. **Padronização de Dados Bancários**: Define tipo de conta como "CC" (Conta Corrente) e remove zeros à esquerda do código do banco
5. **Enriquecimento de Relacionamentos**: Concatena códigos de origem e finalidade para determinar o tipo de produto (SOLAR, FGTS, DESENROLA BRASIL)
6. **Normalização de Sexo**: Mapeia códigos de sexo para M (Masculino), F (Feminino) ou I (Não Informado)
7. **Remoção de Campos Sensíveis**: Remove `numeroBeneficiarioINSS` e `paisNascimento` antes do envio
8. **Geração de Correlation ID**: Gera UUID único para rastreamento da transação
9. **Injeção de Metadados**: Adiciona assinatura, usuário, sistema e evento configurados nas propriedades

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **DadosGerais**: Entidade raiz que encapsula todos os dados do cliente
  - **Dados**: Contém informações gerais e listas de dados relacionados
    - **DetalhePessoaFisica**: Detalhes específicos de pessoa física (1:1)
    - **Contato**: Lista de contatos (1:N)
    - **Endereco**: Lista de endereços (1:N)
    - **DadoBanco**: Lista de dados bancários (1:N)
    - **Documento**: Lista de documentos (1:N)
    - **Relacionamento**: Lista de relacionamentos bancários (1:N)

**Relacionamentos:**
- Dados (1) → (0..1) DetalhePessoaFisica
- Dados (1) → (0..N) Contato
- Dados (1) → (0..N) Endereco
- Dados (1) → (0..N) DadoBanco
- Dados (1) → (0..N) Documento
- Dados (1) → (0..N) Relacionamento

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | leitura | Configuração Spring Boot | Arquivo de configuração de logs |
| application.yml | leitura | Configuração Spring Boot | Arquivo de configuração principal da aplicação |
| application-local.yml | leitura | Configuração Spring Boot | Configurações específicas do perfil local |
| sboot-flex-inbv-orch-atualiza-dado-cliente.yaml | leitura | OpenAPI Generator | Especificação OpenAPI para geração de código |
| sboot-intr-base-acl-mapeamento-dominio.yaml | leitura | OpenAPI Generator | Especificação da API de mapeamento de domínios |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Responsável | Descrição |
|--------------|------------|-------------------|-----------|
| QF.CDSP.BASE.ASSINC-CLIENTES | RabbitMQ | IntegracaoCaduRepositoryImpl | Fila para envio de dados de clientes para processamento assíncrono no CDSP/CADU |

**Configurações:**
- **Exchange**: QF.CDSP.BASE.ASSINC-CLIENTES
- **Host**: Configurável por ambiente (rabbit-cdsp-lega)
- **Porta**: 5672
- **Virtual Host**: /

---

## 12. Integrações Externas

| Sistema/API | Tipo | Classe Responsável | Descrição |
|-------------|------|-------------------|-----------|
| API Gateway OAuth | REST | JwtAuthorizationHeaderGenerator | Obtenção de token JWT para autenticação (endpoint: /auth/oauth/v2/token-jwt) |
| sboot-intr-base-acl-mapeamento-dominio | REST | MapeamentoDominioRepositoryImpl | Consulta de mapeamentos de domínios (de-para) entre sistemas |
| RabbitMQ CDSP | Mensageria | IntegracaoCaduRepositoryImpl | Envio de mensagens para fila de atualização de clientes |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com uso de padrões (Repository, Processor, Mapper)
- Uso adequado de frameworks modernos (Spring Boot, Camel, MapStruct)
- Configuração externalizada por perfis de ambiente
- Tratamento centralizado de exceções
- Uso de Lombok para redução de boilerplate
- Documentação OpenAPI/Swagger

**Pontos de Melhoria:**
- Lógica de negócio complexa concentrada em `DominiosDeParaProcessor` (método `process` com múltiplas responsabilidades)
- Métodos públicos em Processor que deveriam ser privados (ex: `processarListaContatos`, `processarListaEnderecos`)
- Falta de testes unitários nos arquivos principais (marcados como NAO_ENVIAR)
- Uso de `Optional.ifPresentOrElse` com lambda vazia poderia ser simplificado
- Comentários em português misturados com código em inglês
- Alguns métodos muito longos que poderiam ser refatorados
- Falta de validações mais robustas de entrada (dependência excessiva de try-catch)
- Uso de `null` explícito em alguns pontos ao invés de Optional

---

## 14. Observações Relevantes

1. **Arquitetura Atlante**: O projeto segue o padrão arquitetural Atlante do Banco Votorantim, com estrutura de orquestrador stateless
2. **Multi-ambiente**: Suporta múltiplos ambientes (des, uat, prd) com configurações específicas via ConfigMaps e Secrets
3. **Segurança**: Implementa autenticação JWT com interceptor customizado
4. **Cache de Domínios**: Mantém cache de mapeamentos de domínios para evitar consultas repetidas
5. **Correlation ID**: Gera e propaga correlation ID para rastreabilidade de transações
6. **Containerização**: Preparado para deploy em Kubernetes/OpenShift com Dockerfile multi-layer
7. **Observabilidade**: Expõe métricas via Actuator (health, metrics, prometheus) na porta 9090
8. **Produtos Suportados**: SOLAR, FGTS e DESENROLA BRASIL
9. **Perfil Local**: Configuração específica para desenvolvimento local com H2 console disponível
10. **Auditoria**: Integração com trilha de auditoria do Banco Votorantim (springboot-arqt-base-trilha-auditoria)