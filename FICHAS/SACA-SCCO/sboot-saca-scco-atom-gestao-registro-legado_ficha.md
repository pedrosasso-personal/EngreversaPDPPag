---
## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema **sboot-saca-scco-atom-gestao-registro-legado** é um serviço atômico Spring Boot desenvolvido para gerenciar operações relacionadas a boletos e registros legados no contexto do sistema SACA (Sistema de Administração de Contas a Receber) do Banco Votorantim. 

O sistema oferece funcionalidades para:
- Geração de "nosso número" para boletos bancários
- Associação de parcelas a boletos
- Consulta de dados de boletos
- Registro e gravação de histórico no SAC (Sistema de Atendimento ao Cliente)
- Notificação de registro parcial de boletos

O sistema integra-se com bases de dados legadas (Sybase) e implementa regras de negócio específicas para gestão de cobrança bancária, incluindo cálculos de seguro prestamista e geração de dígitos verificadores para diferentes bancos (Banco do Brasil e Banco Votorantim).

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal que inicializa a aplicação Spring Boot |
| **GestaoRegistroLegadoConfiguration** | Configuração de beans do Spring, incluindo JDBI e repositórios |
| **OpenApiConfiguration** | Configuração do Swagger/OpenAPI para documentação da API |
| **AssociarParcelaBoletoController** | Controller REST para associação de parcelas a boletos |
| **ConsultarDadosBoletoController** | Controller REST para consulta de dados de boletos |
| **GerarNossoNumeroController** | Controller REST para geração de nosso número |
| **GestaoRegistroLegadoController** | Controller REST para notificação de registro parcial |
| **GravarHistoricoController** | Controller REST para gravação de histórico |
| **RegistrarHistoricoController** | Controller REST para registro de histórico |
| **AssociarParcelaBoletoService** | Serviço de negócio para associação de parcelas, incluindo cálculo de seguro prestamista |
| **NossoNumeroService** | Serviço de negócio para geração de nosso número com dígito verificador |
| **ConsultarDadosBoletoService** | Serviço de negócio para consulta de boletos |
| **GestaoRegistroLegadoService** | Serviço de negócio para notificação de registro parcial |
| **HistoricoSacService** | Serviço de negócio para operações de histórico SAC |
| **JdbiAssociarParcelaBoletoRepositoryImpl** | Repositório JDBI para operações de associação de parcelas |
| **JdbiConsultarDadosBoletoRepositoryImpl** | Repositório JDBI para consulta de boletos |
| **JdbiGestaoRegistroLegadoRepositoryImpl** | Repositório JDBI para notificação de registro parcial |
| **JdbiHistoricoSacRepositoryImpl** | Repositório JDBI para operações de histórico |
| **JdbiNossoNumeroRepositoryImpl** | Repositório JDBI para operações de nosso número |

### 3. Tecnologias Utilizadas

- **Framework Principal**: Spring Boot 2.x
- **Linguagem**: Java 11
- **Gerenciamento de Dependências**: Maven
- **Acesso a Dados**: JDBI 3.9.1
- **Banco de Dados**: Sybase (jConnect 16.3-SP03-PL07)
- **Documentação API**: Swagger/Springfox 3.0.0
- **Segurança**: Spring Security OAuth2 (Resource Server)
- **Mapeamento de Objetos**: MapStruct 1.4.2
- **Monitoramento**: Spring Boot Actuator, Micrometer Prometheus
- **Logging**: Logback com suporte a JSON
- **Testes**: JUnit 5, Mockito, RestAssured, Pact (Contract Testing)
- **Containerização**: Docker
- **Infraestrutura**: Kubernetes/OpenShift (Google Cloud Platform)
- **Observabilidade**: Prometheus + Grafana

### 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/gerarNossoNumero | GerarNossoNumeroController | Gera o nosso número para um boleto bancário |
| POST | /v1/associar-parcela-boleto | AssociarParcelaBoletoController | Associa parcelas a um boleto |
| GET | /v1/consultarDadosBoleto | ConsultarDadosBoletoController | Consulta dados de um boleto específico |
| PUT | /v1/notificarRegistroParcial | GestaoRegistroLegadoController | Notifica registro parcial de um boleto |
| PUT | /v1/registrarHistorico | RegistrarHistoricoController | Registra histórico no SAC |
| POST | /v1/gravarHistorico | GravarHistoricoController | Grava histórico de operações |

### 5. Principais Regras de Negócio

1. **Geração de Nosso Número**: 
   - Implementa algoritmos específicos para cálculo de dígito verificador para Banco do Brasil (código 001) e Banco Votorantim (código 655)
   - Para BB: usa módulo 11 com fator variável de 2 a 9
   - Para BV: usa módulo 11 com fator de 2 a 9 cíclico

2. **Cálculo de Seguro Prestamista**:
   - Distribui o valor do seguro prestamista proporcionalmente entre as parcelas
   - Calcula o valor por parcela dividindo o total pelo número de parcelas
   - Ajusta a última parcela para compensar diferenças de arredondamento
   - Subtrai o valor do seguro do valor da parcela quando há código de simulação de cobrança

3. **Associação de Parcelas**:
   - Localiza a base de gestão do contrato (DBGESTAOCPC, DBGESTAODCDCG, etc.)
   - Obtém o código do contrato legado
   - Registra o boleto e suas parcelas no sistema legado
   - Valida a existência do contrato nas bases de gestão

4. **Notificação de Registro Parcial**:
   - Atualiza o flag de piloto de registro parcial para contratos relacionados
   - Insere situação de processamento do instrumento de cobrança
   - Atualiza status de controle de remessa quando o código de estado é 2

5. **Registro de Histórico SAC**:
   - Registra mensagem específica para piloto de registro parcial
   - Evita duplicação de registros verificando existência prévia
   - Grava histórico com informações de rotina, ação e mensagem

6. **Normalização de Dados**:
   - Remove acentuação de strings (normalização NFD)
   - Formata valores monetários com 2 casas decimais usando arredondamento HALF_EVEN

### 6. Relação entre Entidades

**Entidades Principais:**

- **BoletoRequest**: Representa um boleto com seus dados bancários
  - Relacionamento 1:N com ParcelaRequest (um boleto possui múltiplas parcelas)
  - Atributos: codigoContaCorrente, numeroContaConvenio, codigoCarteiraBanco, nossoNumero, numeroContrato, valorTitulo, dataVencimento, etc.

- **ParcelaRequest**: Representa uma parcela de um boleto
  - Atributos: numeroParcela, dataVencimento, valorParcela, valorDesconto, valorPrincipal, vrDescontoSeguroPrestamista

- **IdentificacaoBoleto**: Identificação única de um boleto
  - Atributos: codigoNossoNumero, numeroBanco, numeroConvenioCobranca, codigoEstadoProcessamento

- **Historico**: Registro de histórico de operações
  - Atributos: cdVeiculoLegal, nuContratoGestao, sqContratoFinanceiro, dtVencimento, rotina, acao, mensagem

- **NossoNumeroRequest/Response**: Dados para geração e retorno do nosso número
  - Request: numeroContaCorrente, numeroContaConvenio, codigoCarteiraBanco, codigoBanco, codigoAgencia
  - Response: codigoNossoNumero, digitoVerificadorNossoNumero, numeroVariacaoCarteira, codigoContaCorrente

- **ConsultarDadosBoletoRequest/Response**: Dados para consulta de boletos
  - Request: valorTitulo, convenio, nossoNumero
  - Response: dados completos do boleto incluindo beneficiário, pagador, conta corrente, etc.

### 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| DBCOR..TbConexao | tabela | SELECT | Busca informações de conexão e nome do banco de dados |
| DBCOR..TbProduto | tabela | SELECT | Busca informações de produto |
| DBCOR..TbContratoPrincipal | tabela | SELECT | Busca informações do contrato principal |
| [DBGESTAO*]..tbcontrato | tabela | SELECT | Busca número do contrato legado na base de gestão específica |
| DBCARNE..TB_CONTA_CORRENTE | tabela | SELECT | Busca código da conta corrente legada |
| DBCARNE..TB_CARNE_CONTROLE_ENVIO | tabela | SELECT | Busca nosso número e variação de carteira |
| TbRegistroInstrumentoCobranca | tabela | SELECT | Consulta dados completos do boleto |
| SCC_FIN..HIST_COB | tabela | SELECT | Verifica existência de histórico prévio |

### 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| DBCARNE..TB_CARNE_CONTROLE_COBRANCA | tabela | INSERT | Registra novo boleto no sistema de controle de cobrança |
| DBCARNE..TB_CARNE_CONTROLE_COBRANCA | tabela | UPDATE | Atualiza status de controle de remessa |
| DBCARNE..TB_PARCELA_BOLETO | tabela | INSERT | Registra parcelas associadas ao boleto |
| DBCARNE..TB_CARNE_CONTROLE_ENVIO | tabela | UPDATE | Atualiza o nosso número incrementando o contador |
| TbRegistroInstrumentoCobranca | tabela | UPDATE | Atualiza flag de piloto de registro parcial |
| TbSituacaoProcessamentoInsto | tabela | INSERT | Insere nova situação de processamento do instrumento |

### 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot | Arquivo de configuração da aplicação com datasources e profiles |
| logback-spring.xml | leitura | Logback | Configuração de logging em formato JSON |
| *.sql | leitura | JDBI (resources) | Arquivos SQL para queries parametrizadas |
| swagger/sboot-saca-scco-atom-gestao-registro-legado.yaml | leitura | Swagger Codegen | Especificação OpenAPI para geração de interfaces |

### 10. Filas Lidas

não se aplica

### 11. Filas Geradas

não se aplica

### 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Sybase DBCARNE | Banco de Dados | Base de dados legada para controle de carnês e boletos |
| Sybase DBCOR | Banco de Dados | Base de dados corporativa com informações de contratos e produtos |
| Sybase DBGESTAO* | Banco de Dados | Múltiplas bases de gestão de contratos (DBGESTAOCPC, DBGESTAODCDCG, etc.) |
| Sybase SCC_FIN | Banco de Dados | Base de dados financeira com histórico de cobrança |
| API Gateway | OAuth2 | Autenticação e autorização via JWT (jwks.json) |
| Prometheus | Monitoramento | Exportação de métricas da aplicação |

### 13. Avaliação da Qualidade do Código

**Nota: 7.5/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões hexagonais (ports/adapters)
- Separação clara entre camadas (domain, application, common)
- Uso adequado de injeção de dependências e inversão de controle
- Boa cobertura de testes (unitários, integração, funcionais)
- Uso de MapStruct para mapeamento de objetos
- Implementação de transações com anotações Spring
- Documentação OpenAPI/Swagger bem definida
- Configuração adequada de observabilidade (Actuator, Prometheus, Grafana)
- Uso de Lombok para redução de boilerplate

**Pontos de Melhoria:**
- Alguns métodos com lógica de negócio complexa poderiam ser refatorados (ex: cálculo de seguro prestamista)
- Queries SQL embutidas em arquivos separados (boa prática), mas sem documentação sobre o propósito de cada uma
- Falta de tratamento mais granular de exceções em alguns controllers
- Alguns magic numbers no código (ex: códigos de banco "001", "655")
- Validações de parâmetros poderiam usar Bean Validation ao invés de validadores customizados
- Nomenclatura de algumas variáveis em português misturada com inglês
- Falta de constantes para strings repetidas (ex: mensagens de erro, nomes de campos)
- Alguns métodos longos que poderiam ser decompostos para melhor legibilidade

### 14. Observações Relevantes

1. **Ambiente Multi-Profile**: O sistema suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas de datasource e URLs de API Gateway.

2. **Segurança**: Implementa OAuth2 Resource Server com validação de JWT, mas os endpoints do Actuator e Swagger não requerem autenticação.

3. **Banco de Dados Legado**: O sistema integra-se com múltiplas bases Sybase legadas, o que pode representar desafios de manutenção e performance.

4. **Cálculos Financeiros**: Utiliza BigDecimal com RoundingMode.HALF_EVEN para garantir precisão em cálculos monetários.

5. **Piloto de Registro Parcial**: Existe uma funcionalidade específica para um piloto de registro parcial de boletos, indicando uma fase de transição ou teste de nova funcionalidade.

6. **Infraestrutura Cloud**: O sistema está preparado para deploy em Google Cloud Platform usando Kubernetes/OpenShift.

7. **Monitoramento**: Configuração completa de observabilidade com Prometheus e Grafana, incluindo dashboards pré-configurados.

8. **Testes de Contrato**: Implementa Pact para testes de contrato entre consumidores e provedores de API.

9. **Normalização de Dados**: Implementa normalização de strings para remover acentuação, importante para integração com sistemas legados.

10. **Versionamento de API**: Todas as APIs estão sob o path `/v1`, indicando preparação para versionamento futuro.