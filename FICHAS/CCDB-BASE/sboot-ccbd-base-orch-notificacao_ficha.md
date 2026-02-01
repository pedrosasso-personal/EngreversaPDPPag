# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-ccbd-base-orch-notificacao** é um serviço de orquestração de notificações desenvolvido em Spring Boot para o Banco Votorantim. O sistema é responsável por processar e encaminhar notificações de diversas operações bancárias (PIX, débito automático, boletos, débitos veiculares) para diferentes canais (Banco Digital, Internet Banking, Salesforce Marketing Cloud). Atua como um orquestrador central que recebe mensagens de filas RabbitMQ, processa regras de negócio específicas e encaminha as notificações para os destinos apropriados, incluindo integração com sistemas de antifraude.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot que inicializa a aplicação |
| `NotificacaoService` | Serviço principal que orquestra o fluxo de notificações |
| `NotificacaoRouter` | Roteador Apache Camel que define as rotas de processamento |
| `ChaveDictBusinessImpl` | Implementa lógica de negócio para notificações de chaves PIX/DICT |
| `EfetivacaoBusinessImpl` | Processa notificações de efetivação de pagamentos PIX |
| `RecebimentoBusinessImpl` | Trata notificações de recebimento de valores PIX |
| `NotificacaoAgendamentoPixService` | Gerencia notificações de agendamentos PIX cancelados |
| `NotificacaoBoletoService` | Processa notificações de pagamento de boletos |
| `NotificacaoDebitosVeicularesService` | Gerencia notificações de débitos veiculares |
| `NotificacaoPagamentoDebitoAutomaticoService` | Processa notificações de débito automático |
| `PixToGfrdAdapter` | Adapta mensagens PIX para o formato do sistema antifraude |
| `AntifraudeRepositoryImpl` | Integração com API de análise antifraude |
| `NotificacaoSalesForceMarketingCloudRepositoryImpl` | Envia push notifications via Salesforce |

## 3. Tecnologias Utilizadas

- **Framework:** Spring Boot 2.x
- **Linguagem:** Java 11
- **Mensageria:** RabbitMQ (AMQP), IBM MQ (JMS)
- **Integração:** Apache Camel 3.22.4
- **Documentação API:** Swagger/OpenAPI (Springfox 3.0.0)
- **Monitoramento:** Spring Actuator, Micrometer Prometheus
- **Segurança:** Spring Security, JWT
- **Serialização:** Jackson
- **Build:** Maven
- **Containerização:** Docker
- **Orquestração:** Kubernetes/OpenShift (Google Cloud Platform)
- **Auditoria:** Biblioteca BV de trilha de auditoria

## 4. Principais Endpoints REST

não se aplica

(O sistema não expõe endpoints REST próprios - funciona como consumidor de mensagens de filas)

## 5. Principais Regras de Negócio

1. **Roteamento de Notificações por Agência:** Identifica se a notificação deve ir para Internet Banking (agência 0001) ou Banco Digital (agência 2020)
2. **Processamento de Chaves PIX/DICT:** Gerencia portabilidade e reivindicação de chaves PIX, diferenciando quando o BV é doador ou recebedor
3. **Análise Antifraude:** Envia transações PIX de recebimento para análise antifraude de forma assíncrona
4. **Notificação de Status de Pagamento:** Processa diferentes status de operações (confirmado, rejeitado, pendente) e envia notificações apropriadas
5. **Débito Automático com Retentativas:** Implementa lógica de múltiplas tentativas de débito com notificações específicas por tentativa (2ª, 4ª, 7ª e 8ª tentativas)
6. **Diferenciação por Tipo de Produto:** Trata de forma diferente cartões (tipo 1) e financiamentos (tipo 2) em débitos automáticos
7. **Conclusão Automática de Claims:** Conclui automaticamente portabilidades de chaves PIX quando confirmadas
8. **Mascaramento de Dados Sensíveis:** Mascara CPF/CNPJ em mensagens de notificação
9. **Geração de Tokens JWT:** Obtém tokens de autenticação para diferentes instituições (BV e BVSA)
10. **Notificação de Fraudes:** Envia status de operações suspeitas para fila específica de fraudes

## 6. Relação entre Entidades

**Entidades Principais:**
- `Notificacao`: Entidade raiz contendo id, documento, actionType e mensagem
- `MensagemPagamentoPix` / `MensagemDevolucaoPix`: Detalhes de transações PIX
- `MensagemPIX`: Informações de chaves DICT/PIX
- `NotificacaoBancoDigital`: Estrutura para envio ao Banco Digital
- `NotificacaoInternetBanking`: Estrutura para Internet Banking
- `Agendamento` / `NotificacaoAgendamentoPix`: Dados de agendamentos PIX
- `NotificacaoPagamentoDebitoAutomatico`: Informações de débito automático
- `NotificacaoBoleto`: Dados de pagamento de boletos
- `NotificacaoPagamentoDebitosVeiculares`: Informações de débitos veiculares

**Relacionamentos:**
- Notificacao → (contém) → MensagemPagamentoPix/MensagemDevolucaoPix/MensagemPIX
- NotificacaoBancoDigital → (contém) → Mensagem → (contém) → Dados
- Agendamento → (contém) → Conta (remetente e favorecido)
- AnalysisRequest → (contém) → AdditionalData → (contém) → FinancialTransactionData

## 7. Estruturas de Banco de Dados Lidas

não se aplica

(O sistema não acessa diretamente banco de dados - toda comunicação é via APIs REST e filas de mensagens)

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

(O sistema não realiza operações diretas em banco de dados)

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | leitura | /usr/etc/log (runtime) | Configuração de logs da aplicação |
| application.yml | leitura | resources/ | Configurações da aplicação por ambiente |
| sboot-gnms-base-orch-envio-push.yaml | leitura | resources/swagger-client/ | Especificação OpenAPI do cliente de envio de push |
| payload.txt | leitura | resources/ | Exemplos de payloads para testes |

## 10. Filas Lidas

**RabbitMQ:**
- `conta_corrente`: Notificações gerais de conta corrente (PIX, chaves DICT)
- `debito_automatico.notificacao.vencimento`: Notificações de vencimento de débito automático
- `debito_automatico.notificacao.agendamento`: Notificações de agendamento de débito automático
- `debito_automatico.notificarPagamentoSucesso`: Confirmações de pagamento de débito automático
- `debito_automatico.notificacao.pagamento`: Notificações de pagamento de débito automático (erros)
- `notificacao_agendamento_pix`: Notificações de agendamentos PIX cancelados
- `notificacao_pagamento_boleto`: Notificações de pagamento de boletos
- `notificacao_pagamento_debitos_veiculares`: Notificações de débitos veiculares

## 11. Filas Geradas

**RabbitMQ:**
- `ex.ccbd.pix` (exchange) com routing keys:
  - `efetivar.pix`: Efetivação de pagamentos PIX
  - `devolver.pix`: Devolução de pagamentos PIX
- `ex.ccbd.notificacao.fraudes` (exchange):
  - `ccbd.atualizarFeedzai.v1`: Atualização de status de fraudes
- `notificacoes` (exchange):
  - `intb`: Notificações para Internet Banking

**IBM MQ:**
- `QL.CCBD.LIQ_PAGMT_CONTAS_DIG.INT` (DES)
- `QL.GAPP.ENVIA_MENSAGEM.INT` (QA/UAT/PRD): Mensagens para o GAPP (Banco Digital)

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| API Gateway BV | REST | Geração de tokens JWT para autenticação |
| API Gateway BVSA | REST | Geração de tokens JWT para BVSA |
| SPAG PIX - DICT Transação | REST | Consulta de chaves PIX/DICT |
| SPAG PIX - Chaves DICT | REST | Conclusão de claims de portabilidade |
| SPAG PIX - Participantes | REST | Consulta de participantes PIX (bancos) |
| Débito Automático Atom | REST | Consulta de informações de débito automático |
| Cliente Dados Cadastrais | REST | Consulta de pessoas relacionadas |
| Análise de Fraudes (GFRD) | REST | Envio de transações para análise antifraude |
| Envio Push Orch (GNMS) | REST | Envio de notificações push via Salesforce Marketing Cloud |
| IBM MQ (GAPP) | JMS | Envio de mensagens para o sistema GAPP |
| RabbitMQ | AMQP | Consumo e publicação de mensagens |

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (application, domain, common)
- Uso adequado de padrões como Strategy (INotificacaoBusiness) e Adapter (PixToGfrdAdapter)
- Implementação de Apache Camel para orquestração de rotas
- Logs estruturados e informativos
- Uso de Lombok para reduzir boilerplate
- Configuração externalizada por ambiente
- Tratamento de exceções customizadas

**Pontos de Melhoria:**
- Classes de negócio muito extensas (ex: RecebimentoBusinessImpl, StatusMensagem)
- Lógica de negócio misturada com formatação de mensagens
- Uso excessivo de strings literais e "magic numbers" em alguns pontos
- Falta de testes unitários para algumas classes críticas
- Alguns métodos muito longos que poderiam ser refatorados
- Comentários em português misturados com código em inglês
- Algumas classes com múltiplas responsabilidades (ex: StatusMensagem gerencia templates e formatação)
- Falta de documentação JavaDoc em métodos públicos importantes

## 14. Observações Relevantes

1. **Arquitetura Multi-Canal:** O sistema suporta múltiplos canais de notificação (Banco Digital, Internet Banking, Salesforce) com roteamento inteligente baseado em regras de negócio

2. **Processamento Assíncrono:** Utiliza processamento assíncrono para análise antifraude, evitando bloqueio do fluxo principal

3. **Resiliência:** Implementa retry automático em filas RabbitMQ (configurado com maxAttempts: 3)

4. **Segurança:** Implementa autenticação via JWT e integração com API Gateway para obtenção de tokens

5. **Observabilidade:** Exposição de métricas via Prometheus e health checks via Actuator

6. **Multi-Instituição:** Suporta operações tanto para BV quanto BVSA com tokens e configurações específicas

7. **Ambiente Cloud:** Preparado para execução em Kubernetes/OpenShift no Google Cloud Platform

8. **Auditoria:** Integração com biblioteca de auditoria do BV para rastreabilidade de operações

9. **Configuração por Ambiente:** Suporte completo para múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas

10. **Geração de Ticket:** Implementa geração de UUID para rastreamento de requisições (MDC)