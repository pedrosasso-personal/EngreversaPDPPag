# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema orquestrador de portabilidade de salário desenvolvido para o Banco Votorantim. O sistema expõe uma API REST que permite o cadastro de solicitações de portabilidade de salário, orquestrando chamadas a serviços atômicos (banco, conta e portabilidade) através do Apache Camel. A aplicação valida dados de entrada, processa a solicitação e retorna o status da operação com um NSU (Número Sequencial Único).

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal Spring Boot que inicializa a aplicação |
| **PortabilidadeController** | Controlador REST que expõe o endpoint de cadastro de portabilidade |
| **PortabilidadeService / PortabilidadeServiceImpl** | Serviço de domínio que orquestra o fluxo de cadastro via Camel |
| **PortabilidadeRouter** | Rota Camel que define o fluxo de orquestração |
| **PortabilidadeProcessor** | Processador Camel que manipula os dados durante o fluxo |
| **PortabilidadeRepositoryImpl** | Implementação de repositório que chama o serviço atômico de portabilidade |
| **BancoRepositoryImpl** | Implementação de repositório para consulta de bancos (não implementado) |
| **ContaRepositoryImpl** | Implementação de repositório para consulta de contas (não implementado) |
| **PortabilidadeMapper** | Mapeador entre representações REST e DTOs de domínio |
| **PortabilidadeValidation** | Validador de regras de negócio (validação de CPF) |
| **CamelContextWrapper** | Wrapper do contexto Camel para gerenciamento de rotas |
| **PortabilidadeDTO / EmpregadorDTO / StatusDTO** | Objetos de transferência de dados do domínio |

---

## 3. Tecnologias Utilizadas

- **Spring Boot** (framework principal)
- **Spring Web** (APIs REST)
- **Spring Security** (autenticação OAuth2/JWT)
- **Apache Camel 3.0.1** (orquestração de fluxos)
- **Swagger/OpenAPI 2.9.2** (documentação de API)
- **Springfox** (integração Swagger com Spring)
- **Lombok** (redução de boilerplate)
- **RestTemplate** (cliente HTTP)
- **Actuator + Prometheus** (monitoramento e métricas)
- **Logback** (logging em formato JSON)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **OpenShift** (orquestração de containers)
- **JUnit 5** (testes unitários)
- **Rest Assured** (testes de API)
- **Pact** (testes de contrato)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/banco-digital/contas/portabilidade/salario | PortabilidadeController | Cadastra uma solicitação de portabilidade de salário. Recebe dados do banco de folha, empregador e retorna NSU e status |

**Headers obrigatórios:**
- codigoBanco (Integer)
- numeroAgencia (String)
- numeroConta (Long)
- tipoConta (Integer)

---

## 5. Principais Regras de Negócio

1. **Validação de CPF**: O CPF do usuário autenticado deve ter exatamente 11 caracteres
2. **Autenticação obrigatória**: Todas as requisições devem ser autenticadas via OAuth2/JWT
3. **Orquestração de serviços**: O sistema orquestra chamadas a três serviços atômicos (banco, conta e portabilidade)
4. **Geração de NSU**: Cada solicitação de portabilidade gera um Número Sequencial Único
5. **Retorno de status**: O sistema retorna o status da solicitação (código e descrição)

---

## 6. Relação entre Entidades

**PortabilidadeDTO** (entidade principal)
- Contém: numeroIspbBancoFolha, nsu, status
- Relacionamento: 1:1 com **EmpregadorDTO**
- Relacionamento: 1:1 com **StatusDTO**

**EmpregadorDTO**
- Contém: numeroCpfCnpj, razaoSocial
- Pertence a: **PortabilidadeDTO**

**StatusDTO**
- Contém: codigo, descricao
- Pertence a: **PortabilidadeDTO**

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot (startup) | Arquivo de configuração da aplicação com profiles (local, des, qa, uat, prd) |
| logback-spring.xml | leitura | Logback (runtime) | Configuração de logs em formato JSON para stdout |
| sboot-ccbd-base-orch-portabilidade.yaml | leitura | Swagger Codegen (build) | Especificação OpenAPI para geração de interfaces REST |

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
| **sboot-ccbd-base-atom-portabilidade** | API REST | Serviço atômico de cadastro de portabilidade de salário (POST) |
| **sboot-ccbd-base-atom-portabilidade (banco)** | API REST | Serviço atômico de consulta de bancos (não implementado) |
| **sboot-ccbd-base-atom-portabilidade (conta)** | API REST | Serviço atômico de consulta de contas (não implementado) |
| **OAuth2/JWT Provider** | Autenticação | Servidor de autenticação para validação de tokens JWT (api-digitaldes.bancovotorantim.com.br) |

**Observação**: As integrações com os serviços de banco e conta estão preparadas mas não implementadas (código comentado).

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo Clean Architecture (domain, application, infrastructure)
- Uso adequado de padrões como Repository, Service e Mapper
- Separação clara de responsabilidades entre camadas
- Boa documentação via Swagger/OpenAPI
- Configuração adequada de profiles para diferentes ambientes
- Uso de Lombok para reduzir boilerplate
- Implementação de segurança com OAuth2/JWT
- Logs estruturados em JSON

**Pontos Negativos:**
- **Código incompleto**: Implementações de BancoRepository e ContaRepository estão vazias/comentadas
- **Lógica de serviço problemática**: PortabilidadeServiceImpl envia string vazia ao invés do objeto portabilidade
- **Falta de tratamento de exceções**: Tratamento genérico de exceções sem logging adequado
- **Validação insuficiente**: Apenas valida tamanho do CPF, sem validação de dígitos verificadores
- **Falta de testes**: Todos os testes estão marcados como NAO_ENVIAR
- **Documentação incompleta**: README genérico sem informações específicas do projeto
- **Configuração de segurança**: Uso de RestTemplate sem configuração de timeouts
- **Ausência de circuit breaker**: Sem proteção contra falhas em cascata nas integrações

---

## 14. Observações Relevantes

1. **Projeto em desenvolvimento**: O sistema aparenta estar em fase inicial, com funcionalidades core não implementadas (consultas de banco e conta)

2. **Arquitetura de orquestração**: Utiliza Apache Camel para orquestração, mas o fluxo atual é simplificado (apenas chama o repositório de portabilidade)

3. **Segurança**: Implementa autenticação via JWT com integração ao servidor OAuth2 do Banco Votorantim

4. **Ambientes**: Configurado para 4 ambientes (des, qa, uat, prd) com URLs específicas para cada

5. **Monitoramento**: Configurado com Actuator e Prometheus para métricas, com endpoints de health em porta separada (9090)

6. **Containerização**: Preparado para deploy em Docker/OpenShift com configurações de probes (liveness/readiness)

7. **Problema crítico**: A implementação do serviço envia string vazia ao invés do objeto de portabilidade, o que provavelmente causará falha na integração

8. **Auditoria**: Configurado para trilha de auditoria através da biblioteca bv-arqt

9. **Padrão de nomenclatura**: Segue padrão corporativo do Banco Votorantim (prefixo sboot-ccbd-base)

10. **Geração de código**: Utiliza Swagger Codegen para gerar interfaces REST a partir da especificação OpenAPI