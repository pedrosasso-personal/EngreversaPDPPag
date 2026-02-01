---
## Ficha Técnica do Sistema


### 1. Descrição Geral
Sistema atômico responsável pelo gerenciamento de exceções relacionadas a transações de débito em cartões. O sistema recebe dados de transações que geraram exceções, armazena essas informações em banco de dados SQL Server e permite consultas e atualizações posteriores. Originalmente preparado para consumir mensagens de filas PubSub (Google Cloud), mas atualmente com essa funcionalidade desabilitada. O sistema faz parte do domínio CCBD (Cartão de Crédito e Débito) do Banco Votorantim.


### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application.java` | Classe principal Spring Boot que inicializa a aplicação |
| `DebAdviceExceptionServiceImpl` | Implementa a lógica de negócio para salvar, consultar e atualizar exceções de débito |
| `CCBDRepositoryImpl` | Interface JDBI que define operações de banco de dados (insert, select, update) |
| `DebAdviceExceptionMapper` | Mapeia ResultSet do banco de dados para objetos de domínio |
| `QuotesConsumer` | Consumidor de mensagens (atualmente desabilitado/comentado) |
| `DebAdviceDadosExceptionDTO` | DTO para recebimento de dados de exceção |
| `DebAdviceExceptionResponse` | Objeto de resposta com dados da exceção consultada |
| `DataBaseConfiguration` | Configuração do datasource e JDBI |
| `DebAdviceExceptionConfiguration` | Configuração de beans do domínio |


### 3. Tecnologias Utilizadas
- **Framework:** Spring Boot 2.x
- **Linguagem:** Java 11
- **Persistência:** JDBI 3.9.1
- **Banco de Dados:** Microsoft SQL Server (driver 7.2.2.jre11)
- **Documentação API:** Swagger/Springfox 3.0.0
- **Segurança:** Spring Security OAuth2 (JWT)
- **Monitoramento:** Spring Actuator, Micrometer, Prometheus
- **Observabilidade:** Grafana (configurado via docker-compose)
- **Build:** Maven 3.3+
- **Mensageria:** Spring Cloud GCP PubSub (código presente mas desabilitado)
- **Auditoria:** BV Audit 2.3.2
- **Testes:** JUnit 5, Mockito, Rest Assured, Pact


### 4. Principais Endpoints REST
não se aplica

(O sistema não expõe endpoints REST públicos. A classe `DebAdviceExceptionRepresentation` existe mas não há controllers implementados. O sistema foi projetado para consumir mensagens de filas.)


### 5. Principais Regras de Negócio
1. **Salvamento de Exceção:** Ao receber dados de uma transação com exceção, o sistema insere um novo registro na tabela `TbControleExcecaoDebito` com todos os detalhes da transação (conta, cartão, estabelecimento, valores, códigos de resposta, etc.)

2. **Consulta de Exceção Existente:** Busca exceções baseando-se em 8 critérios: número da conta remetente, identificador da transação, código de status do autorizador, código da transação, código de processamento, código da moeda, valor da transação e código do autorizador

3. **Atualização de Exceção:** Se a exceção já existe, atualiza campos como descrição da alteração, flag ativo, descrição da exceção e requisição de débito

4. **Tratamento de Descrição de Alteração:** Utiliza enum `DescricaoAlteracaoTabelaExcecaoEnum` para mapear códigos de status em descrições padronizadas (ex: "00" = tentativa de confirmação de débito, "87" = saque parcial, "E4" = desbloqueio de saldo)

5. **Validação de Descrição de Exceção:** Se não houver descrição e o código não for "E4", utiliza descrição padrão "Exceção não capturada". Para código "E4", força descrição de desbloqueio de saldo

6. **Limitação de Tamanho:** Descrição de exceção é truncada em 299 caracteres

7. **Valores Padrão:** Campos nulos são substituídos por valores padrão (zero para numéricos, data padrão "2023-01-01" para datas ausentes)


### 6. Relação entre Entidades

**Entidades Principais:**

- **DebAdviceDadosException:** Entidade completa com todos os dados da exceção para persistência
- **DebAdviceDadosExceptionDTO:** DTO de entrada com dados da transação problemática
- **DebAdviceExceptionResponse:** Entidade de resposta com dados consultados do banco
- **Cartao:** Dados do cartão (produto, conta, correlativo, indicador wallet)
- **Estabelecimento:** Dados do estabelecimento comercial (código, tipo, nome, cidade, país, CEP)
- **TrilhaDadosCartao:** Dados da trilha do cartão (número mascarado, expiração, código de serviço)

**Relacionamentos:**
- DebAdviceDadosExceptionDTO contém (composição) Cartao, Estabelecimento e TrilhaDadosCartao
- DebAdviceDadosException é mapeado a partir de DebAdviceDadosExceptionDTO para persistência
- DebAdviceExceptionResponse é resultado de consulta e pode ser atualizado


### 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| CCBDTransacaoCartaoDebito.TbControleExcecaoDebito | tabela | SELECT | Consulta exceções de débito por múltiplos critérios (conta, transação, status, valores) |


### 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| CCBDTransacaoCartaoDebito.TbControleExcecaoDebito | tabela | INSERT | Insere novos registros de exceção com dados completos da transação |
| CCBDTransacaoCartaoDebito.TbControleExcecaoDebito | tabela | UPDATE | Atualiza registros existentes (data alteração, descrição, flag ativo, requisição) |


### 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot / resources | Configurações da aplicação por ambiente (local, des, qa, uat, prd) |
| logback-spring.xml | leitura | Logback / resources | Configuração de logs em formato JSON |


### 10. Filas Lidas
**Configuração presente mas desabilitada:**
- Subscription: `business-cart-base-cartao-debito-advice-exception-messages-dql-sub` (projeto GCP: bv-cart-{des|uat|prd})
- Classe consumidora: `QuotesConsumer` (código comentado)
- Canal: `quotesInputChannel`


### 11. Filas Geradas
**Configuração presente mas desabilitada:**
- Topic: `business-cart-base-cartao-debito-advice-dql` (projeto GCP: bv-cart-{des|uat|prd})
- Canal: `quotesOutputChannel`
- Gateway: `QuotesGateway` (código comentado)


### 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| SQL Server (DBCCBD) | Banco de Dados | Banco principal para persistência de exceções (SQLDES35, SQLUAT35, SQLPRD35) |
| API Gateway BV | Autenticação | Geração de tokens JWT para autenticação (endpoints por ambiente) |
| OpenID Connect | Segurança | Validação de tokens JWT via JWKS |
| Google Cloud PubSub | Mensageria | Integração preparada mas desabilitada para consumo/publicação de mensagens |


### 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades em camadas (domain, application)
- Uso adequado de padrões como Repository, Service, DTO
- Configuração bem estruturada por ambientes
- Uso de JDBI com SQL externalizado facilita manutenção
- Enums para padronização de descrições
- Tratamento de valores nulos com defaults
- Configuração de observabilidade (Prometheus/Grafana)

**Pontos de Melhoria:**
- Código de integração PubSub comentado ao invés de removido ou isolado em feature toggle
- Falta de validações de entrada nos DTOs
- Método `pesquisaDescricaoExcecao` com lógica condicional que poderia ser simplificada
- Conversão de objeto para String via `toString()` para persistência (campo `dsRequisicaoDebito`) pode gerar problemas de tamanho
- Falta de tratamento de exceções específicas (apenas genérico)
- Ausência de logs estruturados em pontos críticos
- Classe `DebAdviceExceptionRepresentation` não utilizada
- Constantes mágicas (299 para truncamento, "2023-01-01" como data padrão)


### 14. Observações Relevantes

1. **Sistema em Transição:** O código contém infraestrutura completa para Google Cloud PubSub, mas está totalmente desabilitada via comentários, sugerindo que o sistema pode ter migrado de arquitetura orientada a eventos para outro modelo

2. **Ambientes Múltiplos:** Configuração robusta para 5 ambientes (local, des, qa, uat, prd) com credenciais gerenciadas via cofre de senhas

3. **Segurança:** Implementa OAuth2 com JWT, mas endpoints não estão expostos (sistema interno)

4. **Monitoramento:** Infraestrutura completa de observabilidade com Prometheus e Grafana configurados via Docker Compose

5. **Arquitetura Hexagonal:** Segue padrões de ports/adapters com separação clara entre domínio e infraestrutura

6. **Banco de Dados:** Utiliza JDBI ao invés de JPA/Hibernate, indicando preferência por controle fino sobre SQL

7. **Testes:** Estrutura preparada para testes unitários, integração e funcionais, além de testes de contrato com Pact

8. **Deploy:** Preparado para Kubernetes/OpenShift com configurações de health checks, service accounts e variáveis de ambiente

9. **Limitação de Caracteres:** Campo de descrição de exceção limitado a 299 caracteres pode causar perda de informação em mensagens longas

10. **Data Padrão:** Uso de "2023-01-01" como data padrão pode gerar confusão em análises futuras