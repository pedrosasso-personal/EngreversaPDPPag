# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sbatch-spag-base-gerar-lote-contabil** é um componente batch desenvolvido em Spring Batch para geração de lotes contábeis. Seu objetivo principal é processar lançamentos contábeis (tanto de bancos quanto de empresas), consolidá-los e gerar arquivos no formato específico para integração com o sistema contábil Softpar. O sistema realiza a leitura de parametrizações, consulta lançamentos contábeis em um período definido, consolida os valores, vincula os lançamentos a lotes e grava arquivos formatados em um servidor de arquivos (file server).

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal de inicialização da aplicação Spring Boot com Spring Batch habilitado |
| **JobConfig** | Configuração dos jobs e steps do Spring Batch, incluindo datasources (H2 e MySQL) e transações |
| **Reader** | ItemReader responsável por buscar parametrizações de arquivos contábeis e validar dias úteis |
| **Processor** | ItemProcessor que processa cada arquivo, busca controle de lote e consolida lançamentos contábeis |
| **Writer** | ItemWriter que formata e grava os arquivos contábeis no file server e atualiza status de processamento |
| **ArquivoIntegracaoContabilService** | Serviço para gerenciar parametrizações de arquivos de integração contábil (banco e empresa) |
| **LancamentoContabilService** | Serviço para buscar, vincular e consolidar lançamentos contábeis |
| **ControleLoteArquivoService** | Serviço para gerenciar controle de lotes de arquivos contábeis |
| **FileWritingService** | Serviço para gravação de arquivos em servidor SMB/CIFS |
| **ClientService** | Serviço para integração com API de calendário para validação de dias úteis |
| **GatewayOAuthService** | Serviço para obtenção e gerenciamento de tokens OAuth2 do API Gateway |
| **ArquivoFormatter** | Utilitário para formatação de arquivos contábeis no layout específico (276 caracteres) |

---

## 3. Tecnologias Utilizadas

- **Java 21**
- **Spring Boot 3.x** (baseado no parent pom-atle-base-sbatch-parent 3.3.0)
- **Spring Batch** (processamento batch)
- **Spring Data JPA / Hibernate** (persistência)
- **MySQL Connector** (banco de dados principal)
- **H2 Database** (banco em memória para metadados do Spring Batch)
- **OpenFeign** (cliente HTTP para APIs REST)
- **Lombok** (redução de boilerplate)
- **Jackson** (serialização/deserialização JSON)
- **JCIFS** (acesso a file server SMB/CIFS)
- **Logback** (logging com formato JSON)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Swagger/OpenAPI** (documentação de APIs)

---

## 4. Principais Endpoints REST

Não se aplica. Este é um componente batch que não expõe endpoints REST próprios. A aplicação é executada via linha de comando ou agendamento, recebendo parâmetros via JobParameters do Spring Batch.

---

## 5. Principais Regras de Negócio

1. **Validação de Dia Útil**: O sistema consulta uma API de calendário para determinar se a data de referência é dia útil e obter o dia útil anterior e próximo.

2. **Geração de Lote Suplementar**: Se a data de referência não for dia útil e houver mais de 2 dias entre o dia útil anterior e o próximo, gera-se um lote suplementar.

3. **Parametrização por Tipo de Gerador**: O sistema suporta dois tipos de geração de arquivos:
   - **Banco (B)**: Gera arquivo consolidado por banco
   - **Empresa (E)**: Gera arquivos individuais por empresa/veículo legal contábil

4. **Controle de Lote**: Para cada entidade (banco ou empresa) e data de referência, mantém-se um controle de lote sequencial que é incrementado a cada processamento.

5. **Consolidação de Lançamentos**: Os lançamentos contábeis são consolidados por evento contábil, agrupando débitos e créditos, somando valores.

6. **Vinculação de Lançamentos ao Lote**: Após consolidação, os lançamentos são vinculados ao número do lote gerado para rastreabilidade.

7. **Formatação de Arquivo**: Os arquivos são gerados em formato texto com layout fixo de 276 caracteres por linha, contendo cabeçalho e detalhes.

8. **Tratamento de Histórico e Complemento**: O sistema alterna entre histórico e complemento de histórico dependendo do tipo de gerador (banco ou empresa).

9. **Validação de Entidade**: Para bancos específicos (BV SA - 413), utiliza-se agência e empresa diferentes das demais.

10. **Status de Processamento**: Os arquivos passam por status: 1 (inicial), 2 (em processamento), 3 (finalizado).

---

## 6. Relação entre Entidades

**Principais Entidades e Relacionamentos:**

- **ArquivoIntegracaoContabil**: Representa a parametrização de um arquivo contábil a ser gerado
  - Relaciona-se com **VeiculoLegalContabil** (quando tipo gerador é Empresa)
  - Contém código de banco, filial, lote, data de referência

- **ControleLoteArquivo**: Controla a sequência de lotes por entidade e data
  - Relaciona-se com entidade (banco ou empresa) via código

- **LancamentoContabil**: Representa um lançamento contábil individual
  - Relaciona-se com **EventoContabil** ou **EventoEmpresa** via código de evento
  - Contém valor, data de movimento, contas correntes, bancos

- **EventoContabil**: Define eventos contábeis para bancos
  - Contém contas contábeis de débito e crédito
  - Relaciona-se com **VeiculoLegalContabil**

- **EventoEmpresa**: Define eventos contábeis para empresas
  - Contém contas contábeis de débito e crédito
  - Relaciona-se com **VeiculoLegalContabil** e conta corrente

- **VeiculoLegalContabil**: Representa empresas/entidades legais
  - Contém CNPJ, conta corrente matriz, código de empresa

**Relacionamento Textual:**
```
ArquivoIntegracaoContabil 1--* VeiculoLegalContabil (quando tipo E)
ControleLoteArquivo *--1 Entidade (Banco ou VeiculoLegalContabil)
LancamentoContabil *--1 EventoContabil (para bancos)
LancamentoContabil *--1 EventoEmpresa (para empresas)
EventoContabil *--1 VeiculoLegalContabil
EventoEmpresa *--1 VeiculoLegalContabil
```

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbArquivoIntegracaoContabil | Tabela | SELECT | Parametrizações de arquivos contábeis a serem gerados |
| TbVeiculoLegalContabil | Tabela | SELECT | Empresas/veículos legais associados à geração contábil |
| TbControleLoteArquivo | Tabela | SELECT | Controle de sequência de lotes por entidade e data |
| TbLancamentoContabil | Tabela | SELECT | Lançamentos contábeis individuais para consolidação |
| TbEventoContabil | Tabela | SELECT | Eventos contábeis de bancos com contas débito/crédito |
| TbEventoEmpresa | Tabela | SELECT | Eventos contábeis de empresas com contas débito/crédito |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| TbArquivoIntegracaoContabil | Tabela | INSERT/UPDATE | Inserção de novas parametrizações e atualização de status de processamento |
| TbControleLoteArquivo | Tabela | INSERT/UPDATE | Inserção de novos controles de lote e incremento de número de lote |
| TbLancamentoContabil | Tabela | UPDATE | Vinculação de lançamentos ao número do lote gerado |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| MV90{MMDD}_{LOTE}{BANCO}.DAT | Gravação | FileWritingService / Writer | Arquivo contábil formatado para integração com Softpar, gravado em servidor SMB/CIFS |

**Padrão do nome do arquivo:**
- MV90: Prefixo fixo
- MMDD: Mês e dia da data de referência
- LOTE: Número do lote (4 dígitos)
- BANCO: Código sequencial do banco
- Extensão: .DAT

**Local de gravação:** Configurado via propriedade `spag.fileserver.path` (ex: `//pta-appsdes.bvnet.bv/bvf-appsdes/SPAG/contabil`)

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

---

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas.

---

## 12. Integrações Externas

| Sistema/API | Tipo | Descrição |
|-------------|------|-----------|
| **API de Calendário** | REST (Feign) | Consulta para validação de dias úteis, obtenção de dia útil anterior e próximo. Endpoint: `/v1/calendario/verificar-dia-util/{referenceDate}/{format}/{square}/{previousBusinessDay}/{nextBusinessDay}` |
| **API Gateway OAuth** | REST | Obtenção de token JWT para autenticação nas chamadas à API de Calendário. Endpoint configurado via `gateway.tokenURL` |
| **File Server SMB/CIFS** | SMB | Gravação de arquivos contábeis em servidor de arquivos Windows/Samba usando protocolo CIFS (biblioteca JCIFS) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Código bem organizado seguindo padrões de arquitetura em camadas (config, domain, service, repository, mapper, utils)
- Uso adequado de Spring Batch com separação clara de Reader, Processor e Writer
- Bom uso de DTOs e separação entre entidades de domínio e objetos de transferência
- Implementação de tratamento de exceções customizadas
- Uso de Lombok para redução de boilerplate
- Queries nativas bem documentadas em arquivo de constantes separado
- Configuração adequada de transações e múltiplos datasources
- Uso de projeções JPA para otimização de queries
- Implementação de métodos default em repositories para conversão de projeções

**Pontos de Melhoria:**
- Algumas classes de serviço com múltiplas responsabilidades (ex: ArquivoFormatter com lógica de negócio complexa)
- Queries nativas extensas poderiam ser refatoradas ou documentadas com mais detalhes
- Falta de documentação JavaDoc em algumas classes e métodos públicos
- Alguns métodos longos que poderiam ser quebrados em métodos menores (ex: métodos de formatação)
- Uso de constantes mágicas em alguns pontos (ex: valores hardcoded como "019", "90")
- Testes unitários não foram incluídos na análise, mas a estrutura sugere boa cobertura

**Observações:**
O código demonstra maturidade técnica e segue boas práticas de desenvolvimento Spring Boot/Batch. A organização é clara e facilita manutenção. Pequenos ajustes em documentação e refatoração de métodos longos elevariam ainda mais a qualidade.

---

## 14. Observações Relevantes

1. **Execução Batch**: O sistema é executado via linha de comando com parâmetros obrigatórios:
   - `codigoBanco`: Código do banco (655 para Votorantim, 413 para BV SA)
   - `tpExecucao`: Tipo de execução (B para Banco, E para Empresa)
   - `dtReferencia`: Data de referência no formato yyyy-MM-dd
   - `codigoEmpresa`: Código da empresa (opcional, usado apenas quando tpExecucao=E)

2. **Processamento em Steps**: O job possui dois steps:
   - `stepGerarLoteContabil`: Processa lotes normais
   - `stepGerarLoteContabilSuplementar`: Processa lotes suplementares quando necessário

3. **Formato de Arquivo**: O arquivo gerado possui formato fixo de 276 caracteres por linha, com encoding CP1252, contendo:
   - Cabeçalho com informações do lote
   - Detalhes com lançamentos consolidados (débito, crédito, valor, histórico)

4. **Autenticação**: Utiliza OAuth2 Client Credentials para autenticação no API Gateway, com renovação automática de token quando expirado.

5. **Ambientes**: Suporta múltiplos ambientes (des, uat, prd) com configurações específicas via infra.yml e variáveis de ambiente.

6. **Logging**: Configurado para gerar logs em formato JSON para facilitar integração com ferramentas de observabilidade.

7. **Containerização**: Preparado para execução em containers Docker com suporte a múltiplas camadas (layers) para otimização de build.

8. **Segurança**: Credenciais sensíveis (senhas de banco, file server, client secrets) são gerenciadas via cofre de senhas e injetadas como variáveis de ambiente.

9. **Banco de Dados Dual**: Utiliza H2 em memória para metadados do Spring Batch e MySQL para dados de negócio, com transações separadas.

10. **Validação de Parâmetros**: Implementa validação robusta dos parâmetros de entrada do job, incluindo validação de formato de data, códigos de banco e tipo de execução.