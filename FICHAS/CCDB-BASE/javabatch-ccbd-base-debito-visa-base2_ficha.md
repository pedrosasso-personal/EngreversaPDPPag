# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de processamento batch Java desenvolvido para ler, processar e enviar registros de transações de débito VISA (Base II) para uma fila RabbitMQ. O sistema lê arquivos de texto posicionais contendo transações da bandeira VISA, extrai informações dos registros TCR0 (principal) e TCR5 (complementar), transforma os dados em objetos de conciliação (RecordConciliation) e publica as mensagens em formato JSON em uma fila para processamento posterior.

O batch utiliza o framework BV Sistemas para gerenciamento do ciclo de vida do job, implementando o padrão Reader-Processor-Writer para processamento de dados em lote.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê arquivos de texto posicionais da pasta "recebidos", agrupa registros TCR relacionados (principal + complementares) e move arquivos processados/com erro |
| **ItemProcessor** | Processa grupos de registros String, identifica TCR0 e TCR5, e transforma em objeto RecordConciliation |
| **ItemWriter** | Envia objetos RecordConciliation para fila RabbitMQ em formato JSON |
| **RecordConciliation** | Entidade de domínio que representa uma transação conciliada com todos os dados necessários |
| **TcrZero** | Representa o registro principal (TCR0) com dados da transação |
| **Tcr5** | Representa o registro complementar (TCR5) com dados de fee |
| **RecordConciliationMapper** | Mapeia objetos TcrZero e Tcr5 para RecordConciliation |
| **RegistroMapper** | Extrai campos posicionais das linhas de texto para objetos de domínio |
| **MyResumeStrategy** | Estratégia de retomada do job em caso de falha |
| **TcEnum** | Enum que define tipos de transação (compra, saque, estorno, etc.) |
| **TcrEnum** | Enum que define tipos de registro (TCR0, TCR1, TCR2, TCR5, TCR7) |
| **DateUtils** | Utilitário para formatação e manipulação de datas |
| **FileUtils** | Utilitário para movimentação e listagem de arquivos |
| **MathUtils** | Utilitário para conversão de valores numéricos e BigDecimal |
| **StringUtils** | Utilitário para manipulação de strings e conversão para JSON |

---

## 3. Tecnologias Utilizadas

- **Java** (versão não especificada no código)
- **Spring Framework** (configuração XML, beans, dependency injection)
- **Spring AMQP / RabbitMQ** (versão 1.2.0.M1) - mensageria
- **BV Sistemas Framework Batch** (framework proprietário para jobs batch)
- **Jackson** (versão 2.12.7) - serialização/deserialização JSON
- **Apache Commons Logging / Log4j** - logging
- **Maven** - gerenciamento de dependências e build
- **JUnit / Mockito** - testes unitários

---

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch que não expõe endpoints REST.

---

## 5. Principais Regras de Negócio

1. **Agrupamento de Registros**: O sistema agrupa registros TCR relacionados, iniciando sempre por um TCR0 (principal) seguido de seus complementares (TCR1, TCR2, TCR5, TCR7)

2. **Tipos de Transação**: Identifica e classifica transações em:
   - TC05/TC06/TC07: Compras, Voucher e Saques (código 0100)
   - TC25/TC26/TC27: Estornos de Compra, Voucher e Saque (código 0400)

3. **Tratamento de Fee**: Se não houver registro TCR5 (fee), cria um registro padrão com valor zero e tipo "SEM_TCR5"

4. **Formatação de Valores**: Converte valores monetários de formato posicional para BigDecimal com 2 casas decimais

5. **Formatação de Data**: Adiciona o ano correto à data da transação (considera ano anterior se mês da transação for maior que mês atual)

6. **Mascaramento de Cartão**: Processa número do cartão mascarado ou tenta extrair quina (produto, conta, correlativo, filial, emissor)

7. **Movimentação de Arquivos**: Move arquivos processados com sucesso para pasta "processados" e arquivos com erro para pasta "erro"

8. **Tipo de Arquivo**: Identifica automaticamente como "BASEII - VISA"

---

## 6. Relação entre Entidades

**RecordConciliation** (entidade principal de saída):
- Contém dados consolidados da transação
- Possui referência textual (JSON) aos dados complementares via campo `camposComplementares`

**TcrZero** (registro principal):
- Representa uma transação completa
- Pode conter referência a **Tcr5** (registro de fee)
- Relacionamento 1:0..1 com Tcr5

**Tcr5** (registro complementar):
- Contém informações de taxa (fee) da transação
- Relacionado a um TcrZero

**DadosComplementares**:
- Estrutura auxiliar para armazenar dados complementares (cidade, país, estabelecimento, tipo fee)
- Não é persistida diretamente, mas serializada em JSON dentro de RecordConciliation

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
| Arquivos BASE* (padrão no nome) | Leitura | ItemReader / pasta `arquivo/recebidos/` | Arquivos de texto posicional contendo transações VISA Base II |
| robo.log | Gravação | Log4j / pasta `log/` | Log de execução do batch |
| statistics-{executionId}.log | Gravação | Log4j / pasta `log/` | Log de estatísticas de execução do framework BV |
| Arquivos processados | Movimentação | ItemReader / pasta `arquivo/processados/` | Arquivos movidos após processamento bem-sucedido |
| Arquivos com erro | Movimentação | ItemReader / pasta `arquivo/erro/` | Arquivos movidos quando ocorre erro no processamento |

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

---

## 11. Filas Geradas

| Nome da Fila/Exchange | Tecnologia | Classe Responsável | Breve Descrição |
|----------------------|------------|-------------------|-----------------|
| **Exchange**: events.ex.business.ccbd.registroBandeira<br>**Routing Key**: CCBD.registroBandeira | RabbitMQ | ItemWriter | Publica mensagens JSON contendo objetos RecordConciliation com dados de transações VISA processadas |

**Configurações por Ambiente:**
- **Local/Desenvolvimento**: localhost:5672 (guest/guest)
- **DES**: 10.39.216.137:5672 (usuário: _ccbd_des)
- **UAT**: 10.39.88.213:5672 (usuário: _ccbd_uat)
- **PRD**: 10.39.49.197:5672 (usuário: _ccbd_prd)

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| RabbitMQ | Mensageria | Publicação de mensagens de transações processadas para consumo por outros sistemas |

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades (Reader, Processor, Writer)
- Uso adequado de classes utilitárias
- Tratamento de exceções em pontos críticos
- Uso de enums para constantes
- Logging adequado em pontos importantes

**Pontos Negativos:**
- **Código comentado em português com caracteres mal codificados** (ex: "inv�lido", "N�o foi poss�vel")
- **Falta de tratamento robusto de erros**: alguns métodos retornam null silenciosamente em caso de erro
- **Lógica de negócio misturada com parsing**: RegistroMapper e RecordConciliationMapper têm responsabilidades sobrepostas
- **Hardcoded values**: valores como "1", "1001" para filial e emissor estão fixos no código
- **Falta de validações**: não há validação consistente dos dados de entrada
- **Uso de variável estática mutável**: FileUtils.total é static e pode causar problemas em ambientes concorrentes
- **Configurações sensíveis**: senhas em arquivos XML (mesmo que com placeholder)
- **Falta de documentação JavaDoc**: classes e métodos não possuem documentação formal
- **Testes não incluídos na análise**: não foi possível avaliar cobertura de testes

---

## 14. Observações Relevantes

1. **Framework Proprietário**: O sistema utiliza o framework BV Sistemas, que é proprietário e pode dificultar manutenção por equipes não familiarizadas

2. **Processamento Posicional**: O parsing de arquivos é baseado em posições fixas (substring), o que torna o código frágil a mudanças no layout

3. **Estratégia de Retomada**: A classe MyResumeStrategy sempre retorna `false` em `canResume()`, ou seja, o job nunca é retomado automaticamente em caso de falha

4. **Códigos de Saída Customizados**:
   - 10: Erro na leitura do arquivo
   - 20: Erro durante processamento
   - 30: Erro na inicialização da fila MQ
   - 40: Erro ao postar na fila MQ

5. **Versionamento**: Sistema está na versão 0.12.0, indicando que ainda está em desenvolvimento/evolução

6. **Dependências Desatualizadas**: Spring AMQP 1.2.0.M1 é uma versão muito antiga (milestone), recomenda-se atualização

7. **Serialização de Objetos Completos**: O campo `camposComplementares` contém o objeto TcrZero completo serializado em JSON, o que pode gerar redundância de dados

8. **Ausência de Criptografia**: Dados sensíveis como número de cartão (mesmo mascarado) são transmitidos sem criptografia adicional