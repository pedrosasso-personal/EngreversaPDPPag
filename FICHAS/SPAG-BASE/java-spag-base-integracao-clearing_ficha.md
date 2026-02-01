---
## Ficha Técnica do Sistema

### 1. Descrição Geral
Sistema de integração para processamento de mensagens de clearing bancário SPB (Sistema de Pagamentos Brasileiro). Recebe mensagens via MQ de diversos tipos (PAG, STR, LTR, SLC, TES), realiza transformações, validações e enriquecimento de dados, persiste informações em bancos de dados (ITP/SPAG) e roteia para filas de saída ou esteira de pagamentos. Suporta fluxos síncronos (via orquestrador de transferências) e assíncronos (legado ITP/SPAG), com regras específicas para fintech, correspondência bancária, devoluções R2 e notificações judiciais.

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **PagamentoMDB** | Message-Driven Bean que consome mensagens da fila de clearing e orquestra o processamento |
| **PagamentoBean** | Bean EJB principal que processa mensagens SPB/LTR, aplica regras de negócio, valida dados e coordena persistência |
| **PagamentoDAO** | Acesso a dados para operações em bancos ITP e SPAG (consultas, inclusões, atualizações) |
| **MensagemLTRDAO** | Acesso a dados específico para mensagens LTR (inclusão, consultas de controle e erros) |
| **PagamentoR2DAO** | Acesso a dados para devoluções R2 (consultas de movimentação e erros) |
| **PagamentoJMS** | Envio de mensagens JMS para filas de erro e solicitação de pagamento TEF |
| **TransferenciaIntegrationService** | Integração com orquestrador de transferências (processamento síncrono TED/TES) |
| **FeatureToggleService** | Consulta feature toggles para controle de fluxos (canais internos/externos, correspondência) |
| **TransferenciaMapper** | Mapeamento de CaixaEntradaDTO para TedInRepresentation (formato orquestrador) |
| **UtilCorrespondencia** | Validação de regras de correspondência bancária TED via feature toggles |
| **CamelClient** | Cliente HTTP para chamadas REST às APIs Camel (orquestrador, OAuth) |
| **CaixaEntradaDTO** | DTO principal com 100+ campos representando lançamento de entrada de pagamento |
| **DicionarioPagamento** | DTO completo (150+ campos) para serialização XML em fila TEF |
| **MensagemLTR** | DTO para mensagens LTR (LTR0001-LTR0008, SLC0005) |
| **MensagemTES** | DTO para mensagens TES (TES0004/TES0010) |

### 3. Tecnologias Utilizadas
- **Java EE**: EJB 3.1, JMS, JNDI
- **Persistência**: Spring JDBC, Stored Procedures (Oracle)
- **Integração**: JAX-RS (cliente REST), Apache HttpClient
- **Serialização**: JAXB (XML), Gson (JSON)
- **Segurança**: OAuth 2.0 (client_credentials), Basic Auth, WAS Alias
- **Logging**: SLF4J
- **Build**: Maven (multi-módulo)
- **Servidor**: WebSphere Application Server
- **Bibliotecas**: Apache Commons Lang3, Guava, PowerMock (testes)

### 4. Principais Endpoints REST
**Observação**: O sistema não expõe endpoints REST próprios (é consumidor). Consome os seguintes endpoints externos:

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | /v1/tedIn | Processa TED entrada via orquestrador de transferências |
| POST | /v1/stnIn | Processa TES entrada via orquestrador de transferências |
| GET | /v1/featureToggle/{feature} | Consulta feature toggles (ex: ft_recebimento_ted_sincrona_canais_internos) |
| POST | /oauth/token | Obtém token OAuth para autenticação nas APIs Camel |

### 5. Principais Regras de Negócio

1. **Identificação de Tipo de Mensagem**: Detecta tipo de mensagem SPB por tag XML raiz (PAG0107-PAG0151, STR0004-STR0052, LTR0001-LTR0008, SLC0005, TES0004/TES0010)

2. **Devolução R2**: Busca lançamento original no SPAG, inverte remetente/favorecido, define código transação 7300, cria novo lançamento de devolução

3. **Fintech**: Se conta tipo PG ou agência 1111/655, consulta cadastro fintech, altera favorecido para conta liquidação da fintech, preserva cliente original em campos específicos (ClienteFintech)

4. **Correspondência TED**: Valida via feature toggle (ft_text_spag_base_regras_correspondencia_ted) se TED deve seguir fluxo de correspondência bancária, avalia regras configuradas dinamicamente

5. **Sincronização TED/TES**: Decide entre processamento síncrono (orquestrador) ou assíncrono (legado ITP/SPAG) baseado em:
   - Canal (interno/externo)
   - Migração de participante
   - Feature toggles (ft_recebimento_ted_sincrona_canais_internos/externos)
   - Tipo de cliente (Cash/Wallet)

6. **Cash/Wallet**: Se tipo cliente 'C' ou 'W', marca FlParceiroExterno='S'

7. **Validação CNPJ Banco**: Identifica se é Votorantim (59588111000103) ou BV SA (01858774000110), ajusta código transação (7600 para banco)

8. **Conta Pagamento**: Trunca para 10 caracteres se tipo PG

9. **LTR0006**: Valida existência de LTR0004 origem antes de processar

10. **Notificação Judicial**: PAG0151/STR0051 grava também em tabela específica (TbLancamentoNotificacaoJudicial)

11. **Sanitização de Dados**: Remove acentos, caracteres especiais, aplica padding com zeros, valida formato CNPJ/CPF

12. **Parceiro Processamento**: Valida se cliente pode processar mensagem via orquestrador (TbControleFuncionalidadeParceiro)

### 6. Relação entre Entidades

**Entidades Principais:**

- **CaixaEntrada (ITP)**: Lançamento de entrada de pagamento, relaciona-se com Cliente, Conta, Fintech
- **Lancamento (SPAG)**: Lançamento processado, relaciona-se com LancamentoPessoa (remetente/favorecido), LancamentoClienteFintech
- **MensagemLTR (SPAG)**: Mensagens LTR/SLC, relaciona-se com ProcessamentoLTR
- **MensagemISPB (SPAG)**: Mensagens PAG/STR originais do SPB
- **NotificacaoJudicial (SPAG)**: Notificações judiciais vinculadas a lançamentos
- **ClienteGlobalFintech (ITP)**: Cadastro de fintechs, relaciona-se com ContaPagamentoFintech, ContaUsuarioFintech
- **ParticipanteMigracao (SPAG)**: Controle de migração de participantes para fluxo síncrono
- **ParceiroProcessamentoMensagem (SPAG)**: Configuração de parceiros autorizados a processar via orquestrador

**Relacionamentos:**
- CaixaEntrada → Cliente (1:N)
- Lancamento → LancamentoPessoa (1:2, remetente e favorecido)
- Lancamento → LancamentoClienteFintech (1:1, opcional)
- Lancamento → NotificacaoJudicial (1:1, opcional)
- MensagemLTR → ProcessamentoLTR (1:1)
- ClienteGlobalFintech → ContaPagamentoFintech (1:N)

### 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| tb_ispb_ispb | Tabela | SELECT | Conversão ISPB para código COMPE de bancos |
| TbControleMigracaoParticipante | Tabela | SELECT | Verifica se participante está migrado para fluxo síncrono |
| tbparametropagamentofintech | Tabela | SELECT | Parâmetros de configuração de fintech |
| tbcontapagamentofintech | Tabela | SELECT | Contas de liquidação de fintech |
| tbcontausuariofintech | Tabela | SELECT | Contas de usuários fintech |
| tbusuariocontafintech | Tabela | SELECT | Relacionamento usuário-conta fintech |
| BV_CONSULTA_CX_ENTRADA_R2_DEV | Procedure | SELECT | Consulta caixa entrada para devolução R2 |
| TbProcessamentoLTR | Tabela | SELECT | Controle de processamento de mensagens LTR |
| tb_doat_dominio_atributo | Tabela | SELECT | Descrições de erros R2 devolução |
| TbLancamento | Tabela | SELECT | Lançamentos SPAG para consulta e validação |
| TbLancamentoPessoa | Tabela | SELECT | Dados de remetente/favorecido de lançamentos |
| TbLancamentoClienteFintech | Tabela | SELECT | Dados de cliente fintech em lançamentos |
| TbTipoCliente | Tabela | SELECT | Tipos de cliente (Cash, Wallet, etc) |
| TbTipoFuncionalidade | Tabela | SELECT | Funcionalidades disponíveis para parceiros |
| TbControleFuncionalidadeParceiro | Tabela | SELECT | Controle de parceiros autorizados por funcionalidade |
| DBISPB.tb_erms_erro_mensagem | Tabela | SELECT | Catálogo de erros de mensagens SPB |
| PrConsultaMovDevolucao | Procedure | SELECT | Consulta movimentação SPB para devolução |

### 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbCaixaEntrada (ITP) | Tabela | INSERT | Inclusão de lançamento de entrada via BV_INCLUSAO_CAIXA_ENTRADA |
| TbLancamento (SPAG) | Tabela | INSERT | Inclusão de lançamento via PrIncluirLancamento |
| TbLancamento (SPAG) | Tabela | UPDATE | Atualização de cd_lancamento_origem em devoluções |
| tb_mvpg_movimento_PAG | Tabela | UPDATE | Atualização de status de mensagens PAG |
| tb_mvsr_movimento_STR | Tabela | UPDATE | Atualização de status de mensagens STR |
| TbLancamentoNotificacaoJudicial | Tabela | INSERT | Inclusão de notificação judicial via PrIncluirLancamentoNotificacaoJudicial |
| TbProcessamentoLTR | Tabela | INSERT | Inclusão de mensagem LTR via PrIncluirMensagemLTR |
| TbMensagemLTRErro | Tabela | INSERT | Inclusão de erro LTR via PrIncluirMensagemLTRErro |

### 9. Arquivos Lidos e Gravados
não se aplica

### 10. Filas Lidas

| Nome da Fila | Tecnologia | Descrição |
|--------------|-----------|-----------|
| Fila de Clearing (nome não especificado no código) | JMS | Fila principal que recebe mensagens SPB (PAG, STR, LTR, SLC, TES) do Sistema de Pagamentos Brasileiro para processamento |

### 11. Filas Geradas

| Nome da Fila | Tecnologia | Descrição |
|--------------|-----------|-----------|
| spagBancoLiquidanteErroRecebimentoQueue | JMS | Fila para envio de mensagens de erro durante processamento de mensagens SPB |
| spagSolicitarPagamentoTefQueue | JMS | Fila para envio de solicitações de pagamento TEF (XML DicionarioPagamento formatado) |
| Esteira de Pagamentos (via EnvioEsteiraBeanRemote) | JMS | Fila para envio de dicionário de pagamento em formato JSON para esteira de processamento |

### 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Orquestrador de Transferências (orch-transferencias) | REST API | Processamento síncrono de TED/TES entrada (endpoints /v1/tedIn, /v1/stnIn) |
| Feature Toggle Service | REST API | Consulta de feature toggles para controle de fluxos (endpoint /v1/featureToggle/{feature}) |
| OAuth Server | REST API | Autenticação OAuth 2.0 client_credentials para acesso às APIs Camel |
| Esteira de Pagamentos | EJB Remoto | Envio de dicionário de pagamento para processamento na esteira (EnvioEsteiraBeanRemote.enviarEsteira) |
| Sistema de Pagamentos Brasileiro (SPB) | MQ | Recebimento de mensagens de clearing bancário (PAG, STR, LTR, SLC, TES) |

### 13. Avaliação da Qualidade do Código

**Nota:** 5/10

**Justificativa:**

**Pontos Positivos:**
- Separação clara de responsabilidades em módulos (commons, domain, persistence, integration, business, jms)
- Uso de constantes e enums para valores fixos
- Logging estruturado com SLF4J e MDC para rastreabilidade
- Uso de DAOs para isolamento de acesso a dados
- Tratamento de recursos JMS em blocos finally

**Pontos Negativos:**
- **Classes excessivamente grandes**: PagamentoBean com 1500+ linhas, métodos muito longos (preencheCaixaEntrada, ajustaGeral)
- **Complexidade ciclomática alta**: switch/case extensos em processaMensagemMQ, múltiplos níveis de aninhamento
- **Duplicação de código**: lógica similar em preencheCaixaEntrada para PAG/STR, repetição de validações
- **Tratamento de exceções genérico**: uso excessivo de "throws Exception" sem especificidade
- **Falta de testes unitários evidentes**: não há menção a testes no código analisado
- **DTOs com 100+ campos**: CaixaEntradaDTO e DicionarioPagamento são classes muito grandes e complexas
- **Acoplamento**: PagamentoBean conhece muitos detalhes de implementação (DAOs, JMS, mappers)
- **Falta de documentação**: ausência de Javadoc em métodos críticos
- **Código comentado**: EmailHelper totalmente comentado deveria ser removido

**Recomendações:**
- Refatorar PagamentoBean em classes menores por tipo de mensagem (PagamentoProcessor, StrProcessor, LtrProcessor)
- Implementar padrão Strategy para processamento de diferentes tipos de mensagem
- Adicionar testes unitários e de integração
- Melhorar tratamento de exceções com tipos específicos
- Documentar regras de negócio complexas com Javadoc
- Considerar uso de Builder pattern para DTOs grandes

### 14. Observações Relevantes

1. **Sistema Crítico**: Processa clearing bancário em tempo real, transações configuradas como NOT_SUPPORTED para evitar rollback em cascata

2. **Suporte a 24 Tipos de Mensagem**: PAG (0107-0151), STR (0004-0052), LTR (0001-0008), SLC (0005), TES (0004/0010)

3. **Fluxo Híbrido**: Suporta processamento síncrono (novo, via orquestrador) e assíncrono (legado, via ITP/SPAG) com migração gradual controlada por feature toggles

4. **Fintech**: Lógica específica para alterar favorecido para conta de liquidação da fintech, mantendo cliente original para rastreabilidade

5. **Devolução R2**: Cria novo lançamento invertendo participantes (remetente vira favorecido e vice-versa), código transação 7300

6. **Segurança**: Autenticação OAuth 2.0 para APIs externas, basic auth via WAS Alias, trilha de auditoria em headers HTTP

7. **Proxy**: Configurado para mor-isa:8080 em chamadas HTTP

8. **SSL**: Suporta TLSv1/1.1/1.2 com NoopHostnameVerifier (atenção: pode ser risco de segurança)

9. **Retry**: Implementa retry automático de token OAuth em caso de 401

10. **Correspondência Bancária**: Regras dinâmicas configuradas via feature toggle, validação por reflection em campos anotados

11. **Versão**: 0.79.0 (em evolução ativa)

12. **Dependências Externas**: fjee-base-commons, java-spag-base-envio-esteira-business (bibliotecas internas do banco)