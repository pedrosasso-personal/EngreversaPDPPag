# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-ccbd-base-acl-conta-corrente** é um componente ACL (Anti-Corruption Layer) desenvolvido em Java com Spring Boot, destinado ao descomissionamento do sistema legado NCCS (Novo Core de Conta Corrente). Sua função principal é disponibilizar funcionalidades de consulta de titularidade de contas, tipos de transações, agências e outras configurações relacionadas a contas correntes, atuando como uma camada de transição entre sistemas legados e novos.

O sistema segue a arquitetura hexagonal (Ports & Adapters), promovendo separação clara entre lógica de negócio e infraestrutura, facilitando manutenibilidade e evolução.

---

## 2. Principais Classes e Responsabilidades

| Classe/Componente | Responsabilidade |
|-------------------|------------------|
| `Application.java` | Classe principal que inicializa a aplicação Spring Boot |
| `AccountHoldersApiDelegateImpl` | Controller REST para consulta de titularidade de contas |
| `AccountBranchApiDelegateImpl` | Controller REST para consulta de detalhes de agências |
| `TransactionApiDelegateImpl` | Controller REST para consulta de tipos de transações |
| `GetAccountHolders` | Caso de uso principal que orquestra consultas de titularidade |
| `GetAccountHoldersByAccount` | Caso de uso para buscar titulares por conta específica |
| `GetAccountHoldersByModality` | Caso de uso para buscar titulares por modalidade de conta |
| `GetAccountHoldersByTaxIdNumber` | Caso de uso para buscar titulares por CPF/CNPJ |
| `SearchBranchDetail` | Caso de uso para buscar detalhes de agências |
| `SearchTransactionType` | Caso de uso para buscar tipos de transações |
| `GlobalExceptionHandler` | Tratamento centralizado de exceções |
| `OAuth2ClientConfig` | Configuração de segurança OAuth2 |
| Diversos Mappers | Conversão entre DTOs, representações e modelos de domínio |

---

## 3. Tecnologias Utilizadas

- **Java 21** (com Virtual Threads habilitadas)
- **Spring Boot 3.4.4**
- **Spring Security 6.4.1** (OAuth2 Client e Resource Server)
- **Spring Web** (com Undertow como servidor de aplicação)
- **MapStruct** (para mapeamento de objetos)
- **OpenAPI Generator** (geração de clientes REST a partir de especificações Swagger/OpenAPI)
- **Logback** (com formato JSON para logs)
- **Maven 3.8+** (gerenciamento de dependências)
- **Docker** (containerização)
- **Google Cloud Platform** (infraestrutura)
- **Atlante Framework** (framework corporativo do Banco Votorantim)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/digital-bank/{bank}/account-holders` | `AccountHoldersApiDelegateImpl` | Consulta contas e titulares por diversos filtros (número de conta, CPF/CNPJ, modalidade) |
| GET | `/v1/digital-bank/{bank}/branchs/{branchNumber}` | `AccountBranchApiDelegateImpl` | Consulta detalhes de uma agência específica |
| GET | `/v1/digital-bank/{bank}/transaction-types/{id}` | `TransactionApiDelegateImpl` | Consulta tipo de transação por ID |
| GET | `/v1/digital-bank/{bank}/transaction-types` | `TransactionApiDelegateImpl` | Consulta tipos de transações com filtros opcionais |

---

## 5. Principais Regras de Negócio

1. **Validação de Parâmetros de Entrada**: O sistema valida obrigatoriamente o `bankId` (deve ser maior que zero) e outros parâmetros conforme o tipo de consulta.

2. **Filtros Mutuamente Exclusivos**: Na consulta de titularidade, apenas um filtro pode ser utilizado por vez:
   - Por identificação completa da conta (número, tipo, agência)
   - Por CPF/CNPJ do titular
   - Por modalidade de conta

3. **Paginação**: Consultas por modalidade suportam paginação com `pageSize` e `cursorRef`.

4. **Enriquecimento de Dados**: O sistema busca informações complementares de múltiplas fontes (dados cadastrais, contas, agências) e as consolida.

5. **Processamento Assíncrono**: Utiliza Virtual Threads e ExecutorService para buscar contas de forma paralela quando consultando por CPF/CNPJ.

6. **Mapeamento de Tipos de Titularidade**: Define tipos de titularidade conforme padrão ISO20022 (SIGL - Single Owner, JOIT - Joint Account, CORP - Corporation).

7. **Conversão de Formatos**: Converte datas entre formatos (LocalDate, LocalDateTime, OffsetDateTime) e booleanos entre representações (S/N para true/false).

---

## 6. Relação entre Entidades

**Principais Entidades e Relacionamentos:**

- **Account** (Conta): Entidade central contendo:
  - `AccountId` (identificação: banco, número, tipo, agência)
  - `BasicRecordInformation` para modalidade, status, motivos de bloqueio
  - `AccountClosureRequest` (solicitação de encerramento)
  - Flags booleanas (isNopAccount, isTaxCpmfFree, etc.)

- **AccountHolder** (Titular de Conta):
  - Relacionamento 1:N com `Holder` (titulares)
  - Relacionamento 1:1 com `Account`

- **Holder** (Titular):
  - Relacionamento 1:1 com `Person`
  - Tipo de titularidade (HolderType)

- **Person** (Pessoa):
  - Dados básicos: id, nome, CPF/CNPJ

- **ResponseBranchDetail** (Detalhes da Agência):
  - Informações da agência e datas contábeis

- **ResponseTransactionType** (Tipo de Transação):
  - Informações sobre tipos de transações e categorias

**Relacionamento UML Textual:**
```
AccountHolder "1" --> "1" Account
AccountHolder "1" --> "*" Holder
Holder "1" --> "1" Person
Account "1" --> "1" AccountId
Account "1" --> "0..1" AccountClosureRequest
Account "1" --> "*" BasicRecordInformation
```

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBGlobal.TbBanco | tabela | SELECT | Informações de bancos |
| DBGlobal.TbAgencia | tabela | SELECT | Informações de agências |
| DBGlobal.TbTipoConta | tabela | SELECT | Tipos de conta (CC, CT, IF) |
| DBContaCorrente.TbModalidade | tabela | SELECT | Modalidades de conta corrente |
| DBContaCorrente.TbMotivoEncerramentoConta | tabela | SELECT | Motivos de encerramento de conta |
| Dados de Pessoa (via API) | API | READ | Informações cadastrais de pessoas |
| Dados de Conta Corrente (via API) | API | READ | Informações de contas correntes |

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot | Configurações da aplicação |
| logback-spring.xml | leitura | Logback | Configuração de logs (diferentes por ambiente) |
| openapi.yaml | leitura | OpenAPI Generator | Especificação da API REST |
| sboot-ccbd-base-atom-conta-corrente-dominio.yaml | leitura | OpenAPI Generator | Especificação do cliente de conta corrente domínio |
| sboot-glob-base-atom-cliente-dados-cadastrais.yaml | leitura | OpenAPI Generator | Especificação do cliente de dados cadastrais |
| sboot-glob-base-atom-lista-bancos.yaml | leitura | OpenAPI Generator | Especificação do cliente de lista de bancos |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| sboot-ccbd-base-atom-conta-corrente-dominio | API REST | Consulta informações de contas correntes, tipos de transações e controle de datas |
| sboot-glob-base-atom-cliente-dados-cadastrais | API REST | Consulta dados cadastrais de pessoas, contas por pessoa, contas por CPF/CNPJ |
| sboot-glob-base-atom-lista-bancos | API REST | Consulta informações de agências bancárias |
| OAuth2 Token Provider | API REST | Autenticação e autorização via OAuth2 Client Credentials |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 8/10

**Justificativa:**

**Pontos Positivos:**
- Arquitetura hexagonal bem estruturada com clara separação de responsabilidades
- Uso adequado de padrões como Ports & Adapters, Mappers e DTOs
- Código limpo com nomenclatura descritiva em inglês
- Boa cobertura de validações e tratamento de exceções centralizado
- Uso de tecnologias modernas (Java 21, Virtual Threads, Spring Boot 3.x)
- Documentação presente (README, comentários em código)
- Configuração adequada de segurança OAuth2

**Pontos de Melhoria:**
- Alguns mappers poderiam ter lógica mais simplificada
- Falta de testes unitários nos arquivos fornecidos (embora existam na estrutura)
- Algumas classes de domínio poderiam ter validações mais robustas
- Documentação inline poderia ser mais detalhada em alguns métodos complexos
- Configurações hardcoded em alguns pontos (poderiam ser externalizadas)

---

## 14. Observações Relevantes

1. **Componente de Transição**: Este é um componente temporário destinado ao descomissionamento do sistema legado NCCS, portanto sua arquitetura prioriza integração e adaptação.

2. **Segurança**: O sistema utiliza OAuth2 com JWT para autenticação e autorização, integrando-se ao API Gateway corporativo.

3. **Ambientes**: Possui configurações específicas para ambientes DES, UAT e PRD, com diferentes endpoints e configurações de log.

4. **Monitoramento**: Expõe endpoints Actuator na porta 9090 para health checks e métricas.

5. **Performance**: Utiliza Virtual Threads do Java 21 para melhor performance em operações I/O intensivas e processamento paralelo de consultas.

6. **Containerização**: Preparado para execução em containers Docker com imagem base corporativa.

7. **Infraestrutura**: Configurado para execução na Google Cloud Platform (GCP) com Kubernetes.

8. **Logs**: Configuração de logs em formato JSON para facilitar integração com ferramentas de observabilidade.

9. **Geração de Código**: Utiliza OpenAPI Generator para gerar clientes REST automaticamente a partir de especificações Swagger, reduzindo código boilerplate.

10. **Framework Corporativo**: Integra-se ao framework Atlante do Banco Votorantim, seguindo padrões e práticas corporativas.