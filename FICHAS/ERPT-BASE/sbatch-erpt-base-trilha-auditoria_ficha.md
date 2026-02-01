# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch desenvolvido em Spring Batch para processamento de trilha de auditoria do ERP Protheus. O componente realiza a leitura de logs de auditoria de diversas tabelas do banco de dados SQL Server (SA1700, SA2700, SC7700, SD1700, SE2700, SE5700, SF1700) e gera registros de auditoria no formato LEEF (Log Event Extended Format) para rastreamento de operações realizadas no sistema ERP.

O processamento é executado em batch, lendo registros do dia anterior e gerando logs estruturados em JSON para sistemas de monitoramento e auditoria.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal de inicialização da aplicação Spring Boot |
| `JobConfig` | Configuração do job batch principal com encadeamento de steps |
| `BatchStep` | Constantes com nomes dos steps de processamento |
| `TrilhaAuditoria` | Entidade de domínio representando um registro de auditoria |
| `TrilhaAuditoriaMapper` | Mapper para conversão de ResultSet em objetos TrilhaAuditoria |
| `AbstractTrilhaAuditoriaWriter` | Classe abstrata base para escritores de auditoria |
| `Sa1700Reader`, `Sa2700Reader`, etc. | Readers específicos para cada tabela de log (Cadastro de Clientes, Fornecedores, Pedidos, etc.) |
| `Sa1700Writer`, `Sa2700Writer`, etc. | Writers específicos para cada tabela de log |
| `StepSa1700`, `StepSa2700`, etc. | Configuração dos steps individuais de processamento |
| `ConfigLog` | Utilitário para geração de logs de auditoria no formato LEEF |
| `SqlServerConfiguration` | Configuração do datasource SQL Server |
| `DefaultDatasourceConfiguration` | Configuração do datasource padrão para o Spring Batch |

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.6.x** (via parent pom-atle-base-sbatch-parent 2.6.0)
- **Spring Batch** - Framework para processamento batch
- **Maven 3.8+** - Gerenciamento de dependências
- **SQL Server** - Banco de dados principal (Microsoft SQL Server JDBC Driver 7.4.0)
- **H2 Database 2.2.224** - Banco em memória para testes
- **Lombok** - Redução de código boilerplate
- **Logback** - Framework de logging com saída em JSON
- **JUnit 5 + Mockito** - Testes unitários
- **Spring Boot Actuator** - Monitoramento e health checks
- **Docker** - Containerização da aplicação
- **Google Cloud Platform** - Plataforma de deploy (conforme infra.yml)

## 4. Principais Endpoints REST

não se aplica

(O sistema é um batch job sem exposição de endpoints REST para processamento. Apenas endpoints de monitoramento via Actuator estão disponíveis em http://localhost:9090/actuator/health)

## 5. Principais Regras de Negócio

1. **Processamento Diário**: O sistema processa logs de auditoria do dia anterior (D-1), filtrando registros entre 00:00:00 e 23:59:59 do dia anterior
2. **Agrupamento de Registros**: Os registros são agrupados por operação (TTAT_OPERATI), flag de deleção (TTAT_DELET), data/hora (TTAT_DTIME), identificador único (TTAT_UNQ) e número do registro (TTAT_RECNO)
3. **Numeração Sequencial**: Cada grupo de registros recebe um número sequencial (RowNumber) para controle de fase
4. **Identificação de Operações**: As operações são classificadas como:
   - 'U' = UPDATE (Alterar)
   - 'X' = DELETE (Excluir)
   - Outros = INSERT (Incluir)
5. **Formato de Auditoria LEEF**: Os logs são gerados no formato LEEF 1.0 com campos padronizados (mSourceId, mServiceId, cUserId, cCorrelationId, etc.)
6. **Tratamento de Usuários**: Usuários em branco são substituídos por 'AUTOMAT' para identificar operações automáticas
7. **Chunk Processing**: Processamento em lotes de 100 registros por vez para otimização de performance
8. **Processamento Sequencial**: Os steps são executados em sequência: SA1700 → SA2700 → SC7700 → SD1700 → SE2700 → SE5700 → SF1700

## 6. Relação entre Entidades

**Entidade Principal:**
- `TrilhaAuditoria`: Representa um registro de auditoria com os seguintes atributos:
  - mSourceId: Identificador da origem (PROTHEUS)
  - mSourceAddr: Endereço do servidor
  - mServiceId: Identificação do serviço/operação
  - mCategory: Categoria (ERPT-BASE)
  - cUserId: Identificação do usuário
  - cCorrelationId: ID de correlação único
  - cClientAddr: Endereço do cliente
  - cClientId: Identificação do cliente (ERPT)
  - cClientCorrelationId: ID de correlação do cliente
  - cFase: Número da fase/sequência
  - pBusinessAction: Ação de negócio (programa executado)
  - pUrlReferer: URL de referência

**Relacionamento com Tabelas de Log:**
- SA1700_TTAT_LOG: Logs de Cadastro de Clientes
- SA2700_TTAT_LOG: Logs de Cadastro de Fornecedores
- SC7700_TTAT_LOG: Logs de Pedidos de Compra
- SD1700_TTAT_LOG: Logs de Itens de Nota Fiscal de Entrada
- SE2700_TTAT_LOG: Logs de Títulos a Pagar
- SE5700_TTAT_LOG: Logs de Movimentações de Baixas a Pagar
- SF1700_TTAT_LOG: Logs de Cabeçalho de Nota Fiscal de Entrada

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| SA1700_TTAT_LOG | Tabela | SELECT | Logs de auditoria do cadastro de clientes |
| SA2700_TTAT_LOG | Tabela | SELECT | Logs de auditoria do cadastro de fornecedores |
| SC7700_TTAT_LOG | Tabela | SELECT | Logs de auditoria de pedidos de compra |
| SD1700_TTAT_LOG | Tabela | SELECT | Logs de auditoria de itens de nota fiscal de entrada |
| SE2700_TTAT_LOG | Tabela | SELECT | Logs de auditoria de títulos a pagar |
| SE5700_TTAT_LOG | Tabela | SELECT | Logs de auditoria de movimentações de baixas a pagar |
| SF1700_TTAT_LOG | Tabela | SELECT | Logs de auditoria de cabeçalho de nota fiscal de entrada |

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

(O sistema apenas lê dados das tabelas de log, não realiza operações de INSERT, UPDATE ou DELETE em banco de dados)

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | Leitura | /usr/etc/log/ | Arquivo de configuração de logs em formato JSON |
| spreadsheet.csv | Leitura | src/test/resources/ | Arquivo CSV de teste com dados de usuários |

## 10. Filas Lidas

não se aplica

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| SQL Server PTASQLUAT01/SQLERPPRD | Banco de Dados | Banco de dados ERP Protheus com tabelas de log de auditoria |
| Sistema de Logs Centralizado | Logging | Envio de logs estruturados em JSON via stdout para coleta por sistemas de observabilidade |

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com uso de padrões do Spring Batch (Reader, Writer, Step, Job)
- Uso adequado de Lombok para redução de boilerplate
- Configuração bem estruturada com profiles (local, des, uat, prd)
- Testes unitários presentes para componentes principais
- Uso de constantes para nomes de steps
- Documentação README.md presente

**Pontos de Melhoria:**
- Queries SQL muito longas e complexas embutidas diretamente no código (hardcoded), dificultando manutenção
- Repetição de código entre os Readers (7 classes praticamente idênticas com apenas SQL diferente)
- Repetição de código entre os Writers (7 classes idênticas)
- Classe `ConfigLog` com lógica complexa e comentários de código (código morto)
- Falta de tratamento de exceções específico em alguns pontos
- Ausência de validações de entrada
- Testes unitários básicos, sem cobertura de cenários de erro
- Falta de documentação JavaDoc nas classes
- Configurações de banco de dados com credenciais em arquivo de propriedades (mesmo que para ambiente local)

## 14. Observações Relevantes

1. **Arquitetura Multi-Layer**: O sistema utiliza uma estratégia de layers no Docker para otimização de build e deploy, separando dependências comuns, específicas e da aplicação
2. **Segurança**: Integração com OAuth2/JWT para autenticação, embora seja um batch job
3. **Monitoramento**: Exposição de métricas via Actuator e Prometheus
4. **Infraestrutura como Código**: Configuração completa de infraestrutura no arquivo infra.yml para deploy em múltiplos ambientes
5. **Formato de Log Padronizado**: Uso do formato LEEF (Log Event Extended Format) para padronização de logs de auditoria
6. **Processamento Assíncrono**: Uso de AsyncAppender no Logback para não bloquear o processamento principal
7. **Banco H2 para Testes**: Disponibilização de console H2 em http://localhost:8080/h2-console para facilitar testes locais
8. **Documentação Swagger**: Embora seja um batch, mantém documentação Swagger disponível
9. **Padrão de Nomenclatura**: Seguindo convenções do Banco Votorantim com prefixos (sbatch, erpt, base)
10. **Versionamento**: Sistema de versionamento semântico (0.1.0)