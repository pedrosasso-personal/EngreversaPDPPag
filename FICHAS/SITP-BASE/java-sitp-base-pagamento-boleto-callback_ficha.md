# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de processamento de callbacks e notificações para pagamentos de boletos e concessionárias do SITP (Sistema Integrado de Transferências e Pagamentos). O sistema consome mensagens de filas JMS, realiza validações, interage com APIs externas através de um API Gateway, atualiza status de protocolos no banco de dados e envia notificações aos clientes/parceiros. Opera em arquitetura Java EE com EJBs, MDBs (Message-Driven Beans) e integração via REST.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **PagamentoCallbackProcessadorMDB** | MDB que consome mensagens de callback da fila, valida protocolos, chama APIs externas e atualiza status |
| **PagamentoNotificacaoProcessadorMDB** | MDB que consome mensagens de notificação da fila e envia notificações aos clientes |
| **PagamentoBoletoCallBackBean** | Bean de negócio para gerenciar callbacks, consultar validações e atualizar status de protocolos |
| **PagamentoBoletoNotificacaoBean** | Bean de negócio para gerenciar notificações de retorno de pagamentos |
| **CallBackJms** | Serviço para postar mensagens na fila de validação de pagamentos (callback) |
| **NotificacaoJms** | Serviço para postar mensagens na fila de notificação de pagamentos |
| **PagamentoBoletoCallBackService** | Serviço de integração para enviar callbacks via API Gateway |
| **PagamentoBoletoNotificacaoService** | Serviço de integração para enviar notificações via API Gateway |
| **CAApiServiceImpl** | Implementação de cliente HTTP para chamadas ao API Gateway com autenticação OAuth2 |
| **ApacheHttpClient** | Cliente HTTP utilizando Apache HttpClient para requisições com Bearer Token |
| **PagamentoBoletoCallBackDAO** | DAO para consultas e atualizações relacionadas a callbacks de pagamento |
| **PagamentoBoletoNotificacaoDAO** | DAO para consultas relacionadas a notificações de pagamento |
| **MovimentoChamadaDAO** | DAO para registro e controle de movimentações/chamadas de API |

---

## 3. Tecnologias Utilizadas

- **Java EE 6/7** (EJB 3.1, JMS, JAX-WS, JAXB)
- **Maven** (gerenciamento de dependências e build)
- **IBM WebSphere Application Server** (servidor de aplicação)
- **Spring JDBC** (acesso a dados)
- **Microsoft SQL Server** (banco de dados DBITP, DBGLOBAL, DBINTEGRACAOITP)
- **JMS/MQ** (IBM MQ para filas de mensagens)
- **Apache HttpClient** (cliente HTTP)
- **Gson** (serialização/deserialização JSON)
- **SLF4J + Log4j2** (logging)
- **OAuth2** (autenticação via API Gateway)
- **JUnit, PowerMock, Mockito** (testes unitários)

---

## 4. Principais Endpoints REST

Não se aplica. O sistema não expõe endpoints REST próprios, apenas consome APIs externas através do API Gateway.

---

## 5. Principais Regras de Negócio

1. **Validação de Callback**: Ao receber mensagem de callback, verifica se o protocolo já foi processado antes de prosseguir
2. **Controle de Tentativas**: Limita tentativas de reprocessamento (MAX_TRY = 3 para callback, 5 para notificação)
3. **Tempo de Espera**: Aguarda tempo mínimo (TEMPO_WAIT) entre tentativas para evitar sobrecarga
4. **Renovação de Mensagens**: Após tempo determinado (TEMPO_NEW_MESSAGE), considera como nova mensagem e zera contadores
5. **Versionamento de Segurança**: Suporta dois tipos de segurança (v1 e v2) baseado no campo TpSegurancaMensagemCashOut
6. **Autenticação OAuth2**: Obtém token de acesso antes de cada chamada ao API Gateway
7. **Registro de Movimentações**: Registra todas as chamadas de API (envio e retorno) na tabela TbMovimentoChamada
8. **Atualização de Status**: Atualiza status do protocolo na TBL_CAIXA_ENTRADA_SPB após confirmação
9. **Tratamento de Origem 93**: Lógica diferenciada para pagamentos com código de origem 93 (usa CNPJ_CPF_Favorecido ao invés de Remetente)
10. **Reenvio Automático**: Reenvia mensagens para fila em caso de falha, respeitando limites de tentativas

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **ProtocoloSolicitacaoPagamento**: Representa a solicitação de pagamento recebida via MQ
  - Atributos: numeroProcotoloSolicitacao, numeroProtocoloSolicitacaoCliente, codigoStatusProtocoloSolicitacao, mensagemNotificacao

- **PagamentoBoletoCallBack**: Dados de configuração para callback
  - Atributos: dsURLValidacaoSolicitacaoPgmno, dsURLRetornoSolicitacaoPgmno, dsUrlUsuarioAPI, tpSegurancaMensagemCashOut, numeroProtocoloSolicitacaoCliente

- **PagamentoBoletoNotificacaoBuilder**: Dados para notificação de retorno
  - Atributos: clienteEndPoint, numeroProcotoloSolicitacao, codigoStatusProtocoloSolicitacao, statusProtocoloSolicitacao, dataHoraSolicitacao, dataHoraAprovacao, dataHoraEfetivacao, codigoAutenticacao, entidadeLiquidante

- **MovimentoChamadaBuilder**: Registro de movimentação/chamada de API
  - Atributos: cdTipoMovimentoChamada (1=CallBack, 2=Notificacao), nuProtocolo, dsUrlParceiro, dsMensagemEnvio, dsMensagemRetorno, dtMovimento, flAtivo

- **BuscaMovimentoDomain**: Controle de tentativas e tempo de vida
  - Atributos: cdMovimentoChamada, qtdeTentativas, lastInclusao, tempoVida

**Relacionamentos:**
- Um Protocolo pode ter múltiplas Movimentações registradas
- Cada Movimentação está associada a um tipo (CallBack ou Notificação)
- CallBack e Notificação compartilham o mesmo protocolo mas têm URLs de destino diferentes

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TBL_CAIXA_ENTRADA_SPB | Tabela | SELECT | Consulta dados de protocolos de pagamento, incluindo URLs de callback/notificação |
| TBPESSOA (DBGLOBAL) | Tabela | SELECT | Consulta dados de pessoas (clientes) por CPF/CNPJ |
| TbValidacaoOrigemPagamento | Tabela | SELECT | Consulta configurações de validação e URLs de callback/notificação por cliente, origem e liquidação |
| TbMovimentoChamada | Tabela | SELECT | Consulta histórico de movimentações/chamadas de API para controle de tentativas |
| TbIntegracaoItpIda (DBINTEGRACAOITP) | Tabela | SELECT | Verifica se protocolo já foi processado anteriormente |
| TbTipoMovimentoChamada | Tabela | SELECT | Verifica existência de tipos de movimentação (CallBack=1, Notificacao=2) |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TBL_CAIXA_ENTRADA_SPB | Tabela | UPDATE | Atualiza status (Cod_Status) do protocolo após confirmação de callback |
| TbMovimentoChamada | Tabela | INSERT | Insere registro de cada chamada de API (envio e retorno) |
| TbMovimentoChamada | Tabela | UPDATE | Atualiza flag de ativo (flAtivo) e data de alteração para controle de reprocessamento |
| TbIntegracaoItpIda (DBINTEGRACAOITP) | Tabela | INSERT | Insere registro de protocolo processado com status 'W' (waiting) |
| TbTipoMovimentoChamada | Tabela | INSERT | Insere tipos de movimentação (1=CallBack, 2=Notificacao) se não existirem |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| config-sitp-base.properties | Leitura | PagamentoBoletoMDB.getArqBundleProp() | Arquivo de configuração contendo URL do API Gateway |
| errorMessages.properties | Leitura | PagamentoBoletoMDB (via Messages) | Mensagens de erro do sistema |
| roles.properties | Leitura | N/A | Definição de roles de segurança |
| *-sql.xml | Leitura | DAOs (via getArquivoQueries()) | Queries SQL para operações de banco de dados |
| PagamentoBoletoValidacao.xsd | Leitura | JAXB (geração de classes) | Schema XSD para validação de mensagens de pagamento |

---

## 10. Filas Lidas

- **queue/SITPValidarPagamentoQueue** (jms/sitpValidarPagamentoJMS): Fila de entrada para processamento de callbacks de validação de pagamento. Consumida por PagamentoCallbackProcessadorMDB.

- **queue/SITPNotificarPagamentoQueue** (jms/sitpNotificarPagamentoJMS): Fila de entrada para processamento de notificações de retorno de pagamento. Consumida por PagamentoNotificacaoProcessadorMDB.

---

## 11. Filas Geradas

- **queue/SITPValidarPagamentoQueue** (jms/sitpValidarPagamentoJMS): Fila para reenvio de mensagens de callback em caso de falha (reprocessamento). Publicada por CallBackJms.postarMensagemMQ().

- **queue/SITPNotificarPagamentoQueue** (jms/sitpNotificarPagamentoJMS): Fila para reenvio de mensagens de notificação em caso de falha (reprocessamento). Publicada por NotificacaoJms.postarMensagemMQ().

---

## 12. Integrações Externas

| Sistema/Serviço | Descrição |
|-----------------|-----------|
| **API Gateway (OAuth2)** | Autenticação via endpoint `/auth/oauth/v2/token` usando client_id e client_secret para obter access_token |
| **API Gateway - Callback v1** | Endpoint `/v1/atacado/boleto/confirmar-pagamento` para confirmação de pagamento (versão 1) |
| **API Gateway - Callback v2** | Endpoint `/v2/atacado/boleto/confirmar-pagamento` para confirmação de pagamento (versão 2, inclui clienteUserService) |
| **API Gateway - Notificação** | Endpoint `/v1/atacado/boleto/notificar-pagamento` para envio de notificações de retorno aos clientes |
| **Variáveis de Ambiente WAS** | Leitura de client_id e client_secret via JNDI (`cell/clusters/clus-atacado/client_id_sitp`, `cell/persistent/client_id_sitp`, etc.) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades em camadas (domain, persistence, business, integration, jms)
- Uso adequado de padrões Java EE (EJB, MDB, DAO)
- Implementação de controle de tentativas e reprocessamento
- Logging estruturado com SLF4J
- Tratamento de exceções em pontos críticos
- Uso de builders para construção de objetos complexos

**Pontos Negativos:**
- **Código comentado**: Muitos trechos de código comentado espalhados pelo projeto (ex: logs, queries alternativas)
- **Strings hardcoded**: Mensagens de erro e URLs em strings literais ao invés de constantes ou arquivos de configuração
- **Lógica complexa em MDBs**: Métodos muito longos (ex: processMessageParte2, trataErroProcessMesssageComProtocolo) dificultam manutenção
- **Tratamento de exceções genérico**: Uso excessivo de `catch(Exception e)` ao invés de exceções específicas
- **Mistura de responsabilidades**: MDBs fazendo validações de negócio, chamadas de API e persistência
- **Falta de documentação**: Javadoc ausente ou incompleto na maioria das classes
- **Código duplicado**: Lógica similar entre CallBack e Notificação poderia ser abstraída
- **Uso de comparações de string para lógica**: `if("2".equals(...))` para determinar versão de API
- **Supressão de warnings Sonar**: Uso de `//NOSONAR` sem justificativa adequada
- **Testes unitários incompletos**: Arquivos de teste marcados como NAO_ENVIAR sugerem cobertura insuficiente

---

## 14. Observações Relevantes

1. **Arquitetura Multi-módulo Maven**: Projeto organizado em 7 módulos (commons, domain, persistence, integration, business, jms, ear) facilitando manutenção modular

2. **Compatibilidade com IBM WebSphere**: Configurações específicas para WAS (ibm-ejb-jar-bnd.xml, deployment.xml) e uso de bibliotecas compartilhadas

3. **Versionamento de API**: Sistema suporta duas versões de API de callback (v1 e v2) baseado em configuração de segurança do cliente

4. **Tratamento Especial para Origem 93**: Queries SQL com lógica diferenciada (UNION) para pagamentos com código de origem 93, usando CNPJ_CPF_Favorecido ao invés de Remetente

5. **Controle de Concorrência**: Uso de flag `flAtivo` e timestamps para controlar reprocessamento e evitar duplicação

6. **Prioridade de Mensagens**: CallBack usa prioridade baixa (LOW_PRIORITY = 1) nas mensagens JMS

7. **Dependências Legadas**: Uso de frameworks e versões antigas (Spring JDBC sem Spring Boot, Java EE 6/7, Log4j2)

8. **Configuração Híbrida**: Mistura de configuração via JNDI, arquivos properties e variáveis de ambiente do WAS

9. **Banco de Dados SQL Server**: Uso de sintaxe específica do SQL Server (GetDate(), DATEDIFF, etc.)

10. **Segurança**: Uso de anotações @DeclareRoles e @RolesAllowed para controle de acesso, mas roles genéricas ("intr-middleware", "sitp-integracao")