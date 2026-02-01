# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sbatch-ccbd-base-irrf** é um componente batch desenvolvido em Java com Spring Batch para geração de relatórios mensais de IRRF (Imposto de Renda Retido na Fonte). O sistema realiza consultas paginadas de saldos de contas correntes em banco de dados Sybase, processa os dados, gera arquivos CSV localmente e transfere esses arquivos para um File Server via protocolo SMB. O processamento é executado de forma paralela para diferentes combinações de banco e tipo de pessoa (PF/PJ), otimizando o desempenho através de múltiplas threads.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal que inicializa a aplicação Spring Boot com Spring Batch habilitado |
| `JobConfig` | Configuração do job principal que orquestra o fluxo de execução do batch |
| `ValidaExecucaoDecider` | Decider que determina o fluxo de execução baseado no status do step anterior |
| `VerificaDataTasklet` | Tasklet que valida e prepara os parâmetros de data para execução do job |
| `JdbiContaSaldoReader` | Reader customizado que realiza leitura paginada de contas e saldos do banco de dados |
| `ContaSaldoProcessor` | Processor que transforma objetos `ContaSaldo` em `ContaSaldoCSV` |
| `FileCsvWriter` | Writer customizado que gera arquivos CSV com cabeçalho |
| `TransfereArquivoLocalParaFileServerTasklet` | Tasklet responsável por transferir arquivos CSV gerados para o File Server |
| `ConsultaSaldoPorBancoPessoa` | Configuração que cria dinamicamente steps paralelos para cada tipo de conta bancária |
| `ContaSaldoRepository` | Interface de repositório para consultas de saldos de contas |
| `ContaSaldoRepositoryImpl` | Implementação do repositório usando JDBI |
| `FileServerService` | Serviço para interação com File Server via SMB |
| `TipoContaBancaria` | Enum que define os tipos de contas (Banco Votorantim PF/PJ, Banco BV PF/PJ) |

---

## 3. Tecnologias Utilizadas

- **Java 11+**
- **Spring Boot 2.x** (baseado no parent pom-atle-base-sbatch-parent 2.2.2)
- **Spring Batch** - Framework para processamento batch
- **JDBI 3.9.1** - Framework de acesso a dados
- **Sybase jConnect 16.3** - Driver JDBC para banco Sybase
- **MapStruct** - Mapeamento de objetos
- **Lombok** - Redução de boilerplate code
- **JCIFS 2.1.31** - Biblioteca para acesso a File Server via SMB
- **Apache Commons IO 2.11.0** - Utilitários para manipulação de arquivos
- **HikariCP** - Pool de conexões
- **Logback** - Framework de logging com saída em JSON
- **Spring Actuator** - Monitoramento e métricas
- **Docker** - Containerização
- **Maven** - Gerenciamento de dependências

---

## 4. Principais Endpoints REST

Não se aplica. Este é um componente batch que não expõe endpoints REST para processamento de negócio. Apenas endpoints de monitoramento via Actuator estão disponíveis:

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | /actuator/health | Verificação de saúde da aplicação |
| GET | /actuator/info | Informações da aplicação |
| GET | /actuator/metrics | Métricas da aplicação |
| GET | /actuator/prometheus | Métricas no formato Prometheus |

---

## 5. Principais Regras de Negócio

1. **Validação de Data de Execução**: O sistema valida se a data de execução informada não é futura. Se for execução automática (sem parâmetro de data), utiliza a data atual.

2. **Cálculo de Período de Referência**: O sistema sempre processa dados do mês anterior à data de execução (subtrai 1 mês).

3. **Consulta Paginada**: As consultas ao banco são realizadas de forma paginada, utilizando o número da última conta processada como cursor para a próxima página.

4. **Processamento Paralelo**: O sistema cria dinamicamente steps paralelos para cada combinação de banco e tipo de pessoa (4 combinações: BV PF, BV PJ, Votorantim PF, Votorantim PJ).

5. **Cálculo de Saldo Disponível**: O saldo disponível é calculado como: `saldoAtual - (saldoBloqueado + saldoIndisponivel)`.

6. **Filtros de Conta**: 
   - Contas abertas até a data fim do período
   - Contas encerradas dentro do período ou ainda ativas
   - Filtragem por tipo de pessoa (F para PF, J para PJ)

7. **Isolamento de Leitura**: As consultas utilizam `AT ISOLATION 0` (dirty read) para melhor performance.

8. **Geração de Arquivos**: Cada tipo de conta gera um arquivo CSV separado com nomenclatura padronizada: `{TIPO_CONTA}_{ANO}_{MES}.csv`.

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **ContaSaldo**: Entidade que representa o saldo de uma conta corrente em uma data específica
  - Atributos: dtApuracaoSaldo, nuContaCorrente, cdTipoConta, cdSituacaoCadastral, cdModalidadeConta, dtAberturaConta, dtEncerramentoConta, vrSaldoAtual, vrSaldoBloqueado, vrSaldoIndisponivel, cdBanco

- **ContaSaldoCSV**: Entidade DTO para exportação em CSV
  - Atributos: dataApuracao, numeroConta, tipoConta, idStatusConta, statusConta, idModalidadeConta, modalidadeConta, dataAberturaConta, dataEncerramentoConta, saldoAtual, valorBloqueado, valorIndisponivel, saldoDisponivel, idBanco

- **TipoContaBancaria** (Enum): Define os tipos de contas processadas
  - BANCO_VOTORANTIM_PF (idBanco: 161, cdBanco: 655, tipoPessoa: F)
  - BANCO_VOTORANTIM_PJ (idBanco: 161, cdBanco: 655, tipoPessoa: J)
  - BANCO_BV_PF (idBanco: 436, cdBanco: 413, tipoPessoa: F)
  - BANCO_BV_PJ (idBanco: 436, cdBanco: 413, tipoPessoa: J)

- **InfoTransferenciaArquivo**: Encapsula informações para transferência de arquivos
  - Atributos: caminhoCompletoArquivoOrigem, diretorioDestino, nomeDoArquivo

**Relacionamentos:**
- ContaSaldo é mapeado para ContaSaldoCSV através do `ContaSaldoMapper`
- TipoContaBancaria define os parâmetros de consulta e caminhos de arquivo para cada tipo de conta

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBCONTACORRENTE.dbo.TbConta | Tabela | SELECT | Tabela principal de contas correntes |
| DBCONTACORRENTE.dbo.TbSituacaoCadastral | Tabela | SELECT | Tabela de situações cadastrais das contas |
| DBCONTACORRENTE.dbo.TbModalidadeConta | Tabela | SELECT | Tabela de modalidades de contas |
| DBCONTACORRENTE.dbo.TbHistoricoSaldo | Tabela | SELECT | Tabela de histórico de saldos das contas |

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema apenas realiza operações de leitura no banco de dados. Não há operações de INSERT, UPDATE ou DELETE.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| BANCO_VOTORANTIM_PF_{ANO}_{MES}.csv | Gravação | FileCsvWriter | Arquivo CSV com saldos de contas PF do Banco Votorantim |
| BANCO_VOTORANTIM_PJ_{ANO}_{MES}.csv | Gravação | FileCsvWriter | Arquivo CSV com saldos de contas PJ do Banco Votorantim |
| BANCO_BV_PF_{ANO}_{MES}.csv | Gravação | FileCsvWriter | Arquivo CSV com saldos de contas PF do Banco BV |
| BANCO_BV_PJ_{ANO}_{MES}.csv | Gravação | FileCsvWriter | Arquivo CSV com saldos de contas PJ do Banco BV |

**Locais de Gravação:**
- **Local temporário**: `{java.io.tmpdir}/InformaRendimento/{idBanco}/{cdBanco}/{tipoPessoa}/`
- **File Server (destino final)**: 
  - DES: `//mor-fsdes01.bvnet.bv/APPS-DES/CCBD/InformaRendimento/...`
  - UAT: `//mor-fsuat01.bvnet.bv/APPS-UAT/CCBD/InformaRendimento/...`
  - PRD: `//bcoapps1.bvnet.bv/BCO-APPS/CCBD/InformaRendimento/...`

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

---

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| File Server SMB | Integração de Arquivos | Transferência de arquivos CSV gerados para diretórios compartilhados via protocolo SMB/CIFS. Utiliza autenticação NTLM com credenciais configuradas por ambiente. |
| Banco de Dados Sybase | Banco de Dados | Consulta de dados de contas correntes e histórico de saldos no banco DBCONTACORRENTE. Utiliza pool de conexões HikariCP com configurações específicas por ambiente. |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Código bem estruturado seguindo padrões do Spring Batch
- Uso adequado de design patterns (Builder, Factory, Strategy via Enum)
- Separação clara de responsabilidades em camadas (config, domain, repository, service, helper)
- Uso de Lombok reduzindo boilerplate
- Configuração externalizada via properties
- Implementação de processamento paralelo eficiente
- Uso de JDBI para queries SQL organizadas em arquivos separados
- Logging estruturado em JSON para ambientes produtivos
- Testes unitários presentes (não enviados mas identificados na estrutura)

**Pontos de Melhoria:**
- Algumas classes poderiam ter mais documentação JavaDoc
- A classe `Constants` poderia ser dividida em múltiplas classes de constantes por contexto
- Tratamento de exceções poderia ser mais específico em alguns pontos (uso de `Exception` genérica)
- Falta de validação de parâmetros em alguns métodos públicos
- O método `doJumpToPage` no Reader lança `IllegalCallerException` mas poderia ter implementação ou ser marcado como não suportado de forma mais clara

---

## 14. Observações Relevantes

1. **Execução Agendada**: O sistema é projetado para ser executado via agendador UC4, recebendo opcionalmente um parâmetro de data.

2. **Isolamento de Leitura**: As consultas utilizam `AT ISOLATION 0` (dirty read) para melhorar performance, aceitando leituras não confirmadas.

3. **Processamento Paralelo**: O sistema utiliza o número de processadores disponíveis para definir o pool de threads do processamento paralelo.

4. **Chunk Size Configurável**: O tamanho do chunk (página) é configurável por ambiente via variável `SQL_PAGE_SIZE`.

5. **Multi-layer Docker**: O Dockerfile utiliza estratégia de multi-layer para otimizar o build e deploy da imagem.

6. **Segurança**: O sistema integra com OAuth2/JWT para autenticação, embora seja um batch (provavelmente para APIs de monitoramento).

7. **Monitoramento**: Expõe métricas via Actuator e Prometheus para observabilidade.

8. **Ambientes**: Suporta múltiplos ambientes (local, des, uat, prd) com configurações específicas.

9. **Infraestrutura como Código**: Possui arquivo `infra.yml` para provisionamento automatizado da infraestrutura.

10. **Pool de Conexões**: Configurações de pool diferenciadas por ambiente (DES: 5 max/2 min, PRD: 10 max/5 min, UAT: 5 max/2 min).