# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-spbb-base-atom-ispb-lote** é um microserviço atômico desenvolvido em Spring Boot para gerenciamento e monitoramento de lotes no contexto do Sistema de Pagamentos Brasileiro (SPB/ISPB). O serviço oferece funcionalidades para:

- Geração de números de controle para lotes baseados em identificadores e datas de movimento
- Registro de movimentos de lotes no banco de dados
- Gerenciamento de contingências relacionadas a processamento de lotes
- Consulta de informações de movimentação e controle

O sistema atua como um serviço backend stateful que interage diretamente com o banco de dados Sybase para operações de leitura e escrita relacionadas ao controle de lotes do SPB.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application.java` | Classe principal que inicializa a aplicação Spring Boot e configura segurança JWT |
| `MonitoramentoLoteApiDelegateImpl` | Controlador REST que implementa os endpoints da API de monitoramento de lotes |
| `MonitoramentoLoteService` | Camada de serviço contendo a lógica de negócio para operações de lotes |
| `MonitoramentoLoteRepository` | Interface de repositório JDBI para acesso aos dados de lotes |
| `MonitoramentoLoteMapper` | Mapper MapStruct para conversão entre objetos de domínio e DTOs |
| `AppConfiguration` | Configuração geral da aplicação (Jackson, JDBI, beans) |
| `JdbiConfiguration` | Configuração específica do JDBI para acesso ao banco de dados |
| `GlobalExceptionHandler` | Tratamento centralizado de exceções da aplicação |
| `RegraNegocioException` | Exceção customizada para erros de regras de negócio |
| `NumeroControleDomain` | Entidade de domínio representando número de controle e data de movimento |
| `ContigenciaDomain` | Entidade de domínio representando dados de contingência |

## 3. Tecnologias Utilizadas

- **Framework Principal**: Spring Boot 2.7.8
- **Linguagem**: Java 11
- **Gerenciador de Dependências**: Maven
- **Acesso a Dados**: JDBI 3.9.1 (SQL Object API)
- **Banco de Dados**: Sybase ASE (jConnect 16.3-SP03-PL07)
- **Mapeamento de Objetos**: MapStruct
- **Documentação API**: OpenAPI 3.0 / Swagger UI
- **Segurança**: Spring Security OAuth2 Resource Server (JWT)
- **Logging**: Logback
- **Utilitários**: Lombok, Apache Commons Lang3
- **Testes**: JUnit 5, Mockito
- **Containerização**: Docker
- **Orquestração**: Kubernetes/OpenShift (Google Cloud Platform)
- **Monitoramento**: Spring Actuator, Prometheus
- **Framework Corporativo**: Atlante (ATLE) Base

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/lote/monitoramento-lote/{grmsId}/{moviId}` | `MonitoramentoLoteApiDelegateImpl` | Retorna o número de controle gerado para um lote específico baseado no grmsId e moviId |
| POST | `/v1/lote/monitoramento-lote/insere/ultimo-movimento` | `MonitoramentoLoteApiDelegateImpl` | Insere um registro de último movimento na tabela de controle |
| POST | `/v1/lote/monitoramento-lote/insere/contigencia` | `MonitoramentoLoteApiDelegateImpl` | Registra informações de contingência para um movimento específico |

**Observação**: Todos os endpoints requerem autenticação via Bearer Token JWT.

## 5. Principais Regras de Negócio

1. **Geração de Número de Controle**: O número de controle é formado pela concatenação de:
   - Identificador do grupo (grmsId)
   - Ano do movimento (4 dígitos)
   - Mês do movimento (2 dígitos com zero à esquerda)
   - Dia do movimento (2 dígitos com zero à esquerda)
   - ID do movimento (9 dígitos com zeros à esquerda)

2. **Data de Movimento**: A data de movimento é obtida da tabela de parâmetros gerais (`tb_pmge_parametro_geral`) e representa a data atual de processamento do sistema.

3. **Registro de Contingência**: Permite registrar informações de contingência incluindo ID do movimento, número de controle, data de gravação e hostname do servidor.

4. **Controle de Último Movimento**: Mantém registro temporal dos últimos movimentos processados para fins de auditoria e controle.

5. **Tratamento de Exceções**: Exceções de negócio são tratadas com código 900, enquanto exceções técnicas retornam código 500.

## 6. Relação entre Entidades

**Entidades de Domínio:**

- **NumeroControleDomain**
  - `dtMovto`: Data do movimento (LocalDateTime)
  - `numControle`: Número de controle gerado (String)

- **ContigenciaDomain**
  - `moviId`: Identificador do movimento (Integer)
  - `nuControle`: Número de controle (String)
  - `dtGravacao`: Data de gravação (LocalDateTime)
  - `dsHost`: Nome do host (String)

**Relacionamentos:**
- Não há relacionamentos diretos entre as entidades, pois são utilizadas de forma independente para diferentes operações.
- Ambas se relacionam indiretamente através do `moviId` (ID do movimento) que é a chave de referência no sistema.

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| `tb_pmge_parametro_geral` | Tabela | SELECT | Tabela de parâmetros gerais do sistema, consultada para obter a data de movimento atual (`pmge_dt_movimento_atual`) |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| `tb_movi_nu_ctrl_contingencia` | Tabela | INSERT | Tabela que armazena registros de contingência de movimentos, incluindo ID do movimento, número de controle, data de gravação e hostname |
| `tb_ulmv_ultimo_movimento_idt` | Tabela | INSERT | Tabela que registra timestamps dos últimos movimentos processados para controle e auditoria |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `application.yml` | Leitura | Spring Boot | Arquivo de configuração principal da aplicação com profiles (local, des, uat, prd) |
| `application-local.yml` | Leitura | Spring Boot | Configurações específicas para ambiente local de desenvolvimento |
| `logback-spring.xml` | Leitura | Logback | Configuração de logging da aplicação |
| `openapi.yaml` | Leitura | OpenAPI Generator | Especificação OpenAPI 3.0 dos endpoints REST |
| `*.sql` (resources) | Leitura | JDBI | Arquivos SQL para queries parametrizadas (insereContigencia, insereUltimoMovimento, retornaDataMovimento, retornaNumeroControle) |

## 10. Filas Lidas

Não se aplica.

## 11. Filas Geradas

Não se aplica.

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **API Gateway BV** | Autenticação | Integração com o API Gateway corporativo para validação de tokens JWT via JWKS (endpoints: apigatewaydes.bvnet.bv, apigatewayuat.bvnet.bv, apigateway.bvnet.bv) |
| **Banco de Dados Sybase** | Persistência | Conexão com banco Sybase ASE (DBISPB) em diferentes ambientes (des, qa, uat, prd) para operações de leitura e escrita |
| **ConfigCat** | Configuração | Sistema de feature flags e configuração dinâmica (referenciado nas variáveis de ambiente) |
| **Atlante Security** | Segurança | Framework corporativo de segurança e auditoria (trilha de auditoria web) |

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões de camadas (controller, service, repository, domain)
- Uso adequado de frameworks modernos (Spring Boot, JDBI, MapStruct)
- Separação clara de responsabilidades entre as classes
- Implementação de tratamento centralizado de exceções
- Boa cobertura de testes unitários (service, rest, exception handler)
- Uso de Lombok para reduzir boilerplate
- Configuração adequada de profiles para diferentes ambientes
- Documentação OpenAPI bem estruturada
- Uso de SQL externalizado em arquivos separados (boa prática JDBI)

**Pontos de Melhoria:**
- Falta de comentários JavaDoc nas classes e métodos principais
- Ausência de validações de entrada nos DTOs (Bean Validation)
- Tratamento de exceções poderia ser mais granular
- Falta de logs estruturados em pontos críticos do fluxo
- Configurações de segurança poderiam estar mais documentadas
- Ausência de testes de integração
- Algumas queries SQL poderiam ter comentários explicativos

O código demonstra maturidade técnica e segue boas práticas de desenvolvimento, mas há espaço para melhorias em documentação e validações.

## 14. Observações Relevantes

1. **Ambiente Multi-Cloud**: O sistema está preparado para execução em Google Cloud Platform (GCP) com suporte a múltiplos ambientes (local, des, qa, uat, prd).

2. **Segurança**: Todos os endpoints são protegidos por autenticação JWT Bearer Token, exceto endpoints públicos (swagger, actuator).

3. **Monitoramento**: A aplicação expõe métricas via Actuator na porta 9090, incluindo health checks, métricas e Prometheus.

4. **Banco de Dados Legacy**: Utiliza Sybase ASE, um banco de dados legado, com configurações específicas de charset (iso_1) e parâmetros de conexão customizados.

5. **Probes Kubernetes**: Configurados liveness e readiness probes com tempos de inicialização longos (420s), indicando que a aplicação pode ter dependências pesadas na inicialização.

6. **Recursos Computacionais**: 
   - Requests: 150m CPU, 384Mi memória
   - Limits: 1000m CPU, 1Gi memória
   - JVM configurada para usar 70% da RAM disponível

7. **Padrão Atômico**: Segue o padrão de microserviços atômicos do Banco Votorantim (framework Atlante), sendo um serviço stateful focado em uma responsabilidade específica.

8. **Versionamento de API**: A API está versionada (v1) no path base, facilitando evolução futura.

9. **CSRF Protection**: Habilitado em ambientes produtivos para maior segurança.

10. **Certificados**: Utiliza cacerts customizados montados via secrets do Kubernetes para comunicação segura.