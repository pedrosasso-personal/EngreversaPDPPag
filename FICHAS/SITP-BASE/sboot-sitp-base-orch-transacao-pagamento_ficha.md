# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-sitp-base-orch-transacao-pagamento** é um serviço orquestrador (orchestration layer) desenvolvido em Spring Boot que atua como intermediário para consulta de transações de pagamento. O sistema recebe requisições REST, autentica-se via OAuth JWT em um API Gateway, e consome um serviço backend (atom) para listar transações ITP (Internet Transaction Processing) do SPB (Sistema de Pagamentos Brasileiro). Utiliza Apache Camel para orquestração de fluxos e segue arquitetura hexagonal com separação clara entre camadas de domínio, aplicação e infraestrutura.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal Spring Boot, ponto de entrada da aplicação |
| **TransacaoPagamentoController** | Controller REST que expõe endpoint para listar transações |
| **TransacaoPagamentoService** | Serviço de domínio que orquestra o fluxo via Apache Camel |
| **TransacaoPagamentoRouter** | Roteador Camel que define o fluxo de processamento |
| **TransacaoPagamentoProcessor** | Processador Camel que manipula o exchange de mensagens |
| **TransacaoPagamentoRepositoryImpl** | Implementação de repositório que consome API backend |
| **AuthApiGtwRepositoryImpl** | Repositório para autenticação OAuth no API Gateway |
| **TransacaoPagamentoMapper** | Mapeador entre representations e domain objects |
| **CamelContextWrapper** | Wrapper para gerenciamento do contexto Camel |
| **TransacaoPagamentoConfiguration** | Configuração de beans Spring e integração Camel |
| **AdaptableRestTemplateHeaderModifier** | Interceptor para adicionar headers de autenticação |

---

## 3. Tecnologias Utilizadas

- **Spring Boot** (framework principal)
- **Spring Security OAuth2** (autenticação JWT)
- **Apache Camel 3.0.1** (orquestração de fluxos)
- **Swagger/OpenAPI 2.9.2** (documentação de APIs)
- **RestTemplate** (cliente HTTP)
- **ModelMapper** (mapeamento de objetos)
- **Lombok** (redução de boilerplate)
- **JUnit 5** (testes unitários)
- **Mockito** (mocks em testes)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Prometheus/Grafana** (métricas e monitoramento)
- **Logback** (logging com formato JSON)
- **Java 11**

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /atacado/pagamentos/listarTransacoesItp | TransacaoPagamentoController | Lista transações ITP com base em tipo de lançamento e código de grupo produto |

---

## 5. Principais Regras de Negócio

1. **Autenticação obrigatória**: Todas as requisições devem passar por autenticação OAuth JWT via API Gateway
2. **Filtro por tipo de lançamento**: Sistema permite filtrar transações por tipo de lançamento (ex: "S" para saída)
3. **Filtro por grupo de produto**: Permite filtrar por código de grupo de produto específico
4. **Orquestração sequencial**: O fluxo executa autenticação primeiro, depois consulta transações
5. **Propagação de headers**: Headers de autorização são propagados automaticamente para chamadas downstream
6. **Transformação de dados**: Conversão entre formatos de representation (API) e domain (negócio)

---

## 6. Relação entre Entidades

**Entidades principais:**

- **ListarTransacoesItpRequest**: Entidade de entrada contendo `tipoLancamento` (String) e `codigoGrupoProduto` (Integer)
- **ListarTransacoesItpResponse**: Entidade de saída contendo lista de transações
- **Transacao**: Entidade que representa uma transação com `codigoTransacao` (BigDecimal), `nomeTransacao` (String) e `mnemonicoTransacao` (String)
- **AutenticarResponseDomain**: Entidade contendo `accessToken` e `tokenType` para autenticação OAuth

**Relacionamentos:**
- ListarTransacoesItpResponse **contém** lista de Transacao (1:N)
- Não há relacionamentos de persistência, apenas DTOs para comunicação entre camadas

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot (startup) | Configurações da aplicação por ambiente |
| logback-spring.xml | leitura | Logback (runtime) | Configuração de logs em formato JSON |
| swagger/*.json | leitura | Swagger Codegen (build time) | Especificações OpenAPI para geração de código |
| swagger/*.yaml | leitura | Swagger Codegen (build time) | Especificação da API de autenticação OAuth |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| **API Gateway OAuth** | REST/OAuth2 | Autenticação via endpoint `/auth/oauth/v2/token-jwt` para obtenção de token JWT |
| **sboot-sitp-base-atom-consulta-transacao-spb** | REST | Serviço backend que fornece dados de transações SPB via endpoint `/v1/atacado/listarTransacoesItp` |

**Detalhes das integrações:**
- Autenticação: client_credentials OAuth2 flow com client_id e client_secret
- Backend: Comunicação via RestTemplate com autenticação Basic Auth propagada

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões hexagonais (ports/adapters)
- Separação clara entre módulos (application, domain, common)
- Uso adequado de Apache Camel para orquestração
- Boa cobertura de testes unitários
- Configuração adequada de profiles por ambiente
- Uso de Swagger para documentação de APIs
- Implementação de observabilidade (Prometheus/Grafana)

**Pontos de Melhoria:**
- Classe `GenericRepository` com método `logar()` vazio, indicando código incompleto
- Variável `LOG_TYPE` não utilizada em `GenericRepository`
- Testes unitários com muitos `try-catch` genéricos apenas verificando `assertTrue(true)`, o que não valida comportamento real
- Falta de tratamento de exceções específicas em alguns pontos
- Alguns testes mockam objetos mas não validam comportamentos esperados
- Comentários em português misturados com código
- Configuração de segurança poderia ser mais explícita
- Falta documentação inline em pontos críticos do código

---

## 14. Observações Relevantes

1. **Arquitetura Multi-módulo**: O projeto está dividido em 3 módulos Maven (application, domain, common), facilitando manutenção e separação de responsabilidades

2. **Geração de Código**: Utiliza Swagger Codegen para gerar automaticamente clientes REST e interfaces de API a partir de especificações OpenAPI

3. **Ambientes**: Suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas via Spring Profiles

4. **Segurança**: Implementa OAuth2 Resource Server com validação de JWT via JWK endpoint

5. **Observabilidade**: Endpoints Actuator expostos na porta 9090 separada da aplicação (8080), incluindo métricas Prometheus

6. **Deploy**: Preparado para deploy em Kubernetes/OpenShift com configurações de probes (liveness/readiness) e ConfigMaps/Secrets

7. **CI/CD**: Integrado com Jenkins (jenkins.properties) e possui pipeline automatizado

8. **Padrão de Nomenclatura**: Segue convenção `sboot-sitp-base-orch-*` indicando ser um serviço orquestrador da camada base do SITP

9. **Versionamento**: Versão atual 0.6.0, indicando que ainda está em desenvolvimento/evolução

10. **Dependências Corporativas**: Utiliza bibliotecas internas do Banco Votorantim (arqt-base-*) para auditoria, segurança e tratamento de erros