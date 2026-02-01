# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema atômico responsável pelo processamento de mensagens de Advice (confirmação/estorno de transações) enviadas pela DXC para transações de cartão de débito. O sistema valida e processa diferentes tipos de advice (aprovação, estorno, desfazimento e desfazimento por sistema indisponível), atualizando as bases de dados de controle de transações e integrando com sistemas de efetivação via Google Cloud Pub/Sub.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `DebitoAdviceController` | Controller REST que expõe endpoints para validação, processamento e consulta de advice |
| `AdviceAprovadoServiceImpl` | Implementa lógica de validação e processamento de advice de aprovação |
| `AdviceEstornoServiceImpl` | Implementa lógica de validação e processamento de advice de estorno |
| `AdviceDesfazimentoServiceImpl` | Implementa lógica de validação e processamento de advice de desfazimento |
| `AdviceSistemaIndisponivelServiceImpl` | Implementa lógica de validação e processamento de advice de desfazimento por sistema indisponível |
| `AutorizacaoDebitoServiceImpl` | Gerencia consultas e atualizações de autorizações de débito sem advice |
| `CCBDRepositoryImpl` | Interface de acesso ao banco de dados SQL Server usando JDBI |
| `PubSubPublishImpl` | Publica mensagens de autorizações sem advice para fila do Google Cloud Pub/Sub |
| `TipoAdviceEnum` | Enum que define os tipos de advice e instancia os serviços apropriados |

## 3. Tecnologias Utilizadas

- **Framework**: Spring Boot 2.x
- **Linguagem**: Java 11
- **Persistência**: JDBI 3.19.0 com SQL Server (Microsoft SQL Server JDBC Driver 7.4.0)
- **Mensageria**: Google Cloud Pub/Sub (spring-cloud-gcp 2.0.11)
- **Documentação API**: Swagger/OpenAPI 3.0 (Springfox 3.0.0)
- **Segurança**: Spring Security OAuth2 com JWT
- **Monitoramento**: Spring Actuator + Prometheus + Micrometer
- **Logging**: Logback com formato JSON
- **Build**: Maven 3.3+
- **Containerização**: Docker

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/validar` | DebitoAdviceController | Valida advice enviado pela DXC |
| POST | `/v1/processar` | DebitoAdviceController | Processa advice validado |
| POST | `/v1/log` | DebitoAdviceController | Registra log de erro de advice |
| POST | `/v1/transacao-debito/confirmar-transacao` | DebitoAdviceController | Consulta e envia autorizações sem advice para efetivação |
| PUT | `/v1/processarEfetivacaoInvalida` | DebitoAdviceController | Zera protocolo ITP de efetivação inválida |
| PUT | `/v1/atualizarSequencialBloqueio` | DebitoAdviceController | Atualiza código sequencial de bloqueio |
| PUT | `/v1/update-check-list` | DebitoAdviceController | Atualiza checklist de recebimento de advice |
| GET | `/v1/consultar-authorization-code/{nsu}` | DebitoAdviceController | Consulta código de autorização por NSU |
| GET | `/v1/consultar-codigo-processamento/{nsu}` | DebitoAdviceController | Consulta código de processamento por NSU |

## 5. Principais Regras de Negócio

- **Validação de Advice**: Identifica o tipo de advice (aprovação, estorno, desfazimento) baseado em código de transação e status do autorizador
- **Processamento de Aprovação**: Atualiza transação original com dados do advice, valida moeda (nacional/internacional), calcula IOF quando aplicável
- **Confirmação Parcial**: Detecta e processa confirmações parciais (valor do advice menor que valor original) gerando estorno da diferença
- **Processamento de Estorno/Desfazimento**: Cria nova transação de estorno/desfazimento vinculada à transação original
- **Validação de Transação Processada**: Impede reprocessamento de transações já efetivadas
- **Tratamento de Voucher sem Autorizador**: Cria transação para vouchers Base2 que não passaram pelo autorizador
- **Integração com Processadoras**: Trata diferenças entre processadoras DXC, PSM e BNK (XBNK/XPSM)
- **Cálculo de ITPs**: Determina códigos ITP (transação, liquidação, evento, origem) baseados em tipo de transação, moeda e processadora
- **Gestão de Bloqueios**: Gerencia sequências de bloqueio de saldo e processamento
- **Checklist de Arquivos**: Atualiza controle de recebimento de arquivos (advice, TIF, bandeira)

## 6. Relação entre Entidades

**Entidades Principais:**

- **ControleTransacaoCartao**: Entidade central que armazena dados da transação (valores, datas, códigos, status)
- **TransacaoCartao**: Dados do cartão utilizado na transação (produto, correlativo, emissor, conta)
- **EstabelecimentoComercial**: Dados do estabelecimento onde ocorreu a transação
- **AutorizacaoCartao**: Código de autorização da transação (específico para BNK/PSM)
- **ErroTransacaoCartao**: Log de erros no processamento de advice
- **CheckListTransacaoArquivo**: Controle de recebimento de arquivos relacionados à transação

**Relacionamentos:**
- ControleTransacaoCartao (1) -> (1) TransacaoCartao
- ControleTransacaoCartao (1) -> (1) EstabelecimentoComercial
- ControleTransacaoCartao (1) -> (0..1) AutorizacaoCartao
- ControleTransacaoCartao (1) -> (0..N) ErroTransacaoCartao
- ControleTransacaoCartao (1) -> (0..1) CheckListTransacaoArquivo (via cdControleTransacaoCartaoAprovado)

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbControleTransacaoCartao | tabela | SELECT | Busca transações para validação de advice (por NSU ou identificador) |
| TbTipoTransacao | tabela | SELECT | Consulta tipo de transação (0200, 0400, etc) |
| TbRetornoTransacaoCartao | tabela | SELECT | Consulta código e descrição de retorno por status autorizador |
| TbAutorizacaoCartao | tabela | SELECT | Consulta código de autorização por NSU |
| TbEstabelecimentoComercial | tabela | SELECT | Dados do estabelecimento (via join com controle transação) |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbControleTransacaoCartao | tabela | INSERT | Insere nova transação de estorno/desfazimento ou voucher sem autorizador |
| TbControleTransacaoCartao | tabela | UPDATE | Atualiza transação original com dados do advice de aprovação |
| TbTransacaoCartao | tabela | INSERT | Insere dados do cartão para nova transação |
| TbTransacaoCartao | tabela | UPDATE | Atualiza máscara do cartão na transação original |
| TbEstabelecimentoComercial | tabela | INSERT | Insere dados do estabelecimento para nova transação |
| TbEstabelecimentoComercial | tabela | UPDATE | Atualiza dados do estabelecimento na transação original |
| TbAutorizacaoCartao | tabela | INSERT | Insere código de autorização (para BNK/PSM) |
| TbErroTransacaoCartao | tabela | INSERT | Registra erros no processamento de advice |
| TbCheckListTransacaoArquivo | tabela | UPDATE | Atualiza flags de recebimento de arquivos (advice, TIF, bandeira) |

## 9. Arquivos Lidos e Gravados

não se aplica

## 10. Filas Lidas

não se aplica

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Descrição |
|--------------|------------|-----------|
| `projects/bv-ccbd-des/topics/business-ccbd-base-motor-conciliacao-debito` | Google Cloud Pub/Sub | Publica autorizações de débito sem advice para processamento de efetivação |

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| DXC | API REST (consumidor) | Processadora que envia mensagens de advice |
| XPSM/XBNK | API REST (consumidor) | Processadoras alternativas que enviam advice |
| Google Cloud Pub/Sub | Mensageria | Publicação de autorizações sem advice para efetivação |
| SQL Server (DBCCBD) | Banco de Dados | Armazenamento de transações e controles |
| OAuth2/JWT | Segurança | Autenticação e autorização de requisições |

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com camadas bem definidas (presentation, domain, infrastructure)
- Uso adequado de padrões como Strategy (TipoAdviceEnum) e Builder
- Código bem documentado com logs informativos
- Uso de enums para constantes e mapeamentos de códigos
- Tratamento de exceções customizadas
- Testes unitários e de integração presentes

**Pontos de Melhoria:**
- Algumas classes de serviço muito extensas (AdviceAprovadoServiceImpl com ~300 linhas)
- Lógica de negócio complexa com muitos ifs aninhados em alguns métodos
- Uso de strings mágicas em alguns pontos (ex: "XPSM", "XBNK", "Base2")
- Alguns métodos privados muito longos que poderiam ser refatorados
- Comentários em português misturados com código em inglês
- Falta de documentação JavaDoc em algumas classes públicas
- Queries SQL embutidas em arquivos separados (bom), mas sem documentação do schema

## 14. Observações Relevantes

- O sistema utiliza JDBI ao invés de JPA/Hibernate, o que proporciona maior controle sobre as queries SQL mas requer mais código boilerplate
- Há tratamento específico para diferentes processadoras (DXC, BNK, PSM) com lógicas distintas de mapeamento de ITPs
- O sistema suporta transações nacionais e internacionais com cálculo de IOF para transações internacionais
- Implementa controle de idempotência verificando se transações já foram processadas
- Possui mecanismo de checklist para rastreamento de recebimento de múltiplos arquivos relacionados à mesma transação
- A configuração permite diferentes ambientes (local, des, qa, uat, prd) com externalização de propriedades
- Sistema preparado para observabilidade com Prometheus/Grafana e logs estruturados em JSON
- Utiliza OAuth2 com JWT para segurança, com endpoints públicos configuráveis