# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-spag-base-atom-lancamento-gestao-caixa** é um serviço atômico REST desenvolvido para consultar e fornecer informações sobre lançamentos financeiros relacionados à gestão de caixa do sistema SPAG (Sistema de Pagamentos). O serviço expõe três endpoints principais que retornam lançamentos sintéticos e analíticos (entrada e saída) filtrados por data de movimento, consultando diretamente o banco de dados DBSPAG (SQL Server). O sistema é utilizado para apoiar operações de gestão de caixa, fornecendo visões consolidadas e detalhadas dos lançamentos financeiros.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal Spring Boot que inicializa a aplicação e habilita o servidor de recursos OAuth2 |
| **LancamentoGestaoCaixaController** | Controlador REST que expõe os três endpoints de consulta de lançamentos |
| **LancamentoGestaoCaixaService** | Serviço de domínio que orquestra as chamadas ao repositório |
| **JdbiLancamentoGestaoCaixaRepository** | Interface de repositório JDBI que executa as queries SQL para buscar lançamentos |
| **LancamentoGestaoCaixaConfiguration** | Classe de configuração Spring que define os beans necessários (JDBI, repositório, serviço) |
| **OpenApiConfiguration** | Configuração do Swagger/OpenAPI para documentação dos endpoints |
| **LancamentosAnaliticoSpag** | Entidade de domínio representando lançamentos analíticos |
| **LancamentosSinteticoSpag** | Entidade de domínio representando lançamentos sintéticos |
| **LancamentosAnaliticoSpagMapper** | Mapper que converte entidades de domínio em representações REST |
| **LancamentosSinteticoSpagMapper** | Mapper que converte entidades sintéticas em representações REST |
| **LancamentosAnaliticoSpagRowMapper** | RowMapper JDBI para mapear ResultSet em entidades analíticas |
| **LancamentosSinteticoSpagRowMapper** | RowMapper JDBI para mapear ResultSet em entidades sintéticas |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Spring Security OAuth2** (autenticação via JWT)
- **JDBI 3.9.1** (acesso a dados SQL)
- **SQL Server** (banco de dados)
- **Microsoft SQL Server JDBC Driver 7.4.0**
- **Springfox/Swagger 3.0.0** (documentação de API)
- **Lombok** (redução de boilerplate)
- **Spring Boot Actuator** (monitoramento e métricas)
- **Micrometer + Prometheus** (métricas)
- **Logback** (logging)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Arquitetura Hexagonal/Ports and Adapters** (padrão arquitetural)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/lancamento-gestao-caixa/getLancamentosSinteticoSpag` | LancamentoGestaoCaixaController | Retorna lançamentos sintéticos (consolidados) do SPAG para uma data de movimento |
| GET | `/v1/lancamento-gestao-caixa/getLancamentosEntradaSpag` | LancamentoGestaoCaixaController | Retorna lançamentos analíticos de entrada/recebimento do SPAG para uma data de movimento |
| GET | `/v1/lancamento-gestao-caixa/getLancamentosSaidaSpag` | LancamentoGestaoCaixaController | Retorna lançamentos analíticos de saída/pagamento do SPAG para uma data de movimento |

**Observação:** Todos os endpoints requerem autenticação via token JWT (OAuth2) e recebem o parâmetro `dtMovimento` no formato "dd/MM/yyyy".

---

## 5. Principais Regras de Negócio

1. **Filtro por CNPJ do Banco Votorantim**: Todas as consultas filtram lançamentos onde o CNPJ '01858774000110' (Banco Votorantim) aparece como remetente ou favorecido.

2. **Filtro por Status de Lançamento**: Exclui lançamentos com status 4, 8 ou 99 (provavelmente cancelados, rejeitados ou inválidos).

3. **Filtro por Origem de Operação**: Considera apenas lançamentos com origem 2, 61, 71, 72 ou 73.

4. **Tratamento de Tipo de Lançamento**: 
   - Lançamentos de entrada (tipo 'E') mantêm o valor positivo
   - Lançamentos de saída (tipo diferente de 'E') têm o valor multiplicado por -1

5. **Exclusão de Transferências Internas**: Exclui transferências entre bancos 413 e 655 (provavelmente transferências internas do grupo).

6. **Agregação Sintética**: Na consulta sintética, os valores são agregados (SUM) por origem de operação e código de liquidação.

7. **Conversão de Data**: O sistema recebe datas no formato brasileiro (dd/MM/yyyy) e converte para LocalDate para consulta no banco.

---

## 6. Relação entre Entidades

**Entidades de Domínio:**

- **LancamentosSinteticoSpag**: Representa lançamentos consolidados
  - Atributos: nuOrigemOperacao, cdLiquidacao, nmContaOrigem, nmLiquidacao, vrLancamento

- **LancamentosAnaliticoSpag**: Representa lançamentos detalhados
  - Atributos: cdLancamento, cdOrigem, nmConta, cdLiquidacao, vrLancamento, nmCliente, nmLiquidacao, nmHistorico, cdOperacao, dtInicio, dtLiquidacao, dtDecorrida, nmLoginAutorizante, vlStatus

**Relacionamentos:**
- Não há relacionamentos diretos entre as entidades no código (são DTOs de consulta)
- Ambas representam visões diferentes dos mesmos dados de lançamentos do banco DBSPAG

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbLancamento | Tabela | SELECT | Tabela principal de lançamentos financeiros do SPAG |
| TbLancamentoPessoa | Tabela | SELECT | Tabela com informações de pessoas (remetente/favorecido) relacionadas aos lançamentos |

**Observação:** As tabelas são consultadas com hint `WITH (NOLOCK)` para evitar bloqueios de leitura.

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | Spring Boot (resources) | Arquivo de configuração da aplicação com datasources, OAuth2, profiles |
| logback-spring.xml | Leitura | Logback (resources ou /usr/etc/log) | Configuração de logging da aplicação |
| getLancamentosEntradaSpag.sql | Leitura | JdbiLancamentoGestaoCaixaRepository | Query SQL para buscar lançamentos de entrada |
| getLancamentosSaidaSpag.sql | Leitura | JdbiLancamentoGestaoCaixaRepository | Query SQL para buscar lançamentos de saída |
| getLancamentosSinteticoSpag.sql | Leitura | JdbiLancamentoGestaoCaixaRepository | Query SQL para buscar lançamentos sintéticos |

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
| API Gateway OAuth2 | Autenticação | Validação de tokens JWT via JWK endpoint (URLs variam por ambiente: des, qa, uat, prd) |
| Banco de Dados DBSPAG (SQL Server) | Banco de Dados | Consulta de lançamentos financeiros em diferentes ambientes (SQLBVFDES05, SQLBVFQA05, SQLBVFUAT05, SQLSPAGCONSULTA) |
| Prometheus | Monitoramento | Exportação de métricas via endpoint /actuator/prometheus |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura hexagonal (domain, application, infrastructure)
- Uso adequado de padrões como Repository, Service, Mapper
- Configuração clara de profiles para diferentes ambientes
- Documentação de API com Swagger
- Uso de Lombok para reduzir boilerplate
- Testes estruturados em unit, integration e functional
- Configuração de segurança OAuth2 implementada

**Pontos de Melhoria:**
- Queries SQL embutidas em arquivos separados, mas com lógica complexa e campos vazios (desc_conta, nom_liquidacao, historico, etc.) que sugerem incompletude
- Falta de tratamento de exceções específico nos controllers (apenas retorna 404 genérico)
- Ausência de validação de entrada nos endpoints (formato de data, valores nulos)
- Mappers com lógica simples que poderiam usar bibliotecas como MapStruct
- Falta de paginação nos endpoints que retornam listas
- Código com alguns comentários em português misturados com inglês
- Ausência de cache para consultas frequentes
- Falta de logs estruturados para auditoria de consultas

---

## 14. Observações Relevantes

1. **CNPJ Hardcoded**: O CNPJ '01858774000110' está hardcoded nas queries SQL, o que pode dificultar manutenção e reutilização do código.

2. **Campos Vazios nas Queries**: Várias queries retornam campos com valores vazios (desc_conta = '', nom_liquidacao = '', etc.), sugerindo que a implementação pode estar incompleta ou que esses campos são preenchidos por outra camada não visível no código fornecido.

3. **Segurança**: O sistema utiliza OAuth2 com JWT, mas endpoints do Actuator e Swagger estão configurados como públicos, o que pode ser um risco em produção.

4. **Multi-ambiente**: Boa configuração para múltiplos ambientes (local, des, qa, uat, prd) com diferentes datasources e configurações de segurança.

5. **Monitoramento**: Integração com Prometheus e Grafana configurada para observabilidade.

6. **Containerização**: Dockerfile presente para deploy em containers, usando imagem base Java 11 customizada do Banco Votorantim.

7. **Infraestrutura como Código**: Arquivo infra.yml presente com configurações para deploy em Kubernetes/OpenShift.

8. **Ausência de Testes**: Os arquivos de teste não foram enviados, mas a estrutura sugere cobertura de testes unitários, integração e funcionais.