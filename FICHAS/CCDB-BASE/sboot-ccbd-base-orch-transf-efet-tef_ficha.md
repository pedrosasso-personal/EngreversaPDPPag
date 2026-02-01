# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de orquestração de transferências bancárias TEF (Transferência Eletrônica de Fundos) para o Banco Digital. O sistema é responsável por efetuar e agendar transferências entre contas bancárias, validando limites, consultando dados cadastrais, verificando dias úteis e integrando com sistemas legados e APIs de transferência. Suporta tanto operações síncronas via API REST quanto assíncronas via RabbitMQ (consumindo mensagens de sistemas batch como TSEL).

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `EfetuarTransfTEFControllerV2` | Controller REST que expõe endpoint para efetuar transferências TEF, valida limites, verifica agendamentos e trata erros de negócio |
| `EfetuarTransfTEFListener` | Listener RabbitMQ que consome mensagens de transferências do batch TSEL |
| `EfetuarTransfTEFService` | Serviço de negócio que orquestra as operações de transferência, validação de limites e obtenção de dias úteis |
| `EfetuarTransfTEFRouter` | Rota Camel que orquestra o fluxo de efetivação/agendamento de transferências com base em regras de horário e data |
| `EfetuarTransfTEFRepositoryImpl` | Implementação de repositório que integra com API de transferências (sboot-spag-base-orch-transferencias) |
| `AgendarTransfTEFRepositoryImpl` | Repositório que agenda transferências via chamada ao sistema legado (EJB) |
| `GlobalRepositoryImpl` | Consulta dados cadastrais de pessoas via API (sboot-glob-base-atom-cliente-dados-cadastrais) |
| `GlobalBancoRepositoryImpl` | Consulta lista de bancos via API (sboot-glob-base-atom-lista-bancos) |
| `LimitesRepositoryImpl` | Verifica limites diários de transferência via API (sboot-ccbd-base-orch-limites) |
| `ValidaTefRepositoryImpl` | Valida dados de transferência TEF via API (sboot-ccbd-base-orch-transf-val-tef) |
| `SalvarFavorecidoRepositoryImpl` | Salva favorecido via API (sboot-glob-base-atom-favorecido) |
| `ObterProximoDiaUtilRepositoryImpl` | Obtém próximo dia útil via chamada ao sistema legado (EJB) |
| `EfetTefConversor` | Converte objetos de request/response entre camadas de apresentação e domínio |
| `TransferenciaConversor` | Converte objetos de transferência para formato da API de transferências |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.x** (framework principal)
- **Java 11**
- **Apache Camel 2.24.2** (orquestração de rotas e processamento)
- **Spring Security OAuth2** (autenticação JWT)
- **RabbitMQ** (mensageria assíncrona)
- **RestTemplate** (cliente HTTP)
- **Swagger/OpenAPI 3.0** (documentação de API)
- **Lombok** (redução de boilerplate)
- **Logback** (logging)
- **Micrometer/Prometheus** (métricas)
- **Spring Actuator** (health checks)
- **Maven** (build)
- **Docker** (containerização)
- **Kubernetes/OpenShift** (orquestração de containers)
- **Undertow** (servidor web embarcado)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v2/transferencia-bancaria/transferencia-contas` | `EfetuarTransfTEFControllerV2` | Efetua ou agenda transferência TEF entre contas, validando limites e regras de negócio |

---

## 5. Principais Regras de Negócio

1. **Validação de Horário**: Transferências solicitadas fora do horário permitido (02:00 às 22:30) são automaticamente agendadas para o próximo dia útil
2. **Validação de Data**: Não é permitido agendar transferências com data anterior à data atual
3. **Validação de Limites**: 
   - Verifica limite diário disponível antes de efetuar transferência
   - Se limite for excedido no dia atual, sugere agendamento para próximo dia útil
   - Valida limite também para data de agendamento sugerida
4. **Agendamento Automático**: Transferências com data futura ou fora de horário são agendadas automaticamente
5. **Efetivação Imediata**: Transferências dentro do horário e com data atual são efetivadas imediatamente
6. **Cadastro de Favorecido**: Opcionalmente salva dados do favorecido após transferência bem-sucedida
7. **Validação de Tipo de Pessoa**: Determina automaticamente tipo de pessoa (F/J) com base no tamanho do CPF/CNPJ
8. **Consulta de Bancos**: Enriquece dados de transferência com códigos COMPE dos bancos
9. **Consulta de Dados Cadastrais**: Obtém nome e CPF/CNPJ de remetente e favorecido via integração com sistema Global
10. **Processamento Batch TSEL**: Consome mensagens de transferências do sistema TSEL via RabbitMQ e processa de forma assíncrona

---

## 6. Relação entre Entidades

**Principais Entidades:**

- **TransferenciaDTO**: Entidade central contendo dados completos da transferência (remetente, favorecido, valores, datas)
- **ContaCorrenteDTO**: Representa conta corrente com banco, número, tipo e código COMPE
- **OperacaoTransferenciaTEFDTO**: Resultado da operação de transferência com protocolo, NSU e dados completos
- **LimiteDTO**: Dados para consulta de limite diário
- **LimiteDiarioResponse**: Resposta com limite disponível, total e autorização
- **ValidaTefRequest/Response**: Dados para validação de transferência TEF
- **SalvarFavorecidoDTO**: Dados para cadastro de favorecido
- **CalendarioDTO**: Dados para consulta de dias úteis
- **Pessoa**: Dados cadastrais de pessoa (nome, CPF/CNPJ)
- **Banco**: Dados de banco (código, COMPE, ISPB, nome)
- **Conta**: Identificação de conta (banco, número)

**Relacionamentos:**
- TransferenciaDTO possui ContaCorrenteDTO para remetente e favorecido
- OperacaoTransferenciaTEFDTO é gerado a partir de TransferenciaDTO após efetivação/agendamento
- LimiteDTO é derivado de TransferenciaDTO para validação
- Pessoa é consultada via Conta e enriquece TransferenciaDTO

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
| logback-spring.xml | leitura | /usr/etc/log (runtime) | Arquivo de configuração de logs, carregado em tempo de execução |
| application.yml | leitura | resources (classpath) | Arquivo de configuração da aplicação Spring Boot |
| sboot-ccbd-base-orch-transf-efet-tef-v2.yaml | leitura | resources/swagger | Especificação OpenAPI do serviço (geração de código) |
| sboot-glob-base-atom-cliente-dados-cadastrais.yaml | leitura | resources/swagger/client | Especificação OpenAPI do cliente de dados cadastrais (geração de código) |
| sboot-glob-base-atom-lista-bancos.yaml | leitura | resources/swagger/client | Especificação OpenAPI do cliente de lista de bancos (geração de código) |
| sboot-spag-base-orch-transferencias.yaml | leitura | resources/swagger/client | Especificação OpenAPI do cliente de transferências (geração de código) |

---

## 10. Filas Lidas

| Nome da Fila | Tecnologia | Classe Consumidora | Descrição |
|--------------|------------|-------------------|-----------|
| events.business.CCBD-BASE.tseltransferencia | RabbitMQ | `EfetuarTransfTEFListener` | Fila que recebe mensagens de transferências TEF originadas do sistema batch TSEL para processamento assíncrono |

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema/API | Tipo | Classe Responsável | Descrição |
|-------------|------|-------------------|-----------|
| sboot-spag-base-orch-transferencias | API REST | `EfetuarTransfTEFRepositoryImpl` | API de efetivação de transferências (TED/TEF/DOC) |
| sboot-glob-base-atom-cliente-dados-cadastrais | API REST | `GlobalRepositoryImpl` | API de consulta de dados cadastrais de clientes |
| sboot-glob-base-atom-lista-bancos | API REST | `GlobalBancoRepositoryImpl` | API de consulta de lista de bancos (códigos COMPE, ISPB) |
| sboot-ccbd-base-orch-limites | API REST | `LimitesRepositoryImpl` | API de consulta e validação de limites diários de transferência |
| sboot-ccbd-base-orch-transf-val-tef | API REST | `ValidaTefRepositoryImpl` | API de validação de dados de transferência TEF |
| sboot-glob-base-atom-favorecido | API REST | `SalvarFavorecidoRepositoryImpl` | API de cadastro de favorecidos |
| Sistema Legado (EJB) - TransferenciaServices | EJB/REST | `AgendarTransfTEFRepositoryImpl` | Serviço legado para agendamento de transferências |
| Sistema Legado (EJB) - SCalendarioEJB | EJB/REST | `ObterProximoDiaUtilRepositoryImpl` | Serviço legado para consulta de calendário e dias úteis |
| API Gateway OAuth | OAuth2 | `GatewayOAuthService` | Serviço de autenticação e obtenção de tokens JWT |
| RabbitMQ | Mensageria | `EfetuarTransfTEFListener` | Broker de mensagens para processamento assíncrono |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com módulos domain e application
- Uso adequado de padrões como Repository, Service e Converters
- Implementação de rotas Camel para orquestração de fluxos complexos
- Uso de Lombok para redução de boilerplate
- Configuração externalizada e suporte a múltiplos ambientes
- Tratamento de exceções customizadas
- Documentação via OpenAPI/Swagger
- Uso de builders para objetos complexos

**Pontos de Melhoria:**
- Classe `EfetuarTransfTEFControllerV2` muito extensa (>400 linhas) com lógica de negócio que deveria estar no service
- Métodos privados grandes e repetitivos no controller (`validarLimiteExcederAgendamento`, `validarLimiteUltrapassadoAgendamento`)
- Uso de `RestTemplate` (deprecated) ao invés de `WebClient`
- Falta de testes unitários nos arquivos fornecidos
- Conversores com lógica de negócio (ex: `foraHorarioPermitido()` em `EfetTefConversor`)
- Uso de `ObjectMapper` diretamente em várias classes ao invés de injeção
- Alguns métodos com muitos parâmetros (ex: `FavorecidoConversor.montarRequestFavorecido`)
- Falta de validação de entrada em alguns pontos
- Comentários em português misturados com código em inglês
- Algumas classes de domínio com getters que contêm lógica (ex: `getTipoPessoaRemetente()`)

---

## 14. Observações Relevantes

1. **Arquitetura Multi-Módulo**: O projeto está organizado em dois módulos Maven (domain e application), seguindo boas práticas de separação de camadas
2. **Integração Legado**: O sistema mantém integração com sistemas legados via adaptador EJB/REST, demonstrando estratégia de modernização gradual
3. **Processamento Síncrono e Assíncrono**: Suporta tanto chamadas REST síncronas quanto processamento assíncrono via RabbitMQ
4. **Segurança**: Implementa autenticação OAuth2 com JWT e integração com API Gateway
5. **Observabilidade**: Configurado com Actuator, Prometheus e logs estruturados
6. **Containerização**: Preparado para deploy em Kubernetes/OpenShift com Dockerfile e configurações de infra-as-code
7. **Geração de Código**: Utiliza Swagger Codegen para gerar clientes de APIs externas, garantindo consistência
8. **Configuração por Ambiente**: Suporta múltiplos ambientes (des, qa, uat, prd) com configurações específicas
9. **Auditoria**: Integrado com framework de trilha de auditoria do Banco Votorantim
10. **Resiliência**: Implementa tratamento de erros e validações em múltiplas camadas