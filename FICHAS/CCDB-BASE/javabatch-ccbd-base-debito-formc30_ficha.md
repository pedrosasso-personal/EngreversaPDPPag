# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **javabatch-ccbd-base-debito-formc30** é um processador batch Java desenvolvido para ler, processar e enviar para fila RabbitMQ os dados de transações e ocorrências de cartões de débito provenientes de arquivos no formato FormC30 (formato de arquivo de bandeiras de cartão).

O sistema realiza as seguintes operações principais:
- Lê arquivos FormC30 de um diretório específico
- Processa registros de transações (B1/B2) e ocorrências (B7/B8)
- Converte os dados para o formato de conciliação interno (RecordConciliation)
- Envia os registros processados para uma fila RabbitMQ
- Move os arquivos processados para diretórios de sucesso ou erro

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê arquivos FormC30 do diretório, identifica tipos de registro (B0, B1, B2, B7, B8) e fornece registros para processamento |
| **ItemProcessor** | Processa cada registro lido, delegando para FormCProcessorService e tratando exceções |
| **ItemWriter** | Envia objetos RecordConciliation processados para fila RabbitMQ |
| **FormCProcessorService** | Orquestra o processamento de registros B1/B7 com seus complementos B2/B8 |
| **RegistroMapper** | Mapeia strings de arquivo para objetos de domínio (B1, B2, B7, B8, B0) |
| **RecordConciliationMapper** | Converte objetos de domínio para RecordConciliation (formato de saída) |
| **B1RegistroPrincipalTransacao** | Representa registro principal de transações |
| **B2RegistroComplementarTransacao** | Representa complemento de transação |
| **B7RegistroPrincipalOcorrencia** | Representa registro principal de ocorrências |
| **B8RegistroComplementarOcorrencia** | Representa complemento de ocorrência |
| **BZeroCabecalhoServico** | Representa cabeçalho do arquivo FormC |
| **RecordConciliation** | Objeto de saída contendo dados consolidados para conciliação |
| **FileUtils** | Utilitário para movimentação de arquivos entre diretórios |
| **DateUtils** | Utilitário para conversão e ajuste de datas |
| **StringUtils** | Utilitário para manipulação de strings e conversão JSON |
| **MathUtils** | Utilitário para conversão de valores numéricos |

---

## 3. Tecnologias Utilizadas

- **Java** (linguagem de programação)
- **Spring Batch** (framework de processamento batch)
- **Spring Framework** (injeção de dependências e configuração)
- **Maven** (gerenciamento de dependências e build)
- **RabbitMQ** (fila de mensagens via spring-amqp e spring-rabbit)
- **Jackson** (serialização/deserialização JSON - versão 2.5.1)
- **Log4j** (logging)
- **JUnit** (testes unitários)
- **Mockito** (mocks para testes - versão 2.28.2)
- **BV Framework Batch** (framework proprietário para batch jobs)
- **Apache Commons Lang** (utilitários)

---

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch que não expõe endpoints REST.

---

## 5. Principais Regras de Negócio

1. **Leitura de Arquivos FormC30**: O sistema busca arquivos com "FORMC" no nome no diretório de recebidos
2. **Processamento de Cabeçalho (B0)**: Extrai informações do cabeçalho para contexto de processamento
3. **Identificação de Registros com Complemento**: Verifica flag na posição 79-80 para determinar se há registro complementar
4. **Pareamento de Registros**: Associa registros principais (B1/B7) com seus complementos (B2/B8)
5. **Ajuste de Data**: Ajusta ano da transação baseado na data de referência do cabeçalho
6. **Decodificação de Quina de Cartão**: Extrai código produto, número conta e correlativo do número mascarado do cartão (16 dígitos)
7. **Classificação de Tipo de Transação**: 
   - Código "000100" = Sucesso (0200)
   - Código "002250" = Chargeback (0400)
8. **Conversão de Valores**: Converte valores com casas decimais implícitas
9. **Movimentação de Arquivos**: 
   - Sucesso: move para diretório "processados"
   - Erro: move para diretório "erro"
10. **Serialização para Fila**: Converte objetos para JSON antes de enviar para RabbitMQ

---

## 6. Relação entre Entidades

**Hierarquia de Interfaces:**
- `RegistroPrincipal` (interface) ← implementada por `B1RegistroPrincipalTransacao` e `B7RegistroPrincipalOcorrencia`
- `Complemento` (interface) ← implementada por `B2RegistroComplementarTransacao` e `B8RegistroComplementarOcorrencia`

**Relacionamentos:**
- `FileProcessorRecord` contém: linha principal, linha complementar, nome arquivo e `BZeroCabecalhoServico`
- `B1RegistroPrincipalTransacao` possui um `Complemento` (B2)
- `B7RegistroPrincipalOcorrencia` possui um `Complemento` (B8)
- `RecordConciliation` é o objeto final gerado a partir de `RegistroPrincipal`

**Fluxo de Dados:**
```
Arquivo FormC30 → FileProcessorRecord → RegistroPrincipal (B1/B7) + Complemento (B2/B8) → RecordConciliation → Fila RabbitMQ
```

---

## 7. Estruturas de Banco de Dados Lidas

Não se aplica. O sistema não realiza leitura direta de banco de dados.

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema não realiza operações de escrita em banco de dados.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| Arquivos FormC30 (contendo "FORMC" no nome) | Leitura | `ItemReader` / diretório `arquivo/recebidos/` | Arquivos de entrada contendo transações e ocorrências de cartões |
| robo.log | Gravação | Log4j / diretório `log/` | Log de execução do batch |
| statistics-{executionId}.log | Gravação | Log4j / diretório `log/` | Log de estatísticas de execução |
| Arquivos FormC30 processados | Movimentação | `ItemReader.handleDispose()` / diretório `arquivo/processados/` | Arquivos movidos após processamento com sucesso |
| Arquivos FormC30 com erro | Movimentação | `ItemReader.handleDispose()` / diretório `arquivo/erro/` | Arquivos movidos quando ocorre erro no processamento |

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

---

## 11. Filas Geradas

| Nome da Fila/Exchange | Tecnologia | Classe Responsável | Breve Descrição |
|----------------------|------------|-------------------|-----------------|
| **Exchange:** events.ex.business.ccbd.registroBandeira<br>**Routing Key:** CCBD.registroBandeira | RabbitMQ | `ItemWriter` | Publica mensagens JSON contendo objetos RecordConciliation com dados de transações/ocorrências processadas |

**Configuração por Ambiente:**
- **DES:** Host 10.179.172.71:5672, usuário _ccbd_des
- **UAT:** Host 10.39.88.213:5672, usuário _ccbd_uat
- **PRD:** Host 10.39.49.197:5672, usuário _ccbd_prd

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **RabbitMQ** | Fila de Mensagens | Recebe mensagens JSON com dados de conciliação de transações de cartão processadas do FormC30 |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades (Reader, Processor, Writer)
- Uso adequado de interfaces para abstrair tipos de registro
- Utilitários bem organizados em classes específicas
- Tratamento de exceções com códigos de saída customizados
- Uso de padrões do Spring Batch
- Presença de testes unitários

**Pontos de Melhoria:**
- Comentários em português misturados com código em inglês
- Caracteres especiais mal codificados (encoding issues) nos comentários
- Uso de `StringBuilder` para parsing de strings poderia ser substituído por abordagens mais robustas
- Classe `StringUtils` com método estático `desfazerQuina` que retorna objeto parcialmente preenchido em caso de erro (poderia lançar exceção)
- Falta de validações mais rigorosas em alguns pontos (ex: tamanho de strings)
- Hardcoded de valores como nomes de exchange e routing keys
- Método `charLength` em `RegistroMapper` modifica estado compartilhado (StringBuilder) de forma não thread-safe
- Falta de documentação JavaDoc em métodos públicos
- Alguns métodos muito longos (ex: `RegistroMapper` com múltiplos métodos de parsing similares)

---

## 14. Observações Relevantes

1. **Formato de Arquivo**: O sistema processa arquivos no formato FormC30, que é um padrão de arquivo de bandeiras de cartão com registros de tamanho fixo
2. **Tipos de Registro Suportados**: B0 (cabeçalho), B1/B2 (transações), B7/B8 (ocorrências)
3. **Encoding**: Arquivos são lidos com encoding UTF-8
4. **Execução Concorrente**: Configurado para permitir execução concorrente (`concurrentExecution=true`)
5. **Memória JVM**: Configurado com -Xms512M -Xmx512M
6. **Códigos de Saída Customizados**:
   - 10: Erro na leitura do arquivo
   - 20: Erro durante processamento
   - 30: Erro na inicialização/envio para fila
   - 50: Diretório vazio ou arquivo inválido
7. **Versionamento**: Versão atual 0.8.0
8. **Framework Proprietário**: Utiliza BV Framework Batch (versão 13.0.19), framework interno da organização
9. **Ambientes**: Possui configurações específicas para DES, UAT e PRD
10. **Estratégia de Retomada**: Implementa `MyResumeStrategy` que não permite retomada em caso de erro (`canResume` retorna false)