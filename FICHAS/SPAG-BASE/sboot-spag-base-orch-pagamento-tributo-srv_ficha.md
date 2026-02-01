# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-spag-base-orch-pagamento-tributo-srv** é um sistema orquestrador de pagamentos de tributos e concessionárias desenvolvido em Spring Boot com Apache Camel. O sistema atua como intermediário entre parceiros externos e os sistemas internos do banco, gerenciando todo o fluxo de validação, efetivação, liquidação e callback de pagamentos de tributos via código de barras/linha digitável.

O sistema suporta duas versões de API (v1 e v2) e implementa uma estratégia de migração progressiva entre provedores de liquidação (CellCoin e Santander/ARRC) através de feature toggles, permitindo transição gradual baseada em critérios como CNPJ do cliente e cache de códigos de barras.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **PagamentoTributoSrvController** (v1) | Controller REST v1 - recebe requisições de pagamento de tributos e callbacks de parceiros |
| **PagamentoTributoSrvControllerV2** | Controller REST v2 - versão atualizada com modelo de resposta diferenciado |
| **PagamentoTributoSrvService** | Serviço principal que orquestra o fluxo via Apache Camel, sanitiza dados e valida regras iniciais |
| **PagamentoTributoSrvRouter** | Rota Apache Camel que define o fluxo completo: validação → efetivação TEF → liquidação → integração esteira → callback |
| **FeatureToogleService** | Gerencia feature toggles para migração progressiva entre provedores de liquidação |
| **PagamentoRepositoryImpl** | Adaptador para API de pagamentos (CRUD de lançamentos de tributos) |
| **SuporteNegocioRepositoryImpl** | Adaptador para validação de dados do tributo |
| **EfetivarTefRepositoryImpl** | Adaptador para efetivação de débito em conta corrente via TEF |
| **EfetivarMovimentoRepositoryImpl** | Adaptador para crédito em conta de favorecido (fintech) |
| **SpagArrcLiquidacaoTributoConsumoRepositoryImpl** | Adaptador para liquidação via Santander/ARRC |
| **IntegrarEsteiraRepositoryImpl** | Adaptador para integração com esteira legada via IBM MQ |
| **EstornarPagamentoRepositoryImpl** | Adaptador para estorno de pagamentos em caso de falha |
| **CallbackParceiroRepositoryImpl** | Adaptador para envio de callback assíncrono via RabbitMQ |
| **ParceriaRepositoryImpl** | Adaptador para validação de dados do parceiro |
| **SegurancaRepositoryImpl** | Adaptador para validação de CNPJ autorizado |
| **MQAdapter** | Gerador de XML (via Velocity) para mensagens IBM MQ |
| **ExceptionHandlerConfiguration** | Tratamento centralizado de exceções REST |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.x** - Framework base da aplicação
- **Apache Camel 3.2.0** - Orquestração de fluxos e integração
- **RabbitMQ** - Mensageria assíncrona (callbacks e estornos)
- **IBM MQ (JMS)** - Integração com esteira legada
- **Apache Velocity** - Geração de templates XML
- **Swagger/Springfox** - Documentação de APIs
- **OAuth2/JWT** - Segurança e autenticação
- **Jackson** - Serialização JSON
- **Lombok** - Redução de boilerplate
- **Mockito/JUnit** - Testes unitários
- **Maven** - Gerenciamento de dependências
- **Docker** - Containerização
- **Kubernetes/GCP** - Orquestração e deploy
- **PostgreSQL** - Banco de dados (via APIs atômicas)
- **Java 11** - Linguagem de programação

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/pagamentoTributoSrv | PagamentoTributoSrvController | Processa pagamento de tributo (versão 1) |
| POST | /v1/processarCallBackParceiro | PagamentoTributoSrvController | Processa callback de confirmação do parceiro |
| POST | /v2/pagamentoTributoSrv | PagamentoTributoSrvControllerV2 | Processa pagamento de tributo (versão 2 com resposta diferenciada) |

---

## 5. Principais Regras de Negócio

1. **Validação de CNPJ Autorizado**: Verifica se o CNPJ do cliente está autorizado a realizar pagamentos via API de Segurança
2. **Validação de Parceria**: Valida se a conta do parceiro não é vinculada PF/PJ (códigos 25/26) quando tipo de integração é "E" (externa)
3. **Validação de Tipo Cliente**: Para integrações externas, valida se tipo de cliente é "W" (wallet externo)
4. **Migração Progressiva ARRC**: 
   - Se CNPJ é do BV (01858774000110) E código de barras está em cache E documento está na lista de toggle → usa Santander/ARRC
   - Caso contrário → usa fluxo CellCoin tradicional
5. **Detecção de Duplicidade**: Retorna HTTP 208 (ALREADY_REPORTED) se pagamento já foi processado
6. **Estorno Automático**: Em caso de falha na integração com esteira ou callback, realiza estorno automático com ocorrência tipo 4
7. **Pré-confirmação Fintech**: Para contas fintech, credita o favorecido antes da liquidação final
8. **Mapeamento de Status ARRC**: 
   - PAID → Status 3 (Pago)
   - PROCESSING/PENDING → Status 7 (Aguardando processamento)
   - REJECTED → Status 4 (Rejeitado)
9. **Sanitização de Dados**: Remove caracteres especiais (&) de históricos e nomes antes do processamento
10. **Validação de Conta Especial**: Método is10000001() verifica se conta é especial para tratamento diferenciado
11. **Normalização de Texto**: Remove acentos e caracteres especiais de campos textuais

---

## 6. Relação entre Entidades

**PagamentoTributoSrv** (entidade principal)
- Contém **Participante** remetente (1:1)
- Contém **Participante** favorecido (1:1)
- Gera **Protocolo** de resposta (1:1)
- Possui **Ocorrencia** em caso de erro (1:N)
- Relaciona-se com **Parceria** via CNPJ (N:1)

**Participante**
- Contém dados de **ContaCorrente** (1:1)
- Possui tipo pessoa (PF/PJ) e tipo conta (CC/PG/CT)

**Protocolo**
- Pode conter **ProtocoloErro** (1:1)
- Referencia **PagamentoTributoSrv** (1:1)

**CallbackParceiro**
- Referencia **Protocolo** (1:1)
- Contém dados de retorno de confirmação

**DicionarioPagamento**
- Representa estrutura XML para IBM MQ
- Derivado de **PagamentoTributoSrv**

**Movimento**
- Representa movimentação financeira
- Relaciona-se com **ContaCorrente** (N:1)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TB_SPAG_LANCAMENTO_TRIBUTOS | Tabela | SELECT | Consulta de lançamentos de tributos existentes (via spag-base-atom-pagamento) |
| TB_SPAG_PARCERIA | Tabela | SELECT | Consulta de dados de parcerias (via spag-base-atom-parcerias) |
| TB_SEGURANCA_CNPJ | Tabela | SELECT | Validação de CNPJs autorizados (via spag-base-atom-seguranca) |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TB_SPAG_LANCAMENTO_TRIBUTOS | Tabela | INSERT | Inclusão de novo lançamento de tributo (via spag-base-atom-pagamento) |
| TB_SPAG_LANCAMENTO_TRIBUTOS | Tabela | UPDATE | Atualização de situação do lançamento (status 0-12, 99) (via spag-base-atom-pagamento) |
| TB_SPAG_OCORRENCIA | Tabela | INSERT | Registro de ocorrências de erro/estorno (via spag-base-atom-pagamento) |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| dicionario-esteira-tributo.xml | Leitura | MQAdapter / VelocityEngine | Template Velocity para geração de XML de integração com esteira IBM MQ |
| application.yml | Leitura | Spring Boot | Configurações da aplicação (URLs, credenciais, timeouts) |
| cacerts | Leitura | Kubernetes Volume | Certificados SSL para comunicação HTTPS |

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas, apenas publica.

---

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Routing Key / Destino | Descrição |
|--------------|------------|----------------------|-----------|
| events.business.confirmarPagamentoApi | RabbitMQ | SPAG.rk.confirmarPagamentoApi | Callback assíncrono para parceiros externos com resultado do pagamento |
| events.business.estornoPagamento | RabbitMQ | SPAG.estornoPagamento.v1 | Notificação de estorno de pagamento |
| QL.SPAG.SOLICITAR_PAGAMENTO_TRIBUTO_REQ.INT | IBM MQ | - | Integração com esteira legada ITP (dicionário XML de pagamento) |

---

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| **spag-base-atom-pagamento** | REST API | CRUD de lançamentos de tributos (incluir, atualizar situação, obter detalhes) |
| **spag-base-orch-suporte-negocio** | REST API | Validação de dados do tributo (linha digitável, valores, datas) |
| **ccbd-base-orch-efet-tef-digital** | REST API | Efetivação de débito em conta corrente via TEF |
| **pgft-base-orch-pagamentos** | REST API | Efetivação de crédito em conta de favorecido (fintech) |
| **spag-base-orch-liquidar-pagamento** | REST API | Processamento de estorno de pagamentos |
| **spag-base-atom-seguranca** | REST API | Validação de CNPJ autorizado (clientId) |
| **spag-base-atom-parcerias** | REST API | Consulta de dados de parceiros e validação de contas |
| **spag-arrc-orch-debits** | REST API | Liquidação de tributos via Santander/ARRC (fluxo migrado) |
| **spag-arrc-orch-taxes-utility** | REST API | Consulta de cache de códigos de barras para decisão de roteamento |
| **Gateway OAuth** | REST API | Obtenção de tokens de autenticação para APIs externas |
| **Esteira ITP (IBM MQ)** | Mensageria | Integração legada para processamento de pagamentos |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8.5/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura hexagonal bem definida com separação clara entre domínio, portas e adaptadores
- Uso adequado de padrões de projeto (Strategy para migração, Template Method para processadores Camel)
- Mappers isolados facilitam manutenção e evolução
- Configurações centralizadas e externalizadas
- Tratamento de exceções padronizado e consistente
- Feature toggles permitem migração progressiva sem impacto
- Cobertura de testes unitários abrangente com Mockito
- Logs estruturados para rastreabilidade
- Documentação Swagger para APIs
- Uso de enums para constantes, evitando magic numbers/strings

**Pontos de Melhoria:**
- Alguns processadores Camel poderiam ser mais coesos (responsabilidade única)
- Falta documentação inline em alguns métodos complexos
- Alguns métodos com muitos parâmetros (poderiam usar objetos de transferência)
- Nomenclatura de algumas variáveis poderia ser mais descritiva (ex: "is10000001")
- Falta de testes de integração end-to-end
- Dependência forte de múltiplas APIs externas sem circuit breaker explícito

---

## 14. Observações Relevantes

1. **Estratégia de Migração**: O sistema implementa uma estratégia sofisticada de migração entre provedores de liquidação (CellCoin → Santander/ARRC) usando feature toggles combinados com cache de códigos de barras e lista de documentos habilitados, permitindo rollback rápido em caso de problemas.

2. **Fluxo Complexo Orquestrado**: O fluxo completo envolve 8+ etapas: validação → inclusão lançamento → débito conta corrente → liquidação externa → integração esteira legada → callback parceiro, com tratamento de erro e estorno automático em cada ponto.

3. **Versionamento de API**: Suporta v1 e v2 simultaneamente, com diferença principal no modelo de resposta, permitindo evolução sem quebrar clientes existentes.

4. **Resiliência**: Implementa estorno automático em caso de falhas, garantindo consistência financeira mesmo em cenários de erro.

5. **Integração Híbrida**: Combina tecnologias modernas (REST, RabbitMQ) com sistemas legados (IBM MQ, XML), atuando como ponte entre arquiteturas.

6. **Pré-confirmação Fintech**: Para contas fintech, credita o favorecido antes da confirmação final da liquidação, melhorando experiência do usuário.

7. **Callback Assíncrono**: Notificação de parceiros externos via RabbitMQ desacopla o fluxo principal do processamento de confirmação.

8. **Validações de Segurança**: Múltiplas camadas de validação (CNPJ autorizado, tipo de conta, tipo de integração) garantem conformidade regulatória.

9. **Observabilidade**: Endpoints Actuator na porta 9090 para monitoramento de saúde e métricas.

10. **Infraestrutura Cloud-Native**: Deploy em Kubernetes/GCP com configuração de recursos (CPU 500m-1, Memory 512Mi-2Gi), probes de liveness/readiness e secrets gerenciados por cofre.

11. **Normalização de Dados**: Sanitização automática de caracteres especiais e acentos para compatibilidade com sistemas legados.

12. **Detecção de Duplicidade**: Retorna HTTP 208 para pagamentos já processados, evitando duplicação de cobranças.