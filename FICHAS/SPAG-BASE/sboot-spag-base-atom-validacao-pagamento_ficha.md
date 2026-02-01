---
## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema **sboot-spag-base-atom-validacao-pagamento** é um serviço atômico REST desenvolvido em Java com Spring Boot, responsável por validar solicitações de pagamento e gerenciar operações relacionadas a lançamentos financeiros e boletos. O sistema realiza validações de grade horária, data de movimento, dia útil, além de fornecer funcionalidades para consulta e atualização de informações de boletos (incluindo baixa CIP), registro de transferências e integração com banco de dados SQL Server.

---

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal que inicializa a aplicação Spring Boot |
| **ValidacaoPagamentoController** | Controlador REST para validação de pagamentos |
| **LancamentoController** | Controlador REST para operações de lançamentos (consulta, atualização, registro) |
| **BoletoCompletoInfoController** | Controlador REST para geração de informações completas de boleto |
| **ValidacaoPagamentoServiceImpl** | Implementação da lógica de negócio para validação de pagamentos |
| **LancamentoServiceImpl** | Implementação da lógica de negócio para operações de lançamentos |
| **BoletoCompletoInfoServiceImpl** | Implementação da lógica de negócio para geração de informações de boleto |
| **JdbiValidacaoPagamentoRepository** | Repositório JDBI para operações de atualização de lançamentos |
| **JdbiLancamentoRepository** | Repositório JDBI para operações de consulta e manipulação de lançamentos |
| **ValidacaoPagamentoExceptionHandler** | Tratamento centralizado de exceções da aplicação |
| **OpenApiConfiguration** | Configuração do Swagger/OpenAPI para documentação da API |
| **ValidacaoPagamentoConfiguration** | Configuração de beans e dependências da aplicação |

---

### 3. Tecnologias Utilizadas
- **Java 11**
- **Spring Boot 2.7.18** (framework principal)
- **Spring Security OAuth2** (autenticação JWT)
- **JDBI 3.9.1** (acesso a banco de dados)
- **Microsoft SQL Server** (banco de dados)
- **Swagger/Springfox 3.0.0** (documentação de API)
- **Micrometer/Prometheus** (métricas e monitoramento)
- **Grafana** (visualização de métricas)
- **MapStruct 1.4.1** (mapeamento de objetos)
- **Lombok** (redução de boilerplate)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **HikariCP** (pool de conexões)
- **Logback** (logging)

---

### 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/validacao-pagamento | ValidacaoPagamentoController | Valida uma solicitação de pagamento |
| GET | /v1/lancamento/{codigoLancamento}/baixa-boleto-cip | LancamentoController | Consulta situação de baixa de boleto na CIP |
| PUT | /v1/lancamento/{codLancamento}/baixa-boleto-cip | LancamentoController | Atualiza indicador de baixa de boleto CIP |
| PUT | /v1/lancamento/{codigoLancamento}/numero-protocolo | LancamentoController | Relaciona lançamento à Caixa de Entrada SPB |
| PUT | /v1/lancamento/{codigoLancamento}/codigo-lancamento-pgft | LancamentoController | Relaciona lançamento ao lançamento PGFT |
| GET | /v1/lancamento/{codigoLancamento}/dados-registro-boleto | LancamentoController | Retorna dados para registro de boleto |
| POST | /v1/lancamento/{codigoLancamento}/registro-transferencia | LancamentoController | Registra uma transferência (TED) de boleto STR26 |
| POST | /v1/boleto-completo-info | BoletoCompletoInfoController | Gera informações completas para baixa de boleto na CIP |

---

### 5. Principais Regras de Negócio

1. **Validação de Grade Horária**: Verifica se a hora atual está dentro da grade horária permitida (entre dataInicioGradeCamara e dataFimGradeCamara)
2. **Validação de Data de Movimento**: Garante que a data de movimento não seja anterior à data atual
3. **Validação de Dia Útil**: Verifica se a data de movimento é um dia útil
4. **Atualização de Status de Lançamento**: Atualiza o status do lançamento para 1 (em processamento) durante validação
5. **Atualização de Códigos BUC**: Atualiza códigos de cliente (remetente e favorecido) no lançamento
6. **Geração de Informações de Boleto CIP**: Calcula tipo de baixa (integral/parcial, interbancária/intrabancária) baseado em regras específicas
7. **Validação de Valor para STR**: Boletos acima de R$ 250.000,00 são direcionados para liquidação STR
8. **Registro de Transferência**: Cria novo lançamento de transferência (TED) a partir de dados de boleto STR26
9. **Tratamento de Portador**: Define portador como remetente quando não informado
10. **Identificação de Banco**: Diferencia operações entre Banco BV (413) e Banco Votorantim (655)

---

### 6. Relação entre Entidades

**Entidades Principais:**

- **ValidacaoPagamentoDto**: Representa dados de validação de pagamento (codigoLancamento, datas, flags, códigos BUC)
- **DadosRegistroBoletoDto**: Contém todos os dados de um lançamento/boleto (mais de 100 campos)
- **BaixaBoletoCipDto**: Representa status de baixa de boleto na CIP
- **BoletoCompletoInfoDto**: Informações completas para baixa de boleto na CIP
- **DadosPagamentoBoletoDto**: Dados de pagamento de boleto (portador, remetente, boleto, valores)
- **DadosTransferenciaDto**: Dados para registro de transferência bancária

**Relacionamentos:**
- Um lançamento pode ter dados de pessoa (remetente, favorecido, devedor, portador)
- Um lançamento pode ter dados de cliente fintech associados
- Um boleto está associado a um lançamento
- Uma transferência é criada a partir de um lançamento origem

---

### 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbLancamento | tabela | SELECT | Consulta dados de lançamentos financeiros |
| TbLancamentoPessoa | tabela | SELECT | Consulta dados de pessoas relacionadas ao lançamento |
| TbLancamentoClienteFintech | tabela | SELECT | Consulta dados de clientes fintech relacionados ao lançamento |
| TbParametroPagamentoFintech | tabela | SELECT | Consulta parâmetros de pagamento fintech |

---

### 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbLancamento | tabela | UPDATE | Atualiza status, códigos BUC, protocolo, baixa CIP e código PGFT |
| TbLancamento | tabela | INSERT | Insere novo lançamento via procedure PrIncluirLancamento |

---

### 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Application (Spring Boot) | Configurações da aplicação (datasource, security, server) |
| logback-spring.xml | leitura | Logback | Configuração de logs da aplicação |
| *.sql (resources) | leitura | JDBI Repositories | Queries SQL para operações de banco de dados |
| swagger/*.yaml | leitura | Swagger Codegen | Especificação OpenAPI para geração de interfaces |

---

### 10. Filas Lidas
não se aplica

---

### 11. Filas Geradas
não se aplica

---

### 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| SQL Server (DBSPAG) | Banco de Dados | Banco de dados principal para persistência de lançamentos e boletos |
| OAuth2/JWT Provider | Autenticação | Serviço de autenticação via JWT (apigateway.bvnet.bv) |
| Prometheus | Monitoramento | Exportação de métricas da aplicação |
| CIP (Câmara Interbancária de Pagamentos) | Sistema Externo | Sistema mencionado para baixa de boletos (integração implícita) |

---

### 13. Avaliação da Qualidade do Código

**Nota: 7.5/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões hexagonais (ports/adapters)
- Separação clara de responsabilidades em módulos (common, domain, application)
- Uso adequado de DTOs e mapeadores
- Implementação de testes unitários, integração e funcionais
- Documentação OpenAPI/Swagger bem definida
- Configuração adequada de segurança (OAuth2/JWT)
- Uso de JDBI para acesso a dados de forma eficiente
- Tratamento centralizado de exceções
- Logging estruturado

**Pontos de Melhoria:**
- Classe `DadosRegistroBoletoDto` com mais de 100 campos (violação de coesão)
- Método `map` em `DadosRegistroBoletoMapper` extremamente longo (mais de 150 linhas)
- Lógica complexa de negócio em `BoletoCompletoInfoServiceImpl` poderia ser melhor modularizada
- Alguns métodos com muitos parâmetros (ex: método `tipo` com 6 parâmetros)
- Uso de strings mágicas em alguns pontos ("S", "N", "F", "J")
- Falta de validações de entrada em alguns endpoints
- Comentários em código poderiam ser mais descritivos
- Alguns testes mockados de forma muito simplista

---

### 14. Observações Relevantes

1. **Ambiente Multi-Profile**: Sistema configurado para múltiplos ambientes (local, des, qa, uat, prd)
2. **Monitoramento Completo**: Infraestrutura de observabilidade com Prometheus e Grafana já configurada
3. **Containerização**: Dockerfile e configurações Docker Compose prontas para deploy
4. **CI/CD**: Configuração Jenkins presente (jenkins.properties)
5. **Infraestrutura como Código**: Arquivo infra.yml para deploy em OpenShift/Kubernetes
6. **Segurança**: Implementação de OAuth2 com JWT para autenticação
7. **Pool de Conexões**: HikariCP configurado para gerenciamento eficiente de conexões
8. **Auditoria**: Integração com biblioteca de trilha de auditoria do Banco Votorantim
9. **Versionamento de API**: API versionada (v1)
10. **Testes Abrangentes**: Estrutura completa de testes (unit, integration, functional, architecture)
11. **Procedure SQL**: Utiliza stored procedure `PrIncluirLancamento` para inserção de lançamentos
12. **Valores Hardcoded**: Alguns valores fixos no código (ex: codigoTransacao=8374, codigoLiquidacao=57)

---