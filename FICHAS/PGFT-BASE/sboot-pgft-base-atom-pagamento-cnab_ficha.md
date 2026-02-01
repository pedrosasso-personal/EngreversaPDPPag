---
## Ficha Técnica do Sistema

### 1. Descrição Geral
Sistema responsável pelo processamento de arquivos CNAB (Centro Nacional de Automação Bancária) para pagamentos bancários. Gerencia a inclusão, atualização, consulta e validação de arquivos de remessa e retorno CNAB nos padrões 240 e 400, abrangendo diversos tipos de pagamentos (TED, DOC, PIX, Boleto, Salário, Fornecedor, Tributos, etc). O sistema realiza validação de layout, nomenclatura de arquivos, controle de situações, agendamento de pagamentos e integração com sistemas bancários.

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `PagamentoCnabController` | Controller REST que expõe 17 endpoints para operações de pagamento CNAB (inclusão, atualização, consulta, cancelamento, validação) |
| `PagamentoCnabService` | Service principal contendo regras de negócio para processamento CNAB, validação de arquivos, atualização de detalhes e cancelamento de agendamentos |
| `CnabPessoaConfigService` | Service para gerenciamento de configurações de pessoa/cliente CNAB (layout, tipo transferência, autorização) |
| `PagamentoCnabRepositoryImpl` | Interface JDBI para operações de persistência de arquivos, lotes e detalhes CNAB |
| `CnabPessoaConfigRepositoryImpl` | Interface JDBI para operações de configuração pessoa CNAB |
| `ControllerInitBinderHandler` | Handler global para conversão de datas e tratamento de exceções HTTP |
| `CnabArquivo` | Entidade principal representando arquivo CNAB com lotes, registros, situação e metadados |
| `CnabArquivoDetalhe` | Entidade representando detalhe de pagamento dentro de um arquivo CNAB |
| `CnabArquivoLote` | Entidade representando lote de pagamentos dentro de arquivo CNAB |
| `CnabPessoaConfig` | Entidade de configuração de pessoa para processamento CNAB |
| Diversos Mappers (MapStruct) | Conversão entre entidades de domínio e DTOs de representação |
| Diversos RowMappers (JDBI) | Mapeamento de ResultSet para objetos de domínio |

### 3. Tecnologias Utilizadas

- **Framework**: Spring Boot 2.x
- **Persistência**: JDBI 3.9.1 (acesso direto SQL/Stored Procedures)
- **Banco de Dados**: Sybase 16 (DBPGF_TES)
- **Mapeamento**: MapStruct 1.5.3
- **Segurança**: Spring Security OAuth2 Resource Server, JWT (jwks.json)
- **Documentação**: Swagger/OpenAPI 3.0.0
- **Servidor**: Tomcat 9.0.110
- **Validação CNAB**: Biblioteca votorantim.spag CNAB 0.20.25
- **Testes**: JUnit 5, Mockito, REST Assured, Pact JVM Provider 4.0.3, ArchUnit
- **Containerização**: Docker
- **Orquestração**: Kubernetes (infra-as-code)
- **Utilitários**: Apache Commons Lang3 3.12, Commons Text 1.10, XStream 1.4.19-BV.7
- **Auditoria**: Audit 2.3.5

### 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| PUT | `/v1/pagamento-cnab/detalhe/nsu/{nuProtocoloSolicitacaoCliente}` | PagamentoCnabController | Atualiza detalhe CNAB por NSU (20 caracteres) |
| PUT | `/v1/pagamento-cnab/detalhe/nuProtocolo/{nuProtocolo}` | PagamentoCnabController | Atualiza detalhe CNAB por número de protocolo |
| PUT | `/v1/pagamento-cnab/detalhe/sequencial/{cdCnabArquivo}` | PagamentoCnabController | Atualiza detalhe CNAB por sequencial do arquivo |
| POST | `/v1/pagamento-cnab/finalizar-processamento/{cdCnabArquivo}` | PagamentoCnabController | Finaliza processamento de arquivo CNAB |
| PUT | `/v1/pagamento-cnab/arquivo/status/{cdCnabArquivo}` | PagamentoCnabController | Atualiza status do arquivo CNAB |
| GET | `/v1/cnab/detalhe/{cdCnabArquivo}` | PagamentoCnabController | Busca detalhes de arquivo CNAB |
| POST | `/v1/cnab/detalhe` | PagamentoCnabController | Inclui detalhes em arquivo CNAB |
| POST | `/v1/cnab/arquivo` | PagamentoCnabController | Inclui novo arquivo CNAB |
| GET | `/v1/cnab/arquivo/tipo-transferencia` | PagamentoCnabController | Lista tipos de transferência disponíveis |
| PUT | `/v1/pagamento-cnab/detalhe/sequencial/agendamento` | PagamentoCnabController | Atualiza sequencial de agendamento |
| POST | `/v1/cnab/validacao` | PagamentoCnabController | Valida arquivo CNAB (nomenclatura, layout, cliente) |
| PUT | `/v1/pagamento-cnab/pessoa-layout-arquivo` | PagamentoCnabController | Atualiza configuração pessoa/layout |
| PUT | `/v1/cnab/cancelar-agendamento/{nuNSUAgendamento}` | PagamentoCnabController | Cancela agendamento de pagamento por NSU |
| GET | `/v1/cnab/pessoa/{cdPessoa}` | PagamentoCnabController | Busca configuração de pessoa CNAB |
| GET | `/v1/cnab/arquivo/layout` | PagamentoCnabController | Lista layouts CNAB disponíveis |
| GET | `/v1/cnab/arquivo/resumido` | PagamentoCnabController | Consulta resumida de arquivos com filtros |
| GET | `/v1/cnab/pagamento/detalhe` | PagamentoCnabController | Busca detalhes de pagamento CNAB |

### 5. Principais Regras de Negócio

1. **Validação de Nomenclatura**: Arquivos CNAB devem seguir padrão `FB240BVIB_CNPJ_yyyyMMddHHmm.REM`
2. **Controle de Situações**: Situações 2 (Processado) e 6 (Download Realizado) impedem atualização/cancelamento de pagamentos
3. **Status de Agendamento**: Status 5 (Agendado) é considerado final e impede novas atualizações
4. **NSU de 20 Caracteres**: Protocolo de solicitação cliente deve ter exatamente 20 caracteres (arquivo 0-12, lote 12-15, detalhe 15-20)
5. **Validação de Cliente**: Cliente deve possuir configuração de layout CNAB antes de processar arquivos
6. **CNPJ Banco Votorantim**: CNPJ 59588111000103 força TipoContaCorrente=6
7. **Forma de Pagamento vs Segmento**: Pagamentos de liquidação/título devem usar segmento J
8. **Tipos de Liquidação**: CC=1, TED=STR(32), DOC=DOC(21), Boleto=22
9. **Conta Pagamento**: Favorecido tipo CONTA_PAGAMENTO força agência 9999 e tipo conta 7
10. **Nosso Número**: Layout 2 usa zeropad(5)+numero, demais layouts usam cdArquivo(12)+lote(3)+detalhe(5)
11. **Validação de Layout**: Utiliza biblioteca externa Votorantim SPAG CNAB 0.20.25 para validação estrutural
12. **Descompactação GZIP**: Sistema descompacta arquivos GZIP automaticamente durante validação
13. **Encoding**: Conversão para ISO-8859-1 durante processamento
14. **Valores Padrão Config**: Tipo transferência=1, Autorizado=S, Agrupar=N
15. **Cancelamento Condicional**: Apenas pagamentos não processados (situação != 6,2) podem ser cancelados

### 6. Relação entre Entidades

**Hierarquia Principal:**
- `CnabArquivo` (1) → (N) `CnabArquivoLote` → (N) `CnabArquivoDetalhe`

**Relacionamentos:**
- `CnabArquivo` possui situação (`CnabArquivoSituacao`), layout (`CnabArquivoLayout`), tipo (`TipoArquivoCnab`)
- `CnabArquivoLote` possui tipo operação, tipo pagamento, forma pagamento
- `CnabArquivoDetalhe` possui situação (`CnabArquivoDetalheSituacao`), segmento, movimento, favorecido, valores, datas
- `CnabPessoaConfig` relaciona pessoa com layout (`CnabArquivoLayout`) e tipo transferência (`CnabArquivoTipoTransferencia`)
- `CnabArquivoTipoTransferencia` define estrutura VAN e diretórios

**Enumerações de Domínio:**
- `TipoArquivoCnabEnum`: REMESSA, RETORNO, VARREDURA_DDA
- `TipoPagamentoCnabEnum`: 26 tipos (COBRANCA, FORNECEDOR, SALARIO, TRIBUTOS, etc)
- `FormaPagtoCnabEnum`: 35 formas (Crédito conta, Cheque, DOC/TED, PIX, etc)
- `DetalheSegmentoEnum`: A, B, C, E, G, H, J, Z
- `TipoMovimentoDetalheEnum`: INCLUSAO, ALTERACAO, EXCLUSAO, ESTORNO
- `TipoOperacaoLoteEnum`: C (Crédito), D (Débito), E (Extrato), R (Remessa), T (Retorno)

### 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbCnabArquivo | Tabela | SELECT | Arquivo CNAB principal com metadados, situação, datas |
| TbCnabArquivoDetalhe | Tabela | SELECT | Detalhes de pagamento dentro de arquivo CNAB |
| TbCnabArquivoLote | Tabela | SELECT | Lotes de pagamento dentro de arquivo CNAB |
| TbCnabArquivoDDADetalhe | Tabela | SELECT | Detalhes DDA (Débito Direto Autorizado) |
| TbCnabPessoaConfiguracao | Tabela | SELECT | Configuração de pessoa/cliente para CNAB |
| TbCnabLayout | Tabela | SELECT | Layouts CNAB disponíveis (240, 400) |
| TbCnabTipoTransferencia | Tabela | SELECT | Tipos de transferência CNAB |
| TbPessoa | Tabela | SELECT | Dados de pessoa/cliente (via Parceiro Global) |

### 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbCnabArquivo | Tabela | INSERT/UPDATE | Inclusão e atualização de arquivos CNAB via stored procedures |
| TbCnabArquivoDetalhe | Tabela | INSERT/UPDATE | Inclusão e atualização de detalhes de pagamento |
| TbCnabArquivoLote | Tabela | INSERT | Inclusão de lotes de pagamento |
| TbCnabPessoaConfiguracao | Tabela | INSERT/UPDATE | Inclusão/atualização de configuração pessoa, data/login validação |

**Stored Procedures Utilizadas:**
- `prFinalizaProcessamentoArqCnab`: Finaliza processamento de arquivo
- `prAlterarArquivoCnab`: Altera dados de arquivo CNAB
- `prIncluirArquivoCnab`: Inclui novo arquivo CNAB
- `prIncluirArquivoLote`: Inclui lote em arquivo
- `prIncluirArquivoDetalhe`: Inclui detalhe de pagamento

### 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| Arquivos CNAB (*.REM) | Leitura | PagamentoCnabService.validarArquivoCNAB | Arquivos de remessa CNAB em base64, descompactados se GZIP |
| Arquivos CNAB validados | Gravação | PagamentoCnabService.validarArquivoCNAB | Arquivo validado retornado em base64 após processamento |
| jwks.json | Leitura | application.yml (OAuth2) | Chaves públicas JWT para validação de tokens |
| Logs de aplicação | Gravação | SecureLogUtil | Logs sanitizados da aplicação |

### 10. Filas Lidas
Não se aplica.

### 11. Filas Geradas
Não se aplica.

### 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Biblioteca Votorantim SPAG CNAB 0.20.25 | Biblioteca Externa | Validação estrutural de arquivos CNAB (layout, campos, regras) |
| Sistema Bancário | Integração CNAB | Recepção/envio de arquivos CNAB 240/400 para processamento bancário |
| Parceiro Global (TbPessoa) | Banco de Dados | Consulta de dados de pessoa/cliente |
| OAuth2 Authorization Server | Autenticação/Autorização | Validação de tokens JWT via jwks.json |
| Sistema de GED (Gerenciamento Eletrônico Documentos) | Armazenamento | Armazenamento de arquivos CNAB (cdGed referenciado) |

### 13. Avaliação da Qualidade do Código

**Nota:** 8/10

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada com separação clara de responsabilidades (Controller, Service, Repository, Domain)
- Uso adequado de padrões de projeto (DTO, Mapper, Value Objects)
- Cobertura de testes abrangente (200+ cenários de teste unitário)
- Documentação OpenAPI/Swagger completa
- Tratamento de exceções estruturado com handlers globais
- Uso de enumerações para domínios bem definidos
- Validações de negócio centralizadas no Service
- Configuração externalizada (application.yml, profiles)
- Uso de MapStruct para mapeamento automático
- Sanitização de logs para segurança

**Pontos de Melhoria:**
- Uso de JDBI com SQL direto e stored procedures dificulta manutenibilidade (poderia usar JPA/Hibernate)
- Alguns métodos do Service são extensos e poderiam ser refatorados
- Dependência forte de biblioteca externa proprietária (votorantim.spag CNAB)
- Conversões manuais entre enums e códigos SQL espalhadas pelo código
- Falta de cache para consultas frequentes (layouts, tipos transferência)
- Alguns magic numbers e strings hardcoded (ex: CNPJ BV, agência 9999)
- Documentação inline limitada em alguns métodos complexos

### 14. Observações Relevantes

1. **Banco de Dados Sybase**: Sistema utiliza Sybase 16, tecnologia legada que pode dificultar migração futura
2. **Stored Procedures**: Lógica de persistência delegada a stored procedures Oracle/Sybase, dificultando testes e portabilidade
3. **Biblioteca Proprietária**: Dependência crítica da biblioteca votorantim.spag CNAB 0.20.25 para validação
4. **Múltiplos Ambientes**: Configuração para 5 ambientes (local, des, qa, uat, prd) com portas e conexões distintas
5. **Segurança OAuth2**: Implementação robusta com JWT e endpoints públicos apenas para actuator e swagger
6. **Kubernetes Ready**: Infraestrutura como código com probes de saúde configurados (liveness 420s, readiness 3s)
7. **Encoding Específico**: Conversão para ISO-8859-1 necessária para compatibilidade bancária
8. **Compressão GZIP**: Suporte automático a arquivos compactados
9. **Tipos de Pagamento**: Suporte a 26 tipos diferentes de pagamento (TED, DOC, PIX, Boleto, Salário, Fornecedor, Tributos, etc)
10. **Auditoria**: Sistema de auditoria integrado (Audit 2.3.5)
11. **Testes de Arquitetura**: Uso de ArchUnit para validação de regras arquiteturais
12. **Pact Testing**: Implementação de testes de contrato com Pact JVM Provider
13. **Recursos Kubernetes**: Configuração conservadora (500m-1cpu, 768Mi mem)
14. **Delay de Inicialização**: Liveness probe com delay de 420s indica aplicação pesada na inicialização