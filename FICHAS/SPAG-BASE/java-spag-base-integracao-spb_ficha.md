# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **java-spag-base-integracao-spb** é uma aplicação Java EE que realiza a integração entre o sistema SPAG (Sistema de Pagamentos) e o SPB (Sistema de Pagamentos Brasileiro). O sistema processa movimentações financeiras (transferências, pagamentos, TEDs) enviando-as para o SPB através de mensagens padronizadas (grupos STR e PAG) e recebe retornos de confirmação ou rejeição dessas operações. A aplicação atua como middleware, validando dados, mapeando operações para mensagens SPB específicas e atualizando o status dos lançamentos nos bancos de dados SPAG e SPB.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `IncluirTransferenciaBean` | EJB Stateless que expõe métodos para processar movimentações e retornos do SPB |
| `LancamentoBusinessImpl` | Implementação da lógica de negócio para processamento de lançamentos e integração SPB |
| `LancamentoSpagDAOImpl` | DAO para operações no banco SPAG (consultas e atualizações de lançamentos) |
| `LancamentoSpbDAOImpl` | DAO para operações no banco SPB (inclusão de mensagens STR/PAG, consultas) |
| `IntegracaoSPBController` | Controller REST que expõe endpoints para integração e retorno SPB |
| `RetornoPagamentoJMSProducer` | Produtor JMS que envia mensagens de retorno para fila de pagamentos |
| `Util` | Classe utilitária com métodos de conversão, validação e montagem de DTOs |
| `UtilOperacoesPAG` | Utilitário para montagem de parâmetros de operações do grupo PAG |
| `UtilOperacoesSTR` | Utilitário para montagem de parâmetros de operações do grupo STR |
| `SPBInclusaoPAG` | Stored procedure wrapper para inclusão de mensagens PAG no SPB |
| `SPBInclusaoSTR` | Stored procedure wrapper para inclusão de mensagens STR no SPB |

## 3. Tecnologias Utilizadas

- **Java EE 6/7** (EJB 3.1, JAX-RS, JAX-WS, JMS)
- **IBM WebSphere Application Server** (runtime)
- **Spring JDBC** (acesso a dados)
- **Maven** (gerenciamento de dependências e build)
- **Oracle JDBC** (driver de banco de dados)
- **Microsoft SQL Server** (banco SPB - DBISPB)
- **SLF4J/Log4j2** (logging)
- **Apache Commons Lang3** (utilitários)
- **Swagger** (documentação de APIs REST)
- **JUnit, Mockito, PowerMock** (testes)

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/atacado/pagamentos/integrarSPB/ | IntegracaoSPBController | Recebe um lançamento do SPAG e processa a integração com o SPB |
| POST | /v1/atacado/pagamentos/retornoSPB/ | IntegracaoSPBController | Recebe retorno do SPB (R1) e atualiza status do lançamento no SPAG |

## 5. Principais Regras de Negócio

- Validação de tipo de operação (STR ou CIP) baseada no código de liquidação (31=CIP, 32/57=STR)
- Mapeamento de operações para mensagens SPB específicas (OPPAG001-030, OPSTR003-039) baseado em tipo de conta, finalidade e outros atributos
- Verificação de lançamentos já processados para evitar duplicação
- Reenvio automático de movimentações com status 4 (sucesso) ou 9 (erro) no SPB
- Atualização de status de lançamento no SPAG (Processamento=1, Aguardando SPB=12, Confirmado=3, Erro=99)
- Tratamento especial para contas tipo "IF" (Instituição Financeira), "PG" (Pagamento) e "CO" (Conta Ordem)
- Validação de CPF/CNPJ e ajuste de formato para envio ao SPB
- Tratamento de devoluções e portabilidade de crédito consignado
- Conversão de tipos de conta e ajustes para conformidade com padrões SPB

## 6. Relação entre Entidades

**Principais DTOs:**
- `DicionarioPagamento`: Entidade principal contendo todos os dados de um lançamento/pagamento
- `MovimentacaoDTO`: DTO intermediário para processamento de movimentações SPB
- `RetornoSpbDTO`: DTO para recebimento de retornos do SPB (R1)
- `ParametrosGeraisDTO`: Parâmetros gerais de contexto (holding, instituição, usuário, etc)
- `GenericDTO`: DTO genérico para retorno de stored procedures

**Relacionamentos:**
- `DicionarioPagamento` é convertido para `MovimentacaoDTO` para processamento
- `MovimentacaoDTO` contém `ParametrosGeraisDTO` (composição)
- `GenericDTO` é usado para retornos de consultas e procedures no SPB

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBSPAG..TbLancamento | tabela | SELECT | Consulta lançamentos no SPAG para verificar status e dados |
| DBSPAG..TbLancamentoPessoa | tabela | SELECT | Dados de pessoas (remetente/favorecido) do lançamento |
| DBSPAG..TbLancamentoClienteFintech | tabela | SELECT | Dados de clientes fintech relacionados ao lançamento |
| DBISPB (stored procedures) | procedure | SELECT | Consultas de movimentações e ISPBs no banco SPB |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBSPAG..TbLancamento | tabela | UPDATE | Atualiza status do lançamento, número de controle SPB e código de operação |
| DBISPB (stored procedures) | procedure | INSERT | Inclusão de mensagens STR e PAG no SPB (sp_in_mvsr_movi_032, sp_in_mvpg_movi_084) |
| DBISPB (stored procedures) | procedure | UPDATE | Atualização de status de movimentação (sp_ge_atualiza_status_008) e débito/crédito (sp_up_atualiza_Deb_Cred_030) |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| LancamentoSpagDAOImpl-sql.xml | leitura | LancamentoSpagDAOImpl | Queries SQL para operações no banco SPAG |
| errorMessages.properties | leitura | commons/resources | Mensagens de erro do sistema |
| roles.properties | leitura | commons/resources | Definição de roles de segurança |

## 10. Filas Lidas

não se aplica

## 11. Filas Geradas

| Nome da Fila | Tipo | Classe Responsável | Descrição |
|--------------|------|-------------------|-----------|
| jms/spagRetornoPagamentoTedQueue | JMS Queue | RetornoPagamentoJMSProducer | Fila para envio de retornos de pagamento/TED ao SPAG |

**JNDI:** `jms/spagRetornoPagamentoTed` (ConnectionFactory), `jms/spagRetornoPagamentoTedQueue` (Queue)

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| SPB (Sistema de Pagamentos Brasileiro) | Banco de Dados | Integração via stored procedures SQL Server para envio de mensagens STR/PAG |
| SPAG (Sistema de Pagamentos) | Banco de Dados | Consulta e atualização de lançamentos via Oracle |
| Fila JMS de Retorno | Mensageria | Envio de mensagens XML com retorno de processamento para o SPAG |

## 13. Avaliação da Qualidade do Código

**Nota:** 6/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de camadas (business, persistence, domain, integration)
- Uso adequado de EJBs e injeção de dependências
- Logging estruturado com SLF4J
- Tratamento de exceções customizado (LancamentoException)
- Uso de DTOs para transferência de dados

**Pontos Negativos:**
- Métodos muito extensos com lógica complexa (ex: `montarValidacoesOperacaoCIP`, `montarValidacoesOperacaoSTR`)
- Excesso de condicionais aninhados dificultando manutenibilidade
- Classes utilitárias com métodos estáticos muito grandes (Util, UtilOperacoesPAG, UtilOperacoesSTR)
- Falta de documentação JavaDoc em muitos métodos
- Código comentado em vários lugares
- Strings mágicas e números hardcoded (ex: CNPJs, ISPBs, códigos de operação)
- Lógica de negócio misturada com mapeamento de dados
- Testes unitários insuficientes (marcados como NAO_ENVIAR)

## 14. Observações Relevantes

- O sistema trabalha com dois grupos principais de mensagens SPB: **STR** (Sistema de Transferência de Reservas) e **PAG** (Pagamentos)
- Há tratamento especial para operações de **Neon** (fintech) e **depósitos judiciais**
- O sistema suporta **devoluções** e **portabilidade de crédito consignado**
- Utiliza **stored procedures** do SQL Server para comunicação com o SPB
- Implementa mecanismo de **reenvio automático** para movimentações já processadas
- Possui segurança baseada em **roles** (intr-middleware)
- A aplicação é empacotada como **EAR** (Enterprise Archive) para deploy no WebSphere
- Versão atual: **0.30.0**