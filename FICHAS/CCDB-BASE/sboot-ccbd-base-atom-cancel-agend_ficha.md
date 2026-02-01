# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de cancelamento de agendamentos de lançamentos futuros do Banco Digital (CCBD - Conta Corrente Banco Digital). O sistema permite cancelar agendamentos individuais por NSU (Número Sequencial Único) ou múltiplos agendamentos vinculados a um consentimento específico. Suporta dois tipos de agendamentos: conta corrente tradicional e boletos/pagamentos.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `CancelAgendController` | Controlador REST que expõe endpoints para cancelamento de agendamentos |
| `CancelAgendService` | Serviço de domínio para cancelamento de agendamentos de conta corrente |
| `CancelAgendBoletoService` | Serviço de domínio para cancelamento de agendamentos de boletos |
| `CancelAgendRepository` | Interface de repositório para operações em agendamentos de conta corrente |
| `CancelAgendBoletoRepository` | Interface de repositório para operações em agendamentos de boletos |
| `CancelAgendRepositoryImpl` | Implementação JDBI do repositório de conta corrente |
| `CancelAgendBoletoRepositoryImpl` | Implementação JDBI do repositório de boletos |
| `CancelAgend` | Entidade de domínio representando agendamento de conta corrente |
| `CancelAgendBoleto` | Entidade de domínio representando agendamento de boleto (herda de CancelAgend) |
| `CancelAgendConfiguration` | Configuração de beans do Spring para serviços e repositórios |
| `DatabaseConfiguration` | Configuração de múltiplos datasources (Sybase e SQL Server) |
| `LoggerHelper` | Utilitário para sanitização de mensagens de log |

## 3. Tecnologias Utilizadas

- **Framework Principal**: Spring Boot 2.x
- **Linguagem**: Java 11
- **Segurança**: Spring Security OAuth2 com JWT
- **Persistência**: JDBI 3.12.0 (SQL Object)
- **Bancos de Dados**: 
  - Sybase ASE (jConnect 16.3) - DBCONTACORRENTE
  - Microsoft SQL Server 7.0 - DBCCBD (Agendamento)
- **Documentação API**: Swagger/OpenAPI 3.0 (Springfox)
- **Logging**: Logback com formato JSON
- **Monitoramento**: Spring Actuator + Micrometer (Prometheus)
- **Build**: Maven 3.5.3+
- **Container**: Docker (base Java 11)
- **Utilitários**: Lombok, Apache Commons Lang3, Apache Commons Text
- **Auditoria**: springboot-arqt-base-trilha-auditoria-web

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/agendamentos-movimentacao/cancelar` | `CancelAgendController` | Cancela um agendamento específico por NSU |
| POST | `/v1/agendamentos-movimentacao/cancelar-por-consentimento` | `CancelAgendController` | Cancela todos os agendamentos vinculados a um consentimento |

**Parâmetros comuns**: codigoBanco, numeroAgencia, numeroConta, numeroCpfCnpj (headers)

## 5. Principais Regras de Negócio

1. **Validação de CPF/CNPJ**: O CPF/CNPJ informado deve corresponder ao titular da conta consultada
2. **Busca em cascata**: Primeiro busca em agendamentos de conta corrente; se não encontrar, busca em agendamentos de boletos
3. **Validação de status**: Apenas agendamentos com status diferente de "2" (executado) podem ser cancelados
4. **Autenticação**: Recupera CPF/CNPJ do token JWT caso não seja informado no header
5. **Cancelamento por consentimento**: Cancela múltiplos agendamentos vinculados ao mesmo ID de consentimento
6. **Atualização de status**: 
   - Conta corrente: altera `CdStatusAgendamento` para "2"
   - Boletos: altera `CdStatusAgendamento` para "4" e registra `dtAlteracao`
7. **Validação de dados**: Retorna erro 403 (Forbidden) se conta ou NSU/consentimento forem inválidos

## 6. Relação entre Entidades

**CancelAgend** (entidade base)
- Atributos: codigoBanco, numeroAgencia, numeroConta, numeroCpfCnpj, nsu

**CancelAgendBoleto** (herda de CancelAgend)
- Atributos adicionais: idConsentimento
- Representa agendamentos de boletos/pagamentos com suporte a consentimento

**Relacionamentos**:
- Ambas as entidades não possuem relacionamentos JPA, pois são DTOs de domínio
- A relação com banco é feita via queries SQL diretas através de JDBI

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| `VwContaCorrenteSaldoDia` | View | SELECT | View de conta corrente com saldo diário (Sybase) |
| `TbAgendamentoContaCorrente` | Tabela | SELECT | Tabela de agendamentos de conta corrente (Sybase) |
| `TbAgendamento` | Tabela | SELECT | Tabela principal de agendamentos (SQL Server) |
| `TbPessoaAgendamento` | Tabela | SELECT | Tabela de pessoas vinculadas aos agendamentos (SQL Server) |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| `TbAgendamentoContaCorrente` | Tabela | UPDATE | Atualiza status do agendamento para cancelado (status=2) no Sybase |
| `TbAgendamento` | Tabela | UPDATE | Atualiza status do agendamento para cancelado (status=4) e data de alteração no SQL Server |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `application.yml` | Leitura | Spring Boot | Configurações da aplicação (datasources, profiles, segurança) |
| `logback-spring.xml` | Leitura | Logback | Configuração de logs em formato JSON |
| `*.sql` | Leitura | JDBI (resources) | Queries SQL para validação e cancelamento de agendamentos |
| `sboot-ccbd-base-atom-cancel-lanc-futuro.yaml` | Leitura | Swagger Codegen | Especificação OpenAPI para geração de interfaces |

## 10. Filas Lidas

não se aplica

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **Servidor OAuth2/JWT** | API REST | Validação de tokens JWT via JWK endpoint (https://api-digitaldes.bancovotorantim.com.br/openid/connect/jwks.json) |
| **Banco Sybase ASE** | Banco de Dados | Acesso ao schema DBCONTACORRENTE para agendamentos de conta corrente |
| **SQL Server** | Banco de Dados | Acesso ao schema DBCCBD (ccbdagendamento) para agendamentos de boletos |
| **Prometheus** | Monitoramento | Exportação de métricas via endpoint /actuator/prometheus |

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com módulos domain e application
- Uso adequado de padrões como Repository e Service
- Configuração clara de múltiplos datasources
- Documentação via Swagger/OpenAPI
- Uso de Lombok reduzindo boilerplate
- Logging estruturado em JSON
- Sanitização de logs para segurança
- Testes unitários presentes (embora não enviados)

**Pontos de Melhoria:**
- Lógica de negócio no controller (deveria estar apenas no service)
- Uso de `Boolean` como retorno em vez de tipos mais expressivos
- Falta de tratamento de exceções mais granular
- Queries SQL em arquivos separados (bom), mas sem documentação inline
- Uso de `new ResponseEntity` em vez de métodos helper do Spring
- Falta de validação de entrada mais robusta (Bean Validation)
- Código mistura inglês e português em nomes de variáveis
- Ausência de DTOs específicos para request/response (usa entidades de domínio)
- Configuração de segurança poderia ser mais explícita
- Falta de circuit breaker ou retry para chamadas a banco

## 14. Observações Relevantes

1. **Arquitetura Multi-Banco**: O sistema acessa dois bancos de dados diferentes (Sybase e SQL Server) para diferentes tipos de agendamento, o que adiciona complexidade operacional

2. **Segurança**: Implementa OAuth2 com JWT, recuperando CPF/CNPJ do token quando não informado explicitamente

3. **Profiles Spring**: Suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas

4. **Deployment**: Preparado para Kubernetes/OpenShift com configurações de probes, resources e secrets

5. **Padrão Atômico**: Segue o padrão arquitetural "Atômico" do Banco Votorantim, com estrutura modular bem definida

6. **Versionamento de API**: Usa versionamento via path (`/v1/`)

7. **Auditoria**: Integra com sistema de trilha de auditoria corporativo

8. **Monitoramento**: Expõe métricas via Actuator na porta 9090 (separada da aplicação na 8080)

9. **Build**: Pipeline Jenkins configurado com propriedades específicas (jdk11, springboot-ocp, platform GOOGLE)

10. **Limitação**: Não há suporte para transações distribuídas entre os dois bancos de dados