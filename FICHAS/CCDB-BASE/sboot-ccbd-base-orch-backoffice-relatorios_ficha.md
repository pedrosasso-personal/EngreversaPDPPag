# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema orquestrador responsável pela geração de relatórios e cartas relacionadas ao encerramento de contas correntes do Banco Digital. O sistema atua como intermediário entre diversos microserviços, coordenando a geração de documentos em PDF (cartas de encerramento, históricos de conta, relatórios de contas ativas/inativas e sem movimentação), além de gerenciar créditos não reclamados e armazenar documentos no sistema corporativo de gestão eletrônica de documentos (IGED). Utiliza Apache Camel para orquestração assíncrona de processos e integra-se com múltiplos sistemas para enriquecimento de dados.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **RelatorioController** | Controlador REST que expõe endpoints para geração de relatórios e manipulação de documentos IGED |
| **BackofficeRelatoriosServiceImpl** | Serviço que orquestra a geração de cartas (encerramento, histórico, contas ativas/inativas, sem movimentação) via rotas Camel |
| **CreditoNaoReclamadoServiceImpl** | Serviço responsável pela geração de relatórios de créditos não reclamados através de rotas Camel |
| **DocumentoServiceImpl** | Serviço para salvar e consultar documentos no sistema IGED via rotas Camel |
| **BackofficeRelatoriosRepositoryImpl** | Repositório que consome o serviço atom-relatorios para geração de PDFs |
| **DocumentoRepositoryImpl** | Repositório para integração com API IGED (consulta e salvamento de documentos) |
| **ConsultaMovimentacaoRepositoryImpl** | Repositório para consulta de transações/movimentações |
| **ConsultaGlobalRepositoryImpl** | Repositório para consulta de dados do titular da conta |
| **ConsultaContaCorrenteRepositoryImpl** | Repositório para consulta de motivo de encerramento de conta |
| **BackofficeRelatoriosRouter** | Rotas Camel para orquestração de geração de relatórios (encerramento, histórico, ativas/inativas, sem movimentação) |
| **CreditoNaoReclamadoRouter** | Rota Camel que orquestra consulta de créditos não reclamados e enriquece dados com titular e motivo de encerramento |
| **DocumentoRouter** | Rotas Camel para salvar e consultar documentos no IGED |
| **CreditoNaoReclamadoIterator** | Iterator customizado para processar lista de créditos não reclamados em rotas Camel |
| **CreditoNaoReclamadoDTOProcessor** | Processador Camel que filtra movimentações por iniciativa de encerramento |
| **AppConfiguration** | Classe de configuração de beans da aplicação |
| **AppProperties** | Classe de propriedades externalizadas da aplicação |
| **ResourceExceptionHandler** | Tratador global de exceções REST |

---

## 3. Tecnologias Utilizadas

- **Framework Principal:** Spring Boot 2.x
- **Linguagem:** Java 11
- **Orquestração:** Apache Camel 3.0.1
- **Build:** Maven (multi-módulo)
- **Documentação API:** Swagger/OpenAPI 2.9.2
- **Segurança:** JWT (OAuth2), microservices-error 0.14.0
- **Monitoramento:** Spring Boot Actuator, Prometheus, Grafana
- **Testes:** JUnit 5, Mockito, Pact (testes de contrato), ArchUnit (validação arquitetural)
- **Serialização:** JAXB, Lombok
- **Containerização:** Docker, Kubernetes/OpenShift
- **Geração de Clients:** Swagger Codegen
- **Segurança Web Services:** WSS4J 2.2.2
- **Auditoria:** Audit 2.2.1
- **HTTP Client:** RestTemplate

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/relatorios/encerramento | RelatorioController | Gera carta de encerramento de conta |
| POST | /v1/relatorios/consulta/historicoconta | RelatorioController | Gera PDF com histórico de conta |
| POST | /v1/relatorios/consulta/contasativasinativas | RelatorioController | Gera PDF de contas ativas e inativas |
| POST | /v1/relatorios/consulta/contassemmovsaldo | RelatorioController | Gera PDF de contas sem movimentação ou saldo |
| GET | /v1/relatorios/consulta/credito/nao-reclamados | RelatorioController | Retorna relatório de créditos não reclamados |
| POST | /v1/relatorios/iged | RelatorioController | Salva documento no sistema IGED |
| GET | /v1/relatorios/iged | RelatorioController | Consulta documento no sistema IGED |

---

## 5. Principais Regras de Negócio

1. **Geração de Cartas de Encerramento:** Sistema gera cartas de encerramento de conta considerando diferentes etapas (DEMANDA, EFETIVACAO) e iniciativas (BANCO, CLIENTE, EMERGENCIAL)

2. **Orquestração Assíncrona:** Utiliza Apache Camel para processamento assíncrono de rotas de geração de relatórios

3. **Enriquecimento de Dados:** Para créditos não reclamados, realiza consultas paralelas para enriquecer dados com informações do titular e motivo de encerramento

4. **Armazenamento Corporativo:** Todos os documentos gerados são armazenados no IGED (Gestão Eletrônica de Documentos) na pasta /carta-encerramento/ com objectStore OS_BVBD

5. **Filtragem de Movimentações:** Aplica filtros por iniciativa de encerramento nas movimentações de crédito não reclamado

6. **Encoding Padronizado:** Aplica encoding UTF-8 em todas as respostas

7. **Relatórios Múltiplos:** Gera diferentes tipos de relatórios: histórico de saldo, contas ativas/inativas, contas sem movimentação

8. **Parametrização IGED:** Utiliza propriedades customizadas para filtrar e organizar documentos no IGED (cpfCnpj, banco, agência, conta, tipoConta)

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **CartaEncerramentoDTO:** Representa dados da carta de encerramento (banco, conta, tipo, agência, titular, dtEncerramento, endereço, iniciativa, etapa, motivo)

- **CreditoNaoReclamadoDTO:** Representa crédito não reclamado (dtCredito, vrTransferencia, banco, agência, conta, iniciativa, nome, cpfCnpj, tipoConta, nomeTransacao)

- **NovoDocumentoVO:** Value Object para salvar documento IGED (cpfCnpj, banco, conta, tipoConta, arraybytes, agência, nomeDocumento)

- **PesquisaDocumentoVO:** Value Object para pesquisa de documento IGED (banco, tipoconta, conta, cpfcnpj)

- **DetalheDocumentoDTO:** Representa detalhe de documento (id, arraybytes base64)

- **ContasAtivasInativasDTO:** Lista de contas ativas/inativas com históricos

- **ContasSemMovSaldoDTO:** Contas sem movimentação/saldo com históricos

**Relacionamentos:**
- CartaEncerramentoDTO → utiliza enums (EtapaEncerramentoEnum, IniciativaEncerramentoEnum, MotivoEncerramentoEnum)
- CreditoNaoReclamadoDTO → enriquecido com dados de titular (ConsultaGlobalRepository) e motivo encerramento (ConsultaContaCorrenteRepository)
- NovoDocumentoVO/PesquisaDocumentoVO → mapeados para/de DetalheDocumentoDTO via DocumentoMapper

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

**Observação:** O sistema não acessa banco de dados diretamente. Todas as consultas são realizadas através de APIs REST de outros microserviços.

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

**Observação:** O sistema não realiza operações diretas em banco de dados. Persistência de documentos é feita via API IGED.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| PDFs (base64) | Leitura/Gravação | BackofficeRelatoriosRepositoryImpl, DocumentoRepositoryImpl | Documentos PDF gerados (cartas de encerramento, relatórios) em formato base64 |
| Documentos IGED | Gravação | DocumentoServiceImpl, DocumentoRouter | Armazenamento de documentos no sistema corporativo IGED (pasta /carta-encerramento/) |
| Documentos IGED | Leitura | DocumentoServiceImpl, DocumentoRouter | Consulta de documentos previamente armazenados no IGED |
| application.yml | Leitura | AppProperties | Arquivo de configuração da aplicação por ambiente (local, des, qa, uat, prd) |
| infra.yml | Leitura | Kubernetes/OpenShift | Configurações de infraestrutura (configmaps, secrets, probes, volumes) |

---

## 10. Filas Lidas

não se aplica

**Observação:** O sistema não consome mensagens de filas JMS, Kafka ou RabbitMQ. Utiliza Apache Camel com DirectEndpoint para processamento assíncrono interno.

---

## 11. Filas Geradas

não se aplica

**Observação:** O sistema não publica mensagens em filas externas. O processamento assíncrono é gerenciado internamente pelo Apache Camel.

---

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| **sboot-ccbd-base-atom-relatorios** | API REST | Serviço responsável pela geração física dos PDFs de relatórios e cartas |
| **sboot-iged-base-documentos** | API REST | Sistema corporativo de Gestão Eletrônica de Documentos (IGED) para armazenamento e consulta de documentos. Autenticação via username/password |
| **sboot-ccbd-base-atom-movimentacoes** | API REST | Serviço de consulta de movimentações e transações de contas correntes |
| **sboot-glob-base-atom-cliente-dados-cadastrais** | API REST | Serviço global de consulta de dados cadastrais de clientes/titulares |
| **sboot-ccbd-base-atom-conta-corrente** | API REST | Serviço de consulta de detalhes de conta corrente, incluindo motivo de encerramento |
| **OpenID Connect (JWT)** | Autenticação | Serviço de autenticação JWT OAuth2 (URL jwks.json configurada por ambiente) |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 8.5/10

**Justificativa:**

**Pontos Positivos:**
- Excelente separação de responsabilidades com arquitetura em camadas (domain, application, common)
- Uso adequado de padrões de projeto (Builder, DTO, VO, Repository, Service)
- Cobertura de testes abrangente (unitários, integração, funcionais) com JUnit 5, Mockito e Pact
- Validação arquitetural automatizada com ArchUnit
- Configuração externalizada por ambiente (local, des, qa, uat, prd)
- Uso de Lombok para redução de boilerplate
- Documentação de API com Swagger/OpenAPI
- Logs estruturados em JSON
- Monitoramento com Actuator e Prometheus
- Uso de enums para valores constantes (códigos de erro, etapas, iniciativas, motivos)
- Orquestração bem estruturada com Apache Camel
- Tratamento centralizado de exceções

**Pontos de Melhoria:**
- Ausência de documentação técnica inline (JavaDoc) em algumas classes
- Poderia ter mais comentários explicativos em lógicas de negócio complexas
- Alguns nomes de classes poderiam ser mais descritivos (ex: "Impl" genérico)
- Falta de informações sobre estratégias de retry e circuit breaker nas integrações externas
- Ausência de cache para otimização de consultas repetitivas

---

## 14. Observações Relevantes

1. **Processamento Assíncrono:** O sistema utiliza Apache Camel com DirectEndpoint para processamento assíncrono interno, não dependendo de filas externas

2. **Multi-Módulo Maven:** Projeto organizado em módulos (common, domain, application) facilitando manutenção e reuso

3. **Geração Automática de Clients:** Utiliza Swagger Codegen para gerar automaticamente clients REST dos serviços integrados

4. **Segurança Multi-Camada:** Implementa autenticação JWT OAuth2 e WSS4J para segurança de web services

5. **Ambientes Múltiplos:** Configurações específicas para 5 ambientes (local, des, qa, uat, prd) com URLs e credenciais distintas

6. **Enriquecimento Paralelo:** O CreditoNaoReclamadoIterator permite processamento paralelo para enriquecimento de dados de créditos não reclamados

7. **Formato de Data Padronizado:** Utiliza DateUtils para gerar datas no formato yyyyMMdd

8. **Encoding UTF-8:** Todas as respostas utilizam encoding UTF-8 para suporte a caracteres especiais

9. **ObjectStore IGED:** Documentos armazenados no objectStore OS_BVBD do IGED

10. **Perfis Maven:** Suporta diferentes perfis de execução (unit, integration, functional, architecture) para testes específicos

11. **Auditoria:** Implementa auditoria através da biblioteca audit 2.2.1

12. **Containerização:** Preparado para deploy em ambientes Docker/Kubernetes/OpenShift com configurações de probes, volumes e secrets