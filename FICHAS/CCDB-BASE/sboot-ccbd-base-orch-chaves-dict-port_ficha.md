# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema orquestrador responsável por gerenciar operações de portabilidade de chaves PIX no contexto do Banco Digital (CCBD). O sistema atua como intermediário entre o Banco Votorantim/BV S.A. e o DICT (Diretório de Identificadores de Contas Transacionais) do Banco Central, permitindo criar, consultar, confirmar, cancelar e concluir processos de portabilidade e reivindicação de chaves PIX. Utiliza Apache Camel para orquestração de fluxos e integra-se com sistemas legados e APIs externas para validação de dados cadastrais e contas.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `PortabilidadeController` | Controller REST que expõe endpoints para operações de portabilidade PIX |
| `ChavesDictPortService` | Serviço de domínio que orquestra as operações via Apache Camel |
| `CamelContextWrapper` | Wrapper do contexto Camel para gerenciamento de rotas |
| `SalvarPortabilidadeRouter` | Rota Camel para criação de portabilidade |
| `CancelarPortabilidadeRouter` | Rota Camel para cancelamento de portabilidade |
| `ConfirmarPortabilidadeRouter` | Rota Camel para confirmação de portabilidade |
| `ConcluirPortabilidadeRouter` | Rota Camel para conclusão de portabilidade |
| `ConsultarPortabilidadeRouter` | Rota Camel para consulta de portabilidade |
| `ListarPortabilidadeRouter` | Rota Camel para listagem de portabilidades |
| `ValidacaoTitularidadeService` | Valida se a conta pertence ao CPF/CNPJ informado |
| `PortabilidadeMapper` | Mapeia objetos de domínio para representações REST |
| `FilterMapper` | Mapeia filtros de busca |
| Repositories (Impl) | Implementações de integração com APIs externas (DICT, Global, etc) |

---

## 3. Tecnologias Utilizadas

- **Spring Boot** (framework principal)
- **Apache Camel 3.22.4** (orquestração de fluxos)
- **Spring Security OAuth2** (autenticação e autorização JWT)
- **RestTemplate** (cliente HTTP)
- **Swagger/OpenAPI 3.0** (documentação de API)
- **Lombok** (redução de boilerplate)
- **JUnit 5 + Mockito** (testes unitários)
- **Rest Assured** (testes funcionais)
- **Pact** (testes de contrato)
- **Logback** (logging)
- **Spring Actuator + Prometheus** (monitoramento)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Java 11**

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/banco-digital/dict/chaves/portabilidade` | `PortabilidadeController` | Cria uma nova portabilidade/reivindicação de chave PIX |
| POST | `/v1/banco-digital/dict/chaves/portabilidade/{codigoPortabilidade}/cancelamento` | `PortabilidadeController` | Cancela uma portabilidade existente |
| POST | `/v1/banco-digital/dict/chaves/portabilidade/{codigoPortabilidade}/confirmacao` | `PortabilidadeController` | Confirma uma portabilidade (lado doador) |
| POST | `/v1/banco-digital/dict/chaves/portabilidade/{codigoPortabilidade}/concluir` | `PortabilidadeController` | Conclui uma portabilidade |
| GET | `/v1/banco-digital/dict/chaves/portabilidade/{codigoPortabilidade}` | `PortabilidadeController` | Consulta uma portabilidade específica |
| GET | `/v1/banco-digital/dict/chaves/portabilidades` | `PortabilidadeController` | Lista todas as portabilidades de uma conta |

---

## 5. Principais Regras de Negócio

1. **Validação de Titularidade**: Antes de criar portabilidade, valida se o CPF/CNPJ do usuário autenticado é titular da conta informada
2. **Geração de Token JWT**: Gera tokens diferentes para BV (161) e BVSA (436) conforme o banco da operação
3. **Recuperação de Dados de Pessoa**: Busca nome do titular em sistema legado para preencher dados do claimer
4. **Normalização de Nome**: Remove acentos e caracteres especiais do nome antes de enviar ao DICT
5. **Determinação de Perfil**: Identifica se a conta é solicitante ou solicitada na portabilidade
6. **Filtro de Status**: Lista apenas portabilidades em processo (OPEN, WAITING_RESOLUTION)
7. **Validação de Documento**: Verifica se o CPF/CNPJ do usuário autenticado corresponde ao da portabilidade consultada
8. **Tratamento de Cancelamento**: Define razão de cancelamento baseado no tipo (FRAUD para OWNERSHIP/DONOR, USER_REQUESTED para demais)
9. **Conversão de Status**: Mapeia status CANCELLED + PORTABILITY para status customizado "MANTIDO_CHAVE_BV"
10. **Identificação de Banco**: Determina banco (BV/BVSA) por código COMPE ou ISPB para rotear corretamente

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **ClaimRequest/ClaimResponse**: Representa uma solicitação/resposta de portabilidade
  - Contém: `Claimer` (requisitante), `ClaimerAccount` (conta destino), chave, tipo, status
  
- **Claimer**: Dados do requisitante da portabilidade
  - Atributos: tipo pessoa, CPF/CNPJ, nome
  
- **ClaimerAccount**: Dados da conta destino
  - Atributos: participante (ISPB), agência, conta, tipo conta, data abertura
  
- **Entry**: Representa uma chave PIX registrada
  - Contém: `Owner` (proprietário), `ClaimerAccount` (conta vinculada), tipo chave, data criação
  
- **Owner**: Proprietário de uma chave
  - Atributos: tipo pessoa, CPF/CNPJ, nome, nome fantasia
  
- **InfoPortabilidade**: DTO para operações de consulta/cancelamento
  - Atributos: CPF/CNPJ, código portabilidade
  
- **FilterList**: Filtro para busca de chaves por conta
  - Atributos: banco, agência, conta, CPF/CNPJ

**Relacionamentos:**
- ClaimRequest/Response → Claimer (1:1)
- ClaimRequest/Response → ClaimerAccount (1:1)
- Entry → Owner (1:1)
- Entry → ClaimerAccount (1:1)

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
| `logback-spring.xml` | leitura | Configuração Spring Boot | Arquivo de configuração de logs da aplicação |
| `application.yml` | leitura | Configuração Spring Boot | Arquivo de propriedades da aplicação (URLs, credenciais, etc) |
| `sboot-ccbd-base-orch-chaves-dict-port.yaml` | leitura | Swagger Codegen | Especificação OpenAPI para geração de interfaces REST |
| `sboot-glob-base-atom-cliente-dados-cadastrais.yaml` | leitura | Swagger Codegen | Especificação OpenAPI do cliente de dados cadastrais |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema/API | Tipo | Descrição |
|-------------|------|-----------|
| **DICT/SPAG (sboot-spag-pixx-orch-chaves-dict)** | REST API | Sistema do Banco Central para gerenciamento de chaves PIX - operações de criar, consultar, confirmar, cancelar, concluir portabilidades e listar chaves |
| **API Gateway OAuth** | REST API | Serviço de autenticação para geração de tokens JWT (dois endpoints: BV e BVSA) |
| **Global - Dados Cadastrais (sboot-glob-base-atom-cliente-dados-cadastrais)** | REST API | Consulta contas correntes por CPF/CNPJ para validação de titularidade e obtenção de código do banco |
| **Consulta Pessoa Legado (springboot-glob-base-consulta-pessoa)** | REST API | Sistema legado para recuperar dados de pessoa por número de conta (autenticação básica) |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura modular (application, domain, common)
- Uso adequado de padrões como Repository, Service, Mapper
- Utilização de Apache Camel para orquestração complexa de fluxos
- Cobertura de testes unitários presente
- Uso de DTOs para transferência de dados
- Configuração externalizada via application.yml
- Documentação OpenAPI/Swagger

**Pontos de Melhoria:**
- Uso excessivo de processadores Camel que apenas armazenam propriedades (Store*Processor), poderia ser simplificado
- Lógica de negócio misturada em Mappers (ex: PortabilidadeMapper com regras de status)
- Tratamento de exceções genérico em alguns pontos (catch Exception)
- Classe `ErrorFormat` com métodos estáticos complexos, dificulta testes
- Falta de validações de entrada em alguns endpoints
- Código de mock nos testes muito verboso e complexo
- Algumas classes de domínio com setters públicos desnecessários
- Hardcoded de valores em alguns enums (ex: ParticipanteEnum com 360 participantes)
- Falta de documentação JavaDoc nas classes principais

---

## 14. Observações Relevantes

1. **Multi-banco**: Sistema suporta operações para dois bancos distintos (BV - 161 e BVSA - 436) com tokens e endpoints diferentes
2. **Segurança**: Utiliza OAuth2 com JWT, propagando token de autenticação nas chamadas internas
3. **Auditoria**: Integrado com framework de trilha de auditoria do BV
4. **Ambientes**: Configuração para múltiplos ambientes (local, des, qa, uat, prd)
5. **Normalização**: Tratamento especial para nomes com acentuação antes de enviar ao DICT
6. **Timeout**: Configuração de timeout de 10 segundos para conexões HTTP
7. **Pool de Conexões**: Máximo de 50 conexões totais e 5 por rota
8. **Status Customizado**: Implementa status "MANTIDO_CHAVE_BV" para portabilidades canceladas
9. **Validação de CPF**: Sistema valida se o CPF do token JWT corresponde ao titular da conta
10. **Iteração de Listas**: Usa iterator customizado para processar múltiplas requisições de portabilidade em paralelo