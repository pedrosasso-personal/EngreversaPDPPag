# Ficha Técnica do Sistema

---

## 1. Descrição Geral

O sistema **javabatch-ccbd-base-debito-auto-credito-baixas** é um job batch Java desenvolvido para processar débitos automáticos e gerar arquivos de retorno (remessa) no padrão CNAB 240. O sistema busca pagamentos de débito automático agendados no banco de dados MySQL, processa as informações conforme o status de cada pagamento, e gera um arquivo de retorno formatado contendo headers, detalhes e trailers. Antes do processamento principal, o sistema finaliza automaticamente agendamentos pendentes na data de processamento, alterando seu status para "7" (finalizado/expirado). O arquivo gerado é gravado em disco no diretório `arquivo/processados/` com nomenclatura padronizada.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê os dados de pagamentos de débito automático do banco de dados MySQL através do repositório. Finaliza agendamentos pendentes antes da leitura principal. |
| **ItemProcessor** | Processa os dados lidos, mapeando-os para o formato de arquivo de remessa CNAB 240 (header arquivo, header lote, detalhes, trailer lote, trailer arquivo). |
| **ItemWriter** | Grava o arquivo de retorno formatado em disco no diretório `arquivo/processados/`. |
| **ItemMapper** | Contém métodos estáticos para mapear objetos de domínio para strings formatadas conforme layout CNAB 240. |
| **RemessaRepository / RemessaRepositoryImpl** | Interface e implementação para acesso aos dados de remessa no banco MySQL. |
| **RemessaMapper** | Mapeia ResultSet do banco de dados para objetos `RemessaPlain`. |
| **RemessaPlain** | Objeto de transferência de dados (DTO) contendo informações de pagamento formatadas. |
| **MyResumeStrategy** | Estratégia de retomada do job em caso de falha. |
| **AppUtil** | Utilitário para manipulação de datas de processamento. |
| **SQLUtil** | Utilitário para carregar queries SQL de arquivos XML. |
| **ExitCodeEnum** | Enumeração de códigos de saída do batch. |
| **StatusOcorrenciaEnum** | Enumeração de códigos de ocorrência DXC para mapeamento de status. |
| Demais classes em `model/` | Entidades de domínio representando estruturas de débito automático e layout CNAB. |

---

## 3. Tecnologias Utilizadas

- **Java** (linguagem de programação)
- **Maven** (gerenciamento de dependências e build)
- **Spring Framework** (injeção de dependências, configuração XML)
- **BV Framework Batch** (framework proprietário para jobs batch)
- **MySQL 8.0.22** (banco de dados)
- **JDBC / Spring JDBC** (acesso a dados)
- **Bitronix** (gerenciador de transações XA)
- **Log4j** (logging)
- **JUnit** (testes unitários)
- **BV Crypto** (criptografia de senhas)
- **Apache Commons Lang** (utilitários de string)

---

## 4. Principais Endpoints REST

**não se aplica** - Este é um sistema batch, não possui endpoints REST.

---

## 5. Principais Regras de Negócio

1. **Finalização de Agendamentos Pendentes**: Antes do processamento principal, todos os pagamentos com status "1" (agendado) e data de vencimento igual à data de processamento são automaticamente atualizados para status "7" (finalizado/expirado).

2. **Filtragem de Pagamentos**: Apenas pagamentos com status 3, 4, 5, 6, 7 ou 8 e tipo de produto "1" são processados.

3. **Mapeamento de Status para Códigos de Ocorrência**: Cada status de pagamento é mapeado para um código de ocorrência DXC específico:
   - Status 4 → "00" (confirmado)
   - Status 3 → "IC" (inconsistente)
   - Status 5 → "AJ" (ajuste)
   - Status 6 → "AJ" (ajuste)
   - Status 7 → "01" (erro)
   - Status 8 → "02" (erro)

4. **Cálculo de Valores para Trailer**: Apenas pagamentos com status "4" (confirmado) têm seus valores somados para o trailer do lote.

5. **Formatação de Dados**: Todos os campos numéricos são preenchidos com zeros à esquerda, campos alfanuméricos com espaços à direita, conforme especificação CNAB 240.

6. **Geração de Arquivo de Retorno**: O arquivo é gerado com nomenclatura `RECTST_BV_DEBAUT_DDMMAA_HHMMSS.RET` no diretório `arquivo/processados/`.

7. **Data de Processamento**: Pode ser informada via parâmetro `dataProcessamento` (formato yyyyMMdd) ou utiliza a data atual do sistema.

---

## 6. Relação entre Entidades

- **PagamentoDebitoAutomatico** (entidade principal)
  - Relaciona-se com **PessoaPagamentoDebitoAutomatico** (FK: cdPessoaDebitoAutomatico) - dados do debitado
  - Relaciona-se com **ArquivoDebitoAutomatico** (FK: cdArquivoDebitoAutomatico) - arquivo de origem
  - Relaciona-se com **ConvenioDebitoAutomatico** (FK: cdConvenioDebitoAutomatico) - convênio bancário
  - Relaciona-se com **StatusPagamentoDebitoAutomatico** (FK: cdStatusPagamento) - status do pagamento

- **ConvenioDebitoAutomatico**
  - Relaciona-se com **TipoProdutoDebitoAutomatico** (FK: cdTipoProdutoDebitoAutomatico)

- **RemessaPlain** (DTO) - agrega dados de múltiplas entidades para processamento

- **ListaRemessa** - wrapper contendo lista de RemessaPlain

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbPagamentoDebitoAutomatico | tabela | SELECT | Tabela principal contendo pagamentos de débito automático |
| TbPessoaDebitoAutomatico | tabela | SELECT | Dados cadastrais das pessoas (debitados) |
| TbArquivoDebitoAutomatico | tabela | SELECT | Informações sobre arquivos de remessa/retorno |
| TbConvenioDebitoAutomatico | tabela | SELECT | Convênios de débito automático com bancos |
| TbTipoProdutoDebitoAutomatico | tabela | SELECT | Tipos de produtos de débito automático |
| TbStatusPagamentoDebitoAtmto | tabela | SELECT | Status possíveis para pagamentos |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbPagamentoDebitoAutomatico | tabela | UPDATE | Atualiza status de agendamentos pendentes para "7" (finalizado) quando a data de vencimento é igual à data de processamento |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| RECTST_BV_DEBAUT_DDMMAA_HHMMSS.RET | gravação | ItemWriter / diretório `arquivo/processados/` | Arquivo de retorno CNAB 240 contendo resultado do processamento de débitos automáticos |
| RemessaRepositoryImpl-sql.xml | leitura | RemessaRepositoryImpl / SQLUtil | Arquivo XML contendo queries SQL para busca e atualização de dados |
| job-resources.xml | leitura | Spring Framework | Arquivo de configuração de recursos (datasource) por ambiente |
| job-definitions.xml | leitura | Spring Framework | Arquivo de definição do job batch e seus componentes |
| log4j.xml | leitura | Log4j | Arquivo de configuração de logging |

---

## 10. Filas Lidas

**não se aplica** - O sistema não consome mensagens de filas.

---

## 11. Filas Geradas

**não se aplica** - O sistema não publica mensagens em filas (há código comentado sugerindo integração futura com RabbitMQ, mas não está implementado).

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| MySQL (CCBDDebitoAutomatico) | Banco de Dados | Base de dados principal contendo informações de débitos automáticos. Conexão via JDBC com pool Bitronix. |
| Sistema de Arquivos | File System | Gravação de arquivos de retorno no diretório local `arquivo/processados/`. |

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Estrutura de pacotes bem organizada seguindo padrão MVC/camadas
- Uso adequado de padrões batch (Reader/Processor/Writer)
- Separação de responsabilidades entre classes
- Uso de enums para códigos de status e ocorrências
- Configuração externalizada por ambiente (DES/UAT/PRD/LOCAL)
- Logging adequado em pontos críticos

**Pontos Negativos:**
- **Código duplicado**: Muitos valores hardcoded repetidos nas classes de modelo (RemessaHeaderArquivo, RemessaHeaderLote, etc.)
- **Falta de documentação**: Comentários escassos, especialmente em lógicas de negócio complexas
- **Tratamento de exceções genérico**: Uso excessivo de `catch (Exception e)` sem tratamento específico
- **Magic numbers e strings**: Valores literais espalhados pelo código (ex: "655", "0001", status "4", "7", etc.)
- **Métodos longos**: ItemMapper possui métodos com muitas concatenações de strings, dificultando manutenção
- **Falta de validações**: Pouca validação de dados de entrada e estados inconsistentes
- **Testes insuficientes**: Apenas um teste de integração básico
- **Código comentado**: Presença de código comentado (ex: integração RabbitMQ) que deveria ser removido ou implementado
- **Mistura de responsabilidades**: Classes de modelo com lógica de formatação (RemessaPlain)
- **Nomenclatura inconsistente**: Mistura de português e inglês, abreviações não padronizadas

---

## 14. Observações Relevantes

1. **Ambiente de Execução**: O sistema possui configurações específicas para 4 ambientes: LOCAL, DES (Desenvolvimento), UAT (Homologação) e PRD (Produção), com diferentes conexões MySQL.

2. **Segurança**: Em produção e UAT, as senhas do banco são criptografadas usando BV Crypto com token "BV_CRYPTO_TOKEN".

3. **Parâmetro Opcional**: O parâmetro `dataProcessamento` é opcional; se não informado, o sistema utiliza a data atual.

4. **Códigos de Saída**: 
   - 0 = OK
   - 10 = Erro ao ler base de dados
   - 20 = Erro ao mover arquivo para pasta processados

5. **Framework Proprietário**: O sistema utiliza o framework BV Sistemas, que é proprietário e pode dificultar manutenção por equipes externas.

6. **Processamento em Lote Único**: Todo o processamento é feito em um único lote (cdLote = "0001"), não há suporte para múltiplos lotes no mesmo arquivo.

7. **Formato CNAB 240**: O arquivo gerado segue o padrão CNAB 240 para débito automático, com registros de 240 caracteres.

8. **Script de Execução**: Existe um script `run.sh` para facilitar build, deploy local e execução do batch em ambiente de desenvolvimento.

9. **Integração Futura**: Há indícios de planejamento para integração com RabbitMQ (código comentado no ItemWriter), sugerindo evolução futura para arquitetura orientada a eventos.

10. **Convênio Fixo**: O sistema processa apenas pagamentos dos convênios 1 e 2 (hardcoded na query de atualização de agendamentos pendentes).