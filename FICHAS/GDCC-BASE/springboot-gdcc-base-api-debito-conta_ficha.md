# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de gestão de débito em conta corrente desenvolvido em Spring Boot. O sistema gerencia autorizações de débito, incluindo operações de autenticação, inclusão, cancelamento e consulta de débitos em contas bancárias. Funciona como uma API intermediária que recebe requisições REST, processa regras de negócio relacionadas a autorizações de débito e publica mensagens em filas JMS (IBM MQ) para processamento assíncrono. Também consome filas de retorno para notificar sistemas de origem sobre o resultado das operações.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Server.java** | Classe principal que inicializa a aplicação Spring Boot |
| **ConsultarAutorizacaoServices** | Serviço de negócio para consulta de autorizações de débito |
| **NotificacaoDebitoContaBusiness** | Processa notificações de callback para sistemas de origem |
| **ListaBancoConveniadosService** | Lista bancos conveniados para débito |
| **SistemaOrigemService** | Gerencia informações de sistemas de origem |
| **AutenticarDebitoContaAPI** | Controller REST para autenticação de débito |
| **InclusaoDebitoApi** | Controller REST para inclusão de débito |
| **CancelamentoDebitoApi** | Controller REST para cancelamento de débito |
| **DebitoContaBackendApi** | Controller REST para consultas de autorização e histórico |
| **ListaBancosConveniadosAPI** | Controller REST para listar bancos conveniados |
| **CallbackListener** | Listener JMS que consome mensagens de retorno |
| **AutenticarDebitoContaJmsService** | Serviço para envio de mensagens de autenticação para fila |
| **InclusaoDebitoJmsService** | Serviço para envio de mensagens de inclusão para fila |
| **CancelamentoDebitoJmsService** | Serviço para envio de mensagens de cancelamento para fila |
| **ConsultarAutorizacaoDebitoRepository** | Repository para consultas de autorização no banco |
| **NotificacaoDebitoCallbackRepository** | Repository para envio de notificações via HTTP |
| **JmsConfiguration** | Configuração de mensageria JMS |
| **ConverterJms** | Conversor customizado de mensagens JMS |

## 3. Tecnologias Utilizadas

- **Spring Boot 2.0.0.RELEASE** - Framework principal
- **Spring MVC** - Controllers REST
- **Spring JMS** - Mensageria
- **Spring JDBC** - Acesso a dados
- **IBM MQ** - Broker de mensagens (mq-jms-spring-boot-starter 2.0.9)
- **Sybase jConnect 7.07** - Driver JDBC para banco Sybase
- **Swagger/OpenAPI 2.8.0** - Documentação de API
- **Lombok 1.16.20** - Redução de boilerplate
- **Jackson** - Serialização/deserialização JSON
- **Gradle 4.5.1** - Gerenciamento de build
- **Docker** - Containerização (OpenJDK 8 com OpenJ9)
- **JUnit/Spring Test** - Testes
- **JMeter** - Testes funcionais
- **SonarQube/JaCoCo** - Análise de código e cobertura

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /varejo/debitoConta/v3/autenticarDebitoConta | AutenticarDebitoContaAPI | Autentica débito em conta |
| PUT | /varejo/debitoConta/v3/incluirDebitoConta | InclusaoDebitoApi | Inclui novo débito em conta |
| DELETE | /varejo/debitoConta/v3/cancelarDebitoConta | CancelamentoDebitoApi | Cancela débito em conta |
| POST | /varejo/debitoConta/v3/listarAutorizacoesDebitoConta | DebitoContaBackendApi | Lista autorizações de débito |
| POST | /varejo/debitoConta/v3/obterHistoricoAutorizacoesDebitoConta | DebitoContaBackendApi | Obtém histórico de autorizações |
| POST | /v1/listarBancoConveniado | ListaBancosConveniadosAPI | Lista bancos conveniados |

## 5. Principais Regras de Negócio

1. **Validação de Modelo de Autorização**: O sistema verifica o modelo de autorização configurado para cada banco (sem autorização, única vez, por proposta)
2. **Autorização Automática**: Para bancos configurados como "sem autorização", o débito é automaticamente autorizado
3. **Validação de Sistema Origem**: Verifica se o sistema de origem está cadastrado antes de processar operações
4. **Validação de Dados Bancários**: Valida campos obrigatórios como CPF, banco, agência, conta antes de processar
5. **Validação de Tipo de Operação**: Valida se o tipo de operação é válido (1=proposta, 2=contrato, 3=identificador externo)
6. **Consulta por Múltiplos Critérios**: Permite consultar autorizações por proposta, contrato, identificador externo ou dados bancários
7. **Histórico de Eventos**: Mantém histórico completo de todos os eventos de autorização
8. **Notificação de Callback**: Notifica sistemas de origem sobre resultados de operações via HTTP
9. **Tratamento de Caracteres Especiais**: Remove caracteres especiais de mensagens antes de enviar callbacks
10. **Conversão de Mensagens**: Converte mensagens JMS entre formatos TextMessage e BytesMessage

## 6. Relação entre Entidades

**Principais entidades e relacionamentos:**

- **RegistroAutorizacaoDebito**: Entidade principal que representa uma autorização de débito
  - Relaciona-se com **EventoRegistroAutorizacaoDebito** (1:N) - histórico de eventos
  - Relaciona-se com **AutorizacaoDebitoPrpsaCntro** (1:N) - vínculo com propostas/contratos
  - Relaciona-se com **ContaAutorizacaoDebito** (1:1) - dados bancários
  - Relaciona-se com **SistemaOrigemAutorizacaoDebito** (N:1) - sistema de origem

- **ModeloAutorizacaoDebito**: Define o modelo de autorização por banco
  - Relaciona-se com banco através de nuBanco

- **SistemaOrigem**: Cadastro de sistemas que utilizam o serviço
  - Relaciona-se com **SistemaOrigemEnderecoEletronico** (1:N) - URLs de callback

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbRegistroAutorizacaoDebito | Tabela | SELECT | Registros de autorização de débito |
| TbEventoRegistroAutorizacaoDbo | Tabela | SELECT | Eventos de autorização de débito |
| TbParametroAutorizacaoDebito | Tabela | SELECT | Parâmetros e modelos de autorização por banco |
| TbStatusAutorizacaoDebito | Tabela | SELECT | Status possíveis de autorização |
| TbAutorizacaoDebitoPrpsaCntro | Tabela | SELECT | Vínculo de autorizações com propostas/contratos |
| TbSistemaOrigem | Tabela | SELECT | Cadastro de sistemas de origem |
| TbEnderecoEletronicoAvisoDbto | Tabela | SELECT | URLs de callback dos sistemas |
| TbContaConvenio | Tabela | SELECT | Contas conveniadas para débito |
| TbContaConvenioSistemaOrigem | Tabela | SELECT | Vínculo de contas com sistemas de origem |
| DBCOR..TbBanco | Tabela | SELECT | Cadastro de bancos |
| TbLogEventoRegistroAtrzoDbto | Tabela | SELECT | Log histórico de eventos |
| DBCRED..TbProposta | Tabela | SELECT | Propostas de crédito |
| DBCRED..TbPropostaFavorecido | Tabela | SELECT | Dados bancários de favorecidos |
| DBCOR..TbContratoPrincipal | Tabela | SELECT | Contratos principais |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbEventoRegistroAutorizacaoDbo | Tabela | UPDATE | Atualiza status e datas de eventos de autorização |
| TbRegistroAutorizacaoDebito | Tabela | UPDATE | Atualiza modelo de autorização e status de processamento |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| consultarautorizacaodebitorepository-sql.xml | Leitura | ConsultarAutorizacaoDebitoRepository | Queries SQL para consultas de autorização |
| listabancoconveniadorepository-sql.xml | Leitura | ListaBancoConveniadoRepository | Queries SQL para listar bancos conveniados |
| sistemaorigemrepository-sql.xml | Leitura | SistemaOrigemRepository | Queries SQL para consultar sistemas de origem |
| application.yml | Leitura | Spring Boot | Configurações da aplicação |
| application-local.yml | Leitura | Spring Boot | Configurações para ambiente local |
| logback-spring.xml | Leitura | Logback | Configuração de logs |
| roles/*.yml | Leitura | Spring Security | Configuração de roles por ambiente |

## 10. Filas Lidas

- **${GDCC_JMS_RETORNO_DEBITO_CONTA_QUEUE}** (dev: DEV.QUEUE.3, des: QL.GDCC.RETORNO_DEBITO_CONTA.INT)
  - Consumida por: CallbackListener
  - Descrição: Fila de retorno com resultados de operações de débito (autenticação, inclusão, cancelamento)
  - Propriedades da mensagem: "operacao" (tipo de operação), "siglasistema" (sistema de origem)

## 11. Filas Geradas

- **${GDCC_JMS_TP_DEBITO_EM_CONTA_TP}** (dev: dev/, des: tópico configurado)
  - Tipo: Tópico JMS (pub/sub)
  - Publicada por: AutenticarDebitoContaRequestRepository, InclusaoDebitoEnvioRepository, CancelamentoDebitoEnvioRepository
  - Descrição: Tópico para publicação de operações de débito (autenticação, inclusão, cancelamento)
  - Propriedades da mensagem: "operacao" com valores "autenticar", "debitar" ou "cancelar"

## 12. Integrações Externas

1. **API Gateway de Notificação**
   - URL: ${GDCC_API_GATEWAY_URL_NOTIFICACAO}/v1/varejo/cadastro/notificacao-debito-conta/confirmar
   - Autenticação: Basic Auth
   - Descrição: Envia notificações de callback para sistemas de origem
   - Classe: NotificacaoDebitoCallbackRepository

2. **Sistemas de Origem (via callback)**
   - URLs dinâmicas configuradas em TbEnderecoEletronicoAvisoDbto
   - Autenticação: API Key customizada por sistema
   - Descrição: Notifica sistemas externos sobre resultados de operações
   - Operações: autenticar, debitar, cancelar

3. **Banco de Dados Sybase**
   - Database: DbGestaoDebitoContaCorrente
   - Descrição: Banco principal para gestão de débitos
   - Acesso via: Spring JDBC com jConnect

4. **IBM MQ**
   - Queue Manager: ${GDCC_JMS_TP_DEBITO_EM_CONTA_QMANAGER}
   - Channel: ${GDCC_JMS_TP_DEBITO_EM_CONTA_CHANNEL}
   - Descrição: Broker de mensagens para comunicação assíncrona

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades em camadas (controller, service, repository)
- Uso adequado de anotações Lombok para reduzir boilerplate
- Configuração adequada de profiles para diferentes ambientes
- Documentação Swagger implementada
- Uso de bibliotecas corporativas (springboot-arqt-base)

**Pontos Negativos:**
- **Código duplicado**: Métodos como `verificaParametros`, `preencheCodigo` repetidos em múltiplas classes de serviço
- **Parsing manual de JSON**: Conversão de JSON para objetos feita manualmente com split de strings ao invés de usar Jackson
- **Tratamento de exceções genérico**: Uso excessivo de `Exception` ao invés de exceções específicas
- **Métodos muito longos**: Alguns métodos com mais de 100 linhas (ex: `listarAutorizacoesDebitoConta`, `montaRetorno`)
- **Falta de validação**: Validações de negócio misturadas com lógica de conversão
- **Comentários em português**: Mistura de português e inglês no código
- **SQL em XML**: Queries SQL complexas em arquivos XML dificultam manutenção
- **Falta de testes**: Diretórios de teste vazios (apenas .keep files)
- **Clonagem desnecessária de Dates**: Uso de clone() em getters/setters de Date
- **Conversão de mensagens complexa**: Lógica de conversão BytesMessage/TextMessage repetida

## 14. Observações Relevantes

1. **Ambiente de Desenvolvimento**: Sistema configurado para múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas
2. **Segurança**: Utiliza autenticação Basic Auth com integração LDAP em ambientes não-locais
3. **Containerização**: Preparado para deploy em Docker/OpenShift com configurações de infraestrutura como código
4. **Monitoramento**: Configurado para SonarQube e JaCoCo para análise de qualidade e cobertura
5. **Pipeline CI/CD**: Integrado com Jenkins (jenkins.properties) e possui scripts de release automatizado
6. **Limitação de Memória**: Container configurado com apenas 128MB de heap máximo (-Xmx128m)
7. **Conversão Manual**: Sistema faz parsing manual de JSON em várias classes, o que é propenso a erros
8. **Dependência de Bancos Legados**: Integração com sistemas legados (DBCRED, DBCOR) do Sybase
9. **Callback Síncrono**: Notificações de callback são síncronas, o que pode impactar performance
10. **Falta de Documentação**: README genérico, não específico do projeto