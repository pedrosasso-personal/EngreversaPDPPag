# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-ccbd-base-orch-consulta-cc-cliente** é um serviço orquestrador (orchestrator) desenvolvido em Java com Spring Boot, responsável por fornecer informações sobre contas correntes de clientes do Banco Digital. O sistema atua como intermediário entre múltiplos serviços atômicos, consolidando dados de diferentes fontes (conta corrente, dados cadastrais, participantes PIX, contas fintech) e aplicando regras de validação de titularidade e situação de contas. Utiliza Apache Camel para orquestração de fluxos e integra-se com diversos microsserviços através de APIs REST.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `ConsultaCcClienteController` | Controller REST (v1) que expõe endpoints para consulta e validação de contas correntes |
| `ConsultaCcClienteControllerV2` | Controller REST (v2) com suporte adicional para validação de contas fintech |
| `ConsultaCcClienteService` | Serviço de domínio que coordena a execução das rotas Camel |
| `ConsultaCcClienteRouter` | Rota Camel para orquestração do fluxo de consulta de conta corrente |
| `ValidaCcClienteRouter` | Rota Camel para validação de situação de conta sem fintech |
| `ValidaCcClienteComFintechRouter` | Rota Camel para validação de situação de conta com suporte a fintech |
| `ContaCorrenteRepositoryImpl` | Implementação de repositório para integração com serviço de conta corrente |
| `GlobalRepositoryImpl` | Implementação de repositório para integração com serviços globais (bancos, pessoas) |
| `SpagPixxRepositoryImpl` | Implementação de repositório para integração com serviço de participantes PIX |
| `SpagContaFintechRepositoryImpl` | Implementação de repositório para integração com serviço de contas fintech |
| `CamelContextWrapper` | Wrapper do contexto Camel para gerenciamento de rotas e templates |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Apache Camel 3.2.0** (orquestração de fluxos)
- **Spring Security OAuth2** (autenticação e autorização JWT)
- **Swagger/OpenAPI 3.0** (documentação de APIs)
- **Springfox 3.0.0** (geração de documentação Swagger)
- **Maven** (gerenciamento de dependências e build)
- **Micrometer + Prometheus** (métricas e monitoramento)
- **Logback** (logging)
- **JUnit 5 + Mockito** (testes unitários)
- **RestAssured** (testes funcionais)
- **Pact** (testes de contrato)
- **Docker** (containerização)
- **Kubernetes/OpenShift** (orquestração de containers)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/banco-digital/contas` | `ConsultaCcClienteController` | Consulta informações completas de uma conta corrente |
| POST | `/v1/banco-digital/contas/validacao` | `ConsultaCcClienteController` | Valida situação de conta(s) e titularidade (sem fintech) |
| POST | `/v2/banco-digital/contas/validacao` | `ConsultaCcClienteControllerV2` | Valida situação de conta(s) e titularidade (com suporte fintech) |

---

## 5. Principais Regras de Negócio

1. **Validação de Titularidade**: Verifica se o documento informado corresponde ao titular da conta através de consulta aos dados cadastrais
2. **Validação de Situação de Conta**: Valida se a conta está apta para operações de crédito, débito ou movimentações gerais
3. **Suporte a Contas Fintech**: Para contas não encontradas no sistema principal, busca informações em contas fintech vinculadas
4. **Validação de Banco BV**: Aplica regras específicas para contas do Banco Votorantim (códigos 161 e 436)
5. **Validação de Tipo de Transação**: Diferencia validações para operações de DÉBITO, CRÉDITO ou MOVIMENTAÇÕES
6. **Enriquecimento de Dados**: Consolida informações de múltiplas fontes (participantes PIX, lista de bancos, dados cadastrais)
7. **Tratamento de Exceções de Negócio**: Retorna códigos específicos para situações como conta não encontrada, titularidade inválida, status inválido

---

## 6. Relação entre Entidades

**Principais entidades de domínio:**

- **ConsultaCcCliente**: Representa os dados completos de uma conta corrente (saldos, bloqueios, situação, titular)
- **ValidaSituacaoConta**: Agregador de validações contendo lista de bancos e pessoas/contas a validar
- **PessoaConta**: Representa uma pessoa e sua conta para validação (documento, nome, agência, conta, tipo transação, saldo)
- **InfoConta**: DTO com informações básicas para consulta (banco, agência, conta, tipo)
- **Pessoa**: Dados cadastrais de uma pessoa (CPF/CNPJ, nome, conta, agência)
- **Banco**: Informações de instituição bancária (código, ISPB, nome)
- **Participant**: Participante do sistema PIX
- **SituacaoConta**: Resultado de validação contendo saldo disponível

**Relacionamentos:**
- ValidaSituacaoConta contém múltiplas PessoaConta e Bancos
- ConsultaCcCliente é enriquecido com dados de Pessoa
- PessoaConta é validada contra Banco e Pessoa

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

*Observação: O sistema não acessa diretamente banco de dados, apenas consome APIs REST de outros microsserviços.*

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

*Observação: O sistema não realiza operações de escrita em banco de dados.*

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Descrição |
|-----------------|----------|-------------------------|-----------|
| `application.yml` | Leitura | `src/main/resources` | Configurações da aplicação (profiles, URLs de serviços, OAuth2) |
| `logback-spring.xml` | Leitura | `/usr/etc/log` (runtime) | Configuração de logs da aplicação |
| `swagger/*.yaml` | Leitura | `src/main/resources/swagger` | Definições OpenAPI dos contratos de API |
| `swagger-client/*.yaml` | Leitura | `src/main/resources/swagger-client` | Definições OpenAPI dos serviços consumidos |

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
| `sboot-ccbd-base-atom-conta-corrente` | API REST | Serviço atômico para consulta e validação de contas correntes |
| `sboot-glob-base-atom-cliente-dados-cadastrais` | API REST | Serviço atômico para consulta de dados cadastrais de clientes |
| `sboot-glob-base-atom-lista-bancos` | API REST | Serviço atômico para consulta de lista de bancos |
| `sboot-spag-pixx-atom-participantes` | API REST | Serviço atômico para consulta de participantes do sistema PIX |
| `sboot-spag-pixx-atom-consulta-conta-fintech` | API REST | Serviço atômico para consulta de contas fintech |
| OAuth2 JWT Provider | OAuth2 | Servidor de autenticação para validação de tokens JWT |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (domain, application)
- Uso adequado de padrões como Repository, Service e Controller
- Implementação de testes unitários, integração e funcionais
- Uso de Apache Camel para orquestração de fluxos complexos
- Documentação OpenAPI completa
- Tratamento de exceções estruturado com códigos de erro específicos
- Uso de Lombok para redução de boilerplate

**Pontos de Melhoria:**
- Alguns processadores Camel poderiam ser simplificados
- Falta de comentários explicativos em lógicas mais complexas
- Algumas classes de teste com métodos muito extensos
- Configurações hardcoded em alguns pontos (ex: códigos de banco)
- Poderia haver mais uso de constantes ao invés de strings literais
- Alguns métodos com múltiplas responsabilidades (ex: validações e transformações juntas)

---

## 14. Observações Relevantes

1. **Arquitetura Hexagonal**: O projeto segue princípios de arquitetura hexagonal com clara separação entre domínio (domain) e infraestrutura (application)

2. **Versionamento de API**: Implementa versionamento de endpoints (v1 e v2) para evolução controlada da API

3. **Orquestração com Camel**: Utiliza Apache Camel para implementar padrões de integração empresarial (EIP) de forma declarativa

4. **Segurança**: Implementa autenticação OAuth2 com JWT em todos os endpoints

5. **Observabilidade**: Integração com Prometheus/Grafana para métricas e monitoramento

6. **Multi-ambiente**: Suporte a múltiplos ambientes (des, qa, uat, prd) com configurações específicas

7. **Containerização**: Preparado para execução em containers Docker/Kubernetes

8. **Testes Abrangentes**: Cobertura de testes em múltiplas camadas (unitários, integração, funcionais, contrato)

9. **Padrão BV**: Segue padrões e convenções do Banco Votorantim (nomenclatura, estrutura, bibliotecas corporativas)

10. **Dependências Corporativas**: Utiliza bibliotecas internas do BV para segurança, auditoria e tracing

---