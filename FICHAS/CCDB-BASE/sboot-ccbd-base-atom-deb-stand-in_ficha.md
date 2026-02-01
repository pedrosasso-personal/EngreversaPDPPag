# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-ccbd-base-atom-deb-stand-in** é um serviço atômico desenvolvido em Java com Spring Boot para autorização de transações de débito em modo Stand-In. O Stand-In é um mecanismo de contingência que permite autorizar transações quando o sistema principal de contas está indisponível ou fora do ar. O serviço recebe requisições de autorização de transações de débito, valida o saldo disponível, registra a transação em uma base de dados SQL Server, envia a transação para uma fila JMS (IBM MQ) e, opcionalmente, insere informações em um cache através de uma API externa. O sistema retorna códigos de aprovação ou reprovação conforme a disponibilidade de saldo e regras de negócio aplicadas.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal que inicializa a aplicação Spring Boot com segurança OAuth2 habilitada. |
| `DebtAuthorizationController` | Controlador REST que expõe o endpoint de autorização de transações de débito. Orquestra o fluxo de validação, persistência, envio para fila e cache. |
| `DebStandInService` | Serviço de domínio responsável pela lógica de negócio de autorização de transações Stand-In, incluindo validação de saldo, cálculo de IOF e persistência. |
| `CacheTransactionService` | Serviço responsável por inserir transações no cache através de chamada a API externa. |
| `CCBDRepositoryImpl` | Repositório que implementa operações de banco de dados (SQL Server) usando JDBI, incluindo consultas de saldo e inserção de transações. |
| `CacheTransactionRepositoryImpl` | Repositório que integra com API externa para inserção de cache de transações. |
| `DebtTransaction` | Entidade de domínio que representa uma transação de débito com todos os seus atributos. |
| `CacheTransaction` | Entidade de domínio que representa os dados de cache de uma transação. |
| `Transacao` | Entidade que representa a estrutura de transação enviada para a fila JMS. |
| `TransacaoMapper`, `CacheTransactionMapper`, `CacheTransacaoRequestMapper` | Mappers responsáveis por conversão entre objetos de domínio e representações de API. |

---

## 3. Tecnologias Utilizadas

- **Java 11** (OpenJ9)
- **Spring Boot** (framework principal)
- **Spring Security OAuth2** (autenticação e autorização)
- **JDBI 3.9.1** (acesso a banco de dados)
- **Microsoft SQL Server** (banco de dados)
- **IBM MQ** (mensageria JMS)
- **Swagger/OpenAPI 2.9.2** (documentação de API)
- **Springfox** (geração de documentação Swagger)
- **Lombok** (redução de boilerplate)
- **Jackson** (serialização JSON)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Logback** (logging)
- **Micrometer/Prometheus** (métricas)
- **JUnit 5 e Mockito** (testes unitários)
- **RestTemplate** (cliente HTTP)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/transacao-debito/autorizar-transacao` | `DebtAuthorizationController` | Autoriza uma transação de débito em modo Stand-In, validando saldo, registrando no banco e enviando para fila. |

---

## 5. Principais Regras de Negócio

1. **Validação de Transação Duplicada**: Verifica se a transação já foi processada anteriormente através do identificador único.

2. **Consulta de Saldo Stand-In**: Consulta o saldo disponível considerando o último saldo registrado no Stand-In ou o saldo total da conta, priorizando o mais recente.

3. **Cálculo de IOF**: Para transações internacionais (moeda diferente de Real), calcula IOF de 6,38% sobre o valor da transação.

4. **Validação de Saldo Suficiente**: Verifica se o saldo disponível é suficiente para cobrir o valor da transação (incluindo IOF quando aplicável).

5. **Aprovação/Reprovação de Transação**: 
   - Aprovada (código "00") se saldo suficiente
   - Reprovada (código "V4") se saldo insuficiente ou negativo

6. **Atualização de Saldo Stand-In**: Após aprovação, deduz o valor da transação (e IOF) do saldo disponível e registra na base Stand-In.

7. **Geração de NSU**: Gera um identificador único (UUID) para cada transação processada.

8. **Conversão de Código Bancário**: Converte código de compensação 655 para código interno 161 (Banco Votorantim).

9. **Formatação de Código de Processamento**: Converte código "000000" para "002000" quando necessário.

10. **Envio para Fila**: Todas as transações processadas (aprovadas ou não) são enviadas para fila JMS para processamento posterior.

11. **Cache Opcional**: Transações aprovadas têm seus dados inseridos em cache através de API externa (falhas não impedem o fluxo).

---

## 6. Relação entre Entidades

**DebtTransaction** (entidade principal):
- Contém informações completas da transação de débito
- Relaciona-se com dados de cartão, estabelecimento e conta
- Armazena resultado da autorização (código, mensagem, NSU)

**CacheTransaction**:
- Versão simplificada contendo apenas ID da transação e conta remetente
- Derivada de DebtTransaction para envio ao cache

**Transacao**:
- Estrutura completa para envio à fila JMS
- Contém objetos aninhados: Cartao e Estabelecimento
- Mapeada a partir de DebtTransaction

**Cartao**:
- Dados do cartão (emissor, filial, produto, conta, correlativo)

**Estabelecimento**:
- Dados do estabelecimento comercial (código, nome, cidade, país)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| CCBDAutorizacaoDebito.TbConta | tabela | SELECT | Consulta saldo total da conta corrente e data do último lançamento |
| CCBDAutorizacaoDebito.TbAutorizacaoStandIn | tabela | SELECT | Consulta saldo disponível Stand-In mais recente e verifica existência de transações anteriores |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| CCBDAutorizacaoDebito.TbAutorizacaoStandIn | tabela | INSERT | Insere registro de autorização Stand-In com saldo atualizado, dados da transação e timestamp |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot (startup) | Arquivo de configuração da aplicação com profiles (local, des, qa, uat, prd) |
| logback-spring.xml | leitura | Logback (startup) | Configuração de logging em formato JSON para stdout |
| checkBalance.sql | leitura | CCBDRepositoryImpl | Query SQL para consulta de saldo |
| checkTransactionAlreadyExists.sql | leitura | CCBDRepositoryImpl | Query SQL para verificar duplicidade de transação |
| getCdSequenceStandIn.sql | leitura | CCBDRepositoryImpl | Query SQL para obter código de sequência Stand-In |
| insertTransactionStandIn.sql | leitura | CCBDRepositoryImpl | Query SQL para inserir transação Stand-In |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Responsável | Breve Descrição |
|--------------|------------|-------------------|-----------------|
| QL.CCBD_PROC_TRANSAC_STAND_IN.INT | IBM MQ | DebtAuthorizationController | Fila para processamento de transações Stand-In (aprovadas e reprovadas) |

---

## 12. Integrações Externas

| Sistema/API | Tipo | Classe Responsável | Breve Descrição |
|-------------|------|-------------------|-----------------|
| API de Cache Stand-In | REST API | CacheTransactionRepositoryImpl | Integração com API externa para inserção de cache de transações aprovadas (endpoint: `/v1/banco-digital/contas/debito-cache/inserir`) |
| API Gateway OAuth | OAuth 2.0 | GatewayOAuthService | Autenticação OAuth2 para obtenção de token de acesso para APIs externas |
| SQL Server CCBD | Banco de Dados | CCBDRepositoryImpl | Banco de dados principal para consulta de saldos e persistência de transações Stand-In |
| IBM MQ | Mensageria JMS | JmsTemplate | Fila de mensagens para envio de transações processadas |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades entre camadas (presentation, domain, repository)
- Uso adequado de padrões como Repository, Service e Mapper
- Cobertura de testes unitários presente
- Uso de Lombok reduzindo boilerplate
- Configuração externalizada por profiles
- Tratamento de exceções customizadas
- Uso de JDBI com queries SQL externalizadas
- Documentação Swagger/OpenAPI presente

**Pontos de Melhoria:**
- Lógica de negócio complexa concentrada em métodos longos (DebStandInService)
- Falta de tratamento mais granular de exceções em alguns pontos
- Método `debtTransaction` no controller muito extenso e com muitas responsabilidades
- Uso de flags booleanas primitivas em vez de enums em alguns casos
- Falta de validações de entrada mais robustas
- Comentários de código ausentes em lógicas mais complexas
- Alguns métodos privados poderiam ser extraídos para melhor legibilidade
- Configuração de segurança básica (BasicAuth) poderia ser mais robusta
- Falta de logs estruturados em alguns fluxos críticos

---

## 14. Observações Relevantes

1. **Modo Stand-In**: O sistema opera como contingência quando o sistema principal está indisponível, mantendo controle próprio de saldos.

2. **Transações Internacionais**: O sistema identifica transações em moeda estrangeira e aplica cálculo de IOF automaticamente.

3. **Resiliência**: Falhas na inserção de cache não impedem o fluxo principal da transação, garantindo disponibilidade.

4. **Auditoria**: Todas as transações são registradas no banco com timestamp e enviadas para fila para processamento posterior.

5. **Segurança**: Utiliza OAuth2 com JWT para autenticação e autorização, com integração ao API Gateway.

6. **Observabilidade**: Integração com Prometheus/Grafana para métricas e health checks via Actuator.

7. **Multi-ambiente**: Configuração preparada para múltiplos ambientes (des, qa, uat, prd) com secrets gerenciados externamente.

8. **Containerização**: Aplicação preparada para execução em containers Docker com imagem otimizada (OpenJ9).

9. **Código Bancário**: Sistema específico do Banco Votorantim (código 161/655).

10. **Geração de Código**: Utiliza Swagger Codegen para gerar interfaces de API automaticamente a partir de especificações YAML.