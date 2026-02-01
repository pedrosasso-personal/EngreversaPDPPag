---
## Ficha Técnica do Sistema

### 1. Descrição Geral
Sistema de gestão de pagamentos e devoluções de transferências bancárias (TED/DOC/Entre-contas) desenvolvido em arquitetura Java EE. O sistema atua como middleware entre canais digitais e sistemas legados (ITP e SPAG), gerenciando solicitações de transferências assíncronas, validações de regras de negócio, controle de grade horária, suporte a operações Fintech e processamento de devoluções TED. Utiliza webservices SOAP para comunicação externa e stored procedures para persistência em bancos de dados Oracle.

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **SolicitarTransferenciaBackendServiceImpl** | WebService SOAP principal - orquestra solicitações de transferência e devolução TED |
| **GestaoDevolucaoBeanImpl** | EJB Stateless - gerencia consultas e solicitações de devolução TED |
| **GestaoPagamentoBeanImpl** | EJB Stateless - processa inclusão de lançamentos de transferência assíncrona (TED/DOC/Entre-contas) |
| **GestaoPagamentoSpagBeanImpl** | EJB Stateless - processa lançamentos para banco 413 (SPAG) com verificação de migração de participantes |
| **GestaoDevolucaoDaoImpl** | DAO - consulta movimentações e lançamentos TED para devolução |
| **GestaoDevolucaoPgftDaoImpl** | DAO - executa stored procedures de devolução TED e consulta motivos parametrizados |
| **GestaoPagamentoDaoImpl** | DAO - inclusão de lançamentos TED/DOC/Entre-contas com strategy pattern para Fintech |
| **GestaoPagamentoSpagDaoImpl** | DAO - inclusão de lançamentos SPAG e verificação de migração de participantes |
| **GestaoGradeHorariaItpDaoImpl** | DAO - validação de janela operacional TED com tolerância de 25 minutos |
| **ValidateRequest** | Validador - valida campos de requisição de transferência (CPF/CNPJ, contas, valores, grade horária) |
| **ValidateDevolucao** | Validador - valida regras de negócio para devolução TED |
| **ValidateFintech** | Validador - valida operações Fintech (status ativo, conta cadastrada, tipo conta) |
| **EStrategyIncluirLancamento** | Strategy pattern - define estratégias de inclusão por tipo de liquidação (ENTRE_CONTAS, TED, BOLETO) |
| **HttpClientIntegration** | Cliente HTTP - integração com APIs internas (OAuth2, proxy, retry) |
| **FeatureToggleService** | Serviço - consulta features dinâmicas (ex: validação NSU obrigatória) |

### 3. Tecnologias Utilizadas

- **Java EE 7**: EJB 3.1, CDI, JAX-WS (SOAP), JAXB
- **Spring Framework**: Spring JDBC (NamedParameterJdbcTemplate, StoredProcedure)
- **Segurança**: JAAS (roles "intr-middleware"), OAuth2, WasAlias (credenciais), SSL/TLS
- **Banco de Dados**: Oracle (DBPGF_TES, DBISPB, DBSPAG)
- **Servidor de Aplicação**: IBM WebSphere Application Server
- **Integração HTTP**: Apache HttpClient 4.x
- **Logging**: SLF4J
- **Testes**: JUnit 4, Mockito, PowerMock
- **Proxy**: mor-isa:8080
- **Datasources JNDI**: jdbc/sitpBaseDbItpDS, jdbc/spagBaseDBSPAGDS

### 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/consultaContaUsuarioFintech | ConsultarContaFintechIntegrationServiceImpl | Consulta conta de usuário Fintech |
| GET | /cadastro/v1/produto/feature/{feature} | ItpAtomIntegrarPagamentoIntegrationServiceImpl | Consulta feature toggle (ex: ft_boolean_atacado_integrar_pagamento_valida_nsu) |

**Endpoints SOAP:**

| Operação | Classe | Descrição |
|----------|--------|-----------|
| solicitarTransferenciaTED | SolicitarTransferenciaBackendServiceImpl | Solicita transferência TED/DOC/Entre-contas |
| solicitarDevolucaoTED | SolicitarTransferenciaBackendServiceImpl | Solicita devolução de TED recebido |

### 5. Principais Regras de Negócio

1. **Validação de Transferências:**
   - CPF/CNPJ remetente e favorecido devem ser válidos (dígito verificador)
   - Tipo de conta não pode ser "CI" (Conta de Investimento)
   - Bancos permitidos: 161, 413, 655
   - Códigos de liquidação: 31 (TED-CIP), 32 (TED-STR), 21 (DOC), 1 (Entre Contas)
   - Valores >= R$ 250.000,00 exigem dados completos do favorecido
   - TED entre mesmos bancos proibido, exceto banco 161
   - Validação de grade horária para TED-STR (código 32)
   - NSU (numeroProtocoloSolicitacaoCliente) pode ser obrigatório via feature toggle

2. **Regras Fintech:**
   - Status Fintech deve estar ativo
   - Conta remetente deve estar cadastrada com CP1
   - DOC não permitido para Fintech
   - Tipo de conta "PG" (Pagamento) obrigatório para TED Fintech
   - Banco deve ser 655 (Banco Votorantim)
   - Validação de grade horária específica

3. **Regras de Devolução TED:**
   - Código de liquidação deve ser 31 ou 32 (TED)
   - Status do lançamento deve ser "confirmado"
   - Não permite devolução de devolução
   - Motivo de devolução deve estar parametrizado
   - CPF/CNPJ do favorecido deve ser válido

4. **Roteamento de Lançamentos:**
   - Banco 413 → Sistema SPAG
   - Demais bancos → Sistema ITP
   - Verificação de migração de participante para SPAG

5. **Grade Horária TED:**
   - Janela operacional com tolerância de 25 minutos
   - Consulta parâmetros em TbParametroCamaraLiquidacao

6. **Validação de Protocolo:**
   - Verifica duplicidade de protocolo cliente antes de inclusão
   - Tratamento especial para caracteres BACEN/CIP

7. **Auditoria:**
   - Trilha de auditoria obrigatória em todas as operações
   - Histórico auto-gerado para usuário "NEON"

### 6. Relação entre Entidades

**Entidades Principais:**

- **Transferencia**: Entidade central contendo 115+ atributos (remetente, favorecido, valores, datas, tributos, boleto, Fintech, auditoria)
  - Relaciona-se com **Remetente** (1:1)
  - Relaciona-se com **Favorecido** (1:1)
  - Relaciona-se com **FintechOb** (0:1) - dados específicos Fintech
  - Relaciona-se com **AuditoriaInfo** (1:1) - trilha de auditoria

- **Lancamento**: Representa lançamento no sistema SPAG
  - Relaciona-se com **LancamentoPessoa** (1:N)
  - Relaciona-se com **ControleMigracaoParticipante** (N:1)

- **MovimentacaoRecuperada**: Representa movimentação TED para devolução
  - Relaciona-se com **MotivoDevolucao** (N:1)

- **ParametrosCamaraLiquidacao**: Parâmetros de grade horária
  - Utilizado para validação de janela operacional

**Relacionamentos:**
- Transferencia → FintechOb (opcional, quando operação Fintech)
- Lancamento → ControleMigracaoParticipante (verifica se participante migrado para SPAG)
- MovimentacaoRecuperada → MotivoDevolucao (motivo parametrizado)

### 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TBL_CAIXA_ENTRADA_SPB | Tabela | SELECT | Consulta movimentações TED/DOC para devolução e verificação de protocolo duplicado (DBPGF_TES) |
| TBL_LANCAMENTO | Tabela | SELECT | Consulta lançamentos TED via stored procedure BV_LANCAMENTO_CAIXA_ENTRADA (DBPGF_TES) |
| sp_se_tb_doat_079 | Stored Procedure | SELECT | Consulta motivos de devolução parametrizados (DBPGF_TES) |
| TbLancamento | Tabela | SELECT | Consulta lançamentos SPAG e verificação de protocolo duplicado (DBSPAG) |
| TbLancamentoPessoa | Tabela | SELECT | Consulta pessoas relacionadas a lançamentos SPAG (DBSPAG) |
| TbControleMigracaoParticipante | Tabela | SELECT | Verifica se participante foi migrado para SPAG (DBSPAG) |
| TbParametroCamaraLiquidacao | Tabela | SELECT | Consulta parâmetros de grade horária TED (DBPGF_TES) |

### 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TBL_CAIXA_ENTRADA_SPB | Tabela | INSERT | Inclusão de lançamentos TED/DOC/Entre-contas via stored procedures BV_INCLUSAO_CAIXA_ENTRADA e PrIncluirCaixaEntProtCliCtrl (DBPGF_TES) |
| TBL_LANCAMENTO | Tabela | UPDATE | Solicitação de devolução TED via stored procedure solicitarDevolucaoTedPGFT (DBPGF_TES) |
| TbLancamento | Tabela | INSERT | Inclusão de lançamentos SPAG via stored procedure PrIncluirLancamento (DBSPAG) |

### 9. Arquivos Lidos e Gravados

não se aplica

### 10. Filas Lidas

não se aplica

### 11. Filas Geradas

não se aplica

### 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **API Consulta Conta Fintech** | REST (POST) | Consulta dados de conta de usuário Fintech - endpoint /v1/consultaContaUsuarioFintech |
| **API Feature Toggle (Atom)** | REST (GET) | Consulta features dinâmicas - endpoint /cadastro/v1/produto/feature/{feature} - controla validação NSU obrigatória |
| **Sistema ITP (DBPGF_TES)** | Stored Procedures | Sistema legado de transferências - stored procedures BV_INCLUSAO_CAIXA_ENTRADA, BV_LANCAMENTO_CAIXA_ENTRADA, solicitarDevolucaoTedPGFT |
| **Sistema SPAG (DBSPAG)** | Stored Procedures | Sistema de pagamentos banco 413 - stored procedure PrIncluirLancamento |
| **Proxy mor-isa:8080** | HTTP Proxy | Proxy corporativo para integrações HTTP |
| **OAuth2 Server** | Autenticação | Servidor OAuth2 para obtenção de access tokens (retry em 401 Unauthorized) |

### 13. Avaliação da Qualidade do Código

**Nota:** 8/10

**Justificativa:**

**Pontos Positivos:**
- **Arquitetura bem estruturada**: Separação clara de camadas (WebService → EJB Business → DAO → Stored Procedures)
- **Padrões de projeto**: Uso adequado de Strategy Pattern (EStrategyIncluirLancamento), DAO Pattern, validadores especializados
- **Validações extensivas**: Múltiplas camadas de validação (ValidateRequest, ValidateDevolucao, ValidateFintech, ValidateCPF/CNPJ)
- **Tratamento de exceções**: Exceções customizadas (NegocioException, PagamentoException) com códigos de erro padronizados (ENUM_RETURN_CODE)
- **Logging adequado**: Uso consistente de SLF4J em todas as camadas
- **Cobertura de testes**: Testes unitários com Mockito/PowerMock para classes críticas
- **Flexibilidade**: Feature toggles para controle dinâmico de comportamento (ex: validação NSU)
- **Segurança**: JAAS roles, OAuth2, SSL/TLS, WasAlias para credenciais

**Pontos de Melhoria:**
- **Complexidade de Transferencia**: Classe com 115+ atributos, poderia ser decomposta em objetos menores
- **Acoplamento a Stored Procedures**: Lógica de negócio distribuída entre Java e banco de dados dificulta manutenção
- **Documentação**: Falta JavaDoc em algumas classes críticas
- **Hardcoded values**: Alguns valores fixos (ex: banco 655, proxy mor-isa:8080) poderiam ser externalizados
- **Tratamento de caracteres BACEN/CIP**: Lógica específica poderia ser melhor documentada

### 14. Observações Relevantes

1. **Arquitetura Híbrida**: Sistema integra dois bancos de dados legados distintos (ITP e SPAG) com roteamento baseado em código de banco (413 → SPAG, demais → ITP)

2. **Migração SPAG**: Sistema verifica se participante foi migrado para SPAG através de TbControleMigracaoParticipante, retornando protocolo apropriado

3. **Suporte Fintech**: Implementação específica para operações Fintech com validações adicionais e estratégias de liquidação diferenciadas

4. **Grade Horária**: Validação de janela operacional TED com tolerância de 25 minutos, crítica para operações STR (código 32)

5. **Protocolo Cliente**: Sistema controla duplicidade de NSU (numeroProtocoloSolicitacaoCliente) com possibilidade de tornar obrigatório via feature toggle

6. **Histórico Automático**: Para usuário "NEON", o sistema gera automaticamente o histórico da operação

7. **Devolução TED**: Regras específicas impedem devolução de devolução e exigem motivo parametrizado

8. **Tipos de Transferência Suportados**: TED (CIP/STR), DOC, Entre-contas, DARF, GPS, Boleto, Portabilidade

9. **Retry Mechanism**: Cliente HTTP implementa retry automático em caso de 401 Unauthorized (renovação de token OAuth2)

10. **Datasources JNDI**: Sistema utiliza dois datasources distintos (jdbc/sitpBaseDbItpDS para ITP, jdbc/spagBaseDBSPAGDS para SPAG)

11. **Webservices SOAP**: Contratos definidos em XSD/WSDL com handlers customizados para fault e trilha de auditoria

12. **Deployment WebSphere**: Configurações específicas para IBM WebSphere com virtual hosts e autenticação BASIC