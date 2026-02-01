# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **GDCF - Gestão de Débito em Conta** é uma aplicação Java EE desenvolvida para o Banco Votorantim que gerencia débitos automáticos em conta corrente de contratos financeiros. O sistema permite visualizar, alterar e gerenciar contas de débito, tratar estornos, visualizar inconsistências e registrar contratos de refinanciamento. Integra-se com o sistema de Gestão de Contratos e bases de dados legadas (Tools), fornecendo funcionalidades através de serviços EJB e Web Services.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `AlterarContaBusinessImpl` | Implementa regras de negócio para alteração de contas de débito, consulta de contratos e parcelas |
| `VisualizarSacBusinessImpl` | Gerencia consultas de contratos SAC e parcelas de débito |
| `TratarEstornoBusinessImpl` | Implementa lógica de negócio para tratamento de estornos de débito |
| `VisualizarInconsistenciaBusinessImpl` | Gerencia visualização de inconsistências em débitos |
| `ContratoRefinBusinessImpl` | Gerencia inserção de contratos de refinanciamento |
| `AlterarContaDaoImpl` | Acesso a dados para alteração de contas e logs |
| `ContratoDebitoDaoImpl` | Persistência de contratos de débito |
| `ParcelaDebitoDaoImpl` | Gerenciamento de parcelas de débito |
| `GestaoContratosDaoImpl` | Integração com bases de Gestão de Contratos |
| `BatchKeyGenerator` | Geração de sequenciais para chaves primárias |

## 3. Tecnologias Utilizadas

- **Java EE** (EJB 2.1)
- **Spring Framework 2.0** (Injeção de Dependência e Configuração)
- **Maven** (Gerenciamento de dependências e build)
- **JBoss 4.2.3** (Servidor de aplicação)
- **Apache Axis2 1.3** (Web Services SOAP)
- **Apache Tomcat** (Servidor web para web services)
- **JDBC** (Acesso a banco de dados)
- **Sybase** (Banco de dados - DBGESTAO, DBCOR)
- **XDoclet** (Geração de configurações Spring)
- **BV Framework** (Framework proprietário do Banco Votorantim)

## 4. Principais Endpoints REST

Não se aplica. O sistema utiliza Web Services SOAP (Axis2) e serviços EJB, não REST.

**Serviços SOAP/EJB disponíveis:**
- `BV-bvf-nnegocios-gdcf.AlterarConta.*`
- `BV-bvf-nnegocios-gdcf.VisualizarSAC.*`
- `BV-bvf-nnegocios-gdcf.visualizarinconsistencia.*`
- `BV-bvf-nnegocios-gdcf.tratarestorno.*`
- `BV-bvf-nnegocios-gdcf.refin.*`

## 5. Principais Regras de Negócio

1. **Conversão de Contratos Legados**: Converte números de contratos do sistema legado (Tools - 9 dígitos) para contratos do Gestão
2. **Validação de Bancos Conveniados**: Verifica se o banco informado está parametrizado para débito automático antes de registrar
3. **Suspensão de Débito**: Permite suspender débitos com motivo de suspensão registrado
4. **Agendamento de Cancelamento**: Agenda cancelamento de parcelas de débito futuras
5. **Tratamento de Estornos**: Permite alterar data de estorno de parcelas debitadas
6. **Histórico de Alterações**: Registra todas as alterações de conta em tabela de log (TbLogContratoDebito)
7. **Validação de Filtros**: Exige ao menos um filtro de pesquisa nas consultas
8. **Atualização de Autorização**: Atualiza status de autorização de débito ao alterar conta
9. **Complementação de Dados**: Busca dados complementares do contrato em múltiplas bases (DBGESTAO, DBCOR, bases específicas)
10. **Controle de Status de Parcelas**: Gerencia status das parcelas (Agendado, Cancelado, Erro, Retornado, Estorno)

## 6. Relação entre Entidades

**Principais Entidades e Relacionamentos:**

- **ContratoDebitoVO**: Representa um contrato de débito automático
  - Relaciona-se com **MotivoSuspensaoVO** (motivo de suspensão do débito)
  - Contém múltiplas **ParcelaDebitoVO** (parcelas do contrato)
  
- **ParcelaDebitoVO**: Representa uma parcela de débito
  - Pertence a um **ContratoDebitoVO**
  - Possui status (StatusParcelaDebitoEnum)
  
- **LogContratoDebitoVO**: Histórico de alterações de contratos

- **AlterarContaVO/DTO**: Dados para alteração de conta de débito

- **DadosContratoGestaoDTO**: Dados complementares do sistema de Gestão de Contratos

- **TratarEstornoDTO**: Dados para tratamento de estornos

- **VisualizarInconsistenciaDTO**: Dados de inconsistências em débitos

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBGESTAO..TbContratoDebito | Tabela | SELECT | Contratos de débito automático |
| DBGESTAO..TbParcelaDebito | Tabela | SELECT | Parcelas de débito dos contratos |
| DBGESTAO..TbMotivoSuspensao | Tabela | SELECT | Motivos de suspensão de débito |
| DBCOR..TbPessoa | Tabela | SELECT | Dados cadastrais de pessoas |
| DBCOR..TbContratoPrincipal | Tabela | SELECT | Contratos principais |
| DBCOR..TbProduto | Tabela | SELECT | Produtos financeiros |
| DBCOR..TbConexao | Tabela | SELECT | Conexões de banco de dados |
| DBCOR..TbOperador | Tabela | SELECT | Operadores do sistema |
| DBCOR..TbColaborador | Tabela | SELECT | Colaboradores |
| DBCOR..TbModalidadeProduto | Tabela | SELECT | Modalidades de produtos |
| DBCOR..TbVeiculoLegal | Tabela | SELECT | Veículos legais |
| ${nomeBD}..TbContrato | Tabela | SELECT | Contratos (base dinâmica) |
| ${nomeBD}..TbContratoFinanceiro | Tabela | SELECT | Contratos financeiros (base dinâmica) |
| DbGestaoDebitoContaCorrente..TbAutorizacaoDebitoPrpsaCntro | Tabela | SELECT | Autorizações de débito por proposta/contrato |
| DbGestaoDebitoContaCorrente..TbEventoRegistroAutorizacaoDbo | Tabela | SELECT | Eventos de registro de autorização |
| DbGestaoDebitoContaCorrente..TbRegistroAutorizacaoDebito | Tabela | SELECT | Registros de autorização de débito |
| DBGESTAO..VwTbContrato | View | SELECT | View de contratos |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBGESTAO..TbContratoDebito | Tabela | INSERT/UPDATE | Inserção de novos contratos e atualização de dados bancários |
| DBGESTAO..TbParcelaDebito | Tabela | INSERT/UPDATE | Inserção de parcelas de cancelamento e atualização de status |
| DBGESTAO..TbLogContratoDebito | Tabela | INSERT | Registro de histórico de alterações de contratos |
| DbGestaoDebitoContaCorrente..TbAutorizacaoDebitoPrpsaCntro | Tabela | UPDATE | Inativação de autorizações de débito |

## 9. Arquivos Lidos e Gravados

Não se aplica. O sistema não realiza leitura ou gravação de arquivos diretamente. O processamento é baseado em banco de dados e serviços.

## 10. Filas Lidas

Não se aplica. Não há evidências de consumo de filas (JMS, Kafka, RabbitMQ) no código analisado.

## 11. Filas Geradas

Não se aplica. Não há evidências de publicação em filas no código analisado.

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|----------------|------|-----------|
| ConsultaBancosConveniadosServices | Web Service SOAP | Consulta bancos conveniados para débito automático (validação) |
| Gestão de Contratos | Banco de Dados | Integração com múltiplas bases de dados de gestão de contratos (dinâmicas) |
| Sistema Legado Tools | Banco de Dados | Conversão de números de contratos legados |
| DBCOR | Banco de Dados | Base corporativa com dados de pessoas, produtos, operadores |

## 13. Avaliação da Qualidade do Código

**Nota: 5/10**

**Justificativa:**

**Pontos Positivos:**
- Separação clara de camadas (Business, DAO, Mapper)
- Uso de padrões como DAO e RowMapper
- Injeção de dependências via Spring
- Tratamento de exceções customizadas
- Uso de logs estruturados

**Pontos Negativos:**
- **Código legado com práticas antigas** (EJB 2.1, Spring 2.0)
- **SQL embarcado em arquivos XML** dificulta manutenção
- **Substituição dinâmica de nomes de banco** (`${nomeBD}`) é frágil e perigosa
- **Comentários em português** com caracteres mal codificados
- **Falta de testes unitários** evidentes
- **Código gerado automaticamente** (Axis2 stubs) muito verboso
- **Mistura de responsabilidades** em algumas classes
- **Uso de tipos primitivos** onde objetos seriam mais apropriados
- **Tratamento de exceções inadequado** (catch sem re-throw apropriado)
- **Código comentado** não removido
- **Conversão manual de tipos** poderia usar frameworks
- **Falta de validações consistentes** de entrada

## 14. Observações Relevantes

1. **Arquitetura Multi-Base**: O sistema trabalha com múltiplas bases de dados (DBGESTAO, DBCOR e bases dinâmicas de gestão), exigindo lógica complexa para determinar onde buscar dados

2. **Sistema Legado**: Forte dependência de sistemas legados (Tools) com conversão de números de contrato

3. **Framework Proprietário**: Utiliza extensivamente o BV Framework, framework proprietário do Banco Votorantim

4. **Geração de Sequenciais**: Usa stored procedures específicas do Sybase para geração de IDs (`prObterSequencialDisponivel`)

5. **Deploy Complexo**: Estrutura de deploy envolve JBoss (EAR) e Tomcat (Web Services AAR)

6. **Configuração via XDoclet**: Usa XDoclet para geração de configurações Spring a partir de anotações JavaDoc

7. **Transações Gerenciadas**: Usa transações gerenciadas por container (CMT) com diferentes níveis de propagação

8. **Limitações Técnicas**: Truncamento de número de conta para 9 caracteres devido a limitação de tipo INT no banco

9. **Incidentes Registrados**: Código contém referências a incidentes específicos (ex: 167336) com código comentado

10. **Encoding Issues**: Presença de caracteres mal codificados nos comentários sugere problemas de encoding históricos

11. **Versionamento**: Sistema na versão 0.18.0, indicando maturidade relativa mas ainda em evolução

12. **Jenkins Integration**: Possui configuração para integração contínua via Jenkins