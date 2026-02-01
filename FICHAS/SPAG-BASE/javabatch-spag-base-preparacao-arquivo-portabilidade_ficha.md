# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java responsável pela preparação de arquivos de portabilidade de contas salário. O sistema realiza operações de leitura, renomeação, compressão/descompressão e movimentação de arquivos XML relacionados ao processo de portabilidade bancária, seguindo padrões do CIP (Câmara Interbancária de Pagamentos). O processamento é executado através de um job batch que recebe arquivos, aplica transformações conforme parâmetros configurados e os disponibiliza em diretórios específicos.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê o arquivo de entrada do diretório `/arquivo/recebido/` e valida sua existência |
| **ItemProcessor** | Processa o arquivo (atualmente apenas repassa o arquivo sem transformações) |
| **ItemWriter** | Executa as operações de renomeação, compressão/descompressão e movimentação dos arquivos |
| **MyResumeStrategy** | Estratégia de retomada do job em caso de falha (atualmente não permite retomada) |
| **TipoArquivo** | Enum que define os tipos de arquivos suportados (APCS101, APCS105, etc.) e suas regras de nomenclatura |
| **FileUtils** | Utilitário para operações de compressão/descompressão GZIP e movimentação de arquivos |
| **StringUtils** | Utilitário para manipulação de strings e extração de tipo de arquivo |
| **ApplicationUtils** | Utilitário para fechamento seguro de streams |
| **PortabilidadeException** | Exceção customizada com código de saída para erros do sistema |
| **Constants** | Constantes do sistema (ISPBs, complementos de arquivo) |
| **ErrorConstants** | Códigos de erro padronizados do sistema |

## 3. Tecnologias Utilizadas

- **Java** (linguagem principal)
- **Maven** (gerenciamento de dependências e build)
- **Spring Framework** (configuração e injeção de dependências via XML)
- **BV Framework Batch** (framework proprietário para processamento batch)
- **Log4j** (logging)
- **JUnit 4** (testes unitários)
- **Mockito** (mocks para testes)
- **Apache Commons IO** (utilitários de I/O)
- **GZIP** (compressão/descompressão de arquivos)

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch executado via linha de comando, não possui endpoints REST.

## 5. Principais Regras de Negócio

1. **Validação de Tipo de Arquivo**: O sistema valida se o arquivo recebido corresponde a um dos tipos suportados (APCS101, APCS105, APCS104, APCS108, APCS109 e suas variações RET/ERR/PRO)

2. **Renomeação de Arquivos**: Quando habilitado (parâmetro `renomearArquivo=1`), adiciona complementos específicos ao nome do arquivo:
   - Arquivos APCS101 e APCS105: recebem complemento de criptografia (`#02#46#000#59588111#02992335#CTC.rrc`)
   - Demais arquivos: recebem complemento de descriptografia (`#02#47#000#02992335#59588111#CTC.rrc`)

3. **Compressão/Descompressão**: 
   - `compressaoArquivo=1`: Comprime o arquivo em formato GZIP
   - `compressaoArquivo=0`: Descomprime arquivo GZIP
   - Valida se arquivo já está comprimido/descomprimido antes de processar

4. **Movimentação de Arquivos**: Move arquivos processados para diretórios específicos:
   - `/arquivo/renomeado/`: arquivos apenas renomeados
   - `/arquivo/compactado/`: arquivos comprimidos
   - `/arquivo/descompactado/`: arquivos descomprimidos

5. **Tratamento de Erros**: Sistema utiliza códigos de erro padronizados (10-16) para diferentes situações de falha

6. **ISPBs Envolvidos**: 
   - ISPB Votorantim: 59588111
   - ISPB CIP: 02992335

## 6. Relação entre Entidades

O sistema trabalha com arquivos XML de portabilidade que seguem o schema APCS (Arranjo de Pagamentos da Câmara Interbancária). Não há entidades de banco de dados, apenas manipulação de arquivos físicos.

**Estrutura de Processamento:**
- **File (Arquivo de Entrada)** → lido pelo ItemReader
- **File (Arquivo Processado)** → processado pelo ItemProcessor (passthrough)
- **File (Arquivo de Saída)** → gravado pelo ItemWriter em diretórios específicos

**Tipos de Arquivo (TipoArquivo enum):**
- APCS101: Portabilidade de conta salário (envio)
- APCS105: Portabilidade de conta salário (envio)
- APCS101RET: Retorno de portabilidade
- APCS101ERR: Erro de portabilidade
- APCS104, APCS108, APCS109: Outros tipos de mensagens de portabilidade

## 7. Estruturas de Banco de Dados Lidas

Não se aplica. O sistema não acessa banco de dados.

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema não acessa banco de dados.

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| APCS101_*.xml | Leitura | ItemReader - `/arquivo/recebido/` | Arquivo XML de portabilidade de conta salário (envio) |
| APCS105_*.xml | Leitura | ItemReader - `/arquivo/recebido/` | Arquivo XML de portabilidade de conta salário (envio) |
| APCS101_*_RET | Leitura | ItemReader - `/arquivo/recebido/` | Arquivo de retorno de portabilidade |
| APCS101_*_ERR | Leitura | ItemReader - `/arquivo/recebido/` | Arquivo de erro de portabilidade |
| APCS104_*, APCS108_*, APCS109_* | Leitura | ItemReader - `/arquivo/recebido/` | Outros tipos de arquivos de portabilidade |
| *#02#46#000#*.rrc | Gravação | ItemWriter - `/arquivo/renomeado/` | Arquivo renomeado com complemento de criptografia |
| *#02#47#000#*.rrc | Gravação | ItemWriter - `/arquivo/renomeado/` | Arquivo renomeado com complemento de descriptografia |
| *.gz | Gravação | FileUtils - `/arquivo/compactado/` | Arquivo comprimido em formato GZIP |
| Arquivo descomprimido | Gravação | FileUtils - `/arquivo/descompactado/` | Arquivo descomprimido de GZIP |
| robo.log | Gravação | Log4j - `/log/` | Log de execução do sistema |
| statistics-*.log | Gravação | Log4j - `/log/` | Log de estatísticas do framework batch |

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas.

## 12. Integrações Externas

Não se aplica. O sistema não possui integrações com APIs ou sistemas externos. Opera exclusivamente com arquivos locais do sistema de arquivos.

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades entre as classes (Reader, Processor, Writer)
- Uso adequado de enums para tipos de arquivo
- Tratamento de exceções customizado com códigos de erro
- Cobertura de testes unitários presente
- Uso de utilitários para operações comuns
- Logging adequado em pontos críticos
- Documentação através de comentários em arquivos de configuração

**Pontos de Melhoria:**
- ItemProcessor não realiza nenhum processamento (apenas passthrough), questionável sua necessidade
- Uso de recursos via `getClass().getResource()` pode causar problemas em ambientes de produção
- Hardcoded de paths relativos (`/arquivo/recebido/`, etc.)
- Falta de validação mais robusta dos parâmetros de entrada
- MyResumeStrategy não implementa lógica de retomada (apenas retorna false)
- Mistura de português e inglês nos nomes de variáveis e métodos
- Falta de constantes para valores mágicos (ex: "1", "0" para flags booleanos)
- Dependência de framework proprietário (BV Framework) dificulta portabilidade
- Configuração via XML (Spring) ao invés de anotações (padrão mais moderno)
- Falta de validação do schema XML dos arquivos APCS

## 14. Observações Relevantes

1. **Framework Proprietário**: O sistema utiliza o BV Framework Batch, um framework proprietário da BV Sistemas, o que pode dificultar manutenção e evolução fora desse ecossistema.

2. **Execução**: O sistema pode ser executado via scripts shell (.sh) ou batch (.bat), recebendo três parâmetros:
   - Nome do arquivo
   - Flag de renomeação (0 ou 1)
   - Flag de compressão (0=descomprimir, 1=comprimir, vazio=não processar)

3. **Padrão CIP**: Os arquivos seguem o padrão APCS (Arranjo de Pagamentos da Câmara Interbancária) para portabilidade de contas salário.

4. **Versionamento**: Sistema na versão 0.2.0, indicando estar em fase inicial de desenvolvimento.

5. **Estrutura Multi-módulo**: Projeto Maven dividido em módulos `core` (lógica) e `dist` (distribuição).

6. **Ambiente de Testes**: Possui estrutura completa de testes com arquivos de exemplo e backups para recuperação após testes.

7. **Logs Bitronix**: Scripts removem arquivos de log do Bitronix (gerenciador de transações), embora não haja evidência de uso de transações no código.

8. **Configuração de Memória**: JVM configurada com 512MB de heap (Xms e Xmx).

9. **Jenkins Integration**: Arquivo `jenkins.properties` indica integração com pipeline de CI/CD, com deploy em QA desabilitado.