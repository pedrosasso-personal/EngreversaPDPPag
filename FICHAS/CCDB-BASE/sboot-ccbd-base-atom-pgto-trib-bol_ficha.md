# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de pagamento de tributos e contas de consumo (boletos) desenvolvido em Java com Spring Boot. O sistema gerencia o ciclo completo de pagamentos de boletos, incluindo registro, validação, processamento, notificação e estorno de transações. Suporta diferentes formas de pagamento (conta corrente e cartão de crédito) e integra-se com sistemas externos através de filas IBM MQ e Google Cloud Pub/Sub.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **PgtoTribBolController** | Controlador REST que expõe endpoints para operações de pagamento de boletos |
| **PgtoTribBolService** | Serviço principal contendo regras de negócio para processamento de pagamentos |
| **PgtoTribBolRepository** | Interface de acesso a dados utilizando JDBI para operações no banco SQL Server |
| **LancamentoBoleto** | Entidade de domínio representando um lançamento de pagamento de boleto |
| **BoletoAdapter** | Adaptador para conversão entre entidades de domínio e DTOs |
| **LancamentoAdapter** | Adaptador para conversão de lançamentos entre camadas |
| **NotificarPagamentoAdapter** | Adaptador para processamento de notificações de pagamento |
| **ValidarCallBackAdapter** | Adaptador para validação de callbacks de sistemas externos |
| **DatabaseConfiguration** | Configuração de conexão com banco de dados SQL Server |
| **PgtoTribBolConfiguration** | Configuração principal da aplicação incluindo mensageria |

---

## 3. Tecnologias Utilizadas

- **Framework**: Spring Boot 2.x
- **Linguagem**: Java 11
- **Persistência**: JDBI 3.9.1 com SQL Server
- **Mensageria**: IBM MQ 2.7.18, Google Cloud Pub/Sub
- **Documentação**: Swagger/OpenAPI 3.0
- **Segurança**: Spring Security com OAuth2/JWT
- **Build**: Maven 3.5.3
- **Testes**: JUnit 5, Rest Assured, Pact
- **Monitoramento**: Spring Actuator, Micrometer Prometheus
- **Logging**: Logback com formato JSON
- **Utilitários**: Lombok, Jackson, Gson

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/pagamento-boleto/efetivar | PgtoTribBolController | Salvar novo pagamento de boleto |
| GET | /v1/pagamento-boleto/efetivar | PgtoTribBolController | Consultar boleto por linha digitável |
| PUT | /v1/pagamento-boleto/efetivar | PgtoTribBolController | Atualizar status do pagamento |
| PUT | /v1/pagamento-boleto/efetivar/{idBoleto}/estorno | PgtoTribBolController | Estornar pagamento de boleto |
| POST | /v1/pagamento-boleto/efetivar/validar | PgtoTribBolController | Validar callback de pagamento |
| POST | /v1/pagamento-boleto/efetivar/notificar | PgtoTribBolController | Notificar resultado de pagamento |
| GET | /v1/pagamento-boleto/efetivar/validar-duplicata | PgtoTribBolController | Validar duplicata de pagamento |
| POST | /v1/pagamento-boleto/efetivar/notificar-duplicata | PgtoTribBolController | Notificar pagamento duplicado |
| PUT | /v1/pagamento-boleto/lancamento/atualizar | PgtoTribBolController | Atualizar lançamento de boleto |
| PUT | /v1/pagamento-boleto/lancamento/{idLancamento}/desfazer | PgtoTribBolController | Desfazer lançamento (rollback) |
| GET | /v1/pagamento-boleto/lancamento/{protocoloSpag} | PgtoTribBolController | Consultar lançamento por protocolo SPAG |
| POST | /v1/pagamento-boleto/efetivar/notificar/contigencia | PgtoTribBolController | Notificar pagamentos em contingência |

---

## 5. Principais Regras de Negócio

1. **Geração de NSU**: Se não fornecido, o sistema gera automaticamente um NSU (UUID) para cada transação
2. **Validação de Callback**: Implementa delay de 2 segundos para garantir persistência antes da validação
3. **Tratamento de Status**: Diferencia status de erro para pagamentos com cartão de crédito (código 5) e outros erros (código 6)
4. **Controle de Duplicatas**: Valida e trata pagamentos duplicados através de código de liquidação específico (22)
5. **Estorno de Pagamentos**: Permite reverter transações atualizando status e protocolo de devolução
6. **Notificação Assíncrona**: Envia mensagens para filas IBM MQ com propriedade SIGLA baseada na forma de pagamento
7. **Contingência**: Busca e notifica pagamentos pendentes de confirmação por data de processamento
8. **Histórico de Lançamentos**: Mantém histórico antes de excluir lançamentos (tabela TbLancamentoBoletoHist)
9. **Truncamento de Strings**: Limita nome do remetente a 60 caracteres e descrição a 100 caracteres
10. **Transações**: Operações de desfazer lançamento são transacionais com rollback em caso de erro

---

## 6. Relação entre Entidades

**LancamentoBoleto** (entidade principal):
- Contém **StatusBoleto** (relacionamento 1:1) - representa o status atual do pagamento
- Contém **FormaPagamento** (relacionamento 1:1) - define se é conta corrente ou cartão
- Referencia **TbDetalheBoleto** via codigoDetalhe (relacionamento N:1)

**Boleto** (DTO de saída):
- Contém **Beneficiario** remetente (relacionamento 1:1)
- Contém **Beneficiario** favorecido (relacionamento 1:1)

**Relacionamentos de banco**:
- TbLancamentoBoleto → TbDetalheBoleto (N:1)
- TbLancamentoBoleto → TbStatusBoleto (N:1)
- TbLancamentoBoleto → TbFormaPagamento (N:1)
- TbLancamentoBoleto → TbTransacaoBoleto (N:1)
- TbLancamentoBoleto → TbLancamentoBoletoHist (1:N) - histórico

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbLancamentoBoleto | tabela | SELECT | Consulta lançamentos de pagamento de boletos |
| TbDetalheBoleto | tabela | SELECT | Consulta detalhes do boleto (código de barras, linha digitável) |
| TbStatusBoleto | tabela | SELECT | Consulta descrição dos status de pagamento |
| TbFormaPagamento | tabela | SELECT | Consulta formas de pagamento disponíveis |
| TbTransacaoBoleto | tabela | SELECT | Consulta informações de transação do boleto |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbLancamentoBoleto | tabela | INSERT | Insere novos lançamentos de pagamento |
| TbLancamentoBoleto | tabela | UPDATE | Atualiza status, protocolos e dados do lançamento |
| TbLancamentoBoleto | tabela | DELETE | Exclui lançamentos (após inserir no histórico) |
| TbLancamentoBoletoHist | tabela | INSERT | Insere histórico de lançamentos antes da exclusão |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot | Configurações da aplicação por ambiente |
| logback-spring.xml | leitura | Logback | Configuração de logs em formato JSON |
| *.sql | leitura | PgtoTribBolRepository | Queries SQL para operações de banco |
| sboot-ccdb-base-atom-pgto-trib-bol.yaml | leitura | Swagger Codegen | Especificação OpenAPI para geração de código |

---

## 10. Filas Lidas

Não se aplica - o sistema não consome mensagens de filas, apenas publica.

---

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Descrição |
|--------------|-----------|-----------|
| TP.BANCO_DIGITAL.CCBD.PAGAMENTO_CONTAS | IBM MQ | Publica eventos de pagamento processados com propriedade SIGLA (CCBD ou CART) |
| business-ppbd-pgto-contingencia-notificacao | Google Cloud Pub/Sub | Publica notificações de pagamentos em contingência |

---

## 12. Integrações Externas

1. **IBM MQ**: Publicação de eventos de pagamento para sistemas downstream através do tópico TP.BANCO_DIGITAL.CCBD.PAGAMENTO_CONTAS
2. **Google Cloud Pub/Sub**: Publicação de notificações de contingência no tópico business-ppbd-pgto-contingencia-notificacao
3. **SQL Server (DBCCBD)**: Banco de dados principal para persistência de lançamentos e consultas
4. **Sistema SPAG**: Integração via protocolo para processamento de pagamentos
5. **Serviço de Autenticação OAuth2/JWT**: Validação de tokens através de jwks.json

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades em camadas (presentation, service, infrastructure, domain)
- Uso adequado de padrões como Adapter e Repository
- Documentação via Swagger bem estruturada
- Tratamento de exceções customizadas
- Uso de Lombok reduzindo boilerplate
- Testes unitários, integração e funcionais separados
- Configuração por ambiente bem organizada
- Uso de JDBI com SQL externalizado facilita manutenção

**Pontos de Melhoria:**
- Algumas classes de serviço muito extensas (PgtoTribBolService com múltiplas responsabilidades)
- Uso de delay fixo (Thread.sleep implícito) para sincronização é uma prática inadequada
- Falta de constantes para valores mágicos (ex: "22" para código de liquidação duplicata)
- Logs em português misturados com código em inglês
- Alguns métodos privados poderiam ser extraídos para classes utilitárias
- Falta de validação de entrada em alguns endpoints
- Comentários em português no código Java

---

## 14. Observações Relevantes

1. **Ambientes**: Sistema configurado para 4 ambientes (local, des, qa, uat, prd)
2. **Segurança**: Implementa autenticação via OAuth2/JWT com endpoints públicos configuráveis
3. **Monitoramento**: Expõe métricas Prometheus na porta 9090
4. **Auditoria**: Integrado com framework de trilha de auditoria do Banco Votorantim
5. **Arquitetura**: Segue modelo atômico de microserviços com módulos separados (common, domain, application)
6. **Versionamento**: API versionada (v1) permitindo evolução controlada
7. **Contingência**: Possui mecanismo de notificação de pagamentos pendentes para recuperação de falhas
8. **Transacional**: Operações críticas como desfazer lançamento são transacionais
9. **Performance**: Configurado com lazy initialization e recursos otimizados (80m CPU, 448Mi RAM)
10. **Kubernetes**: Pronto para deploy em Kubernetes com probes de liveness e readiness configurados