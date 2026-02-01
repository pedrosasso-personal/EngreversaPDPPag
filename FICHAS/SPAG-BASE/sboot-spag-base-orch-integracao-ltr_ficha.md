# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de orquestração para integração de mensagens LTR (Liquidação de Transferências de Recursos) do SPB (Sistema de Pagamentos Brasileiro). O sistema atua como intermediário entre o SPAG (Sistema de Pagamentos) e o SPB, processando mensagens LTR dos tipos 0002, 0004 e 0008, realizando consultas, envios e atualizações de status dessas mensagens.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `IntegracaoLtrService` | Serviço de domínio que orquestra o fluxo de envio e consulta de mensagens LTR |
| `IntegracaoLtrController` | Controlador REST que expõe endpoints para operações com mensagens LTR |
| `IntegracaoLtrRouter` | Roteador Apache Camel que define os fluxos de processamento das mensagens |
| `IntegracaoLtrRepositoryImpl` | Implementação de repositório para comunicação com o sistema SPAG |
| `IntegracaoLTRSPBRepositoryImpl` | Implementação de repositório para comunicação com o sistema SPB |
| `IntegracaoLtrMapper` | Mapper para conversão entre objetos de domínio e representações REST |
| `CamelContextWrapper` | Wrapper do contexto Apache Camel para gerenciamento de rotas |
| `LTR0002`, `LTR0004`, `LTR0008` | Entidades de domínio representando os tipos de mensagens LTR |
| `ExceptionControllerHandler` | Tratador centralizado de exceções da aplicação |

## 3. Tecnologias Utilizadas

- **Framework Principal**: Spring Boot 2.x
- **Linguagem**: Java 11
- **Orquestração**: Apache Camel 3.0.1
- **Segurança**: Spring Security OAuth2, JWT
- **Documentação API**: Swagger/OpenAPI 3.0 (Springfox)
- **Comunicação HTTP**: RestTemplate
- **Serialização**: Jackson, Gson
- **Monitoramento**: Spring Actuator, Prometheus, Grafana
- **Testes**: JUnit 5, Mockito, Rest Assured, Pact
- **Build**: Maven
- **Containerização**: Docker
- **Infraestrutura**: OpenShift (Google Cloud Platform)

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/mensagensLTR/{codigoMensagem}` | IntegracaoLtrController | Consulta mensagens LTR por código (LTR0008, LTR0007, etc.) |
| GET | `/v1/mensagensLTR/erro/{codigoMensagem}` | IntegracaoLtrController | Consulta mensagens de erro LTR por código |
| POST | `/v1/mensagemLTR0008` | IntegracaoLtrController | Envia mensagem LTR0008 para SPAG e SPB |
| POST | `/v1/mensagemLTR0002` | IntegracaoLtrController | Envia mensagem LTR0002 para SPAG e SPB |
| POST | `/v1/mensagemLTR0004` | IntegracaoLtrController | Envia mensagem LTR0004 para SPAG e SPB |

## 5. Principais Regras de Negócio

- **Orquestração de Envio**: Para cada mensagem LTR enviada, o sistema primeiro persiste no SPAG, depois envia ao SPB e, em caso de sucesso, atualiza o número de controle IF no SPAG
- **Tratamento de Falhas**: Em caso de erro no envio ao SPB, o sistema desativa o status da mensagem no SPAG (alteraFlAtivo)
- **Validação de Datas**: Conversão e validação de formatos de data/hora no padrão ISO (yyyy-MM-dd'T'HH:mm:ss)
- **Consulta com Filtros**: Permite consulta de mensagens por código, número de controle IF e intervalo de datas
- **Processamento Assíncrono**: Utiliza Apache Camel para processamento em pipeline das mensagens
- **Autenticação**: Todos os endpoints requerem autenticação via OAuth2/JWT

## 6. Relação entre Entidades

**Entidades Principais:**

- **LTR0008**: Mensagem de confirmação/divergência de liquidação
  - Atributos: ispbLTR, dtHrIF, tpConfDivg, dtMovto, numCtrlLTROr, cnpjInstituicao, siglaSistema

- **LTR0002**: Mensagem de confirmação/divergência com ISPB IF
  - Atributos: ispbLTR, ispbIF, dtHrIF, tpConfDivg, dtMovto, numCtrlLTROr, cnpjInstituicao, siglaSistema

- **LTR0004**: Mensagem de lançamento com valor
  - Atributos: ispbLTR, ispbIF, numCtrlLTROr, vlrLanc, subTpAtv, descAtv, hist, dtMovto, cnpjInstituicao, siglaSistema

**Relacionamentos:**
- Todas as mensagens LTR possuem um `cdProcessamentoLTR` (ID) gerado pelo SPAG
- Após processamento no SPB, recebem um `numCtrlIf` que é atualizado no SPAG
- Compartilham atributos comuns como `cnpjInstituicao`, `siglaSistema`, `dtMovto`

## 7. Estruturas de Banco de Dados Lidas

não se aplica

*Observação: O sistema não acessa diretamente banco de dados. Toda persistência é realizada através de APIs REST dos sistemas SPAG e SPB.*

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

*Observação: O sistema não atualiza diretamente banco de dados. Todas as atualizações são realizadas através de APIs REST dos sistemas SPAG e SPB.*

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Descrição |
|-----------------|----------|-------------------------|-----------|
| application.yml | leitura | Spring Boot | Configurações da aplicação (URLs, portas, profiles) |
| logback-spring.xml | leitura | Logback | Configuração de logs da aplicação |
| sboot-spag-base-orch-integracao-ltr.yml | leitura | Swagger Codegen | Especificação OpenAPI para geração de código |

## 10. Filas Lidas

não se aplica

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

| Sistema | Tipo | Descrição |
|---------|------|-----------|
| SPAG Base Integracao LTR | API REST | Sistema de persistência de mensagens LTR. Endpoints para criar, consultar e atualizar mensagens LTR |
| SPB Base Integracao | API REST | Sistema de Pagamentos Brasileiro. Recebe mensagens LTR para processamento no SPB |
| OAuth2 Server | API REST | Servidor de autenticação para validação de tokens JWT |

**URLs por Ambiente:**
- **DES**: 
  - SPAG: https://sboot-spag-base-atom-integracao-ltr.appdes.bvnet.bv
  - SPB: https://sboot-spbb-base-atom-integracao.appdes.bvnet.bv
- **UAT**: 
  - SPAG: https://sboot-spag-base-atom-integracao-ltr.appuat.bvnet.bv
  - SPB: https://sboot-spbb-base-atom-integracao.appuat.bvnet.bv
- **PRD**: 
  - SPAG: https://sboot-spag-base-atom-integracao-ltr.app.bvnet.bv
  - SPB: https://sboot-spbb-base-atom-integracao.app.bvnet.bv

## 13. Avaliação da Qualidade do Código

**Nota:** 7.5/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (domain, application)
- Uso adequado de padrões como Repository, Service e Controller
- Implementação de testes unitários, integração e funcionais
- Uso de Apache Camel para orquestração de fluxos complexos
- Tratamento centralizado de exceções
- Documentação via Swagger/OpenAPI
- Configuração adequada de monitoramento (Actuator, Prometheus)

**Pontos de Melhoria:**
- Uso misto de Gson e Jackson para serialização (falta de padronização)
- Métodos setters públicos nos repositórios que deveriam ser imutáveis
- Tratamento de exceções genérico em alguns pontos (catch Exception)
- Falta de validações de entrada mais robustas nos controllers
- Código de tratamento de exceções duplicado entre repositórios
- Uso de `lenient()` nos testes Mockito indica possível problema de design
- Falta de constantes para strings mágicas (URLs, mensagens de erro)
- Alguns métodos muito longos que poderiam ser refatorados

## 14. Observações Relevantes

- **Arquitetura Hexagonal**: O projeto segue parcialmente a arquitetura hexagonal com separação clara entre domain e application
- **Apache Camel**: Uso estratégico do Camel para orquestração de fluxos complexos com rollback automático em caso de falha
- **Segurança**: Implementa OAuth2 com JWT para autenticação e autorização
- **Multi-ambiente**: Configuração preparada para múltiplos ambientes (local, des, qa, uat, prd)
- **Observabilidade**: Integração completa com Prometheus e Grafana para monitoramento
- **Containerização**: Preparado para deploy em containers Docker/OpenShift
- **Testes**: Cobertura de testes em múltiplas camadas (unit, integration, functional, pact)
- **Versionamento de API**: Uso de versionamento na URL (/v1/)
- **Padrão de Nomenclatura**: Segue convenções do Banco Votorantim (prefixo sboot-spag-base)