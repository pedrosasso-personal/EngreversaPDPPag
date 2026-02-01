---
## Ficha Técnica do Sistema


### 1. Descrição Geral
Sistema atômico responsável por gerenciar débito automático dos produtos do banco digital (Banco Votorantim). O sistema realiza agendamento, processamento e controle de pagamentos via débito automático para produtos como cartão de crédito, financiamento de veículos e crédito pessoal. Integra-se com sistemas de pagamento (SPAG), filas de mensageria (RabbitMQ e IBM MQ) e publica eventos no Kafka para notificação de débitos efetivados.


### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `DebitoAutomaticoController` | Controlador REST que expõe endpoints para agendamento, consulta e cancelamento de débitos automáticos |
| `PagamentoDebitoAutomaticoService` | Serviço transacional que gerencia o ciclo de vida dos pagamentos de débito automático |
| `DebitoAutomaticoService` | Serviço de domínio com regras de negócio para agendamento, cancelamento e consulta de débitos |
| `PagamentoDebitoAutomaticoRepositoryImpl` | Implementação do repositório de acesso a dados usando JDBI |
| `DebitoAutomaticoListener` | Listener RabbitMQ que processa retornos de pagamento do SPAG |
| `CancelarAgendamentoDebitoAutomaticoListener` | Listener IBM MQ que processa cancelamentos de agendamento de fatura |
| `DebitoAutomaticoEfetivadoEventProducer` | Producer Kafka para publicar eventos de débito automático efetivado (versão 1) |
| `DebitoAutomaticoEfetivadoEventProducerV2` | Producer Kafka para publicar eventos de débito automático efetivado (versão 2) |
| `PagamentoDebitoAutomatico` | Entidade de domínio representando um pagamento de débito automático |


### 3. Tecnologias Utilizadas
- **Framework:** Spring Boot 2.x
- **Linguagem:** Java 11
- **Persistência:** JDBI 3.9.1, MySQL 8.0.22
- **Mensageria:** RabbitMQ, IBM MQ (com.ibm.mq:mq-jms-spring-boot-starter 2.3.1), Apache Kafka (com Avro)
- **Documentação API:** Swagger/OpenAPI (Springfox 3.0.0)
- **Monitoramento:** Spring Actuator, Micrometer Prometheus
- **Mapeamento:** MapStruct 1.4.2
- **Segurança:** Spring Security (JWT)
- **Feature Toggle:** ConfigCat (via sbootlib-arqt-base-feature-toggle)
- **Containerização:** Docker
- **Build:** Maven 3.3+
- **Observabilidade:** Grafana, Prometheus


### 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/banco-digital/conta/debito-automatico/agendar` | `DebitoAutomaticoController` | Agendar pagamento em débito automático |
| GET | `/v1/banco-digital/conta/debito-automatico/consultarPagamentoPorNuProtocoloPagamento/{numeroProcotoloSolicitacao}` | `DebitoAutomaticoController` | Consultar pagamento por número de protocolo |
| PUT | `/v1/banco-digital/conta/debito-automatico/cancela-agendamento-debito-por-numero-contrato/{numeroContrato}` | `DebitoAutomaticoController` | Cancelar agendamento por número de contrato |
| GET | `/v1/banco-digital/conta/debito-automatico/consultar` | `DebitoAutomaticoController` | Consultar pagamentos por data |
| GET | `/v1/banco-digital/conta/debito-automatico/consultarTotalPagamentosPorConvenio` | `DebitoAutomaticoController` | Consultar total de pagamentos por convênio |
| POST | `/v1/banco-digital/conta/debito-automatico/iniciar-execucao-envio` | `DebitoAutomaticoController` | Iniciar execução de envio de pagamentos |
| POST | `/v1/banco-digital/conta/debito-automatico/finalizar-execucao-envio` | `DebitoAutomaticoController` | Finalizar execução de envio de pagamentos |
| GET | `/v1/banco-digital/conta/debito-automatico/consultar-pagamentos-enviados` | `DebitoAutomaticoController` | Consultar pagamentos enviados |
| PUT | `/v1/banco-digital/conta/debito-automatico/atualizar-pagamentos-enviados` | `DebitoAutomaticoController` | Atualizar status de pagamentos enviados |
| GET | `/v1/banco-digital/conta/debito-automatico/listar-faturas-efetivadas-cartao` | `DebitoAutomaticoController` | Listar faturas efetivadas de cartão |
| PUT | `/v1/banco-digital/conta/debito-automatico/atualizar-linha-digitavel-fatura-cartao` | `DebitoAutomaticoController` | Atualizar linha digitável de fatura de cartão |
| DELETE | `/v1/banco-digital/conta/debito-automatico/cancelar-unitario/{numeroUnicoDebitoAutomatico}` | `DebitoAutomaticoController` | Cancelar pagamento por NSU |


### 5. Principais Regras de Negócio
- **Agendamento de Débito Automático:** Valida convênio, cria arquivo de remessa, pessoa e pagamento. Para financiamento/crédito, cancela agendamentos anteriores de sequências menores do contrato e verifica duplicidade por valor, data de vencimento e parcela.
- **Cancelamento de Agendamento:** Permite cancelamento apenas de pagamentos com status "Agendado" e data de vencimento futura. Valida NSU único para evitar cancelamento duplicado.
- **Processamento de Retorno SPAG:** Atualiza status do pagamento conforme retorno (Pago, Enviado, Sem Saldo, Serviço Indisponível, Erro). Implementa lógica de retry (até 7 tentativas) para falta de saldo ou serviço indisponível.
- **Publicação de Eventos:** Publica eventos no Kafka quando débito é efetivado com sucesso (versões v1 e v2 do schema).
- **Controle de Tentativas:** Registra histórico de liquidação a cada tentativa de pagamento.
- **Feature Toggle:** Filtra CPFs/CNPJs habilitados para cancelamento de agendamento via ConfigCat.
- **Validação de Produtos:** Diferencia tratamento entre Cartão de Crédito (código 1) e Financiamento/Crédito Pessoal (códigos 2, 3, 4).


### 6. Relação entre Entidades
- **PagamentoDebitoAutomatico:** Entidade principal que representa um pagamento agendado. Relaciona-se com:
  - `PessoaPagamentoDebitoAutomatico` (1:1) - dados da pessoa/conta
  - `ConvenioDebitoAutomatico` (N:1) - convênio do produto
  - `ArquivoDebitoAutomatico` (N:1) - arquivo de remessa/retorno
  - `StatusPagamentoDebitoAutomatico` (N:1) - status atual do pagamento
- **ConvenioDebitoAutomatico:** Relaciona-se com `TipoProdutoDebitoAutomatico` (N:1)
- **ExecucaoEnvioDebitoAutomatico:** Representa uma execução de envio em lote, relaciona-se com múltiplos `PagamentoDebitoAutomatico` via tabela de relacionamento
- **TransicaoHistoricoLiquidacao:** Registra histórico de tentativas de pagamento


### 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbConvenioDebitoAutomatico | Tabela | SELECT | Consulta convênios de débito automático por banco e tipo de produto |
| TbArquivoDebitoAutomatico | Tabela | SELECT | Consulta arquivos de remessa/retorno de débito automático |
| TbPagamentoDebitoAutomatico | Tabela | SELECT | Consulta pagamentos agendados, enviados e efetivados |
| TbPessoaDebitoAutomatico | Tabela | SELECT | Consulta dados de pessoa/conta vinculada ao débito |
| TbStatusPagamentoDebitoAtmto | Tabela | SELECT | Consulta status de pagamento |
| TbTipoProdutoDebitoAutomatico | Tabela | SELECT | Consulta tipos de produto (cartão, financiamento, etc) |
| TbExecucaoEnvioDebitoAutomatico | Tabela | SELECT | Consulta execuções de envio de pagamentos |
| TbRelacionamentoExecucaoPagamento | Tabela | SELECT | Consulta relacionamento entre execução e pagamentos |


### 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbConvenioDebitoAutomatico | Tabela | INSERT | Insere novos convênios de débito automático |
| TbArquivoDebitoAutomatico | Tabela | INSERT | Insere registros de arquivos de remessa |
| TbPessoaDebitoAutomatico | Tabela | INSERT | Insere dados de pessoa/conta |
| TbPagamentoDebitoAutomatico | Tabela | INSERT | Insere novos agendamentos de débito automático |
| TbPagamentoDebitoAutomatico | Tabela | UPDATE | Atualiza status, protocolo, tentativas e dados de pagamento |
| TbExecucaoEnvioDebitoAutomatico | Tabela | INSERT | Insere registro de execução de envio |
| TbExecucaoEnvioDebitoAutomatico | Tabela | UPDATE | Atualiza protocolo e status de execução |
| TbRelacionamentoExecucaoPagamento | Tabela | INSERT | Insere relacionamento entre execução e pagamentos |
| TbControleStatusPagamento | Tabela | INSERT | Insere histórico de tentativas de liquidação |


### 9. Arquivos Lidos e Gravados
não se aplica


### 10. Filas Lidas
- **RabbitMQ:** `debito_automatico.proc.pagamento` - Recebe retornos de processamento de pagamento do SPAG
- **IBM MQ:** `QM.CCBD.CANCELAMENTO_AGENDAMENTO_FATURA.INT` (DES) / `QL.CCBD.CANCELAMENTO_AGENDAMENTO_FATURA.INT` (QA/UAT/PRD) - Recebe solicitações de cancelamento de agendamento de fatura


### 11. Filas Geradas
- **Kafka:** `ccbd-base-debito-automatico-efetivado` - Publica eventos de débito automático efetivado (schema v1)
- **Kafka:** `ccbd-base-debito-automatico-efetivado-v2` - Publica eventos de débito automático efetivado (schema v2 com dados enriquecidos)


### 12. Integrações Externas
- **SPAG (Sistema de Pagamentos):** Integração via RabbitMQ para envio e recebimento de status de pagamentos
- **Sistema de Cartões:** Integração via IBM MQ para receber cancelamentos de agendamento de fatura
- **Kafka/Confluent Cloud:** Publicação de eventos de débito automático efetivado para consumo por outros sistemas
- **ConfigCat:** Serviço de feature toggle para controle de funcionalidades
- **MySQL (Cloud SQL):** Banco de dados principal para persistência


### 13. Avaliação da Qualidade do Código

**Nota:** 7.5

**Justificativa:**
O código apresenta boa organização arquitetural seguindo padrões de Clean Architecture (separação em camadas domain, application). Pontos positivos incluem: uso adequado de DTOs e mappers, tratamento de exceções customizado, logs estruturados, uso de transações, e documentação via Swagger. 

Pontos de melhoria: alguns métodos muito extensos (ex: `DebitoAutomaticoService.agendarPagamento`), lógica de negócio complexa que poderia ser melhor modularizada, uso de mappers manuais onde poderia aproveitar melhor o MapStruct, alguns SQLs inline que poderiam estar em arquivos separados (embora a maioria já esteja), e falta de alguns comentários explicativos em regras de negócio mais complexas. A cobertura de testes parece adequada pela estrutura de pastas, mas não foi possível avaliar a qualidade dos testes unitários.


### 14. Observações Relevantes
- Sistema utiliza JDBI ao invés de JPA/Hibernate, com queries SQL explícitas em arquivos separados
- Implementa versionamento de schemas Avro para eventos Kafka (v1 e v2)
- Possui configuração para múltiplos ambientes (local, des, qa, uat, prd)
- Utiliza HikariCP para pool de conexões
- Implementa retry automático para falhas de saldo insuficiente (até 7 tentativas)
- Feature toggle permite controle granular de funcionalidades por CPF/CNPJ
- Sistema preparado para observabilidade com Prometheus/Grafana
- Possui configuração Docker e infraestrutura como código (infra.yml)
- Utiliza Spring Security com JWT para autenticação/autorização
- Implementa auditoria via trilha de auditoria do BV