# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **springboot-spag-base-enviar-detalhes** é um serviço REST desenvolvido em Spring Boot que gerencia notificações confidenciais para Fintechs parceiras. Sua principal função é permitir que Fintechs consultem detalhes de mensagens de notificação previamente enviadas através de um protocolo e hash de validação, além de possibilitar o reenvio de notificações. O sistema implementa controles de segurança para validar que apenas o CNPJ correto possa acessar suas respectivas notificações, registra logs de todas as operações e integra-se com filas MQ para processamento assíncrono de reenvios.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Server** | Classe principal que inicializa a aplicação Spring Boot |
| **NotificacaoDetalheApi** | Controller REST que expõe os endpoints `/buscaDetalheMensagem` e `/solicitaReenvioMensagem` |
| **NotificacaoDetalheService** | Camada de negócio que implementa as regras de validação, segurança e processamento de notificações |
| **NotificacaoDetalheRepository** | Repositório de acesso a dados que executa queries SQL para consultar e atualizar notificações, eventos e fintechs |
| **NotificacaoMQRepository** | Repositório responsável por enviar mensagens para filas JMS/MQ |
| **NotificacaoFintech** | Entidade de domínio que representa uma notificação enviada a uma Fintech |
| **EventoNotificacao** | Entidade que representa tipos de eventos de notificação |
| **Fintech** | Entidade que representa dados cadastrais de uma Fintech parceira |
| **ControleRetornoNotificacao** | Entidade para registro de logs de operações |
| **UtilSpag** | Classe utilitária com métodos para conversão de datas, JSON e outras operações auxiliares |
| **AppPropertiesFintech** | Classe de configuração que carrega propriedades específicas de Fintech (validade de protocolo) |
| **AppPropertiesMq** | Classe de configuração que carrega propriedades de filas MQ |
| **DocketConfiguration** | Configuração do Swagger para documentação da API |
| **MappingMessageLocalConverter** | Conversor customizado de mensagens JMS com tratamento de erros |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.0.0.RELEASE** - Framework principal
- **Spring Web** - Para criação de APIs REST
- **Spring JDBC** - Para acesso a banco de dados
- **Spring JMS** - Para integração com filas de mensagens
- **IBM MQ** - Sistema de mensageria (mq-jms-spring-boot-starter 2.0.9)
- **Microsoft SQL Server** - Banco de dados (driver mssql-jdbc 7.0.0.jre8)
- **Swagger/Springfox 2.8.0** - Documentação de API
- **Jackson** - Serialização/deserialização JSON
- **Lombok 1.16.20** - Redução de boilerplate
- **Logback** - Framework de logging
- **Gradle 4.5.1** - Ferramenta de build
- **Docker** - Containerização (OpenJDK 8 com OpenJ9)
- **JaCoCo 0.8.1** - Cobertura de testes
- **SonarQube 2.6.2** - Análise de qualidade de código
- **JMeter** - Testes funcionais
- **Bibliotecas internas Votorantim**: springboot-arqt-base-trilha-auditoria-web, springboot-arqt-base-security-basic, springboot-arqt-base-lib-database

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/buscaDetalheMensagem` | NotificacaoDetalheApi | Consulta detalhes de uma notificação através de protocolo e hash, validando CNPJ e expiração |
| POST | `/v1/solicitaReenvioMensagem` | NotificacaoDetalheApi | Solicita o reenvio de uma notificação para a fila MQ, com limite de 10 reenvios por dia |

---

## 5. Principais Regras de Negócio

1. **Validação de Segurança**: Apenas o CNPJ proprietário da notificação pode consultar seus detalhes, validado através de URL do parceiro e login do usuário
2. **Expiração de Hash**: O hash de validação expira após período configurável (3600 segundos/1 hora por padrão)
3. **Eventos Confidenciais**: Apenas eventos marcados como confidenciais (flEnvioConfidencial='S') podem ter seus detalhes consultados
4. **Limite de Reenvios**: Máximo de 10 reenvios por protocolo no mesmo dia
5. **Registro de Auditoria**: Todas as operações são registradas na tabela TbControleRetornoNotificacao com código de retorno e descrição
6. **Entrega Única**: Uma notificação só pode ter seus detalhes consultados uma vez (DtNotificacaoEnvioDetalhe é atualizada na primeira consulta)
7. **Validação de Identificação Fintech**: Para Fintechs cadastradas (cdIdentificacaoContaFintech >= 0), valida-se o código de identificação informado
8. **Inativação no Reenvio**: Ao solicitar reenvio, a notificação original é inativada (flAtivo='N') e uma nova é enviada para a fila

---

## 6. Relação entre Entidades

**NotificacaoFintech** (entidade principal):
- Relaciona-se com **EventoNotificacao** através de `cdEventoNotificacao`
- Contém referência à URL e login do parceiro Fintech
- Possui protocolo de origem e hash de validação únicos
- Armazena a mensagem completa em formato JSON

**EventoNotificacao**:
- Define tipos de eventos de notificação
- Indica se o evento é confidencial (flEnvioConfidencial)
- Relaciona-se 1:N com NotificacaoFintech

**Fintech**:
- Representa parceiros cadastrados
- Relaciona-se com NotificacaoFintech através de CNPJ (NuCpfCnpj)
- Possui código de identificação de conta (CdIdentificacaoContaFintech)

**ControleRetornoNotificacao**:
- Registra logs de operações
- Relaciona-se N:1 com NotificacaoFintech através de `cdNotificacaoFintech`

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| tbNotificacaoFintech | tabela | SELECT | Consulta notificações por protocolo e hash, ou apenas por protocolo |
| TbEventoNotificacao | tabela | SELECT | Consulta eventos de notificação por código |
| TbParametroConsultaCliente | tabela | SELECT | Valida segurança através de URL e usuário do parceiro |
| TbParametroPagamentoFintech | tabela | SELECT | Consulta dados cadastrais de Fintechs para validação de CNPJ e identificação |
| TbValidacaoOrigemPagamento | tabela | SELECT | Valida origem de pagamento e parceiros comerciais |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| tbNotificacaoFintech | tabela | UPDATE | Atualiza data de envio de detalhe (DtNotificacaoEnvioDetalhe) e flag de ativo (flAtivo) |
| TbControleRetornoNotificacao | tabela | INSERT | Insere registros de log de operações com código de retorno e descrição |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| notificacaodetalherepository-sql.xml | leitura | NotificacaoDetalheRepository (via BvSql) | Arquivo XML contendo queries SQL parametrizadas |
| logback-spring.xml | leitura | Configuração Spring Boot | Arquivo de configuração de logs (console output) |
| application.yml / application-local.yml | leitura | Configuração Spring Boot | Arquivos de configuração da aplicação por ambiente |
| roles/*.yml | leitura | Configuração de segurança | Arquivos de configuração de roles e grupos LDAP por ambiente |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

| Nome da Fila | Tipo | Classe Responsável | Breve Descrição |
|--------------|------|-------------------|-----------------|
| QL.SPAG.NOTIFICAR_PARCEIRO_REQ.INT | JMS/IBM MQ | NotificacaoMQRepository | Fila para envio de solicitações de reenvio de notificações às Fintechs |

**Observação**: O nome da fila é configurável por ambiente através da propriedade `bv.mq.inQueueName`. A conexão utiliza IBM MQ com configurações de QueueManager, Channel e credenciais específicas por ambiente.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| IBM MQ | Mensageria | Integração com filas IBM MQ para envio assíncrono de notificações |
| Microsoft SQL Server (DBSPAG) | Banco de Dados | Banco de dados principal contendo tabelas de notificações, eventos, fintechs e logs |
| LDAP BVNet | Autenticação | Servidor LDAP para autenticação de usuários (ambientes des/qa/uat/prd) |
| Swagger UI | Documentação | Interface web para documentação e teste de APIs |

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Uso adequado de anotações Lombok reduzindo boilerplate
- Separação clara de responsabilidades em camadas (controller, service, repository)
- Implementação de logs detalhados para auditoria
- Uso de transações (@Transactional) em operações críticas
- Configuração externalizada por ambiente
- Tratamento de exceções com BusinessException

**Pontos Negativos:**
- **Código comentado**: Presença de código comentado em várias classes (Dockerfile, NotificacaoDetalheService, MappingMessageLocalConverter)
- **Métodos muito longos**: NotificacaoDetalheService.getMessage() e solicitaReevnio() são extensos e fazem múltiplas validações, dificultando manutenção
- **Lógica de negócio no Repository**: NotificacaoDetalheRepository contém lógica que deveria estar no Service (validações, tratamento de erros)
- **Queries SQL em XML**: Queries complexas em arquivo XML dificultam manutenção e não aproveitam recursos de ORM
- **Falta de testes**: Diretórios de testes vazios (apenas arquivos .keep)
- **Tratamento genérico de exceções**: Uso excessivo de `catch (Exception e)` sem tratamento específico
- **Strings mágicas**: Uso de strings literais ("S", "N", "Ok", "Erro") espalhadas pelo código
- **Falta de constantes**: Valores como 500 (tamanho máximo de mensagem de log) deveriam ser constantes
- **Conversão de datas manual**: UtilSpag possui lógica complexa de conversão que poderia usar bibliotecas modernas (java.time)
- **Documentação insuficiente**: Falta de JavaDoc em métodos complexos

---

## 14. Observações Relevantes

1. **Segurança Multi-Camada**: O sistema implementa validação de segurança em três níveis: URL do parceiro, login do usuário e CNPJ da Fintech, consultando múltiplas tabelas (TbParametroConsultaCliente, TbParametroPagamentoFintech, TbValidacaoOrigemPagamento)

2. **Suporte a Parceiros Não-Fintech**: O código contempla parceiros que não são Fintechs (cdIdentificacaoContaFintech = -1), aplicando validações diferenciadas

3. **Logs Fragmentados**: Mensagens de log maiores que 500 caracteres são fragmentadas e inseridas em múltiplos registros na tabela de controle

4. **Conversor Customizado de Mensagens**: MappingMessageLocalConverter implementa tratamento especial para mensagens inválidas na fila, evitando perda de dados

5. **Configuração por Ambiente**: Sistema suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas de banco, filas e LDAP

6. **Infraestrutura como Código**: Arquivo infra.yml define configurações de deployment em Kubernetes/OpenShift incluindo probes de liveness/readiness

7. **Pipeline CI/CD**: Configuração Jenkins (jenkins.properties) e scripts Gradle para build, testes e deploy automatizados

8. **Expiração Configurável**: Tempo de validade do hash é configurável via propriedade `bv.fintech.validade_protocolo` (padrão 3600 segundos)

9. **Mensagens JSON Aninhadas**: O campo `dsMensagem` contém JSON que é parseado e retornado como objeto aninhado na resposta

10. **Auditoria Completa**: Todas as operações (sucesso ou erro) são registradas com timestamp, código de retorno e descrição detalhada