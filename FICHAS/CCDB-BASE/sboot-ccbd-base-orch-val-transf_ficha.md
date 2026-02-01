# Ficha Técnica do Sistema

---

## 1. Descrição Geral

O sistema **sboot-ccbd-base-orch-val-transf** é um microserviço orquestrador desenvolvido em Java com Spring Boot, responsável por validar transferências bancárias no contexto do Banco Digital (CCBD - Conta Corrente Banco Digital). O serviço atua como orquestrador, integrando-se com outros microserviços para validar contas correntes e informações de ITP (Instrução de Transferência de Pagamento) antes de autorizar uma transferência. Utiliza Apache Camel para roteamento de mensagens e integração entre componentes.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal que inicializa a aplicação Spring Boot com segurança OAuth2 habilitada |
| **ValidaTransferenciaController** | Controller REST que expõe o endpoint de validação de transferências |
| **ValidarTransferenciaBusiness** | Camada de negócio que orquestra as validações de conta e ITP |
| **ValTransfService** | Serviço que utiliza Apache Camel para executar as rotas de validação |
| **ValidarContaRouter** | Rota Camel para validação de contas correntes |
| **ValidarItpRouter** | Rota Camel para validação de ITP |
| **ValContaApiRepositoryImpl** | Implementação da integração com API de validação de contas |
| **ValItpApiRepositoryImpl** | Implementação da integração com API de validação de ITP |
| **ValContaMapper / ValItpMapper / ValTransfMapper** | Mapeadores entre objetos de domínio e representações de API |
| **ExceptionHandler** | Tratamento centralizado de exceções de negócio e técnicas |
| **CamelContextWrapper** | Wrapper para gerenciar o contexto do Apache Camel |

---

## 3. Tecnologias Utilizadas

- **Java 11** - Linguagem de programação
- **Spring Boot** - Framework principal para desenvolvimento de microserviços
- **Spring Security OAuth2** - Autenticação e autorização via JWT
- **Apache Camel 3.0.1** - Framework de integração e roteamento
- **Swagger/OpenAPI 2.9.2** - Documentação de APIs REST
- **Springfox** - Geração automática de documentação Swagger
- **RestTemplate** - Cliente HTTP para consumo de APIs externas
- **Lombok** - Redução de código boilerplate
- **Maven** - Gerenciamento de dependências e build
- **Spring Actuator** - Monitoramento e métricas da aplicação
- **Micrometer/Prometheus** - Métricas e observabilidade
- **Logback** - Framework de logging
- **JUnit 5** - Testes unitários
- **Rest Assured** - Testes de APIs REST
- **Pact** - Testes de contrato entre consumidor e provedor
- **Docker** - Containerização da aplicação

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/banco-digital/transferencias/validacao` | ValidaTransferenciaController | Valida uma transferência bancária verificando contas, saldo e informações de ITP |

**Parâmetros de Header:**
- `codigoBanco` (Integer) - Código do banco
- `numeroAgencia` (String) - Número da agência
- `numeroConta` (Long) - Número da conta
- `tipoConta` (Long) - Tipo da conta

**Body:** TransferenciaRequestRepresentation (valor, data, finalidade, favorecido)

**Resposta:** TransferenciaResponseRepresentation (dados completos da transferência validada incluindo remetente, favorecido, fintech e ITP)

---

## 5. Principais Regras de Negócio

1. **Validação de Data**: Não é permitido realizar transferências com data anterior à data atual
2. **Validação de Documento**: O documento (CPF/CNPJ) do remetente deve ser obtido do token JWT de autenticação
3. **Validação de Conta**: Verifica se as contas do remetente e favorecido existem e estão ativas
4. **Validação de Saldo**: Verifica se o remetente possui saldo suficiente para realizar a transferência
5. **Validação de Fintech**: Verifica se existe uma fintech associada às contas envolvidas
6. **Validação de ITP**: Valida os códigos de transação, liquidação, origem e filial no sistema ITP
7. **Código de Liquidação**: Define código de liquidação como 1 para banco identificador 161, caso contrário 31
8. **Tipo de Transação**: Diferencia operações de crédito e débito nas validações de conta
9. **Tratamento de Exceções**: Retorna códigos de erro específicos para cada tipo de falha de validação

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **TransferenciaDomain**: Entidade central que representa uma transferência
  - Contém: valor, data, finalidade, remetente (PessoaDomain), favorecido (PessoaDomain), ITP (ValItpResponseDomain), fintech (FintechDomain)

- **PessoaDomain**: Representa uma pessoa (remetente ou favorecido)
  - Contém: nome, documento, tipoTransacao, conta (ContaDomain)

- **ContaDomain**: Representa uma conta bancária
  - Contém: agencia, numero, tipo, saldo, banco (BancoDomain)

- **BancoDomain**: Representa uma instituição bancária
  - Contém: codigoBacen, codigoIspb, identificador, nome, nomeAbreviado

- **FintechDomain**: Representa uma fintech associada
  - Contém: numeroAgencia, numeroConta, numeroDocumento, razaoSocial, tipoPessoa

- **ValItpResponseDomain**: Representa a resposta da validação ITP
  - Contém: codigoFilial, codigoLiquidacao, codigoOrigem, codigoTransacao, indicadorTerceiro, tipoDocumento, tipoFinalidade, tipoLancamento

**Relacionamentos:**
- TransferenciaDomain (1) -> (1) PessoaDomain (remetente)
- TransferenciaDomain (1) -> (1) PessoaDomain (favorecido)
- TransferenciaDomain (1) -> (0..1) FintechDomain
- TransferenciaDomain (1) -> (0..1) ValItpResponseDomain
- PessoaDomain (1) -> (1) ContaDomain
- ContaDomain (1) -> (0..1) BancoDomain

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
| application.yml | leitura | Spring Boot / AppProperties | Arquivo de configuração da aplicação com URLs de serviços externos e configurações de segurança OAuth2 |
| logback-spring.xml | leitura | Logback Framework | Configuração de logs da aplicação (console, formato JSON, níveis de log) |
| sboot-ccbd-base-orch-val-transf.yaml | leitura | Swagger Codegen | Especificação OpenAPI do serviço para geração de código |
| sboot-ccbd-base-orch-consulta-cc-cliente.yaml | leitura | Swagger Codegen | Especificação OpenAPI do cliente de validação de contas |
| sboot-sitp-base-atom-valida-itp.yaml | leitura | Swagger Codegen | Especificação OpenAPI do cliente de validação ITP |

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
| **sboot-ccbd-base-orch-consulta-cc-cliente** | API REST | Serviço de validação de contas correntes. Valida existência de contas, saldo, situação e retorna informações de fintech associada |
| **sboot-sitp-base-atom-validar** | API REST | Serviço de validação ITP (Instrução de Transferência de Pagamento). Valida códigos de transação, liquidação, origem e filial |
| **OAuth2 JWT Provider** | Autenticação | Provedor de autenticação OAuth2 com JWT. URLs: api-digitaldes.bancovotorantim.com.br (des/qa), api-digitaluat.bancovotorantim.com.br (uat), api-digital.bancovotorantim.com.br (prd) |

**Detalhes das Integrações:**

1. **Validação de Conta (ValContaApiRepositoryImpl)**
   - Endpoint: `/v1/banco-digital/contas/validacao`
   - Método: POST
   - Envia: Lista de pessoas com dados de conta
   - Retorna: Informações validadas das contas e fintech associada

2. **Validação ITP (ValItpApiRepositoryImpl)**
   - Endpoint: `/v1/banco-digital/validar`
   - Método: POST
   - Envia: Códigos de filial, liquidação, origem e transação
   - Retorna: Dados validados de ITP incluindo tipos de lançamento, documento e finalidade

---

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (presentation, business, domain, infrastructure)
- Uso adequado de padrões como Repository, Mapper e Service
- Utilização de Apache Camel para orquestração, demonstrando conhecimento de frameworks de integração
- Tratamento de exceções estruturado com exceções customizadas e handler centralizado
- Uso de Lombok para reduzir boilerplate
- Configuração adequada de segurança OAuth2/JWT
- Documentação OpenAPI/Swagger bem estruturada
- Testes organizados em unit, integration e functional

**Pontos de Melhoria:**
- Alguns métodos na camada de business são extensos e poderiam ser refatorados (ex: validarConta)
- Uso de Optional poderia ser melhor explorado em alguns pontos
- Alguns mappers possuem lógica condicional que poderia ser extraída
- Falta de comentários JavaDoc em classes e métodos públicos
- Tratamento de exceções com múltiplos catch poderia ser simplificado
- Algumas classes de configuração poderiam ter validações mais robustas
- O uso de RestTemplate está deprecado em versões mais recentes do Spring (recomenda-se WebClient)

---

## 14. Observações Relevantes

1. **Arquitetura Modular**: O projeto está organizado em módulos Maven (application, domain, common), seguindo boas práticas de separação de responsabilidades

2. **Ambientes**: O sistema está preparado para múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas para cada um

3. **Containerização**: Possui Dockerfile configurado para deploy em containers Docker/Kubernetes

4. **Infraestrutura como Código**: Arquivo infra.yml define configurações de deployment, probes de saúde, volumes e variáveis de ambiente

5. **Observabilidade**: Integração com Prometheus para métricas e endpoints Actuator para monitoramento

6. **Segurança**: Implementa autenticação OAuth2 com JWT, obtendo o documento do usuário do token para validações

7. **Padrão de Nomenclatura**: Segue convenções do Banco Votorantim (prefixos ccbd, sitp, sboot)

8. **Versionamento de API**: Utiliza versionamento na URL (/v1/)

9. **Logs Estruturados**: Configuração de logs em formato JSON para facilitar análise e integração com ferramentas de observabilidade

10. **Testes de Contrato**: Utiliza Pact para testes de contrato entre consumidor e provedor, garantindo compatibilidade de APIs

11. **Arquitetura de Referência**: Segue o modelo arquitetural definido pelo Banco Votorantim para microserviços stateless

12. **Parent POM**: Herda de arqt-base-master-springboot, indicando uso de padrões corporativos estabelecidos