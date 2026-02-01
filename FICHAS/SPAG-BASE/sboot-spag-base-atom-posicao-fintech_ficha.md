# Ficha Técnica do Sistema

---

## 1. Descrição Geral

Sistema atômico responsável por gerenciar a posição financeira de contas Fintech do Banco Votorantim. O sistema permite atualizar valores de pagamentos de boletos e realizar estornos, mantendo o controle do saldo de investimento e total de boletos pagos por conta.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **PosicaoFintechController** | Controlador REST que expõe endpoints para atualização e estorno de posições |
| **PosicaoFintechService** | Serviço de domínio que implementa regras de negócio para validação de saldo e operações |
| **PosicaoFintechRepositoryImpl** | Implementação do repositório usando JDBI para acesso ao banco de dados Sybase |
| **PosicaoFintechMapper** (infrastructure) | Mapper JDBI para conversão de ResultSet em objetos de domínio |
| **PosicaoFintechMapper** (presentation) | Mapper para conversão entre objetos de representação e domínio |
| **PosicaoFintechExceptionHandler** | Tratador global de exceções da aplicação |
| **PosicaoFintechConfiguration** | Configuração de beans Spring e JDBI |
| **OpenApiConfiguration** | Configuração do Swagger/OpenAPI |
| **PosicaoFintech** | Entidade de domínio representando a posição financeira |
| **Atualizacao** | Objeto de domínio para operações de atualização |
| **Estorno** | Objeto de domínio para operações de estorno |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.x** - Framework principal
- **Java 11** - Linguagem de programação
- **JDBI 3.9.1** - Framework de acesso a dados
- **Sybase jConnect 16.3** - Driver JDBC para Sybase
- **Swagger/Springfox 2.9.2** - Documentação de API
- **Lombok** - Redução de código boilerplate
- **Spring Security OAuth2** - Segurança JWT
- **Micrometer/Prometheus** - Métricas e monitoramento
- **Logback** - Logging
- **JUnit 5** - Testes unitários
- **Mockito** - Mocks para testes
- **Maven** - Gerenciamento de dependências
- **Docker** - Containerização
- **Grafana** - Visualização de métricas

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| PUT | /v1/api/posicao-fintech/atualiza | PosicaoFintechController | Atualiza o valor total de boletos pagos para uma conta Fintech |
| PUT | /v1/api/posicao-fintech/estorno | PosicaoFintechController | Estorna um valor de pagamento de boleto |

---

## 5. Principais Regras de Negócio

1. **Validação de Saldo Disponível**: Antes de atualizar a posição com um novo pagamento, o sistema valida se há saldo suficiente. A fórmula aplicada é:
   - `(valorDisponivel + saldoInvestimento - totalBoletoPago - valorPagamento) >= 0`
   - Se o resultado for negativo, lança exceção: "O saldo da fintech e insuficiente para pagamento do boleto."

2. **Atualização de Posição**: Incrementa o valor total de boletos pagos (`VrTotalBoletoPago`) com o valor do novo pagamento.

3. **Estorno de Pagamento**: Decrementa o valor total de boletos pagos (`VrTotalBoletoPago`) com o valor a ser estornado.

4. **Seleção de Registro Mais Recente**: Todas as operações trabalham com o registro mais recente da conta (MAX(CdPosicaoContaFintech)).

---

## 6. Relação entre Entidades

**PosicaoFintech** (Entidade Principal)
- Atributos:
  - `saldoInvestimento` (BigDecimal): Saldo disponível em investimentos
  - `totalBoletoPago` (BigDecimal): Total acumulado de boletos pagos

**Atualizacao** (Objeto de Comando)
- Atributos:
  - `numeroConta` (String): Identificador da conta
  - `valorDisponivel` (BigDecimal): Valor disponível para pagamento
  - `valorPagamento` (BigDecimal): Valor do boleto a ser pago

**Estorno** (Objeto de Comando)
- Atributos:
  - `numeroConta` (Long): Identificador da conta
  - `valorPagamento` (BigDecimal): Valor a ser estornado

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBCONTACORRENTE.dbo.TbPosicaoContaFintech | tabela | SELECT | Consulta a posição mais recente da conta Fintech (saldo de investimento e total de boletos pagos) |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBCONTACORRENTE.dbo.TbPosicaoContaFintech | tabela | UPDATE | Atualiza o valor total de boletos pagos (incremento) |
| DBCONTACORRENTE.dbo.TbPosicaoContaFintech | tabela | UPDATE | Atualiza o valor total de boletos pagos (decremento para estorno) |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot | Configurações da aplicação (datasource, profiles, security) |
| logback-spring.xml | leitura | Logback | Configuração de logs da aplicação |
| posicaoFintech.sql | leitura | PosicaoFintechRepositoryImpl | Query SQL para consulta de posição |
| atualizar.sql | leitura | PosicaoFintechRepositoryImpl | Query SQL para atualização de posição |
| estornar.sql | leitura | PosicaoFintechRepositoryImpl | Query SQL para estorno de pagamento |

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
| Sybase Database (DBCONTACORRENTE) | Banco de Dados | Banco de dados principal contendo informações de posição de contas Fintech |
| OAuth2 JWT Provider | Autenticação | Serviço de autenticação e autorização via JWT (URLs variam por ambiente: des, qa, uat, prd) |
| Prometheus | Monitoramento | Exportação de métricas da aplicação |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem organizada seguindo padrões de Clean Architecture (separação em camadas: domain, application, common)
- Uso adequado de injeção de dependências e inversão de controle
- Implementação de testes unitários para as principais classes
- Uso de Lombok para reduzir boilerplate
- Configuração adequada de monitoramento e observabilidade (Prometheus, Grafana)
- Documentação de API via Swagger
- Separação clara entre objetos de domínio e representação

**Pontos de Melhoria:**
- Mensagens de erro em português misturadas no código (deveria usar internacionalização)
- Falta de validação de entrada nos endpoints (Bean Validation)
- Queries SQL embutidas em arquivos separados (poderia usar JPA/Hibernate para maior portabilidade)
- Ausência de testes de integração e funcionais (estrutura existe mas não há implementação)
- Falta de tratamento específico para diferentes tipos de exceção de banco de dados
- Logs com informações sensíveis (números de conta) sem ofuscação
- Configuração de segurança básica (poderia ter controle de acesso mais granular)

---

## 14. Observações Relevantes

1. **Ambiente Multi-Profile**: A aplicação suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas de datasource e URLs de autenticação.

2. **Banco de Dados Legado**: Utiliza Sybase como banco de dados, o que pode limitar a portabilidade da aplicação.

3. **Arquitetura Atômica**: Segue o padrão de microserviços atômicos do Banco Votorantim, com estrutura modular bem definida.

4. **Segurança**: Implementa autenticação OAuth2 com JWT, mas os endpoints não possuem controle de autorização granular visível no código.

5. **Monitoramento**: Infraestrutura completa de observabilidade com Prometheus e Grafana pré-configurados.

6. **Deploy**: Preparado para deploy em OpenShift/Kubernetes com configurações de infraestrutura como código (infra.yml).

7. **Versionamento de API**: Utiliza versionamento via path (/v1/api).

8. **Documentação**: README.md fornece informações básicas, mas poderia ser mais detalhado sobre regras de negócio e fluxos.

9. **Dependências Internas**: Utiliza bibliotecas proprietárias do Banco Votorantim (arqt-base-*) para padronização.

10. **Testes Arquiteturais**: Possui profile Maven para validação de regras arquiteturais via ArchUnit.