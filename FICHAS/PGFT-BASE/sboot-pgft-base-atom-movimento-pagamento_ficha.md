# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-pgft-base-atom-movimento-pagamento** é um serviço atômico desenvolvido em Spring Boot que tem como objetivo consultar e fornecer informações sobre movimentos de pagamento e correspondências TED (Transferência Eletrônica Disponível) do sistema PGFT (Plataforma de Gestão Financeira e Tesouraria) do Banco Votorantim. O sistema expõe APIs REST para consulta de movimentos de pagamento por data e correspondências TED, realizando leituras em banco de dados Sybase e retornando informações consolidadas sobre transações financeiras.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application.java` | Classe principal que inicializa a aplicação Spring Boot com segurança OAuth2 habilitada |
| `MovimentoPagamentoController.java` | Controlador REST que expõe endpoints para consulta de movimentos de pagamento e correspondências TED |
| `MovimentoPagamentoService.java` | Serviço de domínio responsável pela lógica de negócio de movimentos de pagamento |
| `CorrespondenciaTedService.java` | Serviço de domínio responsável pela lógica de negócio de correspondências TED, incluindo validações |
| `MovimentoPagamentoRepositoryImpl.java` | Implementação do repositório para acesso a dados de movimentos de pagamento usando JDBI |
| `CorrespondenciaTedRepositoryImpl.java` | Implementação do repositório para acesso a dados de correspondências TED usando JDBI |
| `MovimentoPagamento.java` | Entidade de domínio representando um movimento de pagamento |
| `CorrespondenciaTed.java` | Entidade de domínio representando uma correspondência TED |
| `JdbiConfiguration.java` | Configuração do JDBI para acesso ao banco de dados |
| `MovimentoPagamentoRowMapper.java` | Mapper responsável por converter ResultSet em objetos MovimentoPagamento |
| `CorrespondenciaTedRowMapper.java` | Mapper responsável por converter ResultSet em objetos CorrespondenciaTed |
| `UtilDate.java` | Classe utilitária para manipulação e formatação de datas |

## 3. Tecnologias Utilizadas

- **Framework Principal**: Spring Boot 2.x
- **Linguagem**: Java 11
- **Gerenciamento de Dependências**: Maven
- **Acesso a Dados**: JDBI 3.12.0
- **Banco de Dados**: Sybase (jConnect 16.3-SP03-PL07)
- **Segurança**: Spring Security OAuth2 com JWT
- **Documentação de API**: Swagger/OpenAPI (Springfox 3.0.0)
- **Mapeamento de Objetos**: ModelMapper 2.3.7
- **Logging**: Logback com suporte a JSON
- **Monitoramento**: Spring Boot Actuator com Prometheus
- **Auditoria**: Biblioteca customizada BV (springboot-arqt-base-trilha-auditoria-web 2.3.2)
- **Testes**: JUnit 5, Mockito, Rest Assured, Pact (4.0.3)
- **Containerização**: Docker
- **Orquestração**: OpenShift (OCP)

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/consulta-pgft-pagamento/` | MovimentoPagamentoController | Retorna informações de movimentos de pagamento por data de entrada (formato yyyyMMdd) |
| GET | `/v1/correspondencia-ted` | MovimentoPagamentoController | Retorna correspondências TED por data de movimento (formato yyyy-MM-dd) e código de lançamento |

## 5. Principais Regras de Negócio

1. **Consulta de Movimentos de Pagamento**:
   - Filtra lançamentos por data de movimento específica
   - Considera apenas lançamentos de saída (Tip_Lancamento = 'S')
   - Filtra por códigos de liquidação específicos (31, 32, 22, 21)
   - Considera apenas lançamentos com status validado (Val_Status = 1)
   - Agrupa resultados por origem, liquidação, data e documento do remetente
   - Remove zeros à esquerda do CPF/CNPJ do remetente quando aplicável

2. **Consulta de Correspondências TED**:
   - Valida obrigatoriedade e formato da data de movimento (yyyy-MM-dd)
   - Valida obrigatoriedade do código de lançamento
   - Filtra por códigos de liquidação TED (31, 32)
   - Considera apenas lançamentos de entrada (Tip_Lancamento = 'E')
   - Filtra por origens específicas (2, 41)
   - Considera apenas lançamentos com status processado (Val_Status = 2)
   - Filtra por conta favorecido específica ('10000001')
   - Retorna apenas lançamentos com código superior ao informado (paginação)

3. **Tratamento de Erros**:
   - Retorna HTTP 400 (Bad Request) para validações de entrada
   - Retorna HTTP 500 (Internal Server Error) para erros não tratados
   - Implementa tratamento específico de exceções de negócio (CorrespondenciaTedException)

## 6. Relação entre Entidades

**MovimentoPagamento**:
- Representa um movimento de pagamento consolidado
- Atributos: codigoOrigemPagamento, nomeOrigemPagamento, codLiquidacao, nomeLiquidacao, documentoRemetente, nomeRemetente, quantidade, valorTotal, dataMovimento

**CorrespondenciaTed**:
- Representa uma correspondência de TED
- Atributos: nomeFavorecido, valor, historico, nomeRemetente, numeroDocumentoRemetente, codigoLancamento

**Relacionamentos**:
- Ambas as entidades são independentes e não possuem relacionamento direto entre si
- São consultadas de forma isolada através de endpoints distintos
- Representam visões diferentes dos dados de lançamentos financeiros

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| DBPGF_TES..TBL_LANCAMENTO | Tabela | SELECT | Tabela principal de lançamentos financeiros, contendo informações de movimentos de pagamento e TEDs |
| DBITP..TBL_SIST_ORIGEM_SPB | Tabela | SELECT | Tabela de referência para descrição de origens de pagamento no Sistema de Pagamentos Brasileiro |
| DBITP..TBL_LIQUIDACAO_SPB | Tabela | SELECT | Tabela de referência para descrição de tipos de liquidação no SPB |

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot | Arquivo de configuração da aplicação com profiles (local, des, qa, uat, prd) |
| logback-spring.xml | leitura | Logback | Configuração de logs com formato JSON e console |
| getMovimentoPagamento.sql | leitura | MovimentoPagamentoRepositoryImpl | Query SQL para consulta de movimentos de pagamento |
| getTedsCorrespondencia.sql | leitura | CorrespondenciaTedRepositoryImpl | Query SQL para consulta de correspondências TED |
| sboot-pgft-base-atom-movimento-pagamento.yml | leitura | Swagger Codegen | Especificação OpenAPI para geração de interfaces |

## 10. Filas Lidas

não se aplica

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Banco de Dados Sybase (DBPGF_TES) | Database | Banco de dados principal contendo informações de lançamentos financeiros do PGFT |
| Banco de Dados Sybase (DBITP) | Database | Banco de dados contendo tabelas de referência do Sistema de Pagamentos |
| API Gateway OAuth2 | Autenticação | Serviço de autenticação e autorização via JWT (diferentes URLs por ambiente) |
| Prometheus | Monitoramento | Exportação de métricas para monitoramento |

## 13. Avaliação da Qualidade do Código

**Nota: 7,5/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões hexagonais (ports/adapters)
- Separação clara de responsabilidades em módulos (common, domain, application)
- Uso adequado de padrões de projeto (Builder, Repository, Service)
- Boa cobertura de testes unitários, integração e funcionais
- Documentação OpenAPI bem definida
- Uso de Lombok reduzindo boilerplate
- Configuração adequada de profiles para diferentes ambientes
- Implementação de auditoria e monitoramento

**Pontos de Melhoria:**
- Tratamento de exceções poderia ser mais robusto e padronizado no controller
- Alguns testes unitários estão vazios ou com implementação mínima
- Falta de validação mais rigorosa de parâmetros de entrada em alguns métodos
- Código de mapeamento SQL poderia estar em classes Java ao invés de arquivos .sql externos
- Algumas classes de teste capturam exceções genéricas sem tratamento adequado
- Falta de documentação JavaDoc em várias classes
- Uso de strings mágicas em alguns lugares (códigos de liquidação, status)
- O método `getTedsCorrespondencia` no controller tem lógica de tratamento de erro que poderia ser centralizada em um @ControllerAdvice

## 14. Observações Relevantes

1. **Segurança**: O sistema utiliza OAuth2 com JWT para autenticação, com endpoints públicos configurados apenas para documentação Swagger.

2. **Multi-ambiente**: A aplicação está preparada para execução em múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas para cada um.

3. **Banco de Dados**: Utiliza Sybase como banco de dados com charset ISO-1, com diferentes instâncias por ambiente.

4. **Containerização**: Possui Dockerfile configurado para deploy em OpenShift usando imagem AdoptOpenJDK 11 com OpenJ9.

5. **Monitoramento**: Expõe métricas via Actuator na porta 9090 e integra com Prometheus.

6. **Auditoria**: Implementa trilha de auditoria através de biblioteca customizada do Banco Votorantim.

7. **Paginação**: O endpoint de correspondências TED implementa paginação através do parâmetro `codigoLancamento`.

8. **Formatação de Dados**: O sistema trabalha com dois formatos de data diferentes: yyyyMMdd para movimentos de pagamento e yyyy-MM-dd para correspondências TED.

9. **Infraestrutura como Código**: Possui configuração completa de infraestrutura (infra.yml) com definições de configmaps, secrets, probes e volumes.

10. **Pipeline CI/CD**: Configurado para execução em Jenkins com propriedades específicas (jenkins.properties) e suporte à plataforma Google Cloud.