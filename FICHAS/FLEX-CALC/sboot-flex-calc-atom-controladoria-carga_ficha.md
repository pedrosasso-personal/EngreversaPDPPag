# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-flex-calc-atom-controladoria-carga** é um serviço atômico desenvolvido em Spring Boot para realizar a carga de dados de contratos na controladoria. O sistema recebe informações de contratos financeiros via API REST e persiste esses dados em um banco de dados Sybase (DBGERENCIAL), incluindo informações do contrato principal e suas parcelas associadas.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal que inicializa a aplicação Spring Boot |
| `ControladoriaCargaController` | Controlador REST que expõe o endpoint para criação de contratos de controladoria |
| `ControladoriaCargaService` | Serviço de domínio que implementa a lógica de negócio para criação de contratos |
| `ControladoriaCargaRepositoryJdbi` | Interface de repositório que define operações de banco de dados usando JDBI |
| `ControladoriaCargaMapper` | Mapper MapStruct para conversão entre objetos de domínio e representações REST |
| `Controladoria` | Entidade de domínio que representa um contrato de controladoria |
| `Parcela` | Entidade de domínio que representa uma parcela do contrato |
| `ParceiroComercial` | Entidade de domínio que representa informações do parceiro comercial |
| `ControladoriaCargaConfiguration` | Classe de configuração do Spring para beans e dependências |
| `LogInfo` | Utilitário para logging estruturado com mascaramento de dados sensíveis |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Spring Web** (para APIs REST)
- **Spring JDBC** (para acesso a dados)
- **JDBI 3.9.1** (framework de persistência SQL)
- **Sybase jConnect 16.3** (driver JDBC para Sybase)
- **MapStruct 1.4.1** (mapeamento de objetos)
- **Lombok** (redução de boilerplate)
- **Swagger/SpringFox 2.10.0** (documentação de API)
- **Micrometer/Prometheus** (métricas e monitoramento)
- **Logback** (logging)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Jenkins** (CI/CD)
- **Grafana** (visualização de métricas)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/varejo/contratos/gestao/controladoria` | `ControladoriaCargaController` | Cria um novo contrato de controladoria com suas parcelas |

---

## 5. Principais Regras de Negócio

1. **Criação de Contrato**: O sistema recebe dados de um contrato financeiro e persiste na tabela `TbIntegracaoContrato` com sequência fixa igual a 1 e motivo de contrato financeiro de implantação (código 1).

2. **Situação do Contrato**: Todos os contratos são criados com situação "ABERTO" (código 1) e flag ativo "S".

3. **Cálculo de Valor Financiado Atual**: O valor financiado atual é calculado subtraindo o valor do IOF do valor de financiamento total.

4. **Normalização de Valores**: Todos os valores monetários são normalizados para 2 casas decimais usando arredondamento HALF_EVEN.

5. **Processamento de Parcelas**: Após criar o contrato principal, o sistema processa e persiste cada parcela individualmente na tabela `TbIntegracaoContratoParcela`.

6. **Recuperação de ID**: Após a inserção, o sistema recupera o ID do contrato criado através de consulta ordenada por data de inclusão e código.

7. **Tratamento de Erros**: Qualquer erro durante o processamento resulta em exceção customizada (`ControladoriaCargaException`) com código e mensagem específicos.

8. **Logging Estruturado**: Todo o fluxo é registrado com logs estruturados incluindo mascaramento de dados sensíveis (apenas últimos 6 caracteres do número do contrato são exibidos).

---

## 6. Relação entre Entidades

**Controladoria** (1) ----< (N) **Parcela**
- Um contrato de controladoria possui múltiplas parcelas

**Controladoria** (1) ---- (1) **ParceiroComercial**
- Um contrato de controladoria está associado a um parceiro comercial

**Atributos principais:**
- **Controladoria**: numeroContrato, codigoProduto, dataProcessamento, valorContrato, taxaJuros, quantidadeParcela, loginColaborador, etc.
- **Parcela**: numero, valor, dataVencimento
- **ParceiroComercial**: codigoParceiroComercial, codigoRegiaoParceiro, tipoAtividadeParceiro

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbIntegracaoContrato | tabela | SELECT | Consulta para recuperar o último ID de contrato criado por número de contrato e login |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbIntegracaoContrato | tabela | INSERT | Inserção de novos contratos de controladoria com todos os dados financeiros e comerciais |
| TbIntegracaoContratoParcela | tabela | INSERT | Inserção das parcelas associadas a cada contrato de controladoria |

**Banco de Dados**: DBGERENCIAL (Sybase)

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot | Arquivo de configuração da aplicação com profiles (local, des, uat, prd) |
| logback-spring.xml | leitura | Logback | Configuração de logging da aplicação |
| sboot-flex-calc-atom-controladoria-carga.yaml | leitura | Swagger Codegen | Especificação OpenAPI para geração de interfaces REST |

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
| DBGERENCIAL (Sybase) | Banco de Dados | Banco de dados Sybase onde são persistidos os contratos e parcelas de controladoria |
| Prometheus | Monitoramento | Sistema de coleta de métricas da aplicação via endpoint `/actuator/prometheus` |
| Grafana | Visualização | Dashboard para visualização de métricas coletadas pelo Prometheus |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo princípios de Clean Architecture (separação em camadas: domain, application, common)
- Uso adequado de padrões de projeto (Repository, Service, Mapper)
- Implementação de logging estruturado com mascaramento de dados sensíveis
- Tratamento de exceções customizado e bem organizado
- Uso de utilitários para normalização de dados (DateUtil, NumericUtil)
- Configuração adequada de profiles para diferentes ambientes
- Documentação via Swagger/OpenAPI
- Testes unitários, de integração e funcionais estruturados
- Uso de Lombok para redução de boilerplate

**Pontos de Melhoria:**
- Falta de validações de entrada mais robustas nos DTOs
- Alguns testes estão vazios ou incompletos (ControladoriaCargaServiceTest, ApplicationTest)
- Poderia ter mais documentação inline (JavaDoc) nas classes de serviço
- O tratamento de transações poderia ser mais explícito
- Falta de testes de carga/performance documentados

---

## 14. Observações Relevantes

1. **Segurança**: O sistema utiliza autenticação básica (basicAuth) conforme especificação Swagger, mas os detalhes de implementação não estão visíveis nos arquivos fornecidos.

2. **Auditoria**: Todas as inserções incluem campos de auditoria (DsLogin, FlAtivo, DtInclusao) preenchidos automaticamente.

3. **Infraestrutura**: O projeto está preparado para deploy em OpenShift (Google Cloud Platform) conforme jenkins.properties.

4. **Monitoramento**: Implementação completa de observabilidade com Prometheus, Grafana e Spring Actuator, incluindo dashboards pré-configurados.

5. **Profiles**: O sistema suporta múltiplos ambientes (local, des, uat, prd) com configurações específicas de datasource para cada um.

6. **Versionamento**: A API está versionada (v1) no path, facilitando evolução futura.

7. **Padrão de Nomenclatura**: O código segue convenções do Banco Votorantim com prefixos específicos (sboot-flex-calc-atom).

8. **Dependências Corporativas**: Utiliza bibliotecas internas do Banco Votorantim (arqt-base, microservices-error, trilha-auditoria-web).