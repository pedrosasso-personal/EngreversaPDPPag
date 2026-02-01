# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de gestão e autorização de débito em conta corrente (GDCC) que processa solicitações de débito, valida autorizações conforme modelo de negócio definido e gerencia o ciclo de vida das autorizações. O sistema opera através de filas JMS para receber solicitações e publicar notificações de status, além de expor serviços SOAP (v1 e v2) e REST para consultas e operações. Suporta três modelos de autorização: sem autorização (automático), única vez (com expiração temporal) e por proposta (autorização individual para cada operação).

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `ValidaSolicitacoesDebitoContaImpl` | Orquestra validação de solicitações de débito, determina modelo de autorização e publica status em tópicos JMS |
| `ValidaSolicitacoesDebitoContaMDB` | Message-Driven Bean que consome fila de solicitações, converte XML para entidade e dispara validação |
| `AutorizacaoDebitoBeanImpl` | Lógica principal de gerenciamento de autorizações: validação, inserção, consulta e controle de expiração |
| `RegraAutorizacaoDebitoBeanImpl` | Regras de negócio para inserção de registros, controle de flag flMesmaConta e desativação de autorizações divergentes |
| `AutorizacaoDebitoDAOImpl` | DAO principal para acesso às tabelas de autorização, eventos, parâmetros e consultas em DbCred/DbCor |
| `EventoRegistroAutorizacaoDebitoDAOImpl` | DAO específico para manipulação de eventos de autorização |
| `AutorizacaoDebitoPrpsaCntroDAOImpl` | DAO para relacionamento autorização-proposta-contrato |
| `RegraAutorizacaoDebitoDAOImpl` | DAO para inserção de registros e logs de histórico |
| `ObterSequencialDisponivelStoreProcedureDAOImpl` | Executa stored procedure Sybase para obtenção de sequenciais |
| `FilaMQ` | Utilitário para envio de mensagens JMS aos tópicos de notificação |
| `ConverterUtil` | Conversão XML/JAXB de mensagens JMS (BytesMessage/TextMessage) |
| `DebitoContaEndPoint` | Endpoint SOAP v1 com 3 operações (solicitar, listar, obter histórico) |
| `DebitoContaEndPointV2` | Endpoint SOAP v2 com 2 operações (listar e histórico com filtros por proposta/contrato) |

---

## 3. Tecnologias Utilizadas

- **Java EE**: EJB 3.x (@Stateless, @MessageDriven, @Local)
- **JMS**: Message-Driven Beans, Topics e Queues
- **JAX-WS 2.1**: Serviços SOAP
- **JAX-RS**: API REST
- **JAXB**: Marshalling/Unmarshalling XML
- **Sybase**: Banco de dados principal (jdbc/GDCCSybaseDS)
- **WebSphere Application Server**: Container de aplicação (ibm-web-bnd/ext.xml)
- **Stored Procedures**: prObterSequencialDisponivel (Sybase)
- **Bootstrap CSS/JS**: Frontend (módulo REST)
- **Handlers SOAP**: BvFaultHandler, CapturadorTrilhaInbound, InicializadorContextoRequisicao
- **Segurança**: BASIC Authentication, roles (gdcc-integracao, intr-middleware)
- **Integração**: WasAliasMapper para credenciais MQ (aproBaseMQAuth, gdccBaseMQAuth)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| N/A | `/gdcc-base-webservice-debito-conta-rs/api` | N/A | Context-root base configurado via ibm-web-ext.xml. Endpoints específicos não definidos nos arquivos analisados (somente recursos estáticos CSS/JS) |

**Observação**: O módulo REST possui configuração de filtros (InicializadorContextoRequisicao, CapturadorTrilhaInbound) mas não foram identificadas classes de recursos JAX-RS nos arquivos fornecidos.

---

## 5. Principais Regras de Negócio

1. **Modelo SEM_AUTORIZACAO (código 1)**: Autoriza automaticamente qualquer solicitação, inserindo evento DEBITO_AUTORIZADO sem validações adicionais.

2. **Modelo UNICA_VEZ (código 2)**: Valida expiração temporal (QtDiaExpiracao). Se autorização expirada ou modelo diferente do cadastrado, solicita nova autorização com status DEBITO_PENDENTE_AUTORIZACAO_CLIENTE.

3. **Modelo POR_PROPOSTA (código 3)**: Exige autorização individual para cada proposta/contrato. Cada operação requer validação específica.

4. **Reenvio de Solicitação**: Status DEBITO_NAO_AUTORIZADO_CLIENTE permite reenvio de solicitação de autorização.

5. **Validação de Conta (flMesmaConta)**: Garante que proposta/contrato estejam vinculados à mesma conta bancária. Se divergente, desativa autorizações anteriores.

6. **Sistema Origem**: GDCF é o sistema padrão (código 1). Suporta múltiplos sistemas via TbSistemaOrigem. Workaround para "acom-base-simulacao" -> "GDCF".

7. **Identificadores**: Suporta três tipos de pesquisa: por proposta, por contrato ou por identificador externo do sistema origem.

8. **Histórico de Alterações**: Registra logs de mudança de status em TbLogEventoRegistroAtrzoDbto para auditoria.

9. **Limite de Consulta**: Máximo de 20 autorizações retornadas por requisição SOAP.

10. **Tratamento de Dígitos**: Dígito de agência e conta são opcionais (default "").

11. **Transações**: Inserção de regras usa REQUIRES_NEW para garantir commit independente.

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **RegistroAutorizacaoDebito**: Registro central de autorização contendo modelo, status, dados bancários e sistema origem.
  - Relacionamento 1:N com **EventoRegistroAutorizacaoDebito** (histórico de eventos/status)
  - Relacionamento 1:N com **AutorizacaoDebitoPrpsaCntro** (vínculo com propostas/contratos)
  - Relacionamento N:1 com **ModeloAutorizacaoDebito** (define comportamento: SEM_AUTORIZACAO, UNICA_VEZ, POR_PROPOSTA)
  - Relacionamento N:1 com **SistemaOrigemAutorizacaoDebito** (origem da solicitação)

- **EventoRegistroAutorizacaoDebito**: Eventos de mudança de status da autorização.
  - Relacionamento N:1 com **StatusAutorizacaoDebitoEnum** (5 status possíveis)

- **AutorizacaoDebitoPrpsaCntro**: Tabela associativa que vincula autorização a proposta/contrato.
  - Relacionamento N:1 com **TbProposta** (DbCred)
  - Relacionamento N:1 com **TbContratoPrincipal** (DbCor)
  - Atributo flMesmaConta para validação de conta

- **ContaAutorizacaoDebito**: Dados bancários (CPF, banco, agência, conta, dígitos)

- **DadosBancarios**: Estrutura canônica SOAP com dados da conta

**Enumerações:**
- **ModeloAutorizacaoDebitoEnum**: SEM_AUTORIZACAO=1, UNICA_VEZ=2, POR_PROPOSTA=3
- **StatusAutorizacaoDebitoEnum**: 5 status (DEBITO_AUTORIZADO, DEBITO_NAO_AUTORIZADO_CLIENTE, DEBITO_PENDENTE_AUTORIZACAO_CLIENTE, etc)
- **StatusProcessamentoAutorizacaoDebitoEnum**: Status de processamento interno
- **TipoPesquisaEnum**: PROPOSTA, CONTRATO, IDENTIFICADOR

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbRegistroAutorizacaoDebito | Tabela | SELECT | Registro principal de autorização de débito |
| TbEventoRegistroAutorizacaoDbo | Tabela | SELECT | Eventos de mudança de status da autorização |
| TbParametroAutorizacaoDebito | Tabela | SELECT | Parâmetros de configuração do modelo por banco |
| TbStatusAutorizacaoDebito | Tabela | SELECT | Domínio de status de autorização |
| TbSistemaOrigem | Tabela | SELECT | Cadastro de sistemas origem das solicitações |
| TbAutorizacaoDebitoPrpsaCntro | Tabela | SELECT | Relacionamento autorização-proposta-contrato |
| TbLogEventoRegistroAtrzoDbto | Tabela | SELECT | Histórico de logs de alteração de status |
| DbCred.TbProposta | Tabela | SELECT | Dados de propostas de crédito |
| DbCred.TbPropostaFavorecido | Tabela | SELECT | Favorecidos das propostas |
| DbCred.TbPropostaFinanceiro | Tabela | SELECT | Dados financeiros das propostas |
| DbCor.TbContratoPrincipal | Tabela | SELECT | Contratos principais |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbRegistroAutorizacaoDebito | Tabela | INSERT/UPDATE | Inserção de novos registros e atualização de modelo/status |
| TbEventoRegistroAutorizacaoDbo | Tabela | INSERT/UPDATE | Inserção e atualização de eventos de status |
| TbAutorizacaoDebitoPrpsaCntro | Tabela | INSERT/UPDATE | Inserção de vínculos e desativação (flAtivo=false) de registros divergentes |
| TbLogEventoRegistroAtrzoDbto | Tabela | INSERT | Inserção de logs de histórico de alterações para auditoria |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| *-sql.xml | Leitura | AutorizacaoDebitoDAOImpl | Arquivo de queries SQL externalizadas |
| DebitoContaBackendServiceContract.wsdl | Leitura | DebitoContaEndPoint (v1) | Contrato SOAP v1 |
| DebitoContaBackendService_v2.wsdl | Leitura | DebitoContaEndPointV2 | Contrato SOAP v2 |
| Comum.xsd | Leitura | JAXB Binding | Schema de estruturas comuns (Fault, AuditoriaInfo, Paginacao) |
| jaxws.bindings.xml | Leitura | JAX-WS | Configuração de handlers SOAP |

---

## 10. Filas Lidas

| Nome da Fila | Tipo | Binding/Destino | Breve Descrição |
|--------------|------|-----------------|-----------------|
| queue/GDCCSolicitacaoDebitoContaQueue | Queue | as/GDCCSolicitacaoDebitoContaAS | Fila de entrada para solicitações de autorização de débito em conta. Consumida por ValidaSolicitacoesDebitoContaMDB |

---

## 11. Filas Geradas

| Nome da Fila | Tipo | Credencial MQ | Breve Descrição |
|--------------|------|---------------|-----------------|
| topic/APROStatusAutorizacaoDebitoContaVarejoTP | Topic | aproBaseMQAuth | Tópico de notificações de status de autorização para sistemas de varejo |
| topic/GDCCRetornoDebitoEmContaTP | Topic | gdccBaseMQAuth | Tópico de retorno de débito em conta para múltiplos produtos |

**Observação**: Credenciais MQ obtidas via WasAliasMapper.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| WasAliasMapper | Utilitário | Mapeamento de credenciais MQ (aproBaseMQAuth, gdccBaseMQAuth) |
| DbCred (Crédito) | Banco de Dados | Consulta dados de propostas (TbProposta, TbPropostaFavorecido, TbPropostaFinanceiro) |
| DbCor (Contratos) | Banco de Dados | Consulta contratos principais (TbContratoPrincipal) |
| Stored Procedure prObterSequencialDisponivel | Sybase | Obtenção de sequenciais para chaves primárias |
| Sistemas Origem (via TbSistemaOrigem) | Integração | Múltiplos sistemas podem solicitar autorização (GDCF padrão, ACOM com workaround) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com uso adequado de EJBs (Stateless, MDB) e DAOs
- Uso de transações declarativas (@TransactionAttribute) e controle fino (REQUIRES_NEW para regras críticas)
- Externalização de queries SQL em arquivos XML
- Versionamento de serviços SOAP (v1 e v2) demonstra evolução controlada
- Tratamento de diferentes modelos de autorização de forma extensível (enum)
- Logs de auditoria e histórico bem estruturados
- Handlers SOAP para trilha de auditoria e tratamento de falhas

**Pontos de Melhoria:**
- Workaround hardcoded para sistema "acom-base-simulacao" -> "GDCF" indica dívida técnica
- Referência a incidente específico (2317257) em comentários sugere correções pontuais não documentadas adequadamente
- Falta de testes unitários evidentes nos arquivos analisados
- Conversões manuais entre entidades e DTOs SOAP poderiam usar frameworks de mapeamento (MapStruct, ModelMapper)
- Uso de roles de segurança (@RunAs, @RolesAllowed) mas sem documentação clara de matriz de permissões
- Limite fixo de 20 registros em consultas sem paginação configurável
- Módulo REST com configuração mas sem implementação de recursos identificada

O código demonstra maturidade arquitetural e boas práticas de Java EE, mas apresenta alguns débitos técnicos e oportunidades de modernização (ex: migração para Spring Boot, uso de JPA Criteria API ao invés de SQL nativo, containerização).

---

## 14. Observações Relevantes

1. **Segurança**: Sistema utiliza autenticação BASIC com roles específicas (gdcc-integracao, intr-middleware). Handlers SOAP capturam trilha de auditoria (ticket, siglaSistema, loginUsuario, enderecoIP).

2. **Versionamento de API**: Serviço SOAP possui duas versões:
   - **v1**: 3 operações (solicitar, listar, obter histórico)
   - **v2**: 2 operações (listar e histórico com filtros adicionais por proposta/contrato), removendo operação de solicitação

3. **Modelo de Dados**: Sistema suporta três modelos de autorização com comportamentos distintos, permitindo flexibilidade para diferentes produtos/canais.

4. **Rastreabilidade**: Histórico completo de alterações mantido em TbLogEventoRegistroAtrzoDbto, unindo eventos atuais com logs históricos.

5. **Integração Multi-Sistema**: Suporte a múltiplos sistemas origem via TbSistemaOrigem, com GDCF como padrão.

6. **Tratamento de Expiração**: Modelo UNICA_VEZ implementa controle temporal via QtDiaExpiracao, solicitando reautorização quando necessário.

7. **Validação de Integridade**: Flag flMesmaConta garante consistência entre autorizações e contas bancárias, desativando registros divergentes automaticamente.

8. **Desempenho**: Uso de transações REQUIRES_NEW para operações críticas evita locks prolongados. Consultas limitadas a 20 registros para evitar sobrecarga.

9. **Módulo REST**: Configurado mas sem recursos JAX-RS identificados nos arquivos analisados. Possui apenas recursos estáticos (Bootstrap CSS/JS) e filtros de auditoria.

10. **Dependências de Infraestrutura**: Sistema fortemente acoplado ao WebSphere (ibm-web-bnd/ext.xml) e Sybase (stored procedures), dificultando portabilidade.