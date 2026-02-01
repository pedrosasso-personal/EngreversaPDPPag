# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-sitp-base-atom-integrar-pagamento** é um serviço atômico desenvolvido em Java com Spring Boot, responsável por integrar operações de pagamento entre diferentes sistemas do Banco Votorantim. Atua como intermediário entre o sistema PGFT (Plataforma de Gestão Financeira e Tesouraria) e o sistema legado ITP (Integração de Pagamentos), realizando cadastros de lançamentos na caixa de entrada, consultas de parametrizações, validações de circuit break e conversões automáticas entre diferentes câmaras de liquidação (CIP, STR, DOC). O sistema consome mensagens de filas RabbitMQ para processar solicitações de pagamento e expõe APIs REST para consultas e operações relacionadas.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal que inicializa a aplicação Spring Boot com suporte a Feature Toggle e Cache |
| **LancamentoCaixaEntradaListener** | Listener RabbitMQ que consome mensagens de solicitação de pagamento e processa cadastros no ITP |
| **CadastroController** | Controller REST para operações de consulta de cadastros (bancos, filiais, contas, etc.) |
| **CircuitBreakController** | Controller REST para verificação de circuit break em operações de pagamento |
| **ParametrizacaoController** | Controller REST para conversão automática de TEDs entre câmaras de liquidação |
| **StnController** | Controller REST para consultas relacionadas à Secretaria do Tesouro Nacional |
| **LancamentoService** | Serviço de negócio para cadastro e consulta de lançamentos no ITP |
| **CadastroGlobalService** | Serviço de negócio para consultas de cadastros globais (bancos, filiais, configurações) |
| **ConversaoService** | Serviço de negócio para conversão automática de TEDs entre CIP e STR |
| **FeatureToggleService** | Serviço para gerenciamento de feature toggles e validações de circuit break |
| **JdbiRepositoryConfiguration** | Configuração de repositórios JDBI para acesso ao banco de dados Sybase |
| **RedisConfiguration** | Configuração de cache Redis com tratamento de erros e timeouts |

---

## 3. Tecnologias Utilizadas

- **Java 21** - Linguagem de programação
- **Spring Boot 2.7.x** - Framework principal
- **Spring Security OAuth2** - Segurança e autenticação JWT
- **JDBI 3.19.0** - Framework de acesso a dados
- **Sybase ASE 16.3** - Banco de dados principal
- **RabbitMQ** - Mensageria assíncrona
- **Redis** - Cache distribuído (Lettuce client)
- **Prometheus + Grafana** - Monitoramento e métricas
- **Docker** - Containerização
- **Lombok** - Redução de boilerplate
- **ModelMapper** - Mapeamento de objetos
- **OpenAPI/Swagger** - Documentação de APIs
- **ConfigCat** - Feature Toggle
- **HikariCP** - Pool de conexões
- **Logback** - Logging
- **Maven** - Gerenciamento de dependências

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/cadastro/v1/protocolo` | CadastroController | Consulta dados de um protocolo PGFT/ITP |
| GET | `/cadastro/v1/bancos` | CadastroController | Consulta banco por código COMPE |
| GET | `/cadastro/v1/bancos/ispb` | CadastroController | Consulta banco por código ISPB |
| GET | `/cadastro/v1/filiais` | CadastroController | Consulta filial por código |
| GET | `/cadastro/v1/config-cip` | CadastroController | Consulta parametrizações CIP |
| GET | `/cadastro/v1/conta-cliente` | CadastroController | Consulta conta corrente de cliente |
| POST | `/cadastro/v1/caixa-entrada` | CadastroController | Cadastra lançamento na caixa de entrada ITP |
| GET | `/cadastro/v1/consulta-status` | CadastroController | Consulta status de lançamento |
| GET | `/circuit-break/` | CircuitBreakController | Verifica se circuit break está ativo |
| POST | `/circuit-break-v2/` | CircuitBreakV2Controller | Validação de circuit break com mecanismo de trava |
| POST | `/parametrizacao/v1/conversao-ted` | ParametrizacaoController | Conversão automática de TED entre câmaras |
| GET | `/v1/unidade-gestora/{codigoUnidade}` | StnController | Consulta conta financeira de unidade gestora STN |
| PUT | `/cadastro/v1/atualiza-login` | CadastroController | Atualiza login de devolução no PGFT |
| POST | `/cadastro/v1/bancos/migracao` | CadastroController | Atualiza flag de migração de cliente |

---

## 5. Principais Regras de Negócio

1. **Cadastro de Lançamentos**: Validação e cadastro de lançamentos de pagamento na caixa de entrada do ITP, com verificação de duplicidade por código SPAG
2. **Circuit Break**: Mecanismo de proteção que bloqueia operações de pagamento baseado em regras configuráveis (documento, banco, liquidação, tipo de lançamento, valor)
3. **Conversão Automática de TED**: Conversão inteligente entre câmaras CIP e STR baseada em horário, valor, finalidade e disponibilidade do banco
4. **Validação de Grade Horária**: Verificação de janelas de operação das câmaras de liquidação
5. **Validação de Finalidade**: Verificação de finalidades permitidas para cada tipo de operação (PAG, TED)
6. **Controle de Débito sem Saldo**: Validação de permissão para débito sem saldo disponível por conta/empresa
7. **Validação de Pagamento a Terceiros**: Verificação de permissão para pagamentos a terceiros
8. **Tratamento de Caracteres Especiais**: Remoção de acentos e caracteres inválidos em nomes e históricos
9. **Validação CIP**: Verificação de valores mínimos/máximos e contingência para operações CIP
10. **Cache de Consultas**: Otimização de consultas frequentes com cache Redis (1 hora de TTL)

---

## 6. Relação entre Entidades

**Principais Entidades e Relacionamentos:**

- **LancamentoCaixaEntradaDomain**: Entidade principal que agrega:
  - **LancamentoTransacaoDomain**: Dados da transação (liquidação, filial, transação, origem, evento)
  - **LancamentoMovimentacaoDomain**: Dados da movimentação (valor, data, histórico)
  - **LancamentoParticipanteDomain**: Remetente e Favorecido (cliente, conta, banco)
  - **LancamentoCoParticipanteDomain**: Co-titulares (remetente e favorecido)
  - **LancamentoBoletoTributoDomain**: Dados de boleto/tributo (linha digitável, vencimento)
  - **LancamentoOrigemPagamentoDomain**: Origem do pagamento (canal, sistema origem, protocolo)
  - **LancamentoFintechDomain**: Dados de fintech (remetente e favorecido fintech)
  - **LancamentoPortadorDomain**: Dados do portador

- **TransacaoDomain**: Define tipo de transação, códigos de origem/destino CC, indicadores
- **FilialDomain**: Dados cadastrais da filial (CNPJ, endereço, agência)
- **BancoDomain**: Dados do banco (ISPB, COMPE, nome)
- **ConfigTesourariaDomain**: Parametrizações de tesouraria (CPMF, limites, alertas)
- **CamaraLiquidacaoDomain**: Grade horária e parâmetros de conversão das câmaras

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBISPB..tb_ispb_ispb | tabela | SELECT | Cadastro de bancos ISPB |
| DBGLOBAL..TbBanco | tabela | SELECT | Cadastro global de bancos |
| DBITP..TBL_FILIAL_SPB | tabela | SELECT | Cadastro de filiais |
| dbpgf_tes..TbParametroCamaraLiquidacao | tabela | SELECT | Parâmetros e grade horária das câmaras |
| dbpgf_tes..TbParametroInterfaceCIP | tabela | SELECT | Configurações da interface CIP |
| dbpgf_tes..tbl_setup_tesouraria | tabela | SELECT | Configurações de tesouraria |
| DBGLOBAL..VwClienteContaCorrente | view | SELECT | Dados de contas correntes de clientes |
| dbispb..tb_doat_dominio_atributo | tabela | SELECT | Tabela de domínios e atributos |
| DBITP..TBL_FINALIDADE_SPB | tabela | SELECT | Finalidades de pagamento |
| DBITP..TBL_TRANSACAO_SPB | tabela | SELECT | Transações disponíveis |
| DBITP..TBL_TRIBUTOS_SPB | tabela | SELECT | Cadastro de tributos |
| dbpgf_tes..tbl_lancamento | tabela | SELECT | Lançamentos do PGFT |
| DBITP..TBL_CAIXA_ENTRADA_SPB | tabela | SELECT | Caixa de entrada ITP |
| dbpgf_tes..TbParametroRoboCliente | tabela | SELECT | Parâmetros por conta cliente |
| dbpgf_tes..TbParametroRoboEmpresa | tabela | SELECT | Parâmetros por empresa |
| DBPGF_TES..TbProcessamentoRoboPGFT | tabela | SELECT | Status de processamento PGFT |
| DBPGF_TES..TbUnidadeGestoraConveniada | tabela | SELECT | Unidades gestoras STN |
| dbispb..TbControleMigracaoSPAG | tabela | SELECT | Controle de migração de clientes |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBITP..TBL_CAIXA_ENTRADA_SPB | tabela | INSERT | Cadastro de novos lançamentos via procedure BV_INCLUSAO_CAIXA_ENTRADA_V2 |
| DBPGF_TES..TBL_LANCAMENTO | tabela | UPDATE | Atualização de login de devolução e histórico de documento |
| dbispb..TbControleMigracaoSPAG | tabela | UPDATE | Atualização de flag de migração de clientes |
| DBISPB..TBL_PARAMETROS | tabela | UPDATE | Atualização de flags de recebimento SPB BV |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | leitura | /usr/etc/log/ | Configuração de logging por ambiente |
| application.yml | leitura | src/main/resources/ | Configurações da aplicação |
| integrar-pagamento-contracts.yaml | leitura | src/main/resources/swagger/ | Contrato OpenAPI das APIs |
| *.sql | leitura | src/main/resources/.../repository/ | Queries SQL para operações de banco |

---

## 10. Filas Lidas

- **events.business.SPAG-BASE.integrarPagamentoITP**: Fila principal que consome mensagens de solicitação de cadastro de pagamento no ITP. Possui DLQ configurada (events.business.SPAG-BASE.integrarPagamentoITP.DLQ) para mensagens com falha.

---

## 11. Filas Geradas

- **events.business.retornoPagamentoITP** (routing key: SPAG.retornoPagamentoITP.SPAG.waiting): Fila para envio de confirmação de cadastro de lançamento com o código de protocolo ITP gerado.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **PGFT** | Banco de dados Sybase | Sistema de gestão financeira e tesouraria - consulta e atualização de lançamentos |
| **ITP** | Banco de dados Sybase | Sistema legado de integração de pagamentos - cadastro na caixa de entrada |
| **DBGLOBAL** | Banco de dados Sybase | Base global de cadastros (bancos, clientes, contas) |
| **DBISPB** | Banco de dados Sybase | Base de dados ISPB (bancos, domínios, controle de migração) |
| **RabbitMQ** | Mensageria | Consumo e publicação de mensagens de pagamento |
| **Redis** | Cache | Cache distribuído para otimização de consultas |
| **ConfigCat** | Feature Toggle | Gerenciamento de feature flags e circuit break |
| **Prometheus** | Monitoramento | Coleta de métricas da aplicação |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7,5/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (presentation, service, domain, infrastructure)
- Uso adequado de padrões como Repository, Mapper e Domain-Driven Design
- Implementação de cache Redis com tratamento de erros robusto
- Configuração de monitoramento e observabilidade (Prometheus, Grafana)
- Uso de Feature Toggle para controle de funcionalidades
- Tratamento de caracteres especiais e sanitização de logs
- Configuração de circuit break para proteção do sistema

**Pontos de Melhoria:**
- Presença de lógica de negócio complexa em classes utilitárias (ConversaoUtil)
- Alguns métodos muito extensos com múltiplas responsabilidades (validações de conversão)
- Uso de Optional.get() sem verificação adequada em alguns pontos
- Comentários em português misturados com código em inglês
- Falta de documentação JavaDoc em várias classes
- Alguns magic numbers e strings hardcoded que poderiam ser constantes
- Tratamento de exceções genérico em alguns pontos (catch Exception)
- Queries SQL embutidas em arquivos separados (boa prática) mas sem documentação

---

## 14. Observações Relevantes

1. **Ambiente Multi-Perfil**: Sistema configurado para múltiplos ambientes (local, des, qa, uat, prd) com parametrizações específicas via ConfigMap/Secret do Kubernetes

2. **Procedure Sybase**: O cadastro principal utiliza a procedure `BV_INCLUSAO_CAIXA_ENTRADA_V2` que retorna código de protocolo e status via OUT parameters

3. **Conversão Inteligente**: Sistema implementa lógica sofisticada de conversão automática entre CIP e STR baseada em múltiplos critérios (horário, valor, finalidade, disponibilidade do banco)

4. **Circuit Break Configurável**: Mecanismo de proteção altamente configurável via Feature Toggle, permitindo bloqueio por documento, banco, liquidação, tipo de lançamento e valor

5. **Cache Estratégico**: Implementação de cache Redis com TTL de 1 hora para consultas de cadastros, com tratamento de falhas que permite operação degradada

6. **Segurança**: Autenticação via JWT com múltiplos issuers configurados por ambiente

7. **Resiliência**: Implementação de AsyncAppender para logs, tratamento de erros de cache, e DLQ para mensagens com falha

8. **Monitoramento**: Dashboard Grafana completo com métricas de JVM, HTTP, HikariCP, GC e logs

9. **Containerização**: Dockerfile otimizado com multi-layer para melhor aproveitamento de cache

10. **Migração Controlada**: Sistema possui controle de migração de clientes entre SPAG e ITP via flags configuráveis