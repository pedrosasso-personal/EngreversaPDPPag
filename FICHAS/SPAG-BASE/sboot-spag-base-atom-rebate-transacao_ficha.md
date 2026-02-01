# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-spag-base-atom-rebate-transacao** é um serviço atômico desenvolvido em Spring Boot responsável por gerenciar as transações executadas pelos parceiros do sistema de pagamento de rebate. O sistema processa transações detalhadas recebidas via filas JMS, gera consolidações periódicas dessas transações e disponibiliza APIs REST para consulta de extratos e consolidados. Utiliza arquitetura hexagonal (ports and adapters) com separação clara entre camadas de domínio, aplicação e infraestrutura.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal que inicializa a aplicação Spring Boot |
| **ConsolidadoTransacaoService** | Serviço de domínio que gerencia a lógica de negócio para consolidação de transações |
| **DetalheTransacaoService** | Serviço de domínio que gerencia a lógica de negócio para detalhamento de transações |
| **ConsolidadoTransacaoController** | Controlador REST que expõe endpoints para consulta de consolidados |
| **DetalheTransacaoController** | Controlador REST que expõe endpoints para consulta de transações detalhadas |
| **ConsolidadoListener** | Listener JMS que consome mensagens para geração de consolidados |
| **DetalhadoListener** | Listener JMS que consome mensagens de transações detalhadas |
| **JdbiConsolidadoTransacaoRepository** | Repositório JDBI para operações de banco de dados relacionadas a consolidados |
| **JdbiDetalheTransacaoRepository** | Repositório JDBI para operações de banco de dados relacionadas a detalhes |
| **RetornoConsolidadoRepositoryImpl** | Implementação para publicação de mensagens de retorno de consolidados |
| **RetornoDetalheRepositoryImpl** | Implementação para publicação de mensagens de retorno de detalhes |
| **TransacaoErrorHandler** | Tratador de erros para processamento de mensagens JMS |
| **JdbiConfiguration** | Configuração do JDBI e registro de repositórios |
| **JmsConfiguration** | Configuração do JMS e listeners de filas |

---

## 3. Tecnologias Utilizadas

- **Spring Boot** (framework principal)
- **Spring Web** (APIs REST)
- **Spring JMS** (mensageria)
- **JDBI 3.9.1** (acesso a dados)
- **Microsoft SQL Server** (banco de dados)
- **IBM MQ** (filas de mensagens)
- **Swagger/OpenAPI 2.9.2** (documentação de APIs)
- **Spring Actuator** (monitoramento e métricas)
- **Micrometer/Prometheus** (métricas)
- **Logback** (logging)
- **JUnit 5** (testes unitários)
- **Mockito** (mocks para testes)
- **RestAssured** (testes funcionais)
- **Docker** (containerização)
- **Maven** (gerenciamento de dependências)
- **Java 11** (linguagem)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | /consolidados | ConsolidadoTransacaoController | Consulta consolidados de transações por período, produto, cliente e apuração bancária |
| GET | /transacoes | DetalheTransacaoController | Consulta extrato paginado de transações detalhadas por cliente, período e apuração bancária |

---

## 5. Principais Regras de Negócio

1. **Processamento de Transações Detalhadas**: Recebe transações via fila JMS, valida e persiste no banco de dados com flag ativo ('S')
2. **Geração de Consolidados**: Processa consolidação de transações agrupando por sigla de produto, CPF/CNPJ do cliente, banco e data de movimento
3. **Apuração Bancária**: Diferencia transações por tipo de banco (mesmo banco código 655, outros bancos, ou ambos)
4. **Inativação de Consolidados**: Antes de gerar novos consolidados para uma data, inativa os registros existentes (flag 'N')
5. **Processamento por Período**: Permite gerar consolidados para um intervalo de datas, processando dia a dia
6. **Notificação de Retorno**: Publica mensagens de sucesso, falha ou parcial nas filas de retorno após processamento
7. **Consulta Paginada**: Implementa paginação para consultas de extratos de transações
8. **Auditoria**: Registra data de inclusão/alteração e login do usuário ('rebate-transacao') em todas as operações

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **DetalheTransacao**: Representa uma transação individual com informações detalhadas (valor, data, cliente, banco, código de liquidação, etc.)
- **ConsolidadoTransacao**: Representa a consolidação de múltiplas transações agrupadas por critérios específicos (totalizando valores e quantidades)
- **ExtratoTransacaoDto**: DTO para retorno de extratos paginados de transações
- **ConsolidadoParametros**: Parâmetros para geração de consolidados (datas inicial e final)
- **FiltroExtratoPaginado**: Filtro para consultas paginadas de extratos

**Relacionamentos:**
- ConsolidadoTransacao é gerado a partir do agrupamento de múltiplos DetalheTransacao
- Ambas entidades compartilham atributos comuns: siglaProduto, cpfCnpjCliente, dataMovimento, codigoBanco
- ExtratoTransacaoDto é derivado de DetalheTransacao para apresentação em consultas

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| spagRebateTransacao.TbTransacaoConsolidadoRebate | Tabela | SELECT | Consulta de transações consolidadas por período, produto, cliente e banco |
| spagRebateTransacao.TbTransacaoDetalheRebate | Tabela | SELECT | Consulta de transações detalhadas para geração de extratos paginados |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| spagRebateTransacao.TbTransacaoDetalheRebate | Tabela | INSERT | Inserção de novas transações detalhadas recebidas via fila |
| spagRebateTransacao.TbTransacaoConsolidadoRebate | Tabela | INSERT | Inserção de registros consolidados gerados a partir das transações detalhadas |
| spagRebateTransacao.TbTransacaoConsolidadoRebate | Tabela | UPDATE | Inativação (FlAtivo = 'N') de registros consolidados existentes antes de gerar novos para a mesma data |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | Spring Boot / Resources | Arquivo de configuração da aplicação com profiles (local, des, qa, uat, prd) |
| logback-spring.xml | Leitura | Logback / Resources | Configuração de logging da aplicação |
| *.sql | Leitura | JDBI / Resources | Arquivos SQL para queries executadas pelos repositórios JDBI |

---

## 10. Filas Lidas

- **QL.TRANSACAO_REBATE.INT** (ambiente des/qa/uat/prd): Fila de entrada para recebimento de transações detalhadas
- **QL.ENVIO_CONSOLIDADO_REBATE.INT** (ambiente des/qa/uat/prd): Fila de entrada para solicitação de geração de consolidados
- **DEV.QUEUE.1** (ambiente local): Fila de entrada para transações detalhadas em desenvolvimento
- **DEV.QUEUE.3** (ambiente local): Fila de entrada para consolidados em desenvolvimento

---

## 11. Filas Geradas

- **QL.RETORNO_TRANSACAO_REBATE.INT** (ambiente des/qa/uat/prd): Fila de saída para retorno do processamento de transações detalhadas
- **QL.RETORNO_CONSOLIDADO_REBATE.INT** (ambiente des/qa/uat/prd): Fila de saída para retorno do processamento de consolidados
- **DEV.QUEUE.2** (ambiente local): Fila de saída para retorno de detalhados em desenvolvimento
- **DEV.QUEUE.4** (ambiente local): Fila de saída para retorno de consolidados em desenvolvimento

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| IBM MQ | Mensageria | Integração via filas JMS para recebimento de transações e envio de retornos |
| SQL Server (DBSPAG2) | Banco de Dados | Persistência de transações detalhadas e consolidadas |
| API Gateway | Autenticação | Validação de tokens JWT via JWK (OAuth2) |
| Prometheus | Monitoramento | Exportação de métricas via Actuator |
| Grafana | Visualização | Dashboards de métricas (configuração local) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura hexagonal bem implementada com separação clara de responsabilidades (domain, application, infrastructure)
- Uso adequado de padrões como Repository, Service, Mapper e DTO
- Boa cobertura de testes unitários e de integração
- Configuração externalizada por profiles
- Uso de JDBI com SQL externalizado em arquivos, facilitando manutenção
- Tratamento de erros estruturado com exceções customizadas
- Documentação via Swagger/OpenAPI
- Uso de Lombok reduzindo boilerplate
- Logs estruturados e configuráveis

**Pontos de Melhoria:**
- Alguns métodos de serviço poderiam ser mais granulares (ex: `gerarConsolidado` com múltiplas responsabilidades)
- Falta de validação de entrada em alguns endpoints REST
- Alguns testes unitários poderiam ter melhor cobertura de cenários de exceção
- Comentários em código poderiam ser mais descritivos em algumas classes
- Alguns nomes de variáveis poderiam ser mais descritivos (ex: `map` em `ConsolidadoTransacaoService`)

---

## 14. Observações Relevantes

1. **Estrutura Modular**: O projeto está organizado em módulos Maven (common, domain, application) seguindo boas práticas de separação de camadas
2. **Multi-ambiente**: Suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas
3. **Soft Delete**: Utiliza flag `FlAtivo` para inativação lógica de registros ao invés de exclusão física
4. **Processamento Assíncrono**: Utiliza listeners JMS para processamento assíncrono de mensagens
5. **Auditoria**: Todas as operações registram usuário ('rebate-transacao') e timestamps
6. **Containerização**: Dockerfile configurado para deploy em containers
7. **CI/CD**: Configuração Jenkins e infraestrutura como código (infra.yml) para deploy em OpenShift
8. **Métricas**: Integração com Prometheus e Grafana para monitoramento
9. **Segurança**: Integração com OAuth2/JWT para autenticação (configurado mas não implementado nos controllers)
10. **Paginação**: Implementação customizada de paginação para consultas de grande volume