# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-spag-base-atom-integracao-tributo-pix** é um serviço atômico (microserviço) desenvolvido em Spring Boot para integração de pagamentos de tributos via PIX. Sua principal função é receber notificações de sucesso ou falha de transações PIX relacionadas a pagamentos de tributos e atualizar o status dessas transações no banco de dados. O sistema expõe endpoints REST para receber callbacks de processamento de pagamentos PIX, atualizando registros na tabela `TbLotePagamentoTributo` com informações sobre o resultado do processamento (sucesso ou falha) e mensagens associadas.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal de inicialização da aplicação Spring Boot |
| `IntegracaoTributoPix` | Entidade de domínio que representa um lote de pagamento de tributo, mapeada para a tabela `TbLotePagamentoTributo` |
| `IntegracaoTributoPixRepository` | Interface de repositório JPA para acesso aos dados de integração de tributo PIX |
| `IntegracaoTributoPixService` | Serviço de domínio responsável pela lógica de negócio de atualização de status de pagamentos (sucesso/falha) |
| `IntegracaoTributoPixSuccessApiDelegateImpl` | Implementação do delegate REST para processar notificações de sucesso |
| `IntegracaoTributoPixFailApiDelegateImpl` | Implementação do delegate REST para processar notificações de falha |
| `IntegracaoTributoPixConfiguration` | Classe de configuração Spring para criação de beans do domínio |
| `BusinessActionConfiguration` | Configuração para trilha de auditoria |
| `DefinidorBusinessActionCustom` | Implementação customizada para definição de business actions na trilha de auditoria |
| `ElementNotFoundException` | Exception customizada para indicar que um elemento não foi encontrado (HTTP 404) |

---

## 3. Tecnologias Utilizadas

- **Spring Boot** - Framework principal para desenvolvimento do microserviço
- **Spring Data JPA** - Persistência e acesso a dados
- **Hibernate** - ORM (Object-Relational Mapping)
- **Microsoft SQL Server** - Banco de dados relacional (driver mssql-jdbc 7.4.0.jre11)
- **Maven** - Gerenciamento de dependências e build
- **Lombok** - Redução de código boilerplate
- **OpenAPI 3.0 / Swagger** - Documentação de API
- **Spring Security OAuth2** - Segurança com JWT
- **Logback** - Framework de logging
- **Docker** - Containerização
- **OpenJ9 JDK 11** - Runtime Java
- **Actuator** - Monitoramento e métricas
- **Atlante Base** - Framework corporativo Banco Votorantim (pom-atle-base-sboot-atom-parent 1.1.15)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| PATCH | `/integracao-tributo-pix-success/{transactionId}` | `IntegracaoTributoPixSuccessApiDelegateImpl` | Recebe notificação de sucesso de processamento PIX e atualiza o registro correspondente |
| PATCH | `/integracao-tributo-pix-fail/{transactionId}` | `IntegracaoTributoPixFailApiDelegateImpl` | Recebe notificação de falha de processamento PIX e atualiza o registro correspondente |

**Observação:** Ambos os endpoints requerem autenticação via Bearer Token JWT e recebem um objeto `MessagePix` no corpo da requisição contendo a mensagem de retorno (1-250 caracteres).

---

## 5. Principais Regras de Negócio

1. **Atualização de Status de Sucesso**: Quando uma transação PIX é processada com sucesso, o sistema localiza o registro pelo `transactionId`, atualiza o campo `FlProcessadoPix` para "S", registra a mensagem recebida no campo `DsMensagemRetornoPix` e atualiza o timestamp `DtAlteracao`.

2. **Atualização de Status de Falha**: Quando uma transação PIX falha no processamento, o sistema localiza o registro pelo `transactionId`, atualiza o campo `FlProcessadoPix` para "N", registra a mensagem de erro no campo `DsMensagemRetornoPix` e atualiza o timestamp `DtAlteracao`.

3. **Validação de Existência**: Antes de qualquer atualização, o sistema valida se existe um registro com o `transactionId` informado. Caso não exista, retorna HTTP 404 com a mensagem "Pagamento não encontrado".

4. **Idempotência**: O sistema permite múltiplas chamadas para o mesmo `transactionId`, sempre atualizando o registro com as informações mais recentes.

---

## 6. Relação entre Entidades

O sistema possui uma única entidade principal:

**IntegracaoTributoPix**
- Representa um lote de pagamento de tributo via PIX
- Mapeada para a tabela `TbLotePagamentoTributo`
- Chave primária: `CdLotePagamentoTributo` (id)
- Possui identificador único de transação: `CdUnicoIdentificadorTransacao` (transactionId)
- Contém informações de conta (agência, banco, conta, tipo de conta)
- Contém informações do favorecido (CPF/CNPJ, nome, tipo de pessoa)
- Contém informações de controle (status, parâmetro, protocolo, liquidação)
- Contém informações de processamento PIX (flag processado, mensagem de retorno)
- Contém timestamps de auditoria (inclusão e alteração)

**Relacionamento:** Não há relacionamentos explícitos com outras entidades no código fornecido. A entidade é autocontida.

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbLotePagamentoTributo | Tabela | SELECT | Tabela de lotes de pagamento de tributos, consultada para localizar registros pelo identificador único de transação (CdUnicoIdentificadorTransacao) |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbLotePagamentoTributo | Tabela | UPDATE | Atualização dos campos FlProcessadoPix (flag de processamento), DsMensagemRetornoPix (mensagem de retorno) e DtAlteracao (timestamp de alteração) após recebimento de callback de sucesso ou falha do processamento PIX |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| openapi.yaml | Leitura | `src/main/resources/swagger/` | Contrato OpenAPI 3.0 que define a especificação dos endpoints REST |
| application.yml | Leitura | `src/main/resources/` | Arquivo de configuração principal da aplicação Spring Boot para ambientes des/uat/prd |
| application-local.yml | Leitura | `src/main/resources/` | Arquivo de configuração específico para ambiente local de desenvolvimento |
| logback-spring.xml | Leitura | `src/main/resources/` e `/usr/etc/log/` | Arquivo de configuração de logs da aplicação |
| bootstrap.sh | Leitura/Execução | `docker/utils/` | Script de inicialização do container Docker com gerenciamento de retry e timeout |

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

---

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| API Gateway BV | Autenticação | Integração com serviço de autenticação OAuth2/JWT do Banco Votorantim para validação de tokens (jwks.json) |
| Sistema de Processamento PIX | Callback | Recebe callbacks de sistemas externos que processam transações PIX, notificando sucesso ou falha |
| SQL Server (DBSPAG) | Banco de Dados | Conexão com banco de dados corporativo para persistência de dados de pagamentos de tributos |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Código bem estruturado seguindo padrões de arquitetura em camadas (domain, repository, service, rest)
- Uso adequado de anotações Lombok reduzindo boilerplate
- Separação clara de responsabilidades entre camadas
- Uso de Contract-First com OpenAPI para definição de APIs
- Configuração adequada para múltiplos ambientes
- Tratamento de exceções customizado
- Uso de Optional para evitar NullPointerException
- Documentação básica presente (README.md)
- Configuração de segurança com JWT
- Uso de padrão Builder para entidades

**Pontos de Melhoria:**
- Falta de testes unitários implementados (arquivos de teste existem mas não foram fornecidos)
- Ausência de validações mais robustas nos campos de entrada
- Falta de logs mais detalhados nas operações críticas
- Classe `DefinidorBusinessActionCustom` possui lógica hardcoded que poderia ser configurável
- Ausência de tratamento de transações explícito (@Transactional)
- Falta de documentação JavaDoc nas classes e métodos
- Mensagens de erro poderiam ser mais descritivas e internacionalizadas

O código demonstra boas práticas de desenvolvimento, mas há espaço para melhorias em testes, documentação e robustez.

---

## 14. Observações Relevantes

1. **Arquitetura Corporativa**: O projeto segue o padrão de microserviços atômicos do Banco Votorantim, utilizando o framework Atlante Base como parent POM.

2. **Deployment**: A aplicação está preparada para deployment em OpenShift (OCP) na plataforma Google Cloud, conforme indicado no arquivo `jenkins.properties`.

3. **Monitoramento**: Possui endpoints Actuator expostos na porta 9090 para health checks, métricas e Prometheus.

4. **Segurança**: Todos os endpoints (exceto públicos configurados) requerem autenticação via Bearer Token JWT validado contra o API Gateway do Banco Votorantim.

5. **Ambientes**: Suporta múltiplos ambientes (local, des, uat, prd) com configurações específicas gerenciadas via arquivo `infra.yml`.

6. **Naming Strategy**: Utiliza `PhysicalNamingStrategyStandardImpl` do Hibernate, mantendo os nomes das colunas exatamente como definidos nas anotações JPA.

7. **Retry Mechanism**: O script `bootstrap.sh` implementa mecanismo de retry para conexões e carregamento de metadados durante a inicialização do container.

8. **Limitações de Recursos**: Container configurado com limites de CPU (750m) e memória (512Mi) e requests de CPU (150m) e memória (256Mi).

9. **JVM Tuning**: Configurado com OpenJ9 e parâmetros de memória otimizados (MaxRAMPercentage=70, MinRAMPercentage=70, InitialRAMPercentage=50).

10. **Versionamento**: Projeto na versão 0.2.0, indicando estar em fase inicial de desenvolvimento/estabilização.