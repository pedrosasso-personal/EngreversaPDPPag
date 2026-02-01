# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-spag-base-orch-write-off-request-cancel** é um serviço orquestrador responsável por gerenciar o cancelamento de solicitações de baixa de boletos no contexto do sistema de pagamentos (SPAG) do Banco Votorantim. 

O componente atua como intermediário entre diversos sistemas, realizando validações de segurança, horário de grade da câmara, consulta de informações de boletos, validação de ISPBs e envio de mensagens para o sistema DDA (Débito Direto Autorizado) via filas IBM MQ. O fluxo principal envolve buscar informações do boleto, validar cliente e horários, verificar se a operação é intrabancária e, caso aprovado, enviar a solicitação de cancelamento para o SPB (Sistema de Pagamentos Brasileiro) aguardando resposta via fila.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `WriteOffRequestCancelController` | Controlador REST que expõe endpoints para busca de informações de boleto e cancelamento de baixa |
| `WriteOffRequestCancelService` | Serviço de domínio que orquestra o fluxo de cancelamento e recebimento de mensagens |
| `WriteOffRequestCancelRouter` | Roteador Apache Camel que define as rotas de processamento (validação de segurança, horário, busca de boleto, validação de bancos) |
| `WriteOffRequestCancelRepositoryImpl` | Implementação de repositório que integra com APIs externas (SPAG, PGFT, Segurança, SITP, Lista de Bancos, Roteador DDA) |
| `MessageQueueRepositoryImpl` | Repositório responsável por receber mensagens de filas IBM MQ com seletores |
| `BarcodeValidationProcessor` | Processador Camel que valida código de barras do boleto |
| `BilletInfoValidationProcessor` | Processador que valida informações do boleto e ISPBs, verificando operações intrabancárias |
| `SecurityValidationProcessorInit` | Processador que prepara dados para validação de segurança do cliente |
| `TimetableProcessor` | Processador que valida se a operação está dentro do horário permitido da grade da câmara |
| `WriteOffRequestCancelMapper` | Mapper para conversão entre objetos de domínio e representações REST |

## 3. Tecnologias Utilizadas

- **Java 11** - Linguagem de programação
- **Spring Boot 2.x** - Framework principal
- **Spring Security OAuth2** - Segurança e autenticação JWT
- **Apache Camel 3.0.1** - Framework de integração e roteamento
- **IBM MQ (JMS)** - Middleware de mensageria
- **RestTemplate** - Cliente HTTP para integrações REST
- **Swagger/OpenAPI 3.0** - Documentação de APIs
- **Lombok** - Redução de boilerplate
- **Micrometer/Prometheus** - Métricas e monitoramento
- **Logback** - Framework de logging
- **JUnit 5 + Mockito** - Testes unitários
- **Maven** - Gerenciamento de dependências
- **Docker** - Containerização
- **Grafana** - Visualização de métricas

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/find/{barcode}/{protocol}` | `WriteOffRequestCancelController` | Busca informações de um boleto pelo código de barras e protocolo |
| PUT | `/v1/request-cancel` | `WriteOffRequestCancelController` | Solicita o cancelamento de uma baixa de boleto |

## 5. Principais Regras de Negócio

1. **Validação de Cliente**: Se informado código de origem, valida se o cliente (CNPJ) tem permissão para realizar a operação através do serviço de segurança
2. **Validação de Horário**: Verifica se a solicitação está dentro da grade horária da câmara de liquidação (até 2 horas após o fim da grade)
3. **Busca de Boleto**: Tenta buscar informações do boleto primeiro no SPAG, se não encontrar busca no PGFT
4. **Validação de Código de Barras**: Valida e converte linha digitável (47 posições) para código de barras (44 posições) quando necessário
5. **Validação Intrabancária**: Verifica ISPBs do favorecido e remetente, impedindo cancelamento se ambos forem do Banco Votorantim (ISPBs: 59588111, 1858774)
6. **Envio para SPB**: Envia mensagem DDA0115 para fila do SPB com informações do cancelamento
7. **Recebimento de Resposta**: Aguarda resposta da fila com timeout configurável, validando se retornou DDA0115R1 (sucesso) ou DDA0115E (erro)
8. **Tratamento de Erros DDA**: Interpreta códigos de erro do DDA (ex: EDDA0076, EDDA0800) e retorna mensagens amigáveis

## 6. Relação entre Entidades

**Entidades Principais:**

- **WriteOffCancelRequest**: Entidade de entrada contendo barcode, protocol, originCode e document
- **BilletInfo**: Informações do boleto (writeOffIdentifier, payment, ispb, financialInstitution)
  - Contém **PaymentInfo**: date, value, bondCode, barcode
  - Contém **IspbInfo**: mainReceiver, administeredReceiver, senderCode, payeeCode
  - Contém **FinancialInstitution**: sender, payee
- **WriteOffCancelInfo**: Informações enviadas para cancelamento (ispbPartRecbdrAdmtd, ispbPartRecbdrPrincipal, dtMovto, numCtrlPart, dtHrCanceltBaixa, numIdentcBaixa)
- **Bank**: Informações de bancos do BACEN (ordem, identificador, codigoBanco, nome, codigoIspb)
- **TimeTableResponse**: Resposta de horário da câmara (codigoLiquidacao, horaInicioGradeCamara, horaFimGradeCamara)
- **ClientRepresentation**: Dados do cliente para validação (cnpj, codigoOrigem)

**Relacionamentos:**
- WriteOffCancelRequest → BilletInfo (1:1) - busca informações do boleto
- BilletInfo → WriteOffCancelInfo (1:1) - transformação para envio ao SPB
- BilletInfo → Bank (N:1) - validação de ISPBs contra lista de bancos

## 7. Estruturas de Banco de Dados Lidas

não se aplica

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot | Arquivo de configuração principal da aplicação |
| application-local.yml | leitura | Spring Boot | Configurações específicas do ambiente local |
| logback-spring.xml | leitura | Logback | Configuração de logs da aplicação |
| sboot-spag-base-orch-write-off-request-cancel.yml | leitura | Swagger Codegen | Especificação OpenAPI dos endpoints |

## 10. Filas Lidas

| Nome da Fila | Tecnologia | Classe Responsável | Descrição |
|--------------|-----------|-------------------|-----------|
| QL.SPAG.RETORNO_SOL_BAIXA.RSP | IBM MQ (JMS) | `MessageQueueRepositoryImpl` | Fila de retorno das solicitações de cancelamento de baixa enviadas ao SPB. Utiliza seletor JMS com filtro `numCtrlPart` para receber mensagens específicas |

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Responsável | Descrição |
|--------------|-----------|-------------------|-----------|
| QL.SPAG.BANCO_LIQUIDANTE_RECEBIMENTO_REQ.INT | IBM MQ (JMS) | Serviço externo (Roteador DDA) | Fila de envio de solicitações de cancelamento para o SPB (enviada indiretamente via API do roteador DDA) |

## 12. Integrações Externas

| Sistema/API | Tipo | Descrição |
|-------------|------|-----------|
| sboot-spag-base-atom-write-off-request-cancel | REST | Busca informações de boleto no sistema SPAG pelo código de barras e protocolo |
| sboot-spag-base-atom-registra-boleto | REST | Busca informações de boleto no sistema PGFT pelo protocolo ITP |
| sboot-spag-base-atom-seguranca | REST | Valida permissões do cliente (CNPJ + código origem) |
| sboot-sitp-base-atom-integrar-pagamento | REST | Consulta horário da grade da câmara de liquidação |
| sboot-glob-base-atom-lista-bancos | REST | Obtém lista de bancos do BACEN com códigos ISPB |
| sboot-spbb-base-atom-dda-router | REST | Envia solicitação de cancelamento de baixa para o roteador DDA/SPB |
| IBM MQ | JMS | Recebe respostas assíncronas das solicitações de cancelamento |

## 13. Avaliação da Qualidade do Código

**Nota: 7,5/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (presentation, domain, infrastructure)
- Uso adequado de padrões como Repository, Service e Mapper
- Implementação de testes unitários para as principais classes
- Uso de Apache Camel para orquestração de fluxos complexos de forma declarativa
- Configuração externalizada e separada por ambiente
- Tratamento de exceções customizado com enum de razões
- Uso de Lombok para reduzir boilerplate
- Documentação OpenAPI/Swagger bem estruturada

**Pontos de Melhoria:**
- Presença de strings hardcoded em vários locais (ex: ISPBs dos bancos, mensagens de erro)
- Classe `Util` com métodos estáticos que dificultam testes e violam princípios OO
- Falta de validação de entrada em alguns endpoints
- Timeout de fila configurável mas com lógica de retry limitada
- Logs em português misturados com código em inglês
- Algumas classes de domínio DDA geradas automaticamente com comentários em português mal formatados
- Falta de documentação inline em métodos mais complexos
- Conversão de código de barras poderia estar em classe utilitária específica
- Tratamento de exceções poderia ser mais granular em alguns fluxos

O código demonstra maturidade arquitetural e boas práticas, mas há espaço para melhorias em aspectos como internacionalização, tratamento de erros e organização de constantes.

## 14. Observações Relevantes

1. **Dependência de Múltiplos Sistemas**: O componente depende de 6 sistemas externos diferentes, o que pode impactar disponibilidade e performance. Recomenda-se implementar circuit breakers e fallbacks.

2. **Processamento Síncrono com Fila**: O fluxo aguarda resposta síncrona de uma fila assíncrona, o que pode causar timeouts. O timeout padrão é de 10 segundos.

3. **Validação Intrabancária**: A lógica que impede cancelamento intrabancário está hardcoded com ISPBs específicos do Banco Votorantim, dificultando manutenção.

4. **Segurança**: O sistema utiliza OAuth2 com JWT para autenticação, mas a validação de cliente é opcional (apenas se originCode for informado).

5. **Mensagens DDA**: O sistema trabalha com mensagens XML do padrão DDA do SPB (Sistema de Pagamentos Brasileiro), seguindo especificações do Banco Central.

6. **Ambientes**: Configurado para 4 ambientes (des, qa, uat, prd) com variáveis específicas para cada um.

7. **Monitoramento**: Possui integração completa com Prometheus/Grafana para observabilidade, incluindo métricas de JVM, HTTP, HikariCP e logs.

8. **Containerização**: Aplicação preparada para execução em containers Docker/OpenShift com configurações de health check e recursos.