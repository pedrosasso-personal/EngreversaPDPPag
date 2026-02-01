# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema responsável pelo processamento de cancelamento de baixas de títulos DDA (Débito Direto Autorizado) para destinatários. A aplicação consome mensagens do tipo DDA0116R2 via Google Cloud Pub/Sub, valida a existência da baixa e do título no banco de dados Sybase, e executa o procedimento de cancelamento através de stored procedure, atualizando o valor do título e a situação da baixa.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal de inicialização da aplicação Spring Boot |
| `CancelamentoBaixaListener` | Listener que consome mensagens da fila Pub/Sub e orquestra o processamento |
| `CancelamentoBaixaDestinatariaService` | Serviço de domínio que coordena a lógica de negócio do cancelamento |
| `TituloDdaRepository` | Interface de repositório para operações relacionadas a títulos DDA |
| `TituloBaixaDdaRepository` | Interface de repositório para operações relacionadas a baixas de títulos |
| `TituloDdaJdbi` | Interface JDBI para acesso ao banco de dados de títulos |
| `TituloBaixaDdaJdbi` | Interface JDBI para acesso ao banco de dados de baixas |
| `Titulo` | Entidade de domínio representando um título DDA |
| `TituloBaixa` | Entidade de domínio representando uma baixa de título |
| `Dda116R2Representation` | Representação da mensagem DDA0116R2 recebida via Pub/Sub |

## 3. Tecnologias Utilizadas

- **Framework Principal**: Spring Boot 2.x (baseado no parent pom-atle-base-sboot-atom-parent 1.1.5)
- **Linguagem**: Java 11+
- **Gerenciador de Dependências**: Maven 3.8+
- **Banco de Dados**: Sybase ASE (driver jconn4 versão 16.3-SP03-PL07)
- **Acesso a Dados**: JDBI 3.9.1
- **Mensageria**: Google Cloud Pub/Sub (Spring Cloud GCP 1.2.8.RELEASE)
- **Mapeamento de Objetos**: MapStruct
- **Documentação API**: OpenAPI 3.0 / Swagger
- **Segurança**: Spring Security OAuth2 Resource Server (JWT)
- **Logging**: Logback
- **Utilitários**: Lombok, Jackson (com JavaTimeModule)
- **Trilha de Auditoria**: Framework Atlante Base (br.com.bancobv.atle.base.trilha.auditoria)
- **Pool de Conexões**: HikariCP

## 4. Principais Endpoints REST

Não se aplica. O sistema é orientado a eventos (event-driven), consumindo mensagens de filas Pub/Sub. Não há endpoints REST de negócio expostos, apenas endpoints de infraestrutura (actuator, swagger).

## 5. Principais Regras de Negócio

1. **Validação de Baixa**: Antes de cancelar, o sistema verifica se existe uma baixa ativa (FlAtivo = 'S') para o número de identificação informado
2. **Validação de Título**: Verifica se o título DDA existe no sistema antes de processar o cancelamento
3. **Recálculo de Valor**: Ao cancelar a baixa, o sistema soma o valor da baixa ao valor atual do título, restaurando o saldo
4. **Atualização de Situação**: A situação do título é atualizada conforme informado na mensagem DDA0116R2
5. **Processamento Idempotente**: Mensagens que não encontram baixa ou título geram exceção `ResourceNotFoundException` e são confirmadas (ack) para evitar reprocessamento infinito
6. **Tratamento de Erros**: Erros de negócio (ResourceNotFoundException) são logados e a mensagem é confirmada; outros erros não confirmam a mensagem para permitir retry
7. **Filtragem de Mensagens**: Apenas mensagens contendo "DDA0116R2" são processadas pelo listener

## 6. Relação entre Entidades

**Entidades Principais:**

- **Titulo**: Representa um título DDA no sistema
  - Atributos: cdTitulo (Long), valor (BigDecimal)
  
- **TituloBaixa**: Representa uma baixa operacional de título
  - Atributos: cdTitulo (Long), valor (BigDecimal)
  - Relacionamento: N:1 com Titulo (uma baixa pertence a um título)

**Relacionamento:**
```
Titulo (1) ----< (N) TituloBaixa
```

Um título pode ter múltiplas baixas operacionais ao longo do tempo. O cancelamento de uma baixa restaura o valor ao título original.

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBPGF_TES..TbTituloDDABaixaOperacional | Tabela | SELECT | Consulta baixas operacionais ativas de títulos DDA pelo número de identificação |
| DBPGF_TES..TbTituloDDA | Tabela | SELECT | Consulta informações do título DDA (código e valor/saldo atual) |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBPGF_TES..TbTituloDDABaixaOperacional | Tabela | UPDATE/DELETE | Atualizada via stored procedure PrCancelarTituloDDABaixaOperacional para cancelar a baixa |
| DBPGF_TES..TbTituloDDA | Tabela | UPDATE | Atualizada via stored procedure para restaurar o valor do título e atualizar a situação |

**Nota**: As atualizações são realizadas através da stored procedure `DBPGF_TES..PrCancelarTituloDDABaixaOperacional` que recebe os parâmetros: nuIdentificacaoBaixa, DtHoraBaixa, cdTitulo, valor (recalculado) e situacaoBaixa.

## 9. Arquivos Lidos e Gravados

Não se aplica. O sistema não realiza leitura ou gravação de arquivos físicos. Todo o processamento é baseado em mensagens e banco de dados.

## 10. Filas Lidas

| Nome da Fila | Tecnologia | Breve Descrição |
|--------------|-----------|-----------------|
| receive-dda0116r2-sub (local) / ${GCP_DDA116R2_SUB} (des/uat/prd) | Google Cloud Pub/Sub | Fila de recebimento de mensagens DDA0116R2 contendo solicitações de cancelamento de baixa de títulos destinatários |

**Configuração:**
- **Channel**: `recebimento-dda0116-r2-channel`
- **Modo de Confirmação**: MANUAL
- **Polling**: Fixed delay de 100ms
- **Block on Pull**: true
- **Payload Type**: String (JSON)

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas, apenas consome.

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Breve Descrição |
|-----------------|------|-----------------|
| Google Cloud Pub/Sub | Mensageria | Consumo de mensagens DDA0116R2 para processamento de cancelamento |
| Sybase ASE (DBPGF_TES) | Banco de Dados | Consulta e atualização de títulos e baixas DDA |
| OAuth2 Resource Server | Segurança | Validação de tokens JWT para autenticação (issuer e jwks configuráveis por ambiente) |
| Framework Atlante | Auditoria | Trilha de auditoria para registro de operações (integração via DefinidorBusinessAction) |

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo princípios de Clean Architecture (separação clara entre domain, infrastructure, repository, service)
- Uso adequado de padrões como Repository, Mapper e DTO/Representation
- Configuração modular e organizada (separação de beans por responsabilidade)
- Tratamento de exceções apropriado com distinção entre erros de negócio e técnicos
- Uso de Lombok reduzindo boilerplate
- Queries SQL externalizadas em arquivos separados (boa prática JDBI)
- Configuração por perfis (local, des, uat, prd) bem estruturada
- Logging adequado em pontos estratégicos

**Pontos de Melhoria:**
- Falta de testes unitários implementados (arquivos de teste existem mas não foram fornecidos)
- Classe `DefinidorBusinessActionCustom` possui lógica de exemplo não relacionada ao domínio (verifica "cliente" mas o sistema trata de títulos)
- Ausência de validações de entrada na `Dda116R2Representation`
- Falta documentação JavaDoc em algumas classes importantes
- Configuração de retry/timeout poderia ser mais explícita
- Ausência de métricas customizadas de negócio

## 14. Observações Relevantes

1. **Arquitetura Event-Driven**: Sistema totalmente orientado a eventos, sem exposição de APIs REST de negócio
2. **Processamento Assíncrono**: Utiliza polling com delay fixo de 100ms para consumo de mensagens
3. **Idempotência**: Implementa estratégia de ack manual para controle fino de reprocessamento
4. **Multi-ambiente**: Configuração preparada para 4 ambientes (local, des, uat, prd) com variáveis de ambiente
5. **Segurança**: Implementa autenticação via JWT mesmo sendo um sistema de processamento assíncrono
6. **Emulador Local**: Suporte a emulador Pub/Sub local (localhost:8085) para desenvolvimento
7. **Pool de Conexões**: Configurado com máximo de 10 conexões e timeout de 5 minutos
8. **Stored Procedure**: Lógica crítica de cancelamento delegada ao banco via SP `PrCancelarTituloDDABaixaOperacional`
9. **Framework Corporativo**: Utiliza parent POM do framework Atlante Base do Banco Votorantim
10. **Monitoramento**: Endpoints de health, metrics e prometheus expostos na porta 9090