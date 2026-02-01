# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema stateful desenvolvido em Spring Boot com Camunda BPM para notificar parceiros comerciais sobre a geração de contratos de financiamento Flex. O sistema consome mensagens de uma fila JMS (IBM MQ) contendo informações de contratos gerados, executa um processo BPMN que obtém parâmetros do parceiro, bloqueia a impressão de carnê na gráfica e notifica o parceiro através de uma API REST. Em caso de erros, envia e-mails de notificação para a equipe de sustentação.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot que inicializa a aplicação |
| `ContratoNotificarParceiroJmsListener` | Listener JMS que recebe mensagens de retorno de contrato e inicia o processo Camunda |
| `ObterParametrosServicoDelegate` | Delegate que consulta dados de acesso do parceiro comercial |
| `BloquearRegistroImpressaoGraficaDelegate` | Delegate que bloqueia registro e impressão de carnê na gráfica |
| `NotificarParceiroDelegate` | Delegate que notifica o parceiro sobre a geração do contrato |
| `EnviarEmailSustentacaoDelegate` | Delegate que envia e-mail de notificação de erro para sustentação |
| `ContratoNotificarParceiroIncidentHandler` | Handler customizado de incidentes do Camunda para tratamento de erros |
| `AcessoDadosSistemasParceirosService` | Serviço de domínio para consultar dados de acesso de parceiros |
| `BoletoFinanciamentoFlexService` | Serviço de domínio para operações de boleto/carnê |
| `ContratoNotificarParceiroService` | Serviço de domínio para notificação de parceiros |
| `EnviaEmailService` | Serviço de domínio para envio de e-mails |

---

## 3. Tecnologias Utilizadas

- **Framework:** Spring Boot 2.2.1
- **Motor BPMN:** Camunda BPM 3.4.0
- **Mensageria:** IBM MQ (JMS)
- **Banco de Dados:** Microsoft SQL Server (produção), H2 (desenvolvimento)
- **Autenticação:** OAuth 2.0 (client credentials)
- **Web Services:** SOAP (JAX-WS), REST (RestTemplate)
- **Segurança:** Spring Security, WS-Security
- **Monitoramento:** Spring Actuator, Micrometer, Prometheus
- **Documentação:** Swagger/OpenAPI
- **Build:** Maven
- **Container:** Docker
- **Orquestração:** Kubernetes/OpenShift
- **Logging:** Logback com formato JSON
- **Testes:** JUnit 5, Mockito, Rest Assured, Pact

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| N/A | N/A | N/A | Sistema não expõe endpoints REST próprios, apenas consome APIs externas e utiliza endpoints do Camunda REST API |

**Observação:** O sistema utiliza os endpoints padrão do Camunda REST API disponíveis em `/rest/*` para gerenciamento de processos.

---

## 5. Principais Regras de Negócio

1. **Processamento de Mensagem de Contrato:** Ao receber mensagem JMS com dados de contrato gerado, inicia processo BPMN de notificação
2. **Consulta de Parâmetros do Parceiro:** Obtém endpoint e chave de acesso do parceiro comercial através de serviço SOAP
3. **Bloqueio de Impressão:** Bloqueia registro e impressão de carnê na gráfica para evitar duplicidade
4. **Notificação do Parceiro:** Envia notificação REST ao parceiro com código de retorno (S=sucesso, E=erro) e lista de inconsistências se houver
5. **Tratamento de Erros:** Em caso de falha em qualquer etapa, após esgotadas as tentativas (5 retries com intervalo de 3 minutos), envia e-mail para sustentação
6. **Retry Automático:** Sistema possui mecanismo de retry configurável (R5/PT3M) para todas as tarefas assíncronas
7. **Incident Handling:** Handler customizado intercepta incidentes do Camunda e dispara sinal para envio de e-mail de notificação

---

## 6. Relação entre Entidades

**Entidades de Domínio:**

- `ContratoNotificarParceiroDomain`: Entidade principal com id e version
- `DadosAcessoParceiroDomain`: Contém endpointUri e chaveAcesso do parceiro
- `NotificacaoParceiroDomain`: Dados para notificação (endpoint, chave, código contrato, código retorno, lista de inconsistências)
- `InconsistenciaDomain`: Representa erro de negócio (codigoErro, descricaoErro)

**Relacionamentos:**
- `NotificacaoParceiroDomain` possui lista de `InconsistenciaDomain` (1:N)
- `DadosAcessoParceiroDomain` é consultado e seus dados são utilizados em `NotificacaoParceiroDomain`

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| Tabelas do schema Camunda | tabela | SELECT | Leitura de dados de processos, instâncias, variáveis e histórico do Camunda BPM |

**Observação:** O sistema utiliza o banco de dados principalmente para persistência do estado do Camunda. O schema utilizado é `flexgeracaocontrato`.

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| Tabelas do schema Camunda | tabela | INSERT/UPDATE | Atualização de estado de processos, tarefas, variáveis e incidentes do Camunda BPM |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | leitura | /usr/etc/log | Arquivo de configuração de logs em formato JSON |
| application.yml | leitura | src/main/resources | Arquivo de configuração da aplicação Spring Boot |
| contrato-notificar-parceiro.bpmn | leitura | src/main/resources/bpmn | Definição do processo BPMN de notificação |
| MensagemContratoRetorno_v2.xsd | leitura | src/main/resources/jms | Schema XSD para validação de mensagens JMS |

---

## 10. Filas Lidas

**Fila:** `QL.FLEX.GERAR_CONTRATO_RETORNO.INT`
- **Tipo:** IBM MQ (JMS)
- **Classe Consumidora:** `ContratoNotificarParceiroJmsListener`
- **Descrição:** Fila que recebe mensagens de retorno da geração de contratos contendo: numeroContrato, numeroOrigem, codigoParceiroComercial, codigoStatusPagamento e listaInconsistencias
- **Queue Manager:** QM.VAR.01
- **Channel:** FLEX.SRVCONN

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| AcessoSistemasParceirosTechnicalService | SOAP | Consulta dados de acesso (endpoint e chave) dos parceiros comerciais |
| BoletoFinanciamentoFlexBusinessService | SOAP | Bloqueia impressão de carnê na gráfica |
| API Notificar Parceiro | REST OAuth2 | Notifica parceiro sobre geração do contrato via POST em endpoint parametrizado |
| API Envio Email Corporativo | REST OAuth2 | Envia e-mails de notificação de erro para equipe de sustentação |
| IBM MQ | JMS | Consome mensagens de retorno de geração de contrato |
| API Gateway OAuth | REST | Obtém token OAuth2 para autenticação nas APIs REST |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (application, domain, common)
- Uso adequado de padrões como Ports & Adapters (hexagonal)
- Configuração externalizada e parametrizada por ambiente
- Tratamento de erros estruturado com retry automático e notificação
- Uso de Lombok para reduzir boilerplate
- Testes unitários presentes
- Documentação via Swagger
- Logs estruturados em JSON

**Pontos de Melhoria:**
- Algumas classes de delegate poderiam ter mais validações de entrada
- Falta de tratamento mais granular de exceções em alguns pontos
- Código de mapeamento entre objetos poderia ser extraído para mappers dedicados
- Alguns métodos longos que poderiam ser refatorados (ex: `toRequestBody` em `ContratoNotificarParceiroClientImpl`)
- Falta de documentação JavaDoc em várias classes
- Testes de integração e funcionais estão vazios/incompletos
- Configuração de segurança muito permissiva (disable CSRF, anonymous access)

---

## 14. Observações Relevantes

1. **Tenant ID:** O sistema utiliza tenant "contrato-notificar-parceiro" para isolamento no Camunda
2. **Retry Strategy:** Configurado para 5 tentativas com intervalo de 3 minutos (R5/PT3M)
3. **Incident Handling Customizado:** Implementa handler próprio para interceptar falhas e disparar notificações
4. **Múltiplos Ambientes:** Suporta perfis des, qa, uat e prd com configurações específicas
5. **Monitoramento:** Expõe métricas Prometheus na porta 9090
6. **Segurança WS:** Utiliza WS-Security para autenticação em serviços SOAP
7. **OAuth2:** Implementa fluxo client_credentials para APIs REST
8. **Geração de Código:** Utiliza plugins Maven para gerar código a partir de WSDL (SOAP) e Swagger (REST)
9. **Arquitetura de Plugins:** Utiliza plugin customizado do Camunda para tratamento de incidentes
10. **Infraestrutura como Código:** Possui arquivo infra.yml para deploy em Kubernetes/OpenShift