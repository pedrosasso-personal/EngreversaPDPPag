# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java desenvolvido para processar cancelamentos de portabilidade de conta salário no contexto do sistema SPAG (Sistema de Pagamentos). O sistema consome mensagens de uma fila RabbitMQ contendo solicitações de cancelamento de portabilidade, gera arquivos XML no formato APCS105 (padrão CIP - Câmara Interbancária de Pagamentos) e envia notificações de processamento para outra fila. O processamento segue o padrão Reader-Processor-Writer do Spring Batch, validando os arquivos gerados contra schemas XSD específicos.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê mensagens da fila RabbitMQ contendo dados de portabilidades a serem canceladas |
| **ItemProcessor** | Transforma objetos Portabilidade em PortabilidadeArquivo, preparando dados para geração do XML |
| **ItemWriter** | Gera arquivo XML APCS105, valida contra XSD e envia confirmação para fila |
| **CancelamentoRepository** | Gerencia comunicação com filas RabbitMQ (recebimento e envio de mensagens) |
| **PortabilidadeInterator** | Iterator customizado para consumir mensagens da fila de forma iterativa |
| **ApcsEstrutura** | Classe abstrata para criação da estrutura XML do arquivo APCS105 |
| **Apcs105Impl** | Implementação concreta da estrutura APCS105 para cancelamento de portabilidade |
| **CabecalhoArquivo** | Representa o cabeçalho do arquivo XML com metadados |
| **GrupoCancelamentoPortabilidade** | Entidade de domínio representando dados de cancelamento |
| **Portabilidade** | Entidade principal contendo informações da portabilidade |
| **CancelamentoMapper** | Converte objetos de domínio para objetos de controle de arquivo |
| **EstruturaArquivoFactory** | Factory para criação de documentos XML com configurações de segurança |
| **CancelamentoException** | Exception customizada com código de saída para tratamento de erros |
| **MyResumeStrategy** | Estratégia de retomada do job batch (atualmente não permite retomada) |

## 3. Tecnologias Utilizadas

- **Java** (versão não especificada no código)
- **Spring Batch** (framework BV Sistemas customizado)
- **Spring AMQP / RabbitMQ** (versão 1.5.7.RELEASE)
- **Maven** (gerenciamento de dependências e build)
- **Log4j** (logging)
- **Gson** (versão 2.8.9 - serialização/deserialização JSON)
- **Jackson** (versão 2.12.6 - processamento JSON)
- **Apache Commons IO** (manipulação de arquivos)
- **JUnit** e **Mockito** (testes unitários)
- **XML/XSD** (validação de documentos)

## 4. Principais Endpoints REST

não se aplica

## 5. Principais Regras de Negócio

1. **Consumo de Mensagens**: O sistema consome mensagens da fila `events.business.SPAG-BASE.cancelamento.portabilidade.cip` uma por vez
2. **Geração de Arquivo XML**: Para cada portabilidade cancelada, gera um arquivo XML no formato APCS105 seguindo padrão CIP
3. **Validação de Schema**: Todos os arquivos XML gerados são validados contra o schema XSD APCS105.xsd antes de serem considerados válidos
4. **Nomenclatura de Arquivo**: Nome do arquivo segue padrão `APCS105_[ISPB]_[AAAAMMDD]_[0HHMM]`
5. **Codificação**: Arquivos são gerados em UTF-16BE conforme especificação
6. **Controle de Emissor**: Utiliza ISPB fixo 59588111 (Votorantim) como emissor e 02992335 (CIP) como destinatário
7. **Notificação de Processamento**: Após gerar o arquivo, envia mensagem para fila `events.business.portabilidade` com routing key `SPAG.cancelamentoArqPortabilidade`
8. **Tratamento de Erros**: Erros são categorizados com códigos específicos (10-15) e interrompem o processamento
9. **Processamento Condicional**: Arquivo só é gerado se houver pelo menos um registro de cancelamento (hasBody)

## 6. Relação entre Entidades

**Portabilidade** (entidade principal)
- Atributos: identdPartAdmtd, numCtrlPart, nuCtrlEmis, nuPortddPCS, motvCanceltPortddCtSalr, dataEnvioCIP
- Relacionamento: 1:1 com ControleArquivo

**ControleArquivo** (metadados do arquivo)
- Atributos: nmArquivo, dtEnvioCip, nuCtrlEmis, dtRecebimentoCip
- Relacionamento: pertence a Portabilidade

**PortabilidadeArquivo** (wrapper para processamento)
- Composição: Portabilidade + GrupoCancelamentoPortabilidade
- Uso: intermediário entre leitura e escrita

**GrupoCancelamentoPortabilidade** (estrutura XML)
- Atributos: identdPartAdmtd, numCtrlPart, nuPortddPCS, nuCtrlEmis, motvCanceltPortddCtSalr, dtCanceltPortddCtSalr
- Relacionamento: representa um grupo no XML APCS105

**CabecalhoArquivo** (metadados do arquivo XML)
- Atributos: nuControleEmissor, ispbEmissor, ispbDestinatario, dtHrArquivo, nomeArquivo
- Relacionamento: 1:N com GrupoCancelamentoPortabilidade (um cabeçalho para múltiplos grupos)

## 7. Estruturas de Banco de Dados Lidas

não se aplica

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| APCS105_[ISPB]_[DATA]_[SEQ].xml | gravação | ItemWriter / ApcsEstrutura | Arquivo XML de cancelamento de portabilidade gerado no padrão CIP |
| APCS105.xsd | leitura | ApcsEstrutura.validateXml() | Schema XSD para validação do arquivo APCS105 |
| APCSTIPOS.xsd | leitura | ApcsEstrutura.validateXml() | Schema XSD com tipos globais utilizados pelo APCS105 |
| robo.log | gravação | Log4j (RollingFileAppender) | Log de execução do batch |
| statistics-[executionId].log | gravação | Log4j (BvDailyRollingFileAppender) | Log de estatísticas do framework batch |

## 10. Filas Lidas

**Fila**: `events.business.SPAG-BASE.cancelamento.portabilidade.cip`
- **Tecnologia**: RabbitMQ
- **Classe Responsável**: PortabilidadeInterator / CancelamentoRepository
- **Formato**: JSON (convertido para objeto Portabilidade via Gson)
- **Operação**: Receive (consumo não destrutivo até processamento completo)
- **Descrição**: Fila de entrada contendo solicitações de cancelamento de portabilidade de conta salário

## 11. Filas Geradas

**Fila/Exchange**: `events.business.portabilidade`
- **Routing Key**: `SPAG.cancelamentoArqPortabilidade`
- **Tecnologia**: RabbitMQ
- **Classe Responsável**: CancelamentoRepository.sendPortabilidadeCanceladaArquivo()
- **Formato**: JSON (objeto Portabilidade serializado via Gson)
- **Descrição**: Notificação de processamento de cancelamento com informações do arquivo gerado (nome, data de envio CIP, número de controle)

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **RabbitMQ** | Mensageria | Consumo de mensagens de cancelamento e publicação de confirmações de processamento |
| **CIP (Câmara Interbancária de Pagamentos)** | Arquivo | Geração de arquivos XML no formato APCS105 para envio ao CIP (integração via arquivo) |

**Configurações por Ambiente**:
- **DES**: 10.39.216.217:5672 (usuário: _spag_des)
- **UAT**: 10.39.88.128:5672 (usuário: _spag_uat)
- **PRD**: 10.39.48.27:5672 (usuário: _spag_prd)

## 13. Avaliação da Qualidade do Código

**Nota:** 6/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com padrão Reader-Processor-Writer
- Uso adequado de abstrações (ApcsEstrutura)
- Tratamento de exceções customizado com códigos de erro
- Validação de XML contra schema XSD
- Configurações externalizadas por ambiente
- Presença de testes unitários

**Pontos Negativos:**
- Código com comentários em português misturado com código em inglês (inconsistência)
- Strings hardcoded em várias classes (nomes de filas, ISPBs, routing keys)
- Falta de documentação JavaDoc nas classes principais
- Conversão de encoding UTF-16BE implementada de forma questionável (StringUtils.converterParaUtf16BE)
- Uso de múltiplas bibliotecas JSON (Gson e Jackson) sem justificativa clara
- Classe MyResumeStrategy não implementada adequadamente (apenas retorna false)
- Logs com mensagens genéricas e pouco informativas em alguns pontos
- Falta de constantes para códigos de erro (estão apenas em ErrorCode mas poderiam ser enum)
- Dependências com versões antigas (Spring AMQP 1.5.7, Jackson 2.12.6)
- Tratamento de senha vazia em configuração de produção (possível problema de segurança)

## 14. Observações Relevantes

1. **Framework Proprietário**: O sistema utiliza um framework batch customizado da BV Sistemas (`bv-framework-batch.standalone`), o que pode dificultar manutenção por desenvolvedores não familiarizados

2. **Processamento Síncrono**: O batch processa uma mensagem por vez da fila, o que pode ser um gargalo em cenários de alto volume

3. **Ausência de Retry**: Não há mecanismo de retry automático em caso de falha no processamento

4. **Validação Tardia**: A validação do XML só ocorre após a geração completa do arquivo, o que pode desperdiçar processamento em caso de dados inválidos

5. **Configuração de Segurança XML**: O código implementa proteções contra XXE (XML External Entity) e outras vulnerabilidades XML, o que é uma boa prática

6. **Versionamento**: O projeto está na versão 0.2.0, indicando que ainda está em fase inicial de desenvolvimento

7. **Ambiente de Testes**: Configuração de testes aponta para RabbitMQ local (localhost), facilitando desenvolvimento

8. **Nomenclatura de Arquivos**: Segue padrão específico do CIP com ISPB, data e sequencial, garantindo unicidade

9. **Encoding Específico**: Uso de UTF-16BE é requisito do padrão CIP para arquivos APCS

10. **Ausência de Persistência**: O sistema não persiste dados em banco de dados, operando apenas com filas e arquivos