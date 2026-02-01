# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **javabatch-ccbd-base-debito-auto-credito-baixa-digital** é um job batch Java desenvolvido para processar pagamentos de débito automático. Sua função principal é buscar remessas de pagamento de débito automático do banco de dados MySQL, transformá-las em mensagens JSON e publicá-las em uma fila RabbitMQ para processamento posterior. O sistema também atualiza o status de agendamentos pendentes antes de iniciar o processamento das remessas.

O batch segue o padrão Reader-Processor-Writer, utilizando o framework BV Sistemas para gerenciamento de jobs batch, com suporte a transações, logging estruturado e estratégias de retomada em caso de falhas.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Responsável por ler as remessas de débito automático do banco de dados MySQL através do RemessaRepository. Inicializa o processamento finalizando agendamentos pendentes e busca as remessas elegíveis para processamento. |
| **ItemProcessor** | Processa cada remessa lida. Atualmente apenas registra logs, sem transformações adicionais. |
| **ItemWriter** | Converte objetos RemessaPlain em RemessaDTO, serializa para JSON e publica na fila RabbitMQ (exchange: ex.ccbd.baixa.debito.automatico). |
| **ItemMapper** | Realiza o mapeamento entre RemessaPlain (modelo de banco) e RemessaDTO (modelo de mensageria). |
| **RemessaRepository / RemessaRepositoryImpl** | Interface e implementação para acesso ao banco de dados. Busca remessas e atualiza status de agendamentos pendentes. |
| **RemessaMapper** | Mapeia ResultSet do banco de dados para objetos RemessaPlain. |
| **RemessaDTO** | Objeto de transferência de dados usado para serialização JSON e envio para fila. |
| **RemessaPlain** | Modelo de dados que representa uma remessa lida do banco de dados. |
| **MyResumeStrategy** | Estratégia de retomada do job em caso de falha, verificando o código de saída. |
| **DebitoAutoCreditoException** | Exceção customizada com código de saída específico. |
| **ExitCodeEnum** | Enumeração dos códigos de saída do batch (OK, ERRO_LER_BASE_DE_DADOS, ERRO_POSTAR_MENSAGEM_FILA). |
| **SQLUtil** | Utilitário para carregar queries SQL de arquivos XML. |

---

## 3. Tecnologias Utilizadas

- **Java** (linguagem de programação)
- **Maven** (gerenciamento de dependências e build)
- **Spring Framework** (injeção de dependências, JDBC, AMQP)
- **Spring AMQP / Spring Rabbit** (integração com RabbitMQ)
- **MySQL** (banco de dados relacional)
- **MySQL Connector/J 8.0.22** (driver JDBC)
- **RabbitMQ** (message broker para filas)
- **Bitronix** (gerenciador de transações JTA)
- **Log4j** (logging)
- **Jackson** (serialização/deserialização JSON)
- **BV Framework Batch** (framework proprietário para jobs batch)
- **BV Crypto** (criptografia de senhas)
- **JUnit** (testes unitários)

---

## 4. Principais Endpoints REST

**não se aplica** - Este é um sistema batch que não expõe endpoints REST. A comunicação é feita através de filas RabbitMQ.

---

## 5. Principais Regras de Negócio

1. **Finalização de Agendamentos Pendentes**: Antes de processar as remessas, o sistema atualiza todos os agendamentos com status 1 (pendente) para status 7 (finalizado) na data de vencimento especificada, para produtos de tipo 2, 3 ou 4.

2. **Seleção de Remessas**: Busca remessas com data de vencimento igual à data de processamento (parâmetro ou data atual), com status de pagamento 4, 6 ou 7, e para produtos de débito automático dos tipos 2, 3 ou 4.

3. **Transformação de Dados**: Realiza ajustes nos dados durante o mapeamento, como substring do código do banco (3 primeiros caracteres) e código da agência (4 primeiros caracteres).

4. **Publicação em Fila**: Cada remessa processada é convertida em JSON e publicada individualmente na fila RabbitMQ com encoding UTF-8 e content-type JSON.

5. **Tratamento de Erros**: Em caso de erro na leitura do banco ou publicação na fila, o job define códigos de saída específicos (10 ou 30) e lança exceções para interromper o processamento.

6. **Parâmetro Opcional**: O sistema aceita um parâmetro opcional "dataProcessamento" (formato yyyy-MM-dd). Se não fornecido, utiliza a data atual do sistema.

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **RemessaPlain**: Representa uma remessa de débito automático lida do banco de dados, contendo informações de pagamento, pessoa, conta e produto.

- **RemessaDTO**: Versão simplificada e padronizada da remessa para envio via mensageria.

**Relacionamentos (baseados nas queries SQL):**

- **TbPagamentoDebitoAutomatico** (remessa principal)
  - Relaciona-se com **TbPessoaDebitoAutomatico** (dados do CPF/CNPJ e conta bancária)
  - Relaciona-se com **TbArquivoDebitoAutomatico** (arquivo de origem)
  - Relaciona-se com **TbConvenioDebitoAutomatico** (dados do convênio/beneficiário)
  - Relaciona-se com **TbStatusPagamentoDebitoAtmto** (status do pagamento)

- **TbConvenioDebitoAutomatico**
  - Relaciona-se com **TbTipoProdutoDebitoAutomatico** (tipo de produto: 2, 3 ou 4)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbPagamentoDebitoAutomatico | tabela | SELECT | Tabela principal contendo os pagamentos de débito automático |
| TbPessoaDebitoAutomatico | tabela | SELECT | Dados cadastrais da pessoa (CPF/CNPJ) e conta bancária |
| TbArquivoDebitoAutomatico | tabela | SELECT | Informações sobre o arquivo de remessa |
| TbConvenioDebitoAutomatico | tabela | SELECT | Dados do convênio/beneficiário (banco, agência, conta) |
| TbTipoProdutoDebitoAutomatico | tabela | SELECT | Tipo de produto de débito automático |
| TbStatusPagamentoDebitoAtmto | tabela | SELECT | Status do pagamento |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbPagamentoDebitoAutomatico | tabela | UPDATE | Atualiza status de agendamentos pendentes (status 1) para finalizado (status 7) na data de vencimento especificada |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| RemessaRepositoryImpl-sql.xml | leitura | SQLUtil / RemessaRepositoryImpl | Arquivo XML contendo as queries SQL (buscarRemessas e atualizarAgendamentosPendentes) |
| log/robo.log | gravação | Log4j (RollingFileAppender) | Log principal da aplicação com rotação por tamanho (2MB, 5 backups) |
| log/statistics-${executionId}.log | gravação | BvDailyRollingFileAppender | Log de estatísticas do batch com rotação diária |

---

## 10. Filas Lidas

**não se aplica** - O sistema não consome mensagens de filas. Ele apenas publica mensagens.

---

## 11. Filas Geradas

**Exchange**: ex.ccbd.baixa.debito.automatico  
**Routing Key**: ccbd.baixa_DebitoAutomatico  
**Broker**: RabbitMQ

**Descrição**: O sistema publica mensagens JSON contendo dados de remessas de débito automático processadas. Cada mensagem representa uma remessa individual com informações de pagamento, pessoa, conta e produto.

**Formato da Mensagem**: JSON (RemessaDTO serializado) com encoding UTF-8.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| MySQL (CCBDDebitoAutomatico) | Banco de Dados | Banco de dados principal contendo informações de débito automático. Conexão via JDBC com pool de conexões Bitronix. |
| RabbitMQ | Message Broker | Sistema de mensageria para publicação de remessas processadas. Configurado com confirmação de publicação (publisherConfirms e publisherReturns). |

**Ambientes configurados:**
- LOCAL: localhost (MySQL e RabbitMQ)
- DES: gcmysdgdes07-proxy.bvnet.bv (MySQL), 10.39.216.137 (RabbitMQ)
- UAT: gcmysdguat07-proxy.bvnet.bv (MySQL), 10.39.88.47 (RabbitMQ)
- PRD: gcmysdgprd07-proxy.bvnet.bv (MySQL), 10.39.49.197 (RabbitMQ)

---

## 13. Avaliação da Qualidade do Código

**Nota:** 6/10

**Justificativa:**

**Pontos Positivos:**
- Estrutura bem organizada seguindo padrão Reader-Processor-Writer
- Separação clara de responsabilidades entre camadas (batch, repository, model)
- Uso adequado de logging para rastreabilidade
- Tratamento de exceções com códigos de saída específicos
- Configuração externalizada por ambiente
- Uso de framework batch consolidado (BV Framework)

**Pontos Negativos:**
- **Nomenclatura inconsistente**: Nomes de campos no banco (tpdaCdStatusPagamentoDebitoAtmto) são pouco legíveis e não seguem convenções Java
- **ItemProcessor vazio**: A classe ItemProcessor não realiza nenhuma transformação, apenas registra logs, indicando possível código não utilizado ou incompleto
- **Falta de validações**: Não há validação de dados antes de publicar na fila
- **Hardcoded values**: Exchange e routing key estão hardcoded no ItemWriter
- **Falta de testes**: Apenas um teste de integração básico, sem cobertura de cenários de erro
- **Documentação limitada**: Falta de JavaDoc nas classes e métodos
- **Tratamento de senha**: Senhas em texto claro nos arquivos de configuração de teste
- **Dependências desatualizadas**: Uso de versões antigas de algumas bibliotecas

---

## 14. Observações Relevantes

1. **Framework Proprietário**: O sistema utiliza o framework BV Sistemas (br.com.bvsistemas), que é proprietário e pode dificultar manutenção por equipes externas.

2. **Criptografia de Senhas**: Em produção e UAT, as senhas são criptografadas usando BVCrypto, mas nos ambientes de desenvolvimento e local estão em texto claro.

3. **Versão do Projeto**: Versão atual 0.11.0, indicando que o sistema ainda está em evolução.

4. **Processamento Síncrono**: Cada remessa é processada e publicada individualmente, o que pode impactar performance em grandes volumes.

5. **Transações**: O job está configurado como "noTransactionJobTemplate", indicando que não há controle transacional automático.

6. **Estratégia de Retomada**: O sistema pode retomar execução apenas se o código de saída for 0 (sucesso), conforme implementado em MyResumeStrategy.

7. **Parâmetro de Data**: O sistema aceita data de processamento como parâmetro, permitindo reprocessamento de datas específicas.

8. **Tipos de Produto**: O sistema processa apenas produtos de débito automático dos tipos 2, 3 e 4, conforme filtros nas queries SQL.

9. **Status de Pagamento**: Processa apenas remessas com status 4, 6 ou 7, que provavelmente representam pagamentos confirmados, processados ou finalizados.

10. **Deploy**: Configuração Jenkins indica que o deploy em QA está desabilitado (disableQADeploy=true).