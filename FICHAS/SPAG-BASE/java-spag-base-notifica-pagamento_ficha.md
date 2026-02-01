# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **java-spag-base-notifica-pagamento** é um componente de notificação de pagamentos desenvolvido em Java EE. Seu objetivo principal é processar notificações de pagamentos realizados, atualizar o status de lançamentos no banco de dados, gerenciar arquivos CNAB (Centro Nacional de Automação Bancária) e enviar notificações para sistemas externos através de filas JMS. O sistema atua como intermediário entre o processamento de pagamentos e a notificação de clientes/parceiros, suportando diversos tipos de liquidação (boletos, TED, PIX, etc.) e integrando-se com sistemas legados e fintechs.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `NotificaPagamentoBusinessImpl` | Implementa a lógica de negócio principal para notificação de pagamentos, incluindo atualização de lançamentos, processamento de arquivos CNAB e envio de notificações |
| `NotificaPagamentoDAOImpl` | Gerencia operações de persistência no banco de dados SPAG, incluindo atualizações de lançamentos, detalhes CNAB e consultas |
| `NotificaPagamentoLegadoDAOImpl` | Acessa dados do sistema legado (ITP) para consultas específicas como valor de referência de boletos |
| `EnvioNotificacaoJmsProducer` | Responsável por enviar mensagens para filas JMS de notificação de pagamentos e parceiros |
| `NotificaPagamentoSPAG` | Endpoint REST que expõe a API de notificação de pagamentos |
| `IncluirLancamentoProcedure` | Executa stored procedure para inclusão de novos lançamentos no banco de dados |
| `EndpointInformation` | Entidade que armazena informações de endpoint para notificação de fintechs |
| `MensagemFintech` | DTO para mensagens enviadas a parceiros fintech |
| `NotificacaoPagamento` | Entidade que representa uma notificação de pagamento para a esteira |

---

## 3. Tecnologias Utilizadas

- **Java EE 7** (EJB 3.1, JAX-RS, JMS, CDI)
- **Maven** (gerenciamento de dependências e build)
- **Spring JDBC** (acesso a dados)
- **IBM WebSphere Application Server** (servidor de aplicação)
- **Oracle Database** (banco de dados principal via JDBC)
- **JMS** (Java Message Service para filas)
- **GSON** (serialização/deserialização JSON)
- **Apache Commons Lang3** (utilitários)
- **Log4j2/SLF4J** (logging)
- **JUnit, Mockito, PowerMock** (testes unitários)
- **Swagger** (documentação de APIs REST)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/atacado/pagamentos/notificarPagamentoSPAG/` | `NotificaPagamentoSPAG` | Recebe notificação de pagamento processado e dispara o fluxo de atualização e notificação |

---

## 5. Principais Regras de Negócio

1. **Classificação de Status de Pagamento**: Pagamentos são classificados como agendados (status 10), efetuados (status 3) ou com erro (status 99) baseado em data de agendamento e presença de ocorrências
2. **Tratamento de Boletos de Alto Valor**: Boletos com valor superior à referência SPB (consultada no legado) geram automaticamente um lançamento TED adicional
3. **Notificação Diferenciada por Tipo de Liquidação**: Pagamentos com liquidação tipo 1, 21, 22, 59, 60 ou 31/32 (saída) são notificados via fila de pagamento; liquidações 31/32 (entrada) são notificadas via fila de parceiro
4. **Atualização de Arquivos CNAB**: O sistema atualiza tabelas de arquivo CNAB (pessoa, lote e detalhe) conforme o resultado do processamento
5. **Identificação de Cliente Fintech**: Verifica se favorecido é fintech através de dados específicos (CNPJ, nome, conta) e ajusta a notificação
6. **Geração de Hash para Mensagens**: Mensagens para fintechs recebem hash SHA-256 para controle de integridade
7. **Envio para Esteira**: Lançamentos TED gerados automaticamente são enviados para processamento na esteira

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **DicionarioPagamento**: Entidade central que contém todos os dados do pagamento (remetente, favorecido, valores, datas, códigos)
- **NotificacaoPagamento**: Contém `FinalizarPagamentoRequest` com identificador único da transação
- **NotificacaoFintech**: Contém dados para notificação de parceiros fintech (endpoint, protocolo, hash, mensagem)
- **MensagemFintech**: Detalhes da transação para fintech (valor, protocolo, tipo, dados de remetente/beneficiário, status)
- **EndpointInformation**: Informações de endpoint do cliente (URL, usuário de serviço, status)
- **ArquivoCnabProcessamento**: Estatísticas de processamento CNAB (quantidade de transações, processadas, recusadas)
- **EnvioEsteiraDTO**: DTO para envio de lançamentos à esteira de processamento

**Relacionamentos:**
- DicionarioPagamento → ListaCnabArquivoDetalhe → CnabArquivoDetalheDTO → CnabArquivoLoteDTO → CnabArquivoDTO (hierarquia de arquivo CNAB)
- DicionarioPagamento é transformado em NotificacaoPagamento ou NotificacaoFintech dependendo do tipo de liquidação

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbLancamento | tabela | SELECT | Consulta informações de lançamentos e status |
| TbLancamentoPessoa | tabela | SELECT | Consulta dados de pessoas relacionadas ao lançamento |
| TbValidacaoOrigemPagamento | tabela | SELECT | Busca informações de endpoint para notificação de fintechs |
| TBL_SETUP_TESOURARIA (dbpgf_tes) | tabela | SELECT | Consulta valor de referência para boletos SPB no sistema legado |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbLancamento | tabela | UPDATE | Atualiza status do lançamento (agendado, efetuado, erro) |
| TbArquivoCnabPessoa | tabela | UPDATE | Atualiza código de pessoa no arquivo CNAB |
| TbArquivoCnabLote | tabela | UPDATE | Atualiza descrições de ocorrências no lote CNAB |
| TbArquivoCnabDetalheDocumento | tabela | UPDATE | Atualiza código de ocorrência e número de protocolo no detalhe CNAB |
| TbLancamento | tabela | INSERT | Insere novos lançamentos via stored procedure `PrIncluirLancamento` |

---

## 9. Arquivos Lidos e Gravados

não se aplica

---

## 10. Filas Lidas

não se aplica (o sistema não consome mensagens de filas, apenas produz)

---

## 11. Filas Geradas

| Nome da Fila | JNDI | Descrição |
|--------------|------|-----------|
| Fila de Notificação de Pagamento | `jms/spagBaseNotificacaoPagamentoQueue` | Recebe notificações de pagamentos efetuados para processamento pela esteira (liquidações 1, 21, 22, 59, 60, 31/32-saída) |
| Fila de Notificação de Parceiro | `jms/spagBaseNotificacaoParceiroQueue` | Recebe notificações para parceiros fintech (liquidações 31/32-entrada) |

**Connection Factories:**
- `jms/spagBaseNotificacaoPagamento` (para fila de pagamento)
- `jms/spagBaseNotificacaoParceiro` (para fila de parceiro)

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Esteira de Pagamentos | EJB Remoto | Integração via `EnvioEsteiraBeanRemote` (lookup: `ejb/spag-base/EnvioEsteiraBean`) para envio de lançamentos TED gerados automaticamente |
| Sistema Legado ITP | JDBC | Acesso ao banco de dados legado (`jdbc/sitpBaseDbItpDS`) para consulta de parâmetros como valor de referência de boletos |
| Banco SPAG | JDBC | Banco de dados principal (`jdbc/spagBaseDBSPAGDS`) para operações de lançamentos e CNAB |
| Fintechs/Parceiros | JMS + HTTP | Notificação via fila JMS com informações de endpoint HTTP para callback |

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Separação clara de responsabilidades em camadas (business, persistence, integration, domain, rs)
- Uso adequado de injeção de dependências (CDI)
- Presença de testes unitários
- Logging estruturado
- Uso de DTOs para transferência de dados

**Pontos Negativos:**
- Classe `NotificaPagamentoBusinessImpl` com múltiplas responsabilidades (viola Single Responsibility Principle)
- Método `notificaPagamento` muito extenso e complexo, com lógica condicional aninhada
- Uso de constantes mágicas (números de status, códigos de liquidação) sem enumerações adequadas
- Tratamento de exceções genérico com apenas log, sem estratégia de recuperação
- Comentários em português misturados com código em inglês
- Falta de validação de entrada nos endpoints REST
- Código de mapeamento SQL em arquivos XML separados dificulta manutenção
- Método `trataBoletoVR` com lógica complexa que poderia ser extraída para classe específica
- Uso de `clone()` em `DicionarioPagamento` sem garantia de deep copy
- Falta de documentação JavaDoc nas classes principais

**Recomendações:**
- Refatorar `NotificaPagamentoBusinessImpl` extraindo lógicas específicas para classes dedicadas
- Criar enumerações para status e códigos de liquidação
- Implementar validação de entrada com Bean Validation
- Adicionar tratamento de exceções mais específico
- Padronizar idioma (preferencialmente inglês)
- Adicionar documentação JavaDoc

---

## 14. Observações Relevantes

1. **Arquitetura Multi-módulo Maven**: O projeto está bem estruturado em módulos (commons, domain, persistence, business, integration, jms, rs, ws, ear), facilitando manutenção e reuso
2. **Suporte a Múltiplos Tipos de Liquidação**: O sistema suporta diversos tipos de liquidação (TED, DOC, Boleto, PIX - códigos 1, 21, 22, 31, 32, 59, 60)
3. **Integração com Sistema Legado**: Mantém integração com sistema legado (ITP) para consultas específicas
4. **Processamento CNAB**: Sistema preparado para processar arquivos CNAB com atualização de múltiplas tabelas relacionadas
5. **Segurança**: Configurado com autenticação BASIC e roles (`intr-middleware`, `spag-integracao`)
6. **Deployment IBM WebSphere**: Configurações específicas para WebSphere (ibm-ejb-jar-bnd.xml, ibm-web-bnd.xml, deployment.xml)
7. **Versionamento de API**: Endpoint REST versionado (`/v1/atacado/pagamentos`)
8. **Tratamento Especial para Boletos**: Lógica específica para boletos com valor acima da referência SPB, gerando TED automaticamente
9. **Notificação Assíncrona**: Uso de JMS para desacoplamento entre processamento e notificação
10. **Trilha de Auditoria**: Handlers configurados para captura de trilha de auditoria em requisições (inbound/outbound)