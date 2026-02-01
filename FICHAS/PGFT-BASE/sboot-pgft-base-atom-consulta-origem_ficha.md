# Ficha Técnica do Sistema

## 1. Descrição Geral
Sistema atômico (microserviço) desenvolvido em Spring Boot para consulta de origens de sistemas no SPB (Sistema de Pagamentos Brasileiro). O serviço expõe endpoints REST para listar e consultar informações sobre origens de sistemas cadastradas no banco de dados DBITP (Sybase), retornando dados como código da origem, nome, grupo, empresa e status.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal que inicializa a aplicação Spring Boot com segurança OAuth2 |
| `ConsultaOrigemController` | Controlador REST que expõe os endpoints de consulta de origens |
| `ConsultaOrigemService` | Serviço de domínio que implementa a lógica de negócio para consulta de origens |
| `ConsultaOrigemRepository` | Interface de porta (port) que define o contrato de acesso a dados |
| `ConsultaOrigemRepositoryImpl` | Implementação do repositório usando JDBI para acesso ao banco Sybase |
| `ConvertOrigem` | Classe utilitária para conversão entre objetos de domínio e representação |
| `RetornoOrigem` | Entidade de domínio que representa os dados de uma origem |
| `ConsultaOrigemConfiguration` | Configuração de beans do Spring para injeção de dependências |
| `JdbiConfiguration` | Configuração do JDBI para acesso a dados |
| `OpenApiConfiguration` | Configuração do Swagger/OpenAPI para documentação da API |

## 3. Tecnologias Utilizadas
- **Framework**: Spring Boot 2.x
- **Linguagem**: Java 11
- **Segurança**: Spring Security OAuth2 (JWT)
- **Banco de Dados**: Sybase ASE (driver jConnect 4)
- **Acesso a Dados**: JDBI 3.9.1
- **Documentação API**: Springfox Swagger 3.0.0
- **Observabilidade**: Spring Actuator, Micrometer, Prometheus
- **Auditoria**: BV Trilha Auditoria 2.2.1
- **Pool de Conexões**: HikariCP
- **Build**: Maven
- **Containerização**: Docker
- **Monitoramento**: Grafana + Prometheus
- **Testes**: JUnit 5, Mockito, RestAssured, Pact

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | /v1/consulta/get-origem | ConsultaOrigemController | Consulta origens com código >= 88 |
| GET | /v1/consulta/listarorigens | ConsultaOrigemController | Lista todas as origens cadastradas |

## 5. Principais Regras de Negócio
- **Filtro de Código**: O endpoint `get-origem` retorna apenas origens com código >= 88
- **Tratamento de Exceções**: Erros na consulta ao banco são capturados e retornados como erro HTTP 500 com mensagem padronizada
- **Conversão de Dados**: Os dados do banco são convertidos de objetos de domínio (`RetornoOrigem`) para objetos de representação (`RetornoOrigemRepresentation`)
- **Isolamento de Transação**: As consultas utilizam `ISOLATION 0` (read uncommitted) no Sybase
- **Segurança**: Todos os endpoints (exceto Swagger e Actuator) requerem autenticação JWT via OAuth2

## 6. Relação entre Entidades
O sistema trabalha com uma única entidade principal:

**RetornoOrigem**
- `codigoOrigem` (Integer): Código identificador da origem
- `nomeOrigem` (String): Nome/mnemônico da origem
- `grupoId` (Integer): Identificador do grupo
- `nomeEmpresa` (String): Nome da empresa associada
- `status` (String): Status da origem (ex: "A" para ativo)

Não há relacionamentos complexos entre entidades, pois o sistema trabalha com consultas diretas a uma única tabela.

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBITP.dbo.TBL_SIST_ORIGEM_SPB | Tabela | SELECT | Tabela que armazena informações sobre as origens de sistemas do SPB |

## 8. Estruturas de Banco de Dados Atualizadas
Não se aplica. O sistema realiza apenas operações de leitura (SELECT).

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | Spring Boot | Arquivo de configuração da aplicação (datasource, OAuth2, etc) |
| logback-spring.xml | Leitura | Logback | Configuração de logs da aplicação |
| getOrigem.sql | Leitura | ConsultaOrigemRepositoryImpl | Query SQL para consulta de origens com filtro |
| listarOrigens.sql | Leitura | ConsultaOrigemRepositoryImpl | Query SQL para listagem de todas as origens |

## 10. Filas Lidas
Não se aplica. O sistema não consome mensagens de filas.

## 11. Filas Geradas
Não se aplica. O sistema não publica mensagens em filas.

## 12. Integrações Externas
- **Servidor OAuth2/JWT**: Integração para validação de tokens JWT (URLs variam por ambiente: des, qa, uat, prd)
- **Banco de Dados Sybase**: Conexão JDBC com o banco DBITP para consulta de origens (hosts e portas variam por ambiente)
- **Prometheus**: Exposição de métricas via endpoint `/actuator/prometheus`

## 13. Avaliação da Qualidade do Código

**Nota: 7,5/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura hexagonal bem definida (ports/adapters)
- Separação clara de responsabilidades em módulos (common, domain, application)
- Uso adequado de padrões como injeção de dependência
- Boa cobertura de testes unitários
- Documentação OpenAPI/Swagger implementada
- Configuração de observabilidade (Actuator, Prometheus, Grafana)
- Uso de Lombok para redução de boilerplate

**Pontos de Melhoria:**
- Tratamento de exceções genérico no controller (captura `Exception` ao invés de exceções específicas)
- Falta de validação de entrada nos endpoints
- Logs com informações sensíveis (retorno completo de origens)
- Classe `ConvertOrigem` com construtor privado mas métodos estáticos (poderia ser interface com métodos default ou classe utilitária final)
- Falta de paginação nos endpoints de listagem
- Configurações de ambiente misturadas no mesmo arquivo (application.yml)
- Uso de `ISOLATION 0` pode causar leituras inconsistentes

## 14. Observações Relevantes
- O sistema segue o padrão de microserviços atômicos do Banco Votorantim
- Utiliza o scaffolding plugin `br.com.votorantim.arqt:scaffolding-plugin:0.51.7` com template atomic
- Possui infraestrutura como código (infra-as-code) para deploy em diferentes ambientes
- Implementa testes em três níveis: unitários, integração e funcionais
- Configurado para executar em porta 8080 (aplicação) e 9090 (actuator/métricas)
- Possui dashboard Grafana pré-configurado para monitoramento
- Credenciais de banco de dados são gerenciadas via cofre de senhas por ambiente
- O sistema não realiza operações de escrita, sendo exclusivamente de consulta