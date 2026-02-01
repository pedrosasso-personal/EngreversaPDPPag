# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de cálculo de taxas de financiamento para produtos de varejo do Banco Votorantim. O sistema realiza cálculos complexos de CET (Custo Efetivo Total), taxa pactuada, taxa gerencial, IOF e taxa de retenção para operações de crédito, considerando diversos custos, modalidades de produtos e características específicas de cada financiamento.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **TaxaFinanciamentoBeanImpl** | Orquestra o cálculo de todas as taxas de financiamento, coordenando chamadas aos demais componentes |
| **CalculoCetBeanImpl** | Calcula a taxa CET (Custo Efetivo Total) e taxa pactuada, incluindo tratamento de IOF e custos |
| **CalculoTaxaBeanImpl** | Realiza cálculos de taxas utilizando método de Newton-Raphson para dias corridos |
| **CalculoIofBeanImpl** | Calcula IOF por parcela considerando amortização e juros |
| **IofBeanImpl** | Gerencia cálculo de IOF com alíquotas e gross-up |
| **ImpostoAliquotaBeanImpl** | Obtém alíquotas de IOF do banco de dados |
| **TaxaMercadoBeanImpl** | Obtém taxa TIR (Taxa Interna de Retorno) do mercado |
| **TipoCustoBeanImpl** | Obtém informações sobre tipos de custos |
| **TaxaFinanciamentoBackendServiceImpl** | Implementação do Web Service SOAP que expõe a funcionalidade |

## 3. Tecnologias Utilizadas

- **Java EE 6+** (EJB 3.1, JAX-WS)
- **Spring Framework** (Spring JDBC para acesso a dados)
- **IBM WebSphere Application Server** (servidor de aplicação)
- **Oracle Database** (banco de dados principal via JDBC)
- **Sybase** (banco secundário para propostas)
- **Maven** (gerenciamento de dependências e build)
- **Apache Commons** (bibliotecas utilitárias)
- **SLF4J/Log4j2** (logging)
- **SOAP Web Services** (JAX-WS)
- **CDI** (Contexts and Dependency Injection)

## 4. Principais Endpoints REST

Não se aplica. O sistema utiliza Web Services SOAP, não REST.

**Endpoint SOAP:**
- **Serviço:** TaxaFinanciamentoFlexBackendService
- **Operação:** listarTaxasFinanciamento
- **Namespace:** http://votorantim.com.br/flex/calc/ws/TaxaFinanciamentoFlexBackendService/v1
- **Descrição:** Calcula todas as taxas de financiamento (CET, pactuada, gerencial, IOF, retenção)

## 5. Principais Regras de Negócio

1. **Cálculo de CET**: Considera valor financiado, custos somáveis, IOF e parcelas para calcular o Custo Efetivo Total
2. **Cálculo de Taxa Pactuada**: Inclui valor financiado mais custos totais (exceto serviço de recebimento que é somado às parcelas)
3. **Cálculo de Taxa Gerencial**: Calculada quando há custos de "Acordo Não CET"
4. **Validação de Taxa Pactuada vs TIR**: Se taxa pactuada for inferior à TIR, remove custos CPP e recalcula
5. **Cálculo de IOF com Gross-Up**: IOF é calculado iterativamente para compensar o próprio valor do IOF no financiamento
6. **IOF para Ressarcimento**: Em produtos de ressarcimento, o IOF é zerado após o cálculo
7. **Taxa de Retenção**: Calculada apenas quando há informação de subsídio com valor de retenção
8. **Cálculo por Dias Corridos**: Utiliza método de Newton-Raphson para cálculo preciso de taxas considerando dias corridos entre parcelas
9. **Diferenciação Proposta vs Contrato**: Sistema consulta bases diferentes (DBCOR ou SybCred) dependendo se é proposta ou contrato
10. **Serviços Financiados**: Custos marcados como serviços financiados são tratados separadamente no cálculo

## 6. Relação entre Entidades

**Entidades Principais:**

- **ParamTaxaFinanciamentoInfo**: Agrupa todos os parâmetros de entrada (produto, modalidade, valores, datas, custos)
- **TaxaFinanciamentoVarejoInfo**: Agrupa todas as taxas calculadas (CET, pactuada, gerencial, IOF, retenção)
- **RetornoCustosInfo**: Representa um custo individual com código, valor e flags de controle
- **ParcelaIofInfo**: Representa uma parcela com informações de IOF, juros, amortização e saldo
- **ImpostoAliquotaInfo**: Contém alíquotas de IOF (padrão, máxima, excedente)
- **TaxaMercadoInfo**: Contém taxas de mercado (TIR) por prazo e período
- **TipoCustoInfo**: Contém características de um tipo de custo (se soma ao CET, se é serviço financiado)

**Relacionamentos:**
- ParamTaxaFinanciamentoInfo contém lista de RetornoCustosInfo
- ParamTaxaFinanciamentoInfo contém InformacaoSubsidioInfo (opcional)
- Cálculos geram lista de ParcelaIofInfo
- ImpostoAliquotaInfo é consultada por produto/modalidade/tipo pessoa

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| DBCOR..TbImpostoAliquota | tabela | SELECT | Alíquotas padrão de IOF por tipo de pessoa e período |
| DBCOR..TbExcecaoAliquotaModalidade | tabela | SELECT | Alíquotas de IOF específicas por produto/modalidade |
| DBCOR..TbTaxaMercado | tabela | SELECT | Taxas TIR de mercado por prazo e período |
| DBCOR..TbTipoCusto | tabela | SELECT | Tipos de custos e suas características |
| DBCOR..TbTipoAgrupamentoTipoCusto | tabela | SELECT | Agrupamento de custos (identifica serviços financiados) |

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema realiza apenas operações de leitura (SELECT).

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| *-sql.xml | leitura | Pacote persistence/dao/impl | Arquivos XML contendo queries SQL parametrizadas |
| errorMessages.properties | leitura | commons/resources | Mensagens de erro do sistema |
| roles.properties | leitura | commons/resources | Definição de roles de segurança |
| log4j2.xml | leitura | Diversos módulos | Configuração de logging |

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas.

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Oracle DBCOR | JDBC | Banco de dados principal para consulta de alíquotas, taxas e custos em contratos |
| Sybase SybCred | JDBC | Banco de dados secundário para consulta de taxas e custos em propostas |
| IBM WebSphere | Servidor App | Servidor de aplicação que hospeda os EJBs e Web Services |

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades em camadas (business, persistence, domain, ws)
- Uso adequado de padrões Java EE (EJB, CDI, JAX-WS)
- Logging estruturado com SLF4J
- Tratamento de exceções consistente
- Uso de interfaces locais para EJBs
- Queries SQL externalizadas em arquivos XML
- Documentação JavaDoc presente em pontos-chave

**Pontos de Melhoria:**
- Métodos muito longos (ex: `calcularTaxasFinanciamento` com mais de 200 linhas)
- Complexidade ciclomática alta em alguns métodos
- Uso excessivo de variáveis de instância em vez de parâmetros
- Falta de testes unitários para classes críticas de cálculo
- Comentários em português misturados com código em inglês
- Alguns magic numbers sem constantes nomeadas
- Acoplamento entre camadas poderia ser reduzido
- Falta de validação mais robusta de entrada em alguns pontos

## 14. Observações Relevantes

1. **Cálculo Financeiro Complexo**: O sistema implementa cálculos financeiros sofisticados usando método de Newton-Raphson para convergência de taxas
2. **Dual Database**: Sistema acessa dois bancos diferentes (Oracle e Sybase) dependendo se é proposta ou contrato
3. **Segurança**: Implementa autenticação via WS-Security (UsernameToken e Certificate) com diferentes níveis de classificação
4. **Versionamento**: Sistema possui versionamento claro (v1) e múltiplos WSDLs por ambiente (DES, QA, UAT, PRD)
5. **Auditoria**: Implementa trilha de auditoria via SOAP headers customizados
6. **Gross-Up de IOF**: Implementação específica para cálculo iterativo de IOF que se auto-financia
7. **Produtos Específicos**: Tratamento especial para produto "Ressarcimento" (código 16)
8. **Custos Especiais**: Tratamento diferenciado para custos CPP, IOF, TAC e Acordo Não CET
9. **Dias Corridos**: Cálculos consideram dias corridos reais entre datas, não apenas periodicidade fixa
10. **Maven Multi-módulo**: Projeto bem estruturado em módulos Maven (commons, domain, persistence, business, ws, ear)