# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema atômico de recepção de boletos do SPAG (Sistema de Pagamentos) do Banco Votorantim. O serviço tem como objetivo principal verificar se um participante (identificado por CNPJ/CPF e origem de operação) está habilitado para participar do processo de recepção de boletos, considerando o tipo de meio de integração (CNAB, API ou ambos). Trata-se de um microserviço REST construído com Spring Boot seguindo arquitetura hexagonal (ports and adapters).

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot que inicializa a aplicação |
| `ControleParticipanteController` | Controlador REST que expõe o endpoint de consulta de participação |
| `ControleParticipanteService` | Serviço de domínio que implementa a lógica de negócio de verificação de participação |
| `ControleParticipanteRepository` | Interface de porta (port) para acesso aos dados de participantes |
| `ControleParticipanteRepositoryImpl` | Implementação do repositório usando JDBI para acesso ao SQL Server |
| `ControleParticipante` | Entidade de domínio representando um participante do controle de migração |
| `ParticipanteRowMapper` | Mapper JDBI para conversão de ResultSet em objeto de domínio |
| `RecepcaoBoletoConfiguration` | Configuração de beans e dependências da aplicação |
| `OpenApiConfiguration` | Configuração do Swagger/OpenAPI para documentação da API |
| `RecepcaoBoletoException` | Exceção customizada de domínio |

---

## 3. Tecnologias Utilizadas

- **Java 11** - Linguagem de programação
- **Spring Boot 2.x** - Framework principal
- **Spring Security OAuth2** - Segurança e autenticação JWT
- **JDBI 3.9.1** - Framework de acesso a dados SQL
- **Microsoft SQL Server** - Banco de dados (driver 7.4.0.jre11)
- **Swagger/Springfox 2.9.2** - Documentação de API
- **Lombok** - Redução de boilerplate
- **Micrometer/Prometheus** - Métricas e observabilidade
- **Logback** - Logging
- **JUnit 5** - Testes unitários
- **Mockito** - Mocks para testes
- **Rest Assured** - Testes funcionais
- **Pact** - Testes de contrato
- **Maven** - Gerenciamento de dependências
- **Docker** - Containerização
- **Grafana** - Visualização de métricas

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/recepcao-boleto/participante` | `ControleParticipanteController` | Verifica se um participante está habilitado para recepção de boletos com base em CNPJ/CPF, origem de operação e tipo de meio de integração |

**Parâmetros do endpoint:**
- `numeroCnpjCpf` (obrigatório): CNPJ ou CPF do participante
- `numeroOrigemOperacao` (obrigatório): Número da origem da operação
- `tpMeioIntegracao` (opcional): Tipo de meio de integração (CNAB=1, API=2, Ambos=3)

**Resposta:** `{ "participa": true/false }`

---

## 5. Principais Regras de Negócio

1. **Verificação de Participação**: O sistema verifica se um participante (CNPJ/CPF) está cadastrado e ativo para uma determinada origem de operação.

2. **Tipo de Meio de Integração**: Se o parâmetro `tpMeioIntegracao` não for informado, assume-se o valor padrão 1 (CNAB).

3. **Filtros de Consulta**: A consulta considera:
   - Participante ativo (`FlAtivo = 'S'`)
   - Código de liquidação fixo = 22
   - Tipo entrada/saída = 'S' (Saída)
   - Compatibilidade do tipo de meio de integração (suporta valor 3 que representa "ambos")

4. **Resposta Booleana**: O serviço retorna `true` se o participante existe, está ativo e atende aos critérios; caso contrário, retorna `false`.

---

## 6. Relação entre Entidades

**Entidade Principal:**
- `ControleParticipante`
  - `codigoParticipante` (Integer): Identificador único do participante
  - `numeroCnpjCpf` (String): CNPJ ou CPF do remetente
  - `numeroOrigemOperacao` (Integer): Código da origem da operação
  - `flagAtivo` (Boolean): Indica se o participante está ativo

Não há relacionamentos complexos entre entidades. O sistema trabalha com uma única entidade de domínio que representa o controle de participantes na migração/recepção de boletos.

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| `DBSPAG.dbo.TbControleMigracaoParticipante` | Tabela | SELECT | Tabela que armazena o controle de participantes habilitados para migração/recepção de boletos, incluindo informações de CNPJ/CPF, origem de operação, status ativo e tipo de meio de integração |

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema realiza apenas operações de leitura (SELECT).

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `application.yml` | Leitura | Spring Boot | Arquivo de configuração da aplicação contendo datasource, segurança OAuth2, logging e propriedades do servidor |
| `logback-spring.xml` | Leitura | Logback | Configuração de logging em formato JSON para stdout |
| `findParticipante.sql` | Leitura | `ControleParticipanteRepositoryImpl` | Query SQL para busca de participantes na base de dados |
| `sboot-spag-base-atom-recepcao-boleto.yaml` | Leitura | Swagger Codegen | Especificação OpenAPI da API REST |

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
| **SQL Server (DBSPAG)** | Banco de Dados | Banco de dados principal contendo a tabela `TbControleMigracaoParticipante` para consulta de participantes |
| **Servidor OAuth2/JWT** | Autenticação | Servidor de autenticação para validação de tokens JWT (URLs variam por ambiente: des, uat, prd) |
| **Prometheus** | Observabilidade | Exportação de métricas da aplicação via endpoint `/actuator/prometheus` |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura hexagonal bem implementada com separação clara entre domínio, portas e adaptadores
- Uso adequado de padrões de projeto (Repository, Service, Controller)
- Boa cobertura de testes (unitários, integração e funcionais)
- Configuração adequada de segurança com OAuth2/JWT
- Uso de Lombok para redução de boilerplate
- Documentação OpenAPI/Swagger bem estruturada
- Observabilidade implementada com Prometheus e Grafana
- Estrutura modular (common, domain, application)
- Uso de JDBI com SQL externalizado facilitando manutenção

**Pontos de Melhoria:**
- Falta de tratamento de exceções mais robusto (a exceção `RecepcaoBoletoException` está vazia)
- Ausência de validações de entrada mais detalhadas nos parâmetros da API
- Testes funcionais e de integração estão vazios/incompletos
- Poderia ter mais logs de auditoria para rastreabilidade
- Falta documentação inline (JavaDoc) em algumas classes
- A query SQL poderia estar mais parametrizada/dinâmica

O código demonstra maturidade arquitetural e boas práticas de desenvolvimento, mas há espaço para melhorias em tratamento de erros, validações e completude dos testes.

---

## 14. Observações Relevantes

1. **Ambientes**: O sistema está preparado para múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas de datasource e URLs de autenticação.

2. **Segurança**: Todos os endpoints (exceto actuator) são protegidos por OAuth2 com validação de JWT.

3. **Infraestrutura como Código**: O projeto inclui configurações completas para deploy em OpenShift/Kubernetes via arquivo `infra.yml`.

4. **Monitoramento**: Stack completa de observabilidade com Prometheus e Grafana configurados via Docker Compose para ambiente local.

5. **Padrão de Versionamento**: API versionada com prefixo `/v1/`.

6. **Health Checks**: Probes de liveness e readiness configurados com timeouts e delays apropriados.

7. **Pool de Conexões**: Utiliza HikariCP para gerenciamento eficiente de conexões com o banco de dados.

8. **Arquitetura de Testes**: Estrutura bem organizada separando testes unitários, de integração e funcionais em diretórios distintos.

9. **CI/CD**: Configuração Jenkins presente (`jenkins.properties`) indicando pipeline automatizado.

10. **Valor Padrão**: Quando `tpMeioIntegracao` não é informado, o sistema assume valor 1 (CNAB) como padrão.