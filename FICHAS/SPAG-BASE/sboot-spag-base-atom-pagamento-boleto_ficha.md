# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-spag-base-atom-pagamento-boleto** é um serviço atômico desenvolvido em Spring Boot que permite a convivência entre os sistemas SPAG e SITP para registro de pagamentos de boleto. O sistema oferece funcionalidades para registrar pagamentos de boleto com dois tipos de liquidação (NORMAL e STR_26) e consultar informações sobre sistemas de origem. Trata-se de uma API REST que integra com o banco de dados Sybase (DBITP) para persistência e consulta de dados relacionados a pagamentos de boleto.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal que inicializa a aplicação Spring Boot |
| `PagamentoBoletoController` | Controlador REST responsável por expor endpoints para registro de pagamento de boleto |
| `SistemaOrigemController` | Controlador REST para consulta de informações de sistema de origem |
| `PagamentoBoletoService` | Serviço de domínio contendo regras de negócio para pagamento de boleto |
| `PagamentoBoletoRepositoryImpl` | Implementação do repositório usando JDBI para acesso ao banco de dados |
| `RegistroPagamentoBoleto` | Entidade de domínio representando um registro de pagamento de boleto |
| `RegistroPagamentoBoletoSTR26` | Entidade específica para pagamentos do tipo STR26 |
| `SistemaOrigem` | Entidade representando informações de sistema de origem |
| `PagamentoBoletoConfiguration` | Classe de configuração do Spring para beans do sistema |
| `OpenApiConfiguration` | Configuração do Swagger/OpenAPI |
| `PagamentoBoletoExceptionHandler` | Tratador global de exceções |
| `RegistroPagamentoBoletoMapper` | Mapper MapStruct para conversão entre representações e domínio |
| `RegistroPagamentoBoletoSTR26Mapper` | Mapper para transformação de pagamento normal em STR26 |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.x** (framework principal)
- **Java 11** (linguagem de programação)
- **JDBI 3.9.1** (biblioteca de acesso a banco de dados)
- **Sybase jConnect 16.3** (driver JDBC para Sybase)
- **MapStruct 1.3.1** (mapeamento de objetos)
- **Swagger/Springfox 2.9.2** (documentação de API)
- **Lombok** (redução de boilerplate)
- **Micrometer/Prometheus** (métricas e monitoramento)
- **Logback** (logging)
- **JUnit 5** (testes unitários)
- **Mockito** (mocks para testes)
- **REST Assured** (testes funcionais)
- **Pact** (testes de contrato)
- **Maven** (gerenciamento de dependências e build)
- **Docker** (containerização)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/registra-pagamento-boleto` | `PagamentoBoletoController` | Registra um pagamento de boleto do tipo NORMAL ou STR26 no sistema SITP |
| GET | `/v1/sistema-origem` | `SistemaOrigemController` | Busca informações sobre sistema de origem pelo número da origem da operação |

---

## 5. Principais Regras de Negócio

1. **Validação de Tipo de Liquidação**: O sistema valida se o tipo de liquidação informado é NORMAL ou STR_26, caso contrário lança exceção de negócio.

2. **Verificação de Duplicidade**: Antes de registrar um pagamento, o sistema verifica se já existe um registro com o mesmo código de lançamento. Se existir, retorna o protocolo existente ao invés de criar um novo.

3. **Transformação STR26**: Para pagamentos do tipo STR_26, o sistema aplica transformações específicas preenchendo campos padrão (código de filial = 1, origem = 10, transação = 8374, etc.) e chama uma stored procedure antes de registrar na tabela principal.

4. **Identificação de Lançamento Fintech**: O sistema identifica se um lançamento é do tipo Fintech baseado em critérios específicos (banco remetente cliente fintech não nulo, CPF/CNPJ com mais de 11 caracteres, tipo de conta informado).

5. **Histórico Automático**: Para pagamentos STR26, o sistema gera automaticamente o histórico no formato "Protocolo Comp - {codigoLancamento}".

6. **Validação de Código de Lançamento Obrigatório**: O código de lançamento é obrigatório para qualquer operação de registro.

---

## 6. Relação entre Entidades

**Entidades principais:**

- **RegistroPagamentoBoleto**: Entidade principal contendo todos os dados de um pagamento de boleto (remetente, favorecido, valores, datas, códigos diversos, informações de fintech, etc.)

- **RegistroPagamentoBoletoSTR26**: Entidade específica para pagamentos STR26, com campos pré-definidos e valores padrão do Banco Votorantim como remetente.

- **Protocolo**: Entidade simples contendo apenas o número do protocolo gerado após registro bem-sucedido.

- **SistemaOrigem**: Entidade representando o código da entidade associada a um sistema de origem.

**Relacionamentos:**
- RegistroPagamentoBoleto pode ser transformado em RegistroPagamentoBoletoSTR26 através do mapper quando o tipo de liquidação é STR_26.
- Após registro bem-sucedido, tanto NORMAL quanto STR26 retornam um Protocolo.

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBITP.dbo.TBL_CAIXA_ENTRADA_SPB | tabela | SELECT | Consulta protocolo existente por código de lançamento |
| DBITP.dbo.TBL_SIST_ORIGEM_SPB | tabela | SELECT | Consulta informações de sistema de origem |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBITP.dbo.TBL_CAIXA_ENTRADA_SPB | tabela | INSERT | Insere novo registro de pagamento de boleto (tipo NORMAL e STR26) |
| DBITP.dbo.prIncluirLancamento | stored procedure | CALL | Procedure chamada para registrar pagamento STR26 antes do insert na tabela principal |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot | Arquivo de configuração da aplicação com profiles (local, des, qa, uat, prd) |
| logback-spring.xml | leitura | Logback | Configuração de logs da aplicação |
| buscarPagamentoBoleto.sql | leitura | PagamentoBoletoRepositoryImpl | Query SQL para buscar protocolo por código de lançamento |
| buscarSistemaOrigem.sql | leitura | PagamentoBoletoRepositoryImpl | Query SQL para buscar sistema de origem |
| registrarPagamentoBoleto.sql | leitura | PagamentoBoletoRepositoryImpl | Query SQL para inserir pagamento de boleto |
| registrarPagamentoBoletoSTR26.sql | leitura | PagamentoBoletoRepositoryImpl | Query SQL para chamar stored procedure STR26 |
| sboot-spag-base-atom-pagamento-boleto.yaml | leitura | Swagger Codegen | Especificação OpenAPI para geração de interfaces |

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
| Banco de Dados Sybase (DBITP) | Database | Integração com banco de dados Sybase para persistência e consulta de dados de pagamento de boleto |
| API Gateway OAuth2 | Autenticação | Integração com API Gateway para validação de tokens JWT OAuth2 (diferentes URLs por ambiente) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7,5/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (application, domain, common)
- Uso adequado de padrões como Repository, Service, Mapper
- Implementação de testes unitários, integração e funcionais
- Uso de MapStruct para mapeamento de objetos
- Configuração adequada de profiles para diferentes ambientes
- Documentação via Swagger/OpenAPI
- Tratamento centralizado de exceções
- Uso de Lombok para reduzir boilerplate

**Pontos de Melhoria:**
- Alguns métodos com lógica complexa poderiam ser refatorados (ex: `registrarPagamentoBoletoSTR26`)
- Strings hardcoded em alguns lugares (ex: mensagens de erro, valores padrão)
- Falta de validações mais robustas em alguns campos de entrada
- Alguns comentários em código desatualizados ou genéricos
- Testes de integração comentados (PactTest)
- Uso de SQL em arquivos separados é bom, mas alguns SQLs muito extensos poderiam ser simplificados
- Falta de documentação JavaDoc em algumas classes importantes

---

## 14. Observações Relevantes

1. **Ambientes Múltiplos**: O sistema está preparado para rodar em múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas para cada um.

2. **Monitoramento**: Possui integração completa com Prometheus/Grafana para monitoramento de métricas (CPU, memória, threads, GC, HTTP requests, etc.).

3. **Auditoria**: Utiliza biblioteca de auditoria do Banco Votorantim (`springboot-arqt-base-trilha-auditoria-web`).

4. **Segurança**: Implementa autenticação OAuth2 via API Gateway com validação de tokens JWT.

5. **Containerização**: Possui Dockerfile para containerização da aplicação usando OpenJDK 11 com OpenJ9.

6. **CI/CD**: Configurado para pipeline Jenkins com propriedades específicas (jenkins.properties).

7. **Arquitetura Hexagonal**: Segue princípios de arquitetura hexagonal com separação clara entre domínio, portas e adaptadores.

8. **Testes de Arquitetura**: Possui profile Maven para validação de regras arquiteturais usando ArchUnit.

9. **Conexão com Sybase**: Utiliza driver jConnect da Sybase com charset ISO-1 para compatibilidade.

10. **Geração de Código**: Utiliza Swagger Codegen Maven Plugin para gerar automaticamente interfaces de API a partir da especificação OpenAPI.