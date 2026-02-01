# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-gdcc-base-atom-debito-automatico** é um microserviço atômico responsável por gerenciar contratos de financiamento em débito automático. Atualmente, suporta especificamente o produto de financiamento de veículos (código 12) para o Banco Digital. O sistema permite ativar e cancelar débito automático de contratos, consumindo eventos via RabbitMQ e expondo APIs REST para consulta e gestão. Utiliza banco de dados Sybase para persistência e mantém logs de auditoria das operações realizadas.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `DebitoAutomaticoController` | Controlador REST que expõe endpoints para consulta e adição de débito automático |
| `DebitoAutomaticoService` | Serviço de negócio que implementa a lógica de ativação e cancelamento de débito automático |
| `DebitoAutomaticoServiceTransactional` | Camada transacional que envolve as operações do serviço com controle de transação |
| `DebitoAutomaticoListener` | Listener que consome mensagens da fila RabbitMQ para processar eventos de débito automático |
| `DebitoAutomaticoRepositoryImpl` | Implementação do repositório que realiza operações de banco de dados via JDBI |
| `ContratoRowMapper` | Mapper responsável por converter ResultSet em objetos Contrato |
| `ContratoDebitoAutomaticoRowMapper` | Mapper responsável por converter ResultSet em objetos DebitoAutomatico |
| `DebitoAutomaticoMapper` | Mapper de conversão entre objetos de domínio e representações REST |
| `DebitoAutomaticoConfiguration` | Configuração principal do Spring Boot, incluindo beans JDBI e RabbitMQ |
| `RabbitMQConfiguration` | Configuração específica do RabbitMQ com políticas de retry |
| `OpenApiConfiguration` | Configuração do Swagger/OpenAPI para documentação da API |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.x** - Framework principal para construção do microserviço
- **Java 11** - Linguagem de programação
- **JDBI 3.12.0** - Framework de acesso a dados SQL
- **Sybase jConnect 16.3** - Driver JDBC para banco de dados Sybase
- **RabbitMQ** - Sistema de mensageria para consumo de eventos
- **Spring AMQP** - Integração Spring com RabbitMQ
- **Swagger/Springfox 3.0.0** - Documentação de APIs REST
- **Lombok** - Redução de código boilerplate
- **Micrometer + Prometheus** - Métricas e monitoramento
- **Spring Actuator** - Endpoints de health check e métricas
- **Maven** - Gerenciamento de dependências e build
- **Docker** - Containerização da aplicação
- **Logback** - Framework de logging com suporte a JSON

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/varejo/financiamento/debito-automatico/{numeroContrato}/{sequenciaContrato}` | `DebitoAutomaticoController` | Consulta contrato em débito automático por número e sequência |
| POST | `/v1/varejo/debito-automatico/adiciona-debito-automatico` | `DebitoAutomaticoController` | Adiciona ou cancela débito automático de um contrato |

---

## 5. Principais Regras de Negócio

1. **Ativação de Débito Automático:**
   - Verifica se é a primeira adesão ao débito automático do contrato
   - Se for primeira adesão, insere novo registro na tabela TbContratoDebito
   - Se já existir, atualiza o registro existente com novos dados bancários
   - Determina automaticamente o tipo de pessoa (F ou J) baseado no tamanho do CPF/CNPJ
   - Valida e atualiza a sequência do contrato financeiro se necessário
   - Registra log de ativação na tabela TbLogContratoDebito

2. **Cancelamento de Débito Automático:**
   - Valida se o contrato existe antes de cancelar
   - Atualiza o registro definindo motivo de suspensão como 5 e flag de débito ativo como 'N'
   - Registra log de cancelamento na tabela TbLogContratoDebito

3. **Validação de Sequência Financeira:**
   - Compara a sequência do contrato de débito com a sequência do contrato financeiro
   - Se houver divergência, utiliza a sequência mais recente do contrato financeiro

4. **Geração de Sequencial:**
   - Incrementa e obtém sequencial da tabela TbSequencial para uso nos logs

5. **Processamento de Eventos:**
   - Consome eventos da fila "events.debitoAutomatico"
   - Processa ativação ou cancelamento baseado no campo "ativarDebitoAutomatico"
   - Implementa retry automático com backoff exponencial em caso de falha

---

## 6. Relação entre Entidades

**Entidades principais:**

- **DebitoAutomatico**: Representa um contrato em débito automático
  - Atributos: numeroContrato, sequenciaContrato, codigoPessoa, numeroCpfCnpj, codigoBanco, numeroAgencia, numeroConta, ativarDebitoAutomatico, tipoPessoa, dataAtivacaoDebitoAutomatico

- **Contrato**: Representa um contrato financeiro
  - Atributos: codigoMotivoSuspensao, numeroContrato, sequenciaContrato, debitoAutomaticoAtivo, codigoRegistroAutorizacaoDebito
  - Relacionamento: possui um Cliente (1:1) e uma Conta (1:1)

- **Cliente**: Representa o cliente do contrato
  - Atributos: codigoPessoa, numeroCpfCnpj, tipoPessoa

- **Conta**: Representa a conta bancária para débito
  - Atributos: codigoBanco, numeroAgencia, numeroConta

**Relacionamentos:**
- Contrato → Cliente (1:1)
- Contrato → Conta (1:1)
- DebitoAutomatico é uma visão específica de Contrato com dados bancários

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBGESTAO..TbContratoDebito | Tabela | SELECT | Consulta contratos em débito automático com dados bancários e status |
| DBGESTAO..TbSequencial | Tabela | SELECT | Obtém sequencial disponível para geração de logs |
| DBGESTAOCCDCG..TbContratoFinanceiro | Tabela | SELECT | Consulta sequência ativa do contrato financeiro |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBGESTAO..TbContratoDebito | Tabela | INSERT | Insere novo contrato em débito automático (primeira adesão) |
| DBGESTAO..TbContratoDebito | Tabela | UPDATE | Atualiza dados bancários e status do débito automático (ativação) |
| DBGESTAO..TbContratoDebito | Tabela | UPDATE | Cancela débito automático definindo motivo suspensão e flag inativo |
| DBGESTAO..TbLogContratoDebito | Tabela | INSERT | Registra log de ativação de débito automático |
| DBGESTAO..TbLogContratoDebito | Tabela | INSERT | Registra log de cancelamento de débito automático |
| DBGESTAO..TbSequencial | Tabela | UPDATE | Incrementa sequencial disponível para geração de logs |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | Spring Boot | Arquivo de configuração da aplicação com profiles (local, des, qa, uat, prd) |
| logback-spring.xml | Leitura | Logback | Configuração de logging com saída em JSON e console |
| sboot-gdcc-base-atom-debito-automatico.yml | Leitura | Swagger Codegen | Especificação OpenAPI para geração de interfaces REST |
| *.sql | Leitura | DebitoAutomaticoRepositoryImpl | Arquivos SQL para operações de banco de dados via JDBI |

---

## 10. Filas Lidas

- **events.debitoAutomatico** (RabbitMQ)
  - Exchange: ex.gdcc.debito.automatico
  - Routing Key: debito.automatico
  - Consumidor: `DebitoAutomaticoListener`
  - Formato: JSON com dados de DebitoAutomatico
  - Configuração de retry: 3 tentativas com backoff exponencial (100ms inicial, 1000ms máximo)

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Banco de Dados Sybase (DBGESTAO) | Database | Banco principal para operações de débito automático |
| Banco de Dados Sybase (DBGESTAOCCDCG) | Database | Banco para consulta de contratos financeiros |
| RabbitMQ | Mensageria | Sistema de filas para consumo de eventos de débito automático |
| Prometheus | Monitoramento | Exportação de métricas via Micrometer |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (presentation, service, infrastructure, domain)
- Uso adequado de padrões como Repository, Mapper e DTO
- Implementação de controle transacional separado da lógica de negócio
- Configuração adequada de retry para mensageria
- Uso de JDBI com SQL externalizado, facilitando manutenção
- Documentação OpenAPI bem estruturada
- Logs adequados para rastreabilidade

**Pontos de Melhoria:**
- Falta tratamento de exceções mais específico nos controllers (retorna apenas 500)
- Ausência de validações de entrada nos endpoints REST
- Método `obterTipoPessoa` usa lógica simplista (apenas tamanho do CPF/CNPJ)
- Falta de testes unitários enviados para análise
- Alguns métodos do service poderiam ser quebrados em métodos menores
- Ausência de cache para consultas frequentes
- Falta de documentação inline em métodos mais complexos
- Configuração de segurança básica (apenas basic auth mencionado)

---

## 14. Observações Relevantes

1. **Limitação de Produto:** O sistema atualmente suporta apenas financiamento de veículos (produto 12) para o Banco Digital, conforme documentado no README.

2. **Arquitetura Hexagonal:** O projeto segue uma arquitetura hexagonal com separação clara entre domain, application e infrastructure, utilizando ports e adapters.

3. **Multi-módulo Maven:** Projeto organizado em módulos (common, domain, application) para melhor separação de responsabilidades.

4. **Profiles de Ambiente:** Configuração bem estruturada com profiles para diferentes ambientes (local, des, qa, uat, prd).

5. **Auditoria:** Sistema integrado com biblioteca de auditoria do Banco Votorantim (springboot-arqt-base-trilha-auditoria-web).

6. **Segurança:** Utiliza bibliotecas de segurança customizadas do banco (sboot-arqt-base-security-*).

7. **Monitoramento:** Exposição de métricas via Prometheus e health checks via Actuator na porta 9090.

8. **Containerização:** Dockerfile configurado para deploy em ambiente GCP (Google Cloud Platform).

9. **Geração de Código:** Utiliza Swagger Codegen para gerar interfaces de API a partir da especificação OpenAPI.

10. **Logging Estruturado:** Configuração de logs em formato JSON para facilitar análise e integração com ferramentas de observabilidade.