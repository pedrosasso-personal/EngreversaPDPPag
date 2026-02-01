# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-ccbd-base-orch-backoffice-consulta** é um microserviço orquestrador stateless desenvolvido em Java com Spring Boot, responsável por consolidar e fornecer consultas de backoffice relacionadas a contas correntes, clientes, saldos, bloqueios e encerramentos no contexto do Banco Digital (CCBD - Conta Corrente Banco Digital) do Banco Votorantim.

O serviço atua como uma camada de orquestração que integra múltiplos serviços atômicos (conta-corrente, saldo, movimentações, dados cadastrais) para fornecer informações consolidadas através de endpoints REST. Utiliza Apache Camel para orquestração de fluxos e implementa padrões de arquitetura hexagonal (ports and adapters).

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application.java` | Classe principal Spring Boot que inicializa a aplicação |
| `ConsultaController.java` | Controlador REST que expõe os endpoints de consulta |
| `ConsultaSaldoServiceImpl.java` | Implementa lógica de negócio para consultas de saldo |
| `ConsultaContaServiceImpl.java` | Implementa lógica de negócio para consultas de contas |
| `ConsultaClienteServiceImpl.java` | Implementa lógica de negócio para consultas de clientes |
| `ConsultaPessoaServiceImpl.java` | Implementa lógica de negócio para consultas de pessoas |
| `ConsultaFuncionarioServiceImpl.java` | Implementa lógica de negócio para consultas de funcionários |
| `BloqueioServiceImpl.java` | Implementa lógica de negócio para bloqueios/desbloqueios |
| `ConsultaGlobalRepositoryImpl.java` | Repositório que integra com serviços de dados cadastrais globais |
| `ContaCorrenteRepositoryImpl.java` | Repositório que integra com serviço de conta corrente |
| `SaldoRepositoryImpl.java` | Repositório que integra com serviço de saldo |
| `BloqueioRepositoryImpl.java` | Repositório que integra com serviço de movimentações/bloqueios |
| `CamelContextWrapper.java` | Wrapper para contexto Apache Camel |
| `ConsultaSaldoRouter.java` | Define rotas Camel para fluxos de consulta de saldo |
| `ConsultaContaRouter.java` | Define rotas Camel para fluxos de consulta de conta |
| `BloqueioRouter.java` | Define rotas Camel para fluxos de bloqueio |
| `ResourceExceptionHandler.java` | Tratamento centralizado de exceções |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Spring Security OAuth2** (autenticação JWT)
- **Apache Camel 3.0.1** (orquestração de fluxos)
- **Swagger/OpenAPI 2.9.2** (documentação de APIs)
- **Springfox** (geração de documentação Swagger)
- **RestTemplate** (cliente HTTP)
- **Logback** (logging)
- **Micrometer + Prometheus** (métricas)
- **Grafana** (visualização de métricas)
- **JUnit 5 + Mockito** (testes unitários)
- **Rest Assured** (testes funcionais)
- **Pact** (testes de contrato)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Lombok** (redução de boilerplate)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/consulta/saldo-conta-corrente/banco/{banco}/conta/{conta}/tipo/{tipo}` | ConsultaController | Consulta detalhes e saldo de uma conta corrente |
| GET | `/v1/consulta/saldo-conta-corrente/pesquisa` | ConsultaController | Consulta contas por CPF/CNPJ, nome, apelido ou grupo |
| GET | `/v1/consulta/pessoa/nome/{nomePessoa}` | ConsultaController | Consulta pessoa por nome |
| GET | `/v1/consulta/pessoa/doc/{cpfCnpj}` | ConsultaController | Consulta pessoa por CPF/CNPJ |
| GET | `/v1/consulta/pessoa/id/{codigoPessoa}` | ConsultaController | Consulta pessoa por ID |
| GET | `/v1/consulta/conta/doc/{cpfCnpj}` | ConsultaController | Consulta contas por CPF/CNPJ |
| GET | `/v1/consulta/conta/coTitulares` | ConsultaController | Lista co-titulares de uma conta |
| GET | `/v1/consulta/cliente/banco/{banco}` | ConsultaController | Consulta cliente por CPF/CNPJ, nome ou grupo |
| GET | `/v1/consulta/funcionario/login/{login}` | ConsultaController | Consulta funcionário por login |
| GET | `/v1/encerramento-contas` | ConsultaController | Consulta contas em processo de encerramento |
| GET | `/v1/encerramento-clientes` | ConsultaController | Consulta clientes com contas em encerramento |
| GET | `/v1/encerramento-enderecos` | ConsultaController | Consulta endereços de clientes |
| GET | `/v1/consulta/encerramento/endereco` | ConsultaController | Consulta endereço de encerramento de conta |
| GET | `/v1/consulta-cidades/{uf}` | ConsultaController | Consulta cidades por UF |
| GET | `/v1/consulta-paises` | ConsultaController | Lista países |
| GET | `/v1/consulta-uf` | ConsultaController | Lista UFs |
| POST | `/v1/cadastro-endereco` | ConsultaController | Cadastra novo endereço |
| GET | `/v1/consulta/contas/ativaInativa/banco/{banco}` | ConsultaController | Consulta contas ativas/inativas |
| GET | `/v1/consulta/tipo-conta/{codigoTipoConta}` | ConsultaController | Consulta tipo de conta por código |
| GET | `/v1/consulta/saldo-resumido/banco/{banco}/agencia/{agencia}/conta/{conta}/tipo/{tipo}/dataIni/{dataIni}/dataFim/{dataFim}` | ConsultaController | Consulta saldo resumido (diário ou histórico) |
| POST | `/v1/movimentacao-bancaria/bloqueio` | ConsultaController | Inclui bloqueio de movimentações |
| PUT | `/v1/movimentacao-bancaria/bloqueio` | ConsultaController | Libera bloqueio de movimentações |

---

## 5. Principais Regras de Negócio

1. **Validação de Parâmetros de Consulta**: Para consultas de contas/saldo, apenas um parâmetro de busca pode ser informado por vez (CPF/CNPJ, nome, apelido ou grupo).

2. **Filtro de Contas Encerradas**: Ao listar contas, o sistema filtra automaticamente contas que estão em processo de encerramento (exceto as canceladas - situação 4).

3. **Consulta de Saldo Resumido**: O sistema determina automaticamente se deve consultar saldo diário ou histórico baseado na data final informada (se for data atual, consulta diário; caso contrário, histórico).

4. **Validação de Usuário em Bloqueios**: Antes de incluir ou liberar bloqueios, o sistema valida se o código do usuário existe consultando o serviço de dados cadastrais.

5. **Enriquecimento de Dados**: As consultas de conta são enriquecidas com informações de tipo de conta, pessoa gestora, agência, co-titulares e dados do titular.

6. **Distinção de Registros**: Aplica filtros de distinção em listas de contas para evitar duplicidades baseado em banco, conta e tipo.

7. **Tratamento de Encoding**: Realiza encoding/decoding UTF-8 para garantir correta manipulação de caracteres especiais em URLs e respostas.

---

## 6. Relação entre Entidades

**Principais entidades e relacionamentos:**

- **DetalhesContaDTO**: Entidade principal que agrega informações completas de uma conta
  - Relaciona-se com **Banco** (enum BancoEnum)
  - Contém informações de **Saldo** (valores total, disponível, bloqueado, etc)
  - Contém informações de **Bloqueio** (crédito e débito)
  - Contém informações de **Encerramento**
  - Lista de **Co-titulares** (String)
  - Relaciona-se com **Agência**
  - Relaciona-se com **Pessoa Gestora**

- **ContaDTO**: Representa uma conta de forma simplificada
  - Relaciona-se com **Banco**
  - Relaciona-se com **Pessoa** (titular)
  - Pode ter **Officer** associado

- **ClienteDTO/ConsultaClienteDTO**: Representa um cliente
  - Relaciona-se com **Banco**
  - Pode ter múltiplos **Endereços**
  - Pode ter **Grupo Comercial**

- **Bloqueio**: Representa um bloqueio de movimentação
  - Relaciona-se com **Conta**
  - Relaciona-se com **Usuário** (responsável)
  - Pode ser de múltiplos tipos (CRÉDITO, DÉBITO, VALOR)

- **ConsultaContaEncerramentoDTO**: Representa conta em processo de encerramento
  - Relaciona-se com **Modalidade**
  - Relaciona-se com **Categoria**
  - Relaciona-se com **Tipo de Conta**

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

**Observação**: O sistema não acessa diretamente banco de dados. Todas as consultas são realizadas através de APIs REST de outros microserviços atômicos.

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

**Observação**: O sistema não realiza operações diretas de escrita em banco de dados. Operações de inclusão/atualização são delegadas aos microserviços atômicos através de APIs REST.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `application.yml` | Leitura | Spring Boot (resources) | Arquivo de configuração da aplicação com URLs de serviços, perfis e propriedades |
| `logback-spring.xml` | Leitura | Logback (resources ou /usr/etc/log) | Configuração de logs da aplicação |
| `*.yaml` (swagger) | Leitura | Swagger Codegen Maven Plugin | Especificações OpenAPI para geração de código de clientes e providers |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema Integrado | Tipo | Descrição |
|-------------------|------|-----------|
| **sboot-ccbd-base-atom-conta-corrente** | API REST | Serviço atômico para consulta de estado de conta, encerramentos e contas ativas/inativas |
| **sboot-ccbd-base-atom-conta-corrente-dominio** | API REST | Serviço atômico para consulta de modalidades e categorias de conta |
| **sboot-ccbd-base-atom-saldo** | API REST | Serviço atômico para consulta de saldo diário e histórico |
| **sboot-glob-base-atom-cliente-dados-cadastrais** | API REST | Serviço global para consulta de dados cadastrais de pessoas, contas, agências, tipos de conta, cidades, UFs, países e co-titulares |
| **sboot-ccbd-base-atom-movimentacoes** | API REST | Serviço atômico para inclusão e liberação de bloqueios de movimentações |
| **API Gateway OAuth2** | OAuth2 | Serviço de autenticação para obtenção de tokens JWT (https://apigatewaydes.bvnet.bv/auth/oauth/v2/token-jwt) |

**Observação**: Todas as integrações utilizam autenticação OAuth2 com tokens JWT obtidos via `GatewayOAuthService`.

---

## 13. Avaliação da Qualidade do Código

**Nota: 7.5/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura hexagonal (domain, application, common)
- Uso adequado de padrões como Repository, Service, Mapper e DTO
- Cobertura de testes unitários presente em todas as camadas
- Uso de Apache Camel para orquestração de fluxos complexos
- Documentação OpenAPI/Swagger bem estruturada
- Tratamento centralizado de exceções
- Uso de Lombok para redução de boilerplate
- Configurações externalizadas em application.yml
- Implementação de métricas com Prometheus/Grafana

**Pontos de Melhoria:**
- Classe `ConsultaGlobalRepositoryImpl` muito extensa (mais de 400 linhas) com muitas responsabilidades
- Alguns métodos privados poderiam ser extraídos para classes utilitárias
- Uso excessivo de `Optional` em alguns pontos pode dificultar leitura
- Comentários em código são escassos (principalmente em lógicas complexas)
- Alguns nomes de variáveis poderiam ser mais descritivos (ex: `ll`, `c`, `obj`)
- Mappers poderiam utilizar bibliotecas como MapStruct ao invés de mapeamento manual
- Falta de validação de entrada em alguns endpoints (delegada apenas ao controller)
- Alguns testes unitários são muito simples e não cobrem cenários de erro adequadamente

---

## 14. Observações Relevantes

1. **Arquitetura Multi-módulo**: O projeto está organizado em 3 módulos Maven (common, domain, application) seguindo princípios de separação de camadas.

2. **Geração de Código**: Utiliza Swagger Codegen Maven Plugin para gerar automaticamente clientes REST a partir de especificações OpenAPI dos serviços consumidos.

3. **Segurança**: Implementa autenticação OAuth2 com JWT, utilizando biblioteca customizada do Banco Votorantim (`sboot-arqt-base-security-jwt`).

4. **Auditoria**: Integra com biblioteca de trilha de auditoria do BV (`springboot-arqt-base-trilha-auditoria-web`).

5. **Ambientes**: Suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas por ambiente.

6. **Encoding**: Implementa tratamento especial de encoding UTF-8/ISO-8859-1 para lidar com caracteres especiais em respostas de APIs.

7. **Filtros Customizados**: Implementa filtro de distinção customizado (`EspecifcDistinctFilter`) para remover duplicatas baseado em múltiplos campos.

8. **Versionamento de API**: Todos os endpoints seguem padrão de versionamento `/v1/`.

9. **Monitoramento**: Expõe endpoints Actuator na porta 9090 para health checks e métricas.

10. **Pipeline CI/CD**: Configurado para Jenkins com propriedades específicas (jenkins.properties) e infraestrutura como código (infra.yml).

11. **Testes**: Estrutura de testes bem organizada em functional, integration e unit, com suporte a testes de arquitetura via ArchUnit.

12. **Tratamento de Erros**: Enum `CodigoErroEnum` centraliza códigos e mensagens de erro padronizados.