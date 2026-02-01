# Ficha Técnica do Sistema

---

## 1. Descrição Geral

O sistema **sboot-ccbd-base-orch-notificacao-pix** é um serviço stateless desenvolvido em Java com Spring Boot, responsável por orquestrar e gerenciar notificações relacionadas a transações PIX e processos de portabilidade/reivindicação de chaves PIX. O sistema consulta dados cadastrais de clientes, chaves PIX e transações, processando-os para gerar notificações personalizadas que são expostas via API REST. Utiliza Apache Camel para orquestração de fluxos e integra-se com múltiplos serviços internos do Banco Votorantim.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application.java` | Classe principal de inicialização da aplicação Spring Boot |
| `NotificacaoPixController.java` | Controlador REST que expõe endpoints de notificações PIX |
| `NotificacaoPixService.java` | Serviço de domínio que orquestra a lógica de negócio de notificações |
| `NotificacaoPixConfiguration.java` | Configuração de beans e contexto da aplicação |
| `Router.java` | Configuração de rotas Apache Camel para orquestração |
| `CamelContextWrapper.java` | Wrapper do contexto Camel para gerenciamento de templates |
| `ClienteRepositoryImpl.java` | Implementação de repositório para consulta de dados cadastrais |
| `ChaveRepositoryImpl.java` | Implementação de repositório para consulta de chaves PIX |
| `TransacaoRepositoryImpl.java` | Implementação de repositório para consulta de transações PIX |
| `ClienteMapper.java` | Mapeamento de dados de cliente entre representações |
| `NotificacoesRepresentationMapper.java` | Mapeamento de notificações para representação de API |
| `TransacaoMapper.java` | Mapeamento de transações PIX |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Spring Security** (autenticação OAuth2/JWT)
- **Apache Camel 3.19.0** (orquestração de fluxos)
- **Swagger/OpenAPI 3.0** (documentação de API)
- **RestTemplate** (cliente HTTP)
- **Lombok** (redução de boilerplate)
- **JUnit 5** (testes unitários)
- **Mockito** (mocks em testes)
- **Maven** (gerenciamento de dependências)
- **Micrometer/Prometheus** (métricas)
- **Logback** (logging)
- **Docker** (containerização)
- **Kubernetes/OpenShift** (orquestração de containers)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/banco-digital/pix/notificacoes` | `NotificacaoPixController` | Retorna lista de notificações PIX para um cliente em um período |
| GET | `/v1/banco-digital/pix/existe/notificacoes` | `NotificacaoPixController` | Verifica se existem notificações pendentes para um cliente |

**Parâmetros comuns:**
- Header: `numeroConta` (obrigatório)
- Query: `dataInicio`, `dataFim` (opcionais)

---

## 5. Principais Regras de Negócio

1. **Filtragem de Notificações de Chaves PIX:**
   - Apenas chaves com status "AGUARDANDO_RESOLUCAO" geram notificações
   - Exclui solicitações de reivindicação onde o perfil é "SOLICITANTE"
   - Filtra notificações dentro do período especificado (padrão: últimos 15 dias)

2. **Diferenciação de Mensagens por Instituição:**
   - Mensagens diferentes para portabilidade/reivindicação quando o participante doador é BV (código 59588111 ou 01858774)
   - Mensagens específicas para outras instituições financeiras

3. **Período de Consulta:**
   - Se não informado, utiliza período padrão de 15 dias retroativos
   - Se informada apenas data inicial, adiciona 14 dias
   - Se informada apenas data final, subtrai 14 dias

4. **Validação de Conta:**
   - Verifica se a conta informada pertence ao CPF/CNPJ do token JWT
   - Valida existência da conta no sistema de dados cadastrais

5. **Tipos de Transações PIX Monitoradas:**
   - PIX_TRANSFERENCIA_ENVIADA
   - PIX_TRANSFERENCIA_RECEBIDA
   - PIX_PAGAMENTO_ENVIADO
   - PIX_PAGAMENTO_RECEBIDO
   - PIX_DEVOLUCAO_ENVIADA
   - PIX_DEVOLUCAO_RECEBIDA

6. **Prazo de Resposta:**
   - Notificações de portabilidade/reivindicação têm prazo padrão de 7 dias para resposta

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **Cliente**: Representa o cliente bancário
  - Atributos: numeroCpfCnpjCliente, numeroConta, codigoBanco, agencia, nomeCliente
  - Relacionamentos: possui lista de ChaveDict e lista de Transacao

- **ChaveDict**: Representa uma chave PIX em processo de portabilidade/reivindicação
  - Atributos: chave, status, tipo, perfil, dataInicio, codigoPortabilidade
  - Relacionamentos: possui Participante, ParticipanteDoador e Requisitante

- **Transacao**: Representa uma transação PIX
  - Atributos: id, categoria, titulo, descricao, valor, data

- **Periodo**: Value object para representar intervalo de datas
  - Atributos: dataInicio, dataFim

- **Notificacao**: Entidade de domínio que encapsula mensagens de notificação
  - Contém mapeamento de mensagens por tipo de evento

**Relacionamentos:**
- Cliente 1 ---> N ChaveDict
- Cliente 1 ---> N Transacao
- Cliente 1 ---> 1 Periodo
- ChaveDict 1 ---> 1 Participante
- ChaveDict 1 ---> 1 ParticipanteDoador
- ChaveDict 1 ---> 1 Requisitante

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

*Observação: O sistema não acessa diretamente banco de dados. Todas as consultas são realizadas via APIs REST de outros microserviços.*

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

*Observação: O sistema é somente leitura, não realiza operações de escrita em banco de dados.*

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `application.yml` | Leitura | Spring Boot (startup) | Arquivo de configuração da aplicação com profiles (local, des, qa, uat, prd) |
| `logback-spring.xml` | Leitura | Logback (runtime) | Configuração de logs da aplicação |
| `sboot-ccbd-base-orch-notificacao-pix.yaml` | Leitura | Swagger Codegen (build) | Especificação OpenAPI para geração de código |
| `sboot-glob-base-atom-cliente-dados-cadastrais.yaml` | Leitura | Swagger Codegen (build) | Especificação OpenAPI do cliente de dados cadastrais |

---

## 10. Filas Lidas

não se aplica

*Observação: O sistema não consome mensagens de filas.*

---

## 11. Filas Geradas

não se aplica

*Observação: O sistema não publica mensagens em filas.*

---

## 12. Integrações Externas

| Sistema Integrado | Tipo | Descrição |
|-------------------|------|-----------|
| `sboot-glob-base-atom-cliente-dados-cadastrais` | API REST | Consulta dados cadastrais do cliente (nome, agência, conta, banco) |
| `sboot-ccbd-base-orch-chaves-dict-port` | API REST | Consulta chaves PIX em processo de portabilidade/reivindicação |
| `sboot-ccbd-base-atom-cc-extrato` | API REST | Consulta transações PIX da conta corrente |
| OAuth2/JWT Provider | Autenticação | Validação de tokens JWT para autenticação (URLs variam por ambiente) |

**Observações:**
- Todas as integrações utilizam RestTemplate com autenticação básica ou JWT
- URLs são configuradas por ambiente via variáveis de ambiente
- Comunicação interna via service discovery do Kubernetes (*.svc.cluster.local)

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo princípios de Clean Architecture (separação em módulos: domain, application, common)
- Uso adequado de padrões de projeto (Repository, Mapper, Builder)
- Boa cobertura de testes unitários (presença de classes de teste para praticamente todas as classes de produção)
- Uso de Lombok reduzindo boilerplate
- Configuração adequada de profiles para diferentes ambientes
- Documentação via Swagger/OpenAPI
- Uso de Apache Camel para orquestração, promovendo desacoplamento

**Pontos de Melhoria:**
- Presença de código comentado em várias classes (ex: NotificacoesRepresentationMapper, Notificacao)
- Algumas classes com responsabilidades múltiplas (ex: NotificacoesRepresentationMapper com lógica de negócio)
- Strings hardcoded em várias partes do código (códigos de banco, mensagens)
- Falta de constantes centralizadas para valores mágicos
- Tratamento de exceções genérico em alguns pontos
- Ausência de logs estruturados em pontos críticos
- Algumas classes de domínio com muitos atributos sem validação
- Falta de documentação JavaDoc em métodos públicos
- Dependências com versões desatualizadas (Spring Security 5.7.13 tem vulnerabilidades conhecidas)

---

## 14. Observações Relevantes

1. **Segurança:**
   - Sistema utiliza OAuth2 com JWT para autenticação
   - Extrai CPF/CNPJ do token JWT para validação de acesso
   - Configuração de certificados via volume Kubernetes

2. **Observabilidade:**
   - Endpoints de health check em porta separada (9090)
   - Integração com Prometheus para métricas
   - Logs em formato JSON para facilitar parsing

3. **Deployment:**
   - Containerizado com Docker
   - Configuração de recursos (CPU/Memory) definida no infra.yml
   - Probes de liveness e readiness configurados
   - Suporte a múltiplos ambientes (des, qa, uat, prd)

4. **Padrões de Código:**
   - Utiliza arquitetura hexagonal (ports and adapters)
   - Separação clara entre camadas de apresentação, domínio e infraestrutura
   - Uso de DTOs para comunicação entre camadas

5. **Limitações Identificadas:**
   - Sistema não possui cache, todas as consultas são síncronas
   - Não há tratamento de circuit breaker para falhas em integrações
   - Ausência de retry automático em caso de falha nas APIs externas
   - Período máximo de consulta limitado a 14 dias

6. **Dependências Críticas:**
   - Sistema depende fortemente da disponibilidade de 3 APIs externas
   - Falha em qualquer uma das APIs resulta em erro para o usuário final

---