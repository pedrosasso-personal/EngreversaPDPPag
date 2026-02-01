# Ficha Técnica do Sistema

---

## 1. Descrição Geral

O sistema **sboot-flex-calc-orch-financiamento-flex** é um serviço de orquestração desenvolvido em Spring Boot que gerencia operações de cálculo de taxas de financiamento e criação de contratos na controladoria. Atua como um orquestrador que integra dois serviços principais: um para cálculo de taxas de financiamento e outro para criação de contratos na controladoria. Utiliza Apache Camel para orquestração de fluxos e expõe APIs REST para consumo externo.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal que inicializa a aplicação Spring Boot |
| `FinanciamentoController` | Controlador REST que expõe endpoints para cálculo de taxas e criação de contratos |
| `FinanciamentoFlexService` | Serviço de domínio que orquestra os fluxos de negócio via Apache Camel |
| `FinanciamentoFlexRouter` | Define as rotas do Apache Camel para orquestração dos fluxos |
| `TaxaFinanciamentoRepositoryImpl` | Implementação da integração com o serviço de cálculo de taxas |
| `ControladoriaRepositoryImpl` | Implementação da integração com o serviço de controladoria |
| `TaxaFinanciamentoMapper` | Mapeamento entre objetos de domínio e representações de taxa de financiamento |
| `ControladoriaMapper` | Mapeamento entre objetos de domínio e representações de controladoria |
| `LogInfo` | Utilitário para logging estruturado com mascaramento de dados sensíveis |
| `ExceptionProcessor` | Processador de exceções do Apache Camel |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Apache Camel 3.0.1** (orquestração de fluxos)
- **MapStruct 1.4.1** (mapeamento de objetos)
- **Swagger/OpenAPI 2.10.0** (documentação de APIs)
- **Prometheus/Micrometer** (métricas e monitoramento)
- **Grafana** (visualização de métricas)
- **HikariCP** (pool de conexões)
- **Logback** (logging)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Lombok** (redução de boilerplate)
- **RestTemplate** (cliente HTTP)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/varejo/contratos/gestao/taxa/financiamento` | `FinanciamentoController` | Lista taxas de financiamento com base nos parâmetros fornecidos |
| POST | `/v1/varejo/contratos/gestao/controladoria` | `FinanciamentoController` | Cria contrato na controladoria |

---

## 5. Principais Regras de Negócio

1. **Cálculo de Taxas de Financiamento**: O sistema recebe parâmetros como código do produto, modalidade, tipo de pessoa, valor financiado, quantidade de parcelas, entre outros, e retorna as taxas calculadas (CET, taxa pactuada, IOF, etc.).

2. **Validação de Retorno de Taxas**: O sistema valida se o serviço de taxas retornou dados válidos, lançando exceção caso não haja taxas no retorno.

3. **Criação de Contrato na Controladoria**: Após validações, o sistema envia dados do contrato para a controladoria, incluindo informações de parcelas, valores, taxas e dados do cliente.

4. **Validação de Código de Carga**: O sistema valida se o serviço de controladoria retornou um código de carga válido (maior que zero).

5. **Tratamento de Exceções**: Todas as exceções são tratadas de forma padronizada, retornando códigos de erro específicos e mensagens descritivas.

6. **Mascaramento de Dados Sensíveis em Logs**: O sistema mascara dados sensíveis nos logs, exibindo apenas os últimos 6 caracteres de identificadores.

---

## 6. Relação entre Entidades

**Entidades principais:**

- **TaxaFinanciamento**: Contém informações sobre o financiamento (produto, modalidade, valores, prazos) e as taxas calculadas.
  - Relaciona-se com `Taxa` (composição - 1:1)
  - Relaciona-se com `Custo` (composição - 1:N)
  - Relaciona-se com `InformacaoSubsidio` (composição - 1:1)

- **Controladoria**: Contém informações completas do contrato para controladoria.
  - Relaciona-se com `Parcela` (composição - 1:N)
  - Relaciona-se com `ParceiroComercial` (composição - 1:1)

- **Taxa**: Contém as taxas calculadas (CET, taxa pactuada, IOF, etc.)

- **Custo**: Representa custos associados ao financiamento (tipo e valor)

- **Parcela**: Representa uma parcela do financiamento (número, valor, data de vencimento)

- **ParceiroComercial**: Informações do parceiro comercial envolvido na operação

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
| `application.yml` | leitura | Spring Boot | Arquivo de configuração da aplicação com profiles (local, des, uat, prd) |
| `logback-spring.xml` | leitura | Logback | Configuração de logging da aplicação |
| `prometheus.yml` | leitura | Prometheus | Configuração do Prometheus para coleta de métricas |
| `grafana.ini` | leitura | Grafana | Configuração do Grafana para visualização de métricas |

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
| **sboot-flex-calc-acl-taxa-financiamento-flex** | API REST | Serviço de cálculo de taxas de financiamento. Endpoint: `/v1/varejo/contratos/gestao/taxa/financiamento` (POST) |
| **sboot-flex-calc-atom-controladoria-carga** | API REST | Serviço de criação de contrato na controladoria. Endpoint: `/v1/varejo/contratos/gestao/controladoria` (POST) |

**Observação**: As URLs dos serviços são configuráveis por ambiente através de variáveis de ambiente:
- `URL_LISTAR_TAXAS_FINANCIAMENTO`
- `URL_CRIAR_CONTRATO_CONTROLADORIA`

---

## 13. Avaliação da Qualidade do Código

**Nota: 7.5/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (application, domain, common)
- Uso adequado de padrões como Repository, Service e Mapper
- Implementação de logging estruturado com mascaramento de dados sensíveis
- Tratamento de exceções padronizado e centralizado
- Uso de Apache Camel para orquestração, facilitando manutenção de fluxos
- Documentação de APIs com Swagger/OpenAPI
- Configuração de métricas e monitoramento (Prometheus/Grafana)
- Uso de MapStruct para mapeamento automático de objetos

**Pontos de Melhoria:**
- Falta de testes unitários e de integração nos arquivos fornecidos
- Algumas classes poderiam ter mais documentação JavaDoc
- O uso de `SuppressWarnings("ALL")` em interfaces não é recomendado
- Poderia haver mais validações de entrada nos controllers
- A classe `LogInfo` possui lógica complexa que poderia ser simplificada
- Ausência de cache para otimizar chamadas repetidas aos serviços externos
- Falta de circuit breaker para resiliência nas integrações

---

## 14. Observações Relevantes

1. **Arquitetura Modular**: O projeto está organizado em três módulos Maven (application, domain, common), seguindo boas práticas de separação de responsabilidades.

2. **Segurança**: O sistema utiliza autenticação OAuth2 e JWT, conforme configurado nas dependências e arquivos Swagger.

3. **Ambientes**: O sistema está preparado para múltiplos ambientes (local, des, uat, prd) com configurações específicas para cada um.

4. **Containerização**: Dockerfile configurado para deploy em containers com OpenJDK 11 e OpenJ9.

5. **CI/CD**: Arquivo `jenkins.properties` indica integração com pipeline Jenkins para deploy automatizado.

6. **Infraestrutura como Código**: Arquivo `infra.yml` contém configurações para deploy em Kubernetes/OpenShift.

7. **Monitoramento**: Stack completa de observabilidade com Prometheus e Grafana configurados via Docker Compose.

8. **Padrão de Nomenclatura**: O projeto segue convenções do Banco Votorantim com prefixo `sboot-flex-calc-orch`.

9. **Versionamento**: Projeto na versão 0.1.0, indicando fase inicial de desenvolvimento.

10. **Dependências Corporativas**: Utiliza bibliotecas internas do Banco Votorantim para segurança, auditoria e tratamento de erros.

---