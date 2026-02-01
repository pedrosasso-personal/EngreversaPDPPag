# Ficha Técnica do Sistema

## 1. Descrição Geral
Sistema de consulta de transações conciliadas de cartão de débito do Banco Votorantim (CCBD). O serviço atômico expõe APIs REST para consultar transações processadas a partir de três tipos de arquivos: **T464** (transações Mastercard), **FormC** (transações de conciliação) e **TIF** (Transaction Interchange File). O sistema realiza leitura de dados de transações armazenadas em banco SQL Server, processa informações complementares em formato JSON e retorna dados consolidados sobre transações conciliadas, duplicadas e com erro.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot que inicializa a aplicação |
| `ConsultaConciliacaoController` | Controller REST que expõe os endpoints de consulta |
| `FormcServiceImpl` | Implementa lógica de negócio para consultas de transações FormC |
| `T464ServiceImpl` | Implementa lógica de negócio para consultas de transações T464, incluindo processamento de JSON complementar |
| `TifRegistroServiceImpl` | Implementa lógica de negócio para consultas de transações TIF (processadas, duplicadas e com erro) |
| `FormcRepositoryImpl` | Interface JDBI para acesso aos dados de transações FormC |
| `T464RepositoryImpl` | Interface JDBI para acesso aos dados de transações T464 |
| `TifRegistroRepositoryImpl` | Interface JDBI para acesso aos dados de transações TIF |
| `ConvertListaTransacoes` | Classe utilitária para conversão de objetos de domínio para representações REST |
| `ConvertTifRegistro` | Classe utilitária para conversão de objetos TIF para representações REST |
| `ConsultaConciliacaoConfiguration` | Configuração de beans e injeção de dependências |
| `DataSourceConfiguration` | Configuração do datasource e JDBI |
| `OpenApiConfiguration` | Configuração do Swagger/OpenAPI |
| `AppProperties` | Propriedades de configuração da aplicação (IDs de status TIF) |

---

## 3. Tecnologias Utilizadas

- **Java 11** (OpenJDK)
- **Spring Boot** (framework principal)
- **Spring Security OAuth2** (autenticação JWT)
- **JDBI 3.9.1** (acesso a banco de dados)
- **Microsoft SQL Server** (banco de dados)
- **Swagger/Springfox 2.9.2** (documentação de API)
- **Lombok** (redução de boilerplate)
- **Jackson** (processamento JSON)
- **Logback** (logging)
- **Micrometer/Prometheus** (métricas)
- **Spring Actuator** (health checks)
- **Maven** (build)
- **Docker** (containerização)
- **JUnit 5** (testes unitários)
- **Mockito** (mocks em testes)
- **REST Assured** (testes funcionais)
- **Pact** (testes de contrato)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/consulta-conciliacao/arquivo/formc` | `ConsultaConciliacaoController` | Consulta transações conciliadas do arquivo FormC por período |
| GET | `/v1/consulta-conciliacao/arquivo/t464` | `ConsultaConciliacaoController` | Consulta transações conciliadas do arquivo T464 por período |
| GET | `/v1/registro/tif` | `ConsultaConciliacaoController` | Consulta dashboard de transações TIF (processadas, duplicadas, erro) por data |
| GET | `/v1/registro/tif-analitico` | `ConsultaConciliacaoController` | Consulta analítica detalhada de transações TIF com erro |

**Observação:** Todos os endpoints requerem autenticação OAuth2 JWT.

---

## 5. Principais Regras de Negócio

1. **Ajuste de datas**: As datas de início recebem sufixo " 00:00:00" e datas fim recebem " 23:59:59" para consultas de período completo
2. **Processamento de complemento T464**: Transações T464 possuem campo JSON (`TeComplementoConciliacaoTrnso`) que é deserializado para extrair informações adicionais como estabelecimento, taxa de intercâmbio (fee) e indicadores
3. **Cálculo de valor líquido T464**: O valor líquido da transação é calculado somando ou subtraindo a taxa de intercâmbio conforme o indicador (`interchangeFeeIndicator`): se "C" (crédito) soma, caso contrário subtrai
4. **Totalização T464**: Apenas transações com status "REGISTRO_PROCESSADO" são consideradas nos totais de fee e valor líquido
5. **Agrupamento TIF**: Transações TIF são agrupadas por arquivo e classificadas em três categorias: processadas (ID 15), duplicadas (ID 16) e com erro (ID 17) - valores configuráveis por ambiente
6. **Consulta analítica TIF**: Retorna apenas transações com status de erro para análise detalhada
7. **Mascaramento de cartão**: Números de cartão são armazenados e retornados mascarados (formato: 554624******0887)

---

## 6. Relação entre Entidades

**Entidades principais:**

- **TransacoesConciliadasFormc**: Representa transação conciliada do arquivo FormC
- **TransacoesConciliadasT464**: Representa transação conciliada do arquivo T464 (com campos adicionais de fee e estabelecimento)
- **ResponseTifArquivo**: Representa arquivo TIF processado
- **ResponseTifRegistroPorTipo**: Representa agrupamento de registros TIF por tipo (processado/duplicado/erro)
- **ResponseTifRegistroAnalitico**: Representa registro TIF detalhado para análise

**Relacionamentos:**
- Um arquivo TIF (`ResponseTifArquivo`) pode ter múltiplos registros de cada tipo (processado, duplicado, erro)
- Cada `ResponseTifRegistroDash` agrega um arquivo TIF com seus respectivos registros por tipo
- Transações FormC e T464 são independentes, relacionadas apenas por período de consulta

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| `CCBDTransacaoCartaoDebito.TbConciliacaoTransacao` | Tabela | SELECT | Tabela principal de transações conciliadas |
| `CCBDTransacaoCartaoDebito.TbArquivoOrigem` | Tabela | SELECT | Tabela de origem dos arquivos (FormC, T464) |
| `CCBDTransacaoCartaoDebito.TbStatusProcessamento` | Tabela | SELECT | Tabela de status de processamento das transações |
| `CCBDTransacaoCartaoDebito.TbTipoTransacao` | Tabela | SELECT | Tabela de tipos de transação |
| `CCBDTransacaoCartaoDebito.TbComplementoConciliacaoTrnso` | Tabela | SELECT | Tabela com dados complementares em JSON (T464) |
| `CCBDTransacaoCartaoDebito.TbControleArquivo` | Tabela | SELECT | Tabela de controle de arquivos TIF |
| `CCBDTransacaoCartaoDebito.TbControleRegistroArquivo` | Tabela | SELECT | Tabela de controle de registros dos arquivos TIF |
| `CCBDTransacaoCartaoDebito.TbAutorizacaoArquivoDetalhe` | Tabela | SELECT | Tabela com detalhes de autorização das transações TIF |
| `CCBDTransacaoCartaoDebito.TbPortadorArquivoDetalhe` | Tabela | SELECT | Tabela com detalhes do portador do cartão |

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `logback-spring.xml` | Leitura | `/usr/etc/log` (runtime) | Arquivo de configuração de logs |
| `application.yml` | Leitura | `application/src/main/resources` | Arquivo de configuração da aplicação |
| `sboot-ccbd-base-atom-consulta-conciliacao.yaml` | Leitura | `application/src/main/resources/swagger` | Especificação OpenAPI/Swagger |
| `*.sql` | Leitura | `application/src/main/resources/.../database` | Arquivos SQL para queries JDBI |

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
| **SQL Server** | Banco de dados | Banco de dados principal onde estão armazenadas as transações conciliadas (DBCCBD) |
| **OAuth2 JWT Provider** | Autenticação | Serviço de autenticação OAuth2 com JWT (URLs variam por ambiente: apigatewaydes.bvnet.bv, apigateway.bvnet.bv, apigatewayuat.bvnet.bv) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (controller, service, repository, domain)
- Uso adequado de padrões Spring Boot e injeção de dependências
- Cobertura de testes unitários presente
- Uso de Lombok reduz boilerplate
- Configuração externalizada em arquivos YAML
- Documentação OpenAPI/Swagger bem estruturada
- Uso de JDBI com SQL externalizado facilita manutenção

**Pontos de Melhoria:**
- Tratamento de exceções genérico (catch Exception) em vários pontos, retornando sempre HTTP 500
- Lógica de negócio complexa (processamento JSON, cálculos) dentro de services poderia ser melhor modularizada
- Falta de validação de entrada nos controllers (datas, parâmetros)
- Código com alguns comentários em português misturados com código em inglês
- Classe `TifRegistroServiceImpl` com lógica complexa de agrupamento que poderia ser refatorada
- Falta de logs estruturados em alguns pontos críticos
- Conversores (`ConvertListaTransacoes`, `ConvertTifRegistro`) com métodos estáticos e lógica repetitiva
- Ausência de DTOs específicos para requests (usa apenas headers)

---

## 14. Observações Relevantes

1. **Ambientes**: O sistema está configurado para rodar em múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas por ambiente
2. **Segurança**: Todos os endpoints são protegidos por OAuth2 JWT via `@EnableResourceServer`
3. **Monitoramento**: Exposição de métricas Prometheus e health checks via Actuator na porta 9090
4. **Containerização**: Aplicação preparada para execução em container Docker com imagem OpenJ9
5. **IDs de Status TIF**: Os IDs de status TIF (processado, duplicado, erro) são configuráveis por ambiente via variáveis de ambiente
6. **Formato de Datas**: Sistema trabalha com datas em formato String "yyyy-MM-dd HH:mm:ss"
7. **JSON Complementar**: Transações T464 possuem campo JSON complexo com informações adicionais da Mastercard que é processado dinamicamente
8. **Auditoria**: Sistema integrado com biblioteca de trilha de auditoria do Banco Votorantim
9. **Pipeline CI/CD**: Configurado para deploy em plataforma Google Cloud (OpenShift) via Jenkins
10. **Banco de Dados**: Conexão com SQL Server usando driver JDBC Microsoft com configuração específica de encoding