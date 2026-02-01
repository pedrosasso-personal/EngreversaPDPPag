# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-spag-base-atom-controle-port** é um serviço atômico desenvolvido em Java com Spring Boot, responsável pelo controle e consolidação de arquivos de portabilidade de salário. O sistema atua como intermediário entre a CIP (Câmara Interbancária de Pagamentos) e os sistemas internos do Banco Votorantim, processando solicitações, confirmações, recusas e cancelamentos de portabilidade salarial. Ele consome mensagens de filas RabbitMQ, consolida informações em banco de dados MySQL e envia notificações por e-mail em caso de erros.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal que inicializa a aplicação Spring Boot |
| **ConfirmacaoPortabilidadeListener** | Listener que consome mensagens de confirmação/recusa e cancelamento de portabilidade |
| **SolicitacaoPortabilidadeListener** | Listener que consome mensagens de solicitação de portabilidade e retornos de cancelamento |
| **ConfirmacaoPortabilidadeServiceImpl** | Implementa a lógica de negócio para consolidação de confirmações e cancelamentos |
| **SolicitacaoPortabilidadeService** | Implementa a lógica de negócio para consolidação de solicitações e tratamento de erros |
| **ControlePortRepositoryImpl** | Repositório para operações de controle de arquivos de portabilidade |
| **PortabilidadeRepositoryImpl** | Repositório para operações de portabilidade |
| **ArquivoPortabilidadeMapper** | Mapeia DTOs para entidades de arquivo de portabilidade |
| **PortabilidadeMapper** | Mapeia DTOs para entidades de portabilidade |
| **AppProperties** | Configurações de propriedades da aplicação (filas, exchanges, etc.) |

---

## 3. Tecnologias Utilizadas

- **Java 11** (OpenJ9)
- **Spring Boot 2.x**
- **Spring AMQP** (RabbitMQ)
- **JDBI 3.9.1** (acesso a banco de dados)
- **MySQL 8.0.22** (banco de dados)
- **Lombok** (redução de boilerplate)
- **Swagger/OpenAPI 3.0** (documentação de API)
- **Micrometer/Prometheus** (métricas)
- **Grafana** (visualização de métricas)
- **Docker** (containerização)
- **Maven** (gerenciamento de dependências)
- **JUnit 5 + Mockito** (testes)
- **JavaMailSender** (envio de e-mails)

---

## 4. Principais Endpoints REST

Não se aplica. O sistema não expõe endpoints REST para consumo externo. Trata-se de um serviço orientado a eventos (event-driven) que consome mensagens de filas RabbitMQ.

---

## 5. Principais Regras de Negócio

1. **Consolidação de Solicitações de Portabilidade**: Processa solicitações recebidas da CIP, validando e persistindo informações de portabilidade no banco de dados.

2. **Tratamento de Aceite de Portabilidade**: Atualiza o status de portabilidades aceitas, associando o número único CIP (nuUnicoCip) à solicitação.

3. **Consolidação de Confirmações e Recusas**: Processa confirmações ou recusas de portabilidade, atualizando o status e motivo no banco de dados.

4. **Tratamento de Erros de Arquivo**: Identifica arquivos com erro (sufixo _ERR), consulta portabilidades relacionadas, envia para fila de retorno e notifica por e-mail.

5. **Processamento de Cancelamentos**: Consolida cancelamentos de portabilidade, atualizando status e enviando para filas apropriadas.

6. **Notificação de Erros por E-mail**: Envia e-mails para equipe técnica quando erros são detectados em arquivos da CIP.

7. **Controle de Status de Arquivos**: Mantém controle de status dos arquivos processados (ENVIADO, FALHA_ENVIO, FINALIZADO, AGUARDANDO_AJUSTE, REJEITADO).

8. **Distinção entre Heap e Non-Heap**: Diferencia tratamento de portabilidades em andamento (heap) e erros não tratados (non-heap).

---

## 6. Relação entre Entidades

**PortabilidadeEntity**: Representa uma portabilidade de salário com informações de cliente, bancos, empregador e situação.

**ArquivoPortabilidadeEntity**: Representa o controle de arquivos processados, vinculado a uma portabilidade.

**Relacionamento**: Uma portabilidade (PortabilidadeEntity) pode ter múltiplos registros de controle de arquivo (ArquivoPortabilidadeEntity), representando diferentes etapas do processamento (solicitação, aceite, confirmação, erro, etc.).

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbPortabilidade | Tabela | SELECT | Consulta portabilidades por NSU ou NUC |
| TbDominioArquivo | Tabela | SELECT | Consulta domínio e descrição de erros |
| TbControleArquivoPortabilidade | Tabela | SELECT | Consulta controle de arquivos de portabilidade |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbPortabilidade | Tabela | INSERT | Insere nova solicitação de portabilidade |
| TbPortabilidade | Tabela | UPDATE | Atualiza status, NUC, motivo de portabilidade |
| TbControleArquivoPortabilidade | Tabela | INSERT | Insere registro de controle de arquivo processado |
| TbControleArquivoPortabilidade | Tabela | UPDATE | Atualiza status e data de recebimento de arquivos |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| APCS101 | Leitura | SolicitacaoPortabilidadeListener | Arquivo de solicitação de portabilidade |
| APCS101RET | Leitura | SolicitacaoPortabilidadeListener | Arquivo de retorno de solicitação |
| APCS101ERR | Leitura | SolicitacaoPortabilidadeListener | Arquivo de erro de solicitação |
| APCS104 | Leitura | ConfirmacaoPortabilidadeListener | Arquivo de confirmação/recusa |
| APCS105 | Leitura | ConfirmacaoPortabilidadeListener | Arquivo de cancelamento |
| logback-spring.xml | Leitura | Configuração de logs | Configuração de logging da aplicação |

---

## 10. Filas Lidas

- **events.business.SPAG-BASE.solicitacao.arq.portabilidade.cip**: Solicitações de portabilidade da CIP
- **events.business.SPAG-BASE.confirmacao.arq.portabilidade.cip**: Confirmações/recusas de portabilidade
- **events.business.SPAG-BASE.cancelamento.arq.portabilidade.cip**: Cancelamentos de portabilidade
- **events.business.SPAG-BASE.retorno.cancelamento.arq.portabilidade.cip**: Retornos de cancelamento com erro

---

## 11. Filas Geradas

- **events.business.SPAG-BASE.retorno.solicitacao.portabilidade.cip**: Retorno de solicitações com erro
- **events.business.SPAG-BASE.retorno.cancelamento.portabilidade.cip**: Retorno de cancelamentos com erro

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| CIP (Câmara Interbancária de Pagamentos) | Mensageria | Recebe arquivos de portabilidade via RabbitMQ |
| MySQL (SPAGArquivoPortabilidade) | Banco de Dados | Persiste informações de portabilidade e controle |
| SMTP Relay | E-mail | Envia notificações de erro para equipe técnica |
| Prometheus/Grafana | Monitoramento | Expõe métricas de aplicação |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades (domain, application, infrastructure)
- Uso adequado de padrões como Repository, Mapper e DTO
- Cobertura de testes unitários presente
- Uso de Lombok para reduzir boilerplate
- Configuração externalizada (application.yml)
- Documentação Swagger/OpenAPI

**Pontos de Melhoria:**
- Métodos muito extensos em `SolicitacaoPortabilidadeService` (ex: `consolidarSolicitacaoPortabilidadeErro`)
- Lógica de negócio complexa misturada com tratamento de exceções
- Uso de constantes mágicas (ex: `STATUS_EM_CANCELAMENTO = 13`)
- Falta de documentação JavaDoc em classes e métodos críticos
- Tratamento genérico de exceções em alguns pontos (`catch (Exception ex)`)
- Código comentado em testes (ApplicationTest, PortabilidadeMapperTest)
- Alguns métodos privados poderiam ser extraídos para classes auxiliares

---

## 14. Observações Relevantes

1. **Arquitetura Hexagonal**: O projeto segue princípios de arquitetura hexagonal com separação clara entre domain, application e infrastructure.

2. **Processamento Assíncrono**: Todo processamento é orientado a eventos via RabbitMQ, sem endpoints REST síncronos.

3. **Ambientes Múltiplos**: Configurações específicas para ambientes local, des, qa, uat e prd.

4. **Monitoramento**: Integração com Prometheus e Grafana para observabilidade.

5. **Containerização**: Dockerfile e docker-compose configurados para execução em containers.

6. **Pipeline CI/CD**: Configuração Jenkins presente (jenkins.properties).

7. **Notificação de Erros**: Sistema envia e-mails automáticos para equipe técnica quando detecta erros em arquivos da CIP.

8. **Tratamento de Arquivos ERR**: Lógica específica para processar arquivos com sufixo _ERR, identificando portabilidades relacionadas e notificando stakeholders.

9. **HikariCP**: Utiliza pool de conexões HikariCP para gerenciamento eficiente de conexões com banco de dados.

10. **Profiles Spring**: Utiliza profiles para diferenciar comportamento entre ambientes (local, des, qa, uat, prd).