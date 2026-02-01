# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-spag-base-atom-pld-service** é um serviço atômico desenvolvido para gerenciar dados relacionados à **Prevenção à Lavagem de Dinheiro (PLD)** no contexto de pagamentos. O sistema é responsável por registrar e consultar dados cadastrais de clientes e dados transacionais de parceiros do Banco Votorantim, fornecendo APIs REST para integração com outros sistemas. O serviço armazena informações de cadastro (CPF/CNPJ, dados pessoais, renda, PEP) e transações financeiras (emissor, receptor, valor, tipo de transação) em um banco de dados SQL Server.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal Spring Boot que inicializa a aplicação |
| **PldServiceController** | Controlador REST que expõe os endpoints da API |
| **DadosCadastroCommandServiceImpl** | Implementa a lógica de negócio para dados cadastrais |
| **DadosTransacaoCommandServiceImpl** | Implementa a lógica de negócio para dados transacionais |
| **DadosCadastroTransactional** | Camada de acesso a dados para cadastros (repositório) |
| **DadosTransacaoTransactional** | Camada de acesso a dados para transações (repositório) |
| **DadosCadastroEntity** | Entidade JPA representando dados cadastrais |
| **DadosTransacaoEntity** | Entidade JPA representando dados transacionais |
| **DadosCadastroRepository** | Interface Spring Data JPA para operações de cadastro |
| **DadosTransacaoRepository** | Interface Spring Data JPA para operações de transação |
| **DadosCadastroMapper** | Mapeamento entre representações e domínio (cadastro) |
| **DadosTransacaoMapper** | Mapeamento entre representações e domínio (transação) |
| **ExceptionHandler** | Tratamento centralizado de exceções |
| **HibernateConfiguration** | Configuração do Hibernate e JPA |
| **OpenApiConfiguration** | Configuração do Swagger/OpenAPI |
| **DateUtil** | Utilitário para conversão de datas |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Spring Data JPA** (persistência)
- **Hibernate 5.4.32** (ORM)
- **SQL Server** (banco de dados)
- **MapStruct 1.5.3** (mapeamento de objetos)
- **Lombok** (redução de boilerplate)
- **Swagger/Springfox 3.0.0** (documentação de API)
- **Spring Security OAuth2** (autenticação/autorização JWT)
- **Micrometer/Prometheus** (métricas)
- **Logback** (logging)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/registration | PldServiceController | Registra novos dados cadastrais de cliente |
| GET | /v1/registration | PldServiceController | Consulta dados cadastrais com filtros (data, documento, paginação) |
| GET | /v1/registration/{document} | PldServiceController | Consulta dados cadastrais por documento específico |
| POST | /v1/transactional | PldServiceController | Registra novos dados transacionais |
| GET | /v1/transactional | PldServiceController | Consulta dados transacionais com filtros (data, documentos, paginação) |

---

## 5. Principais Regras de Negócio

1. **Atualização de Cadastro**: Ao inserir dados cadastrais, o sistema verifica se já existe cadastro para o CPF/CNPJ. Se existir, atualiza os dados mantendo o ID e data de inclusão originais.

2. **Auditoria Automática**: Todos os registros incluem automaticamente campos de auditoria (login="atom-pld-service", flagAtivo="S", dataInclusao/dataAlteracao).

3. **Busca de CPF por Conta**: Para transações onde o CPF do emissor não é informado, o sistema busca automaticamente através de uma query que relaciona conta/agência com o CPF do usuário.

4. **Conversão de Enums**: O sistema converte valores de enums (FlagPEP, TipoRenda, TipoTransacao) entre representação de banco (char) e domínio (enum).

5. **Paginação e Filtros**: Consultas suportam paginação e filtros por período de datas e documentos.

6. **Validação de Período**: Consultas exigem data inicial e final, convertidas para OffsetDateTime com início/fim do dia.

---

## 6. Relação entre Entidades

**DadosCadastroEntity**:
- Representa dados cadastrais de clientes/parceiros
- Campos principais: CPF/CNPJ, nome, dados pessoais, renda, ocupação, flag PEP
- Relacionamento: Não possui relacionamentos diretos com outras entidades

**DadosTransacaoEntity**:
- Representa transações financeiras
- Campos principais: dados do emissor, dados do receptor, valor, tipo de transação
- Relacionamento: Não possui relacionamentos diretos, mas busca CPF através de query nativa quando necessário

**Relacionamento Indireto**: DadosTransacaoEntity pode buscar CPF através de consulta em tabelas de usuário/conta (tbcontausuariofintech, tbusuariocontafintech, tbrelacaocontausuariofintech).

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbDadoCadastroPLD | tabela | SELECT | Leitura de dados cadastrais para consultas e verificação de existência |
| TbDadoTransacaoPLD | tabela | SELECT | Leitura de dados transacionais para consultas |
| tbcontausuariofintech | tabela | SELECT | Busca de dados de conta de usuário fintech |
| tbusuariocontafintech | tabela | SELECT | Busca de dados de usuário fintech |
| tbrelacaocontausuariofintech | tabela | SELECT | Busca de relacionamento entre conta e usuário |
| TbStatusContaFintech | tabela | SELECT | Busca de status da conta fintech |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbDadoCadastroPLD | tabela | INSERT/UPDATE | Inserção de novos cadastros ou atualização de cadastros existentes |
| TbDadoTransacaoPLD | tabela | INSERT | Inserção de novos dados transacionais |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot | Configurações da aplicação (datasource, profiles, security) |
| application-local.yml | leitura | Spring Boot | Configurações específicas do ambiente local |
| logback-spring.xml | leitura | Logback | Configuração de logs (console, formato JSON) |
| sboot-spag-base-atom-pld-service.yaml | leitura | Swagger Codegen | Especificação OpenAPI para geração de interfaces |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema/Serviço | Descrição |
|-----------------|-----------|
| **SQL Server (DBSPAG)** | Banco de dados principal para persistência de dados cadastrais e transacionais |
| **OAuth2/JWT Provider** | Serviço de autenticação e autorização (apigateway.bvnet.bv) para validação de tokens JWT |
| **Prometheus** | Sistema de coleta de métricas através do endpoint /actuator/prometheus |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (domain, application, common)
- Uso adequado de padrões como Repository, Service, Mapper
- Utilização de tecnologias modernas e boas práticas (Lombok, MapStruct, Spring Boot)
- Configuração adequada de segurança com OAuth2/JWT
- Presença de testes unitários estruturados
- Documentação OpenAPI bem definida

**Pontos de Melhoria:**
- Beans comentados na classe PldServiceConfiguration sem justificativa clara
- Query SQL nativa hardcoded no repositório (DadosCadastroRepository.findCpfByQuery) - poderia usar JPQL ou Criteria API
- Tratamento de exceções genérico em alguns pontos (catch Exception)
- Falta de validações mais robustas nos endpoints (validação de CPF/CNPJ, valores monetários)
- Uso de escapeJava nos logs pode impactar performance
- Código de configuração do Hibernate muito verboso, poderia usar mais convenções do Spring Boot
- Falta de documentação inline em métodos mais complexos
- Ausência de testes de integração visíveis na estrutura analisada

---

## 14. Observações Relevantes

1. **Arquitetura Hexagonal**: O projeto segue princípios de arquitetura hexagonal com separação clara entre domain (regras de negócio), application (infraestrutura) e ports/adapters.

2. **Multi-ambiente**: Configuração preparada para múltiplos ambientes (local, des, qa, uat, prd) com variáveis externalizadas.

3. **Observabilidade**: Sistema preparado para observabilidade com Prometheus, Grafana e logs estruturados em JSON.

4. **Segurança**: Implementa autenticação OAuth2 com JWT, com endpoints públicos configuráveis.

5. **Containerização**: Dockerfile preparado para deploy em containers, com imagem base customizada do Banco Votorantim.

6. **CI/CD**: Configuração Jenkins presente (jenkins.properties) indicando pipeline automatizado.

7. **Auditoria**: Sistema de auditoria integrado através da biblioteca springboot-arqt-base-trilha-auditoria-web.

8. **Paginação**: Todas as consultas implementam paginação para evitar problemas de performance.

9. **Conversores Customizados**: Implementação de conversores JPA para enums, garantindo consistência entre banco e aplicação.

10. **Nomenclatura**: Padrão de nomenclatura em português para entidades de domínio e banco de dados, seguindo convenção da organização.