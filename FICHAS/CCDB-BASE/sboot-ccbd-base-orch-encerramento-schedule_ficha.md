---
## Ficha Técnica do Sistema

### 1. Descrição Geral
Sistema agendado (schedule) desenvolvido em Spring Boot para processar automaticamente o encerramento de contas bancárias por desinteresse comercial ou ocorrências imediatas. Executa diariamente via cron job (segunda a sexta-feira às 7h) e utiliza Apache Camel para orquestração de fluxos complexos envolvendo múltiplas integrações com APIs REST e WebServices SOAP. O sistema coordena todo o ciclo de encerramento: consulta de contas pendentes, liberação de bloqueios, transferência de saldos, exclusão de chaves PIX, remoção de DDA/DXC e confirmação final do encerramento.

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ScheduledTask** | Job agendado (cron) que dispara a execução do serviço de encerramento |
| **EncerramentoScheduleController** | Controlador REST para execução manual do processo de encerramento |
| **EncerramentoContaServiceImpl** | Serviço principal que coordena todo o fluxo de encerramento via rotas Camel |
| **CamelContextWrapper** | Wrapper do contexto Apache Camel responsável por gerenciar as rotas de orquestração |
| **EncerramentoRouter** | Rota Camel principal que orquestra o fluxo completo de encerramento |
| **BloqueioRouter** | Rota Camel para consultar, incluir e liberar bloqueios de conta |
| **ChavePixRouter** | Rota Camel para exclusão de chaves PIX (listar, cancelar portabilidade, excluir) |
| **ContaCorrenteRouter** | Rota Camel para consulta e alteração de situação cadastral de contas |
| **GlobalRouter** | Rota Camel para consulta de dados cadastrais do cliente |
| **TransferenciaRouter** | Rota Camel para efetivação de transferências TED/TEF |
| **DDARouter** | Rota Camel para verificação e exclusão de DDA |
| **DXCRouter** | Rota Camel para exclusão de dados DXC |
| **TokenRouter** | Rota Camel para geração de tokens OAuth (BV/BVSA) |
| **EncerramentoContaRepositoryImpl** | Repositório para API de listagem e confirmação de encerramentos |
| **ContaCorrenteRepositoryImpl** | Repositório para API de consulta e alteração de conta corrente |
| **BloqueioRepositoryImpl** | Repositório para API de bloqueios de movimentações |
| **ChavePixRepositoryImpl** | Repositório para API DICT PIX |
| **TransferenciaRepositoryImpl** | Repositório para API de transferências |
| **GlobalRepositoryImpl** | Repositório para API de dados cadastrais |
| **DDARepositoryImpl** | Repositório para WebService SOAP de DDA |
| **DXCRepositoryImpl** | Repositório para API de exclusão DXC |
| **TokenRepositoryImpl** | Repositório para API de geração de tokens |
| **ApplicationConfiguration** | Configuração de beans para clients de APIs externas |

### 3. Tecnologias Utilizadas
- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Maven** (gerenciamento de dependências e build)
- **Apache Camel 3.2.0** (orquestração de rotas e integração)
- **RestTemplate** (cliente HTTP para APIs REST)
- **Apache CXF** (cliente SOAP para DDA)
- **Swagger/OpenAPI Codegen** (geração de código a partir de especificações)
- **Lombok** (redução de boilerplate)
- **Jackson** (serialização/deserialização JSON)
- **OAuth2/JWT** (segurança e autenticação)
- **Spring Actuator** (monitoramento e métricas)
- **Prometheus** (coleta de métricas)
- **Grafana** (visualização de métricas)
- **Docker Compose** (orquestração de containers para monitoramento)
- **ArchUnit 0.19.0** (testes de arquitetura)

### 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/encerramento-conta/desinteresse-imediatas/encerrar | EncerramentoScheduleController | Execução manual do processo de encerramento de contas |

### 5. Principais Regras de Negócio
1. **Listagem de Contas Pendentes**: Consulta contas com demanda de encerramento por motivos específicos (cliente, desinteresse comercial, ocorrências imediatas)
2. **Validação de Estado**: Consulta estado da conta corrente e dados cadastrais do cliente antes de iniciar o processo
3. **Liberação de Bloqueios**: Remove bloqueios existentes de crédito e débito para permitir movimentações finais
4. **Transferência de Saldo**: Se saldo > 0, altera situação para "em encerramento", transfere saldo para conta balde específica do banco (BV ou BVSA) e retorna situação para ativa
5. **Exclusão de Chaves PIX**: Remove todas as chaves PIX associadas à conta, cancelando portabilidades pendentes
6. **Verificação e Exclusão DDA**: Verifica existência de DDA ativo e realiza exclusão se necessário
7. **Exclusão de Dados DXC**: Remove dados DXC associados à conta
8. **Confirmação Final**: Confirma o encerramento da demanda no sistema de encerramento
9. **Tratamento de Erros Críticos**: Em caso de falhas críticas durante o processo, inclui bloqueio de débito na conta para evitar movimentações indevidas
10. **Suporte Multi-Banco**: Processa encerramentos para dois bancos distintos (BV - códigos 161/655 e BVSA - códigos 436/413) com tokens OAuth separados

### 6. Relação entre Entidades
O sistema trabalha com as seguintes entidades principais e seus relacionamentos:

- **Conta Corrente**: Entidade central do processo, possui situação cadastral, saldo, bloqueios e está associada a um cliente
- **Cliente**: Possui dados cadastrais consultados via API Global
- **Bloqueio**: Relacionamento N:1 com Conta Corrente, pode ser de crédito ou débito
- **Chave PIX**: Relacionamento N:1 com Conta Corrente, pode ter portabilidade pendente
- **Transferência**: Operação que move saldo da conta a ser encerrada para conta balde
- **DDA**: Relacionamento 1:1 opcional com Conta Corrente
- **DXC**: Dados relacionados à conta que devem ser excluídos
- **Demanda de Encerramento**: Entidade que registra a solicitação de encerramento com motivo específico

**Fluxo de Relacionamentos**:
Demanda de Encerramento → Conta Corrente → Cliente (dados cadastrais)
Conta Corrente → Bloqueios (N)
Conta Corrente → Chaves PIX (N)
Conta Corrente → DDA (0..1)
Conta Corrente → DXC (0..1)
Conta Corrente → Transferência → Conta Balde

### 7. Estruturas de Banco de Dados Lidas
não se aplica

**Observação**: O sistema não acessa diretamente estruturas de banco de dados. Todas as operações são realizadas através de APIs REST e WebServices SOAP que encapsulam o acesso aos dados.

### 8. Estruturas de Banco de Dados Atualizadas
não se aplica

**Observação**: O sistema não atualiza diretamente estruturas de banco de dados. Todas as operações de escrita são realizadas através de APIs REST e WebServices SOAP que encapsulam as operações de persistência.

### 9. Arquivos Lidos e Gravados
não se aplica

**Observação**: O sistema não realiza operações diretas de leitura ou gravação de arquivos. Toda a comunicação é feita via APIs REST e WebServices SOAP. Logs são gerenciados pelo framework Logback/Spring Boot.

### 10. Filas Lidas
não se aplica

### 11. Filas Geradas
não se aplica

### 12. Integrações Externas

| Sistema/API | Tipo | Protocolo | Descrição |
|-------------|------|-----------|-----------|
| **sboot-ccbd-base-atom-conta-corrente** | API REST | HTTP/REST | Consulta estado da conta, situação cadastral e operações de encerramento |
| **sboot-ccbd-base-atom-movimentacoes** | API REST | HTTP/REST | Gerenciamento de bloqueios de conta (consulta, inclusão, liberação) |
| **sboot-glob-base-atom-cliente-dados-cadastrais** | API REST | HTTP/REST | Consulta de dados cadastrais do cliente (API Global) |
| **sboot-spag-base-orch-transferencias** | API REST | HTTP/REST | Efetivação de transferências TED/TEF/DOC para contas balde |
| **sboot-ccbd-orch-encerramento** | API REST | HTTP/REST | Confirmação de demanda de encerramento |
| **sboot-spag-pixx-orch-chaves-dict** | API REST | HTTP/REST | Gestão de chaves PIX (listagem, cancelamento de portabilidade, exclusão) |
| **sboot-cart-base-orch-encerramento-conta-dxc** | API REST | HTTP/REST | Exclusão de dados DXC associados à conta |
| **ddaClienteAtacadoBusinessService** | WebService | SOAP | Consulta e exclusão de DDA (Débito Direto Autorizado) |
| **Auth OAuth/JWT (BV)** | API REST | HTTP/REST | Geração de tokens de autenticação para Banco Votorantim (códigos 161/655) |
| **Auth OAuth/JWT (BVSA)** | API REST | HTTP/REST | Geração de tokens de autenticação para BVSA (códigos 436/413) |

**Observações sobre Integrações**:
- Todas as APIs REST utilizam autenticação OAuth2/JWT
- Tokens são gerados separadamente para BV e BVSA
- Sistema implementa tratamento robusto de erros com retry e fallback
- Logs são sanitizados para segurança (remoção de dados sensíveis)

### 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- **Arquitetura bem estruturada**: Separação clara em camadas (application, domain, infrastructure) seguindo princípios de Clean Architecture
- **Uso adequado de Apache Camel**: Orquestração complexa de múltiplas integrações de forma elegante e manutenível através de rotas
- **Padrões de projeto**: Implementação de Repository Pattern, Service Layer e uso de DTOs para comunicação entre camadas
- **Tratamento de erros robusto**: Implementação de rollback parcial com bloqueio de débito em casos de falha crítica
- **Configuração externalizada**: Uso de profiles para diferentes ambientes (DES, QA, UAT, PRD)
- **Observabilidade**: Integração com Prometheus e Grafana para monitoramento, uso de Spring Actuator
- **Testes de arquitetura**: Uso de ArchUnit para garantir conformidade com padrões arquiteturais
- **Documentação**: Presença de README e configurações bem documentadas
- **Segurança**: Logs sanitizados, uso de OAuth2/JWT para autenticação

**Pontos de Melhoria:**
- **Ausência de código-fonte completo**: A análise foi baseada em resumos, não sendo possível avaliar detalhes de implementação como qualidade de testes unitários, cobertura de código e complexidade ciclomática
- **Documentação técnica**: Poderia haver mais documentação inline (Javadoc) e diagramas de sequência para facilitar onboarding de novos desenvolvedores
- **Possível acoplamento**: Múltiplas integrações podem gerar acoplamento; seria interessante avaliar uso de circuit breakers e bulkheads para maior resiliência

### 14. Observações Relevantes

1. **Agendamento**: O sistema executa automaticamente de segunda a sexta-feira às 7h da manhã via cron job configurado no ScheduledTask

2. **Multi-Banco**: Suporta processamento para dois bancos distintos (BV e BVSA) com configurações e tokens OAuth separados

3. **Contas Balde**: Transferências de saldo são direcionadas para contas balde específicas de cada banco antes do encerramento final

4. **Motivos de Encerramento**: Processa três tipos de motivos:
   - CLIENTE (código 9): Solicitação do próprio cliente
   - DESINTERESSE (código 13): Desinteresse comercial do banco
   - IMEDIATAS (código 14): Ocorrências que exigem encerramento imediato

5. **Tipos de Conta Suportados**: CC (Conta Corrente), CT (Conta Poupança), CI (Conta Investimento), IF (Investimento Fixo), PP (Poupança Programada), entre outros

6. **Recursos Computacionais**: Configurado para rodar em ambiente Kubernetes/OpenShift com:
   - CPU: 150m (mínimo) a 1 core (máximo)
   - Memória: 1GB (mínimo) a 2GB (máximo)

7. **Portas de Comunicação**:
   - 8080: Swagger/API REST
   - 9090: Spring Actuator (métricas e health checks)
   - 9060: Prometheus (coleta de métricas)
   - 3000: Grafana (visualização de métricas)

8. **Execução Manual**: Além do agendamento automático, o sistema permite execução manual via endpoint REST para casos excepcionais ou testes

9. **Tecnologia de Build**: Maven com parent POM arqt-base-master-springboot:2.0.5, seguindo padrões corporativos do Banco Votorantim

10. **Versionamento**: Versão atual 0.10.0, indicando que o sistema está em evolução contínua

11. **Profiles de Teste**: Suporta múltiplos tipos de testes (unit, integration, functional, architecture) através de profiles Maven

12. **Organização**: Desenvolvido e mantido pelo Banco Votorantim, módulo CCBD (Conta Corrente Banco Digital)