# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-spag-base-orch-integracao-fintech** é um serviço de orquestração desenvolvido em Spring Boot que atua como intermediário entre sistemas de gestão de fintechs e serviços de bloqueio de contas. Sua principal função é consumir mensagens de uma fila RabbitMQ contendo solicitações de registro de endereços relacionadas a ordens judiciais (BJUD), consultar informações de pessoas físicas ou jurídicas em um sistema de gestão, e atualizar dados de bloqueio de conta com endereço e saldo obtidos. O fluxo é orquestrado utilizando Apache Camel para roteamento e processamento de mensagens.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal que inicializa a aplicação Spring Boot |
| `IntegracaoFintechConfiguration` | Configuração de beans, RestTemplate com autenticação básica, CamelContext e serviços |
| `RabbitMQConfiguration` | Configuração de conexão, filas e listeners do RabbitMQ |
| `FilaRabbitListener` | Listener que consome mensagens da fila de processamento de endereços BJUD |
| `IntegracaoFintechService` | Serviço de domínio que dispara o fluxo de orquestração via Camel |
| `IntegracaoFintechRouter` | Roteador Camel que define o fluxo de orquestração (consulta PF/PJ e atualização de ordem judicial) |
| `AtomBloqueioContaProcessor` | Processor Camel que extrai dados da solicitação e armazena em propriedades do Exchange |
| `PessoaFisicaProcessor` | Processor que processa resposta de consulta de pessoa física e mapeia endereço e saldo |
| `PessoaJuridicaProcessor` | Processor que processa resposta de consulta de pessoa jurídica e mapeia endereço e saldo |
| `ProcessarRegistroProcessor` | Processor que monta o objeto de requisição para atualização de ordem judicial |
| `SpagBaseGestaoRepositoryImpl` | Implementação de repositório para consulta de pessoas físicas e jurídicas |
| `BloqueioContaRepositoryImpl` | Implementação de repositório para atualização de ordem judicial no sistema de bloqueio de conta |
| `ProcessorMapper` | Utilitário para mapeamento de dados entre domínios (gestão -> bloqueio conta) |
| `IntegracaoFintechMapper` | Mapper para conversão de payload JSON em objeto de domínio |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Spring AMQP / RabbitMQ** (mensageria)
- **Apache Camel 3.0.1** (orquestração e roteamento)
- **Swagger/Springfox 2.9.2** (documentação de API)
- **Spring Actuator + Micrometer + Prometheus** (monitoramento e métricas)
- **RestTemplate** (cliente HTTP)
- **Gson** (serialização/deserialização JSON)
- **Logback** (logging)
- **JUnit 5 + Mockito** (testes unitários)
- **Rest Assured** (testes funcionais)
- **Pact** (testes de contrato)
- **Docker** (containerização)
- **Maven** (gerenciamento de dependências)
- **OAuth2 / JWT** (segurança e autenticação)

---

## 4. Principais Endpoints REST

Não se aplica. O sistema não expõe endpoints REST próprios; ele atua como consumidor de mensagens RabbitMQ e cliente de APIs externas.

---

## 5. Principais Regras de Negócio

- **Roteamento por tipo de documento**: Se o número de documento possui 14 caracteres, é tratado como CNPJ (pessoa jurídica); caso contrário, como CPF (pessoa física).
- **Consulta de dados de pessoa**: O sistema consulta o serviço `spag-base-gestao` para obter informações completas da pessoa (endereços, contas, saldo).
- **Seleção de endereço de correspondência**: Prioriza o endereço marcado como correspondência; se não houver, utiliza o primeiro endereço disponível.
- **Cálculo de saldo**: Busca o saldo da conta específica informada na solicitação.
- **Atualização de ordem judicial**: Envia os dados de endereço e saldo para o serviço `spag-base-atom-bloqueio-conta` para atualização da ordem judicial.
- **Tratamento de erros**: Em caso de falha na consulta de pessoa, retorna valores padrão (endereço vazio e saldo zero).

---

## 6. Relação entre Entidades

**Principais entidades de domínio:**

- **SolicitacaoRegistro**: Contém `id`, `numeroDocumento` e `nuConta` (dados da solicitação recebida via fila).
- **PessoaFisica**: Representa pessoa física com CPF, nome, endereços, contas, telefones, documentos, etc.
- **PessoaJuridica**: Representa pessoa jurídica com CNPJ, razão social, endereços, contas, telefones, beneficiários, etc.
- **PessoaBase**: Classe base abstrata para PessoaFisica e PessoaJuridica, contendo listas de contas, endereços e anexos.
- **PessoaWrapper**: Wrapper que encapsula listas de PF e PJ e indica o tipo de pessoa.
- **EnderecoFintech**: Endereço retornado pelo sistema de gestão.
- **ContaFintech**: Conta bancária com número, saldo, tipo e status.
- **Endereco**: Endereço no formato esperado pelo sistema de bloqueio de conta.
- **RequestAtualizarAtomBloqueioConta**: Requisição para atualização de ordem judicial, contendo `id`, `saldo` e `endereco`.

**Relacionamentos:**
- `SolicitacaoRegistro` → dispara consulta de `PessoaFisica` ou `PessoaJuridica`.
- `PessoaFisica`/`PessoaJuridica` → contém listas de `EnderecoFintech` e `ContaFintech`.
- `PessoaWrapper` → agrupa PF ou PJ para processamento unificado.
- `RequestAtualizarAtomBloqueioConta` → construído a partir de dados de `PessoaWrapper` e `SolicitacaoRegistro`.

---

## 7. Estruturas de Banco de Dados Lidas

Não se aplica. O sistema não acessa diretamente bancos de dados; consome APIs REST de outros serviços.

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema não atualiza diretamente bancos de dados; envia requisições HTTP para APIs externas que realizam as atualizações.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `application.yml` | Leitura | Spring Boot (startup) | Arquivo de configuração da aplicação (profiles, endpoints, credenciais, RabbitMQ) |
| `logback-spring.xml` | Leitura | Logback (startup) | Configuração de logs (formato JSON, níveis de log) |
| `rabbitmq_definitions.json` | Leitura | RabbitMQ (docker-compose) | Definições de filas, exchanges e bindings para ambiente local |

---

## 10. Filas Lidas

- **`events.business.SPAG-BASE.processarEnderecosBjud`**: Fila RabbitMQ consumida pelo listener `FilaRabbitListener`. Contém mensagens JSON com solicitações de registro de endereços relacionadas a ordens judiciais (BJUD).

---

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas; apenas consome.

---

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| **spag-base-gestao** | API REST | Serviço de gestão de usuários fintech. Consultado para obter dados de pessoa física (endpoint `/gestao-bco-liquidante/usuarioFintech/pf/{cpf}`) e pessoa jurídica (endpoint `/gestao-bco-liquidante/usuarioFintech/pj/{cnpj}`). Utiliza autenticação básica. |
| **spag-base-atom-bloqueio-conta** | API REST | Serviço de bloqueio de conta. Recebe requisições PUT para atualizar ordem judicial (endpoint `/v1/atualizar-ordem-judicial`) com dados de endereço e saldo. Utiliza autenticação OAuth2 via API Gateway. |
| **API Gateway (OAuth2)** | OAuth2 | Gateway de autenticação para obtenção de tokens JWT utilizados nas chamadas ao serviço de bloqueio de conta. |
| **RabbitMQ** | Mensageria | Broker de mensagens utilizado para consumo de eventos de processamento de endereços BJUD. |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura modular (application, domain, common).
- Uso adequado de padrões como Repository, Service e Processor.
- Configuração externalizada em `application.yml` com profiles para diferentes ambientes.
- Presença de testes unitários, de integração e funcionais.
- Uso de Apache Camel para orquestração, facilitando manutenção do fluxo.
- Logging estruturado em JSON.
- Documentação via Swagger.

**Pontos de Melhoria:**
- **Tratamento de erros**: Captura genérica de exceções em alguns pontos (ex: `FilaRabbitListener`), retornando `null` ou valores padrão sem propagação adequada de erros.
- **Logs**: Alguns logs em português, falta de padronização de idioma.
- **Testes**: Cobertura de testes pode ser ampliada; alguns testes estão vazios (ex: `IntegracaoFintechConfigurationTest`, `IntegracaoFintechControllerTest`).
- **Hardcoded strings**: Algumas strings mágicas (ex: `"true"`, `"S"`, `"N"`) poderiam ser constantes.
- **Documentação**: Falta de comentários explicativos em classes e métodos complexos.
- **Segurança**: Credenciais em `application.yml` (mesmo que para ambiente local) deveriam ser melhor protegidas ou documentadas como exemplo.

---

## 14. Observações Relevantes

- O sistema é stateless e não mantém estado entre requisições.
- A orquestração via Apache Camel permite fácil extensão do fluxo (ex: adicionar novos processadores ou rotas).
- O uso de `CamelContextWrapper` encapsula a criação e gerenciamento do contexto Camel.
- A aplicação está preparada para deploy em Kubernetes/OpenShift, com configurações de probes (liveness/readiness) e métricas Prometheus.
- O arquivo `infra.yml` contém configurações de infraestrutura como código para diferentes ambientes (des, qa, uat, prd).
- O sistema utiliza autenticação básica para o serviço de gestão e OAuth2 para o serviço de bloqueio de conta.
- A estrutura de testes segue boas práticas com separação de testes unitários, de integração e funcionais.
- O projeto utiliza o plugin `build-helper-maven-plugin` para organizar diferentes tipos de testes em diretórios separados.