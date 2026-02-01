# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema orquestrador responsável pela recepção de boletos de pagamento. Atua como intermediário entre clientes externos (fintechs/parceiros) e os serviços internos de pagamento de boletos do SPAG (Sistema de Pagamentos). O sistema realiza validações de rollout (verificação de participação), encaminha solicitações de pagamento e retorna protocolos de confirmação.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `RecepcaoBoletoController` | Controlador REST que expõe o endpoint de recepção de boletos |
| `RecepcaoBoletoService` | Serviço de domínio que orquestra o fluxo de rollout e pagamento |
| `RecepcaoBoletoRouter` | Roteador Camel para processamento de rollout |
| `PagamentoBoletoRouter` | Roteador Camel para processamento de pagamento de boletos |
| `BoletoProcessor` | Processador Camel que converte requisições em objetos de boleto |
| `RolloutProcessor` | Processador Camel que prepara dados para verificação de rollout |
| `RecepcaoBoletoRepositoryImpl` | Implementação de repositório para comunicação com serviço atômico de recepção |
| `PagamentoBoletoRepositoryImpl` | Implementação de repositório para comunicação com serviço de pagamento |
| `RecepcaoBoletoExceptionHandler` | Tratador global de exceções da aplicação |
| `CamelContextWrapper` | Wrapper para gerenciamento do contexto Apache Camel |

## 3. Tecnologias Utilizadas

- **Framework Principal**: Spring Boot 2.x
- **Linguagem**: Java 11
- **Integração/Orquestração**: Apache Camel 3.0.1
- **Mapeamento de Objetos**: MapStruct 1.3.1
- **Documentação API**: Swagger/OpenAPI 2.9.2
- **Segurança**: Spring Security OAuth2 (JWT)
- **Monitoramento**: Spring Actuator + Prometheus + Grafana
- **Testes**: JUnit 5, Mockito, Rest Assured, Pact
- **Build**: Maven
- **Containerização**: Docker
- **Orquestração**: OpenShift/Kubernetes
- **Feature Toggle**: ConfigCat (biblioteca customizada BV)

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/recepcao-boleto | RecepcaoBoletoController | Recebe solicitação de pagamento de boleto e retorna protocolo |

## 5. Principais Regras de Negócio

1. **Verificação de Feature Toggle**: Valida se a funcionalidade de modernização BaaS está habilitada antes de processar
2. **Rollout de Participantes**: Verifica se o CPF/CNPJ do remetente está autorizado a participar do sistema de recepção de boletos
3. **Redirecionamento Temporário**: Retorna HTTP 307 (Temporary Redirect) quando feature toggle desabilitado ou participante não autorizado
4. **Validação de Dados**: Valida campos obrigatórios como remetente, favorecido, valores, datas e códigos de transação
5. **Conversão de Protocolo**: Converte número de protocolo de String para Long, tratando erros de conversão
6. **Integração via API**: Marca requisições como integração via API para controle interno
7. **Tratamento de Exceções**: Normaliza exceções de sistemas externos em códigos de retorno padronizados

## 6. Relação entre Entidades

**Entidades Principais:**

- **RecepcaoBoletoRequest**: Requisição de entrada contendo dados do boleto, remetente, favorecido e transação
- **BoletoRequest**: Objeto de domínio para comunicação com serviço de pagamento
- **RolloutRequest**: Objeto para verificação de participação no rollout
- **RolloutResponse**: Resposta indicando se participante está autorizado
- **PagamentoBoletoResponse**: Resposta do serviço de pagamento contendo protocolo
- **RecepcaoBoletoResponse**: Resposta final ao cliente com dados do protocolo

**Relacionamentos:**
- RecepcaoBoletoRequest → (conversão) → BoletoRequest
- RecepcaoBoletoRequest → (extração) → RolloutRequest
- RolloutRequest → (validação) → RolloutResponse
- BoletoRequest → (processamento) → PagamentoBoletoResponse
- PagamentoBoletoResponse → (mapeamento) → RecepcaoBoletoResponse

## 7. Estruturas de Banco de Dados Lidas

não se aplica

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot | Configuração da aplicação por ambiente |
| logback-spring.xml | leitura | Logback | Configuração de logs da aplicação |
| swagger/*.yml | leitura | Swagger Codegen | Especificações OpenAPI para geração de código |

## 10. Filas Lidas

não se aplica

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| sboot-spag-base-atom-recepcao-boleto | REST API | Serviço atômico para verificação de rollout de participantes |
| sboot-spag-base-orch-pagamento-boleto-srv | REST API | Serviço orquestrador de pagamento de boletos |
| ConfigCat | Feature Toggle | Serviço de gerenciamento de feature flags |
| OAuth2/JWT Provider | Autenticação | Provedor de autenticação e autorização via JWT |

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões de Clean Architecture (separação domain/application)
- Uso adequado de Apache Camel para orquestração
- Implementação de mappers com MapStruct
- Tratamento centralizado de exceções
- Testes unitários presentes
- Configuração adequada de profiles por ambiente
- Uso de feature toggles para controle de funcionalidades

**Pontos de Melhoria:**
- Falta de validações mais robustas nos DTOs (uso de Bean Validation)
- Conversão de protocolo com try-catch genérico poderia ser mais específica
- Alguns métodos poderiam ser mais coesos (ex: recepcionarBoleto no controller)
- Falta de documentação JavaDoc em classes críticas
- Testes de integração e funcionais estão vazios/incompletos
- Uso de Lombok sem configuração de delombok para geração de documentação
- Algumas classes de teste com setup complexo indicando possível acoplamento

## 14. Observações Relevantes

1. **Arquitetura Multi-módulo**: Projeto organizado em módulos Maven (common, domain, application) seguindo boas práticas
2. **Infraestrutura como Código**: Possui configurações completas para deploy em OpenShift/Kubernetes
3. **Observabilidade**: Implementa stack completa de monitoramento (Prometheus + Grafana) com dashboards pré-configurados
4. **Segurança**: Utiliza OAuth2 com JWT para autenticação e autorização
5. **Versionamento de API**: Endpoint versionado em /v1/
6. **Ambientes**: Suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas
7. **CI/CD**: Configurado para pipeline Jenkins com propriedades específicas
8. **Padrão de Nomenclatura**: Segue convenção do Banco Votorantim (sboot-spag-base-orch-*)
9. **Geração de Código**: Utiliza Swagger Codegen para gerar clientes REST automaticamente
10. **Testes de Contrato**: Estrutura preparada para testes Pact (consumer-driven contracts)