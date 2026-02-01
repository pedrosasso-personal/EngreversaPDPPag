# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de processamento batch Java desenvolvido para exportar e registrar informações de contratos com formas de entrega do tipo carnê. O sistema consulta contratos exportados em um período específico no banco DBCOR, valida se já existem registros correspondentes no banco DBCARNE e, caso não existam, insere novos registros na tabela `TbContratoFormaEntrega`. Utiliza o framework BV Sistemas para processamento batch com padrão Reader-Processor-Writer.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê contratos exportados do banco DBCOR em um período específico (dataInicio/dataFim) e disponibiliza para processamento |
| **ItemProcessor** | Valida se o contrato já possui registro na tabela TbContratoFormaEntrega e prepara objeto para inserção |
| **ItemWriter** | Insere registros de ContratoFormaEntrega no banco DBCARNE e realiza commit da transação |
| **MyResumeStrategy** | Estratégia de retomada que permite continuar processamento quando encontra registros duplicados |
| **DBCORRepository** | Repositório para consultas no banco DBCOR (tabelas TbMonitorContratoExportado e TbPropostaFormaEntrega) |
| **DBCARNERepository** | Repositório para operações no banco DBCARNE (tabela TbContratoFormaEntrega) |
| **RegistroContratoExportado** | Entidade que representa um contrato exportado com suas informações |
| **ContratoFormaEntrega** | Entidade que representa o registro a ser inserido na tabela de destino |
| **PropostaFormaEntrega** | Entidade que representa a forma de entrega associada a uma proposta |

## 3. Tecnologias Utilizadas

- **Java** (linguagem de programação)
- **Maven** (gerenciamento de dependências e build)
- **BV Framework Batch** (framework proprietário para processamento batch)
- **Spring Framework** (injeção de dependências e configuração)
- **Sybase/SQL Server** (banco de dados - via driver JTDS)
- **Bitronix** (gerenciador de transações JTA)
- **Log4j** (logging)
- **JUnit** (testes unitários)
- **JDBC** (acesso a dados)

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch sem endpoints REST.

## 5. Principais Regras de Negócio

1. **Período de Processamento**: O sistema processa contratos exportados dentro de um período específico definido pelos parâmetros `dataInicio` e `dataFim`
2. **Validação de Duplicidade**: Antes de inserir, verifica se já existe registro para o contrato com o mesmo tipo de forma de entrega
3. **Registro Duplicado**: Se o contrato já possui registro, o processamento continua para o próximo item (não interrompe o batch)
4. **Inserção Condicional**: Apenas contratos sem registro prévio são inseridos na tabela TbContratoFormaEntrega
5. **Flag Ativo**: Todos os registros inseridos recebem flag ativo = 'S'
6. **Usuário Sistema**: Registros são inseridos com login "sistema"
7. **Commit em Lote**: Todas as inserções são commitadas ao final do processamento batch
8. **Encerramento Gracioso**: Se não houver contratos elegíveis no período, o sistema encerra com exit code 0

## 6. Relação entre Entidades

**RegistroContratoExportado** (1) -----> (1) **PropostaFormaEntrega**
- Um registro de contrato exportado possui uma forma de entrega associada

**ContratoFormaEntrega**
- Entidade de destino que relaciona um contrato com seu tipo de forma de entrega
- Campos: codigoTipoFormaEntrega, numeroContrato

**Relacionamento entre bancos:**
- DBCOR.TbMonitorContratoExportado (origem) -> DBCARNE.TbContratoFormaEntrega (destino)
- DBCRED.TbPropostaFormaEntrega (consulta) -> enriquece dados do contrato

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBCOR..TbMonitorContratoExportado | Tabela | SELECT | Tabela de contratos exportados, filtrados por período de exportação |
| DBCRED..TbPropostaFormaEntrega | Tabela | SELECT | Tabela com informações de forma de entrega das propostas |
| DBCARNE..TbContratoFormaEntrega | Tabela | SELECT | Verificação de existência de registro para evitar duplicidade |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBCARNE..TbContratoFormaEntrega | Tabela | INSERT | Inserção de novos registros de contrato com forma de entrega |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| log/robo.log | Gravação | Log4j (RollingFileAppender) | Log principal da aplicação com informações de processamento |
| log/statistics-{executionId}.log | Gravação | BvDailyRollingFileAppender | Log de estatísticas do framework BV (não deve ser alterado) |

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas.

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **Banco DBCOR** | Banco de Dados Sybase | Consulta contratos exportados e propostas |
| **Banco DBCRED** | Banco de Dados Sybase | Consulta formas de entrega das propostas |
| **Banco DBCARNE** | Banco de Dados Sybase | Validação e inserção de registros de contrato |

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Estrutura bem organizada seguindo padrão Reader-Processor-Writer
- Separação clara de responsabilidades entre camadas (batch, domain, repository)
- Uso adequado de enums para constantes (Erros, Parametros, BancoDadosEnum)
- Tratamento de exceções com códigos de erro específicos
- Logging adequado em pontos críticos
- Uso de PreparedStatement para evitar SQL Injection

**Pontos Negativos:**
- **Encoding inconsistente**: Comentários em português com caracteres mal codificados (�)
- **Hardcoded values**: String "sistema" como usuário hardcoded no código
- **Falta de constantes**: Nomes de colunas SQL como strings literais
- **Gestão de recursos**: Fechamento de conexões poderia usar try-with-resources
- **Falta de testes**: Apenas um teste de integração básico
- **Documentação**: Ausência de JavaDoc nas classes e métodos
- **Queries SQL**: Queries concatenadas como strings, poderia usar arquivos .sql externos
- **Transação manual**: Uso de autoCommit(false) e commit manual, poderia usar gerenciamento declarativo
- **Acoplamento**: Dependência direta de framework proprietário (BV Sistemas)

## 14. Observações Relevantes

1. **Framework Proprietário**: O sistema utiliza o framework BV Sistemas (br.com.bvsistemas.framework.batch), que é proprietário e pode dificultar manutenção futura
2. **Configuração de Ambiente**: Credenciais de banco estão no arquivo de teste (job-resources.xml), mas não há arquivo equivalente para produção no código
3. **Estratégia de Retomada**: Implementa estratégia customizada que permite continuar processamento mesmo com erros de duplicidade
4. **Versionamento**: Versão 0.1.0 indica que é um sistema em fase inicial
5. **Bitronix Transaction Manager**: Uso de gerenciador de transações JTA, mas com `automaticEnlistingEnabled=false`
6. **Driver JDBC**: Utiliza JTDS (driver open source) para conexão com Sybase
7. **Processamento em Lote**: Todo o processamento é feito em memória (lista completa carregada) antes de iniciar o processamento item a item
8. **Exit Codes**: Sistema define códigos de saída específicos (10-14, 20, 30) para diferentes tipos de erro
9. **Jenkins Integration**: Arquivo jenkins.properties indica integração com pipeline CI/CD