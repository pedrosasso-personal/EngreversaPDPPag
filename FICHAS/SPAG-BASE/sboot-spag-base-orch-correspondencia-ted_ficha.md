# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-spag-base-orch-correspondencia-ted** é um serviço orquestrador (orchestrator) desenvolvido em Spring Boot que realiza a correspondência de TEDs (Transferências Eletrônicas Disponíveis) entre dois sistemas: PGFT (Plataforma de Gestão Financeira e Tesouraria) e SPAG (Sistema de Pagamentos). 

O componente busca TEDs no PGFT que ainda não foram correspondidos no SPAG, baseando-se em um código de lançamento máximo, e insere essas correspondências na base do SPAG para posterior análise e tratamento. O processamento é orquestrado através do Apache Camel, seguindo uma arquitetura de rotas bem definida.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application.java` | Classe principal Spring Boot que inicializa a aplicação |
| `CorrespondenciaTedController.java` | Controller REST que expõe o endpoint de inclusão de correspondências |
| `CorrespondenciaTedService.java` | Serviço de domínio que inicia o processamento via Apache Camel |
| `InclusaoTedService.java` | Serviço responsável por inserir as correspondências no SPAG |
| `CorrespondenciaTedRouter.java` | Define as rotas Apache Camel para orquestração do fluxo |
| `CorrespondenciaTedRepositoryImpl.java` | Implementação do repositório que integra com APIs externas (PGFT e SPAG) |
| `CorrespondenciaTedRepository.java` | Interface (port) que define operações de acesso a dados |
| `CorrespondenciaTedMapper.java` | Responsável por conversões entre objetos de domínio e DTOs |
| `CamelContextWrapper.java` | Wrapper para gerenciamento do contexto Apache Camel |
| `ClientsConfiguration.java` | Configuração dos clientes REST para APIs externas |
| `ExceptionControllerHandler.java` | Tratamento centralizado de exceções |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Spring Security OAuth2** (autenticação via JWT)
- **Apache Camel 3.4.1** (orquestração de rotas e integração)
- **RestTemplate** (cliente HTTP para consumo de APIs)
- **Swagger/OpenAPI 3.0** (documentação de APIs)
- **Springfox 3.0.0** (geração de documentação Swagger)
- **Swagger Codegen 2.4.9** (geração de clientes a partir de contratos OpenAPI)
- **Maven** (gerenciamento de dependências e build)
- **Logback** (logging com formato JSON)
- **Micrometer/Prometheus** (métricas e monitoramento)
- **Lombok** (redução de boilerplate)
- **JUnit 5 e Mockito** (testes unitários)
- **Docker** (containerização)
- **OpenShift/Kubernetes** (orquestração de containers)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/correspondencia-ted?dataMovimento={data}` | `CorrespondenciaTedController` | Realiza a inclusão de correspondências de TED para uma data de movimento específica (formato YYYY-MM-DD) |

---

## 5. Principais Regras de Negócio

1. **Busca de Código Máximo**: O sistema consulta o código de lançamento máximo já registrado no SPAG para evitar duplicação de correspondências.

2. **Filtro por Data de Movimento**: As correspondências são buscadas no PGFT com base em uma data de movimento fornecida como parâmetro.

3. **Filtro por Código de Lançamento**: Apenas TEDs com código de lançamento superior ao máximo já registrado são processados.

4. **Status Padrão**: Todas as correspondências inseridas recebem o status "N" (Não Correspondente) por padrão.

5. **Orquestração via Camel**: O fluxo segue uma sequência bem definida:
   - Consulta do código máximo no SPAG
   - Busca de TEDs no PGFT
   - Inserção das correspondências no SPAG

6. **Tratamento de Erros**: Erros HTTP 422 e 400 são tratados como erros de requisição, 401 como não autorizado, e demais como erro interno.

7. **Autenticação via Gateway**: O sistema utiliza OAuth2 client credentials para autenticação no API Gateway.

---

## 6. Relação entre Entidades

**Entidade Principal: CorrespondenciaTed**

Atributos:
- `nomeFavorecido`: String - Nome do favorecido da TED
- `valor`: BigDecimal - Valor da transferência
- `historico`: String - Histórico/descrição da operação
- `nomeRemetente`: String - Nome do remetente
- `numeroDocumentoRemetente`: String - CPF/CNPJ do remetente
- `codigoLancamento`: Long - Código único de lançamento

**Entidade de Request: CorrespondenciaTedApiRequest**

Atributos:
- `dataMovimento`: String - Data de referência para busca (formato YYYY-MM-DD)

**Relacionamentos:**
- Não há relacionamentos de banco de dados tradicionais, pois o sistema atua como orquestrador entre APIs externas.
- A entidade `CorrespondenciaTed` é mapeada entre os formatos do PGFT (origem) e SPAG (destino).

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

*Observação: O sistema não acessa diretamente bancos de dados. Todas as operações são realizadas via APIs REST.*

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

*Observação: O sistema não atualiza diretamente bancos de dados. As inserções são realizadas via API REST do SPAG.*

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `application.yml` | Leitura | Spring Boot (startup) | Arquivo de configuração da aplicação com profiles (local, des, qa, uat, prd) |
| `logback-spring.xml` | Leitura | Logback (runtime) | Configuração de logs em formato JSON para stdout |
| `swagger/*.yml` | Leitura | Swagger Codegen (build time) | Contratos OpenAPI para geração de clientes e interfaces |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema/API | Tipo | Descrição |
|-------------|------|-----------|
| **sboot-pgft-base-atom-movimento-pagamento** | API REST (GET) | Consulta TEDs para correspondência através do endpoint `/v1/correspondencia-ted`. Retorna lista de TEDs filtradas por data de movimento e código de lançamento. |
| **sboot-spag-base-atom-parcerias** | API REST (GET/POST) | Consulta o código de lançamento máximo (`/correspondencia-ted/max-codigo-lancamento`) e insere novas correspondências (`/correspondencia-ted`). |
| **API Gateway BV** | OAuth2 Token Provider | Fornece tokens JWT para autenticação nas APIs através do endpoint `/auth/oauth/v2/token-jwt` usando client credentials. |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo princípios de Clean Architecture (separação em módulos: common, domain, application)
- Uso adequado de padrões como Repository, Service e Mapper
- Boa separação de responsabilidades entre camadas
- Uso de Apache Camel para orquestração, facilitando manutenção e visualização do fluxo
- Tratamento centralizado de exceções
- Configuração adequada de profiles para diferentes ambientes
- Uso de Lombok para reduzir boilerplate
- Documentação via Swagger/OpenAPI
- Logs estruturados em JSON
- Testes unitários presentes (embora não enviados para análise)

**Pontos de Melhoria:**
- Alguns métodos poderiam ter documentação JavaDoc mais detalhada
- A classe `InclusaoTedService` possui dois construtores, o que pode gerar confusão
- Falta validação mais robusta dos parâmetros de entrada (ex: formato de data)
- Poderia haver mais uso de constantes para strings literais (ex: status "N")
- O tratamento de exceções poderia ser mais granular em alguns pontos
- Ausência de circuit breaker ou retry policies para chamadas externas

---

## 14. Observações Relevantes

1. **Arquitetura Multi-Módulo**: O projeto está organizado em três módulos Maven (common, domain, application), seguindo boas práticas de separação de responsabilidades.

2. **Geração de Código**: O projeto utiliza Swagger Codegen para gerar automaticamente clientes REST a partir de contratos OpenAPI, garantindo consistência com as APIs consumidas.

3. **Segurança**: A aplicação utiliza OAuth2 com JWT para autenticação, integrando-se ao API Gateway do Banco Votorantim.

4. **Observabilidade**: Implementa endpoints do Spring Actuator para health checks e métricas Prometheus, facilitando monitoramento em ambientes de produção.

5. **Containerização**: Possui Dockerfile otimizado usando imagem Alpine com OpenJ9 para reduzir footprint de memória.

6. **Infraestrutura como Código**: Inclui arquivo `infra.yml` com configurações para deploy em OpenShift/Kubernetes, incluindo configmaps, secrets, probes e recursos.

7. **Profiles de Ambiente**: Suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas para cada um.

8. **Processamento Assíncrono**: Utiliza Apache Camel para processamento assíncrono e orquestração de rotas, permitindo escalabilidade e resiliência.

9. **Versionamento de API**: Utiliza versionamento via path (`/v1/`) seguindo boas práticas REST.

10. **Feature Toggle**: Possui dependência para feature toggle, permitindo ativação/desativação de funcionalidades em runtime.