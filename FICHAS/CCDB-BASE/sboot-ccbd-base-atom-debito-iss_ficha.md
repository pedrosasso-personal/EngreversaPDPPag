---
## Ficha Técnica do Sistema


### 1. Descrição Geral
Sistema atômico responsável por gerenciar a cobrança de ISS (Imposto Sobre Serviços) de transações de cartão de débito do Banco Digital. O sistema expõe APIs REST para consulta de transações por protocolo e registro de dados de ISS em lotes, armazenando informações no banco de dados DBCCBD para posterior geração de arquivos de cobrança.


### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot que inicializa a aplicação |
| `DebitoIssController` | Controlador REST que expõe endpoints para consulta e registro de transações ISS |
| `DebitoIssService` / `DebitoIssServiceImpl` | Camada de serviço contendo lógica de negócio para recuperação de transações e inserção de registros ISS |
| `CCBDRepository` / `CCBDRepositoryImpl` | Interface e implementação de acesso a dados usando JDBI |
| `DebitoIssMapper` | Classe utilitária para conversão entre objetos de domínio e representações REST |
| `ResourceExceptionHandler` | Tratamento centralizado de exceções da aplicação |
| `Transacao` | Entidade de domínio representando uma transação de débito |
| `Iss` | Entidade de domínio representando dados de ISS |
| `LoteIss` | Entidade de domínio representando um lote de registros ISS |
| `DataBaseConfiguration` | Configuração de conexão com banco de dados e JDBI |
| `DebitoIssConfiguration` | Configuração de beans do domínio |
| `OpenApiConfiguration` | Configuração do Swagger/OpenAPI |


### 3. Tecnologias Utilizadas
- **Framework:** Spring Boot 2.x
- **Linguagem:** Java 11
- **Persistência:** JDBI 3.9.1
- **Banco de Dados:** Microsoft SQL Server (driver mssql-jdbc 7.4.0)
- **Documentação API:** Swagger 2.9.2 / Springfox
- **Segurança:** Spring Security OAuth2 (Resource Server com JWT)
- **Monitoramento:** Spring Boot Actuator, Micrometer Prometheus
- **Observabilidade:** Grafana, Prometheus
- **Build:** Maven
- **Containerização:** Docker
- **Orquestração:** OpenShift/Kubernetes
- **Auditoria:** springboot-arqt-base-trilha-auditoria-web 2.2.1
- **Testes:** JUnit 5, Rest Assured, Pact (testes de contrato)
- **Gerenciamento de Dependências:** Lombok


### 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/banco-digital/debito/transacao-iss/{nuProtocolo}` | `DebitoIssController` | Consulta transação de débito por número de protocolo SPAG |
| POST | `/v1/banco-digital/debito/transacao-iss` | `DebitoIssController` | Registra dados de ISS de uma transação em um lote |


### 5. Principais Regras de Negócio
1. **Consulta de Transação por Protocolo:** Recupera informações detalhadas de uma transação de débito (valor, fee, estabelecimento, cartão mascarado, etc.) através do número de protocolo SPAG.

2. **Gestão de Lotes ISS:** Ao inserir um registro ISS, o sistema verifica se existe um lote ativo (status 'A') com data final maior ou igual à data atual. Se não existir, cria um novo lote com UUID único.

3. **Validação de Transação:** Lança exceção `TransacaoNaoEncontradaException` quando a transação não é encontrada pelo protocolo informado.

4. **Registro de ISS:** Armazena dados completos da transação incluindo informações do cliente (nome, documento, endereço), estabelecimento (nome, endereço), valores (transação, fee), dados do cartão e tipo de operação.

5. **Auditoria:** Todos os registros são marcados com login 'CCBD_DEBITOISS' e timestamps de inclusão.


### 6. Relação entre Entidades

**Entidades principais:**

- **Transacao:** Representa uma transação de cartão de débito com dados como banco, conta, valor, estabelecimento, cartão mascarado, autorizador, fee, tipo de transação e flag de cartão presente.

- **LoteIss:** Representa um lote de registros ISS com número de lote único (UUID).

- **Iss:** Representa um registro de ISS vinculado a um lote, contendo dados completos do cliente (nome, documento, endereço), estabelecimento (nome, endereço), transação (valores, datas, referências) e tipo de operação.

**Relacionamentos:**
- Um `LoteIss` pode conter múltiplos registros `Iss` (relacionamento 1:N)
- Cada `Iss` está associado a um `LoteIss` através do campo `cdLoteIss`


### 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| `DBCCBD.CCBDTransacaoCartaoDebito.TbLoteIss` | tabela | SELECT | Consulta lote ISS ativo para verificar existência de lote em aberto |
| `DBCCBD.CCBDTransacaoCartaoDebito.TbControleTransacaoCartao` | tabela | SELECT | Tabela principal de controle de transações de cartão |
| `DBCCBD.CCBDTransacaoCartaoDebito.TbTransacaoCartao` | tabela | SELECT | Dados específicos da transação do cartão (cartão mascarado) |
| `DBCCBD.CCBDTransacaoCartaoDebito.TbEstabelecimentoComercial` | tabela | SELECT | Informações do estabelecimento comercial onde ocorreu a transação |
| `DBCCBD.CCBDTransacaoCartaoDebito.TbConciliacaoTransacao` | tabela | SELECT | Dados de conciliação incluindo valor do fee |
| `DBCCBD.CCBDTransacaoCartaoDebito.TbTipoTransacao` | tabela | SELECT | Tipo da transação realizada |
| `DBCCBD.CCBDTransacaoCartaoDebito.TbArquivoOrigem` | tabela | SELECT | Origem do arquivo da transação (com filtro para excluir TIF e FORMC30) |


### 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| `DBCCBD.CCBDTransacaoCartaoDebito.TbLoteIss` | tabela | INSERT | Criação de novo lote ISS quando não existe lote ativo |
| `DBCCBD.CCBDTransacaoCartaoDebito.TbDetalheLoteIss` | tabela | INSERT | Inserção de registro detalhado de ISS no lote |


### 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `application.yml` | leitura | Spring Boot | Arquivo de configuração da aplicação com profiles (local, des, qa, uat, prd) |
| `logback-spring.xml` | leitura | Logback | Configuração de logs da aplicação |
| `*.sql` (findIdLoteIss, findTransacaoByNuProtocolo, insertLoteIss, insertRegistroIss) | leitura | CCBDRepositoryImpl (JDBI) | Arquivos SQL para operações de banco de dados |
| `sboot-ccbd-base-atom-debito-iss.yaml` | leitura | Swagger Codegen | Especificação OpenAPI para geração de interfaces REST |
| `sboot-ccbd-base-atom-debito-iss.jar` | gravação | Maven Build | Artefato executável gerado no processo de build |


### 10. Filas Lidas
não se aplica


### 11. Filas Geradas
não se aplica


### 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Banco de Dados SQL Server (DBCCBD) | Banco de Dados | Banco de dados principal para persistência de transações e lotes ISS |
| Servidor OAuth2/JWT | Autenticação | Validação de tokens JWT para autenticação e autorização (URLs variam por ambiente: des, uat, prd) |
| Prometheus | Monitoramento | Exportação de métricas da aplicação |
| Grafana | Visualização | Dashboards de monitoramento (configurado via docker-compose) |


### 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem organizada seguindo padrões hexagonais (domain, application, infrastructure)
- Separação clara de responsabilidades entre camadas
- Uso adequado de padrões como Repository, Service, Mapper
- Configuração de segurança OAuth2/JWT implementada
- Testes unitários e funcionais estruturados
- Documentação OpenAPI/Swagger bem definida
- Uso de Lombok para redução de boilerplate
- Configuração de observabilidade (Actuator, Prometheus, Grafana)
- Suporte a múltiplos ambientes via profiles

**Pontos de Melhoria:**
- Testes unitários com implementação mínima (classes vazias ou com mocks básicos)
- Falta de tratamento de exceções mais granular (apenas uma exceção customizada)
- Queries SQL embutidas em arquivos separados (boa prática), mas sem paginação ou otimizações evidentes
- Ausência de cache para consultas frequentes
- Falta de validações de entrada mais robustas nos endpoints
- Documentação inline (JavaDoc) ausente na maioria das classes
- Configuração de segurança básica sem customizações avançadas


### 14. Observações Relevantes

1. **Ambiente e Deploy:** O sistema está preparado para deploy em OpenShift/Kubernetes com configurações de infraestrutura como código (infra.yml) e suporte a múltiplos ambientes (des, qa, uat, prd).

2. **Monitoramento:** Infraestrutura completa de observabilidade com Prometheus e Grafana configurados via Docker Compose para ambiente local.

3. **Segurança:** Implementa Resource Server OAuth2 com validação de JWT, mas os endpoints de actuator estão expostos sem autenticação (porta 9090).

4. **Banco de Dados:** Utiliza JDBI ao invés de JPA/Hibernate, o que oferece mais controle sobre SQL mas requer mais código manual.

5. **Versionamento de API:** Utiliza versionamento via path (`/v1/`), seguindo boas práticas REST.

6. **Auditoria:** Integração com biblioteca de auditoria do Banco Votorantim (springboot-arqt-base-trilha-auditoria-web).

7. **Arquitetura de Testes:** Estrutura organizada com separação de testes unitários, integração e funcionais em diretórios distintos.

8. **Geração de Código:** Utiliza Swagger Codegen Maven Plugin para gerar interfaces de API a partir da especificação OpenAPI.

9. **Padrão de Nomenclatura:** Segue convenções do Banco Votorantim com prefixos como `sboot-ccbd-base-atom-` para identificação de componentes.

10. **Gestão de Lotes:** Implementa lógica de lote ativo com controle de data, criando novos lotes automaticamente quando necessário.