# Ficha Técnica do Sistema

## 1. Descrição Geral
Sistema atômico Spring Boot responsável pelo registro e gerenciamento de débitos veiculares. O sistema permite criar, atualizar e consultar débitos veiculares, realizar liquidações de débitos, processar lotes de pagamento e gerenciar ocorrências de erros relacionadas a arrecadadores e pagamentos. Integra-se com banco de dados SQL Server para persistência de dados e expõe APIs REST para consumo.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal que inicializa a aplicação Spring Boot |
| `RegistrarDebitosVeicularesController` | Controlador REST que expõe endpoints para operações de débitos veiculares |
| `RegistrarDebitosVeicularesService` | Serviço de domínio que implementa regras de negócio para registro e atualização de débitos |
| `OcorrenciaErroDebitoVeicularService` | Serviço para buscar e tratar ocorrências de erro de consulta |
| `LiquidacaoDebitoVeicularService` | Serviço para atualizar liquidações de débitos veiculares |
| `DebitoVeicularLiquidacaoLoteService` | Serviço para processar movimentos de lote de pagamento de débitos |
| `ArrecadadorService` | Serviço para validar e obter informações de arrecadadores |
| `ValidaCamposDebitoVeicular` | Classe de validação de campos de entrada (CPF/CNPJ, status, etc) |
| `ResourceExceptionHandler` | Tratador global de exceções da aplicação |
| `JdbiRegistrarDebitosVeicularesRepositoryImpl` | Implementação do repositório usando JDBI para operações de banco de dados |

## 3. Tecnologias Utilizadas
- **Framework**: Spring Boot 2.x
- **Linguagem**: Java 11
- **Gerenciamento de Dependências**: Maven
- **Banco de Dados**: Microsoft SQL Server
- **Acesso a Dados**: JDBI 3.9.1
- **Documentação API**: Swagger/OpenAPI (Springfox 3.0.0)
- **Mapeamento de Objetos**: MapStruct 1.3.1
- **Monitoramento**: Spring Boot Actuator + Micrometer (Prometheus)
- **Observabilidade**: Grafana + Prometheus
- **Logs**: Logback com formato JSON
- **Testes**: JUnit 5, Mockito, Rest Assured, Pact
- **Containerização**: Docker
- **Orquestração**: OpenShift/Kubernetes

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/registrar-debitos-veiculares/inserir` | `RegistrarDebitosVeicularesController` | Insere um novo débito veicular |
| POST | `/registrar-debitos-veiculares/atualizar` | `RegistrarDebitosVeicularesController` | Atualiza um débito veicular existente |
| GET | `/registrar-debitos-veiculares/buscar-ocorrencia-erro-consulta` | `RegistrarDebitosVeicularesController` | Busca ocorrência de erro na consulta de débito |
| PATCH | `/registrar-debitos-veiculares/atualizar-liquidacao` | `RegistrarDebitosVeicularesController` | Atualiza status de liquidação de débito veicular |
| POST | `/registrar-debitos-veiculares/inserir-liquidacao` | `RegistrarDebitosVeicularesController` | Insere débito veicular para liquidação |
| POST | `/registrar-debitos-veiculares/inserir-liquidacao-lote` | `RegistrarDebitosVeicularesController` | Insere movimentos de lote de pagamento |
| GET | `/registrar-debitos-veiculares/monta-solicitacao-liquidacao` | `RegistrarDebitosVeicularesController` | Monta solicitação de liquidação |

## 5. Principais Regras de Negócio

1. **Validação de CPF/CNPJ**: Valida CPF e CNPJ de proprietários e fintechs antes de processar débitos
2. **Validação de Arrecadador**: Verifica se o código do arrecadador existe antes de registrar débitos
3. **Validação de Status de Lançamento**: Valida se o status de lançamento informado existe no sistema (valores de 0 a 99)
4. **Validação de Liquidação**: Verifica existência de código de liquidação antes de processar lotes
5. **Validação de Lançamento**: Impede inserção de movimento de lote se o lançamento já existe na tabela de movimentos
6. **Mapeamento de Erros**: Mapeia códigos de erro do arrecadador para códigos de erro BV através de tabelas de relacionamento
7. **Tratamento de Erros Genéricos**: Retorna erro genérico (999) quando não é possível mapear erro específico
8. **Inclusão de Lançamento via Procedure**: Utiliza stored procedure `PrIncluirLancamento` para criar lançamentos no sistema
9. **Controle de Transações**: Gerencia transações de banco de dados para garantir consistência dos dados
10. **Auditoria**: Registra login do sistema e timestamps de inclusão/alteração em todas as operações

## 6. Relação entre Entidades

**Entidades Principais:**

- **TbConsultaDebitoVeicular**: Armazena consultas de débitos veiculares
  - Relaciona-se com TbArrecadador (N:1)
  - Relaciona-se com TbStatusLancamento (N:1)
  - Relaciona-se com TbOcorrenciaErroPagamento (N:1)

- **TbLancamento**: Armazena lançamentos financeiros
  - Relaciona-se com TbLiquidacao (N:1)
  - Relaciona-se com TbStatusLancamento (N:1)

- **TbLancamentoDebitoVeicular**: Relaciona lançamentos com débitos veiculares
  - Relaciona-se com TbLancamento (N:1)
  - Relaciona-se com TbConsultaDebitoVeicular (N:1)
  - Relaciona-se com TbArrecadador (N:1)

- **TbMovimentoLotePagamentoTrbto**: Armazena movimentos de lote de pagamento
  - Relaciona-se com TbLancamento (N:1)
  - Relaciona-se com TbLiquidacao (N:1)
  - Relaciona-se com TbArrecadador (N:1)

- **TbOcorrenciaErroArrecadador**: Mapeia erros do arrecadador para erros BV
  - Relaciona-se com TbArrecadador (N:1)
  - Relaciona-se com TbOcorrenciaErroPagamento (N:1)

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbArrecadador | Tabela | SELECT | Consulta código de arrecadador para validação |
| TbConsultaDebitoVeicular | Tabela | SELECT | Consulta débitos veiculares por código |
| TbLancamento | Tabela | SELECT | Consulta lançamentos por código |
| TbLiquidacao | Tabela | SELECT | Consulta liquidações por código |
| TbStatusLancamento | Tabela | SELECT | Consulta status de lançamento para validação |
| TbOcorrenciaErroArrecadador | Tabela | SELECT | Consulta mapeamento de erros do arrecadador |
| TbOcorrenciaErroPagamento | Tabela | SELECT | Consulta descrição de erros de pagamento |
| TbMovimentoLotePagamentoTrbto | Tabela | SELECT | Consulta movimentos de lote por código de lançamento |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbConsultaDebitoVeicular | Tabela | INSERT | Insere nova consulta de débito veicular |
| TbConsultaDebitoVeicular | Tabela | UPDATE | Atualiza status e informações de débito veicular |
| TbLancamento | Tabela | INSERT | Insere novo lançamento (via procedure) |
| TbLancamento | Tabela | UPDATE | Atualiza status e autenticação de lançamento |
| TbLancamentoDebitoVeicular | Tabela | INSERT | Insere relacionamento entre lançamento e débito |
| TbLancamentoDebitoVeicular | Tabela | UPDATE | Atualiza protocolo e informações de retorno |
| TbMovimentoLotePagamentoTrbto | Tabela | INSERT | Insere movimento de lote de pagamento |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | Spring Boot | Configurações da aplicação por ambiente |
| logback-spring.xml | Leitura | Logback | Configuração de logs em formato JSON |
| *.sql | Leitura | JDBI Repositories | Queries SQL para operações de banco de dados |
| swagger/*.yml | Leitura | Swagger Codegen | Especificação OpenAPI para geração de código |

## 10. Filas Lidas
não se aplica

## 11. Filas Geradas
não se aplica

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| SQL Server (DBSPAG) | Banco de Dados | Banco de dados principal para persistência de débitos veiculares |
| Prometheus | Monitoramento | Coleta de métricas da aplicação |
| Grafana | Observabilidade | Visualização de métricas e dashboards |
| OpenID Connect | Autenticação | Validação de tokens JWT para segurança das APIs |

## 13. Avaliação da Qualidade do Código

**Nota: 7.5/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura hexagonal bem estruturada com separação clara entre camadas (domain, application, common)
- Uso adequado de padrões de projeto (Repository, Service, Mapper)
- Boa cobertura de testes unitários e de integração
- Documentação OpenAPI/Swagger bem definida
- Uso de MapStruct para mapeamento de objetos
- Configuração adequada de observabilidade (Prometheus/Grafana)
- Validações de entrada implementadas
- Tratamento de exceções centralizado

**Pontos de Melhoria:**
- Algumas classes de serviço com múltiplas responsabilidades (ex: RegistrarDebitosVeicularesService)
- Lógica de validação poderia ser mais modular e reutilizável
- Uso de valores mágicos em alguns pontos do código (ex: códigos de erro hardcoded)
- Comentários em português misturados com código em inglês
- Alguns métodos com muitos parâmetros (ex: execPrIncluirLancamento com 73 parâmetros)
- Falta de documentação JavaDoc em algumas classes importantes
- Queries SQL em arquivos separados é bom, mas algumas queries complexas poderiam ter comentários explicativos

## 14. Observações Relevantes

1. **Arquitetura**: O projeto segue arquitetura hexagonal com módulos bem definidos (application, domain, common)

2. **Banco de Dados**: Utiliza JDBI ao invés de JPA/Hibernate, o que oferece mais controle sobre SQL mas requer mais código boilerplate

3. **Stored Procedure**: A inclusão de lançamentos utiliza uma stored procedure (`PrIncluirLancamento`) com 73 parâmetros, o que pode dificultar manutenção

4. **Ambientes**: Configuração para múltiplos ambientes (local, des, qa, uat, prd) bem estruturada

5. **Segurança**: Implementa autenticação via JWT com integração OpenID Connect

6. **Monitoramento**: Infraestrutura completa de observabilidade com Prometheus e Grafana

7. **CI/CD**: Configuração para Jenkins e OpenShift/Kubernetes presente

8. **Testes**: Estrutura de testes separada por tipo (unit, integration, functional)

9. **Logs**: Configuração de logs em formato JSON para facilitar parsing e análise

10. **Validações**: Sistema de validação robusto com mapeamento de erros entre arrecadador e sistema BV