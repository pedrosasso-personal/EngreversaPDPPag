# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema orquestrador de consultas de extrato bancário que integra múltiplas fontes de dados (Sybase legado, Elasticsearch e Google Cloud Spanner) através de Apache Camel. O sistema oferece duas versões de API (V1 e V2), com roteamento dinâmico baseado em Feature Toggles, validações extensivas de parâmetros e suporte a diferentes origens de parceiros (Internet Banking, Mobile Banking, Open Finance, etc). Implementa arquitetura hexagonal com separação clara entre domínio, portas e adaptadores.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ExtratoV2ServiceImpl** | Orquestra consultas V2 com cadeia de validadores (Body, Origem, CPF/CNPJ, Período, Filtros) |
| **ExtratoService** | Serviço legado V1 para consultas de movimentações, PIX, histórico e exportação |
| **ServiceV2Factory** | Factory pattern para selecionar fluxo de consulta (Sybase/Elastic/Spanner) baseado em FTs |
| **ExtratoV2Fluxo*** | Implementações de fluxo (Sybase, Elasticsearch, Spanner) com conversores específicos |
| **ExtratoController** | Controlador REST V1 (pesquisas, movimentações, PIX, exportação, histórico) |
| **ExtratoV2Controller** | Controlador REST V2 (consulta unificada) |
| **MovimentacoesRouter** | Rota Camel para consultas Sybase (quantidade/data/pesquisa/histórico) |
| **ElasticsearchRouter** | Rota Camel para consultas Elasticsearch com validação de conta |
| **SpannerRouter** | Rota Camel para consultas Google Spanner com validação de conta |
| **ConsultaExtratoV2Mapper** | Mapeia requests V2 para formato interno com tratamento Elastic/Sybase |
| **AccountLedgerPesquisaConverter** | Converte resposta Spanner para formato Elasticsearch padronizado |
| **IdentificaFluxoExtratoStrategy** | Chain of Responsibility para seleção de fluxo (Sybase/Elastic/Spanner) |
| **FiltroRegraStrategy*** | Validadores específicos por tipo de filtro (CdTransacao, VrOperacao, Datas, NSU, etc) |
| **ExtratoValidator** | Validações V1 (tipoPaginacao, CPF/CNPJ, tamanhoPaginacao, filtros data, ordenação) |
| **CategoriaTransacao** | Enum com 80+ tipos de transação (PIX, TED, TEF, Boleto, Cartão, etc) |
| **TipoLancamento** | Enum com 20+ tipos de lançamento (Aplicação, Câmbio, DOC, Empréstimo, etc) |
| **OrigemParceiroEnum** | Define limites de paginação por parceiro (INTB:5000, MBBD:100, etc) |

---

## 3. Tecnologias Utilizadas

- **Framework:** Spring Boot 2.x, Spring MVC, Spring Security (OAuth2 Resource Server)
- **Integração:** Apache Camel 3.x (rotas, ProducerTemplate, ConsumerTemplate)
- **Persistência:** Sybase (legado), Elasticsearch, Google Cloud Spanner
- **Mapeamento:** MapStruct (estilo manual), Lombok
- **Documentação:** Springfox Swagger 2, OpenAPI 3
- **Resiliência:** Resilience4j (TimeLimiter 5s), Feature Toggle (ConfigCat)
- **Serialização:** Jackson, Gson
- **Segurança:** JWT, SHA-256 (hash contas TED Salário)
- **Build:** Maven, Swagger Codegen, OpenAPI Generator
- **Testes:** JUnit 5, Mockito
- **Monitoramento:** Spring Actuator, Prometheus, SLF4J
- **Containerização:** Docker (Java 11, JVM opts 70% RAM)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/movimentacoes-bancaria/pesquisas` | ExtratoController | Pesquisa extrato por origem com termo de busca |
| GET | `/v1/movimentacoes-bancaria` | ExtratoController | Consulta movimentações por quantidade ou data |
| GET | `/v1/movimentacoes-bancaria/extratoPix` | ExtratoController | Consulta detalhes movimentação PIX (NSU/numeroDocumento) |
| POST | `/v1/extrato/exportar` | ExtratoController | Exporta extrato para fila Pubsub (OFX/PDF) |
| GET | `/v1/movimentacoes-bancaria/extrato` | ExtratoController | Consulta histórico movimentações com favorecido |
| POST | `/v2/movimentacoes-bancaria/pesquisas` | ExtratoV2Controller | Consulta extrato V2 unificada (Sybase/Elastic/Spanner) |

**Validações Comuns:**
- Header `origem` obrigatório (OrigemParceiroEnum)
- CPF/CNPJ (11/14 dígitos)
- Paginação limitada por parceiro (FT ou enum)
- Período obrigatório V2 (tipoData, inicio, fim)
- Termo busca mínimo 2 caracteres para Spanner

---

## 5. Principais Regras de Negócio

1. **Roteamento Dinâmico de Fluxo:**
   - FT `fluxo_sybase` ON → Sybase
   - Termo busca OU FT `fluxo_elastic` ON:
     - FT `consulta_spanner` ON + termo ≥2 chars → Spanner
     - Senão → Elasticsearch
   - Default → Sybase

2. **Validações de Entrada:**
   - CPF: 11 dígitos, CNPJ: 14 dígitos
   - Origem obrigatória com limite paginação específico (INTB/EMBK:5000, MBBD:100, OPNF:1000)
   - Período V2: tipoData, inicio, fim obrigatórios
   - Elasticsearch: máximo 10.000 itens (página × tamanho ≤ 10.000)
   - Filtros adicionais: validação por tipo (numérico, data, alfanumérico, enum)

3. **Paginação:**
   - Tipo: QUANTIDADE (offset) ou DATA (cursor)
   - Limites por parceiro via FT `limite_paginacao_parceiros` ou enum
   - Erro se página requisitada > última página com resultados

4. **Conta TED Salário:**
   - Validação via hash SHA-256 (banco+agencia+conta+tipoConta)
   - Oculta dados favorecido em consultas PIX

5. **Mapeamento de Transações:**
   - 80+ categorias (PIX, TED, TEF, Boleto, Cartão, Tarifa, Saque, etc)
   - 20+ tipos lançamento (Aplicação, Câmbio, DOC, Empréstimo, Pix, etc)
   - Conversão TIPO_TRANSACAO/TIPO_LANCAMENTO → códigos numéricos

6. **Cálculos Financeiros:**
   - BigDecimal escala 2, arredondamento HALF_EVEN
   - Total entrada/saída por tipo débito/crédito
   - Saldo antes/após transação

7. **Integração Spanner:**
   - AccountId gerado via SHA-256(banco+agencia+conta+tipoConta)
   - Tentativa bancos 436 e 161 sequencialmente
   - Conversão CreditDebitIndicator (C/D → CREDITO/DEBITO)

8. **Exportação:**
   - Formatos: OFX, PDF
   - Limite máximo movimentações (HTTP 429)
   - Enriquecimento com dados cadastrais (email ativo principal)

9. **Validação Conta Pessoa:**
   - TimeLimiter 5s
   - Valida CPF/CNPJ titular pertence à conta
   - Popula documentoTitular e dataAbertura

10. **Timezone:**
    - Ajuste +3h para V1 (compatibilidade legado)
    - OffsetDateTime formato ISO

---

## 6. Relação entre Entidades

**Hierarquia de Requisição V2:**
```
ExtratoV2RequestDomain
├── banco, agencia, conta, cpfcnpj
├── paginacao (pagina, tamanho)
├── origem (OrigemParceiroEnum)
└── ExtratoV2RequestBodyDomain
    ├── termoBusca
    ├── ordem (ASC/DESC)
    ├── destacar (boolean)
    ├── FiltrosV2RequestPeriodoDomain
    │   ├── tipoData (INCLUSAO/COMANDO/EFETIVACAO)
    │   ├── inicio (OffsetDateTime)
    │   └── fim (OffsetDateTime)
    └── filtrosAdicionais (List)
        ├── campo (FiltroExtratoV2Enum)
        ├── valor
        ├── de (range)
        └── para (range)
```

**Resposta Unificada:**
```
PesquisaElasticsearchResponse
├── resultados (List<Movimentacao>)
│   ├── codBanco, categoria, titulo, descricao
│   ├── valor, saldoAntes, saldoApos
│   ├── id, nsu, numeroDocumento
│   ├── debito (boolean)
│   └── datas (inclusao, efetivacao, comando)
├── PaginacaoDomain
│   ├── quantidade, pagina
│   ├── ultimaPagina, proximaPagina
└── totalEntrada, totalSaida
```

**Conversões:**
- **Spanner:** `PaginatedAccountLedgerResponseDomain` → `PesquisaElasticsearchResponse`
- **Sybase:** `ExtratoMovimentacoesPesquisas` → `PesquisaElasticsearchResponse`
- **PIX:** `MovimentacaoPix` (dados remetente/favorecido, NSU, numeroDocumento)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| **Movimentações Conta (Sybase)** | Tabela | SELECT | Movimentações bancárias legadas (via sboot-atom-cc-extrato) |
| **Índice Movimentações (Elasticsearch)** | Índice | SEARCH | Movimentações indexadas para busca por termo |
| **account_ledger (Spanner)** | Tabela | SELECT | Transações financeiras no Google Cloud Spanner |
| **Contas TED Salário** | Config JSON | READ | Mapa hash SHA-256 → ContaId para validação |
| **Dados Cadastrais Pessoa** | API | GET | Email ativo, dados titular (via sboot-orch-dados-cadastrais-pessoa) |
| **Dados Cadastrais Cliente** | API | GET | Validação conta pessoa, documentoTitular (via sboot-atom-cliente-dados-cadastrais) |
| **Detalhes Movimentação PIX** | API | GET | Dados completos transação PIX (via sboot-orch-det-extrato) |

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| **contas-ted-salario.json** | Leitura | ContaTedSalarioProperties | Configuração contas TED Salário com hash SHA-256 |
| **Extrato OFX** | Gravação | DadosMovimentacaoExtratoRepository | Arquivo extrato formato OFX (via fila Pubsub) |
| **Extrato PDF** | Gravação | DadosMovimentacaoExtratoRepository | Arquivo extrato formato PDF (via fila Pubsub) |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Responsável | Breve Descrição |
|--------------|------------|-------------------|-----------------|
| **Exportação Extrato** | Google Pubsub | NotificacaoRouter (Camel) | Publica requisição exportação extrato (OFX/PDF) via sboot-atom-extrato |

---

## 12. Integrações Externas

| Sistema Externo | Tipo | Endpoint/Recurso | Breve Descrição |
|-----------------|------|------------------|-----------------|
| **sboot-atom-cc-extrato** | REST API | `/cc-extrato`, `/extrato` | Consulta movimentações Sybase (quantidade/data/histórico) |
| **sboot-atom-extrato** | REST API | `/v1/extrato/pesquisas` | Consulta movimentações Elasticsearch |
| **sboot-atom-extrato** | REST API | `ExportarExtratoParaFilaPubsubApi` | Exporta extrato para fila Pubsub |
| **sboot-atom-report** | REST API | `/v1/digital-bank/{bankId}/accounts/{accountId}/transactions` | Consulta transações Google Spanner |
| **sboot-orch-det-extrato** | REST API | `GET ?numeroDocumento=` | Detalhes movimentação PIX |
| **sboot-orch-dados-cadastrais-pessoa** | REST API | `${serviceOrchDadosCadastraisPessoa}` | Dados cadastrais pessoa (email ativo) |
| **sboot-atom-cliente-dados-cadastrais** | REST API | `/{numeroConta}` | Validação conta pessoa, dados titular |
| **ConfigCat** | Feature Toggle | API ConfigCat | Flags: fluxo_sybase, fluxo_elastic, consulta_spanner, limite_paginacao_parceiros |
| **Google Cloud Spanner** | NoSQL DB | Via sboot-atom-report | Banco de dados transacional distribuído |
| **Elasticsearch** | Search Engine | Via sboot-atom-extrato | Índice de movimentações para busca textual |
| **Sybase** | RDBMS | Via sboot-atom-cc-extrato | Banco de dados legado |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8,5/10**

**Justificativa:**

**Pontos Fortes:**
- **Arquitetura Hexagonal:** Separação clara entre domínio (services, domain), portas (repositories interfaces) e adaptadores (implementações), facilitando testes e manutenção
- **Padrões de Projeto:** Uso adequado de Factory (ServiceV2Factory), Strategy (FiltroRegraStrategy, FluxoExtratoStrategy), Chain of Responsibility (validadores V2)
- **Validações Extensivas:** Cadeia de validadores com responsabilidade única, mensagens de erro padronizadas via CodigoErroEnum
- **Feature Toggles:** Roteamento dinâmico sem deploy, permitindo rollback instantâneo
- **Conversores Especializados:** AccountLedgerPesquisaConverter e MovimentacoesPesquisaConverter unificam respostas de fontes heterogêneas
- **Tratamento Financeiro:** BigDecimal com escala 2 e arredondamento bancário (HALF_EVEN)
- **Testes Unitários:** Cobertura de validators, mappers, services, converters e enums
- **Nomenclatura:** Classes e métodos descritivos (ex: `ValidaFluxoExtratoElasticStrategy`)
- **Lombok:** Redução de boilerplate com @AllArgsConstructor, @Slf4j, @Builder

**Pontos de Melhoria:**
- **Lógica Negócio Espalhada:** Regras de validação distribuídas em múltiplas strategies; poderia centralizar em domain services
- **Validações Annotation-Based:** Substituir validadores manuais por Bean Validation (JSR-303) onde aplicável
- **Testes Mock-Heavy:** Dependência excessiva de mocks; considerar testes de integração com Testcontainers
- **Documentação:** Falta Javadoc em classes críticas (ExtratoService, ServiceV2Factory)
- **Complexidade Ciclomática:** Métodos longos em ExtratoService (ex: `consultaExtratoMovimentacoes` com múltiplos ifs)
- **Enums Gigantes:** CategoriaTransacao e TipoLancamento com 80+ e 20+ valores; considerar externalizar em banco/config
- **Acoplamento Camel:** Lógica de negócio misturada com rotas Camel; separar em services puros
- **Tratamento de Erros:** Exceções checked (DadosCadastraisPessoaException) misturadas com unchecked; padronizar

**Recomendações:**
1. Refatorar ExtratoService em services menores (MovimentacoesService, PixService, ExportacaoService)
2. Implementar testes de contrato (Pact) para integrações REST
3. Adicionar métricas customizadas (Micrometer) para monitorar fluxos Sybase/Elastic/Spanner
4. Documentar decisões arquiteturais (ADRs) sobre escolha Camel e Feature Toggles
5. Implementar cache (Redis) para consultas frequentes de dados cadastrais

---

## 14. Observações Relevantes

1. **Migração Gradual:** Sistema em transição de Sybase legado para Spanner, com Elasticsearch como ponte. Feature Toggles permitem rollback sem deploy.

2. **Múltiplas Versões API:** V1 (legado, 5 endpoints) e V2 (unificado, 1 endpoint). V2 usa validadores encadeados e factory para roteamento.

3. **Paginação Complexa:** Dois tipos (QUANTIDADE offset-based, DATA cursor-based) com limites específicos por parceiro (INTB:5000, MBBD:100).

4. **Segurança PIX:** Contas TED Salário (hash SHA-256) têm dados favorecido mascarados para proteger privacidade.

5. **Resiliência:** TimeLimiter 5s em consultas externas, tratamento de timeout com fallback.

6. **Timezone Legacy:** Ajuste +3h em datas V1 para compatibilidade com sistema legado.

7. **Elasticsearch Limits:** Máximo 10.000 itens por consulta (limitação técnica do Elasticsearch).

8. **Spanner Multi-Banco:** Tenta bancos 436 e 161 sequencialmente para cobrir diferentes instituições.

9. **Enriquecimento de Dados:** Exportação busca email ativo principal em dados cadastrais, com fallback para email mais recente.

10. **Validação Extensiva:** 15+ strategies de validação de filtros (numérico, data, alfanumérico, enum, range).

11. **Mapeamento Transações:** 80+ categorias e 20+ tipos de lançamento mapeados para códigos numéricos legados.

12. **Apache Camel:** 7 routers (Movimentacoes, Elasticsearch, Spanner, Pix, DadosCadastrais, Notificacao, Spanner) orquestram integrações assíncronas.

13. **Monitoramento:** Logs estruturados com DashboardHelper (httpStatus, origem, filtros, erros) para observabilidade.

14. **Containerização:** Docker com Java 11, JVM configurada para 70% RAM disponível.

15. **Geração de Código:** Swagger Codegen e OpenAPI Generator para clientes REST (atom-extrato, cliente-dados-cadastrais, det-extrato, cc-extrato, report, corporativo-dados-cadastrais).