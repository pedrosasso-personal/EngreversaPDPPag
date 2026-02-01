# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de gerenciamento de operações do SPB (Sistema de Pagamentos Brasileiro) para o ISPB (Identificador do Sistema de Pagamentos Brasileiro). O sistema fornece APIs REST para consulta, envio e gerenciamento de operações bancárias relacionadas ao SPB, incluindo histórico de operações, console de operações, agenda de operações e manuais de operações. Atua como backend para interfaces de gestão de mensagens e operações do sistema financeiro.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal Spring Boot que inicializa a aplicação |
| **AppConfiguration** | Configuração de beans da aplicação (services, mappers, converters JSON) |
| **JdbiConfiguration** | Configuração do JDBI para acesso a banco de dados |
| **HistoricoOperacoesService** | Lógica de negócio para consulta de histórico de operações por tipo de serviço |
| **EnviarOperacoesService** | Lógica para envio e validação de operações |
| **AgendaOperacaoService** | Gerenciamento de agenda de operações |
| **ConsoleOperacoesService** | Consultas do console de operações |
| **ManualOperacoesService** | Consulta de manuais de operações |
| **PopUpConsoleService** | Validações de popup do console |
| **GlobalExceptionHandler** | Tratamento centralizado de exceções |
| **RegraNegocioException** | Exceção customizada para regras de negócio |
| **Repositories (JDBI)** | Interfaces de acesso a dados usando JDBI |
| **Mappers (MapStruct)** | Conversão entre Domain e DTOs |
| **Delegates** | Implementação dos endpoints REST (padrão delegate) |

## 3. Tecnologias Utilizadas

- **Spring Boot 2.7.7** - Framework principal
- **Java 11** - Linguagem de programação
- **JDBI 3.9.1** - Framework de acesso a banco de dados
- **MapStruct** - Mapeamento de objetos
- **Sybase jConnect 16.3** - Driver de banco de dados Sybase
- **Lombok** - Redução de boilerplate
- **Spring Security OAuth2** - Segurança e autenticação JWT
- **Swagger/OpenAPI 3.0** - Documentação de APIs
- **Logback** - Logging em formato JSON
- **Maven** - Gerenciamento de dependências
- **Docker** - Containerização
- **JUnit 5 + Mockito** - Testes unitários
- **Atlante Base** - Biblioteca corporativa de auditoria

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | /historico-operacoes/{moviId}/{serv} | HistoricoOperacoesDelegateImpl | Busca histórico de operações por movimento e serviço |
| GET | /enviar-operacoes/busca-msbcid/{operId} | EnviarOperacoesDelegateImpl | Busca mensagem BACEN por operação |
| GET | /enviar-operacoes/retorna-data/{holdId} | EnviarOperacoesDelegateImpl | Retorna data de movimento |
| GET | /enviar-operacoes/retorna-resp | EnviarOperacoesDelegateImpl | Valida existência de LAOP/LAME |
| GET | /enviar-operacoes/busca-inst | EnviarOperacoesDelegateImpl | Busca instituições |
| GET | /enviar-operacoes/busca-bacen/{usuaId} | EnviarOperacoesDelegateImpl | Busca mensagens BACEN por usuário |
| GET | /enviar-operacoes/busca-mensagem/{usuaId} | EnviarOperacoesDelegateImpl | Busca mensagens por usuário |
| GET | /enviar-operacoes/busca-grms/{usuaId} | EnviarOperacoesDelegateImpl | Busca grupos de mensagem por usuário |
| GET | /agenda-operacao/pmge | AgendaOperacaoDelegateImpl | Lista parâmetros gerais |
| GET | /agenda-operacao/busca-msbcid/{operId} | AgendaOperacaoDelegateImpl | Busca mensagem por operação |
| GET | /agenda-operacao/busca-by-msbcid/{msbcId} | AgendaOperacaoDelegateImpl | Busca por código de mensagem |
| GET | /agenda-operacao/data-maxima | AgendaOperacaoDelegateImpl | Busca data máxima de movimento |
| GET | /console-operacoes/pmge | ConsoleOperacoesDelegateImpl | Lista parâmetros gerais |
| GET | /console-operacoes/data-maxima | ConsoleOperacoesDelegateImpl | Busca data máxima |
| GET | /console-operacoes/{flIdaVolta}/{data}/{holdId}/{instId}/{nrLinhas} | ConsoleOperacoesDelegateImpl | Busca operações por filtros |
| GET | /popup-console/retorna-resp | PopUpConsoleDelegateImpl | Valida resposta de popup |
| GET | /manual-operacoes/manual-operacoes | ManualOperacoesDelegateImpl | Lista manual de operações |
| GET | /manual-operacoes/manual-operacoes-retorno | ManualOperacoesDelegateImpl | Lista manual de retorno |

## 5. Principais Regras de Negócio

- **Validação de Operações**: Verifica existência de layouts de operação (LAOP) e mensagem (LAME) antes de permitir envio
- **Filtragem por Tipo de Serviço**: Histórico de operações é buscado dinamicamente conforme tipo de serviço (BMC, CBL, CIR, CTP, GEN, LDL, LTR, PAG, RCO, RDC, SEL, SLB, STN, TES, STR)
- **Controle de Acesso por Usuário**: Mensagens e operações são filtradas por perfil de usuário (usuaId)
- **Paginação de Console**: Busca de operações no console com controle de número de linhas e direção (ida/volta)
- **Filtragem por Emissor**: Operações filtradas por tipo de emissor (IF, OII, ACT, AGD, INT)
- **Exclusão de Grupos**: Grupos de mensagem 1 e 24 são excluídos das consultas
- **Data de Movimento**: Sistema trabalha com data de movimento atual, anterior e posterior
- **Validação de Obrigatoriedade**: Campos obrigatórios são validados no manual de operações

## 6. Relação entre Entidades

**Principais entidades do domínio:**

- **tb_movi_movimento**: Tabela central de movimentos, relaciona-se com todas as operações
- **tb_oper_operacao**: Operações disponíveis, relaciona-se com tb_msbc_mensagem_bacen
- **tb_msbc_mensagem_bacen**: Mensagens do BACEN, relaciona-se com grupos e subgrupos
- **tb_inst_instituicao**: Instituições financeiras, relaciona-se com holdings
- **tb_stop_situacao_operacao**: Situações das operações
- **tb_grms_grupo_mensagem**: Grupos de mensagens
- **tb_sgms_subgrupo_mensagem**: Subgrupos de mensagens
- **tb_laop_layout_operacao**: Layout de operações (estrutura de campos)
- **tb_lame_layout_mensagem**: Layout de mensagens (estrutura de campos)
- **tb_pmge_parametro_geral**: Parâmetros gerais do sistema
- **tb_usua_usuario**: Usuários do sistema
- **tb_asop_acesso_operacao**: Controle de acesso às operações

**Relacionamentos:**
- Movimento (1) -> (N) Operações específicas (mvbc, mvcl, mvcr, etc.)
- Operação (N) -> (1) Mensagem BACEN
- Mensagem BACEN (N) -> (1) Grupo de Mensagem
- Mensagem BACEN (N) -> (1) Subgrupo de Mensagem
- Usuário (N) -> (N) Operações (via tb_asop_acesso_operacao)

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View | Tipo | Operação | Breve Descrição |
|---------------------|------|----------|-----------------|
| tb_movi_movimento | tabela | SELECT | Movimentos do sistema SPB |
| tb_oper_operacao | tabela | SELECT | Operações disponíveis |
| tb_msbc_mensagem_bacen | tabela | SELECT | Mensagens do BACEN |
| tb_inst_instituicao | tabela | SELECT | Instituições financeiras |
| tb_stop_situacao_operacao | tabela | SELECT | Situações das operações |
| tb_grms_grupo_mensagem | tabela | SELECT | Grupos de mensagens |
| tb_sgms_subgrupo_mensagem | tabela | SELECT | Subgrupos de mensagens |
| tb_laop_layout_operacao | tabela | SELECT | Layout de operações |
| tb_lame_layout_mensagem | tabela | SELECT | Layout de mensagens |
| tb_pmge_parametro_geral | tabela | SELECT | Parâmetros gerais |
| tb_usua_usuario | tabela | SELECT | Usuários do sistema |
| tb_asop_acesso_operacao | tabela | SELECT | Controle de acesso |
| tb_mvbc_movimento_bmc | tabela | SELECT | Movimentos BMC |
| tb_mvcl_movimento_cbl | tabela | SELECT | Movimentos CBL |
| tb_mvcr_movimento_cir | tabela | SELECT | Movimentos CIR |
| tb_mvcp_movimento_ctp | tabela | SELECT | Movimentos CTP |
| tb_mvgn_movimento_gen | tabela | SELECT | Movimentos GEN |
| tb_mvld_movimento_ldl | tabela | SELECT | Movimentos LDL |
| tb_mvlr_movimento_ltr | tabela | SELECT | Movimentos LTR |
| tb_mvpg_movimento_pag | tabela | SELECT | Movimentos PAG |
| tb_mvro_movimento_rco | tabela | SELECT | Movimentos RCO |
| tb_mvrd_movimento_rdc | tabela | SELECT | Movimentos RDC |
| tb_mvse_movimento_sel | tabela | SELECT | Movimentos SEL |
| tb_mvsb_movimento_slb | tabela | SELECT | Movimentos SLB |
| tb_mvsn_movimento_stn | tabela | SELECT | Movimentos STN |
| tb_mvts_movimento_tes | tabela | SELECT | Movimentos TES |
| tb_mvsr_movimento_str | tabela | SELECT | Movimentos STR |

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | leitura | Configuração Logback | Configuração de logs em JSON |
| application.yml | leitura | Spring Boot | Configurações da aplicação |
| application-local.yml | leitura | Spring Boot | Configurações para ambiente local |
| openapi.yaml | leitura | Swagger | Especificação OpenAPI das APIs |
| *.sql | leitura | JDBI Repositories | Queries SQL para acesso a dados |

## 10. Filas Lidas

não se aplica

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

- **API Gateway BV**: Autenticação e autorização via JWT (JWKS endpoint)
- **Banco de Dados Sybase**: Acesso ao DBISPB para consultas e operações
- **Atlante Base**: Biblioteca corporativa para auditoria e trilha

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades (camadas bem definidas: rest, service, repository, domain, mapper)
- Uso adequado de padrões como Delegate, Repository e Mapper
- Testes unitários implementados para as principais classes
- Configuração adequada de segurança e logging
- Uso de bibliotecas modernas (JDBI, MapStruct, Lombok)
- Documentação OpenAPI completa

**Pontos de Melhoria:**
- Código com muita repetição no HistoricoOperacoesService (switch case extenso poderia usar Strategy Pattern)
- Queries SQL embutidas em arquivos separados, mas com lógica complexa e comentários em português
- Falta de validação de entrada em alguns endpoints
- Uso de `allNotNull` de forma inconsistente (às vezes verifica, às vezes não)
- Alguns métodos retornam objetos vazios em vez de Optional
- Falta de documentação JavaDoc nas classes
- Tratamento de exceções genérico em alguns pontos
- Uso de `*=` (outer join) em queries Sybase que pode ser confuso

## 14. Observações Relevantes

- Sistema legado migrado para Spring Boot, mantendo estrutura de banco Sybase
- Utiliza JDBI em vez de JPA/Hibernate, provavelmente por questões de performance e queries complexas
- Configurações específicas para múltiplos ambientes (local, des, qa, uat, prd)
- Sistema crítico para operações bancárias do SPB
- Autenticação via JWT com integração ao API Gateway corporativo
- Logs estruturados em JSON para facilitar análise
- Deployment em Google Cloud Platform (GKE)
- Probes de liveness e readiness configurados para Kubernetes
- Sistema stateful conforme documentação
- Utiliza padrão de nomenclatura corporativo (sboot-spbb-base-atom-*)