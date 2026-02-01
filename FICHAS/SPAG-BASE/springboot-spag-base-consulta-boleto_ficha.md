# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **springboot-spag-base-consulta-boleto** é um serviço REST desenvolvido em Spring Boot para consulta de boletos de pagamento junto à CIP (Câmara Interbancária de Pagamentos). O sistema atua como intermediário entre aplicações clientes e o SPB (Sistema de Pagamentos Brasileiro), enviando mensagens via filas IBM MQ e processando as respostas em formato XML, convertendo-as para JSON. Implementa funcionalidades de cache com Redis para otimizar consultas recorrentes e possui mecanismos de feature toggle para controle de rollout de funcionalidades.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Server.java** | Classe principal da aplicação Spring Boot, responsável pela inicialização do sistema |
| **BoletoController.java** | Controlador REST que expõe endpoints para consulta de boletos, envio/recebimento de mensagens e gerenciamento de cache |
| **BoletoService.java** | Serviço principal contendo a lógica de negócio para consulta de boletos, com e sem cache |
| **MessageService.java** | Serviço responsável pelo envio e recebimento de mensagens nas filas IBM MQ |
| **MessageQueueRepository.java** | Repositório que encapsula operações de comunicação com filas JMS/IBM MQ |
| **ParametroPagamentoFintechRepository.java** | Repositório para consulta de parâmetros de parceiros Fintech no banco de dados |
| **ConfigCatService.java** | Serviço de integração com ConfigCat para gerenciamento de feature toggles |
| **RolloutService.java** | Serviço que controla a habilitação de funcionalidades (cache) baseado em rollout progressivo |
| **RedisConfiguration.java** | Configuração do Redis para cache distribuído com tratamento de erros |
| **JmsConfiguration.java** | Configuração de filas JMS para comunicação com IBM MQ |
| **DocketConfiguration.java** | Configuração do Swagger para documentação da API |
| **Util.java** | Classe utilitária com métodos para transformação XML/JSON, validações e geração de IDs |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.7.18** - Framework principal
- **Spring Web** - Para construção de APIs REST
- **Spring Data Redis** - Integração com Redis para cache
- **Spring Cache** - Abstração de cache
- **IBM MQ (com.ibm.mq)** - Middleware de mensageria para comunicação com SPB
- **Spring JMS** - Para integração com filas de mensagens
- **SQL Server JDBC Driver** - Conexão com banco de dados SQL Server
- **HikariCP** - Pool de conexões de banco de dados
- **Swagger/Springfox 3.0.0** - Documentação de API
- **Logback** - Framework de logging
- **Lettuce** - Cliente Redis
- **ConfigCat** - Gerenciamento de feature flags
- **XSLT** - Transformação de mensagens XML para JSON
- **Lombok** - Redução de boilerplate
- **JUnit 4 e Mockito** - Testes unitários
- **Gradle 7.5.1** - Ferramenta de build
- **Docker** - Containerização

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/boleto/{codigoBarra}` | BoletoController | Consulta boleto na CIP pelo código de barras (44 dígitos) |
| GET | `/v1/boleto/enviaMensagem/{codigoBarra}` | BoletoController | Envia mensagem para o SPB sem aguardar resposta |
| GET | `/v1/boleto/recebeMensagem/{id}` | BoletoController | Recebe mensagem do SPB pelo ID de correlação |
| GET | `/v1/boleto/removerCacheBoleto/{codigoBarra}` | BoletoController | Remove cache de um boleto específico |
| GET | `/v1/boleto/removerTodosCacheBoleto` | BoletoController | Remove todos os caches de boletos |

**Headers importantes:**
- `apiKey` (opcional): Identificador do parceiro/aplicação para controle de rollout
- `Timeout` (opcional): Timeout customizado para a consulta
- `Accept`: Formato de resposta (padrão: application/json)

---

## 5. Principais Regras de Negócio

1. **Validação de Código de Barras**: O código de barras deve ter exatamente 44 caracteres numéricos
2. **Consulta com Cache Condicional**: A utilização de cache é controlada por feature toggles e pode ser habilitada por parceiro (CNPJ) ou por aplicação (apiKey)
3. **Rollout Progressivo**: O sistema permite ativar o cache de forma gradual, controlando quais parceiros ou aplicações terão acesso à funcionalidade
4. **Transformação de Mensagens**: Mensagens XML recebidas do SPB (formato DDA0110R1) são transformadas em JSON usando XSLT
5. **Geração de ID Único**: IDs de correlação são gerados usando timestamp em nanosegundos + sufixo do hostname
6. **Timeout Configurável**: Permite sobrescrever o timeout padrão de recebimento de mensagens via header HTTP
7. **Tratamento de Erros de Cache**: Falhas no Redis não impedem o funcionamento da aplicação, apenas desabilitam o cache temporariamente
8. **Validação de Mensagem CIP**: Apenas mensagens com tag `<CodMsg>DDA0110R1</CodMsg>` são consideradas válidas

---

## 6. Relação entre Entidades

O sistema não possui entidades de domínio complexas com relacionamentos ORM. As principais estruturas de dados são:

- **BoletoPagamento**: Estrutura JSON representando os dados do boleto (mapeada via XSLT do XML CIP)
  - Contém: numeroControleParticipante, numeroCodigoBarras, valorTitulo, dataVencimento, etc.
  - Relaciona-se com: PessoaBeneficiarioOriginal, PessoaPagador, SacadorAvalista
  
- **PessoaBeneficiarioOriginal/PessoaPagador**: Dados de pessoas envolvidas no boleto
  - Atributos: nome, tipoDocumento (CPF/CNPJ), numeroDocumento

- **ParametroPagamentoFintech**: Tabela de banco de dados
  - Relaciona apiKey com CNPJ do parceiro

Não há relacionamentos JPA/Hibernate tradicionais, pois o sistema trabalha principalmente com transformação de mensagens e consultas diretas via JDBC.

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbParametroPagamentoFintech | tabela | SELECT | Consulta CNPJ do parceiro Fintech através da apiKey para controle de rollout de funcionalidades |

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | leitura | Configuração Spring Boot | Arquivo de configuração de logs em formato JSON para diferentes ambientes |
| parametropagamentofintechrepository-sql.xml | leitura | ParametroPagamentoFintechRepository | Arquivo XML contendo queries SQL para consulta de parâmetros |
| DDA0110R1-JSON.txt | leitura | Util.java | Template XSLT para transformação de XML CIP em JSON |
| application.yml / application-local.yml | leitura | Spring Boot | Arquivos de configuração da aplicação por ambiente |

---

## 10. Filas Lidas

- **QL.SPAG.ROTEADOR_CIP.RSP** (ambiente produção: QM.CASH.01)
- **QL.SPG.ENTRADA** (ambiente local)

**Descrição**: Filas IBM MQ de onde o sistema consome as respostas das consultas de boleto enviadas ao SPB/CIP. As mensagens são filtradas por JMSCorrelationID.

---

## 11. Filas Geradas

- **QR.SPAG.CONSULTA_BOLETO_CIP** (ambiente produção: QM.CASH.01)
- **QR.SPB.SAIDA** (ambiente local)

**Descrição**: Filas IBM MQ para onde o sistema publica as requisições de consulta de boleto que serão processadas pelo SPB/CIP.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **CIP (Câmara Interbancária de Pagamentos)** | Mensageria (IBM MQ) | Sistema principal de consulta de boletos registrados, comunicação via filas JMS com mensagens XML no formato DDA0110R1 |
| **Redis** | Cache | Cache distribuído para armazenamento temporário de consultas de boletos e parâmetros de parceiros |
| **ConfigCat** | Feature Toggle | Serviço de gerenciamento de feature flags para controle de rollout de funcionalidades |
| **SQL Server (DBSPAG)** | Banco de Dados | Banco de dados contendo parâmetros de configuração de parceiros Fintech |
| **LDAP (bvnet.bv)** | Autenticação | Serviço de autenticação de usuários (habilitado em ambientes não-locais) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades em camadas (controller, service, repository)
- Uso adequado de anotações Spring e injeção de dependências
- Implementação de cache com tratamento de falhas (AppCacheErrorHandler)
- Testes unitários presentes com boa cobertura
- Uso de Lombok para reduzir boilerplate
- Configuração externalizada por ambiente
- Documentação Swagger configurada
- Tratamento de erros com logs apropriados

**Pontos de Melhoria:**
- Classe `Util.java` muito extensa e com múltiplas responsabilidades (violação do Single Responsibility Principle)
- Template XSLT hardcoded como String dentro do código Java (deveria estar em arquivo externo)
- Uso de comentários em código comentado em algumas classes
- Alguns métodos muito longos (ex: `getXsl()` com mais de 200 linhas)
- Falta de validação mais robusta de entrada em alguns endpoints
- Uso de `System.nanoTime()` para geração de IDs pode causar colisões em ambientes distribuídos
- Algumas mensagens de log com concatenação de strings ao invés de placeholders
- Falta de DTOs específicos, usando Strings para representação JSON

O código é funcional e bem estruturado em sua maior parte, mas poderia se beneficiar de refatorações para melhorar manutenibilidade e aderência a princípios SOLID.

---

## 14. Observações Relevantes

1. **Ambientes**: O sistema está configurado para múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas de filas, banco de dados e Redis para cada um.

2. **Segurança**: Utiliza autenticação básica (Basic Auth) via LDAP em ambientes não-locais. Em ambiente local, usa autenticação in-memory para facilitar desenvolvimento.

3. **Resiliência**: O sistema foi projetado para continuar funcionando mesmo com falhas no Redis (cache), degradando graciosamente para consultas diretas.

4. **Feature Toggles**: Implementa controle granular de funcionalidades através de ConfigCat, permitindo:
   - Ativação/desativação global do cache
   - Rollout por CNPJ de parceiro
   - Rollout por aplicação (apiKey)

5. **Timeout**: Configurado com timeout padrão de 21 segundos para envio e recebimento de mensagens, podendo ser sobrescrito via header HTTP.

6. **Formato de Mensagens**: O sistema trabalha com o padrão DDA0110R1 da CIP para consulta de boletos, realizando transformação XSLT para JSON.

7. **Containerização**: Preparado para execução em containers Docker com imagem baseada em OpenJ9 JDK 8.

8. **Infraestrutura como Código**: Possui configuração para deploy em Kubernetes (OpenShift) através do arquivo `infra.yml`.

9. **Monitoramento**: Configurado com logs estruturados em JSON e integração com SonarQube para análise de qualidade de código.

10. **Pool de Conexões**: Utiliza HikariCP com configuração de pool ajustável por ambiente (máximo de 40 conexões em produção).