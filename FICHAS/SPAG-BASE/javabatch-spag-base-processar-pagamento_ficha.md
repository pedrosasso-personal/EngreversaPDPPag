# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **javabatch-spag-base-processar-pagamento** é uma aplicação batch Java desenvolvida para processar pagamentos e realizar integração entre os sistemas SPAG (Sistema de Pagamentos) e ITP (Sistema de Integração de Transações de Pagamento). 

O sistema possui dois fluxos principais:
1. **Processamento de Pagamentos**: Busca lançamentos não processados ou específicos (manuais), processa-os e envia notificações de sucesso ou erro para filas RabbitMQ.
2. **Integração SPAG x ITP (Contingência)**: Busca lançamentos em processamento, converte-os para o formato esperado pelo ITP e envia para fila de integração.

O sistema utiliza o framework BV Sistemas para batch processing, com suporte a transações distribuídas via Bitronix, e integra-se com bancos de dados SQL Server (DBSPAG) e Sybase (DBITP), além de utilizar RabbitMQ para mensageria.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** (batch) | Lê lançamentos não processados ou manuais do banco DBSPAG |
| **ItemProcessor** (batch) | Processa lançamentos e gera mensagens de fila (notificações ou retornos ITP) |
| **ItemWriter** (batch) | Envia mensagens processadas para filas RabbitMQ |
| **ItemReader** (integracaospagitp) | Lê lançamentos em processamento para integração com ITP |
| **ItemProcessor** (integracaospagitp) | Converte lançamentos SPAG para formato LancamentoIntegracaoItp |
| **ItemWriter** (integracaospagitp) | Envia lançamentos convertidos para fila de integração ITP |
| **ProcessarPagamento** | Orquestra busca de lançamentos (manuais ou automáticos) e preenche protocolos vazios |
| **LancamentoDAOImpl** | Acesso a dados de lançamentos no banco DBSPAG |
| **CaixaEntradaDAOImpl** | Acesso a dados da caixa de entrada no banco DBITP |
| **BancoDAOImpl** | Busca informações de bancos no DBITP |
| **FilaRabbitServiceImpl** | Serviço de envio de mensagens para filas RabbitMQ |
| **RabbitMQConnectionProvider** | Gerencia conexões e envio de mensagens ao RabbitMQ |
| **LancamentoMapper** | Mapeia ResultSet para objetos de domínio Lancamento |

---

## 3. Tecnologias Utilizadas

- **Java** (versão não especificada no código)
- **Maven** (gerenciamento de dependências e build)
- **Spring Framework** (injeção de dependências e configuração)
- **BV Sistemas Framework Batch** (framework proprietário para processamento batch)
- **Bitronix** (gerenciador de transações distribuídas - JTA/XA)
- **SQL Server** (banco de dados DBSPAG)
- **Sybase** (banco de dados DBITP)
- **RabbitMQ** (mensageria - versão 4.11.3)
- **Gson** (serialização JSON - versão 2.8.6)
- **Log4j** (logging)
- **JUnit** (testes unitários)

---

## 4. Principais Endpoints REST

não se aplica

---

## 5. Principais Regras de Negócio

1. **Busca de Lançamentos**: O sistema busca lançamentos com status 1 ou 7 (em processamento), do banco 655 (remetente), e com códigos de liquidação específicos (1, 21, 22, 31, 32, 61, 62).

2. **Processamento Manual vs Automático**: O sistema pode processar lançamentos específicos (modo manual) ou buscar automaticamente lançamentos não processados.

3. **Notificação vs Retorno ITP**: Dependendo do status do lançamento (1 ou 7 = retorno ITP; 3, 4 ou 99 = notificação), o sistema gera mensagens diferentes.

4. **Conversão de Códigos de Banco**: O sistema converte códigos de banco COMPE para códigos globais do sistema ITP.

5. **Ajuste de Tipo de Conta**: Tipos de conta são convertidos de formato numérico (1-7) para formato de 2 caracteres (CI, IF, PP, CO, CC, CT, PG).

6. **Preenchimento de Protocolos Vazios**: Lançamentos sem protocolo são buscados na caixa de entrada do ITP para completar a informação.

7. **Integração SPAG x ITP**: Lançamentos são convertidos para o formato esperado pelo ITP, incluindo dados de remetente, favorecido, co-titulares e clientes fintech.

8. **Roteamento de Mensagens**: Mensagens de notificação são roteadas para filas diferentes dependendo do status (sucesso ou erro) e origem.

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **Lancamento**: Entidade central representando um lançamento de pagamento
  - Relacionamento 1:1 com **LancamentoPessoa** (dados de remetente e favorecido)
  - Relacionamento 0:1 com **LancamentoFintech** (dados de clientes fintech, quando aplicável)

- **LancamentoIntegracaoItp**: Representação do lançamento no formato ITP
  - Contém **ParticipanteIntegracaoItp** (remetente e favorecido)
  - Contém **CoParticipanteIntegracaoItp** (co-titulares)
  - Contém **ContaCorrenteIntegracaoItp** (dados de conta corrente)

- **CaixaEntrada**: Representa entrada na caixa do ITP, espelhando dados do lançamento

- **MensagemFila**: Envelope para mensagens enviadas às filas
  - Pode conter **MensagemRetornoITP** ou **MensagemNotificacao**

- **Banco**: Entidade auxiliar para conversão de códigos bancários

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbLancamento | tabela | SELECT | Lançamentos de pagamento do sistema SPAG |
| TbLancamentoPessoa | tabela | SELECT | Dados de pessoas (remetente/favorecido) dos lançamentos |
| TbLancamentoClienteFintech | tabela | SELECT | Dados de clientes fintech relacionados aos lançamentos |
| TbStatusLancamento | tabela | SELECT | Descrições dos status de lançamento |
| DBGLOBAL..TbBanco | tabela | SELECT | Informações de bancos (conversão de códigos) |
| tbl_caixa_entrada_spb | tabela | SELECT | Caixa de entrada do sistema ITP |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| tbl_caixa_entrada_spb | tabela | INSERT | Inserção de lançamentos na caixa de entrada do ITP via procedure BV_INCLUSAO_CAIXA_ENTRADA_V2 (código comentado, não utilizado atualmente) |

**Observação**: O código de inserção na caixa de entrada está presente na classe `CaixaEntradaDAOImpl`, mas não é chamado pelos fluxos principais analisados.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| log/robo.log | gravação | log4j.xml | Arquivo de log principal da aplicação |
| log/statistics-${executionId}.log | gravação | log4j.xml | Arquivo de log de estatísticas de execução do batch |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

| Nome da Fila/Exchange | Routing Key | Descrição |
|----------------------|-------------|-----------|
| events.business.retornoPagamentoITP | SPAG.retornoPagamentoITP.SPAG.waiting | Retorno de pagamentos processados para o ITP |
| events.business.esteiraPagamentoOk | SPAG.esteiraPagamentoOk.{origem} | Notificações de pagamentos processados com sucesso |
| events.business.esteiraPagamentoErro | SPAG.esteiraPagamentoErro.{origem} | Notificações de pagamentos com erro |
| events.business.integrarPagamentoITP | SPAG.integrarPagamentoITP.v1 | Lançamentos para integração com ITP (contingência) |

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| DBSPAG (SQL Server) | Banco de Dados | Base de dados principal do sistema SPAG |
| DBITP (Sybase) | Banco de Dados | Base de dados do sistema ITP |
| DBGLOBAL (Sybase) | Banco de Dados | Base de dados global para informações de bancos |
| RabbitMQ | Mensageria | Sistema de filas para comunicação assíncrona entre sistemas |

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades (DAOs, Services, Mappers)
- Uso de padrões de projeto adequados (Factory, Strategy)
- Logging presente em pontos críticos
- Uso de framework batch estruturado

**Pontos Negativos:**
- **Código comentado extensivamente**: Várias classes contêm métodos completos comentados (ex: `preencherCaixaEntrada` no `ItemProcessor` de integração), indicando incerteza sobre funcionalidades
- **Falta de tratamento de exceções**: Muitos blocos catch vazios ou com apenas log, sem tratamento adequado
- **Hardcoded values**: Valores como código de banco (655), status (1, 7, 3, 4, 99) estão espalhados pelo código
- **Falta de documentação**: Ausência de JavaDoc na maioria das classes e métodos
- **Complexidade em métodos**: Alguns métodos são muito longos (ex: `preencherLancamentoItp`, queries SQL inline)
- **Inconsistência de nomenclatura**: Mistura de português e inglês nos nomes
- **Acoplamento**: Dependência direta de classes concretas em alguns pontos
- **Testes limitados**: Apenas um teste unitário básico presente

---

## 14. Observações Relevantes

1. **Dois Jobs Distintos**: O sistema possui dois jobs batch configurados:
   - `job`: Processamento padrão de pagamentos
   - `integracaospagitp-job`: Integração SPAG x ITP (contingência)

2. **Configuração de Ambiente**: As configurações de banco de dados estão hardcoded nos XMLs de recursos, com credenciais expostas (ambiente de desenvolvimento).

3. **Transações Distribuídas**: O sistema utiliza Bitronix para gerenciar transações distribuídas entre múltiplos bancos de dados.

4. **Modo Manual**: O sistema suporta processamento manual através do parâmetro `PARAM_LANCAMENTO`, permitindo reprocessamento de lançamentos específicos.

5. **Modo Notificação**: Através do parâmetro `PARAM_NOTIFICACAO`, é possível executar apenas o envio de notificações sem reprocessar lançamentos.

6. **Conversão de Códigos**: Existe uma lógica complexa de conversão entre códigos de banco COMPE e códigos globais do sistema.

7. **Headers RabbitMQ**: As mensagens enviadas ao RabbitMQ incluem headers customizados para roteamento e identificação.

8. **Isolamento de Leitura**: As queries utilizam `AT ISOLATION 0` (dirty read) para melhor performance em leituras.

9. **Framework Proprietário**: O sistema utiliza extensivamente o framework BV Sistemas, o que pode dificultar manutenção por desenvolvedores não familiarizados.

10. **Dados Sensíveis**: O código manipula dados financeiros sensíveis (CPF/CNPJ, contas bancárias), mas não há evidência de criptografia ou ofuscação.