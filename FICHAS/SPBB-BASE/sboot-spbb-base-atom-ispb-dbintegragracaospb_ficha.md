# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de integração e monitoramento de lotes do SPB (Sistema de Pagamentos Brasileiro) para processamento de transações PGFT (Pagamento de Fornecedores e Tributos). O sistema oferece APIs REST para conciliação de lotes, monitoramento de processamento, consulta de contingências e soma de valores de lançamentos, atualizando registros no banco de dados DBINTEGRACAOSPB.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application.java` | Classe principal Spring Boot que inicializa a aplicação |
| `ConciliacaoLoteService` | Serviço de negócio para atualização de status de conciliação de lotes |
| `MonitoramentoLoteService` | Serviço de negócio para monitoramento, consulta de contingência e soma de valores |
| `ConciliacaoLoteApiDelegateImpl` | Controlador REST para endpoints de conciliação |
| `MonitoramentoLoteApiDelegateImpl` | Controlador REST para endpoints de monitoramento |
| `ConciliacaoLoteRepository` | Repositório JDBI para operações de atualização de conciliação |
| `MonitoramentoLoteRepository` | Repositório JDBI para operações de monitoramento e consultas |
| `GlobalExceptionHandler` | Tratamento centralizado de exceções da aplicação |
| `JdbiConfiguration` | Configuração do framework JDBI para acesso a dados |
| `AppConfiguration` | Configuração geral de beans da aplicação |

## 3. Tecnologias Utilizadas

- **Framework Principal**: Spring Boot 2.x
- **Linguagem**: Java 11
- **Persistência**: JDBI 3.9.1 (SQL Object API)
- **Banco de Dados**: Sybase ASE (jConnect 16.3-SP03-PL07)
- **Mapeamento de Objetos**: MapStruct
- **Documentação API**: OpenAPI 3.0 / Swagger
- **Logging**: Logback com formato JSON
- **Segurança**: OAuth2 Resource Server com JWT
- **Build**: Maven 3.8+
- **Containerização**: Docker
- **Infraestrutura**: Google Cloud Platform (GKE)
- **Utilitários**: Lombok, Apache Commons Lang3

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| PUT | `/v1/lotes/conciliacao-lote` | `ConciliacaoLoteApiDelegateImpl` | Atualiza status de processamento de conciliação de lote |
| PUT | `/v1/lotes/monitoramento-lote` | `MonitoramentoLoteApiDelegateImpl` | Atualiza log de monitoramento ou reprocessamento |
| GET | `/v1/lotes/monitoramento-lote/{nuLote}` | `MonitoramentoLoteApiDelegateImpl` | Busca dados de contingência por número de lote e data |
| GET | `/v1/lotes/monitoramento-lote/soma-valores/{dtEntrada}` | `MonitoramentoLoteApiDelegateImpl` | Retorna soma de valores de lançamentos por data |

## 5. Principais Regras de Negócio

1. **Validação de Status de Processamento**: Apenas status específicos são aceitos para atualização:
   - Conciliação: "O", "E", "C", "R", "P"
   - Monitoramento: "W" (reprocessamento), "O", "E", "C", "R", "P" (monitoramento normal)

2. **Reprocessamento de Lotes**: Quando o status é "W", o sistema registra o histórico em tabela de log de reprocessamento antes de atualizar

3. **Consulta de Contingência**: Retorna apenas lançamentos com status "W" (aguardando processamento) para um lote específico

4. **Agregação de Valores**: Calcula soma de valores e quantidade de registros agrupados por lote para lançamentos com flag de contingência ativa

5. **Tratamento de Exceções**: Diferenciação entre exceções de negócio (código 900) e exceções técnicas (código 500)

## 6. Relação entre Entidades

**Entidades de Domínio:**

- **ConciliacaoLoteDomain**: Representa dados de conciliação (status, erro, código lançamento, número lote)
- **MonitoramentoLoteDomain**: Representa dados de monitoramento (status, erro, número lote)
- **ConsultarContingenciaDomain**: Entidade completa com todos os dados de um lançamento PGFT (50+ atributos incluindo dados de remetente, favorecido, valores, etc.)
- **SomaValoresLancamentosDomain**: Agregação de valores por lote (total, quantidade, login, status)

**Relacionamentos:**
- TbIntegracaoPGFT (1) ←→ (N) TbContingenciaPGFTDetalhe (relacionamento via cdLancamentoPGFT)
- TbIntegracaoPGFT (1) ←→ (N) TbLogReprocessamentoPGFT (histórico de reprocessamentos)

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbIntegracaoPGFT | Tabela | SELECT | Tabela principal de integração PGFT com status de processamento |
| TbContingenciaPGFTDetalhe | Tabela | SELECT | Detalhes dos lançamentos de contingência por lote |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbIntegracaoPGFT | Tabela | UPDATE | Atualização de status, data fim processamento e descrição de erro |
| TbLogReprocessamentoPGFT | Tabela | INSERT | Inserção de log de reprocessamento com histórico de status anterior |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | Leitura | Configuração Logback | Arquivo de configuração de logs em formato JSON |
| application.yml | Leitura | Spring Boot | Configurações da aplicação por ambiente |
| application-local.yml | Leitura | Spring Boot | Configurações específicas para ambiente local |
| openapi.yaml | Leitura | OpenAPI Generator | Especificação da API REST |
| *.sql (resources) | Leitura | JDBI Repositories | Queries SQL para operações de banco de dados |

## 10. Filas Lidas

não se aplica

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| API Gateway BV | OAuth2/JWT | Autenticação e autorização via JWT com validação de tokens |
| Banco Sybase ASE | JDBC | Banco de dados DBISPB para persistência de dados SPB |
| ConfigCat | Feature Flags | Sistema de gerenciamento de configurações (referenciado em infra.yml) |

## 13. Avaliação da Qualidade do Código

**Nota: 7.5/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões de camadas (Controller → Service → Repository)
- Uso adequado de frameworks modernos (Spring Boot, JDBI, MapStruct)
- Separação clara de responsabilidades entre classes
- Boa cobertura de testes unitários
- Uso de DTOs e Domain Objects separados
- Configuração externalizada por ambiente
- Documentação OpenAPI completa

**Pontos de Melhoria:**
- Validações de regras de negócio usando strings literais ("O", "E", "C", etc.) ao invés de enums
- Falta de constantes para valores mágicos repetidos no código
- Tratamento de exceções poderia ser mais granular
- Queries SQL embutidas em arquivos separados (bom), mas sem documentação inline
- Ausência de logs estruturados em pontos críticos de negócio
- Configurações duplicadas entre múltiplos arquivos logback-spring.xml
- Falta de validação de entrada nos endpoints REST (Bean Validation)

## 14. Observações Relevantes

1. **Ambiente Multi-Cloud**: Sistema preparado para execução em Google Cloud Platform (GKE) com suporte a múltiplos ambientes (local, des, qa, uat, prd)

2. **Segurança**: Implementa autenticação JWT com Bearer Token, mas possui endpoints públicos configuráveis

3. **Monitoramento**: Expõe métricas via Actuator na porta 9090 (separada da porta da aplicação 8080)

4. **Banco de Dados Legacy**: Utiliza Sybase ASE, um banco de dados legado, com configurações específicas de charset e parâmetros de conexão

5. **Processamento de Lotes**: Sistema crítico para processamento de pagamentos SPB com controle de contingência e reprocessamento

6. **Auditoria**: Possui integração com sistema de trilha de auditoria (votorantim.arqt.AUDIT)

7. **Performance**: Configurado com AsyncAppender para logs e pool de conexões JDBC otimizado

8. **Deployment**: Utiliza Docker com imagem base customizada e configurações de memória JVM otimizadas (70% MaxRAM)