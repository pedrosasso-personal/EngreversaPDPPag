# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-spag-base-acl-baas-boleto** é um serviço de integração (ACL - Anti-Corruption Layer) desenvolvido em Spring Boot que atua como intermediário para processar pagamentos de boletos bancários. Ele recebe requisições REST, transforma os dados e encaminha para um serviço SOAP legado (SolicitarPagamentoBoletoBusinessService) através do barramento de serviços (ESB). O sistema utiliza Apache Camel para orquestração de fluxos e implementa o padrão de arquitetura hexagonal (ports and adapters), separando as camadas de domínio, aplicação e infraestrutura.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal Spring Boot que inicializa a aplicação e habilita o Resource Server OAuth2 |
| **BaasBoletoController** | Controlador REST que expõe o endpoint de pagamento de boleto |
| **BaasBoletoService** | Serviço de domínio que orquestra o fluxo de pagamento utilizando Apache Camel |
| **BaasBoletoRouter** | Roteador Camel que define o fluxo de processamento da solicitação |
| **SolicitarPagamentoBoletoIIBRepository** | Interface de porta (port) que define o contrato de integração |
| **SolicitarPagamentoBoletoIIBRepositoryImpl** | Implementação da integração com o serviço SOAP usando WebServiceTemplate |
| **SolicitarPagamentoBoletoIIBMapper** | Mapper MapStruct para conversão entre representações e domínio |
| **CamelContextWrapper** | Wrapper que encapsula o contexto do Apache Camel |
| **BaasBoletoConfiguration** | Configuração Spring que define os beans do sistema |
| **WSConfiguration** | Configuração de Web Services (SOAP) com interceptadores de segurança |
| **Pagamento/PagamentoRequest/Protocolo** | Entidades de domínio que representam os dados de pagamento |

---

## 3. Tecnologias Utilizadas

- **Spring Boot** (framework principal)
- **Apache Camel 3.0.1** (orquestração e roteamento de mensagens)
- **Spring Web Services** (cliente SOAP)
- **MapStruct 1.3.1** (mapeamento objeto-objeto)
- **Swagger/OpenAPI 2.9.2** (documentação de API)
- **Spring Security OAuth2** (autenticação e autorização JWT)
- **Lombok** (redução de boilerplate)
- **JAX-WS/JAXB** (binding XML para SOAP)
- **Logback** (logging)
- **Micrometer/Prometheus** (métricas)
- **JUnit 5** (testes unitários)
- **REST Assured** (testes funcionais)
- **Pact** (testes de contrato)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **OpenShift/Kubernetes** (orquestração de containers)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/baas/pagamentos/boleto | BaasBoletoController | Solicita o pagamento de um boleto bancário |

---

## 5. Principais Regras de Negócio

1. **Validação de Dados Obrigatórios**: O sistema valida campos obrigatórios como CNPJ do remetente, dados bancários, valor do pagamento, linha digitável do boleto, etc.

2. **Transformação de Formato de Data**: Converte datas do formato String para XMLGregorianCalendar para compatibilidade com o serviço SOAP.

3. **Enriquecimento de Dados**: Adiciona valores fixos como tipoLancamento="S" e codigoLiquidacao=22 conforme regras de negócio.

4. **Autenticação WS-Security**: Aplica autenticação username/password no header SOAP através de interceptadores.

5. **Trilha de Auditoria**: Propaga informações de auditoria (ticket, sistema origem, usuário, IP) através dos headers SOAP.

6. **Tratamento de Protocolo**: Retorna protocolo de solicitação com código de status e número de protocolo gerado pelo sistema legado.

---

## 6. Relação entre Entidades

**Entidades de Domínio:**

- **PagamentoRequest**: Entidade de entrada contendo todos os dados necessários para solicitar um pagamento de boleto (dados do remetente, favorecido, boleto, valores, etc.)

- **Pagamento**: Entidade de resposta contendo o protocolo da solicitação

- **Protocolo**: Entidade que encapsula o resultado da operação (número do protocolo, código de status, descrição do status)

**Relacionamento:**
```
PagamentoRequest (1) ---> (1) Pagamento
Pagamento (1) ---> (1) Protocolo
```

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
| logback-spring.xml | leitura | /usr/etc/log (runtime) | Arquivo de configuração de logs, montado via ConfigMap |
| application.yml | leitura | classpath (application) | Arquivo de configuração da aplicação Spring Boot |
| SolicitarPagamentoBoletoBusinessService*.wsdl | leitura | classpath/wsdl (build time) | Definições WSDL do serviço SOAP consumido |
| *.xsd | leitura | classpath/wsdl (build time) | Schemas XML para validação e geração de classes JAXB |

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
| **SolicitarPagamentoBoletoBusinessService** | SOAP/ESB | Serviço legado no barramento (IIB/ESB) que processa efetivamente o pagamento de boletos. Endpoint: https://servicebus-{env}.bvnet.bv/atacado/prodServicoPagamentoBoletoCobranca/SolicitarPagamentoBoletoBusinessService/v1 |
| **API Gateway OAuth2** | REST/JWT | Serviço de autenticação e autorização que valida tokens JWT. Endpoint: https://apigateway{env}.bvnet.bv/openid/connect/jwks.json |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura hexagonal (domain, application, infrastructure)
- Uso adequado de padrões como Mapper, Repository, Service
- Configuração externalizada e suporte a múltiplos ambientes
- Implementação de segurança OAuth2/JWT
- Documentação OpenAPI/Swagger
- Estrutura de testes (unit, integration, functional)
- Uso de Lombok para reduzir boilerplate
- Containerização com Docker

**Pontos de Melhoria:**
- Classes de teste vazias (BaasBoletoConfigurationTest, BaasBoletoControllerTest, BaasBoletoServiceTest)
- Falta de tratamento de exceções mais robusto e específico
- Método auxiliar `toSolicitarPagamentoBoletoCobranca` muito extenso e poderia ser refatorado
- Comentários em português misturados com código em inglês
- Falta de validações de entrada mais detalhadas
- Ausência de logs estruturados em JSON (comentado no logback)
- Pouca cobertura de testes implementada

---

## 14. Observações Relevantes

1. **Padrão ACL (Anti-Corruption Layer)**: O sistema implementa o padrão ACL para isolar o domínio moderno (REST/JSON) do sistema legado (SOAP/XML).

2. **Apache Camel**: Utiliza Camel para orquestração, mas de forma relativamente simples - poderia ser substituído por código Spring direto, reduzindo complexidade.

3. **Segurança**: Implementa WS-Security para o SOAP e OAuth2/JWT para o REST, garantindo segurança em ambas as pontas.

4. **Multi-ambiente**: Suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas.

5. **Observabilidade**: Integra com Prometheus para métricas e possui endpoints Actuator para health checks.

6. **Infraestrutura como Código**: Possui arquivo infra.yml para deploy em OpenShift/Kubernetes.

7. **Versionamento de API**: Utiliza versionamento na URL (/v1/).

8. **Dependências Corporativas**: Utiliza bibliotecas internas do Banco Votorantim (arqt-base-*) para padronização.