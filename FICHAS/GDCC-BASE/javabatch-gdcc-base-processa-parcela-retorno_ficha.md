# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java desenvolvido com Spring Batch para processar retornos de débitos automáticos em conta corrente. O sistema consulta arquivos de retorno processados via webservice, processa as informações de débito (baixas, suspensões, inconsistências), atualiza o status das parcelas, gera controles de carga para baixa e cria tarefas SAC quando necessário. Integra-se com o sistema GDCC (Gestão de Débito em Conta Corrente Corporativa) e sistemas legados de gestão de contratos.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Consulta webservice de arquivos processados e inicializa recursos (DAOs, conexões) |
| **ItemProcessor** | Processa retornos de débito, determina ações (baixar, suspender, criar tarefa SAC) e atualiza status das parcelas |
| **ItemWriter** | Persiste alterações nas parcelas, gera controles de carga, informações de baixa e tarefas SAC |
| **MyResumeStrategy** | Estratégia de tratamento de erros e definição de códigos de saída |
| **ControleArquivoRetornoDao** | Gerencia controle de processamento de arquivos de retorno |
| **ConsultarRetornoDao** | Consulta detalhes dos retornos de débito |
| **ParcelaDebitoDao** | Operações CRUD em parcelas de débito |
| **ContratoDebitoDao** | Gerencia contratos de débito e suspensões |
| **GerarTarefaSacDao** | Cria solicitações/tarefas no sistema SAC |
| **TransferObject** | DTO para transferência de dados entre componentes do batch |

## 3. Tecnologias Utilizadas

- **Spring Batch** (framework BV customizado)
- **Java** (versão não especificada, provavelmente Java 6/7 pela sintaxe)
- **Apache Axis 1.4** (cliente SOAP/webservices)
- **Sybase ASE** (banco de dados - jConnect 7.07-SP136)
- **Maven** (gerenciamento de dependências)
- **JUnit** (testes)
- **Log4j** (logging)
- **Framework BV** (framework proprietário do Banco Votorantim)

## 4. Principais Endpoints REST

Não se aplica. O sistema utiliza webservices SOAP, não REST.

**Webservices SOAP consumidos:**
- `BV-bvf-nnegocios-gdcc.arquivosProcessados.ConsultarArquivosProcessados` - Consulta arquivos processados
- `BV-bvf-nnegocios-gdcc.ConsultaRetorno` - Consulta retornos de débito
- `BV-bvf-nnegocios-gdcc.Agendamento` - Agendamento de remessas
- `BV-bvf-nnegocios-gdcc.contaConvenio.ConsultaBancosConveniados` - Consulta bancos conveniados

## 5. Principais Regras de Negócio

1. **Processamento de Retornos**: Consulta arquivos de retorno não processados e processa cada registro de débito
2. **Ações por Tipo de Retorno**:
   - Tipo 1: Baixar parcela (débito efetivado com sucesso)
   - Tipo 2: Suspender débito (inconsistência cadastral)
   - Tipo 3: Não realizar movimentação
   - Tipo 4: Criar tarefa SAC (divergências)
   - Tipo 5: Criar tarefa SAC e suspender débito
3. **Controle de Carga**: Agrupa baixas por agente recebedor em lotes de até 7000 registros
4. **Autorização CEF**: Trata retornos específicos de autorização da Caixa Econômica Federal (códigos AA, 78, AB, BD)
5. **Cadastro Optante**: Processa movimentos tipo 5 (débito optante) com valor zero
6. **Geração de Tarefas SAC**: Cria solicitações com prazo de 15 dias úteis para tratamento de inconsistências
7. **Suspensão de Contratos**: Atualiza flag de débito ativo e motivo de suspensão conforme tipo de retorno
8. **Cancelamento de Débitos**: Trata movimentos tipo 1 (cancelamento) com código de retorno 99

## 6. Relação entre Entidades

**Principais entidades e relacionamentos:**

- **TbLogArquivoDebito** (1) ← (N) **TbEventoRegistroDebito** - Arquivo contém múltiplos eventos
- **TbRegistroDebito** (1) ← (N) **TbEventoRegistroDebito** - Registro possui múltiplos eventos
- **TbParcelaDebito** (N) → (1) **TbRegistroDebito** - Parcela referencia registro de débito
- **TbContratoDebito** (1) ← (N) **TbParcelaDebito** - Contrato possui múltiplas parcelas
- **TbContaConvenioSistemaOrigem** (1) ← (N) **TbRegistroDebito** - Conta convênio associada a registros
- **TbRetornoDebitoAutomatico** (1) ← (N) **TbEventoRegistroDebito** - Código de retorno do banco
- **TbRetornoDebitoSistemaOrigem** (1) ← (N) **TbParametroRetornoDebito** - Mapeamento de ações por retorno

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View | Tipo | Operação | Breve Descrição |
|---------------------|------|----------|-----------------|
| TbLogArquivoDebito | Tabela | SELECT | Consulta arquivos de retorno processados |
| TbEventoRegistroDebito | Tabela | SELECT | Consulta eventos de retorno de débito |
| TbRegistroDebito | Tabela | SELECT | Consulta registros de débito enviados |
| TbParcelaDebito | Tabela | SELECT | Consulta parcelas de débito por código de registro |
| TbContratoDebito | Tabela | SELECT | Consulta contratos de débito ativos |
| TbRetornoDebitoAutomatico | Tabela | SELECT | Consulta códigos de retorno do banco |
| TbParametroRetornoDebito | Tabela | SELECT | Consulta mapeamento de ações por retorno |
| TbRetornoDebitoSistemaOrigem | Tabela | SELECT | Consulta ações do sistema de origem |
| TbContaConvenioSistemaOrigem | Tabela | SELECT | Consulta contas convênio por sistema |
| TbControleArquivoRetorno | Tabela | SELECT | Verifica se arquivo já foi processado |
| TbSolicitacao (DBSLT) | Tabela | SELECT | Consulta solicitações SAC |
| TbNaturezaSolicitacao (DBSLT) | Tabela | SELECT | Consulta descrição de natureza de solicitação |
| TbNtzSltTbAreaTbFilial (DBSLT) | Tabela | SELECT | Consulta filial de execução |
| DbCor..TbFeriado | Tabela | SELECT | Consulta feriados nacionais |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View | Tipo | Operação | Breve Descrição |
|---------------------|------|----------|-----------------|
| TbControleArquivoRetorno (DBGESTAO) | Tabela | INSERT | Registra controle de processamento de arquivo |
| TbParcelaDebito | Tabela | UPDATE | Atualiza status, datas e valores de parcelas |
| TbContratoDebito | Tabela | UPDATE | Atualiza suspensão e motivos de contratos |
| TbLogArquivoDebito | Tabela | UPDATE | Atualiza status do arquivo (baixa/inconsistência) |
| TbControleCarga (DBGESTAO) | Tabela | INSERT/UPDATE | Gera e atualiza controles de carga para baixa |
| TbInformacaoBaixa (DBGESTAO) | Tabela | INSERT | Registra informações de baixa de parcelas |
| TbSolicitacao (DBSLT) | Tabela | INSERT | Cria solicitações SAC |
| TbSltCliente (DBSLT) | Tabela | INSERT | Associa cliente à solicitação |
| TbTarefaEspecial (DBSLT) | Tabela | INSERT | Registra tarefas especiais SAC |

## 9. Arquivos Lidos e Gravados

Não se aplica. O sistema não processa arquivos físicos diretamente, apenas consulta e atualiza registros em banco de dados referentes a arquivos de retorno já processados por outro sistema.

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas.

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| GDCC - ArquivosProcessados | Webservice SOAP | Consulta arquivos de retorno processados |
| GDCC - ConsultaRetorno | Webservice SOAP | Consulta detalhes dos retornos de débito |
| GDCC - Agendamento | Webservice SOAP | Agendamento e cancelamento de remessas |
| GDCC - ContaConvenio | Webservice SOAP | Consulta parâmetros de conta convênio |
| Sybase ASE (DbGestaoDebitoContaCorrente) | Banco de Dados | Banco principal do sistema GDCC |
| Sybase ASE (DBGESTAO) | Banco de Dados | Banco de gestão de contratos |
| Sybase ASE (DBSLT) | Banco de Dados | Banco de solicitações/tarefas SAC |
| Sybase ASE (DbCor) | Banco de Dados | Banco corporativo (feriados) |

## 13. Avaliação da Qualidade do Código

**Nota: 5/10**

**Justificativa:**

**Pontos Positivos:**
- Separação clara de responsabilidades (Reader, Processor, Writer)
- Uso de DAOs para acesso a dados
- Tratamento de exceções com códigos de erro específicos
- Uso de enums para constantes e tipos
- Logging adequado em pontos críticos

**Pontos Negativos:**
- **Código legado com muitos comentários de código antigo** não removido
- **Métodos muito longos** (ex: ItemWriter.handleWrite com múltiplas responsabilidades)
- **Nomes de métodos pouco descritivos** (ex: "extracaoSonar", "methodBatchA")
- **Código duplicado** em várias classes de webservice geradas por ferramentas
- **Falta de documentação JavaDoc** na maioria das classes
- **Mistura de idiomas** (português e inglês) em nomes de variáveis e métodos
- **Uso excessivo de synchronized** sem justificativa clara
- **Queries SQL hardcoded** em strings (dificulta manutenção)
- **Tratamento de exceções genérico** em alguns pontos (printStackTrace)
- **Dependências de versões antigas** (Axis 1.4, Sybase jConnect antigo)
- **Código com "code smells"** identificados pelo SonarQube e corrigidos de forma superficial

## 14. Observações Relevantes

1. **Sistema Legado**: Código aparenta ser de migração/refatoração, com muitos comentários de código antigo
2. **Framework Proprietário**: Utiliza framework batch customizado do Banco Votorantim (BV Framework)
3. **Processamento em Lote**: Commit a cada registro (commitInterval=1), pode impactar performance
4. **Integração Complexa**: Múltiplos bancos de dados e webservices envolvidos
5. **Regras de Negócio Específicas**: Tratamentos especiais para CEF (banco 104) e cadastro optante
6. **Geração de Código**: Muitas classes de webservice geradas automaticamente pelo Axis WSDL2Java
7. **Ambiente**: Configurações apontam para ambientes DEV, QA, UAT e PROD
8. **Execução**: Batch executado via script .bat com parâmetros de endpoints de webservices
9. **Timeout**: Transação configurada com timeout de 2700 segundos (45 minutos)
10. **Monitoramento**: Integração com sistema de monitoramento JMX (bv-monitoring)