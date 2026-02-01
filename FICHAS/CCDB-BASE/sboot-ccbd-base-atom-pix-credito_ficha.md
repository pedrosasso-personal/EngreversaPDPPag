# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema atômico responsável por gerenciar transações PIX via cartão de crédito no contexto do Banco Digital (CCBD). O sistema permite salvar, consultar, atualizar status e listar transações PIX realizadas com cartão de crédito, mantendo controle de protocolos e informações de cartões associados às transações.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **PixCreditoController** | Controlador REST que expõe endpoints para gerenciamento de transações PIX |
| **TransactionalPixCreditoService** | Serviço transacional que orquestra operações de negócio com controle de transação |
| **PixCreditoService** | Serviço de domínio contendo regras de negócio para transações PIX |
| **PixCreditoRepositoryImpl** | Implementação do repositório usando JDBI para acesso ao banco de dados MySQL |
| **Transacao** | Entidade de domínio representando uma transação PIX com cartão de crédito |
| **Cartao** | Entidade de domínio representando dados do cartão utilizado na transação |
| **Protocolo** | Entidade de domínio representando protocolos associados às transações (TEF, Crédito, End-to-End) |
| **PixCreditoMapper** | Mapper para conversão entre objetos de domínio e representações REST |
| **TransacaoMapper** | Mapper JDBI para conversão de ResultSet em objetos Transacao |
| **ProtocoloMapper** | Mapper JDBI para conversão de ResultSet em objetos Protocolo |

## 3. Tecnologias Utilizadas

- **Spring Boot 2.x** - Framework principal
- **Spring Web** - Para construção de APIs REST
- **Spring Security OAuth2** - Autenticação e autorização via JWT
- **JDBI 3.9.1** - Framework de acesso a dados SQL
- **MySQL 8.0.22** - Banco de dados relacional
- **HikariCP** - Pool de conexões
- **Swagger/Springfox 2.9.2** - Documentação de API
- **Micrometer/Prometheus** - Métricas e monitoramento
- **Logback** - Logging
- **Lombok** - Redução de boilerplate
- **JUnit 5** - Testes unitários
- **Mockito** - Mocks para testes
- **Maven** - Gerenciamento de dependências
- **Docker** - Containerização

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/banco-digital/conta/pix-credito/transacao | PixCreditoController | Salvar nova transação PIX |
| GET | /v1/banco-digital/conta/pix-credito/transacao | PixCreditoController | Consultar transação por NSU (End-to-End ID) |
| GET | /v1/banco-digital/conta/pix-credito/transacao/seqTransacao | PixCreditoController | Consultar transação por sequencial |
| PUT | /v1/banco-digital/conta/pix-credito/status | PixCreditoController | Atualizar status da transação |
| GET | /v1/banco-digital/conta/pix-credito/transacao/listar | PixCreditoController | Listar transações por cliente e data |

## 5. Principais Regras de Negócio

1. **Criação de Transação**: Ao salvar uma transação, são criados registros de transação, cartão e protocolos associados de forma transacional
2. **Atualização de Status**: Permite atualizar o status de processamento da transação (PENDENTE, CONCLUIDO, ESTORNADO, ESTORNO_INICIALIZADO, CONCLUIDO_SEM_PIX)
3. **Protocolos Múltiplos**: Uma transação pode ter múltiplos protocolos (TEF, TEF_ESTORNO, CREDITO, CREDITO_ESTORNO, END_TO_END)
4. **Consulta por NSU**: Se o NSU não for informado na atualização, busca a transação pelo sequencial
5. **Validação de Cartão**: Mantém informações de bandeira (VISA, MASTER, ELO), tipo e status do cartão
6. **Cálculo de Valores**: Armazena valores de pagamento, juros, multa e IOF separadamente
7. **Auditoria**: Todas as entidades mantêm data de inclusão e alteração

## 6. Relação entre Entidades

**Transacao** (1) -----> (1) **Cartao**
- Uma transação possui um cartão associado

**Transacao** (1) -----> (N) **Protocolo**
- Uma transação pode ter múltiplos protocolos

**Relacionamentos:**
- Transacao contém: cdBanco, cdAgencia, nuConta (dados da conta)
- Transacao contém: vlPagamento, vlJuros, vlMulta, vlIOF (valores financeiros)
- Transacao contém: statusProcessamento (enum de status)
- Cartao contém: bandeira (enum), status (enum), dataVencimento, ultimosDigitos
- Protocolo contém: tipoProtocolo (enum), cdProtocolo

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| CcbdPixCredito.TbTransacaoPIXCartao | tabela | SELECT | Consulta transações PIX por NSU ou sequencial |
| CcbdPixCredito.TbCartaoTransacao | tabela | SELECT | Consulta dados do cartão associado à transação (via JOIN) |
| CcbdPixCredito.TbProtocolo | tabela | SELECT | Consulta protocolos associados a uma transação |
| CcbdPixCredito.TbTransacaoPIXCartao | tabela | SELECT | Lista transações por cliente (conta, agência, banco) e data |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| CcbdPixCredito.TbTransacaoPIXCartao | tabela | INSERT | Insere nova transação PIX |
| CcbdPixCredito.TbTransacaoPIXCartao | tabela | UPDATE | Atualiza status e NSU da transação |
| CcbdPixCredito.TbCartaoTransacao | tabela | INSERT | Insere dados do cartão utilizado na transação |
| CcbdPixCredito.TbProtocolo | tabela | INSERT | Insere protocolos associados à transação |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot | Configurações da aplicação (datasource, OAuth2, profiles) |
| logback-spring.xml | leitura | Logback | Configuração de logs (console e file) |
| *.sql (8 arquivos) | leitura | PixCreditoRepositoryImpl | Queries SQL para operações de banco de dados |
| sboot-ccbd-base-atom-pix-credito.yaml | leitura | Swagger Codegen | Especificação OpenAPI para geração de interfaces |

## 10. Filas Lidas

não se aplica

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Servidor OAuth2/JWT | API REST | Validação de tokens JWT para autenticação (URL configurável por ambiente) |
| MySQL Database | Banco de Dados | Banco de dados CcbdPixCredito para persistência de transações |
| Prometheus | Monitoramento | Exportação de métricas da aplicação |

## 13. Avaliação da Qualidade do Código

**Nota: 7.5/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo DDD (Domain, Application, Infrastructure)
- Uso adequado de padrões como Repository, Service e Mapper
- Separação clara de responsabilidades entre camadas
- Uso de enums para valores fixos (Status, Bandeira, TipoProtocolo)
- Controle transacional adequado com @Transactional
- Testes unitários presentes para várias classes
- Uso de Lombok para reduzir boilerplate
- Documentação OpenAPI/Swagger bem estruturada
- Configuração de métricas e monitoramento

**Pontos de Melhoria:**
- Tratamento de exceções genérico no controller (captura Exception ao invés de exceções específicas)
- Falta de validações de entrada nos endpoints (Bean Validation)
- Alguns métodos retornam ResponseEntity sem tipo genérico adequado
- Código de mapeamento manual extenso (poderia usar MapStruct)
- Falta de logs estruturados em pontos críticos
- Alguns testes unitários são superficiais (apenas verificam não-nulo)
- Comentários TODO no código indicando funcionalidades incompletas
- Uso de strings literais em alguns lugares ao invés de constantes

## 14. Observações Relevantes

1. **Segurança**: O sistema utiliza OAuth2 com JWT para autenticação, com URLs configuráveis por ambiente
2. **Multi-ambiente**: Suporta profiles Spring (local, des, qa, uat, prd) com configurações específicas
3. **Monitoramento**: Integrado com Prometheus/Grafana para observabilidade
4. **Pool de Conexões**: Utiliza HikariCP com métricas expostas
5. **Auditoria**: Todas as operações registram usuário "CcbdPixCredito_appl" e timestamps
6. **Timezone**: Configurado para UTC nas operações de banco de dados
7. **Arquitetura de Testes**: Separação clara entre testes unitários, integração e funcionais
8. **CI/CD**: Configurado para Jenkins com propriedades específicas (jenkins.properties)
9. **Containerização**: Dockerfile otimizado com OpenJ9 JVM
10. **Versionamento**: Versão atual 0.5.0, indicando que ainda está em desenvolvimento ativo