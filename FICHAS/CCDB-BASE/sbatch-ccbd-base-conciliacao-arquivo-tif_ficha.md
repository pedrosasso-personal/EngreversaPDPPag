# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de processamento batch desenvolvido em Spring Batch para realizar a conciliação de transações de cartão de débito provenientes de arquivos TIF (Transaction Interchange Format). O sistema lê registros de conciliação da tabela `TbConciliacaoTransacao`, processa dados JSON armazenados em campos de texto, e insere os dados normalizados na tabela `TbConciliacaoTransacaoDebito`. O processamento é executado em lotes (chunks) de 100 registros, buscando transações dos últimos 40 dias que ainda não foram conciliadas.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `SpringBatchApplication` | Classe principal que inicializa a aplicação Spring Batch |
| `BatchConfiguration` | Configura o Job principal de processamento |
| `StepConfiguration` | Define o Step de carga com reader, processor e writer |
| `ReadersConfiguration` | Configura o JdbcCursorItemReader para leitura do banco |
| `WritersConfiguration` | Configura o JdbcBatchItemWriter para escrita no banco |
| `ConciliacaoProcessor` | Processa e transforma dados de `ConciliacaoArquivoTif` para `ConciliacaoTifInsert` |
| `ConciliacaoArquivoTifMapper` | Mapeia ResultSet para objetos de domínio e deserializa JSON |
| `ConciliacaoTifInsertConverter` | Converte objetos de domínio para objetos de inserção |
| `MsSqlDatasourceConfiguration` | Configura o DataSource para SQL Server |
| `DefaultBatchConfig` | Configura o DataSource para o repositório do Spring Batch |
| `TaskConfig` | Configura o TaskConfigurer para Spring Cloud Task |
| `DateUtil` | Utilitário para conversão e formatação de datas |
| `BatchExitCodeGenerator` | Gera código de saída apropriado baseado no status do job |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x**
- **Spring Batch** - Framework de processamento batch
- **Spring Cloud Task** - Gerenciamento de tarefas
- **Microsoft SQL Server** - Banco de dados (driver mssql-jdbc 7.2.2.jre11)
- **JDBC/JDBI 3.9.1** - Acesso a dados
- **Gson 2.8.9** - Serialização/deserialização JSON
- **Lombok** - Redução de boilerplate
- **Micrometer/Prometheus** - Métricas e monitoramento
- **Logback** - Logging
- **Docker** - Containerização
- **Kubernetes/OpenShift** - Orquestração
- **Maven** - Gerenciamento de dependências
- **JUnit 5 + Mockito** - Testes unitários

---

## 4. Principais Endpoints REST

**não se aplica** - Este é um sistema batch que não expõe endpoints REST para processamento de negócio. Apenas endpoints do Spring Actuator para monitoramento:
- `/actuator/health` - Health check
- `/actuator/metrics/*` - Métricas
- `/actuator/prometheus` - Métricas no formato Prometheus

---

## 5. Principais Regras de Negócio

1. **Seleção de Registros**: Busca apenas transações dos últimos 40 dias (`dateadd(dd,-40, GETDATE())`) com origem de arquivo igual a 2 (`CdArquivoOrigem = 2`) que ainda não foram conciliadas (LEFT JOIN com `TbConciliacaoTransacaoDebito` onde `CdConciliacaoTransacao IS NULL`)

2. **Limite de Processamento**: Processa no máximo 10.000 registros por execução (`TOP(10000)`)

3. **Tratamento de Nulos**: O processor valida e substitui valores nulos por valores padrão (strings vazias ou valores específicos como "1" para `dsLogin` e "S" para `flAtivo`)

4. **Conversão de Valores Monetários**: Valores monetários em formato string são convertidos para BigDecimal e divididos por 100 quando necessário (`vlTransacaoReal`)

5. **Deserialização JSON**: O campo `TeComplementoConciliacaoTrnso` contém um JSON com dados detalhados da transação que é deserializado para o objeto `TrnsoPayload`

6. **Concatenação de Data/Hora**: Data e hora da transação são concatenadas para formar um `LocalDateTime` completo

7. **Processamento em Chunks**: Registros são processados em lotes de 100 para otimização de performance

8. **Auditoria**: Sistema registra login de processamento (`sbatch-ccbd-base-conciliacao-arquivo-tif`) e timestamps de inclusão/alteração

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **ConciliacaoArquivoTif**: Entidade de leitura que representa dados da tabela de conciliação de transações
  - Contém dados básicos da transação (códigos, valores, datas)
  - Possui relacionamento com `TrnsoPayload` (composição)

- **TrnsoPayload**: Objeto complexo deserializado do JSON armazenado no campo `TeComplementoConciliacaoTrnso`
  - Contém detalhes completos da transação (mais de 60 campos)
  - Inclui dados de cartão, estabelecimento, autorizador, valores, etc.

- **TrnsoPayloadDTO**: DTO para deserialização do JSON

- **ConciliacaoTifInsert**: Entidade de escrita que representa o registro a ser inserido na tabela de destino
  - Combina dados de `ConciliacaoArquivoTif` e `TrnsoPayload`
  - Estrutura normalizada para persistência

**Relacionamento**: ConciliacaoArquivoTif (1) --contém--> (1) TrnsoPayload → converte para → ConciliacaoTifInsert

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBCCBD.CCBDTransacaoCartaoDebito.TbConciliacaoTransacao | Tabela | SELECT | Tabela principal de conciliação de transações de cartão, contém dados básicos e JSON com detalhes |
| DBCCBD.CCBDTransacaoCartaoDebito.TbComplementoConciliacaoTrnso | Tabela | SELECT | Tabela complementar com informações adicionais da conciliação (nome do arquivo, payload JSON) |
| DBCCBD.CCBDTransacaoCartaoDebito.TbConciliacaoTransacaoDebito | Tabela | SELECT | Tabela de destino usada no LEFT JOIN para identificar registros já processados |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBCCBD.CCBDTransacaoCartaoDebito.TbConciliacaoTransacaoDebito | Tabela | INSERT | Tabela de destino onde são inseridos os registros de conciliação processados e normalizados |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| selectConciliacaoTif.sql | Leitura | ReadersConfiguration / resources/sql/reader | Query SQL para leitura dos registros a serem processados |
| insereConciliacaoTif.sql | Leitura | WritersConfiguration / resources/sql/writer | Query SQL parametrizada para inserção dos registros processados |
| application.yml | Leitura | Spring Boot | Arquivo de configuração da aplicação com profiles (local, des, qa, uat, prd) |
| logback-spring.xml | Leitura | Logback | Configuração de logging da aplicação |

---

## 10. Filas Lidas

**não se aplica** - O sistema não consome mensagens de filas.

---

## 11. Filas Geradas

**não se aplica** - O sistema não publica mensagens em filas.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| SQL Server (DBCCBD) | Banco de Dados | Banco de dados principal contendo as tabelas de conciliação de transações de cartão de débito |
| Prometheus/Pushgateway | Monitoramento | Sistema de métricas para monitoramento do processamento batch (porta 9091) |
| Grafana | Visualização | Dashboard para visualização de métricas do batch |
| API Gateway BV | Autenticação | Gateway para autenticação JWT (configurado mas não utilizado ativamente no batch) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Uso adequado do Spring Batch com separação clara de responsabilidades (Reader, Processor, Writer)
- Utilização de Lombok para reduzir boilerplate
- Presença de testes unitários
- Configuração adequada para múltiplos ambientes
- Uso de SQL externalizado em arquivos separados
- Implementação de métricas e monitoramento

**Pontos Negativos:**
- **Processor extremamente verboso**: A classe `ConciliacaoProcessor` possui mais de 200 linhas apenas com validações `if (campo == null)`, o que poderia ser refatorado usando Optional, métodos auxiliares ou anotações de validação
- **Falta de tratamento de erros**: Não há estratégias claras de retry, skip ou tratamento de exceções no processamento batch
- **Código duplicado**: As classes `TrnsoPayload` e `TrnsoPayloadDTO` são praticamente idênticas, sem justificativa clara para duplicação
- **Magic numbers**: Valores hardcoded como "100" (chunk size), "10000" (limit), "2" (arquivo origem) sem constantes nomeadas
- **Falta de documentação**: Ausência de JavaDoc nas classes principais
- **Mapper com lógica de negócio**: A classe `ConciliacaoArquivoTifMapper` mistura responsabilidades de mapeamento com deserialização JSON
- **Testes incompletos**: Alguns testes são apenas stubs vazios (WritersConfigurationTest)
- **Conversão manual de tipos**: Muitas conversões manuais que poderiam ser automatizadas com MapStruct ou similar

---

## 14. Observações Relevantes

1. **Infraestrutura**: O sistema está preparado para execução em Kubernetes/OpenShift com configurações de deployment, config maps e secrets

2. **Performance**: O processamento em chunks de 100 registros é adequado, mas o limite de 10.000 registros por execução pode exigir múltiplas execuções para grandes volumes

3. **Segurança**: Senhas e credenciais são gerenciadas via secrets do Kubernetes/OpenShift, não estão hardcoded

4. **Monitoramento**: Integração com Prometheus permite acompanhamento detalhado do processamento

5. **Profiles**: Sistema bem configurado para diferentes ambientes (local, des, qa, uat, prd)

6. **Índices**: A query utiliza hints de índice (`WITH(nolock, index(...))`) para otimização, mas isso pode mascarar problemas de performance

7. **Janela de Processamento**: A busca por transações dos últimos 40 dias pode gerar volume variável dependendo da carga do sistema

8. **Exit Code**: Implementação customizada de exit code permite integração adequada com orquestradores de jobs

9. **Dependências**: Algumas dependências comentadas no pom.xml sugerem mudanças recentes ou experimentação

10. **Docker**: Imagem base customizada do Banco Votorantim (`pacotedocker-atle-base-java11`)