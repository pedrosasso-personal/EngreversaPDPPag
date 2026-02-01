# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-ccbd-base-atom-extrato-composto** é um serviço stateful responsável pelo domínio de negócio de extrato composto de contas correntes do Banco Votorantim. O sistema consome eventos de transações via Google Pub/Sub, armazena e consolida informações de transações bancárias no Google Firestore, e expõe APIs REST para consulta paginada de extratos. O serviço integra dados de transações com detalhes adicionais (como informações de remetente, favorecido, boletos, etc.) e permite consultas por diferentes tipos de data (inclusão, comando ou efetivação).

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal de inicialização da aplicação Spring Boot com suporte a Firestore reativo |
| **ExtratoCompostoApiDelegateImpl** | Implementação do controller REST, responsável por receber requisições de consulta de extrato |
| **ExtratoCompostoService** | Serviço principal contendo lógica de negócio para salvar e consultar extratos compostos |
| **ListenerTransacoesContaCorrente** | Listener que consome mensagens do Pub/Sub e processa eventos de transações |
| **ExtratoCompostoRepository** | Interface de repositório reativo para operações no Firestore |
| **ConsultarExtratoRepositoryImpl** | Implementação customizada de consultas paginadas no Firestore |
| **PaginacaoAssembler** | Responsável por montar links de navegação (HATEOAS) para paginação |
| **ExtratoComposto** | Entidade de domínio principal representando um extrato composto |
| **GeradorHash** | Utilitário para geração de hash SHA-256 e codificação Base64 para paginação |
| **ExtratoCompostoHandler** | Handler global de exceções da aplicação |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.x** (framework principal)
- **Spring Data Firestore** (persistência reativa no Google Firestore)
- **Google Cloud Pub/Sub** (mensageria assíncrona)
- **Google Cloud Firestore** (banco de dados NoSQL)
- **Spring Security OAuth2** (autenticação e autorização JWT)
- **Spring HATEOAS** (suporte a links de navegação REST)
- **MapStruct** (mapeamento entre objetos)
- **Lombok** (redução de boilerplate)
- **OpenAPI Generator** (geração de código a partir de especificação OpenAPI)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Actuator** (monitoramento e health checks)
- **SLF4J/Logback** (logging)
- **AspectJ** (AOP para logging de tempo de execução)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | /v1/extrato | ExtratoCompostoApiDelegateImpl | Consulta paginada de transações de extrato composto por conta, período e tipo de data |

**Parâmetros principais:**
- Headers: codigoBanco, codigoTipoConta, numeroConta
- Query: tipoDataPesquisa (INCLUSAO/COMANDO/EFETIVACAO), dataInicial, dataFinal, tamanhoPagina, paginacaoReferencia (para navegação)

---

## 5. Principais Regras de Negócio

1. **Consolidação de Transações**: O sistema recebe eventos de transações e detalhes de transações separadamente via Pub/Sub e os consolida em um único documento no Firestore
2. **Validação de Ordem de Eventos**: Informações de detalhes não podem ser salvas antes das informações de transação principal
3. **Geração de ID Único**: Utiliza hash SHA-256 do identificador da transação como chave do documento
4. **Atualização Incremental**: Se o documento já existe, apenas atualiza campos não nulos, preservando informações anteriores
5. **Paginação Customizada**: Implementa paginação bidirecional (próxima/anterior) usando cursor baseado em sequencial de movimento
6. **Validação de Período**: Data inicial não pode ser posterior à data final
7. **Tipos de Pesquisa**: Suporta três tipos de data para filtro: data de inclusão, data de comando ou data de efetivação
8. **Limite de Página**: Busca sempre N+1 registros para determinar se há próxima página
9. **Codificação de Referência**: Parâmetros de paginação são codificados em Base64 para navegação segura

---

## 6. Relação entre Entidades

**ExtratoComposto** (entidade principal)
- Contém **Identificador** (cdBanco, nuContaCorrente, cdTipoConta, nuDocumento, nuSequencialUnicoLancamento, tpDebitoCredito)
- Contém **Transacao** (dados da movimentação: valores, datas, códigos, saldos)
- Contém **DetalhesTransacao** (informações complementares)
  - Possui **ContaPessoa** remetente
  - Possui **ContaPessoa** favorecido
  - Possui **DetalhesAdicionais**
    - Pode conter **DetalhesBoleto**
      - Contém **ValoresBoleto**
        - Contém **Encargos**
- Contém **Categoria** (categorização da transação)

**Relacionamentos:**
- ExtratoComposto 1:1 Identificador
- ExtratoComposto 1:0..1 Transacao
- ExtratoComposto 1:0..1 DetalhesTransacao
- ExtratoComposto 1:0..1 Categoria
- DetalhesTransacao 1:0..1 ContaPessoa (remetente)
- DetalhesTransacao 1:0..1 ContaPessoa (favorecido)
- DetalhesTransacao 1:0..1 DetalhesAdicionais
- DetalhesAdicionais 1:0..1 DetalhesBoleto
- DetalhesBoleto 1:0..1 ValoresBoleto
- ValoresBoleto 1:0..1 Encargos

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| extrato-composto | Coleção Firestore | SELECT/READ | Coleção principal contendo documentos de extratos compostos consolidados |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| extrato-composto | Coleção Firestore | INSERT/UPDATE | Inserção de novos extratos ou atualização incremental de extratos existentes |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | Leitura | Configuração de logging | Arquivo de configuração de logs por ambiente (des/uat/prd) |
| openapi.yaml | Leitura | OpenAPI Generator | Especificação da API REST utilizada para geração de código |
| application.yml | Leitura | Spring Boot | Arquivo de configuração principal da aplicação |

---

## 10. Filas Lidas

**Fila Pub/Sub:**
- **Nome da Subscription**: `business-ccbd-base-extrato-composto-sub`
- **Projeto GCP**: Variável por ambiente (bv-ccbd-des, bv-ccbd-uat, bv-ccbd-prd)
- **Classe Consumidora**: ListenerTransacoesContaCorrente
- **Tipo de Mensagem**: ExtratoCompostoRepresentation (JSON)
- **Modo de Acknowledge**: MANUAL
- **Descrição**: Consome eventos de transações e detalhes de transações de conta corrente para consolidação no Firestore

---

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Google Cloud Firestore | Database NoSQL | Armazenamento persistente de extratos compostos |
| Google Cloud Pub/Sub | Mensageria | Consumo de eventos de transações bancárias |
| OAuth2 Server | Autenticação | Validação de tokens JWT para autenticação de requisições REST (URLs variam por ambiente) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões de microserviços e separação de responsabilidades
- Uso adequado de padrões como Repository, Service, Mapper e DTO
- Implementação de logging estruturado com AOP para medição de tempo de execução
- Tratamento de exceções centralizado e consistente
- Uso de tecnologias modernas e adequadas ao contexto (Firestore reativo, Pub/Sub)
- Documentação OpenAPI bem definida
- Testes unitários presentes (estrutura completa de testes)
- Configuração externalizada por ambiente

**Pontos de Melhoria:**
- Algumas classes de serviço com múltiplas responsabilidades (ExtratoCompostoService poderia ser dividida)
- Lógica de paginação complexa que poderia ser melhor documentada
- Alguns métodos longos que poderiam ser refatorados para melhor legibilidade
- Falta de validações mais robustas em alguns pontos de entrada
- Comentários de código em português e inglês misturados

O código demonstra maturidade técnica e boas práticas, com espaço para melhorias incrementais em organização e documentação.

---

## 14. Observações Relevantes

1. **Modelo de Consistência Eventual**: O sistema trabalha com eventos assíncronos, onde transações e detalhes podem chegar em momentos diferentes
2. **Idempotência**: A geração de ID por hash garante que o mesmo evento processado múltiplas vezes não gera duplicatas
3. **Paginação Bidirecional**: Implementação customizada permite navegação para frente e para trás nos resultados
4. **Multi-ambiente**: Configuração preparada para ambientes des, uat e prd com variáveis específicas
5. **Segurança**: Endpoints protegidos por OAuth2 JWT, com exceção de endpoints públicos (swagger, actuator)
6. **Observabilidade**: Integração com Prometheus e métricas via Actuator
7. **Resiliência**: Configuração de retry e timeout via bootstrap.sh no Docker
8. **Padrão Atlante**: Segue o padrão arquitetural Atlante do Banco Votorantim para microserviços atômicos
9. **Health Checks**: Probes de liveness e readiness configurados para Kubernetes
10. **Limitações**: Tamanho máximo de página configurável (padrão 1000 registros)