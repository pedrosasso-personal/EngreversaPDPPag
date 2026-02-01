# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-ccbd-base-orch-solic-debito** é um microserviço orquestrador responsável por solicitar débito e bloquear saldo de conta corrente no contexto do Banco Digital (CCBD - Conta Corrente Banco Digital) do Banco Votorantim. 

O serviço atua como orquestrador, integrando-se com múltiplos serviços atômicos (atoms) para:
- Solicitar débito em conta corrente
- Consultar transações pendentes em stand-in
- Criar e atualizar monitoramentos de saldo
- Bloquear valores disponíveis em conta
- Validar motivos de bloqueio

Utiliza Apache Camel para orquestração de fluxos e Spring Boot como framework base.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal Spring Boot que inicializa a aplicação |
| **SolicDebitoController** | Controller REST que expõe os endpoints de solicitação de débito |
| **SolicDebitoService** | Serviço de domínio que coordena as solicitações via Apache Camel |
| **SolicDebitoRouter** | Rota Camel para orquestração do fluxo de solicitação de débito |
| **SolicDebitoDiponivelRouter** | Rota Camel para orquestração do fluxo de débito com saldo disponível |
| **SolicDebitoRepositoryImpl** | Implementação de integração com serviço atômico de conta corrente |
| **SolicDebitoStandInRepositoryImpl** | Implementação de integração com serviço stand-in |
| **ConsultaContaRepositoryImpl** | Implementação de consulta de saldo de conta |
| **CriaMonitoramentoRepositoryImpl** | Implementação de criação de monitoramento de saldo |
| **AtualizaMonitoramentoRepositoryImpl** | Implementação de atualização de monitoramento |
| **ConsultaMotivoBloqueioRepositoryImpl** | Implementação de consulta de motivos de bloqueio |
| **CodigoBancoProcessor** | Processador Camel para validação e conversão de código de banco |
| **PreencheValorBloqueadoProcessor** | Processador Camel para cálculo de valor a ser bloqueado |
| **SolicDebitoMapper** | Mapeador de objetos de request para domínio |
| **SolicDebitoResponseMapper** | Mapeador de objetos de domínio para response |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework base)
- **Spring Security OAuth2** (autenticação JWT)
- **Apache Camel 3.0.1** (orquestração de fluxos)
- **Maven** (gerenciamento de dependências)
- **Swagger/OpenAPI 3.0** (documentação de API)
- **Lombok** (redução de boilerplate)
- **RestTemplate** (cliente HTTP)
- **Logback** (logging)
- **JUnit 5** (testes unitários)
- **Mockito** (mocks em testes)
- **Actuator + Prometheus** (métricas e monitoramento)
- **Docker** (containerização)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/banco-digital/contas/debito` | SolicDebitoController | Solicita débito em conta corrente com validação de saldo |
| POST | `/v1/banco-digital/contas/debito-valor-disponivel` | SolicDebitoController | Solicita débito com bloqueio de valor disponível e criação de monitoramento |

**Headers obrigatórios:**
- `codigoBanco`: Código do banco
- `numeroAgencia`: Número da agência
- `numeroConta`: Número da conta
- `tipoConta`: Tipo da conta

---

## 5. Principais Regras de Negócio

1. **Validação de Código de Banco**: Converte código externo (compesação) para código interno (BV=161/655, BVSA=436/413)

2. **Fluxo Stand-In**: 
   - Verifica se conta está na lista permitida para stand-in
   - Consulta transações pendentes em stand-in
   - Se conta fechada ou com transação pendente, redireciona para stand-in

3. **Débito com Saldo Disponível**:
   - Valida número de protocolo (não pode ser nulo/vazio)
   - Valida valor da operação (não pode ser nulo/negativo)
   - Consulta saldo da conta
   - Valida motivo de bloqueio (deve estar ativo e ser monitorado)
   - Calcula valor a bloquear (menor entre solicitado e disponível)
   - Cria monitoramento de saldo
   - Executa débito se valor > 0
   - Atualiza monitoramento com resultado

4. **Validação de Motivo de Bloqueio**: Motivo deve estar ativo (`flAtivo=true`) e ser monitorado (`flMonitorado=true`)

5. **Tratamento de Conta Fechada**: Retorna status 307 (Temporary Redirect) quando conta está fechada

6. **Sanitização de Logs**: Remove quebras de linha e espaços múltiplos de valores logados

---

## 6. Relação entre Entidades

**Entidades principais:**

- **SolicDebito**: Representa uma solicitação de débito
  - Atributos: codigoBanco, numeroAgencia, numeroConta, tipoConta, valorOperacao, flLancamentoIncondicionalSaldo, codigoMotivoBloqueio, dsComplementoOperacao, numeroProtocolo

- **SolicDebitoProcesso**: Encapsula o processo de solicitação
  - Contém: SolicDebito, SolicDebitoResponse, SolicDebitoStandInResponse, flags de controle

- **SolicDebitoDiponivelProcesso**: Estende SolicDebitoProcesso para débito com saldo disponível
  - Adiciona: MonitoramentoSaldo, SaldoConta, MotivoBloqueio

- **MonitoramentoSaldo**: Representa um monitoramento de bloqueio
  - Relacionamento 1:N com MonitoramentoSaldoBloqueado

- **SaldoConta**: Representa saldos da conta
  - Atributos: valorBloqueado, valorDisponivel, valorIndisponivel, valorLimite, valorTotal

- **MotivoBloqueio**: Representa um motivo de bloqueio cadastrado
  - Atributos: cdMotivoBloqueio, descricao, flMonitorado, flAtivo, nuOrdemPrioridade

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

*Observação: O sistema não acessa diretamente banco de dados. Todas as operações são realizadas via APIs REST de serviços atômicos.*

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

*Observação: O sistema não atualiza diretamente banco de dados. Todas as operações de escrita são realizadas via APIs REST de serviços atômicos.*

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot (startup) | Arquivo de configuração da aplicação com profiles (local, des, qa, uat, prd) |
| logback-spring.xml | leitura | Logback (startup) | Configuração de logging em formato JSON |
| sboot-ccbd-base-orch-solic-debito.yaml | leitura | Swagger Codegen (build) | Especificação OpenAPI para geração de interfaces |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema Integrado | Tipo | Descrição |
|-------------------|------|-----------|
| **sboot-ccbd-base-atom-conta-corrente** | API REST | Serviço atômico para operações de débito em conta corrente. Endpoint: `/v1/banco-digital/contas/debito/` |
| **sboot-ccbd-base-atom-conta-corrente-stdin** | API REST | Serviço atômico para operações em modo stand-in. Endpoints: `/v1/banco-digital/contas/transacao` (GET), `/v1/banco-digital/contas/debito` (POST) |
| **sboot-ccbd-base-atom-bloqueios-saldo** | API REST | Serviço atômico para gerenciamento de bloqueios e monitoramentos de saldo. Endpoints: `/v1/contas/monitoramentos` (POST/PUT), `/v1/motivos-bloqueio/{codigo}` (GET) |
| **OAuth2 JWT Provider** | OAuth2 | Provedor de autenticação JWT. URL configurável por ambiente (ex: api-digitaluat.bancovotorantim.com.br) |

**Observações:**
- Todas as integrações utilizam RestTemplate com segurança OAuth2
- Headers customizados são enviados: codigoBanco, numeroAgencia, numeroConta, tipoConta, validaStandIn
- Tratamento específico para erros HTTP 4xx e 5xx com conversão para SolicDebitoException

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (domain/application)
- Uso adequado de padrões como Repository, Service, Mapper
- Cobertura de testes unitários presente
- Uso de Apache Camel para orquestração de fluxos complexos
- Tratamento de exceções estruturado com classe customizada
- Uso de Lombok para reduzir boilerplate
- Documentação OpenAPI/Swagger
- Sanitização de logs para segurança

**Pontos de Melhoria:**
- Código com alguns "code smells": métodos longos (ex: `solicitarDebito` em SolicDebitoRepositoryImpl)
- Lógica de negócio misturada com infraestrutura em alguns pontos
- Uso de flags booleanas em vez de enums para estados (contaCorrenteFechado, transacaoPendenteStandIn)
- Constantes hardcoded em alguns locais (ex: "N", "S" para flags)
- Falta de validação de entrada em alguns pontos
- Comentários em português misturados com código em inglês
- Alguns testes com nomes genéricos (ex: "test()")
- Uso de `@SneakyThrows` que pode esconder exceções
- Configuração de URLs via properties sem validação

**Recomendações:**
- Extrair métodos menores e mais coesos
- Criar enums para estados e flags
- Padronizar nomenclatura (português vs inglês)
- Adicionar validações de entrada com Bean Validation
- Melhorar nomes de testes para refletir cenários
- Considerar uso de Circuit Breaker para integrações externas

---

## 14. Observações Relevantes

1. **Arquitetura Multi-módulo**: O projeto está dividido em dois módulos Maven:
   - `domain`: Contém lógica de negócio, entidades, portas e rotas Camel
   - `application`: Contém infraestrutura, controllers, implementações de repositórios

2. **Segurança**: Utiliza OAuth2 com JWT para autenticação. Endpoints públicos configuráveis incluem Swagger e Actuator.

3. **Profiles de Ambiente**: Suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas via variáveis de ambiente.

4. **Stand-In**: Sistema possui lógica específica para operação em modo stand-in quando sistema principal está indisponível ou conta está fechada. Lista de contas permitidas configurável via properties.

5. **Monitoramento**: Integrado com Prometheus para métricas e possui endpoints Actuator para health checks.

6. **Versionamento de API**: API versionada com prefixo `/v1/`.

7. **Conversão de Códigos de Banco**: Sistema converte códigos de compensação (655, 413) para códigos internos (161, 436) via enum BancoEnum.

8. **Tratamento de Erros**: Erros de integração são convertidos para SolicDebitoException com códigos padronizados (BDCC_ERRO_INTERNO, BDCC_CONTA_NAO_ENCONTRADA, BDCC_MOTIVO_BLOQUEIO_MONITORADO_INVALIDO).

9. **Logs Estruturados**: Configuração de logs em formato JSON para facilitar análise e integração com ferramentas de observabilidade.

10. **Testes**: Estrutura de testes separada em unit, integration e functional, com suporte a testes de arquitetura via ArchUnit.

11. **Containerização**: Dockerfile baseado em imagem Java 11 do repositório interno do banco.

12. **Geração de Código**: Utiliza Swagger Codegen Maven Plugin para gerar interfaces de API a partir da especificação OpenAPI.