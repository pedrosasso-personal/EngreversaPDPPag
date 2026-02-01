# Ficha Técnica do Sistema

---

## 1. Descrição Geral

O sistema **springboot-spag-base-enviar-notificacao** é uma aplicação Spring Boot responsável por enviar notificações para parceiros Fintech. O sistema consome mensagens de filas JMS (IBM MQ), processa as notificações e as envia para endpoints externos via API Gateway. Possui mecanismos de retry, tratamento de erros, notificações passivas e suporte a clientes do tipo Wallet. A aplicação também integra com Feature Toggle (ConfigCat) para controle de funcionalidades.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Server** | Classe principal que inicializa a aplicação Spring Boot |
| **NotificacaoService** | Serviço principal para envio de notificações, incluindo lógica de validação, integração com gateway e tratamento de clientes Wallet |
| **NotificacaoErrorService** | Serviço para tratamento de notificações com erro, incluindo reenvio e inserção em tabela de erro |
| **NotificacaoPassivaService** | Serviço para consulta passiva de notificações com erro |
| **NotificacaoListener** | Listener JMS que consome mensagens da fila principal de notificações |
| **NotificacaoErrorListener** | Listener JMS que consome mensagens da fila de erros |
| **NotificacaoRepository** | Repositório para operações de banco de dados relacionadas a notificações |
| **NotificacaoErroRepository** | Repositório para operações relacionadas a notificações com erro |
| **GatewayRepository** | Repositório responsável pela comunicação com o API Gateway (obtenção de token e envio de mensagens) |
| **SpagRepository** | Repositório para consultas relacionadas a clientes Wallet |
| **NotificacaoApi** | Controller REST para envio manual de notificações |
| **NotificacaoPassivaApi** | Controller REST para consulta passiva de notificações |
| **ToggleUtils** | Utilitário para gerenciamento de Feature Toggles |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.0.0.RELEASE** - Framework principal
- **Spring JMS** - Integração com filas JMS
- **IBM MQ 9.3.0.20** - Message broker
- **Microsoft SQL Server** - Banco de dados (driver mssql-jdbc 7.0.0.jre8)
- **Spring JDBC** - Acesso a dados
- **Springfox 3.0.0** - Documentação Swagger/OpenAPI
- **Jackson** - Serialização/deserialização JSON
- **Lombok** - Redução de boilerplate
- **ConfigCat (Feature Toggle)** - Controle de funcionalidades
- **Logback** - Logging
- **JUnit 4 e Mockito** - Testes unitários
- **Gradle 7.5.1** - Build tool
- **Docker** - Containerização
- **Jacoco e SonarQube** - Análise de qualidade e cobertura de código

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/sendMessage | NotificacaoApi | Envia uma notificação manualmente |
| POST | /v1/processaPendentes | NotificacaoApi | Processa notificações pendentes a partir de uma data |
| POST | /v1/getNotification | NotificacaoPassivaApi | Consulta notificações com erro (notificação passiva) |

---

## 5. Principais Regras de Negócio

1. **Validação de Reprocessamento**: Verifica se uma notificação já foi processada com sucesso antes de reenviar (exceto para parceiro "parceiro.fintech.neon")
2. **Geração de Hash**: Gera hash SHA-256 para validação de mensagens quando não informado
3. **Envio Confidencial**: Mensagens confidenciais (evento tipo 1) têm o conteúdo substituído por "Mensagem confidencial" antes do envio
4. **Retry com Fila de Erro**: Notificações que falham são enviadas para fila de erro com delay de 5 minutos (300000ms) para retry
5. **Controle de Tentativas**: Sistema verifica quantidade de tentativas parametrizadas por fintech antes de inserir em tabela de erro definitivo
6. **Cliente Wallet**: Identifica clientes do tipo Wallet e busca URLs específicas de callback/retorno baseadas no tipo de lançamento (entrada/saída)
7. **Validação de Protocolo**: Protocolo tem validade de 3600 segundos (1 hora) configurável
8. **Token Gateway**: Gerencia token OAuth2 para comunicação com API Gateway, com renovação automática
9. **Notificação Passiva**: Permite consulta de notificações com erro por período e documento, marcando como capturadas após leitura
10. **Sanitização de Logs**: Logs são sanitizados para evitar injection attacks

---

## 6. Relação entre Entidades

**Principais Entidades:**

- **NotificacaoFintech**: Entidade principal de notificação
  - Relaciona-se com **EventoNotificacao** (N:1) via cdEventoNotificacao
  - Relaciona-se com **ControleRetornoNotificacao** (1:N) para histórico de tentativas

- **NotificacaoErroFintech**: Notificações que falharam definitivamente
  - Armazena informações de erro e CPF/CNPJ do cliente

- **EventoNotificacao**: Tipos de eventos de notificação (confidencial ou não)

- **ControleRetornoNotificacao**: Log de retornos das tentativas de envio

- **ClienteWallet**: Informações de clientes do tipo Wallet (URLs de callback)

**Relacionamentos:**
- NotificacaoFintech → EventoNotificacao (N:1)
- NotificacaoFintech → ControleRetornoNotificacao (1:N)
- Cliente → ClienteWallet (1:1 condicional, apenas para clientes tipo Wallet)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbEventoNotificacao | Tabela | SELECT | Consulta tipos de eventos de notificação |
| TbNotificacaoFintech | Tabela | SELECT | Consulta notificações existentes e pendentes |
| TbControleRetornoNotificacao | Tabela | SELECT | Consulta histórico de tentativas de envio |
| TbParametroPagamentoFintech | Tabela | SELECT | Consulta parâmetros de fintech (tentativas, CPF/CNPJ) |
| TbParametroConsultaCliente | Tabela | SELECT | Consulta parâmetros de cliente fintech |
| TbValidacaoOrigemPagamento | Tabela | SELECT | Consulta validações de origem de pagamento |
| TbNotificacaoErroFintech | Tabela | SELECT | Consulta notificações com erro para notificação passiva |
| TbOrigemPagamentoMultiplaConta | Tabela | SELECT | Consulta informações de clientes Wallet |
| TbContaPagamentoFintech | Tabela | SELECT | Consulta contas de pagamento fintech |
| TbRelacaoLiquidacaoGrupo | Tabela | SELECT | Consulta relações de liquidação |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbNotificacaoFintech | Tabela | INSERT | Insere novas notificações |
| TbNotificacaoFintech | Tabela | UPDATE | Atualiza data de envio e flag ativo |
| TbControleRetornoNotificacao | Tabela | INSERT | Insere logs de retorno das tentativas |
| TbNotificacaoErroFintech | Tabela | INSERT | Insere notificações com erro definitivo |
| TbNotificacaoErroFintech | Tabela | UPDATE | Atualiza data de captura e flag ativo (notificação passiva) |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | Spring Boot | Configurações da aplicação |
| application-local.yml | Leitura | Spring Boot | Configurações para ambiente local |
| logback-spring.xml | Leitura | Logback | Configuração de logs |
| *-sql.xml | Leitura | BvSql (repositories) | Queries SQL parametrizadas |
| roles/*.yml | Leitura | Spring Security | Configuração de roles por ambiente |

---

## 10. Filas Lidas

| Nome da Fila | Tecnologia | Classe Consumidora | Descrição |
|--------------|-----------|-------------------|-----------|
| QL.SPAG.NOTIFICAR_PARCEIRO_REQ.INT | IBM MQ | NotificacaoListener | Fila principal de notificações |
| QL.ATACADO.NOTIFICACAO_ERRO.INT | IBM MQ | NotificacaoErrorListener | Fila de notificações com erro para retry |

---

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Produtora | Descrição |
|--------------|-----------|-----------------|-----------|
| QL.ATACADO.NOTIFICACAO_ERRO.INT | IBM MQ | NotificacaoPostMQErrorRepository | Fila de erro para retry (delay de 5 minutos) |
| QL.SPAG.NOTIFICAR_PARCEIRO_REQ.INT | IBM MQ | NotificacaoMQRepository | Reenvio para fila principal (uso interno) |

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| API Gateway Votorantim | REST | Gateway para comunicação com fintechs parceiras. Endpoints: `/auth/oauth/v2/token` (obtenção de token OAuth2) e `/v1` ou `/v2/parceiros/fintech/notificar-detalhes-pagamento/atualizar` (envio de notificações) |
| ConfigCat | Feature Toggle | Serviço de feature toggle para controle de funcionalidades (toggles: `ft_boolean_spag_base_mtls_toggle` e `ft_string_spag_base_mtls_toggle`) |
| IBM MQ | Message Broker | Sistema de filas para processamento assíncrono de notificações |
| Microsoft SQL Server | Banco de Dados | Banco de dados DBSPAG para persistência de notificações e controles |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades entre camadas (controller, service, repository)
- Uso adequado de padrões Spring Boot
- Tratamento de exceções estruturado
- Testes unitários presentes com boa cobertura
- Uso de Lombok para redução de boilerplate
- Configuração de ambientes bem organizada
- Integração com ferramentas de qualidade (SonarQube, Jacoco)
- Sanitização de logs para segurança

**Pontos de Melhoria:**
- Presença de código comentado em várias classes
- Alguns métodos muito extensos (ex: `sendMessage` em NotificacaoService)
- Uso de variáveis estáticas mutáveis (ex: `lastTokenD` e `token` em GatewayRepository) que podem causar problemas de concorrência
- Falta de documentação JavaDoc em muitas classes e métodos
- Alguns tratamentos de exceção genéricos que poderiam ser mais específicos
- Mensagens de log hardcoded em português (poderia usar i18n)
- Alguns métodos com múltiplas responsabilidades que poderiam ser refatorados
- Uso de `@Transactional` comentado em alguns lugares, indicando incerteza sobre transações

---

## 14. Observações Relevantes

1. **Feature Toggles**: O sistema utiliza ConfigCat para controle de rotas (v1/v2) do API Gateway através das toggles `ft_boolean_spag_base_mtls_toggle` e `ft_string_spag_base_mtls_toggle`

2. **Segurança**: Implementa autenticação básica via LDAP e in-memory para diferentes ambientes

3. **Retry Inteligente**: Sistema de retry com controle de tentativas parametrizado por fintech, evitando loops infinitos

4. **Clientes Wallet**: Lógica específica para identificação e tratamento de clientes do tipo Wallet, com URLs dinâmicas baseadas no tipo de lançamento

5. **Ambientes**: Configurado para múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas

6. **Containerização**: Preparado para deploy em Docker/OpenShift com configurações de health checks

7. **Monitoramento**: Endpoints de health e métricas expostos na porta 9090

8. **Validação de Datas**: Sistema possui validação robusta de formatos de data com múltiplos padrões suportados

9. **Pré-cadastro**: Sistema realiza pré-cadastro automático de eventos de notificação na inicialização

10. **Confidencialidade**: Tratamento especial para mensagens confidenciais, substituindo conteúdo antes do envio externo