# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-spag-base-orch-pagamento-cnab** é um orquestrador de pagamentos via arquivo CNAB (Centro Nacional de Automação Bancária) que gerencia o ciclo completo de processamento de remessas bancárias. O sistema recebe arquivos CNAB, valida layouts, traduz registros para pagamentos individuais (boletos, transferências TED/DOC/PIX), envia para execução via microserviços especializados, gerencia agendamentos e processa retornos de confirmação. Utiliza processamento assíncrono via RabbitMQ e GCP Pub/Sub, com controle de retentativas e feature toggles para habilitar funcionalidades como agendamento com/sem saldo.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **CnabController** | Endpoints REST para validação CNAB, configuração pessoa, cancelamento agendamento, consultas |
| **PagamentoCnabController** | Endpoints REST para cancelar/consultar agendamentos |
| **PagamentoCnabService** | Orquestração processamento arquivo CNAB (validação, tradução, envio, rejeição) |
| **ValidacaoArquivoCnabService** | Validação layout arquivo CNAB contra regras configuradas |
| **AgendamentoCcbdService** | Integração com serviços de agendamento CCBD (criar, cancelar, consultar) |
| **PagamentoConfirmacaoService** | Processamento confirmações NSU (confirmado/rejeitado) |
| **PagamentoRetornoService** | Atualização retornos pagamento (sucesso/erro) após execução |
| **FeatureToggleService** | Consulta ConfigCat para habilitar agendamentos CNAB |
| **ProcessamentoCnabRouter** | Fluxo Apache Camel principal: tradução → validação → envio → atualização |
| **PagamentoCnabEnvioRouter** | Roteamento Camel para envio pagamentos (boleto/transferência/agendamento) |
| **PagamentoCnabRetornoRouter** | Roteamento Camel para processar retornos CNAB |
| **FilaRabbitListener** | Consumidores RabbitMQ para processamento CNAB e confirmações |
| **RetornoPagamentoCnabListener** | Consumer GCP Pub/Sub para confirmações pagamento |
| **AgendamentoCcbdRepositoryImpl** | Integração REST com serviços agendamento CCBD |
| **PagamentoBoletoRepositoryImpl** | Envio boletos via API pagamento-boleto |
| **TransferenciaRepositoryImpl** | Envio transferências via API transferências |
| **PagamentoCnabRepositoryImpl** | CRUD detalhes arquivo CNAB, tipos transferência |
| **ValidacaoArquivoCnabRepositoryImpl** | Validação layout CNAB via API atom-pagamento-cnab |
| **AtualizarCnabPessoaConfiguracaoRepositoryImpl** | Manutenção configuração pessoa CNAB |
| **VerificarDiaUtilRepositoryImpl** | Consulta dias úteis via API calendário global |

---

## 3. Tecnologias Utilizadas

- **Framework**: Spring Boot 2.x, Spring Cloud GCP
- **Processamento**: Apache Camel 3.2.0 (roteamento, processadores)
- **Mensageria**: RabbitMQ (processamento assíncrono), GCP Pub/Sub (confirmações)
- **Banco de Dados**: Oracle Database (JDBC)
- **Segurança**: OAuth2 Resource Server (JWT), API Gateway Votorantim
- **Feature Toggle**: ConfigCat
- **Documentação**: Swagger/OpenAPI 2.0
- **Serialização**: Jackson (JSON), Gson (utilitários)
- **Monitoramento**: Spring Actuator, Prometheus
- **Testes**: JUnit 5, Mockito, ArchUnit (validação arquitetura)
- **Containerização**: Docker, Kubernetes
- **Build**: Maven (multi-módulo: common, domain, application)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/cnab/validacao | CnabController | Validar layout arquivo CNAB |
| PUT | /v1/cnab/pessoa-layout-arquivo | CnabController | Atualizar configuração pessoa CNAB |
| PUT | /v1/cnab/cancelar-agendamento | CnabController | Cancelar agendamento CNAB |
| GET | /v1/cnab/pessoa | CnabController | Consultar configuração pessoa CNAB |
| GET | /v1/cnab/arquivo/layout | CnabController | Listar layouts CNAB disponíveis |
| GET | /v1/cnab/tipo-transferencia | CnabController | Buscar tipos transferência CNAB |
| GET | /v1/cnab/pagamento/detalhe | CnabController | Buscar detalhe pagamento CNAB |
| GET | /v1/cnab/arquivo/resumido | CnabController | Consultar arquivos CNAB resumidos (filtros: pessoa, situação, período) |
| POST | /pagamento-cnab/cancelarAgendamento/{nsuAgendamento} | PagamentoCnabController | Cancelar agendamento por NSU |
| GET | /pagamento-cnab/consultarAgendamento | PagamentoCnabController | Consultar agendamento por NSU |

---

## 5. Principais Regras de Negócio

1. **Validação Arquivo CNAB**: Valida layout contra configuração pessoa (CNAB_PESSOA_CONFIG), extensão (.txt/.rem), caracteres especiais, segmentos aceitos.

2. **Tradução CNAB**: Converte registros arquivo remessa em objetos domínio (Boleto, Transferência) conforme tipo liquidação (22=boleto, 21/31/32/61/62=transferência).

3. **Validação Dia Útil**: Consulta calendário global para validar data movimento, ajusta para próximo dia útil se necessário.

4. **Remoção Lançamentos Inválidos**: Remove detalhes com movimento diferente de INCLUSAO (exclusão/alteração) ou já finalizados (status 3,5,6,10).

5. **Roteamento Pagamento**: 
   - Boleto (cdLiquidacao=22) → API pagamento-boleto
   - Transferência (21,31,32,61,62) → API transferências
   - Agendamento → API agendamento CCBD (se dtMovimento > hoje)

6. **Feature Toggles**:
   - `ft_permitir_agendamentos_cnab_spag`: Habilita agendamentos CNAB
   - `ft_permitir_agendamentos_sem_saldo_cnab_spag`: Permite agendar pagamentos com saldo insuficiente

7. **Tratamento Saldo Insuficiente**: Identifica status 77/"ERRO_SALDO_INSUFICIENTE"/"BDCC_SALDO_INSUFICIENTE", tenta agendar se FT habilitado.

8. **Controle Retentativas**: RabbitMQ com header X_RETRIES_HEADER, máximo 5 tentativas, envia para DLQ após exceder.

9. **Confirmação Pagamento**: Processa NSU list com status 3=confirmado, 11=rejeitado, atualiza CNAB_ARQUIVO_DETALHE.

10. **Retorno CNAB**: Consumer GCP Pub/Sub filtra origem "CNAB", diferencia sucesso (codigoStatus=3) de erro, atualiza detalhe com data/valor/autenticação.

11. **Situações Detalhe CNAB**: 1=pendente, 2=excluído, 3=rejeitado, 4=autorizado, 5=agendado, 6=efetuado, 7=devolvido, 8=alterado, 9=conferência, 10=processamento.

12. **Extração Dados NSU**: Regex para extrair cdCnabArquivo/cdSequencialLote/cdSequencialDetalhe de NSU formato específico.

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **CnabArquivo**: Representa arquivo CNAB remessa (1:N CnabArquivoLote)
- **CnabArquivoLote**: Lote dentro do arquivo (1:N CnabArquivoDetalhe)
- **CnabArquivoDetalhe**: Detalhe individual de pagamento (relaciona com Boleto/Transferência)
- **Boleto**: Dados pagamento boleto (herda características detalhe CNAB)
- **Transferencia**: Dados transferência TED/DOC/PIX (herda características detalhe CNAB)
- **AgendamentoCcbd**: Representa agendamento CCBD (vinculado a detalhe via NSU)
- **CnabPessoaConfig**: Configuração layouts/tipos transferência por pessoa
- **ResultadoEnvioPagamento**: Resultado envio pagamento (protocolo, situação, ocorrência)
- **ConfirmacaoPagamento**: Confirmação pagamento via NSU list
- **PagamentoMensagemRetorno**: Retorno pagamento via GCP Pub/Sub

**Relacionamentos:**
- CnabArquivo 1:N CnabArquivoLote 1:N CnabArquivoDetalhe
- CnabArquivoDetalhe 1:1 Boleto/Transferencia (polimorfismo)
- CnabArquivoDetalhe 1:1 AgendamentoCcbd (via NSU)
- CnabPessoaConfig 1:N CnabArquivoLayout

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| CNAB_ARQUIVO | tabela | SELECT | Consulta arquivos CNAB (resumido, detalhe) |
| CNAB_ARQUIVO_LOTE | tabela | SELECT | Consulta lotes arquivo CNAB |
| CNAB_ARQUIVO_DETALHE | tabela | SELECT | Consulta detalhes pagamento CNAB |
| CNAB_PESSOA_CONFIG | tabela | SELECT | Consulta configuração pessoa CNAB (layouts, tipos transferência) |
| CNAB_ARQUIVO_LAYOUT | tabela | SELECT | Consulta layouts CNAB disponíveis |
| CNAB_TIPO_TRANSFERENCIA | tabela | SELECT | Consulta tipos transferência CNAB |
| CNAB_VALIDADOR | tabela | SELECT | Consulta regras validação layout CNAB |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| CNAB_ARQUIVO | tabela | UPDATE | Atualiza situação arquivo (rejeitado) |
| CNAB_ARQUIVO_DETALHE | tabela | INSERT/UPDATE | Inclui/atualiza detalhes pagamento (situação, protocolo, data pagamento, valor, autenticação) |
| CNAB_ARQUIVO_DETALHE | tabela | UPDATE | Atualiza por NSU ou sequencial (situação, ocorrência) |
| CNAB_PESSOA_CONFIG | tabela | UPDATE | Atualiza configuração pessoa CNAB (layouts, tipos transferência, data validação) |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| Arquivo CNAB remessa (.txt/.rem) | leitura | ValidacaoArquivoCnabService, TraduzirArquivoCnabProcessor | Arquivo entrada processamento CNAB (Base64 encoded) |
| Logs aplicação | gravação | Logback (application.yml) | Logs processamento, erros, auditoria |

---

## 10. Filas Lidas

| Nome da Fila | Tecnologia | Classe Consumidora | Descrição |
|--------------|------------|-------------------|-----------|
| PROCESSAMENTO_CNAB_SPAG_QUEUE | RabbitMQ | FilaRabbitListener.novoProcessamentoCnab | Fila principal processamento arquivo CNAB |
| PROCESSAMENTO_CNAB_SPAG_WAITING_QUEUE | RabbitMQ | FilaRabbitListener.novoProcessamentoCnab | Fila retry processamento CNAB |
| PROCESSAMENTO_CNAB_SPAG_DLQ_QUEUE | RabbitMQ | FilaRabbitListener.novoProcessamentoCnabDLQ | Dead Letter Queue processamento CNAB |
| CONFIRMACAO_RETORNO_PAGAMENTO_SPAG_CNAB_QUEUE | RabbitMQ | FilaRabbitListener.confirmacaoRetornoPagamentoCnab | Fila confirmação pagamento via NSU list |
| business-spag-base-confirmacao-cnab-sub | GCP Pub/Sub | RetornoPagamentoCnabListener | Subscription retorno pagamento CNAB (origem "CNAB") |

---

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Produtora | Descrição |
|--------------|------------|-----------------|-----------|
| ENVIO_PAGAMENTO_SPAG_CNAB_WAITING_QUEUE | RabbitMQ | PagamentoCnabEnvioQueueRetry | Fila retry envio pagamento |
| RETORNO_PAGAMENTO_OK_WAITING_QUEUE | RabbitMQ | PagamentoVerificadorEnvioQueueRetry | Fila retry retorno pagamento OK |
| RETORNO_PAGAMENTO_ERRO_WAITING_QUEUE | RabbitMQ | PagamentoVerificadorEnvioQueueRetry | Fila retry retorno pagamento erro |
| CONFIRMACAO_RETORNO_PAGAMENTO_WAITING_QUEUE | RabbitMQ | PagamentoVerificadorEnvioQueueRetry | Fila retry confirmação pagamento |
| NOVO_PROCESSAMENTO_WAITING_QUEUE | RabbitMQ | PagamentoCnabEnvioQueueRetry | Fila retry novo processamento CNAB |
| PROCESSAMENTO_CNAB_SPAG_DLQ_QUEUE | RabbitMQ | PagamentoCnabEnvioQueueRetry | DLQ após exceder 5 tentativas |
| RETORNO_PAGAMENTO_OK_DLQ_QUEUE | RabbitMQ | PagamentoVerificadorEnvioQueueRetry | DLQ retorno OK após exceder tentativas |
| RETORNO_PAGAMENTO_ERRO_DLQ_QUEUE | RabbitMQ | PagamentoVerificadorEnvioQueueRetry | DLQ retorno erro após exceder tentativas |
| CONFIRMACAO_RETORNO_PAGAMENTO_DLQ_QUEUE | RabbitMQ | PagamentoVerificadorEnvioQueueRetry | DLQ confirmação após exceder tentativas |

---

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| **sboot-spag-base-orch-pagamento-boleto-srv** | REST API | Envio pagamentos boleto (POST /v2/pagamento-boleto) |
| **sboot-spag-base-orch-transferencias** | REST API | Envio transferências TED/DOC/PIX (POST /v2/transferencia) |
| **sboot-ccbd-base-orch-agendamento** | REST API | Criação agendamentos CCBD (orquestração) |
| **sboot-ccbd-base-atom-agendamento** | REST API | Cancelamento/consulta agendamentos CCBD (atom) |
| **sboot-pgft-base-atom-pagamento-cnab** | REST API | Validação layout CNAB, CRUD detalhes/arquivo, configuração pessoa |
| **sboot-spag-base-atom-pagamento** | REST API | Consulta pagamento em processamento (retorno CNAB) |
| **sboot-glob-base-atom-calendario** | REST API | Verificação dia útil (GET /verificarDiaUtil) |
| **API Gateway Votorantim** | OAuth2 Gateway | Autenticação/autorização via JWT |
| **ConfigCat** | Feature Toggle | Controle feature toggles (agendamentos CNAB) |
| **GCP Pub/Sub** | Mensageria | Confirmações retorno pagamento CNAB (topic business-spag-base-confirmacao-cnab) |
| **RabbitMQ** | Mensageria | Processamento assíncrono CNAB, confirmações, retries |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura hexagonal bem definida (domain, application, infrastructure)
- Separação clara de responsabilidades (services, repositories, mappers, processors)
- Uso adequado de Apache Camel para orquestração de fluxos complexos
- Tratamento robusto de exceções com handlers específicos por tipo de erro
- Controle de retentativas bem implementado (RabbitMQ + DLQ)
- Feature toggles para controle de funcionalidades em produção
- Testes estruturados (unit, integration, functional) com ArchUnit para validação arquitetural
- Documentação OpenAPI/Swagger completa
- Uso de enums para tipos de negócio (evita magic numbers)
- Mappers dedicados para conversão DTOs (evita lógica espalhada)

**Pontos de Melhoria:**
- Algumas classes com múltiplas responsabilidades (ex: PagamentoCnabService orquestra validação + envio + rejeição)
- Lógica de negócio em processors Camel poderia estar em services dedicados
- Nomenclatura inconsistente em alguns pontos (ex: "Diff Movimentação" poderia ser mais clara)
- Falta de documentação inline em métodos complexos (ex: regex extração NSU)
- Dependência forte de configurações externas (properties) sem validação em startup
- Alguns mappers com lógica de negócio (ex: ajustarConta/Agencia deveria estar em service)
- Tratamento genérico de exceções em alguns pontos (catch Exception)
- Falta de circuit breaker para integrações externas (resiliência)

---

## 14. Observações Relevantes

1. **Arquitetura Multi-Módulo**: Projeto organizado em 3 módulos Maven (common, domain, application) para separação de concerns e reusabilidade.

2. **Processamento Assíncrono Híbrido**: Combina RabbitMQ (processamento interno) com GCP Pub/Sub (confirmações externas) para desacoplamento e resiliência.

3. **Controle de Retentativas Robusto**: Sistema de retry com waiting queues e DLQ após 5 tentativas, header X_RETRIES_HEADER para controle.

4. **Feature Toggles Críticos**: Funcionalidades de agendamento controladas via ConfigCat, permitindo habilitar/desabilitar em runtime sem deploy.

5. **Validação Layout CNAB**: Integração com serviço atom-pagamento-cnab para validação contra regras configuradas por pessoa (CNAB_PESSOA_CONFIG).

6. **Tratamento Saldo Insuficiente**: Lógica específica para identificar erro de saldo (status 77, códigos específicos) e tentar agendamento se FT habilitado.

7. **Segurança OAuth2**: Todas as APIs protegidas via JWT, integração com API Gateway Votorantim para autenticação centralizada.

8. **Monitoramento**: Actuator + Prometheus para métricas, logs estruturados para auditoria.

9. **Ambientes**: Configuração multi-profile (local, des, qa, uat, prd) com variáveis ambiente específicas.

10. **Kubernetes**: Deploy em GKE (Google Kubernetes Engine), projeto GCP bv-spag-{env}.

11. **Fluxo Principal CNAB**: Upload arquivo → Validação layout → Tradução registros → Validação dia útil → Envio pagamento (boleto/transferência/agendamento) → Confirmação → Atualização detalhe → Retorno CNAB.

12. **Tipos Liquidação Suportados**: 22=boleto, 21=TED, 31=DOC, 32=transferência interna, 61/62=PIX.

13. **Situações Detalhe CNAB**: 10 estados possíveis (pendente, excluído, rejeitado, autorizado, agendado, efetuado, devolvido, alterado, conferência, processamento).

14. **Integração CCBD**: Sistema integra com plataforma CCBD (Conta Corrente Banco Digital) para agendamentos, usando tanto orquestração quanto atom.

15. **Tratamento Diff Movimentação**: Lógica específica para tratar exclusões/alterações de lançamentos (movimento diferente de INCLUSAO).

16. **Extração Dados NSU**: Regex complexo para extrair cdCnabArquivo/cdSequencialLote/cdSequencialDetalhe de NSU formato específico, usado para vincular agendamento a detalhe CNAB.

17. **Conversão Datas**: Utilitários para conversão entre BVDate/BVDatetime (padrão Banco Votorantim) e LocalDate/OffsetDateTime (Java 8+).

18. **Sanitização Logs**: SecureLogUtil para remover dados sensíveis de logs (segurança).

19. **Validação Arquitetural**: ArchUnit para garantir aderência a padrões arquiteturais (ex: dependências entre camadas).

20. **Gestão Configuração**: Centralizada em application.yml com profiles, propriedades específicas por ambiente via variáveis.