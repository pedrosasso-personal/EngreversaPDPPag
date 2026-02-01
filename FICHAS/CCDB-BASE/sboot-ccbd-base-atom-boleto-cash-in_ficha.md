# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-ccbd-base-atom-boleto-cash-in** é um microserviço atômico desenvolvido em Spring Boot para gerenciar operações de boletos bancários do tipo "Cash In" (recebimento). O sistema permite a geração e atualização de boletos bancários, incluindo o cadastro de beneficiários, pagadores e endereços, além do controle de status e sequenciamento de "nosso número". Opera com banco de dados SQL Server e expõe APIs REST para integração.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal que inicializa a aplicação Spring Boot com segurança OAuth2 |
| **BoletoCashInController** | Controlador REST que expõe endpoints para gerar e atualizar boletos |
| **GerarBoletoService** | Serviço de domínio responsável pela lógica de geração de boletos |
| **AtualizarBoletoService** | Serviço de domínio responsável pela lógica de atualização de boletos |
| **BoletoCashInRepository** | Interface de repositório para operações de banco de dados |
| **BoletoCashInRepositoryImpl** | Implementação do repositório usando JDBI |
| **BoletoDomain** | Entidade de domínio representando um boleto completo |
| **ClienteDomain** | Entidade de domínio representando beneficiário ou pagador |
| **TituloBoletoDomain** | Entidade de domínio representando informações do título do boleto |
| **BoletoCashinEntity** | Entidade de persistência para tabela de boletos |
| **ClienteCashinEntity** | Entidade de persistência para tabela de clientes |
| **EnderecoPessoaSacadoEntity** | Entidade de persistência para endereços de pagadores |
| **SequenciaNossoNumeroEntity** | Entidade de persistência para controle de sequência de nosso número |

---

## 3. Tecnologias Utilizadas

- **Spring Boot** (framework principal)
- **Spring Security OAuth2** (autenticação e autorização)
- **JDBI 3.9.1** (acesso a banco de dados)
- **Microsoft SQL Server** (banco de dados)
- **Swagger/OpenAPI 2.9.2** (documentação de APIs)
- **Springfox** (geração de documentação Swagger)
- **Lombok** (redução de boilerplate)
- **Spring Actuator** (monitoramento e métricas)
- **Micrometer Prometheus** (métricas)
- **Maven** (gerenciamento de dependências)
- **Java 11** (linguagem e runtime)
- **Docker** (containerização)
- **Logback** (logging)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/banco-digital/contas/boletos/cashin` | BoletoCashInController | Gera um novo boleto cash-in |
| PUT | `/v1/banco-digital/contas/boletos/cashin/{nossoNumero}` | BoletoCashInController | Atualiza um boleto existente com linha digitável e código de barras |

**Headers obrigatórios**: codigoBanco, numeroAgencia, numeroConta, tipoConta

---

## 5. Principais Regras de Negócio

1. **Geração de Boleto**:
   - Cadastra cliente beneficiário (se não existir)
   - Cadastra cliente pagador/sacado (se não existir)
   - Gera sequência de "nosso número" única por convênio
   - Define data de vencimento baseada em dias configuráveis (padrão: 7 dias)
   - Status inicial: "Aguardando emissão"
   - Prazo de baixa automática: 120 dias
   - Tipo de espécie: Duplicata Mercantil
   - Não aceita valor divergente

2. **Atualização de Boleto**:
   - Apenas boletos com status "Aguardando emissão" podem ser atualizados
   - Linha digitável e código de barras só podem ser cadastrados uma vez
   - Atualiza status para "Emitido" após inclusão dos dados bancários

3. **Validações**:
   - Conta bancária obrigatória e válida
   - Beneficiário padrão: Banco BV S/A (código pessoa 1)
   - Controle transacional para geração de nosso número

---

## 6. Relação entre Entidades

**BoletoDomain** (agregado raiz)
- Contém 1 **StatusBoletoDomain**
- Contém 1 **ClienteDomain** (beneficiário)
- Contém 1 **ClienteDomain** (pagador)
  - Pagador contém 1 **EnderecoDomain**
- Contém 1 **TituloBoletoDomain**

**Relacionamentos de persistência**:
- BoletoCashinEntity → ClienteCashinEntity (beneficiário) [N:1]
- BoletoCashinEntity → ClienteCashinEntity (pagador) [N:1]
- BoletoCashinEntity → EnderecoPessoaSacadoEntity [1:1]
- ClienteCashinEntity → SequenciaNossoNumeroEntity [1:N]

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| CCBDBoletoCashIn.TbClienteCashin | tabela | SELECT | Consulta se cliente já está cadastrado e busca dados de clientes |
| CCBDBoletoCashIn.TbSequenciaNossoNumero | tabela | SELECT | Consulta sequência do nosso número por convênio e cliente |
| CCBDBoletoCashIn.TbBoletoCashin | tabela | SELECT | Consulta dados completos de boleto por nosso número |
| CCBDBoletoCashIn.TbEnderecoPessoaSacado | tabela | SELECT | Consulta endereço do pagador vinculado ao boleto |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| CCBDBoletoCashIn.TbClienteCashin | tabela | INSERT | Insere novo cliente (beneficiário ou pagador) |
| CCBDBoletoCashIn.TbSequenciaNossoNumero | tabela | INSERT/UPDATE | Insere ou incrementa sequência de nosso número (transacional) |
| CCBDBoletoCashIn.TbBoletoCashin | tabela | INSERT | Insere novo boleto cash-in |
| CCBDBoletoCashIn.TbBoletoCashin | tabela | UPDATE | Atualiza status, linha digitável e código de barras |
| CCBDBoletoCashIn.TbEnderecoPessoaSacado | tabela | INSERT | Insere endereço do pagador |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot | Configurações da aplicação por ambiente (local, des, qa, uat, prd) |
| logback-spring.xml | leitura | Logback | Configuração de logs (console e JSON) |
| *.sql (10 arquivos) | leitura | JDBI/BoletoCashInRepositoryImpl | Queries SQL para operações de banco de dados |
| sboot-ccbd-base-atom-boleto-cash-in.yaml | leitura | Swagger Codegen | Especificação OpenAPI para geração de interfaces |

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
| OAuth2 JWT Provider | API Externa | Autenticação via JWT (https://api-digitaldes.bancovotorantim.com.br/openid/connect/jwks.json) |
| SQL Server (DBCCBD) | Banco de Dados | Banco de dados principal para persistência de boletos e clientes |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem organizada em camadas (domain, application)
- Uso adequado de padrões como Repository, Service e Mapper
- Separação clara entre entidades de domínio e persistência
- Uso de Lombok para reduzir boilerplate
- Configuração adequada de profiles por ambiente
- Documentação OpenAPI/Swagger
- Uso de transações para operações críticas (nosso número)

**Pontos de Melhoria:**
- Tratamento de exceções genérico (catch Exception) em vários pontos
- Logs em português misturados com código em inglês
- Falta de validações mais robustas nos DTOs
- Ausência de testes unitários nos arquivos analisados
- Hardcoding de valores em alguns enums (ex: DadosBeneficiarioEnum)
- Uso de String para representar datas em alguns pontos (DateUtil)
- Falta de documentação JavaDoc nas classes
- Retorno de ResponseEntity com tipos genéricos sem especificação adequada
- Mensagens de erro poderiam ser mais descritivas e padronizadas

---

## 14. Observações Relevantes

1. **Segurança**: O sistema utiliza OAuth2 com JWT para autenticação, configurado via Spring Security Resource Server.

2. **Monitoramento**: Expõe métricas via Actuator na porta 9090 e integração com Prometheus.

3. **Auditoria**: Utiliza biblioteca BV de trilha de auditoria (springboot-arqt-base-trilha-auditoria-web).

4. **Transações**: A geração de nosso número utiliza transação explícita no SQL Server (BEGIN TRAN/COMMIT TRAN) para garantir atomicidade.

5. **Configuração por Ambiente**: Suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas.

6. **Containerização**: Preparado para deploy em containers Docker com imagem baseada em OpenJDK 11.

7. **Infraestrutura**: Configurado para deploy em OpenShift (Google Cloud Platform) conforme jenkins.properties.

8. **Versionamento**: API versionada (v1) no path dos endpoints.

9. **Dados do Beneficiário**: O Banco BV é hardcoded como beneficiário padrão (código pessoa 1, CNPJ 59588111000103).

10. **Limitações Identificadas**: Não há suporte para cancelamento ou consulta de boletos, apenas geração e atualização.