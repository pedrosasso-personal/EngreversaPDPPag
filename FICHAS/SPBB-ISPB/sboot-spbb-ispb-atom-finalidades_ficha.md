# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-spbb-ispb-atom-finalidades** é um serviço atômico REST desenvolvido em Spring Boot que fornece consulta de finalidades de transferências bancárias (TED). O serviço expõe um endpoint que retorna uma lista de finalidades de transferência filtradas por tipo (atualmente suporta apenas TED), consultando dados de um banco de dados Sybase. O sistema segue uma arquitetura hexagonal (ports and adapters) com separação clara entre camadas de domínio, aplicação e infraestrutura.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal que inicializa a aplicação Spring Boot |
| **FinalidadesController** | Controller REST que expõe o endpoint de consulta de finalidades |
| **FinalidadesService / FinalidadesServiceImpl** | Serviço de domínio que implementa a lógica de negócio para listar finalidades |
| **FinalidadesRepository / FinalidadesRepositoryImpl** | Interface de porta e implementação de repositório usando JDBI para acesso ao banco |
| **FinalidadesMapper** | Classe utilitária para conversão entre objetos de domínio e representações REST |
| **FinalidadeTransferencia** | Entidade de domínio representando uma finalidade de transferência |
| **TipoFinalidadeEnum** | Enum que define os tipos de finalidade suportados (TED) com códigos e descrições |
| **RazaoExceptionEnum** | Enum que define os códigos de erro do sistema |
| **FinalidadesException** | Exceção customizada para erros de negócio |
| **ResourceExceptionHandler** | Handler global de exceções para tratamento de erros REST |
| **DatabaseConfiguration** | Configuração do JDBI para acesso ao banco de dados |
| **FinalidadesConfiguration** | Configuração de beans do domínio (serviços e repositórios) |
| **OpenApiConfiguration** | Configuração do Swagger/OpenAPI para documentação da API |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Spring Security OAuth2** (autenticação JWT)
- **JDBI 3.9.1** (acesso a banco de dados)
- **Sybase ASE** (banco de dados)
- **Swagger/Springfox 2.9.2** (documentação de API)
- **Lombok** (redução de boilerplate)
- **Maven** (gerenciamento de dependências)
- **JUnit 5 / Mockito** (testes unitários)
- **Pact** (testes de contrato)
- **RestAssured** (testes funcionais)
- **Micrometer/Prometheus** (métricas)
- **Grafana** (visualização de métricas)
- **Docker** (containerização)
- **OpenShift/Kubernetes** (orquestração)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/banco-digital/listar-finalidades` | FinalidadesController | Lista finalidades de transferência filtradas por tipo (query param: tipoFinalidade) |

---

## 5. Principais Regras de Negócio

1. **Validação de Tipo de Finalidade**: O sistema valida se o tipo de finalidade informado é válido (atualmente apenas "TED" é suportado). Caso contrário, retorna erro 400 com código `BDCC_TIPO_FINALIDADE_INVALIDO`.

2. **Filtragem por Códigos de Liquidação**: Para cada tipo de finalidade, o sistema utiliza códigos de liquidação específicos (31 e 32 para TED) para filtrar os registros no banco.

3. **Filtragem por Descrições Permitidas**: Apenas finalidades com descrições específicas são retornadas (ex: "Crédito em conta", "Pagamento à Concessionárias de Serviço Público", etc.).

4. **Retorno de Finalidades Ativas**: Apenas registros com status 'A' (ativo) são considerados na consulta.

5. **Ordenação Alfabética**: Os resultados são ordenados alfabeticamente pela descrição da finalidade.

---

## 6. Relação entre Entidades

**FinalidadeTransferencia** (entidade de domínio):
- `codigo` (Long): código identificador da finalidade
- `descricao` (String): descrição textual da finalidade

**TipoFinalidadeEnum**:
- Relaciona-se com FinalidadeTransferencia através dos códigos de liquidação e descrições permitidas
- Atualmente possui apenas o valor TED com códigos [31, 32] e lista de 10 descrições válidas

Não há relacionamentos complexos entre entidades. O modelo é simples com uma única entidade principal.

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TBL_FINALIDADE_SPB | tabela | SELECT | Tabela que armazena as finalidades de transferência do SPB (Sistema de Pagamentos Brasileiro) com campos: Cod_Finalidade, Descr_Finalidade, Cod_Liquidacao e Status |

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot (inicialização) | Arquivo de configuração da aplicação com datasource, profiles e configurações de segurança |
| logback-spring.xml | leitura | Logback (logging) | Configuração de logs da aplicação (console e formato JSON) |
| consultarFinalidades.sql | leitura | FinalidadesRepositoryImpl (JDBI) | Query SQL para consulta de finalidades no banco Sybase |
| sboot-spbb-ispb-atom-finalidades.yaml | leitura | Swagger Codegen (build) | Especificação OpenAPI para geração de interfaces REST |

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
| Banco Sybase (DBITP) | Banco de Dados | Conexão JDBC para consulta de finalidades na tabela TBL_FINALIDADE_SPB |
| Serviço de Autenticação JWT | API REST | Validação de tokens JWT através do endpoint jwks.json (URLs diferentes por ambiente: des, uat, prd) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura hexagonal bem implementada com separação clara de responsabilidades (domain, application, infrastructure)
- Uso adequado de padrões como Repository, Service, Mapper
- Boa cobertura de testes unitários para as principais classes
- Configuração adequada de profiles para diferentes ambientes
- Uso de Lombok para reduzir boilerplate
- Documentação OpenAPI/Swagger presente
- Tratamento centralizado de exceções
- Uso de enums para constantes e códigos de erro
- Configuração de métricas e observabilidade (Prometheus/Grafana)

**Pontos de Melhoria:**
- Falta de validação de entrada no controller (poderia usar Bean Validation)
- Ausência de logs estruturados em alguns pontos críticos
- Testes de integração e funcionais estão vazios (apenas estrutura)
- Poderia ter mais documentação inline (JavaDoc) nas classes principais
- Configuração de segurança básica (poderia ter mais detalhes sobre autorização)
- Query SQL hardcoded em arquivo separado (boa prática, mas poderia ter mais queries documentadas)

O código demonstra maturidade técnica e segue boas práticas de desenvolvimento, com espaço para melhorias incrementais principalmente em testes e documentação.

---

## 14. Observações Relevantes

1. **Ambiente Multi-Perfil**: O sistema está preparado para rodar em múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas de datasource e URLs de autenticação.

2. **Segurança**: A aplicação utiliza OAuth2 com JWT para autenticação, sendo um Resource Server que valida tokens através de JWK.

3. **Observabilidade**: Infraestrutura completa de métricas com Prometheus e Grafana configurados, incluindo dashboards personalizados para monitoramento de JVM, HTTP, HikariCP e logs.

4. **Containerização**: Dockerfile otimizado usando OpenJ9 Alpine com configurações de memória JVM ajustáveis.

5. **CI/CD**: Configuração para Jenkins com propriedades específicas (jenkins.properties) e infraestrutura como código (infra.yml) para deploy no OpenShift.

6. **Limitação Funcional**: Atualmente o sistema suporta apenas finalidades do tipo TED. Para adicionar novos tipos (PIX, DOC, etc.) seria necessário estender o enum TipoFinalidadeEnum.

7. **Banco de Dados Legado**: Utiliza Sybase ASE, um banco de dados legado, com charset iso_1, o que pode requerer atenção especial para caracteres especiais.

8. **Arquitetura de Testes**: Estrutura bem organizada com separação de testes unitários, integração e funcionais em diretórios distintos, embora os testes de integração e funcionais estejam incompletos.