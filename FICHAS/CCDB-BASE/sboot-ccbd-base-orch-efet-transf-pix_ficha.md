# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de orquestração de transferências PIX desenvolvido em Spring Boot com Apache Camel, responsável por gerenciar o ciclo completo de efetivação de pagamentos instantâneos. O sistema realiza validações de conta, análise de fraude, gestão de limites transacionais, envio de pagamentos via SPAG (Sistema de Pagamentos), agendamento de transferências, emissão de comprovantes e notificações. Suporta múltiplos canais de pagamento (primário e secundário), Open Finance, QR Code, saque/troco e contato seguro. Arquitetura hexagonal com separação clara entre domínio, aplicação e infraestrutura.

---

## 2. Principais Classes e Responsabilidades

| Classe/Componente | Responsabilidade |
|-------------------|------------------|
| **EfetTransfPixRouter** | Rota Camel principal para efetivação de transferências PIX com validação de fraude |
| **EfetAgendTransfPixRouter** | Rota Camel para agendamento de transferências PIX |
| **EfetivacaoAssincronaPixRouter** | Rota Camel para validação assíncrona de efetivação |
| **ValidacaoContaRouter** | Validação de contas remetente/favorecido, inclui Feature Toggle para contas controle |
| **ValidacaoFraudeRouter** | Consulta e validação de status de análise de fraude |
| **ValidacaoLimitesRouter** | Consulta e validação de limites transacionais |
| **NotificacaoRecepcaoPagamentoRouter** | Processamento de notificações de recepção de pagamento |
| **NotificacaoFraudesRouter** | Notificação ao sistema de fraudes |
| **EfetTransfPixService** | Orquestração dos fluxos de efetivação/agendamento via Camel |
| **NotificacaoService** | Envio de notificações conforme status da operação |
| **ValidacaoStatusFraudeProcessor** | Valida status de análise de fraude (aprovado/reprovado) |
| **EstornoLimitesProcessor** | Estorno de limites em caso de erro |
| **IdentificadorUnicoProcessor** | Geração de identificador único de transação (end2end) |
| **DefineTipoContaControleProcessor** | Define tipo de conta controle via Feature Toggle |
| **EfetTransfPix** | Entidade principal representando transferência PIX |
| **Agente** | Representa remetente/favorecido com conta, documento e tipo de transação |
| **Pagamento** | Dados do pagamento (endToEndId, valor liquidação, forma iniciação) |
| **StatusFraudePixResponse** | Resposta da análise de fraude |
| **ComprovantePix/ComprovanteAgendamento** | Comprovantes de transação |
| **Notificacao** | Dados de notificação (mensagem pagamento, participante, tipo) |

---

## 3. Tecnologias Utilizadas

- **Framework**: Spring Boot 2.x
- **Orquestração**: Apache Camel 3.22.4
- **Mensageria**: Spring AMQP (RabbitMQ), Google PubSub, IBM MQ
- **HTTP Client**: Feign Client, RestTemplate
- **Feature Toggle**: ConfigCat
- **Serialização**: Jackson, Gson
- **Utilitários**: Lombok
- **Testes**: JUnit 5, Mockito, Camel Test
- **Métricas**: Micrometer Prometheus
- **Logs**: Logback JSON
- **Linguagem**: Java 11
- **Cloud**: Google Cloud Platform (GCP) - Kubernetes

---

## 4. Principais Endpoints REST

O sistema não expõe endpoints REST diretamente neste módulo. A orquestração é realizada via rotas internas do Apache Camel. As integrações externas são consumidas via clientes REST (Feign/RestTemplate) conforme descrito na seção de Integrações Externas.

**Nota**: Endpoints REST são expostos por outros módulos do sistema (ex: sboot-ccbd-base-orch-efet-transf-pix) que invocam este orquestrador.

---

## 5. Principais Regras de Negócio

1. **Validação de Fraude**: Consulta status de fraude (ANALISE_APROVADA/REPROVADA/PAGAMENTO_SOLICITADO). Rejeita transação se status for REPROVADA.

2. **Validação de Limites**: Verifica limite disponível/total do cliente. Rejeita se insuficiente. Diferencia limite noturno (20h-6h) do diurno.

3. **Agendamento**: Se data da transação for maior que data atual, agenda a transferência em vez de efetivar imediatamente.

4. **Estorno de Limites**: Em caso de falha no envio do pagamento, estorna os limites previamente reservados.

5. **Conta Controle**: Via Feature Toggle, define tipo de conta específico para CNPJ BV/BVSA.

6. **Contato Seguro**: Consulta se favorecido é contato seguro. Prioriza limite conforme meio de pagamento.

7. **Canal Secundário**: Feature Toggle habilita envio via canal secundário de pagamento.

8. **Validação de Conta**: Verifica existência/status da conta, bloqueios de débito/crédito.

9. **Emissão de Comprovante**: Retry até 5 vezes com delay progressivo em caso de falha.

10. **Geração de EndToEndId**: Formato E + ISPB (8 dígitos) + Data (17 dígitos) + Random (6 dígitos alfanuméricos).

11. **Notificação**: Diferencia mensagem por tipo de transação (TRANSFERENCIA/PAGAMENTO/FALHA).

12. **PIX Repetido**: Valida duplicidade de transação (CodigoErroSpagEnum.SPAG_ERRO_OCORRENCIAS_NAO_PERMITIDAS).

13. **Titularidade**: Diferencia transações mesma titularidade (PFPF, PJPJ) de titularidade diferente (PFPJ, PJPF).

14. **Saque/Troco**: Suporta modalidades VLDN (valor líquido) e VLCP (valor compra) para saque e troco.

15. **Open Finance**: Suporta consentId e identificadorAgenteIniciadorPagamento para transações iniciadas por terceiros.

16. **Formas de Iniciação**: MANU (manual), DICT (DICT), QRDN (QR Code dinâmico), QRES (QR Code estático), INIC (iniciação), APDN (aplicativo).

---

## 6. Relação entre Entidades

```
EfetTransfPix
├── Agente (remetente)
│   ├── Conta
│   │   └── Participante
│   └── Documento
├── Agente (favorecido)
│   ├── Conta
│   │   └── Participante
│   └── Documento
├── Chave
├── ValorMonetario
├── List<Pagamento>
│   ├── EndToEndId
│   ├── ValorLiquidacao
│   └── FormaIniciacao
└── SaqueTroco
    ├── Modalidade
    ├── AgenteModalidade
    └── Valor

Notificacao
├── MensagemPagamentoPix
├── Participante
└── TokenAuthorization

StatusFraudePixResponse
├── IdTransacao
├── StatusFraude
└── ProtocoloFraude
```

---

## 7. Estruturas de Banco de Dados Lidas

Não se aplica. O sistema não acessa diretamente banco de dados. Todas as consultas são realizadas via APIs REST de outros microserviços.

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema não atualiza diretamente banco de dados. Todas as atualizações são realizadas via APIs REST de outros microserviços.

---

## 9. Arquivos Lidos e Gravados

Não se aplica. O sistema não realiza leitura ou gravação de arquivos.

---

## 10. Filas Lidas

| Nome da Fila | Tecnologia | Operação | Descrição |
|--------------|-----------|----------|-----------|
| ex.ccbd.notificacao.fraudes | RabbitMQ | Consumo | Recebe notificações de fraudes para processamento |
| QL.CCBD.LIQ_PAGMT_CONTAS_DIG.INT | IBM MQ | Consumo | Liquidação de pagamento contas digitais (ambiente DES) |
| QL.GAPP.ENVIA_MENSAGEM.INT | IBM MQ | Consumo | Envio de mensagens (ambientes QA/UAT/PRD) |

---

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Operação | Descrição |
|--------------|-----------|----------|-----------|
| ex.ccbd.notificacao.fraudes | RabbitMQ | Publicação | Notifica sistema de fraudes após efetivação de transação |
| business-ccbd-base-transferencia-pix | Google PubSub | Publicação | Publica eventos de transações PIX para consumo por outros sistemas |
| ppbd-pixx-enviar-notificacao-usuario-cmd | Kafka Confluent | Publicação | Envia comandos de notificação push para usuários |

---

## 12. Integrações Externas

### APIs REST Consumidas:

| Sistema/API | Endpoint Base | Descrição |
|-------------|---------------|-----------|
| **CCBD Validar Conta** | CCBD_VALIDAR_CONTA_URL | Validação de conta corrente do cliente |
| **SGLT Consultar Limites** | SGLT_CONSULTAR_LIMITES_URL | Consulta de limites transacionais |
| **CCBD Consultar Limites** | CCBD_CONSULTAR_LIMITES_URL | Consulta de limites CCBD (v3) |
| **SPAG Enviar Pagamento** | SPAG_ENVIAR_PAGAMENTO_URL | Envio de pagamento PIX (canal primário) |
| **SPAG Canal Secundário** | SPAG_PIXX_CANAL_SECUNDARIO_URL | Envio de pagamento via canal secundário |
| **CCBD Status Fraude** | CCBD_CONSULTA_STATUS_FRAUDE_URL | Consulta status de fraude (GTBD) |
| **CCBD Consulta Transação** | CCBD_CONSULTA_TRANSACAO_URL | Consulta transação por NSU |
| **SPAG Gerar Identificador** | SPAG_GERAR_IDENTIFICADOR_URL | Geração de EndToEndId |
| **SPAG Emitir Comprovante** | SPAG_EMITIR_COMPROVANTE_URL | Consulta operação para comprovante |
| **SPAG Participantes** | SPAG_CONSULTAR_PARTICIPANTES | Consulta participantes PIX |
| **CCBD Salvar Contato** | CCBD_SALVAR_CONTATO_URL | Salva contato favorecido |
| **CCBD Agendar Pagamento** | CCBD_AGENDAR_PAGAMENTO_URL | Agendamento de PIX |
| **CCBD Limite NSU** | CCBD_LIMITE_NSU | Gestão de NSU de limites |
| **GNMS Envio Push** | GNMS_ENVIO_PUSH | Envio de notificação push |
| **CCBD Consulta Instituição** | CCBD_CONSULTA_INSTITUICAO_URL | Consulta instituições financeiras |
| **GLOB Consulta Pessoa** | GLOB_CONSULTA_PESSOA | Consulta dados cadastrais de pessoa |
| **PPBD PIX Movimentações** | PPBD_PIX_MOVIMENTACOES | Movimentações PIX |
| **GFRD Análise Fraude** | GFRD_ANALISE_FRAUDE_URL | Solicitação de análise de fraude |
| **GTBD Atualização Fraude** | GTBD_ATUALIZACAO_STATUS_FRAUDE | Atualização de protocolo de fraude |
| **PPBD Contato Seguro** | PPBD_CONSULTAR_IS_CONTATO_SEGURO | Verifica se é contato seguro |
| **API Gerar Token** | API_GERAR_TOKEN, API_GERAR_TOKEN_PIX | Geração de tokens JWT OAuth2 |

### Mensageria:
- **RabbitMQ**: Notificações de fraudes
- **IBM MQ**: Liquidação de pagamento contas
- **Kafka Confluent**: Publicação de eventos de transferência PIX

### Feature Toggle:
- **ConfigCat**: 
  - `ft_list_digital_ppbd_pixx_conta_controle_pgmto` (lista contas controle)
  - `ft_boolean_digital_ppbd_pixx_habilita_agendamento_canal_secundario` (habilita canal secundário)

---

## 13. Avaliação da Qualidade do Código

**Nota: 8.5/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura hexagonal bem definida com separação clara entre domínio, aplicação e infraestrutura (ports/adapters)
- Uso adequado do Apache Camel para orquestração de fluxos complexos com rotas bem estruturadas
- Separação em módulos (common, domain, application) facilita manutenção e evolução
- Cobertura de testes unitários e de integração com JUnit 5 e Mockito
- Tratamento de exceções customizadas com hierarquia clara (CodigoErroEnum)
- Implementação de retry policies para operações críticas (ex: emissão de comprovante)
- Logs estruturados em JSON facilitam observabilidade
- Feature Toggles permitem configuração dinâmica sem deploy
- Uso de Lombok reduz boilerplate
- Métricas com Micrometer/Prometheus para monitoramento

**Pontos de Melhoria:**
- Algumas classes de teste muito extensas (ex: ValidarContaRepositoryImplTest com múltiplos cenários)
- Documentação inline (Javadoc) poderia ser mais abrangente
- Alguns métodos com alta complexidade ciclomática (múltiplos ifs/switches) poderiam ser refatorados
- Falta de documentação arquitetural (diagramas de sequência, fluxos)
- Alguns nomes de variáveis poderiam ser mais descritivos (ex: `fl`, `cd`, `nu`)

---

## 14. Observações Relevantes

1. **Bancos Suportados**: Sistema suporta 2 bancos - BV (código 161, ISPB 59588111) e BVSA (código 436, ISPB 01858774).

2. **Limites Diferenciados**: Implementa limites diurno, noturno (20h-6h), contato seguro e agendamento.

3. **Fluxos Síncronos e Assíncronos**: Suporta efetivação síncrona e validação assíncrona de transações.

4. **Toggle Canal Secundário**: Feature Toggle ativa canal secundário de pagamento dinamicamente.

5. **Segurança**: Mascaramento de dados sensíveis (documento, conta) via hash SHA-256 base62.

6. **Validação de Duplicidade**: Implementa validação de PIX repetido com janela temporal.

7. **Open Finance**: Suporte completo a Open Finance com consentId e identificadorAgenteIniciadorPagamento.

8. **Formas de Iniciação**: Suporta múltiplas formas de iniciação PIX (MANU, DICT, QRDN, QRES, INIC, APDN).

9. **Tipos de Transação**: Saque, troco, transferência e pagamento.

10. **Notificações Multi-Canal**: Push BD, CRM (GNMS/Salesforce), mensageria (RabbitMQ, Kafka).

11. **Observabilidade**: Métricas Prometheus, logs estruturados JSON, Grafana para dashboards.

12. **Deploy**: Google Cloud Platform (GCP) com Kubernetes, ambientes segregados (DES/QA/UAT/PRD).

13. **Retry Policies**: Implementa retry com backoff exponencial para operações críticas (comprovante até 5x, notificações até 17x/81x).

14. **Geração de Identificadores**: EndToEndId único no formato E + ISPB (8dig) + Data (17dig) + Random (6dig alfanum).

15. **Estorno Automático**: Em caso de falha, estorna automaticamente limites reservados.