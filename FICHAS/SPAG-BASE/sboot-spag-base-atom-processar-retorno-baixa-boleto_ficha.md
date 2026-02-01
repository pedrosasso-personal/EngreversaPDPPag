# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema responsável por processar retornos de baixa de boletos, atuando como intermediário entre os sistemas SPAG (Sistema de Pagamentos) e PGFT (Plataforma de Gestão Financeira e Tesouraria). O sistema gerencia o ciclo de vida completo de baixas de boletos, incluindo consultas, atualizações, devoluções e cancelamentos, integrando-se com a CIP (Câmara Interbancária de Pagamentos) para processamento de transações bancárias.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `ProcessarRetornoBaixaBoletoService` | Serviço principal contendo toda a lógica de negócio para processamento de baixas de boletos |
| `ProcessarRetornoBaixaBoletoApiDelegateImpl` | Controlador REST que expõe os endpoints da API |
| `JdbiSpagRepository` / `JdbiPgftRepository` | Interfaces de acesso aos bancos de dados SPAG e PGFT usando JDBI |
| `DatabaseConfiguration` | Configuração de múltiplos datasources (SPAG e PGFT) |
| `TransacaoPagamentoMapper` | Mapeamento de transações de pagamento para devoluções |
| `BaixaBoleto`, `DadosBoleto`, `TransacaoPagamento` | Entidades de domínio representando boletos e transações |
| `ProcessarRetornoBaixaBoletoMapper` | Mapeamento entre objetos de domínio e representações REST (MapStruct) |
| Diversos RowMappers | Mapeamento de ResultSets JDBC para objetos de domínio |

## 3. Tecnologias Utilizadas

- **Framework**: Spring Boot 2.7.4
- **Linguagem**: Java 11
- **Persistência**: JDBI 3.10.0 (SQL Object API)
- **Bancos de Dados**: 
  - Microsoft SQL Server (SPAG) - Driver 7.4.0.jre11
  - Sybase ASE (PGFT) - Driver 16.3-SP03-PL07
- **Mapeamento**: MapStruct (via parent POM)
- **Documentação API**: OpenAPI 3.0 / Swagger
- **Segurança**: Spring Security OAuth2 Resource Server (JWT)
- **Build**: Maven 3.8+
- **Gerenciamento de Dependências**: Atlante Base Parent POM 2.7.4
- **Utilitários**: Lombok, Apache Commons Text 1.10.0
- **Servidor**: Tomcat Embed 9.0.108

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/cancelamentoBaixaDestinataria` | ProcessarRetornoBaixaBoletoApiDelegateImpl | Cancela baixa de boleto pela destinatária |
| GET | `/v1/obterBoletoSPAG/{cdLancamento}` | ProcessarRetornoBaixaBoletoApiDelegateImpl | Obtém dados do boleto no sistema SPAG |
| PUT | `/v1/atualizarBaixaBoletoSPAG` | ProcessarRetornoBaixaBoletoApiDelegateImpl | Atualiza status de baixa do boleto no SPAG |
| GET | `/v1/obterBoletoPGFT/{cdLancamento}` | ProcessarRetornoBaixaBoletoApiDelegateImpl | Obtém dados do boleto no sistema PGFT |
| PUT | `/v1/atualizarBaixaBoletoPGFT` | ProcessarRetornoBaixaBoletoApiDelegateImpl | Atualiza status de baixa do boleto no PGFT |
| POST | `/v1/incluirRetornoBaixaBoletoSPAG` | ProcessarRetornoBaixaBoletoApiDelegateImpl | Registra retorno de solicitação de baixa no SPAG |
| POST | `/v1/incluirRetornoBaixaBoletoPGFT` | ProcessarRetornoBaixaBoletoApiDelegateImpl | Registra retorno de solicitação de baixa no PGFT |
| POST | `/v1/incluirEnvioBaixaBoletoSPAG` | ProcessarRetornoBaixaBoletoApiDelegateImpl | Registra envio de solicitação de baixa no SPAG |
| POST | `/v1/incluirDevolucaoSPAG` | ProcessarRetornoBaixaBoletoApiDelegateImpl | Cria transação de devolução no SPAG |
| POST | `/v1/incluirDevolucaoITP` | ProcessarRetornoBaixaBoletoApiDelegateImpl | Cria transação de devolução no ITP (PGFT) |
| PUT | `/v1/numero-identificacao-titulo` | ProcessarRetornoBaixaBoletoApiDelegateImpl | Atualiza número de identificação do título CIP |
| GET | `/v1/obterPagamentoBoletoSPAG/identificacaoBaixa/{numIdentcBaixa}` | ProcessarRetornoBaixaBoletoApiDelegateImpl | Obtém boleto por identificação de baixa no SPAG |
| GET | `/v1/obterPagamentoBoletoSPAG/lancamento/{cdLancamento}` | ProcessarRetornoBaixaBoletoApiDelegateImpl | Obtém boleto por código de lançamento no SPAG |
| GET | `/v1/obterPagamentoBoletoPGFT/identificacaoBaixa/{numIdentcBaixa}` | ProcessarRetornoBaixaBoletoApiDelegateImpl | Obtém boleto por identificação de baixa no PGFT |
| GET | `/v1/obterPagamentoBoletoPGFT/lancamento/{cdLancamento}` | ProcessarRetornoBaixaBoletoApiDelegateImpl | Obtém boleto por código de lançamento no PGFT |
| PUT | `/v1/spag/devolucao-boleto` | ProcessarRetornoBaixaBoletoApiDelegateImpl | Atualiza pagamento devolvido no SPAG |

## 5. Principais Regras de Negócio

1. **Processamento de Baixa de Boletos**: Sistema processa baixas de boletos tanto no SPAG quanto no PGFT, mantendo sincronização entre os sistemas
2. **Validação de NSU**: Verifica duplicidade de NSU (Número Sequencial Único) antes de processar devoluções ITP
3. **Devolução de Pagamentos**: Cria automaticamente transações de devolução invertendo remetente/favorecido e ajustando códigos de transação
4. **Tratamento de Bancos BV/BVSA**: Lógica específica para identificar e tratar transações dos bancos Votorantim (código 655/161) e BV S/A (código 413)
5. **Cancelamento de Baixa**: Busca baixa primeiro no PGFT, depois no SPAG, e cria devolução automaticamente (exceto para Banco BV código 655)
6. **Integração CIP**: Atualiza registros de pagamento CIP com números de referência e controle DDA
7. **Gestão de Status**: Controla status de lançamentos (0=Incluído, 7=Aguardando Processamento, 3=Processado)
8. **Suporte a Fintech**: Trata participantes fintech separadamente nas transações
9. **Tratamento de Erros Duplicados**: Ignora erros de chave duplicada em inserções de retorno PGFT
10. **Validação de Sucesso de Baixa**: Verifica se baixa foi processada com sucesso através de mensagem "Processamento OK"

## 6. Relação entre Entidades

**Entidades Principais:**

- **BaixaBoleto**: Representa uma baixa operacional de boleto (cdTituloBaixaOperacional, cdTituloPagamento, linhaDigitavel, flBaixaEmContingencia)
- **DadosBoleto**: Dados completos do boleto incluindo status, mensagens CIP e referências
- **TransacaoPagamento**: Transação completa de pagamento com remetente, favorecido e dados financeiros
- **TransacaoPagamentoITP**: Transação específica para o sistema ITP/PGFT
- **BoletoResumido**: Visão resumida do boleto com participantes e valores
- **Participante**: Dados de pessoa (física/jurídica) envolvida na transação (banco, agência, conta, CPF/CNPJ)
- **EnvioBaixaBoleto**: Registro de envio de solicitação de baixa para CIP
- **ErroBoletoSpag**: Erros de processamento de boletos no SPAG

**Relacionamentos:**
- BaixaBoleto → TransacaoPagamento (1:1 via cdTituloBaixaOperacional)
- DadosBoleto → RegistroPagamentoCIP (1:1)
- TransacaoPagamento → Participante (remetente, favorecido, remetenteFintech, favorecidoFintech)
- BoletoResumido → Participante (remetente, remetenteFintech)

## 7. Estruturas de Banco de Dados Lidas

### SPAG (SQL Server):

| Nome da Tabela/View | Tipo | Operação | Breve Descrição |
|---------------------|------|----------|-----------------|
| TbLancamento | tabela | SELECT | Lançamentos de pagamentos/boletos |
| TbRegistroPagamentoCIP | tabela | SELECT | Registros de pagamento enviados para CIP |
| TbRetornoBaixaOperacionalCIP | tabela | SELECT | Retornos de baixa operacional da CIP |
| TbLancamentoPessoa | tabela | SELECT | Dados de pessoas envolvidas nos lançamentos |
| TbLancamentoClienteFintech | tabela | SELECT | Dados de clientes fintech nos lançamentos |

### PGFT (Sybase):

| Nome da Tabela/View | Tipo | Operação | Breve Descrição |
|---------------------|------|----------|-----------------|
| DBPGF_TES..TBL_LANCAMENTO | tabela | SELECT | Lançamentos de pagamentos no PGFT |
| DBPGF_TES..TbRegistroPagamentoCIP | tabela | SELECT | Registros de pagamento CIP no PGFT |
| DBPGF_TES..TbRetornoBaixaOperacionalCIP | tabela | SELECT | Retornos de baixa operacional CIP no PGFT |
| DBITP..TBL_CAIXA_ENTRADA_SPB | tabela | SELECT | Caixa de entrada SPB/ITP |
| DBITP..TBL_CAIXA_ENTRADA_SPB | tabela | SELECT | Verificação de NSU existente |

## 8. Estruturas de Banco de Dados Atualizadas

### SPAG (SQL Server):

| Nome da Tabela/View | Tipo | Operação | Breve Descrição |
|---------------------|------|----------|-----------------|
| TbLancamento | tabela | UPDATE | Atualiza flag de baixa CIP e número título CIP |
| TbLancamento | tabela | UPDATE | Atualiza devolução de boleto (código, data, protocolo) |
| TbRegistroPagamentoCIP | tabela | INSERT | Insere registro de envio de baixa para CIP |
| TbRetornoBaixaOperacionalCIP | tabela | INSERT | Insere retorno de solicitação de baixa |
| TbErroProcessamento | tabela | INSERT | Insere erros de processamento de boletos |
| TbLancamento | tabela | INSERT | Insere nova transação via procedure PrIncluirLancamentoV2 |

### PGFT (Sybase):

| Nome da Tabela/View | Tipo | Operação | Breve Descrição |
|---------------------|------|----------|-----------------|
| DBPGF_TES..TBL_LANCAMENTO | tabela | UPDATE | Atualiza flag de baixa boleto CIP |
| DBPGF_TES..tbl_lancamento | tabela | UPDATE | Atualiza devolução de boleto (código, data, login, protocolo) |
| DBPGF_TES..TbRegistroPagamentoCIP | tabela | UPDATE | Atualiza número de referência e controle DDA |
| DBPGF_TES..TbRetornoBaixaOperacionalCIP | tabela | INSERT | Insere retorno de solicitação de baixa |
| DBITP..TBL_CAIXA_ENTRADA_SPB | tabela | INSERT | Insere entrada de caixa via procedure PrIncluirCaixaEntProtCliCtrl |
| DBITP..TBL_CAIXA_ENTRADA_SPB | tabela | UPDATE | Atualiza número de título CIP |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| openapi.yaml | leitura | src/main/resources/swagger/ | Especificação OpenAPI para geração de código |
| application.yml | leitura | src/main/resources/ | Configurações da aplicação por perfil |
| application-local.yml | leitura | src/main/resources/ | Configurações específicas para ambiente local |
| *.sql | leitura | src/main/resources/.../database/ | Queries SQL para operações de banco de dados |
| logback-spring.xml | leitura | src/main/resources/ | Configuração de logs |

## 10. Filas Lidas

não se aplica

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

1. **CIP (Câmara Interbancária de Pagamentos)**: Sistema externo para processamento de baixas operacionais de boletos e pagamentos interbancários
2. **Sistema SPAG**: Sistema de Pagamentos interno do banco (SQL Server)
3. **Sistema PGFT**: Plataforma de Gestão Financeira e Tesouraria (Sybase)
4. **Sistema ITP**: Sistema de processamento de transações (integrado ao PGFT)
5. **OAuth2 Resource Server**: Servidor de autenticação JWT para segurança dos endpoints

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com camadas bem definidas (rest, service, repository, domain)
- Uso adequado de padrões como Repository, Mapper e DTO/Representation
- Configuração de múltiplos datasources bem estruturada
- Uso de JDBI com SQL externalizado em arquivos .sql (facilita manutenção)
- Documentação OpenAPI completa
- Uso de Lombok reduzindo boilerplate
- Tratamento de exceções específicas (duplicação de chave)

**Pontos de Melhoria:**
- Lógica de negócio muito concentrada na classe de serviço (método `cancelarBaixaBoleto` com múltiplas responsabilidades)
- Falta de tratamento de exceções mais robusto em vários métodos
- Logs com informações sensíveis mesmo usando `SecureLogUtil` (CPF/CNPJ em alguns lugares)
- Queries SQL complexas misturando lógica de negócio (CASE WHEN para verificar sucesso)
- Falta de testes unitários incluídos na análise
- Alguns métodos muito longos (ex: `TransacaoPagamentoMapper.paraDevolucao`)
- Uso de nulls em vez de Optional em alguns retornos
- Comentários escassos no código
- Hardcoded strings em vários lugares (ex: "sboot-spag-base-atom-processar-retorno-baixa-boleto")

## 14. Observações Relevantes

1. **Arquitetura Multi-Database**: Sistema trabalha simultaneamente com dois bancos de dados diferentes (SQL Server e Sybase), exigindo gerenciamento cuidadoso de transações
2. **Modelo Atômico**: Segue padrão de microserviços atômicos do Banco Votorantim (Atlante)
3. **Segurança**: Todos os endpoints protegidos por JWT OAuth2, exceto endpoints públicos e documentação
4. **Versionamento de API**: Endpoints versionados com prefixo `/v1/`
5. **Monitoramento**: Exposição de métricas via Actuator e Prometheus na porta 9090
6. **Ambientes**: Suporte a múltiplos ambientes (local, des, uat, prd) com configurações específicas
7. **Procedures**: Utiliza stored procedures do banco para inserção de transações (`PrIncluirLancamentoV2`, `PrIncluirCaixaEntProtCliCtrl`)
8. **Contingência**: Sistema trata cenários de baixa em contingência
9. **Histórico**: Mantém histórico de 10 dias para consultas de boletos
10. **Fintech**: Suporte específico para operações envolvendo clientes fintech