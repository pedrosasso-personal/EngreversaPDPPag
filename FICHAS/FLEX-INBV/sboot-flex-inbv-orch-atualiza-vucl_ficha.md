# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-flex-inbv-orch-atualiza-vucl** é um orquestrador desenvolvido em Java com Spring Boot e Apache Camel, responsável por receber dados gerais de clientes (pessoas físicas), realizar mapeamento de domínios (conversão de códigos entre sistemas), e publicar essas informações em uma fila RabbitMQ para processamento assíncrono pelo sistema CADU (Cadastro Único). O sistema atua como intermediário entre o sistema Flex e o CDSP (Cadastro de Pessoas), realizando transformações e validações de dados antes do envio.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal que inicializa a aplicação Spring Boot |
| **AtualizaVuclRouter** | Rota principal do Apache Camel que orquestra o fluxo de atualização de dados |
| **DadosGeraisProcessor** | Processa e deserializa os dados gerais recebidos na requisição |
| **DominiosDeParaProcessor** | Realiza o mapeamento (de-para) de domínios entre sistemas |
| **IntegracaoCaduRepositoryImpl** | Responsável por enviar mensagens para a fila do CADU |
| **MapeamentoDominioRepositoryImpl** | Busca mapeamentos de domínios via API externa |
| **JwtClientCredentialInterceptor** | Intercepta requisições para injetar token JWT de autenticação |
| **TrataErroResponseProcessor** | Processa e padroniza erros ocorridos durante o fluxo |
| **DadosGeraisMapper** | Mapeia objetos de requisição para objetos de domínio |
| **FlexCubeMapeamentoDominios** | Gerencia cache de mapeamentos de domínios |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x**
- **Apache Camel 3.x** (orquestração de rotas e integração)
- **RabbitMQ** (mensageria assíncrona)
- **MapStruct** (mapeamento de objetos)
- **Jackson** (serialização/deserialização JSON)
- **Logback** (logging em formato JSON)
- **SpringDoc OpenAPI** (documentação de APIs)
- **Lombok** (redução de código boilerplate)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Google Cloud Platform** (infraestrutura)
- **Micrometer/Prometheus** (métricas)
- **Spring Security OAuth2** (autenticação JWT)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/atualizar/dados | AtualizaVuclRouter (Camel REST DSL) | Recebe dados gerais de clientes para atualização no VUCL |

---

## 5. Principais Regras de Negócio

1. **Validação de Dados de Entrada**: Valida se os dados obrigatórios de pessoa física foram informados corretamente
2. **Mapeamento de Domínios**: Converte códigos de domínios (sexo, endereço, contato) do padrão CDSP-AFAP para o padrão interno do sistema
3. **Validação de Chaves de Domínio**: Verifica se as chaves de mapeamento existem; caso contrário, retorna erro HTTP 400
4. **Enriquecimento de Dados**: Adiciona informações complementares aos dados antes do envio
5. **Publicação Assíncrona**: Envia dados validados e transformados para fila RabbitMQ para processamento posterior
6. **Tratamento de Erros Padronizado**: Captura exceções de diferentes componentes e retorna respostas de erro padronizadas
7. **Autenticação via JWT**: Todas as requisições externas são autenticadas com token JWT obtido via OAuth2 Client Credentials

---

## 6. Relação entre Entidades

**Principais entidades e seus relacionamentos:**

- **Dados**: Entidade raiz contendo todas as informações do cliente
  - Possui 1 **DetalhePessoaFisica** (dados pessoais)
  - Possui N **Contato** (telefones, emails)
  - Possui N **Endereco** (endereços residenciais/comerciais)
  - Possui N **DadoBanco** (dados bancários)
  - Possui N **Documento** (RG, CNH, etc)
  - Possui N **Relacionamento** (relacionamentos bancários)

- **Dominio**: Estrutura de mapeamento chave-valor para conversão de códigos entre sistemas

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | leitura | Configuração de logging | Arquivo de configuração de logs em formato JSON para diferentes ambientes |
| application.yml | leitura | Spring Boot | Arquivo de configuração principal da aplicação |
| application-des.yml | leitura | Spring Boot | Configurações específicas do ambiente de desenvolvimento |
| application-local.yml | leitura | Spring Boot | Configurações para execução local |
| sboot-flex-inbv-orch-atualiza-vucl.yaml | leitura | OpenAPI Generator | Especificação OpenAPI da API REST |
| sboot-intr-base-acl-mapeamento-dominio.yaml | leitura | OpenAPI Generator | Especificação da API de mapeamento de domínios |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Responsável | Descrição |
|--------------|------------|-------------------|-----------|
| QF.CDSP.BASE.ASSINC-CLIENTES | RabbitMQ | IntegracaoCaduRepositoryImpl | Fila para envio assíncrono de dados de clientes para o sistema CADU |

**Configurações da Fila:**
- **Exchange**: QF.CDSP.BASE.ASSINC-CLIENTES
- **Routing Key**: "" (vazia)
- **Virtual Host**: /
- **Formato**: JSON

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **sboot-intr-base-acl-mapeamento-dominio** | API REST | Serviço de mapeamento de domínios entre sistemas (conversão de códigos) |
| **API Gateway OAuth2** | API REST | Serviço de autenticação para obtenção de tokens JWT via Client Credentials |
| **RabbitMQ CDSP** | Mensageria | Broker de mensagens para comunicação assíncrona com o sistema CADU |

**Endpoints Integrados:**
- Mapeamento de Domínios: `/v2/corporativo/integrador-canais/mapeamento-dominios`
- Token JWT: `/auth/oauth/v2/token-jwt`

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com uso de camadas (router, processor, port, service)
- Uso adequado de padrões como Repository, Mapper e Processor
- Configurações externalizadas em arquivos YAML
- Uso de Lombok para redução de boilerplate
- Implementação de tratamento de erros centralizado
- Documentação OpenAPI presente
- Logs estruturados em JSON

**Pontos de Melhoria:**
- Código duplicado em classes de tratamento de erro (TrataErroResponseProcessor aparece em dois pacotes)
- Falta de testes unitários abrangentes (apenas testes básicos presentes)
- Comentários em código poderiam ser mais descritivos
- Algumas classes com responsabilidades que poderiam ser melhor divididas
- Falta de validações mais robustas em alguns pontos
- Configurações hardcoded em alguns processadores (nomes de interfaces de domínio)
- Ausência de circuit breakers ou retry policies para chamadas externas

---

## 14. Observações Relevantes

1. **Arquitetura Baseada em Camel**: O sistema utiliza Apache Camel como framework de integração, o que proporciona flexibilidade para orquestração de fluxos complexos

2. **Ambientes Suportados**: O sistema está preparado para execução em múltiplos ambientes (local, des, uat, prd) com configurações específicas

3. **Segurança**: Implementa autenticação via JWT com OAuth2 Client Credentials Flow, com tokens gerenciados automaticamente

4. **Observabilidade**: Possui endpoints de health check, métricas Prometheus e logs estruturados em JSON para facilitar monitoramento

5. **Containerização**: Dockerfile multi-layer otimizado para reduzir tempo de build e tamanho da imagem

6. **Mapeamento de Domínios**: Sistema crítico depende de mapeamentos corretos; falhas no mapeamento resultam em rejeição da requisição

7. **Processamento Assíncrono**: Utiliza padrão fire-and-forget para publicação na fila, sem confirmação de processamento pelo consumidor

8. **Infraestrutura**: Preparado para execução em Google Cloud Platform com configurações específicas de infraestrutura como código

9. **Trilha de Auditoria**: Integrado com framework de auditoria do Banco Votorantim (arqt-base-trilha-auditoria)

10. **Limitações Conhecidas**: Não há implementação de retry ou dead letter queue para mensagens que falharem no processamento