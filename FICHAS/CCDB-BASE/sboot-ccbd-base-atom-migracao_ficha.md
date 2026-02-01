---
## Ficha Técnica do Sistema

### 1. Descrição Geral
Sistema responsável pelo gerenciamento de processos de migração de contas correntes e chaves PIX entre instituições financeiras. O sistema controla o fluxo de migração de contas, incluindo portabilidade de chaves PIX, atualização de status, validação de dados e integração com sistemas legados (Sybase e SQL Server). Oferece APIs REST para consulta e atualização de informações de migração tanto para aplicações internas (Cockpit) quanto para aplicativos externos (App).

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **MigracaoController** | Controlador REST que expõe endpoints para operações de migração de contas e chaves PIX |
| **MigracaoChavePixServiceImpl** | Implementa regras de negócio para migração de chaves PIX, incluindo validações e controle de status |
| **MigracaoContaServiceImpl** | Gerencia operações de migração de contas correntes |
| **MigracaoBVINServiceImpl** | Responsável por atualizar envelope de investimentos no sistema BVIN |
| **ChavePixRepositoryImpl** | Acesso a dados de chaves PIX no banco Sybase |
| **MigracaoChavePixRepositoryImpl** | Acesso a dados de migração de chaves PIX no banco Sybase |
| **MigracaoContaRepositoryImpl** | Acesso a dados de migração de contas no banco Sybase |
| **MigracaoBVINRepositoryImpl** | Acesso a dados de envelope de investimentos no SQL Server |
| **ResourceExceptionHandler** | Tratamento centralizado de exceções da aplicação |
| **DataBaseConfiguration** | Configuração de conexões com múltiplos bancos de dados (Sybase e SQL Server) |

### 3. Tecnologias Utilizadas
- **Framework**: Spring Boot 2.x
- **Linguagem**: Java 11
- **Persistência**: JDBI 3.9.1
- **Bancos de Dados**: Sybase (jConnect 16.3), SQL Server (JDBC 7.4.0)
- **Segurança**: Spring Security OAuth2 com JWT
- **Documentação**: Swagger/OpenAPI 3.0.0
- **Observabilidade**: Spring Actuator, Micrometer, Prometheus, Grafana
- **Auditoria**: springboot-arqt-base-trilha-auditoria-web 2.3.2
- **Pool de Conexões**: HikariCP
- **Build**: Maven 3.3+
- **Containerização**: Docker
- **Orquestração**: OpenShift (Google Cloud Platform)
- **Testes**: JUnit 5, Mockito, RestAssured, Pact

### 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | /v1/migracao/chavePix | MigracaoController | Consulta migração de chave PIX para aplicativo (com validação de CPF/CNPJ) |
| POST | /v1/migracao/chavePix | MigracaoController | Cadastra nova migração de chave PIX (Cockpit) |
| PUT | /v1/migracao/chavePix/{id} | MigracaoController | Altera migração de chave PIX (App) |
| GET | /v1/migracao/chavePix/cockpit | MigracaoController | Consulta migração de chave PIX (Cockpit) |
| PUT | /v1/migracao/chavePix/cockpit/{id} | MigracaoController | Altera migração de chave PIX (Cockpit) |
| GET | /v1/migracao/chave-portabilidade | MigracaoController | Consulta chaves PIX em processo de portabilidade |
| GET | /v1/migracao/chavePix/status-migracao | MigracaoController | Consulta status de migração de chaves PIX |
| POST | /v1/migracao/chavePix/status-migracao | MigracaoController | Atualiza status de portabilidade de chave PIX |
| GET | /v1/migracao/conta | MigracaoController | Consulta migração de contas correntes |
| PUT | /v1/migracao/conta/{id} | MigracaoController | Atualiza dados de migração de conta |
| PUT | /v1/migracao/bvin/ | MigracaoController | Atualiza envelope de investimentos BVIN |

### 5. Principais Regras de Negócio

1. **Validação de Origem**: Sistema diferencia requisições vindas do App (aplicativo) e Cockpit (sistema interno), aplicando validações específicas para cada origem
2. **Validação de CPF/CNPJ**: Para requisições do App, valida se o CPF/CNPJ do token JWT corresponde ao proprietário da conta
3. **Controle de Status de Migração**: Gerencia estados da migração (INICIAL, NAO_ACEITO, ACEITO, EM_PORTABILIDADE, CONCLUIDO, EXCLUIDO, etc.)
4. **Controle de Status de Portabilidade**: Gerencia estados da portabilidade de chaves PIX (NAO_PROCESSADO, SALVO, CONFIRMADO, CONCLUIDO, EXCLUIDO)
5. **Fluxo de Portabilidade**: Implementa fluxo completo de portabilidade com ações de SALVAR, CONFIRMAR, CONCLUIR e EXCLUIR
6. **Validação de Conclusão**: Só conclui migração quando todas as chaves PIX associadas estiverem com status CONCLUIDO
7. **Filtro de Data**: Lista apenas migrações com data prevista menor ou igual à data atual
8. **Filtro de Registros Ativos**: Permite filtrar registros ativos/inativos
9. **Aceite de Migração**: Controla se o cliente aceitou ou não a migração
10. **Atualização Condicional**: Permite atualização parcial de dados de migração de conta (protocolo ida/volta, valor migrado, erro)

### 6. Relação entre Entidades

**Entidades Principais:**

- **MigracaoConta**: Representa uma conta corrente em processo de migração
  - Atributos: cdMigracaoContaCorrente (PK), cdBanco, nuContaCorrente, cdTipoConta, cdAgencia, flAceiteMigracao, tpStatusMigracao, dtPrevistaMigracao, nuProtocoloIda, nuProtocoloVolta, vrMigrado, dsErro
  
- **MigracaoChavePix**: Representa uma migração de chave PIX associada a uma conta
  - Atributos: cdMigracaoContaCorrente (FK), cdBanco, nuContaCorrente, cdTipoConta, cdAgencia, flAceiteMigracao, tpStatusMigracao, dtPrevistaMigracao, vrSaldoMigrado, cpfCnpj, origem
  - Relacionamento: N:1 com MigracaoConta

- **ChavePix**: Representa uma chave PIX em processo de portabilidade
  - Atributos: cdMigracaoChavePix (PK), cdMigracaoContaCorrente (FK), cdChavePix, cdPortabilidadeChavePix, dsTipoChavePix, tpStatusPortabilidadeChavePix
  - Relacionamento: N:1 com MigracaoChavePix

- **StatusMigracao**: Agregação de informações de status de migração
  - Contém: dados da conta + lista de chaves PIX associadas
  - Relacionamento: 1:N com ChavePix

- **MigracaoBVIN**: Representa atualização de envelope de investimentos
  - Atributos: nuBanco, nuContaCorrente

**Enumerações:**
- AcaoEnum: SALVAR, CONFIRMAR, CONCLUIR, EXCLUIR
- StatusMigracaoEnum: INICIAL, NAO_ACEITO, ACEITO, EM_PORTABILIDADE, CONCLUIDO, EXCLUIDO, PROCESSANDO_DELETAR, PROCESSANDO_REIVINDICACAO, SEM_CHAVE
- StatusPortabilidadeChavePixEnum: NAO_PROCESSADO, SALVO, CONFIRMADO, CONCLUIDO, EXCLUIDO
- TipoChavePixEnum: CPF, CNPJ, PHONE, EMAIL, EVP
- OrigemRequisicaoEnum: APP, COCKPIT

### 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbMigracaoContaCorrente | tabela | SELECT | Consulta dados de migração de contas correntes (Sybase) |
| TbControleChavePIXMigracaoBVSA | tabela | SELECT | Consulta chaves PIX em processo de portabilidade (Sybase) |

### 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbMigracaoContaCorrente | tabela | INSERT | Insere nova migração de conta corrente (Sybase) |
| TbMigracaoContaCorrente | tabela | UPDATE | Atualiza status, aceite, protocolos e valores de migração (Sybase) |
| TbControleChavePIXMigracaoBVSA | tabela | INSERT | Insere nova chave PIX em portabilidade (Sybase) |
| TbControleChavePIXMigracaoBVSA | tabela | UPDATE | Atualiza status de portabilidade de chave PIX (Sybase) |
| TbEnvelopeInvestimento | tabela | UPDATE | Atualiza banco do envelope de investimentos (SQL Server - BVIN) |

### 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | leitura | /usr/etc/log | Configuração de logs da aplicação |
| application.yml | leitura | classpath | Configurações da aplicação (datasources, profiles, etc) |
| *.sql | leitura | classpath (resources) | Queries SQL utilizadas pelos repositórios JDBI |

### 10. Filas Lidas
não se aplica

### 11. Filas Geradas
não se aplica

### 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **Sybase DBCONTACORRENTE** | Banco de Dados | Banco principal com dados de contas correntes e chaves PIX (porta 7500/3050 conforme ambiente) |
| **SQL Server DBBINV1** | Banco de Dados | Banco de investimentos BVIN para atualização de envelopes (porta 17027/16027 conforme ambiente) |
| **OAuth2/JWT** | Autenticação | Serviço de autenticação para validação de tokens JWT (URLs variam por ambiente: des/uat/prd) |
| **Prometheus** | Observabilidade | Exportação de métricas da aplicação |
| **Grafana** | Observabilidade | Visualização de métricas e dashboards |

### 13. Avaliação da Qualidade do Código

**Nota: 7.5/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões hexagonais (ports/adapters)
- Separação clara de responsabilidades em módulos (common, domain, application)
- Uso adequado de DTOs e mapeadores para separar camadas
- Boa cobertura de testes unitários e de integração
- Tratamento centralizado de exceções
- Uso de enums para constantes e estados
- Configuração adequada de múltiplos datasources
- Implementação de observabilidade (Actuator, Prometheus, Grafana)
- Documentação OpenAPI/Swagger
- Uso de Lombok para reduzir boilerplate

**Pontos de Melhoria:**
- Alguns métodos com lógica complexa poderiam ser refatorados (ex: MigracaoChavePixServiceImpl)
- Uso de StringEscapeUtils para sanitização de logs poderia ser centralizado
- Alguns mappers com lógica duplicada
- Falta de validações de entrada em alguns endpoints
- Queries SQL em arquivos separados dificultam manutenção (poderia usar JPA/Hibernate)
- Alguns métodos com muitos parâmetros (ex: listarMigracaoChavePix com 7 parâmetros)
- Falta de documentação JavaDoc em algumas classes críticas
- Configurações hardcoded em alguns lugares (ex: "user" como dsLogin padrão)

### 14. Observações Relevantes

1. **Múltiplos Bancos de Dados**: Sistema integra com dois bancos distintos (Sybase e SQL Server), cada um com seu pool de conexões HikariCP
2. **Segurança**: Implementa autenticação OAuth2 com JWT, validando CPF/CNPJ do token para operações do App
3. **Ambientes**: Configurado para múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas
4. **Observabilidade**: Implementação completa de observabilidade com métricas customizadas, dashboards Grafana e integração Prometheus
5. **Auditoria**: Utiliza biblioteca específica do Banco Votorantim para trilha de auditoria
6. **Containerização**: Preparado para deploy em containers Docker/OpenShift no Google Cloud Platform
7. **Testes**: Estrutura completa de testes (unitários, integração, funcionais) com Pact para testes de contrato
8. **Versionamento**: Sistema em versão 0.9.0, indicando estar em fase de estabilização pré-release
9. **Data de Corte**: Queries filtram registros com dtInclusao >= 01/12/2021, indicando migração de dados históricos
10. **Pool de Conexões**: Configurações específicas de pool (minimum-idle, maximum-pool-size) para otimização de recursos

---