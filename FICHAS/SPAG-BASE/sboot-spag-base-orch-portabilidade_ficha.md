# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-spag-base-orch-portabilidade** é um serviço orquestrador de portabilidade de salário desenvolvido em Java com Spring Boot. Seu objetivo principal é gerenciar todo o fluxo de solicitação, consulta, cancelamento e acompanhamento de portabilidade salarial entre instituições bancárias. O sistema atua como uma camada de orquestração, integrando-se com diversos serviços atômicos e externos para validar dados cadastrais, consultar instituições bancárias, calcular dias úteis, e processar solicitações de portabilidade conforme regulamentação da CIP (Câmara Interbancária de Pagamentos).

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal que inicializa a aplicação Spring Boot |
| **PortabilidadeController** | Controller REST v1 que expõe endpoints para consulta de status, cancelamento e consulta de TED salário |
| **PortabilidadeControllerV2** | Controller REST v2 com endpoints para consulta de situação, cadastro de portabilidade e consulta de razão social |
| **PortabilidadeService / PortabilidadeServiceImpl** | Serviço de domínio que orquestra as operações de portabilidade |
| **TedSalarioService / TedSalarioServiceImpl** | Serviço responsável por consultas de TED salário |
| **PortabilidadeRouter** | Roteador Apache Camel que define fluxos de processamento paralelo para portabilidade |
| **CancelamentoPortabilidadeRouter** | Roteador Apache Camel para fluxos de cancelamento |
| **TedSalarioRouter** | Roteador Apache Camel para consultas de TED salário |
| **PortabilidadeRepositoryImpl** | Implementação de repositório que integra com API atômica de portabilidade |
| **ConsultaGlobalRepositoryImpl** | Repositório para consultas de dados cadastrais de clientes |
| **ConsultaInstituicoesRepositoryImpl** | Repositório para consulta de instituições bancárias |
| **ConsultaDiasUteisRepositoryImpl** | Repositório para cálculo de dias úteis |
| **RazaoSocialRepositoryImpl** | Repositório para consulta de razão social via CNPJ |
| **PortabilidadeMapper** | Classe utilitária para conversão entre DTOs e Representations |
| **ResourceExceptionHandler** | Tratador global de exceções da aplicação |
| **CamelContextWrapper** | Wrapper do contexto Apache Camel com suporte a thread pool customizado |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Spring Web** (REST APIs)
- **Spring Security** (autenticação OAuth2 JWT)
- **Apache Camel 3.21.4** (orquestração e processamento paralelo)
- **Swagger/OpenAPI 3.0** (documentação de APIs via Springfox)
- **Lombok** (redução de boilerplate)
- **HikariCP** (pool de conexões)
- **Micrometer + Prometheus** (métricas e monitoramento)
- **Grafana** (dashboards de monitoramento)
- **Logback** (logging com formato JSON)
- **JUnit 5 + Mockito** (testes unitários)
- **RestAssured** (testes funcionais)
- **Maven** (gerenciamento de dependências e build)
- **Docker** (containerização)
- **Google Cloud Platform** (deploy em Kubernetes/GKE)

---

## 4. Principais Endpoints REST

### V1 API

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/portabilidade/consulta` | PortabilidadeController | Consulta status de portabilidade (versão 1) |
| PUT | `/v1/portabilidade/cancelamento` | PortabilidadeController | Cancela uma solicitação de portabilidade |
| GET | `/v1/portabilidade/consultaClienteTedSalario` | PortabilidadeController | Consulta TEDs de salário recebidos pelo cliente |
| GET | `/v1/portabilidade/pesquisa-situacao` | PortabilidadeController | Pesquisa portabilidades por situação (PENDENTE, SUCESSO, ERRO, etc) |
| GET | `/v1/portabilidade/cancelamento/motivos/listar` | PortabilidadeController | Lista motivos disponíveis para cancelamento |
| POST | `/v1/portabilidade/cancelamento/motivos/enviar` | PortabilidadeController | Envia motivos de cancelamento selecionados pelo cliente |

### V2 API

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v2/portabilidade/consulta` | PortabilidadeControllerV2 | Consulta situação de portabilidade (versão 2 aprimorada) |
| POST | `/v2/portabilidade/solicitacao` | PortabilidadeControllerV2 | Solicita nova portabilidade de salário |
| GET | `/v2/portabilidade/{cnpj}/razao-social` | PortabilidadeControllerV2 | Consulta razão social por CNPJ |

---

## 5. Principais Regras de Negócio

1. **Validação de Conta Destino**: Verifica se a conta informada pertence ao cliente através de consulta ao serviço de dados cadastrais
2. **Cálculo de Prazo**: Calcula data limite de resposta da CIP considerando 5 dias úteis a partir da solicitação
3. **Validação de Horário CIP**: Solicitações após 19h são consideradas para o próximo dia útil
4. **Validação de CNPJ**: Valida formato e dígitos verificadores do CNPJ do empregador
5. **Consulta de Instituições**: Valida se o banco folha está habilitado para portabilidade via ISPB
6. **Mapeamento de Status**: Converte códigos numéricos de status em enums legíveis (PENDENTE, SUCESSO, ERRO, CANCELADO, etc)
7. **Tratamento de Motivos de Reprovação**: Mapeia códigos de motivo em mensagens amigáveis ao usuário
8. **Aceite Compulsório**: Identifica situações de aceite compulsório da portabilidade
9. **Validação de Cancelamento**: Permite cancelamento apenas de portabilidades em status PENDENTE
10. **Pesquisa por Situação**: Filtra portabilidades por múltiplos status simultaneamente
11. **Consulta de Razão Social**: Busca razão social ou nome fantasia via integração com MDM/VUCL
12. **Processamento Paralelo**: Utiliza Apache Camel para executar consultas em paralelo (conta, pessoa, instituições, dias úteis)

---

## 6. Relação entre Entidades

**Entidade Principal: Portabilidade**
- Contém dados do cliente (CPF/CNPJ, nome, código pessoa global)
- Contém dados da conta destino (banco, agência, conta, tipo conta)
- Contém dados do empregador (CPF/CNPJ, razão social, tipo pessoa)
- Contém dados do banco folha (ISPB, Bacen, nome)
- Contém dados temporais (data solicitação, data limite, data envio CIP)
- Contém status e motivos (situação, motivo, NSU)

**Relacionamentos:**
- Portabilidade → Cliente (1:1)
- Portabilidade → Conta Destino (1:1)
- Portabilidade → Empregador (1:1)
- Portabilidade → Banco Folha (1:1)
- Portabilidade → Motivos Cancelamento (1:N)

**DTOs de Transferência:**
- PortabilidadeVO: Value Object principal usado internamente
- StatusPortabilidadeDTO: Retorno de consulta de status
- SolicitarPortabilidadeDTO: Retorno de solicitação
- ConsultaPortabilidadeDTO: Retorno de pesquisa por situação
- TedSalarioVO: Parâmetros de consulta de TED
- ListaTedSalarioDTO: Lista de TEDs encontrados

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

*Observação: O sistema não acessa banco de dados diretamente. Todas as operações de leitura são realizadas através de APIs REST de serviços atômicos.*

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

*Observação: O sistema não atualiza banco de dados diretamente. Todas as operações de escrita são realizadas através de APIs REST de serviços atômicos.*

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | application/src/main/resources | Arquivo de configuração principal com URLs de serviços e perfis (local, des, qa, uat, prd) |
| logback-spring.xml | leitura | application/src/main/resources | Configuração de logs em formato JSON para diferentes ambientes |
| sboot-spag-base-orch-portabilidade.yaml | leitura | swagger/provider | Especificação OpenAPI dos endpoints providos pelo orquestrador |
| sboot-spag-base-atom-portabilidade.yaml | leitura | swagger/client | Especificação OpenAPI do cliente do serviço atômico de portabilidade |
| sboot-glob-base-atom-cliente-dados-cadastrais.yaml | leitura | swagger/client | Especificação OpenAPI do cliente de dados cadastrais |
| sboot-glob-base-orch-instituicoes.yaml | leitura | swagger/client | Especificação OpenAPI do cliente de instituições |
| sboot-dcor-base-atom-dias-uteis.yaml | leitura | swagger/client | Especificação OpenAPI do cliente de dias úteis |
| sboot-vucl-base-orch-dados-cadastrais-pessoa.yaml | leitura | swagger/client | Especificação OpenAPI do cliente de dados cadastrais pessoa |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| **sboot-spag-base-atom-portabilidade** | API REST | Serviço atômico de portabilidade - cadastro, consulta, cancelamento e pesquisa de portabilidades |
| **sboot-glob-base-atom-cliente-dados-cadastrais** | API REST | Consulta dados cadastrais de clientes (pessoa e conta corrente) |
| **sboot-glob-base-orch-instituicoes** | API REST | Consulta instituições bancárias por ISPB para validação |
| **sboot-dcor-base-atom-dias-uteis** | API REST | Validação de dias úteis e cálculo de prazos |
| **sboot-vucl-base-orch-dados-cadastrais-pessoa** | API REST | Consulta dados cadastrais completos (razão social, nome fantasia) via MDM |
| **OAuth2 JWT Provider** | Autenticação | Provedor de autenticação OAuth2 com JWT (api-digitaldes.bancovotorantim.com.br) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo Clean Architecture (separação em camadas: presentation, domain, infrastructure)
- Uso adequado de padrões como Repository, Service, Mapper e DTO
- Boa cobertura de testes unitários (presença de classes de teste para praticamente todos os componentes)
- Uso de Apache Camel para orquestração com processamento paralelo, otimizando performance
- Tratamento de exceções centralizado e estruturado com enums de códigos de erro
- Configuração externalizada por ambiente (local, des, qa, uat, prd)
- Documentação OpenAPI/Swagger bem definida
- Uso de Lombok para reduzir boilerplate
- Implementação de observabilidade (Prometheus, Grafana, Actuator)
- Logs estruturados em JSON
- Validações de negócio bem encapsuladas

**Pontos de Melhoria:**
- Algumas classes com responsabilidades múltiplas (ex: PortabilidadeMapper com muitos métodos estáticos)
- Uso excessivo de métodos estáticos em mappers dificulta testes e manutenção
- Alguns métodos longos que poderiam ser refatorados (ex: validações em ConsultaGlobalRepositoryImpl)
- Comentários de código comentado em testes (ApplicationTest)
- Falta de documentação JavaDoc em classes de domínio
- Alguns magic numbers sem constantes nomeadas
- Tratamento de exceções poderia ser mais granular em alguns pontos

---

## 14. Observações Relevantes

1. **Arquitetura Multi-módulo**: O projeto está organizado em 3 módulos Maven (common, domain, application), seguindo boas práticas de separação de responsabilidades

2. **Processamento Paralelo**: Utiliza Apache Camel com thread pool customizado (MdcThreadPoolExecutor) para manter contexto MDC e SecurityContext em threads paralelas

3. **Versionamento de API**: Implementa versionamento de endpoints (v1 e v2) permitindo evolução sem quebra de compatibilidade

4. **Segurança**: Integração com OAuth2 JWT do Banco Votorantim, com endpoints públicos apenas para Swagger

5. **Enums de Negócio**: Uso extensivo de enums para representar status, situações e motivos, facilitando manutenção e evitando strings mágicas

6. **Validação de CNPJ**: Implementa algoritmo completo de validação de CNPJ com dígitos verificadores

7. **Cálculo de Dias Úteis**: Lógica específica para calcular 5 dias úteis considerando feriados e finais de semana, com regra de corte às 19h

8. **Mapeamento de Mensagens**: Sistema sofisticado de mapeamento de códigos de erro/motivo em mensagens amigáveis ao usuário final

9. **Infraestrutura como Código**: Configuração completa para deploy em Kubernetes (GKE) com probes, recursos e service accounts

10. **Observabilidade**: Dashboard Grafana pré-configurado com métricas de JVM, HTTP, HikariCP e logs

11. **Sanitização de Logs**: Implementa LogUtils para sanitizar inputs antes de logar, prevenindo log injection

12. **Recuperação de Contexto**: Utilitário RecuperaCpfCnpj para extrair documento do usuário autenticado via JWT quando não informado no header