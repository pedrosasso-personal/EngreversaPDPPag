# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema orquestrador para geração de boletos de cobrança do tipo "cash-in" no contexto de banco digital. O sistema recebe requisições REST para emissão de boletos, consulta dados cadastrais do beneficiário, orquestra a geração do boleto através de serviços atômicos e possui integração preparada com serviços de cobrança via SOAP. Utiliza Apache Camel para roteamento de mensagens entre os componentes.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot que inicializa a aplicação com segurança OAuth2 |
| `BoletoCashInController` | Controller REST que expõe o endpoint de geração de boleto, valida autenticação e trata erros |
| `GerarBoletoCashInService` / `GerarBoletoCashInServiceImpl` | Serviço de domínio que orquestra a geração do boleto, consultando dados cadastrais e delegando para repositórios |
| `BoletoCashInRepositoryImpl` | Repositório que integra com serviço atômico de geração de boleto via REST |
| `DadosCadastraisPessoaRepositoryImpl` | Repositório que consulta dados cadastrais de pessoa via REST |
| `BoletoCobrancaRepositoryImpl` | Repositório preparado para integração SOAP com serviço de cobrança (não implementado) |
| `GerarBoletoCashInRouter` | Rota Camel para processamento de geração de boleto |
| `DadosCadastraisPessoaRouter` | Rota Camel para consulta de dados cadastrais |
| `CamelContextWrapper` | Wrapper do contexto Camel para gerenciamento de rotas e templates |
| `BoletoDomain` | Entidade de domínio representando o boleto completo |
| `GerarBoletoCashInRequestMapper` / `GerarBoletoCashInResponseMapper` | Mapeadores entre representações REST e domínio |

## 3. Tecnologias Utilizadas

- **Framework principal**: Spring Boot 2.x
- **Linguagem**: Java 11
- **Roteamento/Integração**: Apache Camel 3.0.1
- **Segurança**: Spring Security OAuth2 (Resource Server) com JWT
- **Documentação API**: Swagger/OpenAPI 2.0 (Springfox 2.9.2)
- **Comunicação REST**: RestTemplate com segurança integrada
- **Comunicação SOAP**: Spring Web Services com WSS4J 2.2.2
- **Monitoramento**: Spring Actuator + Micrometer + Prometheus
- **Logging**: Logback com formato JSON
- **Testes**: JUnit 5, Rest Assured, Pact (testes de contrato)
- **Build**: Maven 3.3+
- **Containerização**: Docker (OpenJDK 11 com OpenJ9)
- **Orquestração**: Kubernetes/OpenShift (Google Cloud Platform)

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/banco-digital/contas/boletos/cashin` | `BoletoCashInController` | Gera um novo boleto cash-in para uma conta específica. Requer headers: codigoBanco, numeroAgencia, numeroConta. Autenticação OAuth2 obrigatória. |

## 5. Principais Regras de Negócio

1. **Autenticação obrigatória**: Todos os endpoints requerem autenticação OAuth2 com scope 'openid'
2. **Validação de conta**: O sistema valida se a conta informada (banco, agência, conta) é válida antes de gerar o boleto
3. **Enriquecimento de dados**: Antes de gerar o boleto, o sistema consulta dados cadastrais completos do beneficiário (CPF) para preencher informações como endereço, tipo de pessoa, etc.
4. **Mapeamento de dados cadastrais**: Os dados do beneficiário são obtidos de serviço externo e mapeados para o formato esperado pelo serviço de geração de boleto
5. **Dados do pagador**: O sistema define dados fixos para o pagador (tipo "J", documento "11111111111", nome "João") - aparentemente para fins de teste ou placeholder
6. **Tratamento de erros**: Erros de conta inválida retornam HTTP 422 com código "CONTA_INVALIDA"; outros erros retornam HTTP 500
7. **Orquestração via Camel**: A comunicação entre componentes é orquestrada através de rotas Apache Camel para desacoplamento

## 6. Relação entre Entidades

**Entidades principais do domínio:**

- **BoletoDomain**: Entidade raiz representando o boleto completo
  - Contém: numeroConvenio, codigoBanco, numeroAgencia, numeroConta, tipoConta
  - Relacionamento 1:1 com StatusBoletoDomain (status do boleto)
  - Relacionamento 1:1 com ClienteDomain (beneficiario)
  - Relacionamento 1:1 com ClienteDomain (pagador)

- **ClienteDomain**: Representa beneficiário ou pagador
  - Contém: codigo, tipo, documento, nome
  - Relacionamento 1:1 com EnderecoClienteDomain (endereco)
  - Relacionamento 1:1 com TituloBoletoDomain (titulo) - apenas para pagador

- **TituloBoletoDomain**: Dados do título do boleto
  - Contém: valor, dataVencimento, nossoNumero, seuNumero, linhaDigitavel

- **EnderecoClienteDomain**: Endereço do cliente
  - Contém: logradouro, bairro, cidade, uf, cep

**DTOs de integração:**

- **ObterDadosCadastraisResponseDTO**: DTO complexo com dados cadastrais completos da pessoa
  - Contém listas de: telefones, enderecosEletronicos, enderecos
  - Relacionamentos 1:N com TelefoneDTO, EnderecoEletronicoDTO, EnderecoDTO

## 7. Estruturas de Banco de Dados Lidas

não se aplica

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação (leitura/gravação) | Local/Classe Responsável | Breve Descrição |
|-----------------|----------------------------|-------------------------|-----------------|
| `application.yml` | Leitura | Spring Boot / AppProperties | Arquivo de configuração principal com URLs de serviços, perfis de ambiente e configurações de segurança |
| `logback-spring.xml` | Leitura | Logback | Configuração de logs em formato JSON para stdout, com níveis configuráveis por pacote |
| `sboot-ccbd-base-orch-boleto-cash-in.yaml` | Leitura | Swagger Codegen Plugin | Especificação OpenAPI 2.0 usada para gerar interfaces REST e representações |
| `BoletoCobrancaPropriaBusinessServiceContract*.wsdl` | Leitura | JAX-WS Maven Plugin | WSDLs do serviço SOAP de cobrança (DES, UAT, PRD) usados para gerar classes cliente |
| `infra.yml` | Leitura | Pipeline CI/CD | Configuração de infraestrutura como código para deploy em Kubernetes/OpenShift |

## 10. Filas Lidas

não se aplica

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| `sboot-ccbd-base-atom-boleto-cash-in` | REST (POST) | Serviço atômico de geração de boleto cash-in. Recebe dados do boleto e retorna boleto gerado com nosso número e linha digitável |
| `sboot-vucl-base-atom-dados-cadastrais-pessoa` | REST (GET) | Serviço de consulta de dados cadastrais completos de pessoa física/jurídica por CPF/CNPJ |
| `BoletoCobrancaPropriaBusinessService` | SOAP | Serviço de cobrança própria (operações: incluirBoletoCobranca, alterarBoletoCobranca) - integração preparada mas não implementada |
| OAuth2 Authorization Server | OAuth2/JWT | Servidor de autenticação para validação de tokens JWT (api-digitaldes.bancovotorantim.com.br) |

**Observação**: As URLs dos serviços são configuráveis por ambiente (DES, QA, UAT, PRD) através de variáveis de ambiente.

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com módulos domain e application
- Uso adequado de padrões como Repository, Service e Mapper
- Configuração externalizada e preparada para múltiplos ambientes
- Uso de Apache Camel para desacoplamento de integrações
- Documentação OpenAPI bem estruturada
- Segurança OAuth2 implementada
- Observabilidade com Actuator e Prometheus
- Testes estruturados em functional, integration e unit

**Pontos de Melhoria:**
- Classes de teste vazias (BoletoCashInConfigurationTest, BoletoCashInControllerTest, BoletoCashInServiceTest)
- Dados hardcoded do pagador no serviço (documento "11111111111", nome "João")
- Integração SOAP com BoletoCobranca preparada mas não implementada
- Falta tratamento de exceções mais granular (catch genérico de Exception)
- Falta validação de entrada mais robusta (ex: valores nulos, formatos)
- Logs poderiam ser mais descritivos em alguns pontos
- Ausência de testes de contrato implementados (apenas estrutura)
- Comentários de código ausentes em lógicas mais complexas

## 14. Observações Relevantes

1. **Arquitetura Multi-Módulo**: O projeto segue arquitetura hexagonal com separação clara entre domain (lógica de negócio) e application (infraestrutura)

2. **Ambiente de Execução**: Sistema preparado para rodar em Kubernetes/OpenShift na Google Cloud Platform, com configurações específicas por ambiente

3. **Segurança**: Utiliza JWT com validação via JWKS endpoint do servidor OAuth2 do Banco Votorantim

4. **Monitoramento**: Endpoints de health e métricas expostos na porta 9090 (separada da aplicação na 8080)

5. **Pipeline CI/CD**: Configurado para Jenkins com propriedades específicas (jenkins.properties) e tecnologia springboot-ocp

6. **Padrão de Nomenclatura**: Segue convenção do banco com prefixos sboot-ccbd-base-orch (Spring Boot, CCBD, Base, Orquestrador)

7. **Versionamento de API**: API versionada em v1 no path

8. **Trilha de Auditoria**: Integração com biblioteca proprietária de auditoria (springboot-arqt-base-trilha-auditoria-web)

9. **Limitações Identificadas**: 
   - Serviço de cobrança SOAP não está funcional
   - Dados do pagador estão mockados
   - Testes automatizados não implementados completamente

10. **Dependências Proprietárias**: Forte dependência de bibliotecas internas do Banco Votorantim (arqt-base-*)