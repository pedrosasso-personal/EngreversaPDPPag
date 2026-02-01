# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java desenvolvido para processar arquivos XML no formato APCS109 contendo informações sobre movimentos diários de portabilidade de conta salário. O sistema lê arquivos XML do padrão CIP (Câmara Interbancária de Pagamentos), extrai dados de portabilidade e situações, e publica essas informações em filas RabbitMQ para processamento posterior. Após o processamento bem-sucedido, o arquivo é movido para um diretório de processados.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê e parseia arquivos XML APCS109, iterando sobre os movimentos diários de portabilidade |
| **ItemProcessor** | Transforma objetos MovimentoDiario em GrupoPortabilidadeControleArquivo usando o mapper |
| **ItemWriter** | Envia os dados processados para filas RabbitMQ (portabilidade e controle de arquivo) |
| **PortabilidadeRepository** | Gerencia o envio de mensagens para as filas RabbitMQ |
| **PortabilidadeMapper** | Converte objetos de domínio MovimentoDiario em DominioPortabilidade e DominioControleArquivo |
| **Apcs109Estrutura** | Parseia a estrutura XML do arquivo APCS109 e extrai cabeçalho e movimentos |
| **EstruturaArquivoFactory** | Factory para criação de Document XML com configurações de segurança |
| **MyResumeStrategy** | Estratégia de retomada do job em caso de falha |
| **MovimentoDiario** | DTO representando um movimento diário de portabilidade |
| **Portabilidade** | Entidade de domínio com dados de portabilidade |
| **ControleArquivo** | Entidade de controle de processamento de arquivo |

---

## 3. Tecnologias Utilizadas

- **Java** (versão não especificada explicitamente)
- **Spring Batch** (framework BV Sistemas customizado)
- **Spring Framework** (configuração XML)
- **RabbitMQ** (mensageria via Spring AMQP)
- **Maven** (gerenciamento de dependências e build)
- **Jackson** (serialização/deserialização JSON - versão 2.5.1)
- **Log4j** (logging)
- **JUnit** e **Mockito** (testes unitários)
- **Apache Commons IO** (manipulação de arquivos)
- **XML/XSD** (parsing e validação de arquivos)

---

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch que não expõe endpoints REST.

---

## 5. Principais Regras de Negócio

1. **Processamento de Portabilidade**: Extrai informações de portabilidade de conta salário do arquivo APCS109, incluindo situação, motivos e dados do cliente
2. **Validação de Arquivo XML**: Parseia e valida arquivos XML contra schema XSD com configurações de segurança (proteção contra XXE)
3. **Controle de Situação**: Identifica e processa diferentes situações de portabilidade (aprovação, reprovação, cancelamento, aceite compulsório, decurso de prazo, contestação, regularização)
4. **Categorização**: Atribui categoria fixa (4) para situação de portabilidade
5. **Rastreabilidade**: Registra data/hora de recebimento CIP e nome do arquivo para controle
6. **Movimentação de Arquivo**: Move arquivo para diretório de processados apenas em caso de sucesso (exit code = 0)
7. **Tratamento de Múltiplos Motivos**: Processa diferentes tipos de motivos de portabilidade através de enum TagMotivoPortabilidade
8. **Publicação Dual**: Envia dados tanto para fila de portabilidade quanto para fila de controle de arquivo

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **MovimentoDiario**: Contém CabecalhoArquivo (1:1), dados de referência, processamento, controle CIP, participante, número de portabilidade PCS, código de situação e motivo
- **CabecalhoArquivo**: Possui data de referência e nome do arquivo
- **Portabilidade**: Contém número único CIP, código de situação e código de motivo
- **ControleArquivo**: Possui data de recebimento CIP, número único CIP, códigos de motivo/situação, e nome do arquivo
- **DominioPortabilidade**: Wrapper de Portabilidade com categoria
- **DominioControleArquivo**: Wrapper de ControleArquivo
- **GrupoPortabilidadeControleArquivo**: Agrupa DominioPortabilidade e DominioControleArquivo (1:1)

**Relacionamentos:**
- MovimentoDiario → CabecalhoArquivo (1:1)
- MovimentoDiario → Portabilidade (transformação via mapper)
- MovimentoDiario → ControleArquivo (transformação via mapper)
- Portabilidade → DominioPortabilidade (composição)
- ControleArquivo → DominioControleArquivo (composição)

---

## 7. Estruturas de Banco de Dados Lidas

Não se aplica. O sistema não realiza leitura direta de banco de dados.

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema não realiza operações diretas em banco de dados.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| APCS109_*.xml | Leitura | ItemReader (/arquivo/recebido/) | Arquivo XML com movimentos diários de portabilidade no formato CIP |
| APCS109_*.xml | Gravação/Movimentação | ItemReader (/arquivo/processado/) | Arquivo processado movido para diretório de sucesso |
| robo.log | Gravação | Log4j (RollingFileAppender) | Log de execução do batch |
| statistics-*.log | Gravação | Log4j (BvDailyRollingFileAppender) | Log de estatísticas de execução |

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

---

## 11. Filas Geradas

| Nome da Fila/Routing Key | Exchange | Tipo de Mensagem | Descrição |
|--------------------------|----------|------------------|-----------|
| SPAG.confirmacaoPortablidade | events.business.portabilidade | JSON (DominioPortabilidade) | Fila para publicação de dados de portabilidade processados |
| SPAG.confirmacaoArqPortabilidade | events.business.portabilidade | JSON (DominioControleArquivo) | Fila para controle de arquivos processados |

**Configurações por Ambiente:**
- **DES**: host=10.39.216.217, user=_spag_des
- **UAT**: host=35.247.239.246, user=_spag_uat
- **PRD**: host=10.39.49.197, user=_spag_prd
- **TEST**: host=localhost, user=guest

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **RabbitMQ** | Mensageria | Publicação de eventos de portabilidade e controle de arquivo via Spring AMQP |
| **CIP (Câmara Interbancária de Pagamentos)** | Arquivo | Recebimento de arquivos XML APCS109 com dados de portabilidade |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades (Reader, Processor, Writer)
- Uso adequado do padrão Batch com framework Spring
- Tratamento de erros com códigos customizados
- Configuração de segurança XML (proteção contra XXE)
- Uso de DTOs e objetos de domínio bem definidos
- Logging adequado em pontos críticos
- Configurações externalizadas por ambiente

**Pontos de Melhoria:**
- Uso de versões antigas de bibliotecas (Jackson 2.5.1 de 2015)
- Configuração via XML ao invés de anotações Java (padrão legado)
- Falta de documentação JavaDoc nas classes
- Hardcoding de strings (routing keys, exchange names)
- Classe `MyResumeStrategy` muito simples, apenas loga erro e retorna false
- Falta de validações mais robustas nos DTOs
- Uso de `System.out` implícito em alguns logs
- Código com comentários em português misturado com inglês
- Falta de constantes para valores mágicos (categoria = 4)

---

## 14. Observações Relevantes

1. **Framework Proprietário**: O sistema utiliza um framework batch customizado da BV Sistemas (`br.com.bvsistemas.framework.batch`), que é uma camada sobre Spring Batch
2. **Padrão CIP**: Implementa o padrão APCS109 da Câmara Interbancária de Pagamentos para portabilidade de conta salário
3. **Segurança XML**: Implementa proteções contra ataques XXE (XML External Entity) no parsing
4. **Versionamento**: Versão atual 0.2.0, indicando que está em fase inicial de desenvolvimento
5. **Estrutura Multi-módulo**: Projeto Maven dividido em módulos `core` e `dist` para separar lógica de negócio e distribuição
6. **Execução**: Sistema executado via linha de comando (batch script) com parâmetros de nome de arquivo
7. **Transação**: Configurado como `noTransactionJobTemplate`, indicando que não usa transações de banco de dados
8. **Formato de Mensagem**: Mensagens publicadas em formato JSON com encoding UTF-8
9. **Códigos de Saída Customizados**: Define códigos de erro específicos (10-13) para diferentes tipos de falha
10. **Ambiente de Testes**: Possui estrutura completa de testes com arquivo XML de exemplo