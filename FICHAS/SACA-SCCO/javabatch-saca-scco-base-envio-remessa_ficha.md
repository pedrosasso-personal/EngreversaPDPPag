# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de geração de arquivos de remessa bancária em formato CNAB (240/400) para cobrança de títulos de CDC (Crédito Direto ao Consumidor) e Leasing. O sistema opera em modo batch, processando títulos pendentes de registro ou baixa e gerando arquivos físicos específicos para cada instituição bancária (Banco do Brasil, Bradesco, Itaú, Santander e Votorantim). Utiliza framework proprietário BVSistemas para processamento batch com estratégia de tratamento de erros e controle transacional.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ArquivoRemessaProcessor** | Processa registros individuais, gera código sequencial do arquivo, roteia para banco específico e aplica regras de multa/isenção |
| **ArquivoRemessaReader** | Carrega parâmetros de remessa e registros de instrumentos de cobrança do banco de dados |
| **ArquivoRemessaWriter** | Gera arquivo físico de remessa CNAB, nomeia conforme padrão do banco e atualiza situação de processamento no BD |
| **ArquivoRemessaBusiness** | Orquestra busca de parâmetros e registros de remessa através dos DAOs |
| **ArquivoRemessaBancoDoBrasilBusiness** | Monta estrutura de remessa CNAB400 específica do Banco do Brasil |
| **ArquivoRemessaBradescoBusiness** | Monta estrutura de remessa CNAB400 específica do Bradesco |
| **ArquivoRemessaItauBusiness** | Monta estrutura de remessa CNAB400 específica do Itaú |
| **ArquivoRemessaSantanderBusiness** | Monta estrutura de remessa CNAB específica do Santander |
| **ArquivoRemessaVotorantimBusiness** | Monta estrutura de remessa CNAB específica do Votorantim com suporte a piloto EMBCP |
| **DatabaseConnection** | Singleton para gerenciamento de conexões JDBC transacionais e não-transacionais |
| **CarneParametroSistemaDao** | Gerencia sequencial de arquivos de remessa |
| **ParametroRemessaDao** | Consulta parâmetros de remessa via stored procedure |
| **RegistroInstrumentoCobrancaDao** | Busca títulos pendentes para remessa via stored procedure |
| **SituacaoProcessamentoInstoDao** | Registra situação de processamento dos títulos |
| **PilotoDAO** | Verifica se funcionalidades piloto estão ativas |
| **ArquivoRemessaUtil** | Funções utilitárias para formatação de campos CNAB |
| **MyResumeStrategy** | Estratégia customizada de tratamento de erros do batch |

---

## 3. Tecnologias Utilizadas

- **Framework Batch:** BVSistemas Framework Batch (versão 13.0.20-SNAPSHOT)
- **Linguagem:** Java
- **Gerenciamento de Transações:** Bitronix JTA
- **Banco de Dados:** Sybase ASE (servidor ptasybdes15.bvnet.bv:6010)
- **Driver JDBC:** BV JDBC Driver
- **Build:** Maven 3.x
- **Logging:** Log4j
- **Testes:** JUnit
- **Controle de Versão:** Git
- **CI/CD:** Jenkins
- **Charset:** ISO_1 (ISO-8859-1)
- **JVM:** Java com configurações -Xms256M -Xmx1G

---

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch sem exposição de endpoints REST.

---

## 5. Principais Regras de Negócio

1. **Geração de Código Sequencial:** Sistema gera código sequencial único para cada arquivo de remessa através da tabela TB_CARNE_PARAMETRO_SISTEMA

2. **Roteamento por Banco:** Utiliza BancoEnum para direcionar processamento específico (001=BB, 033=Santander, 237=Bradesco, 341=Itaú, 655=Votorantim)

3. **Tratamento de Multa/Isenção:** 
   - Se PcMulta=null/zero E VrMulta=null/zero, envia registro de isenção (BB e Votorantim)
   - Votorantim: TipoCobrancaMultaEnum define forma de cobrança

4. **Estados de Processamento:**
   - PENDENTE_REGISTRO (1): Título aguardando registro no banco
   - PENDENTE_BAIXA (4): Título aguardando baixa
   - PRE_ACATADO (7): Título pré-processado

5. **Comandos de Remessa:**
   - 01/1/48: Registro de título
   - 02/2: Baixa de título

6. **Cálculo de Nosso Número:** Geração sequencial com dígito verificador (DAC) usando módulo 10 ou 11 conforme banco

7. **Piloto EMBCP (Votorantim):** Se CD_INSTRUMENTO_COBRANCA_BOLETAO=12, usa VALOR_AO_DIA, senão usa PERCENTUAL

8. **Validação de Endereço:** Sistema evita endereços contendo "XXX" (inconsistências)

9. **Cálculo de Taxa Bancária:** Condicionado por área operacional e data de vigência

10. **Geração de Contratos CDC:** 
    - Filtra contratos aprovados (status_bdr='1', pre_pos='0', dt_carnet null, emite_carne='1')
    - Calcula dt_pesquisa = data_corrente - nu_dias_geracao_carne

11. **Geração de Contratos Leasing:**
    - Tipos: P/M (carnê) ou I/D (boleto INPC/Dólar)
    - Calcula valores com índice INPC/Dólar quando aplicável
    - Verifica disponibilidade de índice INPC antes de gerar boleto
    - Calcula quinzena para boletos (dia 1-15 ou 16-fim)

12. **Nomenclatura de Arquivos:**
    - BB/Itaú/Votorantim: ddMMyyyyHHmmssSSS
    - Bradesco: ddMMSEQ
    - Santander: padrão específico

13. **Tratamento de Erro:** Em caso de erro, deleta arquivo físico, executa rollback e fecha conexões

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **ParametroRemessaVO:** Contém dados da empresa/convênio bancário (CNPJ, razão social, banco, agência, conta corrente, carteira)

- **RegistroInstrumentoCobrancaVO:** Representa um título de cobrança com 60+ atributos incluindo dados do contrato, valores, datas, informações do pagador e endereço

- **InputUnitOfWork:** Encapsula unidade de trabalho do batch (ParametroRemessaVO + Lista de RegistroInstrumentoCobrancaVO + dtExecucao)

- **OutputUnitOfWork:** Resultado do processamento (cdBanco, cdArq, ArquivoRemessaDTO, lista de registros, parâmetros)

- **BoletoId:** Identificador composto de boleto (nossoNumero, codigoOcoConta, codigoIdEmpresaBanco, codigoCarteiraBanco)

**Relacionamentos:**
- 1 ParametroRemessaVO → N RegistroInstrumentoCobrancaVO (um convênio processa múltiplos títulos)
- 1 InputUnitOfWork → 1 ParametroRemessaVO + N RegistroInstrumentoCobrancaVO
- 1 OutputUnitOfWork → 1 ArquivoRemessaDTO + N RegistroInstrumentoCobrancaVO processados

**VOs Específicos por Banco:**
- Cada banco possui estrutura própria: CabecalhoVO, DetalheVO, RodapeVO (BB, Bradesco, Itaú, Santander, Votorantim)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TB_CARNE_PARAMETRO_SISTEMA | Tabela | SELECT | Busca número sequencial do arquivo de remessa |
| TB_INSTRUMENTO_COBRANCA | Tabela | SELECT | Consulta instrumentos de cobrança configurados |
| TB_CARNE_CONTROLE_ENVIO | Tabela | SELECT | Controle de envios de carnê |
| TB_TAXA_BANCARIA | Tabela | SELECT | Consulta taxas bancárias por vigência |
| DBCOR..TbTipoPiloto | Tabela | SELECT | Verifica se piloto está ativo (SgTipoPiloto, DtInativacao) |
| scc_fin.CONTRATO | Tabela | SELECT | Dados de contratos financeiros CDC |
| scc_fin.BORDERO | Tabela | SELECT | Dados de borderôs |
| scc_fin.PARCELA | Tabela | SELECT | Parcelas de contratos CDC |
| scc_fin.PRODUTO | Tabela | SELECT | Produtos financeiros |
| scc_fin.cliente | Tabela | SELECT | Dados cadastrais de clientes |
| scc_fin.filial | Tabela | SELECT | Dados de filiais |
| sce.CONTRATOS | Tabela | SELECT | Contratos de leasing |
| sce.PARCELAS | Tabela | SELECT | Parcelas de contratos leasing |
| sce.clientes | Tabela | SELECT | Clientes leasing |
| sce.cli_enderecos | Tabela | SELECT | Endereços de clientes leasing |
| sce.mor_cots | Tabela | SELECT | Cotações de moeda |
| sce.mora | Tabela | SELECT | Dados de mora |
| tb_banco_cep | Tabela | SELECT | Dados de CEP |
| tb_indice_inpc | Tabela | SELECT | Índices INPC para correção |
| DBCARNE..PrGeraRemessaConsultaConvenio | Procedure | SELECT | Consulta parâmetros de convênio para remessa |
| DBCARNE..prGeraRemessaConsultaDetalhe | Procedure | SELECT | Consulta títulos pendentes para remessa |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TB_CARNE_PARAMETRO_SISTEMA | Tabela | UPDATE | Incrementa nu_sequencial_arq após geração |
| TbSituacaoProcessamentoInsto | Tabela | INSERT | Registra situação de processamento do título (TpComando R=registro/B=baixa, TpRegistro=B batch, TpInterface=E envio) |
| TB_CARNE_CONTROLE_COBRANCA | Tabela | INSERT | Insere títulos gerados para cobrança |
| TB_CARNE_ARQUIVO | Tabela | INSERT | Registra arquivo de remessa gerado |
| scc_fin.CONTRATO | Tabela | UPDATE | Atualiza dt_carnet após geração |
| scc_fin.boleto_contrato | Tabela | INSERT | Insere controle de boletos |
| scc_fin.boleto_parcelas | Tabela | INSERT | Insere parcelas de boletos |
| scc_fin.boleto_controle | Tabela | INSERT | Controle de geração de boletos |
| sce.contratos | Tabela | UPDATE | Atualiza cod_ban (código do banco) |
| sce.parcelas | Tabela | UPDATE | Atualiza flg_cob='1' (flag de cobrança) |
| tb_carne_contratos_leasing | Tabela | UPDATE | Atualiza controle de carnês leasing |
| TbInconsistenciaEndereco | Tabela | INSERT | Registra inconsistências de endereço detectadas |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| Arquivo CNAB Banco do Brasil | Gravação | arquivos/001/ | ArquivoRemessaWriter | Arquivo de remessa CNAB400 formato BB, nomenclatura ddMMyyyyHHmmssSSS.txt |
| Arquivo CNAB Bradesco | Gravação | arquivos/237/ | ArquivoRemessaWriter | Arquivo de remessa CNAB400 formato Bradesco, nomenclatura ddMMSEQ.txt |
| Arquivo CNAB Itaú | Gravação | arquivos/341/ | ArquivoRemessaWriter | Arquivo de remessa CNAB400 formato Itaú, nomenclatura ddMMyyyyHHmmssSSS.txt |
| Arquivo CNAB Santander | Gravação | arquivos/033/ | ArquivoRemessaWriter | Arquivo de remessa CNAB formato Santander, nomenclatura específica |
| Arquivo CNAB Votorantim | Gravação | arquivos/655/ | ArquivoRemessaWriter | Arquivo de remessa CNAB formato Votorantim, nomenclatura ddMMyyyyHHmmssSSS.txt |
| robo.log | Gravação | Diretório de execução | Log4j RollingFileAppender | Log de execução do batch (2MB por arquivo, máx 100MB, 5 backups) |
| statistics.log | Gravação | Diretório de execução | Log4j BvDailyRollingFileAppender | Log de estatísticas (empresa votorantim/bvfinanceira, plataforma cobranca/saca, sistema batch/scco) |
| btm*.tlog | Leitura/Gravação | Diretório de execução | Bitronix Transaction Manager | Arquivos de log transacional (removidos ao final da execução) |

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

---

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **Banco de Dados Sybase DBCARNE** | JDBC | Base principal de dados de carnê e cobrança, contém tabelas de controle, parâmetros e stored procedures de geração |
| **Banco de Dados Sybase scc_fin** | JDBC | Base de dados de contratos CDC, contém informações de contratos, parcelas, clientes e produtos financeiros |
| **Banco de Dados Sybase sce** | JDBC | Base de dados de contratos Leasing, contém informações específicas de leasing incluindo cotações e índices |
| **Banco de Dados Sybase DBCOR** | JDBC | Base corporativa, contém tabela de pilotos (TbTipoPiloto) para controle de funcionalidades em teste |
| **Sistema de Arquivos** | File System | Geração de arquivos físicos CNAB em diretórios específicos por banco (arquivos/{cdBanco}/) |
| **Bancos Conveniados** | Arquivo CNAB | Integração indireta através de arquivos de remessa: Banco do Brasil (001), Bradesco (237), Itaú (341), Santander (033), Votorantim (655) |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 5/10

**Justificativa:**

**Pontos Positivos:**
- Separação clara de responsabilidades entre Reader, Processor e Writer (padrão batch)
- Uso de DAOs para acesso a dados
- Tratamento de erros com estratégia customizada
- Logging estruturado com statistics
- Uso de constantes e enums para valores fixos
- Testes de integração implementados

**Pontos Negativos:**
- **Código legado** com comentários em português misturados com código
- **Uso excessivo de VOs** (Value Objects) com muitos atributos (60+ em RegistroInstrumentoCobrancaVO)
- **Falta de encapsulamento** de regras de negócio complexas
- **Duplicação de lógica** entre classes de negócio de diferentes bancos (BB, Bradesco, Itaú, Santander, Votorantim)
- **Mistura de responsabilidades**: classes de negócio também fazem formatação CNAB
- **Implementação inconsistente**: piloto EMBCP implementado apenas para Votorantim
- **Dependência de stored procedures** complexas (PrCDCTesteSCCO, prLEATEsteSCCO) dificultando manutenção
- **Falta de abstração**: cada banco tem implementação completamente separada sem interface comum
- **Acoplamento forte** com framework proprietário BVSistemas
- **Configurações hardcoded** em múltiplos locais (XMLs, properties, código)
- **Falta de documentação técnica** inline adequada
- **Tratamento de exceções genérico** em alguns pontos

**Recomendações:**
1. Refatorar para usar padrão Strategy ou Template Method para bancos
2. Criar camada de abstração para formatação CNAB
3. Extrair regras de negócio complexas para classes especializadas
4. Reduzir número de atributos nos VOs através de composição
5. Migrar stored procedures para código Java quando possível
6. Implementar testes unitários além dos de integração
7. Padronizar nomenclatura e idioma (inglês)
8. Adicionar validações de entrada mais robustas

---

## 14. Observações Relevantes

1. **Ambiente de Desenvolvimento:** Sistema configurado para servidor Sybase ptasybdes15.bvnet.bv:6010, banco dbcarne, usuário plat_credito

2. **Charset Específico:** Sistema utiliza ISO_1 (ISO-8859-1) para compatibilidade com sistemas legados

3. **Execução Dual:** Sistema suporta dois modos de execução:
   - **Automático:** Execução agendada sem parâmetros (usa data corrente)
   - **Sob Demanda:** Execução manual com parâmetros cdBanco e dtExecucao

4. **Controle Transacional:** Utiliza Bitronix JTA para gerenciamento de transações distribuídas, com limpeza automática de tlogs

5. **Códigos de Saída:** Sistema retorna exit codes específicos (11-99) para diferentes tipos de erro, facilitando monitoramento

6. **Segurança:** Comentários no código indicam que senhas devem ser criptografadas em ambientes QA/UAT/PROD (atualmente em texto claro no ambiente de desenvolvimento)

7. **Bancos Suportados Adicionais:** Além dos 5 bancos implementados, código menciona HSBC (399) e ABN (356) nas stored procedures, mas sem implementação Java correspondente

8. **Cálculo de DAC:** Sistema implementa dois algoritmos de dígito verificador (módulo 10 e módulo 11) conforme exigência de cada banco

9. **Processamento de Índices:** Sistema leasing possui lógica complexa de correção por INPC e Dólar, com validação de disponibilidade de índices antes de processar

10. **Validação de Dados:** Sistema possui mecanismos de validação de endereço e registra inconsistências em tabela específica (TbInconsistenciaEndereco)

11. **Versionamento:** Tag atual: javabatch-saca-scco-base-envio-remessa-19.04.3.SV-620.1

12. **Dependências de Versão:** Parent bv-sistemas-master:13.0.19, framework batch 13.0.20-SNAPSHOT

13. **Limitações de Memória:** JVM configurada com heap mínimo 256MB e máximo 1GB, com desabilitação de GC overhead limit

14. **Estrutura de Deployment:** Sistema empacotado como ZIP contendo JARs, scripts batch (.bat/.sh) e arquivos de configuração

15. **CI/CD:** Integrado com Jenkins, componente identificado como javabatch-saca-scco-base-envio-remessa, módulo saca-scco