---
## Ficha Técnica do Sistema


### 1. Descrição Geral
Sistema atômico de cancelamento de solicitação de baixa operacional (Write-Off Request Cancel) do SPAG (Sistema de Pagamentos). O serviço expõe uma API REST para consulta de informações de boletos relacionados a baixas operacionais processadas pelo CIP (Câmara Interbancária de Pagamentos), validando status e valor antes de retornar os dados. É utilizado para verificar se um boleto pode ter sua baixa operacional cancelada, aplicando regras de negócio específicas (status processado com sucesso e valor mínimo de R$ 250.000,00).


### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `WriteOffRequestCancelController` | Controlador REST que expõe o endpoint de consulta de boletos |
| `WriteOffRequestCancelService` | Serviço de domínio que implementa as regras de negócio (validação de status e valor) |
| `WriteOffRequestCancelRepository` | Interface de repositório para acesso aos dados |
| `WriteOffRequestCancelRepositoryImpl` | Implementação do repositório usando JDBI para consultas SQL |
| `BilletInfo` | Entidade de domínio representando informações do boleto |
| `BilletRowMapper` | Mapper JDBI para conversão de ResultSet em BilletInfo |
| `BilletInfoMapper` | Mapper para conversão de BilletInfo em BilletInfoRepresentation (DTO) |
| `ExceptionControllerHandler` | Handler centralizado de exceções |
| `WriteOffRequestCancelException` | Exceção customizada de domínio |


### 3. Tecnologias Utilizadas
- **Framework:** Spring Boot 2.x
- **Java:** 11
- **Persistência:** JDBI 3.9.1
- **Banco de Dados:** Microsoft SQL Server (driver 7.4.0.jre11)
- **Documentação API:** Swagger/OpenAPI (Springfox 3.0.0)
- **Segurança:** Spring Security OAuth2 (Resource Server com JWT)
- **Observabilidade:** Spring Boot Actuator, Micrometer Prometheus
- **Monitoramento:** Prometheus + Grafana
- **Pool de Conexões:** HikariCP
- **Testes:** JUnit 5, Mockito, Rest Assured, Pact (contratos)
- **Build:** Maven
- **Container:** Docker (OpenJDK 11 OpenJ9)
- **Orquestração:** OpenShift/Kubernetes


### 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/find/{barcode}/{protocol}` | `WriteOffRequestCancelController` | Busca informações de um boleto por código de barras e protocolo, validando regras de negócio |


### 5. Principais Regras de Negócio
1. **Validação de Status:** O boleto deve ter status igual a 3 (processado com sucesso). Caso contrário, retorna erro 400 com mensagem "Billet was not processed successfully."

2. **Validação de Valor Mínimo:** O valor do boleto deve ser maior ou igual a R$ 250.000,00. Valores inferiores retornam erro 400 com mensagem "Value less than 250 thousand reais."

3. **Validação de Existência:** Se não encontrar dados para os parâmetros informados (protocolo e código de barras), retorna erro 404 com mensagem "No data found for the informed parameter values."

4. **Filtro de Baixa Aceita:** A consulta só retorna boletos cuja baixa operacional foi aceita (FlBaixaOperacionalAceita='S')


### 6. Relação entre Entidades

**BilletInfo** (entidade principal)
- Contém `PaymentInfo` (informações de pagamento: data, valor, código do título, código de barras)
- Contém `IspbInfo` (informações ISPB: recebedor principal e administrado)
- Contém `FinancialInstitution` (instituições financeiras: remetente e favorecido)
- Atributos próprios: writeOffIdentifier, status, value

Relacionamento: BilletInfo agrega PaymentInfo, IspbInfo e FinancialInstitution (composição).


### 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbRetornoBaixaOperacionalCIP | tabela | SELECT | Tabela de retorno de baixas operacionais do CIP |
| TbRegistroPagamentoCIP | tabela | SELECT | Tabela de registros de pagamento do CIP |
| TbLancamento | tabela | SELECT | Tabela de lançamentos contábeis/financeiros |
| TbLancamentoPessoa | tabela | SELECT | Tabela de pessoas relacionadas aos lançamentos (bancos remetente e favorecido) |


### 8. Estruturas de Banco de Dados Atualizadas

não se aplica


### 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | leitura | Configuração de logging | Arquivo de configuração do Logback para logs da aplicação |
| application.yml | leitura | Configuração Spring Boot | Arquivo de configuração da aplicação (datasource, profiles, etc) |
| findBillet.sql | leitura | WriteOffRequestCancelRepositoryImpl | Query SQL para busca de boletos |


### 10. Filas Lidas

não se aplica


### 11. Filas Geradas

não se aplica


### 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| API Gateway (OAuth2/JWT) | Autenticação | Validação de tokens JWT para autenticação e autorização das requisições |
| Banco de Dados DBSPAG (SQL Server) | Persistência | Consulta de dados de baixas operacionais e pagamentos CIP |


### 13. Avaliação da Qualidade do Código

**Nota:** 7,5/10

**Justificativa:**

**Pontos Positivos:**
- Arquitetura hexagonal bem estruturada (separação clara entre domain, application e infrastructure)
- Uso adequado de padrões como Repository, Service e Mapper
- Tratamento de exceções centralizado
- Testes unitários presentes
- Uso de Lombok para reduzir boilerplate
- Configuração adequada de segurança OAuth2
- Observabilidade implementada (Actuator, Prometheus)

**Pontos de Melhoria:**
- Classes de teste vazias (WriteOffRequestCancelConfigurationTest, WriteOffRequestCancelRepositoryImplTest)
- Falta de testes de integração efetivos (classe de teste Pact comentada)
- Logs com concatenação de strings em vez de placeholders parametrizados
- Validação de data com lógica no mapper (validateDate) poderia ser mais robusta
- Falta de documentação JavaDoc em algumas classes
- Uso de "magic numbers" (SUCCESS_STATUS = 3) sem constantes bem nomeadas no contexto de negócio
- Query SQL embutida em arquivo separado, mas sem documentação sobre o modelo de dados


### 14. Observações Relevantes

1. **Ambiente Multi-Profile:** O sistema suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas para cada um.

2. **Segurança:** Implementa OAuth2 Resource Server com validação de JWT, protegendo todos os endpoints exceto actuator, metrics e swagger.

3. **Monitoramento:** Infraestrutura completa de observabilidade com Prometheus e Grafana pré-configurados via Docker Compose.

4. **Arquitetura Limpa:** Segue princípios de Clean Architecture com separação clara entre camadas (domain, application, common).

5. **Padrão Atômico:** Projeto gerado a partir de template de microserviço atômico do Banco Votorantim, seguindo padrões corporativos.

6. **Pipeline CI/CD:** Configurado para Jenkins com propriedades específicas (jenkins.properties) e infraestrutura como código (infra.yml).

7. **Validações de Negócio:** As regras de negócio estão corretamente isoladas na camada de serviço (domain), facilitando manutenção e testes.

8. **Conexão com Banco:** Utiliza JDBI em vez de JPA/Hibernate, oferecendo maior controle sobre as queries SQL e melhor performance para operações de leitura.