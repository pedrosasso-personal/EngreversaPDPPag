# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java responsável pela geração de arquivos de Welcome Kit para gráfica. O sistema busca contratos elegíveis no banco de dados, gera um arquivo texto delimitado por ponto-e-vírgula contendo informações de boletos/carnês e dados de seguros contratados, atualiza o status dos contratos processados e registra histórico no sistema SAC. O processamento pode ser executado em modo normal ou reprocessamento, recebendo como parâmetros a data de execução e flag de reprocessamento.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê parâmetros de entrada (data de execução e flag de reprocessamento), busca contratos elegíveis para o Welcome Kit através da stored procedure e prepara a unidade de trabalho para processamento |
| **ItemProcessor** | Cria o arquivo físico de saída (formato DGWKIT{ddMM}01.txt), processa cada contrato gerando linhas formatadas com dados de boleto e seguros, trata erros de geração |
| **ItemWriter** | Atualiza o status dos contratos processados (flag FlAtivo='N' na TbContratoExperienciaDfrna) e insere mensagem de histórico no sistema de cobrança |
| **ArquivoGraficaBusiness** | Contém a lógica de negócio para carregar contratos e gerar as linhas do arquivo, diferenciando entre carnê normal e carnê digital |
| **ArquivoGraficaWelcomeKitDAO** | Executa a stored procedure PrGerarWelcomekitGrafica para buscar contratos elegíveis |
| **ContratoExperienciaDao** | Atualiza o status do contrato de experiência após processamento |
| **HistoricoDAO** | Insere registro de histórico através da stored procedure PrIncluirHistoricoCob |
| **DatabaseConnection** | Gerencia conexões transacionais e não-transacionais com o banco de dados |
| **ContratoWelcomeKitVO** | Value Object contendo todos os dados de um contrato para geração do Welcome Kit |
| **ArquivoGraficaUtil** | Utilitários para formatação de dados (datas, valores, remoção de acentos, formatação CNPJ) |

---

## 3. Tecnologias Utilizadas

- **Java** (versão não especificada no código)
- **Maven** (gerenciamento de dependências e build)
- **BV Framework Batch** (framework proprietário para processamento batch)
- **Spring Framework** (injeção de dependências e configuração)
- **Bitronix** (gerenciador de transações JTA)
- **JDBC/JTDS** (conectividade com banco de dados Sybase)
- **Log4j** (logging)
- **JUnit** (testes unitários)

---

## 4. Principais Endpoints REST

não se aplica

---

## 5. Principais Regras de Negócio

- Busca contratos elegíveis através de stored procedure considerando data de execução e flag de reprocessamento
- Gera arquivo com nome padrão DGWKIT{ddMM}01.txt no diretório "arquivos/"
- Diferencia geração de linha entre carnê normal e carnê digital (campo stControleRemessa = 'G')
- Para carnê digital, diversos campos são preenchidos com espaços em branco
- Arquivo possui 62 campos delimitados por ponto-e-vírgula, incluindo dados de boleto, endereço do pagador e múltiplos produtos de seguro (campos seguro_65 a seguro_117)
- Contratos com dados incompletos (contendo "null") são excluídos do arquivo e listados no log
- Após geração bem-sucedida, atualiza flag FlAtivo='N' na TbContratoExperienciaDfrna
- Insere mensagem "Emissão de 1a. via de carne, Welcome Kit enviado grafica" no histórico do contrato
- Remove acentos de todos os campos texto antes de gravar no arquivo
- Formata CNPJ da empresa no padrão ###.###.###/####-##
- Calcula valores de mora e multa para inclusão no arquivo
- Valida presença de informações obrigatórias antes de incluir contrato no arquivo

---

## 6. Relação entre Entidades

**ContratoWelcomeKitVO**: Entidade principal contendo dados do contrato, parcela, pagador, empresa, banco e seguros contratados.

**Relacionamentos identificados:**
- Contrato possui dados de Pagador (nome, CPF/CNPJ, endereço completo)
- Contrato possui dados de Empresa credora (nome, CNPJ)
- Contrato possui dados de Banco (número, nome, agência, carteira, convênio)
- Contrato possui múltiplos Seguros opcionais (20 tipos diferentes identificados por códigos)
- Contrato possui Parcela (número, valor, vencimento, nosso número)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBCARNE..PrGerarWelcomekitGrafica | stored procedure | SELECT/READ | Busca contratos elegíveis para geração do Welcome Kit com base na data de execução e flag de reprocessamento |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbContratoExperienciaDfrna | tabela | UPDATE | Atualiza flag FlAtivo='N', data de alteração e login do usuário para contratos processados |
| DBCARNE..PrIncluirHistoricoCob | stored procedure | INSERT | Insere registro de histórico informando envio do Welcome Kit para gráfica |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| DGWKIT{ddMM}01.txt | gravação | ItemProcessor / diretório "arquivos/" | Arquivo texto delimitado por ponto-e-vírgula contendo dados dos contratos para impressão do Welcome Kit pela gráfica |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

não se aplica

---

## 13. Avaliação da Qualidade do Código

**Nota:** 6/10

**Justificativa:**

**Pontos Positivos:**
- Estrutura organizada seguindo padrão batch (Reader/Processor/Writer)
- Separação de responsabilidades em camadas (DAO, Business, VO, Util)
- Uso de framework batch estruturado
- Tratamento de erros com códigos específicos (ErroEnum)
- Logging adequado para rastreabilidade

**Pontos Negativos:**
- Código com comentários em português e encoding ISO-8859-1, dificultando manutenção
- Métodos muito extensos (geraLinhaArquivoWelcomeKitNormal e geraLinhaArquivoDigital com mais de 200 linhas)
- Duplicação de código entre geração de linha normal e digital
- Uso de strings "mágicas" espalhadas pelo código (constantes não centralizadas)
- Falta de validações mais robustas em alguns pontos
- Uso de conexões estáticas no DatabaseConnection pode causar problemas de concorrência
- Tratamento genérico de exceções em alguns pontos (catch Exception)
- Falta de testes unitários abrangentes (apenas teste de integração)
- Hardcoded de valores como "ROBO_GERA_WELCOME_KI" e mensagens de histórico

---

## 14. Observações Relevantes

- Sistema executado via UC4 (agendador de jobs) recebendo parâmetros dtExecucao e reprocessar
- Arquivo gerado é consumido por sistema externo de gráfica para impressão física dos carnês
- Sistema diferencia carnê digital (stControleRemessa='G') de carnê normal, gerando linhas com campos diferentes
- Suporta 20 tipos diferentes de produtos de seguro (códigos 65, 67-71, 80, 90-94, 96-97, 100-105, 117)
- Utiliza banco de dados Sybase (DBCARNE)
- Framework batch proprietário BV Sistemas com gerenciamento de transações JTA
- Configuração de datasource via Bitronix com pool de conexões
- Logs separados: robo.log (aplicação) e statistics-{executionId}.log (métricas do batch)
- Campo 62 do arquivo indica se o contrato também está presente no arquivo de carnês do dia ('S' ou 'N')