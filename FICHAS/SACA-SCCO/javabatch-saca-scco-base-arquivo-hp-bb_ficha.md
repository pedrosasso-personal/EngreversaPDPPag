# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java desenvolvido para processar arquivos de remessa de cobrança no formato CNAB400 do Banco do Brasil. O sistema realiza a leitura de arquivos de remessa de boletos bancários (cartões), valida os dados conforme o layout CNAB400, e persiste as informações nas tabelas do banco de dados (DBCARNE). O processamento inclui header, detalhes principais, detalhes secundários (multa, email, título) e trailler, com validações rigorosas de domínio e formato.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê arquivos CNAB400 linha a linha do diretório configurado |
| **ItemProcessor** | Converte strings do arquivo em objetos VO (Value Objects) conforme tipo de registro |
| **ItemWriter** | Valida os dados e persiste no banco de dados através do DAO |
| **ManipularCartoesDAO** | Executa operações de inserção nas tabelas de cobrança (TBREGISTROINSTRUMENTOCOBRANCA, TBREGISTROINSTOCBRNARCLHO, TBSITUACAOPROCESSAMENTOINSTO) |
| **ConverteStringToHeader** | Converte linha do header CNAB para objeto HeaderVO |
| **ConverteStringToDetalhePrincipal** | Converte linha do detalhe principal para DetalhePrincipalVO |
| **ConverteStringToDetalheMulta** | Converte linha de detalhe de multa para DetalheMultaVO |
| **ConverteStringToDetalheEmail** | Converte linha de detalhe de email para DetalheEmailVO |
| **ConverteStringToDetalheTitulo** | Converte linha de detalhe de título para DetalheNumeroTituloVO |
| **ConverteStringToTrailler** | Converte linha do trailler para TraillerVO |
| **ValidarHeader** | Valida campos obrigatórios do header conforme especificação CNAB400 |
| **ValidarDetalhePrincipal** | Valida campos obrigatórios do detalhe principal |
| **ValidarDetalheMulta** | Valida campos do detalhe de multa |
| **ValidarDetalheEmail** | Valida campos do detalhe de email |
| **ValidarDetalheTitulo** | Valida campos do detalhe de título |
| **ValidarTrailler** | Valida campos do trailler |
| **DatabaseConnection** | Gerencia conexão com banco de dados via DataSource |
| **MyResumeStrategy** | Estratégia de recuperação de erros do batch |

---

## 3. Tecnologias Utilizadas

- **Java** (versão não especificada no código)
- **Maven** - Gerenciamento de dependências e build
- **Spring Framework** - Injeção de dependências e configuração
- **BV Framework Batch** (br.com.bvsistemas.framework.batch) - Framework proprietário para processamento batch
- **Bitronix** - Gerenciador de transações JTA
- **JTDS Driver** - Driver JDBC para SQL Server/Sybase
- **Log4j** - Logging
- **JUnit** - Testes unitários
- **SQL Server/Sybase** - Banco de dados (DBCARNE, DBCOR)

---

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch sem endpoints REST.

---

## 5. Principais Regras de Negócio

1. **Validação de Layout CNAB400**: Todos os registros devem seguir rigorosamente o layout CNAB400 do Banco do Brasil
2. **Tipo de Registro**: Header (0), Detalhe Principal (7), Detalhes Secundários (5), Trailler (9)
3. **Validação de Tipo de Inscrição**: Cedente e Sacado devem ter tipo de inscrição válido (01=PF, 02=PJ)
4. **Validação de Campos Obrigatórios**: Diversos campos possuem valores fixos obrigatórios (ex: Operação=1, Código Serviço=01, Literal Remessa="REMESSA" ou "TESTE")
5. **Campos Zerados**: Vários campos devem estar zerados (Número Prestação, Grupo Valor, Conta Caução, Número Bordero, Zeros Header)
6. **Número Banco**: Deve ser sempre "001" (Banco do Brasil)
7. **Número Sequencial Header**: Deve ser sempre "000001"
8. **Complementos de Registro**: Devem conter apenas espaços em branco
9. **Situação de Processamento**: Boletos inseridos ficam com status "PENDENTE REGISTRO"
10. **Tipo de Cobrança**: Se vazio, assume valor padrão "S"
11. **Conversão de Valores Decimais**: Valores monetários são convertidos com casas decimais específicas
12. **Relacionamento Cedente-Convênio**: Sistema busca instrumento de cobrança pelo número do convênio líder

---

## 6. Relação entre Entidades

**RemessaVO** (Raiz)
- Contém: HeaderVO, DetalheRemessaVO, TraillerVO

**HeaderVO**
- Contém: HeaderInformacoesProcessamentoVO, HeaderInformacoesBancariasVO

**DetalheRemessaVO**
- Contém: DetalhePrincipalVO, DetalheMultaVO, DetalheEmailVO, DetalheNumeroTituloVO

**DetalhePrincipalVO**
- Contém: DetalhePrincipalInformacoesCedenteVO, DetalhePrincipalInformacoesCarteiraVO, DetalhePrincipalInformacoesTituloVO, DetalhePrincipalFinanceiroTituloVO, DetalhePrincipalInformacoesSacadoVO

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| DBCOR..TBVEICULOLEGAL | Tabela | SELECT | Busca código do veículo legal pelo CNPJ do cedente |
| DBCARNE..TBSISTEMAEMISSORBOLETO | Tabela | SELECT | Busca código do sistema emissor de boleto pela sigla "CARTOES" |
| DBCARNE..TB_CARNE_PARAMETRO_REMESSA | Tabela | SELECT | Busca código do instrumento de cobrança pelo convênio |
| DBCARNE..TbEstadoProcessamento | Tabela | SELECT | Busca código da situação "PENDENTE REGISTRO" |
| DBCARNE..TBREGISTROINSTRUMENTOCOBRANCA | Tabela | SELECT | Busca o último código de registro inserido (MAX) |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| DBCARNE..TBREGISTROINSTRUMENTOCOBRANCA | Tabela | INSERT | Insere registro principal do instrumento de cobrança (boleto) com 41 campos |
| DBCARNE..TBREGISTROINSTOCBRNARCLHO | Tabela | INSERT | Insere informações complementares de cobrança (multa, desconto, juros) |
| DBCARNE..TBSITUACAOPROCESSAMENTOINSTO | Tabela | INSERT | Insere situação de processamento do instrumento (status PENDENTE REGISTRO) |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| Arquivos CNAB400 (*.txt) | Leitura | ItemReader / diretório configurável | Arquivos de remessa de cobrança no formato CNAB400 do Banco do Brasil |
| robo.log | Gravação | Log4j / diretório log/ | Log principal da aplicação |
| statistics-{executionId}.log | Gravação | Log4j / diretório log/ | Log de estatísticas de execução do batch |
| sql.properties | Leitura | PropertiesUtil / classpath | Arquivo de propriedades contendo queries SQL |

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
| Banco de Dados SQL Server/Sybase | JDBC | Conexão com bases DBCARNE e DBCOR para persistência de dados de cobrança |
| Sistema de Arquivos | File System | Leitura de arquivos CNAB400 de diretório configurável |

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Separação clara de responsabilidades (Reader, Processor, Writer)
- Uso de Value Objects (VOs) para representar estruturas de dados
- Validações específicas com exceptions customizadas
- Uso de framework batch estruturado
- Configuração externalizada (XML, properties)

**Pontos Negativos:**
- **Código legado com encoding ISO-8859-1**: Comentários com caracteres corrompidos (�)
- **Falta de tratamento adequado de exceções**: Muitos blocos catch apenas fazem log e relançam
- **Métodos muito longos**: `populaPrimeiraMetadeParametros`, `populaSegundaMetadeParametros` com muitas linhas
- **Magic numbers e strings**: Valores hardcoded espalhados pelo código ("001", "CARTOES", "PENDENTE REGISTRO")
- **Falta de constantes**: Posições do CNAB400 estão hardcoded nos métodos de conversão
- **Código comentado**: TODO's não resolvidos (ex: tipo de cobrança vazio)
- **Falta de documentação JavaDoc**: Muitos métodos sem documentação adequada
- **Acoplamento com banco de dados**: Queries SQL em properties, dificultando manutenção
- **Falta de testes unitários**: Apenas um teste de integração básico
- **Nomenclatura inconsistente**: Mistura de português e inglês

---

## 14. Observações Relevantes

1. **Sistema Legado**: Código aparenta ser antigo, com práticas que não seguem padrões modernos
2. **Dependência de Framework Proprietário**: Uso intensivo do BV Framework pode dificultar migração
3. **Configuração de Ambiente**: Diferentes configurações para DEV/QA/UAT/PROD (senha criptografada em produção)
4. **Transações Manuais**: Commits e rollbacks manuais no código, sem uso de @Transactional
5. **Encoding**: Sistema utiliza ISO-8859-1, pode haver problemas com caracteres especiais
6. **Versionamento**: Versão 17.2.3.3-SNAPSHOT indica sistema em desenvolvimento ativo
7. **Servidor de Aplicação**: Configurado para Sybase ASE (serverType=2, porta 6010)
8. **Processamento Sequencial**: Não há paralelização, processa arquivo linha a linha
9. **Validação Rigorosa**: Sistema valida minuciosamente o layout CNAB400, rejeitando arquivos inválidos
10. **Exit Codes Customizados**: Sistema define códigos de saída específicos para diferentes tipos de erro