# Ficha Técnica do Sistema

## 1. Descrição Geral
O sistema **sboot-spbb-base-atom-integracao** é um serviço atômico desenvolvido em Java com Spring Boot para integração de mensagens do Sistema de Pagamentos Brasileiro (SPB). O sistema processa mensagens LTR (Liquidação de Transferências de Reservas), mensagens PAG (Pagamentos) e STR (Sistema de Transferência de Reservas), realizando validações, atualizações de saldo, replicação de movimentos e integração com o sistema legado SPB.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application.java` | Classe principal de inicialização do Spring Boot |
| `IntegracaoLtrController` | Controlador REST para receber mensagens LTR (LTR0002, LTR0004, LTR0008) |
| `ProcessarMensagemCoreController` | Controlador REST para processar mensagens do core SPB |
| `SPBLegadoController` | Controlador REST para validação de mensagens SPB |
| `SPBLegadoReplicaController` | Controlador REST para atualização de réplicas SPB |
| `IntegracaoLtrService` | Serviço de negócio para processamento de mensagens LTR |
| `ProcessarMensagemCoreService` | Serviço de negócio para processamento de mensagens core (PAG/STR) |
| `ValidarMensagemService` | Serviço de validação de mensagens (circuit break, saldo, replicação) |
| `SPBLegadoService` | Serviço para atualização de réplicas no sistema legado |
| `FeatureToggleService` | Serviço para gerenciamento de feature flags |
| `IntegracaoLtrRepositoryImpl` | Implementação de acesso a dados para mensagens LTR |
| `ProcessarMensagemCoreRepositoryImpl` | Implementação de acesso a dados para processamento core |
| `SPBLegadoRepositoryImpl` | Implementação de acesso a dados para sistema legado |

## 3. Tecnologias Utilizadas
- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Spring Security OAuth2** (autenticação e autorização)
- **JDBI 3.9.1** (acesso a banco de dados)
- **Sybase jConnect 16.3** (driver de banco de dados)
- **Swagger/OpenAPI 3.0** (documentação de APIs)
- **MapStruct 1.6.3** (mapeamento de objetos)
- **Jackson** (serialização/deserialização JSON)
- **Logback** (logging em formato JSON)
- **Spring Actuator** (monitoramento e métricas)
- **Prometheus** (métricas)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **ConfigCat** (feature toggle)

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/mensagensLTR0002` | `IntegracaoLtrController` | Recebe e processa mensagens LTR0002 |
| POST | `/v1/mensagensLTR0004` | `IntegracaoLtrController` | Recebe e processa mensagens LTR0004 |
| POST | `/v1/mensagensLTR0008` | `IntegracaoLtrController` | Recebe e processa mensagens LTR0008 |
| POST | `/processarMensagemCore` | `ProcessarMensagemCoreController` | Processa mensagens do core SPB (PAG/STR R1/R2/E) |
| POST | `/validar-mensagem` | `SPBLegadoController` | Valida mensagens SPB (circuit break, saldo, replicação) |
| PUT | `/spb-legado/replica` | `SPBLegadoReplicaController` | Atualiza registros de réplica no sistema legado |

## 5. Principais Regras de Negócio
- **Validação de Circuit Break**: Verifica se o circuit break está ativo antes de processar mensagens
- **Validação de Saldo de Reserva**: Valida se há saldo suficiente na conta reserva para operações de débito
- **Processamento de Mensagens LTR**: Insere mensagens LTR no banco, atualiza status e débito/crédito
- **Processamento de Mensagens Core**: Processa mensagens PAG/STR (R1, R2 e E - erro) com atualização de saldo
- **Replicação de Movimentos**: Replica movimentos para o sistema legado quando feature toggle ativa
- **Validação de Instituição**: Valida código COMPE e ISPB das instituições
- **Tratamento de Erros**: Registra erros de processamento na tabela C_erms_112
- **Validação de Duplicidade**: Verifica se movimento já existe antes de replicar
- **Mapeamento Dinâmico**: Mapeia diferentes tipos de mensagens (PAG0107-0151, STR0004-0052) para domínios específicos

## 6. Relação entre Entidades
- **MensagemLtr**: Entidade de domínio para mensagens LTR (LTR0002, LTR0004, LTR0008)
- **MensagemLtrProc**: Entidade processada de mensagens LTR com dados adicionais
- **ProcessarMensagemDomain**: Entidade para processamento de mensagens core
- **AtualizaSaldoDomain**: Entidade com dados para atualização de saldo (mais de 150 campos)
- **ReplicacaoMensagemDomain**: Entidade para replicação de movimentos no legado
- **SaldoReserva**: Entidade com informações de saldo e flag de operação
- **ValidarMensagemRequest**: Entidade de requisição para validação
- **ProcessarMensagemCoreResponse**: Entidade de resposta com status do processamento

**Relacionamentos principais:**
- MensagemLtr → MensagemLtrProc (transformação para processamento)
- ValidarMensagemRequest → ProcessarMensagemDomain → AtualizaSaldoDomain (fluxo de validação e processamento)
- ProcessarMensagemDomain → ReplicacaoMensagemDomain (fluxo de replicação)

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| tb_inst_instituicao | tabela | SELECT | Busca ID da instituição por CNPJ |
| tb_usua_usuario | tabela | SELECT | Busca ID do usuário por sigla do sistema |
| tb_mvlr_movimento_LTR | tabela | SELECT | Busca número de controle IF por ID do movimento |
| tb_movi_movimento | tabela | SELECT | Consulta movimento por ISPB e header |
| tb_cz_rese_stre | tabela | SELECT | Verifica se circuit break está ativo |
| tb_rese_reserva | tabela | SELECT | Obtém saldo de reserva da instituição |
| tb_ispb_ispb | tabela | SELECT | Relaciona ISPB com instituição |
| tb_oper_operacao | tabela | SELECT | Obtém flag de operação (débito/crédito) |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| tb_movi_movimento | tabela | INSERT/UPDATE | Insere e atualiza movimentos SPB |
| tb_mvlr_movimento_LTR | tabela | INSERT/UPDATE | Insere e atualiza movimentos LTR |
| C_erms_112 | tabela | INSERT | Registra erros de processamento |
| (via stored procedures) | tabela | UPDATE | Atualiza status, débito/crédito e saldo via procedures |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot | Configurações da aplicação |
| application-local.yml | leitura | Spring Boot | Configurações ambiente local |
| logback-spring.xml | leitura | Logback | Configuração de logs em JSON |
| swagger/yaml_spbb.yml | leitura | OpenApiConfiguration | Especificação OpenAPI das APIs |
| *.sql (resources) | leitura | JDBI | Queries SQL para stored procedures |

## 10. Filas Lidas
não se aplica

## 11. Filas Geradas
não se aplica

## 12. Integrações Externas
- **Banco de Dados Sybase (DBISPB/DBITP)**: Integração principal com banco legado SPB via JDBI e stored procedures
- **API Gateway OAuth2**: Autenticação e autorização via JWT (apigateway.bvnet.bv)
- **ConfigCat**: Serviço de feature toggle para controle de funcionalidades
- **Biblioteca sbootlib-spbb-base-mensageria-spb**: Conversão de mensagens SPB entre JSON e Java
- **Prometheus**: Exportação de métricas de monitoramento

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**
**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões hexagonais (domain, application, infrastructure)
- Separação clara de responsabilidades entre controllers, services e repositories
- Uso adequado de padrões de projeto (Strategy para mappers, Builder para DTOs)
- Tratamento de exceções customizado e estruturado
- Configuração adequada de logs em formato JSON
- Uso de feature toggles para controle de funcionalidades
- Documentação OpenAPI/Swagger bem definida

**Pontos de Melhoria:**
- Classe `AtualizaSaldoDomain` com mais de 150 campos (God Object antipattern)
- Classe `ProcessarMensagemCoreService` muito extensa com múltiplas responsabilidades
- Uso excessivo de mapas estáticos para mapeamento de tipos de mensagem
- Falta de testes unitários nos arquivos enviados
- Alguns métodos muito longos que poderiam ser refatorados
- Uso de `isNull`/`nonNull` poderia ser substituído por Optional em alguns casos
- Comentários de código desabilitado em alguns lugares
- Sanitização de logs poderia ser mais consistente

## 14. Observações Relevantes
- O sistema utiliza **JDBI** ao invés de JPA/Hibernate, chamando stored procedures diretamente
- Há suporte para múltiplos tipos de mensagens SPB (PAG0107-0151, STR0004-0052) com mappers específicos
- O sistema implementa **replicação condicional** de movimentos baseada em feature toggle
- Utiliza **circuit break** como mecanismo de proteção contra sobrecarga
- Validação de saldo é feita apenas para operações de débito
- O sistema processa mensagens em três formatos: R1 (requisição), R2 (resposta) e E (erro)
- Configurações específicas por ambiente (des, uat, prd) gerenciadas via ConfigMap e Secrets
- Deployment em Kubernetes com probes de liveness e readiness configurados
- Uso de cache de certificados Java montado via volume
- Integração com LDAP para autenticação (configuração global)