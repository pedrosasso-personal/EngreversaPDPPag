# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java desenvolvido para processar e enviar dados de carnês de contratos financeiros para uma fila RabbitMQ. O sistema consulta contratos específicos (produtos 13 e 10, modalidades 55 e 81) que tiveram alterações de status em boletos, recupera informações detalhadas do contrato, cliente, veículo legal e carnês associados, e publica essas informações em formato JSON para processamento posterior (geração de PDF de carnê).

O processamento é executado com base em uma data específica fornecida como parâmetro, comparando registros entre duas datas consecutivas para identificar mudanças de status nos boletos.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê dados de contratos do banco de dados Sybase IQ com base na data de processamento, valida parâmetros e carrega informações de carnês |
| **ItemProcessor** | Processa os dados lidos, realizando cópia simples das propriedades do input para output |
| **ItemWriter** | Serializa os contratos em JSON e publica na fila RabbitMQ com controle transacional |
| **CarneContratoDAOImpl** | Implementa acesso aos dados, executando queries SQL para obter contratos e carnês |
| **ContratoRowMapper** | Mapeia resultados SQL para objetos Contrato com todas as entidades relacionadas |
| **CarneRowMapper** | Mapeia resultados SQL para objetos Carne |
| **RabbitRepositoryImpl** | Gerencia conexão, publicação e transações com RabbitMQ |
| **MQServiceImpl** | Camada de serviço para operações de mensageria |
| **MyResumeStrategy** | Define estratégia de retomada do job (não permite retomada em caso de erro) |
| **JobUtil** | Utilitário para validação de parâmetros do job |

---

## 3. Tecnologias Utilizadas

- **Java** (versão não especificada no código)
- **Spring Batch** - Framework para processamento batch
- **Spring Framework** - Injeção de dependências e configuração
- **Maven** - Gerenciamento de dependências e build
- **Sybase jConnect (jconn4)** - Driver JDBC para Sybase IQ
- **RabbitMQ Client (amqp-client 4.11.3)** - Cliente para mensageria
- **Gson** - Serialização/deserialização JSON
- **Log4j** - Framework de logging
- **JUnit** - Testes unitários
- **BV Framework Batch** - Framework proprietário para jobs batch
- **BV Crypto** - Biblioteca de criptografia (para senhas)

---

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch sem endpoints REST.

---

## 5. Principais Regras de Negócio

1. **Seleção de Contratos**: Processa apenas contratos com produtos 13 ou 10 e modalidades 55 ou 81
2. **Detecção de Mudanças**: Identifica contratos cujos boletos mudaram de status entre duas datas consecutivas (data atual vs. data anterior)
3. **Filtro de Status**: Considera apenas boletos com status 'REGD' (registrado) na data mais recente
4. **Convênio Específico**: Filtra apenas boletos do convênio '0000001007'
5. **Validação de Contrato**: Exclui números de conta que contenham letras
6. **Endereço de Correspondência**: Seleciona apenas endereços marcados como correspondência (FlCorrespondencia = 'S')
7. **Transacionalidade**: Publica mensagens no RabbitMQ com controle transacional (commit/rollback)
8. **Tratamento de cdEntregaDocumento**: Substitui valor 0 por null no JSON antes de publicar
9. **Parâmetro Obrigatório**: Exige data de processamento como parâmetro de entrada

---

## 6. Relação entre Entidades

**Contrato** (entidade principal)
- Possui um **EntregaDocumento** (1:1)
- Possui uma **Pessoa** (1:1) - dados do cliente para entrega
- Possui um **DadosCarne** (1:1)

**DadosCarne**
- Possui um **Cliente** (1:1) - dados completos do cliente
- Possui um **VeiculoLegal** (1:1) - dados da instituição financeira
- Possui uma lista de **Carne** (1:N) - carnês/boletos do contrato

**Cliente** e **VeiculoLegal**
- Cada um possui um **Endereco** (1:1)

**Pessoa**
- Possui um **Endereco** (1:1)

**Carne**
- Contém dados do boleto bancário (valores, datas, códigos de barras, etc.)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| STGTXT_FLEX.STG_CLTM_BOLETO_DET | Tabela | SELECT | Tabela de staging com detalhes de boletos, usada para identificar mudanças de status |
| STGTXT_FLEX.TbContrato | Tabela | SELECT | Dados principais dos contratos financeiros |
| STGTXT_FLEX.TbPessoa | Tabela | SELECT | Informações cadastrais das pessoas/clientes |
| STGTXT_FLEX.TbPessoaEndereco | Tabela | SELECT | Endereços das pessoas |
| STGTXT_FLEX.TbPessoaTelefone | Tabela | SELECT | Telefones das pessoas |
| DBCOR.TbVeiculoLegal | Tabela | SELECT | Dados dos veículos legais (instituições financeiras) |
| STGTXT_FLEX.CLTM_BOLETO_DET | Tabela | SELECT | Detalhes completos dos boletos/carnês |

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema apenas realiza leituras, não executa operações de INSERT, UPDATE ou DELETE.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| job-resources.xml | Leitura | Configuração Spring | Arquivo de configuração com datasources e parâmetros do RabbitMQ |
| job-definitions.xml | Leitura | Configuração Spring | Definição do job batch, beans e metadados |
| log4j.xml | Leitura | Log4j | Configuração de logging |
| robo.log | Gravação | Log4j (RollingFileAppender) | Log principal da aplicação |
| statistics-{executionId}.log | Gravação | BvDailyRollingFileAppender | Log de estatísticas de execução do job |

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas, apenas publica.

---

## 11. Filas Geradas

| Nome da Fila/Exchange | Tecnologia | Descrição |
|-----------------------|------------|-----------|
| sample-exchange | RabbitMQ | Exchange configurado para receber mensagens JSON com dados de contratos e carnês |
| Routing Key: http://10.36.195.164 | RabbitMQ | Chave de roteamento utilizada para direcionar as mensagens |

**Observação**: O sistema utiliza RabbitMQ com controle transacional (txSelect, txCommit, txRollback) e mensagens persistentes (MessageProperties.PERSISTENT_TEXT_PLAIN).

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Sybase IQ (IQ_BI) | Banco de Dados | Banco de dados analítico Sybase IQ na porta 3330, usado para consultar dados de contratos e boletos |
| RabbitMQ | Fila de Mensagens | Servidor RabbitMQ (10.36.195.164:5672) para publicação de mensagens com dados de carnês |
| BV Crypto | Serviço | Biblioteca de criptografia para descriptografia de senhas (comentado no código, mas presente na configuração) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com camadas bem definidas (DAO, Service, Repository)
- Uso adequado de interfaces e implementações
- Tratamento de exceções com códigos de saída específicos
- Uso de transações no RabbitMQ
- Logging adequado em pontos críticos
- Uso de RowMappers para mapeamento objeto-relacional

**Pontos Negativos:**
- Código com comentários em português e encoding issues (caracteres especiais mal formatados)
- Queries SQL hardcoded em strings concatenadas, dificultando manutenção
- Classe Repository.java aparentemente não utilizada (código morto)
- Falta de tratamento adequado de recursos (try-with-resources)
- Configurações sensíveis (IPs, portas, usuários) hardcoded em XML
- Falta de testes unitários (apenas um teste de integração)
- Uso de System.out.println em código de produção (CarneContratoDAOImpl)
- Substituição de string no JSON de forma manual (replace) ao invés de configuração do Gson
- Código comentado em várias classes (VeiculoLegal no Contrato)
- Falta de documentação JavaDoc nas classes e métodos

---

## 14. Observações Relevantes

1. **Ambiente de Desenvolvimento**: O código contém configurações específicas para ambiente de desenvolvimento/QA (IQUATGCON, credenciais de teste)

2. **Criptografia de Senhas**: Existe infraestrutura para uso de senhas criptografadas via BV Crypto, mas está comentada no código, usando senhas em texto plano

3. **Dependência de Framework Proprietário**: O sistema utiliza extensivamente o BV Framework Batch, que é proprietário, dificultando portabilidade

4. **Códigos de Saída Customizados**: Sistema define códigos de saída específicos (0=sucesso, 2=erro genérico, 10=parâmetro inválido, 20=erro contratos, 30=erro carnê, 40=erro fila)

5. **Processamento em Lote Único**: O ItemReader carrega todos os contratos de uma vez na memória, o que pode ser problemático para grandes volumes

6. **Formato de Data**: Sistema espera data no formato YYYYMMDD como parâmetro

7. **Versão do Projeto**: Versão 0.13.0, indicando que ainda está em desenvolvimento/evolução

8. **Estrutura Maven Multi-módulo**: Projeto organizado em módulos core e dist para separar lógica de negócio e distribuição