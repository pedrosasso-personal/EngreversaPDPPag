# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-spag-base-atom-movimento-pagamento** é um serviço atômico Spring Boot responsável por consolidar e armazenar informações de movimentos de pagamento por dia no sistema SPAG (Sistema de Pagamentos). O sistema recebe listas de informações de pagamentos através de uma API REST, remove registros anteriores da mesma data (se existirem) e insere os novos dados consolidados na tabela `tbpagamentomovimentodia`. Trata-se de um componente de backend que processa dados de pagamentos agrupados por origem, liquidação e remetente.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot que inicializa a aplicação com segurança OAuth2 habilitada |
| `MovimentoPagamentoController` | Controller REST que expõe o endpoint para receber informações de pagamentos |
| `MovimentoPagamentoService` | Serviço de domínio que orquestra a lógica de negócio de inserção de movimentos |
| `MovimentoPagamentoRepositoryImpl` | Implementação do repositório usando JDBI para acesso ao banco de dados |
| `MovimentoPagamento` | Entidade de domínio representando um movimento de pagamento |
| `JdbiConfiguration` | Configuração do JDBI para acesso a dados |
| `ModelMapperConfiguration` | Configuração do ModelMapper para conversão entre objetos |
| `MovimentoPagamentoConfiguration` | Configuração de beans do domínio MovimentoPagamento |
| `OpenApiConfiguration` | Configuração do Swagger/OpenAPI para documentação da API |

---

## 3. Tecnologias Utilizadas

- **Spring Boot** (framework principal)
- **Spring Security OAuth2** (autenticação e autorização via JWT)
- **JDBI 3.9.1** (acesso a banco de dados)
- **SQL Server** (banco de dados)
- **ModelMapper 2.3.7** (mapeamento de objetos)
- **Swagger/Springfox 2.9.2** (documentação de API)
- **Lombok** (redução de boilerplate)
- **Spring Boot Actuator** (monitoramento e métricas)
- **Micrometer Prometheus** (métricas)
- **Logback** (logging)
- **JUnit 5 + Mockito** (testes unitários)
- **Rest Assured** (testes funcionais)
- **Pact** (testes de contrato)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **OpenShift/Kubernetes** (orquestração)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/movimenta-pagamento/` | `MovimentoPagamentoController` | Recebe lista de informações de pagamentos consolidados por dia e persiste no banco de dados |

**Parâmetros:**
- Query param: `dataEntrada` (String) - Data do movimento
- Body: `ListaSpagInfoRepresentation` - Lista de objetos com informações de pagamento

---

## 5. Principais Regras de Negócio

1. **Consolidação Diária**: O sistema consolida movimentos de pagamento agrupados por data, origem de pagamento, tipo de liquidação e remetente.

2. **Substituição de Dados**: Antes de inserir novos registros para uma data específica, o sistema remove todos os registros existentes daquela data (`DELETE` seguido de `INSERT`).

3. **Processamento em Lote**: Os registros são inseridos em lotes de 500 registros por vez (configurado via `@BatchChunkSize(500)`).

4. **Auditoria**: Todos os registros inseridos são marcados com flag ativo ('S'), login 'spag-movimenta-pagamento' e data de inclusão automática.

5. **Tratamento de Erros**: Erros durante o processamento retornam HTTP 500 com mensagem de erro detalhada.

---

## 6. Relação entre Entidades

**MovimentoPagamento** (Entidade de Domínio):
- Representa um movimento consolidado de pagamento
- Atributos principais:
  - `codigoOrigemPagamento`: código da origem do pagamento
  - `nomeOrigemPagamento`: nome da origem do pagamento
  - `codLiquidacao`: código do tipo de liquidação
  - `nomeLiquidacao`: nome do tipo de liquidação
  - `documentoRemetente`: CPF/CNPJ do remetente
  - `nomeRemetente`: nome do remetente
  - `quantidade`: quantidade de movimentos
  - `valorTotal`: valor total dos movimentos
  - `dataMovimento`: data do movimento

Não há relacionamentos complexos entre entidades. O modelo é simples e focado em consolidação de dados.

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| não se aplica | - | - | O sistema não realiza operações de leitura, apenas escrita |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| dbo.tbpagamentomovimentodia | tabela | DELETE | Remove registros de movimentos de pagamento de uma data específica antes de inserir novos dados |
| dbo.tbpagamentomovimentodia | tabela | INSERT | Insere registros consolidados de movimentos de pagamento por dia, incluindo informações de origem, liquidação, remetente, quantidade e valores |

**Campos da tabela tbpagamentomovimentodia:**
- dtmovimento, nucpfcnpjremetente, nmremetente, nuorigemoperacao, cdliquidacao, qtmovimentodia, flativo, dslogin, dtinclusao, dtalteracao, vrmovimentodia, dsliquidacao, dsorigemoperacao

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | leitura | /usr/etc/log (em ambientes) | Arquivo de configuração de logs, montado via ConfigMap em diferentes ambientes |
| application.yml | leitura | resources | Arquivo de configuração da aplicação Spring Boot |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| API Gateway OAuth2 | Autenticação | Integração com serviço de autenticação JWT para validação de tokens (URLs variam por ambiente: des, uat, prd) |
| SQL Server (DBSPAG) | Banco de Dados | Banco de dados principal onde são armazenados os movimentos de pagamento |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura hexagonal bem estruturada com separação clara entre domain, application e infrastructure
- Uso adequado de padrões como Repository, Service e Controller
- Boa cobertura de testes (unitários, integração e funcionais)
- Uso de Lombok reduzindo boilerplate
- Configuração adequada de segurança OAuth2
- Documentação via Swagger
- Uso de JDBI com SQL externalizado em arquivos
- Processamento em lote otimizado (batch de 500 registros)

**Pontos de Melhoria:**
- Tratamento de exceções genérico no controller (captura `Exception` ao invés de exceções específicas)
- Falta de validação de entrada nos dados recebidos (sem anotações de validação como `@Valid`, `@NotNull`, etc)
- Logs em português misturados com código em inglês
- Ausência de transações explícitas (embora JDBI use TransactionAwareDataSourceProxy)
- Testes unitários com implementação vazia em algumas classes
- Falta de documentação JavaDoc em várias classes
- Operação de DELETE seguida de INSERT poderia ser otimizada com MERGE/UPSERT
- Ausência de paginação caso o volume de dados seja muito grande

---

## 14. Observações Relevantes

1. **Segurança**: O sistema utiliza OAuth2 com JWT para autenticação, integrando-se com o API Gateway do Banco Votorantim.

2. **Ambientes**: A aplicação está preparada para múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas via profiles Spring.

3. **Monitoramento**: Possui endpoints Actuator expostos na porta 9090 para health checks e métricas Prometheus.

4. **Containerização**: Aplicação containerizada com Docker usando imagem OpenJDK 11 com OpenJ9 (otimizada para consumo de memória).

5. **Infraestrutura**: Deploy em OpenShift/Kubernetes com configurações de probes (liveness e readiness) bem definidas.

6. **Auditoria**: Integração com biblioteca de trilha de auditoria do Banco Votorantim (`springboot-arqt-base-trilha-auditoria-web`).

7. **Padrão de Nomenclatura**: Segue padrão de nomenclatura corporativo do Banco Votorantim (prefixo `sboot-spag-base-atom-`).

8. **Operação Idempotente**: A operação de consolidação é idempotente - executar múltiplas vezes para a mesma data substitui os dados anteriores.

9. **Performance**: O uso de batch inserts (500 registros por vez) otimiza a performance para grandes volumes de dados.

10. **Arquitetura Limpa**: O projeto segue princípios de Clean Architecture com separação clara de responsabilidades entre camadas.