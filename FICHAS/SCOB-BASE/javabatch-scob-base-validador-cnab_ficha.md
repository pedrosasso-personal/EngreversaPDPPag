# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java desenvolvido com Spring Batch para validação e processamento de arquivos CNAB (Centro Nacional de Automação Bancária) no contexto de cobrança bancária. O sistema realiza a leitura de arquivos de remessa nos formatos CNAB 240 e CNAB 400, executa validações físicas e lógicas, processa títulos de cobrança e instruções, e integra-se com diversos sistemas através de filas IBM MQ. O processamento inclui validação de clientes, convênios, geração de contratos de cobrança e movimentação de arquivos entre diretórios conforme o resultado do processamento.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Leitura e orquestração do processamento de arquivos CNAB. Gerencia o fluxo principal, consulta pré-processamento, validação de clientes e envio de linhas para validação |
| **ItemWriter** | Componente de escrita do Spring Batch (implementação vazia no código fornecido) |
| **ItemProcessor** | Processamento de itens do Spring Batch (implementação simples de passagem) |
| **MantemPreStage** | Thread responsável por manter arquivos temporários (PreStage), validar registros, inserir títulos no banco e gerenciar o ciclo de vida do processamento |
| **EnviaPreStage** | Thread que envia arquivos PreStage para validação lógica (GRID) |
| **RetornoValidacaoLogica** | Thread que processa retornos da validação lógica |
| **InsereTituloSaida** | Thread que gerencia o retorno da inserção de títulos |
| **ControleMensagensErroEmail** | Thread que controla envio de emails de erro |
| **JMSRepository** | Repositório para comunicação com filas IBM MQ |
| **MQConnectionProvider** | Provedor de conexões IBM MQ |
| **ControleProcessamento** | Controla o estado e progresso do processamento de arquivos |
| **FileUtil** | Utilitários para manipulação de arquivos CNAB |
| **CnabUtil** | Utilitários específicos para processamento CNAB |

## 3. Tecnologias Utilizadas

- **Java 7** (JDK 7)
- **Spring Batch** (framework de processamento batch)
- **Spring Framework** (injeção de dependências e configuração)
- **IBM MQ** (WebSphere MQ) - Mensageria
- **Maven** - Gerenciamento de dependências e build
- **Log4j** - Logging
- **JMS** (Java Message Service)
- **GSON** - Serialização/deserialização JSON
- **JSON Simple** - Manipulação JSON
- **JUnit** - Testes (escopo test)
- **BV Framework Batch** (framework proprietário versão 13.0.4)
- **BV JDBC Driver** (driver proprietário versão 15.0.0)

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch que não expõe endpoints REST.

## 5. Principais Regras de Negócio

- Validação de arquivos CNAB 240 e 400 (validação física de estrutura)
- Identificação e validação de CPF/CNPJ de clientes e cedentes
- Validação de convênios bancários
- Detecção de títulos duplicados (por chave composta: seu número, data vencimento, valor nominal, CPF/CNPJ sacado e cedente)
- Detecção de duplicidade de nosso número + convênio
- Validação de duplicidade de duplicatas
- Separação de títulos e instruções de cobrança
- Processamento diferenciado para cobrança escritural e cobrança direta
- Validação de processo piloto (ASIS, TOBE, AMBOS) para determinar fluxo de processamento
- Geração automática de contratos de cobrança quando necessário
- Quebra de arquivos em lotes para processamento (configurável via parâmetro)
- Movimentação de arquivos entre diretórios (recebe, erro, histórico, recebeAsis) conforme resultado
- Validação lógica de regras de negócio (multa, mora, desconto, protesto, etc.)
- Controle de flags de processamento
- Envio de emails em caso de erros

## 6. Relação entre Entidades

**Principais entidades e relacionamentos:**

- **ArquivoCnab**: Representa o arquivo CNAB principal
  - Possui lista de **ArquivoCnabLote** (1:N)
  
- **DadosArquivoCnab**: Representa uma linha do arquivo
  - Contém **ClienteConvenioCnab** (N:1)
  - Contém lista de **LinhaDetalheCnab** (1:N)
  - Referencia **ConsultaLayout** (N:1)
  
- **ClienteConvenioCnab**: Dados do cliente e convênio
  - Contém lista de **ConvenioCnab** (1:N)
  - Contém **ProcessoPiloto** (1:1)
  
- **RegistroTitulo**: Representa um título de cobrança
  - Contém **DadosPagador** (1:1)
  - Contém listas de **MensagemTitulo** (1:N)
  - Contém **VerificaCancelamentoSustacao** (1:1)
  - Contém **VerificaInstrucaoProtesto** (1:1)

- **DadosControleEnvio**: Controla envio de mensagens por arquivo
  - Referencia **File** (arquivo físico)
  - Contém **LogProcessamento**

## 7. Estruturas de Banco de Dados Lidas

Não se aplica. O sistema não acessa diretamente o banco de dados. Toda comunicação é feita através de filas IBM MQ que invocam serviços que acessam o banco.

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema não atualiza diretamente o banco de dados. As atualizações são realizadas por serviços invocados através de filas IBM MQ.

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| Arquivos CNAB (.rem) | Leitura | ItemReader / FileUtil | Arquivos de remessa CNAB 240 ou 400 contendo títulos e instruções de cobrança |
| Arquivos PreStage (.json) | Gravação | MantemPreStage / DadosControlePreStage | Arquivos temporários JSON com dados validados para processamento posterior |
| robo.log | Gravação | Log4j (RollingFileAppender) | Log de execução do robô |
| statistics-{executionId}.log | Gravação | Log4j (BvDailyRollingFileAppender) | Log de estatísticas de execução |

**Diretórios utilizados:**
- `/remessa` - Arquivos de entrada originais
- `/recebe` - Arquivos movidos para processamento
- `/recebeAsis` - Arquivos para processamento pelo sistema legado (ASIS)
- `/historico` - Arquivos processados com sucesso
- `/erro` - Arquivos com erro de processamento
- `validadorCnab/PreStage/` - Arquivos temporários de processamento

## 10. Filas Lidas

- **QL.SCOB.BATCH_CNAB_PARAM.RSP** - Resposta de consulta de pré-processamento
- **QL.SCOB.BATCH_CNAB_VALIDA_REG.RSP** - Resposta de validação de registro
- **QL.SCOB.BATCH_CNAB_CONSULTA_CLI.RSP** - Resposta de consulta de cliente
- **QL.SCOB.BATCH_CNAB_SALVA_ARQ.RSP** - Resposta de salvamento de arquivo
- **QL.SCOB.BATCH_CNAB_VALIDACAO_LOGICA.RSP** - Resposta de validação lógica (GRID)
- **QL.SCOB.BATCH_CNAB_SALVA_TITU.RSP** - Resposta de inserção de títulos
- **QL.SCOB.BATCH_CNAB_GERA_CONTRATO.RSP** - Resposta de geração de contrato
- **QL.SCOB.BATCH_CNAB_SALVA_FLGPROC.RSP** - Resposta de atualização de flag de processo
- **QL.SCOB.BATCH_CNAB_REJEITA_ARQ.RSP** - Resposta de rejeição de arquivo
- **QL.SCOB.BATCH_CNAB_DELETA_ARQ_REJEITADO.RSP** - Resposta de exclusão de arquivo rejeitado

## 11. Filas Geradas

- **QL.SCOB.BATCH_CNAB_INI.INT** - Registro de início de processo
- **QL.SCOB.BATCH_CNAB_FIM.INT** - Registro de fim de processo
- **QL.SCOB.BATCH_CNAB_PARAM.INT** - Consulta de pré-processamento
- **QL.SCOB.BATCH_CNAB_VALIDA_REG.INT** - Validação de registro (física)
- **QL.SCOB.BATCH_CNAB_CONSULTA_CLI.INT** - Consulta de cliente
- **QL.SCOB.BATCH_CNAB_SALVA_ARQ.INT** - Salvamento de arquivo
- **QL.SCOB.BATCH_CNAB_VALIDACAO_LOGICA.INT** - Validação lógica (GRID)
- **QL.SCOB.BATCH_CNAB_SALVA_TITU.INT** - Inserção de títulos
- **QL.SCOB.BATCH_CNAB_GERA_CONTRATO.INT** - Geração de contrato de cobrança
- **QL.SCOB.BATCH_CNAB_SALVA_FLGPROC.INT** - Atualização de flag de processo
- **QL.SCOB.BATCH_CNAB_REJEITA_ARQ.INT** - Rejeição de arquivo
- **QL.SCOB.BATCH_ENVIA_EMAIL_ARQ.INT** - Envio de email de erro
- **QL.SCOB.BATCH_CNAB_DELETA_ARQ_REJEITADO.INT** - Exclusão de arquivo rejeitado

## 12. Integrações Externas

- **IBM MQ (WebSphere MQ)** - Middleware de mensageria para comunicação assíncrona com serviços de backend. Todas as operações de negócio (consultas, validações, persistência) são realizadas através de filas MQ.
- **Sistema de Cobrança (Backend)** - Serviços acessados via MQ para validação de clientes, convênios, geração de contratos, inserção de títulos e validações lógicas.
- **Sistema de Email** - Envio de notificações de erro via fila MQ.
- **Sistema Legado ASIS** - Arquivos que não atendem critérios do processo piloto TOBE são redirecionados para processamento pelo sistema legado.

## 13. Avaliação da Qualidade do Código

**Nota: 5/10**

**Justificativa:**

**Pontos Positivos:**
- Uso de padrões de projeto (Strategy, Repository)
- Separação de responsabilidades em classes específicas
- Uso de enums para constantes e tipos
- Implementação de threads para processamento paralelo
- Tratamento de exceções em pontos críticos
- Logging estruturado

**Pontos Negativos:**
- **Complexidade excessiva**: A classe `ItemReader` possui mais de 800 linhas com múltiplas responsabilidades
- **Acoplamento alto**: Forte dependência de IBM MQ e classes específicas do framework BV
- **Código comentado**: Diversos trechos de código comentado não removidos
- **Falta de documentação**: Ausência de JavaDoc na maioria dos métodos
- **Tratamento de exceções genérico**: Muitos blocos catch com `Exception` genérica
- **Variáveis de instância excessivas**: Classes com muitos atributos dificultando manutenção
- **Lógica de negócio misturada**: Validações e processamento misturados com controle de fluxo
- **Testes ausentes**: Não há testes unitários implementados (apenas estrutura)
- **Hardcoded values**: Alguns valores fixos no código (ex: TAMANHO_LOTE = 100)
- **Nomenclatura inconsistente**: Mistura de português e inglês
- **Threads sem gerenciamento adequado**: Uso de threads sem pool ou controle robusto de ciclo de vida

## 14. Observações Relevantes

- O sistema implementa um processo piloto com três modos: ASIS (legado), TOBE (novo) e AMBOS (convivência)
- Arquivos são processados em lotes configuráveis para otimizar performance
- Existe controle de duplicidade em três níveis: título completo, nosso número + convênio, e duplicata
- O sistema suporta processamento de instruções de cobrança além de títulos (configurável)
- Implementa mecanismo de retry e timeout para comunicação com filas MQ (5 minutos padrão)
- Utiliza arquivos temporários (PreStage) em formato JSON para processamento intermediário
- Possui controle de eventos e métricas de processamento (tempo de execução, quantidade de mensagens)
- Sistema preparado para processar arquivos de múltiplas VANs (Value Added Network)
- Implementa validação de CPF/CNPJ com algoritmo de dígito verificador
- Código contém referências a encoding UTF-8 para tratamento de caracteres especiais
- Versão atual: 0.29.3
- Dependência de framework proprietário BV (versões 13.x e 15.x)