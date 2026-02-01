# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de consulta de dados de contas e protocolos de transações para Fintechs integradas ao SPAG (Sistema de Pagamentos). O sistema oferece APIs REST para consultar informações de contas de usuários, múltiplas contas, saldo e protocolos de transações (pagamentos, transferências, etc.), validando permissões e integrando com banco de dados SQL Server.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Server** | Classe principal Spring Boot que inicializa a aplicação |
| **ConsultaDadosContaService** | Serviço de negócio para consulta de dados de contas e saldos |
| **ConsultaProtocoloService** | Serviço de negócio para consulta de protocolos de transações |
| **ConsultaDadosContaRepository** | Repositório para acesso a dados de contas no banco |
| **ConsultaDadosFintechRepository** | Repositório para validação de existência de Fintechs |
| **ConsultaProtocoloRepository** | Repositório para consulta de protocolos/lançamentos |
| **ConsultaContaFintechAPI** | Controller REST para endpoints de consulta de contas |
| **ConsultaProtocoloAPI** | Controller REST para endpoints de consulta de protocolos |
| **ConsultaContaFintechExceptionHandler** | Tratamento centralizado de exceções |
| **ValidationException** | Exceção customizada para erros de validação |
| **DocketConfiguration** | Configuração do Swagger para documentação da API |
| **UtilSpag** | Utilitários para conversão JSON e manipulação de datas |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.7.18** - Framework principal
- **Spring Web** - APIs REST
- **Spring JDBC** - Acesso a banco de dados
- **SQL Server** - Banco de dados (driver mssql-jdbc 7.0.0)
- **Springfox Swagger 3.0.0** - Documentação de APIs
- **Lombok 1.18.24** - Redução de boilerplate
- **Logback** - Logging com suporte a JSON
- **JUnit 4.13.2** - Testes unitários
- **Mockito 2.17.0** - Mocks para testes
- **Gradle 7.5.1** - Build e gerenciamento de dependências
- **Docker** - Containerização (OpenJDK 8 com OpenJ9)
- **Apache Commons Lang3** - Utilitários
- **Jackson** - Serialização/deserialização JSON
- **Bibliotecas Votorantim (arqt-base)** - Segurança, auditoria, LDAP

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/consultaContaUsuarioFintech` | ConsultaContaFintechAPI | Consulta dados de uma conta de usuário Fintech |
| POST | `/v1/consultaMultiplasContasUsuarioFintech` | ConsultaContaFintechAPI | Consulta dados de múltiplas contas simultaneamente |
| POST | `/v1/consultaSaldoFintech` | ConsultaContaFintechAPI | Consulta saldo de uma conta Fintech (em desenvolvimento) |
| POST | `/consulta/v1/consultaProtocolo` | ConsultaProtocoloAPI | Consulta múltiplos protocolos de transação |
| POST | `/consulta/v2/consultaProtocolo` | ConsultaProtocoloAPI | Consulta protocolo por número ou NSU (sem retornar nuControleSPB) |
| POST | `/consulta/v3/consultaProtocolo` | ConsultaProtocoloAPI | Consulta protocolo por número ou NSU (com nuControleSPB) |

---

## 5. Principais Regras de Negócio

1. **Validação de Fintech**: Verifica se a Fintech existe e está ativa antes de permitir consultas
2. **Validação de Conta Base**: Valida se a conta pertence a uma Fintech através dos 4 primeiros dígitos
3. **Validação de Data de Posição**: Para consulta de saldo, a data deve ser igual à data atual
4. **Validação de Tipo de Movimento**: Determina se a transação é Débito (D), Crédito (C) ou Erro (E) comparando CNPJ solicitante com remetente/favorecido
5. **Validação de Data de Movimento**: Protocolo deve pertencer à data de movimento informada
6. **Agência Especial 1111**: Permite consulta com agência vazia ou "1111" para contas específicas
7. **Tratamento de Status de Protocolo**: Mapeia códigos numéricos para descrições textuais de status
8. **Filtragem de Dados Sensíveis**: Controla retorno de campos como nuControleSPB conforme versão da API

---

## 6. Relação entre Entidades

**Principais entidades e relacionamentos:**

- **ResponseDadosConta**: Contém dados da conta (número, agência, status, cliente global, razão social, tipo pessoa, documento)
  - Possui **ListaConta** (lista de contas de pagamento associadas)
  - Possui **ListaUsuario** (lista de usuários vinculados à conta)

- **Conta**: Representa uma conta de pagamento (número, agência, tipo, descrição)

- **Usuario**: Representa usuário vinculado à conta (tipo pessoa, tipo vínculo, documento, nome)

- **Lancamento**: Representa uma transação/protocolo com dados de remetente, favorecido, valores, datas e status

- **ConsultaProtocoloResponse**: Agrupa dados do protocolo, movimentação, beneficiário e remetente

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbContaUsuarioFintech | Tabela | SELECT | Contas de usuários das Fintechs |
| TbParametroPagamentoFintech | Tabela | SELECT | Parâmetros e configurações das Fintechs |
| TbContaPagamentoFintech | Tabela | SELECT | Contas de pagamento vinculadas às Fintechs |
| TbUsuarioContaFintech | Tabela | SELECT | Usuários vinculados às contas |
| TbRelacaoContaUsuarioFintech | Tabela | SELECT | Relacionamento entre contas e usuários |
| TbTipoVinculoConta | Tabela | SELECT | Tipos de vínculo (Titular, Co-Titular, etc.) |
| TbLancamento | Tabela | SELECT | Lançamentos/transações de pagamento |
| TbLancamentoPessoa | Tabela | SELECT | Dados de pessoas envolvidas nos lançamentos |
| TbErroProcessamento | Tabela | SELECT | Erros ocorridos no processamento de lançamentos |

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | Spring Boot | Configurações da aplicação (datasource, profiles, etc.) |
| application-local.yml | Leitura | Spring Boot | Configurações específicas do ambiente local |
| logback-spring.xml | Leitura | Logback | Configuração de logs (console, JSON, níveis) |
| consultadadoscontarepository-sql.xml | Leitura | ConsultaDadosContaRepository | Queries SQL para consulta de contas |
| consultadadosfintechrepository-sql.xml | Leitura | ConsultaDadosFintechRepository | Queries SQL para validação de Fintechs |
| consultaprotocolorepository-sql.xml | Leitura | ConsultaProtocoloRepository | Queries SQL e stored procedures para protocolos |
| roles/*.yml | Leitura | Spring Security | Configuração de roles por ambiente (des, qa, uat, prd) |

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
| SQL Server (DBSPAG) | Banco de Dados | Banco principal com dados de contas, Fintechs e transações |
| LDAP BVNet | Autenticação | Autenticação de usuários via LDAP corporativo (configurável por ambiente) |
| Nexus | Repositório | Repositório de artefatos Maven/Gradle para dependências |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades (controller, service, repository)
- Uso adequado de anotações Lombok reduzindo boilerplate
- Tratamento centralizado de exceções
- Cobertura de testes unitários presente
- Documentação Swagger configurada
- Uso de bibliotecas corporativas padronizadas
- Logs estruturados em JSON

**Pontos de Melhoria:**
- Queries SQL embutidas em XML ao invés de usar JPA/Hibernate
- Lógica de negócio misturada com acesso a dados em alguns pontos
- Código comentado em várias partes (ex: validação de conta em fintech)
- Alguns métodos muito longos (ex: `consultaDadosConta`, `consultaProtocolo`)
- Tratamento de exceções genérico em alguns casos
- Falta de validação de entrada em alguns endpoints
- Uso de `String.trim()` repetitivo poderia ser centralizado
- Alguns testes com muitos mocks, dificultando manutenção
- Conversão manual de tipos poderia usar mappers (MapStruct)

---

## 14. Observações Relevantes

1. **Ambientes**: Sistema preparado para múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas
2. **Segurança**: Autenticação Basic configurada, com suporte a LDAP e usuários in-memory para testes
3. **Versionamento de API**: Implementa versionamento de endpoints (v1, v2, v3) para evolução controlada
4. **Stored Procedure**: Endpoint v2/v3 de consulta de protocolo utiliza stored procedure `PrConsultarProtocoloV2`
5. **Docker**: Aplicação containerizada com imagem baseada em OpenJDK 8 com OpenJ9 para otimização de memória
6. **CI/CD**: Integração com Jenkins configurada via `jenkins.properties`
7. **Infraestrutura como Código**: Arquivo `infra.yml` define configurações de deployment (probes, configmaps, volumes)
8. **Testes**: Estrutura completa com testes unitários, integração e funcionais (JMeter)
9. **Auditoria**: Integração com biblioteca de trilha de auditoria corporativa
10. **Limitação Conhecida**: Endpoint de consulta de saldo (`consultaSaldoFintech`) retorna null, indicando implementação incompleta