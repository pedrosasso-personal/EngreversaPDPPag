# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-spag-base-atom-pagamento-rebate** é um microserviço atômico desenvolvido em Java com Spring Boot, responsável por gerenciar os pagamentos de rebate (bonificações/reembolsos) no contexto do sistema SPAG (Sistema de Pagamentos) do Banco Votorantim. O sistema permite criar, consultar, aprovar e processar pagamentos de rebate para clientes, com suporte a diferentes periodicidades, formas de cálculo e tipos de apuração.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `PagamentoRebateController` | Controlador REST que expõe endpoints para operações com pagamentos de rebate |
| `PagamentoRebateService` | Serviço de domínio contendo as regras de negócio para gerenciamento de pagamentos |
| `JdbiPagamentoRebateRepository` | Interface de repositório JDBI para acesso ao banco de dados |
| `PagamentoRebate` | Entidade de domínio representando um pagamento de rebate |
| `PagamentoRebateMapper` | Mapeador entre objetos de domínio e representações REST |
| `PagamentoRebateRowMapper` | Mapeador JDBI para conversão de ResultSet em entidades |
| `RestResponseEntityExceptionHandler` | Tratador global de exceções HTTP |
| `JdbiConfiguration` | Configuração do JDBI e registro de componentes |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot** (framework principal)
- **JDBI 3.9.1** (acesso a banco de dados)
- **SQL Server** (banco de dados)
- **Swagger/Springfox 2.9.2** (documentação de API)
- **Lombok** (redução de boilerplate)
- **Spring Actuator + Prometheus** (métricas e monitoramento)
- **Grafana** (visualização de métricas)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **JUnit 5 + Mockito** (testes)
- **RestAssured** (testes funcionais)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/pagamentos` | `PagamentoRebateController` | Busca pagamento por produto, cliente e parâmetro |
| POST | `/pagamentos` | `PagamentoRebateController` | Cria novo pagamento de rebate |
| GET | `/pagamentos/relatorio` | `PagamentoRebateController` | Busca pagamentos por período de apuração (paginado) |
| GET | `/pagamentos/extrato` | `PagamentoRebateController` | Busca pagamentos cadastrados hoje (paginado) |
| GET | `/pagamentos/processamento` | `PagamentoRebateController` | Busca pagamentos por data de pagamento |
| GET | `/pagamentos/aprovacao` | `PagamentoRebateController` | Busca pagamentos para aprovação com filtros (paginado) |
| PATCH | `/pagamentos/{id}/statusProcessamentoExtrato` | `PagamentoRebateController` | Finaliza processamento de extrato |
| PATCH | `/pagamentos/{id}/statusPagamento` | `PagamentoRebateController` | Altera status do pagamento |
| PATCH | `/pagamentos/{id}/codigoProtocolo` | `PagamentoRebateController` | Atualiza código de protocolo |

---

## 5. Principais Regras de Negócio

1. **Validação de Duplicidade**: Não permite criar pagamento duplicado para mesmo produto, cliente, parâmetro e data de pagamento
2. **Controle de Status**: Gerencia ciclo de vida do pagamento (Pendente, Pendente Aprovação, Pago, Recusado, Cancelado)
3. **Processamento de Extrato**: Controla se o pagamento já foi processado no extrato (Aguardando/Finalizado)
4. **Cálculo de Impostos**: Suporta cálculo de ISS e IR sobre valores de pagamento
5. **Tipos de Apuração**: Permite apuração por quantidade ou valor de operações
6. **Formas de Rebate**: Suporta rebate por valor fixo ou percentual
7. **Periodicidade**: Suporta pagamentos diários, semanais, mensais ou personalizados
8. **Aprovação**: Alguns pagamentos necessitam aprovação antes de serem efetivados
9. **Auditoria**: Registra usuário e data de inclusão/alteração de cada operação
10. **Paginação**: Todas as consultas de listagem suportam paginação

---

## 6. Relação entre Entidades

**Entidade Principal: PagamentoRebate**

Atributos principais:
- Identificação: id, codigoProduto, codigoParametroCliente, cpfCnpjCliente
- Valores: valorPagamentoBruto, valorPagamentoLiquido, valorImpostoISS, valorImpostoIR
- Apuração: quantidadeTotalApurado, valorTotalApurado, dataInicioApuracao, dataFimApuracao
- Configuração: tipoPeriodicidade, formaRebate, tipoApuracao, tipoEntrada
- Contas: valorRede, contaCreditoRede, valorCorban, contaCreditoCorban
- Status: statusPagamento, statusProcessamentoExtrato
- Auditoria: dataInclusao, dataAlteracao, loginUsuario, loginAprovador

**Enumerações relacionadas:**
- StatusPagamento, StatusProcessamentoExtrato, Periodicidade, FormaRebate, TipoApuracao, TipoEntrada, TipoConta, ApuracaoBancaria, ContagemPrazo, Flag

**DTOs:**
- PagamentoRebatePaginado (extends PagamentoRebate + totalRegistros)
- RelatorioPagamentoDto (versão simplificada para relatórios)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| spagPagamentoRebate.TbPagamentoRebate | Tabela | SELECT | Consulta pagamentos por diversos filtros (produto/cliente, data apuração, data inclusão, data pagamento, aprovação, ID) |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| spagPagamentoRebate.TbPagamentoRebate | Tabela | INSERT | Insere novos registros de pagamento de rebate |
| spagPagamentoRebate.TbPagamentoRebate | Tabela | UPDATE | Atualiza status de processamento de extrato |
| spagPagamentoRebate.TbPagamentoRebate | Tabela | UPDATE | Atualiza status de pagamento e usuário aprovador |
| spagPagamentoRebate.TbPagamentoRebate | Tabela | UPDATE | Atualiza código de protocolo |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | Spring Boot | Configurações da aplicação (datasource, profiles, actuator) |
| logback-spring.xml | Leitura | Logback | Configuração de logs (console, JSON) |
| *.sql (queries JDBI) | Leitura | JdbiPagamentoRebateRepository | Queries SQL para operações no banco |

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
| SQL Server (DBSPAG2) | Banco de Dados | Banco de dados principal para persistência de pagamentos |
| API Gateway OAuth2 | Autenticação | Validação de tokens JWT via JWK (diferentes URLs por ambiente) |
| Prometheus | Monitoramento | Exportação de métricas da aplicação |
| Grafana | Visualização | Dashboard de métricas (configuração local) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem organizada em camadas (domain, application, common)
- Uso adequado de padrões como Repository, Service, Mapper
- Separação clara entre entidades de domínio e representações REST
- Boa cobertura de testes (unitários, integração, funcionais)
- Uso de enums para valores fixos com conversão para banco
- Documentação Swagger configurada
- Tratamento centralizado de exceções
- Uso de Lombok para reduzir boilerplate
- Configuração de métricas e observabilidade

**Pontos de Melhoria:**
- Alguns métodos de serviço poderiam ser quebrados em métodos menores
- Falta validação de entrada em alguns endpoints (Bean Validation)
- Alguns nomes de variáveis em português misturados com inglês
- Poderia ter mais documentação inline (JavaDoc) nas classes principais
- Alguns testes poderiam ter assertions mais específicas

O código demonstra boas práticas de desenvolvimento, arquitetura limpa e preocupação com qualidade, mas há espaço para melhorias em validações e documentação.

---

## 14. Observações Relevantes

1. **Arquitetura Modular**: O projeto segue arquitetura hexagonal com separação clara entre camadas (domain, application, common)

2. **Multi-ambiente**: Suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas

3. **Auditoria**: Integração com biblioteca de trilha de auditoria do Banco Votorantim (bv-arqt-base-trilha-auditoria-web)

4. **Profiles Maven**: Possui profiles específicos para diferentes tipos de teste (unit, integration, functional, architecture)

5. **ArchUnit**: Implementa testes de arquitetura para garantir conformidade com padrões estabelecidos

6. **Containerização**: Dockerfile configurado com OpenJ9 JVM otimizada para containers

7. **CI/CD**: Configuração para Jenkins (jenkins.properties) e infraestrutura como código (infra.yml)

8. **Segurança**: Autenticação via OAuth2 com validação de tokens JWT

9. **Observabilidade**: Endpoints de health check, métricas Prometheus e dashboards Grafana

10. **Padrão de Nomenclatura**: Segue convenção do Banco Votorantim (sboot-spag-base-atom-*)

11. **Versionamento**: Versão atual 0.12.0, indicando projeto em evolução

12. **Dependências Corporativas**: Utiliza bibliotecas padronizadas do Banco Votorantim (arqt-base-*)