# Ficha Técnica do Sistema

## 1. Descrição Geral
Sistema de listagem de finalidades de transferências bancárias do SPB (Sistema de Pagamentos Brasileiro). O serviço expõe uma API REST que retorna uma lista de finalidades disponíveis para transferências do tipo TED, consultando dados do banco de dados Sybase e aplicando filtros específicos de negócio. Trata-se de um microserviço atômico desenvolvido em Spring Boot seguindo padrões arquiteturais do Banco Votorantim.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application.java` | Classe principal que inicializa a aplicação Spring Boot |
| `PurposesListController.java` | Controlador REST que expõe o endpoint de listagem de finalidades |
| `PurposesListService.java` | Camada de serviço que orquestra a lógica de negócio |
| `PurposesListRepository.java` | Interface do repositório para acesso a dados |
| `PurposesListRepositoryImpl.java` | Implementação do repositório que consulta o banco Sybase |
| `PurposesList.java` | Entidade de domínio representando uma finalidade |
| `PurposeTypeEnum.java` | Enumeração com tipos de finalidades (TED) |
| `PurposesListException.java` | Exceção customizada do domínio |
| `PurposesListConfiguration.java` | Configuração de beans do Spring |
| `OpenApiConfiguration.java` | Configuração do Swagger/OpenAPI |

## 3. Tecnologias Utilizadas
- **Framework**: Spring Boot 2.1.9.RELEASE
- **Linguagem**: Java 11
- **Servidor Web**: Undertow (embedded)
- **Banco de Dados**: Sybase ASE (driver jConnect 4 versão 7.07-ESD-5)
- **Acesso a Dados**: Spring JDBC (NamedParameterJdbcTemplate), JDBI 3.12.0
- **Documentação API**: Swagger 2.9.2 / SpringFox 2.8.0
- **Build**: Maven 3.5.3+
- **Logging**: Logback 1.2.3 com suporte JSON
- **Monitoramento**: Spring Actuator + Micrometer Prometheus
- **Utilitários**: Lombok 1.18.10, Apache Commons Lang3
- **Testes**: JUnit Jupiter 5.5.2, Mockito
- **Container**: Docker com OpenJDK 11 (OpenJ9)
- **Orquestração**: OpenShift/Kubernetes (Google Cloud Platform)

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/listar-finalidades/v1/listar-finalidades` | `PurposesListController` | Retorna lista de finalidades de transferência filtradas por tipo (TED) |

**Parâmetros**: 
- `tipoFinalidade` (query parameter): Tipo da finalidade (aceita apenas "TED")

**Respostas**:
- 200: Lista de finalidades com código e descrição
- 400: Tipo de finalidade inválido
- 500: Erro interno do servidor

## 5. Principais Regras de Negócio
1. **Filtro por Tipo de Liquidação**: Apenas finalidades com códigos de liquidação 31 e 32 (TED) são aceitas
2. **Validação de Entrada**: Somente o parâmetro "TED" é aceito como tipo de finalidade; outros valores retornam erro 400
3. **Filtro de Finalidades**: Aplica uma lista fixa de 10 finalidades permitidas (hardcoded):
   - Crédito em conta
   - Pagamento à Concessionárias de Serviço Público
   - Pagamento de impostos, tributos e taxas
   - Pagamento de fornecedores
   - Pagamento de Aluguéis e Taxas de Condomínio
   - Pagamento de Duplicatas e Títulos
   - Pagamento de mensalidade escolar
   - Depósito Judicial
   - Pensão alimentícia
   - Operação de Câmbio - Não interbancária
4. **Filtro de Status**: Apenas finalidades com status 'A' (ativo) são retornadas
5. **Ordenação**: A lista final é ordenada alfabeticamente pela descrição
6. **Remoção de Duplicatas**: Garante que não haja finalidades duplicadas na resposta

## 6. Relação entre Entidades
- **PurposesList**: Entidade principal contendo:
  - `code` (Long): Código da finalidade
  - `description` (String): Descrição da finalidade
  
- **PurposeTypeEnum**: Enumeração que mapeia tipos de finalidade para códigos de liquidação
  - TED31 → código 31, tipo "TED"

Não há relacionamentos complexos entre entidades. O modelo é simples com uma única entidade de domínio.

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TBL_FINALIDADE_SPB | Tabela | SELECT | Tabela contendo as finalidades de transferências do SPB com código, descrição, tipo de pessoa e status |

**Colunas consultadas**:
- `Cod_Finalidade`: Código da finalidade
- `Descr_Finalidade`: Descrição da finalidade
- `TpFinalidadePessoa`: Tipo de finalidade por pessoa
- `Cod_Liquidacao`: Código de liquidação (filtrado por 31 e 32)
- `Status`: Status da finalidade (filtrado por 'A')

## 8. Estruturas de Banco de Dados Atualizadas
não se aplica

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | Spring Boot | Configurações da aplicação (datasource, profiles, server) |
| application-local.yml | Leitura | Spring Boot | Configurações específicas do ambiente local |
| logback-spring.xml | Leitura | Logback | Configuração de logs em formato JSON para console |
| sboot-spbb-ispb-finalidade-transf.yaml | Leitura | Swagger Codegen | Especificação OpenAPI 2.0 para geração de código |

## 10. Filas Lidas
não se aplica

## 11. Filas Geradas
não se aplica

## 12. Integrações Externas
- **Banco de Dados Sybase**: Integração via JDBC para consulta da tabela `TBL_FINALIDADE_SPB`
  - Ambientes: DES, QA, UAT, PRD
  - Usuário: lgettcompensacao (produção) / morj2eedes (desenvolvimento)
  - Conexão: jdbc:sybase:Tds com charset iso_1

## 13. Avaliação da Qualidade do Código

**Nota:** 6/10

**Justificativa:**
- **Pontos Positivos**:
  - Boa separação de responsabilidades com módulos domain e application
  - Uso adequado de injeção de dependências
  - Documentação via Swagger
  - Uso de Lombok para reduzir boilerplate
  - Configuração adequada de profiles para diferentes ambientes
  - Logging estruturado

- **Pontos Negativos**:
  - **Lista hardcoded**: A lista de finalidades permitidas está hardcoded no repositório (`finalList`), deveria estar em configuração ou banco de dados
  - **Lógica de negócio no repositório**: O método `filterList()` contém regra de negócio e deveria estar na camada de serviço
  - **Tratamento de exceções genérico**: Captura `Exception` genérica em vez de exceções específicas
  - **Falta de validações**: Não valida se a lista retornada do banco está vazia antes de processar
  - **Código comentado**: Várias dependências e configurações comentadas no pom.xml
  - **Nomenclatura inconsistente**: Mistura de português e inglês nos nomes
  - **SQL inline**: Query SQL construída manualmente via StringBuilder, poderia usar anotações ou arquivos externos
  - **Enum subutilizado**: O `PurposeTypeEnum` tem apenas um valor e não é efetivamente usado
  - **Falta de testes**: Arquivos de teste marcados como NAO_ENVIAR

## 14. Observações Relevantes
1. **Arquitetura Atômica**: Segue o padrão de microserviços atômicos do Banco Votorantim
2. **Multi-módulo**: Projeto Maven dividido em módulos `domain` e `application`
3. **Contract-First**: Utiliza Swagger Codegen para gerar interfaces a partir do contrato OpenAPI
4. **Ambientes**: Suporta 4 ambientes (DES, QA, UAT, PRD) com configurações específicas
5. **Infraestrutura**: Deploy em OpenShift/Kubernetes na Google Cloud Platform
6. **Segurança**: Configurações de segurança JWT e LDAP estão comentadas/desabilitadas
7. **Monitoramento**: Expõe métricas Prometheus via `/actuator/prometheus`
8. **Health Check**: Endpoints de liveness e readiness configurados para Kubernetes
9. **Encoding**: Utiliza charset ISO-8859-1 para conexão com Sybase
10. **Limitação funcional**: Atualmente só suporta tipo "TED", apesar da estrutura permitir expansão
11. **Versão**: Projeto na versão 0.11.0 (ainda em desenvolvimento/evolução)