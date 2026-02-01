# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de processamento batch Java responsável por extrair movimentações contábeis analíticas de contas correntes do banco Sybase (DBCONTACORRENTE) e gravar essas informações em uma base MySQL (CCBDContaCorrente). O sistema processa lotes de movimentações contábeis de forma incremental, consultando lotes pendentes de processamento, extraindo as movimentações do dia anterior (D-1) e persistindo os dados analíticos com informações de débito/crédito, contas contábeis e metadados das transações.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê lotes de movimentações contábeis pendentes e consulta as movimentações analíticas do Sybase para cada lote |
| **ItemProcessor** | Processa cada movimentação (atualmente apenas repassa o objeto sem transformações) |
| **ItemWriter** | Grava as movimentações contábeis no MySQL e atualiza o status do lote após o último registro |
| **MovAnalitico** | Entidade de domínio representando uma movimentação analítica contábil |
| **LoteMovimentoContabil** | Entidade representando um lote de movimentações a ser processado |
| **MovimentacoesRepositoryImpl** | Implementação de acesso aos dados de movimentações no Sybase |
| **MovimentoContabilRepositoryImpl** | Implementação de acesso aos dados de movimentos contábeis no MySQL |
| **LoteContabilRepositoryImpl** | Implementação de acesso aos dados de lotes contábeis no Sybase |
| **Queries** | Classe utilitária contendo todas as queries SQL do sistema |
| **DateUtils** | Utilitário para manipulação e formatação de datas |
| **ConstantsUtils** | Constantes de códigos de erro do sistema |

---

## 3. Tecnologias Utilizadas

- **Java** (linguagem principal)
- **Maven** (gerenciamento de dependências e build)
- **Spring Framework** (injeção de dependências e configuração)
- **BV Framework Batch** (framework proprietário para processamento batch)
- **JDBC/Spring JDBC** (acesso a dados via NamedParameterJdbcTemplate)
- **Bitronix** (gerenciador de transações JTA)
- **Sybase jConnect** (driver JDBC para Sybase)
- **MySQL Connector/J** (driver JDBC para MySQL)
- **Log4j** (logging)
- **JUnit** (testes unitários)
- **Mockito** (mocks para testes)

---

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch sem endpoints REST.

---

## 5. Principais Regras de Negócio

1. **Processamento D-1**: O sistema processa movimentações do dia anterior (D-1) por padrão, ou aceita uma data específica via parâmetro `dtMovimentacao`
2. **Filtragem por Banco**: Apenas movimentações do banco 436 são processadas
3. **Filtragem por Agência**: Apenas movimentações da agência '2020' são consideradas
4. **Contas Contábeis**: O sistema determina as contas contábeis de débito e crédito baseado no tipo de operação (débito/crédito) e modalidade da conta
5. **Processamento por Lotes**: Apenas lotes com flag `FlGeracaoLoteMovimento` NULL ou 'N' são processados
6. **Atualização de Status**: Após processar todas as movimentações de um lote, o flag `FlGeracaoLoteMovimento` é atualizado para 'S'
7. **Marcação de Último Registro**: O último registro de cada lote é marcado com flag `ultimoRegistro=true` para controle de atualização do lote
8. **Tratamento de Documento**: Para liquidações do tipo 63, utiliza `nuSequencialUnicoLancamento` ao invés de `nuDocumento`
9. **Código de Banco Fixo**: Todas as movimentações são gravadas com código de banco 413 (hardcoded no mapper)

---

## 6. Relação entre Entidades

**MovAnalitico** (Movimento Analítico Contábil)
- Representa uma movimentação individual de conta corrente
- Contém informações de conta, valores, datas, tipo de operação
- Relaciona-se com **LoteMovimentoContabil** através de `cdLoteMovimentoContabil` e `nuLoteMovimentoContabil`

**LoteMovimentoContabil** (Lote de Movimentos Contábeis)
- Agrupa movimentações por data de movimento
- Controla o status de processamento através de `flGeracaoLoteMovimento`
- Um lote pode conter múltiplas movimentações analíticas

**LancamentoContabil** (Lançamento Contábil)
- Entidade de domínio não utilizada diretamente no fluxo principal
- Aparentemente representa uma estrutura alternativa de lançamento contábil

**Relacionamento**: LoteMovimentoContabil (1) ---> (N) MovAnalitico

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBCONTACORRENTE..tbhistoricomovimento | Tabela | SELECT | Histórico de movimentações de contas correntes (Sybase) |
| DBCONTACORRENTE..tbmovimentodia | Tabela | SELECT | Movimentações do dia corrente (Sybase) |
| DBCONTACORRENTE..TbParametroMovimentoContabil | Tabela | SELECT | Parâmetros de contas contábeis por modalidade (débito/crédito) |
| DBCONTACORRENTE.dbo.TbLoteMovimentoContabil | Tabela | SELECT | Lotes de movimentações contábeis pendentes de processamento |
| CCBDContaCorrente.TbMovimentoContabil | Tabela | SELECT | Consulta do último movimento contábil gravado (MySQL) |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| CCBDContaCorrente.TbMovimentoContabil | Tabela | INSERT | Inserção de novos movimentos contábeis analíticos (MySQL) |
| DBCONTACORRENTE.dbo.TbLoteMovimentoContabil | Tabela | UPDATE | Atualização do flag de geração do lote para 'S' após processamento |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| log/robo.log | Gravação | Log4j (RollingFileAppender) | Log principal da aplicação com rotação de 2MB |
| log/statistics-${executionId}.log | Gravação | Log4j (BvDailyRollingFileAppender) | Log de estatísticas do framework batch |

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
| **Sybase DBCONTACORRENTE** | Banco de Dados | Base origem com histórico de movimentações de contas correntes (leitura) |
| **MySQL CCBDContaCorrente** | Banco de Dados | Base destino para armazenamento de movimentações analíticas contábeis (escrita) |

**Detalhes de Conexão:**
- **Sybase**: Servidores variam por ambiente (sybdesbco.bvnet.bv:7500 em DES, moruatbco.bvnet.bv:4400 em UAT, morsybbco.bvnet.bv:3000 em PRD)
- **MySQL**: Servidores variam por ambiente (gcmysdgdes04-proxy.bvnet.bv:3306 em DES, gcmysdguat04-proxy.bvnet.bv:3306 em UAT, gcmysdgprd04-proxy.bvnet.bv:3306 em PRD)

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Separação clara de responsabilidades (Reader, Processor, Writer)
- Uso de interfaces para repositories (boa prática de abstração)
- Tratamento de exceções com códigos de erro específicos
- Configuração externalizada por ambiente (DES/UAT/PRD)
- Uso de framework batch estruturado

**Pontos Negativos:**
- **Queries SQL hardcoded em Strings**: A classe `Queries` contém SQLs complexos concatenados em Strings, dificultando manutenção e legibilidade
- **Código de banco hardcoded**: O valor 413 está fixo no `ListaMovAnaliticoMapper`, deveria ser configurável
- **ItemProcessor vazio**: Não realiza nenhuma transformação, questionável sua necessidade
- **Tratamento genérico de exceções**: Captura `Exception` e `Error` de forma muito ampla
- **Falta de documentação**: Ausência de JavaDoc nas classes e métodos
- **SQL com tabela temporária**: A query de consulta cria tabela temporária (#analitica), o que pode causar problemas de concorrência
- **Mistura de responsabilidades**: ItemReader realiza lógica de negócio (marcação de último registro)
- **Logs com caracteres especiais**: Comentários e mensagens com caracteres acentuados mal codificados
- **Falta de testes**: Apenas um teste de integração básico
- **Magic numbers e strings**: Valores como "436", "2020", "S", "N" espalhados pelo código

---

## 14. Observações Relevantes

1. **Dependência de Framework Proprietário**: O sistema utiliza o framework `bv-framework-batch` que é proprietário da BV Sistemas, limitando portabilidade
2. **Processamento Sequencial**: O sistema processa movimentações de forma sequencial (item a item), sem paralelização
3. **Isolamento de Transação**: Utiliza `at ISOLATION 0` na query principal, indicando leitura não comprometida (dirty read)
4. **Criptografia de Senhas**: Em produção, utiliza `BVCrypto` para descriptografar senhas do banco
5. **Múltiplas Fontes de Dados**: Consulta tanto `tbhistoricomovimento` quanto `tbmovimentodia` para cobrir histórico e movimentações do dia
6. **Estratégia de Resume Desabilitada**: A classe `MyResumeStrategy` sempre retorna `false`, não permitindo retomada de jobs
7. **Configuração de Pool**: Pools de conexão configurados com mínimo de 1 e máximo de 10 conexões
8. **Transações Locais**: Permite transações locais (`allowLocalTransactions=true`) apesar de usar gerenciador JTA
9. **Versão do Projeto**: Sistema na versão 0.6.0, indicando ainda em fase de evolução
10. **Desabilitação de Deploy QA**: Propriedade `disableQADeploy=true` no jenkins.properties indica que não há deploy automático em ambiente de QA