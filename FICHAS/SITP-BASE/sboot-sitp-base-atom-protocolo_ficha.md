# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-sitp-base-atom-protocolo** é um microserviço atômico desenvolvido em Java com Spring Boot, responsável por consultar e gerenciar protocolos de transações financeiras do sistema SITP (Sistema de Integração de Transações de Pagamento). O serviço expõe uma API REST para consulta de protocolos ITP/PGFT, integrando-se com um banco de dados Sybase através de stored procedures. O sistema valida solicitações, executa consultas no banco de dados e retorna informações detalhadas sobre protocolos de pagamento, incluindo dados de movimentação, beneficiários e remetentes.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application.java` | Classe principal de inicialização do Spring Boot |
| `ProtocoloController.java` | Controlador REST que implementa o delegate da API, recebe requisições HTTP |
| `ProtocoloService.java` | Camada de serviço contendo a lógica de negócio para consulta de protocolos |
| `ConsultarProtocoloV2Procedure.java` | Encapsula a chamada à stored procedure `PrConsultarProtocoloV2` no Sybase |
| `ProtocoloResponse.java` | Entidade de domínio representando a resposta da consulta de protocolo |
| `ConsultaProtocoloRetornoRowMapper.java` | Mapper responsável por converter ResultSet em objetos `ProtocoloResponse` |
| `ProtocoloMapper.java` | Interface MapStruct para conversão entre objetos de domínio e representação |
| `JdbiConfiguration.java` | Configuração do JDBI para acesso ao banco de dados |
| `ProtocoloUtil.java` | Classe utilitária com métodos de validação e conversão de dados |
| `StatusProtocolo.java` | Enum/Classe para mapeamento de códigos de status de protocolo |
| `SqlLoggerImpl.java` | Implementação de logger customizado para queries SQL |

---

## 3. Tecnologias Utilizadas

- **Java 11+**
- **Spring Boot 2.x** (framework principal)
- **Spring Security OAuth2** (autenticação JWT)
- **JDBI 3.19.0** (acesso a banco de dados)
- **Sybase jConnect 16.3-SP03-PL07** (driver JDBC)
- **MapStruct** (mapeamento de objetos)
- **Lombok** (redução de boilerplate)
- **Swagger/OpenAPI 3.0** (documentação de API)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Logback** (logging)
- **Spring Actuator** (monitoramento e health checks)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/protocolo` | `ProtocoloController` | Consulta protocolo ITP/PGFT por CNPJ, número de protocolo, NSU ou data de movimento |

**Parâmetros do endpoint:**
- `cnpjSolicitante` (header): CPF/CNPJ do solicitante
- `numeroProtocoloSolicitacao` (header): Protocolo do pagamento
- `numeroProtocoloSolicitacaoCliente` (header): NSU do pagamento
- `dataMovimento` (header): Data de movimento

---

## 5. Principais Regras de Negócio

1. **Validação de Parâmetros Obrigatórios**: É obrigatório informar pelo menos o número do protocolo OU o NSU do parceiro, além do CNPJ solicitante e data de movimento.

2. **Validação de Tipo de Movimento**: O sistema determina se a operação é de entrada (E), crédito (C) ou débito (D) comparando o CNPJ solicitante com os documentos do remetente e favorecido.

3. **Validação de Propriedade do Protocolo**: Verifica se o protocolo pertence ao CNPJ informado. Caso o tipo seja "Entrada", retorna erro "Protocolo invalido para o CNPJ informado! (ECX02)".

4. **Validação de Data de Movimento**: Compara a data de movimento informada na requisição com a data retornada pela procedure. Se não coincidirem, retorna erro "Protocolo não pertence a data de movimento informado (E01)".

5. **Mapeamento de Status**: Converte códigos numéricos de status (0-9) em descrições textuais legíveis (ex: 0 = "Disponível para o agente de validação", 3 = "Confirmado pela Tesouraria").

6. **Tratamento de Protocolos Não Encontrados**: Quando a procedure não retorna resultados, o sistema informa "Protocolo nao encontrado".

7. **Formatação de Datas**: Converte timestamps do banco para formato dd/MM/yyyy nas respostas.

---

## 6. Relação entre Entidades

**Entidade Principal: ProtocoloResponse**

A entidade `ProtocoloResponse` agrega informações de:
- **Dados do Protocolo**: código NSU, código do protocolo, status, protocolos relacionados (devolução/original), números de controle TED
- **Dados da Movimentação**: datas de aprovação/efetivação, valor, erro, entidade liquidante
- **Dados do Beneficiário**: nome, número da conta, documento
- **Dados do Remetente**: nome, número da conta, banco, agência, documento

**Relacionamentos:**
- Um protocolo pode ter um `protocoloDevolucao` (relacionamento 1:0..1)
- Um protocolo pode ter um `protocoloOriginal` (relacionamento 1:0..1)
- Um protocolo está associado a um remetente (relacionamento 1:1)
- Um protocolo está associado a um beneficiário (relacionamento 1:1)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| PrConsultarProtocoloV2 (procedure) | Stored Procedure | SELECT/READ | Procedure que retorna informações completas de um protocolo de pagamento baseado no código do protocolo ou NSU |

**Observação**: O sistema acessa o banco de dados Sybase (DBPGF_TES) exclusivamente através da stored procedure `PrConsultarProtocoloV2`, não realizando queries diretas em tabelas.

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

O sistema realiza apenas operações de leitura através da stored procedure. Não há evidências de operações de INSERT, UPDATE ou DELETE no código analisado.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot (startup) | Arquivo de configuração principal da aplicação |
| application-local.yml | leitura | Spring Boot (profile local) | Configurações específicas para ambiente local |
| logback-spring.xml | leitura | Logback (logging) | Configuração de logs da aplicação |
| openapi.yaml | leitura | Swagger/OpenAPI | Contrato da API REST (contract-first) |

**Observação**: O sistema não gera arquivos de saída. Os logs são direcionados para console (STDOUT) conforme configuração do Logback.

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
| Banco de Dados Sybase (DBPGF_TES) | Database | Banco de dados principal contendo informações de protocolos de pagamento. Acesso via JDBC com stored procedures |
| API Gateway (OAuth2/JWT) | Autenticação | Sistema de autenticação e autorização via JWT. URLs variam por ambiente (des/uat/prd) |

**Detalhes de Conexão por Ambiente:**
- **DES**: `sybdesspb.bvnet.bv:6500/DBPGF_TES`
- **UAT**: `sybuatspb.bvnet.bv:3400/DBPGF_TES`
- **PRD**: `mor-sybspb.bvnet.bv:5000/DBPGF_TES`

---

## 13. Avaliação da Qualidade do Código

**Nota: 7.5/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades em camadas (controller, service, repository, domain)
- Uso adequado de frameworks modernos (Spring Boot, JDBI, MapStruct)
- Implementação de segurança com OAuth2/JWT
- Documentação da API com OpenAPI/Swagger
- Uso de Lombok para reduzir boilerplate
- Logging estruturado e sanitização de mensagens
- Configuração adequada para múltiplos ambientes
- Testes unitários presentes (embora não analisados)

**Pontos de Melhoria:**
- Classe `ProtocoloUtil` com métodos estáticos e responsabilidades misturadas (validação, conversão de datas, etc.)
- Tratamento de exceções genérico no controller (catch Exception)
- Falta de constantes para mensagens de erro (strings hardcoded)
- Classe `StatusProtocolo` poderia ser um enum real ao invés de classe com array interno
- Método `getProcedure()` no service poderia ser injetado via construtor para melhor testabilidade
- Alguns comentários em português e outros em inglês (inconsistência)
- Validações poderiam usar Bean Validation (JSR-303) ao invés de validações manuais
- Falta de tratamento específico para diferentes tipos de SQLException

---

## 14. Observações Relevantes

1. **Arquitetura Atômica**: O projeto segue o padrão de microserviços atômicos do Banco Votorantim, com estrutura padronizada e uso do framework Atlante.

2. **Contract-First**: A API é definida primeiro através do arquivo OpenAPI YAML, e as interfaces são geradas automaticamente.

3. **Multi-Layer Docker**: O Dockerfile utiliza estratégia de múltiplas camadas para otimização de build e cache.

4. **Infraestrutura como Código**: O arquivo `infra.yml` centraliza todas as configurações de infraestrutura para diferentes ambientes (des/uat/prd).

5. **Segurança**: Todos os endpoints (exceto públicos) são protegidos por autenticação JWT via API Gateway.

6. **Monitoramento**: Exposição de métricas via Spring Actuator na porta 9090 (separada da porta da aplicação 8080).

7. **Charset Específico**: Conexão com Sybase utiliza charset ISO-1, importante para compatibilidade com dados legados.

8. **Versionamento da Procedure**: O nome da procedure inclui "V2", sugerindo que existe ou existiu uma versão anterior.

9. **Ambientes**: O sistema está preparado para rodar em 4 ambientes: local, des (desenvolvimento), uat (homologação) e prd (produção).

10. **Dependências Corporativas**: O projeto herda de um POM parent corporativo (`pom-atle-base-sboot-atom-parent`) que centraliza versões e configurações padrão.