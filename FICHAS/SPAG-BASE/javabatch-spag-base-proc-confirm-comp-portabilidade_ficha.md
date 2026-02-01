# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java responsável por processar arquivos XML no formato APCS108 contendo informações sobre aceites compulsórios de portabilidade de conta salário. O sistema lê arquivos XML recebidos, extrai os dados de aceite compulsório, transforma-os em objetos de domínio e publica mensagens em filas RabbitMQ para processamento posterior. Após o processamento bem-sucedido, move os arquivos para uma pasta de processados.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê e parseia arquivos XML APCS108, iterando sobre os aceites compulsórios contidos no arquivo |
| **ItemProcessor** | Transforma objetos AceiteCompulsorio em objetos de domínio (DominioPortabilidade e DominioControleArquivo) |
| **ItemWriter** | Envia os objetos processados para filas RabbitMQ através do PortabilidadeRepository |
| **PortabilidadeRepository** | Gerencia o envio de mensagens para as filas RabbitMQ (portabilidade e controle de arquivo) |
| **Apcs108Estrutura** | Responsável por extrair e estruturar dados do documento XML APCS108 |
| **EstruturaArquivoFactory** | Factory para criação de documentos XML com validações de segurança |
| **PortabilidadeMapper** | Converte objetos AceiteCompulsorio em objetos de domínio |
| **MyResumeStrategy** | Estratégia de retomada do job em caso de falha (atualmente não permite retomada) |
| **Portabilidade** | Entidade de domínio representando uma portabilidade |
| **ControleArquivo** | Entidade de domínio representando o controle de processamento de arquivo |
| **AceiteCompulsorio** | Estrutura de dados representando um aceite compulsório extraído do XML |

## 3. Tecnologias Utilizadas

- **Java** com Maven
- **Framework BV Sistemas Batch** (framework proprietário para processamento batch)
- **Spring Framework** (versão 2.0 - configuração XML)
- **RabbitMQ** via Spring AMQP para mensageria
- **Log4j** para logging
- **Gson** (2.8.9) para serialização JSON
- **Jackson** (2.12.6) para processamento JSON
- **JUnit** e **Mockito** para testes
- **Apache Commons IO** para manipulação de arquivos
- **XML DOM Parser** para processamento de arquivos XML

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch que não expõe endpoints REST.

## 5. Principais Regras de Negócio

1. **Processamento de Aceites Compulsórios**: O sistema processa aceites compulsórios de portabilidade de conta salário recebidos via arquivo XML no padrão APCS108 da CIP (Câmara Intersticial de Pagamentos)

2. **Validação de Estrutura XML**: Arquivos XML são validados contra XSD com features de segurança habilitadas (proteção contra XXE, DTD injection)

3. **Constantes de Negócio**: 
   - Tipo de motivo de portabilidade fixo: 1 (comentário indica que deveria ser 5 após inclusão de domínio)
   - Situação de portabilidade fixa: 6 (comentário indica que deveria ser 1 após inclusão de domínio)

4. **Movimentação de Arquivos**: Após processamento bem-sucedido (exit code = 0), arquivos são movidos da pasta "recebido" para "processado"

5. **Tratamento de Erros**: Sistema define códigos de erro específicos (10-14) para diferentes tipos de falha no processamento

6. **Publicação Dual**: Para cada aceite compulsório, são publicadas duas mensagens: uma para portabilidade e outra para controle de arquivo

## 6. Relação entre Entidades

**Estrutura de Dados do Arquivo XML:**
- **CabecalhoArquivo**: Contém metadados do arquivo (nome, data de referência)
  - Relaciona-se com múltiplos **AceiteCompulsorio**

- **PortabilidadeCompulsoria**: Agrupa informações de processamento
  - Contém data de referência, data/hora de processamento e número de controle CIP
  - Relaciona-se com múltiplos **AceiteCompulsorio**

- **AceiteCompulsorio**: Entidade principal do processamento
  - Contém: identificador do participante, número de portabilidade PCS, código de situação, data de aceite
  - Referencia **PortabilidadeCompulsoria** e **CabecalhoArquivo**

**Objetos de Domínio:**
- **GrupoPortabilidadeControleArquivo**: Agrupa os dois domínios para processamento conjunto
  - Contém **DominioPortabilidade** e **DominioControleArquivo**

- **DominioPortabilidade**: Wrapper contendo **Portabilidade**
- **DominioControleArquivo**: Wrapper contendo **ControleArquivo**

- **Portabilidade**: Entidade de negócio com número único CIP, código de motivo e situação
- **ControleArquivo**: Entidade de controle com data de recebimento, número único, nome do arquivo e códigos de motivo/situação

## 7. Estruturas de Banco de Dados Lidas

Não se aplica. O sistema não realiza leitura direta de banco de dados.

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema não realiza operações diretas em banco de dados.

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| APCS108_*.xml | Leitura | ItemReader (/arquivo/recebido/) | Arquivos XML contendo aceites compulsórios de portabilidade no formato APCS108 da CIP |
| APCS108_*.xml | Movimentação | ItemReader (de /arquivo/recebido/ para /arquivo/processado/) | Após processamento bem-sucedido, arquivos são movidos para pasta de processados |
| robo.log | Gravação | Log4j (RollingFileAppender) | Log de execução do batch com rotação de 2MB e 5 backups |
| statistics-${executionId}.log | Gravação | BvDailyRollingFileAppender | Log de estatísticas do framework batch com rotação diária |

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

## 11. Filas Geradas

| Nome da Fila (Routing Key) | Exchange | Classe Responsável | Descrição |
|---------------------------|----------|-------------------|-----------|
| SPAG.confirmacaoPortablidade | events.business.portabilidade | PortabilidadeRepository | Fila para publicação de confirmações de portabilidade processadas |
| SPAG.confirmacaoArqPortabilidade | events.business.portabilidade | PortabilidadeRepository | Fila para publicação de controle de arquivos processados |

**Configurações por Ambiente:**
- **DES**: Host 10.39.216.217:5672, usuário _spag_des
- **UAT**: Host 35.247.239.246:5672, usuário _spag_uat
- **PRD**: Host 10.39.49.197:5672, usuário _spag_prd
- **TEST**: Host localhost:5672, usuário guest

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **RabbitMQ** | Mensageria | Sistema de filas para publicação de eventos de portabilidade e controle de arquivos. Utiliza Spring AMQP com confirmações de publicação habilitadas |
| **CIP (Câmara Intersticial de Pagamentos)** | Arquivo XML | Recebe arquivos XML no formato APCS108 contendo aceites compulsórios de portabilidade de conta salário |

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com padrão Reader-Processor-Writer
- Uso adequado de logging
- Tratamento de exceções com códigos de erro específicos
- Validações de segurança XML (proteção contra XXE)
- Testes unitários implementados
- Uso de mappers para transformação de dados

**Pontos Negativos:**
- **Código comentado em produção**: Constantes com TODOs indicando valores temporários (TIPO_MOTIVO_PORTABILIDADE e SITUACAO_PORTABILIDADE)
- **Configurações hardcoded**: Senhas e IPs em arquivos XML de configuração (especialmente problemático em PRD)
- **Falta de externalização**: Nomes de filas, exchanges e routing keys estão hardcoded no código
- **Versões desatualizadas**: Spring 2.0 é extremamente antigo, Gson poderia ser substituído por Jackson já presente
- **Tratamento de erro limitado**: MyResumeStrategy apenas loga e retorna false, sem estratégia de retry
- **Falta de validações**: Não há validação dos dados extraídos do XML antes do envio para filas
- **Encoding inconsistente**: Comentários em português com caracteres especiais podem causar problemas
- **Documentação limitada**: Falta JavaDoc nas classes principais
- **Acoplamento ao framework proprietário**: Dependência forte do framework BV Sistemas dificulta manutenção e migração

## 14. Observações Relevantes

1. **Ambiente de Execução**: Sistema projetado para execução standalone via linha de comando (.bat), não é um serviço contínuo

2. **Parâmetro Obrigatório**: O job requer o parâmetro "nomeArquivo" para execução, indicando qual arquivo processar

3. **Pendências Técnicas**: Existem TODOs no código indicando que valores de constantes (TIPO_MOTIVO_PORTABILIDADE=1 e SITUACAO_PORTABILIDADE=6) devem ser alterados após inclusão de domínio de aceite compulsório no banco

4. **Segurança**: Implementa proteções contra vulnerabilidades XML (XXE, DTD injection, external entities)

5. **Versionamento**: Versão atual 0.3.0, indicando que ainda está em fase de desenvolvimento/estabilização

6. **Formato de Mensagens**: Mensagens publicadas nas filas são em formato JSON com encoding UTF-8

7. **Arquivos de Exemplo**: Projeto contém arquivos XML de exemplo para testes (APCS108_59588111_20210613_00000.xml e APCS108_59588111_20210727_00001)

8. **Schema XSD**: Inclui schemas completos (APCS108.xsd e APCSTIPOS.xsd) para validação dos arquivos XML

9. **Jenkins Integration**: Arquivo jenkins.properties indica integração com pipeline CI/CD, com deploy em QA desabilitado

10. **Identificador Único**: Sistema utiliza número único de 21 dígitos (NU) gerado pelo PCS para identificação de portabilidades