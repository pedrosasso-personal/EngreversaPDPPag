# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **javabatch-spag-base-envia-arquivo** é um job batch Java desenvolvido para processar arquivos recebidos de parceiros/fintechs no contexto do sistema SPAG (Sistema de Pagamentos). O batch realiza duas operações principais:

1. **Listar**: Lista arquivos em diretórios configurados, validando correspondência com CNPJ cadastrado
2. **Postar**: Envia notificações para filas MQ informando parceiros sobre o recebimento de arquivos

O sistema consulta configurações de caminhos de origem/destino no banco de dados, processa arquivos conforme regras de negócio e notifica os parceiros através de mensageria IBM MQ.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê os itens a serem processados, inicializa o tipo de processamento (Listar ou Postar) baseado em parâmetros |
| **ItemProcessor** | Processa cada arquivo individualmente (atualmente com lógica comentada) |
| **ItemWriter** | Escreve/finaliza o processamento de cada arquivo, delegando para o tipo de processamento específico |
| **Listar** | Implementa a lógica de listagem de arquivos nos diretórios configurados, validando CNPJ |
| **Postar** | Implementa a lógica de postagem de notificações na fila MQ |
| **EnviarNotificacao** | Orquestra a busca de dados de notificação e envio para fila MQ |
| **MqWriter** | Responsável pela comunicação com IBM MQ, transformação de objetos em JSON e envio de mensagens |
| **CaminhoDAOImpl** | Acessa dados de configuração de caminhos (origem/destino) de arquivos |
| **NotificacaoDAOImpl** | Busca dados de notificação para envio aos parceiros |
| **ArquivoDTO** | Representa um arquivo a ser processado |
| **CaminhoDTO** | Representa configuração de caminhos de origem/destino |
| **NotificacaoDTO** | Representa dados de notificação a serem enviados |
| **Utils** | Utilitários diversos (extração de CNPJ, listagem de arquivos, etc) |

---

## 3. Tecnologias Utilizadas

- **Java** (versão não especificada explicitamente)
- **Maven** (gerenciamento de dependências e build)
- **Spring Framework** (IoC/DI, JDBC)
- **Spring Batch** (framework BV customizado: bv-framework-batch.standalone)
- **IBM MQ 7.0.1.10** (mensageria)
- **Sybase/SQL Server** (banco de dados DBSPAG via JTDS)
- **Bitronix** (gerenciador de transações)
- **Log4j** (logging)
- **JUnit** (testes)
- **Gson** (serialização JSON)
- **Apache Commons IO** (manipulação de arquivos)
- **Apache Commons Codec** (utilitários de codificação)
- **BV Crypto** (criptografia de senhas)

---

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch sem endpoints REST.

---

## 5. Principais Regras de Negócio

1. **Validação de CNPJ**: Arquivos só são processados se o nome contém o CNPJ cadastrado para o parceiro/fintech
2. **Configuração por Parceiro**: Cada fintech possui configurações específicas de caminhos de origem, destino e mailbox
3. **Tipos de Processamento**: Sistema suporta dois modos de operação (Listar e Postar) definidos por parâmetro
4. **Notificação de Recebimento**: Ao processar arquivo, sistema notifica parceiro via fila MQ com evento tipo "2" (Recebimento de Arquivo)
5. **Múltiplos Tipos de Arquivo**: Suporta arquivos de recebíveis, cobrança e CNAB240 de extrato
6. **Conta Específica**: Apenas fintechs com conta "CP1" ativa são consideradas
7. **Ativação de Cadastros**: Apenas registros com flag FlAtivo = 'S' são processados

---

## 6. Relação entre Entidades

**ArquivoDTO**
- Contém: nome do arquivo, CaminhoDTO, TipoProcessamento
- Representa um arquivo a ser processado

**CaminhoDTO**
- Contém: cdIdentificacaoFintech, NuCpfCnpj, caminhoOrigem, caminhoDestino, caminhoDestinoMailbox
- Representa configuração de diretórios para uma fintech

**NotificacaoDTO**
- Contém: clienteEndPoint, clienteUserService, evento, protocolo, hashMensagem, mensagem
- Representa dados para notificação via MQ

**Relacionamentos:**
- ArquivoDTO → CaminhoDTO (1:1)
- ArquivoDTO → TipoProcessamento (1:1)
- CaminhoDTO é buscado do banco e associado a arquivos encontrados
- NotificacaoDTO é construído a partir de dados do banco relacionados ao arquivo

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbParametroPagamentoFintech | tabela | SELECT | Cadastro de fintechs/parceiros |
| TbContaPagamentoFintech | tabela | SELECT | Contas de pagamento das fintechs |
| TbParametroConsultaCliente | tabela | SELECT | Parâmetros de configuração (URLs, caminhos, endpoints) |
| TbControleArquivoContaFintech | tabela | SELECT | Controle de arquivos processados por fintech |

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema apenas realiza consultas (SELECT), não há operações de INSERT, UPDATE ou DELETE.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| Arquivos diversos (CNPJ no nome) | leitura | Listar.listar() / Utils.listarArquivosDiretorio() | Arquivos de recebíveis, cobrança e CNAB240 nos diretórios configurados |
| robo.log | gravação | Log4j (roboFile appender) | Log de execução do batch |
| statistics-{executionId}.log | gravação | Log4j (statistics appender) | Log de estatísticas de execução |

**Observação**: O código possui lógica comentada no ItemProcessor para cópia de arquivos entre diretórios (Recebidos → Processados e para destino), mas está desabilitada.

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

---

## 11. Filas Geradas

| Nome da Fila | Descrição |
|--------------|-----------|
| QL.SPAG.NOTIFICAR_PARCEIRO_REQ.INT | Fila para notificação de parceiros sobre recebimento de arquivos. Mensagens em formato JSON contendo endpoint do cliente, usuário, evento (tipo 2), protocolo e mensagem de notificação |

**Queue Manager**: QM.ATA.01  
**Host**: qm_ata_des.bvnet.bv  
**Canal**: SPAG.SRVCONN  
**Porta**: 1414

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| IBM MQ | Mensageria | Envio de notificações para parceiros via fila QL.SPAG.NOTIFICAR_PARCEIRO_REQ.INT |
| Banco DBSPAG (Sybase) | Banco de Dados | Consulta de configurações de fintechs, caminhos e dados de notificação |
| Sistema de Arquivos (UNC) | File System | Leitura de arquivos em diretórios de rede (\\bvnet\mor\BATCH-DES\SPAG\BancoLiquidante\) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 5/10**

**Justificativa:**

**Pontos Positivos:**
- Uso de padrões de projeto (Strategy para TipoProcessamento)
- Separação de responsabilidades em camadas (DAO, Domain, Integration, Business)
- Uso de framework batch estruturado
- Configuração externalizada via Spring

**Pontos Negativos:**
- **Código comentado extensivamente** no ItemProcessor, indicando funcionalidade incompleta ou em manutenção
- **Falta de tratamento de exceções** adequado em vários pontos (catch genérico com apenas log)
- **Mistura de responsabilidades**: classe Listar implementa tanto listagem quanto processamento
- **Falta de documentação**: ausência de JavaDoc nas classes e métodos
- **Hardcoding de valores**: strings mágicas ("CP1", "2", "GET-notificar", etc)
- **Nomenclatura inconsistente**: mistura de português e inglês
- **Código duplicado**: lógica de configuração de datasource repetida
- **Falta de validações**: não há validação de parâmetros de entrada
- **Testes insuficientes**: apenas um teste de integração básico
- **Segurança**: senha em texto claro no arquivo de configuração (comentário indica que deveria usar senha criptografada)

---

## 14. Observações Relevantes

1. **Ambiente de Desenvolvimento**: Configurações apontam para ambiente de desenvolvimento (SQLBVFDES05, qm_ata_des, BATCH-DES)

2. **Funcionalidade Parcialmente Implementada**: O ItemProcessor possui toda a lógica de cópia de arquivos comentada, sugerindo que o sistema está em desenvolvimento ou manutenção

3. **Estratégia de Processamento Dinâmica**: O sistema usa reflexão para instanciar dinamicamente a classe de processamento (Listar ou Postar) baseado no parâmetro "acao"

4. **Padrão de Nomenclatura de Arquivos**: Espera-se que arquivos contenham CNPJ de 14 dígitos no nome para validação

5. **Múltiplos Tipos de Origem**: Sistema suporta três tipos de caminhos de origem: recebíveis, cobrança e CNAB240 de extrato

6. **Criptografia de Senha**: Sistema possui infraestrutura para descriptografar senhas usando BVCrypto, mas configuração de desenvolvimento usa senha em texto claro

7. **Versionamento**: Projeto na versão 0.2.1, indicando fase inicial de desenvolvimento

8. **Framework Proprietário**: Utiliza framework batch customizado da BV Sistemas (bv-framework-batch.standalone)

9. **Transações**: Job configurado como "noTransactionJobTemplate", sem controle transacional

10. **Parâmetros de Execução**: Sistema aceita parâmetros "acao" (Listar/Postar) e "nomeArquivo" para definir comportamento