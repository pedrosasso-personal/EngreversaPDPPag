# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema orquestrador responsável por listar os cartões de crédito disponíveis para transação de um cliente no contexto do Banco Digital (CCBD). O sistema recebe requisições REST autenticadas via JWT, extrai o CPF/CNPJ do usuário autenticado, consulta dois serviços externos (um para obter a lista de cartões e outro para obter detalhes de cada cartão), consolida as informações e retorna uma lista de cartões com dados como últimos dígitos, data de vencimento, limite disponível, bandeira e status.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal Spring Boot que inicializa a aplicação |
| **ListarCartoesController** | Controller REST que expõe o endpoint de listagem de cartões |
| **ListarCartoesService** | Serviço de domínio que orquestra a chamada ao repositório via Apache Camel |
| **ListarCartoesRepository** | Interface de porta (hexagonal) para acesso aos dados de cartões |
| **ListarCartoesRepositoryImpl** | Implementação do repositório que integra com serviços externos via RestTemplate |
| **ListarCartoesRouter** | Roteador Apache Camel que define o fluxo de processamento |
| **CamelContextWrapper** | Wrapper do contexto Camel para gerenciar rotas e templates |
| **ListarCartoesMapper** | Mapper que converte objetos de domínio em representações REST |
| **ObterCpf** | Utilitário para extrair CPF/CNPJ do contexto de segurança |
| **ErrorFormat** | Utilitário para formatação de erros em respostas HTTP |
| **AppProperties** | Classe de configuração com propriedades da aplicação |
| **ListarCartoesConfiguration** | Configuração Spring para beans do domínio |
| **OpenApiConfiguration** | Configuração do Swagger/OpenAPI |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.x** (framework principal)
- **Java 11** (linguagem e runtime)
- **Apache Camel 3.0.1** (orquestração e roteamento)
- **Spring Security OAuth2** (autenticação JWT)
- **RestTemplate** (cliente HTTP para integrações)
- **Swagger/Springfox 2.10.0** (documentação de API)
- **Lombok** (redução de boilerplate)
- **Micrometer/Prometheus** (métricas e observabilidade)
- **Logback** (logging)
- **JUnit 5** (testes unitários)
- **Mockito** (mocks em testes)
- **Maven** (gerenciamento de dependências e build)
- **Docker** (containerização)
- **OpenShift/Kubernetes** (orquestração de containers)
- **Grafana** (visualização de métricas)
- **HikariCP** (pool de conexões - configurado mas não utilizado diretamente no código fornecido)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/banco-digital/ccbd/cartoes` | ListarCartoesController | Lista todos os cartões do usuário autenticado com informações consolidadas (últimos dígitos, vencimento, limite, bandeira, status) |

---

## 5. Principais Regras de Negócio

1. **Autenticação obrigatória**: O sistema exige autenticação via JWT OAuth2 para todas as requisições
2. **Extração de CPF/CNPJ**: O CPF/CNPJ do cliente é extraído automaticamente do token JWT do usuário autenticado
3. **Consolidação de dados**: Para cada cartão retornado pelo serviço de listagem, o sistema busca detalhes adicionais (limite disponível e data de vencimento) em outro serviço
4. **Mapeamento de status**: O status numérico do cartão (10 = desbloqueado, outros = bloqueado) é convertido para enum legível
5. **Tratamento de erros**: Erros de integração são capturados e convertidos em respostas HTTP apropriadas (401, 422, 500)
6. **Filtragem de endpoints**: Endpoints do actuator não são incluídos nas métricas de negócio
7. **Conversão de formato de data**: Datas são convertidas de String (yyyy-MM-dd) para LocalDate

---

## 6. Relação entre Entidades

**Entidades principais:**

- **ListaDetalheCartao**: Contém uma lista de ListaCartao
- **ListaCartao**: Representa um cartão com atributos:
  - ultimosQuatroDigitosCartao (String)
  - statusCartaoCredito (Integer)
  - nomePessoaEmbossing (String)
  - detalheCartao (Limites)
  - listaVencimentoFaturaCartao (List<Fatura>)
  - tipoCartao (Tipo)
  - modalidadeCartao (Modalidade)

- **Limites**: Contém limitesCreditoCartao (Limite)
- **Limite**: Contém valorDisponivelCreditoRotativoTotal (BigDecimal)
- **Fatura**: Contém dataVencimentoFaturaCartao (String)
- **Tipo**: Contém código, códigoExterno, descrição e variante
- **Modalidade**: Contém código, descrição e bandeiraCartao
- **Bandeira**: Contém código e descrição
- **Variante**: Contém código e descrição

**Relacionamentos:**
- ListaDetalheCartao 1---* ListaCartao
- ListaCartao 1---1 Limites
- ListaCartao 1---* Fatura
- ListaCartao 1---1 Tipo
- ListaCartao 1---1 Modalidade
- Limites 1---1 Limite
- Tipo 1---1 Variante
- Modalidade 1---1 Bandeira

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
| application.yml | leitura | Spring Boot (startup) | Arquivo de configuração da aplicação com URLs de serviços, configurações de segurança e profiles |
| logback-spring.xml | leitura | Logback (startup) | Configuração de logging (console e arquivo JSON) |
| sboot-ccbd-base-orch-listar-cartoes.yaml | leitura | Swagger Codegen (build time) | Especificação OpenAPI para geração de interfaces REST |

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
| **sboot-cart-svhp-orch-lista-cartoes** | REST API | Serviço que retorna a lista de cartões de um CPF/CNPJ. Endpoint: `/v1/cartoes/cpf` (GET) |
| **sboot-cart-svhp-orch-detalhes-cartoes** | REST API | Serviço que retorna detalhes de um cartão específico (limite e vencimento). Endpoint: `/v1/cartoes/detalhes?ultimosQuatroDigitosCartao={digitos}` (GET) |
| **OAuth2 JWT Provider** | Autenticação | Provedor de tokens JWT para autenticação. URL configurável por ambiente (des/uat/prd) |

**Observação**: As URLs dos serviços são configuráveis por ambiente através de variáveis de ambiente (SERV_NAME_OBTER_DETALHE_CARTOES e SERV_NAME_OBTER_CARTOES).

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Uso de arquitetura hexagonal (ports/adapters) separando domínio de infraestrutura
- Separação clara de responsabilidades em módulos Maven (common, domain, application)
- Uso de padrões modernos (Spring Boot, Apache Camel, JWT)
- Configuração adequada de observabilidade (Prometheus, Grafana)
- Uso de Lombok para reduzir boilerplate
- Documentação OpenAPI/Swagger

**Pontos Negativos:**
- **Lógica complexa no repositório**: A classe `ListarCartoesRepositoryImpl` contém lógica de negócio (iteração sobre cartões, montagem de objetos) que deveria estar no serviço ou domínio
- **Tratamento de exceções genérico**: Captura de `Exception` genérica em múltiplos pontos
- **Acoplamento forte**: Uso direto de RestTemplate sem abstração, dificultando testes e manutenção
- **Falta de validações**: Não há validação de entrada (CPF/CNPJ nulo ou vazio antes de chamar serviços)
- **Código comentado**: Presença de código comentado em algumas classes
- **Nomenclatura inconsistente**: Mistura de português e inglês nos nomes de classes e variáveis
- **Falta de testes**: Arquivos de teste marcados como NAO_ENVIAR, impossibilitando avaliação da cobertura
- **Hardcoded values**: Valores mágicos como status "10" para cartão desbloqueado
- **Logs excessivos**: Muitos logs de informação que poderiam ser debug

---

## 14. Observações Relevantes

1. **Arquitetura de Orquestração**: O sistema atua como orquestrador, fazendo múltiplas chamadas síncronas para consolidar informações. Isso pode gerar latência e problemas de disponibilidade se os serviços downstream estiverem lentos ou indisponíveis.

2. **Apache Camel**: O uso do Camel parece desnecessário para este caso simples. A complexidade adicional não traz benefícios claros, já que há apenas uma rota direta para o repositório.

3. **Segurança**: O sistema utiliza autenticação JWT OAuth2 com validação de JWK, seguindo boas práticas de segurança.

4. **Observabilidade**: Boa configuração de métricas com Prometheus e dashboards Grafana pré-configurados.

5. **Deployment**: Preparado para OpenShift/Kubernetes com configurações de infraestrutura como código (infra.yml).

6. **Profiles**: Suporte a múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas.

7. **Performance**: Não há cache implementado, todas as requisições resultam em chamadas aos serviços externos.

8. **Resiliência**: Não há implementação de circuit breaker, retry ou timeout configurado explicitamente nas chamadas HTTP.

9. **Versionamento**: API versionada (v1) no path, permitindo evolução futura.

10. **Documentação**: README básico presente, mas poderia ser mais detalhado sobre regras de negócio e fluxos.