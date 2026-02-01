# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java responsável por processar arquivos de retorno de autorização de débito em conta corrente provenientes do Banco do Brasil. O sistema lê arquivos de retorno (layout posicional), valida os dados, atualiza o status das autorizações de débito em múltiplas bases de dados (Sybase), e publica notificações em filas/tópicos MQ para sistemas integrados. Também realiza atualização de dados bancários (agência/conta) em propostas e contratos quando necessário, além de controlar reenvios automáticos de solicitações de débito em caso de não autorização.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê o arquivo de retorno linha a linha, valida estrutura (header, detail, footer) e popula lista para processamento |
| **ItemProcessor** | Processa cada linha do arquivo, identifica tipo de registro (A/B/F/Z) e converte em objetos VO |
| **ItemWriter** | Grava dados processados no banco, atualiza status de autorizações, publica mensagens em filas MQ e gerencia reenvios |
| **RegistroDebitoAutDAO** | Acesso a dados de registros de autorização de débito (TbRegistroAutorizacaoDebito) |
| **EventoRegistroDebitoAutDAO** | Gerencia eventos de autorização de débito (TbEventoRegistroAutorizacaoDbo) |
| **LogArquivoDebitoAutDAO** | Controla log de arquivos processados (TbArquivoAutorizacaoDebito) |
| **ContratoDebitoDAO** | Atualiza status e dados bancários de contratos (TbContratoDebito) |
| **TbPropostaDao** | Atualiza dados bancários em propostas (TbPropostaFavorecido) |
| **SimpleMessageSenderImpl** | Implementação de envio de mensagens para filas/tópicos MQ |
| **GenericActions** | Utilitário para parsing de linhas do arquivo usando reflection |
| **DataSourceUtils** | Gerenciamento de conexões com múltiplos datasources (SybFin, SybCred) |

---

## 3. Tecnologias Utilizadas

- **Java** (versão não especificada explicitamente)
- **Maven** (gerenciamento de dependências e build)
- **Spring Framework** (IoC, configuração XML)
- **Spring Batch** (framework BV customizado para processamento batch)
- **Sybase ASE** (banco de dados - jConnect JDBC driver)
- **IBM MQ Series** (mensageria - versão 7.x+)
- **JAXB** (marshalling/unmarshalling XML)
- **Log4j** (logging)
- **JUnit** (testes unitários)
- **BV Framework** (framework proprietário Banco Votorantim para batch, MQ, crypto, JDBC)

---

## 4. Principais Endpoints REST

não se aplica

---

## 5. Principais Regras de Negócio

1. **Validação de Arquivo de Retorno**: Arquivo deve conter obrigatoriamente registro tipo A (header com código movimento "2") e Z (trailer)
2. **Atualização de Status de Autorização**: Baseado no código de movimento (1=não autorizado, 2=autorizado), atualiza status na TbEventoRegistroAutorizacaoDbo
3. **Atualização de Dados Bancários**: Se agência ou conta no retorno diferirem dos dados cadastrados, atualiza em TbRegistroAutorizacaoDebito, TbPropostaFavorecido e TbContratoDebito
4. **Reenvio Automático**: Em caso de não autorização (status 4) ou pendência de dados (status 3), reenvia solicitação para fila até limite de 2 tentativas
5. **Limite de Reenvio Excedido**: Após 2 tentativas, marca registro com status 106 (excedido limite de reenvio automático)
6. **Validação de Registro**: Código de registro de débito deve existir na base e ter status de processamento = '2'
7. **Atualização de Contrato**: Se movimento = 1 (cancelamento), marca FlDebitoAtivo = 'N' em TbContratoDebito
8. **Notificação de Status**: Publica status de autorização em tópico MQ para sistemas consumidores (APRO, MultiProdutos)
9. **Controle de Arquivo**: Registra processamento em TbArquivoAutorizacaoDebito com flag de sucesso
10. **Log de Auditoria**: Registra alterações de dados bancários em TbLogContratoDebito e TbLogEventoRegistroAtrzoDbto

---

## 6. Relação entre Entidades

**Principais Entidades e Relacionamentos:**

- **TbRegistroAutorizacaoDebito**: Registro principal de autorização de débito
  - Relaciona-se com **TbEventoRegistroAutorizacaoDbo** (1:N) - histórico de eventos/status
  - Relaciona-se com **TbAutorizacaoDebitoPrpsaCntro** (1:N) - vínculo com propostas/contratos
  
- **TbEventoRegistroAutorizacaoDbo**: Eventos de mudança de status
  - Relaciona-se com **TbStatusAutorizacaoDebito** (N:1) - descrição do status
  - Gera registros em **TbLogEventoRegistroAtrzoDbto** (1:N) - log de auditoria

- **TbAutorizacaoDebitoPrpsaCntro**: Vínculo entre autorização e operação
  - Relaciona-se com **TbSistemaOrigem** (N:1) - sistema originador
  - Pode referenciar NuProposta, NuContrato ou CdSistemaOrigemExterno

- **TbContratoDebito**: Contrato com débito ativo
  - Gera registros em **TbLogContratoDebito** (1:N) - log de alterações

- **TbArquivoAutorizacaoDebito**: Controle de arquivos processados
  - Relaciona-se com **TbContaConvenio** (N:1) - conta convênio do banco

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbRegistroAutorizacaoDebito | tabela | SELECT | Busca dados bancários originais do registro de autorização |
| TbEventoRegistroAutorizacaoDbo | tabela | SELECT | Lista eventos/status de autorização de débito |
| TbStatusAutorizacaoDebito | tabela | SELECT | Valida existência de código de retorno/status |
| TbContaConvenio | tabela | SELECT | Obtém código de conta convênio e número de arquivo retorno |
| TbContratoDebito | tabela | SELECT | Busca contratos vinculados a dados bancários |
| TbProposta | tabela | SELECT | Busca propostas para atualização de dados bancários (via TbPropostaDao) |
| TbPropostaFavorecido | tabela | SELECT | Busca dados bancários de favorecido em propostas |
| TbAutorizacaoDebitoPrpsaCntro | tabela | SELECT | Busca vínculo entre autorização e proposta/contrato |
| TbSistemaOrigem | tabela | SELECT | Obtém nome do sistema originador |
| TbParametroSistema | tabela | SELECT | Obtém data de exercício (não utilizado na versão atual) |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbEventoRegistroAutorizacaoDbo | tabela | UPDATE | Atualiza status de autorização e datas de envio/retorno |
| TbRegistroAutorizacaoDebito | tabela | UPDATE | Atualiza dados bancários (agência/conta) e flag de alteração |
| TbContratoDebito | tabela | UPDATE | Atualiza flag de débito ativo e dados bancários |
| TbPropostaFavorecido | tabela | UPDATE | Atualiza agência e conta corrente de favorecido |
| TbContaConvenio | tabela | UPDATE | Atualiza número de arquivo retorno |
| TbAutorizacaoDebitoPrpsaCntro | tabela | UPDATE | Inativa registros (FlAtivo = 'N') após processamento |
| TbArquivoAutorizacaoDebito | tabela | INSERT/UPDATE | Insere controle de arquivo e atualiza quantidade de registros |
| TbLogEventoRegistroAtrzoDbto | tabela | INSERT | Insere log de eventos de autorização |
| TbLogContratoDebito | tabela | INSERT | Insere log de alterações em contratos |
| TbControleArquivoDebitoAtmto | tabela | INSERT | Insere controle de arquivo processado |
| TbConteudoLinhaArquivo | tabela | INSERT | Insere conteúdo de linhas do arquivo |
| TbLinhaCabecalhoArquivo | tabela | INSERT | Insere dados do header do arquivo |
| TbLInhaDetalheArquivo | tabela | INSERT | Insere dados de linhas de detalhe |
| TbLInhaRodapeArquivo | tabela | INSERT | Insere dados do footer do arquivo |
| TbLogArquivoDebitoTipoInvalido | tabela | INSERT | Registra linhas inválidas do arquivo |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| DBT927*.RET / BBM.TRN.DBT627.* | leitura | ItemReader | Arquivo de retorno de débito automático do Banco do Brasil (layout posicional 150 caracteres) |
| conf.properties | leitura | PropertiesUtil | Configuração de layout do arquivo (mapeamento posicional) |
| queries.properties | leitura | QueryResources | Queries SQL parametrizadas |
| catalogo-filas.xml | leitura | CatalogXmlReader | Catálogo de filas MQ |
| bv-framework-integration-mq-conf.properties | leitura | Framework MQ | Configuração de localização do catálogo de filas |
| job-resources.xml | leitura | Spring | Configuração de datasources e conexões MQ por ambiente |
| log4j.xml | leitura | Log4j | Configuração de logging |
| robo.log | gravação | Log4j (RollingFileAppender) | Log de execução do batch |
| statistics-{executionId}.log | gravação | BvDailyRollingFileAppender | Log de estatísticas de execução |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

| Nome da Fila/Tópico | Tipo | Descrição |
|---------------------|------|-----------|
| TP.VAREJO.STATUS_AUTORIZACAO_DEBITO_CONTA | Tópico | Notificação de status de autorização de débito para sistemas APRO/POPE |
| QL.GDCC.SOLICITACAO_DEBITO_CONTA.INT | Fila | Reenvio de solicitação de autorização de débito em caso de não autorização |
| TP.VAREJO.RETORNO_DEBITO_EM_CONTA | Tópico | Notificação de retorno de débito para sistemas MultiProdutos |

**Mensagens Publicadas:**
- **NotificacaoStatusAutorizacaoDebitoContaMensagem** (XML/JAXB): numeroProposta, statusAutorizacaoDebitoConta, dataUltimaAtualizacao
- **SolicitacaoAutorizacaoDebitoContaMensagem** (XML/JAXB): dados bancários, tipo/identificador de operação, código sistema origem
- **AutenticarDebitoContaResponse** (JSON): dados completos de autenticação para tópico MultiProdutos

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Banco do Brasil | Arquivo | Recebe arquivo de retorno de débito automático via diretório compartilhado |
| IBM MQ Series | Mensageria | Publica notificações em tópicos e filas para sistemas consumidores |
| Sybase ASE (DbGestaoDebitoContaCorrente) | Banco de Dados | Base principal de gestão de débito em conta |
| Sybase ASE (DBCRED) | Banco de Dados | Base de crédito para atualização de propostas |
| Sistema APRO/POPE | Tópico MQ | Consome notificações de status de autorização |
| Sistema MultiProdutos | Tópico MQ | Consome notificações de retorno de débito |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 6/10

**Justificativa:**

**Pontos Positivos:**
- Uso de padrões de projeto (DAO, VO, Strategy)
- Separação de responsabilidades em camadas (Reader, Processor, Writer)
- Configuração externalizada (properties, XML)
- Tratamento de exceções customizado
- Logging estruturado
- Uso de framework batch consolidado

**Pontos Negativos:**
- **Código comentado e debug**: Presença de System.out.println e código comentado em produção (ex: ItemWriter, RegistroDebitoAutDAO)
- **Complexidade excessiva no Writer**: ItemWriter com mais de 1000 linhas, múltiplas responsabilidades (persistência, MQ, lógica de negócio)
- **Falta de tratamento de transação**: Uso de `@Transactional(propagation=Propagation.NOT_SUPPORTED)` pode causar inconsistências
- **Hardcoded values**: Valores mágicos espalhados (ex: "001", "S", "N", códigos de status)
- **Reflection desnecessária**: GenericActions usa reflection para parsing quando poderia usar estratégias mais simples
- **Falta de testes**: Apenas um teste de integração, sem testes unitários
- **Documentação insuficiente**: Javadoc incompleto, comentários em português misturados com código
- **Acoplamento alto**: Dependência direta de múltiplos DAOs no Writer
- **Código duplicado**: Lógica de atualização de dados bancários repetida em múltiplos DAOs
- **Gestão de recursos**: Alguns métodos não garantem fechamento de conexões em todos os cenários de exceção

---

## 14. Observações Relevantes

1. **Ambiente Multi-Tenant**: Sistema configurado para múltiplos ambientes (DES, QA, UAT, PRD) com datasources e filas específicas
2. **Cofre de Senhas**: Em produção, senhas são gerenciadas via "COFRE_DE_SENHAS" (não hardcoded)
3. **Layout Posicional**: Arquivo de retorno usa layout posicional de 150 caracteres, configurado via properties
4. **Controle de Reenvio**: Sistema implementa controle de tentativas de reenvio (máximo 2) para evitar loops infinitos
5. **Auditoria Completa**: Todas as alterações são registradas em tabelas de log para rastreabilidade
6. **Processamento Idempotente**: Valida se registro já foi processado antes de atualizar
7. **Suporte a Múltiplos Bancos**: Estrutura preparada para processar retornos de diferentes bancos (atualmente apenas BB - código 001)
8. **Cálculo de Dígito Verificador**: Implementa algoritmo específico do Banco do Brasil para validação de conta
9. **Integração com Sistemas Legados**: Atualiza tanto base de gestão de débito quanto base de crédito (propostas)
10. **Monitoramento JMX**: Configuração de monitoramento via agente JMX (monitoring.properties)
11. **Processamento Batch**: Usa framework BV customizado baseado em Spring Batch com estratégia de resume configurável
12. **Versionamento**: Sistema versionado (0.4.0) com controle via Git/SCM