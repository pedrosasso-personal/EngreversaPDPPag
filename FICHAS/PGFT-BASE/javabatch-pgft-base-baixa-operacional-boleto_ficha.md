# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java responsável por realizar a baixa operacional de boletos de pagamento registrados na CIP (Câmara Interbancária de Pagamentos). O sistema processa lançamentos de pagamento de boletos, consulta informações na CIP, valida regras de negócio e efetiva a baixa operacional, podendo operar em modo normal ou contingência.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê lançamentos de boletos a serem processados do banco de dados |
| **ItemProcessor** | Processa cada lançamento, consultando dados do boleto na CIP quando necessário |
| **ItemWriter** | Efetiva a baixa operacional do boleto, gravando registros no banco |
| **BaixaOperacionalServiceImpl** | Orquestra o processo de baixa operacional (normal ou contingência) |
| **ControlarOperacoesCipImpl** | Controla operações de integração com a CIP para baixa operacional |
| **ControlarOperacoesCipUtilImpl** | Utilitários para montagem de dados e validações de baixa operacional |
| **DaoBoletosBaixaOperacionalImpl** | Acesso a dados de boletos para baixa operacional |
| **DbPgfTesDAOImpl** | DAO genérico para operações no banco DBPGF_TES |
| **ConsultarBoletoPagamentoConsumer** | Cliente REST para consulta de boletos |
| **BaixarBoletoPagamentoConsumer** | Cliente REST para solicitação de baixa de boletos |
| **ClientePagamentoBusinessConsumer** | Cliente SOAP para obtenção de dados de boleto (serviço de negócio) |
| **ClientePagamentoIntegrationConsumer** | Cliente SOAP para confirmação/cancelamento de baixa (serviço de integração) |

## 3. Tecnologias Utilizadas

- **Framework**: Spring Framework 2.0, Spring Batch (BV Framework Batch)
- **Linguagem**: Java
- **Build**: Maven
- **Banco de Dados**: Sybase ASE (via JDBC)
- **Web Services**: JAX-WS (SOAP), REST (Apache HttpClient)
- **Segurança**: WS-Security (UsernameToken), BouncyCastle (TLS 1.2)
- **Serialização**: GSON, Jackson
- **Logging**: Log4j, BVLogger
- **Testes**: JUnit, Mockito

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | /v1/boleto/removerCacheBoleto/{codigoBarra} | ConsultarBoletoPagamentoApi | Remove cache de um boleto específico |
| GET | /v1/boleto/removerTodosCacheBoleto | ConsultarBoletoPagamentoApi | Remove todos os caches de boletos |
| GET | /v1/boleto/{codigoBarra} | ConsultarBoletoPagamentoApi | Consulta dados de um boleto |
| POST | /v1/solicitarBaixaBoleto | BaixarBoletoPagamentoApi | Solicita baixa operacional de boleto |

## 5. Principais Regras de Negócio

- **Seleção de Lançamentos**: Seleciona lançamentos de boletos a baixar por data de processamento
- **Consulta CIP**: Consulta dados do boleto na CIP quando não disponíveis localmente
- **Validação de Tipo de Baixa**: Determina tipo de baixa (integral/parcial, intra/interbancária) baseado em:
  - Código de espécie do título
  - Banco remetente vs recebedor
  - Valor pago vs valor do título
  - Histórico de pagamentos parciais
- **Modo Contingência**: Habilita baixa em contingência quando:
  - Flag de contingência CIP está ativa
  - Valor do boleto está dentro dos limites configurados (mínimo e máximo)
- **Tratamento de Remetente**: Identifica se remetente é BV S.A. (banco 413) ou outro banco (655)
- **Agregador Fintech**: Identifica e trata dados de agregador para pagamentos via fintech
- **Conversão Linha Digitável**: Converte linha digitável em código de barras
- **Validação Boleto Vencido**: Verifica vencimento para determinar tipo de baixa
- **Tratamento Caracteres Especiais**: Remove caracteres especiais de nomes (limite 50 caracteres)

## 6. Relação entre Entidades

**LancamentoVO**: Representa um lançamento de pagamento de boleto
- Relaciona-se com **ClienteVO** (remetente)
- Contém **ConsultaBoletoPagamentoVO** (dados do boleto)

**ClienteVO**: Representa cliente/remetente
- Herda de **PessoaVO**
- Contém **ContaVO** (dados bancários)

**BoletosBaixaOperacionalVo**: Agrupa dados para baixa operacional
- Contém **LancamentoVO**
- Contém **BoletoPagamentoCompletoVO**

**BoletoPagamentoCompletoVO**: Dados completos do boleto
- Contém **BoletoPagamentoVO** (dados básicos)
- Contém listas de **BaixaTituloVO** (baixas anteriores)
- Contém listas de **BaixaEfetivaVO** (baixas efetivas)
- Contém listas de **TituloVO** (juros, multa, desconto)

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TBL_LANCAMENTO | Tabela | SELECT | Lançamentos de pagamento de boletos |
| TbProcessamentoRoboPGFT | Tabela | SELECT | Controle de processamento do robô |
| TbRetornoConsultaTitulo | Tabela | SELECT | Retorno de consultas de títulos na CIP |
| TbBaixaOperacionalTitulo | Tabela | SELECT | Histórico de baixas operacionais |
| TbParametroInterfaceCIP | Tabela | SELECT | Parâmetros de contingência CIP |
| DBITP..TBL_CAIXA_ENTRADA_SPB | Tabela | SELECT | Caixa de entrada SPB (para atualização) |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TBL_LANCAMENTO | Tabela | UPDATE | Atualiza flag de baixa do boleto |
| TbRegistroPagamentoCIP | Tabela | INSERT | Registra envio de baixa operacional para CIP |
| TbRetornoBaixaOperacionalCIP | Tabela | INSERT | Registra retorno de baixa operacional da CIP |
| DBITP..TBL_CAIXA_ENTRADA_SPB | Tabela | UPDATE | Atualiza número do título CIP |
| TbRegistroPagamentoCIP | Tabela | DELETE | Remove solicitação de baixa em caso de erro |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| obterBoletoCIP.properties | Leitura | ConsultarBoletoPagamentoFactory, BaixarBoletoPagamentoFactory | Configurações de endpoints e credenciais |
| log4j.xml | Leitura | Framework Log4j | Configuração de logging |
| job-definitions.xml | Leitura | Spring Framework | Definição do job batch |
| job-resources.xml | Leitura | Spring Framework | Recursos (datasources) do job |
| robo.log | Gravação | Log4j RollingFileAppender | Log de execução do robô |
| statistics-{executionId}.log | Gravação | BvDailyRollingFileAppender | Estatísticas de execução |

## 10. Filas Lidas

não se aplica

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

**Web Services SOAP:**
- **BoletoPagamentoBusinessService**: Obtenção de dados de boleto (consulta CIP)
  - Endpoint: https://servicebus.bvnet.bv/varejo/ProdServicoCobrancaRecuperacao/boletoPagamentoBusinessService/v1
  - Operação: obterBoletoPagamento
  - Autenticação: WS-Security UsernameToken

- **BoletoPagamentoIntegrationService**: Confirmação/cancelamento de baixa
  - Endpoint: https://servicebus.bvnet.bv/varejo/ProdServicoCobrancaRecuperacao/boletoPagamentoIntegrationService/v1
  - Operações: confirmarBoletoPagamento, cancelarBoletoPagamento
  - Autenticação: WS-Security UsernameToken

**APIs REST:**
- **springboot-spag-base-consulta-boleto**: Consulta e remoção de cache de boletos
  - Endpoints: /v1/boleto/{codigoBarra}, /v1/boleto/removerCacheBoleto/{codigoBarra}
  - Autenticação: HTTP Basic Auth

- **sboot-spbb-base-atom-dda-router**: Solicitação de baixa de boleto
  - Endpoint: /v1/solicitarBaixaBoleto
  - Autenticação: HTTP Basic Auth

## 13. Avaliação da Qualidade do Código

**Nota:** 6/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades em camadas (batch, business, dao, util)
- Uso de padrões de projeto (Factory, Consumer)
- Tratamento de exceções presente
- Testes unitários implementados (cobertura razoável)
- Uso de frameworks consolidados (Spring, BV Framework)

**Pontos Negativos:**
- Código legado com comentários em português e encoding ISO-8859-1
- Muitos comentários "TODO" e código comentado
- Classes com múltiplas responsabilidades (ex: ControlarOperacoesCipUtilImpl com 500+ linhas)
- Lógica de negócio complexa sem documentação adequada
- Hardcoded values (ISPBs, códigos de banco)
- Tratamento de exceções genérico em vários pontos
- Falta de validação de entrada em alguns métodos
- Uso de reflection e Whitebox em testes (code smell)
- Dependências de versões antigas (Spring 2.0, Sybase JDBC)
- Configurações sensíveis em arquivos de propriedades (senhas)

## 14. Observações Relevantes

- Sistema crítico para operação de pagamentos de boletos
- Suporta múltiplos ambientes (DES, QA, UAT, PRD) via WSDLs específicos
- Implementa mecanismo de contingência para operação offline da CIP
- Utiliza criptografia BVCrypto para senhas em arquivos de configuração
- Configurado para TLS 1.2 com BouncyCastle
- Job batch configurado para execução via linha de comando
- Parâmetro obrigatório: dataprocessamento (formato yyyyMMdd)
- Integração com múltiplos bancos de dados Sybase (DBPGF_TES, DBITP)
- Sistema preparado para rollback em caso de erro (método voltaLancamento)
- Suporte a diferentes tipos de baixa operacional (13 tipos mapeados)
- Tratamento especial para boletos VR (valor >= R$ 250.000,00)
- Identificação de origem do pagamento (API Pagamentos, Fintech, etc)