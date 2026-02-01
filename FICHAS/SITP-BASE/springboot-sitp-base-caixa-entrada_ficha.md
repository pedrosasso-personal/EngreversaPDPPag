# Ficha Técnica do Sistema

---

## 1. Descrição Geral

O sistema **springboot-sitp-base-caixa-entrada** é uma API REST desenvolvida em Spring Boot que tem como objetivo consultar o status de transferências ITP (Internet Transfer Protocol) realizadas através do sistema de caixa de entrada. A aplicação fornece um endpoint para consulta de informações detalhadas sobre operações de transferência bancária, incluindo dados do remetente, favorecido, valores e status da operação. O sistema integra-se com um banco de dados Sybase para recuperar informações através de stored procedures.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Server.java** | Classe principal da aplicação Spring Boot, responsável por inicializar o contexto e habilitar o Swagger |
| **TransferenciaITPApi.java** | Controlador REST que expõe o endpoint de consulta de transferências ITP |
| **TransferenciaITPService.java** | Camada de serviço que implementa a lógica de negócio para consulta de status |
| **TransferenciaITPRepository.java** | Repositório responsável pela comunicação com o banco de dados Sybase |
| **TransferenciaITP.java** | Entidade de domínio que representa os dados de uma transferência ITP |
| **StatusOperacaoMapper.java** | Mapper responsável por converter ResultSet em objetos TransferenciaITP |
| **StatusOperacaoStoredProcedure.java** | Classe que encapsula a chamada à stored procedure do banco |
| **DocketConfiguration.java** | Configuração do Swagger para documentação da API |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.0.0.RELEASE** - Framework principal da aplicação
- **Spring Web** - Para criação de endpoints REST
- **Spring JDBC** - Para acesso ao banco de dados
- **Sybase jConnect 7.07-SP136** - Driver JDBC para banco Sybase
- **Swagger/Springfox 2.8.0** - Documentação da API
- **Lombok 1.16.20** - Redução de código boilerplate
- **Logback** - Framework de logging
- **Gradle 4.5.1** - Sistema de build
- **Docker** - Containerização da aplicação
- **JUnit** - Testes unitários e funcionais
- **JMeter** - Testes de performance
- **Jacoco** - Cobertura de código
- **SonarQube** - Análise de qualidade de código
- **Bibliotecas internas Votorantim**: springboot-arqt-base-trilha-auditoria-web, springboot-arqt-base-security-basic, springboot-arqt-base-lib-database

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | /v1/caixa-entrada/transferencia/{numeroProtocoloITP} | TransferenciaITPApi | Consulta o status de uma transferência ITP pelo número de protocolo |

---

## 5. Principais Regras de Negócio

1. **Consulta de Status de Transferência**: O sistema permite consultar o status de uma transferência ITP através do código de protocolo, retornando informações completas sobre a operação incluindo remetente, favorecido, valores, histórico e status atual.

2. **Autenticação e Autorização**: A API utiliza autenticação básica (Basic Auth) e controle de acesso baseado em roles (USER, ADMIN) através de LDAP ou usuários in-memory conforme o ambiente.

3. **Tratamento de Erros**: Utiliza BusinessException para tratamento centralizado de erros de negócio, especialmente em casos de falha na consulta ao banco de dados.

4. **Auditoria**: Implementa trilha de auditoria através da biblioteca springboot-arqt-base-trilha-auditoria-web, registrando informações de ticket e fase nos logs.

---

## 6. Relação entre Entidades

**TransferenciaITP** (Entidade de Domínio):
- Representa uma transferência bancária no sistema ITP
- Atributos principais:
  - `codProtocolo` (BigDecimal): Identificador único da transferência
  - `dtMovimento` (Date): Data da movimentação
  - `nomeRemetente`, `contaRemetente`: Dados do remetente
  - `agenciaFavorecido`, `cnpjCpfFavorecido`, `nomeFavorecido`, `contaFavorecido`: Dados do favorecido
  - `valor` (Double): Valor da transferência
  - `historico`, `tipLancamento`, `nrOrigem`: Informações da operação
  - `nomeUsuario`: Usuário que realizou a operação
  - `mneStatus`, `mneErro`, `mneDevolucao`: Status e informações de erro/devolução

Não há relacionamentos complexos entre entidades, pois o sistema trabalha com uma única entidade principal.

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| BV_LANCAMENTO_CAIXA_ENTRADA | Stored Procedure | SELECT/READ | Procedure que retorna informações completas de uma transferência ITP pelo código de protocolo |
| DBITP (Database) | Database | SELECT/READ | Banco de dados Sybase que armazena informações do sistema ITP |

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | leitura | /usr/etc/log/ (ambientes) ou classpath (local) | Arquivo de configuração de logs da aplicação |
| application.yml | leitura | src/main/resources/ | Arquivo de configuração principal da aplicação |
| application-local.yml | leitura | src/main/resources/ | Configurações específicas do ambiente local |
| roles/*.yml | leitura | src/main/resources/roles/ | Arquivos de configuração de roles por ambiente (des, qa, uat, prd, local) |
| .env | leitura | Docker runtime | Variáveis de ambiente para execução em container |

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
| **Banco Sybase (DBITP)** | Database | Banco de dados principal que armazena informações das transferências ITP. Conexão via JDBC com diferentes URLs por ambiente (des, qa, uat, prd) |
| **LDAP BVNet** | Autenticação | Serviço de autenticação e autorização corporativo utilizado nos ambientes não-locais para validação de usuários e grupos |
| **Nexus (nexus.bvnet.bv)** | Repositório de Artefatos | Repositório Maven/Gradle para dependências e publicação de artefatos |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades em camadas (API, Service, Repository, Domain)
- Uso adequado de anotações Lombok para redução de boilerplate
- Configuração de testes em múltiplas camadas (unit, integration, functional)
- Documentação da API com Swagger
- Uso de bibliotecas corporativas padronizadas
- Configuração adequada de ambientes (local, des, qa, uat, prd)
- Implementação de probes de liveness e readiness para Kubernetes/OpenShift

**Pontos de Melhoria:**
- Uso de `synchronized` desnecessário no método do controller (TransferenciaITPApi.consulta)
- Gerenciamento manual de conexões JDBC no repositório ao invés de usar JdbcTemplate completamente
- Falta de validação de entrada no endpoint (numeroProtocoloITP poderia ser null ou inválido)
- Ausência de testes unitários implementados (diretórios vazios)
- Comentários em português misturados com código em inglês
- Classe StatusOperacaoStoredProcedure declarada mas não utilizada (o repositório usa JDBC direto)
- Falta de tratamento específico para casos onde a transferência não é encontrada (retorna null)
- Configurações de segurança com senhas em texto claro nos arquivos de exemplo (application-local.yml)

---

## 14. Observações Relevantes

1. **Ambientes Múltiplos**: O sistema está preparado para execução em 5 ambientes distintos (local, des, qa, uat, prd) com configurações específicas para cada um.

2. **Infraestrutura como Código**: Possui arquivos de configuração para deploy em OpenShift/Kubernetes (infra.yml) com definições de ConfigMaps, Secrets, Probes e Volumes.

3. **Pipeline CI/CD**: Configurado para integração com Jenkins (jenkins.properties) e possui tasks Gradle para build, testes e geração de imagem Docker.

4. **Segurança**: Implementa autenticação básica com suporte a LDAP corporativo e usuários in-memory para testes. Possui controle de acesso baseado em roles.

5. **Monitoramento**: Configurado com SonarQube para análise de qualidade e Jacoco para cobertura de código.

6. **Encoding**: O sistema trabalha com charset cp850 e iso_1 na conexão com Sybase, indicando necessidade de tratamento especial de caracteres.

7. **Versionamento**: Utiliza plugin de release do Gradle para gestão de versões seguindo semantic versioning.

8. **Documentação**: README.md fornece links para repositórios de referência com exemplos de implementação de CRUD, WS Client e REST Client.

9. **Proxy**: Configurações indicam uso de proxy corporativo com exceções para nexus.bvnet.bv.

10. **Recursos Computacionais**: Dockerfile configurado com JVM options conservadores (Xms64m, Xmx128m) adequados para ambientes containerizados.