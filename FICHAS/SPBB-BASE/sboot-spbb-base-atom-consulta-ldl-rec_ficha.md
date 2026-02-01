# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema atômico de consulta e registro de mensagens LDL (Liquidação de Recebíveis de Cartão) no contexto do Sistema de Pagamentos Brasileiro (SPB). O sistema permite consultar mensagens SLC (Sistema de Liquidação de Cartões), LTR (Liquidação em Tempo Real) e LDL, além de registrar recusas SLC0002. Integra-se com bancos de dados Sybase (DBISPB e DBINTEGRACAOSPB) para leitura de movimentações financeiras e registro de operações.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal Spring Boot com configuração OAuth2 Resource Server |
| **ConsultaLdlRecConfiguration** | Configuração de beans de serviço e transações |
| **DatasourceConfig** | Configuração de dois datasources (SPB e BCO) |
| **JdbiConfig** | Configuração JDBI para acesso a dados com dois contextos |
| **CustomExceptionHandler** | Tratamento global de exceções (RuntimeException, DomainException) |
| **ConsultaLdlController** | Endpoint REST para consulta de LDL (SLC0001) |
| **ConsultaLtrController** | Endpoint REST para consulta de LTR por data de movimento |
| **ConsultaSlcController** | Endpoints REST para consulta de SLC0005 e SLC0001BL |
| **RegistroSlcController** | Endpoint REST para registro de SLC0002 (recusas) |
| **ConsultaLdlService** | Serviço de domínio para consulta SLC0001 |
| **ConsultaLtrService** | Serviço de domínio para consulta LTR |
| **ConsultaSlcService** | Serviço de domínio para consulta SLC |
| **RegistraSlcService** | Serviço de domínio para processamento de recusas SLC0002 |
| **JdbiConsultaLdlRepository** | Repositório JDBI para consultas LDL |
| **JdbiConsultaLtrRepository** | Repositório JDBI para consultas LTR |
| **JdbiConsultaSlcRepository** | Repositório JDBI para consultas SLC |
| **JdbiIntegracaoSpbRepository** | Repositório JDBI para integração SPB (registro SLC0002) |
| **Mappers (diversos)** | Conversão entre entidades de domínio e representações REST |
| **RowMappers (diversos)** | Mapeamento de ResultSet JDBC para objetos de domínio |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.x** (framework base)
- **Spring Security OAuth2** (autenticação/autorização)
- **JDBI 3.9.1** (acesso a dados)
- **Sybase jConnect 16.3** (driver JDBC)
- **Swagger/OpenAPI 2.0** (documentação de API)
- **Springfox 3.0.0** (geração de documentação Swagger)
- **Micrometer + Prometheus** (métricas)
- **Logback** (logging)
- **Lombok** (redução de boilerplate)
- **Maven** (build)
- **Docker** (containerização)
- **Grafana** (visualização de métricas)
- **JUnit 5 + Mockito** (testes)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/consultar-ldl/{dtRecebimento}` | ConsultaLdlController | Retorna LDL definitivas (SLC0001) para data de recebimento |
| GET | `/v1/consultar-ltr/{dtMovimento}` | ConsultaLtrController | Retorna LTR recebidas para data de movimento |
| GET | `/v1/consultar-slc/{dtMovimento}` | ConsultaSlcController | Retorna SLC0005 para data de movimento |
| GET | `/v1/consultar-slc/0001BL` | ConsultaSlcController | Retorna SLC0001BL por data, ciclo e tipo de processamento |
| POST | `/v1/registra-slc/0002BL` | RegistroSlcController | Registra recusas SLC0002 |

---

## 5. Principais Regras de Negócio

1. **Consulta LDL (SLC0001)**: Retorna apenas transações definitivas (tipo 'D'), com valor > 0, dos tipos 02 ou 03, sem código de produto, para o ISPB do Banco Votorantim
2. **Consulta LTR**: Filtra apenas operações de subtipo 'ANTR' (Antecipação de Recebíveis)
3. **Consulta SLC0005**: Retorna apenas operações de subtipo 'ANTR'
4. **Consulta SLC0001BL**: Filtra por data de movimento, ciclo de liquidação (1 ou 2) e tipo de processamento (P-Prévia ou D-Definitiva)
5. **Registro SLC0002**: 
   - Obtém próximo código de operação SLC
   - Registra cada linha de identificação com tipo de divergência
   - Integra a operação via stored procedure
   - Valida status de processamento (O-OK ou W-Atualizado)
6. **Sanitização de logs**: Remove caracteres especiais e espaços para prevenir log injection
7. **Extração de usuário**: Obtém login do header HTTP "loginUsuarioFinal"

---

## 6. Relação entre Entidades

**Entidades de Domínio:**

- **SLC0001**: Representa mensagem SLC bilateral com dados de liquidação (ISPB credor/devedor, valores, CNPJs, ciclo)
- **SLC0001BL**: Variante de SLC0001 com informações de processamento bilateral
- **SLC**: Mensagem SLC0005 com dados de liquidação e ativos
- **LTR**: Mensagem de Liquidação em Tempo Real com dados de operação, participantes e confirmação
- **SLC0002Request**: Request para registro de recusas (lista de identificações, tipo de divergência, número de controle)
- **RetornoSLC0002DTO**: Resposta do processamento de recusas (status e descrição)

**Relacionamentos:**
- SLC0001 e SLC0001BL são variações da mesma mensagem bilateral
- LTR e SLC representam diferentes tipos de mensagens do SPB
- SLC0002Request é usado para registrar divergências relacionadas a mensagens SLC

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| tb_movi_movimento | tabela | SELECT | Tabela de movimentos do SPB |
| tb_mvsc_movimento_slc | tabela | SELECT | Tabela de movimentos SLC com detalhes de mensagens |
| tb_mvlr_movimento_ltr | tabela | SELECT | Tabela de movimentos LTR |
| TbIntegracaoSLC | tabela | SELECT | Tabela de controle de integração SLC |
| TbRegistroSLC0002 | tabela | SELECT | Tabela de registros SLC0002 para obter próximo código |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbRegistroSLC0002 | tabela | INSERT | Inserção via stored procedure sp_In_RegistroSLC0002 |
| TbIntegracaoSLC | tabela | INSERT | Inserção via stored procedure prIncluirIntegracaoSLC |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | leitura | Application (via Spring Boot) | Configuração de logging em JSON |
| application.yml | leitura | Application (via Spring Boot) | Configurações da aplicação por perfil |
| consulta-ldl-rec-contract.yaml | leitura | Swagger Codegen Plugin | Contrato OpenAPI para geração de interfaces |
| *.sql | leitura | JDBI (via @UseClasspathSqlLocator) | Queries SQL externalizadas |

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
| DBISPB (Sybase) | Banco de dados | Banco de dados do SPB com tabelas de movimentos SLC e LTR |
| DBINTEGRACAOSPB (Sybase) | Banco de dados | Banco de dados de integração SPB para registro de SLC0002 |
| API Gateway OAuth2 | Serviço de autenticação | Validação de tokens JWT via JWK endpoint |
| Prometheus | Serviço de métricas | Exportação de métricas da aplicação |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura hexagonal bem definida (domain/application/infrastructure)
- Separação clara de responsabilidades entre camadas
- Uso de JDBI com queries SQL externalizadas
- Configuração adequada de múltiplos datasources
- Tratamento de exceções centralizado
- Uso de DTOs e mappers para isolamento de camadas
- Documentação OpenAPI completa
- Configuração de métricas e observabilidade

**Pontos de Melhoria:**
- Falta de tratamento específico de exceções de banco de dados
- Sanitização de logs básica (poderia usar biblioteca especializada)
- Alguns mappers com lógica repetitiva
- Falta de validação de entrada em alguns endpoints
- Comentários em código escassos
- Alguns nomes de variáveis poderiam ser mais descritivos (ex: "slc", "ltr")
- Falta de testes unitários nos arquivos enviados
- Uso de `@SuppressWarnings("java:S1874")` sem justificativa clara
- Configurações de segurança desabilitadas em ambientes de desenvolvimento

---

## 14. Observações Relevantes

1. **Segurança**: O sistema desabilita segurança OAuth2 em ambientes local e des, o que é adequado para desenvolvimento mas deve ser monitorado
2. **Múltiplos Datasources**: Configuração de dois datasources (SPB e BCO) com JDBI separados, permitindo acesso a diferentes bases
3. **Stored Procedures**: Utiliza stored procedures Sybase para operações de escrita (sp_In_RegistroSLC0002, prIncluirIntegracaoSLC)
4. **Versionamento de API**: Usa prefixo `/v1` nos endpoints
5. **Métricas**: Configuração completa de Prometheus + Grafana para monitoramento
6. **Containerização**: Dockerfile baseado em imagem Java 11 do repositório interno do banco
7. **Infraestrutura como Código**: Arquivo infra.yml com configurações para múltiplos ambientes (des/qa/uat/prd)
8. **Padrão de Nomenclatura**: Segue convenções do SPB para tipos de mensagens (SLC, LTR, LDL)
9. **Auditoria**: Integração com biblioteca de trilha de auditoria do BV (bv-arqt-base-trilha-auditoria-web)
10. **Encoding**: Uso de charset ISO-1 nas conexões Sybase