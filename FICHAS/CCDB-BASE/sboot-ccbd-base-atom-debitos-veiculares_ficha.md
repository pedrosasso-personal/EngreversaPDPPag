# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-ccbd-base-atom-debitos-veiculares** é um serviço atômico desenvolvido para gerenciar débitos veiculares (IPVA, DPVAT, Multas, RENAINF e Licenciamento). O sistema permite:

- Consultar débitos veiculares por RENAVAM
- Registrar novas transações de débitos
- Processar pagamentos de débitos (via cartão de crédito ou saldo em conta)
- Consultar extratos de pagamentos
- Monitorar etapas de processamento de transações
- Armazenar recibos de pagamento

O sistema atua como intermediário entre canais digitais do banco e sistemas de órgãos estaduais (DETRAN/PRODESP), persistindo informações de consultas e transações de pagamento.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `DebitosVeicularesController` | Controller REST que expõe endpoints para operações de débitos veiculares |
| `DebitosVeicularesServiceImpl` | Implementa lógica de gravação de débitos e validação de veículos |
| `ConsultaDebitosServiceImpl` | Implementa consultas de débitos específicos (IPVA, DPVAT, Multa, etc) |
| `PagamentoDebitoServiceImpl` | Gerencia pagamentos de débitos e atualização de status de transações |
| `TransacaoServiceImpl` | Implementa consultas de monitoramento de transações (sintético/analítico) |
| `ExtratoServiceImpl` | Gerencia inserção de extratos de pagamento |
| `DebitosVeicularesRepositoryImpl` | Interface JDBI para operações de gravação no banco de dados |
| `ConsultaDebitosRepositoryImpl` | Interface JDBI para operações de consulta no banco de dados |
| `TransacaoDebitoRepositoryImpl` | Interface JDBI para operações relacionadas a transações |
| `DebitosVeicularesConfiguration` | Configuração Spring para injeção de dependências e beans JDBI |

---

## 3. Tecnologias Utilizadas

- **Framework**: Spring Boot 2.x
- **Linguagem**: Java 11
- **Persistência**: JDBI 3.9.1 (SQL Object)
- **Banco de Dados**: MySQL 8.0.22
- **Documentação API**: Swagger/OpenAPI 3.0 (Springfox)
- **Mapeamento de Objetos**: MapStruct 1.4.2
- **Segurança**: JWT (sboot-arqt-base-security-jwt 0.19.0)
- **Auditoria**: springboot-arqt-base-trilha-auditoria-web 2.2.1
- **Monitoramento**: Spring Actuator + Micrometer + Prometheus
- **Logging**: Logback com formato JSON
- **Build**: Maven 3.3+
- **Containerização**: Docker
- **Testes**: JUnit 5, Mockito, RestAssured, Pact (Contract Testing)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/transacao` | `DebitosVeicularesController` | Cria nova transação de débitos veiculares |
| POST | `/v1/pagamento-debito` | `DebitosVeicularesController` | Registra novo pagamento de débito |
| GET | `/v1/pagamento-debito/total` | `DebitosVeicularesController` | Consulta total de pagamentos por período |
| GET | `/v1/debito/ipva` | `DebitosVeicularesController` | Consulta débito IPVA específico |
| GET | `/v1/debito/dpvat` | `DebitosVeicularesController` | Consulta débito DPVAT específico |
| GET | `/v1/debito/multa` | `DebitosVeicularesController` | Consulta débito de Multa específico |
| GET | `/v1/debito/renainf` | `DebitosVeicularesController` | Consulta débito RENAINF específico |
| GET | `/v1/debito/licenciamento` | `DebitosVeicularesController` | Consulta débito de Licenciamento específico |
| GET | `/v1/veiculo` | `DebitosVeicularesController` | Consulta informações do veículo por RENAVAM |
| POST | `/v1/atualizacao-transacao` | `DebitosVeicularesController` | Atualiza status de transação |
| POST | `/v1/extrato` | `DebitosVeicularesController` | Insere extrato de pagamentos |
| POST | `/v1/recibos` | `DebitosVeicularesController` | Salva recibos de pagamento |
| POST | `/v1/erroPagamento` | `DebitosVeicularesController` | Registra erros de pagamento do Banco Rendimento |
| GET | `/v1/monitor/etapas/sintetico` | `DebitosVeicularesController` | Consulta transações por etapa (visão sintética) |
| GET | `/v1/monitor/etapas/analitico` | `DebitosVeicularesController` | Consulta transações por etapa (visão analítica) |

---

## 5. Principais Regras de Negócio

1. **Validação de Veículo**: Antes de gravar débitos, verifica se o veículo já existe no banco. Se existir, atualiza; caso contrário, insere novo registro.

2. **Veículo sem Placa**: Quando não há placa informada, o sistema preenche campos do veículo com valores vazios/padrão.

3. **Transação de Débitos**: Ao gravar uma nova transação, o sistema:
   - Grava consulta RENAVAM
   - Grava débitos individuais (IPVA, DPVAT, Multa, RENAINF, Licenciamento)
   - Retorna IDs gerados para cada débito

4. **Licenciamento com Débitos Associados**: Licenciamento pode conter débitos de IPVA, DPVAT e Multas associados, que são gravados em tabelas específicas de relacionamento.

5. **Pagamento de Débitos**: Suporta duas formas de pagamento:
   - Cartão de crédito (com detalhes de parcelamento)
   - Saldo em conta (com dados de transação bancária)

6. **Status de Transação**: Transações podem ter status: PENDENTE, PAGO, REJEITADO.

7. **Validação de Datas**: Data inicial não pode ser posterior à data final em consultas de período.

8. **Extrato Único por Data**: Sistema valida se já existe extrato inserido para a data de consulta antes de inserir novo.

9. **Monitoramento de Etapas**: Sistema permite consultar transações segregadas por etapas (PROCESSADOS, ESTORNADOS, PENDENTES, ERROS).

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **TbVeiculo**: Armazena dados do veículo (RENAVAM, placa, proprietário, CPF/CNPJ)
- **TbConsultaRenavam**: Registra consultas realizadas (vincula conta bancária + RENAVAM)
- **TbDebitoIPVA**: Débitos de IPVA
- **TbDebitoDpvat**: Débitos de DPVAT
- **TbDebitoMulta**: Débitos de Multas
- **TbDebitoRenainf**: Débitos de RENAINF
- **TbDebitoLicenciamento**: Débitos de Licenciamento
- **TbTransacaoDebito**: Transações de pagamento de débitos
- **TbDetalheTransacaoCartao**: Detalhes de pagamento via cartão
- **TbComprovanteFiscal**: Recibos de pagamento
- **TbConsultaExtratoPagamento**: Cabeçalho de extrato
- **TbExtratoPagamento**: Itens de extrato
- **TbErroPagamentoRendimento**: Erros retornados pelo Banco Rendimento

**Relacionamentos:**
- TbConsultaRenavam (1) -> (N) TbDebitoIPVA/TbDebitoDpvat/TbDebitoMulta/TbDebitoRenainf/TbDebitoLicenciamento
- TbDebitoLicenciamento (1) -> (N) TbDebitoIPVA/TbDebitoDpvat/TbDebitoMulta (débitos associados ao licenciamento)
- TbTransacaoDebito (N) -> (1) TbConsultaRenavam
- TbTransacaoDebito (N) -> (1) TbDetalheTransacaoCartao (opcional)
- TbComprovanteFiscal (N) -> (1) TbTransacaoDebito
- TbConsultaExtratoPagamento (1) -> (N) TbExtratoPagamento
- TbErroPagamentoRendimento (N) -> (1) TbTransacaoDebito

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbVeiculo | Tabela | SELECT | Consulta dados do veículo por RENAVAM |
| TbConsultaRenavam | Tabela | SELECT | Recupera número RENAVAM por código de consulta |
| TbDebitoIPVA | Tabela | SELECT | Consulta débitos de IPVA |
| TbDebitoDpvat | Tabela | SELECT | Consulta débitos de DPVAT |
| TbDebitoMulta | Tabela | SELECT | Consulta débitos de Multas |
| TbDebitoRenainf | Tabela | SELECT | Consulta débitos de RENAINF |
| TbDebitoLicenciamento | Tabela | SELECT | Consulta débitos de Licenciamento |
| TbTransacaoDebito | Tabela | SELECT | Consulta transações de pagamento por período e status |
| TbConsultaExtratoPagamento | Tabela | SELECT | Verifica existência de extrato por data |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbVeiculo | Tabela | INSERT/UPDATE | Insere ou atualiza dados do veículo |
| TbConsultaRenavam | Tabela | INSERT | Registra nova consulta de RENAVAM |
| TbDebitoIPVA | Tabela | INSERT | Grava débitos de IPVA |
| TbDebitoDpvat | Tabela | INSERT | Grava débitos de DPVAT |
| TbDebitoMulta | Tabela | INSERT | Grava débitos de Multas |
| TbDebitoRenainf | Tabela | INSERT | Grava débitos de RENAINF |
| TbDebitoLicenciamento | Tabela | INSERT | Grava débitos de Licenciamento |
| TbTransacaoDebito | Tabela | INSERT/UPDATE | Insere transações de pagamento e atualiza status |
| TbDetalheTransacaoCartao | Tabela | INSERT | Insere detalhes de pagamento via cartão |
| TbComprovanteFiscal | Tabela | INSERT | Grava recibos de pagamento |
| TbConsultaExtratoPagamento | Tabela | INSERT | Insere cabeçalho de extrato |
| TbExtratoPagamento | Tabela | INSERT | Insere itens de extrato (batch) |
| TbErroPagamentoRendimento | Tabela | INSERT | Registra erros de pagamento do Banco Rendimento |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | Spring Boot | Configurações da aplicação (datasource, porta, profiles) |
| logback-spring.xml | Leitura | Logback | Configuração de logs (console, JSON format) |
| *.sql | Leitura | JDBI @UseClasspathSqlLocator | Queries SQL carregadas do classpath |
| sboot-ccbd-base-atom-debitos-veiculares.yml | Leitura | Swagger Codegen | Especificação OpenAPI para geração de código |

**Observação**: O sistema grava recibos em formato BLOB (campo `TeImagemComprovante` na tabela `TbComprovanteFiscal`), recebendo imagens em Base64.

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| PRODESP/DETRAN | API Externa | Sistema estadual de consulta de débitos veiculares (implícito pela presença de campos como `CdOperacaoProdesp`, `CdReceptora`) |
| Banco Rendimento | Sistema Externo | Recebe notificações de erro de pagamento via endpoint `/v1/erroPagamento` |
| Sistema de Pagamentos | Integração Interna | Recebe dados de transações de pagamento (campos `cdTransacaoPagamento`, `cdQuitacaoPagamento`, `cdSistemaPagamento`) |

**Observação**: As integrações são inferidas pela estrutura de dados. O sistema parece atuar como receptor de dados de sistemas externos (PRODESP) e provedor de dados para sistemas de pagamento internos.

---

## 13. Avaliação da Qualidade do Código

**Nota:** 7.5/10

**Justificativa:**

**Pontos Positivos:**
- Arquitetura hexagonal bem definida (ports/adapters)
- Separação clara de responsabilidades (domain, application, infrastructure)
- Uso adequado de padrões (Builder, Mapper, Service/Repository)
- Boa cobertura de testes unitários
- Uso de JDBI para queries SQL externalizadas
- Configuração adequada de profiles (local, des, qa, uat, prd)
- Implementação de validações de negócio
- Tratamento de exceções customizado

**Pontos de Melhoria:**
- Alguns métodos muito extensos (ex: `RepresentationMapper` com métodos repetitivos)
- Uso de `@AllArgsConstructor` em alguns lugares pode dificultar manutenção
- Falta de documentação JavaDoc em várias classes
- Alguns mappers poderiam ser simplificados com MapStruct
- Tratamento genérico de exceções em alguns controllers (`catch (Exception e)`)
- Campos com nomenclatura mista (português/inglês)
- Alguns métodos `protected` em services que poderiam ser `private`
- Uso de strings hardcoded para login ("CCBDDebitoVeicular_APPL")

---

## 14. Observações Relevantes

1. **Schema de Banco**: O sistema utiliza o schema `CCBDDebitoVeicular` no MySQL.

2. **Timezone**: Configurado para UTC no datasource (`useTimezone=true&serverTimezone=UTC`).

3. **Transações**: Uso de `@Transactional` em operações de gravação de débitos.

4. **Auditoria**: Campos de auditoria padrão em todas as tabelas (`FlAtivo`, `DsLogin`, `DtInclusao`, `DtAlteracao`).

5. **Soft Delete**: Sistema utiliza flag `FlAtivo = 'S'` para controle de registros ativos.

6. **Portas**: 
   - Aplicação: 8080
   - Actuator/Métricas: 9090

7. **Segurança**: Endpoints protegidos por OAuth2 (exceto Swagger UI).

8. **Formato de Datas**: Sistema trabalha com múltiplos formatos:
   - ISO 8601 para APIs (`yyyy-MM-dd'T'HH:mm:ss`)
   - Formato banco (`yyyy-MM-dd HH:mm:ss`)

9. **UUID**: Débitos individuais possuem UUID para rastreabilidade.

10. **Monitoramento**: Sistema possui endpoints específicos para monitoramento de etapas de processamento, facilitando observabilidade operacional.

11. **Arquitetura Multi-módulo**: Projeto organizado em módulos Maven (common, domain, application).

12. **CI/CD**: Presença de `jenkins.properties` e `infra-as-code/` indica pipeline de deploy automatizado.