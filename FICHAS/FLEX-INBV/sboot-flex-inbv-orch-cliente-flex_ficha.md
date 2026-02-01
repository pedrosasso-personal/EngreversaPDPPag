# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de integração para gerenciamento de clientes no FlexCube, desenvolvido em Java com Spring Boot e Apache Camel. O sistema expõe APIs REST para consulta e cadastro de clientes (Pessoa Física e Pessoa Jurídica), integrando-se com o core bancário FlexCube via SOAP Web Services. Utiliza arquitetura hexagonal (ports and adapters) e implementa roteamento de mensagens através do Apache Camel para orquestração de chamadas aos serviços externos.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal Spring Boot, inicializa a aplicação com @EnableResourceServer |
| **ClienteFlexController** | Controlador REST que expõe endpoints para consulta e manutenção de clientes |
| **ClienteFlexService** | Serviço de domínio que orquestra operações de negócio, validações e integração via Camel |
| **ClienteFlexRouter** | Define rotas Apache Camel para orquestração de chamadas aos serviços externos |
| **ClienteFlexRepositoryImpl** | Implementação do repositório para operações SOAP com FlexCube (query e insert) |
| **ClientFlexRepositoryRequestImpl** | Orquestra criação de clientes PF/PJ, delegando para mappers específicos |
| **MapeamentoDominioRepositoryImpl** | Consulta mapeamentos de domínio via SOAP |
| **CreateCustomerPFMapper** | Mapeia ClienteFlex (PF) para estrutura SOAP CustomerFullType do FlexCube |
| **CreateCustomerPJMapper** | Mapeia ClienteFlex (PJ) para estrutura SOAP CustomerCreateIOType do FlexCube |
| **QueryCustomerMapper** | Mapeia resposta SOAP CustomerFullType para entidade de domínio ClienteFlex |
| **WebServiceConnector** | Estende WebServiceTemplate para logging de requisições/respostas SOAP |
| **CamelContextWrapper** | Wrapper para CamelContext, gerencia inicialização de rotas e templates |
| **ClienteFlex** | Entidade de domínio representando cliente com dados PF/PJ, endereços e telefones |

---

## 3. Tecnologias Utilizadas

- **Java 11** (OpenJ9)
- **Spring Boot** (framework principal)
- **Spring Security** (OAuth2 Resource Server com JWT)
- **Apache Camel** (orquestração e roteamento de mensagens)
- **Spring Web Services** (cliente SOAP)
- **WS-Security** (UsernameToken para autenticação SOAP)
- **Swagger/OpenAPI** (documentação de APIs)
- **Caelum Stella** (validação CPF/CNPJ)
- **Mockito** (testes unitários)
- **RestAssured** (testes funcionais)
- **Pact** (testes de contrato)
- **Kubernetes** (orquestração de containers)
- **Docker** (containerização)
- **Actuator** (health checks e métricas)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/cliente/codigoCliente/{codigoCliente}` | ClienteFlexController | Consulta cliente por código no FlexCube |
| GET | `/cliente` (header: numeroCpfCnpj) | ClienteFlexController | Consulta cliente por CPF ou CNPJ |
| POST | `/cliente` | ClienteFlexController | Cadastra novo cliente (PF ou PJ) no FlexCube |

---

## 5. Principais Regras de Negócio

- **Validação de CPF/CNPJ**: Utiliza biblioteca Caelum Stella para validar formato e dígitos verificadores (11 dígitos para CPF, 14 para CNPJ)
- **Diferenciação PF/PJ**: Sistema identifica tipo de cliente pelo tamanho do documento (CPF=11, CNPJ=14) e direciona para mapper apropriado
- **Validação de Duplicidade**: Antes de inserir cliente, verifica se CPF/CNPJ já existe no FlexCube via queryCustCPFCNPJ
- **Conversão Estado Civil**: Mapeia códigos FlexCube (S, C, D, V) para descrições (Solteiro, Casado, Divorciado, Viúvo)
- **Validação de Dados Obrigatórios**: CreateCustomerPFMapper valida presença de documento e ausência de dados PJ; CreateCustomerPJMapper valida ausência de dados PF
- **Mapeamento de Domínios**: Consulta serviço de mapeamento de domínios para obter configurações e valores válidos
- **Tratamento de Exceções**: Converte exceções técnicas (FlexCubeException) em exceções de domínio (ClienteFlexException, DomainException)

---

## 6. Relação entre Entidades

**ClienteFlex** (entidade principal de domínio)
- Contém dados de Pessoa Física (PF) ou Pessoa Jurídica (PJ) - mutuamente exclusivos
- Possui lista de **Endereços** (residencial, comercial, etc)
- Possui lista de **Telefones** (residencial, comercial, celular)
- Possui dados de **Imóvel** (para PF)
- Possui dados de **Emprego** e **Renda** (para PF)
- Possui dados de **Faturamento** (para PJ)

**Dominio**
- Representa mapeamento de propriedades de domínio (Map<String, Object>)
- Utilizado para configurações e valores válidos do sistema

**Relacionamento com FlexCube**:
- ClienteFlex ↔ CustomerFullType (SOAP - PF)
- ClienteFlex ↔ CustomerCreateIOType (SOAP - PJ)

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

*Observação: O sistema não acessa diretamente banco de dados. Toda persistência é realizada através de Web Services SOAP do FlexCube.*

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

*Observação: O sistema não atualiza diretamente banco de dados. Toda persistência é realizada através de Web Services SOAP do FlexCube.*

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | ApplicationProperties | Arquivo de configuração com profiles (local, des, uat, prd), endpoints SOAP, credenciais e configurações de logging |
| cacerts | Leitura | Configuração K8s (volumes) | Certificados SSL/TLS montados como volume no container |
| Logs de aplicação | Gravação | WebServiceConnector, classes gerais | Logs de requisições/respostas SOAP e eventos da aplicação |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **FlexCube - FCUBSCustomerService** | SOAP Web Service | Core bancário para operações de cliente (CreateCustomer, QueryCustomer, ModifyCustomer). Autenticação via WS-Security UsernameToken |
| **MapeamentoDominiosTechinicalService** | SOAP Web Service | Serviço para consulta de mapeamentos de domínio e configurações (obterDominio, listarDominios) |
| **OAuth2/JWT** | Autenticação | Servidor de autorização para validação de tokens JWT nos endpoints REST |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrão hexagonal (ports and adapters)
- Separação clara de responsabilidades entre camadas (controller, service, repository, mapper)
- Uso adequado de padrões de projeto (Strategy para mappers PF/PJ, Wrapper para CamelContext)
- Boa cobertura de testes (unitários, integração com Pact, funcionais com RestAssured)
- Configuração externalizada e suporte a múltiplos ambientes
- Tratamento estruturado de exceções com conversão entre camadas
- Documentação de API com Swagger/OpenAPI
- Uso de bibliotecas consolidadas (Caelum Stella para validação)

**Pontos de Melhoria:**
- Falta de documentação JavaDoc em algumas classes críticas
- Configuração de segurança desabilitada para endpoints específicos pode ser um risco
- Logs de requisições/respostas SOAP completas podem expor dados sensíveis
- Ausência de cache para consultas de mapeamento de domínio (possível otimização)
- Configurações hardcoded em alguns enums (ValoresInterfaceEnum)

---

## 14. Observações Relevantes

1. **Segurança**: O sistema utiliza OAuth2 Resource Server com JWT, mas desabilita segurança para os endpoints `/cliente` e `/cliente/codigoCliente/{codigoCliente}` através do SecurityConfiguration. Isso pode representar um risco de segurança e deve ser revisado.

2. **Orquestração com Camel**: O uso do Apache Camel para orquestração é interessante, mas adiciona complexidade. As rotas Camel (consultarClientePorCodigo, consultarClientePorCPFCNPJ, inserirCliente) coordenam chamadas sequenciais aos serviços de mapeamento de domínio e FlexCube.

3. **Profiles de Ambiente**: Sistema bem preparado para múltiplos ambientes (local, des, uat, prd) com configurações específicas em application.yml e infra.yml (Kubernetes).

4. **Logging SOAP**: A classe WebServiceConnector registra todas as requisições e respostas SOAP via marshalling, o que é útil para debug mas pode impactar performance e expor dados sensíveis em produção.

5. **Validação de Duplicidade**: Antes de inserir um cliente, o sistema valida se o CPF/CNPJ já existe através de consulta prévia, evitando duplicações no FlexCube.

6. **Containerização**: Aplicação containerizada com Docker, configurada para Kubernetes com probes de liveness/readiness via Actuator, garantindo alta disponibilidade.

7. **Memória JVM**: Configuração conservadora de memória (Xms64m Xmx128m) adequada para microserviços, mas pode precisar ajuste conforme carga.

8. **Testes de Contrato**: Uso de Pact para testes de integração demonstra maturidade na garantia de compatibilidade entre serviços.