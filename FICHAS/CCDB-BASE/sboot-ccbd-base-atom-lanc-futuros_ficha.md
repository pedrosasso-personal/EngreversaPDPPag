# Ficha Técnica do Sistema

## 1. Descrição Geral
O sistema **sboot-ccbd-base-atom-lanc-futuros** é um serviço atômico REST desenvolvido em Java com Spring Boot, responsável por consultar e listar lançamentos futuros de pagamentos agendados no banco digital. O sistema integra múltiplas fontes de dados (agendamentos, boletos, débitos automáticos) e consolida informações de transações futuras para clientes do Banco Votorantim, incluindo boletos, TEF, TED, PIX e débitos automáticos.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `LancFuturoController` | Controlador REST que expõe endpoints para consulta de lançamentos futuros e totalizações |
| `LancFuturoService` | Serviço de domínio que orquestra a consulta em múltiplos repositórios e consolida resultados |
| `LancFuturoRepository` | Repositório para consulta de agendamentos na base DBCONTACORRENTE |
| `LancFuturoBoletoRepository` | Repositório para consulta de agendamentos de boletos na base DBCCBD |
| `LancFuturoDebAutoRepository` | Repositório para consulta de débitos automáticos na base CCBDDebitoAutomatico |
| `DetalheBoletoRepository` | Repositório para consulta de detalhes de boletos |
| `ValidarDadosRepository` | Repositório para validação de dados de conta corrente |
| `TotalLancamentosFuturosConverter` | Conversor de objetos de domínio para representação de resposta |
| `ParametrosConsultaValidation` | Validador de parâmetros de entrada das requisições |
| `DatabaseConfiguration` | Configuração de múltiplos datasources (Sybase, SQL Server, MySQL) |

---

## 3. Tecnologias Utilizadas
- **Java 11**
- **Spring Boot 2.1.9.RELEASE**
- **Spring Security OAuth2** (autenticação JWT)
- **JDBI 3.12.0** (acesso a banco de dados)
- **Sybase jConnect 16.3-SP03-PL07**
- **Microsoft SQL Server JDBC 7.0.0**
- **MySQL Connector 8.2.0**
- **Swagger/OpenAPI 3.0** (documentação de API)
- **Springfox 3.0.0**
- **Lombok 1.18.10**
- **HikariCP** (pool de conexões)
- **Micrometer Prometheus** (métricas)
- **Logback** (logging com formato JSON)
- **Maven 3.5.3**
- **Docker**

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/agendamento-pagamento/agendamentos-futuros/consultar` | `LancFuturoController` | Lista pagamentos futuros com filtros opcionais de data e paginação |
| GET | `/v1/agendamento-pagamento/agendamentos-futuros/total` | `LancFuturoController` | Consulta o valor total de pagamentos futuros por tipo de lançamento e período |

---

## 5. Principais Regras de Negócio
- Validação de CPF/CNPJ do cliente contra os dados da conta corrente
- Consolidação de lançamentos futuros de três fontes distintas: agendamentos gerais, boletos e débitos automáticos
- Ordenação de lançamentos por data de efetivação
- Filtragem por período de datas (dataInicio e dataFim)
- Paginação de resultados (padrão de 10 itens)
- Consulta padrão retorna lançamentos a partir da data atual
- Consulta com datas específicas retorna lançamentos no período informado
- Validação de período: data início não pode ser maior que data fim
- Enriquecimento de descrições de transações baseado em códigos de transação e sistema
- Totalização de valores por tipos de lançamento (BOLETO_CIP, TEF, TED, PIX)
- Exclusão de CPFs específicos na totalização (ex: '59588111000103', '01149953000189')
- Tratamento de débitos automáticos com mapeamento de tipos de produto (cartão, financiamento, empréstimo)

---

## 6. Relação entre Entidades

**Entidades principais:**
- `LancFuturo`: Representa um lançamento futuro com NSU, datas, valor, descrição e tipo de transação
- `TipoTransacao`: Contém código e descrição da transação
- `DetalheBoleto`: Contém nome do beneficiário final do boleto
- `ValidarDados`: Contém dados de validação da conta (banco, agência, conta, CPF/CNPJ)
- `TotalLancamentosFuturos`: Representa a totalização de valores por tipos de lançamento

**Relacionamentos:**
- `LancFuturo` possui um `TipoTransacao` (composição)
- `LancFuturo` pode referenciar um `DetalheBoleto` via `cdDetalheBoleto`
- Múltiplos `LancFuturo` são agregados de diferentes fontes (agendamentos, boletos, débitos automáticos)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| `DBCONTACORRENTE..TbAgendamentoContaCorrente` | Tabela | SELECT | Agendamentos de conta corrente gerais |
| `DBCONTACORRENTE..TbTransacao` | Tabela | SELECT | Tipos de transações |
| `DBCONTACORRENTE..TbConta` | Tabela | SELECT | Dados de contas correntes |
| `dbglobal..TbContaRelacionamento` | Tabela | SELECT | Relacionamento de contas |
| `dbglobal..TbPessoaTitularidade` | Tabela | SELECT | Titularidade de pessoas |
| `dbglobal..TbDeParaLegado` | Tabela | SELECT | Mapeamento de dados legados |
| `dbglobal..vwPessoa` | View | SELECT | Dados de pessoas (CPF/CNPJ) |
| `ccbdagendamento.TbAgendamento` | Tabela | SELECT | Agendamentos de boletos |
| `ccbdagendamento.TbPessoaAgendamento` | Tabela | SELECT | Pessoas relacionadas aos agendamentos de boletos |
| `CCBDPagamentoConta.TbDetalheBoleto` | Tabela | SELECT | Detalhes de boletos (beneficiário final) |
| `CCBDDebitoAutomatico.TbPagamentoDebitoAutomatico` | Tabela | SELECT | Pagamentos de débito automático |
| `CCBDDebitoAutomatico.TbPessoaDebitoAutomatico` | Tabela | SELECT | Pessoas relacionadas ao débito automático |
| `CCBDDebitoAutomatico.TbConvenioDebitoAutomatico` | Tabela | SELECT | Convênios de débito automático |
| `DBCONTACORRENTE..TbAgendamentoFavorecido` | Tabela | SELECT | Favorecidos dos agendamentos (usado na totalização) |

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `application.yml` | Leitura | Spring Boot | Configurações da aplicação (datasources, profiles, segurança) |
| `logback-spring.xml` | Leitura | Logback | Configuração de logs em formato JSON |
| `sboot-ccbd-base-atom-lanc-futuros.yaml` | Leitura | Swagger Codegen | Especificação OpenAPI da API |
| Arquivos SQL (*.sql) | Leitura | JDBI SqlObject | Queries SQL para consultas nos bancos de dados |

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
| **DBCONTACORRENTE (Sybase)** | Banco de Dados | Base principal de conta corrente e agendamentos |
| **DBCCBD (SQL Server)** | Banco de Dados | Base de agendamentos de boletos e detalhes de boletos |
| **CCBDDebitoAutomatico (MySQL)** | Banco de Dados | Base de débitos automáticos |
| **Serviço de Autenticação JWT** | API Externa | Validação de tokens JWT via JWK (URLs variam por ambiente: des/uat/prd) |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades entre camadas (controller, service, repository, domain)
- Uso adequado de padrões como Repository e Service
- Configuração clara de múltiplos datasources
- Uso de Lombok para reduzir boilerplate
- Documentação via Swagger/OpenAPI
- Testes unitários presentes
- Uso de enums para códigos de erro e tipos de transação
- Logging estruturado em JSON

**Pontos de Melhoria:**
- Lógica de negócio complexa no controller (deveria estar mais no service)
- Tratamento de exceções genérico em alguns pontos
- Queries SQL embutidas em arquivos separados (boa prática), mas algumas queries muito complexas e com hints específicos de banco
- Uso de strings mágicas em alguns locais (ex: códigos de status, CPFs hardcoded)
- Falta de documentação inline em métodos mais complexos
- Conversão de tipos manual em alguns pontos (Long para String)
- Código de validação poderia ser mais robusto com Bean Validation
- Algumas classes com múltiplas responsabilidades (ex: TipoTransacaoEnum com lógica de negócio)

---

## 14. Observações Relevantes

- O sistema utiliza **três datasources distintos** (Sybase, SQL Server, MySQL) para consolidar informações de diferentes sistemas legados
- A autenticação é baseada em **OAuth2 com JWT**, com validação via JWK
- O sistema possui **configurações específicas por ambiente** (local, des, uat, prd) gerenciadas via ConfigMaps e Secrets do Kubernetes
- Utiliza **JDBI** ao invés de JPA/Hibernate para acesso a dados, permitindo maior controle sobre as queries SQL
- As queries SQL utilizam **hints de otimização específicos** do Sybase (ex: `with (NOLOCK)`, `AT ISOLATION 0`)
- O sistema implementa **paginação** com tamanho padrão de 10 itens
- Há **sanitização de logs** para prevenir log injection
- O projeto segue a **arquitetura atômica** do Banco Votorantim, com estrutura modular (application e domain)
- Utiliza **Micrometer com Prometheus** para exposição de métricas em `/actuator/prometheus`
- O Dockerfile utiliza uma **imagem base customizada** do Banco Votorantim
- Configuração de **health checks** (liveness e readiness probes) para Kubernetes
- **Pool de conexões HikariCP** configurado com 10 conexões máximas e 2 mínimas por datasource