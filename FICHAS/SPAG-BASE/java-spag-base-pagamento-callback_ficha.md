# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **java-spag-base-pagamento-callback** é um componente Java EE responsável por processar callbacks e notificações de pagamentos. Ele atua como intermediário entre sistemas externos (fintechs/parceiros) e a infraestrutura interna do Banco Votorantim, gerenciando o ciclo de vida de solicitações de pagamento através de filas JMS, APIs REST e integrações com sistemas legados.

O componente recebe mensagens de filas MQ, consulta dados em banco de dados, envia callbacks/notificações para URLs de parceiros externos via HTTP, registra logs de controle e retorna informações para a esteira de pagamentos.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **PagamentoCallBackBean** | Processa mensagens de callback de validação de pagamento, consulta dados, envia para API externa e atualiza status do lançamento |
| **PagamentoNotificacaoBean** | Processa mensagens de notificação de finalização de pagamento, envia notificação para parceiros e posta na fila de retorno |
| **PagamentoCallbackProcessadorMDB** | MDB que consome mensagens da fila de callback (QL.SPAG.VALIDAR_PAGAMENTO_REQ.INT) |
| **PagamentoNotificacaoProcessadorMDB** | MDB que consome mensagens da fila de notificação (QL.SPAG.NOTIFICAR_PAGAMENTO_REQ.INT) |
| **PagamentoIntegrationServices** | Realiza chamadas HTTP para APIs externas de validação/confirmação de pagamento |
| **BoletoNotificacaoIntegrationServices** | Realiza chamadas HTTP para APIs de notificação de boleto (Banco 413) |
| **PagamentoNotificacaoIntegrationServices** | Realiza chamadas HTTP para APIs de notificação de tributos/consumo |
| **HttpCaapiIntegration** | Classe base para integrações HTTP com CA-API, gerencia tokens OAuth |
| **CriarTokenIntegration** | Gerencia criação e renovação de tokens OAuth para autenticação nas APIs |
| **CallBackFintechDAO** | Persiste logs de callbacks enviados na tabela TbRetornoSolicitacaoFintech |
| **NotificacaoFintechDAO** | Persiste logs de notificações enviadas na tabela TbNotificacaoFintech |
| **ControleRetornoCallBackDAO** | Persiste logs de retorno de callbacks na tabela TbControleRetornoSlctoFintech |
| **ControleRetornoNotificacaoDAO** | Persiste logs de retorno de notificações na tabela TbControleRetornoNotificacao |
| **PagamentoCallBackDAO** | Consulta dados de validação de origem de pagamento |
| **PagamentoNotificacaoDAO** | Consulta dados para notificação de retorno de pagamento |
| **EnvioNotificacaoJmsProducer** | Produz mensagens para fila de esteira de pagamento retorno |
| **AclFeatureToggleIntegrationService** | Consulta feature toggles para controle de fluxos condicionais |
| **CamelClient** | Cliente HTTP para comunicação com serviços Camel (feature toggle, OAuth) |

---

## 3. Tecnologias Utilizadas

- **Java EE 7** (EJB 3.1, JMS, JAX-RS, JAX-WS, CDI)
- **IBM WebSphere Application Server** (WAS)
- **Maven** (gerenciamento de dependências e build)
- **Spring JDBC** (acesso a dados)
- **Apache HttpClient** (chamadas HTTP)
- **GSON** (serialização/deserialização JSON)
- **JAXB** (binding XML)
- **SLF4J/Logback** (logging)
- **JUnit, Mockito, PowerMock** (testes)
- **Swagger** (documentação de APIs REST)
- **IBM MQ** (filas JMS)
- **Oracle Database** (via JDBC)
- **OAuth 2.0** (autenticação)
- **Joda-Time** (manipulação de datas)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/atacado/pagamentos/enviarCallbackPagamento | PagamentoCallbackNotificacao | Envia callback de validação de pagamento manualmente |
| POST | /v1/atacado/pagamentos/enviarNotificacaoPagamento | PagamentoCallbackNotificacao | Envia notificação de finalização de pagamento manualmente |

---

## 5. Principais Regras de Negócio

1. **Processamento de Callback**: Ao receber protocolo de solicitação, consulta dados na TbValidacaoOrigemPagamento, identifica tipo de liquidação (59/60 para tributos ou 1/21/22/31/32 para boletos) e envia callback para URL do parceiro
2. **Atualização de Status**: Após callback bem-sucedido (HTTP 200), atualiza status do lançamento para 7 (Aguardando processamento); em caso de erro, atualiza para 8 (Rejeitado pela origem)
3. **Controle de Duplicidade**: Verifica se já existe callback processado com sucesso no dia atual para o mesmo protocolo antes de reenviar
4. **Processamento de Notificação**: Ao receber finalização de pagamento, monta notificação com status, datas e código de autenticação, envia para URL do parceiro e posta na fila de esteira de retorno
5. **Geração de Hash de Validação**: Para notificações, gera hash SHA-256 único como chave de validação da mensagem
6. **Roteamento Condicional**: Utiliza feature toggles para determinar URLs de APIs (v1 vs v2, mTLS vs não-mTLS)
7. **Tratamento de Tokens**: Gerencia tokens OAuth com renovação automática em caso de expiração (HTTP 401/403)
8. **Logs de Auditoria**: Registra todas as solicitações e retornos em tabelas de controle (TbRetornoSolicitacaoFintech, TbNotificacaoFintech, TbControleRetornoSlctoFintech, TbControleRetornoNotificacao)
9. **Mascaramento de Dados Sensíveis**: Aplica mascaramento de CPF/CNPJ em logs
10. **Envio para Esteira**: Após notificação, posta mensagem na fila QL.SPAG.ESTEIRA_PAGTO_RETORNO.INT para processamento downstream

---

## 6. Relação entre Entidades

- **ProtocoloSolicitacaoPagamento**: Entidade raiz que representa uma solicitação de pagamento (contém numeroProcotoloSolicitacao, codigoPessoa)
- **PagamentoCallBack**: Contém URLs de callback/retorno, cdLancamento, cdLiquidacao, nuProtocoloSolicitacaoCliente
- **PagamentoNotificacao**: Similar a PagamentoCallBack, mas inclui dados de status e datas para notificação
- **CallBackFintech**: Log de callback enviado (URL, protocolo, mensagem, cdLancamento, cdLiquidacao, timestamps)
- **ControleRetornoCallBack**: Log de retorno do callback (cdRetornoSolicitacaoFintech, cdRetorno HTTP, dsRetorno)
- **NotificacaoFintech**: Log de notificação enviada (cdEventoNotificacao, URL, protocolo, chave de validação, mensagem, cdLancamento, cdLiquidacao)
- **ControleRetornoNotificacao**: Log de retorno da notificação (cdNotificacaoFintech, cdRetorno HTTP, dsRetorno)
- **DicionarioPagamentoCustom**: Dados consolidados de lançamento para envio à esteira (cdLancamento, stLancamento, numeroProtocoloSolicitacaoCliente, codOrigem, cdLiquidacao, cdAutenticacaoBancaria, datas)
- **ClienteWallet**: Dados de cliente wallet (URLs de callback/retorno, usuário de serviço, cdModalidadeConta)

**Relacionamentos**:
- CallBackFintech 1:N ControleRetornoCallBack (um callback pode ter múltiplos retornos)
- NotificacaoFintech 1:N ControleRetornoNotificacao (uma notificação pode ter múltiplos retornos)
- PagamentoCallBack/PagamentoNotificacao são views/queries que juntam TbValidacaoOrigemPagamento + TbLancamento + TbLancamentoPessoa

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbValidacaoOrigemPagamento | tabela | SELECT | Consulta URLs de callback/retorno e dados de parceiros por cdLiquidacao e origem |
| TbLancamento | tabela | SELECT | Consulta dados de lançamento de pagamento (status, datas, autenticação, protocolo cliente) |
| TbLancamentoPessoa | tabela | SELECT | Consulta dados de pessoa remetente (CPF/CNPJ, conta corrente) |
| TbStatusLancamento | tabela | SELECT | Consulta descrição de status de lançamento |
| TbErroProcessamento | tabela | SELECT | Consulta erros de processamento de lançamento |
| TbOrigemPagamentoMultiplaConta | tabela | SELECT | Consulta dados de origem de pagamento para clientes wallet |
| TbContaPagamentoFintech | tabela | SELECT | Consulta dados de conta de pagamento fintech |
| TbRelacaoLiquidacaoGrupo | tabela | SELECT | Consulta relação entre liquidação e grupo |
| TbParametroPagamentoFintech | tabela | SELECT | Consulta parâmetros de pagamento fintech por CPF/CNPJ |
| TbRetornoSolicitacaoFintech | tabela | SELECT | Consulta logs de callbacks anteriores para controle de duplicidade |
| TbControleRetornoSlctoFintech | tabela | SELECT | Consulta logs de retorno de callbacks anteriores |
| TbNotificacaoFintech | tabela | SELECT | Consulta logs de notificações anteriores para controle de duplicidade |
| TbControleRetornoNotificacao | tabela | SELECT | Consulta logs de retorno de notificações anteriores |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbLancamento | tabela | UPDATE | Atualiza status do lançamento (StLancamento) após callback |
| TbRetornoSolicitacaoFintech | tabela | INSERT | Insere log de callback enviado |
| TbControleRetornoSlctoFintech | tabela | INSERT | Insere log de retorno de callback |
| TbNotificacaoFintech | tabela | INSERT | Insere log de notificação enviada |
| TbControleRetornoNotificacao | tabela | INSERT | Insere log de retorno de notificação |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| config-arqt-base.properties | leitura | ConfigArqtrBaseProperties | Configurações de URLs de serviços (API Gateway, OAuth) por ambiente |
| config_toggle.properties | leitura | AclFeatureToggleProperties | URLs do serviço de feature toggle por ambiente |
| errorMessages.properties | leitura | Messages (fjee-base-commons) | Mensagens de erro do sistema |
| roles.properties | leitura | N/A | Lista de roles de segurança da aplicação |

---

## 10. Filas Lidas

- **QL.SPAG.VALIDAR_PAGAMENTO_REQ.INT**: Fila de entrada para processamento de callbacks de validação de pagamento (consumida por PagamentoCallbackProcessadorMDB)
- **QL.SPAG.NOTIFICAR_PAGAMENTO_REQ.INT**: Fila de entrada para processamento de notificações de finalização de pagamento (consumida por PagamentoNotificacaoProcessadorMDB)

---

## 11. Filas Geradas

- **QL.SPAG.SOLICITAR_PAGAMENTO_TRIBUTO_REQ.INT**: Fila de saída para envio de dicionário de pagamento à esteira (produzida via EnvioEsteiraBeanRemote)
- **QL.SPAG.ESTEIRA_PAGTO_RETORNO.INT**: Fila de saída para envio de notificação de retorno de pagamento à esteira (produzida por EnvioNotificacaoJmsProducer)

---

## 12. Integrações Externas

1. **APIs de Parceiros/Fintechs**: Envia callbacks e notificações via HTTP POST para URLs configuradas em TbValidacaoOrigemPagamento (URLs dinâmicas por parceiro)
2. **CA-API Gateway**: Integração com API Gateway do Banco Votorantim para:
   - `/v1/atacado/gestao/pagamento-tributo-consumo/validar` (callback tributos)
   - `/v1/atacado/gestao/pagamento-tributo-consumo/confirmar` (notificação tributos)
   - `/v1/atacado/boleto/confirmar-pagamento` (callback boleto Banco 413)
   - `/v1/atacado/is2b/pagamentos/confirmar` (notificação boleto)
   - `/v2/atacado/is2b/pagamentos/confirmar` (notificação boleto com mTLS)
3. **Serviço de OAuth**: `/auth/oauth/v2/token` e `/auth/oauth/v2/token-jwt` para obtenção de tokens de autenticação
4. **Serviço de Feature Toggle**: APIs do componente `sboot-spag-base-acl-feature-toggle` para consulta de feature flags
5. **Componente java-spag-base-envio-esteira**: EJB remoto para envio de mensagens à esteira de pagamentos
6. **JNDI Variables**: Consulta variáveis de ambiente via JNDI (client_id, client_secret)

---

## 13. Avaliação da Qualidade do Código

**Nota:** 6/10

**Justificativa:**

**Pontos Positivos:**
- Separação clara de responsabilidades em camadas (domain, persistence, business, integration, jms, rs)
- Uso de padrões Java EE (EJB, MDB, JAX-RS)
- Implementação de logs de auditoria completos
- Tratamento de erros com exceções customizadas
- Uso de injeção de dependências (CDI, EJB)
- Mascaramento de dados sensíveis em logs

**Pontos Negativos:**
- **Código duplicado**: Lógica similar em PagamentoIntegrationServices e BoletoNotificacaoIntegrationServices poderia ser consolidada
- **Strings hardcoded**: Muitas strings mágicas (status codes, mensagens) espalhadas pelo código ao invés de constantes centralizadas
- **Tratamento de exceções genérico**: Muitos blocos catch(Exception e) que mascaram erros específicos
- **Falta de validações**: Pouca validação de entrada de dados (nulls, formatos)
- **Acoplamento**: Dependência forte de estruturas de banco específicas e URLs hardcoded
- **Testes**: Arquivos de teste presentes mas não incluídos na análise (marcados como NAO_ENVIAR)
- **Comentários**: Poucos comentários explicativos no código
- **Complexidade ciclomática**: Métodos longos com múltiplos níveis de if/else (ex: processaMensagem em PagamentoNotificacaoBean)
- **Uso de tipos primitivos**: Uso de String para datas ao invés de tipos apropriados (LocalDateTime, Instant)
- **SQL em XML**: Queries SQL em arquivos XML separados dificulta manutenção e refatoração

---

## 14. Observações Relevantes

1. **Ambiente de Execução**: Sistema projetado para IBM WebSphere Application Server (WAS) com dependências específicas dessa plataforma
2. **Versionamento**: Versão atual 0.33.0, com histórico de tags no Git indicando evolução contínua
3. **Multi-ambiente**: Suporte a múltiplos ambientes (DES, QA, UAT, PRD) via arquivos de propriedades
4. **Segurança**: Uso de roles JAAS (spag-integracao, intr-middleware) para controle de acesso
5. **Transações**: Uso de TransactionAttributeType.NOT_SUPPORTED indica que operações são não-transacionais (provavelmente por questões de performance em processamento assíncrono)
6. **Feature Toggles**: Uso extensivo de feature flags para controle de fluxos e rollout gradual de funcionalidades
7. **Banco de Dados**: Uso de SQL Server (sintaxe T-SQL visível nas queries)
8. **Encoding**: Uso consistente de UTF-8 e charset explícito em requisições HTTP
9. **Retry**: Implementação de retry automático em caso de falha de token (401/403)
10. **Mascaramento**: Implementação de utilitário CpfUtils para mascaramento de CPF/CNPJ em logs (compliance LGPD)
11. **Dependências Externas**: Dependência do componente java-spag-base-envio-esteira para envio de mensagens à esteira
12. **Swagger**: Documentação de APIs REST via anotações Swagger (porém configuração básica)