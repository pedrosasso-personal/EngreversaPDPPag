# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-spag-base-acl-baas-doc-ted-v2** é um serviço de integração (ACL - Anti-Corruption Layer) desenvolvido em Spring Boot que atua como intermediário para operações de transferências bancárias DOC/TED. O sistema recebe requisições REST, processa transferências através de um serviço SOAP legado (DOCTEDTransferenciaBusinessService) e integra com um serviço de notificações (springboot-spag-base-enviar-detalhes) para consulta e reenvio de mensagens. Utiliza Apache Camel para orquestração de fluxos e implementa o padrão de arquitetura hexagonal (ports and adapters).

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot que inicializa a aplicação |
| `BaasDocTedController` | Controlador REST que expõe os endpoints da API |
| `BaasDocTedService` | Serviço de domínio que orquestra as chamadas via Apache Camel |
| `BaasDocTedRouter` | Roteador Apache Camel que define os fluxos de integração |
| `DOCTEDTransferenciaIIBRepositoryImpl` | Implementação do repositório para chamadas SOAP ao serviço legado |
| `EnviarDetalhesRepositoryImpl` | Implementação do repositório para chamadas REST ao serviço de notificações |
| `DOCTEDTransferenciaIIBMapper` | Mapper MapStruct para conversão entre representações e domínio |
| `CamelContextWrapper` | Wrapper do contexto Apache Camel |
| `BaasDocTedConfiguration` | Configuração principal dos beans da aplicação |
| `WSConfiguration` | Configuração de clientes SOAP com segurança WS-Security |
| `RestConfiguration` | Configuração de clientes REST |

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Apache Camel 3.0.1** (orquestração de fluxos)
- **Spring Web Services** (cliente SOAP)
- **Spring Security OAuth2** (autenticação JWT)
- **MapStruct 1.3.1** (mapeamento de objetos)
- **Swagger/OpenAPI 2.9.2** (documentação de API)
- **Lombok** (redução de boilerplate)
- **JUnit 5** (testes unitários)
- **RestAssured** (testes funcionais)
- **Pact** (testes de contrato)
- **Micrometer/Prometheus** (métricas)
- **Logback** (logging)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Kubernetes/OpenShift** (orquestração)

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/baas/pagamentos/transferencia-doc-ted` | `BaasDocTedController.novaTransferencia()` | Cria uma nova transferência DOC/TED |
| GET | `/v1/baas/pagamentos/transferencia-doc-ted/{numProtocolo}` | `BaasDocTedController.consultaTransferencia()` | Consulta detalhes de uma transferência pelo protocolo |
| POST | `/v1/baas/pagamentos/transferencia-doc-ted/{numProtocolo}?action=renviar` | `BaasDocTedController.atualizaTransferencia()` | Solicita reenvio de notificação de uma transferência |

## 5. Principais Regras de Negócio

1. **Validação de Transferências**: O sistema valida dados obrigatórios como CPF/CNPJ do remetente, dados bancários do favorecido, valor da transferência, tipo de conta, etc.

2. **Tipos de Liquidação**: Suporta diferentes códigos de liquidação (31 - TED CIP, 32 - TED STR, 21 - DOC)

3. **Identificação de Fintech**: Permite identificar transferências de clientes de fintechs através do campo `numeroCNPJCPFRemetenteClienteFintech`

4. **Protocolo de Solicitação**: Gera e retorna número de protocolo para rastreamento das transferências

5. **Status de Protocolo**: Retorna código de status (00 = OK, 3 = Sucesso, outros = Erro) e descrição textual

6. **Consulta de Detalhes**: Permite consultar detalhes de transferências através de protocolo e hash de mensagem

7. **Reenvio de Notificações**: Permite solicitar reenvio de notificações para transferências já processadas

8. **Autenticação OAuth2**: Todas as operações requerem token JWT válido

## 6. Relação entre Entidades

**Entidades Principais:**

- **TransacaoRequest**: Representa uma solicitação de transferência contendo:
  - `Remetente`: dados da pessoa/conta origem
  - `Favorecido`: dados da pessoa/conta destino
  - Dados da transação (valor, histórico, códigos, datas)

- **Remetente/Favorecido**: Contêm:
  - `tipo`: tipo de pessoa (F=CPF, J=CNPJ)
  - `nome`: nome da pessoa
  - `documento`: CPF/CNPJ
  - `Conta`: dados bancários

- **Conta**: Contém:
  - `tipo`: tipo de conta (CC=Corrente, CP=Poupança, PG=Pagamento)
  - `banco`: código do banco
  - `agencia`: número da agência
  - `numero`: número da conta

- **TransferenciaResponse**: Resposta da transferência contendo:
  - `numero`: número do protocolo
  - `codigoStatus`: código do status
  - `status`: descrição do status
  - `Links`: links HATEOAS

- **ConsultarRequest/ConsultarResponse**: Para consulta de detalhes
- **ReenvioRequest/ReenvioResponse**: Para reenvio de notificações

## 7. Estruturas de Banco de Dados Lidas

não se aplica

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `application.yml` | leitura | Spring Boot | Arquivo de configuração da aplicação com profiles (local, des, qa, uat, prd) |
| `logback-spring.xml` | leitura | Logback | Configuração de logs da aplicação |
| `*.wsdl` e `*.xsd` | leitura | JAXB/JAX-WS | Definições de contratos SOAP para geração de stubs |
| `*.yaml` e `*.json` (swagger) | leitura | Swagger Codegen | Especificações OpenAPI para geração de código |

## 10. Filas Lidas

não se aplica

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| **DOCTEDTransferenciaBusinessService** | SOAP/WS-Security | Serviço legado IBM IIB para processamento de transferências DOC/TED. Endpoint: `https://servicebus-{env}.bvnet.bv/atacado/pagamentos/DOCTEDTransferenciaBusinessService/v1` |
| **springboot-spag-base-enviar-detalhes** | REST/Basic Auth | Serviço para consulta de detalhes e reenvio de notificações de mensagens. Endpoints: `/v1/buscaDetalheMensagem` e `/v1/solicitaReenvioMensagem` |
| **API Gateway OAuth2** | REST/OAuth2 | Serviço de autenticação JWT. Endpoint: `https://apigateway{env}.bvnet.bv/openid/connect/jwks.json` |

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura hexagonal (domain, application, infrastructure)
- Uso adequado de padrões como Dependency Injection, Repository Pattern e Mapper
- Cobertura de testes unitários presente em todas as camadas
- Uso de tecnologias modernas e consolidadas (Spring Boot, Camel, MapStruct)
- Configuração adequada para múltiplos ambientes
- Documentação OpenAPI/Swagger implementada
- Uso de Lombok para reduzir boilerplate

**Pontos de Melhoria:**
- Alguns métodos auxiliares estáticos (ex: `toSolicitarTransferenciaTEDRequest`) poderiam ser movidos para classes utilitárias ou mappers
- Comentários em código desabilitado encontrados em testes (código morto)
- Falta de tratamento de exceções mais específico em alguns pontos
- Alguns testes unitários com cobertura superficial (apenas verificando `assertNotNull`)
- Classe `Uteis` com apenas um método poderia ser incorporada em outro lugar
- Falta de validações de negócio mais robustas no controller (delegadas ao backend)
- Configurações hardcoded em alguns testes

## 14. Observações Relevantes

1. **Arquitetura Multi-Módulo**: O projeto está organizado em 3 módulos Maven (common, domain, application) seguindo boas práticas de separação de camadas.

2. **Segurança**: Implementa autenticação OAuth2 com JWT e WS-Security para chamadas SOAP, utilizando credenciais armazenadas em secrets do Kubernetes.

3. **Observabilidade**: Possui endpoints Actuator expostos na porta 9090 para health checks e métricas Prometheus.

4. **CI/CD**: Configurado para pipeline Jenkins com propriedades específicas (`jenkins.properties`) e infraestrutura como código (`infra.yml`).

5. **Ambientes**: Suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas via profiles Spring.

6. **Trilha de Auditoria**: Integra com biblioteca corporativa `springboot-arqt-base-trilha-auditoria-web` para auditoria de chamadas.

7. **Testes**: Possui estrutura completa de testes (unit, integration, functional) com suporte a testes de arquitetura via ArchUnit.

8. **Containerização**: Dockerfile otimizado usando OpenJ9 JVM com configurações de memória ajustáveis.

9. **Padrão de Nomenclatura**: Segue convenções do Banco Votorantim com prefixos `sboot-spag-base-acl`.

10. **Versionamento**: Projeto na versão 0.2.0, indicando fase de desenvolvimento/estabilização.