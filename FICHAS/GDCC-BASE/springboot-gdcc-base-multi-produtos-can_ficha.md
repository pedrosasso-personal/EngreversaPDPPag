# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de cancelamento de débitos em conta corrente para múltiplos produtos, desenvolvido em Spring Boot. O sistema consome mensagens JMS de uma fila IBM MQ contendo solicitações de cancelamento de débitos, valida as informações, processa o cancelamento conforme regras de negócio e envia resposta para uma fila de retorno. Também oferece uma API REST para envio de solicitações de cancelamento.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **CancelamentoMultiProdutosService** | Serviço principal que contém a lógica de negócio para cancelamento de débitos, validações de status, data de vencimento e sistema de origem |
| **CancelamentoDebitoMultiprodutosListener** | Listener JMS que recebe mensagens da fila de cancelamento, valida dados básicos e aciona o serviço de cancelamento |
| **CancelamentoDebitoJmsService** | Serviço responsável por enviar mensagens JMS para as filas (cancelamento e retorno) |
| **CancelamentoDebitoRepository** | Repositório para operações de banco de dados relacionadas a débitos (busca, atualização de status, inclusão) |
| **CancelamentoDebitoEnvioRepository** | Repositório para envio de mensagens de cancelamento para o tópico JMS |
| **CancelamentoQueuePutRepository** | Repositório para envio de mensagens de retorno de cancelamento para o tópico JMS |
| **ParametroSistemaService** | Serviço para consulta de parâmetros do sistema (data de exercício) |
| **SistemaOrigemService** | Serviço para busca de informações sobre sistemas de origem |
| **ObterSequencialService** | Serviço para obtenção de sequenciais de registro de débito via stored procedure |
| **CancelamentoDebitoApi** | Controller REST que expõe endpoint para envio de cancelamento de débito |
| **JmsConfiguration** | Configuração do JMS, conversores de mensagens e listeners |
| **ConverterJms** | Conversor customizado para serialização/deserialização de mensagens JMS |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.0.0.RELEASE**
- **Spring JMS** (mensageria)
- **IBM MQ** (broker de mensagens)
- **Spring JDBC** (acesso a banco de dados)
- **Sybase jConnect 4** (driver JDBC para Sybase)
- **Jackson** (serialização JSON)
- **Lombok** (redução de boilerplate)
- **Swagger/Springfox 2.8.0** (documentação de API)
- **Gradle** (build)
- **JUnit e Mockito** (testes unitários)
- **Jacoco** (cobertura de testes)
- **SonarQube** (análise de qualidade de código)
- **Docker** (containerização)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/cancelamento-debito | CancelamentoDebitoApi | Envia solicitação de cancelamento de débito para a fila JMS |

**Parâmetros do endpoint:**
- `Sistema Origem` (Integer): Código do sistema de origem
- `Codigo Registro Debito` (Integer): Código do registro de débito a ser cancelado
- `Data de Vencimento` (String): Data de vencimento do débito

---

## 5. Principais Regras de Negócio

1. **Validação de Registro de Débito**: O registro de débito deve existir e ter tipo de movimento igual a "0" (agendamento)
2. **Validação de Data de Vencimento**: A data de vencimento informada deve corresponder à data cadastrada no registro de débito
3. **Validação de Sistema de Origem**: O sistema de origem informado deve corresponder ao sistema de origem parametrizado para o registro
4. **Regra de Data de Exercício**: Para débitos com status "enviado" (4), a data de vencimento deve ser maior ou igual à data de exercício do sistema
5. **Cancelamento Direto**: Débitos com status "aguardando geração" (3) são cancelados diretamente (status alterado para 7)
6. **Cancelamento por Inclusão**: Débitos com status "processando arquivo" (5), "arquivo enviado" (4), "arquivo gerado" (1) ou "processado com sucesso" (9) geram um novo registro de débito com tipo de movimento "1" (cancelamento) e status "aguardando geração" (3)
7. **Validação de Formato de Data**: A data de vencimento deve estar no formato dd/MM/yyyy
8. **Código de Registro Obrigatório**: O código do registro de débito não pode ser zero ou nulo

---

## 6. Relação entre Entidades

**Principais entidades e relacionamentos:**

- **TbRegistroDebito**: Entidade principal que armazena os registros de débito
  - Relaciona-se com **TbStatusDebito** (N:1) através de `CdStatusDebito`
  - Relaciona-se com **TbContaConvenioSistemaOrigem** (N:1) através de `CdContaConvenioSistemaOrigem`

- **TbContaConvenioSistemaOrigem**: Armazena informações de conta/convênio e sistema de origem
  - Relaciona-se com **TbSistemaOrigem** (N:1) através de `CdSistemaOrigem`

- **TbSistemaOrigem**: Cadastro de sistemas de origem

- **TbParametroSistema**: Armazena parâmetros do sistema (data de exercício, data de processamento)

- **TbStatusDebito**: Cadastro de status de débito

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbRegistroDebito | tabela | SELECT | Busca informações de registro de débito por código |
| TbStatusDebito | tabela | SELECT | Busca descrição do status do débito (via JOIN) |
| TbParametroSistema | tabela | SELECT | Consulta data de exercício e data de processamento |
| TbSistemaOrigem | tabela | SELECT | Busca informações de sistema de origem por código |
| TbContaConvenioSistemaOrigem | tabela | SELECT | Busca sistema de origem através do código de registro de débito (via JOIN) |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbRegistroDebito | tabela | UPDATE | Atualiza status do débito, login e data de alteração |
| TbRegistroDebito | tabela | INSERT | Insere novo registro de débito de cancelamento |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | leitura | Configuração Spring Boot | Arquivo de configuração de logs (montado via ConfigMap no Kubernetes) |
| cancelamentodebitorepository-sql.xml | leitura | CancelamentoDebitoRepository | Arquivo XML contendo queries SQL para operações de débito |
| parametrosistemarepository-sql.xml | leitura | ParametroSistemaRepository | Arquivo XML contendo query SQL para consulta de parâmetros do sistema |
| sistemaorigemrepository-sql.xml | leitura | SistemaOrigemRepository | Arquivo XML contendo queries SQL para busca de sistema de origem |

---

## 10. Filas Lidas

**Filas JMS consumidas pelo sistema:**

| Nome da Fila | Tipo | Descrição |
|--------------|------|-----------|
| ${GDCC_JMS_CANCELAR_DEBITO_CONTA_QUEUE} | Queue | Fila de entrada para recebimento de solicitações de cancelamento de débito |

**Configuração:** A fila é configurada via variável de ambiente e consumida pelo listener `CancelamentoDebitoMultiprodutosListener` através da anotação `@JmsListener`.

---

## 11. Filas Geradas

**Filas/Tópicos JMS para os quais o sistema publica mensagens:**

| Nome da Fila/Tópico | Tipo | Descrição |
|---------------------|------|-----------|
| ${GDCC_JMS_TP_DEBITO_EM_CONTA_TP} | Topic | Tópico para envio de solicitações de cancelamento de débito (usado pela API REST) |
| ${GDCC_JMS_TP_RETORNO_DEBITO_EM_CONTA_TP} | Topic | Tópico para envio de respostas de cancelamento de débito |

**Observação:** As mensagens publicadas no tópico de retorno incluem propriedades customizadas como `siglasistema` e `operacao` para roteamento.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| IBM MQ | Mensageria | Broker de mensagens para comunicação assíncrona via JMS |
| Banco de Dados Sybase (DbGestaoDebitoContaCorrente) | Banco de Dados | Banco de dados principal para persistência de débitos, parâmetros e sistemas de origem |
| LDAP (BVNet) | Autenticação | Serviço de autenticação e autorização via LDAP |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades em camadas (controller, service, repository)
- Uso adequado de injeção de dependências e anotações Spring
- Presença de testes unitários com boa cobertura
- Uso de Lombok para redução de boilerplate
- Configuração externalizada via arquivos YAML
- Tratamento de exceções em pontos críticos
- Logs informativos em operações importantes

**Pontos de Melhoria:**
- Algumas classes de serviço poderiam ter métodos menores e mais coesos
- Conversão de datas poderia ser centralizada em uma classe utilitária
- Alguns métodos com múltiplas responsabilidades (ex: `configuraCancelamento`)
- Falta de validação de entrada em alguns pontos
- Uso de valores mágicos em alguns locais (poderia usar mais constantes)
- Tratamento de exceções genérico em alguns pontos (catch de Exception)
- Falta de documentação JavaDoc em métodos públicos
- Alguns nomes de variáveis poderiam ser mais descritivos
- Classe `MappingMessageConverterCuston` muito extensa e complexa

---

## 14. Observações Relevantes

1. **Ambiente Multi-Profile**: O sistema suporta múltiplos ambientes (des, qa, uat, prd) com configurações específicas via profiles Spring
2. **Infraestrutura como Código**: Possui arquivo `infra.yml` para deploy em Kubernetes com ConfigMaps, Secrets e probes de health
3. **Segurança**: Implementa autenticação básica e integração com LDAP
4. **Stored Procedure**: Utiliza stored procedure `prObterSequencialDisponivel` para geração de sequenciais
5. **Mensageria Pub/Sub**: Utiliza tópicos JMS (pub/sub) ao invés de filas ponto-a-ponto
6. **Correlation ID**: Mantém correlation ID nas mensagens JMS para rastreabilidade
7. **Docker**: Aplicação containerizada com imagem baseada em OpenJ9
8. **Swagger**: API REST documentada via Swagger UI
9. **Monitoramento**: Possui endpoints de health check configurados para Kubernetes
10. **Versionamento**: Utiliza plugin de release do Gradle para versionamento semântico