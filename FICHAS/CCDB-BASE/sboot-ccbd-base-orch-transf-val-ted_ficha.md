# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-ccbd-base-orch-transf-val-ted** é um orquestrador de validação de transferências bancárias DOC e TED para o Banco Digital do Banco Votorantim. Trata-se de um microserviço stateless desenvolvido em Spring Boot que expõe APIs REST para validar transferências bancárias, verificando regras de negócio como dias úteis, horários permitidos, agendamentos e integrando-se com sistemas legados via EJB para efetuar as validações e críticas necessárias.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `ValidaTransfDocTedController` | Controlador REST que expõe o endpoint de validação de DOC/TED |
| `ValidaTransfDocTedService` | Serviço de orquestração que coordena o fluxo de validação via Apache Camel |
| `ValidaTransfDocTedRouter` | Roteador Apache Camel que define o fluxo de validação com decisões baseadas em regras |
| `ValidaTransfDocTedRepositoryImpl` | Implementação de repositório que integra com EJB legado para validação de transferências |
| `ValidaAgendamentoTEDRepositoryImpl` | Implementação de repositório que integra com EJB legado para validação de agendamentos |
| `IsDiaUtilRepositoryImpl` | Implementação de repositório que verifica se uma data é dia útil |
| `ObterProximoDiaUtilRepositoryImpl` | Implementação de repositório que obtém o próximo dia útil |
| `ValidaTransfDocTedConversor` | Conversor entre representações de request/response e DTOs internos |
| `FormatarDados` | Classe utilitária para formatação de datas e validações |
| `TipoContaEnum` | Enumeração de tipos de conta bancária |
| `PracaEnum` | Enumeração de praças bancárias |

---

## 3. Tecnologias Utilizadas

- **Java 11** (OpenJDK com OpenJ9)
- **Spring Boot** (framework principal)
- **Spring Security OAuth2** (autenticação JWT)
- **Apache Camel 3.0.1** (orquestração de fluxos)
- **Swagger/OpenAPI 2.9.2** (documentação de API)
- **RestTemplate** (cliente HTTP para integração)
- **Logback** (logging com formato JSON)
- **Micrometer/Prometheus** (métricas e observabilidade)
- **JUnit 5** e **Mockito** (testes unitários)
- **Rest Assured** (testes funcionais)
- **Pact** (testes de contrato)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **OpenShift/Kubernetes** (orquestração de containers)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/transferencia-bancaria/validar-doc-ted` | `ValidaTransfDocTedController` | Valida uma transferência DOC/TED verificando regras de negócio, dias úteis e horários |

---

## 5. Principais Regras de Negócio

1. **Validação de Data de Transferência**: Não permite agendamento com data anterior à data atual
2. **Verificação de Dia Útil**: Valida se a data de transferência é dia útil (praça Brasil - "NC")
3. **Validação de Horário**: Verifica se a transferência está dentro do horário permitido (00:00 às 17:00), com exceções para datas especiais (24/12 e 31/12 com horário até 10:30)
4. **Obtenção de Próximo Dia Útil**: Quando a data não é dia útil ou está fora do horário, obtém o próximo dia útil
5. **Validação de Agendamento**: Transferências com data futura são tratadas como agendamento
6. **Validação de Transferência Imediata**: Transferências para o mesmo dia dentro do horário são processadas imediatamente
7. **Integração com Sistema Legado**: Todas as validações são confirmadas via chamadas EJB ao sistema legado
8. **Validação de Formato de Data**: Aceita apenas datas no formato "yyyy-MM-dd"
9. **Conversão de Tipos de Conta**: Converte códigos numéricos de tipo de conta para nomenclaturas do sistema legado
10. **Titularidade**: Define titularidade como "OUTRA_TITULARIDADE" (regra a ser refinada conforme comentário TODO no código)

---

## 6. Relação entre Entidades

**Principais DTOs e suas relações:**

- **ValidaTransfDocTedDTO**: DTO principal de entrada contendo:
  - `ContaCorrenteDTO` (remetente e favorecido)
  - Lista de `FavorecidoDTO`
  - Dados da transferência (valor, tipo, finalidade, etc.)
  - Flags de controle (isDiaUtil, isForaHorario, isAgendamento)

- **ValidacaoTransfDocTedDTO**: DTO de saída contendo:
  - `ContaCorrenteDTO` (remetente e favorecido)
  - Lista de `FavorecidoDTO`
  - Dados validados da transferência
  - Data de efetivação calculada

- **ContaCorrenteDTO**: Representa uma conta bancária com código do banco, número da conta e tipo de conta

- **FavorecidoDTO**: Representa o favorecido com nome e CPF/CNPJ

- **CalendarioDTO**: DTO para consultas de calendário bancário (dias úteis)

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
| `application.yml` | leitura | Spring Boot | Arquivo de configuração da aplicação com profiles (local, des, qa, uat, prd) |
| `logback-spring.xml` | leitura | Logback | Configuração de logging em formato JSON para console |
| `sboot-ccbd-base-orch-transf-val-ted.yaml` | leitura | Swagger Codegen | Especificação OpenAPI para geração de interfaces REST |

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
| **EJB Legado - TransferenciaServices** | REST/JSON-RPC | Integração com sistema legado para validação de transferências DOC/TED via endpoint `/esb-adapter/v1/legacy/request` |
| **EJB Legado - Agendamento** | REST/JSON-RPC | Integração com sistema legado para validação de agendamentos TED |
| **EJB Legado - SCalendarioEJB** | REST/JSON-RPC | Integração com sistema legado para consultas de calendário bancário (verificação de dias úteis e obtenção de próximo dia útil) |
| **OAuth2/JWT Provider** | HTTPS | Validação de tokens JWT para autenticação e autorização via `jwks.json` |

**Detalhes das integrações:**
- Utiliza `RestTemplate` com autenticação básica
- Formato de requisição: JSON-RPC com estrutura `{serviceName, methodName, args[]}`
- Ambientes configurados via variáveis de ambiente (des, qa, uat, prd)

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (presentation, domain, repository)
- Uso adequado de padrões como DTO, Builder e Repository
- Cobertura de testes unitários presente em todas as camadas
- Uso de Apache Camel para orquestração de fluxos complexos
- Documentação via Swagger/OpenAPI
- Configuração adequada de profiles para diferentes ambientes
- Uso de Lombok para redução de boilerplate

**Pontos de Melhoria:**
- Presença de TODOs no código indicando regras de negócio incompletas (ex: validação de titularidade)
- Lógica de negócio complexa no conversor (`ValidaTransfDocTedConversor`) que poderia estar em serviços dedicados
- Validações de datas especiais (Natal e Ano Novo) hardcoded, deveriam estar em configuração
- Tratamento de exceções genérico no controller, poderia ser mais específico
- Alguns métodos privados de montagem de request/response muito extensos
- Falta de documentação JavaDoc em classes e métodos principais
- Uso de `System.getenv()` em testes funcionais sem fallback adequado
- Algumas classes de domínio sem validações de negócio (ex: campos obrigatórios)

---

## 14. Observações Relevantes

1. **Arquitetura Multi-módulo**: O projeto está organizado em módulos Maven (application, domain, common) seguindo boas práticas de separação de concerns

2. **Integração com Sistema Legado**: A aplicação atua como uma camada de orquestração e adaptação entre APIs REST modernas e sistemas legados baseados em EJB

3. **Fluxo de Decisão Complexo**: O Apache Camel Router implementa um fluxo de decisão sofisticado baseado em múltiplas condições (dia útil, horário, agendamento)

4. **Segurança**: Implementa autenticação OAuth2 com JWT, mas as credenciais para integração com legado são gerenciadas via variáveis de ambiente e secrets do Kubernetes

5. **Observabilidade**: Configurado com Prometheus, Grafana e logging estruturado em JSON para facilitar monitoramento e troubleshooting

6. **CI/CD**: Possui configuração para Jenkins (`jenkins.properties`) e infraestrutura como código (`infra.yml`) para deploy em OpenShift

7. **Testes**: Boa estrutura de testes separados por tipo (unit, integration, functional) com uso de Pact para testes de contrato

8. **Containerização**: Dockerfile otimizado usando OpenJ9 JVM para redução de consumo de memória

9. **Limitações Conhecidas**: Comentários no código indicam que algumas regras de negócio (como validação de titularidade) precisam ser refinadas

10. **Horários Especiais**: O sistema possui lógica específica para datas de final de ano (24/12 e 31/12) com horários diferenciados, mas essa lógica está hardcoded e poderia ser parametrizável