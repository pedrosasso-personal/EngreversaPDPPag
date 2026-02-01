# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de validação e manutenção de contratos financeiros do produto FLEX INBV. Realiza validação completa de dados contratuais incluindo participantes (pessoas físicas e jurídicas), custos, seguros, favorecidos de recebimento e informações de desembolso. O sistema valida regras de negócio complexas, consistência de dados cadastrais contra bases corporativas e integra-se com serviços externos para obtenção de domínios técnicos e dados de parceiros comerciais. Implementa conversão de custos entre diferentes modalidades através de mapeamento de domínios.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ManutencaoContratoFinanceiroBackendServiceImpl** | Endpoint SOAP principal - orquestra validação de contratos, completar dados e conversão de custos |
| **ValidatorBaseServiceImpl** | Orquestrador central de validação - executa validadores bean e custom sobre requests |
| **BeanValidatorServiceImpl** | Engine de validação por reflexão - processa annotations declarativas (@NotNull, @Validator, etc) |
| **ManutencaoContratoFinanceiroDaoImpl** | DAO para validação de códigos de domínio em tabelas corporativas (20+ validações) |
| **MapeamentoDominioIntegrationServiceImpl** | Cliente WS para consulta de mapeamento de domínios técnicos |
| **GestaoParceiroIntegrationServiceImpl** | Cliente WS para busca de dados de parceiros comerciais e favorecidos |
| **ContratoValidacaoTypeTOConverter** | Conversão stub SOAP para TO de domínio (contrato) |
| **ParticipantesValidacaoTypeTOConverter** | Conversão de participantes (PF/PJ) stub para TO |
| **ValorLiberadoCustomValidatorImpl** | Validador regra: soma valores liberados favorecidos = valor total contrato |
| **ParticipantesCustomValidatorImpl** | Validador regra: obrigatoriedade de proponente (papel=1) |
| **EnderecosCustomValidatorImpl** | Validador regra: exatamente 1 endereço de correspondência por participante |
| **ValidaFavorecidoRecebimentoPrincipalCustomImpl** | Validador regra: favorecido deve estar cadastrado e ativo |
| **CpfCnpjValidador** | Validador formato e dígitos verificadores CPF/CNPJ (módulo 11) |
| **WebserviceBeanMapper** | Mapeamento automático objeto-stub usando reflexão |

---

## 3. Tecnologias Utilizadas

- **Java EE 7** - Plataforma base
- **EJB 3.1** - Stateless Session Beans
- **JAX-WS / SOAP** - Web Services
- **Spring Framework** - Injeção de dependências, JDBC Template
- **Spring JDBC** - Acesso a dados (NamedParameterJdbcTemplate)
- **SLF4J** - Logging
- **Joda-Time** - Manipulação de datas
- **Java Reflection API** - Validação declarativa via annotations
- **Maven** - Gerenciamento de dependências e build
- **WebSphere Application Server** - Servidor de aplicação (deployment descriptors IBM)
- **SQL Server** - Banco de dados corporativo (schema DBCOR)
- **WS-Security** - Segurança em Web Services (policy attachments)

---

## 4. Principais Endpoints REST

Não se aplica - o sistema utiliza **Web Services SOAP**, não REST.

### Endpoints SOAP:

| Operação | Descrição | Classe Implementadora |
|----------|-----------|----------------------|
| **validarDadosContrato** | Valida dados completos do contrato financeiro (participantes, custos, seguros, favorecidos) | ManutencaoContratoFinanceiroBackendServiceImpl |
| **completarDadosContrato** | Completa dados do contrato (implementação vazia - placeholder) | ManutencaoContratoFinanceiroBackendServiceImpl |
| **converterCusto** | Converte custos entre modalidades usando mapeamento de domínios | ManutencaoContratoFinanceiroBackendServiceImpl |

**Namespace:** `http://www.bv.com.br/varejo/prodServicoParceiro/manutencaoContratoFinanceiroBackendService/v1`

**Segurança:** @RolesAllowed("flex-integracao", "intr-middleware")

---

## 5. Principais Regras de Negócio

1. **Validação de Proponente Obrigatório**: Todo contrato deve ter pelo menos 1 participante com codigoTipoPapel=1 (proponente)

2. **Consistência Valor Liberado**: Soma dos valores liberados de todos os favorecidos principais deve ser igual ao valorTotalLiberado do contrato (exceção: produto=17 e modalidade=74 - CVC)

3. **Consistência Valor Comissão**: Soma dos valorTotalComissao dos favorecidos de comissão deve ser igual ao valorTotalComissao do contrato

4. **Consistência Valor Seguro**: Soma dos valorParcela de todos os seguros deve ser igual ao valorTotalSeguro do contrato

5. **Validação Valor Entrada**: valorEntrada deve ser menor que valorFinanciamento

6. **Limites Valor Liberado por Modalidade**: Para modalidade=62 (exceto parceiro=365352), soma dos valores liberados deve estar entre R$ 50.000,00 e R$ 70.000,00

7. **Endereço de Correspondência**: Cada participante deve ter exatamente 1 endereço com indicadorEnderecoCorrespondencia=true

8. **Validação Pessoa Física/Jurídica**: Participante com tipoPessoa=F deve ter dados de PessoaFisica preenchidos; tipoPessoa=J deve ter PessoaJuridica

9. **Receita Obrigatória**: Pelo menos 1 participante deve ter receita ou faturamento mensal maior que zero

10. **Favorecido Principal Obrigatório**: Se tipoDesembolso diferente de "PARCELADO", deve existir favorecido principal

11. **Favorecido Autorizado**: Favorecido principal deve existir na lista de participantes (match por codigoTipoPapel + CPF/CNPJ) e estar cadastrado/ativo no sistema

12. **Validação SMS**: Se indicadorPermiteSms=true, participante deve ter telefone celular (codigoTipoTelefone=3)

13. **Data Contrato Não-Retroativa**: dataContrato não pode ser anterior à data atual

14. **Conversão de Custos**: Custos são convertidos entre modalidades usando mapeamento de domínio CUSTOBV-UDE-VALS com chave FLEX-{produto}{modalidade}

15. **Validação Cadastral**: Todos os códigos de domínio (tipo custo, papel, ramo atividade, forma constituição, etc.) devem existir nas tabelas corporativas

---

## 6. Relação entre Entidades

### Hierarquia Principal:

**ValidarDadosContratoRequestTO** (raiz)
- **ContratoValidacaoTypeTO** (1:1)
  - Dados básicos: produto, modalidade, valores, datas, tipo taxa/cobrança
  - **CustosValidacaoTypeTO** (1:N) - Lista de custos
    - **CustoValidacaoTypeTO** - codigoTipoCusto, valorCusto
  - **SegurosTypeTO** (1:N) - Lista de seguros
    - **SeguroTypeTO** - codigoTipoSeguro, valorParcela
  - **InformacaoDesembolsoTypeTO** (1:1)
    - tipoDesembolso, quantidadeParcelas, dataPrimeiroDesembolso
  - **FavorecidosRecebimentoPrincipalTypeTO** (1:N)
    - **FavorecidoRecebimentoPrincipalTypeTO** - codigoTipoFavorecido, valorLiberado, dados bancários
  - **FavorecidosRecebimentoComissaoTypeTO** (1:N)
    - **FavorecidoRecebimentoComissaoTypeTO** - valorTotalComissao, dados bancários

- **ParticipantesValidacaoTypeTO** (1:N)
  - **ParticipanteValidacaoTypeTO**
    - codigoTipoPapel, tipoPessoa, cpfCnpj
    - **PessoaFisicaTypeTO** (0:1) - nome, dataNascimento, estadoCivil, profissão
    - **PessoaJuridicaTypeTO** (0:1) - razaoSocial, nomeFantasia, ramoAtividade
    - **EnderecosTypeTO** (1:N) - Lista de endereços
    - **TelefonesTypeTO** (1:N) - Lista de telefones
    - **ReceitasTypeTO** (1:N) - Lista de receitas
    - **ImoveisTypeTO** (0:N) - Lista de imóveis
    - **FaturamentoMensalTypeTO** (0:1) - Para PJ

### Relacionamentos:
- Contrato 1:N Participantes
- Contrato 1:N Custos
- Contrato 1:N Seguros
- Contrato 1:N Favorecidos (Principal e Comissão)
- Participante 1:1 PessoaFisica OU 1:1 PessoaJuridica
- Participante 1:N Endereços
- Participante 1:N Telefones
- Participante 1:N Receitas
- Participante 0:N Imóveis

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbTipoCusto | tabela | SELECT | Validação existência código tipo de custo |
| TbPapel | tabela | SELECT | Validação código tipo de papel do participante |
| TbRamoAtividade | tabela | SELECT | Validação código ramo de atividade (PJ) |
| TbFormaConstituicaoPessoaJrdca | tabela | SELECT | Validação código forma de constituição (PJ) |
| TbTipoFontePagadora | tabela | SELECT | Validação código tipo fonte pagadora |
| TbTipoProfissional | tabela | SELECT | Validação código tipo profissional |
| TbEstadoCivil | tabela | SELECT | Validação código estado civil (PF) |
| TbTipoDocumento | tabela | SELECT | Validação código tipo de documento |
| TB_CEP_UF | tabela | SELECT | Validação código estado/UF por CEP |
| TbProfissao | tabela | SELECT | Validação código profissão |
| TbTipoBeneficioInss | tabela | SELECT | Validação código tipo benefício INSS |
| TbNivelCargo | tabela | SELECT | Validação código nível de cargo |
| TbTipoReceita | tabela | SELECT | Validação código tipo de receita |
| TbTipoOutroRendimento | tabela | SELECT | Validação código tipo outro rendimento |
| TbTipoEndereco | tabela | SELECT | Validação código tipo de endereço |
| TbTipoTelefone | tabela | SELECT | Validação código tipo de telefone |
| TbTipoPropriedadeBem | tabela | SELECT | Validação código tipo propriedade de bem/imóvel |
| TbBanco | tabela | SELECT | Validação código banco |
| TbFormaPagto | tabela | SELECT | Validação código forma de pagamento |
| TbFavorecidoAutorizado | tabela | SELECT | Validação favorecido autorizado (codigoParceiro + cpfCnpj) |

**Schema:** DBCOR (SQL Server)

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica - o sistema realiza apenas operações de leitura/consulta para validação. Não há operações de INSERT, UPDATE ou DELETE.

---

## 9. Arquivos Lidos e Gravados

Não se aplica - o sistema não manipula arquivos. Toda comunicação é realizada via Web Services SOAP.

---

## 10. Filas Lidas

Não se aplica - o sistema não consome mensagens de filas.

---

## 11. Filas Geradas

Não se aplica - o sistema não publica mensagens em filas.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição | Endpoint |
|-----------------|------|-----------|----------|
| **Mapeamento Domínios Técnicos** | SOAP WS | Consulta mapeamento de domínios técnicos para conversão de custos. Operações: obterDominio, listarDominios. Domínio usado: CUSTOBV-UDE-VALS | corporativo/integradorCanais/mapeamentoDominiosTechinicalService/v1 |
| **Gestão Parceiro Comercial** | SOAP WS | Busca dados de parceiros comerciais e favorecidos (dados básicos + contas comissão/principal/serviço). Operação: buscarParceiros | varejo/prodServicoParceiro/gestaoParceiroComercialBusinessService/v4 |
| **Banco de Dados Corporativo (DBCOR)** | SQL Server | Validação de códigos de domínio em 20+ tabelas corporativas (tipos de custo, papel, profissão, banco, etc.) | Schema DBCOR via Spring JDBC |

**Observação:** Integração com Gestão Parceiro possui código comentado (TODO) para validação de favorecidos ativos.

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Excelente separação de responsabilidades seguindo arquitetura SOA modular (business, commons, domain, integration, persistence, ws)
- Framework de validação declarativa bem estruturado usando annotations e reflexão, promovendo extensibilidade e reuso
- Uso adequado de padrões de projeto (Builder, Converter, DAO, Service Layer)
- Conversão automática stub-TO reduz código boilerplate
- Logging consistente com SLF4J
- Validações de negócio bem isoladas em classes específicas
- Boa organização de enumerações para domínios

**Pontos Negativos:**
- **Ausência completa de testes unitários** no pacote analisado (crítico para manutenibilidade)
- Múltiplos métodos vazios/placeholder (completarDadosContrato, validações comentadas com TODO)
- Código comentado em produção (validação favorecidos ativos, valorRetencao)
- Algumas validações incompletas (DataPrimeiroDesembolsoValidatorImpl apenas com TODO)
- Falta documentação JavaDoc nas classes principais
- Acoplamento com tecnologias específicas (WebSphere descriptors) dificulta portabilidade
- Conversores com lógica de negócio misturada (ex: setIdentifiers no builder)
- Validações com números mágicos (códigos hardcoded: produto=17, modalidade=74, parceiro=365352)

**Recomendações:**
1. Implementar suite completa de testes unitários e integração
2. Remover código comentado ou implementar TODOs pendentes
3. Adicionar JavaDoc nas interfaces e classes principais
4. Externalizar constantes de negócio (códigos de produto, modalidade) para configuração
5. Completar validações pendentes ou remover se não aplicáveis

---

## 14. Observações Relevantes

1. **Sistema em Desenvolvimento**: Presença de múltiplos TODOs e métodos vazios indica que o sistema ainda está em fase de implementação ou evolução

2. **Validação Híbrida Sofisticada**: Combina validações declarativas via annotations (@NotNull, @Validator) com validadores customizados de regras de negócio complexas, proporcionando flexibilidade e manutenibilidade

3. **Conversão de Custos Dinâmica**: A operação converterCusto utiliza mapeamento de domínios externos (CUSTOBV-UDE-VALS) para conversão entre modalidades, permitindo configuração sem alteração de código

4. **Segurança Baseada em Roles**: Endpoints protegidos com @RolesAllowed (flex-integracao, intr-middleware) para controle de acesso

5. **Ambiente Multi-Stage**: Configuração preparada para múltiplos ambientes (DES/QA/UAT/PRD) via properties

6. **WebSphere Específico**: Presença de descriptors IBM (ibm-application-bnd.xml, deployment.xml) indica dependência do WebSphere Application Server

7. **Auditoria**: Integração com trilha de auditoria corporativa (corporativo/v1)

8. **Validação Cadastral Extensiva**: Sistema valida mais de 20 tipos diferentes de códigos de domínio contra tabelas corporativas, garantindo consistência referencial

9. **Regras de Negócio Específicas por Produto/Modalidade**: Validações condicionais baseadas em combinações produto-modalidade (ex: CVC produto=17/modalidade=74, limites modalidade=62)

10. **Handler de Logging Customizado**: Web Services com handler específico para logging de requisições/respostas SOAP

11. **Padrão de Nomenclatura**: Uso consistente de sufixos (Impl, TO, Validator, Converter, Builder) facilita navegação no código

12. **Validação CPF/CNPJ Robusta**: Implementação completa de validação com dígitos verificadores usando módulo 10 e 11