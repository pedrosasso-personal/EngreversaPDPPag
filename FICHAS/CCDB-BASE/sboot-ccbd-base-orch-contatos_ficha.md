# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-ccbd-base-orch-contatos** é um microsserviço orquestrador desenvolvido em Java com Spring Boot para gerenciar contatos do Banco Digital (CCBD - Conta Corrente Banco Digital). O sistema permite operações de CRUD (criar, listar, consultar, alterar e remover) de contatos associados a contas bancárias, integrando-se com serviços atômicos (MySQL), Elasticsearch para buscas, RabbitMQ para mensageria assíncrona e APIs externas de instituições financeiras. Suporta tanto chaves PIX quanto dados bancários tradicionais (agência/conta).

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal que inicializa a aplicação Spring Boot com segurança OAuth2 e Feature Toggle |
| **ContatosController** | Controlador REST que expõe endpoints para listar, salvar, alterar e remover contatos |
| **ContatosService** | Serviço de domínio que orquestra as operações de contatos utilizando Apache Camel |
| **ContatosRouter** | Define as rotas Camel para processamento de contatos (listar, consultar, salvar, alterar, remover) |
| **ContatosListener** | Consumidor RabbitMQ que processa mensagens de carga de contatos |
| **SalvarContatoRepositoryImpl** | Implementação que envia contatos para fila RabbitMQ para persistência |
| **AlterarContatoRepositoryImpl** | Implementação que envia contatos alterados para fila RabbitMQ |
| **RemoverContatoRepositoryImpl** | Implementação que envia contatos para remoção via fila RabbitMQ |
| **ListarContatosPpbdRepositoryImpl** | Implementação que consulta contatos no serviço atômico MySQL (PPBD) |
| **ConsultarContatoPpbdRepositoryImpl** | Implementação que consulta um contato específico no MySQL |
| **InstituicaoRepositoryImpl** | Implementação que busca dados de instituições financeiras via API externa |
| **GerarTokenJwtBvRepositoryImpl** | Implementação que gera token JWT para autenticação em APIs internas |
| **ContatoConversor** | Utilitário para merge de dados de contatos (target + found) |
| **ContatoRepresentationMapper** | Mapeador entre objetos de domínio e representações REST |
| **ContatoMySQLtoElasticMapper** | Mapeador entre dados do MySQL e modelo legado/Elasticsearch |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (Web, Actuator, AMQP, Security OAuth2)
- **Apache Camel 3.22.4** (orquestração de rotas e integração)
- **RabbitMQ** (mensageria assíncrona)
- **Elasticsearch 7.10.0** (busca e indexação de contatos - referenciado mas não implementado diretamente neste módulo)
- **MySQL** (via serviço atômico sboot-ppbd-base-atom-contatos)
- **RestTemplate** (cliente HTTP para APIs externas)
- **Swagger/OpenAPI 3.0** (documentação de APIs)
- **Springfox 3.0.0** (geração de documentação Swagger)
- **Micrometer + Prometheus** (métricas e monitoramento)
- **Logback** (logging)
- **Lombok** (redução de boilerplate)
- **Apache Commons Lang3** (utilitários)
- **Feature Toggle (ConfigCat)** (controle de funcionalidades)
- **Maven** (gerenciamento de dependências e build)
- **Docker** (containerização)
- **Kubernetes/OpenShift** (deploy em GCP)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/banco-digital/contatos/pesquisas` | ContatosController | Lista contatos com paginação e filtros |
| POST | `/v1/banco-digital/contatos` | ContatosController | Salva um novo contato |
| PUT | `/v1/banco-digital/contatos` | ContatosController | Altera um contato existente |
| DELETE | `/v1/banco-digital/contatos` | ContatosController | Remove um contato |
| POST | `/v1/banco-digital/contatos/migrar` | ContatosController | Endpoint para migração de contatos (não implementado completamente) |

**Observação:** Todos os endpoints requerem autenticação OAuth2 via JWT.

---

## 5. Principais Regras de Negócio

1. **Geração de ID de Contato**: O ID do contato é gerado concatenando `documentoOrigem` + "-" + `documento` do contato.
2. **Merge de Contatos**: Ao salvar um contato existente, o sistema faz merge de chaves e contas, evitando duplicações.
3. **Validação de Instituição**: Se o contato possui dados bancários (agência/conta) sem informações completas da instituição, o sistema busca os dados via API de instituições.
4. **Alteração vs Remoção**: Se um contato alterado não possui mais contas nem chaves, a ação é convertida para remoção (action = "delete").
5. **Consulta Híbrida**: O sistema pode consultar contatos tanto no Elasticsearch quanto no MySQL (PPBD), unificando resultados e removendo duplicações.
6. **Feature Toggle**: A consulta ao MySQL é controlada por feature toggle (`ft_boolean_ccbd_base_contatos_salvos_pix_habilita_consulta_mysql`).
7. **Formatação de Dados**: ISPB é formatado com 8 dígitos (padding com zeros à esquerda), número de conta remove caracteres especiais.
8. **Tipo de Chave PIX**: O sistema identifica automaticamente o tipo de chave (CPF, CNPJ, EMAIL, PHONE, EVP) baseado no formato e código da chave.
9. **Token JWT Interno**: Para chamadas a APIs internas (atom-contatos, instituições), o sistema gera token JWT via OAuth2 client credentials.
10. **Auditoria**: Todas as operações são auditadas via trilha de auditoria (BV Audit).

---

## 6. Relação entre Entidades

**Entidades principais:**

- **Contato**: Representa um contato bancário
  - Atributos: id, documentoOrigem, documento, nome, apelido, email, telefone, dataInclusao, dataAlteracao
  - Relacionamentos: 
    - 1:N com **Chave** (chaves PIX associadas)
    - 1:N com **Conta** (contas bancárias associadas)

- **Chave**: Representa uma chave PIX
  - Atributos: codigo, tipo (CPF, CNPJ, EMAIL, PHONE, EVP)

- **Conta**: Representa uma conta bancária
  - Atributos: numero, tipo, agencia
  - Relacionamentos:
    - N:1 com **Instituicao**

- **Instituicao**: Representa uma instituição financeira
  - Atributos: codigoBanco, codigoBacen, identificadorIspb, nome, nomeAbrev

- **ListarContatos**: Objeto de pesquisa
  - Atributos: numeroCpfCnpj, pesquisa (PesquisaElasticsearch), resultados (List<Contato>), paginacao

- **PesquisaElasticsearch**: Parâmetros de busca
  - Atributos: tamanhoPaginacao, pagina, termoBusca, destacarResultados, ordem, filtros

**Relacionamentos:**
- Contato possui múltiplas Chaves (1:N)
- Contato possui múltiplas Contas (1:N)
- Conta pertence a uma Instituição (N:1)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| contatos (via API atom-contatos) | Tabela MySQL | SELECT/READ | Tabela de contatos no serviço atômico PPBD, consultada via API REST |
| instituicoes (via API glob-instituicoes) | Tabela/View | SELECT/READ | Dados de instituições financeiras (bancos), consultados via API REST |

**Observação:** O acesso ao banco de dados é indireto, via APIs REST dos serviços atômicos. Não há acesso direto a banco de dados neste componente.

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| contatos (índice Elasticsearch) | Índice Elasticsearch | INSERT/UPDATE/DELETE | Índice de contatos no Elasticsearch, atualizado via mensagens RabbitMQ (indiretamente) |

**Observação:** As operações de escrita são realizadas de forma assíncrona via fila RabbitMQ. O componente envia mensagens para a fila `ccbd_contatos`, e outro componente (consumer Logstash ou similar) processa essas mensagens e atualiza o Elasticsearch.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | Spring Boot (startup) | Arquivo de configuração da aplicação (profiles, variáveis de ambiente) |
| logback-spring.xml | Leitura | Logback (startup) | Configuração de logging (console, níveis de log) |
| swagger-server/sboot-ccbd-base-orch-contatos.yaml | Leitura | Swagger Codegen (build) | Especificação OpenAPI para geração de interfaces REST |
| swagger-consumer/sboot-glob-base-orch-instituicoes.yml | Leitura | Swagger Codegen (build) | Especificação OpenAPI para geração de cliente REST (instituições) |
| swagger-consumer/sboot-ppbd-base-atom-contatos.yaml | Leitura | Swagger Codegen (build) | Especificação OpenAPI para geração de cliente REST (atom-contatos) |

**Observação:** Não há gravação de arquivos em disco durante a execução normal da aplicação.

---

## 10. Filas Lidas

| Nome da Fila | Tecnologia | Classe Responsável | Descrição |
|--------------|------------|-------------------|-----------|
| ccbd_carga_contatos | RabbitMQ | ContatosListener | Fila para processamento de carga em lote de contatos (mensagens do tipo MensagemContato) |

---

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Responsável | Descrição |
|--------------|------------|-------------------|-----------|
| ccbd_contatos | RabbitMQ | SalvarContatoRepositoryImpl, AlterarContatoRepositoryImpl, RemoverContatoRepositoryImpl | Fila para envio de contatos a serem indexados/atualizados/removidos no Elasticsearch (via Logstash ou consumer dedicado) |

---

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| sboot-ppbd-base-atom-contatos | API REST (OpenAPI 3.0) | Serviço atômico de contatos (MySQL) - operações CRUD em base transacional |
| sboot-glob-base-orch-instituicoes | API REST (Swagger 2.0) | Serviço de consulta de instituições financeiras (bancos e participantes SPI) |
| OAuth2 Token Service | API REST | Serviço de geração de token JWT para autenticação em APIs internas (client credentials flow) |
| RabbitMQ | Mensageria | Broker de mensagens para comunicação assíncrona (filas ccbd_contatos e ccbd_carga_contatos) |
| Elasticsearch | NoSQL/Search Engine | Base de dados de busca e indexação de contatos (acesso indireto via mensageria) |
| ConfigCat (Feature Toggle) | SaaS | Serviço de gerenciamento de feature flags |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões de Clean Architecture (domain, application, infrastructure)
- Uso adequado de Apache Camel para orquestração de fluxos complexos
- Separação clara de responsabilidades (controllers, services, repositories, mappers)
- Uso de DTOs e mapeadores para isolamento de camadas
- Implementação de tratamento de exceções customizadas
- Configuração adequada de profiles (local, des, qa, uat, prd)
- Uso de Feature Toggle para controle de funcionalidades
- Documentação OpenAPI/Swagger bem estruturada
- Uso de Lombok para redução de boilerplate
- Testes unitários presentes (embora não enviados)

**Pontos de Melhoria:**
- Algumas classes com responsabilidades múltiplas (ex: ContatosRouter com muita lógica de negócio)
- Métodos longos e complexos em algumas classes (ex: `unificarListaContatosElasticComPpbdMysql`)
- Uso de `Optional.ofNullable()` em alguns lugares poderia ser simplificado
- Falta de validações de entrada em alguns pontos (ex: validação de CPF/CNPJ)
- Comentários de código escassos (principalmente em lógicas complexas)
- Alguns métodos estáticos em mappers poderiam ser instâncias para facilitar testes
- Tratamento de erros genérico em alguns pontos (catch Exception)
- Configuração de timeouts hardcoded (10 segundos) poderia ser parametrizável
- Falta de circuit breaker para chamadas externas (resiliência)

---

## 14. Observações Relevantes

1. **Arquitetura Híbrida**: O sistema trabalha com duas fontes de dados (Elasticsearch e MySQL via API), unificando resultados. Isso adiciona complexidade mas garante consistência durante migração/transição.

2. **Processamento Assíncrono**: Operações de escrita (salvar, alterar, remover) são assíncronas via RabbitMQ, garantindo desacoplamento e escalabilidade.

3. **Feature Toggle**: A consulta ao MySQL é controlada por feature flag, permitindo ativar/desativar funcionalidade sem deploy.

4. **Segurança**: Todos os endpoints são protegidos por OAuth2 JWT. O sistema também gera tokens internos para chamadas a APIs do BV.

5. **Auditoria**: Integração com framework de auditoria do BV (trilha de auditoria web e RabbitMQ).

6. **Monitoramento**: Exposição de métricas via Actuator/Prometheus para observabilidade.

7. **Multi-ambiente**: Configuração robusta para múltiplos ambientes (local, des, qa, uat, prd) com secrets gerenciados via cofre.

8. **Containerização**: Aplicação preparada para deploy em Kubernetes/OpenShift (GCP).

9. **Versionamento de API**: Uso de versionamento na URL (`/v1/`).

10. **Padrão de Nomenclatura**: Seguindo convenções do Banco Votorantim (sboot-ccbd-base-orch-*).

11. **Dependências Atualizadas**: Uso de versões relativamente recentes das bibliotecas (Spring Boot 2.x, Camel 3.x).

12. **Documentação**: README.md presente com instruções de build, execução e links para documentação corporativa.