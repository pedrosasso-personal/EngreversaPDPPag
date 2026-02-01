# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java responsável pelo processamento automático de débitos agendados (pagamentos). O sistema consulta lançamentos de débito automático com vencimento na data atual, publica mensagens em fila RabbitMQ para processamento de liquidação e registra histórico das operações. Trata-se de um job batch que processa pagamentos de cartões e financiamentos através de débito automático em conta corrente.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê lançamentos de débito automático agendados para a data atual do banco de dados MySQL |
| **ItemProcessor** | Processa os lançamentos (atualmente apenas repassa os dados sem transformação) |
| **ItemWriter** | Publica mensagens na fila RabbitMQ e insere histórico de processamento no banco |
| **DebitoAutoRepository** | Interface de acesso aos dados de débito automático |
| **DebitoAutoRepositoryImpl** | Implementação do repositório com queries SQL para leitura e gravação |
| **LancamentoMapper** | Mapeia ResultSet do banco para objetos Lancamento e converte para LancamentoPublish |
| **Lancamento** | Value Object representando um lançamento de débito automático completo |
| **LancamentoPublish** | Value Object otimizado para publicação na fila (sem campos internos) |
| **Pessoa** | Value Object representando dados bancários de remetente ou favorecido |
| **MyResumeStrategy** | Estratégia de retomada do job em caso de falha |
| **DebitoAutoUtil** | Utilitário para carregar queries SQL de arquivos XML |

## 3. Tecnologias Utilizadas

- **Java** com Maven para build
- **Spring Framework** (versão 2.x) para injeção de dependências e configuração
- **Spring Batch** (framework BV customizado baseado em Spring Batch)
- **MySQL 8.0.22** como banco de dados
- **RabbitMQ** para mensageria (Spring AMQP 1.5.7)
- **Bitronix** para gerenciamento de transações XA
- **Log4j 1.2.17** para logging
- **Jackson 2.12.7** para serialização JSON
- **JUnit 4** e **Mockito 2.28.2** para testes
- **BV Framework Batch** (framework proprietário para jobs batch)

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch sem endpoints REST.

## 5. Principais Regras de Negócio

1. **Seleção de Lançamentos**: Processa apenas lançamentos com data de vencimento igual à data atual e status = 1 (agendado)
2. **Priorização**: Lançamentos são ordenados por prioridade de pagamento (campo CdPrioridadePagamento)
3. **Tipos de Produto**: Suporta 4 tipos de débito automático:
   - CARTAO (código 1): transação 8912, evento 12837
   - FINANCIAMENTO (código 2): transação 8913, evento 12838
   - FINANCIAMENTO_CP (código 3): transação 8979, evento 12894
   - FINANCIAMENTO_CF (código 4): transação 9047, evento 12924
4. **Tipos de Conta**: Suporta CI, IF, PP, CO, CC, CT, PG
5. **Controle de Tentativas**: Registra número de tentativas de pagamento
6. **Histórico**: Insere registro de controle com status "Agendamento enviado para fila" após publicação
7. **Indicadores**: Define tipo de lançamento como "E" (entrada), finalidade "D" (débito), indicador terceiro "N"
8. **Validação**: Se flag FlPagamentoEnviado for null, define como "N" antes de publicar

## 6. Relação entre Entidades

**Lancamento** (entidade principal)
- Contém: codigoEvento, codigoFilial, codigoLiquidacao, codigoOrigem, codigoTransacao, valorTransferencia
- Possui: 1 Pessoa (remetente) e 1 Pessoa (favorecido)
- Relaciona-se com: TipoProdutoDebitoAutomatico, StatusPagamento, ConvenioDebitoAutomatico

**Pessoa** (entidade de dados bancários)
- Atributos: numeroBanco, numeroAgencia, numeroConta, tipoConta, numeroCpfCnpj, nome, tipoPessoa

**LancamentoPublish** (DTO para fila)
- Versão simplificada de Lancamento para publicação
- Mesmos atributos exceto campos de controle interno

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbPagamentoDebitoAutomatico | tabela | SELECT | Tabela principal de pagamentos agendados |
| TbPessoaDebitoAutomatico | tabela | SELECT | Dados cadastrais da pessoa devedora |
| TbStatusPagamentoDebitoAtmto | tabela | SELECT | Status do pagamento (join) |
| TbConvenioDebitoAutomatico | tabela | SELECT | Dados do convênio/favorecido |
| TbTipoProdutoDebitoAutomatico | tabela | SELECT | Tipo de produto (cartão, financiamento, etc) |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbControleStatusPagamento | tabela | INSERT | Insere histórico de processamento do pagamento com status, tentativa e observação |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| DebitoAutoRepositoryImpl-sql.xml | leitura | DebitoAutoUtil.getSqlFromFile() | Arquivo XML contendo queries SQL parametrizadas |
| log/robo.log | gravação | Log4j RollingFileAppender | Log de execução do batch (max 2MB, 5 backups) |
| log/statistics-{executionId}.log | gravação | BvDailyRollingFileAppender | Log de estatísticas do framework BV (rotação diária) |

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Descrição |
|--------------|------------|-----------|
| **Exchange**: ex.ccbd.debito.automatico<br>**Routing Key**: liquidacao | RabbitMQ | Publica mensagens JSON com dados de lançamentos para processamento de liquidação de débito automático |

**Ambientes:**
- **DES**: rabbit-ccbd-base-lb.appdes.bvnet.bv:5672 (usuário: _ccbd_des)
- **UAT**: rabbit-ccbd-base-lb.appuat.bvnet.bv:5672 (usuário: _ccbd_uat)
- **PRD**: rabbit-ccbd-base-lb.app.bvnet.bv:5672 (usuário: _ccbd_prd)
- **Local**: localhost:5672 (usuário: guest)

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| MySQL CCBDDebitoAutomatico | Banco de Dados | Base de dados de débito automático (leitura de agendamentos e gravação de histórico) |
| RabbitMQ CCBD | Fila de Mensagens | Publicação de lançamentos para sistema de liquidação |

**Conexões por Ambiente:**
- **DES**: gcmysdgdes07-proxy.bvnet.bv:3306
- **UAT**: gcmysdguat07-proxy.bvnet.bv:3306
- **PRD**: gcmysdgprd07-proxy.bvnet.bv:3306

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades (Reader, Processor, Writer)
- Uso de padrões como Repository e Mapper
- Configuração externalizada por ambiente
- Presença de testes unitários e de integração
- Uso de enums para constantes
- Tratamento de exceções customizado

**Pontos Negativos:**
- Comentários em português com caracteres mal codificados (encoding issues)
- ItemProcessor não realiza nenhum processamento real (apenas repassa dados)
- Senhas em texto claro nos arquivos de configuração de teste
- Uso de framework batch legado/proprietário (BV Framework)
- Dependências desatualizadas (Spring 2.x, Log4j 1.2)
- Falta de documentação JavaDoc nas classes
- Código mistura lógica de negócio com infraestrutura
- Tratamento de exceções poderia ser mais específico
- Falta validação de dados antes de publicar na fila
- Testes unitários com cobertura limitada

## 14. Observações Relevantes

1. **Framework Proprietário**: O sistema utiliza o BV Framework Batch, um framework customizado baseado em Spring Batch, o que pode dificultar manutenção e migração futura.

2. **Segurança**: As senhas são criptografadas usando BVCrypto em produção, mas aparecem em texto claro nos ambientes de teste.

3. **Exit Codes**: O sistema define códigos de saída customizados:
   - 0: OK
   - 10: Erro ao carregar lançamentos
   - 20: Erro ao atualizar lançamento
   - 30: Erro ao postar mensagem na fila
   - 40: Erro ao inserir histórico

4. **Processamento**: O job processa lançamentos de forma sequencial (não há paralelização configurada).

5. **Versionamento**: Versão atual 0.15.0, indicando que o sistema ainda está em evolução.

6. **Agendamento**: O sistema é executado via UC4/scheduler externo (evidenciado pelos scripts .sh e .bat).

7. **Encoding**: Há problemas de encoding em comentários (caracteres especiais mal formatados), sugerindo inconsistência na configuração de charset do projeto.

8. **Transações**: Configurado com `allowLocalTransactions=true` e `automaticEnlistingEnabled=false`, indicando controle transacional simplificado.

9. **Retry**: A estratégia de retomada (MyResumeStrategy) permite retry apenas se exitCode = 0, o que parece contraditório (deveria permitir retry em caso de erro).