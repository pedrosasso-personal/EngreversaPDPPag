# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema orquestrador de baixa operacional de boletos desenvolvido em Java com Spring Boot e Apache Camel. O sistema é responsável por processar solicitações de baixa de boletos CIP (Câmara Interbancária de Pagamentos), realizando validações, integrações com sistemas externos e publicando eventos de retorno do processamento. Utiliza arquitetura baseada em mensageria (Google Cloud Pub/Sub) para comunicação assíncrona e orquestração de fluxos de negócio através do Apache Camel.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal de inicialização do Spring Boot |
| `BaixaOperacionalService` | Serviço de domínio que orquestra o fluxo de baixa de boletos |
| `BaixaOperacionalRouter` | Roteador Camel principal que define o fluxo de orquestração |
| `ValidacaoPagamentoRouter` | Roteador Camel para validação de pagamentos |
| `RegistraBoletoRouter` | Roteador Camel para registro de boletos em contingência |
| `RetornoProcessoPagamentoBoletoRouter` | Roteador Camel para publicação de eventos de retorno |
| `BaixaOperacionalBoletoSubscriber` | Subscriber que consome mensagens da fila de baixa operacional |
| `BaixaOperacionalClientImpl` | Cliente HTTP para integração com ACL de baixa operacional |
| `ValidacaoPagamentoClientImpl` | Cliente HTTP para integração com serviço de validação de pagamento |
| `RegistraBoletoClientImpl` | Cliente HTTP para integração com serviço de registro de boletos |
| `RetornoProcessoPagamentoBoletoPublisherImpl` | Publisher que publica eventos de retorno na fila |
| `BaixaOperacionalCallbackProcessor` | Processor Camel que valida grade horária e data de movimento |
| `BaixarBoletoCallbackProcessor` | Processor Camel que determina tipo de baixa (CIP ou contingência) |
| `DadosPagamentoBoletoCallbackProcessor` | Processor Camel que prepara dados para consulta de boleto |
| `BaixaBoletoCipCallbackProcessor` | Processor Camel que prepara atualização de status da baixa |
| `ExceptionCallbackProcessor` | Processor Camel para tratamento de exceções |
| `RetornoProcessoPagamentoBoletoCallbackProcessor` | Processor Camel que prepara payload de retorno |

## 3. Tecnologias Utilizadas

- **Framework Principal**: Spring Boot 2.x
- **Orquestração**: Apache Camel 3.0.1
- **Mensageria**: Google Cloud Pub/Sub (Spring Cloud GCP 2.0.4)
- **Integração**: Spring Integration 5.5.12
- **Documentação API**: Springfox Swagger 3.0.0
- **Mapeamento de Objetos**: MapStruct 1.3.1
- **Segurança**: Spring Security JWT
- **Auditoria**: BV Trilha Auditoria 2.3.2
- **Monitoramento**: Spring Boot Actuator, Micrometer Prometheus
- **Testes**: JUnit 5, Mockito, Rest Assured, Pact JVM
- **Build**: Maven 3.3+
- **Java**: JDK 11
- **Containerização**: Docker
- **Infraestrutura**: Google Cloud Platform (GCP), Kubernetes

## 4. Principais Endpoints REST

não se aplica

(O sistema não expõe endpoints REST próprios, apenas consome de outros serviços)

## 5. Principais Regras de Negócio

1. **Validação de Grade Horária**: Verifica se o pagamento está dentro da grade horária da câmara de liquidação antes de processar
2. **Validação de Data de Movimento**: Valida se a data do movimento é igual à data atual
3. **Determinação de Tipo de Baixa**: Define se a baixa será via CIP ou contingência baseado no tipo de validação do boleto
4. **Controle de Status de Baixa**: Gerencia os estados do lançamento (Em Processamento, Confirmado, Rejeitado, Com Erro)
5. **Processamento Condicional**: Só realiza baixa se o boleto não foi previamente baixado
6. **Tratamento de Erros**: Diferencia erros de negócio (validação) de erros técnicos (infraestrutura)
7. **Publicação de Eventos**: Publica eventos de sucesso, rejeição ou falha do processamento
8. **Atualização de Status**: Atualiza status da baixa em diferentes momentos do fluxo (em processamento, confirmada, com erro)

## 6. Relação entre Entidades

**Entidades Principais:**

- `BaixarBoletoCipPayload`: Payload principal contendo dados da solicitação de baixa
  - Contém: `codigoLancamento`, `dataMovimento`, `camaraLiquidacao`, `valorPagamento`, `portador`, `remetente`, `boleto`, `boletoCalculado`, `tipoValidacaoBoleto`
  
- `CamaraLiquidacao`: Dados da câmara de liquidação
  - Contém: `codigoLiquidacao`, `horaInicioGradeCamara`, `horaFimGradeCamara`

- `Pessoa`: Dados de pessoa (portador)
  - Contém: `tipoPessoa`, `numeroCpfCnpj`, `nome`

- `Cliente`: Estende Pessoa, adiciona conta
  - Contém: `conta` (ContaCliente)

- `ContaCliente`: Dados da conta
  - Contém: `codigoBancoCompe`, `numeroAgencia`, `numeroConta`

- `Boleto`: Dados do boleto
  - Contém: `codigoDeBarras`, `valor`, `dataVencimento`

- `BoletoCalculado`: Dados calculados do boleto
  - Contém: `numeroIdentificacaoTitulo`, `codigoEspecieTitulo`, `dataVencimentoTitulo`, `indicadorBoletoParcial`, `listaBaixaOperacional`

- `BaixaBoletoCip`: Resultado da consulta de baixa
  - Contém: `boletoBaixado`, `situacaoLancamento`

- `RetornoProcessoPagamentoBoletoPayload`: Payload de retorno
  - Contém: `payload` (SucessoPayload, ErroNegocioPayload ou ErroTecnicoPayload), `tipoEvento`

**Relacionamentos:**
- BaixarBoletoCipPayload 1 --- 1 CamaraLiquidacao
- BaixarBoletoCipPayload 1 --- 0..1 Pessoa (portador)
- BaixarBoletoCipPayload 1 --- 1 Cliente (remetente)
- Cliente 1 --- 1 ContaCliente
- BaixarBoletoCipPayload 1 --- 1 Boleto
- BaixarBoletoCipPayload 1 --- 0..1 BoletoCalculado
- BoletoCalculado 1 --- * BaixaTitulo

## 7. Estruturas de Banco de Dados Lidas

não se aplica

(O sistema não acessa diretamente banco de dados, apenas consome APIs REST)

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

(O sistema não acessa diretamente banco de dados, apenas consome APIs REST)

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot | Arquivo de configuração da aplicação |
| logback-spring.xml | leitura | Logback | Configuração de logs da aplicação |
| sboot-spag-base-acl-baixa-operacional.yaml | leitura | Swagger Codegen | Especificação OpenAPI do serviço de baixa operacional |
| sboot-spag-base-atom-registra-boleto.yaml | leitura | Swagger Codegen | Especificação OpenAPI do serviço de registro de boletos |
| sboot-spag-base-atom-validacao-pagamento.yaml | leitura | Swagger Codegen | Especificação OpenAPI do serviço de validação de pagamento |

## 10. Filas Lidas

| Nome da Fila | Tecnologia | Classe Responsável | Descrição |
|--------------|-----------|-------------------|-----------|
| business-spag-baixa-operacional-boleto-sub | Google Cloud Pub/Sub | BaixaOperacionalBoletoSubscriber | Fila de entrada para solicitações de baixa operacional de boletos |

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Responsável | Descrição |
|--------------|-----------|-------------------|-----------|
| business-spag-retorno-processo-pagamento-boleto | Google Cloud Pub/Sub | RetornoProcessoPagamentoBoletoPublisherImpl | Fila de saída para publicação de eventos de retorno do processamento (sucesso, rejeição ou falha) |

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| sboot-spag-base-atom-validacao-pagamento | REST API | Serviço de validação de pagamento - consulta status de baixa CIP, obtém informações completas do boleto e atualiza status da baixa |
| sboot-spag-base-atom-registra-boleto | REST API | Serviço de registro de boletos - registra boletos em modo contingência |
| sboot-spag-base-acl-baixa-operacional | REST API | ACL (Anti-Corruption Layer) para baixa operacional - realiza a baixa efetiva do boleto na CIP |
| API Gateway BV | OAuth2 | Gateway de autenticação para obtenção de tokens JWT para chamadas aos serviços |

## 13. Avaliação da Qualidade do Código

**Nota: 8.0**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões hexagonais (ports/adapters)
- Separação clara de responsabilidades em módulos (common, domain, application)
- Uso adequado de padrões de projeto (Strategy, Template Method via Camel)
- Boa cobertura de testes unitários e de integração
- Uso de frameworks consolidados (Spring Boot, Apache Camel)
- Configuração externalizada e parametrizada por ambiente
- Tratamento de exceções estruturado
- Uso de MapStruct para mapeamento de objetos
- Documentação via Swagger/OpenAPI
- Logs estruturados e informativos

**Pontos de Melhoria:**
- Alguns processadores Camel poderiam ter lógica mais simplificada
- Falta documentação JavaDoc em algumas classes importantes
- Alguns métodos poderiam ser quebrados em métodos menores para melhor legibilidade
- Configurações hardcoded em alguns pontos (ex: timeouts, retries)
- Poderia ter mais validações de entrada nos payloads
- Falta tratamento de circuit breaker para chamadas externas

## 14. Observações Relevantes

1. **Arquitetura Event-Driven**: O sistema utiliza arquitetura orientada a eventos com Google Cloud Pub/Sub, garantindo processamento assíncrono e desacoplamento

2. **Orquestração com Apache Camel**: Uso extensivo do Apache Camel para orquestração de fluxos complexos de negócio, facilitando manutenção e evolução

3. **Ambientes Múltiplos**: Configuração preparada para múltiplos ambientes (local, des, qa, uat, prd) com parametrização adequada

4. **Monitoramento**: Integração com Prometheus e Grafana para observabilidade, com dashboards pré-configurados

5. **Segurança**: Uso de OAuth2/JWT para autenticação nas chamadas aos serviços externos

6. **Containerização**: Aplicação preparada para execução em containers Docker e deploy em Kubernetes/OpenShift

7. **Auditoria**: Integração com biblioteca de trilha de auditoria do Banco Votorantim

8. **Testes**: Estrutura completa de testes (unitários, integração, funcionais) com uso de Pact para testes de contrato

9. **CI/CD**: Configuração para pipeline Jenkins com propriedades específicas

10. **Padrão de Nomenclatura**: Seguindo padrão do Banco Votorantim (sboot-spag-base-orch-*)

11. **Versionamento**: Sistema versionado (0.4.0) seguindo semantic versioning

12. **Dependências Gerenciadas**: Uso de BOM (Bill of Materials) do Spring Cloud para gerenciamento de versões