---
## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema **sboot-ccbd-base-orch-controle-notificacoes** é um microsserviço orquestrador responsável pelo controle e envio de notificações push preditivas para clientes que possuem agendamentos de pagamento de boletos de consumo e tributo para o próximo dia útil. O sistema consulta agendamentos, agrupa por cliente, calcula o valor total agendado e envia notificações personalizadas via push, além de atualizar o status dos agendamentos notificados.

---

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal que inicializa a aplicação Spring Boot |
| `ControleNotificacoesController` | Controlador REST que expõe o endpoint para consulta e envio de notificações |
| `ControleNotificacoesService` | Serviço de domínio que orquestra o fluxo de consulta e notificação via Apache Camel |
| `ControleNotificacoesRepositoryImpl` | Implementação do repositório que integra com APIs externas (agendamento e envio de push) |
| `ControleNotificacoesRouter` | Define as rotas do Apache Camel para orquestração |
| `CamelContextWrapper` | Wrapper para configuração e inicialização do contexto Camel |
| `ControleNotificacoesMapper` | Mapper para conversão entre representações de API e domínio |
| `DataUtils` | Utilitário para cálculo de próximo dia útil |
| `NotificacaoMensagemEnum` | Enum com templates de mensagens de notificação |
| `TpBaseAgendamentoEnum` | Enum para tipos de base de agendamento (Sybase/SQL35) |

---

### 3. Tecnologias Utilizadas
- **Spring Boot 2.x** (framework principal)
- **Apache Camel 3.0.1** (orquestração e integração)
- **Spring Security OAuth2** (segurança e autenticação)
- **Swagger/OpenAPI 3.0** (documentação de APIs)
- **MapStruct 1.3.1** (mapeamento de objetos)
- **Lombok** (redução de boilerplate)
- **Micrometer + Prometheus** (métricas e monitoramento)
- **Grafana** (visualização de métricas)
- **HikariCP** (pool de conexões)
- **Logback** (logging)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **JUnit 5** (testes unitários)
- **Rest Assured** (testes de API)
- **Pact** (testes de contrato)

---

### 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/notificacoes/consumo-tributo` | `ControleNotificacoesController` | Busca agendamentos de consumo/tributo para D+1, agrupa por cliente e envia notificações push |

---

### 5. Principais Regras de Negócio
1. **Consulta de Agendamentos**: Busca todos os agendamentos de consumo e tributo para o próximo dia útil (D+1)
2. **Agrupamento por Cliente**: Agrupa agendamentos por CPF/CNPJ do remetente e soma os valores totais agendados
3. **Cálculo de Dia Útil**: Se o dia seguinte for sábado, considera segunda-feira como próximo dia útil
4. **Formatação de Mensagem**: Formata o valor total em moeda brasileira (R$) na mensagem do push
5. **Envio de Push Personalizado**: Envia notificação push com título, mensagem e valor total agendado
6. **Atualização de Status**: Após envio bem-sucedido, atualiza a data da última notificação do agendamento
7. **Tratamento de Falhas**: Remove da lista de atualização os agendamentos cujo push falhou no envio
8. **Exclusão de Actuator**: Endpoints do actuator são excluídos das métricas HTTP

---

### 6. Relação entre Entidades

**Entidades Principais:**
- `ControleNotificacoes`: Entidade de resposta do processo (code, message)
- `AgendamentoDomainResponse`: Representa um agendamento completo com remetente, favorecido e detalhes
- `PessoaAgendamento`: Dados de pessoa (remetente/favorecido) com CPF/CNPJ, conta, agência
- `AgendamentoPushInfo`: Informações agregadas para envio de push (CPF/CNPJ, valor total, data)
- `UpdateAgendamentoDomain`: Dados para atualização de agendamento após notificação

**Relacionamentos:**
- Um `AgendamentoDomainResponse` possui um `PessoaAgendamento` como remetente e outro como favorecido
- Múltiplos `AgendamentoDomainResponse` são agrupados em um `AgendamentoPushInfo` por CPF/CNPJ
- Cada `AgendamentoDomainResponse` gera um `UpdateAgendamentoDomain` para atualização

---

### 7. Estruturas de Banco de Dados Lidas

não se aplica

---

### 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

### 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `application.yml` | leitura | Spring Boot | Configurações da aplicação (URLs, profiles, portas) |
| `logback-spring.xml` | leitura | Logback | Configuração de logs (formato JSON, níveis) |
| `swagger/*.yaml` | leitura | Swagger Codegen | Especificações OpenAPI para geração de código |

---

### 10. Filas Lidas

não se aplica

---

### 11. Filas Geradas

não se aplica

---

### 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| **sboot-ccbd-base-orch-agendamento** | API REST | Consulta agendamentos de consumo/tributo e atualiza status após notificação |
| **sboot-gnms-base-orch-envio-push** | API REST | Envia notificações push personalizadas para clientes |

**Endpoints Consumidos:**
- `GET /v1/agendamentos/consumo-tributo` - Consulta agendamentos por período
- `PUT /v1/agendamento/atualizar` - Atualiza data de última notificação
- `POST /v1/envio-push/enviarNotificacaoPersonalizada` - Envia push notification

---

### 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**
- **Pontos Positivos:**
  - Boa separação de responsabilidades (domain, application, infrastructure)
  - Uso adequado de padrões como Repository, Service e Mapper
  - Configuração clara de propriedades e profiles
  - Uso de Lombok para redução de boilerplate
  - Implementação de métricas e monitoramento
  - Documentação via Swagger/OpenAPI
  - Testes estruturados (unit, integration, functional)

- **Pontos de Melhoria:**
  - Tratamento de exceções genérico (apenas log de erro sem detalhamento)
  - Lógica de negócio complexa concentrada no `RepositoryImpl` (deveria estar no Service)
  - Falta de validações de entrada mais robustas
  - Ausência de circuit breaker para chamadas externas
  - Código com alguns acoplamentos diretos a bibliotecas específicas
  - Falta de testes para cenários de falha nas integrações
  - Configuração de segurança básica (OAuth2 habilitado mas sem detalhes de implementação)

---

### 14. Observações Relevantes

1. **Arquitetura Hexagonal**: O projeto segue parcialmente a arquitetura hexagonal com separação entre domain, application e infrastructure
2. **Apache Camel**: Utiliza Camel para orquestração, mas de forma simplificada (apenas uma rota direta)
3. **Profiles**: Suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas
4. **Monitoramento**: Integração completa com Prometheus e Grafana para observabilidade
5. **Containerização**: Dockerfile otimizado com OpenJ9 e configurações de memória
6. **CI/CD**: Configuração para Jenkins com propriedades específicas (jenkins.properties)
7. **Segurança**: Aplicação protegida com OAuth2, mas endpoints do Swagger são públicos
8. **Versionamento de API**: Utiliza versionamento via path (`/v1/`)
9. **Geração de Código**: Usa Swagger Codegen para gerar clientes REST automaticamente
10. **Testes de Arquitetura**: Profile específico para validação de regras arquiteturais com ArchUnit

---