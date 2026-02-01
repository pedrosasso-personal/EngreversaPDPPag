# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-spag-base-orch-zeragem-cp** é um microserviço orquestrador responsável por realizar o processo de zeragem diária de contas de Carteira de Pagamento (CP). O sistema consulta parametrizações ativas, valida se já houve execução de zeragem para a data informada, verifica saldos de contas correntes e realiza operações de resgate ou aplicação para zerar o saldo das contas CP conforme regras parametrizadas. Utiliza Apache Camel para orquestração de fluxos e integra-se com outros serviços do ecossistema SPAG e CCBD do Banco Votorantim.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot que inicializa a aplicação |
| `ZeramentoCpController` | Controlador REST que expõe o endpoint de inclusão de zeragem |
| `ZeramentoCpService` | Serviço de domínio que inicia o fluxo de zeragem via Apache Camel |
| `BusinessDevelopmentService` | Serviço de negócio que contém as regras de filtragem, definição e inclusão de zeragens |
| `ZeramentoCpRepositoryImpl` | Implementação do repositório que realiza chamadas HTTP para APIs externas |
| `ZeramentoCpRouter` | Roteador Apache Camel que define o fluxo de processamento de zeragens |
| `CamelContextWrapper` | Wrapper do contexto Camel para gerenciamento de rotas |
| `ExceptionControllerHandler` | Tratador centralizado de exceções da aplicação |
| `ConsultaSaldoCcbdMapper` | Mapper para conversão de dados de consulta de saldo |
| `ZeragemCpMapper` | Mapper para conversão de objetos de zeragem |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Apache Camel 3.4.1** (orquestração de fluxos)
- **Spring Security OAuth2** (autenticação e autorização)
- **RestTemplate** (cliente HTTP)
- **Swagger/OpenAPI 3.0** (documentação de API)
- **Lombok** (redução de boilerplate)
- **Logback** (logging)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Springfox** (geração de documentação Swagger)
- **Micrometer/Prometheus** (métricas e monitoramento)
- **JUnit 5 e Mockito** (testes)
- **GSON** (serialização/deserialização JSON)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/zeragem-cp` | `ZeramentoCpController` | Realiza inclusão diária de zeragem para uma data de referência e código de banco específicos |

---

## 5. Principais Regras de Negócio

1. **Validação de Execução Diária**: Verifica se já foi executada zeragem para a data de referência informada, evitando duplicidade de processamento.

2. **Filtragem de Parametrizações Ativas**: Busca todas as parametrizações ativas de zeragem CP e filtra apenas aquelas que não possuem ocorrência de zeragem para a data e conta específicas.

3. **Consulta de Saldo**: Para cada parametrização filtrada, consulta o saldo disponível da conta corrente/poupança associada.

4. **Definição de Tipo de Operação**: Compara o saldo disponível com o valor parametrizado de zeragem:
   - Se saldo > valor parametrizado: operação de **APLICAÇÃO** (transfere excedente para CP)
   - Se saldo < valor parametrizado: operação de **RESGATE** (transfere de CP para conta)
   - Calcula o valor absoluto da diferença como valor da operação

5. **Validação de Tipo de Conta**: Tenta primeiro validar como Conta Corrente (tipo 5), se falhar, tenta como Conta Poupança (tipo 6).

6. **Inclusão de Zeragens**: Após definir todas as operações necessárias, inclui as zeragens no sistema de gestão.

---

## 6. Relação entre Entidades

**Entidades principais:**

- **ZeragemCP**: Representa uma solicitação de zeragem com data de referência e código do banco
- **ParametrizacaoCp**: Contém as configurações de zeragem (conta, CNPJ, valor, banco, etc.)
- **ZeragemCpRequest**: Representa uma solicitação de inclusão de zeragem com todos os dados necessários (documento, tipo, valor, conta, etc.)
- **ConsultaSaldoResponse**: Resposta da consulta de saldo contendo informações da conta e valores disponíveis

**Relacionamentos:**
- Uma `ZeragemCP` pode gerar múltiplas `ZeragemCpRequest` baseadas nas `ParametrizacaoCp` ativas
- Cada `ParametrizacaoCp` está associada a uma conta específica (numeroConta + CNPJ)
- Uma `ConsultaSaldoResponse` contém informações de uma ou mais contas de um cliente

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

*Observação: O sistema não acessa diretamente banco de dados, todas as operações são realizadas via APIs REST.*

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

*Observação: O sistema não atualiza diretamente banco de dados, todas as operações de escrita são realizadas via APIs REST.*

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `application.yml` | leitura | `application/src/main/resources` | Arquivo de configuração da aplicação com profiles (local, des, qa, uat, prd) |
| `logback-spring.xml` | leitura | `/usr/etc/log` (runtime) | Configuração de logging da aplicação |
| `swagger/*.yaml` | leitura | `application/src/main/resources/swagger` | Especificações OpenAPI para geração de clientes e documentação |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| **springboot-spag-base-gestao** | API REST | Sistema de gestão SPAG para validação de execuções, consulta de parametrizações, verificação de ocorrências e inclusão de zeragens |
| **sboot-ccbd-base-orch-consulta-cc-cliente** | API REST | Serviço de consulta e validação de contas correntes de clientes do banco digital |
| **API Gateway BV** | OAuth2 | Gateway de autenticação para obtenção de tokens JWT |

**Endpoints integrados:**
- `GET /zeragem-cp/execucao/{data}` - Valida se já houve execução de zeragem
- `GET /zeragem-cp/parametrizacao` - Consulta parametrizações ativas
- `GET /zeragem-cp/ocorrencia/{data}/numero-conta/{conta}` - Verifica ocorrência de zeragem
- `POST /zeragem-cp` - Inclui nova zeragem
- `POST /v1/banco-digital/contas/validacao` - Valida conta e consulta saldo

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura modular (application, domain, common)
- Uso adequado de padrões como Repository, Service e Mapper
- Implementação de tratamento de exceções centralizado
- Uso de Apache Camel para orquestração de fluxos complexos
- Configuração adequada de profiles para diferentes ambientes
- Documentação OpenAPI/Swagger implementada
- Uso de Lombok para reduzir boilerplate
- Implementação de logs estruturados

**Pontos de Melhoria:**
- Presença de setters públicos em `ZeramentoCpRepositoryImpl` que quebram encapsulamento
- Uso de `LinkedHashMap` com cast não tipado em `consultarParametrizacoesAtivas`
- Tratamento genérico de exceções em alguns pontos poderia ser mais específico
- Falta de validação de entrada em alguns métodos
- Alguns métodos com múltiplas responsabilidades (ex: `consultarSaldo` tenta dois tipos de conta)
- Comentários em português misturados com código em inglês
- Falta de testes unitários nos arquivos enviados (apenas estrutura de teste)
- Uso de `System.out` implícito em alguns logs poderia ser melhorado

---

## 14. Observações Relevantes

1. **Arquitetura Multi-módulo**: O projeto está organizado em três módulos Maven (application, domain, common), seguindo boas práticas de separação de camadas.

2. **Segurança**: Implementa autenticação OAuth2 com JWT, integrando-se com o API Gateway do Banco Votorantim.

3. **Resiliência**: Configuração de timeouts (60 segundos) para chamadas HTTP e interceptadores de logging para debug.

4. **Monitoramento**: Exposição de métricas via Actuator e Prometheus na porta 9090.

5. **Containerização**: Dockerfile configurado para deploy em ambiente Kubernetes/OpenShift.

6. **Infraestrutura como Código**: Arquivo `infra.yml` define configurações de deployment para múltiplos ambientes (des, qa, uat, prd).

7. **Profiles**: Suporte a múltiplos ambientes com configurações específicas via Spring Profiles.

8. **Geração de Código**: Uso de Swagger Codegen para gerar clientes de APIs externas automaticamente.

9. **Logging**: Configuração de logging JSON estruturado para facilitar análise e monitoramento.

10. **Dependências de Segurança**: Projeto inclui correções de CVEs conhecidas (ex: tomcat-embed-core 9.0.99).