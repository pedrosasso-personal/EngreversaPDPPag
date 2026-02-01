# Ficha Técnica do Sistema

## 1. Descrição Geral
O sistema **sboot-saca-scco-acl-boleto** é um serviço ACL (Anti-Corruption Layer) desenvolvido em Spring Boot que atua como intermediário entre sistemas internos e um serviço SOAP legado de gestão de boletos bancários. O sistema expõe APIs REST modernas que consomem e transformam dados de/para o serviço SOAP backend, implementando operações como registro, consulta, confirmação e baixa de boletos.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal que inicializa a aplicação Spring Boot |
| `BoletoController` | Controlador REST que expõe os endpoints da API de boletos |
| `BoletoService` | Serviço de domínio que orquestra as operações de boleto via Apache Camel |
| `BoletoRepository` | Interface de porta (Hexagonal Architecture) para acesso aos dados de boleto |
| `BoletoRepositoryImpl` | Implementação do repositório que integra com o serviço SOAP |
| `AclMapper` | Mapper (MapStruct) responsável por conversões entre representações REST e domínio |
| `BoletoRouter` | Roteador Apache Camel que define os fluxos de processamento |
| `BoletoConfiguration` | Configuração Spring dos beans do sistema |
| `WSConfiguration` | Configuração do cliente SOAP (WebServiceTemplate) |
| `ExceptionHandlerConfig` | Tratamento centralizado de exceções da API |
| `ThrowExceptionProcessor` | Processador Camel para tratamento de exceções |

## 3. Tecnologias Utilizadas
- **Spring Boot 2.x** (framework base)
- **Java 11** (linguagem e runtime)
- **Apache Camel 3.0.1** (integração e roteamento)
- **Spring Web Services** (cliente SOAP)
- **MapStruct 1.4.1** (mapeamento de objetos)
- **Lombok** (redução de boilerplate)
- **Micrometer/Prometheus** (métricas e observabilidade)
- **Springfox/Swagger 3.0.0** (documentação OpenAPI)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Grafana + Prometheus** (monitoramento)
- **JUnit 5 + Mockito** (testes)
- **REST Assured** (testes funcionais)
- **Pact** (testes de contrato)

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /confirmarRegistroBoleto | BoletoController | Confirma se o boleto foi registrado |
| POST | /listarRegistroBoleto | BoletoController | Lista os registros de boletos |
| POST | /listarStatusBoleto | BoletoController | Retorna o status dos boletos |
| POST | /obterConvenioBoleto | BoletoController | Obtém dados do convênio do boleto |
| POST | /solicitarBaixaRegistroBoleto | BoletoController | Registra a baixa de um boleto |
| POST | /solicitarRegistroBoleto | BoletoController | Registra um novo boleto |

## 5. Principais Regras de Negócio
- **Transformação de dados**: Conversão entre modelo REST moderno e modelo SOAP legado
- **Validação de registro**: Confirmação de registro de boleto com tratamento de rejeições
- **Gestão de status**: Controle de estados do boleto (registrado, baixado, negado)
- **Tratamento de erros**: Captura e transformação de exceções SOAP em respostas REST padronizadas
- **Autenticação SAML2**: Segurança na comunicação com o serviço backend via WS-Security
- **Auditoria**: Trilha de auditoria integrada nas chamadas SOAP

## 6. Relação entre Entidades

**Entidades principais do domínio:**

- **BoletoResponseDomain**: Entidade central contendo todos os dados de um boleto
  - Relaciona-se com `RegistroBoleto` (status do registro)
  - Relaciona-se com `VeiculoLegal` (veículo legal)
  - Relaciona-se com `ContratoDadosBasicos` (dados do contrato)
  - Relaciona-se com `Carteira` (carteira bancária)
  - Relaciona-se com `Convenio` (convênio)
  - Relaciona-se com `PessoaPagador` (dados do pagador)
  - Relaciona-se com `Conta` (conta de cobrança)

- **Conta**: Relaciona-se com `TipoConta`, `Agencia` e `SituacaoConta`
- **Agencia**: Relaciona-se com `Banco`
- **RegistroBoleto**: Relaciona-se com `ListaMotivoRegistroNegado`
- **ContratoInfo**: Contém dados completos do contrato incluindo `Multa` e `PessoaPagador`

## 7. Estruturas de Banco de Dados Lidas

não se aplica

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot (resources) | Configurações da aplicação por ambiente |
| logback-spring.xml | leitura | Logback (resources ou /usr/etc/log) | Configuração de logs |
| BoletoEndpointService.wsdl | leitura | WSConfiguration (resources/wsdl) | Contrato SOAP do serviço backend |
| sboot-saca-scco-acl-boleto.yaml | leitura | OpenAPI Generator | Especificação OpenAPI dos endpoints |

## 10. Filas Lidas

não se aplica

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| BoletoEndpointService (SOAP) | Serviço Web SOAP | Serviço legado de gestão de boletos (saca-scco-webservice-registro-was-ws) hospedado em diferentes ambientes (des/qa/uat/prd) |
| API Gateway OAuth2 | Autenticação | Validação de tokens JWT para autenticação das requisições REST |
| LDAP BVNet | Autenticação | Integração com LDAP corporativo para autenticação |

## 13. Avaliação da Qualidade do Código

**Nota: 7.5/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões hexagonais (ports/adapters)
- Separação clara de responsabilidades em módulos (application, domain, common)
- Uso adequado de frameworks modernos (Spring Boot, Camel, MapStruct)
- Boa cobertura de testes (unitários, integração, funcionais)
- Configuração de observabilidade (Prometheus, Grafana)
- Uso de Lombok para reduzir boilerplate
- Documentação OpenAPI/Swagger
- Tratamento centralizado de exceções

**Pontos de Melhoria:**
- Falta de documentação JavaDoc nas classes principais
- Alguns testes unitários estão vazios ou incompletos (ex: BoletoServiceTest)
- Configurações sensíveis (senhas) expostas em arquivos de configuração
- Falta de validações de entrada mais robustas nos endpoints
- Código de infraestrutura (BoletoRepositoryImpl) com lógica de logging repetitiva
- Ausência de cache para otimizar chamadas ao serviço SOAP
- Falta de circuit breaker para resiliência nas integrações

## 14. Observações Relevantes

- O sistema utiliza **Apache Camel** como motor de integração, o que adiciona uma camada de complexidade mas permite roteamento flexível e processamento de mensagens
- A arquitetura modular (multi-módulo Maven) facilita a manutenção e evolução independente dos componentes
- O projeto está preparado para **deployment em OpenShift/Kubernetes** (infra-as-code com ConfigMaps e Secrets)
- Há configuração completa de **CI/CD** (jenkins.properties) e **containerização** (Dockerfile)
- O sistema implementa **trilha de auditoria** através de interceptadores customizados nas chamadas SOAP
- A segurança é implementada em múltiplas camadas: OAuth2/JWT na API REST e SAML2/WS-Security no SOAP
- O projeto segue padrões corporativos do Banco Votorantim (parent POM arqt-base-master-springboot)
- Existe infraestrutura completa de **observabilidade local** com Docker Compose (Prometheus + Grafana)