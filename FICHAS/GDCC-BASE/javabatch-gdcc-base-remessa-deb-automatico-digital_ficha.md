# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **javabatch-gdcc-base-remessa-deb-automatico-digital** é um job batch desenvolvido em Java que realiza o processamento e envio de remessas de débito automático para produtos financeiros (Crédito Pessoal, Crédito Fácil e Financiamento de Veículos). 

O sistema consulta parcelas de débito agendadas no banco de dados Sybase, processa as informações, atualiza o status das parcelas e envia mensagens para uma fila RabbitMQ para posterior processamento. Também identifica e cancela agendamentos de parcelas que foram quitadas antecipadamente.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê parcelas de débito do banco de dados para os três tipos de produtos (Crédito Pessoal, Crédito Fácil e Financiamento de Veículos), incluindo agendamentos cancelados |
| **ItemProcessor** | Processa e transforma os dados das parcelas, montando o objeto RemessaDebito com todas as informações necessárias |
| **ItemWriter** | Envia as remessas processadas para a fila RabbitMQ e atualiza o status das parcelas no banco de dados |
| **RemessaDebitoRepository** | Repositório responsável por executar as consultas SQL e atualizações no banco de dados |
| **RemessaDebitoMapper** | Mapeia os ResultSets do banco de dados para objetos de domínio RemessaDebito |
| **RemessaDebito** | Entidade de domínio principal que representa uma remessa de débito automático |
| **MyResumeStrategy** | Estratégia de retomada do processamento batch em caso de erros |
| **RemessaDateUtil** | Utilitário para manipulação de datas no contexto do processamento |
| **RemessaDebitoUtil** | Utilitário para leitura de queries SQL de arquivos XML |

---

## 3. Tecnologias Utilizadas

- **Java** (linguagem de programação)
- **Maven** (gerenciamento de dependências e build)
- **Spring Framework** (injeção de dependências e configuração)
- **Spring AMQP / RabbitMQ** (mensageria)
- **BV Framework Batch** (framework proprietário para processamento batch)
- **Sybase ASE** (banco de dados)
- **JDBC / Spring JDBC** (acesso a dados)
- **Bitronix** (gerenciamento de transações JTA)
- **Jackson** (serialização JSON)
- **Log4j** (logging)
- **JUnit** (testes unitários)
- **Docker Compose** (ambiente de desenvolvimento RabbitMQ)

---

## 4. Principais Endpoints REST

não se aplica

---

## 5. Principais Regras de Negócio

1. **Janela de Processamento**: O sistema processa parcelas com vencimento entre D+3 e D+13 (3 a 13 dias a partir da data atual)

2. **Tipos de Produto**: Processa três tipos de produtos financeiros:
   - Crédito Pessoal (código 3, produto 10, subproduto 97)
   - Crédito Fácil (código 4, produto 10, subproduto 101)
   - Financiamento de Veículos (código 2, produto 12, bancos 413 e 655)

3. **Status de Parcelas**:
   - Status 1: Parcela inicial/pendente
   - Status 2: Parcela agendada
   - Status 3: Parcela cancelada (quitada antecipadamente)

4. **Cancelamento de Agendamentos**: Identifica parcelas agendadas (status 2) que foram quitadas (status 'Q') e as marca como canceladas (status 3)

5. **Cálculo de Mora**: Se o valor de mora for nulo, atribui BigDecimal.ZERO

6. **Código de Liquidação**: Fixo em 1 (constante CODIGO_LIQUIDACAO_PAGAMENTO)

7. **Código de Origem do Sistema**: Fixo em 91 (constante CODIGO_ORIGEM_SISTEMA)

8. **Validação de Débito Ativo**: Para Financiamento de Veículos, valida que FlDebitoAtivo = 'S' e CdMotivoSuspensao IS NULL

---

## 6. Relação entre Entidades

**RemessaDebito** (entidade principal)
- Contém: PessoaPagamentoDebitoAutomatico (1:1)
- Contém: ConvenioDebitoAutomatico (1:1)
- Contém: StatusPagamentoDebitoAutomatico (1:1)
- Contém: ArquivoDebitoAutomatico (1:1)

**ConvenioDebitoAutomatico**
- Contém: TipoProdutoDebitoAutomatico (1:1)

**TipoProdutoDebitoAutomaticoEnum**
- Enum com três valores: FINANCIAMENTO_VEICULO (2), CREDITO_PESSOAL (3), CREDITO_FACIL (4)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| DBGESTAO..TbContratoDebito | tabela | SELECT | Contratos configurados para débito automático |
| DBGESTAO..TbParcelaDebito | tabela | SELECT | Parcelas de débito automático |
| DbGestaoDebitoContaCorrente..TbRegistroDebito | tabela | SELECT | Registros de débito com informações de mora |
| DbGestaoDebitoContaCorrente..TbContaConvenioSistemaOrigem | tabela | SELECT | Relacionamento entre convênios e sistemas de origem |
| DbGestaoDebitoContaCorrente..TbContaConvenio | tabela | SELECT | Dados dos convênios de débito automático |
| DBCOR..TbPessoa | tabela | SELECT | Dados cadastrais das pessoas |
| DBCOR..TbContratoprincipal | tabela | SELECT | Contratos principais |
| DBCRED..TbProposta | tabela | SELECT | Propostas de crédito |
| DBGESTAOCP..TbParcela | tabela | SELECT | Parcelas de Crédito Pessoal e Crédito Fácil |
| DBGESTAOCDCCG..TbParcela | tabela | SELECT | Parcelas de Financiamento de Veículos |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| DBGESTAO..TbParcelaDebito | tabela | UPDATE | Atualiza status da parcela para 2 (agendado) quando enviada para fila |
| DBGESTAO..TbParcelaDebito | tabela | UPDATE | Atualiza status da parcela para 3 (cancelado) quando quitada antecipadamente |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| RemessaDebitoRepository-sql.xml | leitura | RemessaDebitoUtil | Arquivo XML contendo as queries SQL utilizadas pelo repositório |
| log/robo.log | gravação | Log4j | Log principal da aplicação com rotação de 2MB e 5 backups |
| log/statistics-{executionId}.log | gravação | BvDailyRollingFileAppender | Log de estatísticas do framework batch |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

**Fila**: events.remessaDebitoAutomatico

**Exchange**: ex.gdcc.remessa.debito.automatico (tipo: direct)

**Routing Key**: gdcc.remessa.debito.automatico

**Descrição**: Fila RabbitMQ para onde são enviadas as mensagens JSON contendo os dados das remessas de débito automático processadas. As mensagens são enviadas com confirmação de publicação (publisherConfirms) e retorno (publisherReturns).

**Configuração por Ambiente**:
- DES: 10.39.214.162:5672 (usuário: _gdcc_base_des)
- QA: 10.39.83.250:5672 (usuário: _gdcc_base_qa)
- UAT: 10.39.88.10:5672 (usuário: _gdcc_base_uat)
- PRD: 10.39.36.235:5672 (usuário: _gdcc_base_prd)

---

## 12. Integrações Externas

1. **Banco de Dados Sybase ASE**:
   - DES: ptasybdes15.bvnet.bv:6010 (DbGestaoDebitoContaCorrente)
   - QA: PTASYBACT.bvnet.bv:4000 (DbGestaoDebitoContaCorrente)
   - UAT: ptasybuatfin.bvnet.bv:5050 (DbGestaoDebitoContaCorrente)
   - PRD: PTASYBFIN.bvnet.bv:5000 (DbGestaoDebitoContaCorrente)
   - Acessa múltiplos databases: DBGESTAO, DbGestaoDebitoContaCorrente, DBCOR, DBCRED, DBGESTAOCP, DBGESTAOCDCCG

2. **RabbitMQ**: Conforme descrito na seção 11 (Filas Geradas)

---

## 13. Avaliação da Qualidade do Código

**Nota:** 6/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades entre Reader, Processor e Writer
- Uso adequado do padrão Repository
- Configuração externalizada por ambiente
- Tratamento de exceções com códigos de saída específicos
- Uso de constantes para valores fixos
- Logging adequado em pontos críticos

**Pontos Negativos:**
- Comentários em português com caracteres especiais mal codificados (encoding issues)
- Queries SQL embutidas em arquivos XML ao invés de usar JPA/Hibernate ou MyBatis
- Lógica de negócio complexa no ItemReader (deveria estar no Processor)
- Falta de documentação JavaDoc nas classes
- Código duplicado nas queries SQL para os três tipos de produto
- Uso de múltiplos databases com nomenclaturas inconsistentes (DBGESTAO, DbGestaoDebitoContaCorrente)
- Falta de testes unitários abrangentes (apenas um teste de integração)
- Hardcoded de valores como "10 dias" no cálculo de datas
- Mistura de responsabilidades no ItemWriter (envio para fila + atualização de banco)
- Uso de framework proprietário (BV Framework) que dificulta manutenção e portabilidade

---

## 14. Observações Relevantes

1. **Framework Proprietário**: O sistema utiliza o BV Framework Batch, um framework proprietário da BV Sistemas, o que pode dificultar a manutenção por desenvolvedores não familiarizados com essa tecnologia.

2. **Múltiplos Ambientes**: O sistema possui configurações específicas para 4 ambientes (DES, QA, UAT, PRD) com credenciais e servidores diferentes.

3. **Criptografia de Senhas**: Em ambientes QA, UAT e PRD, as senhas são criptografadas utilizando o nome do sistema como chave no algoritmo.

4. **Processamento em Lote**: O sistema processa três tipos de produtos em sequência, consolidando os resultados antes de enviar para a fila.

5. **Estratégia de Retomada**: Implementa uma estratégia customizada de retomada (MyResumeStrategy) que permite continuar o processamento após erros, desde que o exitCode seja 0.

6. **Docker para Desenvolvimento**: Inclui configuração Docker Compose para subir ambiente RabbitMQ local para testes.

7. **Versionamento**: O projeto está na versão 0.15.0, indicando que ainda está em fase de evolução.

8. **Jenkins Integration**: Possui arquivo jenkins.properties configurado para integração contínua, com deploy em QA desabilitado (disableQADeploy=true).

9. **Encoding Issues**: Há problemas de encoding em comentários e strings, com caracteres especiais mal formatados (ex: "Cr�dito", "gera��o").

10. **Transações XA**: Utiliza Bitronix para gerenciamento de transações distribuídas (JTA), permitindo rollback em caso de falhas no envio para a fila ou atualização do banco.