# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch desenvolvido em Spring Batch para importação e sincronização de parâmetros externos entre os bancos de dados PGFT/ITP (Sybase) e SPAG (MySQL). O componente realiza a leitura de dados de entidades, eventos contábeis e eventos de empresa do sistema legado PGFT/ITP, compara com os dados existentes no SPAG e executa operações de inserção ou atualização conforme necessário, mantendo a consistência entre os sistemas.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal que inicializa a aplicação Spring Boot |
| `JobConfig` | Configuração do job batch principal |
| `StepConfiguration` | Configuração dos steps do processamento batch |
| `Reader` | Leitura dos dados dos bancos PGFT/ITP e SPAG |
| `Processor` | Comparação e transformação dos dados entre os sistemas |
| `Writer` | Gravação (insert/update) dos dados no banco SPAG |
| `PgftService` | Serviço de acesso aos dados do PGFT/ITP |
| `SpagService` | Serviço de acesso e manipulação dos dados do SPAG |
| `JdbiPgftRepositoryImpl` | Implementação do repositório de acesso ao banco PGFT/ITP |
| `JdbiSpagRepositoryImpl` | Implementação do repositório de acesso ao banco SPAG |
| `EntidadeMapper` | Mapeamento de entidades entre PGFT e SPAG |
| `EventoContabilMapper` | Mapeamento de eventos contábeis entre PGFT e SPAG |
| `EventoEmpresaMapper` | Mapeamento de eventos de empresa entre PGFT e SPAG |
| `DataSourceConfig` | Configuração dos datasources (SPAG, PGFT, H2) |
| `JdbiConfiguration` | Configuração do framework JDBI para acesso a dados |
| `BatchConfig` | Configuração geral do Spring Batch |

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.6.x** (baseado no parent pom-atle-base-sbatch-parent)
- **Spring Batch** - Framework para processamento batch
- **JDBI 3.9.1** - Framework de acesso a dados
- **MySQL Connector 9.2.0** - Driver para banco MySQL
- **Sybase jConnect 7.07** - Driver para banco Sybase
- **H2 Database** - Banco em memória para metadados do Spring Batch
- **Lombok** - Redução de código boilerplate
- **Maven** - Gerenciamento de dependências
- **Docker** - Containerização
- **Logback** - Framework de logging com saída em JSON
- **JUnit 5 e Mockito** - Testes unitários
- **Spring Cloud Sleuth** - Rastreamento distribuído
- **Micrometer/Prometheus** - Métricas e monitoramento

## 4. Principais Endpoints REST

Não se aplica. Este é um componente batch que não expõe endpoints REST. A aplicação executa como um job batch e encerra após a conclusão.

## 5. Principais Regras de Negócio

1. **Sincronização de Entidades**: Compara entidades (VeiculoLegalContabil) entre PGFT e SPAG, identificando diferenças nos campos: codFilial, codEntidade, geraMovimento, valStatus, numCgcCpf e numContaMae.

2. **Sincronização de Eventos Contábeis**: Compara eventos contábeis entre os sistemas, verificando diferenças em: codEvento, codEntidade, contaCredito, contaDebito, historico, valStatus, indCPMF, indConsolidado e codFilial.

3. **Sincronização de Eventos de Empresa**: Compara eventos de empresa, validando: codEntidade, codEvento, numConta, contaDebito, contaCredito, historico, indConsolidado, codEventoCPMF e tipEvento.

4. **Priorização de Contas IFRS9**: Quando disponíveis, utiliza as contas IFRS9 (nuContaCreditoIFRS9 e nuContaDebitoIFRS9) em vez das contas padrão.

5. **Operações de Insert vs Update**: Determina se deve inserir novos registros ou atualizar existentes baseado na presença do registro no SPAG e diferenças nos dados.

6. **Validação de Existência**: Verifica a existência de VeiculoLegalContabil antes de inserir eventos relacionados.

7. **Processamento em Lote**: Utiliza chunks de tamanho 1 para processamento item a item.

8. **Auditoria**: Registra informações de login ("PROCESSO_SINCRONIA"), datas de inclusão/alteração e status em todas as operações.

## 6. Relação entre Entidades

**Entidades PGFT/ITP:**
- `EntidadePgft`: Representa entidades/veículos legais no sistema legado
- `EventoContabilPgft`: Eventos contábeis associados a entidades
- `EventoEmpresaPgft`: Eventos de empresa associados a entidades e contas

**Entidades SPAG:**
- `VeiculoLegalContabilSpag`: Equivalente a EntidadePgft no sistema destino
- `EventoContabilSpag`: Equivalente a EventoContabilPgft
- `EventoEmpresaSpag`: Equivalente a EventoEmpresaPgft

**Relacionamentos:**
- EventoContabilSpag → VeiculoLegalContabilSpag (N:1 via CdVeiculoLegalContabil)
- EventoEmpresaSpag → VeiculoLegalContabilSpag (N:1 via CdVeiculoLegalContabil)
- EventoEmpresaSpag possui chave composta: (CdEventoEmpresaContabil, CdVeiculoLegalContabil, NuConta, TipEvento)

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| DBPGF_TES..TBL_ENTIDADE | tabela | SELECT | Entidades do sistema PGFT |
| DBPGF_TES..Tbl_Evento_Contabil | tabela | SELECT | Eventos contábeis do PGFT |
| DBPGF_TES..TBL_EVENTO_EMPRESA | tabela | SELECT | Eventos de empresa do PGFT |
| TbVeiculoLegalContabil | tabela | SELECT | Veículos legais contábeis do SPAG |
| TbEventoContabil | tabela | SELECT | Eventos contábeis do SPAG |
| TbEventoEmpresa | tabela | SELECT | Eventos de empresa do SPAG |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbVeiculoLegalContabil | tabela | INSERT/UPDATE | Inserção/atualização de veículos legais contábeis |
| TbEventoContabil | tabela | INSERT/UPDATE | Inserção/atualização de eventos contábeis |
| TbEventoEmpresa | tabela | INSERT/UPDATE | Inserção/atualização de eventos de empresa |

## 9. Arquivos Lidos e Gravados

Não se aplica. O sistema não realiza leitura ou gravação de arquivos, apenas operações em banco de dados.

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas.

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| PGFT/ITP (Sybase) | Banco de Dados | Sistema legado fonte dos dados (leitura apenas) - conexão via Sybase jConnect |
| SPAG (MySQL) | Banco de Dados | Sistema destino para sincronização (leitura e escrita) - conexão via MySQL Connector |
| H2 Database | Banco de Dados | Banco em memória para metadados do Spring Batch |

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com uso de camadas (config, domain, service, port, infrastructure)
- Uso adequado de padrões como Repository e Mapper
- Testes unitários abrangentes com boa cobertura
- Configuração externalizada em arquivos YAML
- Uso de Lombok para redução de boilerplate
- Logging estruturado em JSON
- Uso de JDBI para queries SQL externalizadas

**Pontos de Melhoria:**
- Lógica de comparação no Processor está extensa e poderia ser refatorada em métodos menores
- Uso de processamento paralelo (parallelStream) no Processor pode causar problemas de concorrência
- Tratamento de exceções genérico em alguns pontos (apenas log.error)
- Falta de documentação JavaDoc nas classes principais
- Alguns métodos com muitos parâmetros (ex: getCdEventoEmpresa com 4 parâmetros)
- Uso de strings literais para flags ("S", "N") poderia ser substituído por enums
- Código de comparação repetitivo que poderia ser abstraído

## 14. Observações Relevantes

1. **Arquitetura Hexagonal**: O projeto segue princípios de arquitetura hexagonal com uso de ports e adapters (infrastructure).

2. **Multi-DataSource**: Configuração de múltiplos datasources (SPAG, PGFT, H2) com gerenciamento adequado de transações.

3. **Processamento Síncrono**: O batch executa de forma síncrona e encerra após conclusão (System.exit no Application.java).

4. **Ambientes**: Suporte a múltiplos ambientes (local, des, uat, prd) com configurações específicas.

5. **Containerização**: Dockerfile multi-layer otimizado para reduzir tamanho da imagem e melhorar cache.

6. **Observabilidade**: Integração com Prometheus para métricas e Spring Cloud Sleuth para rastreamento.

7. **Segurança**: Configuração de OAuth2 JWT para autenticação (embora não seja utilizado em batch).

8. **Infraestrutura como Código**: Arquivo infra.yml para deploy em Kubernetes com configurações de secrets, configmaps e probes.

9. **Auditoria**: Todas as operações registram usuário (PROCESSO_SINCRONIA) e timestamps para auditoria.

10. **Compatibilidade IFRS9**: Sistema preparado para trabalhar com contas contábeis no padrão IFRS9.