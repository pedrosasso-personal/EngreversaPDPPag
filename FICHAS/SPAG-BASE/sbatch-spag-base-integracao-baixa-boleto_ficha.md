# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de processamento batch desenvolvido em Spring Batch para integração de baixa de boletos. O sistema realiza a leitura de registros de pagamento de boletos de duas fontes de dados distintas (PGFT e SPAG), processa as informações de baixa operacional, transforma os dados em notificações padronizadas e publica essas notificações em um tópico do Google Cloud Pub/Sub para integração com outros sistemas. O processamento é executado em duas etapas (steps) sequenciais, uma para cada fonte de dados, com tratamento de erros e atualização de flags de controle.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal que inicializa a aplicação Spring Boot Batch |
| `BatchConfiguration` | Configuração do job batch com dois steps sequenciais |
| `StepConfiguration` | Configuração dos steps de processamento (PGFT e SPAG) |
| `BaixaBoletoReader` / `BaixaBoletoSpagReader` | Leitura dos registros de baixa de boleto das bases PGFT e SPAG |
| `BaixaBoletoProcessor` / `BaixaBoletoSpagProcessor` | Processamento e transformação dos dados de baixa |
| `BaixaBoletoWriter` / `BaixaBoletoSpagWriter` | Envio das notificações para o Pub/Sub e atualização de flags |
| `BoletoPgftService` / `BoletoSpagService` | Serviços de negócio para tratamento de boletos |
| `IntegracaoBaixaBoletoPublisherImpl` | Implementação da publicação de mensagens no Google Pub/Sub |
| `JdbiPgftRepositoryImpl` / `JdbiSpagRepositoryImpl` | Repositórios de acesso a dados usando JDBI |
| `NotificacaoBaixaBoletoMapper` | Mapeamento de entidades de baixa para notificações |
| `BaixaBoleto` | Entidade de domínio representando uma baixa de boleto |
| `NotificacaoBaixaBoleto` | Entidade de notificação para integração |

## 3. Tecnologias Utilizadas

- **Framework Principal**: Spring Boot 2.x, Spring Batch
- **Linguagem**: Java 11
- **Persistência**: JDBI 3.9.1
- **Bancos de Dados**: Sybase ASE (DBPGF_TES), Microsoft SQL Server (DBSPAG)
- **Mensageria**: Google Cloud Pub/Sub 3.1.0
- **Containerização**: Docker
- **Orquestração**: Kubernetes (Google Cloud Platform)
- **Logging**: Logback com formato JSON
- **Testes**: JUnit 5, Mockito 4.5.1
- **Build**: Maven
- **Serialização**: Jackson, Gson

## 4. Principais Endpoints REST

| Método | Endpoint | Classe | Descrição |
|--------|----------|--------|-----------|
| GET | /actuator/health | Spring Actuator | Health check da aplicação |

**Observação**: Esta é uma aplicação batch, não expõe endpoints REST de negócio, apenas endpoints de monitoramento do Spring Actuator.

## 5. Principais Regras de Negócio

1. **Filtragem de Boletos para Processamento (PGFT)**:
   - Data de movimento igual à data atual
   - Código de liquidação = 22
   - Status = 3
   - IF Remetente e Favorecido = 655 (Banco Votorantim)
   - Valor menor que R$ 250.000,00
   - Flag de notificação de baixa = 'N'
   - Baixa operacional aceita = 'S'

2. **Filtragem de Boletos para Processamento (SPAG)**:
   - Baixa operacional aceita = 'S'
   - Flag de notificação de baixa = 'N'
   - Data de processamento >= data atual
   - Possui número de referência cadastral e controle DDA
   - Banco favorecido e remetente = 655
   - Valor menor que R$ 250.000,00

3. **Geração de Código de Barras**: Transformação de linha digitável (47 dígitos) em código de barras (44 dígitos) através de reorganização posicional

4. **Formatação de CPF/CNPJ**: Adição de zeros à esquerda (11 dígitos para CPF, 14 para CNPJ)

5. **Controle de Processamento**: Atualização de flag `FlNotificacaoBaixa` para controlar registros já processados (null durante processamento, 'S' para sucesso, 'N' para erro)

6. **Tipo de Documento**: Fixado como 40 (Troca de Cobrança) para todas as notificações

7. **Processamento em Chunks**: Leitura e processamento em lotes de 500 registros

8. **Tratamento de Erros**: Em caso de falha no processamento ou publicação, o registro é marcado com flag 'N' para reprocessamento

## 6. Relação entre Entidades

**Entidades Principais:**

- **BaixaBoleto**: Entidade central contendo informações completas da baixa operacional
  - Relaciona-se com TbRegistroPagamentoCIP (registro de pagamento)
  - Relaciona-se com TbRetornoBaixaOperacionalCIP (retorno da baixa)
  - Relaciona-se com TBL_LANCAMENTO/TbLancamento (lançamento financeiro)
  - Relaciona-se com TBL_CAIXA_ENTRADA_SPB (caixa de entrada SPB) ou TbLancamentoPessoa (pessoa do lançamento)

- **NotificacaoBaixaBoleto**: Entidade de integração derivada de BaixaBoleto
  - Representa a mensagem a ser publicada no Pub/Sub
  - Contém dados normalizados para integração externa

- **RegistroPagamento**: Entidade de controle
  - Contém código do registro e flag de notificação
  - Usada para atualização de status de processamento

**Relacionamentos:**
- BaixaBoleto (1) -> (1) NotificacaoBaixaBoleto (transformação)
- BaixaBoleto (1) -> (1) RegistroPagamento (controle de processamento)

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBPGF_TES..TbRetornoBaixaOperacionalCIP | Tabela | SELECT | Retornos de baixa operacional do CIP |
| DBPGF_TES..TbRegistroPagamentoCIP | Tabela | SELECT | Registros de pagamento CIP (PGFT) |
| DBPGF_TES..TBL_LANCAMENTO | Tabela | SELECT | Lançamentos financeiros |
| DBITP..TBL_CAIXA_ENTRADA_SPB | Tabela | SELECT | Caixa de entrada do SPB |
| TbRetornoBaixaOperacionalCIP | Tabela | SELECT | Retornos de baixa operacional (SPAG) |
| TbRegistroPagamentoCIP | Tabela | SELECT | Registros de pagamento CIP (SPAG) |
| TbLancamento | Tabela | SELECT | Lançamentos (SPAG) |
| TbLancamentoPessoa | Tabela | SELECT | Pessoas relacionadas aos lançamentos |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBPGF_TES..TbRegistroPagamentoCIP | Tabela | UPDATE | Atualização do flag FlNotificacaoBaixa para controle de processamento |
| TbRegistroPagamentoCIP | Tabela | UPDATE | Atualização do flag FlNotificacaoBaixa (base SPAG) |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | Leitura | /usr/etc/log (container) | Configuração de logging em formato JSON |
| application.yml | Leitura | Classpath resources | Configurações da aplicação por ambiente |

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

## 11. Filas Geradas

| Nome da Fila/Tópico | Tecnologia | Classe Responsável | Breve Descrição |
|--------------------|------------|-------------------|-----------------|
| business-spag-base-baixa-intrabancaria | Google Cloud Pub/Sub | IntegracaoBaixaBoletoPublisherImpl | Tópico para publicação de notificações de baixa de boletos intrabancários |

**Configuração por ambiente:**
- DES: `projects/bv-spag-des/topics/business-spag-base-baixa-intrabancaria`
- UAT: `projects/bv-spag-uat/topics/business-spag-base-baixa-intrabancaria`
- PRD: `projects/bv-spag-prd/topics/business-spag-base-baixa-intrabancaria`

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|----------------|------|-----------|
| Google Cloud Pub/Sub | Mensageria | Publicação de notificações de baixa de boletos para consumo por outros sistemas |
| Banco Sybase DBPGF_TES | Banco de Dados | Leitura de registros de pagamento e baixas operacionais (sistema legado PGFT) |
| Banco SQL Server DBSPAG | Banco de Dados | Leitura de registros de pagamento e baixas operacionais (sistema SPAG) |
| Kubernetes/GCP | Infraestrutura | Execução do job batch em ambiente containerizado |

## 13. Avaliação da Qualidade do Código

**Nota: 7,5/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com uso de padrões como Repository, Service e Mapper
- Utilização adequada de Spring Batch com configuração clara de steps e chunks
- Implementação de testes unitários com boa cobertura
- Uso de JDBI para queries SQL externalizadas, facilitando manutenção
- Tratamento de erros com flags de controle para reprocessamento
- Configuração adequada para múltiplos ambientes
- Uso de Lombok para reduzir boilerplate
- Logs estruturados em JSON

**Pontos de Melhoria:**
- Duplicação de código entre as implementações PGFT e SPAG (readers, processors, writers)
- Falta de documentação JavaDoc nas classes principais
- Queries SQL complexas poderiam ser melhor documentadas
- Uso misto de Gson e Jackson (poderia padronizar)
- Tratamento de exceções genérico em alguns pontos (catch Exception)
- Falta de validações de entrada mais robustas
- Configuração de timeout hardcoded (60 segundos) no publisher
- Ausência de métricas customizadas implementadas (apesar da estrutura preparada)

## 14. Observações Relevantes

1. **Arquitetura Dual**: O sistema processa dados de duas fontes distintas (PGFT - Sybase e SPAG - SQL Server) em steps separados, mas com lógica similar, sugerindo uma possível consolidação futura.

2. **Processamento Batch Diário**: Baseado nas queries SQL, o sistema processa boletos do dia atual, indicando execução diária agendada.

3. **Limite de Valor**: Existe um limite de R$ 250.000,00 para processamento de boletos, provavelmente por questões regulatórias ou de alçada.

4. **Controle de Reprocessamento**: O sistema utiliza flags para evitar reprocessamento e permitir retry em caso de falhas.

5. **Ambiente Cloud Native**: Aplicação preparada para execução em Kubernetes no GCP, com configurações específicas para cada ambiente.

6. **Exit Code Customizado**: Implementação de `BatchExitCodeGenerator` para retornar códigos de saída apropriados para orquestração Kubernetes.

7. **Segurança**: Senhas e credenciais são gerenciadas via secrets do Kubernetes e variáveis de ambiente.

8. **Monitoramento**: Integração com Spring Actuator para health checks, essencial para liveness e readiness probes no Kubernetes.

9. **Padrão de Nomenclatura**: Prefixo "sbatch" indica Spring Batch, "spag" indica o domínio (Sistema de Pagamentos), "base" indica camada base/comum.

10. **Versionamento**: Projeto na versão 0.11.0, indicando ainda em fase de evolução/estabilização.