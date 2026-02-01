# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java responsável pelo processamento de parcelas de débito digital no contexto de gestão de débito em conta corrente (GDCC). O sistema realiza a consolidação de eventos de baixa de débitos, processa retornos de débito automático, atualiza status de parcelas, gera tarefas SAC quando necessário, e controla autorizações de débito da Caixa Econômica Federal (CEF). Opera em modo batch processando lotes de registros de débito que foram previamente enviados e retornados pelos bancos.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê registros processados de baixa (status 13) do banco de dados e inicializa os DAOs necessários para o processamento |
| **ItemProcessor** | Processa cada retorno de débito, identifica o tipo de ação necessária, atualiza status das parcelas e separa registros para tratamentos específicos (autorizações CEF, cadastro optante) |
| **ItemWriter** | Persiste as alterações no banco, gera controle de carga, cria informações de baixa, atualiza contratos de débito, gera tarefas SAC e trata autorizações especiais |
| **ConsolidaRegistrosDebitoDao** | Consolida eventos de baixa da tabela temporária, agrupa por conta convênio, gera logs de arquivo e eventos de registro de débito |
| **ConsultarRetornoDao** | Consulta detalhes de retorno de débito a partir do log de arquivo |
| **ControleRetornoDao** | Gerencia controle de processamento de arquivos de retorno, atualiza parcelas de débito e gera controle de carga para baixa |
| **ParcelaDebitoDao** | Gerencia operações CRUD de parcelas de débito |
| **ContratoDebitoDao** | Atualiza suspensões e dados bancários de contratos de débito |
| **GerarTarefaSacDao** | Cria solicitações e tarefas especiais no sistema SAC para tratamento de inconsistências |
| **LogArquivoDao** | Atualiza status de processamento dos logs de arquivo de débito |
| **ProcessadosBaixaDao** | Busca registros com status "processado" (13) para iniciar o processamento |
| **DbCorDao** | Consulta feriados nacionais no banco DBCOR |
| **MyResumeStrategy** | Estratégia de tratamento de erros do batch, define códigos de saída e logging |
| **Constants** | Centraliza constantes do sistema (códigos de retorno, tipos de ação, flags) |

---

## 3. Tecnologias Utilizadas

- **Java** (versão não especificada explicitamente, provavelmente Java 6-8 pelo código)
- **Maven** (gerenciamento de dependências e build)
- **Spring Framework 2.0** (injeção de dependências e configuração XML)
- **BV Framework Batch** (framework proprietário para processamento batch)
- **Sybase ASE** (banco de dados principal - driver jConnect 4)
- **JDBC** (acesso a dados)
- **Log4j 1.2.17** (logging)
- **JUnit 4** (testes unitários)
- **Mockito 2.23.4** (mocks em testes)
- **PowerMock 2.0.0-beta.5** (mocks estáticos em testes)
- **Apache Commons Lang** (utilitários)

---

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch que não expõe endpoints REST.

---

## 5. Principais Regras de Negócio

1. **Consolidação de Eventos de Baixa**: Agrupa eventos de baixa por conta convênio, calcula valores totais, gera logs de arquivo e eventos de registro de débito
2. **Processamento de Retornos**: Processa retornos de débito automático dos bancos, identifica tipo de ação necessária (baixar, suspender, criar tarefa SAC)
3. **Atualização de Status de Parcelas**: Altera status das parcelas conforme tipo de ação (RETORNADO_BAIXA, RETORNADO_INCONSISTENTE)
4. **Suspensão de Contratos**: Suspende contratos de débito quando há inconsistências cadastrais ou retornos negativos
5. **Geração de Tarefas SAC**: Cria solicitações no sistema SAC para tratamento manual de divergências de dados, datas ou valores
6. **Controle de Carga**: Gera controle de carga para baixa de parcelas, limitado a 7000 registros por arquivo
7. **Tratamento de Autorizações CEF**: Processa retornos específicos da Caixa Econômica Federal (códigos AA, 78, AB, BD) atualizando status de autorização
8. **Cadastro de Optantes**: Trata cadastro de optantes em débito automático, suspendendo quando não realizado
9. **Cancelamento de Débitos**: Processa cancelamentos de débito com sucesso (código 99)
10. **Validação de Dias Úteis**: Considera feriados nacionais para cálculo de prazos de tarefas SAC
11. **Controle de Reprocessamento**: Evita reprocessamento através da tabela TbControleArquivoRetorno
12. **Limpeza de Dados Temporários**: Remove registros da tabela temporária com mais de 60 dias

---

## 6. Relação entre Entidades

**Principais Entidades e Relacionamentos:**

- **TbLogArquivoDebito**: Log de arquivos de débito processados
  - Relaciona-se com **TbEventoRegistroDebito** (1:N) - eventos de um arquivo
  - Relaciona-se com **TbContaConvenio** (N:1) - conta convênio do arquivo

- **TbRegistroDebito**: Registro individual de débito
  - Relaciona-se com **TbParcelaDebito** (1:1) - parcela associada ao débito
  - Relaciona-se com **TbEventoRegistroDebito** (1:N) - eventos do registro
  - Relaciona-se com **TbContaConvenioSistemaOrigem** (N:1)

- **TbParcelaDebito**: Parcela de débito de um contrato
  - Relaciona-se com **TbContrato** (N:1) - contrato da parcela
  - Relaciona-se com **TbRegistroDebito** (1:1)

- **TbContratoDebito**: Contrato de débito automático
  - Relaciona-se com **TbContrato** (1:1)
  - Relaciona-se com **TbMotivoSuspensao** (N:1)
  - Relaciona-se com **TbAutorizacaoDebitoPrpsaCntro** (1:1)

- **TbEventoRegistroDebito**: Evento de processamento de débito
  - Relaciona-se com **TbLogArquivoDebito** (N:1)
  - Relaciona-se com **TbRegistroDebito** (N:1)
  - Relaciona-se com **TbRetornoDebitoAutomatico** (N:1)

- **TbArquivoDebitoTemp**: Tabela temporária para consolidação
  - Relaciona-se com **TbContaConvenio** (N:1)

- **TbInformacaoBaixa**: Informações de baixa para sistema legado
  - Relaciona-se com **TbContrato** (N:1)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbLogArquivoDebito | Tabela | SELECT | Busca logs de arquivo com status 13 (processado) |
| TbArquivoDebitoTemp | Tabela | SELECT | Consulta eventos de baixa para consolidação |
| TbEventoRegistroDebito | Tabela | SELECT | Consulta eventos de registro de débito |
| TbRegistroDebito | Tabela | SELECT | Consulta registros de débito e seus detalhes |
| TbParcelaDebito | Tabela | SELECT | Consulta parcelas de débito por diversos critérios |
| TbRetornoDebitoAutomatico | Tabela | SELECT | Consulta códigos de retorno de débito automático |
| TbParametroRetornoDebito | Tabela | SELECT | Consulta parâmetros de retorno por banco e convênio |
| TbRetornoDebitoSistemaOrigem | Tabela | SELECT | Consulta mapeamento de retornos para sistema origem |
| TbContaConvenioSistemaOrigem | Tabela | SELECT | Consulta dados de conta convênio |
| TbContrato | Tabela | SELECT | Consulta dados de contratos (via view vwTbContrato) |
| TbPessoa | Tabela | SELECT | Consulta dados de pessoas (DBCOR) |
| TbOperador | Tabela | SELECT | Consulta dados de operadores (DBCOR) |
| TbFeriado | Tabela | SELECT | Consulta feriados nacionais (DBCOR) |
| TbSolicitacao | Tabela | SELECT | Consulta solicitações SAC (DBSLT) |
| TbNaturezaSolicitacao | Tabela | SELECT | Consulta natureza de solicitações SAC (DBSLT) |
| TbNtzSltTbAreaTbFilial | Tabela | SELECT | Consulta filial de execução para solicitações (DBSLT) |
| TbControleArquivoRetorno | Tabela | SELECT | Verifica se arquivo já foi processado |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbLogArquivoDebito | Tabela | INSERT/UPDATE | Insere novos logs de arquivo e atualiza status (13→14 ou 12) |
| TbEventoRegistroDebito | Tabela | INSERT | Insere eventos de registro de débito consolidados |
| TbRegistroDebito | Tabela | UPDATE | Atualiza status de registro de débito para 9 |
| TbArquivoDebitoTemp | Tabela | UPDATE/DELETE | Atualiza flag FlBaixaEnviada e remove registros antigos (>60 dias) |
| TbParcelaDebito | Tabela | INSERT/UPDATE | Insere novas parcelas e atualiza status, datas e valores |
| TbContratoDebito | Tabela | UPDATE | Atualiza suspensões e dados bancários de contratos |
| TbControleArquivoRetorno | Tabela | INSERT | Registra controle de processamento de arquivos |
| TbControleCarga | Tabela | INSERT/UPDATE | Gera e atualiza controle de carga para baixa (DBGESTAO) |
| TbInformacaoBaixa | Tabela | INSERT | Insere informações de baixa para sistema legado (DBGESTAO) |
| TbSolicitacao | Tabela | INSERT | Cria solicitações SAC (DBSLT) |
| TbSltCliente | Tabela | INSERT | Insere cliente na solicitação SAC (DBSLT) |
| TbTarefaEspecial | Tabela | INSERT | Insere tarefa especial na solicitação SAC (DBSLT) |
| TbSequenciais | Tabela | UPDATE | Atualiza sequenciais para geração de IDs |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| log4j.xml | Leitura | Configuração Log4j | Configuração de logging da aplicação |
| job-definitions.xml | Leitura | Spring Framework | Definição do job batch e seus componentes |
| job-resources.xml | Leitura | Spring Framework | Configuração de datasources e recursos |
| robo.log | Gravação | Log4j RollingFileAppender | Log de execução do batch |
| statistics-{executionId}.log | Gravação | BvDailyRollingFileAppender | Log de estatísticas de execução |

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
| **Banco Sybase ASE** | Banco de Dados | Banco principal contendo schemas DbGestaoDebitoContaCorrente, DBGESTAO, DBCOR, DBSLT |
| **Sistema SAC** | Integração via BD | Criação de solicitações e tarefas no sistema de atendimento ao cliente (schema DBSLT) |
| **Sistema Legado de Baixa** | Integração via BD | Geração de informações de baixa através de TbInformacaoBaixa e TbControleCarga |
| **Bancos Depositários** | Integração Assíncrona | Recebe retornos de débito automático processados pelos bancos (dados já carregados em TbArquivoDebitoTemp) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Estrutura de batch bem organizada seguindo padrão Reader-Processor-Writer
- Separação clara de responsabilidades em DAOs específicos
- Uso de enums para constantes e tipos (StatusParcelaDebitoEnum, TipoPessoaEnum, MotivoSuspensaoEnum)
- Tratamento de exceções com códigos de erro específicos
- Testes unitários presentes (cobertura razoável)
- Uso de PreparedStatements para prevenir SQL injection

**Pontos Negativos:**
- **Código legado com práticas antigas**: Spring 2.0, configuração XML, Java 6-8
- **SQL embutido em strings**: Queries SQL hardcoded em classes Java (deveria usar ORM ou pelo menos arquivos externos)
- **Falta de documentação**: Javadoc ausente ou incompleto na maioria das classes
- **Métodos muito longos**: Alguns métodos com mais de 100 linhas (ex: handleWrite, consolidarEventosDeBaixa)
- **Acoplamento alto**: Classes com muitas dependências diretas de DAOs
- **Tratamento de erros genérico**: Muitos catch(Exception) sem tratamento específico
- **Magic numbers**: Valores hardcoded (ex: 7000 registros, 60 dias, códigos de banco)
- **Nomes de variáveis em português misturado com inglês**: Inconsistência de nomenclatura
- **Falta de logs estruturados**: Logs com strings concatenadas ao invés de formato estruturado
- **Transações não explícitas**: Controle transacional não claro no código

**Recomendações:**
- Migrar para versões mais recentes do Spring (Spring Boot)
- Implementar ORM (JPA/Hibernate) para substituir SQL manual
- Adicionar documentação Javadoc completa
- Refatorar métodos longos em métodos menores e mais coesos
- Implementar padrão de injeção de dependências mais moderno
- Adicionar validações de entrada mais robustas
- Implementar logging estruturado (JSON)
- Externalizar configurações (properties/YAML)

---

## 14. Observações Relevantes

1. **Processamento em Lote**: O sistema processa registros em lotes de até 7000 itens por arquivo de controle de carga, gerando novo arquivo quando esse limite é atingido.

2. **Múltiplos Schemas**: O sistema acessa 4 schemas diferentes do Sybase (DbGestaoDebitoContaCorrente, DBGESTAO, DBCOR, DBSLT), indicando integração com múltiplos sistemas.

3. **Tabela Temporária**: Utiliza TbArquivoDebitoTemp como staging area para consolidação de eventos antes de processar definitivamente.

4. **Controle de Reprocessamento**: Implementa mecanismo de controle através de TbControleArquivoRetorno para evitar processamento duplicado.

5. **Tratamento Específico por Banco**: Possui lógica específica para Caixa Econômica Federal (banco 104) e tratamento de autorizações com códigos especiais (AA, 78, AB, BD).

6. **Geração de Sequenciais**: Utiliza procedure prObterSequencialDisponivelOut para geração de IDs únicos.

7. **Cálculo de Dias Úteis**: Considera feriados nacionais para cálculo de prazos de tarefas SAC (15 dias úteis).

8. **Múltiplos Agentes Recebedores**: Processa débitos de diferentes agentes recebedores (1119-CP, 1193-CDC, 1163-CPC).

9. **Limpeza Automática**: Remove registros da tabela temporária com mais de 60 dias automaticamente.

10. **Framework Proprietário**: Utiliza framework batch proprietário da BV (BV Framework Batch) que pode dificultar manutenção e migração futura.

11. **Configuração de Ambiente**: Utiliza arquivo jenkins.properties indicando integração com pipeline CI/CD.

12. **Encoding**: Arquivos configurados com ISO-8859-1 (Latin-1), pode causar problemas com caracteres especiais.