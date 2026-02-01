# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-sitp-base-atom-validar** é um microserviço atômico desenvolvido em Java com Spring Boot, responsável por validar informações de transações no sistema ITP (Sistema de Transferência de Pagamentos) do Banco Votorantim. O serviço recebe dados de transações (código de filial, origem, transação e liquidação) e valida essas informações consultando o banco de dados Sybase, retornando dados de validação como tipo de lançamento, indicadores de crédito/débito e códigos de eventos contábeis.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application.java` | Classe principal que inicializa a aplicação Spring Boot com segurança OAuth2 habilitada |
| `ValidarController.java` | Controlador REST que expõe o endpoint de validação e trata requisições HTTP |
| `ValidarService.java` | Serviço de domínio que implementa a lógica de negócio de validação |
| `ValidarRepositoryImpl.java` | Implementação do repositório que executa consultas SQL no banco de dados |
| `ValidacaoMapper.java` | Mapper que converte representações REST em objetos de domínio |
| `ValidacaoRowMapper.java` | Mapper JDBI que converte ResultSet em objetos de domínio Validacao |
| `DadosValidacao.java` | Entidade de domínio que representa os dados de entrada para validação |
| `Validacao.java` | Entidade de domínio que representa o resultado da validação |
| `DatabaseConfiguration.java` | Configuração do JDBI e integração com DataSource |
| `OpenApiConfiguration.java` | Configuração do Swagger/OpenAPI para documentação da API |
| `ValidarConfiguration.java` | Configuração de beans do domínio de validação |

---

## 3. Tecnologias Utilizadas

- **Java 11** - Linguagem de programação
- **Spring Boot 2.x** - Framework principal
- **Spring Security OAuth2** - Autenticação e autorização via JWT
- **JDBI 3.9.1** - Framework de acesso a dados SQL
- **Sybase ASE (jConnect 16.3)** - Banco de dados
- **Swagger/Springfox 2.9.2** - Documentação de API
- **Lombok** - Redução de boilerplate
- **Spring Actuator** - Monitoramento e métricas
- **Micrometer/Prometheus** - Métricas customizadas
- **Grafana** - Visualização de métricas
- **Logback** - Framework de logging
- **Maven** - Gerenciamento de dependências e build
- **Docker** - Containerização
- **OpenShift/Kubernetes** - Orquestração de containers

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/banco-digital/validar` | `ValidarController` | Valida dados de transação ITP recebendo códigos de filial, liquidação, origem e transação, retornando informações de validação |

---

## 5. Principais Regras de Negócio

1. **Validação de Transação**: O sistema valida se uma transação existe e está ativa no banco de dados ITP com base nos códigos fornecidos (filial, origem, transação e liquidação)

2. **Verificação de Status Ativo**: Apenas transações com `FlAtivo = 'S'` e descrições com `Status = 'A'` são consideradas válidas

3. **Validação de Completude**: O resultado da validação deve conter todos os campos obrigatórios preenchidos (código de evento contábil, tipo de lançamento, indicadores de crédito/débito CC)

4. **Transformação de Indicadores**: Indicadores 'S' são convertidos para Boolean true, demais valores para false

5. **Tratamento de Exceções**: Transações inválidas ou não encontradas geram `TransacaoInvalidaException` com código de erro específico

6. **Valores Padrão na Resposta**: Sempre retorna indicadorTerceiro='N', tipoDocumento='C' e tipoFinalidade='C' independente da validação

---

## 6. Relação entre Entidades

**Entidades de Domínio:**

- **DadosValidacao**: Representa os dados de entrada
  - Atributos: codigoFilial, codigoOrigem, codigoTransacao, codigoLiquidacao

- **Validacao**: Representa o resultado da validação
  - Atributos: codEventoContabil, tipoLancamento, isCreditoCC, isDebitoCC, codTransacaoDebitoCCSC, codTransacaoDebitoCCCC, codTransacatoCreditoCC
  - Possui método `isValid()` para auto-validação

**Relacionamento:**
- DadosValidacao é usado como entrada para consulta
- Validacao é o resultado retornado pela consulta
- Não há relacionamento de agregação, são entidades independentes usadas em fluxo sequencial

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TBL_TRANSACAO_SPB | tabela | SELECT | Tabela principal de transações SPB contendo códigos de evento, indicadores de origem/destino de recursos |
| TBL_DESCRICAO_TRANSACAO_SPB | tabela | SELECT | Tabela de descrições de transações contendo tipo de lançamento e status |
| TBL_TRANSACAO_CCON | tabela | SELECT | Tabela de transações de conta corrente contendo códigos de origem/destino para PMCF |

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot (startup) | Arquivo de configuração da aplicação com datasources, profiles e configurações de segurança |
| logback-spring.xml | leitura | Logback (runtime) | Configuração de logging com formato JSON e console |
| validarDados.sql | leitura | ValidarRepositoryImpl | Query SQL para validação de dados de transação |
| sboot-sitp-base-atom-valida-itp.yaml | leitura | Swagger Codegen (build time) | Especificação OpenAPI para geração de interfaces REST |

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
| Banco de Dados Sybase ITP | Database | Banco de dados principal contendo tabelas de transações SPB (hosts: sybdesspb.bvnet.bv, sybspb_4999_5000_5010.bvnet.bv, sybuatspb.bvnet.bv) |
| Servidor OAuth2/JWT | API REST | Serviço de autenticação e autorização via JWT (api-digitaldes.bancovotorantim.com.br, api-digital.bancovotorantim.com.br) |
| Prometheus | Metrics | Sistema de coleta de métricas exposto via /actuator/prometheus |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura limpa seguindo princípios de Hexagonal Architecture (ports/adapters)
- Separação clara de responsabilidades em módulos (domain, application, common)
- Uso adequado de padrões como Builder, Mapper e Repository
- Boa cobertura de configurações para diferentes ambientes
- Uso de Lombok reduzindo boilerplate
- Documentação via Swagger/OpenAPI
- Implementação de observabilidade (Actuator, Prometheus, Grafana)
- Segurança implementada com OAuth2/JWT
- Uso de JDBI com SQL externalizado facilitando manutenção

**Pontos de Melhoria:**
- Falta de tratamento mais granular de exceções (catch genérico de Exception)
- Ausência de logs estruturados nas classes de negócio
- Validação de entrada poderia usar Bean Validation no controller
- SQL com sintaxe Sybase antiga (uso de *= para outer join)
- Falta de testes unitários enviados para análise
- Método `transformarIndicadorEmBoolean` poderia ser mais robusto tratando null
- Hardcoded de valores na resposta do controller ('N', 'C', 'C')

O código demonstra maturidade arquitetural e boas práticas, mas há espaço para melhorias em tratamento de erros, logging e validações.

---

## 14. Observações Relevantes

1. **Ambiente Multi-Profile**: O sistema suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas de datasource e URLs de autenticação

2. **Segurança**: Todos os endpoints são protegidos por OAuth2 com JWT, requerendo token válido para acesso

3. **Monitoramento**: Aplicação expõe métricas em porta separada (9090) e possui integração completa com Prometheus/Grafana

4. **Infraestrutura como Código**: Possui configuração completa para deploy em OpenShift/Kubernetes via arquivo infra.yml

5. **Charset Específico**: Conexão com Sybase usa charset ISO-1 em ambientes de desenvolvimento

6. **Probes de Saúde**: Configurado com liveness e readiness probes com timeouts e thresholds específicos

7. **Volumes Globais**: Utiliza certificados Java (cacerts) montados via secret no Kubernetes

8. **Auditoria**: Integração com biblioteca de trilha de auditoria do Banco Votorantim (springboot-arqt-base-trilha-auditoria-web)

9. **Pipeline CI/CD**: Configurado para Jenkins com propriedades específicas (jdk11, platform GOOGLE)

10. **Arquitetura Modular**: Projeto dividido em 3 módulos Maven (common, domain, application) seguindo princípios de Clean Architecture