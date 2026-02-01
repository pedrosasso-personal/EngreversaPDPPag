# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-ccbd-base-orch-limites** é um serviço de orquestração responsável por calcular e gerenciar limites transacionais diários para operações bancárias do Banco Votorantim. O sistema valida e calcula limites disponíveis para diferentes tipos de transações (TED, TEF, PIX, Boletos, Débitos Veiculares), considerando movimentações já realizadas, agendamentos futuros, pagamentos e períodos (diurno/noturno). Também permite a alteração de limites configurados. O serviço atua como orquestrador, integrando-se com diversos serviços atômicos para consolidar informações e aplicar regras de negócio complexas.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal Spring Boot que inicializa a aplicação |
| **LimitesController** | Controller REST v1 - expõe endpoint de consulta de limite diário |
| **LimitesControllerV2** | Controller REST v2 - expõe endpoints de consulta e alteração de limites |
| **LimitesControllerV3** | Controller REST v3 - versão aprimorada com validação de CPF/CNPJ |
| **LimiteBusiness** | Contém lógica de negócio para cálculo de limites conforme tipo de transação |
| **LimitesService** | Orquestra chamadas aos routers Camel e consolida resultados |
| **LimitesMapper** | Converte representações REST em objetos de domínio e vice-versa |
| **CamelContextWrapper** | Wrapper para gerenciar contexto Apache Camel e templates de produção/consumo |
| **AgendamentoRouter** | Rota Camel para consulta de agendamentos de pagamentos |
| **AlterarLimiteRouter** | Rota Camel para alteração de limites configurados |
| **ConsultarLimiteRouter** | Rota Camel para consulta de limites com movimentações |
| **ConsultarLimiteCompostoRouter** | Rota Camel para limites compostos (ex: PIX Saque-Troco) |
| **ConsultarLimitePagamentosRouter** | Rota Camel para limites de pagamentos de boletos |
| **LancFuturoRouter** | Rota Camel para consulta de lançamentos futuros |
| **MovimentacoesRouter** | Rota Camel para consulta de movimentações bancárias |
| **PagamentosRouter** | Rota Camel para consulta de pagamentos |
| **PagamentosDebitoVeicularRouter** | Rota Camel para pagamentos de débitos veiculares |
| **AgendamentoRepositoryImpl** | Integração com serviço de agendamentos |
| **AlterarLimiteRepositoryImpl** | Integração com serviço de alteração de limites |
| **ClienteDadosCadastraisRepositoryImpl** | Integração com serviço de dados cadastrais do cliente |
| **ConsultarLimiteRepositoryImpl** | Integração com serviço de consulta de limites configurados |
| **LancFuturoRepositoryImpl** | Integração com serviço de lançamentos futuros |
| **MovimentacaoRepositoryImpl** | Integração com serviço de movimentações bancárias |
| **PagamentoRepositoryImpl** | Integração com serviço de pagamentos |
| **PapelPessoaRepositoryImpl** | Integração com serviço de papel pessoa (funcionário/cliente) |
| **ValidacaoContaPessoaRepositoryImpl** | Valida titularidade de conta |
| **CalculoPagamentosSaldoCartaoUtil** | Utilitário com lógica complexa de cálculo de limites saldo/cartão |
| **DateUtil** | Utilitário para manipulação e validação de datas |
| **HorarioUtil** | Utilitário para determinar período (diurno/noturno/matutino) |
| **ExceptionControllerHandler** | Tratamento centralizado de exceções |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Spring Security OAuth2** (autenticação JWT)
- **Apache Camel 3.0.1** (orquestração de rotas e integração)
- **Swagger/OpenAPI 3.0** (documentação de APIs)
- **Springfox 3.0.0** (geração de documentação Swagger)
- **Lombok** (redução de boilerplate)
- **RestTemplate** (cliente HTTP para integrações)
- **JUnit 5** (testes unitários)
- **Mockito** (mocks em testes)
- **Rest Assured** (testes funcionais)
- **Pact** (testes de contrato)
- **Micrometer + Prometheus** (métricas)
- **Actuator** (monitoramento e health checks)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **OpenShift/Kubernetes** (deploy)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/limites/consulta/` | LimitesController | Consulta limite diário para transação (v1) |
| GET | `/v2/limites/consulta` | LimitesControllerV2 | Consulta limite diário com origem e limite máximo configurado |
| PUT | `/v2/limites/atualizar` | LimitesControllerV2 | Altera limite configurado para tipo de transação |
| GET | `/v3/limites/consulta` | LimitesControllerV3 | Consulta limite diário com tipo de limite (diurno/noturno/matutino) |

**Parâmetros comuns:**
- Headers: `codigoBanco`, `numeroConta`, `numeroAgencia`, `origem` (v2/v3)
- Query: `date`, `tipoTransacao`, `validarConta`, `cpfCnpj`

**Tipos de Transação suportados:** TED, TEF, BOL, PIX, DEB, BOLCIPCONTRICART, BOLCIPCONTRICC, PIX_SAQUE_TROCO, DEB_VEI_CC, DEB_VEI_CARTAO

---

## 5. Principais Regras de Negócio

1. **Validação de Data**: Não permite consultas retroativas; valida se é agendamento (data futura) ou efetivação (data atual)
2. **Limites Diferenciados por Perfil**: Funcionários BV possuem limites diferentes de clientes regulares
3. **Limites por Tipo de Transação**: Cada tipo de transação (TED, PIX, Boleto, etc.) possui limite específico
4. **Limites Noturnos**: Transações realizadas entre 20h e 6h possuem limite reduzido (R$ 1.000,00 padrão)
5. **Limites Compostos**: Algumas transações (ex: PIX Saque-Troco) validam limite próprio e limite pai
6. **Cálculo de Disponível**: Limite disponível = Limite configurado - (Movimentações + Agendamentos + Lançamentos Futuros + Pagamentos)
7. **Pagamentos Saldo/Cartão**: Lógica complexa que considera gastos em saldo e cartão separadamente, com limites específicos para cartão (R$ 3.000 cliente / R$ 5.000 funcionário)
8. **Validação de Titularidade**: Verifica se CPF/CNPJ é titular da conta informada
9. **Divisão Comercial**: Identifica divisão comercial do cliente para aplicar limites corretos
10. **Autorização Booleana**: Retorna se transação está autorizada baseado no limite disponível

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **Request**: Representa requisição de consulta de limite (banco, conta, agência, CPF/CNPJ, data, tipo transação)
- **LimiteDTO**: DTO completo com todas informações para cálculo de limite (estende Request com totais e configurações)
- **Limite/LimiteResponse**: Resposta com limite disponível, total, autorização e tipo
- **TotalMovimentacoes**: Agregação de movimentações por tipo
- **TotalPagamentos**: Agregação de pagamentos
- **TotalLancamentosFuturos**: Agregação de lançamentos futuros (TED/TEF agendados)
- **TotalAgendamentos**: Agregação de agendamentos de boletos
- **PapelPessoa**: Indica se pessoa é funcionário BV

**Relacionamentos:**
- Request → LimiteDTO (conversão/enriquecimento)
- LimiteDTO → LimiteResponse (resultado do cálculo)
- LimiteDTO pode conter LimiteDTO child (para limites compostos)
- Totais (Movimentações, Pagamentos, etc.) são agregados em LimiteDTO

---

## 7. Estruturas de Banco de Dados Lidas

Não se aplica. O sistema não acessa diretamente banco de dados. Todas as consultas são realizadas via APIs REST de serviços atômicos.

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema não atualiza diretamente banco de dados. Alterações são realizadas via APIs REST de serviços atômicos (ex: alteração de limite).

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | Spring Boot / AppProperties | Configurações da aplicação (URLs serviços, limites padrão) |
| logback-spring.xml | Leitura | Logback | Configuração de logs da aplicação |
| sboot-ccbd-base-orch-limites*.yaml | Leitura | Swagger Codegen | Especificações OpenAPI para geração de código |

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
| **sboot-glob-base-atom-cliente-dados-cadastrais** | API REST | Consulta dados cadastrais do cliente e contas correntes |
| **sboot-glob-base-atom-papel-pessoa** | API REST | Consulta se pessoa é funcionário BV ou cliente |
| **sboot-ccbd-base-atom-lanc-futuros** | API REST | Consulta total de lançamentos futuros (TED/TEF agendados) |
| **sboot-ccbd-base-atom-movimentacoes** | API REST | Consulta total de movimentações bancárias (TED/TEF/PIX) |
| **sboot-ccbd-base-atom-pagamentos** | API REST | Consulta total de pagamentos de boletos |
| **sboot-ccbd-base-atom-agendamento** | API REST | Consulta total de agendamentos de boletos consumo/tributo |
| **sboot-ccbd-base-atom-limites** | API REST | Consulta e altera limites configurados por divisão comercial |
| **sboot-ccbd-base-atom-debitos-veiculares** | API REST | Consulta pagamentos de débitos veiculares |
| **OAuth2 Server** | Autenticação | Validação de tokens JWT para autenticação |

Todas as integrações utilizam RestTemplate com segurança OAuth2 configurada.

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades (controllers, business, service, repository)
- Uso adequado de padrões (Builder, DTO, Mapper)
- Cobertura de testes razoável (unitários, integração, funcionais)
- Uso de Lombok reduz boilerplate
- Logs estruturados e informativos
- Tratamento centralizado de exceções
- Documentação OpenAPI completa
- Uso de Apache Camel para orquestração complexa

**Pontos de Melhoria:**
- Lógica de cálculo de limites saldo/cartão extremamente complexa e pouco documentada (CalculoPagamentosSaldoCartaoUtil)
- Muitas rotas Camel com responsabilidades similares, poderia ser consolidado
- Alguns métodos muito longos (ex: getLimiteDiarioResponse com switch case extenso)
- Falta de validações de entrada em alguns pontos
- Uso de Strings para representar enums em alguns locais
- Comentários em código poderiam ser mais descritivos
- Alguns testes apenas verificam "não lança exceção" sem validar resultado
- Duplicação de lógica entre versões de controllers (v1, v2, v3)

---

## 14. Observações Relevantes

1. **Versionamento de API**: Sistema possui 3 versões de API (v1, v2, v3) com evolução gradual de funcionalidades
2. **Segurança**: Utiliza OAuth2 com JWT, recupera CPF/CNPJ do token, header ou query parameter
3. **Limites Padrão Configuráveis**: Valores de limite são configuráveis via properties (funcionário: R$ 20.000, cliente: R$ 20.000, cartão cliente: R$ 3.000, cartão funcionário: R$ 5.000, noturno: R$ 1.000)
4. **Períodos de Operação**: Sistema diferencia 3 períodos - Diurno (6h-20h), Noturno (20h-00h), Matutino (00h-6h)
5. **Limites Compostos**: Transações como PIX_SAQUE_TROCO validam tanto limite específico quanto limite pai (PIX)
6. **Cálculo Complexo Saldo/Cartão**: Pagamentos de boleto no cartão possuem lógica específica que considera gastos em saldo e cartão separadamente, com regras diferentes para período diurno e noturno
7. **Arquitetura Modular**: Projeto dividido em módulos Maven (application, domain, common)
8. **Deploy**: Preparado para deploy em OpenShift/Kubernetes com configurações específicas por ambiente (des, qa, uat, prd)
9. **Observabilidade**: Integrado com Prometheus/Grafana para métricas e Actuator para health checks
10. **Auditoria**: Utiliza biblioteca BV de trilha de auditoria
11. **Validação de Conta**: Pode validar ou não titularidade da conta conforme parâmetro
12. **Tratamento de Erros**: Exceções customizadas com códigos de erro padronizados (RazaoExceptionEnum)