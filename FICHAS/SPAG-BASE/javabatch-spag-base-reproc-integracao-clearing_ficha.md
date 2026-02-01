# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de reprocessamento de mensagens de integração com Clearing (sistema de liquidação bancária). O batch consome mensagens da fila de erro do IBM MQ, processa e reenvia para a fila principal de processamento. Caso o processamento ocorra após às 17h, as mensagens não são reenviadas e um relatório é enviado por e-mail com os detalhes dos pagamentos não processados.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê mensagens da fila de erro do MQ e coordena o fluxo de processamento |
| **ItemProcessor** | Processa individualmente cada mensagem (implementação pass-through) |
| **ItemWriter** | Escreve/processa as mensagens através do ClearingService |
| **ClearingService** | Regra de negócio principal: decide se reenvia para MQ ou envia por e-mail baseado no horário |
| **ClearingProcessor** | Processa mensagens de clearing e extrai informações para relatório |
| **MQRepository** | Gerencia conexões, leitura e escrita de mensagens no IBM MQ |
| **EmailRepository** | Gerencia envio de e-mails com relatório de mensagens não processadas |
| **ClearingMessage** | Entidade de domínio representando uma mensagem de clearing |
| **MQConnectionProperties** | Propriedades de conexão com IBM MQ |
| **MyResumeStrategy** | Estratégia de retomada em caso de erro (atualmente finaliza o processo) |

---

## 3. Tecnologias Utilizadas

- **Framework Batch**: Spring Batch (BV Framework Batch)
- **Mensageria**: IBM WebSphere MQ 7.0.1.10
- **Gerenciador de Dependências**: Maven
- **Logging**: Log4j + Apache Commons Logging
- **E-mail**: JavaMail API
- **Segurança**: BV Crypto (criptografia de senhas)
- **Testes**: JUnit
- **CI/CD**: Jenkins
- **Java Version**: Não especificada explicitamente (compatível com Spring Batch 2.x)

---

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch sem endpoints REST.

---

## 5. Principais Regras de Negócio

1. **Horário de Processamento**: Mensagens são reprocessadas e reenviadas para a fila principal apenas se o horário atual for anterior às 17h (TIME_LIMIT = 17)

2. **Processamento Pós-Horário**: Após às 17h, as mensagens não são reenviadas ao MQ, mas são coletadas e enviadas por e-mail em formato de relatório

3. **Reprocessamento de Erros**: O sistema consome mensagens da fila de erro (`QL.SPAG.BANCO_LIQUIDANTE_ER_RECEBIMENTO_REQ.INT`) e tenta reprocessá-las enviando para a fila principal (`QL.SPAG.BANCO_LIQUIDANTE_RECEBIMENTO_REQ.INT`)

4. **Extração de Informações**: Para o relatório por e-mail, são extraídos o tipo de mensagem (tag `<CodMsg>`) e número de controle (tag `<NumCtrl>`)

5. **Tipos de Mensagem Suportados**: O sistema identifica mensagens SPB (PAG*, STR*) e LTR (LTR*, SLC*)

6. **Estratégia de Erro**: Em caso de exceção, o processo é finalizado (não há retomada automática)

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **ClearingMessage**: Entidade simples contendo apenas o texto da mensagem
  - Atributo: `text` (String)

- **MQConnectionProperties**: Configurações de conexão MQ
  - Atributos: `connectionFactory`, `user`, `password`

**Relacionamentos:**
- Não há relacionamentos complexos entre entidades. O sistema trabalha com mensagens textuais (TextMessage do JMS) que são encapsuladas em ClearingMessage para processamento.

---

## 7. Estruturas de Banco de Dados Lidas

Não se aplica. O sistema não acessa banco de dados diretamente.

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema não acessa banco de dados diretamente.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| job-resources.xml | Leitura | Spring Context | Arquivo de configuração com propriedades de conexão MQ e e-mail |
| job-definitions.xml | Leitura | Spring Batch | Definição do job batch, beans e parâmetros |
| log4j.xml | Leitura | Log4j | Configuração de logging |
| mensagens-clearing-[data].txt | Gravação (anexo e-mail) | EmailRepository | Arquivo anexo ao e-mail contendo mensagens não processadas |

---

## 10. Filas Lidas

| Nome da Fila | Tipo | Classe Responsável | Descrição |
|--------------|------|-------------------|-----------|
| QL.SPAG.BANCO_LIQUIDANTE_ER_RECEBIMENTO_REQ.INT | IBM MQ | MQRepository | Fila de erro contendo mensagens de clearing que falharam no processamento inicial |

---

## 11. Filas Geradas

| Nome da Fila | Tipo | Classe Responsável | Descrição |
|--------------|------|-------------------|-----------|
| QL.SPAG.BANCO_LIQUIDANTE_RECEBIMENTO_REQ.INT | IBM MQ | MQRepository | Fila principal para reprocessamento de mensagens de clearing |

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **IBM WebSphere MQ** | Mensageria | Queue Manager: QM.ATA.01, Host: qm_ata_des.bvnet.bv, Porta: 1414, Canal: SPAG.SRVCONN |
| **Servidor SMTP** | E-mail | Host: smtpduqrelay.bvnet.bv (desenvolvimento) / smtprelay.bvnet.bv (produção) |
| **BV Crypto** | Segurança | Sistema de criptografia/descriptografia de senhas (token: BV_CRYPTO_TOKEN) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com uso de repositories e services
- Uso adequado de interfaces (QueueRepository, ReportRepository)
- Logging presente em pontos importantes
- Tratamento de exceções com códigos de erro customizados
- Uso de enums para constantes (ExitCodes, Queues)

**Pontos Negativos:**
- **ItemProcessor vazio**: apenas retorna a mensagem sem processamento real
- **Hardcoded values**: horário limite (17h) está fixo no código
- **Comentários em português**: mistura de português e inglês
- **Falta de validações**: não há validação de mensagens nulas ou malformadas
- **Configurações expostas**: senha em texto claro no XML (comentário indica uso de senha criptografada em produção)
- **Regex simples**: extração de dados da mensagem XML poderia usar parser XML adequado
- **Falta de testes**: arquivos de teste não foram incluídos na análise
- **Exception handling genérico**: captura de Exception genérica em alguns pontos
- **Acoplamento**: ClearingService instancia ClearingProcessor diretamente
- **Magic numbers**: uso de 500L para timeout sem constante nomeada

---

## 14. Observações Relevantes

1. **Ambiente**: Configurações apontam para ambiente de desenvolvimento (des)

2. **Segurança**: O sistema utiliza BV Crypto para descriptografia de senhas, mas no arquivo de configuração a senha está em texto claro (comentário indica que deve ser alterado em produção)

3. **Destinatários de E-mail**: Configurados para equipe técnica específica (cwi.jbento, cwi.esilva, gft.nbrasiliano)

4. **Reconexão Automática**: MQ configurado com reconexão automática (timeout de 60 segundos)

5. **Tipos de Mensagem**: Sistema preparado para processar mensagens SPB e LTR do sistema de pagamentos

6. **Limitação de Horário**: Regra de negócio crítica baseada em horário (17h) que pode precisar de parametrização

7. **Formato de Mensagens**: Mensagens em formato XML com tags específicas (CodMsg, NumCtrl)

8. **CI/CD**: Integrado com Jenkins, deploy em QA desabilitado (disableQADeploy=true)

9. **Versionamento**: Versão 0.1.0 indica que o sistema está em fase inicial

10. **Framework Proprietário**: Utiliza framework batch proprietário da BV Sistemas (versão 13.0.19)