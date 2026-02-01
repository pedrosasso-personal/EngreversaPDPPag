# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch desenvolvido em Spring Batch para processamento de cancelamento de baixa de boletos através de mensagens CIP ADDA116. O sistema lê arquivos XML do padrão ADDA116RR2 (aviso a terceiros de cancelamento de baixa), processa os títulos, gera transações de devolução e envia para fila IBM MQ para integração com outros sistemas. Utiliza arquitetura hexagonal com separação clara entre domínio, portas e adaptadores.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal Spring Boot que inicializa o batch |
| **BatchConfiguration** | Configuração do job Spring Batch "jobRecebimentoCancelamentoBaixa" |
| **StepConfiguration** | Configuração do step com reader, processor e writer |
| **RecebimentoCancelamentoBaixaItemReader** | Lê arquivos ADDA116 do diretório de entrada, deserializa XML e retorna itens para processamento |
| **RecebimentoCancelamentoBaixaItemProcessor** | Processa cada título, busca baixa original nos bancos PGFT/SPAG e prepara TransacaoPagamento |
| **RecebimentoCancelamentoBaixaItemWriter** | Grava transações de devolução e envia para fila de integração |
| **RecebimentoCancelamentoBaixaService** | Serviço principal com regras de negócio: obtenção de baixas, criação de devoluções, verificação de migração |
| **TransacaoPagamento** | Entidade de domínio principal representando uma transação de pagamento |
| **GrupoADDA116RR2TitComplexType** | Classe JAXB representando um título no arquivo ADDA116 |
| **FileServerImpl** | Implementação de acesso a arquivos via protocolo SMB |
| **IntegracaoRepositoryImpl** | Envia mensagens XML para fila IBM MQ |
| **JdbiSpagRepositoryImpl** | Repositório de acesso ao banco SQL Server (SPAG) |
| **JdbiPgftRepositoryImpl** | Repositório de acesso ao banco Sybase (PGFT) |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x**
- **Spring Batch** - Framework de processamento batch
- **Spring Cloud Task** - Gerenciamento de tarefas batch
- **JDBI 3.9.1** - Acesso a banco de dados
- **Microsoft SQL Server 7.4** - Banco de dados SPAG
- **Sybase 16.3** - Banco de dados PGFT (DBPGF_TES)
- **IBM MQ 2.3.1** - Mensageria para integração
- **JAXB 2.3.1** - Binding XML/Java
- **Apache Velocity 1.7** - Template engine para geração de XML
- **jcifs 2.1.31** - Acesso a arquivos via SMB
- **Feature Toggle 0.0.4** - Controle de features
- **Kubernetes** - Orquestração de containers
- **Logback** - Framework de logging

---

## 4. Principais Endpoints REST

Não se aplica - Sistema batch sem endpoints REST expostos. Utiliza Spring Boot Actuator apenas para health checks em `/actuator/health:9090`.

---

## 5. Principais Regras de Negócio

1. **Processamento de Cancelamento de Baixa de Boletos**: Lê arquivos ADDA116RR2 contendo avisos de cancelamento de baixa de títulos DDA.

2. **Criação de Transação de Devolução**: Para cada cancelamento, cria uma transação de devolução invertendo remetente e favorecido, alterando código de liquidação para CC (Conta Corrente) e status para AGUARDANDO.

3. **Busca de Baixa Original**: Consulta a baixa original nos bancos PGFT (Sybase) ou SPAG (SQL Server) usando número de controle DDA e identificação do título.

4. **Tratamento de Migração BV→BVSA**: Verifica na tabela TbControleMigracaoParticipante se o participante foi migrado do banco BV (655) para BVSA (413) e ajusta os dados conforme necessário.

5. **Vinculação de Devolução ao Original**: Atualiza o lançamento original com o código de protocolo da devolução criada.

6. **Envio para Integração**: Envia a transação de devolução em formato XML para fila IBM MQ (QL.SPAG.SOLICITAR_PAGAMENTO_CC_REQ.INT) para processamento por outros sistemas.

7. **Controle de Feature Toggle**: Verifica flag `ft_boolean_spag_base_devolucao_cancelamento_baixa` antes de processar devoluções.

8. **Movimentação de Arquivos**: Move arquivos processados para diretório específico (processado/rejeitado) conforme resultado do processamento.

9. **Controle de Processamento**: Registra e atualiza status de processamento na tabela TbArquivoADDA com contadores de devoluções processadas.

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **TransacaoPagamento**: Entidade central contendo dados completos da transação (valores, datas, participantes, códigos)
  - Relaciona-se com **Participante** (remetente, favorecido, fintechs)
  - Contém **BaixaBoleto** (dados específicos de boleto)
  - Vincula-se a outra TransacaoPagamento via cdProtocoloDevolucao

- **BaixaBoleto**: Dados de baixa de boleto
  - Relaciona-se com **TituloPagamento** via cdTituloPagamento

- **DadosArquivoADDA**: Controle de arquivos processados
  - Rastreia quantidade de devoluções e status de processamento

- **ParticipanteMigrado**: Controle de migração de participantes entre bancos
  - Relaciona-se com **Participante** para verificar migração BV→BVSA

**Fluxo de Relacionamento:**
```
ADDA116 (XML) → GrupoADDA116RR2TitComplexType → 
BaixaBoleto (busca) → TituloPagamento → 
TransacaoPagamento (original) → TransacaoPagamento (devolução) → 
Fila IBM MQ
```

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbBaixaBoleto (SPAG) | Tabela | SELECT | Busca dados de baixa de boleto por cdTituloBaixaOperacional |
| TbTituloPagamento (SPAG) | Tabela | SELECT | Busca título de pagamento por cdTituloPagamento |
| TbTransacaoPagamento (SPAG) | Tabela | SELECT | Busca transação de pagamento original por cdLancamento |
| TbControleMigracaoParticipante (SPAG) | Tabela | SELECT | Verifica se participante foi migrado de BV para BVSA |
| TbArquivoADDA (SPAG) | Tabela | SELECT | Busca dados de arquivo ADDA já processado |
| PGFT (Sybase) - tabelas de baixa | Tabela | SELECT | Busca baixa de boleto no sistema legado via protocolo ITP |
| PGFT (Sybase) - tabelas de transação | Tabela | SELECT | Busca transação de pagamento no sistema legado |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbTransacaoPagamento (SPAG) | Tabela | INSERT | Insere nova transação de devolução via procedure PrIncluirLancamentoV2 |
| TbTransacaoPagamento (SPAG) | Tabela | UPDATE | Atualiza transação original com cdProtocoloDevolucao |
| TbArquivoADDA (SPAG) | Tabela | INSERT | Insere registro de novo arquivo ADDA processado |
| TbArquivoADDA (SPAG) | Tabela | UPDATE | Atualiza contador de devoluções processadas |
| PGFT (Sybase) - Caixa Entrada | Tabela | INSERT | Insere devolução no sistema legado via procedure BV_INCLUSAO_CAIXA_ENTRADA |
| PGFT (Sybase) - tabelas de transação | Tabela | UPDATE | Atualiza transação original com código de devolução |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| ADDA116*.xml.gz | Leitura | RecebimentoCancelamentoBaixaItemReader | Arquivos XML compactados com mensagens ADDA116RR2 de cancelamento de baixa |
| ADDA116*.xml.gz | Gravação (movimentação) | RecebimentoCancelamentoBaixaItemReader | Move arquivo para diretório "processamento" durante processamento |
| ADDA116*.xml.gz | Gravação (movimentação) | RecebimentoCancelamentoBaixaItemReader | Move arquivo para diretório "processado" após sucesso |
| ADDA116*.xml.gz | Gravação (movimentação) | RecebimentoCancelamentoBaixaItemReader | Move arquivo para diretório "rejeitado" em caso de erro |
| pagamento.xml | Geração | XMLHelper/IntegracaoRepositoryImpl | XML gerado via template Velocity para envio à fila MQ |
| logback-spring.xml | Leitura | Configuração Kubernetes | Arquivo de configuração de logs montado em /usr/etc/log |

**Diretórios configurados:**
- Entrada: `//pta-apps*/bvf-apps*/SPAG/integracao/cip/entrada`
- Processamento: `//pta-apps*/bvf-apps*/SPAG/integracao/cip/processamento`
- Processado: `//pta-apps*/bvf-apps*/SPAG/integracao/cip/processado`
- Rejeitado: `//pta-apps*/bvf-apps*/SPAG/integracao/cip/rejeitado`

---

## 10. Filas Lidas

Não se aplica - O sistema não consome mensagens de filas, apenas produz.

---

## 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Responsável | Breve Descrição |
|--------------|-----------|-------------------|-----------------|
| QL.SPAG.SOLICITAR_PAGAMENTO_CC_REQ.INT | IBM MQ | IntegracaoRepositoryImpl | Fila para envio de transações de devolução em formato XML para processamento por sistemas integrados |

**Configuração IBM MQ:**
- Queue Manager: QM.ATA.01 (des), QM.ATA.02 (qa), QM.ATA.03 (uat), QM.ATA.04 (prd)
- Channel: SPAG.SRVCONN
- Hosts: qm_ata_*.bvnet.bv:1414

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|----------------|------|-----------|
| **IBM MQ** | Mensageria | Envio de transações de devolução para fila de integração |
| **File Server SMB** | Compartilhamento de arquivos | Leitura de arquivos ADDA116 via protocolo SMB com autenticação NTLM |
| **SQL Server (DBSPAG)** | Banco de dados | Banco principal com dados de transações, boletos e controle de processamento |
| **Sybase (DBPGF_TES)** | Banco de dados legado | Sistema legado PGFT para consulta e gravação de transações antigas |
| **ConfigCat** | Feature Toggle | Controle de ativação/desativação de funcionalidades via flag remota |
| **CIP (Câmara Interbancária de Pagamentos)** | Sistema externo | Origem dos arquivos ADDA116 com avisos de cancelamento de baixa DDA |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões hexagonais (portas e adaptadores)
- Separação clara de responsabilidades entre camadas (domain, service, infra, adapter)
- Uso adequado de Spring Batch com configurações separadas e bem organizadas
- Boa cobertura de testes unitários
- Uso de enums para constantes e tipos
- Configuração externalizada (application.yml, properties)
- Uso de feature toggles para controle de funcionalidades
- Mappers dedicados para transformação de dados
- Tratamento de exceções específicas do domínio
- Documentação via código (classes JAXB bem estruturadas)

**Pontos de Melhoria:**
- Chunk size configurado como 0 (processamento item a item pode impactar performance)
- Falta de documentação JavaDoc em algumas classes críticas
- Algumas classes com múltiplas responsabilidades (ex: RecebimentoCancelamentoBaixaService)
- Poderia ter mais logs estruturados para rastreabilidade
- Ausência de retry configurado no job Kubernetes (backoffLimit=0)
- Alguns métodos longos que poderiam ser refatorados

O código demonstra maturidade técnica e boas práticas de engenharia de software, com espaço para melhorias pontuais em performance e manutenibilidade.

---

## 14. Observações Relevantes

1. **Ambiente Multi-Banco**: Sistema preparado para trabalhar com dois bancos de dados distintos (SQL Server e Sybase), refletindo processo de migração/convivência de sistemas legados.

2. **Protocolo SMB**: Utiliza protocolo SMB para acesso a file server Windows, com autenticação NTLM, indicando integração com infraestrutura corporativa tradicional.

3. **Padrão CIP**: Implementa padrão oficial da Câmara Interbancária de Pagamentos (ADDA116) para cancelamento de baixa de boletos DDA, seguindo schemas XSD do Banco Central.

4. **Processamento Síncrono**: Apesar de ser batch, o processamento é item a item (chunk size 0), priorizando controle transacional sobre performance.

5. **Migração BV→BVSA**: Sistema trata especificamente migração entre bancos do grupo (código 655 para 413), mantendo rastreabilidade via tabela de controle.

6. **Fault Tolerance**: Configuração de fault tolerance habilitada no step, mas sem retry no nível do job Kubernetes.

7. **Auditoria**: Integração com framework de auditoria (arqt.AUDIT) para rastreabilidade de operações.

8. **Múltiplos Ambientes**: Configuração completa para 4 ambientes (des, qa, uat, prd) com parametrização específica de cada um.

9. **Segurança**: Uso de secrets Kubernetes para credenciais sensíveis (MQ, file server, banco de dados).

10. **Monitoramento**: Health checks configurados via Spring Actuator na porta 9090 para liveness e readiness probes.