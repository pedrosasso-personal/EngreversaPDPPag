# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-sitp-base-atom-consulta-transacao-spb** é um serviço atômico REST desenvolvido em Spring Boot que tem como objetivo consultar transações do Sistema de Pagamentos Brasileiro (SPB) armazenadas em banco de dados Sybase. O serviço expõe um endpoint REST que permite listar transações ITP (Internet Transaction Processing) com base em filtros de tipo de lançamento e código de grupo de produto. A aplicação segue uma arquitetura hexagonal (ports and adapters) com separação clara entre camadas de domínio, aplicação e infraestrutura.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application.java` | Classe principal Spring Boot que inicializa a aplicação e habilita o Resource Server OAuth2 |
| `ListarTransacoesItpController.java` | Controlador REST que expõe o endpoint `/v1/atacado/listarTransacoesItp` para consulta de transações |
| `ConsultaTransacaoSpbService.java` | Serviço de domínio que orquestra a lógica de negócio para consulta de transações |
| `TransactionalListarTransacoesItpService.java` | Extensão do serviço de domínio com suporte transacional |
| `ConsultaTransacaoSpb.java` | Entidade de domínio que representa uma transação SPB |
| `ConsultaTransacaoSpbRepository.java` | Interface (port) que define o contrato de acesso a dados |
| `JdbiConsultaTransacaoSpbRepository.java` | Implementação do repositório usando JDBI para acesso ao banco Sybase |
| `ConsultaTransacaoSpbMapper.java` | Mapper que converte entidades de domínio em representações REST |
| `ConsultaTransacaoSpbRowMapper.java` | Mapper JDBI que converte ResultSet em entidades de domínio |
| `ConsultaTransacaoSpbConfiguration.java` | Classe de configuração Spring que define os beans da aplicação |
| `OpenApiConfiguration.java` | Configuração do Swagger/OpenAPI para documentação da API |

---

## 3. Tecnologias Utilizadas

- **Java 11** - Linguagem de programação
- **Spring Boot 2.x** - Framework principal
- **Spring Security OAuth2** - Autenticação e autorização via JWT
- **JDBI 3.9.1** - Framework de acesso a dados (alternativa ao JPA)
- **Sybase jConnect 16.3** - Driver JDBC para banco Sybase
- **Swagger/Springfox 2.9.2** - Documentação de API REST
- **Lombok** - Redução de boilerplate code
- **Logback** - Framework de logging com suporte a JSON
- **Spring Actuator** - Monitoramento e métricas
- **Micrometer/Prometheus** - Coleta de métricas
- **JUnit 5** - Framework de testes unitários
- **Mockito** - Framework de mocks para testes
- **RestAssured** - Testes de API REST
- **Pact** - Testes de contrato (contract testing)
- **Maven** - Gerenciamento de dependências e build
- **Docker** - Containerização da aplicação

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/atacado/listarTransacoesItp` | `ListarTransacoesItpController` | Lista transações ITP do SPB filtradas por tipo de lançamento e código de grupo de produto |

**Exemplo de Request:**
```json
{
  "tipoLancamento": "S",
  "codigoGrupoProduto": 125487
}
```

**Exemplo de Response:**
```json
{
  "listaTransacoes": [
    {
      "codigoTransacao": 15,
      "nomeTransacao": "Nome da Transação",
      "mnemonicoTransacao": "MNE"
    }
  ]
}
```

---

## 5. Principais Regras de Negócio

1. **Consulta de Transações SPB**: O sistema consulta transações do Sistema de Pagamentos Brasileiro com base em dois critérios obrigatórios: tipo de lançamento (ex: "S" para saída) e código de grupo de produto.

2. **Filtragem por Tipo de Lançamento**: As transações são filtradas pelo campo `Tip_Lancamento` que indica a direção do fluxo financeiro.

3. **Filtragem por Grupo de Produto**: As transações são filtradas pelo campo `Cod_Grupo_Produto` que categoriza o tipo de produto financeiro.

4. **Retorno de Dados Distintos**: A consulta retorna apenas registros distintos (DISTINCT) para evitar duplicações.

5. **Autenticação JWT**: Todas as requisições devem ser autenticadas via token JWT Bearer fornecido no header Authorization.

---

## 6. Relação entre Entidades

**Entidade Principal:**
- `ConsultaTransacaoSpb`: Representa uma transação do SPB com os atributos:
  - `codigoTransacao` (BigDecimal): Código identificador da transação
  - `nomeTransacao` (String): Nome descritivo da transação
  - `mnemonicoTransacao` (String): Código mnemônico da transação

**Relacionamentos no Banco de Dados:**
- `TBL_TRANSACAO_SPB` (1) ←→ (N) `TBL_DESCRICAO_TRANSACAO_SPB`: Relacionamento entre transações e suas descrições através do campo `Cod_Transacao`

**Fluxo de Dados:**
```
Request → Controller → Service → Repository → Database
                ↓
Response ← Mapper ← Domain Entity ← RowMapper ← ResultSet
```

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TBL_TRANSACAO_SPB | Tabela | SELECT | Tabela principal que armazena as transações do Sistema de Pagamentos Brasileiro |
| TBL_DESCRICAO_TRANSACAO_SPB | Tabela | SELECT | Tabela que contém as descrições e metadados das transações SPB, incluindo tipo de lançamento e grupo de produto |

**Query SQL Executada:**
```sql
SELECT DISTINCT T.Cod_Transacao as cdTransacao,
                DT.Nom_Transacao as nmTransacao,
                DT.Mne_Transacao as mneTransacao
FROM TBL_TRANSACAO_SPB T
INNER JOIN TBL_DESCRICAO_TRANSACAO_SPB DT ON DT.Cod_Transacao = T.Cod_Transacao
WHERE DT.Tip_Lancamento = :tpLancamento
  AND DT.Cod_Grupo_Produto = :cdGrupoProduto
```

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | Spring Boot (startup) | Arquivo de configuração principal da aplicação com profiles (local, des, qa, uat, prd) |
| application-test.yml | Leitura | Testes (startup) | Configurações específicas para execução de testes |
| logback-spring.xml | Leitura | Logback (runtime) | Configuração de logging com formato JSON para stdout |
| getConsultaTransacaoSpb.sql | Leitura | JdbiConsultaTransacaoSpbRepository | Query SQL para consulta de transações SPB |
| springboot-sitp-base-transacao-pagamento.json | Leitura | Swagger Codegen (build time) | Especificação OpenAPI/Swagger usada para gerar interfaces e DTOs |

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
| API Gateway (OAuth2/JWT) | Autenticação | Integração com servidor de autorização para validação de tokens JWT via endpoint JWK (diferentes URLs por ambiente: des, qa, uat, prd) |
| Banco de Dados Sybase (DBITP) | Banco de Dados | Conexão com banco Sybase para consulta de transações SPB. Configurações variam por ambiente com diferentes hosts e portas |
| Prometheus | Monitoramento | Exposição de métricas via endpoint `/actuator/prometheus` para coleta pelo Prometheus |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura hexagonal bem implementada com separação clara de responsabilidades (domain, application, infrastructure)
- Uso adequado de padrões como Repository, Service e Mapper
- Boa cobertura de testes (unitários, integração e funcionais)
- Configuração adequada de profiles para diferentes ambientes
- Uso de Lombok para reduzir boilerplate
- Documentação via Swagger/OpenAPI
- Implementação de segurança com OAuth2/JWT
- Uso de JDBI ao invés de JPA para queries mais performáticas
- Configuração de logging estruturado (JSON)
- Implementação de health checks e métricas

**Pontos de Melhoria:**
- Falta tratamento de exceções customizado (ErrorMessage existe mas não é utilizado)
- Ausência de validações de entrada mais robustas nos DTOs
- Testes funcionais e de integração estão vazios/incompletos
- Falta documentação inline (JavaDoc) em algumas classes
- Poderia ter paginação no endpoint de listagem
- Ausência de cache para consultas frequentes
- Configuração de pool de conexões poderia ser mais detalhada

O código demonstra maturidade arquitetural e boas práticas de desenvolvimento, mas há espaço para melhorias em tratamento de erros, validações e completude dos testes.

---

## 14. Observações Relevantes

1. **Multi-ambiente**: A aplicação está preparada para rodar em múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas para cada um, incluindo diferentes URLs de banco de dados e servidores de autenticação.

2. **Segurança**: O sistema utiliza autenticação via JWT com validação de tokens através de JWK (JSON Web Key) do API Gateway. A anotação `@EnableResourceServer` indica que a aplicação atua como Resource Server OAuth2.

3. **Infraestrutura como Código**: O projeto inclui arquivo `infra.yml` com configurações para deploy em Kubernetes/OpenShift, incluindo ConfigMaps, Secrets, probes de liveness/readiness e volumes.

4. **Containerização**: Dockerfile otimizado usando imagem Alpine com OpenJ9 para reduzir tamanho e consumo de memória.

5. **Observabilidade**: Implementa trilha de auditoria customizada (`votorantim.arqt.AUDIT`) e exposição de métricas para Prometheus na porta 9090.

6. **Charset Específico**: A conexão com Sybase utiliza charset `iso_1` e configurações específicas como `DISABLE_UNICHAR_SENDING=true` e `LITERAL_PARAMS=true`.

7. **Testes de Contrato**: Preparado para testes de contrato com Pact, embora a implementação esteja comentada.

8. **Geração de Código**: Utiliza Swagger Codegen Maven Plugin para gerar automaticamente interfaces de API e DTOs a partir da especificação OpenAPI.

9. **Arquitetura de Testes**: Estrutura de testes bem organizada em três níveis (unit, integration, functional) com suporte a profiles Maven específicos.

10. **Pool de Conexões**: Configurado com HikariCP com valores conservadores (max: 2, min: 1) adequados para um serviço atômico de consulta.