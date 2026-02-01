# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-ccbd-base-orch-extrato-composto-consultar** é um orquestrador (orchestrator) desenvolvido em Spring Boot que atua como intermediário para consulta de extratos compostos bancários. Ele recebe requisições REST, valida parâmetros, autentica via OAuth2 no API Gateway e encaminha as solicitações para um serviço atômico (atom) que efetivamente realiza a consulta de extratos. O sistema faz parte da arquitetura de microserviços do Banco Votorantim (CCBD - Conta Corrente Banco Digital) e segue o padrão de orquestração stateless.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application.java` | Classe principal que inicializa a aplicação Spring Boot |
| `ExtratoApiDelegateImpl.java` | Implementa o endpoint REST de consulta de extrato, recebe requisições HTTP |
| `ExtratoServiceImpl.java` | Contém a lógica de negócio, orquestra chamadas ao serviço atômico e trata exceções |
| `ExtratoService.java` | Interface do serviço de consulta de extrato |
| `ExtratoCompostoMapper.java` | Responsável por mapear objetos entre camadas (atom para presentation) |
| `ExtratoCompostoHandler.java` | Tratador global de exceções da aplicação |
| `ExtratoException.java` | Exceção customizada para erros de negócio |
| `ErrosExtrato.java` | Enumeração com códigos e mensagens de erro padronizados |
| `ExtratoRequest.java` | DTO que encapsula os parâmetros de requisição |
| `AuthProperties.java` | Propriedades de configuração de autenticação OAuth2 |
| `RouteProperties.java` | Propriedades de configuração de rotas/endpoints |
| `ExtratoCompostoConsultarConfiguration.java` | Configurações de beans (RestTemplate, ObjectMapper, OAuth Service) |
| `OpenApiConfiguration.java` | Configuração da documentação OpenAPI/Swagger |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.x** - Framework principal
- **Spring Security OAuth2** - Autenticação e autorização JWT
- **Spring Web** - Endpoints REST
- **MapStruct** - Mapeamento de objetos
- **OpenAPI Generator** - Geração de código a partir de especificações OpenAPI/Swagger
- **Lombok** - Redução de código boilerplate
- **Jackson** - Serialização/deserialização JSON
- **Maven** - Gerenciamento de dependências e build
- **Docker** - Containerização
- **Kubernetes** - Orquestração de containers (infra-as-code)
- **Actuator** - Monitoramento e health checks
- **SLF4J/Logback** - Logging
- **RestTemplate** - Cliente HTTP para chamadas REST
- **Java 11** - Versão da linguagem

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/extrato` | `ExtratoApiDelegateImpl` | Consulta paginada de extrato composto com filtros de data, conta e tipo de data |

**Parâmetros do endpoint:**
- Headers: `codigoBanco`, `codigoTipoConta`, `numeroConta`
- Query params: `tipoDataPesquisa`, `dataInicial`, `dataFinal`, `tamanhoPagina`, `paginacaoReferencia`

---

## 5. Principais Regras de Negócio

1. **Validação de Parâmetros Obrigatórios**: Código do banco, tipo de conta, número da conta, tipo de data de pesquisa, data inicial, data final e tamanho da página são obrigatórios
2. **Autenticação OAuth2**: Todas as requisições devem ser autenticadas via token JWT obtido do API Gateway
3. **Paginação**: Suporte a paginação com referência para navegação entre páginas
4. **Tipos de Data de Pesquisa**: Aceita três tipos - INCLUSAO, COMANDO ou EFETIVACAO
5. **Tratamento de Erros**: Erros de validação (400) e erros internos (500) são tratados de forma padronizada
6. **Orquestração**: O serviço não acessa diretamente banco de dados, apenas orquestra chamadas ao serviço atômico
7. **Tamanho Mínimo de Página**: Deve ser no mínimo 1 registro por página

---

## 6. Relação entre Entidades

O sistema trabalha principalmente com as seguintes representações (DTOs):

- **ExtratoCompostoRepresentation**: Entidade principal contendo:
  - **IdentificadorRepresentation**: Identificação da conta e documento
  - **TransacaoRepresentation**: Dados da transação bancária
  - **DetalhesTransacaoRepresentation**: Detalhes adicionais da transação
    - **ContaPessoaRepresentation**: Dados de remetente e favorecido
    - **DetalhesAdicionaisRepresentation**: Informações complementares
      - **DetalhesBoletoRepresentation**: Específico para boletos
        - **ValoresBoletoRepresentation**: Valores do boleto
          - **EncargosRepresentation**: Multas, juros, descontos
  - **CategoriaRepresentation**: Categorização da transação

- **PaginacaoRepresentation**: Controle de paginação com links para próxima e anterior

- **ExtratoRequest**: DTO interno para encapsular parâmetros de busca

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

*O sistema não acessa diretamente banco de dados. Ele consome um serviço atômico (atom) que realiza as operações de leitura.*

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

*O sistema não realiza operações de escrita em banco de dados.*

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `application.yml` | Leitura | Spring Boot (startup) | Arquivo de configuração principal da aplicação |
| `logback-spring.xml` | Leitura | Logback (configurado via `LOGGING_CONFIG`) | Configuração de logs da aplicação |
| `openapi.yaml` | Leitura | OpenAPI Generator (build time) | Especificação da API REST exposta |
| `sboot-ccbd-base-atom-extrato-composto.yaml` | Leitura | OpenAPI Generator (build time) | Especificação do cliente REST para o serviço atômico |

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

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **API Gateway OAuth2** | REST | Autenticação e obtenção de token JWT (endpoint: `/auth/oauth/v2/token-jwt`) |
| **sboot-ccbd-base-atom-extrato-composto** | REST | Serviço atômico que realiza a consulta efetiva de extratos compostos. Comunicação via HTTP interno do Kubernetes |

**Endpoints do serviço atômico por ambiente:**
- DES: `http://sboot-ccbd-base-atom-extrato-composto.des-ccbd-base.svc.cluster.local:8080`
- UAT: `http://sboot-ccbd-base-atom-extrato-composto.uat-ccbd-base.svc.cluster.local:8080`
- PRD: `http://sboot-ccbd-base-atom-extrato-composto.prd-ccbd-base.svc.cluster.local:8080`

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Código bem estruturado seguindo padrões de arquitetura em camadas (REST → Service → Client)
- Uso adequado de padrões de projeto (Builder, Mapper, Exception Handler)
- Separação clara de responsabilidades entre classes
- Uso de anotações Lombok reduzindo boilerplate
- Tratamento de exceções centralizado e padronizado
- Configurações externalizadas em arquivos YAML
- Logging adequado em pontos estratégicos
- Uso de DTOs para transferência de dados
- Documentação OpenAPI/Swagger bem definida

**Pontos de Melhoria:**
- Falta de comentários JavaDoc em métodos públicos
- Alguns logs poderiam incluir mais contexto (IDs de transação, por exemplo)
- Poderia haver validações mais robustas nos DTOs (Bean Validation)
- Ausência de testes unitários nos arquivos analisados (marcados como NAO_ENVIAR)
- Configuração de timeout e retry para chamadas REST não está explícita
- Poderia ter circuit breaker para resiliência nas chamadas ao serviço atômico

---

## 14. Observações Relevantes

1. **Arquitetura de Microserviços**: O sistema segue o padrão Atlante do Banco Votorantim, separando orquestradores (orch) de serviços atômicos (atom)

2. **Ambientes**: Possui configurações específicas para três ambientes (DES, UAT, PRD) gerenciadas via ConfigMaps e Secrets do Kubernetes

3. **Segurança**: Implementa autenticação JWT com validação de issuer e JWKS, com endpoints públicos apenas para Swagger em desenvolvimento

4. **Monitoramento**: Expõe métricas via Actuator na porta 9090 (separada da porta de aplicação 8080)

5. **Multi-layer Docker**: Utiliza estratégia de build em camadas para otimização de imagens Docker

6. **Paginação HATEOAS**: Implementa paginação com links hipermídia para navegação

7. **Versionamento de API**: Utiliza versionamento via path (`/v1/`)

8. **Geração de Código**: Utiliza OpenAPI Generator para gerar tanto o servidor quanto o cliente REST, garantindo contrato consistente

9. **Resiliência**: Não foram identificados mecanismos explícitos de circuit breaker ou retry, o que pode ser uma área de melhoria para produção

10. **Documentação**: Possui README com informações básicas e links para confluência interna do banco

---