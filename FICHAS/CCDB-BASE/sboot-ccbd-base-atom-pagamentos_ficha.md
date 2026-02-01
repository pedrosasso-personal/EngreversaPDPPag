# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-ccbd-base-atom-pagamentos** é um serviço atômico REST desenvolvido em Spring Boot para gerenciar e consultar pagamentos realizados no banco digital. O sistema permite listar pagamentos, obter resumos, calcular totais de pagamentos (excluindo boletos BV e BVF), e filtrar por diferentes tipos de transação (boletos CIP, consumo, tributos) e formas de pagamento (conta corrente e cartão de crédito). Suporta consultas diurnas e noturnas, além de fornecer totais segmentados por saldo em conta e cartão de crédito.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application.java` | Classe principal que inicializa a aplicação Spring Boot |
| `PagamentosController.java` | Controlador REST que expõe os endpoints de consulta de pagamentos |
| `PagamentosService.java` | Camada de serviço contendo a lógica de negócio para processamento de pagamentos |
| `PagamentosRepositoryImpl.java` | Interface de repositório que define operações de acesso a dados usando JDBI |
| `DatabaseConfiguration.java` | Configuração do JDBI para acesso ao banco de dados SQL Server |
| `OpenApiConfiguration.java` | Configuração do Swagger/OpenAPI para documentação da API |
| `PagamentosConfiguration.java` | Configuração de beans do Spring para injeção de dependências |
| `ListarPagamentosConversor.java` | Conversor entre objetos de domínio e representações REST |
| `Validacoes.java` | Classe utilitária para validações de regras de negócio (datas) |
| `FormataDatas.java` | Utilitário para conversão e formatação de datas |
| `Pagamentos.java` | Entidade de domínio representando um pagamento |
| `TotalPagamentos.java` | Entidade de domínio para totalizações de pagamentos |
| `FormaPagamentoEnum.java` | Enumeração de formas de pagamento (Conta Corrente, Cartão de Crédito) |
| `TipoContabilTransacaoEnum.java` | Enumeração de tipos de transações contábeis |
| `TipoTransacaoEnum.java` | Enumeração de tipos de transações de negócio |

---

## 3. Tecnologias Utilizadas

- **Spring Boot** (framework principal)
- **Spring Web** (REST APIs)
- **Spring Security** (OAuth2 JWT)
- **JDBI 3.9.1** (acesso a dados)
- **SQL Server** (banco de dados)
- **Swagger/Springfox 3.0.0** (documentação de API)
- **Lombok** (redução de boilerplate)
- **Logback** (logging com formato JSON)
- **Spring Actuator** (health checks e métricas)
- **Micrometer Prometheus** (métricas)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Java 11**

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/pagamentos/consultar` | `PagamentosController` | Lista pagamentos por conta e período |
| GET | `/v1/pagamentos/listar-fechados` | `PagamentosController` | Lista pagamentos fechados |
| GET | `/v1/pagamentos/resumir-fechados` | `PagamentosController` | Retorna resumo de pagamentos fechados |
| GET | `/v1/pagamentos/total-sem-bv` | `PagamentosController` | Total de pagamentos excluindo boletos BV/BVF |
| GET | `/v1/pagamentos/total-sem-bv/noturno` | `PagamentosController` | Total de pagamentos noturnos excluindo boletos BV/BVF |
| GET | `/v1/pagamentos/total-sem-bv-saldo-cartao` | `PagamentosController` | Total segmentado por saldo e cartão |
| GET | `/v1/pagamentos/total-sem-bv-saldo-cartao/noturno` | `PagamentosController` | Total noturno segmentado por saldo e cartão |
| GET | `/v1/pagamentos-cartao-credito/total-sem-bv` | `PagamentosController` | Total de pagamentos com cartão de crédito excluindo boletos BV/BVF |

---

## 5. Principais Regras de Negócio

- **Validação de datas**: Data inicial não pode ser posterior à data final
- **Exclusão de boletos BV**: Pagamentos com beneficiários BV (CNPJs específicos) são excluídos dos totais
- **Filtragem por status**: Apenas pagamentos com status diferente de 5 e 6 são considerados
- **Filtragem por sistema**: Apenas pagamentos do sistema 91 são processados
- **Segmentação por horário**: Pagamentos diurnos (00:00-19:59) e noturnos (20:00-23:59) são calculados separadamente
- **Tipos de transação**: Suporte a diferentes tipos (BOLCIPCONTRICART, BOLCIPCONTRICC) com códigos contábeis específicos
- **Formas de pagamento**: Diferenciação entre pagamentos via conta corrente (código 1) e cartão de crédito (código 2)
- **Mascaramento de dados sensíveis**: CPF/CNPJ são parcialmente mascarados nos logs

---

## 6. Relação entre Entidades

**Principais entidades e relacionamentos:**

- **Pagamentos**: Entidade principal contendo NSU, datas, valores, descrição, tipo de pagamento, dados do beneficiário
- **TipoPagamento**: Relacionamento com código e descrição da forma de pagamento
- **PagamentosResumido**: Agregação de valor total e quantidade de pagamentos
- **TotalPagamentos**: Totalização com número da conta, valor total e quantidade
- **TotalPagamentosSaldoCartao**: Totalização por forma de pagamento (ID e valor)

**Enumerações de apoio:**
- FormaPagamentoEnum (1=Conta Corrente, 2=Cartão Crédito)
- TipoContabilTransacaoEnum (7100=Boleto CIP, 8679=Tributo, 8677=Consumo)
- TipoTransacaoEnum (combinações de tipos contábeis e formas de pagamento)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| CCBDPagamentoConta.TbLancamentoBoleto | tabela | SELECT | Tabela principal de lançamentos de boletos/pagamentos |
| CCBDPagamentoConta.TbDetalheBoleto | tabela | SELECT | Detalhes dos boletos incluindo dados do beneficiário |
| CCBDPagamentoConta.TbTransacaoBoleto | tabela | SELECT | Informações de transação (vencimento, valor do documento) |

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot | Configurações da aplicação (datasource, profiles, security) |
| logback-spring.xml | leitura | Logback | Configuração de logs em formato JSON |
| *.sql (11 arquivos) | leitura | PagamentosRepositoryImpl | Queries SQL para consultas de pagamentos |
| sboot-ccbd-base-atom-pagamentos.yaml | leitura | Swagger Codegen | Especificação OpenAPI para geração de interfaces |

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
| SQL Server (DBCCBD) | Banco de Dados | Banco de dados principal contendo tabelas de pagamentos |
| OAuth2 JWT Provider | Autenticação | Serviço de autenticação via JWT (URLs variam por ambiente: des/uat/prd) |
| Prometheus | Métricas | Exportação de métricas da aplicação |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades em camadas (controller, service, repository, domain)
- Uso adequado de padrões Spring Boot e injeção de dependências
- Documentação OpenAPI/Swagger bem estruturada
- Uso de Lombok para reduzir boilerplate
- Validações de negócio centralizadas
- Logs estruturados em JSON
- Testes unitários presentes (estrutura de diretórios)
- Uso de enums para constantes de negócio

**Pontos de Melhoria:**
- Queries SQL embutidas em arquivos separados (boa prática), mas com lógica complexa e repetitiva
- Múltiplos CNPJs hardcoded nas queries SQL (deveria estar em configuração)
- Conversores com lógica de mapeamento manual (poderia usar MapStruct)
- Tratamento de exceções genérico em alguns pontos do controller
- Falta de paginação nos endpoints de listagem
- Código com alguns comentários em português misturados com inglês
- Alguns métodos do service poderiam ser refatorados para reduzir complexidade

---

## 14. Observações Relevantes

- O sistema utiliza JDBI ao invés de JPA/Hibernate, o que proporciona maior controle sobre as queries SQL
- Há suporte para múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas
- O projeto segue o padrão de microserviços atômicos do Banco Votorantim
- Implementa segurança via OAuth2 com JWT
- Possui infraestrutura como código (infra.yml) para deploy em Kubernetes/OpenShift
- O sistema faz distinção entre horário diurno e noturno para cálculos específicos
- Há mascaramento de dados sensíveis (CPF/CNPJ) nos logs para conformidade com LGPD
- A aplicação expõe métricas para Prometheus e health checks via Actuator
- Utiliza connection pool e datasource do Spring Boot para gerenciamento de conexões
- O projeto está configurado para build via Jenkins com propriedades específicas