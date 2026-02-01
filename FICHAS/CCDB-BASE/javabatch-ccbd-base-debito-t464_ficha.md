# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **javabatch-ccbd-base-debito-t464** é um processamento batch Java desenvolvido para ler, processar e enviar registros de transações de débito da bandeira Mastercard (arquivo T464) para uma fila RabbitMQ. O sistema lê arquivos no formato DBK contendo registros financeiros e não-financeiros, processa as informações de transações, realiza mapeamento de dados e publica mensagens em formato JSON para consumo por outros sistemas.

O processamento segue o padrão Reader-Processor-Writer do framework BV Sistemas, realizando a leitura de arquivos posicionais, transformação de dados e envio para fila de mensageria.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê arquivos T464 (.DBK) da pasta "recebidos", processa linha a linha identificando tipos de registro (FHDR, FREC, NREC, EREC, FPST, EPST, etc) |
| **ItemProcessor** | Processa cada registro lido, invocando FinancialService para transformação dos dados |
| **ItemWriter** | Envia objetos RecordConciliation processados para fila RabbitMQ em formato JSON |
| **FinancialService** | Orquestra o processamento de registros financeiros e seus adendos (posting addendum) |
| **FinancialNonFinancialMapper** | Mapeia objetos FinancialAbstract para RecordConciliation, extraindo informações de cartão e transação |
| **ProcessorUtils** | Utilitário para parsing de linhas posicionais em objetos VO específicos por tipo de registro |
| **FileUtils** | Gerencia movimentação de arquivos entre pastas (recebidos/processados/erro) |
| **MyResumeStrategy** | Estratégia de retomada de processamento em caso de falha |

---

## 3. Tecnologias Utilizadas

- **Java** (versão não especificada explicitamente)
- **Apache Maven** (gerenciamento de dependências e build)
- **Spring Framework** (IoC/DI via XML)
- **Spring AMQP / RabbitMQ** (mensageria - versão 1.2.0.M1)
- **BV Framework Batch** (framework proprietário para processamento batch)
- **Jackson** (serialização JSON - versão 2.12.7)
- **Log4j** (logging)
- **JUnit** e **Mockito** (testes unitários)

---

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch sem endpoints REST.

---

## 5. Principais Regras de Negócio

1. **Filtragem de Registros**: Linhas do tipo FPS2 e EPS2 são ignoradas e não processadas
2. **Identificação de Tipo de Transação**: Registros FREC/NREC são classificados como transações de sucesso (código 0200), enquanto EREC são chargebacks (código 0400)
3. **Extração de Dados de Cartão (Quina)**: Tenta extrair código do produto, número da conta e correlativo dos primeiros e últimos dígitos do PAN. Em caso de falha, armazena o número mascarado
4. **Processamento de Pares de Linhas**: Cada registro financeiro (FREC/NREC/EREC) deve ser seguido de seu adendo (FPST/EPST)
5. **Conversão de Valores Monetários**: Valores são convertidos considerando casas decimais implícitas definidas no registro
6. **Movimentação de Arquivos**: Arquivos processados com sucesso vão para pasta "processados", com erro vão para pasta "erro"
7. **Validação de Arquivo**: Sistema valida presença de arquivo T464 antes de iniciar processamento

---

## 6. Relação entre Entidades

**Hierarquia de Value Objects:**

- **FinancialAbstract** (classe abstrata)
  - FinancialNonFinancialRecordVO (registros FREC/NREC)
  - ExceptionFinancialNonFinancialRecordVO (registros EREC)

- **PostingAddendumAbstract** (classe abstrata)
  - FinancialPostingAddendumRecordVO (registros FPST)
  - ExceptionPostingAddendumRecordVO (registros EPST)

**Relacionamentos:**
- FileProcessorRecordVO agrega: linha principal + linha adendo + FileHeaderRecordVO + nome do arquivo
- FinancialAbstract contém: PostingAddendumAbstract + FileHeaderRecordVO
- RecordConciliation é o objeto final enviado para fila, contendo dados consolidados da transação

---

## 7. Estruturas de Banco de Dados Lidas

Não se aplica. O sistema não acessa banco de dados diretamente.

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema não atualiza banco de dados diretamente.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| *.DBK (T464) | Leitura | ItemReader / pasta "recebidos" | Arquivos posicionais contendo registros de transações Mastercard |
| robo.log | Gravação | Log4j / pasta "log" | Log de execução do processamento |
| statistics-{executionId}.log | Gravação | Log4j / pasta "log" | Log de estatísticas do framework BV |

**Movimentação de arquivos:**
- Origem: `/arquivo/recebidos/`
- Sucesso: `/arquivo/processados/`
- Erro: `/arquivo/erro/`

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

---

## 11. Filas Geradas

| Nome da Fila/Exchange | Tecnologia | Classe Responsável | Breve Descrição |
|----------------------|------------|-------------------|-----------------|
| **Exchange**: events.ex.business.ccbd.registroBandeira<br>**Routing Key**: CCBD.registroBandeira | RabbitMQ | ItemWriter | Publica objetos RecordConciliation em formato JSON contendo dados de transações processadas |

**Configurações por ambiente:**
- **DES**: host 10.39.216.137, usuário _ccbd_des
- **UAT**: host 10.39.88.213, usuário _ccbd_uat
- **PRD**: host 10.39.49.197, usuário _ccbd_prd

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| RabbitMQ | Mensageria | Publicação de eventos de transações processadas para consumo por outros sistemas |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades (Reader, Processor, Writer)
- Uso adequado de Value Objects para representar diferentes tipos de registro
- Documentação JavaDoc presente em várias classes VO
- Tratamento de exceções customizado (ProcessorException)
- Uso de enums para tipos de registro e formatos de data
- Testes unitários presentes (embora não enviados para análise)

**Pontos de Melhoria:**
- Uso de StringBuilder mutável em ProcessorUtils com método estático pode causar problemas de concorrência
- Parsing manual de strings posicionais é propenso a erros (poderia usar biblioteca especializada)
- Classe ProcessorUtils muito extensa com múltiplos métodos similares (violação DRY)
- Uso de versões antigas de bibliotecas (Spring AMQP 1.2.0.M1 de 2012)
- Falta de validações mais robustas em conversões numéricas (parseInt retorna 0 em caso de erro)
- Código de extração de "quina" com try-catch genérico mascarando possíveis problemas
- Configurações hardcoded em várias classes (paths, nomes de filas)
- Falta de constantes para números mágicos (tamanhos de campos, posições)

---

## 14. Observações Relevantes

1. **Framework Proprietário**: O sistema utiliza o framework BV Sistemas Batch (br.com.bvsistemas.framework.batch), que não é público
2. **Formato de Arquivo**: Processa arquivos T464 da Mastercard em formato posicional de 250 caracteres por linha
3. **Códigos de Saída Customizados**: 
   - 10: Erro de leitura de arquivo
   - 20: Erro de processamento
   - 30: Erro de inicialização/envio de fila
4. **Versionamento**: Projeto na versão 0.9.0 (pré-release)
5. **Estrutura Maven Multi-módulo**: Separação entre core (lógica) e dist (distribuição)
6. **Ambientes**: Suporta DES, UAT e PRD com configurações específicas por ambiente
7. **Mascaramento de Dados**: Sistema mascara número de cartão quando não consegue extrair informações da "quina"
8. **Processamento Sequencial**: Não há evidências de processamento paralelo ou multi-thread