# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-spag-spib-orch-tratar-mensagem** é um serviço stateless desenvolvido em Java com Spring Boot, responsável por orquestrar o tratamento de mensagens do Sistema de Pagamentos Instantâneos (SPI/PIX) do Banco Central do Brasil. 

O sistema atua como intermediário entre o Banco Central e os sistemas internos do Banco Votorantim, realizando as seguintes funções principais:
- Recepção de mensagens XML do Banco Central via Google Cloud Pub/Sub
- Validação e verificação de assinaturas digitais das mensagens usando HSM (Hardware Security Module)
- Roteamento de mensagens para diferentes processadores conforme o tipo (PACS, PAIN, CAMT, ADMI, REDA, etc.)
- Assinatura digital de mensagens de saída
- Processamento de mensagens em canal secundário para agrupamento e otimização
- Integração com múltiplos ISPBs (BV, BVSA, ACESSO/Bankly)

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot que inicializa a aplicação |
| `TratarMensagemService` | Serviço principal que coordena o tratamento de mensagens |
| `MensagemRecebidaListener` | Listener que consome mensagens do Google Pub/Sub |
| `TratarMensagemRouter` | Router Apache Camel para assinatura de mensagens |
| `MensagemRecebidaBacenRouter` | Router para processamento de mensagens recebidas do Bacen |
| `SecondaryChannelRouter` | Router para processamento de mensagens em canal secundário |
| `TratarMensagemRepositoryImpl` | Implementação para validação e assinatura de mensagens usando HSM |
| `Pacs008XMLProcessor` | Processador para agrupamento de mensagens PACS.008 |
| `Pacs002XMLProcessor` | Processador para agrupamento de mensagens PACS.002 |
| `Pain014XMLProcessor` | Processador para agrupamento de mensagens PAIN.014 |
| `AssinarMensagemProcessor` | Processador para preparação de mensagens para assinatura |
| `ValidarMensagemProcessor` | Processador para validação de mensagens recebidas |
| `MessageParser` | Utilitário para parsing de mensagens XML com tratamento de namespaces |

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.7.8** (via parent pom-atle-base-sboot-orch-stateless-parent)
- **Apache Camel 3.2.0** - Framework de integração e roteamento
- **Google Cloud Pub/Sub** - Sistema de mensageria
- **RabbitMQ** - Message broker (configurado mas não utilizado ativamente)
- **JAXB** - Marshalling/Unmarshalling de XML
- **Dinamo HSM (TacNDJavaLib 4.1.6.0)** - Hardware Security Module para assinatura digital
- **Lombok** - Redução de boilerplate code
- **Jackson** - Serialização/deserialização JSON
- **Maven** - Gerenciamento de dependências
- **Swagger/OpenAPI** - Documentação de API
- **Spring Cloud GCP 1.2.8.RELEASE** - Integração com Google Cloud Platform

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/echo-bacen/pibr001 | EchoBacenController | Envia mensagem de echo (PIBR001) para teste de conectividade com o Banco Central |

## 5. Principais Regras de Negócio

1. **Validação de Assinaturas Digitais**: Todas as mensagens recebidas do Banco Central devem ter suas assinaturas digitais validadas usando certificados armazenados no HSM antes do processamento.

2. **Roteamento por Tipo de Mensagem**: O sistema identifica o tipo de mensagem (PACS, PAIN, CAMT, ADMI, REDA) através do campo `MsgDefIdr` e roteia para o processador apropriado.

3. **Agrupamento de Mensagens em Canal Secundário**: Mensagens PACS.008, PACS.002 e PAIN.014 recebidas pelo canal secundário são agrupadas por ISPB antes do envio, otimizando a comunicação.

4. **Suporte a Múltiplos ISPBs**: O sistema suporta três ISPBs distintos (BV: 59588111, BVSA: 01858774, ACESSO/Bankly: 13140088), cada um com suas próprias credenciais HSM.

5. **Controle de Versão de Catálogo**: O sistema gerencia diferentes versões de catálogo de mensagens (v5.11 e v5.11.1) através de feature toggles, permitindo transição gradual entre versões.

6. **Processamento de Erros ADMI.002**: Mensagens de erro são classificadas e roteadas conforme o tipo de operação (pagamento, devolução, saldo, remuneração, rescaldo).

7. **Geração de Mensagens TRCK.002**: O sistema agrupa transações internas por ISPB e gera mensagens de rastreamento (TRCK.002) para envio ao Banco Central.

8. **Controle de Throughput por Período**: O sistema ajusta dinamicamente a quantidade de mensagens processadas conforme o período (diurno: 35 mensagens, noturno: 350 mensagens).

9. **Processamento de Avisos de Remuneração**: Identifica e processa separadamente avisos de remuneração baseados em messageId específico (00000000000000000000000000000000).

10. **Rescaldo de Transações**: Identifica transações que necessitam conciliação (messageId terminando em "MCR") e as roteia para processamento específico.

## 6. Relação entre Entidades

O sistema trabalha principalmente com mensagens XML do padrão ISO 20022, não possuindo entidades de domínio persistentes tradicionais. As principais estruturas de dados são:

- **SPIEnvelopeMessage**: Envelope padrão contendo AppHdr (cabeçalho) e Document (corpo da mensagem)
  - Contém: AppHdr (metadados da mensagem) e Document (conteúdo específico do tipo de mensagem)
  
- **InternalTransaction**: Representa transação interna para geração de TRCK.002
  - Contém: endToEndId, returnIdentification, ispb, operationCode, debtor (Client), creditor (Client)
  
- **InternalTransactionBank**: Agrupamento de transações por ISPB
  - Contém: ispb, List<InternalTransaction>
  
- **Client**: Dados de participante (devedor ou credor)
  - Contém: accountIdentification, accountIssuer, privateIdentification, agentMemberIdentification, accountType, accountProxy
  
- **Camt025**: Representação de mensagem de recibo/confirmação
  - Contém: messageId, status, creationDateTime, reasonCode, originalInstructionId, additionalInformation
  
- **PacsDataUpdate / PainDataUpdate**: Dados para atualização de controle de mensagens secundárias
  - Contém: messageType, operationCodes/messageControlIds, messageId, creationDateTime

## 7. Estruturas de Banco de Dados Lidas

não se aplica

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | leitura | Configuração Spring Boot | Arquivo de configuração de logs (diferentes versões por ambiente: des, qa, uat, prd) |
| application.yml | leitura | Configuração Spring Boot | Arquivo principal de configuração da aplicação |
| *.xsd (camt.025, pacs.002, pacs.008, pain.013, pain.014, trck.002) | leitura | Plugin JAXB2 Maven | Schemas XSD para geração de classes Java via JAXB |
| sboot-tratar-mensagem.yaml | leitura | Plugin Swagger Codegen | Especificação OpenAPI para geração de interfaces REST |

## 10. Filas Lidas

**Google Cloud Pub/Sub Subscriptions:**

| Nome da Subscription | Descrição |
|---------------------|-----------|
| business-spag-pixx-receber-mensagem-spi-sub | Mensagens recebidas do SPI para BV |
| business-spag-pixx-receber-mensagem-spi-bvsa-sub | Mensagens recebidas do SPI para BVSA |
| business-spag-pixx-receber-mensagem-spi-ba-sub | Mensagens recebidas do SPI para ACESSO/Bankly |
| business-spag-pixx-mensagem-spi-assinar-sub | Mensagens para assinatura digital |
| business-cpix-base-mensagem-spi-assinar-spib-sub | Mensagens CPIX para assinatura |
| business-spag-pixx-receber-mensagem-spi-canal-secundario-sub | Mensagens do canal secundário |
| business-spag-pixx-mensagem-secundario-spi-assinar-bv-pacs008-sub | PACS.008 canal secundário BV |
| business-spag-pixx-mensagem-secundario-spi-assinar-bvsa-pacs008-sub | PACS.008 canal secundário BVSA |
| business-spag-pixx-mensagem-secundario-spi-assinar-ba-pacs008-sub | PACS.008 canal secundário ACESSO |
| business-spag-pixx-mensagem-secundario-spi-assinar-bv-pacs002-sub | PACS.002 canal secundário BV |
| business-spag-pixx-mensagem-secundario-spi-assinar-bvsa-pacs002-sub | PACS.002 canal secundário BVSA |
| business-spag-pixx-mensagem-secundario-spi-assinar-ba-pacs002-sub | PACS.002 canal secundário ACESSO |
| business-cpix-base-mensagem-secundario-spi-assinar-bv-pain014-spib-sub | PAIN.014 canal secundário BV |
| business-cpix-base-mensagem-secundario-spi-assinar-bvsa-pain014-spib-sub | PAIN.014 canal secundário BVSA |
| business-cpix-base-mensagem-secundario-spi-assinar-ba-pain014-spib-sub | PAIN.014 canal secundário ACESSO |
| business-spag-pixx-mensagem-secundario-spi-assinar-pibr001-sub | PIBR.001 (echo) canal secundário |
| business-spag-pixx-mensagem-secundario-assinar-trck002-sub | TRCK.002 canal secundário |

## 11. Filas Geradas

**Google Cloud Pub/Sub Topics:**

| Nome do Topic | Descrição |
|--------------|-----------|
| business-spag-pixx-envio-mensagem-spi | Mensagens assinadas para envio ao SPI (BV) |
| business-spag-pixx-envio-mensagem-spi-bvsa | Mensagens assinadas para envio ao SPI (BVSA) |
| business-spag-pixx-envio-mensagem-spi-ba | Mensagens assinadas para envio ao SPI (ACESSO) |
| business-spag-pixx-receber-pagamento | Pagamentos recebidos (PACS.008) |
| business-spag-pixx-receber-pagamento-canal-secundario | Pagamentos recebidos via canal secundário |
| business-spag-pixx-agendamento-pix-automatico | Agendamentos PIX automático (PAIN.013) |
| business-spag-pixx-recebe-detalhe-lancamento | Detalhes de lançamento (CAMT.054) |
| business-spag-pixx-receber-devolucao-pagamento | Devoluções de pagamento (PACS.004) |
| business-spag-pixx-recebe-aviso-remuneracao | Avisos de remuneração |
| business-spag-pixx-remuneracao-solicitada-conta-pi | Remuneração solicitada |
| business-spag-pixx-recebe-saldo-conta-pi | Saldo da conta PI (CAMT.053) |
| business-spag-pixx-recebe-lancamentos-participante | Lançamentos do participante (CAMT.052) |
| business-spag-pixx-conciliacao-pagamento-detalhe-pagamento | Rescaldo/conciliação |
| business-spag-pixx-aviso-operacao-spi | Avisos de operação (ADMI.004, CAMT.014, REDA.017, REDA.041) |
| business-spag-pixx-confirmar-envio-pagamento | Confirmação de envio (PACS.002) |
| business-spag-pixx-confirmar-envio-pagamento-canal-secundario | Confirmação via canal secundário |
| business-spag-pixx-erro-envio-pagamento | Erros de envio de pagamento |
| business-spag-pixx-erro-envio-devolucao | Erros de envio de devolução |
| business-spag-pixx-erro-recepcao-pagamento | Erros de recepção de pagamento |
| business-spag-pixx-erro-recepcao-devolucao | Erros de recepção de devolução |
| business-spag-pixx-erro-mensagem | Erros gerais de mensagem (ADMI.002) |
| business-spag-pixx-retorno-atualizacao-conta-pi | Retorno de atualização de conta PI (REDA.016) |
| business-spag-pixx-envio-mensagem-secundario-spi | Mensagens assinadas do canal secundário |
| business-spag-pixx-atualizar-dados-pacs-secundario | Atualização de dados PACS secundário |
| business-spag-pixx-solic-pix-automatico | Solicitação PIX automático (PAIN.009) |
| business-spag-pixx-cancelamento-agendamento | Cancelamento de agendamento (CAMT.055) |
| business-spag-pixx-autorizacao-pix-automatico | Autorização PIX automático (PAIN.012) |
| business-spag-pixx-cancelamento-pix-automatico | Cancelamento PIX automático (PAIN.011, CAMT.029) |
| business-spag-pixx-atualizar-controle-mensagem | Atualização de controle de mensagem (PAIN.014) |
| business-spag-pixx-confirmacao-cancelamento-agendamento | Confirmação de cancelamento |
| business-spag-pixx-mensagem-retorno-transacao-interna | Retorno de transação interna (CAMT.025) |

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|----------------|------|-----------|
| Banco Central do Brasil (SPI) | API/Mensageria | Recepção e envio de mensagens PIX via protocolo ISO 20022 |
| Dinamo HSM | Hardware/API | Hardware Security Module para assinatura e validação de certificados digitais (hosts: hsmcertpixuat.bvnet.bv em UAT, configurável por ambiente) |
| Google Cloud Pub/Sub | Mensageria | Sistema de mensageria para comunicação assíncrona entre microserviços |
| RabbitMQ | Mensageria | Message broker configurado (mas não ativamente utilizado no fluxo principal) |
| Feature Toggle Service | API | Serviço de feature toggles para controle de versões de catálogo |

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com uso de padrões como Repository, Service e Processor
- Uso adequado de frameworks consolidados (Spring Boot, Apache Camel)
- Implementação de segurança com HSM para assinatura digital
- Tratamento de múltiplos ISPBs de forma organizada
- Uso de Lombok para redução de boilerplate
- Configuração externalizada por ambiente
- Logs estruturados e informativos

**Pontos de Melhoria:**
- Algumas classes com múltiplas responsabilidades (ex: RouterConstants com muitas constantes e lógica)
- Código com alto acoplamento ao Apache Camel, dificultando testes unitários
- Falta de documentação JavaDoc em várias classes críticas
- Alguns métodos muito extensos (ex: configure() nos routers)
- Uso de strings literais em vários pontos ao invés de constantes
- Tratamento de exceções genérico em alguns pontos
- Falta de validações de entrada em alguns processadores
- Configuração de HSM com credenciais em variáveis de ambiente (boa prática), mas sem rotação aparente
- Alguns processadores com lógica de negócio complexa que poderia ser extraída para services

O código é funcional e bem estruturado em sua arquitetura geral, mas poderia se beneficiar de refatorações para melhorar testabilidade, manutenibilidade e documentação.

## 14. Observações Relevantes

1. **Segurança**: O sistema utiliza HSM (Hardware Security Module) da Dinamo Networks para todas as operações de assinatura e validação de certificados digitais, garantindo alto nível de segurança nas comunicações com o Banco Central.

2. **Multi-tenancy**: O sistema suporta três ISPBs distintos (BV, BVSA e ACESSO/Bankly), cada um com suas próprias credenciais e certificados no HSM.

3. **Canal Secundário**: Implementa otimização de comunicação através de agrupamento de mensagens PACS.008, PACS.002 e PAIN.014 antes do envio, reduzindo overhead de comunicação.

4. **Versionamento de Catálogo**: Suporta transição entre versões de catálogo de mensagens (v5.11 e v5.11.1) através de feature toggles, permitindo migração gradual.

5. **Processamento Assíncrono**: Todo o processamento é assíncrono via Google Cloud Pub/Sub, garantindo escalabilidade e resiliência.

6. **Controle de Throughput**: Ajusta dinamicamente a quantidade de mensagens processadas conforme o período do dia (diurno vs noturno).

7. **Namespace Handling**: Implementa filtro customizado de namespaces XML (NamespaceFilter) para lidar com diferentes versões de schemas.

8. **Geração de Código**: Utiliza JAXB para geração automática de classes Java a partir de schemas XSD e Swagger Codegen para interfaces REST.

9. **Monitoramento**: Expõe métricas via Actuator (porta 9090) incluindo Prometheus para observabilidade.

10. **Ambiente**: Configurado para múltiplos ambientes (local, des, uat, prd) com configurações específicas por ambiente.