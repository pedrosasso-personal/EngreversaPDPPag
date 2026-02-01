# Ficha Técnica do Sistema

---

## 1. Descrição Geral

Sistema batch Java responsável por processar arquivos XML de retorno de solicitações de portabilidade de conta salário (padrão APCS101) recebidos do CIP (Câmara Interbancária de Pagamentos). O sistema lê arquivos XML de um diretório, processa as informações de portabilidade (aceitas ou recusadas), e publica mensagens em filas RabbitMQ para processamento posterior. Após o processamento bem-sucedido, move os arquivos para diretórios específicos (processado ou erro).

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê arquivos XML (APCS101_RET ou APCS101_ERR) do diretório de entrada, faz parse do XML e itera sobre as portabilidades encontradas |
| **ItemProcessor** | Transforma objetos PortabilidadeSalario em PortabilidadeControleArquivo, mapeando para os domínios de negócio |
| **ItemWriter** | Publica mensagens JSON em filas RabbitMQ (portabilidade e controle de arquivo) |
| **APCS101Ret** | Processa arquivos XML de retorno com portabilidades aceitas e recusadas |
| **APCS101Err** | Processa arquivos XML de erro do CIP |
| **PortabilidadeMapper** | Converte objetos de estrutura XML para objetos de domínio |
| **EstruturaArquivoFactory** | Factory para criação de Document XML com configurações de segurança |
| **MyResumeStrategy** | Estratégia de retomada do batch (atualmente não permite retomada) |
| **FileUtils** | Utilitário para movimentação de arquivos entre diretórios |
| **Resource** | Gerencia caminhos dos diretórios de arquivo (recebido, processado, erro) |

---

## 3. Tecnologias Utilizadas

- **Java** (versão não especificada explicitamente)
- **Maven** (gerenciamento de dependências e build)
- **Spring Framework** (IoC/DI, configuração XML)
- **Spring AMQP / RabbitMQ** (mensageria)
- **BV Framework Batch** (framework proprietário para processamento batch)
- **Jackson** (serialização/deserialização JSON - versão 2.5.1)
- **Log4j** (logging)
- **JUnit** (testes unitários)
- **Mockito** (mocks para testes - versão 2.28.2)
- **Apache Commons IO** (manipulação de arquivos)
- **XML DOM Parser** (processamento de arquivos XML)

---

## 4. Principais Endpoints REST

não se aplica

---

## 5. Principais Regras de Negócio

1. **Processamento de Portabilidades Aceitas**: Extrai informações de portabilidades aceitas (IdentdPartAdmtd, NumCtrlPart, NUPortddPCS) e envia para fila de portabilidade
2. **Processamento de Portabilidades Recusadas**: Extrai portabilidades recusadas com código de erro e envia apenas para fila de controle de arquivo
3. **Controle de Arquivo**: Registra informações de controle do arquivo processado (nome, data de recebimento CIP, situação pendente)
4. **Movimentação de Arquivos**: Move arquivos processados com sucesso para diretório "processado" ou para diretório "erro" em caso de falha
5. **Tratamento de Erros CIP**: Processa arquivos de erro (APCS101_ERR) enviados pelo CIP quando há problemas no arquivo original
6. **Validação XML**: Aplica configurações de segurança XML (desabilita DTD, entidades externas) para prevenir ataques XXE
7. **Situação Pendente**: Define código de situação como 1 (SITUACAO_PENDENTE) para controle de arquivo

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **PortabilidadeSalario**: Entidade central contendo dados da portabilidade (codErro, identdPartAdmtd, numCtrlPart, nuPortddPCS) e referência ao CabecalhoArquivo
- **CabecalhoArquivo**: Contém metadados do arquivo (nomeArquivo, numCtrlEmis, numCtrlDestOr, ispbEmissor, ispbDestinatario, dtHrArquivo, dtRef)
- **PortabilidadeRet**: Domínio de portabilidade com nuSequencialUnico e nuUnicoCip
- **ControleArquivo**: Domínio de controle com nmArquivo e dtRecebimentoCip
- **DominioPortabilidade**: Wrapper para PortabilidadeRet
- **DominioControleArquivo**: Wrapper para ControleArquivo com informações adicionais (cdErro, nuSequencialUnico, nuUnicoCip, cdSituacao)
- **PortabilidadeControleArquivo**: Agregador contendo DominioControleArquivo e DominioPortabilidade

**Relacionamentos:**
- PortabilidadeSalario (1) -> (1) CabecalhoArquivo
- PortabilidadeControleArquivo (1) -> (1) DominioControleArquivo
- PortabilidadeControleArquivo (1) -> (1) DominioPortabilidade
- DominioPortabilidade (1) -> (1) PortabilidadeRet
- DominioControleArquivo (1) -> (1) ControleArquivo

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
| APCS101_*_RET.xml | Leitura | ItemReader / APCS101Ret | Arquivo XML de retorno com portabilidades aceitas/recusadas do CIP |
| APCS101_ERR.xml | Leitura | ItemReader / APCS101Err | Arquivo XML de erro enviado pelo CIP |
| robo.log | Gravação | Log4j (RollingFileAppender) | Log de execução do batch |
| statistics-{executionId}.log | Gravação | BvDailyRollingFileAppender | Log de estatísticas do framework batch |
| Arquivos processados | Movimentação | ItemReader.handleDispose() | Arquivos movidos para diretório "processado" após sucesso |
| Arquivos com erro | Movimentação | ItemReader.handleDispose() | Arquivos movidos para diretório "erro" após falha |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

| Nome da Fila | Exchange | Routing Key | Descrição |
|--------------|----------|-------------|-----------|
| Fila de Portabilidade | events.business.portabilidade | SPAG.retornoSolicitacaoPortabilidade | Recebe mensagens JSON com dados de portabilidades aceitas (nuSequencialUnico, nuUnicoCip) |
| Fila de Controle de Arquivo | events.business.portabilidade | SPAG.solicitacaoArqPortabilidade | Recebe mensagens JSON com controle de processamento do arquivo (nome, data recebimento, código erro, situação) |

**Configurações RabbitMQ por Ambiente:**
- **DES**: host=10.39.216.217, port=5672, user=_spag_des
- **UAT**: host=10.39.88.128, port=5672, user=_spag_uat
- **PRD**: host=rabbit-spag-base-lb.app.bvnet.bv, port=5672, user=_spag_prd

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **CIP (Câmara Interbancária de Pagamentos)** | Arquivo XML | Recebe arquivos XML de retorno de solicitações de portabilidade de conta salário (padrão APCS101) |
| **RabbitMQ** | Mensageria | Publica mensagens para sistemas downstream processarem portabilidades e controle de arquivos |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades (Reader, Processor, Writer)
- Uso adequado do padrão batch com framework proprietário
- Implementação de segurança XML contra ataques XXE
- Cobertura de testes unitários presente
- Tratamento de exceções customizado com códigos de erro específicos
- Uso de constantes para valores fixos
- Logging adequado em pontos críticos

**Pontos Negativos:**
- Uso de versões antigas de bibliotecas (Jackson 2.5.1 de 2015)
- Comentários em português com caracteres mal codificados (encoding issues)
- Classe MyResumeStrategy praticamente vazia (apenas retorna false)
- Testes do ItemWriter comentados (não executam)
- Falta de validação de parâmetros em alguns métodos
- Uso de utility classes com construtores privados que lançam exceção (anti-pattern)
- Configurações hardcoded em XMLs por ambiente (poderia usar profiles ou externalização)
- Falta de documentação JavaDoc nas classes principais
- Código de parse XML poderia ser mais robusto com tratamento de casos extremos

---

## 14. Observações Relevantes

1. **Framework Proprietário**: O sistema utiliza o "BV Framework Batch" (br.com.bvsistemas), que é um framework proprietário do Banco Votorantim, abstraindo a complexidade do processamento batch

2. **Padrão CIP**: Os arquivos seguem o padrão APCS101 da CIP para portabilidade de conta salário, com XSDs específicos (APCS101.xsd e APCS101ERR.xsd)

3. **Códigos de Saída Customizados**: 
   - 10: Arquivo não encontrado
   - 11: Erro na leitura do arquivo
   - 12: Erro de parse do arquivo XML
   - 13: Erro ao enviar para fila
   - 14: Erro ao carregar arquivo

4. **Estrutura de Diretórios**: O sistema trabalha com três diretórios principais:
   - `/arquivo/recebido/`: Arquivos a processar
   - `/arquivo/processado/`: Arquivos processados com sucesso
   - `/arquivo/erro/`: Arquivos com erro no processamento

5. **Execução**: O batch é executado via linha de comando (.bat) recebendo o nome do arquivo como parâmetro

6. **Encoding**: Há evidências de problemas de encoding no código (caracteres especiais mal formatados em comentários)

7. **Versionamento**: Versão atual do componente é 0.1.1, indicando que ainda está em fase inicial de desenvolvimento/maturação

8. **Multi-módulo Maven**: Projeto organizado em módulos (core e dist), seguindo boas práticas de separação entre lógica e distribuição