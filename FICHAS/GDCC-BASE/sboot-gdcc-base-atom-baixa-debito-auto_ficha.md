# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de baixa de débito automático para produtos de crédito do Banco Votorantim. O sistema processa eventos de débito automático efetivado, tanto através de fluxo offline (remessa tradicional) quanto online (eventos Kafka em D0), gravando os registros em tabela temporária para posterior processamento de baixa de parcelas. Suporta produtos como Crédito Pessoal, Financiamento de Veículo e Crédito Fácil.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot, ponto de entrada da aplicação |
| `BaixaDebitoAutoService` | Serviço de domínio que orquestra a lógica de negócio para gravação de eventos de baixa |
| `BaixaDebitoAutoController` | Controller REST v1 para receber requisições de baixa de débito automático |
| `BaixaDebitoAutoV2Controller` | Controller REST v2 com suporte a fluxo online (apenas ambientes não produtivos) |
| `DebitoAutomaticoEfetivadoConsumer` | Consumer Kafka que processa eventos de débito automático efetivado em D0 |
| `BaixaDebitoAutoRepositoryImpl` | Implementação do repositório usando JDBI para acesso ao banco Sybase |
| `FeatureToggleService` | Serviço para controle de feature toggle do fluxo online |
| `LogArquivoDebito` | Entidade de domínio representando o evento de baixa |
| `BaixaDebitoAutoMapper` | Mapper para conversão entre representações REST e domínio |
| `ErrorFormat` | Utilitário para formatação de erros de negócio |

## 3. Tecnologias Utilizadas

- **Framework:** Spring Boot 2.x
- **Linguagem:** Java 11
- **Persistência:** JDBI 3.9.1
- **Banco de Dados:** Sybase (jConnect 16.3)
- **Mensageria:** Apache Kafka com Confluent Schema Registry
- **Serialização:** Apache Avro 1.12.0
- **Documentação API:** Swagger/OpenAPI (Springfox 3.0.0)
- **Segurança:** Spring Security OAuth2 com JWT
- **Monitoramento:** Spring Actuator + Prometheus + Grafana
- **Auditoria:** Trilha de Auditoria BV (arqt-base-trilha-auditoria)
- **Feature Toggle:** ConfigCat (arqt-base-feature-toggle)
- **Build:** Maven 3.x
- **Containerização:** Docker
- **Orquestração:** Kubernetes/OpenShift (Google Cloud Platform)

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/credito-pessoal/inserir/log-arquivo` | `BaixaDebitoAutoController` | Realiza baixa de débito automático para crédito pessoal |
| POST | `/v1/financiamento-veiculo/inserir/log-arquivo` | `BaixaDebitoAutoController` | Realiza baixa de débito automático para financiamento de veículo |
| POST | `/v2/credito-pessoal/inserir/log-arquivo` | `BaixaDebitoAutoV2Controller` | Realiza baixa com suporte a fluxo online (flag flFluxoOnline) |
| GET | `/actuator/health` | Spring Actuator | Health check da aplicação |
| GET | `/actuator/prometheus` | Spring Actuator | Métricas para Prometheus |
| GET | `/swagger-ui.html` | Springfox | Documentação interativa da API |

## 5. Principais Regras de Negócio

1. **Validação de Produto:** Apenas produtos parametrizados (Financiamento de Veículo=2, Crédito Pessoal=3, Crédito Fácil=4) são processados
2. **Validação de Status:** Somente débitos com status "PAGO" (código 4) são aceitos no fluxo online
3. **Validação de Conta Convênio:** Verifica existência e status ativo da conta convênio antes de processar
4. **Validação de Registro Débito:** Busca registro de débito ativo (status 3, 5 ou 7) por CPF, contrato, parcela e sequência
5. **Prevenção de Duplicidade:** Verifica se já existe registro na tabela temporária para o mesmo contrato e registro de débito
6. **Priorização de Fluxo Online:** Se uma baixa já foi processada pelo fluxo online (flag='S'), não processa novamente pelo fluxo offline
7. **Feature Toggle:** Fluxo online controlado por feature toggle (ft_boolean_gdcc_base_debito_d0)
8. **Validação de Dados Obrigatórios:** Contrato, sequência do contrato e número da parcela são obrigatórios no fluxo online
9. **Conversão de Retorno:** Mapeia código de status de pagamento (4) para código de retorno "DF" (Débito Efetuado)
10. **Auditoria:** Registra login 'gdcc-base-atom-baixa-debito-auto' e data de inclusão em todos os registros

## 6. Relação entre Entidades

**Entidades de Domínio:**

- **LogArquivoDebito:** Entidade principal contendo dados do evento de baixa (datas, valores, contas, contrato, parcela)
- **ConsultaContaConvenio:** Representa o código da conta convênio obtido do banco
- **RegistroDebito:** Representa o código do registro de débito obtido do banco
- **FluxoOnline:** Indica se o registro foi processado pelo fluxo online ou offline

**Relacionamentos:**
- LogArquivoDebito → ConsultaContaConvenio (via numeroConta + numeroBanco)
- LogArquivoDebito → RegistroDebito (via cpf + numeroContrato + numeroParcela + numeroSequencia)
- LogArquivoDebito → FluxoOnline (via numeroContrato + codigoRegistroDebito)

**Enums:**
- **TipoProdutoEnum:** Define tipos de produto aceitos (2, 3, 4)
- **RetornoDebitoAutomaticoEnum:** Mapeia status de pagamento para código de retorno
- **ExceptionReasonEnum:** Define códigos e mensagens de erro de negócio

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DbGestaoDebitoContaCorrente..TbContaConvenio | Tabela | SELECT | Consulta código da conta convênio por número de conta e banco |
| DbGestaoDebitoContaCorrente..TbRegistroDebito | Tabela | SELECT | Consulta código do registro de débito por CPF e dados do contrato |
| DBGESTAO..TbParcelaDebito | Tabela | SELECT | Consulta parcela de débito vinculada ao registro (join) |
| DbGestaoDebitoContaCorrente..TbArquivoDebitoTemp | Tabela | SELECT | Verifica existência de registro já processado e flag de fluxo online |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DbGestaoDebitoContaCorrente..TbArquivoDebitoTemp | Tabela | INSERT | Grava evento de baixa na tabela temporária para processamento posterior |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | Leitura | /usr/etc/log (runtime) | Configuração de logs da aplicação |
| application.yml | Leitura | Classpath resources | Configurações da aplicação por ambiente |
| kafkaschema-ccbd-base-debito-automatico-efetivado-v2.avsc | Leitura | Classpath resources/avro | Schema Avro para deserialização de eventos Kafka |

## 10. Filas Lidas

**Tópico Kafka:**
- **Nome:** `ccbd-base-debito-automatico-efetivado-v2`
- **Grupo de Consumo:** `sboot-gdcc-base-atom-baixa-debito-auto`
- **Schema:** DebitoAutomaticoEfetivadoV2 (Avro)
- **Classe Consumidora:** `DebitoAutomaticoEfetivadoConsumer`
- **Descrição:** Consome eventos de débito automático efetivado em D0 para processamento de baixa online
- **Configuração:** Manual acknowledgment, offset reset earliest, deserialização Avro com Schema Registry

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas.

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Confluent Kafka | Mensageria | Consumo de eventos de débito automático efetivado |
| Confluent Schema Registry | Schema Management | Gerenciamento de schemas Avro para serialização/deserialização |
| ConfigCat | Feature Toggle | Controle de ativação/desativação do fluxo online |
| Sybase Database | Banco de Dados | Acesso às bases DbGestaoDebitoContaCorrente e DBGESTAO |
| OAuth2/JWT Provider | Autenticação | Validação de tokens JWT para segurança dos endpoints |
| Prometheus | Monitoramento | Exportação de métricas da aplicação |

## 13. Avaliação da Qualidade do Código

**Nota:** 7.5/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (domain, application)
- Uso adequado de padrões como Repository, Service e Controller
- Implementação de testes unitários com boa cobertura
- Uso de feature toggle para controle de funcionalidades
- Tratamento de exceções customizado com enums de erro
- Configuração adequada para múltiplos ambientes
- Uso de Lombok para redução de boilerplate
- Documentação OpenAPI/Swagger
- Logs estruturados e informativos

**Pontos de Melhoria:**
- Alguns métodos estáticos em classes utilitárias (ErrorFormat, BaixaDebitoAutoMapper) poderiam ser injetados como beans
- Lógica de validação no Consumer poderia ser extraída para classes específicas
- Falta de constantes para strings mágicas (ex: "S", "N", "DF")
- Alguns métodos com múltiplas responsabilidades (ex: `consumerSalvarEventoDaRemessaFluxoOnline`)
- Comentários em código poderiam ser mais descritivos
- Falta de documentação JavaDoc em algumas classes públicas
- Alguns testes com mocks excessivos que dificultam manutenção
- Configurações de segurança poderiam estar mais centralizadas

## 14. Observações Relevantes

1. **Ambientes:** O controller V2 com suporte a fluxo online está disponível apenas em ambientes não produtivos (local, des, uat, qa)

2. **Segurança:** Sistema protegido por OAuth2 com JWT, exceto endpoints do Swagger

3. **Resiliência:** Implementa retry automático no consumer Kafka com delay de 300 segundos em caso de falha

4. **Auditoria:** Integrado com trilha de auditoria BV através de interceptor customizado no Kafka

5. **Monitoramento:** Expõe métricas detalhadas via Actuator/Prometheus incluindo JVM, HTTP, HikariCP e logs

6. **Infraestrutura:** Preparado para deploy em Kubernetes/OpenShift no Google Cloud Platform

7. **Versionamento:** Sistema em versão 0.19.0, indicando ainda em fase de evolução

8. **Dependências:** Utiliza bibliotecas internas do Banco Votorantim (arqt-base) para padronização

9. **Testes:** Estrutura de testes separada em unit, integration e functional com profiles Maven específicos

10. **ArchUnit:** Possui validação de arquitetura através de testes automatizados com ArchUnit