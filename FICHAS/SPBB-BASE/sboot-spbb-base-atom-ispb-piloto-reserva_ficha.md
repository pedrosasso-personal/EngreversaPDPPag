# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-spbb-base-atom-ispb-piloto-reserva** é um serviço atômico Spring Boot desenvolvido para gerenciar operações relacionadas ao piloto de reservas bancárias no contexto do Sistema de Pagamentos Brasileiro (SPB). O sistema oferece funcionalidades para controle de reservas, liquidação de câmaras, ajustes, consultas, parâmetros automáticos, compulsório à vista e envio de pendências. Atua como uma API REST stateful que integra com banco de dados Sybase e expõe diversos endpoints para operações financeiras e de controle.

---

## 2. Principais Classes e Responsabilidades

| Classe/Componente | Responsabilidade |
|-------------------|------------------|
| `Application.java` | Classe principal de inicialização da aplicação Spring Boot com configuração de segurança JWT |
| `AppConfiguration.java` | Configuração de beans da aplicação, incluindo mappers, services e conversores HTTP |
| `JdbiConfiguration.java` | Configuração do JDBI para acesso ao banco de dados Sybase |
| `GlobalExceptionHandler.java` | Tratamento centralizado de exceções da aplicação |
| `BusinessException.java` | Exceção customizada para erros de negócio |
| `RegraNegocioException.java` | Exceção específica para violações de regras de negócio |
| `WaitUtil.java` | Utilitário para pausas/delays em processamentos |
| Services (diversos) | `EnviaPendentesService`, `MudancaHorarioService`, `PilotoReservaService`, `AjusteReservaService`, `ParametrosAutomaticosService`, `CompulsorioAvistaService`, `IncluirExcecaoService`, `ConsultaReservaService` - implementam lógica de negócio |
| Repositories (diversos) | Interfaces JDBI para acesso aos dados |
| Mappers (diversos) | Conversão entre DTOs e entidades de domínio usando MapStruct |

---

## 3. Tecnologias Utilizadas

- **Framework**: Spring Boot 2.6.0 (baseado no parent POM)
- **Linguagem**: Java 11
- **Persistência**: JDBI 3.9.1
- **Banco de Dados**: Sybase jConnect 16.3-SP03-PL07
- **Segurança**: Spring Security OAuth2 Resource Server com JWT
- **Documentação API**: OpenAPI 3.0 / Swagger
- **Mapeamento**: MapStruct (via Lombok)
- **Logging**: Logback com formato JSON
- **Build**: Maven 3.8+
- **Containerização**: Docker
- **Infraestrutura**: Google Cloud Platform (GCP)
- **CI/CD**: Jenkins
- **Monitoramento**: Spring Actuator com Prometheus

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/piloto/reserva/envia-pendentes/busca-data` | EnviaPendentesController | Retorna data e hora do sistema (sp_se_pmge_hora_sistema_228) |
| GET | `/v1/piloto/reserva/envia-pendentes/busca-instituicao` | EnviaPendentesController | Busca instituições (sp_se_inst_051) |
| GET | `/v1/piloto/reserva/envia-pendentes/{holdId}/{instId}` | EnviaPendentesController | Busca operações (sp_se_oper_232) |
| GET | `/v1/piloto/reserva/mudanca-horario/validar` | MudancaHorarioController | Valida mudança de horário |
| GET | `/v1/piloto/reserva/ajuste-reserva/{holdId}/{instId}` | AjusteReservaController | Retorna valores de reserva (sp_se_rese_001) |
| POST | `/v1/piloto/reserva/ajuste-reserva/inserir` | AjusteReservaController | Insere ajuste de reserva (sp_in_ajre_001) |
| PUT | `/v1/piloto/reserva/ajuste-reserva/atualiza-valores` | AjusteReservaController | Atualiza saldos (sp_up_rese_001) |
| GET | `/v1/piloto/reserva/piloto-reserva/verifica-certificado` | PilotoReservaController | Verifica certificado digital |
| GET | `/v1/piloto/reserva/piloto-reserva/carregar-liquidacao-camaras` | PilotoReservaController | Carrega liquidação de câmaras |
| PUT | `/v1/piloto/reserva/piloto-reserva/movimento/prio/atualizar` | PilotoReservaController | Atualiza prioridade de movimento (sp_up_movi_032) |
| PUT | `/v1/piloto/reserva/piloto-reserva/movimento/stop/atualizar` | PilotoReservaController | Atualiza status stop de movimento (sp_up_movi_022) |
| GET | `/v1/piloto/reserva/parametros-automaticos/tipo-reserva` | ParametrosAutomaticosController | Retorna tipos de reserva (sp_se_tpre_071) |
| POST | `/v1/piloto/reserva/parametros-automaticos/insere/piloto-auto` | ParametrosAutomaticosController | Insere piloto automático (sp_in_ctpa_028) |
| GET | `/v1/piloto/reserva/compulsorio-avista/gerar-extrato` | CompulsorioAvistaController | Gera extrato de compulsório à vista |
| POST | `/v1/piloto/reserva/compulsorio-avista/calculo-compulsorio-avista` | CompulsorioAvistaController | Calcula compulsório à vista |
| PUT | `/v1/piloto/reserva/incluir-excecao/atualizar` | IncluirExcecaoController | Atualiza parâmetro de controle de envio (sp_up_pmce) |
| GET | `/v1/piloto/reserva/consulta-reserva/verifica-ciclo` | ConsultaReservaController | Verifica ciclo (sp_ge_verifica_ciclo_014) |
| POST | `/v1/piloto/reserva/consulta-reserva/registrar-movimento-mvsr` | ConsultaReservaController | Registra movimento MVSR |

---

## 5. Principais Regras de Negócio

1. **Controle de Reservas Bancárias**: Gerenciamento de saldos de reserva bancária com validações de valores mínimos e máximos
2. **Liquidação de Câmaras**: Processamento de liquidações de diferentes câmaras (LDL, RCO) com controle de horários e prazos
3. **Circuit Breaker**: Implementação de mecanismo de circuit breaker para controle de situações de reserva
4. **Piloto Automático**: Sistema de parametrização automática baseado em horários, valores e ciclos de operação
5. **Compulsório à Vista**: Cálculo de exigibilidade de depósitos compulsórios com base em períodos e médias
6. **Controle de Prioridades**: Gerenciamento de prioridades de movimentos financeiros (PRIO)
7. **Validação de Horários**: Verificação de janelas de operação e horários de abertura/fechamento de câmaras
8. **Ajustes de Reserva**: Processo de ajuste com autorização e justificativa, incluindo notificação por email
9. **Controle de Montante**: Monitoramento de limites e alertas de controle de envio de mensagens
10. **Gestão de Exceções**: Tratamento diferenciado para operações que requerem exceções de parâmetros

---

## 6. Relação entre Entidades

O sistema trabalha com as seguintes entidades principais e seus relacionamentos:

- **Instituição (INST)**: Representa instituições financeiras (holdId, instId)
- **Movimento (MOVI)**: Movimentações financeiras relacionadas a instituições
- **Reserva (RESE)**: Saldos de reserva associados a instituições
- **Operação (OPER)**: Tipos de operações financeiras
- **Mensagem Bacen (MSBC)**: Mensagens do sistema SPB
- **Câmara (CAM)**: Câmaras de liquidação (LDL, RCO)
- **Piloto Automático (CTPA)**: Parâmetros de controle automático
- **Ajuste Reserva (AJRE)**: Registros de ajustes manuais
- **Compulsório (MVRO)**: Dados de compulsório à vista
- **Fluxo Movimento (FLMV)**: Controle de fluxo de movimentos

**Relacionamentos principais**:
- Instituição 1:N Movimento
- Instituição 1:1 Reserva
- Movimento N:1 Operação
- Movimento N:1 Câmara
- Instituição 1:N Piloto Automático
- Movimento 1:N Fluxo Movimento

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| PMGE (Parâmetros Gerais) | Tabela | SELECT | Busca data/hora do sistema e parâmetros gerais |
| INST (Instituição) | Tabela | SELECT | Consulta dados de instituições financeiras |
| MOVI (Movimento) | Tabela | SELECT | Consulta movimentos financeiros |
| RESE (Reserva) | Tabela | SELECT | Consulta saldos de reserva |
| OPER (Operação) | Tabela | SELECT | Consulta tipos de operações |
| MSBC (Mensagem Bacen) | Tabela | SELECT | Consulta mensagens do Bacen |
| TPRE (Tipo Reserva) | Tabela | SELECT | Consulta tipos de reserva |
| STRE (Situação Reserva) | Tabela | SELECT | Consulta situações de reserva |
| CTPA (Controle Piloto Automático) | Tabela | SELECT | Consulta parâmetros de piloto automático |
| CTPM (Controle Piloto Mensagem) | Tabela | SELECT | Consulta mensagens do piloto |
| MVLD (Movimento LDL) | Tabela | SELECT | Consulta movimentos de liquidação LDL |
| MVRO (Movimento RCO) | Tabela | SELECT | Consulta movimentos de compulsório |
| LAOP (Layout Operação) | Tabela | SELECT | Consulta layouts de operações |
| GDEV (Grade Evento) | Tabela | SELECT | Consulta grades de eventos/horários |
| INNL (Instituição Limite) | Tabela | SELECT | Consulta limites de instituições |
| PEPO (Previsão Provisão) | Tabela | SELECT | Consulta previsões e provisões |
| VW_PILOTO_RESERVA_082 | View | SELECT | View consolidada de piloto reserva |
| VW_PILOTO_RESERVA_086 | View | SELECT | View consolidada de piloto reserva |
| PMCE (Parâmetro Controle Envio) | Tabela | SELECT | Consulta parâmetros de controle de envio |
| GRMS (Grupo Mensagem) | Tabela | SELECT | Consulta grupos de mensagens |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| MOVI (Movimento) | Tabela | UPDATE | Atualiza status, prioridade e flags de movimentos |
| RESE (Reserva) | Tabela | UPDATE | Atualiza saldos de reserva |
| AJRE (Ajuste Reserva) | Tabela | INSERT | Insere registros de ajustes de reserva |
| CTPA (Controle Piloto Automático) | Tabela | INSERT/UPDATE/DELETE | Gerencia parâmetros de piloto automático |
| CTPM (Controle Piloto Mensagem) | Tabela | INSERT/UPDATE/DELETE | Gerencia mensagens do piloto |
| FLMV (Fluxo Movimento) | Tabela | INSERT/DELETE | Gerencia fluxo de movimentos |
| PMMV (Parâmetro Movimento) | Tabela | INSERT | Insere parâmetros de movimento |
| MVSR (Movimento Sistema Reserva) | Tabela | INSERT | Registra movimentos no sistema de reserva |
| PMCE (Parâmetro Controle Envio) | Tabela | UPDATE | Atualiza parâmetros de controle de envio |
| STRE (Situação Reserva) | Tabela | UPDATE | Atualiza situação de circuit breaker |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | Leitura | Configuração de logging | Arquivo de configuração de logs em formato JSON |
| application.yml | Leitura | Spring Boot | Configurações da aplicação por ambiente |
| application-local.yml | Leitura | Spring Boot | Configurações específicas para ambiente local |
| openapi.yaml | Leitura | Swagger/OpenAPI | Contrato da API REST |
| infra.yml | Leitura | Infraestrutura | Configurações de infraestrutura e variáveis por ambiente |

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas (JMS, Kafka, RabbitMQ). A comunicação é baseada em REST APIs síncronas.

---

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas. Toda comunicação é realizada via endpoints REST síncronos.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Banco de Dados Sybase | Database | Banco de dados principal (DBISPB) para persistência de dados do SPB |
| OAuth2/JWT Provider | Autenticação | Servidor de autenticação OAuth2 com JWT (apigateway.bvnet.bv) |
| Sistema SPB/Bacen | Integração | Sistema de Pagamentos Brasileiro - troca de mensagens financeiras |
| Câmaras de Liquidação | Integração | Integração com câmaras LDL, RCO para liquidação financeira |
| Prometheus | Monitoramento | Exportação de métricas para monitoramento |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa organização em camadas (config, domain, repository, service, rest)
- Uso adequado de padrões como Dependency Injection e Repository Pattern
- Implementação de tratamento centralizado de exceções
- Documentação OpenAPI completa e detalhada
- Configuração adequada de segurança com JWT
- Uso de MapStruct para mapeamento de objetos
- Separação de configurações por ambiente
- Logging estruturado em JSON

**Pontos de Melhoria:**
- Falta de testes unitários (diretórios de teste vazios)
- Nomenclatura de stored procedures não segue padrão Java (sp_se_*, sp_in_*, sp_up_*)
- Muitas responsabilidades concentradas em poucos services
- Falta de documentação inline no código Java
- Ausência de validações de entrada nos DTOs
- Código poderia se beneficiar de mais abstrações e interfaces
- Falta de tratamento específico para diferentes tipos de exceções de banco de dados
- Configurações hardcoded em alguns pontos (ex: portas, timeouts)

O código é funcional e bem estruturado, mas carece de testes automatizados e poderia ter melhor documentação e tratamento de erros mais granular.

---

## 14. Observações Relevantes

1. **Ambiente Multi-Tenant**: O sistema trabalha com conceito de holding (holdId) e instituição (instId), sugerindo arquitetura multi-tenant

2. **Integração Legado**: Forte integração com sistema legado através de stored procedures Sybase, indicando modernização gradual

3. **Segurança**: Implementa autenticação JWT com endpoints públicos configuráveis, adequado para arquitetura de microserviços

4. **Monitoramento**: Actuator configurado em porta separada (9090) para health checks e métricas

5. **Infraestrutura como Código**: Arquivo infra.yml bem estruturado com variáveis por ambiente (des, uat, prd)

6. **Retry/Timeout**: Bootstrap script para gerenciamento de reconexão e timeout em ambiente containerizado

7. **Performance**: Uso de AsyncAppender no Logback para melhor performance de logging

8. **Compliance**: Sistema crítico para operações bancárias com controles de auditoria e rastreabilidade

9. **Horários de Operação**: Sistema sensível a janelas de operação e horários de câmaras, com validações específicas

10. **Circuit Breaker**: Implementação de padrão circuit breaker para proteção de reservas bancárias