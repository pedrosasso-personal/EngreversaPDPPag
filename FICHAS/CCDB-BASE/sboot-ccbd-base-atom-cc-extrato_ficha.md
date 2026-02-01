# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de consulta e gerenciamento de extratos bancários de contas correntes do Banco Votorantim (BV). O sistema fornece APIs REST para consulta de movimentações financeiras, detalhamento de transações, histórico de documentos e categorização de operações bancárias. Suporta diversos tipos de transações incluindo TED, TEF, PIX, boletos, cartão de débito, tarifas e operações de crédito.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `CcextratoApiDelegateImpl` | Controller principal que implementa os endpoints REST da API |
| `ConsultaExtratoService` | Serviço para consulta de extratos por data ou quantidade |
| `ConsultaExtratoPesquisasService` | Serviço para consulta de extratos com filtros avançados |
| `ExtratoMovimentacoesService` | Serviço para consulta de movimentações com saldo |
| `DetalheMovimentacaoService` | Serviço para obter detalhes de movimentações específicas |
| `ConsultaMovimentacaoService` | Serviço para consulta de movimentações por protocolo e totalizações |
| `ConsultaCategoriaService` | Serviço para categorização de transações |
| `ConsultaExtratoRepository` | Repositório para acesso aos dados de movimentações |
| `MovimentacoesRepository` | Repositório para consultas específicas de movimentações |
| `DadosEntradaValidator` | Validador de dados de entrada das requisições |
| `CategoriaTransacao` | Enum que define as categorias de transações bancárias |

## 3. Tecnologias Utilizadas

- **Framework**: Spring Boot 2.x
- **Linguagem**: Java 11+
- **Build**: Maven 3.8+
- **Banco de Dados**: Sybase ASE (DBCONTACORRENTE, DBITP, DBGLOBAL), SQL Server (boletos)
- **Acesso a Dados**: JDBI 3.13.0
- **Segurança**: Spring Security OAuth2 Resource Server com JWT
- **Documentação API**: OpenAPI 3.0 / Swagger
- **Monitoramento**: Spring Actuator, Prometheus, Grafana
- **Mapeamento**: MapStruct
- **Utilitários**: Apache Commons Lang3, Apache Commons Text, Lombok

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/cc-extrato` | `CcextratoApiDelegateImpl` | Consulta movimentações com paginação por data ou quantidade |
| POST | `/v1/cc-extrato/pesquisas` | `CcextratoApiDelegateImpl` | Consulta movimentações com filtros avançados |
| GET | `/v1/cc-extrato/extrato` | `CcextratoApiDelegateImpl` | Consulta extrato de movimentações por favorecido/período |
| GET | `/v1/cc-extrato/categoria` | `CcextratoApiDelegateImpl` | Consulta categoria de uma movimentação específica |
| GET | `/v1/cc-extrato/detalhe` | `CcextratoApiDelegateImpl` | Obtém detalhes completos de uma movimentação |
| GET | `/v1/cc-extrato/consulta/{protocolo}` | `CcextratoApiDelegateImpl` | Consulta movimentação por número de protocolo |
| GET | `/v1/cc-extrato/total` | `CcextratoApiDelegateImpl` | Calcula total de movimentações por tipo e período |
| GET | `/v1/cc-extrato/historico` | `CcextratoApiDelegateImpl` | Consulta histórico de documento |
| GET | `/v1/cc-extrato/historico-nsu` | `CcextratoApiDelegateImpl` | Consulta histórico por NSU |

## 5. Principais Regras de Negócio

- **Categorização de Transações**: Sistema categoriza automaticamente transações em mais de 50 tipos diferentes (TED, TEF, PIX, boletos, tarifas, etc.)
- **Validação de Períodos**: Limita consultas a períodos específicos (7, 15, 30, 60 ou 90 dias)
- **Paginação**: Suporta dois tipos de paginação - por quantidade de registros ou por data
- **Filtros Avançados**: Permite filtros por múltiplos campos com operadores (igual, maior, menor, contém, etc.)
- **Saldo Calculado**: Calcula saldo após cada lançamento baseado no saldo anterior
- **Validação de Conta**: Valida se conta pertence ao CPF/CNPJ informado
- **Suporte Multi-Banco**: Consulta automaticamente em bancos BV (161) e BVSA (436)
- **Comprovantes**: Identifica transações que possuem comprovante disponível
- **Histórico Dual**: Consulta tanto em movimentos do dia quanto em histórico
- **Limite de Registros**: Aplica limite máximo configurável de registros retornados

## 6. Relação entre Entidades

**Principais Entidades:**

- **Movimentacao**: Representa uma movimentação bancária com dados de transação, valores, saldos e datas
- **Transacao**: Contém tipo e descrição da transação
- **Pessoa**: Representa remetente ou favorecido com dados pessoais e bancários
- **Banco**: Informações do banco (código, nome, ISPB, COMPE)
- **ConsultaExtrato**: Parâmetros de consulta de extrato
- **PesquisaExtrato**: Filtros para pesquisa avançada
- **Agendamento**: Dados de agendamentos de transferências
- **Detalhamento**: Detalhes de movimentações SPB/ITP
- **HistoricoDocumento**: Histórico de documentos e estornos

**Relacionamentos:**
- Movimentacao 1:1 Transacao
- Movimentacao N:1 Pessoa (remetente)
- Movimentacao N:1 Pessoa (favorecido)
- Pessoa N:1 Banco
- Movimentacao 0:1 Agendamento (via NSU)
- Movimentacao 0:1 Detalhamento (via número documento)

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbMovimentoDia | tabela | SELECT | Movimentações do dia corrente |
| TbHistoricoMovimento | tabela | SELECT | Histórico de movimentações |
| TbConta | tabela | SELECT | Dados cadastrais de contas |
| TbHistoricoSaldo | tabela | SELECT | Histórico de saldos diários |
| TbAgendamentoContaCorrente | tabela | SELECT | Agendamentos de transferências |
| TbAgendamentoFavorecido | tabela | SELECT | Favorecidos de agendamentos |
| VwContaCorrenteSaldoDia | view | SELECT | View de contas com saldo do dia |
| TbBanco | tabela | SELECT | Cadastro de bancos |
| TBL_CAIXA_ENTRADA_SPB | tabela | SELECT | Detalhamento de transações SPB/ITP |
| TbDetalheBoleto | tabela | SELECT | Detalhes de boletos pagos |
| TbLancamentoBoleto | tabela | SELECT | Lançamentos de boletos |
| TbContaRelacionamento | tabela | SELECT | Relacionamento conta-titularidade |
| TbPessoaTitularidade | tabela | SELECT | Titularidade de pessoas |
| TbPessoa | tabela | SELECT | Cadastro de pessoas |
| TbTransacao | tabela | SELECT | Tipos de transações |

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| openapi.yaml | leitura | resources/swagger | Especificação OpenAPI da API |
| application.yml | leitura | resources | Configurações da aplicação |
| logback-spring.xml | leitura | resources (múltiplos ambientes) | Configuração de logs |
| *.sql | leitura | resources/br/com/votorantim/.../database | Queries SQL para repositórios |

## 10. Filas Lidas

não se aplica

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Sybase ASE (DBCONTACORRENTE) | Banco de Dados | Base principal de movimentações e contas |
| Sybase ASE (DBITP) | Banco de Dados | Base de detalhamento SPB/ITP |
| Sybase ASE (DBGLOBAL) | Banco de Dados | Base global de bancos e pessoas |
| SQL Server (CCBDPagamentoConta) | Banco de Dados | Base de detalhes de boletos |
| OAuth2 JWT Provider | Autenticação | Validação de tokens JWT para segurança |
| Prometheus | Monitoramento | Exportação de métricas |
| Grafana | Monitoramento | Visualização de métricas via dashboards |

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões de camadas (controller, service, repository, domain)
- Uso adequado de padrões de projeto (Repository, Service, Mapper, Validator)
- Separação clara de responsabilidades entre camadas
- Uso de enums para categorização e constantes
- Validações bem organizadas com validators específicos
- Tratamento de exceções estruturado com handlers customizados
- Uso de JDBI para acesso a dados de forma eficiente
- Documentação OpenAPI completa e bem estruturada
- Configuração adequada de múltiplos datasources
- Uso de Lombok para redução de boilerplate

**Pontos de Melhoria:**
- Queries SQL embutidas em arquivos separados (boa prática, mas dificulta manutenção em alguns casos)
- Algumas classes de serviço com múltiplas responsabilidades
- Falta de testes unitários nos arquivos principais (apenas estrutura de testes presente)
- Código com algumas dependências de versões antigas (Spring Boot 2.x)
- Alguns métodos longos que poderiam ser refatorados
- Uso de `AT ISOLATION 0` em queries pode causar problemas de consistência

## 14. Observações Relevantes

- **Multi-tenancy**: Sistema suporta consultas em múltiplos bancos (BV 161 e BVSA 436) automaticamente
- **Performance**: Uso de `READPAST` e `AT ISOLATION 0` para evitar locks em consultas
- **Segurança**: Implementa OAuth2 com JWT para autenticação e autorização
- **Histórico Dual**: Consultas verificam tanto tabela de movimentos do dia quanto histórico
- **Paginação Inteligente**: Suporta paginação por quantidade ou por data, com cálculo automático de última página
- **Categorização Rica**: Mais de 50 categorias de transações incluindo PIX, Open Finance, empréstimos BV
- **Saldo Calculado**: Sistema calcula saldo após cada lançamento baseado em posição anterior
- **Validações Robustas**: Múltiplos validators para garantir integridade dos dados de entrada
- **Monitoramento**: Integração com Prometheus e Grafana para observabilidade
- **Configuração por Ambiente**: Suporte a múltiplos ambientes (local, des, uat, prd) com configurações específicas
- **Limite Configurável**: Limite máximo de registros configurável via properties
- **Escape de Dados**: Uso de StringEscapeUtils para prevenir injection em logs