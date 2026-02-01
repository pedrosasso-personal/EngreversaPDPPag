# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java responsável por consultar saldo de fornecedores (especificamente IS2B) e liberar pagamentos de tributos. O sistema busca lotes de pagamento pendentes, valida disponibilidade de limite através de API externa, e envia mensagens para fila MQ para processamento dos pagamentos aprovados. Em caso de rejeição, envia notificações por e-mail com detalhes dos pagamentos afetados.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê lotes de pagamento pendentes do banco de dados para processamento |
| **ItemProcessor** | Processa os itens (implementação simples, apenas repassa o objeto) |
| **ItemWriter** | Consulta API de saldo e envia mensagens para fila MQ |
| **ConsultaSaldoFornecedor** | Orquestra a lógica de negócio: consulta API, busca detalhes do lote, envia para fila MQ e notifica por e-mail |
| **ConsultaSaldoFornecedorDAO** | Acesso a dados das tabelas TbLotePagamentoTributo e TbDetalheFornecedorLote |
| **ConsultaSaldoFornecedorService** | Integração com API Gateway para consulta de saldo |
| **CAApiServiceImpl** | Gerencia autenticação OAuth2 e chamadas HTTP para APIs externas |
| **MqWriter** | Publica mensagens XML na fila IBM MQ |
| **EmailHelper** | Envia notificações por e-mail com anexos |
| **MyResumeStrategy** | Estratégia de tratamento de erros do batch |

## 3. Tecnologias Utilizadas

- **Framework Batch**: BV Framework Batch (framework proprietário baseado em Spring Batch)
- **Build**: Maven
- **Banco de Dados**: Microsoft SQL Server (DBSPAG)
- **Mensageria**: IBM MQ 7.0.1.10
- **Integração**: API Gateway com autenticação OAuth2
- **Serialização**: JAXB (XML), Gson (JSON)
- **Transações**: Bitronix Transaction Manager (JTA)
- **Logging**: Log4j
- **E-mail**: JavaMail API com Spring Mail
- **Testes**: JUnit
- **Bibliotecas**: Apache Commons Lang3, Apache HttpComponents

## 4. Principais Endpoints REST

não se aplica (o sistema consome APIs externas mas não expõe endpoints REST próprios)

**APIs Consumidas:**
- `POST {api_gateway_address}/auth/oauth/v2/token` - Obtenção de token OAuth2
- `POST {api_gateway_address}/v1/parceiros/is2b/pagamentos/limites` - Consulta de saldo/limite do fornecedor

## 5. Principais Regras de Negócio

1. **Seleção de Lotes**: Processa apenas lotes do fornecedor IS2B (código 1) com status 0 ou 100, criados no dia corrente
2. **Consulta de Saldo**: Valida disponibilidade de limite antes de liberar pagamentos (implementação comentada no código)
3. **Atualização de Status**: Atualiza status do lote para 1 (Em processamento) após envio bem-sucedido para fila
4. **Filtro de Detalhes**: Envia para fila apenas registros com status diferente de 10 (Enviado ao lote) e 99
5. **Modo Bypass**: Permite reprocessamento de lote específico através do parâmetro `codigoLote`
6. **Notificação de Rejeição**: Envia e-mail com detalhes dos pagamentos quando TED é rejeitada
7. **Controle de Tentativas**: Configurado para até 15 tentativas (parâmetro qtdeTentativas)
8. **Delay entre Mensagens**: Código comentado sugere espera de 15 segundos entre mensagens (atualmente desabilitado)

## 6. Relação entre Entidades

**CapaLoteVO** (Cabeçalho do Lote)
- Representa um lote de pagamentos de tributos
- Atributos: código do lote, fornecedor, valor total, dados bancários, status, datas

**RegistroLoteVO** (Detalhe do Lote)
- Representa um pagamento individual dentro do lote
- Relacionamento: N registros para 1 CapaLoteVO
- Atributos: código do detalhe, código do lançamento, protocolo, valor, status

**MqRequest** (Mensagem MQ)
- Representa a mensagem enviada para fila de liberação de pagamento
- Atributos: número do protocolo, flag de retorno de liberação

**ConsultaSaldoRequest/Response**
- Request: código do banco
- Response: limites (crédito, consumido, disponível, antecipado), status da transação, códigos de erro

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbLotePagamentoTributo | tabela | SELECT | Busca lotes de pagamento pendentes por fornecedor e data |
| TbDetalheFornecedorLote | tabela | SELECT | Busca detalhes (pagamentos individuais) de um lote específico |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbLotePagamentoTributo | tabela | UPDATE | Atualiza status do lote e data de alteração |
| TbDetalheFornecedorLote | tabela | UPDATE | Atualiza status do detalhe do pagamento (código comentado) |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| log/roboConsultaSaldoFornecedor.log | gravação | Log4j (workflow logger) | Log de execução do batch |
| log/statistics-{executionId}.log | gravação | BvDailyRollingFileAppender | Log de estatísticas do framework BV |
| detalhes.txt | gravação (anexo e-mail) | ConsultaSaldoFornecedor.montarAnexo() | Anexo de e-mail com detalhes dos pagamentos rejeitados |

## 10. Filas Lidas

não se aplica

## 11. Filas Geradas

| Nome da Fila | Tipo | Breve Descrição |
|--------------|------|-----------------|
| QL.SPAG.LIBERAR_PAGAMENTO_TRIBUTO_REQ.INT | IBM MQ | Fila para liberação de pagamentos de tributos. Recebe mensagens XML com protocolo de transação e flag de retorno |

**Detalhes da Conexão MQ:**
- Queue Manager: QM.ATA.01
- Host: qm_ata_des.bvnet.bv
- Canal: SPAG.SRVCONN
- Porta: 1414
- Usuário: _spag_des

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Breve Descrição |
|-----------------|------|-----------------|
| API Gateway BV | REST API | Autenticação OAuth2 e consulta de limites de pagamento para fornecedor IS2B |
| IBM MQ | Mensageria | Envio de mensagens para liberação de pagamentos |
| SMTP Server | E-mail | Envio de notificações de rejeição (smtpduqrelay.bvnet.bv) |
| SQL Server DBSPAG | Banco de Dados | Consulta e atualização de lotes e detalhes de pagamento |

## 13. Avaliação da Qualidade do Código

**Nota:** 5/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades (DAO, Service, Business)
- Uso de padrões de projeto (Strategy para tratamento de erros)
- Configuração externalizada via Spring XML
- Tratamento de recursos (close de conexões e statements)

**Pontos Negativos:**
- **Código comentado em excesso**: Várias funcionalidades críticas estão comentadas (consulta de saldo, atualização de status, delay entre mensagens)
- **Lógica de negócio incompleta**: O método `consultarAPI()` apenas retorna `true` sem implementação real
- **Hardcoded values**: Credenciais e configurações sensíveis no XML
- **Falta de tratamento de exceções**: Muitos métodos apenas propagam exceções sem tratamento adequado
- **Código de teste**: Código comentado e valores de teste misturados com código de produção
- **Documentação**: Comentários em português com caracteres mal codificados, falta de JavaDoc
- **Manutenibilidade**: Queries SQL como strings concatenadas dificultam manutenção
- **Segurança**: Senhas em texto claro nos arquivos de configuração (mesmo com criptografia BVCrypto)

## 14. Observações Relevantes

1. **Estado do Código**: O sistema parece estar em desenvolvimento ou transição, com várias funcionalidades comentadas que sugerem implementação incompleta

2. **Ambiente**: Configurado para ambiente de desenvolvimento (DES), com conexões apontando para servidores de desenvolvimento

3. **Fornecedor Específico**: Sistema focado exclusivamente no fornecedor IS2B (código 1), não sendo genérico para outros fornecedores

4. **Modo Bypass**: Permite reprocessamento manual através dos parâmetros `codigoLote` e `tipoExecucao`

5. **Parâmetros de Execução**:
   - `codigoFornecedor`: Obrigatório (1 para IS2B)
   - `codigoLote`: Opcional (0 para processamento normal, ID específico para bypass)
   - `tipoExecucao`: Flag para controle de fluxo

6. **Códigos de Saída**:
   - 11: Parâmetros obrigatórios não informados
   - 12: Erro ao obter datasource
   - 13: Erro durante processamento
   - 14: Erro inesperado
   - 15: Erro retorno API

7. **Destinatários de E-mail**: TEC-Cash-Management@bv.com.br

8. **Namespace XML MQ**: `http://mensagem.bvnet.bv/atacado/pagamentos/liberaPagamentoTributo/v1`