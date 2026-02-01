# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de monitoramento e dashboard para visualização de lançamentos de boletos. Trata-se de um serviço atômico REST desenvolvido em Spring Boot que consulta dados de lançamentos bancários em um banco de dados Sybase, permitindo visualização de informações consolidadas sobre boletos processados, incluindo comparações temporais (dia atual vs. 7 dias atrás).

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal de inicialização do Spring Boot |
| `LancamentoController` | Controlador REST que expõe endpoints para consulta de lançamentos |
| `LancamentoService` | Serviço de domínio que implementa a lógica de negócio para consulta de lançamentos |
| `JdbiLancamentoRepositoryImpl` | Implementação do repositório usando JDBI para acesso ao banco de dados |
| `LancamentoMapper` | Mapper JDBI para conversão de ResultSet em objetos de domínio |
| `Lancamento` | Entidade de domínio representando um lançamento de boleto |
| `DashBoletoConfiguration` | Classe de configuração do Spring para beans e dependências |
| `OpenApiConfiguration` | Configuração do Swagger/OpenAPI para documentação da API |

## 3. Tecnologias Utilizadas

- **Framework Principal**: Spring Boot 2.x
- **Linguagem**: Java 11
- **Build Tool**: Maven
- **Banco de Dados**: Sybase ASE (driver jConnect 16.3)
- **Acesso a Dados**: JDBI 3.9.1
- **Documentação API**: Swagger/Springfox 2.9.2
- **Segurança**: Spring Security OAuth2 (Resource Server com JWT)
- **Monitoramento**: Spring Boot Actuator, Micrometer Prometheus
- **Auditoria**: BV Trilha Auditoria 2.2.1
- **Pool de Conexões**: HikariCP (padrão do Spring Boot)
- **Logging**: Logback com formato JSON
- **Testes**: JUnit 5, Mockito, Rest Assured, Pact
- **Containerização**: Docker
- **Observabilidade**: Prometheus + Grafana

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/dash-monitoramento/visao-geral/{id}` | `LancamentoController` | Retorna lançamentos do dia atual |
| GET | `/v1/dash-monitoramento/visao-geral-compare7/{id}` | `LancamentoController` | Retorna lançamentos de 7 dias atrás para comparação |

## 5. Principais Regras de Negócio

- Consulta de lançamentos filtrados por data de movimento
- Filtragem de lançamentos com código de liquidação igual a 22
- Filtragem de lançamentos com status igual a 1 (ativo)
- Agrupamento de lançamentos por origem, conta remetente e flag de fintech
- Agregação de quantidade e valor total de lançamentos
- Comparação temporal de lançamentos (dia atual vs. 7 dias atrás)
- O parâmetro `idVisao` está previsto mas não implementado (comentário no código indica implementação futura)

## 6. Relação entre Entidades

**Entidade Principal: Lancamento**
- Atributos:
  - `quantidade` (Integer): Quantidade de lançamentos agrupados
  - `valor` (Double): Valor total dos lançamentos
  - `codOrigem` (Integer): Código de origem do lançamento
  - `numContaRemetente` (String): Número da conta remetente
  - `flLancamentoFintech` (String): Flag indicando se é lançamento fintech

**Entidade Secundária: DashBoleto** (não utilizada ativamente no código atual)
- Atributos:
  - `id` (String)
  - `version` (Integer)

Não há relacionamentos complexos entre entidades. O modelo é simples e focado em agregações de dados.

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TBL_LANCAMENTO | Tabela | SELECT | Tabela principal de lançamentos bancários, consultada com filtros por data de movimento, código de liquidação (22) e status (1), com agrupamento por origem, conta remetente e flag fintech |

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema realiza apenas operações de leitura (SELECT).

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | Spring Boot | Arquivo de configuração da aplicação com datasource, segurança OAuth2 e perfis de ambiente |
| logback-spring.xml | Leitura | Logback | Configuração de logs em formato JSON para stdout |
| getLancamento.sql | Leitura | JdbiLancamentoRepositoryImpl | Query SQL para consulta de lançamentos (existem duas cópias idênticas em paths diferentes) |

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas.

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Banco Sybase ASE | Banco de Dados | Conexão JDBC para consulta de lançamentos na tabela TBL_LANCAMENTO |
| API Gateway BV | Serviço de Autenticação | Validação de tokens JWT via JWK endpoint (URLs variam por ambiente: des, qa, uat, prd) |
| Prometheus | Monitoramento | Exportação de métricas via endpoint `/actuator/prometheus` |
| Grafana | Visualização | Dashboards para monitoramento da aplicação (configurado via docker-compose) |

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura hexagonal bem definida (domain, application, infrastructure)
- Separação clara de responsabilidades entre camadas
- Uso de padrões modernos (JDBI, Spring Boot, Lombok)
- Configuração adequada de segurança OAuth2
- Boa estrutura de testes (unit, integration, functional)
- Documentação via Swagger configurada
- Observabilidade com Actuator e Prometheus

**Pontos Negativos:**
- Código duplicado: query SQL existe em dois locais diferentes (cpbd e pgft)
- Parâmetro `idVisao` não implementado, apenas recebido e ignorado
- Método `localDateTeste()` não utilizado no serviço
- Classe `DashBoleto` e suas dependências não são utilizadas no fluxo principal
- Testes unitários vazios ou com asserções triviais (`assertTrue(true)`)
- Falta de validação de entrada nos endpoints
- Ausência de tratamento de exceções específico
- Comentários em português misturados com código em inglês
- Falta de paginação nos endpoints que retornam listas
- Configuração de datasource com credenciais hardcoded no application.yml (deveria usar variáveis de ambiente)

## 14. Observações Relevantes

1. **Duplicação de Recursos SQL**: Existem dois arquivos `getLancamento.sql` idênticos em paths diferentes (`cpbd` e `pgft`), sugerindo possível refatoração ou migração de estrutura não concluída.

2. **Funcionalidade Incompleta**: O parâmetro `idVisao` é recebido nos endpoints mas não é utilizado na lógica de negócio, indicando funcionalidade planejada mas não implementada.

3. **Segurança**: A aplicação está configurada como Resource Server OAuth2, validando tokens JWT contra o API Gateway do Banco Votorantim.

4. **Ambientes**: O sistema suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas via profiles do Spring.

5. **Monitoramento Robusto**: Infraestrutura completa de observabilidade com Prometheus e Grafana pré-configurada, incluindo dashboards customizados.

6. **Pool de Conexões**: Utiliza HikariCP com métricas expostas para monitoramento de performance de banco de dados.

7. **Arquitetura de Deployment**: Preparado para deploy em OpenShift/Kubernetes com configurações de infra-as-code e health checks configurados.

8. **Padrão de Nomenclatura**: Segue padrão de nomenclatura do Banco Votorantim para componentes atômicos (`sboot-pgft-base-atom-*`).