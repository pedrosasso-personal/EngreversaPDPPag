# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java responsável por processar e gerar relatórios de estornos não ocorridos em transações de cartão de débito. O sistema consulta transações marcadas como não estornadas no banco de dados CCBD, processa essas informações e gera um arquivo CSV com os detalhes das transações para análise e conciliação.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê registros de estornos não processados do banco de dados através do repositório |
| **ItemProcessor** | Processa e mapeia objetos Estorno para RegistroEstorno |
| **ItemWriter** | Gera arquivo CSV com os registros de estorno processados |
| **EstornoRepositoryImpl** | Implementa acesso ao banco de dados para consultar transações não estornadas |
| **ArquivoService** | Gerencia operações de criação, escrita e exclusão de arquivos |
| **NaoEstornadoMapper** | Mapeia ResultSet do banco para objetos Estorno |
| **RegistroEstornoMapper** | Converte objetos Estorno em RegistroEstorno |
| **ArquivoEstornoMapper** | Gera cabeçalho e linhas do arquivo CSV usando reflection |
| **Cartao** | Entidade de domínio representando dados do cartão |
| **Estorno** | Entidade de domínio representando transação de estorno |
| **RegistroEstorno** | DTO para representação de registro no arquivo de saída |

---

## 3. Tecnologias Utilizadas

- **Java** (linguagem principal)
- **Maven** (gerenciamento de dependências e build)
- **Spring Framework** (injeção de dependências e configuração)
- **BV Framework Batch** (framework proprietário para processamento batch)
- **Bitronix** (gerenciador de transações JTA)
- **Spring JDBC** (acesso a dados)
- **SQL Server** (banco de dados - driver JTDS)
- **Log4j** (logging)
- **JUnit** (testes unitários)
- **Mockito** (mocks para testes)

---

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch sem endpoints REST.

---

## 5. Principais Regras de Negócio

1. **Seleção de Transações**: Busca apenas transações com flag `FlBase2Estornado = 'N'` (não estornadas)
2. **Extração de Dados do Cartão**: A partir do número de identificação quina do cartão (16 dígitos), extrai:
   - Código do produto (2 primeiros dígitos)
   - Número da conta (dígitos 3 a 11)
   - Número correlativo (dígitos 12 a 16)
3. **Geração de Arquivo**: Cria arquivo CSV com nomenclatura `Estornos_nao_ocorridos_DD-MM-YYYY HH-MM-SS.csv`
4. **Processamento em Lote**: Commit a cada 10.000 registros (configurado no job-definitions.xml)
5. **Códigos de Saída Customizados**:
   - Código 10: Nenhum registro encontrado
   - Código 20: Erro ao escrever no arquivo
   - Código 30: Erro ao criar cabeçalho do arquivo

---

## 6. Relação entre Entidades

**Estorno** (entidade principal)
- Contém: código de conciliação, protocolo ITP, dados da transação (valor, moeda, data), mensagem de erro
- Relaciona-se com **Cartao** através do número de identificação quina

**Cartao**
- Contém: código do produto, número da conta, número correlativo
- Extraído a partir do campo `numeroIdentificacaoQuinaCartao` do Estorno

**RegistroEstorno** (DTO)
- Espelha os campos de Estorno
- Utilizado para geração do arquivo CSV de saída

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBCCBD.CCBDTransacaoCartaoDebito.TbConciliacaoTransacao | Tabela | SELECT | Tabela de conciliação de transações de cartão de débito, consultada para obter transações não estornadas |

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema apenas realiza leitura de dados, não executa operações de INSERT, UPDATE ou DELETE.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| Estornos_nao_ocorridos_DD-MM-YYYY HH-MM-SS.csv | Gravação | ItemWriter / ArquivoService | Arquivo CSV contendo relatório de transações não estornadas |
| robo.log | Gravação | Log4j (RollingFileAppender) | Log de execução do batch |
| statistics-{executionId}.log | Gravação | Log4j (BvDailyRollingFileAppender) | Log de estatísticas de execução |

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
| SQL Server (DBCCBD) | Banco de Dados | Banco de dados SQL Server contendo as transações de cartão de débito. Conexão via JTDS em diferentes ambientes (DES, UAT, PRD) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Uso adequado do padrão batch (Reader-Processor-Writer)
- Separação de responsabilidades em camadas (batch, domain, repository, service, mapper)
- Uso de logging estruturado
- Configuração externalizada por ambiente
- Presença de testes unitários

**Pontos Negativos:**
- **Hardcoding de credenciais**: Senha exposta em texto claro no ambiente DES
- **Uso excessivo de reflection**: ArquivoEstornoMapper usa reflection de forma complexa e pouco legível
- **Nomenclatura inconsistente**: Campos em RegistroEstorno começam com maiúscula (convenção incorreta para Java)
- **Tratamento de exceções genérico**: Captura de Exception genérica em vários pontos
- **Falta de validações**: Não há validação de dados antes do processamento
- **Código comentado em português**: Comentários e mensagens misturados em português e inglês
- **Classe utilitária com construtor privado**: Boa prática, mas poderia usar interface funcional
- **Magic numbers**: Uso de números mágicos (ex: substring(0,2), substring(2,11))
- **Falta de documentação JavaDoc**: Classes não possuem documentação adequada

---

## 14. Observações Relevantes

1. **Ambientes**: O sistema possui configurações específicas para três ambientes (DES, UAT, PRD) com diferentes servidores SQL Server
2. **Framework Proprietário**: Utiliza framework batch proprietário da BV Sistemas, o que pode dificultar manutenção por equipes externas
3. **Segurança**: Credenciais de banco expostas em configuração (ambiente DES), uso de placeholders em UAT/PRD
4. **Formato de Arquivo**: Arquivo CSV gerado com separador ponto-e-vírgula (;)
5. **Processamento**: Configurado para processar até 10.000 registros por commit
6. **Estratégia de Retomada**: Implementa MyResumeStrategy que não permite retomada em caso de falha (retorna false)
7. **Limpeza de Logs**: Scripts de execução removem arquivos de log do Bitronix após execução
8. **Versionamento**: Projeto na versão 0.1.0, indicando fase inicial de desenvolvimento