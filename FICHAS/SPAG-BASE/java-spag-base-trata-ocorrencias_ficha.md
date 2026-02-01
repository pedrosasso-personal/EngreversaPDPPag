# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **java-spag-base-trata-ocorrencias** é um componente da plataforma SPAG (Sistema de Pagamentos) do Banco Votorantim, responsável pelo tratamento de ocorrências e erros que acontecem durante o processamento de pagamentos e transferências. 

O sistema recebe dicionários de pagamento com ocorrências, identifica o tipo de erro ocorrido, aplica tratamentos específicos conforme a natureza do problema (validação, débito/crédito em conta, transferências, etc.), registra as ocorrências em banco de dados e, quando necessário, efetua devoluções automáticas de valores (TED/DOC). Atua como um orquestrador de tratamento de exceções na esteira de pagamentos.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **TrataOcorrenciaBean** | Bean principal que coordena o tratamento de ocorrências: preenche dados, efetua ajustes, grava ocorrências no banco e chama serviços de agendamento |
| **FlTrataOcorrenciaImpl** | Enum que implementa estratégias de tratamento para cada tipo de flag de retorno (validação, débito, crédito, transferência, etc.) |
| **FlagRetornoVerificacao** | Identifica qual flag de retorno está presente no dicionário de pagamento e retorna o tratador apropriado |
| **TransferenciaBean** | Responsável por efetuar devoluções de TED e DOC, incluindo lançamentos e envio para esteira de pagamento |
| **TrataOcorrenciaDAOImpl** | DAO que realiza operações de banco de dados: atualização de lançamentos, inclusão de ocorrências, consulta de códigos de erro |
| **TransferenciaMapper** | Mapeia DicionarioPagamento para TedRefundRepresentation (representação de devolução TED) |
| **DevolucaoEnum** | Enum que mapeia códigos de ocorrência para códigos de devolução TED/DOC |
| **TrataOcorrencia (REST)** | Endpoint REST que expõe o serviço de tratamento de ocorrências |
| **TransferenciaIntegrationService** | Serviço de integração com CAMEL para processar devoluções automáticas de TED e consultar feature toggles |
| **CamelClient** | Cliente HTTP para comunicação com APIs CAMEL (orquestrador de transferências) |

---

## 3. Tecnologias Utilizadas

- **Java EE 7** (EJB 3.1, JAX-RS, CDI)
- **Maven** (gerenciamento de dependências e build)
- **Spring JDBC** (acesso a dados)
- **Apache HttpClient** (comunicação HTTP)
- **Gson** (serialização/deserialização JSON)
- **SLF4J + Log4j2** (logging)
- **IBM WebSphere Application Server** (servidor de aplicação)
- **Oracle JDBC** (banco de dados)
- **Swagger** (documentação de APIs REST)
- **JUnit, PowerMock, Mockito** (testes unitários)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/atacado/pagamentos/tratarOcorrencias/ | TrataOcorrencia | Recebe um dicionário de pagamento com ocorrências, processa o tratamento e retorna o dicionário atualizado |

---

## 5. Principais Regras de Negócio

1. **Identificação do Tipo de Ocorrência**: O sistema analisa flags de retorno no dicionário de pagamento para identificar em qual etapa da esteira ocorreu o erro (validação, débito, crédito, transferência, etc.)

2. **Tratamento Específico por Tipo**: Cada tipo de ocorrência possui um tratamento específico implementado no enum FlTrataOcorrenciaImpl (27 tipos diferentes)

3. **Devolução Automática**: Para erros em lançamentos de entrada (tipo "E"), o sistema efetua devolução automática via TED ou DOC, dependendo do tipo de liquidação

4. **Mapeamento de Códigos de Erro**: Códigos de ocorrência internos são mapeados para códigos CNAB e mensagens amigáveis através da tabela TbOcorrenciaErroPagamento

5. **Registro de Ocorrências**: Todas as ocorrências são registradas na tabela TbErroProcessamento para auditoria e análise

6. **Atualização de Status**: Lançamentos e agendamentos são atualizados com status apropriados conforme o tipo de erro

7. **Tratamento de Saldo Insuficiente**: Código comentado sugere que havia lógica de "teimosinha" (retentativas) para erros de saldo insuficiente

8. **Feature Toggle**: Sistema consulta feature toggles para habilitar/desabilitar funcionalidades como "TED Síncrona sem Estorno"

9. **Inversão de Participantes**: Na devolução, favorecido vira devedor e remetente vira credor

10. **Validação de Lançamento em Conta**: Verifica se o lançamento foi efetivado ou estornado antes de processar devolução

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **DicionarioPagamento**: Entidade central que representa um pagamento/transferência com todos seus atributos (remetente, favorecido, valores, datas, códigos, etc.)
- **OcorrenciaDTO**: Representa uma ocorrência/erro com código e descrição
- **ListaOcorrencia**: Coleção de ocorrências associadas a um pagamento
- **TrataOcorrenciaDTO**: Representa o registro de erro processado no banco
- **TedRefundRepresentation**: Representação de uma devolução TED com participantes, transação, finalidade e origem

**Relacionamentos:**
- DicionarioPagamento **contém** ListaOcorrencia (1:1)
- ListaOcorrencia **contém** múltiplas OcorrenciaDTO (1:N)
- DicionarioPagamento **é mapeado para** TedRefundRepresentation (transformação)
- TrataOcorrenciaDTO **referencia** DicionarioPagamento via CdLancamento (N:1)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbOcorrenciaErroPagamento | tabela | SELECT | Consulta descrições e códigos CNAB de ocorrências de erro |
| TbAgendamentoPagamento | tabela | SELECT | Verifica existência de agendamento para um lançamento |
| TbLancamento | tabela | SELECT | Consulta informações de lançamentos (implícito nas procedures) |
| Stored Procedure: prRetornaDataUtil | procedure | CALL | Obtém data útil para uma data e praça específicas |
| Stored Procedure: PrProximoDiaUtil | procedure | CALL | Obtém próximo dia útil para uma data e praça |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbLancamento | tabela | UPDATE | Atualiza status do lançamento (StLancamento), código de devolução (CdProtocoloDevolucao) e data de devolução |
| TbAgendamentoPagamento | tabela | UPDATE | Atualiza status do agendamento (CdStatusAgendamento) quando existe |
| TbErroProcessamento | tabela | INSERT | Insere registros de ocorrências/erros processados |
| Stored Procedure: PrIncluirLancamento | procedure | CALL | Inclui novo lançamento de devolução (TED/DOC) no sistema |

---

## 9. Arquivos Lidos e Gravados

não se aplica

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema/Serviço | Descrição |
|-----------------|-----------|
| **CAMEL (Orquestrador de Transferências)** | API REST para processar devoluções automáticas de TED e consultar feature toggles. Endpoints: `/v1/automaticTedRefund` (POST) e `/v1/featureToggle/{feature}` (GET) |
| **Esteira de Pagamento (EnvioEsteiraBean)** | EJB remoto para enviar dicionários de pagamento para processamento na esteira |
| **Agendamento de Pagamento (AgendaPagamentoBean)** | EJB remoto para agendar pagamentos (código comentado sugere uso para retentativas de saldo insuficiente) |
| **OAuth/Token Service** | Serviço de autenticação para obter access tokens para chamadas ao CAMEL |
| **Banco de Dados Global** | Consulta de datas úteis e próximos dias úteis através de procedures |

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades em camadas (business, persistence, domain, integration, rs)
- Uso adequado de padrões como Strategy (FlTrataOcorrenciaImpl), DAO, Mapper
- Logging presente em pontos críticos
- Tratamento de exceções implementado
- Uso de injeção de dependências (CDI/EJB)

**Pontos Negativos:**
- **Código comentado extensivamente** (especialmente em FlTrataOcorrenciaImpl e TrataOcorrenciaBean), indicando incerteza sobre funcionalidades ou falta de limpeza
- **Métodos muito longos** (ex: `getSqlMapParamsSPAGDevolucao` com 80+ linhas)
- **Falta de documentação JavaDoc** na maioria das classes
- **Strings hardcoded** em vários lugares (ex: "ESTEIRA_PAGAMENTO", "IntegracaoTratarOcorrencia")
- **Tratamento genérico de exceções** em alguns pontos (catch Exception)
- **Mistura de responsabilidades**: TransferenciaBean faz tanto lógica de negócio quanto chamadas de DAO
- **Código duplicado**: lógica de autorização repetida em GetRequest e PostRequest
- **Falta de validações**: não há validação de entrada nos endpoints REST
- **Uso de valores mágicos**: números como 999, 14, 7400 sem constantes nomeadas
- **Dependência de configurações externas** via JNDI sem fallback ou validação adequada

O código é funcional e organizado estruturalmente, mas precisa de refatoração para melhorar manutenibilidade, remover código morto e adicionar documentação.

---

## 14. Observações Relevantes

1. **Feature Toggle**: O sistema possui integração com feature toggles, especialmente para habilitar/desabilitar "TED Síncrona sem Estorno" (`ft_ted_sincrona_sem_estorno`)

2. **Código Legado Comentado**: Há extensa lógica comentada relacionada a tratamento de saldo insuficiente com "teimosinha" (retentativas), sugerindo que essa funcionalidade foi desabilitada ou está em transição

3. **Múltiplos Tipos de Liquidação**: Sistema suporta TED (STR/CIP), DOC, Tributos e Concessionárias, cada um com tratamento específico

4. **Segurança**: Usa autenticação básica e OAuth2 para integrações externas, com credenciais armazenadas em aliases do WebSphere

5. **Auditoria**: Todas as ocorrências são registradas com informações de usuário, data e processo que gerou o erro

6. **Inversão de Papéis na Devolução**: Na devolução, o favorecido original se torna o devedor e o remetente original se torna o credor

7. **Códigos de Evento**: Sistema usa códigos específicos para diferentes tipos de liquidação (CIP=11849, STR=11855, LIQ=11878)

8. **Transações**: Operações de banco são configuradas como NOT_SUPPORTED, delegando controle transacional para camadas superiores

9. **Proxy**: Comunicação HTTP passa por proxy "mor-isa" na porta 8080

10. **Versionamento**: Projeto está na versão 0.24.0, indicando que ainda está em desenvolvimento ativo