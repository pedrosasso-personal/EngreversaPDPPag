# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-spag-base-orch-extrato** é um serviço orquestrador de extratos bancários desenvolvido em Spring Boot. Sua principal função é consolidar informações de movimentações bancárias de contas correntes, integrando dados de múltiplas fontes (extrato de movimentações, informações de favorecidos e validação de segurança). O sistema atua como uma camada de orquestração que enriquece os dados de extrato com informações complementares de beneficiários/favorecidos antes de retornar ao cliente.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal Spring Boot que inicializa a aplicação |
| **ExtratoController** | Controller REST v1 que expõe endpoint de consulta de movimentações |
| **ExtratoV2Controller** | Controller REST v2 com validação adicional de documento parceiro |
| **ExtratoService** | Serviço de domínio que orquestra o fluxo de obtenção de extratos |
| **ExtratoRouter** | Roteador Apache Camel que define os fluxos de orquestração |
| **ExtratoRepositoryImpl** | Implementação de integração com serviço de extrato (sboot-ccbd-base-orch-extrato) |
| **FavorecidoRepositoryImpl** | Implementação de integração com serviço de favorecidos (sboot-pgft-base-atom-favorecido) |
| **SegurancaRepositoryImpl** | Implementação de integração com serviço de segurança/validação |
| **ExtratoProcessor** | Processador Camel que prepara requisição de favorecidos |
| **FavorecidoProcessor** | Processador Camel que enriquece extrato com dados de favorecidos |
| **ValidacaoDocumentoParceiroProcessor** | Processador Camel que valida documento do parceiro |
| **ExtratoMapper** | Mapeamento entre representações de extrato (client/domain/provider) |
| **FavorecidoMapper** | Mapeamento entre representações de favorecido |
| **MovimentacaoMapper** | Mapeamento de movimentações bancárias |
| **RequestMapper** | Mapeamento e validação de requisições de entrada |

---

## 3. Tecnologias Utilizadas

- **Spring Boot** (framework principal)
- **Spring MVC** (controllers REST)
- **Spring Security OAuth2** (autenticação/autorização via JWT)
- **Apache Camel 3.0.1** (orquestração de fluxos)
- **Swagger/OpenAPI 2.0** (documentação de APIs)
- **SpringFox 2.10.0** (geração de documentação Swagger)
- **RestTemplate** (cliente HTTP para integrações)
- **Apache HttpComponents** (customização de requisições HTTP)
- **Micrometer + Prometheus** (métricas e observabilidade)
- **Spring Actuator** (health checks e endpoints de gerenciamento)
- **Logback** (logging com formato JSON)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **JUnit 5 + Mockito** (testes unitários)
- **Rest Assured** (testes funcionais)
- **Pact** (testes de contrato)
- **Java 11**

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/movimentacoes-bancaria` | ExtratoController | Consulta movimentações bancárias (versão 1) |
| GET | `/v2/movimentacoes-bancaria` | ExtratoV2Controller | Consulta movimentações bancárias com validação de documento parceiro (versão 2) |

**Parâmetros comuns:**
- Headers: codigoBanco, numeroAgencia, numeroConta, numeroCpfCnpj, dataInicio, dataFim
- Query params: tamanhoPaginacao (max 50), pagina

---

## 5. Principais Regras de Negócio

1. **Validação de Período**: O intervalo entre dataInicio e dataFim não pode exceder 1440 minutos (24 horas)
2. **Paginação Limitada**: Tamanho máximo de página é 50 registros; se não informado ou excedido, utiliza 50 como padrão
3. **Datas Padrão**: Se dataInicio e dataFim não forem informados, utiliza o dia atual (00:00:00 até 23:59:59)
4. **Enriquecimento de Favorecidos**: Para movimentações que não são PIX nem boleto, busca informações do favorecido e enriquece o extrato com nome e documento do beneficiário
5. **Validação de Parceiro (v2)**: Na versão 2 da API, valida se o CNPJ do parceiro está autorizado antes de processar a requisição
6. **Filtro por Tipo de Movimentação**: Aplica filtro de data de lançamento por efetivação (padrão)
7. **Tratamento de Erros de Negócio**: Erros específicos são mapeados para códigos de erro padronizados (ExceptionReasonEnum)

---

## 6. Relação entre Entidades

**Entidades principais:**

- **ExtratoMovimentacao**: Agregado raiz contendo lista de movimentações, totais de entrada/saída e paginação
- **Movimentacao**: Representa uma movimentação bancária individual com categoria, valores, datas, identificadores e dados do beneficiário
- **Paginacao**: Informações de paginação (página atual, próxima, última, quantidade)
- **Favorecido**: Dados do favorecido (protocolo/id, nome, documento)
- **ListaFavorecidos**: Coleção de favorecidos

**Relacionamentos:**
- ExtratoMovimentacao **contém** múltiplas Movimentacao (1:N)
- ExtratoMovimentacao **possui** uma Paginacao (1:1)
- Movimentacao **pode referenciar** um Favorecido (0..1:1) através do numeroDocumento
- ListaFavorecidos **agrupa** múltiplos Favorecido (1:N)

**Enums:**
- **CategoriaEnum**: Categoriza tipos de movimentação (TED, TEF, PIX, BOLETO, CARTAO, etc.)
- **FiltroDataLancamentoEnum**: Define filtro de data (COMANDO, EFETIVACAO, INCLUSAO)
- **ExceptionReasonEnum**: Códigos de erro de negócio padronizados

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

*O sistema não acessa diretamente banco de dados. Todas as consultas são realizadas via APIs REST de outros serviços.*

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

*O sistema não realiza operações de escrita em banco de dados. É um serviço de consulta/orquestração apenas.*

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot (resources) | Configurações da aplicação por ambiente |
| logback-spring.xml | leitura | Logback (resources) | Configuração de logging com formato JSON |
| swagger-server/sboot-spag-base-orch-extrato.yml | leitura | Swagger Codegen Plugin | Especificação OpenAPI do serviço provedor |
| swagger-client/sboot-ccbd-base-orch-extrato.yml | leitura | Swagger Codegen Plugin | Especificação OpenAPI do cliente de extrato |
| swagger-client/sboot-pgft-base-atom-favorecido.yml | leitura | Swagger Codegen Plugin | Especificação OpenAPI do cliente de favorecidos |

---

## 10. Filas Lidas

não se aplica

*O sistema não consome mensagens de filas.*

---

## 11. Filas Geradas

não se aplica

*O sistema não publica mensagens em filas.*

---

## 12. Integrações Externas

| Sistema Integrado | Tipo | Descrição |
|-------------------|------|-----------|
| **sboot-ccbd-base-orch-extrato** | API REST | Serviço orquestrador de extrato que consulta movimentações bancárias no ElasticSearch/Sybase |
| **sboot-pgft-base-atom-favorecido** | API REST | Serviço atômico que retorna informações de favorecidos (nome, documento) |
| **sboot-spag-base-atom-seguranca** | API REST | Serviço de validação de documento/CNPJ de parceiros |
| **OAuth2 Server (API Gateway)** | OAuth2/JWT | Servidor de autenticação para validação de tokens JWT |

**Endpoints integrados:**
- POST `/v1/movimentacoes-bancaria/pesquisas` (ccbd-extrato)
- GET `/v1/consultarFavorecidosV2` (pgft-favorecido) - com body no GET
- POST `/v1/seguranca/validar` (spag-seguranca)

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões hexagonais (ports/adapters)
- Separação clara em módulos (application, domain, common)
- Uso adequado de Apache Camel para orquestração de fluxos
- Mapeadores bem definidos para conversão entre camadas
- Tratamento de exceções estruturado com enums de erro
- Documentação OpenAPI completa
- Configuração de observabilidade (Prometheus, Actuator)
- Testes organizados por tipo (unit, integration, functional)

**Pontos de Melhoria:**
- Uso de `@Autowired` em campos ao invés de injeção por construtor em alguns controllers
- Classe utilitária `ExceptionControllerHandler` com método estático que poderia ser um componente Spring
- Falta de validação de entrada mais robusta (Bean Validation)
- Alguns métodos com múltiplos parâmetros que poderiam ser encapsulados em DTOs
- Logs com informações sensíveis mesmo com sanitização (números de conta, documentos)
- Falta de testes unitários para algumas classes (marcados como NAO_ENVIAR)
- Configuração de segurança poderia ser mais explícita
- Uso de `RestTemplate` (considerado legado) ao invés de `WebClient`
- Alguns acoplamentos desnecessários (ex: dependência direta de representações geradas)

---

## 14. Observações Relevantes

1. **Versão da API**: O sistema possui duas versões da API (v1 e v2), sendo que a v2 adiciona validação de documento parceiro antes de processar a requisição.

2. **Customização HTTP**: Implementa `HttpComponentsClientHttpRequestWithBodyFactory` para permitir requisições GET com body, necessário para integração com o serviço de favorecidos.

3. **Orquestração com Camel**: Utiliza Apache Camel para orquestrar o fluxo de chamadas entre serviços, permitindo processamento sequencial e enriquecimento de dados.

4. **Segurança**: Integrado com OAuth2/JWT do API Gateway do Banco Votorantim, com validação de tokens em todas as requisições.

5. **Ambientes**: Configurado para múltiplos ambientes (local, des, qa, uat, prd) com URLs específicas para cada serviço integrado.

6. **Limitações**: 
   - Período máximo de consulta: 24 horas
   - Paginação máxima: 50 registros por página
   - Não suporta consultas históricas extensas

7. **Infraestrutura**: Preparado para deploy em Kubernetes/OpenShift (Google Cloud Platform) com configurações de probes, recursos e volumes.

8. **Observabilidade**: Métricas expostas via Prometheus com dashboards Grafana pré-configurados.

9. **Auditoria**: Integrado com biblioteca de trilha de auditoria do Banco Votorantim (bv-audit).

10. **Geração de Código**: Utiliza Swagger Codegen para gerar automaticamente interfaces de API (servidor) e clientes REST, garantindo contrato consistente.