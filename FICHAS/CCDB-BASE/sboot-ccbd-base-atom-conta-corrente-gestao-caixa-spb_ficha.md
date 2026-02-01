```markdown
## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema "ContaCorrenteGestaoCaixaSpb" é um serviço atômico desenvolvido para gerenciar informações de conta corrente, incluindo históricos e totais de clientes, fundos, nomes e veículos, além de variações e lançamentos. Ele utiliza o framework Spring Boot e integra-se com bancos de dados para realizar operações de leitura e escrita.

### 2. Principais Classes e Responsabilidades
- **AppProperties**: Configurações de propriedades da aplicação.
- **ContaCorrenteGestaoCaixaSpbConfiguration**: Configuração de beans e integração com Jdbi para acesso ao banco de dados.
- **OpenApiConfiguration**: Configuração do Swagger para documentação de APIs.
- **GlobalExceptionHandler**: Tratamento global de exceções.
- **JdbiCCGestaoCaixaSpbRepository**: Implementação de repositório para acesso ao banco de dados.
- **ContaCorrenteGestaoCaixaSpbService**: Serviço de domínio para operações de conta corrente.
- **ContaCorrenteGestaoCaixaSpbController**: Controlador REST para exposição de endpoints.
- **Domain Classes (ex: CCDiaUtilAnterior, CCHistoricoCliente)**: Representação de entidades de domínio.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- Jdbi
- Swagger
- Sybase
- Maven

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET    | /v1/app-properties | AppPropertiesController | Retorna as propriedades da aplicação. |
| GET    | /v1/conta-corrente-gestao-caixa-spb/getCCHistoricoClientes | ContaCorrenteGestaoCaixaSpbController | Retorna o histórico de clientes. |
| GET    | /v1/conta-corrente-gestao-caixa-spb/getCCHistoricoClientesCredor | ContaCorrenteGestaoCaixaSpbController | Retorna o histórico de clientes credores. |
| GET    | /v1/conta-corrente-gestao-caixa-spb/getCCHistoricoFundos | ContaCorrenteGestaoCaixaSpbController | Retorna o histórico de fundos. |
| GET    | /v1/conta-corrente-gestao-caixa-spb/getCCHistoricoNomes | ContaCorrenteGestaoCaixaSpbController | Retorna o histórico de nomes. |
| GET    | /v1/conta-corrente-gestao-caixa-spb/getCCHistoricoVeiculos | ContaCorrenteGestaoCaixaSpbController | Retorna o histórico de veículos. |
| GET    | /v1/conta-corrente-gestao-caixa-spb/getCCTotalClientes | ContaCorrenteGestaoCaixaSpbController | Retorna o total de clientes. |
| GET    | /v1/conta-corrente-gestao-caixa-spb/getCCTotalClientesAnalitico | ContaCorrenteGestaoCaixaSpbController | Retorna o total analítico de clientes. |
| GET    | /v1/conta-corrente-gestao-caixa-spb/getCCTotalClientesCredor | ContaCorrenteGestaoCaixaSpbController | Retorna o total de clientes credores. |
| GET    | /v1/conta-corrente-gestao-caixa-spb/getCCTotalFundos | ContaCorrenteGestaoCaixaSpbController | Retorna o total de fundos. |
| GET    | /v1/conta-corrente-gestao-caixa-spb/getCCTotalFundosAnalitico | ContaCorrenteGestaoCaixaSpbController | Retorna o total analítico de fundos. |
| GET    | /v1/conta-corrente-gestao-caixa-spb/getCCTotalNomes | ContaCorrenteGestaoCaixaSpbController | Retorna o total de nomes. |
| GET    | /v1/conta-corrente-gestao-caixa-spb/getCCTotalNomesAnalitico | ContaCorrenteGestaoCaixaSpbController | Retorna o total analítico de nomes. |
| GET    | /v1/conta-corrente-gestao-caixa-spb/getCCTotalVeiculos | ContaCorrenteGestaoCaixaSpbController | Retorna o total de veículos. |
| GET    | /v1/conta-corrente-gestao-caixa-spb/getCCVariacao | ContaCorrenteGestaoCaixaSpbController | Retorna a variação de conta corrente. |
| GET    | /v1/conta-corrente-gestao-caixa-spb/getCCVariacaoAnalitico | ContaCorrenteGestaoCaixaSpbController | Retorna a variação analítica de conta corrente. |
| GET    | /v1/conta-corrente-gestao-caixa-spb/getLancamentosNCC | ContaCorrenteGestaoCaixaSpbController | Retorna os lançamentos NCC. |
| POST   | /v1/conta-corrente-gestao-caixa-spb/inserirTempAgrupContaCorrente | ContaCorrenteGestaoCaixaSpbController | Insere agrupamento temporário de conta corrente. |
| GET    | /v1/conta-corrente-gestao-caixa-spb/getTempAgrupContaCorrente | ContaCorrenteGestaoCaixaSpbController | Retorna agrupamento temporário de conta corrente. |
| POST   | /v1/conta-corrente-gestao-caixa-spb/excluirTempAgrupContaCorrente | ContaCorrenteGestaoCaixaSpbController | Exclui agrupamento temporário de conta corrente. |

### 5. Principais Regras de Negócio
- Cálculo de saldos disponíveis e totais para diferentes categorias de contas (clientes, fundos, nomes, veículos).
- Manipulação de agrupamentos temporários de conta corrente.
- Determinação de dia útil anterior para operações financeiras.

### 6. Relação entre Entidades
- **CCHistoricoCliente**: Representa o histórico de saldo de clientes.
- **CCHistoricoClienteCredor**: Representa o histórico de saldo de clientes credores.
- **CCHistoricoFundo**: Representa o histórico de saldo de fundos.
- **CCHistoricoNome**: Representa o histórico de saldo de nomes.
- **CCHistoricoVeiculo**: Representa o histórico de saldo de veículos.
- **CCTotalCliente**: Representa o total de saldo de clientes.
- **CCTotalClienteAnalitico**: Representa o total analítico de saldo de clientes.
- **CCTotalClienteCredor**: Representa o total de saldo de clientes credores.
- **CCTotalFundo**: Representa o total de saldo de fundos.
- **CCTotalFundoAnalitico**: Representa o total analítico de saldo de fundos.
- **CCTotalNome**: Representa o total de saldo de nomes.
- **CCTotalNomesAnalitico**: Representa o total analítico de saldo de nomes.
- **CCTotalVeiculo**: Representa o total de saldo de veículos.
- **CCVariacao**: Representa a variação de saldo.
- **CCVariacaoAnalitico**: Representa a variação analítica de saldo.
- **LancamentoNCC**: Representa lançamentos de conta corrente.
- **TempAgrupCC**: Representa agrupamentos temporários de conta corrente.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbConta | tabela | SELECT | Contas correntes. |
| TbHistoricoSaldo | tabela | SELECT | Histórico de saldos. |
| TbPessoaTitularidade | tabela | SELECT | Titularidades de pessoas. |
| TbPessoa | tabela | SELECT | Informações de pessoas. |
| TbMovimentoDia | tabela | SELECT | Movimentos diários. |
| TbHistoricoMovimento | tabela | SELECT | Histórico de movimentos. |
| TbTempAgrupamentoContaCorrente | tabela | SELECT | Agrupamentos temporários de conta corrente. |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbTempAgrupamentoContaCorrente | tabela | INSERT/DELETE | Agrupamentos temporários de conta corrente. |

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- Integração com banco de dados Sybase para operações de leitura e escrita.
- Utilização de Swagger para documentação de APIs.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de desenvolvimento, como injeção de dependências e tratamento de exceções. A documentação das APIs com Swagger é um ponto positivo. No entanto, poderia haver mais comentários explicativos em algumas partes do código para melhorar a legibilidade e manutenção.

### 13. Observações Relevantes
- O sistema utiliza o padrão de projeto de microserviços atômicos.
- A configuração de segurança OAuth2 está presente, mas não detalhada nos arquivos fornecidos.
- A documentação do projeto está incompleta no README.md, necessitando de uma descrição mais detalhada do projeto.
```