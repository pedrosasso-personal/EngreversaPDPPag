# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java responsável por processar arquivos XML de confirmação de portabilidade de contas salário (padrão APCS104) recebidos da CIP (Câmara Interbancária de Pagamentos). O sistema lê arquivos XML contendo confirmações de aprovação ou reprovação de portabilidade, processa os registros e publica mensagens em filas RabbitMQ para controle de arquivo e atualização de situação de portabilidade.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê e parseia o arquivo XML APCS104, extrai o cabeçalho e itera sobre os registros de portabilidade |
| **ItemProcessor** | Transforma objetos ControleArquivo em objetos Situacao através do SituacaoMapper |
| **ItemWriter** | Envia mensagens para filas RabbitMQ (portabilidade e controle de arquivo) |
| **SituacaoRepository** | Gerencia o envio de mensagens para as filas RabbitMQ |
| **SituacaoMapper** | Converte objetos de controle de arquivo em mensagens de portabilidade e controle |
| **Apcs104Estrutura** | Extrai dados estruturados do documento XML APCS104 |
| **EstruturaArquivoFactory** | Factory para criação de Document XML com configurações de segurança |
| **MyResumeStrategy** | Estratégia de retomada do batch em caso de falhas |

---

## 3. Tecnologias Utilizadas

- **Java** com Maven
- **Framework BV Batch** (br.com.bvsistemas.framework.batch) - framework proprietário para processamento batch
- **Spring Framework** (configuração XML)
- **RabbitMQ** via Spring AMQP para mensageria
- **Jackson** (2.5.1) para serialização JSON
- **Log4j** para logging
- **Apache Commons IO** para manipulação de arquivos
- **JUnit** e **Mockito** para testes
- **XML DOM Parser** para processamento de arquivos XML

---

## 4. Principais Endpoints REST

não se aplica

---

## 5. Principais Regras de Negócio

1. **Processamento de Confirmações de Portabilidade**: O sistema processa arquivos XML APCS104 contendo confirmações de portabilidade de contas salário
2. **Identificação de Aprovação/Reprovação**: Verifica se a portabilidade foi aprovada (tag `Grupo_APCS104_PortddCtSalrAprovd`) ou reprovada (tag `Grupo_APCS104_PortddCtSalrRepvd`)
3. **Mapeamento de Situações**: 
   - Aprovado: código situação = 2, motivo = null
   - Reprovado: código situação = 3, motivo extraído do XML
4. **Movimentação de Arquivos**: Após processamento bem-sucedido (exitCode = 0), move o arquivo de `/arquivo/recebido/` para `/arquivo/processado/`
5. **Publicação Dual**: Para cada registro processado, publica duas mensagens: uma para controle de arquivo e outra para atualização de portabilidade
6. **Tratamento de Erros**: Define códigos de erro específicos (10-13) para diferentes tipos de falha no processamento

---

## 6. Relação entre Entidades

**Entidades principais:**

- **CabecalhoArquivo**: Contém metadados do arquivo (nome, data/hora, data referência)
- **ControleArquivo**: Representa um registro de controle com dados da portabilidade (nuUnicoCip, códigos de situação e motivo, nome arquivo, data recebimento)
- **Portabilidade**: Contém dados específicos da portabilidade (nuUnicoCip, códigos)
- **Situacao**: Agrega MessageControleArquivo e MessagePortabilidade
- **MessageControleArquivo**: Envelope para ControleArquivo
- **MessagePortabilidade**: Envelope para Portabilidade

**Relacionamentos:**
- CabecalhoArquivo (1) -> (N) ControleArquivo
- ControleArquivo (1) -> (1) Situacao
- Situacao (1) -> (1) MessageControleArquivo
- Situacao (1) -> (1) MessagePortabilidade

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
| APCS104.xml | Leitura | ItemReader (`/arquivo/recebido/`) | Arquivo XML com confirmações de portabilidade no padrão CIP APCS104 |
| APCS104.xml | Movimentação | ItemReader (`/arquivo/processado/`) | Arquivo processado movido para diretório de processados após sucesso |
| robo.log | Gravação | Log4j (RollingFileAppender) | Log de execução do batch com rotação de 2MB e 5 backups |
| statistics-{executionId}.log | Gravação | Log4j (BvDailyRollingFileAppender) | Log de estatísticas do framework BV Batch |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

**Exchange:** `events.business.portabilidade`

| Nome da Fila/Routing Key | Tipo | Classe Responsável | Breve Descrição |
|--------------------------|------|-------------------|-----------------|
| SPAG.confirmacaoPortablidade | RabbitMQ | SituacaoRepository | Mensagens com atualização de situação de portabilidade (MessagePortabilidade) |
| SPAG.confirmacaoArqPortabilidade | RabbitMQ | SituacaoRepository | Mensagens de controle de processamento de arquivo (MessageControleArquivo) |

**Configurações por ambiente:**
- **DES**: 10.39.216.217:5672 (usuário: _spag_des)
- **UAT**: 35.247.239.246:5672 (usuário: _spag_uat)
- **PRD**: 10.39.49.197:5672 (usuário: _spag_prd)

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **RabbitMQ** | Mensageria | Publicação de eventos de portabilidade e controle de arquivo para consumo por outros sistemas |
| **CIP (Câmara Interbancária de Pagamentos)** | Arquivo | Recebimento de arquivos XML APCS104 com confirmações de portabilidade de contas salário |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 6/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades (Reader, Processor, Writer)
- Uso de padrões como Factory e Mapper
- Tratamento de erros com códigos específicos
- Configurações de segurança XML (proteção contra XXE)
- Uso de logging adequado
- Testes unitários presentes

**Pontos Negativos:**
- **Acoplamento ao sistema de arquivos**: Uso de `getClass().getResource()` dificulta testes e deployment
- **Configurações hardcoded**: Senhas e IPs em arquivos XML de configuração (risco de segurança)
- **Falta de validações**: Não valida estrutura do XML antes de processar
- **Tratamento de exceções genérico**: Captura `Exception` em vários pontos
- **Código legado**: Uso de framework proprietário BV limita portabilidade
- **Falta de documentação**: Classes sem Javadoc
- **Versões desatualizadas**: Jackson 2.5.1 (2015) possui vulnerabilidades conhecidas
- **Magic numbers**: Códigos de situação (2, 3) sem enums
- **Mistura de responsabilidades**: ItemReader também move arquivos

---

## 14. Observações Relevantes

1. **Framework Proprietário**: Sistema utiliza framework BV Batch proprietário, o que pode dificultar manutenção e migração futura
2. **Segurança**: Senhas de RabbitMQ expostas em arquivos de configuração XML (job-resources.xml)
3. **Processamento Síncrono**: Batch processa arquivo completo de forma síncrona, sem paralelização
4. **Dependência de Diretórios**: Sistema depende de estrutura específica de diretórios (`/arquivo/recebido/`, `/arquivo/processado/`)
5. **Versionamento**: Versão 0.3.0 indica sistema em desenvolvimento/evolução
6. **Jenkins Integration**: Arquivo `jenkins.properties` indica integração com pipeline CI/CD
7. **Ambientes**: Configurações separadas para DES, UAT e PRD
8. **Vulnerabilidades**: Uso de Jackson 2.5.1 que possui CVEs conhecidas - recomenda-se atualização urgente
9. **Padrão CIP**: Sistema processa padrão específico brasileiro (APCS104) da Câmara Interbancária de Pagamentos