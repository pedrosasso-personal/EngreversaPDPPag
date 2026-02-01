# Ficha Técnica do Sistema

## 1. Descrição Geral
Sistema orquestrador responsável por processar e compor informações de extratos bancários a partir de múltiplas fontes (transações efetivadas, contrapartes SPAG e PIX). O sistema consome mensagens de filas Pub/Sub do Google Cloud, enriquece os dados com informações de bancos, tipos de conta e categorização de transações, e publica o extrato composto em um tópico para consumo por outros sistemas.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal de inicialização do Spring Boot |
| **ListenerContraparte** | Listener para consumir mensagens de contrapartes SPAG |
| **ListenerContrapartePix** | Listener para consumir mensagens de contrapartes PIX |
| **ListenerTransacaoEfetivada** | Listener para consumir mensagens de transações efetivadas |
| **ContraparteRouter** | Rota Camel para processar contrapartes SPAG |
| **ContrapartePixRouter** | Rota Camel para processar contrapartes PIX |
| **TransacaoEfetivadaRouter** | Rota Camel para processar transações efetivadas |
| **ExtratoCompostoMapper** | Mapeamento de entidades para representação de extrato composto |
| **CategorizacaoTransacaoEnum** | Enum com regras de categorização de transações |
| **ConsultaBancoService** | Serviço para consulta de informações de bancos |
| **PublicarExtratoCompostoService** | Serviço para publicação do extrato composto no Pub/Sub |
| **TipoContaCache** | Cache em memória para tipos de conta |
| **FeatureToggleService** | Serviço para controle de feature toggles |

## 3. Tecnologias Utilizadas
- **Spring Boot 2.x** - Framework base
- **Apache Camel 3.x** - Framework de integração e orquestração
- **Google Cloud Pub/Sub** - Sistema de mensageria
- **MapStruct** - Mapeamento de objetos
- **Lombok** - Redução de boilerplate
- **Jackson** - Serialização/deserialização JSON
- **Spring Security OAuth2** - Autenticação e autorização
- **Logback** - Logging com formato JSON
- **Maven** - Gerenciamento de dependências
- **Docker** - Containerização
- **OpenAPI/Swagger** - Documentação de APIs
- **Feature Toggle (Unleash)** - Controle de features

## 4. Principais Endpoints REST
Não se aplica. O sistema é orientado a eventos (event-driven) e não expõe endpoints REST públicos, apenas endpoints de gerenciamento via Actuator (porta 9090).

## 5. Principais Regras de Negócio

1. **Validação de Contrapartes**:
   - Valida status de pagamento (código 3 = confirmado)
   - Valida dados da pessoa demandante da operação
   - Rejeita contrapartes do Banco Votorantim (655/161)
   - Rejeita contrapartes de conta interna BV sem movimentação

2. **Categorização de Transações**:
   - 71 categorias de transações mapeadas por código
   - Inclui PIX, TED, TEF, boletos, saques, débitos automáticos, tarifas, etc.

3. **Enriquecimento de Dados**:
   - Consulta nome de bancos por código BACEN
   - Consulta participantes SPI por ISPB (para PIX)
   - Consulta e cache de tipos de conta
   - Adiciona informações de contas balde quando necessário

4. **Composição de Conta Balde**:
   - Para boletos de tributo e consumo, adiciona dados de conta interna BV

5. **Controle por Feature Toggle**:
   - Subscriptions podem ser habilitadas/desabilitadas individualmente (SPAG, SPAG-PIX, CCBD)

6. **Mapeamento de Tipos de Pessoa**:
   - Identifica tipo de pessoa (F/J) por tamanho do CPF/CNPJ

## 6. Relação entre Entidades

**Entidades Principais**:

- **Contraparte**: Representa uma movimentação de pagamento SPAG
  - Possui: Debtor (remetente), Creditor (favorecido), SPB, Estorno, Status, CanalPagamento
  - Relaciona-se com: ContaPessoa, ContaCorrente, TipoConta

- **ContrapartePix**: Representa uma movimentação PIX
  - Possui: Message (dados da transação PIX)
  - Contém: dados de pagador e recebedor, valores, datas

- **TransacaoEfetivadaCCBD**: Representa uma transação efetivada no core bancário
  - Contém: dados da conta, valores, datas, códigos de transação

- **ExtratoCompostoRepresentation**: Entidade de saída unificada
  - Composta por: Identificador, Transacao, DetalhesTransacao, Categoria
  - DetalhesTransacao contém: Remetente, Favorecido, DetalhesAdicionais

**Relacionamentos**:
- Contraparte/ContrapartePix/TransacaoEfetivada → ExtratoCompostoRepresentation (mapeamento)
- ContaPessoa → TipoConta (consulta e cache)
- Banco (código) → Nome do Banco (consulta)
- ISPB → Participante SPI (consulta para PIX)

## 7. Estruturas de Banco de Dados Lidas

Não se aplica. O sistema não acessa diretamente banco de dados, apenas consome mensagens de filas e consulta APIs externas.

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema não persiste dados diretamente em banco de dados.

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | Leitura | Configuração Spring Boot | Configuração de logs em formato JSON |
| application.yml | Leitura | Configuração Spring Boot | Configurações da aplicação por ambiente |
| layers.xml | Leitura | Build Maven | Configuração de camadas para otimização de imagem Docker |

## 10. Filas Lidas

**Google Cloud Pub/Sub - Subscriptions:**

1. **business-ccbd-base-transacoes-efetivadas-extrato-composto-sub**
   - Consome: Transações efetivadas do core bancário
   - Listener: ListenerTransacaoEfetivada
   - Formato: TransacaoEfetivadaCCBD (JSON)

2. **business-spag-base-notificacao-extrato-composto-sub**
   - Consome: Contrapartes de pagamentos SPAG
   - Listener: ListenerContraparte
   - Formato: Contraparte (JSON)

3. **business-spag-pixx-extrato-composto-sub**
   - Consome: Contrapartes de transações PIX
   - Listener: ListenerContrapartePix
   - Formato: ContrapartePix (JSON)

## 11. Filas Geradas

**Google Cloud Pub/Sub - Topics:**

1. **business-ccbd-base-extrato-composto**
   - Publica: Extratos compostos processados
   - Service: PublicarExtratoCompostoService
   - Formato: ExtratoCompostoRepresentation (JSON)

## 12. Integrações Externas

| Sistema | Tipo | Descrição |
|---------|------|-----------|
| **sboot-glob-base-atom-lista-bancos** | REST API | Consulta lista de bancos BACEN para obter nome do banco por código |
| **sboot-glob-base-atom-cliente-dados-cadastrais** | REST API | Consulta tipos de conta disponíveis no sistema |
| **sboot-spag-pixx-atom-participantes** | REST API | Consulta participantes do SPI (Sistema de Pagamentos Instantâneos) por ISPB |
| **API Gateway OAuth** | REST API | Autenticação para chamadas às APIs internas |
| **Feature Toggle Service** | Serviço | Controle de habilitação/desabilitação de subscriptions |

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada com separação clara de responsabilidades (listeners, routers, processors, services)
- Uso adequado de padrões de projeto (Strategy, Builder, Mapper)
- Boa cobertura de testes unitários
- Uso de Apache Camel para orquestração de forma apropriada
- Implementação de cache para otimização de consultas
- Validações de negócio bem encapsuladas em classes específicas
- Configuração externalizada por ambiente
- Logging estruturado em JSON
- Uso de feature toggles para controle de funcionalidades

**Pontos de Melhoria:**
- Enum CategorizacaoTransacaoEnum muito extenso (71 categorias) poderia ser externalizado em configuração
- Algumas classes de mapeamento (ExtratoCompostoMapper) são muito complexas e poderiam ser divididas
- Falta documentação JavaDoc em algumas classes críticas
- Alguns métodos muito longos que poderiam ser refatorados
- Poderia ter mais uso de constantes para valores mágicos

## 14. Observações Relevantes

1. **Arquitetura Event-Driven**: Sistema totalmente orientado a eventos, sem endpoints REST expostos para processamento de negócio.

2. **Processamento Assíncrono**: Utiliza Google Cloud Pub/Sub com acknowledgment manual para garantir processamento confiável.

3. **Resiliência**: Implementa validações e tratamento de erros para evitar processamento de mensagens inválidas.

4. **Multi-tenant**: Suporta múltiplos bancos (BV S.A. - 413/436 e Votorantim - 655/161).

5. **Ambientes**: Configurado para DES, UAT e PRD com diferentes projetos GCP.

6. **Monitoramento**: Expõe métricas via Actuator (porta 9090) incluindo health checks e Prometheus.

7. **Segurança**: Utiliza OAuth2 JWT para autenticação nas chamadas de APIs internas.

8. **Performance**: Implementa cache em memória para tipos de conta, reduzindo chamadas externas.

9. **Observabilidade**: Logs estruturados em JSON com correlation ID e tracing distribuído via Spring Cloud Sleuth.

10. **Containerização**: Preparado para deploy em Kubernetes/OpenShift com configuração de layers otimizada.