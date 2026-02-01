# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-ccbd-base-atom-deb-autorizador** é um serviço atômico desenvolvido em Spring Boot para autorização de transações de débito em cartões. O componente é responsável por validar, processar e registrar transações de débito, incluindo cálculo de IOF para transações internacionais, gerenciamento de dados de cartões (quina), estabelecimentos comerciais e controle transacional. O sistema integra-se com banco de dados SQL Server para persistência e oferece APIs REST para consumo por outros sistemas.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal Spring Boot que inicializa a aplicação |
| **AutorizacaoDebtController** | Controlador REST que expõe endpoints para validação e processamento de transações |
| **ValidarService / ValidarServiceImpl** | Serviço responsável por validar transações e calcular IOF |
| **ProcessarService / ProcessarServiceImpl** | Serviço responsável por processar e persistir transações no banco de dados |
| **CCBDRepository / CCBDRepositoryImpl** | Interface de acesso a dados utilizando JDBI para operações no banco |
| **TransacaoMapper** | Mapper para conversão entre objetos de domínio e representações REST |
| **ResourceExceptionHandler** | Tratador global de exceções da aplicação |
| **DataSourceConfiguration** | Configuração do datasource e JDBI |
| **DebAutorizadorConfiguration** | Configuração de beans do domínio |
| **OpenApiConfiguration** | Configuração do Swagger/OpenAPI |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.x** - Framework principal
- **Java 11** - Linguagem de programação
- **Maven** - Gerenciamento de dependências
- **JDBI 3.10.0** - Framework de acesso a dados SQL
- **SQL Server** - Banco de dados relacional (Microsoft SQL Server)
- **Swagger/OpenAPI 2.0** - Documentação de APIs
- **Springfox** - Geração automática de documentação Swagger
- **Spring Security OAuth2** - Segurança e autenticação JWT
- **Lombok** - Redução de boilerplate
- **JUnit 5 (Jupiter)** - Testes unitários
- **Mockito** - Mocks para testes
- **Logback** - Logging
- **Micrometer/Prometheus** - Métricas e monitoramento
- **Docker** - Containerização

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/autorizar-transacao/validar` | AutorizacaoDebtController | Valida uma transação e calcula IOF se aplicável |
| POST | `/v1/autorizar-transacao/processar` | AutorizacaoDebtController | Processa e persiste uma transação completa |
| POST | `/v1/autorizar-transacao/processarInsert` | AutorizacaoDebtController | Processa transação com insert específico |
| PUT | `/v1/autorizar-transacao/processarUpdate` | AutorizacaoDebtController | Atualiza dados de uma transação existente |
| POST | `/v1/autorizar-transacao/validar-processarInsert` | AutorizacaoDebtController | Valida e processa transação em uma única chamada |
| POST | `/v1/autorizar-transacao/processarInsertQuina` | AutorizacaoDebtController | Insere ou atualiza dados da quina (cartão) |

---

## 5. Principais Regras de Negócio

1. **Validação de Transação Duplicada**: Verifica se a transação já foi processada anteriormente através do identificador único
2. **Cálculo de IOF**: Para transações internacionais (moeda diferente de Real), calcula IOF com base em tabela progressiva por ano (2023: 5.38%, 2024: 4.38%, 2025+: 3.5%)
3. **Isenção de IOF**: Transações de crédito em conta (códigos de processamento iniciados com "20" ou "26") são isentas de IOF
4. **Conversão de Códigos de Banco**: Converte códigos de compensação bancária para códigos internos (BV: 655→161, BVSA: 413→436)
5. **Mapeamento de Status de Transação**: Converte códigos de status externos para códigos internos do cartão
6. **Processamento Transacional**: Garante atomicidade nas operações de insert/update através de transações
7. **Gerenciamento de Quina**: Verifica existência e decide entre insert ou update dos dados do cartão
8. **CheckList de Transações Aprovadas**: Registra transações aprovadas em tabela de controle

---

## 6. Relação entre Entidades

**Entidades principais:**

- **Transacao**: Entidade central contendo dados da transação (valores, datas, códigos, status)
  - Relaciona-se com **Cartao** (1:1 opcional)
  - Relaciona-se com **Estabelecimento** (1:1 opcional)
  
- **Cartao (Quina)**: Dados identificadores do cartão (emissor, filial, produto, conta, correlativo)

- **Estabelecimento**: Dados do estabelecimento comercial (código, nome, cidade, país)

- **ProcessarResponse**: Objeto de resposta contendo IDs gerados após processamento

**Relacionamento textual:**
```
Transacao (1) -----> (0..1) Cartao
Transacao (1) -----> (0..1) Estabelecimento
```

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| CCBDTransacaoCartaoDebito.TbControleTransacaoCartao | Tabela | SELECT | Verifica existência de transação processada |
| CCBDTransacaoCartaoDebito.TbTipoTransacao | Tabela | SELECT | Busca código de tipo de transação |
| DBCCBD.CCBDTransacaoCartaoDebito.TbTransacaoCartao | Tabela | SELECT | Conta registros de controle de transação (quina) |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| CCBDTransacaoCartaoDebito.TbControleTransacaoCartao | Tabela | INSERT | Insere nova transação de cartão |
| CCBDTransacaoCartaoDebito.TbControleTransacaoCartao | Tabela | UPDATE | Atualiza dados de transação existente |
| CCBDTransacaoCartaoDebito.TbTransacaoCartao | Tabela | INSERT | Insere dados do cartão (quina) |
| CCBDTransacaoCartaoDebito.TbTransacaoCartao | Tabela | UPDATE | Atualiza dados do cartão (quina) |
| CCBDTransacaoCartaoDebito.TbEstabelecimentoComercial | Tabela | INSERT | Insere dados do estabelecimento comercial |
| CCBDTransacaoCartaoDebito.TbCheckListTransacaoArquivo | Tabela | INSERT | Registra transações aprovadas para controle |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | Spring Boot | Configurações da aplicação (datasource, profiles, security) |
| logback-spring.xml | Leitura | Logback | Configuração de logs (console, formato JSON) |
| *.sql (resources) | Leitura | CCBDRepositoryImpl (JDBI) | Queries SQL para operações no banco |
| sboot-ccbd-base-atom-transacao-debito-autorizar.yaml | Leitura | Swagger Codegen | Especificação OpenAPI para geração de código |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|----------------|------|-----------|
| SQL Server (DBCCBD) | Banco de Dados | Banco de dados principal para persistência de transações |
| API Gateway BV | Serviço de Autenticação | Validação de tokens JWT via JWK endpoint |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades entre camadas (presentation, domain, infrastructure)
- Uso adequado de padrões como Repository, Service e Mapper
- Testes unitários e de integração presentes
- Uso de Lombok reduzindo boilerplate
- Configuração adequada de profiles para diferentes ambientes
- Documentação via Swagger
- Tratamento de exceções centralizado

**Pontos de Melhoria:**
- Alguns métodos com lógica complexa poderiam ser refatorados (ex: processarTransacaoInsert)
- Uso de valores mágicos em alguns pontos (strings hardcoded como "1", "S")
- Falta de validações mais robustas em alguns endpoints
- Comentários em português misturados com código em inglês
- Alguns logs poderiam ser mais informativos
- Falta de documentação JavaDoc em classes e métodos públicos
- Enum DadosIOF com lógica de negócio que poderia estar em serviço dedicado
- Alguns testes poderiam ter melhor cobertura de cenários de erro

---

## 14. Observações Relevantes

1. **Segurança**: O sistema utiliza OAuth2 com JWT para autenticação, integrando-se com API Gateway do Banco Votorantim

2. **Ambientes**: Configurado para múltiplos ambientes (local, des, qa, uat, prd) com diferentes datasources e URLs de autenticação

3. **Monitoramento**: Expõe métricas via Actuator e Prometheus na porta 9090

4. **Containerização**: Possui Dockerfile para deploy em containers, utilizando imagem base Java 11 customizada

5. **Pipeline CI/CD**: Configurado para Jenkins com propriedades específicas (jenkins.properties) e infraestrutura como código (infra.yml)

6. **Arquitetura Atômica**: Segue padrão de microserviços atômicos do Banco Votorantim, com divisão clara entre módulos domain e application

7. **Cálculo de IOF**: Implementa tabela progressiva de IOF com redução anual até 2025, mantendo taxa fixa de 3.5% após 2026

8. **Transações**: Utiliza controle transacional do Spring para garantir consistência nas operações de banco de dados

9. **Versionamento de API**: Utiliza versionamento via path (/v1/) nos endpoints REST

10. **Logging**: Configurado para output em formato JSON facilitando integração com ferramentas de análise de logs