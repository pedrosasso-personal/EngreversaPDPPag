# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sbatch-spag-base-reproc-pagamentos** é um sistema batch desenvolvido em Spring Batch para reprocessamento automático de pagamentos no sistema SPAG (Sistema de Pagamentos). O sistema identifica lançamentos com falhas ou pendências no banco de dados e os envia para reprocessamento através de chamadas REST síncronas ou publicação de mensagens assíncronas no Google Cloud Pub/Sub. Suporta diferentes tipos de liquidação, incluindo transferências (TEF, DOC, Saque Digital, Compra e Débito) e boletos, com controle de horário de processamento e feature toggles para habilitar/desabilitar funcionalidades.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal que inicializa a aplicação Spring Batch |
| **BatchConfiguration** | Configura o job principal de reprocessamento de pagamentos |
| **StepConfiguration** | Define os steps do batch (reader, processor, writer) |
| **ReprocPagamentosItemReader** | Lê lançamentos pendentes de reprocessamento do banco de dados |
| **ReprocPagamentosProcessor** | Processa cada lançamento, validando horário e tipo de liquidação |
| **ReprocPagamentosItemWriter** | Registra logs dos lançamentos processados |
| **ReprocessamentoService** | Orquestra a lógica de negócio do reprocessamento |
| **ReprocessamentoRepository** | Envia transferências para reprocessamento (síncrono ou assíncrono) |
| **ReprocessamentoBoletoRepository** | Envia boletos para reprocessamento via Pub/Sub |
| **JdbiSpagRepositoryImpl** | Acessa o banco de dados SPAG usando JDBI |
| **FeatureToggleService** | Gerencia feature flags para controle de funcionalidades |
| **ReprocessamentoPublisher** | Publica mensagens no Google Cloud Pub/Sub |
| **RestTemplateUtil** | Utilitário para chamadas REST com autenticação OAuth2 |
| **LancamentoDTO** | Representa um lançamento com métodos de validação de tipo |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.x** (baseado no parent arqt-base-master-springbatch 2.0.1)
- **Spring Batch** - Framework para processamento batch
- **Spring Cloud Task** - Gerenciamento de tarefas batch
- **JDBI 3.9.1** - Acesso a banco de dados SQL
- **Microsoft SQL Server** (driver 7.4.0.jre11)
- **Google Cloud Pub/Sub** (spring-cloud-gcp 1.2.8.RELEASE)
- **IBM MQ 2.3.1** - Mensageria
- **Logback** - Logging com suporte a JSON
- **Lombok** - Redução de boilerplate
- **OAuth2** - Autenticação via API Gateway
- **ConfigCat** - Feature Toggle
- **Docker** - Containerização
- **Kubernetes** - Orquestração (jobs e deployments)
- **JUnit 5 + Mockito 4.5.1** - Testes unitários
- **Maven** - Gerenciamento de dependências

---

## 4. Principais Endpoints REST

O sistema é um batch job e não expõe endpoints REST próprios. Porém, **consome** os seguintes endpoints externos:

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/v1/reprocessarTransferencia/{cdLancamento}` | Envia transferência para reprocessamento síncrono (serviço orch-transferencias) |
| POST | `/auth/oauth/v2/token-jwt` | Obtém token OAuth2 para autenticação no API Gateway |

**Observação:** O endpoint de reprocessamento de transferências é configurável via propriedade `bv.service.orch-transferencias.url` e `endpoints.reprocessarTransferencia`.

---

## 5. Principais Regras de Negócio

1. **Seleção de Lançamentos para Reprocessamento:**
   - Lançamentos com status 0, 1, 7, 11 (boletos) ou 12 (transferências)
   - Data de inclusão >= D-1 (último dia)
   - Tempo decorrido desde última alteração >= 30 minutos (transferências) ou 60 minutos (boletos)
   - Códigos de liquidação específicos: 1, 12, 21, 22, 31, 32, 46, 53, 56, 57, 61, 62

2. **Controle de Horário de Processamento:**
   - Transferências: processamento permitido apenas entre 05h e 22h (horário de Brasília)
   - Boletos: processamento permitido 24x7 (sem restrição de horário)

3. **Tipos de Liquidação Suportados:**
   - **Código 1:** TEF (Transferência Eletrônica de Fundos)
   - **Código 21:** DOC
   - **Código 22:** Boleto
   - **Código 61:** Saque Digital
   - **Código 62:** Compra e Débito

4. **Estratégias de Reprocessamento:**
   - **Boletos (código 22):** Sempre via Pub/Sub assíncrono
   - **Transferências:** Síncrono (REST) ou assíncrono (Pub/Sub) conforme feature toggle `ft_boolean_spag_reprocessamento_habilitar_comunicacao_assincrona_transferencias`

5. **Autenticação e Segurança:**
   - Obtenção de token OAuth2 com até 5 tentativas
   - Token reutilizado durante a execução do batch

6. **Tratamento de Erros:**
   - Falhas no envio para reprocessamento são logadas mas não interrompem o batch
   - Lançamentos fora do horário permitido são ignorados (retornam null no processor)

---

## 6. Relação entre Entidades

**Entidade Principal:**
- **LancamentoDTO:** Representa um lançamento no sistema SPAG
  - `cdLancamento` (Long): Código único do lançamento
  - `cdLiquidacao` (int): Código do tipo de liquidação

**Entidades de Suporte:**
- **LancamentoReprocessar:** DTO para publicação no Pub/Sub (contém cdLancamento e cdLiquidacao)
- **TokenDTO:** Representa token OAuth2 obtido do API Gateway

**Relacionamentos:**
- Um lançamento pode ser de um único tipo de liquidação
- Cada tipo de liquidação determina a estratégia de reprocessamento
- Lançamentos são lidos do banco SPAG e enviados para sistemas externos (orch-transferencias ou Pub/Sub)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbLancamento | Tabela | SELECT | Tabela principal de lançamentos do SPAG. Lê lançamentos pendentes de reprocessamento com filtros por status, data de inclusão, código de liquidação e tempo decorrido desde última alteração. Utiliza índice `nnnn3TbLancamento`. |

**Campos utilizados:**
- `cdLancamento`: Código do lançamento
- `cdLiquidacao`: Tipo de liquidação
- `StLancamento`: Status do lançamento
- `DtInclusao`: Data de inclusão
- `DtAlteracao`: Data da última alteração

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

**Observação:** O sistema apenas lê dados do banco SPAG. As atualizações de status dos lançamentos são realizadas pelos sistemas de destino (orch-transferencias ou consumidores do Pub/Sub).

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | Leitura | /usr/etc/log/ (montado via ConfigMap) | Arquivo de configuração de logs por ambiente (des/qa/uat/prd). Define padrões de log em JSON e console. |
| application.yml | Leitura | src/main/resources/ | Arquivo de configuração principal da aplicação com propriedades por perfil (local, des, qa, uat, prd). |
| getLancamentosReprocessar.sql | Leitura | JdbiSpagRepositoryImpl | Query SQL para buscar lançamentos de transferências pendentes de reprocessamento. |
| getLancamentosBoletosReprocessar.sql | Leitura | JdbiSpagRepositoryImpl | Query SQL para buscar lançamentos de boletos pendentes de reprocessamento. |

**Observação:** O sistema não gera arquivos de saída. Toda comunicação é feita via REST ou Pub/Sub.

---

## 10. Filas Lidas

não se aplica

**Observação:** O sistema não consome mensagens de filas. Ele é iniciado como um job batch agendado no Kubernetes.

---

## 11. Filas Geradas

| Nome da Fila/Tópico | Tecnologia | Descrição |
|---------------------|------------|-----------|
| business-spag-base-reprocessamento-pagamentos | Google Cloud Pub/Sub | Tópico para publicação de lançamentos que devem ser reprocessados. Utilizado para boletos (sempre) e transferências (quando feature toggle ativo). Mensagens contêm cdLancamento e cdLiquidacao, com atributos de filtro (ex: "liquidacao":"22", "transferencias":"true"). |

**Configuração:**
- Project ID: Variável por ambiente (bv-spag-des, bv-spag-qa, bv-spag-uat, bv-spag-prd)
- Publisher: `ReprocessamentoPublisher` e `PubSubPublisher`
- Formato: JSON serializado via Gson

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **sboot-spag-base-orch-transferencias** | REST API | Serviço de orquestração de transferências. Recebe requisições POST para reprocessamento síncrono de lançamentos de transferências. Endpoint: `/v1/reprocessarTransferencia/{cdLancamento}`. Autenticação via Bearer token OAuth2. |
| **API Gateway BV** | OAuth2 Provider | Provê autenticação OAuth2 para chamadas aos serviços internos. Endpoint: `/auth/oauth/v2/token-jwt`. Utiliza client credentials flow. |
| **Google Cloud Pub/Sub** | Message Broker | Plataforma de mensageria para comunicação assíncrona. Recebe mensagens de lançamentos para reprocessamento (boletos e transferências). |
| **ConfigCat** | Feature Toggle | Serviço de gerenciamento de feature flags. Controla habilitação de comunicação assíncrona para transferências via flag `ft_boolean_spag_reprocessamento_habilitar_comunicacao_assincrona_transferencias`. |
| **Banco SPAG (SQL Server)** | Database | Banco de dados principal do sistema SPAG. Contém tabela TbLancamento com lançamentos a serem reprocessados. |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 8/10

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões Spring Batch (Reader, Processor, Writer)
- Separação clara de responsabilidades com uso de interfaces e implementações
- Boa cobertura de testes unitários (fixtures, mocks, testes de cenários)
- Uso adequado de injeção de dependências e configuração por perfis
- Implementação de retry para obtenção de token OAuth2
- Logs estruturados e informativos
- Uso de feature toggles para controle de funcionalidades
- Configuração externalizada via application.yml e ConfigMaps
- Tratamento de exceções adequado

**Pontos de Melhoria:**
- Algumas classes com múltiplas responsabilidades (ex: RestTemplateUtil gerencia token e executa requisições)
- Falta de documentação JavaDoc em métodos públicos
- Configuração de chunk size zerada no StepConfiguration (pode impactar performance)
- Uso de `lenient()` em testes indica possível problema de design
- Falta de validação de parâmetros de entrada em alguns métodos
- Tratamento genérico de exceções em alguns pontos (catch Exception)
- Código comentado no application.yml deveria ser removido

O código demonstra maturidade técnica e boas práticas, mas há espaço para melhorias em documentação e refinamento de alguns aspectos de design.

---

## 14. Observações Relevantes

1. **Execução como Kubernetes Job:** O sistema é executado como um CronJob no Kubernetes, não como serviço contínuo. A configuração está em `job.yaml`.

2. **Múltiplos Ambientes:** Suporta 5 ambientes (local, des, qa, uat, prd) com configurações específicas via profiles Spring e ConfigMaps Kubernetes.

3. **Estratégia Híbrida de Comunicação:** Implementa tanto comunicação síncrona (REST) quanto assíncrona (Pub/Sub) para transferências, controlada por feature toggle. Boletos sempre usam Pub/Sub.

4. **Segurança:** Utiliza Service Account Kubernetes (`ksa-spag-base-24466`) e autenticação OAuth2 para chamadas externas. Senhas armazenadas em Secrets Kubernetes.

5. **Monitoramento:** Logs estruturados em JSON para integração com ferramentas de observabilidade. Actuator habilitado na porta 9090 para health checks.

6. **Resiliência:** Implementa retry na obtenção de token (5 tentativas) e tratamento de erros que não interrompem o batch completo.

7. **Performance:** Utiliza índice específico (`nnnn3TbLancamento`) nas queries e NOLOCK para evitar bloqueios no banco.

8. **Versionamento:** Versão atual 0.16.0, indicando sistema em evolução ativa.

9. **Dependências Corporativas:** Utiliza bibliotecas internas do Banco Votorantim (arqt-base) para auditoria, feature toggle e configurações base.

10. **Docker:** Imagem base customizada (`pacotedocker-atle-base-java11`) com Java 11 e certificados corporativos.