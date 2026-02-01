# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-spag-base-orch-pagamento-boleto** é um serviço de orquestração para processamento de pagamentos de boletos no contexto do sistema SPAG (Sistema de Pagamentos) do Banco Votorantim. 

O sistema atua como um orquestrador que coordena múltiplas etapas do fluxo de pagamento de boletos, incluindo validações, débito/crédito em conta, notificações a sistemas legados (SITP, PGFT, SPAG) e tratamento de ocorrências. Utiliza Apache Camel para orquestração de rotas e implementa mecanismos de estorno automático em caso de falhas durante o processamento.

A aplicação consome mensagens de uma fila IBM MQ e também expõe endpoints REST para processamento síncrono de pagamentos.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal Spring Boot que inicializa a aplicação |
| **PagamentoBoletoController** | Controller REST que expõe endpoint POST para processar pagamentos |
| **PagamentoBoletoListener** | Listener JMS que consome mensagens da fila de boletos |
| **PagamentoBoletoService** | Serviço que inicia o processamento via Apache Camel |
| **PagamentoBoletoRouter** | Define as rotas Camel para orquestração do fluxo de pagamento |
| **CamelContextWrapper** | Wrapper do contexto Camel para gerenciamento de rotas |
| **FeatureToggleService** | Gerencia feature toggles (ex: baixa de boleto via job) |
| **NotificacaoAggregation** | Estratégia de agregação para consolidar respostas de notificações |
| **EstornoProcessor** | Processador Camel para tratamento de estorno em caso de erro |
| **ExceptionProcessor** | Processador Camel para tratamento genérico de exceções |
| **ValidarPagamentoRepositoryImpl** | Implementação de chamada ao serviço de validação de pagamento |
| **ValidarCipRepositoryImpl** | Implementação de chamada ao serviço de validação CIP |
| **DebitarCreditarContaRepositoryImpl** | Implementação de chamada ao serviço de débito/crédito em conta |
| **ValidarSolicitacaoBaixaOperacionalRepositoryImpl** | Implementação de chamada ao serviço de baixa operacional |
| **NotificarPagamentoSITPRepositoryImpl** | Implementação de notificação ao sistema SITP |
| **NotificarPagamentoPGFTRepositoryImpl** | Implementação de notificação ao sistema PGFT |
| **NotificarPagamentoSPAGRepositoryImpl** | Implementação de notificação ao sistema SPAG |
| **TratarOcorrenciasRepositoryImpl** | Implementação de chamada ao serviço de tratamento de ocorrências |
| **Mappers (diversos)** | Classes responsáveis por conversão entre DTOs e objetos de domínio |
| **IbmMqConfig** | Configuração do IBM MQ com ajuste dinâmico de concorrência via feature toggle |
| **RestTemplateConfiguration** | Configuração de RestTemplate para chamadas HTTP |
| **OcorrenciaUtil** | Utilitário para criação de objetos de ocorrência |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Apache Camel 3.22.4** (orquestração de rotas e integração)
- **IBM MQ** (mensageria)
- **Spring JMS** (integração com filas)
- **RestTemplate** (cliente HTTP para chamadas REST)
- **Lombok** (redução de boilerplate)
- **Jackson** (serialização/deserialização JSON)
- **JAXB** (unmarshalling de XML)
- **Swagger/OpenAPI 3.0** (documentação de APIs)
- **Spring Actuator** (monitoramento e health checks)
- **Micrometer/Prometheus** (métricas)
- **Logback** (logging)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Feature Toggle (ConfigCat)** (gerenciamento de features)
- **Arquitetura Base BV** (bibliotecas internas do Banco Votorantim)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/pagamento-boleto | PagamentoBoletoController | Processa um pagamento de boleto de forma síncrona |
| GET | /actuator/health | Spring Actuator | Health check da aplicação |
| GET | /actuator/metrics | Spring Actuator | Métricas da aplicação |
| GET | /actuator/prometheus | Spring Actuator | Métricas no formato Prometheus |
| GET | /swagger-ui/* | Swagger UI | Documentação interativa da API |

---

## 5. Principais Regras de Negócio

1. **Validação de Pagamento**: Antes de processar, valida a solicitação de pagamento através do serviço `atom-validar-pagamento`
2. **Validação CIP**: Valida o retorno CIP (Câmara Interbancária de Pagamentos) para garantir conformidade
3. **Débito em Conta**: Realiza o débito na conta do pagador através do serviço `nccs-base-debitar-creditar-conta`
4. **Baixa Operacional Condicional**: A baixa operacional do boleto pode ser feita imediatamente ou via job, controlado por feature toggle (`ft_boolean_boleto_baixa_via_job`)
5. **Notificações Múltiplas**: Notifica três sistemas legados (SITP, PGFT e SPAG) sobre o pagamento realizado
6. **Estorno Automático**: Em caso de falha em qualquer etapa (exceto notificação SPAG), executa estorno automático do débito
7. **Tratamento de Ocorrências**: Registra ocorrências de erro através do serviço `atom-tratar-ocorrencias`
8. **Retry com Backoff**: Implementa retry automático (3 tentativas com delay de 15 segundos) para falhas transientes
9. **Concorrência Dinâmica**: Ajusta dinamicamente o número de threads consumidoras da fila via feature toggle (`ft_number_spag_base_orch_pagamento_boleto_multithread`)
10. **Processamento Assíncrono**: Consome mensagens XML da fila IBM MQ e processa de forma assíncrona

---

## 6. Relação entre Entidades

O sistema trabalha principalmente com a entidade **DicionarioPagamento** (da biblioteca `votorantim.spag.lib.datatype`), que é um objeto complexo contendo todos os dados necessários para o processamento do pagamento.

**Fluxo de dados:**
- **DicionarioPagamento** → entrada do sistema (via REST ou MQ)
- **Request/Response DTOs** → objetos intermediários para comunicação com serviços externos
- **DicionarioPagamento** → saída do sistema (enriquecido com resultados das operações)

**Principais atributos manipulados:**
- Dados do pagamento (valor, data, código de barras)
- Flags de retorno de cada etapa (flRetornoValidaSolicitacaoPagto, flRetornoConsultaCIP, etc.)
- Informações de conta (débito/crédito)
- Dados de notificação (nuDocumento, codProtocolo)
- Lista de ocorrências (erros e avisos)

---

## 7. Estruturas de Banco de Dados Lidas

**não se aplica**

O sistema não acessa diretamente banco de dados. Todas as operações de persistência são realizadas através de chamadas a serviços externos (atoms).

---

## 8. Estruturas de Banco de Dados Atualizadas

**não se aplica**

O sistema não atualiza diretamente banco de dados. Todas as operações de escrita são realizadas através de chamadas a serviços externos (atoms).

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | leitura | /usr/etc/log (runtime) | Arquivo de configuração de logs, carregado em tempo de execução |
| application.yml | leitura | Classpath (resources) | Arquivo de configuração principal da aplicação |
| application-local.yml | leitura | Classpath (resources) | Configurações específicas para ambiente local |

---

## 10. Filas Lidas

- **QL.SPAG.SOLICITAR_PAGAMENTO_BOLETO_REQ.INT** (IBM MQ)
  - **Descrição**: Fila de entrada para solicitações de pagamento de boleto
  - **Formato**: Mensagens XML contendo objeto `PagamentoMensagem`
  - **Listener**: `PagamentoBoletoListener`
  - **Queue Manager**: QM.ATA.01
  - **Concorrência**: Configurável via feature toggle (padrão: 1)

---

## 11. Filas Geradas

**não se aplica**

O sistema não publica mensagens em filas. As notificações são realizadas através de chamadas REST síncronas aos serviços de notificação.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **atom-validar-pagamento** | REST | Valida a solicitação de pagamento antes do processamento |
| **atom-validar-cip** | REST | Valida o retorno da Câmara Interbancária de Pagamentos |
| **nccs-base-debitar-creditar-conta** | REST | Realiza débito/crédito em conta e estorno |
| **atom-solicitacao-baixa-operacional** | REST | Efetua baixa operacional do boleto |
| **sitp-base-notificar-pagamento-sitp** | REST | Notifica sistema legado SITP |
| **pgft-base-notificar-pagamento-pgft** | REST | Notifica sistema legado PGFT |
| **spag-base-notifica-pagamento** | REST | Notifica sistema SPAG |
| **atom-tratar-ocorrencias** | REST | Registra e trata ocorrências de erro |
| **IBM MQ** | Mensageria | Consome mensagens de solicitação de pagamento |
| **ConfigCat** | Feature Toggle | Gerenciamento de features e configurações dinâmicas |

**Autenticação**: Todas as chamadas REST utilizam Basic Authentication com credenciais configuradas por ambiente.

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (application, domain, common)
- Uso adequado de padrões como Repository, Mapper e Service
- Implementação de retry e tratamento de exceções
- Uso de feature toggles para controle de comportamento
- Configuração externalizada por ambiente
- Logs estruturados e informativos
- Uso de Lombok para reduzir boilerplate

**Pontos de Melhoria:**
- Falta de testes unitários e de integração nos arquivos analisados
- Acoplamento forte com a biblioteca `votorantim.spag.lib.datatype` (DicionarioPagamento)
- Uso de `simple()` do Camel para lógica de negócio poderia ser extraído para classes Java
- Configuração de retry hardcoded no router (poderia ser externalizada)
- Falta de validação de entrada nos controllers
- Tratamento de exceções genérico em alguns pontos
- Documentação inline limitada (poucos comentários explicativos)
- Classe `IbmMqConfig` com lógica de scheduler que poderia ser melhor isolada
- Parsing manual de XML no listener (uso de regex) é frágil

O código é funcional e segue boas práticas gerais, mas há espaço para melhorias em testabilidade, desacoplamento e robustez.

---

## 14. Observações Relevantes

1. **Orquestração Complexa**: O sistema implementa um fluxo de orquestração sofisticado com múltiplas etapas sequenciais e paralelas, utilizando Apache Camel como motor de integração.

2. **Resiliência**: Implementa mecanismos de resiliência como retry automático e estorno compensatório em caso de falhas.

3. **Feature Toggles**: Uso extensivo de feature toggles permite ativar/desativar funcionalidades sem deploy (ex: baixa via job, ajuste de concorrência).

4. **Ambientes Múltiplos**: Configuração preparada para múltiplos ambientes (local, des, qa, uat, prd) com variáveis específicas.

5. **Monitoramento**: Integração com Prometheus/Grafana para observabilidade e métricas customizadas.

6. **Segurança**: Implementa autenticação básica e integração com bibliotecas de segurança do BV.

7. **Processamento Híbrido**: Suporta tanto processamento síncrono (REST) quanto assíncrono (MQ).

8. **Parsing XML**: O listener faz parsing manual de mensagens SOAP/XML, removendo namespaces antes do unmarshalling JAXB.

9. **Concorrência Ajustável**: O número de consumidores da fila é ajustável em runtime através de scheduler que consulta feature toggle a cada hora.

10. **Dependências Internas**: Forte dependência de bibliotecas proprietárias do Banco Votorantim (arqt-base, spag-base).