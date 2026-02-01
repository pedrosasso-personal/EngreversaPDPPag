# Ficha Técnica do Sistema

## sbatch-spag-base-retorno-baixa-contigencia

---

### 1. Descrição Geral

Sistema batch Spring Boot desenvolvido para processar arquivos de retorno de baixa de boletos em contingência do SPAG (Sistema de Pagamentos). O sistema consome arquivos XML no formato ADDA114 (padrão CIP - Câmara Interbancária de Pagamentos) disponibilizados em fileserver SMB, realiza validações de negócio, persiste informações de confirmação ou rejeição de baixas no banco de dados Sybase e publica eventos para sistemas downstream via GCP Pub/Sub. Opera em modo batch puro, sem interface web, sendo acionado por scheduler externo via parâmetros de job.

---

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Entry point da aplicação batch Spring Boot |
| `Reader` | Lê arquivos XML ADDA114 compactados (gzip) do fileserver SMB usando protocolo JCIFS |
| `Processor` | Implementa processamento passthrough (sem transformação) no pipeline batch |
| `ContigenciaRetWriter` | Writer do Spring Batch responsável por persistir dados e publicar eventos no Pub/Sub |
| `ContigenciaService` | Orquestra validações de negócio, persistência em banco de dados e publicação de mensagens |
| `XMLHelper` | Realiza unmarshalling de arquivos XML ADDA114 usando JAXB/Jakarta com schema XSD BCB |
| `FileServerImpl` | Implementa acesso ao fileserver SMB via JCIFS com autenticação NTLM |
| `RetornoBaixaContigenciaMapper` | Converte tipos CIP (ADDA114) para objetos de domínio da aplicação |
| `ArquivoCompensacao` | Entidade JPA representando arquivo de compensação processado |
| `DetalheArquivoCompensacao` | Entidade JPA representando detalhes individuais de títulos no arquivo |

---

### 3. Tecnologias Utilizadas

- **Framework Base:** Spring Boot 2.7.5, Spring Batch (chunk-oriented processing)
- **Persistência:** JPA/Hibernate, Sybase ASE (DBPGF_TES), H2 (metadados batch)
- **Transações:** Atomikos JTA (transações distribuídas dual datasource)
- **Mensageria:** GCP Pub/Sub via Atlante Sidecar (porta 8081)
- **Integração Arquivos:** JCIFS 2.1.31 (protocolo SMB/CIFS)
- **Parsing XML:** JAXB/Jakarta XML Binding com schemas XSD BCB versão 9.3.0
- **Build:** Maven, Java 11 (JDK 11)
- **Containerização:** Docker multi-stage build
- **Logging:** Logback com formato JSON estruturado e MDC
- **Observabilidade:** Spring Boot Actuator (porta 9090)
- **Testes:** JUnit 5, Mockito
- **Bibliotecas Auxiliares:** Guava 32.1.3, Lombok, Apache Tomcat Embed 9.0.104

---

### 4. Principais Endpoints REST

Não se aplica. 

O sistema é uma aplicação batch pura sem endpoints de negócio. Disponibiliza apenas endpoints de gerenciamento via Spring Boot Actuator na porta 9090:
- `/actuator/health` - Health check para probes Kubernetes
- `/actuator/info` - Informações da aplicação

---

### 5. Principais Regras de Negócio

1. **Validação de Arquivo Duplicado:** Verifica se arquivo de retorno já foi processado ou está em processamento. Arquivos com sufixo `_ERR` ou já processados são rejeitados com `SkipFileException`.

2. **Parsing XML Contingência:** Processa arquivos XML compactados (gzip) no formato ADDA114 com encoding UTF-16BE seguindo schema XSD CIP versão 9.3.0.

3. **Separação Títulos Aceitos/Recusados:** Classifica títulos em aceitos (`TitActo`) e recusados (`TitRecsd`) baseado em códigos de erro retornados pela câmara.

4. **Atualização Status Arquivo:** Define status do `ArquivoCompensacao` como RECEBIDO (código 12) para arquivos processados com sucesso ou REJEITADO (código 5) para arquivos com erro.

5. **Atualização Status Detalhe:** Atualiza `DetalheArquivoCompensacao` com status CONFIRMADO (código 6) para títulos aceitos ou REJEITADO (código 5) para títulos recusados, usando `NumCtrlReqPart` como chave de correlação.

6. **Publicação Evento Downstream:** Publica evento JSON no tópico GCP Pub/Sub `business-spag-base-contingencia-baixa-boleto` com timestamp UTC para cada título processado, incluindo campo `numIdentcBaixa` como chave de deduplicação.

7. **Movimentação Arquivos:** Move arquivos processados para diretórios específicos: `/entrada/temp/` durante processamento, `/entrada/processado/` para sucesso, `/entrada/rejeitado/` para erro.

8. **Chunk Processing:** Processa registros em lotes de 100 itens (chunk size fixo) para otimização de performance e controle transacional.

---

### 6. Relação entre Entidades

**Modelo de Dados:**

```
ArquivoCompensacao (1) ----< (N) DetalheArquivoCompensacao
```

**Entidades:**

- **ArquivoCompensacao:** Representa o arquivo de retorno CIP processado
  - PK: `cdArquivoCompensacao`
  - Atributos principais: `cdTipoArquivo` (8 para contingência), `nome`, `cdStatusCompensacao`

- **DetalheArquivoCompensacao:** Representa cada título individual dentro do arquivo
  - PK: `cdDetalheArquivoCompensacao`
  - FK: `cdArquivoCompensacao` (relacionamento N:1 com ArquivoCompensacao)
  - Atributos principais: `cdLancamentoTesouraria`, `NumCtrlReqPart` (chave negócio), `cdStatusCompensacao`

**Relacionamento:** Um arquivo de compensação contém múltiplos detalhes (títulos), estabelecendo relação 1:N através da chave estrangeira `cdArquivoCompensacao`.

---

### 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbArquivoCompensacao | Tabela | SELECT | Consulta arquivos de compensação por tipo (8=contingência) e nome para validar duplicidade |
| TbDetalheArquivoCompensacao | Tabela | SELECT | Consulta detalhes por código de lançamento tesouraria e arquivo compensação para correlação com retorno CIP |

---

### 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbArquivoCompensacao | Tabela | UPDATE | Atualiza status compensação (12=RECEBIDO ou 5=REJEITADO) após processamento do arquivo |
| TbDetalheArquivoCompensacao | Tabela | UPDATE | Atualiza status compensação (6=CONFIRMADO ou 5=REJEITADO) para cada título processado |

**Observação:** Utiliza transações JTA distribuídas via Atomikos para garantir consistência entre Sybase (dados negócio) e H2 (metadados Spring Batch).

---

### 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `ADDA114_*_RET` | Leitura | `Reader` / `FileServerImpl` | Arquivos XML compactados (gzip) com retornos CIP no formato ADDA114, lidos do fileserver SMB em `{FILESERVER}{DIRETORIO_ARQUIVOS}/entrada/` |
| `ADDA114_*_ERR` | Leitura | `Reader` / `ContigenciaService` | Arquivos de erro identificados e rejeitados durante validação inicial |
| Arquivos processados | Gravação/Movimentação | `FileServerImpl` | Movimentação para `/entrada/temp/` (processamento), `/entrada/processado/` (sucesso) ou `/entrada/rejeitado/` (erro) |
| `spreadsheet.csv` | Leitura | Testes | Arquivo CSV de teste com 999 registros fictícios (nome, email, data_nasc, idade, id) |

**Padrão de Nomenclatura:** `ADDA114_{cdArquivo}_RET` para retornos válidos, `ADDA114_{cdArquivo}_ERR` para arquivos com erro.

**Localização Fileserver:** `//pta-apps{env}.bvnet.bv/bvf-apps*/SPAG/integracao/cip` com autenticação NTLM.

---

### 10. Filas Lidas

Não se aplica.

O sistema não consome mensagens de filas. Opera exclusivamente em modo batch processando arquivos do fileserver.

---

### 11. Filas Geradas

| Nome da Fila/Tópico | Tecnologia | Classe Responsável | Breve Descrição |
|--------------------|------------|-------------------|-----------------|
| `business-spag-base-contingencia-baixa-boleto` | GCP Pub/Sub | `ContigenciaRetWriter` / `ContigenciaService` | Tópico para publicação de eventos de retorno de baixa de contingência em formato JSON |

**Detalhes da Publicação:**
- **Provider:** GCP (Google Cloud Platform)
- **Project ID:** Configurável via `{GCP_SPAG_PROJECT_ID}`
- **Formato Payload:** JSON com estrutura `RetornoBaixaContigencia`
- **Campos Principais:** `codMsg`, `numCtrlPart`, `numIdentcBaixa` (chave deduplicação), timestamp UTC
- **Integração:** Via Atlante Sidecar na porta 8081

---

### 12. Integrações Externas

| Sistema/Serviço | Tipo | Protocolo/Tecnologia | Breve Descrição |
|-----------------|------|---------------------|-----------------|
| Fileserver SMB Corporativo | Armazenamento | SMB/CIFS via JCIFS 2.1.31 | Acesso a arquivos XML ADDA114 em `//pta-apps{env}.bvnet.bv/bvf-apps*/SPAG/integracao/cip` com autenticação NTLM |
| Sybase ASE (DBPGF_TES) | Banco de Dados | JDBC (jConnect 16.3) | Persistência de dados de compensação e baixa de contingência, usuário `lgettRoboItpConsulta`, portas específicas por ambiente |
| GCP Pub/Sub | Mensageria | HTTP/gRPC via Atlante Sidecar | Publicação de eventos de retorno de baixa para sistemas downstream, porta 8081 |
| CIP (Câmara Interbancária) | Padrão Dados | XML Schema XSD 9.3.0 | Formato padronizado ADDA114 para retornos de baixa de boletos |

**Configurações por Ambiente:**
- **Desenvolvimento (des):** Portas e hosts específicos configurados via `application-des.yml`
- **Homologação (uat):** Configurações em `application-uat.yml`
- **Produção (prd):** Configurações em `application-prd.yml`
- **Credenciais:** Gerenciadas via cofre de senhas (`cofre_senha.*`)

---

### 13. Avaliação da Qualidade do Código

**Nota:** 8/10

**Justificativa:**

**Pontos Positivos:**
- **Arquitetura bem estruturada:** Separação clara de responsabilidades em camadas (config, domain, helper, mapper, service) seguindo boas práticas Spring
- **Uso adequado de padrões:** Implementação correta do Spring Batch com processamento chunk-oriented, otimizando performance e controle transacional
- **Testes automatizados:** Cobertura de testes unitários com JUnit 5 e Mockito para camadas críticas
- **Logging estruturado:** Implementação de logs JSON com MDC facilitando rastreabilidade e observabilidade
- **Tratamento de exceções específico:** Exceções customizadas (`SkipFileException`, `FileServerException`) para diferentes cenários de erro
- **Configuração externalizada:** Múltiplos perfis (des/uat/prd) com configurações específicas por ambiente
- **Versionamento de schemas:** XSD CIP versionado (9.3.0) garantindo compatibilidade com padrão bancário
- **Transações distribuídas:** Uso correto de Atomikos JTA para garantir consistência entre múltiplos datasources

**Pontos de Melhoria:**
- **Uso de Reflection:** Extração de códigos de erro via reflection em atributos ADDA114 pode impactar performance e dificultar manutenção; poderia ser substituído por mapeamento explícito
- **Chunk size fixo:** Valor hardcoded (100) poderia ser parametrizável para ajuste fino por ambiente
- **Documentação inline:** Código poderia se beneficiar de mais comentários JavaDoc em métodos complexos
- **Startup lento:** Initial delay de 420s para liveness probe indica possível otimização no tempo de inicialização

O código demonstra maturidade técnica e aderência a padrões corporativos, com espaço para otimizações pontuais que não comprometem a qualidade geral da solução.

---

### 14. Observações Relevantes

1. **Acionamento do Job:** Sistema requer scheduler externo para disparo, recebendo parâmetro `JobParameters[arquivo]` indicando qual arquivo processar.

2. **Probes Kubernetes:** Configuração de liveness probe com initial delay de 420 segundos (7 minutos) indica tempo de startup significativo, possivelmente devido a inicialização de conexões e carga de schemas.

3. **Segurança:** SecurityContext JWT desabilitado por se tratar de batch interno sem exposição externa.

4. **Padrão Arquitetural:** Segue Chassis Atlante, padrão corporativo Banco Votorantim para aplicações cloud-native na plataforma Google.

5. **CI/CD:** Pipeline automatizado via Jenkins conforme `jenkins.properties`.

6. **Schemas XSD Embedded:** Arquivos `ADDA114.xsd` e `ADDATIPOS.xsd` embarcados como resources para validação offline, reduzindo dependências externas.

7. **Chave de Deduplicação:** Campo `numIdentcBaixa` serve como chave de negócio para deduplicação em sistemas downstream que consomem eventos Pub/Sub.

8. **Encoding Específico:** Arquivos XML processados em UTF-16BE conforme padrão CIP/BCB.

9. **Vulnerabilidades Corrigidas:** Versões atualizadas de Guava (32.1.3) e Tomcat Embed (9.0.104) para correção de vulnerabilidades de segurança conhecidas.

10. **Dados de Teste:** Arquivo `spreadsheet.csv` com 999 registros fictícios para testes de carga e validação de pipeline batch.

---

**Documento gerado em:** 2024
**Versão do Sistema:** Spring Boot 2.7.5 / Java 11
**Ambiente:** Multi-ambiente (Desenvolvimento, Homologação, Produção)