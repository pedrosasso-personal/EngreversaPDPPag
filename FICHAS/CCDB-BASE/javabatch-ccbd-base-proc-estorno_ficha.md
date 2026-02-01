# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java responsável por processar estornos de transações de cartão de débito. O sistema consulta transações pendentes de estorno na tabela `TbConciliacaoTransacao`, processa os dados extraindo informações do cartão a partir da "quina" (identificador único), e publica mensagens em uma fila RabbitMQ para processamento posterior do estorno.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `ItemReader` | Lê transações pendentes de estorno do banco de dados e prepara objetos para processamento |
| `ItemProcessor` | Repassa objetos TransacaoEstorno do Reader para o Writer (processamento passthrough) |
| `ItemWriter` | Converte TransacaoEstorno em JSON e publica na fila RabbitMQ |
| `TransacaoEstorno` | Entidade de domínio representando uma transação de estorno |
| `Cartao` | Entidade de domínio representando dados do cartão (conta, produto, correlativo) |
| `TransacaoEstornoMapper` | Mapeia ResultSet para TransacaoEstorno e decodifica a "quina" do cartão |
| `ConsultaRepositoryImpl` | Implementação do repositório para consultas ao banco de dados |
| `QueryConsultaOperacoesEstorno` | Contém a query SQL para buscar operações de estorno |
| `MyResumeStrategy` | Estratégia de retomada do job (atualmente não permite retomada) |

## 3. Tecnologias Utilizadas

- **Framework Batch**: BV Framework Batch (framework proprietário baseado em Spring)
- **Linguagem**: Java
- **Build**: Maven
- **Banco de Dados**: Microsoft SQL Server (JTDS driver)
- **Mensageria**: RabbitMQ (Spring AMQP)
- **Gerenciamento de Transações**: Bitronix (JTA)
- **Logging**: Log4j
- **Serialização**: Jackson (JSON)
- **Testes**: JUnit, Mockito
- **Spring Framework**: Spring JDBC, Spring Rabbit

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch que não expõe endpoints REST.

## 5. Principais Regras de Negócio

1. **Seleção de Transações para Estorno**: Busca transações com os seguintes critérios:
   - Tipo de transação = 2 (estorno)
   - Sem código de controle de transação (CdControleTransacaoCartao IS NULL)
   - Origem do arquivo = 4 ou 5
   - Transação exclusiva de arquivo (FlTransacaoExclusivaArquivo = 'S')
   - Ainda não estornada na Base2 (FlBase2Estornado IS NULL)
   - Possui identificação de quina do cartão válida (não nula, não vazia, com 16 caracteres)

2. **Decodificação da Quina do Cartão**: A "quina" é um identificador de 16 caracteres que contém:
   - Posições 0-1: Código do produto (2 dígitos)
   - Posições 2-10: Número da conta (9 dígitos)
   - Posições 11-15: Código correlativo do cartão (5 dígitos)

3. **Validação da Quina**: Rejeita transações com quina inválida (diferente de 16 caracteres), registrando warning no log

4. **Commit em Lote**: Processa transações em lotes de 10.000 registros (commitInterval)

5. **Publicação em Fila**: Cada transação válida é convertida em JSON e publicada individualmente na fila RabbitMQ

## 6. Relação entre Entidades

**TransacaoEstorno** (1) -----> (1) **Cartao**

- `TransacaoEstorno` contém todos os dados da transação de estorno
- `Cartao` é extraído da quina e associado à `TransacaoEstorno`
- Relacionamento de composição: o Cartao é parte integrante da TransacaoEstorno

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBCCBD.CCBDTransacaoCartaoDebito.TbConciliacaoTransacao | Tabela | SELECT | Tabela de conciliação de transações de cartão, contendo transações pendentes de estorno |

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema apenas lê dados do banco, não realiza operações de INSERT, UPDATE ou DELETE.

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| log/robo.log | Gravação | Log4j (RollingFileAppender) | Log principal da aplicação com rotação de 2MB e 5 backups |
| log/statistics-{executionId}.log | Gravação | BvDailyRollingFileAppender | Log de estatísticas de execução do batch |
| *.tlog | Gravação/Leitura | Bitronix Transaction Manager | Arquivos de log de transações do gerenciador JTA |

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

## 11. Filas Geradas

| Nome da Fila/Exchange | Tipo | Routing Key | Breve Descrição |
|----------------------|------|-------------|-----------------|
| events.ex.business.ccbd.estornoArquivoBase2 | Exchange (RabbitMQ) | CCBD.estornoArquivoBase2 | Exchange para publicação de eventos de estorno de arquivo Base2 |

**Detalhes da Conexão RabbitMQ:**
- **DES**: Host 10.179.172.71:5672, usuário _ccbd_des
- **UAT**: Host 10.39.88.213:5672, usuário _ccbd_uat
- **PRD**: Host 10.39.49.197:5672, usuário _ccbd_prd

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|----------------|------|-----------|
| Microsoft SQL Server (DBCCBD) | Banco de Dados | Banco de dados de transações de cartão de débito CCBD |
| RabbitMQ | Mensageria | Sistema de mensageria para publicação de eventos de estorno |

**Configurações de Banco por Ambiente:**
- **DES**: SQLDES35:17035
- **UAT**: SQLUAT35:17035
- **PRD**: SQLPRD35:17035

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades (Reader, Processor, Writer)
- Uso adequado de logging
- Tratamento de exceções customizadas
- Configuração externalizada por ambiente
- Testes unitários implementados

**Pontos Negativos:**
- `ItemProcessor` não realiza nenhum processamento real (apenas repassa dados)
- Comentários em português com caracteres mal codificados (encoding issues)
- Query SQL hardcoded como String concatenada (dificulta manutenção)
- Falta de constantes para valores mágicos (ex: tamanho da quina = 16)
- Classe `ConstantsUtils` com apenas 3 constantes
- Falta de validação mais robusta nos dados de entrada
- Configuração de senhas em texto claro nos XMLs de desenvolvimento
- Uso de `@SuppressWarnings("all")` sem justificativa
- Falta de documentação JavaDoc nas classes principais
- Pool de conexões com tamanho fixo (não configurável dinamicamente)

## 14. Observações Relevantes

1. **Framework Proprietário**: O sistema utiliza o BV Framework Batch, um framework proprietário da organização baseado em Spring Batch, o que pode dificultar manutenção por desenvolvedores externos.

2. **Processamento Síncrono**: Cada transação é publicada individualmente na fila, o que pode impactar performance em grandes volumes.

3. **Sem Mecanismo de Retry**: A estratégia de retomada (`MyResumeStrategy`) sempre retorna `false`, não permitindo retomada em caso de falha.

4. **Códigos de Saída Customizados**:
   - Código 10: Erro ao postar na fila MQ
   - Código 20: Erro ao buscar transações

5. **Dependência de Dados Externos**: O sistema depende que o campo `NuIdentificacaoQuinaCartao` esteja sempre preenchido e válido para funcionar corretamente.

6. **Ausência de Atualização de Status**: O sistema não atualiza o status das transações processadas no banco de dados, dependendo de outro sistema para marcar as transações como processadas.

7. **Configuração de Ambiente**: O sistema possui configurações específicas para DES, UAT e PRD, facilitando o deploy em diferentes ambientes.

8. **Execução**: Pode ser executado via scripts .bat (Windows) ou .sh (Linux), recebendo nome do job e execution ID como parâmetros.