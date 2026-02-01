# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-ccbd-base-orch-limites-pix** é um serviço de orquestração RESTful desenvolvido em Spring Boot para gerenciamento de limites transacionais PIX no contexto do Banco Digital Votorantim. O sistema permite consulta, alteração e pré-validação de limites PIX, integrando-se com múltiplos sistemas backend através de APIs REST e mensageria GCP PubSub. Utiliza Apache Camel para orquestração de fluxos complexos de negócio, implementando regras do Banco Central para diferentes categorias de transações PIX (pessoas físicas/jurídicas, contato seguro, saque/troco, agendamento, etc). A aplicação segue arquitetura hexagonal com separação clara de responsabilidades em módulos (common, domain, application) e implementa padrões como Chain of Responsibility para validação de limites por tipo de transação.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application.java** | Classe principal Spring Boot para inicialização da aplicação com OAuth2 Resource Server |
| **LimitesPixController** | Controller REST v1 para operações de consulta e alteração de limites PIX |
| **LimitesPixControllerV2** | Controller REST v2 com endpoints evoluídos de limites PIX |
| **LimitePixService** | Serviço orquestrador que dispara rotas Apache Camel via ProducerTemplate |
| **LimiteServiceImpl** | Implementação de regras de negócio para distinção redução/aumento de limites |
| **ConsultaLimitesPixRouter** | Rota Camel para fluxo de consulta de limites com categorização |
| **LimitesPixRouter** | Rota Camel para fluxo de alteração de limites |
| **PreValidaLimiteRouter** | Rota Camel para pré-validação de transações contra limites disponíveis |
| **LimiteRepositoryImpl** | Repositório de integração com API Gestão Limites e publicação PubSub |
| **GlobalRepositoryImpl** | Repositório de consulta de contas corrente do cliente |
| **ClienteDadosCadastraisRepositoryImpl** | Repositório de validação de titularidade de conta |
| **PreValidacaoLimiteRepositoryImpl** | Repositório de pré-validação de consumo de limites transacionais |
| **ConsultaAlteracaoLimiteRepositoryImpl** | Repositório de consulta de status de solicitações de alteração |
| **LimitesPixMapper** | Mapper de conversão entre DTOs, domain objects e representations |
| **LimiteHandlerFactory** | Factory que cria cadeia de handlers para validação de limites |
| **LimiteAgendamentoHandler** | Handler específico para validação de limites de PIX agendado (regra Bacen R$1.000) |
| **LimiteContatoSeguroHandler** | Handler para validação de limites de contato seguro |
| **LimiteDiferentePFHandler** | Handler para validação de limites entre pessoas físicas de titularidade diferente |
| **LimiteMesmaPFHandler** | Handler para validação de limites entre pessoas físicas de mesma titularidade |
| **LimitePJHandler** | Handler para validação de limites envolvendo pessoas jurídicas |
| **LimitePixCartaoHandler** | Handler para validação de limites PIX com cartão |
| **LimitePixSaqueTrocoHandler** | Handler para validação de limites de saque/troco |
| **CategorizarLimiteProcessor** | Processor Camel que categoriza limites por tipo (Pessoas, Empresas, etc) |
| **AlteraLimiteClienteProcessor** | Processor Camel que prepara request de alteração de limite |
| **ConsultaLimiteProcessor** | Processor Camel que monta request de consulta de limite |
| **OrdenarCategoriaLimiteProcessor** | Processor Camel que ordena categorias por ordem de visualização |
| **ControllerExceptionHandler** | Handler global de exceções REST com tratamento específico por tipo |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.3+** - Framework base da aplicação
- **Spring Security OAuth2** - Autenticação e autorização via JWT
- **Apache Camel 3.22.1** - Orquestração de fluxos e integração
- **GCP PubSub** - Mensageria assíncrona para notificações
- **RestTemplate** - Cliente HTTP para integrações REST
- **OpenAPI 3 / Swagger** - Documentação de APIs
- **Lombok** - Redução de boilerplate code
- **MapStruct** - Mapeamento de objetos
- **JUnit 5** - Framework de testes unitários
- **Mockito** - Framework de mocks para testes
- **Micrometer + Prometheus** - Métricas e monitoramento
- **Spring Actuator** - Health checks e endpoints operacionais
- **HikariCP** - Pool de conexões
- **Jackson** - Serialização/deserialização JSON
- **Maven** - Gerenciamento de dependências e build
- **Kubernetes/OpenShift** - Plataforma de deployment
- **Jenkins** - Pipeline CI/CD
- **Java 11** - Linguagem de programação
- **Apache Tomcat 9.0.106** - Servidor de aplicação embarcado

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/banco-digital/pix/limites/consultar` | LimitesPixController | Consulta limites PIX do cliente com categorização (Global, Pessoas, Empresas, Contato Seguro, Saque/Troco, Agendado, Automático) |
| GET | `/v1/banco-digital/pix/limites/consulta/alteracao` | LimitesPixController | Consulta status de solicitação de alteração de limite por tipo (LIMITE_DIURNO, LIMITE_NOTURNO, LIMITE_TRANSACAO_DIURNO, LIMITE_TRANSACAO_NOTURNO) |
| POST | `/v1/banco-digital/pix/limites/alteracao` | LimitesPixController | Solicita alteração de limite PIX (aumento ou redução) com validação de conta e publicação em fila |
| POST | `/v1/banco-digital/pix/limites/pre-validar` | LimitesPixController | Pré-valida se transação PIX pode ser realizada considerando limites disponíveis e regras Bacen |
| GET | `/v2/banco-digital/pix/limites/consultar` | LimitesPixControllerV2 | Consulta limites PIX versão 2 com melhorias de performance |
| GET | `/v2/banco-digital/pix/limites/consulta/alteracao` | LimitesPixControllerV2 | Consulta status de alteração versão 2 com parâmetro cdParametro |
| POST | `/v2/banco-digital/pix/limites/alteracao` | LimitesPixControllerV2 | Alteração de limite versão 2 com validações aprimoradas |

---

## 5. Principais Regras de Negócio

- **Validação de Titularidade**: Verifica se CPF/CNPJ do token JWT corresponde ao titular da conta informada na requisição
- **Categorização de Limites**: Classifica limites em 7 categorias (Global, Para Pessoas, Empresas, Contato Seguro, Saque/Troco, PIX Agendado, Automático) com ordem de visualização específica
- **Limites Diurno/Noturno**: Controla limites diferenciados para períodos diurno (6h-20h) e noturno (20h-6h)
- **Regra Bacen Agendamento Noturno**: Limita transações PIX agendadas no período noturno a R$ 1.000,00
- **Distinção PF/PJ**: Aplica regras diferentes para pessoas físicas (CPF 11 dígitos) e jurídicas (CNPJ 14 dígitos)
- **Validação Mesma/Diferente Titularidade**: Controla limites específicos para transações entre contas de mesma titularidade ou titularidades diferentes
- **Pré-validação Transacional**: Valida se valor da transação está dentro dos limites disponíveis antes de processar
- **Controle de Solicitações Duplicadas**: Impede solicitação de alteração com mesmo valor já vigente (MesmoValorSolicitacaoAtualException)
- **Status de Processamento**: Gerencia estados de solicitação (FINALIZADO, NEGADO, CANCELADO, EM_PROCESSAMENTO)
- **Redução vs Aumento de Limite**: Diferencia fluxos e mensagens para operações de redução (imediata) e aumento (análise)
- **Validação de Conta Corrente**: Verifica se número de conta, agência e banco correspondem ao cliente
- **Limites por Canal**: Aplica regras específicas para QRCode, cartão, saque/troco, agendamento
- **Contato Seguro**: Permite limites diferenciados para transações com contatos previamente cadastrados
- **Formatação Monetária**: Padroniza valores em BigDecimal com 2 casas decimais
- **Divisão Comercial**: Extrai e valida divisão comercial do cliente para aplicação de regras específicas
- **Período de Consumo**: Calcula e valida período disponível para consumo de limite (diário/noturno)
- **Autorização de Agendamento**: Verifica se cliente possui autorização para realizar PIX agendado
- **Limite Disponível**: Calcula saldo disponível considerando limite configurado menos valor já transacionado
- **Mensagens de Erro Específicas**: Retorna 46 tipos de erros mapeados da API Gestão Limites (ErroRetornoGestaoLimiteEnum)
- **Notificação Assíncrona**: Publica evento em fila GCP PubSub após solicitação de alteração de limite

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **ContaCorrente**: Representa conta bancária do cliente (banco, agência, número, CPF/CNPJ, divisão comercial, tipo conta)
- **LimitePixDTO**: Entidade central contendo limites diário, noturno, transação diurno/noturno, status, datas e solicitações
- **AlterarLimiteCliente**: Request de alteração contendo cdParametroLimite, período, valor
- **PreValidacaoLimiteRequest**: Request de pré-validação com dados da transação (valor, meio pagamento, característica, data movimentação)
- **CategoriaLimiteEnum**: Categorias de limites (PARA_PESSOAS, EMPRESAS, CONTATO_SEGURO, PIX_AGENDADO, SAQUE_TROCO, GLOBAL, AUTOMATICO)

**Relacionamentos:**

- **Cliente (1) --- (N) ContaCorrente**: Um cliente pode ter múltiplas contas corrente
- **ContaCorrente (1) --- (1) LimitePixDTO**: Cada conta possui um conjunto de limites PIX
- **LimitePixDTO (1) --- (N) CategoriaLimite**: Limites são categorizados em múltiplas categorias
- **AlterarLimiteCliente (N) --- (1) ContaCorrente**: Múltiplas solicitações de alteração podem ser feitas para uma conta
- **PreValidacaoLimiteRequest (N) --- (1) ContaCorrente**: Múltiplas pré-validações podem ser realizadas para uma conta
- **CaracteristicaMeioPagamento (N) --- (1) PreValidacaoLimiteRequest**: Cada pré-validação possui uma característica específica (PIX_SAQUE_TROCO, MESMA_TITULARIDADE_PFPF, etc)

**Hierarquia de Handlers (Chain of Responsibility):**

```
LimiteHandlerFactory
    └── LimiteAgendamentoHandler
        └── LimiteContatoSeguroHandler
            └── LimiteDiferentePFHandler
                └── LimiteMesmaPFHandler
                    └── LimitePJHandler
                        └── LimitePixCartaoHandler
                            └── LimitePixSaqueTrocoHandler
                                └── LimiteGeralHandler
                                    └── LimiteNaoValidadoPorHandlers
```

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| Não se aplica | - | - | O sistema não acessa diretamente banco de dados. Todas as consultas são realizadas via APIs REST de outros microserviços (Atom Cliente Dados Cadastrais, Gestão Limites, Limites Transacionais) |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| Não se aplica | - | - | O sistema não atualiza diretamente banco de dados. Todas as alterações são realizadas via APIs REST de outros microserviços (Gestão Limites) |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | Spring Boot Configuration | Arquivo de configuração com URLs de APIs, tópicos PubSub, configurações OAuth2 e parâmetros de ambiente (dev/uat/prd) |
| infra.yml | Leitura | Kubernetes/OpenShift | Arquivo de infraestrutura como código com configmaps, probes, resources e service accounts |
| prometheus.yml | Leitura | Prometheus | Configuração de scraping de métricas do endpoint /actuator/prometheus |
| jenkins.properties | Leitura | Jenkins Pipeline | Propriedades de configuração do pipeline CI/CD |
| pom.xml | Leitura | Maven Build | Arquivo de configuração de dependências e build multi-módulo |

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas. Atua apenas como produtor de eventos.

---

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Responsável | Descrição |
|--------------|------------|-------------------|-----------|
| `projects/bv-ccbd-uat/topics/business-ccbd-base-limite-pix-solicitado` | GCP PubSub | LimiteRepositoryImpl | Publica evento EnvioNotificacaoLimiteSolicitado após solicitação de alteração de limite PIX, contendo dados da conta, CPF/CNPJ, tipo de alteração e valores |

**Observação**: O tópico varia por ambiente:
- Desenvolvimento: `projects/bv-ccbd-des/topics/business-ccbd-base-limite-pix-solicitado`
- UAT: `projects/bv-ccbd-uat/topics/business-ccbd-base-limite-pix-solicitado`
- Produção: `projects/bv-ccbd-prd/topics/business-ccbd-base-limite-pix-solicitado`

---

## 12. Integrações Externas

| Sistema Externo | Tipo | Classe Responsável | Descrição |
|-----------------|------|-------------------|-----------|
| **sboot-sglt-base-orch-gestao-limites** | REST API | LimiteRepositoryImpl | API de CRUD de limites do cliente. Endpoints: consultarLimiteCliente, alterarLimiteCliente, personalizarLimitesSimultaneos, consultarStatusSocilitacaoLimiteV2 |
| **sboot-glob-base-atom-cliente-dados-cadastrais** | REST API | ClienteDadosCadastraisRepositoryImpl, GlobalRepositoryImpl | API de consulta de dados cadastrais do cliente. Retorna lista de contas corrente, divisão comercial e tipo de conta |
| **sboot-sglt-base-orch-limites-transacionais** | REST API | PreValidacaoLimiteRepositoryImpl | API de pré-validação de consumo de limites transacionais. Valida se transação pode ser autorizada considerando limites disponíveis |
| **GCP PubSub** | Mensageria | LimiteRepositoryImpl | Plataforma de mensageria do Google Cloud para publicação assíncrona de eventos de solicitação de limite |
| **OAuth2 JWT Provider** | Autenticação | Spring Security | Provedor de tokens JWT para autenticação e autorização (URL configurável por ambiente) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8,5/10**

**Justificativa:**

**Pontos Positivos:**
- **Arquitetura bem estruturada**: Separação clara em módulos (common, domain, application) seguindo princípios de arquitetura hexagonal
- **Padrões de projeto**: Uso adequado de Chain of Responsibility (handlers de validação), Factory (LimiteHandlerFactory), Strategy (diferentes handlers por tipo de transação)
- **Cobertura de testes**: Testes unitários abrangentes (estimativa 80%+ cobertura) com uso correto de Mockito e JUnit 5
- **Separação de responsabilidades**: Controllers, services, repositories e processors bem definidos
- **Tratamento de exceções**: Hierarquia estruturada de exceções de negócio com handler global
- **Documentação**: OpenAPI/Swagger para documentação de APIs
- **Observabilidade**: Integração com Prometheus e Spring Actuator para métricas e health checks
- **Configuração por ambiente**: Uso de profiles e configmaps para diferentes ambientes

**Pontos de Atenção:**
- **Complexidade em Processors Camel**: Lógica de negócio complexa distribuída em múltiplos processors pode dificultar manutenção e debug
- **Mappers extensos**: LimitesPixMapper com 20kb pode indicar necessidade de refatoração em mappers menores e mais coesos
- **Testes grandes**: Alguns testes unitários com mais de 200 linhas podem ser quebrados em testes menores e mais focados
- **Logs**: Oportunidade de melhoria na estratégia de logging estruturado
- **Configurações hardcoded em testes**: Alguns valores fixos em testes poderiam ser parametrizados
- **Tratamento de erros genéricos**: Em alguns pontos, exceções genéricas poderiam ser mais específicas

**Recomendações:**
- Considerar refatoração de processors Camel muito complexos em serviços menores
- Quebrar LimitesPixMapper em múltiplos mappers especializados
- Implementar logging estruturado (JSON) para melhor rastreabilidade
- Adicionar mais testes de integração end-to-end
- Documentar decisões arquiteturais em ADRs (Architecture Decision Records)

---

## 14. Observações Relevantes

1. **Arquitetura Multi-Módulo**: O projeto é estruturado em 3 módulos Maven (common, domain, application), promovendo separação de conceitos e reusabilidade

2. **Orquestração com Apache Camel**: Uso intensivo de rotas Camel para orquestração de fluxos complexos, permitindo composição de integrações de forma declarativa

3. **Versionamento de API**: Implementa versionamento de endpoints (v1 e v2) permitindo evolução da API sem quebrar clientes existentes

4. **Regras Banco Central**: Implementa regras específicas do Bacen para PIX, como limite de R$ 1.000 para agendamento noturno

5. **Segurança OAuth2**: Autenticação via JWT com validação de CPF/CNPJ do usuário logado contra dados da requisição

6. **Mensageria Assíncrona**: Uso de GCP PubSub para desacoplamento e processamento assíncrono de notificações

7. **Infraestrutura como Código**: Configuração completa de deployment em Kubernetes/OpenShift via YAML

8. **Pipeline CI/CD**: Integração com Jenkins para automação de build, testes e deploy

9. **Monitoramento**: Métricas Prometheus expostas via Spring Actuator na porta 9090

10. **Testes Arquiteturais**: Uso de ArchUnit para validação de regras arquiteturais no build

11. **Padrão Enterprise Votorantim**: Uso de bibliotecas customizadas (arqt-base-master-springboot, sboot-arqt-base-microservices-error) seguindo padrões corporativos

12. **Health Checks**: Endpoints de liveness e readiness configurados para orquestração Kubernetes

13. **Profiles de Teste**: Separação de testes em profiles (unit, integration, functional, architecture) para execução seletiva

14. **Geração de Clientes Swagger**: Build automatizado gera clientes REST a partir de especificações OpenAPI de sistemas integrados

15. **Tratamento de 46 Tipos de Erro**: Mapeamento completo de erros da API Gestão Limites para mensagens de negócio amigáveis

16. **Chain of Responsibility**: Implementação elegante de validação de limites por tipo de transação com 9 níveis de handlers

17. **Categorização Inteligente**: Limites categorizados em 7 tipos com ordenação específica para melhor UX

18. **Pré-validação Transacional**: Validação preventiva antes de processar transação, evitando falhas tardias

19. **Suporte Multi-tenant**: Preparado para atender múltiplas divisões comerciais do banco

20. **Resiliência**: Tratamento robusto de falhas de integrações com fallbacks e mensagens apropriadas