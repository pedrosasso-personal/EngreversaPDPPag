# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de processamento batch Java responsável pela varredura e registro de títulos DDA (Débito Direto Autorizado) de pagadores. O sistema processa arquivos XML compactados (.gz) retornados pela CIP (Câmara Interbancária de Pagamentos), extrai informações de boletos e títulos, persiste os dados em banco de dados Sybase e notifica eventos através de filas RabbitMQ. O processamento segue o padrão Spring Batch com estratégia de leitura, processamento e escrita de itens.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê arquivos XML compactados do diretório de entrada, renomeia para .gz se necessário e gerencia movimentação para pastas processado/rejeitado |
| **ItemProcessor** | Converte arquivos XML em objetos ADDADOCComplexType utilizando FileUtil |
| **ItemWriter** | Persiste títulos DDA no banco de dados e envia notificações para fila RabbitMQ |
| **RegistrarBoletoImpl** | Implementa lógica de negócio para registro de retorno CIP |
| **RegistrarBoletoDAOImpl** | Executa operações de banco de dados (insert/delete) para títulos, juros, multas, descontos, notas fiscais, cálculos e baixas |
| **DatabaseConnection** | Gerencia conexões com banco de dados Sybase através de DataSource |
| **MyResumeStrategy** | Estratégia de tratamento de erros e definição de exit codes do batch |
| **ADDA127Mapper** | Mapeia objetos de domínio para DTOs de notificação |
| **Constants** | Centraliza constantes do sistema (códigos de erro, nomes de filas, exchanges) |

---

## 3. Tecnologias Utilizadas

- **Java** (linguagem principal)
- **Spring Batch** (framework de processamento em lote)
- **Spring AMQP / RabbitMQ** (mensageria)
- **Maven** (gerenciamento de dependências)
- **JAXB** (binding XML para objetos Java)
- **Sybase ASE** (banco de dados - DBPGF_TES)
- **Bitronix** (gerenciador de transações JTA)
- **BVSistemas Framework** (framework corporativo para batch e logging)
- **Jackson** (serialização JSON)
- **JDBC** (acesso a dados)

---

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch sem exposição de endpoints REST.

---

## 5. Principais Regras de Negócio

1. **Processamento de Arquivos DDA**: Lê arquivos XML compactados contendo títulos ADDA127 retornados pela CIP
2. **Exclusão Preventiva**: Antes de inserir um título, exclui registros anteriores do mesmo título (evita duplicação)
3. **Persistência Hierárquica**: Insere título principal e seus relacionamentos (juros, multas, descontos, notas fiscais, cálculos, baixas operacionais)
4. **Notificação de Títulos**: Para cada título processado, envia notificação via RabbitMQ para o exchange `events.business.tituloPagadorDda`
5. **Movimentação de Arquivos**: Arquivos processados com sucesso vão para pasta "processado", com erro vão para "rejeitado"
6. **Tratamento de Nulos**: Campos opcionais são tratados com setNull() apropriado para evitar erros de persistência
7. **Controle Transacional**: Cada arquivo é processado em transação única com commit/rollback
8. **Conversão de Tipos**: Conversões específicas entre BigInteger, BigDecimal, String e tipos primitivos conforme necessidade do banco

---

## 6. Relação entre Entidades

**Entidade Principal: TituloDDA**
- Relacionamento 1:1 com **JurosTituloDDA** (juros do título)
- Relacionamento 1:1 com **MultaTituloDDA** (multa do título)
- Relacionamento 1:N com **DescontoTituloDDA** (descontos aplicáveis)
- Relacionamento 1:N com **NotaFiscalTituloDDA** (notas fiscais vinculadas)
- Relacionamento 1:N com **CalculoTituloDDA** (cálculos de valores)
- Relacionamento 1:N com **BaixaOperacionalTituloDDA** (baixas operacionais)

**Estrutura XML ADDA127**:
- SISARQ contém ADDA127
- ADDA127 contém lista de GrupoADDA127Tit (títulos)
- Cada título contém grupos de juros, multa, descontos, notas, cálculos e baixas

---

## 7. Estruturas de Banco de Dados Lidas

Não se aplica. O sistema não realiza operações de leitura (SELECT) em tabelas do banco de dados.

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|----------------------------|------|----------|-----------------|
| TituloDDA | tabela | DELETE | Exclusão de títulos existentes antes de reprocessamento |
| TituloDDA | tabela | INSERT | Inserção de títulos DDA com dados completos do pagador, beneficiário e características do título |
| JurosTituloDDA | tabela | INSERT | Inserção de informações de juros do título (código, data, valor/percentual) |
| MultaTituloDDA | tabela | INSERT | Inserção de informações de multa do título (código, data, valor/percentual) |
| DescontoTituloDDA | tabela | INSERT | Inserção de descontos aplicáveis ao título (código, data, valor/percentual) |
| NotaFiscalTituloDDA | tabela | INSERT | Inserção de notas fiscais vinculadas ao título (número, data emissão, valor) |
| CalculoTituloDDA | tabela | INSERT | Inserção de cálculos de valores (juros, multa, desconto, total a cobrar) |
| BaixaOperacionalTituloDDA | tabela | INSERT | Inserção de baixas operacionais do título (identificação, tipo, valores, portador) |

**Observação**: Todas as operações são executadas via stored procedures (PrExcluirTituloDDA, PrInserirTitulosDda, PrInserirJurosTitulosDda, etc.)

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| Arquivos XML.gz | Leitura | ItemReader / FileUtil | Arquivos XML compactados contendo títulos ADDA127 retornados pela CIP |
| processamento.xml | Gravação temporária | FileUtil (CAMINHO_PROCESSAMENTO_ROBO) | Arquivo temporário durante processamento |
| Arquivos processados | Movimentação | ItemReader.handleDispose() | Arquivos movidos para pasta "processado" após sucesso |
| Arquivos rejeitados | Movimentação | ItemReader.handleDispose() | Arquivos movidos para pasta "rejeitado" após erro |

**Diretórios configuráveis** (config.properties):
- CAMINHO_RET: Diretório de entrada
- CAMINHO_RET_PROCESSADO: Diretório de arquivos processados
- CAMINHO_RET_REJEITADO: Diretório de arquivos rejeitados
- CAMINHO_PROCESSAMENTO_ROBO: Diretório temporário

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas, apenas publica.

---

## 11. Filas Geradas

| Nome da Fila/Exchange | Tipo | Classe Responsável | Breve Descrição |
|----------------------|------|-------------------|-----------------|
| events.business.tituloPagadorDda | Exchange RabbitMQ | ItemWriter | Exchange para notificação de títulos DDA processados. Mensagens em formato JSON contendo TituloNotificacaoDTO |

**Configuração RabbitMQ**:
- Host: localhost
- Porta: 5672
- Virtual Host: /
- Usuário: guest
- Senha: criptografada com BVCrypto

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|----------------|------|-----------|
| **CIP (Câmara Interbancária de Pagamentos)** | Arquivo | Recebe arquivos XML de retorno contendo títulos DDA (ADDA127) |
| **RabbitMQ** | Mensageria | Publica notificações de títulos processados para consumo por outros sistemas |
| **Sybase ASE (DBPGF_TES)** | Banco de Dados | Persiste informações de títulos DDA e relacionamentos |

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades (Reader, Processor, Writer)
- Uso adequado de framework Spring Batch
- Tratamento de exceções com códigos de erro específicos
- Uso de prepared statements (previne SQL injection)
- Tratamento de valores nulos consistente
- Logging estruturado com BVLogger

**Pontos Negativos:**
- **Código comentado em excesso** no config.properties (múltiplos ambientes)
- **Classe DAO muito extensa** (RegistrarBoletoDAOImpl com 500+ linhas)
- **Métodos auxiliares repetitivos** (setStatementXXX) poderiam ser refatorados
- **Falta de documentação JavaDoc** nas classes principais
- **Hardcoded strings** em várias partes (nomes de stored procedures)
- **Múltiplos PreparedStatements** (1 a 8) na classe AbstractDAO indica design questionável
- **Falta de testes unitários** (não fornecidos)
- **Acoplamento com framework proprietário** (BVSistemas)
- **Tratamento de erro genérico** em alguns pontos (catch Exception)
- **Configurações sensíveis** em arquivo properties (senhas, mesmo que criptografadas)

---

## 14. Observações Relevantes

1. **Ambientes Múltiplos**: O arquivo config.properties contém configurações comentadas para DEV, QA, UAT e PROD, sugerindo deploy manual por ambiente

2. **Estratégia de Retomada**: A classe MyResumeStrategy sempre retorna `false` em `canResume()`, indicando que o batch não tenta recuperação automática de erros

3. **Transações**: Cada arquivo é processado em uma única transação. Falha em qualquer título causa rollback de todo o arquivo

4. **Segurança**: Senha do RabbitMQ utiliza criptografia BVCrypto com token de ambiente

5. **Processamento Sequencial**: O sistema processa um arquivo por vez (não há paralelização)

6. **Dependência de Stored Procedures**: Toda lógica de persistência está em procedures do banco (PrInserirTitulosDda, etc.), dificultando manutenção e testes

7. **Conversão de Tipos**: Há conversões complexas entre BigInteger, BigDecimal e tipos primitivos devido ao mapeamento JAXB vs banco de dados

8. **Nomenclatura**: Uso de português e inglês misturados no código

9. **Framework Legado**: Uso de framework BVSistemas proprietário pode dificultar migração futura

10. **Código Gerado**: Classes de VO (ADDA127ComplexType e relacionadas) são geradas automaticamente pelo JAXB a partir de XSD