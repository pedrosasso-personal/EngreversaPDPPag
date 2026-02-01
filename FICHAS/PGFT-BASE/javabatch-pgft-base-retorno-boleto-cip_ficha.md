# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema Java Batch desenvolvido para processar arquivos de retorno de boletos CIP (Câmara Interbancária de Pagamentos) em contingência. O sistema lê arquivos XML compactados (.gz) contendo informações de baixa operacional de boletos, processa os dados de títulos aceitos e recusados, atualiza o banco de dados e envia notificações por e-mail sobre o resultado do processamento.

O fluxo principal consiste em:
- Leitura de arquivos XML compactados de uma pasta de entrada
- Descompactação e parsing dos arquivos usando JAXB
- Processamento de títulos aceitos e recusados pela CIP
- Atualização de status no banco de dados Sybase
- Movimentação de arquivos para pastas de sucesso ou erro
- Envio de e-mails com relatórios de processamento

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê arquivos XML de retorno da CIP, descompacta arquivos .gz e converte para objetos Java |
| **ItemProcessor** | Processa os itens lidos (implementação simples, apenas repassa os dados) |
| **ItemWriter** | Grava os dados processados no banco, atualiza status de baixa operacional e envia e-mails |
| **BaixaOperacionalBusinessImpl** | Camada de negócio para operações de baixa operacional |
| **BaixaOperacionalDaoImpl** | Acesso a dados para consultas e atualizações de baixa operacional |
| **FileUtil** | Utilitários para manipulação de arquivos (compressão, descompressão, conversão XML) |
| **LeitorXML / LeitorXMLArquivo** | Leitura e navegação em estruturas XML |
| **SpringEmailImpl** | Implementação de envio de e-mails usando Spring Mail |
| **SiteUtil** | Utilitários gerais (formatação de datas, strings, etc.) |

---

## 3. Tecnologias Utilizadas

- **Java 6+** (JAXB, Reflection)
- **Spring Framework** (Injeção de dependências, configuração XML)
- **Spring Batch** (Processamento em lote com padrão Reader-Processor-Writer)
- **Spring Mail** (Envio de e-mails)
- **Maven** (Gerenciamento de dependências)
- **JAXB** (Unmarshalling de XML para objetos Java)
- **Sybase/SQL Server** (Banco de dados DBPGF_TES)
- **Bitronix** (Gerenciamento de transações JTA)
- **Apache Commons Lang** (Utilitários de string)
- **BV Framework** (Framework proprietário do Banco Votorantim para batch e logging)

---

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch sem endpoints REST.

---

## 5. Principais Regras de Negócio

1. **Processamento de Arquivos CIP**: O sistema processa apenas arquivos com prefixo "ADDA114" e extensões específicas (RET, PRO, ERR)

2. **Baixa Operacional em Contingência**: Processa títulos marcados como contingência (FlBaixaOperacionalContingencia='S' e FlProcessamentoCIP='E')

3. **Tratamento de Títulos Aceitos**: Títulos aceitos pela CIP têm seu status atualizado e são registrados na tabela de resposta com código "DDA0108R1"

4. **Tratamento de Títulos Recusados**: Títulos recusados têm seus códigos de erro extraídos via reflection e são notificados por e-mail

5. **Prevenção de Duplicidade**: Verifica se um registro já foi processado antes de atualizar novamente

6. **Movimentação de Arquivos**: Arquivos processados com sucesso vão para pasta "Sucesso", arquivos com erro vão para pasta "Erro"

7. **Notificação por E-mail**: Envia e-mails separados para títulos aceitos e recusados, com detalhes completos de cada operação

8. **Descompactação Automática**: Arquivos sem extensão .gz são automaticamente renomeados antes da descompactação

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **BaixaOperacionalVO**: Representa uma requisição de baixa operacional de boleto
  - Contém: código de registro CIP, meio de pagamento, canal, CPF/CNPJ do portador, valor, código de barras, datas de processamento

- **BaixaOperacionalRespostaVO**: Representa a resposta do processamento CIP
  - Relaciona-se com BaixaOperacionalVO através do código de requisição
  - Contém: flags de aceite/contingência, códigos e descrições de retorno CIP

- **CipTituloRetornoVO**: VO de transporte para dados de retorno
  - Contém: número de controle, identificação do beneficiário, extensão do arquivo, códigos de erro

**Relacionamentos:**
- Um registro de BaixaOperacional pode ter uma ou mais respostas (BaixaOperacionalResposta)
- CipTituloRetornoVO é usado como estrutura intermediária no processamento batch

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbRegistroPagamentoCIP | Tabela | SELECT | Consulta títulos em contingência pendentes de processamento CIP |
| TbRegistroPagamentoCIP | Tabela | SELECT | Recupera dados de baixa operacional por código de requisição |
| TbParametroInterfaceCIP | Tabela | SELECT | Consulta e-mail destinatário para notificações |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbRegistroPagamentoCIP | Tabela | UPDATE | Atualiza flags de processamento CIP e contingência após retorno |
| TbRetornoBaixaOperacionalCIP | Tabela | INSERT | Insere registro de resposta da CIP com status de aceite/recusa e códigos de retorno |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| ADDA114_*_RET.gz | Leitura | ItemReader / FileUtil | Arquivo compactado XML de retorno da CIP com títulos aceitos/recusados |
| ADDA114_*_ERR.gz | Leitura | ItemReader / FileUtil | Arquivo compactado XML de erro quando todo o lote foi rejeitado |
| ADDA114_*_PRO | Leitura | ItemReader | Arquivo indicando processamento em andamento |
| *.xml (descompactado) | Gravação temporária | FileUtil.salvarArquivoRetorno | Arquivo XML descompactado para processamento, apagado após uso |
| Arquivos processados | Movimentação | FileUtil.moverArquivo | Arquivos movidos para pastas Sucesso ou Erro conforme resultado |

**Pastas configuráveis (config.properties):**
- prop.pendente: Pasta de entrada de arquivos
- prop.sucesso: Pasta de arquivos processados com sucesso
- prop.erro: Pasta de arquivos rejeitados

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

---

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **CIP (Câmara Interbancária de Pagamentos)** | Arquivo | Recebe arquivos XML de retorno de processamento de boletos via sistema de arquivos compartilhado |
| **Servidor SMTP** | E-mail | Envia notificações via servidor SMTP (smtprelay.bvnet.bv ou smtpduqrelay.bvnet.bv) |
| **Banco de Dados Sybase** | JDBC | Conecta ao servidor Sybase para leitura e gravação de dados de baixa operacional |

---

## 13. Avaliação da Qualidade do Código

**Nota: 5/10**

**Justificativa:**

**Pontos Positivos:**
- Uso adequado do padrão Spring Batch (Reader-Processor-Writer)
- Separação em camadas (DAO, Business, Batch)
- Tratamento de exceções customizado
- Uso de JAXB para parsing XML
- Configuração externalizada em properties

**Pontos Negativos:**
- **Código legado com encoding problemático**: Comentários em português com caracteres corrompidos (�) indicam problemas de encoding
- **Mistura de responsabilidades**: ItemWriter faz muito mais que escrever (envia e-mail, valida duplicidade, move arquivos)
- **Falta de tratamento adequado de recursos**: Alguns métodos não garantem fechamento de streams em todos os cenários
- **Hardcoding**: Strings mágicas e códigos fixos espalhados pelo código (ex: "DDA0108R1", "ADDA114")
- **Reflection desnecessária**: Uso de reflection em `obterErrosArquivoRetorno` poderia ser substituído por interface ou método comum
- **Falta de testes**: Não há evidências de testes unitários
- **Documentação inconsistente**: Javadoc presente mas incompleto e com encoding corrompido
- **Configuração fragmentada**: Múltiplos arquivos de configuração com informações duplicadas
- **Segurança**: Senhas em texto claro nos arquivos de configuração (embora haja comentário sobre uso de cofre)
- **Código morto**: Variáveis e métodos não utilizados (ex: `configuracoes.properties` com path fixo)

O código funciona mas necessita refatoração significativa para melhorar manutenibilidade, segurança e aderência a boas práticas.

---

## 14. Observações Relevantes

1. **Ambientes Múltiplos**: O sistema possui configurações comentadas para DES, QA, UAT e PRD, facilitando deploy mas aumentando risco de erro de configuração

2. **ISPB Fixos**: Utiliza ISPBs fixos do Banco Votorantim (59588111) e CIP (17423302) como constantes

3. **Framework Proprietário**: Depende fortemente do framework BV (br.com.bvsistemas), o que pode dificultar portabilidade

4. **Processamento Síncrono**: Não há evidências de processamento paralelo ou assíncrono, o que pode ser um gargalo para grandes volumes

5. **Gestão de Arquivos**: Sistema depende de pastas de rede Windows (\\\\bvnet\\...), o que pode causar problemas de permissão e disponibilidade

6. **Encoding**: Projeto possui problemas de encoding em comentários e possivelmente em processamento de arquivos (uso de UTF-16BE)

7. **Versionamento**: Código gerado por JAXB em 2017, indicando que o sistema está em produção há vários anos

8. **Monitoramento**: Usa BVLogger para logging, mas não há evidências de métricas ou monitoramento avançado

9. **Transações**: Utiliza Bitronix para gerenciamento de transações JTA, garantindo consistência nas operações de banco

10. **E-mail Destinatário**: E-mail de destino é buscado dinamicamente do banco de dados, permitindo alteração sem redeploy