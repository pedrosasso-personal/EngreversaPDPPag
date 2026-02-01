# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java desenvolvido para automatizar a consulta e análise de fichas de correspondentes bancários junto ao serviço UpMiner. O sistema identifica fichas cadastrais que necessitam análise PLD (Prevenção à Lavagem de Dinheiro), cria lotes de consulta no UpMiner separando pessoas físicas e jurídicas do quadro societário, e gerencia o ciclo de vida dessas análises. Utiliza integração via API REST com o UpMiner para criação e processamento de lotes de consulta.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê fichas de correspondentes bancários com status "Enviado para Análise PLD" do banco de dados e valida se possuem quadro societário completo |
| **ItemProcessor** | Processa cada ficha, valida se já possui lotes criados, separa sócios PF/PJ, cria novos lotes no UpMiner via API e trata erros |
| **ItemWriter** | Adiciona lotes criados na fila de processamento do UpMiner e persiste informações de análise no banco de dados |
| **ConsultarUpMinerServicesImpl** | Implementa regras de negócio: validação de lotes, separação de sócios por tipo, integração com API UpMiner (autenticação OAuth2, criação de lotes) |
| **ConsultarUpMinerDAOImpl** | Gerencia acesso ao banco de dados Sybase: consultas, inserções e atualizações de fichas, lotes e sócios |
| **FichaCorrespondente** | Entidade representando uma ficha cadastral de correspondente bancário |
| **Lote** | Entidade representando um lote de consulta no UpMiner (PF ou PJ) |
| **Socio** | Entidade representando um sócio do quadro societário |

## 3. Tecnologias Utilizadas

- **Java** com Maven
- **Spring Framework 2.0** (IoC/DI, JDBC)
- **BV Framework Batch** (framework proprietário para processamento batch)
- **Bitronix** (gerenciador de transações JTA)
- **Sybase/SQL Server** (banco de dados)
- **Apache HttpClient** e **HttpURLConnection** (integração REST)
- **Gson** (parsing JSON)
- **Log4j** (logging)
- **JUnit** (testes)
- **OAuth 2.0** (autenticação API)

## 4. Principais Endpoints REST

Não se aplica - o sistema é um job batch que **consome** APIs externas, não expõe endpoints REST.

**APIs Consumidas (UpMiner):**

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/auth/oauth/v2/token` | Autenticação OAuth2 para obter access token |
| POST | `/v1/parceiros/upminer/lotes/criar` | Criação de novo lote de consulta no UpMiner |
| POST | `/v1/parceiros/upminer/lotes/processamento` | Adiciona lote na fila de processamento |

## 5. Principais Regras de Negócio

- Apenas fichas com status "Enviado para Análise PLD" (código 14) são processadas
- Fichas sem quadro societário completo ou sem sócios PF são excluídas do processamento
- Lotes são criados separadamente para Pessoa Física (PF) e Pessoa Jurídica (PJ)
- O CNPJ do correspondente (COBAN) é sempre incluído no lote PJ
- Validação de atualização de lotes: compara quadro societário atual com o registrado no lote anterior
- Se o quadro societário mudou, lotes antigos são excluídos e novos são criados
- Máximo de 5 tentativas de execução por ficha (QtExecucaoAnaliseFicha <= 5)
- Perfis diferentes são aplicados para prospects e não-prospects
- Tribunais Regionais Federais (TRF) são mapeados por UF, com TRF4 sempre incluído
- Fichas com erro na criação de lotes são enviadas para validação manual com parecer automático
- Limite de 1023 itens em cláusulas IN do SQL (MAXIMO_ITENS_IN)

## 6. Relação entre Entidades

**FichaCorrespondente** (1) ----< (N) **Lote**
- Uma ficha pode ter múltiplos lotes (tipicamente 2: um PF e um PJ)
- Relacionamento: `cdFichaCorrespondenteBancario`

**Lote** (1) ----< (N) **Socio**
- Um lote contém múltiplos sócios do quadro societário
- Relacionamento: `cdAnaliseFichaCorrespondente`

**Atributos principais:**
- FichaCorrespondente: cdFichaCorrespondenteBancario, nuCNPJFicha, cdUf, trf, novo, prospect
- Lote: cdAnaliseFichaCorrespondente, cdLoteFonteExterna, tpLote (F/J), listQuadroSocietario
- Socio: nuCpfCnpjSocioCorrespondente, tpPessoaSocio, pcCapitalSocial, cdDossieFonteExterna

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbFichaCorrespondenteBancario | Tabela | SELECT | Fichas cadastrais de correspondentes bancários |
| TbAnaliseFichaCorrespondente | Tabela | SELECT | Lotes de análise PLD associados às fichas |
| TbRegistroCorrespondenteBancro | Tabela | SELECT | Dados de registro do correspondente (CNPJ) |
| TbSocioCorrespondente | Tabela | SELECT | Quadro societário das fichas |
| TbAnaliseSocioCorrespondente | Tabela | SELECT | Sócios incluídos em análises anteriores |
| TbSequencial | Tabela | SELECT | Controle de sequenciais para PKs |
| TbFichaCorrespondenteMtvoAnlse | Tabela | SELECT | Motivos de análise (identifica prospects) |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbAnaliseFichaCorrespondente | Tabela | INSERT | Criação de novos registros de lote de análise |
| TbAnaliseFichaCorrespondente | Tabela | UPDATE | Atualização de status e contadores de execução |
| TbAnaliseFichaCorrespondente | Tabela | DELETE | Remoção de lotes desatualizados |
| TbAnaliseSocioCorrespondente | Tabela | INSERT | Registro de sócios incluídos no lote |
| TbAnaliseSocioCorrespondente | Tabela | DELETE | Remoção de sócios de lotes desatualizados |
| TbSequencial | Tabela | UPDATE | Atualização de sequenciais após uso |
| TbParecerFichaCorrespondente | Tabela | INSERT | Registro de pareceres para fichas com erro |
| TbFichaCorrespondenteBancario | Tabela | UPDATE | Alteração de status para validação manual (código 16) |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| config.properties | Leitura | GetPropertyValues / conf/ | Configurações da API UpMiner (client_id, client_secret, URL, perfis) |
| log4j.xml | Leitura | Configuração Log4j | Configuração de logging do sistema |
| robo.log | Gravação | Log4j RollingFileAppender | Log principal da aplicação |
| statistics-{executionId}.log | Gravação | BvDailyRollingFileAppender | Log de estatísticas de execução |

## 10. Filas Lidas

Não se aplica - o sistema não consome mensagens de filas JMS, Kafka ou RabbitMQ.

## 11. Filas Geradas

Não se aplica - o sistema não publica mensagens em filas. A "fila" mencionada no código refere-se à fila de processamento interna do UpMiner, acionada via API REST.

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **API UpMiner** | REST/HTTPS | Serviço de análise PLD. Autenticação OAuth2, criação de lotes de consulta (PF/PJ), adição de lotes na fila de processamento |
| **Banco Sybase** | JDBC | Banco de dados DbCorrespondenteBancario - leitura e gravação de fichas, lotes e análises |

**Detalhes API UpMiner:**
- Base URL: https://api-des.bancovotorantim.com.br (ambiente desenvolvimento)
- Autenticação: OAuth 2.0 Client Credentials
- Perfis configuráveis por tipo (PF/PJ) e situação (prospect/não-prospect)
- Parâmetros: tipo pessoa, perfil, TJ (Tribunal de Justiça por UF), TRF (Tribunal Regional Federal)

## 13. Avaliação da Qualidade do Código

**Nota: 5/10**

**Justificativa:**

**Pontos Positivos:**
- Separação clara de responsabilidades (Reader/Processor/Writer)
- Uso de padrões DAO e Service
- Configuração externalizada (properties, XML)
- Tratamento de erros com envio para validação manual

**Pontos Negativos:**
- **Código comentado extensivamente** (comentários em português com erros de encoding)
- **Mistura de responsabilidades**: ConsultarUpMinerServicesImpl contém lógica de integração HTTP que deveria estar em classe separada
- **Hardcoding**: Strings SQL construídas manualmente em ConsultarUpMinerDAOProperties ao invés de usar o arquivo .bv-sql
- **Falta de tratamento de exceções**: Múltiplos blocos catch vazios ou apenas com `e.getMessage()`
- **Código duplicado**: Lógica similar para PF e PJ repetida
- **Magic numbers**: Códigos de status (14, 16) e outros valores sem constantes nomeadas
- **Falta de validações**: Pouca validação de entrada e estados inconsistentes
- **Logging inconsistente**: Mistura de System.out.println com logger
- **Código morto**: Método getConnection() comentado e não utilizado
- **Complexidade ciclomática alta**: Métodos muito longos (ex: handleProcess, upMinerPostLoteNew, isLoteAtualizado)
- **Falta de testes**: Apenas um teste de integração básico

## 14. Observações Relevantes

- O sistema utiliza um framework proprietário (BV Framework) que abstrai parte da infraestrutura batch
- Configuração de datasource usa Bitronix para gerenciamento de transações XA
- O banco de dados é Sybase (DbCorrespondenteBancario) acessado via driver JTDS
- Existe inconsistência entre o arquivo .bv-sql (não utilizado) e as queries construídas em ConsultarUpMinerDAOProperties
- O sistema possui lógica de retry (até 5 tentativas) mas não implementa backoff exponencial
- Mapeamento UF -> TRF hardcoded em método setMap()
- Token OAuth2 não é cacheado, sendo solicitado a cada requisição
- Encoding ISO-8859-1 configurado para o banco de dados
- Versão do Spring Framework (2.0) está muito desatualizada
- O projeto está configurado para ambiente de desenvolvimento (URLs, credenciais)