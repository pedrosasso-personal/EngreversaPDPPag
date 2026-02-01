---
## Ficha Técnica do Sistema

### 1. Descrição Geral
Sistema atômico Spring Boot responsável pela geração de relatórios bancários do Banco Digital Votorantim. O sistema processa requisições síncronas via REST e assíncronas via Google Cloud PubSub para gerar documentos em PDF (cartas de encerramento, extratos, consultas de saldo) e arquivos OFX (extrato bancário). Também realiza verificação automática de divergências de saldo entre apurações históricas e movimentações, enviando notificações por email quando detectadas inconsistências.

---

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `RelatoriosController` | Exposição de endpoints REST para geração de relatórios |
| `PubSubListener` | Consumo de mensagens de exportação de extrato via PubSub |
| `SaldoDivergenteListener` | Consumo de mensagens para verificação de saldo divergente |
| `ExtratoService` | Orquestração da geração e exportação de extratos (PDF/OFX) |
| `CartaEncerramentoService` | Preparação de dados para cartas de encerramento |
| `NotificaSaldoDivergenteService` | Verificação de divergências e envio de notificações |
| `VerificaSaldoDivergenteService` | Regra de negócio para cálculo e comparação de saldos |
| `GeradorJasper` | Compilação de templates JRXML e geração de PDFs via JasperReports |
| `ArquivoExtratoPDFRepositoryImpl` | Geração de extrato em formato PDF |
| `ArquivoExtratoOFXRepositoryImpl` | Geração de extrato em formato OFX (XML bancário) |
| `ContaCorrenteRepositoryImpl` | Consulta de saldo atual via JDBI |
| `HistoricoSaldoRepositoryImpl` | Consulta de histórico de saldos apurados |
| `MovimentacaoRepositoryImpl` | Consulta de movimentações bancárias (histórico + dia) |

---

### 3. Tecnologias Utilizadas
- **Framework:** Spring Boot 2.4.x
- **Mensageria:** Google Cloud PubSub 1.2.8
- **Banco de Dados:** Sybase ASE (via Sybase JConnect 16.3)
- **Acesso a Dados:** JDBI 3.12.0
- **Geração de Relatórios:** JasperReports 6.3.0
- **Mapeamento de Objetos:** MapStruct 1.5.5
- **Segurança:** OAuth2/JWT (Spring Security)
- **Serialização:** Gson, JAXB (para OFX)
- **Observabilidade:** Prometheus Metrics, Logback (JSON logging)
- **Build:** Maven, JDK 11
- **Infraestrutura:** Google Cloud Platform (GKE)

---

### 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/relatorios/encerramento` | `RelatoriosController` | Gera carta de encerramento de conta (3 cenários: demanda banco, efetivação, demanda cliente) |
| POST | `/v1/relatorios/consulta/historicoconta` | `RelatoriosController` | Gera PDF com histórico de saldos da conta por data de apuração |
| POST | `/v1/relatorios/consulta/contasativasinativas` | `RelatoriosController` | Gera PDF com relatório de contas ativas/inativas |
| POST | `/v1/relatorios/consulta/contassemmovsaldo` | `RelatoriosController` | Gera PDF com relatório de contas sem movimentação e saldo zero |
| POST | `/v1/relatorios/extrato` | `RelatoriosController` | Gera extrato bancário em PDF com movimentações e saldo resumido |

---

### 5. Principais Regras de Negócio

1. **Geração de Cartas de Encerramento:** Sistema valida combinação de iniciativa (BANCO/CLIENTE/EMERGENCIAL) e etapa (DEMANDA/EFETIVACAO) para determinar tipo de carta a ser gerada (3 templates JasperReports distintos).

2. **Cálculo de Saldo Disponível:** `saldoDisponivel = (vrSaldoTotal + vrLimiteContaCorrente) - (vrSaldoBloqueio + vrSaldoIndisponivel)`

3. **Verificação de Saldo Divergente:** 
   - Busca data de apuração D-1 (2 dias passados)
   - Calcula: `saldoCalculado = vrSaldoHistorico + totalMovimentacao - saldoBloqueado`
   - Compara `saldoCalculado` vs `saldoAtual`
   - Movimentações: soma créditos (C), subtrai débitos (D)
   - Envia email notificação se divergência detectada

4. **Formatação de Extrato:** Calcula saldo acumulado iterativo para cada lançamento (débito reduz, crédito aumenta).

5. **Exportação Assíncrona:** Sistema suporta exportação de extrato em múltiplos formatos (PDF/OFX) via mensageria, enviando resultado por email.

6. **Validação de Dados de Entrada:** Validação obrigatória de campos (banco, conta, agência, tipo conta, endereço, titulares) para cartas de encerramento.

---

### 6. Relação entre Entidades

```
Conta (1) ----< (N) Titulares
Conta (1) ----< (N) HistoricoSaldo (por data apuração)
Conta (1) ----< (N) Movimentacao (histórico + dia)
Conta (1) ----< (N) SaldoBloqueado

Extrato agrega:
  - HistoricoSaldo (saldo inicial período)
  - Movimentacao (lançamentos período)
  - SaldoBloqueado (bloqueios judiciais)
  - ContaCorrente (saldo atual, limite)

CartaEncerramento compõe:
  - Endereco (logradouro, cidade, UF, CEP)
  - Titulares[] (nome, documento)
  - Conta (agência, número, tipo, modalidade)
```

---

### 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbConta (DBCONTACORRENTE) | Tabela | SELECT | Consulta saldo total, limite, saldo bloqueado e indisponível da conta |
| TbHistoricoSaldo | Tabela | SELECT | Consulta histórico de saldos apurados por data (vrSaldoTotal, vrSaldoBloqueio, vrSaldoIndisponivel, vrLimiteContaCorrente) |
| TbHistoricoMovimento | Tabela | SELECT | Consulta movimentações históricas da conta (data efetivação, valor, tipo operação) |
| TbMovimentoDia | Tabela | SELECT | Consulta movimentações do dia atual (complementa histórico) |
| TbSaldoBloqueado | Tabela | SELECT | Consulta soma de bloqueios ativos (CdMotivoDesbloqueio=0) |
| TbControleData | Tabela | SELECT | Consulta data de movimento 2 dias passados (DtMovimento2DiasPassado) |

---

### 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema realiza apenas operações de leitura (SELECT/READ) no banco de dados.

---

### 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `*.jrxml` (templates JasperReports) | Leitura | `GeradorJasper` | Templates de relatórios (cartas encerramento, extrato, histórico conta, consultas) |
| `*.jasper` (compilados) | Leitura | `GeradorJasper` | Templates pré-compilados JasperReports |
| `logo_principal_impresso.gif` | Leitura | Templates Jasper | Logo Banco Votorantim para cabeçalho relatórios |
| `logo_voto_financas.gif` | Leitura | Templates Jasper | Logo Voto Finanças para relatórios |
| `saldo_resumido.jpg` | Leitura | Template extrato | Imagem decorativa saldo resumido |
| PDF (cartas/extratos/consultas) | Gravação | `GeradorJasper`, `ArquivoExtratoPDFRepositoryImpl` | Relatórios gerados em formato PDF (retornados como Base64) |
| OFX (extrato bancário) | Gravação | `ArquivoExtratoOFXRepositoryImpl` | Arquivo XML padrão OFX para importação em sistemas financeiros (retornado como Base64) |

---

### 10. Filas Lidas

| Nome da Fila | Tecnologia | Classe Consumidora | Descrição |
|--------------|------------|-------------------|-----------|
| `business-ccbd-base-exportar-extrato-sub` | Google Cloud PubSub | `PubSubListener` | Recebe solicitações de exportação de extrato (PDF/OFX) para envio por email |
| `business-ccbd-base-verifica-saldo-divergente-sub` | Google Cloud PubSub | `SaldoDivergenteListener` | Recebe solicitações de verificação de divergência de saldo entre contas |

**Configuração:** Ambas filas utilizam `AckMode.MANUAL` (confirmação manual de mensagens) e são condicionais à propriedade `spring.cloud.gcp.pubsub.enabled=true`.

---

### 11. Filas Geradas

| Nome da Fila | Tecnologia | Classe Produtora | Descrição |
|--------------|------------|------------------|-----------|
| `business-ccbd-base-envio-email` | Google Cloud PubSub | `EnviarMensagemTopicoEnvioEmailExtratoRepositoryImpl`, `NotificaSaldoDivergenteService` | Publica mensagens para envio de emails contendo extratos (PDF/OFX) ou notificações de saldo divergente |

**Observação:** Sistema adiciona `ticket` do MDC nos headers das mensagens para rastreabilidade.

---

### 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Google Cloud PubSub | Mensageria | Comunicação assíncrona para exportação de extratos e verificação de saldos |
| Sybase ASE (DBCONTACORRENTE) | Banco de Dados | Consulta de dados transacionais de contas correntes, saldos, movimentações |
| JasperReports Engine | Biblioteca | Geração de relatórios PDF a partir de templates JRXML |
| OAuth2/JWT Provider | Autenticação | Validação de tokens JWT para endpoints REST (Spring Security OAuth2 Resource Server) |

---

### 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de camadas (controller, service, repository, domain)
- Uso adequado de design patterns (Strategy para tipos de extrato, Builder, Mapper)
- Exception handling centralizado via `@ControllerAdvice`
- Uso de enums para constantes e configurações
- Cobertura de testes unitários presente
- Configuração externalizada via properties
- Uso de MapStruct para conversão de objetos (reduz boilerplate)

**Pontos de Melhoria:**
- Classes de serviço com muitas responsabilidades (`ExtratoService` poderia ser refatorado)
- Métodos com muitos parâmetros (ex: preparação de dados Jasper)
- Dependência forte de JasperReports (migração seria complexa)
- Versões antigas de bibliotecas com potenciais vulnerabilidades (iText 2.1.7, Log4j 2.20.0 - verificar CVEs)
- Falta de documentação inline em alguns métodos complexos
- Alguns code smells: classes grandes, acoplamento temporal em validações
- Configuração de datasource poderia usar pool de conexões mais robusto (HikariCP)

---

### 14. Observações Relevantes

1. **Arquitetura Multi-Módulo:** Projeto Maven dividido em `application`, `domain` e `common` para melhor organização.

2. **Feature Flags:** Verificação de saldo divergente pode ser habilitada/desabilitada via propriedade `spring.bv.saldodivergente.enable`.

3. **Processamento Assíncrono:** Sistema utiliza callbacks assíncronos para publicação PubSub, mantendo contexto MDC entre threads.

4. **Segurança PDF:** PDFs gerados com criptografia (`encrypted=true`) e permissões restritas (`allowedPermissions=PRINTING`).

5. **Formato OFX:** Sistema gera extrato no padrão OFX (Open Financial Exchange) para integração com softwares de gestão financeira.

6. **Auditoria:** Integração com biblioteca `trilha-auditoria-web` do Banco Votorantim para rastreamento de operações.

7. **Observabilidade:** Métricas Prometheus expostas, logs estruturados em JSON via Logback.

8. **Infraestrutura:** Deploy em Google Kubernetes Engine (GKE) com configuração de probes (liveness/readiness).

9. **Isolamento Transacional:** Consultas de movimentação utilizam `isolation level 0` (READ UNCOMMITTED) para evitar locks.

10. **Ack Manual:** Listeners PubSub confirmam mensagens manualmente, sempre (mesmo em caso de erro), para evitar reprocessamento infinito.

11. **Compilação Dinâmica:** Templates JasperReports são compilados em runtime se não encontrados pré-compilados.

12. **Vulnerabilidades Potenciais:** Recomenda-se atualização de dependências (Log4j, iText) e análise de segurança (OWASP Dependency Check).

---