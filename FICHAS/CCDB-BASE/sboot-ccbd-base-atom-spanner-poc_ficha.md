# Ficha Técnica do Sistema

## 1. Descrição Geral
Sistema de Proof of Concept (PoC) para migração de serviços de Conta Corrente do Sybase para Google Cloud Spanner. O componente implementa operações de efetivação de TEF (Transferência Eletrônica de Fundos) entre contas, incluindo validações de saldo, bloqueios, movimentações e integração com filas Pub/Sub para publicação de eventos de transações efetivadas e bloqueios monitorados.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application.java` | Classe principal Spring Boot que inicializa a aplicação |
| `ContaController.java` | Controller REST que expõe endpoint para efetivação de TEF |
| `EfetivarTefService.java` | Serviço principal que orquestra a efetivação de TEF entre remetente e favorecido |
| `CriticasService.java` | Realiza validações de negócio (situação da conta, transações, duplicações, bloqueios) |
| `ContaEntity.java` | Entidade JPA que representa a tabela TbConta no Spanner |
| `MovimentoDiaEntity.java` | Entidade que representa movimentações do dia |
| `HistoricoMovimentoEntity.java` | Entidade que armazena histórico de movimentações |
| `SaldoBloqueadoEntity.java` | Entidade que representa bloqueios de saldo |
| `TransacaoEntity.java` | Entidade que representa tipos de transações |
| `DadosEfetivacao.java` | DTO que encapsula dados necessários para efetivação de operações |
| `ContaCorrenteException.java` | Exception customizada para erros de negócio |
| `ExceptionHandlerInterception.java` | Handler global de exceções |

## 3. Tecnologias Utilizadas
- **Framework:** Spring Boot 2.x
- **Linguagem:** Java 11
- **Banco de Dados:** Google Cloud Spanner
- **ORM:** Spring Cloud GCP Data Spanner (versão 1.2.8.RELEASE)
- **Mensageria:** Google Cloud Pub/Sub
- **Documentação API:** SpringDoc OpenAPI 3.0 / Swagger
- **Monitoramento:** Spring Actuator + Micrometer Prometheus
- **Mapeamento:** MapStruct
- **Utilitários:** Lombok
- **Build:** Maven 3.8+
- **Container:** Docker (OpenJ9 Alpine)

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/banco-digital/conta/efetivarTef` | `ContaController` | Efetiva transferência eletrônica de fundos entre remetente e favorecido |

## 5. Principais Regras de Negócio

1. **Validação de Conta:** Verifica se a conta existe e está ativa (situação cadastral 2, 6 ou 7)
2. **Validação de Bloqueios:** 
   - Verifica bloqueio de crédito para operações de crédito
   - Verifica bloqueio de débito para operações de débito (com possibilidade de ignorar conforme motivo)
3. **Validação de Saldo:** Para débitos sem flag incondicional, valida se há saldo disponível considerando limite, bloqueios e indisponibilidades
4. **Idempotência:** Verifica duplicação de transações através do número sequencial único
5. **Validação de Transação:** Verifica se a transação está ativa e se o tipo (débito/crédito) corresponde à operação
6. **Efetivação com Bloqueio:** Quando há bloqueio prévio, atualiza o bloqueio e efetiva a operação
7. **Atualização de Protocolo:** Permite atualização de protocolo de pagamento em transações já efetivadas
8. **Histórico de Saldo:** Mantém histórico de saldos após cada movimentação
9. **Publicação de Eventos:** Publica eventos de transações efetivadas e bloqueios monitorados em filas Pub/Sub
10. **Controle de Data:** Valida se a agência/banco aceita movimentação através da tabela de controle

## 6. Relação entre Entidades

- **ContaEntity** (1) ←→ (N) **MovimentoDiaEntity**: Uma conta possui múltiplas movimentações do dia
- **ContaEntity** (1) ←→ (N) **HistoricoMovimentoEntity**: Uma conta possui múltiplos históricos de movimento
- **ContaEntity** (1) ←→ (N) **SaldoBloqueadoEntity**: Uma conta pode ter múltiplos bloqueios de saldo
- **ContaEntity** (1) ←→ (1) **HistoricoSaldoEntity**: Uma conta possui um histórico de saldo
- **TransacaoEntity** (1) ←→ (N) **MovimentoDiaEntity**: Uma transação pode estar em múltiplas movimentações
- **MotivoBloqueioEntity** (1) ←→ (N) **SaldoBloqueadoEntity**: Um motivo de bloqueio pode estar em múltiplos bloqueios

Chaves compostas: Banco + Conta + Tipo Conta

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbConta | Tabela | SELECT | Consulta dados da conta corrente |
| TbTransacao | Tabela | SELECT | Consulta informações de transações |
| TbMotivoBloqueio | Tabela | SELECT | Consulta motivos de bloqueio |
| TbSaldoBloqueado | Tabela | SELECT | Consulta bloqueios de saldo ativos |
| TbControleData | Tabela | SELECT | Consulta controle de datas de movimentação por agência |
| TbHistoricoSaldo | Tabela | SELECT | Consulta histórico de saldos |
| TbMovimentoDia | Tabela | SELECT | Consulta movimentações do dia para validação de duplicidade |
| TbHistoricoMovimento | Tabela | SELECT | Consulta histórico de movimentos para validação de duplicidade |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbConta | Tabela | UPDATE | Atualiza saldos, sequenciais e data de último lançamento |
| TbMovimentoDia | Tabela | INSERT/UPDATE | Insere novos movimentos do dia e atualiza protocolo |
| TbHistoricoSaldo | Tabela | UPDATE | Atualiza histórico de saldos após movimentações |
| TbSaldoBloqueado | Tabela | UPDATE | Atualiza bloqueios (desbloqueio) após efetivação |
| TbHistoricoMovimento | Tabela | UPDATE | Atualiza protocolo de movimentos históricos |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| openapi.yaml | Leitura | src/main/resources/swagger/ | Especificação OpenAPI da API REST |
| application.yml | Leitura | src/main/resources/ | Configurações da aplicação |
| logback-spring.xml | Leitura | src/main/resources/ | Configuração de logs |

## 10. Filas Lidas
não se aplica

## 11. Filas Geradas

- **business-ccbd-base-transacoes-efetivadas** (Pub/Sub Topic): Publica eventos de transações efetivadas (movimentações) para categorização
- **business-ccbd-base-credito-bloqueado** (Pub/Sub Topic): Publica eventos de créditos monitorados para controle de bloqueios

Configuração por ambiente:
- DES: `projects/bv-ccbd-des/topics/...`
- UAT: `projects/bv-ccbd-uat/topics/...`
- PRD: `projects/bv-ccbd-prd/topics/...`

## 12. Integrações Externas

- **Google Cloud Spanner:** Banco de dados principal para persistência de dados de conta corrente
- **Google Cloud Pub/Sub:** Mensageria para publicação de eventos de transações e bloqueios
- **OAuth2/JWT:** Autenticação e autorização via tokens JWT

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades (controllers, services, repositories, mappers)
- Uso adequado de anotações Spring e Lombok
- Tratamento de exceções customizado
- Implementação de idempotência
- Logs informativos em pontos estratégicos
- Uso de transações para garantir consistência

**Pontos de Melhoria:**
- Código comentado nas classes de configuração Pub/Sub (BloqueiosMonitoradosPublisherConfig, SettledTransactionPublisherConfig, AppGatewayConfig, PubSubProperties)
- Método `efetivarTEF` muito extenso e com alta complexidade ciclomática
- Falta de testes unitários implementados (classes de teste vazias)
- Alguns métodos privados muito longos que poderiam ser refatorados
- Validação de data de processamento comentada no código
- Uso de strings literais em alguns pontos ao invés de constantes
- Falta de documentação JavaDoc em métodos complexos

## 14. Observações Relevantes

1. **PoC em Produção:** Este é um projeto de Proof of Concept para migração do Sybase para Google Spanner, mas já possui características de código produtivo
2. **Configurações Comentadas:** As configurações de Pub/Sub estão comentadas, sugerindo que a funcionalidade de publicação de eventos pode estar desabilitada
3. **Infraestrutura como Código:** Possui arquivo `infra.yml` com configurações de deployment para múltiplos ambientes (DES, UAT, PRD)
4. **Segurança:** Implementa OAuth2 com JWT para autenticação
5. **Monitoramento:** Configurado com Actuator e Prometheus para observabilidade
6. **Conversão de Códigos de Banco:** Possui enum `BancoEnum` para conversão entre códigos internos e externos (161↔655 para Banco Votorantim, 436↔413 para BV SA)
7. **Flags de Controle:** Utiliza diversas flags para controle de comportamento (flLancamentoIncondicionalSaldo, flEnvioCCExterno, etc.)
8. **Pipeline CI/CD:** Configurado para Jenkins com propriedades específicas (jenkins.properties)