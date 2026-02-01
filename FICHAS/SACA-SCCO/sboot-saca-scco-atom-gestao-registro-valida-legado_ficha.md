---
## Ficha Técnica do Sistema

### 1. Descrição Geral
Sistema atômico de validação de restrições de registro de boletos para contratos legados. O serviço verifica se um contrato ou parcela possui restrições que impedem o registro de boletos, consultando bases de dados legadas do sistema SACA/SCCO. A aplicação expõe uma API REST que recebe o código nosso número e número do contrato, retornando indicadores booleanos sobre a existência de restrições.

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot que inicializa a aplicação |
| `RestricaoRegistroBoletoController` | Controlador REST que expõe o endpoint de validação de restrições |
| `GestaoRegistroValidaLegadoService` | Serviço de domínio que orquestra as validações de restrições |
| `RestricaoRegistroBoletoValidator` | Validador de parâmetros de entrada e regras de negócio |
| `JdbiGestaoRegistroValidaLegadoRepository` | Interface de repositório JDBI para acesso aos dados |
| `GestaoRegistroValidaLegadoConfiguration` | Configuração do JDBI e beans do Spring |
| `OpenApiConfiguration` | Configuração do Swagger/OpenAPI para documentação |
| `GestaoRegistroValidaLegado` | Entidade de domínio (aparentemente não utilizada no fluxo principal) |
| `GestaoRegistroValidaLegadoException` | Exceção customizada de domínio |

### 3. Tecnologias Utilizadas
- **Framework:** Spring Boot 2.x
- **Linguagem:** Java 11
- **Acesso a Dados:** JDBI 3.9.1 com SQL Object Plugin e StringTemplate4
- **Banco de Dados:** Sybase ASE (driver jConnect 16.3)
- **Segurança:** Spring Security OAuth2 Resource Server com JWT
- **Documentação:** Swagger/Springfox 2.9.2
- **Monitoramento:** Spring Boot Actuator com Micrometer Prometheus
- **Auditoria:** springboot-arqt-base-trilha-auditoria-web 2.2.1
- **Logging:** Logback com formato JSON
- **Testes:** JUnit 5, Mockito, RestAssured, Pact
- **Build:** Maven
- **Containerização:** Docker
- **Orquestração:** Kubernetes/OpenShift

### 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | /v1/restricaoRegistroBoleto | RestricaoRegistroBoletoController | Valida restrições de contrato e parcela para registro de boleto. Parâmetros: codigoNossoNumero (Long), numeroContrato (Long). Retorna indicadores booleanos de restrição. |

### 5. Principais Regras de Negócio
1. **Validação de Parâmetros Obrigatórios:** O código nosso número e número do contrato devem ser informados obrigatoriamente (retorna HTTP 400 se ausentes).

2. **Validação de Existência do Contrato:** O contrato deve existir na base de dados (retorna HTTP 404 se não localizado).

3. **Restrição de Contrato:** Um contrato possui restrição se estiver liquidado (DtLiquidacaoEfetiva IS NOT NULL) ou cancelado (DtCancelamento IS NOT NULL).

4. **Restrição de Parcela:** Uma parcela possui restrição se estiver quitada (StParcela = 'Q') e associada ao registro de instrumento de cobrança correspondente.

5. **Identificação Dinâmica do Banco de Dados:** O sistema identifica dinamicamente qual banco de dados legado deve ser consultado com base no número do contrato, através da tabela de conexões (DBCOR..TbConexao).

### 6. Relação entre Entidades
- **TbConexao (DBCOR):** Armazena informações de conexão com bancos de dados legados, incluindo o nome do banco (NmBancoDados).
- **TbProduto (DBCOR):** Relaciona produtos com conexões de banco de dados.
- **TbContratoPrincipal (DBCOR):** Armazena contratos principais e seus produtos associados.
- **TbContrato (bancos legados):** Contém informações de contratos, incluindo datas de liquidação e cancelamento.
- **TbParcela (bancos legados):** Armazena parcelas de contratos com status (StParcela).
- **TbRegistroInstrumentoCobranca (DBCARNE):** Registra instrumentos de cobrança (boletos) com código nosso número.

**Relacionamentos:**
- TbConexao 1:N TbProduto (via NuConexao)
- TbProduto 1:N TbContratoPrincipal (via CdProduto)
- TbContratoPrincipal 1:1 TbContrato (via NuContrato, em banco dinâmico)
- TbContrato 1:N TbParcela (via NuContrato e SqContratoFinanceiro)
- TbRegistroInstrumentoCobranca N:1 TbParcela (via NuContratoGestao, NuParcela, SqContratoFinanceiro)

### 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBCOR..TbConexao | Tabela | SELECT | Consulta o nome do banco de dados legado associado ao contrato |
| DBCOR..TbProduto | Tabela | SELECT | Relaciona produtos com conexões de banco de dados |
| DBCOR..TbContratoPrincipal | Tabela | SELECT | Identifica o produto do contrato principal |
| [nmBancoDados]..TbContrato | Tabela | SELECT | Verifica se o contrato está liquidado ou cancelado (banco dinâmico) |
| [nmBancoDados]..TbParcela | Tabela | SELECT | Verifica se a parcela está quitada (banco dinâmico) |
| DBCARNE..TbRegistroInstrumentoCobranca | Tabela | SELECT | Relaciona código nosso número com parcelas |

### 8. Estruturas de Banco de Dados Atualizadas
não se aplica

### 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | Spring Boot | Configurações da aplicação (datasource, servidor, segurança) |
| logback-spring.xml | Leitura | Logback | Configuração de logs em formato JSON |
| sboot-saca-scco-atom-gestao-registro-valida-legado.yaml | Leitura | Swagger Codegen | Especificação OpenAPI para geração de interfaces |

### 10. Filas Lidas
não se aplica

### 11. Filas Geradas
não se aplica

### 12. Integrações Externas
1. **Banco de Dados Sybase (DBCOR):** Consulta metadados de contratos e conexões para identificar o banco de dados legado correto.

2. **Bancos de Dados Legados (dinâmicos):** Consulta informações de contratos e parcelas em múltiplos bancos de dados identificados dinamicamente (ex: DBGESTAOCDCSG).

3. **Banco de Dados DBCARNE:** Consulta registros de instrumentos de cobrança (boletos).

4. **Servidor OAuth2/JWT:** Validação de tokens JWT para autenticação e autorização (configurado via JWT_URI).

5. **Prometheus:** Exportação de métricas de monitoramento via endpoint /actuator/prometheus.

### 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões de microserviços atômicos com separação clara de responsabilidades (domain, application, common)
- Uso adequado de injeção de dependências e inversão de controle
- Implementação de validações de entrada e tratamento de erros
- Boa cobertura de testes unitários e estrutura para testes de integração/funcionais
- Configuração adequada de segurança OAuth2/JWT
- Documentação OpenAPI/Swagger implementada
- Uso de JDBI para acesso a dados com queries SQL externalizadas
- Configuração de observabilidade (Actuator, Prometheus, Grafana)

**Pontos de Melhoria:**
- A entidade de domínio `GestaoRegistroValidaLegado` parece não ser utilizada no fluxo principal, indicando possível código morto
- Falta de tratamento de exceções mais específico (uso genérico de Exception)
- Queries SQL com concatenação dinâmica de nome de banco de dados podem representar risco de segurança se não validadas adequadamente
- Ausência de cache para consultas repetitivas ao banco de metadados
- Testes funcionais e de integração estão vazios/comentados
- Falta de logs estruturados em pontos críticos do fluxo
- Documentação inline (JavaDoc) ausente ou muito básica
- Validação de entrada poderia ser mais robusta (uso de Bean Validation)

### 14. Observações Relevantes

1. **Arquitetura Multi-Tenant de Banco de Dados:** O sistema implementa uma estratégia interessante de identificação dinâmica do banco de dados legado baseada no contrato, permitindo consultar múltiplos bancos de dados sem hardcoding.

2. **Segurança:** A aplicação está configurada como Resource Server OAuth2, exigindo token JWT válido para acesso aos endpoints.

3. **Ambientes:** Suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas de datasource e segurança.

4. **Monitoramento:** Infraestrutura completa de observabilidade com Prometheus e Grafana configurados via Docker Compose.

5. **Pipeline CI/CD:** Configurado para Jenkins com propriedades específicas (jenkins.properties) e infraestrutura como código (infra.yml).

6. **Padrões Corporativos:** Utiliza bibliotecas corporativas do Banco Votorantim (arqt-base) para segurança, auditoria e tratamento de erros.

7. **Testes de Contrato:** Estrutura preparada para testes de contrato com Pact, embora não implementados.

8. **Limitações:** O sistema depende fortemente da estrutura de bancos de dados legados Sybase, o que pode dificultar manutenção e evolução futura.