---
## Ficha Técnica do Sistema

### 1. Descrição Geral
Sistema batch Java desenvolvido em Spring Batch para processar baixa operacional de boletos CIP (Câmara Interbancária de Pagamentos) em cenário de contingência. O sistema lê títulos pendentes do banco de dados, agrupa por ISPB (Votorantim 655 e BVSA 413), gera arquivos XML no formato ADDA114 compactados em GZIP e atualiza o status de processamento no banco de dados. Os arquivos gerados são depositados em diretório de rede para posterior envio ao CIP.

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê títulos em contingência do banco de dados e separa por banco (655/413) |
| **ItemProcessor** | Processa e transforma dados de BaixaOperacionalVO para CipGrupoADDA114TitVO, aplicando regras de negócio |
| **ItemWriter** | Gera arquivos XML/GZIP, atualiza status no BD e persiste informações de compensação |
| **BaixaOperacionalBusinessImpl** | Implementa regras de negócio: pesquisa títulos, atualiza status, gera arquivos |
| **BaixaOperacionalDaoImpl** | Acesso a dados: consulta títulos, atualiza flags de processamento, obtém sequências |
| **ArquivoCompensacaoDaoImpl** | Persiste dados de arquivo e detalhes de compensação |
| **LayoutWriter** | Monta estrutura XML no layout ADDA114 e compacta em GZIP |
| **FileUtil** | Utilitário para conversão objeto→XML (JAXB) e compressão GZIP |
| **Utils** | Funções auxiliares: validação CPF/CNPJ, normalização de dados, formatação |
| **ValidarCpf** | Validação de CPF com cálculo de dígitos verificadores |

### 3. Tecnologias Utilizadas
- **Spring Batch**: Framework para processamento batch
- **JAXB (Java Architecture for XML Binding)**: Binding XML/Java
- **Bitronix JTA**: Gerenciamento de transações distribuídas
- **JDBC**: Acesso a banco de dados Sybase
- **Sybase**: Sistema gerenciador de banco de dados
- **JUnit**: Framework de testes unitários
- **Maven**: Gerenciamento de dependências e build
- **GZIP**: Compressão de arquivos
- **XML**: Formato de intercâmbio de dados (layout ADDA114)

### 4. Principais Endpoints REST
Não se aplica (sistema batch sem interface REST).

### 5. Principais Regras de Negócio

1. **Definição de Portador**: Utiliza dados do portador se preenchidos; caso contrário, usa dados do cliente fintech; se não disponível, usa dados do remetente.

2. **Definição de Agregador**: Para origem=88 usa portador como agregador; para outras origens usa cliente fintech ou remetente.

3. **Separação por ISPB**: Títulos são segregados por banco - 655 (Votorantim/59588111) e 413 (BVSA/01858774).

4. **Normalização de Dados**: Remove caracteres especiais de nomes e normaliza CPF/CNPJ (padding com zeros à esquerda).

5. **Validação de Tipo de Pessoa**: Define tipo pessoa (F=Física, J=Jurídica) baseado na validação de CPF (11 dígitos válidos = F, demais casos = J).

6. **Limite de Registros**: Máximo de 50.000 registros por arquivo.

7. **Sequenciamento Diário**: Utiliza sequência diária para nomenclatura de arquivos.

8. **Nomenclatura de Arquivo**: Segue padrão UC4: `ADDA114_ISPB_DATA_SEQ#02#46#000#ISPB#ISPBCIP#SPB.dda`

9. **Charset UTF-16BE**: Arquivos XML gerados em UTF-16BE.

10. **Processamento Temporário**: Arquivos gravados com extensão .tmp e renomeados para .dda após conclusão.

### 6. Relação entre Entidades

**Hierarquia de Value Objects:**
```
BaixaOperacionalVO (estende CipGrupoADDA114TitVO)
    ├─ codOrigem
    ├─ nomRzSocClienteFintech
    ├─ cpfCnpjClienteFintech
    ├─ nomRzSocRmtnt
    └─ cnpjCpfRmtnt

CipGrupoADDA114TitVO
    ├─ cdRegistro
    ├─ cdMeioPagto
    ├─ cdCanal
    ├─ ISPBs (portador/agregador)
    ├─ valores e datas
    └─ dados cadastrais

CipADDA114VO
    └─ Lista<BaixaOperacionalVO>

ADDA114ComplexType (JAXB)
    └─ Estrutura XML do layout CIP
```

**Relacionamento de Processamento:**
- ItemReader → BaixaOperacionalVO
- ItemProcessor → CipGrupoADDA114TitVO
- ItemWriter → CipADDA114VO → Arquivo XML/GZIP

### 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbRegistroPagamentoCIP | Tabela | SELECT | Leitura de títulos em contingência (flProcessamentoCIP='N') |
| TBL_CAIXA_ENTRADA_SPB | Tabela | SELECT | Consulta dados de caixa entrada SPB |
| Tbl_Lancamento | Tabela | SELECT | Consulta lançamentos financeiros |
| TbLancamentoPortador | Tabela | SELECT | Consulta dados de portador dos lançamentos |
| VwDadosConfiguracaoCip | View | SELECT | Obtenção de data de movimento atual e configurações CIP |

**Schemas:**
- DBPGF_TES: Tabelas operacionais de pagamento
- DBGESTAOCOBRANCA: View de configuração

### 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbRegistroPagamentoCIP | Tabela | UPDATE | Atualização de flags: FlBaixaOperacionalContingencia e flProcessamentoCIP |
| TbArquivoCompensacao | Tabela | INSERT | Inserção de dados do arquivo de compensação gerado |
| TbDetalheArquivoCompensacao | Tabela | INSERT | Inserção de detalhes (títulos) do arquivo de compensação |

**Sequences utilizadas:**
- SEQ_ARQUIVO_COMPENSACAO_ID
- SEQ_NOME_ARQUIVO_COMPENSACAO_ID

### 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| ADDA114_ISPB_DATA_SEQ#02#46#000#ISPB#ISPBCIP#SPB.dda | Gravação | LayoutWriter / ItemWriter | Arquivo XML compactado em GZIP contendo dados de baixa operacional no formato ADDA114 |
| *.tmp | Gravação temporária | LayoutWriter | Arquivo temporário durante processamento, renomeado para .dda após conclusão |

**Diretório de saída:** Configurado por ambiente (DES/QA/UAT/PRD) em arquivos XML de configuração, depositado em diretório de rede para envio ao CIP.

### 10. Filas Lidas
Não se aplica (sistema não consome filas).

### 11. Filas Geradas
Não se aplica (sistema não publica em filas).

### 12. Integrações Externas

| Sistema/Serviço | Tipo de Integração | Descrição |
|-----------------|-------------------|-----------|
| **CIP (Câmara Interbancária de Pagamentos)** | Arquivo (diretório de rede) | Envio de arquivos XML/GZIP com dados de baixa operacional de boletos em contingência |
| **Sybase DBPGF_TES** | JDBC | Banco de dados operacional com tabelas de pagamento CIP |
| **Sybase DBGESTAOCOBRANCA** | JDBC | Banco de dados com configurações e views de gestão de cobrança |

**Bancos participantes:**
- Votorantim (código 655, ISPB 59588111)
- BVSA (código 413, ISPB 01858774)

### 13. Avaliação da Qualidade do Código

**Nota:** 8/10

**Justificativa:**
O código apresenta boa qualidade geral com os seguintes pontos positivos:
- **Arquitetura bem definida**: Separação clara de responsabilidades entre camadas (Reader, Processor, Writer, Business, DAO)
- **Uso adequado de frameworks**: Spring Batch, JAXB e JTA utilizados corretamente
- **Tratamento de erros**: Exit codes definidos, exceções customizadas (PgftException), logs adequados
- **Testabilidade**: Cobertura de testes unitários para classes principais
- **Padrões de projeto**: DAO, VO, Strategy (BancoEnum)
- **Configuração externalizada**: Ambientes separados em XMLs

Pontos de melhoria:
- **Classes JAXB auto-geradas**: Grande volume de classes simples (apenas getters/setters) que poderiam ser otimizadas
- **Documentação**: Ausência de JavaDoc em algumas classes críticas
- **Complexidade em ItemProcessor**: Lógica de mapeamento portador/agregador poderia ser extraída para classe específica
- **Hardcoding**: Alguns valores fixos (ISPBs, códigos) poderiam estar em arquivo de propriedades

### 14. Observações Relevantes

1. **Configuração Multi-ambiente**: Sistema possui configurações específicas para DES, QA, UAT e PRD em arquivos XML separados.

2. **Processamento Assíncrono**: Utiliza taskExecutor com máximo de 2 threads para processamento paralelo.

3. **Commit Interval**: Configurado com commitInterval=1, processando item a item para garantir consistência.

4. **Charset Específico**: Arquivos XML gerados em UTF-16BE conforme especificação CIP.

5. **Nomenclatura Padronizada**: Nome de arquivo segue padrão UC4 com informações estruturadas (ISPB, data, sequência).

6. **Gestão de Transações**: Utiliza Bitronix JTA para gerenciamento de transações distribuídas entre múltiplos recursos.

7. **Validação de CPF**: Implementa algoritmo completo de validação com cálculo de dígitos verificadores.

8. **Normalização de Dados**: Remove caracteres especiais de nomes e formata CPF/CNPJ com padding de zeros.

9. **Limite de Processamento**: Controle de 50.000 registros por arquivo para evitar arquivos muito grandes.

10. **Sequenciamento Diário**: Utiliza sequência que reinicia diariamente para controle de arquivos gerados no dia.

11. **Suporte a Múltiplos Bancos**: Arquitetura preparada para processar títulos de diferentes instituições (atualmente Votorantim e BVSA).

12. **Rastreabilidade**: Inserção de dados em tabelas de compensação permite auditoria e rastreamento completo dos arquivos gerados.

---