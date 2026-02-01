---
## Ficha Técnica do Sistema


### 1. Descrição Geral
O sistema **sboot-ccbd-base-orch-vitrine-seguros** é um serviço de orquestração desenvolvido em Spring Boot que expõe APIs REST para consulta e exibição de seguros no aplicativo de Banco Digital do Banco Votorantim. O sistema integra-se com múltiplos serviços externos para consolidar informações sobre seguros contratados (especialmente seguros auto vinculados a financiamentos de veículos) e seguros disponíveis para contratação via cartão de crédito, apresentando essas informações de forma organizada em uma "vitrine" para o cliente final.


### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **VitrineSegurosController** | Controlador REST que expõe os endpoints `/v1/banco-digital/vitrine-seguros` e `/v1/banco-digital/vitrine-seguros/contratados` |
| **SegurosServiceImpl** | Implementação do serviço de negócio que orquestra as chamadas via Apache Camel |
| **SegurosRouter** | Rota Camel que orquestra a consulta de veículos financiados e seguros contratados |
| **VitrineRouter** | Rota Camel que orquestra a consulta de seguros disponíveis para o cartão |
| **SegurosRepositoryImpl** | Implementação do repositório que consulta seguros contratados via API externa |
| **VeiculosRepositoryImpl** | Implementação do repositório que consulta contratos de financiamento de veículos |
| **SegurosDisponiveisRepositoryImpl** | Implementação do repositório que consulta seguros disponíveis para cartão |
| **SeguroContratadoMapper** | Mapeador de dados de seguros contratados |
| **SeguroDisponivelMapper** | Mapeador de dados de seguros disponíveis |
| **VeiculoMapper** | Mapeador de dados de veículos financiados |
| **VitrineMapper** | Mapeador de dados da vitrine completa |
| **ResourceHandler** | Tratador global de exceções |


### 3. Tecnologias Utilizadas
- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Apache Camel 3.0.1** (orquestração de fluxos)
- **Spring Security OAuth2** (autenticação JWT)
- **Swagger/OpenAPI 3.0** (documentação de APIs)
- **Micrometer + Prometheus** (métricas)
- **Grafana** (visualização de métricas)
- **Logback** (logging)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Lombok** (redução de boilerplate)
- **JUnit 5 + Mockito** (testes unitários)
- **Pact** (testes de contrato)
- **HikariCP** (pool de conexões - configurado mas não evidenciado uso direto)


### 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/banco-digital/vitrine-seguros` | VitrineSegurosController | Retorna a vitrine de seguros disponíveis com base nos últimos 4 dígitos do cartão |
| GET | `/v1/banco-digital/vitrine-seguros/contratados` | VitrineSegurosController | Retorna os seguros auto contratados vinculados aos financiamentos de veículos do cliente |


### 5. Principais Regras de Negócio
- Consulta de seguros contratados é filtrada apenas para seguros do tipo AUTO (código 1)
- Seguros disponíveis são filtrados por elegibilidade (situação = 6 - ELEGIVEL)
- Cálculo de vigência de seguros: identifica se o seguro está vencido, vence amanhã ou está próximo de vencer (até 35 dias)
- Agrupamento de seguros contratados por produto (código e nome)
- Vinculação de seguros contratados aos veículos financiados através do número do contrato
- Enriquecimento da vitrine com informações de contato (telefones, email, chat)
- Ordenação de seguros disponíveis por ordem de prioridade definida em enum (CarouselEnum)
- Inclusão automática do seguro AUTO na vitrine mesmo sem elegibilidade via cartão
- Extração do CPF/CNPJ do cliente a partir do token JWT de autenticação


### 6. Relação entre Entidades

**Entidades de Domínio:**
- **Vitrine**: contém lista de SeguroDisponivel (carousel) e Contato
- **SeguroDisponivel**: representa um seguro disponível para contratação (ordem, ícone, nome, descrição, etc)
- **SeguroAuto**: especialização de SeguroDisponivel
- **Contato**: informações de contato (email, telefones, chat)
- **Telefone**: números de telefone (capital, demais regiões, auto)
- **Auto**: representa um produto de seguro auto com lista de BemSegurado
- **BemSegurado**: representa um bem segurado (veículo) com vigência e flags de vencimento
- **SeguroContratado**: dados de um seguro contratado (produto, vigência, contrato)
- **ContratoFinanciamentoVeiculo**: dados de um contrato de financiamento (número, nome do veículo)
- **Vigencia**: período de vigência do seguro (data inicial e final)
- **Produto**: dados básicos de um produto de seguro (código e nome)

**Relacionamentos:**
- Vitrine 1 ---> N SeguroDisponivel
- Vitrine 1 ---> 1 Contato
- Contato 1 ---> 1 Telefone
- Auto 1 ---> N BemSegurado
- BemSegurado 1 ---> 1 Vigencia
- SeguroContratado 1 ---> 1 Vigencia


### 7. Estruturas de Banco de Dados Lidas

não se aplica

(O sistema não acessa diretamente banco de dados, apenas consome APIs REST de outros serviços)


### 8. Estruturas de Banco de Dados Atualizadas

não se aplica

(O sistema não realiza operações de escrita em banco de dados)


### 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot (startup) | Arquivo de configuração da aplicação |
| logback-spring.xml | leitura | Logback (startup) | Configuração de logs |
| sboot-ccbd-base-orch-vitrine-seguros.yaml | leitura | Swagger Codegen (build) | Especificação OpenAPI do serviço provedor |
| sboot-bvmc-base-orch-finan-veic-extrato.yaml | leitura | Swagger Codegen (build) | Especificação OpenAPI do cliente de veículos |
| sboot-pseg-base-orch-cotacao-contrato.yaml | leitura | Swagger Codegen (build) | Especificação OpenAPI do cliente de seguros contratados |
| springboot-pseg-base-venda-digital.yaml | leitura | Swagger Codegen (build) | Especificação OpenAPI do cliente de seguros disponíveis |


### 10. Filas Lidas

não se aplica

(O sistema não consome mensagens de filas)


### 11. Filas Geradas

não se aplica

(O sistema não publica mensagens em filas)


### 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| **sboot-bvmc-base-orch-finan-veic-extrato** | API REST | Consulta contratos de financiamento de veículos por CPF/CNPJ |
| **sboot-pseg-base-orch-cotacao-contrato** | API REST | Consulta seguros contratados por número de contrato |
| **springboot-pseg-base-venda-digital** | API REST | Consulta seguros disponíveis por últimos 4 dígitos do cartão |
| **OAuth2 JWT Provider** | Autenticação | Validação de tokens JWT para autenticação e autorização |


### 13. Avaliação da Qualidade do Código

**Nota:** 7,5/10

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões de Clean Architecture (separação em camadas: application, domain, common)
- Uso adequado de padrões de projeto (Repository, Mapper, Builder)
- Boa cobertura de testes unitários
- Uso de Apache Camel para orquestração de fluxos complexos
- Configuração adequada de segurança com JWT
- Documentação OpenAPI bem estruturada
- Uso de Lombok para redução de boilerplate
- Configuração de métricas e observabilidade (Prometheus/Grafana)

**Pontos de Melhoria:**
- Uso de Singleton para armazenar estado (SeguroContratadoSingleton) é um antipadrão que pode causar problemas em ambientes concorrentes
- Falta de tratamento de exceções mais granular em alguns pontos
- Alguns métodos poderiam ser quebrados em métodos menores para melhor legibilidade
- Falta de validação de entrada em alguns endpoints
- Comentários de código praticamente inexistentes
- Alguns nomes de variáveis poderiam ser mais descritivos (ex: "c", "s", "d")
- Lógica de negócio misturada com lógica de processamento Camel em alguns pontos


### 14. Observações Relevantes

- O sistema utiliza Apache Camel para orquestração, o que adiciona complexidade mas permite maior flexibilidade na composição de fluxos
- A autenticação é baseada em JWT OAuth2, extraindo o CPF/CNPJ do usuário do token
- O sistema é stateless, mas utiliza um Singleton para compartilhar dados entre rotas Camel, o que pode ser problemático
- Há configuração para múltiplos ambientes (local, des, qa, uat, prd)
- O projeto segue padrões do Banco Votorantim (arquitetura ARQT)
- Há testes de contrato com Pact configurados
- O sistema está preparado para deploy em OpenShift/Kubernetes
- Métricas são expostas via Actuator no formato Prometheus
- Logs estruturados em JSON para facilitar análise

---