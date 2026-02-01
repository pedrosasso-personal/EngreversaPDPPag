# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de processamento batch desenvolvido em Java para leitura, processamento e conciliação de registros de transações de débito da bandeira de cartões (CCBD - Cartão de Crédito Banco Digital). O sistema lê arquivos de texto posicionais contendo transações (tipo T112), processa os registros de detalhes, transforma os dados em objetos de conciliação e publica as informações em filas RabbitMQ para processamento posterior. Após o processamento bem-sucedido, os arquivos são movidos para diretório de processados.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê arquivos de texto posicionais do diretório de recebidos, filtra registros do tipo "1" (detalhes) e gerencia movimentação de arquivos processados |
| **ItemProcessor** | Processa cada linha do arquivo, convertendo strings posicionais em objetos DetalhesRegistro e posteriormente em RecordConciliation |
| **ItemWriter** | Envia objetos RecordConciliation para fila RabbitMQ (exchange: events.ex.business.ccbd.registroBandeira) |
| **DetalhesRegistro** | Entidade de domínio que representa um registro de detalhe do arquivo posicional com todos os campos da transação |
| **FileProcessorRecord** | Wrapper que encapsula DetalhesRegistro para processamento |
| **RecordConciliation** | Objeto de negócio final contendo dados consolidados da transação para envio à fila |
| **RegistroMapper** | Mapeia strings posicionais para objetos DetalhesRegistro através de parsing de posições fixas |
| **RecordConciliationMapper** | Converte FileProcessorRecord em RecordConciliation, aplicando regras de negócio e formatações |
| **MyResumeStrategy** | Estratégia de retomada do job batch em caso de falhas |
| **TransactionType** | Enum que identifica o tipo de transação (PRESENTMENT ou CHARGEBACK) baseado em MTI, function code e processing code |
| **TipoRegistro** | Enum que define os tipos de registro do arquivo (Header=0, Detalhes=1, Trailer=9) |

---

## 3. Tecnologias Utilizadas

- **Java** (linguagem principal)
- **Spring Batch** (framework de processamento batch)
- **Spring AMQP / RabbitMQ** (mensageria - versão 1.2.0.M1)
- **Maven** (gerenciamento de dependências e build)
- **BV Framework Batch** (framework proprietário Banco Votorantim para jobs batch)
- **Jackson** (serialização JSON - versão 2.12.7)
- **Apache POI** (manipulação de arquivos - versão 4.1.0)
- **Log4j** (logging)
- **JUnit e Mockito** (testes unitários)

---

## 4. Principais Endpoints REST

não se aplica

---

## 5. Principais Regras de Negócio

1. **Filtragem de Registros**: Apenas registros do tipo "1" (detalhes) são processados; registros de header (0) e trailer (9) são ignorados
2. **Identificação de Tipo de Transação**: Determina se a transação é PRESENTMENT (0100) ou CHARGEBACK (0400) baseado nos campos MTI (1240), function code (200) e processing code
3. **Conversão de Valores Monetários**: Valores são convertidos de string para BigDecimal com 2 casas decimais, dividindo por 100 (valores vêm sem separador decimal)
4. **Formatação de Data**: Converte data/hora de formato yyMMddHHmmss para yyyy-MM-dd HH:mm:ss
5. **Extração de Quina do Cartão**: Tenta extrair código do produto (2 dígitos), número da conta (9 dígitos) e correlativo (5 dígitos) do cartão mascarado; em caso de falha, mantém o cartão mascarado completo
6. **Movimentação de Arquivos**: Arquivos processados com sucesso são movidos para diretório "processados"; arquivos com erro permanecem em "recebidos"
7. **Campos Complementares**: Todos os campos do DetalhesRegistro são serializados em JSON e armazenados no campo camposComplementares do RecordConciliation
8. **Tipo de Arquivo Fixo**: Todas as transações são marcadas com tipo de arquivo "T112"

---

## 6. Relação entre Entidades

**DetalhesRegistro** → representa um registro de detalhe do arquivo posicional (1:1 com linha do arquivo tipo "1")

**FileProcessorRecord** → encapsula DetalhesRegistro (relacionamento de composição 1:1)

**RecordConciliation** → objeto final de negócio derivado de FileProcessorRecord (relacionamento de transformação 1:1)

**Fluxo de Transformação**:
```
String (linha arquivo) 
  → DetalhesRegistro (via RegistroMapper) 
  → FileProcessorRecord 
  → RecordConciliation (via RecordConciliationMapper) 
  → Fila RabbitMQ
```

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
| T112*.txt | Leitura | ItemReader (diretório: arquivo/recebidos/) | Arquivos de transações de débito em formato posicional com registros de header, detalhes e trailer |
| Arquivos processados | Gravação (movimentação) | ItemReader (diretório: arquivo/processados/) | Arquivos movidos após processamento bem-sucedido |
| Arquivos com erro | Gravação (movimentação) | ItemReader (diretório: arquivo/erro/) | Arquivos movidos em caso de erro no processamento |
| log4j.xml | Leitura | Configuração de logging | Arquivo de configuração de logs da aplicação |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

**Fila RabbitMQ:**
- **Exchange**: events.ex.business.ccbd.registroBandeira
- **Routing Key**: CCBD.registroBandeira
- **Conteúdo**: Objetos RecordConciliation serializados em JSON
- **Classe Responsável**: ItemWriter
- **Configuração por Ambiente**:
  - **DES**: Host 10.39.216.137, porta 5672, usuário _ccbd_des
  - **UAT**: Host 10.39.88.213, porta 5672, usuário _ccbd_uat
  - **PRD**: Host 10.39.49.197, porta 5672, usuário _ccbd_prd

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **RabbitMQ** | Mensageria | Publicação de mensagens de conciliação de transações para consumo por outros sistemas |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades entre Reader, Processor e Writer (padrão Spring Batch)
- Uso adequado de classes utilitárias (DateUtils, MathUtils, StringUtils, FileUtils)
- Tratamento de exceções com códigos de saída customizados
- Uso de enums para constantes (TipoRegistro, TransactionType)
- Presença de testes unitários
- Construtores privados em classes utilitárias para evitar instanciação

**Pontos de Melhoria:**
- Parsing posicional hardcoded com muitos números mágicos (posições fixas espalhadas pelo código)
- Método `paraDetalheRegistroPosicao247a500` quebra o princípio de responsabilidade única
- Falta de documentação JavaDoc nas classes e métodos
- Tratamento de exceções genérico em alguns pontos (catch Exception)
- Uso de versões antigas de bibliotecas (Spring AMQP 1.2.0.M1, Jackson 2.5.1 no properties mas 2.12.7 nas dependências)
- Mensagens de log em português e inglês misturados
- Caracteres especiais com encoding incorreto em alguns comentários
- Falta de validações mais robustas nos dados de entrada
- Código de conversão de "quina" do cartão com try-catch genérico que mascara problemas

---

## 14. Observações Relevantes

1. **Formato de Arquivo**: O sistema processa arquivos posicionais com layout fixo de 500 caracteres por linha, seguindo padrão de mensageria ISO 8583 (campos MTI, processing code, etc.)

2. **Parâmetro Obrigatório**: O job requer o parâmetro "nomeArquivo" para execução, indicando qual arquivo processar

3. **Códigos de Saída Customizados**:
   - 10: Erro ao encontrar arquivo
   - 20: Erro ao inicializar fila
   - 30: Erro ao enviar mensagem para fila
   - 40: Erro na leitura do arquivo

4. **Ambientes**: Sistema configurado para 3 ambientes (DES, UAT, PRD) com configurações específicas de RabbitMQ em arquivos XML separados

5. **Segurança**: Senhas das filas RabbitMQ estão parametrizadas com placeholder {{password}} nos XMLs de configuração

6. **Framework Proprietário**: Utiliza framework batch proprietário do Banco Votorantim (bv-framework-batch), o que pode dificultar manutenção por equipes externas

7. **Processamento Síncrono**: Cada registro é processado e enviado individualmente para a fila (não há processamento em lote)

8. **Resiliência Limitada**: A estratégia de retomada (MyResumeStrategy) sempre retorna false, não permitindo retomada automática em caso de falhas