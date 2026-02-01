# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-ccbd-base-atom-contabil** é um serviço atômico responsável por sintetizar transações efetivadas de contas correntes e gerar movimentações contábeis correspondentes. O sistema consome mensagens de transações via Google Cloud Pub/Sub, processa as informações, cria registros de movimentação contábil em banco de dados MySQL e mantém lotes de movimentação em banco Sybase. Para cada transação, são geradas movimentações tanto para contas normais quanto para contas espelho, conforme parametrização contábil configurada.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal de inicialização da aplicação Spring Boot |
| **ListenerTransacaoContaCorrente** | Listener que consome mensagens do Pub/Sub contendo transações efetivadas |
| **MovimentoContabilService** | Serviço principal que orquestra a criação de movimentos contábeis e detalhes de lote |
| **LoteContabilCacheService** | Gerencia a criação e cache de lotes contábeis |
| **PubSubService** | Serviço de integração com Google Cloud Pub/Sub |
| **MovimentoContabil** (entity) | Entidade JPA representando um movimento contábil no MySQL |
| **MovimentoContabilRepository** | Repositório JPA para persistência de movimentos contábeis |
| **LoteMovimentoContabilRepository** | Repositório JDBI para operações de lote no Sybase |
| **DetalheLoteMovimentoContabilRepository** | Repositório JDBI para detalhes de lote no Sybase |
| **ParametroMovimentoContabilRepository** | Repositório JDBI para consulta de parâmetros contábeis |
| **MovimentoContabilMapper** | Mapper MapStruct para conversão de TransacaoEfetivada em MovimentoContabil |
| **BCODataBaseConfiguration** | Configuração de conexão com banco Sybase (DBCONTACORRENTE) |
| **CCBDDataBaseConfiguration** | Configuração de conexão com banco MySQL (CCBDContaCorrente) |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Spring Data JPA** (persistência MySQL)
- **JDBI 3.12.0** (acesso ao Sybase)
- **Hibernate 5.2.1.Final** (ORM)
- **MapStruct** (mapeamento de objetos)
- **Lombok** (redução de boilerplate)
- **MySQL 8.4.0** (banco de dados principal)
- **Sybase ASE** (banco de dados legado)
- **Google Cloud Pub/Sub** (mensageria)
- **Atlante Sidecar Mensageria** (biblioteca de integração Pub/Sub)
- **Caffeine Cache** (cache em memória)
- **Logback** (logging em formato JSON)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **OpenAPI/Swagger** (documentação de API)
- **JUnit 5 + Mockito** (testes unitários)

---

## 4. Principais Endpoints REST

Não se aplica. O sistema é orientado a eventos (event-driven), consumindo mensagens de filas Pub/Sub. Não expõe endpoints REST de negócio, apenas endpoints de monitoramento via Spring Actuator (porta 9090).

---

## 5. Principais Regras de Negócio

1. **Consumo de Transações Efetivadas**: O sistema consome mensagens contendo transações efetivadas de contas correntes via Pub/Sub.

2. **Parametrização Contábil**: Para cada transação, consulta parâmetros contábeis (contas contrapartida débito/crédito) baseados na modalidade da conta e código do banco.

3. **Criação de Lotes Contábeis**: Agrupa movimentos contábeis em lotes identificados por instituição bancária, número de lote e data de efetivação. Utiliza cache para evitar duplicação.

4. **Geração de Movimentos Contábeis**: Para cada parâmetro contábil encontrado, cria um registro de movimento contábil no MySQL, invertendo débito/crédito conforme o tipo da transação.

5. **Detalhamento de Lotes**: Cria ou atualiza registros de detalhe de lote no Sybase, agregando valores por transação e contas contrapartida.

6. **Tratamento de Duplicidade**: Implementa controle de duplicidade para lotes e detalhes, lançando exceções específicas para reprocessamento ou ACK.

7. **Compensação de Transações**: Em caso de falha ao persistir detalhe de lote, executa rollback deletando o movimento contábil criado.

8. **Identificação de Liquidação**: Para transações PIX sem número de documento, utiliza o NSU (número sequencial único) como identificador.

9. **Instituições Bancárias**: Suporta Banco Votorantim (código 6556/161) e Banco BV S.A. (código 51/436).

10. **Contas Espelho**: Para cada transação, gera movimentações tanto para contas normais quanto para contas espelho, conforme parametrização.

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **TransacaoEfetivada**: Representa uma transação efetivada recebida via mensageria (não persistida, apenas processada).
- **MovimentoContabil**: Entidade JPA persistida no MySQL, representa um movimento contábil individual.
- **LoteMovimentoContabil**: Representa um lote de movimentos contábeis no Sybase.
- **DetalheLoteMovimentoContabil**: Representa o detalhe agregado de um lote por transação e contas contrapartida no Sybase.
- **ParametroMovimentoContabil**: Representa a parametrização de contas contrapartida para débito e crédito.

**Relacionamentos:**

- Um **LoteMovimentoContabil** agrupa múltiplos **MovimentoContabil** (relacionamento 1:N via cdLoteMovimentoContabil).
- Um **LoteMovimentoContabil** possui múltiplos **DetalheLoteMovimentoContabil** (relacionamento 1:N via cdLoteMovimentoContabil).
- Um **DetalheLoteMovimentoContabil** agrega movimentos de uma mesma transação e contas contrapartida dentro de um lote.
- **ParametroMovimentoContabil** é consultado para definir as contas contrapartida de cada **MovimentoContabil**.

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbLoteMovimentoContabil | tabela | SELECT | Consulta lotes de movimento contábil existentes no Sybase para evitar duplicação |
| TbParametroMovimentoContabil | tabela | SELECT | Consulta parâmetros contábeis (contas contrapartida) por modalidade e banco no Sybase |
| TbDetalheLoteMovimentoContabil | tabela | SELECT | Consulta detalhes de lote existentes (implícito no UPDATE) no Sybase |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbMovimentoContabil | tabela | INSERT | Insere novos movimentos contábeis no MySQL |
| TbMovimentoContabil | tabela | DELETE | Remove movimento contábil em caso de compensação de transação no MySQL |
| TbLoteMovimentoContabil | tabela | INSERT | Cria novos lotes de movimento contábil no Sybase |
| TbDetalheLoteMovimentoContabil | tabela | INSERT | Cria novos detalhes de lote no Sybase |
| TbDetalheLoteMovimentoContabil | tabela | UPDATE | Atualiza valor total de movimento em detalhes de lote existentes no Sybase |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | leitura | Configuração de logging | Arquivo de configuração de logs em formato JSON para cada ambiente (des/uat/prd) |
| openapi.yaml | leitura | Documentação Swagger | Contrato OpenAPI da aplicação (vazio, sem endpoints REST de negócio) |
| application.yml | leitura | Configuração Spring | Arquivo de propriedades da aplicação por perfil |
| application-local.yml | leitura | Configuração Spring | Arquivo de propriedades para ambiente local |

---

## 10. Filas Lidas

**Fila Pub/Sub Consumida:**

- **Subscription**: `projects/bv-ccbd-{env}/subscriptions/business-ccbd-base-movimento-contabil-413-sub`
  - **Ambiente DES**: `projects/bv-ccbd-des/subscriptions/business-ccbd-base-movimento-contabil-413-sub`
  - **Ambiente UAT**: `projects/bv-ccbd-uat/subscriptions/business-ccbd-base-movimento-contabil-413-sub`
  - **Ambiente PRD**: `projects/bv-ccbd-prd/subscriptions/business-ccbd-base-movimento-contabil-413-sub`
- **Mensagem**: Transações efetivadas de contas correntes (objeto `TransacaoEfetivada` em JSON)
- **Listener**: `ListenerTransacaoContaCorrente`
- **Provider**: Google Cloud Pub/Sub (GCP)

---

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas, apenas consome.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Google Cloud Pub/Sub | Mensageria | Consumo de mensagens de transações efetivadas via subscription |
| Banco Sybase ASE (DBCONTACORRENTE) | Banco de Dados | Leitura e escrita de lotes e detalhes de movimento contábil, consulta de parâmetros |
| Banco MySQL (CCBDContaCorrente) | Banco de Dados | Persistência de movimentos contábeis individuais |
| Atlante Sidecar | Biblioteca | Biblioteca de integração com Pub/Sub do ecossistema Atlante |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Código bem estruturado seguindo padrões de arquitetura em camadas (config, domain, service, repository, mapper)
- Uso adequado de frameworks modernos (Spring Boot, JDBI, MapStruct)
- Separação clara de responsabilidades entre classes
- Implementação de tratamento de exceções customizadas (MovimentoContabilException, MovimentoContabilReprocessamentoException)
- Boa cobertura de testes unitários (>80% aparente)
- Uso de Lombok para redução de boilerplate
- Implementação de cache para otimização de consultas de lotes
- Logs estruturados em JSON
- Compensação de transações em caso de falha
- Documentação técnica presente (README.md)

**Pontos de Melhoria:**
- Alguns métodos longos no `MovimentoContabilService` que poderiam ser refatorados
- Falta de documentação JavaDoc em algumas classes e métodos públicos
- Configuração de cache comentada (`@Cacheable`) no `LoteContabilCacheService`
- Alguns testes poderiam ter nomes mais descritivos seguindo padrão BDD
- Falta de testes de integração
- Constantes mágicas em alguns pontos (ex: "ROBO.ANALITICO", "user")
- Poderia haver maior uso de constantes centralizadas

O código demonstra maturidade técnica, boas práticas de desenvolvimento e preocupação com manutenibilidade, justificando a nota 8/10.

---

## 14. Observações Relevantes

1. **Arquitetura Event-Driven**: O sistema é totalmente orientado a eventos, sem endpoints REST de negócio, apenas monitoramento via Actuator.

2. **Multi-Database**: Utiliza dois bancos de dados distintos (MySQL e Sybase) com tecnologias diferentes (JPA e JDBI), exigindo configuração cuidadosa de transações.

3. **Estratégia de Reprocessamento**: Implementa exceções específicas para controlar ACK/NACK de mensagens Pub/Sub, permitindo reprocessamento seletivo.

4. **Cache de Lotes**: Utiliza Caffeine Cache com expiração de 60 minutos para otimizar consultas de lotes existentes.

5. **Logging Estruturado**: Todos os ambientes utilizam logging em formato JSON para facilitar análise em ferramentas de observabilidade.

6. **Containerização**: Aplicação preparada para execução em containers Docker com suporte a múltiplas camadas de dependências.

7. **Infraestrutura como Código**: Configurações de infraestrutura centralizadas em `infra.yml` para diferentes ambientes.

8. **Segurança**: Implementa OAuth2 Resource Server com validação JWT (desabilitada para endpoints públicos e Actuator).

9. **Monitoramento**: Expõe métricas Prometheus e endpoints de health check na porta 9090.

10. **Padrão Atlante**: Segue o padrão arquitetural Atlante do Banco Votorantim para microserviços atômicos.