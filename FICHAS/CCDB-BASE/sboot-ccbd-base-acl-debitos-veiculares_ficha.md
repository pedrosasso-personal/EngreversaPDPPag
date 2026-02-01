# Ficha Técnica do Sistema

---

## 1. Descrição Geral

Sistema ACL (Anti-Corruption Layer) para débitos veiculares do Banco Votorantim/BV. Expõe APIs REST para consulta e pagamento de débitos veiculares (IPVA, DPVAT, Multas, Multas RENAINF, Licenciamento, Transferência, Taxas DETRAN e Primeiro Registro). Suporta pagamentos via conta corrente e cartão de crédito, além de cálculo de parcelas, busca de recibos e consulta de extrato bancário. Integra-se com sistemas legados DETRAN/PRODESP via SOAP Web Services através de API Gateway, isolando a complexidade dos sistemas backend.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ConsultaDebitosVeicularesControllerV1** | Controller REST para consultas de débitos (IPVA, DPVAT, Licenciamento, Multas, RENAINF) |
| **PagarComCartaoControllerV1** | Controller REST para pagamentos com cartão de crédito |
| **CalcularParcelasControllerV1** | Controller REST para cálculo de parcelas de pagamento |
| **ConsultaExtratoControllerV1** | Controller REST para consulta de extrato bancário |
| **ConsultaDebitosVeicularesService** | Service para orquestração de consultas de débitos via Camel |
| **PagarDebitoVeicularesService** | Service para orquestração de pagamentos via conta corrente |
| **PagarComCartaoService** | Service para orquestração de pagamentos via cartão |
| **ConsultarExtratoService** | Service para consulta de extrato com validação de range de datas (máx 31 dias) |
| **CalcularParcelaService** | Service para cálculo de parcelas com seguro e taxas |
| **DebitoVeicularMapper** | MapStruct mapper para conversão entre Representation/Domain/Backend de débitos |
| **PagamentoCartaoMapper** | MapStruct mapper para conversão de dados de pagamento com cartão |
| **ExtratoMapper** | Mapper manual para conversão de dados de extrato bancário |
| **CalcularParcelaMapper** | MapStruct mapper para conversão de dados de parcelas |
| **CamelContextWrapper** | Wrapper para gerenciamento de rotas Apache Camel |
| **AuthRepositoryImpl** | Implementação de autenticação OAuth2 client credentials |
| **Routers Camel** | Múltiplos routers (PagaDpvatRouter, PagaIpvaRouter, etc) para orquestração de fluxos |
| **WsConfiguration** | Configuração de beans SOAP WebServiceTemplate para integração backend |
| **ApiKey** | Utilitário para recuperação de chaves de acesso por código de banco |
| **ErrorFormat** | Utilitário centralizado para tratamento e formatação de erros |

---

## 3. Tecnologias Utilizadas

- **Framework Principal:** Spring Boot 2.x
- **Linguagem:** Java 11
- **Orquestração:** Apache Camel 3.0.1
- **Mapeamento:** MapStruct (conversão DTOs)
- **Web Services:** JAX-WS, Spring Web Services, JAXB 2.3.1
- **REST:** Spring Web MVC, Swagger/OpenAPI
- **Segurança:** OAuth2 (client credentials), Spring Security, JWT
- **Pool Conexões:** HikariCP
- **Serialização:** Jackson (JSON), JAXB (XML)
- **Logging:** Logback (formato JSON)
- **Métricas:** Micrometer, Prometheus, Grafana
- **Testes:** JUnit 5, Mockito, EasyRandom, ArchUnit, Pact (contract testing)
- **Build:** Maven (multi-módulo)
- **Infraestrutura:** Kubernetes, Docker, Google Cloud Platform (OCP)
- **CI/CD:** Jenkins
- **Utilitários:** Lombok, WSS4J (WS-Security)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/consultaDebitosIpva` | ConsultaDebitosVeicularesControllerV1 | Consulta débitos de IPVA por RENAVAM |
| GET | `/v1/consultaDebitosDpvat` | ConsultaDebitosVeicularesControllerV1 | Consulta débitos de DPVAT por RENAVAM |
| GET | `/v1/consultaDebitosLicenciamento` | ConsultaDebitosVeicularesControllerV1 | Consulta débitos de Licenciamento por RENAVAM |
| GET | `/v1/consultaDebitosMultas` | ConsultaDebitosVeicularesControllerV1 | Consulta débitos de Multas por RENAVAM |
| GET | `/v1/consultaDebitosRenainf` | ConsultaDebitosVeicularesControllerV1 | Consulta débitos de Multas RENAINF por RENAVAM |
| POST | `/v1/pagarIpva` | ConsultaDebitosVeicularesControllerV1 | Pagamento de IPVA via conta corrente |
| POST | `/v1/pagarDpvat` | ConsultaDebitosVeicularesControllerV1 | Pagamento de DPVAT via conta corrente |
| POST | `/v1/pagarLicenciamento` | ConsultaDebitosVeicularesControllerV1 | Pagamento de Licenciamento via conta corrente |
| POST | `/v1/pagarMultas` | ConsultaDebitosVeicularesControllerV1 | Pagamento de Multas via conta corrente |
| POST | `/v1/pagarMultasRenaInf` | ConsultaDebitosVeicularesControllerV1 | Pagamento de Multas RENAINF via conta corrente |
| POST | `/v1/pagarTransferencia` | ConsultaDebitosVeicularesControllerV1 | Pagamento de Transferência via conta corrente |
| POST | `/v1/pagarTaxasDetran` | ConsultaDebitosVeicularesControllerV1 | Pagamento de Taxas DETRAN via conta corrente |
| POST | `/v1/pagarPrimeiroRegistro` | ConsultaDebitosVeicularesControllerV1 | Pagamento de Primeiro Registro via conta corrente |
| POST | `/v1/pagarDpvatPrimeiroRegistro` | ConsultaDebitosVeicularesControllerV1 | Pagamento de DPVAT Primeiro Registro via conta corrente |
| POST | `/v1/pagarDebitos` | ConsultaDebitosVeicularesControllerV1 | Pagamento múltiplos débitos via conta corrente |
| POST | `/v1/buscarRecibos` | ConsultaDebitosVeicularesControllerV1 | Busca histórico de recibos de pagamento |
| POST | `/v1/pagarIpvaCartao` | PagarComCartaoControllerV1 | Pagamento de IPVA via cartão de crédito |
| POST | `/v1/pagarDpvatCartao` | PagarComCartaoControllerV1 | Pagamento de DPVAT via cartão de crédito |
| POST | `/v1/pagarLicenciamentoCartao` | PagarComCartaoControllerV1 | Pagamento de Licenciamento via cartão de crédito |
| POST | `/v1/pagarMultasCartao` | PagarComCartaoControllerV1 | Pagamento de Multas via cartão de crédito |
| POST | `/v1/pagarCartaoMultasRenanInf` | PagarComCartaoControllerV1 | Pagamento de Multas RENAINF via cartão de crédito |
| POST | `/v1/calc-parcelas` | CalcularParcelasControllerV1 | Cálculo de parcelas com seguro e taxas |
| POST | `/v1/consultaExtrato` | ConsultaExtratoControllerV1 | Consulta extrato bancário (range máx 31 dias) |

---

## 5. Principais Regras de Negócio

- **Validação RENAVAM obrigatório:** Todas as consultas de débitos exigem número RENAVAM válido
- **Código Banco obrigatório:** Todas as operações exigem código do banco (655 - Votorantim ou 413 - BV)
- **Chaves API diferenciadas:** Sistema utiliza chaves de acesso distintas para Banco Votorantim (655) e Banco BV (413)
- **Autenticação OAuth2:** Todas as chamadas aos serviços backend requerem token OAuth2 obtido via client credentials
- **Range de datas extrato:** Consulta de extrato bancário limitada a período máximo de 31 dias
- **Conversão de valores:** Valores monetários convertidos de centavos (Integer) para BigDecimal nas respostas
- **Múltiplos débitos simultâneos:** Endpoint `/pagarDebitos` permite pagamento de múltiplos tipos de débitos em uma única transação
- **Cálculo de parcelas:** Suporta cálculo de parcelas com seguro prestamista e taxas administrativas
- **Tipos de débitos suportados:** IPVA, DPVAT, Multas, Multas RENAINF, Licenciamento, Transferência, Taxas DETRAN, Primeiro Registro
- **Modalidades de pagamento:** Conta corrente e cartão de crédito
- **Validação de dados cartão:** Pagamentos com cartão exigem dados completos (número, CVV, validade, bandeira, dados proprietário, endereço)
- **Trilha de auditoria:** Interceptor customizado (TrilhaAuditoriaWSInterceptor) registra todas as chamadas SOAP
- **Tratamento de erros padronizado:** Exceções mapeadas para códigos HTTP específicos (400, 403, 422, 500) com mensagens descritivas

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **Veiculo:** Contém dados do veículo (RENAVAM, placa, chassi, categoria)
- **IPVA:** Débito de IPVA vinculado a Veiculo, contém exercício, valor, vencimento
- **DPVAT:** Débito de DPVAT vinculado a Veiculo, contém categoria, identificação, valor
- **Multa:** Débito de Multa vinculado a Veiculo, contém auto de infração, valor, data infração
- **MultaRENAINF:** Débito de Multa RENAINF vinculado a Veiculo
- **Licenciamento:** Débito de Licenciamento vinculado a Veiculo, contém exercício, valor
- **Transferencia:** Débito de Transferência vinculado a Veiculo
- **TaxaDETRAN:** Débito de Taxa DETRAN vinculado a Veiculo
- **PrimeiroRegistro:** Débito de Primeiro Registro vinculado a Veiculo
- **ItemPagamento:** Item genérico de pagamento, pode ser IPVA, DPVAT, Multa, etc
- **RetornoPagamento:** Retorno de operação de pagamento (sucesso, mensagem, operacaoId, URL recibo)
- **CartaoDTO:** Dados do cartão de crédito (número, CVV, validade, bandeira)
- **DadosProprietarioCartao:** Dados do proprietário do cartão (CPF, nome, RG, email, telefone, endereço, data nascimento)
- **DadosBeneficiado:** Dados do beneficiário do pagamento
- **DadosPagamento:** Dados da transação (parcelas, plano, seguro, valores)
- **Parcela:** Parcela de pagamento (número, valor, vencimento, taxa)
- **ExtratoDTO:** Extrato bancário contendo lista de DiaExtratoDTO
- **DiaExtratoDTO:** Dia do extrato contendo lista de ItemExtratoDTO
- **ItemExtratoDTO:** Item do extrato (data, documento, histórico, valor, tipo operação)

**Relacionamentos:**
- Veiculo 1:N IPVA/DPVAT/Multa/Licenciamento/etc (um veículo pode ter múltiplos débitos)
- Pagamento 1:N ItemPagamento (um pagamento pode quitar múltiplos débitos)
- PagamentoCartao 1:1 CartaoDTO (um pagamento com cartão possui dados do cartão)
- PagamentoCartao 1:1 DadosProprietarioCartao (um pagamento possui dados do proprietário)
- ExtratoDTO 1:N DiaExtratoDTO 1:N ItemExtratoDTO (hierarquia de extrato)

---

## 7. Estruturas de Banco de Dados Lidas

**Não se aplica**

O sistema é stateless e não acessa diretamente estruturas de banco de dados. Todas as consultas são realizadas via integração com Web Services SOAP externos (DETRAN/PRODESP).

---

## 8. Estruturas de Banco de Dados Atualizadas

**Não se aplica**

O sistema é stateless e não realiza operações diretas em banco de dados. Todas as operações de pagamento são processadas via integração com Web Services SOAP externos (DETRAN/PRODESP).

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| **logback-spring.xml** | Leitura | Logback (configuração) | Arquivo de configuração de logging em formato JSON |
| **application.yml** | Leitura | Spring Boot (configuração) | Arquivo de configuração da aplicação (profiles: local, des, qa, uat, prd) |
| **cacerts** | Leitura | JVM (volume Kubernetes) | Certificados Java para conexões HTTPS |
| **LDAP** | Leitura | Volume Kubernetes | Configurações LDAP (se aplicável) |

---

## 10. Filas Lidas

**Não se aplica**

O sistema não consome mensagens de filas. Toda comunicação é síncrona via REST (entrada) e SOAP (saída).

---

## 11. Filas Geradas

**Não se aplica**

O sistema não publica mensagens em filas. Toda comunicação é síncrona via REST (entrada) e SOAP (saída).

---

## 12. Integrações Externas

| Sistema Externo | Tipo | Protocolo | Descrição |
|-----------------|------|-----------|-----------|
| **API Gateway BV - ServPagamentos** | Backend DETRAN/PRODESP | SOAP/HTTPS | Serviço de pagamentos e consultas de débitos veiculares. Endpoints: PagaIPVA, PagaDPVAT, PagaMultas, PagaMultasRENAINF, PagaTransferencia, PagaLicenciamento, PagaPrimeiroRegistro, PagaTaxasDETRAN, ConsultaIPVA, ConsultaDPVAT, ConsultaMultas, ConsultaLicenciamento, BuscarRecibos |
| **API Gateway BV - PagamentosCartao** | Backend DETRAN/PRODESP | SOAP/HTTPS | Serviço de pagamentos com cartão de crédito. Endpoints: PagaIPVA, PagaDPVAT, PagaMultas, PagaMultasRENAINF, PagaLicenciamento |
| **API Gateway BV - CalcularParcelas** | Backend Financeiro | SOAP/HTTPS | Serviço de cálculo de parcelas com seguro e taxas |
| **API Gateway BV - ConsultaExtrato** | Backend Bancário | SOAP/HTTPS | Serviço de consulta de extrato bancário |
| **OAuth2 Server** | Autenticação | REST/HTTPS | Servidor OAuth2 para obtenção de tokens (grant_type: client_credentials) |
| **Prometheus** | Métricas | HTTP | Coleta de métricas via endpoint /actuator/prometheus (porta 9090) |
| **Grafana** | Dashboards | HTTP | Visualização de métricas e dashboards de monitoramento |
| **Pact Broker** | Contract Testing | HTTP | Servidor de contratos para testes de integração |

**Configurações de Integração:**
- **Proxy Corporativo:** Configurável (host, port, user, password) para acesso aos serviços externos
- **Gateways:** URLs configuradas por ambiente (des, qa, uat, prd) via ConfigMaps Kubernetes
- **Autenticação:** OAuth2 client credentials com CLIENT_ID e CLIENT_SECRET armazenados em Secrets Kubernetes
- **Timeout/Retry:** Configurações gerenciadas pelo Apache Camel
- **WS-Security:** Interceptor customizado (WsSecurityInterceptor) para adicionar headers de segurança

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- **Arquitetura bem definida:** Separação clara em módulos (common, domain, application) seguindo princípios DDD e Arquitetura Hexagonal
- **Padrões de projeto:** Uso adequado de padrões como Repository, Service, Mapper, Factory
- **Mapeamento automatizado:** Uso extensivo de MapStruct reduz código boilerplate e erros de conversão
- **Testes abrangentes:** Boa cobertura de testes unitários com JUnit 5, Mockito e EasyRandom. Testes segregados por tipo (unit, integration, functional, architecture)
- **Tratamento de erros centralizado:** ErrorFormat e exception handlers padronizados
- **Configuração externalizada:** Uso de ConfigMaps e Secrets Kubernetes para configurações sensíveis
- **Observabilidade:** Métricas completas com Micrometer/Prometheus e dashboards Grafana
- **Logging estruturado:** Logs em formato JSON facilitam análise e correlação
- **Contract Testing:** Uso de Pact para validação de contratos de integração
- **Validação arquitetural:** ArchUnit para garantir conformidade com regras arquiteturais
- **Documentação API:** Swagger/OpenAPI para documentação interativa

**Pontos de Melhoria:**
- **Complexidade de mapeamento:** Mappers muito extensos (DebitoVeicularMapper, PagamentoCartaoMapper) com muitas conversões aninhadas, dificultando manutenção
- **Código comentado:** Presença de código comentado (DebitosVeicularesProcessor) que deveria ser removido
- **Duplicação de lógica:** Múltiplos repositórios com lógica similar (PagaIpvaRepositoryImpl, PagaDpvatRepositoryImpl, etc) poderiam ser consolidados
- **Falta de validações de entrada:** Alguns endpoints não validam completamente os dados de entrada antes de processar
- **Documentação inline limitada:** Falta de JavaDoc em algumas classes e métodos importantes
- **Testes de integração:** Embora existam testes unitários, não há evidências de testes de integração end-to-end com os serviços SOAP reais

---

## 14. Observações Relevantes

1. **Padrão ACL (Anti-Corruption Layer):** O sistema atua como camada de isolamento entre APIs REST modernas e sistemas legados SOAP, protegendo o domínio de negócio da complexidade dos sistemas backend.

2. **Multi-tenant:** Suporta dois bancos distintos (Votorantim - 655 e BV - 413) com chaves de acesso e configurações diferenciadas.

3. **Apache Camel:** Uso extensivo de rotas Camel para orquestração de fluxos, permitindo flexibilidade e desacoplamento.

4. **Conversões temporais complexas:** Sistema lida com múltiplos formatos de data/hora (OffsetDateTime, XMLGregorianCalendar, Duration, LocalDate) devido à integração SOAP/REST.

5. **Valores monetários:** Conversão sistemática de centavos (Integer) para BigDecimal nas respostas, garantindo precisão financeira.

6. **Segurança em camadas:** OAuth2 para autenticação, WS-Security para SOAP, JWT para REST, e possibilidade de proxy corporativo.

7. **Infraestrutura cloud-native:** Deploy em Kubernetes (Google Cloud Platform) com ConfigMaps, Secrets, probes de health e recursos de observabilidade.

8. **Profiles por ambiente:** Configurações específicas para local, des, qa, uat e prd, facilitando deploy em múltiplos ambientes.

9. **Interceptors customizados:** TrilhaAuditoriaWSInterceptor para auditoria e WsHeader para customização de headers SOAP.

10. **Namespace principal:** br.com.votorantim.ccbd.base.debitos.veiculares

11. **Portas:** Aplicação (8080), Actuator/Metrics (9090), Prometheus (9060), Grafana (3000)

12. **Limitações conhecidas:** Range de consulta de extrato limitado a 31 dias por restrições do sistema backend.

13. **Dependências críticas:** Sistema depende completamente da disponibilidade dos Web Services SOAP backend (DETRAN/PRODESP).

14. **Estratégia de versionamento:** APIs REST versionadas (v1) permitindo evolução sem quebra de compatibilidade.

15. **Build multi-módulo:** Estrutura Maven facilita reutilização de código e separação de responsabilidades (common, domain, application).

---