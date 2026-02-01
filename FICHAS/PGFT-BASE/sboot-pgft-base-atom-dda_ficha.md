# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-pgft-base-atom-dda** é um serviço atômico desenvolvido em Spring Boot para gestão de DDA (Débito Direto Autorizado). O sistema permite consultar o status de adesão de clientes ao serviço DDA, retornando informações como data de adesão, dados de contato (email e telefone), operadora telefônica e preferências de notificação. O serviço é exposto via API REST e utiliza autenticação OAuth2 com JWT.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application.java` | Classe principal que inicializa a aplicação Spring Boot com suporte a OAuth2 Resource Server |
| `DdaController.java` | Controlador REST que expõe o endpoint de consulta de status DDA |
| `DdaService.java` | Serviço de domínio que implementa a lógica de negócio para consulta de clientes DDA |
| `DdaRepositoryImpl.java` | Implementação do repositório que acessa o banco de dados Sybase via JDBI |
| `ClienteRowMapper.java` | Mapper responsável por converter ResultSet em objetos de domínio Cliente |
| `Cliente.java` | Entidade de domínio representando um cliente DDA |
| `Telefone.java` | Entidade de domínio representando dados telefônicos do cliente |
| `ClienteHelper.java` | Classe utilitária para conversão de indicadores e validação de datas |
| `ConversorHelper.java` | Classe utilitária para conversão entre objetos de domínio e representações REST |
| `CpfCnpjJWTHelper.java` | Helper para extração de CPF/CNPJ do token JWT |
| `DatabaseConfiguration.java` | Configuração do JDBI para acesso ao banco de dados |
| `DdaConfiguration.java` | Configuração dos beans de serviço e repositório |
| `OpenApiConfiguration.java` | Configuração do Swagger/OpenAPI para documentação da API |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Spring Security OAuth2** (autenticação via JWT)
- **JDBI 3.9.1** (acesso a banco de dados)
- **Sybase ASE 16.3** (banco de dados)
- **Swagger/Springfox 2.9.2** (documentação de API)
- **Lombok** (redução de boilerplate)
- **JUnit 5** (testes unitários)
- **Mockito** (mocks para testes)
- **Rest Assured** (testes funcionais)
- **Pact** (testes de contrato)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Micrometer/Prometheus** (métricas)
- **Logback** (logging)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/atacado/dda/status` | `DdaController` | Consulta o status de adesão DDA do cliente autenticado (CPF/CNPJ extraído do token JWT) |

---

## 5. Principais Regras de Negócio

1. **Autenticação obrigatória**: O endpoint requer autenticação OAuth2 com token JWT válido
2. **Identificação do cliente**: O CPF/CNPJ do cliente é extraído automaticamente do token JWT
3. **Conversão de indicadores**: Campos vazios ou nulos são convertidos para "N" (Não), valores preenchidos para "S" (Sim)
4. **Dados de contato condicionais**: Email e telefone só são retornados se os respectivos indicadores de atualização estiverem ativos
5. **Mapeamento de operadora**: O código da operadora telefônica é convertido para nome (VIVO, TIM, OI, CLARO, NEXTEL, OUTROS)
6. **Retorno vazio**: Se o cliente não for encontrado, retorna lista vazia ao invés de erro
7. **Tratamento de exceções**: Erros internos retornam HTTP 500 sem expor detalhes técnicos

---

## 6. Relação entre Entidades

**Cliente** (entidade principal)
- Atributos: código, numeroCpfCnpj, dataAdesao, dataCancelamento, atualizacaoPorEmail, enderecoEmail, atualizacaoPorSms, condicoesGerais, arquivoVarredura
- Relacionamento: 1 Cliente possui 0..1 Telefone (composição)

**Telefone** (entidade dependente)
- Atributos: numeroDDD, numeroTelefone, codigoOperadora, nomeOperadora
- Relacionamento: pertence a 1 Cliente

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbClienteDDA | tabela | SELECT | Tabela principal contendo dados de clientes cadastrados no serviço DDA, incluindo informações de adesão, contato e preferências |

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot | Arquivo de configuração da aplicação com profiles (local, des, qa, uat, prd) |
| logback-spring.xml | leitura | Logback | Configuração de logging da aplicação |
| getCliente.sql | leitura | DdaRepositoryImpl | Query SQL para consulta de dados do cliente DDA |
| sboot-pgft-base-atom-dda.yaml | leitura | OpenApiConfiguration | Especificação OpenAPI/Swagger da API |

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
| Servidor OAuth2/JWT | API REST | Validação de tokens JWT através do endpoint jwks.json para autenticação de usuários |
| Banco Sybase ASE | Banco de dados | Acesso ao banco DBPGF_TES para consulta de dados de clientes DDA |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem organizada seguindo padrões hexagonais (domain, application, infrastructure)
- Separação clara de responsabilidades entre camadas
- Uso adequado de injeção de dependências
- Boa cobertura de testes unitários
- Uso de Lombok para reduzir boilerplate
- Configuração adequada de profiles para diferentes ambientes
- Documentação via Swagger/OpenAPI
- Uso de helpers para lógica de conversão

**Pontos de Melhoria:**
- Tratamento de exceções genérico no controller (captura Exception ao invés de exceções específicas)
- Falta de validação de entrada (CPF/CNPJ)
- Logs poderiam ser mais estruturados
- Ausência de cache para consultas frequentes
- Testes funcionais e de integração praticamente vazios
- Falta de documentação inline em alguns métodos mais complexos

---

## 14. Observações Relevantes

1. **Segurança**: O sistema utiliza OAuth2 com JWT, extraindo automaticamente o CPF/CNPJ do usuário autenticado, evitando que o cliente informe manualmente sua identificação
2. **Multi-ambiente**: Configuração preparada para múltiplos ambientes (local, des, qa, uat, prd) com diferentes conexões de banco e URLs de validação JWT
3. **Monitoramento**: Endpoints do Actuator expostos na porta 9090 para health checks e métricas Prometheus
4. **Containerização**: Dockerfile configurado com OpenJ9 para otimização de memória
5. **Infraestrutura como código**: Arquivo infra.yml define configurações de deploy no Kubernetes/OpenShift
6. **Pipeline CI/CD**: Configuração Jenkins presente (jenkins.properties) para automação de build e deploy
7. **Arquitetura modular**: Projeto dividido em módulos Maven (common, domain, application) facilitando manutenção
8. **Testes de arquitetura**: Profile Maven específico para validação de regras arquiteturais via ArchUnit