# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java responsável por processar arquivos de remessa de débito automático. O sistema lê arquivos de entrada em formato texto posicional (padrão FEBRABAN), extrai informações de pagamentos de débito automático, valida os dados e publica mensagens em filas RabbitMQ para processamento posterior. Após o processamento bem-sucedido, os arquivos são movidos para pasta de processados; em caso de erro, são movidos para pasta de erro.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê arquivos de remessa da pasta de entrada e disponibiliza para processamento |
| **ItemProcessor** | Processa o conteúdo dos arquivos, parseando linhas conforme layout FEBRABAN (header, lotes, detalhes, trailers) |
| **ItemWriter** | Converte os dados processados em mensagens JSON e publica nas filas RabbitMQ; move arquivos processados |
| **DebitoAutomaticoMapper** | Mapeia objetos de remessa para objetos de pagamento de débito automático |
| **LeituraArquivoUtils** | Utilitário para leitura de arquivos e extração de campos posicionais |
| **MyResumeStrategy** | Estratégia de retomada do job em caso de falha |
| **PagamentoDebitoAutomatico** | Entidade principal representando um pagamento de débito automático |
| **Remessa** | Estrutura que representa o arquivo de remessa completo |
| **ValidateCPF/ValidateCNPJ** | Validadores de documentos CPF e CNPJ |

## 3. Tecnologias Utilizadas

- **Java** (versão não especificada no código)
- **Maven** (gerenciamento de dependências e build)
- **Spring Framework** (IoC/DI)
- **Spring AMQP / RabbitMQ** (mensageria)
- **BV Framework Batch** (framework proprietário para processamento batch)
- **Log4j** (logging)
- **JUnit** (testes unitários)
- **Mockito** (mocks para testes)
- **Apache Commons IO** (manipulação de arquivos)
- **Jackson** (serialização JSON)
- **Apache POI** (manipulação de arquivos Office - dependência presente)

## 4. Principais Endpoints REST

não se aplica

## 5. Principais Regras de Negócio

- Validação de CPF e CNPJ dos pagadores
- Verificação de data de vencimento: pagamentos com data de vencimento anterior à data atual são rejeitados e o arquivo é movido para pasta de erro
- Processamento de arquivos no formato FEBRABAN com estrutura de header de arquivo, header de lote, detalhes de lançamento, trailer de lote e trailer de arquivo
- Extração de dados posicionais conforme enums de posição (PosicaoHeaderArquivoEnum, PosicaoDetalheLancamentoEnum, etc.)
- Conversão de valores monetários com 2 casas decimais
- Identificação automática do tipo de pessoa (física ou jurídica) baseado na validação do CPF
- Status inicial de pagamento definido como "AGENDAMENTO"
- Tipo de produto fixo como "CARTÃO"
- Código de liquidação fixo: 1
- Código de sistema fixo: 91
- Delay de 5 segundos após o primeiro registro para evitar sobrecarga na fila

## 6. Relação entre Entidades

**Remessa** (1) → (1) **Arquivo** (nome do arquivo físico)  
**Remessa** (1) → (1) **HeaderArquivo** (cabeçalho do arquivo)  
**Remessa** (1) → (N) **Lotes** (lotes de pagamentos)  
**Remessa** (1) → (1) **TrailerArquivo** (rodapé do arquivo)  

**Lotes** (1) → (1) **HeaderLote** (cabeçalho do lote)  
**Lotes** (1) → (N) **DetalheLancamento** (detalhes dos lançamentos)  
**Lotes** (1) → (1) **TrailerLote** (rodapé do lote)  

**PagamentoDebitoAutomatico** (1) → (1) **PessoaPagamentoDebitoAutomatico** (dados do pagador)  
**PagamentoDebitoAutomatico** (1) → (1) **ConvenioDebitoAutomatico** (dados do convênio)  
**PagamentoDebitoAutomatico** (1) → (1) **StatusPagamentoDebitoAutomatico** (status do pagamento)  
**PagamentoDebitoAutomatico** (1) → (1) **ArquivoDebitoAutomatico** (metadados do arquivo)  

**ConvenioDebitoAutomatico** (1) → (1) **TipoProdutoDebitoAutomatico** (tipo de produto)

## 7. Estruturas de Banco de Dados Lidas

não se aplica

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| Arquivos de remessa (padrão: *.OUT) | Leitura | ItemReader / LeituraArquivoUtils | Arquivos de entrada contendo dados de débito automático no formato FEBRABAN |
| statistics-${executionId}.log | Gravação | BvDailyRollingFileAppender (Log4j) | Logs de estatísticas de execução do batch |
| robo.log | Gravação | RollingFileAppender (Log4j) | Logs gerais da aplicação |

**Estrutura de Diretórios:**
- `arquivo/recebidos/` - Pasta de entrada para arquivos a processar
- `arquivo/processados/` - Pasta de destino para arquivos processados com sucesso
- `arquivo/erro/` - Pasta de destino para arquivos com erro no processamento

## 10. Filas Lidas

não se aplica

## 11. Filas Geradas

| Nome da Fila | Exchange | Routing Key | Descrição |
|--------------|----------|-------------|-----------|
| Fila de agendamento de pagamento | ex.ccbd.debito.automatico | agendar.pagamento | Fila principal para publicação de pagamentos de débito automático |
| Fila de monitoramento | ex.ccbd.debito.automatico | monitor.agendamento.pagamento | Fila para monitoramento dos agendamentos de pagamento |

**Configuração RabbitMQ:**
- DES: host 10.39.216.137, porta 5672, usuário _ccbd_des
- UAT: host 10.39.88.213, porta 5672, usuário _ccbd_uat
- PRD: host 10.39.49.197, porta 5672, usuário _ccbd_prd

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| RabbitMQ | Mensageria | Publicação de mensagens de pagamento para processamento assíncrono |

## 13. Avaliação da Qualidade do Código

**Nota:** 6/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades entre Reader, Processor e Writer
- Uso de enums para constantes e posições de arquivo
- Validação de CPF/CNPJ implementada
- Tratamento de exceções com códigos de saída específicos
- Uso de utilitários para operações comuns
- Logs informativos em pontos estratégicos

**Pontos Negativos:**
- Código com comentários em português misturado com código em inglês
- Presença de código comentado (ex: convenio.setCdConvenioDebitoAutomatico)
- Hardcoded delay de 5 segundos no ItemWriter sem justificativa clara
- Falta de tratamento específico para erro ao enviar para fila de monitoramento (apenas log)
- Uso de índices mágicos (remessa.getLotes().size() -1)
- Falta de validações mais robustas nos dados extraídos
- Métodos utilitários retornando null em vez de Optional
- Exceções genéricas sendo lançadas em alguns pontos
- Falta de testes unitários abrangentes (apenas um teste de integração)
- Configurações de ambiente (senhas) expostas nos XMLs

## 14. Observações Relevantes

- O sistema utiliza um framework batch proprietário (BV Framework Batch) da BV Sistemas
- O processamento é configurado com commit interval de 10.000 registros
- Existe um mecanismo de retry desabilitado (MyResumeStrategy retorna false)
- O sistema espera receber o nome do arquivo como parâmetro obrigatório na execução
- Há validação de data de vencimento: arquivos com vencimento passado são rejeitados
- O sistema suporta múltiplos ambientes (DES, UAT, PRD) com configurações separadas
- Formato de arquivo esperado: layout FEBRABAN com registros posicionais de 240 caracteres
- O sistema não realiza operações de banco de dados, apenas leitura de arquivos e publicação em filas
- Existe uma dependência do Apache POI que não parece ser utilizada no código analisado