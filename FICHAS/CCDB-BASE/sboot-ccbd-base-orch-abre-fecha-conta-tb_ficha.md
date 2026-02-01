# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema orquestrador responsável por gerenciar processos de abertura e fechamento de contas correntes no Banco Votorantim. O sistema atua como um orquestrador que integra múltiplos serviços atômicos para realizar operações como:
- Encerramento de contas correntes (iniciativa cliente ou banco)
- Importação de limites de crédito e contratos agendados
- Sincronização de modalidades de contas entre sistemas legados (Total Banco) e novo core bancário (NCC)
- Atualização de flags de total banco
- Gravação e processamento de movimentos priorizados
- Gestão de ocorrências e status de encerramento

O sistema utiliza Apache Camel para orquestração de fluxos e RabbitMQ para comunicação assíncrona via filas.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot que inicializa a aplicação |
| `AbreFechaContaTbService` | Serviço principal que orquestra o processo de fechamento de contas |
| `ImportarService` | Gerencia importação de limites de crédito e contratos agendados |
| `SincronizarService` | Coordena sincronização de modalidades entre sistemas |
| `MovimentoService` | Gerencia movimentos priorizados (gravação, atualização, efetivação) |
| `AtualizaTotalBancoService` | Atualiza flag de total banco nas contas |
| `AbreFechaContaTbController` | Controller REST para endpoints HTTP |
| `V1Controller` | Controller REST para operações de importação e sincronização |
| `AbreFechaContaTbListener` | Listener RabbitMQ que consome mensagens das filas |
| `AbreFechaContaTbRouter` | Roteador Camel para fluxos de encerramento |
| `ImportarLimiteCreditoRouter` | Roteador Camel para importação de limites |
| `SincronizarRouter` | Roteador Camel para sincronização de modalidades |
| `MovimentoRouter` | Roteador Camel para movimentos priorizados |
| `AbreFechaContaTbRepositoryImpl` | Implementação de integração com APIs de conta corrente |
| `ContaCorrenteFechaRepositoryImpl` | Integração com serviço de fechamento de contas |
| `SboaContaCorrenteRepositoryImpl` | Integração com sistema legado SBOA |
| `GlobalRepositoryImpl` | Integração com base global de contas |
| `MovimentoRepositoryImpl` | Integração com serviço de movimentações |

## 3. Tecnologias Utilizadas

- **Framework Principal**: Spring Boot 2.x
- **Linguagem**: Java 11
- **Orquestração**: Apache Camel 3.0.1
- **Mensageria**: RabbitMQ (Spring AMQP)
- **Segurança**: Spring Security OAuth2 (Resource Server com JWT)
- **Documentação API**: Swagger/OpenAPI 2.0 (Springfox 2.9.2)
- **Mapeamento de Objetos**: MapStruct 1.4.2
- **Serialização JSON**: Gson
- **Logs**: Logback com formato JSON
- **Testes**: JUnit 5, Mockito, Rest Assured, Pact (testes de contrato)
- **Build**: Maven 3.3+
- **Containerização**: Docker
- **Orquestração de Containers**: Kubernetes/OpenShift (OCP)
- **Monitoramento**: Spring Actuator, Micrometer, Prometheus
- **Auditoria**: Biblioteca customizada BV (springboot-arqt-base-trilha-auditoria-web)

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/abre-fecha-conta-tb` | `AbreFechaContaTbController` | Retorna informações básicas do serviço |
| POST | `/v1/limite/credito/importar` | `V1Controller` | Importa limites de crédito da tabela T401LICR |
| POST | `/v1/contrato/agendado/importar` | `V1Controller` | Importa contratos agendados da tabela T401OPLI |
| POST | `/v1/modalidades/sincronizar` | `V1Controller` | Sincroniza modalidades de contas entre TB e NCC |

**Observação**: O sistema também expõe endpoints do Swagger UI em `/swagger-ui.html` e endpoints de monitoramento via Actuator em `/actuator/*` (porta 9090).

## 5. Principais Regras de Negócio

1. **Validação de Pendências para Encerramento**: Antes de encerrar uma conta, o sistema valida se não há pendências (saldo total, limite, bloqueios, saldo indisponível). Se houver pendências, a conta fica com status "Aguardando Pendente Total Banco" (código 11).

2. **Encerramento Condicional**: Conta só é efetivamente encerrada se não houver saldos pendentes, bloqueios ativos ou limites não zerados.

3. **Diferenciação de Iniciativa**: O sistema trata encerramentos por iniciativa do cliente (código motivo 9) e do banco (código motivo 7) de forma diferenciada.

4. **Sincronização de Modalidades**: Processo que sincroniza códigos de modalidade entre sistema legado (Total Banco) e novo core (NCC), validando existência de contas e atualizando logs de alteração.

5. **Movimentos Priorizados**: Movimentos são gravados com status "Agendado", processados (efetivação de débito) e têm status atualizado para "Processado" ou "Erro" conforme resultado.

6. **Importação de Limites**: Importa apenas registros válidos (data de vigência acima da data atual) das tabelas T401LICR e T401OPLI.

7. **Registro de Ocorrências**: Todas as alterações de status de encerramento geram ocorrências no histórico da conta.

8. **Atualização Assíncrona**: Utiliza filas RabbitMQ para processar encerramentos, atualizações de total banco e gravação de movimentos de forma assíncrona.

## 6. Relação entre Entidades

**Entidades Principais:**

- **EncerramentoConta**: Entidade central que representa uma solicitação de encerramento, contendo dados da conta, motivo, situação, responsável, prazos e pendências.

- **StatusConta**: Representa o estado atual de uma conta corrente (saldos, bloqueios, situação cadastral).

- **MovimentoPriorizadoDomain**: Representa um movimento financeiro priorizado para processamento.

- **RegistroSincronizarModalidadesDomain**: Representa um registro de sincronização de modalidade entre sistemas.

**Relacionamentos:**
- EncerramentoConta → MotivoEncerramentoConta (N:1)
- EncerramentoConta → TipoConta (N:1)
- EncerramentoConta → ControleEncerramentoContaEndereco (1:1)
- EncerramentoConta → TransferenciaEncerramento (1:1)
- ControleEncerramentoContaEndereco → Uf (N:1)
- ControleEncerramentoContaEndereco → Pais (N:1)

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| T401LICR | tabela | SELECT | Tabela do sistema legado contendo limites de crédito válidos |
| T401OPLI | tabela | SELECT | Tabela do sistema legado contendo contratos agendados válidos |
| TbContaCorrente (DBGLOBAL) | tabela | SELECT | Tabela global de contas correntes |
| TbContaCorrente (NCC) | tabela | SELECT | Consulta de status, saldos e bloqueios de conta corrente |
| TbControleEncerramentoConta | tabela | SELECT | Consulta de dados de encerramento de contas |
| TbOcorrenciaEncerramentoConta | tabela | SELECT | Consulta última ocorrência de encerramento |
| TbModalidadeConta | tabela | SELECT | Consulta de modalidades de conta |
| TbMovimentoPriorizado | tabela | SELECT | Consulta de movimentos priorizados |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbContaCorrente (NCC) | tabela | UPDATE | Atualiza flag total banco, situação cadastral, modalidade |
| TbContaCorrente (DBGLOBAL) | tabela | UPDATE | Atualiza modalidade de conta via PrAlterarContaCorrente |
| TbControleEncerramentoConta | tabela | UPDATE | Atualiza situação de encerramento e controle pós-prazo |
| TbOcorrenciaEncerramentoConta | tabela | INSERT | Insere ocorrências de encerramento |
| TbLogAlteracao | tabela | INSERT | Registra log de alterações de modalidade |
| TbMovimentoPriorizado | tabela | INSERT/UPDATE | Insere novos movimentos e atualiza status de processamento |
| TbContaCorrente (Total Banco) | tabela | UPDATE | Encerra conta no sistema legado |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | leitura | `/usr/etc/log` (runtime) | Arquivo de configuração de logs em formato JSON |
| application.yml | leitura | `src/main/resources` | Arquivo de configuração da aplicação Spring Boot |

## 10. Filas Lidas

| Nome da Fila | Tecnologia | Classe Consumidora | Descrição |
|--------------|------------|-------------------|-----------|
| `events.business.CCBD-BASE.consisteAberturaConta` | RabbitMQ | `AbreFechaContaTbListener.atualizaTotalBanco()` | Recebe eventos para atualizar flag total banco |
| `events.business.CCBD-BASE.consisteEncerramentoConta` | RabbitMQ | `AbreFechaContaTbListener.encerramentoConta()` | Recebe eventos para processar encerramento de contas |
| `events.business.CCBD-BASE.gravarMovimento` | RabbitMQ | `AbreFechaContaTbListener.gravarMovimento()` | Recebe eventos para gravar movimentos priorizados |

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| `sboot-ccbd-base-atom-conta-corrente` | REST API | Serviço atômico de conta corrente - consultas, atualizações, encerramentos |
| `sboot-sboa-base-atom-conta-corrente` | REST API | Serviço legado SBOA - encerramento no Total Banco, consulta de registros |
| `sboot-ccbd-base-atom-conta-corrente-fecha` | REST API | Serviço de fechamento de contas - importação e sincronização |
| `sboot-glob-base-atom-conta-bd` | REST API | Serviço global de contas - validações e atualizações na base global |
| `sboot-ccbd-base-atom-movimentacoes` | REST API | Serviço de movimentações - gravação e atualização de movimentos priorizados |
| `sboot-ccbd-base-orch-efet-debito` | REST API | Serviço orquestrador de efetivação de débitos |
| API Gateway OAuth2 | OAuth2/JWT | Serviço de autenticação e autorização - obtenção de tokens JWT |
| RabbitMQ | Message Broker | Broker de mensagens para comunicação assíncrona |

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (presentation, domain, infrastructure)
- Uso adequado de padrões como Repository, Service e Mapper
- Implementação de testes unitários, integração e funcionais
- Uso de Apache Camel para orquestração de fluxos complexos
- Configuração externalizada e separada por ambiente
- Documentação OpenAPI/Swagger bem estruturada
- Uso de MapStruct para mapeamento de objetos
- Logs estruturados em JSON

**Pontos de Melhoria:**
- Métodos muito longos em `AbreFechaContaTbService.fechaContas()` com lógica complexa que poderia ser refatorada
- Uso de conversões manuais (`toInt()`, `toLong()`, `toString()`) que poderiam ser centralizadas
- Tratamento de exceções genérico em alguns pontos (catch Exception)
- Falta de validações de entrada em alguns métodos
- Código com alguns "code smells" como constantes mágicas (números hardcoded)
- Comentários em português misturados com código em inglês
- Algumas classes de teste vazias ou incompletas
- Uso de `@Deprecated` sem justificativa clara em construtores

## 14. Observações Relevantes

1. **Arquitetura Multi-Módulo**: O projeto está organizado em módulos Maven (application, domain, common) seguindo boas práticas de separação.

2. **Integração com Sistemas Legados**: O sistema faz ponte entre o sistema legado (Total Banco/SBOA) e o novo core bancário (NCC), sendo crítico para a migração tecnológica.

3. **Processamento Assíncrono**: Utiliza filas RabbitMQ para processar operações de forma assíncrona, permitindo escalabilidade e resiliência.

4. **Segurança**: Implementa OAuth2 com JWT para autenticação e autorização, integrando com API Gateway corporativo.

5. **Observabilidade**: Possui endpoints de health check, métricas Prometheus e logs estruturados em JSON para facilitar monitoramento.

6. **Ambientes**: Configurado para múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas por ambiente.

7. **Infraestrutura como Código**: Possui arquivo `infra.yml` com configurações para deploy em Kubernetes/OpenShift.

8. **Padrão de Nomenclatura**: Segue convenção de nomenclatura do Banco Votorantim (prefixos sboot, ccbd, base, orch, atom).

9. **Dependências Críticas**: O sistema depende de múltiplos serviços externos; falha em qualquer um pode impactar o funcionamento.

10. **Complexidade de Negócio**: Implementa regras complexas de encerramento de contas com múltiplas validações e integrações, sendo um componente crítico para operações bancárias.