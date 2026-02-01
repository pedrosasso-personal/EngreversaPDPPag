# Ficha Técnica do Sistema

---

## 1. Descrição Geral

O sistema **java-flex-parc-contrato-notificar-parceiro** é um componente de integração responsável por processar retornos de contratos do sistema FLEX e notificar parceiros comerciais sobre o resultado do processamento. 

O fluxo principal consiste em:
1. Consumir mensagens de uma fila JMS contendo informações de retorno de processamento de contratos
2. Validar e transformar os dados recebidos
3. Obter credenciais de acesso e token OAuth para integração com API externa (CAAPI)
4. Enviar notificações ao parceiro comercial via API REST com o resultado do processamento (sucesso ou erro) e eventuais inconsistências

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `RetornoProcessamentoContratoMDB` | Message-Driven Bean que consome mensagens da fila JMS e orquestra o processamento |
| `RetornoProcessamentoContratoBeanImpl` | Implementa a lógica de negócio para processar retorno de contratos e enviar para API externa |
| `HttpCaapiIntegration` | Classe abstrata base para integração HTTP com a CAAPI, gerencia chamadas GET/POST e headers |
| `CriarTokenIntegration` | Responsável por obter e gerenciar tokens OAuth para autenticação na CAAPI |
| `CaapiToken` | Bean de sessão que armazena o token JWT |
| `MensagemContratoRetornoConverter` | Converte objetos Java para XML e vice-versa (marshal/unmarshal) |
| `MensagemRetornoProcessamentoValidator` | Valida os dados da mensagem de retorno antes do processamento |
| `RetornoContratoSecurityServiceImpl` | Carrega configurações de segurança e endpoints das variáveis do servidor |
| `NameSpaceBindingUtil` | Utilitário para recuperar variáveis de configuração do JNDI do WebSphere |

---

## 3. Tecnologias Utilizadas

- **Java EE 6/7** (EJB 3.1, CDI, JMS, JAX-WS, JAX-RS)
- **IBM WebSphere Application Server** (servidor de aplicação)
- **Maven** (gerenciamento de dependências e build)
- **JMS** (Java Message Service) para mensageria assíncrona
- **JAX-B** (XML binding)
- **Apache HttpClient** para chamadas HTTP
- **Gson** para serialização/deserialização JSON
- **SLF4J/Log4j2** para logging
- **OAuth 2.0** (client credentials) para autenticação
- **Swagger** para documentação de APIs REST
- **Apache Commons Lang3** para utilitários

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| N/A | `/api` | `BaseAppConfig` | Configuração base para APIs REST (não possui endpoints implementados no código fornecido) |
| N/A | `/api-security` | `SecurityAppConfig` | APIs de segurança da arquitetura (delegadas para `SecurityRestApi`) |
| N/A | `/api-utils` | `UtilsAppConfig` | APIs utilitárias de arquitetura (delegadas para `LogRestApi`) |

**Observação:** O código fornecido não contém implementações de endpoints REST específicos do negócio, apenas configurações de aplicação e classes de infraestrutura.

---

## 5. Principais Regras de Negócio

1. **Validação de Mensagem**: Todos os campos obrigatórios da mensagem de retorno devem ser validados (numeroContrato, numeroOrigem, codigoParceiroComercial, codigoStatusPagamento)
2. **Código de Status**: O código de status "1" indica erro (E) e "2" indica sucesso (S)
3. **Retry com Token**: Em caso de erro 401 (Unauthorized), o sistema tenta reprocessar até 6 vezes, renovando o token OAuth
4. **Inconsistências**: Quando o processamento falha, uma lista de inconsistências com código e descrição deve ser enviada ao parceiro
5. **Trilha de Auditoria**: Todas as chamadas externas devem incluir headers de trilha de auditoria (ticket, siglaSistema, loginUsuarioFinal, enderecoIpCliente)
6. **Token Caching**: O token OAuth é armazenado em sessão e reutilizado enquanto válido, sendo renovado apenas quando expirado ou inválido

---

## 6. Relação entre Entidades

**Entidades principais:**

- **MensagemContratoRetorno**: Entidade raiz que representa o retorno do processamento de um contrato
  - numeroContrato (Long)
  - numeroOrigem (Long)
  - codigoParceiroComercial (Long)
  - codigoStatusPagamento (String)
  - listaInconsistencias (ListaInconsistenciaInfo)

- **ListaInconsistenciaInfo**: Contém uma coleção de inconsistências
  - inconsistencias (List<InconsistenciaInfo>)

- **InconsistenciaInfo**: Representa uma inconsistência individual
  - codigo (String)
  - descricao (String)

- **RetornoProcessamentoContratoVO**: VO para envio à API externa
  - endPointParceiro (String)
  - chave (String)
  - codigoContrato (Long)
  - numeroContratoExterno (String)
  - codigoRetorno (String)
  - inconsistencias (List<InconsistenciaVO>)

**Relacionamentos:**
- MensagemContratoRetorno (1) -> (0..1) ListaInconsistenciaInfo
- ListaInconsistenciaInfo (1) -> (0..*) InconsistenciaInfo

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

não se aplica

---

## 10. Filas Lidas

| Nome da Fila | Tipo | Descrição |
|--------------|------|-----------|
| `queue/FLEXGerarRetornoProcessamentoContratoQueue` | JMS Queue | Fila que contém mensagens XML com retornos de processamento de contratos FLEX para notificação aos parceiros |

**Activation Spec:** `as/FLEXGerarRetornoProcessamentoContratoAS`

**Connection Factory:** `jms/FLEXGerarRetornoProcessamentoContratoJMS`

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema/API | Tipo | Descrição |
|-------------|------|-----------|
| **CAAPI (API Gateway)** | REST/HTTP | API externa para notificação de parceiros sobre retorno de processamento de contratos |
| **Serviço de Token OAuth** | REST/HTTP | Endpoint para obtenção de token OAuth 2.0 (client credentials) |
| **Endpoint de Notificação** | REST/HTTP | Endpoint específico para envio das notificações de retorno de contrato |

**Variáveis de Configuração (JNDI):**
- `cell/persistent/flex_url_endpoint_token` - URL do serviço de token
- `cell/persistent/flex_url_api_notificacao` - URL da API de notificação
- `cell/persistent/flex_url_pravaler` - URL do parceiro Pravaler
- `cell/persistent/flex_chave_pravaler` - Chave de acesso do parceiro
- `cell/persistent/flex_user_name` - Usuário para autenticação OAuth
- `cell/persistent/flex_user_password` - Senha para autenticação OAuth

**Alias de Autenticação WebSphere:**
- `flexParcCaapiAuth` - Credenciais OAuth (client_id e client_secret)

---

## 13. Avaliação da Qualidade do Código

**Nota:** 6/10

**Justificativa:**

**Pontos Positivos:**
- Uso adequado de padrões Java EE (EJB, CDI, JMS)
- Separação em módulos Maven bem estruturada
- Logging presente em pontos críticos
- Tratamento de exceções com retry em caso de falha de autenticação
- Uso de validação de dados antes do processamento

**Pontos Negativos:**
- **Código comentado e debug excessivo**: Muitos logs de debug em produção (ex: impressão de senhas, tokens)
- **Segurança**: Logs expõem informações sensíveis (senhas, tokens) que não deveriam ser registrados
- **Hardcoding**: Valores como número máximo de tentativas (6) estão hardcoded
- **Tratamento de exceções genérico**: Uso de `Exception` genérica em vários pontos ao invés de exceções específicas
- **Falta de testes unitários**: Não há testes unitários no código fornecido
- **Singleton mal implementado**: `MensagemContratoRetornoConverter.getInstance()` cria nova instância a cada chamada
- **Gestão de recursos**: Falta de uso de try-with-resources em alguns pontos (HttpClient)
- **Documentação**: Javadoc incompleto ou ausente em várias classes
- **Mistura de responsabilidades**: Classe `HttpCaapiIntegration` acumula muitas responsabilidades
- **Código morto**: Classe `TestServlet` marcada como NAO_ENVIAR sugere código de teste em produção

---

## 14. Observações Relevantes

1. **Ambiente de Execução**: O sistema foi projetado especificamente para IBM WebSphere Application Server, utilizando recursos específicos como JNDI bindings e alias de autenticação

2. **Arquitetura Base**: O projeto utiliza frameworks internos da Votorantim (`arqt-base`, `fjee-base`) que fornecem funcionalidades comuns de arquitetura

3. **Segurança**: O sistema implementa autenticação OAuth 2.0 com client credentials e suporta políticas de segurança WS-Security para web services

4. **Retry Logic**: Implementa mecanismo de retry específico para erros 401 (Unauthorized), tentando até 6 vezes antes de desistir

5. **Configuração Dinâmica**: Todas as URLs e credenciais são carregadas dinamicamente de variáveis do servidor (JNDI), facilitando a configuração por ambiente

6. **Classloader**: Configurado com modo `PARENT_LAST` para permitir que bibliotecas da aplicação tenham precedência sobre as do servidor

7. **Módulos Maven**: Projeto multi-módulo bem estruturado (commons, domain, persistence, integration, business, jms, ws, rs, ear)

8. **Versionamento**: Utiliza RTC (Rational Team Concert) da IBM para controle de versão

9. **Pipeline CI/CD**: Possui arquivo `jenkins.properties` indicando integração com Jenkins para build automatizado

10. **Swagger**: Configurado para geração automática de documentação de APIs REST, embora não haja endpoints implementados no código fornecido