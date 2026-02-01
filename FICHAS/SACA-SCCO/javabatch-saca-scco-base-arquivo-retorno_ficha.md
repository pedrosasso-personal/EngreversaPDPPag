---
## Ficha Técnica do Sistema

### 1. Descrição Geral
Sistema batch Java responsável pelo processamento de arquivos de retorno bancário no formato CNAB 400. O sistema lê arquivos de retorno de múltiplos bancos (Banco do Brasil, Bradesco, Itaú, Santander e Votorantim), valida as informações, registra situações de processamento, trata rejeições, atualiza hash MD5 e linha digitável de boletos, e publica mensagens em filas RabbitMQ para contratos de carnê acatados. Implementa regras específicas de negócio para cada banco, incluindo validação de ocorrências, tratamento de rejeições e cálculo de códigos de barras.

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê arquivos CNAB do diretório configurado, organiza por banco, valida data de modificação, renomeia/exclui arquivos inválidos |
| **ItemProcessor** | Processa linhas CNAB, valida ocorrências, registra situações, gera hash MD5, calcula linha digitável, publica mensagens RabbitMQ |
| **ItemWriter** | Persiste situações de processamento e ocorrências de rejeição no banco de dados |
| **DatabaseConnection** | Gerencia conexões JDBC singleton com autoCommit desabilitado |
| **LinhaDigitavelBusiness** | Calcula linha digitável e código de barras para boletos de diferentes bancos |
| **InstrumentoCobrancaDAO** | CRUD para TbRegistroInstrumentoCobranca, valida reprocessamento, atualiza hash e linha digitável |
| **OcorrenciaBoletoDAO** | Gerencia ocorrências de boleto, insere novas ocorrências não cadastradas |
| **SituacaoProcessamentoDAO** | Insere registros de situação de processamento |
| **OcorrenciaRejeicaoDAO** | Insere ocorrências de rejeição |
| **SubOcorrenciaRejeicaoBoletoDAO** | Gerencia sub-ocorrências de rejeição |
| **ConvenioBoletoDAO** | Consulta convênios de boleto com cache |
| **RabbitRepositoryImpl** | Implementa publicação transacional de mensagens RabbitMQ |
| **MyResumeStrategy** | Estratégia de retomada de processamento batch após erros |
| **Util Classes** (BancoBrasilUtil, BradescoUtil, etc.) | Parse de linhas CNAB específicas de cada banco para VOs |
| **CodigoDeBarraUtil** | Helpers para cálculo de dígitos verificadores (mod10/mod11) |

### 3. Tecnologias Utilizadas

- **Framework Batch**: Spring Batch (bv-framework-batch)
- **Linguagem**: Java
- **Banco de Dados**: Sybase (JDBC)
- **Mensageria**: RabbitMQ 4.11.3 (com.rabbitmq.client)
- **Gerenciamento de Transações**: Bitronix (mencionado em scripts)
- **Build**: Maven
- **Logging**: Log4j
- **Criptografia**: MessageDigest MD5
- **Containerização**: Docker (docker-compose para RabbitMQ)
- **Bibliotecas**: commons-lang3, bv-crypto
- **Formato de Arquivo**: CNAB 400 (posicional)

### 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch sem endpoints REST.

### 5. Principais Regras de Negócio

1. **Validação de Reprocessamento**: Impede processamento de arquivos com mesmo nome no mesmo dia através de consulta em TbSituacaoProcessamentoInsto
2. **Forçar Acatamento de Rejeições Específicas**: 
   - Rejeições "nosso número existente" (código 23-Votorantim, 33-BB) são forçadas como acatadas
   - Rejeições "data vencimento anterior à emissão" (código 13-Votorantim, 38-BB) são forçadas como acatadas
3. **Ignorar Atualização de Mora BB**: Ignora processamento de comando 16 com ocorrências 00/84 do Banco do Brasil
4. **Validação de Ocorrências**: Valida se ocorrência está cadastrada; se não existir, insere com estado rejeitado (código 3)
5. **Cálculo de Linha Digitável**: Calcula linha digitável específica para banco Votorantim usando regras próprias
6. **Publicação Seletiva em Fila**: Publica mensagem RabbitMQ apenas para:
   - Contratos de carnê
   - Situação acatada
   - Contrato não repetido na mesma execução
   - Tipo de produto diferente de Neon (subprodutos 85, 86)
7. **Commit em Lote**: Realiza commit manual a cada 10.000 registros processados
8. **Validação de Data de Arquivo**: Processa apenas arquivos com data de modificação igual ao dia corrente
9. **Renomeação de Arquivos**: Arquivos inválidos são renomeados com sufixo "_PROC"
10. **Exclusão de Arquivos Antigos**: Arquivos com mais de 5 dias são excluídos
11. **Cálculo de Fator de Vencimento**: Usa data base 07/10/1997; se data > 21/02/2025, soma 1000 dias
12. **Suporte Multi-Banco**: Processa arquivos de 5 bancos diferentes com regras específicas para cada um

### 6. Relação entre Entidades

**Entidades Principais e Relacionamentos:**

- **TbRegistroInstrumentoCobranca** (entidade central)
  - → **TbSituacaoProcessamentoInsto** (1:N) - Histórico de situações de processamento
  - → **TbOcorrenciaRejeicaoPrcso** (1:N) - Ocorrências de rejeição associadas
  
- **TbOcorrenciaBoleto** (catálogo de ocorrências)
  - → **TbSubOcorrenciaRejeicaoBoleto** (1:N) - Sub-ocorrências detalhadas
  
- **TbCarneControleEnvio** (controle de convênios)
  - Relacionada com TbRegistroInstrumentoCobranca via nuConvenioCobranca

- **DbGestaoCP..TbContrato** (cross-database)
  - → **DBCRED..TbProposta** (JOIN) - Para validação de tipo Neon

**Fluxo de Dados:**
1. Arquivo CNAB → InputUnitOfWork
2. Parse CNAB → VOs específicos por banco (Header/Detalhe/Trailler)
3. Validação → TbRegistroInstrumentoCobranca
4. Processamento → TbSituacaoProcessamentoInsto + TbOcorrenciaRejeicaoPrcso
5. Publicação → RabbitMQ (para carnês acatados)

### 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbRegistroInstrumentoCobranca | Tabela | SELECT | Consulta instrumentos de cobrança por nosso número, banco e convênio (excluindo situações 11/12/13) |
| TbSituacaoProcessamentoInsto | Tabela | SELECT | Consulta arquivos processados no dia para validar reprocessamento |
| TbOcorrenciaBoleto | Tabela | SELECT | Consulta ocorrências cadastradas por banco e código de ocorrência |
| TbSubOcorrenciaRejeicaoBoleto | Tabela | SELECT | Consulta sub-ocorrências de rejeição por código de ocorrência |
| TbCarneControleEnvio | Tabela | SELECT | Consulta convênio de boleto (TOP 1 ORDER BY dt_inc DESC) |
| DbGestaoCP..TbContrato | Tabela | SELECT | Valida se contrato é tipo Neon (cross-database join com TbProposta) |
| DBCRED..TbProposta | Tabela | SELECT | Join para validação de subproduto Neon (códigos 85, 86) |

### 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbRegistroInstrumentoCobranca | Tabela | UPDATE | Atualiza CdHashBoleto (MD5) e NuDigitavelCodigoBarra quando valores são nulos |
| TbSituacaoProcessamentoInsto | Tabela | INSERT | Insere nova situação de processamento com estado, comando, tipo e arquivo origem |
| TbOcorrenciaRejeicaoPrcso | Tabela | INSERT | Insere ocorrências de rejeição com código de registro, data e descrição |
| TbOcorrenciaBoleto | Tabela | INSERT | Insere novas ocorrências não cadastradas com estado rejeitado (código 3) |
| TbSubOcorrenciaRejeicaoBoleto | Tabela | INSERT | Insere novas sub-ocorrências não cadastradas |

### 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| Arquivos CNAB 400 | Leitura | ItemReader / diretorioArquivos (injetado) | Arquivos de retorno bancário organizados em subdiretórios por código de banco (001, 237, 033, 341, 655) |
| Arquivos *_PROC | Gravação | ItemReader | Arquivos inválidos renomeados com sufixo "_PROC" |
| robo.log | Gravação | Log4j (RollingFileAppender) | Log de execução do batch (máximo 100MB) |
| statistics.log | Gravação | Log4j (DailyRollingFileAppender) | Log de estatísticas diárias |
| Bitronix logs | Leitura/Exclusão | processar-arquivos-retorno.bat | Logs de transação limpos antes da execução |

### 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas, apenas publica.

### 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Responsável | Breve Descrição |
|--------------|-----------|-------------------|-----------------|
| RabbitMQ (routing key configurável) | RabbitMQ | RabbitRepositoryImpl / ItemProcessor | Publica mensagens com payload contendo numeroContrato, sequenciaContratoFinanceiro e codigoVeiculoLegal para contratos de carnê acatados (exceto tipo Neon) |
| entrega-documento (teste) | RabbitMQ | job-resources.xml (test) | Exchange/queue configurada para ambiente de teste |

**Características da Publicação:**
- Canal transacional (txSelect/txCommit/txRollback)
- Mensagens persistentes (MessageProperties.PERSISTENT_TEXT_PLAIN)
- Commit coordenado com transação JDBC
- Controle de duplicação por contrato na mesma execução

### 12. Integrações Externas

| Sistema/Serviço | Tipo | Classe Responsável | Breve Descrição |
|-----------------|------|-------------------|-----------------|
| RabbitMQ | Mensageria | RabbitRepositoryImpl | Publicação transacional de mensagens para processamento de carnês acatados |
| Sybase Database (dbcarne) | Banco de Dados | DatabaseConnection / DAOs | Persistência de dados de cobrança e situações de processamento |
| DbGestaoCP (cross-database) | Banco de Dados | SubProdutoDAO | Consulta de contratos para validação de tipo Neon |
| DBCRED (cross-database) | Banco de Dados | SubProdutoDAO | Consulta de propostas vinculadas a contratos |
| Sistema de Arquivos | File System | ItemReader | Leitura de arquivos CNAB de diretórios organizados por banco |

**Bancos Suportados:**
- Banco do Brasil (001)
- Bradesco (237)
- Santander (033)
- Itaú (341)
- Votorantim (655)

### 13. Avaliação da Qualidade do Código

**Nota: 4/10**

**Justificativa:**

**Pontos Negativos:**
1. **Método Gigante**: ItemProcessor.handleProcess possui mais de 300 linhas, violando princípios de responsabilidade única e dificultando manutenção
2. **Código Hardcoded**: Lógica específica de cada banco (processaLinhasVotorantim, BB, Bradesco, etc.) está embutida no processador principal ao invés de usar Strategy Pattern
3. **Thread-Safety**: Variáveis estáticas compartilhadas (qtdLinhaComitar, mqControle) tornam o código não thread-safe
4. **Duplicação de Código**: Classes comentadas (ProcessaLinhaArquivoBV, ProcessaRetornoArquivoBB) indicam duplicação de lógica não refatorada
5. **Commits Manuais**: Controle manual de commit a cada 10k registros aumenta complexidade e risco de inconsistência
6. **Cache Manual**: Implementação própria de cache (GenericObjectCache) sem thread-safety ao invés de usar soluções consolidadas
7. **Enum com Código Duplicado**: ErroEnum possui código 14 duplicado (ERRO_PROCESSAMENTO_LINHA e ERRO_GERACAO_HASHCODE)
8. **Tratamento de Erros Inconsistente**: ItemWriter ignora erros de gravação apenas logando warning
9. **Acoplamento Alto**: Dependência direta de implementações concretas ao invés de interfaces
10. **Falta de Testes**: Apenas um teste de integração básico

**Pontos Positivos:**
1. **Separação de Responsabilidades**: Uso adequado do padrão Reader/Processor/Writer do Spring Batch
2. **VOs Bem Definidos**: Objetos de valor específicos para cada banco facilitam mapeamento CNAB
3. **Utilitários Reutilizáveis**: Classes helper para formatação e cálculos (CodigoDeBarraUtil, FormataCampo)
4. **Transações Coordenadas**: Integração transacional entre JDBC e RabbitMQ

**Recomendações:**
- Refatorar ItemProcessor usando Strategy Pattern para cada banco
- Implementar pool de conexões adequado
- Adicionar testes unitários e de integração abrangentes
- Remover código comentado e classes não utilizadas
- Usar cache thread-safe (Caffeine, Guava)
- Extrair constantes mágicas para configuração
- Implementar retry e circuit breaker para integrações

### 14. Observações Relevantes

1. **Formato CNAB 400**: Sistema processa exclusivamente arquivos no formato CNAB 400 posicional, não suportando CNAB 240
2. **Limite de Commit**: Configurado para commit a cada 10.000 registros para otimizar performance e reduzir lock de banco
3. **Validação de Data**: Arquivos devem ter data de modificação igual ao dia corrente, caso contrário são ignorados ou renomeados
4. **Reprocessamento Bloqueado**: Sistema impede reprocessamento de arquivos com mesmo nome no mesmo dia através de validação em banco
5. **Regras Específicas por Banco**: Cada banco possui parser e regras de validação específicas implementadas em classes Util separadas
6. **Cross-Database Queries**: Sistema realiza consultas entre databases diferentes (DbGestaoCP e DBCRED) para validação de tipo Neon
7. **Ambiente Docker**: Configuração docker-compose disponível para RabbitMQ local (desenvolvimento/teste)
8. **Scripts de Execução**: Fornece scripts .bat (Windows) e .sh (Linux) para execução do batch
9. **Logs Estruturados**: Separação entre logs de aplicação (robo.log) e estatísticas (statistics.log)
10. **Versionamento**: Sistema na versão 0.6.2, indicando ainda em evolução
11. **Parent POM**: Herda de bv-sistemas-master 13.0.19, sugerindo padrão corporativo
12. **Bitronix Transaction Manager**: Utiliza Bitronix para gerenciamento de transações distribuídas (JDBC + RabbitMQ)
13. **Fator de Vencimento**: Implementa regra específica de boleto brasileiro com data base 07/10/1997 e ajuste para datas após 21/02/2025
14. **Carnê vs Boleto Avulso**: Sistema diferencia tratamento entre carnês (publica em fila) e boletos avulsos
15. **Exclusão Automática**: Arquivos com mais de 5 dias são automaticamente excluídos do diretório de processamento