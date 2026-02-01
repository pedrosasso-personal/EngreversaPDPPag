# Ficha Técnica do Sistema

## 1. Descrição Geral
Sistema de validação de transferências TEF (Transferência Eletrônica de Fundos) do Banco Votorantim. O serviço é responsável por validar transferências entre contas bancárias, verificando dias úteis, horários permitidos e realizando críticas de agendamento quando necessário. Utiliza integração com sistemas legados via EJB para validação de calendário bancário e processamento de transferências.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ValidarTransTEFController** | Controller REST que expõe o endpoint de validação de transferências |
| **ValidarTransfTEFService** | Serviço de negócio que orquestra a validação de transferências usando Apache Camel |
| **ValidarTransfTEFRouter** | Rota Apache Camel que define o fluxo de validação (verificação de dia útil, horário, agendamento) |
| **ValidarTransfTEFRepository** | Repositório para validação de transferência TEF via chamada ao legado |
| **ValidarAgendTEFRepository** | Repositório para validação de agendamento de transferência TEF |
| **IsDiaUtilRepository** | Repositório para verificar se uma data é dia útil |
| **ObterProximoDiaUtilRepository** | Repositório para obter o próximo dia útil |
| **FormatarDados** | Classe utilitária para formatação de datas e conversões |
| **CamelContextWrapper** | Wrapper do contexto Apache Camel para gerenciamento de rotas |
| **AppProperties** | Classe de configuração com propriedades da aplicação |

## 3. Tecnologias Utilizadas
- **Spring Boot 2.1.9** - Framework principal
- **Apache Camel 2.24.2** - Orquestração de fluxos e integração
- **Spring Security OAuth2** - Autenticação e autorização via JWT
- **Swagger/OpenAPI 3.0** - Documentação de API
- **Logback** - Logging estruturado
- **Micrometer/Prometheus** - Métricas e monitoramento
- **RestTemplate** - Cliente HTTP para integração com legado
- **Lombok** - Redução de boilerplate
- **Maven** - Gerenciamento de dependências
- **Docker** - Containerização
- **OpenShift/Kubernetes** - Orquestração de containers
- **JDK 11** - Versão Java

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/transferencia-bancaria/validar-transferencia-contas | ValidarTransTEFController | Valida uma transferência entre contas, verificando dias úteis, horários e realizando críticas de negócio |

## 5. Principais Regras de Negócio
1. **Validação de Data**: Não permite agendamento de transferências com data anterior à data atual
2. **Verificação de Dia Útil**: Valida se a data da transferência é dia útil bancário (praça Brasil)
3. **Validação de Horário**: Verifica se a transferência está dentro do horário permitido (02:00 às 22:30)
4. **Agendamento Automático**: Se a data não for dia útil ou estiver fora do horário, agenda automaticamente para o próximo dia útil
5. **Validação de Contas**: Valida dados de conta remetente e favorecido (banco, agência, conta)
6. **Crítica de Saldo**: Valida saldo disponível para transferência
7. **Tipos de Transferência**: Suporta diferentes tipos de transação (código de produto 171, sistema 1)
8. **Validação de Favorecido**: Verifica dados do favorecido incluindo CPF/CNPJ e nome

## 6. Relação entre Entidades

**ValidarTEFDTO** (Entidade principal de entrada)
- Contém: ContaCorrenteDTO (remetente), ContaCorrenteDTO (favorecido)
- Relaciona-se com: CalendarioDTO (para validação de data)

**ContaCorrenteDTO**
- Atributos: codigoBanco, numeroContaCorrente

**OperacaoTransferenciaTEFDTO** (Entidade de saída)
- Contém dados completos da transferência validada
- Inclui informações de remetente e favorecido expandidas

**CalendarioDTO**
- Usado para validação de dias úteis
- Relaciona-se com ValidacaoDataUtilDTO

**ValidacaoDataUtilDTO**
- Resultado da validação de dia útil
- Contém flags: isDiaUtil, isForaHorario, isHoje

## 7. Estruturas de Banco de Dados Lidas

não se aplica

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot | Arquivo de configuração da aplicação com profiles (local, des, qa, uat, prd) |
| logback-spring.xml | leitura | Logback | Configuração de logging estruturado por ambiente |
| sboot-ccbd-base-orch-transf-val-tef.yaml | leitura | Swagger Codegen | Contrato OpenAPI para geração de código |

## 10. Filas Lidas

não se aplica

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **EJB Legado - TransferenciaServices** | REST/JSON-RPC | Serviço legado para crítica de transferência entre contas com validação de saldo (método: CCPagamento.Transferencia.criticarTransferenciaEntreContasBancoValidarSaldo) |
| **EJB Legado - SCalendarioEJB** | REST/JSON-RPC | Serviço de calendário bancário para verificação de dias úteis (métodos: verificaDiaUtil, proximoDiaUtil) |
| **EJB Legado - Agendamento** | REST/JSON-RPC | Serviço para crítica de agendamento de transferências (método: CCAgendamento.Transferencia.criticarAgendamentoEntreContasBanco) |
| **OAuth2/JWT Provider** | HTTPS | Servidor de autenticação para validação de tokens JWT (jwks.json) |
| **ESB Adapter** | REST | Adaptador de integração com sistemas legados (URLs variam por ambiente) |

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com módulos domain e application
- Uso adequado de padrões como Repository e Service
- Implementação de orquestração com Apache Camel bem estruturada
- Configuração externalizada por ambiente
- Uso de Lombok para reduzir boilerplate
- Documentação via OpenAPI/Swagger
- Implementação de segurança com OAuth2/JWT
- Logs estruturados

**Pontos de Melhoria:**
- Tratamento de exceções genérico em alguns pontos (catch Exception)
- Valores hardcoded em algumas classes (ex: cdProduto=171, cdSistema=1)
- Falta de validações de entrada mais robustas
- Comentários de código desnecessários ou incompletos
- Algumas classes com responsabilidades que poderiam ser melhor distribuídas
- Falta de testes unitários enviados para análise
- Conversões de data repetidas em múltiplos locais (poderia ser centralizado)
- Nomenclatura de variáveis em português misturada com inglês

## 14. Observações Relevantes

1. **Arquitetura Multi-módulo**: O projeto está dividido em módulos `domain` (lógica de negócio) e `application` (exposição REST), seguindo boas práticas de separação de camadas

2. **Integração Legado**: Utiliza um padrão JSON-RPC customizado para comunicação com EJBs legados através de um ESB Adapter

3. **Ambientes**: Suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas via ConfigMaps e Secrets

4. **Observabilidade**: Implementa health checks, métricas Prometheus e logs estruturados em JSON

5. **Segurança**: Requer autenticação OAuth2 com scope 'openid' para acesso aos endpoints

6. **Horário de Operação**: Sistema opera com janela de horário específica (02:00 às 22:30) para transferências imediatas

7. **Praça Bancária**: Utiliza praça "NC" (Brasil) como padrão para validação de calendário

8. **Container**: Utiliza imagem AdoptOpenJDK 11 com OpenJ9 em Alpine Linux para otimização de recursos

9. **Pipeline**: Integrado com Jenkins para CI/CD com propriedades específicas de build

10. **Auditoria**: Implementa trilha de auditoria através de biblioteca específica do Banco Votorantim