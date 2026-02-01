# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-spag-base-atom-bloqueio-conta** é um serviço atômico desenvolvido em Java com Spring Boot para gerenciar ordens judiciais relacionadas a bloqueio e desbloqueio de contas bancárias. O sistema atua como intermediário entre o Bacen BJUD (Banco Central - Sistema de Bloqueio Judicial) e os parceiros fintechs do Banco Votorantim, permitindo consultar, inserir e atualizar informações sobre ordens judiciais, além de gerar relatórios e resumos de processamento.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal que inicializa a aplicação Spring Boot |
| **OrdemJudicialController** | Controlador REST que expõe endpoints para consulta, inserção e atualização de ordens judiciais |
| **OrdemJudicialService** | Serviço de domínio que implementa a lógica de negócio para ordens judiciais |
| **BloqueioContaService** | Serviço de domínio para processamento de bloqueios e geração de resumos |
| **OrdemJudicialRepositoryImpl** | Implementação do repositório para acesso aos dados de ordens judiciais (JDBI) |
| **BloqueioContaRepositoryImpl** | Implementação do repositório para acesso aos dados de bloqueio de contas (JDBI) |
| **OrdemJudicial** | Entidade de domínio representando uma ordem judicial |
| **OrdemJudicialMapper** | Responsável por conversões entre entidades de domínio e representações REST |
| **DBConfiguration** | Configuração de múltiplos datasources (DBSPAG e DBSPAG2) |
| **JdbiConfiguration** | Configuração do framework JDBI para acesso a banco de dados |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Spring Security OAuth2** (autenticação e autorização via JWT)
- **JDBI 3.9.1** (framework de acesso a dados)
- **Microsoft SQL Server** (banco de dados)
- **Swagger/OpenAPI 3.0** (documentação de APIs)
- **Springfox 3.0.0** (geração de documentação Swagger)
- **Micrometer + Prometheus** (métricas e monitoramento)
- **Spring Actuator** (health checks e métricas)
- **Logback** (logging com formato JSON)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Grafana** (visualização de métricas)
- **Lombok** (redução de boilerplate)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/ordem-judicial` | OrdemJudicialController | Consulta ordens judiciais por período e documentos |
| POST | `/v1/ordem-judicial` | OrdemJudicialController | Insere uma nova ordem judicial |
| PUT | `/v1/atualizar-ordem-judicial` | OrdemJudicialController | Atualiza dados de uma ordem judicial (endereço e saldo) |
| GET | `/v1/registros-sem-endereco` | OrdemJudicialController | Retorna registros sem endereço cadastrado |
| GET | `/v1/bloqueio-conta/resumo-bloqueio-dia` | OrdemJudicialController | Retorna resumo de bloqueios e processamentos do dia |
| GET | `/v1/bloqueio-conta/resumo-erro-processamento-parceiro` | OrdemJudicialController | Retorna erros de processamento dos parceiros |
| GET | `/v1/bloqueio-conta/resumo-ordens-naoTrabalhadas` | OrdemJudicialController | Retorna ordens judiciais não processadas |

---

## 5. Principais Regras de Negócio

1. **Consulta de Ordens Judiciais**: Permite filtrar ordens por período (data inicial e final) e opcionalmente por lista de documentos (CPF/CNPJ)
2. **Inserção de Ordens**: Valida e persiste novas ordens judiciais recebidas do Bacen BJUD
3. **Atualização de Endereços**: Permite complementar informações de endereço e saldo de contas para ordens já cadastradas
4. **Geração de Resumos**: Consolida informações de bloqueios realizados, processamentos e erros por parceiro fintech
5. **Identificação de Ordens Não Trabalhadas**: Lista ordens recebidas mas ainda não processadas pelos parceiros
6. **Validação de Protocolos**: Verifica se um protocolo já foi processado em determinado período
7. **Mascaramento de Dados Sensíveis**: Aplica mascaramento em CPF/CNPJ e nomes de clientes pessoa física nos relatórios

---

## 6. Relação entre Entidades

**OrdemJudicial** (entidade principal):
- Contém dados da ordem judicial (protocolo, tipo de solicitação, valores, datas)
- Relaciona-se com dados do cliente fintech (CPF/CNPJ, nome, conta)
- Relaciona-se com dados da fintech parceira (razão social, documento)
- Contém informações de endereço (logradouro, número, complemento, bairro, cidade, estado, CEP, país)
- Possui informações de auditoria (data inclusão, alteração, login, flag ativo)

**SolicitacaoRegistro**:
- Representa registros que necessitam complementação de dados
- Relaciona-se com OrdemJudicial através do ID

**ResumoBloqueioDia**:
- Agregação de dados de bloqueios por fintech, CPF/CNPJ e protocolo

**ResumoProcessamentoDia**:
- Agregação de status de processamento (processado, a processar)

**ErroProcessamentoParceiro**:
- Detalhamento de erros ocorridos no processamento por parceiro

**OrdemNaoTrabalhada**:
- Ordens recebidas mas não processadas pelos parceiros

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbProcessoJuridico | tabela | SELECT | Dados dos processos judiciais |
| TbSolicitacaoJuridico | tabela | SELECT | Solicitações de bloqueio/desbloqueio |
| TbProcessamentoMovimentoJuridico | tabela | SELECT | Histórico de processamentos de movimentações |
| TbTipoSolicitacaoJuridico | tabela | SELECT | Tipos de solicitação (bloqueio, desbloqueio, etc) |
| TbContaUsuarioFintech | tabela | SELECT | Contas de usuários nas fintechs |
| TbParametroPagamentoFintech | tabela | SELECT | Parâmetros das fintechs parceiras |
| TbUsuarioContaFintech | tabela | SELECT | Usuários vinculados às contas |
| TbStatusContaFintech | tabela | SELECT | Status das contas (ativo, inativo, etc) |
| spagBloqueioConta.TbControleBloqueioConta | tabela | SELECT | Tabela de controle de ordens judiciais |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| spagBloqueioConta.TbControleBloqueioConta | tabela | INSERT | Inserção de novas ordens judiciais |
| spagBloqueioConta.TbControleBloqueioConta | tabela | UPDATE | Atualização de endereço e saldo de ordens existentes |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | leitura | /usr/etc/log (produção) | Configuração de logs da aplicação |
| application.yml | leitura | resources | Configurações da aplicação por ambiente |
| *.sql | leitura | resources/br/com/.../database/ | Queries SQL utilizadas pelo JDBI |
| sboot-spag-base-atom-bloqueio-conta.yml | leitura | resources/swagger/ | Especificação OpenAPI dos endpoints |

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
| API Gateway BV | REST/OAuth2 | Autenticação e autorização via JWT (jwks.json) |
| DBSPAG (SQL Server) | JDBC | Banco de dados principal do SPAG com dados de bloqueios |
| DBSPAG2 (SQL Server) | JDBC | Banco de dados secundário com controle de ordens judiciais |
| Prometheus | HTTP | Exportação de métricas da aplicação |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões de Clean Architecture (domain, application, infrastructure)
- Uso adequado de injeção de dependências e inversão de controle
- Separação clara de responsabilidades entre camadas
- Uso de Lombok para reduzir boilerplate
- Documentação OpenAPI bem definida
- Configuração adequada de múltiplos ambientes
- Uso de Optional para tratamento de valores nulos
- Implementação de health checks e métricas

**Pontos de Melhoria:**
- Queries SQL muito extensas e complexas embutidas em annotations (deveriam estar em arquivos .sql separados)
- Falta de tratamento de exceções mais específico em alguns pontos
- Logs de erro sem contexto suficiente em alguns casos
- Uso de `@SuppressWarnings("java:S1874")` sem justificativa clara
- Algumas classes de mapper com lógica de negócio misturada (ex: ErroProcessamentoParceiroRowMapper)
- Falta de testes unitários para validar regras críticas
- Comentários em português misturados com código em inglês
- Algumas queries SQL poderiam ser otimizadas (uso excessivo de subqueries)

---

## 14. Observações Relevantes

1. **Múltiplos Datasources**: O sistema trabalha com dois bancos de dados distintos (DBSPAG e DBSPAG2), sendo necessário atenção na configuração de transações
2. **Segurança**: Implementa mascaramento de dados sensíveis (CPF/CNPJ e nomes) para pessoas físicas nos relatórios
3. **Performance**: Algumas queries são muito complexas e podem impactar performance em grandes volumes
4. **Auditoria**: Integrado com biblioteca de trilha de auditoria do Banco Votorantim
5. **Ambientes**: Configurado para múltiplos ambientes (local, des, qa, uat, prd) com diferentes datasources
6. **Monitoramento**: Bem instrumentado com Prometheus e Grafana para observabilidade
7. **Containerização**: Preparado para deploy em containers Docker/Kubernetes (OpenShift)
8. **Versionamento**: Sistema versionado (0.14.0) seguindo padrões do Banco Votorantim