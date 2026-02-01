# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java responsável pelo envio automatizado de avisos de títulos DDA (Débito Direto Autorizado) para clientes do Banco Votorantim. O sistema busca títulos pendentes de notificação no banco de dados e envia avisos através de e-mail e SMS, utilizando serviços externos de notificação. Após o envio bem-sucedido, atualiza o status de notificação no banco de dados.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê os avisos pendentes de envio do banco de dados através do EnvioAvisoBus |
| **ItemProcessor** | Processa os avisos (implementação simples, apenas repassa o objeto) |
| **ItemWriter** | Escreve/envia os avisos através do EnvioAvisoBus |
| **EnvioAvisoBus** | Orquestra a lógica de negócio: busca avisos, envia e-mail, envia SMS e atualiza flags |
| **EnvioAvisoDAO** | Acesso a dados: busca avisos, verifica envios e atualiza flags de pendência |
| **AvisoVO** | Objeto de transferência de dados contendo informações do aviso |
| **EmailHelper** | Utilitário para envio de e-mails usando Spring Mail |
| **NotificacaoTechnicalServiceConsumer** | Cliente do serviço SOAP de notificação (envio de SMS) |
| **MyResumeStrategy** | Estratégia de tratamento de erros e códigos de saída do batch |
| **ExitCode** | Enum com códigos e descrições de erros do sistema |

## 3. Tecnologias Utilizadas

- **Java** com Maven para gerenciamento de dependências
- **Spring Batch** (framework de processamento batch)
- **Spring Framework** (IoC/DI)
- **Apache Axis2** (cliente SOAP/Web Services)
- **Spring Mail / JavaMail** (envio de e-mails)
- **Sybase/SQL Server** (banco de dados via JTDS)
- **Bitronix** (gerenciador de transações JTA)
- **Log4j** (logging)
- **JUnit** (testes)
- **BV Framework** (framework proprietário do Banco Votorantim)
- **BV Crypto** (criptografia de senhas)

## 4. Principais Endpoints REST

não se aplica

## 5. Principais Regras de Negócio

1. **Busca de Avisos Pendentes**: Busca títulos DDA com flag de notificação pendente (`FlNotificacaoPendenteEnvio = 'S'`), incluindo clientes diretos e agregados
2. **Verificação de Envio Duplicado**: Antes de enviar, verifica se já foi enviado aviso para o CPF/CNPJ no mesmo dia
3. **Envio Condicional de E-mail**: Envia e-mail apenas se o cliente possuir endereço eletrônico cadastrado
4. **Envio Condicional de SMS**: Envia SMS apenas se o cliente possuir DDD e telefone cadastrados
5. **Formatação de SMS**: Limita o texto do SMS a 142 caracteres e trunca o nome do pagador em 14 caracteres
6. **Atualização de Status**: Após envio bem-sucedido, atualiza flag de pendência para 'N' e registra data de alteração
7. **Tratamento de Erros**: Captura exceções e as converte em códigos de saída específicos para monitoramento

## 6. Relação entre Entidades

**AvisoVO** (Value Object principal):
- Contém dados do título DDA e informações de contato do pagador
- Atributos: dsEmail, cpfCnpj, ddd, telefone, mensagemSms, cdTitulo, dtVencimentoTitulo, nmPagador

**Relacionamentos no Banco de Dados**:
- **TbTituloDDA** ↔ **TbControleNotificacaoTituloDDA**: relacionamento por NuCPFCNPJPagador
- **TbTituloDDA** ↔ **TbClienteDDA**: relacionamento por NuCPFCNPJPagador/NuCpfCnpjClienteDDA
- **TbTituloDDA** ↔ **TbAgregadoDDA**: relacionamento por NuCPFCNPJPagador/NuCpfCnpjAgregadoDDA
- **TbAgregadoDDA** ↔ **TbClienteDDA**: relacionamento por CdClienteDDA
- **TbClienteDDA** ↔ **VwPessoa** (DbGlobal): relacionamento por CdPessoa

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBPGF_TES..TbTituloDDA | tabela | SELECT | Títulos DDA para pagamento |
| DBPGF_TES..TbControleNotificacaoTituloDDA | tabela | SELECT | Controle de notificações pendentes de envio |
| DBPGF_TES..TbClienteDDA | tabela | SELECT | Dados cadastrais dos clientes DDA (e-mail, telefone) |
| DBPGF_TES..TbAgregadoDDA | tabela | SELECT | Relacionamento de agregados DDA |
| DbGlobal..VwPessoa | view | SELECT | Nome da pessoa/pagador |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBPGF_TES..TbControleNotificacaoTituloDDA | tabela | UPDATE | Atualiza flag de notificação pendente para 'N' e data de alteração após envio |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| log/statistics-${executionId}.log | gravação | BvDailyRollingFileAppender | Log de estatísticas do batch (framework BV) |
| log/roboEnvioAvisoDda.log | gravação | DailyRollingFileAppender | Log específico da aplicação com rotação diária |

## 10. Filas Lidas

não se aplica

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **NotificacaoTechnicalService** | SOAP/Web Service | Serviço de envio de SMS através do barramento (servicebus.bvnet.bv). Operação: enviarSms |
| **Servidor SMTP** | SMTP | Envio de e-mails através do servidor smtpduqrelay.bvnet.bv |
| **Banco de Dados Sybase** | JDBC | Acesso ao banco DBPGF_TES (servidor sybdesspb:6500) |

## 13. Avaliação da Qualidade do Código

**Nota:** 5/10

**Justificativa:**

**Pontos Positivos:**
- Estrutura bem organizada seguindo padrão Spring Batch (Reader/Processor/Writer)
- Separação de responsabilidades entre camadas (DAO, Bus, Batch)
- Uso de framework consolidado (Spring Batch)
- Tratamento de exceções com códigos de erro específicos
- Logging adequado em pontos críticos

**Pontos Negativos:**
- **Encoding inconsistente**: Comentários e strings em ISO-8859-1 causando caracteres corrompidos
- **ItemProcessor vazio**: Não agrega valor, apenas repassa o objeto
- **Lógica de negócio no Bus**: EnvioAvisoBus concentra muitas responsabilidades (deveria delegar mais)
- **SQL embutido no código**: Queries SQL hardcoded no DAO dificultam manutenção
- **Falta de validações**: Não valida dados de entrada (e-mail, telefone)
- **Tratamento genérico de exceções**: Catch de Exception genérico em vários pontos
- **Código duplicado**: Query UNION ALL poderia ser refatorada
- **Falta de testes**: Apenas um teste de integração básico
- **Dependências desatualizadas**: Uso de versões antigas de bibliotecas
- **Senha em texto claro**: Apesar de usar BVCrypto, há senhas em arquivos de configuração

## 14. Observações Relevantes

1. **Ambientes**: O sistema possui configurações para múltiplos ambientes (DES, QA, UAT, PRD) através de WSDLs específicos
2. **Segurança**: Utiliza WS-Security com UsernameToken para autenticação no serviço de SMS
3. **Auditoria**: Implementa trilha de auditoria com ticket único para rastreamento
4. **Limitações de Caracteres**: SMS limitado a 142 caracteres e nome do pagador a 14 caracteres
5. **Processamento Idempotente**: Verifica se já enviou aviso no mesmo dia antes de reenviar
6. **Framework Proprietário**: Forte dependência do framework BV (bv-framework-batch), dificultando portabilidade
7. **Versão do Projeto**: 19.4.4.P1883-1.0 indica versionamento relacionado a sprint/projeto específico
8. **Encoding**: Projeto possui problemas de encoding (ISO-8859-1 vs UTF-8) que precisam ser corrigidos