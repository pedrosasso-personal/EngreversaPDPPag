# Ficha Técnica do Sistema

---

## 1. Descrição Geral

Este sistema é um **BFF (Backend For Frontend)** desenvolvido em Spring Boot que atua como intermediário entre o frontend e um serviço de cadastro de programas. O componente `sboot-spbb-base-stat-ispb-bff` expõe endpoints REST para operações CRUD (listar, buscar por ID, inserir, atualizar e deletar) relacionadas a programas, delegando as chamadas para um serviço backend através de um cliente Feign.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application.java` | Classe principal que inicializa a aplicação Spring Boot e habilita clientes Feign |
| `AtomProgramaController.java` | Controlador REST que expõe endpoints HTTP para operações com programas |
| `AtomProgramaServiceImpl.java` | Camada de serviço que implementa a lógica de negócio e orquestra chamadas ao cliente Feign |
| `AtomProgramaClient.java` | Interface Feign Client que define a comunicação com o serviço backend de cadastro de programas |
| `ProgramaDTO.java` | Objeto de transferência de dados (DTO) que representa a entidade Programa |
| `OpenApiConfiguration.java` | Configuração do Swagger/OpenAPI para documentação dos endpoints |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.x** (framework principal)
- **Spring Cloud OpenFeign** (cliente HTTP declarativo)
- **Swagger/Springfox 2.9.2** (documentação de API)
- **Micrometer + Prometheus** (métricas e monitoramento)
- **Grafana** (visualização de métricas)
- **Logback** (logging)
- **Lombok** (redução de boilerplate)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Java 11** (linguagem e runtime)
- **HikariCP** (pool de conexões - configurado mas não utilizado diretamente no código fornecido)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/bff/listaProgramas` | `AtomProgramaController` | Lista todos os programas |
| GET | `/v1/bff/{id}` | `AtomProgramaController` | Busca um programa por ID |
| POST | `/v1/bff/{progDsName}/{progDsForm}/{progDsMenu}` | `AtomProgramaController` | Insere um novo programa |
| PUT | `/v1/bff` | `AtomProgramaController` | Atualiza um programa existente |
| DELETE | `/v1/bff/{id}` | `AtomProgramaController` | Deleta um programa por ID |

---

## 5. Principais Regras de Negócio

O sistema atua como um **proxy/BFF**, não implementando regras de negócio complexas. Sua responsabilidade principal é:

1. **Receber requisições HTTP** do frontend
2. **Delegar chamadas** ao serviço backend (`localhost:9090/v1/cadastro-programa`) via Feign Client
3. **Retornar respostas** ao cliente

Não foram identificadas validações de negócio ou transformações de dados significativas no código fornecido.

---

## 6. Relação entre Entidades

**ProgramaDTO** é a única entidade de domínio identificada, contendo os seguintes atributos:

- `idPrograma` (short): identificador único do programa
- `progDsNome` (String): nome do programa
- `progDsForm` (String): descrição do formulário
- `progDsMenu` (String): descrição do menu

Não há relacionamentos com outras entidades no código fornecido.

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
| `application.yml` | leitura | Spring Boot (configuração) | Arquivo de configuração da aplicação com profiles e propriedades |
| `logback-spring.xml` | leitura | Logback (logging) | Configuração de logs da aplicação |
| `prometheus.yml` | leitura | Prometheus (métricas) | Configuração do Prometheus para scraping de métricas |
| `grafana.ini` | leitura | Grafana (visualização) | Configuração do Grafana para dashboards |

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
| Serviço de Cadastro de Programas | REST API (Feign) | Integração via `AtomProgramaClient` com endpoint `localhost:9090/v1/cadastro-programa` para operações CRUD de programas |
| Prometheus | Métricas | Exposição de métricas via `/actuator/prometheus` |
| ConfigCat | Feature Toggle | Configuração de feature flags (variável de ambiente `CONFIGCAT_KEY`) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 5/10**

**Justificativa:**

**Pontos Positivos:**
- Estrutura modular bem definida (application, domain, common)
- Uso de padrões REST adequados
- Documentação via Swagger configurada
- Observabilidade com Actuator, Prometheus e Grafana
- Uso de Lombok para redução de boilerplate

**Pontos Negativos:**
- **Falta de injeção de dependências**: `AtomProgramaServiceImpl` e `AtomProgramaController` não possuem anotações `@Service` ou `@RestController` adequadas, e as dependências não são injetadas via construtor ou `@Autowired`
- **Ausência de tratamento de erros**: Não há validações, exception handlers ou tratamento de erros HTTP
- **Falta de testes**: Não foram fornecidos testes unitários ou de integração
- **Design de API inconsistente**: Endpoint POST usa path parameters em vez de request body
- **Documentação incompleta**: Swagger configurado mas sem descrições detalhadas
- **Hardcoded URL**: URL do Feign Client está hardcoded (`localhost:9090`)
- **Falta de validação de entrada**: Não há validações de dados de entrada (Bean Validation)

---

## 14. Observações Relevantes

1. **Arquitetura BFF**: O sistema segue o padrão Backend For Frontend, atuando como camada intermediária
2. **Ambiente de desenvolvimento**: Configuração completa para ambiente local com Docker Compose, Prometheus e Grafana
3. **Multi-ambiente**: Suporte a múltiplos ambientes (local, des, qa, uat, prd) via profiles do Spring
4. **Monitoramento robusto**: Infraestrutura completa de observabilidade com dashboards Grafana pré-configurados
5. **Pipeline CI/CD**: Configuração Jenkins presente (`jenkins.properties`) para deploy automatizado
6. **Kubernetes ready**: Arquivo `infra.yml` com configurações para deploy em OpenShift/Kubernetes
7. **Problema crítico**: O código apresentado não funcionará corretamente sem as anotações Spring adequadas (`@Service`, `@Autowired`, etc.)
8. **Feature Toggle**: Integração com ConfigCat para gerenciamento de features
9. **Auditoria**: Dependência de trilha de auditoria do Banco Votorantim configurada

---