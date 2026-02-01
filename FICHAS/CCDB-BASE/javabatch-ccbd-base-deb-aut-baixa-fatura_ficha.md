# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java responsável por processar pagamentos de débito automático de faturas. O sistema consulta pagamentos com status específico em uma data determinada, agrupa-os em lotes e publica mensagens em uma fila RabbitMQ para processamento posterior de baixa de faturas. Utiliza o framework BV Sistemas para processamento batch com padrão Reader-Processor-Writer.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê pagamentos do banco de dados MySQL para uma data específica e prepara mensagens para processamento |
| **ItemProcessor** | Processa as mensagens (atualmente apenas repassa sem transformação) |
| **ItemWriter** | Serializa mensagens em JSON e publica na fila RabbitMQ |
| **PagamentosRepository** | Interface para acesso aos dados de pagamentos |
| **PagamentosRepositoryImpl** | Implementação do repositório usando Spring JDBC Template |
| **PagamentoMapper** | Mapeia ResultSet do banco para objetos PagamentoDebitoAutomatico |
| **Mensagem** | Encapsula lote de pagamentos para envio à fila |
| **LotePagamentos** | Agrupa pagamentos em lote ou individual |
| **PagamentoDebitoAutomatico** | Value Object representando um pagamento |
| **MyResumeStrategy** | Estratégia de retomada do job em caso de falha |
| **ExitCodeEnum** | Enumeração de códigos de saída do batch |
| **PagamentoException** | Exceção customizada para erros de pagamento |
| **QueryUtils** | Utilitário para carregar queries SQL de arquivos XML |

## 3. Tecnologias Utilizadas

- **Java** (versão não especificada explicitamente)
- **Maven** - Gerenciamento de dependências e build
- **Spring Framework** - Injeção de dependências e configuração
- **Spring JDBC** - Acesso a dados (NamedParameterJdbcTemplate)
- **Spring AMQP / RabbitMQ** - Mensageria
- **MySQL 8.0.22** - Banco de dados (driver com.mysql.cj.jdbc.Driver)
- **Bitronix** - Gerenciamento de transações (XA DataSource)
- **BV Framework Batch** - Framework proprietário para processamento batch
- **BV Crypto** - Criptografia de senhas
- **Jackson 2.0.0** - Serialização JSON
- **Log4j 1.2.17** - Logging
- **JUnit** - Testes unitários

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch sem endpoints REST.

## 5. Principais Regras de Negócio

1. **Seleção de Pagamentos**: Recupera apenas pagamentos com status 4 (CdStatusPagamentoDebitoAtmto = 4) e convênios 1 ou 2 (CdConvenioDebitoAutomatico IN (1,2))

2. **Data de Pagamento**: Se não informada como parâmetro, utiliza a data atual do sistema

3. **Agrupamento em Lote**: Se houver mais de um pagamento, cria um lote; se houver apenas um, cria mensagem individual

4. **Validação de Dados**: Se nenhum pagamento for encontrado para a data especificada, o job falha com código de saída 10

5. **Publicação em Fila**: Mensagens são publicadas no exchange "ex.ccbd.debito.automatico" com routing key "baixa.fatura"

6. **Tratamento de Erros**: Erros na leitura de dados resultam em código de saída 10; erros ao postar na fila resultam em código de saída 20

## 6. Relação entre Entidades

**PagamentoDebitoAutomatico** (entidade principal):
- nuCpfCnpj: String (CPF/CNPJ do pagador)
- cdSeuNumero: String (código identificador)
- vrPagamento: BigDecimal (valor do pagamento)
- dtVencimento: Date (data de vencimento)

**LotePagamentos** (agregador):
- Contém uma lista de PagamentoDebitoAutomatico OU
- Contém um único PagamentoDebitoAutomatico

**Mensagem** (envelope):
- Contém um LotePagamentos

**Relacionamento no Banco**:
- TbPessoaDebitoAutomatico (1) ← (N) TbPagamentoDebitoAutomatico
- Join pela chave CdPessoaDebitoAutomatico

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbPessoaDebitoAutomatico | Tabela | SELECT | Contém dados das pessoas cadastradas no débito automático (CPF/CNPJ) |
| TbPagamentoDebitoAutomatico | Tabela | SELECT | Contém dados dos pagamentos de débito automático (valor, vencimento, status, convênio) |

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema apenas lê dados do banco, não realiza operações de INSERT, UPDATE ou DELETE.

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| PagamentosRepositoryImpl-sql.xml | Leitura | QueryUtils / PagamentosRepositoryImpl | Arquivo XML contendo queries SQL parametrizadas |
| log/statistics-${executionId}.log | Gravação | BvDailyRollingFileAppender | Log de estatísticas de execução do batch |
| log/robo.log | Gravação | RollingFileAppender (produção) | Log geral da aplicação em produção |

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas, apenas publica.

## 11. Filas Geradas

**Exchange**: ex.ccbd.debito.automatico  
**Routing Key**: baixa.fatura  
**Tipo**: RabbitMQ  
**Descrição**: Fila para processamento de baixa de faturas de débito automático. Recebe mensagens JSON contendo lotes de pagamentos.

**Configurações por Ambiente**:
- **DES**: 10.39.216.137:5672 (usuário: _ccbd_des)
- **UAT**: 10.183.100.69:5672 (usuário: _ccbd_uat)
- **PRD**: 10.39.49.197:5672 (usuário: _ccbd_prd)
- **Local**: localhost:5672 (usuário: guest)

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| MySQL CCBDDebitoAutomatico | Banco de Dados | Base de dados de débito automático (leitura de pagamentos) |
| RabbitMQ | Mensageria | Publicação de mensagens para processamento de baixa de faturas |
| BV Crypto | Serviço | Descriptografia de senhas de banco de dados usando token BV_CRYPTO_TOKEN |

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com padrão Reader-Processor-Writer
- Uso adequado de Value Objects imutáveis (PagamentoDebitoAutomatico)
- Tratamento de exceções com códigos de saída específicos
- Configuração externalizada por ambiente (DES/UAT/PRD)
- Uso de logging apropriado
- Testes de integração presentes

**Pontos de Melhoria:**
- ItemProcessor não realiza nenhuma transformação (apenas repassa dados)
- Senhas hardcoded em alguns arquivos de configuração (ambiente PRD/UAT com valores vazios)
- Falta documentação JavaDoc nas classes
- Uso de framework proprietário (BV Framework) pode dificultar manutenção
- Versões antigas de bibliotecas (Jackson 2.0.0, Log4j 1.2.17)
- Query SQL embutida em arquivo XML ao invés de usar JPA/Hibernate
- Falta validação mais robusta de parâmetros de entrada
- Código de teste comentado no JobIntegrationTest

## 14. Observações Relevantes

1. **Dependência de Framework Proprietário**: O sistema utiliza extensivamente o BV Framework Batch, que é proprietário da organização, o que pode dificultar portabilidade

2. **Segurança**: Utiliza BVCrypto para descriptografar senhas, mas alguns arquivos de configuração (PRD/UAT) possuem campos de senha vazios

3. **Banco de Dados**: Schema CCBDDebitoAutomatico em MySQL, com proxy de acesso (gcmysdgXXX-proxy.bvnet.bv)

4. **Parâmetro Opcional**: O parâmetro dataPagamento é opcional; se não fornecido, usa a data atual

5. **Processamento em Lote Único**: O sistema processa todos os pagamentos de uma data em uma única mensagem/lote

6. **Versionamento**: Versão atual 0.1.0, indicando que o sistema está em fase inicial

7. **Ambientes**: Configurações específicas para DES, UAT e PRD, além de configuração local para desenvolvimento

8. **Exit Codes**: Sistema bem definido de códigos de saída (0=OK, 10=Erro BD, 20=Erro Fila)