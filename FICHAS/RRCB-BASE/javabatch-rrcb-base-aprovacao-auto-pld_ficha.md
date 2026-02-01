# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java desenvolvido para automação da aprovação de análises PLD (Prevenção à Lavagem de Dinheiro) de fichas de correspondentes bancários. O sistema integra-se com a plataforma UpMiner para consultar dossiês de análise de risco, verificar status de processamento de lotes, identificar apontamentos (PEP - Pessoas Politicamente Expostas e municípios fronteiriços) e aprovar automaticamente fichas sem restrições ou encaminhá-las para análise manual quando necessário.

O processamento segue o padrão Reader-Processor-Writer, onde fichas em análise PLD são lidas do banco de dados, validadas contra a API UpMiner, e então aprovadas automaticamente ou direcionadas para validação manual conforme regras de negócio estabelecidas.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê fichas de correspondentes bancários com status "em análise PLD" do banco de dados |
| **ItemProcessor** | Valida fichas consultando status dos lotes no UpMiner e verificando se todos os dossiês foram processados |
| **ItemWriter** | Grava resultados: aprova fichas automaticamente, envia para análise manual ou solicita reprocessamento |
| **AprovarUpMinerServicesImpl** | Implementa lógica de negócio e integração com API UpMiner (OAuth2, consultas de lotes e dossiês) |
| **AprovarUpMinerDAOImpl** | Acesso a dados: consultas e atualizações no banco de dados Sybase |
| **FichaCorrespondente** | Entidade representando ficha de correspondente bancário com seus lotes |
| **Lote** | Entidade representando lote de análise com quadro societário |
| **Socio** | Entidade representando sócio/pessoa do quadro societário |
| **DossieApontamento** | DTO com informações de dossiê (workflow, PEP, fronteiriço) |
| **AcaoFichaEnum** | Enumeração com ações possíveis para fichas (aprovar, análise manual, reprocessar, etc) |

## 3. Tecnologias Utilizadas

- **Java** (versão não especificada no código)
- **Maven** - Gerenciamento de dependências e build
- **Spring Framework 2.0** - Injeção de dependências e configuração
- **BV Framework Batch** - Framework proprietário para processamento batch
- **Spring JDBC** (NamedParameterJdbcTemplate) - Acesso a dados
- **Bitronix** - Gerenciador de transações JTA
- **Sybase ASE** - Banco de dados (via JTDS driver)
- **Gson** - Parsing de JSON para integração com API REST
- **Log4j** - Logging
- **JUnit** - Testes unitários
- **API REST UpMiner** - Integração externa via HTTP/HTTPS com autenticação OAuth2

## 4. Principais Endpoints REST

Não se aplica - este é um sistema batch que **consome** endpoints REST externos, mas não expõe endpoints próprios.

**Endpoints consumidos da API UpMiner:**
- `POST /auth/oauth/v2/token` - Autenticação OAuth2
- `GET /v1/parceiros/upminer/lotes/situacao` - Consulta status de lote
- `GET /v1/parceiros/upminer/lista-dossie` - Lista dossiês de um lote
- `GET /v1/parceiros/upminer/dossies/obter` - Obtém detalhes de dossiê específico

## 5. Principais Regras de Negócio

1. **Seleção de Fichas**: Apenas fichas com status "ENVIADO ANALISE PLD" (status 14) e lotes em processamento (status 'P') são processadas
2. **Validação de Lotes**: Todos os lotes da ficha devem estar com status "PROCESSADO" (4) ou "PROCESSADO_COM_EXCEÇÃO" (5) no UpMiner
3. **Reprocessamento**: Fichas com lotes processados com exceção são reprocessadas até 6 tentativas, após isso vão para análise manual
4. **Aprovação Automática**: Ficha é aprovada automaticamente se:
   - Todos os dossiês têm workflow status "aprovado"
   - Nenhum sócio é PEP (Pessoa Politicamente Exposta)
   - Nenhum sócio está em município fronteiriço
5. **Classificação de Risco**: 
   - Risco BAIXO: tempo de relacionamento com BV >= 5 anos
   - Risco MÉDIO: tempo de relacionamento < 5 anos
6. **Análise Manual**: Ficha vai para análise manual se:
   - Houver apontamentos no workflow
   - Houver PEP ou fronteiriço identificado
   - Dossiê sem informação de workflow
   - Excedido limite de reprocessamentos (6 tentativas)

## 6. Relação entre Entidades

```
FichaCorrespondente (1) -----> (N) Lote
                                  |
                                  v
                            (N) Socio
```

- **FichaCorrespondente**: Representa a ficha cadastral do correspondente bancário
  - Contém lista de Lotes
  - Possui CNPJ do correspondente
  - Tem ação de processamento (aprovar, análise manual, etc)
  
- **Lote**: Representa um lote de análise enviado ao UpMiner
  - Pertence a uma FichaCorrespondente
  - Contém lista de Sócios (quadro societário)
  - Possui código externo do lote no UpMiner
  
- **Socio**: Representa pessoa física ou jurídica do quadro societário
  - Pertence a um Lote
  - Possui CPF/CNPJ e código de dossiê no UpMiner
  - Tem flags de PEP e fronteiriço

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbAnaliseFichaCorrespondente | Tabela | SELECT | Lista fichas em análise PLD e seus lotes |
| TbFichaCorrespondenteBancario | Tabela | SELECT | Dados da ficha do correspondente bancário |
| TbRegistroCorrespondenteBancro | Tabela | SELECT | Registro do correspondente (CNPJ) |
| TbAnaliseSocioCorrespondente | Tabela | SELECT | Sócios/pessoas do quadro societário |
| TbPessoa (dbcor) | Tabela | SELECT | Consulta tempo de relacionamento com BV |
| TbParceiroComercial (dbcor) | Tabela | SELECT | Relacionamento de parceiros comerciais |
| TbSequencial | Tabela | SELECT | Obtém sequencial para TbParecerFichaCorrespondente |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbFichaCorrespondenteBancario | Tabela | UPDATE | Atualiza status de análise e risco PLD da ficha |
| TbAnaliseFichaCorrespondente | Tabela | UPDATE | Atualiza status e data de conclusão da análise |
| TbParecerFichaCorrespondente | Tabela | INSERT | Grava parecer técnico da análise PLD |
| TbSequencial | Tabela | UPDATE | Atualiza sequencial disponível |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| conf/config.properties | Leitura | GetPropertyValues | Configurações da API UpMiner (client_id, client_secret, URL) |
| log/robo.log | Gravação | Log4j (roboFile appender) | Log geral da aplicação |
| log/statistics-{executionId}.log | Gravação | Log4j (statistics appender) | Log de estatísticas de execução do batch |

## 10. Filas Lidas

Não se aplica - o sistema não consome mensagens de filas.

## 11. Filas Geradas

Não se aplica - o sistema não publica mensagens em filas.

## 12. Integrações Externas

| Sistema/API | Tipo | Descrição |
|-------------|------|-----------|
| **API UpMiner** | REST/HTTPS | Plataforma de análise de risco PLD. Integração via OAuth2 para consultar status de lotes, listar dossiês e obter detalhes de análises (workflow, PEP, fronteiriço) |
| **Banco Sybase (DbCorrespondenteBancario)** | JDBC | Banco de dados principal com informações de fichas, lotes e análises |
| **Banco Sybase (dbcor)** | JDBC | Banco corporativo para consulta de tempo de relacionamento de clientes |

## 13. Avaliação da Qualidade do Código

**Nota: 5/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem definida com separação de responsabilidades (DAO, Service, Batch)
- Uso adequado de padrões (DAO, Service, DTO)
- Logging presente em pontos críticos
- Tratamento de exceções em operações críticas

**Pontos Negativos:**
- **Código legado com problemas graves**: Comentários indicam código alternativo comentado para geração de sequenciais (método `getConnection()` hardcoded)
- **Strings SQL concatenadas**: Queries SQL construídas por concatenação de strings, vulnerável a SQL injection e difícil manutenção
- **Hardcoding de valores**: URLs, credenciais e configurações misturadas no código
- **Falta de constantes**: Valores mágicos espalhados (status "P", "S", "E", códigos 14, 10, 16)
- **Métodos muito longos**: `handleWrite()` e `upMinerGetDossieView()` com lógica complexa e aninhada
- **Encoding problemático**: Caracteres especiais mal codificados (��) indicando problemas de charset
- **Falta de testes**: Apenas um teste de integração básico
- **Tratamento de erro genérico**: Muitos `catch (Exception e)` sem tratamento específico
- **Código morto**: Método `getConnection()` comentado mas não removido
- **Nomenclatura inconsistente**: Mistura de português e inglês

## 14. Observações Relevantes

1. **Ambiente de Desenvolvimento**: Configurações apontam para ambiente de desenvolvimento (api-des.bancovotorantim.com.br, servidor ptasybdes15)

2. **Limite de Reprocessamento**: Sistema permite até 6 tentativas de reprocessamento antes de enviar para análise manual

3. **Problema de Encoding**: Código fonte apresenta caracteres corrompidos (��) em strings, indicando problemas de encoding ISO-8859-1 vs UTF-8

4. **Dependência de Framework Proprietário**: Uso extensivo do BV Framework (framework proprietário do Banco Votorantim), dificultando portabilidade

5. **Segurança**: Credenciais OAuth2 armazenadas em arquivo properties sem criptografia aparente

6. **Transações**: Configuração indica uso de transações locais (`allowLocalTransactions=true`) com Bitronix JTA

7. **Versionamento**: Versão 19.3.3.AUTO119.1 sugere processo de versionamento automatizado

8. **Banco de Dados**: Sistema utiliza Sybase ASE com driver JTDS, charset ISO-8859-1

9. **Processamento**: Commit interval configurado para 1, processando ficha por ficha

10. **Exit Codes**: Sistema define códigos de saída específicos (10 para erro de processamento, 20 para erro de sequencial) para integração com scheduler UC4