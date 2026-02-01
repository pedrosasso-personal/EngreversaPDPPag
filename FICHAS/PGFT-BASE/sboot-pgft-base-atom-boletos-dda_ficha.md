# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-pgft-base-atom-boletos-dda** é um serviço atômico REST desenvolvido em Java com Spring Boot para gerenciar e consultar boletos DDA (Débito Direto Autorizado) de clientes do Banco Votorantim. O sistema permite listar boletos DDA com base em filtros como CPF/CNPJ, período de vencimento e situação de pagamento (pagos ou em aberto). O serviço consulta informações detalhadas dos boletos incluindo dados do beneficiário, pagador, encargos (juros, multas, descontos), cálculos de valores e histórico de baixas operacionais e efetivas.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal que inicializa a aplicação Spring Boot |
| `BoletosDDAController` | Controller REST que expõe o endpoint de listagem de boletos DDA |
| `BoletoDDAService` | Serviço de domínio que orquestra a lógica de negócio para recuperação e mapeamento de boletos |
| `BoletoRepositoryImpl` | Implementação do repositório que acessa o banco de dados Sybase usando JDBI |
| `BoletoDDARepository` | Interface do repositório com métodos de acesso a dados |
| `BoletoConfiguration` | Configuração dos beans de serviço e repositório |
| `DatabaseConfiguration` | Configuração do datasource e JDBI para acesso ao banco DBPGF_TES |
| `OpenApiConfiguration` | Configuração do Swagger/OpenAPI para documentação da API |
| `ConverteParaRepresentation` | Conversor que transforma objetos de domínio em objetos de representação (DTOs) |
| `Boleto` | Entidade de domínio representando um boleto DDA |
| `BaixaOperacional` | Entidade representando baixa operacional de boleto |
| `BaixaEfetiva` | Entidade representando baixa efetiva de boleto |
| `CalculoTitulo` | Entidade com cálculos de valores do título |
| `Desconto`, `Encargo` | Entidades representando descontos, juros e multas |
| `*RowMapper` | Classes responsáveis por mapear ResultSet do banco para objetos de domínio |

---

## 3. Tecnologias Utilizadas

- **Java 11** (OpenJDK 11 com OpenJ9)
- **Spring Boot 2.x** (framework principal)
- **Spring Web** (para APIs REST)
- **Spring Security OAuth2** (autenticação JWT)
- **JDBI 3.12.0** (framework de acesso a dados SQL)
- **Sybase jConnect 4 (7.07-ESD-5)** (driver JDBC para Sybase)
- **Swagger/Springfox 2.9.2** (documentação de API)
- **Lombok** (redução de boilerplate)
- **Logback** (logging com formato JSON)
- **Micrometer/Prometheus** (métricas e monitoramento)
- **Maven** (gerenciamento de dependências e build)
- **Docker** (containerização)
- **Undertow** (servidor de aplicação embarcado)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/cliente/dda/boletos` | `BoletosDDAController` | Lista os boletos DDA de um cliente com base em filtros (CPF/CNPJ, período, situação de pagamento) |

**Parâmetros:**
- Header: `numeroCpfCnpj` (obrigatório)
- Body: `ListaBoletosDDARequestRepresentation` (dataInicio, dataFim, boletosPagos)

**Resposta:** `ListaBoletosDDAResponseRepresentation` contendo lista de boletos com todos os detalhes

---

## 5. Principais Regras de Negócio

1. **Filtro de Boletos por Situação**: O sistema permite filtrar boletos pagos (código 2) ou em aberto (código 1) através do parâmetro `boletosPagos`

2. **Consulta por Período**: Boletos são filtrados pela data de vencimento dentro do intervalo especificado (dataInicio e dataFim)

3. **Mapeamento de Encargos**: Para cada boleto recuperado, o sistema busca e associa:
   - Descontos aplicáveis
   - Juros e multas
   - Cálculos de valores totais a cobrar

4. **Tratamento Especial para Cartão de Crédito**: Boletos com código de espécie 31 (cartão de crédito) possuem lógica diferenciada para recuperação de baixas operacionais, buscando registros dos últimos 14 dias antes do vencimento

5. **Baixas Operacionais e Efetivas**: O sistema recupera histórico de baixas operacionais (não canceladas) e baixas efetivas associadas aos títulos

6. **Conversão de Indicadores**: Indicadores do tipo "S"/"N" são convertidos para boolean (true/false)

7. **Filtro de Situação de Título**: Apenas títulos com situação DDA em (1,5) e situação de pagamento em (5,11,12) são retornados

---

## 6. Relação entre Entidades

**Entidade Principal: Boleto**
- Contém informações do beneficiário original e final
- Contém informações do pagador
- Possui relacionamento 1:N com `CalculoTitulo` (lista de cálculos)
- Possui relacionamento 1:N com `Desconto` (lista de descontos)
- Possui relacionamento 1:N com `Encargo` (juros e multas)
- Possui relacionamento 1:N com `BaixaOperacional` (histórico de baixas operacionais)
- Possui relacionamento 1:N com `BaixaEfetiva` (histórico de baixas efetivas)

**Relacionamentos:**
- `Boleto` → `CalculoTitulo` (1:N) - via `idTituloDDA`
- `Boleto` → `Desconto` (1:N) - via `idTituloDDA`
- `Boleto` → `Encargo` (1:N) - via `idTituloDDA` (juros e multas)
- `Boleto` → `BaixaOperacional` (1:N) - via `idTituloDDA`
- `Boleto` → `BaixaEfetiva` (1:N) - via `idTituloDDA`
- `BaixaEfetiva` → `BaixaOperacional` (N:1) - via `idTituloBaixaOperacional`

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| `TbTituloDDA` | Tabela | SELECT | Tabela principal de títulos DDA contendo informações do boleto, beneficiário, pagador, valores e datas |
| `TbDescontoTituloDDA` | Tabela | SELECT | Tabela de descontos aplicáveis aos títulos DDA |
| `TbMultaTituloDDA` | Tabela | SELECT | Tabela de multas associadas aos títulos DDA |
| `TbJuroTituloDDA` | Tabela | SELECT | Tabela de juros associados aos títulos DDA |
| `TbCalculoTituloDDA` | Tabela | SELECT | Tabela com cálculos de valores (juros, multa, desconto, total a cobrar) |
| `TbTituloDDABaixaOperacional` | Tabela | SELECT | Tabela de baixas operacionais dos títulos DDA |
| `TbTituloDDABaixaEfetiva` | Tabela | SELECT | Tabela de baixas efetivas dos títulos DDA |

**Banco de Dados:** DBPGF_TES (Sybase)

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `application.yml` | Leitura | Spring Boot | Arquivo de configuração principal da aplicação com profiles e datasources |
| `application-local.yml` | Leitura | Spring Boot | Configurações específicas para ambiente local |
| `logback-spring.xml` | Leitura | Logback | Configuração de logging com formato JSON para stdout |
| `*.sql` (resources) | Leitura | JDBI/BoletoRepositoryImpl | Arquivos SQL com queries parametrizadas para consultas ao banco |
| `sboot-pgft-base-atom-boletos-dda.yaml` | Leitura | Swagger Codegen | Especificação OpenAPI para geração de interfaces e DTOs |

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
| Banco de Dados Sybase (DBPGF_TES) | Database | Banco de dados principal contendo informações de títulos DDA, baixas, encargos e cálculos |
| Serviço de Autenticação OAuth2/JWT | API Externa | Validação de tokens JWT através do endpoint jwks.json para autenticação e autorização |

**Endpoints de Autenticação:**
- DES: `https://api-digitaldes.bancovotorantim.com.br/openid/connect/jwks.json`
- PRD: `https://api-digital.bancovotorantim.com.br/openid/connect/jwks.json`
- UAT: `https://api-digitaluat.bancovotorantim.com.br/openid/connect/jwks.json`

---

## 13. Avaliação da Qualidade do Código

**Nota:** 7.5/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (controller, service, repository, domain)
- Uso adequado de frameworks modernos (Spring Boot, JDBI)
- Implementação de RowMappers específicos para cada entidade
- Uso de Lombok para reduzir boilerplate
- Configuração adequada de profiles para diferentes ambientes
- Documentação OpenAPI/Swagger implementada
- Logs estruturados em JSON
- Uso de injeção de dependências e configuração via beans

**Pontos de Melhoria:**
- Tratamento de exceções genérico no controller (catch Exception), poderia ser mais específico
- Código comentado no serviço (método `mapearBaixaEfetiva`) deveria ser removido ou implementado
- Falta de validações de entrada mais robustas
- Alguns métodos do serviço são extensos e poderiam ser refatorados
- Ausência de testes unitários nos arquivos enviados (marcados como NAO_ENVIAR)
- Conversão manual entre entidades e representations poderia usar bibliotecas como MapStruct
- Alguns nomes de campos no banco não seguem convenções Java (ex: CdTituloDDA)
- Falta de documentação JavaDoc nas classes e métodos principais

---

## 14. Observações Relevantes

1. **Arquitetura Modular**: O projeto está dividido em dois módulos Maven (domain e application), seguindo boas práticas de separação de conceitos

2. **Segurança**: A aplicação possui integração com OAuth2/JWT, mas está comentada na classe Application (`@EnableResourceServer`), sugerindo que pode estar desabilitada em alguns ambientes

3. **Monitoramento**: Implementa endpoints do Spring Actuator na porta 9090 para health checks e métricas Prometheus

4. **Containerização**: Possui Dockerfile configurado com imagem OpenJDK 11 com OpenJ9 para otimização de memória

5. **CI/CD**: Configurado para deploy em OpenShift (OCP) na plataforma Google Cloud, com pipelines Jenkins

6. **Ambientes**: Suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas

7. **Banco de Dados Legacy**: Utiliza Sybase, um banco de dados legado, com queries SQL nativas armazenadas em arquivos separados

8. **Performance**: Uso de AsyncAppender no Logback para não bloquear threads durante logging

9. **Lazy Initialization**: Configurado para inicialização lazy de beans Spring para melhorar tempo de startup

10. **Arquitetura de Testes**: Estrutura preparada para testes unitários, integração e funcionais em diretórios separados, embora os testes não tenham sido incluídos na análise