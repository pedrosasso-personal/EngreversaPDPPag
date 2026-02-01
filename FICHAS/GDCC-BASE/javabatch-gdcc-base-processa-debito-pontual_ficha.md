# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java desenvolvido para processar débitos pontuais no contexto do GDCC (Gestão de Débito em Conta Corrente). O sistema lê um arquivo texto posicional contendo solicitações de débito ou cancelamento, valida as informações contra bases de dados do sistema de Gestão de Contratos e do GDCF, e realiza o agendamento ou cancelamento de débitos automáticos em conta corrente. Gera arquivo de retorno com o resultado do processamento de cada registro.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê arquivo de entrada posicional, faz parse dos registros e consulta dados complementares nos bancos de dados (Gestão de Contratos e GDCF) |
| **ItemProcessor** | Aplica regras de negócio, valida dados do contrato e parcela, prepara objetos para inclusão/atualização no banco |
| **ItemWriter** | Persiste dados no banco (ContratoDebito, ParcelaDebito, RegistroDebito) e gera arquivo de retorno com status de processamento |
| **RegistroDebitoPontualParser** | Realiza parsing de linhas do arquivo posicional de entrada |
| **IntegracaoAgendaBusinessImpl** | Implementa lógica de integração com sistema de agendamento de débitos (GDCC) |
| **ContratoDebitoDao** | Acesso à tabela TbContratoDebito (consulta, inclusão e atualização) |
| **ParcelaDebitoDao** | Acesso à tabela TbParcelaDebito (consulta, inclusão e atualização) |
| **GestaoContratosDao** | Acesso aos dados de contratos e parcelas nos sistemas legados |
| **RegistroDebitoDao** | Acesso à tabela TbRegistroDebito (inclusão e atualização) |

## 3. Tecnologias Utilizadas

- **Java** (versão não especificada explicitamente)
- **Maven** - Gerenciamento de dependências e build
- **Spring Framework** - Injeção de dependências e configuração
- **BV Framework Batch** - Framework proprietário para processamento batch
- **Apache Axis 1.4** - Cliente para consumo de Web Services SOAP
- **Sybase jConnect 4 (7.07-SP136)** - Driver JDBC para banco Sybase
- **Log4j** - Framework de logging
- **JUnit** - Testes unitários
- **Apache Commons Lang** - Utilitários diversos

## 4. Principais Endpoints REST

Não se aplica. O sistema é um processamento batch que não expõe endpoints REST.

## 5. Principais Regras de Negócio

1. **Validação de Layout**: Arquivo de entrada deve ter 87 posições com campos obrigatórios (contrato, parcela, banco, agência, conta, CPF/CNPJ, valor)
2. **Validação de Contrato**: Contrato deve existir no sistema de Gestão de Contratos e não pode estar fechado
3. **Validação de Parcela**: Parcela deve existir no sistema legado e não pode estar quitada
4. **Controle de Duplicidade**: Verifica se contrato/parcela já foi cadastrado no arquivo ou no GDCF
5. **Validação CPF/CNPJ**: Aplica algoritmo de validação de CPF para determinar tipo de pessoa
6. **Agendamento de Débito**: Data de agendamento deve respeitar prazos mínimo e máximo configurados na conta convênio
7. **Cancelamento de Débito**: Permite cancelamento apenas de débitos ainda não processados ou agenda cancelamento futuro
8. **Atualização de Dados Bancários**: Atualiza dados bancários do contrato quando divergentes do sistema legado
9. **Validação de Data de Exercício**: Data de débito deve ser maior ou igual à data de exercício do sistema
10. **Geração de Arquivo de Retorno**: Cada linha processada gera registro de retorno com código e descrição do resultado

## 6. Relação entre Entidades

**TbContratoDebito** (1) ----< (N) **TbParcelaDebito**
- Um contrato pode ter várias parcelas de débito

**TbParcelaDebito** (N) ----< (1) **TbRegistroDebito**
- Cada parcela está associada a um registro de débito

**TbContaConvenio** (1) ----< (N) **TbRegistroDebito**
- Conta convênio define parâmetros para os registros de débito

**Sistema Legado (Gestão de Contratos)** fornece dados para **GDCF**
- Contratos e parcelas são consultados no legado para validação

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| DBGESTAO..TbContratoDebito | Tabela | SELECT | Consulta contratos com débito ativo e dados bancários |
| DBGESTAO..TbParcelaDebito | Tabela | SELECT | Consulta situação de parcelas de débito já cadastradas |
| DbGestaoDebitoContaCorrente..TbContaConvenio | Tabela | SELECT | Consulta parâmetros de conta convênio (prazos, tentativas) |
| DbGestaoDebitoContaCorrente..TbContaConvenioSistemaOrigem | Tabela | SELECT | Associação entre conta convênio e sistema origem |
| DbGestaoDebitoContaCorrente..TbParametroSistema | Tabela | SELECT | Consulta data de exercício do sistema |
| DbGestaoDebitoContaCorrente..TbRegistroDebito | Tabela | SELECT | Consulta registros de débito por código |
| DBCOR..TbContratoPrincipal | Tabela | SELECT | Identifica banco de dados de origem do contrato |
| DBCOR..TbProduto | Tabela | SELECT | Dados de produto do contrato |
| DBCOR..TbConexao | Tabela | SELECT | Informações de conexão com BD legado |
| ${nomeBD}..TbContrato | Tabela | SELECT | Dados do contrato no sistema legado |
| ${nomeBD}..TbContratoFinanceiro | Tabela | SELECT | Dados financeiros do contrato no legado |
| ${nomeBD}..TbParcela | Tabela | SELECT | Dados de parcelas no sistema legado |
| DBCRED..TbProposta | Tabela | SELECT | Dados da proposta de crédito |
| DBGESTAO..vwTbContrato | View | SELECT | View de contratos com número legado |
| DBCOR..TbPessoa | Tabela | SELECT | Dados de pessoa |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| DBGESTAO..TbContratoDebito | Tabela | INSERT | Inclusão de novos contratos de débito |
| DBGESTAO..TbContratoDebito | Tabela | UPDATE | Atualização de dados bancários e suspensão de contratos |
| DBGESTAO..TbParcelaDebito | Tabela | INSERT | Inclusão de novas parcelas de débito agendadas |
| DBGESTAO..TbParcelaDebito | Tabela | UPDATE | Atualização de status de parcelas (cancelamento, erro) |
| DbGestaoDebitoContaCorrente..TbRegistroDebito | Tabela | INSERT | Inclusão de registros de débito para agendamento |
| DbGestaoDebitoContaCorrente..TbRegistroDebito | Tabela | UPDATE | Atualização de status de registros de débito |
| DbGestaoDebitoContaCorrente..TbLogArquivoDebito | Tabela | UPDATE | Atualização de status de processamento de arquivo |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| DebitoPontual.txt (parametrizável) | Leitura | ItemReader | Arquivo posicional de entrada com solicitações de débito/cancelamento (87 posições) |
| DebitoPontual_Erro.txt (parametrizável) | Gravação | ItemWriter | Arquivo de retorno com resultado do processamento de cada registro |
| robo.log | Gravação | Log4j (roboFile appender) | Log de execução do batch |
| statistics-{executionId}.log | Gravação | Log4j (statistics appender) | Log de estatísticas de execução |

## 10. Filas Lidas

Não se aplica.

## 11. Filas Geradas

Não se aplica.

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **GDCC - Serviço de Agendamento** | Web Service SOAP | Agendamento e cancelamento de débitos em conta corrente (endpoint parametrizável via webServiceAgendamentoEndpoint) |
| **Sistema Legado de Gestão de Contratos** | Banco de Dados | Consulta dados de contratos e parcelas em múltiplos bancos de dados legados (conexão dinâmica via DBCOR..TbConexao) |

## 13. Avaliação da Qualidade do Código

**Nota:** 5/10

**Justificativa:**

**Pontos Positivos:**
- Separação clara de responsabilidades entre Reader, Processor e Writer
- Uso de enums para representar estados e tipos
- Utilização de DAOs para acesso a dados
- Tratamento de exceções específicas

**Pontos Negativos:**
- **Código legado com muitos code smells**: Métodos com nomes como "extracaoSonar1", "extracaoSonar2" indicam refatorações mal feitas para atender análise estática
- **Métodos muito longos**: ItemProcessor.handleProcess() e métodos de validação são extensos e complexos
- **Lógica de negócio misturada**: Validação de CPF implementada diretamente no Processor ao invés de classe utilitária
- **Comentários em português com caracteres especiais**: Problemas de encoding (�) dificultam leitura
- **Código comentado**: Várias seções de código comentado não removidas
- **Falta de documentação**: Javadoc incompleto ou ausente em muitos métodos
- **Hardcoded values**: Strings e valores mágicos espalhados pelo código
- **Tratamento de exceções genérico**: Muitos catch(Exception) sem tratamento específico
- **Dependência de framework legado**: Uso de framework proprietário BV limita portabilidade
- **Queries SQL como Strings**: SQLs hardcoded em classes Resources ao invés de arquivos externos

## 14. Observações Relevantes

1. **Sistema Legado**: O código apresenta características de sistema legado com refatorações para atender análise estática (Sonar), evidenciado pelos nomes de métodos "extracaoSonar"
2. **Multi-tenant Database**: Sistema acessa múltiplos bancos de dados dinamicamente baseado no contrato (${nomeBD})
3. **Processamento Transacional**: Utiliza controle transacional do framework BV com commit/rollback
4. **Arquivo Posicional**: Layout fixo de 87 caracteres com campos em posições específicas
5. **Códigos de Retorno**: Sistema retorna códigos específicos (00-12) para cada tipo de resultado no arquivo de saída
6. **Validação de CPF**: Implementação própria do algoritmo de validação de CPF
7. **Geração de Sequenciais**: Utiliza stored procedure customizada (prObterSequencialDisponivelOut) para geração de IDs
8. **Configuração via Spring XML**: Toda configuração do job é feita via arquivos XML do Spring
9. **Encoding**: Código fonte apresenta problemas de encoding (caracteres �) sugerindo conversão inadequada de ISO-8859-1
10. **Ambiente**: Configurações apontam para ambientes Votorantim (ptasybdes15.bvnet.bv)