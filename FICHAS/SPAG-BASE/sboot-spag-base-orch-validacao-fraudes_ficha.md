# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-spag-base-orch-validacao-fraudes** é um orquestrador de validação de fraudes para transações financeiras, desenvolvido em Java com Spring Boot e Apache Camel. Ele recebe solicitações de análise transacional (transferências e boletos), aplica regras de negócio baseadas em Feature Toggles, e encaminha as requisições para o serviço externo de eventos financeiros (antifraude). O sistema atua como intermediário, normalizando dados, roteando requisições conforme o tipo de transação e retornando o resultado da análise de fraude.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal de inicialização da aplicação Spring Boot com Feature Toggle habilitado. |
| **ValidacaoFraudesController** | Controller REST que expõe o endpoint de validação de fraudes e delega para o serviço. |
| **ValidacaoFraudesServiceImpl** | Implementa a lógica de negócio de validação, incluindo geração/normalização de NSU e decisão via Feature Toggle. |
| **FeatureToggleService** | Gerencia as Feature Toggles para habilitar/desabilitar validação de fraudes globalmente ou por origem/sigla. |
| **ValidacaoFraudeRouter** | Roteador Apache Camel que direciona requisições para validação de transferência ou boleto conforme código de liquidação. |
| **ExtraiCodigoLiquidacaoProcessor** | Processor Camel que extrai o código de liquidação da transação para decisão de roteamento. |
| **EventosFinanceirosRepositoryImpl** | Implementa chamadas HTTP aos serviços externos de eventos financeiros (transferência e boleto). |
| **ValidacaoTransferenciaMapper** | Mapeia DTOs internos para requisições de análise de transferência e respostas. |
| **ValidacaoBoletoMapper** | Mapeia DTOs internos para requisições de análise de boleto e respostas. |
| **ValidacaoFraudeMapper** | Mapeia requisições REST para DTOs internos de análise transacional. |
| **Utils** | Classe utilitária com funções para geração/normalização de NSU, determinação de canal/produto, etc. |
| **LoggerHelper** | Classe utilitária para sanitização de mensagens de log. |
| **AppProperties** | Classe de configuração que carrega propriedades da aplicação (URLs de serviços externos). |

---

## 3. Tecnologias Utilizadas

- **Java 21**
- **Spring Boot 3.x** (com Spring Security OAuth2 Resource Server)
- **Apache Camel 3.x** (integração e roteamento)
- **Spring Data JPA / Hibernate** (persistência, embora não haja uso explícito de banco no código fornecido)
- **OpenAPI Generator** (geração de clientes e contratos a partir de especificações YAML)
- **ConfigCat / Feature Toggle** (gerenciamento de funcionalidades via flags)
- **OkHttp / RestTemplate** (clientes HTTP)
- **Logback** (logging com formato JSON)
- **Swagger/OpenAPI 3.0** (documentação de APIs)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Google Cloud Platform (GCP)** (infraestrutura)
- **Micrometer / Prometheus** (métricas e observabilidade)
- **OpenTelemetry** (tracing distribuído)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/transacional/analise-fraude` | ValidacaoFraudesController | Recebe uma transação financeira e retorna o resultado da análise de fraude (OK, NOK ou N/A). |

---

## 5. Principais Regras de Negócio

1. **Geração/Normalização de NSU**: Se o NSU (identificador da transação) não for fornecido ou for inválido, o sistema gera um novo NSU baseado no código de origem, CNPJ do remetente e UUID parcial.

2. **Feature Toggle Global**: Se a feature `ft_boolean_spag_base_validacao_fraudes_global` estiver ativa, todas as transações são validadas via serviço de antifraude.

3. **Feature Toggle por Origem/Sigla**: Se a feature global estiver inativa, o sistema verifica a feature `ft_text_spag_base_origem_sigla_validacao_fraudes`, que contém regras de origem e sigla (ex: "78;CNAB/88;*"). Apenas transações que correspondem às regras configuradas são validadas.

4. **Roteamento por Código de Liquidação**:
   - Código 22: Rota para validação de boleto.
   - Códigos 1, 31, 32: Rota para validação de transferência.
   - Outros códigos: Não há validação específica.

5. **Determinação de Canal e Produto**:
   - Origem 88: Canal "EXTERNO".
   - Origem 78 + Sigla CNAB/CCBD: Canal "IB", Produto "CNAB".

6. **Retorno de Status**: O sistema retorna `OK` (aprovado), `NOK` (reprovado) ou `N/A` (não aplicável, quando a validação está desabilitada).

7. **Retry em Falhas**: O roteador Camel aplica até 2 tentativas de reenvio em caso de falha na chamada ao serviço externo.

---

## 6. Relação entre Entidades

- **AnaliseTransacionalDTO**: Representa a transação a ser analisada, contendo ID, valor, tipo de lançamento, remetente, favorecido, linha digitável, código de origem, sigla do sistema e código de liquidação.
- **DadosParticipanteDTO**: Representa remetente ou favorecido, com tipo de pessoa (PF/PJ), CPF/CNPJ e dados bancários.
- **DadosBancariosDTO**: Contém número da conta, código do banco, agência e tipo de conta.
- **AnaliseFraudeResponse**: Resposta da validação, contendo protocolo de análise e status (OK/NOK/N/A).

**Relacionamentos**:
- `AnaliseTransacionalDTO` possui 1 `DadosParticipanteDTO` para remetente e 1 para favorecido.
- `DadosParticipanteDTO` possui 0..1 `DadosBancariosDTO`.

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|--------------------------|-----------------|
| application.yml | Leitura | Spring Boot (AppProperties) | Arquivo de configuração principal da aplicação. |
| application-des.yml | Leitura | Spring Boot | Configurações específicas do ambiente de desenvolvimento. |
| application-local.yml | Leitura | Spring Boot | Configurações específicas do ambiente local. |
| logback-spring.xml | Leitura | Logback | Configuração de logs (formato JSON, appenders, níveis). |
| infra.yml | Leitura | Infraestrutura (Kubernetes/GCP) | Configurações de infraestrutura como código (variáveis de ambiente, secrets, probes). |
| Dockerfile | Leitura | Docker | Definição da imagem Docker da aplicação. |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| **sboot-gfrd-base-orch-eventos-financeiros** (Transferência) | API REST | Serviço de análise de fraudes para transferências (TED). Endpoint: `/v1/eventos-financeiro/ted`. |
| **sboot-gfrd-base-orch-eventos-financeiros** (Boleto) | API REST | Serviço de análise de fraudes para boletos. Endpoint: `/v1/eventos-financeiro/boleto`. |
| **ConfigCat** | Feature Toggle | Serviço de gerenciamento de feature flags (via biblioteca `sbootlib-arqt-base-feature-toggle`). |
| **OAuth2 / JWT** | Autenticação | Validação de tokens JWT via Spring Security OAuth2 Resource Server. |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 8/10

**Justificativa:**

**Pontos Positivos:**
- Código bem estruturado, seguindo padrões de arquitetura em camadas (controller, service, repository, mapper).
- Uso adequado de Spring Boot, Apache Camel e Feature Toggles para flexibilidade.
- Separação clara de responsabilidades entre classes.
- Uso de DTOs e mappers para isolamento de camadas.
- Tratamento de exceções e retry em integrações externas.
- Sanitização de logs para segurança.
- Documentação via OpenAPI/Swagger.
- Configuração de infraestrutura como código (infra.yml).

**Pontos de Melhoria:**
- Algumas classes utilitárias (Utils, LoggerHelper) poderiam ser mais coesas e divididas em responsabilidades menores.
- Falta de testes unitários nos arquivos fornecidos (embora a estrutura de testes exista).
- Alguns métodos longos (ex: `deveValidarPorOrigemESigla`) poderiam ser refatorados para melhor legibilidade.
- Uso de constantes mágicas em alguns pontos (ex: códigos de liquidação, CNPJs hardcoded).
- Documentação inline (JavaDoc) ausente em algumas classes e métodos.

---

## 14. Observações Relevantes

1. **Feature Toggles**: O sistema depende fortemente de Feature Toggles para habilitar/desabilitar funcionalidades. A configuração incorreta pode resultar em transações não validadas.

2. **Geração de NSU**: A lógica de geração de NSU depende do código do banco do remetente (655 ou 413). Caso o banco não seja reconhecido, uma exceção é lançada.

3. **Ambientes**: O sistema está preparado para múltiplos ambientes (local, des, uat, prd) com configurações específicas.

4. **Observabilidade**: Integração com OpenTelemetry, Prometheus e Micrometer para tracing e métricas.

5. **Segurança**: Uso de OAuth2 JWT para autenticação e autorização. Endpoints públicos configuráveis por perfil.

6. **Containerização**: Aplicação dockerizada com suporte a multi-layer para otimização de builds.

7. **Retry e Resiliência**: O roteador Camel aplica retry automático em falhas de integração (até 2 tentativas).

8. **Sanitização de Logs**: Todos os logs são sanitizados para evitar injeção de caracteres especiais.

9. **Swagger UI**: Disponível apenas em ambientes de desenvolvimento (des) e local.

10. **Dependências Externas**: O sistema depende de serviços externos (eventos financeiros) e de um serviço de Feature Toggle (ConfigCat).