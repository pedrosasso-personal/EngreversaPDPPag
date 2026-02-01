---
## Ficha Técnica do Sistema

### 1. Descrição Geral

Sistema de orquestração de migração de contas correntes e chaves PIX do Banco Votorantim (código 655) para o Banco Votorantim S.A. - BVSA (código 413). O sistema gerencia todo o ciclo de vida da portabilidade de chaves PIX, incluindo processos de reivindicação, exclusão, transferências de saldo e ativação de cartões de débito. Utiliza Apache Camel para orquestração de fluxos complexos multi-etapas, integrando-se com múltiplas APIs internas e externas, além de processamento assíncrono via RabbitMQ.

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **MigracaoChavePixController** | Controller REST que expõe endpoints para migração e exclusão de chaves PIX |
| **MigracaoChavePixServiceImpl** | Implementação do serviço de orquestração, delegando para rotas Camel |
| **MainMigracaoRouter** | Rota Camel principal que orquestra todo o fluxo de migração |
| **PortabilidadeChaveRouter** | Gerencia o fluxo de portabilidade de chaves PIX |
| **OperacoesChavePixRouter** | Controla operações específicas de chaves PIX (salvar/confirmar/concluir) |
| **MigracaoListener** | Listener RabbitMQ que consome mensagens das filas de portabilidade |
| **PortabilidadePixRepositoryImpl** | Integração com API SPAG para operações de portabilidade PIX |
| **GlobalRepositoryImpl** | Consulta dados cadastrais de contas via API Global |
| **TransferenciaRepositoryImpl** | Efetiva transferências TEF entre contas transitórias e BVSA |
| **DxcRepositoryImpl** | Ativa débito automático em cartões via API DXC |
| **MigracaoChavePixRepositoryImpl** | Gerencia dados de migração de chaves PIX via API CCBD |

### 3. Tecnologias Utilizadas

- **Framework Principal**: Spring Boot 2.x
- **Orquestração**: Apache Camel 3.0.1
- **Mensageria**: RabbitMQ
- **Segurança**: OAuth2 (Resource Server), JWT
- **HTTP Client**: RestTemplate, OAuth2RestTemplate
- **Documentação API**: Swagger 2 (OpenAPI)
- **Mapeamento**: MapStruct
- **Build**: Maven
- **Java**: JDK 11
- **Arquitetura Base**: arqt-base-master-springboot 1.0.10
- **Plataforma**: OpenShift (OCP) - Google Cloud Platform
- **CI/CD**: Jenkins

### 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/migracao/chavePix | MigracaoChavePixController | Inicia processo de migração de chave PIX |
| DELETE | /v1/migracao/chavePix | MigracaoChavePixController | Exclui chave PIX do processo de migração |

### 5. Principais Regras de Negócio

1. **Migração Multi-Etapa**: Processo de migração segue fluxo sequencial com estados bem definidos (INICIAL → NAO_ACEITO/ACEITO → EM_PORTABILIDADE → CONCLUIDO/EXCLUIDO)

2. **Portabilidade PIX**: Implementa protocolo completo de portabilidade do DICT com três fases: SALVAR (WAITING_RESOLUTION) → CONFIRMAR (CONFIRMED) → CONCLUIR (COMPLETED)

3. **Transferência de Saldo**: Realiza transferência TEF do saldo da conta origem (BV 655) para conta destino (BVSA 413) via conta transitória

4. **Validação de Chaves**: Exclui automaticamente chaves do tipo EVP (chave aleatória) antes do processamento

5. **Ativação de Cartões**: Ativa débito automático em cartões elegíveis (Mastercard, BV) na nova conta BVSA

6. **Controle de Portabilidade**: Verifica status de portabilidade em andamento e cancela se necessário antes de iniciar nova

7. **Reivindicação vs Portabilidade**: Diferencia tratamento entre processos de reivindicação e portabilidade de chaves

8. **Migração BVIN**: Atualiza sistema BVIN após conclusão da migração

9. **Tratamento de Erros**: Erros 5xx e 3xx geram OrquestracaoException (reenvio para fila), demais erros geram MigracaoPixException

10. **Validação de Saldo**: Verifica saldo disponível antes de efetuar transferências

### 6. Relação entre Entidades

**Entidades Principais:**

- **MigracaoChave**: Entidade central que representa uma migração de chave PIX
  - Relaciona-se com **ChavePix** (chave sendo migrada)
  - Contém **MigracaoConta** (dados da conta origem e destino)
  - Possui **StatusMigracaoEnum** (controle de estado)

- **ChavePix**: Representa uma chave PIX
  - Atributos: tipo (CPF/CNPJ/PHONE/EMAIL/EVP), valor, conta associada
  - Relaciona-se com **Entry** (entrada no DICT)

- **MigracaoConta**: Dados da conta em migração
  - Contém informações de conta origem (BV 655) e destino (BVSA 413)
  - Relaciona-se com **ContaGlobalDTO** (dados cadastrais completos)
  - Possui lista de **CartaoDebitoAtivarDXC**

- **Entry**: Representa entrada no DICT (Diretório de Identificadores de Contas Transacionais)
  - Relaciona-se com **StatusEnum** (status da portabilidade)
  - Contém **TipoChavePix** e dados da conta

**Relacionamentos:**
- MigracaoChave 1:N ChavePix
- MigracaoConta 1:1 ContaGlobalDTO
- MigracaoConta 1:N CartaoDebitoAtivarDXC
- ChavePix 1:1 Entry

### 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| Não se aplica | - | - | Sistema não acessa banco de dados diretamente, todas operações são via APIs REST |

**Observação**: O sistema consome dados de bancos de dados através de APIs intermediárias (CCBD, SPAG, Global, DXC), não realizando acesso direto a estruturas de dados.

### 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| Não se aplica | - | - | Sistema não atualiza banco de dados diretamente, todas operações de escrita são via APIs REST |

**Observação**: Atualizações são realizadas através de chamadas PUT/POST para APIs (CCBD, SPAG, DXC, BVIN), que por sua vez persistem os dados em seus respectivos bancos.

### 9. Arquivos Lidos e Gravados

Não se aplica. O sistema não realiza operações diretas de leitura ou gravação de arquivos. Todo processamento é baseado em APIs REST e mensageria (RabbitMQ).

### 10. Filas Lidas

| Nome da Fila | Tecnologia | Classe Consumidora | Descrição |
|--------------|------------|-------------------|-----------|
| **salvarchavepix.queue** | RabbitMQ | MigracaoListener | Consome mensagens para iniciar processo de portabilidade (salvar chave) |
| **confirmarchavepix.queue** | RabbitMQ | MigracaoListener | Consome mensagens para confirmar portabilidade de chave |
| **concluirchavepix.queue** | RabbitMQ | MigracaoListener | Consome mensagens para concluir portabilidade de chave |
| **excluirchavepix.queue** | RabbitMQ | MigracaoListener | Consome mensagens para excluir chave do processo de portabilidade |
| **migracao.chave.dlq.queue** | RabbitMQ | MigracaoListener | Dead Letter Queue - processa mensagens que falharão após tentativas |

**Configuração**: Todas as filas configuradas com `requeue=false` para evitar reprocessamento infinito.

### 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Produtora | Descrição |
|--------------|------------|------------------|-----------|
| **salvarchavepix.queue** | RabbitMQ | PortabilidadePixRabbitRepositoryImpl | Publica mensagens para iniciar portabilidade (exchange: salvarchavepix.exchange, routing key: salvarchavepix.rk) |
| **confirmarchavepix.queue** | RabbitMQ | PortabilidadePixRabbitRepositoryImpl | Publica mensagens para confirmar portabilidade (exchange: confirmarchavepix.exchange, routing key: confirmarchavepix.rk) |
| **concluirchavepix.queue** | RabbitMQ | PortabilidadePixRabbitRepositoryImpl | Publica mensagens para concluir portabilidade (exchange: concluirchavepix.exchange, routing key: concluirchavepix.rk) |
| **excluirchavepix.queue** | RabbitMQ | PortabilidadePixRabbitRepositoryImpl | Publica mensagens para excluir chave (exchange: excluirchavepix.exchange, routing key: excluirchavepix.rk) |

### 12. Integrações Externas

| Sistema/API | Tipo | Classe Responsável | Descrição |
|-------------|------|-------------------|-----------|
| **API SPAG - Chaves PIX DICT** | REST | ChavePixRepositoryImpl | Consulta e gerencia chaves PIX no diretório DICT do Banco Central |
| **API SPAG - Portabilidade PIX** | REST | PortabilidadePixRepositoryImpl | Operações de portabilidade: salvar, confirmar, concluir, cancelar, consultar status |
| **API SPAG - Transferências** | REST | TransferenciaRepositoryImpl | Efetiva transferências TEF entre contas (conta transitória e BVSA) |
| **API Global - Dados Cadastrais** | REST | GlobalRepositoryImpl | Consulta dados cadastrais completos de contas correntes |
| **API CCBD - Atom Migração** | REST | MigracaoChavePixRepositoryImpl | Gerencia dados de migração: consultar contas, alterar status, atualizar migração |
| **API CCBD - Conta Corrente Domínio** | REST | MigracaoContaRepositoryImpl | Migra conta corrente e atualiza status da conta |
| **API DXC - Cartões por CPF** | REST | QuinaRepositoryImpl | Lista cartões de débito associados a um CPF |
| **API DXC - Ativação Débito** | REST | DxcRepositoryImpl | Ativa débito automático em cartões |
| **API BVIN - Migração** | REST | MigracaoBvinRepositoryImpl | Atualiza sistema BVIN após migração |
| **API BVSA - Token JWT** | REST | GerarTokenJwtRepositoryImpl | Gera token JWT para autenticação em APIs BVSA |
| **API Consulta Saldo** | REST | SaldoRepositoryImpl | Consulta saldo disponível em conta corrente |
| **Gateway OAuth2 - Cartões** | OAuth2 | ApplicationConfiguration | Autenticação para APIs de cartões (client credentials) |
| **Gateway OAuth2 - Corporativo** | OAuth2 | ApplicationConfiguration | Autenticação para APIs corporativas (client credentials) |
| **RabbitMQ** | Mensageria | MigracaoListener, PortabilidadePixRabbitRepositoryImpl | Processamento assíncrono de portabilidade PIX |

**Ambientes Configurados**: Desenvolvimento, QA, UAT, Produção (URLs e credenciais por ambiente via infra.yml)

### 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- **Arquitetura bem estruturada**: Separação clara em camadas (controller, service, repository, domain) seguindo princípios SOLID
- **Uso adequado de padrões**: Implementação de Repository, Mapper, Strategy (enums com comportamento)
- **Orquestração robusta**: Apache Camel bem aplicado para fluxos complexos com decisões baseadas em predicates
- **Tratamento de exceções estruturado**: Hierarquia de exceções específicas do domínio com enum de mensagens padronizadas
- **Configuração externalizada**: Uso de properties e profiles para diferentes ambientes
- **Documentação API**: Swagger configurado para documentação automática
- **Segurança**: OAuth2 implementado corretamente com diferentes contextos (cart/corp)
- **Mensageria assíncrona**: RabbitMQ bem configurado com DLQ e controle de requeue

**Pontos de Melhoria:**
- **Falta de testes**: Não foram fornecidos testes unitários ou de integração no resumo
- **Acoplamento com Camel**: Lógica de negócio fortemente acoplada às rotas Camel, dificultando testes isolados
- **Documentação inline**: Ausência de JavaDoc nas classes principais
- **Complexidade dos Processors**: Alguns processors Camel concentram muita lógica, poderiam ser decompostos
- **Validações**: Não há evidência de validações robustas de entrada (Bean Validation)
- **Logs estruturados**: Não há menção a logs estruturados ou rastreabilidade (correlation ID)

**Recomendações:**
1. Implementar cobertura de testes (unitários, integração, contrato)
2. Adicionar JavaDoc nas interfaces e classes principais
3. Implementar validações com Bean Validation nos DTOs
4. Adicionar logs estruturados com correlation ID para rastreabilidade
5. Considerar extrair lógica de negócio dos processors Camel para services testáveis
6. Implementar circuit breaker para chamadas externas (Resilience4j)

### 14. Observações Relevantes

1. **Complexidade de Orquestração**: O sistema implementa um dos processos mais complexos do ecossistema bancário - migração de contas com portabilidade PIX. A orquestração via Apache Camel permite gerenciar múltiplas etapas interdependentes de forma declarativa.

2. **Conformidade Regulatória**: Implementa o protocolo oficial de portabilidade PIX do Banco Central, seguindo os estados definidos (OPEN, WAITING_RESOLUTION, CONFIRMED, COMPLETED, CANCELLED).

3. **Processamento Híbrido**: Combina processamento síncrono (APIs REST) com assíncrono (RabbitMQ), permitindo resiliência e desacoplamento temporal.

4. **Migração Banco Votorantim → BVSA**: Processo crítico de negócio que envolve transferência de saldo, migração de chaves PIX, ativação de cartões e atualização de múltiplos sistemas.

5. **Tratamento de Falhas**: Estratégia sofisticada de tratamento de erros com diferenciação entre erros recuperáveis (5xx/3xx → reenvio para fila) e não recuperáveis (4xx → exceção de negócio).

6. **Múltiplos Tipos de Chave PIX**: Suporta todos os tipos de chave PIX (CPF, CNPJ, telefone, e-mail, EVP) com tratamento específico para cada tipo.

7. **Segurança Multi-Camada**: Implementa OAuth2 com diferentes contextos (cartões, corporativo), JWT para BVSA e autenticação via Gateway.

8. **Configuração por Ambiente**: Infraestrutura preparada para múltiplos ambientes (des, qa, uat, prd) com configurações específicas via OpenShift.

9. **Iteradores Camel**: Uso de iteradores customizados (MigracaoIterator, EntryIterator, CartoesIterator) para processar lotes de dados de forma eficiente.

10. **Dependência de APIs Externas**: Sistema altamente dependente de disponibilidade de múltiplas APIs (SPAG, CCBD, Global, DXC), requerindo estratégias de resiliência robustas.

11. **Arquitetura Base Corporativa**: Utiliza arquitetura base padronizada (arqt-base-master-springboot) garantindo conformidade com padrões corporativos do Banco Votorantim.

12. **Plataforma Cloud**: Deployado em OpenShift na Google Cloud Platform, com probes de liveness/readiness configurados para alta disponibilidade.

---