# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sbatch-ccbd-base-cc-virada-data** é um sistema batch desenvolvido em Java com Spring Batch, responsável pelo processo de **virada de data contábil** do sistema de Conta Corrente do Banco Votorantim. O sistema realiza a atualização da data contábil, validando dias úteis, atualizando controles de data, gerenciando rotinas de execução por agência e publicando informações de contas ativas em filas do Google Cloud Pub/Sub para processamento posterior (geração de histórico de saldos).

O batch é executado de forma agendada (configurável por ambiente) e processa todas as agências do banco, atualizando as datas de movimento, validando feriados e dias úteis através de integração com um serviço de calendário, e controlando o status de execução das rotinas.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `SpringBatchApplication` | Classe principal que inicializa a aplicação Spring Batch |
| `BatchConfiguration` | Configura o Job principal com todos os steps em sequência |
| `ValidarDataProcessor` | Valida se a data de execução é dia útil e se está dentro do horário permitido |
| `ControleDataProcessor` | Calcula os próximos dias úteis para atualização do controle de data |
| `ControleDataWriter` | Persiste as atualizações de controle de data no banco |
| `ConsultaContasItemReader` | Reader paginado que consulta contas ativas para processamento |
| `PubSubContasWriter` | Publica mensagens com lotes de contas ativas no Google Pub/Sub |
| `ContasAGerarHistoricoSaldoPubSubService` | Gerencia o envio paralelo de mensagens para o Pub/Sub com retry |
| `RotinaExecucaoService` | Gerencia o ciclo de vida das rotinas de execução (iniciar/finalizar) |
| `RotinaExecucaoAgenciaService` | Gerencia execução de rotinas por agência |
| `ControleDataService` | Serviço de negócio para validação e cálculo de datas |
| `CalendarioRepositoryImpl` | Integração com API de calendário para verificação de dias úteis |
| `ProcessarErrosListener` | Listener que captura erros do job e registra problemas no banco |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x**
- **Spring Batch** (processamento batch)
- **Spring Cloud Task** (gerenciamento de tarefas)
- **Spring Cloud GCP** (integração com Google Cloud Platform)
- **Google Cloud Pub/Sub** (mensageria)
- **JDBI 3.9.1** (acesso a dados SQL)
- **Sybase ASE** (banco de dados principal - jConnect 16.3)
- **MapStruct 1.4.2** (mapeamento de objetos)
- **Lombok** (redução de boilerplate)
- **Logback** (logging)
- **Docker** (containerização)
- **Kubernetes/GKE** (orquestração - via Spring Cloud Deployer)
- **Maven** (build)
- **Swagger Codegen** (geração de clientes REST)

---

## 4. Principais Endpoints REST

**Não se aplica** - Este é um sistema batch que não expõe endpoints REST próprios. Ele consome endpoints de sistemas externos (API de Calendário).

---

## 5. Principais Regras de Negócio

1. **Validação de Data de Execução**: A data de execução deve ser dia útil e o horário de execução deve ser maior ou igual ao configurado (padrão: 22h em produção, 8h em desenvolvimento)

2. **Validação de Data Movimento Atual**: A data de movimento atual no controle de data deve ser dia útil

3. **Cálculo de Dias Úteis Futuros**: O sistema calcula e armazena os próximos 5 dias úteis a partir da data de movimento atual

4. **Atualização em Cascata de Datas**: As datas são movidas em cascata (5 dias passado → 4 dias passado → ... → atual → próximo movimento → ... → 5 dias futuro)

5. **Controle de Rotina de Execução**: Cada execução do batch é registrada na tabela TbRotinaExecucao com status (A iniciar, Em processamento, Sucesso, Erro)

6. **Controle por Agência**: Cada agência tem seu próprio registro de execução na TbRotinaExecucaoAgencia

7. **Processamento de Contas Ativas**: Apenas contas não encerradas ou encerradas dentro de um período específico (entre 2 dias passado e data de execução) são processadas

8. **Publicação em Lote**: Contas ativas são agrupadas em lotes configuráveis (padrão: 500 contas por mensagem em produção) antes de serem publicadas no Pub/Sub

9. **Retry de Publicação**: Mensagens que falham ao serem publicadas no Pub/Sub são reprocessadas até um número máximo de tentativas (padrão: 2 em produção)

10. **Tratamento de Erros**: Erros durante a execução são capturados, registrados na TbRotinaExecucaoProblema e associados à execução da rotina

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **ControleData**: Armazena as datas de movimento (5 dias passado até 5 dias futuro) por banco e agência
  - Chave: CdBanco + CdAgencia
  - Relacionamento: 1 registro por agência

- **RotinaExecucao**: Controla a execução da rotina de virada de data
  - Chave: CdRotina (30 - Virada de Data) + DtMovimento
  - Relacionamento: 1:1 com RotinaExecucaoProblema (opcional)

- **RotinaExecucaoAgencia**: Controla a execução por agência
  - Chave: CdBanco + CdAgencia + DtMovimento
  - Relacionamento: N:1 com RotinaExecucao, 1:1 com RotinaExecucaoProblema (opcional)

- **RotinaExecucaoProblema**: Armazena detalhes de problemas ocorridos
  - Chave: SqRotinaExecucaoProblema (sequence)
  - Relacionamento: 1:N com RotinaExecucao e RotinaExecucaoAgencia

- **Conta**: Representa uma conta corrente
  - Chave: CdBanco + NuContaCorrente + CdTipoConta
  - Relacionamento: N contas por agência

- **TbParametro**: Armazena parâmetros globais do sistema (DtAtualProcCC, DtAtualControleProc)

**Relacionamentos:**
```
RotinaExecucao (1) -----> (0..1) RotinaExecucaoProblema
RotinaExecucaoAgencia (1) -----> (0..1) RotinaExecucaoProblema
ControleData (1) -----> (N) Conta [via CdBanco + CdAgencia]
```

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbControleData | tabela | SELECT | Lê informações de controle de datas por agência (datas de movimento, flags de aceitação) |
| TbConta | tabela | SELECT | Consulta contas ativas ou encerradas recentemente para processamento |
| TbRotinaExecucao | tabela | SELECT | Consulta status de execução da rotina de virada de data |
| TbRotinaExecucaoAgencia | tabela | SELECT | Consulta status de execução por agência |
| TbRotinaExecucaoProblema | tabela | SELECT | Consulta o próximo ID disponível para registro de problemas |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbControleData | tabela | UPDATE | Atualiza as datas de movimento (5 dias passado até 5 dias futuro) e data de alteração |
| TbParametro | tabela | UPDATE | Atualiza DtAtualProcCC e DtAtualControleProc com a nova data de movimento |
| TbRotinaExecucao | tabela | INSERT/UPDATE | Insere nova execução ou atualiza status, datas de início/fim e problemas |
| TbRotinaExecucaoAgencia | tabela | INSERT/UPDATE | Insere nova execução por agência ou atualiza status e datas |
| TbRotinaExecucaoProblema | tabela | INSERT/DELETE | Insere novos problemas ou deleta problemas resolvidos |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | leitura | Configuração de logging (múltiplos ambientes) | Arquivo de configuração do Logback para controle de logs |
| application.yml | leitura | Configuração Spring Boot | Arquivo de configuração principal da aplicação |
| *.sql (resources) | leitura | JDBI Repositories | Arquivos SQL para queries parametrizadas (consultas e atualizações) |
| sboot-glob-base-atom-calendario.yaml | leitura | Swagger Codegen (build time) | Especificação OpenAPI para geração de cliente REST |

**Observação**: O sistema não gera arquivos físicos de saída. Os logs são direcionados para console (STDOUT) e podem ser redirecionados para arquivos pelo orquestrador (Kubernetes).

---

## 10. Filas Lidas

**Não se aplica** - O sistema não consome mensagens de filas. Ele é um produtor de mensagens.

---

## 11. Filas Geradas

| Nome da Fila/Tópico | Tecnologia | Breve Descrição |
|--------------------|------------|-----------------|
| business-ccbd-base-conta-ativa | Google Cloud Pub/Sub | Tópico onde são publicadas mensagens contendo lotes de contas ativas para geração de histórico de saldos. Cada mensagem contém um objeto `ContasAGerarHistoricoSaldo` com coleção de contas, data de apuração e data contábil vigente |

**Configuração por ambiente:**
- **DES**: `projects/bv-ccbd-des/topics/business-ccbd-base-conta-ativa`
- **UAT**: `projects/bv-ccbd-uat/topics/business-ccbd-base-conta-ativa`
- **PRD**: `projects/bv-ccbd-prd/topics/business-ccbd-base-conta-ativa`

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Breve Descrição |
|----------------|------|-----------------|
| sboot-glob-base-atom-calendario | API REST | Serviço de calendário para verificação de dias úteis, obtenção de próximo dia útil e cálculo de prazos. Utiliza autenticação OAuth2 via API Gateway |
| API Gateway BV | OAuth2 | Gateway de autenticação para obtenção de tokens JWT para consumo de APIs internas |
| Google Cloud Pub/Sub | Mensageria | Plataforma de mensageria para publicação de eventos de contas ativas |
| Sybase ASE (DBCONTACORRENTE) | Banco de Dados | Banco de dados principal contendo tabelas de conta corrente, controle de data e rotinas |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões de Clean Architecture (separação em camadas: domain, port, infrastructure, service, config)
- Uso adequado de Spring Batch com steps bem definidos e responsabilidades claras
- Tratamento de erros robusto com listener dedicado e registro de problemas no banco
- Uso de JDBI para queries SQL externalizadas, facilitando manutenção
- Configuração externalizada por ambiente (application.yml, infra.yml)
- Uso de MapStruct para mapeamento de objetos
- Implementação de retry e skip policies para tratamento de falhas
- Processamento paralelo de publicação de mensagens no Pub/Sub
- Testes unitários presentes (embora não enviados para análise)
- Uso de Lombok para redução de boilerplate
- Documentação inline adequada em pontos críticos

**Pontos de Melhoria:**
- Algumas classes de serviço poderiam ter métodos menores e mais coesos (ex: `ControleDataService.calcularProximosDiasUteis`)
- Uso de `@SneakyThrows` em `ContasAGerarHistoricoSaldoPubSubService` pode mascarar exceções
- Supressão de warning Sonar (`@SuppressWarnings("java:S2142")`) sem justificativa clara no código
- Algumas constantes poderiam estar centralizadas em um único local
- Falta de documentação JavaDoc em métodos públicos de serviços
- Configuração de chunk sizes e timeouts poderia ter valores mais descritivos ou documentados

O código demonstra maturidade técnica, boas práticas de engenharia de software e preocupação com manutenibilidade, mas há espaço para melhorias em documentação e refinamento de alguns métodos mais complexos.

---

## 14. Observações Relevantes

1. **Execução Agendada**: O sistema é executado como um Kubernetes Job agendado (CronJob), não como um serviço contínuo. A configuração de horário varia por ambiente (22h em produção, 8h em desenvolvimento/UAT).

2. **Isolamento de Transações**: O sistema utiliza `AT ISOLATION 0` (dirty read) em algumas consultas para evitar locks e melhorar performance em leituras de grande volume.

3. **Processamento em Lote**: O sistema processa contas em chunks configuráveis (100 em DES, 10.000 em UAT, 100.000 em PRD) e agrupa em mensagens menores para publicação (100 em DES, 500 em UAT/PRD).

4. **Resiliência**: Implementa retry automático para chamadas à API de calendário (3 tentativas com delay de 2 segundos) e para publicação no Pub/Sub (2 tentativas em produção).

5. **Controle de Concorrência**: Cada agência tem seu próprio registro de controle, permitindo processamento independente e rastreabilidade.

6. **Versionamento**: O projeto está na versão 0.16.0, indicando que ainda está em evolução ativa.

7. **Segurança**: Utiliza bibliotecas de segurança do Banco Votorantim (bv-security) com autenticação OAuth2/JWT, mas a segurança está desabilitada para endpoints de health e métricas.

8. **Observabilidade**: Integrado com Actuator do Spring Boot para health checks, métricas e Prometheus.

9. **Infraestrutura como Código**: Possui configuração completa de infraestrutura (infra.yml, job.yaml) para deploy automatizado no Google Kubernetes Engine.

10. **Dependências Legadas**: Utiliza Sybase ASE como banco de dados, que é uma tecnologia mais antiga, mas ainda amplamente utilizada em instituições financeiras.